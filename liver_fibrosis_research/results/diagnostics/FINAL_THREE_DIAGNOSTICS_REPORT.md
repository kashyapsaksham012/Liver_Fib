# Final Three-Diagnostics Report

SECONDARY / DIAGNOSTIC / SUPPLEMENTARY. Does not replace or alter any frozen Phase 1–8 result.
Protocol: `documentation/diagnostics/THREE_DIAGNOSTICS_PROTOCOL_FREEZE.md`. Baseline reference:
`results/diagnostics/three_diagnostics_baseline_snapshot.md`.

## 1–3. Continuous BMI / Age

**BMI is compatible with a genuine continuous gradient, not a categorical-cutpoint artifact.**
The RCS-spline fit (OOF-fitted, applied to the test range) shows a monotonic pattern for every
model: sensitivity rises smoothly and coverage falls smoothly across the full observed BMI range
(e.g. XGBoost: sensitivity 0.56→0.98, coverage 0.92→0.35, from BMI≈15 to BMI≈70), with no sharp
discontinuity localized at the Obese cutoff (BMI=30). `results/diagnostics/continuous_bmi_metrics.csv`.

**Age shows a more complex, non-monotonic pattern than the categorical 60+ finding alone reveals.**
The sensitivity curve rises through middle age and **peaks around age 65**, then plateaus or
slightly declines toward the oldest ages, rather than declining monotonically with age as the
categorical "60+ is worse" framing might suggest. Coverage declines monotonically with age
throughout. `results/diagnostics/continuous_age_metrics.csv`.

**60–69 vs. 70–80 does not show a simple "older is worse" gradient.** Sensitivity in 70–80 is
similar to or, for 3 of 5 models (Logistic, Random Forest, MLP), *higher* than in 60–69; only
XGBoost and LightGBM show lower sensitivity in the oldest band. Coverage is similar or slightly
better in 70–80 than 60–69 for 4 of 5 models. `results/diagnostics/fine_age_band_metrics.csv`.

**Interpretation:** the categorical BMI finding is strengthened by the continuous analysis (genuine
gradient, not an artifact). The categorical Age-60+ finding is **not** simply explained as "risk
worsens monotonically past 60" — the mechanism is more complex, and the finer bands argue against
attributing the disparity to the oldest participants specifically. No causal claim is made.

## 4–6. Group-Specific Decision Thresholds

Giving each subgroup its own OOF-derived Youden threshold, evaluated on the locked test set:

| Model | BMI gap (Obese − Normal), global → group threshold | Age gap (40–59 − 60+), global → group threshold |
|---|---|---|
| Logistic | 47.7pp → 14.9pp | 8.6pp → 13.1pp |
| Random Forest | 31.6pp → 16.1pp | 13.2pp → 16.2pp |
| XGBoost | 31.4pp → 14.7pp | 11.2pp → 26.1pp |
| LightGBM | 27.1pp → 10.4pp | 14.1pp → 20.1pp |
| MLP | 39.0pp → 15.8pp | 14.7pp → 18.6pp |

**BMI: strong, consistent threshold contribution.** The disparity shrinks by roughly half to
two-thirds for every model. **Age: little to no threshold contribution — thresholding makes it
worse, consistently, for every model.** Giving Age-60+ its own Youden-optimal threshold trades
sensitivity for specificity within that subgroup, widening rather than narrowing the gap.

`results/diagnostics/group_specific_threshold_metrics.csv`. This is a threshold/operating-point
effect, not a calibration effect — predicted probabilities are unchanged.

## 7–9. Subgroup-Specific Recalibration

**Calibration metrics (intercept/slope/Brier) do not materially improve, and sometimes slightly
worsen, under subgroup-specific Platt recalibration** for either BMI-Obese or Age-60+, across all 5
models (`results/diagnostics/subgroup_recalibration_metrics.csv`) — Brier score changes are in the
4th decimal place; intercepts move in both directions depending on model.

**Conformal coverage improves substantially for BMI-Obese** under a fully re-derived subgroup-Platt
+ subgroup-quantile pipeline: 76.8%–82.3% (baseline) → 89.9%–91.6% (after), reaching or exceeding
the 90% target for every model — a **larger improvement than the project's existing frozen Phase 7
Mondrian mitigation achieves for BMI-Obese** (87.3%–89.4% under the existing method, per
`results/mitigation/test_set_mitigation_final.csv`).

**Conformal coverage improves more modestly for Age-60+**: 81.1%–85.6% → 86.7%–88.0%, still below
the 90% target for every model, and **comparable to or somewhat weaker than** the existing Phase 7
method for this specific subgroup (e.g. XGBoost's existing Mondrian mitigation reaches 90.0% for
Age-60+, vs. 86.8% under this subgroup-recalibration approach).
`results/diagnostics/subgroup_recalibration_conformal_metrics.csv`.

**This directly tests, and does not confirm, the assumption "better calibration ⇒ better conformal
coverage."** The coverage gain for BMI-Obese occurs without a corresponding improvement in the
calibration-in-the-large metrics — the mechanism is more likely a shift in the probability
distribution/ranking within the subgroup that interacts favorably with the conformal quantile
procedure, not a fix to miscalibration in the traditional sense.

## 10. One Mechanism or Different Mechanisms?

**Different mechanisms for BMI vs. Age, consistently across all three diagnostics:**
- **BMI-Obese**: continuous gradient (not a cutpoint artifact); disparity substantially
  threshold-driven; conformal coverage substantially improved by subgroup-specific probability
  recalibration.
- **Age-60+**: more complex, non-monotonic continuous relationship; disparity **not**
  threshold-driven (thresholding makes it worse); conformal coverage only modestly improved by
  subgroup-specific recalibration, and not clearly better than the existing method.

## 11–17. Strength of Conclusions

- **Strongly supported:** BMI's disparity is a genuine continuous phenomenon with a real,
  quantifiable threshold-driven component, and its conformal coverage problem is substantially
  more fixable via subgroup-specific probability recalibration than the currently deployed method
  achieves.
- **Strongly supported:** Age-60+'s disparity is not a simple thresholding artifact, and naive
  subgroup-specific thresholding actively worsens it.
- **Uncertain / needs further work:** whether the BMI-Obese conformal-coverage improvement found
  here generalizes beyond this specific train/calibration/test split, and whether it interacts
  differently with the true BMI×Age intersection (not evaluated in this diagnostic pass — the
  intersection was not one of the two target subgroups specified in the frozen protocol for this
  task).
- **Descriptive only:** the continuous spline curves themselves (no formal hypothesis test was
  attached to "is this curve monotonic" beyond the qualitative pattern described).
- **Narrowest defensible interpretation:** the BMI and Age-60+ subgroup reliability problems are
  not explained by, or fixable through, the same single mechanism. BMI responds well to both
  threshold and probability-recalibration corrections; Age-60+ responds poorly to both, and is
  worsened by naive threshold correction specifically. No manuscript-level novelty claim is made
  here — that requires a separate literature check, not performed as part of this execution.

## Relationship to the Existing Frozen Phase 7 Mitigation

- Thresholding did **not** explain the problem Phase 7 was addressing for Age-60+ — Phase 7 uses
  conformal-quantile (not classification-threshold) adjustment, and this diagnostic shows the
  Age-60+ disparity is not primarily a classification-threshold phenomenon either.
- Subgroup-specific probability recalibration is a **complementary, more effective alternative** to
  Phase 7's approach specifically for BMI-Obese conformal coverage — it is not shown here to be
  superior for Age-60+.
- **Phase 7 is not rewritten or replaced.** This diagnostic provides context suggesting that, if
  the project pursues further mitigation work, subgroup-specific probability recalibration (rather
  than subgroup-specific conformal thresholding alone) may be a more promising direction for
  BMI-Obese specifically — a scientific observation, not an implemented change to the primary
  pipeline.
