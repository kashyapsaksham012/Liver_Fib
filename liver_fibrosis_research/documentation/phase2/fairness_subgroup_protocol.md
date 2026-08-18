# Fairness Subgroup Protocol (Phase 2L)

**Generated:** 2026-08-18 — frozen before any model is trained.

## Primary Fairness Dimensions

All counts below are within the **primary cohort** (N=7,153) at the **primary threshold** (8.2 kPa);
full detail in `results/tables/phase2_outcome_prevalence.csv`.

### 1. Sex — PRIMARY
- **Variable:** `RIAGENDR`. **Categories:** Male (N=3,531, 394 positive), Female (N=3,622, 272 positive).
- **Missing handling:** 0 missing within the primary cohort (eligibility requires non-missing sex).
- **Minimum requirement met:** Yes, both categories are "primary-feasibility candidate" tier
  (positive & negative N both ≥100) per `phase2_statistical_feasibility.csv`.
- **Status: PRIMARY.**

### 2. Race/Ethnicity — PRIMARY (RIDRETH3)
- **Variable:** `RIDRETH3` (NOT `RIDRETH1` — confirmed in Phase 1's `race_ethnicity_verification.md`
  because RIDRETH3 alone preserves Non-Hispanic Asian as a distinct category).
- **Categories:** Mexican American (902, 94+), Other Hispanic (754, 69+), Non-Hispanic White (2,484,
  237+), Non-Hispanic Black (1,787, 177+), Non-Hispanic Asian (866, 52+), Other/Multi-Racial (360, 37+).
- **Missing handling:** 0 missing within the primary cohort.
- **Precision tiers (per `phase2_statistical_feasibility.csv`):** Mexican American, Non-Hispanic White,
  Non-Hispanic Black = primary-feasibility candidate tier (borderline; Mexican American/Black have
  positive N in the 90s-100s range, treated as primary given proximity); **Non-Hispanic Asian (52
  positive) and Other/Multi-Racial (37 positive) = exploratory candidate tier — reported with wider
  expected confidence intervals, NOT dropped or pooled** (non-negotiable rule).
- **Status: PRIMARY**, with explicit per-category precision labeling carried into every downstream table.

### 3. Age — PRIMARY (final bins, revised from Phase 1's provisional bins)
- **Variable:** `RIDAGEYR`, binned. **Final categories:** 18–39 (2,423, 122+), 40–59 (2,318, 221+),
  60+ (2,412, 323+). The Phase 1 provisional "Under 18" bin is dropped — the primary cohort is adult-only
  by definition (`primary_cohort_decision.md`), so that category is structurally empty here.
- **Missing handling:** 0 missing (eligibility requires non-missing age).
- **Precision:** All three bins are "primary-feasibility candidate" tier.
- **Status: PRIMARY.**

### 4. BMI — PRIMARY (final bins, standard WHO categories, unchanged from Phase 1 provisional bins)
- **Variable:** `BMXBMI`, binned. **Categories:** Underweight <18.5 (109, 5+), Normal 18.5–24.9 (1,802,
  72+), Overweight 25–29.9 (2,316, 121+), Obese ≥30 (2,926, 468+).
- **Missing handling:** 0 missing within the primary cohort (eligibility requires non-missing BMI).
- **Precision:** Normal/Overweight/Obese = exploratory-to-primary tier; **Underweight (5 positive) =
  insufficient evidence tier — explicitly reported as such, not dropped, not pooled into Normal.**
- **Status: PRIMARY dimension, with Underweight carried as an explicitly low-precision category.**

## Handling of Limited-Precision Subgroups

Per non-negotiable rule 14 ("never silently combine demographic groups") and Issue 12's original
directive, **no subgroup is pooled or dropped**. Every subgroup-level metric in Phase 3 must be reported
with its feasibility tier attached (primary-feasibility / exploratory / limited-precision / insufficient
evidence) and with a bootstrap or Wilson confidence interval whose width communicates the actual
precision — a wide CI on a small subgroup is the correct, honest output, not a reason to remove that
subgroup from the report.

## Minimum Sample/Outcome Requirements (frozen thresholds, from Phase 1's classification heuristic)

- **Insufficient evidence:** positive N < 10 or negative N < 10 — reported but flagged as not
  interpretable as a point estimate.
- **Limited precision:** positive or negative N in [10, 30) — reported with a visibly wide CI.
- **Exploratory candidate:** positive or negative N in [30, 100).
- **Primary-feasibility candidate:** positive AND negative N both ≥ 100.

These are a project-defined heuristic (binomial-proportion CI-width based), not a universal statistical
standard — stated explicitly, as required.
