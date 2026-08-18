# CV-Based Development Design (Clarification, Not a Three-Way Split)

**Generated:** 2026-08-18 16:59:40

## Explicit clarification

This project's frozen `documentation/phase2/model_development_protocol.md` specifies: *"5-fold stratified cross-validation within the training set only, for hyperparameter tuning and model selection"* -- it does NOT specify a separate, fixed, disjoint validation partition distinct from the 70% training set and the 30% locked test set.

**`data/processed/splits/validation_ids.csv` MUST NOT be read as an independent validation cohort.** It is byte-identical to `train_ids.csv` by construction. It exists only because the generic Phase 3 deliverable template requested a `validation_ids.csv` file; its actual content and purpose are:

> **`validation_ids.csv` = the CV-development partition. Every participant in it serves as held-out (out-of-fold) validation data exactly once across the 5 stratified CV folds during hyperparameter search. There is no participant held out from training as a separate, disjoint validation set.**

## Canonical filename (added at closure verification, item 1)

The name `validation_ids.csv` is retained (for backward compatibility with the original Phase 3
deliverable list, which named this exact path) but is no longer the sole or primary name. A
second, unambiguous file with identical content has been added:

> **`data/processed/splits/cv_fold_assignment_ids.csv`** — byte-identical to both
> `train_ids.csv` and `validation_ids.csv`. This is the name that should be used in any new
> documentation, methods-section prose, or code going forward, since it directly states what
> the file is (the pool of SEQNs assigned across CV folds) rather than implying a separate
> held-out cohort. `validation_ids.csv` remains on disk only as a legacy alias satisfying the
> original deliverable path; it is not deprecated/removed to avoid breaking any existing
> reference, but it should not be cited in new writing.

## Correct terminology for downstream use

| Term | What it means in THIS project | What it does NOT mean |
|---|---|---|
| "Training partition" | The 70% (N=5,007) used for both model fitting and CV | — |
| "Validation predictions" (`results/predictions/validation_predictions_<model>.csv`) | Out-of-fold predictions from 5-fold CV, computed WITHIN the training partition | NOT predictions on a separate held-out set never used in any fold's training |
| "Test set" | The locked 30% (N=2,146), touched exactly once for final evaluation | — |

## Why this matters (per remediation Part 3D)

A future researcher reading only `validation_ids.csv`/`train_ids.csv` filenames could reasonably assume a classic train/validation/test three-way split was used, which would misrepresent this project's actual (valid, frozen) CV-based development design. This document exists specifically to prevent that misreading. No data or code was changed by this clarification -- it is a documentation fix, not a methodological amendment.

## Split integrity (re-confirmed)

- Train N=5,007, Test N=2,146 (sum=7,153, matches full cohort exactly)
- Train/test overlap: 0
- Split seed: 42

## Demographic composition (descriptive only, not used to alter the split)

| partition              |    n |   outcome_prevalence_pct |   pct_Male |   pct_Female |   median_age |   median_bmi |
|:-----------------------|-----:|-------------------------:|-----------:|-------------:|-------------:|-------------:|
| Full cohort (N=7,153)  | 7153 |                     9.31 |      49.36 |        50.64 |           50 |         28.5 |
| Train (N=5,007)        | 5007 |                     9.31 |      49.61 |        50.39 |           50 |         28.5 |
| Test (N=2,146, LOCKED) | 2146 |                     9.32 |      48.79 |        51.21 |           50 |         28.4 |
