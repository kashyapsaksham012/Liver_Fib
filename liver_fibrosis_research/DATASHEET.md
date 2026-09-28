# Datasheet: analysis cohort (NHANES 2017–March 2020)

Condensed to the Gebru et al. "Datasheets for Datasets" categories that apply to a derived
analysis cohort from a public federal health survey. For anything not covered here, the
authoritative sources are `documentation/data_dictionary/` and `PHASE1_DATA_ASSEMBLY_REPORT.md`.

## Motivation

Built to audit whether ML models predicting significant liver fibrosis from routine
demographic/anthropometric/laboratory data are reliable and equitable across demographic
subgroups — not to build the most accurate fibrosis classifier (that space is already crowded;
see `info.md` for the original scoping rationale).

## Composition

- **Source:** NHANES 2017–March 2020 pre-pandemic cycle, public CDC/NCHS survey data
  (`data/raw/NHANES_2017_2020/`, public-domain `.xpt` files).
- **Root population:** 10,409 participants with an elastography exam attempt
  (`COHORT_0_SOURCE`).
- **Analysis cohort:** 7,153 adults (≥18y) with quality-valid elastography (`LUAXSTAT==1`) and
  zero missingness on all 10 predictors, by construction (complete-case) — 666
  fibrosis-positive, 6,487 negative (prevalence ≈9.3%).
- **Label:** `LUXSMED >= 8.2 kPa` (VCTE-measured liver stiffness), a continuous elastography
  measurement thresholded at a literature Youden-optimal cutoff chosen before modeling, **not**
  a biopsy/histology ground truth — VCTE is itself an imperfect proxy for fibrosis stage
  (see model card limitation 5, temporal validation §, for a related measurement-bias
  investigation).
- **Protected/stratification attributes:** sex, race/ethnicity (`RIDRETH1`/`RIDRETH3`), age,
  BMI. Race/ethnicity is **not** a model input — retained only for fairness stratification, per
  `documentation/phase2/prediction_time_and_leakage_protocol.md`.
- Several other candidate cohort definitions exist in the repo (broader elastography-eligibility
  rule, fasting-extended architecture, adolescent-inclusive) as pre-registered sensitivity
  variants — the 7,153-participant complete-case cohort above is the primary one; see
  `PHASE1_DATA_ASSEMBLY_REPORT.md` for the full cohort-derivation table and why each variant was
  or wasn't used.

## Collection process

Collected by CDC/NCHS via NHANES' standard household interview + mobile examination center
protocol (physical exam, elastography, phlebotomy). This project performed no new data
collection — only cohort derivation, merging, and quality auditing of the public release.

## Preprocessing / cleaning / labeling

- **Complete-case, unweighted.** NHANES uses a complex, multistage probability sample with
  survey weights (`WTMECPRP` etc.); the pre-registered primary analysis is **unweighted**
  complete-case (`documentation/phase2/survey_weight_protocol.md`,
  `documentation/final_research_audit/FINAL_REMAINING_WORK_REGISTER.md`). A survey-weighted BMI
  sensitivity check exists as a post-hoc addendum
  (`documentation/sensitivity/SURVEY_WEIGHTED_REPORT.md`) — it is a secondary check, not a
  reweighting of the primary results.
- No imputation in the primary analysis (complete-case by cohort construction); a targeted
  multiple-imputation sensitivity check exists for one subgroup comparison
  (`MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`) and does not alter the primary findings.
- Full missingness audit trail: `src/06_missingness_audit.py`,
  `documentation/audit_reports/` (per-source-file audits).

## Uses

Intended for reproducing or extending this reliability audit. **Not** intended as a
general-purpose liver-fibrosis prediction benchmark dataset — the cohort, label threshold, and
predictor set were frozen specifically for this fairness/calibration/uncertainty study
(`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`), not optimized for predictive benchmarking.

## Distribution

Raw NHANES `.xpt` files are public domain and redistributed as-is under
`data/raw/NHANES_2017_2020/`. Derived analysis datasets (`data/processed/`) and split
assignments are versioned in this repository under the MIT license (code) — NHANES data itself
carries no additional restriction beyond CDC/NCHS's own public-domain terms.

## Maintenance

Frozen at git tag `evidence-freeze` (2026-08-27); tier 1/2 cohort files are not modified going
forward (see `REPOSITORY_MAP.md` §1, preservation rule). A temporal cohort (NHANES
2021–2023) was later added as a separate, non-modifying tier 4 —
`temporal_validation_2021_2023/`.
