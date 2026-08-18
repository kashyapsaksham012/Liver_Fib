# Research Pipeline Dependency Graph

**Generated:** 2026-08-18 (end-to-end Phase 1→3 audit) — traced from actual `import`/file-read
statements in the source scripts, not asserted from memory.

## Phase 1 → Phase 2 consumption

| Phase 1 artifact | Consumed by (Phase 2 script) | Verified |
|---|---|---|
| `data/interim/nhanes_master_phase1.parquet` | `phase2_01_candidate_cohorts.py`, `phase2_02...py`, `phase2_04_build_analysis_dataset.py` (all `pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")`) | Yes — direct read confirmed by grep |
| `src/_cohorts.py` (canonical cohort defs) | `from _cohorts import compute_all` in every `phase2_0*.py` | Yes |
| `documentation/audit_reports/preliminary_leakage_audit.csv` | `phase2_02_outcome_predictors_leakage.py` (`read_csv_safe(AUDIT_DIR / "preliminary_leakage_audit.csv")`) | Yes |

## Phase 2 → Phase 3 consumption

| Phase 2 artifact | Consumed by (Phase 3 script) | Verified |
|---|---|---|
| `data/processed/analysis_dataset_primary.parquet` | `phase3_01_handoff_verification.py`, `phase3_02...py`, `phase3_03_split_and_lock.py`, `phase3_05_train_and_tune.py`, `phase3_06...py` (all read this file directly) | Yes |
| `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` (frozen predictor list, N=7,153, threshold=8.2kPa) | Hardcoded as constants in `src/phase3_common.py` (`PRIMARY_COHORT_N`, `PRIMARY_OUTCOME_COL`, `PRIMARY_PREDICTORS`) — **not read programmatically at runtime, but manually transcribed and then independently re-verified against Phase 1 raw data in `phase3_01_handoff_verification.py`** | Yes, with the caveat noted |
| `documentation/phase2/uncertainty_protocol.md` (Split Conformal Prediction, 80/20 example) | `src/phase3_21_reserve_conformal_calibration_split.py` (`CALIBRATION_FRACTION = 0.20`, comment cites the doc) | Yes |
| `documentation/phase2/model_development_protocol.md` (5-fold CV, 70/30 split, retain-all-models rule) | `src/phase3_common.py` (`N_CV_FOLDS = 5`, `TRAIN_FRACTION = 0.70`), `downstream_model_retention_rule.md` (quotes the doc directly) | Yes |

**Caveat on the second row:** `phase3_common.py`'s constants are manually transcribed from the
Phase 2 freeze document rather than parsed from it programmatically. This is a real, if minor,
traceability gap — a typo in transcription would not be caught by any automated dependency check.
It is partially mitigated by `phase3_01_handoff_verification.py`, which independently
*recomputes* N=7,153/positive=666 from the Phase 1 raw master data and asserts equality, so a
transcription error in the *cohort size* would be caught; a transcription error in, say, the
exact predictor variable *names* would only be caught by the separate `phase3_02` whitelist
check against `_common.VAR_METADATA`, not by re-deriving the list from the Phase 2 document text
itself.

## Phase 3 internal chain

`phase3_03_split_and_lock.py` (writes `train_ids.csv`/`test_ids.csv`) → `phase3_05_train_and_tune.py`
(reads `train_ids.csv` only) → `phase3_06_threshold_and_test_eval.py` (reads `train`-derived OOF
predictions, then `test_ids.csv` last) → `phase3_07_plots_and_comparison.py` (reads
`test_predictions_*.csv`) → `phase3_09`/`phase3_20_generate_*_report.py` (reads all result tables).

## Orphan files (exist but are not consumed downstream, as of this audit)

- `data/processed/splits/validation_ids.csv` — legacy alias, superseded by
  `cv_fold_assignment_ids.csv`; neither is read by any Phase 3 script (CV folds are generated
  fresh from `train_ids.csv` at runtime, not read from either file). **This is expected, not a
  bug** — both files exist for documentation/deliverable-completeness purposes, not as a runtime
  dependency.
- `data/processed/splits/proper_train_ids.csv` / `conformal_calibration_ids.csv` — reserved for
  the future Uncertainty phase; not consumed by any current script (correctly — that phase hasn't
  started).

## Unauthorized dependencies found

**None.** No Phase 3 script reads any file outside the Phase 1/2 artifact set listed above plus
its own Phase 3 intermediate outputs.
