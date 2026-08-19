"""
phase7_03_pretest_evaluation.py
Project Phase 7 Part 6: pre-test-set evaluation, using ONLY proper-training/calibration data --
never the test set. Two checks:
  1. Same-data check: coverage of the group-specific threshold ON THE SAME calibration data used
     to derive it -- expected to be close to 90% BY CONSTRUCTION (same circularity Phase 4
     disclosed for its OOF pre/post recalibration comparison). Reported for completeness, not
     treated as real evidence.
  2. Split-half check (the genuine pre-test signal): each target subgroup's calibration
     participants are split 50/50 (fixed seed); the group-specific threshold is refit on one
     half and its coverage evaluated on the OTHER, held-out half -- non-circular, still entirely
     within calibration data, never touching the test set.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, SPLIT_DIR, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL
from phase3_common import load_primary_dataset, fail
from phase5_common import bin_age, bin_bmi

REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"
RESULTS_DIR = ROOT / "results" / "mitigation"
ALPHA = 0.10
SPLIT_SEED = 42

TARGET_COMBINATIONS = [
    ("bmi", "Obese", ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]),
    ("age", "60+", ["random_forest", "xgboost", "lightgbm", "mlp"]),
]

def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def conformal_threshold(y, proba_pos):
    proba_true = np.where(y == 1, proba_pos, 1 - proba_pos)
    scores = 1 - proba_true
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - ALPHA)))
    sorted_scores = np.sort(scores)
    return (np.inf if k > n else float(sorted_scores[k - 1])), scores

def coverage_with_threshold(y, proba_pos, threshold):
    include_pos = (1 - proba_pos) <= threshold
    include_neg = proba_pos <= threshold
    true_in_set = np.where(y == 1, include_pos, include_neg)
    return int(true_in_set.sum()), len(y)

master = load_primary_dataset()
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])
cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)
cal_df["_bmi"] = cal_df["BMXBMI"].apply(bin_bmi)
cal_df["_age"] = cal_df["RIDAGEYR"].apply(bin_age)
DIM_COL = {"bmi": "_bmi", "age": "_age"}

group_thresholds = pd.read_csv(RESULTS_DIR / "group_specific_thresholds.csv").set_index(["model", "dimension", "category"])

rows = []
for dim, category, models in TARGET_COMBINATIONS:
    col = DIM_COL[dim]
    sub_cal = cal_df[cal_df[col] == category].reset_index(drop=True)
    rng = np.random.default_rng(SPLIT_SEED)
    idx = rng.permutation(len(sub_cal))
    half = len(sub_cal) // 2
    fit_idx, eval_idx = idx[:half], idx[half:]
    fit_df, eval_df = sub_cal.iloc[fit_idx], sub_cal.iloc[eval_idx]

    for model in models:
        refit = joblib.load(REFIT_DIR / f"model_{model}_proper_train_refit.joblib")
        pipe = refit["pipeline"]

        # Check 1: same-data (circular by construction)
        X_full = sub_cal[PRIMARY_PREDICTORS]
        y_full = sub_cal[PRIMARY_OUTCOME_COL].values
        proba_full = pipe.predict_proba(X_full)[:, 1]
        thresh_full, _ = conformal_threshold(y_full, proba_full)
        covered_full, n_full = coverage_with_threshold(y_full, proba_full, thresh_full)
        cov_full = covered_full / n_full

        # Check 2: split-half (genuine, non-circular, still calibration-only)
        X_fit, y_fit = fit_df[PRIMARY_PREDICTORS], fit_df[PRIMARY_OUTCOME_COL].values
        X_eval, y_eval = eval_df[PRIMARY_PREDICTORS], eval_df[PRIMARY_OUTCOME_COL].values
        proba_fit = pipe.predict_proba(X_fit)[:, 1]
        proba_eval = pipe.predict_proba(X_eval)[:, 1]
        thresh_split, _ = conformal_threshold(y_fit, proba_fit)
        covered_split, n_split = coverage_with_threshold(y_eval, proba_eval, thresh_split)
        cov_split = covered_split / n_split if n_split else None
        lo, hi = wilson_ci(covered_split, n_split)

        rows.append({
            "model": model, "dimension": dim, "category": category,
            "same_data_threshold": round(thresh_full, 6), "same_data_n": n_full,
            "same_data_coverage": round(cov_full, 6),
            "same_data_note": "circular by construction -- expected close to 90%, not real evidence, mirrors Phase 4's disclosed OOF check",
            "split_half_fit_n": len(fit_df), "split_half_eval_n": len(eval_df),
            "split_half_threshold": round(thresh_split, 6),
            "split_half_coverage": round(cov_split, 6) if cov_split is not None else None,
            "split_half_ci_lower": round(lo, 6) if lo is not None else None,
            "split_half_ci_upper": round(hi, 6) if hi is not None else None,
            "split_half_ci_includes_90pct": bool(lo <= 0.90 <= hi) if lo is not None else None,
        })

out = pd.DataFrame(rows)
out.to_csv(RESULTS_DIR / "pre_test_evaluation.csv", index=False)
print(out.to_string(index=False))
print(f"\nSaved results/mitigation/pre_test_evaluation.csv ({len(out)} rows)")
print("\nNo test-set data was accessed at any point in this script.")
