# Authoritative Results Register

- CAND_1: N=7,153; 666 positive; 9.31%.
- Baseline AUROC: 0.8229–0.8429; no FDR-significant winner.
- Calibration: OOF intercepts and locked-test Platt results.
- Fairness: Normal-BMI versus Obese deficit 27.1–47.7 pp in 5/5; Age-60+ significant in 4/5.
- Conformal: marginal 88.12–90.82%; BMI-Obese 76.8–82.3%; Age-60+ 81.1–85.6%.
- Project Phase 7: partial Mondrian result (5/9), with XGBoost tolerance breach and BMI×Age precedence limitation.
- NHB holdout: N=1,787; AUC 0.7719–0.7893; within-NHANES demographic holdout.
- Temporal separate work: N=4,910; 563 positive; AUROC 0.7765–0.7824; **PARTIAL TEMPORAL REPLICATION**.

Sources and lineage are in the CSV registry.
