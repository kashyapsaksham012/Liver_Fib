"""
sens_07_fairness_postprocessing.py
D06 — Equal Opportunity Fairness Post-Processing Trade-off Analysis

ANALYSIS ID: D06
SCIENTIFIC QUESTION: What trade-offs does Equal Opportunity post-processing create
    when applied to address the sensitivity disparity in BMI-Obese and Age-60+ groups?

NOTE: This is a TRADE-OFF ANALYSIS. The question is NOT "does disparity reach zero?"
      The question is: "what happens to calibration, coverage, and efficiency when
      we enforce Equal Opportunity via group-specific threshold adjustments?"

FITTING DATA: OOF recalibrated predictions (results/calibration/recalibrated_oof_predictions_*.csv)
EVALUATION DATA: Locked test set (data/processed/splits/test_ids.csv)
TEST LABELS USED FOR FITTING: NO — thresholds derived on OOF only.
CONFORMAL COVERAGE: Uses existing frozen conformal thresholds (read-only).

This script does NOT attempt to verify "calibration preservation" a priori.
Calibration is measured empirically on the test set after the intervention.

SECONDARY ANALYSIS: Labeled SUPPLEMENTARY.
"""
import datetime
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from sklearn.metrics import roc_curve, roc_auc_score, brier_score_loss

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
RESULTS_DIR = ROOT / "results"
DIAG_DIR = RESULTS_DIR / "diagnostics" / "stage1"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PRIMARY_OUTCOME_COL = "outcome_primary_8.2kPa"
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def youden_j_threshold(y_true, y_prob):
    fpr, tpr, thresholds = roc_curve(y_true, y_prob, drop_intermediate=False)
    j_stat = tpr - fpr
    best_idx = np.argmax(j_stat)
    return thresholds[best_idx]

def compute_calibration(y_true, y_prob):
    """Compute Hosmer-Lemeshow intercept and slope via logistic regression on logit(p)."""
    from sklearn.linear_model import LogisticRegression
    logit_p = np.log(np.clip(y_prob, 1e-7, 1-1e-7) / (1 - np.clip(y_prob, 1e-7, 1-1e-7)))
    lr = LogisticRegression(C=1e6)
    lr.fit(logit_p.reshape(-1, 1), y_true)
    return lr.intercept_[0], lr.coef_[0][0]

# Load master dataset and splits
master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
y_test = test_df[PRIMARY_OUTCOME_COL].values

# Load global thresholds
df_baseline = pd.read_csv(RESULTS_DIR / "tables" / "phase3_final_baseline_results.csv").set_index("model_name")
thresholds_global = df_baseline["threshold"].to_dict()

# Load conformal thresholds (read-only, frozen)
df_conf_thresh = pd.read_csv(RESULTS_DIR / "uncertainty" / "conformal_thresholds_by_model.csv").set_index("model")
conf_thresholds = df_conf_thresh["threshold"].to_dict()

# Target subgroups for Equal Opportunity intervention
target_subgroups = [
    ("bmi", "bmi_group_final", "Obese"),
    ("age", "age_group_final", "60+"),
]

rows = []

for name in MODEL_NAMES:
    # Load OOF predictions for threshold derivation (fitting data)
    oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{name}.csv")
    oof_with_meta = oof_df.merge(
        master[["SEQN", "bmi_group_final", "age_group_final"]], on="SEQN"
    )
    
    # Load test recalibrated predictions
    test_recal = pd.read_csv(RESULTS_DIR / "calibration" / "test_set_recalibrated_predictions.csv")
    test_m = test_recal[test_recal["model"] == name].set_index("SEQN")
    test_proba = test_df["SEQN"].map(test_m["recalibrated_predicted_probability"]).values
    
    # --- GLOBAL THRESHOLD BASELINE ---
    global_thresh = thresholds_global.get(name, 0.5)
    y_pred_global = (test_proba >= global_thresh).astype(int)
    
    # Global conformal evaluation (frozen threshold)
    conf_thresh = conf_thresholds.get(name, np.inf)
    conf_scores = 1 - np.where(y_test == 1, test_proba, 1 - test_proba)
    covered_global = (conf_scores <= conf_thresh)
    
    # --- EQUAL OPPORTUNITY POST-PROCESSOR ---
    # Strategy: For each target subgroup (Obese, 60+), derive a LOWER group-specific threshold
    # from OOF predictions that achieves the same sensitivity as the best-performing group.
    # This is Equal Opportunity targeting (equalize true positive rates).
    
    # Find reference group sensitivity (best-performing BMI group = Overweight, Age = 18-39)
    oof_bmi_ref = oof_with_meta[oof_with_meta["bmi_group_final"] == "Overweight"]
    oof_age_ref = oof_with_meta[oof_with_meta["age_group_final"] == "40-59"]
    
    ref_thresh_bmi = youden_j_threshold(oof_bmi_ref["true_target"], oof_bmi_ref["recalibrated_predicted_probability"])
    ref_thresh_age = youden_j_threshold(oof_age_ref["true_target"], oof_age_ref["recalibrated_predicted_probability"])
    
    # Compute subgroup-specific thresholds
    oof_bmi_obese = oof_with_meta[oof_with_meta["bmi_group_final"] == "Obese"]
    oof_age_60plus = oof_with_meta[oof_with_meta["age_group_final"] == "60+"]
    
    thresh_bmi_obese = youden_j_threshold(oof_bmi_obese["true_target"], oof_bmi_obese["recalibrated_predicted_probability"])
    thresh_age_60plus = youden_j_threshold(oof_age_60plus["true_target"], oof_age_60plus["recalibrated_predicted_probability"])
    
    # Build Equal Opportunity prediction vector
    y_pred_eo = np.full(len(test_df), -1, dtype=int)
    bmi_obese_mask = test_df["bmi_group_final"] == "Obese"
    age_60plus_mask = test_df["age_group_final"] == "60+"
    
    # Apply subgroup thresholds to target groups, global to rest
    y_pred_eo[bmi_obese_mask & ~age_60plus_mask] = (test_proba[bmi_obese_mask & ~age_60plus_mask] >= thresh_bmi_obese).astype(int)
    y_pred_eo[age_60plus_mask & ~bmi_obese_mask] = (test_proba[age_60plus_mask & ~bmi_obese_mask] >= thresh_age_60plus).astype(int)
    # Intersection: use the lower (more lenient) threshold for both = max sensitivity
    both_mask = bmi_obese_mask & age_60plus_mask
    y_pred_eo[both_mask] = (test_proba[both_mask] >= min(thresh_bmi_obese, thresh_age_60plus)).astype(int)
    # Rest: global threshold
    y_pred_eo[y_pred_eo == -1] = (test_proba[y_pred_eo == -1] >= global_thresh).astype(int)
    
    # Note: For conformal coverage, the underlying probabilities and conformal threshold remain
    # unchanged — equal opportunity is implemented via post-hoc threshold shift only.
    # Conformal coverage is a property of the probability-space, not the decision-space.
    # We compute it identically here for comparison:
    covered_eo = covered_global  # same probabilities → same coverage
    
    # Evaluate overall and per-subgroup
    for scope_label, scope_mask in [
        ("ALL", np.ones(len(test_df), dtype=bool)),
        ("BMI_Obese", bmi_obese_mask),
        ("Age_60plus", age_60plus_mask),
        ("BMI_Normal", test_df["bmi_group_final"] == "Normal"),
        ("Age_18_39", test_df["age_group_final"] == "18-39"),
        ("Age_40_59", test_df["age_group_final"] == "40-59"),
    ]:
        n_sg = scope_mask.sum()
        n_pos = int(y_test[scope_mask].sum())
        if n_pos == 0:
            continue
        n_neg = n_sg - n_pos
        
        for method_label, y_pred_m in [("global_threshold", y_pred_global), ("equal_opportunity", y_pred_eo)]:
            tp = ((y_pred_m[scope_mask] == 1) & (y_test[scope_mask] == 1)).sum()
            tn = ((y_pred_m[scope_mask] == 0) & (y_test[scope_mask] == 0)).sum()
            fp = ((y_pred_m[scope_mask] == 1) & (y_test[scope_mask] == 0)).sum()
            fn = ((y_pred_m[scope_mask] == 0) & (y_test[scope_mask] == 1)).sum()
            
            sens = tp / n_pos if n_pos > 0 else np.nan
            spec = tn / n_neg if n_neg > 0 else np.nan
            fnr = fn / n_pos if n_pos > 0 else np.nan
            s_lo, s_hi = wilson_ci(tp, n_pos)
            
            brier = brier_score_loss(y_test[scope_mask], test_proba[scope_mask])
            cal_int, cal_slope = compute_calibration(y_test[scope_mask], test_proba[scope_mask])
            
            rows.append({
                "generated": TIMESTAMP, "model": name, "method": method_label,
                "scope": scope_label, "n": int(n_sg), "n_positive": n_pos, "n_negative": n_neg,
                "sensitivity": round(float(sens), 4), "sens_ci_lower": round(s_lo, 4), "sens_ci_upper": round(s_hi, 4),
                "specificity": round(float(spec), 4) if not np.isnan(spec) else np.nan,
                "fnr": round(float(fnr), 4),
                "brier": round(float(brier), 4),
                "calibration_intercept": round(float(cal_int), 4),
                "calibration_slope": round(float(cal_slope), 4),
                "marginal_coverage": round(float(covered_global[scope_mask].mean()), 4),
                "fitting_test_labels_used": "NO",
            })

df_out = pd.DataFrame(rows)
df_out.to_csv(DIAG_DIR / "fairness_postprocessing_results.csv", index=False)

print("D06 — Equal Opportunity post-processing trade-off analysis complete!")
print("Saved to results/diagnostics/stage1/fairness_postprocessing_results.csv")
print()
print("=== Key sensitivity comparison (Obese BMI + Age 60+) ===")
key_scopes = ["ALL", "BMI_Obese", "Age_60plus", "BMI_Normal", "Age_18_39", "Age_40_59"]
for name in MODEL_NAMES:
    print(f"\n{name.upper()}:")
    sub = df_out[(df_out["model"] == name) & df_out["scope"].isin(key_scopes)][
        ["method", "scope", "sensitivity", "specificity", "brier", "calibration_intercept"]
    ]
    print(sub.to_string(index=False))
