# Phase 1 BMI fairness reproduction summary

**Analysis status: REPRODUCED.** The historical BMI sensitivity disparity was reproduced from the locked test set, raw Phase 3 predictions, and frozen thresholds. No model was retrained, no threshold was changed, and no intervention was selected.

| Model | Normal-BMI N | Normal-BMI positives | Obese N | Obese positives | Normal-BMI sensitivity | Obese sensitivity | Difference | 95% CI | BH-FDR q |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| logistic | 562 | 22 | 883 | 140 | 0.409091 | 0.885714 | 47.6623 pp | 25.6847 to 69.5017 | 0.000000 |
| random_forest | 562 | 22 | 883 | 140 | 0.590909 | 0.907143 | 31.6234 pp | 10.2285 to 53.3570 | 0.006000 |
| xgboost | 562 | 22 | 883 | 140 | 0.636364 | 0.950000 | 31.3636 pp | 11.1043 to 53.5666 | 0.003000 |
| lightgbm | 562 | 22 | 883 | 140 | 0.636364 | 0.907143 | 27.0779 pp | 6.7666 to 48.5048 | 0.006000 |
| mlp | 562 | 22 | 883 | 140 | 0.545455 | 0.935714 | 39.0260 pp | 18.6747 to 60.6754 | 0.000000 |

## Verification answers

1. **Authoritative BMI finding reproduced:** Yes. All five model-specific reproduced disparities and inference values match the historical `results/fairness/fairness_inference.csv` rows.
2. **All five models agree:** Yes. Each has a positive Obese-minus-Normal sensitivity difference and is FDR-significant.
3. **Numerical discrepancy:** No substantive discrepancy was found.
4. **Rounding:** Any difference is representation/rounding only; full-precision calculations agree with historical rounded output.
5. **Phase 2:** Safe to begin under the sequential workflow; Phase 2 was not started automatically.

## Source trace

Primary cohort: `data/processed/analysis_dataset_primary.parquet`; locked test: `data/processed/splits/test_ids.csv`; canonical BMI bins and thresholds: `src/phase5_common.py`; raw predictions: `results/predictions/test_predictions_<model>.csv`; historical inference: `results/fairness/fairness_inference.csv`. The recalibrated predictions artifact was verified as available but was not used to alter the historical Phase 5 raw-threshold reproduction.

**Status: REPRODUCED. Phase 2 may begin, but was not started automatically.**
