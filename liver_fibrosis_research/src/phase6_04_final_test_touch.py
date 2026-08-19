"""
phase6_04_final_test_touch.py
Phase 6 Part 9: THE FIRST AND ONLY OFFICIAL FINAL TEST-SET UNCERTAINTY TOUCH.

All decisions are already frozen (refit models, nonconformity score, conformal thresholds,
subgroup definitions inherited exactly from Phase 5, inference method = Wilson score interval
[Amendment #10], FDR family = Phase 6's own [Amendment #11]). This single script:
  1. Loads the locked test set and scores it with the refit models.
  2. Constructs prediction sets from the frozen per-model thresholds.
  3. Computes marginal coverage + efficiency (Part 10-11).
  4. Computes REQUIRED subgroup coverage + efficiency, exact Phase 5 bins (Part 12).
  5. Computes Wilson CIs and the Phase 6 FDR-corrected one-sample test (H0: coverage=90%).
No inspect-modify-rerun iteration follows this script. Downstream analyses (Part 13's Phase5-
Phase6 relationship) read this script's FROZEN, SAVED output only -- they do not reopen the
raw test set.
"""
import sys
import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, SPLIT_DIR, MODEL_NAMES, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL
from phase3_common import load_primary_dataset, fail
from phase5_common import DIMENSIONS, precision_tier, SEX_MAP, RACE_MAP_RIDRETH3, bin_age, bin_bmi

REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"
RESULTS_DIR = ROOT / "results" / "uncertainty"
CI_LEVEL = 0.95

def wilson_ci(k, n, level=CI_LEVEL):
    if n == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))

thresholds = pd.read_csv(RESULTS_DIR / "conformal_thresholds_by_model.csv").set_index("model")["threshold"]

master = load_primary_dataset()
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
if len(test_df) != 2146:
    fail(f"Test-set join produced {len(test_df)} rows, expected 2146")

test_df["_sex"] = test_df["RIAGENDR"].map(SEX_MAP)
test_df["_race"] = test_df["RIDRETH3"].map(RACE_MAP_RIDRETH3)
test_df["_age"] = test_df["RIDAGEYR"].apply(bin_age)
test_df["_bmi"] = test_df["BMXBMI"].apply(bin_bmi)

TOUCH_TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

marginal_rows = []
per_participant_records = []
subgroup_rows = []
inference_rows = []

for name in MODEL_NAMES:
    refit = joblib.load(REFIT_DIR / f"model_{name}_proper_train_refit.joblib")
    pipe = refit["pipeline"]
    threshold = thresholds[name]

    X_test = test_df[PRIMARY_PREDICTORS]
    y_test = test_df[PRIMARY_OUTCOME_COL].values
    proba_pos = pipe.predict_proba(X_test)[:, 1]

    # Prediction set: include candidate class c iff its nonconformity score 1-P(c|x) <= threshold.
    # score(x, c=1) = 1 - P(1|x) = 1 - proba_pos
    # score(x, c=0) = 1 - P(0|x) = 1 - (1 - proba_pos) = proba_pos
    include_pos = (1 - proba_pos) <= threshold
    include_neg = proba_pos <= threshold
    set_size = include_pos.astype(int) + include_neg.astype(int)
    true_in_set = np.where(y_test == 1, include_pos, include_neg)

    n = len(test_df)
    covered = int(true_in_set.sum())
    coverage = covered / n
    ci_lo, ci_hi = wilson_ci(covered, n)

    marginal_rows.append({
        "generated": TOUCH_TIMESTAMP, "model": name, "n": n, "target_coverage": 0.90,
        "empirical_coverage": round(coverage, 6), "ci_lower": round(ci_lo, 6), "ci_upper": round(ci_hi, 6),
        "ci_method": "Wilson score interval, 95% (Amendment #10)",
        "coverage_minus_target": round(coverage - 0.90, 6),
        "mean_set_size": round(float(set_size.mean()), 6), "median_set_size": float(np.median(set_size)),
        "singleton_rate": round(float((set_size == 1).mean()), 6),
        "ambiguous_rate_both_classes": round(float((set_size == 2).mean()), 6),
        "empty_set_rate": round(float((set_size == 0).mean()), 6),
        "threshold_used": threshold,
    })

    per_participant_records.append(pd.DataFrame({
        "SEQN": test_df["SEQN"].values, "model": name, "true_target": y_test,
        "predicted_probability_positive": proba_pos, "include_negative": include_neg,
        "include_positive": include_pos, "set_size": set_size, "true_in_set": true_in_set,
        "_sex": test_df["_sex"].values, "_race": test_df["_race"].values,
        "_age": test_df["_age"].values, "_bmi": test_df["_bmi"].values,
    }))

    for dim, spec in DIMENSIONS.items():
        col = "_" + dim.replace("race_ethnicity", "race")
        for cat in test_df[col].dropna().unique():
            mask = test_df[col].values == cat
            sub_n = int(mask.sum())
            sub_y = y_test[mask]
            sub_covered = int(true_in_set[mask].sum())
            sub_coverage = sub_covered / sub_n if sub_n else None
            slo, shi = wilson_ci(sub_covered, sub_n)
            n_pos, n_neg = int((sub_y == 1).sum()), int((sub_y == 0).sum())
            tier = precision_tier(n_pos, n_neg)

            # One-sample exact binomial test: H0 coverage = 0.90
            p_val = stats.binomtest(sub_covered, sub_n, 0.90, alternative="two-sided").pvalue if sub_n else None

            subgroup_rows.append({
                "generated": TOUCH_TIMESTAMP, "model": name, "dimension": dim, "category": cat,
                "n": sub_n, "n_positive": n_pos, "n_negative": n_neg, "precision_tier": tier,
                "empirical_coverage": round(sub_coverage, 6), "ci_lower": round(slo, 6), "ci_upper": round(shi, 6),
                "ci_method": "Wilson score interval, 95%",
                "coverage_minus_target": round(sub_coverage - 0.90, 6),
                "ci_excludes_target": bool(slo > 0.90 or shi < 0.90),
                "mean_set_size": round(float(set_size[mask].mean()), 6),
                "singleton_rate": round(float((set_size[mask] == 1).mean()), 6),
                "raw_p_binomial_vs_90pct": round(p_val, 6),
            })
            inference_rows.append({"model": name, "dimension": dim, "category": cat, "raw_p": p_val})

marginal_out = pd.DataFrame(marginal_rows)
marginal_out.to_csv(RESULTS_DIR / "marginal_coverage_test_set.csv", index=False)

pd.concat(per_participant_records, ignore_index=True).to_csv(RESULTS_DIR / "test_set_prediction_sets.csv", index=False)

subgroup_out = pd.DataFrame(subgroup_rows)

# Phase 6 FDR family (Amendment #11): BH-FDR per (model x dimension), independent of subgroup_out row order
inf_df = pd.DataFrame(inference_rows)
adj_rows = []
for (model, dim), grp in inf_df.groupby(["model", "dimension"]):
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
        adj_rows.append({"model": model, "dimension": dim, "category": cat, "bh_fdr_adjusted_p": round(float(a), 6)})
adj_df = pd.DataFrame(adj_rows)

subgroup_out = subgroup_out.merge(adj_df, on=["model", "dimension", "category"], how="left")
subgroup_out["significant_after_fdr_0.05"] = subgroup_out["bh_fdr_adjusted_p"] < 0.05
subgroup_out.to_csv(RESULTS_DIR / "subgroup_coverage.csv", index=False)

subgroup_out[["model", "dimension", "category", "n", "empirical_coverage", "ci_lower", "ci_upper",
              "raw_p_binomial_vs_90pct", "bh_fdr_adjusted_p", "significant_after_fdr_0.05"]].to_csv(
    RESULTS_DIR / "coverage_inference.csv", index=False)

print(marginal_out.to_string(index=False))
print(f"\nSaved results/uncertainty/marginal_coverage_test_set.csv")
print(f"Saved results/uncertainty/subgroup_coverage.csv ({len(subgroup_out)} rows)")
print(f"Saved results/uncertainty/coverage_inference.csv")
print(f"Saved results/uncertainty/test_set_prediction_sets.csv (per-participant, per-model)")
print(f"\nTest-set touch timestamp: {TOUCH_TIMESTAMP}")
print("THIS IS THE FIRST AND ONLY OFFICIAL FINAL TEST-SET UNCERTAINTY TOUCH. Do not re-run.")
