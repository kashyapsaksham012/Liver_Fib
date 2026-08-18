# Phase 1 Data Assembly Report

**Generated:** 2026-08-18 11:28:22  
**Python:** 3.14.3 (main, Feb  3 2026, 15:32:20) [Clang 17.0.0 (clang-1700.6.3.2)]

---

## A. Execution Status

**PARTIALLY COMPLETE**

Core files (P_LUX, P_DEMO, P_BMX) successfully assembled. Laboratory XPT files not yet present — Phase 1 is BLOCKED on laboratory data.

## B. Raw Files Found

| File | Size | Rows | Cols |
|---|---|---|---|
| P_BMX.xpt | 2.52 MB | 14300 | 22 |
| P_DEMO.xpt | 3.61 MB | 15560 | 29 |
| P_LUX.xpt | 1.11 MB | 10409 | 13 |

## C. Dataset Shapes

| Dataset | Rows | Cols |
|---|---|---|
| P_LUX | 10409 | 13 |
| P_DEMO | 15560 | 29 |
| P_BMX | 14300 | 22 |
| **MASTER** | **10409** | **62** |

## D. Linkage Audit (SEQN)

| dataset             |   rows |   unique_seqn |   missing_seqn |   duplicate_seqn |
|:--------------------|-------:|--------------:|---------------:|-----------------:|
| P_LUX               |  10409 |         10409 |              0 |                0 |
| P_DEMO              |  15560 |         15560 |              0 |                0 |
| P_BMX               |  14300 |         14300 |              0 |                0 |
| MERGE: LUX+DEMO     |  10409 |         10409 |              0 |                0 |
| MERGE: LUX+DEMO+BMX |  10409 |         10409 |              0 |                0 |

All merges confirmed one-to-one. No row multiplication detected.

## E. Final Candidate Cohort

| step                               | n       | excluded   | reason                             |
|:-----------------------------------|:--------|:-----------|:-----------------------------------|
| P_LUX total participants           | 10409   | 0          | Starting cohort                    |
| Valid liver stiffness measurement  | 9700    | 709        | Missing/invalid FibroScan          |
| Age ≥ 18 (adults only – candidate) | 8965    | TBD        | Pending Phase 2 outcome definition |
| Demographic data available         | 10409   | TBD        | Required for fairness analysis     |
| BMI available                      | 10213   | TBD        | Candidate predictor/subgroup       |
| Laboratory data available          | PENDING | PENDING    | Lab files not yet downloaded       |

> Laboratory data absent – final candidate N cannot be confirmed until lab files are added.

## F. P_LUX Findings

- Stiffness variable identified: `LUXSMED`
- Valid measurements: 9700
- Missing: 709
- Range: 1.60 – 75.00 kPa
- Median: 5.00 kPa
- Mean: 5.89 kPa

### Candidate Threshold Analysis (descriptive only)

| Threshold (kPa) | N Positive | % Positive |
|---|---|---|
| 7.0 | 1506 | 15.5% |
| 7.5 | 1223 | 12.6% |
| 8.0 | 1000 | 10.3% |
| 8.5 | 840 | 8.7% |
| 9.0 | 712 | 7.3% |
| 10.0 | 568 | 5.9% |
| 12.0 | 367 | 3.8% |

> Threshold selection deferred to Phase 2.

## G. Demographic Availability

### Sex (`RIAGENDR`)

|   RIAGENDR |   count |
|-----------:|--------:|
|          2 |    5314 |
|          1 |    5095 |

### Race/Ethnicity (`RIDRETH3`)

|   RIDRETH3 |   count |
|-----------:|--------:|
|          3 |    3519 |
|          4 |    2762 |
|          1 |    1273 |
|          6 |    1225 |
|          2 |    1054 |
|          7 |     576 |

### Age (`RIDAGEYR`)

- Range: 12 – 80 years
- Mean: 44.6 | Median: 45.0

## H. Laboratory Availability

**STATUS: BLOCKED** — No laboratory XPT files found in `data/raw/NHANES_2017_2020/`.

Required files from NHANES 2017-Mar2020 pre-pandemic cycle:

| Component | Expected File | Key Variables |
|---|---|---|
| Biochemistry Profile | P_BIOPRO.XPT | AST, ALT, Albumin, Bilirubin, Alk Phos |
| Complete Blood Count | P_CBC.XPT | Platelets |
| Glucose (fasting) | P_GLU.XPT | Glucose |
| Lipids | P_TRIGLY.XPT / P_HDL.XPT | Triglycerides, HDL |

Download from: https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Laboratory&CycleBeginYear=2017

## I. Data Quality

- Duplicate SEQN detected: **None** (all files clean)
- Plausibility flags raised: **2**

| variable   | suspected_issue            |   observation_count | proposed_action                         | justification                                    |
|:-----------|:---------------------------|--------------------:|:----------------------------------------|:-------------------------------------------------|
| BMXBMI     | BMI > 80 (extreme outlier) |                   5 | Investigate – do not auto-remove        | Possible but unusual; confirm with height/weight |
| RIDAGEYR   | Age < 18                   |                1444 | Potentially exclude – adults only study | FibroScan reference values are adult-specific    |

- Variables with >50% missingness: 18
  - ['BMXRECUM', 'BMIRECUM', 'BMXHEAD', 'BMIHEAD', 'RIDAGEMN', 'BMIHT', 'LUARXND', 'BMIARML', 'BMIARMC', 'BMIWT', 'BMIHIP', 'LUARXIN', 'BMIWAIST', 'BMILEG', 'LUARXNC', 'RIDEXPRG', 'BMDBMIC', 'DMDYRUSZ']

## J. Master Dataset

- Path: `data/interim/nhanes_master_phase1.parquet`
- Dimensions: 10409 rows × 62 columns

## K. Outstanding Decisions for Phase 2

- [ ] Download and integrate NHANES laboratory files (BIOPRO, CBC, GLU, TRIGLY, HDL)
- [ ] Define liver fibrosis outcome threshold (candidate: ≥ 8 kPa; do NOT choose based on ML performance)
- [ ] Define FibroScan quality inclusion criteria (IQR/median ratio, examination status)
- [ ] Decide adult-only restriction age floor (e.g., ≥ 18 years)
- [ ] Define race/ethnicity groupings for fairness analysis
- [ ] Define age group bins for fairness analysis
- [ ] Define BMI category cutpoints
- [ ] Choose missing-data strategy (median imputation vs multiple imputation)
- [ ] Decide whether and how to apply NHANES survey weights
- [ ] Confirm no target leakage before feature matrix construction
- [ ] Resolve plausibility flags before modeling

## L. Phase 1 Scientific Readiness

**NO**

Phase 1 is PARTIALLY COMPLETE. The dataset is not ready for Phase 2 because:

1. **Laboratory files are absent.** Required predictor variables (AST, ALT, albumin, bilirubin, platelets, glucose, lipids) have not been downloaded or integrated.
2. **Outcome definition deferred.** The fibrosis threshold must be pre-specified using clinical criteria before any modeling begins.
3. **Quality exclusion criteria not finalized.** FibroScan IQR/quality filter must be defined before the final cohort is established.

**Next required action:** Download the NHANES 2017-Mar2020 laboratory XPT files listed in section H, place them in `data/raw/NHANES_2017_2020/`, and re-run the full Phase 1 pipeline.
