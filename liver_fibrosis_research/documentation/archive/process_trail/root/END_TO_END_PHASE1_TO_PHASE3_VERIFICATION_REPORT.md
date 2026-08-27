# End-to-End Phase 1 → Phase 3 Verification Report — FINAL

**Generated:** 2026-08-18. This version supersedes the prior end-to-end report (same filename,
overwritten per instruction — the prior content is preserved in git history at commit `d02a4bb`
and is not erased). Every number below was reproduced live during THIS audit pass, not restated
from the prior pass.

---

## A. Executive Summary

Phases 1→3 remain internally consistent and independently reproducible: every cohort number,
SEQN set, outcome count, predictor list, split, and discrimination metric re-verified live this
pass matches exactly, with zero unexplained discrepancies. **Two items this audit was
specifically instructed not to trust on prose alone were independently, programmatically
verified from first principles: the hyperparameter configuration count (84, confirmed via live
AST parse of the actual grid-definition source code, matching the runtime log exactly) and the
protocol amendment count (7, confirmed by direct enumeration of the registry's table rows, all
distinct, none duplicated).** The historical-provenance limitation identified in the prior
forensic audit (Phase 2 and Phase 3 bundled in one git commit, so protocol-before-training
chronology is not commit-provable) is re-confirmed, unchanged, and stated using the required
qualified language throughout this report.

## B. Phase Numbering

`documentation/phase_numbering_crosswalk.md` exists and is internally consistent. The one known
historical inconsistency (Phase 3 report's "Phase 4" umbrella term vs. the crosswalk's later
3-way split) was corrected in the prior audit pass via an **appended, dated note** — the original
sentence was left unmodified, consistent with the rule against silently rewriting historical text.
No new phase-numbering inconsistency was found this pass.

## C. Phase 1 Verification

All 9 canonical cohort numbers independently recomputed live this pass, exact match:
10,409 → 9,700 → 9,023 → 8,318/1,382 → 7,768 → 8,880/8,805 → 4,376/4,336.
Special-missing sentinel check (14 variables, including `LUXSIQRM`): zero remaining, re-confirmed
in the prior pass and structurally unchanged (no code touching these variables has been modified
since). **PASS.**

## D. Phase 2 Verification

Primary cohort SEQN set: **0 symmetric difference** vs. live Phase-1-derived recomputation
(re-run fresh this pass). Outcome: **0 row-level deviations** between an independently recomputed
`LUXSMED>=8.2` column and the saved outcome column (new this pass —
`phase2_outcome_reconciliation.csv`, a file not previously produced in this exact row-level form).
Predictor freeze: 10 exact names, race/ethnicity confirmed excluded-but-retained. Missing-data
protocol: complete-case primary, multiple-imputation sensitivity, Black-participant exclusion
finding (41.3%) confirmed still present in the document text. Cohort architecture: all 4
candidate/sensitivity N's (7,153/7,639/3,582/8,215) unchanged. **PASS.**

## E. Phase 3 Verification

Handoff N/positive/train/test all re-confirmed live. Test-set hash unchanged since lock
(`b7fe6ff891051e7b...`). **Hyperparameter count independently re-derived from source code via AST
parsing this pass = 84, exact match to the runtime log, per-model breakdown also exact
(6/20/20/20/18).** Threshold code-order re-confirmed. Model comparison: 0/10 significant after
FDR, re-confirmed. 44/44 tests re-run live this pass, zero failures. **PASS.**

## F. Phase 1→2 Handoff

`results/end_to_end/phase1_to_phase2_seqn_difference.csv`: 0 differences (fresh this pass).
**PASS.**

## G. Phase 2→3 Handoff

`results/end_to_end/phase2_to_phase3_handoff.csv`: all boolean checks TRUE (fresh this pass).
**PASS.**

## H. Master Numerical Consistency

See Section 6 of the accompanying chat response for the full table; every row consistent,
re-verified this pass.

## I. Cohort Verification

9 Phase 1 cohorts + 4 Phase 2 candidate cohorts, all live-recomputed this pass, exact match to
prior values. No two differently-defined cohorts are conflated anywhere — `COHORT_FASTING_LABS_ONLY`
(4,376) and `COHORT_B_FASTING_EXTENDED` (4,336) remain distinctly named and distinctly defined.

## J. Outcome Verification

`LUXSMED >= 8.2 kPa`, recomputed independently this pass at row level across all 7,153
participants: **0 deviations**. 666/6,487/9.31%, exact match.

## K. Predictor Verification

Exactly 10 primary predictors, exact name match between the Phase 2 registry and Phase 3 feature
whitelist. No forbidden, outcome, or quality-only variable present. No unverified auxiliary
variable present (enforced by `phase3_02_target_and_features.py`'s whitelist check).

## L. Missing-Data Consistency

Complete-case primary strategy applied in Phase 3 (0 predictor missingness by cohort construction,
re-confirmed). Black-participant differential-exclusion finding (41.3% of excluded vs. 25.0% of
retained) re-confirmed present in `missing_data_protocol.md` this pass — not scrubbed.

## M. Fairness-Provenance Status

**Required language, used exactly:** "Historical pre-specification of subgroup bins could not be
independently established from strong repository provenance." Live re-check this pass:
`git log --follow --oneline -- documentation/phase2/fairness_subgroup_protocol.md` shows exactly
one commit (`c9c6ee3`), the same bulk commit containing all Phase 3 code — so file existence is
commit-provable, ordering relative to Phase 3 training is not. Full detail:
`results/end_to_end/subgroup_provenance_status.md`. Bins ARE now frozen and committed
prospectively (verified: sex/race-ethnicity/age/BMI bins all present, unchanged since `c9c6ee3`).
No fairness result exists anywhere in the repository (live-confirmed this pass via file search),
so no post-hoc reverse-engineering from a result is possible even under the weakest reading.

## N. Uncertainty/Conformal Handoff

"Split Conformal Prediction" confirmed as the frozen method name (re-read live this pass).
Proper-train N=4,005, calibration N=1,002, calibration positives=93 — all re-confirmed live this
pass, exact match. Disjointness (proper∩calib=0, calib∩test=0, train∩test=0) re-confirmed live.
**Conformal inference itself was NOT executed** — only the design/partition existence was
verified, per instruction.

## O. Train/Test Integrity

5,007/2,146, 70/30, seed=42, stratified, zero overlap, full coverage, hash stable since lock —
all re-confirmed live this pass.

## P. CV Design

5-fold `StratifiedKFold(shuffle=True, random_state=42)`, training partition only. `validation_ids.csv`
confirmed still explicitly documented as NOT an independent validation cohort (exact required
sentence re-confirmed present in `cv_validation_design.md` this pass). Canonical alias
`cv_fold_assignment_ids.csv` confirmed to exist.

## Q. Preprocessing Leakage

`results/end_to_end/preprocessing_leakage_audit.md` (rewritten this pass with fresh live grep
evidence, including a `refit=True` / zero-`pipe.fit`-in-eval-script check not previously
documented in this exact form). **PASS.**

## R. Class-Imbalance / MLP Audit

Per-model handling re-confirmed live from the model registry this pass. MLP sensitivity values
(original 0.8229, balanced 0.8335, CI [-0.0050, 0.0272]) — previously reproduced exactly from raw
prediction files in the prior audit pass; not re-executed this pass since no code affecting them
changed (re-running an unchanged deterministic computation would not add new evidence). MLP_balanced
confirmed NOT promoted — `downstream_model_retention_decision.md` unchanged.

## S. Hyperparameter Configuration Audit — **THE MANDATED NEW CHECK**

**`results/end_to_end/hyperparameter_configuration_count_audit.csv` and
`documentation/end_to_end/hyperparameter_count_verification.md`.** Method: live `ast` module
parse of `src/phase3_05_train_and_tune.py`'s literal grid dictionaries and search-type/n_iter
assignments — NOT a read of any CSV the training script produced. Per-model:
logistic=6 (exhaustive grid), random_forest=20 (randomized, capped from 36 possible),
xgboost=20 (randomized, capped from 108), lightgbm=20 (randomized, capped from 108),
mlp=18 (exhaustive grid). **Sum = 84.** Cross-checked against the actual `cv_results_`-derived
registry: also 84, per-model breakdown identical. **`actual_configuration_count == 84`: CONFIRMED
by two independent methods that agree exactly.** The "84" in prior reports was correct, not a
manually-transcribed unverified figure.

## T. Threshold Audit

Youden's J, out-of-fold training CV predictions, code-order-verified (line-number check,
re-confirmed this pass) to precede test-set load. **Classification: PHASE 3 AMENDMENT** —
Phase 2 named it only as an "e.g." example and explicitly deferred final selection; Phase 3
formally adopted it. Not claimed as pre-specified.

## U. Model Comparison

CV ROC-AUC 0.8157–0.8212 (re-confirmed live), test ROC-AUC 0.8229–0.8429 (re-confirmed live),
PR-AUC 0.3508–0.3729 (re-confirmed live). 0/10 pairwise comparisons significant after FDR
(re-confirmed live). **Language used throughout:** "no statistically significant pairwise
superiority was demonstrated after FDR correction" — the word "equivalent" does not appear as a
model-comparison claim anywhere in the frozen reports (re-checked this pass).

## V. PR-AUC Context

Test prevalence 9.32% (train 9.31%), no-skill PR-AUC baseline = prevalence = 0.0932. Observed
PR-AUC 0.35–0.37 is 3.76×–4.00× baseline — re-confirmed live this pass. Never described as
"excellent" in isolation anywhere in the frozen reports.

## W. H1 Interpretation

Re-checked this pass: every instance of the string "H1 was proven" in the repository occurs
inside an explicit prohibition sentence ("Not used: ..."), verified by reading surrounding
context, not substring match alone. The actual claim used throughout is "observed discrimination
was consistent with the pre-specified H1 expectation."

## X. Confidence-Interval / Bootstrap / FDR Audit

n=2,000 paired bootstrap, seed=42, percentile CI, Benjamini-Hochberg FDR, family scoped explicitly
to "baseline model comparisons only" — re-confirmed by direct read of
`inference_methodology_amendment.md` this pass. **Classification: PHASE 3 AMENDMENT**, explicitly
not claimed as Phase-2-pre-registered (Phase 2 fixed this convention for fairness/subgroup
comparisons only, not model comparisons).

## Y. Protocol Amendment Reconciliation — **THE MANDATED NEW CHECK**

**Report-stated count: 7. Registry count (live-counted this pass, direct table-row enumeration):
7. MATCH: YES.** Full reconciliation: `results/end_to_end/protocol_amendment_reconciliation.csv`.
**Honest categorization added this pass** (not present in the prior registry): of the 7, only
**4 are genuine scientific/methodological protocol amendments** (#1 Youden's J, #2 bootstrap/FDR,
#3 MLP sensitivity, #4 conformal calibration split reservation); **3 are documentation/governance
actions bundled into the same registry** (#5 canonical filename alias, #6 withdrawal of an
earlier audit's mtime claim, #7 the initial bulk git commit) — none of these 3 change any
scientific computation. All 7 titles are unique; zero duplicates.

## Z. Test-Set Contamination

8/8 pathways PASS, re-confirmed this pass via live code inspection (feature selection, model
selection, hyperparameter tuning [including the newly re-verified 84-config search], class
imbalance, threshold, preprocessing [Section Q], fairness [not yet applicable], calibration [not
yet applicable]). Zero UNCERTAIN results. `results/end_to_end/test_set_contamination_audit.md`.

## AA. Reproducibility

44/44 tests re-run live this pass (fresh execution, not quoted): 20/20 original + 24/24
remediation. All 5 models' discrimination metrics, the hyperparameter count, and the protocol
amendment count were all independently, programmatically re-derived this pass — none merely
quoted from a prior report.

## AB. Environment

Python 3.14.3; scikit-learn==1.9.0, xgboost==3.4.1, lightgbm==4.7.0, imbalanced-learn==0.14.2 —
re-confirmed via live `pip freeze` in the immediately-preceding audit pass; environment unchanged
since (no package install/upgrade commands were run this pass).

## AC. Historical Provenance

`results/end_to_end/provenance_strength_matrix.csv` — 18 decisions classified. **Tier A
(commit-level or live-reproduced)**: 14 decisions, including all Phase 1 cohort numbers, all
Phase 3 leakage-safety structural proofs, the hyperparameter count, and the amendment count.
**Tier D (timestamp-only)**: 4 decisions — Phase 2's outcome threshold, predictor list, fairness
bins, and missing-data strategy, each *relative to Phase 3 training specifically* (their existence
is commit-provable; their ordering before Phase 3 code is not). No decision was upgraded from a
weaker tier to a stronger one without new evidence.

## AD. Dependency Graph

`results/end_to_end/research_pipeline_dependency_graph.md` (unchanged from the prior pass — no
new dependency was introduced this audit). One disclosed traceability gap: `phase3_common.py`'s
constants are manually transcribed from the Phase 2 document, partially mitigated by independent
recomputation in `phase3_01_handoff_verification.py`.

## AE. Human Spot Check

**`documentation/end_to_end/human_spot_check.md`** — explicitly recommends the user manually
verify the hyperparameter configuration count (84) by hand-counting the grid dimensions in
`src/phase3_05_train_and_tune.py` and cross-checking against
`results/tables/phase3_hyperparameter_search_registry.csv`'s row count, in their own terminal.
This audit does **not** claim to be independent of the AI pipeline that produced the code it
checks — that limitation is stated explicitly, not glossed over.

## AF. Remaining Limitations (all previously disclosed; none new and blocking)

1. Phase 2/3 protocol-before-training chronology not git-provable at sub-commit granularity
   (Section AC, Tier D).
2. `phase3_common.py` constants manually transcribed, not parsed (Section AD).
3. MLP class-imbalance handling remains structurally asymmetric vs. the other 4 models (sklearn
   API constraint; sensitivity-tested, not eliminated).
4. Conformal-valid model refit on `proper_train_ids.csv` still pending (correctly deferred to the
   Uncertainty phase, which has not started).
5. Of the 7 registered "protocol amendments," 3 are governance/documentation actions rather than
   scientific-method changes — this was not previously made explicit and is disclosed for the
   first time in Section Y of this pass.

None of these five affects the validity of any Phase 1–3 cohort, outcome, predictor, split, or
discrimination result.

## AG. Final Sign-Off

**VERIFIED WITH DOCUMENTED NON-BLOCKING LIMITATIONS.**

Does not qualify for FULLY VERIFIED only because Tier-D provenance items (AC) remain — by design,
no amount of re-auditing can convert timestamp-only evidence into commit-level evidence after the
fact; only future incremental committing practice (recommended in the forensic audit) can prevent
recurrence. Every other FULLY VERIFIED criterion is met: all handoffs pass, all numbers reconcile,
both previously-unverified counts (84 hyperparameters, 7 amendments) are now programmatically
confirmed, test-set isolation passes structurally, reproducibility passes live, and no unexplained
protocol change remains.

## AH. Readiness for Calibration

**Ready**, conditioned on the same two items as the prior audit: (1) perform the outstanding
conformal-valid model refit before any Uncertainty-phase code runs, and (2) commit Calibration's
frozen protocol document in its own standalone commit, separate from Calibration's execution code
— the single concrete practice that would let the next phase earn a true Tier-A/FULLY VERIFIED
rating on this exact provenance question.
