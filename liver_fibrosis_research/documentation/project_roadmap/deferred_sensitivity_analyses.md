# Deferred Sensitivity Analyses — Roadmap

**Generated:** 2026-08-19, live, per Part 13 of the Phase 6 Closure-Clarification task. Names,
counts, and rationale taken verbatim from the authoritative frozen source,
`documentation/phase2/sensitivity_analysis_plan.md` (read live this pass, not from memory).

This document is the single, dedicated tracking record for the 4 Phase-2-frozen sensitivity
analyses. It supersedes the prose-only tracking previously embedded in
`PHASE5_FAIRNESS_RESULTS_REPORT.md` §21–22 and `PHASE6_UNCERTAINTY_RESULTS_REPORT.md` §19 (those
sections remain valid as historical record; this document is the authoritative, current status).

## 1. Alternative fibrosis threshold (8.0 kPa vs. primary 8.2 kPa)

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 1) |
| Reason for deferral | Two candidate thresholds are both defensible; a low-cost robustness check on the primary threshold choice |
| Current status | **NOT EXECUTED** |
| Any execution occurred? | No — no model, prediction, or calibration artifact exists anywhere in the repository for an 8.0kPa outcome definition (verified: no such file found in this or prior audit passes) |
| Authorized for a specific future phase? | Not yet formally scheduled |
| Retraining required? | **Yes** — requires re-deriving the outcome column and refitting all 5 models |
| Priority | Medium — a standard robustness check, no specific finding depends on it |

## 2. Alternative elastography eligibility (CAND_2, N=7,639 vs. primary CAND_1, N=7,153)

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 2) |
| Reason for deferral | Phase 1 could not assume the two eligibility populations behave identically |
| Current status | **NOT EXECUTED** |
| Any execution occurred? | No |
| Authorized for a specific future phase? | Not yet formally scheduled |
| Retraining required? | **Yes** — requires rebuilding the cohort and refitting all 5 models |
| Priority | Medium |

## 3. Broad-lab (primary) vs. fasting-extended (secondary) predictor architecture

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 3) |
| Reason for deferral | Already elevated to a full SECONDARY analysis (not merely a sensitivity check) per `statistical_analysis_plan.md`, given its importance to the metabolic-signal question |
| Current status | **NOT EXECUTED** (as either a secondary analysis or a sensitivity check) |
| Any execution occurred? | No |
| Authorized for a specific future phase? | Not yet formally scheduled |
| Retraining required? | **Yes** — different predictor set (12 predictors, adds glucose/triglycerides), full refit |
| Priority | Medium-High — already a SECONDARY analysis by Phase 2's own classification, not a lower-tier sensitivity check |

## 4. Complete-case (primary) vs. multiple-imputation missing-data strategy

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 4) |
| Reason for deferral | The concrete, documented differential-missingness finding for Non-Hispanic Black participants (41.3% of complete-case exclusions vs. 25.0% of retained, `missing_data_protocol.md`) — a targeted response to a real finding, not a generic robustness check |
| Current status | **NOT EXECUTED** — confirmed exhaustively this pass: `find . -iname "*imput*"` across the entire repository returns zero results; no imputation model, imputed dataset, or imputation-derived prediction/calibration artifact exists anywhere; no git commit has ever added such a file; the only "impute" string matches in `src/phase6_*.py` are the unrelated, standard `SimpleImputer(strategy="median")` preprocessing no-op used throughout Phases 1–6 (0% missingness in the primary cohort, so this step is defensive, not a missing-data strategy) |
| Authorized for a specific future phase? | Not yet formally scheduled |
| Retraining required? | **Yes** — requires constructing an imputed dataset, an imputation model, and refitting all 5 models on it |
| Priority | **High** — directly interpretively relevant to the race/ethnicity fairness findings (Phase 5) and to the Non-Hispanic Black subgroup coverage result (Phase 6), because it bears on whether the analysis population itself is representative of the source population for that group. **This is a sensitivity analysis, not a primary analysis, and remains so unless a later formal protocol explicitly changes its scientific status** — it has not been silently promoted. |

## Governing rule (unchanged from Phase 2)

Per `sensitivity_analysis_plan.md`'s own governing rule: these 4 (plus the already-elevated
secondary architecture, item 3) are the complete, fixed set. Adding a new sensitivity analysis
after seeing results requires a logged protocol amendment, not an ad hoc addition. None of the 4
has been executed as of this document; none has been silently marked complete because related
context was discussed in a report.
