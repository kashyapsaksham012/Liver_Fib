# Phase 4 Corrected Final Audit Decision Log

**Mode:** Read-only post-audit; no experiment rerun and no existing artifact modified.

| Audit item | Decision | Evidence / limitation |
|---|---|---|
| Overall disposition | **B — accepted with limitations** | Corrected defects are addressed and the main conclusion is supported; provenance and inferential limits remain. |
| Frozen scope | PASS | Corrected script carries five primary models, ten predictors, primary outcome, BMI/age definitions, and frozen thresholds. |
| ECE definition | PASS | `ece_equal_frequency()` uses ten equal-frequency deciles; `ece_validation.csv` has 11/11 PASS rows and max absolute difference ≈1.04e-17. |
| ECE validation meaning | LIMITED | This is an implementation/protocol cross-check, not a significance test or independent-population validation. |
| OOF fit/evaluation separation | PASS | Sorted OOF rows: 2,504 fit / 2,503 evaluation; maps are fit only on the fit half. |
| Conformal fit/evaluation separation | PASS | Identical 501/501 development split for both candidates; maps and conformal thresholds are recomputed per arm. |
| Probability mapping | PASS | All conformal rows report `map_applied_to_fit=True` and `map_applied_to_eval=True`; global and subgroup status labels are explicit. |
| Sparse cells | PASS WITH LIMITATION | Requirements are n≥20, positive≥10, negative≥10; fallback is explicit and source-counted. BMI×Age metrics use precedence, not a joint map. |
| Selection gate | PASS ARITHMETICALLY | Code and manifest implement ECE improvement, Brier +0.01, sensitivity/specificity ±5 pp, and Age-gap limit. A separate prospective freeze for this new gate was not found. |
| Exact choices | PASS | Logistic/MLP retain global; Random Forest/XGBoost/LightGBM select subgroup, exactly as the corrected comparison and manifest record. |
| BMI fairness effect | NO IMPROVEMENT | Frozen raw thresholds make classification invariant; all selected-vs-global locked-test BMI-gap changes are 0.000 pp. |
| Age/BMI×Age interpretation | QUALIFIED | Age gaps and all BMI×Age scopes are present, but no formal candidate-difference inference and no joint intersectional calibrator were produced. |
| Conformal target interpretation | QUALIFIED | Development coverages are descriptive (0.8782–0.8902); Wilson intervals are reported, but no external or locked-test conformal validation is claimed here. |
| Locked-test order | PARTIAL PASS | Static source order places manifest write before test loading (lines 650, 653, 660). No external runtime access logger exists. |
| Locked-test fitting protection | PASS | Test outcomes are checked for consistency and scored after selection; no test labels enter `fit_platt()` in the test block. |
| Runtime proof | LIMITED | Lineage has start/finish metadata but explicitly records unavailable runtime event logging. |
| Hash lineage | PASS WITH ONE GAP | Current lineage hashes core inputs/outputs and they match; duplicate `phase4_corrected_ece_validation.csv` is listed but not emitted by the current script. |
| Prior-artifact preservation | PASS | Historical Phase 4 and prior exploratory paths, scripts, and outputs remain separate and unchanged. |
| Statistical claims | RESTRICTED | Do not add p-values, CIs, equivalence, or superiority claims absent from corrected files. |
| Final scientific conclusion | **SUPPORTED WITH SCOPE** | “No acceptable subgroup-calibration improvement identified” is supported for the BMI fairness/reliability objective, not as a claim that no calibration metric ever improves. |

## Required wording

Use: **“Corrected Phase 4 found no acceptable subgroup-calibration improvement for the
BMI fairness/reliability objective; probability calibration left frozen classification
disparities unchanged.”**

Do not use: “fair,” “jointly mitigated,” “statistically superior,” “equivalent,” or
“externally validated.”
