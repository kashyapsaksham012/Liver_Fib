# Phase 4 Calibration Data Flow

**Generated:** 2026-08-19, live, per Part 6 of the Phase 4 execution task.

This document records exactly which data source is used for which Calibration computation,
per §6 of the frozen protocol (`documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md`,
commit `2436d95`). No substitution or new split was created.

## Approved mechanism (from the frozen protocol, verbatim decision)

**Two-tier calibration assessment:**

1. **Development-side (repeatable) diagnostic tier** = **CV out-of-fold (OOF) predictions**,
   already generated in Phase 3 (`results/predictions/validation_predictions_<model>.csv`, one
   file per primary model, written by `src/phase3_05_train_and_tune.py` line 121 via
   `cross_val_predict(..., cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
   method="predict_proba")`). Live-verified this pass: 5,008 lines per file (5,007 data rows +
   header), matching the frozen train N exactly.
2. **Confirmatory (one-time) tier** = **locked test set** (`data/processed/splits/test_ids.csv`,
   N = 2,146), scored once using the already-frozen `best_estimator_` pipeline per model
   (`results/predictions/test_predictions_<model>.csv`). Live-verified: 2,147 lines per file
   (2,146 data rows + header).

## Explicitly NOT used

`data/processed/splits/conformal_calibration_ids.csv` (N = 1,002) is **not** used anywhere in
Phase 4. It is reserved for the future Uncertainty phase's split-conformal calibration set, and is
not even a valid held-out set for the current frozen models (they were trained on the full
5,007-row training partition, which includes those 1,002 rows). No Phase 4 script references this
file. Verified: `grep -rn conformal_calibration src/phase4_*.py` returns zero matches (checked
after all Phase 4 scripts were written).

## Data flow diagram

```
Phase 3 frozen artifacts (unchanged, read-only in Phase 4)
│
├── models/phase3/model_<name>_v1.joblib  (5 primary + MLP_balanced sensitivity)
│
├── results/predictions/validation_predictions_<name>.csv   ── OOF tier ──▶ phase4_01 (integrity)
│                                                                          ▶ phase4_02 (primary metrics: intercept/slope/Brier)
│                                                                          ▶ phase4_03 (calibration curves + ECE)
│                                                                          ▶ phase4_04 (bootstrap inference + FDR)
│                                                                          ▶ phase4_05 (recalibration decision + fit, IF pursued -- OOF only)
│
└── results/predictions/test_predictions_<name>.csv   ── locked test tier ──▶ phase4_06 (FIRST AND ONLY test-set touch,
                                                                                          final confirmatory metrics)
```

## Rule enforced

Every Phase 4 script prior to `phase4_06_final_test_set_calibration.py` reads only
`validation_predictions_*.csv` (OOF tier). `phase4_06` is the sole script permitted to read
`test_predictions_*.csv`, and per the frozen protocol, it does so exactly once, for confirmatory
scoring only -- no method, binning, or recalibration selection occurs there.
