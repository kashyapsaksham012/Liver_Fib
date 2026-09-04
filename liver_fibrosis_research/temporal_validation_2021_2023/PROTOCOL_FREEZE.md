# Temporal validation protocol — NHANES 2021–2023

**Frozen:** 2026-09 (before the 2021–2023 outcome was used for any number).
**Status:** pre-registration. Hash this file and tag it `temporal-protocol-freeze` before running `src/t03_*`.

---

## 0. Purpose and boundary

A later-cycle (temporal) evaluation of the **frozen** `evidence-freeze` models on
NHANES **August 2021–August 2023** (`_L` files). This is TRIPOD **narrow /
temporal validation**, not external, geographic, or independent-cohort validation.

**This addendum adds a temporal-evaluation evidence tier. It supersedes nothing.**
Every primary and secondary claim from `evidence-freeze` stands unchanged.

### Preservation rules (enforced)

1. No file under `../data/processed/splits/`, `../models/`, `../results/`, or
   `../documentation/` (Phase 0–8, BMI-investigation, sensitivity, master
   reports) is modified, moved, or deleted. All outputs go under
   `temporal_validation_2021_2023/`.
2. No model retrained. No hyperparameter searched or changed. No operating
   threshold re-derived. No Platt parameter re-fit. No conformal quantile
   re-computed. Every frozen artifact is loaded by a path whose SHA-256 is
   asserted against `FROZEN_ARTIFACT_MANIFEST.csv`.
3. The 2021–2023 primary outcome is used ("touched") once per analysis family;
   each use logged in `documentation/TEMPORAL_TOUCH_LOG.md`.
4. Frozen 2017–2020 results are **read** for comparison; never recalculated.
5. No claim of external / geographic / independent-cohort validation, model
   updating, clinical readiness, or causal explanation.

---

## 1. Frozen artifacts to be used (read-only, hash-verified)

| Purpose | Artifact |
|---|---|
| Discrimination / calibration / fairness scoring | `../models/phase3/model_{logistic,random_forest,xgboost,lightgbm,mlp}_v1.joblib` (full-train fit) |
| Conformal scoring | `../models/phase6_conformal_refit/model_{…}_proper_train_refit.joblib` (proper-train fit) |
| Operating thresholds (Youden, OOF) | `../results/tables/phase3_final_baseline_results.csv` col `threshold` — logistic 0.5173 / RF 0.4499 / XGB 0.4108 / LGBM 0.4988 / MLP 0.1065 |
| Platt recalibration (intercept, slope; OOF-fit) | `../results/calibration/test_set_recalibrated_predictions.csv` — logistic (−2.242509, 1.060614) / RF (−1.86245, 1.198516) / XGB (−2.046007, 1.03932) / LGBM (−2.053483, 1.06221) / MLP (−0.280858, 0.829627) |
| Conformal nonconformity threshold (score = 1 − P(true class); α = 0.10) | `../results/uncertainty/conformal_thresholds_by_model.csv` col `threshold` — logistic 0.672744 / RF 0.607211 / XGB 0.653193 / LGBM 0.656959 / MLP 0.377967 |
| Predictor list (order) | `RIDAGEYR, RIAGENDR, BMXBMI, LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD` (also stored inside each joblib) |
| Outcome definition | `LUXSMED ≥ 8.2 kPa` on a quality-valid VCTE (`LUAXSTAT == 1`) — `../documentation/phase2/primary_outcome_definition.md` |
| Subgroup band definitions | age 18–39 / 40–59 / 60+ ; BMI <18.5 / 18.5–24.9 / 25–29.9 / ≥30 ; sex `RIAGENDR`; race `RIDRETH3` (1 Mex-Am, 2 Other Hisp, 3 NH White, 4 NH Black, 6 NH Asian, 7 Other/Multi) |
| 2017–2020 comparison values | `../results/tables/phase3_final_baseline_results.csv`, `../results/calibration/test_set_calibration_final.csv`, `../results/fairness/fairness_inference.csv`, `../results/uncertainty/{subgroup_coverage,marginal_coverage_test_set,intersectional_coverage_ci}.csv` |

The MLP joblib is `model_mlp_v1.joblib` (unweighted primary), **not**
`model_mlp_balanced_v1_sensitivity.joblib`.

---

## 2. Cohort construction (mirrors `evidence-freeze` Phase 2 exactly)

Input files: `../../NHANES 2021–2023 temporal validation dataset/{DEMO,BMX,BIOPRO,CBC,HDL,LUX}_L.xpt`.

Eligibility, applied in order (identical rule to CAND_1):
1. Non-missing `LUXSMED` (elastography attempted, stiffness recorded).
2. `LUAXSTAT == 1` (complete + quality-valid exam).
3. `RIDAGEYR ≥ 18` (adult).
4. Complete on all 10 predictors.

The outcome column is derived but **flagged `outcome_used_for_decisions: false`**
in the cohort manifest — it is sealed until `src/t03_*`.

Missing-data strategy: **complete-case**, matching the frozen primary analysis.
Survey weights: **not used**, matching the frozen primary analysis (weighted
training was a deferred exploratory item).

---

## 3. Analyses (mirror Phases 3–6; M4b excluded per Amendment #20)

| Family | Metrics | 2017–2020 comparison source |
|---|---|---|
| Discrimination | AUROC, PR-AUC (percentile bootstrap n=2000, seed=42); sensitivity/specificity/PPV/NPV at the frozen threshold | `phase3_final_baseline_results.csv` |
| Calibration | intercept, slope, ECE (decile), Brier — raw and Platt | `test_set_calibration_final.csv` |
| Fairness | subgroup sensitivity by BMI band / age band / sex / race; bootstrap 95% CI; within-family (model × dimension) BH-FDR | `fairness_inference.csv` |
| Conformal | marginal + BMI-Obese + Age-60+ + Obese∩60+ coverage; Wilson 95% CI; one-sample binomial vs 0.90; within-family BH-FDR | `subgroup_coverage.csv`, `marginal_coverage_test_set.csv`, `intersectional_coverage_ci.csv` |

**Not computed:** M4b / joint intersectional conformal (removed from the
manuscript, Amendment #20).

### 3b. Value-add analyses (in-boundary — frozen scores only, no refitting)

- **Dissociation check.** Does BMI-Obese show the fairness-favorable /
  reliability-unfavorable split temporally? (Obese sensitivity vs Normal-BMI
  *and* Obese conformal coverage vs target, same cohort.)
- **Matched-stiffness shortcut (Amendment #18 replication).** Among participants
  with `LUXSMED` in 8.2–12 kPa, OLS of the frozen model's raw score on an `is_obese`
  indicator (+ `LUXSMED` as covariate). Tests whether the frozen models still
  score obese participants higher at matched measured stiffness in 2021–2023.

---

## 4. Lab-method contingency (ALT / enzyme analyzer change)

The `temporal-validation-standalone` branch found NHANES changed the biochemistry
analyzer between cycles (Roche Cobas 6000) and built an ALT crosswalk.

- **PRIMARY analysis: raw 2021–2023 predictor values, no crosswalk.** This is the
  honest "would the deployed frozen model work on the data as it arrives" test.
- `src/t02_drift_audit.py` checks the NHANES analytic notes / distributional shift
  for **all six** lab predictors (ALT, AST, albumin, ALP, bilirubin, platelets, HDL).
- **SENSITIVITY analysis (only if the drift audit shows a material method-attributable
  shift):** re-score with the branch's crosswalk, reported separately, labelled a
  sensitivity analysis — never folded into the primary number.

---

## 5. Pre-registered replication verdicts

Fixed before the outcome is touched:

| Finding | REPLICATED if… | STRENGTHENED if… |
|---|---|---|
| Discrimination | AUROC within −0.05 of 2017–2020 for ≥ 4/5 models | — |
| Calibration correction | Platt intercept within ±0.5 of 0 for ≥ 4/5 models | — |
| **BMI-Obese vs Normal sensitivity gap** | direction preserved (Obese > Normal) AND BH-significant in ≥ 4/5 models | gap magnitude larger than 2017–2020 in ≥ 4/5 models |
| **Marginal-vs-subgroup conformal split** | marginal within ±0.03 of 0.90 AND BMI-Obese coverage < lower bound of a 90% Wilson CI for ≥ 4/5 models | — |
| Age-60+ sensitivity deficit | direction preserved AND BH-significant in ≥ 4/5 | *(fragility anticipated — a non-replication here is expected and not adverse)* |
| Matched-stiffness shortcut | `is_obese` OLS coefficient > 0, p < 0.05 in ≥ 4/5 models | — |

Overall classification ∈ {FULL / PARTIAL / MINIMAL TEMPORAL REPLICATION}, decided
by how many of the above (excluding the anticipated-fragile age row) replicate.

---

## 6. Framing rules for any write-up

- "temporal validation on a subsequent NHANES cycle" — never "external",
  "independent", "generalizes", "transportable".
- Report the pandemic discontinuity as a confounder of transport vs population
  change — an observed fact, not an explanation.
- The ALT/enzyme analyzer change is disclosed; the crosswalk (if used) is a
  sensitivity analysis, not a correction.
- Temporal numbers get their own tier in `../documentation/START_HERE.md` and are
  never merged into `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` primary rows.

---

## 7. Deliverables

`FROZEN_ARTIFACT_MANIFEST.csv`, `data/processed/temporal_cohort_2021_2023.parquet`
(+ manifest), `documentation/{TEMPORAL_DRIFT_AUDIT,TEMPORAL_VALIDATION_REPORT,
TEMPORAL_TOUCH_LOG,LIMITATIONS_ADDENDUM}.md`, `results/temporal_*_results.csv`,
`MANUSCRIPT_SECTION_temporal.md`, `src/verify_temporal.py` (passing).
