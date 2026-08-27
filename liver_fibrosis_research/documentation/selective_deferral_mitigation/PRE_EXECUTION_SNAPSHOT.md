# Pre-execution snapshot — selective-deferral mitigation

**Captured:** 2026-08-27T10:13:43Z · **git HEAD:** `e5b773f0f0d79e97c1ada08f886fbefc9881ba25`

Frozen inputs this analysis consumes (SHA-256). Nothing below is modified by the analysis.

| File | SHA-256 |
|---|---|
| `data/processed/splits/conformal_calibration_ids.csv` | `4d696cbcd0f2aecfd07dd7b223825df10c39bbfaf3f093a117e4c224b6c5b3c5` |
| `data/processed/splits/proper_train_ids.csv` | `bc29dbe6402ffb82790801a97d6baf26732f6964bf77741a8f716e78dab01fef` |
| `data/processed/splits/test_ids.csv` | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| `data/processed/analysis_dataset_primary.parquet` | `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938` |
| `results/uncertainty/test_set_prediction_sets.csv` | `527969c3529389d3e857e4e86e66e0aab06cc5e5784e73a48d471f155f175506` |
| `results/uncertainty/conformal_thresholds_by_model.csv` | `23909e42f7ed2f514528694e54ee6a253850e6d4517b2aeaec5d8104efbbbdd2` |
| `results/uncertainty/calibration_scores_{logistic,random_forest,xgboost,lightgbm,mlp}.csv` | per-file, recorded in the Phase 1–2 report |

Cross-check: the `conformal_calibration_ids.csv` hash matches
`results/uncertainty/phase6_partition_audit.csv` (`4d696cbc…`) — the genuine frozen Phase-6
calibration partition.

Frozen conformal parameters (from `conformal_thresholds_by_model.csv`): calibration N = 1,002
(93 positive / 909 negative); α = 0.10; finite-sample quantile level 0.901198; score =
`1 − P̂(y = true class | x)`. Per-model nonconformity thresholds: logistic 0.672744,
random_forest 0.607211, xgboost 0.653193, lightgbm (from file), mlp (from file).

Environment: Python 3, pandas 3.0.5, numpy, scipy available; **joblib / scikit-learn / xgboost /
lightgbm NOT available** — models are not loaded; the analysis uses cached predictions and
nonconformity scores only.
