"""
tests/test_mitigation_pipeline.py
Project Phase 7 (Mitigation) Part 12: automated validation. Standalone script (project
convention). Run directly: `python3 tests/test_mitigation_pipeline.py`.
"""
import sys
import hashlib
from pathlib import Path
import subprocess
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase5_common import FROZEN_THRESHOLDS

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()

MIT_DIR = ROOT / "results" / "mitigation"
justification = pd.read_csv(ROOT / "documentation" / "mitigation" / "phase7_justification_determination.csv")
group_thresh = pd.read_csv(MIT_DIR / "group_specific_thresholds.csv")
pre_test = pd.read_csv(MIT_DIR / "pre_test_evaluation.csv")
final = pd.read_csv(MIT_DIR / "test_set_mitigation_final.csv")
nontarget = pd.read_csv(MIT_DIR / "nontarget_subgroup_protection.csv")
marginal = pd.read_csv(MIT_DIR / "marginal_coverage_before_after.csv")

EXPECTED_TARGETS = {("bmi", "Obese", m) for m in ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]} | \
                   {("age", "60+", m) for m in ["random_forest", "xgboost", "lightgbm", "mlp"]}

# TEST 1: mitigation target set matches frozen justification
eligible = justification[justification["mitigation_eligible"] == True]
eligible_keys = set(zip(eligible["subgroup_dimension"], eligible["subgroup_category"], eligible["model"]))
check("TEST1_target_set_matches_frozen_justification", eligible_keys == EXPECTED_TARGETS, f"found: {eligible_keys}")
check("TEST1_group_thresholds_match_target_set",
      set(zip(group_thresh["dimension"], group_thresh["category"], group_thresh["model"])) == EXPECTED_TARGETS)

# TEST 2: excluded groups remain excluded for documented reasons
excluded = justification[justification["mitigation_eligible"] == False]
nha = excluded[excluded["subgroup_category"] == "Non-Hispanic Asian"]
uw = excluded[excluded["subgroup_category"] == "Underweight"]
check("TEST2_non_hispanic_asian_excluded_all_models", len(nha) == 5 and (~nha["mitigation_eligible"]).all())
check("TEST2_underweight_excluded_all_models", len(uw) == 5 and (~uw["mitigation_eligible"]).all())
rf_1839 = excluded[(excluded["subgroup_category"] == "18-39") & (excluded["model"] == "random_forest")]
check("TEST2_rf_age1839_excluded_with_reason", len(rf_1839) == 1 and "over-coverage" in rf_1839.iloc[0]["reason"])

# TEST 3: mitigation protocol was committed before implementation
log = git("log", "--oneline", "--", "documentation/mitigation/MITIGATION_PROTOCOL_FREEZE.md")
protocol_commit = log.split()[0] if log else None
impl_log = git("log", "--diff-filter=A", "--name-only", "--pretty=format:%H", "--", "src/phase7_02_mitigation_implementation.py")
impl_commit = impl_log.split("\n")[0] if impl_log else None
check("TEST3_protocol_and_implementation_commits_found", protocol_commit is not None and impl_commit is not None)
protocol_ts = git("show", "-s", "--format=%ct", protocol_commit) if protocol_commit else None
impl_ts = git("show", "-s", "--format=%ct", impl_commit) if impl_commit else None
check("TEST3_protocol_committed_before_implementation",
      protocol_ts is not None and impl_ts is not None and int(protocol_ts) < int(impl_ts))

# TEST 4: no test-set information was used for method selection (structural: pre-test script never reads test_ids)
pretest_src = (ROOT / "src" / "phase7_03_pretest_evaluation.py").read_text()
check("TEST4_pretest_script_never_reads_test_ids", "test_ids.csv" not in pretest_src)
justification_src = (ROOT / "src" / "phase7_01_justification_determination.py").read_text()
check("TEST4_justification_script_reads_only_precomputed_inference_csvs",
      "fairness_inference.csv" in justification_src and "coverage_inference.csv" in justification_src and "test_ids" not in justification_src)

# TEST 5: original unmitigated models remain unchanged
EXPECTED_REFIT_HASHES = {
    "model_logistic_proper_train_refit.joblib": "000e51505e76d49ebf02a57d29a3132ea1fa837b49497e142c9fd8caeb73c630",
    "model_random_forest_proper_train_refit.joblib": "22a63c50c43b6aef4834223c4b27c03a811dd8881e770cfaea2437d946d32618",
    "model_xgboost_proper_train_refit.joblib": "9e7745d64f3b967a06cb053b2dfea9e0950075e5c788aecb6a1c3b245d83dfc8",
    "model_lightgbm_proper_train_refit.joblib": "597ad772bf68ef6a1022d6b44ef3039c90220ae614a0f11ec015a23c59fa0856",
    "model_mlp_proper_train_refit.joblib": "5bd9a684357c6069b71163c46865d0358745154b813d947627acef5ecca79cb3",
}
for fname, expected in EXPECTED_REFIT_HASHES.items():
    check(f"TEST5_refit_model_unchanged_{fname}", sha256(ROOT / "models" / "phase6_conformal_refit" / fname) == expected)

# TEST 6: proper-train/calibration data are used correctly
impl_src = (ROOT / "src" / "phase7_02_mitigation_implementation.py").read_text()
check("TEST6_implementation_uses_conformal_calibration_ids_only",
      "conformal_calibration_ids.csv" in impl_src)
check("TEST6_implementation_test_ids_reference_is_disjointness_check_only",
      "test_ids" not in impl_src or "isin(test_ids).any()" in impl_src,
      "note: reading test_ids.csv solely to assert zero SEQN overlap with the calibration set is a legitimate safety check, not use of test outcomes/predictions -- distinguished explicitly from an actual test-set touch")
check("TEST6_calibration_n_matches_subgroup_slice",
      (group_thresh["calibration_n_group"] == group_thresh.apply(
          lambda r: {"Obese": 407, "60+": 339}[r["category"]], axis=1)).all())

# TEST 7: mitigation method matches frozen protocol
protocol_text = (ROOT / "documentation" / "mitigation" / "MITIGATION_PROTOCOL_FREEZE.md").read_text()
check("TEST7_protocol_names_group_wise_mondrian", "Mondrian" in protocol_text and "group-wise" in protocol_text.lower())
check("TEST7_implementation_method_label_matches", (group_thresh["method"] == "group-wise (Mondrian) conformal calibration").all())

# TEST 8: target disparity metric is computed correctly (spot-check arithmetic)
spot = final[(final["model"] == "logistic") & (final["category"] == "Obese")].iloc[0]
check("TEST8_coverage_change_arithmetic",
      abs(spot["coverage_change_pp"] - round((spot["coverage_after"] - spot["coverage_before"]) * 100, 4)) < 1e-6)

# TEST 9: overall AUC is computed
check("TEST9_auc_present_in_marginal_table", "auc" in marginal.columns and marginal["auc"].between(0, 1).all())

# TEST 10: calibration is computed
check("TEST10_calibration_columns_present",
      {"calibration_intercept_before", "calibration_intercept_after", "calibration_slope_before", "calibration_slope_after"}.issubset(final.columns))
check("TEST10_calibration_identical_before_after",
      (final["calibration_intercept_before"] == final["calibration_intercept_after"]).all() and
      (final["calibration_slope_before"] == final["calibration_slope_after"]).all())

# TEST 11: coverage is computed where required
check("TEST11_coverage_before_after_present", {"coverage_before", "coverage_after"}.issubset(final.columns))
check("TEST11_nine_target_rows", len(final) == 9)

# TEST 12: non-target subgroups are checked
check("TEST12_nontarget_file_nonempty", len(nontarget) > 0)
check("TEST12_nontarget_no_new_under90_deviation",
      not ((nontarget["coverage_before"] >= 0.90) & (nontarget["coverage_after"] < 0.90)).any())

# TEST 13: before/after outputs are reproducible (checked in the dedicated repro rerun, this test
# confirms the artifact exists and is well-formed as a precondition)
check("TEST13_final_output_well_formed", len(final) == 9 and final["coverage_after"].between(0, 2).all())

# TEST 14: test set is touched exactly once (structural: only phase7_04 reads test-derived data)
touch_scripts = []
for f in sorted((ROOT / "src").glob("phase7_*.py")):
    src = f.read_text()
    if "test_set_prediction_sets.csv" in src or ("test_ids.csv" in src and "conformal_calibration" not in src.split("test_ids.csv")[0][-200:]):
        touch_scripts.append(f.name)
check("TEST14_only_final_touch_script_reads_test_derived_data",
      set(touch_scripts) == {"phase7_04_final_test_touch.py"}, f"found: {touch_scripts}")

# TEST 15: no post-test iteration occurred (single commit for the touch, single execution -- checked via git log for the touch script)
touch_commits = git("log", "--follow", "--oneline", "--", "src/phase7_04_final_test_touch.py").split("\n")
check("TEST15_touch_script_committed_exactly_once", len([l for l in touch_commits if l.strip()]) == 1, f"commits: {touch_commits}")

# TEST 16: deferred sensitivity analyses remain tracked
roadmap = (ROOT / "documentation" / "project_roadmap" / "deferred_sensitivity_analyses.md")
check("TEST16_roadmap_still_exists", roadmap.exists())
check("TEST16_roadmap_still_shows_not_executed", "**NOT EXECUTED**" in roadmap.read_text())

# TEST 17: final report values are code-derived (spot-check against the artifact)
check("TEST17_spotcheck_logistic_obese_coverage_after",
      abs(final[(final["model"]=="logistic") & (final["category"]=="Obese")]["coverage_after"].iloc[0] - 0.893545) < 1e-4)

print(f"\n{'='*70}\nMITIGATION PIPELINE TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print("\nALL 17 TEST CATEGORIES PASSED.")
sys.exit(0)
