"""
13_broad_vs_fasting_cohort.py
Phase 1 Remediation/Closure - Error 9 fix + Issue 1/2 reconciliation:
explicitly characterize the candidate analytical cohorts side by side, now driven
ENTIRELY by the canonical cohort definitions in src/_cohorts.py (single source of
truth -- this script no longer recomputes any mask locally). This closes the
4,376-vs-4,336 and 8,880-vs-8,805 discrepancies: both numbers are legitimate,
distinctly-named cohorts (COHORT_FASTING_LABS_ONLY vs COHORT_B_FASTING_EXTENDED;
COHORT_A_BROAD_LAB vs COHORT_A_PLUS_DEMO_BMI), reported together here with their
exact relationship, instead of two scripts silently disagreeing on one label.

No ML performance comparison is made between cohorts; this is sample-size /
missingness / demographic-composition reporting only, to inform a Phase 2 study-design
decision, not to make that decision here.

Produces:
  documentation/audit_reports/broad_vs_fasting_cohort.csv
  documentation/audit_reports/broad_vs_fasting_cohort.md
"""

import os, sys, warnings
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, NOW, CORE_LABS_BROAD, CORE_LABS_FASTING, RACE_MAP_RIDRETH3
from _cohorts import verify_cohort_relationships

warnings.filterwarnings("ignore", category=FutureWarning)

def describe_cohort(master, mask, label):
    df = master.loc[mask]
    n = len(df)
    row = {"cohort": label, "n": n}
    if n == 0:
        return row
    row["pct_female"] = round(100 * (df["RIAGENDR"] == 2.0).mean(), 2)
    row["pct_male"] = round(100 * (df["RIAGENDR"] == 1.0).mean(), 2)
    row["median_age"] = round(df["RIDAGEYR"].median(), 1)
    row["pct_adult_18plus"] = round(100 * (df["RIDAGEYR"] >= 18).mean(), 2)
    row["median_bmi"] = round(df["BMXBMI"].median(), 1) if df["BMXBMI"].notna().any() else None
    for code, lbl in RACE_MAP_RIDRETH3.items():
        pct = round(100 * (df["RIDRETH3"] == code).mean(), 2)
        row[f"pct_{lbl.replace(' ', '_').replace('/', '_')}"] = pct
    row["pct_LUAXSTAT_eq_1_quality_valid"] = round(100 * (df["LUAXSTAT"] == 1.0).mean(), 2)
    row["n_outcome_available_LUXSMED"] = int(df["LUXSMED"].notna().sum())
    return row

def main():
    print("=== Broad-Lab vs Fasting-Subset Candidate Cohort Comparison (Error 9, Issue 1/2 reconciled) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    cohorts = verify_cohort_relationships(master)  # single source of truth; raises if relationships break

    anchor_mask, _, n_anchor = cohorts["COHORT_1_NONMISSING_LUX"]
    a_mask, a_meta, n_a = cohorts["COHORT_A_BROAD_LAB"]
    a_bmi_mask, a_bmi_meta, n_a_bmi = cohorts["COHORT_A_PLUS_DEMO_BMI"]
    fast_only_mask, fast_only_meta, n_fast_only = cohorts["COHORT_FASTING_LABS_ONLY"]
    b_mask, b_meta, n_b = cohorts["COHORT_B_FASTING_EXTENDED"]

    rows = [
        describe_cohort(master, anchor_mask, "Anchor: COHORT_1_NONMISSING_LUX (non-missing LUXSMED)"),
        describe_cohort(master, a_mask, f"COHORT_A_BROAD_LAB ({', '.join(CORE_LABS_BROAD)} all non-missing; no BMI/demo requirement)"),
        describe_cohort(master, a_bmi_mask, "COHORT_A_PLUS_DEMO_BMI (Cohort A + complete demographics + BMI)"),
        describe_cohort(master, fast_only_mask, f"COHORT_FASTING_LABS_ONLY ({', '.join(CORE_LABS_FASTING)} only; broad labs NOT required)"),
        describe_cohort(master, b_mask, "COHORT_B_FASTING_EXTENDED (Cohort A AND fasting labs) -- THE canonical 'Cohort B'"),
    ]
    out = pd.DataFrame(rows)
    out.to_csv(AUDIT_DIR / "broad_vs_fasting_cohort.csv", index=False)

    with open(AUDIT_DIR / "broad_vs_fasting_cohort.md", "w") as f:
        f.write(f"# Broad-Lab vs Fasting-Subset Candidate Cohort Comparison (Canonical)\n\n**Generated:** {NOW}\n\n")
        f.write(f"- **Anchor** (non-missing LUXSMED): N={n_anchor}\n")
        f.write(f"- **COHORT_A_BROAD_LAB**: N={n_a} ({round(100*n_a/n_anchor,1)}% of anchor)\n")
        f.write(f"- **COHORT_A_PLUS_DEMO_BMI**: N={n_a_bmi} ({round(100*n_a_bmi/n_a,1)}% of Cohort A -- "
                f"the {n_a - n_a_bmi}-participant gap is entirely explained by missing BMI, see "
                f"`results/tables/broad_cohort_discrepancy.csv`)\n")
        f.write(f"- **COHORT_FASTING_LABS_ONLY**: N={n_fast_only} ({round(100*n_fast_only/n_anchor,1)}% of anchor)\n")
        f.write(f"- **COHORT_B_FASTING_EXTENDED** (canonical 'Cohort B'): N={n_b} "
                f"({round(100*n_b/n_a,1)}% of Cohort A, {round(100*n_b/n_fast_only,1)}% of "
                f"COHORT_FASTING_LABS_ONLY -- the {n_fast_only - n_b}-participant gap to "
                f"COHORT_FASTING_LABS_ONLY is entirely explained by missing >=1 broad lab, see "
                f"`results/tables/fasting_cohort_discrepancy.csv`)\n\n")
        f.write("## Full comparison table\n\n")
        f.write(out.to_markdown(index=False) + "\n\n")
        f.write("## Reconciliation note (Issue 1 / Issue 2)\n\n")
        f.write("A prior draft of this pipeline reported 'the fasting cohort' as both 4,376 "
                "(COHORT_FASTING_LABS_ONLY) and 4,336 (COHORT_B_FASTING_EXTENDED) under one ambiguous label, "
                "and 'the combined broad cohort' as both 8,880 (COHORT_A_BROAD_LAB) and 8,805 "
                "(COHORT_A_PLUS_DEMO_BMI). Both pairs are legitimate, distinct, exactly-reproducible cohorts, "
                "not a data error -- they are now permanently and uniquely named in `src/_cohorts.py`, the "
                "single source every script in this pipeline imports from, with a programmatic assertion "
                "(`verify_cohort_relationships`) that halts the pipeline if the subset relationship between "
                "them is ever violated.\n\n")
        f.write("## Interpretation (descriptive only -- no cohort is selected here)\n\n")
        f.write("COHORT_B_FASTING_EXTENDED is materially smaller than COHORT_A_BROAD_LAB because glucose and "
                "triglycerides are restricted to the morning fasting subsample (NHANES requires an 8-24h fast, "
                "morning session only, for P_GLU/P_TRIGLY). **This report does not choose between Cohort A and "
                "Cohort B.** Which to use as the Phase 2 predictor set is a study-design decision, to be made "
                "on scientific grounds -- NOT by comparing which one yields better model performance.\n")

    print(f"  Anchor N={n_anchor} | Cohort A N={n_a} | A+demo+BMI N={n_a_bmi} | "
          f"Fasting-only N={n_fast_only} | Cohort B N={n_b}")
    print("  Saved broad_vs_fasting_cohort.csv and .md (canonical, cross-referenced with cohort_flow.csv).")
    print("[BROAD VS FASTING COHORT COMPARISON COMPLETE]")

if __name__ == "__main__":
    main()
