"""
phase3_15_comparability_matrix.py
Phase 3 Remediation, Part 3U - Explicit model-comparability matrix: what is
identical across all 5 models (cohort, predictors, target, split, CV folds,
evaluation population, primary scoring metric) vs. what intentionally differs
(preprocessing, imbalance handling) -- so the comparison's scientific
interpretability is fully transparent.

Produces:
  results/tables/phase3_model_comparability_matrix.csv
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import TAB_DIR, MODEL_NAMES

def main():
    print("=== Phase 3 Remediation, Part 3U: Model Comparability Matrix ===")
    model_reg = pd.read_csv(TAB_DIR / "phase3_model_registry.csv")

    rows = []
    for dim, identical, detail_fn in [
        ("Cohort (N=7,153)", True, lambda r: "identical for all models"),
        ("Predictors (10 frozen)", True, lambda r: "identical for all models"),
        ("Target (LUXSMED>=8.2kPa)", True, lambda r: "identical for all models"),
        ("Train/test split (seed=42, 70/30)", True, lambda r: "identical for all models"),
        ("CV folds (5-fold StratifiedKFold, seed=42)", True, lambda r: "identical for all models"),
        ("Evaluation population (locked test set, N=2,146)", True, lambda r: "identical for all models"),
        ("Primary scoring/selection metric (mean CV ROC-AUC)", True, lambda r: "identical for all models"),
        ("Missing-data handling", True, lambda r: "identical: median-impute no-op (0 missingness by cohort construction)"),
        ("Preprocessing: scaling", False, lambda r: r),
        ("Class-imbalance handling", False, lambda r: r),
        ("Hyperparameter search space size", False, lambda r: r),
    ]:
        row = {"comparability_dimension": dim, "identical_across_all_5_models": identical}
        if identical:
            row["detail"] = detail_fn(None)
        else:
            for _, m in model_reg.iterrows():
                if "scaling" in dim.lower():
                    row[m["model_name"]] = "StandardScaler" if m["model_name"] in ("logistic", "mlp") else "None (tree-based)"
                elif "imbalance" in dim.lower():
                    row[m["model_name"]] = m["class_imbalance_handling"]
                elif "search space" in dim.lower():
                    n_combos = {"logistic": 6, "random_forest": "20 (randomized of 36 possible)",
                               "xgboost": "20 (randomized of 108 possible)", "lightgbm": "20 (randomized of 108 possible)",
                               "mlp": 18}
                    row[m["model_name"]] = n_combos[m["model_name"]]
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(TAB_DIR / "phase3_model_comparability_matrix.csv", index=False)
    print(df.to_string(index=False))
    print("\n  Identical across all 5 models: cohort, predictors, target, split, CV design, evaluation "
          "population, primary scoring metric, missing-data handling.")
    print("  Intentionally differing: scaling (algorithm-appropriate), class-imbalance mechanism "
          "(library-native, MLP asymmetry documented separately), hyperparameter search space size "
          "(model-appropriate ranges).")
    print("  Saved phase3_model_comparability_matrix.csv.")
    print("[COMPARABILITY MATRIX COMPLETE]")

if __name__ == "__main__":
    main()
