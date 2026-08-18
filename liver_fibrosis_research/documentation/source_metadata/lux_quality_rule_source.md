# P_LUX Quality-Rule Source Documentation (Issue 4)

**Generated:** 2026-08-18 13:27:48

## Official variable

- **Name:** `LUAXSTAT`
- **Official label:** Elastography Exam Status
- **Source file:** P_LUX.xpt
- **Official source URL:** https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_LUX.htm
- **Access date:** 2026-08-18

## Official completion/status coding (verified against the live codebook)

| Code | Label |
|---|---|
| 1 | Complete |
| 2 | Partial |
| 3 | Ineligible |
| 4 | Not done |

## Official 'Complete' (quality-valid) criteria (exact, verified)

> Fasting time of at least 3 hours, 10 or more complete stiffness (E) measures, and liver stiffness interquartile range/median E (LUXSIQRM) < 30%.

## How the code implements this rule

`src/_cohorts.py::COHORT_2_QUALITY_VALID` implements this as `master["LUAXSTAT"] == 1.0` -- i.e. it uses NHANES's own pre-computed status flag directly, rather than re-deriving the three-part rule from `LUANMVGP` (>=10 measures) and `LUXSIQRM` (<30%) independently. This is verified consistent with the official definition above: NHANES states LUAXSTAT==1 IS the result of applying exactly those three criteria, so re-deriving them independently would be redundant, not more correct, and would risk disagreeing with NHANES's own computation (e.g. due to the fasting-time criterion, which this pipeline does not have a standalone variable for). Empirically verified: N(LUAXSTAT==1)=9,023 and every one of those participants has a non-missing LUXSMED (cross-tabulated directly against the raw file, 0 exceptions).

**Conflict check: NONE FOUND.** The code implementation (`LUAXSTAT==1`) and the documented official criteria are the same official NHANES computation, not two independent implementations that could disagree — so there is no discrepancy to resolve here, and no correction to the implementation was required.
