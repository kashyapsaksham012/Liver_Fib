"""
tests/test_calibration_pipeline.py
Phase 4 Part 30: automated validation of the Calibration pipeline. Standalone script
(project convention, not pytest -- consistent with tests/test_source_of_truth.py and every
Phase 1/3 validation script). Run directly: `python3 tests/test_calibration_pipeline.py`.
Exits 1 if any check fails.
"""
import sys
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase4_common import (
    CALIB_RESULTS_DIR, CALIB_DOC_DIR, CALIB_CURVE_DATA_DIR, PRIMARY_MODELS, SENSITIVITY_MODEL,
    CALIBRATION_PROTOCOL_COMMIT, CALIBRATION_PROTOCOL_CHECKSUM, MODEL_ARTIFACT_FILES,
    MODEL_DIR, load_oof_predictions, load_test_predictions,
)
from phase3_common import PRIMARY_COHORT_N, PRIMARY_OUTCOME_COL, PRIMARY_PREDICTORS

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# TEST 1: Calibration protocol checksum matches frozen protocol
protocol_path = CALIB_DOC_DIR / "CALIBRATION_PROTOCOL_FREEZE.md"
live_checksum = sha256(protocol_path)
check("TEST1_protocol_checksum_matches", live_checksum == CALIBRATION_PROTOCOL_CHECKSUM,
      f"live={live_checksum} expected={CALIBRATION_PROTOCOL_CHECKSUM}")

# TEST 2: Phase 3 model artifact hashes match expected frozen artifacts (recorded in phase4_pre_execution_snapshot.md)
EXPECTED_MODEL_HASHES = {
    "model_logistic_v1.joblib": "ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5",
    "model_random_forest_v1.joblib": "37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a",
    "model_xgboost_v1.joblib": "8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4",
    "model_lightgbm_v1.joblib": "dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02",
    "model_mlp_v1.joblib": "4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc",
    "model_mlp_balanced_v1_sensitivity.joblib": "d89a49e31e401493dd7c1ec8234cf823c386ac518edf9d475a872c6779b5bb9d",
}
for fname, expected in EXPECTED_MODEL_HASHES.items():
    live = sha256(MODEL_DIR / fname)
    check(f"TEST2_model_hash_{fname}", live == expected, f"live={live} expected={expected}")

# TEST 3: input prediction hashes match expected frozen prediction artifacts (recorded in snapshot)
EXPECTED_PRED_HASHES = {
    "validation_predictions_logistic.csv": "f283f1b5ee390973e2d43a7b8bed4562f1f5a9fc0acbae8c41c6acc57ef3f691",
    "validation_predictions_random_forest.csv": "ae446e55cd31f3d3f8f89205d1fcdd158d4e6680a1c98e383bebcc82fdaab723",
    "validation_predictions_xgboost.csv": "4cfa72d64ef4f6f52c0466935646335f209c17eee3488dc1dfa2f73dc9b89abd",
    "validation_predictions_lightgbm.csv": "99496e2270f669942dff18f5c95a49f4b67060fe669e240f7e4c6eb4351bfc5a",
    "validation_predictions_mlp.csv": "b9fe782e60f2db84f1a1e4dadf38c23672d5903b392b01a0b206f2e9bee63f84",
    "test_predictions_logistic.csv": "87fa5df55f55ae749e70205eaab0fb6a57b0650e25fa901a824b15ccd1a8cd45",
    "test_predictions_random_forest.csv": "25088452a18af7c6a88438049fff12b3346db7f9387051245059879bb76f373e",
    "test_predictions_xgboost.csv": "651ef1bcbbd2f36121a26f52508479349b25b526bc7563bef183efc7f5e57e4a",
    "test_predictions_lightgbm.csv": "eb9e7c78a6f3dc1c6854b7b7b6a66be64c0ae4910f7f7b69181d8a13c2d3e1ad",
    "test_predictions_mlp.csv": "a48b0a2d9d6c7c827adbc8e5682f512cf291042d75055c2ec6d33f8395d4bc51",
}
from phase4_common import PRED_DIR
for fname, expected in EXPECTED_PRED_HASHES.items():
    live = sha256(PRED_DIR / fname)
    check(f"TEST3_prediction_hash_{fname}", live == expected, f"live={live} expected={expected}")

# TEST 4: calibration data source matches protocol (OOF = cross_val_predict output; test = frozen best_estimator_ scoring)
flow_doc = (CALIB_DOC_DIR / "phase4_calibration_data_flow.md").read_text()
check("TEST4_data_flow_doc_references_OOF", "out-of-fold" in flow_doc.lower())
check("TEST4_data_flow_doc_excludes_conformal_set", "conformal_calibration_ids.csv" in flow_doc and "not used" in flow_doc.lower())
conformal_refs = []
for f in (ROOT / "src").glob("phase4_*.py"):
    if "conformal_calibration" in f.read_text():
        conformal_refs.append(f.name)
check("TEST4_no_phase4_script_reads_conformal_calibration_set", conformal_refs == [], f"found in: {conformal_refs}")

# TEST 5-9: per-model prediction integrity (duplicate participants, missing, range, target)
for name in PRIMARY_MODELS + [SENSITIVITY_MODEL]:
    for tier, loader in [("OOF", load_oof_predictions), ("test", load_test_predictions)]:
        df = loader(name)
        check(f"TEST5_no_duplicate_participant_{name}_{tier}", df["SEQN"].nunique() == len(df))
        check(f"TEST6_no_missing_predictions_{name}_{tier}", df["predicted_probability"].isna().sum() == 0)
        check(f"TEST7_probabilities_in_0_1_{name}_{tier}", df["predicted_probability"].between(0, 1).all())
        check(f"TEST8_no_nan_inf_{name}_{tier}", not (df["predicted_probability"].isna().any() or np.isinf(df["predicted_probability"]).any()))
        check(f"TEST9_target_matches_frozen_binary_{name}_{tier}", sorted(df["true_target"].dropna().unique().tolist()) == [0, 1])

# TEST 10: no unauthorized test-set use before Part 21 (structural check: only phase4_09 references TEST_PREDICTION_FILE
# for a purpose other than integrity auditing; phase4_01 reads it for integrity-only per phase4_test_set_protection_audit.md)
test_touch_scripts = []
for f in sorted((ROOT / "src").glob("phase4_*.py")):
    src = f.read_text()
    if "load_test_predictions" in src or "TEST_PREDICTION_FILE" in src:
        test_touch_scripts.append(f.name)
non_definitional = [s for s in test_touch_scripts if s != "phase4_common.py"]  # phase4_common.py only DEFINES the path helper, never calls it
check("TEST10_only_expected_scripts_touch_test_predictions",
      set(non_definitional) == {"phase4_01_prediction_input_audit.py", "phase4_09_final_test_set_calibration.py"},
      f"scripts referencing test predictions: {non_definitional}")

# TEST 11: no calibration TRANSFORMATION fitted using prohibited test outcomes. phase4_09 does call
# LogisticRegression.fit() internally (via cal_in_the_large()), but only to MEASURE calibration-in-the-
# large as a reported metric on already-fixed probabilities -- a diagnostic "scoring" computation exactly
# analogous to computing test-set AUC, not a recalibration fit. The actual recalibration TRANSFORM applied
# to the test set uses platt_intercept/platt_slope values -- this test proves those values are identical
# to the ones already committed from the OOF-only fit in Commit A, i.e. no new transform was derived from
# test outcomes.
fit_script = (ROOT / "src" / "phase4_05_recalibration.py").read_text()
check("TEST11_recalibration_fit_script_uses_oof_only", "load_oof_predictions" in fit_script and "load_test_predictions" not in fit_script)
oof_platt = pd.read_csv(CALIB_RESULTS_DIR / "recalibration_pre_post_comparison.csv").set_index("model")[["platt_fit_intercept", "platt_fit_slope"]]
test_recal = pd.read_csv(CALIB_RESULTS_DIR / "test_set_recalibrated_predictions.csv")
test_platt = test_recal.groupby("model")[["platt_intercept", "platt_slope"]].first()
for name in PRIMARY_MODELS:
    check(f"TEST11_test_set_platt_params_match_oof_fit_{name}",
          np.isclose(oof_platt.loc[name, "platt_fit_intercept"], test_platt.loc[name, "platt_intercept"]) and
          np.isclose(oof_platt.loc[name, "platt_fit_slope"], test_platt.loc[name, "platt_slope"]),
          f"OOF-fit=({oof_platt.loc[name,'platt_fit_intercept']},{oof_platt.loc[name,'platt_fit_slope']}) "
          f"vs applied-to-test=({test_platt.loc[name,'platt_intercept']},{test_platt.loc[name,'platt_slope']})")

# TEST 12: five original models represented
primary_metrics = pd.read_csv(CALIB_RESULTS_DIR / "primary_metrics_by_model.csv")
check("TEST12_five_primary_models_represented", sorted(primary_metrics["model"].tolist()) == sorted(PRIMARY_MODELS),
      f"found: {sorted(primary_metrics['model'].tolist())}")

# TEST 13: MLP-balanced sensitivity model not accidentally promoted
check("TEST13_mlp_balanced_excluded_from_primary_metrics_table", SENSITIVITY_MODEL not in primary_metrics["model"].tolist())
brier_df = pd.read_csv(CALIB_RESULTS_DIR / "brier_scores.csv")
sens_rows = brier_df[brier_df["model"] == SENSITIVITY_MODEL]
check("TEST13_mlp_balanced_labeled_sensitivity_where_present",
      (sens_rows["status"] == "SENSITIVITY (MLP_balanced, not primary)").all() if len(sens_rows) else True)
inference_df = pd.read_csv(CALIB_RESULTS_DIR / "calibration_inference.csv")
check("TEST13_mlp_balanced_excluded_from_formal_inference",
      SENSITIVITY_MODEL not in inference_df.get("model", pd.Series(dtype=str)).tolist() and
      SENSITIVITY_MODEL not in inference_df.get("model_a", pd.Series(dtype=str)).tolist() and
      SENSITIVITY_MODEL not in inference_df.get("model_b", pd.Series(dtype=str)).tolist())

# TEST 14: primary/secondary metric labels match protocol (intercept/slope/Brier = primary; curve/ECE = secondary)
check("TEST14_primary_metrics_file_contains_intercept_slope_brier",
      {"calibration_intercept", "calibration_slope"}.issubset(primary_metrics.columns) and "brier_score" in brier_df.columns)
ece_df = pd.read_csv(CALIB_RESULTS_DIR / "ece_secondary_metric.csv")
check("TEST14_ece_file_labeled_secondary", "ece_secondary_metric" in ece_df.columns)

# TEST 15: calibration curves have corresponding underlying data
fig_files = set(f.stem.replace("calibration_curve_", "") for f in (CALIB_RESULTS_DIR / "figures").glob("*.png"))
curve_data_files = set(f.stem.replace("curve_data_", "") for f in CALIB_CURVE_DATA_DIR.glob("curve_data_*.csv") if f.stem not in ("curve_data_all_models", "curve_data_test_set_final"))
check("TEST15_every_figure_has_curve_data", fig_files.issubset(curve_data_files), f"figures without data: {fig_files - curve_data_files}")

# TEST 16: raw Phase 3 predictions remain unchanged (re-hash against the same expected values as TEST 3 -- if TEST 3
# passed, this is definitionally true; re-stated as its own check per Part 30's explicit numbering)
check("TEST16_raw_phase3_predictions_unchanged", all(sha256(PRED_DIR / f) == h for f, h in EXPECTED_PRED_HASHES.items()))

# TEST 17: all primary Calibration metrics are traceable to saved artifacts (files exist and are non-empty)
for fname in ["primary_metrics_by_model.csv", "brier_scores.csv", "calibration_inference.csv", "test_set_calibration_final.csv"]:
    p = CALIB_RESULTS_DIR / fname
    check(f"TEST17_artifact_exists_and_nonempty_{fname}", p.exists() and p.stat().st_size > 0)

# TEST 18: no Phase 1/2 frozen definition changed
check("TEST18_primary_cohort_n_unchanged", PRIMARY_COHORT_N == 7153)
check("TEST18_primary_outcome_col_unchanged", PRIMARY_OUTCOME_COL == "outcome_primary_8.2kPa")
check("TEST18_primary_predictors_unchanged", PRIMARY_PREDICTORS == ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI",
      "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"])

# TEST 19: no Phase 5/6 analysis accidentally executed
forbidden_dirs = [ROOT / "results" / "fairness", ROOT / "results" / "uncertainty", ROOT / "results" / "conformal"]
existing_forbidden = [str(d) for d in forbidden_dirs if d.exists()]
check("TEST19_no_fairness_or_uncertainty_output_dirs", existing_forbidden == [], f"found: {existing_forbidden}")
subgroup_calib_files = list(CALIB_RESULTS_DIR.glob("*subgroup*")) + list(CALIB_RESULTS_DIR.glob("*fairness*"))
check("TEST19_no_subgroup_calibration_output", subgroup_calib_files == [], f"found: {subgroup_calib_files}")
conformal_refit_files = list((ROOT / "models" / "phase3").glob("*proper_train*")) + list((ROOT / "results" / "predictions").glob("*conformal*"))
check("TEST19_no_conformal_refit_artifacts", conformal_refit_files == [], f"found: {conformal_refit_files}")

# TEST 20: final report values are code-derived -- spot-check headline claims against the saved CSVs directly
# (report is generated after this test suite runs, per the execution order; this test validates that the
# specific numbers this suite's own summary will cite are the exact values present in the artifacts, not
# independently-typed prose)
pm = primary_metrics.set_index("model")
check("TEST20_logistic_intercept_matches_artifact", abs(pm.loc["logistic", "calibration_intercept"] - (-2.242509)) < 1e-4)
check("TEST20_mlp_intercept_matches_artifact", abs(pm.loc["mlp", "calibration_intercept"] - (-0.280858)) < 1e-4)
tscf = pd.read_csv(CALIB_RESULTS_DIR / "test_set_calibration_final.csv").set_index(["model", "variant"])
check("TEST20_logistic_test_raw_intercept_matches_artifact",
      abs(tscf.loc[("logistic", "raw"), "calibration_intercept"] - (-2.260225)) < 1e-4)
check("TEST20_logistic_test_recal_brier_matches_artifact",
      abs(tscf.loc[("logistic", "recalibrated"), "brier_score"] - 0.070538) < 1e-4)

print(f"\n{'='*70}\nCALIBRATION PIPELINE TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
print(f"\n({len(PASS)} PASS lines omitted for brevity; re-run with -v flag equivalent by editing this script if needed)")

if FAIL:
    sys.exit(1)
print("\nALL 20 TEST CATEGORIES PASSED.")
sys.exit(0)
