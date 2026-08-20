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

**Reconciliation note (2026-08-19, MI Closure Reconciliation task) — SUPERSEDED, see below:** an
earlier project summary referred to a fifth item, "all-ages 12+," and this note (preserved above
in the original commit history, not deleted) concluded it was "deliberately grouped with item 2
... not an omission." **That conclusion is superseded by the 2026-08-20 CAND_4 Classification
Resolution audit below**, which found it was reached without cross-checking
`statistical_analysis_plan.md`.

**Update (2026-08-20, CAND_4 Classification Resolution task, Amendment #14):** items 1–3 below
have since been **executed** as controlled sensitivity/robustness checks — see
`DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md` for the full result (main findings partially
robust: discrimination, calibration, and the BMI-Obese fairness disparity fully robust; the
Age-60+ fairness disparity directionally robust but loses statistical significance in most
sensitivity variants). Separately, a dedicated source-level audit re-examined the CAND_4
("all-ages 12+," N=8,215) classification question and found the 2026-08-19 note above incomplete:
it cited only `sensitivity_analysis_plan.md` and `primary_cohort_decision.md`, not
`statistical_analysis_plan.md`, which **independently and explicitly tracks CAND_4 as its own
EXPLORATORY-tier item, separate from CAND_2's SECONDARY-tier item** ("All-ages sensitivity
cohort: CAND_4 (N=8,215, includes ages 12-17) — exploratory check of whether adolescent inclusion
changes conclusions"). Cohort-mask evidence from `primary_cohort_decision.md` further shows CAND_2
and CAND_4 are orthogonal, single-axis perturbations of CAND_1 (CAND_2 relaxes only the
elastography-quality rule; CAND_4 relaxes only the age rule) — not the same "cohort robustness"
question. **Both conflicting documents share one commit (`c9c6ee3`) and neither was ever edited
afterward — no historical precedence is recoverable from version history.** Neither historical
Phase 2 document has been modified; this correction is recorded as Amendment #14
(`documentation/end_to_end/protocol_amendment_registry.md`) and in the dedicated
`CAND4_CLASSIFICATION_RESOLUTION_REPORT.md`.

**Final classification: CAND_4 is DISTINCT — EXPLORATORY — UNEXECUTED, tracked separately from
CAND_2 as of this update (item 2b below).** It remains genuinely unexecuted — no cohort,
model, prediction, or result artifact for CAND_4 exists anywhere in the repository (verified via
repository-wide search this pass). Its EXPLORATORY tier (vs. CAND_2/item-3's SECONDARY tier) means
any future CAND_4 result may inform discussion/future-work but may never be silently promoted to
a primary or secondary conclusion (`statistical_analysis_plan.md`'s own Governing Rule).

## 1. Alternative fibrosis threshold (8.0 kPa vs. primary 8.2 kPa)

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 1) |
| Reason for deferral | Two candidate thresholds are both defensible; a low-cost robustness check on the primary threshold choice. Deferred due to scope/time considerations; not used to alter the primary analysis or conclusions. |
| Current status | **EXECUTED 2026-08-20** — see `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md` §10; required no retraining (reused frozen Phase 3 predictions against the already-existing `outcome_sensitivity_8.0kPa` column) |
| Result summary | Test ROC-AUC 0.8145–0.8326 (vs. primary 0.8229–0.8429); calibration pattern and BMI-Obese fairness disparity both STABLE; Age-60+ disparity direction preserved but 2/4 previously-significant models (Random Forest, XGBoost) lose significance at this threshold |
| Retraining required? | No — see above |
| Affects current conclusions? | No material change; see `results/sensitivity/primary_vs_sensitivity_comparison.csv` |

## 2. Alternative elastography eligibility (CAND_2, N=7,639 vs. primary CAND_1, N=7,153)

**As of 2026-08-20 (Amendment #14), CAND_4 is no longer tracked under this item — see item 2b
below.** CAND_2 and CAND_4 are orthogonal, single-axis perturbations of CAND_1 (CAND_2 relaxes
only the elastography-quality rule; CAND_4 relaxes only the age rule), and
`statistical_analysis_plan.md` independently tracks them in two different evidentiary tiers
(CAND_2 = SECONDARY, CAND_4 = EXPLORATORY). The prior grouping (below the line, preserved for
historical record) is superseded.

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 2; `statistical_analysis_plan.md` SECONDARY item 3) |
| Reason for deferral | Phase 1 could not assume the two eligibility populations behave identically. Deferred due to scope/time considerations; not used to alter the primary analysis or conclusions. |
| Scope | CAND_2 only (N=7,639, relaxed elastography-completeness rule), adult restriction unchanged from CAND_1 |
| Current status | **EXECUTED 2026-08-20** — see `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md` §8 |
| Result summary | Test ROC-AUC 0.8526–0.8572 (slightly higher than primary's 0.8229–0.8429); calibration pattern and BMI-Obese fairness disparity STABLE; Age-60+ disparity direction preserved, 3/4 previously-significant models lose significance |
| Retraining required? | No — already performed (fresh 70/30 split, seed=42, frozen Phase 3 hyperparameters reused) |
| Affects current conclusions? | No material change; see `results/sensitivity/primary_vs_sensitivity_comparison.csv` |

## 2b. All-ages 12+ cohort (CAND_4, N=8,215) — DISTINCT item, separated from item 2 on 2026-08-20

| Field | Value |
|---|---|
| Original phase | `statistical_analysis_plan.md` EXPLORATORY item 2 (not `sensitivity_analysis_plan.md`'s numbered list — see the reconciliation note above) |
| Definition | LUAXSTAT==1 (quality-valid, identical to CAND_1's elastography rule) + broad labs + BMI/sex complete, **no adult restriction** (ages 12–150) |
| Scientific question | "Exploratory check of whether adolescent inclusion changes conclusions" (`statistical_analysis_plan.md`, verbatim) — an age-eligibility robustness question, distinct from CAND_2's elastography-quality question |
| Evidentiary tier | **EXPLORATORY** (lower tier than CAND_2's SECONDARY tier) — per `statistical_analysis_plan.md`'s Governing Rule, any future result may inform discussion/future-work but may never be silently promoted to a primary or secondary conclusion |
| Current status | **NOT EXECUTED** — no cohort, model, prediction, or result artifact for CAND_4 exists anywhere in the repository (verified via repository-wide search, 2026-08-20) |
| Classification | **DISTINCT — EXPLORATORY — UNEXECUTED** (Amendment #14, `CAND4_CLASSIFICATION_RESOLUTION_REPORT.md`) |
| Retraining required? | Yes, if ever executed — requires constructing the cohort and refitting all 5 models |
| Affects current conclusions? | No — unexecuted; the three completed sensitivity analyses (items 1–3 above) are independently verified unaffected by this classification question |
| Recommended future-work status | Optional future work, EXPLORATORY tier — not required before manuscript preparation; the documentation classification question (this update) and the scientific-necessity question (whether to ever execute it) are kept separate, per this task's own governing principle |

## 3. Broad-lab (primary) vs. fasting-extended (secondary) predictor architecture

| Field | Value |
|---|---|
| Original phase | Phase 2 (`sensitivity_analysis_plan.md` item 3) |
| Reason for deferral | Already elevated to a full SECONDARY analysis (not merely a sensitivity check) per `statistical_analysis_plan.md`, given its importance to the metabolic-signal question. Deferred due to scope/time considerations; not used to alter the primary analysis or conclusions. |
| Current status | **EXECUTED 2026-08-20** — see `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md` §9 (CAND_3, already-built Phase 2 dataset, N=3,582, verified against archived count) |
| Result summary | Test ROC-AUC 0.8280–0.8457; calibration pattern and BMI-Obese fairness disparity STABLE; Age-60+ disparity direction preserved, all 4 previously-significant models lose significance (smallest cohort, most attenuated) |
| Retraining required? | No — already performed (fresh 70/30 split, seed=42, frozen Phase 3 hyperparameters reused, 12 predictors) |
| Affects current conclusions? | No material change; see `results/sensitivity/primary_vs_sensitivity_comparison.csv` |

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
after seeing results requires a logged protocol amendment, not an ad hoc addition. **As of this
2026-08-20 update: items 1, 2, and 3 have been executed (`DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_
REPORT.md`); item 4 was executed narrowly on 2026-08-19 (Non-Hispanic Black scope only); item 2b
(CAND_4, formally separated from item 2 on 2026-08-20, Amendment #14) remains DISTINCT —
EXPLORATORY — UNEXECUTED.** All four originally-numbered items are now executed; CAND_4 is not,
and was never, one of the four — its correct status is tracked in item 2b, not silently folded
into item 2's now-complete status. None has been silently marked complete because related context
was discussed in a report — this document is the explicit, current status record.
