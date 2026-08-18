# Sensitivity Analysis Plan (Phase 2V)

**Generated:** 2026-08-18 — pre-specified; not every possible sensitivity analysis is run, only those
scientifically justified by decisions made elsewhere in this protocol.

## Selected Sensitivity Dimensions (4, each tied to a specific Phase 2 decision with residual uncertainty)

1. **Alternative fibrosis threshold: 8.0 kPa vs. primary 8.2 kPa.** Justified because the two candidate
   thresholds are both defensible (`primary_outcome_definition.md`) and differ by only 0.2 kPa — a
   natural, low-cost robustness check on the primary threshold choice.
2. **Alternative elastography eligibility: CAND_2 (non-missing-only, N=7,639) vs. primary CAND_1
   (quality-valid, N=7,153).** Justified because Phase 1 explicitly could not assume these two
   populations behave identically (`elastography_eligibility_protocol.md`).
3. **Broad-lab (primary) vs. fasting-extended (secondary) predictor architecture.** Already elevated to a
   full SECONDARY analysis (not merely a sensitivity check) given its scientific importance to the
   metabolic-signal question — see `statistical_analysis_plan.md`.
4. **Complete-case (primary) vs. multiple-imputation missing-data strategy.** Justified by the concrete,
   documented differential-missingness finding for Non-Hispanic Black participants
   (`missing_data_protocol.md`) — this is not a generic robustness check but a targeted response to a
   real finding.

## Explicitly NOT Selected as Formal Sensitivity Analyses (with reasons)

- **Alternative weighting strategy** — already elevated to its own protocol (`survey_weight_protocol.md`)
  with its own primary/sensitivity split; not duplicated here.
- **Alternative demographic grouping (RIDRETH1 vs. RIDRETH3)** — Phase 1 already produced a
  evidence-based recommendation (RIDRETH3) with clear reasoning (Non-Hispanic Asian preservation); running
  a full parallel RIDRETH1 analysis would not resolve any open uncertainty, only reproduce a known,
  already-explained category collapse. Not selected.
- **Model family as a "sensitivity analysis"** — model family comparison is a PRIMARY analysis structural
  element (all 4 families are run and reported; see `model_development_protocol.md`), not a sensitivity
  perturbation of a single chosen model.
- **Alternative uncertainty method** — the original research plan explicitly recommends conformal
  prediction as primary specifically because it is easier to interpret than the alternatives (`info.md`
  Phase 12); running MC dropout/ensembles as a full parallel sensitivity track adds substantial Phase 3
  scope without a specific documented uncertainty about the conformal-prediction choice itself. Not
  selected as a Phase 2-frozen sensitivity analysis (may still be explored informally in Phase 3 as
  exploratory work, per `statistical_analysis_plan.md`).
- **All-ages (12-17y) cohort** — already covered as a sensitivity cohort under item 2's broader "cohort
  robustness" umbrella and separately listed as CAND_4 in `primary_cohort_decision.md`; not duplicated as
  a fifth item here.

## Governing Rule

These 4 (plus the already-elevated secondary architecture) are the complete, fixed set of Phase 3
robustness checks. Adding a new sensitivity analysis after seeing Phase 3 results requires a logged
protocol amendment (`PHASE2_PROTOCOL_FREEZE.md`), not an ad hoc addition.
