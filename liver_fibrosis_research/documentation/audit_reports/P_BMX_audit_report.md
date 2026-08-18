# P_BMX Audit Report

**Generated:** 2026-08-18 11:28:13

## Shape

- Rows: 14300
- Columns: 22

## All Columns

```
SEQN
BMDSTATS
BMXWT
BMIWT
BMXRECUM
BMIRECUM
BMXHEAD
BMIHEAD
BMXHT
BMIHT
BMXBMI
BMDBMIC
BMXLEG
BMILEG
BMXARML
BMIARML
BMXARMC
BMIARMC
BMXWAIST
BMIWAIST
BMXHIP
BMIHIP
```

## SEQN Check

- Unique SEQN: 14300
- Missing SEQN: 0

## BMI (`BMXBMI`)

- Stats: N=13137 | min=11.900 | p25=20.400 | median=25.800 | p75=31.400 | max=92.300 | mean=26.657 | std=8.420
- Missing: 1163 (8.1%)

## Height (cm) (`BMXHT`)

- Stats: N=13157 | min=78.300 | p25=151.100 | median=162.100 | p75=171.300 | max=199.600 | mean=156.490 | std=22.621
- Missing: 1143 (8.0%)

## Weight (kg) (`BMXWT`)

- Stats: N=14075 | min=3.200 | p25=42.300 | median=68.100 | p75=86.300 | max=254.300 | mean=65.426 | std=33.332
- Missing: 225 (1.6%)

## Plausibility Notes

- BMI > 70: 11 records (flagged for review, NOT removed)
- BMI < 10: 0 records (flagged for review, NOT removed)

## Missingness Table

| variable   |   n_obs |   n_missing |   pct_missing |
|:-----------|--------:|------------:|--------------:|
| SEQN       |   14300 |           0 |          0    |
| BMDSTATS   |   14300 |           0 |          0    |
| BMXWT      |   14075 |         225 |          1.57 |
| BMIWT      |     588 |       13712 |         95.89 |
| BMXRECUM   |    1470 |       12830 |         89.72 |
| BMIRECUM   |      43 |       14257 |         99.7  |
| BMXHEAD    |     310 |       13990 |         97.83 |
| BMIHEAD    |       0 |       14300 |        100    |
| BMXHT      |   13157 |        1143 |          7.99 |
| BMIHT      |     171 |       14129 |         98.8  |
| BMXBMI     |   13137 |        1163 |          8.13 |
| BMDBMIC    |    4749 |        9551 |         66.79 |
| BMXLEG     |   10984 |        3316 |         23.19 |
| BMILEG     |     488 |       13812 |         96.59 |
| BMXARML    |   13490 |         810 |          5.66 |
| BMIARML    |     487 |       13813 |         96.59 |
| BMXARMC    |   13484 |         816 |          5.71 |
| BMIARMC    |     493 |       13807 |         96.55 |
| BMXWAIST   |   12574 |        1726 |         12.07 |
| BMIWAIST   |     617 |       13683 |         95.69 |
| BMXHIP     |    9862 |        4438 |         31.03 |
| BMIHIP     |     376 |       13924 |         97.37 |
