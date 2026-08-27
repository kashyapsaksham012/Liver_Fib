# Reliability Extension — Pre-Execution Snapshot

**Generated:** live, before any new analysis code is written or executed.

## Repository state

| Item | Value |
|---|---|
| Git HEAD | `ad4fb230706536edb66bb663a4e2620bcf5ba726` |
| Branch | `main` |
| Working tree | Clean except pre-existing, unrelated untracked literature-review artifacts (`MASTER_RESEARCH_ARCHIVE.md`, `NOVELTY_VERIFICATION_FULL_TEXT_AUDIT.{md,pdf}`) from an earlier, separate task — not touched by this task |
| Date/time | 2026-08-21 12:46 IST |

## Source-of-truth files (exact paths, verified to exist, hashed)

| Purpose | File | SHA-256 |
|---|---|---|
| **A. Fairness disparity values** | `results/fairness/fairness_inference.csv` | `b7351bd9daf6ee5c26d7f6cf33e0859bbb952e6129c310fd0e291c133c21e132` |
| **B. Coverage values** | `results/uncertainty/coverage_inference.csv` | `4004dda509a61c1a87dda0ad699eae4ed0a3ae10e252a2e2051bebcd75eb32e7` |
| **C. Model predicted probabilities (recalibrated, primary DCA source — see Part 6.1)** | `results/calibration/test_set_recalibrated_predictions.csv` | `a945825b6d927c9e7f0194e8b27197ec7aeee959c034ec7a7511ee8e5d250dda` |
| C (raw, reference only, not used as primary) | `results/predictions/test_predictions_logistic.csv` (+ 4 sibling model files) | `87fa5df55f55ae749e70205eaab0fb6a57b0650e25fa901a824b15ccd1a8cd45` |
| **D. Subgroup labels** | `data/processed/analysis_dataset_primary.parquet` (`bmi_group_final`, `age_group_final`, `RIDRETH3`, `RIAGENDR` columns, joined by SEQN) | `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938` |
| **E. Locked test-set ID list (integrity reference, not modified)** | `data/processed/splits/test_ids.csv` | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |

## Frozen-status verification (Part 2)

Git history checked for each source file (`git log --follow`), confirming each has been touched by **exactly one** commit, self-described as a single, final test-set touch — no later correction, regeneration, or supersession exists:

| File | Sole commit | Subject |
|---|---|---|
| `fairness_inference.csv` | `63d41b7` | "Phase 5 Fairness: FIRST AND ONLY FAIRNESS TEST-SET TOUCH (Commit B)" |
| `coverage_inference.csv` | `387e9fc` | "Phase 6 Uncertainty: FIRST AND ONLY FINAL TEST-SET TOUCH (Commit C)" |
| `test_set_recalibrated_predictions.csv` | `204d008` | "Phase 4 Calibration: FIRST AND ONLY TEST-SET TOUCH (Commit B)" |

No later document, commit, or amendment supersedes any of these three files. They are confirmed authoritative and final — no version-selection ambiguity exists.

## Explicit non-goals (restated, binding for this task)

No model retraining, no hyperparameter tuning, no new model family, no AUC/sensitivity/specificity optimization, no cohort/outcome/predictor-set change, no change to the original fairness definitions or conformal method, no new predictions generated, no modification of locked test-set predictions, no external dataset, no analysis chosen after seeing its result, no subgroup removed or added after seeing a result, no statistical test altered because its result is unfavorable. Exactly two new analyses are authorized: (A) co-occurrence correlation between fairness-disparity magnitude and coverage-deficit magnitude; (B) Decision Curve Analysis. No third analysis is created.
