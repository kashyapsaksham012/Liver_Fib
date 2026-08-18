# P_LUX Audit Report (Remediated)

**Generated:** 2026-08-18 13:27:20

## Shape

- Rows: 10409
- Columns: 13

## SEQN Check

- Unique SEQN: 10409
- Missing SEQN: 0
- Duplicate SEQN: 0

## OFFICIAL NHANES Quality-Valid Exam Definition (verified against live P_LUX codebook)

> `LUAXSTAT == 1` ('Complete') is officially defined by NHANES as: fasting time of at least 3 hours, 10 or more complete stiffness (E) measures, AND stiffness IQR/median (LUXSIQRM) < 30%. This is NHANES's own definition, not a criterion invented by this project. Prior Phase 1 material incorrectly treated 'non-missing LUXSMED' as equivalent to a quality-valid measurement; this report corrects that terminology throughout.

### LUAXSTAT distribution

| Code | Meaning | N |
|---|---|---|
| 1.0 | Complete (quality-valid) | 9023 |
| 2.0 | Partial | 748 |
| 3.0 | Ineligible | 386 |
| 4.0 | Not done | 252 |

### Reconciliation: non-missing LUXSMED vs. quality-valid exam

- Non-missing `LUXSMED` (any completeness): **9700**
- `LUAXSTAT == 1` (official quality-valid, 'Complete'): **9023**
- Non-missing `LUXSMED` AND `LUAXSTAT == 1`: **9023**
- Non-missing `LUXSMED` but NOT quality-valid (LUAXSTAT in {2,3,4}, i.e. mostly Partial exams that still produced a numeric median): **677**

> These are two different populations. Phase 2 must decide, as a pre-specified protocol choice, whether the analytical cohort requires `LUAXSTAT==1` or only non-missing `LUXSMED`. This decision is NOT made here.

## Outcomes Profile

### Liver Stiffness (`LUXSMED`)

- Non-missing (any completeness): 9700
- Stats: N=9700 | min=1.60 | p25=4.10 | median=5.00 | p75=6.10 | max=75.00 | mean=5.89

#### Candidate Cutpoint Counts, ALL non-missing LUXSMED (Descriptive / Feasibility Only)

| Cutpoint (kPa) | N >= Cutpoint | % >= Cutpoint | Candidate Label | Citation |
|---|---|---|---|---|
| 7.0 | 1506 | 15.53% | General cutoff (literature range, low end) | literature range, non-specific |
| 7.5 | 1223 | 12.61% | General cutoff (literature range) | literature range, non-specific |
| 8.0 | 1000 | 10.31% | Candidate: significant fibrosis (>=F2), lower literature estimate | Multiple NAFLD/MASLD VCTE studies; see phase1_references.md |
| 8.2 | 939 | 9.68% | Candidate: significant fibrosis (>=F2), meta-analytic Youden-optimal cutoff | VCTE-vs-MRE meta-analysis, PMC11493355 (2024) |
| 9.0 | 712 | 7.34% | General cutoff (literature range) | literature range, non-specific |
| 9.7 | 604 | 6.23% | Candidate: advanced fibrosis (>=F3), meta-analytic Youden-optimal cutoff | VCTE-vs-MRE meta-analysis, PMC11493355 (2024) |
| 10.0 | 568 | 5.86% | Candidate: advanced fibrosis (>=F3) / cACLD rule-of-thumb, commonly-cited round number | Widely used practical rule-of-thumb; literature range for advanced fibrosis spans 6.8-13.6 kPa (e-cmh.org editorial) |
| 12.0 | 367 | 3.78% | Candidate: cirrhosis (F4), commonly-cited round number | Widely used practical rule-of-thumb |
| 13.6 | 278 | 2.87% | Candidate: cirrhosis (F4), meta-analytic Youden-optimal cutoff | VCTE-vs-MRE meta-analysis, PMC11493355 (2024) |

> NOTE: All cutpoints above are CANDIDATE / provisional, sourced from external clinical literature (see documentation/source_metadata/phase1_references.md), NOT from NHANES documentation, and NOT finalized. Do NOT select a threshold by optimizing ML performance.

#### Same table restricted to LUAXSTAT==1 (quality-valid) subset, N=9023

| Cutpoint (kPa) | N >= Cutpoint | % >= Cutpoint |
|---|---|---|
| 7.0 | 1295 | 14.35% |
| 7.5 | 1033 | 11.45% |
| 8.0 | 828 | 9.18% |
| 8.2 | 772 | 8.56% |
| 9.0 | 576 | 6.38% |
| 9.7 | 474 | 5.25% |
| 10.0 | 443 | 4.91% |
| 12.0 | 271 | 3.0% |
| 13.6 | 196 | 2.17% |

### Controlled Attenuation Parameter (`LUXCAPM`)

- Non-missing: 9698
- Stats: N=9698 | min=100.00 | p25=211.00 | median=253.00 | p75=302.00 | max=400.00 | mean=257.59

## Quality / Status Variables Profile

### LUAXSTAT

|   LUAXSTAT |   count |
|-----------:|--------:|
|          1 |    9023 |
|          2 |     748 |
|          3 |     386 |
|          4 |     252 |

### LUARXNC

|   LUARXNC |   count |
|----------:|--------:|
|       nan |    9661 |
|         1 |     371 |
|         3 |     198 |
|         2 |     179 |

### LUARXND

|   LUARXND |   count |
|----------:|--------:|
|       nan |   10157 |
|         3 |     115 |
|         2 |      76 |
|         1 |      61 |

### LUARXIN

|   LUARXIN |   count |
|----------:|--------:|
|       nan |   10023 |
|         2 |     238 |
|         1 |     148 |

### LUANMVGP

- Stats: N=9700 | min=1.00 | p25=10.00 | median=10.00 | p75=12.00 | max=30.00 | mean=11.11

### LUANMTGP

- Stats: N=9738 | min=1.00 | p25=10.00 | median=12.00 | p75=16.00 | max=30.00 | mean=14.39

## Missingness Table (post sentinel-correction)

| variable   |   n_obs |   n_missing |   pct_missing |
|:-----------|--------:|------------:|--------------:|
| SEQN       |   10409 |           0 |          0    |
| LUAXSTAT   |   10409 |           0 |          0    |
| LUARXNC    |     748 |        9661 |         92.81 |
| LUARXND    |     252 |       10157 |         97.58 |
| LUARXIN    |     386 |       10023 |         96.29 |
| LUAPNME    |   10409 |           0 |          0    |
| LUANMVGP   |    9700 |         709 |          6.81 |
| LUANMTGP   |    9738 |         671 |          6.45 |
| LUXSMED    |    9700 |         709 |          6.81 |
| LUXSIQR    |    9679 |         730 |          7.01 |
| LUXSIQRM   |    9679 |         730 |          7.01 |
| LUXCAPM    |    9698 |         711 |          6.83 |
| LUXCPIQR   |    9609 |         800 |          7.69 |
