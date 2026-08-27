# SUPERSEDED / INVALID RESULTS

Read-only audit, 2026-08-27. Historical artifacts are **preserved on disk** and were not
modified. Format: OLD RESULT → CURRENT REPLACEMENT → REASON → MANUSCRIPT STATUS.

---

## S1. Historical baseline AUROC / prevalence transcription errors

- **OLD:** narrative-draft AUROCs 0.8407 / 0.8354 / 0.8348 / 0.8184 (LR/RF/LGBM/MLP); CAND_2
  prevalence 9.49%, CAND_3 9.13%.
- **CURRENT:** `results/tables/phase3_final_baseline_results.csv` → 0.8334 / 0.8343 / 0.8394 /
  0.8229; CAND_2 = 10.52% (804/7,639), CAND_3 = 8.91% (319/3,582)
  (`phase2_candidate_cohort_comparison.csv`).
- **REASON:** early text draft diverged from the frozen result files; corrected in the final
  audit (CORR-01/02).
- **MANUSCRIPT STATUS:** DO NOT CITE the old values. Use the CSV values.

## S2. Age-60+ FDR significance in 5/5 models

- **OLD:** "Age-60+ sensitivity deficit is FDR-significant in all five models."
- **CURRENT:** `results/fairness/fairness_inference.csv` → significant in **4/5** (RF, XGBoost,
  LightGBM, MLP); Logistic not significant (reported FDR p ≈ 0.18–0.20).
- **REASON:** misreading of the inference table; Logistic never reached FDR significance — this
  is why Project Phase 7 gives Logistic no Age rule.
- **MANUSCRIPT STATUS:** INVALID. Report 4/5 only.

## S3. BMI-Obese ∩ Age-60+ overlap described as "294 people (~62% of the cohort)"

- **OLD:** the intersection is 294 people and ≈62% of the cohort.
- **CURRENT:** the intersection is 294 people = **13.7%** of the test set (294/2,146). The
  **62%** figure (≈1,330 people) is the **union** — anyone in either target group
  (589 Obese-only + 447 Age-only + 294 both) (`threshold_precedence_audit.csv`,
  `MASTER_END_TO_END_RESEARCH_REPORT.md` §B5).
- **REASON:** conflation of intersection and union.
- **MANUSCRIPT STATUS:** INVALID. Use "294 people, 13.7% of the test set" for the intersection.

## S4. Historical BMI-investigation Phase 3 mitigation

- **OLD:** `results/fairness_bmi_investigation/phase3_mitigation_comparison.csv` +
  `src/run_phase3_bmi_sensitivity_mitigation.py` — reported a BMI mitigation conclusion using a
  restricted Normal/Obese-only "overall", early locked-test access, and same-OOF calibration.
- **CURRENT:** corrected full-cohort independent-split run
  (`phase3_corrected/PHASE3_CORRECTED_MITIGATION_REPORT.md`) → **NO ACCEPTABLE MITIGATION
  IDENTIFIED** (see `VERIFIED_WITH_LIMITATIONS.md` V3).
- **REASON:** restricted-cohort "overall", premature test access, and calibration fit on the
  same OOF used for evaluation invalidate the full-cohort conclusion.
- **MANUSCRIPT STATUS:** SUPERSEDED / NOT_USABLE. Registry `superseded_by = P3C`.

## S5. Historical BMI-investigation Phase 4 subgroup calibration

- **OLD:** `results/fairness_bmi_investigation/phase4_subgroup_calibration/*` +
  `src/run_phase4_subgroup_calibration.py` — used wrong ECE binning and a mislabelled global
  conformal arm.
- **CURRENT:** corrected run (`phase4_corrected/`, `PHASE4_CORRECTED_FINAL_AUDIT_REPORT.md`
  Decision B) → **no acceptable subgroup-calibration improvement** (see
  `VERIFIED_WITH_LIMITATIONS.md` V4).
- **REASON:** equal-width vs equal-frequency ECE mismatch with the frozen protocol; the "global"
  conformal arm did not actually apply a global Platt map.
- **MANUSCRIPT STATUS:** SUPERSEDED / NOT_USABLE. Registry `superseded_by = P4C`.

## S6. Old KNN-AFCP approximation

- **OLD:** `src/sens_08_afcp_comparison.py` +
  `results/diagnostics/stage1/afcp_vs_mondrian_comparison.csv` — labelled a KNN nonconformity
  heuristic as "AFCP"; inflated overall coverage to 92.5–93.8%.
- **CURRENT:** faithful Zhou & Sesia AFCP (`src/sens_11_afcp_faithful.py`,
  `afcp_faithful_results.csv`) — EXPLORATORY, no superiority claim (see `EXPLORATORY_RESULTS.md`
  E7).
- **REASON:** methodological-fidelity violation (heuristic ≠ full conformal).
- **MANUSCRIPT STATUS:** INVALID / SUPERSEDED. No AFCP-superiority claim in any form.

## S7. Old M4b N0=100 test-set sweep

- **OLD:** `src/tradeoff_02_m4b_sensitivity_and_lock.py` — chose N0=100 after evaluating locked
  test-set coverage.
- **CURRENT:** `src/sens_12_m4b_n0_prespecified.py` — 5-fold CV on the calibration split only,
  no test labels → **N0* = 0** (`m4b_n0_cv_selection.csv`,
  `M4B_N0_SELECTION_PROTOCOL_FREEZE.md`).
- **REASON:** partition-integrity violation (hyperparameter chosen on the locked test).
- **MANUSCRIPT STATUS:** SUPERSEDED. Registry `superseded_by = old N0=100 → SUPERSEDED`. Use
  N0=0.

## S8. Early leakage-prone diagnostic scripts (pre-commit `5f1f9e5` / `f1b03ac`)

- **OLD:** `sens_04_continuous_splines.py` fitted the spline transformer on the locked test set;
  `sens_06_group_specific_thresholds.py` compared recalibrated probabilities against raw-scale
  thresholds and omitted Underweight.
- **CURRENT:** rewritten scripts (RCS on OOF only; raw probabilities across all 4 BMI
  categories) → `continuous_bmi_metrics.csv`, `group_specific_threshold_metrics.csv`.
- **REASON:** test-set leakage; probability-scale mismatch.
- **MANUSCRIPT STATUS:** SUPERSEDED. Use only the post-commit outputs; both remain EXPLORATORY.

## S9. Equal Opportunity `sens_07_fairness_postprocessing.py`

- **OLD:** reported baseline Logistic sensitivity = 0.10 (raw-vs-recalibrated scale mismatch).
- **CURRENT:** corrected diagnostic
  `results/diagnostics/stage1/correct_fairness_postprocessing_results.csv`.
- **REASON:** scale-mismatch defect.
- **MANUSCRIPT STATUS:** UNVERIFIED / UNTRUSTED for the old file; the newer file is EXPLORATORY.
  (Repository notes an old-vs-new status conflict; it remains diagnostic either way.)

## S10. `documentation/MASTER_RESEARCH_RESULTS.md` — conformal-coverage section (items 26–27, §3.5)

- **OLD (this document):** marginal coverage 89.00–90.12%; *Normal-BMI* coverage fails
  (81.04–82.65%); Age-60+ 84.40–85.80%.
- **CURRENT (raw artifacts):** `results/uncertainty/marginal_coverage_test_set.csv` →
  88.12–90.82%; `results/uncertainty/subgroup_coverage.csv` → **BMI-Obese** fails
  (76.8–82.3%), Normal-BMI/Overweight over-cover (0.95–0.97), Age-60+ 81.1–85.6%. Consistent
  with `MASTER_END_TO_END_RESEARCH_REPORT.md` §B4 and the `final_research_state` registers.
- **REASON:** `MASTER_RESEARCH_RESULTS.md` (frozen at git HEAD 142595d, before temporal work and
  the final consolidation) misreports its own cited CSV and inverts the BMI group label; all its
  other spot-checked numbers reconcile.
- **MANUSCRIPT STATUS:** the conformal-coverage numbers and BMI label in
  `MASTER_RESEARCH_RESULTS.md` are **SUPERSEDED / erroneous**; cite the raw CSVs and
  `MASTER_END_TO_END_RESEARCH_REPORT.md`. **Flagged for the register owner to correct or
  annotate `MASTER_RESEARCH_RESULTS.md`; not modified by this audit.**

## S11. Earlier temporal preflight ("FAILED — DO NOT PROCEED")

- **OLD:** `results/temporal_validation/PHASE3_FAILURE_REPORT.md` — first preflight failed
  (outcome + `RIDRETH3` companion data absent).
- **CURRENT:** resolved by attaching `LUX_L.xpt` / `DEMO_L.xpt` and bridging BMX/DEMO; all 4,910
  SEQNs matched; temporal Phases 1–4 completed
  (`PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md`).
- **REASON:** intermediate data-preparation failure, since resolved.
- **MANUSCRIPT STATUS:** historical intermediate record; not a final result.

## S12. CAND_4 all-ages cohort

- **OLD/STATUS:** N=8,215 constructed; documentation tension over whether it is folded under
  sensitivity item 2 or a distinct EXPLORATORY item (conflict C4).
- **CURRENT:** `NOT_EXECUTED` — no model / prediction / result artifact exists anywhere
  (`cand4_resolution_evidence.csv`).
- **MANUSCRIPT STATUS:** NOT_EXECUTED. Do not report any CAND_4 performance.

---

## Preservation note

All files named above remain present and unaltered. This register records their status; it does
not delete or overwrite them.
