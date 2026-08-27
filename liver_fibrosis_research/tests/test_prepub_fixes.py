"""
tests/test_prepub_fixes.py
Amendment #18 (pre-publication fixes) — validation of Fix 1 (model-fit alignment) and
Fix 2 (VCTE reference-standard measurement-bias sensitivity).

Standalone script (project convention). Run directly:
    python3 tests/test_prepub_fixes.py

Checks: leakage (test disjoint from calibration / proper-train), single non-iterative run per
script, bit-for-bit reproducibility (seed 42), count identities, and the pre-registered decision
rules. Operates on committed CSVs plus a clean re-run of the two analysis scripts.
"""
import subprocess
import sys
import hashlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "prepublication_fixes"
SPLITS = ROOT / "data" / "processed" / "splits"

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ids(name):
    return set(pd.read_csv(SPLITS / name)["SEQN"].astype("int64"))


# ----------------------------------------------------------------------------
# TEST 1-2: leakage pre-check (the Fix-1 script asserts this; re-assert here)
# ----------------------------------------------------------------------------
test_ids = ids("test_ids.csv")
cal_ids = ids("conformal_calibration_ids.csv")
pt_ids = ids("proper_train_ids.csv")
check("TEST1_test_disjoint_from_calibration", len(test_ids & cal_ids) == 0,
      f"overlap={len(test_ids & cal_ids)}")
check("TEST2_test_disjoint_from_proper_train", len(test_ids & pt_ids) == 0,
      f"overlap={len(test_ids & pt_ids)}")

# ----------------------------------------------------------------------------
# TEST 3: count identities — Fix 2 stiffness-threshold relabel positive counts
# (plan §2.9: 200/22/140 at >=8.2 ; 7 Normal-BMI positives at >=12)
# ----------------------------------------------------------------------------
c1 = pd.read_csv(OUT / "fix2_gap_by_stiffness_threshold.csv")
bmi = c1[c1.dimension == "bmi"]
at82 = bmi[bmi.cut_kPa == 8.2].iloc[0]
check("TEST3a_obese_positives_ge8.2_is_140", int(at82.nA_pos) == 140, f"{int(at82.nA_pos)}")
check("TEST3b_normal_positives_ge8.2_is_22", int(at82.nB_pos) == 22, f"{int(at82.nB_pos)}")
normal_counts = [int(bmi[bmi.cut_kPa == c].iloc[0].nB_pos) for c in [8.2, 9.7, 10.0, 12.0, 13.6]]
check("TEST3c_normal_positive_collapse_22_11_9_7_6", normal_counts == [22, 11, 9, 7, 6], f"{normal_counts}")

# ----------------------------------------------------------------------------
# TEST 4: Fix 1 decision rule (STRENGTHENING) reproduces from the comparison table
# ----------------------------------------------------------------------------
cmp = pd.read_csv(OUT / "fix1_comparison_table.csv")
ct_neg = int((cmp["refit_conformal_sensitivity_gap_pp"] <= -15).sum())
cl_neg = int((cmp["refit_classification_gap_at_tau_star_pp"] <= -15).sum())
check("TEST4a_refit_conformal_gap_le_-15_for_ge4_models", ct_neg >= 4, f"{ct_neg}/5")
check("TEST4b_refit_classification_gap_le_-15_for_ge4_models", cl_neg >= 4, f"{cl_neg}/5")
check("TEST4c_verdict_strengthening", ct_neg >= 4 and cl_neg >= 4)

# ----------------------------------------------------------------------------
# TEST 5: Fix 2 BMI-shortcut — is_obese coefficient positive and significant, 5/5
# ----------------------------------------------------------------------------
c4 = pd.read_csv(OUT / "fix2_bmi_shortcut_check.csv")
check("TEST5a_bmi_shortcut_beta_positive_5of5", bool((c4["beta_is_obese"] > 0).all()),
      f"min={c4['beta_is_obese'].min():.3f}")
check("TEST5b_bmi_shortcut_beta_in_0.15_0.40", bool(c4["beta_is_obese"].between(0.15, 0.40).all()))
check("TEST5c_bmi_shortcut_p_lt_0.001_5of5", bool((c4["p_value"] < 0.001).all()))

# ----------------------------------------------------------------------------
# TEST 6: Fix 2 verdict V3 — Normal-BMI positives at >=12 kPa < 8
# ----------------------------------------------------------------------------
check("TEST6_verdict_V3_normal_bmi_underpowered", normal_counts[3] < 8, f"n={normal_counts[3]}")

# ----------------------------------------------------------------------------
# TEST 7: Fix 2 obese-side stability (C2) — |delta obese sensitivity| small
# ----------------------------------------------------------------------------
c2 = pd.read_csv(OUT / "fix2_obese_side_highpower.csv")
check("TEST7_obese_sensitivity_stable_ge12_vs_ge8.2", c2["delta_obese_sens"].abs().median() <= 0.10,
      f"median|delta|={c2['delta_obese_sens'].abs().median():.3f}")

# ----------------------------------------------------------------------------
# TEST 8: BMI-Obese conformal under-coverage persists under stricter labels (C5)
# ----------------------------------------------------------------------------
c5 = pd.read_csv(OUT / "fix2_coverage_under_stricter_labels.csv")
obese12 = c5[(c5.category == "Obese") & (c5.positive_cut_kPa == 12.0)]
n_under = int((obese12["coverage"] < 0.90).sum())
check("TEST8_bmi_obese_undercovers_at_ge12_for_ge4_models", n_under >= 4, f"{n_under}/5")

# ----------------------------------------------------------------------------
# TEST 9-10: bit-for-bit reproducibility (seed 42) — re-run both scripts, compare hashes
# ----------------------------------------------------------------------------
FIX_OUTPUTS = [
    "fix1_youden_thresholds.csv", "fix1_comparison_table.csv", "fix1_threshold_robustness.csv",
    "fix1_refit_subgroup_sensitivity.csv", "fix1_refit_gaps.csv",
    "fix2_gap_by_stiffness_threshold.csv", "fix2_obese_side_highpower.csv",
    "fix2_stiffness_stratified.csv", "fix2_bmi_shortcut_check.csv",
    "fix2_coverage_under_stricter_labels.csv",
]
before = {f: sha256(OUT / f) for f in FIX_OUTPUTS}
r1 = subprocess.run([sys.executable, str(ROOT / "src" / "prepub_01_model_fit_alignment.py")],
                    capture_output=True, text=True)
r2 = subprocess.run([sys.executable, str(ROOT / "src" / "prepub_02_vcte_bias_sensitivity.py")],
                    capture_output=True, text=True)
check("TEST9a_fix1_script_runs_clean", r1.returncode == 0, r1.stderr[-300:])
check("TEST9b_fix2_script_runs_clean", r2.returncode == 0, r2.stderr[-300:])
after = {f: sha256(OUT / f) for f in FIX_OUTPUTS}
unchanged = [f for f in FIX_OUTPUTS if before[f] == after[f]]
check("TEST10_all_outputs_reproduce_bit_for_bit", len(unchanged) == len(FIX_OUTPUTS),
      f"{len(unchanged)}/{len(FIX_OUTPUTS)} unchanged; changed={set(FIX_OUTPUTS)-set(unchanged)}")

# ----------------------------------------------------------------------------
# TEST 11: no model artifact is loaded / written by either script (frozen-scope)
# ----------------------------------------------------------------------------
for s in ["prepub_01_model_fit_alignment.py", "prepub_02_vcte_bias_sensitivity.py"]:
    src = (ROOT / "src" / s).read_text()
    check(f"TEST11_{s}_no_joblib_load", "joblib.load" not in src and "joblib.dump" not in src)

# ----------------------------------------------------------------------------
print()
print(f"{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    for n, d in FAIL:
        print(f"  FAILED: {n}  {d}")
    sys.exit(1)
print("ALL PREPUB-FIX TESTS PASSED")
