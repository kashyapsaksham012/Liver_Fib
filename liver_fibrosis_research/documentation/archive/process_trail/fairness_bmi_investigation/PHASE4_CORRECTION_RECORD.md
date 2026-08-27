# Phase 4 Correction Record

**Disposition:** The historical subgroup-calibration execution is superseded for the audited
claims, but all historical Phase 4 files remain preserved and were not modified. This
re-execution creates only `results/fairness_bmi_investigation/phase4_corrected/`.

## Audited defects corrected

1. ECE uses the frozen ten equal-frequency risk deciles, verified against
   `documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md`; the verification artifact is
   `results/fairness_bmi_investigation/phase4_corrected/ece_validation.csv`.
2. Both conformal arms fit and apply their named maps on the same conformal-development
   even/odd split. `global_platt` now fits and applies one global Platt map; the comparator
   uses BMI-first, age-second, global-fallback subgroup Platt maps.

Maps require at least 20 observations, 10 positives, and
10 negatives. Every non-estimable cell is explicitly recorded and falls back to
the global map. The frozen model set, predictors, outcome, cohort, BMI/age definitions,
thresholds, and existing selection gate are unchanged.

## Ordering and preservation

OOF development and conformal comparison were completed before selection was frozen. The
selection manifest was written before any locked-test IDs, metadata, predictions, or outcomes
were loaded. Exactly one locked-test confirmation pass followed; no selection or parameter
changes were made afterward. The prior exploratory artifact and Phase 0–3, Phase 7, master,
and later-phase artifacts were not modified.

Selected development methods: `logistic=global_platt, random_forest=subgroup_platt_bmi_age, xgboost=subgroup_platt_bmi_age, lightgbm=subgroup_platt_bmi_age, mlp=global_platt`.

Final scientific status: **NO ACCEPTABLE SUBGROUP CALIBRATION IMPROVEMENT IDENTIFIED**
