# Calibration Protocol Commit Record

**Generated:** 2026-08-18, immediately after the commit below, by live `git show` inspection
(not restated from memory).

## Commit

| Field | Value |
|---|---|
| Commit hash | `2436d9554647c65af43e7d8cc61cdfeed9fb9a6a` |
| Author date | 2026-08-18 20:52:52 +0530 |
| Author | Saksham Kashyap |
| Branch | `main` (local; `origin/main` remains at `b390fbe`, unrelated — this commit has not been pushed) |
| Parent commit | `194aa69` (the immediately preceding, separate source-of-truth-audit commit) |

## Files committed (live-verified, exactly one file)

```
liver_fibrosis_research/documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md
```

Verified via `git show --name-only --pretty="" 2436d95` this pass — no other file, and
specifically no implementation/execution code, is part of this commit.

## Protocol document checksum

SHA-256 (computed immediately before staging, matches the committed content):

```
3c843ad02cd91736a597ad3256a6c6309ffac2819a882c72f77b9220c64fca1d  documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md
```

## Confirmation: execution had not started at commit time

Live-checked this pass, immediately after the commit:

```
find . -iname "*calibrat*" -not -path "*/documentation/calibration/*" -not -path "*/.git/*"
```

returned only: (1) the pre-existing `conformal_calibration_ids.csv` split and its associated
Phase 3 reservation script/protocol doc — these belong to the **separate, future Uncertainty
phase's** split-conformal-prediction calibration set (see §6 of the frozen protocol document for
why this is explicitly not the same thing), and predate this commit; and (2) files inside
`scikit-learn`'s own installed package (`sklearn/calibration.py` and its test file) — third-party
library source, not project output. No project-generated calibration metric, plot, recalibration
model, or results file of any kind exists anywhere in the repository as of this commit.

## Relationship to prior provenance findings

This commit exists specifically to produce commit-level (Tier A) provenance for the Calibration
protocol's freeze date, in contrast to the Phase 2 outcome-threshold, predictor-list, fairness-bin,
and missing-data-strategy decisions, which remain Tier D (timestamp-only) because they share a
single bundled commit (`c9c6ee3`) with the Phase 3 execution code that used them. That limitation
is unchanged by this commit and is not claimed to be resolved retroactively — only the Calibration
protocol going forward benefits from clean commit-level separation.
