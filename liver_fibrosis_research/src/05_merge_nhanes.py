"""
05_merge_nhanes.py
Phase 1 Remediation - Participant-level Merging and Integrity Verification (sentinel-corrected).
Integrates P_LUX, P_DEMO, P_BMX, P_BIOPRO, P_CBC, P_GLU, P_TRIGLY, P_HDL sequentially on SEQN.

Produces:
  documentation/audit_reports/seqn_linkage_audit.csv   (NEW - Error/Deliverable requirement)
  documentation/audit_reports/merge_audit.csv
  documentation/audit_reports/transformation_log.md
  documentation/audit_reports/special_missing_code_audit.csv (sentinel-fix log, cohort-wide)
  data/interim/nhanes_master_phase1.parquet
  data/interim/nhanes_master_phase1.csv
"""

import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import (ROOT, AUDIT_DIR, INT_DIR, REQUIRED_FILES, NOW, load_xpt,
                      get_sentinel_log, fail)

TLOG = []

def log_transformation(var, orig, transform, reason, result):
    TLOG.append({"variable": var, "original": orig, "transformation": transform,
                 "reason": reason, "result": result, "timestamp": NOW})

def main():
    print("=== Step 10, 12 & 16: SEQN Linkage Audit + Merge All NHANES Datasets (Remediated) ===")

    dfs = {}
    for name in REQUIRED_FILES:
        print(f"Loading {name} for merge (sentinel-corrected)...")
        dfs[name] = load_xpt(name)
    log_transformation("ALL::numeric columns", "raw SAS xport (may contain unconverted special-missing sentinel 5.397605346934028e-79)",
                        "recode SAS special-missing sentinel to NaN", "Prevent silent corruption of min/mean/missingness statistics",
                        "sentinel recoded to NaN; see special_missing_code_audit.csv for exact scope")
    for name in REQUIRED_FILES:
        log_transformation(f"{name}::SEQN", "float64 (SAS)", "convert to Int64", "Ensure integer key consistency", "Int64")

    # ── SEQN Linkage Audit (per-file, pre-merge) ────────────────────────────
    lux_seqns = set(dfs[REQUIRED_FILES[0]]["SEQN"].dropna())
    linkage_rows = []
    for name, df in dfs.items():
        dups = df[df.duplicated("SEQN", keep=False)]
        if len(dups) > 0:
            fail(f"Dataset {name} has {len(dups)} duplicate SEQN values!")
        seqns = set(df["SEQN"].dropna())
        matched = len(seqns & lux_seqns)
        unmatched_in_lux = len(lux_seqns - seqns)
        extra_not_in_lux = len(seqns - lux_seqns)
        linkage_rows.append({
            "dataset": name, "n_rows": len(df), "n_unique_seqn": df["SEQN"].nunique(),
            "n_missing_seqn": int(df["SEQN"].isna().sum()), "n_duplicate_seqn": int(len(df) - df["SEQN"].nunique()),
            "matched_to_lux_cohort": matched, "lux_participants_missing_from_this_file": unmatched_in_lux,
            "rows_in_this_file_outside_lux_cohort": extra_not_in_lux,
            "pct_of_lux_cohort_matched": round(100*matched/len(lux_seqns), 2) if lux_seqns else 0.0
        })
    pd.DataFrame(linkage_rows).to_csv(AUDIT_DIR / "seqn_linkage_audit.csv", index=False)
    print("  Saved seqn_linkage_audit.csv.")

    merge_audit = []
    master_name = REQUIRED_FILES[0]
    master = dfs[master_name].copy()
    n_start = len(master)
    print(f"Starting cohort master with {master_name}: N={n_start} rows")
    merge_audit.append({"dataset": master_name, "rows_before": n_start, "rows_after": n_start,
                        "matched_seqn": n_start, "unmatched_seqn": 0, "row_multiplication": "None",
                        "description": "Baseline transient elastography population (root cohort denominator)"})

    for name in REQUIRED_FILES[1:]:
        df_to_merge = dfs[name]
        n_before = len(master)
        master = master.merge(df_to_merge, on="SEQN", how="left", suffixes=("", f"_{name[:4]}"))
        n_after = len(master)
        if n_after != n_before:
            fail(f"Row multiplication detected when merging {name}! {n_before} -> {n_after}")
        matched = master["SEQN"].isin(df_to_merge["SEQN"]).sum()
        unmatched = n_before - matched
        merge_audit.append({"dataset": name, "rows_before": n_before, "rows_after": n_after,
                            "matched_seqn": int(matched), "unmatched_seqn": int(unmatched),
                            "row_multiplication": "No" if n_before == n_after else "Yes",
                            "description": "Left merge on SEQN" + (" [FASTING SUBSAMPLE FILE]" if name in ("P_GLU.xpt", "P_TRIGLY.xpt") else "")})
        print(f"  Merged {name}: N={n_after} | Matched={matched} | Unmatched={unmatched}")

    assert master["SEQN"].nunique() == len(master), "Participant level uniqueness violation!"
    print("One-row-per-participant uniqueness verified (TEST 5 / TEST 6).")

    out_parquet = INT_DIR / "nhanes_master_phase1.parquet"
    out_csv = INT_DIR / "nhanes_master_phase1.csv"
    master.to_parquet(out_parquet, index=False)
    master.to_csv(out_csv, index=False)
    print(f"Saved merged master dataset to {out_parquet} and {out_csv}")

    pd.DataFrame(merge_audit).to_csv(AUDIT_DIR / "merge_audit.csv", index=False)

    with open(AUDIT_DIR / "transformation_log.md", "w") as f:
        f.write(f"# Transformation Log\n\n**Generated:** {NOW}\n\n")
        f.write("| Variable | Original | Transformation | Reason | Result | Timestamp |\n")
        f.write("|---|---|---|---|---|---|\n")
        for t in TLOG:
            f.write(f"| {t['variable']} | {t['original']} | {t['transformation']} | {t['reason']} | {t['result']} | {t['timestamp']} |\n")

    # Persist the module-level sentinel-fix log accumulated across every load_xpt() call so far
    sentinel_log = get_sentinel_log()
    sentinel_log.to_csv(AUDIT_DIR / "special_missing_code_audit_raw_scan.csv", index=False)
    print(f"  Sentinel-correction log: {len(sentinel_log)} (file,column) pairs touched, "
          f"{int(sentinel_log['n_sentinel_recoded_to_nan'].sum()) if len(sentinel_log) else 0} cells recoded "
          f"across all loads performed in this run (see 10_special_missing_code_audit.py for the authoritative, full-scope audit).")

    print("[STEP 10, 12 & 16 COMPLETE]")

if __name__ == "__main__":
    main()
