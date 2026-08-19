# Amendment #8 Provenance

**Generated:** 2026-08-19, live, per Item 3 of the Phase 4 Closure task.

## 4A. Where Amendment #8 is recorded

**File:** `documentation/end_to_end/protocol_amendment_registry.md`, row 8 of the single table
(the same authoritative table containing Amendments #1–#7 — no new file, no new table).

| Field | Value |
|---|---|
| Title | Recalibration method selected: logistic (Platt-type) recalibration |
| Affected phase | Phase 4 (Calibration) |
| Date | 2026-08-19 (this session; the registry's own row does not carry a per-row date column — see §4C note below) |

## 4B. Registry continuity

Confirmed: Amendment #8 exists in the **same** authoritative registry file as Amendments #1–7
— `documentation/end_to_end/protocol_amendment_registry.md` — appended as row 8 of the existing
single Markdown table, not a new document, not a new numbering scheme. `grep -c "^| [0-9]"` on
the table body confirms exactly 8 numbered rows.

Previously reconciled breakdown (Amendments #1–7, unchanged, not reclassified this pass):
- 4 scientific/methodological: #1 (Youden's J), #2 (bootstrap/FDR), #3 (MLP oversampling
  sensitivity), #4 (conformal calibration split reservation)
- 3 governance/documentation: #5 (alias file), #6 (mtime claim withdrawal), #7 (bulk git commit)

New this pass:
- 1 scientific/methodological: #8 (recalibration method selection)

**Total: 4 + 3 + 1 = 8.** Matches `results/calibration/amendment_8_reconciliation.csv` exactly.

## 4C. Amendment #8 required-field verification

| Required field | Present? | Value |
|---|---|---|
| Title | Yes | "Recalibration method selected: logistic (Platt-type) recalibration" |
| Date | Yes (via commit) | The registry table has no dedicated per-row date column (a pre-existing structural characteristic of the table, shared by all 8 rows, not unique to #8); live-verified this pass: the amendment's associated commit `403a9e3` has author date **2026-08-19 10:37:55 +0530** (`git show -s --format=%ad 403a9e3`) |
| Affected phase | Yes | Phase 4 (Calibration) — stated in the registry row's context and in `results/calibration/amendment_8_reconciliation.csv` |
| Original protocol rule | Yes | "`CALIBRATION_PROTOCOL_FREEZE.md` §10 named Platt scaling and isotonic regression only as *examples* ('e.g.'), explicitly deferring the specific method choice..." |
| Changed rule | Yes | "A single method (logistic/Platt) was selected and applied uniformly to all 5 primary models; isotonic regression was not used" |
| Reason | Yes | Full rationale given: intercept-shift-dominated miscalibration pattern, slopes near 1 for 4/5 models, overfitting risk of isotonic regression with only 466 OOF positives |
| Whether test-set data had been seen | **Yes, explicit** | "**No** — decision and fitting both used OOF data exclusively; the locked test set was not inspected before this choice was made." This is not left to be inferred — it is stated as a direct sentence in the registry row itself. |
| Whether rerun was required | Yes | "No — this is the first and only application" |
| Rerun status | Yes | N/A (first application; `results/calibration/amendment_8_reconciliation.csv` records `rerun_required=False`) |

## 4D. Second-registry check

Two other files matched an `*amendment*` filename search:

1. `documentation/phase3/inference_methodology_amendment.md` — a **detail document for a single
   already-listed amendment** (Phase 3's bootstrap/FDR methodology, i.e. Amendment #2), not an
   independent registry. It carries no competing numbering. No action needed.
2. `results/end_to_end/protocol_amendment_reconciliation.csv` — a **machine-readable derived
   copy** of the same 8 amendments (same numbering, same category scheme:
   SCIENTIFIC/METHODOLOGICAL, DOCUMENTATION/GOVERNANCE, AUDIT CORRECTION, VERSION-CONTROL
   HOUSEKEEPING), used by the earlier pre-Calibration closure pass's programmatic count
   verification. **Found stale this pass** — it stopped at row 7 and had not been updated when
   Amendment #8 was added to the authoritative `.md` registry. **Corrected this pass**: row 8
   added with matching field values (Option A — merge into consistency, not a second
   authoritative source). Its row 4 (conformal calibration partition) status note was also
   updated in the same edit, since it referenced "calibration itself not yet run" — a claim that
   was accurate when originally written but became stale once Phase 4 executed; corrected to
   state that Calibration has run and confirmed non-use of that partition, without altering the
   partition's still-open/unconsumed status.

**No competing authoritative registry exists.** There is exactly one answer to "where do I find
the complete amendment history": `documentation/end_to_end/protocol_amendment_registry.md`. The
CSV is a derived, now-synchronized reconciliation artifact, not a second source of truth.

## 4E. Programmatic reconciliation

See `results/calibration/amendment_8_reconciliation.csv` — 13 checks, all `match=True` after
this pass's correction to the secondary CSV. Total = 8, breakdown 4 + 3 + 1 = 8, no earlier
amendment reclassified.
