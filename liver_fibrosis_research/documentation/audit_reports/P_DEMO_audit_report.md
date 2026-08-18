# P_DEMO Audit Report

**Generated:** 2026-08-18 11:28:13

## Shape

- Rows: 15560
- Columns: 29

## All Columns

```
SEQN
SDDSRVYR
RIDSTATR
RIAGENDR
RIDAGEYR
RIDAGEMN
RIDRETH1
RIDRETH3
RIDEXMON
DMDBORN4
DMDYRUSZ
DMDEDUC2
DMDMARTZ
RIDEXPRG
SIALANG
SIAPROXY
SIAINTRP
FIALANG
FIAPROXY
FIAINTRP
MIALANG
MIAPROXY
MIAINTRP
AIALANGA
WTINTPRP
WTMECPRP
SDMVPSU
SDMVSTRA
INDFMPIR
```

## SEQN Check

- Unique SEQN: 15560
- Missing SEQN: 0

## Key Demographic Variables

### Age (`RIDAGEYR`)

|     RIDAGEYR |   count |
|-------------:|--------:|
| 80           |     682 |
|  5.39761e-79 |     574 |
|  2           |     431 |
|  1           |     406 |
| 10           |     354 |
| 11           |     351 |
|  9           |     339 |
|  8           |     331 |
|  5           |     317 |
|  3           |     312 |
|  7           |     310 |
|  4           |     302 |
|  6           |     300 |
| 14           |     286 |
| 12           |     261 |
| 13           |     258 |
| 17           |     254 |
| 16           |     248 |
| 18           |     234 |
| 15           |     233 |
| 60           |     232 |
| 19           |     227 |
| 61           |     208 |
| 55           |     202 |
| 62           |     198 |
| 63           |     195 |
| 64           |     178 |
| 56           |     174 |
| 54           |     170 |
| 41           |     167 |
| 33           |     165 |
| 66           |     159 |
| 52           |     157 |
| 59           |     157 |
| 29           |     156 |
| 47           |     156 |
| 65           |     155 |
| 42           |     154 |
| 32           |     153 |
| 57           |     153 |
| 23           |     150 |
| 48           |     149 |
| 45           |     149 |
| 70           |     148 |
| 28           |     146 |
| 50           |     146 |
| 22           |     145 |
| 39           |     145 |
| 67           |     144 |
| 31           |     143 |
| 36           |     142 |
| 69           |     142 |
| 24           |     142 |
| 34           |     142 |
| 43           |     141 |
| 58           |     140 |
| 46           |     140 |
| 40           |     139 |
| 53           |     139 |
| 30           |     137 |
| 68           |     135 |
| 25           |     135 |
| 38           |     135 |
| 37           |     133 |
| 44           |     132 |
| 27           |     128 |
| 26           |     128 |
| 51           |     127 |
| 21           |     126 |
| 35           |     126 |
| 71           |     125 |
| 20           |     122 |
| 72           |     120 |
| 49           |     119 |
| 74           |     110 |
| 73           |     102 |
| 75           |      94 |
| 77           |      81 |
| 76           |      76 |
| 79           |      69 |
| 78           |      69 |

Stats: N=15560 | min=0.000 | p25=10.000 | median=30.000 | p75=56.000 | max=80.000 | mean=33.742 | std=25.321

### Sex (`RIAGENDR`)

|   RIAGENDR |   count |
|-----------:|--------:|
|          2 |    7839 |
|          1 |    7721 |

Stats: N=15560 | min=1.000 | p25=1.000 | median=2.000 | p75=2.000 | max=2.000 | mean=1.504 | std=0.500

### Race/Ethnicity (`RIDRETH1`)

|   RIDRETH1 |   count |
|-----------:|--------:|
|          3 |    5271 |
|          4 |    4098 |
|          5 |    2657 |
|          1 |    1990 |
|          2 |    1544 |

Stats: N=15560 | min=1.000 | p25=3.000 | median=3.000 | p75=4.000 | max=5.000 | mean=3.250 | std=1.223

## Survey Weight Variables

- `WTINTPRP`: N=15560 | min=1017.784 | p25=7435.543 | median=12712.564 | p75=22761.141 | max=338363.600 | mean=20714.921 | std=25323.916
- `WTMECPRP`: N=15560 | min=0.000 | p25=6762.822 | median=12639.579 | p75=23308.392 | max=367555.743 | mean=20714.921 | std=27114.912

## Survey Design Variables

- `SDMVPSU`: {2.0: 7727, 1.0: 7491, 3.0: 342}
- `SDMVSTRA`: {156.0: 1015, 151.0: 779, 159.0: 760, 158.0: 735, 150.0: 701, 161.0: 695, 168.0: 693, 164.0: 693, 149.0: 691, 170.0: 689, 152.0: 681, 171.0: 662, 157.0: 653, 155.0: 638, 165.0: 612, 163.0: 609, 169.0: 605, 167.0: 604, 172.0: 596, 162.0: 554, 166.0: 551, 154.0: 510, 153.0: 510, 160.0: 324}

## Missingness Table

| variable   |   n_obs |   n_missing |   pct_missing |
|:-----------|--------:|------------:|--------------:|
| SEQN       |   15560 |           0 |          0    |
| SDDSRVYR   |   15560 |           0 |          0    |
| RIDSTATR   |   15560 |           0 |          0    |
| RIAGENDR   |   15560 |           0 |          0    |
| RIDAGEYR   |   15560 |           0 |          0    |
| RIDAGEMN   |     987 |       14573 |         93.66 |
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
| WTMECPRP   |   15560 |           0 |          0    |
| SDMVPSU    |   15560 |           0 |          0    |
| SDMVSTRA   |   15560 |           0 |          0    |
| INDFMPIR   |   13359 |        2201 |         14.15 |

> NOTE: Race/ethnicity groupings and age group bins are NOT finalized here. Collapsing decisions belong to Phase 2 analysis planning.
