# BMI × Age Target Overlap — Four-Way Mitigation Disaggregation

**Generated:** 2026-08-19, live, per the Phase 7 overlap-closure task. This is a
**re-partitioning of already-frozen Phase 7 test-set output** — the raw locked test set was not
reopened, no prediction was regenerated, no conformal threshold was recomputed, and no mitigation
method was changed. Source: `src/phase7_05_bmi_age_overlap_analysis.py`, reading exclusively
`results/uncertainty/test_set_prediction_sets.csv` (frozen Phase 6 artifact) and
`results/mitigation/group_specific_thresholds.csv` (frozen Phase 7 artifact).

## 1. Overlap Prevalence (unchanged from the original Phase 7 finding, re-verified here)

883 BMI-Obese (41.1%), 741 Age-60+ (34.5%), 294 in both (13.7%), 1,330 in at least one (62.0%),
816 in neither (38.0%) — all figures reconciled exactly against the four-way group sizes below
(883 = 589 + 294; 741 = 447 + 294).

## 2. Four Subgroup Definitions (canonical, unchanged from Phase 5/7 — no redefinition)

- **BMI-Obese only**: `_bmi == "Obese"` AND `_age != "60+"`
- **Age-60+ only**: `_age == "60+"` AND `_bmi != "Obese"`
- **Intersection**: `_bmi == "Obese"` AND `_age == "60+"`
- **Neither**: neither condition

## 3. Counts

| Group | N | % of test set |
|---|---|---|
| BMI-Obese only | 589 | 27.4% |
| Age-60+ only | 447 | 20.8% |
| Intersection | 294 | 13.7% |
| Neither | 816 | 38.0% |

## 4–5. Baseline and Mitigated Coverage (full table: `results/mitigation/bmi_age_overlap_four_way_analysis.csv`)

The single most important observation in this disaggregation: **the intersection group has, by a
wide margin, the worst baseline coverage of all four groups, for every model** — 64.9%–75.1%,
versus 82.7%–95.1% for the two single-category groups and 97.6%–98.6% for "Neither." This pattern
was **not visible** in the original Phase 7 aggregate reporting, which only reported BMI-Obese
and Age-60+ as separate (overlapping) totals, never isolating the compounded population.

**After mitigation, the intersection group remains the worst-covered of the four for every
model** (75.9%–84.4%), despite receiving some of the largest absolute improvements. Mitigation
did not equalize the intersection population up to the level of the other three groups.

## 6. Model-by-Model Comparison

| Model | BMI-only Δ (pp) | Age-only Δ (pp) | Intersection Δ (pp) | Neither Δ (pp) | Pattern |
|---|---|---|---|---|---|
| Logistic | +3.06 | 0.00 (not an age target) | **+14.97** | 0.00 | A — possible overlap-associated benefit |
| Random Forest | +8.15 | +1.12 | +5.44 | 0.00 | B — consistent with shared/additive effect |
| XGBoost | +7.98 | +4.47 | **+15.65** | 0.00 | A — possible overlap-associated benefit |
| LightGBM | +8.83 | +0.67 | +4.76 | 0.00 | B — consistent with shared/additive effect |
| MLP | +7.98 | +1.79 | +7.82 | 0.00 | C — no clear evidence of an overlap-specific effect |

"Neither" shows exactly 0.00pp change for every model, confirmed programmatically — these
participants never receive a group-specific threshold under any target combination, which is the
one part of the original "non-target unaffected" expectation that holds without qualification.

## 7. Evidence For/Against Overlap-Associated Behavior

**Mixed, model-dependent — no single answer applies to all 5 models.** Logistic and XGBoost show
intersection improvements (+15.0pp, +15.6pp) clearly exceeding either single-category component
(threshold: >2pp above the larger of the two, stated explicitly as a descriptive cutoff, not a
statistical test) — classified **Pattern A: possible overlap-associated benefit**, using the
required cautious framing (not a proven interaction). Random Forest and LightGBM show
intersection improvement smaller than the largest single-category component — **Pattern B:
consistent with a shared/additive effect** (roughly what combining two separate corrections would
produce, not evidence of something specific to the overlap). MLP's intersection change is close
to its BMI-only change — **Pattern C: no clear evidence of an overlap-specific effect**.

**This does not, and cannot, establish that BMI and age causally interact to determine
mitigation effectiveness.** The Pattern-A models (Logistic, XGBoost) show a descriptive pattern
*consistent with* an overlap-associated benefit; this closure task did not run, and could not run
without a new test-set touch, a formal interaction test (e.g., testing whether the intersection's
improvement significantly exceeds the sum or maximum of the single-category improvements under a
pre-specified inferential framework). That would require new statistical machinery not already
present in the frozen artifacts.

## 8. Limitations

- No confidence interval exists in any frozen artifact at this four-way granularity — every "CI"
  field in `bmi_age_overlap_four_way_analysis.csv` is explicitly recorded as **"NOT AVAILABLE
  FROM EXISTING FROZEN ARTIFACT"** rather than fabricated.
- The 2pp descriptive threshold used to classify Patterns A/B/C is a stated, transparent
  convention for this closure pass, not a statistical significance test.
- The intersection group (N=294) is smaller than the single-category groups, so its coverage
  estimates carry inherently more sampling noise — a plausible partial explanation for some of
  the model-to-model variability in pattern classification, though this closure task cannot
  distinguish "genuine model-dependent mechanism" from "small-sample noise" without a new,
  properly-powered analysis.
- The tie-break rule (age threshold applied after, and overwriting, the BMI threshold for
  overlapping participants in models targeting both) means the intersection group's "mitigated"
  status in 4 of 5 models (all but Logistic) reflects the age-specific threshold, not a blended
  or jointly-derived one — this is unchanged from the original Phase 7 disclosure and is not a
  new finding, but is restated here because it directly shapes how the intersection numbers
  above should be read.

## 9. Explicit Statement: This Is Not a Causal Interaction Test

This four-way disaggregation is **descriptive**. It identifies where the largest, most severe,
and previously-invisible reliability failure is concentrated (the intersection population) and
characterizes how each model's mitigation behaved there relative to the two single-category
groups. It does not, and cannot, establish that BMI and age *causally interact* to produce this
pattern. The correct language for any of the Pattern-A findings is "evidence consistent with an
overlap-associated effect" or "an overlap-associated pattern" — never "BMI × age interaction
caused" the observed behavior.
