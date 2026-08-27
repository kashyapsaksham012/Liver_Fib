# Discrimination and aggregate calibration are insufficient evidence of subgroup-safe reliability: a calibration–fairness–uncertainty audit of routine-data models for significant liver fibrosis

**Draft v1 — 2026-08-27.** Grounded strictly in
`documentation/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv`,
`AUTHORITATIVE_RESULTS.md`, `MANUSCRIPT_FRAMING_GUIDANCE.md`, `FINAL_LIMITATIONS_REGISTER.md`,
`DO_NOT_CLAIM.md`, and `CONFLICT_ADJUDICATIONS.md`. Every numeric claim traces to a frozen result
artifact (see Appendix A). This is a working draft for the authors, not a submission.

---

## Structured abstract

**Background.** Machine-learning models built from routine primary-care data are widely proposed
for non-invasive liver-fibrosis triage. Such models are typically evaluated on discrimination and,
increasingly, on aggregate calibration. We asked whether a model that looks acceptable on those
axes can still fail reliability guarantees for identifiable demographic subgroups, and whether
group-wise methods can repair it.

**Methods.** Using NHANES 2017–March 2020, we defined a primary cohort of 7,153 adults with a
quality-valid vibration-controlled transient elastography (VCTE) examination (significant fibrosis
= `LUXSMED ≥ 8.2 kPa`; 9.31% prevalence), with the outcome threshold and ten routine
demographic/laboratory predictors frozen before any model was trained. We trained five model
families (logistic regression, random forest, XGBoost, LightGBM, multilayer perceptron) with a
single locked 70/30 split, evaluated discrimination with Benjamini–Hochberg (BH) false-discovery
control, corrected probability calibration with out-of-fold Platt scaling, conducted a
pre-specified subgroup fairness audit (sex, race/ethnicity, age band, body-mass-index [BMI] band),
and quantified predictive uncertainty with split-conformal prediction (marginal target 90%). We
then tested group-wise (Mondrian) conformal recalibration and a structured set of threshold-,
calibration-, and conformal-based mitigation strategies against a pre-specified multi-metric gate.
Robustness was assessed across an alternative 8.0-kPa threshold and two independently constructed
cohorts, a within-NHANES demographic holdout, and a later NHANES cycle (2021–2023).

**Results.** The five families reached statistically indistinguishable discrimination (test AUROC
0.823–0.843; 0/10 pairwise comparisons significant after BH correction). Four of five models
over-predicted risk severely in raw output (out-of-fold calibration intercepts −2.24 to −1.86); a
single out-of-fold Platt step restored aggregate calibration (test expected calibration error
0.25–0.30 → 0.01–0.03) without changing discrimination. Beneath this aggregate adequacy,
sensitivity for significant fibrosis was 27–48 percentage points lower in normal-weight than in
obese participants in all five models (all q ≤ 0.006), a finding we independently reproduced and
that widened to 63–72 points in the 2021–2023 cycle. Split-conformal prediction met its 90%
marginal coverage target overall (88–91%) but under-covered obese (77–82%) and, less robustly,
older (81–86%) participants — and their intersection (65–75%) — in every model, while
normal-weight and younger participants over-covered. This coverage failure replicated on both
sensitivity cohorts and the alternative threshold. No mitigation strategy tested — group-wise
conformal recalibration, subgroup-specific thresholds, subgroup calibration, equalized-odds
post-processing, model retuning, or joint intersectional calibration — produced an acceptable
multi-metric fix; group-wise conformal recalibration was a partial repair (5/9 targeted
combinations) that breached the marginal-coverage tolerance for one model. Withholding an entire
demographic subgroup from training degraded discrimination and calibration on that subgroup, and
the 2021–2023 cycle only partially replicated the findings.

**Conclusions.** In a large US survey population, routine-data models for significant liver
fibrosis reach a comparable, modest-to-strong discrimination ceiling and can be made
aggregate-calibrated, yet still under-detect normal-weight patients and provide systematically
over-confident prediction sets for obese and older patients — failures that standard evaluation
conceals and that we could not repair within the study's scope. Discrimination plus aggregate
calibration are insufficient evidence of subgroup-safe reliability. External validation has not
been performed and is the foremost outstanding requirement.

---

## 1. Introduction

Liver fibrosis is common and under-diagnosed, and non-invasive triage tools that use only routine
primary-care variables are attractive for population screening. A large literature reports
machine-learning models for this task, almost always benchmarked on the area under the receiver
operating characteristic curve (AUROC) and, in better studies, on calibration curves or the Brier
score.

Two problems with this evaluation paradigm motivate the present work. First, aggregate metrics
average over the population and can hide subgroup-specific failure — a model can discriminate and
calibrate well overall while systematically missing cases in a demographic subgroup. Second,
point predictions (or even calibrated probabilities) do not convey case-level uncertainty;
conformal prediction supplies prediction *sets* with a finite-sample coverage guarantee, but that
guarantee is *marginal* — it holds on average over the population, not conditionally within
subgroups.

We conducted a pre-registered audit that holds discrimination, calibration, subgroup fairness,
and conformal reliability to the same standard, on one frozen cohort and outcome definition, with
multiplicity control throughout. Our aim was not to produce a deployable model — we show the
discrimination ceiling for this data type is modest — but to characterise, with a disciplined
protocol, whether and how routine-data fibrosis models fail for identifiable subgroups, and
whether that failure is fixable.

## 2. Methods

### 2.1 Data source and cohort

We used the National Health and Nutrition Examination Survey (NHANES) 2017–March 2020
pre-pandemic combined release (public-use files `P_DEMO`, `P_BMX`, `P_BIOPRO`, `P_CBC`, `P_GLU`,
`P_TRIGLY`, `P_HDL`, `P_LUX`). The anchor population was 10,409 participants with elastography
attempted and a non-missing stiffness measurement. Applying, in order, valid-examination,
adult-age, and complete-predictor criteria yielded the primary analytic cohort
(`CAND_1_QUALITYVALID_ADULT_BROAD`): **N = 7,153** adults (cohort flow 10,409 → 9,700 → 9,023 →
7,768 → 7,153). Complete-case filtering excluded 615 quality-valid adults; Non-Hispanic Black
participants were 41.3% of those exclusions versus 25.0% of the retained cohort, a differential
we address by targeted imputation (§2.9) and disclose as a limitation.

### 2.2 Outcome

The primary outcome was significant fibrosis, defined as `LUXSMED ≥ 8.2 kPa` on a quality-valid
VCTE examination (`LUAXSTAT == 1`). The 8.2-kPa cut-point is the Youden-optimal value from a 2024
systematic review/meta-analysis of VCTE against magnetic-resonance elastography. **The threshold
and its rationale were fixed before any model was trained.** Two severity-graded outcomes
(advanced fibrosis `≥ 9.7 kPa`; cirrhosis `≥ 13.6 kPa`) were pre-registered as secondary and are
reported descriptively (§2.9, §3.11).

### 2.3 Predictors

Ten routine variables, frozen before training: age, sex, BMI, alanine aminotransferase (ALT),
aspartate aminotransferase (AST), albumin, alkaline phosphatase, total bilirubin, platelet count,
and HDL cholesterol. **Race/ethnicity was excluded from the model input by design** and retained
only for post-hoc fairness stratification — an explicit, documented decision, not an omission.
Direct elastography-derived quantities were forbidden as predictors.

### 2.4 Model development

A single stratified 70/30 split (seed 42) produced a training partition (N = 5,007; 466 positive)
and a **locked test set (N = 2,146; 200 positive)** that was evaluated once per analysis phase.
Hyperparameters were tuned by 5-fold stratified cross-validation within the training partition
only. Five families were fitted: logistic regression and multilayer perceptron (with feature
scaling), random forest, XGBoost, and LightGBM. Class imbalance was handled with class weights
(logistic, random forest) or `scale_pos_weight` (XGBoost, LightGBM); the perceptron used no
weighting (a scikit-learn API constraint, examined in a training-fold-only oversampling
sensitivity analysis). Operating thresholds were the Youden-optimal points on out-of-fold
predictions; adoption of this rule is recorded as a protocol amendment.

### 2.5 Calibration

Probability calibration was assessed by calibration-in-the-large (intercept and slope of a
logistic recalibration fit), expected calibration error (ECE, decile bins), and the Brier score.
Recalibration used Platt scaling with parameters fitted **on out-of-fold predictions only**,
frozen, then applied once to the locked test set. Isotonic regression was considered and rejected
given only 466 out-of-fold positive cases (Amendment #8).

### 2.6 Fairness analysis

The fairness dimensions (sex; race/ethnicity by NHANES `RIDRETH3`; age band 18–39/40–59/60+; BMI
band underweight/normal/overweight/obese), the disparity metric (subgroup sensitivity difference
from a reference group), bootstrap confidence intervals (2,000 resamples), and within-family BH
correction were all pre-specified. Analyses used the Platt-recalibrated test predictions. The
underweight band (one test positive) is statistically flagged but excluded from interpretation by
protocol.

### 2.7 Conformal prediction

Split-conformal prediction (nominal coverage 90%, α = 0.10) used a further 80/20 stratified split
of the training partition into a proper-training set (N = 4,005) and a conformal-calibration set
(N = 1,002); models were refit on the proper-training set only. The nonconformity score was
`1 − P(true class | x)`; the threshold was the k-th smallest calibration score with
`k = ⌈(n_cal + 1)(1 − α)⌉` (k = 903). Prediction sets contained each class whose nonconformity
score fell at or below the threshold. Coverage was assessed marginally and within every fairness
subgroup, with Wilson 95% intervals and a one-sample binomial test against 0.90, BH-corrected
within each model × dimension family.

### 2.8 Mitigation

We applied group-wise (Mondrian) conformal recalibration to the model × subgroup combinations
that were BH-significant in **both** the fairness and the conformal analysis (BMI-obese and
age-60+). Separately, we evaluated a structured set of interventions against a pre-specified
multi-metric acceptance gate: BMI-specific decision thresholds, BMI-specific Platt scaling,
joint BMI × age thresholds, subgroup-specific calibration, equalized-odds (equal-opportunity)
post-processing, model retuning within the frozen hyperparameter family, and joint
(intersectional) conformal calibration. Mitigation candidates were compared descriptively against
the gate; no candidate-vs-candidate significance test was performed.

### 2.9 Sensitivity analyses

Three independently derived variants were executed: (i) an 8.0-kPa outcome relabel of the primary
cohort (frozen predictions re-scored; no retraining); (ii) `CAND_2`, a relaxed
elastography-eligibility cohort (N = 7,639), independently re-split and refit with the frozen
hyperparameters; (iii) `CAND_3`, a fasting-extended 12-predictor cohort (N = 3,582), likewise
refit. The pre-registered subgroup conformal-coverage replication for these variants was executed
(Amendment #16; §3.6). Complete-case analysis was the pre-registered primary missing-data
strategy; a targeted multiple-imputation analysis (fold-embedded `IterativeImputer`, m = 5)
addressed the differential Non-Hispanic Black exclusion specifically. The severity-graded
secondary outcomes were executed as a relabel-only descriptive pass (Amendment #15).

### 2.10 Demographic holdout and temporal evaluation

For a within-NHANES transportability probe, models were retrained with all Non-Hispanic Black
participants withheld (train N = 5,366) and evaluated on that withheld subgroup (N = 1,787). For
a temporal probe (reported as **separate work**), the frozen models, thresholds, and conformal
parameters were applied without any refitting to NHANES 2021–2023 (N = 4,910; 11.47% prevalence),
after an ALT assay bridge between cycles.

### 2.11 Statistical analysis and multiplicity

Confidence intervals used bootstrap resampling (discrimination, fairness disparities), Wilson
score intervals (coverage proportions), or Clopper–Pearson intervals (small intersectional
cells). Multiple testing was controlled with BH false-discovery control within pre-specified
families and, additionally, in a project-wide 182-test pooled correction. No exploratory finding
was promoted to a primary or secondary conclusion.

### 2.12 Reproducibility

A single fixed seed (42) governs the split, cross-validation folds, stochastic model components,
and bootstrap resampling. Split membership is stored by participant identifier; model and
result-to-script lineage, frozen file hashes, and a pinned environment are retained. An internal
validation suite (44/44 tests) and a test-set contamination audit (8/8 pathways) passed.

## 3. Results

### 3.1 Cohort

The primary cohort comprised 7,153 adults (666 with significant fibrosis; 9.31% prevalence).
Baseline characteristics by fibrosis status and by BMI band are in **Table 1**.

### 3.2 Discrimination

All five model families achieved statistically indistinguishable discrimination on the locked
test set: AUROC 0.8334 (logistic), 0.8343 (random forest), 0.8429 (XGBoost), 0.8394 (LightGBM),
0.8229 (perceptron) — range **0.823–0.843**. **None of the 10 pairwise comparisons was
significant after BH correction.** Precision-recall AUC was 0.35–0.37 at 9.31% prevalence
(**Table 2**; **Figure 1**, ROC and PR curves). XGBoost had the highest point estimate but no
significant superiority.

### 3.3 Calibration

The four class-balanced models over-predicted risk severely in raw output (out-of-fold
calibration intercepts −2.24, −1.86, −2.05, −2.05; the unweighted perceptron, −0.28). The shift
matches the Bayesian prior-mismatch correction for training against an implicit 50:50 prior on a
9.31%-prevalence outcome (log(0.0931/0.9069) ≈ −2.27). A single out-of-fold Platt step, applied
once to the locked test, restored aggregate calibration (test ECE 0.25–0.30 → **0.011–0.026**;
Brier 0.146–0.176 → 0.069–0.072; intercepts → −0.15 to +0.14) with **AUROC unchanged by
construction** (**Table 2**; **Figure 2**). Without this step the raw probabilities would
over-refer a large fraction of the population; recalibration is mandatory, not cosmetic.

### 3.4 Body-mass fairness (primary finding)

After recalibration, **sensitivity for significant fibrosis was 27–48 percentage points lower in
normal-weight than in obese participants in all five models** (logistic −47.7, random forest
−31.6, XGBoost −31.4, LightGBM −27.1, perceptron −39.0 pp; all BH q ≤ 0.006; **Figure 3**). We
reproduced this independently before any diagnostic step (counts exact; inference within
rounding). A mechanistic analysis attributed it to a score-distribution difference — fibrosis-
positive normal-weight cases receive systematically lower model scores (Mann–Whitney significant
among both positive and negative cases) — compounded by operating-threshold placement; the
mechanism is empirical, not causal. Sex and race/ethnicity showed no BH-significant sensitivity
or AUROC disparity in the primary complete-case test set (in-distribution only).

### 3.5 Marginal versus subgroup conformal coverage (primary finding)

Split-conformal prediction met its target overall: marginal coverage **88.1–90.8%** across the
five models. Within subgroups, coverage **failed** for the same populations flagged by the
fairness audit: **BMI-obese 76.8–82.3%** and **age-60+ 81.1–85.6%**, with Wilson intervals
excluding 90% and BH-significant for every model; the **obese-and-60+ intersection (N = 294)
fell to 65–75%**. Normal-weight, overweight, and 18–39-year-old participants **over-covered**
(≈ 0.95–0.97) — the marginal guarantee is met by borrowing coverage from over-served subgroups
(**Figure 4**; **Table 3**). Better-calibrated probabilities (the perceptron) produced tighter
prediction sets (96.9% singletons vs. 23–43% ambiguous two-class sets for the class-weighted
models); coverage *validity* does not require calibration, but *efficiency* benefits from it.

### 3.6 Replication of the coverage failure across cohorts (Amendment #16)

The subgroup coverage analysis was repeated on the 8.0-kPa relabel and, using the frozen
conformal framework and hyperparameters, on `CAND_2` and `CAND_3`. **The pattern replicated on
all three constructions.** Marginal coverage remained on target (`CAND_2` 0.896–0.906; `CAND_3`
0.899–0.917). **BMI-obese under-coverage was robust**: 5/5 models on every construction, all
Wilson intervals excluding 90%, all BH-significant (`CAND_2` 0.790–0.841; `CAND_3` 0.799–0.838;
8.0 kPa 0.790–0.822). Age-60+ under-coverage held in direction on every construction but was
BH-significant in 5/5 models on `CAND_2` and only 2/5 on the smaller `CAND_3` (age-60+ cell ≈ 34
positives) — the same direction-robust, significance-fragile character as the age-60+ sensitivity
disparity. Normal-weight/overweight/younger over-coverage reproduced throughout (**Table 3**).

### 3.7 Mitigation attempts (all negative or partial)

**No intervention produced an acceptable multi-metric fix** (**Table 4**). Group-wise (Mondrian)
conformal recalibration restored nominal coverage in **5 of 9** targeted model–subgroup
combinations; it left four unresolved, **breached the marginal-coverage tolerance for XGBoost
(+5.3 pp)**, and in the overlap population applied single-attribute rules sequentially (age
overwriting BMI) rather than jointly. A dedicated re-analysis of four BMI-targeted mitigation
strategies on an independent split identified **none** meeting the pre-specified gate; only the
perceptron received a candidate (BMI-specific Platt: gap 39.0 → 34.5 pp, no formal inference).
Subgroup-specific calibration improved ECE for three models but left classification decisions and
sensitivity gaps unchanged. Subgroup-specific decision thresholds roughly halved the BMI gap but
**widened the age gap by 26–133%** and cost ~40 points of specificity — evidence of two distinct
mechanisms (a threshold-driven BMI gap, a non-threshold-driven age gap), not a fix.
Equal-opportunity post-processing achieved large target-group sensitivity gains at ~40 points of
specificity and roughly 400 excess false positives per 1,000 normal-weight participants screened
— clinically unacceptable. Model retuning within the frozen family removed no coverage breach
without an 11–22-point sensitivity cost. Joint intersectional conformal calibration restored the
overlap coverage on the primary cohort for most models but breached the marginal tolerance for
two and did not replicate on the later cycle.

### 3.8 Older-age findings (secondary observation)

The age-60+ **sensitivity** deficit was directionally consistent (negative in all five models,
−8.6 to −14.7 pp) but reached BH significance in **four of five** models (not logistic), was lost
under 9 of 12 alternative cohort/threshold specifications, **reversed direction** in the 2021–2023
cycle, and reflects a **non-monotonic** age effect (peak ≈ 65 y, no further decline at 70+). We
therefore report it as a hypothesis-generating observation rather than an established disparity.
The age-60+ **conformal under-coverage** (§3.5–3.6) is a separate, firmer result and is retained
at full strength.

### 3.9 Demographic holdout

Withholding all Non-Hispanic Black participants from training reduced discrimination on that
subgroup (AUROC 0.772–0.789, −0.05 to −0.06) and destabilised calibration (holdout intercepts
−0.58 to −2.17; slopes 0.64–0.97). This is a within-NHANES demographic holdout, **not external
validation**.

### 3.10 Temporal evaluation (separate work)

Applied without refitting to NHANES 2021–2023 (N = 4,910; 11.47% prevalence), the frozen models
showed **partial temporal replication**: AUROC declined to 0.777–0.782 (−0.04 to −0.06) while
precision-recall AUC rose; raw calibration remained poor (Brier worse); the **BMI-obese vs.
normal sensitivity disparity persisted and widened to 62.8–71.9 pp** (all BH-significant); the
age-60+ disparity shrank or reversed; marginal conformal coverage stayed near target (87.9–90.2%)
while subgroup and intersectional under-coverage persisted (obese 77.0–81.3%, 60+ 84.9–87.8%,
intersection 69.7–76.5%); and the frozen intersectional-mitigation configuration met its target
for only one of five models (vs. four originally). A drift-to-performance analysis supports
*association* only (increased prevalence, composition shift), not a single causal mechanism.

### 3.11 Sensitivity and secondary outcomes

Discrimination, the calibration correction, and the BMI-obese disparity reproduced across the
8.0-kPa threshold and both independently constructed cohorts (BMI-obese disparity stable in 15/15
tested instances); the age-60+ disparity's direction never reversed but its significance was lost
in 9/12 instances. The full-pipeline 8.0-kPa re-run's own verdict was that *some* findings
(age-60+ significance, some conformal detail) are threshold-sensitive; **8.2 kPa remains the
primary analysis**. For the severity-graded secondary outcomes, discrimination was comparable to
the primary outcome (AUROC 0.85–0.86 at ≥ 9.7 kPa; 0.84–0.86 at ≥ 13.6 kPa), but the frozen
8.2-kPa recalibration did not transport to the rarer outcomes (recalibrated intercepts −0.4 to
−0.8 and −1.2 to −1.9 respectively). The targeted multiple-imputation analysis did not materially
change discrimination or the Non-Hispanic Black sensitivity estimate (ΔAUROC < 0.007; subgroup
change ≤ ±4.2 pp; all intervals include zero).

### 3.12 Interpretability

ALT, AST, BMI, and age were the top four predictors across all five families (permutation
importance and standardised logistic coefficients) — established markers of hepatic injury and
metabolic risk. Decision-curve analysis showed net benefit over treat-all/treat-none strategies
across a plausible threshold range, including within the obese and 60+ subgroups (reported as an
exploratory clinical-utility extension, not a deployment endpoint).

## 4. Discussion

Five common model families, trained on ten routine variables, reach a comparable discrimination
ceiling for significant fibrosis (AUROC ≈ 0.82–0.84) and, after a mandatory recalibration step,
are well calibrated in aggregate. On the standard evaluation paradigm the study would end here,
with an unremarkable additional benchmark.

The substantive findings come from looking past aggregate metrics. The same models systematically
under-detect normal-weight patients — a 27–48-point sensitivity gap that we reproduced, that is
stable across three sensitivity constructions, and that *widened* in a later survey cycle. This is
the opposite of reassuring: normal-weight patients with fibrosis are exactly the group for whom a
routine-data screen might add the most value over a BMI-driven clinical prior, and they are the
group the models miss. In parallel, split-conformal prediction — whose marginal guarantee is
often presented as a subgroup-safety property — under-covers obese and older patients (and their
intersection) in every model, on every cohort construction we tried, while over-covering the
better-served subgroups. Marginal coverage is met by redistribution, not by uniform reliability.

Neither failure was repairable within our scope. Group-wise conformal recalibration is a genuine
but partial repair that trades a subgroup fix for a marginal-coverage breach; threshold tuning
helps one gap while worsening another because the two gaps have different mechanisms; and every
calibration-, post-processing-, or retuning-based approach we tested either failed the
pre-specified gate, failed to generalise across model families, or failed on the later cycle.
Reporting "we identified a problem we could not solve" is uncomfortable but is the accurate
result.

Two framing points follow. First, the body-mass finding, not the age finding, is the robust
subgroup result; the age-60+ *sensitivity* deficit is directionally suggestive but statistically
fragile and should be read as hypothesis-generating. Second, the contribution is methodological:
a model that passes discrimination and aggregate-calibration review is not thereby shown to be
subgroup-safe, and conformal prediction's marginal guarantee does not close that gap.

## 5. Limitations

The following limitations are material and must be read with the results (full register in
`FINAL_LIMITATIONS_REGISTER.md`):

- **No external validation.** The models have never been evaluated on an independent, non-NHANES
  population, and no compatible cohort was identified. This is the foremost limitation. The
  2021–2023 analysis is a *partial temporal replication*, not external validation; the
  Non-Hispanic Black holdout is internal to NHANES.
- **No acceptable mitigation** was found for the body-mass reliability–fairness failure.
- **Conformal** provides a marginal guarantee only; subgroup coverage was empirically deficient
  and is not a conditional-validity guarantee. Group-wise mitigation was partial (5/9), breached
  the XGBoost marginal tolerance (+5.3 pp), and handled the overlap sequentially, not jointly.
  The frozen intersectional configuration did not replicate temporally (1/5 models).
- **Age-60+ sensitivity** significance is specification-sensitive (4/5 primary; lost in 9/12
  sensitivity instances; reverses temporally).
- **Low prevalence** (9.31%; 666 positives) limits positive predictive value (~0.12–0.25 at a
  Youden operating point) and subgroup precision. Normal-weight sensitivity rests on 22 test
  positives; the underweight band (one positive) is uninterpretable and excluded.
- **Calibration**: class-balanced models are unusable without out-of-fold recalibration; aggregate
  recalibration did not extend to subgroups; temporal calibration remained poor and was not
  refit.
- **Missing data**: complete-case is primary; multiple imputation covered only the Non-Hispanic
  Black selection question, and its conformal extension lacks a fully reconstructable pipeline.
- **Design**: a single US survey program, a single pre-pandemic release for the primary analysis,
  a VCTE (not biopsy) reference standard, and a single 70/30 split without nested resampling.
  Adults only.

## 6. Conclusion

Routine-data machine-learning models for significant liver fibrosis reach a comparable,
modest-to-strong discrimination ceiling and can be made aggregate-calibrated, but still
under-detect normal-weight patients and under-cover obese and older patients with their
prediction sets — failures that discrimination and aggregate calibration conceal, that replicate
across cohorts and a later time period, and that we could not repair. Discrimination plus
aggregate calibration are insufficient evidence of subgroup-safe reliability. Independent external
validation is the necessary next step before any consideration of use.

---

## Tables

| # | Title | Source artifact(s) |
|---|---|---|
| **1** | Baseline characteristics of the primary cohort, overall and by fibrosis status and BMI band | `results/tables/phase1_table1.md`, `phase2_outcome_prevalence.csv` |
| **2** | Discrimination and calibration by model family (test set), raw and recalibrated | `results/tables/phase3_final_baseline_results.csv`, `results/calibration/test_set_calibration_final.csv`, `phase3_model_comparison_fdr.csv` |
| **3** | Conformal coverage — marginal and by subgroup — on CAND_1, and replication on 8.0 kPa / CAND_2 / CAND_3 | `results/uncertainty/{marginal_coverage_test_set,subgroup_coverage}.csv`, `results/sensitivity/conformal_replication_{marginal,subgroup}.csv`, `results/fairness_bmi_investigation/phase6_8kpa_robustness/phase6_8kpa_conformal_results.csv` |
| **4** | Mitigation strategies, objective, outcome vs the pre-specified gate, and disposition | `results/mitigation/*`, `results/fairness_bmi_investigation/phase3_corrected/*`, `phase4_corrected/*`, `phase7_mitigation_cleanup/*` |
| **5** | Sensitivity/robustness summary: primary vs 8.0 kPa / CAND_2 / CAND_3 / targeted MI | `results/sensitivity/primary_vs_sensitivity_comparison.csv`, `sensitivity_discrimination_calibration_results.csv`, `mi_black_subgroup_comparison.csv` |
| **6** | Temporal evaluation (NHANES 2021–2023): frozen-model performance vs the 2017–2020 locked test | `results/temporal_validation/PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.csv` |

## Figures

| # | Content | File(s) |
|---|---|---|
| **1** | ROC and precision-recall curves, five model families (test set) | `results/figures/phase3_roc_combined.png`, `results/figures/phase3_pr_combined.png` |
| **2** | Calibration curves, raw vs recalibrated, by model | `results/calibration/figures/calibration_curve_*.png` |
| **3** | Sensitivity by BMI band with disparity vs the normal-weight reference, by model | `results/fairness/figures/sensitivity_disparity_*.png` |
| **4** | Conformal coverage by subgroup with the 90% target line, by model (CAND_1) | `results/uncertainty/figures/subgroup_coverage_*.png` |
| **5** | Fairness–specificity trade-off (Pareto) for BMI and age interventions | `results/figures/figure1_bmi_fairness_vs_specificity_pareto.png`, `figure2_age_fairness_vs_specificity_pareto.png` |
| **6** | Temporal calibration curves (2021–2023), by model | `results/temporal_validation/figures/temporal_calibration_curve_*.png` |
| **S1** | Coverage vs prediction-set-size trade-off across conformal variants | `results/figures/figure3_coverage_vs_set_size_tradeoff.png` |
| **S2** | Liver stiffness distribution by BMI band, age, sex, race/ethnicity | `results/figures/liver_stiffness_by_*.png` |

## Appendix A — Claim traceability

Every numbered claim in the Results maps to a row of
`results/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv`:

| Manuscript section | Registry claim_id | Manuscript status |
|---|---|---|
| §3.2 discrimination | DISC-01, DISC-02 | MANUSCRIPT_READY |
| §3.3 calibration | CAL-01 | MANUSCRIPT_READY |
| §3.4 BMI fairness | FAIR-BMI-01, FAIR-BMI-02 | MANUSCRIPT_READY / _WITH_QUALIFICATION |
| §3.5 conformal (marginal + subgroup) | CONF-01, CONF-02, CONF-03 | MANUSCRIPT_READY / _WITH_QUALIFICATION |
| §3.6 conformal replication | CONF-02 (updated, Amendment #16) | MANUSCRIPT_READY_WITH_QUALIFICATION |
| §3.7 mitigation | MIT-01…MIT-05 | _WITH_QUALIFICATION / EXPLORATORY_ONLY |
| §3.8 age (secondary) | FAIR-AGE-01 | MANUSCRIPT_READY_WITH_QUALIFICATION (secondary observation) |
| §3.9 demographic holdout | GEN-01 | MANUSCRIPT_READY_WITH_QUALIFICATION |
| §3.10 temporal | TEMP-01 | SEPARATE_WORK |
| §3.11 sensitivity / secondary outcomes | SENS-01, SENS-02, SECOUT-01, MI-01 | _WITH_QUALIFICATION |
| §3.12 interpretability / DCA | INT-01, DCA-01 | MANUSCRIPT_READY / EXPLORATORY_ONLY |

**Claims explicitly not made** (per `DO_NOT_CLAIM.md`): no model is superior; no strong /
clinical-grade discrimination; no universal or subgroup calibration adequacy; no conditional /
subgroup / intersectional conformal validity; no successful mitigation; no external validation; no
full temporal replication; the NHB holdout and the 2021–2023 work are not external validation; no
deployment readiness; no causal mechanism; the age-60+ sensitivity disparity is not a co-headline
finding and not significant in 5/5 models; the obese-and-60+ overlap is 294 people (13.7% of the
test set), not 62%.

## Appendix B — Reporting-guideline mapping

Author to complete a TRIPOD+AI checklist. Key items are covered as follows: source of data and
eligibility (§2.1); outcome and predictors, blinded/frozen before modelling (§2.2–2.3); sample
size and missing-data handling (§2.1, §2.9); model development and internal validation
(§2.4–2.5); performance measures including calibration and fairness (§2.5–2.6, §3.2–3.4);
uncertainty quantification (§2.7, §3.5–3.6); model updating / transportability (§2.10, §3.9–3.10);
and limitations (§5).
