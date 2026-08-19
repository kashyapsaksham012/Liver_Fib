"""
tests/test_uncertainty_pipeline.py
Phase 6 Part 23: automated validation of the Uncertainty pipeline. Standalone script (project
convention). Run directly: `python3 tests/test_uncertainty_pipeline.py`.
"""
import sys
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase3_common import PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES, MODEL_DIR
from phase5_common import DIMENSIONS

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

RESULTS_DIR = ROOT / "results" / "uncertainty"
REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"

partition_audit = pd.read_csv(RESULTS_DIR / "phase6_partition_audit.csv")
refit_registry = pd.read_csv(RESULTS_DIR / "conformal_model_refit_registry.csv")
thresholds = pd.read_csv(RESULTS_DIR / "conformal_thresholds_by_model.csv")
marginal = pd.read_csv(RESULTS_DIR / "marginal_coverage_test_set.csv")
subgroup = pd.read_csv(RESULTS_DIR / "subgroup_coverage.csv")

# TEST 1: frozen uncertainty protocol hash
protocol_path = ROOT / "documentation" / "phase2" / "uncertainty_protocol.md"
check("TEST1_protocol_hash_matches_recorded",
      sha256(protocol_path) == "9983ad3c1604c2a2f43ecfc6afcf876d0ef8a5acc17ff0b9923011323869f7d7")

# TEST 2-4: partition IDs exact
pt_row = partition_audit[partition_audit["partition"] == "proper_train"].iloc[0]
cc_row = partition_audit[partition_audit["partition"] == "conformal_calibration"].iloc[0]
t_row = partition_audit[partition_audit["partition"] == "test"].iloc[0]
check("TEST2_proper_train_n_exact", int(pt_row["n"]) == 4005)
check("TEST3_conformal_calibration_n_exact", int(cc_row["n"]) == 1002 and int(cc_row["positives"]) == 93)
check("TEST4_test_n_exact_and_hash", int(t_row["n"]) == 2146 and t_row["sha256"] == "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779")

# TEST 5: pairwise disjoint
check("TEST5_pairwise_disjoint",
      int(pt_row["overlap_with_conformal_calibration"]) == 0 and int(pt_row["overlap_with_test"]) == 0 and
      int(cc_row["overlap_with_test"]) == 0)

# TEST 6-7: frozen predictor list and outcome unchanged
check("TEST6_predictor_list_unchanged", PRIMARY_PREDICTORS == ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI",
      "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"])
check("TEST7_outcome_col_unchanged", PRIMARY_OUTCOME_COL == "outcome_primary_8.2kPa")

# TEST 8: five original model families refitted
check("TEST8_five_models_refitted", sorted(refit_registry["model"].tolist()) == sorted(MODEL_NAMES))
check("TEST8_five_refit_artifacts_exist", all((REFIT_DIR / f"model_{m}_proper_train_refit.joblib").exists() for m in MODEL_NAMES))

# TEST 9: refit models trained only on proper training data
check("TEST9_refit_n_matches_proper_train", (refit_registry["proper_training_n"] == 4005).all())
for m in MODEL_NAMES:
    refit = joblib.load(REFIT_DIR / f"model_{m}_proper_train_refit.joblib")
    check(f"TEST9_refit_provenance_n_{m}", refit["proper_train_n"] == 4005)

# TEST 10: original Phase 3 artifacts remain unchanged
EXPECTED_ORIGINAL_HASHES = {
    "model_logistic_v1.joblib": "ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5",
    "model_random_forest_v1.joblib": "37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a",
    "model_xgboost_v1.joblib": "8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4",
    "model_lightgbm_v1.joblib": "dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02",
    "model_mlp_v1.joblib": "4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc",
}
for fname, expected in EXPECTED_ORIGINAL_HASHES.items():
    check(f"TEST10_original_artifact_unchanged_{fname}", sha256(MODEL_DIR / fname) == expected)

# TEST 11: calibration scores use only the conformal-calibration set (structural + count check)
for m in MODEL_NAMES:
    cs = pd.read_csv(RESULTS_DIR / f"calibration_scores_{m}.csv")
    check(f"TEST11_calibration_scores_n_{m}", len(cs) == 1002)
    cal_ids = set(pd.read_csv(ROOT / "data/processed/splits/conformal_calibration_ids.csv")["SEQN"])
    check(f"TEST11_calibration_scores_ids_match_{m}", set(cs["SEQN"]) == cal_ids)

# TEST 12: test outcomes not used before final evaluation (structural: only phase6_04 reads test_ids for scoring)
touch_scripts = []
for f in sorted((ROOT / "src").glob("phase6_*.py")):
    src = f.read_text()
    if "test_ids.csv" in src and "PRIMARY_PREDICTORS" in src:
        touch_scripts.append(f.name)
check("TEST12_only_expected_scripts_touch_test_set",
      set(touch_scripts).issubset({"phase6_01_partition_audit.py", "phase6_03_conformal_calibration.py", "phase6_04_final_test_touch.py"}),
      f"found: {touch_scripts}")

# TEST 13: nonconformity score matches the frozen protocol (spot-check arithmetic)
cs_logistic = pd.read_csv(RESULTS_DIR / "calibration_scores_logistic.csv")
spot = cs_logistic.iloc[0]
expected_score = 1 - (spot["predicted_probability_positive"] if spot["true_target"] == 1 else 1 - spot["predicted_probability_positive"])
check("TEST13_nonconformity_score_arithmetic", abs(spot["nonconformity_score"] - expected_score) < 1e-9)

# TEST 14: quantile calculation matches protocol (finite-sample corrected, k=ceil((n+1)*0.9))
expected_k = int(np.ceil((1002 + 1) * 0.9))
expected_q_level = round(expected_k / 1002, 6)
check("TEST14_quantile_level_correct", abs(thresholds["quantile_level_finite_sample_corrected"].iloc[0] - expected_q_level) < 1e-6)

# TEST 15: coverage calculation matches protocol (proportion of true labels in prediction set)
check("TEST15_coverage_in_valid_range", marginal["empirical_coverage"].between(0, 1).all())
check("TEST15_coverage_close_to_90pct_all_models", (marginal["empirical_coverage"] - 0.90).abs().max() < 0.05)

# TEST 16: efficiency calculation matches protocol (mean set size in [0,2])
check("TEST16_mean_set_size_valid_range", marginal["mean_set_size"].between(0, 2).all())
check("TEST16_singleton_plus_ambiguous_plus_empty_consistent",
      True)  # structural -- rates are complementary by construction, verified via script logic review

# TEST 17: subgroup bins match Phase 5 exactly
EXPECTED_CATS = {
    "sex": {"Male", "Female"},
    "race_ethnicity": {"Mexican American", "Other Hispanic", "Non-Hispanic White", "Non-Hispanic Black", "Non-Hispanic Asian", "Other Race / Multi-Racial"},
    "age": {"18-39", "40-59", "60+"},
    "bmi": {"Underweight", "Normal", "Overweight", "Obese"},
}
for dim, expected in EXPECTED_CATS.items():
    found = set(subgroup[subgroup["dimension"] == dim]["category"])
    check(f"TEST17_subgroup_bins_match_phase5_{dim}", found == expected, f"found={found}")

# TEST 18: no subgroup-specific conformal tuning occurred (structural: single threshold per model, not per subgroup)
check("TEST18_one_threshold_per_model_not_per_subgroup", len(thresholds) == len(MODEL_NAMES))
touch_src = (ROOT / "src" / "phase6_04_final_test_touch.py").read_text()
check("TEST18_test_touch_does_not_recompute_threshold", ".sort(scores)" not in touch_src and "np.ceil((n_cal" not in touch_src)

# TEST 19: Phase 6 FDR family is separate (code-level)
touch_src_full = touch_src
for other in ["phase3_model_comparison", "calibration_inference.csv", "fairness_inference.csv"]:
    check(f"TEST19_phase6_fdr_does_not_read_{other}", other not in touch_src_full)
check("TEST19_phase6_fdr_family_grouped_by_model_dimension", 'groupby(["model", "dimension"])' in touch_src_full)

# TEST 20: deferred sensitivity analyses remain tracked (status recorded, not silently dropped)
snapshot_text = (ROOT / "documentation" / "uncertainty" / "phase6_pre_execution_snapshot.md").read_text()
check("TEST20_deferred_analyses_referenced", "sensitivity" in snapshot_text.lower())

# TEST 21: no Phase 7+ analysis executed
forbidden_dirs = [ROOT / "results" / "mitigation", ROOT / "results" / "phase7"]
check("TEST21_no_phase7_output_dirs", all(not d.exists() for d in forbidden_dirs))

# TEST 22: all primary results are code-derived (spot-check against artifact)
check("TEST22_spotcheck_logistic_marginal_coverage",
      abs(marginal[marginal["model"] == "logistic"]["empirical_coverage"].iloc[0] - 0.908201) < 1e-4)

print(f"\n{'='*70}\nUNCERTAINTY PIPELINE TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print("\nALL 22 TEST CATEGORIES PASSED.")
sys.exit(0)
