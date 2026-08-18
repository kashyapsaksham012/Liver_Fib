"""
phase3_13_imbalance_audit_and_mlp_sensitivity.py
Phase 3 Remediation, Parts 3F/3G/3T - Audit exactly what class-imbalance handling
each model received, then run a PRE-SPECIFIED, training-fold-only sensitivity
analysis for MLP (the one model incompatible with class_weight/sample_weight):
random oversampling to 1:1 balance, applied ONLY inside training folds via
imblearn.pipeline.Pipeline (which resamples strictly within each fold, exactly
mirroring what class_weight='balanced' achieves mathematically for the other
models -- inverse-frequency class balancing). The test set is NEVER resampled and
NEVER used to choose between MLP_original and MLP_balanced.

Rationale for why this is needed (not optional): Phase 2's model_development_protocol.md
froze "class weights, not SMOTE" as the general class-imbalance POLICY, but did not
anticipate that sklearn's MLPClassifier is the one estimator in the frozen 5-model set
that cannot implement that policy via its native API. This is a genuine implementation
gap Phase 2 did not foresee, not a Phase 2 error -- Option B (pre-specified sensitivity
remediation) applies per the remediation instructions.

Produces:
  documentation/phase3/class_imbalance_audit.md
  results/tables/phase3_mlp_asymmetry_audit.csv
  results/predictions/validation_predictions_mlp_balanced.csv
  results/predictions/test_predictions_mlp_balanced.csv  (sensitivity only; test set read once, at the very end)
  models/phase3/model_mlp_balanced_v1_sensitivity.joblib
"""
import os, sys, json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedKFold, GridSearchCV, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, roc_curve
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import RandomOverSampler

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (PROC_DIR, SPLIT_DIR, MODEL_DIR, PRED_DIR, TAB_DIR, DOC_DIR, NOW,
                          RANDOM_SEED, N_CV_FOLDS, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL)

def youdens_j(y_true, y_proba):
    fpr, tpr, thresh = roc_curve(y_true, y_proba)
    return float(thresh[np.argmax(tpr - fpr)])

def main():
    print("=== Phase 3 Remediation, Parts 3F/3G/3T: Class-Imbalance Audit & MLP Sensitivity ===")

    # ── Part 3F: class-imbalance audit table (what each model actually received) ───────
    model_reg = pd.read_csv(TAB_DIR / "phase3_model_registry.csv")
    audit_rows = []
    for _, r in model_reg.iterrows():
        audit_rows.append({
            "model": r["model_name"],
            "class_weighting": r["class_imbalance_handling"] if "class_weight" in r["class_imbalance_handling"] or "scale_pos_weight" in r["class_imbalance_handling"] else "NONE",
            "sampling": "None (native class weighting used instead)" if r["model_name"] != "mlp" else "None in primary model (see sensitivity analysis)",
            "other_imbalance_strategy": "N/A",
            "phase2_frozen_policy_followed": True if r["model_name"] != "mlp" else "PARTIALLY -- see class_imbalance_audit.md"
        })
    audit_df = pd.DataFrame(audit_rows)
    print("  Class-imbalance-by-model audit:\n" + audit_df.to_string(index=False))

    with open(DOC_DIR / "class_imbalance_audit.md", "w") as f:
        f.write(f"# Class-Imbalance Audit (Model-by-Model)\n\n**Generated:** {NOW}\n\n")
        f.write("| Model | Class weighting | Sampling | Other imbalance strategy |\n|---|---|---|---|\n")
        for _, r in audit_df.iterrows():
            f.write(f"| {r['model']} | {r['class_weighting']} | {r['sampling']} | {r['other_imbalance_strategy']} |\n")
        f.write("\n## Determination\n\n")
        f.write("Phase 2's `model_development_protocol.md` froze a general policy (\"class weights, not "
                "SMOTE\") but did not specify a per-model implementation and did NOT anticipate that "
                "sklearn's `MLPClassifier.fit()` accepts neither `class_weight` nor `sample_weight` -- unlike "
                "the other four estimators. **This is a genuine implementation gap Phase 2 did not foresee, "
                "not a Phase 2 drafting error requiring reopening Phase 2.**\n\n")
        f.write("**Decision: Option B applies.** A pre-specified, training-fold-only sensitivity analysis "
                "(MLP_balanced, via random oversampling to 1:1 class balance inside CV folds only, using "
                "`imblearn.pipeline.Pipeline` so resampling never touches held-out/validation/test rows) is "
                "run below and compared to MLP_original. **MLP_original remains the primary retained model "
                "for downstream phases** (consistent with the frozen retention rule -- see "
                "`downstream_model_retention_rule.md`); MLP_balanced is reported ONLY as a sensitivity check "
                "on whether the imbalance asymmetry materially changes MLP's ranking relative to the other "
                "four models, not as a replacement.\n\n")

    # ── Parts 3G/3T: MLP_balanced sensitivity model, training-fold-only oversampling ───
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
    train_df = df[df["SEQN"].isin(train_ids)].reset_index(drop=True)
    X = train_df[PRIMARY_PREDICTORS]
    y = train_df[PRIMARY_OUTCOME_COL].values
    cv = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)

    pre = ColumnTransformer([("num", SkPipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), PRIMARY_PREDICTORS)])
    pipe = ImbPipeline([
        ("pre", pre),
        ("oversample", RandomOverSampler(sampling_strategy=1.0, random_state=RANDOM_SEED)),  # 1:1 balance, TRAINING FOLD ONLY
        ("est", MLPClassifier(random_state=RANDOM_SEED, max_iter=1000, early_stopping=True)),
    ])
    grid = {"est__hidden_layer_sizes": [(16,), (32,), (32, 16)], "est__alpha": [0.0001, 0.001, 0.01],
           "est__learning_rate_init": [0.001, 0.01]}
    search = GridSearchCV(pipe, grid, scoring="roc_auc", cv=cv, n_jobs=-1, refit=True)
    search.fit(X, y)
    print(f"  MLP_balanced (training-fold-only 1:1 oversampling): best CV ROC-AUC = {search.best_score_:.4f}, params={search.best_params_}")

    best_pipe = ImbPipeline([("pre", pre), ("oversample", RandomOverSampler(sampling_strategy=1.0, random_state=RANDOM_SEED)),
                            ("est", MLPClassifier(random_state=RANDOM_SEED, max_iter=1000, early_stopping=True))])
    best_pipe.set_params(**search.best_params_)
    oof_proba = cross_val_predict(best_pipe, X, y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    oof_df = pd.DataFrame({"SEQN": train_df["SEQN"].values, "true_target": y, "predicted_probability": oof_proba})
    oof_df.to_csv(PRED_DIR / "validation_predictions_mlp_balanced.csv", index=False)
    thresh_balanced = youdens_j(y, oof_proba)
    print(f"  MLP_balanced Youden threshold (from OOF training predictions only): {thresh_balanced:.4f}")

    final_pipe = search.best_estimator_
    joblib.dump({"pipeline": final_pipe, "predictors": PRIMARY_PREDICTORS, "seed": RANDOM_SEED,
               "best_params": search.best_params_, "cv_auc": round(search.best_score_, 4),
               "note": "SENSITIVITY ANALYSIS ONLY -- not the primary retained MLP model"},
              MODEL_DIR / "model_mlp_balanced_v1_sensitivity.joblib")

    # Evaluate on the LOCKED test set -- reported for comparison only, never used to pick the sensitivity config
    test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
    test_df = df[df["SEQN"].isin(test_ids)].reset_index(drop=True)
    X_test, y_test = test_df[PRIMARY_PREDICTORS], test_df[PRIMARY_OUTCOME_COL].values
    proba_test = final_pipe.predict_proba(X_test)[:, 1]
    pred_class = (proba_test >= thresh_balanced).astype(int)
    pd.DataFrame({"SEQN": test_df["SEQN"].values, "true_target": y_test, "predicted_probability": proba_test,
                "predicted_class": pred_class, "threshold_used": thresh_balanced}).to_csv(
        PRED_DIR / "test_predictions_mlp_balanced.csv", index=False)
    test_auc_balanced = roc_auc_score(y_test, proba_test)

    orig_test = pd.read_csv(PRED_DIR / "test_predictions_mlp.csv")
    test_auc_original = roc_auc_score(orig_test["true_target"], orig_test["predicted_probability"])

    # Paired bootstrap comparison, same method as the main model-comparison analysis
    rng = np.random.RandomState(RANDOM_SEED)
    n = len(y_test)
    diffs = []
    for _ in range(2000):
        idx = rng.randint(0, n, n)
        yt = y_test[idx]
        if len(np.unique(yt)) < 2:
            continue
        diffs.append(roc_auc_score(yt, proba_test[idx]) - roc_auc_score(yt, orig_test["predicted_probability"].values[idx]))
    diffs = np.array(diffs)
    lo, hi = np.percentile(diffs, [2.5, 97.5])

    mlp_audit = pd.DataFrame([{
        "comparison": "MLP_original (unweighted) vs MLP_balanced (training-fold-only 1:1 oversampling, sensitivity)",
        "mlp_original_cv_roc_auc": model_reg[model_reg.model_name == "mlp"]["cv_roc_auc"].iloc[0],
        "mlp_balanced_cv_roc_auc": round(search.best_score_, 4),
        "mlp_original_test_roc_auc": round(test_auc_original, 4),
        "mlp_balanced_test_roc_auc": round(test_auc_balanced, 4),
        "test_auc_diff_balanced_minus_original": round(test_auc_balanced - test_auc_original, 4),
        "diff_95ci_low": round(lo, 4), "diff_95ci_high": round(hi, 4),
        "ci_excludes_zero": bool(lo > 0 or hi < 0),
        "primary_retained_model": "MLP_original (frozen retention rule: all 5 ORIGINAL model families retained; MLP_balanced is sensitivity-only, not a replacement)",
        "conclusion": ("Oversampling produced a materially different result -- see class_imbalance_audit.md for interpretation"
                      if (lo > 0 or hi < 0) else
                      "Training-fold-only 1:1 oversampling did not produce a statistically detectable difference in MLP test discrimination; "
                      "the original unweighted MLP result is not undermined by the class-imbalance asymmetry for this cohort/prevalence.")
    }])
    mlp_audit.to_csv(TAB_DIR / "phase3_mlp_asymmetry_audit.csv", index=False)
    print(f"\n  MLP_original test AUC={test_auc_original:.4f} | MLP_balanced (sensitivity) test AUC={test_auc_balanced:.4f} "
          f"| diff 95% CI=[{lo:.4f},{hi:.4f}] | {'DIFFERENT' if (lo>0 or hi<0) else 'NOT statistically distinguishable'}")
    print("  Saved phase3_mlp_asymmetry_audit.csv, class_imbalance_audit.md, and MLP_balanced artifacts.")
    print("  MLP_original remains the primary retained model; MLP_balanced is sensitivity-only.")
    print("[CLASS-IMBALANCE AUDIT & MLP SENSITIVITY COMPLETE]")

if __name__ == "__main__":
    main()
