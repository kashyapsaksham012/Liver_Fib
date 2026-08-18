"""
01_data_inventory.py  –  Phase 1 Step 1
Inventory all raw NHANES files.

Outputs (relative to project root):
  documentation/audit_reports/raw_file_inventory.csv
  documentation/audit_reports/raw_file_inventory.md
"""

import os, sys, csv, hashlib, datetime
import pandas as pd
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent
RAW_DIR  = ROOT / "data" / "raw" / "NHANES_2017_2020"
AUDIT    = ROOT / "documentation" / "audit_reports"
AUDIT.mkdir(parents=True, exist_ok=True)

KNOWN = {
    "P_LUX.xpt":  ("2017-Mar2020 Pre-Pandemic", "Exam – Liver Elastography",    "Liver stiffness / CAP / quality"),
    "P_DEMO.xpt": ("2017-Mar2020 Pre-Pandemic", "Demographics",                  "Age/sex/race/weights"),
    "P_BMX.xpt":  ("2017-Mar2020 Pre-Pandemic", "Exam – Body Measures",          "Height/weight/BMI"),
}

def md5(p):
    h = hashlib.md5()
    with open(p,"rb") as f:
        for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
    return h.hexdigest()

def inspect(p):
    try:
        df = pd.read_sas(p, format="xport", encoding="utf-8")
        r,c = df.shape
        hs  = "SEQN" in df.columns
        if hs:
            u = int(df["SEQN"].nunique())
            m = int(df["SEQN"].isna().sum())
            d = int(r - u)
        else:
            u=m=d="N/A"
        return r,c,hs,u,m,d,None
    except Exception as e:
        return "ERR","ERR",False,"ERR","ERR","ERR",str(e)

records = []
files   = sorted(RAW_DIR.glob("*.xpt")) + sorted(RAW_DIR.glob("*.XPT"))
files   = list({p.name:p for p in files}.values())

if not files:
    print("ERROR: No XPT files found. Aborting.")
    sys.exit(1)

for p in files:
    fname  = p.name
    stat   = p.stat()
    kb     = stat.st_size/1024
    mtime  = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
    chk    = md5(p)
    cyc,comp,purp = KNOWN.get(fname, ("UNKNOWN","UNKNOWN","UNKNOWN"))
    r,c,hs,u,m,d,err = inspect(p)
    records.append(dict(
        filename=fname, size_kb=round(kb,1), file_modified=mtime,
        md5=chk, nhanes_cycle=cyc, component=comp, purpose=purp,
        rows=r, cols=c, has_seqn=hs,
        seqn_unique=u, seqn_missing=m, seqn_duplicates=d, error=err
    ))
    print(f"{fname}: {r} rows × {c} cols | SEQN unique={u} | dups={d}")

# CSV
csv_out = AUDIT / "raw_file_inventory.csv"
with open(csv_out,"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    w.writeheader(); w.writerows(records)

# Markdown
md_out = AUDIT / "raw_file_inventory.md"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(md_out,"w") as f:
    f.write(f"# Raw File Inventory\n\n**Generated:** {now}\n\n")
    f.write(f"**Files found:** {len(records)}\n\n---\n\n")
    for r in records:
        f.write(f"## {r['filename']}\n\n| Field | Value |\n|---|---|\n")
        for k,v in r.items():
            if k!="filename": f.write(f"| {k} | {v} |\n")
        f.write("\n")

print(f"\nSaved → {csv_out}")
print(f"Saved → {md_out}")
print("[STEP 1 COMPLETE]")
