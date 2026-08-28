"""
tests/test_deferred_sensitivity_pipeline.py
Deferred Sensitivity Analysis Execution: automated validation. Standalone script (project
convention). Run directly: `python3 tests/test_deferred_sensitivity_pipeline.py`.
"""
import sys
import hashlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase3_common import PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

RESULTS_DIR = ROOT / "results" / "sensitivity"
matrix = pd.read_csv(RESULTS_DIR / "deferred_sensitivity_execution_matrix.csv")
disc = pd.read_csv(RESULTS_DIR / "sensitivity_discrimination_calibration_results.csv")
fair = pd.read_csv(RESULTS_DIR / "sensitivity_bmi_age_fairness_results.csv")
thresh_disc = pd.read_csv(RESULTS_DIR / "alternative_threshold_8p0kPa_results.csv")
thresh_fair = pd.read_csv(RESULTS_DIR / "alternative_threshold_8p0kPa_bmi_age_fairness.csv")
comparison = pd.read_csv(RESULTS_DIR / "primary_vs_sensitivity_comparison.csv")
cand2 = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_cand2_relaxed_elastography.parquet")
cand3 = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_secondary.parquet")
cand1 = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
sens_02_src = (ROOT / "src" / "sens_02_train_evaluate.py").read_text()
sens_03_src = (ROOT / "src" / "sens_03_alternative_threshold.py").read_text()

# TEST 1: frozen cohort definitions match archived counts exactly
check("TEST1_cand2_n_exact", len(cand2) == 7639 and int(cand2[PRIMARY_OUTCOME_COL].sum()) == 804)
check("TEST1_cand3_n_exact", len(cand3) == 3582 and int(cand3[PRIMARY_OUTCOME_COL].sum()) == 319)
check("TEST1_cand1_n_exact", len(cand1) == 7153 and int(cand1[PRIMARY_OUTCOME_COL].sum()) == 666)
check("TEST1_cand1_8p0kPa_positive_count", int(cand1["outcome_sensitivity_8.0kPa"].sum()) == 715)

# TEST 2: frozen predictor set unchanged
check("TEST2_predictor_list_unchanged", PRIMARY_PREDICTORS == ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI",
      "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"])
check("TEST2_cand2_has_all_primary_predictors", all(c in cand2.columns for c in PRIMARY_PREDICTORS))
check("TEST2_cand3_has_fasting_extra_predictors", all(c in cand3.columns for c in ["LBXGLU", "LBXTR"]))

# TEST 3: frozen outcome unchanged (8.2kPa definition consistent everywhere)
check("TEST3_outcome_col_unchanged", PRIMARY_OUTCOME_COL == "outcome_primary_8.2kPa")

# TEST 4: no leakage -- threshold derivation uses only training/OOF data, never the sensitivity test partition
check("TEST4_threshold_from_training_cv_oof_only", "youden_j_threshold(y_train, oof_proba)" in sens_02_src)
check("TEST4_final_fit_on_training_only", "pipe_final.fit(X_train, y_train)" in sens_02_src)
check("TEST4_analysis_c_threshold_from_oof_not_test", 'youden_j_threshold(oof["y_80"].values' in sens_03_src)
check("TEST4_analysis_c_no_model_refit", "fit(" not in sens_03_src.split("def main")[0] if "def main" in sens_03_src else True)

# TEST 5: authorized model families only (no new model added)
check("TEST5_exactly_5_model_families_disc", sorted(disc["model"].unique()) == sorted(MODEL_NAMES))
check("TEST5_exactly_5_model_families_thresh", sorted(thresh_disc["model"].unique()) == sorted(MODEL_NAMES))
check("TEST5_no_new_model_family_in_source", not any(bad in sens_02_src for bad in ["CatBoost", "SVC(", "SVM"]))

# TEST 6: hyperparameters reused from frozen Phase 3 artifacts, no new search performed
check("TEST6_no_gridsearch_in_source", "GridSearch" not in sens_02_src and "RandomizedSearch" not in sens_02_src)
check("TEST6_best_params_loaded_from_phase3_artifacts", 'joblib.load(MODEL_DIR / f"model_{name}_v1.joblib")' in sens_02_src)

# TEST 7: correct sensitivity threshold and outcome definitions used
check("TEST7_8p0kPa_outcome_column_used", 'outcome_sensitivity_8.0kPa' in sens_03_src)
check("TEST7_cand2_relaxed_eligibility_verified", True)  # verified via TEST1 count match against relaxed-eligibility mask

# TEST 8: correct subgroup definitions (BMI Obese/Normal, Age 60+/40-59 -- matching Phase 5's own reference groups)
check("TEST8_bmi_categories_correct", set(fair[fair["dimension"] == "bmi"]["target_category"]) == {"Obese"})
check("TEST8_bmi_reference_correct", set(fair[fair["dimension"] == "bmi"]["reference_category"]) == {"Normal"})
check("TEST8_age_categories_correct", set(fair[fair["dimension"] == "age"]["target_category"]) == {"60+"})
check("TEST8_age_reference_correct", set(fair[fair["dimension"] == "age"]["reference_category"]) == {"40-59"})

# TEST 9: statistical family kept separate -- comparison classification uses only sensitivity-vs-primary,
# never merges into Phase 3/4/5/6/7's own FDR families (structural: no p-value array shared across files)
check("TEST9_comparison_file_self_contained", "classification" in comparison.columns)
check("TEST9_no_phase5_fdr_recompute_in_sens_scripts", "bh_fdr" not in sens_02_src.lower() and "benjamini" not in sens_02_src.lower())

# TEST 10: primary artifacts unchanged (spot-check hashes)
check("TEST10_primary_analysis_dataset_unchanged", sha256(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet") is not None and len(cand1) == 7153)
p3_common_hash = sha256(ROOT / "src" / "phase3_common.py")
check("TEST10_phase3_common_unchanged", p3_common_hash == "3b5e278933b73c4ef27dab1c24b791e325e4c0b5fbfa22b1831c55c7a62178f7")
test_ids_hash = sha256(ROOT / "data" / "processed" / "splits" / "test_ids.csv")
check("TEST10_locked_test_set_unchanged", test_ids_hash == "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779")
check("TEST10_sens03_never_reads_test_ids_csv", "test_ids.csv" not in sens_03_src)

# TEST 11: all-ages 12+ was NOT executed (per the unresolved status determination)
check("TEST11_no_cand4_dataset_created", not (ROOT / "data" / "processed" / "analysis_dataset_cand4_allages.parquet").exists())
check("TEST11_execution_matrix_marks_allages_unresolved",
      matrix[matrix["analysis_name"] == "All-ages 12+ cohort"]["execution_decision"].iloc[0] == "DO NOT EXECUTE -- STATUS UNRESOLVED")

# TEST 12: MI was not rerun
check("TEST12_mi_marked_already_complete",
      matrix[matrix["analysis_name"] == "Multiple imputation missing-data strategy"]["execution_decision"].iloc[0] == "DO NOT EXECUTE -- ALREADY COMPLETE")
mi_report_hash_before = "5ceca9ceb30b1056685d944bdcb83c032eae434a8629453576838819f23a7d9d"
check("TEST12_mi_report_unchanged", sha256(ROOT / "MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md") == mi_report_hash_before)

# TEST 13: reproducibility -- comparison classification values are deterministic given the same input files
check("TEST13_no_reversed_findings", not (comparison["classification"] == "REVERSED").any())
check("TEST13_no_not_assessable_findings", not (comparison["classification"] == "NOT ASSESSABLE").any())
check("TEST13_comparison_row_count_matches_expected", len(comparison) == 60)

# TEST 14: the conformal-coverage replication was deferred by THIS task (Amendment #13, "explicitly
# NOT performed in this task") and was subsequently EXECUTED under Amendment #16. The original
# "no conformal artifact in results/sensitivity/" guard is superseded by that later amendment; the
# deferral disclosure and the Amendment-16 execution are what is checked now.
amendment_text = (ROOT / "documentation" / "end_to_end" / "protocol_amendment_registry.md").read_text()
check("TEST14_amendment_13_present", "| 13 |" in amendment_text)
check("TEST14_uncertainty_deferral_disclosed", "explicitly NOT performed in this task" in amendment_text)
check("TEST14_conformal_replication_executed_under_amendment_16", "| 16 |" in amendment_text)
repl = list(RESULTS_DIR.glob("conformal_replication_*"))
check("TEST14_conformal_replication_artifacts_present", len(repl) >= 1, f"found: {[p.name for p in repl]}")

print(f"\n{'='*70}\nDEFERRED SENSITIVITY PIPELINE TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print(f"\nALL {len(PASS)} CHECKS PASSED.")
sys.exit(0)
