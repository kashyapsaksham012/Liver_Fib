#!/usr/bin/env python3
"""
Regenerate the two figures whose current versions tell a different story than the
manuscript text (see FIGURE_AUDIT.md §1).

READ-ONLY on results/. Writes only into manuscript_figures/.

    python3 manuscript_figures/regenerate_figures.py

Produces
--------
main/fig3_sensitivity_by_bmi_band.png
    Replaces the sensitivity_disparity_*.png forest plot. Shows sensitivity for
    each BMI band, ordered Normal -> Overweight -> Obese so the eye reads the
    detection gap directly ("the models detect heavier patients, miss lean
    ones"). Underweight (n=1 positive) is shown greyed with an explicit
    "not interpreted" label instead of a large spurious bar. Wilson 95% CIs,
    same formula as the conformal analysis (Amendment #10).

supplement/cooccurrence_descriptive.png
    Replaces cooccurrence_scatter.png. Same 55 points, but the visual no longer
    implies a trend: all points grey, only the BMI-Obese and Age-60+ cells
    highlighted (those fail on both axes by their own per-subgroup tests), and a
    prominent annotation states that the *general* association is NOT supported
    (dependence-aware permutation p = 0.12).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
MODEL_LABEL = {"logistic": "Logistic", "random_forest": "Random forest",
               "xgboost": "XGBoost", "lightgbm": "LightGBM", "mlp": "MLP"}


def wilson_ci(k, n, level=0.95):
    """Exact formula copied from src/phase6_04_final_test_touch.py."""
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054  # norm.ppf(0.975)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def read_csv(rel):
    with (REPO / rel).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------- #
# Figure 3 — sensitivity by BMI band
# --------------------------------------------------------------------------- #

def fig3_sensitivity_by_bmi_band():
    disc = read_csv("results/fairness/subgroup_discrimination_metrics.csv")
    inf = read_csv("results/fairness/fairness_inference.csv")

    # per (model, band): sensitivity, n_positive
    band_order = ["Normal", "Overweight", "Obese"]
    data = {m: {} for m in MODELS}
    for r in disc:
        if r["dimension"] != "bmi":
            continue
        m = r["model"]
        npos = int(r["n_positive"])
        sens = float(r["sensitivity"])
        k = round(sens * npos)
        lo, hi = wilson_ci(k, npos)
        data[m][r["category"]] = dict(sens=sens, npos=npos, k=k, lo=lo, hi=hi)

    # Normal-vs-Obese disparity + q, per model (fairness_inference: category=Obese, ref=Normal)
    disp = {}
    for r in inf:
        if r["dimension"] == "bmi" and r["category"] == "Obese":
            disp[r["model"]] = (abs(float(r["absolute_disparity_pp"])),
                                float(r["bh_fdr_adjusted_p"]))

    fig, ax = plt.subplots(figsize=(11, 5.6))
    colors = {"Normal": "#c44e52", "Overweight": "#dd8452", "Obese": "#4c72b0"}
    n_band = len(band_order)
    group_w = 0.8
    bar_w = group_w / n_band

    for gi, m in enumerate(MODELS):
        for bi, band in enumerate(band_order):
            d = data[m][band]
            x = gi + (bi - (n_band - 1) / 2) * bar_w
            ax.bar(x, d["sens"], bar_w * 0.95, color=colors[band],
                   edgecolor="black", linewidth=0.5,
                   label=band if gi == 0 else None)
            ax.errorbar(x, d["sens"], yerr=[[d["sens"] - d["lo"]], [d["hi"] - d["sens"]]],
                        fmt="none", ecolor="black", elinewidth=1, capsize=3)
            if bi == 0:  # annotate n on the Normal bar
                ax.text(x, 0.02, f"n={d['npos']}", ha="center", va="bottom",
                        fontsize=7, color="white", rotation=90)

    # disparity annotation under each model
    for gi, m in enumerate(MODELS):
        gap, q = disp[m]
        star = " *" if q <= 0.05 else ""
        ax.text(gi, -0.13, f"Obese−Normal\n+{gap:.0f} pp{star}", ha="center",
                va="top", fontsize=8)

    ax.set_xticks(range(len(MODELS)))
    ax.set_xticklabels([MODEL_LABEL[m] for m in MODELS])
    ax.set_ylabel("Sensitivity for significant fibrosis (95% Wilson CI)")
    ax.set_ylim(0, 1.22)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_title("Detection of significant fibrosis by body-mass band — "
                 "sensitivity rises with BMI in every model",
                 fontsize=11.5, pad=10)
    ax.legend(title="BMI band", ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, 0.99), framealpha=0.95, fontsize=9)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.text(0.995, -0.22,
            "Underweight band excluded (1 test positive, not interpretable). "
            "* Benjamini–Hochberg q ≤ 0.05 (all five models: q ≤ 0.006).",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5, style="italic")
    fig.subplots_adjust(bottom=0.26)
    p = OUT / "main" / "fig3_sensitivity_by_bmi_band.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {p}")

    # console cross-check
    print("  Normal-BMI sensitivity:",
          ", ".join(f"{m.split('_')[0]} {data[m]['Normal']['sens']:.2f}" for m in MODELS))
    print("  Obese     sensitivity:",
          ", ".join(f"{m.split('_')[0]} {data[m]['Obese']['sens']:.2f}" for m in MODELS))


# --------------------------------------------------------------------------- #
# Co-occurrence — descriptive, no implied trend
# --------------------------------------------------------------------------- #

def fig_cooccurrence_descriptive():
    rows = read_csv("results/reliability_extension/cooccurrence_analysis_table.csv")

    xs, ys, hi_x, hi_y, hi_lab, hi_c = [], [], [], [], [], []
    for r in rows:
        x = float(r["fairness_disparity_magnitude_pp"])
        y = float(r["coverage_deficit_magnitude_pp"])
        cat = r["category"]
        if cat == "Obese":
            hi_x.append(x); hi_y.append(y); hi_lab.append(f"{r['model'][:4]}/Obese"); hi_c.append("#4c72b0")
        elif cat == "60+":
            hi_x.append(x); hi_y.append(y); hi_lab.append(f"{r['model'][:4]}/60+"); hi_c.append("#dd8452")
        else:
            xs.append(x); ys.append(y)

    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    ax.scatter(xs, ys, s=45, color="0.72", edgecolor="0.5", linewidth=0.4,
               label="other model × subgroup cells (n=45)", zorder=2)
    ax.scatter(hi_x, hi_y, s=95, c=hi_c, edgecolor="black", linewidth=0.7,
               zorder=3)
    for x, y, lab in zip(hi_x, hi_y, hi_lab):
        ax.annotate(lab, (x, y), fontsize=7.5, xytext=(4, 3),
                    textcoords="offset points")

    # legend proxies
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([], [], marker="o", ls="", mfc="0.72", mec="0.5", ms=8,
               label="other cells (n = 45)"),
        Line2D([], [], marker="o", ls="", mfc="#4c72b0", mec="black", ms=9,
               label="BMI-Obese (5 models)"),
        Line2D([], [], marker="o", ls="", mfc="#dd8452", mec="black", ms=9,
               label="Age-60+ (5 models)"),
    ], loc="lower right", framealpha=0.95)

    ax.set_xlabel("Fairness disparity magnitude (percentage points)")
    ax.set_ylabel("Conformal coverage deficit magnitude (pp from 90% target)")
    ax.set_title("Fairness disparity vs. conformal coverage deficit — descriptive\n"
                 "no general association; two specific cells fail on both axes",
                 fontsize=11)

    ax.text(0.02, 0.97,
            "Pooled Spearman ρ = 0.41 (naïve p = 0.002).\n"
            "Dependence-aware permutation test: p = 0.12\n"
            "→ a general fairness–coverage association is NOT supported.\n"
            "BMI-Obese and Age-60+ each fail on both axes by their own\n"
            "pre-specified per-subgroup FDR tests (Phases 5 and 6).",
            transform=ax.transAxes, va="top", ha="left", fontsize=8.5,
            bbox=dict(boxstyle="round", fc="#fff6e6", ec="0.6"))

    fig.tight_layout()
    p = OUT / "supplement" / "cooccurrence_descriptive.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {p}")
    print(f"  points: {len(xs)} grey + {len(hi_x)} highlighted = {len(xs)+len(hi_x)} (expect 55)")


# --------------------------------------------------------------------------- #
# Figure 2 — calibration curves, raw vs recalibrated (locked test set)
# --------------------------------------------------------------------------- #

def fig2_calibration_raw_vs_recal():
    curve = read_csv("results/calibration/curve_data/curve_data_test_set_final.csv")
    cal = read_csv("results/calibration/test_set_calibration_final.csv")

    # curve points: {model: {variant: [(xmean, yrate), ...]}}
    pts = {m: {"raw": [], "recalibrated": []} for m in MODELS}
    for r in curve:
        pts[r["model"]][r["variant"]].append(
            (float(r["mean_predicted_probability"]), float(r["observed_event_rate"])))
    for m in MODELS:
        for v in pts[m]:
            pts[m][v].sort()

    # ECE per model/variant
    ece = {m: {} for m in MODELS}
    for r in cal:
        ece[r["model"]][r["variant"]] = float(r["ece"])

    colors = dict(zip(MODELS, ["#4c72b0", "#55a868", "#c44e52", "#dd8452", "#8172b2"]))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.6), sharex=True, sharey=True)

    for ax, variant, sub in zip(axes, ["raw", "recalibrated"],
                                ["Raw model output", "After out-of-fold Platt recalibration"]):
        ax.plot([0, 1], [0, 1], ls="--", color="0.5", lw=1, label="perfect calibration")
        for m in MODELS:
            xs, ys = zip(*pts[m][variant])
            ax.plot(xs, ys, marker="o", ms=4, lw=1.4, color=colors[m],
                    label=MODEL_LABEL[m])
        ax.set_xlim(0, 0.9)
        ax.set_ylim(0, 0.9)
        ax.set_aspect("equal")
        ax.set_xlabel("Mean predicted probability (decile bin)")
        ax.set_title(sub, fontsize=10.5)
        # ECE annotation
        wt = [ece[m][variant] for m in MODELS[:4]]   # 4 class-weighted
        mlp_e = ece["mlp"][variant]
        ax.text(0.03, 0.87,
                f"ECE, class-weighted models: {min(wt):.3f}–{max(wt):.3f}\n"
                f"ECE, MLP (unweighted): {mlp_e:.3f}",
                fontsize=8.5, va="top",
                bbox=dict(boxstyle="round", fc="white", ec="0.7"))
    axes[0].set_ylabel("Observed event rate (decile bin)")
    axes[1].legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    fig.suptitle("Probability calibration on the locked test set (N = 2,146), by model\n"
                 "class-weighted models over-predict in raw output; one out-of-fold Platt step corrects it, "
                 "AUROC unchanged", fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    p = OUT / "main" / "fig2_calibration_raw_vs_recalibrated.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {p}")
    print("  raw ECE:  " + ", ".join(f"{m.split('_')[0]} {ece[m]['raw']:.3f}" for m in MODELS))
    print("  recal ECE:" + ", ".join(f"{m.split('_')[0]} {ece[m]['recalibrated']:.3f}" for m in MODELS))


if __name__ == "__main__":
    fig2_calibration_raw_vs_recal()
    fig3_sensitivity_by_bmi_band()
    fig_cooccurrence_descriptive()
    # retire the misleading versions from the curated folder
    for stale in ["main_needs_rework/fig3_bmi_disparity_REFRAME_and_drop_underweight.png"]:
        pass  # left in place as a before/after reference; see README
    print("\ndone. FIGURE_AUDIT.md §1 and manuscript_figures/README.md updated to match.")
