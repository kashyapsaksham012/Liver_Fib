# Phase 2 -> Phase 3 Handoff Verification

**Generated:** 2026-08-18 14:43:56

Every check below independently recomputes its target from the Phase 1 master dataset, bypassing the saved Phase 2 parquet, then compares against both the frozen protocol spec and the saved dataset.

| Check | Status | Detail |
|---|---|---|
| Recomputed N matches frozen spec | PASS | recomputed=7153, frozen=7153 |
| Saved dataset N matches frozen spec | PASS | saved=7153, frozen=7153 |
| Recomputed SEQN set == saved SEQN set | PASS | symmetric_diff=0 |
| Recomputed outcome-positive N matches frozen spec | PASS | recomputed=666, frozen=666 |
| Saved dataset outcome-positive N matches frozen spec | PASS | saved=666 |
| Prevalence matches frozen ~9.31% | PASS | prevalence=9.31% |
| All 10 frozen predictors present in saved dataset | PASS | missing=set() |
| No forbidden variable present as a column named identically to a predictor | PASS | structural check: forbidden/predictor lists disjoint |
| No missing values in the 10 predictors (complete-case, as frozen) | PASS | missing_cells=0 |
| No duplicate SEQN in saved dataset | PASS | dups=0 |
| Fairness-stratification demographic columns retained (RIDRETH1/RIDRETH3) | PASS | present=True |

**Overall: PASSED**
