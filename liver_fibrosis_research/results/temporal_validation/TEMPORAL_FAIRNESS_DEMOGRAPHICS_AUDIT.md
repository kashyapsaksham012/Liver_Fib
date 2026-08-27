# Temporal fairness demographics audit

This preparation attached original NHANES variables only; no evaluation was performed.

- Source files: `BMX_L.xpt` (`SEQN`, `BMXBMI`) and `DEMO_L.xpt` (`SEQN`, `RIDAGEYR`, `RIAGENDR`).
- Cohort anchor: existing `temporal_validation_labels_demographics.csv`.
- Rows / unique SEQNs / duplicate SEQNs / missing SEQNs: 4910 / 4910 / 0 / 0.
- Matched from BMX_L / DEMO_L: 4910 / 4910; unmatched: none.
- Missing BMXBMI / RIDAGEYR / RIAGENDR: 0 / 0 / 0.
- The 4,910-person cohort, predictors, outcomes, models, and existing prediction files were not changed.
