# Candidate Cohort Flow — Phase 1 CLOSURE (Canonical, Arithmetically Verified)

**Generated:** 2026-08-18 13:27:25

> Every row below satisfies `n_before - n_excluded == n_after` (asserted programmatically). Every named cohort is defined EXACTLY ONCE in `src/_cohorts.py` and imported here -- this script no longer recomputes any mask locally, closing the discrepancy class documented in `results/tables/fasting_cohort_discrepancy.csv` and `broad_cohort_discrepancy.csv`. Steps 2a/2b, 4a/4b, and 5a/5b are branches computed independently against their stated parent population, NOT chained sequentially, so no single combination is silently pre-selected as 'the' final cohort.

| Step | Cohort ID | N Before | N Excluded | N After | % LUAXSTAT==1 in result | Reason |
|---|---|---|---|---|---|---|
| 0. P_LUX Total Participants (source cohort denominator) | `COHORT_0_SOURCE` | 10409 | 0 | 10409 | 86.68% | Root cohort; every subsequent row is a subset of this population |
| 1. Non-missing LUXSMED (NOTE: non-missingness, NOT the NHANES quality-valid flag) | `COHORT_1_NONMISSING_LUX` | 10409 | 709 | 9700 | 93.02% | Missing/invalid FibroScan attempt (LUAXSTAT in {3,4}, or {2} with no numeric result) |
| 1b. NHANES Quality-Valid Elastography (LUAXSTAT==1), among Step 1 (Issue 3) | `COHORT_2_QUALITY_VALID` | 9700 | 677 | 9023 | 100.0% | Official NHANES 'Complete' definition (fasting>=3h, >=10 complete measures, IQRe/Med<30%) -- see documentation/source_metadata/lux_quality_rule_source.md. These 677 participants have a non-missing LUXSMED from a Partial (LUAXSTAT=2) exam that does not meet the full quality bar. |
| 2a. Adult Participants (Age>=18), among Step 1 (non-missing LUXSMED) | `COHORT_3A_ADULT_OF_NONMISSING` | 9700 | 1382 | 8318 | 93.39% | CANDIDATE Phase 2 restriction, reported for descriptive flow accounting only |
| 2b. Adult Participants (Age>=18), among Step 1b (quality-valid) (Issue 6) | `COHORT_3B_ADULT_OF_QUALITY_VALID` | 9023 | 1255 | 7768 | 100.0% | Reported separately because the quality-valid population (9,023) is NOT the same as the non-missing population (9,700) -- the two adult counts are not assumed identical |
| 3. Demographics Available (RIAGENDR non-missing), among Step 1 | `COHORT_1_NONMISSING_LUX` | 9700 | 0 | 9700 | 93.02% | Fairness analysis requirement |
| 4a. Broad Routine-Lab Predictors Available (Cohort A), among Step 1 | `COHORT_A_BROAD_LAB` | 9700 | 820 | 8880 | 93.22% | Candidate broad-lab predictor cohort (LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD all non-missing); does NOT require BMI/demographics (Issue 9: renamed for clarity, was 'Step 5') |
| 4b. Cohort A FURTHER restricted to complete demographics + BMI (Issue 2/9) | `COHORT_A_PLUS_DEMO_BMI` | 8880 | 75 | 8805 | 93.3% | Strict nesting inside Cohort A. NOT a separate lab-availability concept, and NOT the same population as Cohort A (75-participant gap, entirely explained by missing BMI -- see results/tables/broad_cohort_discrepancy.csv). Renamed from ambiguous 'combined broad cohort'. |
| 5a. Fasting-Subsample Labs Available ONLY (glucose+triglycerides, broad NOT required) | `COHORT_FASTING_LABS_ONLY` | 9700 | 5324 | 4376 | 94.9% | [BRANCH, not chained into the main flow] Renamed from ambiguous 'fasting labs available' -- see results/tables/fasting_cohort_discrepancy.csv for why this differs from Cohort B below |
| 5b. Cohort B = Fasting-Extended (Cohort A AND fasting labs) (Issue 1, THE canonical 'Cohort B') | `COHORT_B_FASTING_EXTENDED` | 8880 | 4544 | 4336 | 94.86% | Requires BOTH broad labs (Cohort A) AND fasting labs. Exactly the intersection of Step 4a and Step 5a (asserted programmatically in _cohorts.verify_cohort_relationships) -- this IS the authoritative Cohort B number used everywhere else in this pipeline (4,336, not 4,376). |

**Final inclusion/exclusion logic, adult-only decision, and quality-valid-only decision all remain OPEN Phase 2 protocol decisions. No cohort defined above is asserted to be final.**
