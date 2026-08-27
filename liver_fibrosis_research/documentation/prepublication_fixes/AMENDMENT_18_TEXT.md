# Protocol Amendment #18

**Date:** 2026-08-27
**Title:** Pre-publication sensitivity analyses — model-fit alignment and VCTE reference-standard
measurement bias — plus a Methods disclosure and a mitigation-narrative consolidation.

**Motivation.** A pre-submission read of the frozen study identified three issues:
(1) the subgroup fairness audit (§3.4) evaluated the Phase-3 models trained on the full training
partition, while the split-conformal analysis (§3.5–3.6) evaluated models refit on the
proper-training subset (the conformal architecture requires a disjoint calibration set); the
manuscript reads as if one model. (2) Vibration-controlled transient elastography over-reads liver
stiffness at high body-mass index, so some obese "significant-fibrosis" labels near the 8.2-kPa
cut-point may be inflated — a threat to the interpretation of the body-mass detection finding.
(3) Three overlapping mitigation analyses (Project Phase 7 Mondrian; BMI-investigation Phases 3–7;
Amendment #17 selective deferral) reach slightly different conclusions and are reported
separately.

**Change.**
- **Fix 1 (analysis).** Recompute the Normal-vs-Obese and Age-60+ subgroup sensitivity gap on the
  Phase-6 proper-train-refit models, using the cached refit predictions
  (`results/uncertainty/test_set_prediction_sets.csv`, `calibration_scores_*.csv`) — **no model is
  loaded**. Report the gap as conformal sensitivity (coverage among positives) and as
  classification sensitivity at a Youden threshold derived on the calibration set, across a
  threshold sweep. Decide STRENGTHENING / PARTIAL / CAVEAT by the rule pre-registered in
  `PREPUBLICATION_FIXES_PLAN.md` §0.3. Add a Methods paragraph disclosing the two fits.
- **Fix 2 (analysis).** Relabel the primary outcome at LUXSMED ≥ 8.2 / 9.7 / 10 / 12 / 13.6 kPa
  (model scores unchanged) and recompute the body-mass and age sensitivity gaps and the subgroup
  conformal coverage; run the obese-side high-power check, the stiffness-stratified sensitivity,
  and a matched-stiffness BMI-shortcut check. Assign the V1/V2/V3 verdict by the rule
  pre-registered in `PREPUBLICATION_FIXES_PLAN.md` §0.3. Expand the reference-standard limitation
  into a paragraph.
- **Fix 3 (writing only, no amendment force).** Consolidate the three mitigation analyses into one
  Results subsection and one table, and update the registers.

**What does not change.** No model is retrained; no hyperparameter is searched; no predictor or
outcome definition is altered; the primary outcome remains `LUXSMED ≥ 8.2 kPa`. All Fix-1/Fix-2
computations operate on frozen predictions and the frozen analysis dataset.

**Locked-test touches.** Two additional touches of the CAND_1 locked test — one per analysis
script (`src/prepub_01_model_fit_alignment.py`, `src/prepub_02_vcte_bias_sensitivity.py`), each a
single non-iterative run. Recorded in `documentation/phase3/test_set_lock.md` and this registry.
The project-wide pooled-FDR family count is incremented by the number of new hypothesis tests in
Phase 5.

**Pre-registered decision rules.** Fix-1 (STRENGTHENING / PARTIAL / CAVEAT) and Fix-2 (V1 / V2 /
V3) thresholds are fixed in `PREPUBLICATION_FIXES_PLAN.md` §0.3 before any script is run and are
applied mechanically. The consequence for the abstract (no change / body-mass finding downgraded
/ "cannot exclude" clause) is pre-written in §4.5 of that plan.

**Environment note.** joblib / scikit-learn / xgboost / lightgbm are not available in the
execution environment; the analyses use cached predictions and nonconformity scores only.
