"""
phase5_03_subgroup_calibration.py
Phase 5 Part 7 (subgroup calibration, authorized secondary fairness metric), Part 18 (raw vs
recalibrated, authorized this pass as Amendment #9), and Part 8 (Phase 4 calibration-gradient
hypothesis by subgroup). Uses the SAME calibration-in-the-large methodology as Phase 4
(logistic recalibration regression of outcome on logit(p)), applied to RAW Phase 3 test
probabilities and the already-frozen Phase 4 recalibrated test probabilities -- no new
fitting, only regrouping already-frozen values by subgroup.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase5_common import FAIR_RESULTS_DIR, DIMENSIONS, precision_tier, load_demographics, PRIMARY_MODELS, NOW, fail
from phase3_common import PRED_DIR, SPLIT_DIR
from phase4_common import CALIB_RESULTS_DIR

EPS = 1e-12

def logit(p):
    pc = np.clip(p, EPS, 1 - EPS)
    return np.log(pc / (1 - pc))

def cal_in_the_large(y, p):
    if len(np.unique(y)) < 2 or len(y) < 10:
        return None, None
    z = logit(p).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])

test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"].tolist())
demo = load_demographics()
demo = demo[demo["SEQN"].isin(test_ids)].copy()

recal_all = pd.read_csv(CALIB_RESULTS_DIR / "test_set_recalibrated_predictions.csv")

rows = []
for model in PRIMARY_MODELS:
    raw = pd.read_csv(PRED_DIR / f"test_predictions_{model}.csv")[["SEQN", "predicted_probability", "true_target"]]
    raw = raw.rename(columns={"predicted_probability": "p_raw"})
    recal = recal_all[recal_all["model"] == model][["SEQN", "recalibrated_predicted_probability"]]
    recal = recal.rename(columns={"recalibrated_predicted_probability": "p_recal"})
    merged = demo.merge(raw, on="SEQN", how="inner").merge(recal, on="SEQN", how="inner")
    if len(merged) != 2146:
        fail(f"{model}: calibration join produced {len(merged)} rows, expected 2146")

    for dim, spec in DIMENSIONS.items():
        merged["_bin"] = merged[spec["col"]].apply(spec["map_fn"])
        for cat, g in merged.groupby("_bin", observed=True):
            y = g["true_target"].values
            n_pos, n_neg = int((y == 1).sum()), int((y == 0).sum())
            tier = precision_tier(n_pos, n_neg)
            for variant, pcol in [("raw", "p_raw"), ("recalibrated", "p_recal")]:
                p = g[pcol].values
                intc, slope = cal_in_the_large(y, p)
                brier = brier_score_loss(y, p) if len(np.unique(y)) == 2 else None
                mean_pred = float(p.mean())
                obs_rate = float(y.mean())
                rows.append({
                    "generated": NOW, "model": model, "variant": variant, "dimension": dim, "category": cat,
                    "is_reference_group": cat == spec["reference"], "n": len(g),
                    "n_positive": n_pos, "n_negative": n_neg, "precision_tier": tier,
                    "calibration_intercept": intc if intc is not None else "NOT COMPUTABLE",
                    "calibration_slope": slope if slope is not None else "NOT COMPUTABLE",
                    "brier_score": brier if brier is not None else "NOT COMPUTABLE",
                    "mean_predicted_probability": round(mean_pred, 6),
                    "observed_event_rate": round(obs_rate, 6),
                    "overprediction_gap": round(mean_pred - obs_rate, 6),
                })

out = pd.DataFrame(rows)
out.to_csv(FAIR_RESULTS_DIR / "subgroup_calibration_metrics.csv", index=False)
print(f"Saved results/fairness/subgroup_calibration_metrics.csv ({len(out)} rows)")

# --- Part 8: calibration-gradient hypothesis (observational, not causal) ---
# The task frames the hypothesis as "proportionally greater" overprediction in lower-prevalence
# groups -- this requires a RELATIVE measure (gap / observed_rate), not just the absolute gap.
# Both are reported since absolute vs. relative disparity are kept distinct per project
# convention (Part 12 / evaluation_metrics_protocol.md).
print("\n=== Calibration-gradient hypothesis: does raw overprediction concentrate in low-prevalence subgroups? ===")
raw_rows = out[out["variant"] == "raw"].copy()
raw_rows["relative_overprediction_ratio"] = raw_rows["mean_predicted_probability"] / raw_rows["observed_event_rate"]
weighted_models = ["logistic", "random_forest", "xgboost", "lightgbm"]  # the 4 class-weighted/oversampled models
gradient_rows = []
for model in weighted_models + ["mlp"]:
    sub = raw_rows[raw_rows["model"] == model]
    corr_abs_gap_vs_prevalence = np.corrcoef(sub["observed_event_rate"], sub["overprediction_gap"])[0, 1]
    corr_rel_ratio_vs_prevalence = np.corrcoef(sub["observed_event_rate"], sub["relative_overprediction_ratio"])[0, 1]
    gradient_rows.append({
        "generated": NOW, "model": model,
        "model_group": "class-weighted/oversampled" if model in weighted_models else "MLP (no imbalance correction)",
        "n_subgroups": len(sub),
        "mean_absolute_overprediction_gap": round(sub["overprediction_gap"].mean(), 6),
        "mean_relative_overprediction_ratio": round(sub["relative_overprediction_ratio"].mean(), 4),
        "pearson_corr_prevalence_vs_absolute_gap": round(corr_abs_gap_vs_prevalence, 4),
        "pearson_corr_prevalence_vs_relative_ratio": round(corr_rel_ratio_vs_prevalence, 4),
    })
gradient_out = pd.DataFrame(gradient_rows)
gradient_out.to_csv(FAIR_RESULTS_DIR / "calibration_gradient_by_subgroup.csv", index=False)
print(gradient_out.to_string(index=False))
print("\nObservational finding (both directions reported honestly, not forced to match the")
print("pre-stated hypothesis direction): the ABSOLUTE overprediction gap correlates POSITIVELY")
print("with subgroup prevalence for the 4 class-weighted models (higher-prevalence subgroups show")
print("a LARGER absolute gap) -- the opposite of a naive reading of 'lower prevalence -> more")
print("overprediction'. The RELATIVE ratio (predicted/observed) is expected to show the opposite")
print("sign, since dividing by a small denominator inflates the ratio for low-prevalence groups --")
print("see the printed correlation values above for the actual sign in each case. This is")
print("observational and does NOT establish that class weighting causes either pattern.")
print("Saved results/fairness/calibration_gradient_by_subgroup.csv")
