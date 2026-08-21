"""
rel_01_cooccurrence_analysis.py
Reliability Extension, Analysis A: co-occurrence correlation between subgroup fairness-disparity
magnitude and subgroup conformal-coverage-deficit magnitude. Executes exactly the protocol frozen
in documentation/reliability_extension/COOCCURRENCE_PROTOCOL_FREEZE.md, Commit A -- this script
was written and this analysis run only after that protocol was committed.

Uses ONLY already-existing, frozen Phase 5/6 result artifacts. No prediction is regenerated, no
model is touched, no cohort/outcome/predictor is changed.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT

RESULTS_DIR = ROOT / "results" / "reliability_extension"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PERM_N = 10000
PERM_SEED = 42

fair = pd.read_csv(ROOT / "results" / "fairness" / "fairness_inference.csv")
cov = pd.read_csv(ROOT / "results" / "uncertainty" / "coverage_inference.csv")

# Build the full analysis table: inner join on (model, dimension, category) -- every non-reference
# fairness row (N=55) matched to its coverage row. No filtering by significance or magnitude.
fair["total_n"] = fair["n_positive"] + fair["n_negative"]
merged = fair.merge(
    cov[["model", "dimension", "category", "n", "empirical_coverage", "ci_lower", "ci_upper",
         "bh_fdr_adjusted_p", "significant_after_fdr_0.05"]].rename(
        columns={"n": "coverage_n", "bh_fdr_adjusted_p": "coverage_bh_fdr_p",
                 "significant_after_fdr_0.05": "coverage_significant_after_fdr"}),
    on=["model", "dimension", "category"], how="inner"
)
if len(merged) != 55:
    print(f"RELIABILITY EXTENSION STOP CONDITION: merged N={len(merged)}, expected 55"); sys.exit(1)

merged["fairness_disparity_signed_pp"] = merged["absolute_disparity_pp"]
merged["fairness_disparity_magnitude_pp"] = merged["absolute_disparity_pp"].abs()
merged["coverage_deviation_signed_pp"] = merged["empirical_coverage"] * 100 - 90
merged["coverage_deficit_magnitude_pp"] = merged["coverage_deviation_signed_pp"].abs()
merged["precision_limited"] = merged["precision_tier"].isin(["insufficient evidence", "limited precision"])

analysis_cols = ["model", "dimension", "category", "reference_group", "total_n", "n_positive", "n_negative",
                  "precision_tier", "precision_limited",
                  "fairness_disparity_signed_pp", "fairness_disparity_magnitude_pp",
                  "ci_lower_pp", "ci_upper_pp", "significant_after_fdr_0.05",
                  "coverage_n", "empirical_coverage", "coverage_deviation_signed_pp",
                  "coverage_deficit_magnitude_pp", "ci_lower", "ci_upper", "coverage_significant_after_fdr"]
analysis_table = merged[analysis_cols].copy()
analysis_table.to_csv(RESULTS_DIR / "cooccurrence_analysis_table.csv", index=False)
print(f"Saved cooccurrence_analysis_table.csv (N={len(analysis_table)})")

X = merged["fairness_disparity_magnitude_pp"].values
Y = merged["coverage_deficit_magnitude_pp"].values

# ---- Primary: pooled Spearman ----
rho, p_spearman = spearmanr(X, Y)
n_boot = 10000
rng = np.random.default_rng(PERM_SEED)
boot_rhos = []
idx_all = np.arange(len(X))
for _ in range(n_boot):
    idx = rng.integers(0, len(X), size=len(X))
    if len(np.unique(X[idx])) < 2 or len(np.unique(Y[idx])) < 2:
        continue
    r, _ = spearmanr(X[idx], Y[idx])
    boot_rhos.append(r)
ci_lo, ci_hi = np.percentile(boot_rhos, [2.5, 97.5])

print(f"\n=== PRIMARY: pooled Spearman (N={len(X)}) ===")
print(f"rho={rho:.4f}, 95% CI=[{ci_lo:.4f},{ci_hi:.4f}], p={p_spearman:.6f}")

# ---- Dependence-aware sensitivity: category-block permutation test ----
categories = merged["dimension"].astype(str) + "|" + merged["category"].astype(str)
uniq_cats = categories.unique()
cat_to_idx = {c: np.where(categories.values == c)[0] for c in uniq_cats}
rng2 = np.random.default_rng(PERM_SEED)
perm_rhos = []
for _ in range(PERM_N):
    perm_order = rng2.permutation(uniq_cats)
    y_perm = np.empty_like(Y)
    for orig_cat, new_cat in zip(uniq_cats, perm_order):
        y_perm[cat_to_idx[orig_cat]] = Y[cat_to_idx[new_cat]]
    r, _ = spearmanr(X, y_perm)
    perm_rhos.append(r)
perm_rhos = np.array(perm_rhos)
perm_p = float((np.abs(perm_rhos) >= abs(rho)).mean())
print(f"Category-block permutation test: {PERM_N} resamples, seed={PERM_SEED}, permutation p={perm_p:.6f}")

# ---- Precision-limited sensitivity ----
mask_hp = ~merged["precision_limited"].values
X_hp, Y_hp = X[mask_hp], Y[mask_hp]
rho_hp, p_hp = spearmanr(X_hp, Y_hp)
print(f"\n=== SENSITIVITY: precision-filtered (N={mask_hp.sum()}, excludes {(~mask_hp).sum()} insufficient/limited-precision obs) ===")
print(f"rho={rho_hp:.4f}, p={p_hp:.6f}")

# ---- Within-model secondary (5 tests, BH-FDR) ----
within_model_rows = []
for m in sorted(merged["model"].unique()):
    sub = merged[merged["model"] == m]
    r, p = spearmanr(sub["fairness_disparity_magnitude_pp"], sub["coverage_deficit_magnitude_pp"])
    within_model_rows.append({"model": m, "n": len(sub), "spearman_rho": r, "raw_p": p})
wm = pd.DataFrame(within_model_rows)
pvals = wm["raw_p"].values
order = np.argsort(pvals)
ranked = pvals[order]
m_tests = len(pvals)
bh = ranked * m_tests / (np.arange(m_tests) + 1)
bh = np.minimum.accumulate(bh[::-1])[::-1]
bh = np.clip(bh, 0, 1)
adj = np.empty(m_tests)
adj[order] = bh
wm["bh_fdr_adjusted_p"] = adj
wm["significant_after_fdr_0.05"] = adj < 0.05
print("\n=== SECONDARY: within-model (N=11 each, BH-FDR family of 5) ===")
print(wm.to_string(index=False))

# Save primary + sensitivity + within-model results
pd.DataFrame([{
    "analysis": "primary_pooled_spearman", "n": len(X), "spearman_rho": rho,
    "ci_lower_bootstrap": ci_lo, "ci_upper_bootstrap": ci_hi, "raw_p_spearman": p_spearman,
    "cluster_permutation_p": perm_p, "permutation_n": PERM_N, "permutation_seed": PERM_SEED,
}, {
    "analysis": "precision_filtered_sensitivity", "n": int(mask_hp.sum()), "spearman_rho": rho_hp,
    "ci_lower_bootstrap": None, "ci_upper_bootstrap": None, "raw_p_spearman": p_hp,
    "cluster_permutation_p": None, "permutation_n": None, "permutation_seed": None,
}]).to_csv(RESULTS_DIR / "cooccurrence_correlation_results.csv", index=False)
wm.to_csv(RESULTS_DIR / "cooccurrence_within_model_secondary.csv", index=False)

print(f"\nSaved cooccurrence_correlation_results.csv")
print(f"Saved cooccurrence_within_model_secondary.csv")
