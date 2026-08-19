# Phase 4 Test-Set Protection Audit

**Generated:** 2026-08-19, live, per Part 8 of the Phase 4 execution task. This audit is
performed BEFORE any calibration metric, calibration curve, bootstrap CI, or recalibration
decision is computed.

## State verified at this point

- `data/processed/splits/test_ids.csv` SHA-256 hash confirmed unchanged from the
  Pre-Calibration Closure pass (see `documentation/calibration/phase4_pre_execution_snapshot.md`
  §11: exact match).
- `results/predictions/test_predictions_*.csv` files exist (frozen Phase 3 artifacts, read-only)
  but **have not yet been loaded, read, or referenced by any Phase 4 script** as of this audit.
  Verified: only `src/phase4_common.py` (defines the file-path lambda, does not call it) and
  `src/phase4_01_prediction_input_audit.py` reference `TEST_PREDICTION_FILE`/`load_test_predictions`
  so far -- and that script's *purpose* is itself a data-integrity check (Part 7), not a
  method-selection, binning, or recalibration-fitting operation. Per §6 of the frozen protocol,
  this integrity check (verifying shape/range/no-NaN) is explicitly categorized as "scoring,"
  not "development," the same category already used for Phase 3's one-time discrimination-metric
  test evaluation -- it does not select a calibration method, bin count, or recalibration
  transformation, so it does not consume the "first and only touch" budget reserved for Part 21
  of this task (final calibration metric computation). This distinction is recorded explicitly
  here to avoid ambiguity.

## Explicit confirmation of no unauthorized test-set use

| Prohibited use | Status |
|---|---|
| Calibration-method selection | NOT PERFORMED using test data |
| Calibration fitting (recalibration model fit) | NOT PERFORMED using test data |
| Binning selection (bin count/strategy choice) | NOT PERFORMED using test data -- 10 equal-frequency deciles is a frozen protocol decision (§9), not chosen from test-set inspection |
| Recalibration method selection | NOT PERFORMED using test data |
| Metric selection | NOT PERFORMED using test data -- intercept/slope/Brier (primary), curve/ECE (secondary) are frozen protocol decisions (§7-8) |
| Threshold modification | NOT PERFORMED -- the Youden's J threshold remains the frozen Phase 3 value; Calibration does not touch it |
| Model selection | NOT PERFORMED -- all 5 primary models are carried forward unchanged; no model is dropped or promoted based on any Calibration finding in this phase |

## Rule for the remainder of Phase 4

All primary/secondary calibration metrics, calibration curves, bootstrap confidence intervals,
multiple-comparison correction, and the recalibration-pursue/no-pursue decision will be computed
**exclusively from the OOF (development) tier** (`validation_predictions_*.csv`). The locked test
set (`test_predictions_*.csv`) will be touched exactly once, at Part 21 of this task, for final
confirmatory scoring only, after all upstream Calibration work is frozen and committed (Commit A).

## Result

**TEST-SET PROTECTION: VERIFIED. No contamination found. Safe to proceed.**
