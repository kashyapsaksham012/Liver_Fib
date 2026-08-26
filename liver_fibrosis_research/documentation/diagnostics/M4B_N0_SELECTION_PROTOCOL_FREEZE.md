# M4b N0 Selection Protocol Freeze

**Frozen:** 26 Aug 2026, BEFORE any candidate N0 is evaluated against the locked test set (or
against any data derived from it). This document exists because the prior "N0=100" choice in
`src/tradeoff_02_m4b_sensitivity_and_lock.py` was audited and found to be **not verifiable as
pre-specified** (`documentation/final_audit/FINAL_NUMERICAL_AND_M4B_AUDIT.md`, Audit 2B): that
script computed test-set coverage for every candidate N0 in the same run before declaring one
"locked." This protocol defines a genuine pre-specified selection rule using only non-test data,
to be followed exactly, with no changes permitted after this document is written.

## Method: `q_M4b = w * q_joint + (1-w) * q_envelope`, `w = N_joint_cal / (N_joint_cal + N0)`

Unchanged from the existing implementation
(`src/tradeoff_02_m4b_sensitivity_and_lock.py:117-125`; `documentation/final_audit/
m4b_prior_art_comparison.md:15-18`). Only the *procedure for choosing N0* is being corrected here.

## Candidate grid

`N0 in {0, 10, 25, 50, 75, 100, 150, 200, 300, 500}` — the same grid used in the prior
(non-pre-registered) sweep. Reusing the same candidate values is not itself a test-set-derived
choice; it is simply the set of values considered, fixed here before any calibration-only
cross-validation is run.

## Selection data: calibration split ONLY, never the locked test set

All N0 selection work uses exclusively `data/processed/splits/conformal_calibration_ids.csv`
(N=1,002). The locked test set (`test_ids.csv`, N=2,146) is not read, touched, or referenced by
any part of the selection procedure below.

## Selection procedure (exact, to be followed without deviation)

1. Split the N=1,002 calibration set into **5 stratified folds**, stratified by joint-cell
   membership (BMI-Obese AND Age-60+, the same binary indicator used throughout this project),
   `random_state=42` (this project's standing convention for reproducible splits).
2. For each fold `f` (1..5), for each of the 5 primary models, and for each candidate `N0`:
   - **Fit** `q_joint`, `q_envelope`, and the resulting `q_M4b(N0)` using the OTHER 4 folds
     (~801-802 calibration points) — this mirrors exactly how the real calibration set is used
     to fit these quantiles in the deployed pipeline, just on a 4/5 subset.
   - **Evaluate**, on the held-out 1/5 fold (~200 points, disjoint from the fitting portion, and
     never overlapping the locked test set at any point): (a) intersectional coverage on the
     joint-cell members within this held-out fold, and (b) marginal drift, defined identically
     to the project's existing convention (`marg_drift_pp = (overall coverage under the blended
     per-participant threshold) - (overall coverage under the M1 global threshold)`, both
     computed on the same held-out fold).
3. Average across the 5 folds to get, per (model, N0): `CV_coverage(model, N0)` and
   `CV_drift(model, N0)`.
4. **Primary selection rule:** choose the **smallest** N0 in the grid such that, **simultaneously
   for all 5 models**, `CV_coverage >= 0.90` AND `|CV_drift| <= 5.0` percentage points. Smallest
   is preferred because a smaller N0 gives more weight to the actual joint-cell quantile
   (`w = N_joint_cal/(N_joint_cal+N0)` is larger for smaller N0), which is the more scientifically
   motivated default when the data support it.
5. **Fallback rule, defined now, before any results are seen:** if no single N0 in the grid
   satisfies the criterion in step 4 for all 5 models simultaneously, select the N0 minimizing
   `max over models of [ max(0, 0.90 - CV_coverage) + max(0, |CV_drift| - 5.0)/5.0 ]` — a
   normalized worst-case penalty combining coverage shortfall and excess drift. This fallback, if
   triggered, will be reported as such, not silently treated as a clean pass.
6. The selected `N0*` is then used **exactly once** to fit `q_joint`, `q_envelope`, and
   `q_M4b(N0*)` on the **full** N=1,002 calibration set (no folds), and evaluated **exactly once**
   on the locked test set (N=2,146) for final reporting. No further N0 values are tried against
   the test set after this point.

## What this protocol explicitly forbids

- Evaluating any candidate N0's coverage or drift against the locked test set before step 6.
- Changing the candidate grid, the fold count, the stratification variable, the selection
  criterion, or the fallback rule after seeing any cross-validated result.
- Selecting a different "smallest N0" than the one the rule in step 4 (or the fallback in step 5)
  actually produces.
