# Phase 3 -- deferral-rule development (Amendment #17)

Developed on the conformal-calibration partition (N=1,002) only. No locked-test access.

**Mechanism established in Phase 2-3:** in the under-covered subgroups (BMI-Obese, Age-60+) the conformal *coverage* is carried by the two-class {pos,neg} prediction sets, which always contain the truth; the misses are wrong SINGLETON predictions. A rule that defers 'uncertain' cases (two-class sets) therefore *lowers* retained coverage. Only deferring *weak singletons* (candidate 3b), or widening the sets group-conditionally (3d/3e), can help.

## Candidate metrics (per model, calibration partition)

| candidate   | model         |   defer_rate_overall |   retained_marginal_cov |   cov_bmi_Obese |   cov_age_60+ |   cov_bmi_Normal |   cov_bmi_Overweight |   cov_age_18-39 |   csens_bmi_Normal |   csens_bmi_Obese |   defer_bmi_Obese |   defer_age_60+ | G1    | G2    | G3    | G4proxy   | G6    | G7   | core   |
|:------------|:--------------|---------------------:|------------------------:|----------------:|--------------:|-----------------:|---------------------:|----------------:|-------------------:|------------------:|------------------:|----------------:|:------|:------|:------|:----------|:------|:-----|:-------|
| 3a          | logistic      |             0.422156 |                0.829016 |        0.57754  |      0.568182 |         0.973822 |             0.92973  |        0.941176 |           0.333333 |          0.977778 |          0.540541 |        0.610619 | False | False | False | False     | False | True | False  |
| 3b          | logistic      |             0.148703 |                0.953107 |        0.901361 |      0.928571 |         0.985849 |             0.981928 |        0.965517 |           0.625    |          1        |          0.277641 |        0.215339 | True  | False | False | False     | True  | True | False  |
| 3d          | logistic      |             0        |                0.94511  |        0.904177 |      0.920354 |         0.982759 |             0.971182 |        0.95092  |           0.555556 |          0.985294 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3e          | logistic      |             0        |                0.94511  |        0.904177 |      0.920354 |         0.982759 |             0.971182 |        0.95092  |           0.555556 |          0.985294 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3a          | random_forest |             0.242515 |                0.868248 |        0.670543 |      0.762376 |         0.980861 |             0.964029 |        0.924399 |           0.4      |          0.833333 |          0.366093 |        0.40413  | False | False | False | False     | True  | True | False  |
| 3b          | random_forest |             0.175649 |                0.955206 |        0.903846 |      0.938931 |         0.986425 |             0.975684 |        0.958333 |           0.666667 |          0.973684 |          0.361179 |        0.227139 | True  | False | False | False     | True  | True | False  |
| 3d          | random_forest |             0        |                0.949102 |        0.904177 |      0.935103 |         0.987069 |             0.976945 |        0.957055 |           0.666667 |          0.970588 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3e          | random_forest |             0        |                0.949102 |        0.904177 |      0.935103 |         0.987069 |             0.976945 |        0.957055 |           0.666667 |          0.970588 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3a          | xgboost       |             0.302395 |                0.858369 |        0.644068 |      0.710383 |         0.97449  |             0.964427 |        0.942238 |           0.4      |          0.959184 |          0.420147 |        0.460177 | False | False | False | False     | True  | True | False  |
| 3b          | xgboost       |             0.180639 |                0.959805 |        0.903571 |      0.956897 |         0.99061  |             0.990385 |        0.959732 |           0.75     |          0.954545 |          0.312039 |        0.315634 | True  | False | False | False     | True  | True | False  |
| 3d          | xgboost       |             0        |                0.951098 |        0.904177 |      0.941003 |         0.987069 |             0.982709 |        0.96319  |           0.777778 |          0.970588 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3e          | xgboost       |             0        |                0.951098 |        0.904177 |      0.941003 |         0.987069 |             0.982709 |        0.96319  |           0.777778 |          0.970588 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3a          | lightgbm      |             0.311377 |                0.856522 |        0.628205 |      0.745455 |         0.989744 |             0.963563 |        0.925    |           0.5      |          0.958333 |          0.425061 |        0.513274 | False | False | False | False     | True  | True | False  |
| 3b          | lightgbm      |             0.162675 |                0.957092 |        0.90378  |      0.953125 |         0.990566 |             0.984375 |        0.959459 |           0.777778 |          0.979592 |          0.285012 |        0.244838 | True  | False | False | False     | True  | True | False  |
| 3d          | lightgbm      |             0        |                0.953094 |        0.904177 |      0.946903 |         0.991379 |             0.985591 |        0.960123 |           0.777778 |          0.985294 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3e          | lightgbm      |             0        |                0.953094 |        0.904177 |      0.946903 |         0.991379 |             0.985591 |        0.960123 |           0.777778 |          0.985294 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3a          | mlp           |             0        |                0.901198 |        0.815725 |      0.864307 |         0.965517 |             0.956772 |        0.93865  |           0.111111 |          0.102941 |          0        |        0        | False | True  | False | True      | True  | True | False  |
| 3b          | mlp           |             0.394212 |                0.927512 |        0        |      0.892683 |         0.965517 |             0.961424 |        0.961353 |           0.111111 |          0        |          0.945946 |        0.39528  | False | True  | False | True      | True  | True | False  |
| 3d          | mlp           |             0        |                0.937126 |        0.904177 |      0.932153 |         0.969828 |             0.95389  |        0.953988 |           0.222222 |          0.441176 |          0        |        0        | True  | False | False | False     | True  | True | False  |
| 3e          | mlp           |             0        |                0.937126 |        0.904177 |      0.932153 |         0.969828 |             0.95389  |        0.953988 |           0.222222 |          0.441176 |          0        |        0        | True  | False | False | False     | True  | True | False  |

## Selection

| candidate   |   models_core_pass |   mean_defer |
|:------------|-------------------:|-------------:|
| 3d          |                  0 |     0        |
| 3e          |                  0 |     0        |
| 3b          |                  0 |     0.212375 |
| 3a          |                  0 |     0.255689 |

**Selected: `3d`** -- passes the core coverage+burden gate for **0/5** models on the calibration partition.

Frozen manifest SHA-256: `13435ceb11044f0013a6389fc29b60a03d1bd57144593d519c5f680413cefd96`  
Frozen at: 2026-08-27T10:22:36.202233+00:00


## Verdict: DEVELOPMENT-STAGE NEGATIVE (per the pre-registered gate)

No candidate in the pre-registered family (3a, 3b, 3d, 3e) meets the full core gate (G1 & G2 & G3 & G6 & G7) on the calibration partition. **Per the plan the locked test is NOT touched** (Phase 4 skipped). No post-hoc gate relaxation or new candidate is permitted.

**Characterised negative -- what the pre-registered candidates do and do not achieve:**

1. **Deferring 'uncertain' cases makes coverage worse, not better (3a).** In BMI-Obese and Age-60+ the conformal coverage is carried by the two-class {pos,neg} sets (which always contain the truth); the misses are wrong *singletons*. Deferring the two-class sets (3a) removes the covering predictions -- retained BMI-Obese coverage falls to 0.58-0.82 (worse than the 0.77-0.82 unmitigated).

2. **Deferring weak singletons (3b) can lift the under-covered groups to ~0.90**, but only by deferring 15-40 % overall and, for the near-singleton MLP, degenerately (defers ~95 % of obese cases). It fails G2 (retained marginal coverage rises) and does not generalise cleanly across families.

3. **Group-conditional (Mondrian) conformal (3d) restores BMI-Obese and Age-60+ coverage to >= 0.88 for 5/5 models with zero deferral** -- an improvement on Project Phase 7's 5/9 targets -- **but necessarily raises retained marginal coverage to 0.94-0.95** (G2 fail) and leaves the well-served subgroups above 0.95 (G3 fail). Forcing marginal coverage back to <= 0.93 would require deliberately under-covering the well-served subgroups -- *levelling down*, the fairness anti-pattern documented for coverage-equalising conformal methods (arXiv:2412.07879; ICLR 2025).

**Reportable finding:** on this task, subgroup-safe conformal coverage and target-level marginal coverage cannot be jointly achieved by any pre-registered post-hoc method without levelling down the well-served subgroups; and the under-coverage is not concentrated in flagged-uncertain cases (so selective deferral does not fix it) but in confidently-wrong singleton predictions in the obese and older groups -- a failure of the model's within-subgroup score ordering that a post-hoc decision layer cannot repair.
