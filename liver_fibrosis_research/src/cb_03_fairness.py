"""
cb_03_fairness.py
E1 (part 2): FIB-4 subgroup sensitivity disparity, mirroring phase5_04_inference.py's
method exactly (stratified-within-subgroup bootstrap, n=2000, seed=42 + per-comparison
crc32 offset; BH-FDR within each dimension family; same 10pp meaningful-difference rule).
The only difference from phase5_04: there is one score (FIB-4) instead of five models, so
each dimension is its own full FDR family (no per-model loop).

Output: results/clinical_baselines/fib4_fairness_inference.csv
"""
import sys
import zlib
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, PRIMARY_OUTCOME_COL, NOW
from phase5_common import DIMENSIONS, precision_tier, BOOTSTRAP_N, BOOTSTRAP_SEED, CI_LEVEL, MEANINGFUL_DIFFERENCE_PP

OUT_DIR = ROOT / "results" / "clinical_baselines"
scores = pd.read_csv(OUT_DIR / "fib4_scores.csv")
test = scores[scores["split"] == "test"].copy()
assert len(test) == 2146

thr = pd.read_csv(OUT_DIR / "fib4_discrimination.csv")["threshold"].iloc[0]
test["pred_class"] = (test["fib4"] >= thr).astype(int)
test["true_target"] = test[PRIMARY_OUTCOME_COL].values

SCORE_NAME = "FIB-4"
alpha = 1 - CI_LEVEL
rows = []

for dim, spec in DIMENSIONS.items():
    col = spec["col"]
    # bmi/age already have canonical *_final columns; sex/race use the raw coded columns via map_fn
    if dim == "bmi":
        test["_bin"] = test["bmi_group_final"]
    elif dim == "age":
        test["_bin"] = test["age_group_final"]
    else:
        test["_bin"] = test[col].apply(spec["map_fn"])

    ref_df = test[test["_bin"] == spec["reference"]]
    ref_y, ref_yhat = ref_df["true_target"].values, ref_df["pred_class"].values

    def sensitivity(y, yhat):
        pos = y == 1
        if pos.sum() == 0:
            return None
        return float((yhat[pos] == 1).mean())

    ref_sens_point = sensitivity(ref_y, ref_yhat)

    family_pvals, family_meta = [], []
    categories = sorted(test["_bin"].dropna().unique().tolist())
    for cat in categories:
        if cat == spec["reference"]:
            continue
        sub_df = test[test["_bin"] == cat]
        sub_y, sub_yhat = sub_df["true_target"].values, sub_df["pred_class"].values
        n_pos, n_neg = int((sub_y == 1).sum()), int((sub_y == 0).sum())
        tier = precision_tier(n_pos, n_neg)
        sub_sens_point = sensitivity(sub_y, sub_yhat)

        if sub_sens_point is None or ref_sens_point is None:
            rows.append({"generated": NOW, "score_name": SCORE_NAME, "dimension": dim, "category": cat,
                         "reference_group": spec["reference"], "n": len(sub_df), "n_positive": n_pos,
                         "n_negative": n_neg, "precision_tier": tier,
                         "subgroup_sensitivity": "NOT COMPUTABLE", "reference_sensitivity": "NOT COMPUTABLE",
                         "absolute_disparity_pp": "NOT COMPUTABLE", "ci_lower_pp": "NOT COMPUTABLE",
                         "ci_upper_pp": "NOT COMPUTABLE", "raw_p_bootstrap": "NOT COMPUTABLE",
                         "bh_fdr_adjusted_p": "NOT COMPUTABLE", "significant_after_fdr_0.05": "NOT COMPUTABLE",
                         "meaningful_disparity_ge_10pp_and_ci_excludes_zero": "NOT COMPUTABLE"})
            continue

        seed_offset = zlib.crc32(f"{SCORE_NAME}|{dim}|{cat}".encode()) % 1_000_000
        rng = np.random.default_rng(BOOTSTRAP_SEED + seed_offset)
        n_ref, n_sub = len(ref_y), len(sub_y)
        diffs = []
        for _ in range(BOOTSTRAP_N):
            r_idx = rng.integers(0, n_ref, size=n_ref)
            s_idx = rng.integers(0, n_sub, size=n_sub)
            r_y_b, r_yhat_b = ref_y[r_idx], ref_yhat[r_idx]
            s_y_b, s_yhat_b = sub_y[s_idx], sub_yhat[s_idx]
            if (r_y_b == 1).sum() == 0 or (s_y_b == 1).sum() == 0:
                continue
            ref_b_sens = (r_yhat_b[r_y_b == 1] == 1).mean()
            sub_b_sens = (s_yhat_b[s_y_b == 1] == 1).mean()
            diffs.append(sub_b_sens - ref_b_sens)
        diffs = np.array(diffs)
        if len(diffs) < 500:
            rows.append({"generated": NOW, "score_name": SCORE_NAME, "dimension": dim, "category": cat,
                         "reference_group": spec["reference"], "n": len(sub_df), "n_positive": n_pos,
                         "n_negative": n_neg, "precision_tier": tier,
                         "subgroup_sensitivity": round(sub_sens_point, 6), "reference_sensitivity": round(ref_sens_point, 6),
                         "absolute_disparity_pp": round(100 * (sub_sens_point - ref_sens_point), 4),
                         "ci_lower_pp": "NOT COMPUTABLE (insufficient positive resamples)",
                         "ci_upper_pp": "NOT COMPUTABLE (insufficient positive resamples)",
                         "raw_p_bootstrap": "NOT COMPUTABLE", "bh_fdr_adjusted_p": "NOT COMPUTABLE",
                         "significant_after_fdr_0.05": "NOT COMPUTABLE",
                         "meaningful_disparity_ge_10pp_and_ci_excludes_zero": "NOT COMPUTABLE"})
            continue

        lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        p_two_sided = min(2 * min((diffs <= 0).mean(), (diffs >= 0).mean()), 1.0)
        point_disparity = sub_sens_point - ref_sens_point
        family_pvals.append(p_two_sided)
        family_meta.append((cat, tier, n_pos, n_neg, sub_sens_point, ref_sens_point, point_disparity, lo, hi))

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
            rows.append({"generated": NOW, "score_name": SCORE_NAME, "dimension": dim, "category": cat,
                         "reference_group": spec["reference"], "n": None, "n_positive": n_pos, "n_negative": n_neg,
                         "precision_tier": tier, "subgroup_sensitivity": round(sub_sens, 6),
                         "reference_sensitivity": round(ref_sens, 6), "absolute_disparity_pp": round(disp * 100, 4),
                         "ci_lower_pp": round(lo * 100, 4), "ci_upper_pp": round(hi * 100, 4),
                         "raw_p_bootstrap": round(raw_p, 6), "bh_fdr_adjusted_p": round(adj_p, 6),
                         "significant_after_fdr_0.05": bool(adj_p < 0.05),
                         "meaningful_disparity_ge_10pp_and_ci_excludes_zero": bool(meaningful)})

out = pd.DataFrame(rows)
out.to_csv(OUT_DIR / "fib4_fairness_inference.csv", index=False)
print(out.to_string(index=False))
print(f"\nSaved results/clinical_baselines/fib4_fairness_inference.csv ({len(out)} rows)")
