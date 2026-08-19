"""
phase5_06_figures.py
Phase 5 Part 22: figures + underlying figure data. One forest plot per model: sensitivity
disparity (subgroup - reference) with 95% bootstrap CI, from the already-computed
fairness_inference.csv (no new test-set computation -- purely a visualization of existing
results).
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase5_common import FAIR_RESULTS_DIR, FAIR_FIG_DIR, FAIR_CURVE_DATA_DIR, PRIMARY_MODELS, NOW

inf = pd.read_csv(FAIR_RESULTS_DIR / "fairness_inference.csv")
plot_data_all = []

for model in PRIMARY_MODELS:
    sub = inf[(inf["model"] == model) & (inf["absolute_disparity_pp"] != "NOT COMPUTABLE")].copy()
    sub["absolute_disparity_pp"] = sub["absolute_disparity_pp"].astype(float)
    sub["ci_lower_pp"] = pd.to_numeric(sub["ci_lower_pp"], errors="coerce")
    sub["ci_upper_pp"] = pd.to_numeric(sub["ci_upper_pp"], errors="coerce")
    sub = sub.dropna(subset=["ci_lower_pp", "ci_upper_pp"])
    sub["label"] = sub["dimension"] + ": " + sub["category"]
    sub = sub.sort_values("absolute_disparity_pp")
    plot_data_all.append(sub.assign(model=model))

    fig, ax = plt.subplots(figsize=(7, max(3, 0.4 * len(sub))))
    y_pos = range(len(sub))
    colors = ["#c0392b" if s else "#7f8c8d" for s in sub["significant_after_fdr_0.05"]]
    ax.errorbar(sub["absolute_disparity_pp"], y_pos,
                xerr=[sub["absolute_disparity_pp"] - sub["ci_lower_pp"], sub["ci_upper_pp"] - sub["absolute_disparity_pp"]],
                fmt="o", ecolor="gray", capsize=3, markerfacecolor="none")
    for i, c in zip(y_pos, colors):
        ax.plot(sub["absolute_disparity_pp"].iloc[i], i, "o", color=c)
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.axvline(10, color="orange", linestyle=":", linewidth=1, label="+/-10pp meaningful-difference threshold")
    ax.axvline(-10, color="orange", linestyle=":", linewidth=1)
    ax.set_yticks(list(y_pos)); ax.set_yticklabels(sub["label"], fontsize=8)
    ax.set_xlabel("Sensitivity disparity (percentage points, subgroup - reference)")
    ax.set_title(f"Sensitivity disparity by subgroup -- {model} (locked test set)\nred = significant after FDR (0.05); gray = not significant")
    ax.legend(loc="lower right", fontsize=7)
    fig.tight_layout()
    fig.savefig(FAIR_FIG_DIR / f"sensitivity_disparity_{model}.png", dpi=150)
    plt.close(fig)

pd.concat(plot_data_all, ignore_index=True).to_csv(FAIR_CURVE_DATA_DIR / "sensitivity_disparity_plot_data.csv", index=False)
print(f"Saved {len(PRIMARY_MODELS)} forest plots to results/fairness/figures/")
print("Saved results/fairness/curve_data/sensitivity_disparity_plot_data.csv")
