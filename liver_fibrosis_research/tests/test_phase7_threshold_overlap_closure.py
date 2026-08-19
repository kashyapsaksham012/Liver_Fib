"""
tests/test_phase7_threshold_overlap_closure.py
Phase 7 threshold-override closure validation (Part 18). Standalone script (project
convention). Run directly: `python3 tests/test_phase7_threshold_overlap_closure.py`.
"""
import sys
import hashlib
import re
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

precedence = pd.read_csv(ROOT / "results" / "mitigation" / "threshold_precedence_audit.csv")
participant = pd.read_csv(ROOT / "results" / "mitigation" / "intersection_participant_level_audit.csv")
pred_sets = pd.read_csv(ROOT / "results" / "uncertainty" / "test_set_prediction_sets.csv")
report_text = (ROOT / "PHASE7_MITIGATION_RESULTS_REPORT.md").read_text()
implementation_src = (ROOT / "src" / "phase7_02_mitigation_implementation.py").read_text()
touch_src = (ROOT / "src" / "phase7_04_final_test_touch.py").read_text()
audit_src = (ROOT / "src" / "phase7_06_threshold_precedence_audit.py").read_text()

logi = pred_sets[pred_sets["model"] == "logistic"]
is_obese = (logi["_bmi"] == "Obese").values
is_60plus = (logi["_age"] == "60+").values

# TEST 1: canonical BMI definition unchanged
check("TEST1_canonical_bmi_categories", set(pred_sets["_bmi"].dropna().unique()) == {"Underweight", "Normal", "Overweight", "Obese"})

# TEST 2: canonical Age definition unchanged
check("TEST2_canonical_age_categories", set(pred_sets["_age"].dropna().unique()) == {"18-39", "40-59", "60+"})

# TEST 3: four-way subgroup partition is mutually exclusive
g_bmi_only = is_obese & ~is_60plus
g_age_only = ~is_obese & is_60plus
g_both = is_obese & is_60plus
g_neither = ~is_obese & ~is_60plus
overlap = (g_bmi_only & g_age_only) | (g_bmi_only & g_both) | (g_age_only & g_both) | (g_bmi_only & g_neither) | (g_age_only & g_neither) | (g_both & g_neither)
check("TEST3_four_way_mutually_exclusive", not overlap.any())

# TEST 4: four-way partition covers the analyzed population
check("TEST4_four_way_covers_population", (g_bmi_only | g_age_only | g_both | g_neither).all() and int(g_both.sum()) == 294)

# TEST 5: threshold precedence matches actual code (spot-check: for a dual-target model, the
# "BMI-Obese AND Age-60+" applied_threshold must equal that model's Age-specific threshold)
group_thresh = pd.read_csv(ROOT / "results" / "mitigation" / "group_specific_thresholds.csv").set_index(["model", "dimension", "category"])
for model in ["random_forest", "xgboost", "lightgbm", "mlp"]:
    row = precedence[(precedence["model"] == model) & (precedence["membership_state"] == "BMI-Obese AND Age-60+")].iloc[0]
    expected_age_thresh = group_thresh.loc[(model, "age", "60+"), "group_specific_threshold"]
    check(f"TEST5_precedence_matches_code_{model}", abs(row["applied_threshold"] - expected_age_thresh) < 1e-6)
logi_row = precedence[(precedence["model"] == "logistic") & (precedence["membership_state"] == "BMI-Obese AND Age-60+")].iloc[0]
expected_bmi_thresh = group_thresh.loc[("logistic", "bmi", "Obese"), "group_specific_threshold"]
check("TEST5_precedence_matches_code_logistic", abs(logi_row["applied_threshold"] - expected_bmi_thresh) < 1e-6)

# TEST 6: model-specific precedence is correctly documented (4 Age-overwrites-BMI, 1 uncontested BMI)
age_wins = precedence[(precedence["membership_state"] == "BMI-Obese AND Age-60+") & (precedence["winner"] == "Age (overwrites BMI)")]
check("TEST6_exactly_four_models_age_overwrites_bmi", len(age_wins) == 4)
check("TEST6_logistic_uncontested_bmi",
      precedence[(precedence["model"] == "logistic") & (precedence["membership_state"] == "BMI-Obese AND Age-60+")]["winner"].iloc[0] == "BMI (uncontested)")

# TEST 7: no test-set file was reopened
check("TEST7_audit_script_never_reads_test_ids", "test_ids.csv" not in audit_src)
check("TEST7_audit_script_never_reads_raw_dataset", "analysis_dataset_primary" not in audit_src and "load_primary_dataset" not in audit_src)

# TEST 8: no prediction was regenerated
check("TEST8_no_model_scoring_in_audit_script", "predict_proba" not in audit_src and "joblib.load" not in audit_src)

# TEST 9: no mitigation method changed (thresholds read from existing artifact, not recomputed)
check("TEST9_thresholds_read_not_recomputed", "group_specific_thresholds.csv" in audit_src and "np.ceil" not in audit_src)

# TEST 10: no Phase 1-6 artifact changed
EXPECTED_UNCHANGED = {
    ROOT / "models" / "phase6_conformal_refit" / "model_logistic_proper_train_refit.joblib": "000e51505e76d49ebf02a57d29a3132ea1fa837b49497e142c9fd8caeb73c630",
    ROOT / "data" / "processed" / "splits" / "test_ids.csv": "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779",
    ROOT / "results" / "uncertainty" / "test_set_prediction_sets.csv": "527969c3529389d3e857e4e86e66e0aab06cc5e5784e73a48d471f155f175506",
}
for path, expected in EXPECTED_UNCHANGED.items():
    check(f"TEST10_unchanged_{path.name}", sha256(path) == expected)

# TEST 11: existing coverage outputs are unchanged (test_set_mitigation_final.csv not modified by this closure pass)
check("TEST11_test_set_mitigation_final_unchanged",
      sha256(ROOT / "results" / "mitigation" / "test_set_mitigation_final.csv") == "e496fc8401c35b7aa27910aff8de870a973697267d5a49d4ecbde4db9c40df43")

# TEST 12: no causal interaction language introduced without evidence (negation-aware check, same
# methodology as the prior closure pass's corrected test)
NEGATION_WINDOW = 80
def has_unnegated_claim(text, phrase):
    for m in re.finditer(re.escape(phrase), text.lower()):
        window = text.lower()[max(0, m.start() - NEGATION_WINDOW):m.start()]
        if not any(neg in window for neg in ["not", "cannot", "can't", "never", "no evidence", "does not", "rules out"]):
            return True
    return False
forbidden = ["causally interact", "proves an interaction", "confirms the interaction", "caused by the interaction"]
check("TEST12_report_avoids_unnegated_causal_claims", not any(has_unnegated_claim(report_text, p) for p in forbidden))

# TEST 13: existing limitation about N=294 is preserved
check("TEST13_n294_limitation_preserved", "294" in report_text and "sample-size" in report_text.lower())

# TEST 14: final report matches the audited implementation (spot-check a specific numeric claim)
check("TEST14_report_states_four_of_five_age_overwrites",
      "4 of 5" in report_text or "4 models (Random Forest, XGBoost" in report_text)
check("TEST14_report_correctly_describes_logistic_as_uncontested",
      "uncontested" in report_text.lower())

print(f"\n{'='*70}\nPHASE 7 THRESHOLD-OVERLAP CLOSURE TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print("\nALL 14 TEST CATEGORIES PASSED.")
sys.exit(0)
