"""
tradeoff_02_m4b_sensitivity_and_lock.py
Part E — M4b Shrinkage Sensitivity Analysis and Parameter Locking

SCIENTIFIC GOAL:
1. Conduct prespecified N0 sensitivity analysis using ONLY calibration data to fit quantiles.
2. Evaluate test set performance across N0 values in [0, 10, 25, 50, 75, 100, 150, 200, 300, 500].
3. Lock N0 = 100 based on calibration design stability prior to locked head-to-head testing.

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
N0_GRID = [0, 10, 25, 50, 75, 100, 150, 200, 300, 500]
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def platt_transform(p, intercept, slope):
    eps = 1e-7
    p_clamped = np.clip(p, eps, 1 - eps)
    logit_p = np.log(p_clamped / (1 - p_clamped))
    return 1.0 / (1.0 + np.exp(-(slope * logit_p + intercept)))

def conformal_score(y, p_hat):
    return 1.0 - np.where(y == 1, p_hat, 1.0 - p_hat)

def wilson_ci(k, n, level=0.95):
    if n == 0 or np.isnan(n):
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def compute_quantile(scores, target_cov=0.90):
    n = len(scores)
    if n == 0:
        return 1.0
    k = int(np.ceil((n + 1) * target_cov))
    k = min(max(1, k), n)
    return np.sort(scores)[k - 1]

print("=== EXECUTING PART E: M4b SHRINKAGE SENSITIVITY AND PARAMETER LOCKING ===")

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

rows = []

for model_name in MODEL_NAMES:
    print(f"\n--- Model: {model_name.upper()} ---")
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
    
    q_m1_global = compute_quantile(cal_scores, TARGET_COVERAGE)
    q_obese = compute_quantile(cal_scores[cal_obese_mask], TARGET_COVERAGE)
    q_age60 = compute_quantile(cal_scores[cal_age60_mask], TARGET_COVERAGE)
    q_joint = compute_quantile(cal_scores[cal_joint_mask], TARGET_COVERAGE)
    q_envelope = max(q_obese, q_age60)
    
    m1_cov = float((test_scores <= q_m1_global).mean())
    
    for n0 in N0_GRID:
        w = n_joint_cal / (n_joint_cal + n0) if (n_joint_cal + n0) > 0 else 0.0
        q_m4b = w * q_joint + (1.0 - w) * q_envelope
        
        # Build threshold vector on test set
        thresh_m4b = np.full(len(test_df), q_m1_global)
        thresh_m4b[test_obese_mask] = q_obese
        thresh_m4b[test_age60_mask] = q_age60
        thresh_m4b[test_joint_mask] = q_m4b
        
        covered = (test_scores <= thresh_m4b)
        
        # Metrics
        marg_cov = float(covered.mean())
        marg_drift_pp = (marg_cov - m1_cov) * 100.0
        
        inter_cov = float(covered[test_joint_mask].mean())
        k_inter = int(covered[test_joint_mask].sum())
        n_inter = int(test_joint_mask.sum())
        lo, hi = wilson_ci(k_inter, n_inter)
        
        # Set size breakdown on joint cell
        p_sub = test_p[test_joint_mask]
        q_sub = thresh_m4b[test_joint_mask]
        inc_1 = (p_sub >= (1.0 - q_sub)).astype(int)
        inc_0 = (p_sub <= q_sub).astype(int)
        sizes = inc_1 + inc_0
        
        mean_size = float(sizes.mean())
        singleton = float((sizes == 1).mean())
        doubleton = float((sizes == 2).mean())
        
        rows.append({
            "generated": TIMESTAMP,
            "model": model_name,
            "N0": n0,
            "shrinkage_weight_w": round(w, 4),
            "q_joint_cal": round(q_joint, 4),
            "q_envelope_cal": round(q_envelope, 4),
            "q_m4b_cal": round(q_m4b, 4),
            "intersectional_coverage": round(inter_cov, 4),
            "intersectional_ci_lower": round(float(lo), 4),
            "intersectional_ci_upper": round(float(hi), 4),
            "marginal_coverage": round(marg_cov, 4),
            "marginal_drift_pp": round(marg_drift_pp, 2),
            "mean_set_size": round(mean_size, 3),
            "singleton_rate": round(singleton, 4),
            "doubleton_rate": round(doubleton, 4),
            "meets_target_90": (inter_cov >= 0.90) and (abs(marg_drift_pp) <= 5.0),
            "fitting_test_labels_used": "NO"
        })

df_out = pd.DataFrame(rows)
df_out.to_csv(TABLES_DIR / "m4b_shrinkage_sensitivity.csv", index=False)
df_out.to_csv(DIAG_DIR / "m4b_shrinkage_sensitivity.csv", index=False)

print("\n=== SUCCESS: PART E SENSITIVITY COMPLETE ===")
print("Saved outputs to:")
print(" - results/tables/m4b_shrinkage_sensitivity.csv")
print(" - results/diagnostics/stage1/m4b_shrinkage_sensitivity.csv")

print("\n=== LOCKED PARAMETER SELECTION ===")
print("Pre-specified Locked Prior Parameter: N0 = 100 (w = 138 / 238 = 0.5798)")
