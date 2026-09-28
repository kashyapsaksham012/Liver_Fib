"""
tests/test_phase8_subgroup_holdout.py
Phase 8 (Generalization, subgroup-holdout design): automated validation. Standalone script
(project convention). Run directly: `python3 tests/test_phase8_subgroup_holdout.py`.
"""
import sys
import subprocess
import hashlib
from pathlib import Path
import pandas as pd
import joblib

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

def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True, text=True, check=True).stdout.strip()

def _doc(p):
    """Resolve a documentation path, falling back to documentation/archive/process_trail/
    where the 2026-08-27 consolidation moved process-trail files (see START_HERE.md §1)."""
    p = Path(p)
    if p.exists():
        return p
    try:
        arch = ROOT / "documentation" / "archive" / "process_trail" / p.relative_to(ROOT / "documentation")
        if arch.exists():
            return arch
    except ValueError:
        pass
    return p

VAL_DIR = ROOT / "results" / "validation"
DOC_DIR = ROOT / "documentation" / "validation"

info_text = (ROOT.parent / "info.md").read_text()
crosswalk_text = (ROOT / "documentation" / "phase_numbering_crosswalk.md").read_text()
snapshot_text = _doc(DOC_DIR / "phase8_pre_execution_snapshot.md").read_text()
decision_text = (DOC_DIR / "phase8_holdout_candidate_decision.md").read_text()
protocol_text = (DOC_DIR / "PHASE8_SUBGROUP_HOLDOUT_PROTOCOL_FREEZE.md").read_text()
mi02_src = (ROOT / "src" / "phase8_02_train_and_holdout_evaluate.py").read_text()
mi01_src = (ROOT / "src" / "phase8_01_partition_and_leakage_check.py").read_text()

training_ids = pd.read_csv(VAL_DIR / "phase8_training_ids.csv")["SEQN"]
holdout_ids = pd.read_csv(VAL_DIR / "phase8_holdout_ids.csv")["SEQN"]
training_registry = pd.read_csv(VAL_DIR / "phase8_training_registry.csv")
protocol_matrix = pd.read_csv(VAL_DIR / "phase8_model_protocol_matrix.csv")
gen_results = pd.read_csv(VAL_DIR / "phase8_generalization_results.csv")
master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")

# TEST 1: official Phase 8 definition
check("TEST1_project_phase8_equals_mentor_phase14", "Project Phase 8" in crosswalk_text and "Mentor Phase 14" in crosswalk_text)
check("TEST1_mentor_generalization_text_recorded", "Generalization" in info_text)

# TEST 2: within-release time-split infeasibility documented with evidence
check("TEST2_within_release_timesplit_infeasibility_documented", "single constant" in snapshot_text or "SDDSRVYR" in snapshot_text)
check("TEST2_no_fabricated_cycle_split", "2017-2018" not in protocol_text and "2019-2020" not in protocol_text.replace("2019-March 2020", ""))

# TEST 3: candidate matrix exists and covers required minimum candidates
matrix = pd.read_csv(VAL_DIR / "phase8_candidate_holdout_matrix.csv")
check("TEST3_candidate_matrix_exists", matrix is not None)
check("TEST3_matrix_covers_minimum_candidates",
      set(matrix["candidate"]) >= {"Non-Hispanic Black", "BMI-Obese", "Age-60+"})

# TEST 4: selected subgroup frozen before training (protocol commit predates training commits)

# NOTE 2026-09-28: 77e2b1c/6fb7e93/279b672 (Phase 8 Commits A/B/C) predate a history
# rewrite and are unreachable from main on a fresh clone; repointed to their current,
# main-reachable equivalents (a75cd16/fddf7e9/3c504d6 -- identical commit messages,
# verified same ordering and file contents).
commit_a = git("log", "--format=%H", "-1", "--grep=Phase 8.*Commit A", "--all").strip()
check("TEST4_protocol_commit_a_exists", len(commit_a) == 40, detail=commit_a)
commit_order = git("log", "--oneline", "--reverse", "a75cd16..3c504d6")  # post-rewrite equivalents of 77e2b1c..279b672 (see NOTE below)
check("TEST4_commit_A_precedes_B_and_C",
      "fddf7e9" in commit_order and "3c504d6" in commit_order)

# TEST 5: prior terminal subgroup statement transparently documented (PATH B, not presented as discovery)
check("TEST5_prior_statement_quoted_verbatim",
      "Hold out Non-Hispanic Black participants entirely and retrain" in decision_text)
check("TEST5_explicitly_labeled_prior_commitment",
      "PATH B" in decision_text and "prior researcher commitment" in decision_text)
check("TEST5_not_presented_as_independent_discovery",
      "not presented" in decision_text and "independent discovery" in decision_text)

# TEST 6: protocol commit predates training (Commit A committed before any src/phase8_02 file existed)
files_in_a = git("show", "--name-only", "--format=", "a75cd16").splitlines()
check("TEST6_commit_A_contains_no_training_code",
      not any("phase8_02" in f or "phase8_holdout" in f and "models/" in f for f in files_in_a))
files_in_c = git("show", "--name-only", "--format=", "3c504d6").splitlines()
check("TEST6_commit_C_contains_training_code_and_models",
      any("phase8_02" in f for f in files_in_c) and any("models/phase8_holdout" in f for f in files_in_c))

# TEST 7: training/holdout disjointness
check("TEST7_training_holdout_disjoint", len(set(training_ids) & set(holdout_ids)) == 0)
check("TEST7_counts_match_protocol", len(training_ids) == 5366 and len(holdout_ids) == 1787)

# TEST 8: selected subgroup completely absent from training
train_races = master[master["SEQN"].isin(training_ids)]["RIDRETH3"]
hold_races = master[master["SEQN"].isin(holdout_ids)]["RIDRETH3"]
check("TEST8_non_hispanic_black_absent_from_training", not (train_races == 4.0).any())
check("TEST8_holdout_entirely_non_hispanic_black", (hold_races == 4.0).all())

# TEST 9: no holdout leakage into preprocessing (structural: StandardScaler/SimpleImputer fit only on X_train, never X_hold)
check("TEST9_preprocessing_fit_on_training_only",
      ".fit(X_hold" not in mi02_src and "pipe_final.fit(X_train, y_train)" in mi02_src)

# TEST 10: no holdout leakage into tuning (no hyperparameter search performed at all)
check("TEST10_no_hyperparameter_search_performed", not protocol_matrix["hyperparameter_search_performed"].any())
check("TEST10_no_gridsearch_in_source", "GridSearch" not in mi02_src and "RandomizedSearch" not in mi02_src)

# TEST 11: no holdout leakage into threshold selection (threshold derived from training CV-OOF only)
check("TEST11_threshold_from_training_cv_oof_only",
      "youden_j_threshold(y_train, oof_proba)" in mi02_src)
check("TEST11_holdout_not_used_in_threshold_flag", not protocol_matrix["holdout_used_in_threshold_selection"].any())

# TEST 12: frozen predictors unchanged
check("TEST12_predictor_list_unchanged", PRIMARY_PREDICTORS == ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI",
      "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"])

# TEST 13: frozen outcome unchanged
check("TEST13_outcome_col_unchanged", PRIMARY_OUTCOME_COL == "outcome_primary_8.2kPa")

# TEST 14: five model families preserved, no new family added
check("TEST14_exactly_5_model_families", sorted(gen_results["model"]) == sorted(MODEL_NAMES))
check("TEST14_training_registry_covers_5_models", sorted(training_registry["model"]) == sorted(MODEL_NAMES))

# TEST 15: training counts correctly recorded
check("TEST15_training_n_recorded_correctly", (training_registry["training_n"] == 5366).all())
check("TEST15_training_positive_n_recorded_correctly", (training_registry["training_positive_n"] == 489).all())

# TEST 16: holdout counts correctly recorded
check("TEST16_holdout_n_recorded_correctly", (gen_results["holdout_n"] == 1787).all())
check("TEST16_holdout_positive_n_recorded_correctly", (gen_results["holdout_positive_n"] == 177).all())

# TEST 17: no post-hoc tuning (hyperparameter source is frozen Phase 3 params for every model, no model-specific override)
check("TEST17_hyperparameter_source_uniform_and_frozen",
      (training_registry["hyperparameter_source"] == "frozen Phase 3 best_params, reused unchanged").all())

# TEST 18: results reproducible -- model artifact hashes recorded and match on-disk files
disk_hashes = {row["model"]: sha256(ROOT / row["model_path"]) for _, row in training_registry.iterrows()}
check("TEST18_model_hashes_match_disk", all(disk_hashes[m] == training_registry.set_index("model").loc[m, "model_sha256"] for m in disk_hashes))

# TEST 19: prior Phase 3-7 artifacts remain unchanged (spot-check hashes recorded in the pre-execution snapshot)
p3_common_hash = sha256(ROOT / "src" / "phase3_common.py")
check("TEST19_phase3_common_unchanged", p3_common_hash == "3b5e278933b73c4ef27dab1c24b791e325e4c0b5fbfa22b1831c55c7a62178f7")
test_ids_hash = sha256(ROOT / "data" / "processed" / "splits" / "test_ids.csv")
check("TEST19_locked_test_set_unchanged", test_ids_hash == "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779")
fairness_hash = sha256(ROOT / "results" / "fairness" / "subgroup_discrimination_metrics.csv")
check("TEST19_phase5_fairness_artifact_unchanged", fairness_hash == "e16b44ea6f9e2a9ac5339e61a1869a68847f328c03e36633fd1b0d00ca58d1a5")

print(f"\n{'='*70}\nPHASE 8 SUBGROUP-HOLDOUT TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print(f"\nALL {len(PASS)} CHECKS PASSED.")
sys.exit(0)
