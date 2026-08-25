# Three-Diagnostics Baseline Snapshot



Generated: 2026-08-25T10:59:16.339641+00:00



Reference only. Reconstructed programmatically from frozen result files (not manually transcribed). Does not modify any underlying frozen result.



## Discrimination + confusion matrix (results/tables/phase3_overall_discrimination.csv)

| model_name    |   test_n |   threshold |   roc_auc |   sensitivity |   specificity |    ppv |    npv |   tp |   fp |   tn |   fn |
|:--------------|---------:|------------:|----------:|--------------:|--------------:|-------:|-------:|-----:|-----:|-----:|-----:|
| logistic      |     2146 |      0.5173 |    0.8334 |         0.75  |        0.7621 | 0.2447 | 0.9674 |  150 |  463 | 1483 |   50 |
| random_forest |     2146 |      0.4499 |    0.8343 |         0.79  |        0.7359 | 0.2351 | 0.9715 |  158 |  514 | 1432 |   42 |
| xgboost       |     2146 |      0.4108 |    0.8429 |         0.845 |        0.6773 | 0.212  | 0.977  |  169 |  628 | 1318 |   31 |
| lightgbm      |     2146 |      0.4988 |    0.8394 |         0.795 |        0.7492 | 0.2457 | 0.9726 |  159 |  488 | 1458 |   41 |
| mlp           |     2146 |      0.1065 |    0.8229 |         0.815 |        0.6644 | 0.1998 | 0.9722 |  163 |  653 | 1293 |   37 |



## Recalibrated test-set calibration (results/calibration/test_set_calibration_final.csv, variant=recalibrated)

| model         |    n |   calibration_intercept |   calibration_slope |   brier_score |      ece |
|:--------------|-----:|------------------------:|--------------------:|--------------:|---------:|
| logistic      | 2146 |               -0.153655 |            0.939466 |      0.070538 | 0.01718  |
| random_forest | 2146 |                0.023778 |            1.06943  |      0.070856 | 0.011272 |
| xgboost       | 2146 |                0.124137 |            1.11802  |      0.069405 | 0.015195 |
| lightgbm      | 2146 |                0.141848 |            1.13326  |      0.069587 | 0.014283 |
| mlp           | 2146 |               -0.11893  |            1.12105  |      0.071485 | 0.026373 |



## Fairness disparity, BMI-Obese and Age-60+ only (results/fairness/fairness_inference.csv)

| model         | dimension   | category   |   n |   n_positive |   subgroup_sensitivity |   reference_sensitivity |   absolute_disparity_pp |   ci_lower_pp |   ci_upper_pp | significant_after_fdr_0.05   |
|:--------------|:------------|:-----------|----:|-------------:|-----------------------:|------------------------:|------------------------:|--------------:|--------------:|:-----------------------------|
| logistic      | age         | 60+        | nan |          101 |               0.732673 |                0.818182 |                 -8.5509 |      -21.0158 |        4.2124 | False                        |
| logistic      | bmi         | Obese      | nan |          140 |               0.885714 |                0.409091 |                 47.6623 |       25.6847 |       69.5017 | True                         |
| random_forest | age         | 60+        | nan |          101 |               0.762376 |                0.893939 |                -13.1563 |      -23.8882 |       -1.954  | True                         |
| random_forest | bmi         | Obese      | nan |          140 |               0.907143 |                0.590909 |                 31.6234 |       10.2285 |       53.357  | True                         |
| xgboost       | age         | 60+        | nan |          101 |               0.811881 |                0.924242 |                -11.2361 |      -20.8628 |       -1.8252 | True                         |
| xgboost       | bmi         | Obese      | nan |          140 |               0.95     |                0.636364 |                 31.3636 |       11.1043 |       53.5666 | True                         |
| lightgbm      | age         | 60+        | nan |          101 |               0.752475 |                0.893939 |                -14.1464 |      -24.9452 |       -2.2097 | True                         |
| lightgbm      | bmi         | Obese      | nan |          140 |               0.907143 |                0.636364 |                 27.0779 |        6.7666 |       48.5048 | True                         |
| mlp           | age         | 60+        | nan |          101 |               0.762376 |                0.909091 |                -14.6715 |      -25.5505 |       -4.0274 | True                         |
| mlp           | bmi         | Obese      | nan |          140 |               0.935714 |                0.545455 |                 39.026  |       18.6747 |       60.6754 | True                         |



## Marginal conformal coverage (results/uncertainty/marginal_coverage_test_set.csv)

| model         |    n |   target_coverage |   empirical_coverage |   ci_lower |   ci_upper |   mean_set_size |   singleton_rate |
|:--------------|-----:|------------------:|---------------------:|-----------:|-----------:|----------------:|-----------------:|
| logistic      | 2146 |               0.9 |             0.908201 |   0.895245 |   0.919699 |        1.43197  |         0.568034 |
| random_forest | 2146 |               0.9 |             0.896086 |   0.88246  |   0.908296 |        1.23159  |         0.768406 |
| xgboost       | 2146 |               0.9 |             0.881174 |   0.866798 |   0.894188 |        1.27074  |         0.729264 |
| lightgbm      | 2146 |               0.9 |             0.896086 |   0.88246  |   0.908296 |        1.31221  |         0.687791 |
| mlp           | 2146 |               0.9 |             0.891892 |   0.878047 |   0.904336 |        0.968779 |         0.968779 |



## Subgroup conformal coverage, BMI-Obese and Age-60+ only (results/uncertainty/subgroup_coverage.csv)

| model         | dimension   | category   |   n |   n_positive |   empirical_coverage |   ci_lower |   ci_upper |   mean_set_size |   singleton_rate | significant_after_fdr_0.05   |
|:--------------|:------------|:-----------|----:|-------------:|---------------------:|-----------:|-----------:|----------------:|-----------------:|:-----------------------------|
| logistic      | age         | 60+        | 741 |          101 |             0.848853 |   0.821267 |   0.87284  |        1.60864  |         0.391363 | True                         |
| logistic      | bmi         | Obese      | 883 |          140 |             0.82333  |   0.796789 |   0.847069 |        1.56172  |         0.438279 | True                         |
| random_forest | age         | 60+        | 741 |          101 |             0.855601 |   0.828457 |   0.879076 |        1.38327  |         0.616734 | True                         |
| random_forest | bmi         | Obese      | 883 |          140 |             0.801812 |   0.774236 |   0.826773 |        1.33182  |         0.668177 | True                         |
| xgboost       | age         | 60+        | 741 |          101 |             0.811066 |   0.781304 |   0.83762  |        1.40756  |         0.592443 | True                         |
| xgboost       | bmi         | Obese      | 883 |          140 |             0.767837 |   0.738865 |   0.794489 |        1.35674  |         0.643262 | True                         |
| lightgbm      | age         | 60+        | 741 |          101 |             0.847503 |   0.819831 |   0.871591 |        1.48043  |         0.519568 | True                         |
| lightgbm      | bmi         | Obese      | 883 |          140 |             0.791619 |   0.763596 |   0.817117 |        1.4145   |         0.585504 | True                         |
| mlp           | age         | 60+        | 741 |          101 |             0.838057 |   0.809799 |   0.862827 |        0.950067 |         0.950067 | True                         |
| mlp           | bmi         | Obese      | 883 |          140 |             0.808607 |   0.781344 |   0.833196 |        0.935447 |         0.935447 | True                         |



## True intersectional (Obese AND 60+) conformal coverage, computed this session (results/uncertainty/intersectional_coverage_ci.csv)

| model         | stage           |   n |   n_covered |   coverage |   ci_lower |   ci_upper | ci_method                                                                                                      |
|:--------------|:----------------|----:|------------:|-----------:|-----------:|-----------:|:---------------------------------------------------------------------------------------------------------------|
| logistic      | baseline        | 294 |         204 |   0.693878 |   0.638976 |   0.743778 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| logistic      | post_mitigation | 294 |         248 |   0.843537 |   0.797611 |   0.880602 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| random_forest | baseline        | 294 |         221 |   0.751701 |   0.699283 |   0.797626 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| random_forest | post_mitigation | 294 |         237 |   0.806122 |   0.757104 |   0.847245 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| xgboost       | baseline        | 294 |         191 |   0.64966  |   0.593515 |   0.701945 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| xgboost       | post_mitigation | 294 |         237 |   0.806122 |   0.757104 |   0.847245 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| lightgbm      | baseline        | 294 |         209 |   0.710884 |   0.656606 |   0.759722 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| lightgbm      | post_mitigation | 294 |         223 |   0.758503 |   0.706449 |   0.80389  | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| mlp           | baseline        | 294 |         217 |   0.738095 |   0.684998 |   0.785051 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |
| mlp           | post_mitigation | 294 |         240 |   0.816327 |   0.768082 |   0.856411 | Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py wilson_ci(), reused for consistency) |



## Global (existing) Youden thresholds, source: results/tables/phase3_threshold_selection.csv

| model_name    | method                                            |   threshold | source                                         |
|:--------------|:--------------------------------------------------|------------:|:-----------------------------------------------|
| logistic      | Youden's J on out-of-fold training CV predictions |      0.5173 | training partition only, test set not accessed |
| random_forest | Youden's J on out-of-fold training CV predictions |      0.4499 | training partition only, test set not accessed |
| xgboost       | Youden's J on out-of-fold training CV predictions |      0.4108 | training partition only, test set not accessed |
| lightgbm      | Youden's J on out-of-fold training CV predictions |      0.4988 | training partition only, test set not accessed |
| mlp           | Youden's J on out-of-fold training CV predictions |      0.1065 | training partition only, test set not accessed |
