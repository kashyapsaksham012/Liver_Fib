"""
tests/test_phase7_overlap_closure.py
Phase 7 overlap-closure validation (Part 15). Standalone script (project convention). Run
directly: `python3 tests/test_phase7_overlap_closure.py`.
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

four_way = pd.read_csv(ROOT / "results" / "mitigation" / "bmi_age_overlap_four_way_analysis.csv")
pred_sets = pd.read_csv(ROOT / "results" / "uncertainty" / "test_set_prediction_sets.csv")
interp_text = (ROOT / "documentation" / "mitigation" / "phase7_bmi_age_overlap_interpretation.md").read_text()

logi = pred_sets[pred_sets["model"] == "logistic"]
is_obese = (logi["_bmi"] == "Obese").values
is_60plus = (logi["_age"] == "60+").values

# TEST 1: four groups are mutually exclusive
g_bmi_only = is_obese & ~is_60plus
g_age_only = ~is_obese & is_60plus
g_both = is_obese & is_60plus
g_neither = ~is_obese & ~is_60plus
overlap_check = (g_bmi_only & g_age_only) | (g_bmi_only & g_both) | (g_bmi_only & g_neither) | \
                (g_age_only & g_both) | (g_age_only & g_neither) | (g_both & g_neither)
check("TEST1_four_groups_mutually_exclusive", not overlap_check.any())

# TEST 2: four groups collectively cover the analyzed test-set population
check("TEST2_four_groups_cover_full_population", (g_bmi_only | g_age_only | g_both | g_neither).all())
check("TEST2_counts_sum_to_test_n", int(g_bmi_only.sum() + g_age_only.sum() + g_both.sum() + g_neither.sum()) == len(logi) == 2146)

# TEST 3: BMI-Obese total reconciles to BMI-only + intersection
check("TEST3_bmi_obese_reconciles", int(is_obese.sum()) == int(g_bmi_only.sum() + g_both.sum()) == 883)

# TEST 4: Age-60+ total reconciles to Age-only + intersection
check("TEST4_age_60plus_reconciles", int(is_60plus.sum()) == int(g_age_only.sum() + g_both.sum()) == 741)

# TEST 5: canonical subgroup definitions were reused (same column names/values as Phase 5/6/7)
check("TEST5_uses_canonical_bmi_column", "_bmi" in pred_sets.columns and set(pred_sets["_bmi"].dropna().unique()) == {"Underweight", "Normal", "Overweight", "Obese"})
check("TEST5_uses_canonical_age_column", "_age" in pred_sets.columns and set(pred_sets["_age"].dropna().unique()) == {"18-39", "40-59", "60+"})

# TEST 6: no test-set file was reopened (structural: overlap script never reads test_ids.csv or analysis_dataset_primary.parquet)
overlap_src = (ROOT / "src" / "phase7_05_bmi_age_overlap_analysis.py").read_text()
check("TEST6_overlap_script_never_reads_test_ids", "test_ids.csv" not in overlap_src)
check("TEST6_overlap_script_never_reads_raw_dataset", "analysis_dataset_primary" not in overlap_src and "load_primary_dataset" not in overlap_src)

# TEST 7: no new predictions were generated (structural: no predict_proba call, no model loading)
check("TEST7_no_model_scoring_in_overlap_script", "predict_proba" not in overlap_src and "joblib.load" not in overlap_src)

# TEST 8: no mitigation method was changed (thresholds read from existing frozen artifact, not recomputed)
check("TEST8_thresholds_read_not_recomputed", "group_specific_thresholds.csv" in overlap_src and "np.ceil" not in overlap_src and "np.sort(scores" not in overlap_src)

# TEST 9: no Phase 3-6 artifact was modified
EXPECTED_UNCHANGED_HASHES = {
    ROOT / "models" / "phase6_conformal_refit" / "model_logistic_proper_train_refit.joblib": "000e51505e76d49ebf02a57d29a3132ea1fa837b49497e142c9fd8caeb73c630",
    ROOT / "data" / "processed" / "splits" / "test_ids.csv": "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779",
}
for path, expected in EXPECTED_UNCHANGED_HASHES.items():
    check(f"TEST9_unchanged_{path.name}", sha256(path) == expected)

# TEST 10: baseline and mitigated outputs come from existing frozen Phase 7 artifacts (cross-check N reconciliation)
official_final = pd.read_csv(ROOT / "results" / "mitigation" / "test_set_mitigation_final.csv")
logi_obese_official_n = official_final[(official_final["model"] == "logistic") & (official_final["category"] == "Obese")]["n"].iloc[0]
four_way_logi_obese_n = four_way[(four_way["model"] == "logistic") & (four_way["subgroup_category"].isin(["BMI-Obese only", "Intersection (Obese AND 60+)"]))]["n"].sum()
check("TEST10_four_way_reconciles_with_official_aggregate", int(four_way_logi_obese_n) == int(logi_obese_official_n) == 883)

# TEST 11: de7ff5b file contents match the protocol-only criterion
de7ff5b_files = git("show", "--name-only", "--pretty=", "de7ff5b").split("\n")
de7ff5b_files = [f for f in de7ff5b_files if f.strip()]
forbidden_patterns = ["phase7_02_mitigation_implementation", "phase7_03_pretest", "phase7_04_final_test_touch",
                       "MITIGATION_PROTOCOL_FREEZE", "group_specific_thresholds", "test_set_mitigation_final",
                       "pre_test_evaluation", "marginal_coverage_before_after", "nontarget_subgroup_protection"]
violations = [f for f in de7ff5b_files if any(p in f for p in forbidden_patterns)]
check("TEST11_de7ff5b_protocol_only", violations == [], f"unexpected files: {violations}")
check("TEST11_de7ff5b_contains_expected_justification_files",
      any("phase7_justification_determination" in f for f in de7ff5b_files) and
      any("phase7_01_justification_determination.py" in f for f in de7ff5b_files))

# TEST 12: the updated interpretation does not claim causal interaction (affirmatively).
# "causally interact"/"interaction" appearing after a negation word within ~40 chars (e.g.
# "does not... establish that... causally interact") is the REQUIRED cautious framing, not a
# violation -- only an unnegated affirmative causal claim should fail this check.
import re
NEGATION_WINDOW = 60
def has_unnegated_causal_claim(text, phrase):
    for m in re.finditer(re.escape(phrase), text.lower()):
        window = text.lower()[max(0, m.start() - NEGATION_WINDOW):m.start()]
        if not any(neg in window for neg in ["not", "cannot", "can't", "never", "no evidence", "does not"]):
            return True
    return False

forbidden_causal_phrases = ["caused the", "causally interact", "proves an interaction", "confirms the interaction"]
interp_violation = any(has_unnegated_causal_claim(interp_text, p) for p in forbidden_causal_phrases)
check("TEST12_interpretation_avoids_unnegated_causal_claims", not interp_violation)
check("TEST12_interpretation_uses_cautious_framing",
      "not, and cannot, establish" in interp_text or "not a causal interaction" in interp_text.lower())
report_text = (ROOT / "PHASE7_MITIGATION_RESULTS_REPORT.md").read_text()
report_violation = any(has_unnegated_causal_claim(report_text, p) for p in forbidden_causal_phrases)
check("TEST12_report_section_avoids_unnegated_causal_claims", not report_violation)

print(f"\n{'='*70}\nPHASE 7 OVERLAP-CLOSURE TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print("\nALL 12 TEST CATEGORIES PASSED.")
sys.exit(0)
