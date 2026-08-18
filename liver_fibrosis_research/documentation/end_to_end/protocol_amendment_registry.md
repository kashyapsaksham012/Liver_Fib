# Protocol Amendment Registry (Complete, Cross-Phase)

**Generated:** 2026-08-18 (end-to-end Phase 1→3 audit) — consolidates every amendment made across
Phase 1, 2, and 3; none invented for this audit, all traced to their originating document.

| # | Amendment | Original protocol | What changed | Why | Test-set involved? | Downstream results affected? | Rerun required? |
|---|---|---|---|---|---|---|---|
| 1 | Youden's J threshold, computed from OOF training CV | Phase 2 named it as an explicit "e.g." example, deferred final adoption | Phase 3 formally adopted the named example as the frozen method | Phase 2 explicitly deferred exact threshold selection to Phase 3 | **No** — verified structurally, threshold code precedes test-set load | Yes — determines sensitivity/specificity/PPV/NPV/F1 per model | No — already correctly computed |
| 2 | Bootstrap (n=2,000, paired) + Benjamini-Hochberg FDR for baseline model comparison | Phase 2 fixed 2,000-resample bootstrap for *fairness* disparities and FDR for *subgroup* comparisons; did not freeze a procedure for *model* comparison | Phase 3 extended the closest existing convention to a new comparison family (models, not subgroups) | Gap in Phase 2 scope, not an error | **No** | Yes — determines whether any model is flagged as significantly different | No |
| 3 | MLP training-fold-only 1:1 oversampling sensitivity analysis (`imbalanced-learn` added as a new dependency) | Phase 2 froze "class weights, not SMOTE" as the general imbalance policy; did not anticipate sklearn's `MLPClassifier` API constraint | A pre-specified sensitivity model added, training-fold-only, never touching validation/test | Genuine implementation gap in the general policy, discovered during Phase 3 execution | **No** — verified via `imblearn.pipeline.Pipeline`, resampling strictly inside CV folds | No — MLP_original remains primary; MLP_balanced is sensitivity-only, not promoted | No |
| 4 | Reservation of a conformal calibration partition (`proper_train_ids.csv` N=4,005, `conformal_calibration_ids.csv` N=1,002) | Phase 2 named "e.g. 80/20" and explicitly deferred the exact proportion to "Phase 3" | The exact 80/20 split was generated for the first time during the closure-verification pass (not during original Phase 3 execution) | Gap identified during closure verification: Phase 3's original scope never actually carved this out | **No** — carved only from `train_ids.csv`, verified disjoint from `test_ids.csv` | Not yet — Uncertainty phase has not started | N/A — this IS the first run |
| 5 | `cv_fold_assignment_ids.csv` added as a canonical alias for `validation_ids.csv` | Original Phase 3 deliverable template named the file `validation_ids.csv` | A second, unambiguously-named file with identical content was added; original name retained for backward compatibility | `validation_ids.csv` risked being misread as an independent held-out cohort | No | No | No |
| 6 | Withdrawal of the mtime-based provenance claim for `fairness_subgroup_protocol.md` | An earlier closure-verification turn cited filesystem mtime as evidence the file predated Phase 3 | Claim formally withdrawn after `git log --follow -p` found zero commit history for the file; downgraded to `CURRENTLY-DOCUMENTED-ONLY` | mtime is not tamper-proof, tamper-independent evidence | N/A | No scientific result changed — only the provenance-strength claim | No |
| 7 | Entire Phase 2/3 working tree committed to git for the first time (`c9c6ee3`, `d218152`) | No formal protocol existed requiring commits at any specific granularity | 140 files committed in one bulk commit, then 2 correction commits | No version-control history existed for any Phase 2/3 artifact prior to this | N/A | None — commit does not alter any file's content beyond the correction commits | No |

## Amendments explicitly considered and NOT made

- **Race/ethnicity reintroduced as a model predictor** — never done; confirmed excluded in every
  predictor registry check this audit performed.
- **Primary cohort/outcome/threshold changed based on any model result** — never done; every
  live recomputation this audit performed matches the originally frozen Phase 2 values exactly.
- **A model declared "the winner" based on test AUC** — never done; `downstream_model_retention_decision.md`
  explicitly retains all 5 original families per the Phase-2-frozen retention rule.

## Governing rule (restated, enforced)

No amendment above was inserted into any final-report narrative silently — each is cross-referenced
from `PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md` Section Y ("Protocol Amendments")
and/or its own dedicated audit document, and none altered a frozen Phase 1 or Phase 2 cohort,
outcome, or predictor-set decision.
