"""
phase5_05_intersectional.py
Phase 5 Part 19: EXPLORATORY intersectional analysis, using ONLY the 26 cells pre-specified in
results/tables/phase2_intersectional_feasibility.csv (Sex x Race/Ethnicity, Sex x Age, Sex x
BMI -- no other intersections were pre-specified, none are invented here). Per
multiple_comparisons_protocol.md, these are reported WITHOUT formal multiple-comparison
correction, explicitly labeled exploratory/uncorrected, and never promoted to primary
conclusions.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase5_common import FAIR_RESULTS_DIR, load_demographics, PRIMARY_MODELS, FROZEN_THRESHOLDS, precision_tier, NOW, fail
from phase3_common import PRED_DIR, SPLIT_DIR
from phase5_common import RACE_MAP_RIDRETH3, SEX_MAP, bin_age, bin_bmi, INTERSECTIONAL_FEASIBILITY_FILE

pre_specified = pd.read_csv(INTERSECTIONAL_FEASIBILITY_FILE)
if len(pre_specified) != 26:
    fail(f"Pre-specified intersectional feasibility file has {len(pre_specified)} rows, expected 26")

test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"].tolist())
demo = load_demographics()
demo = demo[demo["SEQN"].isin(test_ids)].copy()
demo["_sex"] = demo["RIAGENDR"].map(SEX_MAP)
demo["_race"] = demo["RIDRETH3"].map(RACE_MAP_RIDRETH3)
demo["_age"] = demo["RIDAGEYR"].apply(bin_age)
demo["_bmi"] = demo["BMXBMI"].apply(bin_bmi)

DIM2_MAP = {"Sex x Race/Ethnicity": "_race", "Sex x Age": "_age", "Sex x BMI": "_bmi"}

rows = []
for model in PRIMARY_MODELS:
    pred = pd.read_csv(PRED_DIR / f"test_predictions_{model}.csv")[["SEQN", "predicted_probability", "true_target"]]
    merged = demo.merge(pred, on="SEQN", how="inner")
    threshold = FROZEN_THRESHOLDS[model]
    merged["pred_class"] = (merged["predicted_probability"] >= threshold).astype(int)

    for _, cell in pre_specified.iterrows():
        col2 = DIM2_MAP[cell["intersection"]]
        g = merged[(merged["_sex"] == cell["group_1"]) & (merged[col2] == cell["group_2"])]
        y, yhat = g["true_target"].values, g["pred_class"].values
        n = len(g)
        n_pos, n_neg = int((y == 1).sum()), int((y == 0).sum())
        full_cohort_tier = cell["feasibility_classification"]
        test_tier = precision_tier(n_pos, n_neg)

        if n_pos == 0 or n_neg == 0:
            auc = sens = spec_ = "NOT COMPUTABLE"
        else:
            auc = roc_auc_score(y, g["predicted_probability"].values)
            tp = int(((y == 1) & (yhat == 1)).sum()); fn = int(((y == 1) & (yhat == 0)).sum())
            tn = int(((y == 0) & (yhat == 0)).sum()); fp = int(((y == 0) & (yhat == 1)).sum())
            sens = tp / (tp + fn); spec_ = tn / (tn + fp)

        rows.append({
            "generated": NOW, "label": "EXPLORATORY -- UNCORRECTED (multiple_comparisons_protocol.md)",
            "model": model, "intersection": cell["intersection"], "group_1": cell["group_1"],
            "group_2": cell["group_2"], "n_test": n, "n_positive_test": n_pos, "n_negative_test": n_neg,
            "full_cohort_feasibility_tier": full_cohort_tier, "test_set_precision_tier": test_tier,
            "roc_auc": auc, "sensitivity": sens, "specificity": spec_,
        })

out = pd.DataFrame(rows)
out.to_csv(FAIR_RESULTS_DIR / "intersectional_exploratory_metrics.csv", index=False)
print(out.head(15).to_string(index=False))
print(f"\n... ({len(out)} total rows = 5 models x 26 pre-specified cells)")
print("Saved results/fairness/intersectional_exploratory_metrics.csv")
print("\nALL rows in this file are EXPLORATORY and UNCORRECTED per the frozen protocol -- none")
print("are eligible for promotion to primary/confirmatory conclusions.")
