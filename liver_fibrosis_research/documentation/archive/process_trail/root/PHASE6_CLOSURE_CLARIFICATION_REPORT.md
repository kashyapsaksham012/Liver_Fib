# Phase 6 Closure-Clarification Report

**Generated:** 2026-08-19, live, in a session with continuous direct git/filesystem access
throughout. This is a narrow investigation task, not a new experiment — it does not re-derive,
rerun, or alter any Phase 3–6 scientific finding.

## 1. Scope

Answer exactly one question: did the Phase 6 report's statement that the Non-Hispanic Black
subgroup's coverage deviation was "much milder than BMI/Age" reflect (A) an interpretive
connection to an already-authorized Phase 6 result, or (B) an actual multiple-imputation
analysis executed outside the frozen Phase 6 scope. No re-execution of conformal calibration,
coverage, prediction sets, or model refitting occurred in this task.

## 2. Exact Disputed Report Passage

`PHASE6_UNCERTAINTY_RESULTS_REPORT.md`, lines 210–231 (as they stood before this task's
correction), introduced whole in commit `a62ab686668d264396889908de2ac3c129dad3d4` (confirmed via
`git log -S"much milder deviation"` — the only commit ever to touch that string). Full verbatim
quotation preserved in `results/uncertainty/phase6_mi_claim_trace.md`. The specific disputed
fragment: *"coverage ranges 86.9%–88.7% across the 5 models, only 1 of 5 (XGBoost) has a CI
excluding 90%, a much milder deviation."*

## 3. Evidence Trail

| Step | Finding | Evidence |
|---|---|---|
| Report → result file | The passage cites exactly one artifact: `results/uncertainty/phase5_phase6_relationship.csv` | Direct citation in the report text |
| Result file → source code | Produced by `src/phase6_05_phase5_relationship.py`, which reads only `results/uncertainty/subgroup_coverage.csv` and `results/fairness/fairness_inference.csv` — a pure pandas merge/correlation, no data loading, no model fitting | Full script read live this pass |
| `subgroup_coverage.csv` → source code | Produced by `src/phase6_04_final_test_touch.py` (the already-established single, official Phase 6 test-set touch, Commit C `387e9fc`) | `grep` confirms this is the only script writing that filename |
| Cohort used | `load_primary_dataset()` in `src/phase3_common.py` reads only `analysis_dataset_primary.parquet` — the standard complete-case dataset, no branching, no imputed variant | Function definition read live |

## 4. Dataset/Cohort Used

The standard, single complete-case cohort used throughout Phases 1–6. No multiple-imputation
dataset exists: `find . -iname "*imput*"` across the entire repository (excluding `.git`/`.venv`)
returns **zero results**. No commit in the full git history has ever added a file matching
`*imput*` (`git log --all --diff-filter=A --name-only`, checked exhaustively, zero matches).

## 5. Model-Refit Evidence

No imputation-related refit occurred. `src/phase6_02_conformal_refit.py` (the only Phase 6 refit
script) references `proper_train_ids.csv` — the single, standard proper-training partition — and
contains no reference to "imputation" (the one incidental match for the substring "impute" is the
routine `SimpleImputer(strategy="median")` preprocessing-description string, unrelated to the
statistical multiple-imputation sensitivity analysis; distinguished explicitly in
`tests/test_phase6_closure_clarification.py` TEST 6).

## 6. Conformal-Calibration Evidence

No imputation-related calibration occurred. `src/phase6_03_conformal_calibration.py` references
only `conformal_calibration_ids.csv` — the single, standard calibration partition — with no
imputation reference of any kind.

## 7. Test-Set-Touch Audit

**Decisive evidence**: every row of `results/uncertainty/subgroup_coverage.csv` — including all
5 Non-Hispanic Black rows — carries the identical `generated` timestamp
(`2026-08-19 14:16:42`), the single, unique timestamp for the entire 75-row file. This proves the
Non-Hispanic Black coverage numbers were produced by the exact same single execution of
`phase6_04_final_test_touch.py` as every other subgroup and model in the file — there was no
second test-set access, no separate execution, no imputation-specific evaluation. Verified live
this pass via `pandas` (`cov["generated"].nunique() == 1`), not inferred.

**The locked test set was touched exactly once**, consistent with the already-established Commit
C record. No second touch occurred.

## 8. Scenario A/B/Indeterminate Determination

**SCENARIO A: INTERPRETIVE CONNECTION ONLY.**

Every angle of evidence converges: no imputed dataset exists anywhere in the repository or its
full git history; no model was refit on imputed data; no imputation-specific conformal
calibration occurred; the Non-Hispanic Black result traces to the single, standard, already-
established Phase 6 test-set touch, sharing its exact timestamp with every other subgroup result
in the file. The phrase "multiple-imputation" in the disputed passage referred back to the Phase
2 rationale (the documented complete-case exclusion disparity) for *why* this particular
subgroup's coverage result is interpretively relevant — not to any analysis actually performed
using imputed data.

## 9. Corrective Action

`PHASE6_UNCERTAINTY_RESULTS_REPORT.md` §19 was edited to remove the ambiguity: it now states
explicitly, in the passage itself, that "No multiple-imputation-based reanalysis was performed in
Phase 6," that the Non-Hispanic Black result came from "the same standard Phase 6 complete-case
cohort, the same conformal-valid refit models, and the same conformal calibration procedure"
as every other subgroup, and cites the shared single-touch timestamp as the concrete evidence.
**No underlying Phase 6 result, number, coverage value, or CI was changed** — only the prose
around an already-correct number was clarified. No amendment to the continuous authoritative
registry was required or made, since no unauthorized scope expansion occurred (Part 10 applies,
not Part 11).

## 10. Deferred Sensitivity-Analysis Status

New dedicated tracking document created: `documentation/project_roadmap/deferred_sensitivity_analyses.md`,
using the exact 4 analysis names from the authoritative `documentation/phase2/sensitivity_analysis_plan.md`
(read live this pass). All 4 — alternative 8.0kPa threshold, CAND_2 cohort eligibility,
fasting-extended predictor architecture, and complete-case vs. multiple-imputation — remain
**NOT EXECUTED**. None was falsely marked complete because related context was discussed in a
report.

## 11. Multiple-Imputation Priority

Explicitly recorded in the new roadmap document as **High priority** — directly interpretively
relevant to the Phase 5 race/ethnicity fairness findings and the Phase 6 Non-Hispanic Black
subgroup coverage result, because of the documented complete-case exclusion disparity. It
**remains a sensitivity analysis, not the primary analysis**, and has not been silently promoted
— this is stated explicitly in the roadmap document per this task's Part 14.

## 12. Confirmation That Phase 6 Headline Findings Were Not Altered

Re-verified live this pass, unchanged: `results/uncertainty/marginal_coverage_test_set.csv`
still has exactly 5 rows, Logistic's marginal coverage still 90.8201% (within 1e-4 of the
originally reported 90.82%); `results/uncertainty/subgroup_coverage.csv` still has exactly 75
rows. None of the 5 previously-established Phase 6 headline findings listed in this task's scope
section were touched, re-derived, or reinterpreted.

## 13. Remaining Limitations

- This clarification resolves the wording ambiguity but does not execute the deferred
  multiple-imputation analysis itself — that remains future work, tracked in the new roadmap
  document.
- The roadmap document is new; prior reports' prose-only tracking (Phase 5 §21-22, Phase 6 §19)
  remains as historical record and was not retroactively rewritten, only superseded going
  forward.

## 14. Final Status

**SCENARIO A CONFIRMED — REPORT CLARIFIED, NO FURTHER SCIENTIFIC ACTION NEEDED**
