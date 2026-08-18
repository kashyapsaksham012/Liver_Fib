# P_DEMO Audit Report (Remediated)

**Generated:** 2026-08-18 13:27:20

## Shape

- Rows: 15560
- Columns: 29

## SEQN Check

- Unique SEQN: 15560
- Missing SEQN: 0

## Demographic Subgroups Availability

### Sex (`RIAGENDR`)

|   RIAGENDR |   count |
|-----------:|--------:|
|          2 |    7839 |
|          1 |    7721 |

### Race/Ethnicity (RIDRETH1, 5-cat) (`RIDRETH1`)

|   RIDRETH1 |   count |
|-----------:|--------:|
|          3 |    5271 |
|          4 |    4098 |
|          5 |    2657 |
|          1 |    1990 |
|          2 |    1544 |

### Race/Ethnicity (RIDRETH3, 6-cat, incl. NH Asian) (`RIDRETH3`)

|   RIDRETH3 |   count |
|-----------:|--------:|
|          3 |    5271 |
|          4 |    4098 |
|          1 |    1990 |
|          6 |    1638 |
|          2 |    1544 |
|          7 |    1019 |

### Age at Screening (topcoded at 80) (`RIDAGEYR`)

- Stats: N=14986 | min=1.00 | p25=11.00 | median=32.00 | p75=57.00 | max=80.00 | mean=35.03
- Missing: 574

> See `race_ethnicity_verification.md` for the RIDRETH1-vs-RIDRETH3 comparison and Phase 2 recommendation.

## Survey Weights & Design Variables (preserved, NOT yet applied to any analysis)

### WTMECPRP

- Stats: N=14300 | min=1116.25 | p25=8024.49 | median=13784.31 | p75=24696.45 | max=367555.74 | mean=22540.15

### WTINTPRP

- Stats: N=15560 | min=1017.78 | p25=7435.54 | median=12712.56 | p75=22761.14 | max=338363.60 | mean=20714.92

### SDMVPSU

|   SDMVPSU |   count |
|----------:|--------:|
|         2 |    7727 |
|         1 |    7491 |
|         3 |     342 |

### SDMVSTRA

|   SDMVSTRA |   count |
|-----------:|--------:|
|        156 |    1015 |
|        151 |     779 |
|        159 |     760 |
|        158 |     735 |
|        150 |     701 |
|        161 |     695 |
|        168 |     693 |
|        164 |     693 |
|        149 |     691 |
|        170 |     689 |

## Missingness Table (post sentinel-correction)

| variable   |   n_obs |   n_missing |   pct_missing |
|:-----------|--------:|------------:|--------------:|
| SEQN       |   15560 |           0 |          0    |
| SDDSRVYR   |   15560 |           0 |          0    |
| RIDSTATR   |   15560 |           0 |          0    |
| RIAGENDR   |   15560 |           0 |          0    |
| RIDAGEYR   |   14986 |         574 |          3.69 |
| RIDAGEMN   |     930 |       14630 |         94.02 |
| RIDRETH1   |   15560 |           0 |          0    |
| RIDRETH3   |   15560 |           0 |          0    |
| RIDEXMON   |   14300 |        1260 |          8.1  |
| DMDBORN4   |   15560 |           0 |          0    |
| DMDYRUSZ   |    3028 |       12532 |         80.54 |
| DMDEDUC2   |    9232 |        6328 |         40.67 |
| DMDMARTZ   |    9232 |        6328 |         40.67 |
| RIDEXPRG   |    1874 |       13686 |         87.96 |
| SIALANG    |   15560 |           0 |          0    |
| SIAPROXY   |   15560 |           0 |          0    |
| SIAINTRP   |   15560 |           0 |          0    |
| FIALANG    |   14481 |        1079 |          6.93 |
| FIAPROXY   |   14481 |        1079 |          6.93 |
| FIAINTRP   |   14481 |        1079 |          6.93 |
| MIALANG    |   11000 |        4560 |         29.31 |
| MIAPROXY   |   11000 |        4560 |         29.31 |
| MIAINTRP   |   11000 |        4560 |         29.31 |
| AIALANGA   |    8224 |        7336 |         47.15 |
| WTINTPRP   |   15560 |           0 |          0    |
| WTMECPRP   |   14300 |        1260 |          8.1  |
| SDMVPSU    |   15560 |           0 |          0    |
| SDMVSTRA   |   15560 |           0 |          0    |
| INDFMPIR   |   13217 |        2343 |         15.06 |
