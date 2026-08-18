"""
04_merge_nhanes.py  –  Phase 1 Steps 10–12
Merge P_LUX, P_DEMO, P_BMX (and any lab files present) on SEQN.
Verify integrity at each step. Record transformation log.

Outputs:
  documentation/audit_reports/merge_audit.csv
  documentation/audit_reports/transformation_log.md
  data/interim/nhanes_master_phase1.parquet
"""

import datetime, warnings, csv
import pandas as pd
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT    = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "NHANES_2017_2020"
AUD_DIR = ROOT / "documentation" / "audit_reports"
INT_DIR = ROOT / "data" / "interim"
AUD_DIR.mkdir(parents=True, exist_ok=True)
INT_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TLOG = []  # transformation log

def log(var, orig, transform, reason, result):
    TLOG.append(dict(variable=var, original=orig, transformation=transform,
                     reason=reason, result=result, timestamp=NOW))

def load(fname):
    p = RAW_DIR / fname
    df = pd.read_sas(p, format="xport", encoding="utf-8")
    # Ensure SEQN is integer for reliable merging
    if "SEQN" in df.columns:
        df["SEQN"] = pd.to_numeric(df["SEQN"], errors="coerce").astype("Int64")
        log("SEQN", "float64 (SAS)", "convert to Int64", "Reliable integer key for merging", "Int64")
    print(f"  Loaded {fname}: {df.shape}")
    return df

def audit_seqn(df, name):
    rows = len(df)
    uniq = int(df["SEQN"].nunique())
    miss = int(df["SEQN"].isna().sum())
    dups = rows - uniq
    print(f"  {name}: {rows} rows | {uniq} unique SEQN | {miss} missing | {dups} duplicates")
    return dict(dataset=name, rows=rows, unique_seqn=uniq, missing_seqn=miss, duplicate_seqn=dups)

merge_audit = []

# ── Load ──────────────────────────────────────────────────────────────────────
print("=== Loading files ===")
lux  = load("P_LUX.xpt")
demo = load("P_DEMO.xpt")
bmx  = load("P_BMX.xpt")

# Load any lab files
lab_files = [p for p in sorted(RAW_DIR.glob("*.xpt"))
             if p.name not in ("P_LUX.xpt","P_DEMO.xpt","P_BMX.xpt")]
lab_dfs = {}
for lp in lab_files:
    ldf = pd.read_sas(lp, format="xport", encoding="utf-8")
    if "SEQN" in ldf.columns:
        ldf["SEQN"] = pd.to_numeric(ldf["SEQN"], errors="coerce").astype("Int64")
    lab_dfs[lp.name] = ldf
    print(f"  Loaded lab: {lp.name}: {ldf.shape}")

# ── SEQN audits ───────────────────────────────────────────────────────────────
print("\n=== SEQN Linkage Audit ===")
merge_audit.append(audit_seqn(lux,  "P_LUX"))
merge_audit.append(audit_seqn(demo, "P_DEMO"))
merge_audit.append(audit_seqn(bmx,  "P_BMX"))
for name, ldf in lab_dfs.items():
    merge_audit.append(audit_seqn(ldf, name))

# ── Check for duplicates – STOP if found ─────────────────────────────────────
for name, df in [("P_LUX",lux),("P_DEMO",demo),("P_BMX",bmx)]:
    dups = df[df.duplicated("SEQN", keep=False)]
    if len(dups) > 0:
        print(f"\nSTOP: {name} contains {len(dups)} rows with duplicate SEQN values!")
        print(f"  Duplicated SEQNs: {dups['SEQN'].unique()[:10]}")
        print("  Investigate before proceeding. Aborting merge.")
        raise SystemExit(1)
    else:
        print(f"  {name}: No duplicate SEQN – OK")

# ── Merge sequence: LUX → DEMO → BMX → labs ──────────────────────────────────
print("\n=== Merging ===")
n_before = len(lux)
print(f"  Starting with P_LUX: {n_before} rows")

# Merge DEMO
master = lux.merge(demo, on="SEQN", how="left", suffixes=("","_DEMO"))
n_after = len(master)
matched = master["RIDAGEYR"].notna().sum() if "RIDAGEYR" in master.columns else None
print(f"  After merging DEMO: {n_after} rows | Demo vars matched: {matched}")
assert n_after == n_before, f"Row multiplication during DEMO merge! {n_before} → {n_after}"
merge_audit.append({"dataset":"MERGE: LUX+DEMO", "rows":n_after,
                    "unique_seqn":master["SEQN"].nunique(),
                    "missing_seqn":0,"duplicate_seqn":n_after-master["SEQN"].nunique()})

# Merge BMX
master = master.merge(bmx, on="SEQN", how="left", suffixes=("","_BMX"))
n_after = len(master)
print(f"  After merging BMX: {n_after} rows")
assert n_after == n_before, f"Row multiplication during BMX merge! {n_before} → {n_after}"
merge_audit.append({"dataset":"MERGE: LUX+DEMO+BMX", "rows":n_after,
                    "unique_seqn":master["SEQN"].nunique(),
                    "missing_seqn":0,"duplicate_seqn":n_after-master["SEQN"].nunique()})

# Merge lab files
for lname, ldf in lab_dfs.items():
    master = master.merge(ldf, on="SEQN", how="left", suffixes=("","_"+lname[:4]))
    n_after = len(master)
    print(f"  After merging {lname}: {n_after} rows")
    assert n_after == n_before, f"Row multiplication during {lname} merge!"
    merge_audit.append({"dataset":f"MERGE+{lname}", "rows":n_after,
                        "unique_seqn":master["SEQN"].nunique(),
                        "missing_seqn":0,"duplicate_seqn":0})

print(f"\n  Final master shape: {master.shape}")
print(f"  One-row-per-SEQN verified: {master['SEQN'].nunique() == len(master)}")

# ── Save ──────────────────────────────────────────────────────────────────────
out_parquet = INT_DIR / "nhanes_master_phase1.parquet"
master.to_parquet(out_parquet, index=False)
out_csv = INT_DIR / "nhanes_master_phase1.csv"
master.to_csv(out_csv, index=False)
print(f"\n  → Saved: {out_parquet}")
print(f"  → Saved (CSV): {out_csv}")

# Merge audit CSV
pd.DataFrame(merge_audit).to_csv(AUD_DIR / "merge_audit.csv", index=False)
print(f"  → Saved: {AUD_DIR / 'merge_audit.csv'}")

# Transformation log
with open(AUD_DIR / "transformation_log.md","w") as f:
    f.write(f"# Transformation Log\n\n**Generated:** {NOW}\n\n")
    f.write("| Variable | Original | Transformation | Reason | Result | Timestamp |\n")
    f.write("|---|---|---|---|---|---|\n")
    for t in TLOG:
        f.write(f"| {t['variable']} | {t['original']} | {t['transformation']} | "
                f"{t['reason']} | {t['result']} | {t['timestamp']} |\n")
print(f"  → Saved: {AUD_DIR / 'transformation_log.md'}")
print("[STEP 4 (MERGE) COMPLETE]")
