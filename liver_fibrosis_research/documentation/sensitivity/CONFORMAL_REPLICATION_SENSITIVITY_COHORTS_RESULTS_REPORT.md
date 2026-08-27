# Conformal Subgroup-Coverage Replication on the Sensitivity Cohorts — Results Report

**Analysis:** replication of the primary study's split-conformal subgroup-coverage finding
(Phase 6) on the sensitivity cohorts. **Protocol Amendment #16.**
**Date:** 2026-08-27.
**Script:** `src/sens_14_conformal_replication_sensitivity_cohorts.py` (mirrors
`src/phase6_02..04`).
**Outputs:** `results/sensitivity/conformal_replication_{marginal,subgroup,thresholds}.csv`,
`conformal_replication_lineage.json`.

---

## 1. Motivation

The subgroup conformal-coverage failure (BMI-Obese and Age-60+ under-cover while marginal coverage
meets target) was the one primary finding measured on **CAND_1 only**. Amendment #13 executed
discrimination / calibration / fairness for CAND_2 and CAND_3 but explicitly **deferred** the
conformal replication. This analysis closes that gap. Combined with the already-executed 8.0-kPa
conformal pass, the finding is now checked across four independent cohort/threshold constructions.

## 2. Method (frozen framework, unchanged)

Per cohort: fresh 70/30 stratified split (seed 42, identical to `sens_02`); 80/20 stratified split
(seed 42) of the training partition → proper-train / conformal-calibration (Phase 6 design); refit
the 5 model families on proper-train only with the **frozen Phase 3 `best_params`** (no
hyperparameter search); CAND_3 keeps its 12-predictor fasting-extended architecture. Nonconformity
score `1 − P(true class | x)`; threshold = k-th smallest calibration score,
`k = ⌈(n_cal+1)(1−α)⌉`, α = 0.10. Prediction sets on the cohort's own locked test; Wilson 95% CIs;
one-sample binomial test vs 0.90; BH-FDR within each (model × dimension) family. **The CAND_1
Phase 3/6 test set is never loaded.** Pre-specified targets: **BMI-Obese** and **Age-60+**.

Partition sizes: CAND_2 — proper-train 4,277 / calibration 1,070 / test 2,292 (241 positive,
10.5%). CAND_3 — proper-train 2,005 / calibration 502 / test 1,075 (96 positive, 8.9%).

## 3. Marginal coverage — meets target on both cohorts

| Cohort | Empirical coverage range (5 models) |
|---|---|
| CAND_1 (primary) | 0.881–0.908 |
| 8.0 kPa (existing) | 0.891–0.906 |
| **CAND_2 (new)** | **0.896–0.906** |
| **CAND_3 (new)** | **0.899–0.917** |

## 4. Subgroup coverage — the CAND_1 pattern replicates

Empirical coverage, 5 models, α = 0.10 (target 0.90):

| Subgroup | CAND_1 | 8.0 kPa | **CAND_2** | **CAND_3** |
|---|---|---|---|---|
| **BMI-Obese** (target) | 0.768–0.823 | 0.790–0.822 | **0.790–0.841** | **0.799–0.838** |
| **Age-60+** (target) | 0.811–0.856 | 0.835–0.850 | **0.823–0.871** | **0.850–0.882** |
| BMI-Normal | 0.96–0.97 (over) | 0.96–0.97 (over) | 0.956–0.977 (over) | 0.956–0.963 (over) |
| BMI-Overweight | over | over | 0.954–0.974 (over) | 0.952–0.982 (over) |
| Age 18–39 | over | over | 0.942–0.959 (over) | 0.939–0.950 (over) |
| Age 40–59 | ≈ target | ≈ target | 0.890–0.910 | 0.909–0.926 |

**BMI-Obese under-coverage:** CI excludes 0.90 for **all 5 models on both new cohorts** (10/10);
FDR-significant in **5/5 on CAND_2** and **5/5 on CAND_3** (`bh_fdr_adjusted_p` ≤ 2.4×10⁻⁴).

**Age-60+ under-coverage:** direction (under-covers) holds for **all 5 models on both cohorts**;
CI excludes 0.90 in **5/5 on CAND_2** and **3/5 on CAND_3** (logistic, MLP); FDR-significant in
**5/5 on CAND_2** and **2/5 on CAND_3** (random forest, XGBoost, LightGBM lose significance on
CAND_3, where the Age-60+ cell has only ~34 test positives).

## 5. Verdict

| Finding | Status across CAND_1 / 8.0 kPa / CAND_2 / CAND_3 |
|---|---|
| Marginal coverage meets target | **ROBUST** (4/4 constructions) |
| Marginal coverage conceals subgroup under-coverage | **ROBUST** (4/4) |
| **BMI-Obese under-coverage** | **ROBUST** — CI excludes 0.90 for every model in every construction; FDR-significant throughout |
| **Age-60+ under-coverage** | **DIRECTION ROBUST, significance specification-/power-sensitive** — under-covers everywhere; FDR-significant in CAND_1, 8.0 kPa, CAND_2; drops to 2/5 in the smaller CAND_3 |
| BMI-Normal / Overweight / Age-18–39 over-cover (compensating inefficiency) | **ROBUST** (4/4) |

The single previously un-triangulated primary finding is now triangulated. The
marginal-vs-subgroup coverage contrast — and specifically the **BMI-Obese** under-coverage — is a
robust property of this modelling setup, not an artifact of the CAND_1 cohort construction or the
8.2-kPa threshold. The **Age-60+** conformal under-coverage tracks the same pattern as the Age-60+
*sensitivity* disparity: consistent direction, sample-size-sensitive significance.

## 6. Scope and limitations

- Frozen framework, frozen hyperparameters, cohorts already constructed and validated
  (Amendment #13). This is a **robustness check**, not a new primary result, and does not change
  the primary CAND_1 conformal numbers.
- No FDR pooling across cohorts (each cohort is its own family).
- CAND_3's small Age-60+ cell (~34 positives) limits power for that subgroup specifically.
- Fresh split (seed 42) rather than a persisted split-ID file, matching `sens_02`.
- Still within NHANES 2017–March 2020; not external validation.
