# Phase 3.5 — Root-cause / Drift-to-Performance Analysis

Scope: read-only comparison of Phase 2 temporal drift against the completed Phase 3 temporal validation results. This phase reports only associations supported by repository evidence; it does not infer cause, update models, or modify frozen results.

## Source evidence used
- `results/temporal_validation/temporal_original_vs_validation_comparison.csv`
- `results/temporal_validation/temporal_discrimination_results.csv`
- `results/temporal_validation/temporal_calibration_results.csv`
- `results/temporal_validation/temporal_fairness_results.csv`
- `results/temporal_validation/temporal_conformal_results.csv`
- `results/temporal_validation/temporal_predictor_drift.csv`
- `results/temporal_validation/temporal_subgroup_composition_drift.csv`
- `results/temporal_validation/temporal_measurement_differences.csv`

## Executive summary
- The 2021–2023 cohort had higher outcome prevalence: 11.47% vs 9.31% (absolute increase +0.0216; +23.2%).
- The clearest direct predictor drift was ALP (`LBXSAPSI`): mean 77.6 -> 84.2 U/L, SMD 0.246, classified as CLEAR DRIFT.
- Age composition shifted toward older adults (60+ share 33.7% -> 42.8%), and BMI fairness deterioration remained consistent across all five models.
- All five models showed worse AUROC and sensitivity in the temporal cohort, with the largest declines in Random Forest and LightGBM. The pattern is consistent with the preserved subgroup/fairness drift, not with a causal claim.
- The repository evidence does not support a wholesale threshold or prediction-score shift as the main driver of performance deterioration; the evidence is better described as a composition/fairness drift pattern plus measurement/documented ALT bridge differences.

## 1) Phase 2 drift vs Phase 3 model change

| Model | AUROC change | Sensitivity change | Specificity change | Brier change | ECE change | Overall evidence classification |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Logistic Regression | -0.0515 | -0.0839 | -0.0209 | +0.0083 | -0.0120 | SUPPORTED ASSOCIATION |
| Random Forest | -0.0578 | -0.0991 | +0.0113 | +0.0044 | -0.0234 | SUPPORTED ASSOCIATION |
| XGBoost | -0.0605 | -0.1061 | +0.0066 | +0.0035 | -0.0237 | SUPPORTED ASSOCIATION |
| LightGBM | -0.0608 | -0.1200 | +0.0088 | +0.0035 | -0.0229 | SUPPORTED ASSOCIATION |
| MLP | -0.0415 | -0.0406 | -0.0104 | +0.0134 | -0.0082 | SUPPORTED ASSOCIATION |

Interpretation: the pattern is consistent across all five models but is not a causal explanation. The most consistent evidence is that model discrimination and sensitivity worsened in the higher-risk, older, and obese-heavy temporal cohort.

## 2) Prediction score distribution changes

The score-shift summaries were computed from the frozen original 2017–2020 predictions and the completed temporal prediction files without modifying the research codebase.

| Model | Original mean | Temporal mean | Mean delta | Original threshold | Temporal threshold | Prop above threshold (orig -> temp) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.3899 | 0.3993 | +0.0094 | 0.5173 | 0.5173 | 0.2856 -> 0.3055 |
| Random Forest | 0.3384 | 0.3364 | -0.0020 | 0.4499 | 0.4499 | 0.3131 -> 0.3031 |
| XGBoost | 0.3504 | 0.3481 | -0.0022 | 0.4108 | 0.4108 | 0.3714 -> 0.3646 |
| LightGBM | 0.3570 | 0.3556 | -0.0014 | 0.4988 | 0.4988 | 0.3015 -> 0.2916 |
| MLP | 0.1191 | 0.1251 | +0.0060 | 0.1065 | 0.1065 | 0.3802 -> 0.3951 |

Classification: `NOT SUPPORTED` for a large wholesale score shift as the main explanation. The score distributions stayed broadly similar, and the threshold exceed proportions did not change dramatically.

## 3) Prevalence and calibration comparison

The cohort prevalence increased from 9.31% to 11.47% (+0.0216; +23.2%). This pattern is reflected in the calibration summary:

- Logistic: calibration intercept -2.260 -> -2.001; slope 0.996 -> 0.906
- Random Forest: intercept -1.968 -> -1.640; slope 1.281 -> 1.031
- XGBoost: intercept -2.163 -> -1.781; slope 1.162 -> 0.934
- LightGBM: intercept -2.185 -> -1.798; slope 1.203 -> 0.947
- MLP: intercept -0.435 -> -0.371; slope 0.929 -> 0.833

Classification: `SUPPORTED ASSOCIATION` for the observed association between prevalence increase and calibration degradation, because the direction is consistent across models. This does not establish causation.

## 4) BMI fairness deterioration

The fairness evidence from `temporal_fairness_results.csv` shows all five models had worsening BMI sensitivity gaps.

- Logistic: 47.7 pp -> 68.9 pp (+21.2 pp)
- Random Forest: 31.6 pp -> 62.8 pp (+31.2 pp)
- XGBoost: 31.4 pp -> 67.7 pp (+36.4 pp)
- LightGBM: 27.1 pp -> 67.6 pp (+40.6 pp)
- MLP: 39.0 pp -> 71.9 pp (+32.9 pp)

BMI composition remained heavily weighted toward higher-risk groups, with obese individuals still accounting for ~38.6–40.9% of the cohort and their prevalence increasing from 15.99% to 20.15%.

Classification: `SUPPORTED ASSOCIATION`.

## 5) Age fairness change

Age composition shifted strongly toward older adults.

- 18–39: 33.9% -> 28.7%
- 40–59: 32.4% -> 28.5%
- 60+: 33.7% -> 42.8%

Age sensitivity gaps across models also worsened markedly:

- Logistic: -8.6 pp -> +10.0 pp, change +18.5 pp
- Random Forest: -13.2 pp -> +4.5 pp, change +17.7 pp
- XGBoost: -11.2 pp -> +6.4 pp, change +17.7 pp
- LightGBM: -14.1 pp -> +4.9 pp, change +19.1 pp
- MLP: -14.7 pp -> +3.3 pp, change +18.0 pp

Classification: `SUPPORTED ASSOCIATION`.

## 6) BMI × Age intersection analysis

The intersectional subgroup with the strongest composition and fairness pressure was the `Obese × 60+` subgroup.

- Original N / temporal N: 971 -> 788
- Prevalence: 21.2% -> 22.6%
- Overall coverage in temporal cohort: 0.72–0.77 depending on model, below the cohort-wide coverage for most models
- M4b coverage for this subgroup remained lower than overall coverage for all models, with the largest drop in XGBoost and Random Forest.

This is evidence of a distributional concentration in a higher-risk subgroup but not proof of a single cause. Classification: `SUPPORTED ASSOCIATION` for the pattern, not for causation.

## 7) Specific variables assessed

- ALP (`LBXSAPSI`): CLEAR DRIFT, strongest direct predictor shift. Supported association with performance loss.
- Bilirubin (`LBXSTB`): POSSIBLE DRIFT; observed but not isolated enough to classify as a sole driver.
- Platelets (`LBXPLTSI`): POSSIBLE DRIFT; observed but not enough repository evidence to isolate it as a driver.
- Age: POSSIBLE DRIFT in the 2017–2020 to 2021–2023 comparison; age-composition shift is strongly supported in the fairness summary.
- BMI: NO MATERIAL CHANGE in mean distribution, but composition and subgroup prevalence changes were large enough to influence fairness.
- ALT measurement difference: `LBXSATSI` was transformed in the temporal data via the documented bridge; classification `POSSIBLE EXPLANATION` only.

## 8) Cross-model consistency

All five models showed the same broad pattern:
- AUROC decline
- sensitivity decline
- worse BMI and age fairness gaps
- higher prevalence
- smaller or similar score-distribution shifts

This consistency supports a `SUPPORTED ASSOCIATION` classification for the overall drift-to-performance pattern and a `NOT SUPPORTED` classification for any single-cause mechanism.

## 9) Scientific boundary

This phase answers only: `WHAT CHANGED between 2017–2020 and 2021–2023?` It does not answer: `WHY did model performance change?`

The repository evidence supports the following limited conclusions:
- the temporal cohort was different in prevalence and composition;
- subgroup/fairness drift is consistently present;
- a documented ALT bridge was applied;
- model performance and fairness changed in the same direction;
- no single root-cause statement is supported by the repo evidence.

## 10) Final classification of relationships

- `NOT SUPPORTED`: a wholesale threshold shift or large score-distribution redistribution as the primary explanation.
- `POSSIBLE EXPLANATION`: ALT bridge and other measurement differences, because they are documented but not isolated in the frozen results.
- `OBSERVED`: bilirubin/platelets drift and other distributional changes when noted in the drift audit but not isolated as a model driver.
- `SUPPORTED ASSOCIATION`: prevalence increase, BMI/age fairness drift, and the alignment between drift and performance/fairness deterioration across all five models.
