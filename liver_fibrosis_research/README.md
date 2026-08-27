# Liver Fibrosis ML Reliability Study

> **New readers / anyone citing a number: start with
> [`documentation/START_HERE.md`](documentation/START_HERE.md)** — it fixes the documentation
> authority order, records what is superseded, and adjudicates the known conflicts. The repository
> is at its **pre-manuscript evidence freeze** (see the `evidence-freeze` git tag).

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
the primary findings' qualitative pattern (the BMI-Obese disparity is stable in 15/15 instances;
the Age-60+ disparity's direction never reverses but its statistical significance is lost in 9/12).
Scope limits in `documentation/final_research_audit/FINAL_SCIENTIFIC_FINDINGS.md`.

## Follow-up work completed since the original Phases 1–8
- **BMI-fairness investigation (its own Phases 0–7):** independent reproduction of the disparity,
  mechanism diagnosis (score-distribution + threshold, non-causal), and a structured mitigation
  search — **no acceptable BMI-sensitivity mitigation was identified**; XGBoost coverage-breach
  retuning also found no acceptable candidate. `documentation/fairness_bmi_investigation/`.
- **NHANES 2021–2023 temporal validation (separate work, complete):** frozen models/thresholds/
  conformal parameters applied to a later cycle (N=4,910). Result: **PARTIAL TEMPORAL REPLICATION**
  — discrimination fell (AUROC 0.777–0.782), the BMI-Obese sensitivity disparity persisted and
  enlarged, the Age-60+ disparity shrank/reversed, subgroup and intersectional conformal
  under-coverage persisted, and the frozen intersectional-mitigation configuration held for only
  1/5 models. `results/temporal_validation/PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md`.

## Current project status
Phases 1–8, the BMI-fairness investigation, the full sensitivity suite, and a temporal cycle are
complete. The repository is at its **pre-manuscript evidence freeze**. No non-validation analysis
is required before manuscript preparation. Open items — no external (non-NHANES) validation, no
acceptable BMI-sensitivity mitigation, an unresolved XGBoost coverage-tolerance breach, no primary
joint mitigation for the BMI×Age overlap, and an unexecuted all-ages sensitivity cohort — are
tracked in `documentation/final_research_audit/FINAL_REMAINING_WORK_REGISTER.md`.

## Known limitations
No external (non-NHANES) validation has been performed; the only out-of-sample evidence is the
NHANES 2021–2023 temporal work, which is a **partial**, not full, replication. The Age-60+ fairness
finding's direction is robust but its statistical significance is specification-sensitive (and
reverses in the temporal cycle). The Phase 7 mitigation is a genuine but partial fix (5/9), not a
resolution. Full limitations register:
`documentation/final_research_audit/FINAL_LIMITATIONS_REGISTER.md`.

## Detailed documentation
- **Authority map and reading order: `documentation/START_HERE.md` (read first).**
- Current master synthesis: `documentation/final_research_audit/FINAL_RESEARCH_AUDIT.md`;
  narrative history: `documentation/final_audit/MASTER_END_TO_END_RESEARCH_REPORT.md`.
- Phase-by-phase reports: `PHASE1_DATA_ASSEMBLY_REPORT.md` through
  `PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md` (this directory).
- Sensitivity / extension reports: `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md`,
  `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`, `RELIABILITY_EXTENSION_RESULTS_REPORT.md`.
- Reproducing this project: `documentation/final_audit/REPRODUCIBILITY.md`.
