# VERIFIED WITH LIMITATIONS

Read-only audit, 2026-08-27. Each item is a real, executed analysis whose conclusion the
repository supports **only within a stated scope**. For each: WHAT IS SUPPORTED / WHAT IS NOT
SUPPORTED. These map to the `VERIFIED_WITH_LIMITATIONS` authority tier and
`MANUSCRIPT_READY_WITH_QUALIFICATION` manuscript tier.

---

## V1. Age-60+ sensitivity deficit

**Source:** `results/fairness/fairness_inference.csv`,
`results/sensitivity/primary_vs_sensitivity_comparison.csv`;
`documentation/fairness_bmi_investigation/PHASE2_DIAGNOSTIC_REPORT.md`. **Phase:** Project Phase 5
+ diagnostics.

**Supported:**
- Age-60+ sensitivity is lower than Age-40–59 in **all 5** primary models (−8.6 to −14.7 pp).
- The deficit is FDR-significant in **4/5** (RF, XGBoost, LightGBM, MLP); Logistic is not
  significant (reported FDR p ≈ 0.18–0.20).
- Direction never reverses across the 8.0-kPa relabel, CAND_2, or CAND_3.
- The mechanism differs from BMI: subgroup thresholding **worsens** the Age gap (26–133%),
  indicating a non-threshold mechanism.

**Not supported:**
- 5/5 FDR significance (that is an INVALID historical claim — see `SUPERSEDED_INVALID_RESULTS.md`).
- Stable statistical significance: it is lost in 9/12 sensitivity-cohort instances where it held
  at the primary specification.
- Monotone "older is worse" — continuous-age splines and fine bands show a non-monotonic curve
  peaking near 65 with no further decline at 70+.
- Any causal interpretation.

**Manuscript wording:** "Older participants (≥60 y) showed consistently lower sensitivity
(direction robust across all models and sensitivity analyses), but the finding was statistically
significant in four of five models and its significance was specification-sensitive."

---

## V2. Project Phase 7 — FDR-gated Mondrian conformal mitigation (outcome)

**Source:** `results/mitigation/test_set_mitigation_final.csv`,
`marginal_coverage_before_after.csv`, `threshold_precedence_audit.csv`,
`documentation/mitigation/phase7_bmi_age_overlap_interpretation.md`. **Phase:** Project Phase 7.

**Supported:**
- 5/9 qualifying model×subgroup targets reached nominal (≥90%) coverage after group-wise
  recalibration.
- Logistic correctly received a BMI-only rule (its Age-60+ fairness result was not
  FDR-significant) — by design, not oversight.
- The intervention is a genuine, documented, pre-specified group-conditional conformal method.

**Not supported:**
- Resolution of the subgroup coverage problem: RF/Obese, XGBoost/Obese, LightGBM/Obese,
  LightGBM/60+ remained below target.
- Preservation of marginal-coverage tolerance: XGBoost rose to ~93.4%, a **+5.27 pp breach** of
  the pre-specified ±5 pp limit.
- Joint / intersectional mitigation: in the 294-person BMI-Obese ∩ Age-60+ overlap the Age rule
  overwrites the BMI rule (last-write-wins), so the overlap is not jointly mitigated.
- Any claim that Phase 7 fixed the BMI **classification** (sensitivity) disparity — it targets
  conformal coverage only.

**Manuscript wording:** "Mondrian recalibration partially, not fully, repaired subgroup
coverage (5/9 targets), with a documented XGBoost marginal-coverage breach and sequential rather
than joint handling of the intersectional population."

---

## V3. Corrected BMI-investigation Phase 3 — BMI-sensitivity mitigation

**Source:** `results/fairness_bmi_investigation/phase3_corrected/*.csv`,
`documentation/fairness_bmi_investigation/phase3_corrected/PHASE3_CORRECTED_MITIGATION_REPORT.md`,
`PHASE3_AUDIT_REPORT.md`. **Phase:** BMI-investigation Phase 3. **Authority:**
VERIFIED_WITH_LIMITATIONS.

**Supported:**
- On an independent deterministic split of the 5,007 OOF rows, four candidate strategies
  (BMI thresholding; BMI-specific Platt; BMI×Age thresholds with explicit small-cell fallback;
  combined BMI-Platt + BMI thresholds) were evaluated against a pre-declared multi-metric gate
  (full-cohort sensitivity/specificity within 5 pp; Brier within +0.01; Age-60+ gap not worse by
  >5 pp), with absolute BMI gap as a secondary criterion.
- The gate selected the **original frozen model** for Logistic, RF, XGBoost, LightGBM, and
  **BMI-specific Platt for MLP only**.
- Locked-test confirmation: MLP BMI gap 39.03 → 34.48 pp; no meaningful AUROC/Brier change;
  overall specificity 0.664 → 0.676.
- Conclusion: **NO ACCEPTABLE MITIGATION IDENTIFIED.**

**Not supported:**
- Any universal / cross-family BMI mitigation.
- Statistical significance or equivalence of candidate differences (no formal inference
  produced).
- That the MLP calibration change is a fairness "fix" — it is a modest single-model gap
  reduction with unchanged classification decisions on the other four.
- Causal claims.

**Manuscript wording:** "A dedicated, independently split re-analysis of four BMI-targeted
mitigation strategies identified no strategy meeting the pre-specified multi-metric acceptance
criteria across model families."

---

## V4. Corrected BMI-investigation Phase 4 — subgroup calibration

**Source:** `results/fairness_bmi_investigation/phase4_corrected/*.csv`,
`documentation/fairness_bmi_investigation/PHASE4_CORRECTED_FINAL_AUDIT_REPORT.md` (**Decision B**),
`PHASE4_CORRECTED_REPORT.md`. **Phase:** BMI-investigation Phase 4.

**Supported:**
- Corrected implementation uses equal-frequency ECE (matching the frozen calibration protocol;
  11/11 `ece_validation.csv` PASS, max deviation ≈1e-17), independent 2,504/2,503 fit/eval
  separation, explicit BMI-first→age→global fallback for non-estimable cells, and both conformal
  arms actually map probabilities before recomputing the split-conformal threshold.
- OOF gate choices: `global_platt` for Logistic and MLP (subgroup ECE worsened);
  `subgroup_platt_bmi_age` for RF, XGBoost, LightGBM (subgroup ECE improved, safety constraints
  held).
- Conclusion: **no acceptable subgroup-calibration improvement** for the BMI fairness/reliability
  objective.

**Not supported:**
- That subgroup calibration improves BMI **classification** fairness — decisions use the
  unchanged raw probability vs the frozen threshold, so classification gaps are **identical**
  (locked-test 47.66 / 31.62 / 31.36 / 27.08 / 39.03 pp) for both candidates.
- Joint intersectional calibration — BMI×Age rows are descriptive under the fallback precedence,
  not from a jointly fitted calibrator.
- Statistical superiority/equivalence of candidates (no p-value / comparative CI produced).
- Fully proven runtime test-access order (no runtime event log; static control-flow only).
- Generation provenance of `phase4_corrected_ece_validation.csv` (byte-identical duplicate not
  written by the current script).
- Population-level subgroup conformal coverage (development sample 501/501; not external
  validation).

**Manuscript wording:** "Subgroup-specific probability calibration did not improve subgroup
reliability or fairness beyond global Platt scaling and left classification decisions unchanged."

---

## V5. BMI-investigation Phase 5 — MI conformal reliability sensitivity

**Source:** `results/fairness_bmi_investigation/phase5_mi_conformal/*.csv`,
`documentation/fairness_bmi_investigation/PHASE5_MI_CONFORMAL_REPORT.md`,
`PHASE5_FINAL_AUDIT_REPORT.md`. **Phase:** BMI-investigation Phase 5.

**Supported (descriptively):**
- With `IterativeImputer(BayesianRidge, sample_posterior=True)` embedded in the model pipeline
  and fit only on each expanded proper-training partition (4,620 = 4,005 + 615), across 5 imputed
  datasets and 5 models, overall test coverage changes vs frozen complete-case are small
  (descriptive means −0.53 to +0.97 pp).
- **BMI-Obese coverage stays below 90% in every model and every imputation** (≈0.776–0.828).
- Non-Hispanic Black coverage reported per imputation (≈0.871–0.898).
- Conclusion: **MI conformal reliability is consistent with complete-case results** (descriptive).
- Locked test evaluated exactly once; manifest frozen first; test hash matched.

**Not supported:**
- Executable reproducibility: **`LINEAGE NOT FOUND IN REPOSITORY`** — no committed MI-conformal
  source / models / scores / prediction sets / runtime log.
- Any pooled inferential estimate — the authorized MI protocol defines no Rubin-style pooling for
  prediction-set outputs.
- Equivalence of MI and complete-case (no equivalence test).
- That this replaces the primary complete-case analysis (it is an exploratory missing-data
  sensitivity layer).

**Manuscript wording (only if cited):** "An exploratory multiple-imputation sensitivity analysis
of conformal reliability produced subgroup coverage consistent with the complete-case results
(descriptive; the analysis pipeline could not be fully reconstructed from committed artifacts)."

---

## V6. BMI-investigation Phase 6 — full 8.0-kPa robustness

**Source:** `results/fairness_bmi_investigation/phase6_8kpa_robustness/*.csv`,
`documentation/fairness_bmi_investigation/PHASE6_8KPA_ROBUSTNESS_REPORT.md` (**"SOME MAJOR
FINDINGS ARE THRESHOLD-SENSITIVE"**). **Phase:** BMI-investigation Phase 6.

**Supported:**
- Same CAND_1 cohort, ten predictors, five frozen families, inherited hyperparameters, fresh OOF
  Platt, fresh split-conformal, new outcome `LUXSMED ≥ 8.0 kPa` (715 positives; 49 relabelled;
  independently derived label agrees with the pre-existing sensitivity column).
- Selection manifest written before any test access; locked test touched once.
- Discrimination and the BMI-Obese disparity direction are robust to the 8.0-kPa cutoff.

**Not supported:**
- That all findings are threshold-invariant — the report's own conclusion is that **some are
  threshold-sensitive** (Age-60+ significance, some conformal detail; see
  `phase6_8kpa_vs_82_comparison.csv`).
- That 8.0 kPa is or supersedes the primary analysis — **8.2 kPa remains PRIMARY**.
- Full lineage: frozen 8.2-kPa protocol commit and model-artifact manifest =
  `NOT FOUND IN REPOSITORY`.
- Any equivalence claim between 8.0 and 8.2 (none made; none supported).

**Manuscript wording:** "A full re-run of the pipeline at an 8.0-kPa cutoff left discrimination
and the obese-BMI disparity intact but confirmed that the older-age disparity's significance is
threshold-sensitive."

---

## V7. BMI-investigation Phase 7 — XGBoost retuning + joint-mitigation audit

**Source:** `results/fairness_bmi_investigation/phase7_mitigation_cleanup/*.csv`,
`documentation/fairness_bmi_investigation/PHASE7_MITIGATION_CLEANUP_REPORT.md`,
`PHASE7_MITIGATION_CLEANUP_VERIFICATION.md`. **Phase:** BMI-investigation Phase 7.

**Supported:**
- XGBoost candidates were exactly the authorized Phase 3 family, fit on OOF/development only,
  manifest frozen before a single locked-test confirmation.
- **NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED** — no retuned candidate passed the multi-metric
  gate; the original frozen XGBoost is retained.
- The prior `joint_intersectional_mitigation.csv` implementation is a **genuine** joint
  Obese-AND-60+ calibration slice (N=138: 30 positive, 108 negative), not sequential — audited,
  not modified.

**Not supported:**
- That the XGBoost conformal marginal-coverage breach is resolvable within scope (it is not:
  gap-closing candidates cost 11–22 pp overall sensitivity or flip the breach).
- Primary status for the joint artifact — it is **`EXPLORATORY_GENUINE_JOINT`**; its generating
  script / manifest / runtime log = `NOT FOUND IN REPOSITORY`; XGBoost and LightGBM exceed the
  ±5 pp marginal tolerance in it.

**Manuscript wording:** "Attempts to retune XGBoost within the authorized model family did not
remove its post-mitigation coverage-tolerance breach; a genuinely joint intersectional
calibration exists only as an exploratory artifact with its own tolerance breaches."

---

## V8. Reliability extension — Decision Curve Analysis and co-occurrence

**Source:** `results/reliability_extension/*.csv`, `RELIABILITY_EXTENSION_RESULTS_REPORT.md`.
**Phase:** reliability extension.

**Supported:**
- DCA: all five models exceed "treat all" / "treat none" across the clinical threshold range
  (~p_t 0.05–0.35), at population level and within BMI-Obese and Age-60+.
- Co-occurrence of the Phase 5 fairness flags and the Phase 6 coverage flags is descriptively
  positive.

**Not supported:**
- A confirmed statistical co-occurrence association — pooled ρ=0.4076 has raw p=0.0020 but
  category-block permutation p=0.1195 (**not** confirmed); the precision-filtered ρ=0.7043 is a
  sensitivity-only subset.
- Any claim of clinical utility beyond net-benefit curves on this internal cohort.

---

## Consolidated statement for the manuscript

Every item above is a completed analysis that **narrows** rather than establishes a positive
claim. The recurring pattern: interventions that improve one metric (an ECE, one model's BMI gap,
a joint-cell coverage) do **not** meet the pre-specified multi-metric bar, do **not** generalize
across model families, and in several cases do **not** replicate temporally. None may be reported
as a successful mitigation.
