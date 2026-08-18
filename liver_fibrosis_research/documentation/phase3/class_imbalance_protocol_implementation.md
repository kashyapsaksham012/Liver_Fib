# Class-Imbalance Protocol Implementation

**Generated:** 2026-08-18 14:46:32

Primary outcome prevalence: 666/7153 = 9.31% (negative:positive ratio = 9.7402:1).

**Frozen strategy (model_development_protocol.md Part 10): class weights, NOT SMOTE/resampling.** No oversampling or synthetic minority generation is used anywhere in this pipeline.

## Per-model implementation

| Model | Mechanism | Value |
|---|---|---|
| Logistic Regression | `class_weight='balanced'` (sklearn) | inverse class-frequency weighting |
| Random Forest | `class_weight='balanced'` (sklearn) | inverse class-frequency weighting |
| XGBoost | `scale_pos_weight=9.7402` | negative/positive ratio, computed on TRAINING folds only |
| LightGBM | `scale_pos_weight=9.7402` | negative/positive ratio, computed on TRAINING folds only |
| MLP (sklearn `MLPClassifier`) | **NONE -- documented technical constraint** | sklearn's `MLPClassifier.fit()` does not accept `class_weight` or `sample_weight` (unlike the other four estimators). Trained unweighted; imbalance is instead partially compensated at the decision-threshold stage via the Youden's-J threshold rule (Part 20), which is computed per-model from that model's own out-of-fold CV predictions. This is a genuine implementation limitation, disclosed here and in the final report's Limitations section (AA), not a silent deviation.

## Leakage-safety guarantee

`scale_pos_weight` for XGBoost/LightGBM is computed separately within EACH cross-validation training fold (not once globally) to avoid any information leakage from validation folds into the class-weighting parameter. The final scale_pos_weight used for the test-set-evaluated model is computed from the full training partition only (N=see data_split_registry.md), never from the test set.

Class-imbalance handling never modifies the validation or test population itself -- no rows are added, removed, or duplicated in any partition; only the loss function's per-class weighting changes.
