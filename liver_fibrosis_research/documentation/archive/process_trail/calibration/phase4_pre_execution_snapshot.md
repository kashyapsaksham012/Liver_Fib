# Phase 4 (Calibration) — Pre-Execution Snapshot

**Timestamp (live, local machine clock):** 2026-08-19 10:26:55 +0530

This snapshot is recorded before any Calibration computation runs, per Part 1 of the Phase 4
execution task. It does not overwrite any earlier snapshot (none existed under this filename).

## 1-3. Git state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `1fc309f7a9ee9165382645d23af8aa75c3841963` |
| Working tree | Clean (0 uncommitted, 0 untracked) |
| Upstream | `origin/main`, up to date (confirmed via `git status`) |

## 4-5. Calibration protocol commit and checksum

| Field | Value |
|---|---|
| Protocol commit (live-verified via `git log --all -- CALIBRATION_PROTOCOL_FREEZE.md`) | `2436d9554647c65af43e7d8cc61cdfeed9fb9a6a` |
| Protocol file current checksum (SHA-256) | `3c843ad02cd91736a597ad3256a6c6309ffac2819a882c72f77b9220c64fca1d` |
| Matches value recorded at commit time in `calibration_protocol_commit_record.md`? | YES (identical) |
| `git diff 2436d95 -- CALIBRATION_PROTOCOL_FREEZE.md` | Empty (file unchanged since that commit) |

**Correction to the task prompt's claimed status:** the prompt asserts "Human test-set spot-check:
COMPLETED and recorded." Live inspection of
`documentation/end_to_end/human_spot_check_record_template.md` shows all fields still contain the
placeholder `_____` — it has **not** actually been filled in by a human. This is disclosed here
rather than silently accepted. Per the prior closure report's own rule, this does not block
Calibration execution (the accepted status was explicitly "READY FOR CALIBRATION — HUMAN
SPOT-CHECK PENDING"), so execution proceeds, but the claim of completion is factually incorrect
and is not repeated as true anywhere in this Phase 4 work.

## 6-8. Environment

| Field | Value |
|---|---|
| Python version | 3.14.3 |
| scikit-learn | 1.9.0 |
| xgboost | 3.4.1 |
| lightgbm | 4.7.0 |
| numpy | 2.5.2 |
| pandas | 3.0.5 |
| scipy | 1.18.0 |
| joblib | 1.5.3 |

Matches `requirements-phase3-lock.txt` exactly (live `pip`-equivalent import check performed, not
merely read from the lock file).

## 9. Frozen Phase 3 model artifact hashes (SHA-256, live-computed)

| Model | File | SHA-256 |
|---|---|---|
| Logistic Regression | `models/phase3/model_logistic_v1.joblib` | `ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5` |
| Random Forest | `models/phase3/model_random_forest_v1.joblib` | `37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a` |
| XGBoost | `models/phase3/model_xgboost_v1.joblib` | `8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4` |
| LightGBM | `models/phase3/model_lightgbm_v1.joblib` | `dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02` |
| MLP (original) | `models/phase3/model_mlp_v1.joblib` | `4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc` |
| MLP (balanced, sensitivity only) | `models/phase3/model_mlp_balanced_v1_sensitivity.joblib` | `d89a49e31e401493dd7c1ec8234cf823c386ac518edf9d475a872c6779b5bb9d` |

No prior expected-hash record exists to compare against (these are being hashed for the first
time as a Phase 4 artifact) — this snapshot establishes the baseline that Phase 4's own
reproducibility rerun (Part 31) will be checked against.

## 10. Phase 3 prediction file hashes (SHA-256, live-computed)

The 5 primary models' out-of-fold (`validation_predictions_*.csv`) and locked-test-set
(`test_predictions_*.csv`) prediction files:

| File | SHA-256 |
|---|---|
| `validation_predictions_logistic.csv` | `f283f1b5ee390973e2d43a7b8bed4562f1f5a9fc0acbae8c41c6acc57ef3f691` |
| `validation_predictions_random_forest.csv` | `ae446e55cd31f3d3f8f89205d1fcdd158d4e6680a1c98e383bebcc82fdaab723` |
| `validation_predictions_xgboost.csv` | `4cfa72d64ef4f6f52c0466935646335f209c17eee3488dc1dfa2f73dc9b89abd` |
| `validation_predictions_lightgbm.csv` | `99496e2270f669942dff18f5c95a49f4b67060fe669e240f7e4c6eb4351bfc5a` |
| `validation_predictions_mlp.csv` | `b9fe782e60f2db84f1a1e4dadf38c23672d5903b392b01a0b206f2e9bee63f84` |
| `test_predictions_logistic.csv` | `87fa5df55f55ae749e70205eaab0fb6a57b0650e25fa901a824b15ccd1a8cd45` |
| `test_predictions_random_forest.csv` | `25088452a18af7c6a88438049fff12b3346db7f9387051245059879bb76f373e` |
| `test_predictions_xgboost.csv` | `651ef1bcbbd2f36121a26f52508479349b25b526bc7563bef183efc7f5e57e4a` |
| `test_predictions_lightgbm.csv` | `eb9e7c78a6f3dc1c6854b7b7b6a66be64c0ae4910f7f7b69181d8a13c2d3e1ad` |
| `test_predictions_mlp.csv` | `a48b0a2d9d6c7c827adbc8e5682f512cf291042d75055c2ec6d33f8395d4bc51` |

Row counts confirmed live: `validation_predictions_*.csv` = 5,008 lines (5,007 data + 1 header,
matching the frozen train N); `test_predictions_*.csv` = 2,147 lines (2,146 data + 1 header,
matching the frozen test N). Source confirmed by `grep`: `validation_predictions_<model>.csv`
is written by `src/phase3_05_train_and_tune.py` line 121 from `cross_val_predict(...,
method="predict_proba", cv=StratifiedKFold(5-fold))` — genuine 5-fold CV out-of-fold predictions,
not a separate holdout partition.

## 11. Frozen test-set hash

| Field | Value |
|---|---|
| File | `data/processed/splits/test_ids.csv` |
| SHA-256 (live-computed now) | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| Previously recorded value (`human_spot_check.md`, Pre-Calibration Closure pass) | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| Match? | **YES — exact match.** No integrity failure. Test set is unchanged since the Pre-Calibration Closure pass. |

## 12. Execution timestamp

2026-08-19 10:26:55 +0530 (recorded above; all subsequent Phase 4 steps proceed from this point).
