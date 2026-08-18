# Missing-Data Protocol (Phase 2K)

**Generated:** 2026-08-18

## Missingness Assessment

Starting pool: adults with quality-valid elastography, no predictor-completeness restriction yet
(`COHORT_3B_ADULT_OF_QUALITY_VALID`, N=7,768). Restricting to complete broad-lab + BMI + sex data (the
primary cohort's eligibility rule) excludes 615 participants (7.9%).

**Demographic composition, pool vs. complete-case vs. excluded** (full detail reproducible from
`_cohorts.py` + `phase2_predictor_registry.csv` missingness columns):

| Group | Full pool (N=7,768) | Complete-case (N=7,153) | Excluded (N=615) |
|---|---|---|---|
| Male | 49.7% | 49.4% | 53.8% |
| Female | 50.3% | 50.6% | 46.2% |
| Non-Hispanic White | 33.9% | 34.7% | 24.9% |
| **Non-Hispanic Black** | **26.3%** | **25.0%** | **41.3%** |
| Mexican American | 12.1% | 12.6% | 6.7% |
| Non-Hispanic Asian | 12.1% | 12.1% | 12.5% |
| Median age | 50.0 | 50.0 | 52.0 |
| Outcome prevalence (≥8.2kPa) | 9.37% | 9.31% | 10.08% |

**Finding (must not be hidden):** Non-Hispanic Black participants are disproportionately represented
among those excluded by lab-completeness restriction (41.3% of excluded vs. 25.0% of the retained
complete-case cohort) — a 16.3-percentage-point over-representation. Sex composition and outcome
prevalence are comparatively similar between groups. **This is a directly fairness-relevant missingness
pattern and is documented here rather than glossed over**, consistent with the research question's core
concern.

## Decision

> **PRIMARY STRATEGY: Complete-case analysis.**
> The primary cohort's eligibility rule already requires the 10 primary predictors to be non-missing
> (`primary_cohort_decision.md`), so the primary analysis is complete-case *by construction* — a standard,
> TRIPOD-consistent approach for a primary prediction-model analysis. No further imputation is applied to
> the primary dataset.

**Justification:** (1) Overall missingness in the eligible pool is modest (7.9%) and not so large that
complete-case analysis discards a majority of the sample. (2) Complete-case avoids introducing
imputation-model assumptions into the primary result, keeping the primary analysis maximally
interpretable. (3) The demographic shift identified above is real but bounded (the retained cohort's
Black representation drops only from 26.3% to 25.0% of *all* participants — a modest 1.3pp population-level
shift, even though it is a 16.3pp shift in *who gets excluded*) — not treated as disqualifying, but
explicitly flagged and addressed via the sensitivity analysis below, not ignored.

> **SENSITIVITY ANALYSIS: Multiple imputation (MICE-style) on the full adult quality-valid pool
> (N=7,768), predictors imputed from other predictors + outcome-independent auxiliary variables only.**

**Purpose:** Directly test whether the identified differential-missingness pattern changes conclusions —
in particular, whether Black-subgroup fairness metrics differ meaningfully between the complete-case
primary analysis and an imputation-based analysis that retains the additional 615 participants.

## Leakage-Safety Requirements (binding for Phase 3 implementation)

1. Imputation models (if the sensitivity analysis is run) must be **fit on training data only** and
   applied to validation/test data using parameters learned exclusively from training data — never
   refit or re-parameterized using validation/test rows (non-negotiable rules 10–11).
2. The primary complete-case dataset requires no such step, since eligibility is determined before any
   train/test split and does not depend on the split itself.
3. Missingness indicators themselves are not currently flagged as informative (`MISSING NOT AT RANDOM`)
   beyond the race/ethnicity pattern above — this is noted as an open item for Phase 3 diagnostic review,
   not resolved here.

## Not Selected

- **Simple (e.g. median) imputation on the primary dataset** — rejected as the default because it would
  silently discard the differential-missingness signal identified above without the interpretability
  benefit of a documented multiple-imputation sensitivity model.
- **Model-specific missing handling (e.g. tree-based native NA handling)** — deferred to Phase 3 as a
  model-family-specific implementation detail, not a Phase 2 protocol decision; if used, it must be
  applied identically to the complete-case primary dataset (where it is a no-op, since there is no
  missingness) to keep primary/sensitivity comparisons clean.
