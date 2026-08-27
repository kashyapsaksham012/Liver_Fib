# Phase 3 BMI-Sensitivity Mitigation

**Status:** COMPLETE — separate BMI-sensitivity investigation  
**Final result:** **NO ACCEPTABLE MITIGATION IDENTIFIED**

This phase is separate from the repository's authoritative Phase 7 work. Phase 7 remains
unchanged and authoritative for its original objective: Mondrian conformal calibration of
conformal under-coverage. It is not treated as a solution to the Normal-BMI versus Obese
classification-sensitivity disparity.

## Frozen protocol and data protection

The primary outcome, ten predictors, cohort, BMI/age definitions, model families, split, and
original model artifacts were unchanged. Candidate development used only the existing OOF
predictions for the 5,007-person training partition. Candidate parameters were frozen before
the locked-test evaluation. The locked test set was then evaluated once for the original model
and the OOF-selected candidate for each model; no candidate was changed afterward.

The pre-specified OOF selection gate was: overall specificity no more than 5 percentage points
below the original; overall sensitivity no more than 5 percentage points below the original;
Brier score no more than 0.01 above the original; and the Age-60+ versus Age-40–59 sensitivity
gap no more than 5 percentage points worse than the original. Among candidates passing the gate,
the smallest absolute Obese-minus-Normal sensitivity gap was selected. This was a
multi-metric rule, not a fairness-only rule.

## Candidates

| Candidate | Phase 2 justification | OOF status |
|---|---|---|
| `original_frozen` | Baseline comparator | RETAINED comparator |
| `bmi_youden` | Directly addresses threshold crossing using BMI-specific OOF Youden thresholds | Selected for Logistic, MLP; rejected for other models by the multi-metric rule |
| `bmi_platt_global_youden` | Addresses BMI score/calibration shifts, then uses one OOF-derived operating threshold | Selected for Random Forest, XGBoost, LightGBM; fairness improvement was small on locked test |
| `bmi_age_youden` | Addresses the possible BMI × Age contribution | Rejected: age-stratum trade-offs and/or sensitivity loss failed the gate |
| `bmi_platt_youden` | Combined score calibration and BMI-specific decision adjustment | Rejected: no advantage over simpler candidates under the gate |

All candidate metrics, scopes, counts, thresholds, calibration values, AUROC, PR-AUC, Brier,
ECE, and sensitivity intervals are in `phase3_candidate_mitigation_results.csv`.

## Locked-test confirmation

The confirmatory file is `phase3_locked_test_confirmation.csv`. The selected candidate reduced
the BMI sensitivity gap for Logistic Regression from 47.66 percentage points to 14.94 and for
MLP from 39.03 to 15.84. Random Forest changed from 31.62 to 30.19, XGBoost from 31.36 to
29.94, and LightGBM remained 27.08 percentage points. Thus, benefit was model-dependent and
not consistently meaningful.

Specificity trade-offs were material and model-dependent. For example, Logistic overall
specificity changed from 0.708 to 0.690 and overall sensitivity from 0.821 to 0.765; MLP
specificity changed from 0.609 to 0.604 and sensitivity from 0.883 to 0.864. Calibration
candidates substantially changed Brier/ECE for Random Forest, XGBoost, and LightGBM, while
threshold-only candidates left probability-based AUROC, PR-AUC, Brier, ECE, calibration
intercept, and calibration slope unchanged. Exact values are in the locked-test CSV.

## Trade-offs and reliability

AUROC and PR-AUC are unchanged by threshold-only post-processing. Probability calibration is
unchanged by threshold-only candidates. BMI × Age metrics and all age-group metrics are
reported for every candidate; several BMI × Age cells are sparse and must not be
overinterpreted. The OOF-selected candidates do not alter conformal prediction sets, so
conformal coverage and set size are **NOT APPLICABLE** to those classification-only
mitigations. The separate Phase 7 Mondrian conformal results remain the authoritative
conformal analysis and are not merged here.

## Decision

No candidate satisfied the full scientific objective across all five model families while
preserving acceptable sensitivity, specificity, calibration, age behavior, and meaningful BMI
fairness improvement. The selected-per-model candidates are retained as confirmatory
descriptive results, not as a universal deployed mitigation.

**NO ACCEPTABLE MITIGATION IDENTIFIED.**

This conclusion is empirical and non-causal. It does not claim that BMI causes poor
performance or that any intervention produces causal fairness improvement.
