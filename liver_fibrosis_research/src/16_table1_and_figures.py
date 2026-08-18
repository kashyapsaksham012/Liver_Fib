"""
16_table1_and_figures.py
Phase 1 Remediation - Error 12 & 13 fixes: proper descriptive Table 1 and the full
required figure set. DESCRIPTIVE ONLY -- no model exists yet; demographic differences
in raw LUXSMED/CAP/lab values are NOT described as "bias" anywhere in this script.

Produces:
  results/tables/phase1_table1.csv
  results/tables/phase1_table1.md
  results/figures/LUXSMED_distribution.png (duplicate-safe alias of P_LUX_stiffness_distribution.png)
  results/figures/LUXCAPM_distribution.png
  results/figures/liver_stiffness_by_race_ethnicity.png
  results/figures/liver_stiffness_by_bmi_group.png
  results/figures/laboratory_distributions.png
  results/figures/candidate_predictor_correlation_matrix.png
"""

import os, sys, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, TAB_DIR, FIG_DIR, NOW, RACE_MAP_RIDRETH3, SEX_MAP, CORE_LABS_BROAD, CORE_LABS_FASTING

warnings.filterwarnings("ignore", category=FutureWarning)

CONTINUOUS = {
    "RIDAGEYR": "Age (years)", "BMXBMI": "Body Mass Index (kg/m^2)", "BMXWT": "Weight (kg)", "BMXHT": "Height (cm)",
    "LUXSMED": "Liver stiffness, median (kPa)", "LUXCAPM": "CAP, median (dB/m)",
    "LUXSIQRM": "Stiffness IQR/median ratio (%)",
    "LBXSATSI": "ALT (U/L)", "LBXSASSI": "AST (U/L)", "LBXSAL": "Albumin (g/dL)", "LBXSAPSI": "ALP (IU/L)",
    "LBXSTB": "Total Bilirubin (mg/dL)", "LBXPLTSI": "Platelets (10^9/L)",
    "LBXGLU": "Fasting Glucose (mg/dL)", "LBXTR": "Triglycerides (mg/dL)", "LBDHDD": "HDL (mg/dL)"
}
CATEGORICAL = {"RIAGENDR": SEX_MAP, "RIDRETH3": RACE_MAP_RIDRETH3, "LUAXSTAT": {1.0: "Complete", 2.0: "Partial", 3.0: "Ineligible", 4.0: "Not done"}}

def main():
    print("=== Table 1 & Required Figure Set (Error 12 & 13) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    n_total = len(master)

    # ── Table 1 ──────────────────────────────────────────────────────────────
    rows = []
    rows.append({"variable": "N (full P_LUX-anchored cohort)", "type": "N", "n": n_total, "missing_n": 0, "missing_pct": 0,
                "mean_or_pct": None, "sd": None, "median": None, "iqr": None, "min": None, "max": None})
    for var, label in CONTINUOUS.items():
        if var not in master.columns:
            continue
        s = master[var]
        obs = s.dropna()
        rows.append({
            "variable": label, "type": "continuous", "n": int(obs.shape[0]),
            "missing_n": int(s.isna().sum()), "missing_pct": round(100*s.isna().mean(), 2),
            "mean_or_pct": round(obs.mean(), 2) if len(obs) else None, "sd": round(obs.std(), 2) if len(obs) else None,
            "median": round(obs.median(), 2) if len(obs) else None,
            "iqr": round(obs.quantile(0.75) - obs.quantile(0.25), 2) if len(obs) else None,
            "min": round(obs.min(), 2) if len(obs) else None, "max": round(obs.max(), 2) if len(obs) else None
        })
    for var, vmap in CATEGORICAL.items():
        if var not in master.columns:
            continue
        for code, lbl in vmap.items():
            n = int((master[var] == code).sum())
            rows.append({"variable": f"{var}: {lbl}", "type": "categorical", "n": n, "missing_n": None,
                        "missing_pct": None, "mean_or_pct": round(100*n/n_total, 2), "sd": None, "median": None,
                        "iqr": None, "min": None, "max": None})
        n_miss = int(master[var].isna().sum())
        rows.append({"variable": f"{var}: Missing", "type": "categorical", "n": n_miss, "missing_n": None,
                    "missing_pct": None, "mean_or_pct": round(100*n_miss/n_total, 2), "sd": None, "median": None,
                    "iqr": None, "min": None, "max": None})

    t1 = pd.DataFrame(rows)
    t1.to_csv(TAB_DIR / "phase1_table1.csv", index=False)
    with open(TAB_DIR / "phase1_table1.md", "w") as f:
        f.write(f"# Phase 1 Descriptive Table 1\n\n**Generated:** {NOW}  \n**N = {n_total}** (P_LUX-anchored cohort, "
                "no exclusions applied -- descriptive characterization only)\n\n")
        f.write(t1.to_markdown(index=False) + "\n")
    print(f"  Saved phase1_table1.csv/.md ({len(t1)} rows).")

    # ── Figures ──────────────────────────────────────────────────────────────
    if "LUXSMED" in master.columns:
        sv = master["LUXSMED"].dropna()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.hist(sv, bins=60, color="#2196F3", edgecolor="white")
        ax.set_title("LUXSMED Distribution (non-missing, DESCRIPTIVE ONLY)"); ax.set_xlabel("kPa"); ax.set_ylabel("Count")
        plt.tight_layout(); plt.savefig(FIG_DIR / "LUXSMED_distribution.png", dpi=150); plt.close()

    if "LUXCAPM" in master.columns:
        cv = master["LUXCAPM"].dropna()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.hist(cv, bins=60, color="#8E24AA", edgecolor="white")
        ax.set_title("LUXCAPM Distribution (non-missing, DESCRIPTIVE ONLY)"); ax.set_xlabel("dB/m"); ax.set_ylabel("Count")
        plt.tight_layout(); plt.savefig(FIG_DIR / "LUXCAPM_distribution.png", dpi=150); plt.close()

    if {"LUXSMED", "RIDRETH3"}.issubset(master.columns):
        d = master[["LUXSMED", "RIDRETH3"]].dropna()
        d["Race"] = d["RIDRETH3"].map(RACE_MAP_RIDRETH3)
        fig, ax = plt.subplots(figsize=(10, 5))
        groups = [g["LUXSMED"].values for _, g in d.groupby("Race")]
        labels = [lbl for lbl, _ in d.groupby("Race")]
        ax.boxplot(groups, tick_labels=labels, showfliers=False)
        ax.set_ylabel("Liver Stiffness (kPa)"); ax.set_title("LUXSMED by Race/Ethnicity (RIDRETH3) - DESCRIPTIVE ONLY, no model exists")
        plt.xticks(rotation=30, ha="right"); plt.tight_layout()
        plt.savefig(FIG_DIR / "liver_stiffness_by_race_ethnicity.png", dpi=150); plt.close()

    if {"LUXSMED", "BMXBMI"}.issubset(master.columns):
        d = master[["LUXSMED", "BMXBMI"]].dropna().copy()
        d["BMI_Group"] = pd.cut(d["BMXBMI"], bins=[0, 18.5, 24.9, 29.9, 200],
                                labels=["Underweight", "Normal", "Overweight", "Obese"])
        fig, ax = plt.subplots(figsize=(8, 5))
        groups = [g["LUXSMED"].values for _, g in d.groupby("BMI_Group", observed=True)]
        labels = [lbl for lbl, _ in d.groupby("BMI_Group", observed=True)]
        ax.boxplot(groups, tick_labels=labels, showfliers=False)
        ax.set_ylabel("Liver Stiffness (kPa)"); ax.set_title("LUXSMED by Provisional BMI Group - DESCRIPTIVE ONLY")
        plt.tight_layout(); plt.savefig(FIG_DIR / "liver_stiffness_by_bmi_group.png", dpi=150); plt.close()

    lab_vars = [v for v in ["LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBXGLU", "LBXTR", "LBDHDD"] if v in master.columns]
    if lab_vars:
        n_cols = 3
        n_rows = int(np.ceil(len(lab_vars) / n_cols))
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 3.2*n_rows))
        axes = np.array(axes).reshape(-1)
        for ax, var in zip(axes, lab_vars):
            s = master[var].dropna()
            ax.hist(s, bins=40, color="#E57373", edgecolor="white")
            ax.set_title(f"{var} (N={len(s)})", fontsize=10)
        for ax in axes[len(lab_vars):]:
            ax.axis("off")
        plt.suptitle("Major Laboratory Variable Distributions (non-missing, DESCRIPTIVE ONLY)")
        plt.tight_layout(); plt.savefig(FIG_DIR / "laboratory_distributions.png", dpi=150); plt.close()

    corr_vars = [v for v in list(CORE_LABS_BROAD) + list(CORE_LABS_FASTING) + ["BMXBMI", "RIDAGEYR"] if v in master.columns]
    if len(corr_vars) > 2:
        corr = master[corr_vars].corr(method="spearman")
        fig, ax = plt.subplots(figsize=(8, 7))
        im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr_vars))); ax.set_xticklabels(corr_vars, rotation=45, ha="right")
        ax.set_yticks(range(len(corr_vars))); ax.set_yticklabels(corr_vars)
        plt.colorbar(im, label="Spearman correlation")
        ax.set_title("Candidate Predictor Correlation Matrix (DESCRIPTIVE ONLY)")
        plt.tight_layout(); plt.savefig(FIG_DIR / "candidate_predictor_correlation_matrix.png", dpi=150); plt.close()

    print("  Saved all required descriptive figures.")
    print("[TABLE 1 & FIGURES COMPLETE]")

if __name__ == "__main__":
    main()
