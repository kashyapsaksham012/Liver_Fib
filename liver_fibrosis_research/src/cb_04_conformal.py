"""
cb_04_conformal.py
E1 (part 3): split-conformal coverage for FIB-4, mirroring phase6_02/03/04's method and
partition discipline exactly (fit on proper_train_ids only, calibrate the nonconformity
threshold on conformal_calibration_ids only, one single locked-test touch at the end).

Methodological note (stated here and in the report, not hidden): split-conformal prediction
as specified requires a class probability p_hat(y|x) to form the nonconformity score
1 - p_hat(true class). FIB-4 is a fixed continuous index with no native probability -- unlike
the five ML models, there is nothing to "refit" for FIB-4 itself. The minimal, standard way to
obtain p_hat from a single continuous score is a univariate logistic mapping (mechanically the
same idea as Platt scaling), fit ONLY on proper_train_ids (N=4005, exactly the same partition
the five ML models were refit on for their own conformal analysis -- never the calibration or
test partitions), i.e. p_hat = sigmoid(b0 + b1 * FIB4). This auxiliary fit is the necessary
price of applying split-conformal to a score that is not itself a probabilistic classifier;
it changes nothing about the underlying FIB-4 formula, which is never modified, and it
preserves the same calibration/test exchangeability discipline as the ML pipeline.

Output:
  results/clinical_baselines/fib4_conformal_threshold.csv
  results/clinical_baselines/fib4_marginal_coverage.csv
  results/clinical_baselines/fib4_subgroup_coverage.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, RANDOM_SEED, PRIMARY_OUTCOME_COL
from phase5_common import DIMENSIONS, precision_tier

OUT_DIR = ROOT / "results" / "clinical_baselines"
TARGET_COVERAGE = 0.90
ALPHA = 1 - TARGET_COVERAGE

scores = pd.read_csv(OUT_DIR / "fib4_scores.csv")
proper_train = scores[scores["split"] == "proper_train"]
cal = scores[scores["split"] == "conformal_calibration"]
test = scores[scores["split"] == "test"]
assert len(proper_train) == 4005 and len(cal) == 1002 and len(test) == 2146

# ── Auxiliary univariate logistic mapping, fit on proper_train ONLY ──────────────────────
clf = LogisticRegression(random_state=RANDOM_SEED)
clf.fit(proper_train[["fib4"]].values, proper_train[PRIMARY_OUTCOME_COL].values)
print(f"Auxiliary logistic (FIB-4 -> probability), fit on proper_train N={len(proper_train)}: "
      f"intercept={clf.intercept_[0]:.4f}, coef={clf.coef_[0][0]:.4f}")

def to_proba(df):
    return clf.predict_proba(df[["fib4"]].values)[:, 1]

# ── Calibration: nonconformity score + finite-sample-corrected threshold ────────────────
proba_cal = to_proba(cal)
y_cal = cal[PRIMARY_OUTCOME_COL].values
n_cal = len(cal)
proba_true_class = np.where(y_cal == 1, proba_cal, 1 - proba_cal)
cal_scores = 1 - proba_true_class

k = int(np.ceil((n_cal + 1) * (1 - ALPHA)))
sorted_scores = np.sort(cal_scores)
if k > n_cal:
    threshold = np.inf
    q_level = 1.0
else:
    threshold = sorted_scores[k - 1]
    q_level = k / n_cal

pd.DataFrame([{
    "score_name": "FIB-4 (+ auxiliary univariate logistic)", "calibration_n": n_cal,
    "calibration_positives": int(y_cal.sum()), "calibration_negatives": int((y_cal == 0).sum()),
    "target_coverage": TARGET_COVERAGE,
    "score_definition": "1 - P(y=true_class | FIB4), P from auxiliary logistic fit on proper_train only",
    "quantile_level_finite_sample_corrected": round(q_level, 6),
    "threshold": round(float(threshold), 6),
    "mean_score": round(float(cal_scores.mean()), 6), "median_score": round(float(np.median(cal_scores)), 6),
}]).to_csv(OUT_DIR / "fib4_conformal_threshold.csv", index=False)
print(f"Conformal threshold (from calibration partition, N={n_cal}): {threshold:.6f} "
      f"(quantile level {q_level:.4f})")

# ── Single locked-test touch: prediction sets, marginal + subgroup coverage ──────────────
def wilson_ci(k_, n_, level=0.95):
    if n_ == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k_ / n_
    denom = 1 + z**2 / n_
    center = (phat + z**2 / (2 * n_)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n_ + z**2 / (4 * n_**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))

test = test.copy()
test["_bin_bmi"] = test["bmi_group_final"]
test["_bin_age"] = test["age_group_final"]
test["_bin_sex"] = test["RIAGENDR"].apply(DIMENSIONS["sex"]["map_fn"])
test["_bin_race"] = test["RIDRETH3"].apply(DIMENSIONS["race_ethnicity"]["map_fn"])

proba_test = to_proba(test)
y_test = test[PRIMARY_OUTCOME_COL].values
include_pos = (1 - proba_test) <= threshold
include_neg = proba_test <= threshold
set_size = include_pos.astype(int) + include_neg.astype(int)
true_in_set = np.where(y_test == 1, include_pos, include_neg)

n = len(test)
covered = int(true_in_set.sum())
coverage = covered / n
ci_lo, ci_hi = wilson_ci(covered, n)
pd.DataFrame([{
    "score_name": "FIB-4 (+ auxiliary univariate logistic)", "n": n, "target_coverage": 0.90,
    "empirical_coverage": round(coverage, 6), "ci_lower": round(ci_lo, 6), "ci_upper": round(ci_hi, 6),
    "ci_method": "Wilson score interval, 95%",
    "coverage_minus_target": round(coverage - 0.90, 6),
    "mean_set_size": round(float(set_size.mean()), 6), "median_set_size": float(np.median(set_size)),
    "singleton_rate": round(float((set_size == 1).mean()), 6),
    "ambiguous_rate_both_classes": round(float((set_size == 2).mean()), 6),
    "empty_set_rate": round(float((set_size == 0).mean()), 6),
    "threshold_used": threshold,
}]).to_csv(OUT_DIR / "fib4_marginal_coverage.csv", index=False)
print(f"Marginal coverage (locked test, N={n}): {coverage:.4f} [{ci_lo:.4f},{ci_hi:.4f}], "
      f"mean set size={set_size.mean():.3f}")

subgroup_rows, inference_rows = [], []
for dim in ["bmi", "age", "sex", "race_ethnicity"]:
    col = "_bin_" + ("race" if dim == "race_ethnicity" else dim)
    for cat in test[col].dropna().unique():
        mask = test[col].values == cat
        sub_n = int(mask.sum())
        sub_y = y_test[mask]
        sub_covered = int(true_in_set[mask].sum())
        sub_coverage = sub_covered / sub_n if sub_n else None
        slo, shi = wilson_ci(sub_covered, sub_n)
        n_pos, n_neg = int((sub_y == 1).sum()), int((sub_y == 0).sum())
        tier = precision_tier(n_pos, n_neg)
        p_val = stats.binomtest(sub_covered, sub_n, 0.90, alternative="two-sided").pvalue if sub_n else None
        subgroup_rows.append({
            "score_name": "FIB-4", "dimension": dim, "category": cat, "n": sub_n, "n_positive": n_pos,
            "n_negative": n_neg, "precision_tier": tier, "empirical_coverage": round(sub_coverage, 6),
            "ci_lower": round(slo, 6), "ci_upper": round(shi, 6), "ci_method": "Wilson score interval, 95%",
            "coverage_minus_target": round(sub_coverage - 0.90, 6),
            "ci_excludes_target": bool(slo > 0.90 or shi < 0.90),
            "mean_set_size": round(float(set_size[mask].mean()), 6),
            "singleton_rate": round(float((set_size[mask] == 1).mean()), 6),
            "raw_p_binomial_vs_90pct": round(p_val, 6),
        })
        inference_rows.append({"dimension": dim, "category": cat, "raw_p": p_val})

subgroup_out = pd.DataFrame(subgroup_rows)
inf_df = pd.DataFrame(inference_rows)
adj_rows = []
for dim, grp in inf_df.groupby("dimension"):
    pvals = grp["raw_p"].values
    m = len(pvals)
    order = np.argsort(pvals)
    ranked = pvals[order]
    bh = ranked * m / (np.arange(m) + 1)
    bh = np.minimum.accumulate(bh[::-1])[::-1]
    bh = np.clip(bh, 0, 1)
    adj = np.empty(m)
    adj[order] = bh
    for cat, a in zip(grp["category"].values, adj):
        adj_rows.append({"dimension": dim, "category": cat, "bh_fdr_adjusted_p": round(float(a), 6)})
adj_df = pd.DataFrame(adj_rows)
subgroup_out = subgroup_out.merge(adj_df, on=["dimension", "category"], how="left")
subgroup_out["significant_after_fdr_0.05"] = subgroup_out["bh_fdr_adjusted_p"] < 0.05
subgroup_out.to_csv(OUT_DIR / "fib4_subgroup_coverage.csv", index=False)

pd.DataFrame({"SEQN": test["SEQN"].values, "fib4": test["fib4"].values,
              "auxiliary_probability": proba_test, "true_target": y_test,
              "include_positive": include_pos, "include_negative": include_neg,
              "set_size": set_size, "true_in_set": true_in_set}).to_csv(
    OUT_DIR / "fib4_test_prediction_sets.csv", index=False)

print(subgroup_out[["dimension", "category", "n", "empirical_coverage", "ci_lower", "ci_upper",
                     "significant_after_fdr_0.05"]].to_string(index=False))
print(f"\nSaved fib4_conformal_threshold.csv, fib4_marginal_coverage.csv, fib4_subgroup_coverage.csv, "
      f"fib4_test_prediction_sets.csv")
