# Statistical Analysis Plan (Phase 2P)

**Generated:** 2026-08-18 — defines PRIMARY vs. SECONDARY vs. EXPLORATORY before any model is trained.
Exploratory findings may never be promoted to primary after seeing results (non-negotiable rule 5).

## PRIMARY ANALYSIS

- **Cohort:** CAND_1_QUALITYVALID_ADULT_BROAD (N=7,153) — `primary_cohort_decision.md`.
- **Outcome:** LUXSMED ≥ 8.2 kPa, significant fibrosis, binary — `primary_outcome_definition.md`.
- **Predictors:** 10 broad-lab + demographic + BMI variables — `phase2_predictor_registry.csv`.
- **Missing-data strategy:** Complete-case (by cohort construction) — `missing_data_protocol.md`.
- **Models:** Logistic Regression, Random Forest, XGBoost/LightGBM, simple MLP (per `info.md` Phase 6) —
  no single model is "the" primary model; each is evaluated on the same primary metrics.
- **Primary discrimination metric:** ROC-AUC.
- **Primary calibration metric:** Calibration slope + intercept, and Brier score.
- **Primary fairness dimensions:** Sex, Race/Ethnicity (RIDRETH3), Age (18-39/40-59/60+), BMI
  (Underweight/Normal/Overweight/Obese) — `fairness_subgroup_protocol.md`.
- **Primary uncertainty metric:** Split conformal prediction empirical coverage at 90% nominal target —
  `uncertainty_protocol.md`.

## SECONDARY ANALYSES

1. **Fasting-extended architecture:** CAND_3 cohort (N=3,582), 12 predictors (adds glucose,
   triglycerides) — same models/metrics as primary, compared descriptively (not by performance-driven
   cohort re-selection).
2. **Severity-graded outcome:** Advanced fibrosis (≥9.7 kPa) and cirrhosis (≥13.6 kPa) as an ordinal or
   separate-binary secondary target, primary cohort, primary predictors.
3. **Elastography-eligibility sensitivity cohort:** CAND_2 (N=7,639, non-missing-only eligibility) —
   same primary predictors/outcome, compared to primary-cohort results.

## EXPLORATORY ANALYSES

1. **Intersectional fairness** (sex × race/ethnicity, sex × age, sex × BMI) — 26 intersections evaluated
   for feasibility in `phase2_intersectional_feasibility.csv` (6 primary-feasibility, 14 exploratory, 3
   limited-precision, 3 insufficient-evidence tier). Only the 6 primary-feasibility-tier intersections may
   be treated with any confidence; all others are explicitly exploratory and must be labeled as such in
   any report.
2. **All-ages sensitivity cohort:** CAND_4 (N=8,215, includes ages 12-17) — exploratory check of whether
   adolescent inclusion changes conclusions; not primary because of the clinical-appropriateness reasoning
   in `primary_cohort_decision.md`.
3. **Multiple-imputation missing-data sensitivity** (`missing_data_protocol.md`) — exploratory given it
   introduces an additional modeling assumption (the imputation model itself).
4. **Weighted-loss model training** (`survey_weight_protocol.md`) — exploratory given the genuinely
   unresolved methodological status of ML weighting.
5. **Fairness mitigation** (group-wise calibration, threshold adjustment, reweighting) — exploratory,
   and only attempted AFTER primary fairness results are obtained (Phase 3), never used to select the
   primary cohort/outcome/predictors in this phase.

## Governing Rule

Findings from EXPLORATORY analyses may inform discussion and future-work sections of the eventual thesis,
but may never be substituted for, or silently promoted to, PRIMARY or SECONDARY conclusions after the
fact. Any reclassification requires an explicit, dated protocol amendment recorded in
`PHASE2_PROTOCOL_FREEZE.md`.
