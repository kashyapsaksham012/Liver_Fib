# Broad-Lab vs Fasting-Subset Candidate Cohort Comparison (Canonical)

**Generated:** 2026-08-18 13:27:27

- **Anchor** (non-missing LUXSMED): N=9700
- **COHORT_A_BROAD_LAB**: N=8880 (91.5% of anchor)
- **COHORT_A_PLUS_DEMO_BMI**: N=8805 (99.2% of Cohort A -- the 75-participant gap is entirely explained by missing BMI, see `results/tables/broad_cohort_discrepancy.csv`)
- **COHORT_FASTING_LABS_ONLY**: N=4376 (45.1% of anchor)
- **COHORT_B_FASTING_EXTENDED** (canonical 'Cohort B'): N=4336 (48.8% of Cohort A, 99.1% of COHORT_FASTING_LABS_ONLY -- the 40-participant gap to COHORT_FASTING_LABS_ONLY is entirely explained by missing >=1 broad lab, see `results/tables/fasting_cohort_discrepancy.csv`)

## Full comparison table

| cohort                                                                                                                       |    n |   pct_female |   pct_male |   median_age |   pct_adult_18plus |   median_bmi |   pct_Mexican_American |   pct_Other_Hispanic |   pct_Non-Hispanic_White |   pct_Non-Hispanic_Black |   pct_Non-Hispanic_Asian |   pct_Other_Race___Multi-Racial |   pct_LUAXSTAT_eq_1_quality_valid |   n_outcome_available_LUXSMED |
|:-----------------------------------------------------------------------------------------------------------------------------|-----:|-------------:|-----------:|-------------:|-------------------:|-------------:|-----------------------:|---------------------:|-------------------------:|-------------------------:|-------------------------:|--------------------------------:|----------------------------------:|------------------------------:|
| Anchor: COHORT_1_NONMISSING_LUX (non-missing LUXSMED)                                                                        | 9700 |        49.97 |      50.03 |           45 |              85.75 |         27.9 |                  12.52 |                10.15 |                    33.7  |                    26.34 |                    11.7  |                            5.59 |                             93.02 |                          9700 |
| COHORT_A_BROAD_LAB (LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD all non-missing; no BMI/demo requirement) | 8880 |        50.24 |      49.76 |           45 |              86.76 |         28   |                  12.96 |                10.35 |                    34.45 |                    25.01 |                    11.71 |                            5.52 |                             93.22 |                          8880 |
| COHORT_A_PLUS_DEMO_BMI (Cohort A + complete demographics + BMI)                                                              | 8805 |        50.31 |      49.69 |           45 |              86.76 |         28   |                  12.92 |                10.29 |                    34.51 |                    25.03 |                    11.75 |                            5.49 |                             93.3  |                          8805 |
| COHORT_FASTING_LABS_ONLY (LBXGLU, LBXTR only; broad labs NOT required)                                                       | 4376 |        50.32 |      49.68 |           46 |              87.8  |         27.9 |                  13.76 |                10.17 |                    33.27 |                    24.93 |                    12.13 |                            5.74 |                             94.9  |                          4376 |
| COHORT_B_FASTING_EXTENDED (Cohort A AND fasting labs) -- THE canonical 'Cohort B'                                            | 4336 |        50.44 |      49.56 |           46 |              87.8  |         27.9 |                  13.77 |                10.12 |                    33.35 |                    24.86 |                    12.13 |                            5.77 |                             94.86 |                          4336 |

## Reconciliation note (Issue 1 / Issue 2)

A prior draft of this pipeline reported 'the fasting cohort' as both 4,376 (COHORT_FASTING_LABS_ONLY) and 4,336 (COHORT_B_FASTING_EXTENDED) under one ambiguous label, and 'the combined broad cohort' as both 8,880 (COHORT_A_BROAD_LAB) and 8,805 (COHORT_A_PLUS_DEMO_BMI). Both pairs are legitimate, distinct, exactly-reproducible cohorts, not a data error -- they are now permanently and uniquely named in `src/_cohorts.py`, the single source every script in this pipeline imports from, with a programmatic assertion (`verify_cohort_relationships`) that halts the pipeline if the subset relationship between them is ever violated.

## Interpretation (descriptive only -- no cohort is selected here)

COHORT_B_FASTING_EXTENDED is materially smaller than COHORT_A_BROAD_LAB because glucose and triglycerides are restricted to the morning fasting subsample (NHANES requires an 8-24h fast, morning session only, for P_GLU/P_TRIGLY). **This report does not choose between Cohort A and Cohort B.** Which to use as the Phase 2 predictor set is a study-design decision, to be made on scientific grounds -- NOT by comparing which one yields better model performance.
