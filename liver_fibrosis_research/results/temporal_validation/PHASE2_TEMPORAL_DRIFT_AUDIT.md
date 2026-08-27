# Phase 2 — Temporal Drift Audit

Diagnostic comparison only. Does not explain cause or modify the original study.

## Part A — Cohort and outcome drift
- Original cohort N: 7153
- Temporal cohort N: 4910
- N difference: -2243
- Original outcome prevalence: 9.31%
- Temporal outcome prevalence: 11.47%
- Absolute prevalence difference: 0.0216
- Drift status: CLEAR DRIFT

## Part B — Predictor distribution drift
The per-variable file is `temporal_predictor_drift.csv`. For continuous variables, the predefined distribution-shift metric is the standardized mean difference (SMD).

## Part C — Missingness drift
The missingness file is `temporal_missingness_drift.csv`.

## Part D — Subgroup composition drift
The subgroup file is `temporal_subgroup_composition_drift.csv`.

## Part E — Measurement / variable drift
Only the ALT measurement bridge is directly supported: `LBXSATSI` in the 2021–2023 cohort was transformed via `Y_Cobas6000 = -1.529 + 1.035 * X_Cobas8000`.

## Part F — Temporal outcome distribution
The outcome distribution comparison is in `temporal_outcome_drift.csv`.

## Part G — Drift interpretation
This phase reports drift only; it does not infer causality or model root cause.

## Part H — Master drift table
`PHASE2_TEMPORAL_DRIFT_MASTER_TABLE.csv` contains the combined drift summary.

## Part I — Outputs created
- `PHASE2_TEMPORAL_DRIFT_AUDIT.md`
- `temporal_predictor_drift.csv`
- `temporal_missingness_drift.csv`
- `temporal_subgroup_composition_drift.csv`
- `temporal_outcome_drift.csv`
- `temporal_measurement_differences.csv`
- `PHASE2_TEMPORAL_DRIFT_MASTER_TABLE.csv`
