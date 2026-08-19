"""
phase5_04_inference.py
Phase 5 Part 9-13: statistical inference for the PRIMARY fairness metric (sensitivity
disparity, absolute, subgroup - reference), per fairness_definition.md:
  - bootstrap 95% CI (n=2000), stratified within subgroup, around the DIFFERENCE itself
    (not the union of two individual CIs).
  - Benjamini-Hochberg FDR, one family per (model x dimension) combination -- Part 10 --
    kept structurally separate from Phase 3's and Phase 4's FDR families (different script,
    different arrays, different output file; no code path reads Phase 3/4 output here).
  - 10-percentage-point meaningful-difference tolerance (fairness_definition.md), reported
    alongside statistical significance, kept distinct (Part 13).
Uses the SAME frozen thresholds and RAW test-set predictions as phase5_02 -- no new model
scoring, only resampling of already-computed per-participant correctness.
"""
import sys
import zlib
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase5_common import (
    FAIR_RESULTS_DIR, DIMENSIONS, load_demographics, PRIMARY_MODELS, FROZEN_THRESHOLDS,
    BOOTSTRAP_N, BOOTSTRAP_SEED, CI_LEVEL, MEANINGFUL_DIFFERENCE_PP, precision_tier, NOW, fail,
)
from phase3_common import PRED_DIR, SPLIT_DIR

test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"].tolist())
demo = load_demographics()
demo = demo[demo["SEQN"].isin(test_ids)].copy()

alpha = 1 - CI_LEVEL
rows = []

for model in PRIMARY_MODELS:
    pred = pd.read_csv(PRED_DIR / f"test_predictions_{model}.csv")[["SEQN", "predicted_probability", "true_target"]]
    merged = demo.merge(pred, on="SEQN", how="inner")
    threshold = FROZEN_THRESHOLDS[model]
    merged["pred_class"] = (merged["predicted_probability"] >= threshold).astype(int)

    for dim, spec in DIMENSIONS.items():
        merged["_bin"] = merged[spec["col"]].apply(spec["map_fn"])
        ref_df = merged[merged["_bin"] == spec["reference"]]
        ref_y, ref_yhat = ref_df["true_target"].values, ref_df["pred_class"].values

        # Point sensitivity for reference group
        def sensitivity(y, yhat):
            pos = y == 1
            if pos.sum() == 0:
                return None
            return float((yhat[pos] == 1).mean())

        ref_sens_point = sensitivity(ref_y, ref_yhat)

        family_pvals = []
        family_meta = []

        categories = sorted(merged["_bin"].dropna().unique().tolist())
        for cat in categories:
            if cat == spec["reference"]:
                continue
            sub_df = merged[merged["_bin"] == cat]
            sub_y, sub_yhat = sub_df["true_target"].values, sub_df["pred_class"].values
            n_pos, n_neg = int((sub_y == 1).sum()), int((sub_y == 0).sum())
            tier = precision_tier(n_pos, n_neg)
            sub_sens_point = sensitivity(sub_y, sub_yhat)

            if sub_sens_point is None or ref_sens_point is None:
                rows.append({
                    "generated": NOW, "model": model, "dimension": dim, "category": cat,
                    "reference_group": spec["reference"], "n": len(sub_df), "n_positive": n_pos,
                    "n_negative": n_neg, "precision_tier": tier,
                    "subgroup_sensitivity": "NOT COMPUTABLE", "reference_sensitivity": "NOT COMPUTABLE",
                    "absolute_disparity_pp": "NOT COMPUTABLE", "ci_lower_pp": "NOT COMPUTABLE",
                    "ci_upper_pp": "NOT COMPUTABLE", "raw_p_bootstrap": "NOT COMPUTABLE",
                    "bh_fdr_adjusted_p": "NOT COMPUTABLE", "significant_after_fdr_0.05": "NOT COMPUTABLE",
                    "meaningful_disparity_ge_10pp_and_ci_excludes_zero": "NOT COMPUTABLE",
                })
                continue

            # Stratified-within-subgroup bootstrap (fairness_definition.md): resample each GROUP's
            # full participant set independently (not just its positives) with replacement, then
            # recompute sensitivity on whichever positives land in that resample -- the standard
            # nonparametric bootstrap for a conditional rate. One RNG per (model, dimension,
            # category) comparison, seeded deterministically from the frozen project seed plus a
            # stable string-derived offset (not Python's salted hash()) so this is reproducible
            # across processes/runs.
            seed_offset = zlib.crc32(f"{model}|{dim}|{cat}".encode()) % 1_000_000
            rng = np.random.default_rng(BOOTSTRAP_SEED + seed_offset)
            n_ref, n_sub = len(ref_y), len(sub_y)
            diffs = []
            for _ in range(BOOTSTRAP_N):
                r_idx = rng.integers(0, n_ref, size=n_ref)
                s_idx = rng.integers(0, n_sub, size=n_sub)
                r_y_b, r_yhat_b = ref_y[r_idx], ref_yhat[r_idx]
                s_y_b, s_yhat_b = sub_y[s_idx], sub_yhat[s_idx]
                if (r_y_b == 1).sum() == 0 or (s_y_b == 1).sum() == 0:
                    continue  # degenerate resample (no positives) -- skip, do not treat as zero
                ref_b_sens = (r_yhat_b[r_y_b == 1] == 1).mean()
                sub_b_sens = (s_yhat_b[s_y_b == 1] == 1).mean()
                diffs.append(sub_b_sens - ref_b_sens)
            diffs = np.array(diffs)
            if len(diffs) < 500:  # too few valid (non-degenerate) resamples to trust a percentile CI
                rows.append({
                    "generated": NOW, "model": model, "dimension": dim, "category": cat,
                    "reference_group": spec["reference"], "n": len(sub_df), "n_positive": n_pos,
                    "n_negative": n_neg, "precision_tier": tier,
                    "subgroup_sensitivity": round(sub_sens_point, 6), "reference_sensitivity": round(ref_sens_point, 6),
                    "absolute_disparity_pp": round(100 * (sub_sens_point - ref_sens_point), 4),
                    "ci_lower_pp": "NOT COMPUTABLE (insufficient positive resamples)",
                    "ci_upper_pp": "NOT COMPUTABLE (insufficient positive resamples)",
                    "raw_p_bootstrap": "NOT COMPUTABLE", "bh_fdr_adjusted_p": "NOT COMPUTABLE",
                    "significant_after_fdr_0.05": "NOT COMPUTABLE",
                    "meaningful_disparity_ge_10pp_and_ci_excludes_zero": "NOT COMPUTABLE",
                })
                continue

            lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
            p_two_sided = min(2 * min((diffs <= 0).mean(), (diffs >= 0).mean()), 1.0)
            point_disparity = sub_sens_point - ref_sens_point

            family_pvals.append(p_two_sided)
            family_meta.append((cat, tier, n_pos, n_neg, sub_sens_point, ref_sens_point, point_disparity, lo, hi))

        # BH-FDR within this (model x dimension) family
        m_tests = len(family_pvals)
        if m_tests > 0:
            order = np.argsort(family_pvals)
            ranked = np.array(family_pvals)[order]
            bh_adj = ranked * m_tests / (np.arange(m_tests) + 1)
            bh_adj = np.minimum.accumulate(bh_adj[::-1])[::-1]
            bh_adj = np.clip(bh_adj, 0, 1)
            adj_pvals = np.empty(m_tests)
            adj_pvals[order] = bh_adj

            for (cat, tier, n_pos, n_neg, sub_sens, ref_sens, disp, lo, hi), raw_p, adj_p in zip(family_meta, family_pvals, adj_pvals):
                ci_excludes_zero = (lo > 0) or (hi < 0)
                meaningful = abs(disp * 100) >= MEANINGFUL_DIFFERENCE_PP and ci_excludes_zero
                rows.append({
                    "generated": NOW, "model": model, "dimension": dim, "category": cat,
                    "reference_group": spec["reference"], "n": None, "n_positive": n_pos, "n_negative": n_neg,
                    "precision_tier": tier, "subgroup_sensitivity": round(sub_sens, 6),
                    "reference_sensitivity": round(ref_sens, 6), "absolute_disparity_pp": round(disp * 100, 4),
                    "ci_lower_pp": round(lo * 100, 4), "ci_upper_pp": round(hi * 100, 4),
                    "raw_p_bootstrap": round(raw_p, 6), "bh_fdr_adjusted_p": round(adj_p, 6),
                    "significant_after_fdr_0.05": bool(adj_p < 0.05),
                    "meaningful_disparity_ge_10pp_and_ci_excludes_zero": bool(meaningful),
                })

out = pd.DataFrame(rows)
out.to_csv(FAIR_RESULTS_DIR / "fairness_inference.csv", index=False)
print(out.to_string(index=False))
print(f"\nSaved results/fairness/fairness_inference.csv ({len(out)} rows)")
n_meaningful = (out["meaningful_disparity_ge_10pp_and_ci_excludes_zero"] == True).sum()
print(f"\nSubgroups meeting the frozen meaningful-difference criterion (>=10pp AND CI excludes zero): {n_meaningful}")
