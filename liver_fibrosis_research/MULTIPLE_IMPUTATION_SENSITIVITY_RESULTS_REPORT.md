# Multiple-Imputation Sensitivity Analysis — Results Report

**Targeted Sensitivity Analysis Before Phase 8** (Project Phase 8 = Mentor Phase 14 =
"Generalization", per `documentation/phase_numbering_crosswalk.md`)

## 1. Executive Summary

This task executed the single Phase-2-frozen "complete-case vs. multiple-imputation" sensitivity
analysis (`documentation/phase2/sensitivity_analysis_plan.md`, item 4;
`documentation/phase2/missing_data_protocol.md`), narrowly scoped to one question: **does
complete-case exclusion of 615 participants (7.9% of the full N=7,768 quality-valid adult pool)
materially affect Non-Hispanic Black fairness/uncertainty conclusions?** It is not a re-run of any
Phase 3–7 pipeline, not a broad robustness campaign, and not a re-opening of the closed Phase 7
BMI/Age threshold-precedence issue.

**Result:** across all 5 primary models, the complete-case-vs-MI difference in Non-Hispanic Black
subgroup sensitivity (true positive rate) at each model's frozen classification threshold is small
(range: −1.32pp to +4.16pp), and not statistically significant after Benjamini-Hochberg FDR
correction for any model (all adjusted p = 0.978). 4 of 5 models classify as **A — STABLE UNDER
MI**; 1 of 5 (MLP) classifies as **F — INDETERMINATE** (its point estimate is larger, +4.16pp, but
its bootstrap CI still includes zero). No model shows a reversed or materially strengthened
disparity.

**Final status: MULTIPLE IMPUTATION COMPLETE — NON-HISPANIC BLACK ROBUSTNESS ASSESSED.**

## 2. Important Premise Correction

Before interpreting this result, one correction to the task's own framing must be stated plainly:
**no statistically significant Non-Hispanic Black fairness or coverage disparity was found in
Phase 5 or Phase 6** (confirmed by re-reading `PHASE5_FAIRNESS_RESULTS_REPORT.md` and
`PHASE6_UNCERTAINTY_RESULTS_REPORT.md` live, not from memory, during the pre-execution snapshot —
see `documentation/sensitivity/multiple_imputation_pre_execution_snapshot.md` §"Important premise
correction"). This analysis therefore does not "reassess a finding that would otherwise stand
unquestioned" — it tests whether a data-inclusion choice (complete-case exclusion) could plausibly
*produce or mask* a Black-subgroup effect that complete-case analysis alone would miss, given the
concrete, documented differential-exclusion rate (41.3% of exclusions vs. 25.0% of retained
participants are Non-Hispanic Black). The answer, reported here, is: no material effect is
detected in either direction.

## 3. Frozen Protocol and Genuine Gaps

`missing_data_protocol.md` freezes: (a) complete-case as the PRIMARY strategy, (b) MICE-style
imputation on the full N=7,768 pool as the SENSITIVITY strategy, (c) imputation predictors
restricted to "other predictors + outcome-independent auxiliary variables only," and (d) a
leakage-safety requirement that imputation models never be refit or re-parameterized using
validation/test rows. It does **not** specify: number of imputations, the concrete algorithm,
seeds, a pooling method, or a model-refit rule. These gaps were confirmed genuine via a full
re-read of every Phase 2 document mentioning MI (`documentation/sensitivity/
mi_protocol_extraction_and_gaps.md`), not assumed.

## 4. Protocol Amendment #12

The gaps above were resolved via a single, dated, pre-execution amendment — **Amendment #12** in
`documentation/end_to_end/protocol_amendment_registry.md` (row 12, verified live via
`grep -c "^| [0-9]"` = 11 existing rows before this task, confirming #12 as the correct next
number). Specifics: m=5 imputations, `IterativeImputer(estimator=BayesianRidge(),
sample_posterior=True)`, seed=42+i per imputation i, imputation predictor matrix = the 10 frozen
primary predictors only, predictive pooling (mean predicted probability across the 5 imputed
datasets' CV-OOF outputs), model-refit = CV-OOF only, never touching the locked test set. This
amendment was committed separately (Commit A, `30a866a`) **before** any imputation was
constructed, per this task's explicit rule against silently inserting methodological decisions
into an implementation commit.

### 4.1 Self-caught implementation bug (disclosed, not hidden)

An initial run of the imputation construction script used `sample_posterior=False` (sklearn's
default). Combined with the default non-random imputation order, this produced **byte-identical
output across all 5 "imputations" regardless of seed** — silently defeating the statistical
purpose of multiple imputation (no between-imputation variance to reflect imputation uncertainty).
This was caught via routine hash comparison (`hashlib.sha256` on each output file) before any
downstream analysis used the flawed output. Fix: `sample_posterior=True` (sklearn's own documented
mechanism for generating genuinely distinct multiple imputations). Re-run confirmed 5 distinct
file hashes (Section 6 below). The bug and fix are disclosed verbatim in Amendment #12's registry
entry, per this project's standing practice of never hiding implementation mistakes.

## 5. Cohort Definitions

| Population | N | Source |
|---|---|---|
| Full quality-valid adult pool | 7,768 | `COHORT_3B_ADULT_OF_QUALITY_VALID(master)` |
| Complete-case subset of the pool | 7,153 | `pool[PRIMARY_PREDICTORS].notna().all(axis=1)` — matches the frozen primary cohort exactly |
| Excluded by complete-case | 615 (7.9%) | Pool minus complete-case |
| Non-Hispanic Black, complete-case | 1,787 | `RIDRETH3 == 4.0` within complete-case |
| Non-Hispanic Black, full MI pool | 2,041 | `RIDRETH3 == 4.0` within full pool |

The Black-subgroup N growth (1,787 → 2,041, +254 participants, +14.2%) is the direct, expected
consequence of the documented differential-exclusion rate and confirms the MI pool is doing what
it is supposed to do: retaining participants complete-case analysis drops disproportionately from
this subgroup.

## 6. MI Dataset Construction and Diagnostics

`src/mi_01_construct_and_diagnostics.py` constructed 5 static, full-pool-fit imputed datasets for
descriptive diagnostics only (missingness patterns, imputed-value ranges) — **not** used for the
leakage-safety-critical model-refit step (Section 7 fits a fresh imputer inside each CV fold).

| Imputation | Seed | File SHA-256 (first 16 hex) | Missing after imputation |
|---|---|---|---|
| 0 | 42 | `74509ff3648f74d5` | 0 |
| 1 | 43 | `14d3c44c21fd7b34` | 0 |
| 2 | 44 | `841efe8d164a9292` | 0 |
| 3 | 45 | `5a4289204910ddc5` | 0 |
| 4 | 46 | `361533d2013dba4f` | 0 |

All 5 hashes distinct (confirms the `sample_posterior=True` fix worked). 8 of the 10 primary
predictors had missingness in the full pool; `RIDAGEYR` and `RIAGENDR` had none (0% missing, as
expected for demographic fields). Full diagnostics (observed vs. imputed mean/std per variable per
imputation): `results/sensitivity/multiple_imputation_diagnostics.csv`.

## 7. Two-Arm Comparison Design

`src/mi_02_black_subgroup_comparison.py` implements a symmetric, leakage-safe, two-arm CV-OOF
comparison, deliberately **not** reusing Phase 3's N=5,007 train-only OOF predictions (which would
confound the comparison with a different evaluation population):

- **Arm 1 (complete-case):** N=7,153, `SimpleImputer(strategy="median")` (a no-op — 0% missingness
  in this subset by construction), 5-fold `StratifiedKFold(seed=42)`, frozen Phase 3 `best_params`
  reused unchanged, no hyperparameter search.
- **Arm 2 (multiple imputation):** N=7,768, fresh `IterativeImputer(BayesianRidge(),
  sample_posterior=True)` fit inside each CV fold's training portion only (mirrors Phase 3's
  leakage-safe `Pipeline`/`ColumnTransformer` pattern), repeated for each of the 5 imputations,
  pooled via the mean predicted probability (predictive pooling, Amendment #12).

Both arms use identical CV design, predictors, and hyperparameters — they differ **only** in which
participants are included and whether missing values are imputed. This isolates the effect of
imputation-based inclusion from other confounds. The locked test set is never loaded anywhere in
this script (verified structurally in Section 15).

Full per-model refit documentation: `results/sensitivity/mi_model_protocol_decision.csv`.

## 8. Black-Subgroup Fairness Comparison

`src/mi_03_black_subgroup_inference.py` extracts the Non-Hispanic Black subgroup from each arm's
OOF predictions, applies each model's frozen Youden's J threshold, and computes sensitivity/FNR/
specificity/FPR. Full table: `results/sensitivity/mi_black_subgroup_comparison.csv`.

| Model | Threshold | CC N | CC Sens. | MI N | MI Sens. | Diff (MI−CC) | 95% CI | BH-FDR p |
|---|---|---|---|---|---|---|---|---|
| logistic | 0.5173 | 1,787 | 67.80% | 2,041 | 67.68% | −0.12pp | [−9.71, +9.33]pp | 0.978 |
| random_forest | 0.4499 | 1,787 | 70.62% | 2,041 | 71.21% | +0.59pp | [−8.71, +10.04]pp | 0.978 |
| xgboost | 0.4108 | 1,787 | 79.10% | 2,041 | 77.78% | −1.32pp | [−10.09, +6.82]pp | 0.978 |
| lightgbm | 0.4988 | 1,787 | 71.19% | 2,041 | 70.20% | −0.98pp | [−10.50, +8.72]pp | 0.978 |
| mlp | 0.1065 | 1,787 | 65.54% | 2,041 | 69.70% | +4.16pp | [−5.33, +13.65]pp | 0.978 |

## 9. Inference Methodology

Bootstrap: n=2,000 resamples, seed=42, independent resampling within each arm's Black subgroup
(not paired-by-participant — the arms have different N and only partially overlapping participant
sets, since the MI pool adds 254 Black participants complete-case never sees). Two-sided bootstrap
p-value = 2·min(P(diff≤0), P(diff≥0)) among valid resamples. Multiple-comparison correction:
Benjamini-Hochberg FDR across the single 5-model family (one family per model×dimension,
consistent with this project's established convention — Amendment #11), implemented via the
project's own manual BH-FDR code (`statsmodels` is not a pinned dependency; reused the identical
algorithm already in `src/phase4_04_inference.py`).

## 10. Uncertainty/Conformal-Coverage Comparison — Not Performed

The frozen `missing_data_protocol.md` was re-read in full for any Phase-6-era conformal-coverage
language; none exists. Extending this comparison to conformal prediction-set coverage was
therefore **NOT AUTHORIZED** and is not performed. This is a genuinely open question for a future,
separately-scoped protocol amendment — not silently skipped.

## 11. Classification (Part 16 schema)

| Model | Classification |
|---|---|
| logistic | A — STABLE UNDER MI |
| random_forest | A — STABLE UNDER MI |
| xgboost | A — STABLE UNDER MI |
| lightgbm | A — STABLE UNDER MI |
| mlp | F — INDETERMINATE |

Classification rule (applied uniformly, magnitude+direction+CI, not p-value alone): magnitude
<2pp with a CI including zero → STABLE; CI excluding zero → STRENGTHENED (same direction, larger)
or ATTENUATED (opposing direction); CI including zero but magnitude ≥2pp → INDETERMINATE (the
data cannot rule out a real effect of that size, but also cannot confirm one — reported honestly
rather than rounded to "stable"). MLP's own point estimate (+4.16pp) exceeds the 2pp stability
band, but its bootstrap CI is wide enough to include zero — hence INDETERMINATE, not STABLE. No
model reaches D (REVERSED) or E (NO LONGER DETECTABLE).

## 12. Overall Robustness Conclusion

**MI ROBUSTNESS PARTIAL.** 4 of 5 models show clean, stable results under MI inclusion of the 615
previously-excluded participants. 1 of 5 (MLP) cannot be classified as stable due to bootstrap
imprecision in the Black subgroup at this sample size (N≈1,787–2,041, 177–198 positives) — this is
a precision limitation of the MLP's specific decision threshold and subgroup positive count, not
evidence of a detected true difference. No model shows evidence of a reversed or materially
strengthened disparity. **This conclusion applies only to the Non-Hispanic Black CV-OOF sensitivity
question under this specific MI specification (Amendment #12) — it is not generalized to any other
subgroup, metric, or missing-data question.**

## 13. Forbidden Overclaims — Compliance Statement

This report does **not** claim "Multiple imputation proves the model is unbiased" and does **not**
claim "Multiple imputation proves selection bias caused the disparity." Neither claim is
supportable by this analysis design (a CV-OOF sensitivity/FNR comparison cannot establish
"unbiasedness," and no significant disparity was found in Phase 5/6 for this MI check to explain a
cause for). Verified absent from this report and from `mi_black_subgroup_comparison.csv` via
automated test (`tests/test_multiple_imputation_sensitivity.py` TEST21).

## 14. Deferred Sensitivity Analyses (4 remaining, explicitly not silently forgotten)

Per `documentation/project_roadmap/deferred_sensitivity_analyses.md` (updated this task):

| # | Analysis | Status |
|---|---|---|
| 1 | Alternative fibrosis threshold (8.0 vs 8.2 kPa) | **NOT EXECUTED** — deferred due to scope/time considerations; not used to alter the primary analysis or conclusions |
| 2 | Alternative elastography eligibility (CAND_2 N=7,639) | **NOT EXECUTED** — deferred due to scope/time considerations; not used to alter the primary analysis or conclusions |
| 3 | Broad-lab vs. fasting-extended predictor architecture | **NOT EXECUTED** — deferred due to scope/time considerations; not used to alter the primary analysis or conclusions |
| 4 | Complete-case vs. multiple imputation | **EXECUTED this task** (this report) |

## 15. Leakage Safety and Scope Verification

- No script in `src/mi_0{1,2,3}_*.py` references `test_ids.csv` or loads the locked test set
  (verified structurally, `tests/test_multiple_imputation_sensitivity.py` TEST9).
- Imputation (`IterativeImputer`) is fit only inside each CV fold's training portion, mirroring
  Phase 3's `SimpleImputer`/`StandardScaler` leakage-safe pattern (`ColumnTransformer` +
  `Pipeline`) — never fit on the full pool for the model-refit/prediction step.
- No hyperparameter search occurred; each model's frozen Phase 3 `best_params` were reused
  unchanged (verified, TEST7).
- This analysis did not propagate into Phase 3 model comparison, Phase 4 calibration, Phase 5
  fairness for every subgroup, Phase 6 uncertainty for every subgroup, Phase 7 mitigation, or the
  BMI/Age mitigation threshold-precedence issue — none of those pipelines or their output
  directories were touched (verified, TEST18).
- No uncertainty/conformal-coverage artifact was produced under MI (verified, TEST17).

## 16. Reproducibility

An isolated rerun of the m=5 imputation construction (same seeds, same `IterativeImputer`
configuration, run outside any committed script to a scratch location) reproduced all 5 file
hashes exactly:

```
imputation 0 rerun hash: 74509ff3648f74d5a21ffd234c5426c45b5ec0fe34e066d0d64f339567d67a9e  (matches)
imputation 1 rerun hash: 14d3c44c21fd7b3405e12ef06de0341d19488534027e36f481ba72c1d4402508  (matches)
imputation 2 rerun hash: 841efe8d164a9292f7e64142ca0af80cad4dabde9115b0c475d568bb02d86e86  (matches)
imputation 3 rerun hash: 5a4289204910ddc5e1eb110415e931140ef4badd988a08a23087cf9e9294feb8  (matches)
imputation 4 rerun hash: 361533d2013dba4f60b3306f9f528c19b4e62fdbb7f3576f1e584d1d149e0b81  (matches)
```

This analysis never touches the locked test set, so the project's "no repeated test-set
evaluations" constraint is trivially and structurally satisfied (Section 15) — this rerun exists
only to confirm seed-level determinism of the imputation construction step itself.

## 17. Validation Tests

`tests/test_multiple_imputation_sensitivity.py`: 36 live checks (seed/hash integrity,
leakage-safety structural checks, no hyperparameter search, cohort N exactness, BH-FDR family
correctness, classification-value restriction to the authorized A–F set, deferred-analysis
bookkeeping, forbidden-overclaim absence). **All 36 passed.**

## 18. Limitations

- Black-subgroup N (1,787–2,041) and positive counts (177–198) give the bootstrap CIs meaningful
  width (roughly ±5–10pp); a true effect smaller than this cannot be distinguished from noise at
  this sample size — this is a power limitation, not a finding of "no effect."
- Predictive pooling (mean probability across imputations) was used rather than Rubin's rules
  (parameter pooling); this is standard for pooling *predictions* but does not yield a
  between-imputation variance component in the classical Rubin sense — the CV-OOF bootstrap CI
  reported here captures resampling uncertainty within each pooled-arm estimate, not
  imputation-uncertainty variance explicitly.
- This analysis addresses one specific missing-data question (complete-case vs. MI for the Black
  subgroup's sensitivity) and does not address the other 4 deferred sensitivity analyses, which
  remain genuinely open (Section 14).
- No novelty is claimed anywhere in this analysis or report; all methods (MICE-style multiple
  imputation, CV-OOF comparison, bootstrap CI, BH-FDR) are standard, well-established techniques
  applied to this project's own frozen cohort and models.

## Final Status

**MULTIPLE IMPUTATION COMPLETE — NON-HISPANIC BLACK ROBUSTNESS ASSESSED**
