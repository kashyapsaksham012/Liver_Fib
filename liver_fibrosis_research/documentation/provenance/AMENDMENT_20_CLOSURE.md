# Amendment #20 — closure

**Date:** 2026-08-28 · **Status:** COMPLETE · **Type:** provenance closure + manuscript-scope
reduction. **No scientific result changed.**
**Registry row:** `documentation/end_to_end/protocol_amendment_registry.md` row 20.

---

## Why

The forensic and final-audit passes disclosed a set of provenance gaps
(`FINAL_LIMITATIONS_REGISTER.md` H1–H3, `RESEARCH_WEAKNESSES.md` W11). Two of them touch
material that reaches the manuscript:

1. **`results/uncertainty/intersectional_coverage_ci.csv`** — the source for Table 3's
   *Obese ∩ 60+* row and the §3.5 intersection figures — entered via a bulk "finalize" commit
   (`142595d`) with only a `ci_method` note and **no committed generating script**.
2. **The frozen 8.2-kPa model-artifact manifest** was recorded as `NOT FOUND IN REPOSITORY`
   (`PHASE6_8KPA_ROBUSTNESS_REPORT.md`). The Phase-3 registry has hyperparameters/seed but no
   file hash; only the Phase-6 conformal-refit registry carries hashes, and only for its own
   five files.

Two further gaps are on **exploratory** material:

3. **MI-conformal extension** (`results/fairness_bmi_investigation/phase5_mi_conformal/*`) —
   `phase5_mi_lineage.json` missing, no committed producer (`LINEAGE NOT FOUND`).
4. **Joint-cell / M4b intersectional conformal mitigation**
   (`results/mitigation/joint_intersectional_mitigation.csv` + the M4b `N0` sweep) — generating
   script / selection manifest / runtime log `NOT FOUND` (`FINAL_LIMITATIONS_REGISTER.md` H3).

---

## Decision

| Gap | Disposition |
|---|---|
| 1. intersectional_coverage_ci.csv | **Reconstruct** — add a derivation script that reproduces it byte-identically from an artifact that *does* have committed lineage. |
| 2. model-artifact manifest | **Reconstruct** — add a hash manifest for all 32 committed `.joblib` files. |
| 3. MI-conformal extension | **Remove from the main manuscript.** Exploratory, non-load-bearing, descriptive-only; reconstruction judged higher-risk than removal. |
| 4. joint-cell / M4b mitigation | **Remove from the main manuscript.** Same rationale; it is `EXPLORATORY_ONLY` and its stated "success" already carried a marginal-tolerance breach for XGBoost/LightGBM. |

The MI **selection-question** discrimination/calibration analysis (`src/mi_01/02/03_*.py`,
full lineage; NHANES Non-Hispanic Black exclusion) and the **Phase-7 Mondrian** mitigation are
unaffected and remain in the manuscript.

---

## What ran

### `src/prov_01_derive_intersectional_coverage_ci.py`

Reads the frozen `results/mitigation/bmi_age_overlap_four_way_analysis.csv` (written by
`src/phase7_05_bmi_age_overlap_analysis.py`, which re-partitions the frozen Phase-6 "Commit C"
artifact `results/uncertainty/test_set_prediction_sets.csv` — raw refit-model probabilities,
frozen global split-conformal threshold, **no Platt** — into the four BMI×Age cells). For the
`Intersection (Obese AND 60+)` rows it takes the frozen `baseline_coverage` (global threshold)
and `mitigated_coverage` (Phase-7 Mondrian), derives the integer covered count, and computes the
Wilson 95% interval with the **identical formula** to `src/phase6_04_final_test_touch.py`
`wilson_ci()`.

**Result: byte-identical** to the committed file.

```
derived  sha256: ea97ebb29349ed85effc75c26b9e1db73bba85207f4e4e11a05e205edf440bae
frozen   sha256: ea97ebb29349ed85effc75c26b9e1db73bba85207f4e4e11a05e205edf440bae
PASS: derivation is BYTE-IDENTICAL
```

No model is loaded, no test data reopened, no coverage proportion recomputed — the covered
counts come from the frozen four-way file.

### `src/prov_02_model_artifact_manifest.py`

Writes `results/tables/model_artifact_manifest.csv`: for every committed `models/**/*.joblib`
(32 files) — group, path, purpose, `size_bytes`, `sha256`, and (for the Phase-3 baseline family)
the seed / hyperparameters / CV-AUC already committed in `phase3_model_registry.csv`. Does
**not** load any joblib (no library-version dependency). The five `phase6_conformal_refit`
hashes are cross-checked against `conformal_model_refit_registry.csv` — **all match**.

Coverage: `phase3_baseline` 6 · `phase6_conformal_refit` 5 · `phase8_holdout` 5 ·
`amendment19_training_time_mitigation` 16 = **32**.

### `src/phase7_07_intersectional_coverage_figure.py`

Visualization only — the intersectional-cell companion to `src/phase6_07_figures.py`. Reads the
now-lineage-closed `results/uncertainty/intersectional_coverage_ci.csv` verbatim and draws
`results/uncertainty/figures/intersectional_coverage_by_model.png` (baseline vs frozen Mondrian
coverage for the Obese ∩ 60+ cell, N = 294, five families, 90% target). Loads no model, reopens
no test data, computes no coverage, changes no result. Not yet cited in the manuscript Figures
list; committed so the frozen artifact has a committed producer.

### `tests/test_prov_closure.py`

7 checks, **7/7 pass**: prov_01 runs clean and reports byte-identical; the manifest exists,
covers every on-disk joblib, its hashes/sizes are current, it matches the conformal-refit
registry, and the Phase-3 rows carry seed 42.

---

## Manuscript edits (`MANUSCRIPT_DRAFT.md`)

| Location | Change |
|---|---|
| Structured abstract | removed "joint intersectional calibration" from the list of tested mitigations |
| §3.7 (Mitigation attempts) | removed the sentence reporting joint intersectional conformal calibration |
| §5 (Limitations) | removed the sentence disclosing the MI-conformal extension's incomplete pipeline |
| §2.8 (Mitigation methods) | removed "joint (intersectional) conformal calibration" from the enumerated interventions |
| §5 (small-cell limitation) | removed the joint conformal-calibration cell (N = 138) clause; the Obese ∩ 60+ test cell (N = 294) and descriptive-only handling stay |
| Table 4 (mitigation summary) | removed the "Joint (intersectional) conformal calibration (exploratory)" row |
| Appendix A (claim map) | §3.7 row → "MIT-01–MIT-04, MIT-06"; MIT-05 noted as removed |
| Figures list | removed former Supplementary **S1** (`figure3_coverage_vs_set_size_tradeoff.png` — M1–M4b coverage vs set-size trade-off, Platt-recalibrated space, superseded N₀ = 100); former **S2** (liver-stiffness distributions) renumbered to **S1** |
| revision note (top) | dated 2026-08-28 entry recording this scope reduction |

`FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` row **MIT-05** is left unedited (append-only convention);
its `manuscript_status` was already `EXPLORATORY_ONLY` and it is now simply not manuscript-cited.

Table 3's Obese ∩ 60+ row (0.694 / 0.752 / 0.650 / 0.711 / 0.738) and the §3.5 intersection
range (65–75%) are **unchanged**; their source note now also cites
`bmi_age_overlap_four_way_analysis.csv`.

The M4b / joint / AFCP exploratory material is retained in
`documentation/final_research_audit/EXPLORATORY_RESULTS.md` (E8, E9) and in the repository
artifacts — it is simply no longer cited by the manuscript.

---

## Addendum — 2026-08-28 test-suite + lock-file hygiene (no analysis re-run, no result changed)

Folded into Amendment #20 (same "provenance / hygiene closure, no result change" scope). Full
change list and the last-run tally in `tests/README.md`.

- **`requirements-phase3-lock.txt`** was missing `tabulate` (needed by `src/prepub_01/02`) —
  added `tabulate==0.10.0`. This closed the only genuine reproducibility gap in the set.
- **11 test scripts updated** for post-consolidation / post-Amendment drift:
  - moved-doc reads → a `_doc()` archive-fallback resolver (5 scripts);
  - 3 forward-leakage guards (`test_calibration` T19, `test_fairness` T23, `test_uncertainty`
    T21) converted from "downstream `results/` dir must not exist yet" (permanently false now)
    to the structural guarantee they proxied — *phase-N code never writes into a downstream
    output tree* (Option 1);
  - ~7 "analysis X not executed yet" bookkeeping checks updated to the current documented state,
    since Amendments #12/#13/#14/#16 executed that work and the human spot-check was completed
    (Option 2);
  - `test_mitigation` T14 split into "no `phase7_*` script re-scores the raw locked test" +
    "frozen-artifact readers are the documented allowlist".
- **`results/end_to_end/protocol_amendment_reconciliation.csv`** row `num=10` has an unquoted
  comma (12 fields vs 11-column header) — **flagged, not fixed** (frozen artifact); the one
  test that reads it now uses `on_bad_lines="skip"`.
- **Full suite from a clean venv:** 18 scripts · **667 checks · 0 failed · 0 crashed**.

No test now asserts a weaker guarantee than before: the 3 leakage guards are strengthened
(structural, stable regardless of downstream execution), and the bookkeeping checks track the
amendment-documented reality instead of a superseded snapshot.

## Residual (not addressed by this amendment)

- Phases 1–3 protocol-vs-code commit ordering is still not git-verifiable (`c9c6ee3` bundles the
  Phase-2 freeze with Phase-3 modelling). This is a wording/transparency matter for
  `documentation/PROVENANCE_STATEMENT.md` and the manuscript Methods, not a reconstruction.
- The MI-conformal and joint-mitigation **artifacts** remain in the repository without a
  producer; they are now flagged descriptive/exploratory-only and are not manuscript-cited.
- `results/tables/final_research_status.csv` still carries one stale row (joint mitigation
  "NOT EXECUTED"); left per the append-only convention, superseded by `final_research_audit/`.
