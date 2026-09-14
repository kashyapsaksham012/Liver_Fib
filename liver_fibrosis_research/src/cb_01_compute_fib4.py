"""
cb_01_compute_fib4.py
Clinical-baseline addendum (post-freeze, requested explicitly -- see
documentation/manuscript/REVISION_PLAN.md, New Analysis Queue E1/E2). NOT part of the
frozen Phase 0-8 protocol; does not modify any frozen artifact, split file, or model.

Computes FIB-4 = (RIDAGEYR * LBXSASSI) / (LBXPLTSI * sqrt(LBXSATSI)) for every participant
in the frozen primary cohort (N=7,153), using the identical frozen dataset and predictor
columns already used for the five ML models. No new NHANES data pulled -- all four inputs
(age, AST, ALT, platelets) are already frozen predictors in analysis_dataset_primary.parquet.

Output: results/clinical_baselines/fib4_scores.csv (SEQN, fib4, + split membership flags)
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, PROC_DIR, SPLIT_DIR, PRIMARY_OUTCOME_COL, fail

OUT_DIR = ROOT / "results" / "clinical_baselines"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
if len(df) != 7153:
    fail(f"Primary dataset has {len(df)} rows, expected 7153")

required = ["RIDAGEYR", "LBXSASSI", "LBXSATSI", "LBXPLTSI"]
missing = [c for c in required if df[c].isna().any()]
if missing:
    fail(f"Unexpected missingness in FIB-4 inputs (should be zero in the complete-case frozen cohort): {missing}")

df["fib4"] = (df["RIDAGEYR"] * df["LBXSASSI"]) / (df["LBXPLTSI"] * np.sqrt(df["LBXSATSI"]))

if not np.isfinite(df["fib4"]).all():
    fail("Non-finite FIB-4 values produced -- check for zero/negative platelets or ALT")

train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
proper_train_ids = set(pd.read_csv(SPLIT_DIR / "proper_train_ids.csv")["SEQN"])
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])

# Every participant must fall in exactly one of {train, test}; proper_train + calibration must
# partition train exactly. This re-verifies split disjointness/coverage before reusing the
# frozen split files for a new analysis, rather than assuming.
if train_ids & test_ids:
    fail("train_ids and test_ids overlap -- CRITICAL")
if proper_train_ids | cal_ids != train_ids:
    fail("proper_train_ids + conformal_calibration_ids does not reconstruct train_ids exactly")
if proper_train_ids & cal_ids:
    fail("proper_train_ids and conformal_calibration_ids overlap -- CRITICAL")
if not (train_ids | test_ids) <= set(df["SEQN"]):
    fail("Split files reference SEQNs not present in the primary dataset")

out = df[["SEQN", "RIDAGEYR", "LBXSASSI", "LBXSATSI", "LBXPLTSI", "BMXBMI", "fib4",
          PRIMARY_OUTCOME_COL, "LUXSMED", "bmi_group_final", "age_group_final",
          "RIAGENDR", "RIDRETH3"]].copy()
out["split"] = np.select(
    [out["SEQN"].isin(proper_train_ids), out["SEQN"].isin(cal_ids), out["SEQN"].isin(test_ids)],
    ["proper_train", "conformal_calibration", "test"],
    default="UNASSIGNED",
)
if (out["split"] == "UNASSIGNED").any():
    fail("Some SEQNs did not receive a split assignment")

out.to_csv(OUT_DIR / "fib4_scores.csv", index=False)

print(f"FIB-4 computed for N={len(out)} (matches frozen primary cohort).")
print(out.groupby("split").size().to_string())
print(f"FIB-4 summary: min={out['fib4'].min():.3f}, median={out['fib4'].median():.3f}, "
      f"max={out['fib4'].max():.3f}")
print(f"Saved results/clinical_baselines/fib4_scores.csv")
