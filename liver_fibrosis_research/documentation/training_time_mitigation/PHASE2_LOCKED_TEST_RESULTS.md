# Phase 2 — locked-test results (Amendment #19)

**Executed 2026-08-27.** Two locked-test touches:
`src/ttm_03_test_classification.py` (2026-08-27T15:09:13Z) and
`src/ttm_04_test_conformal.py` (2026-08-27T15:09:48Z). Leakage checks = 0 on both
(`test ∩ {train, proper-train, calibration}`). `MLP_FALLBACK=1` (see Phase 1); **four
`sample_weight`-capable families** evaluated; gate thresholds "≥ 4/5" → "≥ 3/4" per the
pre-registration.

## Gate (pre-registered §0.3.6), applied mechanically by `src/ttm_05_apply_gate.py`

| Gate | Arm A | Arm B |
|---|---|---|
| G1 — sensitivity efficacy (\|gap\| cut ≥ 50 % **and** residual < 15 pp, ≥ 3/4) | **FAIL** (1/4) | **FAIL** (0/4) |
| G2 — coverage efficacy (BMI-Obese ≥ 0.88, LB ≥ 0.85 **and** Age-60+ ≥ 0.88, ≥ 3/4) | **FAIL** (0/4) | **FAIL** (0/4) |
| G3 — marginal coverage ∈ [0.87, 0.93] (4/4) | PASS | PASS |
| G4 — test AUROC within −0.02 (≥ 3/4) | **FAIL** (0/4) | **FAIL** (0/4) |
| G5 — recalibrated Brier within +0.01 (≥ 3/4) | PASS | PASS |
| G6 — no other-subgroup harm (age gap not worse > 5 pp; no new sex/race BH-sig) | **FAIL** (1 new: LR Female) | **FAIL** (age gap worse + 1 new) |
| G7 — overall sens & spec within 5 pp (≥ 3/4) | **FAIL** | **FAIL** |

### VERDICT: **NEGATIVE (no efficacy)** — both arms. Arm A (primary) is the study verdict.

The gate returns "no efficacy" because neither efficacy gate crosses its (deliberately strict)
threshold — the gate required the gap essentially *closed* (≥ 50 % reduction **and** < 15 pp
residual) and coverage *restored* to ≥ 0.88. The intervention delivered a **halving** of the gap
and coverage *near* target — real movement, short of the bar — while also failing the cost gates.

---

## What the intervention did — Arm A (BMI reweighing, primary; 4 families)

| Metric | Frozen baseline | Arm A | Change |
|---|---|---|---|
| Normal-vs-Obese sensitivity disparity | +27 to +48 pp; **BH-sig 5/5** | **+13.7 to +16.8 pp; BH-sig 0/4** (q 0.14–0.28) | gap **halved**, no longer significant; Normal-BMI reference sensitivity ~0.41–0.64 → **0.68–0.73** |
| BMI-shortcut coefficient (matched-stiffness OLS, OOF) | 0.18–0.25 | **0.008–0.036** | **collapsed** — the models stopped using body mass as a risk cue |
| BMI-Obese **conformal coverage** | 0.768–0.823 (BH-sig 5/5) | **0.857–0.871** (Wilson LB 0.833–0.847; BH-sig 4/4) | +0.03 to +0.10; **most of the way to nominal, still short of 0.88** |
| Age-60+ conformal coverage | 0.811–0.856 | 0.803–0.842 | ~unchanged (logistic −0.046) — the intervention does **not** address the age shortfall |
| Obese ∩ 60+ intersection coverage | 0.65–0.75 | 0.70–0.83 (RF/XGB/LGBM 0.81–0.83) | improved, still short |
| Marginal conformal coverage | 0.881–0.908 | **0.893–0.898** | on target |

## What it cost — Arm A

| Cost | Magnitude |
|---|---|
| Test AUROC | **−0.022 to −0.033** (logistic worst) — all 4 exceed the −0.02 tolerance |
| Overall specificity | **−0.7 to −12.2 pp** (logistic −12.2, RF −7.7, LightGBM −5.8, XGBoost −0.7) |
| Overall sensitivity | −2.5 to +6.0 pp (mixed) |
| Recalibrated Brier | +0.003 to +0.004 (small) |
| New subgroup disparity | **Logistic: Female sensitivity −15.1 pp vs Male (BH q = 0.012), newly significant** — a levelling-shift side effect (LR only) |

## Arm B (BMI × age reweighing, secondary) — worse on every axis

- BMI disparity halved similarly (+17 to +20 pp) but **the Age-60+ sensitivity gap WORSENED and became
  BH-significant for random forest, XGBoost, and LightGBM** (−10.8 to −17.2 pp; was −8 to −14, 0/4
  significant → 3/4). This is the two-mechanism failure: forcing BMI×age independence trades the
  BMI gap for the age gap.
- Larger specificity cost (−6 to −15 pp). BMI-Obese coverage lower than Arm A (0.839–0.846).
- Phase-1 diagnostic already showed Arm B **reduces** within-Normal-BMI OOF AUROC (−0.0003 to −0.012)
  — the small BMI×age cells hurt the fit.

## Reproducibility

`models/training_time_mitigation/*.joblib` (16 artefacts) all carry the exact frozen Phase-3
`best_params` (test T16, 16/16 pass). Environment: `requirements-phase3-lock.txt` (scikit-learn
1.9.0, xgboost 3.4.1, lightgbm 4.7.0, imbalanced-learn 0.14.2). Seed 42 throughout. The two
touch manifests record the leakage checks and timestamps.
