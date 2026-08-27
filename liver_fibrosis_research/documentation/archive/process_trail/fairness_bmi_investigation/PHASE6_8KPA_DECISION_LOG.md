# Phase 6 8.0-kPa Decision Log

- New analysis namespace: `results/fairness_bmi_investigation/phase6_8kpa_robustness`; pre-existing artifacts were read-only.
- Outcome frozen before test access: `LUAXSTAT==1 and LUXSMED>=8.0`.
- Cohort: N=7153; 8.2 positives=666; 8.0 positives=715; changed labels=49.
- Five models were retrained with Phase 3 frozen configurations; no hyperparameter search occurred.
- OOF thresholds and approved OOF Platt calibration were frozen before test access.
- Conformal calibration used the frozen 90% split-conformal score and finite-sample correction.
- Locked test set was used exactly once after all development decisions.
- No external or out-of-sample validation and no mitigation.
- Missing lineage links: frozen 8.2 protocol commit — NOT FOUND IN REPOSITORY; frozen 8.2
  model-artifact manifest — NOT FOUND IN REPOSITORY.

## Final conclusion
SOME MAJOR FINDINGS ARE THRESHOLD-SENSITIVE
