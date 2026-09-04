# Model-update re-audit protocol — pooled NHANES 2017–2023

**Frozen:** 2026-09 (before the pooled locked-test outcome was used for any number).
**Status:** pre-registration. Hash and tag `pooled-protocol-freeze` before running `src/p02_*`.

---

## 0. Question and boundary

The `evidence-freeze` audit and the temporal validation both found a body-mass
detection gap + a split-conformal subgroup-coverage failure that no post-hoc or
training-time intervention resolved, and that *widened* on a later cycle. A
reviewer will ask: **"does simply keeping the model current fix it?"**

This study answers that. It retrains the five model families on a **pooled
2017–2023 cohort**, using the **frozen hyperparameters unchanged**, then re-runs
the full audit.

### This is a separate study. It supersedes nothing.

- `evidence-freeze` (2017–March 2020) and `temporal_validation_2021_2023/` are
  **read-only**. No file under `../data/`, `../models/`, `../results/`,
  `../documentation/`, or `../temporal_validation_2021_2023/` is modified.
- All outputs go under `pooled_model_update_2017_2023/`.
- New models trained here live in `pooled_model_update_2017_2023/models/` — never
  in `../models/`.
- Results are a **model-update evidence tier**, never merged into
  `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` primary rows.

### What is frozen (read-only, hash-verified)

| item | source |
|---|---|
| model architecture + hyperparameters | extracted from `../models/phase3/model_{m}_v1.joblib` — see §2 |
| predictor list (order) | `RIDAGEYR RIAGENDR BMXBMI LBXSATSI LBXSASSI LBXSAL LBXSAPSI LBXSTB LBXPLTSI LBDHDD` |
| outcome definition | `LUXSMED ≥ 8.2 kPa` on `LUAXSTAT == 1` |
| subgroup band definitions | age 18–39/40–59/60+; BMI <18.5/18.5–24.9/25–29.9/≥30; sex; `RIDRETH3` |
| 2017–2020 cohort | `../data/processed/analysis_dataset_primary.parquet` |
| 2021–2023 cohort | `../temporal_validation_2021_2023/data/processed/temporal_cohort_2021_2023.parquet` |
| comparison values | `../results/tables/phase3_final_baseline_results.csv`, `../results/fairness/fairness_inference.csv`, `../results/uncertainty/{subgroup_coverage,marginal_coverage_test_set}.csv`, `../results/prepublication_fixes/fix2_bmi_shortcut_check.csv`, `../temporal_validation_2021_2023/results/temporal_*` |

**Nothing about the hyperparameters, preprocessing, class-imbalance policy,
threshold method, calibration method, or conformal method is changed** — only the
training data is expanded to the pooled cohort.

---

## 2. Frozen model recipe (reconstructed from the joblibs — verified §1)

All models: `SimpleImputer(strategy='median')` first (inert on complete-case data,
kept for fidelity). Logistic and MLP additionally `StandardScaler()`.

| model | estimator + frozen hyperparameters |
|---|---|
| logistic | `LogisticRegression(C=0.01, class_weight='balanced', solver='lbfgs', max_iter=2000, random_state=42)` |
| random_forest | `RandomForestClassifier(n_estimators=100, max_depth=7, min_samples_leaf=5, class_weight='balanced', random_state=42)` |
| xgboost | `XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.7, scale_pos_weight=⟨n_neg/n_pos on the new training partition⟩, objective='binary:logistic', eval_metric='logloss', random_state=42, n_jobs=-1)` |
| lightgbm | `LGBMClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.7, scale_pos_weight=⟨same⟩, random_state=42)` |
| mlp | `MLPClassifier(hidden_layer_sizes=(32,16), alpha=0.01, learning_rate_init=0.01, early_stopping=True, n_iter_no_change=10, max_iter=1000, solver='adam', random_state=42)` — unweighted, as in the frozen study |

Env: `../.venv` (`requirements-phase3-lock.txt`): sklearn 1.9.0, xgboost 3.4.1,
lightgbm 4.7.0.

---

## 3. Pipeline (mirrors Phases 3–6, on the pooled cohort)

1. **Pool.** 2017–2020 CAND_1 (N ≈ 7,153) + 2021–2023 CAND_1 (N ≈ 4,910) = N ≈ 12,063.
   Add a `cycle` indicator. Complete-case (already applied in both).
2. **Split.** Fresh stratified 70/30, seed 42, stratified on `outcome × cycle`
   (both cycles proportionally represented in train and locked test). Store by SEQN.
3. **Retrain.** Five families, frozen hyperparameters. `scale_pos_weight`
   recomputed from the new training class counts.
4. **OOF.** 5-fold stratified CV (seed 42) on the training partition → out-of-fold
   predictions.
5. **Threshold.** Youden's J on the OOF predictions, per model (frozen method).
6. **Calibration.** OOF-fit Platt (`sigmoid(a + b·logit(p))`), per model (frozen method).
7. **Conformal.** 80/20 stratified split of the training partition into
   proper-train / calibration; refit on proper-train; nonconformity score
   `1 − P(true class)`; threshold = k-th smallest calibration score,
   `k = ⌈(n_cal+1)(1−α)⌉`, α = 0.10 (frozen method).
8. **Locked test — touched once.** Score; apply threshold, Platt, conformal sets.

---

## 4. Analyses and comparisons

Discrimination, calibration, subgroup fairness (BMI/age/sex/race; bootstrap CI +
within-family BH), split-conformal (marginal + BMI-Obese + Age-60+ + Obese∩60+;
Wilson CI + binomial vs 0.90 + BH), the dissociation check, and the
matched-stiffness shortcut — all as in the frozen study and the temporal module.

Each result is reported three ways: pooled locked test overall; **pooled locked
test restricted to the 2021–2023 cycle** (does updating help on the newer data?);
and Δ vs the frozen 2017–2020 and temporal 2021–2023 values.

M4b not computed (removed from the manuscript, Amendment #20).

---

## 5. Pre-registered verdicts (fixed before the locked test is touched)

| Question | "resolved by updating" if… | "NOT resolved" if… |
|---|---|---|
| **Body-mass detection gap** | Obese−Normal sensitivity gap direction reverses OR loses BH significance in ≥ 4/5 models | direction preserved AND BH-significant in ≥ 4/5 |
| **BMI-Obese conformal under-coverage** | BMI-Obese coverage's Wilson CI includes 0.90 in ≥ 4/5 models | CI excludes 0.90 below in ≥ 4/5 |
| **Matched-stiffness shortcut** | `is_obese` OLS coefficient not significant (p ≥ 0.05) in ≥ 4/5 | coefficient > 0, p < 0.05 in ≥ 4/5 |
| Discrimination recovery | pooled-test AUROC ≥ 0.81 for ≥ 4/5 models | — |
| Discrimination on the 2021–2023 slice | 2021–2023-slice AUROC ≥ 0.80 for ≥ 4/5 | still < 0.80 |

Overall verdict ∈ {UPDATING RESOLVES THE FAILURE / UPDATING PARTIALLY HELPS /
UPDATING DOES NOT RESOLVE THE FAILURE}, decided by the first three rows.

Pre-registered expectation (stated, not binding): based on the training-time
reweighting result (Amendment #19, NEGATIVE) and the temporal replication, the
body-mass failure is expected to **persist** after updating; discrimination is
expected to **recover** toward 0.81–0.83.

---

## 6. Framing rules

- "model-update re-audit on a pooled 2017–2023 cohort" — a diagnostic of whether
  recency fixes the failure, **not** a proposed deployable model and **not**
  external validation.
- If the failure persists: the message is *"the failure is structural, not a
  staleness artefact."*
- If discrimination recovers but the failure persists: *"keeping the model current
  restores aggregate performance without resolving the subgroup reliability
  failure."*
- Pooled numbers are a separate evidence tier; they change no `evidence-freeze`
  primary or secondary claim.

---

## 7. Deliverables

`FROZEN_ARTIFACT_MANIFEST.csv`, `data/processed/pooled_cohort_2017_2023.parquet`
(+ split IDs, manifest), `models/pooled_{m}.joblib` (+ proper-train refits),
`results/pooled_*_results.csv`, `documentation/{POOLED_REAUDIT_REPORT,
POOLED_TOUCH_LOG,LIMITATIONS_ADDENDUM}.md`, `MANUSCRIPT_SECTION_pooled.md`,
`src/verify_pooled.py` (passing).
