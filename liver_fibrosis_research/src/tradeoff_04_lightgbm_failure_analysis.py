"""
tradeoff_04_lightgbm_failure_analysis.py
Part F — Deep Diagnostic Audit: Why Does LightGBM Fail M4b Intersectional Target?

SCIENTIFIC GOAL:
Investigate why M4b succeeds for Logistic, RF, XGBoost, and MLP (achieving >=90% coverage),
but achieves only 87.07% coverage for LightGBM.
Use calibration split distributions, score dispersion, quantile gaps, and prediction set breakdowns.

FITTING DATA: Conformal calibration split (data/processed/splits/conformal_calibration_ids.csv, N=1,002)
EVALUATION DATA: Locked test set (data/processed/splits/test_ids.csv, N=2,146)
TEST LABELS USED FOR FITTING: NO — all quantiles fit on calibration split only.
"""

import datetime
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
DIAG_DIR = RESULTS_DIR / "diagnostics" / "stage1"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
DIAG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PRIMARY_PREDICTORS = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
    "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"
]
PRIMARY_OUTCOME_COL = "outcome_primary_8.2kPa"
TARGET_COVERAGE = 0.90
LOCKED_N0 = 100.0
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def platt_transform(p, intercept, slope):
    eps = 1e-7
    p_clamped = np.clip(p, eps, 1 - eps)
    logit_p = np.log(p_clamped / (1 - p_clamped))
    return 1.0 / (1.0 + np.exp(-(slope * logit_p + intercept)))

def conformal_score(y, p_hat):
    return 1.0 - np.where(y == 1, p_hat, 1.0 - p_hat)

def compute_quantile(scores, target_cov=0.90):
    n = len(scores)
    if n == 0:
        return 1.0
    k = int(np.ceil((n + 1) * target_cov))
    k = min(max(1, k), n)
    return np.sort(scores)[k - 1]

print("=== EXECUTING PART F: LIGHTGBM FAILURE DIAGNOSTIC AUDIT ===")

master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])

test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)

y_test = test_df[PRIMARY_OUTCOME_COL].values
y_cal = cal_df[PRIMARY_OUTCOME_COL].values

test_obese_mask = (test_df["bmi_group_final"] == "Obese").values
test_age60_mask = (test_df["age_group_final"] == "60+").values
test_joint_mask = test_obese_mask & test_age60_mask

cal_obese_mask = (cal_df["bmi_group_final"] == "Obese").values
cal_age60_mask = (cal_df["age_group_final"] == "60+").values
cal_joint_mask = cal_obese_mask & cal_age60_mask
n_joint_cal = int(cal_joint_mask.sum())
w_locked = n_joint_cal / (n_joint_cal + LOCKED_N0)

rows = []

for model_name in MODEL_NAMES:
    print(f"\n--- Diagnostics for Model: {model_name.upper()} ---")
    refit_path = ROOT / "models" / "phase6_conformal_refit" / f"model_{model_name}_proper_train_refit.joblib"
    refit = joblib.load(refit_path)
    pipe = refit["pipeline"]
    
    oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{model_name}.csv")
    global_intercept = oof_df["platt_intercept"].iloc[0]
    global_slope = oof_df["platt_slope"].iloc[0]
    
    cal_raw = pipe.predict_proba(cal_df[PRIMARY_PREDICTORS])[:, 1]
    test_raw = pipe.predict_proba(test_df[PRIMARY_PREDICTORS])[:, 1]
    
    cal_p = platt_transform(cal_raw, global_intercept, global_slope)
    test_p = platt_transform(test_raw, global_intercept, global_slope)
    
    cal_scores = conformal_score(y_cal, cal_p)
    test_scores = conformal_score(y_test, test_p)
    
    # Quantiles on calibration set
    q_global = compute_quantile(cal_scores, TARGET_COVERAGE)
    q_obese = compute_quantile(cal_scores[cal_obese_mask], TARGET_COVERAGE)
    q_age60 = compute_quantile(cal_scores[cal_age60_mask], TARGET_COVERAGE)
    q_joint = compute_quantile(cal_scores[cal_joint_mask], TARGET_COVERAGE)
    q_envelope = max(q_obese, q_age60)
    q_m4b = w_locked * q_joint + (1.0 - w_locked) * q_envelope
    
    # Calibration joint cell score statistics
    cal_joint_scores = cal_scores[cal_joint_mask]
    cal_joint_mean = float(cal_joint_scores.mean())
    cal_joint_std = float(cal_joint_scores.std())
    cal_joint_median = float(np.median(cal_joint_scores))
    cal_joint_p90 = float(np.percentile(cal_joint_scores, 90))
    cal_joint_skew = float(stats.skew(cal_joint_scores))
    
    # Test joint cell score statistics
    test_joint_scores = test_scores[test_joint_mask]
    test_joint_mean = float(test_joint_scores.mean())
    test_joint_std = float(test_joint_scores.std())
    test_joint_p90 = float(np.percentile(test_joint_scores, 90))
    
    # Quantile gap and shrinkage deficit
    quantile_gap_cal = q_joint - q_envelope
    shrinkage_deficit = q_joint - q_m4b
    
    # Test performance of M4b
    thresh_m4b = np.full(len(test_df), q_global)
    thresh_m4b[test_obese_mask] = q_obese
    thresh_m4b[test_age60_mask] = q_age60
    thresh_m4b[test_joint_mask] = q_m4b
    
    test_cov_m4b = float((test_scores <= thresh_m4b)[test_joint_mask].mean())
    
    # Set size breakdown on test joint cell
    p_sub = test_p[test_joint_mask]
    q_sub = thresh_m4b[test_joint_mask]
    inc_1 = (p_sub >= (1.0 - q_sub)).astype(int)
    inc_0 = (p_sub <= q_sub).astype(int)
    sizes = inc_1 + inc_0
    
    mean_size = float(sizes.mean())
    singleton_rate = float((sizes == 1).mean())
    doubleton_rate = float((sizes == 2).mean())
    empty_rate = float((sizes == 0).mean())
    
    # Out-of-bounds score count on test set above q_m4b
    oob_count = int((test_joint_scores > q_m4b).sum())
    
    rows.append({
        "generated": TIMESTAMP,
        "model": model_name,
        "is_lightgbm": (model_name == "lightgbm"),
        "calibration_joint_cell_n": n_joint_cal,
        "q_global_cal": round(q_global, 4),
        "q_obese_cal": round(q_obese, 4),
        "q_age60_cal": round(q_age60, 4),
        "q_joint_cal": round(q_joint, 4),
        "q_envelope_cal": round(q_envelope, 4),
        "q_m4b_cal": round(q_m4b, 4),
        "quantile_gap_joint_vs_envelope": round(quantile_gap_cal, 4),
        "shrinkage_deficit": round(shrinkage_deficit, 4),
        "cal_joint_score_mean": round(cal_joint_mean, 4),
        "cal_joint_score_std": round(cal_joint_std, 4),
        "cal_joint_score_p90": round(cal_joint_p90, 4),
        "test_joint_score_mean": round(test_joint_mean, 4),
        "test_joint_score_p90": round(test_joint_p90, 4),
        "test_intersectional_coverage_m4b": round(test_cov_m4b, 4),
        "meets_90_target": (test_cov_m4b >= 0.90),
        "test_out_of_bounds_count": oob_count,
        "test_joint_mean_set_size": round(mean_size, 3),
        "test_joint_singleton_rate": round(singleton_rate, 4),
        "test_joint_doubleton_rate": round(doubleton_rate, 4),
        "test_joint_empty_rate": round(empty_rate, 4),
        "fitting_test_labels_used": "NO"
    })

df_out = pd.DataFrame(rows)
df_out.to_csv(TABLES_DIR / "m4b_lightgbm_failure_analysis.csv", index=False)
df_out.to_csv(DIAG_DIR / "m4b_lightgbm_failure_analysis.csv", index=False)

print("\n=== SUCCESS: PART F AUDIT EXECUTED CLEANLY ===")
print("Saved outputs to:")
print(" - results/tables/m4b_lightgbm_failure_analysis.csv")
print(" - results/diagnostics/stage1/m4b_lightgbm_failure_analysis.csv")
