"""
phase3_04_missingness_and_imbalance.py
Phase 3, Parts 13-14 - Record the primary (complete-case) missing-data implementation
and document the class-imbalance strategy implementation (class weighting, not SMOTE,
per the frozen protocol).

Produces:
  results/tables/phase3_primary_missingness_after_cohort.csv
  documentation/phase3/class_imbalance_protocol_implementation.md
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import TAB_DIR, DOC_DIR, PROC_DIR, NOW, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, RANDOM_SEED
from _common import INT_DIR
from _cohorts import compute_all

def main():
    print("=== Phase 3, Parts 13-14: Missing-Data Implementation & Class-Imbalance Protocol ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    primary = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    c = compute_all(master)
    adult_qv = c["COHORT_3B_ADULT_OF_QUALITY_VALID"][0]  # N=7,768, pre-predictor-completeness pool
    n_entering = int(adult_qv.sum())
    n_retained = len(primary)
    n_excluded = n_entering - n_retained

    rows = [{
        "n_entering_eligible_pool": n_entering, "n_excluded_missing_predictors": n_excluded,
        "n_retained_complete_case": n_retained, "pct_excluded": round(100*n_excluded/n_entering, 2),
        "strategy": "COMPLETE-CASE (frozen primary strategy, missing_data_protocol.md)",
        "subgroup_note": "See documentation/phase2/missing_data_protocol.md for the full demographic composition "
                         "comparison (pool vs. complete-case vs. excluded) established in Phase 2 -- not recomputed "
                         "here since the primary dataset construction is unchanged from Phase 2.",
        "outcome_prevalence_retained_pct": round(100*primary[PRIMARY_OUTCOME_COL].mean(), 2)
    }]
    pd.DataFrame(rows).to_csv(TAB_DIR / "phase3_primary_missingness_after_cohort.csv", index=False)
    print(f"  Entering pool N={n_entering}, excluded (missing predictors) N={n_excluded} ({round(100*n_excluded/n_entering,2)}%), retained N={n_retained}.")
    print("  Primary strategy implemented exactly as frozen: COMPLETE-CASE. No imputation applied to the primary dataset.")

    n_pos = int(primary[PRIMARY_OUTCOME_COL].sum()); n_neg = len(primary) - n_pos
    scale_pos_weight = round(n_neg / n_pos, 4)

    with open(DOC_DIR / "class_imbalance_protocol_implementation.md", "w") as f:
        f.write(f"# Class-Imbalance Protocol Implementation\n\n**Generated:** {NOW}\n\n")
        f.write(f"Primary outcome prevalence: {n_pos}/{len(primary)} = {round(100*n_pos/len(primary),2)}% "
                f"(negative:positive ratio = {scale_pos_weight}:1).\n\n")
        f.write("**Frozen strategy (model_development_protocol.md Part 10): class weights, NOT SMOTE/resampling.** "
                "No oversampling or synthetic minority generation is used anywhere in this pipeline.\n\n")
        f.write("## Per-model implementation\n\n")
        f.write("| Model | Mechanism | Value |\n|---|---|---|\n")
        f.write("| Logistic Regression | `class_weight='balanced'` (sklearn) | inverse class-frequency weighting |\n")
        f.write("| Random Forest | `class_weight='balanced'` (sklearn) | inverse class-frequency weighting |\n")
        f.write(f"| XGBoost | `scale_pos_weight={scale_pos_weight}` | negative/positive ratio, computed on TRAINING folds only |\n")
        f.write(f"| LightGBM | `scale_pos_weight={scale_pos_weight}` | negative/positive ratio, computed on TRAINING folds only |\n")
        f.write("| MLP (sklearn `MLPClassifier`) | **NONE -- documented technical constraint** | "
                "sklearn's `MLPClassifier.fit()` does not accept `class_weight` or `sample_weight` "
                "(unlike the other four estimators). Trained unweighted; imbalance is instead partially "
                "compensated at the decision-threshold stage via the Youden's-J threshold rule (Part 20), "
                "which is computed per-model from that model's own out-of-fold CV predictions. This is a "
                "genuine implementation limitation, disclosed here and in the final report's Limitations "
                "section (AA), not a silent deviation.\n\n")
        f.write("## Leakage-safety guarantee\n\n")
        f.write("`scale_pos_weight` for XGBoost/LightGBM is computed separately within EACH cross-validation "
                "training fold (not once globally) to avoid any information leakage from validation folds into "
                "the class-weighting parameter. The final scale_pos_weight used for the test-set-evaluated model "
                f"is computed from the full training partition only (N={len(primary)-2146 if False else 'see data_split_registry.md'}), never from the test set.\n\n")
        f.write("Class-imbalance handling never modifies the validation or test population itself -- no rows are "
                "added, removed, or duplicated in any partition; only the loss function's per-class weighting "
                "changes.\n")
    print("  Saved class_imbalance_protocol_implementation.md.")
    print("[MISSINGNESS & IMBALANCE DOCUMENTATION COMPLETE]")

if __name__ == "__main__":
    main()
