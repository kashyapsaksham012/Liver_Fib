"""
tests/test_reliability_extension.py
Reliability Extension (co-occurrence correlation + Decision Curve Analysis): automated validation.
Standalone script (project convention). Run directly: `python3 tests/test_reliability_extension.py`.
"""
import sys
import hashlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase3_common import MODEL_NAMES

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

REL_DIR = ROOT / "results" / "reliability_extension"
coocc_table = pd.read_csv(REL_DIR / "cooccurrence_analysis_table.csv")
coocc_results = pd.read_csv(REL_DIR / "cooccurrence_correlation_results.csv")
within_model = pd.read_csv(REL_DIR / "cooccurrence_within_model_secondary.csv")
dca = pd.read_csv(REL_DIR / "dca_results.csv")
rel_01_src = (ROOT / "src" / "rel_01_cooccurrence_analysis.py").read_text()
rel_02_src = (ROOT / "src" / "rel_02_decision_curve_analysis.py").read_text()

# TEST 1: no model was retrained -- no .fit( call anywhere in either script
check("TEST1_rel01_no_model_fit_call", ".fit(" not in rel_01_src)
check("TEST1_rel02_no_model_fit_call", ".fit(" not in rel_02_src)

# TEST 2: no new predictions were generated -- neither script imports a model class or predict_proba
check("TEST2_rel01_no_predict_proba", "predict_proba" not in rel_01_src)
check("TEST2_rel02_no_predict_proba", "predict_proba" not in rel_02_src)
check("TEST2_no_sklearn_estimator_imports", not any(x in rel_01_src + rel_02_src for x in
      ["LogisticRegression(", "RandomForestClassifier(", "XGBClassifier(", "LGBMClassifier(", "MLPClassifier("]))

# TEST 3: original test IDs were not modified
test_ids_hash = sha256(ROOT / "data" / "processed" / "splits" / "test_ids.csv")
check("TEST3_locked_test_ids_unchanged", test_ids_hash == "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779")

# TEST 4: all intended model x subgroup observations were included (N=55, no cherry-picking)
check("TEST4_cooccurrence_table_n55", len(coocc_table) == 55)
check("TEST4_all_4_dimensions_present", set(coocc_table["dimension"].unique()) == {"sex", "race_ethnicity", "age", "bmi"})
check("TEST4_all_5_models_present", set(coocc_table["model"].unique()) == set(MODEL_NAMES))
check("TEST4_not_limited_to_headline_subgroups",
      set(coocc_table["category"].unique()) > {"Obese", "60+"})

# TEST 5: precision flags were preserved (not silently dropped or overwritten)
check("TEST5_precision_tier_column_present", "precision_tier" in coocc_table.columns)
check("TEST5_precision_limited_flag_present", "precision_limited" in coocc_table.columns)
check("TEST5_insufficient_evidence_category_present",
      (coocc_table["precision_tier"] == "insufficient evidence").any())
check("TEST5_precision_filtered_sensitivity_excludes_fewer_than_primary",
      int(coocc_results[coocc_results["analysis"] == "precision_filtered_sensitivity"]["n"].iloc[0]) < 55)

# TEST 6: DCA used the explicitly documented probability source (recalibrated, not raw)
check("TEST6_dca_uses_recalibrated_column", "recalibrated_predicted_probability" in rel_02_src)
check("TEST6_dca_does_not_use_raw_column_as_primary",
      "raw_predicted_probability" not in rel_02_src.split("recalibrated_predicted_probability")[0])
check("TEST6_probability_source_documented",
      "RECALIBRATED" in (ROOT / "src" / "rel_02_decision_curve_analysis.py").read_text())

# TEST 7: Phase 1-8 artifacts remain unchanged (spot-check hashes)
p3_common_hash = sha256(ROOT / "src" / "phase3_common.py")
check("TEST7_phase3_common_unchanged", p3_common_hash == "3b5e278933b73c4ef27dab1c24b791e325e4c0b5fbfa22b1831c55c7a62178f7")
fairness_hash = sha256(ROOT / "results" / "fairness" / "fairness_inference.csv")
check("TEST7_phase5_fairness_unchanged", fairness_hash == "b7351bd9daf6ee5c26d7f6cf33e0859bbb952e6129c310fd0e291c133c21e132")
coverage_hash = sha256(ROOT / "results" / "uncertainty" / "coverage_inference.csv")
check("TEST7_phase6_coverage_unchanged", coverage_hash == "4004dda509a61c1a87dda0ad699eae4ed0a3ae10e252a2e2051bebcd75eb32e7")
recal_hash = sha256(ROOT / "results" / "calibration" / "test_set_recalibrated_predictions.csv")
check("TEST7_phase4_recalibrated_predictions_unchanged", recal_hash == "a945825b6d927c9e7f0194e8b27197ec7aeee959c034ec7a7511ee8e5d250dda")

# TEST 8: output files are reproducible (deterministic given fixed seeds -- verified via isolated rerun this task)
check("TEST8_permutation_seed_documented", "PERM_SEED = 42" in rel_01_src)
check("TEST8_correlation_results_file_exists", (REL_DIR / "cooccurrence_correlation_results.csv").exists())
check("TEST8_dca_results_file_exists", (REL_DIR / "dca_results.csv").exists())

# Additional: protocol was frozen before code existed (commit ordering)
import subprocess
def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True, text=True, check=True).stdout.strip()
# NOTE 2026-09-28: the pre-existing SHA here (1876858) predates a history
# rewrite (co-author-strip, see git tag backup-before-coauthor-strip, local-
# only, never pushed) and is unreachable from main on any fresh clone -- it
# only "worked" locally via that orphaned tag. 9ab5e30 is the same commit
# (identical message/timestamp/file list) under its current, main-reachable hash.
commit_a_files = git("show", "--name-only", "--format=", "9ab5e30").splitlines()
check("TEST9_commit_A_contains_no_analysis_code",
      not any("rel_01" in f or "rel_02" in f for f in commit_a_files))
check("TEST9_commit_A_contains_protocol_freeze",
      any("COOCCURRENCE_PROTOCOL_FREEZE" in f for f in commit_a_files))

# TEST 10: DCA reliability flags correctly computed and no subgroup silently dropped
check("TEST10_bmi_obese_dca_present", (dca["population"] == "bmi_obese").any())
check("TEST10_age_60plus_dca_present", (dca["population"] == "age_60plus").any())
check("TEST10_reference_strategies_present", set(dca["model"].unique()) >= set(MODEL_NAMES) | {"TREAT_ALL", "TREAT_NONE"})

print(f"\n{'='*70}\nRELIABILITY EXTENSION TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print(f"\nALL {len(PASS)} CHECKS PASSED.")
sys.exit(0)
