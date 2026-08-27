# Secondary Severity-Graded Outcomes — Results Report

**Analysis:** Pre-registered SECONDARY analysis (`documentation/phase2/statistical_analysis_plan.md`
SECONDARY item 2; `documentation/phase2/primary_outcome_definition.md`;
`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` row 17) — severity-graded outcomes.
**Mode:** RELABEL-ONLY DESCRIPTIVE PASS. Mirrors the 8.0-kPa check (`src/sens_03_alternative_threshold.py`,
Amendment #13). Executed under **Amendment #15**.
**Date:** 2026-08-27.
**Script:** `src/sens_13_secondary_severity_outcomes.py`.
**Outputs:** `results/sensitivity/secondary_severity_outcomes_results.csv`,
`results/sensitivity/secondary_severity_outcomes_9p7_bmi_age_fairness.csv`,
`results/sensitivity/secondary_severity_outcomes_lineage.json`.

---

## 1. What was and was not done

| Aspect | Status |
|---|---|
| Cohort | CAND_1 primary (N=7,153), unchanged |
| Predictors | 10 frozen primary predictors, unchanged |
| Models | 5 frozen Phase 3 models — **not refit** |
| Platt recalibration | frozen 8.2-kPa parameters **applied unchanged — not re-fit** |
| Conformal calibration | **not repeated** |
| Locked test set | **not re-accessed for any model fitting**; Youden thresholds re-derived on frozen OOF predictions relabeled to each outcome |
| Outcome relabelled to | `outcome_secondary_advanced_9.7kPa` (411 pos / 5.75% overall; **124 test positives**), `outcome_secondary_cirrhosis_13.6kPa` (177 pos / 2.47% overall; **59 test positives**) |
| ≥9.7 kPa reporting | discrimination + calibration (raw and frozen-Platt) + BMI/Age sensitivity disparity (descriptive, low power) |
| ≥13.6 kPa reporting | discrimination + calibration **only** — 59 test positives is too few for any subgroup statement |
| Multiplicity | **no FDR** — descriptive secondary pass, CI-only, matching `sens_03` |

**Rationale for relabel-only rather than per-outcome retraining:** a severity-threshold shift that
adds no new predictors cannot change model-family or preprocessing selection. Full per-outcome
retraining is not justified and was not performed. Recorded in Amendment #15 and
`documentation/final_research_audit/FINAL_REMAINING_WORK_REGISTER.md` item 10.

---

## 2. Discrimination

### Advanced fibrosis (≥ 9.7 kPa), 124 test positives

| Model | ROC-AUC (95% CI) | PR-AUC | Sensitivity | Specificity | PPV |
|---|---|---:|---:|---:|---:|
| Logistic | 0.862 (0.829–0.891) | 0.309 | 0.790 | 0.768 | 0.173 |
| Random Forest | 0.846 (0.812–0.878) | 0.268 | 0.806 | 0.717 | 0.149 |
| XGBoost | 0.856 (0.822–0.889) | 0.305 | 0.831 | 0.758 | 0.174 |
| LightGBM | 0.850 (0.815–0.883) | 0.296 | 0.815 | 0.753 | 0.168 |
| MLP | 0.851 (0.814–0.883) | 0.299 | 0.887 | 0.586 | 0.116 |

### Cirrhosis (≥ 13.6 kPa), 59 test positives

| Model | ROC-AUC (95% CI) | PR-AUC | Sensitivity | Specificity | PPV |
|---|---|---:|---:|---:|---:|
| Logistic | 0.862 (0.810–0.909) | 0.208 | 0.746 | 0.773 | 0.085 |
| Random Forest | 0.841 (0.787–0.889) | 0.207 | 0.763 | 0.760 | 0.083 |
| XGBoost | 0.847 (0.790–0.898) | 0.243 | 0.814 | 0.745 | 0.083 |
| LightGBM | 0.842 (0.780–0.894) | 0.237 | 0.797 | 0.735 | 0.078 |
| MLP | 0.858 (0.799–0.907) | 0.220 | 0.881 | 0.655 | 0.067 |

**Reading.** Rank discrimination for both severity-graded outcomes is comparable to, and if
anything slightly above, the primary 8.2-kPa result (test AUROC 0.823–0.843) — expected, since
more severe disease is easier to separate from the rest of the cohort. As at 8.2 kPa, no model
family is distinguishable from the others (CIs overlap heavily across all five). PR-AUC and PPV
fall as prevalence falls (PPV 0.12–0.17 at ≥9.7 kPa; 0.07–0.09 at ≥13.6 kPa): at a Youden
operating point these thresholds flag many false positives per true cirrhosis case. The models
are screening aids, not stand-alone diagnostics, and this is more pronounced at lower prevalence.

---

## 3. Calibration

Calibration-in-the-large (intercept, slope) and Brier / decile-ECE, computed on the frozen test
probabilities relabelled to each outcome. **Raw** = Phase 3 output; **Platt-recal** = frozen
8.2-kPa Platt transform applied unchanged.

### Advanced fibrosis (≥ 9.7 kPa)

| Model | Raw intercept | Raw slope | Raw ECE | Platt-recal intercept | Platt-recal slope | Platt-recal ECE |
|---|---:|---:|---:|---:|---:|---:|
| Logistic | −2.87 | 1.00 | 0.33 | −0.76 | 0.94 | 0.039 |
| Random Forest | −2.59 | 1.34 | 0.28 | −0.50 | 1.12 | 0.042 |
| XGBoost | −2.83 | 1.25 | 0.29 | −0.38 | 1.20 | 0.041 |
| LightGBM | −2.83 | 1.27 | 0.30 | −0.37 | 1.20 | 0.041 |
| MLP | −0.91 | 1.03 | 0.06 | −0.57 | 1.24 | 0.061 |

### Cirrhosis (≥ 13.6 kPa)

| Model | Raw intercept | Raw slope | Raw ECE | Platt-recal intercept | Platt-recal slope | Platt-recal ECE |
|---|---:|---:|---:|---:|---:|---:|
| Logistic | −3.64 | 0.81 | 0.36 | −1.92 | 0.77 | 0.069 |
| Random Forest | −3.46 | 1.36 | 0.31 | −1.36 | 1.13 | 0.072 |
| XGBoost | −3.70 | 1.24 | 0.32 | −1.27 | 1.19 | 0.071 |
| LightGBM | −3.71 | 1.28 | 0.33 | −1.24 | 1.21 | 0.071 |
| MLP | −1.84 | 0.99 | 0.09 | −1.50 | 1.20 | 0.091 |

(Full raw and recalibrated intercept/slope/Brier/ECE for all 10 rows are in
`secondary_severity_outcomes_results.csv`.)

**Reading.** Two points, both expected and both consistent with the primary calibration finding:

1. **Raw over-prediction is worse, not better, at the rarer outcomes.** The class-balanced models'
   raw intercepts move further negative as prevalence falls (−2.6 to −3.7 at these thresholds vs
   −1.9 to −2.2 at 8.2 kPa). The unweighted MLP again shows the smallest raw shift.
2. **The frozen 8.2-kPa Platt recalibration does not transport to a different outcome
   definition.** Applying it unchanged leaves residual over-prediction: recalibrated intercepts of
   −0.4 to −0.8 for ≥9.7 kPa and −1.2 to −1.9 for ≥13.6 kPa, with decile-ECE rising to ~0.04 and
   ~0.07–0.09 respectively (vs ≈0.01–0.03 for the primary outcome). A recalibration map is
   specific to the base rate it was fit against; a severity-graded outcome at a different
   prevalence needs its own recalibration. **No recalibration was fit here** — doing so would be
   beyond a relabel-only pass.

---

## 4. Fairness — Advanced fibrosis (≥ 9.7 kPa) only

BMI-Obese vs Normal-BMI and Age-60+ vs Age-40–59 sensitivity disparity (percentage points), at
the re-derived Youden operating point, 2,000-resample bootstrap 95% CI, **no FDR**.

| Model | BMI Obese−Normal (pp) [95% CI] | Age 60+ − 40–59 (pp) [95% CI] |
|---|---|---|
| Logistic | +35.6 [+4.4, +66.4] | −1.5 [−17.4, +14.8] |
| Random Forest | +17.4 [−9.8, +48.6] | −5.0 [−19.2, +10.3] |
| XGBoost | +19.6 [−7.4, +49.6] | −10.0 [−23.2, +3.7] |
| LightGBM | +19.6 [−8.0, +49.9] | −10.6 [−25.0, +4.4] |
| MLP | +22.9 [−3.9, +53.8] | −2.3 [−14.2, +10.2] |

**Power caveat — read before interpreting.** The Normal-BMI reference cell has **11 test
positives** (and 27 at 8.2 kPa was already the primary study's smallest interpretable cell). The
Age-40–59 cell has 40. These CIs are wide by construction.

**Reading.** The **direction** of the BMI disparity is preserved — Obese patients are detected
more sensitively than Normal-BMI patients for advanced fibrosis in 5/5 models (+17 to +36 pp) —
consistent with the primary 8.2-kPa finding (Normal-BMI under-detection) and its 8.0-kPa / CAND_2
/ CAND_3 replications. Only the logistic model's CI excludes zero; the rest do not, which is a
**power** statement (11 positives), not evidence of absence. The Age-60+ disparities are small,
negative in 4/5, and every CI includes zero — consistent with the primary Age-60+ finding being
directionally suggestive but statistically fragile. **This pass does not add independent
statistical support for either subgroup finding; it shows the primary pattern is not contradicted
at the severity-graded outcome.**

---

## 5. Bottom line

- The pre-registered SECONDARY severity-graded outcome now has a result artifact and a tracked
  status. It was silently absent from every prior register and master report; that gap is closed.
- **Discrimination** for advanced fibrosis and cirrhosis is comparable to the primary outcome;
  no model family is superior.
- **Raw calibration** is worse at lower prevalence, and the **frozen 8.2-kPa recalibration does
  not transport** to a different outcome definition — a clean illustration of the primary study's
  point that recalibration is prevalence/outcome-specific, not a one-time global fix.
- The **BMI disparity direction** is preserved; **statistical support is not added** here
  (Normal-BMI n=11 positives). **Age-60+** remains fragile.
- **DO NOT** report these as primary or secondary *performance* claims of a deployable
  severity-staging model — they are a relabel-only descriptive check on frozen 8.2-kPa models.
  **DO NOT** fit a per-outcome recalibration or retrain without a new protocol amendment.
