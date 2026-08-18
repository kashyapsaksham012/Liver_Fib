"""
phase3_11_split_and_cv_design_audit.py
Phase 3 Remediation, Parts 3C/3D - Audit the 70/30 split (demographic composition in
full/train/test, descriptive only -- not altered for subgroup balance since Phase 2
did not require it), and formally clarify the CV-vs-"validation" terminology so no
future reader mistakes this for a classic three-way split.

Produces:
  documentation/phase3/cv_validation_design.md
  results/tables/phase3_split_demographic_audit.csv
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import PROC_DIR, SPLIT_DIR, DOC_DIR, TAB_DIR, NOW, RANDOM_SEED, PRIMARY_OUTCOME_COL
from _common import RACE_MAP_RIDRETH3, SEX_MAP

def describe(df, label):
    n = len(df)
    row = {"partition": label, "n": n, "outcome_prevalence_pct": round(100*df[PRIMARY_OUTCOME_COL].mean(), 2)}
    for code, lbl in SEX_MAP.items():
        row[f"pct_{lbl}"] = round(100*(df["RIAGENDR"] == code).mean(), 2)
    for code, lbl in RACE_MAP_RIDRETH3.items():
        row[f"pct_{lbl.replace(' ','_').replace('/','_')}"] = round(100*(df["RIDRETH3"] == code).mean(), 2)
    row["median_age"] = round(df["RIDAGEYR"].median(), 1)
    row["median_bmi"] = round(df["BMXBMI"].median(), 1)
    return row

def main():
    print("=== Phase 3 Remediation, Parts 3C/3D: Split Demographic Audit & CV-Design Clarification ===")
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
    test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
    train_df, test_df = df[df["SEQN"].isin(train_ids)], df[df["SEQN"].isin(test_ids)]

    assert len(train_df) == 5007, f"Train N changed! {len(train_df)}"
    assert len(test_df) == 2146, f"Test N changed! {len(test_df)}"
    assert len(train_ids & test_ids) == 0, "Train/test overlap detected!"
    assert len(train_ids | test_ids) == len(df), "Split does not cover full cohort!"

    rows = [describe(df, "Full cohort (N=7,153)"), describe(train_df, "Train (N=5,007)"), describe(test_df, "Test (N=2,146, LOCKED)")]
    out = pd.DataFrame(rows)
    out.to_csv(TAB_DIR / "phase3_split_demographic_audit.csv", index=False)
    print(f"  Prevalence: full={rows[0]['outcome_prevalence_pct']}%, train={rows[1]['outcome_prevalence_pct']}%, test={rows[2]['outcome_prevalence_pct']}%")
    print("  Demographic composition is descriptive only -- split was NOT altered for subgroup balance "
          "(Phase 2 did not require stratification beyond the primary outcome).")

    with open(DOC_DIR / "cv_validation_design.md", "w") as f:
        f.write(f"# CV-Based Development Design (Clarification, Not a Three-Way Split)\n\n**Generated:** {NOW}\n\n")
        f.write("## Explicit clarification\n\n")
        f.write("This project's frozen `documentation/phase2/model_development_protocol.md` specifies: "
                "*\"5-fold stratified cross-validation within the training set only, for hyperparameter "
                "tuning and model selection\"* -- it does NOT specify a separate, fixed, disjoint validation "
                "partition distinct from the 70% training set and the 30% locked test set.\n\n")
        f.write("**`data/processed/splits/validation_ids.csv` MUST NOT be read as an independent validation "
                "cohort.** It is byte-identical to `train_ids.csv` by construction. It exists only because "
                "the generic Phase 3 deliverable template requested a `validation_ids.csv` file; its actual "
                "content and purpose are:\n\n")
        f.write("> **`validation_ids.csv` = the CV-development partition. Every participant in it serves as "
                "held-out (out-of-fold) validation data exactly once across the 5 stratified CV folds during "
                "hyperparameter search. There is no participant held out from training as a separate, "
                "disjoint validation set.**\n\n")
        f.write("## Correct terminology for downstream use\n\n")
        f.write("| Term | What it means in THIS project | What it does NOT mean |\n|---|---|---|\n")
        f.write("| \"Training partition\" | The 70% (N=5,007) used for both model fitting and CV | — |\n")
        f.write("| \"Validation predictions\" (`results/predictions/validation_predictions_<model>.csv`) | "
                "Out-of-fold predictions from 5-fold CV, computed WITHIN the training partition | NOT predictions on a separate held-out set never used in any fold's training |\n")
        f.write("| \"Test set\" | The locked 30% (N=2,146), touched exactly once for final evaluation | — |\n\n")
        f.write("## Why this matters (per remediation Part 3D)\n\n")
        f.write("A future researcher reading only `validation_ids.csv`/`train_ids.csv` filenames could "
                "reasonably assume a classic train/validation/test three-way split was used, which would "
                "misrepresent this project's actual (valid, frozen) CV-based development design. This "
                "document exists specifically to prevent that misreading. No data or code was changed by "
                "this clarification -- it is a documentation fix, not a methodological amendment.\n\n")
        f.write("## Split integrity (re-confirmed)\n\n")
        f.write(f"- Train N=5,007, Test N=2,146 (sum=7,153, matches full cohort exactly)\n")
        f.write(f"- Train/test overlap: 0\n- Split seed: {RANDOM_SEED}\n\n")
        f.write("## Demographic composition (descriptive only, not used to alter the split)\n\n")
        f.write(out[["partition", "n", "outcome_prevalence_pct", "pct_Male", "pct_Female", "median_age", "median_bmi"]].to_markdown(index=False) + "\n")
    print("  Saved cv_validation_design.md and phase3_split_demographic_audit.csv.")
    print("[SPLIT & CV-DESIGN AUDIT COMPLETE]")

if __name__ == "__main__":
    main()
