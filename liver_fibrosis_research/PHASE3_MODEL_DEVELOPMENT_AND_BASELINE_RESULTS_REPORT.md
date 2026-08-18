# Phase 3 Model Development and Baseline Results Report — REMEDIATED

**Generated:** 2026-08-18 17:01:16

This report supersedes the original Phase 3 report (archived: `documentation/phase3/archive/PHASE3_REPORT_pre_remediation_20260818.md`). This remediation pass audited every methodological decision in the original Phase 3 execution, found the core experiment (cohort, split, leakage-safety, hyperparameter search, threshold isolation) sound, corrected imprecise interpretive language, added a pre-specified MLP class-imbalance sensitivity analysis, and formally documented several Phase-3-specific methodological clarifications that Phase 2 had explicitly deferred. **No original baseline model or test-set prediction was retrained, re-evaluated, or modified** — all 5 original models' artifacts and predictions are hash-verified byte-identical to before this remediation began (see Section W).

---

## A. Phase 3 Objective

Audit and remediate the existing Phase 3 baseline ML implementation: verify the Phase 2 handoff, resolve every flagged methodological ambiguity (MLP imbalance asymmetry, CV-vs-validation terminology, threshold provenance, CI/FDR protocol status, model-retention rule, PR-AUC/H1 interpretation), independently reproduce results, and freeze a single authoritative baseline result package. No calibration, fairness, uncertainty, or mitigation analysis is performed.

## B. Phase 2 Handoff Verification

Re-independently verified (not assumed from the prior report): N=7,153, 666 positive, 6,487 negative, SEQN set identical to the Phase 1/2 frozen cohort, 10 predictors present with zero missingness. Full detail: `documentation/phase3/phase2_handoff_reverification.md`.

## C. Cohort Verification

Unchanged from Phase 2 (N=7,153); NOT reopened. Independently recomputed from the frozen Phase 1 master dataset in Section B.

## D. Outcome Verification

Unchanged (LUXSMED >= 8.2 kPa, 666 positive); NOT reopened.

## E. Predictor Verification

Unchanged (10 frozen predictors); NOT reopened.

## F. Split Design

70/30 stratified, seed=42. Demographic composition audited descriptively (NOT used to alter the split):

| partition              |    n |   outcome_prevalence_pct |   pct_Male |   pct_Female |   median_age |   median_bmi |
|:-----------------------|-----:|-------------------------:|-----------:|-------------:|-------------:|-------------:|
| Full cohort (N=7,153)  | 7153 |                     9.31 |      49.36 |        50.64 |           50 |         28.5 |
| Train (N=5,007)        | 5007 |                     9.31 |      49.61 |        50.39 |           50 |         28.5 |
| Test (N=2,146, LOCKED) | 2146 |                     9.32 |      48.79 |        51.21 |           50 |         28.4 |

**CV-vs-validation terminology formally clarified:** `validation_ids.csv` is NOT an independent validation cohort — it is byte-identical to `train_ids.csv`, since Phase 2's frozen design uses 5-fold CV within training as the sole development/validation mechanism, not a three-way split. Full clarification: `documentation/phase3/cv_validation_design.md`.

## G. Test-Set Lock

Locked once, SHA-256-hashed, chronology-audited (split -> lock -> development -> CV -> tuning -> threshold -> freeze -> test evaluation, verified no out-of-order access — `results/tables/phase3_test_set_audit.csv`).

## H. Preprocessing Design

Leakage audit PASSED (5/5 code-level checks) with a per-model pipeline diagram for all 5 models. Full detail: `documentation/phase3/preprocessing_leakage_audit.md`.

## I. Missing-Data Implementation

Unchanged: complete-case by cohort construction, 0 missing predictor values. NOT altered based on model performance.

## J. Class-Imbalance Audit

| Model | Class weighting | Sampling |
|---|---|---|
| Logistic Regression | class_weight=balanced | None |
| Random Forest | class_weight=balanced | None |
| XGBoost | scale_pos_weight=9.745 | None |
| LightGBM | scale_pos_weight=9.745 | None |
| MLP | **NONE (sklearn API constraint)** | See sensitivity analysis, Section V |

This asymmetry was NOT anticipated by Phase 2's general "class weights, not SMOTE" policy (a genuine implementation gap, not a Phase 2 drafting error). Full audit: `documentation/phase3/class_imbalance_audit.md`.

## K. Model List

Unchanged: Logistic Regression, Random Forest, XGBoost, LightGBM, MLP (the frozen 5-family set). No model added or removed.

## L. Model Comparability

**Identical across all 5 models:** Cohort (N=7,153), Predictors (10 frozen), Target (LUXSMED>=8.2kPa), Train/test split (seed=42, 70/30), CV folds (5-fold StratifiedKFold, seed=42), Evaluation population (locked test set, N=2,146), Primary scoring/selection metric (mean CV ROC-AUC), Missing-data handling.

**Intentionally differing** (algorithm-appropriate, not arbitrary): preprocessing scaling, class-imbalance mechanism, hyperparameter search space size. Full matrix: `results/tables/phase3_model_comparability_matrix.csv`.

## M. CV Design

5-fold `StratifiedKFold(shuffle=True, random_state=42)`, training partition only, unchanged from the original Phase 3 pass.

## N. Hyperparameter Search

| model         |   n_configurations_evaluated | search_type   |   cv_folds | scoring_metric               |   random_seed | preprocessing_inside_fold                                                         | test_information_used                                                               |   best_cv_score |
|:--------------|-----------------------------:|:--------------|-----------:|:-----------------------------|--------------:|:----------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|----------------:|
| logistic      |                            6 | grid          |          5 | roc_auc (mean over CV folds) |            42 | Yes (sklearn Pipeline/ColumnTransformer, verified preprocessing_leakage_audit.md) | NO -- test_ids.csv is never imported in phase3_05_train_and_tune.py (grep-verified) |          0.8157 |
| random_forest |                           20 | randomized    |          5 | roc_auc (mean over CV folds) |            42 | Yes (sklearn Pipeline/ColumnTransformer, verified preprocessing_leakage_audit.md) | NO -- test_ids.csv is never imported in phase3_05_train_and_tune.py (grep-verified) |          0.821  |
| xgboost       |                           20 | randomized    |          5 | roc_auc (mean over CV folds) |            42 | Yes (sklearn Pipeline/ColumnTransformer, verified preprocessing_leakage_audit.md) | NO -- test_ids.csv is never imported in phase3_05_train_and_tune.py (grep-verified) |          0.8212 |
| lightgbm      |                           20 | randomized    |          5 | roc_auc (mean over CV folds) |            42 | Yes (sklearn Pipeline/ColumnTransformer, verified preprocessing_leakage_audit.md) | NO -- test_ids.csv is never imported in phase3_05_train_and_tune.py (grep-verified) |          0.8157 |
| mlp           |                           18 | grid          |          5 | roc_auc (mean over CV folds) |            42 | Yes (sklearn Pipeline/ColumnTransformer, verified preprocessing_leakage_audit.md) | NO -- test_ids.csv is never imported in phase3_05_train_and_tune.py (grep-verified) |          0.8184 |

**Confirmed: the test set never entered hyperparameter optimization** (code-level grep verification, `results/tables/phase3_hyperparameter_audit.csv`).

## O. Threshold Selection

Youden's J on out-of-fold training CV predictions, per model, computed strictly before the test set is loaded (code-order-verified). Phase 2 named this method as its explicit example and deferred final adoption to Phase 3 — formally documented as such, not presented as pre-registered. Full provenance audit (6 questions answered): `documentation/phase3/threshold_selection_audit.md`.

## P. Model-Selection Rule

**Retain all 5 original model families for downstream calibration/fairness/uncertainty phases** — this is a Phase 2-frozen rule (`model_development_protocol.md`), re-confirmed and re-applied, not a new Phase 3 choice. No model is declared a winner from test-set discrimination. Full documentation: `documentation/phase3/downstream_model_retention_rule.md` and `..._decision.md`.

## Q. Baseline Model Results

| model_name    |   cv_roc_auc |   test_roc_auc |   roc_auc_95ci_low |   roc_auc_95ci_high |   test_pr_auc |   sensitivity |   specificity |    ppv |    npv |     f1 |   threshold |
|:--------------|-------------:|---------------:|-------------------:|--------------------:|--------------:|--------------:|--------------:|-------:|-------:|-------:|------------:|
| logistic      |       0.8157 |         0.8334 |             0.8021 |              0.861  |        0.3725 |         0.75  |        0.7621 | 0.2447 | 0.9674 | 0.369  |      0.5173 |
| random_forest |       0.821  |         0.8343 |             0.8036 |              0.8611 |        0.3508 |         0.79  |        0.7359 | 0.2351 | 0.9715 | 0.3624 |      0.4499 |
| xgboost       |       0.8212 |         0.8429 |             0.8123 |              0.8693 |        0.3717 |         0.845 |        0.6773 | 0.212  | 0.977  | 0.339  |      0.4108 |
| lightgbm      |       0.8157 |         0.8394 |             0.8088 |              0.867  |        0.3729 |         0.795 |        0.7492 | 0.2457 | 0.9726 | 0.3754 |      0.4988 |
| mlp           |       0.8184 |         0.8229 |             0.7903 |              0.8532 |        0.3652 |         0.815 |        0.6644 | 0.1998 | 0.9722 | 0.3209 |      0.1065 |

Single authoritative table: `results/tables/phase3_final_baseline_results.csv` (discrimination metrics ONLY — no calibration/fairness/uncertainty).

## R. Confidence Intervals

Percentile bootstrap, n=2,000, paired resampling (same test participants across models), seed=42. **Formally documented as a Phase 3 methodological amendment** (Phase 2 did not freeze a Phase-3-specific CI procedure) — full specification: `documentation/phase3/inference_methodology_amendment.md`.

## S. FDR/Model Comparison

10 pairwise comparisons, Benjamini-Hochberg FDR at 0.05, family = baseline-model-discrimination-comparison ONLY (strictly separate from any future fairness-comparison family). **0 significant after correction.**

**Correct interpretation:** "No statistically significant pairwise superiority was demonstrated after FDR correction" — NOT "the models are equivalent" (no equivalence/non-inferiority test was performed). Effect sizes: max observed |AUC difference| = 0.02 (small magnitude, per pre-specified <0.01/0.01-0.02/>0.02 bins) — `results/tables/phase3_model_effect_sizes.csv`.

## T. PR-AUC / Prevalence Context

| model_name    |   pr_auc |   no_skill_baseline_pr_auc |   fold_improvement_over_baseline |
|:--------------|---------:|---------------------------:|---------------------------------:|
| logistic      |   0.3725 |                     0.0932 |                             4    |
| random_forest |   0.3508 |                     0.0932 |                             3.76 |
| xgboost       |   0.3717 |                     0.0932 |                             3.99 |
| lightgbm      |   0.3729 |                     0.0932 |                             4    |
| mlp           |   0.3652 |                     0.0932 |                             3.92 |

Test-set prevalence (no-skill PR-AUC baseline) = 9.32%. Observed PR-AUC (0.35-0.37) is ~3.7-4.0x the no-skill baseline — meaningfully above chance for this prevalence, but NOT described as "excellent" in absolute terms without this context.

## U. Hypothesis Interpretation

Phase 2's H1 was a directional expectation/range (ROC-AUC 0.75-0.85), not a formal statistical hypothesis test — no null/test-statistic was pre-specified. All 5 models' test ROC-AUC point estimates (0.823-0.843) fall within this range. **Correct language used throughout: "observed discrimination was consistent with the pre-specified H1 expectation"** — never "H1 was proven/confirmed." Full detail: `documentation/phase3/hypothesis_interpretation.md`.

## V. MLP Asymmetry

| comparison                                                                                   |   mlp_original_cv_roc_auc |   mlp_balanced_cv_roc_auc |   mlp_original_test_roc_auc |   mlp_balanced_test_roc_auc |   test_auc_diff_balanced_minus_original |   diff_95ci_low |   diff_95ci_high | ci_excludes_zero   | primary_retained_model                                                                                                            | conclusion                                                                                                                                                                                                                              |
|:---------------------------------------------------------------------------------------------|--------------------------:|--------------------------:|----------------------------:|----------------------------:|----------------------------------------:|----------------:|-----------------:|:-------------------|:----------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MLP_original (unweighted) vs MLP_balanced (training-fold-only 1:1 oversampling, sensitivity) |                    0.8184 |                    0.8207 |                      0.8229 |                      0.8335 |                                  0.0106 |          -0.005 |           0.0272 | False              | MLP_original (frozen retention rule: all 5 ORIGINAL model families retained; MLP_balanced is sensitivity-only, not a replacement) | Training-fold-only 1:1 oversampling did not produce a statistically detectable difference in MLP test discrimination; the original unweighted MLP result is not undermined by the class-imbalance asymmetry for this cohort/prevalence. |

A pre-specified, training-fold-only sensitivity analysis (1:1 random oversampling via `imblearn.pipeline.Pipeline`, resampling strictly inside CV folds, never touching held-out or test data) found the balanced-vs-original MLP test-AUC difference not statistically distinguishable. **MLP_original remains the primary retained model; MLP_balanced is reported as a sensitivity check only, never promoted to primary status.**

## W. Reproducibility

Granular hash table across dataset/split/feature-order/model/prediction/result-table categories (`results/tables/phase3_reproducibility_hashes.csv`, 24 artifacts) confirms **all 5 original baseline models and their predictions are byte-identical** to before this remediation began (10 by direct hash comparison, 5 by code audit for artifacts not separately hashed pre-remediation). An exact independent rerun (byte-for-byte identical results, only wall-clock timing differed) was performed and documented earlier — `documentation/phase3/reproducibility_registry.md` and `reproducibility_audit.md`.

## X. Environment

Exact pinned versions now recorded in `requirements-phase3-lock.txt` (scikit-learn==1.9.0, xgboost==3.4.1, lightgbm==4.7.0, imbalanced-learn==0.14.2, pandas==3.0.5, numpy==2.5.2, scipy==1.18.0, Python 3.14.3) — a genuine reproducibility improvement over the original loose-range `requirements-phase3.txt`. The `mongosh` environment incident from original Phase 3 setup remains disclosed and was not repeated in this remediation (no system packages modified).

## Y. Protocol Amendments

1. **Threshold-selection method (Youden's J):** Phase 2 named this as its explicit example and deferred final adoption to Phase 3 — Phase 3 formally adopted it. Clarification, not an unprecedented invention.
2. **CI/bootstrap/FDR methodology for baseline model comparison:** Phase 2 did not freeze a Phase-3-specific procedure. Phase 3 extended the closest existing Phase 2 convention (2,000-resample bootstrap, Benjamini-Hochberg FDR), documented explicitly as a Phase 3 amendment, not presented as pre-registered.
3. **MLP class-imbalance sensitivity analysis:** a genuine implementation gap in Phase 2's general imbalance policy (not anticipating sklearn's MLPClassifier API constraint) was resolved with a pre-specified, training-fold-only sensitivity analysis, per the remediation instructions' Option B.

None of these amendments altered the frozen Phase 2 cohort, outcome, predictor set, or missing-data strategy.

## Z. What Remains Deferred to Later Phases

Calibration analysis, fairness analysis, conformal/uncertainty analysis, and fairness mitigation — none performed here. Raw test-set probabilities and demographic metadata remain preserved and untouched for these phases.

## AA. Limitations

1. MLP's class-imbalance handling remains structurally different from the other 4 models (sklearn API constraint) even after the sensitivity analysis — the sensitivity result increases confidence this did not materially distort MLP's ranking, but does not eliminate the underlying asymmetry.
2. The CI/FDR methodology, while now fully documented and fixed before any comparison was computed, remains a Phase 3 clarification rather than a Phase-2-frozen procedure.
3. `validation_predictions_*.csv` files for the 5 original models were not separately hashed in the Part 3A pre-remediation snapshot (a scope gap in that snapshot, corrected for this remediation's own artifacts going forward); their unchanged status is confirmed by code audit rather than a direct pre/post hash comparison.

## AB. Final Phase 3 Readiness Decision

**PHASE 3 — COMPLETE AND FROZEN**

Every remediation completion criterion is satisfied: Phase 2 handoff independently re-verified; primary cohort/outcome/predictors confirmed unchanged; CV-vs-validation terminology corrected; test set locked and chronology-audited; preprocessing leakage audit passed; hyperparameter tuning confirmed development-data-only; threshold selection confirmed protocol-compliant; CI and FDR methodology explicitly documented; model-comparison interpretation corrected to avoid equivalence overclaiming; PR-AUC interpreted relative to prevalence; H1 interpreted as "consistent with," not "proven"; MLP asymmetry fully documented and sensitivity-tested; model-comparability matrix exists; raw probabilities preserved; all metrics reproducible and hash-verified; environment pinned exactly; clean rerun succeeded; original 20 tests AND new 24 remediation tests all pass (44/44 total); final baseline results table exists; downstream model-retention rule frozen and reconfirmed; no calibration, fairness, or uncertainty claim made; no mitigation performed; no unresolved blocker remains.

**Phase 4 (calibration, fairness, and uncertainty analysis) may now proceed using the frozen, remediated, hash-verified models and locked test predictions produced here.**

> **[CORRECTION APPENDED 2026-08-18, end-to-end audit — original sentence above left unmodified per the non-negotiable rule against silently rewriting frozen reports]:** at the time this sentence was written, "Phase 4" was used loosely as an umbrella term for all remaining work. `documentation/phase_numbering_crosswalk.md` (created afterward) formally splits this into three separate project phases: **Project Phase 4 = Calibration only** (mentor Phase 9), **Project Phase 5 = Fairness** (mentor Phase 10), **Project Phase 6 = Uncertainty** (mentor Phase 12). Read "Phase 4" above as "Phases 4–6" going forward; this is a terminology-only correction and changes no scientific claim in this report.
