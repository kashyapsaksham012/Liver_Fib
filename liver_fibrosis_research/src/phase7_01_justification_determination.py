"""
phase7_01_justification_determination.py
Project Phase 7 (Mitigation, = mentor Phase 13) Part 3: formal mitigation justification.
Reads results/fairness/fairness_inference.csv and results/uncertainty/coverage_inference.csv
DIRECTLY -- these CSVs are the authority, not report prose. Determines every (model, dimension,
category) combination where EITHER Phase 5 sensitivity disparity OR Phase 6 coverage deviation
was FDR-significant, and flags which satisfy the frozen dual criterion (BOTH significant) for
mitigation eligibility. Read-only -- computes no new statistics, fits no models, touches no
test-set predictions beyond reading the already-frozen inference CSVs.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT

fair = pd.read_csv(ROOT / "results" / "fairness" / "fairness_inference.csv")
cov = pd.read_csv(ROOT / "results" / "uncertainty" / "coverage_inference.csv")

fair_sig_keys = set(map(tuple, fair[fair["significant_after_fdr_0.05"] == True][["model", "dimension", "category"]].values))
cov_sig_keys = set(map(tuple, cov[cov["significant_after_fdr_0.05"] == True][["model", "dimension", "category"]].values))
union_keys = fair_sig_keys | cov_sig_keys

fair_idx = fair.set_index(["model", "dimension", "category"])
cov_idx = cov.set_index(["model", "dimension", "category"])

INSUFFICIENT_EVIDENCE_CATEGORIES = {"Underweight"}  # BMI Underweight: N_positive=1 in test set, insufficient-evidence tier (Phase 5 precision rule)
FRAGILE_UNCONFIRMED = {"Non-Hispanic Asian"}  # named explicitly in the task as an expected exclusion

rows = []
for model, dim, cat in sorted(union_keys):
    p5_sig = (model, dim, cat) in fair_sig_keys
    p6_sig = (model, dim, cat) in cov_sig_keys
    dual_qualified = p5_sig and p6_sig

    p5_row = fair_idx.loc[(model, dim, cat)] if (model, dim, cat) in fair_idx.index else None
    p6_row = cov_idx.loc[(model, dim, cat)] if (model, dim, cat) in cov_idx.index else None

    reason = []
    eligible = False
    if cat in INSUFFICIENT_EVIDENCE_CATEGORIES:
        reason.append("EXCLUDED: insufficient-evidence precision tier (N_positive=1 in test set) -- Phase 5 finding is non-interpretable as a point estimate regardless of mechanical significance")
    elif cat in FRAGILE_UNCONFIRMED and not p5_sig:
        reason.append("EXCLUDED: Phase 5 sensitivity disparity did not reach FDR significance (fragile, limited-precision N=14 positives) -- fails the dual criterion on the Phase 5 side")
    elif dual_qualified:
        # Check coverage DIRECTION: under-coverage (empirical < 0.90) is the reliability-failure
        # pattern co-occurring with Phase 5 sensitivity deficits; over-coverage (>0.90) reflects
        # excess caution/inefficiency, a qualitatively different phenomenon not addressed by the
        # same mitigation logic.
        coverage = p6_row["empirical_coverage"] if p6_row is not None else None
        direction = "under-coverage (below 90% target)" if coverage is not None and coverage < 0.90 else "over-coverage (above 90% target)"
        if coverage is not None and coverage < 0.90:
            eligible = True
            reason.append(f"ELIGIBLE: both Phase 5 sensitivity disparity and Phase 6 coverage deviation are FDR-significant, and coverage deviation is {direction} -- the reliability-failure pattern the dual criterion is designed to flag")
        else:
            reason.append(f"EXCLUDED despite meeting the mechanical dual-significance criterion: Phase 6 coverage deviation is {direction}, not under-coverage -- this is a different phenomenon (excess caution/inefficiency) from the reliability failure seen in the primary targets, and standard mitigation methods (group-wise recalibration, threshold adjustment, reweighting) are not designed to address it the same way")
    elif p5_sig and not p6_sig:
        reason.append("NOT DUAL-QUALIFIED: Phase 5 sensitivity disparity significant, but Phase 6 coverage deviation not FDR-significant")
    elif p6_sig and not p5_sig:
        reason.append("NOT DUAL-QUALIFIED: Phase 6 coverage deviation significant, but Phase 5 sensitivity disparity not FDR-significant")

    rows.append({
        "subgroup_dimension": dim, "subgroup_category": cat, "model": model,
        "phase5_metric": "sensitivity_disparity_pp (subgroup - reference)",
        "phase5_effect_size_pp": p5_row["absolute_disparity_pp"] if p5_row is not None else "N/A (not in Phase 5 significant set)",
        "phase5_ci_lower_pp": p5_row["ci_lower_pp"] if p5_row is not None else "N/A",
        "phase5_ci_upper_pp": p5_row["ci_upper_pp"] if p5_row is not None else "N/A",
        "phase5_bh_fdr_adjusted_p": p5_row["bh_fdr_adjusted_p"] if p5_row is not None else "N/A",
        "phase5_significant_after_fdr": p5_sig,
        "phase5_n_positive": p5_row["n_positive"] if p5_row is not None else "N/A",
        "phase5_precision_tier": p5_row["precision_tier"] if p5_row is not None else "N/A",
        "phase6_metric": "empirical_coverage vs 90% target",
        "phase6_empirical_coverage": p6_row["empirical_coverage"] if p6_row is not None else "N/A (not in Phase 6 significant set)",
        "phase6_ci_lower": p6_row["ci_lower"] if p6_row is not None else "N/A",
        "phase6_ci_upper": p6_row["ci_upper"] if p6_row is not None else "N/A",
        "phase6_bh_fdr_adjusted_p": p6_row["bh_fdr_adjusted_p"] if p6_row is not None else "N/A",
        "phase6_significant_after_fdr": p6_sig,
        "mitigation_eligible": eligible,
        "reason": " | ".join(reason),
    })

# Also explicitly record the two named expected-exclusion subgroups even where they involve
# models/dimensions not otherwise in the union (e.g. if Non-Hispanic Asian or Underweight never
# appear as FDR-significant for a given model, still document the check was performed).
for cat, dim in [("Non-Hispanic Asian", "race_ethnicity"), ("Underweight", "bmi")]:
    for model in ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]:
        if (model, dim, cat) in union_keys:
            continue  # already covered above
        p5_present = (model, dim, cat) in fair_idx.index
        p6_present = (model, dim, cat) in cov_idx.index
        rows.append({
            "subgroup_dimension": dim, "subgroup_category": cat, "model": model,
            "phase5_metric": "sensitivity_disparity_pp (subgroup - reference)",
            "phase5_effect_size_pp": fair_idx.loc[(model, dim, cat), "absolute_disparity_pp"] if p5_present else "N/A",
            "phase5_ci_lower_pp": fair_idx.loc[(model, dim, cat), "ci_lower_pp"] if p5_present else "N/A",
            "phase5_ci_upper_pp": fair_idx.loc[(model, dim, cat), "ci_upper_pp"] if p5_present else "N/A",
            "phase5_bh_fdr_adjusted_p": fair_idx.loc[(model, dim, cat), "bh_fdr_adjusted_p"] if p5_present else "N/A",
            "phase5_significant_after_fdr": False,
            "phase5_n_positive": fair_idx.loc[(model, dim, cat), "n_positive"] if p5_present else "N/A",
            "phase5_precision_tier": fair_idx.loc[(model, dim, cat), "precision_tier"] if p5_present else "N/A",
            "phase6_metric": "empirical_coverage vs 90% target",
            "phase6_empirical_coverage": cov_idx.loc[(model, dim, cat), "empirical_coverage"] if p6_present else "N/A",
            "phase6_ci_lower": cov_idx.loc[(model, dim, cat), "ci_lower"] if p6_present else "N/A",
            "phase6_ci_upper": cov_idx.loc[(model, dim, cat), "ci_upper"] if p6_present else "N/A",
            "phase6_bh_fdr_adjusted_p": cov_idx.loc[(model, dim, cat), "bh_fdr_adjusted_p"] if p6_present else "N/A",
            "phase6_significant_after_fdr": False,
            "mitigation_eligible": False,
            "reason": "EXCLUDED (not FDR-significant on either side for this model) -- included here for completeness of the named-exclusion audit" if cat not in INSUFFICIENT_EVIDENCE_CATEGORIES
                      else "EXCLUDED: insufficient-evidence precision tier (N_positive=1 in test set)",
        })

out = pd.DataFrame(rows).sort_values(["mitigation_eligible", "subgroup_dimension", "subgroup_category", "model"], ascending=[False, True, True, True])
out.to_csv(ROOT / "documentation" / "mitigation" / "phase7_justification_determination.csv", index=False)
print(out[["subgroup_dimension", "subgroup_category", "model", "phase5_significant_after_fdr",
           "phase6_significant_after_fdr", "mitigation_eligible"]].to_string(index=False))
print(f"\nSaved documentation/mitigation/phase7_justification_determination.csv ({len(out)} rows)")
n_eligible = out["mitigation_eligible"].sum()
print(f"\n{n_eligible} (model, subgroup) combinations are ELIGIBLE for mitigation under the frozen dual criterion.")
print(out[out["mitigation_eligible"]][["subgroup_dimension", "subgroup_category", "model"]].to_string(index=False))
