# Contributing

Before opening a pull request, read this — it will save you writing a diff that gets rejected on
sight.

## This repository is a frozen, append-only evidentiary ledger, not a conventional codebase

The core study (tiers 1–2: `liver_fibrosis_research/src/`, `results/`, `models/phase3` +
`phase6_conformal_refit` + `phase8_holdout`, the phase/audit `documentation/` trees, root
`PHASE*_REPORT.md` files) is frozen at git tag `evidence-freeze`. **No file under those paths is
moved, renamed, or edited, ever** — full rationale in
`liver_fibrosis_research/REPOSITORY_MAP.md` §1. Scripts hard-code paths, artifacts are
hash-verified, and the study's credibility rests on this tree being demonstrably append-only.
A PR that reformats, renames, or "cleans up" anything under those paths will be closed without
review, regardless of how correct the change is in isolation.

This is not neglect — it's the opposite. See `liver_fibrosis_research/REPOSITORY_MAP.md` for the
five-tier structure and `liver_fibrosis_research/documentation/START_HERE.md` for the frozen
study's internal authority order.

## What you *can* contribute

- **New evidence tiers.** Extensions like `temporal_validation_2021_2023/` and
  `pooled_model_update_2017_2023/` are the model: a self-contained module with its own
  `PROTOCOL_FREEZE.md`, `FROZEN_ARTIFACT_MANIFEST.csv`, `src/`, `results/`, `documentation/`,
  and a verification harness — that adds evidence without touching anything upstream.
- **Fixes to genuinely broken, non-frozen tooling** — e.g. the test-path issues noted in the
  root `README.md` "Known follow-ups" section, or `.github/workflows/`, or documentation *outside*
  the frozen trees (this file, `REPOSITORY_MAP.md` navigation text, `SUBMISSION_PACKAGE.md`).
- **Issues** reporting a discrepancy between a manuscript claim and a `results/**/*.csv` number —
  those CSVs are the authority; if you find a mismatch, that's a real bug report.

## Before you file anything

1. Read `liver_fibrosis_research/documentation/START_HERE.md`.
2. Check `liver_fibrosis_research/documentation/final_research_audit/DO_NOT_CLAIM.md` — if your
   issue is "the paper doesn't claim X," it's very likely deliberate.
3. Run the relevant verification harness (`liver_fibrosis_research/REPOSITORY_MAP.md` §5) before
   assuming a number is wrong.
