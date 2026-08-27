# Phase 0 repository and lineage audit

**Scope:** Phase 0 audit and Phase 1 reproduction only. No retraining, threshold changes, mitigation, temporal validation, external validation, predictor changes, or outcome changes were performed.

## Frozen-state verification

- Outcome: `LUXSMED >= 8.2 kPa` with valid VCTE/LUAXSTAT, represented as `outcome_primary_8.2kPa`.
- Predictors: Age, Sex, BMI, ALT, AST, Albumin, AlkPhos, Bilirubin, Platelets, HDL.
- Primary cohort: N=7,153.
- Locked split: train N=5,007 and test N=2,146.
- Models: Logistic Regression, Random Forest, XGBoost, LightGBM, MLP.
- Canonical BMI bins and frozen thresholds were read from `src/phase5_common.py`.
- Historical Phase 5 uses raw Phase 3 predictions and frozen thresholds; recalibrated predictions were not substituted.

## Artifact register

| Artifact path | Purpose | Found | Authoritative | SHA-256 | Lineage status | Discrepancy |
|---|---|---|---|---|---|---|
| `data/processed/analysis_dataset_primary.parquet` | Primary CAND_1 cohort and outcome/predictors | YES | YES | `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938` | VERIFIED | None identified |
| `data/processed/splits/train_ids.csv` | Frozen training IDs | YES | YES | `ae5c5124c4d47deb0c256747c591159afa2782304a9c54e29f7105c72e12ecb4` | VERIFIED | None identified |
| `data/processed/splits/test_ids.csv` | Frozen locked-test IDs | YES | YES | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` | VERIFIED | None identified |
| `results/tables/phase2_predictor_registry.csv` | Frozen predictor registry | YES | YES | `9a1a88f756bc1da3f33d1aac55dbe34d00d85842e59e71a7187ff93a688480a3` | VERIFIED | None identified |
| `results/tables/phase3_final_baseline_results.csv` | Frozen baseline thresholds and model metrics | YES | YES | `6c849134f7b3d4b608824087ed05cd3025f390495d0b558d1c1acbf0ce7b0dd6` | VERIFIED | None identified |
| `results/predictions/test_predictions_logistic.csv` | Frozen logistic raw test predictions | YES | YES | `87fa5df55f55ae749e70205eaab0fb6a57b0650e25fa901a824b15ccd1a8cd45` | VERIFIED | None identified |
| `results/predictions/test_predictions_random_forest.csv` | Frozen random_forest raw test predictions | YES | YES | `25088452a18af7c6a88438049fff12b3346db7f9387051245059879bb76f373e` | VERIFIED | None identified |
| `results/predictions/test_predictions_xgboost.csv` | Frozen xgboost raw test predictions | YES | YES | `651ef1bcbbd2f36121a26f52508479349b25b526bc7563bef183efc7f5e57e4a` | VERIFIED | None identified |
| `results/predictions/test_predictions_lightgbm.csv` | Frozen lightgbm raw test predictions | YES | YES | `eb9e7c78a6f3dc1c6854b7b7b6a66be64c0ae4910f7f7b69181d8a13c2d3e1ad` | VERIFIED | None identified |
| `results/predictions/test_predictions_mlp.csv` | Frozen mlp raw test predictions | YES | YES | `a48b0a2d9d6c7c827adbc8e5682f512cf291042d75055c2ec6d33f8395d4bc51` | VERIFIED | None identified |
| `results/calibration/test_set_recalibrated_predictions.csv` | Frozen OOF-Platt recalibrated test predictions | YES | YES | `a945825b6d927c9e7f0194e8b27197ec7aeee959c034ec7a7511ee8e5d250dda` | VERIFIED | None identified |
| `results/fairness/subgroup_discrimination_metrics.csv` | Historical subgroup metrics and counts | YES | YES | `e16b44ea6f9e2a9ac5339e61a1869a68847f328c03e36633fd1b0d00ca58d1a5` | VERIFIED | None identified |
| `results/fairness/fairness_inference.csv` | Historical CIs, raw p-values, BH-FDR q-values | YES | YES | `b7351bd9daf6ee5c26d7f6cf33e0859bbb952e6129c310fd0e291c133c21e132` | VERIFIED | None identified |
| `src/phase5_common.py` | Canonical BMI/age bins, model list, thresholds | YES | YES | `d72236d5bfa1ecb1bd1dcc20d6df25215ece267fe3d787ca4ec694b9f0c1924e` | VERIFIED | None identified |
| `src/phase5_02_subgroup_discrimination.py` | Historical raw-probability subgroup metrics | YES | YES | `d2c7512473fc198f14aceef295cb5184f0c0956ad4f77113b72d4a5b4f3d04ea` | VERIFIED | None identified |
| `src/phase5_04_inference.py` | Historical bootstrap and BH-FDR inference | YES | YES | `ee874db97ab9bebb0b112de314fcab8430ed4080a61615d9d457da385c9bb8c1` | VERIFIED | None identified |
| `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` | Frozen outcome, predictors, fairness dimensions | YES | YES | `8fa176f2b43e91fcf6ad23afd33f25a59625f66afe65817e61db709b7143b801` | VERIFIED | None identified |
| `documentation/phase2/fairness_subgroup_protocol.md` | BMI and age subgroup definitions | YES | YES | `0c1cf80360b10572c003f8a27406a6499d64804f4680b5c038c1ac85aeb9634b` | VERIFIED | None identified |
| `documentation/phase2/fairness_definition.md` | Disparity, CI, and significance rules | YES | YES | `9cd818dcbc99fb6b630efe248e1e1d694f31cea902905052152f0aa64288f68d` | VERIFIED | None identified |

## Reproduction checks

- Primary test join: 2,146 rows and 2,146 unique SEQNs.
- Primary test positives: 200.
- Each model prediction file: 2,146 rows and 2,146 unique SEQNs.
- Each prediction target matched `outcome_primary_8.2kPa` exactly.
- Historical Normal/Obese counts matched exactly; sensitivities, disparities, CIs, raw p-values, and BH-FDR q-values matched the reproduction within the historical file's documented six-decimal/four-decimal rounding.

## Final decision

**PHASE 0 COMPLETE — VERIFIED.** All required dependencies were found and lineage was established. **PHASE 1 COMPLETE — REPRODUCED.** No substantive discrepancy was identified; only representation/rounding differences were present. Phase 2 is safe to begin, but was not executed automatically.

A missing or unverified dependency would have been marked `LINEAGE NOT FOUND`; none occurred for the Phase 0/1 dependency set.
