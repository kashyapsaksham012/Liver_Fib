# Temporal validation synthesis — NHANES 2021–2023

**Cohort:** 4910 adults, 563 with significant fibrosis, prevalence 11.4664% (2017–March 2020: 9.3108%).
**Design:** frozen models, thresholds, Platt parameters and conformal quantile applied once, unmodified, to a later NHANES cycle. Raw predictors, no crosswalk (primary). M4b not computed (removed from the manuscript, Amendment #20).

## Overall classification: **PARTIAL TEMPORAL REPLICATION**

5 of 6 pre-registered core findings replicated or strengthened (the age-60+ sensitivity row was pre-specified as fragility-anticipated and is excluded from the count).

## Finding-by-finding

| Finding                                           | Temporal result                                                                                                                | Verdict                                               |
|:--------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------|
| Discrimination (AUROC)                            | AUROC 0.776–0.782 (Δ -0.062 to -0.042); 1/5 models within the pre-specified ±0.05 tolerance                                    | ATTENUATED                                            |
| Calibration correction (frozen Platt)             | recalibrated intercepts -0.11 to +0.22 (5/5 within ±0.5); slopes 0.86–1.01; ECE 0.016–0.021; Brier 0.085–0.087 (up from ~0.07) | REPLICATED (mild over-correction)                     |
| BMI-Obese vs Normal sensitivity gap               | gap 63–72 pp (2017–2020: 27–48); BH-significant 5/5; larger than 2017–2020 in 5/5                                              | STRENGTHENED                                          |
| Marginal-vs-subgroup conformal split              | marginal 0.878–0.902 (5/5 within ±0.03 of 0.90); BMI-Obese 0.761–0.813, CI excludes 0.90 and BH-significant 5/5                | REPLICATED                                            |
| Age-60+ sensitivity deficit (anticipated fragile) | disparity +2.6 to +10.3 pp (2017–2020 direction was negative); negative direction in 0/5; BH-significant 1/5                   | NOT REPLICATED (reversed; anticipated in protocol §5) |
| Matched-stiffness body-mass shortcut (mechanism)  | is_obese OLS coefficient 0.21–0.40 (2017–2020: 0.19–0.33); p<0.05 in 5/5, positive in 5/5                                      | REPLICATED (slightly stronger)                        |
| Fairness–reliability dissociation (BMI-Obese)     | obese are fairness-favorable on detection AND reliability-unfavorable on conformal coverage in 5/5 models                      | REPLICATED                                            |

## Reading

- **What replicated — and it is the thesis of the paper.** The body-mass detection gap reproduced in all five models and was *larger* than in the development cohort. The split-conformal pattern — marginal coverage on target, obese and older participants and their intersection under-covered — reproduced in all five models. The fairness–reliability *dissociation* (obese favoured on detection, disfavoured on uncertainty-set reliability) reproduced in all five. The matched-stiffness body-mass shortcut — the proposed mechanism — reproduced and was slightly stronger.
- **What attenuated.** Raw discrimination fell ~0.04–0.06 AUROC in every model, slightly beyond the pre-specified ±0.05 tolerance for four of five. This is unsurprising: the development cohort is pre-pandemic and the validation cohort is post-pandemic, older (mean age 49→52), heavier at the tails, with higher outcome prevalence (9.3%→11.5%) and at least one biochemistry analyzer change (alkaline phosphatase shifted materially; ALT was stable). Transport failure and genuine population change cannot be separated here.
- **What did not replicate — as anticipated.** The age-60+ *sensitivity* deficit reversed (60+ now modestly higher, significant only for logistic regression). The frozen protocol pre-registered this row as fragility-anticipated; the reversal confirms the development-study decision to demote it to a secondary observation. The age-60+ *conformal* under-coverage — a separate, firmer finding — did replicate (5/5).
- **The discrimination decline is concept drift, and it is targeted (`TEMPORAL_DROP_DECOMPOSITION.md`).** Covariate-shift reweighting recovers only ~17% of the AUROC drop; no single predictor recovers more than 0.004. Within-band AUROC is unchanged for obese and 60+ participants but **collapses for normal-weight participants** (≈0.82 → 0.62; bootstrap CI on the change excludes 0). The models degrade over time preferentially for the same subgroup they already under-detect — a second axis on which the equity gap widened.

## Boundary statement

This is a later-cycle temporal evaluation within one survey programme. It is **not** external, geographic, or independent-cohort validation, and establishes no clinical readiness, model-updating basis, or causal explanation. No primary or secondary claim from `evidence-freeze` was changed; this is a separate evidence tier.
