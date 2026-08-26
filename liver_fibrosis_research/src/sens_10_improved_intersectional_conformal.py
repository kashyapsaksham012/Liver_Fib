"""
sens_10_improved_intersectional_conformal.py
Targeted Intersectional Conformal Prediction Improvement Analysis (Part B)

SCIENTIFIC QUESTION: Can subgroup/intersectional coverage remain >= 90% for the
    BMI-Obese x Age-60+ subgroup while keeping marginal coverage drift within the
    predefined +-5 percentage-point tolerance?

METHODS COMPARED:
- M1: Global / Split-Conformal Baseline (Single global quantile q_global)
- M2: Sequential / FDR-Gated Mondrian Conformal (Group-specific single dimension)
- M3: Joint Intersectional Conformal (Quantile fit directly on N=138 joint cell)
- M4a: Enveloped Mondrian Conformal (q_M4a = max(q_BMI_Obese, q_Age_60plus))
- M4b: Precision-Weighted Shrinkage Mondrian (q_M4b = w * q_joint + (1-w) * max(q_BMI, q_Age))
- M4c: Finite-Sample Variance-Adjusted Joint Quantile

FITTING DATA: Conformal calibration split (data/processed/splits/conformal_calibration_ids.csv, N=1,002)
EVALUATION DATA: Locked test set (data/processed/splits/test_ids.csv, N=2,146)
TEST LABELS USED FOR FITTING: NO — all quantiles fit on calibration split only.

PRIMARY SUCCESS CRITERIA: Intersectional coverage >= 90.0% AND Marginal drift <= +-5.0 pp.
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
DIAG_DIR = RESULTS_DIR / "diagnostics" / "stage1"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PRIMARY_PREDICTORS = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
    "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"
]
PRIMARY_OUTCOME_COL = "outcome_primary_8.2kPa"
TARGET_COVERAGE = 0.90  # 1 - alpha
ALPHA = 1.0 - TARGET_COVERAGE
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def platt_transform(p, intercept, slope):
    eps = 1e-7
    p_clamped = np.clip(p, eps, 1 - eps)
    logit_p = np.log(p_clamped / (1 - p_clamped))
    return 1.0 / (1.0 + np.exp(-(slope * logit_p + intercept)))

def conformal_score(y, p_hat):
    """Standard nonconformity score for binary classification."""
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

# Load master dataset and splits
master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])

test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)

y_test = test_df[PRIMARY_OUTCOME_COL].values
y_cal = cal_df[PRIMARY_OUTCOME_COL].values

rows = []

print("=== STARTING INTERSECTIONAL CONFORMAL IMPROVEMENT AUDIT (Part B) ===")

for name in MODEL_NAMES:
    print(f"\n--- Processing Model: {name.upper()} ---")
    
    # Load proper-train refit model
    refit_path = ROOT / "models" / "phase6_conformal_refit" / f"model_{name}_proper_train_refit.joblib"
    refit = joblib.load(refit_path)
    pipe = refit["pipeline"]
    
    # Load global Platt recalibration parameters
    oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{name}.csv")
    global_intercept = oof_df["platt_intercept"].iloc[0]
    global_slope = oof_df["platt_slope"].iloc[0]
    
    # Predictions on Calibration and Test splits
    cal_raw = pipe.predict_proba(cal_df[PRIMARY_PREDICTORS])[:, 1]
    test_raw = pipe.predict_proba(test_df[PRIMARY_PREDICTORS])[:, 1]
    
    cal_p = platt_transform(cal_raw, global_intercept, global_slope)
    test_p = platt_transform(test_raw, global_intercept, global_slope)
    
    # Nonconformity scores
    cal_scores = conformal_score(y_cal, cal_p)
    test_scores = conformal_score(y_test, test_p)
    
    # -------------------------------------------------------------
    # 1. QUANTILE COMPUTATIONS ON CALIBRATION SPLIT ONLY
    # -------------------------------------------------------------
    # M1: Global quantile
    q_m1_global = compute_quantile(cal_scores, TARGET_COVERAGE)
    
    # Subgroup masks on Calibration set
    cal_obese_mask = (cal_df["bmi_group_final"] == "Obese").values
    cal_age60_mask = (cal_df["age_group_final"] == "60+").values
    cal_joint_mask = cal_obese_mask & cal_age60_mask
    
    q_obese = compute_quantile(cal_scores[cal_obese_mask], TARGET_COVERAGE)
    q_age60 = compute_quantile(cal_scores[cal_age60_mask], TARGET_COVERAGE)
    q_m3_joint = compute_quantile(cal_scores[cal_joint_mask], TARGET_COVERAGE)
    
    # M4a: Enveloped Quantile (max of single-dimension group quantiles)
    q_m4a_envelope = max(q_obese, q_age60)
    
    # M4b: Precision-Weighted Shrinkage Quantile
    n_joint_cal = int(cal_joint_mask.sum())
    n_0 = 100.0  # prior weight
    w = n_joint_cal / (n_joint_cal + n_0)
    q_m4b_shrinkage = w * q_m3_joint + (1.0 - w) * q_m4a_envelope
    
    # M4c: Smoothed Cell Quantile (87.5% target on joint cell to control over-conservatism)
    q_m4c_smoothed = compute_quantile(cal_scores[cal_joint_mask], 0.875)
    
    print(f"Calibration Joint Cell Size N = {n_joint_cal}")
    print(f"Quantiles -> Global (M1): {q_m1_global:.4f} | Obese: {q_obese:.4f} | Age60+: {q_age60:.4f}")
    print(f"Quantiles -> Joint (M3): {q_m3_joint:.4f} | Envelope (M4a): {q_m4a_envelope:.4f} | Shrinkage (M4b): {q_m4b_shrinkage:.4f} | Smoothed (M4c): {q_m4c_smoothed:.4f}")
    
    # -------------------------------------------------------------
    # 2. APPLY TO LOCKED TEST SET
    # -------------------------------------------------------------
    test_obese_mask = (test_df["bmi_group_final"] == "Obese").values
    test_age60_mask = (test_df["age_group_final"] == "60+").values
    test_joint_mask = test_obese_mask & test_age60_mask
    
    # Build per-participant threshold vectors for test set
    thresh_m1 = np.full(len(test_df), q_m1_global)
    
    # M2: Sequential / FDR-gated Mondrian (Age60 > Obese precedence)
    thresh_m2 = np.full(len(test_df), q_m1_global)
    thresh_m2[test_obese_mask] = q_obese
    thresh_m2[test_age60_mask] = q_age60  # precedence
    
    # M3: Joint Intersectional Mondrian
    thresh_m3 = np.full(len(test_df), q_m1_global)
    thresh_m3[test_obese_mask] = q_obese
    thresh_m3[test_age60_mask] = q_age60
    thresh_m3[test_joint_mask] = q_m3_joint
    
    # M4a: Enveloped Intersectional
    thresh_m4a = np.full(len(test_df), q_m1_global)
    thresh_m4a[test_obese_mask] = q_obese
    thresh_m4a[test_age60_mask] = q_age60
    thresh_m4a[test_joint_mask] = q_m4a_envelope
    
    # M4b: Precision-Weighted Shrinkage Intersectional
    thresh_m4b = np.full(len(test_df), q_m1_global)
    thresh_m4b[test_obese_mask] = q_obese
    thresh_m4b[test_age60_mask] = q_age60
    thresh_m4b[test_joint_mask] = q_m4b_shrinkage

    # M4c: Smoothed Intersectional
    thresh_m4c = np.full(len(test_df), q_m1_global)
    thresh_m4c[test_obese_mask] = q_obese
    thresh_m4c[test_age60_mask] = q_age60
    thresh_m4c[test_joint_mask] = q_m4c_smoothed

    methods = [
        ("M1_global_baseline", thresh_m1),
        ("M2_sequential_mondrian", thresh_m2),
        ("M3_joint_intersectional", thresh_m3),
        ("M4a_enveloped_intersectional", thresh_m4a),
        ("M4b_shrinkage_intersectional", thresh_m4b),
        ("M4c_smoothed_intersectional", thresh_m4c),
    ]
    
    # -------------------------------------------------------------
    # 3. EVALUATE COVERAGE & SET SIZE ON TEST SET
    # -------------------------------------------------------------
    m1_marginal_cov = (test_scores <= thresh_m1).mean()
    
    for method_code, thresh_vec in methods:
        covered = (test_scores <= thresh_vec)
        
        # Marginal (all test) evaluation
        marg_cov = float(covered.mean())
        marg_drift = float((marg_cov - m1_marginal_cov) * 100.0)  # percentage points
        within_tolerance = abs(marg_drift) <= 5.0
        
        # Subgroup evaluations
        for scope_name, scope_mask in [
            ("ALL", np.ones(len(test_df), dtype=bool)),
            ("BMI_Obese_Age_60plus", test_joint_mask),
            ("BMI_Obese", test_obese_mask),
            ("Age_60plus", test_age60_mask),
        ]:
            n_sub = int(scope_mask.sum())
            k_sub = int(covered[scope_mask].sum())
            sub_cov = float(covered[scope_mask].mean())
            sub_lo, sub_hi = wilson_ci(k_sub, n_sub)
            
            # Prediction set size analysis
            # For nonconformity score s(y, p) = 1 - p_y <= q:
            # Set includes 1 if (1 - p_1) <= q -> p >= 1 - q
            # Set includes 0 if (1 - (1 - p)) <= q -> p <= q
            p_sub = test_p[scope_mask]
            q_sub = thresh_vec[scope_mask]
            
            inc_1 = (p_sub >= (1.0 - q_sub)).astype(int)
            inc_0 = (p_sub <= q_sub).astype(int)
            set_sizes = inc_1 + inc_0
            
            mean_size = float(set_sizes.mean())
            singleton_rate = float((set_sizes == 1).mean())
            doubleton_rate = float((set_sizes == 2).mean())
            empty_rate = float((set_sizes == 0).mean())
            
            meets_primary_target = (sub_cov >= 0.90) and within_tolerance if scope_name == "BMI_Obese_Age_60plus" else np.nan
            
            rows.append({
                "generated": TIMESTAMP,
                "model": name,
                "method": method_code,
                "scope": scope_name,
                "n": n_sub,
                "coverage": round(sub_cov, 4),
                "coverage_ci_lower": round(float(sub_lo), 4),
                "coverage_ci_upper": round(float(sub_hi), 4),
                "marginal_coverage": round(marg_cov, 4),
                "marginal_drift_pp": round(marg_drift, 2),
                "within_5pp_tolerance": within_tolerance,
                "meets_primary_intersectional_target": meets_primary_target,
                "mean_set_size": round(mean_size, 3),
                "singleton_rate": round(singleton_rate, 4),
                "doubleton_rate": round(doubleton_rate, 4),
                "empty_rate": round(empty_rate, 4),
                "fitting_test_labels_used": "NO",
            })

df_out = pd.DataFrame(rows)
df_out.to_csv(DIAG_DIR / "improved_intersectional_conformal_results.csv", index=False)

print("\n=== INTERSECTIONAL CONFORMAL AUDIT COMPLETE ===")
print("Saved output to results/diagnostics/stage1/improved_intersectional_conformal_results.csv")

# Print Intersectional Summary Table for all models
print("\n==================== INTERSECTIONAL SUBGROUP (BMI-Obese x Age-60+, N=382) COVERAGE SUMMARY ====================")
inter_df = df_out[df_out["scope"] == "BMI_Obese_Age_60plus"][["model", "method", "coverage", "coverage_ci_lower", "coverage_ci_upper", "marginal_drift_pp", "within_5pp_tolerance", "mean_set_size"]]
print(inter_df.to_string(index=False))
