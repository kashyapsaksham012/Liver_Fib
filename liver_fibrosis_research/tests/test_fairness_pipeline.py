"""
tests/test_fairness_pipeline.py
Phase 5 Part 23: automated validation of the Fairness pipeline. Standalone script (project
convention). Run directly: `python3 tests/test_fairness_pipeline.py`. Exits 1 if any check
fails.
"""
import sys
import re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase5_common import (
    FAIR_RESULTS_DIR, DIMENSIONS, PRIMARY_MODELS, FROZEN_THRESHOLDS,
    RACE_MAP_RIDRETH3, SEX_MAP, precision_tier,
)
from phase3_common import PRIMARY_PREDICTORS, PRIMARY_COHORT_N, PRIMARY_OUTCOME_COL

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))

feas = pd.read_csv(FAIR_RESULTS_DIR / "subgroup_feasibility_table.csv")
disc = pd.read_csv(FAIR_RESULTS_DIR / "subgroup_discrimination_metrics.csv")
calib = pd.read_csv(FAIR_RESULTS_DIR / "subgroup_calibration_metrics.csv")
infer = pd.read_csv(FAIR_RESULTS_DIR / "fairness_inference.csv")
inter = pd.read_csv(FAIR_RESULTS_DIR / "intersectional_exploratory_metrics.csv")

# TEST 1: subgroups match frozen protocol (exact category sets per dimension)
EXPECTED_CATS = {
    "sex": {"Male", "Female"},
    "race_ethnicity": {"Mexican American", "Other Hispanic", "Non-Hispanic White", "Non-Hispanic Black", "Non-Hispanic Asian", "Other Race / Multi-Racial"},
    "age": {"18-39", "40-59", "60+"},
    "bmi": {"Underweight", "Normal", "Overweight", "Obese"},
}
full = feas[feas["population"] == "full_primary_cohort"]
for dim, expected in EXPECTED_CATS.items():
    found = set(full[full["dimension"] == dim]["category"])
    check(f"TEST1_subgroups_match_protocol_{dim}", found == expected, f"found={found}")

# TEST 2: race/ethnicity collapsing rule matches (RIDRETH3, 6 categories, Non-Hispanic Asian preserved)
check("TEST2_ridreth3_six_categories_used", len(RACE_MAP_RIDRETH3) == 6)
check("TEST2_non_hispanic_asian_preserved", "Non-Hispanic Asian" in RACE_MAP_RIDRETH3.values())

# TEST 3: no subgroup modification (live-recomputed full-cohort counts match frozen doc exactly)
EXPECTED_FULL_COHORT = {
    ("sex", "Male"): 3531, ("sex", "Female"): 3622,
    ("race_ethnicity", "Mexican American"): 902, ("race_ethnicity", "Other Hispanic"): 754,
    ("race_ethnicity", "Non-Hispanic White"): 2484, ("race_ethnicity", "Non-Hispanic Black"): 1787,
    ("race_ethnicity", "Non-Hispanic Asian"): 866, ("race_ethnicity", "Other Race / Multi-Racial"): 360,
    ("age", "18-39"): 2423, ("age", "40-59"): 2318, ("age", "60+"): 2412,
    ("bmi", "Underweight"): 109, ("bmi", "Normal"): 1802, ("bmi", "Overweight"): 2316, ("bmi", "Obese"): 2926,
}
full_idx = full.set_index(["dimension", "category"])
for (dim, cat), exp_n in EXPECTED_FULL_COHORT.items():
    check(f"TEST3_no_modification_{dim}_{cat}", int(full_idx.loc[(dim, cat), "n"]) == exp_n)

# TEST 4: demographic variables exist
check("TEST4_demographic_cols_used", all(spec["col"] in ["RIAGENDR", "RIDRETH3", "RIDAGEYR", "BMXBMI"] for spec in DIMENSIONS.values()))

# TEST 5: participant IDs unique (checked at feasibility-table-generation time; re-verify source)
demo_check = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
check("TEST5_participant_ids_unique", demo_check["SEQN"].nunique() == len(demo_check) == PRIMARY_COHORT_N)

# TEST 6: five original models included
check("TEST6_five_models_in_discrimination", sorted(disc["model"].unique()) == sorted(PRIMARY_MODELS))
check("TEST6_five_models_in_calibration", sorted(calib["model"].unique()) == sorted(PRIMARY_MODELS))
check("TEST6_five_models_in_inference", sorted(infer["model"].unique()) == sorted(PRIMARY_MODELS))

# TEST 7: MLP-balanced remains sensitivity-only (never appears in any Phase 5 primary output)
for df_name, df in [("discrimination", disc), ("calibration", calib), ("inference", infer), ("intersectional", inter)]:
    check(f"TEST7_mlp_balanced_absent_from_{df_name}", "mlp_balanced" not in df["model"].unique())

# TEST 8: frozen thresholds used (spot-check against source constant, and against phase3 table)
p3_table = pd.read_csv(ROOT / "results" / "tables" / "phase3_overall_discrimination.csv").set_index("model_name")["threshold"]
for m in PRIMARY_MODELS:
    check(f"TEST8_frozen_threshold_matches_phase3_{m}", abs(FROZEN_THRESHOLDS[m] - p3_table.loc[m]) < 1e-6)
check("TEST8_discrimination_file_records_threshold_used",
      set(disc["frozen_threshold"].unique()) == set(FROZEN_THRESHOLDS.values()))

# TEST 9: no subgroup-specific threshold optimization (structural: no script computes a new threshold)
for f in (ROOT / "src").glob("phase5_*.py"):
    src = f.read_text()
    check(f"TEST9_no_threshold_optimization_in_{f.name}",
          "youdens_j" not in src.lower() and ".optimize(" not in src and "roc_curve(" not in src)

# TEST 10: fairness metrics match protocol (sensitivity primary; AUC/specificity/FNR/FPR/calib secondary; no PPV/NPV)
check("TEST10_discrimination_metrics_match_frozen_list",
      set(disc.columns).issuperset({"roc_auc", "sensitivity", "specificity", "fnr", "fpr"}))
check("TEST10_no_ppv_npv_columns", "ppv" not in disc.columns and "npv" not in disc.columns)
check("TEST10_calibration_metrics_match_frozen_list",
      set(calib.columns).issuperset({"calibration_intercept", "calibration_slope"}))

# TEST 11: reference groups match protocol
EXPECTED_REFS = {"sex": "Male", "race_ethnicity": "Non-Hispanic White", "age": "40-59", "bmi": "Normal"}
for dim, ref in EXPECTED_REFS.items():
    check(f"TEST11_reference_group_{dim}", DIMENSIONS[dim]["reference"] == ref)
    ref_rows = infer[(infer["dimension"] == dim)]["reference_group"].unique()
    check(f"TEST11_reference_group_used_in_inference_{dim}", list(ref_rows) == [ref] if len(ref_rows) else True)

# TEST 12: absolute/relative disparity calculations are correct (spot-check one row against raw sensitivity values)
spot = infer[(infer["model"] == "logistic") & (infer["dimension"] == "sex") & (infer["category"] == "Female")]
if len(spot):
    row = spot.iloc[0]
    check("TEST12_absolute_disparity_arithmetic_correct",
          abs(float(row["absolute_disparity_pp"]) - 100 * (float(row["subgroup_sensitivity"]) - float(row["reference_sensitivity"]))) < 1e-6)

# TEST 13: Phase 5 FDR family is separate from Phase 3 and Phase 4 (code-level)
phase5_inf_src = (ROOT / "src" / "phase5_04_inference.py").read_text()
check("TEST13_phase5_never_reads_phase3_comparison_table", "phase3_model_comparison" not in phase5_inf_src)
check("TEST13_phase5_never_reads_phase4_inference_table", "calibration_inference.csv" not in phase5_inf_src)
check("TEST13_phase5_has_own_per_model_dimension_family_reset", "family_pvals = []" in phase5_inf_src)

# TEST 14: precision-limited subgroups flagged
check("TEST14_precision_tier_column_present_feasibility", "precision_tier" in feas.columns)
check("TEST14_precision_tier_column_present_discrimination", "precision_tier" in disc.columns)
check("TEST14_precision_tier_column_present_inference", "precision_tier" in infer.columns)
check("TEST14_insufficient_evidence_tier_present_somewhere",
      (feas["precision_tier"] == "insufficient evidence").any())

# TEST 15: degenerate groups marked NOT COMPUTABLE (structural check -- code path exists, even if not triggered this run)
disc_src = (ROOT / "src" / "phase5_02_subgroup_discrimination.py").read_text()
check("TEST15_not_computable_path_exists", "NOT COMPUTABLE" in disc_src)

# TEST 16: no unauthorized intersectional analysis (only the pre-specified 26 cells, no invented ones)
check("TEST16_intersectional_row_count_matches_26_cells_x_5_models", len(inter) == 26 * len(PRIMARY_MODELS))
check("TEST16_intersectional_labeled_exploratory", (inter["label"].str.contains("EXPLORATORY")).all())
allowed_intersections = {"Sex x Race/Ethnicity", "Sex x Age", "Sex x BMI"}
check("TEST16_only_prespecified_intersection_types", set(inter["intersection"].unique()) == allowed_intersections)

# TEST 17: no mitigation performed (no thresholds changed, no group-specific recalibration files)
mitigation_files = list(FAIR_RESULTS_DIR.glob("*mitigat*")) + list(FAIR_RESULTS_DIR.glob("*reweight*"))
check("TEST17_no_mitigation_artifacts", mitigation_files == [], f"found: {mitigation_files}")

# TEST 18: selection-bias analysis remains separate (no script recomputes or alters the Phase 2 missing-data finding)
for f in (ROOT / "src").glob("phase5_*.py"):
    check(f"TEST18_no_missing_data_protocol_recomputation_in_{f.name}", "missing_data_protocol" not in f.read_text())

# TEST 19: test-set use follows protocol (only phase5_02/03/04/05/06 touch test_predictions; phase5_01 does not score models)
touch_scripts = []
for f in sorted((ROOT / "src").glob("phase5_*.py")):
    if "PRED_DIR" in f.read_text() and "test_predictions" in f.read_text():
        touch_scripts.append(f.name)
check("TEST19_test_predictions_only_touched_by_expected_scripts",
      set(touch_scripts) == {"phase5_02_subgroup_discrimination.py", "phase5_03_subgroup_calibration.py",
                              "phase5_04_inference.py", "phase5_05_intersectional.py"},
      f"found: {touch_scripts}")

# TEST 20: results are code-derived (spot-check a headline value against the artifact)
check("TEST20_spotcheck_logistic_male_sensitivity",
      abs(disc[(disc["model"] == "logistic") & (disc["dimension"] == "sex") & (disc["category"] == "Male")]["sensitivity"].astype(float).iloc[0] - 0.762295) < 1e-4)

# TEST 21: figures have underlying data
fig_files = list((FAIR_RESULTS_DIR / "figures").glob("*.png"))
curve_data_file = FAIR_RESULTS_DIR / "curve_data" / "sensitivity_disparity_plot_data.csv"
check("TEST21_figures_exist", len(fig_files) == len(PRIMARY_MODELS))
check("TEST21_figure_underlying_data_exists", curve_data_file.exists())

# TEST 22: Phase 1-4 frozen artifacts unchanged (hash re-check against Phase 4/5-snapshot-recorded values)
import hashlib
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
EXPECTED_MODEL_HASHES = {
    "model_logistic_v1.joblib": "ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5",
    "model_random_forest_v1.joblib": "37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a",
    "model_xgboost_v1.joblib": "8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4",
    "model_lightgbm_v1.joblib": "dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02",
    "model_mlp_v1.joblib": "4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc",
}
for fname, expected in EXPECTED_MODEL_HASHES.items():
    check(f"TEST22_model_artifact_unchanged_{fname}", sha256(ROOT / "models" / "phase3" / fname) == expected)
check("TEST22_test_ids_hash_unchanged",
      sha256(ROOT / "data" / "processed" / "splits" / "test_ids.csv") == "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779")

# TEST 23: Phase 5 scripts do not write into any downstream-phase output tree, and contain no
# conformal reference (forward-leakage guard). The original "results/uncertainty must not exist"
# form is obsolete now that Phase 6+ and Amendments #13-19 have run; the structural guarantee it
# proxied is checked directly here and is stable regardless of downstream execution.
downstream = ("results/uncertainty", "results/conformal", "results\\uncertainty", "results\\conformal")
phase5_writes_downstream = [
    f.name for f in sorted((ROOT / "src").glob("phase5_*.py"))
    if any(d in f.read_text() for d in downstream)
]
check("TEST23_phase5_scripts_do_not_write_downstream_trees",
      phase5_writes_downstream == [], f"found: {phase5_writes_downstream}")
for f in sorted((ROOT / "src").glob("phase5_*.py")):
    check(f"TEST23_no_conformal_reference_in_{f.name}", "conformal" not in f.read_text().lower())

print(f"\n{'='*70}\nFAIRNESS PIPELINE TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print("\nALL 23 TEST CATEGORIES PASSED.")
sys.exit(0)
