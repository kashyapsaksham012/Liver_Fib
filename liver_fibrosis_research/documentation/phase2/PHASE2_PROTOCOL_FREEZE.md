# PHASE 2 PROTOCOL FREEZE

**Generated:** 2026-08-18 — **This document is the authoritative pre-modeling protocol.** No change may
be made after model training begins (Phase 3) without an explicit, dated protocol amendment logged in a
new section appended to the end of this file.

## Frozen Decisions

| Decision | Value | Source document |
|---|---|---|
| Primary cohort | CAND_1_QUALITYVALID_ADULT_BROAD, N=7,153 (adult, LUAXSTAT==1, broad labs + BMI + sex complete) | `primary_cohort_decision.md` |
| Secondary cohort | CAND_3_QUALITYVALID_ADULT_FASTING, N=3,582 | `primary_cohort_decision.md` |
| Sensitivity cohorts | CAND_2 (N=7,639, relaxed eligibility), CAND_4 (N=8,215, all ages) | `primary_cohort_decision.md` |
| Elastography eligibility | `LUAXSTAT==1` (NHANES quality-valid) | `elastography_eligibility_protocol.md` |
| Primary outcome | `LUXSMED >= 8.2 kPa` (significant fibrosis, binary) | `primary_outcome_definition.md` |
| Sensitivity outcome | `LUXSMED >= 8.0 kPa` | `primary_outcome_definition.md` |
| Secondary outcome | `LUXSMED >= 9.7 kPa` (advanced fibrosis), `>= 13.6 kPa` (cirrhosis) | `primary_outcome_definition.md` |
| Primary predictor set (10) | RIDAGEYR, RIAGENDR, BMXBMI, LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD | `phase2_predictor_registry.csv` |
| Secondary predictors (+2, fasting arch. only) | LBXGLU, LBXTR | `phase2_predictor_registry.csv` |
| Excluded: outcome-only | LUXSMED, LUXCAPM | `phase2_final_leakage_registry.csv` |
| Excluded: quality-only | LUAXSTAT, LUXSIQR, LUXSIQRM, LUXCPIQR, BMDSTATS, BMIWT, BMIHT, survey weight/design vars | `phase2_final_leakage_registry.csv` |
| Excluded: fairness-only (not a predictor) | RIDRETH1, RIDRETH3 | `prediction_time_and_leakage_protocol.md` |
| Excluded: unverified | 64 auxiliary LBX*/LBD* labs | `phase2_predictor_registry.csv` |
| Missing-data strategy | Complete-case (primary); multiple imputation (sensitivity) | `missing_data_protocol.md` |
| Fairness dimensions | Sex, RIDRETH3, Age (18-39/40-59/60+), BMI (WHO categories) | `fairness_subgroup_protocol.md` |
| Intersectional analyses | 26 evaluated; 6 primary-feasibility, 14 exploratory, 3 limited-precision, 3 insufficient | `phase2_intersectional_feasibility.csv` |
| Survey weights | Unweighted primary for training/evaluation/fairness; weighted for population-descriptive estimates only | `survey_weight_protocol.md` |
| Train/test split | 70/30 stratified, fixed seed (to be recorded at Phase 3 start), 5-fold CV within training | `model_development_protocol.md` |
| Discrimination metric | ROC-AUC primary; PR-AUC/sensitivity/specificity/PPV/NPV/F1 secondary | `evaluation_metrics_protocol.md` |
| Calibration metric | Slope + intercept + Brier primary; calibration curve + ECE secondary | `evaluation_metrics_protocol.md` |
| Fairness definition | Sensitivity absolute-difference from reference group, primary; 10pp + CI-excludes-zero = meaningful | `fairness_definition.md` |
| Uncertainty method | Split conformal prediction, 90% target coverage, subgroup coverage evaluated | `uncertainty_protocol.md` |
| Multiple comparisons | FDR (Benjamini-Hochberg) within dimension×model×metric families; exploratory tier uncorrected | `multiple_comparisons_protocol.md` |
| Sensitivity analyses | 4 pre-specified (threshold, eligibility, architecture, missing-data) | `sensitivity_analysis_plan.md` |

## Amendment Log

*(No amendments yet. Any future change to a frozen decision above must be appended here with: date,
decision changed, old value, new value, reason, and confirmation that no Phase 3 model results influenced
the change.)*
