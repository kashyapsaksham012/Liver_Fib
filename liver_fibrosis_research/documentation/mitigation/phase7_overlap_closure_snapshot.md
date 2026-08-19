# Phase 7 Overlap-Closure — Pre-Closure Snapshot

**Timestamp (live):** 2026-08-19 21:14:05 +0530

Recorded before any investigation or new artifact is created, per Part 2. Does not overwrite any
earlier Phase 7 snapshot (`documentation/mitigation/phase7_pre_execution_snapshot.md` remains
unmodified).

## Git state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `586341e447429e9dea24a07556a1e46150603d39` |
| Working tree | Clean (0 uncommitted, 0 untracked) |
| Upstream | `origin/main`, up to date |

## Artifact hashes (SHA-256, live-computed, before this pass's edits)

| File | SHA-256 |
|---|---|
| `PHASE7_MITIGATION_RESULTS_REPORT.md` | `dc8029990785e98bd1033b20539a315d486fe5c9eb02230a74b8704a5742f77b` |
| `documentation/mitigation/MITIGATION_PROTOCOL_FREEZE.md` | `b8cffee52f39d3b20056c0071ea202d01bd8649bc9c8f12d9945d9360813f48d` |
| `documentation/mitigation/phase7_justification_determination.md` | `03647e34393fad05522643ba1bf2513cd47f396de9e4527c08afadc73267b7fd` |
| `results/predictions/test_predictions_logistic.csv` (baseline, Phase 3, read-only reference) | `87fa5df55f55ae749e70205eaab0fb6a57b0650e25fa901a824b15ccd1a8cd45` |
| `results/mitigation/test_set_mitigation_final.csv` (mitigated, Phase 7 Commit D, read-only reference) | `e496fc8401c35b7aa27910aff8de870a973697267d5a49d4ecbde4db9c40df43` |
| `results/uncertainty/test_set_prediction_sets.csv` (baseline coverage per-participant, Phase 6 Commit C, read-only reference) | `527969c3529389d3e857e4e86e66e0aab06cc5e5784e73a48d471f155f175506` |
| `results/mitigation/group_specific_thresholds.csv` (Phase 7 Commit C, read-only reference) | `4cbc3070492af57b567174c09c28e8193517a809d5ab26fe0b1823a339a445ea` |

## Scope confirmation

This pass will not reopen `data/processed/splits/test_ids.csv`, will not regenerate model
predictions, will not rerun conformal calibration, will not alter the mitigation protocol or
targets, and will not modify any Phase 3–6 artifact. It re-partitions the already-frozen
per-participant output in `results/uncertainty/test_set_prediction_sets.csv` (baseline) and the
mitigated in-set/out-of-set status already computed inside
`src/phase7_04_final_test_touch.py`'s logic (re-derivable deterministically from the already-frozen
`group_specific_thresholds.csv` applied to the already-frozen per-participant probabilities —
no new probability, no new threshold, no new raw data access).
