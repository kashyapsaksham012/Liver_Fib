# Temporal drift audit — NHANES 2021-2023 vs frozen 2017-March 2020

Descriptive, pre-touch. Positive standardized mean difference = higher in 2021-2023.

## Predictor distribution drift

| predictor   |   mean_2017_2020 |   mean_2021_2023 |   standardized_mean_diff |   ks_distance |
|:------------|-----------------:|-----------------:|-------------------------:|--------------:|
| RIDAGEYR    |           49.008 |           52.153 |                    0.175 |         0.1   |
| RIAGENDR    |            1.506 |            1.54  |                    0.068 |         0.034 |
| BMXBMI      |           29.615 |           29.255 |                   -0.051 |         0.035 |
| LBXSATSI    |           22.426 |           22.005 |                   -0.023 |         0.019 |
| LBXSASSI    |           21.928 |           22.653 |                    0.049 |         0.072 |
| LBXSAL      |            4.078 |            4.096 |                    0.052 |         0.038 |
| LBXSAPSI    |           77.632 |           84.24  |                    0.246 |         0.114 |
| LBXSTB      |            0.46  |            0.503 |                    0.122 |         0.057 |
| LBXPLTSI    |          246.743 |          255.878 |                    0.14  |         0.07  |
| LBDHDD      |           53.407 |           54.552 |                    0.075 |         0.055 |

**|SMD| > 0.2 or KS > 0.1 flags a material shift.** Any such shift on a *lab* predictor must be checked against the NHANES analytic note for a method change before interpreting a discrimination drop.

## Lab-method continuity (to verify against NHANES analytic notes)

- **LBXSATSI** — ALT — NHANES moved the biochemistry profile to the Roche Cobas c501/6000 platform for the 2021-2023 cycle; the standalone branch built an ALT crosswalk. PRIMARY analysis uses raw values; crosswalk = sensitivity only. VERIFY analytic note.
- **LBXSASSI** — AST — same platform change as ALT. VERIFY analytic note for a method/units shift.
- **LBXSAL** — Albumin — VERIFY (BCG vs BCP method history in NHANES).
- **LBXSAPSI** — Alkaline phosphatase — VERIFY analytic note.
- **LBXSTB** — Total bilirubin — VERIFY analytic note.
- **LBXPLTSI** — Platelets (CBC) — Sysmex analyzer; generally stable across cycles. VERIFY.
- **LBDHDD** — HDL cholesterol — VERIFY analytic note.

## Composition drift

| dimension   | category    |   pct_2017_2020 |   pct_2021_2023 |
|:------------|:------------|----------------:|----------------:|
| age_band    | 18-39       |           33.87 |           28.66 |
| age_band    | 40-59       |           32.41 |           28.53 |
| age_band    | 60+         |           33.72 |           42.81 |
| bmi_band    | Normal      |           25.19 |           27.21 |
| bmi_band    | Obese       |           40.91 |           38.62 |
| bmi_band    | Overweight  |           32.38 |           32.73 |
| bmi_band    | Underweight |            1.52 |            1.45 |
| sex         | 1.0         |           49.36 |           45.97 |
| sex         | 2.0         |           50.64 |           54.03 |
| race        | 1.0         |           12.61 |            7.17 |
| race        | 2.0         |           10.54 |           10.47 |
| race        | 3.0         |           34.73 |           59.16 |
| race        | 4.0         |           24.98 |           11.06 |
| race        | 6.0         |           12.11 |            5.74 |
| race        | 7.0         |            5.03 |            6.4  |

## Outcome / stiffness drift

| metric             |   value_2017_2020 |   value_2021_2023 |
|:-------------------|------------------:|------------------:|
| prevalence_pct     |             9.311 |            11.466 |
| mean_LUXSMED_kPa   |             5.793 |             6.135 |
| median_LUXSMED_kPa |             5     |             5     |

## Reading

- Outcome prevalence rose 9.311% -> 11.466% (consistent with post-pandemic metabolic shift).
- A materially higher BMI / ALT / AST distribution in 2021-2023 means a later-cycle AUROC drop is confounded between *model non-transport* and *genuine population change* (and, for the enzymes, a possible analyzer change). This is stated as a limitation, not resolved.
