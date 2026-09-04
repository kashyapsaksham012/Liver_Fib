# Reconciliation — this run vs the `temporal-validation-standalone` branch

A temporal validation already exists on the git branch
`temporal-validation-standalone` (`liver_fibrosis_research/{src,results}/temporal_validation/`).
This module is a **clean re-execution from the `evidence-freeze` code structure**,
with two deliberate differences.

## What matches exactly

| item | branch | this run |
|---|---|---|
| cohort N | 4,910 | 4,910 |
| positives / prevalence | 563 / 11.4664% | 563 / 11.466% |
| BMI-band positives | Normal 65, Obese 382, Overweight 113, Underweight 3 | identical |
| AUROC (logistic) | 0.78187 | 0.7819 |
| BMI-Obese sensitivity gap | 62.8–71.9 pp, 5/5 sig | 63.0–71.9 pp, 5/5 sig |
| conformal marginal / BMI-Obese / Age-60+ | 0.879–0.902 / 0.770–0.813 / 0.849–0.878 | 0.878–0.902 / 0.761–0.813 / 0.845–0.876 |
| Age-60+ sensitivity direction | reversed (60+ higher), sig only logistic | identical |

Cohort construction and frozen-model application are confirmed correct.

## Deliberate differences

1. **ALT handling.** The branch built a Roche-Cobas-6000 ALT crosswalk
   (`temporal_validation_input_cobas6000_alt.csv`, `prepare_temporal_validation_alt_bridge.py`)
   and scored on bridged ALT. **This run uses raw released ALT** — the honest
   "would the deployed model work on the data as it arrives" test. The predictor-drift
   audit (§`TEMPORAL_DRIFT_AUDIT.md`) shows **ALT is stable across cycles**
   (standardized mean difference −0.02), so the crosswalk changes AUROC by only
   ≈ 0.001 (tree models; logistic essentially unchanged). The raw run is authoritative
   for the primary analysis; the crosswalk is unnecessary for ALT. (Alkaline
   phosphatase *did* shift — flagged, not bridged.)

2. **M4b removed.** The branch computed temporal M4b coverage
   (`temporal_m4b_results.csv`). Amendment #20 removed M4b from the manuscript, so
   this run does not compute it.

## Disposition

- The `temporal-validation-standalone` branch is the **earlier execution**; this
  module is the **clean re-run of record** for the flagship manuscript.
- The standalone temporal manuscript draft on that branch should be **retired and
  its usable content folded into the flagship §3.12** (see
  `MANUSCRIPT_SECTION_temporal.md`), not published separately.
- The branch is kept for provenance; nothing on it is deleted.
