# Training-time mitigation — detailed phase-by-phase plan (Amendment #19)

**Created 2026-08-27.** This document specifies every step: inputs (file + column names), exact
computations (formulas), outputs, decision branches, stop conditions, and verification. Nothing is
left implicit. It mirrors the structure of `documentation/prepublication_fixes/PREPUBLICATION_FIXES_PLAN.md`.

---

## Motivation

The frozen study establishes a body-mass reliability–fairness failure that **no post-hoc method
repairs**: subgroup decision thresholds, subgroup calibration, group-conditional (Mondrian)
conformal recalibration, equalized-odds post-processing, model retuning, joint intersectional
conformal, and — Amendment #17 — conformal selective deferral all fail a pre-specified multi-metric
gate or trade one subgroup for another. Amendment #17 characterised the mechanism: in the
under-covered subgroups the misses are **confidently-scored wrong singleton predictions**, i.e. a
**within-subgroup score-ordering failure**. The manuscript (§3.7, §4, §5, Conclusion) now names a
**training-time intervention** as the indicated next step and explicitly does not attempt one.

This amendment attempts exactly one training-time intervention: **subgroup instance reweighting of
the training loss** (Kamiran & Calders reweighing), applied to the five frozen model families,
followed by the frozen classification and conformal evaluation.

**Honest prior on the outcome.** Normal-BMI has 50 fibrosis-positive cases in the training
partition (41 in the conformal proper-train subset, 22 in the locked test). Reweighting changes
the loss landscape but adds no Normal-BMI signal; if the ten routine predictors do not separate
lean fibrosis from lean non-fibrosis, reweighting will trade specificity for sensitivity without
fixing the ranking. The two-mechanism finding (BMI gap is threshold-driven, age gap is not) means
one intervention may fix one and not the other. The modal expected outcome is **PARTIAL** or
**NEGATIVE (no efficacy)**. All four verdict branches (§0.3) are pre-written and each improves the
manuscript.

| | |
|---|---|
| **Type** | one training-time intervention on frozen model families; frozen predictors, outcome, splits, seed, hyperparameters |
| **Governed by** | Amendment #19 (`AMENDMENT_19_TEXT.md`) |
| **Locked-test touches** | 2 (one classification-evaluation script, one conformal-evaluation script), recorded in `documentation/phase3/test_set_lock.md` and `protocol_amendment_registry.md` row 19 |
| **Non-negotiables** | no hyperparameter search; no predictor/outcome change; primary outcome remains `LUXSMED ≥ 8.2 kPa`; weights applied to **training / proper-train only**, never to the conformal-calibration set or the locked test; decision rule (§0.3) fixed before any test access |

---

# PHASE 0 — Pre-registration & freeze  ·  ~1 day, no compute

### 0.1 Amendment #19 text
- [ ] `documentation/training_time_mitigation/AMENDMENT_19_TEXT.md`; append row 19 to
      `documentation/end_to_end/protocol_amendment_registry.md`.

### 0.2 Pre-execution snapshot
- [ ] `documentation/training_time_mitigation/PRE_EXECUTION_SNAPSHOT.md` with git HEAD, UTC
      timestamp, and SHA-256 of every input (dataset, four split ID files, five Phase-3 model
      artifacts, the frozen baseline result CSVs used for comparison in §0.3).

### 0.3 Frozen analysis specification — **this section IS the pre-registration**

#### 0.3.1 The intervention

For each training participant *i* with BMI band `g_i ∈ {Underweight, Normal, Overweight, Obese}`
(column `bmi_group_final`) and primary outcome `y_i` (column `outcome_primary_8.2kPa`), the
Kamiran & Calders reweighing weight is

```
w_i  =  ( n(g_i) / N ) · ( n(y_i) / N )  /  ( n(g_i, y_i) / N )
     =  n(g_i) · n(y_i)  /  ( N · n(g_i, y_i) )
```

where all counts are computed **on the fitting partition only** (the full training partition
N = 5,007 for the classification fits; the proper-train subset N = 4,005 for the conformal fits),
then rescaled so `mean_i(w_i) = 1`. This makes `bmi_group_final ⟂ outcome` in the reweighted
fitting distribution.

- **Arm A (primary):** `g` = the 4 BMI bands. Maps directly to the §3.4 headline finding.
- **Arm B (secondary):** `g` = the 12 BMI×age cells (`bmi_group_final` × `age_group_final`). A cell
  with **fewer than 10 positive** training members falls back to its Arm-A (BMI-marginal) weight.
  (On the training partition the fallback cells are: Underweight×{18-39, 40-59, 60+}, Normal×18-39.)

**Weights use `y`** → they are a fitting-time quantity only; inference never uses them. Weights are
**not** applied to the conformal-calibration set, and **not** to the locked test — this preserves
split-conformal exchangeability, so the marginal coverage guarantee still holds.

**Reference weight table (Arm A, training partition N = 5,007, 466 positive; for verification):**

| BMI band | n(neg) | n(pos) | w(neg) | w(pos) |
|---|---:|---:|---:|---:|
| Underweight | 77 | 4 | 0.954 | 1.885 |
| Normal | 1,190 | 50 | 0.945 | 2.308 |
| Overweight | 1,559 | 84 | 0.956 | 1.820 |
| Obese | 1,715 | 328 | 1.080 | 0.580 |

Dataset-level effective sample size after Arm-A reweighting: **4,795 / 5,007 (95.8 %)** — no
material concentration. (Proper-train weights are recomputed on N = 4,005 and will differ slightly;
the script computes them, they are not retyped.)

#### 0.3.2 Models, hyperparameters, preprocessing — all frozen

- Five families, `MODEL_NAMES = [logistic, random_forest, xgboost, lightgbm, mlp]`.
- Reuse the exact frozen `best_params` from `models/phase3/model_{name}_v1.joblib["best_params"]`
  (extracted live, not retyped). **No `GridSearchCV` / `RandomizedSearchCV` runs.**
- Pipeline construction: `build_pipeline(name, n_neg, n_pos)` imported directly from
  `src/phase3_05_train_and_tune.py` (same import pattern as `src/phase6_02_conformal_refit.py`).
- Preprocessing unchanged: median impute (no-op, 0 missingness) + `StandardScaler` for logistic /
  MLP only.
- Base class-imbalance handling is **kept** (`class_weight="balanced"` for LR/RF;
  `scale_pos_weight = n_neg/n_pos` for XGB/LGBM; MLP none). The subgroup weights are applied **on
  top** via `sample_weight` — for LR/RF/XGB/LGBM the effective per-row weight is
  `class_weight_or_spw(y_i) × w_i` handled by sklearn/xgboost/lightgbm natively when
  `sample_weight` is passed (`class_weight` and `sample_weight` multiply).
- **MLP** (`sklearn.MLPClassifier` has no `sample_weight`): approximate the reweighted
  distribution by **random resampling within each training fold**, using
  `imblearn.over_sampling.RandomOverSampler` inside an `imblearn.pipeline.Pipeline`, exactly as
  Amendment #3 (`src/phase3_13_imbalance_audit_and_mlp_sensitivity.py`) did for class balance —
  here the resampling target is the reweighted `(bmi_band × y)` (Arm A) or `(bmi_band × age × y)`
  (Arm B) stratum counts. The resampler is fit **strictly inside folds / on the fitting
  partition**, never on validation/calibration/test. Resampling seed = 42.
  **Fallback:** if MLP resampling produces unstable OOF AUROC (SD across a 3-seed check > 0.01),
  report MLP as "intervention not applicable in the frozen implementation" and evaluate the four
  `sample_weight`-capable families, exactly as Amendment #3 treats MLP as a special case.

#### 0.3.3 Threshold & recalibration — frozen methods, freshly applied

- Youden's J re-derived on the **new** out-of-fold predictions (5-fold `StratifiedKFold(shuffle=True,
  random_state=42)`, the frozen CV design). Never reuse the old numeric thresholds.
- OOF Platt recalibration re-fit per the frozen Phase-4 method on the new OOF predictions
  (`p_recal = sigmoid(intercept + slope·logit(p_raw))`, `intercept`/`slope` from a
  calibration-in-the-large logistic fit on OOF). No new method choice.

#### 0.3.4 Evaluation — identical to the frozen Phase 5 / Phase 6 evaluation

Classification (Phase 5 metrics): test AUROC + bootstrap 95 % CI (2,000 resamples, seed 42),
PR-AUC, sensitivity, specificity at the new Youden threshold; calibration intercept/slope/Brier/ECE
raw and recalibrated; subgroup sensitivity for BMI bands, age bands, sex, race with 2,000-resample
bootstrap CIs and within-family BH-FDR.

Conformal (Phase 6): refit on proper-train with weights; nonconformity `s = 1 − P̂(y = true | x)`;
threshold = k-th smallest **unweighted** conformal-calibration score,
`k = ⌈(n_cal + 1)(1 − α)⌉`, α = 0.10; marginal coverage; subgroup coverage for BMI-Obese,
Age-60+, all bands; Obese∩60+ intersection; Wilson 95 % CIs; one-sample binomial test vs 0.90;
BH-FDR within each model × dimension family.

#### 0.3.5 Frozen baseline (for the gate) — from the committed artifacts

| model | test AUROC | overall sens | overall spec | Obese−Normal sens disparity (pp) | Age 60+−40-59 disparity (pp) | BMI-Obese conformal cov | Age-60+ conformal cov | marginal cov |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| logistic | 0.8334 | 0.750 | 0.762 | +47.66 (sig) | −8.55 (ns) | 0.823 | 0.849 | 0.908 |
| random_forest | 0.8343 | 0.790 | 0.736 | +31.62 (sig) | −13.16 (sig) | 0.802 | 0.856 | 0.896 |
| xgboost | 0.8429 | 0.845 | 0.677 | +31.36 (sig) | −11.24 (sig) | 0.768 | 0.811 | 0.881 |
| lightgbm | 0.8394 | 0.795 | 0.749 | +27.08 (sig) | −14.15 (sig) | 0.792 | 0.848 | 0.896 |
| mlp | 0.8229 | 0.815 | 0.664 | +39.03 (sig) | −14.67 (sig) | 0.809 | 0.838 | 0.892 |

Sources: `results/tables/phase3_final_baseline_results.csv`, `results/fairness/fairness_inference.csv`,
`results/uncertainty/subgroup_coverage.csv`, `results/uncertainty/marginal_coverage_test_set.csv`.
"Obese−Normal sens disparity" is `absolute_disparity_pp` for `dimension=bmi, category=Obese`
(reference = Normal); the study's headline "Normal−Obese gap" is its negation.

#### 0.3.6 Pre-registered decision gate (applied in Phase 2.3, per arm)

| Gate | Pass condition |
|---|---|
| **G1 — efficacy, sensitivity** | the Obese−Normal sensitivity disparity is reduced in magnitude by **≥ 50 %** vs baseline for **≥ 4/5** models, **and** the residual \|disparity\| < 15 pp for those models |
| **G2 — efficacy, coverage** | BMI-Obese conformal coverage ≥ **0.88** with Wilson lower bound ≥ 0.85 for **≥ 4/5** models, **and** Age-60+ coverage ≥ 0.88 for **≥ 4/5** |
| **G3 — no marginal breach** | marginal coverage ∈ **[0.87, 0.93]** for **5/5** models |
| **G4 — discrimination** | test AUROC within **−0.02** of baseline for **≥ 4/5** models |
| **G5 — calibration** | recalibrated Brier within **+0.01** of baseline for **≥ 4/5** models |
| **G6 — no other-subgroup harm** | Age 60+−40-59 sensitivity disparity not worsened (more negative) by **> 5 pp** for **≥ 4/5**; no sex or race subgroup that was non-significant at baseline becomes BH-significant |
| **G7 — overall performance** | overall sensitivity **and** specificity within **5 pp** of baseline for **≥ 4/5** models |

**Verdict (mechanical):**

- **SUCCESS** — G1–G7 all pass for the **primary arm (A)**.
- **PARTIAL** — exactly one of {G1, G2} passes for arm A, and G3–G7 all pass.
- **NEGATIVE (cost)** — G1 or G2 passes for some arm but a cost gate (G3–G7) fails.
- **NEGATIVE (no efficacy)** — neither G1 nor G2 passes for either arm.

Arm B is read the same way but is **secondary**; it cannot upgrade the verdict above what arm A
supports, only add nuance ("the joint BMI×age reweighting additionally / did not additionally …").

#### 0.3.7 Pre-written manuscript consequence per verdict

- **SUCCESS** → new §3.7b becomes a genuine positive result. Abstract Results gains one sentence:
  *"A training-time subgroup-reweighting intervention closed the body-mass sensitivity gap to <X>
  pp and restored subgroup conformal coverage in <k>/5 models without an unacceptable
  multi-metric cost."* Conclusion: "resistant to every **post-hoc** method; a training-time
  reweighting closed the gap." Table 4 gains a "**SUCCESSFUL**" row (the first).
- **PARTIAL** → §3.7b reports the split ("reweighting closed the sensitivity gap but not the
  coverage gap" / vice versa). Table 4 row = **PARTIALLY EFFECTIVE (training-time)**. Abstract adds
  a half-sentence; the methodological thesis is unchanged.
- **NEGATIVE (cost)** → §3.7b: "an efficacy gate was met only at a cost that failed the
  pre-specified gate (specify which)." Strengthens the "resistant" claim with the strongest test
  yet. Table 4 row = **NO ACCEPTABLE TRAINING-TIME MITIGATION**. Abstract: add "including a
  training-time reweighting intervention" to the mitigation list.
- **NEGATIVE (no efficacy)** → §3.7b: "loss reweighting did not move the subgroup metrics; the
  limit is the small number of normal-weight fibrosis cases (50 training / 22 test) and/or the
  routine feature set, not the training objective." §5 Limitations: this becomes the binding
  data/feature-space limitation. Conclusion sharpens: the fix requires **more lean-fibrosis data or
  richer features**, not a better objective — a more informative endpoint than the current
  manuscript's open "training-time intervention indicated." Table 4 row as NEGATIVE (cost).

### 0.4 Leakage & touch plan
- [ ] Weights derived only from `bmi_group_final` / `age_group_final`, deterministic functions of
      `BMXBMI` / `RIDAGEYR` (already model inputs) → no new information enters the model.
- [ ] **Touch 1** — `src/ttm_03_test_classification.py`: loads the locked test **once**; evaluates
      both arms × 5 models for discrimination / calibration / fairness.
- [ ] **Touch 2** — `src/ttm_04_test_conformal.py`: loads the locked test **once**; evaluates both
      arms × 5 models for conformal coverage.
- [ ] Both recorded in `test_set_lock.md` and registry row 19. Project touch count += 2.
- [ ] Phase 5 folds the new formal hypothesis tests into their own within-family BH (not the
      frozen 182-test pooled family — post-freeze convention, per Amendments #16 and #18).

---

# PHASE 1 — Intervention design & training  ·  ~2–3 days, **no locked-test access**

**Scripts:** `src/ttm_00_compute_weights.py`, `src/ttm_01_train_reweighted.py`,
`src/ttm_02_conformal_refit_reweighted.py`. All import the frozen `build_pipeline` and
`phase3_common` constants. The locked test set is never loaded.

### 1.1 Compute weights  (`ttm_00`)
- Load `analysis_dataset_primary.parquet`; join `train_ids.csv` (N = 5,007) and
  `proper_train_ids.csv` (N = 4,005) separately.
- Compute Arm-A and Arm-B weights per §0.3.1 on each fitting partition; rescale to mean 1.
- Output `results/training_time_mitigation/weights_{armA,armB}_{train,propertrain}.csv`
  (columns `SEQN, bmi_group_final, age_group_final, outcome_primary_8.2kPa, weight`).
- Print: weight range per cell; dataset ESS `(Σw)²/Σw²`; per-subgroup ESS. **Stop-and-flag** (not
  stop-and-abort) if Normal-BMI positive-cell ESS after weighting < 15 or dataset ESS < 0.70·N.

### 1.2 Retrain the classification models  (`ttm_01`)
For each arm, each `name` in `MODEL_NAMES`:
- `pipe, _, _, _ = build_pipeline(name, n_neg, n_pos)` on the full training partition; apply frozen
  `best_params` via `pipe.set_params(**best_params)`.
- **OOF predictions** by an explicit 5-fold loop (`StratifiedKFold(5, shuffle=True,
  random_state=42)`): for each fold, fit on the 4 training folds with `sample_weight = w`
  (`pipe.fit(X_tr, y_tr, est__sample_weight=w_tr)` for LR/RF/XGB/LGBM; the imblearn resampling
  pipeline for MLP), predict `predict_proba` on the held-out fold. An explicit loop is used rather
  than `cross_val_predict` to keep the weight routing transparent.
- Save OOF predictions to `results/training_time_mitigation/oof_predictions_{arm}_{name}.csv`
  (`SEQN, true_target, predicted_probability`).
- Fit the final model on the full training partition with weights; save to
  `models/training_time_mitigation/model_{arm}_{name}.joblib`.

### 1.3 Thresholds + recalibration  (`ttm_01`)
- Youden's J on the new OOF predictions → `results/training_time_mitigation/youden_thresholds_{arm}.csv`.
- OOF Platt (frozen Phase-4 method) on the new OOF predictions → store intercept/slope per model.

### 1.4 Conformal refit  (`ttm_02`)
- Recompute Arm weights on the **proper-train** partition (N = 4,005).
- Refit each family on proper-train with `sample_weight` (imblearn resampling for MLP), frozen
  `best_params`; save to `models/training_time_mitigation/model_{arm}_{name}_proper_train.joblib`
  (mirrors `models/phase6_conformal_refit/`).
- Score the **unweighted** `conformal_calibration_ids.csv` (N = 1,002): nonconformity
  `s = 1 − P̂(y = true | x)`; conformal threshold `q̂ = k-th smallest s`,
  `k = ⌈(1002 + 1)(1 − 0.10)⌉ = 903`.
- Output `results/training_time_mitigation/conformal_thresholds_{arm}.csv`.

### 1.5 Pre-test mechanism diagnostic  (`ttm_01`, OOF only — decides whether Phase 2 is a formality)
- **Within-Normal-BMI OOF AUROC**, baseline vs reweighted, per model. (Baseline OOF from
  `results/predictions/validation_predictions_{name}.csv`.)
- **Score separation:** median OOF score of Normal-BMI positives vs Normal-BMI negatives, baseline
  vs reweighted.
- **BMI-shortcut coefficient (Amendment #18 C4 replication on OOF):** OLS
  `predicted_probability ~ LUXSMED + is_obese` in the 8.2–12 kPa band, baseline vs reweighted — a
  shrinking `is_obese` coefficient is direct evidence the intervention worked on the mechanism.
- Output `results/training_time_mitigation/phase1_mechanism_diagnostic.csv`.
- **If** within-Normal-BMI OOF AUROC does not increase for any model **and** the score separation
  does not widen, Phase 2 is expected to return NEGATIVE (no efficacy) — still run it for the
  pre-registered record, but the answer is knowable here without a test touch.

### 1.6 Phase-1 report
`documentation/training_time_mitigation/PHASE1_INTERVENTION_AND_DIAGNOSTIC.md`: weights, ESS, the
MLP handling decision (native resample vs fallback), and the §1.5 diagnostic with a predicted
Phase-2 verdict.

---

# PHASE 2 — Locked-test evaluation  ·  ~1 day, **the 2 touches**

### 2.1 Touch 1 — classification  (`src/ttm_03_test_classification.py`)
- Assert `test_ids ∩ train_ids = ∅`, `test_ids ∩ proper_train_ids = ∅`, `test_ids ∩
  conformal_calibration_ids = ∅`; log the intersection sizes (must be 0).
- Load the locked test **once**. For each arm × model: apply the final reweighted model + its new
  Youden threshold + its new Platt transform.
- Compute: test AUROC + bootstrap CI, PR-AUC, sensitivity, specificity; calibration
  intercept/slope/Brier/ECE (raw + recalibrated); subgroup sensitivity (BMI bands, age bands, sex
  by `RIAGENDR`, race by `RIDRETH3`) with 2,000-resample bootstrap CIs and within-(model × arm ×
  dimension) BH-FDR.
- Output `results/training_time_mitigation/test_classification_{arm}.csv`,
  `test_subgroup_sensitivity_{arm}.csv`.

### 2.2 Touch 2 — conformal  (`src/ttm_04_test_conformal.py`)
- Same leakage asserts. Load the locked test **once**.
- For each arm × model: build prediction sets from the reweighted proper-train model + the
  Arm's conformal threshold; compute marginal coverage, subgroup coverage (BMI-Obese, Age-60+, all
  bands, Normal/Overweight for context), Obese∩60+ intersection; Wilson 95 % CIs; binomial test vs
  0.90; BH-FDR within each (model × arm × dimension) family; set-size / singleton-rate.
- Output `results/training_time_mitigation/test_conformal_{arm}.csv`,
  `test_conformal_intersectional_{arm}.csv`.

### 2.3 Apply the gate
- [ ] Compute G1–G7 per §0.3.6 for arm A (primary) and arm B (secondary); record the exact
      numbers that trigger each pass/fail.
- [ ] Assign the verdict (SUCCESS / PARTIAL / NEGATIVE-cost / NEGATIVE-no-efficacy).
- [ ] Output `results/training_time_mitigation/decision.csv`; report
      `documentation/training_time_mitigation/PHASE2_LOCKED_TEST_RESULTS.md`.

---

# PHASE 3 — Comparison & mechanism  ·  ~1 day

### 3.1 Unified comparison table
Rows: frozen baseline → each post-hoc mitigation (from the existing manuscript Table 4) → Arm A →
Arm B. Columns: Obese−Normal sensitivity disparity; BMI-Obese coverage; Age-60+ coverage; marginal
coverage; overall sensitivity / specificity; test AUROC; recalibrated Brier. This is the row block
that goes into the manuscript Table 4.
Output `results/training_time_mitigation/comparison_vs_battery.csv`.

### 3.2 Mechanism
- Did the intervention fix the **score ordering** (within-Normal-BMI test AUROC up; obese
  confident-wrong-singleton rate down) or only move the **threshold**? Compare, baseline vs each
  arm: within-subgroup test AUROC; the fraction of obese under-coverage that is singleton-vs-set;
  the Amendment #18 C4 `is_obese` matched-stiffness coefficient on the **test** set.
- Output `results/training_time_mitigation/mechanism_comparison.csv`.

### 3.3 Cost accounting
Per arm × model: Δ overall sensitivity, Δ specificity, Δ AUROC, Δ Brier, Δ each other subgroup;
list every subgroup that moved in the wrong direction.

### 3.4 Report
`documentation/training_time_mitigation/PHASE3_COMPARISON_AND_MECHANISM.md`.

---

# PHASE 4 — Manuscript & register integration  ·  ~2–3 days

### 4.1 Methods
- [ ] New **§2.8b** — training-time mitigation: the reweighing formula, the two arms, frozen
      hyperparameters, MLP handling, the two touches, the pre-registered gate.

### 4.2 Results
- [ ] New **§3.7b** — the result, verdict-conditional text per §0.3.7.
- [ ] **Table 4** — new rows "Training-time subgroup reweighing (BMI)" and "(BMI×age)".

### 4.3 Discussion §4
- [ ] Replace "a training-time intervention (subgroup reweighting or a subgroup-aware objective) is
      the indicated next step" with what actually happened.

### 4.4 Limitations §5
- [ ] If NEGATIVE (no efficacy): add the lean-fibrosis event-count ceiling (50 training / 22 test)
      as the binding limitation, and state that the fix needs data or features, not an objective.
- [ ] Update `FINAL_LIMITATIONS_REGISTER.md` D1.

### 4.5 Abstract / Conclusion
- [ ] One sentence, per §0.3.7 branch.

### 4.6 Registers
- [ ] `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` — new row `MIT-07`.
- [ ] `FINAL_SCIENTIFIC_FINDINGS.md` §7 / §11 / §14 · `FINAL_RESEARCH_AUDIT.md` §7 ·
      `DO_NOT_CLAIM.md` · `RESEARCH_WEAKNESSES.md` W2 · `RESEARCH_STRENGTHS.md` #7 ·
      `EXPLORATORY_RESULTS.md` (Arm B if exploratory) · `MANUSCRIPT_FRAMING_GUIDANCE.md`.
- [ ] `documentation/manuscript/RESULTS_VERIFICATION.md` — Amendment #19 addendum, every new number
      vs its CSV.

---

# PHASE 5 — Validation & Amendment #19 closure  ·  ~1 day

- [ ] `tests/test_training_time_mitigation.py`:
  - `test_ids` disjoint from `train_ids`, `proper_train_ids`, `conformal_calibration_ids`
  - weights: mean ≈ 1; a weight is a pure function of `(bmi_group_final[, age_group_final],
    outcome)`; the conformal-calibration and test rows carry **no** weight in any script
  - hyperparameters used equal `models/phase3/model_{name}_v1.joblib["best_params"]` exactly
  - exactly 2 locked-test touches, timestamped after Phase 0
  - re-running `ttm_00`…`ttm_04` reproduces every number (seed 42) — subject to
    MLP-resampling determinism (fixed seed) or MLP excluded per the §0.3.2 fallback
  - count identities: train 5,007 / 466; proper-train 4,005 / 373; conformal-cal 1,002 / 93;
    test 2,146 / 200; Normal-BMI train positives = 50
  - the gate in `decision.csv` is reproduced from the raw metric CSVs by an independent re-implementation
- [ ] Independent spot-check of ≥ 15 new numbers against the result CSVs.
- [ ] `documentation/training_time_mitigation/AMENDMENT_19_CLOSURE.md` — what ran, the verdict, the
      two touches, the residual limitation.
- [ ] `protocol_amendment_registry.md` row 19 outcome; `test_set_lock.md` touch log;
      `documentation/START_HERE.md` §7; `documentation/manuscript/README.md` → v5.

---

# Timeline

| Phase | | Days |
|---|---|---|
| 0 | Pre-registration | 1 |
| 1 | Intervention + training + diagnostic | 2–3 |
| 2 | Locked-test evaluation (2 touches) | 1 |
| 3 | Comparison + mechanism | 1 |
| 4 | Manuscript + registers | 2–3 |
| 5 | Validation + closure | 1 |
| | **Total** | **≈ 8–12 working days** |

# Risk register

| # | Risk | Trigger | Action |
|---|---|---|---|
| R1 | MLP resampling unstable | Phase 1.2 3-seed OOF AUROC SD > 0.01 | §0.3.2 fallback: report MLP as not-applicable, evaluate 4 families; the gate's "≥ 4/5" becomes "≥ 3/4" (pre-registered here) |
| R2 | Reweighting closes BMI gap, blows up age gap | Phase 2.3 G6 fails | verdict NEGATIVE (cost); this is itself the two-mechanism finding confirmed at training time — report as such |
| R3 | Marginal coverage breaches after reweighting | Phase 2.3 G3 fails | verdict NEGATIVE (cost); note the reweighted model's score distribution shifted enough to break the conformal calibration transfer |
| R4 | NEGATIVE (no efficacy) — the modal outcome | Phase 2.3 | this is a **publishable sharpening**, not a failure: the limit is data/features, not the objective (§0.3.7) |
| R5 | Arm B tiny cells make it uninterpretable | Phase 1.1 ESS flags | Arm B stays secondary/exploratory; conclusions rest on Arm A only |
| R6 | A reviewer wants group-DRO too | post-submission | pre-empt in §2.8b: reweighing is the uniformly-applicable choice across tree ensembles; group-DRO for LR/MLP only is named as further work |

# New files this plan creates

Docs: `AMENDMENT_19_TEXT.md`, `PRE_EXECUTION_SNAPSHOT.md`, `PHASE1_INTERVENTION_AND_DIAGNOSTIC.md`,
`PHASE2_LOCKED_TEST_RESULTS.md`, `PHASE3_COMPARISON_AND_MECHANISM.md`, `AMENDMENT_19_CLOSURE.md`
(all under `documentation/training_time_mitigation/`).
Code: `src/ttm_00_compute_weights.py`, `src/ttm_01_train_reweighted.py`,
`src/ttm_02_conformal_refit_reweighted.py`, `src/ttm_03_test_classification.py`,
`src/ttm_04_test_conformal.py`, `tests/test_training_time_mitigation.py`.
Results: `results/training_time_mitigation/*.csv`.
Models: `models/training_time_mitigation/*.joblib`.
Modified: the manuscript, ~8 register files, `protocol_amendment_registry.md`, `test_set_lock.md`,
`START_HERE.md`, `documentation/manuscript/README.md`.

# Execution note

`scikit-learn` / `xgboost` / `lightgbm` are not available in the plan-authoring environment;
Phases 1–2 (training + test evaluation) are executed by the operator on the full pinned
environment (`requirements-phase3-lock.txt`). Phases 0, 3, 4, 5 (pre-registration, results-driven
writing, validation) are done from the produced CSVs.
