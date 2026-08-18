# Threshold-Selection Provenance Audit

**Generated:** 2026-08-18 16:59:58

## 1. Was Youden's J explicitly frozen by Phase 2?

**Partially.** `documentation/phase2/evaluation_metrics_protocol.md` states: *"an operating threshold to be determined in Phase 3 by a pre-specified rule (e.g. Youden's J on the training/CV data only, never the test set)"* -- Phase 2 named Youden's J as the recommended example method and explicitly deferred the final selection to Phase 3. Phase 3 formally adopted this named example as the frozen implementation. **This is a Phase 3 protocol clarification (Phase 2 named the method; Phase 3 operationalized it), not an unprecedented invention.**

## 2. Was the threshold based entirely on training/CV predictions?

**Yes.** Verified by code order: `youdens_j_threshold()` is called on out-of-fold training predictions at line index 2149 of `phase3_06_threshold_and_test_eval.py`, which precedes the test-set load at line index 2974 in the same file. Order check: PASS.

## 3. Was the test set untouched during threshold selection?

**Yes** — same evidence as (2).

## 4. Was the threshold the same across all models?

**No — each model has its own threshold**, computed from that model's own out-of-fold CV predictions:

| model_name    | method                                            |   threshold | source                                         |
|:--------------|:--------------------------------------------------|------------:|:-----------------------------------------------|
| logistic      | Youden's J on out-of-fold training CV predictions |      0.5173 | training partition only, test set not accessed |
| random_forest | Youden's J on out-of-fold training CV predictions |      0.4499 | training partition only, test set not accessed |
| xgboost       | Youden's J on out-of-fold training CV predictions |      0.4108 | training partition only, test set not accessed |
| lightgbm      | Youden's J on out-of-fold training CV predictions |      0.4988 | training partition only, test set not accessed |
| mlp           | Youden's J on out-of-fold training CV predictions |      0.1065 | training partition only, test set not accessed |

## 5. If the threshold differed by model, was that allowed?

**Yes.** Nothing in the frozen protocol requires a single shared threshold across model families, and per-model thresholding is standard practice (different models produce differently-scaled/shaped probability distributions, so a shared threshold would not be meaningful). This is a reasonable, defensible operationalization, not a deviation.

## 6. Were any thresholds manually adjusted after viewing test performance?

**No.** Every threshold in the table above was computed programmatically from `results/predictions/validation_predictions_<model>.csv` (out-of-fold training predictions) before `phase3_06_threshold_and_test_eval.py` loads `test_ids.csv`. No manual override exists anywhere in the codebase.

## Conclusion

**PASSED** — threshold selection is protocol-compliant and leakage-safe.
