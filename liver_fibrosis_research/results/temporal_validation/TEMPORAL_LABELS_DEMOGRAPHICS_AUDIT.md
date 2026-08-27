# Temporal labels and demographics audit

## Scope

This task attached only LUX outcome inputs and race/ethnicity to the existing frozen temporal prediction cohort. No Phase 3 evaluation was performed.

## Source files used

- Frozen cohort anchor: `data/processed/temporal_validation/temporal_validation_input_cobas6000_alt.csv` (4,910 prediction-cohort SEQNs).
- LUX source: `NHANES 2021–2023 temporal validation dataset/LUX_L.xpt`; retrieved only `SEQN`, `LUXSMED`, and `LUAXSTAT`.
- DEMO source: `NHANES 2021–2023 temporal validation dataset/DEMO_L.xpt`; retrieved only `SEQN` and `RIDRETH3`.

## Matching and cohort integrity

- Output rows: 4910
- Unique SEQN: 4910
- Duplicate SEQN: 0
- Missing SEQN: 0
- SEQNs matched from LUX_L: 4910
- SEQNs matched from DEMO_L: 4910
- Unmatched LUX_L SEQNs: none
- Unmatched DEMO_L SEQNs: none
- Output SEQNs exactly match the existing 4,910-person temporal prediction cohort: yes.

## Missingness

- Missing `LUXSMED`: 0
- Missing `LUAXSTAT`: 0
- Missing `RIDRETH3`: 0

## Derived outcome

`outcome = 1` where `LUXSMED >= 8.2`; `outcome = 0` where `LUXSMED < 8.2`. No outcome was created where `LUXSMED` is missing.

- Positive outcomes: 563
- Negative outcomes: 4347
- Outcome prevalence among non-missing `LUXSMED`: 0.114664

## Isolation confirmation

The original 4,910-person cohort was not changed or redefined. No predictor, model, or temporal prediction file was modified. The outcome was not used to alter cohort membership. No discrimination, calibration, fairness, conformal, M4b, DCA, or other evaluation was performed.
