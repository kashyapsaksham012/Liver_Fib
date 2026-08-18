# Laboratory File Audit Report (Remediated)

**Generated:** 2026-08-18 13:27:21

Profiles the five required NHANES 2017-March 2020 pre-pandemic laboratory files, sentinel-corrected. Fasting-subsample structure documented explicitly per component.

## P_BIOPRO.xpt [Broad MEC sample]

- **Dimensions:** 10409 rows x 41 columns
- **Unique SEQN:** 10409
- **Missing SEQN:** 0
- **Duplicate SEQN:** 0
- **Overlap with P_LUX cohort:** 10409 participants (100.0% of P_LUX N=10409)

### Target Variables Profile

| Variable | Official Description | Unit | Valid Obs | Missing | Missing % | Min | Max | Mean |
|---|---|---|---|---|---|---|---|---|
| `SEQN` | Respondent sequence number | - | 10409 | 0 | 0.0% | 109264.00 | 124822.00 | 117094.51 |
| `LBXSATSI` | Alanine Aminotransferase (ALT) | - | 9473 | 936 | 8.99% | 2.00 | 682.00 | 21.27 |
| `LBXSAL` | Albumin, refrigerated serum | - | 9477 | 932 | 8.95% | 2.10 | 5.40 | 4.08 |
| `LBXSAPSI` | Alkaline Phosphatase (ALP) | - | 9474 | 935 | 8.98% | 16.00 | 638.00 | 89.26 |
| `LBXSASSI` | Aspartate Aminotransferase (AST) | - | 9435 | 974 | 9.36% | 6.00 | 489.00 | 21.58 |
| `LBXSGL` | Glucose, serum (non-fasting, full biochemistry sample) | - | 9473 | 936 | 8.99% | 39.00 | 626.00 | 100.33 |
| `LBXSTB` | Total Bilirubin | - | 9475 | 934 | 8.97% | 0.10 | 3.80 | 0.46 |

---

## P_CBC.xpt [Broad MEC sample]

- **Dimensions:** 13772 rows x 22 columns
- **Unique SEQN:** 13772
- **Missing SEQN:** 0
- **Duplicate SEQN:** 0
- **Overlap with P_LUX cohort:** 10409 participants (100.0% of P_LUX N=10409)

### Target Variables Profile

| Variable | Official Description | Unit | Valid Obs | Missing | Missing % | Min | Max | Mean |
|---|---|---|---|---|---|---|---|---|
| `SEQN` | Respondent sequence number | - | 13772 | 0 | 0.0% | 109263.00 | 124822.00 | 117079.86 |
| `LBXPLTSI` | Platelet count | - | 12156 | 1616 | 11.73% | 8.00 | 1021.00 | 262.64 |

---

## P_GLU.xpt [FASTING SUBSAMPLE ONLY]

- **Dimensions:** 5090 rows x 4 columns
- **Unique SEQN:** 5090
- **Missing SEQN:** 0
- **Duplicate SEQN:** 0
- **Overlap with P_LUX cohort:** 5090 participants (48.9% of P_LUX N=10409)

> **Fasting subsample caveat (verified from official NHANES documentation):** eligibility requires age 12+, examination in the morning session, and a fast of 8 to <24 hours. This is a materially smaller and non-random subpopulation of the full P_LUX/MEC cohort, not just 'extra missingness'. The paired weight variable `WTSAFPRP` is 0 (not merely missing) for fasting-eligible participants who gave no specimen or did not meet the fasting window -- a documented, meaningful code.

- **`WTSAFPRP == 0` count in this file:** 0 (fasting-eligible but excluded from valid fasting analysis)

### Target Variables Profile

| Variable | Official Description | Unit | Valid Obs | Missing | Missing % | Min | Max | Mean |
|---|---|---|---|---|---|---|---|---|
| `SEQN` | Respondent sequence number | - | 5090 | 0 | 0.0% | 109264.00 | 124822.00 | 117177.33 |
| `WTSAFPRP` | Fasting subsample weight (2-cycle) | - | 4476 | 614 | 12.06% | 4808.07 | 741259.19 | 61275.55 |
| `LBXGLU` | Fasting Glucose | - | 4744 | 346 | 6.8% | 47.00 | 524.00 | 111.18 |

---

## P_TRIGLY.xpt [FASTING SUBSAMPLE ONLY]

- **Dimensions:** 5090 rows x 10 columns
- **Unique SEQN:** 5090
- **Missing SEQN:** 0
- **Duplicate SEQN:** 0
- **Overlap with P_LUX cohort:** 5090 participants (48.9% of P_LUX N=10409)

> **Fasting subsample caveat (verified from official NHANES documentation):** eligibility requires age 12+, examination in the morning session, and a fast of 8 to <24 hours. This is a materially smaller and non-random subpopulation of the full P_LUX/MEC cohort, not just 'extra missingness'. The paired weight variable `WTSAFPRP` is 0 (not merely missing) for fasting-eligible participants who gave no specimen or did not meet the fasting window -- a documented, meaningful code.

- **`WTSAFPRP == 0` count in this file:** 0 (fasting-eligible but excluded from valid fasting analysis)

### Target Variables Profile

| Variable | Official Description | Unit | Valid Obs | Missing | Missing % | Min | Max | Mean |
|---|---|---|---|---|---|---|---|---|
| `SEQN` | Respondent sequence number | - | 5090 | 0 | 0.0% | 109264.00 | 124822.00 | 117177.33 |
| `WTSAFPRP` | Fasting subsample weight (2-cycle) | - | 4476 | 614 | 12.06% | 4808.07 | 741259.19 | 61275.55 |
| `LBXTR` | Triglycerides | - | 4650 | 440 | 8.64% | 10.00 | 2684.00 | 103.72 |

---

## P_HDL.xpt [Broad MEC sample]

- **Dimensions:** 12198 rows x 3 columns
- **Unique SEQN:** 12198
- **Missing SEQN:** 0
- **Duplicate SEQN:** 0
- **Overlap with P_LUX cohort:** 10409 participants (100.0% of P_LUX N=10409)

### Target Variables Profile

| Variable | Official Description | Unit | Valid Obs | Missing | Missing % | Min | Max | Mean |
|---|---|---|---|---|---|---|---|---|
| `SEQN` | Respondent sequence number | - | 12198 | 0 | 0.0% | 109264.00 | 124822.00 | 117082.95 |
| `LBDHDD` | Direct HDL-Cholesterol | - | 10828 | 1370 | 11.23% | 5.00 | 189.00 | 53.47 |

---

