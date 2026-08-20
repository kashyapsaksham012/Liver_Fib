"""
sens_01_construct_cohorts.py
Deferred Sensitivity Analysis Execution, Parts 5-6: construct the CAND_2 (relaxed elastography
eligibility) analysis dataset, exactly mirroring phase2_04_build_analysis_dataset.py's own
primary-dataset construction pattern but substituting the non-missing-only elastography rule for
the quality-valid rule (per CAND_2's frozen definition, primary_cohort_decision.md). CAND_3
(fasting-extended) already exists as data/processed/analysis_dataset_secondary.parquet (built in
Phase 2) and is verified, not reconstructed. CAND_1 (primary, for the alternative-threshold
analysis) is also verified, not reconstructed -- it already exists unchanged.

No retraining occurs in this script -- it only constructs and verifies cohorts.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import INT_DIR, ROOT, CORE_LABS_BROAD, RACE_MAP_RIDRETH3, SEX_MAP
from _cohorts import compute_all

PROC_DIR = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "results" / "sensitivity"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL",
                       "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
CARRY_COLUMNS = ["SEQN", "LUXSMED", "RIDRETH1", "RIDRETH3",
                  "WTMECPRP", "WTINTPRP", "WTSAFPRP", "SDMVPSU", "SDMVSTRA"]

def add_outcomes(df):
    df = df.copy()
    df["outcome_primary_8.2kPa"] = (df["LUXSMED"] >= 8.2).astype(int)
    df["outcome_sensitivity_8.0kPa"] = (df["LUXSMED"] >= 8.0).astype(int)
    df["age_group_final"] = pd.cut(df["RIDAGEYR"], bins=[17, 39, 59, 120], labels=["18-39", "40-59", "60+"])
    df["bmi_group_final"] = pd.cut(df["BMXBMI"], bins=[0, 18.5, 24.9, 29.9, 200],
                                    labels=["Underweight", "Normal", "Overweight", "Obese"])
    return df

def summarize(df, label):
    n = len(df)
    pos = int(df["outcome_primary_8.2kPa"].sum())
    rows = [{
        "cohort": label, "n": n, "n_positive_8.2kPa": pos, "n_negative_8.2kPa": n - pos,
        "prevalence_8.2kPa_pct": round(100 * pos / n, 4),
        "pct_female": round(100 * (df["RIAGENDR"] == 2.0).mean(), 2),
        "median_age": round(df["RIDAGEYR"].median(), 1),
        "median_bmi": round(df["BMXBMI"].median(), 1),
    }]
    for code, lbl in RACE_MAP_RIDRETH3.items():
        rows[0][f"pct_{lbl.replace(' ', '_').replace('/', '_')}"] = round(100 * (df["RIDRETH3"] == code).mean(), 2)
    return rows[0]

def main():
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    c = compute_all(master)
    adult = master["RIDAGEYR"] >= 18
    broad_complete = master[CORE_LABS_BROAD].notna().all(axis=1)
    bmi_demo_complete = master["BMXBMI"].notna() & master["RIAGENDR"].notna()
    nonmissing = c["COHORT_1_NONMISSING_LUX"][0]

    # CAND_2_NONMISSINGONLY_ADULT_BROAD -- relaxes quality-valid (LUAXSTAT==1) to any non-missing LUXSMED
    cand2_mask = nonmissing & adult & broad_complete & bmi_demo_complete
    cand2_cols = CARRY_COLUMNS + PRIMARY_PREDICTORS
    cand2_df = add_outcomes(master.loc[cand2_mask, cand2_cols])

    if len(cand2_df) != 7639:
        print(f"SENSITIVITY STOP CONDITION: CAND_2 N={len(cand2_df)}, expected 7639 (archived, primary_cohort_decision.md)")
        sys.exit(1)
    if int(cand2_df["outcome_primary_8.2kPa"].sum()) != 804:
        print(f"SENSITIVITY STOP CONDITION: CAND_2 positive={int(cand2_df['outcome_primary_8.2kPa'].sum())}, expected 804")
        sys.exit(1)

    cand2_df.to_parquet(PROC_DIR / "analysis_dataset_cand2_relaxed_elastography.parquet", index=False)
    print(f"CAND_2 constructed and verified: N={len(cand2_df)}, positive={int(cand2_df['outcome_primary_8.2kPa'].sum())} -- matches archived N=7639/804 exactly")

    # Verify CAND_3 (fasting-extended) already exists and matches archived counts
    cand3_df = pd.read_parquet(PROC_DIR / "analysis_dataset_secondary.parquet")
    if len(cand3_df) != 3582 or int(cand3_df["outcome_primary_8.2kPa"].sum()) != 319:
        print(f"SENSITIVITY STOP CONDITION: CAND_3 N={len(cand3_df)} pos={int(cand3_df['outcome_primary_8.2kPa'].sum())}, expected 3582/319")
        sys.exit(1)
    print(f"CAND_3 verified (already built in Phase 2): N={len(cand3_df)}, positive={int(cand3_df['outcome_primary_8.2kPa'].sum())} -- matches archived N=3582/319 exactly")

    # Verify CAND_1 (primary, unchanged, used for the alternative-threshold analysis)
    cand1_df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    if len(cand1_df) != 7153 or int(cand1_df["outcome_primary_8.2kPa"].sum()) != 666:
        print(f"SENSITIVITY STOP CONDITION: CAND_1 N={len(cand1_df)} pos={int(cand1_df['outcome_primary_8.2kPa'].sum())}, expected 7153/666"); sys.exit(1)
    if "outcome_sensitivity_8.0kPa" not in cand1_df.columns:
        print("SENSITIVITY STOP CONDITION: CAND_1 missing outcome_sensitivity_8.0kPa column"); sys.exit(1)
    n_pos_80 = int(cand1_df["outcome_sensitivity_8.0kPa"].sum())
    print(f"CAND_1 verified (unchanged primary cohort): N={len(cand1_df)}, positive@8.2kPa={int(cand1_df['outcome_primary_8.2kPa'].sum())}, positive@8.0kPa={n_pos_80}")

    summary_rows = [
        summarize(cand2_df, "CAND_2_NONMISSINGONLY_ADULT_BROAD (relaxed elastography eligibility)"),
        summarize(cand3_df, "CAND_3_QUALITYVALID_ADULT_FASTING (fasting-extended, already built in Phase 2)"),
    ]
    pd.DataFrame(summary_rows).to_csv(RESULTS_DIR / "relaxed_elastography_cohort_summary.csv", index=False)
    pd.DataFrame([summary_rows[1]]).to_csv(RESULTS_DIR / "fasting_extended_cohort_summary.csv", index=False)
    print("\nSaved results/sensitivity/relaxed_elastography_cohort_summary.csv")
    print("Saved results/sensitivity/fasting_extended_cohort_summary.csv")

if __name__ == "__main__":
    main()
