# Phase 3 temporal-validation preflight failure

**Status: FAILED — DO NOT PROCEED.**

Date checked: 2026-08-26 (Asia/Kolkata).

## Available temporal inputs

- `predictions/temporal_prediction_manifest.json` records 4,910 frozen-model predictions for each of the five models.
- `data/processed/temporal_validation/temporal_validation_input_cobas6000_alt.csv` has 4,910 rows and exactly these columns: `SEQN`, the 10 frozen model predictors (`RIDAGEYR`, `RIAGENDR`, `BMXBMI`, `LBXSATSI`, `LBXSASSI`, `LBXSAL`, `LBXSAPSI`, `LBXSTB`, `LBXPLTSI`, `LBDHDD`).
- Its manifest explicitly records `outcome_columns_written: []`.

## Blocking missing input

No independently prepared 2021–2023 temporal cohort/outcome companion dataset is present anywhere under `liver_fibrosis_research/data`. In particular, no file is available that can be joined to the frozen predictions by `SEQN` to provide:

- the frozen primary outcome (`outcome_primary_8.2kPa`, or the components/data required to derive it under the pre-specified definition);
- `RIDRETH3`, required for the pre-specified race/ethnicity fairness analysis.

The available temporal input does include age, sex, and BMI, but this does not resolve the missing outcome or race/ethnicity data.

## Consequence

Without temporal outcomes, it is not scientifically valid to calculate discrimination, calibration, threshold metrics, fairness performance, conformal coverage, M4b coverage, confidence intervals, p-values, FDR correction, or the requested original-versus-temporal comparison. No model, threshold, calibration procedure, conformal procedure, or M4b parameter was run, refit, tuned, or changed.

## Required next input

Provide the independently prepared 2021–2023 cohort/outcome file (including `SEQN`, the pre-specified outcome, and `RIDRETH3`) plus its temporal-validation manifest. It may remain read-only outside the temporal-validation output directory; it must be available for read-only evaluation.

