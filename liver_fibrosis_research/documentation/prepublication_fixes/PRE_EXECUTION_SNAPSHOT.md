# Pre-execution snapshot — pre-publication fixes (Amendment #18)

**Captured:** 2026-08-27T13:11:41Z · **git HEAD:** `3f1fefcb5370481d8529ff13b7ee166abb5edc1a`

Inputs consumed by `src/prepub_01_model_fit_alignment.py` (Phase 1) and
`src/prepub_02_vcte_bias_sensitivity.py` (Phase 2). Nothing below is modified by the analyses.

| File | SHA-256 |
|---|---|
| `data/processed/analysis_dataset_primary.parquet` | `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938` |
| `data/processed/splits/test_ids.csv` | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| `data/processed/splits/conformal_calibration_ids.csv` | `4d696cbcd0f2aecfd07dd7b223825df10c39bbfaf3f093a117e4c224b6c5b3c5` |
| `data/processed/splits/proper_train_ids.csv` | `bc29dbe6402ffb82790801a97d6baf26732f6964bf77741a8f716e78dab01fef` |
| `results/predictions/test_predictions_logistic.csv` | `87fa5df55f55ae749e70205eaab0fb6a57b0650e25fa901a824b15ccd1a8cd45` |
| `results/predictions/test_predictions_random_forest.csv` | `25088452a18af7c6a88438049fff12b3346db7f9387051245059879bb76f373e` |
| `results/predictions/test_predictions_xgboost.csv` | `651ef1bcbbd2f36121a26f52508479349b25b526bc7563bef183efc7f5e57e4a` |
| `results/predictions/test_predictions_lightgbm.csv` | `eb9e7c78a6f3dc1c6854b7b7b6a66be64c0ae4910f7f7b69181d8a13c2d3e1ad` |
| `results/predictions/test_predictions_mlp.csv` | `a48b0a2d9d6c7c827adbc8e5682f512cf291042d75055c2ec6d33f8395d4bc51` |
| `results/uncertainty/test_set_prediction_sets.csv` | `527969c3529389d3e857e4e86e66e0aab06cc5e5784e73a48d471f155f175506` |
| `results/uncertainty/conformal_thresholds_by_model.csv` | `23909e42f7ed2f514528694e54ee6a253850e6d4517b2aeaec5d8104efbbbdd2` |
| `results/uncertainty/calibration_scores_logistic.csv` | `0242fbbe5b3b170119175f57bd7897ea865aae3e0ceff4d775d0e1efc2948834` |
| `results/uncertainty/calibration_scores_random_forest.csv` | `70ef55a3b24e8271a15521ddcafd622db29296ec5da3f7dce5a9ae9e189f1075` |
| `results/uncertainty/calibration_scores_xgboost.csv` | `4ff795482c3a9de8b8861090738044604d7b1e77eeca7e8047dba7033fe8e5b6` |
| `results/uncertainty/calibration_scores_lightgbm.csv` | `8afaf2f73799dcb75283a14bc8960b16a7cbf4a4b23c4b9ff8ac10969f97ac76` |
| `results/uncertainty/calibration_scores_mlp.csv` | `a3ae680ccd15459a1d90961ecb7a4714ed8ed9825e44c14d09da97454c300b2c` |
| `results/fairness/fairness_inference.csv` | `b7351bd9daf6ee5c26d7f6cf33e0859bbb952e6129c310fd0e291c133c21e132` |
| `results/uncertainty/subgroup_coverage.csv` | `0d2a837d8a82c59f8b652c2deeb0b7072dc546ac5020345d1b227d36653129ad` |
| `results/sensitivity/secondary_severity_outcomes_9p7_bmi_age_fairness.csv` | `4b856cfb12f64c404a0682e536e306b3ac9209d8e3c896c39366c9d5fd2b41fd` |

**Leakage pre-check (asserted in the Phase-1 script):**
`test_ids ∩ conformal_calibration_ids = ∅`; `test_ids ∩ proper_train_ids = ∅`
(both already PASS in `results/uncertainty/phase6_partition_audit.csv`).

**Frozen conformal parameters** (from `conformal_thresholds_by_model.csv`): calibration N = 1,002
(93 positive / 909 negative); α = 0.10; finite-sample quantile level 0.901198; nonconformity
score `1 − P̂(y = true class | x)`. Per-model thresholds: logistic 0.672744, random_forest
0.607211, xgboost 0.653193, lightgbm and mlp from file.

**Frozen §3.4 operating thresholds** (Youden's J on OOF, Phase-3 full-train): logistic 0.5173,
random_forest 0.4499, xgboost 0.4108, lightgbm 0.4988, mlp 0.1065 — carried in
`test_predictions_{model}.csv` column `threshold_used`.

**Environment:** Python 3, pandas 3.0.5, numpy, scipy. joblib / scikit-learn / xgboost / lightgbm
NOT available.
