# NHANES Survey Design Metadata & Guidelines (Remediated)

**Generated:** 2026-08-18 13:27:28

NHANES uses a complex, multistage, probability sampling design. Any representative prevalence estimate or statistical test must incorporate survey weights, primary sampling units (PSU), and strata to avoid biased estimates.

## Preserved Survey Design Variables in Master Dataset (NOT yet applied to any analysis)

- **`WTMECPRP`**: Full-sample 2-cycle MEC Exam Weight. Required for elastography (FibroScan) analysis since it is a MEC exam component.
- **`WTINTPRP`**: Full-sample 2-cycle Interview Weight. Use only for interview-only variables.
- **`WTSAFPRP`**: Fasting Subsample Weight (confirmed correct name for this cycle). Required if analysis is restricted to the fasting subsample (glucose/triglycerides).
- **`SDMVPSU`** / **`SDMVSTRA`**: Masked variance pseudo-PSU / pseudo-stratum, for Taylor-series variance estimation under the masked complex design.

## Official NHANES Weight-Selection Rule (verified quote, NHANES Weighting Tutorial)

> "You must use the weight of the smallest subpopulation that includes all the variables you want to include in your analysis." NHANES's own worked example uses exactly this project's scenario: triglycerides are measured on a fasting MEC subsample, so "the fasting subsample is the smallest subsample in the analysis and you would use the AM fasting weights."

**Direct application to this project:** any analysis combining FibroScan/MEC-exam variables with glucose or triglycerides must use `WTSAFPRP`, not `WTMECPRP`. Analyses that exclude the fasting-only labs may use `WTMECPRP`. This rule is sourced from NHANES's own tutorial, not inferred by this project.

## Phase 2 Methodological Guidelines (still open decisions)

1. **Weight selection** follows the rule above once the final predictor set (broad vs. fasting-extended, see broad_vs_fasting_cohort.md) is locked.
2. **ML training vs. weighting:** Official NHANES materials are SILENT on whether/how survey weights should be used inside predictive model training (vs. reserved for population-representative estimation and variance calculation). This is a genuinely open methodological question that NHANES documentation does not resolve -- it must be answered from general survey-statistics/ML methodology literature in Phase 2, not attributed to NHANES guidance.
3. **Design variables** (`SDMVPSU`/`SDMVSTRA`) should be used for any variance/CI estimation that claims population representativeness; not required for internal train/test ML validation splits, which is a separate concern from population inference.
