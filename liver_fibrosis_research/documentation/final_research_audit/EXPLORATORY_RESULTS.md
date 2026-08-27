# EXPLORATORY RESULTS

Read-only audit, 2026-08-27. These analyses are explicitly EXPLORATORY per
`documentation/final_research_state/EXPLORATORY_RESULTS_REGISTER.md`,
`results/diagnostics/stage0_decision_report.md`, `stage1_decision_report.md`, and the frozen
`statistical_analysis_plan.md` Governing Rule ("an EXPLORATORY-tier result may not be promoted to
a primary/secondary conclusion"). For each: purpose · result · limitation · manuscript
eligibility · required wording.

---

## E1. Continuous BMI restricted cubic splines (D02)

- **Purpose:** test whether the BMI sensitivity gap is an artifact of the categorical cutpoints.
- **Result:** OOF-fit RCS (4 knots): sensitivity rises monotonically ≈0.43 (Normal) → ≈0.96
  (Obese III) while conformal coverage decays ≈0.98 → ≈0.55 across the BMI range
  (`results/diagnostics/continuous_bmi_metrics.csv`).
- **Limitation:** model-specific spline fits; wide uncertainty at BMI extremes; descriptive.
- **Manuscript:** may be mentioned as a supporting mechanistic illustration.
- **Wording:** "The disparity was a continuous gradient across BMI, not an artifact of the
  category boundaries, with a strong threshold component."

## E2. Continuous Age splines (D03) + fine age bands

- **Purpose:** test the shape of the age effect.
- **Result:** non-monotonic sensitivity curve peaking ≈65 y, **no further decline at 70+**; fine
  bands show 70+ sensitivity (0.71–0.82) ≥ 60–69 (0.70–0.84) in 3/5 models
  (`results/diagnostics/continuous_age_metrics.csv`, `fine_age_band_metrics.csv`).
- **Limitation:** small cells at the oldest ages; descriptive.
- **Manuscript:** may be mentioned to qualify the Age-60+ finding (disproves "older is
  monotonically worse").
- **Wording:** "The age-related sensitivity deficit was non-monotonic and did not worsen beyond
  70 years."

## E3. Subgroup-specific recalibration + re-quantiling (D04)

- **Purpose:** test whether calibration causes the coverage failure.
- **Result:** subgroup Platt changed Brier by <0.0005 and coverage by ≤0.68 pp
  (`results/diagnostics/stage0/subgroup_recalibration_metrics.csv`); re-deriving nonconformity
  quantiles within subgroups restored Obese-BMI coverage to ≈89.9–91.6% but left Age-60+ at
  ≈86.7–88.0% (`subgroup_recalibration_conformal_metrics.csv`).
- **Limitation:** development-set estimates; not a population guarantee.
- **Manuscript:** may be mentioned — it supports the point that conformal validity depends on
  residual variance, not probability calibration.
- **Wording:** "Better subgroup probability calibration did not improve subgroup conformal
  coverage; re-deriving subgroup nonconformity quantiles did (for the obese group only)."

## E4. Group-specific Youden thresholds (D05 / D07)

- **Purpose:** test whether threshold placement drives the disparities.
- **Result:** subgroup thresholds **reduced** the BMI sensitivity gap by 49–69% (to 10.4–16.1
  pp) but **widened** the Age-60+ gap by 26–133%; class-balanced models showed 51–80 pp
  subgroup sensitivity swings; ~38–40 pp specificity cost in Normal-BMI
  (`results/diagnostics/group_specific_threshold_metrics.csv`).
- **Limitation:** exploratory; large specificity/false-positive cost; not a deployable rule.
- **Manuscript:** may be reported as the "Two-Mechanism" diagnostic, clearly labelled
  exploratory and non-clinical.
- **Wording:** "Exploratory subgroup-specific thresholds indicated the BMI disparity is
  threshold-driven and the age disparity is not; neither was adopted, and both incurred large
  specificity costs."

## E5. Equal Opportunity post-processing (D06)

- **Purpose:** diagnostic test of TPR equalisation.
- **Result:** ~50–80 pp target-group sensitivity gain in class-balanced models at ~38–40 pp
  specificity cost; ≈399 excess false-positive referrals per 1,000 normal-weight screened; MLP
  sensitivity *decreased* slightly (different mechanism). No change to probabilities, Brier,
  AUROC (`results/diagnostics/stage1/correct_fairness_postprocessing_results.csv`,
  `clinically_interpretable_fairness_costs.csv`).
- **Limitation:** an earlier implementation (`sens_07`) had a raw/recalibrated scale-mismatch
  defect and is UNVERIFIED/UNTRUSTED; the corrected diagnostic (`correct_fairness_postprocessing_results.csv`)
  is the one to cite.
- **Manuscript:** may be mentioned to show naive parity interventions are clinically
  unacceptable.
- **Wording:** "Equalising true-positive rates by post-processing imposed a ~40-percentage-point
  specificity penalty (~399 extra false positives per 1,000 normal-weight patients) and was not
  pursued."

## E6. Fairness–specificity Pareto + clinical cost analysis

- **Purpose:** quantify the fairness/specificity trade-off.
- **Result:** equalising BMI-subgroup sensitivity drops Normal-BMI specificity ~76% → ~36–40%
  (`results/tables/fairness_specificity_pareto_results.csv`).
- **Manuscript:** supporting, exploratory.

## E7. Faithful AFCP (Zhou & Sesia 2024)

- **Purpose:** an adaptive full-conformal alternative to Mondrian.
- **Result:** BMI-Obese coverage 89.92–91.51%, Age-60+ 88.53–90.42%, intersection 86.05–89.46%,
  overall 92.78–93.66%, set sizes 1.05–1.27
  (`results/diagnostics/stage1/afcp_faithful_results.csv`).
- **Limitation:** the older KNN-AFCP is INVALID/SUPERSEDED; the faithful version's final
  narrative status is `CONFLICT UNRESOLVED IN REPOSITORY` (blocked vs conditional-frozen);
  intersectional coverage still below target; overall coverage exceeds 90%.
- **Manuscript:** mention only as an exploratory alternative; **no superiority claim** permitted.
- **Wording:** "A faithful adaptive-conformal method achieved near-target single-attribute
  subgroup coverage but still under-covered the intersection; it was not adopted."

## E8. Joint intersectional conformal — Method (b), Method (c), M4b N0=0

- **Purpose:** restore BMI-Obese ∩ Age-60+ coverage.
- **Result:** on CAND_1, intersectional coverage ≥90% for 4–5/5 models (Method b 90.8–94.9%;
  M4b N0=0: LR 90.82, RF 92.86, XGB 91.50, LGBM 89.46, MLP 90.82); minimal set-size cost
  (+0.09). Methods b and c differ by up to 4.08 pp (raw-cell vs finite-sample quantile);
  both code-clean, both preserved.
- **Limitation:** joint calibration cell N=138 (30 positive); XGBoost/LightGBM breach the ±5 pp
  marginal tolerance (+6.80 / +5.50 pp); generating lineage for the joint
  artifact `NOT FOUND IN REPOSITORY`; stale status-CSV conflict (C2).
- **Manuscript:** EXPLORATORY only; must not be presented as a solution to the intersectional
  coverage problem.
- **Wording:** "An exploratory joint-cell conformal calibration restored intersectional coverage
  on the primary cohort for most models but breached the marginal-coverage tolerance for two."

## E9. M4b shrinkage sensitivity / coverage–set-size trade-off / LightGBM failure analysis

- **Purpose:** characterise M4b behaviour.
- **Result:** intersectional coverage decays smoothly 91.5% (N0=0) → 82.3% (N0=500) for XGBoost;
  LightGBM's 89.46% = 263/294 (2 cases short, 95% CI contains 90%), attributed to `max_depth=4`
  histogram-bin quantisation near the quantile boundary.
- **Manuscript:** supporting, exploratory.

## E10. Co-occurrence and Decision Curve Analysis

Covered in `VERIFIED_WITH_LIMITATIONS.md` V8. Exploratory extension; the permutation-based
co-occurrence result is **not confirmed**.

## E11. Intersectional exploratory fairness metrics

- **Source:** `results/fairness/intersectional_exploratory_metrics.csv`. Pre-specified cells
  computed descriptively; no post-hoc FDR claims. Manuscript: supporting only.

## E12. Conformal selective deferral (Amendment #17) — pre-registered, DEVELOPMENT-STAGE NEGATIVE

- **Purpose:** test whether abstaining on flagged-uncertain cases and referring them to
  elastography restores BMI-Obese / Age-60+ conformal coverage.
- **Result:** on the conformal-calibration partition (N=1,002; **locked test not touched**), none
  of the pre-registered candidates (3a defer two-class sets; 3b defer weak singletons; 3d/3e
  group-conditional Mondrian) meets the multi-metric core gate for any of the 5 models. 3a makes
  BMI-Obese coverage *worse* (0.58–0.82). 3b lifts under-covered groups to ~0.90 but defers
  15–40% overall and fails the retained-marginal-coverage gate. 3d (Mondrian) restores BMI-Obese
  and Age-60+ to ≥ 0.88 for 5/5 with zero deferral but raises retained marginal coverage to
  0.94–0.95 and leaves well-served subgroups > 0.95 (*levelling down* required to fix).
  `results/selective_deferral/phase3_candidate_metrics.csv`,
  `frozen_deferral_rule_manifest.json`.
- **Limitation:** development-stage; per the pre-registered gate the locked test was not accessed,
  so there is no confirmatory test-set number. No post-hoc gate relaxation permitted.
- **Manuscript:** report as **NO IMPROVEMENT** in the mitigation results (Table 4 / §3.7) with the
  mechanism (under-coverage = confidently-scored wrong singletons, not uncertain sets → post-hoc
  deferral cannot fix it → training-time intervention indicated). Not "exploratory" — it is a
  pre-registered negative — but listed here for completeness alongside the other mitigation
  attempts. `documentation/selective_deferral_mitigation/*`.

---

## Governing rule (do not violate)

No item on this page may be cited as primary or secondary evidence. Each must carry the word
"exploratory" (or "diagnostic") in the manuscript and must not be used to claim that any
disparity was mitigated, that calibration is subgroup-valid, or that any conformal method
achieves conditional validity.
