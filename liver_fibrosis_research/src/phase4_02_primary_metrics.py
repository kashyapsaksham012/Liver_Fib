"""
phase4_02_primary_metrics.py
Phase 4 Parts 9-13: raw-probability calibration intercept, slope, and Brier score for the
5 primary models (plus MLP_balanced reported separately as sensitivity, never merged into
the primary table), computed EXCLUSIVELY from the CV out-of-fold (OOF) tier per the frozen
protocol's data-separation decision (§6). The locked test set is not touched by this script.

Calibration-in-the-large method (frozen protocol §7, from evaluation_metrics_protocol.md):
logistic recalibration regression of observed outcome on the model's logit(predicted
probability): y ~ 1 + logit(p_hat). Intercept and slope are the fitted coefficients of an
unpenalized logistic regression with a single feature (the logit).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_common import CALIB_RESULTS_DIR, PRIMARY_MODELS, SENSITIVITY_MODEL, load_oof_predictions, NOW, fail

EPS = 1e-12  # clip only to avoid exact 0/1 producing +/-inf logits; does not alter any decision value

def logit(p):
    p_clipped = np.clip(p, EPS, 1 - EPS)
    return np.log(p_clipped / (1 - p_clipped))

def calibration_in_the_large(y, p):
    z = logit(p).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)  # effectively unpenalized; avoids deprecated penalty=None
    reg.fit(z, y)
    intercept = float(reg.intercept_[0])
    slope = float(reg.coef_[0][0])
    return intercept, slope

rows = []
n_clipped_total = 0
for name in PRIMARY_MODELS + [SENSITIVITY_MODEL]:
    df = load_oof_predictions(name)
    y = df["true_target"].values
    p = df["predicted_probability"].values
    n_at_boundary = int(((p <= EPS) | (p >= 1 - EPS)).sum())
    n_clipped_total += n_at_boundary
    intercept, slope = calibration_in_the_large(y, p)
    brier = brier_score_loss(y, p)
    rows.append({
        "model": name,
        "status": "PRIMARY" if name in PRIMARY_MODELS else "SENSITIVITY (MLP_balanced, not primary)",
        "data_source": "CV out-of-fold predictions (train partition, N=5007)",
        "n": len(df),
        "calibration_intercept": round(intercept, 6),
        "calibration_slope": round(slope, 6),
        "brier_score": round(brier, 6),
        "n_probabilities_clipped_for_logit": n_at_boundary,
    })

out = pd.DataFrame(rows)
out.insert(0, "generated", NOW)

primary_out = out[out["status"] == "PRIMARY"].drop(columns=["status"])
primary_out.to_csv(CALIB_RESULTS_DIR / "primary_metrics_by_model.csv", index=False)

brier_out = out[["generated", "model", "status", "data_source", "n", "brier_score"]]
brier_out.to_csv(CALIB_RESULTS_DIR / "brier_scores.csv", index=False)

print(out.to_string(index=False))
print(f"\nTotal probabilities clipped for logit computation (near-0/near-1 boundary): {n_clipped_total}")
print("\nSaved: results/calibration/primary_metrics_by_model.csv (5 PRIMARY models only)")
print("Saved: results/calibration/brier_scores.csv (5 PRIMARY models + MLP_balanced sensitivity, clearly labeled)")
