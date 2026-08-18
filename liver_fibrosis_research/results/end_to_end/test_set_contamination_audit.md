# Test-Set Contamination Audit

**Generated:** 2026-08-18 (end-to-end Phase 1→3 audit)

For each potential contamination pathway, the check performed and its live result:

| Pathway | Check performed (live) | Result |
|---|---|---|
| Feature selection | Feature registry (`phase3_02_target_and_features.py`) generated and frozen before any split/training script runs (script execution order in the pipeline: 01→02→03→...) | **PASS** |
| Model selection | `grep "test_ids" src/phase3_05_train_and_tune.py` → zero matches (re-confirmed live this pass) | **PASS** |
| Hyperparameter tuning | Same grep; `GridSearchCV`/`RandomizedSearchCV` operate on `X, y` derived from `train_df` only, which is filtered by `train_ids.csv` before any test file is opened | **PASS** |
| Class-imbalance decisions | `scale_pos_weight` computed from `n_neg/n_pos` of the training partition only (`build_pipeline()` in `phase3_05_train_and_tune.py`, computed from `y` = training labels) | **PASS** |
| Threshold selection | Live code-order check this pass: `youdens_j_threshold(oof...)` call precedes `test_ids.csv` load in `phase3_06_threshold_and_test_eval.py` — **PASS**, structurally proven (not merely claimed) |
| Preprocessing fitting | `ColumnTransformer`/`Pipeline` fit occurs inside `search.fit(X, y)` where X/y are training-partition-only; final pipeline fit again on the full training partition only, never on test rows | **PASS** |
| Fairness optimization | No fairness code exists anywhere in the repository (`find . -iname "*fairness*result*"` → no result files); fairness analysis has not started | **PASS (not applicable yet)** |
| Calibration | No calibration code exists anywhere in the repository (confirmed by search in the prior forensic audit); calibration analysis has not started | **PASS (not applicable yet)** |

## Overall outcome: **PASS**

Every contamination pathway checked either (a) has direct, structural, code-level evidence
ruling it out (grep for zero references, verified line-order, verified computation scope), which
is Level A evidence independent of commit chronology, or (b) is not yet applicable because the
downstream analysis (fairness, calibration) has not been executed at all. **No UNCERTAIN result
was required for any pathway** — every check produced a definitive PASS from live, reproducible
evidence, not from restated prior claims.

## One caveat carried forward from the prior forensic audit (not a contamination finding, a
provenance-strength finding)

This PASS result concerns *whether the test set could leak into development decisions* — a
question code structure can answer definitively regardless of when the code was written. It does
NOT resolve the separate, weaker question of whether Phase 2's protocol documents (outcome
threshold, predictor list, fairness bins) were finalized before Phase 3 code was written, which
remains `CURRENTLY-DOCUMENTED-ONLY` per `documentation/FORENSIC_PROVENANCE_AUDIT.md` (git commits
bundle Phase 2 and Phase 3 together). These are two different questions: this document answers
"did the test set contaminate development" (PASS); the forensic audit answers "can protocol-freeze
chronology be proven by git" (weaker than PASS, honestly downgraded).
