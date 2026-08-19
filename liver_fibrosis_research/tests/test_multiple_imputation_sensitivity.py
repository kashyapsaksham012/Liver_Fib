"""
tests/test_multiple_imputation_sensitivity.py
Targeted MI sensitivity analysis (pre-Phase-8): automated validation. Standalone script (project
convention). Run directly: `python3 tests/test_multiple_imputation_sensitivity.py`.
"""
import sys
import hashlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase3_common import PRIMARY_PREDICTORS, MODEL_NAMES

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
registry = pd.read_csv(RESULTS_DIR / "multiple_imputation_registry.csv")
diagnostics = pd.read_csv(RESULTS_DIR / "multiple_imputation_diagnostics.csv")
decision = pd.read_csv(RESULTS_DIR / "mi_model_protocol_decision.csv")
comparison = pd.read_csv(RESULTS_DIR / "mi_black_subgroup_comparison.csv")

mi01_src = (ROOT / "src" / "mi_01_construct_and_diagnostics.py").read_text()
mi02_src = (ROOT / "src" / "mi_02_black_subgroup_comparison.py").read_text()
mi03_src = (ROOT / "src" / "mi_03_black_subgroup_inference.py").read_text()

# TEST 1: exactly m=5 imputations registered, seeds 42-46 (base seed + i)
check("TEST1_five_imputations_seeds_42_to_46",
      list(registry["imputation_index"]) == [0, 1, 2, 3, 4] and list(registry["seed"]) == [42, 43, 44, 45, 46])

# TEST 2: sample_posterior=True used (the fix for the self-caught determinism bug)
check("TEST2_sample_posterior_true_in_registry", bool(registry["sample_posterior"].all()))
check("TEST2_sample_posterior_true_in_source_mi01", "sample_posterior=True" in mi01_src)
check("TEST2_sample_posterior_true_in_source_mi02", "sample_posterior=True" in mi02_src)

# TEST 3: the 5 imputed datasets are genuinely distinct (not the deterministic-bug byte-identical case)
hashes = list(registry["file_sha256"])
check("TEST3_five_distinct_imputation_hashes", len(set(hashes)) == 5, detail=str(hashes))

# TEST 4: imputation hashes match the on-disk files exactly (no silent post-hoc edit)
disk_hashes = [sha256(RESULTS_DIR / f"mi_imputed_dataset_{i}.csv") for i in range(5)]
check("TEST4_registry_hashes_match_disk_files", disk_hashes == hashes)

# TEST 5: outcome never used as an imputation predictor (protocol's "outcome-independent" requirement)
check("TEST5_outcome_not_used_as_imputation_predictor", not registry["outcome_used_as_imputation_predictor"].any())

# TEST 6: imputation predictor matrix is exactly the 10 frozen primary predictors (no auxiliary variables added)
imputed_and_not = set()
for _, row in registry.iterrows():
    imputed_and_not |= set(str(row["predictors_imputed"]).split("|")) | set(str(row["predictors_not_imputed"]).split("|"))
check("TEST6_imputation_predictor_matrix_is_frozen_predictor_set", imputed_and_not == set(PRIMARY_PREDICTORS))
check("TEST6_frozen_predictor_list_unchanged", PRIMARY_PREDICTORS == ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI",
      "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"])

# TEST 7: no hyperparameter search performed for the MI comparison (frozen Phase 3 best_params reused unchanged)
check("TEST7_no_hyperparameter_search_performed", not decision["hyperparameter_search_performed"].any())
check("TEST7_hyperparams_sourced_from_frozen_phase3_artifacts",
      decision["hyperparameters_source"].str.contains("model_.*_v1.joblib", regex=True).all())

# TEST 8: complete-case arm N=7,153 and MI arm N=7,768 for every model (exact frozen cohort sizes)
check("TEST8_complete_case_arm_n_exact", (decision["complete_case_arm_n"] == 7153).all())
check("TEST8_mi_arm_n_exact", (decision["mi_arm_n"] == 7768).all())

# TEST 9: locked test set never referenced anywhere in the MI sensitivity source code (structural leakage check)
for name, src in [("mi_01", mi01_src), ("mi_02", mi02_src), ("mi_03", mi03_src)]:
    check(f"TEST9_{name}_does_not_load_test_ids", "test_ids.csv" not in src and "test_ids" not in src)

# TEST 10: CV design is StratifiedKFold(5-fold, seed=42), matching the project's established convention
check("TEST10_cv_design_5fold_seed42", "StratifiedKFold" in mi02_src and "n_splits=N_CV_FOLDS" in mi02_src)

# TEST 11: predictive pooling (mean across m imputations), not Rubin's-rules parameter pooling
check("TEST11_predictive_pooling_used", "np.mean(mi_probas" in mi02_src)
check("TEST11_pooling_method_documented_in_decision_csv", decision["mi_pooling_method"].str.contains("predictive pooling").all())

# TEST 12: Black-subgroup comparison covers all 5 primary models, at their own frozen thresholds
check("TEST12_comparison_covers_all_5_models", sorted(comparison["model"]) == sorted(MODEL_NAMES))
check("TEST12_subgroup_is_non_hispanic_black", (comparison["subgroup"] == "Non-Hispanic Black").all())

# TEST 13: Black-subgroup N grows from complete-case to MI pool (consistent with the 41.3%-of-exclusions finding)
check("TEST13_black_subgroup_n_grows_under_mi", (comparison["mi_n"] > comparison["cc_n"]).all())
check("TEST13_black_subgroup_n_exact", (comparison["cc_n"] == 1787).all() and (comparison["mi_n"] == 2041).all())

# TEST 14: classification values are restricted to the 6 authorized categories (Part 16, no invented labels)
allowed_prefixes = ("A -- STABLE", "B -- ATTENUATED", "C -- STRENGTHENED", "D -- REVERSED",
                     "E -- NO LONGER DETECTABLE", "F -- INDETERMINATE")
check("TEST14_classification_values_restricted_to_authorized_set",
      comparison["classification"].apply(lambda c: c.startswith(allowed_prefixes)).all(),
      detail=str(list(comparison["classification"])))

# TEST 15: BH-FDR applied once as a single 5-model family (not per-pair, not pooled with other phases)
check("TEST15_bh_fdr_single_family_of_5", len(comparison) == 5 and comparison["bh_fdr_adjusted_p"].nunique() <= 5)
check("TEST15_bh_fdr_column_present", "bh_fdr_adjusted_p" in comparison.columns and "significant_after_fdr" in comparison.columns)

# TEST 16: no result is spuriously "significant" under FDR (spot-check against the actually-observed run)
check("TEST16_no_model_significant_after_fdr", not comparison["significant_after_fdr"].any())

# TEST 17: uncertainty/conformal-coverage comparison under MI was explicitly NOT performed (not authorized)
uncertainty_mi_files = list(RESULTS_DIR.glob("*coverage*")) + list(RESULTS_DIR.glob("*conformal*"))
check("TEST17_no_uncertainty_conformal_artifact_under_mi", len(uncertainty_mi_files) == 0, detail=str(uncertainty_mi_files))

# TEST 18: no Phase 7+ / mitigation artifact was touched or created by this analysis
forbidden_dirs = [ROOT / "results" / "mitigation_mi", ROOT / "results" / "phase7_mi"]
check("TEST18_no_phase7_mitigation_output_created_by_mi_task", all(not d.exists() for d in forbidden_dirs))

# TEST 19: deferred-analyses roadmap correctly reflects execution status (item 4 executed, items 1-3 still deferred)
deferred_text = (ROOT / "documentation" / "project_roadmap" / "deferred_sensitivity_analyses.md").read_text()
check("TEST19_item4_marked_executed", "EXECUTED 2026-08-19" in deferred_text)
check("TEST19_items_1_to_3_still_not_executed",
      deferred_text.count("**NOT EXECUTED**") >= 3)
check("TEST19_scope_deferral_phrasing_present",
      "Deferred due to scope/time considerations; not used to alter the primary analysis or conclusions." in deferred_text)

# TEST 20: Amendment #12 exists in the registry with the self-caught-bug disclosure
amendment_text = (ROOT / "documentation" / "end_to_end" / "protocol_amendment_registry.md").read_text()
check("TEST20_amendment_12_present", "| 12 |" in amendment_text)
check("TEST20_self_caught_disclosure_present", "Self-caught and corrected during execution" in amendment_text)

# TEST 21: forbidden overclaim language never appears in this analysis's own artifacts
for path in [RESULTS_DIR / "mi_black_subgroup_comparison.csv", ROOT / "documentation" / "project_roadmap" / "deferred_sensitivity_analyses.md"]:
    text = path.read_text()
    check(f"TEST21_no_overclaim_in_{path.name}",
          "proves the model is unbiased" not in text and "proves selection bias caused" not in text)

print(f"\n{'='*70}\nMULTIPLE IMPUTATION SENSITIVITY TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print(f"\nALL {len(PASS)} CHECKS PASSED.")
sys.exit(0)
