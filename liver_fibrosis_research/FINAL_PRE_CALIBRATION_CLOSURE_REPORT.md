# Final Pre-Calibration Closure Report

**Generated:** 2026-08-18, live, in a repository session with continuous direct git/filesystem
access throughout.

## 1. Repository Access

Confirmed real, live access at the start of this pass and throughout (git commits created,
files read and written, tests executed — all with real output shown in this report). No
hypothetical or simulated execution occurred at any point.

## 2. Scope of This Pass

Per the task's explicit instruction, this pass did **not** re-run the full Phase 1-3 audit. It
performed exactly four new activities: (1) a source-of-truth/duplication audit distinct from any
prior audit, (2) creation and standalone commit of the Calibration protocol freeze, (3) recording
that commit's hash, and (4) preparing (not performing) the human spot-check handoff. Calibration,
Fairness, Uncertainty, and Conformal Prediction execution were explicitly out of scope and were
not performed.

## 3. Prior Evidence Relied Upon (Not Re-Verified This Pass)

Per Part 1's 20-item list, treated as settled prior evidence: Phase 1 cohort definitions and
counts (primary cohort N = 7,153); SEQN-based record linkage; outcome N = 666 positive / 6,487
negative (9.31% prevalence); train N = 5,007 / test N = 2,146 split; 10 primary predictors; 5
primary models; 84 hyperparameter configurations (independently re-verified twice in the prior
audit pass via AST parse); 7 protocol amendments (individually enumerated in the prior pass, 4
scientific + 3 governance); 44/44 validation tests (20 Phase 1 + 24 Phase 3); test-set
non-contamination in hyperparameter search (structural, code-inspection-based); MLP sensitivity
results (AUC 0.8229 vs 0.8335); baseline discrimination metrics for all 5 models; cross-phase
consistency; and reproducibility/environment evidence. None of these were reopened; no active
conflict was found this pass that would justify reopening any of them.

## 4. Source-of-Truth Audit (New This Pass)

Full detail: `results/pre_calibration/source_of_truth_matrix.csv` (7 rows) and
`tests/test_source_of_truth.py` (16 live-executed assertions, 16/16 passed). Objects audited:
cohort mask definitions, primary predictor list, primary outcome threshold, hyperparameter grid
source, protocol constants (seed/CV-folds/train-fraction), variable metadata, and the previously
disclosed Phase2-doc-to-phase3_common.py transcription limitation.

**Result: zero active conflicts.** Three genuine duplication risks were found and are now
enforced against drift by the new test:
- Primary predictor list independently re-typed (but currently identical) across 5 files.
- Primary outcome threshold (`PRIMARY_THRESHOLD = 8.2`) independently defined (but currently
  identical) in 2 files.
- MLP hyperparameter grid duplicated (but currently identical) between the primary training
  script and the sensitivity-analysis script.

Three historical Phase 1 audit scripts (`03_audit_lux_demo_bmx.py`, `12_subgroup_outcome_
feasibility.py`, `18_generate_phase1_report.py`) independently compute a cohort-like mask rather
than importing `src/_cohorts.py`, but are confirmed inert — grep-verified this pass to be
referenced by zero `phase2_*`/`phase3_*` scripts, so they pose no active drift risk to the current
pipeline. Variable metadata (`_common.py:VAR_METADATA`) has no duplicate anywhere.

## 5. Active Source Conflicts

**None found.** No fix was therefore required (Step 3 of this task's execution order was a no-op,
correctly, given the finding in §4).

## 6. Fixes Applied

No source-code fixes were applied (none were needed). One preventive artifact was added:
`tests/test_source_of_truth.py`, which will fail loudly in the future if any of the three
identified duplicate-but-currently-matching definitions above are ever edited without updating
the others.

## 7. Calibration Protocol Status

**Frozen.** `documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md` (18 subsections) is
complete and cross-checked against all 5 existing Phase 2 protocol documents (`PHASE2_PROTOCOL_
FREEZE.md`, `evaluation_metrics_protocol.md`, `statistical_analysis_plan.md`, `model_development_
protocol.md`, `uncertainty_protocol.md`) — no conflicts found; no amendment to any Phase 2
document was required. The document explicitly states "Calibration execution has not begun,"
which is true as of this report (live-checked: no calibration metric, plot, or recalibration
model exists anywhere in the repository outside the unrelated, pre-existing conformal-calibration
split reserved for the future Uncertainty phase).

Key decisions frozen: model set = 5 original models only (MLP_balanced explicitly excluded from
primary status); calibration data separation = CV-OOF diagnostic tier (repeatable) + one-time
locked-test-set confirmatory tier (never `conformal_calibration_ids.csv`, which is reserved for
a different phase and is not even a clean held-out set for these specific frozen models); primary
metrics = intercept/slope/Brier (inherited unchanged from Phase 2); secondary = calibration curve
(10 deciles) + ECE (inherited unchanged); recalibration method genuinely left open pending
diagnostic findings, with only the anti-leakage boundary (CV-OOF only, never the test set)
pre-committed; CIs and multiple-comparison handling disclosed as inherited from the Phase 3
bootstrap/FDR amendment precedent, not a Phase 2 freeze (statistical_analysis_plan.md was
live-grepped this pass and confirmed to contain zero bootstrap/FDR mentions).

## 8. Standalone Calibration Commit

**Done.** Commit `2436d9554647c65af43e7d8cc61cdfeed9fb9a6a`, containing exactly one file
(`documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md`, live-verified via `git show
--name-only`), committed separately from the source-of-truth audit artifacts (commit `194aa69`,
prior) and separately from the commit-record/spot-check update (commit `cf44f44`, after). No
implementation code exists in this commit or anywhere in the repository at this point. Full
record, including the SHA-256 checksum of the protocol document at commit time: `documentation/
calibration/calibration_protocol_commit_record.md`.

## 9. Human Spot-Check Status

**HUMAN SPOT-CHECK — NOT YET PERFORMED.** `documentation/end_to_end/human_spot_check.md` was
updated (not replaced — original content retained) to make the primary recommended target locked
test-set integrity: `wc -l` (expect 2,147 lines including header) and `shasum -a 256` on
`data/processed/splits/test_ids.csv`, with this pass's live-computed hash
(`a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779`) recorded for the user to
compare against their own independently computed hash. The original hyperparameter-count
instructions remain as a secondary option. No human has performed either check yet; this AI has
not fabricated or claimed to substitute for that check.

## 10. Historical Provenance Limitation

Unchanged from the prior audit pass: Phase 2 and Phase 3 remain bundled in a single commit
(`c9c6ee3`), so sub-commit-granularity chronology for those decisions (e.g., outcome threshold
predates model-training code) remains Tier D (timestamp-only), not Tier A (commit-level). This
pass does not resolve that retroactively — it only ensures the Calibration protocol going
forward has clean, commit-level (Tier A) provenance, per §8 above.

## 11. Remaining Non-Blocking Limitations

- The two remaining cosmetic documentation-text duplications of `random_state=42` (in `phase3_09_
  generate_report.py` and `phase3_20_generate_remediated_report.py`, as prose strings, not
  executable logic) — Very Low severity, does not block Calibration.
- Recalibration method (if any) is genuinely undecided pending diagnostic findings — this is by
  design, not an oversight, and is explicitly not a blocker per this document's own §10 ("Not
  pre-decided as mandatory").
- Human spot-check remains unperformed — explicitly permitted to remain so without blocking
  readiness, per this task's Part 9 instructions.

## 12. Future Conformal Prerequisite

Unchanged, carried forward as prior evidence: the 5 frozen primary models (fit on the full
5,007-row training partition) are not valid for direct reuse in split conformal prediction and
must be refit on `proper_train_ids.csv` (N = 4,005) before any conformal code runs. This refit is
explicitly a future Uncertainty-phase prerequisite, not a Calibration-phase task, and was not
touched this pass.

## 13. Final Readiness Decision

**READY FOR CALIBRATION.**

Basis: no active source-of-truth conflicts were found; the Calibration protocol is fully frozen,
cross-checked against Phase 2, and committed in its own standalone, execution-free commit with a
recorded hash and checksum; the anti-leakage data-separation decision is made and justified before
any execution; and the human spot-check handoff is correctly prepared and honestly marked as not
yet performed, which per this task's own instructions does not block readiness.
