"""
phase4_03_curves_and_ece.py
Phase 4 Part 15 (calibration curves) and Part 14 (ECE, secondary/supplementary metric).
Binning per frozen protocol §9: 10 equal-frequency (decile) bins of predicted probability.
Computed EXCLUSIVELY from the OOF tier -- the locked test set is not touched.
Bins are NOT altered after seeing curve shape (frozen decision, applied mechanically).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_common import (
    CALIB_FIG_DIR, CALIB_CURVE_DATA_DIR, CALIB_RESULTS_DIR,
    PRIMARY_MODELS, SENSITIVITY_MODEL, N_CALIBRATION_BINS,
    load_oof_predictions, NOW,
)

ece_rows = []

def compute_curve(name):
    df = load_oof_predictions(name)
    p = df["predicted_probability"].values
    y = df["true_target"].values
    n = len(df)

    # Equal-frequency (decile) bins, frozen protocol §9. duplicates="drop" only triggers if
    # probability values repeat heavily enough to prevent exactly 10 unique bin edges; if so,
    # this is reported explicitly (a diagnostic finding), not silently patched.
    try:
        bin_id, bin_edges = pd.qcut(p, q=N_CALIBRATION_BINS, retbins=True, duplicates="raise")
        n_bins_achieved = N_CALIBRATION_BINS
        degenerate = False
    except ValueError:
        bin_id, bin_edges = pd.qcut(p, q=N_CALIBRATION_BINS, retbins=True, duplicates="drop")
        n_bins_achieved = len(bin_edges) - 1
        degenerate = True

    curve_df = pd.DataFrame({"SEQN": df["SEQN"].values, "predicted_probability": p, "true_target": y, "bin": bin_id})
    agg = curve_df.groupby("bin", observed=True).agg(
        n_in_bin=("true_target", "size"),
        mean_predicted_probability=("predicted_probability", "mean"),
        observed_event_rate=("true_target", "mean"),
    ).reset_index(drop=True)
    agg.insert(0, "bin_index", range(1, len(agg) + 1))
    agg.insert(0, "model", name)
    agg["n_bins_requested"] = N_CALIBRATION_BINS
    agg["n_bins_achieved"] = n_bins_achieved
    agg["binning_degenerate"] = degenerate

    # ECE: sum over bins of (n_bin/N) * |mean_predicted - observed_rate|, same decile bins as the curve
    ece = float((agg["n_in_bin"] / n * (agg["mean_predicted_probability"] - agg["observed_event_rate"]).abs()).sum())

    return agg, ece, n_bins_achieved, degenerate

all_curve_data = []
for name in PRIMARY_MODELS + [SENSITIVITY_MODEL]:
    agg, ece, n_bins_achieved, degenerate = compute_curve(name)
    all_curve_data.append(agg)
    agg.to_csv(CALIB_CURVE_DATA_DIR / f"curve_data_{name}.csv", index=False)

    status = "PRIMARY" if name in PRIMARY_MODELS else "SENSITIVITY (MLP_balanced, not primary)"
    ece_rows.append({
        "generated": NOW, "model": name, "status": status,
        "data_source": "CV out-of-fold predictions (train partition, N=5007)",
        "ece_secondary_metric": round(ece, 6),
        "n_bins_requested": N_CALIBRATION_BINS, "n_bins_achieved": n_bins_achieved,
        "binning_degenerate": degenerate,
    })

    # Plot
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfect calibration")
    ax.plot(agg["mean_predicted_probability"], agg["observed_event_rate"], marker="o", label=name)
    for _, r in agg.iterrows():
        ax.annotate(f"n={int(r['n_in_bin'])}", (r["mean_predicted_probability"], r["observed_event_rate"]),
                    fontsize=7, textcoords="offset points", xytext=(4, 4))
    ax.set_xlabel("Mean predicted probability (decile bin)")
    ax.set_ylabel("Observed event rate (decile bin)")
    ax.set_title(f"Calibration curve (OOF) -- {name}" + (" [SENSITIVITY]" if name == SENSITIVITY_MODEL else ""))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(CALIB_FIG_DIR / f"calibration_curve_{name}.png", dpi=150)
    plt.close(fig)

pd.concat(all_curve_data, ignore_index=True).to_csv(CALIB_CURVE_DATA_DIR / "curve_data_all_models.csv", index=False)

ece_out = pd.DataFrame(ece_rows)
ece_out.to_csv(CALIB_RESULTS_DIR / "ece_secondary_metric.csv", index=False)
print(ece_out.to_string(index=False))
print(f"\nSaved {len(PRIMARY_MODELS)+1} calibration curve plots to results/calibration/figures/")
print(f"Saved underlying binned data to results/calibration/curve_data/ (per-model + combined)")
print("Saved results/calibration/ece_secondary_metric.csv")
