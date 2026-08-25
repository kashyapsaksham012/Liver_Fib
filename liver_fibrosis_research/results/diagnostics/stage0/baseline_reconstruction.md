# Baseline Reconstruction Report

This report reconstructs the baseline performance of the five primary models (**Logistic Regression, Random Forest, XGBoost, LightGBM, MLP**) on the locked test set (N = 2,146), verified from the project's own frozen results.

---

## 1. Model Discrimination
Below are the baseline model discrimination metrics on the locked test set:

| Model | test_roc_auc | ROC-AUC 95% CI | Sensitivity | Specificity | PPV | NPV | F1 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **LOGISTIC** | 0.8334 | [0.8021, 0.8610] | 0.7500 | 0.7621 | 0.2447 | 0.9674 | 0.3690 |
| **RANDOM_FOREST** | 0.8343 | [0.8036, 0.8611] | 0.7900 | 0.7359 | 0.2351 | 0.9715 | 0.3624 |
| **XGBOOST** | 0.8429 | [0.8123, 0.8693] | 0.8450 | 0.6773 | 0.2120 | 0.9770 | 0.3390 |
| **LIGHTGBM** | 0.8394 | [0.8088, 0.8670] | 0.7950 | 0.7492 | 0.2457 | 0.9726 | 0.3754 |
| **MLP** | 0.8229 | [0.7903, 0.8532] | 0.8150 | 0.6644 | 0.1998 | 0.9722 | 0.3209 |

---

## 2. Model Calibration (Raw vs. Recalibrated)
All models except MLP were class-weighted/resampled during training, resulting in severe raw calibration intercept shifts (prior shifts). Recalibration was performed using Platt scaling fit on CV out-of-fold training data.

| Model | Raw Intercept | Recal Intercept | Raw Slope | Recal Slope | Raw Brier | Recal Brier | Raw ECE | Recal ECE |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **LOGISTIC** | -2.260 | -0.154 | 0.996 | 0.939 | 0.1755 | 0.0705 | 0.2967 | 0.0172 |
| **RANDOM_FOREST** | -1.968 | 0.024 | 1.281 | 1.069 | 0.1458 | 0.0709 | 0.2452 | 0.0113 |
| **XGBOOST** | -2.163 | 0.124 | 1.162 | 1.118 | 0.1557 | 0.0694 | 0.2572 | 0.0152 |
| **LIGHTGBM** | -2.185 | 0.142 | 1.203 | 1.133 | 0.1603 | 0.0696 | 0.2638 | 0.0143 |
| **MLP** | -0.435 | -0.119 | 0.929 | 1.121 | 0.0716 | 0.0715 | 0.0290 | 0.0264 |

---

## 3. Subgroup Fairness Disparities (Sensitivity)
Primary fairness assessment evaluates the sensitivity disparity (Equal Opportunity) between targeted categories on the locked test set.

### Obese vs. Normal BMI
| Model | Obese Sens | Normal BMI Sens | Disparity (pp) | 95% Bootstrap CI (pp) | FDR Significant? |
|:---|:---:|:---:|:---:|:---:|:---:|
| **LOGISTIC** | 0.8857 | 0.4091 | 47.66 | [25.68, 69.50] | True |
| **RANDOM_FOREST** | 0.9071 | 0.5909 | 31.62 | [10.23, 53.36] | True |
| **XGBOOST** | 0.9500 | 0.6364 | 31.36 | [11.10, 53.57] | True |
| **LIGHTGBM** | 0.9071 | 0.6364 | 27.08 | [6.77, 48.50] | True |
| **MLP** | 0.9357 | 0.5455 | 39.03 | [18.67, 60.68] | True |

### Age 60+ vs. 40-59
| Model | Age 60+ Sens | Age 40-59 Sens | Disparity (pp) | 95% Bootstrap CI (pp) | FDR Significant? |
|:---|:---:|:---:|:---:|:---:|:---:|
| **LOGISTIC** | 0.7327 | 0.8182 | -8.55 | [-21.02, 4.21] | False |
| **RANDOM_FOREST** | 0.7624 | 0.8939 | -13.16 | [-23.89, -1.95] | True |
| **XGBOOST** | 0.8119 | 0.9242 | -11.24 | [-20.86, -1.83] | True |
| **LIGHTGBM** | 0.7525 | 0.8939 | -14.15 | [-24.95, -2.21] | True |
| **MLP** | 0.7624 | 0.9091 | -14.67 | [-25.55, -4.03] | True |

---

## 4. Conformal Uncertainty & Efficiency
Nominal target coverage is set to **90%** (alpha = 0.10).

| Model | Marginal Cov | Marginal Set Size | Obese Coverage | Normal Coverage | Age 60+ Coverage | Age 40-59 Coverage |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LOGISTIC** | 0.9082 | 1.432 | 0.8233 | 0.9680 | 0.8489 | 0.9188 |
| **RANDOM_FOREST** | 0.8961 | 1.232 | 0.8018 | 0.9644 | 0.8556 | 0.8932 |
| **XGBOOST** | 0.8812 | 1.271 | 0.7678 | 0.9609 | 0.8111 | 0.8902 |
| **LIGHTGBM** | 0.8961 | 1.312 | 0.7916 | 0.9698 | 0.8475 | 0.9008 |
| **MLP** | 0.8919 | 0.969 | 0.8086 | 0.9537 | 0.8381 | 0.8842 |

---

## 5. Existing Mitigation (Before vs. After Mondrian Conformal)
Under Mondrian conformal mitigation (Phase 7), specific targets are set for Obese and Age 60+ groups.

| Model | Dimension | Category | Cov Before | Cov After | Cov Change (pp) | Set Size Before | Set Size After |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **LOGISTIC** | bmi | Obese | 0.8233 | 0.8935 | 7.02 | 1.562 | 1.725 |
| **RANDOM_FOREST** | age | 60+ | 0.8556 | 0.8839 | 2.83 | 1.383 | 1.474 |
| **RANDOM_FOREST** | bmi | Obese | 0.8018 | 0.8743 | 7.25 | 1.332 | 1.541 |
| **XGBOOST** | age | 60+ | 0.8111 | 0.9001 | 8.91 | 1.408 | 1.642 |
| **XGBOOST** | bmi | Obese | 0.7678 | 0.8732 | 10.53 | 1.357 | 1.598 |
| **LIGHTGBM** | age | 60+ | 0.8475 | 0.8704 | 2.29 | 1.480 | 1.556 |
| **LIGHTGBM** | bmi | Obese | 0.7916 | 0.8664 | 7.47 | 1.414 | 1.592 |
| **MLP** | age | 60+ | 0.8381 | 0.8799 | 4.18 | 0.950 | 1.026 |
| **MLP** | bmi | Obese | 0.8086 | 0.8879 | 7.93 | 0.935 | 1.103 |
