# Amendment #19 — closure

**Date:** 2026-08-27 · **Status:** COMPLETE · **Verdict:** **NEGATIVE (no efficacy)** by the
pre-registered gate — Arm A (primary) is the study verdict.
**Governing plan:** `TRAINING_TIME_MITIGATION_PLAN.md` · **Amendment text:** `AMENDMENT_19_TEXT.md`
· **Pre-execution snapshot:** `PRE_EXECUTION_SNAPSHOT.md` (git HEAD
`16459ae3a958da858917e9b26e050d5ad4106301`).

## What ran

One training-time intervention: retrain the frozen model families with Kamiran–Calders instance
reweighting so that body-mass band is independent of the outcome in the reweighted **training /
proper-train** distribution (conformal-calibration and locked test never weighted). Frozen
predictors, outcome (`LUXSMED ≥ 8.2 kPa`), splits, seed (42), CV design, preprocessing, base
class-imbalance handling, and Phase-3 `best_params` (extracted live from
`models/phase3/model_{name}_v1.joblib`). **Arm A** = 4 BMI bands (primary); **Arm B** = 12 BMI×age
cells (secondary; cells < 10 positives use the Arm-A weight).

Scripts `src/ttm_00`…`ttm_06`. Environment: the exact `requirements-phase3-lock.txt` pins
(scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0, imbalanced-learn 0.14.2, joblib 1.5.3,
pandas 3.0.5, numpy 2.5.2, scipy 1.18.0), installed in an isolated virtual environment.

**MLP excluded.** The perceptron has no `sample_weight`; the resampling approximation
(§0.3.2) was unstable across seeds for Arm B (3-seed OOF AUROC SD 0.0116 > 0.01), so per the
pre-registration `MLP_FALLBACK=1` was set: MLP reported "not applicable in the frozen
implementation", **four** families evaluated, and the gate's "≥ 4/5" thresholds relaxed to "≥ 3/4".

## Locked-test touches

Two, one per evaluation script:

| Script | UTC | Nature |
|---|---|---|
| `src/ttm_03_test_classification.py` | 2026-08-27T15:09:13Z | score the locked test with the reweighted final models; discrimination, calibration (raw + OOF-Platt), subgroup sensitivity + bootstrap CIs + BH-FDR |
| `src/ttm_04_test_conformal.py` | 2026-08-27T15:09:48Z | prediction sets from the reweighted proper-train models + per-arm conformal thresholds; marginal + subgroup + intersectional coverage, Wilson CIs, BH-FDR |

Leakage check = 0 on both (`test ∩ {train, proper-train, calibration}`), recorded in
`test_touch{1,2}_manifest.json` and in `documentation/phase3/test_set_lock.md`.

## Result

### Gate (mechanical, `src/ttm_05_apply_gate.py`)

| | G1 sens | G2 cov | G3 marginal | G4 AUROC | G5 Brier | G6 no-harm | G7 overall | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Arm A** | FAIL 1/4 | FAIL 0/4 | PASS | FAIL 0/4 | PASS | FAIL (LR Female) | FAIL | **NEGATIVE (no efficacy)** |
| Arm B | FAIL 0/4 | FAIL 0/4 | PASS | FAIL 0/4 | PASS | FAIL (age gap) | FAIL | NEGATIVE (no efficacy) |

### The substance (Arm A, primary)

**Moved the mechanism** (OOF, pre-touch): matched-stiffness BMI coefficient (Amendment #18 C4)
collapsed 0.18–0.25 → 0.008–0.036 (4/4); within-normal-weight OOF AUROC rose for 3/4;
Normal-BMI positive-vs-negative score separation widened for 4/4.

**Moved both primary subgroup metrics** (locked test): normal-weight-vs-obese sensitivity gap
**halved**, +27 to +48 pp (BH-sig 5/5) → +14 to +17 pp (BH-sig **0/4**); BMI-obese conformal
coverage 0.77–0.82 → **0.857–0.871** (Wilson LB 0.833–0.847; still < 0.88). Age-60+ conformal
coverage ~unchanged (0.80–0.84). Marginal coverage on target (0.893–0.898).

**Cost that failed the gate:** test AUROC −0.022 to −0.033 (4/4 exceed the −0.02 tolerance);
overall specificity −0.7 to −12.2 pp; logistic regression acquired a newly BH-significant Female
sensitivity disparity (−15.1 pp, q = 0.012). Recalibrated Brier barely moved (+0.003–0.004).

**Arm B** reduced the body-mass gap similarly but **worsened the age-60+ sensitivity gap**
(BH-significant in 3/4 models, was 0/4) and cost more specificity — the two-mechanism failure
confirmed: one objective cannot repair both.

## Interpretation

The body-mass reliability–fairness failure is **addressable at training time in mechanism** — a
subgroup-balancing objective removes the body-mass shortcut and halves the sensitivity gap — but
within the ten routine predictors and this sample it **cannot be eliminated to an acceptable
standard without a discrimination/specificity cost the pre-registered gate rejects**, and a single
objective cannot fix the body-mass and age problems together. This sharpens the manuscript's
prior open "a training-time intervention is the indicated next step" into a concrete bounded
result: the remaining options are more normal-weight fibrosis cases (the binding data limit — 50
training / 22 test), richer features that separate lean fibrosis, or a deployment that explicitly
accepts and monitors a quantified performance–equity trade.

## New hypothesis tests / multiplicity

`ttm_03` subgroup-sensitivity BH families (per arm × model × dimension) and `ttm_04` coverage BH
families (per arm × model × dimension) are corrected within themselves. Consistent with Amendments
#16 and #18, these post-freeze tests are **not** folded into the frozen project-wide 182-test
pooled-FDR family.

## Reproducibility

`tests/test_training_time_mitigation.py` — 52/52 (leakage; weight-is-a-function-of-key; the
conformal-calibration and test sets carry no weight; count identities; **all 16 reweighted model
artefacts carry the exact frozen Phase-3 `best_params`**; exactly 2 touch manifests, both
leakage-0). Seed 42 throughout. The isolated venv used for execution is not committed; the pins
are in `requirements-phase3-lock.txt`.

## Registers updated

`FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` (+MIT-07), `FINAL_SCIENTIFIC_FINDINGS.md` §7/§11/§14,
`FINAL_RESEARCH_AUDIT.md` §7, `DO_NOT_CLAIM.md`, `RESEARCH_WEAKNESSES.md` W2,
`RESEARCH_STRENGTHS.md` #7, `FINAL_LIMITATIONS_REGISTER.md` (D1 + new D5),
`EXPLORATORY_RESULTS.md` (E13 — completeness note), `MANUSCRIPT_FRAMING_GUIDANCE.md` §5b,
`documentation/manuscript/RESULTS_VERIFICATION.md` (Amendment #19 addendum),
`protocol_amendment_registry.md` row 19, `test_set_lock.md`, `START_HERE.md` §7,
`documentation/manuscript/README.md` → v5. Manuscript → **v5** (§2.8, §3.7b, Table 4, §4/§4.1, §5,
§6, abstract, Appendix A).
