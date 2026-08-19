"""
phase4_01_prediction_input_audit.py
Phase 4 Part 7: verify integrity of the OOF (development) and locked-test (confirmatory)
prediction inputs for all 5 primary models, before any calibration metric is computed.
Writes results/calibration/phase4_prediction_input_audit.csv.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_common import (
    CALIB_RESULTS_DIR, PRIMARY_MODELS, SENSITIVITY_MODEL,
    load_oof_predictions, load_test_predictions, fail, NOW,
)

rows = []

def audit_one(name, tier, df):
    n = len(df)
    n_unique = df["SEQN"].nunique()
    n_missing_prob = df["predicted_probability"].isna().sum()
    n_inf = np.isinf(df["predicted_probability"]).sum()
    prob_min = df["predicted_probability"].min()
    prob_max = df["predicted_probability"].max()
    in_range = df["predicted_probability"].between(0, 1, inclusive="both").all()
    n_missing_target = df["true_target"].isna().sum()
    target_values = sorted(df["true_target"].dropna().unique().tolist())
    n_pos = int((df["true_target"] == 1).sum())
    n_neg = int((df["true_target"] == 0).sum())
    rows.append({
        "model": name, "tier": tier, "n_rows": n, "n_unique_seqn": n_unique,
        "one_row_per_participant": n == n_unique,
        "n_missing_probability": int(n_missing_prob), "n_inf_probability": int(n_inf),
        "probability_min": prob_min, "probability_max": prob_max,
        "probability_in_0_1": bool(in_range),
        "n_missing_target": int(n_missing_target), "target_values": str(target_values),
        "target_binary_0_1": target_values == [0, 1],
        "n_positive": n_pos, "n_negative": n_neg,
        "prevalence_pct": round(100 * n_pos / n, 4),
    })

for name in PRIMARY_MODELS + [SENSITIVITY_MODEL]:
    oof = load_oof_predictions(name)
    audit_one(name, "OOF (development)", oof)
    test = load_test_predictions(name)
    audit_one(name, "locked test (confirmatory)", test)

out = pd.DataFrame(rows)

# Cross-model consistency checks: same participant set and same target across all 5 primary models per tier
for tier in ["OOF (development)", "locked test (confirmatory)"]:
    tier_df = out[out["tier"] == tier]
    primary_only = tier_df[tier_df["model"].isin(["logistic", "random_forest", "xgboost", "lightgbm", "mlp"])]
    if primary_only["n_rows"].nunique() != 1:
        fail(f"Row-count mismatch across primary models in tier '{tier}': {primary_only[['model','n_rows']].to_dict('records')}")
    if primary_only["n_positive"].nunique() != 1:
        fail(f"Positive-count mismatch across primary models in tier '{tier}' -- target inconsistency: {primary_only[['model','n_positive']].to_dict('records')}")

any_fail = False
if not out["one_row_per_participant"].all():
    print("FAIL: duplicate participant rows found"); any_fail = True
if (out["n_missing_probability"] > 0).any():
    print("FAIL: missing probabilities found"); any_fail = True
if (out["n_inf_probability"] > 0).any():
    print("FAIL: infinite probabilities found"); any_fail = True
if not out["probability_in_0_1"].all():
    print("FAIL: probabilities outside [0,1] found"); any_fail = True
if (out["n_missing_target"] > 0).any():
    print("FAIL: missing targets found"); any_fail = True
if not out["target_binary_0_1"].all():
    print("FAIL: non-binary target values found"); any_fail = True

out.insert(0, "generated", NOW)
out.to_csv(CALIB_RESULTS_DIR / "phase4_prediction_input_audit.csv", index=False)
print(out.to_string(index=False))

if any_fail:
    fail("Prediction-input integrity audit failed -- see FAIL lines above.")
print("\nPASS: all prediction-input integrity checks passed for all 5 primary models + MLP_balanced sensitivity model.")
