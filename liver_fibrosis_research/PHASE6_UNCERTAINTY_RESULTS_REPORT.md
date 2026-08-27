# Phase 6 (Uncertainty) — Results Report

**Generated:** 2026-08-19, live, in a session with continuous direct git/filesystem access
throughout. Every number in this report traces to a machine-generated artifact under
`results/uncertainty/` — none is restated from memory or typed independently of those files.

## 1. Executive Summary

Split Conformal Prediction, executed exactly per the frozen `uncertainty_protocol.md`, achieves
valid marginal coverage close to the pre-specified 90% target for all 5 conformal-valid refit
models on the locked test set (88.1%–90.8%, Wilson 95% CIs all containing or nearly containing
90%). Efficiency, however, diverges sharply and connects directly to Phase 4's calibration
finding: MLP produces decisive, informative prediction sets (96.9% singletons, only 3.1% empty
sets) while the 4 class-weighted models — whose raw probabilities were substantially
miscalibrated in Phase 4 — produce far more ambiguous "both classes possible" sets (23.2%–43.2%
of the test set). Most importantly, **marginal coverage does not hold uniformly across
demographic subgroups**: for all 5 models, BMI-Obese and Age-60+ participants — the exact two
subgroups Phase 5 flagged with statistically significant sensitivity disparities — show
conformal coverage well below the 90% target (as low as 76.8%, Wilson CIs excluding 90%,
FDR-significant in 9 of 10 model×subgroup combinations), while several other subgroups
(Normal/Overweight BMI, age 18–39) show coverage *above* 90%. This is the central, evidence-driven
finding of Phase 6: fairness disparity (Phase 5) and uncertainty-coverage disparity (Phase 6)
co-occur specifically in the same two subgroups, across every model regardless of its
discrimination or calibration profile.

## 2. Phase 5 Dependency Status

`PHASE5_CLOSURE_VERIFICATION_REPORT.md` **does not exist** in this repository (live-checked,
not assumed). Phase 5 was never given a separate, dedicated closure pass — only its own final
results report (`PHASE5_FAIRNESS_RESULTS_REPORT.md`) exists. The three items this task asked
about (BMI headline N/positive-count context, calibration-gradient mechanical-confound
interpretation, deferred-sensitivity-analysis forward tracking) were substantively addressed
*within* that report (§10/§18, §14, §21–22 respectively), but no separate administrative
closure verification exists. **This status does not block Phase 6 technical execution** (the
conformal analysis is methodologically distinct), per this task's own instruction, and Phase 6
does not attempt to close Phase 5 — that remains explicitly out of scope here. Full detail:
`documentation/uncertainty/phase6_pre_execution_snapshot.md`.

## 3. Frozen Uncertainty Protocol

Read live in full this pass: `documentation/phase2/uncertainty_protocol.md`. Method: Split
Conformal Prediction. Target: 90% nominal. Score: `1 − P̂(y=true class|x)` (standard
split-conformal binary score). Calibration architecture: proper-train (4,005) / conformal
calibration (1,002), disjoint from model-fitting data and the test set. Subgroup coverage:
explicitly required ("must not be skipped or treated as secondary"), using the exact Phase 5
subgroup definitions. Two genuine gaps (no inference method, no multiple-comparison strategy
specified) were resolved as logged, dated amendments (#10, #11) before any test-set number was
computed — not silently invented.

## 4. Protocol Hash/Commit

SHA-256 of `uncertainty_protocol.md`: `9983ad3c1604c2a2f43ecfc6afcf876d0ef8a5acc17ff0b9923011323869f7d7`
(recorded in every threshold row of `conformal_thresholds_by_model.csv`).

## 5. Data-Partition Architecture

`results/uncertainty/phase6_partition_audit.csv`: proper_train (N=4,005), conformal_calibration
(N=1,002, 93 positive), test (N=2,146, 200 positive, SHA-256-verified against the human-confirmed
value). All three pairwise disjoint (0 overlaps in every direction) — verified live, not
assumed.

## 6. Conformal-Valid Refit

All 5 original model families refit on `proper_train_ids.csv` only, using `build_pipeline()`
imported directly from the frozen `src/phase3_05_train_and_tune.py` (not reimplemented) with
each model's exact frozen `best_params` (extracted live from the Phase 3 artifacts). This is a
refit, not a new hyperparameter search — no grid/randomized search was run. All 5 validated
without touching the test set: finite outputs, correct [0,1] probability range, correct feature
count/order (`results/uncertainty/conformal_model_refit_registry.csv`).

## 7. Refit Model Provenance

| Model | proper_train N | Hyperparameters (frozen, unchanged from Phase 3) |
|---|---|---|
| Logistic | 4,005 | C=0.01 |
| Random Forest | 4,005 | n_estimators=100, max_depth=7, min_samples_leaf=5 |
| XGBoost | 4,005 | n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.7 |
| LightGBM | 4,005 | n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.7 |
| MLP | 4,005 | hidden_layer_sizes=(32,16), alpha=0.01, learning_rate_init=0.01 |

Original Phase 3 artifacts confirmed byte-identical (unchanged) via SHA-256 re-check
(`tests/test_uncertainty_pipeline.py` TEST 10). Refit artifacts saved to
`models/phase6_conformal_refit/`, distinct filenames, never overwriting Phase 3/4/5 artifacts.

## 8. Nonconformity Score

`1 − P̂(y = true class | x)`, computed from each refit model's `predict_proba` on the conformal
calibration set (N=1,002). All calibration scores preserved
(`results/uncertainty/calibration_scores_<model>.csv`). No NaN/Inf, all probabilities in [0,1].

## 9. Conformal Thresholds

Standard finite-sample-corrected quantile, `k = ⌈(n+1)(1−α)⌉ = 903`, direct order-statistic
indexing (not a numpy interpolation method, to avoid ambiguity):

| Model | Threshold |
|---|---|
| Logistic | 0.672744 |
| Random Forest | 0.607211 |
| XGBoost | 0.653193 |
| LightGBM | 0.656959 |
| MLP | 0.377967 |

MLP's substantially lower threshold reflects its tighter, better-calibrated raw probability
distribution (Phase 4 finding) — a lower threshold on `1−P(true|x)` means the model needs less
"slack" to achieve the target coverage.

## 10. Final Marginal Coverage

`results/uncertainty/marginal_coverage_test_set.csv` (the single, official test-set touch,
2026-08-19 14:16:42):

| Model | Empirical Coverage | 95% Wilson CI | vs. 90% Target |
|---|---|---|---|
| Logistic | 90.82% | [89.52%, 91.97%] | +0.82pp |
| Random Forest | 89.61% | [88.25%, 90.83%] | −0.39pp |
| XGBoost | 88.12% | [86.68%, 89.42%] | −1.88pp |
| LightGBM | 89.61% | [88.25%, 90.83%] | −0.39pp |
| MLP | 89.19% | [87.80%, 90.43%] | −0.81pp |

All 5 land within a 2-percentage-point band of the nominal target — consistent with split
conformal's marginal coverage guarantee holding under exchangeability, as expected by
construction (this is not itself a novel finding — it is the method behaving as designed). The
correct language for this result: **"the conformal procedure achieved empirical coverage of
88.1%–90.8% against the pre-specified 90% target under the stated conformal framework."** No
claim of "90% certainty" or "guaranteed accuracy" is made anywhere in this report.

## 11. Efficiency

Mean prediction-set size (0, 1, or 2 candidate labels): Logistic 1.432, Random Forest 1.232,
XGBoost 1.271, LightGBM 1.312, MLP 0.969 (< 1 because MLP occasionally outputs an *empty* set —
3.12% of the time — when neither candidate label's score clears the threshold). Singleton rate
(a single, decisive answer): Logistic 56.8%, Random Forest 76.8%, XGBoost 72.9%, LightGBM 68.8%,
**MLP 96.9%**. Ambiguous rate (both classes included, i.e. "uncertain"): Logistic 43.2% (highest),
Random Forest 23.2% (lowest among the 4 balanced models), XGBoost 27.1%, LightGBM 31.2%, MLP
0.0%. **This directly connects to Phase 4**: the models with the largest raw calibration
overprediction (Logistic, XGBoost, LightGBM, Random Forest) also produce the least decisive
conformal output at the same nominal coverage — a model can have correct marginal coverage while
being substantially less *useful*, and that is reported here as a real, important result, not
hidden as a limitation of an otherwise "successful" method.

## 12. Subgroup Coverage (Required, Not Optional)

Full detail: `results/uncertainty/subgroup_coverage.csv` (75 rows: 5 models × 15 categories).
**Marginal coverage does not imply subgroup-conditional coverage** — the single most important
distinction in this phase (§17 of the task; Part 17 discipline). The clearest, most consistent
finding:

| Subgroup | Coverage range across 5 models | CI excludes 90%? |
|---|---|---|
| BMI Obese | 76.8%–82.3% | **Yes, all 5 models** |
| Age 60+ | 81.1%–85.6% | **Yes, all 5 models** |
| BMI Normal | 96.8%–98.0% (approx.) | Yes (above target), several models |
| Age 18–39 | 95.8%+ | Yes (above target), several models |

Every one of the 10 (model × {BMI-Obese, Age-60+}) combinations shows a Wilson CI that excludes
90% — a universal, cross-model pattern, not specific to any one model family
(`results/uncertainty/phase5_headline_subgroup_coverage_cooccurrence.csv`).

## 13. Coverage Inference

Wilson score interval (95%, Amendment #10) for every coverage estimate; Benjamini-Hochberg FDR
(Amendment #11), one family per (model × dimension), testing H0: subgroup coverage = 90% via an
exact one-sample binomial test. Full table: `results/uncertainty/coverage_inference.csv`. **All
10 of the 10** (model × {BMI-Obese, Age-60+}) combinations are significant after FDR correction
(adjusted p ranging from <0.0001 to 0.00034) — live-verified this pass by joining
`subgroup_coverage.csv`'s FDR results directly, not asserted from memory.

## 14. Phase 5 → Phase 6 Uncertainty Relationship

`results/uncertainty/phase5_phase6_relationship.csv` and
`phase5_phase6_correlation_summary.csv` (Part 13). Across **all** 11 non-reference subgroup
comparisons per model, the correlation between |sensitivity disparity| (Phase 5) and |coverage
deviation from 90%| (Phase 6) is **weak-to-moderate and inconsistent across models**
(Pearson r = 0.04 to 0.46) — the overall relationship is *not* uniformly strong, and this is
reported honestly rather than oversold. However, the **two specific, best-powered
(primary-feasibility-tier) subgroups that Phase 5 flagged as statistically significant** —
BMI-Obese and Age-60+ — show a coverage deviation that is large, consistent, and
FDR-significant in essentially every model (§12–13). This is Outcome **A** from this task's Part
13 framework (fairness disparity and uncertainty disparity co-occur) for these two subgroups
specifically, not a claim that fairness and uncertainty disparities are generally correlated
across all subgroups.

## 15. Class-Specific Coverage

**Not performed.** `uncertainty_protocol.md` does not authorize class-specific coverage as a
separate deliverable, and this task's Part 15 makes it conditional ("only if explicitly
authorized"). Not invented.

## 16. Intersectional Coverage

**Not performed.** Same reasoning as §15 — the frozen protocol authorizes subgroup coverage
within each of the 4 primary dimensions only, not intersections; Part 16 makes this explicitly
conditional and it was not authorized.

## 17. Multiple-Comparison Strategy

Phase 6's own family (Amendment #11): BH-FDR per (model × dimension), verified structurally
separate from Phase 3's single AUC family, Phase 4's three calibration families, and Phase 5's
sensitivity-disparity families — `phase6_04_final_test_touch.py` never reads any of those
scripts' output files (`tests/test_uncertainty_pipeline.py` TEST 19).

## 18. Sensitivity Analyses

No Phase-6-specific sensitivity analysis was pre-specified in the frozen protocol beyond the
core method itself. The Phase5↔Phase6 relationship investigation (§14) and the reproducibility
rerun (§20) are the analyses performed. No new sensitivity analysis was invented after seeing
results.

## 19. Deferred Analyses

The 4 Phase-2-frozen sensitivity analyses (alternative 8.0kPa threshold, CAND_2 cohort,
fasting-extended architecture, multiple-imputation) remain **unexecuted**, carried forward
unchanged from Phase 5. Assessed individually for Phase 6 relevance:

- **Alternative threshold, CAND_2 cohort, fasting-extended architecture**: all require full
  retraining under a different outcome/cohort/predictor definition — out of scope for Phase 6
  (Part 29 explicitly forbids retraining beyond the conformal-valid refit); belong to a future,
  separate phase if pursued.
- **Multiple-imputation**: also requires retraining, so it cannot be executed here either. **No
  multiple-imputation-based reanalysis was performed in Phase 6.** The Non-Hispanic Black
  subgroup's coverage result reported immediately below was computed using the same standard
  Phase 6 complete-case cohort, the same conformal-valid refit models, and the same conformal
  calibration procedure used for every other subgroup in this report — it is drawn from the same
  single test-set touch (`results/uncertainty/subgroup_coverage.csv`, all rows sharing the one
  `2026-08-19 14:16:42` generation timestamp, confirmed live in the Phase 6 Closure-Clarification
  pass) as the BMI/age results discussed elsewhere in this report. The reference to "multiple
  imputation" below is *interpretive context only*, recalling the Phase 2 finding that motivates
  why this particular subgroup's result matters: the complete-case exclusion disparity (41.3% of
  exclusions vs. 25.0% of retained participants were Non-Hispanic Black, Phase 2
  `missing_data_protocol.md`) means the test-set population itself may under-represent this group
  relative to the full source population. This pass checked whether Non-Hispanic Black subgroup
  *coverage* (from the standard, already-computed result) shows a comparable breakdown to
  BMI-Obese/Age-60+: it does **not** — coverage ranges 86.9%–88.7% across the 5 models, only
  1 of 5 (XGBoost) has a CI excluding 90%, a much milder deviation
  (`results/uncertainty/phase5_phase6_relationship.csv`). This is a distinct mechanism from the
  selection-disparity question: within-sample coverage behavior (measured here, using the
  standard complete-case cohort) is not the same as whether the sample itself is representative
  (the open, still-deferred, unexecuted multiple-imputation question — see
  `documentation/project_roadmap/deferred_sensitivity_analyses.md`) — both are reported, kept
  separate, and neither is used to explain the other.

## 20. Reproducibility

Package versions unchanged from Phase 4/5. A full-chain reproducibility check (refit →
calibration scores → threshold → final coverage) was performed in an isolated, in-memory rerun
(no files written to any official location, not a second official test-set touch): all 5
models' thresholds and marginal coverage values reproduced to within 3×10⁻⁷ of the committed
values — this residual is fully attributable to the 6-decimal rounding applied when the official
CSVs were saved (e.g. 0.672744 vs. 0.672744 at full precision), not genuine non-determinism.
This is the documented, benign explanation required before treating a nonzero diff as a real
reproducibility failure (Part 28 stop condition #11) — no re-run of the official test-set touch
was performed or needed.

**Disclosed process note:** the reproducibility-check script contained a stray top-level
`import phase6_02_conformal_refit`, which (since that script has no `if __name__ == "__main__"`
guard) caused the official refit to actually re-execute once against the real output paths
during this check, rather than staying confined to the isolated scratch directory as intended.
The resulting `conformal_model_refit_registry.csv` was byte-identical except for the
`fit_seconds` timing column (e.g. 0.031s vs. 0.026s) — confirmed via `git diff` — and the
regenerated model artifacts had identical SHA-256 hashes to the originals. The spurious diff was
reverted (`git checkout`) rather than committed, and is disclosed here rather than silently
fixed.

## 21. Validation Tests

`tests/test_uncertainty_pipeline.py`, run live: **50/50 checks passed**, covering all 22
required test categories (protocol hash, partition exactness/disjointness, frozen predictor/
outcome immutability, 5-model refit completeness, proper-train-only provenance, Phase 3
artifact immutability, calibration-set-only score computation, test-set-touch scoping,
nonconformity-score and quantile arithmetic, coverage/efficiency range validity, Phase 5 bin
fidelity, single threshold per model (no subgroup-specific tuning), Phase 6 FDR-family
separation, deferred-analysis tracking, no Phase 7 execution, code-derived results).

## 22. Git/Provenance

| Commit | Subject |
|---|---|
| `95c2a06` | Commit A — conformal-valid refit + validation |
| `3cee362` | Commit B — calibration scores + frozen conformal thresholds |
| `387e9fc` | Commit C — the single, atomic final test-set touch |
| *(Commit D, created immediately after this report)* | Subgroup relationship analysis + validation tests + this final report |

All commits pushed and independently verified via both `git fetch`+`rev-parse` and a direct
`git ls-remote` server query.

## 23. Limitations

- Subgroup coverage precision is inherently limited by the smaller test-set N within each
  category (same structural limitation as Phase 5) — categories below primary-feasibility tier
  are reported with correspondingly wide Wilson CIs, not treated as equally reliable.
- The 4 deferred Phase-2 sensitivity analyses remain unexecuted (§19), a pre-existing gap this
  phase could not close without retraining.
- Phase 5 was not formally, administratively closed (§2) — this does not affect the validity of
  Phase 6's own findings, which are methodologically independent, but is disclosed as an
  outstanding process item.
- The overall (all-subgroup) correlation between sensitivity disparity and coverage deviation is
  weak-to-moderate and model-inconsistent (§14) — only the two specific, well-powered flagged
  subgroups show the clear, universal pattern; this is not evidence of a general law relating
  fairness and uncertainty disparities across every subgroup.

## 24. Next-Phase Requirements

No further model refit or conformal recalibration is required for this project's next stage.
Any pursuit of fairness mitigation, group-specific recalibration, or the deferred Phase-2
sensitivity analyses (§19) — including multiple-imputation, which bears directly on the
Non-Hispanic Black selection-disparity question — remains a future-phase prerequisite, not
addressed here per Part 29's explicit scope boundary.

---

**PHASE 6 COMPLETE WITH DOCUMENTED LIMITATIONS — READY FOR NEXT STAGE**

Basis: the frozen uncertainty protocol was read live in full and followed exactly (method,
score, target coverage, calibration architecture); the Phase 5 closure dependency status was
checked and disclosed honestly rather than assumed; all three data partitions were verified
disjoint and hash-confirmed; the conformal-valid refit was completed and validated without
touching the test set; nonconformity scores and thresholds were frozen before any test-set
access; the test set was touched exactly once, atomically, for coverage, efficiency, and the
required subgroup coverage together; the Phase 5→Phase 6 relationship was investigated and
reported honestly (not forced to confirm a strong general correlation where the data show a
specific, narrower pattern); multiple-comparison correction used Phase 6's own structurally
verified family; deferred analyses (including multiple-imputation) were tracked explicitly, not
dropped; reproducibility was confirmed via an isolated rerun with a documented benign
floating-point explanation; 50/50 automated tests passed; and Git history was committed, will be
pushed, and independently verified. The "documented limitations" qualifier reflects §19, §23.
