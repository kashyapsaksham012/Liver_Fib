"""
phase5_02_subgroup_discrimination.py
Phase 5 Part 6: subgroup discrimination + error-rate metrics on the LOCKED TEST SET, using
RAW Phase 3 probabilities and the frozen, model-specific Youden's J threshold (never
subgroup-optimized). Part of the single, first-and-only Fairness test-set touch (executed
together with phase5_03/04/05 in one coordinated pass, per Part 21).

Metrics: ROC-AUC (threshold-free), sensitivity, specificity, FNR, FPR at the frozen threshold
-- exactly the frozen protocol's per-subgroup metric list (evaluation_metrics_protocol.md).
PPV/NPV are deliberately NOT computed here -- not in the frozen fairness metric list.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase5_common import (
    FAIR_RESULTS_DIR, DIMENSIONS, precision_tier, load_demographics, PRIMARY_MODELS,
    FROZEN_THRESHOLDS, NOW, fail,
)
from phase3_common import PRED_DIR, SPLIT_DIR, PRIMARY_OUTCOME_COL

test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"].tolist())
demo = load_demographics()
demo = demo[demo["SEQN"].isin(test_ids)].copy()
if len(demo) != 2146:
    fail(f"Test-set demographic join produced {len(demo)} rows, expected 2146")

rows = []
for model in PRIMARY_MODELS:
    pred = pd.read_csv(PRED_DIR / f"test_predictions_{model}.csv")
    if pred["SEQN"].nunique() != len(pred) or len(pred) != 2146:
        fail(f"{model}: test prediction file integrity issue (n={len(pred)}, unique={pred['SEQN'].nunique()})")
    merged = demo.merge(pred[["SEQN", "predicted_probability", "true_target"]], on="SEQN", how="inner")
    if len(merged) != 2146:
        fail(f"{model}: demographic-prediction join produced {len(merged)} rows, expected 2146")
    if not (merged["true_target"] == merged[PRIMARY_OUTCOME_COL]).all():
        fail(f"{model}: true_target in prediction file does not match frozen outcome column")

    threshold = FROZEN_THRESHOLDS[model]
    merged["pred_class"] = (merged["predicted_probability"] >= threshold).astype(int)

    for dim, spec in DIMENSIONS.items():
        merged["_bin"] = merged[spec["col"]].apply(spec["map_fn"])
        for cat, g in merged.groupby("_bin", observed=True):
            y = g["true_target"].values
            yhat = g["pred_class"].values
            n_pos, n_neg = int((y == 1).sum()), int((y == 0).sum())
            tier = precision_tier(n_pos, n_neg)

            if n_pos == 0 or n_neg == 0:
                auc = sens = spec_ = fnr = fpr = "NOT COMPUTABLE"
            else:
                auc = roc_auc_score(y, g["predicted_probability"].values)
                tp = int(((y == 1) & (yhat == 1)).sum()); fn = int(((y == 1) & (yhat == 0)).sum())
                tn = int(((y == 0) & (yhat == 0)).sum()); fp = int(((y == 0) & (yhat == 1)).sum())
                sens = tp / (tp + fn)
                spec_ = tn / (tn + fp)
                fnr = fn / (tp + fn)
                fpr = fp / (tn + fp)

            rows.append({
                "generated": NOW, "model": model, "dimension": dim, "category": cat,
                "is_reference_group": cat == spec["reference"], "frozen_threshold": threshold,
                "n": len(g), "n_positive": n_pos, "n_negative": n_neg, "precision_tier": tier,
                "roc_auc": auc, "sensitivity": sens, "specificity": spec_, "fnr": fnr, "fpr": fpr,
            })

out = pd.DataFrame(rows)
out.to_csv(FAIR_RESULTS_DIR / "subgroup_discrimination_metrics.csv", index=False)
print(out.head(20).to_string(index=False))
print(f"\n... ({len(out)} total rows)")
print(f"NOT COMPUTABLE cells: {(out['roc_auc'] == 'NOT COMPUTABLE').sum()}")
print("Saved results/fairness/subgroup_discrimination_metrics.csv")
