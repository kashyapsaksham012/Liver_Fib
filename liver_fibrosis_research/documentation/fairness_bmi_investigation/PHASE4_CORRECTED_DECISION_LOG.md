# Phase 4 Corrected Decision Log

| Decision | Corrected execution |
|---|---|
| Historical Phase 4 status | Superseded for the audited claims; preserved unchanged |
| ECE | Ten equal-frequency risk deciles, validated in `ece_validation.csv` |
| Development split | OOF rows sorted by SEQN; even index fit, odd index evaluation |
| Calibration candidates | `global_platt`; `subgroup_platt_bmi_age` |
| Cell minimums | n >= 20, positives >= 10, negatives >= 10; explicit global fallback |
| Conformal comparator | Global Platt and subgroup Platt both fit/apply maps under the identical split-conformal framework |
| Selection gate | Existing gate: ECE improvement; Brier <= global +0.01; overall sensitivity/specificity within 5 pp; absolute Age-60-vs-40 gap within 5 pp |
| Locked-test access | Manifest written first; one confirmatory scoring pass only |
| Selected methods | logistic=global_platt, random_forest=subgroup_platt_bmi_age, xgboost=subgroup_platt_bmi_age, lightgbm=subgroup_platt_bmi_age, mlp=global_platt |
| Scientific status | **NO ACCEPTABLE SUBGROUP CALIBRATION IMPROVEMENT IDENTIFIED** |

No significance claims are introduced; uncertainty is descriptive and limited to supported
Wilson intervals and conformal-development summaries.
