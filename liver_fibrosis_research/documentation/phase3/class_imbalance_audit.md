# Class-Imbalance Audit (Model-by-Model)

**Generated:** 2026-08-18 16:59:42

| Model | Class weighting | Sampling | Other imbalance strategy |
|---|---|---|---|
| logistic | class_weight=balanced | None (native class weighting used instead) | N/A |
| random_forest | class_weight=balanced | None (native class weighting used instead) | N/A |
| xgboost | scale_pos_weight=9.745 | None (native class weighting used instead) | N/A |
| lightgbm | scale_pos_weight=9.745 | None (native class weighting used instead) | N/A |
| mlp | NONE | None in primary model (see sensitivity analysis) | N/A |

## Determination

Phase 2's `model_development_protocol.md` froze a general policy ("class weights, not SMOTE") but did not specify a per-model implementation and did NOT anticipate that sklearn's `MLPClassifier.fit()` accepts neither `class_weight` nor `sample_weight` -- unlike the other four estimators. **This is a genuine implementation gap Phase 2 did not foresee, not a Phase 2 drafting error requiring reopening Phase 2.**

**Decision: Option B applies.** A pre-specified, training-fold-only sensitivity analysis (MLP_balanced, via random oversampling to 1:1 class balance inside CV folds only, using `imblearn.pipeline.Pipeline` so resampling never touches held-out/validation/test rows) is run below and compared to MLP_original. **MLP_original remains the primary retained model for downstream phases** (consistent with the frozen retention rule -- see `downstream_model_retention_rule.md`); MLP_balanced is reported ONLY as a sensitivity check on whether the imbalance asymmetry materially changes MLP's ranking relative to the other four models, not as a replacement.

