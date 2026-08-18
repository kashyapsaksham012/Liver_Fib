"""
20_denominator_registry.py
Phase 1 Closure - Closure Phase E: for every number that appears anywhere in the
final report, register its numerator, denominator, exact definition, source script,
and cohort name, so no ambiguous statistic can appear without a traceable origin.

Produces:
  documentation/audit_reports/phase1_denominator_registry.csv
"""

import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, CANDIDATE_THRESHOLDS
from _cohorts import compute_all

def main():
    print("=== Denominator Registry (Closure Phase E) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    cohorts = compute_all(master)
    n_total = len(master)

    rows = []
    def reg(report_section, statistic_name, numerator, denominator, denominator_n, definition, cohort_name, source_script):
        rows.append({"report_section": report_section, "statistic_name": statistic_name, "numerator": numerator,
                    "denominator": denominator, "denominator_n": denominator_n, "definition": definition,
                    "cohort_name": cohort_name, "source_script": source_script})

    reg("C", "Master dataset row count", n_total, "P_LUX raw row count", n_total,
        "One row per P_LUX-examined participant", "COHORT_0_SOURCE", "05_merge_nhanes.py")

    reg("E/F", "Non-missing LUXSMED", cohorts["COHORT_1_NONMISSING_LUX"][2], "COHORT_0_SOURCE", n_total,
        "LUXSMED not null, any exam completeness", "COHORT_1_NONMISSING_LUX", "07_quality_and_plausibility_audit.py")
    reg("E/F", "Quality-valid elastography (LUAXSTAT==1)", cohorts["COHORT_2_QUALITY_VALID"][2],
        "COHORT_1_NONMISSING_LUX", cohorts["COHORT_1_NONMISSING_LUX"][2],
        "Official NHANES 'Complete' exam status", "COHORT_2_QUALITY_VALID", "07_quality_and_plausibility_audit.py")
    reg("E", "Adults among non-missing LUXSMED", cohorts["COHORT_3A_ADULT_OF_NONMISSING"][2],
        "COHORT_1_NONMISSING_LUX", cohorts["COHORT_1_NONMISSING_LUX"][2], "RIDAGEYR>=18 within Cohort 1",
        "COHORT_3A_ADULT_OF_NONMISSING", "07_quality_and_plausibility_audit.py")
    reg("E", "Adults among quality-valid", cohorts["COHORT_3B_ADULT_OF_QUALITY_VALID"][2],
        "COHORT_2_QUALITY_VALID", cohorts["COHORT_2_QUALITY_VALID"][2], "RIDAGEYR>=18 within Cohort 2",
        "COHORT_3B_ADULT_OF_QUALITY_VALID", "07_quality_and_plausibility_audit.py")
    reg("N", "Broad routine-lab cohort (Cohort A)", cohorts["COHORT_A_BROAD_LAB"][2],
        "COHORT_1_NONMISSING_LUX", cohorts["COHORT_1_NONMISSING_LUX"][2],
        "7 broad labs all non-missing within Cohort 1", "COHORT_A_BROAD_LAB", "13_broad_vs_fasting_cohort.py")
    reg("N", "Cohort A + complete demo/BMI", cohorts["COHORT_A_PLUS_DEMO_BMI"][2],
        "COHORT_A_BROAD_LAB", cohorts["COHORT_A_BROAD_LAB"][2], "Cohort A AND RIAGENDR AND BMXBMI non-missing",
        "COHORT_A_PLUS_DEMO_BMI", "13_broad_vs_fasting_cohort.py")
    reg("N", "Fasting labs available (only)", cohorts["COHORT_FASTING_LABS_ONLY"][2],
        "COHORT_1_NONMISSING_LUX", cohorts["COHORT_1_NONMISSING_LUX"][2],
        "Glucose+triglycerides non-missing within Cohort 1, broad labs not required",
        "COHORT_FASTING_LABS_ONLY", "13_broad_vs_fasting_cohort.py")
    reg("N", "Cohort B (fasting-extended, canonical)", cohorts["COHORT_B_FASTING_EXTENDED"][2],
        "COHORT_A_BROAD_LAB", cohorts["COHORT_A_BROAD_LAB"][2], "Cohort A AND fasting labs non-missing",
        "COHORT_B_FASTING_EXTENDED", "13_broad_vs_fasting_cohort.py")

    for t in CANDIDATE_THRESHOLDS:
        for denom_name in ["COHORT_1_NONMISSING_LUX", "COHORT_2_QUALITY_VALID"]:
            dmask, _, dn = cohorts[denom_name]
            n_pos = int((master.loc[dmask, "LUXSMED"] >= t["kpa"]).sum())
            reg("F", f"Provisional cutpoint {t['kpa']}kPa positive count", n_pos, denom_name, dn,
                f"LUXSMED >= {t['kpa']} within {denom_name}", denom_name, "19_cohort_reconciliation.py")

    lab_files = {"LBXSATSI": "P_BIOPRO.xpt", "LBXSASSI": "P_BIOPRO.xpt", "LBXSAL": "P_BIOPRO.xpt",
                "LBXSAPSI": "P_BIOPRO.xpt", "LBXSTB": "P_BIOPRO.xpt", "LBXPLTSI": "P_CBC.xpt",
                "LBXGLU": "P_GLU.xpt", "LBXTR": "P_TRIGLY.xpt", "LBDHDD": "P_HDL.xpt"}
    for var, src in lab_files.items():
        n_obs = int(master[var].notna().sum())
        reg("I", f"{var} availability", n_obs, "COHORT_0_SOURCE (full master)", n_total,
            f"{var} non-missing within the full master cohort (NOT the raw {src} file's own row count -- "
            "see Section H fix, prior report conflated these)", "COHORT_0_SOURCE", "18_generate_phase1_report.py")

    df = pd.DataFrame(rows)
    df.to_csv(AUDIT_DIR / "phase1_denominator_registry.csv", index=False)
    print(f"  Saved phase1_denominator_registry.csv ({len(df)} registered statistics).")
    print("[DENOMINATOR REGISTRY COMPLETE]")

if __name__ == "__main__":
    main()
