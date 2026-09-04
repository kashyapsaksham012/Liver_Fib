# Temporal outcome touch log

One entry per use of the NHANES 2021–2023 primary outcome
(`temporal_cohort_2021_2023.parquet`, `outcome_primary_8.2kPa`).

| # | UTC | script | cohort SHA-256 (16) | nature |
|---|---|---|---|---|
| 1 | 2026-09-04T09:47Z / 09:48Z | `src/t03_apply_and_evaluate.py` | `59daca140e683d66` | Single non-iterative evaluation of the frozen `phase3` (full-train) and `phase6_conformal_refit` (proper-train) models on the 2021–2023 primary outcome, **raw predictors, no crosswalk**. Computes discrimination, calibration (raw + frozen Platt), subgroup fairness, split-conformal coverage, the dissociation check, and the matched-stiffness shortcut. |

**Note on the two timestamps for entry 1.** The script was executed, aborted on
an ancillary step (`statsmodels` not installed — used only for the matched-stiffness
OLS), the OLS was reimplemented with `numpy.linalg.lstsq`, and the script was
re-run. The re-run reproduced the discrimination / calibration / fairness /
conformal numbers **bit-for-bit** (deterministic; seed 42; no test-set-derived
tuning of any kind). This is a reproducibility re-run, not a second inspection
that could bias model or parameter selection — nothing about the frozen models,
thresholds, Platt parameters, or conformal quantile was chosen or changed.

**Leakage.** The 2021–2023 cohort SEQNs are from a later NHANES cycle and are
disjoint from the 2017–March 2020 train / test / conformal-calibration
partitions by construction. No SEQN overlap.

**No frozen artifact was written.** All outputs are under
`temporal_validation_2021_2023/`.
