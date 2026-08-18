"""
phase3_18_retention_and_final_baseline.py
Phase 3 Remediation, Parts 3W/3X - Produce the single authoritative baseline
results table (discrimination metrics only -- no calibration/fairness/uncertainty)
and formally document the downstream model-retention decision.

Produces:
  results/tables/phase3_final_baseline_results.csv
  documentation/phase3/downstream_model_retention_rule.md
  documentation/phase3/downstream_model_retention_decision.md
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import DOC_DIR, TAB_DIR, NOW, MODEL_NAMES

def main():
    print("=== Phase 3 Remediation, Parts 3W/3X: Final Baseline Results & Model Retention ===")
    disc = pd.read_csv(TAB_DIR / "phase3_overall_discrimination.csv")
    model_reg = pd.read_csv(TAB_DIR / "phase3_model_registry.csv")
    thresh = pd.read_csv(TAB_DIR / "phase3_threshold_selection.csv")

    final = disc.merge(model_reg[["model_name", "cv_roc_auc", "class_imbalance_handling"]], on="model_name")
    final = final.merge(thresh[["model_name", "method"]], on="model_name").rename(columns={"method": "threshold_selection_method"})
    final["model_version"] = "v1"
    final = final[["model_name", "model_version", "cv_roc_auc", "roc_auc", "roc_auc_95ci_low", "roc_auc_95ci_high",
                  "pr_auc", "pr_auc_95ci_low", "pr_auc_95ci_high", "sensitivity", "specificity", "ppv", "npv", "f1",
                  "threshold", "threshold_selection_method", "class_imbalance_handling"]]
    final = final.rename(columns={"roc_auc": "test_roc_auc", "pr_auc": "test_pr_auc"})
    final.to_csv(TAB_DIR / "phase3_final_baseline_results.csv", index=False)
    print("  Saved phase3_final_baseline_results.csv (discrimination metrics ONLY -- no calibration/fairness/uncertainty).")
    print(final[["model_name", "cv_roc_auc", "test_roc_auc", "test_pr_auc", "sensitivity", "specificity"]].to_string(index=False))

    with open(DOC_DIR / "downstream_model_retention_rule.md", "w") as f:
        f.write(f"# Downstream Model-Retention Rule\n\n**Generated:** {NOW}\n\n")
        f.write("## What Phase 2 froze\n\n")
        f.write("`documentation/phase2/model_development_protocol.md`, Part 7 (Model selection rule): "
                "*\"Best cross-validated ROC-AUC within each model family selects that family's "
                "hyperparameters; no family is declared 'the' final model in Phase 2 ... Phase 3 will "
                "report all four families'\"* [sic — five, including MLP] *\"calibration/fairness/"
                "uncertainty profiles rather than picking one 'winner' on discrimination alone.\"*\n\n")
        f.write("**This IS a pre-specified retention rule, written and frozen in Phase 2 -- before any "
                "Phase 3 model was trained.** It directly answers Part 3X's question: Option A "
                "(\"Retain all model families for later calibration/fairness/uncertainty evaluation\") "
                "applies, and it applies because Phase 2 said so, not because this remediation is choosing "
                "it now to avoid picking a winner.\n\n")
        f.write("## Confirmation this was not violated\n\n")
        f.write("No script anywhere in Phase 3 (original or remediated) drops, deprioritizes, or silently "
                "excludes any of the 5 original model families based on test-set discrimination. The FDR-"
                "corrected model comparison (Section W of the final report) is diagnostic/descriptive, not "
                "a filtering step.\n")

    with open(DOC_DIR / "downstream_model_retention_decision.md", "w") as f:
        f.write(f"# Downstream Model-Retention Decision (Final)\n\n**Generated:** {NOW}\n\n")
        f.write("## Decision\n\n")
        f.write("> **Retain all 5 original baseline models (Logistic Regression, Random Forest, XGBoost, "
                "LightGBM, MLP_original) for the downstream calibration, fairness, and uncertainty phases.**\n\n")
        f.write("**MLP_balanced (the training-fold-only oversampling sensitivity model) is NOT added to "
                "this retained set.** It exists solely to characterize whether MLP's class-imbalance "
                "asymmetry materially affects its result (`phase3_mlp_asymmetry_audit.csv` found the "
                "difference not statistically distinguishable from MLP_original on the locked test set). "
                "Promoting a sensitivity-analysis model to primary-retained status without a documented, "
                "pre-specified reason to do so would itself be an undisciplined protocol deviation.\n\n")
        f.write("## Explicit non-decisions (per the governing scientific-interpretation rules)\n\n")
        f.write("- No model is declared \"the best\" or \"clinically better\" based on its numerical test "
                "ROC-AUC (XGBoost's 0.8429 point estimate is NOT elevated to a winner -- see "
                "`phase3_model_effect_sizes.csv`: max pairwise |AUC diff|=0.02, small effect, not "
                "significant after FDR correction).\n")
        f.write("- No equivalence or non-inferiority claim is made between any pair of models.\n")
        f.write("- All 5 models' raw test-set probabilities, thresholds, and demographic-metadata-joinable "
                "predictions are preserved unmodified for the designated calibration/fairness/uncertainty "
                "phases.\n")

    print("  Saved downstream_model_retention_rule.md and downstream_model_retention_decision.md.")
    print("[FINAL BASELINE RESULTS & RETENTION DECISION COMPLETE]")

if __name__ == "__main__":
    main()
