# TEST SET LOCK

**Locked at:** 2026-08-18 14:45:56

- **Test N:** 2146
- **Test SEQN list SHA-256:** `b7fe6ff891051e7b1ef96dde4170e4fc745b1f80ce5063ca71020934b3ed4e72`
- **Protocol version:** documentation/phase2/PHASE2_PROTOCOL_FREEZE.md (zero amendments)

## THE TEST SET IS NOW LOCKED.

From this point forward the test set MUST NOT be used for: feature selection, preprocessing fit, imputation fit, scaling fit, model selection, hyperparameter tuning, threshold selection, early stopping decisions, model comparison during development, fairness optimization, calibration fitting, or uncertainty calibration. It may be used ONLY for the final frozen evaluation in Phase 3, Part 23 onward.

---

## Locked-test touch log (post-freeze amendments)

| Date | Amendment | Script | Nature of touch |
|---|---|---|---|
| 2026-08-27 | #18 (Fix 1) | `src/prepub_01_model_fit_alignment.py` | single non-iterative re-analysis of **frozen** refit test predictions + conformal sets, re-sliced by subgroup; no model evaluated anew |
| 2026-08-27 | #18 (Fix 2) | `src/prepub_02_vcte_bias_sensitivity.py` | single non-iterative relabel of the frozen test outcome at higher stiffness cut-points; re-score of frozen full-train predictions; no model evaluated anew |
| 2026-08-27T15:09:13Z | #19 (touch 1) | `src/ttm_03_test_classification.py` | single non-iterative evaluation of the **Amendment #19 reweighted** models on the locked test — discrimination, calibration, subgroup sensitivity. Leakage check `test ∩ {train, proper-train, calibration}` = 0. |
| 2026-08-27T15:09:48Z | #19 (touch 2) | `src/ttm_04_test_conformal.py` | single non-iterative evaluation of the Amendment #19 reweighted proper-train models on the locked test — marginal + subgroup + intersectional conformal coverage. Leakage check = 0. |

Amendment #18 touches are re-analyses of already-frozen predictions (no new model×test
evaluation). Amendment #19 touches are genuine evaluations of newly reweighted models on the
locked test, per its pre-registration. See `AMENDMENT_18_CLOSURE.md` and
`documentation/training_time_mitigation/AMENDMENT_19_CLOSURE.md`.
