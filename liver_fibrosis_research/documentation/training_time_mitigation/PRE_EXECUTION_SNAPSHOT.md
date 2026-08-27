# Pre-execution snapshot — training-time mitigation (Amendment #19)

**Captured:** 2026-08-27T14:20:47Z · **git HEAD:** `16459ae3a958da858917e9b26e050d5ad4106301`
(branch `experiment/training-time-mitigation`, off `consolidation/evidence-freeze` @ Amendment #18)

Inputs consumed by Phases 1–2 (`src/ttm_00`…`ttm_04`). Nothing below is modified by the analysis;
the reweighted models and all Amendment-#19 results are written to new paths
(`models/training_time_mitigation/`, `results/training_time_mitigation/`).

| File | SHA-256 |
|---|---|
| `data/processed/analysis_dataset_primary.parquet` | `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938` |
| `data/processed/splits/train_ids.csv` | `ae5c5124c4d47deb0c256747c591159afa2782304a9c54e29f7105c72e12ecb4` |
| `data/processed/splits/test_ids.csv` | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| `data/processed/splits/proper_train_ids.csv` | `bc29dbe6402ffb82790801a97d6baf26732f6964bf77741a8f716e78dab01fef` |
| `data/processed/splits/conformal_calibration_ids.csv` | `4d696cbcd0f2aecfd07dd7b223825df10c39bbfaf3f093a117e4c224b6c5b3c5` |
| `data/processed/splits/validation_ids.csv` | `ae5c5124c4d47deb0c256747c591159afa2782304a9c54e29f7105c72e12ecb4` |
| `models/phase3/model_logistic_v1.joblib` | `ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5` |
| `models/phase3/model_random_forest_v1.joblib` | `37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a` |
| `models/phase3/model_xgboost_v1.joblib` | `8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4` |
| `models/phase3/model_lightgbm_v1.joblib` | `dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02` |
| `models/phase3/model_mlp_v1.joblib` | `4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc` |
| `results/tables/phase3_final_baseline_results.csv` | `6c849134f7b3d4b608824087ed05cd3025f390495d0b558d1c1acbf0ce7b0dd6` |
| `results/fairness/fairness_inference.csv` | `b7351bd9daf6ee5c26d7f6cf33e0859bbb952e6129c310fd0e291c133c21e132` |
| `results/uncertainty/subgroup_coverage.csv` | `0d2a837d8a82c59f8b652c2deeb0b7072dc546ac5020345d1b227d36653129ad` |
| `results/uncertainty/marginal_coverage_test_set.csv` | `59f778a8465b4b356cf3fb88ba7284a8766fffc486f5746a12e4290d6b7c289c` |
| `results/uncertainty/conformal_thresholds_by_model.csv` | `23909e42f7ed2f514528694e54ee6a253850e6d4517b2aeaec5d8104efbbbdd2` |
| `results/calibration/test_set_calibration_final.csv` | `165df2eea4ba26068787cfc0a15fe7782de576c9d495ca28b6222e4d685ad0ce` |

**Partition / subgroup counts (verified live at snapshot time):**

| partition | N | positives | Normal-BMI (neg / pos) | Obese (neg / pos) | Age-60+ (neg / pos) |
|---|---:|---:|---:|---:|---:|
| training (`train_ids`) | 5,007 | 466 | 1,190 / 50 | 1,715 / 328 | 1,449 / 222 |
| proper-train (`proper_train_ids`) | 4,005 | 373 | 967 / 41 | 1,376 / 260 | 1,151 / 181 |
| conformal-calibration | 1,002 | 93 | 223 / 9 | 339 / 68 | 298 / 41 |
| locked test (`test_ids`) | 2,146 | 200 | 540 / 22 | 743 / 140 | 640 / 101 |

BMI categories: `Normal, Obese, Overweight, Underweight`. Age categories: `18-39, 40-59, 60+`.
Zero missing `bmi_group_final` / `age_group_final` in the training partition.

**Leakage pre-check (asserted in `ttm_03` and `ttm_04`):**
`test_ids ∩ train_ids = ∅`, `test_ids ∩ proper_train_ids = ∅`, `test_ids ∩
conformal_calibration_ids = ∅`.

**Frozen conformal parameters:** calibration N = 1,002 (93 positive); α = 0.10;
`k = ⌈(1002 + 1)(0.90)⌉ = 903`; nonconformity `s = 1 − P̂(y = true class | x)`.

**Environment (operator, for Phases 1–2):** `requirements-phase3-lock.txt` — Python 3, pandas,
numpy, scipy, scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0, imbalanced-learn 0.14.2, joblib.
Plan-authoring environment: pandas / numpy / scipy only (no sklearn / xgboost / lightgbm).
