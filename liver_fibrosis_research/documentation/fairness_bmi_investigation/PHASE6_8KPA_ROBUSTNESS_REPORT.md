# Phase 6 Full 8.0-kPa Robustness Report

## Scope
New outcome: valid VCTE (`LUAXSTAT==1`) and `LUXSMED>=8.0 kPa`. The same quality-valid
adult broad-lab CAND_1 cohort, ten frozen predictors, five frozen model families, inherited
hyperparameters, development partitions, OOF Platt calibration, and split-conformal method
were used. No external or out-of-sample validation was performed, and no mitigation was introduced.

## Cohort and label verification
The cohort contains **N=7153**, with 8.2-kPa positives **666 (9.3108%)** and
8.0-kPa positives **715 (9.9958%)**. Labels differ for **49** participants.
The independently derived 8.0 label agrees with the pre-existing sensitivity column; that
column was not used as the outcome source.

## Leakage and test protection
All configurations, OOF Youden thresholds, OOF Platt parameters, and conformal thresholds were
written to the selection manifest before reading any test IDs, metadata, outcomes, or predictions.
The locked test set was touched exactly once afterward; it was not used for tuning or selection.

## Results
See `phase6_8kpa_vs_82_comparison.csv` for the exact columns
`Metric, Model, 8.2-kPa result, 8.0-kPa result, Difference, 95% CI, Interpretation`.
BMI, age, BMI×Age intersectional cells, calibration, and conformal coverage are reported in
the dedicated result tables. Wilson/bootstrap methods are used only for the corresponding
supported quantities; no equivalence claim is made.

## Lineage limitations
Frozen 8.2 protocol commit: **NOT FOUND IN REPOSITORY**.
Frozen 8.2 model-artifact manifest: **NOT FOUND IN REPOSITORY**.
Complete available input/output hashes and runtime metadata are in `phase6_8kpa_lineage.json`.

## Final conclusion
SOME MAJOR FINDINGS ARE THRESHOLD-SENSITIVE
