# Phase 8 Holdout Candidate Decision

**Generated:** 2026-08-19, live, before any Phase 8 model training. Precedes
`PHASE8_SUBGROUP_HOLDOUT_PROTOCOL_FREEZE.md` and all training code.

## 1. Candidates considered

Three protocol-relevant candidates were evaluated, matching the mega-prompt's minimum-required
set: Non-Hispanic Black, BMI-Obese, Age-60+. No other candidate is evaluated as primary — the
frozen `fairness_subgroup_protocol.md` dimensions (sex, race/ethnicity, age, BMI) were reviewed,
and these three are the only categories with a documented Phase 5–7 finding profile substantial
enough to motivate a Phase 8 generalization test (sex showed no material Phase 5 disparity; other
race/ethnicity categories were either the reference group, non-significant, or already flagged
fragile/non-confirmed).

## 2. Counts (from `results/validation/phase8_candidate_holdout_matrix.csv`, computed live from
`data/processed/analysis_dataset_primary.parquet`, N=7,153)

| Candidate | Holdout N/pos/neg | Remaining train N/pos/neg | Train prevalence | % positive-case reduction |
|---|---|---|---|---|
| Non-Hispanic Black | 1,787 / 177 / 1,610 | 5,366 / 489 / 4,877 | 9.11% | 26.58% |
| BMI-Obese | 2,926 / 468 / 2,458 | 4,227 / 198 / 4,029 | 4.68% | 70.27% |
| Age-60+ | 2,412 / 323 / 2,089 | 4,741 / 343 / 4,398 | 7.23% | 48.50% |

## 3. Scientific purpose per candidate

- **Non-Hispanic Black:** tests generalization of a group connected to the complete-case/MI
  selection thread (41.3% of complete-case exclusions vs. 25.0% of retained were Non-Hispanic
  Black; targeted MI found MI ROBUSTNESS PARTIAL, no reversal). No significant Phase 5 fairness
  disparity or Phase 6 undercoverage was found for this group (0/5 models each, after FDR); it was
  not a Phase 7 mitigation target.
- **BMI-Obese:** tests generalization of a group with a confirmed Phase 5 fairness disparity (5/5
  models significant after FDR), confirmed Phase 6 undercoverage (5/5 models), and a Phase 7
  mitigation target with incomplete resolution.
- **Age-60+:** tests generalization of a group with a confirmed Phase 5 fairness disparity (4/5
  models significant after FDR), confirmed Phase 6 undercoverage (5/5 models), and a Phase 7
  mitigation target with incomplete resolution.

## 4. Feasibility

Non-Hispanic Black is FEASIBLE with the mildest training-population impact (26.58% positive-case
reduction, remaining training prevalence 9.11%, close to the full 9.31%). BMI-Obese is MARGINAL —
excluding it strips 70.27% of all positive cases from training (666→198), a severe,
clinically-expected class-imbalance shift (obesity is strongly associated with liver fibrosis)
that would confound any holdout-generalization result with a training-population-integrity
problem independent of the holdout question itself. Age-60+ is feasible with caution (48.50%
positive-case reduction, a real but less severe impact than BMI-Obese).

## 5. Previous terminal statement — transparent reconciliation

**This section documents PATH B (prior researcher commitment), not PATH A (independent
discovery), exactly as required.**

Before this Phase 8 mega-prompt was issued, the assistant asked the researcher directly (via a
structured question) how to proceed on Phase 8 scope — including which subgroup to hold out. The
researcher's literal, explicit answer was:

> "Hold out Non-Hispanic Black participants entirely and retrain."

This was a direct, explicit instruction, not an inference drawn from prior context, and not
something producible by ambiguity or guesswork. It was given **before** the candidate matrix in
Section 2 above was computed. Therefore:

**The candidate matrix in this document is a confirmation/feasibility assessment of an
already-committed researcher decision, not a blind discovery mechanism that arrived at
Non-Hispanic Black independently.**

It is scientifically honest to also note: had the matrix been run with no prior instruction, its
training-population-integrity analysis (Section 4) would likely have favored Non-Hispanic Black
on feasibility grounds alone, since it is the only candidate that does not create a severe
class-imbalance confound in the remaining training population. This is stated as an observation,
not as evidence that the matrix "discovered" the choice independently — the choice was made by
the researcher first.

## 6. Final primary holdout decision

**Non-Hispanic Black.**

## 7. Why chosen

1. Directly instructed by the researcher (Section 5) — a legitimate, sufficient basis on its own.
2. Independently feasible on training-population-integrity grounds (mildest positive-case
   reduction of the three candidates; Section 4).
3. Scientifically distinct from, and directly extends, the already-completed MI sensitivity
   thread: MI asked whether *including* previously-excluded participants changes the result;
   Phase 8 asks whether the model can generalize to this group with *zero* representation during
   training — a genuinely new question, not a repeat.
4. No significant Phase 5/6 disparity for this group means Phase 8's result here is not
   confounded by a group the model was already known to treat differently while trained on it —
   any generalization gap found here is attributable more cleanly to unseen-group transportability
   itself, rather than compounding an already-known in-training disparity.

## 8. Why other candidates were not primary

- **BMI-Obese:** not selected as primary due to the severe (70.27%) positive-case reduction in
  the remaining training population — a training-integrity confound independent of the
  researcher's instruction. This is documented as a genuine open candidate for future work (see
  Phase 9 handoff), not dismissed as uninteresting.
- **Age-60+:** not selected as primary for the same class of reason (48.50% positive-case
  reduction), though its impact is more moderate than BMI-Obese's. Also documented as a candidate
  for future work.

## 9. Discovery vs. confirmation — explicit statement

**This was PATH B: a prior researcher commitment, confirmed feasible by the candidate matrix.**
It is not presented, and must not be read, as an independent discovery by the matrix.
