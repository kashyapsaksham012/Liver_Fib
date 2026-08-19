"""
phase6_05_phase5_relationship.py
Phase 6 Part 13: connect Phase 5 fairness (sensitivity disparity) to Phase 6 uncertainty
(conformal coverage deviation from the 90% target). Reads ONLY the already-frozen, saved
outputs from Commit C (results/uncertainty/subgroup_coverage.csv) and Phase 5
(results/fairness/fairness_inference.csv) -- does NOT reopen the raw test set.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT

cov = pd.read_csv(ROOT / "results" / "uncertainty" / "subgroup_coverage.csv")
fair = pd.read_csv(ROOT / "results" / "fairness" / "fairness_inference.csv")

# fairness_inference.csv reports disparity vs. a REFERENCE group (no row for the reference
# category itself). Coverage deviation is defined for every category including the reference.
# Join on (model, dimension, category) where both exist; reference-category rows are kept in
# the output with disparity=NaN (there's no "disparity from itself").
fair_sub = fair[["model", "dimension", "category", "absolute_disparity_pp", "meaningful_disparity_ge_10pp_and_ci_excludes_zero",
                  "significant_after_fdr_0.05"]].rename(columns={
    "meaningful_disparity_ge_10pp_and_ci_excludes_zero": "sensitivity_disparity_meaningful",
    "significant_after_fdr_0.05": "sensitivity_disparity_fdr_significant",
})

merged = cov.merge(fair_sub, on=["model", "dimension", "category"], how="left")
merged["coverage_deviation_pp"] = merged["coverage_minus_target"] * 100

merged.to_csv(ROOT / "results" / "uncertainty" / "phase5_phase6_relationship.csv", index=False)

# Correlation: does larger |sensitivity disparity| co-occur with larger |coverage deviation|?
valid = merged.dropna(subset=["absolute_disparity_pp"])
corr_rows = []
for model in valid["model"].unique():
    sub = valid[valid["model"] == model]
    if len(sub) < 3:
        continue
    corr = np.corrcoef(sub["absolute_disparity_pp"].abs(), sub["coverage_deviation_pp"].abs())[0, 1]
    corr_rows.append({
        "model": model, "n_subgroup_comparisons": len(sub),
        "pearson_corr_abs_sensitivity_disparity_vs_abs_coverage_deviation": round(corr, 4),
    })
corr_out = pd.DataFrame(corr_rows)
corr_out.to_csv(ROOT / "results" / "uncertainty" / "phase5_phase6_correlation_summary.csv", index=False)

# Explicit co-occurrence check for the two Phase 5 headline subgroups
headline = merged[merged["category"].isin(["Obese", "60+"]) & merged["dimension"].isin(["bmi", "age"])]
headline_summary = headline[["model", "dimension", "category", "n", "empirical_coverage", "ci_lower", "ci_upper",
                              "ci_excludes_target", "absolute_disparity_pp", "sensitivity_disparity_meaningful",
                              "sensitivity_disparity_fdr_significant"]]
headline_summary.to_csv(ROOT / "results" / "uncertainty" / "phase5_headline_subgroup_coverage_cooccurrence.csv", index=False)

print("=== Correlation summary (all subgroups, |sensitivity disparity| vs |coverage deviation|) ===")
print(corr_out.to_string(index=False))
print("\n=== Co-occurrence check: Phase 5 headline subgroups (BMI Obese, Age 60+) ===")
print(headline_summary.to_string(index=False))
print(f"\nSaved results/uncertainty/phase5_phase6_relationship.csv ({len(merged)} rows)")
print("Saved results/uncertainty/phase5_phase6_correlation_summary.csv")
print("Saved results/uncertainty/phase5_headline_subgroup_coverage_cooccurrence.csv")
