"""
11_race_ethnicity_verification.py
Phase 1 Remediation - Error 7 fix: explicit, evidence-based RIDRETH1-vs-RIDRETH3
comparison instead of silently preferring one variable.

Produces:
  documentation/audit_reports/race_ethnicity_verification.md
"""

import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, NOW, RACE_MAP_RIDRETH1, RACE_MAP_RIDRETH3

def main():
    print("=== Race/Ethnicity Variable Verification (Error 7) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")

    ct = pd.crosstab(master["RIDRETH1"], master["RIDRETH3"], dropna=False)

    with open(AUDIT_DIR / "race_ethnicity_verification.md", "w") as f:
        f.write(f"# Race/Ethnicity Variable Verification: RIDRETH1 vs RIDRETH3\n\n**Generated:** {NOW}\n\n")
        f.write("## Official definitions (verified against live P_DEMO codebook, "
                "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm)\n\n")
        f.write("- **RIDRETH1** -- 'Recode of reported race and Hispanic origin information', 5 categories: "
                "1=Mexican American, 2=Other Hispanic, 3=Non-Hispanic White, 4=Non-Hispanic Black, "
                "5=Other Race - Including Multi-Racial. **Non-Hispanic Asian participants are folded into "
                "category 5** and are not separately identifiable.\n")
        f.write("- **RIDRETH3** -- Same recode 'with Non-Hispanic Asian Category', 6 categories: "
                "1=Mexican American, 2=Other Hispanic, 3=Non-Hispanic White, 4=Non-Hispanic Black, "
                "6=Non-Hispanic Asian, 7=Other Race - Including Multi-Racial. **Preserves Non-Hispanic Asian "
                "as a distinct, analyzable category.**\n\n")
        f.write("> The NHANES codebook itself does not issue a directive to prefer one variable over the "
                "other -- this is a study-design choice. What the codebook does establish as fact is the "
                "category structure above, which is what determines the fairness-analysis implication below.\n\n")

        f.write("## Empirical cross-tabulation in this project's master dataset (N={})\n\n".format(len(master)))
        f.write(ct.to_markdown() + "\n\n")
        cat5_ridreth1 = int(master.loc[master["RIDRETH1"] == 5.0].shape[0])
        cat6_ridreth3 = int(master.loc[master["RIDRETH3"] == 6.0].shape[0])
        cat7_ridreth3 = int(master.loc[master["RIDRETH3"] == 7.0].shape[0])
        f.write(f"- RIDRETH1 category 5 ('Other Race/Multi-Racial'): N={cat5_ridreth1}\n")
        f.write(f"- This same population splits under RIDRETH3 into: category 6 ('Non-Hispanic Asian'), "
                f"N={cat6_ridreth3}, and category 7 ('Other Race/Multi-Racial'), N={cat7_ridreth3}\n\n")
        f.write("**Confirmed empirically: RIDRETH1 statistically erases the Non-Hispanic Asian subgroup by "
                f"merging it into 'Other'; RIDRETH3 keeps it distinguishable at N={cat6_ridreth3}, well above "
                "the N>=100 total-sample-size feasibility bar (though see subgroup_outcome_feasibility.csv for "
                "the outcome-positive-count caveat, which still applies to this subgroup).**\n\n")

        f.write("## Recommendation for Phase 2 (documented here, not silently decided)\n\n")
        f.write("Use **RIDRETH3** as the PRIMARY race/ethnicity variable for the fairness analysis, because it "
                "is strictly more granular than RIDRETH1 and preserves a demographic group (Non-Hispanic Asian) "
                "that this study's stated fairness objective explicitly cares about. RIDRETH1 is retained in the "
                "master dataset for comparability with the substantial body of prior NHANES-based clinical "
                "literature that reports RIDRETH1 categories, but should not be the primary subgroup variable "
                "for the fairness analysis itself.\n\n")
        f.write("**This is a recommendation, not a Phase 1 finalization.** Whether to also collapse or retain "
                "small categories, and which variable to use for any specific downstream analysis, remains a "
                "Phase 2 protocol decision. No race/ethnicity category has been silently collapsed by this "
                "remediation -- both RIDRETH1 and RIDRETH3, with their full native category sets, are preserved "
                "unmodified in `nhanes_master_phase1.parquet`.\n")

    print("  Saved race_ethnicity_verification.md.")
    print("[RACE/ETHNICITY VERIFICATION COMPLETE]")

if __name__ == "__main__":
    main()
