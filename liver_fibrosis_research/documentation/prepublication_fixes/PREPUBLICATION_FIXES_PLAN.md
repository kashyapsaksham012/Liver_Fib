# Pre-publication fixes — plan

**Created 2026-08-27.** Three issues identified as needing action before the manuscript is
submittable. This plan says exactly how each is fixed, what is analysis vs writing, and what is
**irreducible** (must be disclosed, cannot be solved with this data).

| # | Issue | Type | Amendment? |
|---|---|---|---|
| **1** | §3.4 (BMI classification sensitivity) uses the Phase-3 full-train models; §3.5–3.6 (conformal coverage) use the Phase-6 proper-train-refit models. The paper reads as one model. | small analysis + disclosure | **#18** |
| **2** | VCTE over-reads liver stiffness at high BMI → some obese "positive" labels near 8.2 kPa may be inflated → threat to the primary body-mass finding's interpretation. | small analysis + honest bounded disclosure (partly irreducible) | **#18** |
| **3** | Three overlapping mitigation analyses (Project Phase 7 / BMI-investigation Phases 3–7 / Amendment #17 selective deferral) with slightly different conclusions. | writing / consolidation only | none |

**Non-negotiables (all fixes):** no retraining; work from frozen predictions / nonconformity
scores / the frozen analysis dataset; locked test touched once per new analysis under Amendment
#18; no post-hoc changes to any frozen result; every new number verified against its artifact.

---

## What is already known / already partly done

- **Fix 2 is partly answered by Amendment #15** (severity-graded relabel). At LUXSMED ≥ 9.7 kPa the
  BMI-Obese vs Normal-BMI sensitivity disparity is **still positive in 5/5 models** (logistic
  +35.6, RF +17.4, XGBoost +19.6, LightGBM +19.6, MLP +22.9 pp) — the direction persists — but
  Normal-BMI has only **11 test positives** at that cut and the CIs are wide (mostly include 0).
- **Fix 2 has an irreducible core.** Normal-BMI fibrosis-positive test counts: 22 (≥ 8.2), 9
  (≥ 10), 7 (≥ 12), 6 (≥ 13.6 kPa). A stricter-threshold sensitivity comparison rests on
  ≤ 9 Normal-BMI events — **uninterpretable as a point estimate**. This data cannot fully exclude
  a measurement-bias contribution; the fix is a defensible bounded statement, not a resolution.
- **Fix 1** is tractable: the refit models' test-set predictions are cached
  (`results/uncertainty/test_set_prediction_sets.csv`), so the subgroup sensitivity gap can be
  recomputed on the refit fit without loading any model.

---

## Phase A — Amendment #18 + snapshot · ~0.5 day

- [ ] Draft **Amendment #18** (covers the Fix-1 and Fix-2 analyses; Fix 3 is writing, no
      amendment). Add to `documentation/end_to_end/protocol_amendment_registry.md`.
- [ ] `documentation/prepublication_fixes/PRE_EXECUTION_SNAPSHOT.md` — SHA-256 of the inputs:
      `analysis_dataset_primary.parquet`, `data/processed/splits/test_ids.csv`,
      `results/predictions/test_predictions_*.csv`,
      `results/uncertainty/test_set_prediction_sets.csv`,
      `results/uncertainty/calibration_scores_*.csv`,
      `results/sensitivity/secondary_severity_outcomes_9p7_bmi_age_fairness.csv`.
- [ ] Pre-register the exact analyses below (this document is that pre-registration).

---

## Phase B — Fix 1: does the subgroup gap appear in *both* model fits? · ~1–2 days

**Script:** `src/prepub_01_model_fit_alignment.py`. Reads only cached predictions.

- [ ] Compute, on the **locked test**, the refit models' (`test_set_prediction_sets.csv`,
      column `predicted_probability_positive`) subgroup **conformal sensitivity** = coverage among
      true positives = fraction of positives whose prediction set includes `positive` — for
      Normal-BMI, Obese, Age-40–59, Age-60+.
- [ ] Derive a Youden-optimal operating threshold for each refit model **on the conformal-
      calibration set** (`calibration_scores_*.csv`; 93 positives — note the reduced precision vs
      the Phase-3 threshold's 466 OOF positives). Apply to the refit test predictions. Compute
      classification sensitivity by subgroup and the Normal-vs-Obese / Age-60+ gaps.
- [ ] Also report the gap at a **range** of thresholds (0.30–0.60 grid) to show it is
      threshold-robust, not an artifact of one noisy cut.
- [ ] Compare to the Phase-5 full-train numbers (`results/fairness/fairness_inference.csv`).
- [ ] **Deliverable / expected outcome:** a table showing the Normal-vs-Obese sensitivity gap in
      *both* fits. Preliminary evidence from the Amendment-#17 development run
      (`results/selective_deferral/phase3_candidate_metrics.csv`, the no-deferral rows) already
      shows the refit models' conformal sensitivity is ~0.56–0.78 (Normal-BMI) vs ~0.97–0.99
      (Obese) for 4/5 families — i.e. the gap **does** appear in the refit fit. Phase B confirms
      this on the test set and quantifies it.
      → `documentation/prepublication_fixes/FIX1_MODEL_FIT_ALIGNMENT.md`

**If the gap appears in both fits (expected):** Fix 1 becomes a *strengthening* — the paper says
"the same subgroup failure is present in both model fits" and a one-paragraph Methods disclosure
of the two fits.
**If the gap appears only in the full-train fit:** Fix 1 becomes a material caveat — §3.5 can no
longer claim the conformal failure hits "the same populations flagged by the fairness audit" in
the same models; the two findings must be presented as independent.

---

## Phase C — Fix 2: VCTE measurement-bias sensitivity (what is possible) · ~2–3 days

**Script:** `src/prepub_02_vcte_bias_sensitivity.py`. Relabel-only on frozen test predictions +
`LUXSMED`.

- [ ] **(C1) Direction across stiffness thresholds.** BMI-Obese vs Normal-BMI sensitivity gap and
      the subgroup conformal coverage recomputed with positives defined at LUXSMED ≥ 8.2 / 9.7 /
      10 / 12 kPa, all five models. Show the direction persists and the Normal-BMI CI widens to
      uninformative — quantify the power collapse explicitly.
- [ ] **(C2) Obese-side, where there is power.** Restrict the Obese group's positives to
      LUXSMED ≥ 12 kPa ("unambiguous fibrosis, minimal measurement concern"; 53 obese events) and
      recompute Obese sensitivity + Obese conformal coverage. If similar to the full Obese group
      → the obese performance is **not** driven by borderline (possibly-inflated) cases.
- [ ] **(C3) Stiffness-stratified sensitivity.** Model sensitivity by BMI band *within* the
      8.2–10 kPa band vs the ≥ 10 kPa band. Tests whether the "obese advantage" is concentrated in
      the borderline band (measurement-suspect) or holds across the range.
- [ ] **(C4) Concordant vs BMI-driven.** Among participants in the 8.2–10 kPa band, is model
      P(positive) higher for obese than for normal-weight *at matched stiffness*? (A crude check
      of whether the model uses BMI as a shortcut, independent of measurement bias.)
- [ ] **Verdict (pre-registered wording):** one of —
      *"the disparity persists across stiffness thresholds and within the unambiguous-fibrosis
      subset, arguing against a purely measurement-driven explanation (though Normal-BMI power is
      limited)"* — or —
      *"the disparity attenuates substantially when borderline-stiffness positives are excluded,
      indicating a measurement-bias contribution that cannot be separated from a genuine detection
      gap in this data"* — or —
      *"the analysis is underpowered on the Normal-BMI side and cannot adjudicate; a
      biopsy- or MRE-referenced cohort is required."*
      → `documentation/prepublication_fixes/FIX2_VCTE_BIAS_SENSITIVITY.md`

- [ ] **Manuscript:** expand Limitation [J3]/[reference-standard measurement bias] from a bullet
      into a short paragraph carrying the C1–C4 result and the verdict. Add one sentence to §3.4
      and §4.1.

---

## Phase D — Fix 3: consolidate the mitigation narrative · ~2–3 days (writing only)

- [ ] Replace §3.7 with **one** paragraph covering all mitigation work: four method families
      (subgroup decision thresholds; subgroup/group calibration; group-conditional [Mondrian]
      conformal; selective deferral) evaluated against pre-specified multi-metric gates.
- [ ] Replace **Table 4** with one integrated table (method family → objective → best result →
      disposition).
- [ ] The unified conclusion (fixed wording to draft from):
      > *Post-hoc mitigation was tested across four method families. Group-conditional (Mondrian)
      > conformal recalibration was the most effective: it restored ≥ 0.88 subgroup coverage for
      > BMI-obese and age-60+ in all five model families — improving on the initial 5-of-9
      > model×subgroup result — but at the cost of marginal over-coverage (0.94–0.95); returning
      > marginal coverage to target would require deliberately under-serving the well-covered
      > subgroups. No method closed the normal-weight classification sensitivity gap without a
      > ~40-point specificity cost. Selective deferral could not improve coverage because the
      > under-coverage is carried by confidently-scored singleton predictions, not
      > flagged-uncertain cases. The residual failure is a within-subgroup score-ordering problem
      > that post-hoc methods cannot repair; a training-time intervention (subgroup reweighting or
      > a subgroup-aware objective) is the indicated next step and is outside this study's frozen
      > scope.*
- [ ] Update the registers to the single narrative: `FINAL_SCIENTIFIC_FINDINGS.md` §14,
      `FINAL_RESEARCH_AUDIT.md` §7, `DO_NOT_CLAIM.md`, `RESEARCH_WEAKNESSES.md` (W2),
      `MANUSCRIPT_FRAMING_GUIDANCE.md`, `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` (MIT rows +
      the new DEFER row).
- [ ] Fold the Amendment-#17 selective-deferral work in as part of this narrative (it is not a
      separate result section — it is one of the four method families).

---

## Phase E — fold B & C into the manuscript · ~2–3 days

- [ ] **Methods §2.4 / §2.7:** one paragraph — "The fairness audit (§2.6) evaluated the Phase-3
      models (trained on the full training partition). The split-conformal analysis (§2.7)
      evaluated models refit on the proper-training subset, as the conformal architecture
      requires a held-out calibration set. The subgroup findings are reported for each fit;
      §3.[B-ref] shows the body-mass sensitivity gap is present in both."
- [ ] **Results:** short §3.4b (Fix 1 — gap in both fits) and §3.4c / Limitations paragraph
      (Fix 2 — VCTE-bias sensitivity + verdict).
- [ ] **Abstract / Discussion / Conclusion:** adjust only if Phase C's verdict is the
      "attenuates substantially" branch (then the body-mass finding is downgraded and the
      conformal/methodological finding becomes the sole headline).
- [ ] Update `FINAL_LIMITATIONS_REGISTER.md`, `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv`,
      `RESULTS_VERIFICATION.md` (addendum for every new number).

---

## Phase F — validation + Amendment #18 closure · ~1 day

- [ ] `tests/test_prepub_fixes.py`: leakage (no train rows in any new test computation),
      single-touch record, number reproducibility, count identities.
- [ ] Independent spot-check of ≥ 15 new numbers against artifacts.
- [ ] `documentation/prepublication_fixes/AMENDMENT_18_CLOSURE.md` — what ran, the verdicts, the
      residual (irreducible) limitations.
- [ ] Update `documentation/manuscript/README.md` status → v4.

---

## Timeline

| Phase | Days |
|---|---|
| A Amendment + snapshot | 0.5 |
| B Fix 1 analysis | 1.5 |
| C Fix 2 analysis | 3 |
| D Fix 3 consolidation (writing) | 3 |
| E Fold B & C into manuscript | 3 |
| F Validation + closure | 1 |
| **Total** | **≈ 12 working days ≈ 2–2.5 calendar weeks** |

## Honest expectations

- **Fix 1:** almost certainly a *strengthening* (the gap is in both fits per the preliminary
  numbers). Small risk it becomes a caveat.
- **Fix 2:** partly resolved (direction persists at ≥ 9.7 kPa), partly **irreducible** (Normal-BMI
  power). The realistic outcome is a *bounded, defensible* limitation statement backed by the
  obese-side and stiffness-stratified analyses — not a clean resolution. If C's verdict is
  "attenuates substantially," the body-mass finding is demoted and the paper's headline shifts
  fully to the conformal / methodological point — which is the more defensible headline anyway.
- **Fix 3:** pure writing; low risk; makes the paper read as one coherent story instead of three.

After Phase F the analysis is genuinely closed. Everything past that point is writing and the
systematic literature search.
