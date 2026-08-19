"""
phase7_02_mitigation_implementation.py
Project Phase 7 (Mitigation) Part 5: implement the frozen method (group-wise/Mondrian conformal
calibration) for the 9 frozen target (model, subgroup) combinations. Uses ONLY the existing
conformal_calibration_ids.csv (Phase 6 Commit B, N=1,002), filtered to each target subgroup.
No model refitting. No test-set access. Original Phase 3/4/5/6 artifacts are not touched --
mitigated thresholds are new, separate artifacts.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, SPLIT_DIR, MODEL_NAMES, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL
from phase3_common import load_primary_dataset, fail
from phase5_common import SEX_MAP, RACE_MAP_RIDRETH3, bin_age, bin_bmi

REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"
RESULTS_DIR = ROOT / "results" / "mitigation"
ALPHA = 0.10

TARGET_COMBINATIONS = [
    ("bmi", "Obese", ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]),
    ("age", "60+", ["random_forest", "xgboost", "lightgbm", "mlp"]),
]

master = load_primary_dataset()
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])
cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)
if len(cal_df) != 1002:
    fail(f"conformal_calibration join produced {len(cal_df)} rows, expected 1002")

test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
if cal_df["SEQN"].isin(test_ids).any():
    fail("Test-set participant found in conformal calibration set -- CRITICAL")

cal_df["_bmi"] = cal_df["BMXBMI"].apply(bin_bmi)
cal_df["_age"] = cal_df["RIDAGEYR"].apply(bin_age)
DIM_COL = {"bmi": "_bmi", "age": "_age"}

global_thresholds = pd.read_csv(ROOT / "results" / "uncertainty" / "conformal_thresholds_by_model.csv").set_index("model")["threshold"]

rows = []
for dim, category, models in TARGET_COMBINATIONS:
    col = DIM_COL[dim]
    sub_cal = cal_df[cal_df[col] == category]
    n_group = len(sub_cal)
    X_group = sub_cal[PRIMARY_PREDICTORS]
    y_group = sub_cal[PRIMARY_OUTCOME_COL].values
    n_pos_group = int(y_group.sum())

    for model in models:
        refit = joblib.load(REFIT_DIR / f"model_{model}_proper_train_refit.joblib")
        pipe = refit["pipeline"]
        proba_pos = pipe.predict_proba(X_group)[:, 1]

        if np.isnan(proba_pos).any() or np.isinf(proba_pos).any():
            fail(f"{model}/{dim}={category}: NaN/Inf in group calibration predictions")

        proba_true_class = np.where(y_group == 1, proba_pos, 1 - proba_pos)
        scores = 1 - proba_true_class

        k = int(np.ceil((n_group + 1) * (1 - ALPHA)))
        sorted_scores = np.sort(scores)
        if k > n_group:
            group_threshold = np.inf
            q_level = 1.0
        else:
            group_threshold = float(sorted_scores[k - 1])
            q_level = k / n_group

        rows.append({
            "model": model, "dimension": dim, "category": category,
            "calibration_n_group": n_group, "calibration_positives_group": n_pos_group,
            "calibration_negatives_group": n_group - n_pos_group,
            "target_coverage": 0.90, "quantile_level": round(q_level, 6),
            "group_specific_threshold": round(group_threshold, 6),
            "original_global_threshold": global_thresholds[model],
            "threshold_change": round(group_threshold - global_thresholds[model], 6),
            "method": "group-wise (Mondrian) conformal calibration",
            "training_source": "unchanged -- reuses models/phase6_conformal_refit/*.joblib (proper_train_ids.csv, N=4005)",
            "calibration_source": f"conformal_calibration_ids.csv subgroup slice ({dim}={category}, N={n_group})",
            "seed": 42,
        })

out = pd.DataFrame(rows)
out.to_csv(RESULTS_DIR / "group_specific_thresholds.csv", index=False)
print(out.to_string(index=False))
print(f"\nSaved results/mitigation/group_specific_thresholds.csv ({len(out)} rows)")
print("\nPASS: 9 group-specific conformal thresholds computed. No model refit occurred. No test-set data was accessed.")
