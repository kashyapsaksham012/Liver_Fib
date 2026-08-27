# Phase 3 Model Development and Baseline Results Report

**Generated:** 2026-08-18 14:56:01

---

## A. Phase 3 Objective

Execute the frozen Phase 2 model-development protocol exactly: build a leakage-safe modeling pipeline, split and lock the test set, train the frozen 5-model baseline set with cross-validated hyperparameter tuning on training data only, select candidate models, generate locked test predictions, and compute the pre-specified baseline discrimination metrics. No calibration, fairness, uncertainty, or mitigation analysis is performed.

## B. Frozen Phase 2 Protocol Version

`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`, zero amendments logged. No contradiction between code, data, and protocol was found during verification (Section C).

## C. Dataset Handoff Verification

11/11 independent checks passed (dataset N, SEQN set, outcome count, prevalence, predictor completeness, no forbidden variables, no missingness, no duplicates) — full detail: `documentation/phase3/phase2_handoff_verification.md`.

## D. Primary Analytical Cohort

Unchanged from Phase 2: N=7,153 (adult, quality-valid elastography, broad labs + BMI + sex complete). Not modified in Phase 3.

## E. Primary Outcome

| check                                                                 |   n_positive |   n_negative |   prevalence_pct |   n_missing_target |   n_impossible_values | matches_saved_outcome_column   | created_before_preprocessing   |
|:----------------------------------------------------------------------|-------------:|-------------:|-----------------:|-------------------:|----------------------:|:-------------------------------|:-------------------------------|
| TARGET recreated from LUXSMED >= 8.2 kPa, independent of saved column |          666 |         6487 |             9.31 |                  0 |                     0 | True                           | True                           |

Threshold (LUXSMED >= 8.2 kPa) unchanged from Phase 2; not touched in Phase 3.

## F. Primary Predictors

| variable   | role                                                                | enters_model_matrix   |
|:-----------|:--------------------------------------------------------------------|:----------------------|
| RIDAGEYR   | PRIMARY MODEL PREDICTOR                                             | True                  |
| RIAGENDR   | PRIMARY MODEL PREDICTOR                                             | True                  |
| BMXBMI     | PRIMARY MODEL PREDICTOR                                             | True                  |
| LBXSATSI   | PRIMARY MODEL PREDICTOR                                             | True                  |
| LBXSASSI   | PRIMARY MODEL PREDICTOR                                             | True                  |
| LBXSAL     | PRIMARY MODEL PREDICTOR                                             | True                  |
| LBXSAPSI   | PRIMARY MODEL PREDICTOR                                             | True                  |
| LBXSTB     | PRIMARY MODEL PREDICTOR                                             | True                  |
| LBXPLTSI   | PRIMARY MODEL PREDICTOR                                             | True                  |
| LBDHDD     | PRIMARY MODEL PREDICTOR                                             | True                  |
| SEQN       | ID (metadata only)                                                  | False                 |
| RIDRETH1   | FAIRNESS STRATIFICATION ONLY (Phase 2 fairness-by-design exclusion) | False                 |
| RIDRETH3   | FAIRNESS STRATIFICATION ONLY (Phase 2 fairness-by-design exclusion) | False                 |

Model matrix = exactly the 10 frozen predictors: ['RIDAGEYR', 'RIAGENDR', 'BMXBMI', 'LBXSATSI', 'LBXSASSI', 'LBXSAL', 'LBXSAPSI', 'LBXSTB', 'LBXPLTSI', 'LBDHDD']. Race/ethnicity (RIDRETH1/RIDRETH3) confirmed present as metadata but excluded from the model matrix.

## G. Train/Validation/Test Design

70% train (=CV validation pool) / 30% test, stratified on the primary outcome, seed=42. 5-fold stratified CV within training for tuning/selection (no separate fixed validation partition — see reconciliation note in `data_split_registry.md`).

## H. Split Counts and Integrity

- Train (= CV validation pool): N=5007
- Test (LOCKED): N=2146

| check                                                   | status   | detail                                        |
|:--------------------------------------------------------|:---------|:----------------------------------------------|
| train ∩ test = empty                                    | PASS     | overlap=0                                     |
| union(train, test) = full modeling cohort               | PASS     | union_size=7153, cohort_size=7153             |
| Every participant appears exactly once                  | PASS     | 5007+2146=7153 vs 7153                        |
| No participant-level duplication across partitions      | PASS     | same as check 1                               |
| Target distribution documented per partition            | PASS     | train_prevalence=9.31%, test_prevalence=9.32% |
| Subgroup distributions documented (sex, race/ethnicity) | PASS     | train_pct_female=50.4, test_pct_female=51.2   |

## I. Preprocessing Pipeline

sklearn `ColumnTransformer` + `Pipeline`: median imputation (no-op, zero missingness by cohort construction) + `StandardScaler` for Logistic Regression and MLP; no scaling for tree-based models (Random Forest, XGBoost, LightGBM). Fit exclusively within each CV fold / on the training partition — never on the test set (verified TEST9/TEST10).

## J. Missing-Data Implementation

|   n_entering_eligible_pool |   n_excluded_missing_predictors |   n_retained_complete_case |   pct_excluded | strategy                                                          | subgroup_note                                                                                                                                                                                                                                           |   outcome_prevalence_retained_pct |
|---------------------------:|--------------------------------:|---------------------------:|---------------:|:------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------:|
|                       7768 |                             615 |                       7153 |           7.92 | COMPLETE-CASE (frozen primary strategy, missing_data_protocol.md) | See documentation/phase2/missing_data_protocol.md for the full demographic composition comparison (pool vs. complete-case vs. excluded) established in Phase 2 -- not recomputed here since the primary dataset construction is unchanged from Phase 2. |                              9.31 |

## K. Class-Imbalance Handling

Class weighting (NOT SMOTE), per model — see `documentation/phase3/class_imbalance_protocol_implementation.md`. Note: sklearn's `MLPClassifier` does not support class weighting; this is a documented technical constraint, not a silent deviation (see Section AA).

## L. Model List

Logistic Regression, Random Forest, XGBoost, LightGBM, MLP — the exact 5-model set from `info.md` Phase 6 / `model_development_protocol.md`. No additional model was added.

## M. Hyperparameter Search

| model_name    | best_hyperparameters                                                                               |   cv_roc_auc |   training_time_sec |
|:--------------|:---------------------------------------------------------------------------------------------------|-------------:|--------------------:|
| logistic      | {"est__C": 0.01}                                                                                   |       0.8157 |                 2.1 |
| random_forest | {"est__n_estimators": 100, "est__min_samples_leaf": 5, "est__max_depth": 7}                        |       0.821  |                13.5 |
| xgboost       | {"est__subsample": 0.7, "est__n_estimators": 100, "est__max_depth": 3, "est__learning_rate": 0.05} |       0.8212 |                 1.9 |
| lightgbm      | {"est__subsample": 0.7, "est__n_estimators": 100, "est__max_depth": 3, "est__learning_rate": 0.05} |       0.8157 |                18.2 |
| mlp           | {"est__alpha": 0.01, "est__hidden_layer_sizes": [32, 16], "est__learning_rate_init": 0.01}         |       0.8184 |                 2   |

Total hyperparameter configurations evaluated across all 5 models: 84. Search spaces, scoring (mean CV ROC-AUC), and tie-break rule (prefer simpler/more-regularized config within 0.001 AUC of the best) were fixed before any search ran. Full detail: `results/tables/phase3_hyperparameter_search_registry.csv`.

## N. Cross-Validation Design

5-fold `StratifiedKFold(shuffle=True, random_state=42)`, applied within the 70% training partition only, for both hyperparameter tuning and out-of-fold validation-prediction generation.

## O. Model-Selection Rule

Best mean CV ROC-AUC selects each model family's hyperparameters independently; no single family is declared an overall winner (frozen rule, `model_development_protocol.md`). All 5 tuned models are retained as candidates for subsequent calibration/fairness/uncertainty phases.

## P. Final Selected Candidate Model(s)

All 5: Logistic Regression, Random Forest, XGBoost, LightGBM, MLP — each independently tuned. Artifacts: `models/phase3/model_<name>_v1.joblib`.

## Q. Validation Performance

Out-of-fold CV ROC-AUC per model (from the same folds used for tuning): logistic=0.8157, random_forest=0.821, xgboost=0.8212, lightgbm=0.8157, mlp=0.8184. Full out-of-fold predictions: `results/predictions/validation_predictions_<model>.csv`.

## R. Locked Test Performance

| model_name    |   threshold |   roc_auc |   roc_auc_95ci_low |   roc_auc_95ci_high |   pr_auc |   sensitivity |   specificity |    ppv |    npv |     f1 |
|:--------------|------------:|----------:|-------------------:|--------------------:|---------:|--------------:|--------------:|-------:|-------:|-------:|
| logistic      |      0.5173 |    0.8334 |             0.8021 |              0.861  |   0.3725 |         0.75  |        0.7621 | 0.2447 | 0.9674 | 0.369  |
| random_forest |      0.4499 |    0.8343 |             0.8036 |              0.8611 |   0.3508 |         0.79  |        0.7359 | 0.2351 | 0.9715 | 0.3624 |
| xgboost       |      0.4108 |    0.8429 |             0.8123 |              0.8693 |   0.3717 |         0.845 |        0.6773 | 0.212  | 0.977  | 0.339  |
| lightgbm      |      0.4988 |    0.8394 |             0.8088 |              0.867  |   0.3729 |         0.795 |        0.7492 | 0.2457 | 0.9726 | 0.3754 |
| mlp           |      0.1065 |    0.8229 |             0.7903 |              0.8532 |   0.3652 |         0.815 |        0.6644 | 0.1998 | 0.9722 | 0.3209 |

Test set (N=2146) was loaded exactly once, after all model/hyperparameter/threshold decisions were frozen from training/CV data only (verified TEST10/TEST12).

## S. ROC-AUC

See Section R table and `results/figures/phase3_roc_combined.png` / individual `phase3_roc_<model>.png` files.

## T. PR-AUC

See Section R table and `results/figures/phase3_pr_combined.png` / individual `phase3_pr_<model>.png` files. Precision-recall is reported alongside ROC-AUC given the primary cohort's moderate class imbalance (9.31% prevalence).

## U. Sensitivity/Specificity and Other Approved Metrics

Sensitivity, specificity, PPV, NPV, F1 at each model's Youden-derived threshold — see Section R table. Threshold-selection detail: `results/tables/phase3_threshold_selection.csv`.

## V. Confidence Intervals

Percentile bootstrap, n=2,000 resamples, seed=42, fixed before any result was observed (consistent with the 2,000-resample convention already fixed in `documentation/phase2/fairness_definition.md`). Reported for ROC-AUC and PR-AUC in Section R.

## W. Model Comparison

| model_a       | model_b       |   auc_diff_a_minus_b |   diff_95ci_low |   diff_95ci_high |   raw_p_value_bootstrap | ci_excludes_zero   |   fdr_adjusted_p_value | significant_after_fdr_0.05   |
|:--------------|:--------------|---------------------:|----------------:|-----------------:|------------------------:|:-------------------|-----------------------:|:-----------------------------|
| logistic      | random_forest |              -0.0009 |         -0.0157 |           0.0138 |                   0.883 | False              |                 0.883  | False                        |
| logistic      | xgboost       |              -0.0095 |         -0.0229 |           0.0034 |                   0.152 | False              |                 0.304  | False                        |
| logistic      | lightgbm      |              -0.006  |         -0.0199 |           0.0075 |                   0.392 | False              |                 0.4356 | False                        |
| logistic      | mlp           |               0.0106 |         -0.0006 |           0.0223 |                   0.059 | False              |                 0.1475 | False                        |
| random_forest | xgboost       |              -0.0086 |         -0.0169 |          -0.001  |                   0.03  | True               |                 0.1    | False                        |
| random_forest | lightgbm      |              -0.0051 |         -0.0139 |           0.0038 |                   0.254 | False              |                 0.3175 | False                        |
| random_forest | mlp           |               0.0115 |         -0.0057 |           0.0298 |                   0.199 | False              |                 0.3175 | False                        |
| xgboost       | lightgbm      |               0.0035 |         -0.0026 |           0.0093 |                   0.251 | False              |                 0.3175 | False                        |
| xgboost       | mlp           |               0.02   |          0.0059 |           0.0353 |                   0.005 | True               |                 0.05   | False                        |
| lightgbm      | mlp           |               0.0166 |          0.0015 |           0.033  |                   0.029 | True               |                 0.1    | False                        |

Paired bootstrap AUC-difference comparisons (predictions correlated — identical test participants across models), FDR-corrected (Benjamini-Hochberg) across the 10 pairwise comparisons, consistent with `multiple_comparisons_protocol.md`. **After FDR correction, no pairwise model difference remains statistically significant** — the 5 model families perform comparably on this primary cohort/predictor set. No clinical-utility or 'better model' claim is made from this discrimination-only comparison (non-negotiable rules, Part 36).

## X. Reproducibility Information

Full configuration and an exact independent reproduction (byte-for-byte identical discrimination/threshold results, only wall-clock timing differed) — `documentation/phase3/reproducibility_registry.md`.

## Y. Validation-Test Integrity Checks

20/20 tests passed. Full detail: `documentation/phase3/phase3_validation_results.csv`.

## Z. What Is Intentionally Deferred to Later Phases

- **Calibration analysis** (calibration slope/intercept/Brier/curve) — raw test-set probabilities are saved (`results/predictions/test_predictions_<model>.csv`) but NOT recalibrated or evaluated for calibration here.
- **Fairness analysis** — demographic metadata (RIDRETH1/RIDRETH3, sex, age, BMI) is preserved in every prediction file's source (`SEQN`-joinable to the primary dataset) but no subgroup metric is computed or interpreted in Phase 3.
- **Uncertainty/conformal prediction** — no conformal calibration set was carved out or used; the full training partition and locked test set remain available and untouched for this purpose in the designated later phase.
- **Fairness mitigation, threshold re-optimization for fairness, or any post-hoc recalibration** — none performed.

## AA. Phase 3 Limitations

1. **MLP class-imbalance handling.** sklearn's `MLPClassifier` does not support `class_weight`/`sample_weight`; the MLP was trained unweighted, partially compensated only at the decision-threshold stage. This is a real, disclosed asymmetry versus the other 4 models.
2. **No separate fixed validation partition.** "Validation" = out-of-fold CV predictions within the training set, per the frozen protocol's own CV-based design — not a limitation of execution, but worth restating for a reader expecting a classic 3-way split.
3. **Confidence-interval and model-comparison methods** (bootstrap, FDR) were the most reasonable pre-specified choices consistent with conventions already fixed in Phase 2's fairness/multiple-comparisons protocols, but Phase 2 did not explicitly freeze a Phase-3-specific CI method — this gap was resolved by extending the closest existing Phase 2 convention, documented transparently rather than left as an unstated assumption.
4. **Environment side effect (disclosed, corrected):** installing XGBoost's OpenMP dependency via Homebrew triggered an autoremove that unintentionally uninstalled the unrelated `mongosh` package; it was immediately reinstalled. See `phase3_pre_modeling_snapshot.md`.

## AB. Final Phase 3 Readiness Decision

**PHASE 3 — COMPLETE**

All Phase 3 completion criteria are satisfied: Phase 2 handoff verified; primary cohort, outcome, and predictors match the frozen protocol exactly; the leakage whitelist passes; the train/test split is frozen and the test set locked (SHA-256-verified unchanged); preprocessing is leakage-safe (fit only within training/CV); the missing-data and class-imbalance strategies are implemented exactly as frozen (with one disclosed MLP constraint); all 5 primary models are trained with completed cross-validated hyperparameter search; the model-selection rule was followed (no family declared a winner); the test set remained untouched until final evaluation; final predictions, discrimination metrics, and confidence intervals are computed and saved; ROC/PR figures are generated; all 20 validation tests pass; and a clean independent rerun reproduced every scientific result exactly.

**Phase 4 (calibration, fairness, and uncertainty analysis) may now proceed using the frozen models and locked test predictions produced here. No calibration, fairness, or uncertainty claim has been made in this report.**
