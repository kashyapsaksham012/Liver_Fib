# Multiple-Imputation Sensitivity — Pre-Execution Snapshot

**Timestamp (live):** 2026-08-19 22:05:34 +0530

## Phase-numbering guardrail

`info.md` and `documentation/phase_numbering_crosswalk.md` read live in full this pass.
**Project Phase 8 = Mentor Phase 14 = "Generalization"** (temporal/subgroup validation).
This task is explicitly framed as pre-Phase-8 work (a targeted sensitivity analysis), not Phase 8
itself — no divergence to reconcile; Phase 8 work is not executed here.

## Git state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `e2f59ebf5dc30c91840691acd5b89259b874acf8` |
| Working tree | Clean (0 uncommitted, 0 untracked) |
| Upstream | `origin/main`, up to date |

## Artifact hashes (SHA-256, live-computed)

| File | SHA-256 |
|---|---|
| `documentation/phase2/missing_data_protocol.md` | `8bdd17a9a18c18f8a1202c53f6aa33115e860fcda0e7c289824beee600ac8b49` |
| `documentation/phase2/sensitivity_analysis_plan.md` | `0110c749578212022305ba1abcbb279c3256d35f269ad2e0ddff08709984606b` |
| `data/processed/analysis_dataset_primary.parquet` (primary cohort, complete-case) | `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938` |
| `data/processed/splits/test_ids.csv` (frozen test set — will NOT be touched by this analysis) | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| `results/fairness/fairness_inference.csv` (Phase 5, read-only reference) | `b7351bd9daf6ee5c26d7f6cf33e0859bbb952e6129c310fd0e291c133c21e132` |
| `results/uncertainty/coverage_inference.csv` (Phase 6, read-only reference) | `4004dda509a61c1a87dda0ad699eae4ed0a3ae10e252a2e2051bebcd75eb32e7` |
| `PHASE7_MITIGATION_RESULTS_REPORT.md` (read-only reference) | `485a9b08c1378db50177b80802bf0fde7b5e8da26e3e4ae1ca4eb7a9da5d7583` |
| `documentation/project_roadmap/deferred_sensitivity_analyses.md` (to be updated this pass) | `c66e0423aa6ba18c71609d6a5a69a4c53603c154a0d1d086cdc66ab0c02b92c5` |

## Environment

Python 3.14.3, scikit-learn 1.9.0 (includes `IterativeImputer`, confirmed available this pass) —
unchanged from all prior phases; matches `requirements-phase3-lock.txt`.

## Selection-disparity evidence that motivated MI (re-verified live, not restated from memory)

Recomputed directly from `_cohorts.py`'s `COHORT_3B_ADULT_OF_QUALITY_VALID` this pass: full pool
N=7,768; complete-case N=7,153; excluded N=615 — **exact match** to `missing_data_protocol.md`'s
reported figures. Excluded group is 41.3% Non-Hispanic Black vs. 25.0% in the retained
complete-case cohort — confirmed exactly. Missingness is concentrated in BMI (69 missing) and the
7 broad-lab predictors (305–554 missing each); `RIDAGEYR`/`RIAGENDR` are fully observed in this
pool (demographic completeness is a cohort-eligibility requirement, not something MI needs to
address). Full pool outcome-positive N=728 (vs. 666 in complete-case; the 615 excluded contribute
62 additional positive cases, ~10.08% prevalence within that group, matching the frozen
document's reported 10.08%).

## Important premise correction (established via direct data inspection, not assumed)

This task's framing refers to "the previously observed Non-Hispanic Black fairness and
uncertainty findings." **Live-checked against `results/fairness/fairness_inference.csv` and
`results/uncertainty/coverage_inference.csv`: Non-Hispanic Black shows no FDR-significant Phase 5
sensitivity disparity and no FDR-significant Phase 6 coverage deviation for any of the 5
models** (all `significant_after_fdr_0.05 == False`; none meet the "meaningful disparity"
criterion either). There is no existing significant Black-subgroup fairness or uncertainty
finding to "reassess." The actual, documented Non-Hispanic Black finding in this project is the
**Phase 2 selection/exclusion disparity** (a cohort-composition finding, not a model-performance
finding). This distinction is preserved throughout this analysis: the real scientific question
this task answers is **whether complete-case exclusion could be masking a Black-subgroup
disparity that the current complete-case analysis is underpowered or structurally unable to
detect, precisely because it excludes the participants most likely to carry that signal** — not
whether an existing finding changes. This correction is stated once, prominently, and carried
through to the final report and Phase 8 handoff rather than silently accepted from the prompt.
