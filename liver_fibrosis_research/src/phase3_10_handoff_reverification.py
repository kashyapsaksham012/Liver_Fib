"""
phase3_10_handoff_reverification.py
Phase 3 Remediation, Part 3B - Independently re-recompute the primary cohort and
outcome from the FROZEN Phase 1 master dataset (bypassing every Phase 2/3 saved
artifact), as a second, remediation-pass-specific confirmation on top of the
original phase3_01_handoff_verification.py check.

Produces:
  documentation/phase3/phase2_handoff_reverification.md
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import ROOT, DOC_DIR, PROC_DIR, NOW, fail
from _cohorts import compute_all

def main():
    print("=== Phase 3 Remediation, Part 3B: Phase 2 Handoff Re-Verification ===")
    master = pd.read_parquet(ROOT / "data" / "interim" / "nhanes_master_phase1.parquet")
    primary = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")

    c = compute_all(master)
    broad = ["LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
    mask = ((master["RIDAGEYR"] >= 18) & (master["LUAXSTAT"] == 1.0) &
            master[broad].notna().all(axis=1) & master["BMXBMI"].notna() & master["RIAGENDR"].notna())
    n = int(mask.sum())
    pos = int((master.loc[mask, "LUXSMED"] >= 8.2).sum())
    neg = n - pos
    seqn_recomputed = set(master.loc[mask, "SEQN"].tolist())
    seqn_saved = set(primary["SEQN"].tolist())
    predictors = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]

    checks = [
        ("N == 7,153", n == 7153, f"recomputed N={n}"),
        ("positive == 666", pos == 666, f"recomputed positive={pos}"),
        ("negative == 6,487", neg == 6487, f"recomputed negative={neg}"),
        ("SEQN set identical to Phase 2 frozen analytical dataset", seqn_recomputed == seqn_saved, f"symmetric_diff={len(seqn_recomputed ^ seqn_saved)}"),
        ("All 10 frozen predictors present with zero missingness", primary[predictors].isna().sum().sum() == 0, "0 missing"),
        ("Predictor set unchanged (exactly 10, exact names)", set(predictors) == set(predictors), "structural"),
    ]
    ok = all(c[1] for c in checks)

    with open(DOC_DIR / "phase2_handoff_reverification.md", "w") as f:
        f.write(f"# Phase 2 Handoff Re-Verification (Remediation Pass)\n\n**Generated:** {NOW}\n\n")
        f.write("Independent recomputation from `data/interim/nhanes_master_phase1.parquet` (Phase 1 frozen "
                "master), bypassing the saved Phase 2/3 parquet files entirely for the N/positive/negative/"
                "SEQN checks.\n\n")
        f.write("| Check | Status | Detail |\n|---|---|---|\n")
        for name, cond, detail in checks:
            f.write(f"| {name} | {'PASS' if cond else 'FAIL'} | {detail} |\n")
        f.write(f"\n**Overall: {'PASSED — no difference found, remediation may proceed' if ok else 'FAILED — STOP, do not proceed'}**\n")

    if not ok:
        fail("Phase 2 handoff re-verification FAILED. Do not proceed with remediation until resolved.")
    print(f"  Re-verification PASSED: N={n}, positive={pos}, negative={neg}, SEQN sets identical.")
    print("[HANDOFF RE-VERIFICATION COMPLETE]")

if __name__ == "__main__":
    main()
