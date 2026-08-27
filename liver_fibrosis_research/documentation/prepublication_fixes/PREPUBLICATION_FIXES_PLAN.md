# Pre-publication fixes — detailed phase-by-phase plan

**Created 2026-08-27.** Three issues must be resolved before the manuscript is submittable. This
document specifies **every** step: inputs (with file + column names), exact computations
(formulas), outputs, decision branches, stop conditions, and verification. Nothing is left
implicit.

| Fix | Issue | Type | Governed by |
|---|---|---|---|
| **1** | §3.4 (BMI classification sensitivity) uses the **Phase-3 full-train** models; §3.5–3.6 (conformal coverage) use the **Phase-6 proper-train-refit** models. The paper reads as one model. | analysis (cached predictions) + disclosure | Amendment #18 |
| **2** | VCTE over-reads liver stiffness at high BMI → some obese "positive" labels near 8.2 kPa may be inflated → threat to the primary body-mass finding. | analysis (relabel-only) + bounded disclosure (partly irreducible) | Amendment #18 |
| **3** | Three overlapping mitigation analyses with slightly different conclusions. | writing / consolidation only | none |

**Non-negotiables:** no retraining, no hyperparameter search, no predictor/outcome change; work
from frozen predictions and the frozen analysis dataset only; each new analysis touches the locked
test **once** (recorded); no post-hoc change to any frozen result; every new number verified
against its source artifact; pre-registered decision rules (Phase 0) are applied mechanically.

---

# PHASE 0 — Pre-registration & freeze  ·  ~0.5 day

### 0.1 Amendment #18 text
- [ ] Write `documentation/prepublication_fixes/AMENDMENT_18_TEXT.md` and append a one-line entry
      to `documentation/end_to_end/protocol_amendment_registry.md` (row 18).
- [ ] Content: two sensitivity analyses (Fix 1, Fix 2) on frozen predictions; a Methods disclosure
      of the two model fits; two additional locked-test touches (one per analysis script), added
      to the project-wide pooled-FDR family in Phase 5; the mitigation-narrative consolidation
      (Fix 3) is writing and needs no amendment but is noted.

### 0.2 Pre-execution snapshot
- [ ] Write `documentation/prepublication_fixes/PRE_EXECUTION_SNAPSHOT.md` with git HEAD, UTC
      timestamp, and SHA-256 of every input file used in Phases 1–2:
  - `data/processed/analysis_dataset_primary.parquet` = `1c1f16a4…12023938`
  - `data/processed/splits/test_ids.csv` = `a9e54315…a6624779`
  - `data/processed/splits/conformal_calibration_ids.csv` = `4d696cbc…24b6c5b3c5`
  - `data/processed/splits/proper_train_ids.csv` = `bc29dbe6…dab01fef`
  - `results/predictions/test_predictions_{logistic,random_forest,xgboost,lightgbm,mlp}.csv`
  - `results/uncertainty/test_set_prediction_sets.csv` = `527969c3…155f175506`
  - `results/uncertainty/calibration_scores_{…}.csv`
  - `results/uncertainty/conformal_thresholds_by_model.csv` = `23909e42…efbbbdd2`
  - `results/fairness/fairness_inference.csv` = `b7351bd9…33c21e132`
  - `results/uncertainty/subgroup_coverage.csv`
  - `results/sensitivity/secondary_severity_outcomes_9p7_bmi_age_fairness.csv` = `4b856cfb…fd2b41fd`

### 0.3 Frozen analysis specification (this section IS the pre-registration)

**Fix 1 decision rule (applied in Phase 1.6):**
- Let `gap_ct` = Normal − Obese conformal-sensitivity gap (Phase 1.2); `gap_cls` = Normal − Obese
  classification-sensitivity gap at the derived Youden threshold (Phase 1.3).
- **STRENGTHENING** if `gap_ct ≤ −0.15` for ≥ 4/5 models **and** `gap_cls ≤ −0.15` for ≥ 4/5
  models (i.e. the gap is clearly present in the refit fit too).
- **PARTIAL** if the gap is present (`≤ −0.10`) for 2–3/5 models in either measure.
- **CAVEAT** if the gap is `> −0.10` for ≥ 4/5 models in both measures (i.e. essentially absent in
  the refit fit).

**Fix 2 verdict rule (applied in Phase 2.7):**
- Let `G(cut)` = median across models of the Obese−Normal classification-sensitivity gap
  (Phase 2.2) at LUXSMED ≥ `cut`. Let `Δobese` = |Obese sensitivity at ≥12 kPa − Obese
  sensitivity at ≥8.2 kPa| (Phase 2.3).
- **V1 (not purely measurement-driven):** `G(12) ≥ +0.15` (obese still detected ≥ 15 pp better)
  for ≥ 3/5 models **and** `Δobese ≤ 0.10` (obese performance stable across the stiffness range).
- **V2 (measurement-bias contribution, inseparable):** `G(12) < +0.10` for ≥ 3/5 models **or**
  `Δobese > 0.15`.
- **V3 (underpowered, cannot adjudicate):** anything else, **or** Normal-BMI positives at ≥ 12 kPa
  < 8 (currently 7 — so V3 is the likely floor; V1/V2 are read from the obese side + direction).
- The verdict text and its consequence for the abstract are pre-written in Phase 4.5.

### 0.4 Leakage pre-check
- [ ] Confirm `set(test_ids) ∩ set(conformal_calibration_ids) == ∅` and
      `set(test_ids) ∩ set(proper_train_ids) == ∅` (both already PASS in
      `phase6_partition_audit.csv`; re-assert in the Phase-1 script and log the intersection
      sizes, which must be 0).

---

# PHASE 1 — Fix 1: does the subgroup gap appear in *both* model fits?  ·  ~1.5 days

**Script:** `src/prepub_01_model_fit_alignment.py`. Reads cached predictions only; no model loaded.
**One locked-test touch** (all computations in a single run).

### 1.1 Inputs
| Purpose | File | Columns used |
|---|---|---|
| refit-model test predictions + sets + subgroup labels | `results/uncertainty/test_set_prediction_sets.csv` | `SEQN, model, true_target, predicted_probability_positive, include_positive, include_negative, _bmi, _age` |
| refit-model calibration predictions (for the Youden threshold) | `results/uncertainty/calibration_scores_{model}.csv` | `SEQN, true_target, predicted_probability_positive` |
| full-train §3.4 numbers (comparison target) | `results/fairness/fairness_inference.csv` | `model, dimension, category, subgroup_sensitivity, reference_sensitivity, absolute_disparity_pp` |
| frozen conformal coverage (context) | `results/uncertainty/subgroup_coverage.csv` | `model, dimension, category, empirical_coverage` |

### 1.2 Computation A — conformal sensitivity by subgroup (refit models)
For each `model` and each subgroup `g` in {BMI: Normal, Overweight, Obese; Age: 18–39, 40–59, 60+}:
- Restrict to test rows with `true_target == 1` and subgroup `g`.
- `conf_sens(model, g) = mean(include_positive)` over that set. *(= coverage among positives = the
  fraction of true positives whose prediction set contains the positive class.)*
- `gap_ct_bmi(model) = conf_sens(Normal) − conf_sens(Obese)`
- `gap_ct_age(model) = conf_sens(60+) − conf_sens(40–59)`
- **Bootstrap 95% CI** on each gap: 2,000 resamples of the test rows (seed 42), recompute the gap,
  take the 2.5/97.5 percentiles.
- Record `n_positive` in Normal (expect 22) and Obese (expect 140).

### 1.3 Computation B — classification sensitivity at a derived Youden threshold (refit models)
For each `model`:
- On `calibration_scores_{model}` (1,002 rows, 93 positives): for `t` on a grid
  `0.01 … 0.99` step 0.005, compute `sens(t)` and `spec(t)`; `τ* = argmax_t [sens(t)+spec(t)−1]`.
  **Log that this threshold is derived from 93 positives — materially fewer than the Phase-3
  threshold's 466 OOF positives — so it is noisier; this is why 1.4 (threshold sweep) is the
  primary robustness evidence, not τ* alone.**
- On the refit test predictions: `pred_pos = predicted_probability_positive > τ*`.
- `cls_sens(model, g) = mean(pred_pos)` over `{g ∩ true_target==1}`.
- `gap_cls_bmi(model) = cls_sens(Normal) − cls_sens(Obese)`; `gap_cls_age` analogously.
- Bootstrap 95% CIs as in 1.2.

### 1.4 Computation C — threshold robustness
- Repeat 1.3's classification-sensitivity computation for fixed `τ ∈ {0.30, 0.35, 0.40, 0.45,
  0.50, 0.55, 0.60}`.
- Output: for each `(model, τ)`, the Normal−Obese gap. The finding is robust if the gap is
  negative (Normal < Obese) at **every** τ for ≥ 4/5 models.

### 1.5 Computation D — side-by-side comparison
Build one table:
| model | full-train classification gap (§3.4, pp) | refit conformal-sens gap (1.2, pp) | refit classification gap @τ* (1.3, pp) | refit gap sign at all τ in 1.4? |

### 1.6 Decision (apply 0.3's Fix-1 rule mechanically)
- [ ] Classify the outcome as **STRENGTHENING / PARTIAL / CAVEAT** and record which, with the
      numbers that triggered it.

### 1.7 Outputs
- `results/prepublication_fixes/fix1_refit_subgroup_sensitivity.csv` (1.2 + 1.3, per model × subgroup, with CIs)
- `results/prepublication_fixes/fix1_threshold_robustness.csv` (1.4)
- `results/prepublication_fixes/fix1_comparison_table.csv` (1.5)
- `results/prepublication_fixes/fix1_youden_thresholds.csv` (τ* per model + n_positive used)
- `documentation/prepublication_fixes/FIX1_MODEL_FIT_ALIGNMENT.md` — narrative + decision + the
  Methods-paragraph draft.

### 1.8 Verification checks (recorded in the report)
- [ ] `test_ids ∩ calibration_ids == 0`, `test_ids ∩ proper_train_ids == 0`.
- [ ] Row counts: 2,146 test rows per model; 200 positives; Normal-BMI 22 positives, Obese 140.
- [ ] Re-running the script reproduces every number bit-for-bit (seed 42).
- [ ] The full-train gap read from `fairness_inference.csv` matches the manuscript §3.4 values
      (LR −47.7, RF −31.6, XGB −31.4, LGBM −27.1, MLP −39.0 pp).

---

# PHASE 2 — Fix 2: VCTE measurement-bias sensitivity  ·  ~3 days

**Script:** `src/prepub_02_vcte_bias_sensitivity.py`. Relabel-only on frozen predictions.
**One locked-test touch.**

### 2.1 Inputs
| Purpose | File | Columns |
|---|---|---|
| continuous stiffness + subgroup + outcome | `data/processed/analysis_dataset_primary.parquet` | `SEQN, LUXSMED, bmi_group_final, age_group_final, outcome_primary_8.2kPa` |
| test SEQNs | `data/processed/splits/test_ids.csv` | `SEQN` |
| full-train model test predictions (consistent with §3.4) | `results/predictions/test_predictions_{model}.csv` | `SEQN, predicted_probability, threshold_used` |
| refit + conformal sets (for the coverage side) | `results/uncertainty/test_set_prediction_sets.csv` | `SEQN, model, predicted_probability_positive, include_positive, include_negative, _bmi, _age` |
| Amendment #15 (already has ≥9.7) | `results/sensitivity/secondary_severity_outcomes_9p7_bmi_age_fairness.csv` | all |

Merge everything on `SEQN`, restricted to the 2,146 test participants.

### 2.2 Computation C1 — BMI (and age) sensitivity gap across stiffness thresholds
For `cut ∈ {8.2, 9.7, 10.0, 12.0, 13.6}` and each full-train `model`:
- `positive_i = LUXSMED_i ≥ cut`  *(relabel; model scores unchanged)*
- `pred_pos_i = predicted_probability_i > threshold_used_i`  *(the frozen Youden threshold from §3.4)*
- `sens(BMI-group, cut) = mean(pred_pos)` over `{group ∩ positive}`
- `gap_bmi(model, cut) = sens(Obese) − sens(Normal)`  *(Obese − Normal; positive = obese detected better)*
- `gap_age(model, cut) = sens(40–59) − sens(60+)`
- Bootstrap 95% CI (2,000 resamples, seed 42). **Also record `n_positive` per group** — this
  will show the Normal-BMI power collapse: 22 → 11 → 9 → 7 → 6.
- Output table: `cut × model × [n_pos_Normal, n_pos_Obese, sens_Normal, sens_Obese, gap, CI_lo, CI_hi]`.

### 2.3 Computation C2 — obese-side, high power
- `Δobese(model)` = obese classification sensitivity with `positive = LUXSMED ≥ 12` (53 events)
  **minus** obese classification sensitivity with `positive = LUXSMED ≥ 8.2` (140 events),
  same frozen threshold.
- `Δobese_cov(model)` = obese conformal coverage (from `test_set_prediction_sets.csv`,
  `mean(true class ∈ set)` over obese true-positives) at ≥ 12 vs ≥ 8.2.
- Interpretation: |Δobese| ≤ 0.10 → obese performance is stable across the stiffness range → the
  obese "advantage" is **not** carried by borderline (possibly-inflated) positives.

### 2.4 Computation C3 — stiffness-stratified sensitivity
- Band A: `8.2 ≤ LUXSMED < 10` (borderline; measurement-suspect). Band B: `LUXSMED ≥ 10`.
- For each band, each model, each BMI group: `sens = mean(pred_pos)` over `{group ∩ band}`.
- Report `sens(Obese, band) − sens(Normal, band)` for A and B. If the obese advantage is only in
  Band A → measurement-suspect; if in both → more likely a real detection gap (or a BMI shortcut,
  see C4).
- Note Band-A Normal-BMI n is tiny (≈ 22 − 9 = 13); report it.

### 2.5 Computation C4 — BMI-shortcut check
- Among **all** test participants (any outcome) with `8.2 ≤ LUXSMED < 12`:
  fit `predicted_probability ~ LUXSMED + C(bmi_group_final)` (OLS, per model), and separately bin
  by 0.5-kPa stiffness and compare mean `predicted_probability` for Obese vs Normal within each
  bin.
- If Obese gets a systematically higher score at matched stiffness (positive BMI coefficient) →
  the model uses BMI as a shortcut — a fairness concern that exists **independent of** any
  measurement bias, and one the paper should state.

### 2.6 Computation C5 — conformal coverage under stricter labels
- Recompute BMI-Obese and Age-60+ conformal coverage (from `test_set_prediction_sets.csv`) with
  `positive = LUXSMED ≥ 10` and `≥ 12`. (Obese N is large → this has power.)
- Does the under-coverage persist? Report the coverage and Wilson CI at each cut.

### 2.7 Verdict (apply 0.3's Fix-2 rule mechanically)
- [ ] Compute `G(12)` = median across models of `gap_bmi(model, 12)` from C1 and `Δobese` from C2.
- [ ] Assign **V1 / V2 / V3** per 0.3. Record the numbers that triggered it.
- [ ] Draft the Limitations paragraph carrying C1–C5 and the verdict.

### 2.8 Outputs
- `results/prepublication_fixes/fix2_gap_by_stiffness_threshold.csv` (C1)
- `results/prepublication_fixes/fix2_obese_side_highpower.csv` (C2)
- `results/prepublication_fixes/fix2_stiffness_stratified.csv` (C3)
- `results/prepublication_fixes/fix2_bmi_shortcut_check.csv` (C4)
- `results/prepublication_fixes/fix2_coverage_under_stricter_labels.csv` (C5)
- `documentation/prepublication_fixes/FIX2_VCTE_BIAS_SENSITIVITY.md` — narrative + verdict + the
  Limitations-paragraph draft + the §3.4 / §4.1 one-liners.

### 2.9 Verification checks
- [ ] `n_positive` per cut per group matches the counts in this plan (200/22/140, 115/9/86,
      75/7/53, 59/6/40 for ≥8.2/10/12/13.6).
- [ ] The `cut = 9.7` row of C1 matches `secondary_severity_outcomes_9p7_bmi_age_fairness.csv`
      within rounding (that file used the refit-independent frozen predictions; document any
      method difference).
- [ ] Reproducible bit-for-bit (seed 42).

---

# PHASE 3 — Fix 3: consolidate the mitigation narrative  ·  ~2.5 days (writing only)

### 3.1 Gather the three analyses
| Analysis | Source |
|---|---|
| Project Phase 7 Mondrian (5/9; XGBoost +5.3 pp breach; sequential overlap) | `PHASE7_MITIGATION_RESULTS_REPORT.md`, `results/mitigation/*` |
| BMI-investigation Phases 3–7 (7 strategies, none acceptable; two-mechanism finding) | `documentation/fairness_bmi_investigation/*`, `results/fairness_bmi_investigation/*` |
| Amendment #17 selective deferral (development-stage negative; 3d Mondrian 5/5 with over-coverage; mechanism) | `documentation/selective_deferral_mitigation/*`, `results/selective_deferral/*` |

### 3.2 Build the unified Table 4
Rows = method families; columns = Objective · Best result · Disposition:
- Subgroup decision thresholds → equalize subgroup sensitivity → BMI gap halved, **age gap +26–133 %**, ~40 pp specificity cost → EXPLORATORY, not a fix
- Subgroup / group calibration → improve subgroup reliability → ECE improved 3 models, gaps unchanged → NO ACCEPTABLE MITIGATION
- **Group-conditional (Mondrian) conformal** → restore subgroup coverage → ≥ 0.88 coverage for BMI-obese & age-60+ in **5/5 models** (Amdt #17 3d); original Phase 7: 5/9 + XGBoost breach; **cost: marginal over-coverage 0.94–0.95** → PARTIALLY EFFECTIVE
- Selective deferral → restore coverage via defer-to-elastography → **no improvement** (under-coverage is confidently-scored singletons, not flagged-uncertain cases) → NO IMPROVEMENT
- Equalized-odds post-processing → equalize TPR → ~399 excess FP / 1,000 normal-weight → EXPLORATORY, clinically unacceptable
- XGBoost retuning → remove coverage breach → 11–22 pp sensitivity cost → NO ACCEPTABLE RETUNING
- Joint intersectional conformal → restore Obese ∩ 60+ → ≥ 90 % for 4–5/5 on CAND_1, marginal breach for 2 → EXPLORATORY

### 3.3 Rewrite §3.7 to the single paragraph (fixed wording)
> Post-hoc mitigation was tested across four method families (subgroup decision thresholds;
> subgroup/group calibration; group-conditional [Mondrian] conformal recalibration; selective
> deferral) against pre-specified multi-metric gates. Group-conditional conformal recalibration
> was the most effective: it restored ≥ 0.88 subgroup coverage for BMI-obese and age-60+ in all
> five model families — improving on the initial 5-of-9 model×subgroup result — but at the cost of
> marginal over-coverage (0.94–0.95); returning marginal coverage to target would require
> deliberately under-serving the well-covered subgroups. No method closed the normal-weight
> classification sensitivity gap without a ~40-point specificity cost. Selective deferral could
> not improve coverage because the under-coverage is carried by confidently-scored singleton
> predictions, not flagged-uncertain cases. The residual failure is a within-subgroup
> score-ordering problem that post-hoc methods cannot repair; a training-time intervention
> (subgroup reweighting or a subgroup-aware objective) is the indicated next step and is outside
> this study's frozen scope.

### 3.4 Update registers to the single narrative
- [ ] `FINAL_SCIENTIFIC_FINDINGS.md` §14 · `FINAL_RESEARCH_AUDIT.md` §7 · `EXPLORATORY_RESULTS.md`
- [ ] `DO_NOT_CLAIM.md` — add: do not claim group-conditional conformal "solves" the failure;
      state the over-coverage cost; do not present selective deferral as effective.
- [ ] `RESEARCH_WEAKNESSES.md` W2 · `RESEARCH_STRENGTHS.md` #7 · `MANUSCRIPT_FRAMING_GUIDANCE.md`
- [ ] `results/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` — revise MIT-01…MIT-05,
      add `MIT-06` (selective deferral, NO IMPROVEMENT) and update the Mondrian row to "5/5
      subgroup coverage, over-covers marginally."

---

# PHASE 4 — fold Phases 1–2 into the manuscript  ·  ~3 days

### 4.1 Methods
- [ ] §2.4 / §2.7 — one paragraph: *"The subgroup fairness audit (§2.6) evaluated the Phase-3
      models, trained on the full training partition. The split-conformal analysis (§2.7)
      evaluated models refit on the proper-training subset, as the conformal architecture requires
      a disjoint calibration set. Findings are reported for each fit; §[3.4b] shows the body-mass
      sensitivity gap is present in both."*

### 4.2 Results
- [ ] New short **§3.4b** — "Consistency across model fits" — the Fix-1 comparison table + the
      STRENGTHENING / PARTIAL / CAVEAT verdict.
- [ ] Fix-2 goes into a short **§3.4c** *or* is merged into the Limitations paragraph (decide by
      whether the verdict changes a conclusion; V1 → Limitations paragraph; V2 → §3.4c + abstract
      change).

### 4.3 Discussion §4.1
- [ ] Update the body-mass paragraph: add the Fix-1 alignment result; add the Fix-2 verdict
      sentence.

### 4.4 Limitations §5
- [ ] Expand the reference-standard bullet [J3] into a paragraph carrying C1–C5 and the verdict.

### 4.5 Abstract / Conclusion — conditional on the Fix-2 verdict
- **If V1:** no abstract change; add one caveat clause to the Limitations sentence.
- **If V2:** the body-mass finding is **downgraded** — the abstract leads solely with the
  conformal / methodological finding; the body-mass gap is described as "directionally consistent
  but confounded by BMI-dependent measurement of the reference standard."
- **If V3:** abstract keeps the body-mass finding but adds "the contribution of BMI-dependent
  reference-standard measurement could not be excluded."

### 4.6 Registers
- [ ] `FINAL_LIMITATIONS_REGISTER.md` — new/expanded reference-standard item with the C1–C5 result.
- [ ] `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` — new rows `FAIR-BMI-03` (fit-alignment) and
      `FAIR-BMI-04` (VCTE-bias sensitivity + verdict).
- [ ] `documentation/manuscript/RESULTS_VERIFICATION.md` — addendum: every Phase-1/2 number
      checked against its CSV.

---

# PHASE 5 — validation & Amendment #18 closure  ·  ~1 day

- [ ] `tests/test_prepub_fixes.py`:
  - `test_ids` disjoint from `calibration_ids` and `proper_train_ids`
  - the two new scripts each record exactly one locked-test touch, timestamped after Phase 0
  - re-running each script reproduces every number (seed 42)
  - count identities: `n_pos(≥8.2)=200`, Normal 22, Obese 140; and the ≥10/12/13.6 counts
  - the pooled-FDR family count is incremented by the number of new hypothesis tests
- [ ] Independent spot-check of ≥ 15 new numbers against the result CSVs.
- [ ] `documentation/prepublication_fixes/AMENDMENT_18_CLOSURE.md` — what ran, the Fix-1 decision,
      the Fix-2 verdict, the residual (irreducible) limitation, the two test touches.
- [ ] Update `documentation/manuscript/README.md` → draft **v4**; note Fixes 1–3 done.
- [ ] Update `documentation/end_to_end/protocol_amendment_registry.md` row 18 with the outcome.
- [ ] Update `documentation/START_HERE.md` §7 (executed-after-consolidation list) with Amendment #18.

---

# Timeline

| Phase | | Days |
|---|---|---|
| 0 | Pre-registration | 0.5 |
| 1 | Fix 1 analysis | 1.5 |
| 2 | Fix 2 analysis | 3 |
| 3 | Fix 3 consolidation (writing) | 2.5 |
| 4 | Fold 1–2 into manuscript | 3 |
| 5 | Validation + closure | 1 |
| | **Total** | **≈ 11.5 working days ≈ 2–2.5 calendar weeks** |

# Risk register

| # | Risk | Trigger | Action |
|---|---|---|---|
| R1 | Fix 1 = CAVEAT (gap absent in refit fit) | Phase 1.6 | §3.5 drops the "same models as the fairness audit" phrasing; the two findings become independent; abstract unchanged (both still hold, just not linked). |
| R2 | Fix 2 = V2 (measurement bias inseparable) | Phase 2.7 | Body-mass finding downgraded per 4.5; conformal/methodological finding becomes the sole headline (it is the stronger finding regardless). |
| R3 | Fix 2 = V3 (underpowered) — likely given 7 Normal-BMI events at ≥12 | Phase 2.7 | Report the bounded statement; the obese-side (C2/C3/C5) still carries useful evidence; abstract adds the "cannot exclude" clause. |
| R4 | The derived Youden threshold (93 positives) is unstable | Phase 1.3 | 1.4 (threshold sweep) is the primary evidence; τ* reported as secondary with the n_positive caveat. |
| R5 | C4 shows a strong BMI shortcut | Phase 2.5 | This is a *finding*, not a problem — add it to §3.4 / §4.1 ("the models use BMI partly as a shortcut, detected by matched-stiffness score comparison"). |

# New files this plan creates

Docs: `AMENDMENT_18_TEXT.md`, `PRE_EXECUTION_SNAPSHOT.md`, `FIX1_MODEL_FIT_ALIGNMENT.md`,
`FIX2_VCTE_BIAS_SENSITIVITY.md`, `AMENDMENT_18_CLOSURE.md` (all under
`documentation/prepublication_fixes/`).
Code: `src/prepub_01_model_fit_alignment.py`, `src/prepub_02_vcte_bias_sensitivity.py`,
`tests/test_prepub_fixes.py`.
Results: `results/prepublication_fixes/fix1_*.csv` (4), `results/prepublication_fixes/fix2_*.csv` (5).
Modified: the manuscript, ~8 register files (Phases 3–4), `protocol_amendment_registry.md`,
`START_HERE.md`, `documentation/manuscript/README.md`.
