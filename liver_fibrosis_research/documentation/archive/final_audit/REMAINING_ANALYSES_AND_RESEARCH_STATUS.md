# Remaining Analyses and Research Status

Status of every analysis this project has ever pre-registered, attempted, or deferred, verified
against the repository's own files as of this audit (not inferred from any external summary).

| # | Analysis | Status | Evidence |
|---|---|---|---|
| 1 | Primary pipeline: Phases 1–8 (assembly → protocol → baseline models → calibration → fairness → conformal uncertainty → mitigation → NHB holdout generalization) | **COMPLETE** | All 8 `PHASE*_REPORT.md` files present; all frozen result CSVs verified in this and a prior audit |
| 2 | Fibrosis-threshold sensitivity (8.0 kPa vs. primary 8.2 kPa) | **COMPLETE, narrow scope** — relabel + reapply existing model outputs only | `results/sensitivity/alternative_threshold_8p0kPa_results.csv`, `alternative_threshold_8p0kPa_bmi_age_fairness.csv` |
| 3 | Relaxed-elastography-eligibility sensitivity cohort (CAND_2) | **COMPLETE** — independently re-split and retrained, not merely dataset-constructed | `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md` §8; `data/processed/analysis_dataset_cand2_relaxed_elastography.parquet` |
| 4 | Fasting-extended architecture sensitivity cohort (CAND_3, 12 predictors) | **COMPLETE** — independently re-split and retrained | `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md` §9; `data/processed/analysis_dataset_secondary.parquet` |
| 5 | Cross-sensitivity comparison of BMI/Age fairness findings across all three above | **COMPLETE** | `results/sensitivity/primary_vs_sensitivity_comparison.csv` (60 rows) |
| 6 | Multiple imputation for the Non-Hispanic Black complete-case selection-bias concern | **COMPLETE, narrow scope** — discrimination/calibration/fairness only | `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`, `MI_CLOSURE_RECONCILIATION_REPORT.md` |
| 7 | Conformal-coverage comparison under multiple imputation (NHB) | **NOT PERFORMED** — explicitly not authorized under the frozen `missing_data_protocol.md` for this MI round | `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` §13 |
| 8 | Conformal-coverage repetition for the 8.0 kPa threshold, CAND_2, or CAND_3 | **NOT PERFORMED** — deferred as future work | `deferred_sensitivity_execution_matrix.csv` |
| 9 | Model retraining and Platt recalibration specifically for the 8.0 kPa threshold | **NOT PERFORMED** — existing 8.2 kPa model outputs were relabeled and reapplied, not retrained | `alternative_threshold_8p0kPa_results.csv`: `retrained=False` for every row |
| 10 | All-ages (12–17 included) sensitivity cohort, CAND_4 (N=8,215) | **NOT EXECUTED** — remains an open, formally-tracked EXPLORATORY item | `CAND4_CLASSIFICATION_RESOLUTION_REPORT.md`; `deferred_sensitivity_execution_matrix.csv` |
| 11 | Broader multiple imputation (beyond the NHB scope — e.g. calibration/fairness robustness for other subgroups under MI) | **NOT PERFORMED / NOT FROZEN** — this scope was never protocol-frozen and is explicitly marked `DO NOT EXECUTE — NOT FROZEN` in the execution matrix | `deferred_sensitivity_execution_matrix.csv` |
| 12 | Intersectional (joint) Mondrian mitigation for the BMI-Obese ∩ Age-60+ overlap population (294 people) | **NOT PERFORMED** — current mitigation applies single-rule, last-write-wins precedence (Age overwrites BMI) instead | `../mitigation/phase7_bmi_age_overlap_interpretation.md`, `src/phase7_04_final_test_touch.py` |
| 13 | XGBoost-specific re-tuning to bring its post-mitigation marginal coverage back within the ±5pp tolerance | **NOT PERFORMED** | `PHASE7_MITIGATION_RESULTS_REPORT.md` §14/16 |
| 14 | External (non-NHANES, independent-population) validation | **NOT PERFORMED** — named as the single most important next step in this project's own documentation | `../reliability_extension/external_validation_future_work.md` |
| 15 | Temporal (cross-cycle) validation within NHANES | **DETERMINED INFEASIBLE**, not merely undone — `SDDSRVYR` is constant (66.0) across every record in this release | `PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md` §6 |
| 16 | Co-occurrence correlation and Decision Curve Analysis extension | **COMPLETE** | `RELIABILITY_EXTENSION_RESULTS_REPORT.md` |
| 17 | Literature novelty/duplication audit (separate task, same repository) | **COMPLETE** — see the published artifact from that session; not duplicated here | out of scope for this document |

## What this means for a manuscript

Items 1–6 and 16 are load-bearing, completed results that can be reported as such, with their
documented scope limits stated (item 2's relabel-only scope; item 6's NHB-only scope). Items 7–15
are legitimate, explicitly-acknowledged gaps — none of them should be described in a manuscript as
resolved, and none should be silently omitted from a limitations section. Item 14 in particular
(no external validation) is the largest single generalizability caveat on the entire project and
should be foregrounded, not buried.
