# Phase 4 Decision Log

| Decision | Evidence |
|---|---|
| Global comparator | Existing global Platt calibration, evaluated on independent OOF rows |
| New candidate | BMI/age subgroup Platt calibration with explicit sparse-cell fallback |
| Development split | Deterministic even/odd `SEQN` split of OOF rows |
| Test protection | Selection manifest written before locked-test files were loaded |
| Subgroups | BMI: Underweight/Normal/Overweight/Obese; Age: 18–39/40–59/60+; BMI × Age cells |
| Selection rule | ECE improvement, Brier within +0.01, overall sensitivity/specificity within 5 pp, Age-60+ gap within +5 pp |
| Selected model-level methods | Global for Logistic, Random Forest, XGBoost, MLP; subgroup for LightGBM |
| BMI fairness effect | No meaningful improvement; frozen classification decisions are unchanged |
| Conformal effect | Subgroup calibration reduced development coverage for most models; no general reliability benefit |
| Prior exploratory result | Preserved separately; not overwritten or merged |
| Final status | **NO ACCEPTABLE SUBGROUP CALIBRATION IMPROVEMENT IDENTIFIED** |

No Phase 0–3, primary, Phase 7, temporal, external, or master-report artifact was modified.
