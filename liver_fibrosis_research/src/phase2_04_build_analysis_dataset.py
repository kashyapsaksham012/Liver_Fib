"""
phase2_04_build_analysis_dataset.py
Phase 2X - Generate the FROZEN primary (and secondary) analysis datasets. Run ONLY
after documentation/phase2/PHASE2_PROTOCOL_FREEZE.md exists. Built exclusively from
frozen Phase 1 data (src/_cohorts.py) and frozen Phase 2 definitions above -- no
model performance was inspected while creating this dataset.

Produces:
  data/processed/analysis_dataset_primary.parquet   (N=7,153, 10 predictors)
  data/processed/analysis_dataset_secondary.parquet (N=3,582, 12 predictors, fasting-extended)
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, ROOT, RACE_MAP_RIDRETH3, SEX_MAP
from _cohorts import compute_all

assert (ROOT / "documentation" / "phase2" / "PHASE2_PROTOCOL_FREEZE.md").exists(), \
    "Protocol must be frozen (PHASE2_PROTOCOL_FREEZE.md) before generating the analysis dataset."

PROC_DIR = ROOT / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL",
                     "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
SECONDARY_ONLY_PREDICTORS = ["LBXGLU", "LBXTR"]
CARRY_COLUMNS = ["SEQN", "LUXSMED", "RIDRETH1", "RIDRETH3",
                 "WTMECPRP", "WTINTPRP", "WTSAFPRP", "SDMVPSU", "SDMVSTRA"]

def add_outcomes(df):
    df = df.copy()
    df["outcome_primary_8.2kPa"] = (df["LUXSMED"] >= 8.2).astype(int)
    df["outcome_sensitivity_8.0kPa"] = (df["LUXSMED"] >= 8.0).astype(int)
    df["outcome_secondary_advanced_9.7kPa"] = (df["LUXSMED"] >= 9.7).astype(int)
    df["outcome_secondary_cirrhosis_13.6kPa"] = (df["LUXSMED"] >= 13.6).astype(int)
    df["age_group_final"] = pd.cut(df["RIDAGEYR"], bins=[17, 39, 59, 120], labels=["18-39", "40-59", "60+"])
    df["bmi_group_final"] = pd.cut(df["BMXBMI"], bins=[0, 18.5, 24.9, 29.9, 200],
                                   labels=["Underweight", "Normal", "Overweight", "Obese"])
    return df

def summarize(df, label, predictors):
    n = len(df)
    print(f"\n--- {label}: N={n} ---")
    print(f"  Predictor columns: {predictors}")
    print(f"  Outcome positive/negative (primary 8.2kPa): {int(df['outcome_primary_8.2kPa'].sum())} / "
          f"{n - int(df['outcome_primary_8.2kPa'].sum())} ({round(100*df['outcome_primary_8.2kPa'].mean(),2)}%)")
    miss = df[predictors].isna().sum()
    print(f"  Missingness in predictors (should be all-zero, complete-case by construction): "
          f"{dict(miss[miss > 0]) if miss.sum() else 'none (complete)'}")
    print(f"  Sex: {dict((SEX_MAP.get(k,k), v) for k,v in df['RIAGENDR'].value_counts().items())}")
    print(f"  Race/Ethnicity (RIDRETH3): {dict((RACE_MAP_RIDRETH3.get(k,k), v) for k,v in df['RIDRETH3'].value_counts().items())}")
    print(f"  Age group: {dict(df['age_group_final'].value_counts())}")
    print(f"  BMI group: {dict(df['bmi_group_final'].value_counts())}")

def main():
    print("=== Phase 2X: Generate Frozen Primary & Secondary Analysis Datasets ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    c = compute_all(master)
    adult = master["RIDAGEYR"] >= 18
    quality_valid = c["COHORT_2_QUALITY_VALID"][0]
    broad_complete = master[[p for p in PRIMARY_PREDICTORS if p.startswith("LB")]].notna().all(axis=1)
    bmi_demo_complete = master["BMXBMI"].notna() & master["RIAGENDR"].notna()
    fasting_complete = master[SECONDARY_ONLY_PREDICTORS].notna().all(axis=1)

    primary_mask = quality_valid & adult & broad_complete & bmi_demo_complete
    secondary_mask = primary_mask & fasting_complete

    primary_cols = CARRY_COLUMNS + PRIMARY_PREDICTORS
    primary_df = add_outcomes(master.loc[primary_mask, primary_cols])
    primary_df.to_parquet(PROC_DIR / "analysis_dataset_primary.parquet", index=False)
    summarize(primary_df, "PRIMARY analysis dataset (data/processed/analysis_dataset_primary.parquet)", PRIMARY_PREDICTORS)

    secondary_cols = CARRY_COLUMNS + PRIMARY_PREDICTORS + SECONDARY_ONLY_PREDICTORS
    secondary_df = add_outcomes(master.loc[secondary_mask, secondary_cols])
    secondary_df.to_parquet(PROC_DIR / "analysis_dataset_secondary.parquet", index=False)
    summarize(secondary_df, "SECONDARY (fasting-extended) analysis dataset (data/processed/analysis_dataset_secondary.parquet)",
              PRIMARY_PREDICTORS + SECONDARY_ONLY_PREDICTORS)

    # Sanity: secondary must be a strict subset of primary by SEQN
    assert set(secondary_df["SEQN"]) <= set(primary_df["SEQN"]), "Secondary dataset must be nested within primary!"
    print(f"\n  Verified: secondary dataset ({len(secondary_df)}) is a strict subset of primary ({len(primary_df)}) by SEQN.")
    print("[ANALYSIS DATASET GENERATION COMPLETE]")

if __name__ == "__main__":
    main()
