"""
phase3_07_plots_and_comparison.py
Phase 3, Parts 25-26 - ROC/PR curves (per model + combined comparison) and paired
bootstrap AUC-difference model comparisons on the identical locked test set. The
comparison method (paired bootstrap, since predictions are correlated -- same test
participants for every model) is fixed here, before interpreting any result, and is
NOT selected after seeing which method yields significance.

Produces:
  results/figures/phase3_roc_<model>.png
  results/figures/phase3_pr_<model>.png
  results/figures/phase3_roc_combined.png
  results/figures/phase3_pr_combined.png
  results/tables/phase3_model_comparison.csv
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve, roc_auc_score
from itertools import combinations

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import PRED_DIR, FIG_DIR, TAB_DIR, RANDOM_SEED, MODEL_NAMES

N_BOOTSTRAP = 2000
COLORS = {"logistic": "#1E88E5", "random_forest": "#43A047", "xgboost": "#E53935",
         "lightgbm": "#FB8C00", "mlp": "#8E24AA"}

def main():
    print("=== Phase 3, Parts 25-26: ROC/PR Curves & Model Comparison ===")
    preds = {name: pd.read_csv(PRED_DIR / f"test_predictions_{name}.csv") for name in MODEL_NAMES}

    fig, ax = plt.subplots(figsize=(7, 6))
    for name, d in preds.items():
        fpr, tpr, _ = roc_curve(d["true_target"], d["predicted_probability"])
        auc = roc_auc_score(d["true_target"], d["predicted_probability"])
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})", color=COLORS[name])

        fig_i, ax_i = plt.subplots(figsize=(6, 5.5))
        ax_i.plot(fpr, tpr, color=COLORS[name])
        ax_i.plot([0, 1], [0, 1], "k--", alpha=0.3)
        ax_i.set_xlabel("False Positive Rate"); ax_i.set_ylabel("True Positive Rate")
        ax_i.set_title(f"ROC Curve - {name} (locked test set, N={len(d)}, AUC={auc:.3f})")
        plt.tight_layout(); fig_i.savefig(FIG_DIR / f"phase3_roc_{name}.png", dpi=150); plt.close(fig_i)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves - All Models (locked test set, N=2,146)")
    ax.legend(loc="lower right")
    plt.tight_layout(); fig.savefig(FIG_DIR / "phase3_roc_combined.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    prevalence = preds["logistic"]["true_target"].mean()
    for name, d in preds.items():
        prec, rec, _ = precision_recall_curve(d["true_target"], d["predicted_probability"])
        ax.plot(rec, prec, label=name, color=COLORS[name])

        fig_i, ax_i = plt.subplots(figsize=(6, 5.5))
        ax_i.plot(rec, prec, color=COLORS[name])
        ax_i.axhline(prevalence, color="grey", linestyle="--", alpha=0.5, label=f"prevalence={prevalence:.3f}")
        ax_i.set_xlabel("Recall"); ax_i.set_ylabel("Precision")
        ax_i.set_title(f"PR Curve - {name} (locked test set)")
        ax_i.legend()
        plt.tight_layout(); fig_i.savefig(FIG_DIR / f"phase3_pr_{name}.png", dpi=150); plt.close(fig_i)
    ax.axhline(prevalence, color="grey", linestyle="--", alpha=0.5, label=f"prevalence baseline={prevalence:.3f}")
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curves - All Models (locked test set)")
    ax.legend(loc="upper right")
    plt.tight_layout(); fig.savefig(FIG_DIR / "phase3_pr_combined.png", dpi=150); plt.close(fig)
    print("  Saved 5 individual ROC + 5 individual PR curves, plus combined comparison plots.")

    # ── Part 26: paired bootstrap AUC-difference comparison (predefined method) ─────────
    rng = np.random.RandomState(RANDOM_SEED)
    y_true = preds["logistic"]["true_target"].values  # identical across all models (same test set)
    n = len(y_true)
    boot_idx = [rng.randint(0, n, n) for _ in range(N_BOOTSTRAP)]

    boot_aucs = {}
    for name, d in preds.items():
        proba = d["predicted_probability"].values
        vals = []
        for idx in boot_idx:
            yt, ys = y_true[idx], proba[idx]
            if len(np.unique(yt)) < 2:
                continue
            vals.append(roc_auc_score(yt, ys))
        boot_aucs[name] = np.array(vals)

    comp_rows = []
    pairs = list(combinations(MODEL_NAMES, 2))
    raw_p = []
    for a, b in pairs:
        diffs = boot_aucs[a][:min(len(boot_aucs[a]), len(boot_aucs[b]))] - boot_aucs[b][:min(len(boot_aucs[a]), len(boot_aucs[b]))]
        obs_diff = roc_auc_score(y_true, preds[a]["predicted_probability"]) - roc_auc_score(y_true, preds[b]["predicted_probability"])
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        p_two_sided = 2 * min((diffs <= 0).mean(), (diffs >= 0).mean())
        raw_p.append(p_two_sided)
        comp_rows.append({"model_a": a, "model_b": b, "auc_diff_a_minus_b": round(obs_diff, 4),
                         "diff_95ci_low": round(lo, 4), "diff_95ci_high": round(hi, 4),
                         "raw_p_value_bootstrap": round(p_two_sided, 4),
                         "ci_excludes_zero": bool(lo > 0 or hi < 0)})
    # Benjamini-Hochberg FDR across this comparison family (consistent with multiple_comparisons_protocol.md's approach)
    m = len(raw_p)
    order = np.argsort(raw_p)
    ranked = np.array(raw_p)[order]
    bh = ranked * m / (np.arange(m) + 1)
    bh_sorted = np.minimum.accumulate(bh[::-1])[::-1]
    fdr_adj = np.empty(m); fdr_adj[order] = np.minimum(bh_sorted, 1.0)
    for i, row in enumerate(comp_rows):
        row["fdr_adjusted_p_value"] = round(fdr_adj[i], 4)
        row["significant_after_fdr_0.05"] = bool(fdr_adj[i] < 0.05)

    comp_df = pd.DataFrame(comp_rows)
    comp_df.to_csv(TAB_DIR / "phase3_model_comparison.csv", index=False)
    print(f"\n  Model comparison ({len(pairs)} pairs, paired bootstrap n={N_BOOTSTRAP}, FDR-corrected):")
    print(comp_df[["model_a", "model_b", "auc_diff_a_minus_b", "ci_excludes_zero", "significant_after_fdr_0.05"]].to_string(index=False))
    print("\n  NOTE: statistically detectable AUC differences here are NOT automatically 'clinically meaningful' "
          "-- no clinical-utility claim is made from discrimination alone (Phase 3 scope boundary).")
    print("[ROC/PR CURVES & MODEL COMPARISON COMPLETE]")

if __name__ == "__main__":
    main()
