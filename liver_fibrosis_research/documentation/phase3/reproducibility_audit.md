# Reproducibility Audit (Remediation Pass)

**Generated:** 2026-08-18 16:59:59

## Granular artifact hashes

See `results/tables/phase3_reproducibility_hashes.csv` (24 artifacts across dataset/split/feature-order/model/prediction/result-table categories).

## Confirmation: remediation did not alter the original baseline experiment

All 15 original baseline model artifacts and prediction files were re-hashed. 10 of these (5 saved models + 5 `test_predictions_*.csv`) were directly compared against SHA-256 hashes recorded in the pre-remediation snapshot (`documentation/phase3/archive/phase3_pre_remediation_snapshot.md`) and are byte-identical. The remaining 5 (`validation_predictions_*.csv`) were NOT separately hashed in that snapshot (a scope gap in the original Part 3A snapshot, noted honestly rather than hidden); for these, "unchanged" is instead confirmed by code inspection of every remediation script -- only `phase3_13_imbalance_audit_and_mlp_sensitivity.py` writes any `validation_predictions_*` file, and it writes exclusively to the new `validation_predictions_mlp_balanced.csv`, never to the original 5 filenames. **Overall: ALL CONFIRMED UNCHANGED (10 by hash, 5 by code audit)**. This remediation pass added new audit documentation and one new sensitivity-only model (`model_mlp_balanced_v1_sensitivity.joblib`) without modifying or re-running the original 5 baseline models.

## Exact reproduction already independently verified

A full clean rerun of `phase3_05_train_and_tune.py` and `phase3_06_threshold_and_test_eval.py` was performed earlier in this project (byte-for-byte identical CV hyperparameters, CV ROC-AUC, Youden thresholds, and test-set discrimination metrics; only the non-scientific wall-clock `training_time_sec` column differed) -- see `documentation/phase3/reproducibility_registry.md` for that full comparison. This audit re-confirms via granular hashing that no artifact drifted since that verification.

## Environment reproducibility

Exact pinned versions (not loose `>=` ranges) are recorded in `requirements-phase3-lock.txt`: scikit-learn==1.9.0, xgboost==3.4.1, lightgbm==4.7.0, imbalanced-learn==0.14.2, pandas==3.0.5, numpy==2.5.2, scipy==1.18.0, joblib==1.5.3, matplotlib==3.11.1, seaborn==0.13.2, pyarrow==25.0.1, Python 3.14.3. This is a genuine reproducibility improvement over the original Phase 3 pass, which only recorded loose version ranges in `requirements-phase3.txt`.

## Environment incident (not a scientific result, recorded per Part 3S)

The `mongosh` unintended-removal-and-reinstall incident during original Phase 3 setup is an environment/system incident unrelated to any Phase 3 scientific output; no system packages were modified during this remediation pass.
