# Subgroup Provenance Status

**Generated:** 2026-08-18 (final end-to-end audit) — live re-check performed this pass.

## Live git evidence

```
$ git log --follow --oneline -- documentation/phase2/fairness_subgroup_protocol.md
c9c6ee3 Phase 2 protocol freeze, Phase 3 baseline ML, and Phase 3 remediation/closure
```

The file now has exactly **one** commit in its history: `c9c6ee3`. That same commit also
contains every Phase 3 training script and model artifact — so while the file's *existence* is
now commit-provable, its ordering *relative to Phase 3 model training* is not, because both are
in the identical commit.

## Required statement (per the governing language rule)

> **Historical pre-specification of subgroup bins could not be independently established from
> strong repository provenance.**

File modification time (14:21:08, per the prior audit) and this conversation's turn ordering are
**not** treated as equivalent to commit-level proof, per the standing rule. Neither is upgraded
to a stronger evidence tier here.

## What IS verified (present-tense, current state)

- **Sex bins:** Male, Female — `fairness_subgroup_protocol.md` Section 1.
- **Race/ethnicity bins:** RIDRETH3, all 6 native categories, none collapsed — Section 2.
- **Age bins:** 18–39, 40–59, 60+ — Section 3.
- **BMI bins:** WHO standard categories (Underweight/Normal/Overweight/Obese) — Section 4.
- These are now **committed and frozen as of `c9c6ee3`** (2026-08-18 17:57:33 +0530) — this
  commit timestamp IS strong (Level A/commit-level) evidence that, from this point forward, the
  bins are fixed and any future change would require a new, separately-timestamped commit.
- **Fairness analysis has not started** (confirmed live this audit: `find . -iname "*fairness*result*"`
  → no result files exist anywhere in the repository) — so even under the weakest possible
  provenance reading, there is no fairness *result* the bins could have been reverse-engineered
  from. This mitigates, but does not eliminate, the provenance gap.

## Forward-looking commitment

Any future modification to these bins, made after fairness analysis has produced a result, would
need to be logged as a post-hoc amendment with explicit clinical/methodological justification —
not silently applied. The bins as they exist in the current commit are the ones that will be used
when the Fairness phase begins.
