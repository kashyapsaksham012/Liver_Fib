"""
05_missingness_audit.py  –  Phase 1 Step 13
Quantify missingness overall and by major demographic groups.

Outputs:
  documentation/audit_reports/missingness_overall.csv
  documentation/audit_reports/missingness_by_group.csv
  results/figures/missingness_heatmap.png
  results/figures/missingness_barchart.png
"""

import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT    = Path(__file__).resolve().parent.parent
INT_DIR = ROOT / "data" / "interim"
AUD_DIR = ROOT / "documentation" / "audit_reports"
FIG_DIR = ROOT / "results" / "figures"
AUD_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
print(f"Loaded master: {master.shape}")

# ── Overall missingness ───────────────────────────────────────────────────────
rows = []
for col in master.columns:
    n = len(master)
    nm = int(master[col].isna().sum())
    rows.append({"variable":col, "n_obs":n-nm, "n_missing":nm, "pct_missing":round(100*nm/n,2)})
ov = pd.DataFrame(rows).sort_values("pct_missing", ascending=False)
ov.to_csv(AUD_DIR / "missingness_overall.csv", index=False)
print(f"  Saved missingness_overall.csv ({len(ov)} variables)")

# ── Bar chart of top 30 most-missing variables ────────────────────────────────
top = ov.head(30)
fig, ax = plt.subplots(figsize=(12,7))
bars = ax.barh(top["variable"][::-1], top["pct_missing"][::-1], color="#EF5350")
ax.set_xlabel("% Missing")
ax.set_title("Top 30 Variables by Missingness — NHANES Master Phase 1")
ax.axvline(50, color="orange", linestyle="--", alpha=0.7, label="50%")
ax.axvline(80, color="red",    linestyle="--", alpha=0.7, label="80%")
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "missingness_barchart.png", dpi=150)
plt.close()
print("  Saved missingness_barchart.png")

# ── Missingness heatmap (top 30 vars, sample 500 rows) ───────────────────────
top_vars = top["variable"].tolist()
sample = master[top_vars].sample(min(500, len(master)), random_state=42)
fig, ax = plt.subplots(figsize=(14,8))
sns.heatmap(sample.isna().T, cbar=False, yticklabels=True, xticklabels=False,
            cmap=["#4CAF50","#EF5350"], ax=ax)
ax.set_title("Missingness Pattern Heatmap (top 30 variables, sample 500 participants)")
ax.set_xlabel("Participants (sample)")
plt.tight_layout()
plt.savefig(FIG_DIR / "missingness_heatmap.png", dpi=150)
plt.close()
print("  Saved missingness_heatmap.png")

# ── Missingness by sex ───────────────────────────────────────────────────────
sex_var = next((c for c in master.columns if "RIAGENDR" in c), None)
race_var = next((c for c in master.columns if "RIDRETH3" in c or "RIDRETH1" in c), None)

group_rows = []
for grp_var, grp_label in [(sex_var,"sex"),(race_var,"race_ethnicity")]:
    if grp_var is None:
        print(f"  WARNING: {grp_label} variable not found")
        continue
    for grp_val in master[grp_var].dropna().unique():
        subset = master[master[grp_var] == grp_val]
        for col in master.columns:
            nm = int(subset[col].isna().sum())
            n  = len(subset)
            group_rows.append({"group_variable":grp_var,"group_value":grp_val,
                                "variable":col,"n_obs":n-nm,"n_missing":nm,
                                "pct_missing":round(100*nm/n,2)})

gb = pd.DataFrame(group_rows)
gb.to_csv(AUD_DIR / "missingness_by_group.csv", index=False)
print(f"  Saved missingness_by_group.csv ({len(gb)} rows)")
print("[STEP 5 (MISSINGNESS) COMPLETE]")
