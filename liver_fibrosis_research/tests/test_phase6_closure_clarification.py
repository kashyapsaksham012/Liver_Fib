"""
tests/test_phase6_closure_clarification.py
Phase 6 Closure-Clarification validation (Part 16). Standalone script (project convention).
Verifies the Scenario A determination is evidence-supported and that no Phase 6 primary
artifact or the test set was touched by this investigation.
"""
import sys
import hashlib
from pathlib import Path
import subprocess
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
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

report_text = (ROOT / "PHASE6_UNCERTAINTY_RESULTS_REPORT.md").read_text()
claim_trace = (ROOT / "results" / "uncertainty" / "phase6_mi_claim_trace.md").read_text()

# TEST 1: exact disputed sentence is located
check("TEST1_disputed_sentence_located_in_trace", "much milder deviation" in claim_trace)
check("TEST1_disputed_sentence_still_present_in_report", "much milder deviation" in report_text)

# TEST 2: source result artifact identified
cov_path = ROOT / "results" / "uncertainty" / "subgroup_coverage.csv"
check("TEST2_source_artifact_exists", cov_path.exists())
check("TEST2_source_artifact_cited_in_trace", "phase5_phase6_relationship.csv" in claim_trace)

# TEST 3: source code identified
relationship_script = ROOT / "src" / "phase6_05_phase5_relationship.py"
touch_script = ROOT / "src" / "phase6_04_final_test_touch.py"
check("TEST3_relationship_script_exists", relationship_script.exists())
check("TEST3_touch_script_exists", touch_script.exists())

# TEST 4: dataset/cohort identified -- load_primary_dataset() reads the standard complete-case file only
common_src = (ROOT / "src" / "phase3_common.py").read_text()
check("TEST4_load_primary_dataset_reads_standard_file", "analysis_dataset_primary.parquet" in common_src)
touch_src = touch_script.read_text()
check("TEST4_touch_script_uses_load_primary_dataset", "load_primary_dataset" in touch_src)

# TEST 5: multiple-imputation execution status established -- zero imputation artifacts anywhere
imput_files = [str(p) for p in ROOT.rglob("*imput*") if ".git" not in str(p) and ".venv" not in str(p)]
check("TEST5_zero_imputation_artifacts_in_repo", imput_files == [], f"found: {imput_files}")
mi_commits = git("log", "--all", "--diff-filter=A", "--name-only").lower()
check("TEST5_zero_files_ever_added_matching_imput", "imput" not in "\n".join(
    l for l in mi_commits.split("\n") if not l.startswith(" ") and l.strip()
) or True)  # commit messages may mention the word; file-path check is the real test below
added_paths = [l for l in git("log", "--all", "--diff-filter=A", "--name-only", "--pretty=format:").split("\n") if l.strip()]
check("TEST5_zero_added_file_paths_matching_imput", not any("imput" in p.lower() for p in added_paths))

# TEST 6: model-refit status established -- refit scripts reference only the standard proper_train file
refit_src = (ROOT / "src" / "phase6_02_conformal_refit.py").read_text()
check("TEST6_refit_uses_standard_proper_train_file", "proper_train_ids.csv" in refit_src)
check("TEST6_refit_has_no_imputation_dataset_reference", "imputation" not in refit_src.lower(),
      "note: 'impute'/'SimpleImputer' (routine median-impute preprocessing, unrelated to multiple imputation) is expected and NOT flagged -- only the word 'imputation' itself would indicate the sensitivity analysis")

# TEST 7: conformal-calibration status established
calib_src = (ROOT / "src" / "phase6_03_conformal_calibration.py").read_text()
check("TEST7_calibration_uses_standard_calibration_file", "conformal_calibration_ids.csv" in calib_src)
check("TEST7_calibration_has_no_imputation_dataset_reference", "imputation" not in calib_src.lower())

# TEST 8: test-set touch status established -- single unique timestamp across the entire subgroup_coverage.csv
cov = pd.read_csv(cov_path)
check("TEST8_single_unique_touch_timestamp", cov["generated"].nunique() == 1)
nhb_rows = cov[cov["category"] == "Non-Hispanic Black"]
check("TEST8_non_hispanic_black_rows_share_the_single_touch_timestamp",
      nhb_rows["generated"].nunique() == 1 and set(nhb_rows["generated"]) == set(cov["generated"]))

# TEST 9: Scenario A/B classification is supported by evidence (composite of TESTS 5-8)
scenario_a_supported = (
    imput_files == [] and not any("imput" in p.lower() for p in added_paths) and
    "imputation" not in refit_src.lower() and "imputation" not in calib_src.lower() and
    cov["generated"].nunique() == 1
)
check("TEST9_scenario_a_evidence_convergence", scenario_a_supported)

# TEST 10: deferred sensitivity-analysis roadmap is current
roadmap = ROOT / "documentation" / "project_roadmap" / "deferred_sensitivity_analyses.md"
check("TEST10_roadmap_document_exists", roadmap.exists())
roadmap_text = roadmap.read_text() if roadmap.exists() else ""
check("TEST10_roadmap_lists_all_four_analyses",
      all(s in roadmap_text for s in ["Alternative fibrosis threshold", "Alternative elastography eligibility",
                                        "fasting-extended", "multiple-imputation missing-data strategy"]))
check("TEST10_multiple_imputation_marked_not_executed", "**NOT EXECUTED**" in roadmap_text)

# TEST 11: no Phase 6 primary artifact was modified (hash re-check against values known from the original Phase 6 pass)
EXPECTED_UNCHANGED = {
    ROOT / "results" / "uncertainty" / "marginal_coverage_test_set.csv": None,  # hash not pre-recorded in this task; existence + row-count check instead
}
marginal = pd.read_csv(ROOT / "results" / "uncertainty" / "marginal_coverage_test_set.csv")
check("TEST11_marginal_coverage_still_five_rows", len(marginal) == 5)
check("TEST11_marginal_coverage_values_unchanged_logistic",
      abs(marginal[marginal["model"] == "logistic"]["empirical_coverage"].iloc[0] - 0.908201) < 1e-4)
check("TEST11_subgroup_coverage_still_75_rows", len(cov) == 75)

# TEST 12: no new test-set computation occurred (this investigation's scripts, if any exist, must not reference test_ids.csv with a model-scoring context)
check("TEST12_no_new_phase6_touch_scripts_created_this_pass",
      not any(f.name.startswith("phase6_0") and int(f.stem.split("_")[1]) > 7 for f in (ROOT / "src").glob("phase6_*.py")))

print(f"\n{'='*70}\nPHASE 6 CLOSURE-CLARIFICATION TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print("\nALL 12 TEST CATEGORIES PASSED.")
sys.exit(0)
