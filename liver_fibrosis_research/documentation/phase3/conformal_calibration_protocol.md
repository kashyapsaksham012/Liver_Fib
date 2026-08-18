# Conformal Calibration Protocol

**Generated:** 2026-08-18 (Phase 3 Closure Verification, Item 2) — committed before any conformal
prediction code is run.

## The gap this resolves

`documentation/phase2/uncertainty_protocol.md` froze the METHOD ("Split Conformal Prediction," not
CV+ — chosen explicitly over ensembles/MC-dropout) but explicitly deferred the exact calibration-set
proportion: *"reserve a further split (e.g. 80% proper-train / 20% conformal calibration, exact
proportion to be fixed in Phase 3 alongside the random seed)."* Phase 3 execution was scoped to
baseline discrimination only and never actually carved out this partition. Until now, only two
partitions existed (train N=5,007, locked test N=2,146) — no data was reserved for conformal
calibration, meaning either the locked test set would have to be misused for calibration (which
would invalidate every frozen Phase 3 discrimination result) or the calibration step would have to
be improvised under time pressure at Uncertainty-phase start. This document closes that gap now.

## Decision: Option A — held-out calibration split

**Option A was selected, not Option B (CV+),** because Phase 2 named "Split Conformal Prediction"
specifically as the frozen method. CV+ is a related but methodologically distinct variant (Barber,
Candès, Ramdas & Tibshirani, "Predictive inference with the jackknife+", *Annals of Statistics*,
2021, and its extension to K-fold CV+) with different theoretical guarantees and a different
calibration mechanism; adopting it here would silently substitute a different frozen method rather
than implement the one Phase 2 actually chose. That substitution is exactly the kind of undisciplined
protocol drift this project's audit process exists to prevent.

## Exact partition (generated, not merely planned)

Carved from the existing 70% training partition ONLY (`data/processed/splits/train_ids.csv`,
N=5,007) — **the locked test set (N=2,146) was never touched, opened, or referenced by this
script.** 80/20 split, stratified on the primary outcome, seed=42 (matching the "e.g. 80/20"
example Phase 2 itself proposed — not a deviation).

| Partition | File | N | Outcome-positive | Prevalence |
|---|---|---|---|---|
| Proper-train | `data/processed/splits/proper_train_ids.csv` | 4,005 | 373 | 9.31% |
| Conformal calibration | `data/processed/splits/conformal_calibration_ids.csv` | 1,002 | 93 | 9.28% |

N=1,002 (93 positive) falls within the commonly-cited "several hundred to low thousands" range for
stable split-conformal quantile estimation at 90% target coverage; it is on the smaller side for
*subgroup*-conditional coverage precision (per `uncertainty_protocol.md`'s own documented
limitation: "the calibration-set size directly limits achievable coverage precision for smaller
subgroups") — this is a known, pre-acknowledged limitation, not a new one introduced here.

Integrity, verified programmatically (`src/phase3_21_reserve_conformal_calibration_split.py`):
proper-train ∩ calibration = ∅; proper-train ∪ calibration = the original training partition
exactly; both ∩ locked test set = ∅.

## Critical implementation note for the Uncertainty phase (read before writing any conformal code)

**The 5 baseline models frozen in Phase 3 (`models/phase3/model_<name>_v1.joblib`) were fit on the
FULL training partition (N=5,007), which includes the 1,002 rows now reserved for conformal
calibration.** Those specific model artifacts are therefore **not valid to reuse directly** as the
score-producing models for split conformal prediction — split conformal requires the calibration
set to be unseen by the model that produces its non-conformity scores; reusing a model that was
partly fit on its own calibration data would invalidate the coverage guarantee.

**Required action at Uncertainty-phase start:** refit each of the 5 model families on
`proper_train_ids.csv` only (N=4,005), using the exact hyperparameters already selected via CV in
Phase 3 (`results/tables/phase3_model_registry.csv`, `best_hyperparameters` column) — no new
hyperparameter search. Save these as new, separately-versioned artifacts (e.g.
`models/uncertainty/model_<name>_conformal_v1.joblib`), distinct from and never overwriting the
Phase 3 discrimination-baseline artifacts.

**This does NOT reopen or invalidate any frozen Phase 3 discrimination result.** The Phase 3
baseline results (`results/tables/phase3_final_baseline_results.csv`) remain exactly as reported —
they answer "how well does a model fit on the full 5,007-row training partition discriminate on the
locked test set," a complete and valid question in its own right. The conformal-specific refit
answers a different, additional question ("what is this model's calibrated uncertainty"), which
requires its own model instance by conformal prediction's own methodological requirements — this is
not a weakness of the Phase 3 result, it is an inherent property of how split conformal prediction
works.

## Confirmation

This amendment does not touch the locked Phase 3 test set in any way (verified: the script that
generated the split reads only `train_ids.csv`; `test_ids.csv` is loaded solely to assert zero
overlap, never for splitting). Logged here as a formal protocol amendment, in the same honest style
as the Phase 3 amendments (Youden's J, bootstrap/FDR) — this proportion was NOT specified by Phase 2
beyond its own "e.g." example; Phase 2 explicitly deferred the exact figure, and this document is
where it is finally fixed.
