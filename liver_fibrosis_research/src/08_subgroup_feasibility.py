"""
08_subgroup_feasibility.py
Phase 1 Remediation - Subgroup Feasibility Audit, STAGE A (total sample size only).
Error 8 fix: total N alone is no longer described as "sufficient for fairness" --
that claim requires outcome-positive counts too (see 12_subgroup_outcome_feasibility.py,
Stage B). Both RIDRETH1 and RIDRETH3 are reported (Error 7).

Produces:
  documentation/audit_reports/subgroup_feasibility.csv
"""

import os, sys, warnings
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, RACE_MAP_RIDRETH1, RACE_MAP_RIDRETH3, SEX_MAP

warnings.filterwarnings("ignore", category=FutureWarning)

FEASIBILITY_NOTE = ("Total-sample-size feasibility only (Stage A). Total N alone does NOT establish "
                     "'sufficient for fairness analysis' -- statistical precision for sensitivity/FNR/"
                     "calibration depends on OUTCOME-POSITIVE counts within the subgroup, not just total N. "
                     "See subgroup_outcome_feasibility.csv (Stage B) for outcome-stratified counts.")

def main():
    print("=== Step 21: Subgroup Feasibility Audit -- STAGE A (Total N) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    n_total = len(master)
    print(f"Loaded master: {master.shape}")

    subgroups = []

    def add_group(category, var, value_map=None):
        if var not in master.columns:
            return
        vc = master[var].value_counts(dropna=False)
        for val, count in vc.items():
            lbl = "Missing" if pd.isna(val) else (value_map.get(val, f"Unknown ({val})") if value_map else str(val))
            subgroups.append({
                "category": category, "group_label": lbl, "group_value": str(val), "sample_size": int(count),
                "percentage": round(100 * count / n_total, 2),
                "total_n_ge_100": "Yes" if count >= 100 else "No",
                "feasibility_statement": FEASIBILITY_NOTE,
                "notes": f"Based on variable {var}"
            })

    add_group("Sex", "RIAGENDR", SEX_MAP)
    add_group("Race_Ethnicity_RIDRETH1", "RIDRETH1", RACE_MAP_RIDRETH1)
    add_group("Race_Ethnicity_RIDRETH3", "RIDRETH3", RACE_MAP_RIDRETH3)

    if "RIDAGEYR" in master.columns:
        age_bins = pd.cut(master["RIDAGEYR"], bins=[0, 17, 39, 59, 120], labels=["Under 18", "18-39", "40-59", "60+"])
        for val, count in age_bins.value_counts(dropna=False).items():
            subgroups.append({"category": "Age_Group_Provisional", "group_label": str(val), "group_value": str(val),
                              "sample_size": int(count), "percentage": round(100 * count / n_total, 2),
                              "total_n_ge_100": "Yes" if count >= 100 else "No",
                              "feasibility_statement": FEASIBILITY_NOTE,
                              "notes": "PROVISIONAL descriptive age grouping for feasibility only; not a locked Phase 2 bin scheme"})

    if "BMXBMI" in master.columns:
        bmi_bins = pd.cut(master["BMXBMI"], bins=[0, 18.5, 24.9, 29.9, 200],
                          labels=["Underweight (<18.5)", "Normal (18.5-24.9)", "Overweight (25-29.9)", "Obese (>=30)"])
        for val, count in bmi_bins.value_counts(dropna=False).items():
            lbl = "Missing" if pd.isna(val) else str(val)
            subgroups.append({"category": "BMI_Group_Provisional", "group_label": lbl, "group_value": str(val),
                              "sample_size": int(count), "percentage": round(100 * count / n_total, 2),
                              "total_n_ge_100": "Yes" if count >= 100 else "No",
                              "feasibility_statement": FEASIBILITY_NOTE,
                              "notes": "PROVISIONAL descriptive BMI grouping for feasibility only; not a locked Phase 2 bin scheme"})

    pd.DataFrame(subgroups).to_csv(AUDIT_DIR / "subgroup_feasibility.csv", index=False)
    print("  Saved subgroup_feasibility.csv (Stage A: total N only; see Stage B for outcome-positive counts).")
    print("[STEP 21 COMPLETE]")

if __name__ == "__main__":
    main()
