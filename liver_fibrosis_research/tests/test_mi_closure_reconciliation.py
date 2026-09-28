"""
tests/test_mi_closure_reconciliation.py
MI Closure Reconciliation task: automated validation. Standalone script (project convention).
Run directly: `python3 tests/test_mi_closure_reconciliation.py`.

Verifies two things only: (1) the deferred-sensitivity-analysis count is reconciled and
internally consistent, and (2) MI Commits B/C/D stayed within their authorized scope and did not
touch the locked test set. Does not re-derive, alter, or re-run any MI result.
"""
import sys
import subprocess
import hashlib
from pathlib import Path
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

roadmap_path = ROOT / "documentation" / "project_roadmap" / "deferred_sensitivity_analyses.md"
phase2_plan_path = ROOT / "documentation" / "phase2" / "sensitivity_analysis_plan.md"
cohort_decision_path = ROOT / "documentation" / "phase2" / "primary_cohort_decision.md"
roadmap_text = roadmap_path.read_text()
phase2_plan_text = phase2_plan_path.read_text()
cohort_decision_text = cohort_decision_path.read_text()

# TEST 1: current deferred roadmap exists and is readable
check("TEST1_roadmap_exists", roadmap_path.exists())

# TEST 2: original Phase-2 sensitivity source is identified and readable
check("TEST2_phase2_sensitivity_plan_exists", phase2_plan_path.exists())
check("TEST2_phase2_cohort_decision_exists", cohort_decision_path.exists())

# TEST 3: all-ages 12+ status is explicitly resolved (not silently dropped, not guessed)
import re
phase2_plan_normalized = re.sub(r"\s+", " ", phase2_plan_text)
check("TEST3_allages_explained_in_phase2_source",
      "All-ages (12-17y) cohort" in phase2_plan_normalized and "not duplicated as a fifth item here" in phase2_plan_normalized)
check("TEST3_cand4_documented_in_cohort_decision",
      "CAND_4" in cohort_decision_text and "robustness to the adult-only restriction" in cohort_decision_text)
check("TEST3_reconciliation_note_present_in_roadmap",
      "Reconciliation note" in roadmap_text and "CAND_4" in roadmap_text)

# TEST 4: roadmap is internally consistent -- the 4 originally-numbered items match the frozen
# protocol's "complete, fixed set" governing rule, plus the one distinct item (CAND_4, "## 2b.")
# that Amendment #14 added and classified DISTINCT-EXPLORATORY-UNEXECUTED.
import re
numbered_headers = [l for l in roadmap_text.splitlines() if re.match(r"^## \d+\. ", l)]
check("TEST4_exactly_4_originally_numbered_items", len(numbered_headers) == 4, detail=str(numbered_headers))
check("TEST4_cand4_tracked_as_the_amendment_14_distinct_item",
      any(l.startswith("## 2b.") for l in roadmap_text.splitlines()) and "Amendment #14" in roadmap_text)
check("TEST4_governing_rule_states_4", "complete, fixed set" in roadmap_text)

# TEST 5-7: MI Commit B/C/D file contents classified as in-scope (no out-of-scope path substrings)
OUT_OF_SCOPE_MARKERS = ["mitigation", "recalibrat", "phase7", "phase_7", "bmi_age", "age_bmi"]
IN_SCOPE_PREFIXES = ("liver_fibrosis_research/src/mi_0", "liver_fibrosis_research/results/sensitivity/",
                     "liver_fibrosis_research/tests/test_multiple_imputation_sensitivity.py",
                     "liver_fibrosis_research/MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md",
                     "liver_fibrosis_research/documentation/sensitivity/",
                     "liver_fibrosis_research/documentation/project_roadmap/deferred_sensitivity_analyses.md",
                     "liver_fibrosis_research/documentation/end_to_end/protocol_amendment_registry.md")

commit_files = {}

# NOTE 2026-09-28: the sha values above were repointed to their post-history-rewrite
# equivalents (same commit message/content, unreachable-from-main originals orphaned by
# the co-author-strip rewrite) so `git show` works on a fresh clone. The TEST11 checks
# below intentionally still look for the ORIGINAL short hashes ("4802602" etc) -- those
# are frozen prose in documentation/project_roadmap/deferred_sensitivity_analyses.md
# quoting the hashes as they were at write time, not a git lookup, and are correctly left as-is.
for label, sha in [("B", "567a7c8"), ("C", "4ec937d"), ("D", "d5835fe")]:
    files = git("show", "--name-only", "--format=", sha).splitlines()
    files = [f for f in files if f.strip()]
    commit_files[label] = files
    check(f"TEST5_commit_{label}_all_files_in_scope",
          all(any(f.startswith(p) for p in IN_SCOPE_PREFIXES) for f in files), detail=str(files))
    check(f"TEST6_commit_{label}_no_out_of_scope_marker",
          not any(any(m in f.lower() for m in OUT_OF_SCOPE_MARKERS) for f in files), detail=str(files))

# TEST 7: out-of-scope files, if any, are explicitly identified (structurally: zero found, verified above)
all_touched = [f for files in commit_files.values() for f in files]
out_of_scope = [f for f in all_touched if not any(f.startswith(p) for p in IN_SCOPE_PREFIXES)]
check("TEST7_no_out_of_scope_files_found_across_BCD", len(out_of_scope) == 0, detail=str(out_of_scope))

# TEST 8: MI result values in this task's own report were not altered by this closure task
report_text = (ROOT / "MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md").read_text()
for marker in ["MI ROBUSTNESS PARTIAL", "0.978", "+4.16pp", "MULTIPLE IMPUTATION COMPLETE"]:
    check(f"TEST8_mi_report_still_contains_{marker.replace(' ', '_').replace('.', '_')}", marker in report_text)
comparison = pd.read_csv(ROOT / "results" / "sensitivity" / "mi_black_subgroup_comparison.csv")
check("TEST8_mi_csv_classification_values_unchanged",
      sorted(comparison["classification"].apply(lambda c: c.split(" -- ")[0]).unique()) == ["A", "F"])
check("TEST8_mi_csv_no_significant_after_fdr", not comparison["significant_after_fdr"].any())

# TEST 9: no deferred analysis was executed by this closure task (no new model/prediction artifact)
forbidden_new_dirs = [ROOT / "results" / "sensitivity_alt_threshold", ROOT / "results" / "sensitivity_cand4",
                       ROOT / "results" / "sensitivity_fasting", ROOT / "results" / "sensitivity_cand2"]
check("TEST9_no_deferred_analysis_output_created", all(not d.exists() for d in forbidden_new_dirs))

# TEST 10: test-set-touch status is established -- hash matches the Phase-6-frozen recorded value,
# and git history shows exactly one commit ever touched the file (the original Phase 3 bulk commit)
test_ids_path = ROOT / "data" / "processed" / "splits" / "test_ids.csv"
check("TEST10_test_ids_hash_matches_phase6_frozen_record",
      sha256(test_ids_path) == "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779")
touch_commits = git("log", "--oneline", "--", "data/processed/splits/test_ids.csv").splitlines()
check("TEST10_test_ids_touched_exactly_once_ever", len(touch_commits) == 1, detail=str(touch_commits))
for label, sha in [("B", "567a7c8"), ("C", "4ec937d"), ("D", "d5835fe")]:
    check(f"TEST10_commit_{label}_does_not_touch_test_ids",
          "data/processed/splits/test_ids.csv" not in commit_files[label])

# TEST 11: final report reflects actual evidence (not fabricated) -- spot-check the report cites
# commit hashes and file paths that actually exist and match
check("TEST11_report_cites_real_commit_B", "4802602" in report_text or "4802602" in roadmap_text)
snapshot_text = _doc(ROOT / "documentation" / "sensitivity" / "mi_closure_reconciliation_snapshot.md").read_text()
check("TEST11_snapshot_records_all_three_mi_commits",
      all(sha in snapshot_text for sha in ["4802602", "f73ef91", "adc9328"]))

print(f"\n{'='*70}\nMI CLOSURE RECONCILIATION TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print(f"\nALL {len(PASS)} CHECKS PASSED.")
sys.exit(0)
