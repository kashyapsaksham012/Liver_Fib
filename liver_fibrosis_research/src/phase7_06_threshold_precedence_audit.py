"""
phase7_06_threshold_precedence_audit.py
Phase 7 threshold-override closure task, Parts 3-9: formal audit of which conformal threshold
was actually applied to each of the 4 mutually exclusive BMI/Age membership states, per model,
traced directly from src/phase7_04_final_test_touch.py's TARGET_COMBINATIONS loop logic (bmi
processed first, age second, numpy array-index overwrite = last-write-wins). Confirmed by direct
code inspection (documented in this task's evidence trail) that no combined/dual threshold rule
exists anywhere in src/phase7_02_mitigation_implementation.py or src/phase7_04_final_test_touch.py.

Does NOT reopen the raw locked test set. Does NOT regenerate predictions. Does NOT recompute
conformal thresholds. Reads exclusively the already-frozen
results/uncertainty/test_set_prediction_sets.csv and results/mitigation/
group_specific_thresholds.csv, applying the identical sequential rule already used by Phase 7
Commit D to attribute, per participant, which threshold actually governed their outcome.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, MODEL_NAMES

RESULTS_DIR = ROOT / "results" / "mitigation"
UNCERTAINTY_DIR = ROOT / "results" / "uncertainty"

pred_sets = pd.read_csv(UNCERTAINTY_DIR / "test_set_prediction_sets.csv")
global_thresh = pd.read_csv(UNCERTAINTY_DIR / "conformal_thresholds_by_model.csv").set_index("model")["threshold"]
group_thresh = pd.read_csv(RESULTS_DIR / "group_specific_thresholds.csv").set_index(["model", "dimension", "category"])

# Exact order from src/phase7_04_final_test_touch.py TARGET_COMBINATIONS -- bmi first, age second
TARGET_COMBINATIONS = [
    ("bmi", "Obese", "_bmi", ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]),
    ("age", "60+", "_age", ["random_forest", "xgboost", "lightgbm", "mlp"]),
]

def prediction_set(y, p, threshold):
    include_pos = (1 - p) <= threshold
    include_neg = p <= threshold
    return np.where(y == 1, include_pos, include_neg)

# ---- Part 4/5/6: formal threshold-precedence table, per model, per membership state ----
precedence_rows = []
for model in MODEL_NAMES:
    is_bmi_target = model in TARGET_COMBINATIONS[0][3]
    is_age_target = model in TARGET_COMBINATIONS[1][3]
    bmi_thresh = group_thresh.loc[(model, "bmi", "Obese"), "group_specific_threshold"] if is_bmi_target else None
    age_thresh = group_thresh.loc[(model, "age", "60+"), "group_specific_threshold"] if is_age_target else None
    g_thresh = global_thresh[model]

    states = [
        ("Neither BMI-Obese nor Age-60+", False, False),
        ("BMI-Obese only", True, False),
        ("Age-60+ only", False, True),
        ("BMI-Obese AND Age-60+", True, True),
    ]
    for state_label, obese, sixty in states:
        if not obese and not sixty:
            rule, applied_thresh, winner = "global (neither is a target)", g_thresh, "global"
        elif obese and not sixty:
            if is_bmi_target:
                rule, applied_thresh, winner = "BMI-specific (only applicable rule)", bmi_thresh, "BMI"
            else:
                rule, applied_thresh, winner = "global (BMI not a target for this model)", g_thresh, "global"
        elif not obese and sixty:
            if is_age_target:
                rule, applied_thresh, winner = "Age-specific (only applicable rule)", age_thresh, "Age"
            else:
                rule, applied_thresh, winner = "global (Age not a target for this model)", g_thresh, "global"
        else:  # both
            if is_bmi_target and is_age_target:
                rule = "BMI computed first, then Age OVERWRITES it (sequential last-write-wins, TARGET_COMBINATIONS order)"
                applied_thresh, winner = age_thresh, "Age (overwrites BMI)"
            elif is_bmi_target and not is_age_target:
                rule, applied_thresh, winner = "BMI-specific (Age never a target for this model, no contest)", bmi_thresh, "BMI (uncontested)"
            elif is_age_target and not is_bmi_target:
                rule, applied_thresh, winner = "Age-specific (BMI never a target for this model, no contest)", age_thresh, "Age (uncontested)"
            else:
                rule, applied_thresh, winner = "global (neither is a target)", g_thresh, "global"

        precedence_rows.append({
            "model": model, "membership_state": state_label, "is_bmi_target_model": is_bmi_target,
            "is_age_target_model": is_age_target, "applicable_rule": rule,
            "applied_threshold": round(applied_thresh, 6) if applied_thresh is not None else None,
            "winner": winner,
        })

precedence_out = pd.DataFrame(precedence_rows)
precedence_out.to_csv(RESULTS_DIR / "threshold_precedence_audit.csv", index=False)

# ---- Part 6: verify the "4/5" claim precisely ----
intersection_rows = precedence_out[precedence_out["membership_state"] == "BMI-Obese AND Age-60+"]
age_overwrites_bmi = intersection_rows[intersection_rows["winner"] == "Age (overwrites BMI)"]
print("=== VERIFY 4/5 CLAIM: models where Age genuinely OVERWRITES BMI (contested precedence) ===")
print(age_overwrites_bmi[["model", "winner"]].to_string(index=False))
print(f"\nCount: {len(age_overwrites_bmi)} of 5 models show genuine Age-overwrites-BMI precedence.")
print("\n=== The 5th model (Logistic): what actually differs ===")
print(intersection_rows[intersection_rows["model"] == "logistic"][["model", "applicable_rule", "winner"]].to_string(index=False))

# ---- Part 7: participant-level intersection audit (N=294), re-derived from frozen artifacts ----
participant_rows = []
for model in MODEL_NAMES:
    m = pred_sets[pred_sets["model"] == model].copy()
    y = m["true_target"].values
    p = m["predicted_probability_positive"].values
    g_thresh = global_thresh[model]

    is_obese = (m["_bmi"] == "Obese").values
    is_60plus = (m["_age"] == "60+").values
    both_mask = is_obese & is_60plus

    before_in_set = m["true_in_set"].values

    after_in_set = before_in_set.copy()
    applied_source = np.full(len(m), "global", dtype=object)
    for dim, category, col, models in TARGET_COMBINATIONS:
        if model not in models:
            continue
        mask = (m[col] == category).values
        thresh = group_thresh.loc[(model, dim, category), "group_specific_threshold"]
        after_in_set[mask] = prediction_set(y[mask], p[mask], thresh)
        applied_source[mask] = dim.upper()

    both_df = m[both_mask].copy()
    both_df["baseline_threshold"] = g_thresh
    both_df["baseline_in_set"] = before_in_set[both_mask]
    both_df["mitigated_threshold_source"] = applied_source[both_mask]
    both_df["mitigated_threshold_value"] = [
        group_thresh.loc[(model, s.lower(), {"BMI": "Obese", "AGE": "60+"}[s]), "group_specific_threshold"] if s != "global" else g_thresh
        for s in applied_source[both_mask]
    ]
    both_df["mitigated_in_set"] = after_in_set[both_mask]
    both_df["model"] = model
    participant_rows.append(both_df[["SEQN", "model", "true_target", "predicted_probability_positive",
                                       "baseline_threshold", "baseline_in_set", "mitigated_threshold_source",
                                       "mitigated_threshold_value", "mitigated_in_set"]])

participant_out = pd.concat(participant_rows, ignore_index=True)
participant_out.to_csv(RESULTS_DIR / "intersection_participant_level_audit.csv", index=False)
print(f"\nSaved results/mitigation/intersection_participant_level_audit.csv ({len(participant_out)} rows = 294 participants x 5 models)")
print(f"Saved results/mitigation/threshold_precedence_audit.csv ({len(precedence_out)} rows)")

# Cross-check: does the source attribution for the intersection match what we already know
# (BMI for logistic, AGE for the other 4)?
source_summary = participant_out.groupby("model")["mitigated_threshold_source"].apply(lambda s: s.unique().tolist())
print("\n=== Mitigated-threshold-source per model, intersection participants only ===")
print(source_summary.to_string())
