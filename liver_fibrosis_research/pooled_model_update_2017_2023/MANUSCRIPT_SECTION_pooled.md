# Drop-in manuscript content — model-update re-audit (pooled NHANES 2017–2023)

Paste targets: `documentation/manuscript/MANUSCRIPT_DRAFT.md`. Numbers trace to
`pooled_model_update_2017_2023/results/*.csv`; `src/verify_pooled.py` pins them (16/16).

---

## Abstract — extend the mitigation sentence

> Retraining the five families on a pooled 2017–2023 cohort with the frozen
> architecture — the natural response to temporal drift — partially recovered
> aggregate discrimination but did not resolve any of the three reliability
> failures: the body-mass detection gap (32–57 pp, all q < 0.001), the conformal
> subgroup under-coverage (0.78–0.82, 5/5), and the matched-stiffness body-mass
> shortcut (5/5) all persisted, and discrimination on the 2021–2023 test slice
> was unchanged from the un-updated model (AUROC 0.77–0.79).

---

## §2.8c Model-update re-audit (Methods — new subsection)

> To test whether the reliability failures are an artefact of model staleness, we
> retrained the five families on a **pooled cohort of the 2017–March 2020 and
> 2021–August 2023 CAND_1 participants** (N = 12,063; 1,229 with significant
> fibrosis; 10.2% prevalence). The frozen hyperparameters, preprocessing pipeline,
> class-imbalance handling, out-of-fold Youden threshold method, out-of-fold Platt
> recalibration, and split-conformal procedure were used **unchanged** — only the
> training data was expanded. A fresh 70/30 split stratified on cycle × outcome
> gave a locked test set of N = 3,619 (2021–2023 slice N = 1,473), touched once.
> This is a diagnostic re-audit, not a proposed deployable model.

---

## §3.7c Model updating does not resolve the failure (Results — new subsection)

> **The reliability failures persist.** On the pooled locked test the
> Normal-vs-Obese sensitivity gap was 32–57 percentage points (all
> Benjamini–Hochberg q < 0.001; 5/5 models), and 38–69 pp on the 2021–2023 test
> slice — larger than in the development cohort (27–48 pp), not smaller.
> BMI-obese split-conformal coverage was 0.78–0.82 with Wilson intervals excluding
> 0.90 in all five models; the obese-and-60+ intersection was 0.70–0.77. The
> matched-stiffness body-mass shortcut was undiminished (ordinary least-squares
> `obese` coefficient 0.11–0.35, p < 0.001 in all five models). By the
> pre-registered rule, **model updating does not resolve any of the three failures.**
>
> **Discrimination recovers only partially, and not on the newer data.**
> Pooled-test AUROC rose to 0.806–0.813 (from 0.776–0.782 for the un-updated model
> on the 2021–2023 cycle), but on the 2021–2023 test slice the retrained models
> scored AUROC **0.773–0.787 — statistically identical to the un-updated frozen
> model**. The post-pandemic concept drift (§3.12) is not learnable by adding the
> drifted cycle to the training set, consistent with a genuinely changed
> predictor–outcome relationship and/or a reference-standard measurement change
> rather than model staleness.
>
> **Consolidated conclusion.** No approach tested — post-hoc recalibration,
> subgroup thresholds, equalised-odds post-processing, conformal group-wise
> recalibration, conformal selective deferral (§3.7), training-time subgroup
> reweighting (§3.7b), or model updating on newer data (§3.7c) — resolves the
> body-mass reliability–fairness failure. It is structural: it survives every
> intervention within the model-development toolkit, replicates temporally, and
> widens over time.

---

## §5 Limitations — add

> - **Model-update re-audit [D6].** The pooled 2017–2023 retraining used the
>   frozen architecture and hyperparameters; a bespoke architecture or
>   hyperparameter search on the pooled data was not attempted and could behave
>   differently. The 2021–2023 concept drift was not recoverable by pooling, which
>   we interpret as a changed predictor–outcome relationship or a reference-standard
>   change, but a device/protocol audit of the NHANES 2021–2023 elastography
>   documentation is still outstanding.

---

## DO_NOT_CLAIM — add (additive)

> - Model updating on a pooled 2017–2023 cohort is **not** a proposed deployable
>   model and **not** external validation.
> - The pooled re-audit does not test a re-optimised architecture; "structural"
>   means "not resolved by any intervention within the frozen model-development
>   toolkit tested here", not "provably unsolvable".

---

## START_HERE.md §1 — add a tier

> **MODEL-UPDATE RE-AUDIT TIER.** `pooled_model_update_2017_2023/` — five families
> retrained on the pooled 2017–2023 cohort with frozen hyperparameters. Separate
> evidence tier; supersedes nothing. Protocol:
> `pooled_model_update_2017_2023/PROTOCOL_FREEZE.md`.
