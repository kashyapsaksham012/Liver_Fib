# Phase 3 Verification Log

**Generated:** 2026-08-18 (Phase 3 Closure Verification, Item 4) — every row below was checked
directly against the actual file/artifact, not recalled from the remediation report's prose.

| # | Claimed fix | File checked | Verification method | Result |
|---|---|---|---|---|
| 1 | Tightened comparison language ("perform comparably" removed) | `PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md` | `grep -c "perform comparably"` | **0 occurrences — CONFIRMED** |
| 2 | PR-AUC no-skill baseline table with calculation shown | `results/tables/phase3_auc_interpretation.csv` | Read file directly | **CONFIRMED** — contains `pr_auc`, `no_skill_baseline_pr_auc` (0.0932), and `fold_improvement_over_baseline` (computed as `pr_auc / baseline`, 3.76x–4.0x across models) as actual columns, not just asserted in prose |
| 3 | `hypothesis_interpretation.md` exists and prevents "H1 proven" overclaiming | `documentation/phase3/hypothesis_interpretation.md` | `ls -la` (confirms existence, 1,663 bytes, timestamp 16:59) + content read in Section U of the final report | **CONFIRMED** — file exists; states the correct language explicitly ("observed discrimination was consistent with the pre-specified H1 expectation," never "H1 was proven") |
| 4 | MLP oversampling sensitivity: AUC 0.8335 (balanced) vs. 0.8229 (original), 95% CI [-0.0050, 0.0272] | `results/predictions/test_predictions_mlp.csv`, `test_predictions_mlp_balanced.csv` | **Independent recomputation from raw predictions**, bypassing `phase3_mlp_asymmetry_audit.csv` entirely — recomputed ROC-AUC via `sklearn.metrics.roc_auc_score` and re-ran the paired bootstrap (n=2,000, seed=42) from scratch | **EXACT MATCH**: recomputed AUC 0.8229 / 0.8335, recomputed CI [-0.0050, 0.0272] — all bit-identical to the claimed values |
| 5 | `cv_validation_design.md` explicitly resolves the `validation_ids.csv` naming risk | `documentation/phase3/cv_validation_design.md` | `grep -n "MUST NOT be read as an independent validation cohort"` | **CONFIRMED** (line 9) — see also Item 1 above, which additionally added a canonical-named alias file (`cv_fold_assignment_ids.csv`) at this verification pass |
| 6 | `inference_methodology_amendment.md` states bootstrap n=2,000, seed=42, and FDR family scoping exactly | `documentation/phase3/inference_methodology_amendment.md` | `grep -n` for exact figures | **CONFIRMED**: "Number of resamples: 2000" (line 12), "Random seed: 42" (line 19), family explicitly scoped as "BASELINE MODEL COMPARISONS ONLY ... does NOT include any subgroup/fairness comparison" (line 18) |
| 7 | 44/44 validation tests pass | `src/phase3_08_validation_tests.py` (original 20), `src/phase3_19_validation_tests_v2.py` (remediation 24) | **Re-ran both suites fresh, right now** (not reading a stored log from the original report) | **20/20 PASS + 24/24 PASS = 44/44 PASS, confirmed at re-run time, not merely at time of original report** |

## Summary

All 7 previously-claimed Phase 3 fixes are verified as actual, correct, file-system-present
artifacts. No claim in the remediation report was found to be prose-only or unsubstantiated.
