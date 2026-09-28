"""
phase6_07_figures.py
Phase 6: coverage figures. Purely visualizes already-frozen, saved outputs from Commit C --
does not reopen the raw test set.
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, MODEL_NAMES

RESULTS_DIR = ROOT / "results" / "uncertainty"
FIG_DIR = RESULTS_DIR / "figures"
subgroup = pd.read_csv(RESULTS_DIR / "subgroup_coverage.csv")
marginal = pd.read_csv(RESULTS_DIR / "marginal_coverage_test_set.csv")

for model in MODEL_NAMES:
    sub = subgroup[subgroup["model"] == model].sort_values("empirical_coverage")
    sub["label"] = sub["dimension"] + ": " + sub["category"]
    fig, ax = plt.subplots(figsize=(7, max(3, 0.35 * len(sub))))
    y_pos = range(len(sub))
    colors = ["#c0392b" if e else "#7f8c8d" for e in sub["ci_excludes_target"]]
    ax.errorbar(sub["empirical_coverage"], y_pos,
                xerr=[sub["empirical_coverage"] - sub["ci_lower"], sub["ci_upper"] - sub["empirical_coverage"]],
                fmt="none", ecolor="gray", capsize=3)
    for i, c in zip(y_pos, colors):
        ax.plot(sub["empirical_coverage"].iloc[i], i, "o", color=c)
    ax.axvline(0.90, color="black", linestyle="--", linewidth=1, label="90% target")
    marg = marginal[marginal["model"] == model]["empirical_coverage"].iloc[0]
    ax.axvline(marg, color="blue", linestyle=":", linewidth=1, label=f"marginal ({marg:.3f})")
    ax.set_yticks(list(y_pos)); ax.set_yticklabels(sub["label"], fontsize=8)
    ax.set_xlabel("Empirical conformal coverage (95% Wilson CI)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.14), ncol=2, fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"subgroup_coverage_{model}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

print(f"Saved {len(MODEL_NAMES)} subgroup coverage figures to results/uncertainty/figures/")
