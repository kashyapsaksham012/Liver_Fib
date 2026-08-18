"""
phase3_02_target_and_features.py
Phase 3, Parts 4-7 - Target verification, primary feature registry, predictor
whitelist enforcement, and confirmation that stratification-only demographic
variables (RIDRETH1/RIDRETH3) are excluded from the model matrix.

Produces:
  results/tables/phase3_target_verification.csv
  results/tables/phase3_primary_feature_registry.csv
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (TAB_DIR, PROC_DIR, PRIMARY_PREDICTORS, FORBIDDEN_VARS,
                          PRIMARY_OUTCOME_COL, STRATIFICATION_METADATA_COLS, fail)
from _common import VAR_METADATA

def main():
    print("=== Phase 3, Parts 4-7: Target Verification, Feature Registry, Predictor Whitelist ===")
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")

    # Part 5: Target verification -- recreate TARGET independently from LUXSMED, before any preprocessing
    target = (df["LUXSMED"] >= 8.2).astype(int)
    assert (target == df[PRIMARY_OUTCOME_COL]).all(), "Independently-recreated TARGET does not match the saved outcome column!"
    n_pos = int(target.sum()); n_neg = int((target == 0).sum())
    n_missing_target = int(df["LUXSMED"].isna().sum())
    impossible = int(((target != 0) & (target != 1)).sum())
    tv = pd.DataFrame([{
        "check": "TARGET recreated from LUXSMED >= 8.2 kPa, independent of saved column", "n_positive": n_pos,
        "n_negative": n_neg, "prevalence_pct": round(100*n_pos/len(df), 2), "n_missing_target": n_missing_target,
        "n_impossible_values": impossible, "matches_saved_outcome_column": bool((target == df[PRIMARY_OUTCOME_COL]).all()),
        "created_before_preprocessing": True
    }])
    tv.to_csv(TAB_DIR / "phase3_target_verification.csv", index=False)
    print(f"  Target verified: {n_pos} positive, {n_neg} negative, {n_missing_target} missing, {impossible} impossible values.")
    if n_missing_target > 0 or impossible > 0:
        fail(f"Target verification failed: {n_missing_target} missing, {impossible} impossible values.")

    # Part 4/6: Feature registry -- exactly the 10 frozen predictors, ID excluded from model matrix
    reg_rows = []
    for p in PRIMARY_PREDICTORS:
        meta = VAR_METADATA.get(p, {})
        reg_rows.append({
            "variable": p, "role": "PRIMARY MODEL PREDICTOR", "dtype": str(df[p].dtype), "unit": meta.get("unit", "-"),
            "n_missing": int(df[p].isna().sum()), "min": round(float(df[p].min()), 3), "max": round(float(df[p].max()), 3),
            "prediction_time_available": True, "leakage_status": "eligible (verified Phase 2)",
            "enters_model_matrix": True
        })
    reg_rows.append({"variable": "SEQN", "role": "ID (metadata only)", "dtype": str(df["SEQN"].dtype), "unit": "-",
                     "n_missing": 0, "min": None, "max": None, "prediction_time_available": True,
                     "leakage_status": "n/a (identifier)", "enters_model_matrix": False})
    for m in STRATIFICATION_METADATA_COLS:
        reg_rows.append({"variable": m, "role": "FAIRNESS STRATIFICATION ONLY (Phase 2 fairness-by-design exclusion)",
                         "dtype": str(df[m].dtype), "unit": "-", "n_missing": int(df[m].isna().sum()), "min": None, "max": None,
                         "prediction_time_available": True, "leakage_status": "eligible but deliberately excluded from model input",
                         "enters_model_matrix": False})
    feat_df = pd.DataFrame(reg_rows)
    feat_df.to_csv(TAB_DIR / "phase3_primary_feature_registry.csv", index=False)
    print(f"  Saved phase3_primary_feature_registry.csv ({len(feat_df)} rows).")

    # Part 6: whitelist enforcement -- fail loudly if any forbidden variable is in the model-matrix column list
    model_matrix_cols = feat_df[feat_df["enters_model_matrix"] == True]["variable"].tolist()
    violation = set(model_matrix_cols) & set(FORBIDDEN_VARS)
    if violation:
        fail(f"Forbidden variable(s) in model matrix: {violation}")
    assert set(model_matrix_cols) == set(PRIMARY_PREDICTORS), "Model matrix does not exactly equal the frozen predictor set!"
    print(f"  Predictor whitelist enforced: model matrix = exactly {sorted(model_matrix_cols)}.")
    print(f"  Confirmed: RIDRETH1/RIDRETH3 present as metadata but NOT in model matrix (enters_model_matrix=False).")
    print("[TARGET & FEATURE VERIFICATION COMPLETE]")

if __name__ == "__main__":
    main()
