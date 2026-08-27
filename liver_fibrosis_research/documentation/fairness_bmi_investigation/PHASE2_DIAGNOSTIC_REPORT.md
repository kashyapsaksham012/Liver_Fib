# Phase 2 BMI Fairness Mechanism Diagnosis

**Study:** Machine Learning for Liver Fibrosis Prediction: A Comprehensive Evaluation of Discrimination, Calibration, Fairness, Conformal Reliability, and Temporal Transportability  
**Status:** COMPLETE — diagnostic only  
**Data used:** 5-fold OOF predictions on the frozen training partition (`N=5,007`), linked to `analysis_dataset_primary.parquet`. The locked test partition was not used for Phase 2 discovery, threshold analysis, or method selection.

## Scope and lineage

The frozen outcome was `outcome_primary_8.2kPa` (LUXSMED >= 8.2 kPa with valid VCTE/LUAXSTAT), and the ten frozen predictors were unchanged. The canonical BMI bins were applied exactly as `pd.cut([0, 18.5, 24.9, 29.9, 200])`; this report uses only Normal-BMI and Obese observations. Frozen age groups were 18–39, 40–59, and 60+. Frozen model thresholds were used only as reference points: Logistic 0.5173, Random Forest 0.4499, XGBoost 0.4108, LightGBM 0.4988, and MLP 0.1065. A 0.00–1.00 grid in 0.01 increments was evaluated without selecting a threshold. File hashes and lineage checks are in `results/fairness_bmi_investigation/phase2_lineage.json`.

## Required outputs

| Analysis | Output |
|---|---|
| Threshold grid | `phase2_oof_threshold_grid.csv` |
| Subgroup discrimination | `phase2_subgroup_discrimination.csv` |
| Positive-case scores | `phase2_positive_case_scores.csv` |
| Negative-case scores | `phase2_negative_case_scores.csv` |
| Threshold crossing | `phase2_threshold_crossing.csv` |
| Calibration by BMI | `phase2_calibration_by_bmi.csv` |
| Predictor distributions | `phase2_predictor_distributions.csv` |
| BMI × age | `phase2_bmi_age_analysis.csv` |
| Figures | `figures/phase2/` |

## Findings

### Threshold dependence and threshold crossing

The sensitivity gap is present over the evaluated threshold range rather than being confined to one threshold. At the frozen operating points, Normal-BMI positive-case false-negative rates were 0.66, 0.54, 0.44, 0.58, and 0.64 for Logistic, Random Forest, XGBoost, LightGBM, and MLP, respectively; corresponding Obese rates were 0.162, 0.162, 0.104, 0.180, and 0.177. Thus, the decision boundary is associated with a substantially larger fraction of Normal-BMI fibrosis cases falling below it, but the grid does not support calling this solely a threshold artifact. Specificity differences and all confusion-matrix components are in the threshold-grid file.

### Threshold-independent discrimination

OOF AUROC (Normal-BMI / Obese) was: Logistic 0.803 / 0.768; Random Forest 0.831 / 0.756; XGBoost 0.828 / 0.762; LightGBM 0.810 / 0.753; MLP 0.814 / 0.770. Bootstrap 95% intervals are reported in the CSV. The Normal-BMI samples contain only 50 positive cases, so intervals are wide and overlap the Obese intervals. The results are evidence of possible subgroup ranking differences, not definitive proof of a statistically distinct AUROC in every model. PR-AUC is also reported. No new inferential test or FDR selection was used.

### Positive- and negative-case score distributions

For every model, actual fibrosis-positive Normal-BMI cases have lower prediction-score distributions than Obese fibrosis-positive cases; two-sided Mann–Whitney p-values are reported in `phase2_positive_case_scores.csv`. The same direction is also present among non-fibrosis cases in every model, with p-values in `phase2_negative_case_scores.csv`. Therefore, the score shift is not restricted to positive cases. These are associations in model scores and do not establish that BMI causes the disparity.

### Calibration by BMI

BMI-stratified calibration intercept, slope, Brier score, and ten-bin equal-width ECE are reported in `phase2_calibration_by_bmi.csv`. Calibration diagnostics differ materially between groups, particularly for Brier/ECE, but prevalence and score-distribution differences contribute to these aggregate measures. This phase did not recalibrate and does not establish that calibration is the sole mechanism.

### Predictor distributions

The predictor-distribution table reports group-specific sample size, mean, standard deviation, median, quartiles, standardized mean difference, and Welch p-value where defined for all ten frozen predictors. Differences describe covariate composition; they are not causal or fairness explanations by themselves.

### BMI × age

BMI × age metrics are in `phase2_bmi_age_analysis.csv`. The Normal-BMI versus Obese sensitivity contrast is visible in the 40–59 and 60+ strata across model families. The 18–39 Normal-BMI cells have six positive cases and are flagged `UNSTABLE_SMALL_CELL`; estimates from those cells must not be overinterpreted. The pattern is compatible with age-related effect modification but does not prove an interaction.

### Existing sensitivity evidence

The repository contains overall discrimination/calibration comparisons for CAND_2, CAND_3, and the 8.0-kPa relabel-only analysis. Those comparisons do not provide a Phase 2 BMI-stratified reproduction of the mechanism. **BMI-specific sensitivity-cohort mechanism consistency: NOT FOUND IN REPOSITORY.**

## Mechanism summary

| Model | Threshold evidence | Score-distribution evidence | Subgroup discrimination evidence | Calibration evidence | BMI × Age evidence | Sensitivity-cohort consistency | Overall mechanism classification | Confidence |
|---|---|---|---|---|---|---|---|---|
| Logistic Regression | Persistent; larger Normal-BMI FN fraction | Positive and negative score shifts | Normal AUROC higher; uncertainty overlaps | Group metrics differ | Present in older strata; young cell unstable | NOT FOUND IN REPOSITORY | MIXED MECHANISM: SCORE-DISTRIBUTION DIFFERENCE + THRESHOLD-RELATED, with possible ranking/calibration contribution | Moderate |
| Random Forest | Persistent | Positive and negative score shifts | Normal AUROC higher; uncertainty overlaps | Group metrics differ | Same pattern; young cell unstable | NOT FOUND IN REPOSITORY | MIXED MECHANISM | Moderate |
| XGBoost | Persistent | Positive and negative score shifts | Normal AUROC higher; uncertainty overlaps | Group metrics differ | Same pattern; young cell unstable | NOT FOUND IN REPOSITORY | MIXED MECHANISM | Moderate |
| LightGBM | Persistent | Positive and negative score shifts | Normal AUROC higher; uncertainty overlaps | Group metrics differ | Same pattern; young cell unstable | NOT FOUND IN REPOSITORY | MIXED MECHANISM | Moderate |
| MLP | Persistent | Positive and negative score shifts | Normal AUROC higher; uncertainty overlaps | Group metrics differ | Same pattern; young cell unstable | NOT FOUND IN REPOSITORY | MIXED MECHANISM | Moderate |

## Model-specific answers to the required questions

For **each of Logistic Regression, Random Forest, XGBoost, LightGBM, and MLP**:  
1. The disparity **persists across thresholds** in the evaluated grid; it is not mainly confined to the frozen operating point.  
2. The frozen point shows substantial threshold crossing, but the grid does not support a threshold-only explanation.  
3. **Yes:** true fibrosis Normal-BMI cases receive systematically lower scores.  
4. **Yes:** non-fibrosis cases also show a score-distribution difference.  
5. Subgroup AUROC differences are suggestive, but bootstrap uncertainty overlaps; material ranking disparity is **not conclusively established**.  
6. BMI-stratified calibration metrics differ; a calibration contribution is plausible, but not isolated as the sole cause.  
7. BMI × age may explain part of the pattern, especially in older strata; young Normal-BMI cells are unstable.  
8. The score-shift and threshold-crossing findings are consistent across all five families.  
9. Supported classification: **mixed empirical mechanism**, dominated by BMI-group score-distribution differences and operating-threshold consequences, with possible calibration/ranking contributions.  
10. Uncertain: causal interpretation, definitive AUROC interaction, stable young-age interaction, and BMI-specific sensitivity-cohort transportability.

## Stop condition

Phase 2 is complete. No mitigation, group-specific threshold, recalibration, retraining, predictor change, temporal validation, external validation, or master-report modification was performed.
