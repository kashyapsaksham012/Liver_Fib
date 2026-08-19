# Project Phase 7 (Mitigation) — Justification Determination

**Generated:** 2026-08-19, live, per Part 3 of the Project Phase 7 (= mentor Phase 13) task.
This document is **frozen** upon completion — the target set below is not expanded or
shrunk based on mitigation results observed later in this phase.

## Method

Read `results/fairness/fairness_inference.csv` and `results/uncertainty/coverage_inference.csv`
**directly** — these CSVs, not any report's prose, are the authority. A (model, subgroup)
combination is **mitigation-eligible** only if it satisfies, simultaneously:

1. Statistically significant Phase 5 sensitivity disparity after Benjamini-Hochberg FDR
   correction (`significant_after_fdr_0.05 == True` in `fairness_inference.csv`), **and**
2. Statistically significant Phase 6 coverage deviation after FDR correction
   (`significant_after_fdr_0.05 == True` in `coverage_inference.csv`), **and**
3. The Phase 6 deviation is specifically **under-coverage** (empirical coverage below the 90%
   target) — the reliability-failure pattern this dual criterion is designed to identify, not
   over-coverage (excess caution), which is a qualitatively different phenomenon that standard
   mitigation methods are not designed to address the same way.

Full machine-generated table (39 rows, every combination where either side was significant, plus
explicit checks of the two named expected-exclusion subgroups for every model):
`documentation/mitigation/phase7_justification_determination.csv`, produced by
`src/phase7_01_justification_determination.py` (read-only script — computes no new statistics,
fits no models, does not touch test-set predictions beyond reading the already-frozen inference
CSVs).

## Result: 9 (model, subgroup) combinations are ELIGIBLE

| Subgroup | Models |
|---|---|
| **BMI Obese** (vs. Normal reference) | Logistic, Random Forest, XGBoost, LightGBM, MLP — **all 5** |
| **Age 60+** (vs. 40–59 reference) | Random Forest, XGBoost, LightGBM, MLP — **4 of 5** (Logistic excluded: its Phase 5 age-60+ sensitivity disparity did not reach FDR significance, even though its Phase 6 coverage deviation did) |

This matches the two subgroups Phases 5–6 historically suggested as likely candidates — verified
directly from the CSVs, not assumed.

## A third dual-significant finding, explicitly excluded with reasoning

**Random Forest × Age 18–39** satisfies the mechanical dual-significance criterion (Phase 5
sensitivity disparity −22.7pp, FDR-adjusted p=0.016; Phase 6 coverage deviation FDR-adjusted
p<0.001) but is **excluded from the target set**: its Phase 6 coverage (93.9%) is *above* the
90% target — over-coverage, reflecting excess caution/inefficiency for that subgroup under that
one model, not the under-coverage reliability failure seen in BMI-Obese/Age-60+. It is also a
single-model-only finding, unlike the two primary targets which are broadly consistent across
4–5 of 5 models. This is a documented, evidence-based exclusion, not an oversight — it is
recorded in full in the CSV with its exact reasoning string.

## Explicit Named Exclusions (as required by this task)

### Non-Hispanic Asian

**Excluded.** Phase 5 sensitivity disparity did **not** reach FDR significance for any of the 5
models (raw p ranged from moderate to non-trivial; adjusted p 0.075–0.720 across models,
confirmed live from `fairness_inference.csv`) — consistent with the Phase 5 report's own
characterization: fragile, only 14 positive cases (limited-precision tier), not FDR-confirmed.
Fails the dual criterion on the Phase 5 side for every model. (Logistic does show a
FDR-significant Phase 6 coverage deviation for this subgroup, but that alone does not satisfy
the dual criterion.)

### BMI Underweight

**Excluded.** Phase 5 shows a mechanically FDR-significant sensitivity disparity for all 5
models — but this is driven entirely by a single positive case in the test set (N_positive=1,
insufficient-evidence precision tier), a known non-interpretable artifact already flagged in the
Phase 5 report. Independently, it also fails the dual criterion on the Phase 6 side: BMI
Underweight does not appear anywhere in `coverage_inference.csv`'s FDR-significant set for any
model. Excluded for two independent, sufficient reasons.

## Frozen Target Set

**Primary mitigation targets: BMI-Obese (all 5 models) and Age-60+ (4 of 5 models, excluding
Logistic).** This set is frozen as of this document. It will not be expanded or contracted based
on mitigation results observed in Parts 6–9 of this task.
