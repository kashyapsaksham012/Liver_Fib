"""
06_missingness_audit.py
Phase 1 – Step 13 & 15 & 16: Missingness Audit.
Calculates missingness overall, by group, and creates visualizations (bar charts and heatmap).

Produces:
  documentation/audit_reports/missingness_overall.csv
  documentation/audit_reports/missingness_by_group.csv
  results/figures/missingness_barchart.png
  results/figures/missingness_heatmap.png
"""

import os, sys, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, FIG_DIR

warnings.filterwarnings("ignore", category=FutureWarning)

def main():
    print("=== Step 13, 15 & 16: Missingness Audit (post sentinel-correction) ===")
    
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    n_total = len(master)
    print(f"Loaded master dataset: {master.shape}")
    
    # ── Overall missingness ───────────────────────────────────────────────────
    ov_rows = []
    for col in master.columns:
        nm = int(master[col].isna().sum())
        ov_rows.append({
            "variable": col,
            "n_obs": n_total - nm,
            "n_missing": nm,
            "pct_missing": round(100 * nm / n_total, 2)
        })
    df_ov = pd.DataFrame(ov_rows).sort_values("pct_missing", ascending=False)
    df_ov.to_csv(AUDIT_DIR / "missingness_overall.csv", index=False)
    print("  Saved missingness_overall.csv.")
    
    # Missingness barchart (top 30 most missing)
    top_30 = df_ov.head(30)
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(top_30["variable"][::-1], top_30["pct_missing"][::-1], color="#E57373")
    ax.set_xlabel("% Missing")
    ax.set_title("Top 30 Variables by Missingness Percentage")
    ax.axvline(30, color="orange", linestyle="--", alpha=0.7, label="30% threshold")
    ax.axvline(50, color="red", linestyle="--", alpha=0.7, label="50% threshold")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "missingness_barchart.png", dpi=150)
    plt.close()
    print("  Saved missingness_barchart.png.")
    
    # Missingness Heatmap (sample 500 rows, top 25 vars)
    top_25_vars = df_ov.head(25)["variable"].tolist()
    sample_df = master[top_25_vars].sample(min(500, n_total), random_state=42)
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(sample_df.isna().T, cbar=False, cmap=["#4CAF50", "#E57373"], ax=ax)
    ax.set_title("Missingness Pattern Heatmap (top 25 variables, sample of 500 participants)")
    ax.set_xlabel("Participants")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "missingness_heatmap.png", dpi=150)
    plt.close()
    print("  Saved missingness_heatmap.png.")

    # ── Missingness by Demographic Group ──────────────────────────────────────
    sex_var = "RIAGENDR"
    race_var = "RIDRETH1" if "RIDRETH1" in master.columns else ("RIDRETH3" if "RIDRETH3" in master.columns else None)
    
    group_rows = []
    for gvar, glbl in [(sex_var, "Sex"), (race_var, "Race_Ethnicity")]:
        if gvar and gvar in master.columns:
            for gval in master[gvar].dropna().unique():
                sub = master[master[gvar] == gval]
                n_sub = len(sub)
                for col in master.columns:
                    nm = int(sub[col].isna().sum())
                    group_rows.append({
                        "group_variable": gvar,
                        "group_value": gval,
                        "variable": col,
                        "n_obs": n_sub - nm,
                        "n_missing": nm,
                        "pct_missing": round(100 * nm / n_sub, 2)
                    })
                    
    if group_rows:
        pd.DataFrame(group_rows).to_csv(AUDIT_DIR / "missingness_by_group.csv", index=False)
        print("  Saved missingness_by_group.csv.")
        
    print("[STEP 13 & 15 & 16 COMPLETE]")

if __name__ == "__main__":
    main()
