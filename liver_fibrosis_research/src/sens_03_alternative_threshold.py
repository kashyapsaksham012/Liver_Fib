"""
sens_03_alternative_threshold.py
Deferred Sensitivity Analysis Execution, Part 7 (Analysis C): alternative fibrosis threshold
(8.0 kPa vs. primary 8.2 kPa). Per Amendment #13, this requires NO retraining -- CAND_1's cohort,
predictors, and frozen Phase 3 models are unchanged; only the outcome label changes. Re-evaluates
the already-frozen Phase 3 test-set and OOF predicted probabilities
(results/predictions/{test,validation}_predictions_<model>.csv) against the already-existing
outcome_sensitivity_8.0kPa column. No model is refit, no new test-set access of any model occurs.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, PROC_DIR, MODEL_NAMES

RESULTS_DIR = ROOT / "results" / "sensitivity"
PRED_DIR = ROOT / "results" / "predictions"
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 42
CI_LEVEL = 0.95
EPS = 1e-12

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

primary = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
outcome_map = primary.set_index("SEQN")["outcome_sensitivity_8.0kPa"]
group_map = primary.set_index("SEQN")[["bmi_group_final", "age_group_final"]]

def bmi_age_fairness_threshold(test_df, y_true, y_pred_class, rng):
    rows = []
    dims = [("bmi", "bmi_group_final", "Obese", "Normal"), ("age", "age_group_final", "60+", "40-59")]
    for dim_name, col, target_cat, ref_cat in dims:
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
                          "absolute_disparity_pp": None, "ci_lower_pp": None, "ci_upper_pp": None})
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
            diffs.append(100 * ((yhb_t[yb_t == 1] == 1).mean() - (yhb_r[yb_r == 1] == 1).mean()))
        alpha = 1 - CI_LEVEL
        lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)]) if diffs else (None, None)
        rows.append({"dimension": dim_name, "target_category": target_cat, "reference_category": ref_cat,
                      "target_n": int(target_mask.sum()), "target_n_positive": n_t_pos,
                      "reference_n": int(ref_mask.sum()), "reference_n_positive": n_r_pos,
                      "target_sensitivity": round(sens_t, 6), "reference_sensitivity": round(sens_r, 6),
                      "absolute_disparity_pp": round(100 * (sens_t - sens_r), 4),
                      "ci_lower_pp": round(lo, 4) if lo is not None else None,
                      "ci_upper_pp": round(hi, 4) if hi is not None else None})
    return rows

rows = []
fair_rows = []
rng = np.random.default_rng(BOOTSTRAP_SEED)
for name in MODEL_NAMES:
    # Re-derive threshold via Youden's J on the already-frozen OOF (training) predictions,
    # relabeled at 8.0kPa -- never touches the test set.
    oof = pd.read_csv(PRED_DIR / f"validation_predictions_{name}.csv")
    oof["y_80"] = oof["SEQN"].map(outcome_map)
    threshold = youden_j_threshold(oof["y_80"].values, oof["predicted_probability"].values)

    # Re-evaluate the already-frozen TEST predictions (never refit, never re-touched as a model)
    test = pd.read_csv(PRED_DIR / f"test_predictions_{name}.csv")
    test["y_80"] = test["SEQN"].map(outcome_map)
    test = test.join(group_map, on="SEQN")
    y_test = test["y_80"].values
    p_test = test["predicted_probability"].values
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

    rows.append({
        "model": name, "outcome_threshold": "8.0kPa", "test_n": len(test),
        "test_n_positive": int(y_test.sum()), "threshold": round(threshold, 6),
        "roc_auc": round(auc, 6), "roc_auc_ci_lower": round(auc_lo, 6), "roc_auc_ci_upper": round(auc_hi, 6),
        "pr_auc": round(pr_auc, 6), "sensitivity": round(sens, 6) if sens is not None else None,
        "specificity": round(spec, 6) if spec is not None else None,
        "calibration_intercept": round(intercept, 6), "calibration_slope": round(slope, 6),
        "brier_score": round(brier, 6), "bootstrap_n_valid_auc": len(auc_boot),
        "retrained": False, "test_set_reaccessed_for_model_fitting": False,
    })
    print(f"{name}: threshold={threshold:.4f}, test AUC={auc:.4f}, sens={sens:.4f}, calib intercept={intercept:.4f}, slope={slope:.4f}")

    for row in bmi_age_fairness_threshold(test, y_test, yhat_test, rng):
        row.update({"model": name, "outcome_threshold": "8.0kPa"})
        fair_rows.append(row)

out = pd.DataFrame(rows)
out.to_csv(RESULTS_DIR / "alternative_threshold_8p0kPa_results.csv", index=False)
fair_out = pd.DataFrame(fair_rows)
fair_out.to_csv(RESULTS_DIR / "alternative_threshold_8p0kPa_bmi_age_fairness.csv", index=False)
print(f"\nSaved results/sensitivity/alternative_threshold_8p0kPa_results.csv ({len(out)} rows)")
print(f"Saved results/sensitivity/alternative_threshold_8p0kPa_bmi_age_fairness.csv ({len(fair_out)} rows)")
print("No model was refit; only the outcome label and downstream metrics were recomputed from")
print("already-frozen Phase 3 predicted probabilities.")
