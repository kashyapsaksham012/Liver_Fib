"""
12_subgroup_outcome_feasibility.py
Phase 1 Remediation - Error 8 fix, STAGE B: outcome-positive/negative counts per
subgroup, not just total N. A large total N with very few outcome-positive cases
cannot reliably support sensitivity/FNR/calibration estimation -- this stage makes
that visible instead of declaring "N>=100 -> sufficient."

Uses a PROVISIONAL candidate outcome (LUXSMED >= 8.2 kPa, the meta-analytic
Youden-optimal cutoff for significant fibrosis identified in phase1_references.md)
applied ONLY for this feasibility count -- NOT a finalized outcome definition.
Computed on the LUAXSTAT==1 (NHANES quality-valid) subset, since that is the
scientifically correct denominator per the Error 2/3 finding; the non-missing-only
denominator is reported alongside for comparison.

Produces:
  documentation/audit_reports/subgroup_outcome_feasibility.csv
"""

import os, sys, warnings
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, RACE_MAP_RIDRETH1, RACE_MAP_RIDRETH3, SEX_MAP

warnings.filterwarnings("ignore", category=FutureWarning)

PROVISIONAL_CUTPOINT = 8.2  # kPa; see _common.CANDIDATE_THRESHOLDS citation (PMC11493355, 2024)
FEASIBILITY_WORDING = ("Potentially feasible; final statistical precision depends on outcome-positive "
                       "counts and confidence-interval width, not on total N alone.")

# Issue 12: classify feasibility from outcome-POSITIVE count (the binding constraint for
# sensitivity/FNR precision). Thresholds are a PROJECT-DEFINED heuristic based on standard
# binomial-proportion confidence-interval width (a 95% Wilson CI half-width is roughly
# +/-18% at N=30 and +/-10% at N=100, at p=0.5) -- NOT an NHANES or universal statistical
# standard. Groups are NEVER dropped or pooled based on this classification; it is reported
# information only, per Issue 12 / non-negotiable rule.
def classify_feasibility(n_positive, n_negative):
    if n_positive < 10 or n_negative < 10:
        return "insufficient evidence"
    if n_positive < 30 or n_negative < 30:
        return "limited precision"
    if n_positive < 100 or n_negative < 100:
        return "exploratory candidate"
    return "primary-feasibility candidate"

def outcome_rows(df, category_label, var, value_map, denom_label):
    rows = []
    if var not in df.columns:
        return rows
    for val, grp in df.groupby(var, dropna=False):
        lbl = "Missing" if pd.isna(val) else (value_map.get(val, f"Unknown ({val})") if value_map else str(val))
        n_total = len(grp)
        n_outcome_avail = int(grp["LUXSMED"].notna().sum())
        pos = int((grp["LUXSMED"] >= PROVISIONAL_CUTPOINT).sum())
        neg = n_outcome_avail - pos
        assert pos + neg == n_outcome_avail, "positive + negative must equal n_with_outcome_available (Issue 11)"
        rows.append({
            "denominator": denom_label, "category": category_label, "group_label": lbl, "group_value": str(val),
            "total_n": n_total, "n_with_outcome_available": n_outcome_avail,
            "provisional_outcome_positive_n": pos, "provisional_outcome_negative_n": neg,
            "provisional_positive_prevalence_pct": round(100*pos/n_outcome_avail, 2) if n_outcome_avail else None,
            "provisional_negative_prevalence_pct": round(100*neg/n_outcome_avail, 2) if n_outcome_avail else None,
            "provisional_cutpoint_kpa": PROVISIONAL_CUTPOINT,
            "feasibility_classification": classify_feasibility(pos, neg) if n_outcome_avail else "insufficient evidence (empty group)",
            "feasibility_statement": FEASIBILITY_WORDING
        })
    return rows

def main():
    print("=== Subgroup Outcome Feasibility Audit -- STAGE B (Error 8) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")

    valid = master[master["LUAXSTAT"] == 1.0].copy()
    nonmissing = master[master["LUXSMED"].notna()].copy()
    print(f"Quality-valid (LUAXSTAT==1) N={len(valid)}; non-missing-LUXSMED N={len(nonmissing)}")

    all_rows = []
    for denom_df, denom_label in [(valid, "LUAXSTAT==1 (quality-valid, PRIMARY)"),
                                   (nonmissing, "non-missing LUXSMED (any completeness, comparison)")]:
        all_rows += outcome_rows(denom_df, "Sex", "RIAGENDR", SEX_MAP, denom_label)
        all_rows += outcome_rows(denom_df, "Race_Ethnicity_RIDRETH1", "RIDRETH1", RACE_MAP_RIDRETH1, denom_label)
        all_rows += outcome_rows(denom_df, "Race_Ethnicity_RIDRETH3", "RIDRETH3", RACE_MAP_RIDRETH3, denom_label)

        if "RIDAGEYR" in denom_df.columns:
            d2 = denom_df.copy()
            d2["_age_bin"] = pd.cut(d2["RIDAGEYR"], bins=[0, 17, 39, 59, 120], labels=["Under 18", "18-39", "40-59", "60+"])
            all_rows += outcome_rows(d2, "Age_Group_Provisional", "_age_bin", None, denom_label)

        if "BMXBMI" in denom_df.columns:
            d3 = denom_df.copy()
            d3["_bmi_bin"] = pd.cut(d3["BMXBMI"], bins=[0, 18.5, 24.9, 29.9, 200],
                                    labels=["Underweight (<18.5)", "Normal (18.5-24.9)", "Overweight (25-29.9)", "Obese (>=30)"])
            all_rows += outcome_rows(d3, "BMI_Group_Provisional", "_bmi_bin", None, denom_label)

    out = pd.DataFrame(all_rows)
    out.to_csv(AUDIT_DIR / "subgroup_outcome_feasibility.csv", index=False)
    print(f"  Saved subgroup_outcome_feasibility.csv ({len(out)} rows). Feasibility classification counts:")
    print(out["feasibility_classification"].value_counts().to_string())
    print("  No group was dropped or pooled based on this classification (Issue 12 / non-negotiable rule).")
    print("[SUBGROUP OUTCOME FEASIBILITY COMPLETE]")

if __name__ == "__main__":
    main()
