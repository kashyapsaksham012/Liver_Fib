"""
cb_06_calibration.py
E1 (part 4, added to close the gap against REVISION_PLAN.md's original E1 spec, which names
calibration alongside discrimination/subgroup-sensitivity/conformal coverage). Mirrors
phase4_09_final_test_set_calibration.py's exact diagnostics: calibration-in-the-large
(intercept + slope via an unregularized logistic regression of y on logit(p)), Brier score,
and the 10-bin (decile) ECE -- for a "raw" and a "recalibrated" variant, computed on the
locked test set.

FIB-4 has no native probability (same caveat as cb_04_conformal.py), so:
  - "raw"          = the auxiliary univariate logistic from cb_04 (fit on proper_train_ids,
                      N=4005, only), applied directly to the locked test set.
  - "recalibrated" = a second-stage calibration-in-the-large correction, fit on the
                      auxiliary logistic's predictions on conformal_calibration_ids (N=1002)
                      -- data the auxiliary logistic never trained on -- then applied to the
                      locked test set. This plays the same role the OOF-fit Platt transform
                      plays for the five ML models (a correction fit on genuinely held-out
                      predictions, never on the evaluation set).
Both variants are refit here deterministically from cb_01's frozen fib4_scores.csv (the
auxiliary logistic has no random component beyond a fixed random_state, already confirmed
bit-for-bit reproducible against cb_04's saved outputs).

Output: results/clinical_baselines/fib4_calibration.csv
        results/clinical_baselines/fib4_calibration_curve_data.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, RANDOM_SEED, PRIMARY_OUTCOME_COL

OUT_DIR = ROOT / "results" / "clinical_baselines"
N_CALIBRATION_BINS = 10
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

def decile_curve(y, p, variant_label):
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
    agg.insert(0, "score_name", "FIB-4")
    n = len(df)
    ece = float((agg["n_in_bin"] / n * (agg["mean_predicted_probability"] - agg["observed_event_rate"]).abs()).sum())
    return agg, ece, n_bins_achieved, degenerate

scores = pd.read_csv(OUT_DIR / "fib4_scores.csv")
proper_train = scores[scores["split"] == "proper_train"]
cal = scores[scores["split"] == "conformal_calibration"]
test = scores[scores["split"] == "test"]
assert len(proper_train) == 4005 and len(cal) == 1002 and len(test) == 2146

# Refit the identical auxiliary logistic from cb_04 (deterministic; verified bit-for-bit
# reproducible against cb_04's saved outputs before this script was written).
clf = LogisticRegression(random_state=RANDOM_SEED)
clf.fit(proper_train[["fib4"]].values, proper_train[PRIMARY_OUTCOME_COL].values)

p_raw_cal = clf.predict_proba(cal[["fib4"]].values)[:, 1]
y_cal = cal[PRIMARY_OUTCOME_COL].values
recal_intc, recal_slope = cal_in_the_large(y_cal, p_raw_cal)
print(f"Second-stage recalibration (fit on conformal_calibration, N={len(cal)}, held-out from "
      f"the auxiliary logistic's own training): intercept={recal_intc:.4f}, slope={recal_slope:.4f}")

p_raw_test = clf.predict_proba(test[["fib4"]].values)[:, 1]
y_test = test[PRIMARY_OUTCOME_COL].values
p_recal_test = sigmoid(recal_intc + recal_slope * logit(p_raw_test))

metric_rows, curve_rows = [], []
for variant, p in [("raw", p_raw_test), ("recalibrated", p_recal_test)]:
    cil_intc, cil_slope = cal_in_the_large(y_test, p)
    brier = brier_score_loss(y_test, p)
    agg, ece, n_bins_achieved, degenerate = decile_curve(y_test, p, variant)
    curve_rows.append(agg)
    metric_rows.append({
        "score_name": "FIB-4", "variant": variant, "n": len(test),
        "calibration_intercept": round(cil_intc, 6), "calibration_slope": round(cil_slope, 6),
        "brier_score": round(brier, 6), "ece": round(ece, 6),
        "n_bins_achieved": n_bins_achieved, "binning_degenerate": degenerate,
        "note": ("auxiliary univariate logistic (FIB-4 -> P), fit on proper_train N=4005 only"
                 if variant == "raw" else
                 "raw + second-stage calibration-in-the-large correction fit on conformal_calibration N=1002 (held out from the auxiliary fit)"),
    })

metrics_out = pd.DataFrame(metric_rows)
metrics_out.to_csv(OUT_DIR / "fib4_calibration.csv", index=False)
pd.concat(curve_rows, ignore_index=True).to_csv(OUT_DIR / "fib4_calibration_curve_data.csv", index=False)

print(metrics_out.to_string(index=False))
print("\nSaved results/clinical_baselines/fib4_calibration.csv")
print("Saved results/clinical_baselines/fib4_calibration_curve_data.csv")
