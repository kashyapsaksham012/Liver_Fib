# Deferred Sensitivity Analysis — Scope Reconciliation

**Generated:** live, before any sensitivity cohort is constructed or any model is trained in this
task. This document answers Part 1's seven required questions using only direct inspection of
the frozen Phase 2 source documents — not memory, not prior conversational summaries, and not
this project's own earlier (and, as shown below, incomplete) closure conclusions.

This task is called **"Deferred Sensitivity Analysis Execution"** throughout. It is explicitly
NOT a new "Phase 9" — `documentation/phase_numbering_crosswalk.md` was re-read this pass and
confirms Project Phase 8 = Mentor Phase 14 ("Generalization") is the last officially-numbered
project phase; no Phase 9 exists anywhere in the crosswalk or `info.md`. This task has no phase
number and does not claim one.

## 1. Which sensitivity analyses were formally frozen?

The authoritative source is `documentation/phase2/sensitivity_analysis_plan.md` ("Phase 2V"),
read live in full this pass. It defines exactly **4 "Selected Sensitivity Dimensions"**:

| # | Original frozen name (verbatim) | Cohort/mechanism |
|---|---|---|
| 1 | "Alternative fibrosis threshold: 8.0 kPa vs. primary 8.2 kPa" | Same cohort (CAND_1, N=7,153), different outcome label |
| 2 | "Alternative elastography eligibility: CAND_2 (non-missing-only, N=7,639) vs. primary CAND_1 (quality-valid, N=7,153)" | Different cohort, same predictors |
| 3 | "Broad-lab (primary) vs. fasting-extended (secondary) predictor architecture" | Different cohort (CAND_3, N=3,582), different (12-variable) predictor set — **already elevated to SECONDARY status**, not merely a sensitivity check |
| 4 | "Complete-case (primary) vs. multiple-imputation missing-data strategy" | Same cohort population expanded via imputation (N=7,768 full pool) |

`documentation/phase2/statistical_analysis_plan.md` ("Phase 2P") independently corroborates
items 2 and 3 under its own **SECONDARY ANALYSES** tier (3 items: fasting-extended architecture,
severity-graded outcome, elastography-eligibility sensitivity cohort) and item 4 under its
**EXPLORATORY ANALYSES** tier. Both documents were introduced in the same commit (`c9c6ee3`,
2026-08-18 17:57:33 +0530 — confirmed via `git log --follow`, no precedence between them is
recoverable from commit history).

## 2. What was each sensitivity analysis called originally, and what was its scientific purpose?

| # | Name | Scientific purpose (verbatim reasoning) |
|---|---|---|
| 1 | Alternative fibrosis threshold | "the two candidate thresholds are both defensible... and differ by only 0.2 kPa — a natural, low-cost robustness check on the primary threshold choice" |
| 2 | Alternative elastography eligibility | "Phase 1 explicitly could not assume these two populations behave identically" |
| 3 | Fasting-extended architecture | "given its scientific importance to the metabolic-signal question" — elevated to SECONDARY |
| 4 | Multiple-imputation missing-data strategy | "the concrete, documented differential-missingness finding for Non-Hispanic Black participants... a targeted response to a real finding" |

## 3. Which have already been executed?

**Item 4 only** — the targeted MI sensitivity analysis, executed narrowly for the Non-Hispanic
Black CV-OOF sensitivity/FNR question (`MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`,
Commits `30a866a`→`adc9328`). Result: MI ROBUSTNESS PARTIAL (4/5 models STABLE, MLP
INDETERMINATE, all adjusted p=0.978). **This execution is not rerun in this task** (Part 3 below).

## 4. Which remain unexecuted?

Items 1, 2, and 3 — confirmed via `documentation/project_roadmap/deferred_sensitivity_analyses.md`
(live-read this pass): all three still marked **NOT EXECUTED**, with no model, prediction, or
calibration artifact anywhere in the repository for an 8.0kPa outcome, CAND_2, or CAND_3 cohort
(verified: no such file exists under `results/sensitivity/`, `models/`, or `data/processed/`
before this task begins).

## 5. Which are optional vs. required?

None of the 4 are labeled "required" in any frozen document — `sensitivity_analysis_plan.md`'s
own Governing Rule calls them "the complete, fixed set of Phase 3 robustness checks," a
pre-registered list, not a mandatory execution schedule with a deadline. Item 3 (fasting-extended)
carries the highest priority of the three unexecuted items because it is independently elevated
to full SECONDARY-analysis status by both frozen documents (not merely a sensitivity check) —
this is reflected in the execution matrix (Part 4) but does not change the fact that execution
timing was always left open ("Deferred due to scope/time considerations" — the project's own
consistent language across every prior deferred-analysis document).

## 6. Were any later documentation changes inconsistent with the original frozen plan?

**Yes — a genuine, previously incompletely-diagnosed inconsistency was found this pass,
specifically concerning the "all-ages 12+" / CAND_4 question.** This is addressed in full in
Part 2 below. Summary: `sensitivity_analysis_plan.md` states all-ages (CAND_4) is "already
covered as a sensitivity cohort under item 2's broader 'cohort robustness' umbrella... not
duplicated as a fifth item here" — i.e., CAND_4 is folded into item 2 and has no independent
status. But `statistical_analysis_plan.md` lists **"All-ages sensitivity cohort: CAND_4"** as its
own distinct, separately-numbered item under the EXPLORATORY tier (item 2 of 5), entirely
separate from its own SECONDARY-tier item 3 ("Elastography-eligibility sensitivity cohort:
CAND_2") — treating CAND_2 and CAND_4 as two different analyses in two different tiers, not one
folded item. `PHASE2_PROTOCOL_FREEZE.md` (the document both source files' own "Governing Rule"
sections name as the authoritative consolidation) compounds the ambiguity: its own summary table
lists "Sensitivity cohorts | CAND_2 (N=7,639, relaxed eligibility), CAND_4 (N=8,215, all ages)"
side by side on one row (implying parity between them), while a separate row states "Sensitivity
analyses | 4 pre-specified (threshold, eligibility, architecture, missing-data)" (implying only
4 exist, with no explicit 5th).

**Correction to this project's own prior closure work:** the MI Closure Reconciliation task
(`MI_CLOSURE_RECONCILIATION_REPORT.md`, and the resulting note in
`documentation/project_roadmap/deferred_sensitivity_analyses.md`) concluded all-ages/CAND_4 was
cleanly "folded into item 2... not an omission," based on cross-referencing only
`sensitivity_analysis_plan.md` and `primary_cohort_decision.md`. That conclusion did **not**
cross-reference `statistical_analysis_plan.md`, which independently and explicitly tracks CAND_4
as its own EXPLORATORY-tier item. **This archive does not silently let the earlier, incomplete
conclusion stand** — it is corrected here, in Part 2, using the fuller evidence now assembled.
This is disclosed as a genuine finding of this task, not hidden.

## 7. Final determination for this reconciliation document

Items 1, 2, and 3 are unambiguously, consistently frozen across both source documents and are
authorized for execution in this task (Part 4 onward). Item 4 (MI) is complete and not rerun.
The all-ages/CAND_4 question is **not** resolved by this document — full treatment in Part 2 of
the execution below, per the task's own explicit instruction not to guess.
