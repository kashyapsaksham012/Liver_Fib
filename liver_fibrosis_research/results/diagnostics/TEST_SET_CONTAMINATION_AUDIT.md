# Test-Set Contamination Audit — Three Diagnostics

## Scripts audited (this execution)

### `src/sens_04_continuous_splines.py`
- Files read: `analysis_dataset_primary.parquet`, `train_ids.csv`, `test_ids.csv`,
  `validation_predictions_<model>.csv` (OOF), `test_predictions_<model>.csv`,
  `test_set_recalibrated_predictions.csv`, `test_set_prediction_sets.csv`,
  `phase3_threshold_selection.csv`, `conformal_thresholds_by_model.csv`.
- Labels accessed: OOF `true_target` (fitting); test `true_target` (evaluation/description only).
- Fitting operations: RCS-basis logistic/linear regression, fit exclusively on
  `build_oof_frame()` output (OOF training predictions). Knots computed from `train_ids.csv`'s
  covariate distribution only.
- Test-set operations: frozen OOF-fit coefficients applied to a covariate grid derived from the
  training range; decile description computed directly from test data (no fitting, no parameter
  estimation) — purely descriptive.
- **Verified: NO test labels were used to select spline complexity, choose knots, or fit any
  spline/regression parameter.**

### `src/sens_06_group_specific_thresholds.py`
- Files read: same base files, plus `bmi_group_final`/`age_group_final` from the master parquet.
- Fitting operations: `youdens_j_threshold()` (identical to `phase3_06`'s implementation) computed
  on `validation_predictions_<model>.csv` (OOF), filtered per subgroup. Frozen before any test
  score is computed.
- Test-set operations: frozen per-subgroup thresholds applied to test-set raw probabilities.
- **Verified: NO test labels were used to derive any threshold.**

### `src/sens_05_subgroup_recalibration.py`
- Files read: OOF/test predictions (v1 model family), `conformal_calibration_ids.csv`,
  `test_ids.csv`, `proper_train_refit` model joblibs, `subgroup_coverage.csv` (existing baseline,
  read-only for comparison).
- Fitting operations: Arm A — Platt logistic regression fit on `validation_predictions_<model>.csv`
  (OOF), filtered per subgroup. Arm B — Platt logistic regression and the new conformal quantile
  fit on `conformal_calibration_ids.csv` rows only, filtered per subgroup; explicit assertion
  confirms `cal_ids.isdisjoint(test_ids)` before any calibration-set computation proceeds.
- Test-set operations: frozen subgroup Platt parameters and the frozen new quantile threshold
  applied to test-set raw probabilities for coverage/efficiency evaluation only.
- **Verified: NO test labels were used to fit any Platt parameter or derive the new conformal
  quantile.**

## Confirmed contamination in the SUPERSEDED prior scripts (not used as a source; documented for
the scientific record per the governing protocol's "do not silently overwrite" rule)

| File | Defect | Evidence |
|---|---|---|
| Prior `src/sens_04_continuous_splines.py` | Fit every spline model (`SplineTransformer` + `LogisticRegression`/`LinearRegression`) directly on `test_df` — the locked test set — despite a docstring claiming OOF-only fitting | Lines 90–91 loaded `X_test = test_df[...]`; lines 118–201 fit all six spline models per BMI/Age on data derived from `test_df` |
| Prior `src/sens_05_subgroup_recalibration.py` | (a) Mislabeled the raw pre-Platt calibration intercept/slope as the "global_platt" post-recalibration metric; (b) applied a raw-probability-scale Youden threshold to Platt-recalibrated probabilities when computing "subgroup_sensitivity", producing implausible near-zero values | (a) Output showed intercept=−2.2425 for logistic under method="global_platt", matching the independently-verified RAW intercept, not the ≈0 post-Platt value; (b) `y_pred_sg = (test_mixed_recal >= global_thresh)` where `test_mixed_recal` is Platt-scale and `global_thresh` (e.g. 0.5173) is raw-scale |
| Prior `src/sens_06_group_specific_thresholds.py` | Evaluated the "global threshold" baseline using RECALIBRATED test probabilities against a threshold value (e.g. 0.4108) derived for RAW probabilities — a scale mismatch; also omitted the frozen BMI-Underweight category entirely | `test_proba = ... "recalibrated_predicted_probability"` compared against `thresholds_global` sourced from the raw-probability Youden fit; `subgroup_configs` for BMI listed only `["Normal", "Overweight", "Obese"]` |

None of these three defects involved locked-test labels being used to *select* a threshold, knot,
or calibration parameter (i.e., none is a leakage violation in the strict sense) — but each
produces numerically wrong or mislabeled output, which is why this execution treats none of the
prior scripts' outputs as usable, per the explicit user decision to redo from scratch.

## Overall verdict

**No test-set contamination (in the leakage sense: test labels influencing a fitting or
decision-making step) was found in this session's three fresh implementations.** The three defects
found in the pre-existing, superseded scripts are computation/labeling errors, not leakage, and are
documented rather than hidden.
