"""
phase3_21_reserve_conformal_calibration_split.py
Phase 3 Closure Verification, Item 2 - Reserve the conformal calibration partition
required by the frozen documentation/phase2/uncertainty_protocol.md ("Split Conformal
Prediction"), which explicitly deferred the exact proportion to "Phase 3" but was
never actually carved out during Phase 3 execution (baseline-discrimination scope
only). This script closes that gap NOW, before any conformal prediction code runs,
per Option A (held-out calibration split) -- the protocol-consistent choice, since
Phase 2 named "Split Conformal Prediction" specifically, not the CV+ variant.

Split: within the existing 70% training partition (N=5,007) ONLY. The locked test
set (N=2,146) is never touched. 80% proper-train / 20% calibration, stratified on
the primary outcome, same fixed seed=42.

Produces:
  data/processed/splits/proper_train_ids.csv
  data/processed/splits/conformal_calibration_ids.csv
"""
import os, sys
import pandas as pd
from sklearn.model_selection import train_test_split
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import PROC_DIR, SPLIT_DIR, NOW, RANDOM_SEED, PRIMARY_OUTCOME_COL

CALIBRATION_FRACTION = 0.20  # matches the "e.g. 80/20" example explicitly named in uncertainty_protocol.md

def main():
    print("=== Reserve Conformal Calibration Split (Closure Verification Item 2) ===")
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
    test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
    train_df = df[df["SEQN"].isin(train_ids)].reset_index(drop=True)
    assert len(train_df) == 5007, f"Training partition size changed unexpectedly: {len(train_df)}"

    proper_train_df, calib_df = train_test_split(
        train_df, test_size=CALIBRATION_FRACTION, stratify=train_df[PRIMARY_OUTCOME_COL],
        random_state=RANDOM_SEED, shuffle=True)

    proper_train_df[["SEQN"]].to_csv(SPLIT_DIR / "proper_train_ids.csv", index=False)
    calib_df[["SEQN"]].to_csv(SPLIT_DIR / "conformal_calibration_ids.csv", index=False)

    # Integrity checks
    proper_ids = set(proper_train_df["SEQN"])
    calib_ids = set(calib_df["SEQN"])
    assert len(proper_ids & calib_ids) == 0, "proper-train and calibration overlap!"
    assert (proper_ids | calib_ids) == train_ids, "union does not equal the original training partition!"
    assert len(proper_ids & test_ids) == 0 and len(calib_ids & test_ids) == 0, "LEAKAGE: overlap with locked test set!"

    calib_pos = int(calib_df[PRIMARY_OUTCOME_COL].sum())
    proper_pos = int(proper_train_df[PRIMARY_OUTCOME_COL].sum())
    print(f"  Proper-train: N={len(proper_train_df)}, positive={proper_pos} ({round(100*proper_pos/len(proper_train_df),2)}%)")
    print(f"  Conformal calibration: N={len(calib_df)}, positive={calib_pos} ({round(100*calib_pos/len(calib_df),2)}%)")
    print(f"  Disjoint from locked test set (N=2,146): CONFIRMED")
    print(f"  Disjoint from each other, union == original training partition: CONFIRMED")
    print(f"  Seed: {RANDOM_SEED}")
    print("[CONFORMAL CALIBRATION SPLIT RESERVED]")

if __name__ == "__main__":
    main()
