# Phase 1 Data Assembly Report — CLOSURE

**Generated:** 2026-08-18 13:27:50  
**Operating Environment:** python 3.14.3 (macOS-26.5.2-arm64-arm-64bit-Mach-O)  
**Data Directory:** `data/raw/NHANES_2017_2020/`  

This report supersedes all prior Phase 1 reports (archived under `documentation/audit_reports/archive/`). This closure pass traced and resolved two reporting-clarity discrepancies flagged for reconciliation (fasting-cohort count 4,376 vs 4,336; broad-cohort count 8,880 vs 8,805) -- both confirmed to be legitimate, exactly-reproducible, distinct cohort definitions, not data errors -- and introduced a single canonical cohort-definition module (`src/_cohorts.py`) so every script in this pipeline now computes each named cohort identically. See Section E and Section V.

---

## A. Execution Status

**PHASE 1 — COMPLETE AND FROZEN**

All pipeline steps executed without error, all required deliverables were produced, both closure-phase discrepancies were traced to exact participant-level evidence and reconciled, and all internal validation tests passed.

## B. Raw Files

| filename     | size_human   |   rows |   columns | has_seqn   | looks_like_valid_xpt   | md5_checksum                     |
|:-------------|:-------------|-------:|----------:|:-----------|:-----------------------|:---------------------------------|
| P_LUX.xpt    | 1.11 MB      |  10409 |        13 | True       | True                   | f13a60ec6b7dfb74ac70437f567ab9a0 |
| P_DEMO.xpt   | 3.61 MB      |  15560 |        29 | True       | True                   | 850382076eca1bef83b681d721c8362d |
| P_BMX.xpt    | 2.52 MB      |  14300 |        22 | True       | True                   | 62ff0ed76b35124059ddf97af4510310 |
| P_BIOPRO.xpt | 3.42 MB      |  10409 |        41 | True       | True                   | c8751a52982cafc58235438866d3dff6 |
| P_CBC.xpt    | 2.43 MB      |  13772 |        22 | True       | True                   | 498bb01dcc4f8ed6f66260aa85e97657 |
| P_GLU.xpt    | 0.16 MB      |   5090 |         4 | True       | True                   | b18d588f479a5d07053d480cb26a76a2 |
| P_TRIGLY.xpt | 0.41 MB      |   5090 |        10 | True       | True                   | e870c5f806d9bef8f8f7511ce2bde5c3 |
| P_HDL.xpt    | 0.29 MB      |  12198 |         3 | True       | True                   | 2ff256d85224ee3de8a87c4fb26aa8de |

## C. Dataset Shapes

| File / Component | Rows | Columns |
|---|---|---|
| `P_LUX.xpt` | 10409 | 13 |
| `P_DEMO.xpt` | 15560 | 29 |
| `P_BMX.xpt` | 14300 | 22 |
| `P_BIOPRO.xpt` | 10409 | 41 |
| `P_CBC.xpt` | 13772 | 22 |
| `P_GLU.xpt` | 5090 | 4 |
| `P_TRIGLY.xpt` | 5090 | 10 |
| `P_HDL.xpt` | 12198 | 3 |
| **MASTER DATASET** | **10409** | **137** |

## D. Linkage

| dataset      |   n_rows |   n_unique_seqn |   n_missing_seqn |   n_duplicate_seqn |   matched_to_lux_cohort |   lux_participants_missing_from_this_file |   rows_in_this_file_outside_lux_cohort |   pct_of_lux_cohort_matched |
|:-------------|---------:|----------------:|-----------------:|-------------------:|------------------------:|------------------------------------------:|---------------------------------------:|----------------------------:|
| P_LUX.xpt    |    10409 |           10409 |                0 |                  0 |                   10409 |                                         0 |                                      0 |                       100   |
| P_DEMO.xpt   |    15560 |           15560 |                0 |                  0 |                   10409 |                                         0 |                                   5151 |                       100   |
| P_BMX.xpt    |    14300 |           14300 |                0 |                  0 |                   10409 |                                         0 |                                   3891 |                       100   |
| P_BIOPRO.xpt |    10409 |           10409 |                0 |                  0 |                   10409 |                                         0 |                                      0 |                       100   |
| P_CBC.xpt    |    13772 |           13772 |                0 |                  0 |                   10409 |                                         0 |                                   3363 |                       100   |
| P_GLU.xpt    |     5090 |            5090 |                0 |                  0 |                    5090 |                                      5319 |                                      0 |                        48.9 |
| P_TRIGLY.xpt |     5090 |            5090 |                0 |                  0 |                    5090 |                                      5319 |                                      0 |                        48.9 |
| P_HDL.xpt    |    12198 |           12198 |                0 |                  0 |                   10409 |                                         0 |                                   1789 |                       100   |

### Merge Audit

| dataset      |   rows_before |   rows_after |   matched_seqn |   unmatched_seqn | row_multiplication   | description                                                          |
|:-------------|--------------:|-------------:|---------------:|-----------------:|:---------------------|:---------------------------------------------------------------------|
| P_LUX.xpt    |         10409 |        10409 |          10409 |                0 | nan                  | Baseline transient elastography population (root cohort denominator) |
| P_DEMO.xpt   |         10409 |        10409 |          10409 |                0 | No                   | Left merge on SEQN                                                   |
| P_BMX.xpt    |         10409 |        10409 |          10409 |                0 | No                   | Left merge on SEQN                                                   |
| P_BIOPRO.xpt |         10409 |        10409 |          10409 |                0 | No                   | Left merge on SEQN                                                   |
| P_CBC.xpt    |         10409 |        10409 |          10409 |                0 | No                   | Left merge on SEQN                                                   |
| P_GLU.xpt    |         10409 |        10409 |           5090 |             5319 | No                   | Left merge on SEQN [FASTING SUBSAMPLE FILE]                          |
| P_TRIGLY.xpt |         10409 |        10409 |           5090 |             5319 | No                   | Left merge on SEQN [FASTING SUBSAMPLE FILE]                          |
| P_HDL.xpt    |         10409 |        10409 |          10409 |                0 | No                   | Left merge on SEQN                                                   |

**Row Preservation:** invariant at 10409 across all merge steps (TEST5/TEST6).

## E. Cohort Definitions

Every named data-feasibility cohort used anywhere in this project is defined EXACTLY ONCE, in `src/_cohorts.py`, and every script that needs one imports it from there -- no script recomputes a cohort mask independently. This is what prevents the discrepancy class traced in Section F/N below from recurring (enforced by `_cohorts.verify_cohort_relationships()`, which halts the pipeline if any subset relationship is ever violated -- TEST17).

| cohort_id                        | purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                       | source_population       |     n | requires_quality_valid_luaxstat1   | requires_adult_18plus   | requires_broad_labs   | requires_fasting_labs   |
|:---------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|------:|:-----------------------------------|:------------------------|:----------------------|:------------------------|
| COHORT_0_SOURCE                  | Root cohort denominator: every P_LUX-examined participant                                                                                                                                                                                                                                                                                                                                                                                                     | P_LUX (all rows)        | 10409 | False                              | False                   | False                 | False                   |
| COHORT_1_NONMISSING_LUX          | Participants with a non-missing liver stiffness value, ANY exam completeness (NOT the NHANES quality-valid definition -- see COHORT_2)                                                                                                                                                                                                                                                                                                                        | COHORT_0_SOURCE         |  9700 | False                              | False                   | False                 | False                   |
| COHORT_2_QUALITY_VALID           | OFFICIAL NHANES quality-valid elastography exam ('Complete')                                                                                                                                                                                                                                                                                                                                                                                                  | COHORT_0_SOURCE         |  9023 | True                               | False                   | False                 | False                   |
| COHORT_3A_ADULT_OF_NONMISSING    | Adults (>=18y) among the non-missing-LUXSMED population                                                                                                                                                                                                                                                                                                                                                                                                       | COHORT_1_NONMISSING_LUX |  8318 | False                              | True                    | False                 | False                   |
| COHORT_3B_ADULT_OF_QUALITY_VALID | Adults (>=18y) among the NHANES quality-valid (LUAXSTAT==1) population -- distinct from COHORT_3A because quality-valid (N=9,023) is not the same population as non-missing LUXSMED (N=9,700) (Issue 6)                                                                                                                                                                                                                                                       | COHORT_2_QUALITY_VALID  |  7768 | True                               | True                    | False                 | False                   |
| COHORT_A_BROAD_LAB               | Candidate broad routine-laboratory predictor cohort. Does NOT require BMI or demographic completeness (see COHORT_A_PLUS_DEMO_BMI for that stricter nesting).                                                                                                                                                                                                                                                                                                 | COHORT_1_NONMISSING_LUX |  8880 | False                              | False                   | True                  | False                   |
| COHORT_A_PLUS_DEMO_BMI           | Cohort A (broad labs) FURTHER RESTRICTED to complete demographics AND BMI. Strictly nested inside Cohort A. In this dataset the entire A-vs-this gap (75 participants, verified) is driven by missing BMI; demographics are essentially complete within Cohort A. NOT a separate lab-availability concept -- a stricter predictor-completeness nesting of Cohort A. Renamed from the ambiguous prior label 'combined broad cohort' (Issue 2/Closure Phase D). | COHORT_A_BROAD_LAB      |  8805 | False                              | False                   | True                  | False                   |
| COHORT_FASTING_LABS_ONLY         | Participants with the fasting-subsample labs (glucose, triglycerides) present, REGARDLESS of broad-lab completeness. This is NOT the same population as COHORT_B_FASTING_EXTENDED (which additionally requires the broad labs) -- the two were previously conflated under one ambiguous 'fasting cohort' label (Issue 1). Renamed from the prior 'fasting labs available (branch)' cohort_flow step.                                                          | COHORT_1_NONMISSING_LUX |  4376 | False                              | False                   | False                 | True                    |
| COHORT_B_FASTING_EXTENDED        | THE canonical 'Cohort B': the full fasting-extended candidate predictor cohort -- requires BOTH the broad labs (Cohort A) AND the fasting-subsample labs (glucose, triglycerides). This is the population usable if the eventual Phase 2 predictor set includes fasting glucose/triglycerides. Strict subset of both COHORT_A_BROAD_LAB and COHORT_FASTING_LABS_ONLY (asserted in verify_cohort_relationships()).                                             | COHORT_A_BROAD_LAB      |  4336 | False                              | False                   | True                  | True                    |

Full inclusion/exclusion criteria and required variables for each cohort: `results/tables/phase1_cohort_definition_table.csv` / `.md`.

## F. Corrected Cohort Flow

> Every transition below is programmatically verified: `n_before - n_excluded == n_after` (TEST7), computed from the canonical cohorts in Section E.

| step                                                                                            | cohort_id                        |   n_before |   n_excluded |   n_after |   pct_LUAXSTAT_eq_1 | reason                                                                                                                                                                                                                                                                                 |
|:------------------------------------------------------------------------------------------------|:---------------------------------|-----------:|-------------:|----------:|--------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0. P_LUX Total Participants (source cohort denominator)                                         | COHORT_0_SOURCE                  |      10409 |            0 |     10409 |               86.68 | Root cohort; every subsequent row is a subset of this population                                                                                                                                                                                                                       |
| 1. Non-missing LUXSMED (NOTE: non-missingness, NOT the NHANES quality-valid flag)               | COHORT_1_NONMISSING_LUX          |      10409 |          709 |      9700 |               93.02 | Missing/invalid FibroScan attempt (LUAXSTAT in {3,4}, or {2} with no numeric result)                                                                                                                                                                                                   |
| 1b. NHANES Quality-Valid Elastography (LUAXSTAT==1), among Step 1 (Issue 3)                     | COHORT_2_QUALITY_VALID           |       9700 |          677 |      9023 |              100    | Official NHANES 'Complete' definition (fasting>=3h, >=10 complete measures, IQRe/Med<30%) -- see documentation/source_metadata/lux_quality_rule_source.md. These 677 participants have a non-missing LUXSMED from a Partial (LUAXSTAT=2) exam that does not meet the full quality bar. |
| 2a. Adult Participants (Age>=18), among Step 1 (non-missing LUXSMED)                            | COHORT_3A_ADULT_OF_NONMISSING    |       9700 |         1382 |      8318 |               93.39 | CANDIDATE Phase 2 restriction, reported for descriptive flow accounting only                                                                                                                                                                                                           |
| 2b. Adult Participants (Age>=18), among Step 1b (quality-valid) (Issue 6)                       | COHORT_3B_ADULT_OF_QUALITY_VALID |       9023 |         1255 |      7768 |              100    | Reported separately because the quality-valid population (9,023) is NOT the same as the non-missing population (9,700) -- the two adult counts are not assumed identical                                                                                                               |
| 3. Demographics Available (RIAGENDR non-missing), among Step 1                                  | COHORT_1_NONMISSING_LUX          |       9700 |            0 |      9700 |               93.02 | Fairness analysis requirement                                                                                                                                                                                                                                                          |
| 4a. Broad Routine-Lab Predictors Available (Cohort A), among Step 1                             | COHORT_A_BROAD_LAB               |       9700 |          820 |      8880 |               93.22 | Candidate broad-lab predictor cohort (LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD all non-missing); does NOT require BMI/demographics (Issue 9: renamed for clarity, was 'Step 5')                                                                                  |
| 4b. Cohort A FURTHER restricted to complete demographics + BMI (Issue 2/9)                      | COHORT_A_PLUS_DEMO_BMI           |       8880 |           75 |      8805 |               93.3  | Strict nesting inside Cohort A. NOT a separate lab-availability concept, and NOT the same population as Cohort A (75-participant gap, entirely explained by missing BMI -- see results/tables/broad_cohort_discrepancy.csv). Renamed from ambiguous 'combined broad cohort'.           |
| 5a. Fasting-Subsample Labs Available ONLY (glucose+triglycerides, broad NOT required)           | COHORT_FASTING_LABS_ONLY         |       9700 |         5324 |      4376 |               94.9  | [BRANCH, not chained into the main flow] Renamed from ambiguous 'fasting labs available' -- see results/tables/fasting_cohort_discrepancy.csv for why this differs from Cohort B below                                                                                                 |
| 5b. Cohort B = Fasting-Extended (Cohort A AND fasting labs) (Issue 1, THE canonical 'Cohort B') | COHORT_B_FASTING_EXTENDED        |       8880 |         4544 |      4336 |               94.86 | Requires BOTH broad labs (Cohort A) AND fasting labs. Exactly the intersection of Step 4a and Step 5a (asserted programmatically in _cohorts.verify_cohort_relationships) -- this IS the authoritative Cohort B number used everywhere else in this pipeline (4,336, not 4,376).       |

### Discrepancy Reconciliation (Issues 1 & 2 — CLOSED)

- **Fasting cohort:** COHORT_FASTING_LABS_ONLY (N=4376, glucose+triglycerides only) vs. COHORT_B_FASTING_EXTENDED (N=4336, THE canonical 'Cohort B' -- also requires the broad labs). Difference = 40 participants, traced exactly to individuals missing >=1 broad lab (100% of the gap; full participant-level evidence in `results/tables/fasting_cohort_discrepancy.csv`, 40 rows). **Not a bug — two legitimately different, now uniquely-named cohorts.**
- **Broad cohort:** COHORT_A_BROAD_LAB (N=8880) vs. COHORT_A_PLUS_DEMO_BMI (N=8805, Cohort A further restricted to complete demographics+BMI). Difference = 75 participants, traced exactly to missing BMI (0 missing demographics; full evidence in `results/tables/broad_cohort_discrepancy.csv`, 75 rows). **Not a bug — a strict nesting of Cohort A, now uniquely named.**

## G. P_LUX Findings

- **Non-missing LUXSMED (COHORT_1):** 9700 of 10409
- **Quality-valid, LUAXSTAT==1 (COHORT_2):** 9023 of 10409 (official NHANES 'Complete' definition, verified source in `documentation/source_metadata/lux_quality_rule_source.md` -- Issue 3/4, code and documentation confirmed to agree exactly, no conflict found)
- **Observed Range:** 1.60 - 75.00 kPa | Median: 5.00 kPa

### Candidate Cutpoint Counts, BOTH denominators (Issue 10 — denominator reconciled)

| Cutpoint (kPa) | N in COHORT_1 (non-missing) | N in COHORT_2 (quality-valid) | Label |
|---|---|---|---|
| 7.0 | 1506 | 1295 | General cutoff (literature range, low end) |
| 7.5 | 1223 | 1033 | General cutoff (literature range) |
| 8.0 | 1000 | 828 | Candidate: significant fibrosis (>=F2), lower literature estimate |
| 8.2 | 939 | 772 | Candidate: significant fibrosis (>=F2), meta-analytic Youden-optimal cutoff |
| 9.0 | 712 | 576 | General cutoff (literature range) |
| 9.7 | 604 | 474 | Candidate: advanced fibrosis (>=F3), meta-analytic Youden-optimal cutoff |
| 10.0 | 568 | 443 | Candidate: advanced fibrosis (>=F3) / cACLD rule-of-thumb, commonly-cited round number |
| 12.0 | 367 | 271 | Candidate: cirrhosis (F4), commonly-cited round number |
| 13.6 | 278 | 196 | Candidate: cirrhosis (F4), meta-analytic Youden-optimal cutoff |

> All counts include participants under 18 (P_LUX's own target population is ages 12-150); these are raw cutpoint counts against non-missing LUXSMED, NOT post-quality-filtered unless using the COHORT_2 column. All values remain provisional/candidate, not a final threshold.

## H. Demographics (Stage A: total N; see Section O for outcome-positive counts)

| category                | group_label               |   sample_size |   percentage | total_n_ge_100   |
|:------------------------|:--------------------------|--------------:|-------------:|:-----------------|
| Sex                     | Female                    |          5314 |        51.05 | Yes              |
| Sex                     | Male                      |          5095 |        48.95 | Yes              |
| Race_Ethnicity_RIDRETH1 | Non-Hispanic White        |          3519 |        33.81 | Yes              |
| Race_Ethnicity_RIDRETH1 | Non-Hispanic Black        |          2762 |        26.53 | Yes              |
| Race_Ethnicity_RIDRETH1 | Other Race / Multi-Racial |          1801 |        17.3  | Yes              |
| Race_Ethnicity_RIDRETH1 | Mexican American          |          1273 |        12.23 | Yes              |
| Race_Ethnicity_RIDRETH1 | Other Hispanic            |          1054 |        10.13 | Yes              |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic White        |          3519 |        33.81 | Yes              |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic Black        |          2762 |        26.53 | Yes              |
| Race_Ethnicity_RIDRETH3 | Mexican American          |          1273 |        12.23 | Yes              |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic Asian        |          1225 |        11.77 | Yes              |
| Race_Ethnicity_RIDRETH3 | Other Hispanic            |          1054 |        10.13 | Yes              |
| Race_Ethnicity_RIDRETH3 | Other Race / Multi-Racial |           576 |         5.53 | Yes              |
| Age_Group_Provisional   | 60+                       |          3141 |        30.18 | Yes              |
| Age_Group_Provisional   | 18-39                     |          3016 |        28.97 | Yes              |
| Age_Group_Provisional   | 40-59                     |          2808 |        26.98 | Yes              |
| Age_Group_Provisional   | Under 18                  |          1444 |        13.87 | Yes              |
| BMI_Group_Provisional   | Obese (>=30)              |          3928 |        37.74 | Yes              |
| BMI_Group_Provisional   | Overweight (25-29.9)      |          3034 |        29.15 | Yes              |
| BMI_Group_Provisional   | Normal (18.5-24.9)        |          2872 |        27.59 | Yes              |
| BMI_Group_Provisional   | Underweight (<18.5)       |           379 |         3.64 | Yes              |
| BMI_Group_Provisional   | Missing                   |           196 |         1.88 | Yes              |

## I. Laboratory Availability (relative to the master/LUX-anchored cohort, N=10409)

| Variable | Source File | Fasting Subsample? | N Observed | N Missing | Missing % |
|---|---|---|---|---|---|
| `LBXSATSI` | P_BIOPRO.xpt | False | 9473 | 936 | 8.99% |
| `LBXSASSI` | P_BIOPRO.xpt | False | 9435 | 974 | 9.36% |
| `LBXSAL` | P_BIOPRO.xpt | False | 9477 | 932 | 8.95% |
| `LBXSAPSI` | P_BIOPRO.xpt | False | 9474 | 935 | 8.98% |
| `LBXSTB` | P_BIOPRO.xpt | False | 9475 | 934 | 8.97% |
| `LBXPLTSI` | P_CBC.xpt | False | 9788 | 621 | 5.97% |
| `LBXGLU` | P_GLU.xpt | True | 4744 | 5665 | 54.42% |
| `LBXTR` | P_TRIGLY.xpt | True | 4650 | 5759 | 55.33% |
| `LBDHDD` | P_HDL.xpt | False | 9527 | 882 | 8.47% |

## J. Missingness

- Overall/by-group missingness characterized for all 137 merged variables.
- **Special missing-value code audit:** 18 (file, column) pairs carried an unconverted SAS special-missing sentinel, 43311 raw cells total; all recoded to NaN prior to any statistic in this pipeline.

## K. Quality

### Demographic/Anthropometric/LUX Plausibility Flags

| variable   | suspected_issue                                                         |   observation_count | proposed_action         | justification                                                                           |
|:-----------|:------------------------------------------------------------------------|--------------------:|:------------------------|:----------------------------------------------------------------------------------------|
| BMXBMI     | BMI > 80 (extreme outlier, near NHANES-documented observed max of 92.3) |                   5 | Review                  | Extreme biological value; verify height/weight jointly, not evidence of error by itself |
| RIDAGEYR   | Age < 18                                                                |                1444 | Not excluded in Phase 1 | Adult-only restriction is a Phase 2 protocol decision, not applied here                 |

### Laboratory Plausibility Audit (comprehensive, flag-only)

7 flags raised across 9 laboratory variables; nothing was deleted.

## L. Leakage

| Classification | N variables |
|---|---|
| likely_eligible | 77 |
| uncertain_phase2_decision | 42 |
| quality_only | 16 |
| outcome_only | 2 |

## M. Candidate Predictors

| Variable | Category | Description | Missing % |
|---|---|---|---|
| `RIDAGEYR` | demographic | Age at screening (years) | 0.0% |
| `RIAGENDR` | demographic | Gender | 0.0% |
| `RIDRETH1` | demographic | Race/Hispanic origin (5 categories) | 0.0% |
| `RIDRETH3` | demographic | Race/Hispanic origin (6 categories, incl. NH Asian) | 0.0% |
| `BMXBMI` | candidate_predictor | Body Mass Index | 1.88% |
| `BMXWT` | candidate_predictor | Weight | 1.66% |
| `BMXHT` | candidate_predictor | Standing height | 1.74% |
| `LBXSATSI` | candidate_predictor | Alanine Aminotransferase (ALT) | 8.99% |
| `LBXSASSI` | candidate_predictor | Aspartate Aminotransferase (AST) | 9.36% |
| `LBXSAL` | candidate_predictor | Albumin, refrigerated serum | 8.95% |
| `LBXSAPSI` | candidate_predictor | Alkaline Phosphatase (ALP) | 8.98% |
| `LBXSTB` | candidate_predictor | Total Bilirubin | 8.97% |
| `LBXSGL` | candidate_predictor_broad | Glucose, serum (non-fasting, full biochemistry sample) | 8.99% |
| `LBXPLTSI` | candidate_predictor | Platelet count | 5.97% |
| `LBXGLU` | candidate_predictor_fasting | Fasting Glucose | 54.42% |
| `LBXTR` | candidate_predictor_fasting | Triglycerides | 55.33% |
| `LBDHDD` | candidate_predictor | Direct HDL-Cholesterol | 8.47% |

**Protection rule (Issue 13):** UNVERIFIED AUXILIARY VARIABLES MUST NOT ENTER MODELING OR SCIENTIFIC DERIVED OUTCOMES WITHOUT SOURCE VERIFICATION. Enforced by TEST22/TEST23: the candidate-predictor pool above and every canonical cohort definition (Section E) are checked programmatically to contain zero variables flagged as unverified in `variable_source_verification.csv`.

## N. Broad vs Fasting Feasibility

| cohort                                                                                                                       |    n |   pct_female |   pct_male |   median_age |   pct_adult_18plus |   median_bmi |   pct_Mexican_American |   pct_Other_Hispanic |   pct_Non-Hispanic_White |   pct_Non-Hispanic_Black |   pct_Non-Hispanic_Asian |   pct_Other_Race___Multi-Racial |   pct_LUAXSTAT_eq_1_quality_valid |   n_outcome_available_LUXSMED |
|:-----------------------------------------------------------------------------------------------------------------------------|-----:|-------------:|-----------:|-------------:|-------------------:|-------------:|-----------------------:|---------------------:|-------------------------:|-------------------------:|-------------------------:|--------------------------------:|----------------------------------:|------------------------------:|
| Anchor: COHORT_1_NONMISSING_LUX (non-missing LUXSMED)                                                                        | 9700 |        49.97 |      50.03 |           45 |              85.75 |         27.9 |                  12.52 |                10.15 |                    33.7  |                    26.34 |                    11.7  |                            5.59 |                             93.02 |                          9700 |
| COHORT_A_BROAD_LAB (LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD all non-missing; no BMI/demo requirement) | 8880 |        50.24 |      49.76 |           45 |              86.76 |         28   |                  12.96 |                10.35 |                    34.45 |                    25.01 |                    11.71 |                            5.52 |                             93.22 |                          8880 |
| COHORT_A_PLUS_DEMO_BMI (Cohort A + complete demographics + BMI)                                                              | 8805 |        50.31 |      49.69 |           45 |              86.76 |         28   |                  12.92 |                10.29 |                    34.51 |                    25.03 |                    11.75 |                            5.49 |                             93.3  |                          8805 |
| COHORT_FASTING_LABS_ONLY (LBXGLU, LBXTR only; broad labs NOT required)                                                       | 4376 |        50.32 |      49.68 |           46 |              87.8  |         27.9 |                  13.76 |                10.17 |                    33.27 |                    24.93 |                    12.13 |                            5.74 |                             94.9  |                          4376 |
| COHORT_B_FASTING_EXTENDED (Cohort A AND fasting labs) -- THE canonical 'Cohort B'                                            | 4336 |        50.44 |      49.56 |           46 |              87.8  |         27.9 |                  13.77 |                10.12 |                    33.35 |                    24.86 |                    12.13 |                            5.77 |                             94.86 |                          4336 |

## O. Subgroup Feasibility

Primary denominator (`LUAXSTAT==1`, quality-valid), provisional outcome = LUXSMED >= 8.2 kPa. Feasibility classification is a project-defined heuristic based on outcome-positive/negative counts (see `12_subgroup_outcome_feasibility.py`) -- **no group is dropped or pooled**:

| category                | group_label               |   total_n |   provisional_outcome_positive_n |   provisional_outcome_negative_n | feasibility_classification    |
|:------------------------|:--------------------------|----------:|---------------------------------:|---------------------------------:|:------------------------------|
| Sex                     | Male                      |      4521 |                              466 |                             4055 | primary-feasibility candidate |
| Sex                     | Female                    |      4502 |                              306 |                             4196 | primary-feasibility candidate |
| Race_Ethnicity_RIDRETH1 | Mexican American          |      1131 |                              105 |                             1026 | primary-feasibility candidate |
| Race_Ethnicity_RIDRETH1 | Other Hispanic            |       918 |                               75 |                              843 | exploratory candidate         |
| Race_Ethnicity_RIDRETH1 | Non-Hispanic White        |      3042 |                              267 |                             2775 | primary-feasibility candidate |
| Race_Ethnicity_RIDRETH1 | Non-Hispanic Black        |      2364 |                              218 |                             2146 | primary-feasibility candidate |
| Race_Ethnicity_RIDRETH1 | Other Race / Multi-Racial |      1568 |                              107 |                             1461 | primary-feasibility candidate |
| Race_Ethnicity_RIDRETH3 | Mexican American          |      1131 |                              105 |                             1026 | primary-feasibility candidate |
| Race_Ethnicity_RIDRETH3 | Other Hispanic            |       918 |                               75 |                              843 | exploratory candidate         |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic White        |      3042 |                              267 |                             2775 | primary-feasibility candidate |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic Black        |      2364 |                              218 |                             2146 | primary-feasibility candidate |
| Race_Ethnicity_RIDRETH3 | Non-Hispanic Asian        |      1061 |                               62 |                              999 | exploratory candidate         |
| Race_Ethnicity_RIDRETH3 | Other Race / Multi-Racial |       507 |                               45 |                              462 | exploratory candidate         |
| Age_Group_Provisional   | Under 18                  |      1255 |                               44 |                             1211 | exploratory candidate         |
| Age_Group_Provisional   | 18-39                     |      2633 |                              132 |                             2501 | primary-feasibility candidate |
| Age_Group_Provisional   | 40-59                     |      2482 |                              243 |                             2239 | primary-feasibility candidate |
| Age_Group_Provisional   | 60+                       |      2653 |                              353 |                             2300 | primary-feasibility candidate |
| BMI_Group_Provisional   | Underweight (<18.5)       |       324 |                               13 |                              311 | limited precision             |
| BMI_Group_Provisional   | Normal (18.5-24.9)        |      2578 |                               99 |                             2479 | exploratory candidate         |
| BMI_Group_Provisional   | Overweight (25-29.9)      |      2709 |                              133 |                             2576 | primary-feasibility candidate |
| BMI_Group_Provisional   | Obese (>=30)              |      3330 |                              517 |                             2813 | primary-feasibility candidate |
| BMI_Group_Provisional   | Missing                   |        82 |                               10 |                               72 | limited precision             |

Classification summary: primary-feasibility candidate=14, exploratory candidate=6, limited precision=2

## P. Survey Metadata

`WTMECPRP`, `WTINTPRP`, `WTSAFPRP`, `SDMVPSU`, `SDMVSTRA` preserved, unmodified, NOT applied to any analysis in Phase 1. Official rule (verified quote): *"you must use the weight of the smallest subpopulation that includes all the variables you want to include in your analysis"* — see `survey_design_notes.md`.

## Q. Master Dataset

- Parquet: `data/interim/nhanes_master_phase1.parquet` | CSV: `data/interim/nhanes_master_phase1.csv`
- Dimensions: 10409 rows x 137 columns | One row per participant: verified (TEST6)

## R. Table 1

| variable                            | type        |     n |   missing_n |   missing_pct |   mean_or_pct |     sd |   median |   iqr |   min |    max |
|:------------------------------------|:------------|------:|------------:|--------------:|--------------:|-------:|---------:|------:|------:|-------:|
| N (full P_LUX-anchored cohort)      | N           | 10409 |           0 |          0    |        nan    | nan    |    nan   | nan   | nan   |  nan   |
| Age (years)                         | continuous  | 10409 |           0 |          0    |         44.61 |  20.98 |     45   |  37   |  12   |   80   |
| Body Mass Index (kg/m^2)            | continuous  | 10213 |         196 |          1.88 |         29.12 |   7.71 |     27.9 |   9.3 |  13.2 |   92.3 |
| Weight (kg)                         | continuous  | 10236 |         173 |          1.66 |         80.95 |  23.63 |     77.5 |  29.2 |  27.6 |  254.3 |
| Height (cm)                         | continuous  | 10228 |         181 |          1.74 |        166.38 |  10.09 |    165.9 |  14.6 | 131.1 |  199.6 |
| Liver stiffness, median (kPa)       | continuous  |  9700 |         709 |          6.81 |          5.89 |   4.87 |      5   |   2   |   1.6 |   75   |
| CAP, median (dB/m)                  | continuous  |  9698 |         711 |          6.83 |        257.59 |  63.55 |    253   |  91   | 100   |  400   |
| Stiffness IQR/median ratio (%)      | continuous  |  9679 |         730 |          7.01 |         15.11 |  18.56 |     13.2 |   9.3 |   0.8 | 1338   |
| ALT (U/L)                           | continuous  |  9473 |         936 |          8.99 |         21.27 |  18.26 |     17   |  12   |   2   |  682   |
| AST (U/L)                           | continuous  |  9435 |         974 |          9.36 |         21.58 |  13.97 |     19   |   7   |   6   |  489   |
| Albumin (g/dL)                      | continuous  |  9477 |         932 |          8.95 |          4.08 |   0.35 |      4.1 |   0.4 |   2.1 |    5.4 |
| ALP (IU/L)                          | continuous  |  9474 |         935 |          8.98 |         89.26 |  51.38 |     77   |  33   |  16   |  638   |
| Total Bilirubin (mg/dL)             | continuous  |  9475 |         934 |          8.97 |          0.46 |   0.28 |      0.4 |   0.3 |   0.1 |    3.8 |
| Platelets (10^9/L)                  | continuous  |  9788 |         621 |          5.97 |        249.62 |  65.24 |    243   |  81   |   8   |  818   |
| Fasting Glucose (mg/dL)             | continuous  |  4744 |        5665 |         54.42 |        111.18 |  36.31 |    102   |  17   |  47   |  524   |
| Triglycerides (mg/dL)               | continuous  |  4650 |        5759 |         55.33 |        103.72 |  89.82 |     84   |  70   |  10   | 2684   |
| HDL (mg/dL)                         | continuous  |  9527 |         882 |          8.47 |         53.24 |  15.4  |     51   |  19   |   5   |  189   |
| RIAGENDR: Male                      | categorical |  5095 |         nan |        nan    |         48.95 | nan    |    nan   | nan   | nan   |  nan   |
| RIAGENDR: Female                    | categorical |  5314 |         nan |        nan    |         51.05 | nan    |    nan   | nan   | nan   |  nan   |
| RIAGENDR: Missing                   | categorical |     0 |         nan |        nan    |          0    | nan    |    nan   | nan   | nan   |  nan   |
| RIDRETH3: Mexican American          | categorical |  1273 |         nan |        nan    |         12.23 | nan    |    nan   | nan   | nan   |  nan   |
| RIDRETH3: Other Hispanic            | categorical |  1054 |         nan |        nan    |         10.13 | nan    |    nan   | nan   | nan   |  nan   |
| RIDRETH3: Non-Hispanic White        | categorical |  3519 |         nan |        nan    |         33.81 | nan    |    nan   | nan   | nan   |  nan   |
| RIDRETH3: Non-Hispanic Black        | categorical |  2762 |         nan |        nan    |         26.53 | nan    |    nan   | nan   | nan   |  nan   |
| RIDRETH3: Non-Hispanic Asian        | categorical |  1225 |         nan |        nan    |         11.77 | nan    |    nan   | nan   | nan   |  nan   |
| RIDRETH3: Other Race / Multi-Racial | categorical |   576 |         nan |        nan    |          5.53 | nan    |    nan   | nan   | nan   |  nan   |
| RIDRETH3: Missing                   | categorical |     0 |         nan |        nan    |          0    | nan    |    nan   | nan   | nan   |  nan   |
| LUAXSTAT: Complete                  | categorical |  9023 |         nan |        nan    |         86.68 | nan    |    nan   | nan   | nan   |  nan   |
| LUAXSTAT: Partial                   | categorical |   748 |         nan |        nan    |          7.19 | nan    |    nan   | nan   | nan   |  nan   |
| LUAXSTAT: Ineligible                | categorical |   386 |         nan |        nan    |          3.71 | nan    |    nan   | nan   | nan   |  nan   |
| LUAXSTAT: Not done                  | categorical |   252 |         nan |        nan    |          2.42 | nan    |    nan   | nan   | nan   |  nan   |
| LUAXSTAT: Missing                   | categorical |     0 |         nan |        nan    |          0    | nan    |    nan   | nan   | nan   |  nan   |

## S. Figures

- `LUXSMED_distribution.png` [OK]
- `LUXCAPM_distribution.png` [OK]
- `missingness_barchart.png` [OK]
- `missingness_heatmap.png` [OK]
- `liver_stiffness_by_sex.png` [OK]
- `liver_stiffness_by_age.png` [OK]
- `liver_stiffness_by_race_ethnicity.png` [OK]
- `liver_stiffness_by_bmi_group.png` [OK]
- `laboratory_distributions.png` [OK]
- `P_LUX_stiffness_distribution.png` [OK]
- `P_LUX_cap_distribution.png` [OK]
- `candidate_predictor_correlation_matrix.png` [OK]

All figures are DESCRIPTIVE ONLY. No model exists in Phase 1.

## T. Phase 2 Open Decisions

Full document with question/evidence/established/must-decide structure for each of the 11 open decisions: `documentation/audit_reports/phase2_open_decisions.md`. None of these decisions were made in this closure pass, per the non-negotiable rule against forcing premature methodological closure.

## U. Validation Results

| test_id   | description                                                                                              | status   | detail                                                                                                                 |
|:----------|:---------------------------------------------------------------------------------------------------------|:---------|:-----------------------------------------------------------------------------------------------------------------------|
| TEST1     | All eight raw files exist                                                                                | PASS     | missing=[]                                                                                                             |
| TEST2     | All eight raw files load without error                                                                   | PASS     | errors=[]                                                                                                              |
| TEST3     | All eight raw files contain SEQN                                                                         | PASS     | missing_seqn=[]                                                                                                        |
| TEST4     | No unexpected duplicate SEQN within any raw file                                                         | PASS     | files_with_dups=[]                                                                                                     |
| TEST5     | Master row count equals P_LUX row count                                                                  | PASS     | master=10409, P_LUX=10409                                                                                              |
| TEST6     | Master unique SEQN equals master row count                                                               | PASS     | unique=10409, rows=10409                                                                                               |
| TEST7     | Every cohort_flow.csv row satisfies n_before - n_excluded = n_after                                      | PASS     | bad_rows=[]                                                                                                            |
| TEST8     | Adult + under-18 + age-missing = non-missing-outcome denominator                                         | PASS     | 8318+1382+0 vs 9700                                                                                                    |
| TEST9     | observed + missing = total for every master-dataset variable                                             | PASS     | bad_cols=[]                                                                                                            |
| TEST10    | Laboratory observed + missing = total for all 9 lab variables                                            | PASS     | bad=[]                                                                                                                 |
| TEST11    | Table 1 LUXSMED median matches direct recomputation from master dataset                                  | PASS     | table1=5.0, recomputed=5.0                                                                                             |
| TEST12    | Final report generator reads all statistics from CSV audit outputs (procedural, verified by code review) | PASS     | 18_generate_phase1_report.py contains no manually-typed count; all values are read from CSV/parquet at generation time |
| TEST13    | No variable classified as both outcome_only and likely_eligible                                          | PASS     | overlap=set()                                                                                                          |
| TEST14    | Fasting-subset labs have materially higher missingness than a broad (non-fasting) lab                    | PASS     | fasting_missing_rate=0.549, broad_missing_rate=0.085                                                                   |
| TEST15    | Every observed RIDRETH1/RIDRETH3 code has a known official label                                         | PASS     | unknown_r1=set(), unknown_r3=set()                                                                                     |
| TEST16    | Any negative lab values present are captured in laboratory_plausibility_audit.csv (none silently missed) | PASS     | neg_found=[]                                                                                                           |
| TEST17    | All canonical cohort subset relationships hold (_cohorts.verify_cohort_relationships)                    | PASS     | no CohortRelationshipError raised                                                                                      |
| TEST18    | Fasting-cohort discrepancy (COHORT_FASTING_LABS_ONLY vs COHORT_B) fully reconciled                       | PASS     | discrepancy_rows=40, expected=40                                                                                       |
| TEST19    | Broad-cohort discrepancy (COHORT_A vs COHORT_A_PLUS_DEMO_BMI) fully reconciled                           | PASS     | discrepancy_rows=75, expected=75                                                                                       |
| TEST20    | Every cohort_flow.csv row references a canonical cohort_id from _cohorts.py                              | PASS     | unknown_ids=set()                                                                                                      |
| TEST21    | Every subgroup row satisfies positive + negative = n_with_outcome_available                              | PASS     | bad_rows=0                                                                                                             |
| TEST22    | No unverified auxiliary variable appears in the curated candidate-predictor pool (VAR_METADATA)          | PASS     | leaked=set()                                                                                                           |
| TEST23    | No unverified auxiliary variable is referenced by any canonical cohort definition (Issue 13)             | PASS     | leaked=set()                                                                                                           |
| TEST24    | phase1_reconciled_counts.csv 8.2kPa cutpoint count matches independent recomputation                     | PASS     | reported=939, recomputed=939                                                                                           |

## V. Final Readiness Decision

**PHASE 1 — COMPLETE AND FROZEN**

Every Closure Phase N sign-off criterion is satisfied: the 4,376-vs-4,336 and 8,880-vs-8,805 discrepancies are fully traced and reconciled (Section F); one authoritative definition exists for every data-feasibility cohort (Section E, `src/_cohorts.py`, TEST17); quality-valid and non-missing LUXSMED remain clearly distinguished everywhere (Section G); the official P_LUX quality-rule source is documented and confirmed to agree with the code (`lux_quality_rule_source.md`); adult counts are internally consistent in both denominators (Section E, TEST8); provisional threshold counts are reported against both documented denominators (Section G); Cohort A and Cohort B are both reproducible from raw data (TEST18/TEST19); subgroup and outcome-positive/negative counts reconcile (TEST21); unverified auxiliary variables are programmatically confirmed absent from both the candidate-predictor pool and every cohort definition (TEST22/TEST23); every statistic in this report is code-generated (TEST24 spot-check); all internal validation tests pass; the pipeline was re-run clean from raw data; independent spot-checks against raw data succeeded; no Phase 1 ambiguity remains.

**This is a data-foundation readiness decision only. Phase 1 does NOT authorize ML modeling, hyperparameter tuning, fairness mitigation, calibration modeling, or conformal prediction.**
