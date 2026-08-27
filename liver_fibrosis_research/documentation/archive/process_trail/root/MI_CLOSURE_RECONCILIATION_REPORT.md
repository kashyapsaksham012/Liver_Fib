# MI Closure Reconciliation Report

## 1. Scope of this closure task

This task answers exactly two documentation/provenance questions: (1) how many sensitivity
analyses are actually deferred, reconciling an apparent "all-ages 12+" discrepancy, and (2) did
the completed multiple-imputation (MI) task's execution (Commits B/C/D) actually stay within its
authorized Non-Hispanic Black scope. It is not a new experiment, sensitivity analysis, test-set
evaluation, Phase 8 execution, or MI re-run.

## 2. MI result being preserved (unchanged by this task)

4/5 models = STABLE UNDER MI; MLP = INDETERMINATE (point estimate +4.16pp, CI spans zero); BH-FDR
adjusted p = 0.978 for all 5 models; no reversal; no material strengthening; overall conclusion =
**MI ROBUSTNESS PARTIAL**. Verified unchanged in `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`
and `results/sensitivity/mi_black_subgroup_comparison.csv` (`tests/test_mi_closure_reconciliation.py`
TEST8).

## 3. Deferred-analysis discrepancy

An earlier project summary referred to a fifth item, "all-ages 12+," alongside the 3 currently
deferred items (alternative threshold, alternative elastography eligibility, fasting-extended
architecture). This section reconciles that reference using the actual frozen Phase-2 source, not
memory or prior summaries.

## 4. Original Phase-2 sensitivity list (verbatim from `documentation/phase2/sensitivity_analysis_plan.md`)

**Selected (4, formally tracked):**
1. Alternative fibrosis threshold: 8.0 kPa vs. primary 8.2 kPa.
2. Alternative elastography eligibility: CAND_2 (N=7,639) vs. primary CAND_1 (N=7,153).
3. Broad-lab (primary) vs. fasting-extended (secondary) predictor architecture.
4. Complete-case (primary) vs. multiple-imputation missing-data strategy.

**Explicitly NOT selected (with reasons), including the relevant entry:**
> "All-ages (12-17y) cohort — already covered as a sensitivity cohort under item 2's broader
> 'cohort robustness' umbrella and separately listed as CAND_4 in `primary_cohort_decision.md`;
> not duplicated as a fifth item here."

Governing rule (verbatim): "These 4 (plus the already-elevated secondary architecture) are the
complete, fixed set of Phase 3 robustness checks."

## 5. All-ages 12+ determination

Cross-checked against `documentation/phase2/primary_cohort_decision.md`, which lists **CAND_4**
(N=8,215, `LUAXSTAT==1` + broad labs + BMI/sex complete, **no adult restriction, ages 12–150**)
under an explicit "SENSITIVITY COHORTS" heading: "CAND_4 (N=8,215) — tests robustness to the
adult-only restriction."

**Determination:** CAND_4/"all-ages 12+" is a real, genuinely frozen Phase-2 sensitivity cohort —
but it was **never a separate, fifth item** in the formal `sensitivity_analysis_plan.md` list.
Phase 2 deliberately grouped it under item 2 (cohort-eligibility robustness) rather than tracking
it as an independent item, and this grouping is documented in the frozen source itself (not
inferred or asserted after the fact). This does not cleanly match any single one of the three
candidate explanations as literally worded in the task prompt:

- It is **not** "never a separately frozen Phase-2 sensitivity analysis... referenced elsewhere"
  in the sense of being absent from Phase 2 — it *is* frozen, by name, in `primary_cohort_decision.md`.
- It is **not** "accidentally omitted" — the omission from the 4-item list is explicit and
  intentional, stated in `sensitivity_analysis_plan.md` itself.
- It is **not** an *undocumented* consolidation — the consolidation ("covered under item 2's
  broader umbrella") is written into the frozen protocol.

The accurate characterization is: **a genuinely frozen sensitivity cohort, intentionally and
transparently folded into item 2's scope, with the fold-in explicitly documented in both source
files.** Restoring it as an independent 5th deferred item would contradict the frozen protocol's
own "complete, fixed set of 4" governing rule; the correct closure action is documentation
clarification, not roadmap expansion.

## 6. Updated deferred roadmap

`documentation/project_roadmap/deferred_sensitivity_analyses.md` updated (not re-created):
- Added a "Reconciliation note" citing both frozen source documents verbatim, permanently
  resolving the "all-ages 12+" question for any future reader.
- Item 2's table now explicitly states its scope covers **both** CAND_2 (relaxed elastography
  completeness) **and** CAND_4 (all-ages 12+) — two distinct cohort variants Phase 2 chose to
  track under one roadmap item — with a note that they should be run as two distinct executions
  if item 2 is ever carried out.
- The roadmap's formally tracked count remains **4** (items 1–4, unchanged), consistent with the
  frozen protocol's own governing rule.
- Item 4 (MI) updated with this task's scope-audit finding (Section 10 below).
- No analysis was executed as part of this update.

## 7. Commit B scope classification (`4802602`)

9 files touched, all Category A (in-scope): `src/mi_01_construct_and_diagnostics.py`, 5 imputed
dataset CSVs, `multiple_imputation_diagnostics.csv`, `multiple_imputation_registry.csv`, and the
Amendment #12 disclosure addendum in `protocol_amendment_registry.md`. Zero files matching
mitigation/recalibration/BMI-threshold/Age-threshold/Phase-7 markers (verified via `git show
--name-only` and source-code grep — zero matches).

## 8. Commit C scope classification (`f73ef91`)

15 files touched, all Category A: `src/mi_02_black_subgroup_comparison.py`,
`src/mi_03_black_subgroup_inference.py`, 10 OOF-prediction CSVs (complete-case + MI arms, 5 models
each), `mi_model_protocol_decision.csv`, `mi_black_subgroup_comparison.csv`, and
`tests/test_multiple_imputation_sensitivity.py`. Source-code inspection of `mi_02`/`mi_03`
confirms: zero references to mitigation, recalibration, BMI/Age-specific thresholds, or Phase 7;
`mi_03` computes exactly one subgroup ("Non-Hispanic Black") and no other race, BMI, or Age
grouping.

## 9. Commit D scope classification (`adc9328`)

3 files touched, all Category A: `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`,
`documentation/sensitivity/phase8_handoff.md`, and the deferred-roadmap update marking item 4
executed while reaffirming items 1–3 as deferred.

**Across all three commits: zero Category B (out-of-scope) files found.** No BMI/Age MI
propagation, no Phase 4 calibration reanalysis, no Phase 7 mitigation-under-MI, and no unrelated
subgroup or sensitivity analysis exists anywhere in this commit range.

## 10. Test-set-touch audit

- `data/processed/splits/test_ids.csv` SHA-256: `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779`
  — identical to the value recorded and independently verified in Phase 6
  (`tests/test_uncertainty_pipeline.py` TEST4).
- `git log --oneline -- data/processed/splits/test_ids.csv` returns exactly **one** commit ever
  (`c9c6ee3`, the original Phase 3 bulk commit) — the file has not been touched since, including
  throughout the entire MI task.
- None of Commits B/C/D's file lists include `data/processed/splits/test_ids.csv` or any other
  test-partition file.
- Source-code grep of `mi_01`/`mi_02`/`mi_03` for `test_ids`, `test_set`, `X_test`, `y_test`,
  "locked test" finds only prose comments explicitly *disclaiming* test-set access — no code path
  loads it.
- OOF-prediction file row counts match the training/CV populations exactly (complete-case N=7,153,
  MI pool N=7,768), not the locked test-set size (N=2,146), a further structural confirmation.

**Conclusion: no test-set touch occurred, authorized or otherwise, during Commits B/C/D.**

## 11. Out-of-scope execution found

**None.** Every file in Commits B, C, and D is within the MI task's authorized Non-Hispanic Black
scope. No BMI/Age MI propagation, no Phase 4 calibration reanalysis, no Phase 7 mitigation-under-MI,
and no full-pipeline MI rerun occurred.

## 12. Amendment handling

Not applicable. No unauthorized or out-of-scope execution was found (Section 11), so no new
amendment was created. The existing Amendment #12 (already logged, disclosed, and committed in the
original MI task) remains the sole and sufficient amendment for this analysis; it is unmodified by
this closure task.

## 13. Confirmation that MI findings were unchanged

Confirmed via `tests/test_mi_closure_reconciliation.py` TEST8: `mi_black_subgroup_comparison.csv`
still contains only classification codes A and F, no model significant after FDR, and
`MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` still states MI ROBUSTNESS PARTIAL, adjusted
p=0.978, +4.16pp MLP estimate, and the MULTIPLE IMPUTATION COMPLETE final status — byte-for-byte
unmodified by this closure task (no edit was made to either file).

## 14. Confirmation that no deferred analysis was executed by this closure

Confirmed via `tests/test_mi_closure_reconciliation.py` TEST9: no new results directory for
alternative-threshold, CAND_2, CAND_4, or fasting-extended analyses exists. This closure task only
read, classified, and documented — it trained no model, evaluated no cohort, and touched no test
data.

## 15. Validation tests

`tests/test_mi_closure_reconciliation.py`: 29 live checks (roadmap/source existence, all-ages
resolution evidence, roadmap internal consistency at exactly 4 tracked items, per-commit
in-scope/out-of-scope file classification for B/C/D, MI-result immutability, no deferred-analysis
execution, test-set hash/touch-count integrity, evidence-grounding of the final report). **All 29
passed.**

## 16. Final status

**BOTH ITEMS CLOSED — ROADMAP RECONCILED, SCOPE BOUNDARY CONFIRMED**
