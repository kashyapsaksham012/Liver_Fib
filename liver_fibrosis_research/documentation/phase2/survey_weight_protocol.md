# Survey Weight Strategy (Phase 2N)

**Generated:** 2026-08-18

## Four Distinct Uses, Four Distinct Decisions (not assumed to be the same)

### 1. Survey-weighted descriptive/population estimates
> **USE WEIGHTS.** Apply `WTMECPRP` for any population-representative estimate using only broad-cohort
> (non-fasting) variables; apply `WTSAFPRP` for any estimate that includes fasting glucose/triglycerides,
> per the official NHANES weighting-tutorial rule verified in Phase 1 ("use the weight of the smallest
> subpopulation that includes all the variables you want to include"). `SDMVPSU`/`SDMVSTRA` must be used
> for correct variance estimation (Taylor-series linearization) whenever a population-representative
> prevalence or CI is reported (e.g. "X% of U.S. adults have significant fibrosis").
> **Caveat:** the outcome-prevalence Wilson CIs already produced in `phase2_outcome_prevalence.csv` are
> UNWEIGHTED, sample-level binomial CIs — appropriate for internal ML-sample characterization, NOT a
> claim about U.S. population prevalence. Any population-representative prevalence claim in Phase 3/thesis
> writing must be recomputed with `WTMECPRP`/`SDMVPSU`/`SDMVSTRA` design-based methods, not lifted from
> that CSV.

### 2. Individual-level predictive modeling (training)
> **PRIMARY: UNWEIGHTED.** Train models on the raw sample without incorporating survey weights into the
> loss function.
**Rationale:** This is standard ML practice, and NHANES's own documentation is explicitly silent on
whether/how survey weights should enter model training (confirmed in Phase 1 research — not an NHANES
recommendation either way). Training unweighted optimizes for the *sample* distribution, which is the
correct target when the goal is a risk score to be evaluated and deployed onto the kind of population
NHANES sampled (its participants), not a lower-variance *population-average* effect estimate.
> **SENSITIVITY: weighted-loss training** (e.g. `sample_weight` in XGBoost/LightGBM using `WTMECPRP` or
> `WTSAFPRP`) as an exploratory comparison, given this is a genuinely unresolved methodological question
> the project should not pretend is settled.

### 3. Weighted model evaluation (test-set metrics)
> **PRIMARY: UNWEIGHTED.** Evaluate discrimination/calibration on the same (unweighted) sample
> distribution the model was trained and will be conceptually deployed against.
**Rationale:** Consistency with (2); a model trained unweighted but evaluated weighted would create a
train/evaluation objective mismatch. Weighting a modestly-sized held-out test set can also materially
inflate metric variance (a small number of high-weight participants can dominate a weighted estimate).
> **SECONDARY (context only, not primary evaluation):** report survey-weighted subgroup prevalence
> alongside model metrics purely for population-representativeness context, clearly labeled as such.

### 4. Subgroup / fairness evaluation
> **PRIMARY: UNWEIGHTED**, for the same consistency and variance-inflation reasons as (3) — and because
> several primary fairness subgroups are already modestly sized (e.g. Non-Hispanic Asian N=866, Underweight
> BMI N=109 in the primary cohort); introducing survey weighting here would only inflate the effective
> variance of an already lower-precision estimate, undermining exactly the subgroups the fairness analysis
> most needs to characterize honestly.

## Summary Table

| Use case | Primary approach | Sensitivity/secondary approach |
|---|---|---|
| Population descriptive estimates | Weighted (WTMECPRP/WTSAFPRP + SDMVPSU/SDMVSTRA) | — |
| Model training | Unweighted | Weighted-loss training (exploratory) |
| Model evaluation | Unweighted | Weighted subgroup prevalence (context only) |
| Fairness/subgroup evaluation | Unweighted | — |

## Uncertainty Acknowledged, Not Hidden

Whether ML training/evaluation *should* incorporate survey weights is a genuinely open question in the
survey-statistics/ML methodology literature that this project does not resolve definitively — the
decision above is this project's documented, defensible primary choice plus an explicit sensitivity check,
not a claim that the question is settled.
