# PDF ↔ repository reconciliation checklist

**Purpose.** You are rebuilding the submission PDF yourself. This is the list of
every place the compiled PDF (`documentation/manuscript/conference_submission_2026-09-04.pdf`,
"Reliability Beyond Accuracy", Kashyap & Meheta, IEEE two-column — git-ignored, kept
locally only) diverges from the repository
manuscript of record (`documentation/manuscript/MANUSCRIPT_DRAFT.md`, v5). For
each item: what the PDF says, what is correct, and the frozen source.

The repo manuscript is the numerically-verified version — 43/43 checks pass in
`manuscript_verification/verify.py`. Where the two disagree, **the repo + the raw
artifact win** (this is the `START_HERE.md` §1 authority order; post-`evidence-freeze`
the artifact governs).

Legend: 🔴 factual error in the PDF · 🟠 stale / superseded content · 🟡 structure/style · ⚪ decision needed

---

## 🔴 Factual errors in the PDF — must change

### R1 · Phase 8 holdout calibration intercepts (PDF §IV-G)
- **PDF says:** "recalibrated intercepts shifting to −0.38 to −0.18 … A separate
  summary document reported a substantially larger drift (−2.17 to −0.58) … we
  adopt the pipeline-file-sourced estimate as primary here."
- **Correct:** **−0.58 to −2.17**, and they are **raw** intercepts — *no
  recalibration was performed on the holdout models* (Phase 8 report §12: "No
  recalibration was performed — this is an assessment, not a fix").
- **Source:** `results/validation/phase8_generalization_results.csv`,
  column `calibration_intercept` = −2.169, −1.886, −2.049, −2.037, −0.577.
- **Action:** state "−0.58 to −2.17 (raw; the holdout models were not
  recalibrated)". Delete the "separate summary document / we adopt" sentence
  entirely — a submission resolves the discrepancy, it does not narrate it.
- Pinned by harness check `GEN-01-INTERCEPT`.

### R2 · "should be confirmed by re-running Phase 8" (PDF §IV-G)
- **PDF says:** "This discrepancy should still be confirmed by re-running the
  Phase 8 holdout evaluation before the number is treated as final."
- **Correct:** the frozen artifact is final. Delete the sentence.

### R3 · Severity-graded secondary outcomes execution status (PDF §IV-H)
- **PDF says:** "We flag this internal inconsistency: the project's own results
  log at one stage marked these secondary-threshold analyses as unexecuted; a
  cross-check source reports them as completed … we recommend confirming
  execution status against the pipeline's run manifest before treating them as
  final."
- **Correct:** they **were executed** — **Amendment #15, 2026-08-27**, as a
  relabel-only descriptive pass. No retraining, no Platt refit, no conformal
  repeat, locked test not re-accessed for fitting.
- **Source:** `results/sensitivity/secondary_severity_outcomes_results.csv`
  (10 rows; `retrained=False`, `platt_refit=False`, `conformal_repeated=False`,
  `test_set_reaccessed_for_model_fitting=False` on every row);
  `results/sensitivity/secondary_severity_outcomes_lineage.json`;
  amendment-registry row 15.
- **Action:** delete the "internal inconsistency / we recommend confirming"
  paragraph. Cite Amendment #15. Report AUROC 0.85–0.86 (≥9.7 kPa) and
  0.84–0.86 (≥13.6 kPa); state the frozen 8.2-kPa Platt recalibration does not
  transport to the rarer outcomes.
- Pinned by harness checks `SECOUT-01-*`.

### R4 · Fig 3 (M4b bar chart) built from the wrong quantile column
- **PDF caption says:** "the values plotted here for Random Forest and LightGBM
  differ from the prespecified-CV values reported in the text and Table V (which
  use the `q_m4b_cal` quantile column); this figure should be regenerated from
  that column before inclusion in a final submission."
- **Correct:** see R6 — M4b is removed from the manuscript by Amendment #20, so
  this figure is **cut**, not regenerated. (If you keep it as an exploratory
  supplement, regenerate strictly from `q_m4b_cal`.)

### R5 · Fig 4 (coverage-vs-set-size Pareto) uses a superseded M4b parameter
- **PDF note says:** "the M4b marker shown here uses an exploratory shrinkage
  weight of N₀ = 100 … superseded by the prespecified, cross-validation-selected
  N₀* = 0."
- **`DO_NOT_CLAIM.md` #12:** "Do not report N0=100 as the M4b parameter
  (SUPERSEDED by N0=0)."
- **Action:** with M4b removed (R6) this figure is cut. This was the PDF's former
  "Figure 3: Intersectional Coverage vs. Efficiency" / Amendment #20's former
  Supplementary S1 (`figure3_coverage_vs_set_size_tradeoff.png`) — Amendment #20
  removed it and renumbered former S2 → S1.

---

## 🟠 Superseded / stale content in the PDF — remove or relabel

### R6 · M4b joint-cell conformal + MI conformal are removed from the manuscript (Amendment #20)
- The PDF presents both as results: §IV-D/§IV-E, Table V rows "Prespecified M4b"
  and "Faithful AFCP" and "Exploratory direct joint", Appendix C (M4b formula),
  Figures 3/4/5.
- **Amendment #20 (2026-08-28)** removed the MI **conformal** extension
  (`LINEAGE NOT FOUND`) and the joint-cell / M4b intersectional conformal
  mitigation (generating pipeline `NOT FOUND`; its "≥ 90%" carried an
  XGBoost/LightGBM marginal-tolerance breach) from `MANUSCRIPT_DRAFT.md` —
  structured abstract, §2.8, §3.7, §5, Table 4, Appendix A row MIT-05, Figures.
- **Action:** cut M4b and MI-conformal from the PDF too. What stays: the MI
  **selection-question** discrimination/calibration analysis (full lineage) and
  the Phase-7 Mondrian mitigation. AFCP: `DO_NOT_CLAIM.md` #10 — do not cite the
  KNN-AFCP result at all; faithful AFCP is EXPLORATORY, no superiority claim.
  Simplest: drop the AFCP row from the PDF's Table V.

### R7 · Amendment #19 (training-time mitigation) is missing from the PDF
- The repo manuscript v5 has a full **§3.7b** (Kamiran–Calders subgroup instance
  reweighting; **VERDICT: NEGATIVE**), two extra rows in Table 4, and abstract +
  §4/§4.1/§5/§6 sentences.
- **Source:** `results/training_time_mitigation/*`;
  `documentation/training_time_mitigation/AMENDMENT_19_CLOSURE.md`.
- **Key numbers (harness-pinned):** matched-stiffness BMI coefficient collapses
  0.18–0.25 → 0.008–0.036 OOF; Normal-vs-Obese sensitivity gap halves
  (+27–48 → +14–17 pp; BH-sig 5/5 → 0/4); BMI-Obese conformal coverage
  0.77–0.82 → 0.86–0.87 (still < 0.88); cost: test AUROC −0.02 to −0.03,
  specificity up to −12 pp, a new BH-significant logistic Female disparity
  (−15.1 pp); joint BMI×age arm worsened the age gap.
- **Action:** port §3.7b and the Table 4 rows into the PDF. This is a
  *strengthening* addition — "we tried the obvious training-time fix and it
  failed the gate" closes a reviewer question.

### R8 · Selective-deferral mitigation (Amendment #17) — confirm it's in the PDF
- Repo §3.7 carries the conformal selective-deferral result (VERDICT:
  DEVELOPMENT-STAGE NEGATIVE — no candidate met the gate; locked test not
  touched; the under-coverage is confidently-scored wrong singletons).
- **Source:** `results/selective_deferral/*`;
  `documentation/selective_deferral_mitigation/`.
- **Action:** if absent from the PDF, add the one-paragraph result + the Table 4 row.

### R9 · Funding / affiliation statement contradicts the repo
- **PDF Acknowledgment:** "This work was supported by the Department of Computer
  Science, Guru Gobind Singh Indraprastha University."
- **Repo Declarations:** "received no specific grant … The author is an
  independent researcher and self-funded this work."
- **Action:** ⚪ decide which is true and make both consistent. If GGSIPU
  provided no funding, the PDF line should be an acknowledgement of institutional
  support (compute/library access), not funding — or removed.

---

## 🟡 Structure / numbering / framing

### R10 · Figure numbering is broken in the PDF
- Two figures numbered **"Figure 3"** (M4b intersectional-coverage bar chart;
  and "Intersectional Coverage vs. Efficiency (Set Size) Trade-Off" scatter).
- Two numbered **"Figure 5"** (M4b Intersectional Coverage across Models; and
  "Sensitivity of the M4b shrinkage method to prior weight N₀").
- **Repo Figures list (clean, use this):** 1 = ROC + PR; 2 = calibration curves
  raw vs recalibrated; 3 = sensitivity by BMI band; 4 = conformal coverage by
  subgroup; 5 = fairness–specificity Pareto (BMI + age); S1 = liver-stiffness
  distributions by BMI/age/sex/race. See `manuscript_verification/figure_manifest.csv`.
- With M4b/AFCP cut (R6), the PDF's Figs 3/4/5(first) go away and the numbering
  resolves.

### R11 · Cohort-flow numbers
- **PDF §III-A:** 10,409 → 9,023 → 7,768 → 7,153 (4 steps).
- **Repo §2.1:** 10,409 → 9,700 → 9,023 → 7,768 → 7,153 (5 steps; the 9,700 step
  is "elastography attempted and non-missing stiffness").
- **Action:** use the repo's 5-step flow; it matches the participant flow
  diagram you still need to draw (`SUBMISSION_CHECKLIST.md` A5).

### R12 · Reference list: 15 (PDF) vs 28 (repo, verified)
- The PDF omits, among others: the fairness-metrics scoping review; the
  selective-classification / learning-to-defer papers; the cost-aware conformal
  deferral paper; Rafe & Das (socio-conformal, the independent marginal-vs-
  subgroup replication); Cresswell et al. (conformal sets → disparate impact);
  Zhou & Sesia / AFCP; conformal risk control; TRIPOD+AI.
- **Action:** adopt the repo's 28-reference list and its in-text `[n]` markers.
  Status and corrections: `documentation/manuscript/REFERENCE_VERIFICATION.md`
  (note F1 Cao-not-Zhou, F3 merge 22+23). Remaining `[author list to confirm]`:
  see `manuscript_verification/reference_bylines.md`.

### R13 · Title and author line
- ⚪ **Title:** PDF = "Reliability Beyond Accuracy: …"; repo = "Discrimination and
  aggregate calibration are insufficient evidence of subgroup-safe reliability:
  …". Pick one and set it in both places. (The repo title states the thesis; the
  PDF title is more conventional. Either is defensible — just converge.)
- ⚪ **Authors:** PDF = two (Kashyap, Meheta). Repo = single author throughout
  (Declarations: "The single author designed the study …"; `SUBMISSION_CHECKLIST.md`
  B4). **Decide now** — it changes the Declarations, Author Contributions, the
  cover letter, and whether the internal audit trail substitutes for co-author
  review (`SUBMISSION_CHECKLIST.md` A10, B4).

### R14 · Abstract
- The PDF abstract is one long unstructured stat-dense block. The repo abstract
  is structured (Background / Methods / Results / Conclusions) and is the better
  starting point — port it, then trim per journal word limit.

### R15 · Headline framing — align to the repo (recommended, not just cosmetic)
- The PDF frames the contribution around **co-occurrence / convergence** of
  fairness and conformal failures. The repo's own reliability extension
  (`RELIABILITY_EXTENSION_RESULTS_REPORT.md`) shows the *general* co-occurrence
  is **not statistically supported** once subgroup clustering is respected
  (dependence-aware permutation p = 0.12). The narrow finding (BMI-Obese and
  Age-60+ each show both problems) holds on its own.
- The repo manuscript v5 leads instead with the **dissociation**: marginal
  conformal coverage is not a subgroup-safety property; on BMI the model is
  fairness-favorable and reliability-unfavorable toward *opposite* groups; no
  mitigation fixes it. That framing survives the robustness check.
- **Action:** move the PDF's "convergence" language to a secondary observation;
  lead with the dissociation + "discrimination + aggregate calibration are
  insufficient evidence of subgroup-safe reliability".

---

## Quick pre-rebuild gate

Before you compile the PDF, from the repo root:

```bash
python3 manuscript_verification/verify.py --strict
```

Expect: 43 checks pass, and the hedge scan lists only the reference-byline TODOs
(tracked in `reference_bylines.md`) — no number errors, no execution-status
hedges, no "regenerate before submission" notes.
