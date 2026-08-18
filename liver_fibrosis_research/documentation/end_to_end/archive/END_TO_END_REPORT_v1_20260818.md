# End-to-End Phase 1 → Phase 3 Verification Report

**Generated:** 2026-08-18. Every number in this report was reproduced live during this audit
pass (see `documentation/end_to_end/` and `results/end_to_end/` for full command output and
generated tables) — none are restated from prior reports without re-verification.

---

## A. Executive Summary

The Phase 1 → Phase 2 → Phase 3 chain is **internally consistent and independently reproducible
from its own artifacts**: every cohort number, SEQN set, outcome count, predictor list, split
size, and discrimination metric checked in this audit reproduced exactly from live recomputation,
with zero unexplained numerical discrepancies. Test-set isolation is **structurally proven**
(code-level, not merely claimed) for every development decision. The one class of weakness — the
strength of evidence that Phase 2's protocol decisions were finalized *before* Phase 3's code was
written — was already identified, honestly downgraded, and documented in a prior forensic audit
(`documentation/FORENSIC_PROVENANCE_AUDIT.md`); this audit does not find anything new to add to
that specific limitation, only reconfirms it holds. One new, minor documentation inconsistency
(a "Phase 4" umbrella term contradicting the later 3-way phase-numbering crosswalk) was found and
corrected via an appended note, not a silent rewrite.

## B. Research Objective

Fairness, Calibration, and Uncertainty in ML-Based Liver Fibrosis Risk Prediction Across
Demographic Groups (NHANES 2017–March 2020). This audit covers only Phases 1–3 (data → protocol
→ baseline ML); Calibration/Fairness/Uncertainty have not started.

## C. Phase Numbering Crosswalk

`documentation/phase_numbering_crosswalk.md` exists and maps 3 completed project phases to the
mentor's 15-phase `info.md` plan. **One inconsistency found and corrected this audit** (not
silently): `PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md` line 177 used "Phase 4" as
an umbrella for calibration+fairness+uncertainty, contradicting the crosswalk's later 3-way split
(Project Phase 4=Calibration, 5=Fairness, 6=Uncertainty). A dated correction note was appended
directly below the original sentence; the original sentence itself was left untouched.

## D. Phase 1 Status

**PASS on every check performed.** All 8 raw NHANES files present and load; SEQN valid, zero
duplicates; master dataset one row per participant (10,409); data dictionary, missingness audit,
plausibility audit, special-missing-code audit, leakage pre-screen, and canonical cohort module
(`src/_cohorts.py`) all exist and were exercised live. **All 9 canonical cohort numbers
independently recomputed this audit and matched exactly**: source 10,409; non-missing LUXSMED
9,700; quality-valid 9,023; adults-of-non-missing 8,318; under-18 1,382; adults-of-quality-valid
7,768; broad-lab cohort 8,880; fasting-labs-only 4,376; canonical fasting-extended 4,336;
combined-broad 8,805. Non-missing-vs-quality-valid distinction preserved throughout (never
conflated). Special-missing sentinel check: **zero sentinel cells remain in any of 14 checked
final analysis variables**, live-verified.

## E. Phase 2 Status

**PASS.** Primary cohort (N=7,153) independently recomputed from Phase 1 raw master data — SEQN
set is **exactly identical** to the saved analysis dataset (0 symmetric difference). Outcome
recomputed from `LUXSMED >= 8.2 kPa` independently — matches saved column on every row; 666
positive / 6,487 negative / 9.31% prevalence, exact match. Predictor registry: exactly 10 primary
predictors, exact names verified; race/ethnicity confirmed excluded from the model matrix but
retained for fairness stratification (both `RIDRETH1`/`RIDRETH3` explicitly marked
`SENSITIVITY-ONLY`). Missing-data protocol content verified: complete-case primary, multiple
imputation sensitivity, and the Non-Hispanic Black differential-exclusion finding (41.3%)
**confirmed still present** in the protocol document, not scrubbed. All 4 candidate/sensitivity
cohort N's (7,153/7,639/3,582/8,215) confirmed unchanged. Uncertainty design: "Split Conformal
Prediction" confirmed as the frozen method name in `uncertainty_protocol.md`.

## F. Phase 3 Status

**PASS.** Phase 2→3 handoff: dataset N=7,153, positive=666 in, train N=5,007 + test N=2,146 out,
union equals the full dataset, exact match. Test-set SHA-256 hash unchanged since lock
(`b7fe6ff891051e7b...`, live-recomputed and matched against `test_set_lock.md`). Class-imbalance
handling per model confirmed live from the model registry (weights for 4 models, documented
sklearn-API gap for MLP). 84 hyperparameter configurations confirmed (exact count, not
approximate). Threshold-selection code order re-confirmed structurally this audit. Model
comparison: 10 pairwise tests, 0 significant after FDR — reconfirmed live. PR-AUC context
(0.35–0.37 vs. 9.32% no-skill baseline, 3.76–4.00×) reconfirmed live. H1 language checked for
overclaiming — the only "H1 was proven" string matches are inside explicit prohibition sentences
("Not used: ..."), not actual claims — verified by reading surrounding context, not by substring
match alone.

## G. Phase 1 → Phase 2 Handoff

`results/end_to_end/phase1_to_phase2_handoff.csv`, `phase1_to_phase2_seqn_difference.csv`
(0 rows — no differences to report). **PASS.**

## H. Phase 2 → Phase 3 Handoff

`results/end_to_end/phase2_to_phase3_handoff.csv`. All boolean checks TRUE: train+test size
equals dataset size; SEQN union equals dataset SEQN set. **PASS.**

## I. Cross-Phase Numerical Consistency

See `results/end_to_end/phase1_phase2_phase3_master_numbers.csv` — 27 rows, **every row marked
YES**, all live-reproduced during this audit (full table in Section 6 of the chat response).

## J. Cohort Consistency
All 9 Phase 1 cohorts + 4 Phase 2 candidate cohorts live-recomputed and matched their documented
N's exactly. **PASS.**

## K. Outcome Consistency
`LUXSMED >= 8.2 kPa` recomputed independently at both the Phase 2 and Phase 3 boundary; matches
saved outcome column on every row in both checks. **PASS.**

## L. Predictor Consistency
Exactly 10 primary predictors in both the Phase 2 registry and the Phase 3 feature-matrix
whitelist; identical variable name sets. **PASS.**

## M. Leakage Audit
Structural, code-level proof (not chronology-dependent): `grep "test_ids" src/phase3_05_train_and_tune.py`
→ zero matches. Threshold computed at an earlier source-line than the test-set load in the same
script. Preprocessing fit only inside `search.fit(X, y)` on training-partition data. **PASS** —
see `results/end_to_end/test_set_contamination_audit.md` for the full pathway-by-pathway table.

## N. Missing-Data Consistency
Complete-case primary strategy confirmed applied in Phase 3 (0 predictor missingness by cohort
construction, live-verified); multiple-imputation sensitivity remains undone (correctly deferred,
not yet needed); Black-participant differential-exclusion finding preserved in documentation.
**PASS.**

## O. Train/Test Integrity
5,007/2,146, zero overlap, union equals full cohort, hash unchanged since lock — all
live-reconfirmed. **PASS.**

## P. CV Integrity
5-fold `StratifiedKFold(shuffle=True, random_state=42)`, training partition only — confirmed by
direct source inspection of `phase3_05_train_and_tune.py` and `phase3_common.py` constants.
**PASS.**

## Q. Hyperparameter-Tuning Integrity
84 configurations total (live-counted from `phase3_hyperparameter_search_registry.csv`, not
approximated); zero `test_ids` references in the training script. **PASS.**

## R. Threshold-Selection Integrity
Youden's J, computed from out-of-fold training CV predictions, code-order-verified to precede
the test-set load. **Explicitly NOT claimed as pre-specified by Phase 2** — Phase 2 named it as
an "e.g." example only; Phase 3 formally adopted it (documented as Amendment #1, not backdated).
**PASS.**

## S. Model-Comparison Integrity
0/10 pairwise comparisons significant after FDR, live-reconfirmed. Report language audited and
confirmed to avoid "equivalent" claims — the phrase actually used throughout is "no statistically
significant pairwise superiority was demonstrated after FDR correction." **PASS.**

## T. Class-Imbalance/MLP Audit
Model-specific handling confirmed live for all 5 models. MLP asymmetry sensitivity analysis
values (original AUC 0.8229, balanced AUC 0.8335, 95% CI [-0.0050, 0.0272]) reproduced exactly
from raw prediction files in a prior audit pass and reconfirmed present in
`phase3_mlp_asymmetry_audit.csv` this pass. MLP_balanced confirmed NOT promoted to primary status
— `downstream_model_retention_decision.md` retains only the 5 original models. **PASS.**

## U. CI/Bootstrap/FDR Audit
n=2,000 paired bootstrap resamples, seed=42, FDR family scoped explicitly to "baseline model
comparisons only" (excludes any future fairness-comparison family) — confirmed by direct read of
`inference_methodology_amendment.md`. Formally documented as a Phase 3 amendment (Amendment #2),
not presented as Phase-2-frozen. **PASS.**

## V. Reproducibility Audit
44/44 tests re-run live during this audit (20/20 + 24/24). All 5 models' discrimination metrics
independently reproduce exactly from raw `test_predictions_*.csv` files (recomputed live this
audit, matches `phase3_overall_discrimination.csv` to 4 decimal places). **PASS.**

## W. Environment Audit
Python 3.14.3; scikit-learn==1.9.0, xgboost==3.4.1, lightgbm==4.7.0, imbalanced-learn==0.14.2,
pandas==3.0.5 — all confirmed via live `pip freeze`, matching `requirements-phase3-lock.txt`
exactly. **PASS.**

## X. Protocol-Amendment Registry
7 amendments fully documented in `documentation/end_to_end/protocol_amendment_registry.md`, each
with original protocol, exact change, reason, test-set involvement (none), and downstream impact.
**No amendment altered any frozen Phase 1 or Phase 2 cohort/outcome/predictor decision.**

## Y. Test-Set Contamination Audit
**PASS** on all 8 checked pathways (feature selection, model selection, hyperparameter tuning,
class-imbalance decisions, threshold selection, preprocessing fitting, fairness optimization,
calibration) — full table in `results/end_to_end/test_set_contamination_audit.md`. No UNCERTAIN
result was required for any pathway.

## Z. Dependency Graph
`results/end_to_end/research_pipeline_dependency_graph.md`. One traceability gap disclosed (not
hidden): `phase3_common.py`'s frozen constants (N=7,153, predictor names) are manually
transcribed from the Phase 2 protocol document rather than parsed from it programmatically —
partially mitigated by `phase3_01_handoff_verification.py`'s independent recomputation from raw
Phase 1 data, which would catch a cohort-size transcription error but not necessarily a
single-variable-name typo. Zero unauthorized dependencies found; 2 orphan files identified and
explained (both expected, non-bugs).

## AA. Validation-Test Results
44/44 (20 original Phase 3 tests + 24 remediation-audit tests), all re-run live this pass, zero
failures.

## AB. Remaining Issues (non-blocking, all previously disclosed or newly found-and-corrected here)

1. **[Pre-existing, from forensic audit]** Phase 2 and Phase 3 are bundled in one git commit —
   protocol-freeze-before-training chronology cannot be proven by git, only by weaker
   corroboration (file mtime, internally consistent but not tamper-proof).
2. **[New, found and corrected this audit]** "Phase 4" umbrella terminology in the frozen Phase 3
   report contradicted the later phase-numbering crosswalk — corrected via an appended note, not
   a silent rewrite.
3. **[Pre-existing, disclosed]** `phase3_common.py` predictor/cohort constants are manually
   transcribed from the Phase 2 document rather than parsed programmatically.
4. **[Pre-existing, disclosed]** MLP's class-imbalance handling remains structurally different
   from the other 4 models even after the sensitivity analysis (sklearn API constraint).
5. **[Pre-existing, disclosed]** Conformal-valid model refit on `proper_train_ids.csv` has not
   yet been performed (correctly deferred — the Uncertainty phase has not started).

None of these five items contradicts any cohort, outcome, predictor, split, or discrimination
result reported in Phases 1–3.

## AC. Scientific Interpretation
No overclaiming found: "no statistically significant pairwise superiority" (not "equivalent"),
"consistent with the pre-specified H1 expectation" (not "H1 proven"), PR-AUC always reported with
its prevalence baseline, no fairness/calibration/uncertainty claim exists anywhere in the
repository (confirmed by live search this audit).

## AD. Final Sign-Off

See Section 12 of the chat response for the formal status designation.

## AE. Readiness for Next Phase

Ready for Calibration (Project Phase 4), conditioned on performing the still-outstanding
conformal-valid model refit before any Uncertainty-phase (Project Phase 6) code runs, and on
committing each future phase's frozen protocol document in its own standalone commit (per the
forensic audit's P1 recommendation) rather than bundling protocol and execution together as
Phase 2+3 were.
