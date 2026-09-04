# Limitations — temporal validation addendum

To be read with the `evidence-freeze` limitations register. These are *additional*
to it; none of the primary study's limitations are removed by the temporal work.

1. **Not external validation.** NHANES 2021–2023 is a later cycle of the *same*
   survey programme, same country, same VCTE instrument, same cross-sectional
   design. This is TRIPOD narrow/temporal validation. Geographic, health-system,
   and reference-standard (biopsy/MRE) generalisability remain unestablished and
   are still the foremost outstanding requirement.

2. **The discrimination decline is concept drift of uncertain origin.** The
   development cycle (2017–March 2020) is pre-pandemic; the validation cycle
   (August 2021–August 2023) is post-pandemic, with modified survey operations, an
   older cohort (mean age 52 vs 49), and higher outcome prevalence (11.5% vs 9.3%).
   The decomposition (`TEMPORAL_DROP_DECOMPOSITION.md`) shows the AUROC decline is
   **not** explained by case-mix change (covariate-shift reweighting recovers
   ~17%) or by any single assay (including the alkaline-phosphatase analyzer
   change); it is a changed predictor–outcome relationship, concentrated in
   normal-weight and middle-aged participants. A **reference-standard (VCTE)
   measurement change** — a device, software, or probe-selection difference in the
   2021–2023 elastography protocol — is a plausible contributor and cannot be
   excluded; the NHANES 2021–2023 elastography documentation should be checked, and
   a histology- or MRE-referenced cohort would be needed to separate a genuine
   change in the predictor–disease relationship from a change in how the reference
   standard measures disease. No model updating was performed.

3. **Biochemistry-analyzer change.** The predictor-drift audit found a material
   upward shift in alkaline phosphatase (standardized mean difference 0.25,
   KS 0.11) between cycles, consistent with an analyzer change; total bilirubin
   and platelets shifted mildly; ALT and AST were stable. The primary analysis
   used predictor values **as released, without cross-cycle harmonisation** — the
   honest test of the deployed model. A crosswalk-adjusted sensitivity analysis
   was not required by the drift audit for ALT (stable) and is noted as possible
   future work for alkaline phosphatase.

4. **Modest subgroup and intersectional cells.** N = 4,910 overall is adequate;
   the normal-weight fibrosis-positive cell (65), the obese-and-60+ intersection
   (788 total), and several race cells remain small, so subgroup point estimates
   carry wide intervals.

5. **Single evaluation, frozen models only.** One outcome touch; no model
   updating, recalibration to the new cycle, or threshold re-selection was
   performed or is implied.

6. **Age-60+ sensitivity reversed.** Pre-registered as fragility-anticipated;
   the reversal is reported and reinforces the development-study decision to treat
   the age-60+ sensitivity disparity as a secondary observation. It is not a
   contradiction of a primary claim.
