"""
phase7_04_final_test_touch.py
Project Phase 7 Part 7: THE SINGLE OFFICIAL TEST-SET MITIGATION EVALUATION.

Preconditions verified before running: justification frozen (Commit A), protocol committed
standalone (Commit B, 81791db), implementation complete (Commit C), pre-test evaluation complete
(Commit C), test-set hash re-verified unchanged, no methodology selection occurred using test
results (pre-test evaluation used calibration data only).

Reads the already-frozen Phase 6 test-set-touch artifact (results/uncertainty/
test_set_prediction_sets.csv) -- constructing and evaluating NEW prediction sets under the
group-specific thresholds against test-set true outcomes for the first time is what makes this
script the single official Phase 7 test-set touch, not a re-scoring of the raw test set (probabilities
are unchanged, reused from the already-frozen Phase 6 artifact).

Computes, in one execution, no iteration: BEFORE vs AFTER for all 9 target combinations across
every required metric (Part 8), plus non-target subgroup protection checks (Part 8A) and marginal
coverage tolerance checks (protocol Part 8).
"""
import sys
import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.linear_model import LogisticRegression
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, MODEL_NAMES
from phase5_common import FROZEN_THRESHOLDS  # Youden's J classification thresholds -- unrelated to, and untouched by, the conformal nonconformity threshold this mitigation modifies

RESULTS_DIR = ROOT / "results" / "mitigation"
UNCERTAINTY_DIR = ROOT / "results" / "uncertainty"
EPS = 1e-12

def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def logit(p):
    pc = np.clip(p, EPS, 1 - EPS)
    return np.log(pc / (1 - pc))

def cal_in_the_large(y, p):
    if len(np.unique(y)) < 2:
        return None, None
    z = logit(p).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])

def prediction_set(y, p, threshold):
    include_pos = (1 - p) <= threshold
    include_neg = p <= threshold
    true_in_set = np.where(y == 1, include_pos, include_neg)
    set_size = include_pos.astype(int) + include_neg.astype(int)
    return true_in_set, set_size

TOUCH_TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

pred_sets = pd.read_csv(UNCERTAINTY_DIR / "test_set_prediction_sets.csv")
global_thresholds = pd.read_csv(UNCERTAINTY_DIR / "conformal_thresholds_by_model.csv").set_index("model")["threshold"]
group_thresholds = pd.read_csv(RESULTS_DIR / "group_specific_thresholds.csv").set_index(["model", "dimension", "category"])

TARGET_COMBINATIONS = [
    ("bmi", "Obese", "_bmi", ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]),
    ("age", "60+", "_age", ["random_forest", "xgboost", "lightgbm", "mlp"]),
]

before_after_rows = []
nontarget_rows = []
marginal_rows = []

for model in MODEL_NAMES:
    m = pred_sets[pred_sets["model"] == model].copy()
    y = m["true_target"].values
    p = m["predicted_probability_positive"].values
    g_thresh = global_thresholds[model]

    # BEFORE: global threshold applied to everyone (re-derived here from raw probabilities to
    # confirm exact agreement with Phase 6's own already-saved true_in_set/set_size columns)
    before_in_set, before_size = prediction_set(y, p, g_thresh)
    if not np.array_equal(before_in_set, m["true_in_set"].values):
        print(f"WARNING: {model} recomputed BEFORE true_in_set does not exactly match Phase 6's saved values")

    # AFTER: target-subgroup participants get their group-specific threshold; everyone else keeps the global threshold
    after_in_set = before_in_set.copy()
    after_size = before_size.copy()
    after_threshold_used = np.full(len(m), g_thresh)

    for dim, category, col, models in TARGET_COMBINATIONS:
        if model not in models:
            continue
        mask = (m[col] == category).values
        g_thresh_specific = group_thresholds.loc[(model, dim, category), "group_specific_threshold"]
        sub_in_set, sub_size = prediction_set(y[mask], p[mask], g_thresh_specific)
        after_in_set[mask] = sub_in_set
        after_size[mask] = sub_size
        after_threshold_used[mask] = g_thresh_specific

    m["after_true_in_set"] = after_in_set
    m["after_set_size"] = after_size
    m["after_threshold_used"] = after_threshold_used

    # Marginal (overall) coverage BEFORE vs AFTER
    cov_before = before_in_set.mean()
    cov_after = after_in_set.mean()
    marginal_rows.append({
        "generated": TOUCH_TIMESTAMP, "model": model, "n": len(m),
        "marginal_coverage_before": round(cov_before, 6), "marginal_coverage_after": round(cov_after, 6),
        "marginal_coverage_change_pp": round((cov_after - cov_before) * 100, 4),
        "within_5pp_tolerance": bool(abs((cov_after - cov_before) * 100) <= 5.0),
        "mean_set_size_before": round(before_size.mean(), 6), "mean_set_size_after": round(after_size.mean(), 6),
        "auc": round(roc_auc_score(y, p), 6), "brier": round(brier_score_loss(y, p), 6),
    })

    # Per-category BEFORE/AFTER for every subgroup category across all 4 dimensions -- target and non-target alike
    for dim, col in [("sex", "_sex"), ("race_ethnicity", "_race"), ("age", "_age"), ("bmi", "_bmi")]:
        for cat in m[col].dropna().unique():
            mask = (m[col] == cat).values
            n_cat = int(mask.sum())
            y_cat = y[mask]
            n_pos, n_neg = int((y_cat == 1).sum()), int((y_cat == 0).sum())

            cov_b = before_in_set[mask].mean()
            cov_a = after_in_set[mask].mean()
            kb, ka = int(before_in_set[mask].sum()), int(after_in_set[mask].sum())
            lo_b, hi_b = wilson_ci(kb, n_cat)
            lo_a, hi_a = wilson_ci(ka, n_cat)

            is_target = any(model in tm and dim2 == dim and cat == c2 for dim2, c2, _, tm in TARGET_COMBINATIONS)

            # Sensitivity is a property of the CLASSIFICATION decision (frozen Youden's J
            # threshold), which this mitigation never touches -- only conformal SET construction
            # is modified. Sensitivity is therefore computed once, using the frozen classification
            # threshold, and is IDENTICAL before/after by construction (reported as a sanity check,
            # not a trade-off metric, consistent with AUC/calibration below).
            class_thresh = FROZEN_THRESHOLDS[model]
            yhat = (p >= class_thresh).astype(int)
            def sens(yv, yhv):
                pos = yv == 1
                return float((yhv[pos] == 1).mean()) if pos.sum() else None
            sens_fixed = sens(y_cat, yhat[mask])
            sens_b = sens_fixed
            sens_a = sens_fixed

            intc_b, slope_b = cal_in_the_large(y_cat, p[mask])
            # calibration is a property of probabilities only -- identical before/after by construction; recomputed once
            row = {
                "generated": TOUCH_TIMESTAMP, "model": model, "dimension": dim, "category": cat,
                "is_target": is_target, "n": n_cat, "n_positive": n_pos, "n_negative": n_neg,
                "coverage_before": round(cov_b, 6), "coverage_after": round(cov_a, 6),
                "coverage_change_pp": round((cov_a - cov_b) * 100, 4),
                "ci_before": f"[{round(lo_b,4)}, {round(hi_b,4)}]" if lo_b is not None else "N/A",
                "ci_after": f"[{round(lo_a,4)}, {round(hi_a,4)}]" if lo_a is not None else "N/A",
                "ci_after_includes_90pct": bool(lo_a <= 0.90 <= hi_a) if lo_a is not None else None,
                "mean_set_size_before": round(before_size[mask].mean(), 6),
                "mean_set_size_after": round(after_size[mask].mean(), 6),
                "singleton_rate_before": round((before_size[mask] == 1).mean(), 6),
                "singleton_rate_after": round((after_size[mask] == 1).mean(), 6),
                "sensitivity_before": round(sens_b, 6) if sens_b is not None else None,
                "sensitivity_after": round(sens_a, 6) if sens_a is not None else None,
                "auc_before": round(roc_auc_score(y_cat, p[mask]), 6) if n_pos and n_neg else None,
                "auc_after": round(roc_auc_score(y_cat, p[mask]), 6) if n_pos and n_neg else None,  # identical -- probabilities untouched
                "calibration_intercept_before": round(intc_b, 6) if intc_b is not None else None,
                "calibration_intercept_after": round(intc_b, 6) if intc_b is not None else None,  # identical -- probabilities untouched
                "calibration_slope_before": round(slope_b, 6) if slope_b is not None else None,
                "calibration_slope_after": round(slope_b, 6) if slope_b is not None else None,  # identical -- probabilities untouched
            }
            if is_target:
                before_after_rows.append(row)
            else:
                nontarget_rows.append(row)

before_after_out = pd.DataFrame(before_after_rows)
before_after_out.to_csv(RESULTS_DIR / "test_set_mitigation_final.csv", index=False)

nontarget_out = pd.DataFrame(nontarget_rows)
nontarget_out.to_csv(RESULTS_DIR / "nontarget_subgroup_protection.csv", index=False)

marginal_out = pd.DataFrame(marginal_rows)
marginal_out.to_csv(RESULTS_DIR / "marginal_coverage_before_after.csv", index=False)

print("=== TARGET subgroups: before/after ===")
print(before_after_out[["model", "dimension", "category", "n", "coverage_before", "coverage_after",
                          "ci_after_includes_90pct", "mean_set_size_before", "mean_set_size_after"]].to_string(index=False))
print("\n=== Marginal coverage before/after (all models) ===")
print(marginal_out[["model", "marginal_coverage_before", "marginal_coverage_after", "marginal_coverage_change_pp", "within_5pp_tolerance"]].to_string(index=False))
print(f"\nTouch timestamp: {TOUCH_TIMESTAMP}")
print("Saved results/mitigation/test_set_mitigation_final.csv")
print("Saved results/mitigation/nontarget_subgroup_protection.csv")
print("Saved results/mitigation/marginal_coverage_before_after.csv")
print("\nTHIS IS THE SINGLE OFFICIAL PHASE 7 TEST-SET MITIGATION EVALUATION. Do not re-run.")
