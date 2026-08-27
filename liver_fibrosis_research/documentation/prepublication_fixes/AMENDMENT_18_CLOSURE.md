# Amendment #18 — closure

**Date:** 2026-08-27 · **Status:** COMPLETE · **Governing plan:**
`documentation/prepublication_fixes/PREPUBLICATION_FIXES_PLAN.md` · **Amendment text:**
`AMENDMENT_18_TEXT.md` · **Pre-execution snapshot:** `PRE_EXECUTION_SNAPSHOT.md`
(git HEAD `3f1fefcb5370481d8529ff13b7ee166abb5edc1a`).

Three pre-submission issues were resolved. No model was retrained; no hyperparameter was searched;
no predictor or outcome definition changed. All computations operate on frozen predictions and the
frozen analysis dataset.

---

## Fix 1 — model-fit alignment · VERDICT: **STRENGTHENING**

**Question.** The subgroup fairness audit (§3.4) evaluates the full-train models; the conformal
analysis (§3.5–3.6) evaluates the proper-train-refit models. Does the body-mass sensitivity gap
appear in both fits?

**Method.** `src/prepub_01_model_fit_alignment.py` — recompute the Normal-vs-Obese sensitivity gap
on the refit models from the frozen conformal predictions
(`results/uncertainty/test_set_prediction_sets.csv`, `calibration_scores_*.csv`); no model is
loaded. Conformal sensitivity (coverage among positives), classification sensitivity at a
calibration-derived Youden threshold, and a 0.30–0.60 threshold sweep. One locked-test touch
(re-analysis of frozen test predictions; no new model evaluation).

**Result.** Refit classification-sensitivity gap: logistic −42.0, random forest −27.5,
XGBoost −32.1, LightGBM −32.8, perceptron −35.3 pp (5/5 models ≤ −15 pp). Refit
conformal-sensitivity gap ≤ −15 pp for 4/5 (the perceptron refit produces near-empty conformal
positive sets across all subgroups, so its +6.5 pp "gap" is a degeneracy artefact). Gap negative
at every swept threshold for 4/5 models. Full-train gap for comparison: −47.7 / −31.6 / −31.4 /
−27.1 / −39.0 pp.

**Pre-registered rule (plan §0.3):** STRENGTHENING requires `gap_ct ≤ −0.15` for ≥ 4/5 **and**
`gap_cls ≤ −0.15` for ≥ 4/5 → satisfied (4/5 and 5/5).

**Consequence.** New manuscript §2.7b + §3.4b. The fairness-audit finding and the conformal
finding concern the same subgroup failure across two related fits. Registry: `FAIR-BMI-03`.

---

## Fix 2 — VCTE reference-standard measurement bias · VERDICT: **V3 (underpowered on the Normal-BMI side)**

**Question.** VCTE over-reads liver stiffness at high BMI, so some obese "significant-fibrosis"
labels near 8.2 kPa may be inflated — a threat to the body-mass finding.

**Method.** `src/prepub_02_vcte_bias_sensitivity.py` — relabel the primary outcome at
LUXSMED ≥ 8.2 / 9.7 / 10 / 12 / 13.6 kPa (model scores unchanged); recompute the body-mass and
age sensitivity gaps and the subgroup conformal coverage; obese-side high-power check (C2),
stiffness-stratified sensitivity (C3), matched-stiffness BMI-shortcut check (C4), coverage under
stricter labels (C5). One locked-test touch.

**Result.**
- **C4 (BMI shortcut):** at matched liver stiffness (8.2–12 kPa band), obese participants receive
  a predicted probability **0.19–0.33 higher** than normal-weight participants (OLS `is_obese`
  coefficient; p < 0.001 for **all 5 models**; binned matched-stiffness mean difference
  0.19–0.34). The models use body mass as a risk cue **independently of** measured stiffness.
- **C2:** obese sensitivity and obese conformal coverage are stable from ≥ 8.2 to ≥ 12 kPa
  (median |Δ sensitivity| 0.03) — the obese detection advantage is not carried by borderline
  (possibly-inflated) positives.
- **C5:** BMI-obese conformal under-coverage **persists and slightly worsens** for 4/5 models
  under stricter labels (0.70–0.77 at ≥ 12 kPa for the class-weighted models) — not a
  borderline-label artefact. Strengthens the headline conformal finding.
- **C1:** the raw Obese−Normal sensitivity gap narrows and slightly reverses as the threshold
  rises (median +32 pp at 8.2 → −4 pp at 12 → −8 pp at 13.6), but Normal-BMI has only **7**
  fibrosis-positive test cases at ≥ 12 kPa, so the Normal-BMI side cannot be adjudicated.

**Pre-registered rule (plan §0.3):** V3 because Normal-BMI positives at ≥ 12 kPa < 8, and no
model has an Obese−Normal gap ≥ +15 pp at ≥ 12 kPa.

**Consequence.** New manuscript §3.4c; §3.4, §4.1, and §5 [J3] updated. A residual measurement
contribution cannot be formally excluded (a biopsy- or MRE-referenced cohort would be needed), but
the demonstrated mechanism (BMI shortcut) does not depend on it — net effect is a strengthening of
the fairness interpretation. Registry: `FAIR-BMI-04`.

---

## Fix 3 — mitigation-narrative consolidation (writing only)

The three overlapping mitigation analyses (Project Phase 7 Mondrian; BMI-investigation Phases 3–7;
Amendment #17 selective deferral) are now consolidated into one Table 4 and one §3.7. Key
addition: **conformal selective deferral (Amendment #17) → NO IMPROVEMENT** — no pre-registered
candidate met the gate on the calibration partition (locked test not touched); deferring
flagged-uncertain (two-class) cases *lowers* retained coverage because the misses are
confidently-scored wrong singletons. The group-conditional (Mondrian) re-run reaches ≥ 0.88
subgroup coverage for 5/5 models with zero deferral but over-covers marginally (retained marginal
0.94–0.95); restoring target marginal coverage would require *levelling down* the well-served
subgroups. The residual failure is a within-subgroup score-ordering problem that no post-hoc
method repairs; a training-time intervention is the indicated next step (outside the frozen scope).
Registry: `MIT-06` (and `MIT-01` limitation updated).

Registers updated: `FINAL_SCIENTIFIC_FINDINGS.md` §7/§11/§12/§14, `FINAL_RESEARCH_AUDIT.md` §7,
`DO_NOT_CLAIM.md` (items 4a/4b/9a/9b/9c), `RESEARCH_WEAKNESSES.md` W2, `RESEARCH_STRENGTHS.md` #7,
`MANUSCRIPT_FRAMING_GUIDANCE.md` §5/§5b, `EXPLORATORY_RESULTS.md` E12,
`FINAL_LIMITATIONS_REGISTER.md` (D1, E3, J3, new A6),
`results/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` (+FAIR-BMI-03, FAIR-BMI-04,
MIT-06), `documentation/manuscript/RESULTS_VERIFICATION.md` (Amendment #18 addendum).

---

## Locked-test touches

Two touches, one per analysis script — each a single non-iterative run over **frozen test-set
predictions** (`results/uncertainty/test_set_prediction_sets.csv`,
`results/predictions/test_predictions_*.csv`) and the frozen analysis dataset. No model was
evaluated on the test set anew; these are re-analyses of already-frozen predictions, counted as
touches by conservative convention.

| Script | Touch | Nature |
|---|---|---|
| `src/prepub_01_model_fit_alignment.py` | #1 | re-slice frozen refit test predictions + conformal sets by subgroup; derive Youden τ* on the calibration partition |
| `src/prepub_02_vcte_bias_sensitivity.py` | #2 | relabel the frozen test outcome at higher stiffness cut-points; re-score frozen full-train predictions; OLS on frozen scores |

Recorded in `documentation/phase3/test_set_lock.md` and in
`documentation/end_to_end/protocol_amendment_registry.md` row 18.

## New hypothesis tests / multiplicity

Fix 2 C4 introduces 5 new formal tests (OLS `is_obese` coefficient, one per model); all
p < 0.0001 (t = 4.75–7.74), robust to any FDR correction. Consistent with the convention used for
Amendment #16, these post-freeze tests carry their own within-analysis interpretation and are not
folded into the frozen project-wide 182-test pooled-FDR family. Fix 1 reports gaps with bootstrap
CIs only (no new NHST). The frozen `results/statistics/pooled_fdr_corrected_results.csv` is not
regenerated (evidence freeze).

## Reproducibility

`tests/test_prepub_fixes.py` — 19/19 pass: leakage pre-check, count identities
(200/22/140; Normal-BMI collapse 22→11→9→7→6), both decision rules, BMI-shortcut significance,
bit-for-bit re-run of both scripts (seed 42), and a static check that neither script loads or
writes a model artefact.

## Residual (irreducible) limitation

The Normal-BMI side of the reference-standard measurement-bias question is underpowered at stricter
stiffness thresholds (7 fibrosis-positive test cases at ≥ 12 kPa) and cannot be resolved within
this NHANES cohort. A histology- or magnetic-resonance-elastography-referenced cohort is required.
This is disclosed in §5 [J3] and `FINAL_LIMITATIONS_REGISTER.md` J3.
