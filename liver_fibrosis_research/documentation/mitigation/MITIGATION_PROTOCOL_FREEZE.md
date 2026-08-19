# Mitigation Protocol Freeze — Project Phase 7 (= mentor Phase 13)

**Generated:** 2026-08-19. **Status: FROZEN, PROSPECTIVELY, BEFORE ANY MITIGATION EXECUTION.**
**No mitigation results existed and no final test-set information was inspected before this
protocol was frozen.** This document is committed in a standalone git commit, separate from any
implementation code, mirroring the discipline already established for
`CALIBRATION_PROTOCOL_FREEZE.md` (Phase 4).

## 1. Formal Mitigation Justification

Per `documentation/mitigation/phase7_justification_determination.md` (frozen, this task's
Part 3), computed directly from `results/fairness/fairness_inference.csv` and
`results/uncertainty/coverage_inference.csv`: **9 (model, subgroup) combinations satisfy the
frozen dual criterion** (FDR-significant Phase 5 sensitivity disparity AND FDR-significant
Phase 6 under-coverage) — BMI-Obese (all 5 models) and Age-60+ (4 of 5 models, excluding
Logistic). Explicitly excluded, with documented reasons: Random Forest × Age-18-39 (dual-
significant but over-coverage, a different phenomenon), Non-Hispanic Asian (Phase 5
non-significant, fragile), BMI-Underweight (single-positive-case artifact).

**Important interpretive nuance, stated explicitly here to prevent misreading**: the Phase 5
disparity for BMI is computed as *Obese minus Normal* — Obese's sensitivity is numerically
*higher* than Normal's (Normal is the group with the lower absolute sensitivity). The mitigation
target here is **BMI-Obese specifically because that is the subgroup whose conformal coverage
reliability failed in Phase 6** (76.8%–82.3%, under the 90% target), not because Obese has lower
sensitivity in absolute terms. This protocol targets the Phase 6 reliability failure directly;
it does not claim to address Normal-BMI's comparatively lower sensitivity, which is a distinct
finding not targeted by this mitigation.

## 2. Targeted Subgroup/Model Combinations (Frozen Target Set)

| Subgroup | Dimension | Models |
|---|---|---|
| Obese | bmi | logistic, random_forest, xgboost, lightgbm, mlp |
| 60+ | age | random_forest, xgboost, lightgbm, mlp |

This set is frozen and will not be expanded or contracted after seeing mitigation results.

## 3. Method Selected: Group-Wise (Mondrian) Conformal Calibration

From the three legitimate candidate families named in the original project plan (`info.md`
mentor Phase 13: group-wise calibration, threshold adjustment, reweighting), **group-wise
calibration** is selected as the primary and only method for this pass, adapted specifically to
the conformal-threshold context (the natural analog, for this thesis's Uncertainty pillar, of
"calibrate predicted probabilities separately by group").

**Rationale for this choice over the alternatives:**
- The justified targets were identified via a Phase 6 *coverage/reliability* failure, not
  primarily a probability-miscalibration failure (Phase 4 already showed raw probabilities are
  systematically shifted for 4/5 models, addressed by Amendment #8's global recalibration — this
  is a separate, already-closed matter). The natural, most directly on-target fix for a
  subgroup-specific conformal coverage failure is **Mondrian (group-conditional) split conformal
  prediction** — computing the conformal threshold separately within each target subgroup's
  calibration data, rather than one global threshold pooled across all subgroups.
- **Threshold adjustment** (classification decision threshold) targets Phase 5 sensitivity
  disparity more directly, but was not selected as the primary method this pass — it remains a
  viable alternate method for a future pass, not pursued here to keep this pass's scope
  well-defined and avoid conflating the two different downstream effects (classification
  threshold changes affect sensitivity/specificity; conformal threshold changes affect coverage/
  set size) within one intervention.
- **Reweighting** requires full model retraining, a substantially heavier intervention not
  justified by the specific, narrowly-scoped nature of the Phase 6 finding (a threshold-
  construction issue, not a training-data-representation issue per se).
- No new mitigation technique is invented — group-wise conformal calibration is a well-
  established, standard extension of split conformal prediction (Mondrian conformal prediction,
  Vovk et al.), not a novel method chosen to flatter results.

## 4. Data-Source Plan

Uses **only** the existing, already-frozen `conformal_calibration_ids.csv` (N=1,002, from Phase
6 Commit B), filtered to each target subgroup's participants. **No new data collection, no new
participants, no test-set involvement.** For each (model, target subgroup) pair, the subgroup-
specific calibration slice is a strict subset of the same 1,002-person calibration set already
used for the Phase 6 global threshold — never overlapping with `proper_train_ids.csv` or
`test_ids.csv` (this disjointness was already verified in Phase 6 and does not change here, since
no new partition is created).

## 5. Training/Calibration Separation

**No model refitting occurs in this mitigation.** The Phase 6 conformal-valid refit models
(`models/phase6_conformal_refit/*.joblib`) are reused unchanged — their predicted probabilities
are not touched. Only the conformal threshold-derivation step is modified: instead of one global
threshold per model (Phase 6), each target subgroup gets its own threshold, computed from that
subgroup's slice of the same calibration set, using the identical nonconformity score and
finite-sample-corrected quantile formula already frozen in Phase 6 (`1 − P̂(y=true class|x)`,
`k = ⌈(n_group+1)(1−α)⌉`-th order statistic, α=0.10).

## 6. Exact Metrics

**Primary target metric:** subgroup-specific empirical conformal coverage on the locked test
set, for each of the 9 frozen (model, subgroup) target combinations, evaluated against the 90%
nominal target with a 95% Wilson score interval (same inference method as Phase 6, Amendment
#10).

**Required before/after metrics for every target combination** (per this task's Part 8):
sensitivity, FNR, targeted disparity (coverage gap from 90%), AUC, overall calibration (Brier/
intercept/slope), subgroup calibration, marginal conformal coverage, subgroup conformal
coverage, uncertainty efficiency (mean prediction-set size, singleton rate), non-target subgroup
fairness.

## 7. Primary Success Criterion

**A target (model, subgroup) combination is judged successfully mitigated if, after applying
the group-specific threshold, the subgroup's test-set coverage 95% Wilson CI includes 90%**
(i.e., the CI no longer excludes the nominal target, resolving the Phase 6 under-coverage
finding). This is the sole primary criterion — "the p-value became significant" alone is not
used; the CI-inclusion criterion is a direct, interpretable statement about coverage validity,
consistent with how Phase 6 itself defined the original failure.

## 8. Secondary Trade-Off Metrics (Pre-Specified Tolerances)

| Metric | Maximum acceptable degradation | Rationale |
|---|---|---|
| AUC (per model, overall) | **0** — no change expected or permitted | Method does not touch model probabilities; any AUC change indicates an implementation error, not a trade-off |
| Overall calibration (Brier/intercept/slope) | **0** — no change expected or permitted | Same reasoning — probabilities are untouched |
| Marginal (overall) conformal coverage | Must remain within **±5 percentage points** of its pre-mitigation value, per model | Target subgroups are large fractions of the test set (Obese ≈41%, 60+ ≈35%), so a real (not necessarily zero) shift in marginal coverage is plausible and must be bounded, not assumed away |
| Non-target subgroup coverage | No non-target subgroup may develop a **new** FDR-significant under-90% deviation that was not already present pre-mitigation | Mondrian conformal prediction is expected, by construction, to leave non-target subgroups' thresholds completely unchanged (they still use the original global per-model threshold) — this is an empirical check confirming that expectation, not assumed |
| Efficiency (mean prediction-set size, singleton rate) within target subgroups | **No pre-specified maximum** — reported honestly as a trade-off, since improving under-coverage by definition typically requires a less restrictive (larger) threshold, which mechanically increases prediction-set size for that subgroup; this is an expected, reportable cost, not a pass/fail gate |

## 9. Non-Target Subgroup Checks

Every non-target category within `sex`, `race_ethnicity`, `age` (other than 60+), and `bmi`
(other than Obese) will have its coverage recomputed after mitigation and compared to its
pre-mitigation value, per model, per this task's Part 8A. Any degradation is reported as a real
result, not omitted.

## 10. Test-Set Protection

Group-specific thresholds are derived **exclusively** from `conformal_calibration_ids.csv`
subgroup slices — never from `test_ids.csv`. The test set is opened for the single, official
Phase 7 test-set touch only after this protocol is committed standalone, implementation is
complete, and pre-test evaluation (using only calibration-set data) is complete.

## 11. Amendment Status

No amendment to the continuous authoritative registry
(`documentation/end_to_end/protocol_amendment_registry.md`) is required to freeze this protocol
— this is a new, prospectively-frozen protocol for a phase that had no prior frozen protocol,
not a deviation from an existing one. If any deviation from this document is discovered
necessary during execution, it will be logged as a dated amendment to the existing continuous
registry (next number in sequence), not a new registry.

## 12. Explicit Confirmation

**No mitigation results existed and no final test-set information was inspected before this
protocol was frozen.** As of this document's commit, no mitigated prediction, no group-specific
threshold, and no pre-test or test-set evaluation result exists anywhere in the repository.
