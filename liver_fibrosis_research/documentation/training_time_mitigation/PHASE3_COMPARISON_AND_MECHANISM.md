# Phase 3 — comparison & mechanism (Amendment #19)

**2026-08-27.** From `src/ttm_06_comparison.py`
(`comparison_vs_battery.csv`, `mechanism_comparison.csv`, `cost_accounting.csv`) and the Phase-2
locked-test outputs.

## 3.1 The training-time intervention vs the full mitigation battery

| Method | Obese−Normal sens gap | BMI-Obese conformal cov | Age-60+ conformal cov | Overall cost | Disposition |
|---|---|---|---|---|---|
| **Frozen baseline** | +27 to +48 pp (5/5 sig) | 0.77–0.82 | 0.81–0.86 | — | — |
| Subgroup Youden thresholds (exploratory) | halved | n/a | n/a | age gap +26–133 %; ~40 pp specificity | EXPLORATORY |
| Subgroup calibration | unchanged | unchanged | unchanged | — | NO ACCEPTABLE MITIGATION |
| Mondrian conformal (Phase 7) | n/a | ≥ 0.88 for 5/9 | partial | XGBoost +5.3 pp marginal breach | PARTIALLY EFFECTIVE |
| Mondrian re-run (Amdt #17, 3d) | n/a | ≥ 0.88 for 5/5 | ≥ 0.88 for 5/5 | retained marginal 0.94–0.95 (over-covers) | PARTIALLY EFFECTIVE |
| Equalized-odds post-processing (exploratory) | ~ 0 | n/a | n/a | ~40 pp specificity; ~399 excess FP/1,000 | EXPLORATORY (unacceptable) |
| XGBoost retuning | n/a | no breach removed w/o cost | n/a | 11–22 pp sensitivity | NO ACCEPTABLE RETUNING |
| Joint intersectional conformal (exploratory) | n/a | n/a | n/a | XGB/LGBM marginal breach | EXPLORATORY |
| Selective deferral (Amdt #17) | n/a | *lowered* | *lowered* | — | NO IMPROVEMENT |
| **Training-time reweighing, BMI (Amdt #19, Arm A)** | **+14 to +17 pp; 0/4 sig — halved** | **0.857–0.871 (near, not at, 0.88)** | 0.80–0.84 (~unchanged) | **AUROC −0.02 to −0.03; specificity −0.7 to −12 pp; new LR sex disparity** | **NEGATIVE (no efficacy)** — gate not met |
| Training-time reweighing, BMI×age (Arm B) | +17 to +20 pp — halved | 0.839–0.846 | **worsened, 3/4 newly sig** | specificity −6 to −15 pp | NEGATIVE (no efficacy) |

**Reading:** every *post-hoc* method either did nothing to the sensitivity gap or traded one
subgroup for another; the *training-time* intervention (Arm A) is the **first** to move both
primary subgroup metrics substantially in the right direction *and* remove the mechanism — but not
to the pre-registered standard, and not without an overall-performance cost the gate rejects.

## 3.2 Mechanism — did it fix the score ordering or just the threshold?

From `mechanism_comparison.csv` (OOF, computed before the test touch):

| Arm A model | within-Normal-BMI OOF AUROC Δ | score-separation Δ | shortcut coef (base → reweighted) | interpretation |
|---|---:|---:|---|---|
| logistic | +0.012 | +0.067 | 0.249 → 0.036 | score ordering improved |
| random forest | +0.013 | +0.049 | 0.184 → 0.008 | score ordering improved |
| xgboost | +0.008 | +0.059 | 0.222 → 0.012 | ordering ~flat, shortcut removed |
| lightgbm | +0.016 | +0.050 | 0.212 → 0.008 | score ordering improved |

The reweighting **does** change the within-subgroup score ordering, not only where the threshold
falls: Normal-BMI positive-vs-negative OOF AUROC rises for 3 of 4 families and the separation
between Normal-BMI positive and negative scores widens for all 4. The matched-stiffness BMI
coefficient (the Amendment #18 C4 quantity) collapses from ~0.2 to ~0.01 — the models no longer
assign obese participants a higher score at equal liver stiffness. This **confirms the Amendment
#17 hypothesis**: the residual failure is a within-subgroup score-ordering problem, and it is
addressable at training time.

Arm B: within-Normal-BMI OOF AUROC *decreases* for all 4 families and the shortcut coefficient
only partially shrinks (to 0.05–0.09) — the 12 BMI×age cells (4 of them below 10 positives, using
the Arm-A fallback weight) are too sparse to fit against.

## 3.3 Cost accounting (Arm A)

| model | Δ AUROC | Δ sensitivity | Δ specificity | Δ Brier (recal) | wrong-direction subgroups |
|---|---:|---:|---:|---:|---|
| logistic | −0.033 | +0.060 | **−0.122** | +0.003 | Female (newly BH-sig, −15.1 pp) |
| random forest | −0.022 | +0.015 | −0.077 | +0.003 | — |
| xgboost | −0.025 | −0.025 | −0.007 | +0.004 | — |
| lightgbm | −0.027 | −0.015 | −0.058 | +0.003 | — |

The cost is a **discrimination and specificity trade** — the reweighted models refer more of the
population (lower specificity) to raise sensitivity in the under-detected subgroup. For logistic
regression this also surfaces a sex disparity that was not significant at baseline. Calibration is
barely affected (Brier +0.003–0.004). XGBoost carries the smallest cost (specificity −0.7 pp) and
the best coverage recovery (BMI-Obese 0.871).

## 3.4 What this means

The body-mass reliability–fairness failure is **addressable at training time in mechanism** — a
subgroup-balancing objective removes the BMI shortcut and halves the sensitivity gap — but within
the ten routine predictors and this sample it **cannot be eliminated to an acceptable standard
without a discrimination/specificity cost the pre-registered gate rejects**, and a single
objective cannot fix the BMI and age problems together (Arm B worsens age). The remaining paths
are: more normal-weight fibrosis cases (the binding data limit — 50 training / 22 test), richer
features that separate lean fibrosis, or a deployment that explicitly accepts and monitors a
quantified performance–equity trade. This sharpens the manuscript's open "training-time
intervention is the indicated next step" into a concrete, bounded result.
