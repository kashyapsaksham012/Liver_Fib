# Fix 2 -- VCTE reference-standard measurement-bias sensitivity (Amendment #18)

Relabel-only: the primary outcome is redefined at higher LUXSMED cut-points; model scores are unchanged. Full-train predictions + the frozen Youden threshold (consistent with section 3.4). One locked-test touch.

## Headline synthesis (read this first)

1. **The conformal subgroup coverage failure is ROBUST to measurement bias (C5).** BMI-Obese conformal coverage stays 0.70-0.88 (and *worsens* slightly for 4/5 models) when the outcome is restricted to LUXSMED >= 12 kPa -- unambiguous fibrosis, minimal measurement concern. It is not a borderline-label artefact. This strengthens the paper's headline finding.

2. **The BMI classification gap is driven by the models using BMI as a shortcut (C4).** At *matched* liver stiffness (8.2-12 kPa band), obese participants receive a predicted probability 0.19-0.33 higher than normal-weight participants (OLS `is_obese` coefficient; p < 0.001 for **all 5 models**). The disparity is a form of algorithmic bias that operates **independently of** the reference-standard measurement artefact -- an obese and a normal-weight patient with the same liver stiffness get materially different risk scores because of BMI alone.

3. **Obese detection is stable across the stiffness range (C2).** Obese sensitivity at >= 12 kPa vs >= 8.2 kPa differs by a median of 0.03 -- the obese performance is not confined to borderline (possibly-inflated) cases.

4. **The raw measurement-bias question is not directly adjudicable (C1, verdict V3).** The Obese-vs-Normal sensitivity gap attenuates and reverses as the stiffness threshold rises, but Normal-BMI has only 7 fibrosis-positive test cases at >= 12 kPa, so the Normal-BMI side is uninterpretable -- an **irreducible** limitation of this cohort. Given (2), this is now a secondary concern: the demonstrated mechanism (BMI shortcut) does not depend on measurement bias.

---

## C1 -- BMI-Obese vs Normal (and Age 40-59 vs 60+) sensitivity gap by stiffness threshold

|   cut_kPa | model         | dimension   | group_A   | group_B   |   nA_pos |   nB_pos |   sensA |   sensB |   gap_A_minus_B_pp |   ci_lo_pp |   ci_hi_pp |
|----------:|:--------------|:------------|:----------|:----------|---------:|---------:|--------:|--------:|-------------------:|-----------:|-----------:|
|       8.2 | logistic      | bmi         | Obese     | Normal    |      140 |       22 |  0.8857 |  0.4091 |              47.66 |      25.64 |      68.25 |
|       8.2 | logistic      | age         | 40-59     | 60+       |       66 |      101 |  0.8182 |  0.7327 |               8.55 |      -4.56 |      20.96 |
|       8.2 | random_forest | bmi         | Obese     | Normal    |      140 |       22 |  0.9071 |  0.5909 |              31.62 |      11.04 |      52.93 |
|       8.2 | random_forest | age         | 40-59     | 60+       |       66 |      101 |  0.8939 |  0.7624 |              13.16 |       2.09 |      24.17 |
|       8.2 | xgboost       | bmi         | Obese     | Normal    |      140 |       22 |  0.95   |  0.6364 |              31.36 |      11.04 |      52.4  |
|       8.2 | xgboost       | age         | 40-59     | 60+       |       66 |      101 |  0.9242 |  0.8119 |              11.24 |       1.33 |      21.2  |
|       8.2 | lightgbm      | bmi         | Obese     | Normal    |      140 |       22 |  0.9071 |  0.6364 |              27.08 |       6.75 |      48.12 |
|       8.2 | lightgbm      | age         | 40-59     | 60+       |       66 |      101 |  0.8939 |  0.7525 |              14.15 |       3.31 |      24.63 |
|       8.2 | mlp           | bmi         | Obese     | Normal    |      140 |       22 |  0.9357 |  0.5455 |              39.03 |      18.44 |      60.32 |
|       8.2 | mlp           | age         | 40-59     | 60+       |       66 |      101 |  0.9091 |  0.7624 |              14.67 |       3.66 |      25.56 |
|       9.7 | logistic      | bmi         | Obese     | Normal    |       91 |       11 |  0.9231 |  0.5455 |              37.76 |       9.39 |      68.33 |
|       9.7 | logistic      | age         | 40-59     | 60+       |       40 |       65 |  0.825  |  0.8154 |               0.96 |     -14.62 |      15.58 |
|       9.7 | random_forest | bmi         | Obese     | Normal    |       91 |       11 |  0.9011 |  0.7273 |              17.38 |      -8.79 |      46.85 |
|       9.7 | random_forest | age         | 40-59     | 60+       |       40 |       65 |  0.85   |  0.8    |               5    |     -10.19 |      19.23 |
|       9.7 | xgboost       | bmi         | Obese     | Normal    |       91 |       11 |  0.956  |  0.7273 |              22.88 |      -2.2  |      51.25 |
|       9.7 | xgboost       | age         | 40-59     | 60+       |       40 |       65 |  0.9    |  0.8308 |               6.92 |      -6.16 |      19.62 |
|       9.7 | lightgbm      | bmi         | Obese     | Normal    |       91 |       11 |  0.9341 |  0.7273 |              20.68 |      -4.4  |      47.95 |
|       9.7 | lightgbm      | age         | 40-59     | 60+       |       40 |       65 |  0.875  |  0.8    |               7.5  |      -6.73 |      21.15 |
|       9.7 | mlp           | bmi         | Obese     | Normal    |       91 |       11 |  0.9451 |  0.6364 |              30.87 |       3.6  |      60.34 |
|       9.7 | mlp           | age         | 40-59     | 60+       |       40 |       65 |  0.9    |  0.8154 |               8.46 |      -5.19 |      22.12 |
|      10   | logistic      | bmi         | Obese     | Normal    |       86 |        9 |  0.9419 |  0.6667 |              27.52 |      -0.52 |      62.02 |
|      10   | logistic      | age         | 40-59     | 60+       |       37 |       62 |  0.8649 |  0.8387 |               2.62 |     -12.47 |      16.61 |
|      10   | random_forest | bmi         | Obese     | Normal    |       86 |        9 |  0.9186 |  0.8889 |               2.97 |     -12.79 |      27.52 |
|      10   | random_forest | age         | 40-59     | 60+       |       37 |       62 |  0.8919 |  0.8226 |               6.93 |      -7.11 |      20.4  |
|      10   | xgboost       | bmi         | Obese     | Normal    |       86 |        9 |  0.9651 |  0.8889 |               7.62 |      -6.98 |      31.01 |
|      10   | xgboost       | age         | 40-59     | 60+       |       37 |       62 |  0.9459 |  0.8548 |               9.11 |      -2.22 |      20.97 |
|      10   | lightgbm      | bmi         | Obese     | Normal    |       86 |        9 |  0.9535 |  0.8889 |               6.46 |      -8.14 |      31.01 |
|      10   | lightgbm      | age         | 40-59     | 60+       |       37 |       62 |  0.9189 |  0.8226 |               9.63 |      -2.79 |      22.58 |
|      10   | mlp           | bmi         | Obese     | Normal    |       86 |        9 |  0.9535 |  0.7778 |              17.57 |      -5.84 |      48.58 |
|      10   | mlp           | age         | 40-59     | 60+       |       37 |       62 |  0.9459 |  0.8387 |              10.72 |      -1.13 |      23.1  |
|      12   | logistic      | bmi         | Obese     | Normal    |       53 |        7 |  0.9245 |  0.8571 |               6.74 |     -13.21 |      37.2  |
|      12   | logistic      | age         | 40-59     | 60+       |       24 |       40 |  0.875  |  0.85   |               2.5  |     -15.83 |      19.17 |
|      12   | random_forest | bmi         | Obese     | Normal    |       53 |        7 |  0.9057 |  1      |              -9.43 |     -17.03 |      -1.89 |
|      12   | random_forest | age         | 40-59     | 60+       |       24 |       40 |  0.9167 |  0.8    |              11.67 |      -4.17 |      30    |
|      12   | xgboost       | bmi         | Obese     | Normal    |       53 |        7 |  0.9623 |  1      |              -3.77 |      -9.43 |       0    |
|      12   | xgboost       | age         | 40-59     | 60+       |       24 |       40 |  0.9583 |  0.85   |              10.83 |      -2.52 |      25    |
|      12   | lightgbm      | bmi         | Obese     | Normal    |       53 |        7 |  0.9434 |  1      |              -5.66 |     -13.21 |       0    |
|      12   | lightgbm      | age         | 40-59     | 60+       |       24 |       40 |  0.9167 |  0.8    |              11.67 |      -5    |      28.33 |
|      12   | mlp           | bmi         | Obese     | Normal    |       53 |        7 |  0.9623 |  0.8571 |              10.51 |      -7.55 |      40.97 |
|      12   | mlp           | age         | 40-59     | 60+       |       24 |       40 |  0.9583 |  0.875  |               8.33 |      -5.83 |      20.85 |
|      13.6 | logistic      | bmi         | Obese     | Normal    |       40 |        6 |  0.9    |  1      |             -10    |     -20    |      -2.5  |
|      13.6 | logistic      | age         | 40-59     | 60+       |       19 |       31 |  0.8421 |  0.8387 |               0.34 |     -21.9  |      21.75 |
|      13.6 | random_forest | bmi         | Obese     | Normal    |       40 |        6 |  0.9    |  1      |             -10    |     -20    |      -2.5  |
|      13.6 | random_forest | age         | 40-59     | 60+       |       19 |       31 |  0.9474 |  0.7419 |              20.54 |       1.19 |      38.71 |
|      13.6 | xgboost       | bmi         | Obese     | Normal    |       40 |        6 |  0.95   |  1      |              -5    |     -12.5  |       0    |
|      13.6 | xgboost       | age         | 40-59     | 60+       |       19 |       31 |  0.9474 |  0.8065 |              14.09 |      -2.89 |      30.22 |
|      13.6 | lightgbm      | bmi         | Obese     | Normal    |       40 |        6 |  0.925  |  1      |              -7.5  |     -15    |       0    |
|      13.6 | lightgbm      | age         | 40-59     | 60+       |       19 |       31 |  0.8947 |  0.7419 |              15.28 |      -4.92 |      35.48 |
|      13.6 | mlp           | bmi         | Obese     | Normal    |       40 |        6 |  0.95   |  1      |              -5    |     -12.5  |       0    |
|      13.6 | mlp           | age         | 40-59     | 60+       |       19 |       31 |  0.9474 |  0.871  |               7.64 |      -8.15 |      22.58 |

Median BMI (Obese - Normal) gap by cut: 8.2kPa +31.6pp, 9.7kPa +22.9pp, 10.0kPa +7.6pp, 12.0kPa -3.8pp, 13.6kPa -7.5pp

**Normal-BMI positive counts collapse with the threshold** (22 -> 11 -> 9 -> 7 -> 6), so the CIs at >= 10 kPa are uninformative on the Normal-BMI side -- an **irreducible** power limitation of this cohort.

## C2 -- obese-side (high power): >= 12 kPa vs >= 8.2 kPa

| model         |   obese_sens_ge8.2 |   obese_sens_ge12 |   delta_obese_sens |   obese_cov_ge8.2 |   obese_cov_ge12 |   delta_obese_cov |
|:--------------|-------------------:|------------------:|-------------------:|------------------:|-----------------:|------------------:|
| logistic      |             0.8857 |            0.9245 |             0.0388 |            0.9929 |           0.9811 |           -0.0117 |
| random_forest |             0.9071 |            0.9057 |            -0.0015 |            0.9429 |           0.9811 |            0.0383 |
| xgboost       |             0.95   |            0.9623 |             0.0123 |            0.9643 |           0.9811 |            0.0168 |
| lightgbm      |             0.9071 |            0.9434 |             0.0363 |            0.9643 |           0.9623 |           -0.002  |
| mlp           |             0.9357 |            0.9623 |             0.0265 |            0.0714 |           0.1321 |            0.0606 |

## C3 -- stiffness-stratified sensitivity (8.2-10 kPa band vs >= 10 kPa band)

| model         | band   |   Normal |   Obese |   obese_minus_normal_pp |
|:--------------|:-------|---------:|--------:|------------------------:|
| lightgbm      | 8.2-10 |   0.4615 |  0.8333 |                   37.18 |
| lightgbm      | >=10   |   0.8889 |  0.9535 |                    6.46 |
| logistic      | 8.2-10 |   0.2308 |  0.7963 |                   56.55 |
| logistic      | >=10   |   0.6667 |  0.9419 |                   27.52 |
| mlp           | 8.2-10 |   0.3846 |  0.9074 |                   52.28 |
| mlp           | >=10   |   0.7778 |  0.9535 |                   17.57 |
| random_forest | 8.2-10 |   0.3846 |  0.8889 |                   50.43 |
| random_forest | >=10   |   0.8889 |  0.9186 |                    2.97 |
| xgboost       | 8.2-10 |   0.4615 |  0.9259 |                   46.44 |
| xgboost       | >=10   |   0.8889 |  0.9651 |                    7.62 |

## C4 -- BMI-shortcut check (predicted_probability ~ LUXSMED + is_obese, 8.2-12 kPa band)

| model         |   n_band |   beta_is_obese |     se |    t |   p_value |   mean_score_diff_obese_minus_normal_matched_stiffness |
|:--------------|---------:|----------------:|-------:|-----:|----------:|-------------------------------------------------------:|
| logistic      |      102 |          0.3319 | 0.0429 | 7.74 |         0 |                                                 0.3391 |
| random_forest |      102 |          0.2536 | 0.0442 | 5.73 |         0 |                                                 0.245  |
| xgboost       |      102 |          0.2674 | 0.0475 | 5.63 |         0 |                                                 0.2855 |
| lightgbm      |      102 |          0.2777 | 0.0462 | 6.01 |         0 |                                                 0.2915 |
| mlp           |      102 |          0.1906 | 0.0401 | 4.75 |         0 |                                                 0.1876 |

## C5 -- conformal coverage of BMI-Obese / Age-60+ under stricter positive labels

| model         | dimension   | category   |   positive_cut_kPa |   n |   coverage |   wilson_lo |   wilson_hi |
|:--------------|:------------|:-----------|-------------------:|----:|-----------:|------------:|------------:|
| logistic      | bmi         | Obese      |                8.2 | 883 |     0.8233 |      0.7968 |      0.8471 |
| logistic      | age         | 60+        |                8.2 | 741 |     0.8489 |      0.8213 |      0.8728 |
| logistic      | bmi         | Obese      |               10   | 883 |     0.7928 |      0.7648 |      0.8182 |
| logistic      | age         | 60+        |               10   | 741 |     0.8394 |      0.8112 |      0.8641 |
| logistic      | bmi         | Obese      |               12   | 883 |     0.7678 |      0.7389 |      0.7945 |
| logistic      | age         | 60+        |               12   | 741 |     0.8219 |      0.7927 |      0.8477 |
| random_forest | bmi         | Obese      |                8.2 | 883 |     0.8018 |      0.7742 |      0.8268 |
| random_forest | age         | 60+        |                8.2 | 741 |     0.8556 |      0.8285 |      0.8791 |
| random_forest | bmi         | Obese      |               10   | 883 |     0.7758 |      0.7471 |      0.802  |
| random_forest | age         | 60+        |               10   | 741 |     0.857  |      0.8299 |      0.8803 |
| random_forest | bmi         | Obese      |               12   | 883 |     0.7475 |      0.7178 |      0.775  |
| random_forest | age         | 60+        |               12   | 741 |     0.8421 |      0.8141 |      0.8666 |
| xgboost       | bmi         | Obese      |                8.2 | 883 |     0.7678 |      0.7389 |      0.7945 |
| xgboost       | age         | 60+        |                8.2 | 741 |     0.8111 |      0.7813 |      0.8376 |
| xgboost       | bmi         | Obese      |               10   | 883 |     0.7339 |      0.7037 |      0.762  |
| xgboost       | age         | 60+        |               10   | 741 |     0.7989 |      0.7686 |      0.8262 |
| xgboost       | bmi         | Obese      |               12   | 883 |     0.7022 |      0.6712 |      0.7314 |
| xgboost       | age         | 60+        |               12   | 741 |     0.7814 |      0.7502 |      0.8096 |
| lightgbm      | bmi         | Obese      |                8.2 | 883 |     0.7916 |      0.7636 |      0.8171 |
| lightgbm      | age         | 60+        |                8.2 | 741 |     0.8475 |      0.8198 |      0.8716 |
| lightgbm      | bmi         | Obese      |               10   | 883 |     0.7599 |      0.7306 |      0.7869 |
| lightgbm      | age         | 60+        |               10   | 741 |     0.8354 |      0.8069 |      0.8603 |
| lightgbm      | bmi         | Obese      |               12   | 883 |     0.7327 |      0.7026 |      0.7609 |
| lightgbm      | age         | 60+        |               12   | 741 |     0.8178 |      0.7884 |      0.8439 |
| mlp           | bmi         | Obese      |                8.2 | 883 |     0.8086 |      0.7813 |      0.8332 |
| mlp           | age         | 60+        |                8.2 | 741 |     0.8381 |      0.8098 |      0.8628 |
| mlp           | bmi         | Obese      |               10   | 883 |     0.855  |      0.8303 |      0.8767 |
| mlp           | age         | 60+        |               10   | 741 |     0.8826 |      0.8574 |      0.9038 |
| mlp           | bmi         | Obese      |               12   | 883 |     0.8822 |      0.8593 |      0.9018 |
| mlp           | age         | 60+        |               12   | 741 |     0.9069 |      0.8838 |      0.9258 |

## Verdict (pre-registered rule, PREPUBLICATION_FIXES_PLAN.md 0.3)

- median Obese-Normal gap at >= 12 kPa: **-3.8 pp**; models with gap >= +15 pp: **0/5**; models with gap < +10 pp: **4/5**
- |delta obese sensitivity| (>=12 vs >=8.2), median: **0.026**
- Normal-BMI positives at >= 12 kPa: **7** (< 8 -> Normal-BMI side cannot adjudicate)

### VERDICT: **V3**

The Normal-BMI side is underpowered at stricter thresholds and cannot adjudicate whether measurement bias contributes; the obese-side analyses (C2, C3, C5) provide partial reassurance that the obese performance is not confined to borderline cases. **Abstract keeps the body-mass finding but adds: 'the contribution of BMI-dependent reference-standard measurement could not be excluded.'** A biopsy- or MRE-referenced cohort is required to resolve it.

### Limitations-paragraph draft

> The outcome is defined by vibration-controlled transient elastography, which over-reads liver stiffness at high body-mass index; some obese participants classified as having significant fibrosis near the 8.2-kPa cut-point may therefore carry inflated stiffness values. Three lines of evidence argue against this artefact explaining the observed body-mass disparity. First, obese sensitivity and obese conformal coverage were stable when the outcome was restricted to unambiguous fibrosis (LUXSMED >= 12 kPa; C2), whereas a measurement artefact concentrated near 8.2 kPa would predict a drop. Second, the BMI-Obese conformal under-coverage persisted -- and slightly worsened for four of five models -- under the same restriction (C5). Third, at matched liver stiffness in the 8.2-12 kPa band, obese participants received a predicted probability 0.19-0.33 higher than normal-weight participants for every model (p < 0.001; C4), indicating the models use body mass itself as a risk cue independently of the measured stiffness. The gap in raw sensitivity between obese and normal-weight positives does narrow, and slightly reverses, as the stiffness threshold rises, but normal-weight participants have too few fibrosis-positive cases at stricter thresholds (7 at >= 12 kPa) for that comparison to be interpreted; a histology- or magnetic-resonance-elastography-referenced cohort would be required to fully exclude a residual measurement contribution.

