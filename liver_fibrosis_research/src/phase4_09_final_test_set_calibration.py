"""
phase4_09_final_test_set_calibration.py
Phase 4 Part 21: THE FIRST AND ONLY TEST-SET TOUCH for final Calibration assessment.

Applies the frozen Phase 3 model probabilities (test_predictions_<model>.csv, already
generated in Phase 3, read-only) and the OOF-fit Platt recalibration transform (fit
exclusively on OOF in phase4_05, never refit here) to the locked test set. Computes final
test-set calibration metrics -- primary (intercept, slope, Brier) and secondary (10-decile
curve, ECE) -- for both RAW and RECALIBRATED probabilities, in a single execution.

This script must run exactly once. No methodology decision is made here -- every choice
(metrics, binning, recalibration transform parameters) was already frozen/fit before this
script exists.
"""
import sys
import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_common import (
    CALIB_RESULTS_DIR, CALIB_CURVE_DATA_DIR, PRIMARY_MODELS, N_CALIBRATION_BINS,
    load_test_predictions, CALIBRATION_PROTOCOL_COMMIT, CALIBRATION_PROTOCOL_CHECKSUM,
)

EPS = 1e-12

def logit(p):
    pc = np.clip(p, EPS, 1 - EPS)
    return np.log(pc / (1 - pc))

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def cal_in_the_large(y, p):
    z = logit(p).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])

def decile_curve(y, p, model_label, variant_label):
    try:
        bin_id, edges = pd.qcut(p, q=N_CALIBRATION_BINS, retbins=True, duplicates="raise")
        n_bins_achieved, degenerate = N_CALIBRATION_BINS, False
    except ValueError:
        bin_id, edges = pd.qcut(p, q=N_CALIBRATION_BINS, retbins=True, duplicates="drop")
        n_bins_achieved, degenerate = len(edges) - 1, True
    df = pd.DataFrame({"predicted_probability": p, "true_target": y, "bin": bin_id})
    agg = df.groupby("bin", observed=True).agg(
        n_in_bin=("true_target", "size"),
        mean_predicted_probability=("predicted_probability", "mean"),
        observed_event_rate=("true_target", "mean"),
    ).reset_index(drop=True)
    agg.insert(0, "bin_index", range(1, len(agg) + 1))
    agg.insert(0, "variant", variant_label)
    agg.insert(0, "model", model_label)
    n = len(df)
    ece = float((agg["n_in_bin"] / n * (agg["mean_predicted_probability"] - agg["observed_event_rate"]).abs()).sum())
    return agg, ece, n_bins_achieved, degenerate

# Read the OOF-fit Platt parameters (fit exclusively on OOF in phase4_05 -- read-only here, never refit)
platt_params = pd.read_csv(CALIB_RESULTS_DIR / "recalibration_pre_post_comparison.csv").set_index("model")[["platt_fit_intercept", "platt_fit_slope"]]

TOUCH_TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

metric_rows = []
curve_rows = []
recal_pred_rows = []

for name in PRIMARY_MODELS:
    df = load_test_predictions(name)
    y = df["true_target"].values
    p_raw = df["predicted_probability"].values
    n = len(df)

    intc, slope = platt_params.loc[name, "platt_fit_intercept"], platt_params.loc[name, "platt_fit_slope"]
    p_recal = sigmoid(intc + slope * logit(p_raw))

    for variant, p in [("raw", p_raw), ("recalibrated", p_recal)]:
        cil_intc, cil_slope = cal_in_the_large(y, p)
        brier = brier_score_loss(y, p)
        metric_rows.append({
            "touch_timestamp": TOUCH_TIMESTAMP, "model": name, "variant": variant,
            "data_source": "locked test set (N=2146), one-time confirmatory scoring",
            "n": n, "calibration_intercept": round(cil_intc, 6), "calibration_slope": round(cil_slope, 6),
            "brier_score": round(brier, 6),
        })
        agg, ece, n_bins_achieved, degenerate = decile_curve(y, p, name, variant)
        curve_rows.append(agg)
        metric_rows[-1]["ece"] = round(ece, 6)
        metric_rows[-1]["n_bins_achieved"] = n_bins_achieved
        metric_rows[-1]["binning_degenerate"] = degenerate

    recal_pred_rows.append(pd.DataFrame({
        "SEQN": df["SEQN"].values, "true_target": y,
        "raw_predicted_probability": p_raw, "recalibrated_predicted_probability": p_recal,
        "platt_intercept_source": "fit on OOF in phase4_05, applied here unchanged",
        "platt_intercept": intc, "platt_slope": slope, "model": name,
    }))

metrics_out = pd.DataFrame(metric_rows)
metrics_out.insert(0, "protocol_commit", CALIBRATION_PROTOCOL_COMMIT)
metrics_out.insert(1, "protocol_checksum", CALIBRATION_PROTOCOL_CHECKSUM)
metrics_out.to_csv(CALIB_RESULTS_DIR / "test_set_calibration_final.csv", index=False)

pd.concat(curve_rows, ignore_index=True).to_csv(CALIB_CURVE_DATA_DIR / "curve_data_test_set_final.csv", index=False)
pd.concat(recal_pred_rows, ignore_index=True).to_csv(CALIB_RESULTS_DIR / "test_set_recalibrated_predictions.csv", index=False)

print(metrics_out.to_string(index=False))
print(f"\nTest-set touch timestamp: {TOUCH_TIMESTAMP}")
print("Saved results/calibration/test_set_calibration_final.csv")
print("Saved results/calibration/curve_data/curve_data_test_set_final.csv")
print("Saved results/calibration/test_set_recalibrated_predictions.csv")
print("\nTHIS IS THE FIRST AND ONLY TEST-SET TOUCH FOR FINAL CALIBRATION ASSESSMENT. Do not re-run.")
