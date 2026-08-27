# FINAL SCIENTIFIC FINDINGS

Read-only audit, 2026-08-27. Verdict scale: **CONFIRMED** · **SUPPORTED WITH LIMITATIONS** ·
**EXPLORATORY** · **INCONCLUSIVE** · **NOT SUPPORTED**. Evidence is the raw artifact plus the
consistent consolidation layer.

---

## 1. Discrimination — **CONFIRMED**

Five model families (LR, RF, XGBoost, LightGBM, MLP) achieve comparable, modest-to-strong
discrimination for `LUXSMED ≥ 8.2 kPa` from ten routine predictors: test AUROC 0.8229–0.8429,
PR-AUC ≈0.35–0.37; 0/10 pairwise comparisons FDR-significant.
`results/tables/phase3_final_baseline_results.csv`, `phase3_model_comparison_fdr.csv`.
XGBoost has the highest point estimate but **no** significant superiority (**NOT SUPPORTED**:
"XGBoost is the best model").

## 2. Calibration — **CONFIRMED**

Class-balancing (`class_weight='balanced'` / `scale_pos_weight`) causes severe raw
over-prediction (OOF intercepts −2.24 to −1.86; MLP, unweighted, −0.28); OOF-fit Platt scaling
applied once to the locked test restores aggregate calibration (test ECE → 0.011–0.026, Brier
→ 0.069–0.072, intercepts → −0.15…+0.14) with **AUROC unchanged**.
`results/calibration/primary_metrics_by_model.csv`, `test_set_calibration_final.csv`.
**NOT SUPPORTED:** subgroup-level or universal calibration adequacy (see finding 5).

## 3. BMI fairness — **CONFIRMED** (see §11 for the consolidated BMI assessment)

Normal-BMI sensitivity is 27.1–47.7 pp lower than Obese in all 5 models, FDR-significant
(q ≤ 0.006); independently reproduced; stable across all three sensitivity cohorts (15/15).
`results/fairness/fairness_inference.csv`,
`results/fairness_bmi_investigation/phase1_bmi_reproduction.csv`,
`results/sensitivity/primary_vs_sensitivity_comparison.csv`.
This is the single most robust finding in the study.

## 4. Age fairness — **SUPPORTED WITH LIMITATIONS**

Age-60+ sensitivity is lower than Age-40–59 in 5/5 primary models (−8.6 to −14.7 pp),
FDR-significant in **4/5** (not Logistic). Direction never reverses across sensitivity cohorts;
significance is lost in 9/12 instances.
The shape is non-monotonic (peak ≈65 y, no decline at 70+). **Directionally robust,
statistically fragile, non-monotonic.** `fairness_inference.csv`,
`primary_vs_sensitivity_comparison.csv`, `results/diagnostics/continuous_age_metrics.csv`.
**NOT SUPPORTED:** "Age-60+ deficit significant in all models"; "older is monotonically worse".

**MANUSCRIPT FRAMING (2026-08-27, `MANUSCRIPT_FRAMING_GUIDANCE.md`):** the Age-60+ *sensitivity*
disparity is a **secondary observation** — Results body and Limitations only, not the abstract or
headline, and not paired with the BMI finding as "two subgroup failures." The Age-60+ *conformal
under-coverage* (finding 6, §12) is a separate, firmer result and is retained at full strength.

## 5. BMI × Age reliability (intersectional) — **SUPPORTED WITH LIMITATIONS** (descriptive)

In the BMI-Obese ∩ Age-60+ cell (test N=294, 35 positives) baseline split-conformal coverage
collapses to 64.97–75.17% (Clopper–Pearson CIs exclude 90%). Descriptive, pre-specified,
small-cell. `results/uncertainty/intersectional_coverage_ci.csv`. **NOT SUPPORTED:** any
conditional-validity or causal-interaction claim; the
"294 = ~62%" characterisation (that is the union — see `SUPERSEDED_INVALID_RESULTS.md` S3).

## 6. Conformal reliability — **CONFIRMED for the marginal/subgroup split** (see §12)

Split conformal at α=0.10 meets its marginal coverage target overall (88.12–90.82%) but
under-covers BMI-Obese (76.8–82.3%) and Age-60+ (81.1–85.6%) in every model, Wilson CIs
excluding 90%, FDR-significant. `results/uncertainty/marginal_coverage_test_set.csv`,
`subgroup_coverage.csv`. Marginal validity is a mathematical guarantee; subgroup adequacy is
**NOT SUPPORTED** — the central empirical finding of the study.

## 7. Mitigation effectiveness — **NOT SUPPORTED as a solution; PARTIALLY EFFECTIVE for conformal coverage** (see §14)

No intervention (Mondrian, corrected BMI mitigation, corrected subgroup calibration, group
thresholds, Equal Opportunity, XGBoost retuning, joint conformal, selective deferral) produced an
acceptable multi-metric fix for the BMI classification disparity. Mondrian conformal recalibration
is a genuine but partial repair of subgroup **coverage** (Project Phase 7: 5/9 targets, XGBoost
breach, sequential overlap; Amendment #17 re-run: ≥0.88 for 5/5 models with zero deferral but
retained marginal coverage 0.94–0.95 — over-covers). **Selective deferral (Amendment #17):
DEVELOPMENT-STAGE NEGATIVE** — no pre-registered candidate meets the gate on the calibration
partition (locked test not touched); the under-coverage is confidently-scored wrong singletons,
not flagged-uncertain cases, so a defer-to-elastography layer cannot fix it. **Training-time
subgroup reweighting (Amendment #19): NEGATIVE by the pre-registered gate** — it removed the
body-mass score-ordering mechanism (matched-stiffness BMI coef 0.18–0.25 → 0.008–0.036 OOF) and
**halved** the Normal-vs-Obese sensitivity gap (BH-sig 5/5 → 0/4) with BMI-Obese conformal
coverage 0.77–0.82 → 0.86–0.87, but at a discrimination cost (test AUROC −0.02 to −0.03), a
specificity cost (up to −12 pp), a new logistic Female sensitivity disparity, and no gain on
age-60+; the joint BMI×age arm worsened the age gap. The failure is addressable at training time
*in mechanism* but not eliminable within routine features and this sample without a
gate-failing cost.
`results/mitigation/test_set_mitigation_final.csv`, `phase3_corrected/`, `phase4_corrected/`,
`phase7_mitigation_cleanup/`, `results/selective_deferral/`, `results/training_time_mitigation/`.

## 8. MI robustness — **SUPPORTED WITH LIMITATIONS (narrow scope)**

Targeted MI for the Non-Hispanic Black selection question: ΔAUROC < 0.007, ΔBrier < 0.003; NHB
sensitivity changes ≤ ±4.2 pp, all CIs include 0, BH-adjusted p = 0.978 (correction-ceiling
artifact); 4/5 STABLE, MLP INDETERMINATE. MI conformal reliability (BMI-inv Phase 5) is
descriptively consistent with complete-case but has `LINEAGE NOT FOUND IN REPOSITORY`.
`results/sensitivity/mi_black_subgroup_comparison.csv`,
`results/fairness_bmi_investigation/phase5_mi_conformal/*`. **NOT SUPPORTED:** MI/complete-case
equivalence; whole-cohort MI conclusions.

## 9. Threshold robustness — **SUPPORTED WITH LIMITATIONS** (see §13)

Discrimination, calibration correction, and the BMI-Obese disparity are robust to an 8.0-kPa
cutoff (relabel and full re-run). The full re-run's own verdict is **"SOME MAJOR FINDINGS ARE
THRESHOLD-SENSITIVE"** — Age-60+ significance and some conformal detail are threshold-sensitive.
8.2 kPa is PRIMARY; 8.0 kPa is a sensitivity analysis and does not replace it.
`results/sensitivity/alternative_threshold_8p0kPa_results.csv`,
`results/fairness_bmi_investigation/phase6_8kpa_robustness/phase6_8kpa_vs_82_comparison.csv`.

## 10. Out-of-sample transportability — **NOT ESTABLISHED**

No later-cycle (temporal) or independent-cohort evaluation is within the scope of this study. A
NHANES 2021–2023 temporal evaluation was completed and has been split into a separate manuscript
(preserved on the `temporal-validation-standalone` git branch); it is not part of this study's
evidence base. **NOT SUPPORTED:** any temporal or external replication claim; clinical readiness.

---

## 11. BMI FAIRNESS — FINAL CONSOLIDATED ASSESSMENT

| Element | Finding | Verdict |
|---|---|---|
| Original disparity | Normal-BMI vs Obese sensitivity deficit 27.1–47.7 pp, 5/5 models, FDR q ≤ 0.006 (`fairness_inference.csv`) | CONFIRMED |
| Reproduction | Independently reproduced, counts exact, inference within rounding (`PHASE1_REPRODUCTION.md`) | CONFIRMED |
| Mechanism | Mixed empirical mechanism: fibrosis-positive Normal-BMI cases receive systematically lower model scores (Mann–Whitney significant, positive AND negative cases), plus operating-threshold consequences; possible calibration/ranking contribution; BMI×Age effect modification in older strata; young Normal-BMI cells unstable. **Non-causal.** (`PHASE2_DIAGNOSTIC_REPORT.md`) | SUPPORTED WITH LIMITATIONS |
| Threshold vs non-threshold | Subgroup thresholds reduce the BMI gap 49–69% → BMI disparity has a strong threshold component (D05/D07) | EXPLORATORY |
| Mitigation candidates tested | BMI thresholding; BMI-specific Platt; BMI×Age thresholds; combined; subgroup calibration; group Youden thresholds; Equal Opportunity; XGBoost retuning; joint conformal | — |
| Corrected mitigation result | **NO ACCEPTABLE MITIGATION IDENTIFIED** (only MLP got BMI-Platt: gap 39.03 → 34.48 pp, no formal inference) (`PHASE3_CORRECTED_MITIGATION_REPORT.md`) | SUPPORTED WITH LIMITATIONS |
| Subgroup-calibration evidence | **No acceptable subgroup-calibration improvement**; classification gaps identical to global Platt; no joint calibrator; Decision B (`PHASE4_CORRECTED_FINAL_AUDIT_REPORT.md`) | SUPPORTED WITH LIMITATIONS |
| Conformal coverage in BMI groups | BMI-**Obese** under-covers (76.8–82.3%); Normal-BMI/Overweight over-cover; Mondrian restores 2/5 Obese targets; not resolved for RF/XGB/LGBM (`subgroup_coverage.csv`, `test_set_mitigation_final.csv`) | CONFIRMED (failure); PARTIALLY EFFECTIVE (mitigation) |
| Model-fit alignment (Amendment #18) | Normal-vs-Obese classification-sensitivity gap present on the proper-train-refit models too: −27 to −42 pp, 5/5 models; negative at every threshold in a 0.30–0.60 sweep for 4/5 (`results/prepublication_fixes/fix1_*.csv`) | **STRENGTHENING** (pre-registered rule) |
| Matched-stiffness BMI shortcut (Amendment #18) | At LUXSMED 8.2–12 kPa, obese get predicted probability 0.19–0.33 higher than Normal at identical stiffness (OLS `is_obese` coef, p<0.001 all 5 models) (`fix2_bmi_shortcut_check.csv`) | CONFIRMED (fairness finding, independent of measurement bias) |
| Reference-standard measurement bias (Amendment #18) | Relabel at ≥9.7/10/12/13.6 kPa: obese sensitivity + obese conformal coverage stable (Δ≈0.03); BMI-Obese under-coverage persists/worsens; raw Obese−Normal sensitivity gap narrows/reverses but Normal-BMI n=7 at ≥12 kPa → underpowered (`fix2_*.csv`) | **V3** (pre-registered): residual measurement contribution cannot be formally excluded; demonstrated mechanism does not depend on it |
| Training-time reweighting (Amendment #19) | Kamiran–Calders instance reweighting removed the matched-stiffness BMI shortcut (0.18–0.25 → ~0.01 OOF) and **halved** the sensitivity gap (BH-sig 5/5 → 0/4); BMI-Obese coverage 0.77–0.82 → 0.86–0.87; **cost:** AUROC −0.02–0.03, specificity up to −12 pp, new logistic sex disparity; efficacy + cost gates not met (`results/training_time_mitigation/*`) | **NEGATIVE** by the pre-registered gate — mechanism addressable at training time but not eliminable within routine features / this sample without a gate-failing cost |
| Remaining limitation | Normal-BMI has 22 test positives (50 in training — the binding data limit); mechanism non-causal; no acceptable post-hoc *or* training-time fix within the pre-registered gates; measurement-bias question underpowered on the Normal-BMI side |

**Currently supported conclusion:** the Normal-BMI vs Obese sensitivity disparity is real,
reproduced, mechanism-linked, robust across independently constructed cohorts, and **NO ACCEPTABLE
BMI-SENSITIVITY MITIGATION HAS BEEN IDENTIFIED.** Repository evidence does **not** contradict this wording.
**DO NOT CLAIM** BMI fairness was solved, or that subgroup calibration / Phase 7 solved it.

---

## 12. CONFORMAL — FINAL CONSOLIDATED ASSESSMENT

| Layer | Result | Status |
|---|---|---|
| Marginal (overall) coverage | 88.12–90.82% at α=0.10; near target; mathematically guaranteed under exchangeability | CONFIRMED / by construction |
| Subgroup coverage — BMI-Obese | 76.8–82.3%, CIs exclude 90%, 5/5, FDR-significant | CONFIRMED failure |
| Subgroup coverage — Age-60+ | 81.1–85.6%, CIs exclude 90%, 5/5, FDR-significant | CONFIRMED failure |
| Exploratory intersectional (Obese ∩ 60+, N=294) | baseline 64.97–75.17% | SUPPORTED WITH LIMITATIONS (descriptive, small cell) |
| Mondrian mitigation (Project Phase 7) | 5/9 targets nominal; XGBoost marginal +5.27 pp breach; sequential overlap | PARTIALLY EFFECTIVE |
| MI conformal (BMI-inv Phase 5) | descriptively consistent with complete-case; BMI-Obese still under-covers | EXPLORATORY / `LINEAGE NOT FOUND` |
| Joint conformal (Method b/c, M4b N0=0) | CAND_1 intersectional coverage ≥90% for 4–5/5; XGB/LGBM marginal breach | EXPLORATORY |
| Faithful AFCP | near-target single-attribute; intersection still <90%; overall >90% | EXPLORATORY (C3 ADJUDICATED 2026-08-27: KNN-AFCP INVALID, faithful AFCP EXPLORATORY, no superiority claim) |
| Selective deferral (Amendment #17) | no pre-registered candidate meets the gate; deferring uncertain sets lowers retained coverage; Mondrian 3d restores 5/5 with zero deferral but over-covers marginally (0.94–0.95) | DEVELOPMENT-STAGE NEGATIVE (locked test not touched) |
| 8.0-kPa conformal | some detail threshold-sensitive (BMI-inv Phase 6) | SUPPORTED WITH LIMITATIONS |
| CAND_2 / CAND_3 conformal replication | **MEASURED (Amendment #16):** marginal on target (0.896–0.917); BMI-Obese under-covers 5/5 both cohorts (FDR-sig); Age-60+ direction-robust, FDR-sig 5/5 CAND_2 / 2/5 CAND_3 | CONFIRMED (BMI-Obese); SUPPORTED WITH LIMITATIONS (Age-60+) |

**Do not claim conditional / subgroup conformal validity.** Marginal validity holds; subgroup
adequacy does not; no method tested achieves subgroup or intersectional validity that is
acceptable on all metrics.

---

## 13. THRESHOLD-ROBUSTNESS ASSESSMENT (8.2 kPa PRIMARY; 8.0 kPa SENSITIVITY)

| Finding | 8.0-kPa behaviour | Verdict |
|---|---|---|
| Discrimination (AUROC band) | 0.8145–0.8326 (relabel); direction/ordering stable | ROBUST (magnitude changed) |
| Calibration correction by OOF Platt | holds | ROBUST |
| Normal-BMI vs Obese sensitivity disparity | **strengthens** to 35.1–51.6 pp; 5/5 significant | ROBUST (magnitude changed) |
| Age-60+ disparity direction | negative 5/5 | ROBUST (direction) |
| Age-60+ disparity significance | drops to 2/5 (relabel); "threshold-sensitive" (full re-run) | THRESHOLD-SENSITIVE |
| Conformal subgroup coverage detail | some detail threshold-sensitive | MAGNITUDE CHANGED / THRESHOLD-SENSITIVE |
| Equivalence of 8.0 and 8.2 | never tested | INCONCLUSIVE — **do not claim statistical indistinguishability** |

Full-pipeline verdict from `PHASE6_8KPA_ROBUSTNESS_REPORT.md`: **SOME MAJOR FINDINGS ARE
THRESHOLD-SENSITIVE.** 8.0 kPa must be reported as a robustness/sensitivity analysis, never as a
replacement for the primary analysis.

---

## 14. MITIGATION — FINAL CONSOLIDATED ASSESSMENT

| Intervention | Objective | Method | Result | Status | Manuscript |
|---|---|---|---|---|---|
| Mondrian (Project Phase 7) | restore subgroup conformal coverage | FDR-gated group-conditional quantiles for dual-criterion targets | 5/9 nominal; XGBoost +5.27 pp marginal breach; Age-over-BMI precedence in overlap | **PARTIALLY EFFECTIVE** | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Mondrian re-run (Amendment #17, candidate 3d) | restore subgroup conformal coverage on the calibration partition | group-conditional quantiles, no deferral | BMI-Obese & Age-60+ ≥ 0.88 for **5/5** models with zero deferral, but retained **marginal coverage rises to 0.94–0.95** (G2 fail) and well-served subgroups stay > 0.95 (G3 fail) — restoring target marginal coverage needs *levelling down* | **PARTIALLY EFFECTIVE** (coverage only; over-covers) | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Conformal selective deferral (Amendment #17) | restore subgroup coverage by deferring flagged-uncertain cases to elastography | pre-registered candidates 3a/3b/3d/3e vs a multi-metric core gate, calibration partition only | **no candidate meets the core gate (0/5 models)**; deferring two-class {pos,neg} sets *lowers* retained coverage (the misses are wrong singletons); locked test NOT touched (Phase 4 skipped per pre-registration) | **NO IMPROVEMENT / DEVELOPMENT-STAGE NEGATIVE** | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Corrected BMI-sensitivity mitigation (BMI-inv Phase 3) | close Normal-BMI sensitivity gap | 4 candidates, independent split, multi-metric gate | none passed across families; MLP-only BMI-Platt (39.03→34.48 pp) | **NO ACCEPTABLE MITIGATION** | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Corrected subgroup calibration (BMI-inv Phase 4) | improve subgroup reliability via calibration | equal-frequency ECE, independent fit/eval, explicit fallback | ECE improved 3 models; classification/gaps unchanged; no reliability gain; Decision B | **NO ACCEPTABLE MITIGATION** | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Group-specific Youden thresholds (D05/D07) | equalize subgroup sensitivity | OOF-derived subgroup thresholds | BMI gap halved; Age gap +26–133%; ~40 pp specificity cost | **EXPLORATORY ONLY** | EXPLORATORY_ONLY |
| Equal Opportunity post-processing (D06) | equalize TPR | subgroup threshold shift to target TPR | ~50–80 pp sensitivity gain at ~40 pp specificity cost; ~399 excess FP/1,000 | **EXPLORATORY ONLY** (clinically unacceptable) | EXPLORATORY_ONLY |
| XGBoost mitigation retuning (BMI-inv Phase 7) | remove XGBoost coverage breach | authorized Phase 3 candidate family, OOF only | every gap-closing candidate costs 11–22 pp sensitivity or flips the breach | **NO ACCEPTABLE RETUNING** | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Joint intersectional conformal (Method b/c, M4b N0=0) | restore Obese∩60+ coverage | joint-cell / shrinkage quantiles | CAND_1 ≥90% for 4–5/5; XGB/LGBM marginal breach | **EXPLORATORY ONLY / VALID SECONDARY METHOD** | EXPLORATORY_ONLY |
| **Training-time subgroup reweighing — BMI (Amendment #19, Arm A, primary)** | remove the body-mass score-ordering failure at training time | Kamiran–Calders instance reweighting; frozen hyperparameters; 2 locked-test touches; MLP excluded (unstable), gate ≥3/4 | matched-stiffness BMI coef 0.18–0.25 → 0.008–0.036 (OOF); Normal-vs-Obese sensitivity gap **halved** (+27–48 → +14–17 pp; BH-sig 5/5 → 0/4); BMI-Obese conformal coverage 0.77–0.82 → 0.857–0.871 (<0.88); age-60+ coverage unchanged. **Cost:** AUROC −0.02–0.03; specificity up to −12 pp; new logistic Female disparity (−15.1 pp). Efficacy + cost gates not met. | **NEGATIVE** (mechanism addressed, not eliminated to standard) | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Training-time subgroup reweighing — BMI×age (Amendment #19, Arm B, secondary) | as above, jointly | 12 BMI×age cells (4 use the Arm-A fallback weight) | body-mass gap halved similarly, but **age-60+ sensitivity gap worsened, BH-sig 3/4**; larger specificity cost; within-Normal-BMI OOF AUROC *fell* | **NEGATIVE** (one objective cannot repair both mechanisms) | supporting |

**Classification key:** SUCCESSFUL — *none*. PARTIALLY EFFECTIVE — Mondrian (conformal coverage
only, at the cost of marginal over-coverage). NO ACCEPTABLE MITIGATION — corrected BMI mitigation,
corrected subgroup calibration, XGBoost retuning. NO IMPROVEMENT — selective deferral. NEGATIVE
(mechanism addressed, gate not met) — training-time reweighting. EXPLORATORY ONLY — group
thresholds, Equal Opportunity, joint conformal.

**Do not describe any intervention as successful because one metric improved.** The residual
under-coverage is a within-subgroup score-ordering failure that no post-hoc method repairs; the
Amendment #19 training-time reweighting addresses the mechanism and halves the gap but not without
a gate-failing discrimination/specificity cost. Closing the gap to an acceptable standard would
require more normal-weight fibrosis cases (50 train / 22 test — the binding data limit), features
that better separate lean fibrosis, or an explicitly accepted performance–equity trade — not a
better objective alone.
