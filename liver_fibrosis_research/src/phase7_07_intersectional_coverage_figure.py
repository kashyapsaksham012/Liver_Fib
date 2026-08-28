"""
phase7_07_intersectional_coverage_figure.py
Visualization ONLY. Draws one manuscript figure from the already-frozen, authoritative
artifact:

    results/uncertainty/intersectional_coverage_ci.csv

-- empirical split-conformal coverage for the pre-specified BMI-obese AND age-60+
intersection cell (N = 294), all five model families, at the 90% target, before and
after the frozen group-wise (Mondrian) recalibration. Grouped bar chart.

This script re-runs nothing, loads no model, reopens no test data, computes no coverage,
and changes no result. Every value plotted is read verbatim from the CSV. It is the
intersectional-cell companion to phase6_07_figures.py (which plots the one-dimensional
subgroup coverage but not the joint cell).

CSV lineage (for the methods / caption):
  stage == baseline        : raw refit-model probabilities + the frozen global
                             split-conformal threshold, re-partitioned to the joint
                             cell by src/phase7_05_bmi_age_overlap_analysis.py from the
                             frozen Phase-6 artifact
                             results/uncertainty/test_set_prediction_sets.csv
                             (written by src/phase6_04_final_test_touch.py; NO Platt
                             recalibration). Authority: AUTHORITATIVE (descriptive) --
                             documentation/final_research_audit/AUTHORITATIVE_RESULTS.md A7.
  stage == post_mitigation : the frozen Phase-7 FDR-gated Mondrian recalibration.

Produces:
  results/uncertainty/figures/intersectional_coverage_by_model.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "results" / "uncertainty" / "intersectional_coverage_ci.csv"
FIG_DIR = ROOT / "results" / "uncertainty" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
OUT = FIG_DIR / "intersectional_coverage_by_model.png"

TARGET = 0.90
MODEL_ORDER = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
MODEL_LABEL = {
    "logistic": "Logistic\nregression",
    "random_forest": "Random\nforest",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "mlp": "MLP",
}
STAGE = {
    "baseline": dict(label="Global split-conformal (baseline)", color="#1f2a44"),
    "post_mitigation": dict(label="After group-wise (Mondrian) recalibration", color="#c47f17"),
}


def main():
    df = pd.read_csv(CSV)
    n_cell = int(df["n"].iloc[0])

    x = np.arange(len(MODEL_ORDER))
    w = 0.38

    fig, ax = plt.subplots(figsize=(9.0, 5.2), dpi=300)

    for k, (stage, st) in enumerate(STAGE.items()):
        offs = (k - 0.5) * w
        cov, lo_err, hi_err, labels = [], [], [], []
        for model in MODEL_ORDER:
            r = df[(df["model"] == model) & (df["stage"] == stage)].iloc[0]
            cov.append(r["coverage"])
            lo_err.append(r["coverage"] - r["ci_lower"])
            hi_err.append(r["ci_upper"] - r["coverage"])
            labels.append(f"{r['coverage']:.3f}")
        bars = ax.bar(x + offs, cov, w, color=st["color"], label=st["label"],
                      edgecolor="white", linewidth=0.6, zorder=2)
        ax.errorbar(x + offs, cov, yerr=[lo_err, hi_err], fmt="none",
                    ecolor="#333333", elinewidth=1.2, capsize=3, zorder=3)
        for xi, c, lab in zip(x + offs, cov, labels):
            ax.annotate(lab, (xi, c), textcoords="offset points", xytext=(0, 3),
                        ha="center", va="bottom", fontsize=7.5, color=st["color"])

    ax.axhline(TARGET, color="#c0392b", ls="--", lw=1.8, zorder=4, label="90% target")
    ax.axhspan(0, TARGET, color="#c0392b", alpha=0.045, zorder=0)

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABEL[m] for m in MODEL_ORDER])
    ax.set_ylim(0, 1.0)
    ax.set_yticks(np.arange(0, 1.01, 0.1))
    ax.set_ylabel("Empirical conformal coverage of the intersection cell\n"
                  f"(BMI-obese ∩ age-60+, N = {n_cell}); target 0.90", fontsize=9.5)
    ax.set_title("Intersectional split-conformal test-set coverage, five model families",
                 fontsize=11, pad=9)
    ax.grid(axis="y", ls=":", alpha=0.4, zorder=0)
    ax.set_axisbelow(True)

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=8,
              framealpha=0.95)

    fig.text(0.5, -0.04,
             "Error bars: 95% Wilson score intervals. All values verbatim from "
             "results/uncertainty/intersectional_coverage_ci.csv "
             "(frozen Phase-6 raw-probability split conformal; no recomputation).",
             ha="center", fontsize=6.8, color="#666666")

    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUT.relative_to(ROOT)}")
    print(df[["model", "stage", "n", "n_covered", "coverage", "ci_lower", "ci_upper"]]
          .to_string(index=False))


if __name__ == "__main__":
    main()
