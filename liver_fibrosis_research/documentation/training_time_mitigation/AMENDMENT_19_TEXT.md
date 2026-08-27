# Protocol Amendment #19

**Date:** 2026-08-27
**Title:** One training-time mitigation of the body-mass reliability–fairness failure — subgroup
instance reweighting of the training loss.

**Motivation.** The frozen study establishes a body-mass reliability–fairness failure that no
post-hoc method repairs (subgroup thresholds, subgroup calibration, Mondrian conformal
recalibration, equalized-odds post-processing, model retuning, joint intersectional conformal, and
— Amendment #17 — conformal selective deferral). Amendment #17 characterised the mechanism as a
**within-subgroup score-ordering failure** (the misses are confidently-scored wrong singletons),
and the manuscript now names a **training-time intervention** as the indicated next step without
attempting one. This amendment attempts exactly one.

**Change.**
- **The intervention.** Retrain the five frozen model families with **Kamiran & Calders
  reweighing** — a per-row training weight `w_i = n(g_i)·n(y_i) / (N·n(g_i,y_i))` computed on the
  fitting partition, making the BMI band statistically independent of the outcome in the reweighted
  fitting distribution. **Arm A (primary):** `g` = 4 BMI bands. **Arm B (secondary):** `g` = 12
  BMI×age cells (cells with < 10 positives fall back to the Arm-A weight).
- **What is applied where.** Weights are applied to the **training partition** (classification
  fits, N = 5,007) and the **proper-train subset** (conformal fits, N = 4,005) only — never to the
  conformal-calibration set and never to the locked test. This preserves split-conformal
  exchangeability, so the marginal coverage guarantee is retained.
- **Evaluation.** The frozen Phase 5 (classification + fairness) and Phase 6 (conformal coverage)
  evaluations, unchanged. Youden thresholds and OOF Platt recalibration are re-derived on the new
  out-of-fold predictions using the already-frozen methods.
- **Decision.** A pre-registered multi-metric gate (G1–G7, fixed in
  `TRAINING_TIME_MITIGATION_PLAN.md` §0.3.6 before any test access) yields one of four verdicts:
  SUCCESS / PARTIAL / NEGATIVE (cost) / NEGATIVE (no efficacy). The manuscript consequence of each
  is pre-written in §0.3.7.

**What does not change.** No hyperparameter search (the exact frozen Phase-3 `best_params` are
reused, extracted live from `models/phase3/model_{name}_v1.joblib`); no predictor is added or
removed; the outcome remains `LUXSMED ≥ 8.2 kPa`; the 70/30 split, the 80/20 proper-train/
calibration sub-split, the seed (42), the CV design (5-fold `StratifiedKFold`, shuffle, seed 42),
the preprocessing (median impute + `StandardScaler` for logistic/MLP), and the base
class-imbalance handling (`class_weight="balanced"` / `scale_pos_weight`) are all frozen. The
subgroup weights are applied **on top of** the base handling via `sample_weight`.

**MLP.** `sklearn.MLPClassifier` has no `sample_weight` (the reason Amendment #3 exists). The
reweighted distribution is approximated by random resampling of the `(BMI band × outcome)` (Arm A)
or `(BMI band × age × outcome)` (Arm B) strata **strictly inside training folds / on the fitting
partition**, using `imblearn.over_sampling.RandomOverSampler` in an `imblearn.pipeline.Pipeline`,
exactly as Amendment #3 did for class balance (`src/phase3_13_imbalance_audit_and_mlp_sensitivity.py`).
If MLP OOF AUROC is unstable across a 3-seed check (SD > 0.01), MLP is reported as "intervention
not applicable in the frozen implementation" and the four `sample_weight`-capable families are
evaluated, and the gate's "≥ 4/5" thresholds become "≥ 3/4".

**Locked-test touches.** **Two** — one per evaluation script (`src/ttm_03_test_classification.py`,
`src/ttm_04_test_conformal.py`), each a single non-iterative run. Recorded in
`documentation/phase3/test_set_lock.md` and this registry (row 19). The new formal hypothesis tests
are corrected within their own BH families; consistent with Amendments #16 and #18, they are not
folded into the frozen project-wide 182-test pooled-FDR family.

**Pre-registration.** The weight formula, the two arms, the frozen hyperparameters, the evaluation,
and the G1–G7 gate with its four verdicts and their pre-written manuscript consequences are all
fixed in `documentation/training_time_mitigation/TRAINING_TIME_MITIGATION_PLAN.md` §0.3 before any
script is run. The pre-execution input snapshot (git HEAD, timestamp, SHA-256 of every input) is
in `PRE_EXECUTION_SNAPSHOT.md`.

**Honest prior.** Normal-BMI has 50 fibrosis-positive cases in the training partition (41 in
proper-train, 22 in the locked test). Reweighting changes the loss landscape but adds no Normal-BMI
signal; the two-mechanism finding (BMI gap threshold-driven, age gap not) means one intervention
may fix one and not the other. The modal expected outcome is PARTIAL or NEGATIVE (no efficacy).
All four verdict branches improve the manuscript.

**Environment note.** `scikit-learn` / `xgboost` / `lightgbm` are not available in the
plan-authoring environment; Phases 1–2 are executed by the operator on the pinned environment
(`requirements-phase3-lock.txt`: scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0,
imbalanced-learn 0.14.2). Phases 0, 3, 4, 5 are done from the produced CSVs.
