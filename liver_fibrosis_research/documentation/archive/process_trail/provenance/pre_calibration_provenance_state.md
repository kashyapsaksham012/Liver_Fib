# Pre-Calibration Provenance State

**Generated:** 2026-08-18, live, immediately after independently-verified remote push.

This document records the project's provenance posture at the moment of handoff into Calibration.

## 1. Local frozen Git history

`main` at `b3669b198d42b33214e30b8dd12c73643c52a66a`, working tree clean, 12 commits spanning
Phase 1 through Pre-Calibration closure (full list: `results/provenance/frozen_commit_registry.csv`).

## 2. Remote backup

**VERIFIED.** `origin` (`https://github.com/kashyapsaksham012/Liver_Fib.git`), branch `main`, at
the same commit as local HEAD, confirmed via both `git fetch`+`rev-parse` and a direct
`git ls-remote` query. Full detail: `results/provenance/remote_backup_verification.md`.

## 3. Standalone Calibration protocol commit

`2436d9554647c65af43e7d8cc61cdfeed9fb9a6a`, single file
(`documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md`), no implementation code, confirmed
present both locally and on the remote. Commit-level (Tier A) provenance for the Calibration
protocol's freeze date — the specific gap this commit was designed to close, since Phase 2/Phase 3
remain bundled in one commit (`c9c6ee3`) with only Tier D (timestamp) provenance for their
internal chronology.

## 4. Source-of-truth drift tests

`tests/test_source_of_truth.py`, 16/16 checks passing as of this pass, committed at `194aa69`.
Guards against silent drift in the primary predictor list, outcome threshold, and MLP
hyperparameter grid — the three genuine (currently non-conflicting) duplication risks identified
in `results/pre_calibration/source_of_truth_matrix.csv`.

## 5. Archived Phase 1-3 evidence

`documentation/end_to_end/archive/END_TO_END_REPORT_v1_20260818.md` (prior end-to-end report,
archived before the v2 rewrite), plus the full audit-report trail under
`documentation/audit_reports/` and `results/end_to_end/`. All now remotely backed up.

## 6. Documented historical provenance limitations

Unchanged and still accurate: Phase 2 and Phase 3 share a single commit (`c9c6ee3`), so
sub-commit-granularity chronology within that commit is Tier D (timestamp-consistent only), not
Tier A (commit-provable). This is disclosed, not resolved, and does not block Calibration per the
prior closure report's reasoning (§10, `FINAL_PRE_CALIBRATION_CLOSURE_REPORT.md`).

## 7. Human spot-check

**NOT YET PERFORMED.** Primary target: locked test-set integrity (SHA-256 of `test_ids.csv`,
live-computed this project as `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779`).
Instructions: `documentation/end_to_end/human_spot_check.md`. Recording template (new this task):
`documentation/end_to_end/human_spot_check_record_template.md`. No AI session may mark this
performed on the researcher's behalf.

## Summary

Local history, remote backup, and the standalone Calibration protocol commit are all verified
consistent. The only remaining open item before treating readiness as fully unconditional is the
human spot-check, which is expected to remain open until the researcher performs it personally.
