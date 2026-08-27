# Phase 4 Subgroup Calibration Reliability Investigation

**Final status: NO ACCEPTABLE SUBGROUP CALIBRATION IMPROVEMENT IDENTIFIED**

This is a new analysis, separate from `results/diagnostics/stage0/subgroup_recalibration_metrics.csv`
and the prior exploratory result reported in the master report (maximum historical coverage
change approximately 0.68 percentage points). The prior artifact was not overwritten or
relabelled.

## Protocol and leakage protection

Only the five frozen model families, primary cohort, outcome, predictors, and BMI/age definitions
were used. Existing OOF predictions were sorted by `SEQN`; even-index rows were used to fit
calibrators and odd-index rows were used for independent development evaluation. Calibration
cells required at least 20 rows, 10 positives, and 10 negatives; otherwise the global Platt
calibrator was used. No isotonic or hierarchical method was added because the available
subgroup evidence did not justify it.

The locked-test manifest was written before any test IDs, test metadata, or test predictions
were loaded. The locked test was evaluated once afterward, with no post-test modification.

## Methods evaluated

1. Existing global Platt calibration.
2. Subgroup Platt calibration using BMI cells where estimable, otherwise age cells, otherwise
   global fallback.

The subgroup method was assessed on BMI categories Underweight, Normal, Overweight, and Obese,
age groups 18–39, 40–59, and 60+, and BMI × Age cells. Sparse cells are explicitly flagged in
the calibration results. Exact metrics are in `phase4_calibration_results.csv` and
`phase4_subgroup_calibration_results.csv`.

## Findings

Independent OOF evaluation showed that subgroup calibration produced only small changes in
Brier/ECE and did not change the frozen classification decisions. Consequently, Normal-BMI
sensitivity, Obese sensitivity, the Obese-minus-Normal sensitivity gap, specificity, and age
sensitivity disparities were unchanged between global and subgroup calibration. AUROC and
PR-AUC were essentially preserved, with small numerical changes from probability transformation
reported explicitly.

The pre-specified safety rule selected global calibration for Logistic Regression, Random Forest,
XGBoost, and MLP. It selected subgroup calibration for LightGBM on development ECE, but locked
test confirmation showed no BMI fairness improvement: the gap remained 27.08 percentage points.
The selected LightGBM subgroup calibration also slightly worsened ECE and Brier relative to its
global-calibration comparator.

The independent split-conformal development comparison is in
`phase4_conformal_comparison.csv`. Subgroup probability calibration reduced conformal coverage
for Logistic Regression, Random Forest, XGBoost, and LightGBM and did not improve MLP coverage.
Prediction-set size and singleton/doubleton rates are reported. Existing Phase 7 Mondrian
conformal results remain separate and authoritative for their original under-coverage
objective.

## Interpretation and limitations

Subgroup calibration did not provide a meaningful BMI-fairness benefit: calibration changes
probabilities but the frozen decision rule preserves classification outcomes. No unacceptable
classification degradation was observed for the selected comparator, but neither was there a
reliable fairness improvement. Calibration and conformal estimates are descriptive; this run
does not provide a formal BH-FDR family for calibration-metric differences or bootstrap
confidence intervals for every calibration metric. Sensitivity Wilson intervals and explicit
sample/positive/negative counts are provided. No unsupported significance claims are made.

The result is consistent with the prior exploratory finding that subgroup recalibration produces
small changes and does not resolve the reliability problem. It is not the same analysis and its
results are not merged with the prior artifact.

**NO ACCEPTABLE SUBGROUP CALIBRATION IMPROVEMENT IDENTIFIED**
