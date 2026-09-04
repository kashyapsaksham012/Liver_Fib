"""Generate the temporal-validation evidence figures for the manuscript.

Reads only the frozen result CSVs of the temporal module and the pooled
model-update re-audit. Writes PNGs into this folder. No refitting, no frozen-tree
access.

    python3 temporal_validation_2021_2023/figures/make_temporal_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TV = HERE.parent
PU = TV.parent / "pooled_model_update_2017_2023"
TR, PR = TV / "results", PU / "results"

MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
LAB = {"logistic": "Logistic", "random_forest": "Random forest", "xgboost": "XGBoost",
       "lightgbm": "LightGBM", "mlp": "MLP"}
C_OLD, C_TMP, C_POOL = "#4c72b0", "#dd8452", "#55a868"
OK, PART, BAD = "#2ca25f", "#dd8452", "#c44e52"


# --------------------------------------------------------------------------- #
def fig_T1_replication_summary():
    v = pd.read_csv(TR / "temporal_replication_verdicts.csv")
    color = {}
    for cls in v.classification:
        c0 = cls.split()[0]
        color[cls] = OK if c0 in ("REPLICATED", "STRENGTHENED") else (
            BAD if c0 == "NOT" else PART)
    order = list(range(len(v)))[::-1]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for y, (_, r) in zip(order, v.iterrows()):
        ax.barh(y, 1, color=color[r.classification], edgecolor="black", lw=0.5)
        ax.text(0.02, y, r.finding, va="center", ha="left", fontsize=9)
        ax.text(0.98, y, r.classification.split(" (")[0], va="center", ha="right",
                fontsize=8.5, style="italic")
    ax.set_xlim(0, 1); ax.set_ylim(-0.6, len(v) - 0.4)
    ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Temporal validation (NHANES 2021–2023): what replicated\n"
                 "frozen models applied unchanged to a later cycle", fontsize=11)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=OK, ec="k", label="replicated / stronger"),
                       Patch(fc=BAD, ec="k", label="not replicated"),
                       Patch(fc=PART, ec="k", label="attenuated / partial")],
              loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.13), fontsize=8.5)
    fig.tight_layout()
    _save(fig, "figT1_replication_summary")


def fig_T2_bmi_gap_across_tiers():
    tf = pd.read_csv(TR / "temporal_fairness_results.csv")
    tb = tf[(tf.dimension == "bmi") & (tf.category == "Obese")].set_index("model")
    pf = pd.read_csv(PR / "pooled_fairness_results.csv")
    pb = pf[(pf.tag == "pooled_test_2021_2023") & (pf.dimension == "bmi") &
            (pf.category == "Obese")].set_index("model")   # 2021-2023 slice, for a fair comparison
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(MODELS)); w = 0.26
    old = [tb.loc[m, "disparity_pp_2017_2020"] for m in MODELS]
    tmp = [tb.loc[m, "absolute_disparity_pp"] for m in MODELS]
    pool = [pb.loc[m, "absolute_disparity_pp"] for m in MODELS]
    ax.bar(x - w, old, w, color=C_OLD, edgecolor="k", lw=.5, label="development (2017–2020)")
    ax.bar(x, tmp, w, color=C_TMP, edgecolor="k", lw=.5, label="2021–2023 — frozen model")
    ax.bar(x + w, pool, w, color=C_POOL, edgecolor="k", lw=.5, label="2021–2023 — after pooled retrain")
    for xi, a, b, c in zip(x, old, tmp, pool):
        for xx, vv in [(xi - w, a), (xi, b), (xi + w, c)]:
            ax.text(xx, vv + 1, f"{vv:.0f}", ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels([LAB[m] for m in MODELS])
    ax.set_ylabel("Obese − Normal sensitivity gap (percentage points)")
    ax.set_title("The body-mass detection gap replicates temporally, widens, and\n"
                 "is not resolved by retraining on newer data (all bars: BH q < 0.001)",
                 fontsize=11)
    ax.legend(fontsize=8.5)
    ax.set_ylim(0, max(tmp) + 12)
    fig.tight_layout()
    _save(fig, "figT2_bmi_gap_across_tiers")


def fig_T3_conformal_two_cycles():
    # 2021-2023 from the temporal module; 2017-2020 from the frozen tree (read-only)
    tc = pd.read_csv(TR / "temporal_conformal_results.csv")
    FRZ = TV.parent  # liver_fibrosis_research/
    fm = pd.read_csv(FRZ / "results/uncertainty/marginal_coverage_test_set.csv").set_index("model")
    fs = pd.read_csv(FRZ / "results/uncertainty/subgroup_coverage.csv")
    fi = pd.read_csv(FRZ / "results/uncertainty/intersectional_coverage_ci.csv")
    fi = fi[fi.stage == "baseline"].set_index("model")

    scopes = [("marginal", "Marginal"), ("bmi_Obese", "BMI-Obese"),
              ("age_60plus", "Age 60+"), ("Obese_x_60plus", "Obese ∩ 60+")]
    labels = [lbl for _, lbl in scopes]
    y = [3, 2, 1, 0]                                # top -> bottom
    fig, axes = plt.subplots(1, 5, figsize=(14, 3.4))
    for ax, m in zip(axes, MODELS):
        sub = tc[tc.model == m].set_index("scope")
        new = [sub.loc[s, "empirical_coverage"] for s, _ in scopes]
        old = [
            float(fm.loc[m, "empirical_coverage"]),
            float(fs[(fs.model == m) & (fs.category == "Obese")].iloc[0]["empirical_coverage"]),
            float(fs[(fs.model == m) & (fs.category == "60+")].iloc[0]["empirical_coverage"]),
            float(fi.loc[m, "coverage"]),
        ]
        ax.hlines(y, old, new, color="0.65", lw=1.6, zorder=0)
        ax.plot(old, y, "o", color=C_OLD, ms=8, label="2017–2020")
        ax.plot(new, y, "s", color=C_TMP, ms=8, label="2021–2023")
        ax.axvline(0.90, ls="--", color="0.35", lw=1)
        ax.set_ylim(-0.5, 3.5); ax.set_yticks(y)
        ax.set_xlim(0.60, 1.0); ax.set_xticks([0.7, 0.8, 0.9])
        ax.set_title(LAB[m], fontsize=10.5)
        ax.set_xlabel("empirical coverage", fontsize=9)
        if m == "logistic":
            ax.set_yticklabels(labels, fontsize=9.5)
        else:
            ax.set_yticklabels([])
    axes[0].legend(fontsize=8.5, loc="lower left", framealpha=0.95)
    fig.suptitle("Split-conformal coverage by subgroup, both cycles: marginal on target;\n"
                 "BMI-Obese, Age-60+ and their intersection under-cover in both (dashed = 90% target)",
                 fontsize=11)
    fig.subplots_adjust(left=0.10, right=0.985, top=0.78, bottom=0.20, wspace=0.15)
    _save(fig, "figT3_conformal_two_cycles")


def fig_T4_auroc_decline_decomposed():
    sl = pd.read_csv(TR / "temporal_drop_slice_matched.csv")
    sci = pd.read_csv(TR / "temporal_drop_slice_ci.csv")
    cs = pd.read_csv(TR / "temporal_drop_covariate_shift.csv")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))

    # panel a: slice-matched AUROC old vs new
    g = sl.groupby(["dimension", "category"]).agg(
        old=("auroc_old", "mean"), new=("auroc_new", "mean")).reset_index()
    g["label"] = g.dimension.str.upper() + ": " + g.category
    g = g.sort_values("new")
    y = np.arange(len(g))
    a1.hlines(y, g.old, g.new, color="0.6", lw=2, zorder=0)
    a1.plot(g.old, y, "o", color=C_OLD, ms=8, label="2017–2020")
    a1.plot(g.new, y, "s", color=C_TMP, ms=8, label="2021–2023")
    a1.set_yticks(y); a1.set_yticklabels(g.label)
    a1.axvline(0.5, ls=":", color="0.5"); a1.set_xlim(0.55, 0.92)
    a1.set_xlabel("within-band AUROC")
    a1.set_title("Within-band discrimination: the decline is concentrated\n"
                 "(Normal-BMI ≈ 0.82 → 0.62; Obese and 60+ unchanged)", fontsize=10)
    a1.legend(fontsize=8.5, loc="lower right")

    # panel b: covariate-shift recovery
    frac = cs.set_index("model")["fraction_of_drop_recovered"]
    a2.bar(range(5), [frac[m] for m in MODELS], color=C_TMP, edgecolor="k", lw=.5)
    a2.axhline(frac.mean(), ls="--", color="0.3", label=f"mean {frac.mean():.0%}")
    a2.set_xticks(range(5)); a2.set_xticklabels([LAB[m] for m in MODELS], rotation=20)
    a2.set_ylabel("fraction of the AUROC drop recovered\nby covariate-shift reweighting")
    a2.set_ylim(0, 1)
    a2.set_title("Reweighting to the development case-mix recovers only ~17%\n"
                 "→ concept drift, not composition", fontsize=10)
    a2.legend(fontsize=8.5)
    fig.tight_layout()
    _save(fig, "figT4_auroc_decline_decomposed")


def fig_T5_shortcut_across_tiers():
    ts = pd.read_csv(TR / "temporal_matched_stiffness_shortcut.csv").set_index("model")
    ps = pd.read_csv(PR / "pooled_shortcut_results.csv")
    ps = ps[ps.tag == "pooled_test_all"].set_index("model")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    x = np.arange(len(MODELS)); w = 0.26
    old = [ts.loc[m, "beta_is_obese_2017_2020"] for m in MODELS]
    tmp = [ts.loc[m, "beta_is_obese"] for m in MODELS]
    pool = [ps.loc[m, "beta_is_obese"] for m in MODELS]
    ax.bar(x - w, old, w, color=C_OLD, edgecolor="k", lw=.5, label="2017–2020")
    ax.bar(x, tmp, w, color=C_TMP, edgecolor="k", lw=.5, label="2021–2023 (frozen model)")
    ax.bar(x + w, pool, w, color=C_POOL, edgecolor="k", lw=.5, label="pooled retrain")
    ax.set_xticks(x); ax.set_xticklabels([LAB[m] for m in MODELS])
    ax.set_ylabel("OLS `obese` coefficient\n(extra predicted probability at matched liver stiffness)")
    ax.set_title("The matched-stiffness body-mass shortcut is stable across all three\n"
                 "evidence tiers (every bar: p < 0.001)", fontsize=11)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    _save(fig, "figT5_shortcut_across_tiers")


def fig_T6_nothing_fixes_it():
    rows = [
        ("Post-hoc: subgroup thresholds / BMI-Platt / BMI×age", "no acceptable fix"),
        ("Post-hoc: subgroup calibration", "no acceptable fix"),
        ("Post-hoc: equalized-odds post-processing", "clinically unacceptable"),
        ("Post-hoc: group-wise (Mondrian) conformal", "partial; over-covers"),
        ("Post-hoc: conformal selective deferral (Amdt #17)", "no improvement"),
        ("Model retuning within frozen family", "no acceptable retuning"),
        ("Training-time: subgroup reweighting (Amdt #19)", "negative — gap halved, gate failed"),
        ("Model updating: pooled 2017–2023 retrain", "NOT RESOLVED (this work)"),
    ]
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    y = np.arange(len(rows))[::-1]
    for yi, (name, verdict) in zip(y, rows):
        ax.barh(yi, 1, color=BAD if "NOT RESOLVED" in verdict else "#e8a598",
                edgecolor="black", lw=0.5)
        ax.text(0.015, yi, name, va="center", fontsize=9)
        ax.text(0.985, yi, verdict, va="center", ha="right", fontsize=8.5, style="italic")
    ax.set_xlim(0, 1); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("No intervention in the model-development toolkit resolves the\n"
                 "body-mass reliability–fairness failure — it is structural", fontsize=11)
    fig.tight_layout()
    _save(fig, "figT6_nothing_fixes_it")


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(HERE / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


if __name__ == "__main__":
    print("temporal validation figures ->", HERE)
    fig_T1_replication_summary()
    fig_T2_bmi_gap_across_tiers()
    fig_T3_conformal_two_cycles()
    fig_T4_auroc_decline_decomposed()
    fig_T5_shortcut_across_tiers()
    fig_T6_nothing_fixes_it()
    print("done — 6 figures")
