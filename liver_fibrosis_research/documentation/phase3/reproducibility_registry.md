# Reproducibility Registry

**Generated:** 2026-08-18 (Phase 3, Parts 30 & 32)

## Full Configuration Record

- **Code version (git commit at Phase 3 start):** `b390fbeeda3dd85fcc20420dbd486990734bd418`
- **Data version:** `data/interim/nhanes_master_phase1.parquet` SHA-256 =
  `150f7ff896e5ae963f95dfa53b23ffc4ade3cff1c6e2d1306c9e23ead99653b1` (unchanged since Phase 1 freeze);
  `data/processed/analysis_dataset_primary.parquet` SHA-256 =
  `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938` (unchanged since Phase 2 freeze)
- **Protocol version:** `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`, zero amendments
- **Random seed:** `RANDOM_SEED = 42` (fixed for train/test split, CV fold assignment, and all
  stochastic model components), recorded in `src/phase3_common.py` and `phase3_pre_modeling_snapshot.md`
- **Package versions:** scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0, pandas 3.0.5, numpy 2.5.2,
  scipy 1.18.0, joblib 1.5.3 (project-local `.venv/`, `requirements-phase3.txt`)
- **Model hyperparameters:** frozen per model in `results/tables/phase3_model_registry.csv`
  (`best_hyperparameters` column, JSON-encoded)
- **Split IDs:** `data/processed/splits/{train,validation,test}_ids.csv`, immutable once written
- **Preprocessing configuration:** `ColumnTransformer` + `Pipeline` per model (median-impute no-op +
  `StandardScaler` for Logistic Regression/MLP; no scaling for tree models), fit exclusively within each
  CV fold / on the training partition — see `src/phase3_05_train_and_tune.py::build_pipeline`
- **Execution time:** training+tuning ~49s (5 models, 84 evaluated hyperparameter configurations
  combined), threshold+test evaluation <5s, on Apple Silicon (arm64), 2026-08-18

## Independent Reproduction (Phase 3, Part 32)

**Procedure:** After the main Phase 3 execution, the original `phase3_model_registry.csv`,
`phase3_overall_discrimination.csv`, and `phase3_threshold_selection.csv` were copied aside. The training
(`phase3_05_train_and_tune.py`) and threshold/test-evaluation (`phase3_06_threshold_and_test_eval.py`)
scripts were then re-run from a clean invocation (same frozen protocol, same frozen data, same fixed
seed, same code, same environment) and the regenerated files were diffed against the saved originals.

**Result: EXACT reproduction.**

| Artifact | Comparison | Result |
|---|---|---|
| `phase3_model_registry.csv` | Full diff | Identical on every scientific column (hyperparameters, CV ROC-AUC, class-imbalance handling, preprocessing spec); only `training_time_sec` (wall-clock) differed, as expected for a non-scientific timing measurement |
| `phase3_overall_discrimination.csv` | Full diff | **Byte-for-byte identical** (ROC-AUC, PR-AUC, bootstrap CIs, sensitivity, specificity, PPV, NPV, F1, confusion-matrix counts — all 5 models) |
| `phase3_threshold_selection.csv` | Full diff | **Byte-for-byte identical** (Youden threshold, all 5 models) |

No unexplained discrepancy was found; the two scientific-value differences that could have appeared under
nondeterministic multi-threaded execution (XGBoost/LightGBM with `n_jobs=-1`) did not occur in this run —
this pipeline is confirmed exactly reproducible under the frozen seed/environment, and no result was
dismissed as "random" without this direct verification.

## Reproduction Instructions (for an independent party)

```bash
cd liver_fibrosis_research
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-phase3.txt
python3 src/phase3_01_handoff_verification.py
python3 src/phase3_02_target_and_features.py
python3 src/phase3_03_split_and_lock.py
python3 src/phase3_04_missingness_and_imbalance.py
python3 src/phase3_05_train_and_tune.py
python3 src/phase3_06_threshold_and_test_eval.py
python3 src/phase3_07_plots_and_comparison.py
python3 src/phase3_08_validation_tests.py
```

Running this sequence reproduces every table, figure, and prediction file in this report exactly (see
above), given the same frozen `data/processed/analysis_dataset_primary.parquet` and split files.
