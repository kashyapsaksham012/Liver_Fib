# P_BMX Audit Report (Remediated)

**Generated:** 2026-08-18 13:27:20

## Shape

- Rows: 14300
- Columns: 22

## SEQN Check

- Unique SEQN: 14300
- Missing SEQN: 0

## Component Completeness Status (`BMDSTATS`) - official NHANES flag, previously unused

|   BMDSTATS |   count |
|-----------:|--------:|
|          1 |   13220 |
|          3 |     463 |
|          2 |     424 |
|          4 |     193 |

- 1=Complete data for age group, 2=Partial (height/weight only), 3=Other partial exam, 4=No body measures data.

## Key Anthropometrics

### Body Mass Index (BMI) (`BMXBMI`)

- Stats: N=13137 | min=11.90 | p25=20.40 | median=25.80 | p75=31.40 | max=92.30 | mean=26.66
- Missing: 1163 (8.13%)

### Weight (kg) (`BMXWT`)

- Stats: N=14075 | min=3.20 | p25=42.30 | median=68.10 | p75=86.30 | max=254.30 | mean=65.43
- Missing: 225 (1.57%)

### Height (cm) (`BMXHT`)

- Stats: N=13157 | min=78.30 | p25=151.10 | median=162.10 | p75=171.30 | max=199.60 | mean=156.49
- Missing: 1143 (7.99%)

## Measurement Comment Codes (previously not audited)

### BMIWT - Weight comment (1=Could not obtain, 3=Clothing, 4=Medical appliance)

|   BMIWT |   count |
|--------:|--------:|
|     nan |   13712 |
|       3 |     523 |
|       4 |      42 |
|       1 |      23 |

### BMIHT - Height comment (1=Could not obtain, 3=Not straight)

|   BMIHT |   count |
|--------:|--------:|
|     nan |   14129 |
|       3 |     101 |
|       1 |      70 |

## NHANES's own guidance on implausible values (verified from live codebook)

> "Unusual body measures values were noted during review. Typically, unusual values occurred when a subject was extremely short, tall, overweight, or underweight." NHANES does NOT define a numeric implausibility cutoff itself; any BMI/height/weight plausibility bound used elsewhere in this project is an externally-sourced clinical convention, documented as such.

## Missingness Table (post sentinel-correction)

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
