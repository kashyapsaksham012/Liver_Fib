"""
tradeoff_03_head_to_head_conformal.py
Part C, Part D, Part G — Head-to-Head Conformal Trade-off Analysis & Classification

SCIENTIFIC GOAL:
1. Compare M1 (Global), M2 (Sequential Mondrian), M3 (Joint Intersectional), and M4b (Shrinkage, Locked N0=100).
2. Report Reliability, Fairness, Efficiency, and Trade-off metrics across all 5 models.
3. Classify every method/model against predefined success criterion: Intersectional Coverage >= 90.0% AND Drift <= +-5.0 pp.

FITTING DATA: Conformal calibration split (data/processed/splits/conformal_calibration_ids.csv, N=1,002)
EVALUATION DATA: Locked test set (data/processed/splits/test_ids.csv, N=2,146)
TEST LABELS USED FOR FITTING: NO — strictly calibration split quantiles.
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

print("=== EXECUTING PART C, D, G: HEAD-TO-HEAD CONFORMAL TRADE-OFF AUDIT ===")

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
    print(f"\n--- Processing Model: {model_name.upper()} ---")
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
    
    # Fit quantiles on calibration split
    q_m1_global = compute_quantile(cal_scores, TARGET_COVERAGE)
    q_obese = compute_quantile(cal_scores[cal_obese_mask], TARGET_COVERAGE)
    q_age60 = compute_quantile(cal_scores[cal_age60_mask], TARGET_COVERAGE)
    q_m3_joint = compute_quantile(cal_scores[cal_joint_mask], TARGET_COVERAGE)
    q_envelope = max(q_obese, q_age60)
    q_m4b_shrinkage = w_locked * q_m3_joint + (1.0 - w_locked) * q_envelope
    
    # Participant threshold vectors on test set
    thresh_m1 = np.full(len(test_df), q_m1_global)
    
    thresh_m2 = np.full(len(test_df), q_m1_global)
    thresh_m2[test_obese_mask] = q_obese
    thresh_m2[test_age60_mask] = q_age60  # Age-60+ precedence
    
    thresh_m3 = np.full(len(test_df), q_m1_global)
    thresh_m3[test_obese_mask] = q_obese
    thresh_m3[test_age60_mask] = q_age60
    thresh_m3[test_joint_mask] = q_m3_joint
    
    thresh_m4b = np.full(len(test_df), q_m1_global)
    thresh_m4b[test_obese_mask] = q_obese
    thresh_m4b[test_age60_mask] = q_age60
    thresh_m4b[test_joint_mask] = q_m4b_shrinkage
    
    methods = [
        ("M1_global_baseline", thresh_m1),
        ("M2_sequential_mondrian", thresh_m2),
        ("M3_pure_joint_intersectional", thresh_m3),
        ("M4b_shrinkage_intersectional", thresh_m4b),
    ]
    
    # M1 baseline values for trade-off calculation
    m1_covered = (test_scores <= thresh_m1)
    m1_marg_cov = float(m1_covered.mean())
    m1_inter_cov = float(m1_covered[test_joint_mask].mean())
    
    inc1_m1 = (test_p >= (1.0 - thresh_m1)).astype(int)
    inc0_m1 = (test_p <= thresh_m1).astype(int)
    m1_mean_size_all = float((inc1_m1 + inc0_m1).mean())
    
    for method_code, thresh_vec in methods:
        covered = (test_scores <= thresh_vec)
        
        # Reliability
        marg_cov = float(covered.mean())
        inter_cov = float(covered[test_joint_mask].mean())
        k_inter = int(covered[test_joint_mask].sum())
        n_inter = int(test_joint_mask.sum())
        inter_lo, inter_hi = wilson_ci(k_inter, n_inter)
        
        # Fairness
        coverage_disparity = abs(marg_cov - inter_cov)
        intersectional_gap = inter_cov - marg_cov
        
        # Efficiency (overall test & joint cell)
        inc1 = (test_p >= (1.0 - thresh_vec)).astype(int)
        inc0 = (test_p <= thresh_vec).astype(int)
        set_sizes = inc1 + inc0
        
        mean_size_all = float(set_sizes.mean())
        singleton_all = float((set_sizes == 1).mean())
        doubleton_all = float((set_sizes == 2).mean())
        
        set_sizes_joint = set_sizes[test_joint_mask]
        mean_size_joint = float(set_sizes_joint.mean())
        singleton_joint = float((set_sizes_joint == 1).mean())
        doubleton_joint = float((set_sizes_joint == 2).mean())
        
        # Trade-off metrics
        marg_drift_pp = (marg_cov - m1_marg_cov) * 100.0
        change_set_size = mean_size_all - m1_mean_size_all
        improvement_inter_cov_pp = (inter_cov - m1_inter_cov) * 100.0
        
        # Classification against predefined success criteria
        # Intersectional coverage >= 90% AND |drift| <= 5 pp
        meets_cov = (inter_cov >= 0.90)
        meets_drift = (abs(marg_drift_pp) <= 5.0)
        
        if meets_cov and meets_drift:
            status = "SUCCESS"
        elif (inter_cov >= 0.88 and meets_drift) or (meets_cov and abs(marg_drift_pp) <= 6.0):
            status = "PARTIAL"
        else:
            status = "FAILURE"
            
        rows.append({
            "generated": TIMESTAMP,
            "model": model_name,
            "method": method_code,
            "locked_N0": LOCKED_N0,
            "intersectional_coverage": round(inter_cov, 4),
            "intersectional_ci_lower": round(float(inter_lo), 4),
            "intersectional_ci_upper": round(float(inter_hi), 4),
            "marginal_coverage": round(marg_cov, 4),
            "subgroup_coverage_disparity": round(coverage_disparity, 4),
            "intersectional_vs_marginal_gap": round(intersectional_gap, 4),
            "overall_mean_set_size": round(mean_size_all, 3),
            "overall_singleton_rate": round(singleton_all, 4),
            "overall_doubleton_rate": round(doubleton_all, 4),
            "joint_mean_set_size": round(mean_size_joint, 3),
            "joint_singleton_rate": round(singleton_joint, 4),
            "joint_doubleton_rate": round(doubleton_joint, 4),
            "marginal_coverage_drift_pp": round(marg_drift_pp, 2),
            "change_in_set_size": round(change_set_size, 3),
            "improvement_in_intersectional_cov_pp": round(improvement_inter_cov_pp, 2),
            "predefined_status": status,
            "fitting_test_labels_used": "NO"
        })

df_out = pd.DataFrame(rows)
df_out.to_csv(TABLES_DIR / "conformal_tradeoff_comparison.csv", index=False)
df_out.to_csv(DIAG_DIR / "conformal_tradeoff_comparison.csv", index=False)

print("\n=== SUCCESS: PART C, D, G EXECUTED CLEANLY ===")
print("Saved outputs to:")
print(" - results/tables/conformal_tradeoff_comparison.csv")
print(" - results/diagnostics/stage1/conformal_tradeoff_comparison.csv")
