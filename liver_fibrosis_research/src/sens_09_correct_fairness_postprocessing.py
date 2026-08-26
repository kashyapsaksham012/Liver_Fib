"""
sens_09_correct_fairness_postprocessing.py
Correct Equal Opportunity Fairness Post-Processing Analysis (D06 Replacement)

ANALYSIS ID: D06-v2 (Clean Replacement)
SCIENTIFIC QUESTION: What trade-offs does Equal Opportunity post-processing create
    when applied on a strictly consistent recalibrated probability scale to equalize sensitivity
    between disadvantaged (BMI-Normal, Age-60+) and reference groups?

PROBABILITY SCALE: Recalibrated probabilities (Platt-scaled) used exclusively for both
    threshold derivation (on OOF CV development data) and test set evaluation.

FITTING DATA: OOF recalibrated predictions (results/calibration/recalibrated_oof_predictions_*.csv)
EVALUATION DATA: Locked test set (results/calibration/test_set_recalibrated_predictions.csv)
TEST LABELS USED FOR FITTING: NO — thresholds derived on OOF development set only.

SECONDARY ANALYSIS: SUPPLEMENTARY / EXPLORATORY. Does NOT overwrite frozen primary results.
"""
import datetime
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from sklearn.metrics import roc_curve, brier_score_loss, confusion_matrix

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
RESULTS_DIR = ROOT / "results"
DIAG_DIR = RESULTS_DIR / "diagnostics" / "stage1"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PRIMARY_OUTCOME_COL = "outcome_primary_8.2kPa"
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def wilson_ci(k, n, level=0.95):
    if n == 0 or np.isnan(n):
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def youden_j_threshold(y_true, y_prob):
    """Compute Youden's J optimal threshold on given probabilities."""
    fpr, tpr, thresholds = roc_curve(y_true, y_prob, drop_intermediate=False)
    j_stat = tpr - fpr
    best_idx = np.argmax(j_stat)
    return thresholds[best_idx]

def equal_opportunity_threshold(y_true, y_prob, target_tpr):
    """
    Find threshold on y_prob that achieves sensitivity >= target_tpr on y_true.
    Returns the maximum threshold that achieves at least target_tpr (or closest).
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_prob, drop_intermediate=False)
    valid_idx = np.where(tpr >= target_tpr)[0]
    if len(valid_idx) > 0:
        best_idx = valid_idx[0]
        return thresholds[best_idx]
    else:
        return thresholds[-1]

def compute_calibration(y_true, y_prob):
    """Compute Hosmer-Lemeshow calibration intercept and slope on logit scale."""
    from sklearn.linear_model import LogisticRegression
    eps = 1e-7
    p_clamped = np.clip(y_prob, eps, 1 - eps)
    logit_p = np.log(p_clamped / (1 - p_clamped))
    lr = LogisticRegression(C=1e6, solver='lbfgs')
    lr.fit(logit_p.reshape(-1, 1), y_true)
    return float(lr.intercept_[0]), float(lr.coef_[0][0])

master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
y_test = test_df[PRIMARY_OUTCOME_COL].values

test_recal_all = pd.read_csv(RESULTS_DIR / "calibration" / "test_set_recalibrated_predictions.csv")

rows = []

print("=== STARTING CORRECT FAIRNESS POST-PROCESSING AUDIT (D06-v2) ===")

for name in MODEL_NAMES:
    print(f"\n--- Processing Model: {name.upper()} ---")
    
    oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{name}.csv")
    oof_with_meta = oof_df.merge(
        master[["SEQN", "bmi_group_final", "age_group_final"]], on="SEQN"
    )
    
    oof_y = oof_with_meta["true_target"].values
    oof_p = oof_with_meta["recalibrated_predicted_probability"].values
    
    global_recal_thresh = youden_j_threshold(oof_y, oof_p)
    print(f"Global OOF Recalibrated Youden Threshold: {global_recal_thresh:.4f}")
    
    test_m = test_recal_all[test_recal_all["model"] == name].set_index("SEQN")
    test_p = test_df["SEQN"].map(test_m["recalibrated_predicted_probability"]).values
    
    y_pred_global = (test_p >= global_recal_thresh).astype(int)
    
    oof_bmi_obese = oof_with_meta[oof_with_meta["bmi_group_final"] == "Obese"]
    oof_bmi_normal = oof_with_meta[oof_with_meta["bmi_group_final"] == "Normal"]
    
    obese_oof_pred = (oof_bmi_obese["recalibrated_predicted_probability"].values >= global_recal_thresh).astype(int)
    target_tpr_bmi = obese_oof_pred[oof_bmi_obese["true_target"] == 1].mean()
    print(f"OOF Obese Reference Sensitivity (Target TPR): {target_tpr_bmi:.4f}")
    
    eo_thresh_bmi_normal = equal_opportunity_threshold(
        oof_bmi_normal["true_target"].values,
        oof_bmi_normal["recalibrated_predicted_probability"].values,
        target_tpr_bmi
    )
    print(f"Derived EO Threshold for BMI-Normal: {eo_thresh_bmi_normal:.4f} (Global was {global_recal_thresh:.4f})")
    
    oof_age_40_59 = oof_with_meta[oof_with_meta["age_group_final"] == "40-59"]
    oof_age_60plus = oof_with_meta[oof_with_meta["age_group_final"] == "60+"]
    
    age_ref_oof_pred = (oof_age_40_59["recalibrated_predicted_probability"].values >= global_recal_thresh).astype(int)
    target_tpr_age = age_ref_oof_pred[oof_age_40_59["true_target"] == 1].mean()
    print(f"OOF Age 40-59 Reference Sensitivity (Target TPR): {target_tpr_age:.4f}")
    
    eo_thresh_age_60plus = equal_opportunity_threshold(
        oof_age_60plus["true_target"].values,
        oof_age_60plus["recalibrated_predicted_probability"].values,
        target_tpr_age
    )
    print(f"Derived EO Threshold for Age-60+: {eo_thresh_age_60plus:.4f} (Global was {global_recal_thresh:.4f})")
    
    y_pred_eo_bmi = y_pred_global.copy()
    normal_mask = (test_df["bmi_group_final"] == "Normal").values
    y_pred_eo_bmi[normal_mask] = (test_p[normal_mask] >= eo_thresh_bmi_normal).astype(int)
    
    y_pred_eo_age = y_pred_global.copy()
    age60_mask = (test_df["age_group_final"] == "60+").values
    y_pred_eo_age[age60_mask] = (test_p[age60_mask] >= eo_thresh_age_60plus).astype(int)
    
    y_pred_eo_dual = y_pred_global.copy()
    y_pred_eo_dual[normal_mask] = (test_p[normal_mask] >= eo_thresh_bmi_normal).astype(int)
    y_pred_eo_dual[age60_mask] = (test_p[age60_mask] >= eo_thresh_age_60plus).astype(int)
    both_mask = normal_mask & age60_mask
    y_pred_eo_dual[both_mask] = (test_p[both_mask] >= min(eo_thresh_bmi_normal, eo_thresh_age_60plus)).astype(int)

    subgroup_definitions = [
        ("ALL", np.ones(len(test_df), dtype=bool)),
        ("BMI_Normal", normal_mask),
        ("BMI_Overweight", (test_df["bmi_group_final"] == "Overweight").values),
        ("BMI_Obese", (test_df["bmi_group_final"] == "Obese").values),
        ("Age_18_39", (test_df["age_group_final"] == "18-39").values),
        ("Age_40_59", (test_df["age_group_final"] == "40-59").values),
        ("Age_60plus", age60_mask),
        ("BMI_Normal_Age_60plus", (normal_mask & age60_mask)),
        ("BMI_Obese_Age_60plus", ((test_df["bmi_group_final"] == "Obese").values & age60_mask)),
    ]
    
    methods = [
        ("recalibrated_baseline", y_pred_global),
        ("eo_bmi_postprocessed", y_pred_eo_bmi),
        ("eo_age_postprocessed", y_pred_eo_age),
        ("eo_dual_postprocessed", y_pred_eo_dual),
    ]
    
    for method_name, y_pred_m in methods:
        for scope_name, scope_mask in subgroup_definitions:
            n_sg = int(scope_mask.sum())
            if n_sg == 0:
                continue
            
            y_sub = y_test[scope_mask]
            pred_sub = y_pred_m[scope_mask]
            prob_sub = test_p[scope_mask]
            
            n_pos = int(y_sub.sum())
            n_neg = n_sg - n_pos
            
            if n_pos > 0 and n_neg > 0:
                tn, fp, fn, tp = confusion_matrix(y_sub, pred_sub, labels=[0, 1]).ravel()
                sens = tp / n_pos
                spec = tn / n_neg
                fnr = fn / n_pos
                ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
            elif n_pos > 0:
                tp = int((pred_sub == 1).sum())
                fn = n_pos - tp
                fp, tn = 0, 0
                sens = tp / n_pos
                spec, fnr, ppv, npv = np.nan, fn / n_pos, np.nan, np.nan
            else:
                sens, spec, fnr, ppv, npv = np.nan, np.nan, np.nan, np.nan, np.nan
            
            s_lo, s_hi = wilson_ci(tp, n_pos) if n_pos > 0 else (np.nan, np.nan)
            
            brier = brier_score_loss(y_sub, prob_sub)
            cal_int, cal_slope = compute_calibration(y_sub, prob_sub)
            
            rows.append({
                "generated": TIMESTAMP,
                "model": name,
                "method": method_name,
                "scope": scope_name,
                "n": n_sg,
                "n_positive": n_pos,
                "n_negative": n_neg,
                "sensitivity": round(float(sens), 4),
                "sens_ci_lower": round(float(s_lo), 4),
                "sens_ci_upper": round(float(s_hi), 4),
                "specificity": round(float(spec), 4) if not np.isnan(spec) else np.nan,
                "fnr": round(float(fnr), 4) if not np.isnan(fnr) else np.nan,
                "ppv": round(float(ppv), 4) if not np.isnan(ppv) else np.nan,
                "npv": round(float(npv), 4) if not np.isnan(npv) else np.nan,
                "brier": round(float(brier), 4),
                "calibration_intercept": round(float(cal_int), 4),
                "calibration_slope": round(float(cal_slope), 4),
                "fitting_test_labels_used": "NO",
            })

df_out = pd.DataFrame(rows)
df_out.to_csv(DIAG_DIR / "correct_fairness_postprocessing_results.csv", index=False)

print("\n=== D06-v2 CORRECT FAIRNESS POST-PROCESSING AUDIT COMPLETE ===")
print("Saved output to results/diagnostics/stage1/correct_fairness_postprocessing_results.csv")
