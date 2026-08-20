"""
sens_02_train_evaluate.py
Deferred Sensitivity Analysis Execution, Parts 5-6 (Analyses A and B): train + evaluate all 5
frozen model families on CAND_2 (relaxed elastography eligibility, N=7,639) and CAND_3
(fasting-extended, N=3,582), per Amendment #13: frozen Phase 3 hyperparameters reused unchanged
(no new search), fresh per-model Youden's-J-on-CV-OOF threshold derived on each cohort's own
training partition, fresh 70/30 stratified split (seed=42, mirroring the frozen Phase 3 split
design). Scope = discrimination + calibration in full, plus a targeted BMI+Age fairness check
(Part 14 of this task). Uncertainty/conformal replication is explicitly NOT performed (deferred,
Amendment #13).

Leakage safety: all preprocessing (imputation, scaling) fit only inside each cohort's own training
partition via sklearn Pipeline/ColumnTransformer, mirroring Phase 3's established pattern. The
locked Phase 3 test set is never loaded or referenced anywhere in this script.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve
import xgboost as xgb
import lightgbm as lgb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, PROC_DIR, MODEL_DIR, PRIMARY_OUTCOME_COL, RANDOM_SEED, N_CV_FOLDS, MODEL_NAMES, TRAIN_FRACTION

RESULTS_DIR = ROOT / "results" / "sensitivity"
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 42
CI_LEVEL = 0.95
EPS = 1e-12

PRIMARY_PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL",
                       "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
FASTING_EXTRA = ["LBXGLU", "LBXTR"]

def logit(p):
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))

def calibration_in_the_large(y, p):
    z = logit(np.asarray(p)).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])

def youden_j_threshold(y, p):
    fpr, tpr, thr = roc_curve(y, p)
    j = tpr - fpr
    return float(thr[np.argmax(j)])

best_params_by_model = {}
for name in MODEL_NAMES:
    art = joblib.load(MODEL_DIR / f"model_{name}_v1.joblib")
    best_params_by_model[name] = art["best_params"]

def build_pipeline(name, scale, predictors):
    steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scale", StandardScaler()))
    pre = ColumnTransformer([("num", Pipeline(steps), predictors)])
    if name == "logistic":
        est = LogisticRegression(class_weight="balanced", solver="lbfgs", max_iter=2000, random_state=RANDOM_SEED)
    elif name == "random_forest":
        est = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1)
    elif name == "xgboost":
        est = xgb.XGBClassifier(eval_metric="logloss", random_state=RANDOM_SEED, n_jobs=-1)
    elif name == "lightgbm":
        est = lgb.LGBMClassifier(random_state=RANDOM_SEED, n_jobs=-1, verbosity=-1)
    elif name == "mlp":
        est = MLPClassifier(random_state=RANDOM_SEED, max_iter=1000, early_stopping=True)
    else:
        raise ValueError(name)
    stripped = {k.replace("est__", ""): v for k, v in best_params_by_model[name].items()}
    est.set_params(**stripped)
    return Pipeline([("pre", pre), ("est", est)])

def bmi_age_fairness(test_df, y_true, y_pred_class, rng):
    """Targeted fairness check: BMI-Obese vs Normal, Age-60+ vs 40-59, sensitivity absolute
    difference from reference (Phase 5's primary fairness metric), bootstrap CI n=2000."""
    rows = []
    dims = [("bmi", "bmi_group_final", "Obese", "Normal"), ("age", "age_group_final", "60+", "40-59")]
    for dim_name, col, target_cat, ref_cat in dims:
        for cat, label in [(target_cat, "target"), (ref_cat, "reference")]:
            pass
        target_mask = (test_df[col] == target_cat).values
        ref_mask = (test_df[col] == ref_cat).values
        y_t, yhat_t = y_true[target_mask], y_pred_class[target_mask]
        y_r, yhat_r = y_true[ref_mask], y_pred_class[ref_mask]
        n_t_pos, n_r_pos = int((y_t == 1).sum()), int((y_r == 1).sum())
        if n_t_pos == 0 or n_r_pos == 0:
            rows.append({"dimension": dim_name, "target_category": target_cat, "reference_category": ref_cat,
                          "target_n": int(target_mask.sum()), "target_n_positive": n_t_pos,
                          "reference_n": int(ref_mask.sum()), "reference_n_positive": n_r_pos,
                          "target_sensitivity": None, "reference_sensitivity": None,
                          "absolute_disparity_pp": None, "ci_lower_pp": None, "ci_upper_pp": None,
                          "note": "insufficient positive cases for sensitivity computation"})
            continue
        sens_t = (yhat_t[y_t == 1] == 1).mean()
        sens_r = (yhat_r[y_r == 1] == 1).mean()
        diffs = []
        for _ in range(BOOTSTRAP_N):
            idx_t = rng.integers(0, len(y_t), size=len(y_t))
            idx_r = rng.integers(0, len(y_r), size=len(y_r))
            yb_t, yhb_t = y_t[idx_t], yhat_t[idx_t]
            yb_r, yhb_r = y_r[idx_r], yhat_r[idx_r]
            if (yb_t == 1).sum() == 0 or (yb_r == 1).sum() == 0:
                continue
            s_t = (yhb_t[yb_t == 1] == 1).mean()
            s_r = (yhb_r[yb_r == 1] == 1).mean()
            diffs.append(100 * (s_t - s_r))
        alpha = 1 - CI_LEVEL
        lo, hi = (np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)]) if diffs else (None, None))
        rows.append({"dimension": dim_name, "target_category": target_cat, "reference_category": ref_cat,
                      "target_n": int(target_mask.sum()), "target_n_positive": n_t_pos,
                      "reference_n": int(ref_mask.sum()), "reference_n_positive": n_r_pos,
                      "target_sensitivity": round(sens_t, 6), "reference_sensitivity": round(sens_r, 6),
                      "absolute_disparity_pp": round(100 * (sens_t - sens_r), 4),
                      "ci_lower_pp": round(lo, 4) if lo is not None else None,
                      "ci_upper_pp": round(hi, 4) if hi is not None else None, "note": ""})
    return rows

def run_cohort(cohort_name, df, predictors, expected_n, expected_pos):
    if len(df) != expected_n or int(df[PRIMARY_OUTCOME_COL].sum()) != expected_pos:
        print(f"SENSITIVITY STOP CONDITION: {cohort_name} N={len(df)} pos={int(df[PRIMARY_OUTCOME_COL].sum())}, expected {expected_n}/{expected_pos}")
        sys.exit(1)

    train_df, test_df = train_test_split(df, test_size=1 - TRAIN_FRACTION, stratify=df[PRIMARY_OUTCOME_COL],
                                          random_state=RANDOM_SEED)
    train_df, test_df = train_df.reset_index(drop=True), test_df.reset_index(drop=True)
    print(f"\n=== {cohort_name}: N={len(df)} (train={len(train_df)}, test={len(test_df)}) ===")

    X_train, y_train = train_df[predictors], train_df[PRIMARY_OUTCOME_COL].values
    X_test, y_test = test_df[predictors], test_df[PRIMARY_OUTCOME_COL].values

    cv = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    disc_rows, fair_rows = [], []
    rng = np.random.default_rng(BOOTSTRAP_SEED)

    for name in MODEL_NAMES:
        scale = name in ("logistic", "mlp")
        pipe_oof = build_pipeline(name, scale, predictors)
        if name in ("xgboost", "lightgbm"):
            n_pos, n_neg = int(y_train.sum()), int((y_train == 0).sum())
            pipe_oof.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
        oof_proba = cross_val_predict(pipe_oof, X_train, y_train, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
        threshold = youden_j_threshold(y_train, oof_proba)

        pipe_final = build_pipeline(name, scale, predictors)
        if name in ("xgboost", "lightgbm"):
            n_pos, n_neg = int(y_train.sum()), int((y_train == 0).sum())
            pipe_final.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
        pipe_final.fit(X_train, y_train)

        p_test = pipe_final.predict_proba(X_test)[:, 1]
        yhat_test = (p_test >= threshold).astype(int)
        auc = roc_auc_score(y_test, p_test)
        pr_auc = average_precision_score(y_test, p_test)
        tp = int(((y_test == 1) & (yhat_test == 1)).sum()); fn = int(((y_test == 1) & (yhat_test == 0)).sum())
        tn = int(((y_test == 0) & (yhat_test == 0)).sum()); fp = int(((y_test == 0) & (yhat_test == 1)).sum())
        sens = tp / (tp + fn) if (tp + fn) else None
        spec = tn / (tn + fp) if (tn + fp) else None
        intercept, slope = calibration_in_the_large(y_test, p_test)
        brier = brier_score_loss(y_test, p_test)

        auc_boot = []
        for _ in range(BOOTSTRAP_N):
            idx = rng.integers(0, len(y_test), size=len(y_test))
            yb, pb = y_test[idx], p_test[idx]
            if len(np.unique(yb)) < 2:
                continue
            auc_boot.append(roc_auc_score(yb, pb))
        alpha = 1 - CI_LEVEL
        auc_lo, auc_hi = np.percentile(auc_boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])

        disc_rows.append({
            "cohort": cohort_name, "model": name, "train_n": len(train_df), "test_n": len(test_df),
            "threshold": round(threshold, 6), "roc_auc": round(auc, 6),
            "roc_auc_ci_lower": round(auc_lo, 6), "roc_auc_ci_upper": round(auc_hi, 6),
            "pr_auc": round(pr_auc, 6), "sensitivity": round(sens, 6) if sens is not None else None,
            "specificity": round(spec, 6) if spec is not None else None,
            "calibration_intercept": round(intercept, 6), "calibration_slope": round(slope, 6),
            "brier_score": round(brier, 6), "bootstrap_n_valid_auc": len(auc_boot),
        })
        print(f"  {name}: threshold={threshold:.4f}, test AUC={auc:.4f}, sens={sens:.4f}, calib intercept={intercept:.4f}, slope={slope:.4f}")

        for row in bmi_age_fairness(test_df, y_test, yhat_test, rng):
            row.update({"cohort": cohort_name, "model": name})
            fair_rows.append(row)

    return disc_rows, fair_rows

def main():
    cand2 = pd.read_parquet(PROC_DIR / "analysis_dataset_cand2_relaxed_elastography.parquet")
    cand3 = pd.read_parquet(PROC_DIR / "analysis_dataset_secondary.parquet")

    disc_a, fair_a = run_cohort("CAND_2_relaxed_elastography", cand2, PRIMARY_PREDICTORS, 7639, 804)
    disc_b, fair_b = run_cohort("CAND_3_fasting_extended", cand3, PRIMARY_PREDICTORS + FASTING_EXTRA, 3582, 319)

    disc_all = pd.DataFrame(disc_a + disc_b)
    fair_all = pd.DataFrame(fair_a + fair_b)
    disc_all.to_csv(RESULTS_DIR / "sensitivity_discrimination_calibration_results.csv", index=False)
    fair_all.to_csv(RESULTS_DIR / "sensitivity_bmi_age_fairness_results.csv", index=False)
    print(f"\nSaved results/sensitivity/sensitivity_discrimination_calibration_results.csv ({len(disc_all)} rows)")
    print(f"Saved results/sensitivity/sensitivity_bmi_age_fairness_results.csv ({len(fair_all)} rows)")

if __name__ == "__main__":
    main()
