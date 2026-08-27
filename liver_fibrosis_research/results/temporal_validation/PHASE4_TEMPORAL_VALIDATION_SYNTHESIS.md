# Phase 4 temporal-validation synthesis

## Design and verification

This synthesis reads completed Phase 3 artifacts only. The frozen five-model design, frozen thresholds, frozen Phase 6 conformal parameters, and frozen N0=0 M4b configuration were retained. The temporal cohort had **4,910** participants, **563** outcomes and **4,347** non-outcomes (prevalence **11.4664%**). Phase 3 input hashes and its before/after checks confirm exact SEQN matching and no modification of frozen inputs.

## Model performance

| model         | metric                |   locked_test_2017_2020 |   temporal_validation_2021_2023 |   difference | point_estimate_direction   |
|:--------------|:----------------------|------------------------:|--------------------------------:|-------------:|:---------------------------|
| logistic      | AUROC                 |                  0.8334 |                          0.7819 |      -0.0515 | WORSENED                   |
| logistic      | PR-AUC                |                  0.3725 |                          0.3916 |       0.0191 | IMPROVED                   |
| logistic      | sensitivity           |                  0.7500 |                          0.6661 |      -0.0839 | WORSENED                   |
| logistic      | specificity           |                  0.7621 |                          0.7412 |      -0.0209 | WORSENED                   |
| logistic      | calibration intercept |                 -2.2602 |                         -2.0011 |       0.2592 | IMPROVED                   |
| logistic      | calibration slope     |                  0.9961 |                          0.9058 |      -0.0903 | WORSENED                   |
| logistic      | ECE                   |                  0.2967 |                          0.2846 |      -0.0120 | IMPROVED                   |
| logistic      | Brier                 |                  0.1755 |                          0.1838 |       0.0083 | WORSENED                   |
| random_forest | AUROC                 |                  0.8343 |                          0.7765 |      -0.0578 | WORSENED                   |
| random_forest | PR-AUC                |                  0.3508 |                          0.3849 |       0.0341 | IMPROVED                   |
| random_forest | sensitivity           |                  0.7900 |                          0.6909 |      -0.0991 | WORSENED                   |
| random_forest | specificity           |                  0.7359 |                          0.7472 |       0.0113 | IMPROVED                   |
| random_forest | calibration intercept |                 -1.9679 |                         -1.6396 |       0.3283 | IMPROVED                   |
| random_forest | calibration slope     |                  1.2812 |                          1.0305 |      -0.2507 | WORSENED                   |
| random_forest | ECE                   |                  0.2452 |                          0.2218 |      -0.0234 | IMPROVED                   |
| random_forest | Brier                 |                  0.1458 |                          0.1502 |       0.0044 | WORSENED                   |
| xgboost       | AUROC                 |                  0.8429 |                          0.7824 |      -0.0605 | WORSENED                   |
| xgboost       | PR-AUC                |                  0.3717 |                          0.4132 |       0.0415 | IMPROVED                   |
| xgboost       | sensitivity           |                  0.8450 |                          0.7389 |      -0.1061 | WORSENED                   |
| xgboost       | specificity           |                  0.6773 |                          0.6839 |       0.0066 | IMPROVED                   |
| xgboost       | calibration intercept |                 -2.1629 |                         -1.7807 |       0.3822 | IMPROVED                   |
| xgboost       | calibration slope     |                  1.1616 |                          0.9340 |      -0.2276 | WORSENED                   |
| xgboost       | ECE                   |                  0.2572 |                          0.2335 |      -0.0237 | IMPROVED                   |
| xgboost       | Brier                 |                  0.1557 |                          0.1593 |       0.0035 | WORSENED                   |
| lightgbm      | AUROC                 |                  0.8394 |                          0.7786 |      -0.0608 | WORSENED                   |
| lightgbm      | PR-AUC                |                  0.3729 |                          0.4049 |       0.0320 | IMPROVED                   |
| lightgbm      | sensitivity           |                  0.7950 |                          0.6750 |      -0.1200 | WORSENED                   |
| lightgbm      | specificity           |                  0.7492 |                          0.7580 |       0.0088 | IMPROVED                   |
| lightgbm      | calibration intercept |                 -2.1846 |                         -1.7981 |       0.3865 | IMPROVED                   |
| lightgbm      | calibration slope     |                  1.2031 |                          0.9473 |      -0.2558 | WORSENED                   |
| lightgbm      | ECE                   |                  0.2638 |                          0.2409 |      -0.0229 | IMPROVED                   |
| lightgbm      | Brier                 |                  0.1603 |                          0.1638 |       0.0035 | WORSENED                   |
| mlp           | AUROC                 |                  0.8229 |                          0.7814 |      -0.0415 | WORSENED                   |
| mlp           | PR-AUC                |                  0.3652 |                          0.4075 |       0.0423 | IMPROVED                   |
| mlp           | sensitivity           |                  0.8150 |                          0.7744 |      -0.0406 | WORSENED                   |
| mlp           | specificity           |                  0.6644 |                          0.6540 |      -0.0104 | WORSENED                   |
| mlp           | calibration intercept |                 -0.4354 |                         -0.3711 |       0.0643 | IMPROVED                   |
| mlp           | calibration slope     |                  0.9293 |                          0.8332 |      -0.0962 | WORSENED                   |
| mlp           | ECE                   |                  0.0290 |                          0.0208 |      -0.0082 | IMPROVED                   |
| mlp           | Brier                 |                  0.0716 |                          0.0851 |       0.0134 | WORSENED                   |
| logistic      | PPV                   |                  0.2447 |                          0.2500 |       0.0053 | IMPROVED                   |
| logistic      | NPV                   |                  0.9674 |                          0.9449 |      -0.0225 | WORSENED                   |
| random_forest | PPV                   |                  0.2351 |                          0.2614 |       0.0263 | IMPROVED                   |
| random_forest | NPV                   |                  0.9715 |                          0.9492 |      -0.0223 | WORSENED                   |
| xgboost       | PPV                   |                  0.2120 |                          0.2324 |       0.0204 | IMPROVED                   |
| xgboost       | NPV                   |                  0.9770 |                          0.9529 |      -0.0241 | WORSENED                   |
| lightgbm      | PPV                   |                  0.2457 |                          0.2654 |       0.0197 | IMPROVED                   |
| lightgbm      | NPV                   |                  0.9726 |                          0.9474 |      -0.0252 | WORSENED                   |
| mlp           | PPV                   |                  0.1998 |                          0.2247 |       0.0249 | IMPROVED                   |
| mlp           | NPV                   |                  0.9722 |                          0.9572 |      -0.0150 | WORSENED                   |

AUROC declined for every model (about 0.041–0.064), while PR-AUC increased for every model. Threshold sensitivity/specificity changes were model-dependent. Thus discrimination is **MIXED**, not evidence that any model is generally better. Raw Brier score rose for every model, whereas ECE decreased; calibration intercepts remained negative and slopes were below 1. Calibration is **MIXED** and raw probability calibration still requires caution.

## Fairness

### BMI: obese versus normal reference

| model         |    n |   n_positive |   sensitivity |   absolute_sensitivity_gap_pp |   bh_fdr_adjusted_p | significant_after_fdr_0_05   |
|:--------------|-----:|-------------:|--------------:|------------------------------:|--------------------:|:-----------------------------|
| logistic      | 1896 |          382 |        0.8272 |                       68.8764 |              0.0000 | True                         |
| random_forest | 1896 |          382 |        0.8586 |                       62.7870 |              0.0000 | True                         |
| xgboost       | 1896 |          382 |        0.8927 |                       67.7286 |              0.0000 | True                         |
| lightgbm      | 1896 |          382 |        0.8455 |                       67.6319 |              0.0000 | True                         |
| mlp           | 1896 |          382 |        0.9346 |                       71.9170 |              0.0000 | True                         |

### Age: 60+ versus 40–59 reference

| model         |    n |   n_positive |   sensitivity |   absolute_sensitivity_gap_pp |   bh_fdr_adjusted_p | significant_after_fdr_0_05   |
|:--------------|-----:|-------------:|--------------:|------------------------------:|--------------------:|:-----------------------------|
| logistic      | 2102 |          282 |        0.7411 |                        9.9830 |              0.0220 | True                         |
| random_forest | 2102 |          282 |        0.7411 |                        4.5483 |              0.3100 | False                        |
| xgboost       | 2102 |          282 |        0.7979 |                        6.4177 |              0.1070 | False                        |
| lightgbm      | 2102 |          282 |        0.7234 |                        4.9491 |              0.2320 | False                        |
| mlp           | 2102 |          282 |        0.8156 |                        3.2994 |              0.3630 | False                        |

The original BMI sensitivity disparity remained and was substantially larger temporally: obese-versus-normal gaps were 62.8–71.9 percentage points, FDR-significant for all five models. The age 60+ disparity changed direction: 60+ sensitivity was modestly higher than 40–59 (3.3–10.0 points), statistically significant only for logistic regression. Lower sensitivity among ages 18–39 was significant for logistic regression, random forest, XGBoost, and MLP. Sex findings were mixed (female sensitivity lower and FDR-significant for logistic regression and XGBoost); race/ethnicity contrasts were not FDR-significant. BMI × Age remains problematic descriptively: obese 60+ sensitivity was very high but paired with low specificity, while normal-BMI cells had markedly low sensitivity; these exploratory cells were not given new post-hoc FDR claims.

Fairness is **WORSENED** overall because the pre-specified BMI gap persisted and enlarged. Sex/race stability is **MIXED**.

## Conformal transportability

| model         | scope                  |   coverage |   coverage_ci_lower |   coverage_ci_upper |   mean_set_size |   singleton_rate |   doubleton_rate |
|:--------------|:-----------------------|-----------:|--------------------:|--------------------:|----------------:|-----------------:|-----------------:|
| logistic      | overall                |     0.9022 |              0.8936 |              0.9102 |          1.4527 |           0.5473 |           0.4527 |
| logistic      | bmi_obese              |     0.8128 |              0.7946 |              0.8297 |          1.5723 |           0.4277 |           0.5723 |
| logistic      | age_60plus             |     0.8654 |              0.8501 |              0.8793 |          1.6227 |           0.3773 |           0.6227 |
| logistic      | bmi_obese_x_age_60plus |     0.7195 |              0.6872 |              0.7498 |          1.5622 |           0.4378 |           0.5622 |
| random_forest | overall                |     0.8906 |              0.8816 |              0.8991 |          1.2405 |           0.7595 |           0.2405 |
| random_forest | bmi_obese              |     0.7901 |              0.7712 |              0.8078 |          1.3803 |           0.6197 |           0.3803 |
| random_forest | age_60plus             |     0.8749 |              0.8600 |              0.8883 |          1.3658 |           0.6342 |           0.3658 |
| random_forest | bmi_obese_x_age_60plus |     0.7652 |              0.7344 |              0.7935 |          1.5216 |           0.4784 |           0.5216 |
| xgboost       | overall                |     0.8825 |              0.8732 |              0.8912 |          1.2853 |           0.7147 |           0.2853 |
| xgboost       | bmi_obese              |     0.7700 |              0.7506 |              0.7884 |          1.3982 |           0.6018 |           0.3982 |
| xgboost       | age_60plus             |     0.8492 |              0.8333 |              0.8639 |          1.4191 |           0.5809 |           0.4191 |
| xgboost       | bmi_obese_x_age_60plus |     0.6967 |              0.6637 |              0.7278 |          1.4632 |           0.5368 |           0.4632 |
| lightgbm      | overall                |     0.8937 |              0.8848 |              0.9020 |          1.3191 |           0.6809 |           0.3191 |
| lightgbm      | bmi_obese              |     0.7896 |              0.7706 |              0.8073 |          1.4378 |           0.5622 |           0.4378 |
| lightgbm      | age_60plus             |     0.8782 |              0.8635 |              0.8915 |          1.4848 |           0.5152 |           0.4848 |
| lightgbm      | bmi_obese_x_age_60plus |     0.7500 |              0.7186 |              0.7790 |          1.5457 |           0.4543 |           0.5457 |
| mlp           | overall                |     0.8786 |              0.8692 |              0.8875 |          0.9713 |           0.9713 |           0.0000 |
| mlp           | bmi_obese              |     0.7827 |              0.7636 |              0.8007 |          0.9346 |           0.9346 |           0.0000 |
| mlp           | age_60plus             |     0.8492 |              0.8333 |              0.8639 |          0.9591 |           0.9591 |           0.0000 |
| mlp           | bmi_obese_x_age_60plus |     0.7335 |              0.7016 |              0.7632 |          0.9023 |           0.9023 |           0.0000 |

Marginal coverage stayed near 90% (87.9%–90.2%), but BMI-obese coverage was 77.0%–81.3%, age-60+ coverage 84.9%–87.8%, and the BMI-obese × age-60+ intersection was 69.7%–76.5%. Hence the original pattern—acceptable-looking global coverage masking subgroup undercoverage—persists. Intersectional baseline coverage was somewhat higher for several models than in the locked test but remains far below 90%. Conformal reliability is **MIXED**, not stable subgroup transportability.

## Frozen M4b (N0 = 0)

| model         | scope                  |   coverage |   coverage_ci_lower |   coverage_ci_upper |   mean_set_size |   singleton_rate |   doubleton_rate | intersection_target_ge_90_maintained   |
|:--------------|:-----------------------|-----------:|--------------------:|--------------------:|----------------:|-----------------:|-----------------:|:---------------------------------------|
| logistic      | overall                |     0.9189 |              0.9110 |              0.9263 |          1.0660 |           0.9328 |           0.0666 | False                                  |
| logistic      | bmi_obese              |     0.8850 |              0.8699 |              0.8986 |          1.1704 |           0.8296 |           0.1704 | False                                  |
| logistic      | age_60plus             |     0.9087 |              0.8956 |              0.9202 |          1.0999 |           0.9001 |           0.0999 | False                                  |
| logistic      | bmi_obese_x_age_60plus |     0.8858 |              0.8617 |              0.9061 |          1.2614 |           0.7386 |           0.2614 | False                                  |
| random_forest | overall                |     0.9216 |              0.9137 |              0.9288 |          1.0853 |           0.9143 |           0.0855 | True                                   |
| random_forest | bmi_obese              |     0.8898 |              0.8749 |              0.9031 |          1.2189 |           0.7811 |           0.2189 | True                                   |
| random_forest | age_60plus             |     0.9158 |              0.9032 |              0.9269 |          1.1356 |           0.8644 |           0.1356 | True                                   |
| random_forest | bmi_obese_x_age_60plus |     0.9010 |              0.8782 |              0.9200 |          1.3553 |           0.6447 |           0.3553 | True                                   |
| xgboost       | overall                |     0.9177 |              0.9097 |              0.9251 |          1.0648 |           0.9348 |           0.0650 | False                                  |
| xgboost       | bmi_obese              |     0.8797 |              0.8643 |              0.8936 |          1.1672 |           0.8328 |           0.1672 | False                                  |
| xgboost       | age_60plus             |     0.9058 |              0.8926 |              0.9176 |          1.0909 |           0.9091 |           0.0909 | False                                  |
| xgboost       | bmi_obese_x_age_60plus |     0.8769 |              0.8521 |              0.8980 |          1.2398 |           0.7602 |           0.2398 | False                                  |
| lightgbm      | overall                |     0.9179 |              0.9099 |              0.9253 |          1.0633 |           0.9350 |           0.0642 | False                                  |
| lightgbm      | bmi_obese              |     0.8803 |              0.8649 |              0.8941 |          1.1624 |           0.8376 |           0.1624 | False                                  |
| lightgbm      | age_60plus             |     0.9053 |              0.8921 |              0.9171 |          1.0818 |           0.9182 |           0.0818 | False                                  |
| lightgbm      | bmi_obese_x_age_60plus |     0.8731 |              0.8480 |              0.8945 |          1.2094 |           0.7906 |           0.2094 | False                                  |
| mlp           | overall                |     0.9216 |              0.9137 |              0.9288 |          1.0713 |           0.9267 |           0.0723 | False                                  |
| mlp           | bmi_obese              |     0.8877 |              0.8727 |              0.9011 |          1.1851 |           0.8149 |           0.1851 | False                                  |
| mlp           | age_60plus             |     0.9110 |              0.8981 |              0.9225 |          1.0994 |           0.9006 |           0.0994 | False                                  |
| mlp           | bmi_obese_x_age_60plus |     0.8858 |              0.8617 |              0.9061 |          1.2602 |           0.7398 |           0.2602 | False                                  |

The ≥90% temporal intersectional target held **only for random forest** (90.1%). It did not hold for logistic regression (88.6%), XGBoost (87.7%), LightGBM (87.3%), or MLP (88.6%). The same models therefore did not succeed as in the original N0=0 report: original success was four of five (all except LightGBM), versus one of five temporally. LightGBM remained below target. Overall set sizes were lower temporally (about 1.06–1.09), but this efficiency gain came with loss of intersectional target attainment, so the M4b trade-off did not remain similar. M4b performance is **WORSENED**.

## Main scientific story and interpretation

- Reasonable rank discrimination remains present, but AUROC decreased in all five models; temporal discrimination is mixed.
- The evidence continues to show that raw probabilities are not well calibrated; temporal Brier deterioration prevents any claim of calibration improvement despite lower ECE.
- BMI sensitivity disparity is reproduced and stronger. Age effects are not reproduced in the same direction: 60+ disparity is smaller/reversed, while lower sensitivity in 18–39 is evident in most models.
- Global conformal coverage continues to conceal substantial BMI, age, and intersectional undercoverage.
- The frozen N0=0 M4b configuration no longer delivers its intersectional target for most models; no tuning or replacement was performed.

## Paper-level conclusion and limitations

The overall classification is **PARTIAL TEMPORAL REPLICATION**. The temporal data reproduce useful discrimination, persistent calibration concerns, severe BMI-related disparity, and the central limitation of marginal conformal coverage. They do not reproduce reliable N0=0 M4b intersectional protection for most models, and age-related patterns changed. This is a later-cohort evaluation using frozen models and does not establish clinical readiness, causal explanations, broad external generalization, or a basis for model updating. Differences in cohort composition and outcome prevalence are observed facts here, not explanations for performance change.

No Phase 3 result was overwritten or recalculated; no primary research artifact was changed.
