# Operational Fairness Definition (Phase 2S)

**Generated:** 2026-08-18 — frozen before any fairness result is observed.

## Operational Definition

> A model is considered **more equitable** across a given demographic dimension if no primary-feasibility
> or exploratory-tier subgroup within that dimension shows a PRIMARY disparity metric (absolute
> difference from the reference group) exceeding a predefined tolerance, AND any exceedance is
> distinguished from sampling noise using a bootstrap confidence interval on the disparity itself. A
> model is **not** automatically deemed inequitable based on a single point-estimate difference without
> confidence-interval context, and low-precision-tier subgroups (insufficient evidence / limited
> precision) are reported descriptively without a pass/fail equity judgment, since the data cannot support
> one at that N.

## Specification

- **Primary fairness metric:** Sensitivity (recall for the positive/fibrosis class) — chosen as primary
  because a missed significant-fibrosis case (false negative) is the clinically costlier error type for a
  screening-oriented risk model, consistent with the research plan's emphasis on FNR disparity as the
  headline fairness concern (`info.md` Phase 10 example table).
- **Secondary fairness metrics:** ROC-AUC, specificity, calibration slope/intercept — reported for every
  subgroup but not the primary pass/fail criterion.
- **Disparity calculation:** `subgroup_sensitivity − reference_group_sensitivity` (absolute difference,
  percentage points), with a bootstrap 95% CI (2,000 resamples, stratified within subgroup) computed
  around this difference — NOT around each group's sensitivity independently, since the CI of a
  difference is not the same as the union of two individual CIs.
- **Reference groups:** Fixed in `evaluation_metrics_protocol.md` (Male; Non-Hispanic White; 40-59; Normal
  BMI).
- **Meaningful-difference tolerance:** A PRIMARY-feasibility-tier subgroup disparity is flagged as
  clinically meaningful if the absolute sensitivity difference is **≥10 percentage points** AND its 95%
  bootstrap CI excludes zero. The 10-point threshold is chosen as a round, pre-specified, clinically
  interpretable magnitude (comparable to the ~12-point sensitivity gap the original research plan cited
  as a real, prior-literature-documented sex disparity example, `info.md` Phase 10) — **not derived from
  or adjusted to this dataset's own results**, since no fairness analysis has been run yet.
- **Statistical vs. clinical significance:** Both are reported and explicitly distinguished — a
  statistically significant (CI excludes zero) but small (<10pp) difference is reported as
  "statistically detectable, below the pre-specified clinical-meaningfulness threshold," and is not
  treated the same as a ≥10pp, CI-excludes-zero disparity.

## What This Definition Does NOT Do

It does not claim group-level statistical parity (equal predicted-positive rates) or equalized odds as
the fairness target — sensitivity-disparity (a form of equal opportunity) is the chosen primary
operationalization, consistent with the clinical-harm reasoning above. Other fairness definitions
(demographic parity, predictive parity) will be reported as secondary/exploratory context in Phase 3 but
are not the primary criterion, and this choice is not revisited after seeing results (non-negotiable rule 6).
