# P0/P1 Remediation Addendum

Executed against the frozen repository. No retraining, no refitting, no new test-set scoring —
every computation below reuses an already-existing artifact or an already-fitted model. This
document supplements, and does not replace, `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md` and
`FINAL_SCIENTIFIC_INTERPRETATION.md`.

---

## P0-1 — Intersectional conformal-coverage confidence intervals

**File:** `results/uncertainty/intersectional_coverage_ci.csv`
**Source:** `results/mitigation/intersection_participant_level_audit.csv` (frozen Phase 7 artifact;
per-participant `baseline_in_set`/`mitigated_in_set` indicators for the true BMI-Obese ∩ Age-60+
intersection, N=294, confirmed exactly matching the prior verified definition).
**Method:** the identical Wilson score formula already used project-wide
(`phase6_04_final_test_touch.py:34–42`), reused rather than reimplemented.

| Model | Baseline coverage (95% CI) | Post-mitigation coverage (95% CI) |
|---|---|---|
| Logistic | 69.4% (63.9%–74.4%) | 84.4% (79.8%–88.1%) |
| Random Forest | 75.2% (69.9%–79.8%) | 80.6% (75.7%–84.7%) |
| XGBoost | 65.0% (59.4%–70.2%) | 80.6% (75.7%–84.7%) |
| LightGBM | 71.1% (65.7%–76.0%) | 75.9% (70.6%–80.4%) |
| MLP | 73.8% (68.5%–78.5%) | 81.6% (76.8%–85.6%) |

**Finding:** all 10 confidence intervals — every model, both stages — have an upper bound below
0.90. The true intersectional subgroup's under-coverage is a statistically formalized result at
N=294, not an artifact of small-sample noise, and it persists after mitigation for every model.

---

## P0-2 — Interpretability: logistic coefficients and permutation importance

**Files:** `results/tables/interpretability_logistic_coefficients.csv`,
`results/tables/interpretability_permutation_importance.csv`

**Logistic coefficients** (primary v1 model, matching the headline cv_auc=0.8157; standardized
scale, since predictors are scaled inside the pipeline):

| Predictor | Standardized coefficient | Odds ratio per 1 SD |
|---|---:|---:|
| BMI | +0.746 | 2.11 |
| Age | +0.526 | 1.69 |
| AST | +0.339 | 1.40 |
| ALT | +0.218 | 1.24 |
| HDL | −0.188 | 0.83 |
| ALP | +0.154 | 1.17 |
| Sex | −0.142 | 0.87 |
| Total bilirubin | +0.126 | 1.13 |
| Albumin | −0.101 | 0.90 |
| Platelets | −0.099 | 0.91 |

All ten directions match the clinically expected sign (already confirmed by a univariate check in
a prior audit pass) — no reversed or implausible relationship.

**Permutation importance** (mean ROC-AUC drop, 30 repeats, seed=42), computed on the Phase 6
proper-train-refit model instances (fit on N=4,005, the complement of the conformal-calibration
set) evaluated on the conformal-calibration set (N=1,002) — genuinely held out from that specific
model instance, reusing existing project infrastructure, and **not** the locked test set:

| Rank | Random Forest | XGBoost | LightGBM | MLP |
|---|---|---|---|---|
| 1 | BMI (0.122) | BMI (0.135) | BMI (0.142) | BMI (0.150) |
| 2 | Age (0.050) | Age (0.060) | Age (0.057) | AST (0.047) |
| 3 | ALT (0.021) | ALT (0.030) | ALT (0.034) | Age (0.040) |

**Cross-model consistency finding — directly relevant to the fairness/conformal results:** BMI and
Age are the two most important predictors in every model except MLP (where Age ranks third, just
behind AST). The model's discrimination is substantially driven by the same two variables that
define its two most under-served demographic subgroups. This is an observation about the model's
learned reliance, not a causal claim about disease mechanism, and should be reported as such.

---

## P1-1 — Youden's J clinical cost-tradeoff paragraph

> The classification threshold for each model was selected via Youden's J statistic, computed
> exclusively from out-of-fold training-CV predictions before the locked test set was ever
> accessed (verified at the code level; see `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md` Part G).
> Youden's J maximizes sensitivity + specificity − 1, which implicitly treats a false negative
> (a missed fibrosis case) and a false positive (an unnecessary confirmatory workup) as equally
> costly. In a fibrosis-screening context this symmetry is a simplification: missing a case of
> significant fibrosis plausibly carries a materially higher clinical cost than a false positive,
> which typically triggers a further non-invasive evaluation rather than an invasive procedure. At
> the chosen operating points, this project's models achieve favorable sensitivity (75.0%–84.5%)
> and excellent NPV (96.7%–97.7%), at the cost of low PPV (20.0%–24.6%) — roughly three of every
> four positive predictions are false positives at 9.32% test-set prevalence. Youden's J was
> retained here specifically because it is a pre-specified, non-post-hoc rule that avoids
> threshold-shopping after seeing results — a methodological-integrity justification, not a claim
> that it is the clinically optimal operating point. A cost-weighted threshold (e.g., favoring
> sensitivity further, given the asymmetry above) is a reasonable alternative for a deployment
> context and should be considered if this model is ever operationalized, but was not explored
> here in order to keep the primary discrimination/calibration/fairness/uncertainty analysis on a
> single, pre-registered operating point per model.

---

## P1-2 — Corrected mitigation wording

**Replace any prior wording implying the mitigation "resolved" or "fixed" the subgroup coverage
problem with the following:**

> Group-wise (Mondrian) conformal mitigation produced real, in several cases substantial,
> improvements in the true BMI-Obese ∩ Age-60+ intersectional subgroup's coverage — gains of
> +5.4 to +15.6 percentage points across the five models (see P0-1 above). It did **not** resolve
> the problem for any model: the post-mitigation 95% confidence interval for this subgroup remains
> entirely below the 90% nominal target in all five cases (upper bounds 80.4%–88.1%). Separately,
> applying mitigation to XGBoost caused its *overall* (marginal, whole-test-set) coverage to rise
> to 93.4% — a +5.27 percentage-point drift that breaches this project's own pre-specified ±5pp
> marginal-coverage tolerance. The correct, complete characterization is: mitigation measurably
> improved but did not solve the intersectional subgroup problem for any model, and for one model
> (XGBoost) this improvement came with a documented, out-of-tolerance side effect on overall
> coverage. Neither fact should be reported without the other.

---

## P1-3 — External validation status, made explicit

> This model has not been externally validated. All reported results derive from a single
> internal random 70/30 split of one NHANES release (2017–March 2020); no independent, non-NHANES
> dataset, and no temporally or geographically distinct cohort, was used at any stage. The
> Non-Hispanic Black holdout evaluation (Phase 8) is a **within-NHANES demographic holdout** —
> retraining with one demographic subgroup withheld from the same source population and evaluating
> on it — and must not be described or interpreted as external validation. It is informative about
> transportability to an unseen demographic composition within the same data-generating process
> (showing a moderate discrimination drop, AUC 0.82–0.84 → 0.77–0.79, and materially less stable
> calibration), but it does not speak to performance in a different health system, country, time
> period, or measurement protocol. External validation on an independent cohort remains the single
> largest open limitation of this project and should be stated as such wherever the model's
> reliability or fairness properties are summarized, not confined to a single limitations
> paragraph.

---

## Status

| Item | Status |
|---|---|
| P0-1 Intersectional coverage CI | **DONE** — `intersectional_coverage_ci.csv` written and verified |
| P0-2 Interpretability | **DONE** — coefficients + permutation importance written and verified |
| P1-1 Youden's J paragraph | **DONE** — see above |
| P1-2 Mitigation wording correction | **DONE** — see above |
| P1-3 External validation statement | **DONE** — see above |

No core pipeline code was modified. No model was retrained or refit. No new test-set scoring
occurred at any point in this remediation pass.
