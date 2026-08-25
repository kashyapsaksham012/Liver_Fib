import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
DIAG_DIR = RESULTS_DIR / "diagnostics" / "stage0"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

models = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]

# 1. Discrimination metrics
df_disc = pd.read_csv(RESULTS_DIR / "tables" / "phase3_final_baseline_results.csv")
disc_dict = {}
for idx, row in df_disc.iterrows():
    m = row["model_name"]
    disc_dict[m] = {
        "auc": row["test_roc_auc"],
        "auc_ci": f"[{row['roc_auc_95ci_low']:.4f}, {row['roc_auc_95ci_high']:.4f}]",
        "sens": row["sensitivity"],
        "spec": row["specificity"],
        "ppv": row["ppv"],
        "npv": row["npv"],
        "f1": row["f1"],
    }

# 2. Calibration metrics
df_cal = pd.read_csv(RESULTS_DIR / "calibration" / "test_set_calibration_final.csv")
cal_dict = {}
for m in models:
    raw_row = df_cal[(df_cal["model"] == m) & (df_cal["variant"] == "raw")].iloc[0]
    recal_row = df_cal[(df_cal["model"] == m) & (df_cal["variant"] == "recalibrated")].iloc[0]
    cal_dict[m] = {
        "raw_intercept": raw_row["calibration_intercept"],
        "raw_slope": raw_row["calibration_slope"],
        "raw_brier": raw_row["brier_score"],
        "raw_ece": raw_row["ece"],
        "recal_intercept": recal_row["calibration_intercept"],
        "recal_slope": recal_row["calibration_slope"],
        "recal_brier": recal_row["brier_score"],
        "recal_ece": recal_row["ece"],
    }

# 3. Fairness metrics (Obese vs Normal BMI and 60+ vs 40-59 Age)
df_fair = pd.read_csv(RESULTS_DIR / "fairness" / "subgroup_discrimination_metrics.csv")
fair_dict = {}
for m in models:
    fair_dict[m] = {}
    
# Let's compute fairness stats directly
# Note: we can read them from subgroup_discrimination_metrics.csv
# Wait, let's load fairness_inference.csv or print values directly.
# Let's inspect columns or print unique entries in fairness_inference.csv if it exists
df_fair_inf = pd.read_csv(RESULTS_DIR / "fairness" / "fairness_inference.csv")
for m in models:
    # Obese vs Normal
    bmi_row = df_fair_inf[(df_fair_inf["model"] == m) & (df_fair_inf["dimension"] == "bmi") & (df_fair_inf["category"] == "Obese")].iloc[0]
    age_row = df_fair_inf[(df_fair_inf["model"] == m) & (df_fair_inf["dimension"] == "age") & (df_fair_inf["category"] == "60+")].iloc[0]
    fair_dict[m] = {
        "bmi_target_sens": bmi_row["subgroup_sensitivity"],
        "bmi_ref_sens": bmi_row["reference_sensitivity"],
        "bmi_disparity": bmi_row["absolute_disparity_pp"],
        "bmi_ci": f"[{bmi_row['ci_lower_pp']:.2f}, {bmi_row['ci_upper_pp']:.2f}]",
        "bmi_sig": bmi_row["significant_after_fdr_0.05"],
        "age_target_sens": age_row["subgroup_sensitivity"],
        "age_ref_sens": age_row["reference_sensitivity"],
        "age_disparity": age_row["absolute_disparity_pp"],
        "age_ci": f"[{age_row['ci_lower_pp']:.2f}, {age_row['ci_upper_pp']:.2f}]",
        "age_sig": age_row["significant_after_fdr_0.05"],
    }

# 4. Conformal uncertainty & Efficiency
df_cov_inf = pd.read_csv(RESULTS_DIR / "uncertainty" / "coverage_inference.csv")
df_cov_sub = pd.read_csv(RESULTS_DIR / "uncertainty" / "subgroup_coverage.csv")
df_cov_marg = pd.read_csv(RESULTS_DIR / "uncertainty" / "marginal_coverage_test_set.csv")

cov_dict = {}
for m in models:
    marg_row = df_cov_marg[df_cov_marg["model"] == m].iloc[0]
    obese_row = df_cov_sub[(df_cov_sub["model"] == m) & (df_cov_sub["dimension"] == "bmi") & (df_cov_sub["category"] == "Obese")].iloc[0]
    normal_row = df_cov_sub[(df_cov_sub["model"] == m) & (df_cov_sub["dimension"] == "bmi") & (df_cov_sub["category"] == "Normal")].iloc[0]
    age60_row = df_cov_sub[(df_cov_sub["model"] == m) & (df_cov_sub["dimension"] == "age") & (df_cov_sub["category"] == "60+")].iloc[0]
    age40_row = df_cov_sub[(df_cov_sub["model"] == m) & (df_cov_sub["dimension"] == "age") & (df_cov_sub["category"] == "40-59")].iloc[0]
    
    cov_dict[m] = {
        "marginal_coverage": marg_row["empirical_coverage"],
        "marginal_set_size": marg_row["mean_set_size"],
        "marginal_singleton": marg_row["singleton_rate"],
        "obese_coverage": obese_row["empirical_coverage"],
        "obese_set_size": obese_row["mean_set_size"],
        "obese_singleton": obese_row["singleton_rate"],
        "normal_coverage": normal_row["empirical_coverage"],
        "normal_set_size": normal_row["mean_set_size"],
        "normal_singleton": normal_row["singleton_rate"],
        "age60_coverage": age60_row["empirical_coverage"],
        "age60_set_size": age60_row["mean_set_size"],
        "age60_singleton": age60_row["singleton_rate"],
        "age40_coverage": age40_row["empirical_coverage"],
        "age40_set_size": age40_row["mean_set_size"],
        "age40_singleton": age40_row["singleton_rate"],
    }

# Let's generate a clean markdown baseline reconstruction report
md_content = """# Baseline Reconstruction Report

This report reconstructs the baseline performance of the five primary models (**Logistic Regression, Random Forest, XGBoost, LightGBM, MLP**) on the locked test set (N = 2,146), verified from the project's own frozen results.

---

## 1. Model Discrimination
Below are the baseline model discrimination metrics on the locked test set:

| Model | test_roc_auc | ROC-AUC 95% CI | Sensitivity | Specificity | PPV | NPV | F1 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
"""

for m in models:
    d = disc_dict[m]
    md_content += f"| **{m.upper()}** | {d['auc']:.4f} | {d['auc_ci']} | {d['sens']:.4f} | {d['spec']:.4f} | {d['ppv']:.4f} | {d['npv']:.4f} | {d['f1']:.4f} |\n"

md_content += """
---

## 2. Model Calibration (Raw vs. Recalibrated)
All models except MLP were class-weighted/resampled during training, resulting in severe raw calibration intercept shifts (prior shifts). Recalibration was performed using Platt scaling fit on CV out-of-fold training data.

| Model | Raw Intercept | Recal Intercept | Raw Slope | Recal Slope | Raw Brier | Recal Brier | Raw ECE | Recal ECE |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
"""

for m in models:
    c = cal_dict[m]
    md_content += f"| **{m.upper()}** | {c['raw_intercept']:.3f} | {c['recal_intercept']:.3f} | {c['raw_slope']:.3f} | {c['recal_slope']:.3f} | {c['raw_brier']:.4f} | {c['recal_brier']:.4f} | {c['raw_ece']:.4f} | {c['recal_ece']:.4f} |\n"

md_content += """
---

## 3. Subgroup Fairness Disparities (Sensitivity)
Primary fairness assessment evaluates the sensitivity disparity (Equal Opportunity) between targeted categories on the locked test set.

### Obese vs. Normal BMI
| Model | Obese Sens | Normal BMI Sens | Disparity (pp) | 95% Bootstrap CI (pp) | FDR Significant? |
|:---|:---:|:---:|:---:|:---:|:---:|
"""

for m in models:
    f = fair_dict[m]
    md_content += f"| **{m.upper()}** | {f['bmi_target_sens']:.4f} | {f['bmi_ref_sens']:.4f} | {f['bmi_disparity']:.2f} | {f['bmi_ci']} | {f['bmi_sig']} |\n"

md_content += """
### Age 60+ vs. 40-59
| Model | Age 60+ Sens | Age 40-59 Sens | Disparity (pp) | 95% Bootstrap CI (pp) | FDR Significant? |
|:---|:---:|:---:|:---:|:---:|:---:|
"""

for m in models:
    f = fair_dict[m]
    md_content += f"| **{m.upper()}** | {f['age_target_sens']:.4f} | {f['age_ref_sens']:.4f} | {f['age_disparity']:.2f} | {f['age_ci']} | {f['age_sig']} |\n"

md_content += """
---

## 4. Conformal Uncertainty & Efficiency
Nominal target coverage is set to **90%** (alpha = 0.10).

| Model | Marginal Cov | Marginal Set Size | Obese Coverage | Normal Coverage | Age 60+ Coverage | Age 40-59 Coverage |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
"""

for m in models:
    v = cov_dict[m]
    md_content += f"| **{m.upper()}** | {v['marginal_coverage']:.4f} | {v['marginal_set_size']:.3f} | {v['obese_coverage']:.4f} | {v['normal_coverage']:.4f} | {v['age60_coverage']:.4f} | {v['age40_coverage']:.4f} |\n"

md_content += """
---

## 5. Existing Mitigation (Before vs. After Mondrian Conformal)
Under Mondrian conformal mitigation (Phase 7), specific targets are set for Obese and Age 60+ groups.

| Model | Dimension | Category | Cov Before | Cov After | Cov Change (pp) | Set Size Before | Set Size After |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
"""

df_mit = pd.read_csv(RESULTS_DIR / "mitigation" / "test_set_mitigation_final.csv")
for idx, row in df_mit.iterrows():
    md_content += f"| **{row['model'].upper()}** | {row['dimension']} | {row['category']} | {row['coverage_before']:.4f} | {row['coverage_after']:.4f} | {row['coverage_change_pp']:.2f} | {row['mean_set_size_before']:.3f} | {row['mean_set_size_after']:.3f} |\n"

with open(DIAG_DIR / "baseline_reconstruction.md", "w") as f:
    f.write(md_content)

print("Baseline reconstruction completed successfully!")
print("Saved to results/diagnostics/stage0/baseline_reconstruction.md")
