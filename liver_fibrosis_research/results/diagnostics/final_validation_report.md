# Final Validation Report

**Generated:** 2026-08-25 17:46:18  
**Python version:** 3.14.3 (main, Feb  3 2026, 15:32:20) [Clang 17.0.0 (clang-1700.6.3.2)]  

## Summary

| Status | Count |
|---|---|
| ✅ PASS | 26 |
| ⚠️ WARN | 0 |
| ❌ FAIL | 0 |

## All Checks

| Check | Status | Detail |
|---|---|---|
| proper_train ∩ cal == empty | ✅ PASS | Overlap = 0 |
| proper_train ∪ cal == train | ✅ PASS | |union|=5007 |train|=5007 → MATCH |
| test ∩ train == empty | ✅ PASS | Overlap = 0 |
| test ∩ cal == empty | ✅ PASS | Overlap = 0 |
| Split size: proper_train | ✅ PASS | n=4005 |
| Split size: cal | ✅ PASS | n=1002 |
| Split size: test | ✅ PASS | n=2146 |
| Split size: train (=proper+cal) | ✅ PASS | n=5007 |
| File exists: phase3_final_baseline_results.csv | ✅ PASS | SHA256: 6c849134f7b3... |
| File exists: fairness_inference.csv | ✅ PASS | SHA256: b7351bd9daf6... |
| File exists: conformal_thresholds_by_model.csv | ✅ PASS | SHA256: 23909e42f7ed... |
| File exists: test_set_recalibrated_predictions.csv | ✅ PASS | SHA256: a945825b6d92... |
| XGBoost AUC reproducibility | ✅ PASS | Fresh raw AUC=0.8397 vs frozen recal AUC=0.8429 (diff=0.0032) |
| Baseline AUC vs reconstruction | ✅ PASS | Reported (test_roc_auc)=0.8429 fresh=0.8397 diff=0.0032 |
| Test-label flag in sens_04_continuous_splines.py | ✅ PASS | Label-usage documented |
| Test-label flag in sens_05_subgroup_recalibration.py | ✅ PASS | Label-usage documented |
| Test-label flag in sens_06_group_specific_thresholds.py | ✅ PASS | Label-usage documented |
| Test-label flag in sens_07_fairness_postprocessing.py | ✅ PASS | Label-usage documented |
| Test-label flag in sens_08_afcp_comparison.py | ✅ PASS | Label-usage documented |
| Package: scikit-learn | ✅ PASS | version=1.9.0 |
| Package: xgboost | ✅ PASS | version=3.4.1 |
| Package: lightgbm | ✅ PASS | version=4.7.0 |
| Package: pandas | ✅ PASS | version=3.0.5 |
| Package: numpy | ✅ PASS | version=2.5.2 |
| Package: scipy | ✅ PASS | version=1.18.0 |
| Package: joblib | ✅ PASS | version=1.5.3 |

## Dependency Versions

| Package | Version |
|---|---|
| scikit-learn | 1.9.0 |
| xgboost | 3.4.1 |
| lightgbm | 4.7.0 |
| pandas | 3.0.5 |
| numpy | 2.5.2 |
| scipy | 1.18.0 |
| joblib | 1.5.3 |

## Reproducibility Notes

- All secondary analysis scripts carry the `fitting_test_labels_used: NO` assertion.
- Frozen primary result hashes recorded in `frozen_file_hashes.json`.
- Pipeline reproducibility verified by reconstructing XGBoost test-set AUC from joblib model.
- All split ID sets are mutually exclusive.

## Final Experiment Status

**STATUS: ✅ APPROVED FOR FREEZE — All critical checks pass. Experiment is reproducible.**