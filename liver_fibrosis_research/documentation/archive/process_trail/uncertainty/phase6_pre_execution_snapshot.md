# Phase 6 (Uncertainty) — Pre-Execution Snapshot

**Timestamp (live):** 2026-08-19 14:09:37 +0530

## Phase 5 closure dependency status (checked before any Phase 6 execution)

`PHASE5_CLOSURE_VERIFICATION_REPORT.md` **does not exist** in this repository (live-checked via
`ls`/`find`, both returned no match). Only `PHASE5_FAIRNESS_RESULTS_REPORT.md` exists — Phase 5's
own final results report, produced at the end of the Phase 5 execution task. Unlike Phase 4,
Phase 5 was never given a separate, dedicated "closure" pass.

Substantively, the three items this task asks about were addressed **within**
`PHASE5_FAIRNESS_RESULTS_REPORT.md` itself (not in a separate closure document):
1. **BMI headline N/positive-count context** — addressed in §10/§18 of that report (BMI
   Underweight's N=1 positive explicitly flagged as non-interpretable; Normal BMI's
   limited-precision tier stated; Obese's primary-feasibility tier stated).
2. **Calibration-gradient mechanical-confound interpretation** — addressed in §14 (both absolute
   and relative overprediction framings reported, with the mechanical/mathematical explanation
   for why they point in opposite directions, and an explicit "observational, does not establish
   causality" caveat).
3. **Deferred-sensitivity-analysis forward tracking** — addressed in §21–22 (the 4 unexecuted
   Phase-2 sensitivity analyses are named individually and carried forward as a documented
   limitation).

**Per this task's explicit instruction, Phase 6 technical execution proceeds** (the core
conformal analysis is methodologically distinct from Fairness), but this status is recorded
here and will be restated in the final Phase 6 report: **Phase 5 was NOT formally,
administratively closed via a dedicated closure-verification document.** This task does not
attempt to create one — that would be out of scope for Phase 6.

## Git state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `b028097335201b07ac0faf514416ffbb42ff2504` |
| Working tree | Clean (0 uncommitted, 0 untracked) |
| Upstream | `origin/main`, up to date |

## Frozen protocol hash

`documentation/phase2/uncertainty_protocol.md` SHA-256:
`9983ad3c1604c2a2f43ecfc6afcf876d0ef8a5acc17ff0b9923011323869f7d7`

## Phase 3 model hashes (unchanged, read-only reference — Phase 6 does not touch these)

| Model | SHA-256 |
|---|---|
| Logistic | `ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5` |
| Random Forest | `37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a` |
| XGBoost | `8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4` |
| LightGBM | `dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02` |
| MLP | `4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc` |

## Phase 4/5 result hashes (unchanged, read-only reference)

Confirmed present and unmodified: `results/calibration/test_set_calibration_final.csv`,
`results/fairness/fairness_inference.csv` — not re-hashed here since Phase 6 does not depend on
their content directly (only on the shared frozen partitions and frozen thresholds below).

## Data-partition files (live-verified)

| File | SHA-256 | Rows (incl. header) | N |
|---|---|---|---|
| `proper_train_ids.csv` | `bc29dbe6402ffb82790801a97d6baf26732f6964bf77741a8f716e78dab01fef` | 4,006 | 4,005 |
| `conformal_calibration_ids.csv` | `4d696cbcd0f2aecfd07dd7b223825df10c39bbfaf3f093a117e4c224b6c5b3c5` | 1,003 | 1,002 |
| `test_ids.csv` | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` | 2,147 | 2,146 |

Test-set hash matches the human-verified value exactly (researcher-reported PASS, transcribed in
`documentation/end_to_end/human_spot_check_record_template.md` during the Phase 5 pre-work pass).

## Environment

Python 3.14.3, scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0 — unchanged from Phase 4/5
(matches `requirements-phase3-lock.txt`).

## Frozen uncertainty protocol — extracted decisions (read live in full this pass)

From `documentation/phase2/uncertainty_protocol.md`:

1. **Method:** Split Conformal Prediction.
2. **Target coverage:** 90% nominal.
3. **Nonconformity score:** `1 − P̂(y = true class | x)` — the standard split-conformal binary
   classification score, computed from each refit model's predicted probability.
4. **Calibration architecture:** proper-train (4,005) / conformal-calibration (1,002) split,
   disjoint from both model-fitting data and the locked test set — exact proportion (80/20) was
   fixed during the Phase 3 closure-verification pass (Amendment #4), not in this task.
5. **Final test-set role:** empirical coverage evaluation (proportion of true labels contained
   in their prediction set vs. the 90% target).
6. **Primary uncertainty metric:** empirical marginal coverage.
7. **Efficiency metric:** average prediction-set size (discrete, since this is binary
   classification with 2 candidate labels — the "continuous risk-score interval" variant named
   in the protocol does not apply here).
8. **Subgroup coverage:** explicitly authorized and explicitly **required** — "must not be
   skipped or treated as secondary" — using Phase 5's exact frozen subgroup definitions (sex,
   race/ethnicity, age, BMI).
9. **Statistical inference:** **not specified** in this document — a genuine gap, to be resolved
   as a logged, dated protocol amendment (consistent with how Phase 4/5 handled undefined
   inference choices), not silently invented.
10. **Multiple-comparison strategy:** **not specified** — same gap; Phase 6 will define its own
    family if formal comparisons are performed, per this task's Part 19, logged as an amendment.
11. **Prediction-set construction variant:** the document's own conformity-score formula (`1 −
    P̂(y=true|x)`) IS the "standard" (non-APS) split-conformal score — this pins the variant
    despite a separate sentence saying "the exact variant... to be fixed in Phase 3" (which was
    never actually done in Phase 3, since Phase 3 never implemented any conformal code). Read as:
    the score formula is the specification; "standard" is used here, not APS. Not treated as a
    contradiction requiring a STOP, since the formula itself is unambiguous and directly
    implementable.
12. **Sensitivity analyses:** not specified for Phase 6 specifically; the general Phase 2
    sensitivity-analysis-plan items are addressed under §21 (deferred-analysis tracking) per
    this task's Part 21.

## Conformal-valid refit requirement (why it's needed, confirmed)

The original Phase 3 models were fit on the full 5,007-row training partition, which includes
the 1,002 rows now reserved as `conformal_calibration_ids.csv`. Using those same models' outputs
as conformal calibration scores would violate the calibration set's required independence from
model-fitting data. A refit on `proper_train_ids.csv` only is therefore mandatory before any
conformal calibration step, exactly as this task's Part 5 specifies.
