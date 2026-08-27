# Phase 7 Mitigation Cleanup Report

## Status

**NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED**

No algorithm, model, predictor, outcome, threshold definition, or unrelated analysis was added.
The XGBoost candidates are exactly the previously authorized Phase 3 family and were fit on
OOF/development data only. The selection manifest was written before the single locked-test
confirmation.

## XGBoost

Results are in `phase7_xgb_retuning_results.csv` and `phase7_xgb_comparison.csv`. The comparison
reports sensitivity, specificity, BMI and age fairness, calibration, conformal coverage, set size,
singleton/doubleton rates, and supported Wilson intervals. No retuned candidate passed the
multi-metric gate; the original frozen XGBoost configuration is therefore not replaced.

## Existing joint artifact

`phase7_joint_mitigation_audit.csv` and `phase7_joint_mitigation_results.csv` audit the prior
`results/mitigation/joint_intersectional_mitigation.csv` without modifying it. The implementation
is a genuine joint Obese AND Age-60+ calibration slice, not sequential BMI-first/Age-second.
It is **EXPLORATORY_GENUINE_JOINT**, not primary, because its generating script, manifest, and
runtime log are NOT FOUND IN REPOSITORY. The N=138 calibration cell
contains 30 positives and 108 negatives; XGBoost and LightGBM exceed the prior ±5 pp marginal
tolerance in that artifact and remain disclosed as breaches.

Historical Phase 7, Phase 0–6, primary/master, external, and existing joint/XGB artifacts
were preserved and not merged.
