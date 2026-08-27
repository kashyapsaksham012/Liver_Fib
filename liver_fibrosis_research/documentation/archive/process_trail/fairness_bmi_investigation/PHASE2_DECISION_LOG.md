# Phase 2 Decision Log

| Decision | Evidence and rationale |
|---|---|
| Use OOF only | Existing `validation_predictions_<model>.csv` files each contained 5,007 IDs matching the training/validation prediction partition; outcome linkage matched the frozen primary outcome. |
| Preserve frozen definitions | Outcome, ten predictors, BMI bins, age bins, and model-specific thresholds were taken from the existing frozen implementation. |
| Evaluate a fixed grid | Used thresholds 0.00–1.00 by 0.01. No threshold was selected or recommended. |
| Treat frozen thresholds as reference only | Threshold crossing was descriptive and did not optimize sensitivity, specificity, or fairness. |
| Do not call AUROC differences definitive | Bootstrap intervals overlap and the Normal-BMI positive count is 50. |
| Classify as mixed mechanism | All models show positive- and negative-case score shifts, persistent threshold behavior, group calibration differences, and possible but uncertain ranking/age contributions. |
| Mark BMI sensitivity-cohort comparison unavailable | Existing CAND_2/CAND_3/8.0-kPa artifacts report overall analyses, not BMI-stratified Phase 2 mechanism results. |
| Protect the next phase | No mitigation or confirmatory locked-test evaluation is authorized by this Phase 2 output. |

## Execution status

**PHASE 2 COMPLETE — DIAGNOSTIC ONLY.** The locked test set was not used for new discovery. The master report was not modified.
