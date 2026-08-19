"""
phase4_05_recalibration.py
Phase 4 Parts 19-20: recalibration, authorized per Protocol Amendment #8
(documentation/end_to_end/protocol_amendment_registry.md) -- logistic (Platt-type)
recalibration, fit EXCLUSIVELY on OOF predictions, applied uniformly to all 5 primary models.

Recalibration mapping: p_recal = sigmoid(intercept + slope * logit(p_raw)), where intercept
and slope are the calibration-in-the-large parameters already fit in phase4_02 on the OOF
tier. This IS the standard Platt-scaling transform (a 1-feature logistic regression of the
outcome on logit(p_raw)) -- no new fitting procedure is introduced beyond what §7 already
computed; this script reuses those exact fitted parameters as a transform and re-evaluates
metrics under it.

Original (raw) OOF predictions are never overwritten. Recalibrated predictions are saved as a
separate, clearly labeled artifact.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_common import CALIB_RESULTS_DIR, PRIMARY_MODELS, load_oof_predictions, NOW

EPS = 1e-12

def logit(p):
    pc = np.clip(p, EPS, 1 - EPS)
    return np.log(pc / (1 - pc))

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def fit_platt(y, p):
    z = logit(p).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])

rows = []
for name in PRIMARY_MODELS:
    df = load_oof_predictions(name)
    y = df["true_target"].values
    p_raw = df["predicted_probability"].values

    intercept, slope = fit_platt(y, p_raw)  # fit on OOF only
    p_recal = sigmoid(intercept + slope * logit(p_raw))

    # Save recalibrated OOF predictions as a separate artifact (raw file untouched)
    recal_df = pd.DataFrame({
        "SEQN": df["SEQN"].values, "true_target": y,
        "raw_predicted_probability": p_raw, "recalibrated_predicted_probability": p_recal,
        "platt_intercept": intercept, "platt_slope": slope,
    })
    recal_df.to_csv(CALIB_RESULTS_DIR / f"recalibrated_oof_predictions_{name}.csv", index=False)

    # Post-recalibration diagnostics on the SAME OOF data (pre/post comparison, Part 20)
    post_intercept, post_slope = fit_platt(y, p_recal)
    brier_raw = brier_score_loss(y, p_raw)
    brier_recal = brier_score_loss(y, p_recal)

    rows.append({
        "generated": NOW, "model": name, "data_source": "CV out-of-fold predictions (train partition, N=5007)",
        "platt_fit_intercept": round(intercept, 6), "platt_fit_slope": round(slope, 6),
        "raw_calibration_intercept": round(intercept, 6),  # identical to platt_fit_intercept -- reused, not refit
        "raw_calibration_slope": round(slope, 6),
        "recalibrated_calibration_intercept": round(post_intercept, 6),
        "recalibrated_calibration_slope": round(post_slope, 6),
        "raw_brier": round(brier_raw, 6), "recalibrated_brier": round(brier_recal, 6),
        "brier_change": round(brier_recal - brier_raw, 6),
    })

out = pd.DataFrame(rows)
out.to_csv(CALIB_RESULTS_DIR / "recalibration_pre_post_comparison.csv", index=False)
print(out.to_string(index=False))
print(f"\nSaved recalibrated OOF predictions for {len(PRIMARY_MODELS)} primary models (separate files, originals untouched).")
print("Saved results/calibration/recalibration_pre_post_comparison.csv")
print("\nNote: post-recalibration intercept/slope on the SAME data used to fit the transform are")
print("expected to be ~(0, 1) by construction (this is a property of Platt scaling, not new evidence")
print("of quality -- genuine held-out evidence of recalibration benefit is deferred to the one-time")
print("locked test-set touch (Part 21), which is the only place an honest out-of-sample check exists.")
