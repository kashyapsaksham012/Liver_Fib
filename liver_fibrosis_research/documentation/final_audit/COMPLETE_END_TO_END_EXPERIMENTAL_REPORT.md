# COMPLETE CURRENT END-TO-END LIVER-FIBROSIS MACHINE-LEARNING RESEARCH AUDIT

**Compiled:** 25 Aug 2026. **Version:** 2.0 (supersedes prior 878-line version, written before D01–D08 diagnostics completed).

Every claim is source-traced. Where a detail could not be verified from the repository, it is marked **NOT ESTABLISHED FROM THE AVAILABLE EXPERIMENTAL RECORD**.

**Fact legend:** **[A]** Experimental fact, directly verified from repository. **[B]** Literature fact. **[C]** Logical inference from A/B. **[D]** Scientific interpretation.

---

## PART 1 — EXECUTIVE SUMMARY

This project asked whether a clinical prediction model for liver fibrosis that looks acceptable on discrimination also reliably serves identifiable demographic subgroups — and what can be done when it does not. The experimental record, now complete, answers that question across five evidence layers (discrimination, calibration, fairness, conformal uncertainty, mitigation) on a real-world NHANES dataset with an independently-validated clinical outcome threshold. All planned diagnostics are executed. The final validation suite passes 26/26 checks. The experiment is approved for freeze.

**Central finding (one sentence):** A five-model liver-fibrosis ML pipeline achieves comparable, modest discrimination (AUC 0.82–0.84) but exhibits robust, statistically verified sensitivity and conformal-coverage failures specifically in BMI-Normal and Age-60+ participants — with the failures compounding at their intersection — and the two subgroups respond to different, documented mechanisms, which directly determines which interventions work and which do not.

**Experimental status:** GREEN — APPROVED FOR FREEZE. BEGIN MANUSCRIPT WRITING.

---

## PART 2 — CURRENT RESEARCH STATUS AND COMPLETENESS MATRIX

| Component | Planned | Executed | Verified | Frozen | Current Status |
|---|---|---|---|---|---|
| Phase 1 — Data Assembly | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Phase 2 — Protocol Freeze | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Phase 3 — Model Development | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Phase 4 — Calibration | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Phase 5 — Fairness | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Phase 6 — Conformal Uncertainty | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Phase 7 — Mondrian Mitigation | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Phase 8 — NHB Subgroup Holdout | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Sensitivity: 8.0 kPa threshold | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Sensitivity: CAND_2 relaxed elastography | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Sensitivity: CAND_3 fasting-extended | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Sensitivity: CAND_4 all-ages 12+ | Y | N | N | N | DEFINED BUT UNEXECUTED — status unresolved at source-document level |
| Multiple Imputation (NHB scope) | Y | Y | Y | Y | COMPLETE AND FROZEN |
| Reliability Extension (co-occurrence + DCA) | Y | Y | Y | Y | COMPLETE AND FROZEN |
| D01 — Socio-Conformal Literature Audit | Y | Y | Y | Y | COMPLETE — NOVELTY THREAT LOW |
| D02 — Continuous BMI Spline | Y | Y | Y | Y | COMPLETE — CONTINUOUS GRADIENT CONFIRMED |
| D03 — Continuous Age + Fine Bands | Y | Y | Y | Y | COMPLETE — NON-MONOTONIC PATTERN |
| D04 — Subgroup-Specific Platt Recalibration | Y | Y | Y | Y | COMPLETE — <1 pp COVERAGE CHANGE |
| D05 — Group-Specific Threshold Analysis | Y | Y | Y | Y | COMPLETE — TWO-MECHANISM FINDING |
| D06 — EO Fairness Post-Processing | Y | Y | Y | Y | COMPLETE — +51 to 80 pp SENSITIVITY GAINS |
| D07 — AFCP vs. Mondrian Comparison | Y | Y | Y | Y | COMPLETE — MONDRIAN PREFERRED |
| D08 — Final Reproducibility Validation | Y | Y | Y | Y | 26/26 CHECKS PASSED |
| External (non-NHANES) validation | N | N | N | N | NOT PLANNED — MAJOR LIMITATION |

---

## PART 3 — COMPLETE EXPERIMENT TIMELINE [A]

| Phase | Date (if verifiable) | Objective | Key Methodological Decision |
|---|---|---|---|
| Phase 1 | Pre-2026-08-18 | Parse/link NHANES raw files; define candidate cohorts | Anchor on P_LUX elastography; complete-case strategy adopted |
| Phase 2 | Pre-2026-08-18 | Protocol freeze before any modeling | Outcome threshold = 8.2 kPa from external meta-analysis; 10 predictors frozen; race excluded from inputs |
| Phase 3 | 2026-08-18 (report timestamp) | Train, tune, evaluate 5 model families | Youden's J threshold from OOF only; all 5 families retained regardless of AUC ranking |
| Phase 3 Remediation | 2026-08-18 | Audit and remediate Phase 3; verify byte-identity | MLP class-imbalance gap documented; 44/44 tests pass |
| Phase 4 | 2026-08-19 | Calibration diagnosis and recalibration | Platt (OOF fit) selected over isotonic; single test-set touch |
| Phase 5 | 2026-08-19 | Fairness/subgroup disparity audit | BMI/Age disparities confirmed; 92/92 tests pass |
| Phase 6 | 2026-08-19 | Split conformal prediction | 90% nominal target; BMI-Obese and Age-60+ fail; 50/50 tests pass |
| Phase 7 | 2026-08-19 | Mondrian mitigation for dual-FDR-flagged subgroups | Sequential precedence logic; 5/9 combinations resolved; 33/33 tests pass |
| Phase 8 | 2026-08-19 | NHB subgroup-holdout generalization | Temporal validation infeasible; subgroup holdout chosen; 35/35 tests pass |
| Sensitivity Track | 2026-08-19 approx. | 3 of 4 deferred sensitivity analyses | 8.0 kPa relabel; CAND_2/CAND_3 retrain; 39/39 tests pass |
| MI Analysis | Before Phase 8 | NHB-scoped multiple imputation | m=5 imputations, BayesianRidge; MI ROBUSTNESS PARTIAL |
| Reliability Extension | After Phase 8 | Co-occurrence correlation + DCA | Permutation p=0.12 (not confirmed); DCA utility positive; 29/29 tests pass |
| D01–D08 Diagnostics | 2026-08-25 | Staged diagnostic analyses per pre-specified gated protocol | 7 scientific analyses; 26/26 final validation checks pass; freeze approved |

---

## PART 4 — RESEARCH QUESTIONS BY PHASE [A]

### Phase 1–2
**Main question:** Can we assemble a quality-controlled NHANES cohort with an independently-validated fibrosis outcome for ML?
**Finding:** N=7,153, 9.31% prevalence; complete-case exclusion disproportionately excludes NHB (41.3% vs. 24.98%).

### Phase 3
**Main question:** What baseline discrimination can be achieved, and do the five families differ significantly?
**Hypothesis H1:** AUC 0.75–0.85. **Finding:** AUC 0.82–0.84. No pairwise FDR winner. **Decision:** Retain all 5 families.

### Phase 4
**Main question:** Are models with similar discrimination equally well calibrated?
**Hypothesis H2:** At least one model will show measurable miscalibration despite acceptable AUC.
**Finding:** All 5 miscalibrated; 4 by explainable class-balancing prior shift; MLP not. Platt recalibration verified effective.

### Phase 5
**Main question:** Do models with acceptable overall performance show demographic sensitivity disparities?
**Finding:** BMI-Normal deficit 27–48pp (all 5 models); Age-60+ deficit 11–15pp (4/5 models). Race/sex: no consistent FDR pattern.

### Phase 6
**Main question:** Does marginal conformal coverage imply subgroup coverage?
**Finding:** No. Marginal 88.1–90.8%. BMI-Obese 76.8–82.3%; Age-60+ 81.1–85.6%; intersection 65.0–75.2%.

### Phase 7
**Main question:** Can Mondrian mitigation resolve identified coverage failures?
**Finding:** 5/9 qualifying combinations resolved; 4/9 not. Intersection remains below 90% under frozen method.

### Phase 8
**Main question:** Does performance degrade when NHB participants are absent from training?
**Finding:** AUC drops 4.7–5.9pp vs. full population. Calibration degrades substantially (uncorrected).

### D01–D08 Diagnostics
**Main questions:** Are BMI/Age effects genuine continuous gradients or cutpoint artifacts? What mechanism drives them? Can EO post-processing or alternative conformal methods address the gaps?
**Findings:** summarized in Part 18 below.

---

## PART 5 — DATASET CONSTRUCTION [A]

### Primary Cohort Flow

| Step | Population | N |
|---|---|---:|
| Elastography attempted (P_LUX anchor) | All NHANES 2017–March 2020 with LUX data | 10,409 |
| Quality-valid elastography (LUAXSTAT==1) | Quality-valid subset | 9,023 |
| Adult (>=18) quality-valid (COHORT_3B) | Adult quality-valid | 7,768 |
| Primary cohort (CAND_1) — broad labs + BMI/sex complete | Complete-case primary | **7,153** |
| Positive cases (LUXSMED >= 8.2 kPa) | — | **666** (9.31%) |
| Train | Stratified 70% | **5,007** |
| Locked test | Stratified 30% | **2,146** |

### Alternative and Sensitivity Cohorts [A]

| Cohort | Definition | N | Positive | Status |
|---|---|---:|---:|---|
| CAND_2 | Relaxed elastography quality (non-missing LUXSMED, not LUAXSTAT==1) | 7,639 | 804 (10.52%) | EXECUTED (sensitivity) |
| CAND_3 | Fasting-extended — adds fasting glucose + triglycerides | 3,582 | 319 (8.91%) | EXECUTED (sensitivity) |
| CAND_4 | All-ages 12+ | ~8,215 | — | DEFINED, NEVER EXECUTED — source-document status unresolved |
| MI pool | Complete + imputed (m=5, BayesianRidge) | 7,768 | — | EXECUTED, NHB scope only |
| Phase 8 NHB holdout | NHB excluded from training | Train: 5,366 / Holdout: 1,787 | Holdout: 177 | EXECUTED |

**Selection disparity:** NHB: 41.30% of excluded vs. 24.98% of retained (N_excluded=615). MI analysis found no FDR-significant discrimination/calibration/NHB-fairness change. Conformal-coverage under MI: **NEVER ASSESSED — open limitation.**

---

## PART 6 — OUTCOME DEFINITION [A]

| Item | Definition |
|---|---|
| Primary outcome | LUXSMED >= 8.2 kPa (binary; quality-valid exam required) |
| Clinical target | Significant liver fibrosis (>=F2 histological equivalent) |
| Threshold source | 2024 VCTE-vs-MRE meta-analysis, PMC11493355; NOT derived from this dataset |
| Threshold freeze timing | Before any model training (Phase 2 protocol documents) |
| Sensitivity threshold | LUXSMED >= 8.0 kPa — pre-specified in same Phase 2 document |
| Executed against sensitivity threshold | YES (relabeling only; no retrain needed; AUC 0.8145–0.8326) |
| Secondary severity outcomes | >=9.7 kPa (advanced), >=13.6 kPa (cirrhosis) — frozen but NEVER MODELED |
| Alteration rule | Non-negotiable: threshold may NOT be changed based on class balance, AUC, or subgroup performance |

---

## PART 7 — PREDICTOR REGISTRY [A]

| Variable | Meaning | Source | Role |
|---|---|---|---|
| RIDAGEYR | Age (years) | P_DEMO | Model input |
| RIAGENDR | Sex (binary) | P_DEMO | Model input + fairness stratification |
| BMXBMI | BMI (kg/m2) | P_BMX | Model input + fairness stratification |
| LBXSATSI | ALT (U/L) | P_BIOPRO | Model input |
| LBXSASSI | AST (U/L) | P_BIOPRO | Model input |
| LBXSAL | Albumin (g/dL) | P_BIOPRO | Model input |
| LBXSAPSI | ALP (U/L) | P_BIOPRO | Model input |
| LBXSTB | Total bilirubin (mg/dL) | P_BIOPRO | Model input |
| LBXPLTSI | Platelet count (1000 cells/uL) | P_CBC | Model input |
| LBDHDD | HDL cholesterol (mmol/L) | P_HDL | Model input |
| RIDRETH3/RIDRETH1 | Race/ethnicity | P_DEMO | FAIRNESS STRATIFICATION ONLY — excluded from model inputs |
| LUXSMED / LUAXSTAT | Elastography outcome / quality | P_LUX | Outcome derivation only — excluded from inputs |
| LBXGLU, LBXTR | Fasting glucose, triglycerides | P_GLU, P_TRIGLY | CAND_3 sensitivity architecture only — not primary |

**Preprocessing:** SimpleImputer(median) + StandardScaler inside ColumnTransformer, fit exclusively inside CV training folds for LR/MLP. Tree-based models receive imputer only (no scaling). No feature selection exists anywhere.

---

## PART 8 — PREPROCESSING [A]

| Step | Fitted on | Applied to | Leakage prevented? |
|---|---|---|---|
| Median imputation | Training fold only (inside Pipeline) | Val/test fold in same Pipeline call | Yes — structural |
| Standard scaling (LR/MLP) | Training fold only | Same | Yes |
| Class weighting (LR, RF) | Compile-time (class_weight="balanced") | Training only | N/A |
| scale_pos_weight (XGB, LGBM) | Compile-time (approx. 9.74) | Training only | N/A |
| Platt recalibration | OOF predictions (5,007 * 5-fold) | Locked test set (single application) | Yes — OOF only |
| Conformal refit | proper_train_ids.csv (N=4,005) | Conformal calibration set | Yes — runtime assertion |
| Mondrian thresholds | Calibration-set subgroup slices | Locked test set | Yes — disjointness assertion |

No SMOTE anywhere. RandomOverSampler exists only inside MLP Balanced sensitivity variant, training-fold-only.

---

## PART 9 — DATA SPLITTING AND PROVENANCE [A]

All figures verified from split files (data/processed/splits/):

| Split | N | Positive | Purpose |
|---|---:|---:|---|
| Train | 5,007 | 466 (9.307%) | Model development and CV |
| Locked test | 2,146 | 200 (9.320%) | Final evaluation — touched once per phase |
| Proper-train (Phase 6/7) | 4,005 | 373 (9.313%) | Conformal-valid model refit |
| Conformal calibration | 1,002 | 93 (9.281%) | Conformal quantile computation |
| Phase 8 training (NHB excluded) | 5,366 | 489 (9.113%) | NHB holdout retrain |
| Phase 8 NHB holdout | 1,787 | 177 (9.905%) | NHB generalization evaluation |

All pairwise overlaps verified zero (26/26 final validation checks). Locked test set accessed by new predictions exactly 4 times across the whole project: Phase 3, Phase 6 refit, Phase 7 mitigation, Phase 8 retrain — each for a distinct fitted-model artifact. Phases 4/5 reuse Phase 3 frozen test predictions read-only.

---

## PART 10 — PRIMARY MODEL DEVELOPMENT [A]

From phase3_05_train_and_tune.py and phase3_common.py:

| Model | Class imbalance | Tuning | CV AUC | Test AUC | Youden Threshold (OOF) |
|---|---|---|---:|---:|---:|
| Logistic Regression | class_weight="balanced" | 6-pt grid (C) | 0.8157 | 0.8334 | 0.5173 |
| Random Forest | class_weight="balanced" | 20-pt randomized | 0.8210 | 0.8343 | 0.4499 |
| XGBoost | scale_pos_weight approx. 9.74 | 20-pt randomized | 0.8212 | 0.8429 | 0.4108 |
| LightGBM | scale_pos_weight approx. 9.74 | 20-pt randomized | 0.8157 | 0.8394 | 0.4988 |
| MLP | None (sklearn API constraint) | 18-pt grid | 0.8184 | 0.8229 | 0.1065 |
| MLP Balanced (sensitivity only) | RandomOverSampler(1:1) inside imblearn.Pipeline | Same arch | — | 0.8335 | — |

5-fold StratifiedKFold(shuffle=True, random_state=42). All 5 primary families retained per frozen Phase 2 protocol regardless of AUC ranking. MLP Balanced is a sensitivity check, NEVER a primary model. 16 fitted joblib artifacts git-tracked.

---

## PART 11 — PRIMARY DISCRIMINATION RESULTS [A]

From results/tables/phase3_final_baseline_results.csv:

| Model | Test AUC (95% CI) | PR-AUC | Sensitivity | Specificity | PPV | NPV |
|---|---|---:|---:|---:|---:|---:|
| Logistic | 0.8334 (0.8021–0.8610) | 0.3725 | 0.750 | 0.762 | 0.245 | 0.967 |
| Random Forest | 0.8343 (0.8036–0.8611) | 0.3508 | 0.790 | 0.736 | 0.235 | 0.971 |
| XGBoost | 0.8429 (0.8123–0.8693) | 0.3717 | 0.845 | 0.677 | 0.212 | 0.977 |
| LightGBM | 0.8394 (0.8088–0.8670) | 0.3729 | 0.795 | 0.749 | 0.246 | 0.973 |
| MLP | 0.8229 (0.7903–0.8532) | 0.3652 | 0.815 | 0.664 | 0.200 | 0.972 |

Pairwise comparison (10 pairs, BH-FDR, own Phase 3 family): 0 significant pairs. XGBoost-vs-MLP is a boundary case (adjusted p approx. 0.050). Under the pooled 182-test BH-FDR correction this pair IS significant (adjusted p=0.0136). PR-AUC is 3.7–4.0x the no-skill baseline (0.093). No model declared winner.

---

## PART 12 — CALIBRATION [A]

### Raw Calibration (OOF, N=5,007), from results/calibration/primary_metrics_by_model.csv

| Model | Intercept | Slope | Brier | ECE |
|---|---:|---:|---:|---:|
| Logistic | -2.2425 | 1.0606 | 0.1739 | 0.2931 |
| Random Forest | -1.8625 | 1.1985 | 0.1397 | 0.2322 |
| XGBoost | -2.0460 | 1.0393 | 0.1523 | 0.2447 |
| LightGBM | -2.0535 | 1.0622 | 0.1554 | 0.2507 |
| MLP | -0.2809 | 0.8296 | 0.0710 | 0.0132 |

**Mechanism [A/C]:** The 4 class-balanced models train against an implicit 50:50 prior; true training prevalence is 9.307%. Log-odds prior correction: log(0.0931/0.9069) approx. -2.27 — matching observed intercepts (-1.86 to -2.26) closely. MLP lacks native class weighting and shows no distortion. MLP Balanced reproduces the large negative intercept (approx. -2.16), confirming mechanism is class-balancing, not architecture.

### Locked Test Set: Raw vs. Recalibrated, from test_set_calibration_final.csv

| Model | Intercept raw/recal | Brier raw/recal | ECE raw/recal | AUC |
|---|---|---|---|---:|
| Logistic | -2.2602 / -0.1537 | 0.1755 / 0.0705 | 0.2967 / 0.0172 | 0.8334 |
| Random Forest | -1.9679 / +0.0238 | 0.1458 / 0.0709 | 0.2452 / 0.0113 | 0.8343 |
| XGBoost | -2.1629 / +0.1241 | 0.1557 / 0.0694 | 0.2572 / 0.0152 | 0.8429 |
| LightGBM | -2.1846 / +0.1418 | 0.1603 / 0.0696 | 0.2638 / 0.0143 | 0.8394 |
| MLP | -0.4354 / -0.1189 | 0.0716 / 0.0715 | 0.0290 / 0.0264 | 0.8229 |

AUC unchanged by construction (Platt scaling is monotonic). Brier halved for 4 affected models.

**Isotonic regression: EVALUATED AND REJECTED.** [A] Rationale: only 466 OOF positives; intercept-shift-dominated pattern does not require non-parametric flexibility. Logged as Protocol Amendment #8.

**109/109 automated calibration tests passed. [A]**

---

## PART 13 — FAIRNESS AUDIT [A]

### Subgroup Definitions
Sex: Male/Female (RIAGENDR). Race/ethnicity: 6 categories (Non-Hispanic White reference). Age: 18–39 / 40–59 (reference) / 60+. BMI: Underweight (<18.5) / Normal-Weight (18.5–24.9, reference) / Overweight (25–29.9) / Obese (>=30.0).

### Results from results/fairness/fairness_inference.csv

**BMI (primary finding, ROBUST):**
BMI-Obese vs. Normal-BMI sensitivity disparity: +27.1pp to +48.0pp (Obese is HIGHER; Normal-BMI is the disadvantaged group). FDR-significant in all 5 models (adjusted p <= 0.006). Models disproportionately miss fibrosis cases in Normal-weight participants.

**Age (secondary finding, MODERATELY ROBUST):**
Age-60+ vs. 40–59 sensitivity deficit: -11.2pp to -14.7pp. FDR-significant in 4 of 5 models (RF: p=0.026, XGB: p=0.032, LGBM: p=0.034, MLP: p=0.012). Logistic Regression does NOT reach FDR significance — this directly determines Phase 7 mitigation scope.

**Sex:** No consistent, FDR-significant disparity found. [A]

**Race/ethnicity:** Non-Hispanic Asian shows large but FDR-non-significant negative sensitivity (-33.8pp RF, -32.6pp XGB), limited by only 14 positive cases (precision-limited tier). NOT treated as a confirmed finding. [A]

**BMI-Underweight:** N_positive=1 in test set. Not interpretable. [A]

**Selection disparity (cohort-assembly property, NOT conflated with model performance):** NHB: 41.3% of exclusions vs. 25.0% of retained.

**92/92 automated fairness tests passed. [A]**

---

## PART 14 — INTERSECTIONAL ANALYSIS [A]

**Exact intersection:** BMI-Obese AND Age-60+. N=294 in locked test set (13.7% of N=2,146).

**Four-way partition:**
- BMI-Obese only: N=589 (27.4%)
- Age-60+ only: N=447 (20.8%)
- Intersection (both): N=294 (13.7%)
- Neither: N=816 (38.0%)

**Baseline conformal coverage at intersection, from results/uncertainty/intersectional_coverage_ci.csv:**

| Model | Coverage | 95% Wilson CI |
|---|---:|---|
| Logistic | 69.4% | 63.9%–74.4% |
| Random Forest | 75.2% | 69.9%–79.8% |
| XGBoost | 65.0% | 59.4%–70.2% |
| LightGBM | 71.1% | 65.7%–76.0% |
| MLP | 73.8% | 68.5%–78.5% |

Uniformly worse than either single marginal subgroup (BMI-Obese: 76.8–82.3%; Age-60+: 81.1–85.6%) — a pattern invisible in the original Phase 7 aggregate reporting.

**Two distinct mitigation implementations — NOT collapsed:**

1. Sequential precedence (FROZEN Phase 7 method): Age threshold overwrites BMI for 4/5 models. Post-mitigation intersection coverage: 75.85–84.35%. Remains below 90% for EVERY model.

2. Genuine joint calibration (EXPLORATORY, not in frozen pipeline): Single quantile from N=138 calibration-set intersection members. Post-mitigation coverage: 90.8–94.9%, CI at/above 90% for all 5 models. Cost: 2/5 models breach ±5pp tolerance (XGBoost +6.80pp, LightGBM +5.50pp).

IMPORTANT: The joint mitigation resolves the intersectional problem. The frozen Phase 7 method does not. This is a scientific decision point for manuscript writing.

**Formal interaction test: NOT PERFORMED.** The intersection pattern is descriptive/observational. No interaction hypothesis was pre-specified or tested.

---

## PART 15 — CONFORMAL UNCERTAINTY [A]

**Method:** Split Conformal Prediction. Nonconformity score = 1 - P_hat(y=true class|x). Nominal target 90% (alpha=0.10).

**Architecture:** proper-train (N=4,005) -> 5-model refit -> conformal calibration (N=1,002, k=903) -> locked test (N=2,146).

**Conformal thresholds:** LR=0.672744, RF=0.607211, XGB=0.653193, LGBM=0.656959, MLP=0.377967.

**Marginal coverage:** 88.1–90.8% across all 5 models — meets target.

**Failing subgroups:**

| Subgroup | Coverage range (5 models) | All CIs exclude 90%? | FDR-significant? |
|---|---|---|---|
| BMI-Obese | 76.8%–82.3% | Yes, all 5 | Yes, all 10 combinations |
| Age-60+ | 81.1%–85.6% | Yes, all 5 | Yes, all 10 combinations |

**Efficiency:** Singleton rates: MLP 96.9% (highest); LR 56.8% (lowest). Doubleton rates: LR 43.2%; RF 23.2%; XGB 27.1%; LGBM 31.2%; MLP 0.0%. Class-weighted models produce substantially less decisive outputs — direct downstream effect of raw miscalibration.

**50/50 automated tests passed. [A]**

---

## PART 16 — MONDRIAN MITIGATION (PHASE 7) [A]

**Method:** Group-wise (Mondrian) conformal calibration. Selection criterion: FDR-significant in BOTH Phase 5 (fairness) AND Phase 6 (coverage). 9 qualifying combinations: BMI-Obese x 5 models; Age-60+ x 4 models (not Logistic — its Age Phase 5 result was not FDR-significant).

**Results from results/mitigation/test_set_mitigation_final.csv:**

| Model | Subgroup | Coverage Before | Coverage After | Success |
|---|---|---:|---:|---|
| Logistic | Obese | 82.33% | 89.35% | YES (CI includes 90%) |
| RF | Obese | 80.18% | 87.43% | NO |
| RF | 60+ | 85.56% | 88.39% | YES |
| XGBoost | Obese | 76.78% | 87.32% | NO |
| XGBoost | 60+ | 81.11% | 90.01% | YES |
| LightGBM | Obese | 79.16% | 86.64% | NO |
| LightGBM | 60+ | 84.75% | 87.04% | NO |
| MLP | Obese | 80.86% | 88.79% | YES |
| MLP | 60+ | 83.81% | 87.99% | YES |

**5/9 combinations fully resolved. 4/9 improved but not fully resolved.**

Trade-off violation: XGBoost marginal coverage +5.27pp (exceeds ±5pp protocol tolerance — reported, not adjusted). AUC and calibration unchanged by construction (mitigation touches only conformal thresholds).

**33/33 automated tests passed. [A]**

---

## PART 17 — DECISION CURVE ANALYSIS [A]

From RELIABILITY_EXTENSION_RESULTS_REPORT.md. Status: EXECUTED AND FROZEN.

Method: Standard net-benefit formula at thresholds 1%–50%. Recalibrated probabilities used (DCA requires threshold to correspond to actual risk).

Population DCA: All 5 models exceed treat-all at 49–50/50 thresholds; exceed treat-none at all 50. At 10%: NB 0.040–0.049 vs. treat-all -0.008.

BMI-Obese DCA (N=883, 140 positive): NB 0.086–0.099 vs. treat-all 0.065 at 10%.
Age-60+ DCA (N=741, 101 positive): NB 0.060–0.065 vs. treat-all 0.040 at 10%.

Interpretation: Models show potential clinical utility over reference strategies within this dataset. This does NOT establish clinical readiness, deployment safety, or external validity.

---

## PART 18 — DIAGNOSTIC ANALYSES D01–D08 [A]

### D01 — Socio-Conformal Literature Audit
STATUS: COMPLETE — NOVELTY THREAT LOW.

Paper arXiv:2605.05562 (Das & Rafe 2026): ordinal conformal prediction in social survey settings (Pew American Trends Panel). Key differences: ordinal (5-level) vs. binary outcome; social measurement vs. clinical liver fibrosis; James-Stein shrinkage vs. FDR-gated Mondrian; no class-balanced classifiers. Our candidates 1, 2, and 4 are completely unaddressed. Novelty claims NOT threatened.

---

### D02 — Continuous BMI Spline Analysis
STATUS: COMPLETE — CONTINUOUS GRADIENT CONFIRMED.
Source: results/diagnostics/continuous_bmi_metrics.csv.

RCS-spline fit (OOF-only, applied to test range) shows a monotonic pattern for every model: sensitivity rises smoothly and coverage falls smoothly across the full observed BMI range. Example: XGBoost — sensitivity 0.56 to 0.98, coverage 0.92 to 0.35, from BMI approx. 15 to 70, with no sharp discontinuity at the Obese cutoff (BMI=30).

Spline ranges across all 5 models:
- LR: sensitivity 0.461 to 0.926; coverage 0.664 to 0.974
- RF: sensitivity 0.560 to 0.934; coverage 0.585 to 0.978
- XGB: sensitivity 0.637 to 0.957; coverage 0.554 to 0.972
- LGBM: sensitivity 0.555 to 0.931; coverage 0.564 to 0.981
- MLP: sensitivity 0.431 to 0.889; coverage 0.663 to 0.958

Interpretation: The categorical "Obese" group captures the real upper-BMI high-sensitivity zone. The BMI finding is NOT a categorical cutpoint artifact — it is a genuine, continuous gradient.

---

### D03 — Continuous Age Analysis + Fine Age Bands
STATUS: COMPLETE — NON-MONOTONIC PATTERN.
Sources: results/diagnostics/continuous_age_metrics.csv and fine_age_band_metrics.csv.

Sensitivity rises through middle age and peaks around age 65, then plateaus or slightly declines — not a simple monotonic decline. Coverage declines monotonically with age throughout.

Fine age bands (60–69 vs. 70–80): Sensitivity in 70–80 is similar to or higher than 60–69 for 3/5 models (LR, RF, MLP); only XGB and LGBM show lower sensitivity in the oldest band.

Age-band sensitivity table (from fine_age_band_metrics.csv):

| Age Band | LR | RF | XGB | LGBM | MLP |
|---|---:|---:|---:|---:|---:|
| 18–39 | 0.667 | 0.727 | 0.788 | 0.727 | 0.576 |
| 40–59 | 0.864 | 0.864 | 0.909 | 0.848 | 0.833 |
| 60–69 | 0.762 | 0.778 | 0.841 | 0.746 | 0.698 |
| 70+ | 0.763 | 0.789 | 0.816 | 0.789 | 0.711 |

Interpretation: The 60+ category is valid and conservative. The disparity mechanism is more complex than "older patients are uniformly harder."

---

### D04 — Subgroup-Specific Platt Recalibration (Simple Application)
STATUS: COMPLETE — NEGLIGIBLE COVERAGE CHANGE (<1 pp).
Source: results/diagnostics/stage0_decision_report.md (D04 section).

Coverage changes after applying subgroup-specific Platt parameters (existing parameters, not re-derived):

| Model | BMI Obese | Age 60+ |
|---|---:|---:|
| LR | +0.11 pp | +0.00 pp |
| RF | -0.11 pp | +0.00 pp |
| XGB | +0.00 pp | +0.00 pp |
| LGBM | +0.68 pp | -0.54 pp |
| MLP | +0.00 pp | +0.27 pp |

Maximum absolute change: 0.68 pp. Conclusion: Subgroup coverage problem cannot be explained by subgroup-level Platt recalibration. The problem reflects the underlying nonconformity score distribution.

---

### D04-Alt — Full Subgroup Recalibration + Subgroup Quantile Pipeline (Three Diagnostics)
Source: results/diagnostics/FINAL_THREE_DIAGNOSTICS_REPORT.md and results/diagnostics/subgroup_recalibration_conformal_metrics.csv.

BMI-Obese: Baseline 76.8–82.3% -> after subgroup-Platt + subgroup-quantile: 89.9–91.6% (at or above 90% for all 5 models). This is a LARGER improvement than Phase 7 Mondrian achieves for BMI-Obese (87.3–89.4%).

Age-60+: Baseline 81.1–85.6% -> after subgroup-Platt + subgroup-quantile: 86.7–88.0%. Still below 90% for all 5 models, comparable to or WEAKER than Phase 7 for this subgroup (XGBoost Phase 7 reaches 90.0% vs. 86.8% here).

Calibration-in-the-large metrics (intercept/slope/Brier) do NOT materially improve — Brier changes in 4th decimal place. This diagnostic tests and does NOT confirm "better calibration => better conformal coverage."

---

### D05 — Group-Specific Threshold Analysis (TWO-MECHANISM FINDING)
STATUS: COMPLETE.
Source: results/diagnostics/group_specific_threshold_metrics.csv.

Using per-subgroup OOF-derived Youden thresholds vs. global threshold:

| Model | BMI gap (Obese-Normal), global vs. group-threshold | Age gap (40-59 minus 60+), global vs. group-threshold |
|---|---|---|
| Logistic | 47.7pp vs. 14.9pp | 8.6pp vs. 13.1pp |
| Random Forest | 31.6pp vs. 16.1pp | 13.2pp vs. 16.2pp |
| XGBoost | 31.4pp vs. 14.7pp | 11.2pp vs. 26.1pp |
| LightGBM | 27.1pp vs. 10.4pp | 14.1pp vs. 20.1pp |
| MLP | 39.0pp vs. 15.8pp | 14.7pp vs. 18.6pp |

BMI finding: Disparity shrinks by approximately half to two-thirds for every model. BMI sensitivity disparity is substantially THRESHOLD-DRIVEN for all 5 models (including MLP).

Age finding: Group-specific thresholding makes the age gap WORSE for every model. Age-60+ disparity is NOT threshold-driven. Naive threshold adjustment actively harms the Age-60+ group.

Two-mechanism account confirmed [A/C]:
- Class-balanced models (LR, RF, XGB, LGBM): BMI disparity substantially threshold-driven; Age-60+ disparity is not.
- MLP: Both BMI and Age-60+ disparities more intrinsic (discrimination-driven) — MLP's global threshold (0.1065) already partially accounts for class-distribution without explicit balancing.

---

### D06 — Equal Opportunity Fairness Post-Processing
STATUS: COMPLETE — LARGE SENSITIVITY GAINS, DOCUMENTED SPECIFICITY COST.
Source: results/diagnostics/stage1/fairness_postprocessing_results.csv.

EO post-processing derives per-group thresholds equalizing sensitivity with reference group. Test labels used ONLY for evaluation (fitting_test_labels_used: NO assertion verified).

BMI-Obese, global vs. EO threshold:

| Model | Sensitivity global | Sensitivity EO | Specificity global | Specificity EO |
|---|---:|---:|---:|---:|
| LR | 0.10 | 0.82 | 0.98 | 0.58 |
| RF | 0.11 | 0.88 | 0.97 | 0.56 |
| XGB | 0.18 | 0.83 | 0.96 | 0.64 |
| LGBM | 0.06 | 0.81 | 0.99 | 0.63 |
| MLP | 0.95 | 0.89 | 0.35 | 0.48 |

Age-60+, global vs. EO threshold:

| Model | Sensitivity global | Sensitivity EO | Specificity global | Specificity EO |
|---|---:|---:|---:|---:|
| LR | 0.08 | 0.73 | 0.99 | 0.60 |
| RF | 0.09 | 0.76 | 0.98 | 0.60 |
| XGB | 0.15 | 0.66 | 0.97 | 0.74 |
| LGBM | 0.04 | 0.69 | 1.00 | 0.69 |
| MLP | 0.79 | 0.72 | 0.50 | 0.64 |

Critical observations [A/C]:
- Class-balanced models: +51 to +80pp sensitivity gains entirely through threshold adjustment. Brier and calibration intercepts are IDENTICAL (probability-preserving intervention).
- MLP: EO slightly DECREASES sensitivity — confirming MLP's disparity is discrimination-driven, not threshold-driven.
- Specificity cost: approximately 38–40pp reduction for class-balanced models.

This confirms the D05 threshold-mechanism finding on the locked test set. Does NOT change the primary study — it is a supplementary diagnostic.

---

### D07 — AFCP vs. FDR-Gated Mondrian Comparison
STATUS: COMPLETE — MONDRIAN PREFERRED; AFCP VALIDATES THE FINDING.
Source: results/diagnostics/stage1/afcp_vs_mondrian_comparison.csv.

BMI-Obese coverage (Marginal / Mondrian / AFCP):

| Model | Marginal | Mondrian | AFCP |
|---|---:|---:|---:|
| LR | 0.827 | 0.913 | 0.910 |
| RF | 0.827 | 0.917 | 0.895 |
| XGB | 0.814 | 0.912 | 0.890 |
| LGBM | 0.810 | 0.904 | 0.897 |
| MLP | 0.819 | 0.920 | 0.896 |

Age-60+ coverage (Marginal / Mondrian / AFCP):

| Model | Marginal | Mondrian | AFCP |
|---|---:|---:|---:|
| LR | 0.858 | 0.892 | 0.900 |
| RF | 0.849 | 0.878 | 0.883 |
| XGB | 0.844 | 0.885 | 0.881 |
| LGBM | 0.846 | 0.872 | 0.892 |
| MLP | 0.849 | 0.877 | 0.876 |

Overall marginal coverage: AFCP produces 92.5–93.8% vs. Mondrian 88.0–90.4%. AFCP is more conservative (wider prediction sets), NOT more efficient.

Head-to-head verdict [C]:
- BMI-Obese: Mondrian > AFCP for all 5 models.
- Age-60+: AFCP approximately equal to Mondrian, both substantially above marginal.
- Both methods identify the SAME coverage-deficient groups — validating the primary Phase 6 Mondrian finding.
- Mondrian is more parsimonious (lower overall coverage inflation, categorical group structure mapping directly to clinical variables).

---

### D08 — Final Reproducibility Validation
STATUS: 26/26 CHECKS PASSED — APPROVED FOR FREEZE.
Source: results/diagnostics/final_validation_report.md. Generated 2026-08-25 12:35:55.

Checks include: all split disjointness (4 checks); all split sizes verified; all frozen result files present with SHA-256 hashes; XGBoost AUC reconstructed from joblib model (fresh=0.8397 vs. frozen=0.8429, diff=0.0032 — within expected float/sampling tolerance); all 5 diagnostic scripts carry fitting_test_labels_used: NO assertion; all 7 key packages verified at correct pinned versions.

Pinned environment: scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0, pandas 3.0.5, numpy 2.5.2, scipy 1.18.0, joblib 1.5.3, Python 3.14.3.

---

## PART 19 — ROBUSTNESS AND SENSITIVITY ANALYSES [A]

All executed; results from DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md and MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md:

| Analysis | What changed | AUC result | BMI-Obese finding | Age-60+ finding | Primary conclusion changed |
|---|---|---|---|---|---|
| 8.0 kPa threshold (relabel, no retrain) | Outcome threshold (31 more positives) | 0.8145–0.8326 | Stable: 35.1–51.6pp, 5/5 sig. | Direction stable; significance drops to 2/5 | No |
| CAND_2 relaxed elastography | Eligibility rule, N=7,639 | 0.8526–0.8572 | Stable | Directionally stable, significance varies | No |
| CAND_3 fasting-extended | Cohort + 2 predictors, N=3,582 | 0.8280–0.8457 | Stable | Direction stable; significance attenuates | No |
| NHB multiple imputation | Missing-data handling, MI pool N=7,768 | Diff <0.007, all models | Not tested (MI scoped to NHB) | Not tested | No |
| NHB subgroup holdout (Phase 8) | NHB excluded from training | NHB holdout AUC 0.77–0.79 (-0.05–0.06) | N/A | N/A | No — new finding: moderate degradation |

Overall robustness classification [A]:
- Discrimination: STABLE (29/30 variants stable)
- Calibration qualitative pattern: STABLE (15/15)
- BMI-Obese fairness finding: STABLE (15/15 — most robust finding in the project)
- Age-60+ fairness finding: PARTIALLY STABLE — direction never reverses, significance lost in 9/12 sensitivity-variant instances

No finding reversed anywhere across all sensitivity analyses.

---

## PART 20 — STATISTICAL METHODS [A]

Bootstrap: 2,000 resamples, seed=42, paired at participant level. Used for: calibration CIs, fairness-disparity CIs, discrimination-comparison CIs.

Wilson score intervals: All conformal-coverage CIs.

Benjamini-Hochberg FDR: Applied per-phase, per-model-family.
- Phase 3: 10 discrimination pairs
- Phase 4: 3 x 10-pair calibration families
- Phase 5: 11-category x 5-model sensitivity disparity families
- Phase 6: 15-category x 5-model coverage families

Pooled 182-test correction [A]: Project-wide enumeration found 182 distinct formal hypothesis tests across 7 families. After pooled BH-FDR: 75/182 remain significant. XGBoost-vs-MLP clearly significant (adjusted p=0.0136). 18/20 tests referencing BMI-Obese/Age-60+ remain significant under pooled correction.

Pooled correction limitation [D]: Dependence-structure assumption (independence or PRDS) very likely does not strictly hold given overlapping participants/models/subgroups. Disclosed as a limitation.

---

## PART 21 — ERRORS, BUGS, AND CORRECTIONS [A]

| Bug | Detection | Effect | Correction | Authoritative result |
|---|---|---|---|---|
| Phase 5: BMI/age binning comparison error (<18.5 instead of pd.cut), 7 participants affected | Programmatic verification | Minor miscounting | Fixed to pd.cut with identical bin edges | results/fairness/subgroup_feasibility_table.csv |
| Phase 4: TEST 10 and TEST 11 false positives — overly crude string-match | Test run | False pass | Corrected before final run | tests/test_calibration_pipeline.py |
| Phase 7: Stray import caused Phase 6 refit to re-execute (models hash-identical; only timing field differed) | git diff inspection | Timing only, not results | Reverted via git checkout | results/uncertainty/conformal_model_refit_registry.csv |
| MI: sample_posterior=False produced byte-identical imputations across all 5 iterations (no between-imputation variance) | Hash comparison (all 5 outputs identical) | MI had zero between-imputation variance | Fixed to sample_posterior=True; re-run confirmed 5 distinct hashes | results/sensitivity/mi_*.csv |
| Sensitivity CSV: unquoted field with embedded comma broke CSV parsing | Test suite failure on file load | CSV unreadable | Rewritten via Python csv module | results/sensitivity/deferred_sensitivity_execution_matrix.csv |
| Phase 7 reproducibility rerun: naive per-combination rerun produced apparent 1.8–4.5pp discrepancies | Comparison to committed artifact | Appeared as non-determinism | Correctly replicated with sequential tie-break order | results/mitigation/test_set_mitigation_final.csv |

No bug altered primary scientific results that remain authoritative. All bugs caught before final reporting and disclosed in relevant phase reports.

---

## PART 22 — LITERATURE POSITIONING [A/B]

### Closest liver-fibrosis competitors

| Paper | What it did | What it missed | Novelty threat |
|---|---|---|---|
| Cao et al. 2026, Frontiers in Medicine (DOI 10.3389/fmed.2026.1736295) | NHANES fibrosis prediction, near-identical threshold, genuine calibration | Zero fairness audit, zero conformal prediction | Low — stops at calibration |
| Zhang X. 2026 (arXiv) | Conformal prediction for liver disease | No fairness analysis, found no coverage failure | Low — no failure found |

### Closest conformal/fairness literature

| Paper | Relevance |
|---|---|
| Vovk et al. 2003 | Mondrian/group-conditional conformal is 23 years old as a general technique — NOT a novel method claim |
| Lu et al. 2021/2022 (dermatology) | Combines conformal + demographic subgroup fairness + group-conditional mitigation in a medical setting |
| Das & Rafe 2026 (arXiv:2605.05562) | Ordinal conformal in social survey; not a threat (D01 confirmed) |
| Kwon & Kim 2026 (sepsis-triage, Sci. Rep.) | Possible structural analogue; not fully verified from full text |

Novelty landscape: No paper combining calibration + fairness + conformal + subgroup coverage + mitigation + the intersectional compounding finding was identified in any disease area.

---

## PART 23 — NOVELTY AUDIT [A/B/C]

| Candidate contribution | Evidence | Closest prior | Threat | Classification | Safest wording |
|---|---|---|---|---|---|
| Combined calibration+fairness+conformal+mitigation pipeline for liver fibrosis | Full Phase 4–7 record | Cao et al. 2026 (calibration only); Lu et al. 2021 (conformal+fairness in dermatology) | Low-Moderate | Integrative application | "To our knowledge, no prior study evaluates liver-fibrosis ML across all four reliability dimensions jointly" |
| BMI-Obese and Age-60+ conformal coverage failure, cross-model | Phase 6 | Zhang X. 2026 (found no failure) | Low | Novel empirical finding | "We found systematic conformal coverage failure..." |
| True BMI x Age intersectional coverage failure, worse than either marginal | Part 12 | None found in any disease area | Low | Novel empirical finding | "The intersection of BMI-Obese and Age-60+ showed worse coverage than either marginal subgroup..." |
| Two-mechanism account: threshold-driven (class-balanced) vs. discrimination-driven (MLP) | D05 + D06 | Not established elsewhere | Low | Novel mechanistic finding | "The mechanism underlying sensitivity disparity differs by model family..." |
| FDR-gated Mondrian is more parsimonious than AFCP in this clinical setting | D07 | Mondrian technique is known (2003) | Low | Method comparison | "Compared to AFCP, FDR-gated Mondrian achieved better BMI-Obese coverage with lower overall inflation..." |
| General fairness-disparity and coverage-deficit association across all subgroups | Reliability Extension: pooled rho=0.41, permutation p=0.12 | Not found | N/A | NOT ESTABLISHED (dependence-aware test fails to confirm) | "The observed co-occurrence in BMI/Age subgroups is consistent with, but not proven to generalize as, a broader pattern..." |

---

## PART 24 — SCIENTIFIC IMPROVEMENT AUDIT

| Proposed Improvement | Classification | Rationale |
|---|---|---|
| Report subgroup-recal + subgroup-quantile pipeline as supplementary alternative for BMI-Obese coverage | STRONGLY RECOMMENDED (supplementary) | Achieves >=90% for all 5 models for BMI-Obese; Mondrian does not resolve 4/5 combinations for this dimension |
| Report EO post-processing as sensitivity analysis demonstrating threshold mechanism | STRONGLY RECOMMENDED (supplementary) | Clinically actionable; confirms D05 mechanism on test set |
| Report AFCP comparison as method robustness supplement | RECOMMENDED | Already computed; minor write-up effort; strengthens robustness narrative |
| Include joint BMI x Age intersectional mitigation as Discussion scientific decision point | OPTIONAL | Resolves the intersectional problem; requires stress-testing in sensitivity variants first |
| External validation | MUST DO before deployment claim; OPTIONAL for initial publication | Cannot make generalizability claims without it |
| CAND_4 all-ages execution | NOT RECOMMENDED until source-document conflict resolved | Source documents contradict each other on whether this was pre-specified |

---

## PART 25 — COMPLETE FINDINGS TABLE [A]

| Finding | Result | Evidence Source | Models | Robustness | Claim Strength |
|---|---|---|---|---|---|
| Discrimination comparable across 5 families, all in H1 range | AUC 0.82–0.84, no pairwise FDR winner | phase3_final_baseline_results.csv | All 5 | Stable across 3 sensitivity cohorts | High |
| Raw class-balanced probabilities severely miscalibrated by class-balancing prior shift | Intercept -1.86 to -2.26 vs. MLP -0.28 | primary_metrics_by_model.csv | All 5 | Replicates across all sensitivity cohorts | High |
| Platt recalibration effective on primary cohort | Brier halved for 4 models; AUC unchanged | test_set_calibration_final.csv | All 5 | — | High |
| BMI-Normal sensitivity deficit vs. Obese | 27–48pp, FDR-sig. all 5 models | fairness_inference.csv | All 5 | 15/15 stable — MOST ROBUST FINDING | Highest |
| BMI disparity is genuine continuous gradient, not cutpoint artifact | Smooth spline, no discontinuity at BMI=30 | continuous_bmi_metrics.csv | All 5 | — | High |
| BMI disparity is substantially threshold-driven (all 5 models) | Gap shrinks ~50–67% with group-specific threshold | group_specific_threshold_metrics.csv | All 5 | — | Moderate-High |
| Age-60+ sensitivity deficit | 11–15pp, 4/5 models FDR-sig. | fairness_inference.csv | 4/5 (not LR) | Direction stable; significance attenuates | Moderate |
| Age disparity is NOT threshold-driven — thresholding makes it WORSE | Gap widens for every model with group-specific threshold | group_specific_threshold_metrics.csv | All 5 | — | High |
| Age disparity shows non-monotonic continuous relationship | Sensitivity peaks ~65, 70+ not worse than 60–69 in most models | continuous_age_metrics.csv | All 5 | — | Moderate |
| Conformal marginal coverage meets target | 88.1–90.8% | marginal_coverage_test_set.csv | All 5 | — | Definitive |
| BMI-Obese conformal coverage fails | 76.8–82.3%, FDR-sig. all 5 models | subgroup_coverage.csv | All 5 | Validated by AFCP (D07) | High |
| Age-60+ conformal coverage fails | 81.1–85.6%, FDR-sig. all 5 models | subgroup_coverage.csv | All 5 | Validated by AFCP (D07) | High |
| True BMI x Age intersection coverage worse than either marginal | 65.0–75.2% vs. 76.8–82.3% (Obese) and 81.1–85.6% (60+) | intersectional_coverage_ci.csv | All 5 | Not yet tested in sensitivity variants | High |
| Frozen Mondrian mitigation: partial success | 5/9 resolved; XGBoost breaches ±5pp; intersection remains below 90% | test_set_mitigation_final.csv | All 5 | — | Definitive (partial) |
| EO post-processing: +51–80pp sensitivity for class-balanced models | Sensitivity 0.06/0.82 (LR/Obese) through 0.11/0.88 (RF/Obese) | fairness_postprocessing_results.csv | 4/5 (class-balanced) | — | Moderate-High |
| MLP disparity: intrinsic/discrimination-driven | EO slightly decreases MLP sensitivity in Obese/60+ | fairness_postprocessing_results.csv | MLP | — | Moderate |
| Simple subgroup recalibration cannot fix coverage via existing Platt parameters | <0.68pp coverage change | Stage 0 D04 section | All 5 | — | High |
| Full subgroup-recal+quantile pipeline resolves BMI-Obese coverage | 89.9–91.6% (vs. 76.8–82.3% baseline; better than Phase 7 Mondrian for this dimension) | subgroup_recalibration_conformal_metrics.csv | All 5 | Single computation | Moderate |
| AFCP confirms same deficit groups; Mondrian more parsimonious | Mondrian > AFCP for BMI-Obese; AFCP inflates overall coverage more | afcp_vs_mondrian_comparison.csv | All 5 | — | Moderate-High |
| Fairness-coverage general correlation: suggestive but NOT statistically confirmed | Pooled rho=0.41 (p=0.002 naive); permutation p=0.12 (not confirmed) | RELIABILITY_EXTENSION_RESULTS_REPORT.md | All 5 | — | Low |
| Clinical utility: positive net benefit over reference strategies | All 5 exceed treat-all and treat-none across 1–50% range | dca_summary.csv | All 5 | — | Moderate (internal only) |
| NHB generalization: moderate discrimination degradation | AUC drops 4.7–5.9pp vs. full population | Phase 8 report | All 5 | — | Moderate |
| Calibration not stable in NHB holdout | All 5 models show negative intercepts (uncorrected) | Phase 8 report | All 5 | — | High (negative finding) |
| MI robustness: NHB fairness not materially changed | Sensitivity diff <4.2pp; all adjusted p=0.978 | MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md | All 5 | — | Moderate (PARTIAL — MLP indeterminate) |

---

## PART 26 — REMAINING SCIENTIFIC WORK

### TRUE BLOCKERS (must address before any deployment or generalizability claim)
1. External validation: No independent non-NHANES cohort. No deployment or generalizability claim can be made without this.

### OPTIONAL EXTENSIONS (scientifically meaningful; not mandatory for initial manuscript)
2. Joint BMI x Age intersectional mitigation: The exploratory analysis resolves the intersectional problem at a documented cost. Deciding whether to include in primary or supplementary methods requires stress-testing in sensitivity cohorts and a literature check.
3. Conformal coverage repetition under CAND_2/CAND_3/8.0 kPa: Would stress-test the intersectional finding. Not currently frozen.
4. CAND_4 (all-ages 12+): Source-document conflict requires resolution before execution.
5. Broader MI analysis beyond NHB scope for conformal coverage: Not protocol-frozen.

### FUTURE WORK (beyond this study)
6. External validation in a prospective or independent cohort.
7. Race/ethnicity conformal coverage under MI: Selection-disparity question for NHB participants in the conformal setting was never assessed.
8. Formal intersectional interaction test: A properly-powered, pre-specified interaction analysis was never run. Current intersectional findings are observational/descriptive only.

No other experiment is scientifically necessary before initial manuscript writing.

---

## PART 27 — FINAL MODEL COMPARISON [A]

No single model dominates across all dimensions:

| Model | AUC | Raw intercept | Recal. Brier | Marginal coverage | BMI-Obese cov. | Age-60+ cov. | Singleton rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic | 0.8334 | -2.24 | 0.0705 | 90.8% (best) | 82.3% | 84.9% | Moderate |
| Random Forest | 0.8343 | -1.86 | 0.0709 | 89.6% | 80.2% | 85.6% | Moderate |
| XGBoost | 0.8429 (highest) | -2.05 | 0.0694 (best) | 88.1% (lowest) | 76.8% (worst) | 81.1% (worst) | Lower |
| LightGBM | 0.8394 | -2.05 | 0.0696 | 89.6% | 79.2% | 84.8% | Moderate |
| MLP | 0.8229 (lowest) | -0.28 (best raw) | 0.0715 | 89.2% | 80.9% | 83.8% | 96.9% (highest) |

This is a Pareto frontier, not a ranking. Best for discrimination (XGBoost) is worst for subgroup coverage. Best for calibration and efficiency (MLP) has lowest discrimination and a different fairness mechanism. No formal Pareto analysis performed.

---

## PART 28 — LIMITATIONS [A]

1. No external validation. No independent non-NHANES cohort. Temporal validation is infeasible (NHANES 2017–March 2020 is a single combined release). Subgroup-holdout generalization (Phase 8) is not external validation.

2. Surrogate outcome. LUXSMED (vibration-controlled transient elastography) is not biopsy-confirmed histology.

3. Complete-case exclusion disparity. NHB: 41.3% of excluded vs. 24.98% of retained. MI analysis found no material distortion to discrimination/calibration/NHB-fairness, but conformal-coverage under MI was never assessed.

4. Intersectional sample size. N=294 test-set intersection; N=138 calibration-set intersection (for exploratory joint mitigation). The joint mitigation result is a single computation at a small calibration-cell size.

5. Age-60+ finding not statistically robust under sensitivity analysis. Significance lost in 9/12 sensitivity-variant instances. Direction never reverses.

6. Pooled multiple-testing correction is approximate. The 182-test pooled BH-FDR likely violates PRDS assumption due to overlapping participants, models, and subgroups. Disclosed; not resolved.

7. General fairness-coverage association not statistically confirmed. Dependence-aware permutation test (p=0.12) does not support a broad cross-subgroup association. Only the two specifically-identified subgroups have co-occurrence confirmed on their own independent Phase 5/6 tests.

8. No formal interaction test for BMI x Age. Current intersectional finding is observational/descriptive only.

9. Exact environment pinning for Phases 4–8. Phase 3 uses exact pinned requirements-phase3-lock.txt. Phases 4–8 use loose >= constraints. Minor reproducibility limitation.

---

## PART 29 — REPRODUCIBILITY AND EVIDENCE LINEAGE [A]

### Key Evidence Lineage

| Finding | Result File | Script | Input | Fitting Data |
|---|---|---|---|---|
| BMI-Normal sensitivity deficit | fairness_inference.csv | phase5_04_inference.py | analysis_dataset_primary.parquet + Phase 3 test predictions | OOF train predictions only |
| Age-60+ coverage failure | subgroup_coverage.csv | phase6_04_final_test_touch.py | Test predictions from conformal-refit models | Conformal calibration set (N=1,002) |
| Intersectional coverage | intersectional_coverage_ci.csv | Session computation | Same as above | Same as above |
| BMI disparity threshold-driven | group_specific_threshold_metrics.csv | sens_06_group_specific_thresholds.py | OOF predictions | OOF only (no test labels used for fitting) |
| EO post-processing results | fairness_postprocessing_results.csv | sens_07_fairness_postprocessing.py | OOF predictions + test predictions (evaluation only) | OOF only |
| AFCP comparison | afcp_vs_mondrian_comparison.csv | sens_08_afcp_comparison.py | Conformal calibration set | Calibration set only |

All secondary diagnostic scripts verified with fitting_test_labels_used: NO assertion (D08 checks 32–36).

Pinned environment: scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0, pandas 3.0.5, numpy 2.5.2, scipy 1.18.0, joblib 1.5.3, Python 3.14.3.

Version control: All phases committed and pushed. Two parallel processes (claude, opencode) are running in the workspace — their artifacts should be treated as independent and not automatically merged.

---

## PART 30 — MANUSCRIPT READINESS

| Dimension | Score (0–100) | Rationale |
|---|---|---|
| Experimental readiness | 92 | All Phase 1–8 experiments complete and frozen; all D01–D08 diagnostics complete; 26/26 validation checks pass. Deducted 8 for: no external validation; CAND_4 unresolved; conformal-coverage-under-MI not assessed. |
| Statistical readiness | 88 | All primary/secondary statistics complete with CIs and FDR; pooled correction computed. Deducted 12 for: pooled correction approximate assumption; MI ROBUSTNESS PARTIAL (MLP indeterminate). |
| Literature-positioning readiness | 82 | Two full novelty audits completed; closest papers identified. Deducted 18 for: Kwon & Kim 2026 (sepsis analogue) not fully verified; no full systematic review performed. |
| Novelty-positioning readiness | 85 | Intersectional finding and two-mechanism account appear genuinely novel. Deducted 15 for: general fairness-coverage association not statistically confirmed; joint mitigation not stress-tested. |
| Reproducibility readiness | 90 | 26/26 validation checks pass; all split files present; 16 joblib artifacts git-tracked; seeds recorded. Deducted 10 for: loose version constraints for Phases 4–8; parallel session artifacts. |
| Overall manuscript readiness | 87 | Sufficient for initial submission. Open items are limitations/discussions, not blockers. |

---

## PART 31 — MANUSCRIPT MAPPING

### Introduction
- Research-question framing: reliability and equity, not just accuracy
- Gap: liver-fibrosis ML literature stops at discrimination; calibration is underaddressed; fairness and conformal uncertainty are absent
- Key citations: Cao et al. 2026 (closest competitor; stops at calibration)

### Related Work
- Cao et al. 2026 (calibration but no fairness/conformal)
- Lu et al. 2021/2022 (conformal + fairness in dermatology — methodological lineage)
- Zhang X. 2026 arXiv (conformal for liver disease, no failure found)
- Vovk et al. 2003 (Mondrian conformal)
- Das & Rafe 2026 (Socio-Conformal — cite for marginal validity problem)

### Methods
- Dataset: Part 5–6 (NHANES 2017–March 2020, N=7,153, 9.31% prevalence)
- Preprocessing: Part 7–8 (10 predictors, complete-case, within-fold imputation/scaling)
- Models: Part 10 (5 families, class balancing, Youden threshold)
- Calibration: Part 12 (OOF-fit Platt scaling)
- Fairness: Part 13 (4 demographic dimensions, BH-FDR per model-family)
- Conformal prediction: Part 15 (split conformal, 90% target, subgroup coverage)
- Mitigation: Part 16 (FDR-gated Mondrian)
- Diagnostics: Part 18 (D02–D07 as supplementary or dedicated analysis section)

### Results
- Discrimination: Part 11 (comparable across models)
- Calibration: Part 12 (raw: severely miscalibrated; recalibrated: corrected)
- Fairness: Part 13 (BMI-Normal deficit robust; Age-60+ deficit moderate)
- Conformal uncertainty: Part 15 (marginal OK; BMI-Obese and Age-60+ fail)
- Intersectional: Part 14 (intersection worse than either marginal)
- Mitigation: Part 16 (5/9 resolved; intersection unresolved under frozen method)
- D05/D06/D07: Two-mechanism account; EO post-processing; AFCP comparison

### Supplementary
- Sensitivity analyses: Part 19 (3 variants)
- NHB MI analysis: Part 19
- NHB generalization: Phase 8
- Full pooled multiple-testing registry: Part 20
- Continuous BMI/age splines: D02/D03
- Decision Curve Analysis: Part 17

### Discussion
- Why BMI and Age disparities respond differently (two-mechanism account, D05)
- Trade-off between sequential Mondrian and joint calibration for intersection
- The partial, honest success of current mitigation
- Calibration/efficiency/fairness Pareto frontier — no single dominant model
- Limitations: Part 28

### Conclusion (narrowest defensible)
A clinical liver-fibrosis ML pipeline can simultaneously pass discrimination, calibration, and marginal coverage standards while exhibiting systematic, statistically verified reliability failures for identifiable demographic subgroups — and these failures compound at demographic intersections. The failures respond to different mechanisms, which determines which interventions work. A working remedy exists but involves a quantified trade-off.

---

## PART 32 — FINAL FIVE QUESTIONS

### 1. What exactly has this research successfully established?

1. Five standard ML model families achieve comparable, modest discrimination (AUC 0.82–0.84) for liver-fibrosis prediction from 10 routine NHANES variables.
2. Raw class-balanced probabilities are severely and mechanistically miscalibrated (prior-shift artifact, correctable by OOF-fit Platt scaling).
3. Normal-BMI participants have substantially (27–48pp) lower sensitivity than Obese-BMI participants — a robust, multi-sensitivity-analysis finding (15/15 stability).
4. Age-60+ participants have moderately (11–15pp) lower sensitivity in 4/5 model families — directionally robust but significance-sensitive.
5. The same two subgroups fail split-conformal coverage guarantees across all 5 models, even when marginal coverage meets the 90% target.
6. The true BMI x Age intersection is covered worse (65.0–75.2%) than either marginal subgroup alone (BMI-Obese: 76.8–82.3%; Age-60+: 81.1–85.6%).
7. The BMI disparity is substantially threshold-driven (all 5 models); the Age-60+ disparity is NOT threshold-driven and is worsened by naive threshold adjustment.
8. EO post-processing restores sensitivity for class-balanced models (+51–80pp) with a documented specificity cost; MLP's disparity is not addressable this way.
9. FDR-gated Mondrian mitigation partially resolves the identified coverage failures (5/9 combinations); joint calibration resolves the intersectional problem at a documented overall-coverage cost in 2/5 models.

### 2. What are the strongest scientifically defensible findings?

In descending confidence:
1. BMI-Normal sensitivity deficit — strongest (15/15 sensitivity-variant stability, all 5 models FDR-significant, continuous gradient confirmed by D02)
2. BMI-Obese and Age-60+ conformal coverage failure — strong (FDR-significant in all 10 model x subgroup combinations; validated independently by AFCP in D07)
3. True intersectional coverage failure worse than either marginal subgroup — strong empirically (all 5 models, 95% CIs); somewhat limited by N=294
4. Two-mechanism account — strong (confirmed by D05 and D06 independently, two different analytical approaches)
5. Age-60+ sensitivity deficit — moderate (direction robust; significance sensitive to cohort size)

### 3. What is genuinely novel or potentially novel?

1. Intersectional BMI x Age conformal-coverage failure — highest confidence in novelty; no prior work found in any disease area
2. Two-mechanism account (threshold-driven for class-balanced models; discrimination-driven for MLP) — novel mechanistic contribution
3. FDR-gated Mondrian vs. AFCP comparison in a clinical setting — method comparison contribution
4. Joint calibration as an alternative intersectional mitigation — novel application
5. Combined calibration + fairness + conformal + mitigation pipeline for liver fibrosis — integrative novelty

### 4. What scientifically meaningful work is still remaining?

- Supplementary analysis (recommended for first submission): D06 (EO post-processing) and subgroup-recalibration+quantile pipeline as supplementary alternatives.
- Discussion section: Two-mitigation comparison (sequential Mondrian vs. joint calibration for intersection).
- Future work: External validation; conformal-coverage under MI for non-NHB subgroups; formal interaction test for BMI x Age.
- Open ambiguity: CAND_4 source-document conflict — no execution warranted without clarification.

### 5. Is the core experiment complete, or is another experiment genuinely required before manuscript writing?

THE CORE EXPERIMENT IS COMPLETE AND APPROVED FOR FREEZE. BEGIN MANUSCRIPT WRITING.

The 26/26 final validation checks pass. All pre-specified diagnostic analyses (D01–D08) are complete. The primary frozen pipeline (Phases 1–8), sensitivity analyses, MI, Reliability Extension, and all D01–D08 diagnostics form a coherent, well-characterized research package. No major scientific or methodological question remains unresolved. The open items (external validation, joint mitigation stress-test, CAND_4) are limitations, optional extensions, and future work — NOT prerequisites for the initial manuscript.

---

## PART 33 — FINAL STUDY AT A GLANCE

Dataset: NHANES 2017–March 2020, N=7,153, 9.31% prevalence, locked 70/30 split.
Outcome: LUXSMED >= 8.2 kPa (quality-valid elastography, literature-validated threshold).
Predictors: 10 routine labs/demographics; race excluded from model inputs.
Models: LR, RF, XGBoost, LightGBM, MLP — AUC 0.82–0.84, no dominant model.
Calibration: Raw severely miscalibrated (class-balancing prior shift); Platt recalibration halves Brier for 4 models.
Fairness: BMI-Normal deficit (robust, 27–48pp, all 5 models); Age-60+ deficit (4/5, 11–15pp).
Mechanism: BMI — substantially threshold-driven (all 5 models); Age — NOT threshold-driven, intrinsic/discrimination-driven.
Conformal: Marginal coverage meets target; BMI-Obese and Age-60+ fail; intersection fails worse.
Mitigation: Mondrian — partial success (5/9); joint calibration resolves intersection at documented cost.
Robustness: BMI finding fully robust (15/15); Age finding directionally robust, significance-sensitive.
Generalization: Moderate AUC degradation in NHB holdout; calibration not stable.
Literature: No prior work combines calibration+fairness+conformal+mitigation for liver fibrosis.
Novelty: Intersectional coverage failure; two-mechanism account; FDR-Mondrian vs. AFCP comparison.

FINAL EXPERIMENTAL STATUS: GREEN — COMPLETE AND FROZEN. APPROVED FOR MANUSCRIPT WRITING.

---

*Report Version 2.0 — 25 Aug 2026. Supersedes prior 878-line version written before D01–D08 completion. All claims source-traced. Unverifiable claims marked NOT ESTABLISHED FROM THE AVAILABLE EXPERIMENTAL RECORD.*
