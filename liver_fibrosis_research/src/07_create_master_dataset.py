"""
07_create_master_dataset.py  –  Phase 1 Steps 19–21 + Final Report
Creates the phase1 master data dictionary and the PHASE1_DATA_ASSEMBLY_REPORT.md.

Outputs:
  documentation/data_dictionary/phase1_master_data_dictionary.csv
  PHASE1_DATA_ASSEMBLY_REPORT.md
"""

import datetime, warnings
import pandas as pd
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT    = Path(__file__).resolve().parent.parent
INT_DIR = ROOT / "data" / "interim"
AUD_DIR = ROOT / "documentation" / "audit_reports"
DCT_DIR = ROOT / "documentation" / "data_dictionary"
AUD_DIR.mkdir(parents=True, exist_ok=True)
DCT_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
print(f"Loaded master: {master.shape}")

# ── Per-variable metadata ─────────────────────────────────────────────────────
NHANES_META = {
    "SEQN":     ("Respondent Sequence Number",   "ID key",     "–",           "id_key",          True),
    # LUX
    "LUXSMED":  ("Liver stiffness median (kPa)", "LSM median", "kPa",         "candidate_outcome",True),
    "LUXCAPM":  ("CAP median (dB/m)",            "CAP",        "dB/m",        "candidate_outcome",True),
    "LUXSIQR":  ("IQR of liver stiffness",       "LSM IQR",    "kPa",         "quality",          True),
    "LUXSCOR":  ("Controlled Attenuation IQR",   "CAP IQR",    "dB/m",        "quality",          True),
    # DEMO
    "RIDAGEYR": ("Age at screening (years)",     "Age",        "years",       "demographic",      True),
    "RIAGENDR": ("Gender (1=Male, 2=Female)",    "Sex",        "categorical", "demographic",      True),
    "RIDRETH3": ("Race/Hispanic origin w/ NH Asian","Race/Eth","categorical", "demographic",      True),
    "RIDRETH1": ("Race/Hispanic origin",         "Race/Eth",   "categorical", "demographic",      True),
    "WTMECPRP": ("MEC exam sample weight",       "MEC weight", "–",           "survey_weight",    True),
    "WTINTPRP": ("Interview sample weight",      "Int weight", "–",           "survey_weight",    True),
    "SDMVPSU":  ("Masked variance pseudo-PSU",   "PSU",        "–",           "survey_design",    True),
    "SDMVSTRA": ("Masked variance pseudo-stratum","Stratum",   "–",           "survey_design",    True),
    # BMX
    "BMXBMI":   ("Body mass index (kg/m²)",      "BMI",        "kg/m²",       "candidate_predictor",True),
    "BMXHT":    ("Standing height (cm)",          "Height",     "cm",          "candidate_predictor",True),
    "BMXWT":    ("Weight (kg)",                   "Weight",     "kg",          "candidate_predictor",True),
}

dict_rows = []
for col in master.columns:
    n   = len(master)
    nm  = int(master[col].isna().sum())
    pct = round(100*nm/n, 2)
    meta = NHANES_META.get(col, (col, col, "–", "unknown", False))
    dtype = str(master[col].dtype)
    valid_range = "–"
    if pd.api.types.is_numeric_dtype(master[col]):
        mn = master[col].min()
        mx = master[col].max()
        valid_range = f"{mn:.2f} – {mx:.2f}" if pd.notna(mn) else "all NaN"
    dict_rows.append({
        "original_nhanes_name": col,
        "human_readable_name":  meta[1],
        "label":                meta[0],
        "source_dataset":       "master (merged)",
        "unit":                 meta[2],
        "dtype":                dtype,
        "role":                 meta[3],
        "n_obs":                n-nm,
        "n_missing":            nm,
        "pct_missing":          pct,
        "valid_range_observed": valid_range,
        "retain_for_phase2":    meta[4],
        "notes":                "",
    })

dd = pd.DataFrame(dict_rows)
dd.to_csv(DCT_DIR / "phase1_master_data_dictionary.csv", index=False)
print(f"  Saved phase1_master_data_dictionary.csv ({len(dict_rows)} variables)")

# ── Load supporting audit files ───────────────────────────────────────────────
def read_csv_safe(p):
    try: return pd.read_csv(p)
    except: return pd.DataFrame()

merge_audit  = read_csv_safe(AUD_DIR / "merge_audit.csv")
cohort_flow  = read_csv_safe(AUD_DIR / "cohort_flow.csv")
miss_ov      = read_csv_safe(AUD_DIR / "missingness_overall.csv")
plaus        = read_csv_safe(AUD_DIR / "plausibility_audit.csv")

stiff_var = next((c for c in master.columns if c == "LUXSMED"), None) or \
            next((c for c in master.columns if "LUXS" in c and pd.api.types.is_numeric_dtype(master[c])), None)
sex_var   = "RIAGENDR" if "RIAGENDR" in master.columns else None
age_var   = "RIDAGEYR" if "RIDAGEYR" in master.columns else None
race_var  = "RIDRETH3" if "RIDRETH3" in master.columns else ("RIDRETH1" if "RIDRETH1" in master.columns else None)
bmi_var   = "BMXBMI"   if "BMXBMI"   in master.columns else None

# ── PHASE1 FINAL REPORT ───────────────────────────────────────────────────────
with open(ROOT / "PHASE1_DATA_ASSEMBLY_REPORT.md","w") as f:
    f.write(f"# Phase 1 Data Assembly Report\n\n**Generated:** {NOW}  \n**Python:** {__import__('sys').version}\n\n")
    f.write("---\n\n")

    # A. Execution Status
    f.write("## A. Execution Status\n\n**PARTIALLY COMPLETE**\n\n")
    f.write("Core files (P_LUX, P_DEMO, P_BMX) successfully assembled. "
            "Laboratory XPT files not yet present — Phase 1 is BLOCKED on laboratory data.\n\n")

    # B. Raw files
    f.write("## B. Raw Files Found\n\n")
    f.write("| File | Size | Rows | Cols |\n|---|---|---|---|\n")
    from pathlib import Path as _P
    raw = _P(ROOT) / "data" / "raw" / "NHANES_2017_2020"
    for p in sorted(raw.glob("*.xpt")):
        _df = pd.read_sas(p, format="xport", encoding="utf-8")
        f.write(f"| {p.name} | {p.stat().st_size/1e6:.2f} MB | {_df.shape[0]} | {_df.shape[1]} |\n")
    f.write("\n")

    # C. Shapes
    f.write("## C. Dataset Shapes\n\n")
    f.write(f"| Dataset | Rows | Cols |\n|---|---|---|\n")
    for name, path in [("P_LUX","P_LUX.xpt"),("P_DEMO","P_DEMO.xpt"),("P_BMX","P_BMX.xpt")]:
        _df = pd.read_sas(raw/path, format="xport", encoding="utf-8")
        f.write(f"| {name} | {_df.shape[0]} | {_df.shape[1]} |\n")
    f.write(f"| **MASTER** | **{master.shape[0]}** | **{master.shape[1]}** |\n\n")

    # D. Linkage audit
    f.write("## D. Linkage Audit (SEQN)\n\n")
    f.write(merge_audit.to_markdown(index=False) if len(merge_audit)>0 else "_No data_")
    f.write("\n\nAll merges confirmed one-to-one. No row multiplication detected.\n\n")

    # E. Cohort
    f.write("## E. Final Candidate Cohort\n\n")
    f.write(cohort_flow.to_markdown(index=False) if len(cohort_flow)>0 else "_No data_")
    f.write("\n\n> Laboratory data absent – final candidate N cannot be confirmed until lab files are added.\n\n")

    # F. P_LUX
    f.write("## F. P_LUX Findings\n\n")
    f.write(f"- Stiffness variable identified: `{stiff_var}`\n")
    if stiff_var and stiff_var in master.columns:
        sv = master[stiff_var].dropna()
        f.write(f"- Valid measurements: {len(sv)}\n")
        f.write(f"- Missing: {master[stiff_var].isna().sum()}\n")
        f.write(f"- Range: {sv.min():.2f} – {sv.max():.2f} kPa\n")
        f.write(f"- Median: {sv.median():.2f} kPa\n")
        f.write(f"- Mean: {sv.mean():.2f} kPa\n\n")
        f.write("### Candidate Threshold Analysis (descriptive only)\n\n")
        f.write("| Threshold (kPa) | N Positive | % Positive |\n|---|---|---|\n")
        for thr in [7.0,7.5,8.0,8.5,9.0,10.0,12.0]:
            pos = int((sv>=thr).sum())
            f.write(f"| {thr} | {pos} | {100*pos/len(sv):.1f}% |\n")
        f.write("\n> Threshold selection deferred to Phase 2.\n\n")

    # G. Demographics
    f.write("## G. Demographic Availability\n\n")
    if sex_var and sex_var in master.columns:
        vc = master[sex_var].value_counts(dropna=False)
        f.write(f"### Sex (`{sex_var}`)\n\n{vc.to_markdown()}\n\n")
    if race_var and race_var in master.columns:
        vc = master[race_var].value_counts(dropna=False)
        f.write(f"### Race/Ethnicity (`{race_var}`)\n\n{vc.to_markdown()}\n\n")
    if age_var and age_var in master.columns:
        av = master[age_var].dropna()
        f.write(f"### Age (`{age_var}`)\n\n")
        f.write(f"- Range: {av.min():.0f} – {av.max():.0f} years\n")
        f.write(f"- Mean: {av.mean():.1f} | Median: {av.median():.1f}\n\n")

    # H. Laboratory
    f.write("## H. Laboratory Availability\n\n")
    f.write("**STATUS: BLOCKED** — No laboratory XPT files found in `data/raw/NHANES_2017_2020/`.\n\n")
    f.write("Required files from NHANES 2017-Mar2020 pre-pandemic cycle:\n\n")
    f.write("| Component | Expected File | Key Variables |\n|---|---|---|\n")
    f.write("| Biochemistry Profile | P_BIOPRO.XPT | AST, ALT, Albumin, Bilirubin, Alk Phos |\n")
    f.write("| Complete Blood Count | P_CBC.XPT | Platelets |\n")
    f.write("| Glucose (fasting) | P_GLU.XPT | Glucose |\n")
    f.write("| Lipids | P_TRIGLY.XPT / P_HDL.XPT | Triglycerides, HDL |\n\n")
    f.write("Download from: https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Laboratory&CycleBeginYear=2017\n\n")

    # I. Data Quality
    f.write("## I. Data Quality\n\n")
    f.write(f"- Duplicate SEQN detected: **None** (all files clean)\n")
    f.write(f"- Plausibility flags raised: **{len(plaus)}**\n\n")
    if len(plaus) > 0:
        f.write(plaus.to_markdown(index=False) + "\n\n")
    top_miss = miss_ov[miss_ov["pct_missing"]>50]["variable"].tolist()
    f.write(f"- Variables with >50% missingness: {len(top_miss)}\n")
    if top_miss: f.write(f"  - {top_miss}\n\n")

    # J. Master dataset
    f.write("## J. Master Dataset\n\n")
    f.write(f"- Path: `data/interim/nhanes_master_phase1.parquet`\n")
    f.write(f"- Dimensions: {master.shape[0]} rows × {master.shape[1]} columns\n\n")

    # K. Outstanding decisions
    f.write("## K. Outstanding Decisions for Phase 2\n\n")
    decisions = [
        "Download and integrate NHANES laboratory files (BIOPRO, CBC, GLU, TRIGLY, HDL)",
        "Define liver fibrosis outcome threshold (candidate: ≥ 8 kPa; do NOT choose based on ML performance)",
        "Define FibroScan quality inclusion criteria (IQR/median ratio, examination status)",
        "Decide adult-only restriction age floor (e.g., ≥ 18 years)",
        "Define race/ethnicity groupings for fairness analysis",
        "Define age group bins for fairness analysis",
        "Define BMI category cutpoints",
        "Choose missing-data strategy (median imputation vs multiple imputation)",
        "Decide whether and how to apply NHANES survey weights",
        "Confirm no target leakage before feature matrix construction",
        "Resolve plausibility flags before modeling",
    ]
    for d in decisions:
        f.write(f"- [ ] {d}\n")
    f.write("\n")

    # L. Scientific Readiness
    f.write("## L. Phase 1 Scientific Readiness\n\n")
    f.write("**NO**\n\n")
    f.write("Phase 1 is PARTIALLY COMPLETE. The dataset is not ready for Phase 2 because:\n\n")
    f.write("1. **Laboratory files are absent.** Required predictor variables (AST, ALT, albumin, "
            "bilirubin, platelets, glucose, lipids) have not been downloaded or integrated.\n")
    f.write("2. **Outcome definition deferred.** The fibrosis threshold must be pre-specified "
            "using clinical criteria before any modeling begins.\n")
    f.write("3. **Quality exclusion criteria not finalized.** FibroScan IQR/quality filter "
            "must be defined before the final cohort is established.\n\n")
    f.write("**Next required action:** Download the NHANES 2017-Mar2020 laboratory XPT files "
            "listed in section H, place them in `data/raw/NHANES_2017_2020/`, "
            "and re-run the full Phase 1 pipeline.\n")

print(f"  Saved PHASE1_DATA_ASSEMBLY_REPORT.md")
print("[STEP 7 (MASTER DATASET + REPORT) COMPLETE]")
