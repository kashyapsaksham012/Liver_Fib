# Liver Fibrosis ML Reliability Study

## Research question
In adults with a quality-valid transient elastography exam, how accurately, fairly, and reliably
can routine demographic and laboratory predictors identify significant liver fibrosis — and does a
model that looks acceptable on discrimination and calibration alone still fail reliability
guarantees for specific demographic subgroups?

## Cohort and outcome
NHANES 2017–March 2020 (pre-pandemic release), primary analytic cohort N=7,153, 666 positive
(9.31% prevalence). Outcome: `LUXSMED ≥ 8.2 kPa` (significant fibrosis by vibration-controlled
transient elastography), frozen before any model was trained.

## Predictors
10 routine variables: age, sex, BMI, ALT, AST, albumin, ALP, total bilirubin, platelet count,
HDL-cholesterol. Race/ethnicity is **excluded as a model input** and retained only for post-hoc
fairness stratification — an explicit design choice, not an omission.

## Models
Logistic Regression, Random Forest, XGBoost, LightGBM, and an MLP — evaluated head-to-head, with no
statistically significant pairwise difference in discrimination (test AUC 0.8229–0.8429).

## Primary findings
- **Calibration**: the four class-balanced models substantially overpredict risk in their raw
  output (a training-time class-balancing artifact); out-of-fold Platt recalibration corrects this
  without affecting discrimination.
- **Fairness**: Normal-BMI patients show 27–48 percentage points lower sensitivity than Obese
  patients (all 5 models); patients 60+ show a similar deficit vs. 40–59 in 4 of 5 models.
- **Conformal uncertainty**: split conformal prediction meets its 90% marginal coverage target
  overall, but coverage fails specifically for BMI-Obese (76.8–82.3%) and Age-60+ (81.1–85.6%)
  patients — the same subgroups flagged by the fairness audit.
- **Mitigation**: group-wise (Mondrian) recalibration resolves 5 of 9 flagged model×subgroup
  combinations, with a documented residual tolerance breach (XGBoost) and an unresolved
  intersectional-overlap precedence issue.
- **Generalization**: retraining with an entire demographic subgroup (Non-Hispanic Black) withheld
  and evaluating on it shows a moderate discrimination drop (AUC 0.77–0.79) and materially less
  stable calibration than the primary cohort.

## Sensitivity analyses
Three independently-derived cohort/threshold variants (8.0 kPa outcome relabeling, a
relaxed-elastography-eligibility cohort, a fasting-extended-predictor cohort) and a fold-embedded
multiple-imputation check for a documented Non-Hispanic Black selection-bias concern all reproduce
the primary findings' qualitative pattern; details and scope limits in
`documentation/final_audit/FINAL_SCIENTIFIC_INTERPRETATION.md`.

## Current project status
Phases 1–8 and all listed sensitivity analyses are complete. Known open items — no external
(non-NHANES) validation, no intersectional mitigation for the BMI×Age overlap population, an
unresolved XGBoost coverage-tolerance breach, and an unexecuted all-ages sensitivity cohort — are
tracked in full in `documentation/final_audit/REMAINING_ANALYSES_AND_RESEARCH_STATUS.md`.

## Known limitations
No external validation has ever been performed on this project; temporal (cross-cycle) validation
is infeasible within this NHANES release; the Age-60+ fairness finding's direction is robust across
every sensitivity check but its statistical significance is specification-sensitive; the Phase 7
mitigation is a genuine but partial fix, not a resolution.

## Detailed documentation
- Phase-by-phase reports: `PHASE1_DATA_ASSEMBLY_REPORT.md` through
  `PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md` (this directory).
- Sensitivity analyses: `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md`,
  `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`, `RELIABILITY_EXTENSION_RESULTS_REPORT.md`.
- Consolidated, independently-re-verified audit: `documentation/final_audit/` — start with
  `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md` and `FINAL_CLAIM_AUDIT.md`.
- Reproducing this project: `documentation/final_audit/REPRODUCIBILITY.md`.
