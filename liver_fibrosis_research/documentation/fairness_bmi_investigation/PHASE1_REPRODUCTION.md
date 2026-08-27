# Phase 1 BMI fairness reproduction

## Method

The reproduction followed the authoritative Phase 5 implementation: locked test IDs, primary outcome `outcome_primary_8.2kPa`, raw Phase 3 test probabilities, and model-specific frozen thresholds. BMI categories use the exact `pd.cut` bins in `src/phase5_common.py`. The analysis was descriptive/reproductive only; it did not fit, tune, retrain, recalibrate, or optimize.

## Reproduced group metrics

| Model | Group | N | Positives | Negatives | Prevalence | Sensitivity | Specificity | PPV | NPV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| logistic | Normal | 562 | 22 | 540 | 0.039145907 | 0.409090909 | 0.961111111 | 0.300000000 | 0.975563910 |
| logistic | Obese | 883 | 140 | 743 | 0.158550396 | 0.885714286 | 0.523553163 | 0.259414226 | 0.960493827 |
| random_forest | Normal | 562 | 22 | 540 | 0.039145907 | 0.590909091 | 0.924074074 | 0.240740741 | 0.982283465 |
| random_forest | Obese | 883 | 140 | 743 | 0.158550396 | 0.907142857 | 0.485868102 | 0.249508841 | 0.965240642 |
| xgboost | Normal | 562 | 22 | 540 | 0.039145907 | 0.636363636 | 0.888888889 | 0.189189189 | 0.983606557 |
| xgboost | Obese | 883 | 140 | 743 | 0.158550396 | 0.950000000 | 0.415881561 | 0.234567901 | 0.977848101 |
| lightgbm | Normal | 562 | 22 | 540 | 0.039145907 | 0.636363636 | 0.938888889 | 0.297872340 | 0.984466019 |
| lightgbm | Obese | 883 | 140 | 743 | 0.158550396 | 0.907142857 | 0.503364738 | 0.256048387 | 0.966408269 |
| mlp | Normal | 562 | 22 | 540 | 0.039145907 | 0.545454545 | 0.929629630 | 0.240000000 | 0.980468750 |
| mlp | Obese | 883 | 140 | 743 | 0.158550396 | 0.935714286 | 0.375504711 | 0.220168067 | 0.968750000 |

## Inference and reproduction status

| Model | Obese-minus-Normal difference (pp) | 95% CI (pp) | Raw p | BH-FDR q | Significant after FDR | Status |
|---|---:|---|---:|---:|---|---|
| logistic | 47.6623 | 25.6847 to 69.5017 | 0.000000 | 0.000000 | True | **REPRODUCED** |
| random_forest | 31.6234 | 10.2285 to 53.3570 | 0.004000 | 0.006000 | True | **REPRODUCED** |
| xgboost | 31.3636 | 11.1043 to 53.5666 | 0.002000 | 0.003000 | True | **REPRODUCED** |
| lightgbm | 27.0779 | 6.7666 to 48.5048 | 0.004000 | 0.006000 | True | **REPRODUCED** |
| mlp | 39.0260 | 18.6747 to 60.6754 | 0.000000 | 0.000000 | True | **REPRODUCED** |

## Determination

The previously established Normal-BMI versus Obese sensitivity deficit was reproduced for all five models. The point differences span the historically reported 27.1–47.7 percentage-point range. Counts agree exactly; historical inference values agree within the source file's rounding precision. No substantive numerical discrepancy was identified.

## Source paths

- `data/processed/analysis_dataset_primary.parquet`
- `data/processed/splits/test_ids.csv`
- `src/phase5_common.py`
- `results/predictions/test_predictions_logistic.csv`
- `results/predictions/test_predictions_random_forest.csv`
- `results/predictions/test_predictions_xgboost.csv`
- `results/predictions/test_predictions_lightgbm.csv`
- `results/predictions/test_predictions_mlp.csv`
- `results/fairness/subgroup_discrimination_metrics.csv`
- `results/fairness/fairness_inference.csv`
- `results/tables/phase2_predictor_registry.csv`

**Phase 1 status: REPRODUCED. Phase 2 is safe to begin.**
