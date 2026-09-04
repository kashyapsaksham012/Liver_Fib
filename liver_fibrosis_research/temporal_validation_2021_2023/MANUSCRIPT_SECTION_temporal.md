# Drop-in manuscript content — temporal validation (NHANES 2021–2023)

Paste targets are for `documentation/manuscript/MANUSCRIPT_DRAFT.md`. Every number
traces to `temporal_validation_2021_2023/results/*.csv`; the verification harness
`src/verify_temporal.py` pins them.

---

## Abstract — add to Results (after the sensitivity-cohort sentence)

> The body-mass detection gap, the split-conformal subgroup-coverage failure, and
> the fairness–reliability dissociation each replicated in all five models on a
> subsequent NHANES cycle (August 2021–August 2023; 4,910 adults, 11.5% prevalence),
> where the body-mass gap was larger still (63–72 vs 27–48 percentage points).
> Overall discrimination was attenuated (AUROC −0.04 to −0.06); this decline was
> concept drift rather than case-mix change (covariate-shift reweighting recovered
> only ~17%) and was concentrated in normal-weight participants, whose
> discrimination fell to near chance (AUROC ≈ 0.82 → 0.62) — a temporal degradation
> targeting the same subgroup the models already under-detect.

---

## §2.10a Temporal validation cohort (Methods — new subsection)

> As a later-cycle temporal evaluation, the five frozen model families, their
> frozen operating thresholds, the frozen out-of-fold Platt parameters, and the
> frozen split-conformal quantile were applied **without modification** to NHANES
> August 2021–August 2023 (`_L` public-use files). The temporal cohort was built
> with the identical eligibility rule as the primary cohort (quality-valid VCTE,
> adult, complete on the ten predictors): 11,933 → 6,700 → 6,280 → 5,526 → **4,910
> adults**, 563 with significant fibrosis (**11.5% prevalence**). Predictor values
> were used as released (no cross-cycle harmonisation) in the primary analysis; a
> distribution audit against the development cohort and the NHANES analytic notes
> is reported (§3.12). No model, threshold, calibration parameter, or conformal
> quantile was retrained, re-tuned, or re-fitted; the 2021–2023 outcome was
> evaluated once. This is temporal validation within one survey programme, not
> external, geographic, or independent-cohort validation.

---

## §3.12 Temporal validation (Results — new subsection)

> **Cohort and drift.** The 2021–2023 cohort was older than the development cohort
> (mean age 52 vs 49 years), had higher outcome prevalence (11.5% vs 9.3%), and
> showed a materially higher alkaline-phosphatase distribution (standardized mean
> difference 0.25), consistent with a biochemistry-analyzer change; alanine
> aminotransferase was stable (standardized mean difference −0.02).
>
> **Discrimination and calibration.** Applied unchanged, the models' discrimination
> was attenuated: test AUROC fell to 0.776–0.782 (Δ −0.04 to −0.06), slightly
> beyond the pre-specified ±0.05 tolerance for four of five models. The frozen
> out-of-fold Platt recalibration transported: recalibrated calibration-in-the-large
> intercepts were −0.11 to +0.22 (a mild over-correction toward under-prediction),
> decile expected calibration error 0.016–0.021, Brier score 0.085–0.087 (up from
> ≈ 0.07).
>
> **Decomposition of the discrimination decline.** Reweighting the 2021–2023 cohort
> to the development covariate distribution (cross-fitted density-ratio weights)
> recovered only ~17% of the AUROC drop, and quantile-mapping any single predictor
> — including the analyzer-shifted alkaline phosphatase — back to its development
> distribution recovered essentially none (all |ΔAUROC| < 0.004). The decline is
> therefore concept drift (a changed predictor–outcome relationship), not case-mix
> change or a single-assay artefact. It was **not uniform**: within-band AUROC was
> essentially unchanged for obese (Δ −0.05, 95% CI −0.09 to 0.00) and older
> participants (Δ +0.01, −0.06 to +0.06), fell moderately for the 40–59 band
> (Δ −0.10, −0.15 to −0.04), and **collapsed for normal-weight participants**
> (AUROC ≈ 0.82 → 0.62; Δ −0.21, −0.32 to −0.08). The models' discrimination
> degraded over time preferentially for the subgroup they already under-detect.
> A reference-standard (VCTE) measurement change is a possible contributor to the
> apparent concept drift and cannot be excluded (§5).
>
> **Body-mass detection gap (primary finding) — replicated and larger.** Sensitivity
> for significant fibrosis was **63–72 percentage points lower in normal-weight than
> obese participants** in all five models (all Benjamini–Hochberg q < 0.001), a
> larger gap than in the development cohort (27–48 pp). The matched-stiffness
> body-mass shortcut also replicated: among participants with liver stiffness in the
> 8.2–12 kPa band, the frozen models scored obese participants **0.21–0.34 higher**
> than normal-weight participants at identical measured stiffness (ordinary
> least-squares `obese` coefficient, p < 0.001 in all five models; development
> cohort 0.19–0.33).
>
> **Marginal versus subgroup conformal coverage (primary finding) — replicated.**
> Marginal split-conformal coverage stayed near target (0.878–0.902), while
> **BMI-obese coverage was 0.76–0.81** and **age-60+ coverage 0.85–0.88**, with
> Wilson intervals excluding 0.90 and Benjamini–Hochberg significance in all five
> models; the obese-and-60+ intersection (N = 788) fell to **0.69–0.75**.
>
> **Fairness–reliability dissociation — replicated.** In all five models the obese
> subgroup was simultaneously favoured on detection (higher sensitivity than
> normal-weight) and disfavoured on uncertainty-set reliability (conformal coverage
> below target) — the same opposite-direction pattern reported for the development
> cohort.
>
> **Older-age sensitivity — not replicated.** The age-60+ *sensitivity* deficit
> reversed (60+ sensitivity 3–10 pp *higher* than 40–59, Benjamini–Hochberg
> significant only for logistic regression). We had pre-registered this row as
> fragility-anticipated; the reversal confirms the decision to treat the age-60+
> sensitivity disparity as a secondary observation. The age-60+ *conformal*
> under-coverage — a distinct finding — did replicate (5/5).
>
> **Overall.** Partial temporal replication: the two primary findings and the
> proposed mechanism reproduced across an independently assembled later cycle. The
> discrimination decline was concept drift concentrated in normal-weight
> participants — a second axis on which the equity gap widened over time, alongside
> the widening sensitivity gap. Aggregate-AUROC monitoring would have registered
> a modest, arguably tolerable decline while the subgroup harm nearly doubled.

---

## §5 Limitations — add

> - **Temporal validation is within one survey programme [J1a].** The 2021–2023
>   evaluation is a later NHANES cycle, not an external, geographic, or
>   independent-cohort validation. The development cycle is pre-pandemic and the
>   validation cycle post-pandemic; the ~0.05 AUROC decline cannot be attributed to
>   model non-transport as opposed to genuine population change (older, higher
>   prevalence), and at least one biochemistry-analyzer change (alkaline
>   phosphatase) affects a model predictor. Predictor values were used as released
>   without cross-cycle harmonisation. No model updating, clinical readiness, or
>   causal claim follows.

---

## DO_NOT_CLAIM — add (additive; boundary preserved)

> - Temporal replication on NHANES 2021–2023 is **not** external, geographic, or
>   independent-cohort validation and does not establish transportability.
> - The ~0.05 AUROC decline is **not** attributed to model non-transport — it is
>   confounded with a shifted post-pandemic population and an analyzer change.
> - Temporal numbers are a separate evidence tier; they do not enter the primary
>   claim registry and supersede no `evidence-freeze` result.

---

## START_HERE.md §1 — add a tier

> **TEMPORAL EVALUATION TIER (NHANES 2021–2023).** `temporal_validation_2021_2023/`
> — a later-cycle application of the frozen models. Separate evidence tier;
> supersedes nothing; never merged into `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv`
> primary rows. Protocol: `temporal_validation_2021_2023/PROTOCOL_FREEZE.md`.
