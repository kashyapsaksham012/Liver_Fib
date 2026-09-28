# Liver Fibrosis ML Reliability Study — repository root

[![tests](https://github.com/kashyapsaksham012/Liver_Fib/actions/workflows/tests.yml/badge.svg)](https://github.com/kashyapsaksham012/Liver_Fib/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Evidence freeze](https://img.shields.io/badge/evidence--freeze-2026--08--27-blue)](https://github.com/kashyapsaksham012/Liver_Fib/releases/tag/evidence-freeze)

This repository contains a single research project: a calibration / fairness / uncertainty
audit of routine-data machine-learning models for **significant liver fibrosis**, built on
NHANES 2017–March 2020. The study is complete and frozen at its pre-manuscript evidence
freeze (git tag `evidence-freeze`).

**The project lives in [`liver_fibrosis_research/`](liver_fibrosis_research/).**
Everything at this top level is orientation only.

## Where to start

1. [`liver_fibrosis_research/documentation/START_HERE.md`](liver_fibrosis_research/documentation/START_HERE.md)
   — **read first, before citing any number.** The research question, cohort, and models, plus
   the documentation authority order, what is superseded, and the four adjudicated internal
   conflicts (C1–C4).
2. [`liver_fibrosis_research/documentation/final_audit/REPRODUCIBILITY.md`](liver_fibrosis_research/documentation/final_audit/REPRODUCIBILITY.md)
   — environment, seeds, input data, and the exact script run order.
3. [`liver_fibrosis_research/documentation/manuscript/MANUSCRIPT_DRAFT.md`](liver_fibrosis_research/documentation/manuscript/MANUSCRIPT_DRAFT.md)
   — working draft (v5), every numeric claim traced to a frozen result artifact.

`info.md` (this directory) is the original research brief the project was scoped from —
kept as historical context, not a current source.

## Model card / datasheet / citation

- [`liver_fibrosis_research/MODEL_CARD.md`](liver_fibrosis_research/MODEL_CARD.md) — intended
  use, performance, and the fairness/reliability limitations, grounded in the frozen results.
- [`liver_fibrosis_research/DATASHEET.md`](liver_fibrosis_research/DATASHEET.md) — the NHANES
  analysis cohort: composition, collection, preprocessing, known caveats.
- [`CITATION.cff`](CITATION.cff) — machine-readable citation (GitHub's "Cite this repository").
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — read before opening a PR; the core study is a frozen,
  append-only evidentiary ledger, not a conventional codebase.

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

- ~~Four of the 17 scripts in `liver_fibrosis_research/tests/` reference documentation paths
  that the 2026-08-27 consolidation moved...~~ **Resolved.** The `_doc()` fallback-path helper
  (documented in `liver_fibrosis_research/tests/README.md`, "2026-08-28 maintenance") already
  fixes this. Verified 2026-09-28: all 18 scripts in `liver_fibrosis_research/tests/` pass with
  0 failures (`for t in liver_fibrosis_research/tests/test_*.py; do .venv/bin/python "$t"; done`).
  This bullet was stale — left here so the "it used to be broken" history isn't lost.
- No external (non-NHANES) validation has been performed — the study's foremost stated
  limitation.
- `requirements.txt` and `requirements-phase3.txt` look like avoidable duplicates but are
  **not safe to collapse**: both are named explicitly, by filename, in the frozen
  `liver_fibrosis_research/documentation/final_audit/REPRODUCIBILITY.md` ("`requirements.txt`
  and `requirements-phase3.txt` are the unpinned/earlier variants") as historical artifacts of
  what was actually installed at each stage. Deleting or rewriting either breaks that
  documented, frozen claim's verifiability. `requirements-phase3-lock.txt` remains the
  authoritative file to install from; leave the other two as read-only history.
