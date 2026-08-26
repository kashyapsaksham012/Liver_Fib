"""
tradeoff_01_fairness_specificity_pareto.py
Part A, Part B, Part H — Fairness-Specificity Trade-off, Differential Response, and Clinical Costs

SCIENTIFIC GOAL:
1. Construct OOF Pareto frontier of Fairness (sensitivity disparity) vs Specificity Cost.
2. Select fairness-constrained threshold on OOF data using pre-specified <= 5.0 pp overall specificity loss constraint.
3. Lock threshold and apply once to locked test set.
4. Calculate formal BMI vs Age Fairness Response and clinical FP/FN trade-offs with 95% CIs.

FITTING DATA: OOF recalibrated predictions (results/calibration/recalibrated_oof_predictions_*.csv)
EVALUATION DATA: Locked test set (results/calibration/test_set_recalibrated_predictions.csv)
TEST LABELS USED FOR FITTING: NO — strictly OOF development selection.
"""

import datetime
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from sklearn.metrics import roc_curve, confusion_matrix

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
DIAG_DIR = RESULTS_DIR / "diagnostics" / "stage1"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
DIAG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PRIMARY_OUTCOME_COL = "outcome_primary_8.2kPa"
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def wilson_ci(k, n, level=0.95):
    if n == 0 or np.isnan(n) or np.isnan(k):
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

def compute_metrics(y_true, y_pred):
    n_total = len(y_true)
    n_pos = int(y_true.sum())
    n_neg = n_total - n_pos
    if n_pos > 0 and n_neg > 0:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        sens = tp / n_pos
        spec = tn / n_neg
        fnr = fn / n_pos
        fpr = fp / n_neg
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    else:
        tn, fp, fn, tp = 0, 0, 0, 0
        sens, spec, fnr, fpr, ppv, npv = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    return {
        "n": n_total, "n_pos": n_pos, "n_neg": n_neg,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "sens": sens, "spec": spec, "fnr": fnr, "fpr": fpr, "ppv": ppv, "npv": npv
    }

print("=== EXECUTING PART A, B, H: FAIRNESS-SPECIFICITY PARETO & CLINICAL COST AUDIT ===")

master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
y_test = test_df[PRIMARY_OUTCOME_COL].values
test_recal_all = pd.read_csv(RESULTS_DIR / "calibration" / "test_set_recalibrated_predictions.csv")

pareto_rows = []
response_rows = []
clinical_rows = []

grid = np.linspace(0.001, 0.999, 999)

for model_name in MODEL_NAMES:
    print(f"\n--- Model: {model_name.upper()} ---")
    oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{model_name}.csv")
    oof_with_meta = oof_df.merge(master[["SEQN", "bmi_group_final", "age_group_final"]], on="SEQN")
    
    oof_y = oof_with_meta["true_target"].values
    oof_p = oof_with_meta["recalibrated_predicted_probability"].values
    
    t_global_oof = youden_j_threshold(oof_y, oof_p)
    
    # Baseline OOF metrics
    base_oof_pred = (oof_p >= t_global_oof).astype(int)
    base_oof_m = compute_metrics(oof_y, base_oof_pred)
    base_oof_spec = base_oof_m["spec"]
    
    # Subgroup OOF masks
    oof_normal_mask = (oof_with_meta["bmi_group_final"] == "Normal").values
    oof_obese_mask = (oof_with_meta["bmi_group_final"] == "Obese").values
    oof_age40_mask = (oof_with_meta["age_group_final"] == "40-59").values
    oof_age60_mask = (oof_with_meta["age_group_final"] == "60+").values
    
    # Reference sensitivity on OOF at global threshold
    ref_sens_bmi_oof = compute_metrics(oof_y[oof_obese_mask], base_oof_pred[oof_obese_mask])["sens"]
    ref_sens_age_oof = compute_metrics(oof_y[oof_age40_mask], base_oof_pred[oof_age40_mask])["sens"]
    
    # -------------------------------------------------------------
    # 1. BMI Candidate Threshold Search on OOF
    # -------------------------------------------------------------
    bmi_search_records = []
    for t_cand in grid:
        # Predict: Normal gets t_cand, others get t_global_oof
        pred_cand = base_oof_pred.copy()
        pred_cand[oof_normal_mask] = (oof_p[oof_normal_mask] >= t_cand).astype(int)
        
        m_overall = compute_metrics(oof_y, pred_cand)
        m_normal = compute_metrics(oof_y[oof_normal_mask], (oof_p[oof_normal_mask] >= t_cand).astype(int))
        
        disparity = abs(ref_sens_bmi_oof - m_normal["sens"])
        spec_cost_pp = (base_oof_spec - m_overall["spec"]) * 100.0
        
        bmi_search_records.append({
            "t_cand": t_cand,
            "normal_sens": m_normal["sens"],
            "normal_spec": m_normal["spec"],
            "normal_ppv": m_normal["ppv"],
            "normal_npv": m_normal["npv"],
            "overall_spec": m_overall["spec"],
            "spec_cost_pp": spec_cost_pp,
            "disparity": disparity
        })
    
    df_bmi_search = pd.DataFrame(bmi_search_records)
    
    # Pre-specified OOF constraint: spec_cost_pp <= 5.0 pp
    valid_bmi = df_bmi_search[df_bmi_search["spec_cost_pp"] <= 5.0]
    if len(valid_bmi) > 0:
        best_bmi_idx = valid_bmi["disparity"].idxmin()
        t_bmi_constrained = valid_bmi.loc[best_bmi_idx, "t_cand"]
    else:
        t_bmi_constrained = t_global_oof
        
    print(f"BMI Constraint Search: Selected Threshold = {t_bmi_constrained:.4f} (Global: {t_global_oof:.4f})")
    
    # -------------------------------------------------------------
    # 2. Age Candidate Threshold Search on OOF
    # -------------------------------------------------------------
    age_search_records = []
    for t_cand in grid:
        pred_cand = base_oof_pred.copy()
        pred_cand[oof_age60_mask] = (oof_p[oof_age60_mask] >= t_cand).astype(int)
        
        m_overall = compute_metrics(oof_y, pred_cand)
        m_age60 = compute_metrics(oof_y[oof_age60_mask], (oof_p[oof_age60_mask] >= t_cand).astype(int))
        
        disparity = abs(ref_sens_age_oof - m_age60["sens"])
        spec_cost_pp = (base_oof_spec - m_overall["spec"]) * 100.0
        
        age_search_records.append({
            "t_cand": t_cand,
            "age60_sens": m_age60["sens"],
            "age60_spec": m_age60["spec"],
            "age60_ppv": m_age60["ppv"],
            "age60_npv": m_age60["npv"],
            "overall_spec": m_overall["spec"],
            "spec_cost_pp": spec_cost_pp,
            "disparity": disparity
        })
        
    df_age_search = pd.DataFrame(age_search_records)
    valid_age = df_age_search[df_age_search["spec_cost_pp"] <= 5.0]
    if len(valid_age) > 0:
        best_age_idx = valid_age["disparity"].idxmin()
        t_age_constrained = valid_age.loc[best_age_idx, "t_cand"]
    else:
        t_age_constrained = t_global_oof
        
    print(f"Age Constraint Search: Selected Threshold = {t_age_constrained:.4f} (Global: {t_global_oof:.4f})")
    
    # -------------------------------------------------------------
    # 3. Apply Locked Thresholds to Locked Test Set
    # -------------------------------------------------------------
    test_m = test_recal_all[test_recal_all["model"] == model_name].set_index("SEQN")
    test_p = test_df["SEQN"].map(test_m["recalibrated_predicted_probability"]).values
    
    test_normal_mask = (test_df["bmi_group_final"] == "Normal").values
    test_obese_mask = (test_df["bmi_group_final"] == "Obese").values
    test_age40_mask = (test_df["age_group_final"] == "40-59").values
    test_age60_mask = (test_df["age_group_final"] == "60+").values
    
    # Baseline Test Predictions
    pred_test_base = (test_p >= t_global_oof).astype(int)
    
    # Post-Intervention Test Predictions
    pred_test_bmi = pred_test_base.copy()
    pred_test_bmi[test_normal_mask] = (test_p[test_normal_mask] >= t_bmi_constrained).astype(int)
    
    pred_test_age = pred_test_base.copy()
    pred_test_age[test_age60_mask] = (test_p[test_age60_mask] >= t_age_constrained).astype(int)
    
    # Evaluate baseline test metrics
    m_test_base_all = compute_metrics(y_test, pred_test_base)
    m_test_base_normal = compute_metrics(y_test[test_normal_mask], pred_test_base[test_normal_mask])
    m_test_base_obese = compute_metrics(y_test[test_obese_mask], pred_test_base[test_obese_mask])
    m_test_base_age40 = compute_metrics(y_test[test_age40_mask], pred_test_base[test_age40_mask])
    m_test_base_age60 = compute_metrics(y_test[test_age60_mask], pred_test_base[test_age60_mask])
    
    base_bmi_disparity = abs(m_test_base_obese["sens"] - m_test_base_normal["sens"])
    base_age_disparity = abs(m_test_base_age40["sens"] - m_test_base_age60["sens"])
    
    # Evaluate post-intervention test metrics
    m_test_post_bmi_all = compute_metrics(y_test, pred_test_bmi)
    m_test_post_bmi_normal = compute_metrics(y_test[test_normal_mask], pred_test_bmi[test_normal_mask])
    m_test_post_bmi_obese = m_test_base_obese
    post_bmi_disparity = abs(m_test_post_bmi_obese["sens"] - m_test_post_bmi_normal["sens"])
    
    m_test_post_age_all = compute_metrics(y_test, pred_test_age)
    m_test_post_age_60 = compute_metrics(y_test[test_age60_mask], pred_test_age[test_age60_mask])
    m_test_post_age_40 = m_test_base_age40
    post_age_disparity = abs(m_test_post_age_40["sens"] - m_test_post_age_60["sens"])
    
    # Fairness Response Calculation (Part B)
    bmi_response = (base_bmi_disparity - post_bmi_disparity) / base_bmi_disparity if base_bmi_disparity > 0 else np.nan
    age_response = (base_age_disparity - post_age_disparity) / base_age_disparity if base_age_disparity > 0 else np.nan
    
    response_rows.append({
        "model": model_name,
        "bmi_baseline_disparity": round(base_bmi_disparity, 4),
        "bmi_post_disparity": round(post_bmi_disparity, 4),
        "bmi_fairness_response": round(bmi_response, 4),
        "bmi_pct_reduction": round(bmi_response * 100.0, 2) if not np.isnan(bmi_response) else np.nan,
        "age_baseline_disparity": round(base_age_disparity, 4),
        "age_post_disparity": round(post_age_disparity, 4),
        "age_fairness_response": round(age_response, 4),
        "age_pct_reduction": round(age_response * 100.0, 2) if not np.isnan(age_response) else np.nan,
        "response_diff_bmi_vs_age": round((bmi_response - age_response) * 100.0, 2) if (not np.isnan(bmi_response) and not np.isnan(age_response)) else np.nan,
        "fitting_test_labels_used": "NO"
    })
    
    # Clinical Costs Table (Part H) - BMI intervention focus
    # Compare pred_test_base vs pred_test_bmi on test set overall & normal subgroup
    sens_ci_base = wilson_ci(m_test_base_normal["tp"], m_test_base_normal["n_pos"])
    sens_ci_post = wilson_ci(m_test_post_bmi_normal["tp"], m_test_post_bmi_normal["n_pos"])
    spec_ci_base = wilson_ci(m_test_base_all["tn"], m_test_base_all["n_neg"])
    spec_ci_post = wilson_ci(m_test_post_bmi_all["tn"], m_test_post_bmi_all["n_neg"])
    
    add_fp = m_test_post_bmi_all["fp"] - m_test_base_all["fp"]
    add_fn = m_test_post_bmi_all["fn"] - m_test_base_all["fn"]
    sens_gain_pp = (m_test_post_bmi_normal["sens"] - m_test_base_normal["sens"]) * 100.0
    spec_loss_pp = (m_test_base_all["spec"] - m_test_post_bmi_all["spec"]) * 100.0
    ppv_change_pp = (m_test_post_bmi_all["ppv"] - m_test_base_all["ppv"]) * 100.0
    
    clinical_rows.append({
        "model": model_name,
        "global_threshold": round(t_global_oof, 4),
        "bmi_normal_threshold": round(t_bmi_constrained, 4),
        "baseline_normal_sens": round(m_test_base_normal["sens"], 4),
        "baseline_normal_sens_ci": f"[{sens_ci_base[0]:.4f}, {sens_ci_base[1]:.4f}]",
        "post_normal_sens": round(m_test_post_bmi_normal["sens"], 4),
        "post_normal_sens_ci": f"[{sens_ci_post[0]:.4f}, {sens_ci_post[1]:.4f}]",
        "sens_gain_pp": round(sens_gain_pp, 2),
        "baseline_overall_spec": round(m_test_base_all["spec"], 4),
        "baseline_overall_spec_ci": f"[{spec_ci_base[0]:.4f}, {spec_ci_base[1]:.4f}]",
        "post_overall_spec": round(m_test_post_bmi_all["spec"], 4),
        "post_overall_spec_ci": f"[{spec_ci_post[0]:.4f}, {spec_ci_post[1]:.4f}]",
        "spec_loss_pp": round(spec_loss_pp, 2),
        "additional_false_positives": int(add_fp),
        "additional_false_negatives": int(add_fn),
        "baseline_overall_ppv": round(m_test_base_all["ppv"], 4),
        "post_overall_ppv": round(m_test_post_bmi_all["ppv"], 4),
        "ppv_change_pp": round(ppv_change_pp, 2),
        "baseline_disparity": round(base_bmi_disparity, 4),
        "post_disparity": round(post_bmi_disparity, 4),
        "fitting_test_labels_used": "NO"
    })
    
    # Record Pareto summary points for Table 1 and Table 2
    pareto_rows.append({
        "model": model_name,
        "target_subgroup": "BMI_Normal",
        "global_threshold": round(t_global_oof, 4),
        "constrained_threshold": round(t_bmi_constrained, 4),
        "baseline_sensitivity": round(m_test_base_normal["sens"], 4),
        "constrained_sensitivity": round(m_test_post_bmi_normal["sens"], 4),
        "baseline_specificity": round(m_test_base_all["spec"], 4),
        "constrained_specificity": round(m_test_post_bmi_all["spec"], 4),
        "baseline_disparity": round(base_bmi_disparity, 4),
        "constrained_disparity": round(post_bmi_disparity, 4),
        "spec_loss_pp": round(spec_loss_pp, 2),
        "false_positives_baseline": m_test_base_all["fp"],
        "false_positives_constrained": m_test_post_bmi_all["fp"],
        "false_negatives_baseline": m_test_base_all["fn"],
        "false_negatives_constrained": m_test_post_bmi_all["fn"],
        "fitting_test_labels_used": "NO"
    })
    pareto_rows.append({
        "model": model_name,
        "target_subgroup": "Age_60plus",
        "global_threshold": round(t_global_oof, 4),
        "constrained_threshold": round(t_age_constrained, 4),
        "baseline_sensitivity": round(m_test_base_age60["sens"], 4),
        "constrained_sensitivity": round(m_test_post_age_60["sens"], 4),
        "baseline_specificity": round(m_test_base_all["spec"], 4),
        "constrained_specificity": round(m_test_post_age_all["spec"], 4),
        "baseline_disparity": round(base_age_disparity, 4),
        "constrained_disparity": round(post_age_disparity, 4),
        "spec_loss_pp": round((m_test_base_all["spec"] - m_test_post_age_all["spec"]) * 100.0, 2),
        "false_positives_baseline": m_test_base_all["fp"],
        "false_positives_constrained": m_test_post_age_all["fp"],
        "false_negatives_baseline": m_test_base_all["fn"],
        "false_negatives_constrained": m_test_post_age_all["fn"],
        "fitting_test_labels_used": "NO"
    })

# Save outputs to both results/tables and results/diagnostics/stage1
df_pareto = pd.DataFrame(pareto_rows)
df_response = pd.DataFrame(response_rows)
df_clinical = pd.DataFrame(clinical_rows)

df_pareto.to_csv(TABLES_DIR / "fairness_specificity_pareto_results.csv", index=False)
df_pareto.to_csv(DIAG_DIR / "fairness_specificity_pareto_results.csv", index=False)

df_response.to_csv(TABLES_DIR / "bmi_age_intervention_response.csv", index=False)
df_response.to_csv(DIAG_DIR / "bmi_age_intervention_response.csv", index=False)

df_clinical.to_csv(TABLES_DIR / "clinically_interpretable_fairness_costs.csv", index=False)
df_clinical.to_csv(DIAG_DIR / "clinically_interpretable_fairness_costs.csv", index=False)

print("\n=== SUCCESS: PART A, B, H EXECUTED CLEANLY ===")
print("Saved files:")
print(" - fairness_specificity_pareto_results.csv")
print(" - bmi_age_intervention_response.csv")
print(" - clinically_interpretable_fairness_costs.csv")
