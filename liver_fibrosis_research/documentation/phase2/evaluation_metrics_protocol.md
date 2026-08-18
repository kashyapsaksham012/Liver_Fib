# Future Evaluation Metrics Protocol (Phase 2R)

**Generated:** 2026-08-18 — metrics are frozen; NONE are computed in Phase 2.

## Discrimination
- **Primary:** ROC-AUC (with 95% bootstrap CI, primary cohort test set, and separately per fairness
  subgroup).
- **Secondary:** PR-AUC (particularly informative given the primary cohort's 9.31% prevalence is
  moderately imbalanced), sensitivity, specificity, PPV, NPV, F1 — all at an operating threshold to be
  determined in Phase 3 by a pre-specified rule (e.g. Youden's J on the training/CV data only, never
  the test set) rather than chosen post-hoc to flatter results.

## Calibration
- **Primary:** Calibration intercept and slope (from a logistic recalibration regression of observed
  outcome on the model's linear predictor), and Brier score.
- **Secondary:** Calibration curve (reliability diagram, 10 risk deciles), Expected Calibration Error
  (ECE) reported as supplementary given known sensitivity to binning choices.

## Fairness (operationalized fully in `fairness_definition.md`)
- **Per-subgroup metrics:** ROC-AUC, sensitivity, specificity, false-negative rate (FNR), false-positive
  rate (FPR), calibration slope/intercept — computed for every category in every primary fairness
  dimension (`fairness_subgroup_protocol.md`), each tagged with its precision tier.
- **Disparity summaries:** absolute difference (subgroup metric − reference-group metric) as the PRIMARY
  disparity quantity (interpretable on the same scale as the metric itself); relative difference
  (ratio) reported as a SECONDARY quantity only where the reference-group rate is not near zero (ratios
  are unstable/misleading near-zero denominators, e.g. a small subgroup's near-zero FPR).
- **Reference group:** For each dimension, the largest-N category is the reference (Male for sex,
  Non-Hispanic White for race/ethnicity, 40-59 for age [chosen as the numerically central bin], Normal
  BMI for BMI) — chosen for statistical stability of the reference estimate, not for any substantive
  claim about which group is "normal."

## Uncertainty (fully specified in `uncertainty_protocol.md`)
- **Primary:** Split conformal prediction, 90% target coverage, empirical marginal coverage on the test
  set, and empirical coverage per fairness subgroup.
- **Secondary:** Average prediction-set size (or interval width for a continuous-risk formulation) as
  the efficiency companion metric to coverage.

## Governing Rule

No fairness definition, disparity metric, or tolerance threshold may be chosen or adjusted after
observing subgroup results (non-negotiable rules 6-7). The reference-group choice and disparity-metric
choice above are frozen now.
