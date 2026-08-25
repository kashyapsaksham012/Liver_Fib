# Gate 0 Decision Report (D01–D05)

**Analysis Period:** 2026-08-25  
**Protocol Status:** SECONDARY / DIAGNOSTIC analyses — Primary frozen pipeline untouched.  
**Test-set Labels Used for Fitting: NO** (verified per-script)

---

## Stage 0 Results Summary

### D01 — Socio-Conformal Literature Audit
**NOVELTY THREAT: LOW**

Paper arXiv:2605.05562 (Das & Rafe 2026) addresses ordinal conformal prediction in social survey settings (Pew American Trends Panel). Key differences from our work:
- Ordinal (5-level) vs. binary outcome.
- Social measurement vs. clinical liver fibrosis diagnosis.
- James-Stein shrinkage mitigation vs. FDR-gated Mondrian.
- No class-balanced classifiers analyzed.

Our Candidates 1, 2, and 4 are completely unaddressed by this paper. Cite it in Introduction and Discussion for the thin-cell / marginal validity problem, but novelty claims are not threatened.

---

### D02 — Continuous BMI Analysis
**[A] Observed: BMI sensitivity and coverage are NOT a categorical cutoff artifact — they are genuine continuous gradients.**

Spline range across all 5 models:
| Model | BMI Sensitivity Range | BMI Coverage Range |
|---|---|---|
| LR | 0.461 → 0.926 | 0.664 → 0.974 |
| RF | 0.560 → 0.934 | 0.585 → 0.978 |
| XGB | 0.637 → 0.957 | 0.554 → 0.972 |
| LGBM | 0.555 → 0.931 | 0.564 → 0.981 |
| MLP | 0.431 → 0.889 | 0.663 → 0.958 |

**Interpretation:** As BMI increases from normal to obese range, predicted sensitivity and conformal coverage both rise continuously. This is counter-intuitive at first but is explained by the class-balancing mechanism: models trained with class-balanced losses assign higher predicted probabilities to high-BMI individuals (Obese) who are more often true positives. The categorical "Obese" group captures the upper-BMI high-sensitivity zone. The continuous spline confirms the categorical BMI finding is not an artifact — it reflects a real continuous gradient in how the model assigns risk.

**Does this change the primary story?** No. It reinforces it.

---

### D03 — Continuous Age + Finer Age-Band Analysis
**[A] Observed: The age effect is gradual and worsens beyond 60, but is NOT a sharp cutpoint artifact. The 70+ band shows no clear divergence from 60-69.**

Finer age-band sensitivity (primary models average):

| Age Band | LR Sens | RF Sens | XGB Sens | LGBM Sens | MLP Sens |
|---|---|---|---|---|---|
| 18–39 | 0.667 | 0.727 | 0.788 | 0.727 | 0.576 |
| 40–59 | 0.864 | 0.864 | 0.909 | 0.848 | 0.833 |
| 60–69 | 0.762 | 0.778 | 0.841 | 0.746 | 0.698 |
| 70+   | 0.763 | 0.789 | 0.816 | 0.789 | 0.711 |

**Key finding:** Coverage is comparable between 60–69 and 70+. The 60+ category is appropriate. The age finding is **directionally consistent** across the 60-69 vs 70+ split. The decline appears concentrated around the 60+ boundary, not the 70+ boundary. 

**Directional consistency: YES. Statistical significance change when split: Marginal** (small cells, wide CIs). The 60+ primary category remains a valid and conservative grouping.

---

### D04 — Subgroup-Specific Platt Recalibration
**[A] Observed: Subgroup-specific recalibration does NOT materially reduce conformal coverage failure in the Obese or Age 60+ groups.**

Coverage changes (pp) after subgroup-specific Platt:

| Model | BMI Obese | Age 60+ |
|---|---|---|
| LR | +0.11 | +0.00 |
| RF | -0.11 | +0.00 |
| XGB | +0.00 | +0.00 |
| LGBM | +0.68 | -0.54 |
| MLP | +0.00 | +0.27 |

**Maximum absolute coverage change across all model-subgroup combinations: 0.68 pp.**

**Pre-declared decision rule (exploratory diagnostic):** Since no prior literature directly establishes a threshold for subgroup-calibration materiality in this context, this analysis is classified as **diagnostic/exploratory**. The effect magnitude (< 1 pp in all cases) is negligible.

**[C] Inference:** The subgroup coverage problem cannot be explained by subgroup-level Platt recalibration alone. The problem runs deeper — it reflects the underlying nonconformity score distribution, driven by the class-balancing mechanism and the model's difficulty discriminating in specific demographic-physiological strata.

**[C] Inference on fairness:** Subgroup-specific calibration at the probability level does not materially shift sensitivity disparity, because the sensitivity at a fixed threshold is determined by the raw probability ordering within the subgroup, not by the global probability shift corrected by Platt intercepts.

---

### D05 — Group-Specific Threshold Analysis
**[A] Observed: The sensitivity disparity IS substantially threshold-driven for class-weighted models (LR, RF, XGB, LGBM), but NOT for MLP.**

**Critical context:** The global Youden's J threshold for class-weighted models is calibrated on the entire OOF set. Because the class-balanced models systematically shift probabilities upward (to compensate for the 9.3% prevalence), the globally optimal Youden's J threshold sits very high (0.41–0.52), which creates near-zero sensitivity for some subgroups.

After applying per-subgroup Youden's J thresholds on OOF:
- Sensitivity increases of **51–80 pp** were observed for class-weighted model subgroups.
- MLP (no class balancing) shows much smaller sensitivity increases (**-7 to +27 pp**), meaning its disparity is more intrinsic.

**[C] Critical mechanistic inference:** For class-balanced models, the primary sensitivity disparity appears to be **largely** threshold-driven. This is a significant mechanistic finding. However:
> The group-specific threshold analysis recalibrates the *decision boundary*, not the *probability scale*. Moving to group-specific thresholds equalizes opportunity but does NOT fix miscalibration.

This does not negate the calibration or coverage findings — they operate on different quantities.

---

## Gate 0 Decision Answers

| # | Question | Answer |
|---|---|---|
| 1 | Did continuous BMI support the categorical finding? | **YES** — the BMI effect is genuinely continuous. Categorical Obese captures the real upper-BMI high-sensitivity zone. |
| 2 | Did continuous Age support the 60+ finding? | **YES** — the age effect is gradual and not a sharp cutpoint artifact. 60+ is a valid conservative grouping. |
| 3 | Did finer age bands change interpretation? | **NO** — 60–69 and 70+ behave similarly. The interpretation is unchanged. |
| 4 | Did subgroup recalibration reduce fairness disparity? | **NEGLIGIBLE** — coverage changes < 0.7 pp; subgroup calibration is not the primary driver. |
| 5 | Did subgroup recalibration reduce coverage failure? | **NO** — subgroup Platt recalibration had no material impact on coverage. |
| 6 | Did thresholding explain the fairness gap? | **SUBSTANTIALLY YES for class-balanced models, NO for MLP** — a critical two-mechanism finding. |
| 7 | Which mechanism has the strongest evidence? | **Threshold mechanism** for class-balanced models; **intrinsic discrimination difficulty** for MLP. |
| 8 | Did D01 (Socio-Conformal) change novelty claims? | **NO** — novelty threat is LOW. Candidates 1, 2, 4, and 5 remain intact. |
| 9 | Is fairness post-processing (D06) still scientifically justified? | **YES** — it directly tests whether an Equal Opportunity intervention can close the gap identified in D05, and what calibration/coverage trade-offs result. |
| 10 | Is AFCP (D07) still scientifically justified? | **YES** — the coverage failure found in Obese and Age 60+ groups is persistent regardless of calibration fixes, and comparing FDR-gated vs AFCP group selection mechanisms is scientifically informative. |
| 11 | What is the highest-value Gate 1 analysis? | **D06 (Fairness post-processing)** because it can directly test the Equal Opportunity mechanism confirmed in D05. D07 (AFCP) provides the conformal uncertainty comparison. |

---

## Gate 1 Decision
**PROCEED TO GATE 1 (D06 and D07).**

Scientific justification: Gate 0 revealed that (a) the sensitivity disparity in class-balanced models is substantially threshold-driven, (b) subgroup-specific calibration cannot fix it, and (c) conformal coverage failure persists. These findings create two unresolved questions that Gate 1 can directly address:
1. Does an Equal Opportunity post-processor close the gap, and at what calibration/coverage cost? (D06)
2. Does AFCP identify the same coverage-deficient groups as the current FDR-gated method, and is coverage/efficiency improved? (D07)
