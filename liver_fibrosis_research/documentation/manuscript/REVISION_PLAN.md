# Revision plan — `research_doc (4).pdf` (6-page conference submission)

**Note (reconstructed 2026-09-14, post-session):** this file was found deleted from disk
(never committed to git — it was untracked from its original creation) partway through the
revision session that also produced the clinical-baseline and survey-weighted addenda below.
It has been reconstructed verbatim from conversation record and updated with a status log
(Section G) reflecting what has actually been done since. Nothing in Sections A–F below was
altered from the original plan; only Section G is new.

**Reviewed against:** `documentation/manuscript/MANUSCRIPT_DRAFT.md` (manuscript of record) and
the frozen result artifacts it cites. Nothing in either source was modified to produce this plan.
`research_doc (4).pdf`: 6 pages (pdfinfo), untracked by git, four authors (Kashyap, Mehata,
Thapa, Singh; Guru Gobind Singh Indraprastha Univ.), 35 references.

---

## A. ONE-SENTENCE CLAIM

**Keep:** *A standard subgroup-fairness audit and a standard split-conformal coverage audit of
the same liver-fibrosis risk models disagree in direction across the same body-mass subgroups —
the group that is fairness-disadvantaged (normal-BMI, under-sensitivity) is the group that is
reliability-advantaged (over-coverage), and vice versa for obese participants — so passing one
audit gives no evidence about the other.*

The current draft defends at least three claims as co-equal:
1. The BMI-axis fairness/coverage direction-dissociation (above). **Keep — this is the only
   claim with a stated, checkable delta over prior work.**
2. A comprehensive negative mitigation battery (five methods — Mondrian, retuning, selective
   deferral, equal-opportunity post-processing, training-time reweighting — none passing the
   pre-registered gate). **Cut to one supporting paragraph.** This is a second, independent
   contribution class (intervention evaluation) competing for the same six pages; only the
   training-time-reweighting result is mechanistically tied to claim 1 (it is the only
   intervention shown to move the matched-stiffness coefficient, §IV.D/E) and should be the one
   kept in the main text.
3. The two-mechanism separation (threshold-driven BMI effect vs. non-threshold-driven age
   effect, §IV.D). **Cut to two sentences.** Interesting, but it is a diagnostic in service of
   claim 1, not a third finding; the restricted-cubic-spline detail and the 70+ sub-band note add
   nothing a reviewer needs to accept or reject the paper's claim.

---

## B. DELTA STATEMENT

**Closest prior work: [28]** (A. Rafe and S. Das, "Socio-conformal calibration in complex survey
data: marginal validity is not enough for subgroup reliability," arXiv:2605.05562, 2026) — its
title states almost exactly this paper's headline framing, which makes it the single most
dangerous piece of prior work in the paper's own bibliography.

**Delta (three sentences).** [28] shows that a group-conditional *conformal calibration method*
applied to complex survey data can itself misbehave — worsening both the coverage gap and
set-size efficiency under thin subgroup cells unless shrinkage-regularized — which is a property
of a correction method under sparse data. This paper reports a different, upstream fact observed
with **no correction applied**: on raw split-conformal output, the direction of a standard
sensitivity-based fairness disparity and the direction of a standard conformal-coverage failure
are anti-correlated across the same BMI subgroups (fairness-disadvantaged normal-BMI over-covers;
fairness-advantaged obese under-covers), which is a property of the model-and-subgroup structure,
not of any calibration method's behavior under sparsity. Because [28]'s failure mode is triggered
by thin cells and correction-method choice, while this paper's dissociation appears pre-correction
in cells that are not uniformly thin (obese N=883, normal N=562), the two are not the same
phenomenon restated on a new dataset.

**Strongest objection a reviewer could raise, using only references already in the
bibliography:** [27] (fair conformal predictors, medical imaging) and [29] (conformal prediction
sets can cause disparate impact) already establish that conformal coverage and other fairness
desiderata trade off against each other in other domains; combined with [28], a reviewer can
argue that "coverage and fairness don't align" is already a established, multi-domain finding,
and this paper only relocates it to liver fibrosis — a thin, dataset-swap contribution.

**Answer:** [27] and [29], like [28], describe what happens *when a correction or a specific
conformal-set construction is applied* (a fairness-constrained conformal predictor in [27]; a
disparate-impact side effect of set construction in [29]). None of [27]–[29] report a
*pre-correction* directional relationship between an independently-defined fairness metric
(subgroup sensitivity at a fixed operating point) and split-conformal coverage on the same
subgroup axis. This paper's contribution is that the two audits, run separately and without any
attempt to reconcile them, already point in opposite directions before any mitigation is
attempted — which is what makes marginal conformal validity uninformative about subgroup safety
even for a practitioner running no mitigation at all. This is currently *asserted* rather than
*shown against [27]–[29] explicitly*; see Change Table row C15.

---

## C. CHANGE TABLE

| ID | Section/line | What is wrong | Why a reviewer rejects on it | Evidence (CSV path or reference) | Exact replacement text or analysis to run | Priority | Fixable now? | **Status (2026-09-14)** |
|---|---|---|---|---|---|---|---|---|
| C1 | §II Related Work, sentence ending "...routine laboratory predictors [?], [6]–[8]." | Broken citation marker `[?]` — a `\cite{}` key failed to resolve. | Visible compilation defect in the camera-ready PDF; signals the submission was not proofread. | Reference [9] (Kalka et al., "FibroPredict") is never cited anywhere in the body text. | Diagnosed live in Overleaf: root cause was a duplicate `\bibitem{fibropredict2025}` shadowing the real, pre-existing `\bibitem{kalka2025fibropredict}` and shifting every subsequent reference number by one. | Critical | Yes | **Root-caused and fixed** (duplicate `\bibitem` removed, `\cite{}` key corrected to `kalka2025fibropredict`); user confirmed the elastography citation — collaterally shifted by the same bug — now compiles to `[12]–[14]` as expected. |
| C2 | §II Related Work, "...straight to elastography [?], [13], [14]." | Broken citation marker `[?]`, later found to be a numbering-shift artifact of C1's duplicate-bibitem bug, not an independent error. | Same as C1. | Reference [12] (Shaheen et al.). | No separate fix needed once C1's duplicate was removed — confirmed by user (`[12]–[14]`). | Critical | Yes | **Resolved** (collateral fix from C1). |
| C3 | §II Related Work, "...an established concern [?], [3], [15]." | Broken citation marker `[?]`. | Same as C1. | Reference [16] (Barocas, Hardt, Narayanan). Actual `\cite{}` key found to be `barocas2019fairness` against a real `\bibitem{barocas2023fairness}` — a year typo, not a missing entry. | Change `\cite{...,barocas2019fairness}` to `\cite{...,barocas2023fairness}`. | Critical | Yes | **Fix given to user**; not yet confirmed compiled (last reported result was C1/C2's `[12]–[14]`, no confirmation message received yet for this one). |
| C4 | Abstract, "...normal-weight participants over-cover (94.8–97.2%)" | 94.8–97.2% is the Normal ∪ Overweight range; Normal alone is 95.4–97.0%. | `results/uncertainty/subgroup_coverage.csv`. | "while normal- and overweight-BMI participants over-cover (94.8–97.2%)" | High | Yes | **Fix given to user** (exact find/replace text); not confirmed applied. |
| C5 | §IV.E vs §V, "(∆ < 2 pp)" vs "(∆ ≤ 0.6 pp)" | Same claim, two numeric bounds. | `phase4_corrected_conformal_comparison.csv`, max delta 0.60 pp. | Replace "< 2 pp" with "≤ 0.6 pp" in §IV.E. | High | Yes | **Fix given to user**; not confirmed applied. |
| C6 | Conclusion "three" vs Abstract "two" independently constructed cohorts | Disagreement within the same document. | §III.E, §III.D, §IV.F name exactly two. | Change Conclusion's "three" to "two". | High | Yes | **Fix given to user**; not confirmed applied. |
| C7 | §IV.E, "FDR-significant 5/5 → 0/4" | Denominator changes from 5 to 4 unlabelled. | `MANUSCRIPT_DRAFT.md` mitigation table row. | "FDR-significant in 4/4 of the reweighting-compatible models at baseline → 0/4 after reweighting (MLP excluded)". | Medium | Yes | **Fix given to user** (folded into the Cut List's D1 replacement text, §D below); not confirmed applied. |
| C8 | §IV.A, "4–5×" MLP intercept ratio | True range 4.52×–5.19×. | `test_set_calibration_final.csv`. | Replace "4–5×" with "4.5–5.2×". | Medium | Yes | **Fix given to user**; not confirmed applied. |
| C9 | Abstract/§IV.B "0.19–0.33" vs §IV.E "0.18–0.25" | Two matched-stiffness ranges, unlabelled splits/model-sets. | `fix2_bmi_shortcut_check.csv` vs `mechanism_comparison.csv`. | Label both at first use with split/model-set. | Medium | Yes | **Fix given to user**; not confirmed applied. |
| C10 | §IV.F, "BMI and age... first and second in every model" | Overstated; age is 3rd in the MLP. | `interpretability_permutation_importance.csv`. | "...age ranked second in four of five models (third in the MLP, where AST ranked second)." | High | Yes | **Fix given to user**; not confirmed applied. |
| C11 | Whole paper — no external clinical baseline | FIB-4/NFS cited as BMI-dependent but never computed on this cohort. | Confirmed absent by search; New Analysis Queue E1/E2 below. | Run E1 (FIB-4 full audit) + E2 (matched-stiffness). | Critical | Needed new analysis | **DONE.** Full E1+E2 (+calibration, added after a follow-up gap check) executed and reproducibility-verified bit-for-bit. Scripts: `src/cb_01_compute_fib4.py`–`cb_06_calibration.py`. Results: `results/clinical_baselines/`. Report: `documentation/clinical_baselines/FIB4_BASELINE_REPORT.md`. **Headline finding: FIB-4's BMI-sensitivity and matched-stiffness results run in the *opposite* direction from all five ML models** (FIB-4 under-detects Obese; ML models over-detect Obese), while conformal-coverage direction matches across both. Manuscript insertion text (new Methods §F, Results §G, one Discussion sentence, one Limitations clause) drafted and handed to user; **not yet applied to `research_doc (4).pdf`**. |
| C12 | Table III / Abstract, disparities reported to 0.01 pp | CI width ~44 pp on N=22 positives; false precision. | `fairness_inference.csv` — independently re-verified (logistic CI [25.68, 69.50] pp). | Round to nearest whole pp + CI/N per cell. | Medium | Yes | **Fix specified**, not yet applied. |
| C13 | Limitations — no NHANES complex-survey-design disclosure | Unweighted analysis never stated; design variables present but unused. | `WTMECPRP`, `SDMVPSU`, `SDMVSTRA` confirmed present, non-missing, N=7,153, 24 strata all ≥2 PSUs. | Add disclosure sentence; optionally run E3 (survey-weighted check). | Medium | Sentence: yes; full check: needed new analysis | **DONE (full E3, exceeding the minimum sentence).** `src/svy_01_prevalence.py`, `svy_02_bmi_sensitivity.py`. Results: `results/sensitivity/survey_weighted/`. Report: `documentation/sensitivity/SURVEY_WEIGHTED_REPORT.md`. **Findings: weighted prevalence 8.30% (95% CI 7.00–9.81%) vs. unweighted 9.31%; BMI-sensitivity disparity direction holds under weighting but attenuates ~35–65% in magnitude, and weighted per-domain CIs overlap (no formal CI was computed on the difference itself — stated limitation).** Manuscript insertion (Limitations sentence, minimum-disclosure version recommended given page budget) drafted; **not yet applied**. |
| C14 | Declarations, code URL has a space (`Liver Fib`) vs. actual remote (`Liver_Fib`) | Link 404s as printed. | `git remote -v`. | Replace with correct underscore URL. | Medium | Yes | **Not yet addressed this session.** |
| C15 | Structural — §IV.D/E and Table V dilute the headline claim | Space allocation doesn't signal which finding is primary. | Line-count breakdown. | Execute Cut List D1/D2/D4; add one Discussion sentence distinguishing this paper's pre-correction dissociation from [27]/[29]'s post-correction trade-offs. | Critical | Yes | **Cut-list replacement text drafted for D1–D4 (see §D)**, given to user; not confirmed applied. The Discussion sentence distinguishing from [27]/[29] is still open (not drafted). |
| C16 | Declarations, author list/contributions (P.M., B.T., N.S.) | Repo git history shows a single committer; no amendment names the other three authors. | `git log` (single committer, unchanged as of 2026-09-14); `TARGET_VENUE_DECISION.md` recommends "Independent Researcher" framing. | Not verifiable from repository contents — author(s) must resolve directly. | Critical | No — needs author confirmation | **Still open.** Discussed explicitly with the user; flagged as their decision, not something repo evidence can settle either way. |

---

## D. CUT LIST

| Cut | What / where | Column-inches recovered (est.) | Justification against the one claim (Section A) | **Status** |
|---|---|---|---|---|
| D1 | §IV.E Mitigation: compress the four non-reweighting interventions into 2–3 sentences, keep training-time reweighting at full detail. | ≈45–55 lines | These four are supporting evidence that "nothing fixes it," not evidence for the dissociation claim itself. | **Replacement text drafted and given to user** (also folds in C7's fix); not confirmed applied. |
| D2 | §IV.F Robustness: replace per-cohort AUROC/coverage figures with one summary sentence. | ≈12–15 lines | Supports "delta survives," not the claim itself. | **Replacement text drafted and given to user**; not confirmed applied. |
| D3 | §V.A Limitations: collapse the twelve-item enumeration into 3 grouped sentences. | ≈8 lines | Defensive completeness, not the claim. | **Replacement text drafted and given to user**; not confirmed applied. |
| D4 | §IV.D Mechanism: cut the restricted-cubic-spline detail to two sentences. | ≈10 lines | Secondary diagnostic. | **Replacement text drafted and given to user**; not confirmed applied. |

**Total recovered: ≈75–90 extracted-text lines (roughly 11–13% of the paper's body length)** —
originally sized to fit E1/E2 alone. **Now needs to absorb both the FIB-4 addition (C11) and
the survey-weighted disclosure (C13) in the same budget** — see §G below for the current
compressed insertion text sized against this constraint.

---

## E. NEW ANALYSIS QUEUE

| Order | Analysis | Claim it defends | Artifact | Feasibility note | **Status** |
|---|---|---|---|---|---|
| E1 | Compute FIB-4 on the identical frozen cohort/split; run through discrimination, calibration, BMI/age-subgroup-sensitivity, and split-conformal pipelines. | Criterion #5 (credible external baseline). | `results/clinical_baselines/` | All four inputs already in the frozen parquet. | **DONE** — see C11 status above. |
| E2 | Matched-stiffness regression using FIB-4. | Same as E1. | Extends E1's artifact. | Zero incremental data cost. | **DONE** — see C11 status above. |
| E3 | Survey-weighted sensitivity check (Taylor linearization, `WTMECPRP`/`SDMVSTRA`/`SDMVPSU`). | Criterion #8 (pre-empted limitations). | `results/sensitivity/survey_weighted/` | Design variables present; required installing `samplics` (already declared in `requirements.txt` since 2026-08-28, not previously installed locally — installed this session). | **DONE** — see C13 status above. |
| E4 | NAFLD Fibrosis Score (NFS) on the same cohort. | Same as E1, second comparator. | Extends E1 if pursued. | **Still blocked as scoped** — NFS needs a glucose/diabetes field absent from `analysis_dataset_primary.parquet`; a genuine new-NHANES-source-file pull. | **Not attempted** (correctly out of scope per original plan). |

---

## F. BLOCKERS

- **F1.** Three unresolved `[?]` citation placeholders in §II Related Work (C1–C3). — **2 of 3 resolved and confirmed by user; 1 fix given, not yet confirmed.**
- **F2.** Author list and contribution statement cannot be verified against this repository (C16). — **Still open; requires the author(s), not further analysis.**
- **F3.** The submission is already at the venue's apparent 6-page limit with no slack, while Criteria #5 and #8 now require adding **two** new pieces of content (E1/E2 *and* E3), not one. — **Compounded since this plan was written.** Cut List (§D) drafted to compensate; combined insertion text for both C11 and C13 sized against it (see §G); actual page-count impact not yet verified because it depends on the compiled document's exact layout, which is not available on this machine.
- **F4.** The code-availability URL in Declarations does not resolve to the repository's actual remote (C14). — **Still open, not yet addressed.**

---

## G. Session status log (added 2026-09-14, this update)

**What changed since this plan was first written:**

1. **C1–C3 (citations):** root cause was not three independent bad references but one
   duplicate-`\bibitem` bug (C1) that shifted every subsequent reference number by one,
   collaterally breaking C2's citation too. Both confirmed fixed by the user via a recompiled
   `[12]–[14]` result. C3 (`barocas2019fairness` → `barocas2023fairness`, a year typo) has a
   given fix, not yet confirmed compiled.
2. **C4–C10, C12 (numeric/wording fixes):** all diagnosed with exact find/replace text handed
   to the user for direct application in Overleaf (no editable source for `research_doc (4).pdf`
   exists on this machine, so these cannot be applied programmatically). None confirmed applied
   yet.
3. **C11 (FIB-4 baseline) and C13 (survey-weighted check): both fully executed as new,
   reproducibility-verified analyses**, well beyond the original plan's minimum bar (a
   calibration step was added to C11 after a follow-up gap check against this very document's
   original E1 spec, which named calibration and had been skipped in the first pass). Both are
   currently **verification artifacts only** — nothing in `research_doc (4).pdf` reflects them
   yet. Manuscript insertion text for both (new Methods/Results subsections, Discussion
   sentences, Limitations clauses) has been drafted and given to the user, sized against the
   Cut List's freed space, but not yet applied.
4. **C15 (Cut List):** replacement text for D1–D4 drafted and given to the user; not confirmed
   applied. This is now the binding constraint (F3) for fitting C11+C13's insertions.
5. **C14, C16:** untouched this session — C14 (broken URL) is a trivial pending fix; C16
   (authorship) remains an author-only decision, restated but not resolved.
6. **This file itself** was found deleted from disk (never git-committed) partway through the
   session and has been reconstructed here from conversation record. Recommend committing it
   (and the other two similarly-untracked audit files, if still needed, also reconstructable
   from the same source) once the author reviews this update, so a repeat of this loss is not
   possible.

**Recommended next actions, in order:** (a) confirm C3's citation fix compiled; (b) apply the
Cut List (D1–D4) in Overleaf and confirm the resulting page count; (c) insert the C11/C13
manuscript text sized to whatever space that frees; (d) fix C14 (URL, trivial); (e) resolve
C16 (authorship) independently of any further analysis, since no repository evidence can settle
it either way.
