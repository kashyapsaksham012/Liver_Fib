# Corrected Phase 3 Decision Log

| Item | Decision |
|---|---|
| Development cohort | Complete OOF-linked primary training partition, including all BMI categories |
| Independent calibration evaluation | Deterministic OOF fit/evaluation halves; calibration parameters never evaluated on fit rows |
| Threshold derivation | OOF fit half only; Youden rule fixed before evaluation |
| Candidate selection | Full-cohort multi-metric gate, then absolute BMI gap within the gate |
| Test access | Test IDs, predictions, and metadata loaded only after selection manifest was written |
| Selected candidates | Original frozen for Logistic, Random Forest, XGBoost, LightGBM; BMI Platt calibration for MLP |
| Conformal analysis | Split-conformal development evaluation for all candidates; calibration candidates evaluated after probability transformation |
| Multiplicity | Candidate comparison treated as a prespecified descriptive family; no unsupported significance claims made |
| Small cells | BMI × Age cells reported with counts; threshold fallback used below 10 positive or negative fit cases |
| Phase 7 separation | Existing Mondrian conformal work retained unchanged and outside the BMI-sensitivity candidate pool |
| Final result | **NO ACCEPTABLE MITIGATION IDENTIFIED** |
