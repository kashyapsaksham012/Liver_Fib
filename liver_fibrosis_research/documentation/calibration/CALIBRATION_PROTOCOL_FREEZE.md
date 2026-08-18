# Calibration Protocol Freeze (Project Phase 4)

**Generated:** 2026-08-18. **Status: FROZEN, PROSPECTIVELY, BEFORE ANY CALIBRATION EXECUTION.**
**Calibration execution has not begun.** No calibration metric has been computed, no
recalibration model has been fit, and no calibration plot has been generated as of the writing
of this document. This document is committed in a standalone git commit, separate from any
implementation code, specifically so that its freeze date is independently git-provable —
addressing the P1 recommendation from the prior end-to-end audit (commit-granularity provenance
was previously not achievable because Phase 2 and Phase 3 were bundled into one commit).

This document was written after reading, and is required to be consistent with, the existing
frozen Phase 2 documents: `PHASE2_PROTOCOL_FREEZE.md`, `evaluation_metrics_protocol.md`,
`statistical_analysis_plan.md`, `model_development_protocol.md`, and `uncertainty_protocol.md`.
Where Phase 2 already specified a decision, it is carried forward unchanged below (cited).
Where Phase 2 left a decision open, that is disclosed explicitly rather than silently filled in
as if it had always been frozen.

Per the naming crosswalk (`documentation/phase_numbering_crosswalk.md`): **Project Phase 4 =
Calibration only** (mentor `info.md` Phase 9). Fairness (Project Phase 5) and Uncertainty
(Project Phase 6) are separate, later phases and are explicitly out of scope here.

## 1. Objective

Assess whether the predicted probabilities produced by each of the 5 frozen primary models
(Logistic Regression, Random Forest, XGBoost, LightGBM, MLP — the **MLP_original** variant;
`MLP_balanced` is a sensitivity analysis and is explicitly excluded from primary Calibration
status per standing project rule) are quantitatively trustworthy as probabilities — i.e., among
participants assigned a predicted risk of *p*, does the observed event rate approximate *p* —
and to characterize any miscalibration found. This is a diagnostic and reporting phase; it is
NOT a phase that reopens model selection, hyperparameters, the outcome threshold, or the
predictor set.

## 2. Research Question

For the primary liver-fibrosis-risk outcome (LUXSMED ≥ 8.2 kPa) and the primary cohort
(N = 7,153; source: `documentation/audit_reports` and prior Phase 1 closure, treated as prior
evidence per Part 1 of this task and not re-derived here), how well-calibrated are the predicted
probabilities of each of the 5 frozen primary models, overall and (as a handoff item for the
future Fairness phase, not executed here) per fairness subgroup?

## 3. Primary Cohort

Unchanged from Phase 2/3: the primary analysis cohort (N = 7,153), split into the frozen
`train_ids.csv` (N = 5,007) and `test_ids.csv` (N = 2,146) partitions defined in
`data/processed/splits/`. No new cohort definition is introduced. Cohort masks, if referenced by
any future Calibration implementation code, must import from `src/_cohorts.py` (the sole
canonical source confirmed by this pass's source-of-truth audit — see
`results/pre_calibration/source_of_truth_matrix.csv`), not recompute independently.

## 4. Primary Outcome

Unchanged: `outcome_primary_8.2kPa` (LUXSMED ≥ 8.2 kPa), 666 positive / 6,487 negative in the
primary cohort. Confirmed single-canonical-value by this pass's source-of-truth audit (the two
independent `PRIMARY_THRESHOLD = 8.2` definitions in `phase2_02_outcome_predictors_leakage.py`
and `phase2_03_design_and_feasibility.py` are confirmed to agree, both matching the value
enforced by `tests/test_source_of_truth.py`).

## 5. Model Set

All 5 originally frozen Phase 3 primary models, evaluated as their single frozen
`best_estimator_` artifact each (no re-tuning):

| Model | Status |
|---|---|
| Logistic Regression | Primary |
| Random Forest | Primary |
| XGBoost | Primary |
| LightGBM | Primary |
| MLP (original, no oversampling) | Primary |
| MLP_balanced (oversampling sensitivity variant) | **Explicitly NOT primary.** May be reported as a supplementary sensitivity calibration check only if requested later, never silently promoted. |

## 6. Calibration Data Separation (Anti-Leakage — Core Decision)

This is the single most important decision in this document, made explicitly and justified
before any execution:

**Decision: two-tier calibration assessment.**

1. **Development-side (repeatable) diagnostic tier:** Calibration metrics computed from the
   **CV out-of-fold (OOF) predictions** already generated during Phase 3 hyperparameter search
   (`GridSearchCV`/`RandomizedSearchCV` with `StratifiedKFold(n_splits=5, ...)` — the same OOF
   predictions already used for Youden's J threshold selection in
   `phase3_06_threshold_and_test_eval.py`). Because each fold's predictions come from a model
   instance that never saw that fold during fitting, this is leakage-safe and may be inspected
   or iterated on freely without touching the test set.
2. **Confirmatory (one-time) tier:** Calibration metrics computed once on the **locked test set**
   (`test_ids.csv`, N = 2,146) using the already-frozen `best_estimator_` pipelines, exactly
   analogous to how discrimination metrics (ROC-AUC, PR-AUC, sensitivity/specificity) were
   already locked-test-evaluated in Phase 3 per `evaluation_metrics_protocol.md`. This is
   **scoring**, not fitting — no parameter of any model is touched — and is therefore not a
   test-set-development violation under the standing rule (which prohibits using the test set
   for feature selection, model selection, hyperparameter tuning, threshold selection, or
   preprocessing fitting; scoring a fully frozen model once is the same category of operation
   already performed for discrimination metrics).

**Explicit exclusion:** `data/processed/splits/conformal_calibration_ids.csv` (N = 1,002) is
**NOT** used for this Calibration phase's diagnostics. That partition is reserved exclusively for
the future **Uncertainty** phase's split-conformal-prediction calibration set (a different,
unrelated technical use of the word "calibration" — see `documentation/phase3/
conformal_calibration_protocol.md`). Using it here would also be scientifically invalid for the
current frozen models regardless of naming, because those models were fit on the full 5,007-row
training partition, which includes the 1,002 rows reserved as `conformal_calibration_ids.csv` —
they are therefore not a clean held-out set for these specific model artifacts. This naming
collision is flagged explicitly here to prevent future confusion between "calibration" (this
phase, statistical probability calibration) and "conformal calibration set" (future Uncertainty
phase, a disjoint technical concept).

**If recalibration (e.g., Platt scaling / isotonic regression) is later found necessary** based
on the diagnostic findings above: any such recalibration mapping must be **fit only on the
CV-based OOF predictions** (tier 1 above), never on the test set. This pre-commitment is made now,
before execution, specifically so that IF miscalibration is found and recalibration is pursued,
the anti-leakage boundary is not decided under the influence of having already seen test-set
results. Whether recalibration is actually needed is a diagnostic finding to be made during
execution, not decided here — this document only pre-commits *where* such fitting would occur
if it becomes necessary.

## 7. Primary Calibration Metrics

Per `evaluation_metrics_protocol.md` (already frozen in Phase 2, carried forward unchanged):

- **Calibration intercept and slope** — from a logistic recalibration regression of observed
  outcome on the model's linear predictor (logit of predicted probability).
- **Brier score.**

## 8. Secondary Calibration Metrics

Per `evaluation_metrics_protocol.md` (already frozen in Phase 2, carried forward unchanged):

- **Calibration curve** (reliability diagram, 10 risk deciles).
- **Expected Calibration Error (ECE)** — reported as supplementary given its known sensitivity to
  binning choices (this caveat is itself already stated in the frozen Phase 2 document).

## 9. Calibration Plot Binning Strategy

10 risk deciles (equal-frequency bins of predicted probability), consistent with the "10 risk
deciles" language already frozen in `evaluation_metrics_protocol.md` §Calibration. Equal-frequency
(rather than equal-width) binning is used so that each bin has comparable statistical precision,
given the moderate 9.31% base rate makes equal-width high-probability bins sparse.

## 10. Recalibration Method

**Not pre-decided as mandatory.** Phase 2's `evaluation_metrics_protocol.md` freezes calibration
*metrics* (§7-8 above) but does not freeze a recalibration *procedure* — this is a genuinely open
decision that Phase 2 left to be made based on diagnostic findings, not an omission being
silently filled in here. This document pre-commits only the anti-leakage boundary for recalibration
IF it is pursued (§6 above: CV-OOF only, never the test set). The decision of *whether* to
recalibrate, and *which* method (Platt scaling vs isotonic regression) if so, is deferred to
after the primary/secondary diagnostic metrics are computed, and must be logged as a dated
protocol amendment in `documentation/end_to_end/protocol_amendment_registry.md` when made,
consistent with the standing project rule that all protocol amendments are explicitly logged and
distinguished from pre-specified Phase 2 rules.

## 11. Subgroup Calibration Handoff Language

Calibration-by-subgroup is a **future Fairness-phase (Project Phase 5) activity**, not executed
in this Calibration phase. This section exists only to freeze the handoff language in advance so
that when it is executed, it inherits the same precision-tier discipline already established in
`fairness_subgroup_protocol.md` rather than reinventing it:

- Subgroup calibration curves must carry forward the same **precision-tier labeling** already
  frozen for discrimination/fairness metrics (primary-feasibility tier vs exploratory tier, e.g.
  Non-Hispanic Asian [52 positive] and Other/Multi-Racial [37 positive] are exploratory-tier and
  must be reported with wider expected confidence intervals, never dropped or pooled).
- Any claim about *when* a subgroup calibration decision was made relative to other decisions
  must use the standing required language where repository provenance is not commit-level strong:
  **"Historical pre-specification of [X] could not be independently established from strong
  repository provenance."** This document's own freeze date, by contrast, IS commit-level provable
  going forward (§14 below), which is precisely why this document is being committed standalone.

## 12. Confidence Intervals

Percentile bootstrap, **n = 2,000** resamples, paired resampling at the participant level —
the same method already used for Phase 3's discrimination-metric confidence intervals
(`model_development_protocol.md` / Phase 3 remediation). **Disclosure:** this method was not
itself pre-specified in Phase 2's `statistical_analysis_plan.md` (grep-confirmed zero mentions
of "bootstrap" or "FDR" in that document this pass) — it was introduced as Phase 3 Amendment #2
(bootstrap n=2,000 + FDR correction, per `protocol_amendment_registry.md`). Adopting the same
method here for calibration CIs is a deliberate consistency choice, made explicitly rather than
silently, and is itself logged as an extension of that same amendment rather than presented as
having been Phase-2-frozen.

## 13. Multiple-Comparison Handling

Benjamini-Hochberg FDR correction, applied across the set of pairwise model comparisons on each
calibration metric (intercept, slope, Brier), consistent with the same method used for Phase 3
discrimination-metric pairwise comparisons. Per the standing project language rule: non-significant
pairwise differences after FDR correction must be reported as "no statistically significant
pairwise superiority was demonstrated after FDR correction," never as "equivalent."

## 14. Sensitivity Analysis

`MLP_balanced` (the class-imbalance oversampling variant) may be included as a **supplementary,
explicitly labeled** sensitivity calibration check, reported alongside but never merged into the
5-model primary calibration table, consistent with the standing rule that it must never be
silently promoted to primary status.

## 15. Reproducibility Requirements

Consistent with Phase 3 precedent: all calibration computations must be produced by committed
source scripts (not notebook/interactive-only code), must not touch `test_ids.csv` beyond the
one-time confirmatory scoring pass described in §6, and must record package versions against
`requirements-phase3-lock.txt` (or a Phase-4-specific lock file if new packages are introduced,
e.g. for isotonic regression — `scikit-learn`'s `IsotonicRegression` is already available in the
existing pinned `scikit-learn==1.9.0`, so no new dependency is anticipated).

## 16. Stop Conditions

Per this task's Part 8, Calibration execution must halt and escalate to the user if:
- The locked test set would need to be touched more than once, or touched for any purpose other
  than one-time confirmatory scoring of already-frozen models.
- A recalibration method choice cannot be justified by the diagnostic findings alone and would
  require a new, unauthorized scientific decision.
- Any finding contradicts a Phase 2-frozen decision (e.g., if `evaluation_metrics_protocol.md`'s
  metric definitions turn out to be inconsistent with what this document specifies — reviewed for
  consistency in §17 below, no such conflict was found).

## 17. Phase 2 Consistency Review

This document was cross-checked against all 5 named Phase 2 documents:

| Phase 2 document | Consistency finding |
|---|---|
| `PHASE2_PROTOCOL_FREEZE.md` | Row "Calibration metric: Slope + intercept + Brier primary; calibration curve + ECE secondary" — **matches §7-8 above exactly.** |
| `evaluation_metrics_protocol.md` | §Calibration — **matches §7-9 above exactly** (source of the metric and binning-strategy freeze). |
| `statistical_analysis_plan.md` | No calibration-specific content; no bootstrap/FDR content (confirmed by live grep this pass) — **no conflict, but §12-13's bootstrap/FDR choice is disclosed as inherited from Phase 3 amendment precedent, not Phase 2 freeze, per the honesty requirement.** |
| `model_development_protocol.md` | States model retention should ultimately be decided "using the FULL primary metric suite (discrimination + calibration + fairness + ...)" — **consistent; this Calibration phase produces exactly the calibration component of that suite, without reopening model retention now.** |
| `uncertainty_protocol.md` | Defines the split-conformal calibration set (`conformal_calibration_ids.csv`) for the **separate, future Uncertainty phase** — **§6 above explicitly distinguishes this from the current Calibration phase's data to prevent the naming collision.** |

**No conflicts found.** No amendment to any Phase 2 document was required.

## 18. Amendment Policy

Any deviation from this document discovered necessary during Calibration execution (e.g., a
different recalibration method, a different binning count) must be logged as a dated,
individually-described entry in `documentation/end_to_end/protocol_amendment_registry.md`,
distinguished from this prospective freeze, following the same discipline already established
for the 4 true scientific amendments logged during Phase 3.

---

**Confirmation: Calibration execution has not begun.** As of this document's commit, no
calibration metric has been computed, no recalibration model fit, and no calibration plot
generated. This is a protocol freeze only.
