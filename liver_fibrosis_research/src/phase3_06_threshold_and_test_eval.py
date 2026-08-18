"""
phase3_06_threshold_and_test_eval.py
Phase 3, Parts 20-24 - Determine each model's classification threshold via Youden's J
on OUT-OF-FOLD TRAINING CV predictions ONLY (frozen example rule, evaluation_metrics_
protocol.md), THEN -- and only then -- load the locked test set for the first time,
generate final predictions, and compute the predefined discrimination metrics with
bootstrap confidence intervals.

THIS IS THE ONLY SCRIPT IN PHASE 3 THAT LOADS THE TEST SET.

Produces:
  results/tables/phase3_threshold_selection.csv
  results/predictions/test_predictions_<model>.csv
  results/tables/phase3_overall_discrimination.csv
"""
import os, sys
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve, confusion_matrix

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (PROC_DIR, SPLIT_DIR, MODEL_DIR, PRED_DIR, TAB_DIR, NOW, RANDOM_SEED,
                          PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES)

N_BOOTSTRAP = 2000  # matches the 2,000-resample convention already fixed in fairness_definition.md

def youdens_j_threshold(y_true, y_proba):
    fpr, tpr, thresh = roc_curve(y_true, y_proba)
    j = tpr - fpr
    return float(thresh[np.argmax(j)])

def bootstrap_ci(y_true, y_score, metric_fn, n_boot=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.RandomState(seed)
    n = len(y_true)
    vals = []
    y_true = np.asarray(y_true); y_score = np.asarray(y_score)
    for _ in range(n_boot):
        idx = rng.randint(0, n, n)
        yt, ys = y_true[idx], y_score[idx]
        if len(np.unique(yt)) < 2:
            continue
        vals.append(metric_fn(yt, ys))
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return round(lo, 4), round(hi, 4)

def main():
    print("=== Phase 3, Parts 20-24: Threshold Selection (train/CV only) then LOCKED Test Evaluation ===")

    # ── Part 20: threshold from OOF training predictions, TEST SET NOT YET LOADED ──────
    thresh_rows = []
    thresholds = {}
    for name in MODEL_NAMES:
        oof = pd.read_csv(PRED_DIR / f"validation_predictions_{name}.csv")
        t = youdens_j_threshold(oof["true_target"], oof["predicted_probability"])
        thresholds[name] = t
        thresh_rows.append({"model_name": name, "method": "Youden's J on out-of-fold training CV predictions",
                           "threshold": round(t, 4), "source": "training partition only, test set not accessed"})
        print(f"  {name}: Youden threshold = {t:.4f} (from OOF CV predictions only)")
    pd.DataFrame(thresh_rows).to_csv(TAB_DIR / "phase3_threshold_selection.csv", index=False)
    print("  All thresholds frozen from training/CV data. NOW loading the locked test set for the first time.\n")

    # ── Part 23: load the LOCKED test set (first and only time in Phase 3) ──────────────
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
    test_df = df[df["SEQN"].isin(test_ids)].reset_index(drop=True)
    print(f"  Loaded LOCKED TEST SET: N={len(test_df)}. This is the only script that touches it.")
    X_test = test_df[PRIMARY_PREDICTORS]
    y_test = test_df[PRIMARY_OUTCOME_COL].values

    disc_rows = []
    for name in MODEL_NAMES:
        bundle = joblib.load(MODEL_DIR / f"model_{name}_v1.joblib")
        pipe = bundle["pipeline"]
        proba = pipe.predict_proba(X_test)[:, 1]
        pred_class = (proba >= thresholds[name]).astype(int)

        pred_df = pd.DataFrame({"SEQN": test_df["SEQN"].values, "true_target": y_test,
                               "predicted_probability": proba, "predicted_class": pred_class,
                               "threshold_used": thresholds[name]})
        pred_df.to_csv(PRED_DIR / f"test_predictions_{name}.csv", index=False)

        auc = roc_auc_score(y_test, proba)
        pr_auc = average_precision_score(y_test, proba)
        tn, fp, fn, tp = confusion_matrix(y_test, pred_class).ravel()
        sens = tp / (tp + fn) if (tp + fn) else np.nan
        spec = tn / (tn + fp) if (tn + fp) else np.nan
        ppv = tp / (tp + fp) if (tp + fp) else np.nan
        npv = tn / (tn + fn) if (tn + fn) else np.nan
        f1 = 2 * ppv * sens / (ppv + sens) if (ppv and sens and (ppv + sens)) else np.nan

        auc_lo, auc_hi = bootstrap_ci(y_test, proba, roc_auc_score)
        prauc_lo, prauc_hi = bootstrap_ci(y_test, proba, average_precision_score)

        disc_rows.append({
            "model_name": name, "test_n": len(test_df), "threshold": round(thresholds[name], 4),
            "roc_auc": round(auc, 4), "roc_auc_95ci_low": auc_lo, "roc_auc_95ci_high": auc_hi,
            "pr_auc": round(pr_auc, 4), "pr_auc_95ci_low": prauc_lo, "pr_auc_95ci_high": prauc_hi,
            "sensitivity": round(sens, 4), "specificity": round(spec, 4), "ppv": round(ppv, 4),
            "npv": round(npv, 4), "f1": round(f1, 4), "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
            "ci_method": f"percentile bootstrap, n={N_BOOTSTRAP} resamples, seed={RANDOM_SEED}"
        })
        print(f"  {name}: TEST ROC-AUC={auc:.4f} [{auc_lo},{auc_hi}], PR-AUC={pr_auc:.4f}, "
              f"sens={sens:.3f}, spec={spec:.3f}")

    pd.DataFrame(disc_rows).to_csv(TAB_DIR / "phase3_overall_discrimination.csv", index=False)
    print(f"\n  Saved phase3_threshold_selection.csv, {len(MODEL_NAMES)} test_predictions_<model>.csv files, "
          "and phase3_overall_discrimination.csv.")
    print("[THRESHOLD SELECTION & LOCKED TEST EVALUATION COMPLETE]")

if __name__ == "__main__":
    main()
