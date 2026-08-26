# FINAL EXPERIMENTAL EVIDENCE LINEAGE

**Project:** Machine Learning Discrimination, Calibration, Fairness, and Conformal Uncertainty in Non-Invasive Liver Fibrosis Prediction (NHANES 2017–March 2020)  
**Date:** 2026-08-25  
**Repository Path:** `liver_fibrosis_research/`  
**Git HEAD:** `1be2523`  
**Audit Purpose:** Traceability mapping for every primary, secondary, sensitivity, and diagnostic claim across the entire experimental lifecycle.

---

## 1. Cohort Construction & Data Assembly Lineage

### Claim 1.1: Primary Analytic Cohort Assembly (CAND_1, N=7,153, 9.31% Prevalence)
- **Claim:** The primary analytic cohort consists of N=7,153 adult NHANES 2017–March 2020 participants with valid VCTE elastography, non-missing routine laboratory predictors, and a primary elastography cutoff of LUXSMED ≥ 8.2 kPa (666 positive cases, 9.31% prevalence).
- **Table / Figure:** Table 1 (`results/figures/table1_cohort_characteristics.png`), `results/tables/data_and_result_lineage.csv`
- **Result File:** `data/processed/analysis_dataset_primary.parquet`, `data/processed/master_nhanes_analytic_dataset.parquet`
- **Source Script:** `src/15_create_master_dataset.py`, `src/_cohorts.py`, `src/phase2_04_build_analysis_dataset.py`
- **Input Data:** `P_DEMO.xpt`, `P_BMX.xpt`, `P_LUX.xpt`, `P_BIOPRO.xpt`, `P_CBC.xpt` (raw NHANES SAS transport files in `data/raw/`)
- **Fitting Data:** N/A (Data cleaning and deterministic filtration only)
- **Evaluation Data:** Full candidate cohort N=10,409 → valid elastography N=9,023 → adult complete case N=7,153
- **Protocol Document:** `documentation/phase2/primary_outcome_definition.md`, `PHASE1_DATA_ASSEMBLY_REPORT.md`

### Claim 1.2: Candidate Cohorts CAND_2 (N=7,639) and CAND_3 (N=3,582)
- **Claim:** Relaxing elastography quality rules yields CAND_2 (N=7,639, ~~9.49%~~ **CORRECTED: 10.52%** prevalence); restricting to fasting-subsample laboratory variables yields CAND_3 (N=3,582, ~~9.13%~~ **CORRECTED: 8.91%** prevalence). *[Correction sourced from `results/tables/phase2_candidate_cohort_comparison.csv` and `results/sensitivity/relaxed_elastography_cohort_summary.csv`, re-verified 26 Aug 2026 — see `documentation/final_audit/FINAL_NUMERICAL_AND_M4B_AUDIT.md` §1.1.]*
- **Table / Figure:** `results/tables/sensitivity_cohort_comparisons.csv`
- **Result File:** `data/processed/analysis_dataset_cand2.parquet`, `data/processed/analysis_dataset_cand3.parquet`
- **Source Script:** `src/phase2_01_candidate_cohorts.py`, `src/sens_01_construct_cohorts.py`
- **Input Data:** `data/raw/P_*.xpt`
- **Fitting Data:** N/A
- **Evaluation Data:** CAND_2 (N=7,639), CAND_3 (N=3,582)
- **Protocol Document:** `PHASE2_ANALYTICAL_PROTOCOL_AND_FEASIBILITY_REPORT.md`

### Claim 1.3: CAND_4 All-Ages Cohort (N=8,215) Status
- **Claim:** CAND_4 (all ages ≥ 12, N=8,215) was defined and constructed but never modeled.
- **Status:** `PLANNED` / `CONSTRUCTED BUT NOT EXECUTED`
- **Result File:** `CAND4_CLASSIFICATION_RESOLUTION_REPORT.md`
- **Source Script:** `src/phase2_01_candidate_cohorts.py`
- **Protocol Document:** `CAND4_CLASSIFICATION_RESOLUTION_REPORT.md`

---

## 2. Model Discrimination Lineage (Phase 3)

### Claim 2.1: Baseline Discrimination Equality Across 5 Model Families (AUROC 0.8229–0.8429)
- **Claim:** Five machine learning models (Logistic Regression, Random Forest, XGBoost, LightGBM, MLP) achieve non-statistically different discrimination performance on the locked test set (N=2,146), with AUROC ranging from 0.8229 to 0.8429.
- **Table / Figure:** `results/tables/phase3_overall_discrimination.csv`, `results/figures/roc_curves_baseline.png`
- **Result File:** `results/predictions/test_predictions_logistic.csv`, `test_predictions_random_forest.csv`, `test_predictions_xgboost.csv`, `test_predictions_lightgbm.csv`, `test_predictions_mlp.csv`
- **Source Script:** `src/phase3_05_train_and_tune.py`, `src/phase3_06_threshold_and_test_eval.py`
- **Input Data:** `data/processed/analysis_dataset_primary.parquet`
- **Fitting Data:** Training Set (N=5,007, 5-fold cross-validation)
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `documentation/phase3/MODEL_DEVELOPMENT_PROTOCOL.md`

### Claim 2.2: XGBoost vs MLP Statistical Comparison under Pooled Correction Nuance
- **Claim:** Under primary 10-test FDR correction, no pairwise model difference is significant. Under a project-wide 182-test pooled correction, XGBoost (0.8429) vs MLP (0.8229) reaches adjusted significance (p = 0.0136).
- **Table / Figure:** `results/tables/pooled_fdr_corrected_results.csv`
- **Result File:** `results/tables/pooled_fdr_corrected_results.csv`
- **Source Script:** `src/phase3_16_inference_methodology.py`
- **Fitting Data:** OOF predictions (N=5,007)
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `P0_P1_REMEDIATION_ADDENDUM.md`

---

## 3. Model Calibration Lineage (Phase 4)

### Claim 3.1: Raw Model Miscalibration via Class-Balancing Prior Shift
- **Claim:** Raw probability outputs from class-balanced models (LR, RF, XGB, LGBM) exhibit severe probability distortion (intercept -2.24 to -1.33, slope 1.34 to 1.88, ECE 0.12 to 0.28) caused by class-weighting prior shift.
- **Table / Figure:** `results/calibration/primary_metrics_by_model.csv`, `results/figures/calibration_curves_raw.png`
- **Result File:** `results/calibration/recalibrated_oof_predictions_*.csv`
- **Source Script:** `src/phase4_03_curves_and_ece.py`, `src/phase4_05_recalibration.py`
- **Input Data:** OOF validation predictions (N=5,007)
- **Fitting Data:** OOF Validation Set (N=5,007)
- **Evaluation Data:** OOF Validation Set & Locked Test Set (N=2,146)
- **Protocol Document:** `PHASE4_CALIBRATION_RESULTS_REPORT.md`

### Claim 3.2: OOF Platt Recalibration Efficacy
- **Claim:** Applying univariate Platt scaling fit on OOF predictions restores calibration on the locked test set (intercept -0.05 to +0.08, slope 0.94 to 1.05, ECE < 0.03) without altering AUROC.
- **Table / Figure:** `results/calibration/test_set_calibration_final.csv`
- **Result File:** `results/predictions/test_set_recalibrated_predictions.csv`
- **Source Script:** `src/phase4_09_final_test_set_calibration.py`
- **Fitting Data:** OOF Validation Set (N=5,007)
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `PHASE4_CLOSURE_VERIFICATION_REPORT.md`

---

## 4. Demographic Fairness Audit Lineage (Phase 5)

### Claim 4.1: Robust BMI Sensitivity Disparity (5/5 Models)
- **Claim:** Normal-BMI participants experience severe, FDR-significant sensitivity deficits compared to Obese participants across all 5 models (sensitivity gap 27.1% to 48.0%, p < 0.001).
- **Table / Figure:** `results/fairness/fairness_inference.csv`, `results/tables/fairness_headline_summary.csv`
- **Result File:** `results/fairness/subgroup_discrimination_metrics.csv`
- **Source Script:** `src/phase5_02_subgroup_discrimination.py`, `src/phase5_04_inference.py`
- **Input Data:** `results/predictions/test_set_recalibrated_predictions.csv`
- **Fitting Data:** None (Evaluation only using frozen global Youden thresholds)
- **Evaluation Data:** Locked Test Set (N=2,146: Normal N=559, Overweight N=690, Obese N=861)
- **Protocol Document:** `PHASE5_FAIRNESS_RESULTS_REPORT.md`

### Claim 4.2: Age 60+ Sensitivity Deficit (4/5 Models)
- **Claim:** Participants aged 60+ experience sensitivity deficits (11.2% to 14.7%) significant in 4/5 models (RF, XGB, LGBM, MLP), while Logistic Regression displays a directionally consistent but non-significant gap.
- **Table / Figure:** `results/fairness/fairness_inference.csv`
- **Result File:** `results/fairness/subgroup_discrimination_metrics.csv`
- **Source Script:** `src/phase5_04_inference.py`
- **Fitting Data:** None
- **Evaluation Data:** Locked Test Set (N=2,146: Age 18–39 N=764, Age 40–59 N=741, Age 60+ N=641)
- **Protocol Document:** `PHASE5_FAIRNESS_RESULTS_REPORT.md`

---

## 5. Conformal Prediction & Uncertainty Lineage (Phase 6)

### Claim 5.1: Marginal Coverage Validity vs. Subgroup Undercoverage Failure
- **Claim:** Standard split conformal prediction (alpha = 0.10) achieves target marginal coverage (88.1% to 90.8%), but systematically fails subgroup coverage in Normal-BMI (76.8% to 82.3%) and Age 60+ (81.1% to 85.6%).
- **Table / Figure:** `results/uncertainty/subgroup_coverage.csv`, `results/uncertainty/marginal_coverage_test_set.csv`
- **Result File:** `results/uncertainty/test_set_prediction_sets.csv`
- **Source Script:** `src/phase6_02_conformal_refit.py`, `src/phase6_03_conformal_calibration.py`, `src/phase6_04_final_test_touch.py`
- **Input Data:** `data/processed/analysis_dataset_primary.parquet`
- **Fitting Data:** Proper-train Refit Set (N=4,005) for model training; Conformal Calibration Set (N=1,002) for nonconformity quantile derivation
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `PHASE6_UNCERTAINTY_RESULTS_REPORT.md`

---

## 6. Mondrian Mitigation Lineage (Phase 7)

### Claim 6.1: FDR-Gated Mondrian Mitigation Resolution
- **Claim:** Group-conditional Mondrian conformal calibration restores coverage in targeted subgroups (5/9 model-subgroup combinations reach >= 90%), but leaves XGBoost with an overall coverage tolerance breach and fails to resolve the true BMI x Age intersection.
- **Table / Figure:** `results/mitigation/test_set_mitigation_final.csv`
- **Result File:** `results/mitigation/test_set_mitigation_final.csv`
- **Source Script:** `src/phase7_02_mitigation_implementation.py`, `src/phase7_04_final_test_touch.py`
- **Fitting Data:** Conformal Calibration Set (N=1,002, subgroup-partitioned)
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `PHASE7_MITIGATION_RESULTS_REPORT.md`

### Claim 6.2: Genuine Joint Intersectional Mitigation (Exploratory)
- **Claim:** Fitting Mondrian conformal quantiles directly on the joint BMI x Age intersection (N=138 cal) restores intersection coverage to 90.8%–94.9% across all 5 models, at the cost of expanding set sizes and creating overall coverage tolerance breaches in 2/5 models (XGBoost 94.6%, LightGBM 94.8%).
- **Table / Figure:** `results/mitigation/joint_intersectional_mitigation.csv`
- **Result File:** `results/mitigation/joint_intersectional_mitigation.csv`
- **Source Script:** Executed during P0/P1 remediation pass
- **Fitting Data:** Conformal Calibration Set (N=1,002, joint-partitioned)
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `ITEMS_1_5_REFINEMENT_ADDENDUM.md`

---

## 7. Demographic Holdout Generalization Lineage (Phase 8)

### Claim 7.1: Non-Hispanic Black (NHB) Demographic Holdout Transportability Loss
- **Claim:** Training on non-NHB participants (N=5,366) and evaluating on an NHB holdout set (N=1,787) results in moderate AUROC loss (0.82–0.84 → 0.7719–0.7893) and severe calibration instability.
- **Table / Figure:** `PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md`
- **Result File:** `results/validation/nhb_holdout_predictions_*.csv`
- **Source Script:** `src/phase8_01_partition_and_leakage_check.py`, `src/phase8_02_train_and_holdout_evaluate.py`
- **Input Data:** Non-NHB Training Split (N=5,366)
- **Fitting Data:** Non-NHB Training Split (N=5,366)
- **Evaluation Data:** NHB Holdout Set (N=1,787)
- **Protocol Document:** `PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md`

---

## 8. Diagnostic Pass (Three Diagnostics D02–D05) Lineage

### Claim 8.1: Continuous BMI RCS-Spline Gradient (D02)
- **Claim:** Sensitivity and conformal coverage exhibit smooth, monotonic gradients across continuous BMI (sensitivity 0.43→0.96, coverage 0.98→0.55 from normal to severely obese), proving the BMI gap is a genuine continuous physiological gradient, not a categorical cutpoint artifact.
- **Table / Figure:** `results/diagnostics/continuous_bmi_metrics.csv`, `results/diagnostics/FINAL_THREE_DIAGNOSTICS_REPORT.md`
- **Result File:** `results/diagnostics/continuous_bmi_metrics.csv`
- **Source Script:** `src/sens_04_continuous_splines.py` (Commit `5f1f9e5`)
- **Input Data:** `validation_predictions_*.csv` (OOF), `analysis_dataset_primary.parquet`
- **Fitting Data:** OOF Validation Set (N=5,007) for RCS basis logistic regressions (4 knots at 5th, 35th, 65th, 95th training percentiles)
- **Evaluation Data:** Locked Test Set (N=2,146, decile-binned)
- **Protocol Document:** `documentation/diagnostics/THREE_DIAGNOSTICS_PROTOCOL_FREEZE.md`, `results/diagnostics/TEST_SET_CONTAMINATION_AUDIT.md`

### Claim 8.2: Continuous Age & Finer Age-Band Non-Monotonic Pattern (D03)
- **Claim:** Sensitivity peaks near age 65 and plateaus/declines in 70+, proving the Age 60+ gap is non-monotonic and not a sharp cutpoint artifact.
- **Table / Figure:** `results/diagnostics/continuous_age_metrics.csv`, `results/diagnostics/fine_age_band_metrics.csv`
- **Result File:** `results/diagnostics/continuous_age_metrics.csv`, `results/diagnostics/fine_age_band_metrics.csv`
- **Source Script:** `src/sens_04_continuous_splines.py` (Commit `5f1f9e5`)
- **Fitting Data:** OOF Validation Set (N=5,007)
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `documentation/diagnostics/THREE_DIAGNOSTICS_PROTOCOL_FREEZE.md`

### Claim 8.3: Subgroup-Specific Youden Thresholds (D05) — Two-Mechanism Finding
- **Claim:** Subgroup-specific Youden thresholds shrink the BMI sensitivity gap by 50%–67% (threshold-driven mechanism), but worsen the Age 60+ sensitivity gap for all 5 models (non-threshold-driven mechanism).
- **Table / Figure:** `results/diagnostics/group_specific_threshold_metrics.csv`
- **Result File:** `results/diagnostics/group_specific_threshold_metrics.csv`
- **Source Script:** `src/sens_06_group_specific_thresholds.py` (Commit `f1b03ac`)
- **Fitting Data:** OOF Validation Set (N=5,007, per subgroup)
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `documentation/diagnostics/THREE_DIAGNOSTICS_PROTOCOL_FREEZE.md`

### Claim 8.4: Subgroup-Specific Recalibration & Conformal Quantiles (D04)
- **Claim:** Subgroup-specific Platt recalibration does not improve Brier scores or Hosmer-Lemeshow metrics, but re-derived subgroup conformal quantiles restore BMI Obese coverage to 89.9%–91.6% (outperforming Mondrian), while Age 60+ coverage remains below target (86.7%–88.0%). This refutes the assumption that "better calibration implies better conformal coverage."
- **Table / Figure:** `results/diagnostics/subgroup_recalibration_metrics.csv`, `results/diagnostics/subgroup_recalibration_conformal_metrics.csv`
- **Result File:** `results/diagnostics/subgroup_recalibration_metrics.csv`, `results/diagnostics/subgroup_recalibration_conformal_metrics.csv`
- **Source Script:** `src/sens_05_subgroup_recalibration.py` (Commit `f362a33`)
- **Fitting Data:** OOF Validation Set (N=5,007) for Arm A Platt; Conformal Calibration Set (N=1,002) for Arm B Platt & quantiles
- **Evaluation Data:** Locked Test Set (N=2,146)
- **Protocol Document:** `documentation/diagnostics/THREE_DIAGNOSTICS_PROTOCOL_FREEZE.md`

---

## 9. Parallel & Supplementary Diagnostic Analyses Lineage

### Claim 9.1: Socio-Conformal Literature Audit (D01)
- **Claim:** arXiv:2605.05562 (Das & Rafe 2026) investigates ordinal conformal prediction in Pew survey data using James-Stein shrinkage; it poses low novelty threat to this clinical binary elastography study.
- **Status:** `EXECUTED` (parallel session), provisionally accepted
- **Result File:** `documentation/final_audit/SOCIO_CONFORMAL_AUDIT_AND_CROSS_SESSION_ADDENDUM.md`, `results/diagnostics/stage0_decision_report.md`
- **Protocol Document:** `results/diagnostics/ANALYSIS_MANIFEST_FINAL.csv`

### Claim 9.2: Equal Opportunity Fairness Post-Processing (D06)
- **Claim:** Enforcing Equal Opportunity thresholding closes sensitivity gaps (+50–80 pp) at severe specificity costs (~40 pp drop), leaving probability calibration unaffected.
- **Status:** `EXECUTED` (parallel session), `UNVERIFIED` (suspected raw/recalibrated probability scale mismatch)
- **Result File:** `results/diagnostics/stage1/fairness_postprocessing_results.csv`
- **Source Script:** `src/sens_07_fairness_postprocessing.py`
- **Protocol Document:** `results/diagnostics/stage1_decision_report.md`

### Claim 9.3: Adaptive Full Conformal Prediction (AFCP) Comparison (D07)
- **Claim:** AFCP KNN approximation achieves similar subgroup coverage to Mondrian but inflates overall coverage to 92.5%–93.8%, decreasing set-size efficiency.
- **Status:** `BLOCKED` / `INVALID` (Rule violation: non-faithful KNN approximation labeled as AFCP)
- **Result File:** `results/diagnostics/stage1/afcp_vs_mondrian_comparison.csv`
- **Source Script:** `src/sens_08_afcp_comparison.py` (Line 10 explicit KNN admission)
- **Protocol Document:** `results/diagnostics/stage1_decision_report.md`

---

## 10. Summary Lineage Matrix

| Claim ID | Primary Finding | Key Result File | Source Script | Fitting Partition | Evaluation Partition | Provenance Status |
|---|---|---|---|---|---|---|
| 1.1 | Primary Cohort (N=7,153) | `analysis_dataset_primary.parquet` | `15_create_master_dataset.py` | None | N=7,153 | Verified & Frozen |
| 2.1 | Baseline AUROC (0.82–0.84) | `test_predictions_*.csv` | `phase3_06...py` | Train N=5,007 | Test N=2,146 | Verified & Frozen |
| 3.1 | Prior-Shift Miscalibration | `primary_metrics_by_model.csv` | `phase4_05...py` | OOF N=5,007 | OOF / Test | Verified & Frozen |
| 3.2 | Platt Recalibration | `test_set_calibration_final.csv` | `phase4_09...py` | OOF N=5,007 | Test N=2,146 | Verified & Frozen |
| 4.1 | BMI Fairness Deficit | `fairness_inference.csv` | `phase5_04...py` | None | Test N=2,146 | Verified & Frozen |
| 5.1 | Conformal Subgroup Deficit | `subgroup_coverage.csv` | `phase6_04...py` | Cal N=1,002 | Test N=2,146 | Verified & Frozen |
| 6.1 | Mondrian Mitigation | `test_set_mitigation_final.csv` | `phase7_04...py` | Cal N=1,002 | Test N=2,146 | Verified & Frozen |
| 7.1 | NHB Holdout Drop | `nhb_holdout_predictions_*.csv` | `phase8_02...py` | Train N=5,366 | Holdout N=1,787 | Verified & Frozen |
| 8.1 | Continuous BMI Gradient | `continuous_bmi_metrics.csv` | `sens_04...py` | OOF N=5,007 | Test N=2,146 | Verified & Frozen |
| 8.2 | Continuous Age Curve | `continuous_age_metrics.csv` | `sens_04...py` | OOF N=5,007 | Test N=2,146 | Verified & Frozen |
| 8.3 | Subgroup Youden Thresholds | `group_specific_threshold_metrics.csv` | `sens_06...py` | OOF N=5,007 | Test N=2,146 | Verified & Frozen |
| 8.4 | Subgroup Recalibration | `subgroup_recalibration_metrics.csv` | `sens_05...py` | Cal N=1,002 | Test N=2,146 | Verified & Frozen |
| 9.1 | Socio-Conformal Audit | `SOCIO_CONFORMAL_ADDENDUM.md` | Manual Fetch | N/A | Full text | Provisionally Accepted |
| 9.2 | Equal Opportunity Thresholds | `fairness_postprocessing_results.csv` | `sens_07...py` | OOF N=5,007 | Test N=2,146 | Unverified |
| 9.3 | AFCP KNN Comparison | `afcp_vs_mondrian_comparison.csv` | `sens_08...py` | Cal N=1,002 | Test N=2,146 | Blocked / Invalid |
