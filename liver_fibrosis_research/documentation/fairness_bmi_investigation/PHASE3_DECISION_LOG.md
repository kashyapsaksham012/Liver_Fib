# Phase 3 Decision Log

| Item | Decision |
|---|---|
| Prior Phase 7 work | Kept separate and unchanged; authoritative only for conformal under-coverage mitigation |
| Development data | Existing OOF predictions on the 5,007-person training partition only |
| Locked-test use | One confirmatory evaluation after OOF selection was frozen |
| Threshold candidate | BMI-specific OOF Youden thresholds |
| Calibration candidate | BMI-specific Platt calibration with OOF-derived global transformed threshold |
| BMI × Age candidate | OOF Youden thresholds per estimable BMI × age cell; fallback to global threshold for sparse cells |
| Combined candidate | BMI-specific Platt calibration plus BMI-specific OOF Youden thresholds |
| Selection gate | Specificity >= baseline -5 pp; sensitivity >= baseline -5 pp; Brier <= baseline +0.01; Age-60+ vs Age-40–59 sensitivity gap <= baseline +5 pp |
| Within-gate choice | Smallest absolute Obese-minus-Normal sensitivity gap; specificity used as tie-break |
| Selected candidates | Logistic/MLP: `bmi_youden`; Random Forest/XGBoost/LightGBM: `bmi_platt_global_youden` |
| Rejected candidates | BMI × Age and combined methods failed the pre-specified multi-metric comparison or offered no advantage |
| Conformal metrics | NOT APPLICABLE to classification threshold/calibration candidates; prior Phase 7 conformal results remain separate |
| Final classification | **NO ACCEPTABLE MITIGATION IDENTIFIED** |

## Required interpretation

The selected candidates were not declared successful merely because they reduced a fairness
gap. Locked-test confirmation showed meaningful improvement for Logistic Regression and MLP,
little improvement for Random Forest and XGBoost, and no improvement for LightGBM, alongside
specificity and overall-sensitivity trade-offs. Therefore no universal BMI-sensitivity
mitigation is accepted.

No predictors, outcomes, BMI definitions, models, architectures, preprocessing, or primary
results were changed. Temporal and external validation were not performed. The master report
was not modified.
