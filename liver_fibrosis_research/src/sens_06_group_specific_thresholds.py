"""
sens_06_group_specific_thresholds.py
Diagnostic Analysis 2 (Three-Diagnostics Protocol Freeze, 2026-08-25): group-specific Youden's J
decision thresholds vs. the existing global threshold.

SECONDARY / DIAGNOSTIC / SUPPLEMENTARY. Does not modify or replace any frozen Phase 1-8 result.

SUPERSEDES a prior same-named script found on 2026-08-25 that (a) omitted the frozen BMI-Underweight
category entirely, and (b) evaluated the "global threshold" baseline by applying a threshold derived
for RAW probabilities to RECALIBRATED test probabilities -- a scale mismatch that would make the
baseline comparison invalid. Documented in results/diagnostics/TEST_SET_CONTAMINATION_AUDIT.md.
That prior file/output is not used as a source for this implementation.

Reuses the project's exact existing Youden's J implementation
(src/phase3_06_threshold_and_test_eval.py: roc_curve + argmax(tpr-fpr)) and RAW predicted
probabilities throughout, matching the pairing already used for the project's own headline
confusion-matrix results (raw probability + raw-derived threshold).

FITTING DATA: OOF training predictions (results/predictions/validation_predictions_<model>.csv),
filtered per subgroup.
EVALUATION DATA: locked test set, using each subgroup's own frozen threshold.
TEST LABELS USED FOR FITTING: NO.
"""
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_curve

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
PRED_DIR = ROOT / "results" / "predictions"
DIAG_DIR = ROOT / "results" / "diagnostics"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
RUN_TS = datetime.now(timezone.utc).isoformat()


def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def youdens_j_threshold(y_true, y_proba):
    """Identical to src/phase3_06_threshold_and_test_eval.py's implementation."""
    fpr, tpr, thresh = roc_curve(y_true, y_proba)
    j = tpr - fpr
    return float(thresh[np.argmax(j)])


master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
test_df_master = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
if len(test_df_master) != 2146:
    raise SystemExit("FAIL: test partition size mismatch -- STOP, do not proceed")

global_thresholds = pd.read_csv(ROOT / "results" / "tables" / "phase3_threshold_selection.csv")
name_col = "model_name" if "model_name" in global_thresholds.columns else global_thresholds.columns[0]
thr_map = global_thresholds.set_index(name_col)["threshold"]

# Frozen subgroup definitions -- all categories, including Underweight (not dropped)
SUBGROUP_CONFIGS = [
    ("bmi", "bmi_group_final", ["Underweight", "Normal", "Overweight", "Obese"], "Normal"),
    ("age", "age_group_final", ["18-39", "40-59", "60+"], "40-59"),
]

cov_map = master.set_index("SEQN")[["bmi_group_final", "age_group_final"]]

rows = []
for model in MODEL_NAMES:
    oof = pd.read_csv(PRED_DIR / f"validation_predictions_{model}.csv").join(cov_map, on="SEQN")
    test = pd.read_csv(PRED_DIR / f"test_predictions_{model}.csv").join(cov_map, on="SEQN")
    global_thr = float(thr_map[model])

    for dim, col, categories, reference in SUBGROUP_CONFIGS:
        group_thresholds = {}
        for cat in categories:
            oof_sg = oof[oof[col] == cat]
            n_pos = int(oof_sg["true_target"].sum())
            n_neg = len(oof_sg) - n_pos
            if n_pos < 10 or n_neg < 10:
                # Frozen project precision_tier convention (src/phase5_common.py):
                # n_pos<10 or n_neg<10 = "insufficient evidence" -- flagged, not silently dropped,
                # and NOT used to derive a subgroup threshold; falls back to the global threshold.
                group_thresholds[cat] = (global_thr, "insufficient_evidence_fallback_to_global")
                continue
            thr = youdens_j_threshold(oof_sg["true_target"].values, oof_sg["predicted_probability"].values)
            group_thresholds[cat] = (thr, "oof_derived")

        for cat in categories:
            mask = test[col] == cat
            sub = test[mask]
            n = len(sub)
            n_pos = int(sub["true_target"].sum())
            n_neg = n - n_pos
            if n_pos == 0:
                continue
            thr_group, thr_source = group_thresholds[cat]

            yhat_global = (sub["predicted_probability"] >= global_thr).astype(int)
            yhat_group = (sub["predicted_probability"] >= thr_group).astype(int)
            y = sub["true_target"].values

            tp_g = int(((y == 1) & (yhat_global == 1)).sum()); tn_g = int(((y == 0) & (yhat_global == 0)).sum())
            fn_g = n_pos - tp_g; fp_g = n_neg - tn_g
            sens_g = tp_g / n_pos; spec_g = tn_g / n_neg if n_neg else None; fnr_g = fn_g / n_pos

            tp_s = int(((y == 1) & (yhat_group == 1)).sum()); tn_s = int(((y == 0) & (yhat_group == 0)).sum())
            fn_s = n_pos - tp_s; fp_s = n_neg - tn_s
            sens_s = tp_s / n_pos; spec_s = tn_s / n_neg if n_neg else None; fnr_s = fn_s / n_pos

            s_lo, s_hi = wilson_ci(tp_s, n_pos)
            g_lo, g_hi = wilson_ci(tp_g, n_pos)

            rows.append({
                "generated": RUN_TS, "model": model, "dimension": dim, "category": cat,
                "reference_group": reference,
                "n": n, "n_positive": n_pos, "n_negative": n_neg,
                "global_threshold": round(global_thr, 4),
                "group_threshold": round(thr_group, 4),
                "group_threshold_source": thr_source,
                "sensitivity_global_thresh": round(sens_g, 6),
                "sensitivity_global_thresh_ci_lower": round(g_lo, 6),
                "sensitivity_global_thresh_ci_upper": round(g_hi, 6),
                "sensitivity_group_thresh": round(sens_s, 6),
                "sensitivity_group_thresh_ci_lower": round(s_lo, 6),
                "sensitivity_group_thresh_ci_upper": round(s_hi, 6),
                "sensitivity_change_pp": round((sens_s - sens_g) * 100, 4),
                "specificity_global_thresh": round(spec_g, 6) if spec_g is not None else None,
                "specificity_group_thresh": round(spec_s, 6) if spec_s is not None else None,
                "fnr_global_thresh": round(fnr_g, 6),
                "fnr_group_thresh": round(fnr_s, 6),
                "tp_global": tp_g, "fp_global": fp_g, "tn_global": tn_g, "fn_global": fn_g,
                "tp_group": tp_s, "fp_group": fp_s, "tn_group": tn_s, "fn_group": fn_s,
                "sparse_cell": bool(n_pos < 10 or n_neg < 10),
                "probability_scale": "raw (uncalibrated) predicted_probability, matching the project's own headline threshold pairing",
                "fitting_test_labels_used": "NO",
            })

out = pd.DataFrame(rows)
out.to_csv(DIAG_DIR / "group_specific_threshold_metrics.csv", index=False)
print("Wrote group_specific_threshold_metrics.csv:", len(out), "rows")
print()
for model in MODEL_NAMES:
    sub = out[out["model"] == model][["dimension", "category", "n", "n_positive", "sensitivity_global_thresh", "sensitivity_group_thresh", "sensitivity_change_pp", "sparse_cell"]]
    print(f"--- {model} ---")
    print(sub.to_string(index=False))
