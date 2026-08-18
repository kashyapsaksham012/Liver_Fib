"""
phase3_01_handoff_verification.py
Phase 3, Part 3 - Verify the Phase 2 primary analysis dataset exactly matches the
frozen specification, by independently recomputing the cohort/outcome from the
Phase 1 master dataset (bypassing the saved Phase 2 parquet entirely for this check).

Produces:
  documentation/phase3/phase2_handoff_verification.md
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (ROOT, DOC_DIR, PROC_DIR, NOW, PRIMARY_COHORT_N, PRIMARY_OUTCOME_COL,
                          PRIMARY_OUTCOME_POSITIVE_N, PRIMARY_PREDICTORS, FORBIDDEN_VARS, fail)
from _cohorts import compute_all

def main():
    print("=== Phase 3, Part 3: Phase 2 Handoff Verification ===")
    master = pd.read_parquet(ROOT / "data" / "interim" / "nhanes_master_phase1.parquet")
    primary = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")

    # Independent recomputation, bypassing the saved Phase 2 dataset
    c = compute_all(master)
    broad = ["LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
    mask = ((master["RIDAGEYR"] >= 18) & (master["LUAXSTAT"] == 1.0) &
            master[broad].notna().all(axis=1) & master["BMXBMI"].notna() & master["RIAGENDR"].notna())
    recomputed_n = int(mask.sum())
    recomputed_pos = int((master.loc[mask, "LUXSMED"] >= 8.2).sum())
    recomputed_seqn = set(master.loc[mask, "SEQN"].tolist())
    saved_seqn = set(primary["SEQN"].tolist())

    checks = []
    def rec(name, cond, detail):
        checks.append({"check": name, "status": "PASS" if cond else "FAIL", "detail": detail})
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}: {detail}")
        return cond

    ok = True
    ok &= rec("Recomputed N matches frozen spec", recomputed_n == PRIMARY_COHORT_N, f"recomputed={recomputed_n}, frozen={PRIMARY_COHORT_N}")
    ok &= rec("Saved dataset N matches frozen spec", len(primary) == PRIMARY_COHORT_N, f"saved={len(primary)}, frozen={PRIMARY_COHORT_N}")
    ok &= rec("Recomputed SEQN set == saved SEQN set", recomputed_seqn == saved_seqn, f"symmetric_diff={len(recomputed_seqn ^ saved_seqn)}")
    ok &= rec("Recomputed outcome-positive N matches frozen spec", recomputed_pos == PRIMARY_OUTCOME_POSITIVE_N,
              f"recomputed={recomputed_pos}, frozen={PRIMARY_OUTCOME_POSITIVE_N}")
    saved_pos = int(primary[PRIMARY_OUTCOME_COL].sum())
    ok &= rec("Saved dataset outcome-positive N matches frozen spec", saved_pos == PRIMARY_OUTCOME_POSITIVE_N, f"saved={saved_pos}")
    prevalence = round(100 * saved_pos / len(primary), 2)
    ok &= rec("Prevalence matches frozen ~9.31%", abs(prevalence - 9.31) < 0.01, f"prevalence={prevalence}%")
    ok &= rec("All 10 frozen predictors present in saved dataset", set(PRIMARY_PREDICTORS).issubset(set(primary.columns)),
              f"missing={set(PRIMARY_PREDICTORS) - set(primary.columns)}")
    ok &= rec("No forbidden variable present as a column named identically to a predictor",
              len(set(FORBIDDEN_VARS) & set(PRIMARY_PREDICTORS)) == 0, "structural check: forbidden/predictor lists disjoint")
    ok &= rec("No missing values in the 10 predictors (complete-case, as frozen)", primary[PRIMARY_PREDICTORS].isna().sum().sum() == 0,
              f"missing_cells={primary[PRIMARY_PREDICTORS].isna().sum().sum()}")
    ok &= rec("No duplicate SEQN in saved dataset", primary["SEQN"].duplicated().sum() == 0, f"dups={primary['SEQN'].duplicated().sum()}")
    demo_present = all(c in primary.columns for c in ["RIDRETH1", "RIDRETH3"])
    ok &= rec("Fairness-stratification demographic columns retained (RIDRETH1/RIDRETH3)", demo_present, f"present={demo_present}")

    with open(DOC_DIR / "phase2_handoff_verification.md", "w") as f:
        f.write(f"# Phase 2 -> Phase 3 Handoff Verification\n\n**Generated:** {NOW}\n\n")
        f.write("Every check below independently recomputes its target from the Phase 1 master dataset, "
                "bypassing the saved Phase 2 parquet, then compares against both the frozen protocol spec "
                "and the saved dataset.\n\n")
        f.write("| Check | Status | Detail |\n|---|---|---|\n")
        for c_ in checks:
            f.write(f"| {c_['check']} | {c_['status']} | {c_['detail']} |\n")
        f.write(f"\n**Overall: {'PASSED' if ok else 'FAILED'}**\n")

    if not ok:
        fail("Phase 2 handoff verification FAILED -- see documentation/phase3/phase2_handoff_verification.md. "
             "Do NOT silently repair Phase 2; halt and report.")
    print("  Saved phase2_handoff_verification.md. Handoff verification PASSED.")
    print("[HANDOFF VERIFICATION COMPLETE]")

if __name__ == "__main__":
    main()
