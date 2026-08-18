"""
phase2_01_candidate_cohorts.py
Phase 2C - Build and compare candidate PRIMARY analytical cohorts, extending the
frozen Phase 1 canonical cohorts (src/_cohorts.py) with the two additional axes
Phase 2 must resolve: adult restriction x elastography-quality rule x predictor-set
completeness. Every candidate cohort here is a documented composition of frozen
Phase 1 cohort masks -- no new independent filtering logic is invented.

Produces:
  results/tables/phase2_candidate_cohort_comparison.csv
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, TAB_DIR, CORE_LABS_BROAD, CORE_LABS_FASTING, RACE_MAP_RIDRETH3, SEX_MAP
from _cohorts import compute_all

def describe(master, mask, name, definition):
    df = master.loc[mask]
    n = len(df)
    row = {"candidate_cohort": name, "definition": definition, "n": n}
    if n == 0:
        return row
    row["n_outcome_available"] = int(df["LUXSMED"].notna().sum())
    row["pct_female"] = round(100 * (df["RIAGENDR"] == 2.0).mean(), 2)
    row["median_age"] = round(df["RIDAGEYR"].median(), 1)
    row["median_bmi"] = round(df["BMXBMI"].median(), 1) if df["BMXBMI"].notna().any() else None
    for code, lbl in RACE_MAP_RIDRETH3.items():
        row[f"pct_{lbl.replace(' ', '_').replace('/', '_')}"] = round(100 * (df["RIDRETH3"] == code).mean(), 2)
    row["n_positive_8.2kPa"] = int((df["LUXSMED"] >= 8.2).sum())
    row["prevalence_8.2kPa_pct"] = round(100 * row["n_positive_8.2kPa"] / n, 2)
    row["min_subgroup_outcome_positive_n"] = None  # filled below for race/ethnicity as the tightest dimension
    race_pos = [int((df.loc[df["RIDRETH3"] == code, "LUXSMED"] >= 8.2).sum()) for code in RACE_MAP_RIDRETH3]
    row["min_subgroup_outcome_positive_n"] = min(race_pos) if race_pos else None
    row["pct_broad_labs_missing_any"] = round(100 * (1 - df[CORE_LABS_BROAD].notna().all(axis=1).mean()), 2)
    row["pct_fasting_labs_missing_any"] = round(100 * (1 - df[CORE_LABS_FASTING].notna().all(axis=1).mean()), 2)
    row["pct_bmi_missing"] = round(100 * df["BMXBMI"].isna().mean(), 2)
    return row

def main():
    print("=== Phase 2C: Candidate Primary Cohort Comparison ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    c = compute_all(master)

    adult = master["RIDAGEYR"] >= 18
    broad_complete = master[CORE_LABS_BROAD].notna().all(axis=1)
    fasting_complete = master[CORE_LABS_FASTING].notna().all(axis=1)
    bmi_demo_complete = master["BMXBMI"].notna() & master["RIAGENDR"].notna()
    quality_valid = c["COHORT_2_QUALITY_VALID"][0]
    nonmissing = c["COHORT_1_NONMISSING_LUX"][0]

    candidates = [
        ("CAND_1_QUALITYVALID_ADULT_BROAD",
         nonmissing & quality_valid & adult & broad_complete & bmi_demo_complete,
         "Adult (>=18) AND LUAXSTAT==1 (NHANES quality-valid) AND broad labs (ALT/AST/albumin/ALP/bilirubin/"
         "platelets/HDL) complete AND BMI+sex non-missing. Complete-case for the finalized predictor set."),
        ("CAND_2_NONMISSINGONLY_ADULT_BROAD",
         nonmissing & adult & broad_complete & bmi_demo_complete,
         "Same as Candidate 1 but relaxes the quality-valid requirement to any non-missing LUXSMED "
         "(includes Partial exams). Sensitivity cohort for the elastography eligibility decision."),
        ("CAND_3_QUALITYVALID_ADULT_FASTING",
         nonmissing & quality_valid & adult & broad_complete & fasting_complete & bmi_demo_complete,
         "Candidate 1 further restricted to fasting labs (glucose+triglycerides) complete. Secondary "
         "predictor architecture (fasting-extended)."),
        ("CAND_4_QUALITYVALID_ALLAGES_BROAD",
         nonmissing & quality_valid & broad_complete & bmi_demo_complete,
         "Same as Candidate 1 but WITHOUT the adult restriction (includes ages 12-17, P_LUX's own target "
         "population). Sensitivity/exploratory cohort for the adult-only decision."),
    ]

    rows = [describe(master, mask, name, defn) for name, mask, defn in candidates]
    out = pd.DataFrame(rows)
    out.to_csv(TAB_DIR / "phase2_candidate_cohort_comparison.csv", index=False)
    for r in rows:
        print(f"  {r['candidate_cohort']}: N={r['n']}, outcome+={r.get('n_positive_8.2kPa')}, "
              f"min_race_subgroup_pos={r.get('min_subgroup_outcome_positive_n')}")
    print(f"  Saved phase2_candidate_cohort_comparison.csv ({len(out)} candidates).")
    print("[CANDIDATE COHORT COMPARISON COMPLETE]")

if __name__ == "__main__":
    main()
