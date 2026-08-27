# Temporal frozen conformal input audit

No Phase 3 evaluation was performed.

## Frozen sources

- Phase 6 refit artifacts: `models/phase6_conformal_refit/model_<model>_proper_train_refit.joblib`.
- Platt constants: `results/calibration/recalibrated_oof_predictions_<model>.csv`.
- Global conformal thresholds: `results/uncertainty/conformal_thresholds_by_model.csv`.
- Final N0=0 M4b configuration: `results/tables/m4b_prespecified_n0_final_results.csv`; group/joint quantiles: `results/tables/m4b_lightgbm_failure_analysis.csv`.

## Generated conformal inputs

- `logistic`: 4,910 predictions, 4,910 unique SEQNs, no missing/dropped values, finite probabilities in [0,1]; artifact SHA-256 `000e51505e76d49ebf02a57d29a3132ea1fa837b49497e142c9fd8caeb73c630`.
- `random_forest`: 4,910 predictions, 4,910 unique SEQNs, no missing/dropped values, finite probabilities in [0,1]; artifact SHA-256 `22a63c50c43b6aef4834223c4b27c03a811dd8881e770cfaea2437d946d32618`.
- `xgboost`: 4,910 predictions, 4,910 unique SEQNs, no missing/dropped values, finite probabilities in [0,1]; artifact SHA-256 `9e7745d64f3b967a06cb053b2dfea9e0950075e5c788aecb6a1c3b245d83dfc8`.
- `lightgbm`: 4,910 predictions, 4,910 unique SEQNs, no missing/dropped values, finite probabilities in [0,1]; artifact SHA-256 `597ad772bf68ef6a1022d6b44ef3039c90220ae614a0f11ec015a23c59fa0856`.
- `mlp`: 4,910 predictions, 4,910 unique SEQNs, no missing/dropped values, finite probabilities in [0,1]; artifact SHA-256 `5bd9a684357c6069b71163c46865d0358745154b813d947627acef5ecca79cb3`.

The exact frozen Phase 6 pipeline preprocessing was applied through the loaded refit artifacts. No training, refitting, parameter fitting, quantile recomputation, outcome use, demographic use, threshold tuning, N0 selection, or coverage evaluation occurred. Existing temporal prediction files and all frozen sources had identical before/after SHA-256 hashes.
