# Deferred Sensitivity Analysis Results Report

**This is "Deferred Sensitivity Analysis Execution" — NOT a new numbered project phase.** Project
Phase 8 (Generalization = Mentor Phase 14) remains the last officially-numbered phase; no Phase 9
exists in `documentation/phase_numbering_crosswalk.md` or `info.md` (re-verified live this task).

## 1. Executive summary

Three of the four Phase-2-frozen sensitivity analyses — alternative fibrosis threshold (8.0 vs.
8.2 kPa), alternative elastography eligibility (CAND_2, N=7,639), and the fasting-extended
predictor architecture (CAND_3, N=3,582) — were executed as controlled, pre-specified robustness
checks. The fourth (multiple imputation) was already executed in a prior task and is not rerun. A
genuine cross-document inconsistency was found and disclosed regarding a fifth candidate,
"all-ages 12+"/CAND_4: it is **not executed**, reported as **ALL-AGES 12+ SENSITIVITY STATUS
UNRESOLVED — NO EXECUTION WITHOUT SOURCE-LEVEL CONFIRMATION**.

**Result:** the project's central conclusions are, in the main, robust. Discrimination (AUC) and
the qualitative calibration pattern (large systematic overprediction for the 4 class-weighted
models, near-zero intercept for MLP) replicate almost perfectly across every sensitivity cohort
and threshold (29/30 STABLE or MOSTLY STABLE, 0 material changes, 0 reversals). The project's most
central fairness finding — BMI-Obese participants show substantially higher sensitivity than
Normal-BMI — is **completely robust**: direction and statistical significance hold in all 5
models across all 3 sensitivity variants (15/15 STABLE). The Age-60+ finding is directionally
robust (never reverses) but **loses statistical significance in the majority of sensitivity
variants** for the models that were significant in the primary analysis — a genuine, honestly
reported attenuation, most pronounced under the smaller fasting-extended cohort.

**Final status: DEFERRED SENSITIVITY ANALYSIS COMPLETE — MAIN FINDINGS PARTIALLY ROBUST.**

## 2. Purpose of sensitivity analysis

Per this task's own Core Principle: to determine whether the completed study's important
conclusions remain reasonably stable when repeated under alternative, pre-specified conditions —
not to find a better result, and not to hide an unfavorable one.

## 3. Source of the frozen sensitivity protocol

`documentation/phase2/sensitivity_analysis_plan.md` (4 selected sensitivity dimensions),
cross-verified against `documentation/phase2/statistical_analysis_plan.md` (PRIMARY/SECONDARY/
EXPLORATORY tiers) and `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` (authoritative
consolidation). Full extraction: `documentation/validation/
deferred_sensitivity_scope_reconciliation.md`.

## 4. Final list of authorized sensitivity analyses

| # | Analysis | Status before this task | Executed this task? |
|---|---|---|---|
| 1 | Alternative fibrosis threshold (8.0 vs. 8.2 kPa) | NOT EXECUTED | **YES** |
| 2 | Alternative elastography eligibility (CAND_2) | NOT EXECUTED | **YES** |
| 3 | Fasting-extended architecture (CAND_3) | NOT EXECUTED | **YES** |
| 4 | Multiple imputation | EXECUTED (prior task, Non-Hispanic Black scope only) | No — not rerun |

## 5. All-ages-12+ reconciliation

A genuine, previously incompletely-diagnosed inconsistency was found this pass. `sensitivity_
analysis_plan.md` states all-ages/CAND_4 is folded into item 2 with no separate status.
`statistical_analysis_plan.md` independently lists **"All-ages sensitivity cohort: CAND_4"** as
its own distinct EXPLORATORY-tier item, separate from its own SECONDARY-tier CAND_2 item.
`PHASE2_PROTOCOL_FREEZE.md` lists CAND_2 and CAND_4 with apparent parity as "sensitivity cohorts"
while separately stating only "4 pre-specified" analyses exist. All four source documents share
one commit (`c9c6ee3`), so no precedence is recoverable from git history. Per this task's explicit
instruction not to guess: **ALL-AGES 12+ SENSITIVITY STATUS UNRESOLVED — NO EXECUTION WITHOUT
SOURCE-LEVEL CONFIRMATION.** This corrects, and does not silently let stand, an earlier closure
task's conclusion that had not cross-referenced `statistical_analysis_plan.md`. Full detail:
`documentation/validation/deferred_sensitivity_scope_reconciliation.md` §6.

## 6. Multiple-imputation scope status

Already executed (targeted Non-Hispanic Black CV-OOF sensitivity/FNR question only; MI ROBUSTNESS
PARTIAL). **Not rerun.** No broader MI replication (calibration, fairness beyond Black subgroup,
uncertainty) was ever frozen with an explicit execution scope, so none is performed — logged in
the execution matrix as `DO NOT EXECUTE — NOT FROZEN`, not silently expanded.

## 7. Primary cohort definition

CAND_1_QUALITYVALID_ADULT_BROAD, N=7,153, 666 positive at LUXSMED≥8.2kPa (9.31% prevalence), 10
frozen predictors — unchanged, re-verified this pass, never modified.

## 8. Relaxed-elastography analysis (Analysis A)

CAND_2 (N=7,639, 804 positive, verified exactly against the archived count). Fresh 70/30 split
(seed=42): train N=5,347, test N=2,292. Frozen Phase 3 hyperparameters reused; fresh per-model
Youden's-J-on-CV-OOF threshold. Test ROC-AUC 0.8526–0.8572 across the 5 models — if anything
slightly higher than the primary cohort's 0.8229–0.8429. Calibration: intercepts −2.23 to −2.12
for the 4 class-weighted models, +0.03 for MLP — the identical qualitative pattern as primary.

## 9. Fasting-extended analysis (Analysis B)

CAND_3 (N=3,582, 319 positive, verified — this cohort already existed as `data/processed/
analysis_dataset_secondary.parquet` from Phase 2 and was verified, not reconstructed). Fresh
70/30 split: train N=2,507, test N=1,075. 12 predictors (10 primary + fasting glucose/
triglycerides). Test ROC-AUC 0.8280–0.8457. Calibration pattern identical to primary (MLP
intercept −0.11 vs. −1.71 to −2.33 for the other 4). Per the project's own established caution
(`primary_cohort_decision.md`), this cohort's race/ethnicity subgroup positive counts are smaller
(min subgroup positive N=16 archived) — precision-limited subgroup estimates were not
over-interpreted; the fairness check here was restricted to BMI/Age only, per the frozen scope
decision (Amendment #13), avoiding the smallest, most fragile subgroups entirely.

## 10. Alternative-threshold analysis (Analysis C)

**Required no retraining.** CAND_1's cohort, predictors, and frozen Phase 3 models are unchanged;
only the outcome label changes (8.0kPa vs. 8.2kPa, 715 vs. 666 positive in the full cohort, a
31-participant OOF-training relabeling out of 5,007). Re-evaluated the already-frozen Phase 3
test-set and OOF predicted probabilities against the already-existing `outcome_sensitivity_8.0kPa`
column — no model was refit, no model's test set was re-accessed for fitting. Test ROC-AUC
0.8145–0.8326. The re-derived Youden's-J thresholds turned out numerically identical to the
primary 8.2kPa thresholds for all 5 models — verified not a bug (only 31/5,007 OOF labels differ
between the two outcome definitions, and the ROC curve's optimal-J point landed on the same
candidate threshold in both cases).

## 11. All-ages-12+ analysis

**Not executed** — see Section 5.

## 12. Cohort sizes and event counts

| Cohort | N | Positive | Prevalence | Train N | Test N |
|---|---|---|---|---|---|
| CAND_1 (primary, @8.2kPa) | 7,153 | 666 | 9.31% | 5,007 (frozen) | 2,146 (frozen, locked) |
| CAND_1 (@8.0kPa, sensitivity) | 7,153 | 715 | 10.00% | 5,007 (same participants) | 2,146 (same participants) |
| CAND_2 (relaxed elastography) | 7,639 | 804 | 10.52% | 5,347 (fresh split) | 2,292 (fresh split) |
| CAND_3 (fasting-extended) | 3,582 | 319 | 8.91% | 2,507 (fresh split) | 1,075 (fresh split) |

## 13. Modeling procedure

Hyperparameters: frozen Phase 3 `best_params` reused unchanged for every model in every
sensitivity cohort (no new search, Amendment #13). Threshold: Youden's J on 5-fold
`StratifiedKFold(seed=42)` CV-OOF, computed fresh per cohort per model, never touching that
cohort's own test partition (Analyses A/B) or the locked Phase 3 test set (Analysis C).
Preprocessing: `SimpleImputer`(median, structural no-op)+`StandardScaler` (where used) fit only
on each cohort's own training partition.

## 14. Leakage prevention

Verified structurally (`tests/test_deferred_sensitivity_pipeline.py` TEST4, TEST9): threshold
derivation reads only training/OOF data; final model fit uses only the training partition;
Analysis C's threshold derivation reads only the already-frozen OOF file, never the test file, and
no `.fit()` call occurs anywhere before the sensitivity-comparison logic in that script. No script
in this task references `data/processed/splits/test_ids.csv`. No primary-study artifact (Phase 3
models, Phase 3/4/5/6/7/8 results, the MI report) was modified — spot-check hashes confirmed
unchanged (`src/phase3_common.py`, `test_ids.csv`, the MI report).

## 15. Statistical inference

Bootstrap CI (n=2,000, seed=42) for AUC and for the BMI/Age fairness sensitivity-disparity
metric, matching the project's established convention throughout Phases 3–8. The
primary-vs-sensitivity comparison (Section 16) is a **new, self-contained comparison**, not
merged into any Phase 3/4/5/6/7 multiple-comparison family — verified structurally (no BH-FDR
computation occurs anywhere in the sensitivity execution scripts; the comparison classifies each
finding independently against its own primary-analysis baseline).

## 16. Primary-vs-sensitivity comparison

`results/sensitivity/primary_vs_sensitivity_comparison.csv` (60 rows), classified programmatically
from the actual result files:

| Finding category | STABLE | MOSTLY STABLE | PARTIALLY STABLE (attenuated significance) | MATERIAL CHANGE | REVERSED |
|---|---|---|---|---|---|
| Discrimination AUC (15 rows) | 14 | 1 (MLP/CAND_2, +0.034) | 0 | 0 | 0 |
| Calibration intercept (15 rows) | 15 | 0 | 0 | 0 | 0 |
| BMI-Obese fairness disparity (15 rows) | 15 | 0 | 0 | 0 | 0 |
| Age-60+ fairness disparity (15 rows) | 6 (incl. 3 "non-significant in both") | 0 | 9 | 0 | 0 |

**No finding was reversed anywhere. No finding showed an unexplained material change.**

## 17. Stability classification

- **Discrimination:** STABLE.
- **Calibration (qualitative dissociation pattern):** STABLE.
- **BMI-Obese fairness:** STABLE — the project's single most robust finding.
- **Age-60+ fairness:** PARTIALLY STABLE — direction never reverses, but statistical significance
  is lost in 9 of 12 sensitivity-variant instances where the primary finding was itself
  significant (Random Forest, XGBoost, LightGBM, MLP across CAND_2/CAND_3/8.0kPa). Logistic
  (already non-significant in the primary analysis) remains non-significant everywhere — itself a
  stable result, just not a significant one.

## 18. Fairness interpretation

The Age-60+ attenuation is not automatically interpreted as evidence the original finding was
spurious. Smaller sensitivity cohorts (especially CAND_3, N=3,582, roughly half the primary
cohort) mechanically widen bootstrap CIs for any subgroup comparison — this is a genuine,
expected precision effect, not necessarily evidence the underlying effect size shrank. The
Non-Hispanic Black cohort-selection consideration (41.3% of complete-case exclusions vs. 25.0% of
retained) is a separate, already-addressed question (targeted MI task) and is not conflated with
this BMI/Age fairness sensitivity check.

## 19. Calibration interpretation

The core Phase 4 finding — near-identical discrimination but substantially different raw
calibration across the 5 models, with MLP closest to calibrated — replicates without exception
across every sensitivity cohort and threshold tested. This is now the project's most
robustness-tested finding.

## 20. Uncertainty interpretation

**Not assessed in this task.** Conformal/uncertainty replication for the sensitivity cohorts was
never frozen with an explicit execution scope and is explicitly deferred (Amendment #13, Section
22/future work below) — not silently dropped.

## 21. Limitations

- Uncertainty (conformal coverage) was not replicated for any sensitivity cohort — the project's
  central fairness/coverage co-occurrence finding (Phase 5↔Phase 6) has not been stress-tested
  under alternative cohort definitions.
- All-ages/CAND_4 remains genuinely unresolved and unexecuted.
- CAND_3's smaller size limits statistical power for any subgroup comparison beyond BMI/Age; race/
  ethnicity-level sensitivity checks were not attempted here given the project's own documented
  precision concerns for that cohort.
- Fresh 70/30 splits for CAND_2/CAND_3 are not the same participants as the locked Phase 3 test
  set — some overlap with Phase 3's training population is expected and not a leakage concern
  (each cohort's own train/test boundary is respected within itself), but cross-cohort
  comparisons are not paired at the participant level.
- NHANES elastography (`LUXSMED`) remains a surrogate outcome context, not biopsy-confirmed
  histology — unaffected by, and unrelated to, this sensitivity work.

## 22. Reproducibility

Isolated clean rerun of the CAND_2/CAND_3 training+evaluation script reproduced every threshold,
AUC, sensitivity, and calibration value exactly (byte-identical) to the committed run — confirming
full determinism under the fixed seed (42) used throughout. Analysis C requires no reproducibility
rerun beyond what Phase 3's own already-verified reproducibility record covers, since it performs
no model fitting.

## 23. Tests

`tests/test_deferred_sensitivity_pipeline.py`: 39 live checks (frozen cohort/predictor/outcome
verification, no-leakage structural checks, authorized-model-family enforcement, hyperparameter-
reuse verification, correct subgroup definitions, statistical-family separation, primary-artifact
immutability, all-ages-unresolved enforcement, MI-not-rerun enforcement, no-reversed/no-
not-assessable findings, uncertainty-deferral disclosure). **All 39 passed.**

**One implementation bug found and fixed during this task:** the initial `deferred_sensitivity_
execution_matrix.csv` (Commit A) contained an unquoted field with an embedded comma ("EXECUTED
(targeted Non-Hispanic Black question only, prior task)"), which broke CSV parsing. Caught when
the test suite failed to load the file; fixed by rewriting the CSV via Python's `csv` module
(proper quoting) in this commit — disclosed here, not silently corrected.

## 24. Git/provenance

| Commit | Subject |
|---|---|
| `a02f60a` | Commit A — scope verification and execution matrix |
| `f6b17e6` | Commit B — sensitivity cohort construction |
| `9d7abb0` | Commit C — sensitivity execution (Analyses A, B, C) |
| `3ab927b` | Commit D — primary-vs-sensitivity statistical comparison |
| *(Commit E, created immediately after this report)* | Tests + final report + CSV bugfix |

Pushed and independently verified via both `git fetch`+`rev-parse` and `git ls-remote`.

## 25. Scientific conclusion

The project's central conclusions — near-identical discrimination across 5 models, a real
discrimination/calibration dissociation, and a robust BMI-Obese fairness disparity — are
**robust** to the three executed sensitivity analyses. The Age-60+ fairness finding is
**directionally robust but not statistically robust** under smaller or alternative cohorts —
reported honestly as a genuine limitation of that specific finding's statistical strength, not
smoothed over. No sensitivity analysis reversed, materially changed, or contradicted any primary
conclusion.

## 26. Remaining work (future work, not silently converted into new experiments)

- Resolve the all-ages/CAND_4 status at the source-document level (would require the researcher
  or a future protocol amendment to state definitively which frozen document governs).
- Replicate conformal-uncertainty coverage on CAND_2/CAND_3/8.0kPa, given its direct relevance to
  the project's central fairness↔coverage co-occurrence finding.
- If pursued, race/ethnicity-level sensitivity checks on CAND_3 would need explicit
  precision-tier labeling given its known small subgroup counts.

Per this task's own Part 22: **this work is now complete and bounded.** No further threshold,
cohort, model, or subgroup sensitivity check is added beyond what was pre-specified and executed
here.

## Final Status

**DEFERRED SENSITIVITY ANALYSIS COMPLETE — MAIN FINDINGS PARTIALLY ROBUST**

(Discrimination, calibration, and the BMI-Obese fairness finding are fully robust; the Age-60+
fairness finding is directionally robust but loses statistical significance in most sensitivity
variants — this mixed picture, not a uniform "robust" or "not robust," is the accurate and honest
summary.)
