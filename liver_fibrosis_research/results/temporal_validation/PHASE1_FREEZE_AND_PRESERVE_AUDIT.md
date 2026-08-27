# Phase 1 — Freeze and Preserve Audit

## Final Audit Status

**PHASE 1 = COMPLETE — RESEARCH STATE FROZEN**

This is an authoritative, read-only preservation snapshot and audit report. No scientific calculations, model re-executions, drift analyses, refitting, recalibration, threshold adjustments, conformal parameter changes, M4b $N_0$ tuning, or experiment reruns were performed.

---

## 1. Repository Preservation & Git Verification

The primary research codebase, primary datasets, primary model artifacts, primary results, and original reports were verified as strictly read-only and un-modified.

- **`git status` output:** On branch `main`, branch up to date with `origin/main`. No tracked files modified. Untracked directory additions present in designated temporal locations only (`data/processed/temporal_validation/`, `results/temporal_validation/`).
- **`git diff --name-only` output:** Strictly empty (`0` lines). No primary tracked research file was modified or altered by this phase.
- **Result Overwrite Check:** No primary result or temporal validation result file was overwritten, truncated, or modified.
- **Governing Standard:** The original 2017–2020 experiment, completed 2021–2023 temporal cohort/predictions, Phase 3 evaluation, and Phase 4 synthesis are designated frozen authoritative references for all downstream phases.

---

## 2. Documented Cohort Sizes & Partition Integrity

### 2.1 Primary 2017–2020 Benchmark Cohort (CAND_1)
- **Total Analytic Cohort (CAND_1):** $N = 7,153$ | Positives = $666$ | Negatives = $6,487$ | Prevalence = **9.31%** (`LUXSMED >= 8.2 kPa`)
- **Primary Training Partition:** $N = 5,007$ (466 positives, 9.31%)
- **Primary Locked Test Partition:** $N = 2,146$ (200 positives, 9.32%)
- **Proper-Train Refit Partition:** $N = 4,005$ (373 positives, 9.31%)
- **Conformal Calibration Partition:** $N = 1,002$ (93 positives, 9.28%)

### 2.2 Temporal Validation Cohort (NHANES 2021–2023)
- **Total Temporal Cohort:** $N = 4,910$ | Positives = $563$ | Negatives = $4,347$ | Prevalence = **11.4664%** ($563 / 4,910$)
- **Participant ID Linkage:** 100% exact SEQN matching; 0 ID leakage across partitions; 0 input file modification.

---

## 3. Model Artifacts & SHA-256 Hashes

The frozen five-model design, frozen Youden decision thresholds, frozen Phase 6 split-conformal nonconformity quantiles, and frozen $N_0^* = 0$ M4b joint conformal configuration were retained without modification.

### Phase 6 Conformal Refit Model Artifact Hashes (SHA-256)
- **Logistic Regression:** `000e51505e76d49ebf02a57d29a3132ea1fa837b49497e142c9fd8caeb73c630`
- **Random Forest:** `22a63c50c43b6aef4834223c4b27c03a811dd8881e770cfaea2437d946d32618`
- **XGBoost:** `9e7745d64f3b967a06cb053b2dfea9e0950075e5c788aecb6a1c3b245d83dfc8`
- **LightGBM:** `597ad772bf68ef6a1022d6b44ef3039c90220ae614a0f11ec015a23c59fa0856`
- **MLP Classifier:** `5bd9a684357c6069b71163c46865d0358745154b813d947627acef5ecca79cb3`

---

## 4. Frozen Authoritative Reference Sources

The following exact file surfaces are verified present, internally accessible, and locked as read-only inputs for Phase 2:

### 4.1 Authoritative Primary Experiment Sources (2017–2020)
- `results/tables/phase3_overall_discrimination.csv`
- `results/calibration/test_set_calibration_final.csv`
- `results/fairness/subgroup_discrimination_metrics.csv`
- `results/uncertainty/marginal_coverage_test_set.csv`
- `results/uncertainty/subgroup_coverage.csv`
- `results/uncertainty/intersectional_coverage_ci.csv`
- `results/tables/m4b_prespecified_n0_final_results.csv`
- `results/tables/m4b_shrinkage_sensitivity.csv`

### 4.2 Authoritative Temporal Validation Sources (2021–2023)
- `results/temporal_validation/temporal_validation_labels_demographics.csv`
- `results/temporal_validation/temporal_validation_fairness_demographics.csv`
- `results/temporal_validation/predictions/temporal_prediction_manifest.json`
- `results/temporal_validation/temporal_conformal_refit_prediction_manifest.json`
- `results/temporal_validation/temporal_discrimination_results.csv`
- `results/temporal_validation/temporal_calibration_results.csv`
- `results/temporal_validation/temporal_fairness_results.csv`
- `results/temporal_validation/temporal_conformal_results.csv`
- `results/temporal_validation/temporal_m4b_results.csv`
- `results/temporal_validation/temporal_original_vs_validation_comparison.csv`
- `results/temporal_validation/PHASE3_TEMPORAL_VALIDATION_REPORT.md`
- `results/temporal_validation/PHASE3_TEMPORAL_VALIDATION_MANIFEST.json`
- `results/temporal_validation/PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md`
- `results/temporal_validation/PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.csv`

---

## 5. Temporal-Validation Status & Phase 4 Classification

- **Temporal-Validation Status:** `Phase 3 COMPLETE` (Manifest verified, 100% SEQN matching confirmed).
- **Final Phase 4 Classification:** **`PARTIAL TEMPORAL REPLICATION`**
  - *Discrimination:* AUROC dropped by 0.041–0.061 across all 5 models (0.7765–0.7824); PR-AUC improved (+0.019 to +0.042). Discrimination is **MIXED**.
  - *Calibration:* Brier scores deteriorated for all 5 models (0.0851–0.1838) while ECE decreased; prior-shift calibration intercept remained negative (-2.00 to -0.37). Calibration is **MIXED**.
  - *Fairness:* Normal-BMI sensitivity gap persisted and widened (62.8–71.9 pp deficit, FDR $q < 0.001$ across all 5 models). Fairness is **WORSENED**.
  - *Conformal:* Marginal coverage held near 90% (87.9%–90.2%), but Obese x Age 60+ intersectional coverage collapsed (69.7%–76.5%). Conformal reliability is **MIXED**.
  - *Frozen M4b ($N_0^* = 0$):* Intersectional $\ge 90\%$ target held **only for Random Forest** (90.10%), failing for LR (88.58%), XGB (87.69%), LGBM (87.31%), and MLP (88.58%). M4b performance is **WORSENED**.

---

## 6. Phase 2 Source Set Protocol

Any subsequent Phase 2 work must treat the primary research files and temporal validation files listed above as read-only inputs. All downstream artifacts must be created exclusively within authorized temporal-validation output directories. No frozen reference source may be replaced, recalculated, or modified.
