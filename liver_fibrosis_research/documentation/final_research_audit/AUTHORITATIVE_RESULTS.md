# AUTHORITATIVE RESULTS

Read-only audit, 2026-08-27. Every finding below is currently authoritative: it is supported by a
raw frozen result artifact and is consistent with
`documentation/final_audit/MASTER_END_TO_END_RESEARCH_REPORT.md` and the
`documentation/final_research_state/` registers. Numbers are re-checked against raw CSVs where
noted. "Reproducibility" = whether a raw artifact + script + input lineage chain is established.

---

## A1. Primary cohort composition

- **Claim:** CAND_1 (`CAND_1_QUALITYVALID_ADULT_BROAD`) contains N=7,153; 666 positives; 6,487
  negatives; prevalence 9.31% (9.3108%). Outcome `LUXSMED ≥ 8.2 kPa` with `LUAXSTAT == 1`,
  frozen before training.
- **Source artifact:** `results/tables/phase2_outcome_prevalence.csv`,
  `results/tables/phase2_candidate_cohort_comparison.csv`; cohort flow
  `documentation/audit_reports/cohort_flow.csv` (10,409 → 9,700 → 9,023 → 7,768 → 7,153).
- **Source script:** `src/_cohorts.py`, `src/phase2_04_build_analysis_dataset.py`.
- **Phase:** Project Phase 1–2.
- **Authority:** AUTHORITATIVE. **Reproducibility:** ESTABLISHED (re-derived in
  `PHASE0_LINEAGE_AUDIT.md`, `PHASE1_REPRODUCTION.md` join = 7,153).
- **Limitation:** Complete-case filtering excludes 615 quality-valid adults; Non-Hispanic Black
  = 41.30% of exclusions vs 24.98% of the retained cohort (differential missingness).
- **Manuscript wording:** "The primary analytic cohort comprised 7,153 adults with a
  quality-valid VCTE examination (666 with `LUXSMED ≥ 8.2 kPa`; 9.31% prevalence)."

## A2. Data partitions

- **Claim:** Stratified 70/30 split (seed 42): train N=5,007 (466 positives), locked test
  N=2,146 (200 positives). For conformal work the training partition was split into proper-train
  N=4,005 (373 positives) and conformal-calibration N=1,002 (93 positives); quantile index
  k=903. Partitions disjoint.
- **Source artifact:** `data/processed/splits/*.csv`,
  `results/uncertainty/phase6_partition_audit.csv`, `results/tables/data_and_result_lineage.csv`.
- **Phase:** Project Phase 3 / 6. **Authority:** AUTHORITATIVE. **Reproducibility:** ESTABLISHED.
- **Limitation:** Single split; no repeated / nested outer resampling of the locked test.
- **Manuscript wording:** "A single stratified 70/30 split was used; the test set (N=2,146) was
  locked and evaluated once per analysis phase."

## A3. Baseline discrimination

- **Claim:** Test AUROC — Logistic 0.8334, Random Forest 0.8343, XGBoost 0.8429, LightGBM
  0.8394, MLP 0.8229 (range 0.8229–0.8429). 0/10 pairwise comparisons FDR-significant.
- **Source artifact:** `results/tables/phase3_final_baseline_results.csv`,
  `results/tables/phase3_model_comparison_fdr.csv` (`significant_after_fdr_0.05 = False`, 10/10).
- **Source script:** `src/phase3_05_train_and_tune.py`,
  `src/phase3_06_threshold_and_test_eval.py`.
- **Phase:** Project Phase 3. **Dataset:** CAND_1 locked test. **Authority:** AUTHORITATIVE.
  **Reproducibility:** ESTABLISHED (`FINAL_EXPERIMENTAL_EVIDENCE_LINEAGE.md`).
- **Key numbers:** AUROC band 0.8229–0.8429; Youden thresholds 0.4108–0.5211 (OOF-derived).
- **Limitation:** XGBoost has the highest point estimate but **not** statistically significant
  superiority. Modest PR-AUC (~0.35–0.37) at 9.31% prevalence.
- **Manuscript wording:** "Five model families achieved statistically indistinguishable
  discrimination (test AUROC 0.823–0.843; no pairwise comparison significant after
  Benjamini–Hochberg correction)."

## A4. Calibration and OOF Platt recalibration

- **Claim:** The four class-balanced models over-predict in raw output (OOF intercepts −2.243
  Logistic, −1.862 RF, −2.046 XGBoost, −2.053 LightGBM; MLP −0.281). OOF-fit Platt scaling,
  applied once to the locked test, corrects this (ECE 0.2452–0.2967 → 0.0113–0.0264; Brier
  0.1458–0.1755 → 0.0694–0.0715; intercepts → −0.15 to +0.14) with **AUROC unchanged**.
- **Source artifact:** `results/calibration/primary_metrics_by_model.csv`,
  `results/calibration/test_set_calibration_final.csv`.
- **Source script:** `src/phase4_05_recalibration.py`,
  `src/phase4_09_final_test_set_calibration.py`.
- **Phase:** Project Phase 4. **Authority:** AUTHORITATIVE. **Reproducibility:** ESTABLISHED.
- **Limitation:** Mechanism (prior shift ≈ log(0.0931/0.9069) ≈ −2.27) is the primary
  explanation, not a certainty about every contribution; isotonic rejected (466 OOF positives,
  Amendment #8). Recalibrated probabilities are the correct input to Phases 5–7.
- **Manuscript wording:** "Class-balancing produced severe raw over-prediction; out-of-fold
  Platt scaling restored aggregate calibration without altering discrimination."

## A5. BMI fairness — Normal-BMI vs Obese sensitivity deficit

- **Claim:** Normal-BMI sensitivity is 27.1–47.7 pp lower than Obese, FDR-significant in **all 5
  models** (Logistic −47.66, RF −31.62, XGBoost −31.36, LightGBM −27.08, MLP −39.03 pp;
  BH q ≤ 0.006).
- **Source artifact:** `results/fairness/subgroup_discrimination_metrics.csv`,
  `results/fairness/fairness_inference.csv`; reproduced in
  `results/fairness_bmi_investigation/phase1_bmi_reproduction.csv`.
- **Source script:** `src/phase5_04_inference.py`; reproduction
  `src/run_phase2_bmi_diagnostics.py` lineage.
- **Phase:** Project Phase 5 (reproduced BMI-investigation Phase 1). **Dataset:** CAND_1 locked
  test (Normal N=562, 22 positives; Obese N=883, 140 positives). **Authority:** AUTHORITATIVE.
  **Reproducibility:** ESTABLISHED and independently REPRODUCED.
- **Limitation:** Normal-BMI has 22 test positives → wide CIs. Underweight (1 positive) is
  uninterpretable and excluded. This is a model-fairness fact, distinct from the cohort-level
  differential-missingness fact.
- **Manuscript wording:** "Sensitivity for significant fibrosis was 27–48 percentage points
  lower in normal-weight than in obese participants across all five models (all q ≤ 0.006)."

## A6. Split conformal — marginal vs subgroup coverage

- **Claim:** At nominal 90% (α=0.10): marginal coverage 88.12–90.82% (acceptable). **BMI-Obese
  coverage 76.8–82.3%** and **Age-60+ coverage 81.1–85.6%**, Wilson CIs excluding 90% and
  FDR-significant for all five models. Normal-BMI and Overweight **over-cover** (0.95–0.97).
- **Source artifact:** `results/uncertainty/marginal_coverage_test_set.csv` (re-read: LR 0.9082,
  RF 0.8961, XGB 0.8812, LGBM 0.8961, MLP 0.8919), `results/uncertainty/subgroup_coverage.csv`
  (re-read: BMI-Obese 0.8233/0.8018/0.7678/0.7916/0.8086; Age-60+
  0.8489/0.8556/0.8111/0.8475/0.8381).
- **Source script:** `src/phase6_02_conformal_refit.py`,
  `src/phase6_03_conformal_calibration.py`, `src/phase6_04_final_test_touch.py`.
- **Phase:** Project Phase 6. **Authority:** AUTHORITATIVE. **Reproducibility:** ESTABLISHED.
- **Limitation:** Empirical subgroup coverage on one cohort (CAND_1); **not** a conditional
  conformal validity guarantee; small subgroup precision. `documentation/MASTER_RESEARCH_RESULTS.md`
  reports different numbers and the opposite BMI label — that document is **erroneous on this
  point** (conflict C1 in `FINAL_RESEARCH_AUDIT.md`); the raw CSVs above are authoritative.
- **Manuscript wording:** "Split-conformal prediction met its 90% marginal coverage target
  overall (88–91%) but under-covered obese (77–82%) and 60+ (81–86%) participants in every
  model."

## A7. Intersectional conformal coverage (baseline, descriptive)

- **Claim:** For BMI-Obese ∩ Age-60+ (test N=294, 35 positives) baseline split-conformal
  coverage collapses to 64.97–75.17% (Clopper–Pearson CIs exclude 90%).
- **Source artifact:** `results/uncertainty/intersectional_coverage_ci.csv`.
- **Phase:** Project Phase 6. **Authority:** AUTHORITATIVE (descriptive). **Reproducibility:**
  ESTABLISHED.
- **Limitation:** N=294 / 35 positives → wide CIs; descriptive, pre-specified cell.
- **Manuscript wording:** "In the obese-and-60+ intersection (N=294), baseline conformal
  coverage fell to 65–75%."

## A8. Project Phase 7 — FDR-gated Mondrian mitigation (authoritative description, limited outcome)

- **Claim:** Mitigation targeted only model×subgroup combinations FDR-significant in **both**
  Phase 5 and Phase 6 (BMI-Obese, Age-60+; Logistic got a BMI-only rule). **5/9** qualifying
  combinations reached nominal coverage; RF/Obese, XGBoost/Obese, LightGBM/Obese, LightGBM/60+
  did not. XGBoost marginal coverage rose to ~93.4% (**+5.27 pp breach** of the ±5 pp
  tolerance). Overlap = 294 people (13.7% of test); rules applied BMI-first then Age → Age
  overwrites BMI in the overlap (sequential precedence, not joint mitigation).
- **Source artifact:** `results/mitigation/test_set_mitigation_final.csv`,
  `results/mitigation/marginal_coverage_before_after.csv`,
  `results/mitigation/threshold_precedence_audit.csv`.
- **Source script:** `src/phase7_04_final_test_touch.py`.
- **Phase:** Project Phase 7. **Authority:** AUTHORITATIVE for the description; the *outcome* is
  VERIFIED_WITH_LIMITATIONS (see `VERIFIED_WITH_LIMITATIONS.md`).
- **Limitation:** Partial fix; documented tolerance breach; no joint intersectional mitigation.
- **Manuscript wording:** "Group-wise (Mondrian) conformal recalibration restored nominal
  coverage in 5 of 9 targeted model–subgroup combinations; it did not resolve the remaining four,
  breached the marginal-coverage tolerance for XGBoost (+5.3 pp), and applied single-attribute
  rules sequentially rather than jointly in the overlap population."

## A9. Phase 8 — Non-Hispanic Black subgroup-holdout generalization

- **Claim:** With Non-Hispanic Black participants (N=1,787; 148–177 positives depending on
  source column) withheld from training and used as the evaluation set, AUROC drops to
  0.7719–0.7893 (−0.049 to −0.062) and calibration becomes materially less stable (holdout
  intercepts −0.58 to −2.17, slopes 0.64–0.97).
- **Source artifact:** `results/validation/phase8_generalization_results.csv`,
  `results/validation/phase8_population_shift.csv`.
- **Source script:** `src/phase8_02_train_and_holdout_evaluate.py`.
- **Phase:** Project Phase 8. **Authority:** AUTHORITATIVE. **Reproducibility:** ESTABLISHED.
- **Limitation:** This is a **within-NHANES demographic holdout**, not external validation.
- **Manuscript wording:** "Withholding an entire demographic subgroup (Non-Hispanic Black) from
  training reduced discrimination on that subgroup (AUROC ≈ 0.77–0.79) and destabilised
  calibration."

## A10. Sensitivity cohorts and threshold (executed)

- **Claim:** 8.0-kPa relabel: AUROC 0.8145–0.8326; BMI-Obese disparity 35.1–51.6 pp (5/5 sig);
  Age-60+ negative 5/5, significant 2/5. CAND_2 (N=7,639; 804 positives; fresh fit): AUROC
  0.8526–0.8572. CAND_3 (N=3,582; 319 positives; 12 predictors; fresh fit): AUROC 0.8280–0.8457.
  Across the three variants BMI-Obese disparity stable 15/15; Age-60+ direction never reverses,
  significance lost 9/12.
- **Source artifact:** `results/sensitivity/alternative_threshold_8p0kPa_results.csv`,
  `sensitivity_discrimination_calibration_results.csv`, `primary_vs_sensitivity_comparison.csv`.
- **Phase:** Deferred sensitivity plan (executed 2026-08-20). **Authority:** AUTHORITATIVE
  (EXECUTED AND VERIFIED). **Reproducibility:** ESTABLISHED.
- **Limitation:** 8.0-kPa is relabel-only (no retraining/recalibration/conformal). 8.2 kPa is
  primary; 8.0 kPa is sensitivity.
- **Manuscript wording:** "The primary discrimination, calibration, and obese-BMI fairness
  findings reproduced across an alternative 8.0-kPa threshold and two independently constructed
  cohorts; the older-age disparity's direction reproduced but its statistical significance did
  not."

## A11. Targeted multiple imputation (Non-Hispanic Black selection-bias question)

- **Claim:** Fold-embedded `IterativeImputer(BayesianRidge, sample_posterior=True)`, m=5, MI
  pool N=7,768 (615 recovered). ΔAUROC < 0.007, ΔBrier < 0.003 all models; NHB sensitivity
  changes ≤ ±4.2 pp, all CIs include 0; BH-adjusted p = 0.978 for all five models. 4/5 STABLE,
  MLP INDETERMINATE.
- **Source artifact:** `results/sensitivity/mi_black_subgroup_comparison.csv`,
  `results/sensitivity/multiple_imputation_diagnostics.csv`.
- **Source script:** `src/mi_02_black_subgroup_comparison.py`,
  `src/mi_03_black_subgroup_inference.py`.
- **Phase:** MI sensitivity (narrow scope). **Authority:** AUTHORITATIVE (EXECUTED AND VERIFIED,
  NARROW SCOPE). **Reproducibility:** ESTABLISHED for this analysis.
- **Limitation:** Scope is the NHB selection question only; BH q=0.978 is a correction-ceiling
  artifact on a 5-member family, not evidence of equivalence.
- **Manuscript wording:** "A targeted multiple-imputation analysis of the differential
  Non-Hispanic Black exclusion did not materially change discrimination or the subgroup
  sensitivity estimate."

## A12. Interpretability

- **Claim:** ALT, AST, BMI, and Age are the top four predictors across all five model families
  (permutation importance + logistic coefficients).
- **Source artifact:** `results/tables/interpretability_permutation_importance.csv`,
  `interpretability_logistic_coefficients.csv`.
- **Phase:** Reliability/interpretability extension. **Authority:** AUTHORITATIVE.
- **Limitation:** Association with model output, not causal.

## A13. M4b prespecified N0 selection (process authoritative; outcome exploratory)

- **Claim:** 5-fold CV **on the calibration split only** (no test labels) selected N0* = 0
  (w = 1.0) for all five models. The old N0=100 test-set sweep is SUPERSEDED.
- **Source artifact:** `results/diagnostics/stage1/m4b_n0_cv_selection.csv`,
  `results/tables/m4b_prespecified_n0_final_results.csv`.
- **Source script:** `src/sens_12_m4b_n0_prespecified.py`.
- **Phase:** Stage-1 diagnostics. **Authority:** AUTHORITATIVE for the selection *process* and
  for freezing N0=0 for temporal use; the coverage *result* is EXPLORATORY (see
  `EXPLORATORY_RESULTS.md`).
- **Limitation:** The joint-cell coverage outcome is exploratory and did not replicate
  temporally (1/5 models).

---

### Authoritative headline numbers block (for manuscript methods/results)

```
CAND_1: N=7,153 | 666 pos | 6,487 neg | 9.31%
Train/test: 5,007 / 2,146 (466 / 200 pos)
Conformal proper-train / calibration: 4,005 / 1,002 (373 / 93 pos); k=903
Baseline test AUROC: 0.8229–0.8429 (LR .8334 RF .8343 XGB .8429 LGBM .8394 MLP .8229); 0/10 FDR-sig
OOF calibration intercepts: -2.243 to -0.281 → post-Platt locked-test ECE 0.011–0.026, AUROC unchanged
Normal-BMI vs Obese sensitivity deficit: 27.1–47.7 pp, 5/5 FDR-significant (q ≤ 0.006)
Age-60+ sensitivity deficit: negative 5/5, FDR-significant 4/5 (not Logistic)
Conformal: marginal 88.12–90.82% | BMI-Obese 76.8–82.3% | Age-60+ 81.1–85.6% | Obese∩60+ 64.97–75.17%
Phase 7 Mondrian: 5/9 targets nominal; XGBoost marginal 93.4% (+5.27 pp breach)
Phase 8 NHB holdout: AUROC 0.7719–0.7893 (within-NHANES)
Temporal (separate work): N=4,910 | 563 pos | 11.4664% | AUROC 0.7765–0.7824 | BMI-Obese deficit 62.8–71.9 pp | PARTIAL TEMPORAL REPLICATION
```
