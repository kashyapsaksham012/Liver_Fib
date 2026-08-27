# Preprocessing Leakage Audit

**Generated:** 2026-08-18 16:59:41

## Code-level verification

| Check | Status | Detail |
|---|---|---|
| Preprocessing built via sklearn Pipeline/ColumnTransformer (not manual global fit) | PASS | confirmed by source inspection |
| Preprocessing fit happens inside search.fit(X, y) where X/y are TRAINING-partition only | PASS | search.fit called on X,y derived from train_df only; test_ids never referenced in this script |
| Out-of-fold predictions use cross_val_predict (refits preprocessing per fold internally) | PASS | confirmed by source inspection |
| Final model prediction on test data uses only pipe.predict_proba (no refit) | PASS | confirmed: test-eval script loads a pre-fitted pipeline via joblib.load and calls predict_proba only |
| No scaler/imputer statistics computed from test data anywhere in the codebase | PASS | confirmed: no preprocessing-fitting code exists in the test-evaluation script |

**Overall: PASSED**

## Per-model preprocessing pipeline diagram

### logistic

```
RAW TRAINING FOLD (within 5-fold CV, hyperparameter search)
  -> fit SimpleImputer(median) on this fold's training rows only [no-op: 0 missingness by cohort construction]
  -> fit StandardScaler on this fold's training rows only
  -> transform this fold's training rows
  -> transform this fold's held-out (validation) rows using the SAME fitted imputer/scaler

FINAL MODEL (after CV-selected hyperparameters are frozen)
  -> fit imputer + scaler on the FULL training partition (N=5,007)
  -> fit logistic estimator on the FULL training partition with frozen hyperparameters
  -> [MODEL FROZEN, SAVED TO models/phase3/model_logistic_v1.joblib]
  -> LOCKED TEST SET (N=2,146) loaded for the first time in a SEPARATE script (phase3_06)
  -> transform test rows using the imputer + scaler already fitted on training data (NO refitting)
  -> predict_proba(test) -> final locked prediction
```

### random_forest

```
RAW TRAINING FOLD (within 5-fold CV, hyperparameter search)
  -> fit SimpleImputer(median) on this fold's training rows only [no-op: 0 missingness by cohort construction]
  -> transform this fold's training rows (no scaling: tree-based model)
  -> transform this fold's held-out (validation) rows using the SAME fitted imputer (no scaling)

FINAL MODEL (after CV-selected hyperparameters are frozen)
  -> fit imputer on the FULL training partition (N=5,007)
  -> fit random_forest estimator on the FULL training partition with frozen hyperparameters
  -> [MODEL FROZEN, SAVED TO models/phase3/model_random_forest_v1.joblib]
  -> LOCKED TEST SET (N=2,146) loaded for the first time in a SEPARATE script (phase3_06)
  -> transform test rows using the imputer already fitted on training data (NO refitting)
  -> predict_proba(test) -> final locked prediction
```

### xgboost

```
RAW TRAINING FOLD (within 5-fold CV, hyperparameter search)
  -> fit SimpleImputer(median) on this fold's training rows only [no-op: 0 missingness by cohort construction]
  -> transform this fold's training rows (no scaling: tree-based model)
  -> transform this fold's held-out (validation) rows using the SAME fitted imputer (no scaling)

FINAL MODEL (after CV-selected hyperparameters are frozen)
  -> fit imputer on the FULL training partition (N=5,007)
  -> fit xgboost estimator on the FULL training partition with frozen hyperparameters
  -> [MODEL FROZEN, SAVED TO models/phase3/model_xgboost_v1.joblib]
  -> LOCKED TEST SET (N=2,146) loaded for the first time in a SEPARATE script (phase3_06)
  -> transform test rows using the imputer already fitted on training data (NO refitting)
  -> predict_proba(test) -> final locked prediction
```

### lightgbm

```
RAW TRAINING FOLD (within 5-fold CV, hyperparameter search)
  -> fit SimpleImputer(median) on this fold's training rows only [no-op: 0 missingness by cohort construction]
  -> transform this fold's training rows (no scaling: tree-based model)
  -> transform this fold's held-out (validation) rows using the SAME fitted imputer (no scaling)

FINAL MODEL (after CV-selected hyperparameters are frozen)
  -> fit imputer on the FULL training partition (N=5,007)
  -> fit lightgbm estimator on the FULL training partition with frozen hyperparameters
  -> [MODEL FROZEN, SAVED TO models/phase3/model_lightgbm_v1.joblib]
  -> LOCKED TEST SET (N=2,146) loaded for the first time in a SEPARATE script (phase3_06)
  -> transform test rows using the imputer already fitted on training data (NO refitting)
  -> predict_proba(test) -> final locked prediction
```

### mlp

```
RAW TRAINING FOLD (within 5-fold CV, hyperparameter search)
  -> fit SimpleImputer(median) on this fold's training rows only [no-op: 0 missingness by cohort construction]
  -> fit StandardScaler on this fold's training rows only
  -> transform this fold's training rows
  -> transform this fold's held-out (validation) rows using the SAME fitted imputer/scaler

FINAL MODEL (after CV-selected hyperparameters are frozen)
  -> fit imputer + scaler on the FULL training partition (N=5,007)
  -> fit mlp estimator on the FULL training partition with frozen hyperparameters
  -> [MODEL FROZEN, SAVED TO models/phase3/model_mlp_v1.joblib]
  -> LOCKED TEST SET (N=2,146) loaded for the first time in a SEPARATE script (phase3_06)
  -> transform test rows using the imputer + scaler already fitted on training data (NO refitting)
  -> predict_proba(test) -> final locked prediction
```

