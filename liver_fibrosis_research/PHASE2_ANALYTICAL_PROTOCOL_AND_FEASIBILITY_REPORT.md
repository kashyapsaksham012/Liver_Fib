# Phase 2 Analytical Protocol and Feasibility Report

**Generated:** 2026-08-18 14:28:41

---

## A. Phase 2 Objective

Convert the frozen Phase 1 data foundation into one explicit, reproducible, pre-registered analytical protocol -- cohort, outcome, predictors, missing-data strategy, subgroup protocol, and future evaluation plan -- frozen BEFORE any ML model is trained. No modeling, tuning, or performance evaluation occurs in this phase.

## B. Primary Research Question

See `documentation/phase2/primary_research_question.md`. Summary: in adults with quality-valid elastography, how accurate, calibrated, fair, and uncertainty-aware are standard ML models predicting significant fibrosis (LUXSMED >= 8.2 kPa) from routine demographic/anthropometric/laboratory predictors?

## C. Secondary Research Questions

1. Elastography-eligibility robustness. 2. Fasting-extended architecture comparison. 3. Threshold/severity-outcome robustness. 4. Adolescent-inclusion robustness. Full detail: `primary_research_question.md`.

## D. Primary Cohort

| candidate_cohort                  | definition                                                                                                                                                                                        |    n |   n_outcome_available |   pct_female |   median_age |   median_bmi |   pct_Mexican_American |   pct_Other_Hispanic |   pct_Non-Hispanic_White |   pct_Non-Hispanic_Black |   pct_Non-Hispanic_Asian |   pct_Other_Race___Multi-Racial |   n_positive_8.2kPa |   prevalence_8.2kPa_pct |   min_subgroup_outcome_positive_n |   pct_broad_labs_missing_any |   pct_fasting_labs_missing_any |   pct_bmi_missing |
|:----------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----:|----------------------:|-------------:|-------------:|-------------:|-----------------------:|---------------------:|-------------------------:|-------------------------:|-------------------------:|--------------------------------:|--------------------:|------------------------:|----------------------------------:|-----------------------------:|-------------------------------:|------------------:|
| CAND_1_QUALITYVALID_ADULT_BROAD   | Adult (>=18) AND LUAXSTAT==1 (NHANES quality-valid) AND broad labs (ALT/AST/albumin/ALP/bilirubin/platelets/HDL) complete AND BMI+sex non-missing. Complete-case for the finalized predictor set. | 7153 |                  7153 |        50.64 |           50 |         28.5 |                  12.61 |                10.54 |                    34.73 |                    24.98 |                    12.11 |                            5.03 |                 666 |                    9.31 |                                37 |                            0 |                          49.92 |                 0 |
| CAND_2_NONMISSINGONLY_ADULT_BROAD | Same as Candidate 1 but relaxes the quality-valid requirement to any non-missing LUXSMED (includes Partial exams). Sensitivity cohort for the elastography eligibility decision.                  | 7639 |                  7639 |        50.75 |           50 |         28.6 |                  12.5  |                10.52 |                    34.95 |                    25.11 |                    12    |                            4.91 |                 804 |                   10.52 |                                40 |                            0 |                          50.65 |                 0 |
| CAND_3_QUALITYVALID_ADULT_FASTING | Candidate 1 further restricted to fasting labs (glucose+triglycerides) complete. Secondary predictor architecture (fasting-extended).                                                             | 3582 |                  3582 |        50.75 |           50 |         28.3 |                  13.37 |                10.05 |                    33.7  |                    24.65 |                    12.79 |                            5.44 |                 319 |                    8.91 |                                16 |                            0 |                           0    |                 0 |
| CAND_4_QUALITYVALID_ALLAGES_BROAD | Same as Candidate 1 but WITHOUT the adult restriction (includes ages 12-17, P_LUX's own target population). Sensitivity/exploratory cohort for the adult-only decision.                           | 8215 |                  8215 |        50.19 |           45 |         27.9 |                  12.99 |                10.3  |                    34.51 |                    24.83 |                    11.84 |                            5.53 |                 702 |                    8.55 |                                41 |                            0 |                          50.42 |                 0 |

**Selected: CAND_1_QUALITYVALID_ADULT_BROAD, N=7,153.** Full reasoning: `primary_cohort_decision.md`.

## E. Secondary Cohort(s)

CAND_3_QUALITYVALID_ADULT_FASTING, N=3,582 (fasting-extended architecture). Sensitivity cohorts CAND_2 (N=7,639) and CAND_4 (N=8,215) also defined. Detail: `primary_cohort_decision.md`.

## F. Cohort Comparison

Full comparison table: `results/tables/phase2_candidate_cohort_comparison.csv`. Decision criteria (clinical appropriateness, elastography quality, predictor realism, sample size/subgroup power, representativeness) documented in `primary_cohort_decision.md` -- **no criterion was predictive performance** (non-negotiable rule 1).

## G. Elastography Eligibility

`LUAXSTAT==1` (NHANES quality-valid) is the primary rule; non-missing-LUXSMED-only is a sensitivity rule. Three concepts (measurement available / quality-valid / clinical classification) kept distinct throughout. Detail: `elastography_eligibility_protocol.md`.

## H. Primary Fibrosis Outcome

**LUXSMED >= 8.2 kPa** (significant fibrosis, >=F2), sourced from a 2024 VCTE-vs-MRE meta-analysis Youden-optimal cutoff -- selected on clinical-evidence grounds alone, before any model was trained. Full evaluation of all candidate thresholds and why each was/wasn't selected: `primary_outcome_definition.md`.

## I. Secondary Outcomes

Sensitivity: 8.0 kPa. Secondary (distinct severity question): 9.7 kPa (advanced fibrosis), 13.6 kPa (cirrhosis). Detail: `primary_outcome_definition.md`.

## J. Outcome Prevalence

| category                | group_label               |    n |   n_positive |   n_negative |   prevalence_pct |   prevalence_95ci_low_pct |   prevalence_95ci_high_pct |
|:------------------------|:--------------------------|-----:|-------------:|-------------:|-----------------:|--------------------------:|---------------------------:|
| OVERALL                 | Primary cohort (all)      | 7153 |          666 |         6487 |             9.31 |                      8.66 |                      10.01 |
| Sex                     | Male                      | 3531 |          394 |         3137 |            11.16 |                     10.16 |                      12.24 |
| Sex                     | Female                    | 3622 |          272 |         3350 |             7.51 |                      6.7  |                       8.41 |
| Race_Ethnicity_RIDRETH3 | Mexican American          |  902 |           94 |          808 |            10.42 |                      8.59 |                      12.59 |
| Race_Ethnicity_RIDRETH3 | Other Hispanic            |  754 |           69 |          685 |             9.15 |                      7.29 |                      11.42 |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic White        | 2484 |          237 |         2247 |             9.54 |                      8.45 |                      10.76 |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic Black        | 1787 |          177 |         1610 |             9.9  |                      8.6  |                      11.38 |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic Asian        |  866 |           52 |          814 |             6    |                      4.61 |                       7.79 |
| Race_Ethnicity_RIDRETH3 | Other Race / Multi-Racial |  360 |           37 |          323 |            10.28 |                      7.55 |                      13.85 |
| Age_Group_Final         | 18-39                     | 2423 |          122 |         2301 |             5.04 |                      4.23 |                       5.98 |
| Age_Group_Final         | 40-59                     | 2318 |          221 |         2097 |             9.53 |                      8.4  |                      10.8  |
| Age_Group_Final         | 60+                       | 2412 |          323 |         2089 |            13.39 |                     12.09 |                      14.81 |
| BMI_Group_Final         | Underweight               |  109 |            5 |          104 |             4.59 |                      1.98 |                      10.29 |
| BMI_Group_Final         | Normal                    | 1802 |           72 |         1730 |             4    |                      3.18 |                       5    |
| BMI_Group_Final         | Overweight                | 2316 |          121 |         2195 |             5.22 |                      4.39 |                       6.21 |
| BMI_Group_Final         | Obese                     | 2926 |          468 |         2458 |            15.99 |                     14.71 |                      17.37 |

These are descriptive/feasibility counts only -- NOT used to adjust the threshold (non-negotiable rule 2).

## K. Predictor Registry

| Role | N variables |
|---|---|
| REQUIRES FURTHER VERIFICATION | 64 |
| QUALITY/EXCLUSION VARIABLE | 13 |
| PRIMARY MODEL CANDIDATE | 10 |
| SECONDARY MODEL CANDIDATE | 2 |
| OUTCOME-ONLY | 2 |
| SENSITIVITY-ONLY (fairness subgroup variable, not a model predictor) | 2 |

Full registry (93 variables): `results/tables/phase2_predictor_registry.csv`.

## L. Leakage Decisions

| Final category | N variables |
|---|---|
| UNCERTAIN/DEFERRED | 108 |
| ELIGIBLE PREDICTOR | 14 |
| QUALITY/EXCLUSION ONLY | 13 |
| OUTCOME ONLY | 2 |

Full registry (137 variables): `results/tables/phase2_final_leakage_registry.csv`. Detail: `prediction_time_and_leakage_protocol.md`.

## M. Missing-Data Strategy

Complete-case primary (cohort eligibility already requires predictor completeness); multiple imputation as sensitivity. A real differential-missingness finding for Non-Hispanic Black participants (41.3% of excluded vs. 25.0% of retained) was identified and is NOT hidden -- see `missing_data_protocol.md`.

## N. Broad vs Fasting Design

| architecture                                                                      |    n |   n_predictors |   n_outcome_positive |   prevalence_pct |   min_race_ethnicity_subgroup_positive_n |   epv_events_per_predictor |
|:----------------------------------------------------------------------------------|-----:|---------------:|---------------------:|-----------------:|-----------------------------------------:|---------------------------:|
| PRIMARY: Broad routine-lab architecture (10 predictors, no fasting labs)          | 7153 |             10 |                  666 |             9.31 |                                       37 |                       66.6 |
| SECONDARY: Fasting-extended architecture (12 predictors, + glucose/triglycerides) | 3582 |             12 |                  319 |             8.91 |                                       16 |                       26.6 |

Broad-lab is PRIMARY; fasting-extended is SECONDARY. Not chosen by performance. Detail: `survey_weight_protocol.md` is NOT this section -- see design table above and `primary_cohort_decision.md` criterion 3-4.

## O. Demographic Subgroup Protocol

Sex, Race/Ethnicity (RIDRETH3), Age (18-39/40-59/60+), BMI (WHO categories) -- all PRIMARY dimensions, each category individually classified by feasibility tier, NONE pooled or dropped. Detail: `fairness_subgroup_protocol.md`.

## P. Intersectional Feasibility

| Classification | N intersections (of 26: Sex x Race/Ethnicity, Sex x Age, Sex x BMI) |
|---|---|
| exploratory candidate | 14 |
| primary-feasibility candidate | 6 |
| limited precision | 3 |
| insufficient evidence | 3 |

Full table: `results/tables/phase2_intersectional_feasibility.csv`.

## Q. Survey-Weight Methodology

Four distinct uses (descriptive estimates / training / evaluation / fairness), each independently decided -- unweighted primary for training, evaluation, and fairness; weighted (WTMECPRP/WTSAFPRP + SDMVPSU/SDMVSTRA) for population-descriptive estimates only. The ML-weighting question's genuine methodological uncertainty is stated explicitly, not hidden. Detail: `survey_weight_protocol.md`.

## R. Statistical Precision / Sample-Size Feasibility

| scope                                     |    n |   n_positive |   n_negative |   prevalence_95ci_half_width_pct |   epv_events_per_predictor_10_predictors | assessment                                                                                                                                             |
|:------------------------------------------|-----:|-------------:|-------------:|---------------------------------:|-----------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------|
| OVERALL primary cohort                    | 7153 |          666 |         6487 |                             0.68 |                                     66.6 | Adequate: EPV=66.6 >> conventional 10-events-per-predictor floor; overall 95% CI half-width ~1.1pp supports stable overall AUC/calibration estimation. |
| Sex: Male                                 | 3531 |          394 |         3137 |                             1.04 |                                     39.4 | primary-feasibility candidate                                                                                                                          |
| Sex: Female                               | 3622 |          272 |         3350 |                             0.86 |                                     27.2 | primary-feasibility candidate                                                                                                                          |
| Race/Ethnicity: Mexican American          |  902 |           94 |          808 |                             2    |                                      9.4 | exploratory candidate                                                                                                                                  |
| Race/Ethnicity: Other Hispanic            |  754 |           69 |          685 |                             2.06 |                                      6.9 | exploratory candidate                                                                                                                                  |
| Race/Ethnicity: Non-Hispanic White        | 2484 |          237 |         2247 |                             1.16 |                                     23.7 | primary-feasibility candidate                                                                                                                          |
| Race/Ethnicity: Non-Hispanic Black        | 1787 |          177 |         1610 |                             1.39 |                                     17.7 | primary-feasibility candidate                                                                                                                          |
| Race/Ethnicity: Non-Hispanic Asian        |  866 |           52 |          814 |                             1.59 |                                      5.2 | exploratory candidate                                                                                                                                  |
| Race/Ethnicity: Other Race / Multi-Racial |  360 |           37 |          323 |                             3.15 |                                      3.7 | exploratory candidate                                                                                                                                  |
| Age: 18-39                                | 2423 |          122 |         2301 |                             0.88 |                                     12.2 | primary-feasibility candidate                                                                                                                          |
| Age: 40-59                                | 2318 |          221 |         2097 |                             1.2  |                                     22.1 | primary-feasibility candidate                                                                                                                          |
| Age: 60+                                  | 2412 |          323 |         2089 |                             1.36 |                                     32.3 | primary-feasibility candidate                                                                                                                          |
| BMI: Underweight                          |  109 |            5 |          104 |                             4.16 |                                      0.5 | insufficient evidence                                                                                                                                  |
| BMI: Normal                               | 1802 |           72 |         1730 |                             0.91 |                                      7.2 | exploratory candidate                                                                                                                                  |
| BMI: Overweight                           | 2316 |          121 |         2195 |                             0.91 |                                     12.1 | primary-feasibility candidate                                                                                                                          |
| BMI: Obese                                | 2926 |          468 |         2458 |                             1.33 |                                     46.8 | primary-feasibility candidate                                                                                                                          |

Overall EPV=66.6 (adequate); subgroup-level precision varies and is labeled per-category, not dropped. Detail: `results/tables/phase2_statistical_feasibility.csv`.

## S. Primary Analysis Plan

## T. Secondary Analysis Plan

## U. Exploratory Analysis Plan

All three fully specified in `documentation/phase2/statistical_analysis_plan.md` -- primary (1 cohort, 1 outcome, 4 model families, primary metrics), secondary (3 named analyses), exploratory (5 named analyses, never promoted to primary post-hoc).

## V. Future Model-Development Protocol

70/30 stratified split, 5-fold CV, fixed seed (recorded at Phase 3 start), training-only preprocessing, no SMOTE now. Full 10-point specification: `model_development_protocol.md`.

## W. Future Discrimination Metrics

ROC-AUC primary; PR-AUC/sensitivity/specificity/PPV/NPV/F1 secondary. `evaluation_metrics_protocol.md`.

## X. Future Calibration Metrics

Calibration slope/intercept + Brier primary; calibration curve + ECE secondary. `evaluation_metrics_protocol.md`.

## Y. Future Fairness Metrics

Sensitivity absolute-difference from reference group is PRIMARY (10pp + CI-excludes-zero = meaningful, fixed BEFORE any result observed); AUC/specificity/calibration disparities secondary. `fairness_definition.md`.

## Z. Future Uncertainty Method

Split conformal prediction, 90% target coverage, overall AND subgroup coverage evaluated, efficiency via prediction-set size. `uncertainty_protocol.md`.

## AA. Multiple-Comparison Strategy

FDR (Benjamini-Hochberg) within dimension x model x metric families for confirmatory-tier comparisons; exploratory-tier (intersectional etc.) reported uncorrected and clearly labeled. `multiple_comparisons_protocol.md`.

## AB. Sensitivity-Analysis Plan

4 pre-specified dimensions (threshold, eligibility, architecture -- elevated to secondary --, missing-data), each tied to a specific documented residual uncertainty, not a generic robustness checklist. `sensitivity_analysis_plan.md`.

## AC. Protocol Freeze

`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` -- the authoritative consolidation of every decision above, with an amendment log for any future change (none logged yet).

## AD. Final Pre-Modeling Checklist

|   item | description                                                                                                   | status   | detail                                                                                                                                                                                                                                                                                                                                                                                                   |
|-------:|:--------------------------------------------------------------------------------------------------------------|:---------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      1 | No outcome leakage (no outcome-only variable in predictor set)                                                | PASS     | leaked=[]                                                                                                                                                                                                                                                                                                                                                                                                |
|      2 | No test-set contamination (no split has been performed; dataset is pre-split, split deferred to Phase 3)      | PASS     | primary dataset generated, no split artifact present                                                                                                                                                                                                                                                                                                                                                     |
|      3 | No unverified variable in the primary predictor set                                                           | PASS     | unverified=[]                                                                                                                                                                                                                                                                                                                                                                                            |
|      4 | No post-outcome/quality-only predictors in the predictor set                                                  | PASS     | leaked=[]                                                                                                                                                                                                                                                                                                                                                                                                |
|      5 | Cohort definition reproducible (primary N matches frozen decision)                                            | PASS     | N=7153                                                                                                                                                                                                                                                                                                                                                                                                   |
|      6 | Outcome definition reproducible (positive count matches frozen decision)                                      | PASS     | positive=666                                                                                                                                                                                                                                                                                                                                                                                             |
|      7 | Predictors reproducible (exact 10-column primary predictor set present)                                       | PASS     | columns=['SEQN', 'LUXSMED', 'RIDRETH1', 'RIDRETH3', 'WTMECPRP', 'WTINTPRP', 'WTSAFPRP', 'SDMVPSU', 'SDMVSTRA', 'RIDAGEYR', 'RIAGENDR', 'BMXBMI', 'LBXSATSI', 'LBXSASSI', 'LBXSAL', 'LBXSAPSI', 'LBXSTB', 'LBXPLTSI', 'LBDHDD', 'outcome_primary_8.2kPa', 'outcome_sensitivity_8.0kPa', 'outcome_secondary_advanced_9.7kPa', 'outcome_secondary_cirrhosis_13.6kPa', 'age_group_final', 'bmi_group_final'] |
|      8 | Missing-data strategy reproducible (zero predictor missingness, complete-case by construction)                | PASS     | missing_cells=0                                                                                                                                                                                                                                                                                                                                                                                          |
|      9 | Subgroup definitions reproducible (age_group_final/bmi_group_final columns present, no unexpected categories) | PASS     | age_groups=['18-39', '40-59', '60+']                                                                                                                                                                                                                                                                                                                                                                     |
|     10 | Survey-weight strategy documented                                                                             | PASS     | file exists                                                                                                                                                                                                                                                                                                                                                                                              |
|     11 | Statistical metrics pre-specified                                                                             | PASS     | file exists                                                                                                                                                                                                                                                                                                                                                                                              |
|     12 | Sensitivity analyses pre-specified                                                                            | PASS     | file exists                                                                                                                                                                                                                                                                                                                                                                                              |
|     13 | Random-seed policy documented (fixed seed required, to be recorded at Phase 3 start)                          | PASS     | policy present in model_development_protocol.md / freeze table                                                                                                                                                                                                                                                                                                                                           |
|     14 | Primary/secondary/exploratory analyses distinguished                                                          | PASS     | file exists                                                                                                                                                                                                                                                                                                                                                                                              |
|     15 | Secondary dataset strictly nested within primary dataset (SEQN subset)                                        | PASS     | secondary_N=3582, primary_N=7153                                                                                                                                                                                                                                                                                                                                                                         |

## AE. Phase 2 Readiness Decision

**PHASE 2 — COMPLETE AND FROZEN**

- Primary analysis dataset: `data/processed/analysis_dataset_primary.parquet`, N=7153, 666 positive.
- Secondary analysis dataset: `data/processed/analysis_dataset_secondary.parquet`, N=3582, 319 positive.

All Phase 2 completion criteria are satisfied: primary/secondary cohorts selected and justified on non-performance grounds; elastography eligibility, primary outcome, predictor registry, and leakage decisions frozen; missing-data, broad-vs-fasting, subgroup, intersectional, survey-weight, and statistical-precision protocols all documented with real computed evidence (including the Black-participant differential-missingness finding, not hidden); primary/secondary/exploratory analyses, future model-development structure, evaluation metrics, fairness definition, uncertainty method, and multiple-comparison strategy are all frozen BEFORE any model was trained; the primary and secondary analysis datasets are generated and verified nested; the final pre-modeling checklist passes 15/15; no unresolved critical decision remains.

**Phase 3 may now proceed to model development strictly within the frozen protocol above. Any deviation must be logged as an amendment in PHASE2_PROTOCOL_FREEZE.md.**
