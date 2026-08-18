"""
03_audit_lux_demo_bmx.py
Phase 1 Remediation - Dedicated audits of P_LUX, P_DEMO, and P_BMX.
Uses sentinel-corrected loads. Distinguishes "non-missing LUXSMED" from the OFFICIAL
NHANES quality-valid exam definition (LUAXSTAT==1). Adds P_BMX completeness (BMDSTATS)
and measurement comment codes (BMIWT/BMIHT), previously not audited.

Produces:
  documentation/audit_reports/P_LUX_audit_report.md
  documentation/audit_reports/P_DEMO_audit_report.md
  documentation/audit_reports/P_BMX_audit_report.md
  results/figures/P_LUX_stiffness_distribution.png
  results/figures/P_LUX_cap_distribution.png
"""

import os, sys, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(__file__))
from _common import AUDIT_DIR, FIG_DIR, NOW, load_xpt, CANDIDATE_THRESHOLDS

warnings.filterwarnings("ignore", category=FutureWarning)

def miss_table(df):
    rows = []
    for c in df.columns:
        n = len(df)
        nm = int(df[c].isna().sum())
        rows.append({"variable": c, "n_obs": n-nm, "n_missing": nm, "pct_missing": round(100*nm/n, 2)})
    return pd.DataFrame(rows)

def num_stats(s):
    d = s.describe()
    return f"N={int(d['count'])} | min={d['min']:.2f} | p25={d['25%']:.2f} | median={d['50%']:.2f} | p75={d['75%']:.2f} | max={d['max']:.2f} | mean={d['mean']:.2f}"

def main():
    print("=== Step 5-8: Dedicated Audits of Core NHANES Files (Remediated) ===")

    # ── P_LUX AUDIT ───────────────────────────────────────────────────────────
    print("Auditing P_LUX...")
    lux = load_xpt("P_LUX.xpt")
    stiff_var, cap_var = "LUXSMED", "LUXCAPM"

    if stiff_var in lux.columns:
        sv = lux[stiff_var].dropna()
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        axes[0].hist(sv, bins=60, color="#2196F3", edgecolor="white")
        axes[0].set_title(f"Liver Stiffness ({stiff_var}) - non-missing")
        axes[0].set_xlabel("kPa"); axes[0].set_ylabel("Count")
        axes[1].hist(np.log1p(sv), bins=60, color="#4CAF50", edgecolor="white")
        axes[1].set_title(f"log1p({stiff_var})")
        axes[1].set_xlabel("log1p(kPa)"); axes[1].set_ylabel("Count")
        plt.tight_layout(); plt.savefig(FIG_DIR / "P_LUX_stiffness_distribution.png", dpi=150); plt.close()

    if cap_var in lux.columns:
        cv = lux[cap_var].dropna()
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(cv, bins=60, color="#8E24AA", edgecolor="white")
        ax.set_title(f"CAP ({cap_var}) - non-missing"); ax.set_xlabel("dB/m"); ax.set_ylabel("Count")
        plt.tight_layout(); plt.savefig(FIG_DIR / "P_LUX_cap_distribution.png", dpi=150); plt.close()

    with open(AUDIT_DIR / "P_LUX_audit_report.md", "w") as f:
        f.write(f"# P_LUX Audit Report (Remediated)\n\n**Generated:** {NOW}\n\n")
        f.write(f"## Shape\n\n- Rows: {lux.shape[0]}\n- Columns: {lux.shape[1]}\n\n")
        f.write("## SEQN Check\n\n")
        f.write(f"- Unique SEQN: {lux['SEQN'].nunique()}\n")
        f.write(f"- Missing SEQN: {lux['SEQN'].isna().sum()}\n")
        f.write(f"- Duplicate SEQN: {lux.shape[0] - lux['SEQN'].nunique()}\n\n")

        f.write("## OFFICIAL NHANES Quality-Valid Exam Definition (verified against live P_LUX codebook)\n\n")
        f.write("> `LUAXSTAT == 1` ('Complete') is officially defined by NHANES as: fasting time of at least "
                "3 hours, 10 or more complete stiffness (E) measures, AND stiffness IQR/median (LUXSIQRM) < 30%. "
                "This is NHANES's own definition, not a criterion invented by this project. Prior Phase 1 "
                "material incorrectly treated 'non-missing LUXSMED' as equivalent to a quality-valid measurement; "
                "this report corrects that terminology throughout.\n\n")

        vc = lux["LUAXSTAT"].value_counts(dropna=False).sort_index()
        f.write("### LUAXSTAT distribution\n\n")
        f.write("| Code | Meaning | N |\n|---|---|---|\n")
        labels = {1.0: "Complete (quality-valid)", 2.0: "Partial", 3.0: "Ineligible", 4.0: "Not done"}
        for code, n in vc.items():
            f.write(f"| {code} | {labels.get(code, 'Unknown')} | {int(n)} |\n")
        f.write("\n")

        n_nonmissing_smed = int(lux[stiff_var].notna().sum())
        n_valid_exam = int((lux["LUAXSTAT"] == 1.0).sum())
        n_smed_and_valid = int(((lux["LUAXSTAT"] == 1.0) & lux[stiff_var].notna()).sum())
        n_smed_notna_not_valid = int((lux[stiff_var].notna() & (lux["LUAXSTAT"] != 1.0)).sum())
        f.write("### Reconciliation: non-missing LUXSMED vs. quality-valid exam\n\n")
        f.write(f"- Non-missing `LUXSMED` (any completeness): **{n_nonmissing_smed}**\n")
        f.write(f"- `LUAXSTAT == 1` (official quality-valid, 'Complete'): **{n_valid_exam}**\n")
        f.write(f"- Non-missing `LUXSMED` AND `LUAXSTAT == 1`: **{n_smed_and_valid}**\n")
        f.write(f"- Non-missing `LUXSMED` but NOT quality-valid (LUAXSTAT in {{2,3,4}}, i.e. mostly Partial "
                f"exams that still produced a numeric median): **{n_smed_notna_not_valid}**\n\n")
        f.write("> These are two different populations. Phase 2 must decide, as a pre-specified protocol "
                "choice, whether the analytical cohort requires `LUAXSTAT==1` or only non-missing `LUXSMED`. "
                "This decision is NOT made here.\n\n")

        if stiff_var in lux.columns:
            sv = lux[stiff_var].dropna()
            f.write(f"## Outcomes Profile\n\n### Liver Stiffness (`{stiff_var}`)\n\n")
            f.write(f"- Non-missing (any completeness): {len(sv)}\n- Stats: {num_stats(sv)}\n\n")
            f.write("#### Candidate Cutpoint Counts, ALL non-missing LUXSMED (Descriptive / Feasibility Only)\n\n")
            f.write("| Cutpoint (kPa) | N >= Cutpoint | % >= Cutpoint | Candidate Label | Citation |\n|---|---|---|---|---|\n")
            for t in CANDIDATE_THRESHOLDS:
                pos = (sv >= t["kpa"]).sum()
                pct = round(100*pos/len(sv), 2)
                f.write(f"| {t['kpa']} | {pos} | {pct}% | {t['label']} | {t['citation']} |\n")
            f.write("\n> NOTE: All cutpoints above are CANDIDATE / provisional, sourced from external clinical "
                    "literature (see documentation/source_metadata/phase1_references.md), NOT from NHANES "
                    "documentation, and NOT finalized. Do NOT select a threshold by optimizing ML performance.\n\n")

            sv_valid = lux.loc[lux["LUAXSTAT"] == 1.0, stiff_var].dropna()
            f.write(f"#### Same table restricted to LUAXSTAT==1 (quality-valid) subset, N={len(sv_valid)}\n\n")
            f.write("| Cutpoint (kPa) | N >= Cutpoint | % >= Cutpoint |\n|---|---|---|\n")
            for t in CANDIDATE_THRESHOLDS:
                pos = (sv_valid >= t["kpa"]).sum()
                pct = round(100*pos/len(sv_valid), 2) if len(sv_valid) else 0
                f.write(f"| {t['kpa']} | {pos} | {pct}% |\n")
            f.write("\n")

        if cap_var in lux.columns:
            cv = lux[cap_var].dropna()
            f.write(f"### Controlled Attenuation Parameter (`{cap_var}`)\n\n- Non-missing: {len(cv)}\n- Stats: {num_stats(cv)}\n\n")

        f.write("## Quality / Status Variables Profile\n\n")
        for col in ["LUAXSTAT", "LUARXNC", "LUARXND", "LUARXIN", "LUANMVGP", "LUANMTGP"]:
            if col in lux.columns:
                f.write(f"### {col}\n\n")
                if pd.api.types.is_numeric_dtype(lux[col]) and lux[col].nunique() > 15:
                    f.write(f"- Stats: {num_stats(lux[col].dropna())}\n\n")
                else:
                    f.write(lux[col].value_counts(dropna=False).to_markdown() + "\n\n")

        f.write("## Missingness Table (post sentinel-correction)\n\n")
        f.write(miss_table(lux).to_markdown(index=False) + "\n")

    # ── P_DEMO AUDIT ──────────────────────────────────────────────────────────
    print("Auditing P_DEMO...")
    demo = load_xpt("P_DEMO.xpt")
    with open(AUDIT_DIR / "P_DEMO_audit_report.md", "w") as f:
        f.write(f"# P_DEMO Audit Report (Remediated)\n\n**Generated:** {NOW}\n\n")
        f.write(f"## Shape\n\n- Rows: {demo.shape[0]}\n- Columns: {demo.shape[1]}\n\n")
        f.write("## SEQN Check\n\n- Unique SEQN: {}\n- Missing SEQN: {}\n\n".format(
            demo['SEQN'].nunique(), demo['SEQN'].isna().sum()))

        f.write("## Demographic Subgroups Availability\n\n")
        for col, lbl in [("RIAGENDR", "Sex"), ("RIDRETH1", "Race/Ethnicity (RIDRETH1, 5-cat)"),
                         ("RIDRETH3", "Race/Ethnicity (RIDRETH3, 6-cat, incl. NH Asian)"),
                         ("RIDAGEYR", "Age at Screening (topcoded at 80)")]:
            if col in demo.columns:
                f.write(f"### {lbl} (`{col}`)\n\n")
                if col == "RIDAGEYR":
                    f.write(f"- Stats: {num_stats(demo[col].dropna())}\n- Missing: {demo[col].isna().sum()}\n\n")
                else:
                    f.write(demo[col].value_counts(dropna=False).to_markdown() + "\n\n")
        f.write("> See `race_ethnicity_verification.md` for the RIDRETH1-vs-RIDRETH3 comparison and Phase 2 recommendation.\n\n")

        f.write("## Survey Weights & Design Variables (preserved, NOT yet applied to any analysis)\n\n")
        for col in ["WTMECPRP", "WTINTPRP", "SDMVPSU", "SDMVSTRA"]:
            if col in demo.columns:
                f.write(f"### {col}\n\n")
                if col.startswith("WT"):
                    f.write(f"- Stats: {num_stats(demo[col].dropna())}\n\n")
                else:
                    f.write(demo[col].value_counts(dropna=False).head(10).to_markdown() + "\n\n")

        f.write("## Missingness Table (post sentinel-correction)\n\n")
        f.write(miss_table(demo).to_markdown(index=False) + "\n")

    # ── P_BMX AUDIT ───────────────────────────────────────────────────────────
    print("Auditing P_BMX...")
    bmx = load_xpt("P_BMX.xpt")
    with open(AUDIT_DIR / "P_BMX_audit_report.md", "w") as f:
        f.write(f"# P_BMX Audit Report (Remediated)\n\n**Generated:** {NOW}\n\n")
        f.write(f"## Shape\n\n- Rows: {bmx.shape[0]}\n- Columns: {bmx.shape[1]}\n\n")
        f.write("## SEQN Check\n\n- Unique SEQN: {}\n- Missing SEQN: {}\n\n".format(
            bmx['SEQN'].nunique(), bmx['SEQN'].isna().sum()))

        f.write("## Component Completeness Status (`BMDSTATS`) - official NHANES flag, previously unused\n\n")
        if "BMDSTATS" in bmx.columns:
            f.write(bmx["BMDSTATS"].value_counts(dropna=False).to_markdown() + "\n\n")
            f.write("- 1=Complete data for age group, 2=Partial (height/weight only), 3=Other partial exam, "
                    "4=No body measures data.\n\n")

        f.write("## Key Anthropometrics\n\n")
        for col, lbl in [("BMXBMI", "Body Mass Index (BMI)"), ("BMXWT", "Weight (kg)"), ("BMXHT", "Height (cm)")]:
            if col in bmx.columns:
                f.write(f"### {lbl} (`{col}`)\n\n- Stats: {num_stats(bmx[col].dropna())}\n"
                        f"- Missing: {bmx[col].isna().sum()} ({100*bmx[col].isna().mean():.2f}%)\n\n")

        f.write("## Measurement Comment Codes (previously not audited)\n\n")
        for col, lbl in [("BMIWT", "Weight comment (1=Could not obtain, 3=Clothing, 4=Medical appliance)"),
                         ("BMIHT", "Height comment (1=Could not obtain, 3=Not straight)")]:
            if col in bmx.columns:
                f.write(f"### {col} - {lbl}\n\n")
                f.write(bmx[col].value_counts(dropna=False).to_markdown() + "\n\n")

        f.write("## NHANES's own guidance on implausible values (verified from live codebook)\n\n")
        f.write("> \"Unusual body measures values were noted during review. Typically, unusual values occurred "
                "when a subject was extremely short, tall, overweight, or underweight.\" NHANES does NOT define "
                "a numeric implausibility cutoff itself; any BMI/height/weight plausibility bound used elsewhere "
                "in this project is an externally-sourced clinical convention, documented as such.\n\n")

        f.write("## Missingness Table (post sentinel-correction)\n\n")
        f.write(miss_table(bmx).to_markdown(index=False) + "\n")

    print("[STEP 5-8 COMPLETE]")

if __name__ == "__main__":
    main()
