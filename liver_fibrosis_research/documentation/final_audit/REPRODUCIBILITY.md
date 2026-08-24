# Reproducibility Guide

## 1. Environment
- Python (project-local virtual environment at `liver_fibrosis_research/.venv/`).
- Package versions are pinned in `requirements-phase3-lock.txt` (the authoritative lock file for
  the modeling phases); `requirements.txt` and `requirements-phase3.txt` are the unpinned/earlier
  variants — use the lock file for exact reproduction. Key pinned versions referenced in the
  frozen reports: scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0, numpy 2.5.2.

## 2. Random seeds
A single fixed seed, `random_state=42`, is used throughout: the train/test split, `StratifiedKFold`
fold assignment, all stochastic model components (Random Forest, XGBoost/LightGBM, MLP
initialization), and the bootstrap resampling used for confidence intervals. This is recorded in
`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` and referenced in `documentation/phase3/
reproducibility_registry.md`.

## 3. Input data
Raw NHANES 2017–March 2020 `.xpt` files (`P_DEMO`, `P_BMX`, `P_BIOPRO`, `P_CBC`, `P_GLU`,
`P_TRIGLY`, `P_HDL`, `P_LUX`) are public-use CDC/NCHS files, downloadable from
`https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/<FILE>.htm` for each component (exact
URLs verified in `documentation/source_metadata/phase1_references.md`). No restricted-access or
patient-identifying data is used — NHANES public-use files carry no direct identifiers.

## 4. How the train/test split is generated or recovered
The split is not re-generated on each run; it is locked once and stored by `SEQN` list:
`data/processed/splits/train_ids.csv` and `test_ids.csv` (produced by
`src/phase3_03_split_and_lock.py`, stratified 70/30 on the primary outcome, `random_state=42`). Any
later pipeline change must reuse this stored list, not regenerate the split — this is a
non-negotiable rule stated in `documentation/phase3/test_set_lock.md`.

## 5. How each phase is executed (script entry points, in order)
```
src/01_data_inventory.py                                  # Phase 1
src/phase2_04_build_analysis_dataset.py                    # Phase 2
src/phase3_03_split_and_lock.py                             # Phase 3: split
src/phase3_05_train_and_tune.py                             # Phase 3: train/tune/OOF
src/phase3_13_imbalance_audit_and_mlp_sensitivity.py        # Phase 3: MLP Balanced sensitivity
src/phase4_01_prediction_input_audit.py                     # Phase 4
src/phase4_02_primary_metrics.py
src/phase4_03_curves_and_ece.py
src/phase4_04_inference.py                                  # bootstrap CIs
src/phase4_05_recalibration.py                              # Platt fit on OOF
src/phase4_07_probability_diagnostics.py
src/phase4_09_final_test_set_calibration.py                 # ONE-TIME test-set touch
src/phase5_04_inference.py                                  # Phase 5
src/phase6_02_conformal_refit.py                             # Phase 6
src/phase6_03_conformal_calibration.py
src/phase7_02_mitigation_implementation.py                   # Phase 7
src/phase7_04_final_test_touch.py
src/phase8_02_train_and_holdout_evaluate.py                  # Phase 8
src/sens_02_train_evaluate.py                                # CAND_2/CAND_3 sensitivity
src/sens_03_alternative_threshold.py                         # 8.0kPa threshold sensitivity
src/mi_01_construct_and_diagnostics.py                       # MI construction
src/mi_02_black_subgroup_comparison.py                       # MI two-arm comparison
src/mi_03_black_subgroup_inference.py                        # MI statistical inference
```
Each script reads its inputs from the paths listed in Part D of
`RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md` and writes to the corresponding `results/` subdirectory.

## 6. Where each output is written
See `FINAL_RESEARCH_ARCHITECTURE.md`'s directory map. The authoritative Phase 3 final metrics are
`results/tables/phase3_final_baseline_results.csv` (there is no `results/model_comparison/`
directory — a prior external-tool session looked there and did not find it).

## 7. How final tables/figures are regenerated
Every reported table in the Phase 1–8 reports and the sensitivity reports is generated
deterministically from its listed script and input files, given the same pinned environment and
seed. Figures live under each phase's `figures/` subdirectory (e.g.
`results/calibration/figures/`, `results/fairness/figures/`, `results/uncertainty/figures/`).

## 8. Which analyses are intentionally deferred (do not attempt to "complete" these without a new
protocol amendment)
- CAND_4 (all-ages 12+) sensitivity cohort — defined but not executed.
- Broader multiple imputation beyond the Non-Hispanic Black scope.
- Conformal-coverage repetition for the 8.0 kPa threshold, CAND_2, or CAND_3.
- Intersectional (joint) Mondrian mitigation for the BMI-Obese ∩ Age-60+ overlap.
- XGBoost-specific re-tuning to bring mitigated coverage within tolerance.
- External (non-NHANES) validation.
See `REMAINING_ANALYSES_AND_RESEARCH_STATUS.md` for the full, current list.

## 9. Which analyses use frozen outputs rather than retraining
The 8.0 kPa threshold sensitivity check **relabels the existing 8.2 kPa model's test predictions**
against the alternative outcome definition — it does not retrain, does not refit Platt parameters,
and does not repeat conformal calibration (`alternative_threshold_8p0kPa_results.csv` records
`retrained=False` for every row). CAND_2 and CAND_3, by contrast, are **independently re-split and
retrained** from scratch on their own cohorts.

## 10. Verified reproducibility claims (this audit)
`phase3_verification_log.md` and `reproducibility_audit.md`
(`documentation/phase3/`) record that reruns of the Phase 3 pipeline produce identical predictions
and metrics (max absolute difference of 0) under the pinned environment and fixed seed. This audit
did not itself re-execute the full pipeline end-to-end; it verified reported numbers against the
already-frozen result files and source code, which is a documentation/consistency check, not a
from-scratch reproduction run.
