# Fix 1 -- model-fit alignment (Amendment #18)

Leakage pre-check: test x calibration = 0, test x proper-train = 0 (**PASS**). One locked-test touch.

## Youden thresholds derived on the calibration set (93 positives -- noisier than Phase-3)

| model         |   tau_star_calibration |   youden_J |
|:--------------|-----------------------:|-----------:|
| logistic      |                  0.555 |     0.5152 |
| random_forest |                  0.345 |     0.4936 |
| xgboost       |                  0.4   |     0.5539 |
| lightgbm      |                  0.37  |     0.5421 |
| mlp           |                  0.115 |     0.5477 |

## Comparison: does the Normal-vs-Obese gap appear in the refit fit?

| model         |   fulltrain_classification_gap_pp_(sec3.4) |   refit_conformal_sensitivity_gap_pp |   refit_classification_gap_at_tau_star_pp | refit_gap_negative_at_all_sweep_thresholds   |
|:--------------|-------------------------------------------:|-------------------------------------:|------------------------------------------:|:---------------------------------------------|
| logistic      |                                     -47.66 |                               -40.19 |                                    -41.95 | True                                         |
| random_forest |                                     -31.62 |                               -30.65 |                                    -27.53 | True                                         |
| xgboost       |                                     -31.36 |                               -32.79 |                                    -32.08 | True                                         |
| lightgbm      |                                     -27.08 |                               -23.7  |                                    -32.79 | True                                         |
| mlp           |                                     -39.03 |                                 6.49 |                                    -35.26 | False                                        |

*Note on MLP:* the refit MLP produces near-empty conformal positive sets across **all** subgroups (conformal sensitivity 0.07-0.16 for Normal, Overweight and Obese alike), so its +6.5 pp conformal-sensitivity 'gap' is an artefact of that degeneracy, not a reversal. Its classification gap at tau* (-35 pp) is in line with the other four families.

## Threshold sweep (Normal - Obese classification-sensitivity gap, pp)

| model         |    0.3 |   0.35 |    0.4 |   0.45 |    0.5 |   0.55 |    0.6 |
|:--------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| lightgbm      | -19.87 | -23.7  | -31.36 | -28.51 | -34.74 | -41.69 | -42.21 |
| logistic      | -35.65 | -38.77 | -38.05 | -40.45 | -45.97 | -43.38 | -41.04 |
| mlp           | -12.73 |  -7.27 |  -1.56 |  -1.82 |   6.04 |   2.92 |   5.06 |
| random_forest | -19.16 | -27.53 | -34.48 | -36.17 | -29.74 | -41.49 | -45.13 |
| xgboost       | -24.42 | -32.79 | -32.08 | -27.08 | -28.77 | -30.45 | -35.26 |

## Per-subgroup refit sensitivity (conformal / classification@tau*)

| model         | dimension   | category   |   n_positive |   refit_conformal_sensitivity |   refit_classification_sensitivity_at_tau_star |
|:--------------|:------------|:-----------|-------------:|------------------------------:|-----------------------------------------------:|
| logistic      | bmi         | Normal     |           22 |                     0.590909  |                                       0.409091 |
| logistic      | bmi         | Overweight |           37 |                     0.864865  |                                       0.378378 |
| logistic      | bmi         | Obese      |          140 |                     0.992857  |                                       0.828571 |
| logistic      | age         | 18-39      |           33 |                     0.818182  |                                       0.606061 |
| logistic      | age         | 40-59      |           66 |                     0.954545  |                                       0.772727 |
| logistic      | age         | 60+        |          101 |                     0.930693  |                                       0.673267 |
| random_forest | bmi         | Normal     |           22 |                     0.636364  |                                       0.681818 |
| random_forest | bmi         | Overweight |           37 |                     0.621622  |                                       0.675676 |
| random_forest | bmi         | Obese      |          140 |                     0.942857  |                                       0.957143 |
| random_forest | age         | 18-39      |           33 |                     0.757576  |                                       0.787879 |
| random_forest | age         | 40-59      |           66 |                     0.909091  |                                       0.909091 |
| random_forest | age         | 60+        |          101 |                     0.831683  |                                       0.871287 |
| xgboost       | bmi         | Normal     |           22 |                     0.636364  |                                       0.636364 |
| xgboost       | bmi         | Overweight |           37 |                     0.675676  |                                       0.594595 |
| xgboost       | bmi         | Obese      |          140 |                     0.964286  |                                       0.957143 |
| xgboost       | age         | 18-39      |           33 |                     0.787879  |                                       0.787879 |
| xgboost       | age         | 40-59      |           66 |                     0.924242  |                                       0.909091 |
| xgboost       | age         | 60+        |          101 |                     0.861386  |                                       0.831683 |
| lightgbm      | bmi         | Normal     |           22 |                     0.727273  |                                       0.636364 |
| lightgbm      | bmi         | Overweight |           37 |                     0.756757  |                                       0.648649 |
| lightgbm      | bmi         | Obese      |          140 |                     0.964286  |                                       0.964286 |
| lightgbm      | age         | 18-39      |           33 |                     0.818182  |                                       0.818182 |
| lightgbm      | age         | 40-59      |           66 |                     0.939394  |                                       0.924242 |
| lightgbm      | age         | 60+        |          101 |                     0.891089  |                                       0.841584 |
| mlp           | bmi         | Normal     |           22 |                     0.136364  |                                       0.454545 |
| mlp           | bmi         | Overweight |           37 |                     0.162162  |                                       0.432432 |
| mlp           | bmi         | Obese      |          140 |                     0.0714286 |                                       0.807143 |
| mlp           | age         | 18-39      |           33 |                     0.0606061 |                                       0.575758 |
| mlp           | age         | 40-59      |           66 |                     0.151515  |                                       0.787879 |
| mlp           | age         | 60+        |          101 |                     0.0693069 |                                       0.673267 |

## Decision (pre-registered rule, PREPUBLICATION_FIXES_PLAN.md 0.3)

- refit conformal-sensitivity gap <= -15 pp for **4/5** models
- refit classification gap (@tau*) <= -15 pp for **5/5** models
- refit gap negative at **all** sweep thresholds: 4/5 models

### VERDICT: **STRENGTHENING**

The body-mass subgroup sensitivity failure is present in **both** model fits. The manuscript can state that the fairness-audit finding and the conformal finding concern the same subgroup failure across two related fits. Methods paragraph draft:

> *The subgroup fairness audit evaluated the Phase-3 models (trained on the full training partition); the split-conformal analysis evaluated models refit on the proper-training subset, as the conformal architecture requires a disjoint calibration set. The Normal-vs-Obese sensitivity deficit was of comparable magnitude in both fits (full-train -48, -32, -31, -27, -39 pp; refit -42, -28, -32, -33, -35 pp), and the conformal coverage failure and the classification deficit therefore concern the same subgroup across two related model fits.*
