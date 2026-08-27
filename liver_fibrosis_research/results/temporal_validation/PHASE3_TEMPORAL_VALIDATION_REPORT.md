# Phase 3 temporal validation report

**Scope:** frozen-model temporal evaluation only; no model updating, threshold selection, recalibration, conformal fitting, quantile recomputation, or N0 selection occurred.

## Cohort

The temporal cohort contains 4,910 participants, 563 outcomes (11.4664%) and 4,347 non-outcomes. All required input SEQNs matched exactly.

## Interpretation

Results are reported in the accompanying tables. They quantify performance change on this later NHANES cohort under the frozen protocol; they do not by themselves establish clinical readiness or broader external generalization. Any adverse discrimination, calibration, fairness, or coverage changes are retained without mitigation or model modification.

## Reproducibility

Discrimination CIs use 2,000 percentile bootstrap resamples. Fairness sensitivity-gap CIs use the original 2,000 resamples and BH-FDR within each model × original subgroup dimension; BMI × Age cells remain exploratory, as in the original protocol. Coverage CIs are 95% Wilson intervals. Calibration uses raw frozen Phase 3 probabilities and frozen 10-quantile-bin ECE. Conformal uses Phase 6 refit probabilities and frozen thresholds. M4b applies the frozen N0=0 group/joint quantiles.
