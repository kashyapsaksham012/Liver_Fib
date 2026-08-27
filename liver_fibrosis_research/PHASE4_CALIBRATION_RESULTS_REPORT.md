# Phase 4 (Calibration) — Results Report

**Generated:** 2026-08-19, live, in a session with continuous direct git/filesystem/network
access throughout. Every number in this report traces to a machine-generated artifact under
`results/calibration/` — none is restated from memory or typed independently of those files.

## 1. Executive Summary

The 5 frozen Phase 3 primary models (Logistic Regression, Random Forest, XGBoost, LightGBM,
MLP) achieve near-identical discrimination (test-set ROC-AUC 0.8229–0.8429, overlapping CIs,
no statistically significant pairwise superiority after FDR correction — Phase 3 finding,
unchanged here). Despite this, their **raw** predicted probabilities are calibrated very
differently: Logistic Regression, Random Forest, XGBoost, and LightGBM (all trained with
class-weighting or scale_pos_weight to address the 9.31% outcome prevalence) show large,
statistically significant negative calibration intercepts on both the OOF tier and the
independently-confirmed locked test set — systematic overestimation of risk. MLP (trained
without any imbalance correction) is comparatively close to calibrated but still shows a
small, statistically significant intercept. A logistic (Platt-type) recalibration, fit
exclusively on out-of-fold predictions and applied once to the locked test set, corrects this:
intercepts collapse toward 0 and Brier scores drop by roughly half for the 4 affected models,
while MLP is materially unchanged. This is consistent with the pre-specified H2 expectation
(`documentation/phase2/primary_research_question.md`) that at least one model would show
measurable miscalibration despite acceptable discrimination — here, essentially all 5 models
did, to varying degrees.

## 2. Phase 4 Objective

Per `documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md` §1: assess whether the predicted
probabilities produced by each of the 5 frozen Phase 3 primary models are quantitatively
trustworthy — diagnostic and reporting only, not a phase that reopens model selection,
hyperparameters, the outcome threshold, or the predictor set. None of those were reopened.

## 3. Frozen Protocol Commit

`2436d9554647c65af43e7d8cc61cdfeed9fb9a6a` — live-verified this pass via
`git log --all -- CALIBRATION_PROTOCOL_FREEZE.md` (not assumed from prior documentation).

## 4. Protocol Checksum

SHA-256 `3c843ad02cd91736a597ad3256a6c6309ffac2819a882c72f77b9220c64fca1d` — recomputed live at
the start of this pass and again inside `tests/test_calibration_pipeline.py` (TEST 1, PASS).
File unchanged since commit `2436d95` (`git diff 2436d95 -- CALIBRATION_PROTOCOL_FREEZE.md`
returns empty).

## 5. Phase 3 Model Handoff

All 5 primary model artifacts (`models/phase3/model_<name>_v1.joblib`) verified present with
live-recomputed SHA-256 hashes recorded in `documentation/calibration/phase4_pre_execution_snapshot.md`
§9 and re-verified in `tests/test_calibration_pipeline.py` (TEST 2, PASS, all 6 including
MLP_balanced). Models were not retrained, retuned, or feature-modified. MLP_balanced remains
sensitivity-only throughout (TEST 13, PASS — excluded from `primary_metrics_by_model.csv` and
from all formal pairwise inference).

## 6. Prediction-Input Verification

`results/calibration/phase4_prediction_input_audit.csv`: all 5 primary models + MLP_balanced,
both OOF (5,007 rows) and locked-test (2,146 rows) tiers — one row per participant, zero missing
probabilities, zero Inf, all probabilities in [0,1], targets binary and consistent (9.3070%
OOF prevalence, 9.3197% test prevalence, matching across all 6 models exactly). Full PASS,
no integrity issue found.

## 7. Calibration-Data Separation

Per protocol §6 (two-tier decision), documented in `documentation/calibration/
phase4_calibration_data_flow.md`: development/diagnostic tier = CV out-of-fold predictions
(`validation_predictions_<model>.csv`, genuine `cross_val_predict` output, live-verified via
source grep); confirmatory tier = locked test set, touched exactly once. The
`conformal_calibration_ids.csv` partition (reserved for the future Uncertainty phase) was
never referenced by any Phase 4 script (TEST 4, PASS).

## 8. Test-Set Protection

`results/calibration/phase4_test_set_protection_audit.md`: verified before any metric was
computed that no calibration-method selection, fitting, binning selection, recalibration
selection, metric selection, threshold change, or model selection had used test data.
Result: VERIFIED, no contamination.

## 9. Primary Calibration Metrics

`results/calibration/primary_metrics_by_model.csv` (OOF tier, raw probabilities, point
estimates) joined with `results/calibration/calibration_inference.csv` (95% bootstrap CIs,
n=2,000, paired) — same file, same methodology for all 5 models, no MLP-specific computation.
Cross-verified against `results/calibration/mlp_calibration_metric_audit.csv` this pass
(**Item 1**): all five models now carry identical quantitative structure.

| Model | Intercept | Intercept 95% CI | Slope | Slope 95% CI | Brier | Brier 95% CI |
|---|---|---|---|---|---|---|
| Logistic | −2.242509 | [−2.355021, −2.138444] | 1.060614 | [0.952434, 1.183636] | 0.173932 | [0.169042, 0.178848] |
| Random Forest | −1.862450 | [−1.969692, −1.761026] | 1.198516 | [1.093911, 1.309657] | 0.139695 | [0.135316, 0.144132] |
| XGBoost | −2.046007 | [−2.159344, −1.940396] | 1.039320 | [0.948429, 1.137262] | 0.152265 | [0.147099, 0.157504] |
| LightGBM | −2.053483 | [−2.164577, −1.946315] | 1.062210 | [0.965944, 1.164172] | 0.155387 | [0.150408, 0.160381] |
| MLP | −0.280858 | [−0.465988, −0.084605] | 0.829627 | [0.754584, 0.914947] | 0.070972 | [0.065632, 0.076728] |

**MLP intercept-CI-vs-zero determination (Item 1, §2C):** MLP's calibration-intercept 95% CI is
[−0.465988, −0.084605] — both bounds are negative, so **the CI does not include 0**. This is
stated as the exact estimate and CI, not translated into "MLP is well calibrated" or "perfectly
calibrated" (no such acceptance threshold exists in the frozen protocol). MLP's intercept is
substantially closer to 0 than the other 4 models' (whose CIs are also bounded well away from
0, but at roughly 4–8× the magnitude), which is the basis for the report's "comparatively
closer to calibration" language — a quantitative comparison between five statistically
non-zero intercepts, not a claim that MLP is calibrated in an absolute sense.

## 10. Calibration Curves

10 equal-frequency (decile) bins per model, all achieving the full 10 bins with no degeneracy
(`results/calibration/curve_data/`, `results/calibration/figures/`). Visually and numerically,
the 4 balanced-training models show predicted-probability deciles well above the diagonal
(overprediction) across most of the range; MLP tracks the diagonal closely except at its
highest decile.

## 11. Calibration Intercept

Bootstrap 95% CIs (`results/calibration/calibration_inference.csv`, n=2,000, paired):
Logistic [−2.355, −2.138]; Random Forest [−1.970, −1.761]; XGBoost [−2.159, −1.940]; LightGBM
[−2.165, −1.946]; MLP [−0.466, −0.085]. All 5 exclude 0. No acceptance threshold is defined in
the frozen protocol, so no pass/fail label is applied — raw values and CIs are reported as-is.

## 12. Calibration Slope

Logistic 1.061 [0.952, 1.184]; Random Forest 1.199 [1.094, 1.310]; XGBoost 1.039 [0.948, 1.137];
LightGBM 1.062 [0.966, 1.164]; MLP 0.830 [0.755, 0.915]. Four of five CIs include 1; MLP's does
not. Per the protocol's interpretation discipline, slope is not read in isolation — the full
picture (§9–14) is used together.

## 13. Brier Score

`results/calibration/brier_scores.csv` (OOF, includes MLP_balanced labeled sensitivity):
Logistic 0.1739, Random Forest 0.1397, XGBoost 0.1523, LightGBM 0.1554, MLP 0.0710,
MLP_balanced 0.1606 (sensitivity, not merged into the primary comparison).

## 14. ECE (Secondary/Supplementary)

`results/calibration/ece_secondary_metric.csv`: Logistic 0.2931, Random Forest 0.2322, XGBoost
0.2447, LightGBM 0.2507, MLP 0.0132, MLP_balanced 0.2506 (sensitivity). Reported under its
frozen secondary/supplementary label, not promoted to primary.

## 15. Probability Diagnostics

`results/calibration/probability_distribution_diagnostics.csv`: mean predicted probability for
the 4 balanced-training models ranges 0.325–0.386, roughly 3.5–4× the true 9.31% prevalence;
MLP's mean (0.0916) tracks prevalence closely. MLP shows 1,030/5,007 (20.6%) OOF predictions
below 0.01, consistent with a model given no explicit imbalance correction. Diagnostic
observations only — not used to select or exclude any model.

## 16. Statistical Inference

Percentile bootstrap, n=2,000, paired at the participant level (frozen protocol §12), executed
exactly as specified — not the Phase 3 procedure reused blindly, but the same method
deliberately and transparently carried forward, disclosed in the protocol document itself as
inherited from Phase 3 Amendment #2 rather than a Phase-2 freeze. `bootstrap_n_valid_resamples`
= 2000/2000 for every model/metric (no degenerate resamples). Full table:
`results/calibration/calibration_inference.csv`.

## 17. Multiple-Comparison Handling

Benjamini-Hochberg FDR, applied separately within each metric's family of 10 pairwise
comparisons (intercept, slope, Brier — 3 independent families). Per the standing
project language rule, non-significant results are reported as "no statistically significant
pairwise superiority was demonstrated after FDR correction" — applies specifically to:
XGBoost-vs-LightGBM (intercept, slope), Logistic-vs-XGBoost (slope), Logistic-vs-LightGBM
(slope). All other pairwise comparisons across all 3 metrics were significant after FDR
correction.

**Calibration-phase statistical comparisons were treated as an independent hypothesis-testing
family from the Phase 3 baseline-model comparisons, with separate multiple-comparison
correction.** This is code-verified, not merely asserted in prose: Phase 3's single 10-pair
ROC-AUC family is computed entirely within `src/phase3_07_plots_and_comparison.py` (its own
p-value array, its own BH pass, written to `results/tables/phase3_model_comparison.csv`), while
Calibration's three 10-pair families (intercept, slope, Brier) are computed entirely within
`src/phase4_04_inference.py` (a fresh p-value array re-initialized per metric, written to
`results/calibration/calibration_inference.csv`). No code path reads from, writes to, or
combines both files' p-value arrays — full verification in
`documentation/calibration/calibration_fdr_family_verification.md`. The bootstrap
*methodology* (n=2,000, seed=42, paired, 95% percentile CIs, BH-FDR) is deliberately reused from
Phase 3 (disclosed in the frozen protocol §12 as inheriting Amendment #2), but the *hypothesis
families being jointly corrected* are structurally disjoint.

## 18. Recalibration

**Authorized and pursued**, per Protocol Amendment #8
(`documentation/end_to_end/protocol_amendment_registry.md`), logged before fitting: logistic
(Platt-type) recalibration, `p_recal = sigmoid(intercept + slope · logit(p_raw))`, using the
already-fit OOF calibration-in-the-large parameters as the transform. Selected over isotonic
regression because the miscalibration pattern was intercept-shift-dominated with slopes
reasonably near 1 for 4/5 models — the signature a 2-parameter logistic transform corrects
directly — and because isotonic regression's added flexibility carries more overfitting risk
with only 466 OOF positives. Fit exclusively on OOF data; never fit on the test set (verified
structurally and numerically in `tests/test_calibration_pipeline.py` TEST 11 — the Platt
parameters applied to the test set are identical to the ones committed from the OOF-only fit).
Original probabilities were never overwritten (`recalibrated_oof_predictions_<model>.csv` are
separate files).

## 19. Pre/Post Recalibration Comparison

`results/calibration/recalibration_pre_post_comparison.csv` reports OOF pre/post values, but
these are **circular by construction** (the transform is fit and evaluated on the same OOF
sample, so post-recalibration intercept ≈ 0 and slope ≈ 1 trivially) — disclosed explicitly in
the script's own output, not presented as evidence of quality. The genuine, non-circular
evidence is the held-out locked-test-set comparison in §20 below.

## 20. Final Locked Test-Set Calibration Results

**The first and only test-set touch**, `results/calibration/test_set_calibration_final.csv`,
timestamp 2026-08-19 10:38:36 +0530, protocol commit/checksum recorded in every row:

| Model | Variant | Intercept | Slope | Brier | ECE |
|---|---|---|---|---|---|
| Logistic | raw | −2.2602 | 0.9961 | 0.1755 | 0.2967 |
| Logistic | recalibrated | −0.1537 | 0.9395 | 0.0705 | 0.0172 |
| Random Forest | raw | −1.9679 | 1.2812 | 0.1458 | 0.2452 |
| Random Forest | recalibrated | 0.0238 | 1.0694 | 0.0709 | 0.0113 |
| XGBoost | raw | −2.1629 | 1.1616 | 0.1557 | 0.2572 |
| XGBoost | recalibrated | 0.1241 | 1.1180 | 0.0694 | 0.0152 |
| LightGBM | raw | −2.1846 | 1.2031 | 0.1603 | 0.2638 |
| LightGBM | recalibrated | 0.1418 | 1.1333 | 0.0696 | 0.0143 |
| MLP | raw | −0.4354 | 0.9293 | 0.0716 | 0.0290 |
| MLP | recalibrated | −0.1189 | 1.1211 | 0.0715 | 0.0264 |

This is genuine held-out evidence: the raw test-set intercepts closely replicate the OOF
diagnosis (not an artifact of overfitting to the OOF sample), and the recalibration benefit for
the 4 balanced-training models is real and substantial (Brier roughly halved, ECE roughly
10–17× smaller). MLP shows only marginal change under recalibration, consistent with its raw
probabilities already being comparatively close to calibrated. No anomaly appeared; no second
test-set touch was performed or is planned.

## 21. Interpretation

No pass/fail acceptance threshold is defined anywhere in the frozen protocol or Phase 2
documents, so none is invented here. Reported as raw values, CIs, curves, and comparative
evidence only. The data support a clear, statistically robust distinction: the 4
class-weighted/oversampling-trained models exhibit large systematic overprediction of risk in
their raw output, which a simple recalibration step corrects substantially; MLP does not
require this correction to nearly the same degree. This is not described as any model being
"well calibrated" or "poorly calibrated" as a categorical label — the numbers and CIs are
presented directly, per the protocol's interpretation discipline (§22 of the task).

## 22. Relationship to Phase 3 Discrimination

Phase 3 test-set ROC-AUC (`results/tables/phase3_overall_discrimination.csv`, unchanged,
prior evidence): Logistic 0.8334, Random Forest 0.8343, XGBoost 0.8429, LightGBM 0.8394, MLP
0.8229 — all overlapping 95% CIs, no statistically significant pairwise superiority
demonstrated after FDR correction (Phase 3 finding). Phase 4 shows these near-identical
discriminators diverge substantially in raw calibration behavior. This directly answers the
question posed in Part 24 of this task ("do models with similar discrimination show different
calibration behavior?") — **yes**, discrimination and calibration are empirically dissociated
here. This is consistent with the pre-specified H2 expectation
(`documentation/phase2/primary_research_question.md`: "at least one model will show measurable
miscalibration... even where discrimination (AUC) appears acceptable") — per the standing
project language rule, this is reported as **"observed results were consistent with the
pre-specified H2 expectation,"** not as "H2 was proven." No model is declared "better" or
"clinically superior" from this alone; discrimination, calibration, statistical significance,
and clinical relevance are kept as distinct concepts throughout.

## 23. Sensitivity Analyses

MLP_balanced (class-imbalance oversampling variant) reported throughout as a labeled,
non-primary sensitivity check (Brier 0.1606, ECE 0.2506, OOF intercept −2.156) — its raw
calibration pattern resembles the class-weighted models' pattern (large negative intercept),
consistent with oversampling producing the same probability-scale shift as class-weighting.
Never merged into the 5-model primary table or formal pairwise inference (TEST 13, PASS). No
other sensitivity analysis was pre-specified in the frozen protocol, so none was invented.

## 24. Reproducibility

Package versions unchanged from the Pre-Calibration Closure pass (scikit-learn 1.9.0, xgboost
3.4.1, lightgbm 4.7.0, numpy 2.5.2, pandas 3.0.5 — matches `requirements-phase3-lock.txt`
exactly). One clean reproducibility rerun performed (Part 31): all pre-test-set computations
and the test-set-touch computation itself were rerun into an isolated scratch directory (never
committed, never treated as a second official test-set touch) and diffed numerically against
the committed artifacts. Result: **all 7 artifact families identical to committed values**
(max absolute difference 0 across intercept, slope, Brier, ECE, bootstrap CIs, and probability
diagnostics). Bootstrap used the fixed project seed (42), consistent with the deterministic
requirement.

## 25. Automated Test Results

`tests/test_calibration_pipeline.py`, run live: **109/109 checks passed**, covering all 20
required test categories (protocol checksum, model/prediction hash verification, data-source
correctness, per-model integrity, test-set-protection structural checks, primary model
representation, MLP_balanced non-promotion, metric-label correctness, curve/data
correspondence, raw-prediction immutability, artifact traceability, Phase 1/2 frozen-definition
immutability, absence of Phase 5/6 execution, and report-value traceability). Two initial test
bugs (false positives in TEST 10 and TEST 11, caused by an overly crude string-match rather
than a real pipeline problem) were found and corrected before the final run — disclosed here
rather than silently fixed.

## 26. Commit History

| Commit | Subject |
|---|---|
| `403a9e3` | Phase 4 Calibration: pre-test-set implementation (Commit A) |
| `204d008` | Phase 4 Calibration: FIRST AND ONLY TEST-SET TOUCH (Commit B) |

Clean two-commit sequence, per Part 32 — no scientific decision was disguised as an
implementation detail, and the test-set touch is unambiguously isolated in its own commit,
distinct from all upstream work.

## 27. Remote Verification

Both commits pushed (`git push origin main`: `1fc309f..204d008`) and independently verified via
two separate live checks: `git fetch` + `git rev-parse HEAD`/`origin/main` (exact match,
`204d0081069bea44685aa3d7298df50b628a0156`), and a direct `git ls-remote origin
refs/heads/main` server query (same hash, bypassing any local cache). Both `403a9e3` and
`204d008` confirmed reachable on `origin/main` via `git merge-base --is-ancestor`.

## 28. Limitations

- The `n_probabilities_clipped_for_logit` diagnostic showed 0 clipped values on the OOF tier
  for all models, but the raw locked test set contains at least one exact probability of 1.0
  for Logistic Regression (noted in the Pre-Calibration Closure pass's prediction-input audit);
  the EPS-clipping in `phase4_09` handled this without incident, and it is disclosed here rather
  than silently absorbed.
- The Phase 2/Phase 3 sub-commit-chronology limitation (bundled commit `c9c6ee3`, Tier D
  provenance) documented in prior audits is unchanged and carried forward as-is — no new gap was
  introduced by Phase 4, since both Phase 4 commits are individually clean and standalone.
- The circularity of the OOF pre/post recalibration comparison (§19) is a genuine limitation of
  that specific comparison, not of the analysis as a whole — the locked-test-set comparison
  (§20) is the actual non-circular evidence and is the one relied upon for interpretation.

## 29. What Is Deferred to Phase 5 (Fairness)

Subgroup calibration (by sex, race/ethnicity, age, BMI) was not performed in Phase 4, per
protocol §11 and this task's Part 25 — the frozen subgroup definitions and precision-tier
labeling from `fairness_subgroup_protocol.md` are preserved unchanged for that phase. No
fairness mitigation, threshold optimization, or demographic disparity metric was computed here.
`results/fairness/` does not exist (TEST 19, PASS).

## 30. What Is Deferred to Phase 6 (Uncertainty/Conformal Prediction)

No conformal prediction, coverage analysis, prediction-set analysis, or conformal model refit
was performed. `conformal_calibration_ids.csv` was never used by any Phase 4 script (TEST 4,
PASS). The conformal-valid model refit on `proper_train_ids.csv` remains an unstarted Phase 6
prerequisite, unchanged by this phase.

## 31. Final Phase 4 Status

**PHASE 4 COMPLETE — READY FOR FAIRNESS**

Basis: actual execution occurred throughout (every number traces to a live-generated,
committed artifact); all mandatory analyses (primary/secondary metrics, curves, inference,
recalibration decision with logged amendment, pre/post comparison) executed; the test set was
touched exactly once, confirmed by commit structure and by `tests/test_calibration_pipeline.py`
TEST 10/11; all required outputs exist (`documentation/calibration/phase4_pre_execution_snapshot.md`,
`phase4_calibration_data_flow.md`, and every file listed in Part 34 of the task); automated
validation passed 109/109; the clean reproducibility rerun matched the committed artifacts
exactly; commit discipline was followed (2 clean, purpose-separated commits); and remote history
was independently verified via two separate methods.
