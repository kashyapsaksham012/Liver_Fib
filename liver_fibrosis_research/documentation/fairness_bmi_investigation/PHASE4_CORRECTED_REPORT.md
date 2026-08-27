# Phase 4 Corrected Subgroup Calibration Report

## Final status

**NO ACCEPTABLE SUBGROUP CALIBRATION IMPROVEMENT IDENTIFIED**

## Execution

The corrected run retained the five frozen primary models, ten predictors, primary cohort and
outcome, frozen thresholds, and the existing selection gate. OOF rows were sorted by SEQN and
split deterministically into even-index fit and odd-index evaluation partitions. Global Platt
and BMI/age subgroup Platt candidates were evaluated without accessing the locked test.
Subgroup cells used documented minimum requirements and explicit fallback/status fields.

ECE was recomputed with ten equal-frequency risk deciles, not equal-width probability bins.
`ece_validation.csv` records agreement with an independent implementation and the frozen
protocol hash. The conformal comparison fits and applies a global Platt map in the
`global_platt` arm and compares it with subgroup Platt under identical 501/501
development conformal splits.

The manifest froze method selection and parameters before one locked-test confirmation pass.
No test result was used to revise a method, parameter, or selection rule. The historical Phase
4 output and prior exploratory artifact remain separate and unchanged.

## Selected methods and confirmation

- logistic: selected `global_platt`; test BMI gap change +0.000 pp versus global
- random_forest: selected `subgroup_platt_bmi_age`; test BMI gap change +0.000 pp versus global
- xgboost: selected `subgroup_platt_bmi_age`; test BMI gap change +0.000 pp versus global
- lightgbm: selected `subgroup_platt_bmi_age`; test BMI gap change +0.000 pp versus global
- mlp: selected `global_platt`; test BMI gap change +0.000 pp versus global

The transformed probabilities do not alter classification decisions because the frozen raw
prediction thresholds are retained. Therefore calibration alone cannot claim to resolve the
classification-level BMI sensitivity disparity. Metrics, supported Wilson intervals, conformal
coverage/efficiency summaries, hashes, and runtime metadata are in the corrected namespace.

No unsupported significance or equivalence claim is made.
