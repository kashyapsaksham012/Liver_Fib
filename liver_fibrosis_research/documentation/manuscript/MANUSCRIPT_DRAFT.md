# Discrimination and aggregate calibration are insufficient evidence of subgroup-safe reliability: a calibration–fairness–uncertainty audit of routine-data models for significant liver fibrosis

**Draft v4 — 2026-08-27.** Grounded strictly in
`documentation/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv`,
`AUTHORITATIVE_RESULTS.md`, `MANUSCRIPT_FRAMING_GUIDANCE.md`, `FINAL_LIMITATIONS_REGISTER.md`,
`DO_NOT_CLAIM.md`, and `CONFLICT_ADJUDICATIONS.md`; related-work positioning in
`documentation/manuscript/LITERATURE_REVIEW.md`. Every numeric claim traces to a frozen result
artifact (see Appendix A). This is a working draft for the authors, not a submission.

**v3 → v4 changes (Amendment #18):** new §2.7b (two model fits and their alignment); new §3.4b
(body-mass gap present in both fits — STRENGTHENING) and §3.4c (reference-standard measurement-bias
sensitivity — verdict V3, with a matched-stiffness BMI-shortcut finding); §3.4, §3.7, Table 4,
§4/§4.1, and §5 [J3, D1] updated to carry the Fix-1/Fix-2 results and the selective-deferral
(Amendment #17) outcome; abstract updated (matched-stiffness shortcut; deferral added to the
mitigation list; measurement-bias caveat).
**v2 → v3 changes:** literature-grounded Introduction with `[n]` markers; new §4.1 (relation to
prior work); 28-item reference list (verified — `REFERENCE_VERIFICATION.md`; +1 from a Track 2.3 search: ref 28); **Tables 1–5 rendered from the frozen artifacts** (Table 1
via `src/manuscript_01_table1.py`, a read-only descriptive script); TRIPOD+AI crosswalk
(Appendix B); every figure already exists as a committed PNG (§Figures); a full second-reader
number check (`documentation/manuscript/RESULTS_VERIFICATION.md` — one Table 3 value corrected).
**Still outstanding:** a formal PRISMA-style systematic search + DOI/PMID/author verification
(10/28 verified; `LITERATURE_REVIEW.md` §4); figure panel assembly to the chosen journal's style;
target-journal choice (`LITERATURE_REVIEW.md` §5); a human co-author repeating the verification
pass and a final read against `DO_NOT_CLAIM.md`.

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
calibration-, conformal-, and selective-deferral-based mitigation strategies against a
pre-specified multi-metric gate.
Robustness was assessed across an alternative 8.0-kPa threshold and two independently constructed
cohorts and a within-NHANES demographic holdout.

**Results.** The five families reached statistically indistinguishable discrimination (test AUROC
0.823–0.843; 0/10 pairwise comparisons significant after BH correction). Four of five models
over-predicted risk severely in raw output (out-of-fold calibration intercepts −2.24 to −1.86); a
single out-of-fold Platt step restored aggregate calibration (test expected calibration error
0.25–0.30 → 0.01–0.03) without changing discrimination. Beneath this aggregate adequacy,
sensitivity for significant fibrosis was 27–48 percentage points lower in normal-weight than in
obese participants in all five models (all q ≤ 0.006), a finding we independently reproduced, that
was present in both model fits, and that tracked a BMI risk shortcut — at matched liver stiffness
the models assigned obese participants a 0.19–0.33 higher predicted probability (p < 0.001) —
although a residual contribution of BMI-dependent measurement of the reference standard could not
be excluded.
Split-conformal prediction met its 90%
marginal coverage target overall (88–91%) but under-covered obese (77–82%) and, less robustly,
older (81–86%) participants — and their intersection (65–75%) — in every model, while
normal-weight and younger participants over-covered. This coverage failure replicated on both
sensitivity cohorts and the alternative threshold. No mitigation strategy tested — group-wise
conformal recalibration, subgroup-specific thresholds, subgroup calibration, equalized-odds
post-processing, model retuning, joint intersectional calibration, or conformal selective
deferral — produced an acceptable multi-metric fix; group-wise conformal recalibration restored
subgroup coverage only by over-covering the well-served subgroups, and selective deferral did not
help because the under-coverage is carried by confidently-scored singleton predictions. Withholding an entire
demographic subgroup from training degraded discrimination and calibration on that subgroup.

**Conclusions.** In a large US survey population, routine-data models for significant liver
fibrosis reach a comparable, modest-to-strong discrimination ceiling and can be made
aggregate-calibrated, yet still under-detect normal-weight patients and provide systematically
over-confident prediction sets for obese and older patients. **Discrimination plus aggregate
calibration are insufficient evidence of subgroup-safe reliability**; the failing subgroups here
were identifiable, reproducible across independently constructed cohorts, mechanism-linked, and
resistant to every post-hoc mitigation strategy we tested — the residual failure is a
within-subgroup score-ordering problem that points to a training-time rather than a post-hoc
remedy. External validation has not been performed and is the foremost outstanding requirement.

---

## 1. Introduction

Significant liver fibrosis is common and under-diagnosed, and non-invasive triage tools that use
only routine primary-care variables are attractive for population screening. The established
serum indices (FIB-4, the NAFLD Fibrosis Score [NFS], APRI) are used in a widely adopted two-step
pathway — a first-line blood score, then vibration-controlled transient elastography (VCTE) or the
Enhanced Liver Fibrosis test for those above a rule-out cut-point — which reduces unnecessary
specialist referral by roughly 80% [8]. A growing machine-learning literature aims to improve the
first step, and several models have been built on the National Health and Nutrition Examination
Survey (NHANES) with a VCTE reference standard, reaching areas under the receiver operating
characteristic curve (AUROC) of approximately 0.82–0.87 and outperforming FIB-4/APRI/NFS
[1,2]. These models are almost always benchmarked on AUROC and, in better studies, on calibration
curves or the Brier score.

Two well-documented problems with this evaluation paradigm motivate the present work. First,
**the serum indices themselves are known to be BMI-dependent**: FIB-4 sensitivity is roughly
constant across body-mass categories, but NFS — which takes BMI and diabetes as positive
predictors — has substantially lower sensitivity in lean patients (about 54% versus FIB-4's 82%
at standard cut-points), and both indices lose accuracy at the BMI extremes [4,5,6,7]. Whether
modern multi-feature ML inherits this behaviour, and how it interacts with other demographic
axes, is not established. Second, **aggregate metrics average over the population and can hide
subgroup-specific failure** — a model can discriminate and calibrate well overall while
systematically missing cases in a demographic subgroup [12,13]; and **class-imbalance corrections,
now near-universal in this literature, are known to miscalibrate probabilities** by shifting the
implicit outcome prevalence, an effect corrected only by post-hoc recalibration [10,11]. Third,
point predictions — even calibrated probabilities — do not convey case-level uncertainty.
Conformal prediction supplies prediction *sets* with a distribution-free finite-sample coverage
guarantee [15,16], but that guarantee is *marginal*: it holds on average over the population, and
exact conditional (subgroup) coverage is provably unattainable without distributional assumptions
[17]. Group-balanced variants exist [18,22], but forcing equal coverage can itself increase
downstream decision disparity [21].

Prior work has examined these dimensions **separately**. Sex-related bias has been reported in
liver-disease classifiers on other datasets [12]; the class-imbalance calibration artifact has
been shown generally [10,11] and on the same NHANES release with a near-identical VCTE outcome
[1]; and conformal prediction has been applied to liver-disease risk on non-NHANES cohorts, where
no subgroup coverage failure was reported [23]. We are not aware of a study that holds all of them —
discrimination, aggregate calibration, a pre-specified multi-axis subgroup fairness audit,
split-conformal *subgroup* coverage, and a structured mitigation battery — to the same standard,
under one frozen protocol, on this task.

We conducted such an audit on one pre-registered, hash-frozen NHANES cohort and outcome
definition, with multiplicity control throughout. Our aim was not to produce a deployable model —
the discrimination ceiling for this data type is modest and already well characterised — but to
determine, with a disciplined protocol, whether and how routine-data fibrosis models fail for
identifiable subgroups, and whether that failure is fixable within the model-development toolkit.

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
and its rationale were fixed before any model was trained.** The elastography examination is
instrument-measured and was performed independently of, and blind to, the predictor variables. Two severity-graded outcomes
(advanced fibrosis `≥ 9.7 kPa`; cirrhosis `≥ 13.6 kPa`) were pre-registered as secondary and are
reported descriptively (§2.9, §3.11).

### 2.3 Predictors

Ten routine variables, frozen before training: age, sex, BMI, alanine aminotransferase (ALT),
aspartate aminotransferase (AST), albumin, alkaline phosphatase, total bilirubin, platelet count,
and HDL cholesterol. All are demographic or standard laboratory measurements taken as part of the
NHANES examination, independently of and blind to the elastography outcome. **Race/ethnicity was
excluded from the model input by design** and retained only for post-hoc fairness stratification —
an explicit, documented decision, not an omission. Direct elastography-derived quantities were
forbidden as predictors.

### 2.4 Model development

A single stratified 70/30 split (seed 42) produced a training partition (N = 5,007; 466 positive)
and a **locked test set (N = 2,146; 200 positive)** that was evaluated once per analysis phase.
The sample size was fixed by the available NHANES release rather than by an a-priori power
calculation; the resulting events-per-predictor and subgroup-cell sizes are reported and their
limits discussed (§5, limitations B1–B3). Hyperparameters were tuned by 5-fold stratified
cross-validation within the training partition only. Five families were fitted: logistic regression and multilayer perceptron (with feature
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

### 2.7b Two model fits and their alignment

Two fits of each family are used. The subgroup fairness audit (§2.6) evaluates the models trained
on the full training partition (N = 5,007). The split-conformal analysis (§2.7) evaluates models
refit on the proper-training subset (N = 4,005), because the conformal architecture requires a
calibration set disjoint from both training and test. Findings are reported for each fit; a
pre-registered sensitivity analysis (Amendment #18; §3.4b) confirms the body-mass sensitivity
deficit is present in both fits, so the fairness-audit finding and the conformal finding concern
the same subgroup failure.

### 2.8 Mitigation

We applied group-wise (Mondrian) conformal recalibration to the model × subgroup combinations
that were BH-significant in **both** the fairness and the conformal analysis (BMI-obese and
age-60+). Separately, we evaluated a structured set of interventions against a pre-specified
multi-metric acceptance gate: BMI-specific decision thresholds, BMI-specific Platt scaling,
joint BMI × age thresholds, subgroup-specific calibration, equalized-odds (equal-opportunity)
post-processing, model retuning within the frozen hyperparameter family, joint
(intersectional) conformal calibration, and — under a later pre-registered amendment
(Amendment #17) — conformal selective deferral (abstaining on flagged-uncertain cases and
referring them to elastography). Mitigation candidates were compared descriptively against
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

### 2.10 Demographic holdout

For a within-NHANES transportability probe, models were retrained with all Non-Hispanic Black
participants withheld (train N = 5,366) and evaluated on that withheld subgroup (N = 1,787).

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

### 2.13 Related-work search

A structured single-reviewer search of PubMed/MEDLINE, arXiv, and general web sources was
conducted (last run 2026-08-27; query strings and results in the supplement), covering
routine-data machine-learning models for liver fibrosis, class-imbalance calibration, algorithmic
fairness of clinical prediction models, and conformal prediction with subgroup/conditional
coverage. This was a scoping search to position the contribution, not a PRISMA systematic review;
a two-screener search with recorded database hit counts is planned before publication.

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
mechanism is empirical, not causal. A pre-registered matched-stiffness check (Amendment #18)
sharpened this: among test participants with liver stiffness in the 8.2–12 kPa band, obese
participants received a predicted probability 0.19–0.33 higher than normal-weight participants at
*identical* measured stiffness (ordinary-least-squares `obese` coefficient, p < 0.001 in all five
models), indicating the models use body mass itself as a risk cue. Sex and race/ethnicity showed
no BH-significant sensitivity or AUROC disparity in the primary complete-case test set
(in-distribution only).

### 3.4b Consistency of the body-mass gap across model fits (Amendment #18)

The subgroup fairness audit uses the full-train models; the conformal analysis uses the
proper-train-refit models (§2.7b). Re-computing the normal-weight-vs-obese sensitivity gap on the
**refit** models, from the frozen conformal predictions, reproduced the deficit: classification
sensitivity at a calibration-derived Youden threshold was 27–42 percentage points lower in
normal-weight participants in all five models (logistic −42.0, random forest −27.5, XGBoost −32.1,
LightGBM −32.8, perceptron −35.3 pp), and the gap was negative at every threshold in a
0.30–0.60 classification sweep for four of five models (the perceptron gap turns positive above
0.45). The perceptron's refit also produces near-empty conformal positive sets across all
subgroups, so its conformal-sensitivity gap is uninformative and only its classification gap is
read. By the pre-registered rule this is a **STRENGTHENING** outcome: the fairness-audit and
conformal findings concern the same subgroup failure in two related fits, not an artefact of one
fit.

### 3.4c Reference-standard measurement bias (Amendment #18)

VCTE over-reads liver stiffness at high BMI, so some obese "significant-fibrosis" labels near the
8.2-kPa cut-point may be inflated. In a pre-registered relabel-only sensitivity analysis (outcome
redefined at LUXSMED ≥ 9.7, 10, 12, 13.6 kPa; model scores unchanged), three findings argue
against this artefact explaining the body-mass disparity. First, obese sensitivity and obese
conformal coverage were stable when the outcome was restricted to unambiguous fibrosis
(LUXSMED ≥ 12 kPa; median change in obese sensitivity 0.03), whereas a measurement artefact
concentrated near 8.2 kPa would predict a drop. Second, BMI-obese conformal under-coverage
persisted — and slightly worsened for four of five models — under the same restriction (coverage
0.70–0.77 at ≥ 12 kPa for the four class-weighted models). Third, the matched-stiffness result
(§3.4) shows a BMI-driven score gap at identical stiffness. The raw sensitivity gap between obese
and normal-weight positives does narrow, and slightly reverses, as the stiffness threshold rises,
but normal-weight participants have only 7 fibrosis-positive test cases at ≥ 12 kPa, so that
comparison is uninterpretable. By the pre-registered rule the verdict is **V3 (underpowered on
the normal-weight side)**: a residual measurement contribution cannot be formally excluded and a
histology- or MRE-referenced cohort would be needed to do so, but the demonstrated mechanism does
not depend on it (§5).

### 3.5 Marginal versus subgroup conformal coverage (primary finding)

Split-conformal prediction met its target overall: marginal coverage **88.1–90.8%** across the
five models. Within subgroups, coverage **failed** for the same populations flagged by the
fairness audit: **BMI-obese 76.8–82.3%** and **age-60+ 81.1–85.6%**, with Wilson intervals
excluding 90% and BH-significant for every model; the **obese-and-60+ intersection (N = 294)
fell to 65–75%** (Wilson intervals exclude 90%). Normal-weight, overweight, and 18–39-year-old
participants **over-covered** (≈ 0.94–0.97) — the marginal guarantee is met by borrowing coverage
from over-served subgroups
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
two.

A subsequent pre-registered evaluation of **conformal selective deferral** (Amendment #17) —
abstaining on flagged-uncertain cases and referring them to elastography — did not improve
subgroup coverage: no candidate rule met the pre-specified gate on the calibration partition, so
the locked test was not touched. The mechanism is diagnostic. In the under-covered subgroups the
conformal coverage is carried by the two-class {positive, negative} prediction sets, which always
contain the truth; the misses are confidently-scored *singleton* predictions. Deferring uncertain
(two-class) cases therefore removes covering predictions and lowers retained coverage. A
group-conditional (Mondrian) recalibration restored ≥ 0.88 subgroup coverage for BMI-obese and
age-60+ in all five model families with **zero** deferral — improving on the 5-of-9
model×subgroup result above — but necessarily raised retained marginal coverage to 0.94–0.95;
returning marginal coverage to target would require deliberately under-covering the well-served
subgroups (*levelling down*). The residual failure is a within-subgroup score-ordering problem
that no post-hoc decision layer repairs; a training-time intervention (subgroup reweighting or a
subgroup-aware objective) is the indicated next step and is outside this study's frozen scope.

### 3.8 Older-age findings (secondary observation)

The age-60+ **sensitivity** deficit was directionally consistent (negative in all five models,
−8.6 to −14.7 pp) but reached BH significance in **four of five** models (not logistic), was lost
under 9 of 12 alternative cohort/threshold specifications, and reflects a **non-monotonic** age
effect (peak ≈ 65 y, no further decline at 70+). We therefore report it as a hypothesis-generating
observation rather than an established disparity. The age-60+ **conformal under-coverage**
(§3.5–3.6) is a separate, firmer result and is retained at full strength.

### 3.9 Demographic holdout

Withholding all Non-Hispanic Black participants from training reduced discrimination on that
subgroup (AUROC 0.772–0.789, −0.05 to −0.06) and destabilised calibration (holdout intercepts
−0.58 to −2.17; slopes 0.64–0.97). This is a within-NHANES demographic holdout, **not external
validation**.

### 3.10 Sensitivity and secondary outcomes

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

### 3.11 Interpretability

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
under-detect normal-weight patients — a 27–48-point sensitivity gap that we reproduced and that is
stable across three sensitivity constructions. This is
the opposite of reassuring: normal-weight patients with fibrosis are exactly the group for whom a
routine-data screen might add the most value over a BMI-driven clinical prior, and they are the
group the models miss. In parallel, split-conformal prediction — whose marginal guarantee is
often presented as a subgroup-safety property — under-covers obese and older patients (and their
intersection) in every model, on every cohort construction we tried, while over-covering the
better-served subgroups. Marginal coverage is met by redistribution, not by uniform reliability.

Neither failure was repairable within our scope. Group-wise conformal recalibration is a genuine
but partial repair that trades a subgroup fix for marginal over-coverage; threshold tuning
helps one gap while worsening another because the two gaps have different mechanisms; selective
deferral cannot help because the under-coverage is carried by confidently-scored singleton
predictions rather than flagged-uncertain cases; and every calibration-, post-processing-, or
retuning-based approach we tested either failed the pre-specified gate or failed to generalise
across model families. The common thread is that the residual failure is a within-subgroup
score-ordering problem, which points to a training-time intervention (subgroup reweighting or a
subgroup-aware objective) as the next step — outside this study's frozen scope.
Reporting "we identified a problem we could not solve with post-hoc methods" is uncomfortable but
is the accurate result.

Two framing points follow. First, the body-mass finding, not the age finding, is the robust
subgroup result; the age-60+ *sensitivity* deficit is directionally suggestive but statistically
fragile and should be read as hypothesis-generating. Second, the contribution is methodological: a
model that passes discrimination and aggregate-calibration review is not thereby shown to be
subgroup-safe, and conformal prediction's marginal guarantee does not close that gap. The failing
subgroups in this study are **identifiable** (obese and older patients, and normal-weight patients
for detection), **reproducible** (across three independently constructed cohorts and an alternative
outcome threshold), **mechanism-linked** (a score-distribution difference with a threshold component for the
body-mass gap; two distinct mechanisms for the body-mass and age gaps), and **resistant to every
mitigation strategy we tested**.

### 4.1 Relation to prior work

Our individual results are, taken one at a time, consistent with an existing literature; the
contribution is holding them together under one protocol. The **discrimination ceiling** (AUROC
≈ 0.82–0.84) matches prior NHANES routine-data fibrosis models [1,2]. The **calibration finding**
is a replication: class-imbalance correction is known to inflate minority-class probabilities and
is remedied by post-hoc recalibration [10,11], and a closely comparable finding has already been
reported on the same NHANES release with a near-identical VCTE outcome (Cao et al.'s > 8 kPa vs
our ≥ 8.2 kPa), corrected there by a Bayesian prevalence prior-shift (raw Brier ≈ 0.15 → 0.07)
rather than out-of-fold Platt scaling [1]; the numerical agreement between our out-of-fold
intercept shift (−2.24 to −2.05) and the prior-mismatch term (log[0.093/0.907] ≈ −2.27) makes the
mechanism explicit. The
**body-mass detection gap** is directionally consistent with the long-known limitation of the
NAFLD Fibrosis Score in lean patients [4,5]; our result shows the pattern survives in modern
five-family ML where BMI is one of ten features and race/ethnicity is excluded from the model,
that it is present in both model fits (§3.4b), and — unlike the serum-index literature — that it
co-occurs with a conformal coverage failure in the same subgroup. A pre-registered sensitivity
analysis (§3.4c) bounds the competing explanation of reference-standard measurement bias: VCTE
over-reads liver stiffness at high BMI, but obese sensitivity and obese conformal coverage were
stable when the outcome was restricted to unambiguous fibrosis, and at matched liver stiffness the
models still assigned obese participants materially higher risk scores (§3.4) — so the disparity
is, at least in part, the models using body mass as a risk shortcut rather than an artefact of the
labels. The normal-weight side of the measurement-bias question is underpowered and a residual
contribution cannot be formally excluded (§5).
That **marginal coverage does not imply subgroup coverage** is a theoretical
result [17], and enforcing equal coverage can worsen downstream fairness [21]; the same
marginal-vs-subgroup coverage gap has independently been reported in survey-based social-attitude
prediction (~13 percentage-point weighted subgroup gaps under standard split conformal) [28],
indicating the phenomenon is not specific to this clinical task. What we add is the
empirical demonstration on routine-data fibrosis triage, triangulated across cohort constructions,
that no tested group-wise method achieves acceptable and generalisable subgroup validity. This last point
contrasts with a recent conformal NAFLD-risk model on a non-NHANES cohort that reported
distribution-free coverage without a subgroup coverage failure [23] — a difference in task,
cohort, and outcome that itself argues against assuming subgroup validity transfers. *(Ref [23]'s
subgroup claim is to be re-checked against its full text — see `REFERENCE_VERIFICATION.md`.)* The closest fairness-audit
analog remains a sex-stratified analysis of liver-disease classifiers on a different dataset
[12].

## 5. Limitations

The following limitations are material and must be read with the results. The IDs in brackets
index `documentation/final_research_audit/FINAL_LIMITATIONS_REGISTER.md`; every item in that
register's mandated minimum set appears below.

- **No external or out-of-sample validation [J1, J4].** The models have never been evaluated on an
  independent, non-NHANES population or a later survey cycle, and no compatible cohort was
  identified. This is the foremost limitation. The Non-Hispanic Black holdout [J4] is a
  within-NHANES demographic holdout, not external validation.
- **No acceptable mitigation [D1].** No calibration-, threshold-, conformal-, or
  selective-deferral-based intervention tested produced an acceptable multi-metric fix for the
  body-mass reliability–fairness failure; mitigation candidates were compared against a
  pre-specified gate without candidate-vs-candidate significance testing [A2]. Group-conditional
  conformal recalibration restores subgroup coverage only by over-covering the well-served
  subgroups; selective deferral cannot help because the under-coverage is carried by
  confidently-scored singleton predictions, not flagged-uncertain cases. A training-time
  intervention was not attempted (frozen scope).
- **Conformal guarantees are marginal only [E1].** Split conformal provides a marginal coverage
  guarantee; subgroup coverage was empirically deficient and is **not** a conditional-validity
  guarantee. Group-wise mitigation was partial (5/9 targets) and breached the marginal-coverage
  tolerance for one model (+5.3 pp) [E3]; a re-run reaching 5/5 subgroup targets did so only by
  over-covering the well-served subgroups (retained marginal coverage 0.94–0.95); and in the
  overlap population single-attribute rules were applied sequentially, not jointly [E4].
- **Small subgroup and intersectional cells [B2, B3].** Normal-weight sensitivity rests on 22
  test positives; the underweight band (one positive) is uninterpretable and is excluded. The
  obese-and-60+ intersection cell has 294 participants and ~35 events; intersectional coverage
  and any joint calibration are descriptive.
- **Low outcome prevalence [B1].** At 9.31% prevalence (666 positives) positive predictive value
  is low (~0.12–0.25 at a Youden operating point) and subgroup estimates are imprecise.
- **Age-60+ sensitivity is specification-sensitive [A1].** Directionally consistent but
  BH-significant in only four of five models and lost under 9 of 12 alternative specifications. It
  is reported as a secondary observation.
- **Threshold sensitivity [G1, A5].** An 8.0-kPa cut-point preserved discrimination, the
  calibration correction, and the body-mass disparity, but altered the age-60+ disparity's
  significance and some conformal detail; 8.0 and 8.2 kPa were not tested for statistical
  equivalence, and 8.2 kPa is the primary analysis.
- **Calibration [C1, C2].** The four class-balanced models are unusable without out-of-fold
  recalibration — a mandatory step, not an option [C1] — and aggregate recalibration did not
  extend to subgroup-level calibration [C2].
- **Missing data [F1, F2, F3, D4].** Complete-case analysis is the pre-registered primary
  strategy; complete-case exclusion disproportionately affected Non-Hispanic Black participants
  (41.3% of exclusions vs 25.0% of the retained cohort) [D4], and a targeted multiple-imputation
  analysis addressed that specific selection question only [F1]. The multiple-imputation conformal extension is
  descriptive, lacks a fully reconstructable pipeline, and carries no pooled inferential estimate.
- **Design [J2, J3, J5, A2].** A single US survey program, a single pre-pandemic release for the
  primary analysis, a VCTE (`LUXSMED`, not liver biopsy) reference standard, adults only, and a
  single 70/30 split without nested outer resampling of the locked test set. Operating thresholds
  were derived from out-of-fold predictions and their adoption recorded as a protocol amendment.
- **Reference-standard measurement bias by BMI [J3].** VCTE liver-stiffness measurement is itself
  BMI-dependent: obesity (and, more specifically, skin-to-capsule distance) is associated with
  *falsely elevated* stiffness readings, and the standard probe is less reliable at high BMI
  [D1–D4 in `RELATED_WORK_SCAN.md`]. NHANES applies a quality rule but does not eliminate this.
  A component of the higher model sensitivity in obese participants could therefore reflect
  inflated stiffness labels in that group rather than true detection. A pre-registered relabel-only
  sensitivity analysis (Amendment #18; §3.4c) addressed this. Redefining the outcome at
  successively higher stiffness thresholds (9.7–13.6 kPa) left obese sensitivity and obese
  conformal coverage essentially unchanged (median change in obese sensitivity 0.03), and the
  BMI-obese conformal under-coverage persisted — evidence against an artefact concentrated near
  the 8.2-kPa cut-point. A matched-stiffness analysis showed the models assign obese participants a
  0.19–0.33 higher predicted probability than normal-weight participants at identical measured
  stiffness (p < 0.001, all five models), locating part of the disparity in a BMI risk shortcut
  that is independent of the measurement artefact. However, normal-weight participants have only 7
  fibrosis-positive test cases at ≥ 12 kPa, so the normal-weight side cannot be adjudicated and a
  residual measurement contribution cannot be formally excluded (pre-registered verdict: V3,
  underpowered). A biopsy- or magnetic-resonance-elastography-referenced cohort would be required
  to fully separate a measurement artefact from a genuine detection deficit.
- **Pre-registered analyses not executed.** The all-ages (adolescent-inclusive) sensitivity
  cohort and survey-weighted / weighted-loss model training were pre-registered exploratory items
  and were formally deferred; no conclusion depends on them.

## 6. Conclusion

Routine-data machine-learning models for significant liver fibrosis reach a comparable,
modest-to-strong discrimination ceiling and can be made aggregate-calibrated, yet still
under-detect normal-weight patients and provide over-confident prediction sets for obese and older
patients — failures that discrimination and aggregate calibration conceal. **Discrimination plus
aggregate calibration are insufficient evidence of subgroup-safe reliability.** In this study the
failing subgroups were identifiable, reproducible across independently constructed cohorts,
mechanism-linked, and resistant to every post-hoc mitigation strategy we tested; the residual
failure is a within-subgroup score-ordering problem that a training-time intervention, not a
post-hoc layer, would need to address. Independent external validation is the necessary next step
before any consideration of use.

---

## Declarations

**Funding.** This research received no specific grant from any funding agency in the public,
commercial, or not-for-profit sectors. The author is an independent researcher and self-funded
this work.

**Competing interests.** The author declares no competing interests.

**Ethics approval and consent to participate.** This is a secondary analysis of the publicly
available, de-identified NHANES 2017–March 2020 data. The NHANES protocol was approved by the
NCHS Research Ethics Review Board, and all participants provided written informed consent. No
additional ethical approval was required for this analysis of public data.

**Protocol and pre-registration.** The analysis protocol — cohort definition, primary outcome
(`LUXSMED ≥ 8.2 kPa`), the ten predictors, the fairness dimensions, the conformal target, and the
multiplicity strategy — was frozen and hash-verified before any model was trained. All subsequent
deviations are recorded as dated protocol amendments (19 in total; supplied with the code). The
study was not registered on a trial/registry platform, being a methodological analysis of
existing public data.

**Data and code availability.** The NHANES 2017–March 2020 public-use files are available from the
NCHS (`https://www.cdc.gov/nchs/nhanes/`). All analysis code, the frozen protocol and amendment
registry, the pinned computational environment, per-participant split membership (by NHANES
respondent sequence number), model-to-script lineage, frozen artefact hashes, and the full
results tables will be deposited in a public repository with a versioned archival DOI on
acceptance. No individual-level data are redistributed; the code regenerates every result from
the public NHANES files.

**Author contributions.** The single author designed the study, wrote the code, performed the
analysis and the internal audit, and wrote the manuscript.

**Reporting guideline.** This study is reported in accordance with TRIPOD+AI [9]; the completed
checklist is provided as a supplement.

---

## References

*Verification status: `documentation/manuscript/REFERENCE_VERIFICATION.md` (each entry checked
against its primary source, 2026-08-27; a co-author should repeat the pass). Items marked
[author list to confirm] still need the full byline. Full positioning is in `LITERATURE_REVIEW.md`.*

1. Cao D, Wang J, Hou C, et al. Integrative and interpretable machine learning framework for early non-invasive detection of clinically significant liver fibrosis. *Front Med (Lausanne)* 2026;13:1736295. doi:10.3389/fmed.2026.1736295
2. Machine learning-based disease risk stratification and prediction of metabolic dysfunction-associated fatty liver disease using vibration-controlled transient elastography: result from NHANES 2021–2023. *BMC Gastroenterol* 2025;25:255. doi:10.1186/s12876-025-03850-x [author list to confirm]
3. Fibro predict: a machine learning risk score for advanced liver fibrosis in the general population using Israeli electronic health records. *Sci Rep* 2025;15:32035. doi:10.1038/s41598-025-17534-9. PMID:40887472
4. Accuracy of Fibrosis-4 index and non-alcoholic fatty liver disease fibrosis scores in metabolic (dysfunction) associated fatty liver disease according to body mass index: failure in the prediction of advanced fibrosis in lean and morbidly obese individuals. *Eur J Gastroenterol Hepatol* 2020. PMID:32976186. doi:10.1097/MEG.0000000000001946 [author list to confirm]
5. Diagnostic performance of the Fibrosis-4 index and nonalcoholic fatty liver disease fibrosis score in lean adults with nonalcoholic fatty liver disease. *JAMA Netw Open* 2023;6(8):e2328692. PMID:37589973 [author list to confirm]
6. Graupera I, et al. Low accuracy of FIB-4 and NAFLD Fibrosis Scores for screening for liver fibrosis in the population. *Clin Gastroenterol Hepatol* 2022;20(11):2567–2576. doi:10.1016/j.cgh.2021.12.034. PMID:34971806
7. Diabetes and obesity reduce FIB-4 accuracy in MASLD referral pathways. *JHEP Rep* 2026. doi:10.1016/j.jhepr.2026.101735 [author list to confirm]
8. Srivastava A, et al. Prospective evaluation of a primary-care referral pathway for patients with non-alcoholic fatty liver disease. *J Hepatol* 2019;71(2):371–378. doi:10.1016/j.jhep.2019.03.033. PMID:30965069
9. Collins GS, Moons KGM, Dhiman P, Riley RD, Beam AL, Van Calster B, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ* 2024;385:e078378. doi:10.1136/bmj-2023-078378. PMID:38626948
10. van den Goorbergh R, van Smeden M, Timmerman D, Van Calster B. The harm of class imbalance corrections for risk prediction models: illustration and simulation using logistic regression. *JAMIA* 2022;29(9):1525–1534. doi:10.1093/jamia/ocac093
11. Carriero A, Luijken K, de Hond A, Moons KGM, van Calster B, van Smeden M. The harms of class imbalance corrections for machine-learning-based prediction models: a simulation study. *Stat Med* 2025;44(3-4):e10320. doi:10.1002/sim.10320
12. Straw I, Wu H. Investigating for bias in healthcare algorithms: a sex-stratified analysis of supervised machine learning models in liver disease prediction. *BMJ Health Care Inform* 2022;29(1):e100457. doi:10.1136/bmjhci-2021-100457
13. Understanding algorithmic fairness for clinical prediction in terms of subgroup net benefit and health equity. *Epidemiology* 2026;37(3) [May issue]. Preprint: arXiv:2412.07879. [author list to confirm]
14. Critical appraisal of fairness metrics for artificial-intelligence-based clinical prediction models: a scoping review. *Lancet Digit Health* 2026. Preprint: arXiv:2506.17035. [author list to confirm]
15. Vovk V, Gammerman A, Shafer G. *Algorithmic Learning in a Random World*. Springer, 2005 (2nd ed. 2022).
16. Angelopoulos AN, Bates S. A gentle introduction to conformal prediction and distribution-free uncertainty quantification. arXiv:2107.07511, 2021. *Found Trends Mach Learn* 2023;16(4):494–591.
17. Barber RF, Candès EJ, Ramdas A, Tibshirani RJ. The limits of distribution-free conditional predictive inference. *Inf Inference* 2021;10(2):455–482. doi:10.1093/imaiai/iaaa017. arXiv:1903.04684
18. Romano Y, Barber RF, Sabatti C, Candès EJ. With malice toward none: assessing uncertainty via equalized coverage. *Harv Data Sci Rev* 2020;2(2). doi:10.1162/99608f92.03f00592
19. Angelopoulos AN, Bates S, Fisch A, Lei L, Schuster T. Conformal risk control. *ICLR* 2024. arXiv:2208.02814
20. Conformal prediction in clinical artificial intelligence. *CHEST* 2026 (article S0012-3692(25)05184-0). [author list to confirm from full text]
21. Cresswell JC, Kumar B, Sui Y, Belbahri M. Conformal prediction sets can cause disparate impact. *ICLR* 2025 (Spotlight). arXiv:2410.01888
22. Zhou Y, Sesia M. Conformal classification with equalized coverage for adaptively selected groups (adaptively fair conformal prediction, AFCP). *NeurIPS* 2024. arXiv:2405.15106
23. Zhang X. Conformal risk prediction for non-alcoholic fatty liver disease using gradient boosting with distribution-free coverages. arXiv:2606.09860, 2026.
24. Jones E, Sagawa S, Koh PW, Kumar A, Liang P. Selective classification can magnify disparities across groups. *ICLR* 2021. arXiv:2010.14134
25. Schreuder N, Chzhen E. Classification with abstention but without disparities. *UAI* 2021 (PMLR v161). arXiv:2102.12258
26. Madras D, Pitassi T, Zemel R. Predict responsibly: improving fairness and accuracy by learning to defer. *NeurIPS* 2018. arXiv:1711.06664
27. Kwon H, Kim DJ. Conformal selective prediction with cost-aware deferral for safe clinical triage under distribution shift. *Sci Rep* 2026. doi:10.1038/s41598-026-40637-w
28. Rafe A, Das S. Socio-conformal calibration in complex survey data: marginal validity is not enough for subgroup reliability. arXiv:2605.05562, 2026.

---

## Tables

**Table 1 — Baseline characteristics of the primary analytic cohort (N = 7,153), overall and by
significant-fibrosis status.** Source: `results/tables/manuscript_table1_by_fibrosis.{csv,md}`
(`src/manuscript_01_table1.py`). Continuous: mean (SD), Welch *t*-test; categorical: n (%),
χ² test. Liver stiffness is the outcome measurement, shown for description only.

| Characteristic | Overall (N=7,153) | No fibrosis (n=6,487) | Significant fibrosis (n=666) | p |
|---|---|---|---|---|
| Age, years | 49.0 (18.1) | 48.3 (18.2) | 55.6 (16.0) | <0.001 |
| Body-mass index, kg/m² | 29.6 (7.2) | 29.0 (6.5) | 35.6 (9.8) | <0.001 |
| ALT, U/L | 22.4 (19.3) | 21.3 (17.5) | 33.2 (30.1) | <0.001 |
| AST, U/L | 21.9 (14.5) | 21.1 (11.8) | 30.4 (28.5) | <0.001 |
| Albumin, g/dL | 4.1 (0.3) | 4.1 (0.3) | 4.0 (0.4) | <0.001 |
| Alkaline phosphatase, IU/L | 77.6 (25.7) | 76.7 (23.7) | 86.8 (38.8) | <0.001 |
| Total bilirubin, mg/dL | 0.5 (0.3) | 0.5 (0.3) | 0.5 (0.3) | <0.001 |
| Platelet count, 10⁹/L | 246.7 (64.8) | 248.2 (63.8) | 232.6 (72.1) | <0.001 |
| HDL cholesterol, mg/dL | 53.4 (15.8) | 53.9 (15.7) | 48.3 (15.7) | <0.001 |
| Liver stiffness (VCTE), kPa | 5.8 (4.6) | 4.9 (1.2) | 14.2 (11.5) | <0.001 |
| Female sex, n (%) | 3,622 (50.6) | 3,350 (51.6) | 272 (40.8) | <0.001 |
| Race/ethnicity, n (%) | | | | 0.017 |
|  Non-Hispanic White | 2,484 (34.7) | 2,247 (34.6) | 237 (35.6) | |
|  Non-Hispanic Black | 1,787 (25.0) | 1,610 (24.8) | 177 (26.6) | |
|  Non-Hispanic Asian | 866 (12.1) | 814 (12.5) | 52 (7.8) | |
|  Mexican American | 902 (12.6) | 808 (12.5) | 94 (14.1) | |
|  Other Hispanic | 754 (10.5) | 685 (10.6) | 69 (10.4) | |
|  Other / multi-racial | 360 (5.0) | 323 (5.0) | 37 (5.6) | |
| Age band, n (%) | | | | <0.001 |
|  18–39 | 2,423 (33.9) | 2,301 (35.5) | 122 (18.3) | |
|  40–59 | 2,318 (32.4) | 2,097 (32.3) | 221 (33.2) | |
|  60+ | 2,412 (33.7) | 2,089 (32.2) | 323 (48.5) | |
| BMI band, n (%) | | | | <0.001 |
|  Underweight (<18.5) | 109 (1.5) | 104 (1.6) | 5 (0.8) | |
|  Normal (18.5–24.9) | 1,802 (25.2) | 1,730 (26.7) | 72 (10.8) | |
|  Overweight (25–29.9) | 2,316 (32.4) | 2,195 (33.8) | 121 (18.2) | |
|  Obese (≥30) | 2,926 (40.9) | 2,458 (37.9) | 468 (70.3) | |

*Prevalence of significant fibrosis: 9.31%. Fibrosis-positive participants are older, heavier,
more often male, and concentrated in the obese and 60+ bands — the covariate structure the
subgroup analyses interrogate.*

**Table 2 — Discrimination and calibration by model family, locked test set (N = 2,146; 200
positive).** Discrimination from `results/tables/phase3_final_baseline_results.csv`; calibration
(raw → out-of-fold-Platt-recalibrated) from `results/calibration/test_set_calibration_final.csv`;
pairwise comparison from `phase3_model_comparison_fdr.csv`.

| Model | Test AUROC (95% CI) | Test PR-AUC (95% CI) | Calib. intercept (raw → recal.) | Calib. slope (raw → recal.) | Brier (raw → recal.) | ECE (raw → recal.) |
|---|---|---|---|---|---|---|
| Logistic regression | 0.833 (0.802–0.861) | 0.373 (0.313–0.448) | −2.26 → −0.15 | 1.00 → 0.94 | 0.175 → 0.071 | 0.297 → 0.017 |
| Random forest | 0.834 (0.804–0.861) | 0.351 (0.292–0.420) | −1.97 → +0.02 | 1.28 → 1.07 | 0.146 → 0.071 | 0.245 → 0.011 |
| XGBoost | 0.843 (0.812–0.869) | 0.372 (0.310–0.441) | −2.16 → +0.12 | 1.16 → 1.12 | 0.156 → 0.069 | 0.257 → 0.015 |
| LightGBM | 0.839 (0.809–0.867) | 0.373 (0.312–0.445) | −2.18 → +0.14 | 1.20 → 1.13 | 0.160 → 0.070 | 0.264 → 0.014 |
| MLP (unweighted) | 0.823 (0.790–0.853) | 0.365 (0.304–0.440) | −0.44 → −0.12 | 0.93 → 1.12 | 0.072 → 0.071 | 0.029 → 0.026 |

*0/10 pairwise AUROC comparisons were significant after Benjamini–Hochberg correction. AUROC is
unchanged by recalibration by construction. The four class-balanced models (logistic, random
forest, XGBoost, LightGBM) show the large negative raw intercepts characteristic of the
prevalence prior-shift; the unweighted MLP does not.*

**Table 3 — Split-conformal coverage (α = 0.10; target 0.90), primary cohort, and replication.**
`results/uncertainty/{marginal_coverage_test_set,subgroup_coverage}.csv`;
`results/sensitivity/conformal_replication_subgroup.csv`;
`results/fairness_bmi_investigation/phase6_8kpa_robustness/phase6_8kpa_conformal_results.csv`.
Empirical coverage; Wilson 95% intervals; one-sample binomial test vs 0.90, BH-corrected within
each model × dimension family. **Bold** = interval excludes 0.90 and BH-significant.

| | Logistic | Random forest | XGBoost | LightGBM | MLP |
|---|---|---|---|---|---|
| **Marginal (overall)** | 0.908 | 0.896 | 0.881 | 0.896 | 0.892 |
| BMI — Normal | **0.968** | **0.964** | **0.961** | **0.970** | **0.954** |
| BMI — Overweight | **0.969** | **0.963** | **0.963** | **0.972** | **0.948** |
| **BMI — Obese** | **0.823** | **0.802** | **0.768** | **0.792** | **0.809** |
| Age — 18–39 | **0.958** | **0.939** | **0.943** | **0.941** | **0.953** |
| Age — 40–59 | 0.919 | 0.893 | 0.890 | 0.901 | 0.884 |
| **Age — 60+** | **0.849** | **0.856** | **0.811** | **0.848** | **0.838** |
| Obese ∩ 60+ (N = 294) | 0.694 | 0.752 | 0.650 | 0.711 | 0.738 |
| **BMI-Obese, CAND_2** | **0.790** | **0.812** | **0.802** | **0.805** | **0.841** |
| **BMI-Obese, CAND_3** | **0.799** | **0.813** | **0.817** | **0.838** | **0.838** |
| **BMI-Obese, 8.0 kPa relabel** | 0.790–0.822 across models (all BH-significant) | | | | |
| Age-60+, CAND_2 | **0.823** | **0.871** | **0.856** | **0.863** | **0.862** |
| Age-60+, CAND_3 | **0.850** | 0.869 | 0.871 | 0.882 | **0.861** |

*Marginal coverage holds; BMI-Obese under-coverage is BH-significant in 5/5 models on CAND_1 and
on both replication cohorts; Age-60+ under-coverage is BH-significant 5/5 on CAND_1 and CAND_2,
2/5 on the smaller CAND_3. Normal-weight, overweight, and 18–39-year-old participants over-cover
throughout.*

**Table 4 — Mitigation strategies evaluated against the pre-specified multi-metric acceptance
gate.** Gate: full-cohort sensitivity and specificity within 5 pp of baseline; Brier within
+0.01; Age-60+ vs 40–59 sensitivity gap within +5 pp; then absolute BMI gap as a secondary
comparison. Sources: `results/mitigation/*`,
`results/fairness_bmi_investigation/{phase3_corrected,phase4_corrected,phase7_mitigation_cleanup}/*`,
`results/selective_deferral/*` (Amendment #17).

| Intervention | Objective | Result vs gate | Disposition |
|---|---|---|---|
| Group-wise (Mondrian) conformal recalibration | restore subgroup conformal coverage | primary analysis (Project Phase 7): nominal coverage restored in **5 / 9** targeted model×subgroup combinations; **XGBoost marginal coverage 93.4% (+5.3 pp tolerance breach)**; overlap handled by sequential (age-over-BMI) precedence. Re-run under Amendment #17 on the conformal-calibration partition: **≥ 0.88** BMI-obese and age-60+ coverage in **5 / 5** models with zero deferral, but retained marginal coverage rises to **0.94–0.95** (over-covers) | **PARTIALLY EFFECTIVE** (coverage only; trades a subgroup fix for marginal over-coverage) |
| BMI-specific decision thresholds / BMI-specific Platt / BMI×Age thresholds / combined (independent split) | close the normal-weight sensitivity gap | **none** passed the gate across model families; MLP only received a candidate (BMI-Platt: locked-test gap 39.0 → 34.5 pp; no formal inference) | **NO ACCEPTABLE MITIGATION** |
| Subgroup-specific probability calibration | improve subgroup reliability via calibration | ECE improved for 3 models; classification decisions and sensitivity gaps unchanged; no reliability gain (Decision B) | **NO ACCEPTABLE MITIGATION** |
| Group-specific Youden thresholds (exploratory) | equalize subgroup sensitivity | BMI gap roughly halved but **age gap widened 26–133%**; ~38–40 pp specificity cost in normal-weight | **EXPLORATORY** — two-mechanism diagnostic, not a fix |
| Equalized-odds (equal-opportunity) post-processing (exploratory) | equalize true-positive rate | ~50–80 pp target-group sensitivity gain at ~40 pp specificity cost; ≈ 399 excess false positives per 1,000 normal-weight screened | **EXPLORATORY** — clinically unacceptable |
| XGBoost retuning within the frozen hyperparameter family | remove the XGBoost coverage-tolerance breach | every gap-closing candidate cost 11–22 pp overall sensitivity or flipped the breach | **NO ACCEPTABLE RETUNING** |
| Joint (intersectional) conformal calibration (exploratory) | restore Obese ∩ 60+ coverage | intersectional coverage ≥ 90% for 4–5/5 models on the primary cohort, but XGBoost/LightGBM breach the ±5 pp marginal tolerance; joint calibration cell N = 138 | **EXPLORATORY ONLY** |
| Conformal selective deferral (Amendment #17) | restore subgroup coverage by referring flagged-uncertain cases to elastography | **no candidate rule met the pre-specified gate** on the calibration partition (locked test not touched); deferring two-class {pos,neg} sets *lowers* retained coverage because the misses are confidently-scored singletons, not uncertain sets | **NO IMPROVEMENT** — mechanistic dead end for post-hoc deferral |

*Successful: none. No intervention resolved the body-mass reliability–fairness failure within the
pre-specified gate. The residual under-coverage is a within-subgroup score-ordering failure that
post-hoc methods cannot repair; a training-time intervention is the indicated next step.*

**Table 5 — Sensitivity / robustness summary (per-model detail in the cited CSVs).** Sources:
`results/sensitivity/primary_vs_sensitivity_comparison.csv`,
`sensitivity_discrimination_calibration_results.csv`, `mi_black_subgroup_comparison.csv`,
`conformal_replication_subgroup.csv`.

| Perturbation | Test AUROC band | Normal-vs-Obese sensitivity gap | Age-60+ vs 40–59 gap | Conformal BMI-Obese coverage | Verdict |
|---|---|---|---|---|---|
| **Primary** — 8.2 kPa, CAND_1 (test N=2,146) | 0.823–0.843 | 27.1–47.7 pp; **5/5 BH-significant** | −8.6 to −14.7 pp; BH-significant 4/5 | 0.768–0.823; **5/5 BH-significant** | — |
| 8.0-kPa outcome relabel (frozen predictions rescored) | 0.814–0.833 | 35.1–51.6 pp; 5/5 significant | negative 5/5; significant 2/5 | 0.790–0.822; 5/5 significant | discrimination + BMI gap robust; **Age significance is threshold-sensitive** |
| CAND_2 — relaxed elastography eligibility, fresh fit (N=7,639) | 0.853–0.857 | ≈ 30–55 pp; 5/5 significant | attenuated (significant 3/4 lost) | 0.790–0.841; 5/5 significant | pattern stable; Age significance lost |
| CAND_3 — fasting-extended 12-predictor, fresh fit (N=3,582) | 0.828–0.846 | ≈ 38–63 pp; 5/5 significant | attenuated (significant 4/4 lost) | 0.799–0.838; 5/5 significant | pattern stable; Age significance lost |
| Targeted multiple imputation (Non-Hispanic Black selection question; full pool N=7,768) | ΔAUROC < 0.007 | — | — | — | NHB sensitivity Δ ≤ ±4.2 pp; all bootstrap CIs include 0; 4/5 STABLE, MLP indeterminate |

*The full-pipeline 8.0-kPa re-run's own verdict was "some major findings are threshold-sensitive"
(Age-60+ significance, some conformal detail); 8.2 kPa remains the primary analysis. The
BMI-Obese sensitivity gap is stable in 15/15 tested model×cohort instances; the Age-60+ gap's
direction never reverses across these constructions but its significance is lost in 9/12.*

## Figures

All figure files below are committed PNGs in the repository (generated during the frozen
analysis). For submission they need only relabelling/panel assembly to the target journal's
style — no re-computation.

| # | Content | File(s) |
|---|---|---|
| **1** | ROC and precision-recall curves, five model families (test set) | `results/figures/phase3_roc_combined.png`, `results/figures/phase3_pr_combined.png` |
| **2** | Calibration curves, raw vs recalibrated, by model | `results/calibration/figures/calibration_curve_*.png` |
| **3** | Sensitivity by BMI band with disparity vs the normal-weight reference, by model | `results/fairness/figures/sensitivity_disparity_*.png` |
| **4** | Conformal coverage by subgroup with the 90% target line, by model (CAND_1) | `results/uncertainty/figures/subgroup_coverage_*.png` |
| **5** | Fairness–specificity trade-off (Pareto) for BMI and age interventions | `results/figures/figure1_bmi_fairness_vs_specificity_pareto.png`, `figure2_age_fairness_vs_specificity_pareto.png` |
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
| §3.4b fit alignment | FAIR-BMI-03 | MANUSCRIPT_READY |
| §3.4c reference-standard measurement bias | FAIR-BMI-04 | MANUSCRIPT_READY_WITH_QUALIFICATION |
| §3.5 conformal (marginal + subgroup) | CONF-01, CONF-02, CONF-03 | MANUSCRIPT_READY / _WITH_QUALIFICATION |
| §3.6 conformal replication | CONF-02 (updated, Amendment #16) | MANUSCRIPT_READY_WITH_QUALIFICATION |
| §3.7 mitigation | MIT-01…MIT-06 | _WITH_QUALIFICATION / EXPLORATORY_ONLY / NO_IMPROVEMENT |
| §3.8 age (secondary) | FAIR-AGE-01 | MANUSCRIPT_READY_WITH_QUALIFICATION (secondary observation) |
| §3.9 demographic holdout | GEN-01 | MANUSCRIPT_READY_WITH_QUALIFICATION |
| §3.10 sensitivity / secondary outcomes | SENS-01, SENS-02, SECOUT-01, MI-01 | _WITH_QUALIFICATION |
| §3.11 interpretability / DCA | INT-01, DCA-01 | MANUSCRIPT_READY / EXPLORATORY_ONLY |

**Claims explicitly not made** (per `DO_NOT_CLAIM.md`): no model is superior; no strong /
clinical-grade discrimination; no universal or subgroup calibration adequacy; no conditional /
subgroup / intersectional conformal validity; no successful mitigation — group-conditional
conformal recalibration is not described as "solving" the coverage failure (it over-covers the
well-served subgroups) and selective deferral is not described as effective; the
reference-standard measurement-bias question is bounded, not resolved (verdict V3); no external or
out-of-sample validation; the NHB holdout is not external validation; no
deployment readiness; no causal mechanism; the age-60+ sensitivity disparity is not a co-headline
finding and not significant in 5/5 models; the obese-and-60+ overlap is 294 people (13.7% of the
test set), not 62%.

## Appendix B — Reporting-guideline mapping (TRIPOD+AI [9])

A full TRIPOD+AI checklist is to be completed and submitted; the crosswalk below shows where each
item group is addressed.

| TRIPOD+AI item group | Where addressed |
|---|---|
| Title / abstract — model type, data, purpose | Title; structured abstract |
| Background & objectives; rationale for AI use | §1 (with related-work grounding); §1 final paragraph |
| Source of data, study design, setting | §2.1 (NHANES 2017–March 2020 combined release; cross-sectional) |
| Participants — eligibility, inclusion/exclusion, cohort flow | §2.1 (10,409 → 9,700 → 9,023 → 7,768 → 7,153); Table 1 |
| Outcome — definition, blinding, timing; **frozen before modelling** | §2.2 (`LUXSMED ≥ 8.2 kPa`; 8.2-kPa rationale; threshold fixed pre-training) |
| Predictors — definition, timing (before outcome), **frozen before modelling**; race/ethnicity handling | §2.3 (ten routine variables; prediction-time = pre-elastography; race/ethnicity excluded from input by design, retained for stratification) |
| Sample size / events per variable | §2.4 (466 training positives; 200 test positives); Limitation B1 |
| Missing data | §2.1 (complete-case by construction), §2.9 (targeted multiple imputation); Limitations F1–F3, D4 |
| Model development — algorithms, hyperparameter tuning, class imbalance | §2.4 (five families; 5-fold CV within training partition; class weights / `scale_pos_weight`; MLP unweighted) |
| Internal validation — resampling, data partitioning, leakage control | §2.4 (single locked 70/30 split; 80/20 proper-train/calibration sub-split); §2.12 (contamination audit 8/8; 44/44 internal tests); Limitation J2 (no nested outer resampling) |
| Calibration methods and assessment | §2.5, §3.3, Table 2 (calibration-in-the-large, ECE, Brier; out-of-fold Platt) |
| Model performance — discrimination, with CIs, **including subgroups** | §2.11, §3.2, §3.4, §3.5–3.6, Tables 2–3 (bootstrap / Wilson / Clopper–Pearson CIs; BH-FDR) |
| Fairness — approaches, rationale, subgroup results | §2.6, §3.4, §3.8 (pre-specified dimensions, disparity metric, within-family FDR); §4.1 |
| Uncertainty quantification | §2.7, §3.5–3.6 (split conformal; marginal + subgroup + intersectional coverage) |
| Model updating / transportability | §2.10, §3.9 (within-NHANES demographic holdout); §5 (no external or later-cycle validation — foremost limitation) |
| Multiplicity | §2.11 (within-family BH-FDR; project-wide 182-test pooled correction) |
| Fairness / equity impact on underserved populations | §2.6, §3.4, §4.1, §5 (D1, D4); DCA subgroup net benefit (§3.11, exploratory) |
| Limitations | §5 (mandated minimum set, indexed to `FINAL_LIMITATIONS_REGISTER.md`) |
| Data / code availability, reproducibility | §2.12; Declarations; `documentation/final_audit/REPRODUCIBILITY.md` |
| Funding / conflicts / ethics / protocol | Declarations section (funding: none/self-funded; competing interests: none; ethics: NCHS ERB + participant consent; protocol frozen pre-modelling, 19 amendments) |
