"""
phase6_03_conformal_calibration.py
Phase 6 Parts 6-7: generate calibration-set predictions from the refit (proper-train-only)
models, compute the frozen nonconformity score (1 - P(true class)), and derive the conformal
threshold at the frozen 90% target coverage using the standard finite-sample-corrected
quantile: q_hat = the ceil((n+1)*(1-alpha))/n order statistic of the calibration scores.
Amendment #10/#11 (Wilson CI, Phase 6 FDR family) do not affect this script -- they govern
downstream inference only.
"""
import sys
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, SPLIT_DIR, MODEL_NAMES, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL
from phase3_common import load_primary_dataset, fail

REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"
RESULTS_DIR = ROOT / "results" / "uncertainty"
TARGET_COVERAGE = 0.90
ALPHA = 1 - TARGET_COVERAGE

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

master = load_primary_dataset()
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])
cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)
if len(cal_df) != 1002:
    fail(f"conformal_calibration join produced {len(cal_df)} rows, expected 1002")

test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
if cal_df["SEQN"].isin(test_ids).any():
    fail("Test-set participant found in conformal calibration set -- CRITICAL")

X_cal = cal_df[PRIMARY_PREDICTORS]
y_cal = cal_df[PRIMARY_OUTCOME_COL].values
n_cal = len(cal_df)

threshold_rows = []
all_scores = {}
for name in MODEL_NAMES:
    refit = joblib.load(REFIT_DIR / f"model_{name}_proper_train_refit.joblib")
    pipe = refit["pipeline"]
    proba_pos = pipe.predict_proba(X_cal)[:, 1]

    if np.isnan(proba_pos).any() or np.isinf(proba_pos).any():
        fail(f"{name}: NaN/Inf in calibration-set predictions")
    if not ((proba_pos >= 0) & (proba_pos <= 1)).all():
        fail(f"{name}: calibration-set probabilities out of [0,1] range")

    # Nonconformity score for the TRUE class: 1 - P(true class | x)
    proba_true_class = np.where(y_cal == 1, proba_pos, 1 - proba_pos)
    scores = 1 - proba_true_class
    all_scores[name] = scores

    # Standard finite-sample-corrected conformal quantile (Vovk et al.): threshold is the
    # k-th smallest calibration score, k = ceil((n+1)*(1-alpha)) -- direct order-statistic
    # indexing, not numpy's quantile-interpolation methods, to avoid any off-by-one ambiguity.
    k = int(np.ceil((n_cal + 1) * (1 - ALPHA)))
    sorted_scores = np.sort(scores)
    if k > n_cal:
        threshold = np.inf  # coverage target not achievable at finite n -- would require the trivial full set
        q_level = 1.0
    else:
        threshold = sorted_scores[k - 1]  # k is 1-indexed
        q_level = k / n_cal

    threshold_rows.append({
        "model": name, "calibration_n": n_cal, "calibration_positives": int(y_cal.sum()),
        "calibration_negatives": int((y_cal == 0).sum()), "target_coverage": TARGET_COVERAGE,
        "score_definition": "1 - P(y=true_class | x), standard split-conformal binary score",
        "quantile_level_finite_sample_corrected": round(q_level, 6),
        "threshold": round(float(threshold), 6),
        "mean_score": round(float(scores.mean()), 6), "median_score": round(float(np.median(scores)), 6),
    })

    cal_score_df = pd.DataFrame({"SEQN": cal_df["SEQN"].values, "true_target": y_cal,
                                  "predicted_probability_positive": proba_pos, "nonconformity_score": scores})
    cal_score_df.to_csv(RESULTS_DIR / f"calibration_scores_{name}.csv", index=False)

out = pd.DataFrame(threshold_rows)
protocol_hash = sha256(ROOT / "documentation" / "phase2" / "uncertainty_protocol.md")
out.insert(0, "protocol_hash", protocol_hash)
out.to_csv(RESULTS_DIR / "conformal_thresholds_by_model.csv", index=False)
print(out.drop(columns=["protocol_hash"]).to_string(index=False))
print(f"\nSaved results/uncertainty/conformal_thresholds_by_model.csv")
print("Saved per-model calibration_scores_<model>.csv (all calibration scores preserved)")
print("\nPASS: nonconformity scores and conformal thresholds computed for all 5 refit models.")
print("Test-set outcomes were NOT inspected at any point in this script.")
