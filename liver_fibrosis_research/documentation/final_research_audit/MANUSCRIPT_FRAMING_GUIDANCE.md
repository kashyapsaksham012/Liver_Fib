# Manuscript Framing Guidance

**Date:** 2026-08-27 · **Status:** AUTHORITATIVE (author's framing decision) · **Type:** positioning
guidance. No analysis, no result change — this governs how the existing verified findings are
*presented*.

---

## 1. The headline

Two things, and only these two, carry the abstract and the framing:

1. **A reproducible subgroup detection failure by body-mass:** normal-weight participants are
   under-detected — sensitivity 27–48 pp lower than in obese participants, in all five model
   families (FDR q ≤ 0.006), independently reproduced, and stable across three sensitivity cohorts
   (15/15). This is the single most robust finding in the study.
2. **The methodological point (the paper's thesis sentence):** *discrimination plus aggregate
   calibration are insufficient evidence of subgroup-safe reliability; the failing subgroups are
   identifiable, reproducible, mechanism-linked, and resistant to every mitigation strategy we
   tested.* Split-conformal prediction meets its marginal coverage target (88–91%) while
   under-covering identifiable subgroups (BMI-Obese 77–82%, Age-60+ 81–86%) in every model, on
   every cohort construction, and no mitigation tested produced an acceptable fix.

## 2. Age-60+ — demoted to a secondary observation

The **Age-60+ sensitivity disparity** is **not** a co-headline finding. It is directionally
consistent but statistically fragile, and it must be presented that way.

- **Where it goes:** Results body and Limitations. **Not** the abstract, **not** the title, **not**
  the first paragraph of the Discussion. Never paired with the BMI finding as "two subgroup
  failures."
- **How to state it:** always with its fragility in the same sentence —
  > "Older participants (≥ 60 y) showed a consistent-direction sensitivity deficit that reached
  > significance in four of five models but was lost under 9 of 12 alternative cohort/threshold
  > specifications, and reflects a non-monotonic age effect (peak ≈ 65 y); we therefore treat it
  > as a hypothesis-generating observation rather than an established disparity."
- **Why:** leading with two subgroup findings when one is weak invites reviewers to attack the
  fragile one and let that doubt spread to the robust one. Leading with BMI alone protects the
  study's strongest result.
- **Do not claim:** Age-60+ significance in 5/5 models; a monotone "older is worse" gradient;
  cross-cohort robustness of the age finding.

## 3. Age-60+ in the conformal story — retained at full strength

The **Age-60+ conformal under-coverage** is a *different, firmer* finding and stays in the
conformal-reliability results as reported:

- 81.1–85.6% empirical coverage on CAND_1, Wilson CIs excluding 90%, all 5 models, FDR-significant.
- Replicated on CAND_2 / CAND_3 / 8.0 kPa (Amendment #16).
- It is part of the marginal-vs-subgroup coverage contrast: "marginal coverage concealed
  under-coverage of **obese and older** participants in every model."

**Distinguish the two Age-60+ findings explicitly in the text.** The *sensitivity* disparity is a
fragile secondary observation; the *conformal coverage* shortfall is a supported subgroup-reliability
result. They are correlated consequences of related mechanisms but have different evidentiary
weight, and a reader must not conflate them.

## 4. Abstract — do / don't

**Do:**
- Lead with the normal-weight under-detection finding and its independent reproduction.
- State the marginal-vs-subgroup conformal coverage contrast (name obese and older participants).
- State that no mitigation strategy tested produced an acceptable fix.
- State that no external or out-of-sample (later-cycle / independent-cohort) validation was
  performed.

**Don't:**
- Present Age-60+ sensitivity as a co-primary subgroup finding.
- Use "two demographic subgroups fail" phrasing.
- Imply a deployable model, clinical-grade discrimination, or resolved fairness.

## 5. Recommended framing paragraph (adapt as needed)

> Five routine-data model families reached a comparable, modest-to-strong discrimination ceiling
> for significant liver fibrosis (AUROC ≈ 0.82–0.84) and, after a required out-of-fold
> recalibration, were well calibrated in aggregate. That aggregate adequacy concealed a
> reproducible, mechanism-linked detection failure in normal-weight participants, who were
> substantially under-identified across every model and every sensitivity cohort, in both model
> fits, and at matched liver stiffness (a body-mass risk shortcut). Split-conformal prediction
> exposed a parallel reliability gap: marginal coverage met its target while coverage for obese
> and older participants — and their intersection — fell well below it, and no calibration-,
> threshold-, conformal-, or selective-deferral-based intervention we tested produced an
> acceptable repair (group-conditional recalibration only over-covers the well-served subgroups).
> A consistent-direction but specification-sensitive sensitivity deficit in older participants is
> reported as a secondary observation. The contribution is not a deployable model but a
> demonstration that discrimination and aggregate calibration are insufficient evidence of
> subgroup-safe reliability.

## 5b. Amendment #18 pre-publication fixes — how to frame them

- **Fit alignment (Fix 1): STRENGTHENING.** State plainly that the body-mass gap is present in
  both the full-train fit (fairness audit) and the proper-train-refit fit (conformal). Do not
  hedge the link between the two findings.
- **Reference-standard measurement bias (Fix 2): verdict V3.** Keep the body-mass finding; add the
  caveat that a residual BMI-dependent measurement contribution could not be excluded (Normal-BMI
  underpowered at stricter labels). But lead the limitation paragraph with the evidence *against*
  the artefact explaining the gap: obese sensitivity/coverage stable under stricter labels, and
  the matched-stiffness shortcut (obese +0.19–0.33 predicted probability at identical stiffness,
  p<0.001, 5/5). Net effect: a strengthening of the fairness interpretation, not a retreat.
- **Selective deferral (Amendment #17): NO IMPROVEMENT.** Frame as a mechanistic dead-end for
  post-hoc methods, not as a failed attempt — it shows the under-coverage is confidently-scored
  wrong singletons, which is why a training-time intervention is the indicated next step.

## 6. Cross-references

- Evidentiary tiers: `FINAL_SCIENTIFIC_FINDINGS.md` (BMI = CONFIRMED §3; Age = SUPPORTED WITH
  LIMITATIONS §4), `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` (`FAIR-AGE-01`, `CONF-02`).
- Required limitations: `FINAL_LIMITATIONS_REGISTER.md`.
- Prohibited claims: `DO_NOT_CLAIM.md`.
