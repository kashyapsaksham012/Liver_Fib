# Final Research Architecture

End-to-end pipeline, with the key input/output artifact at every stage. Paths are relative to
`liver_fibrosis_research/`.

```
Raw NHANES 2017–March 2020 (.xpt: P_DEMO, P_BMX, P_BIOPRO, P_CBC, P_GLU, P_TRIGLY, P_HDL, P_LUX)
        │
        ▼  src/01_data_inventory.py, Phase 1 assembly
data/interim/nhanes_master_phase1.{csv,parquet}
        │  anchor cohort (elastography attempted, non-missing outcome): N=10,409
        ▼  src/_cohorts.py (CAND_1 definition) + Phase 2 protocol freeze
data/processed/analysis_dataset_primary.parquet
        │  N=7,153, 666 positive (9.31%), 10 predictors, outcome = LUXSMED ≥ 8.2 kPa
        ▼  src/phase3_03_split_and_lock.py
data/processed/splits/{train_ids,test_ids}.csv   (70/30, stratified, seed=42)
        │
        ├───────────────────────────────┐
        ▼ train N=5,007                 ▼ locked test N=2,146 (touched once per phase)
src/phase3_05_train_and_tune.py         │
  5-fold StratifiedKFold CV             │
  → model joblibs + OOF predictions     │
        │                               │
        ▼                               │
results/tables/phase3_final_baseline_results.csv,  phase3_model_comparison_fdr.csv
        │  AUC 0.8229–0.8429, no significant pairwise winner after FDR
        ▼  src/phase4_05_recalibration.py  (Platt, fit on OOF only)
results/calibration/{primary_metrics_by_model.csv, recalibration params}
        │
        ▼  src/phase4_09_final_test_set_calibration.py  (apply frozen Platt params, ONE touch)
results/calibration/test_set_calibration_final.csv, test_set_recalibrated_predictions.csv
        │  raw intercepts −1.86…−2.26 → recalibrated −0.15…+0.14; AUC unchanged
        ▼  Phase 5 fairness audit on recalibrated test predictions
results/fairness/*  (subgroup sensitivity/specificity/AUC/PPV/NPV, FDR-corrected)
        │  Normal-BMI vs Obese: 27–48pp deficit, 5/5 significant
        │  Age-60+ vs 40–59: deficit in 5/5, FDR-significant in 4/5 (not Logistic)
        │
        ├──────────────────────────────────────────────┐
        ▼ (independent 80/20 split of train N=5,007)    │
proper_train N=4,005 ──► refit models ──► conformal_calibration N=1,002
        │                                               │
        ▼  src/phase6_03_conformal_calibration.py       │
results/uncertainty/*  (split conformal, 90% target)    │
        │  marginal coverage 88.1–90.8%; BMI-Obese 76.8–82.3%, Age-60+ 81.1–85.6% (both fail 90%)
        ▼  src/phase7_02_mitigation_implementation.py, phase7_04_final_test_touch.py
results/mitigation/*  (Mondrian group-wise calibration, targets = FDR-sig combos from Phase 5∩6)
        │  5/9 combinations resolved; XGBoost marginal coverage +5.27pp (tolerance breach)
        │  BMI∩Age overlap (294 people, 13.7%) resolved by list-order precedence (Age overwrites BMI)
        ▼  src/phase8_02_train_and_holdout_evaluate.py
Non-Hispanic Black holdout (N=1,787) vs. retrain-excluding-NHB (N=5,366)
        │  AUC 0.8229–0.8429 → 0.7719–0.7893; calibration unstable on holdout (intercepts <0, slopes <1)
        ▼
results/end_to_end/*, PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md

                    ┌─────────────────────────────────────────────────────────┐
                    │                 SENSITIVITY ANALYSES                    │
                    │  (each independently derived from the Phase 2 protocol, │
                    │   not folded into the primary numbers above)            │
                    ├─────────────────────────────────────────────────────────┤
                    │ 8.0kPa threshold: relabel only, no retrain/recal/conformal│
                    │ CAND_2 relaxed elastography: independent retrain, N=7,639│
                    │ CAND_3 fasting-extended: independent retrain, N=3,582    │
                    │ NHB multiple imputation: recovers 615 excluded ppts,     │
                    │   MI pool N=7,768, fold-embedded IterativeImputer        │
                    │ CAND_4 (all-ages 12+, N=8,215): NOT EXECUTED             │
                    └─────────────────────────────────────────────────────────┘
```

## Directory map (as actually found on disk)

```
liver_fibrosis_research/
├── data/{interim,processed,raw}/
├── src/                          — all pipeline scripts, phase-numbered
├── results/
│   ├── tables/                   — phase3_final_baseline_results.csv (authoritative Phase 3 metrics),
│   │                                phase2_predictor_registry.csv, phase3_model_comparison_fdr.csv
│   ├── calibration/               — Phase 4 raw/recalibrated metrics, curve_data/, figures/
│   ├── fairness/                  — Phase 5 subgroup metrics, curve_data/, figures/
│   ├── uncertainty/                — Phase 6 conformal coverage/efficiency, figures/
│   ├── mitigation/                — Phase 7 Mondrian results
│   ├── sensitivity/                — 8.0kPa threshold, CAND_2, CAND_3, MI diagnostics/results
│   ├── validation/, end_to_end/, pre_calibration/, provenance/, reliability_extension/
│   └── predictions/                — per-model raw/OOF/test prediction CSVs
├── documentation/
│   ├── phase2/, phase3/            — frozen pre-analysis protocols (read before results existed)
│   ├── calibration/, fairness/, uncertainty/, mitigation/, validation/, sensitivity/
│   ├── reliability_extension/       — co-occurrence + DCA extension, external-validation note
│   ├── source_metadata/            — external literature citations used for threshold selection
│   ├── data_dictionary/, audit_reports/, provenance/
│   └── final_audit/                — THIS consolidation set
└── PHASE{1..8}_*.md, *_REPORT.md   — phase-by-phase and closure reports (root of this directory)
```

Note: `results/model_comparison/` does **not** exist — an external tool session looking for Phase 3
final metrics there was looking in the wrong place; the correct file is
`results/tables/phase3_final_baseline_results.csv`.
