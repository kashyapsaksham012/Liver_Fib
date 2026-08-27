# Phase 4 Closure Verification Report

**Generated:** 2026-08-19, live, in a session with continuous direct git/filesystem access
throughout. This pass closes 3 of 4 targeted reporting/provenance issues in the already-complete
Phase 4 Calibration analysis; it does not reopen, re-derive, or reinterpret the headline
scientific finding, and it does not touch the locked test set.

## 1. Executive Summary

Items 1–3 (MLP quantitative parity, Calibration FDR-family separation, Amendment #8 registry
continuity) are closed, each with a real, code-or-artifact-level verification, not a prose
restatement. One genuine bug was found and fixed along the way: a malformed CSV
(`mlp_calibration_metric_audit.csv`, an unquoted comma inside a field) and one stale secondary
artifact (`protocol_amendment_reconciliation.csv`, missing Amendment #8) — both disclosed and
corrected, not silently absorbed. Item 4 (human spot-check) remains, correctly, **researcher-only
and NOT YET PERFORMED** — this AI did not run it, fabricate a result, or claim completion.

## 2. Current Phase 4 Status

Unchanged: **PHASE 4 COMPLETE — READY FOR FAIRNESS** (established in
`PHASE4_CALIBRATION_RESULTS_REPORT.md`). This closure pass adds supporting detail and
verification artifacts; it does not alter that status, the model set, the recalibration
decision, or any numeric finding.

## 3. Item 1 — MLP Quantitative Calibration Reporting

**What was checked:** Located the actual authoritative files (not assumed):
`results/calibration/primary_metrics_by_model.csv` (OOF point estimates) and
`results/calibration/calibration_inference.csv` (bootstrap CIs) — the same files, same
methodology, used for all 5 models. Extracted MLP's OOF intercept (−0.280858, CI
[−0.465988, −0.084605]), slope (0.829627, CI [0.754584, 0.914947]), and Brier (0.070972, CI
[0.065632, 0.076728]) directly from these files — no separate computation, no different data
source. Also opened the existing `results/calibration/test_set_calibration_final.csv` (without
re-running it) and confirmed MLP's raw and recalibrated test-set point metrics are present
(intercept −0.435428 raw / −0.118930 recalibrated; slope 0.929347 / 1.121055; Brier 0.071641 /
0.071485; ECE 0.029026 / 0.026373).

**What was found:** MLP's intercept CI does **not** include 0 (both bounds negative). Stated
precisely, per the task's explicit instruction, as: MLP's calibration intercept was
statistically distinguishable from 0 under the specified bootstrap procedure — not translated
into "MLP is well calibrated" or "perfectly calibrated." No test-set CI exists for **any** of
the 5 models (not an MLP-specific gap) — the frozen protocol's inference section (§12) only
required OOF-tier bootstrap CIs; test-set evaluation was point-estimate-only by original
protocol design. This is disclosed, not treated as a defect requiring a test-set re-touch.

**Whether anything was corrected:** Yes — one genuine bug: the newly created
`results/calibration/mlp_calibration_metric_audit.csv` initially had an unquoted comma inside
the `tier` field ("locked test set (confirmatory, one-time touch)"), which broke CSV parsing
(`pandas.errors.ParserError` on first test run). Rewritten via pandas' own CSV writer to
guarantee correct quoting; re-parse verified successful.

**Exact file paths:**
- `results/calibration/primary_metrics_by_model.csv` (source, unmodified)
- `results/calibration/calibration_inference.csv` (source, unmodified)
- `results/calibration/test_set_calibration_final.csv` (source, read-only, NOT re-touched)
- `results/calibration/mlp_calibration_metric_audit.csv` (new, Item 1 deliverable)
- `PHASE4_CALIBRATION_RESULTS_REPORT.md` §9 (updated: unified 5-model table with CI columns for
  intercept, slope, and Brier, plus an explicit MLP-intercept-vs-zero sentence)

**Verification result:** `tests/test_phase4_closure.py` TEST1–TEST3 (14 individual checks) —
PASS.

## 4. Item 2 — Calibration FDR Family Separation

**What was checked:** Opened the actual code, not just the prose claim already in the report:
`src/phase4_04_inference.py` (Calibration's inference implementation) and
`src/phase3_07_plots_and_comparison.py` (Phase 3's model-comparison implementation). Confirmed,
by reading both files end-to-end, that Phase 3 computes a single 10-pair ROC-AUC family
(`pairs = list(combinations(MODEL_NAMES, 2))`, one `raw_p` array, written to
`results/tables/phase3_model_comparison.csv`), while Calibration computes three separate
10-pair families (intercept, slope, Brier), each with its own `pair_pvals` list
re-initialized inside a `for metric in [...]:` loop, written to
`results/calibration/calibration_inference.csv`. Neither script references the other's output
file or p-value array.

**What was found:** The separation the report already claimed in prose is genuinely
code-supported — no pooling occurred. Bootstrap *methodology* (n=2,000, seed=42, paired,
95% CIs, BH-FDR) is deliberately reused from Phase 3 (disclosed in the frozen protocol §12 as
inheriting Amendment #2); the *hypothesis families being corrected* are structurally disjoint.
This nuance — methodology reuse with family independence — is stated explicitly rather than
forced into a false "reused vs. distinct" binary.

**Whether anything was corrected:** No code change was needed (none was pooled incorrectly).
The report's §17 was strengthened with the exact required sentence and a pointer to the new
verification document, since an implied separation was judged insufficient per this task's
own standard.

**Exact file paths:**
- `src/phase4_04_inference.py` lines 76–99 (Calibration's 3 independent families)
- `src/phase3_07_plots_and_comparison.py` lines 91–113 (Phase 3's single family)
- `documentation/calibration/calibration_fdr_family_verification.md` (new, Item 2 deliverable)
- `PHASE4_CALIBRATION_RESULTS_REPORT.md` §17 (updated: explicit separation sentence + code
  citation)

**Verification result:** `tests/test_phase4_closure.py` TEST4–TEST5 (9 individual checks) —
PASS.

## 5. Item 3 — Amendment #8 Registry Continuity

**What was checked:** Located Amendment #8's actual recorded location
(`documentation/end_to_end/protocol_amendment_registry.md`, row 8 of the single existing table
— confirmed via `grep`, not assumed). Searched the whole repository for any file matching
`*amendment*` to check for a competing registry: found 2 additional files —
`documentation/phase3/inference_methodology_amendment.md` (a detail document for the
already-listed Amendment #2, not an independent registry — no numbering conflict) and
`results/end_to_end/protocol_amendment_reconciliation.csv` (a machine-readable derived copy of
the same registry, same numbering/categories, used by the earlier pre-Calibration closure
pass's programmatic reconciliation).

**What was found:** The reconciliation CSV was **stale** — it stopped at row 7 and had not been
updated when Amendment #8 was added to the authoritative `.md` registry, a real inconsistency
matching exactly the "two registries silently diverging" risk this task's Part 4D warned about.
Its row 4 (conformal calibration partition) status note was also stale ("calibration itself not
yet run" — no longer true).

**Whether anything was corrected:** Yes — the CSV was updated (Option A: merge into
consistency) to add row 8 with matching field values, and row 4's status note was corrected to
reflect that Calibration has run and confirmed non-use of that partition (the partition's
still-open/unconsumed status itself was not changed — only the stale parenthetical). Amendment
#8's row in the authoritative `.md` registry was not altered — it was already correct,
including the explicit sentence "the locked test set was not inspected before this choice was
made," satisfying the task's requirement not to leave this to implication.

**Reconciliation:** 4 previously classified scientific/methodological + 3 governance/
documentation + 1 new Phase 4 scientific/methodological (Amendment #8) = **8**. No earlier
amendment was reclassified.

**Exact file paths:**
- `documentation/end_to_end/protocol_amendment_registry.md` (source of truth, row 8 unmodified,
  already correct)
- `results/end_to_end/protocol_amendment_reconciliation.csv` (corrected this pass: row 8 added,
  row 4 status note updated)
- `results/calibration/amendment_8_reconciliation.csv` (new, Item 3 deliverable, 13 checks)
- `documentation/calibration/amendment_8_provenance.md` (new, Item 3 deliverable)

**Verification result:** `tests/test_phase4_closure.py` TEST6–TEST9 (7 individual checks) —
PASS.

## 6. Item 4 — Human Spot-Check Status

**Human spot-check remains researcher-only and is not closed by this task.**

Active instruction file confirmed: `documentation/end_to_end/human_spot_check.md` (primary
target: locked test-set integrity, SHA-256 of `test_ids.csv` or direct N=2,146 count). Record
template: `documentation/end_to_end/human_spot_check_record_template.md` — live-checked this
pass and confirmed still genuinely blank (`_____` placeholders throughout, "Date performed,"
"Researcher (name)," and "Observed result" all unfilled). No command was executed on the
researcher's behalf, no name was filled in, no output was fabricated, and no PASS/FAIL was
recorded. **STATUS: NOT YET PERFORMED.**

## 7. Headline Scientific Finding — Unchanged

Verified unchanged in `PHASE4_CALIBRATION_RESULTS_REPORT.md`: ROC-AUC 0.8229–0.8429 across 5
models (Phase 3, unchanged); no significant pairwise discrimination difference after FDR
correction; calibration intercepts for Logistic/Random Forest/XGBoost/LightGBM approximately
−1.86 to −2.24, CIs excluding 0; MLP comparatively closer to 0 (−0.280858 OOF, CI
[−0.465988, −0.084605] — itself excluding 0, not "perfectly calibrated"); confirmed on the
locked test set, touched exactly once; consistent with the pre-specified H2 expectation, using
the required non-overclaiming phrasing throughout. This closure pass added CI columns and a
code-level FDR-separation verification — it did not change any point estimate, any CI bound, any
model's classification as primary/sensitivity, or the interpretive language.

## 8. Files Modified

| File | Nature of change |
|---|---|
| `PHASE4_CALIBRATION_RESULTS_REPORT.md` | §9 table expanded with CI columns for all 5 models + explicit MLP-vs-zero sentence; §17 strengthened with explicit separation sentence + code citation |
| `results/end_to_end/protocol_amendment_reconciliation.csv` | Row 8 added (Amendment #8); row 4's stale status note corrected |
| `results/calibration/mlp_calibration_metric_audit.csv` | New (Item 1) — rewritten once after a CSV-quoting bug was found and fixed |
| `documentation/calibration/calibration_fdr_family_verification.md` | New (Item 2) |
| `results/calibration/amendment_8_reconciliation.csv` | New (Item 3) |
| `documentation/calibration/amendment_8_provenance.md` | New (Item 3) |
| `documentation/calibration/phase4_closure_pre_snapshot.md` | New (Part 1 pre-closure snapshot) |
| `tests/test_phase4_closure.py` | New (Part 9) |

No file under `results/calibration/test_set_calibration_final.csv`,
`test_set_recalibrated_predictions.csv`, or `curve_data_test_set_final.csv` was modified —
the locked test set was not re-touched.

## 9. Tests Executed

`tests/test_phase4_closure.py`, run live: **41/41 checks passed**, covering all 10 required
test categories. One test bug found and fixed before the final run (TEST4's separation-sentence
search failed on a markdown line-wrap, not a real report problem — fixed by normalizing
whitespace before the substring search, disclosed here rather than silently patched).
`tests/test_calibration_pipeline.py` (the prior Phase 4 suite) re-run for regression safety:
**109/109 still passing**, confirming this closure pass did not break anything upstream.

## 10. Remaining Limitations

- No test-set bootstrap CIs exist for any model (protocol-design characteristic, not a gap
  introduced or found problematic this pass) — disclosed in Item 1, not treated as blocking.
- The Phase 2/Phase 3 bundled-commit (Tier D) provenance limitation remains unchanged, carried
  forward from prior audits, unaffected by this pass.
- Item 4 (human spot-check) remains open by design — this is expected, not a defect.

## 11. Final Readiness for Phase 5

Items 1–3 are genuinely closed with code/artifact-level verification, not prose restatement.
Item 4 is intentionally left open, researcher-only. No test-set re-touch, no Calibration rerun,
and no Phase 5/6 execution occurred in this pass.
