# Hypothesis Interpretation (H1)

**Generated:** 2026-08-18 16:59:59

## Exact H1 wording from Phase 2

`documentation/phase2/primary_research_question.md`: *"H1 (accuracy): Standard ML models will achieve moderate discrimination (ROC-AUC in the 0.75-0.85 range) for significant fibrosis using routine demographic and laboratory variables..."*

**H1 was framed as a directional expectation/range, NOT a formal statistical hypothesis test with a pre-specified null and test statistic.** No one-sample test against a null AUC value, nor any other inferential test of H1 itself, was pre-specified in Phase 2 or performed in Phase 3.

## Observed results vs. H1

| model_name    |   roc_auc |   roc_auc_95ci_low |   roc_auc_95ci_high |
|:--------------|----------:|-------------------:|--------------------:|
| logistic      |    0.8334 |             0.8021 |              0.861  |
| random_forest |    0.8343 |             0.8036 |              0.8611 |
| xgboost       |    0.8429 |             0.8123 |              0.8693 |
| lightgbm      |    0.8394 |             0.8088 |              0.867  |
| mlp           |    0.8229 |             0.7903 |              0.8532 |

All 5 models' point-estimate test ROC-AUC values fall within the pre-specified 0.75-0.85 range: **True**.

## Correct interpretive language (used in the final report)

> **"The observed discrimination was consistent with the pre-specified H1 expectation."**

**Not used:** "H1 was proven," "H1 was confirmed," or any language implying a formal hypothesis test was conducted and passed. Consistency with a pre-specified range is a weaker and more accurate claim than statistical confirmation.
