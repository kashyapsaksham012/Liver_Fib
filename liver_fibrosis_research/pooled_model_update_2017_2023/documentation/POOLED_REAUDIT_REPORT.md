# Model-update re-audit — pooled NHANES 2017-2023

**Design.** Five families retrained on a pooled 2017-2023 cohort (N=12063, 1229 positive, 10.188% prevalence; train 8444 / locked test 3619, stratified on cycle x outcome), using the **frozen hyperparameters, preprocessing, threshold method, Platt method and conformal method unchanged**. Locked test touched once.

## Overall: **UPDATING DOES NOT RESOLVE THE FAILURE**

3/3 core reliability failures persist after updating.

| question                               | result                                                                                          | verdict             |
|:---------------------------------------|:------------------------------------------------------------------------------------------------|:--------------------|
| Body-mass detection gap                | pooled test: 32-57 pp, BH-significant 5/5 (2021-2023 slice: 38-69 pp, 5/5)                      | NOT RESOLVED        |
| BMI-Obese conformal under-coverage     | pooled test: coverage 0.776-0.822, Wilson CI excludes 0.90 in 5/5                               | NOT RESOLVED        |
| Matched-stiffness body-mass shortcut   | pooled test: is_obese coefficient 0.11-0.35, p<0.05 in 5/5                                      | NOT RESOLVED        |
| Aggregate discrimination (pooled test) | AUROC 0.806-0.813 (frozen 2017-2020: 0.823-0.843; temporal 2021-2023: 0.776-0.782); 3/5 >= 0.81 | PARTIALLY RECOVERED |
| Discrimination on the 2021-2023 slice  | AUROC 0.773-0.787; 0/5 >= 0.80 (un-updated frozen model on 2021-2023 was 0.776-0.782)           | NOT RECOVERED       |

## Reading

- **The body-mass detection gap is not a staleness artefact.** Retraining on data that includes the 2021-2023 cycle leaves the Normal-vs-Obese sensitivity gap intact (32-57 pp, BH-significant 5/5; larger still on the 2021-2023 slice). The matched-stiffness body-mass shortcut is likewise unchanged (5/5, p<0.001). The conformal subgroup under-coverage persists 5/5.
- **Updating restores aggregate discrimination only partially, and not at all on the newer data.** Pooled-test AUROC recovered to ~0.81 (from the temporal 0.78), but on the 2021-2023 test slice it stayed at 0.77-0.79 — no better than the un-updated frozen model. The 2021-2023 concept drift is not learnable by adding the drifted cycle to training; a genuinely changed predictor-outcome relationship (or reference-standard change) is the parsimonious explanation.
- **Conclusion.** Neither post-hoc mitigation (Amendments #17-18), training-time reweighting (Amendment #19), nor model updating on newer data resolves the body-mass reliability-fairness failure. It is structural.

## Boundary

A diagnostic re-audit, not a proposed deployable model and not external validation. Pooled numbers are a separate evidence tier and change no `evidence-freeze` primary or secondary claim. Nothing in the frozen tree or the temporal module was modified.
