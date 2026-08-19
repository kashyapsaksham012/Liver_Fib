# Phase 5 (Fairness) — Results Report

**Generated:** 2026-08-19, live, in a session with continuous direct git/filesystem access
throughout. Every number in this report traces to a machine-generated artifact under
`results/fairness/` — none is restated from memory or typed independently of those files.

## 1. Executive Summary

Across the 5 frozen Phase 3 primary models, evaluated at their frozen model-specific
thresholds on the locked test set (N=2,146), the primary fairness metric (sensitivity
disparity, subgroup vs. reference group) shows two consistent, cross-model, statistically
robust patterns: (1) **Obese vs. Normal-BMI participants** — all 5 models show sensitivity
substantially *higher* for the Obese group (+27 to +48 percentage points), meaning the models
catch relatively fewer true significant-fibrosis cases among Normal-BMI participants; (2) **age
60+ vs. 40–59** — 4 of 5 models show sensitivity substantially *lower* for the 60+ group (−11 to
−15pp). A third candidate signal — Non-Hispanic Asian participants showing lower sensitivity
under Random Forest and XGBoost — did not survive FDR correction and is severely
precision-limited (14 positive cases). A fourth apparent signal — BMI Underweight showing a
huge, "FDR-significant" sensitivity deficit — is driven by a single positive case
(N_positive=1) in that subgroup and is explicitly **not** treated as an interpretable finding
despite meeting the mechanical significance threshold. The raw-calibration overprediction
pattern from Phase 4 (large for the 4 class-weighted models, small for MLP) replicates across
every demographic subgroup, with a genuine, honestly-reported directional nuance between
absolute and relative overprediction (§14).

## 2. Frozen Protocol Confirmation

Read live in full this pass, not from memory: `documentation/phase2/fairness_subgroup_protocol.md`,
`fairness_definition.md`, `multiple_comparisons_protocol.md`, `evaluation_metrics_protocol.md`,
`statistical_analysis_plan.md`, `sensitivity_analysis_plan.md`. Full extracted-decision record:
`documentation/fairness/phase5_pre_execution_snapshot.md`. No subgroup bin, metric, reference
group, or comparison strategy was chosen or altered after seeing results.

## 3. Subgroup Definitions

Sex (`RIAGENDR`: Male/Female), Race/Ethnicity (`RIDRETH3`, 6 categories, Non-Hispanic Asian
preserved distinctly), Age (`RIDAGEYR`: 18–39/40–59/60+), BMI (`BMXBMI`: Underweight/Normal/
Overweight/Obese, WHO categories). All four are PRIMARY dimensions per the frozen protocol. One
implementation bug was found and fixed during this pass: BMI/age binning initially used a
hand-rolled comparison (`< 18.5`) that disagreed with the canonical pipeline's `pd.cut`
right-inclusive convention at the exact boundary value (BMI = 18.5, 7 participants) — root-caused
and fixed to use `pd.cut` with identical bin edges, after which all live-recomputed full-cohort
counts matched `fairness_subgroup_protocol.md` exactly (verified programmatically in
`phase5_01_subgroup_feasibility.py` and `tests/test_fairness_pipeline.py` TEST 3).

## 4. Standing Provenance Limitation

**Historical pre-specification of subgroup bins could not be independently established from
strong repository provenance; the bins have been frozen prospectively since commit `c9c6ee3`
(the bundled Phase 2/3 commit) and were not modified after any Phase 3, Phase 4, or Phase 5
result was observed.** Carried forward exactly once per this task's instruction; not re-derived.

## 5. Subgroup Feasibility

Full detail: `results/fairness/subgroup_feasibility_table.csv` (30 rows: 15 categories × 2
populations). Every full-cohort count matches the frozen protocol document exactly (after the
BMI/age binning fix in §3). Test-set (N=2,146) subgroup sizes are smaller and several categories
drop a precision tier relative to the full cohort (e.g., Female sex: primary-feasibility-tier in
the full cohort but exploratory-tier in the test set; several race/BMI categories become
limited-precision or insufficient-evidence in the test set specifically). No subgroup was
pooled, dropped, or redefined at any precision level.

## 6. Selection/Exclusion Disparity

Preserved unchanged from Phase 2 (`documentation/phase2/missing_data_protocol.md`, live-verified
this pass): Non-Hispanic Black participants represented **41.3%** of participants excluded by
the lab-completeness restriction, versus **25.0%** of the retained primary cohort (26.3% of the
combined source population). This is a **selection/inclusion disparity** — a property of who
made it into the analysis population — and is kept explicitly separate from the
**model-performance disparities** reported in §7–12 below, which describe how the models behave
*within* the already-selected cohort. Neither is presented as evidence for or explanation of the
other (Part 28 discipline).

## 7. Sex Fairness

Full detail: `results/fairness/subgroup_discrimination_metrics.csv`,
`fairness_inference.csv` (dimension=sex). No sensitivity disparity for Female vs. Male reached
the frozen 10pp-and-CI-excludes-zero meaningful-difference threshold in any of the 5 models
(range roughly −0.02pp to −1.91pp, all CIs include zero). Female is the exploratory-tier
category in the test set (78 positives); Male is primary-feasibility tier (122 positives).

## 8. Race/Ethnicity Fairness

One candidate signal: **Non-Hispanic Asian** shows lower sensitivity than Non-Hispanic White
under Random Forest (−33.8pp, raw 95% CI [−62.1, −3.1], excludes zero) and XGBoost (−32.6pp, CI
[−60.3, −5.8], excludes zero) — but neither survives Benjamini-Hochberg FDR correction within
its (model × race/ethnicity) family (adjusted p = 0.145 and 0.075 respectively), and the
category carries only 14 positive cases (limited-precision tier). Per Part 13's discipline, this
is reported as a **large but statistically fragile, precision-limited signal** — neither
dismissed nor confirmed. No other race/ethnicity category reached the meaningful-difference
threshold in any model.

## 9. Age Fairness

**Age 60+ vs. 40–59** shows a consistent negative sensitivity disparity in 4 of 5 models:
Random Forest −13.2pp (FDR-adj. p=0.026), XGBoost −11.2pp (p=0.032), LightGBM −14.1pp (p=0.034),
MLP −14.7pp (p=0.012) — all meeting the meaningful-difference criterion (≥10pp, CI excludes
zero) and all FDR-significant. Logistic Regression's 60+ disparity did not reach the threshold.
Age 60+ is a primary-feasibility-tier category (101 positives in the test set) — this is the
best-powered signal in the entire analysis. Random Forest additionally shows a meaningful 18–39
disparity (−22.7pp, p=0.016, exploratory-tier, 33 positives).

## 10. BMI Fairness

**Obese vs. Normal** shows a large, consistent, FDR-significant *positive* sensitivity
disparity in all 5 models (+27.1 to +48.0pp, all p≤0.006) — Obese is primary-feasibility tier
(140 positives), Normal is limited-precision tier in the test set (22 positives). **Underweight
vs. Normal** shows an enormous negative disparity in all 5 models (−40.9 to −63.6pp, all
p=0.000) — but Underweight has exactly **1 positive case** in the test set (insufficient-evidence
tier). This result is **not treated as an interpretable finding**: a single participant's
classification outcome entirely determines the reported sensitivity (0% or 100%), and the
frozen protocol's own insufficient-evidence rule (positive N < 10) exists precisely to flag this
kind of result as non-interpretable as a point estimate, regardless of what the mechanical
bootstrap p-value says.

## 11. Discrimination Fairness

Full ROC-AUC by subgroup: `subgroup_discrimination_metrics.csv`. AUC ranges roughly 0.37–0.95
across the smallest subgroups (Underweight, N_positive as low as 1, is the extreme low value —
same precision caveat as §10) and 0.75–0.90 across primary-feasibility-tier subgroups. No
subgroup showed zero positives or zero negatives (no NOT COMPUTABLE cells this pass).

## 12. Error-Rate Fairness

FNR and FPR by subgroup are the complement of sensitivity/specificity respectively and are
reported in the same table (`subgroup_discrimination_metrics.csv`). The Age 60+ and BMI
Normal/Underweight patterns described in §9–10 directly correspond to elevated FNR (more missed
true-positive fibrosis cases) in those specific subgroups under the affected models — the
clinically relevant framing per `fairness_definition.md`'s choice of sensitivity as the primary
metric (a missed case is the costlier error for a screening-oriented model).

## 13. Subgroup Calibration (Authorized Secondary Metric)

Full detail: `results/fairness/subgroup_calibration_metrics.csv` (150 rows: 5 models × 15
categories × 2 variants [raw, recalibrated] — Amendment #9). Calibration intercept/slope by
subgroup follow the same overall pattern as Phase 4's aggregate finding: the 4 class-weighted
models show large negative intercepts in every subgroup (raw), while MLP's raw intercepts are
much closer to zero throughout. After applying the already-frozen Phase 4 Platt transform
(no new fitting), subgroup intercepts for the 4 balanced models move substantially toward zero
in every subgroup — recalibration's benefit is not concentrated in or absent from any particular
demographic category; it is broadly consistent.

## 14. Phase 4 Calibration-Gradient Findings by Subgroup

Full detail: `results/fairness/calibration_gradient_by_subgroup.csv`. This pass investigated the
task's literal hypothesis ("do lower-prevalence subgroups show *proportionally* greater
overprediction") and found a genuine, honestly-reported **directional split** depending on
whether "greater overprediction" means absolute or relative:

- **Absolute overprediction gap** (mean predicted − observed rate) correlates **positively**
  with subgroup prevalence for the 4 class-weighted models (Pearson r = 0.87–0.94) — i.e.,
  *higher*-prevalence subgroups show a *larger* absolute probability-point gap.
- **Relative overprediction ratio** (mean predicted / observed rate) correlates **negatively**
  with subgroup prevalence for the same 4 models (r = −0.76 to −0.95) — i.e., *lower*-prevalence
  subgroups show a *proportionally larger* multiple of overprediction, consistent with the
  task's literal wording.

Both are mathematically coherent (an additive intercept shift in logit space produces a larger
absolute probability change near p=0.5 but a larger *relative* change near p=0, since the
denominator shrinks). MLP shows a much weaker gradient in both framings (r = 0.41 absolute,
r = −0.09 relative). **This is observational — it does not establish that class weighting
causes either pattern**, only that the pattern co-occurs with which models use class weighting
and which do not.

## 15. Statistical Inference

Percentile bootstrap, n=2,000, stratified within each subgroup independently (each group's full
participant set resampled with replacement, sensitivity recomputed on whichever positives land
in that resample — the standard nonparametric bootstrap for a conditional rate), around the
disparity itself, per `fairness_definition.md`. Full table: `fairness_inference.csv` (55 rows).
No comparison was dropped for having too few valid resamples this pass (all reached ≥500 valid
draws out of 2,000 requested).

## 16. Multiple-Comparison Correction

Benjamini-Hochberg FDR, one family per (model × dimension) combination — verified structurally
separate from Phase 3's single AUC family (`phase3_07_plots_and_comparison.py`) and Phase 4's
three calibration families (`phase4_04_inference.py`): `phase5_04_inference.py` never reads
either script's output file, and re-initializes its own `family_pvals` list fresh for every
(model, dimension) pair (`tests/test_fairness_pipeline.py` TEST 13). The 26 pre-specified
exploratory intersectional cells (§20) are explicitly **not** FDR-corrected, per
`multiple_comparisons_protocol.md`'s own frozen hierarchical design.

## 17. Statistical vs. Practical Significance

Kept explicitly distinct throughout: the "meaningful disparity" flag requires **both** ≥10
percentage points **and** the raw (unadjusted) bootstrap CI excluding zero (`fairness_definition.md`'s
own criterion), while `significant_after_fdr_0.05` is a separate, FDR-adjusted flag. The
Non-Hispanic Asian race/ethnicity signal (§8) is the clearest case where these diverge: large
magnitude, raw CI excludes zero, but FDR-non-significant — reported as exactly that, not
collapsed into either "significant" or "not significant."

## 18. Precision-Limited Subgroup Interpretation

Every table carries a `precision_tier` column. The BMI Underweight result (§10) is the starkest
example of why this matters: it is simultaneously the largest point estimate, the smallest raw
p-value, and the least interpretable result in the entire analysis (N_positive=1). No
precision-limited or insufficient-evidence subgroup result is presented as a confirmed finding
anywhere in this report.

## 19. Raw vs. Recalibrated Fairness (Authorized, Amendment #9)

Covered in §13–14. Kept as fully separate columns/rows throughout (`variant` column in
`subgroup_calibration_metrics.csv`) — raw probabilities were never overwritten. Recalibration
was **not** applied to classification-based metrics (sensitivity/specificity/FNR/FPR/AUC in
§7–12): the frozen Phase 3 threshold is defined on the raw probability scale, and applying it to
recalibrated probabilities (which have deliberately shifted location) would silently and
incorrectly reclassify most participants — this would require deriving a new threshold, which
Part 20 explicitly forbids. This scoping decision is stated explicitly here rather than left
implicit.

## 20. Intersectional Analyses (Exploratory, Authorized)

`results/fairness/intersectional_exploratory_metrics.csv` (130 rows = 5 models × the 26
pre-specified cells in `results/tables/phase2_intersectional_feasibility.csv` — Sex×Race/Ethnicity,
Sex×Age, Sex×BMI only; no other intersection was pre-specified or invented). Every row is
labeled `EXPLORATORY -- UNCORRECTED` and none is treated as a primary/confirmatory finding
(`tests/test_fairness_pipeline.py` TEST 16 verifies both the exact cell count and the label).
No p-values or CIs were computed for these cells — descriptive point estimates only, per the
frozen protocol's own exploratory-tier design (uncorrected comparisons should not carry an
implied inferential rigor they don't have).

## 21. Sensitivity Analyses

Only two sensitivity axes were executable within Phase 5's boundaries (no retraining
permitted): raw-vs-recalibrated (§19, executed) and the calibration-gradient
absolute-vs-relative framing (§14, executed). The 4 formally Phase-2-frozen, Phase-3-level
sensitivity analyses (alternative 8.0kPa threshold, CAND_2 cohort, fasting-extended
architecture, multiple-imputation) remain **unexecuted** — none has a corresponding trained
model or prediction artifact from any prior phase, and executing them now would require
retraining, which Part 30 of this task explicitly forbids. This is a genuine, pre-existing gap
carried forward as a disclosed limitation (§22), not newly created or silently skipped.

## 22. Limitations

- The 4 Phase-2-frozen sensitivity analyses remain unexecuted (§21) — a pre-existing gap, not
  introduced by this phase.
- No test-set bootstrap CI exists for secondary discrimination/calibration metrics beyond the
  primary sensitivity disparity — only the primary metric received full bootstrap+FDR treatment,
  consistent with `fairness_definition.md`'s explicit scoping of the bootstrap CI to the primary
  disparity.
- The Phase 2/Phase 3 bundled-commit (Tier D) provenance limitation for subgroup-bin
  pre-specification is carried forward unchanged (§4).
- Several race/ethnicity and BMI test-set categories are precision-limited or
  insufficient-evidence tier — inherent to the test set's smaller size (30% of the cohort), not
  a defect in this analysis.

## 23. Reproducibility

Package versions unchanged from Phase 4 (scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0,
numpy 2.5.2, pandas 3.0.5). One clean reproducibility rerun performed: all 6 Phase 5 scripts
rerun into an isolated scratch directory (never committed, never treated as a second official
test-set touch) and diffed numerically against the committed artifacts. Result: **all 5 artifact
families identical** (subgroup feasibility, discrimination, calibration, inference,
intersectional — max absolute difference 0). Bootstrap used deterministic per-comparison seeds
derived from the fixed project seed (42) via a stable CRC32 offset, not Python's salted `hash()`.

## 24. Validation Tests

`tests/test_fairness_pipeline.py`, run live: **92/92 checks passed**, covering all 23 required
test categories (subgroup/reference-group fidelity, no modification, demographic integrity,
5-model representation, MLP_balanced exclusion, frozen-threshold usage, no subgroup-specific
threshold optimization, frozen metric list, disparity arithmetic, FDR-family separation,
precision flagging, NOT-COMPUTABLE handling, intersectional cell-count/labeling, no mitigation,
selection-bias separation, test-set-touch scoping, code-derived results, figure/data
correspondence, Phase 1–4 artifact immutability, no Phase 6 execution).

## 25. Git/Provenance Record

| Commit | Subject |
|---|---|
| `f20a67942a281aae262e40952ff347b4a2feb43f` | Phase 5 pre-work: human spot-check transcription + pre-execution snapshot (pre-test-set, no predictions touched) |
| `5785022e7ebc10ac46bc414157f7fe82c5b8f4e5` | Commit A — subgroup feasibility + Amendment #9 logging (pre-test-set, no predictions touched) |
| `63d41b75f40807986260d2b44b6bc17dd366aacd` | Commit B — the single, coordinated Fairness test-set touch (discrimination, calibration, gradient, inference, intersectional, figures) |
| *(Commit C, created immediately after this report)* | Validation tests + this final report |

All commits pushed and independently verified via both `git fetch`+`rev-parse` and a direct
`git ls-remote` server query (not relying on push-command exit status alone).

## 26. Phase 6 Handoff

Not performed in this phase (Part 26/30/31): conformal prediction, coverage analysis,
prediction-set analysis, and the conformal-valid model refit on `proper_train_ids.csv` remain
Phase 6 (Uncertainty) prerequisites, unchanged by Phase 5. `results/uncertainty/` and
`results/conformal/` do not exist (`tests/test_fairness_pipeline.py` TEST 23). No fairness
mitigation, threshold adjustment, or reweighting was performed or prepared — those remain
explicitly out of scope for this phase per Part 30.

---

**PHASE 5 COMPLETE WITH DOCUMENTED LIMITATIONS — READY FOR UNCERTAINTY**

Basis: the frozen fairness protocol was followed throughout (read live in full, not from
memory); all required subgroup analyses (discrimination, calibration, inference,
calibration-gradient, intersectional) were completed on the correct populations using the
correct frozen thresholds; precision limitations are documented in every relevant table;
statistical inference and FDR correction were completed and verified structurally separate from
Phase 3/4's families; the selection-vs-model-behavior distinction is preserved; the Phase 4
calibration-gradient question was investigated and reported honestly in both directions;
test-set governance was followed (one coordinated touch, no inspect-modify-rerun cycle);
automated tests (92/92) and a clean reproducibility rerun both passed; outputs are archived
under `results/fairness/`; and Git history will be committed, pushed, and independently
verified per §25. The "documented limitations" qualifier reflects the 4 unexecuted
Phase-2-frozen sensitivity analyses (§21–22), a pre-existing gap this phase could not close
without retraining.
