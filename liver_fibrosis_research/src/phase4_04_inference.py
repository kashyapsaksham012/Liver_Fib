"""
phase4_04_inference.py
Phase 4 Parts 17-18: statistical inference exactly per frozen protocol §12-13:
  - Percentile bootstrap, n=2000 resamples, paired resampling at participant level.
  - Benjamini-Hochberg FDR correction across pairwise model comparisons per metric.
Computed EXCLUSIVELY from the OOF tier (5 PRIMARY models only -- MLP_balanced sensitivity
model is excluded from formal pairwise inference per §14, consistent with never merging it
into the primary comparison set).
"""
import sys
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_common import CALIB_RESULTS_DIR, PRIMARY_MODELS, load_oof_predictions, BOOTSTRAP_N, BOOTSTRAP_SEED, CI_LEVEL, NOW

EPS = 1e-12

def logit(p):
    pc = np.clip(p, EPS, 1 - EPS)
    return np.log(pc / (1 - pc))

def cal_in_the_large(y, p):
    z = logit(p).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])

def metrics_for(y, p):
    intercept, slope = cal_in_the_large(y, p)
    brier = brier_score_loss(y, p)
    return {"intercept": intercept, "slope": slope, "brier": brier}

# Load all 5 primary models, confirmed identical participant order (verified separately)
data = {name: load_oof_predictions(name) for name in PRIMARY_MODELS}
n = len(data[PRIMARY_MODELS[0]])
y_arrays = {name: data[name]["true_target"].values for name in PRIMARY_MODELS}
p_arrays = {name: data[name]["predicted_probability"].values for name in PRIMARY_MODELS}

point_estimates = {name: metrics_for(y_arrays[name], p_arrays[name]) for name in PRIMARY_MODELS}

rng = np.random.default_rng(BOOTSTRAP_SEED)
boot_results = {name: {"intercept": [], "slope": [], "brier": []} for name in PRIMARY_MODELS}

for b in range(BOOTSTRAP_N):
    idx = rng.integers(0, n, size=n)  # same resampled indices applied to every model -- paired
    for name in PRIMARY_MODELS:
        y_b = y_arrays[name][idx]
        p_b = p_arrays[name][idx]
        if y_b.sum() == 0 or y_b.sum() == n:  # degenerate resample, skip (both classes required)
            continue
        m = metrics_for(y_b, p_b)
        for k in m:
            boot_results[name][k].append(m[k])

alpha = 1 - CI_LEVEL
ci_rows = []
for name in PRIMARY_MODELS:
    for metric in ["intercept", "slope", "brier"]:
        arr = np.array(boot_results[name][metric])
        lo, hi = np.percentile(arr, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        ci_rows.append({
            "generated": NOW, "model": name, "metric": metric,
            "point_estimate": round(point_estimates[name][metric], 6),
            "ci_lower": round(float(lo), 6), "ci_upper": round(float(hi), 6),
            "ci_level": CI_LEVEL, "bootstrap_n": BOOTSTRAP_N, "bootstrap_n_valid_resamples": len(arr),
            "data_source": "CV out-of-fold predictions (train partition, N=5007)",
        })
ci_df = pd.DataFrame(ci_rows)

# Pairwise comparisons per metric, paired bootstrap differences, BH-FDR across all pairs within each metric
pairwise_rows = []
for metric in ["intercept", "slope", "brier"]:
    pair_pvals = []
    pair_meta = []
    for a, b_ in combinations(PRIMARY_MODELS, 2):
        arr_a = np.array(boot_results[a][metric])
        arr_b = np.array(boot_results[b_][metric])
        m = min(len(arr_a), len(arr_b))
        diff = arr_a[:m] - arr_b[:m]
        point_diff = point_estimates[a][metric] - point_estimates[b_][metric]
        lo, hi = np.percentile(diff, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        # two-sided bootstrap p-value: proportion of resampled diffs crossing zero, doubled tail
        p_two_sided = 2 * min((diff <= 0).mean(), (diff >= 0).mean())
        p_two_sided = min(p_two_sided, 1.0)
        pair_pvals.append(p_two_sided)
        pair_meta.append((a, b_, point_diff, lo, hi))

    # Benjamini-Hochberg FDR correction within this metric's family of pairwise comparisons
    m_tests = len(pair_pvals)
    order = np.argsort(pair_pvals)
    ranked = np.array(pair_pvals)[order]
    bh_adj = ranked * m_tests / (np.arange(m_tests) + 1)
    bh_adj = np.minimum.accumulate(bh_adj[::-1])[::-1]
    bh_adj = np.clip(bh_adj, 0, 1)
    adj_pvals = np.empty(m_tests)
    adj_pvals[order] = bh_adj

    for (a, b_, point_diff, lo, hi), raw_p, adj_p in zip(pair_meta, pair_pvals, adj_pvals):
        pairwise_rows.append({
            "generated": NOW, "metric": metric, "model_a": a, "model_b": b_,
            "point_diff_a_minus_b": round(point_diff, 6),
            "ci_lower": round(float(lo), 6), "ci_upper": round(float(hi), 6),
            "raw_p_two_sided_bootstrap": round(float(raw_p), 6),
            "bh_fdr_adjusted_p": round(float(adj_p), 6),
            "significant_after_fdr_0.05": bool(adj_p < 0.05),
        })
pairwise_df = pd.DataFrame(pairwise_rows)

combined = pd.concat([
    ci_df.assign(row_type="point_estimate_and_ci"),
    pairwise_df.assign(row_type="pairwise_comparison"),
], ignore_index=True, sort=False)
combined.to_csv(CALIB_RESULTS_DIR / "calibration_inference.csv", index=False)

print("=== Point estimates + bootstrap CIs ===")
print(ci_df.to_string(index=False))
print("\n=== Pairwise comparisons (BH-FDR corrected) ===")
print(pairwise_df.to_string(index=False))
print(f"\nSaved results/calibration/calibration_inference.csv ({len(combined)} rows)")
