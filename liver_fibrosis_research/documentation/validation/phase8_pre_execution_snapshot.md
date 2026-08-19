# Phase 8 (Subgroup-Holdout Generalization) — Pre-Execution Snapshot

**Generated:** 2026-08-19, live, before any Phase 8 candidate-matrix computation or model
training. Precedes `documentation/validation/phase8_holdout_candidate_decision.md` and
`documentation/validation/PHASE8_SUBGROUP_HOLDOUT_PROTOCOL_FREEZE.md`.

## Repository / Git state

| Item | Value |
|---|---|
| Git HEAD | `17bee8e587059f7f2619dccae16d3db29799e440` |
| Branch | `main` |
| Working-tree status | Clean (no uncommitted changes) |

## Phase 8 authority documents

| File | SHA-256 |
|---|---|
| `info.md` (mentor plan, repo root parent) | `528b5221f13c248c3b5a278bd03cb441691c10d761cef66ff37643ab533097ff` |
| `documentation/phase_numbering_crosswalk.md` | `407a8ab308f2fed1a41a725e552715cc403325fe605dd6bf3428416b865d8764` |
| `documentation/audit_reports/raw_file_inventory.md` (temporal-infeasibility evidence) | `3fa8c5056d2b30a90f5a2523eb596a321e4e5f85bb047542e777f73fcc9bbfab` |

**Verified:** Project Phase 8 = Mentor Phase 14 = "Generalization" (crosswalk table, row 9).
Mentor `info.md` text for Phase 14, quoted in full: *"If your NHANES data support it, perform a
temporal or subgroup validation. For example: train on one portion/cycle, test on another. Or
perform subgroup holdout experiments. Ask: Does performance drop? Which groups are most affected?
Does calibration remain stable?"* No external/independently-sourced dataset is mentioned anywhere
in this text.

**Temporal validation — re-confirmed infeasible:** `raw_file_inventory.md` records `SDDSRVYR`
(release-cycle code) as a single constant value (66.0) across all 15,560 `P_DEMO.xpt` rows — the
NHANES 2017–March 2020 "pre-pandemic" combined release. No sub-cycle or exam-date variable
distinguishing 2017–2018 from 2019–March 2020 participants exists in any of the 8 raw source
files used by this project. This is deliberate on NHANES's part (the 2019–March 2020 portion was
never fielded as an independently nationally-representative cycle). Therefore only
**subgroup-holdout validation** is feasible per the mentor-authorized design space.

## Frozen upstream artifacts (unchanged as of this snapshot)

| Artifact | SHA-256 |
|---|---|
| `documentation/phase2/fairness_subgroup_protocol.md` | `0c1cf80360b10572c003f8a27406a6499d64804f4680b5c038c1ac85aeb9634b` |
| `documentation/phase2/primary_cohort_decision.md` | `242aec1d346ee01885c110a9199a9726b3b33bcb5507ea13ef28bacd6e6314ba` |
| `documentation/phase2/model_development_protocol.md` | `10ac677088872bc8c0882da421442b3d32f1b38d946ce7adba421ea23998fe53` |
| `src/phase3_common.py` (frozen predictor/model registry) | `3b5e278933b73c4ef27dab1c24b791e325e4c0b5fbfa22b1831c55c7a62178f7` |
| `results/fairness/subgroup_discrimination_metrics.csv` (Phase 5) | `e16b44ea6f9e2a9ac5339e61a1869a68847f328c03e36633fd1b0d00ca58d1a5` |
| `results/fairness/fairness_inference.csv` (Phase 5) | `b7351bd9daf6ee5c26d7f6cf33e0859bbb952e6129c310fd0e291c133c21e132` |
| `results/uncertainty/coverage_inference.csv` (Phase 6) | `4004dda509a61c1a87dda0ad699eae4ed0a3ae10e252a2e2051bebcd75eb32e7` |
| `results/uncertainty/marginal_coverage_test_set.csv` (Phase 6) | `59f778a8465b4b356cf3fb88ba7284a8766fffc486f5746a12e4290d6b7c289c` |
| `results/mitigation/test_set_mitigation_final.csv` (Phase 7) | `e496fc8401c35b7aa27910aff8de870a973697267d5a49d4ecbde4db9c40df43` |
| `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` (targeted MI) | `5ceca9ceb30b1056685d944bdcb83c032eae434a8629453576838819f23a7d9d` |
| `data/processed/splits/test_ids.csv` (Phase 3 locked test set) | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |

Frozen model artifacts: `models/phase3/model_{logistic,random_forest,xgboost,lightgbm,mlp}_v1.joblib`
(5 files) — these are read-only references for Phase 8; Phase 8 trains its own new artifacts
under `models/phase8_holdout/`, it does not overwrite these.

## Environment

| Package | Version |
|---|---|
| Python | 3.14.3 |
| scikit-learn | 1.9.0 |
| xgboost | 3.4.1 |
| lightgbm | 4.7.0 |
| pandas | 3.0.5 |
| numpy | 2.5.2 |

## Procedural note on subgroup pre-commitment (documented here, elaborated in Part 6)

Before this Phase 8 mega-prompt was issued, the researcher was directly asked (via
`AskUserQuestion`) how to proceed on Phase 8 scope, and explicitly typed: **"Hold out
Non-Hispanic Black participants entirely and retrain."** This is a direct, explicit, prior
researcher instruction — not an inference, not a guess, and not something that could be
mistaken for output of an independent candidate-matrix process. This snapshot records that fact
before any candidate matrix is built, so that the candidate-decision document (Part 6) can
transparently classify this as PATH B (prior commitment) rather than presenting the matrix as a
blind discovery mechanism.
