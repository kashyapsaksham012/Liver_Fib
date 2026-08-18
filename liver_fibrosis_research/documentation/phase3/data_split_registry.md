# Data Split Registry

**Generated:** 2026-08-18 14:45:56

## Reconciliation: 'validation' in this study = out-of-fold CV predictions, not a separate partition

The frozen `model_development_protocol.md` specifies 70/30 train/test with 5-fold stratified CV **within training** for tuning/selection -- no separate fixed validation partition exists. `validation_ids.csv` is therefore an exact copy of `train_ids.csv` (every training participant serves as out-of-fold validation data across the 5 CV folds). This is a documented reconciliation of the generic 3-file deliverable template against the specific frozen protocol, not a deviation.

## Split parameters

- Method: `sklearn.model_selection.train_test_split`, stratified on `outcome_primary_8.2kPa`
- Train fraction: 0.7
- Random seed: 42
- CV folds (within training): 5, `StratifiedKFold(shuffle=True, random_state=42)`

## Counts

- Train (= validation pool): N=5007, outcome-positive=466 (9.31%)
- Test (LOCKED): N=2146, outcome-positive=200 (9.32%)

## Integrity checks

| check                                                   | status   | detail                                        |
|:--------------------------------------------------------|:---------|:----------------------------------------------|
| train ∩ test = empty                                    | PASS     | overlap=0                                     |
| union(train, test) = full modeling cohort               | PASS     | union_size=7153, cohort_size=7153             |
| Every participant appears exactly once                  | PASS     | 5007+2146=7153 vs 7153                        |
| No participant-level duplication across partitions      | PASS     | same as check 1                               |
| Target distribution documented per partition            | PASS     | train_prevalence=9.31%, test_prevalence=9.32% |
| Subgroup distributions documented (sex, race/ethnicity) | PASS     | train_pct_female=50.4, test_pct_female=51.2   |
