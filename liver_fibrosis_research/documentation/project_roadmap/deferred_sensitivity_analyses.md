# Deferred Sensitivity Analyses — Roadmap

**Generated:** 2026-08-19, live, per Part 13 of the Phase 6 Closure-Clarification task. Names,
counts, and rationale taken verbatim from the authoritative frozen source,
`documentation/phase2/sensitivity_analysis_plan.md` (read live this pass, not from memory).

**Updated:** 2026-08-19, per the "Targeted Sensitivity Analysis Before Phase 8" task (Part 16).
Item 4 (multiple imputation) has now been **executed**, narrowly scoped to the Non-Hispanic Black
complete-case-exclusion question — see `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` for the
full result. Items 1–3 remain deferred; this update reaffirms their status explicitly so none is
silently forgotten as a side effect of item 4's execution. Executing item 4 did not authorize,
imply, or begin execution of items 1–3 — each remains a fully separate, independently-scoped piece
of future work. Deferred due to scope/time considerations; not used to alter the primary analysis
or conclusions.

This document is the single, dedicated tracking record for the 4 Phase-2-frozen sensitivity
analyses. It supersedes the prose-only tracking previously embedded in
`PHASE5_FAIRNESS_RESULTS_REPORT.md` §21–22 and `PHASE6_UNCERTAINTY_RESULTS_REPORT.md` §19 (those
sections remain valid as historical record; this document is the authoritative, current status).

**Reconciliation note (2026-08-19, MI Closure Reconciliation task):** an earlier project summary
referred to a fifth item, "all-ages 12+." This section resolves that reference permanently. Per
the frozen `documentation/phase2/sensitivity_analysis_plan.md` §"Explicitly NOT Selected as Formal
Sensitivity Analyses," verbatim: *"All-ages (12-17y) cohort — already covered as a sensitivity
cohort under item 2's broader 'cohort robustness' umbrella and separately listed as CAND_4 in
`primary_cohort_decision.md`; not duplicated as a fifth item here."* `documentation/phase2/
primary_cohort_decision.md` confirms CAND_4 (N=8,215, ages 12–150, no adult restriction) is listed
under "SENSITIVITY COHORTS" as testing "robustness to the adult-only restriction" — a real,
frozen, documented sensitivity cohort, but **never a separate fifth item in the formal
sensitivity-analysis list**; Phase 2 deliberately grouped it with item 2 (cohort-eligibility
robustness) rather than tracking it independently. This was not an omission, and the consolidation
is documented in the frozen source itself (not merely asserted after the fact). Item 2's status
below now explicitly notes this. **The count of formally tracked sensitivity analyses remains 4,
matching the frozen protocol's own "complete, fixed set" governing rule** — "all-ages 12+" was
never a 5th item to lose track of.

## 1. Alternative fibrosis threshold (8.0 kPa vs. primary 8.2 kPa)

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 1) |
| Reason for deferral | Two candidate thresholds are both defensible; a low-cost robustness check on the primary threshold choice. Deferred due to scope/time considerations; not used to alter the primary analysis or conclusions. |
| Current status | **NOT EXECUTED** — reaffirmed 2026-08-19; the current targeted MI task did not touch this item |
| Any execution occurred? | No — no model, prediction, or calibration artifact exists anywhere in the repository for an 8.0kPa outcome definition (verified: no such file found in this or prior audit passes) |
| Authorized for a specific future phase? | Not yet formally scheduled |
| Retraining required? | **Yes** — requires re-deriving the outcome column and refitting all 5 models |
| Priority | Medium — a standard robustness check, no specific finding depends on it |
| Affects current conclusions? | No — out of scope of the current MI sensitivity task; primary conclusions stand unchanged |
| Recommended future-work status | Candidate for a future dedicated sensitivity-analysis phase, not urgent |

## 2. Alternative elastography eligibility (CAND_2, N=7,639 vs. primary CAND_1, N=7,153)

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 2) |
| Reason for deferral | Phase 1 could not assume the two eligibility populations behave identically. Deferred due to scope/time considerations; not used to alter the primary analysis or conclusions. |
| Scope includes | CAND_2 (N=7,639, relaxed elastography-completeness rule) **and** CAND_4 (N=8,215, all-ages 12+, no adult restriction) — both are Phase-2-frozen "cohort robustness" sensitivity cohorts (`primary_cohort_decision.md`) that Phase 2 deliberately grouped under this single item rather than tracking separately; neither has been executed |
| Current status | **NOT EXECUTED** — reaffirmed 2026-08-19; the current targeted MI task did not touch this item |
| Any execution occurred? | No |
| Authorized for a specific future phase? | Not yet formally scheduled |
| Retraining required? | **Yes** — requires rebuilding the cohort and refitting all 5 models (for either CAND_2 or CAND_4) |
| Priority | Medium |
| Affects current conclusions? | No — out of scope of the current MI sensitivity task; primary conclusions stand unchanged |
| Recommended future-work status | Candidate for a future dedicated sensitivity-analysis phase, not urgent; if executed, CAND_2 and CAND_4 should be treated as two distinct runs even though tracked under one roadmap item |

## 3. Broad-lab (primary) vs. fasting-extended (secondary) predictor architecture

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 3) |
| Reason for deferral | Already elevated to a full SECONDARY analysis (not merely a sensitivity check) per `statistical_analysis_plan.md`, given its importance to the metabolic-signal question. Deferred due to scope/time considerations; not used to alter the primary analysis or conclusions. |
| Current status | **NOT EXECUTED** (as either a secondary analysis or a sensitivity check) — reaffirmed 2026-08-19; the current targeted MI task did not touch this item |
| Any execution occurred? | No |
| Authorized for a specific future phase? | Not yet formally scheduled |
| Retraining required? | **Yes** — different predictor set (12 predictors, adds glucose/triglycerides), full refit |
| Priority | Medium-High — already a SECONDARY analysis by Phase 2's own classification, not a lower-tier sensitivity check |
| Affects current conclusions? | No — out of scope of the current MI sensitivity task; primary conclusions stand unchanged |
| Recommended future-work status | Higher priority than items 1/2 given its SECONDARY classification; recommended for the next dedicated analysis phase |

## 4. Complete-case (primary) vs. multiple-imputation missing-data strategy

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 4) |
| Reason originally deferred | The concrete, documented differential-missingness finding for Non-Hispanic Black participants (41.3% of complete-case exclusions vs. 25.0% of retained, `missing_data_protocol.md`) — a targeted response to a real finding, not a generic robustness check |
| Current status | **EXECUTED 2026-08-19** — see `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`, `results/sensitivity/mi_black_subgroup_comparison.csv`, and Amendment #12 in `documentation/end_to_end/protocol_amendment_registry.md` |
| Scope of execution | Narrowly targeted to the Non-Hispanic Black CV-OOF sensitivity/FNR question only, per the "Targeted Sensitivity Analysis Before Phase 8" task — NOT a full re-run of Phase 3 model comparison, Phase 4 calibration, Phase 5 fairness for every subgroup, Phase 6 uncertainty, or Phase 7 mitigation |
| Result summary | m=5 imputations (`IterativeImputer(BayesianRidge(), sample_posterior=True)`), full pool N=7,768 vs. complete-case N=7,153; Black subgroup N grew from 1,787 (complete-case) to 2,041 (MI pool). Complete-case-vs-MI sensitivity difference was not significant after BH-FDR correction for any of the 5 models (all adjusted p=0.978); 4/5 models classified STABLE UNDER MI, 1/5 (MLP) classified INDETERMINATE (point estimate +4.2pp, but CI includes zero). No model showed a reversed or materially strengthened disparity. |
| Authorized for a specific future phase? | Complete — no further scheduling needed for this narrow question |
| Retraining required? | Already performed (CV-OOF refit only, frozen hyperparameters, never touching the locked test set) |
| Priority | Resolved for the Non-Hispanic Black question. **This remains a sensitivity analysis, not a primary analysis** — it has not been silently promoted, and its result does not alter the frozen primary cohort, outcome, predictor set, or any Phase 3–7 conclusion. |
| Uncertainty/conformal-coverage comparison under MI | **NOT AUTHORIZED** by the frozen `missing_data_protocol.md` (confirmed via full re-read: no Phase-6-era conformal-coverage language exists in that document) and explicitly not performed in this task — remains a genuinely open, separately-scoped future question if a later protocol amendment authorizes it |
| Scope audit (2026-08-19, MI Closure Reconciliation task) | Independently verified: every file touched in Commits B (`4802602`), C (`f73ef91`), D (`adc9328`) is in-scope (MI construction/diagnostics, Black-subgroup comparison, MI test suite, MI report/handoff, this roadmap, the amendment registry) — no BMI/Age, calibration, or mitigation file was touched; `data/processed/splits/test_ids.csv` was not modified by any of the three commits and its hash is unchanged since Phase 3 (`c9c6ee3`). Full detail: `MI_CLOSURE_RECONCILIATION_REPORT.md`. |

## Governing rule (unchanged from Phase 2)

Per `sensitivity_analysis_plan.md`'s own governing rule: these 4 (plus the already-elevated
secondary architecture, item 3) are the complete, fixed set. Adding a new sensitivity analysis
after seeing results requires a logged protocol amendment, not an ad hoc addition. As of this
2026-08-19 update, item 4 has been executed (narrowly, per its documented scope above); items 1–3
remain not executed. None has been silently marked complete because related context was discussed
in a report — this document is the explicit, current status record for all 4.
