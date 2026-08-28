# Test suite

Standalone validation scripts (project convention — not pytest). Each prints a
`N passed, M failed` summary and exits non-zero on any failure.

## Run

```bash
cd liver_fibrosis_research
python3 -m venv .venv && .venv/bin/pip install -r requirements-phase3-lock.txt
for t in tests/test_*.py; do .venv/bin/python "$t" || echo "FAILED: $t"; done
```

The suite reads only committed artifacts, source, and documentation — it loads no
raw data for re-scoring and never touches the locked test set.

## Last full run — 2026-08-28 (clean venv from `requirements-phase3-lock.txt`)

**18 scripts · 667 checks · 0 failed · 0 crashed.**

| Script | Checks |
|---|---|
| `test_afcp_faithful.py` | 8 |
| `test_calibration_pipeline.py` | 109 |
| `test_deferred_sensitivity_pipeline.py` | 40 |
| `test_fairness_pipeline.py` | 92 |
| `test_mi_closure_reconciliation.py` | 30 |
| `test_mitigation_pipeline.py` | 34 |
| `test_multiple_imputation_sensitivity.py` | 37 |
| `test_phase4_closure.py` | 43 |
| `test_phase6_closure_clarification.py` | 24 |
| `test_phase7_overlap_closure.py` | 19 |
| `test_phase7_threshold_overlap_closure.py` | 23 |
| `test_phase8_subgroup_holdout.py` | 35 |
| `test_prepub_fixes.py` | 19 |
| `test_prov_closure.py` | 7 |
| `test_reliability_extension.py` | 29 |
| `test_source_of_truth.py` | 16 |
| `test_training_time_mitigation.py` | 52 |
| `test_uncertainty_pipeline.py` | 50 |

## 2026-08-28 maintenance (Amendment #20 addendum — no analysis re-run, no result changed)

The 2026-08-27 documentation consolidation and Amendments #13–19 had left several checks
stale. Fixed:

- **`requirements-phase3-lock.txt`** was missing `tabulate` (needed by `prepub_01/02`) — added
  (`tabulate==0.10.0`).
- **Moved-doc reads** (5 scripts): a `_doc()` helper now resolves a documentation path to its
  `documentation/archive/process_trail/…` location when the consolidation moved it there
  (`test_calibration_pipeline`, `test_uncertainty_pipeline`, `test_phase8_subgroup_holdout`,
  `test_mi_closure_reconciliation`, `test_phase4_closure`).
- **Forward-leakage guards** (`test_calibration_pipeline` T19, `test_fairness_pipeline` T23,
  `test_uncertainty_pipeline` T21): the "downstream results/ dir must not exist yet" form is
  obsolete now that all phases have run; converted to the structural guarantee it proxied —
  *phase-N scripts never write into a downstream-phase output tree*.
- **Obsolete "not executed yet" bookkeeping** (`test_deferred_sensitivity_pipeline` T14,
  `test_multiple_imputation_sensitivity` T17/T19, `test_phase6_closure_clarification` T5/T9,
  `test_mi_closure_reconciliation` T4, `test_phase4_closure` T6/T10): the analyses these guards
  forbade were subsequently executed under dated amendments (#12/#13/#14/#16) or the human
  spot-check was completed (commit `187ba3a`). Each check was updated to the current, documented
  state.
- **`test_mitigation_pipeline` T14**: the "only `phase7_04` touches test-derived data" check was
  flagging `phase7_05/06/07` + `phase7_mitigation_cleanup`, which only *re-read* the frozen
  `test_set_prediction_sets.csv`. Split into (a) no `phase7_*` script re-scores the raw locked
  test set, and (b) the frozen-artifact readers are the documented allowlist.
- **`results/end_to_end/protocol_amendment_reconciliation.csv`** row `num=10` has an unquoted
  comma (12 fields vs an 11-column header). It is a frozen artifact and was **not** modified;
  `test_phase4_closure` now reads it with `on_bad_lines="skip"` (it only needs the well-formed
  `num=8` row).
