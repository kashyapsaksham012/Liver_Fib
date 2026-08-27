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
(q ≤ 0.006); independently reproduced; stable across all three sensitivity cohorts (15/15) and
**enlarged temporally** to 62.8–71.9 pp. `results/fairness/fairness_inference.csv`,
`results/fairness_bmi_investigation/phase1_bmi_reproduction.csv`,
`results/sensitivity/primary_vs_sensitivity_comparison.csv`,
`results/temporal_validation/temporal_fairness_results.csv`.
This is the single most robust finding in the study.

## 4. Age fairness — **SUPPORTED WITH LIMITATIONS**

Age-60+ sensitivity is lower than Age-40–59 in 5/5 primary models (−8.6 to −14.7 pp),
FDR-significant in **4/5** (not Logistic). Direction never reverses across sensitivity cohorts;
significance is lost in 9/12 instances and reverses direction temporally (60+ slightly higher).
The shape is non-monotonic (peak ≈65 y, no decline at 70+). **Directionally robust,
statistically fragile, non-monotonic.** `fairness_inference.csv`,
`primary_vs_sensitivity_comparison.csv`, `results/diagnostics/continuous_age_metrics.csv`,
`results/temporal_validation/temporal_fairness_results.csv`.
**NOT SUPPORTED:** "Age-60+ deficit significant in all models"; "older is monotonically worse".

**MANUSCRIPT FRAMING (2026-08-27, `MANUSCRIPT_FRAMING_GUIDANCE.md`):** the Age-60+ *sensitivity*
disparity is a **secondary observation** — Results body and Limitations only, not the abstract or
headline, and not paired with the BMI finding as "two subgroup failures." The Age-60+ *conformal
under-coverage* (finding 6, §12) is a separate, firmer result and is retained at full strength.

## 5. BMI × Age reliability (intersectional) — **SUPPORTED WITH LIMITATIONS** (descriptive)

In the BMI-Obese ∩ Age-60+ cell (test N=294, 35 positives) baseline split-conformal coverage
collapses to 64.97–75.17% (Clopper–Pearson CIs exclude 90%). Descriptive, pre-specified,
small-cell. `results/uncertainty/intersectional_coverage_ci.csv`. Persists temporally
(69.7–76.5%). **NOT SUPPORTED:** any conditional-validity or causal-interaction claim; the
"294 = ~62%" characterisation (that is the union — see `SUPERSEDED_INVALID_RESULTS.md` S3).

## 6. Conformal reliability — **CONFIRMED for the marginal/subgroup split** (see §12)

Split conformal at α=0.10 meets its marginal coverage target overall (88.12–90.82%) but
under-covers BMI-Obese (76.8–82.3%) and Age-60+ (81.1–85.6%) in every model, Wilson CIs
excluding 90%, FDR-significant. `results/uncertainty/marginal_coverage_test_set.csv`,
`subgroup_coverage.csv`. Marginal validity is a mathematical guarantee; subgroup adequacy is
**NOT SUPPORTED** — the central empirical finding of the study.

## 7. Mitigation effectiveness — **NOT SUPPORTED as a solution; PARTIALLY EFFECTIVE for conformal coverage** (see §14)

No intervention (Mondrian, corrected BMI mitigation, corrected subgroup calibration, group
thresholds, Equal Opportunity, XGBoost retuning, joint conformal) produced an acceptable
multi-metric fix for the BMI classification disparity. Mondrian conformal recalibration is a
genuine but partial repair of subgroup **coverage** (5/9 targets; XGBoost breach; sequential
overlap handling). `results/mitigation/test_set_mitigation_final.csv`,
`phase3_corrected/`, `phase4_corrected/`, `phase7_mitigation_cleanup/`.

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

## 10. Temporal transportability — **NOT SUPPORTED as full replication; PARTIAL TEMPORAL REPLICATION**

NHANES 2021–2023 (N=4,910; 11.4664%): AUROC declined to 0.7765–0.7824 (discrimination MIXED —
AUROC down, PR-AUC up); raw calibration still poor (Brier worse); **BMI-Obese sensitivity
disparity persisted and enlarged (62.8–71.9 pp)**; Age-60+ disparity shrank/reversed; marginal
conformal coverage near target but subgroup/intersectional under-coverage persisted; frozen
N0=0 M4b met its intersectional target for **1/5 models** (vs 4/5 originally). Final
classification **PARTIAL TEMPORAL REPLICATION**. `PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md`.
**NOT SUPPORTED:** full temporal replication, external validation, clinical readiness, causal
drift explanation (root-cause analysis found only SUPPORTED ASSOCIATIONS —
`PHASE3_5_ROOT_CAUSE_DRIFT_TO_PERFORMANCE_REPORT.md`).

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
| Temporal | Disparity persisted and **enlarged** to 62.8–71.9 pp | CONFIRMED |
| Remaining limitation | Normal-BMI has 22 test positives; mechanism non-causal; no acceptable fix; conformal replication on sensitivity cohorts not measured |

**Currently supported conclusion:** the Normal-BMI vs Obese sensitivity disparity is real,
reproduced, mechanism-linked, robust across cohorts and time, and **NO ACCEPTABLE BMI-SENSITIVITY
MITIGATION HAS BEEN IDENTIFIED.** Repository evidence does **not** contradict this wording.
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
| Joint conformal (Method b/c, M4b N0=0) | CAND_1 intersectional coverage ≥90% for 4–5/5; XGB/LGBM marginal breach; **fails temporally (1/5)** | EXPLORATORY |
| Faithful AFCP | near-target single-attribute; intersection still <90%; overall >90% | EXPLORATORY (C3 ADJUDICATED 2026-08-27: KNN-AFCP INVALID, faithful AFCP EXPLORATORY, no superiority claim) |
| 8.0-kPa conformal | some detail threshold-sensitive (BMI-inv Phase 6) | SUPPORTED WITH LIMITATIONS |
| CAND_2 / CAND_3 conformal replication | NOT MEASURED | INCONCLUSIVE |

**Do not claim conditional / subgroup conformal validity.** Marginal validity holds; subgroup
adequacy does not; no method tested achieves subgroup or intersectional validity that is
acceptable on all metrics and replicates over time.

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
| Corrected BMI-sensitivity mitigation (BMI-inv Phase 3) | close Normal-BMI sensitivity gap | 4 candidates, independent split, multi-metric gate | none passed across families; MLP-only BMI-Platt (39.03→34.48 pp) | **NO ACCEPTABLE MITIGATION** | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Corrected subgroup calibration (BMI-inv Phase 4) | improve subgroup reliability via calibration | equal-frequency ECE, independent fit/eval, explicit fallback | ECE improved 3 models; classification/gaps unchanged; no reliability gain; Decision B | **NO ACCEPTABLE MITIGATION** | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Group-specific Youden thresholds (D05/D07) | equalize subgroup sensitivity | OOF-derived subgroup thresholds | BMI gap halved; Age gap +26–133%; ~40 pp specificity cost | **EXPLORATORY ONLY** | EXPLORATORY_ONLY |
| Equal Opportunity post-processing (D06) | equalize TPR | subgroup threshold shift to target TPR | ~50–80 pp sensitivity gain at ~40 pp specificity cost; ~399 excess FP/1,000 | **EXPLORATORY ONLY** (clinically unacceptable) | EXPLORATORY_ONLY |
| XGBoost mitigation retuning (BMI-inv Phase 7) | remove XGBoost coverage breach | authorized Phase 3 candidate family, OOF only | every gap-closing candidate costs 11–22 pp sensitivity or flips the breach | **NO ACCEPTABLE RETUNING** | MANUSCRIPT_READY_WITH_QUALIFICATION |
| Joint intersectional conformal (Method b/c, M4b N0=0) | restore Obese∩60+ coverage | joint-cell / shrinkage quantiles | CAND_1 ≥90% for 4–5/5; XGB/LGBM marginal breach; temporal 1/5 | **EXPLORATORY ONLY / VALID SECONDARY METHOD** | EXPLORATORY_ONLY |

**Classification key:** SUCCESSFUL — *none*. PARTIALLY EFFECTIVE — Mondrian (conformal coverage
only). NO ACCEPTABLE MITIGATION — corrected BMI mitigation, corrected subgroup calibration,
XGBoost retuning. EXPLORATORY ONLY — group thresholds, Equal Opportunity, joint conformal.

**Do not describe any intervention as successful because one metric improved.**
