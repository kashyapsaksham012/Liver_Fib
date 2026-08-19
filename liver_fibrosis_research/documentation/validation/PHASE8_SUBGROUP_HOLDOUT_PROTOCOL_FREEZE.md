# Phase 8 Subgroup-Holdout Generalization — Protocol Freeze

**Generated:** 2026-08-19, live, before any Phase 8 model training or holdout evaluation.

> **"The Phase-8 holdout subgroup was frozen before any Phase-8 model training or holdout
> evaluation."**

## 1. Official Phase 8 definition

Project Phase 8 = Mentor Phase 14 = "Generalization" (`documentation/phase_numbering_crosswalk.md`,
verified live this task). Mentor `info.md` text, quoted in full: *"If your NHANES data support
it, perform a temporal or subgroup validation. For example: train on one portion/cycle, test on
another. Or perform subgroup holdout experiments. Ask: Does performance drop? Which groups are
most affected? Does calibration remain stable?"*

## 2. Temporal-validation infeasibility

Confirmed not feasible: `SDDSRVYR` is a single constant value (66.0) across the entire NHANES
"2017–March 2020 pre-pandemic" combined release used by this project; no sub-cycle or exam-date
variable distinguishing 2017–2018 from 2019–March 2020 exists in any raw source file. Full detail:
`documentation/validation/phase8_pre_execution_snapshot.md`. Subgroup-holdout validation is the
only mentor-authorized design that is data-feasible.

## 3. Selected subgroup

**Non-Hispanic Black** (`RIDRETH3 == 4.0`), per
`documentation/validation/phase8_holdout_candidate_decision.md` — a prior, explicit researcher
instruction ("Hold out Non-Hispanic Black participants entirely and retrain"), independently
confirmed feasible by the candidate matrix (mildest training-population impact of the three
candidates evaluated: 26.58% positive-case reduction vs. 70.27% for BMI-Obese and 48.50% for
Age-60+).

## 4. Training population

All primary-cohort participants (`data/processed/analysis_dataset_primary.parquet`, N=7,153)
**except** Non-Hispanic Black: **N=5,366, 489 positive, 4,877 negative (9.11% prevalence)**.

## 5. Holdout population

All primary-cohort Non-Hispanic Black participants: **N=1,787, 177 positive, 1,610 negative
(9.90% prevalence)**. Precision tier (frozen `phase5_common.precision_tier` heuristic): 177 ≥ 100
and 1,610 ≥ 100 → **primary-feasibility candidate**, the highest tier.

## 6. Model families

The 5 frozen Phase 3 families, unchanged: Logistic Regression, Random Forest, XGBoost, LightGBM,
MLP-original. No new family is added.

## 7. Hyperparameter policy

**Reuse Phase 3's frozen `best_params` unchanged for each model family** (Option A from the
mega-prompt's Part 13). Rationale: (a) consistent with this project's already-established
precedent for population-composition-driven retraining (the targeted MI sensitivity analysis,
Amendment #12, made the identical choice for the same reason); (b) isolates the experiment to
testing whether the *absence* of Non-Hispanic Black from training changes generalization, without
conflating that question with a second source of variability (a fresh hyperparameter search on a
reduced population); (c) avoids the risk of overfitting a new search to an already-smaller
training set. No hyperparameter search is performed in Phase 8.

## 8. Preprocessing policy

`StandardScaler` (for `logistic`/`mlp`) is refit on the Phase 8 training population only.
Imputation is a structural no-op: the primary cohort has 0% missingness on all 10 frozen
predictors by construction (verified live, `analysis_dataset_primary.parquet`). No preprocessing
transform is ever fit using holdout (Non-Hispanic Black) data.

## 9. Threshold policy

A **new** per-model classification threshold is derived via **the same frozen method** Phase 3
originally used (Youden's J on 5-fold `StratifiedKFold(seed=42)` CV-out-of-fold predictions —
Amendment #1, `protocol_amendment_registry.md`), computed **on the Phase 8 training population
only**, before any holdout evaluation. Reusing Phase 3's original numeric threshold values
verbatim would be methodologically incorrect here, since the underlying model weights differ (a
different, smaller training population) — the predicted-probability distribution shifts, and an
unchanged threshold would not correspond to the same operating point. Applying the *same,
already-frozen selection method* to the new model is not a new methodological decision; it is the
correct, leakage-safe reapplication of an existing one.

## 10. Calibration policy

**Authorized** — mentor `info.md` explicitly asks "Does calibration remain stable?" Evaluate the
frozen (non-recalibrated) Phase 8 model's calibration intercept, slope, and Brier score on the
holdout population. No recalibration is performed in Phase 8 (out of scope; the mentor text does
not request a fix, only an assessment).

## 11. Uncertainty (conformal) policy

**NOT AUTHORIZED.** The mentor's Phase 14 text does not mention uncertainty or conformal
prediction anywhere (unlike calibration, which is named explicitly). Per this project's
established discipline (the identical determination was made for the MI sensitivity analysis),
uncertainty/conformal evaluation is explicitly skipped and documented as not authorized, not
silently omitted.

## 12. Fairness policy

Phase 5's fairness machinery (per-model subgroup sensitivity comparisons) is **not** re-run inside
this experiment — Phase 8 is not another Phase 5 analysis (Part 19 of the mega-prompt). The
question "which groups are most affected" is answered at the **model** level within this one
holdout experiment (which of the 5 model families generalizes best/worst to the excluded group),
not via new intersectional subgroup analysis inside the holdout population itself.

## 13. Phase 7 mitigation policy

Not authorized and not applicable: Non-Hispanic Black was never a Phase 7 mitigation target
(confirmed live: zero rows for this category in `results/mitigation/test_set_mitigation_final.csv`).

## 14. Primary endpoint

Per model, on the fully-unseen Non-Hispanic Black holdout population: ROC-AUC, PR-AUC,
sensitivity, and specificity at the Phase-8-derived threshold (Section 9).

## 15. Secondary endpoints

Calibration intercept, slope, Brier score (Section 10); population-shift descriptive comparison
(Section 17).

## 16. Inference method

Bootstrap CI, n=2,000, seed=42 (the project's established convention, reused deliberately —
consistent with Phase 4/5/6/7/MI).

## 17. Population-shift analysis

Compare the Phase 8 training population (Non-Hispanic Black excluded) against the holdout
population (Non-Hispanic Black only) on: age, BMI, sex, the 8 laboratory predictors, outcome
prevalence, and missingness (structurally 0% for both, by construction of the primary cohort).

## 18. Stop conditions (carried from mega-prompt Part 33)

Training-size inadequacy, holdout leakage, holdout influencing tuning/threshold selection,
unplanned methodological change mid-experiment, reproducibility failure without explanation, or
uncontrolled expansion into additional holdout subgroups all trigger a STOP, not an improvisation.

## 19. Reproducibility design

Seed=42 throughout (StratifiedKFold, bootstrap, model `random_state` where applicable). All
training/holdout ID lists, model artifacts, and predictions are hashed. One isolated clean rerun
is performed before the final report is written (Part 27 of the mega-prompt).

## 20. Relationship to already-completed work (explicit, not implied)

This is not a Phase 5 fairness re-run (Phase 5 trained on the full population and measured
subgroup behavior; Phase 8 trains with the subgroup entirely absent). This is not a repeat of the
targeted MI sensitivity analysis (MI asked whether *including* previously-excluded participants
changes the result; Phase 8 asks whether the model generalizes to a group with *zero*
representation in training). No causal claim is made in either direction.
