"""
phase7_05_bmi_age_overlap_analysis.py
Phase 7 overlap-closure task, Parts 4-9: four-way disaggregation of the ALREADY-FROZEN Phase 7
test-set mitigation output into BMI-Obese-only, Age-60+-only, intersection, and neither.

Does NOT reopen the raw locked test set. Does NOT regenerate predictions. Does NOT recompute
conformal thresholds. Reads exclusively:
  - results/uncertainty/test_set_prediction_sets.csv (frozen Phase 6 Commit C artifact:
    per-participant probability, true outcome, BASELINE/global-threshold set-membership, and
    the exact canonical _bmi/_age subgroup labels already used throughout Phase 5-7)
  - results/mitigation/group_specific_thresholds.csv (frozen Phase 7 Commit C artifact: the
    already-computed group-specific thresholds)

The MITIGATED per-participant status is re-derived by applying these already-frozen thresholds
with the EXACT SAME sequential tie-break order already used by src/phase7_04_final_test_touch.py
(bmi processed before age -- age wins for the intersection population) -- this is a
re-partitioning of already-computed arithmetic, not a new mitigation method or a new test-set
touch.
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
group_thresh = pd.read_csv(RESULTS_DIR / "group_specific_thresholds.csv").set_index(["model", "dimension", "category"])
official_final = pd.read_csv(RESULTS_DIR / "test_set_mitigation_final.csv")

TARGET_COMBINATIONS = [  # same order as phase7_04_final_test_touch.py -- bmi first, age second
    ("bmi", "Obese", "_bmi", ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]),
    ("age", "60+", "_age", ["random_forest", "xgboost", "lightgbm", "mlp"]),
]

def prediction_set(y, p, threshold):
    include_pos = (1 - p) <= threshold
    include_neg = p <= threshold
    return np.where(y == 1, include_pos, include_neg)

rows = []
for model in MODEL_NAMES:
    m = pred_sets[pred_sets["model"] == model].copy()
    y = m["true_target"].values
    p = m["predicted_probability_positive"].values
    before_in_set = m["true_in_set"].values  # already-frozen, global-threshold baseline

    targets_this_model = [t for t in TARGET_COMBINATIONS if model in t[3]]

    # Re-derive AFTER status using the exact same sequential overwrite order as phase7_04
    after_in_set = before_in_set.copy()
    for dim, category, col, models in targets_this_model:
        mask = (m[col] == category).values
        thresh = group_thresh.loc[(model, dim, category), "group_specific_threshold"]
        after_in_set[mask] = prediction_set(y[mask], p[mask], thresh)

    is_obese = (m["_bmi"] == "Obese").values
    is_60plus = (m["_age"] == "60+").values

    four_way = {
        "BMI-Obese only": is_obese & ~is_60plus,
        "Age-60+ only": ~is_obese & is_60plus,
        "Intersection (Obese AND 60+)": is_obese & is_60plus,
        "Neither": ~is_obese & ~is_60plus,
    }

    for label, mask in four_way.items():
        n = int(mask.sum())
        if n == 0:
            continue
        y_g = y[mask]
        n_pos, n_neg = int((y_g == 1).sum()), int((y_g == 0).sum())
        cov_before = float(before_in_set[mask].mean())
        cov_after = float(after_in_set[mask].mean())

        is_bmi_target = model in ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
        is_age_target = model in ["random_forest", "xgboost", "lightgbm", "mlp"]
        mitigation_applies = (label == "BMI-Obese only" and is_bmi_target) or \
                              (label == "Age-60+ only" and is_age_target) or \
                              (label == "Intersection (Obese AND 60+)" and (is_bmi_target or is_age_target)) or \
                              (label == "Neither")

        rows.append({
            "model": model, "mitigation_condition": "baseline_vs_mitigated",
            "subgroup_category": label, "n": n, "positive_n": n_pos, "negative_n": n_neg,
            "baseline_coverage": round(cov_before, 6), "mitigated_coverage": round(cov_after, 6),
            "change_from_baseline_pp": round((cov_after - cov_before) * 100, 4),
            "target_coverage": 0.90,
            "existing_ci": "NOT AVAILABLE FROM EXISTING FROZEN ARTIFACT -- Phase 7 did not compute a CI at this four-way granularity",
            "receives_group_specific_threshold_in_official_run": mitigation_applies and label != "Neither",
            "interpretation_flag": None,  # filled in below
        })

out = pd.DataFrame(rows)

# Part 7: four-way effect classification per model (descriptive, non-causal)
classification_rows = []
for model in MODEL_NAMES:
    sub = out[out["model"] == model].set_index("subgroup_category")
    if "Intersection (Obese AND 60+)" not in sub.index:
        continue  # logistic has no age target, but Obese-only/Intersection/Neither still exist -- keep going
    inter_change = sub.loc["Intersection (Obese AND 60+)", "change_from_baseline_pp"]
    bmi_change = sub.loc["BMI-Obese only", "change_from_baseline_pp"] if "BMI-Obese only" in sub.index else None
    age_change = sub.loc["Age-60+ only", "change_from_baseline_pp"] if "Age-60+ only" in sub.index else None
    neither_change = sub.loc["Neither", "change_from_baseline_pp"] if "Neither" in sub.index else None

    available = [c for c in [bmi_change, age_change] if c is not None]
    max_single = max(available) if available else None

    if max_single is not None and inter_change > max_single + 2.0:  # >2pp materially larger, descriptive threshold stated explicitly in interpretation doc
        pattern = "PATTERN A -- POSSIBLE OVERLAP-ASSOCIATED BENEFIT (descriptive only, not a causal claim)"
    elif max_single is not None and abs(inter_change - max_single) <= 2.0:
        pattern = "PATTERN C -- NO CLEAR EVIDENCE OF AN OVERLAP-SPECIFIC EFFECT"
    elif max_single is not None:
        pattern = "PATTERN B -- CONSISTENT WITH SHARED/ADDITIVE EFFECT"
    else:
        pattern = "PATTERN D -- INDETERMINATE (insufficient comparison groups)"

    classification_rows.append({
        "model": model, "bmi_only_change_pp": bmi_change, "age_only_change_pp": age_change,
        "intersection_change_pp": inter_change, "neither_change_pp": neither_change,
        "pattern_classification": pattern,
    })

    out.loc[(out["model"] == model), "interpretation_flag"] = pattern

class_out = pd.DataFrame(classification_rows)

out.to_csv(RESULTS_DIR / "bmi_age_overlap_four_way_analysis.csv", index=False)
class_out.to_csv(RESULTS_DIR / "bmi_age_overlap_pattern_classification.csv", index=False)

print(out[["model", "subgroup_category", "n", "baseline_coverage", "mitigated_coverage", "change_from_baseline_pp"]].to_string(index=False))
print("\n=== Pattern classification (descriptive, non-causal) ===")
print(class_out.to_string(index=False))
print(f"\nSaved results/mitigation/bmi_age_overlap_four_way_analysis.csv ({len(out)} rows)")
print("Saved results/mitigation/bmi_age_overlap_pattern_classification.csv")

# Cross-check: does the "Obese only" + "Intersection" union reproduce the official aggregate
# "bmi/Obese" N and (for logistic, the only single-dimension-target model) coverage exactly?
logi_obese_official = official_final[(official_final["model"] == "logistic") & (official_final["category"] == "Obese")].iloc[0]
logi_obese_n = out[(out["model"] == "logistic") & (out["subgroup_category"].isin(["BMI-Obese only", "Intersection (Obese AND 60+)"]))]["n"].sum()
print(f"\nCross-check (Logistic, BMI-Obese N): four-way sum={logi_obese_n}, official={logi_obese_official['n']}, match={logi_obese_n == logi_obese_official['n']}")
