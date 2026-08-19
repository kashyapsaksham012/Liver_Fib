# Phase 8 Handoff — Multiple-Imputation Sensitivity Analysis

**Project Phase 8 = Mentor Phase 14 = "Generalization"**, per
`documentation/phase_numbering_crosswalk.md` (confirmed live this task, not from memory).

This document hands off the completed, narrowly-scoped MI sensitivity analysis to whatever work
begins Phase 8. It does not begin Phase 8 itself.

## A. What was asked

Determine whether complete-case exclusion of 615 participants (7.9% of the N=7,768 quality-valid
adult pool) materially affects Non-Hispanic Black fairness/uncertainty conclusions, using the
Phase-2-frozen multiple-imputation sensitivity analysis
(`documentation/phase2/missing_data_protocol.md`).

## B. What was executed

A two-arm, leakage-safe, symmetric 5-fold CV-OOF comparison (complete-case N=7,153 vs. MI pool
N=7,768, m=5 imputations, `IterativeImputer(BayesianRidge(), sample_posterior=True)`, seeds
42–46), for all 5 primary models at their frozen Youden's J thresholds, restricted to the
Non-Hispanic Black subgroup. Full detail: `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`.

## C. What was explicitly not executed (scope discipline)

- No Phase 3 model comparison, Phase 4 calibration, Phase 5 fairness (all subgroups), Phase 6
  uncertainty (all subgroups), or Phase 7 mitigation was re-run under MI.
- The uncertainty/conformal-coverage comparison under MI was **not authorized** by the frozen
  protocol and was not performed.
- The BMI×Age mitigation threshold-precedence issue (closed in Phase 7) was not reopened; no
  combined BMI+Age rule or new interaction experiment was created.
- The other 3 Phase-2-frozen sensitivity analyses (alternative fibrosis threshold, alternative
  elastography eligibility, fasting-extended predictor architecture) remain **not executed** —
  see `documentation/project_roadmap/deferred_sensitivity_analyses.md` items 1–3.

## D. Result

4 of 5 models: **A — STABLE UNDER MI**. 1 of 5 (MLP): **F — INDETERMINATE** (point estimate
+4.16pp, bootstrap CI includes zero). No model significant after BH-FDR (all adjusted p=0.978). No
reversal or material strengthening detected.

## E. Overall robustness conclusion

**MI ROBUSTNESS PARTIAL** — confirmed for 4/5 models; indeterminate (not contradictory, not
reversed) for MLP due to bootstrap imprecision at this subgroup's sample size. Scoped strictly to
the Non-Hispanic Black CV-OOF sensitivity question under Amendment #12's MI specification — not
generalized to any other subgroup, metric, or missing-data question.

## F. Important premise correction carried forward

No statistically significant Non-Hispanic Black disparity exists in Phase 5 or Phase 6 to begin
with (re-confirmed live this task). Phase 8 work should not assume this MI analysis "resolved a
known Black-subgroup problem" — it tested whether one might be hidden by complete-case exclusion,
and found no material evidence that it is.

## G. Artifacts produced

- `documentation/sensitivity/multiple_imputation_pre_execution_snapshot.md`
- `documentation/sensitivity/mi_protocol_extraction_and_gaps.md`
- `results/sensitivity/multiple_imputation_registry.csv`, `multiple_imputation_diagnostics.csv`,
  `mi_imputed_dataset_{0..4}.csv`
- `results/sensitivity/mi_model_protocol_decision.csv`
- `results/sensitivity/oof_predictions_{complete_case,multiple_imputation}_{model}.csv` (10 files)
- `results/sensitivity/mi_black_subgroup_comparison.csv`
- `tests/test_multiple_imputation_sensitivity.py` (36 checks, all passing)
- `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`
- Amendment #12, `documentation/end_to_end/protocol_amendment_registry.md` and
  `results/end_to_end/protocol_amendment_reconciliation.csv`
- `documentation/project_roadmap/deferred_sensitivity_analyses.md` (updated, items 1–3 reaffirmed
  deferred, item 4 marked executed)

## H. Known limitations for Phase 8 to be aware of

- Black-subgroup positive counts (177–198) limit bootstrap CI precision to roughly ±5–10pp; a true
  effect smaller than this is not distinguishable from noise at this sample size.
- Predictive pooling (mean probability), not Rubin's rules, was used to combine the 5 imputations
  — standard for prediction pooling, but does not decompose into a classical between-imputation
  variance term.
- The 4 remaining deferred sensitivity analyses (Section C) are genuinely open; none has been
  executed, approximated, or ruled out by this task.

## I. No novelty claimed

All methods used (MICE-style multiple imputation via `IterativeImputer`, CV-OOF comparison,
bootstrap CI, BH-FDR) are standard, established techniques applied to this project's own frozen
cohort, predictors, and models. No new statistical method is proposed.

## J. Final status carried forward to Phase 8

**MULTIPLE IMPUTATION COMPLETE — NON-HISPANIC BLACK ROBUSTNESS ASSESSED**
