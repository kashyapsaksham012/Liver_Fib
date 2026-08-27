# Corrected Phase 3 BMI-Sensitivity Mitigation

**Status:** COMPLETE  
**Final conclusion:** **NO ACCEPTABLE MITIGATION IDENTIFIED**

This corrected execution is separate from the invalid historical Phase 3 outputs and from the
authoritative prior Phase 7 Mondrian conformal work. Primary cohort, outcome, predictors,
models, preprocessing, split, and Phase 0–2 results were unchanged.

## Protocol

Development used a deterministic, independent split of the 5,007 OOF rows: sorted `SEQN`,
even positions for parameter fitting and odd positions for evaluation. Candidates were:

1. `bmi_thresholding`: BMI-specific Youden thresholds.
2. `bmi_platt_calibration`: BMI-specific Platt maps fit on the fit half, followed by a global
   transformed-probability Youden threshold.
3. `bmi_age_thresholding`: estimable BMI × Age Youden thresholds, with explicit fallback for
   cells having fewer than 10 positives or negatives.
4. `combined_bmi_platt_thresholding`: BMI-specific Platt maps followed by BMI-specific
   transformed-probability Youden thresholds.

All four candidates were evaluated against `original_frozen`. Overall metrics used the complete
development cohort, including Underweight, Normal, Overweight, and Obese participants.
Subgroup and BMI × Age metrics were retained separately. Calibration-changing candidates also
received an independent split-conformal development evaluation.

Before test access, the frozen selection gate required full-cohort sensitivity and specificity
within 5 percentage points of baseline, Brier score within +0.01, and Age-60+ versus Age-40–59
sensitivity disparity within +5 percentage points. Within that gate, absolute BMI gap was the
secondary comparison; it was not the sole acceptance criterion. Gap bootstrap intervals,
sensitivity intervals, calibration metrics, age strata, BMI × Age cells, and conformal
development results are provided in the corrected result directory.

## Selection and confirmation

The OOF gate selected the original frozen model for Logistic Regression, Random Forest, XGBoost,
and LightGBM. It selected BMI-specific Platt calibration for MLP. After the manifest was frozen,
the locked test was opened once. The selected MLP calibration reduced the test BMI sensitivity
gap from 39.03 to 34.48 percentage points, with no meaningful AUROC or Brier change and an
overall specificity increase from 0.664 to 0.676. The other four models had no selected
mitigation and therefore have original-only confirmation rows.

The full candidate comparison and locked-test metrics are in:

- `results/fairness_bmi_investigation/phase3_corrected/phase3_corrected_candidate_mitigation_results.csv`
- `results/fairness_bmi_investigation/phase3_corrected/phase3_corrected_mitigation_comparison.csv`
- `results/fairness_bmi_investigation/phase3_corrected/phase3_corrected_locked_test_confirmation.csv`
- `results/fairness_bmi_investigation/phase3_corrected/phase3_corrected_conformal_development.csv`

## Decision

No tested strategy provided a sufficiently meaningful and consistent BMI-sensitivity
improvement across the five model families while satisfying the full-cohort performance,
calibration, age, BMI × Age, and reliability requirements. The calibration candidate selected
for MLP produced only a modest locked-test gap reduction. No candidate was accepted as a
universal mitigation.

**NO ACCEPTABLE MITIGATION IDENTIFIED**

This is an empirical, non-causal conclusion. Existing Phase 7 conformal results remain
unchanged and are not reclassified as BMI-sensitivity mitigation.
