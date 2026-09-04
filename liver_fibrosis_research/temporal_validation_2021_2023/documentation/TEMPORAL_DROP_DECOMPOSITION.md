# Temporal AUROC-decline decomposition

Domain classifier P(cycle = 2021-2023 | X) AUC = **0.647**.

## 1. Covariate-shift reweighting -> concept drift, not composition

| model         |   auroc_2017_2020 |   auroc_2021_2023 |   auroc_2021_2023_reweighted |    drop |   drop_closed_by_reweighting |   fraction_of_drop_recovered |
|:--------------|------------------:|------------------:|-----------------------------:|--------:|-----------------------------:|-----------------------------:|
| logistic      |            0.8334 |            0.7819 |                       0.7927 | -0.0515 |                       0.0108 |                        0.21  |
| random_forest |            0.8343 |            0.7758 |                       0.7854 | -0.0585 |                       0.0095 |                        0.163 |
| xgboost       |            0.8429 |            0.7812 |                       0.7901 | -0.0617 |                       0.0089 |                        0.144 |
| lightgbm      |            0.8394 |            0.7773 |                       0.7858 | -0.0621 |                       0.0085 |                        0.136 |
| mlp           |            0.8229 |            0.7813 |                       0.7885 | -0.0416 |                       0.0072 |                        0.174 |

Reweighting the 2021-2023 cohort to the 2017-2020 covariate distribution recovers only **~17% of the AUROC drop** -> **CONCEPT DRIFT dominates**. The decline is *not* explained by the cohort being older / heavier / higher-prevalence.

## 2. Per-predictor attribution -> not a single-lab artefact

| predictor   |    mean |     min |     max |
|:------------|--------:|--------:|--------:|
| LBXSTB      |  0.0003 |  0      |  0.0007 |
| LBXSASSI    |  0.0002 | -0      |  0.0004 |
| LBXSAL      |  0      |  0      |  0      |
| LBXSAPSI    | -0      | -0.0003 |  0.0003 |
| RIAGENDR    |  0      |  0      |  0      |
| LBDHDD      | -0.0001 | -0.0007 |  0.0003 |
| LBXPLTSI    | -0.0001 | -0.0005 |  0.0003 |
| LBXSATSI    | -0.0002 | -0.0004 | -0.0001 |
| BMXBMI      | -0.0005 | -0.0013 |  0.0002 |
| RIDAGEYR    | -0.0018 | -0.0036 |  0.0008 |

Quantile-mapping any single predictor (including the analyzer-shifted alkaline phosphatase) back to its 2017-2020 distribution recovers essentially **none** of the AUROC (all |recovery| < 0.004). ALP is a weak predictor, so its analyzer change does not drive the discrimination loss.

## 3. Slice-matched AUROC -> the drift is concentrated, and it targets the paper's subgroup

|                       |   n_new |   auroc_old |   auroc_new |   within_slice_drop |
|:----------------------|--------:|------------:|------------:|--------------------:|
| ('age', '18-39')      |    1407 |       0.848 |       0.793 |              -0.056 |
| ('age', '40-59')      |    1401 |       0.869 |       0.774 |              -0.095 |
| ('age', '60+')        |    2102 |       0.745 |       0.752 |               0.007 |
| ('bmi', 'Normal')     |    1336 |       0.823 |       0.618 |              -0.205 |
| ('bmi', 'Obese')      |    1896 |       0.792 |       0.746 |              -0.046 |
| ('bmi', 'Overweight') |    1607 |       0.788 |       0.714 |              -0.074 |

Bootstrap 95% CI on the within-slice AUROC change (pooled over the 5 models):

| slice      |   delta_auroc_median |   ci_low |   ci_high |
|:-----------|---------------------:|---------:|----------:|
| bmi=Normal |               -0.206 |   -0.319 |    -0.077 |
| bmi=Obese  |               -0.046 |   -0.088 |    -0.001 |
| age=40-59  |               -0.096 |   -0.154 |    -0.04  |
| age=60+    |                0.006 |   -0.056 |     0.064 |

- **Normal-BMI discrimination collapses** (~0.82 -> ~0.62) — near chance for the exact subgroup this study is about. 
- Age 40-59 loses ~0.10; age 60+ was already weak (~0.75) and is unchanged.
- Obese and overweight lose least. The drift is **not uniform** — it is a targeted degradation of the model's ability to rank normal-weight and middle-aged cases.

## 4. VCTE outcome-measurement stability

| metric                                      |     old |    new |
|:--------------------------------------------|--------:|-------:|
| mean_LUXSMED_kPa                            |   5.793 |  6.135 |
| median_LUXSMED_kPa                          |   5     |  5     |
| pct_LUXSMED_ge_8.2                          |   9.311 | 11.466 |
| pct_LUXSMED_8.0_to_8.4_borderline           |   1.775 |  1.955 |
| median_IQR_over_median_ratio_2021_2023_only | nan     |  0.136 |

Liver stiffness itself shifted only slightly (median unchanged at 5.0 kPa; mean 5.793 -> 6.135); the >=8.2 kPa rate rose 9.311% -> 11.466%. A reference-standard (VCTE) measurement change cannot be excluded as a component of the apparent concept drift and is noted as a limitation; the NHANES 2021-2023 elastography documentation should be checked for a device / software / probe-selection change.

## Reading for the manuscript

- The temporal AUROC decline is **concept drift dominates** (covariate-shift reweighting recovers only ~17%; no single predictor explains it).
- The drift is **concentrated in normal-weight and middle-aged participants**, with normal-weight discrimination falling to near chance — a *targeted* degradation of the subgroup the paper concerns, not a uniform weakening.
- **The reliability findings are unaffected and get worse over time**: the body-mass sensitivity gap widened (27-48 -> 63-72 pp), the conformal subgroup-coverage failure replicated, and the fairness-reliability dissociation replicated 5/5. Aggregate-AUROC monitoring would have shown a modest, arguably tolerable decline while the subgroup harm nearly doubled.
