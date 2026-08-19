"""
mi_03_black_subgroup_inference.py
Multiple-imputation sensitivity analysis, Part 9 (continued) + Part 15-16: extract the
Non-Hispanic Black subgroup from both arms' OOF predictions (results/sensitivity/
oof_predictions_<arm>_<model>.csv, produced by mi_02), compute sensitivity/FNR/specificity/FPR at
the frozen Youden's J classification thresholds (unchanged, not re-derived), bootstrap CI
(n=2000, seed=42, paired resampling -- same convention as Phase 5/6/7) for the complete-case vs
MI difference, and classify the result per this task's Part 16 (A-F).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import INT_DIR
from _cohorts import COHORT_3B_ADULT_OF_QUALITY_VALID
from phase3_common import ROOT, MODEL_NAMES
from phase5_common import FROZEN_THRESHOLDS, RACE_MAP_RIDRETH3

RESULTS_DIR = ROOT / "results" / "sensitivity"
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 42
CI_LEVEL = 0.95

master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
mask, meta = COHORT_3B_ADULT_OF_QUALITY_VALID(master)
pool = master[mask].reset_index(drop=True).copy()
demo = pool[["SEQN", "RIDRETH3"]].copy()
demo["_race"] = demo["RIDRETH3"].map(RACE_MAP_RIDRETH3)

def sens_fnr_spec_fpr(y, yhat):
    pos, neg = y == 1, y == 0
    tp = int(((y == 1) & (yhat == 1)).sum()); fn = int(((y == 1) & (yhat == 0)).sum())
    tn = int(((y == 0) & (yhat == 0)).sum()); fp = int(((y == 0) & (yhat == 1)).sum())
    sens = tp / (tp + fn) if (tp + fn) else None
    fnr = fn / (tp + fn) if (tp + fn) else None
    spec = tn / (tn + fp) if (tn + fp) else None
    fpr = fp / (tn + fp) if (tn + fp) else None
    return sens, fnr, spec, fpr

rows = []
for model in MODEL_NAMES:
    thresh = FROZEN_THRESHOLDS[model]
    arm_data = {}
    for arm in ["complete_case", "multiple_imputation"]:
        df = pd.read_csv(RESULTS_DIR / f"oof_predictions_{arm}_{model}.csv")
        df = df.merge(demo[["SEQN", "_race"]], on="SEQN", how="left")
        black = df[df["_race"] == "Non-Hispanic Black"].copy()
        black["pred_class"] = (black["predicted_probability"] >= thresh).astype(int)
        arm_data[arm] = black

    cc, mi = arm_data["complete_case"], arm_data["multiple_imputation"]
    n_cc, n_mi = len(cc), len(mi)
    n_pos_cc, n_neg_cc = int((cc["true_target"] == 1).sum()), int((cc["true_target"] == 0).sum())
    n_pos_mi, n_neg_mi = int((mi["true_target"] == 1).sum()), int((mi["true_target"] == 0).sum())

    sens_cc, fnr_cc, spec_cc, fpr_cc = sens_fnr_spec_fpr(cc["true_target"].values, cc["pred_class"].values)
    sens_mi, fnr_mi, spec_mi, fpr_mi = sens_fnr_spec_fpr(mi["true_target"].values, mi["pred_class"].values)

    # Bootstrap CI for the sensitivity DIFFERENCE (MI - CC), resampling each arm's Black subgroup independently
    # (arms have different N and different, only partially overlapping participant sets -- 615 additional MI-only
    # participants -- so independent resampling per arm, not paired-by-participant, is the correct design here)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    diffs = []
    y_cc_arr, yhat_cc_arr = cc["true_target"].values, cc["pred_class"].values
    y_mi_arr, yhat_mi_arr = mi["true_target"].values, mi["pred_class"].values
    for _ in range(BOOTSTRAP_N):
        idx_cc = rng.integers(0, n_cc, size=n_cc)
        idx_mi = rng.integers(0, n_mi, size=n_mi)
        y_cc_b, yhat_cc_b = y_cc_arr[idx_cc], yhat_cc_arr[idx_cc]
        y_mi_b, yhat_mi_b = y_mi_arr[idx_mi], yhat_mi_arr[idx_mi]
        if (y_cc_b == 1).sum() == 0 or (y_mi_b == 1).sum() == 0:
            continue
        sens_cc_b = (yhat_cc_b[y_cc_b == 1] == 1).mean()
        sens_mi_b = (yhat_mi_b[y_mi_b == 1] == 1).mean()
        diffs.append(sens_mi_b - sens_cc_b)
    diffs = np.array(diffs)
    alpha = 1 - CI_LEVEL
    lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    point_diff = sens_mi - sens_cc
    ci_excludes_zero = bool(lo > 0 or hi < 0)

    # Two-sided bootstrap p-value: 2 * min(P(diff<=0), P(diff>=0)) among valid resamples, capped at 1
    p_le0 = (diffs <= 0).mean()
    p_ge0 = (diffs >= 0).mean()
    raw_p = min(1.0, 2 * min(p_le0, p_ge0))

    rows.append({
        "analysis_type": "Multiple-imputation missing-data sensitivity (exploratory tier)",
        "cohort": "COHORT_3B_ADULT_OF_QUALITY_VALID (N=7,768 full pool) vs its complete-case subset (N=7,153)",
        "model": model, "subgroup": "Non-Hispanic Black", "fairness_metric": "Sensitivity (true positive rate) at frozen Youden's J threshold",
        "frozen_threshold": thresh,
        "cc_n": n_cc, "cc_n_positive": n_pos_cc, "cc_n_negative": n_neg_cc,
        "mi_n": n_mi, "mi_n_positive": n_pos_mi, "mi_n_negative": n_neg_mi,
        "cc_sensitivity": round(sens_cc, 6), "mi_sensitivity": round(sens_mi, 6),
        "sensitivity_diff_mi_minus_cc": round(point_diff, 6),
        "sensitivity_diff_ci_lower": round(lo, 6), "sensitivity_diff_ci_upper": round(hi, 6),
        "ci_excludes_zero": ci_excludes_zero, "raw_p_bootstrap_two_sided": round(raw_p, 6),
        "cc_fnr": round(fnr_cc, 6), "mi_fnr": round(fnr_mi, 6),
        "cc_specificity": round(spec_cc, 6), "mi_specificity": round(spec_mi, 6),
        "cc_fpr": round(fpr_cc, 6), "mi_fpr": round(fpr_mi, 6),
        "bootstrap_n": BOOTSTRAP_N, "bootstrap_n_valid": len(diffs),
    })

out = pd.DataFrame(rows)

# BH-FDR across this single family (5 models x 1 subgroup x 1 fairness metric), mirroring the project's
# established one-family-per-(model x dimension) convention (Amendment #11) and its manual BH-FDR
# implementation (src/phase4_04_inference.py) -- statsmodels is not a pinned project dependency
pvals = out["raw_p_bootstrap_two_sided"].values
m_tests = len(pvals)
order = np.argsort(pvals)
ranked = pvals[order]
bh_adj = ranked * m_tests / (np.arange(m_tests) + 1)
bh_adj = np.minimum.accumulate(bh_adj[::-1])[::-1]
bh_adj = np.clip(bh_adj, 0, 1)
adj_pvals = np.empty(m_tests)
adj_pvals[order] = bh_adj
out["bh_fdr_adjusted_p"] = np.round(adj_pvals, 6)
out["significant_after_fdr"] = adj_pvals < 0.05

# Classification per Part 16 (A-F)
def classify(row):
    diff_pp = row["sensitivity_diff_mi_minus_cc"] * 100
    magnitude = abs(diff_pp)
    excludes_zero = row["ci_excludes_zero"]
    if row["bootstrap_n_valid"] < 500:
        return "F -- INDETERMINATE (insufficient valid bootstrap resamples)"
    if magnitude < 2.0 and not excludes_zero:
        return "A -- STABLE UNDER MI (magnitude <2pp, CI includes zero)"
    if not excludes_zero:
        return "F -- INDETERMINATE (CI includes zero; magnitude alone not used per Part 16)"
    if diff_pp > 0:
        return "C -- STRENGTHENED UNDER MI (effect larger, CI excludes zero)"
    else:
        return "B -- ATTENUATED/DIFFERENT DIRECTION UNDER MI (CI excludes zero, MI sensitivity lower than CC)"

out["classification"] = out.apply(classify, axis=1)

def interpret(row):
    diff_pp = row["sensitivity_diff_mi_minus_cc"] * 100
    direction = "higher" if diff_pp > 0 else "lower" if diff_pp < 0 else "unchanged"
    return (f"Including the 615 complete-case-excluded participants via multiple imputation changes "
            f"{row['model']}'s Non-Hispanic Black subgroup sensitivity by {diff_pp:+.2f} percentage points "
            f"({direction} under MI vs. complete-case), 95% bootstrap CI [{row['sensitivity_diff_ci_lower']*100:+.2f}, "
            f"{row['sensitivity_diff_ci_upper']*100:+.2f}] pp, {'excludes' if row['ci_excludes_zero'] else 'includes'} zero, "
            f"BH-FDR adjusted p={row['bh_fdr_adjusted_p']:.4f} ({'significant' if row['significant_after_fdr'] else 'not significant'} "
            f"at q=0.05). Classification: {row['classification'].split(' -- ')[0]}.")

out["interpretation"] = out.apply(interpret, axis=1)
out.to_csv(RESULTS_DIR / "mi_black_subgroup_comparison.csv", index=False)

print(out[["model", "cc_n", "mi_n", "cc_sensitivity", "mi_sensitivity", "sensitivity_diff_mi_minus_cc",
           "sensitivity_diff_ci_lower", "sensitivity_diff_ci_upper", "ci_excludes_zero",
           "bh_fdr_adjusted_p", "significant_after_fdr", "classification"]].to_string(index=False))
print(f"\nSaved results/sensitivity/mi_black_subgroup_comparison.csv ({len(out)} rows)")
