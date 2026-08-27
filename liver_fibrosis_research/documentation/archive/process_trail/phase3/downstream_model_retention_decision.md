# Downstream Model-Retention Decision (Final)

**Generated:** 2026-08-18 17:00:00

## Decision

> **Retain all 5 original baseline models (Logistic Regression, Random Forest, XGBoost, LightGBM, MLP_original) for the downstream calibration, fairness, and uncertainty phases.**

**MLP_balanced (the training-fold-only oversampling sensitivity model) is NOT added to this retained set.** It exists solely to characterize whether MLP's class-imbalance asymmetry materially affects its result (`phase3_mlp_asymmetry_audit.csv` found the difference not statistically distinguishable from MLP_original on the locked test set). Promoting a sensitivity-analysis model to primary-retained status without a documented, pre-specified reason to do so would itself be an undisciplined protocol deviation.

## Explicit non-decisions (per the governing scientific-interpretation rules)

- No model is declared "the best" or "clinically better" based on its numerical test ROC-AUC (XGBoost's 0.8429 point estimate is NOT elevated to a winner -- see `phase3_model_effect_sizes.csv`: max pairwise |AUC diff|=0.02, small effect, not significant after FDR correction).
- No equivalence or non-inferiority claim is made between any pair of models.
- All 5 models' raw test-set probabilities, thresholds, and demographic-metadata-joinable predictions are preserved unmodified for the designated calibration/fairness/uncertainty phases.
