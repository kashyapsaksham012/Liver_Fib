# Phase 5 MI Conformal Reliability Sensitivity Analysis

## Final conclusion

MI CONFORMAL RELIABILITY IS CONSISTENT WITH COMPLETE-CASE RESULTS

## Scope and lineage gate

The authoritative repository was `/Users/sakshamkashyap/Desktop/Research /liver_fibrosis_research`. The MI lineage gate passed before any locked-test access. The committed lineage is MI Commits B/C/D (`4802602`, `f73ef91`, `adc9328`), with five registered datasets, seeds 42–46, and distinct on-disk hashes. The existing static MI CSVs were used as lineage/diagnostic evidence; they were not used as prediction inputs because their construction is explicitly full-pool diagnostic-only. The conformal sensitivity refit instead embedded the authorized `IterativeImputer(BayesianRidge, max_iter=10, sample_posterior=True)` in the model pipeline and fit it only on each expanded proper-training partition.

Protocol: five MI datasets; ten frozen primary predictors; outcome excluded from imputation; frozen Phase 3 best hyperparameters and five model families; fixed proper-train/conformal-calibration/test partition structure; standard split conformal score `1 - P(true class)`; finite-sample corrected 90% threshold; Wilson 95% coverage intervals; exact Phase 5 subgroup bins and 26 pre-specified intersectional cells. No inferential pooling was invented. Every MI dataset/model result is reported separately; means, ranges, and SDs are descriptive between-imputation summaries only.

The expanded MI proper-training set contains 4,620 participants (4,005 original proper-train plus 615 complete-case-excluded participants); calibration remains 1,002 and the locked test remains 2,146. Complete-case values are read from frozen Phase 6 outputs rather than recomputed.

## Results

### Overall test-set reliability

| Model | MI coverage range | Descriptive MI mean | Frozen complete-case coverage | MI mean − CC | MI mean set size |
|---|---:|---:|---:|---:|---:|
| lightgbm | 0.8891–0.8993 | 0.8956 | 0.8961 | -0.05 pp | 1.3274 |
| logistic | 0.9059–0.9110 | 0.9087 | 0.9082 | +0.05 pp | 1.4518 |
| mlp | 0.8896–0.8998 | 0.8945 | 0.8919 | +0.26 pp | 0.9736 |
| random_forest | 0.8844–0.8966 | 0.8908 | 0.8961 | -0.53 pp | 1.2209 |
| xgboost | 0.8858–0.8961 | 0.8909 | 0.8812 | +0.97 pp | 1.3006 |

The complete-case reference and exact MI-minus-complete-case values are available in `phase5_mi_vs_complete_case.csv`; the table above deliberately avoids implying a pooled MI estimate. Across models, descriptive mean coverage changes were small to moderate (approximately −0.53 to +0.97 percentage points, model-dependent), while all five imputations remain visible in the machine-readable outputs.

### Subgroup and intersectional reliability

BMI-Obese coverage remained below the 90% nominal target in every model and every imputation (ranges: lightgbm 0.777–0.800; logistic 0.819–0.828; mlp 0.798–0.824; random_forest 0.777–0.801; xgboost 0.776–0.797). Non-Hispanic Black coverage was reported separately for all imputations (ranges: lightgbm 0.871–0.891; logistic 0.891–0.898; mlp 0.882–0.895; random_forest 0.871–0.882; xgboost 0.873–0.884). These are coverage observations, not claims of conditional conformal validity or causal explanations. The 26 pre-specified Sex×Race/Ethnicity, Sex×Age, and Sex×BMI cells are retained without pooling or post-hoc cell creation.

## Locked-test protection and evaluation count

`phase5_mi_selection_manifest.json` was written before opening `test_ids.csv`. The manifest froze model/protocol/threshold-selection rules and recorded the expected locked-test SHA-256. Exactly one official test evaluation was then performed in a single run across the five MI datasets and five frozen models. The live test-set hash matched the expected frozen value. No subsequent analysis step reopened the raw test set; figures and summaries read saved Phase 5 outputs.

## Limitations

This is an exploratory missing-data/conformal sensitivity analysis, not a replacement for the primary complete-case analysis. Split conformal guarantees are marginal and exchangeability-based; subgroup coverage is descriptive and precision-limited in small cells. The authorized MI protocol does not define Rubin-style pooling for these prediction-set outputs, so no pooled inferential estimate is reported. Test-set evaluation was intentionally not repeated.

## Output inventory

- `results/fairness_bmi_investigation/phase5_mi_conformal/phase5_mi_conformal_overall.csv`
- `results/fairness_bmi_investigation/phase5_mi_conformal/phase5_mi_conformal_subgroups.csv`
- `results/fairness_bmi_investigation/phase5_mi_conformal/phase5_mi_vs_complete_case.csv`
- `results/fairness_bmi_investigation/phase5_mi_conformal/phase5_mi_intersectional.csv`
- `results/fairness_bmi_investigation/phase5_mi_conformal/phase5_mi_uncertainty.csv`
- `results/fairness_bmi_investigation/phase5_mi_conformal/phase5_mi_lineage.json`
- `results/fairness_bmi_investigation/phase5_mi_conformal/phase5_mi_selection_manifest.json`
- `results/fairness_bmi_investigation/phase5_mi_conformal_figures/phase5_mi_coverage_<model>.png`

## Key lineage hashes

- `data/processed/analysis_dataset_primary.parquet`: `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938`
- `data/processed/splits/conformal_calibration_ids.csv`: `4d696cbcd0f2aecfd07dd7b223825df10c39bbfaf3f093a117e4c224b6c5b3c5`
- `data/processed/splits/proper_train_ids.csv`: `bc29dbe6402ffb82790801a97d6baf26732f6964bf77741a8f716e78dab01fef`
- `documentation/phase2/missing_data_protocol.md`: `8bdd17a9a18c18f8a1202c53f6aa33115e860fcda0e7c289824beee600ac8b49`
- `documentation/phase2/sensitivity_analysis_plan.md`: `0110c749578212022305ba1abcbb279c3256d35f269ad2e0ddff08709984606b`
- `documentation/phase2/uncertainty_protocol.md`: `9983ad3c1604c2a2f43ecfc6afcf876d0ef8a5acc17ff0b9923011323869f7d7`
- `results/sensitivity/mi_imputed_dataset_0.csv`: `74509ff3648f74d5a21ffd234c5426c45b5ec0fe34e066d0d64f339567d67a9e`
- `results/sensitivity/mi_imputed_dataset_1.csv`: `14d3c44c21fd7b3405e12ef06de0341d19488534027e36f481ba72c1d4402508`
- `results/sensitivity/mi_imputed_dataset_2.csv`: `841efe8d164a9292f7e64142ca0af80cad4dabde9115b0c475d568bb02d86e86`
- `results/sensitivity/mi_imputed_dataset_3.csv`: `5a4289204910ddc5e1eb110415e931140ef4badd988a08a23087cf9e9294feb8`
- `results/sensitivity/mi_imputed_dataset_4.csv`: `361533d2013dba4f60b3306f9f528c19b4e62fdbb7f3576f1e584d1d149e0b81`
- `results/sensitivity/multiple_imputation_diagnostics.csv`: `0262de06c672a79bc745cc589c7cc11d071bac7b57a30e6bd974e7ac8e56157a`
- `results/sensitivity/multiple_imputation_registry.csv`: `8d57c1b5b6417df5a3361d919bac8316fd4f19a189db08ecda5a6317fda3fe30`
- `results/tables/model_lineage.csv`: `32a8a8960e9ed37fb689ec30c0f90cc42f2ea1e8b664156d4474a5c1ac2fd02f`
- `results/uncertainty/conformal_model_refit_registry.csv`: `956b90ae5779f6328caed17aaa1cb4447982dcf4d534ed7712d4dbdefc8cf9c3`
- `results/uncertainty/conformal_thresholds_by_model.csv`: `23909e42f7ed2f514528694e54ee6a253850e6d4517b2aeaec5d8104efbbbdd2`
- `src/mi_01_construct_and_diagnostics.py`: `70f5143b7eca6580fc9ec5bb18fec9ec75804a37b5a954a44a40902bec71cd03`
- `src/mi_02_black_subgroup_comparison.py`: `25c08fa123d36a7586affbf3c061acb1b75b0c82ab404c672315896999274441`
- `src/mi_03_black_subgroup_inference.py`: `f987b308bd8a0c1cd12ab2f7b9efe5909b09ff7e0341991f8aea09b5e2fd452f`
- `models/phase3/model_logistic_v1.joblib`: `ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5`
- `models/phase3/model_random_forest_v1.joblib`: `37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a`
- `models/phase3/model_xgboost_v1.joblib`: `8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4`
- `models/phase3/model_lightgbm_v1.joblib`: `dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02`
- `models/phase3/model_mlp_v1.joblib`: `4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc`
- `models/phase6_conformal_refit/model_logistic_proper_train_refit.joblib`: `000e51505e76d49ebf02a57d29a3132ea1fa837b49497e142c9fd8caeb73c630`
- `models/phase6_conformal_refit/model_random_forest_proper_train_refit.joblib`: `22a63c50c43b6aef4834223c4b27c03a811dd8881e770cfaea2437d946d32618`
- `models/phase6_conformal_refit/model_xgboost_proper_train_refit.joblib`: `9e7745d64f3b967a06cb053b2dfea9e0950075e5c788aecb6a1c3b245d83dfc8`
- `models/phase6_conformal_refit/model_lightgbm_proper_train_refit.joblib`: `597ad772bf68ef6a1022d6b44ef3039c90220ae614a0f11ec015a23c59fa0856`
- `models/phase6_conformal_refit/model_mlp_proper_train_refit.joblib`: `5bd9a684357c6069b71163c46865d0358745154b813d947627acef5ecca79cb3`
- Locked test set: `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779`
- Phase 5 output hashes and figure hashes: recorded in `phase5_mi_lineage.json`.

MI ROBUSTNESS PARTIAL
