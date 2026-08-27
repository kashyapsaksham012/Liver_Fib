# Liver Fibrosis ML Reliability Study — repository root

This repository contains a single research project: a calibration / fairness / uncertainty
audit of routine-data machine-learning models for **significant liver fibrosis**, built on
NHANES 2017–March 2020. The study is complete and frozen at its pre-manuscript evidence
freeze (git tag `evidence-freeze`).

**The project lives in [`liver_fibrosis_research/`](liver_fibrosis_research/).**
Everything at this top level is orientation only.

## Where to start

1. [`liver_fibrosis_research/README.md`](liver_fibrosis_research/README.md) — research
   question, cohort, models, and headline findings.
2. [`liver_fibrosis_research/documentation/START_HERE.md`](liver_fibrosis_research/documentation/START_HERE.md)
   — **read before citing any number.** Fixes the documentation authority order, records what
   is superseded, and adjudicates the four known internal conflicts (C1–C4).
3. [`liver_fibrosis_research/documentation/final_audit/REPRODUCIBILITY.md`](liver_fibrosis_research/documentation/final_audit/REPRODUCIBILITY.md)
   — environment, seeds, input data, and the exact script run order.
4. [`liver_fibrosis_research/documentation/manuscript/MANUSCRIPT_DRAFT.md`](liver_fibrosis_research/documentation/manuscript/MANUSCRIPT_DRAFT.md)
   — working draft (v5), every numeric claim traced to a frozen result artifact.

`info.md` (this directory) is the original research brief the project was scoped from —
kept as historical context, not a current source.

## Environment setup

```bash
cd liver_fibrosis_research
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-phase3-lock.txt   # authoritative pinned versions
```

`requirements-phase3-lock.txt` is the exact lock file used for the frozen results.
`requirements.txt` is the same dependency set unpinned. A single seed (`random_state=42`)
is used throughout. Raw NHANES `.xpt` inputs are public CDC/NCHS files and are included
under `liver_fibrosis_research/data/raw/NHANES_2017_2020/`.

## Branch map

| Branch | Purpose |
|---|---|
| `consolidation/evidence-freeze` | **Authoritative working branch.** All study work landed here; it carries the latest commit. |
| `main` | Release branch. `consolidation/evidence-freeze` is merged into it via pull request (last done in PR #3); its tree is identical to the evidence-freeze branch at each merge point. |
| `experiment/training-time-mitigation` | Amendment #19 work branch (subgroup-reweighting mitigation, verdict negative); its result was consolidated back into the evidence freeze. Kept for provenance. |
| `temporal-validation-standalone` | A NHANES 2021–2023 temporal evaluation that was **split into a separate manuscript** and removed from this study's scope. Not part of this repository's evidence base. |

Tags: `evidence-freeze` (pre-manuscript freeze), `pre-handover-cleanup-2026-08-28`
(state immediately before this repository tidy-up).

## Not tracked here

- `liver_fibrosis_research/.venv/` — local virtual environment, rebuild from the lock file.
- `NHANES 2021–2023 temporal validation dataset/` — raw inputs for the separate
  temporal-validation manuscript; gitignored, not part of this study.

## Known follow-ups for a new maintainer

- Four of the 17 scripts in `liver_fibrosis_research/tests/` reference documentation paths
  that the 2026-08-27 consolidation moved into `documentation/archive/process_trail/`, so
  they now error on those paths (`test_calibration_pipeline`, `test_uncertainty_pipeline`,
  `test_phase8_subgroup_holdout`) or assert against it (`test_fairness_pipeline` TEST23,
  `test_mitigation_pipeline` TEST14). The pipeline logic they cover is unchanged; only the
  path references need updating. The amendment-specific suites
  (`test_source_of_truth`, `test_prepub_fixes`, `test_training_time_mitigation`) pass.
- No external (non-NHANES) validation has been performed — the study's foremost stated
  limitation.
