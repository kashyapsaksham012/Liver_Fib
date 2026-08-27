# Phase 1-2 -- development partition & baseline reproduction (Amendment #17)

Leakage checks: calibration N=1002; overlap with proper-train 0; overlap with locked test 0. Both must be 0 -- **PASS**.

## Subgroup calibration-cell sizes (sub-amendment #17a trigger)

| dimension | group | n | positives |
|---|---|---:|---:|
| bmi | Underweight | 16 | 1 |
| bmi | Normal | 232 | 9 |
| bmi | Overweight | 347 | 15 |
| bmi | Obese | 407 | 68 |
| age | 18-39 | 326 | 19 |
| age | 40-59 | 337 | 33 |
| age | 60+ | 339 | 41 |

BMI-Obese cell: n=407, pos=68. Age-60+ cell: n=339, pos=41.
**Sub-amendment #17a trigger (cell < 50 or positives < 15): not triggered.**


## Baseline subgroup conformal coverage on the calibration partition

(frozen threshold; should show BMI-Obese and Age-60+ below 0.90, as on the locked test)

| model | dimension | category | n | coverage (calib) | singleton rate | mean set size |
|---|---|---|---:|---:|---:|---:|
| lightgbm | age | 18-39 | 326 | 0.936 | 0.859 | 1.141 |
| lightgbm | age | 40-59 | 337 | 0.893 | 0.727 | 1.273 |
| lightgbm | age | 60+ | 339 | 0.876 | 0.487 | 1.513 |
| lightgbm | bmi | Normal | 232 | 0.991 | 0.841 | 1.159 |
| lightgbm | bmi | Obese | 407 | 0.786 | 0.575 | 1.425 |
| lightgbm | bmi | Overweight | 347 | 0.974 | 0.712 | 1.288 |
| lightgbm | bmi | Underweight | 16 | 0.938 | 0.875 | 1.125 |
| lightgbm | marginal | overall | 1002 | 0.901 | 0.689 | 1.311 |
| logistic | age | 18-39 | 326 | 0.954 | 0.782 | 1.218 |
| logistic | age | 40-59 | 337 | 0.920 | 0.570 | 1.430 |
| logistic | age | 60+ | 339 | 0.832 | 0.389 | 1.611 |
| logistic | bmi | Normal | 232 | 0.978 | 0.823 | 1.177 |
| logistic | bmi | Obese | 407 | 0.806 | 0.459 | 1.541 |
| logistic | bmi | Overweight | 347 | 0.963 | 0.533 | 1.467 |
| logistic | bmi | Underweight | 16 | 0.875 | 1.000 | 1.000 |
| logistic | marginal | overall | 1002 | 0.901 | 0.578 | 1.422 |
| mlp | age | 18-39 | 326 | 0.939 | 0.991 | 0.991 |
| mlp | age | 40-59 | 337 | 0.902 | 0.985 | 0.985 |
| mlp | age | 60+ | 339 | 0.864 | 0.953 | 0.953 |
| mlp | bmi | Normal | 232 | 0.966 | 0.996 | 0.996 |
| mlp | bmi | Obese | 407 | 0.816 | 0.946 | 0.946 |
| mlp | bmi | Overweight | 347 | 0.957 | 0.997 | 0.997 |
| mlp | bmi | Underweight | 16 | 0.938 | 1.000 | 1.000 |
| mlp | marginal | overall | 1002 | 0.901 | 0.976 | 0.976 |
| random_forest | age | 18-39 | 326 | 0.933 | 0.893 | 1.107 |
| random_forest | age | 40-59 | 337 | 0.911 | 0.789 | 1.211 |
| random_forest | age | 60+ | 339 | 0.858 | 0.596 | 1.404 |
| random_forest | bmi | Normal | 232 | 0.983 | 0.901 | 1.099 |
| random_forest | bmi | Obese | 407 | 0.791 | 0.634 | 1.366 |
| random_forest | bmi | Overweight | 347 | 0.971 | 0.801 | 1.199 |
| random_forest | bmi | Underweight | 16 | 0.938 | 0.875 | 1.125 |
| random_forest | marginal | overall | 1002 | 0.900 | 0.757 | 1.243 |
| xgboost | age | 18-39 | 326 | 0.951 | 0.850 | 1.150 |
| xgboost | age | 40-59 | 337 | 0.911 | 0.709 | 1.291 |
| xgboost | age | 60+ | 339 | 0.844 | 0.540 | 1.460 |
| xgboost | bmi | Normal | 232 | 0.978 | 0.845 | 1.155 |
| xgboost | bmi | Obese | 407 | 0.794 | 0.580 | 1.420 |
| xgboost | bmi | Overweight | 347 | 0.974 | 0.729 | 1.271 |
| xgboost | bmi | Underweight | 16 | 0.938 | 0.875 | 1.125 |
| xgboost | marginal | overall | 1002 | 0.901 | 0.698 | 1.302 |

**Under-coverage reproduced on calibration data (BMI-Obese & Age-60+ < 0.90 for the majority of models): YES.**

