# `stage1/` file index

This directory carries at least one pair of same-purpose files where one superseded the
other after a defect was found. Frozen result files are never edited or deleted (see the
top-level provenance discipline), so both remain on disk — use this index instead of
guessing from the filename.

- **`fairness_postprocessing_results.csv` — SUPERSEDED, UNVERIFIED/UNTRUSTED.** Has a
  raw-vs-recalibrated scale-mismatch defect (reported baseline Logistic sensitivity 0.10,
  which is the raw-probability threshold applied to recalibrated-scale scores). Produced by
  `src/sens_07_fairness_postprocessing.py`. Do not cite this file for any manuscript claim.
- **`correct_fairness_postprocessing_results.csv` — the corrected replacement.** Produced by
  `src/sens_09_correct_fairness_postprocessing.py`. This is the file backing the
  equal-opportunity post-processing numbers in the manuscript (e.g. the normal-BMI
  specificity drop and excess-false-positive counts in the Robustness/exploratory section).

Full reasoning: `documentation/final_research_audit/SUPERSEDED_INVALID_RESULTS.md` (item
around `S9`/E5) and `documentation/final_research_audit/EXPLORATORY_RESULTS.md` (E5).
