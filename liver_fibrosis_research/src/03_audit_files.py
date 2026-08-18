"""
03_audit_files.py  –  Phase 1 Steps 5–9
Dedicated audit of P_LUX, P_DEMO, P_BMX. Produces per-file audit reports.

Outputs:
  documentation/audit_reports/P_LUX_audit_report.md
  documentation/audit_reports/P_DEMO_audit_report.md
  documentation/audit_reports/P_BMX_audit_report.md
  documentation/audit_reports/laboratory_audit_report.md
  documentation/audit_reports/laboratory_inventory.csv
"""

import datetime, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT     = Path(__file__).resolve().parent.parent
RAW_DIR  = ROOT / "data" / "raw" / "NHANES_2017_2020"
AUD_DIR  = ROOT / "documentation" / "audit_reports"
FIG_DIR  = ROOT / "results" / "figures"
AUD_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load(fname):
    p = RAW_DIR / fname
    df = pd.read_sas(p, format="xport", encoding="utf-8")
    print(f"  Loaded {fname}: {df.shape}")
    return df

def miss_table(df, cols=None):
    cols = cols or df.columns.tolist()
    rows = []
    for c in cols:
        n = len(df)
        nm = int(df[c].isna().sum())
        rows.append({"variable": c, "n_obs": n-nm, "n_missing": nm,
                     "pct_missing": round(100*nm/n,2)})
    return pd.DataFrame(rows)

def num_stats(s):
    d = s.describe()
    return (f"N={int(d['count'])} | min={d['min']:.3f} | "
            f"p25={d['25%']:.3f} | median={d['50%']:.3f} | "
            f"p75={d['75%']:.3f} | max={d['max']:.3f} | "
            f"mean={d['mean']:.3f} | std={d['std']:.3f}")

# ──────────────────────────────────────────────────────────────────────────────
# P_LUX audit
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== Auditing P_LUX ===")
lux = load("P_LUX.xpt")
lux_cols = lux.columns.tolist()

# Identify stiffness, CAP, quality columns
stiff_cols = [c for c in lux_cols if "LSM" in c or "LUXS" in c or "LUX" in c]
cap_cols   = [c for c in lux_cols if "CAP" in c or "CAP" in c.upper()]
qual_cols  = [c for c in lux_cols if any(x in c for x in ["IQR","IQRM","STATUS","STAT","PASS","QUAL","VALID","FLAG","EXAM"])]

# Distribution plot of liver stiffness if found
stiff_var = None
for candidate in ["LUXSMED","LUXS010","LUXS020","LUXS030"]:
    if candidate in lux.columns:
        stiff_var = candidate; break
if not stiff_var:
    # try any numeric LUX col that looks like stiffness
    for c in lux.columns:
        if "LUX" in c and pd.api.types.is_numeric_dtype(lux[c]):
            stiff_var = c; break

cap_var = None
for candidate in ["LUXCAPM","LUXCAP"]:
    if candidate in lux.columns:
        cap_var = candidate; break

print(f"  Stiffness candidate variable: {stiff_var}")
print(f"  CAP candidate variable: {cap_var}")
print(f"  All columns: {lux_cols}")

if stiff_var:
    fig, axes = plt.subplots(1,2, figsize=(12,4))
    sv = lux[stiff_var].dropna()
    axes[0].hist(sv, bins=60, color="#2196F3", edgecolor="white")
    axes[0].set_title(f"Liver Stiffness ({stiff_var})")
    axes[0].set_xlabel("kPa"); axes[0].set_ylabel("Count")
    axes[1].hist(np.log1p(sv), bins=60, color="#4CAF50", edgecolor="white")
    axes[1].set_title(f"log1p({stiff_var})")
    axes[1].set_xlabel("log1p(kPa)"); axes[1].set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "P_LUX_stiffness_distribution.png", dpi=150)
    plt.close()
    print(f"  → Saved stiffness distribution plot")

mt_lux = miss_table(lux)

with open(AUD_DIR / "P_LUX_audit_report.md","w") as f:
    f.write(f"# P_LUX Audit Report\n\n**Generated:** {NOW}\n\n")
    f.write(f"## Shape\n\n- Rows: {lux.shape[0]}\n- Columns: {lux.shape[1]}\n\n")
    f.write("## All Columns\n\n```\n" + "\n".join(lux_cols) + "\n```\n\n")
    f.write(f"## SEQN Check\n\n")
    f.write(f"- SEQN present: {'SEQN' in lux.columns}\n")
    if "SEQN" in lux.columns:
        f.write(f"- Unique SEQN: {lux['SEQN'].nunique()}\n")
        f.write(f"- Missing SEQN: {lux['SEQN'].isna().sum()}\n")
        f.write(f"- Duplicate SEQN: {lux.shape[0]-lux['SEQN'].nunique()}\n\n")
    f.write(f"## Candidate Outcome Variables\n\n")
    f.write(f"- Stiffness variable identified: `{stiff_var}`\n")
    f.write(f"- CAP variable identified: `{cap_var}`\n\n")
    if stiff_var:
        sv = lux[stiff_var].dropna()
        f.write(f"### {stiff_var} Distribution\n\n")
        f.write(f"- Valid (non-missing): {len(sv)}\n")
        f.write(f"- Missing: {lux[stiff_var].isna().sum()}\n")
        f.write(f"- Stats: {num_stats(lux[stiff_var].dropna())}\n\n")
        # Candidate thresholds
        for thr in [7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 12.0]:
            pos = int((sv >= thr).sum())
            pct = round(100*pos/len(sv),1) if len(sv)>0 else 0
            f.write(f"- At threshold {thr} kPa: {pos} positive ({pct}%)\n")
        f.write("\n> NOTE: Threshold selection is deferred to Phase 2. "
                "Do not select threshold based on class balance.\n\n")
    if cap_var:
        cv = lux[cap_var].dropna()
        f.write(f"### {cap_var} (CAP) Distribution\n\n")
        f.write(f"- Valid: {len(cv)} | Missing: {lux[cap_var].isna().sum()}\n")
        f.write(f"- Stats: {num_stats(cv)}\n\n")
    f.write("## Quality / Status Variables\n\n")
    for c in qual_cols:
        vc = lux[c].value_counts(dropna=False).to_dict()
        f.write(f"- `{c}`: {vc}\n")
    f.write("\n## Missingness Table\n\n")
    f.write(mt_lux.to_markdown(index=False))
    f.write("\n")
print("  → Saved P_LUX_audit_report.md")

# ──────────────────────────────────────────────────────────────────────────────
# P_DEMO audit
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== Auditing P_DEMO ===")
demo = load("P_DEMO.xpt")
demo_cols = demo.columns.tolist()

age_var  = next((c for c in demo.columns if "RIDAGE" in c), None)
sex_var  = next((c for c in demo.columns if "GENDER" in c or "RIAGENDR" in c), None)
race_var = next((c for c in demo.columns if "RIDRETH" in c), None)
wt_vars  = [c for c in demo.columns if c.startswith("WT") and "MEC" in c or c.startswith("WT") and "INT" in c]
sv_vars  = [c for c in demo.columns if "SDMV" in c]

print(f"  Age var: {age_var} | Sex var: {sex_var} | Race var: {race_var}")
print(f"  Weight vars: {wt_vars} | Survey design: {sv_vars}")

mt_demo = miss_table(demo)

with open(AUD_DIR / "P_DEMO_audit_report.md","w") as f:
    f.write(f"# P_DEMO Audit Report\n\n**Generated:** {NOW}\n\n")
    f.write(f"## Shape\n\n- Rows: {demo.shape[0]}\n- Columns: {demo.shape[1]}\n\n")
    f.write("## All Columns\n\n```\n" + "\n".join(demo_cols) + "\n```\n\n")
    f.write("## SEQN Check\n\n")
    if "SEQN" in demo.columns:
        f.write(f"- Unique SEQN: {demo['SEQN'].nunique()}\n")
        f.write(f"- Missing SEQN: {demo['SEQN'].isna().sum()}\n\n")
    f.write("## Key Demographic Variables\n\n")
    for var, label in [(age_var,"Age"), (sex_var,"Sex"), (race_var,"Race/Ethnicity")]:
        if var:
            f.write(f"### {label} (`{var}`)\n\n")
            vc = demo[var].value_counts(dropna=False)
            f.write(vc.to_markdown() + "\n\n")
            if pd.api.types.is_numeric_dtype(demo[var]):
                f.write(f"Stats: {num_stats(demo[var].dropna())}\n\n")
    f.write("## Survey Weight Variables\n\n")
    for v in wt_vars:
        f.write(f"- `{v}`: {num_stats(demo[v].dropna())}\n")
    f.write("\n## Survey Design Variables\n\n")
    for v in sv_vars:
        vc = demo[v].value_counts(dropna=False).to_dict()
        f.write(f"- `{v}`: {vc}\n")
    f.write("\n## Missingness Table\n\n")
    f.write(mt_demo.to_markdown(index=False))
    f.write("\n\n> NOTE: Race/ethnicity groupings and age group bins are NOT finalized here. "
            "Collapsing decisions belong to Phase 2 analysis planning.\n")
print("  → Saved P_DEMO_audit_report.md")

# ──────────────────────────────────────────────────────────────────────────────
# P_BMX audit
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== Auditing P_BMX ===")
bmx = load("P_BMX.xpt")
bmx_cols = bmx.columns.tolist()

bmi_var = next((c for c in bmx.columns if "BMI" in c and "BMXBMI" == c), None) or \
          next((c for c in bmx.columns if "BMI" in c), None)
ht_var  = next((c for c in bmx.columns if "HT" in c and "BMXHT" == c), None) or \
          next((c for c in bmx.columns if "HT" in c and "BMX" in c), None)
wt_var2 = next((c for c in bmx.columns if "WT" in c and "BMXWT" == c), None) or \
          next((c for c in bmx.columns if "WT" in c and "BMX" in c), None)

print(f"  BMI: {bmi_var} | Height: {ht_var} | Weight: {wt_var2}")
mt_bmx = miss_table(bmx)

with open(AUD_DIR / "P_BMX_audit_report.md","w") as f:
    f.write(f"# P_BMX Audit Report\n\n**Generated:** {NOW}\n\n")
    f.write(f"## Shape\n\n- Rows: {bmx.shape[0]}\n- Columns: {bmx.shape[1]}\n\n")
    f.write("## All Columns\n\n```\n" + "\n".join(bmx_cols) + "\n```\n\n")
    f.write("## SEQN Check\n\n")
    if "SEQN" in bmx.columns:
        f.write(f"- Unique SEQN: {bmx['SEQN'].nunique()}\n")
        f.write(f"- Missing SEQN: {bmx['SEQN'].isna().sum()}\n\n")
    for var, label in [(bmi_var,"BMI"), (ht_var,"Height (cm)"), (wt_var2,"Weight (kg)")]:
        if var:
            f.write(f"## {label} (`{var}`)\n\n")
            f.write(f"- Stats: {num_stats(bmx[var].dropna())}\n")
            f.write(f"- Missing: {bmx[var].isna().sum()} ({100*bmx[var].isna().mean():.1f}%)\n\n")
    f.write("## Plausibility Notes\n\n")
    if bmi_var:
        extreme = bmx[bmx[bmi_var] > 70]
        f.write(f"- BMI > 70: {len(extreme)} records (flagged for review, NOT removed)\n")
        extreme2 = bmx[bmx[bmi_var] < 10]
        f.write(f"- BMI < 10: {len(extreme2)} records (flagged for review, NOT removed)\n\n")
    f.write("## Missingness Table\n\n")
    f.write(mt_bmx.to_markdown(index=False))
    f.write("\n")
print("  → Saved P_BMX_audit_report.md")

# ──────────────────────────────────────────────────────────────────────────────
# Laboratory audit (only core files; expand when lab XPTs are added)
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== Laboratory Audit ===")
lab_files = [p for p in RAW_DIR.glob("*.xpt") if p.name not in ("P_LUX.xpt","P_DEMO.xpt","P_BMX.xpt")]
lab_files += [p for p in RAW_DIR.glob("*.XPT") if p.name not in ("P_LUX.XPT","P_DEMO.XPT","P_BMX.XPT")]

lab_rows = []
with open(AUD_DIR / "laboratory_audit_report.md","w") as f:
    f.write(f"# Laboratory File Audit Report\n\n**Generated:** {NOW}\n\n")
    if not lab_files:
        f.write("## Status\n\nNo additional laboratory XPT files found in the raw directory.\n\n")
        f.write("**Action required before Phase 2:** Download the relevant NHANES 2017-Mar2020 "
                "laboratory component files (e.g., Biochemistry Profile, CBC, Lipids) and place "
                "them in:\n`data/raw/NHANES_2017_2020/`\n\n")
        f.write("### Required Laboratory Variables (from research protocol)\n\n")
        for v in ["AST (LBXSASSI)","ALT (LBXSATSI)","Total Bilirubin (LBXSTB)",
                  "Albumin (LBXSAL)","Platelets (LBXPLTSI)",
                  "Glucose (LBXGLU)","Total Cholesterol (LBXTC)",
                  "HDL Cholesterol (LBDHDD)","Triglycerides (LBXTR)",
                  "Alkaline Phosphatase (LBXSAPSI)"]:
            f.write(f"- {v}\n")
        f.write("\n> STOP CONDITION: Laboratory files are absent. "
                "Phase 1 cannot be declared complete until they are downloaded, "
                "audited, and merged.\n")
        print("  WARNING: No laboratory XPT files found. Phase 1 blocked on lab data.")
    else:
        for lpath in lab_files:
            ldf = pd.read_sas(lpath, format="xport", encoding="utf-8")
            f.write(f"## {lpath.name}\n\n")
            f.write(f"Shape: {ldf.shape[0]} rows × {ldf.shape[1]} cols\n\n")
            f.write("Columns: " + ", ".join(ldf.columns.tolist()) + "\n\n")
            mt = miss_table(ldf)
            f.write(mt.to_markdown(index=False) + "\n\n")
            for col in ldf.columns:
                lab_rows.append({"file": lpath.name, "variable": col,
                                 "n_obs": int((~ldf[col].isna()).sum()),
                                 "n_missing": int(ldf[col].isna().sum()),
                                 "pct_missing": round(100*ldf[col].isna().mean(),2)})

pd.DataFrame(lab_rows).to_csv(AUD_DIR / "laboratory_inventory.csv", index=False)
print("  → Saved laboratory_audit_report.md")
print("  → Saved laboratory_inventory.csv")
print("[STEP 3 (FILE AUDITS) COMPLETE]")
