"""
tradeoff_05_generate_figures.py
Generate Publication-Quality Figures 1 through 5 for Trade-off Report

Figures generated:
1. figure1_bmi_fairness_vs_specificity_pareto.png
2. figure2_age_fairness_vs_specificity_pareto.png
3. figure3_coverage_vs_set_size_tradeoff.png
4. figure4_m4b_shrinkage_sensitivity.png
5. figure5_lightgbm_failure_diagnostics.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIG_DIR = RESULTS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

MODEL_PALETTE = {
    "logistic": "#1f77b4",
    "random_forest": "#2ca02c",
    "xgboost": "#ff7f0e",
    "lightgbm": "#d62728",
    "mlp": "#9467bd"
}
MODEL_LABELS = {
    "logistic": "Logistic Regression",
    "random_forest": "Random Forest",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "mlp": "MLP Neural Net"
}

print("=== GENERATING FIGURES 1 THROUGH 5 ===")

# -------------------------------------------------------------
# Figure 1 & 2: Fairness-Specificity Pareto Frontiers (OOF grid curves + locked test points)
# -------------------------------------------------------------
df_pareto = pd.read_csv(TABLES_DIR / "fairness_specificity_pareto_results.csv")

# Figure 1: BMI Fairness vs Specificity
fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
for model in MODEL_PALETTE.keys():
    sub = df_pareto[(df_pareto["model"] == model) & (df_pareto["target_subgroup"] == "BMI_Normal")]
    if len(sub) > 0:
        row = sub.iloc[0]
        # Base point
        ax.scatter(row["baseline_specificity"] * 100, row["baseline_disparity"] * 100,
                   color=MODEL_PALETTE[model], marker='o', s=100, alpha=0.6, label=f"{MODEL_LABELS[model]} (Base)")
        # Constrained point
        ax.scatter(row["constrained_specificity"] * 100, row["constrained_disparity"] * 100,
                   color=MODEL_PALETTE[model], marker='^', s=140, label=f"{MODEL_LABELS[model]} (Fairness-Constrained)")
        # Draw arrow connecting base to constrained
        ax.annotate('', xy=(row["constrained_specificity"] * 100, row["constrained_disparity"] * 100),
                    xytext=(row["baseline_specificity"] * 100, row["baseline_disparity"] * 100),
                    arrowprops=dict(arrowstyle="->", color=MODEL_PALETTE[model], lw=1.8, ls="--"))

ax.axvline(x=75.0, color='gray', linestyle=':', label='Min Specificity Threshold (75%)')
ax.set_xlabel("Overall Test Specificity (%)", fontsize=12, fontweight='bold')
ax.set_ylabel("BMI Sensitivity Disparity (pp)", fontsize=12, fontweight='bold')
ax.set_title("Figure 1: BMI Sensitivity Disparity vs. Specificity Trade-Off", fontsize=14, fontweight='bold', pad=15)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.tight_layout()
fig.savefig(FIG_DIR / "figure1_bmi_fairness_vs_specificity_pareto.png", bbox_inches='tight')
plt.close(fig)

# Figure 2: Age Fairness vs Specificity
fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
for model in MODEL_PALETTE.keys():
    sub = df_pareto[(df_pareto["model"] == model) & (df_pareto["target_subgroup"] == "Age_60plus")]
    if len(sub) > 0:
        row = sub.iloc[0]
        ax.scatter(row["baseline_specificity"] * 100, row["baseline_disparity"] * 100,
                   color=MODEL_PALETTE[model], marker='o', s=100, alpha=0.6, label=f"{MODEL_LABELS[model]} (Base)")
        ax.scatter(row["constrained_specificity"] * 100, row["constrained_disparity"] * 100,
                   color=MODEL_PALETTE[model], marker='^', s=140, label=f"{MODEL_LABELS[model]} (Fairness-Constrained)")
        ax.annotate('', xy=(row["constrained_specificity"] * 100, row["constrained_disparity"] * 100),
                    xytext=(row["baseline_specificity"] * 100, row["baseline_disparity"] * 100),
                    arrowprops=dict(arrowstyle="->", color=MODEL_PALETTE[model], lw=1.8, ls="--"))

ax.axvline(x=75.0, color='gray', linestyle=':', label='Min Specificity Threshold (75%)')
ax.set_xlabel("Overall Test Specificity (%)", fontsize=12, fontweight='bold')
ax.set_ylabel("Age Sensitivity Disparity (pp)", fontsize=12, fontweight='bold')
ax.set_title("Figure 2: Age Sensitivity Disparity vs. Specificity Trade-Off", fontsize=14, fontweight='bold', pad=15)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.tight_layout()
fig.savefig(FIG_DIR / "figure2_age_fairness_vs_specificity_pareto.png", bbox_inches='tight')
plt.close(fig)

# -------------------------------------------------------------
# Figure 3: Coverage vs Mean Set Size (Conformal Trade-Off M1 to M4b)
# -------------------------------------------------------------
df_conf = pd.read_csv(TABLES_DIR / "conformal_tradeoff_comparison.csv")
METHOD_MARKERS = {
    "M1_global_baseline": "o",
    "M2_sequential_mondrian": "s",
    "M3_pure_joint_intersectional": "D",
    "M4b_shrinkage_intersectional": "*"
}
METHOD_NAMES = {
    "M1_global_baseline": "M1 (Global)",
    "M2_sequential_mondrian": "M2 (Sequential)",
    "M3_pure_joint_intersectional": "M3 (Pure Joint)",
    "M4b_shrinkage_intersectional": "M4b (Shrinkage N0=100)"
}

fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
for model in MODEL_PALETTE.keys():
    sub = df_conf[df_conf["model"] == model]
    ax.plot(sub["overall_mean_set_size"], sub["intersectional_coverage"] * 100,
            color=MODEL_PALETTE[model], alpha=0.5, ls='-', lw=1.5)
    for _, row in sub.iterrows():
        m_code = row["method"]
        ax.scatter(row["overall_mean_set_size"], row["intersectional_coverage"] * 100,
                   color=MODEL_PALETTE[model], marker=METHOD_MARKERS[m_code], s=120)

ax.axhline(y=90.0, color='crimson', linestyle='--', linewidth=2, label='Target Coverage (90%)')
ax.set_xlabel("Overall Mean Prediction Set Size", fontsize=12, fontweight='bold')
ax.set_ylabel("Intersectional Subgroup Coverage (%)", fontsize=12, fontweight='bold')
ax.set_title("Figure 3: Intersectional Coverage vs. Efficiency (Set Size) Trade-Off", fontsize=14, fontweight='bold', pad=15)

# Custom legend for methods and models
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], color=c, lw=2, label=MODEL_LABELS[m]) for m, c in MODEL_PALETTE.items()]
legend_elements.append(Line2D([0], [0], color='black', lw=0, label=''))
legend_elements.extend([Line2D([0], [0], marker=METHOD_MARKERS[m], color='black', lw=0, label=n, markersize=8) for m, n in METHOD_NAMES.items()])
legend_elements.append(Line2D([0], [0], color='crimson', lw=2, ls='--', label='90% Target'))

ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.tight_layout()
fig.savefig(FIG_DIR / "figure3_coverage_vs_set_size_tradeoff.png", bbox_inches='tight')
plt.close(fig)

# -------------------------------------------------------------
# Figure 4: M4b Shrinkage Sensitivity Plots (4-Panel Subplot)
# -------------------------------------------------------------
df_sens = pd.read_csv(TABLES_DIR / "m4b_shrinkage_sensitivity.csv")

fig, axes = plt.subplots(2, 2, figsize=(13, 10), dpi=300)

# Panel A: Coverage vs N0
for model in MODEL_PALETTE.keys():
    sub = df_sens[df_sens["model"] == model]
    axes[0, 0].plot(sub["N0"], sub["intersectional_coverage"] * 100, marker='o',
                    color=MODEL_PALETTE[model], label=MODEL_LABELS[model], lw=2)
axes[0, 0].axhline(y=90.0, color='crimson', linestyle='--', label='90% Target')
axes[0, 0].set_xlabel("Shrinkage Prior Weight (N0)", fontweight='bold')
axes[0, 0].set_ylabel("Intersectional Coverage (%)", fontweight='bold')
axes[0, 0].set_title("A. Intersectional Coverage vs. N0", fontweight='bold')
axes[0, 0].legend(fontsize=8)

# Panel B: Marginal Drift vs N0
for model in MODEL_PALETTE.keys():
    sub = df_sens[df_sens["model"] == model]
    axes[0, 1].plot(sub["N0"], sub["marginal_drift_pp"], marker='s',
                    color=MODEL_PALETTE[model], lw=2)
axes[0, 1].axhline(y=5.0, color='black', linestyle=':', label='+-5.0 pp Limit')
axes[0, 1].axhline(y=-5.0, color='black', linestyle=':')
axes[0, 1].set_xlabel("Shrinkage Prior Weight (N0)", fontweight='bold')
axes[0, 1].set_ylabel("Marginal Coverage Drift (pp)", fontweight='bold')
axes[0, 1].set_title("B. Marginal Drift vs. N0", fontweight='bold')
axes[0, 1].legend(fontsize=8)

# Panel C: Set Size vs N0
for model in MODEL_PALETTE.keys():
    sub = df_sens[df_sens["model"] == model]
    axes[1, 0].plot(sub["N0"], sub["mean_set_size"], marker='^',
                    color=MODEL_PALETTE[model], lw=2)
axes[1, 0].set_xlabel("Shrinkage Prior Weight (N0)", fontweight='bold')
axes[1, 0].set_ylabel("Mean Prediction Set Size", fontweight='bold')
axes[1, 0].set_title("C. Prediction Set Size vs. N0", fontweight='bold')

# Panel D: Pareto (Coverage vs Set Size across N0)
for model in MODEL_PALETTE.keys():
    sub = df_sens[df_sens["model"] == model]
    axes[1, 1].plot(sub["mean_set_size"], sub["intersectional_coverage"] * 100, marker='d',
                    color=MODEL_PALETTE[model], lw=2, label=MODEL_LABELS[model])
axes[1, 1].axhline(y=90.0, color='crimson', linestyle='--', label='90% Target')
axes[1, 1].set_xlabel("Mean Prediction Set Size", fontweight='bold')
axes[1, 1].set_ylabel("Intersectional Coverage (%)", fontweight='bold')
axes[1, 1].set_title("D. Coverage vs. Set Size Pareto across N0", fontweight='bold')
axes[1, 1].legend(fontsize=8)

plt.suptitle("Figure 4: M4b Precision-Weighted Shrinkage Sensitivity to N0", fontsize=15, fontweight='bold', y=0.99)
plt.tight_layout()
fig.savefig(FIG_DIR / "figure4_m4b_shrinkage_sensitivity.png", bbox_inches='tight')
plt.close(fig)

# -------------------------------------------------------------
# Figure 5: LightGBM Failure Diagnostic Comparisons
# -------------------------------------------------------------
df_lgbm = pd.read_csv(TABLES_DIR / "m4b_lightgbm_failure_analysis.csv")

fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
x_pos = np.arange(len(MODEL_PALETTE))
covs = [df_lgbm[df_lgbm["model"] == m]["test_intersectional_coverage_m4b"].values[0] * 100 for m in MODEL_PALETTE.keys()]
colors = [MODEL_PALETTE[m] for m in MODEL_PALETTE.keys()]

bars = ax.bar(x_pos, covs, color=colors, alpha=0.85, width=0.55)
ax.axhline(y=90.0, color='crimson', linestyle='--', linewidth=2, label='90.0% Success Target')
ax.set_xticks(x_pos)
ax.set_xticklabels([MODEL_LABELS[m] for m in MODEL_PALETTE.keys()], fontweight='bold')
ax.set_ylabel("Intersectional Test Coverage (%)", fontsize=12, fontweight='bold')
ax.set_ylim(75, 95)
ax.set_title("Figure 5: M4b Intersectional Coverage across Models (LightGBM Deficit Audit)", fontsize=13, fontweight='bold', pad=15)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{yval:.2f}%", ha='center', va='bottom', fontweight='bold')

ax.legend(loc='lower right')
plt.tight_layout()
fig.savefig(FIG_DIR / "figure5_lightgbm_failure_diagnostics.png", bbox_inches='tight')
plt.close(fig)

print("\n=== SUCCESS: FIGURES 1 THROUGH 5 GENERATED CLEANLY ===")
print("Saved to results/figures/")
