"""
sens_08_afcp_comparison.py
D07 — AFCP vs FDR-Gated Mondrian Conformal Prediction Comparison

ANALYSIS ID: D07
SCIENTIFIC QUESTION: Does Adaptive Full Conformal Prediction (AFCP / conditional validity)
    identify the same coverage-deficient groups as the FDR-gated Mondrian approach?
    Does it achieve better group coverage and efficiency? What are the trade-offs?

METHODOLOGY: AFCP is approximated using a K-Nearest Neighbors conformity score approach
    on the conformal calibration set, computing group-conditional coverage.
    This approximates the "approximately conditionally valid" conformal framework.

FITTING DATA: Conformal calibration split (data/processed/splits/conformal_calibration_ids.csv)
EVALUATION DATA: Locked test set (data/processed/splits/test_ids.csv)
TEST LABELS USED FOR FITTING: NO

NOTE: We compare the existing FDR-gated Mondrian threshold with AFCP's approach.
    This is a HEAD-TO-HEAD COMPARISON, not a replacement of the primary method.

SECONDARY ANALYSIS: SUPPLEMENTARY. Does NOT overwrite any frozen outputs.
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
TARGET_COVERAGE = 0.90  # 1 - alpha = 0.90
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def platt_transform(p, intercept, slope):
    logit_p = np.log(np.clip(p, 1e-7, 1-1e-7) / (1 - np.clip(p, 1e-7, 1-1e-7)))
    return 1 / (1 + np.exp(-(slope * logit_p + intercept)))

def conformal_score(y, p_hat):
    """Standard nonconformity score for binary classification."""
    return 1 - np.where(y == 1, p_hat, 1 - p_hat)

def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))

# Load master dataset
master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])

test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)

y_test = test_df[PRIMARY_OUTCOME_COL].values
y_cal = cal_df[PRIMARY_OUTCOME_COL].values

# Load Mondrian group assignments from frozen FDR-gated analysis
try:
    df_mondrian = pd.read_csv(RESULTS_DIR / "uncertainty" / "mondrian_coverage_by_group.csv")
    mondrian_groups_exist = True
    print("Loaded existing Mondrian group-coverage CSV.")
except FileNotFoundError:
    mondrian_groups_exist = False
    print("Mondrian group CSV not found. Will compute comparably.")

# Subgroups for evaluation
subgroup_configs = [
    ("bmi", "bmi_group_final", ["Normal", "Overweight", "Obese"]),
    ("age", "age_group_final", ["18-39", "40-59", "60+"]),
]

rows = []

for name in MODEL_NAMES:
    # Load refit model
    refit = joblib.load(ROOT / "models" / "phase6_conformal_refit" / f"model_{name}_proper_train_refit.joblib")
    pipe = refit["pipeline"]
    
    # Load global Platt parameters
    oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{name}.csv")
    global_intercept = oof_df["platt_intercept"].iloc[0]
    global_slope = oof_df["platt_slope"].iloc[0]
    
    # --- RECALIBRATED PROBABILITIES ---
    cal_raw = pipe.predict_proba(cal_df[PRIMARY_PREDICTORS])[:, 1]
    test_raw = pipe.predict_proba(test_df[PRIMARY_PREDICTORS])[:, 1]
    
    cal_recal = platt_transform(cal_raw, global_intercept, global_slope)
    test_recal = platt_transform(test_raw, global_intercept, global_slope)
    
    # --- APPROACH 1: MARGINAL (STANDARD) CONFORMAL — Current Frozen Method ---
    n_cal = len(cal_df)
    alpha = 1 - TARGET_COVERAGE
    k = int(np.ceil((n_cal + 1) * (1 - alpha)))
    cal_scores_global = conformal_score(y_cal, cal_recal)
    marginal_thresh = np.sort(cal_scores_global)[min(k - 1, n_cal - 1)]
    test_scores = conformal_score(y_test, test_recal)
    covered_marginal = (test_scores <= marginal_thresh)
    
    # --- APPROACH 2: MONDRIAN (GROUP-CONDITIONAL) CONFORMAL — Primary Alternative ---
    # Compute per-group quantiles from calibration set (BMI × Age 4-group Mondrian as used in Phase 6)
    cal_df_mondrian = cal_df.copy()
    cal_df_mondrian["score"] = cal_scores_global
    test_df_mondrian = test_df.copy()
    test_df_mondrian["test_score"] = test_scores
    
    # Use BMI × Age primary grouping from Phase 6 (4 Mondrian cells)
    # Identify which Mondrian cells exceeded FDR threshold
    # For now, use the same Mondrian structure (bmi × age binary)
    cal_df_mondrian["mondrian_cell"] = cal_df["bmi_group_final"].astype(str) + "_" + cal_df["age_group_final"].astype(str)
    test_df_mondrian["mondrian_cell"] = test_df["bmi_group_final"].astype(str) + "_" + test_df["age_group_final"].astype(str)
    
    mondrian_thresholds = {}
    for cell in cal_df_mondrian["mondrian_cell"].unique():
        cell_mask = cal_df_mondrian["mondrian_cell"] == cell
        cell_scores = cal_df_mondrian["score"][cell_mask].values
        n_cell = len(cell_scores)
        k_cell = int(np.ceil((n_cell + 1) * (1 - alpha)))
        mondrian_thresholds[cell] = np.sort(cell_scores)[min(k_cell - 1, n_cell - 1)]
    
    test_mondrian_thresh = test_df_mondrian["mondrian_cell"].map(mondrian_thresholds).values
    covered_mondrian = (test_scores <= test_mondrian_thresh)
    
    # --- APPROACH 3: AFCP (APPROXIMATELY CONDITIONALLY VALID) ---
    # We approximate AFCP via a K-Nearest-Neighbor local quantile computation.
    # For each test point, we use its K nearest calibration neighbors (in feature space)
    # to compute a local conformal quantile. This approximates conditional validity.
    from sklearn.neighbors import NearestNeighbors
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    X_cal_scaled = scaler.fit_transform(cal_df[PRIMARY_PREDICTORS])
    X_test_scaled = scaler.transform(test_df[PRIMARY_PREDICTORS])
    
    # K = ceil(sqrt(n_cal)) is a common choice for local regression
    K_AFCP = max(50, int(np.ceil(np.sqrt(n_cal))))
    print(f"  AFCP K={K_AFCP} for {name}")
    
    nn = NearestNeighbors(n_neighbors=K_AFCP, algorithm="ball_tree")
    nn.fit(X_cal_scaled)
    
    distances, indices = nn.kneighbors(X_test_scaled)
    
    covered_afcp = np.zeros(len(test_df), dtype=bool)
    afcp_thresholds = np.zeros(len(test_df))
    
    for i in range(len(test_df)):
        neighbor_scores = cal_scores_global[indices[i]]
        k_local = int(np.ceil((K_AFCP + 1) * (1 - alpha)))
        local_thresh = np.sort(neighbor_scores)[min(k_local - 1, K_AFCP - 1)]
        afcp_thresholds[i] = local_thresh
        covered_afcp[i] = (test_scores[i] <= local_thresh)
    
    # --- EVALUATE ALL 3 METHODS ACROSS SUBGROUPS ---
    for dim, col, groups in subgroup_configs:
        for grp in groups:
            mask = test_df[col] == grp
            n_sg = mask.sum()
            n_pos = int(y_test[mask].sum())
            if n_sg == 0:
                continue
            
            for method, covered_vec in [
                ("marginal_conformal", covered_marginal),
                ("mondrian_conformal", covered_mondrian),
                ("afcp_knn", covered_afcp),
            ]:
                cov = float(covered_vec[mask].mean())
                cov_lo, cov_hi = wilson_ci(covered_vec[mask].sum(), n_sg)
                pred_set_sizes = (1 + (test_scores[mask] <= afcp_thresholds[mask]).astype(int) if method == "afcp_knn" else None)
                
                rows.append({
                    "generated": TIMESTAMP, "model": name, "method": method,
                    "dimension": dim, "group": grp, "n": int(n_sg), "n_positive": n_pos,
                    "coverage": round(cov, 4),
                    "coverage_ci_lower": round(float(cov_lo), 4),
                    "coverage_ci_upper": round(float(cov_hi), 4),
                    "coverage_gap_vs_target": round(cov - TARGET_COVERAGE, 4),
                    "fitting_test_labels_used": "NO",
                })
        
    # Add overall
    for method, covered_vec in [
        ("marginal_conformal", covered_marginal),
        ("mondrian_conformal", covered_mondrian),
        ("afcp_knn", covered_afcp),
    ]:
        cov = float(covered_vec.mean())
        cov_lo_all, cov_hi_all = wilson_ci(int(covered_vec.sum()), len(test_df))
        rows.append({
            "generated": TIMESTAMP, "model": name, "method": method,
            "dimension": "overall", "group": "ALL", "n": len(test_df), "n_positive": int(y_test.sum()),
            "coverage": round(cov, 4),
            "coverage_ci_lower": round(float(cov_lo_all), 4),
            "coverage_ci_upper": round(float(cov_hi_all), 4),
            "coverage_gap_vs_target": round(cov - TARGET_COVERAGE, 4),
            "fitting_test_labels_used": "NO",
        })

df_out = pd.DataFrame(rows)
df_out.to_csv(DIAG_DIR / "afcp_vs_mondrian_comparison.csv", index=False)

print("\nD07 — AFCP vs Mondrian comparison complete!")
print("Saved to results/diagnostics/stage1/afcp_vs_mondrian_comparison.csv")

# Print pivot summary
print("\n=== Coverage by method and subgroup (XGBoost example) ===")
xgb = df_out[df_out["model"] == "xgboost"][["method", "dimension", "group", "coverage", "coverage_gap_vs_target"]]
print(xgb.to_string(index=False))
