# Future Model Development Protocol (Phase 2Q)

**Generated:** 2026-08-18 — defines the Phase 3 experimental structure. NO model is trained in Phase 2.

1. **Training set / Final test set.** 70% train / 30% test, stratified on the primary outcome (LUXSMED ≥
   8.2 kPa), drawn once from the primary analysis dataset (`data/processed/analysis_dataset_primary.parquet`)
   using a fixed random seed (below). **The test set is locked immediately after the split and touched
   exactly once, at final evaluation** (non-negotiable rules 4, 12).
2. **Validation / CV strategy.** 5-fold stratified cross-validation within the training set only, for
   hyperparameter tuning and model selection.
3. **Preprocessing placement.** All preprocessing (scaling for Logistic Regression/MLP; no scaling needed
   for tree models; any encoding) is fit exclusively on the training folds within each CV iteration, and
   only the fitted transform is applied to validation folds and, later, the test set — never fit on
   validation/test data (non-negotiable rule 11).
4. **Random seed.** A single fixed seed will be recorded in `PHASE2_PROTOCOL_FREEZE.md` at the start of
   Phase 3 and reused for the train/test split, CV fold assignment, and all stochastic model components
   (Random Forest, XGBoost/LightGBM, MLP initialization), to keep Phase 3 reproducible.
5. **Repeated CV.** Single 5-fold CV is the primary tuning strategy; repeated (e.g. 5×5) CV may be used as
   a secondary robustness check on hyperparameter stability, not as a Phase 2 decision requiring separate
   freezing (it is a Phase 3 implementation detail, non-scientific).
6. **Hyperparameter tuning strategy.** Grid or randomized search within the training-set CV loop only,
   using the primary discrimination metric (ROC-AUC, cross-validated) as the tuning objective — the test
   set is never used for tuning.
7. **Model selection rule.** Best cross-validated ROC-AUC within each model family selects that family's
   hyperparameters; no family is declared "the" final model in Phase 2 — per the research plan, model
   comparison is not this project's novelty (`info.md` Phase 6), and Phase 3 will report all four
   families' calibration/fairness/uncertainty profiles rather than picking one "winner" on discrimination
   alone.
8. **Final model selection rule (if a single deployable model is eventually required).** Deferred to
   Phase 3, to be decided using the FULL primary metric suite (discrimination + calibration + fairness +
   uncertainty jointly), not discrimination alone — consistent with the thesis's central "accuracy is not
   sufficient" premise.
9. **Test-set lock.** Once split, the test set's rows are fixed by `SEQN` list and stored; any subsequent
   pipeline change must reuse the identical stored test-set `SEQN` list, not regenerate the split.
10. **Resampling (SMOTE, oversampling).** **NOT used now.** If considered in Phase 3, it is a
    training-fold-only operation, refit within each CV fold, and **never** applied to validation or test
    data (non-negotiable rule 12) — consistent with the original research plan's caution against
    automatically applying SMOTE (`info.md` Phase 5) in favor of class weights or natural-prevalence
    evaluation as the default.
