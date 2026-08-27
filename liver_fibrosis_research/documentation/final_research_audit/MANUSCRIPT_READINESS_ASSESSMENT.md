# MANUSCRIPT-READINESS ASSESSMENT

Read-only audit, 2026-08-27. "Completed" is not equated with "manuscript-ready". Assessment
dimensions rated: **STRONG · ADEQUATE WITH LIMITATIONS · LIMITED · INSUFFICIENT**.

---

## Overall verdict: **MANUSCRIPT-READY WITH SPECIFIED QUALIFICATIONS** (recommendation B)

The scientific state is stable and internally consistent. All primary analyses, the BMI
follow-up, the sensitivity suite, and a temporal cycle are complete. No required non-validation
work remains. The manuscript can be drafted now provided it carries the mandated limitations,
frames every non-primary result at its register tier, and makes none of the `DO_NOT_CLAIM.md`
claims.

---

## Dimension assessments

### RESULT VALIDITY — ADEQUATE WITH LIMITATIONS

- Primary results (discrimination, calibration, BMI fairness, marginal-vs-subgroup conformal,
  NHB holdout) are verified against raw artifacts and reproduced.
- One documentation conflict (C1: `MASTER_RESEARCH_RESULTS.md` conformal section vs raw CSVs) is
  flagged; it does **not** change any result because the raw artifact is authoritative and the
  other master report agrees with it.
- Mitigation results are all "no acceptable fix" / "partial" — valid negative/partial findings,
  not positive claims.
- Exploratory diagnostics are valid within their tier; two early scripts had leakage/scale
  defects and are superseded (not used).

### REPRODUCIBILITY — ADEQUATE WITH LIMITATIONS

- Strong: split ID files, model lineage, result-to-script lineage, frozen hashes, environment
  locks, 44/44 internal validation tests, contamination audit 8/8 PASS.
- Gaps (all disclosed, none load-bearing): Phase 5 MI conformal `LINEAGE NOT FOUND IN
  REPOSITORY`; frozen 8.2-kPa protocol commit / model manifest `NOT FOUND`; joint mitigation
  generating pipeline `NOT FOUND`; corrected Phase 4 runtime event log absent; one
  dependency-graph transcription gap.
- A reader outside this environment must note the primary code tree (`src/`, `data/`, `models/`)
  is referenced by lineage tables and hashes but was not re-executed in this audit (read-only).

### STATISTICAL SUPPORT — ADEQUATE WITH LIMITATIONS

- Discrimination: bootstrap CIs + BH-FDR (10 pairwise) + pooled 182-test FDR. STRONG.
- Fairness: bootstrap CIs + within-family BH-FDR; BMI finding STRONG (5/5), Age finding LIMITED
  (4/5, specification-sensitive).
- Conformal: Wilson / Clopper–Pearson CIs; marginal STRONG, subgroup STRONG (as a failure),
  intersectional LIMITED (small cell).
- Mitigation: no candidate-vs-candidate inference (descriptive gates only) — LIMITED but
  appropriate for "no acceptable mitigation" conclusions.
- MI: BH q=0.978 is a correction-ceiling artifact, not evidence of no effect — must be worded
  carefully.

### LINEAGE — ADEQUATE WITH LIMITATIONS

Primary result families (discrimination, calibration, fairness, conformal, temporal) have
documented result→script→input→artifact traces (`MASTER_END_TO_END_RESEARCH_REPORT.md` §L). The
exceptions are enumerated above and each carries an explicit missing-lineage token.

### INTERPRETABILITY — STRONG

Clinically grounded 10-predictor panel; consistent top-4 features (ALT/AST/BMI/Age); a clear
mechanistic account of the BMI disparity (score-distribution + threshold, non-causal); a clean
"Two-Mechanism" framing distinguishing threshold-driven (BMI) from non-threshold-driven (Age)
disparity; DCA showing net benefit within the plausible threshold range.

### LIMITATIONS — ADEQUATE (disclosure is thorough)

`FINAL_LIMITATIONS_REGISTER.md` enumerates 40+ limitations across 10 categories with severity and
wording. The mandated minimum set (external validation absent; partial temporal replication;
Age-60+ fragile; Phase 7 partial + XGBoost breach + sequential overlap; no acceptable BMI
mitigation; conformal marginal-only; conformal measured on CAND_1 only; MI narrow + no lineage;
NHB holdout internal; single survey / VCTE reference / cross-sectional; underweight
uninterpretable; class-balancing artifact) is complete.

---

## Findings that can be stated WITHOUT qualification

1. CAND_1 composition (N=7,153; 666 positives; 9.31%).
2. Five model families, test AUROC 0.8229–0.8429; no FDR-significant pairwise winner.
3. Class-balanced models over-predict raw risk; OOF Platt scaling corrects aggregate calibration
   without changing AUROC.
4. Normal-BMI vs Obese sensitivity deficit 27.1–47.7 pp in all five models (q ≤ 0.006).
5. Split conformal meets marginal coverage overall (88–91%) but under-covers BMI-Obese (77–82%)
   and Age-60+ (81–86%) in every model.
6. ALT, AST, BMI, Age are the top four predictors across all families.

## Findings that REQUIRE qualification

- Age-60+ deficit (direction robust; significant 4/5; specification-sensitive; non-monotonic).
- Project Phase 7 Mondrian mitigation (partial: 5/9; XGBoost marginal breach; sequential overlap).
- Corrected BMI mitigation / subgroup calibration (no acceptable improvement; MLP-only modest
  gap reduction; no formal inference).
- 8.0-kPa robustness ("some findings threshold-sensitive"; 8.2 kPa primary).
- CAND_2 / CAND_3 reproduction (pattern holds; Age significance does not).
- Targeted MI (narrow scope; correction-ceiling p-values).
- NHB holdout (within-NHANES; not external validation).
- Intersectional conformal coverage collapse (descriptive; small cell; 294 = 13.7%, not 62%).

## Findings that must remain EXPLORATORY

Continuous BMI/Age splines, fine age bands, subgroup recalibration + re-quantiling, group-specific
thresholds, Equal Opportunity post-processing, fairness–specificity Pareto, clinical
false-positive costs, faithful AFCP, joint intersectional conformal (Methods b/c, M4b), M4b
trade-offs, LightGBM failure analysis, co-occurrence, DCA.

## Findings that must be EXCLUDED

Historical baseline AUROCs / prevalences (transcription errors); Age-60+ 5/5 significance;
historical BMI-investigation Phase 3 / Phase 4 conclusions; KNN-AFCP; N0=100; the "294 ≈ 62%"
overlap characterisation; `MASTER_RESEARCH_RESULTS.md` conformal-coverage numbers and BMI label;
any CAND_4 or severity-graded secondary-outcome performance; any external-validation claim; any
full-temporal-replication or deployment-readiness claim; any causal claim.

---

## Required before submission (author-side housekeeping; not blocking analyses)

1. Correct or annotate `documentation/MASTER_RESEARCH_RESULTS.md` conformal section (conflict C1).
2. Add register entries for the severity-graded secondary outcomes and survey-weighted training
   (mark formally deferred; optionally run a relabel-only descriptive pass for the secondary
   outcomes).
3. Adjudicate on paper the joint-mitigation status conflict (C2) and the AFCP narrative status
   (C3) — a one-line decision each; no analysis.
4. Ensure the manuscript's limitations section reproduces the mandated minimum set from
   `FINAL_LIMITATIONS_REGISTER.md`.

## Not required

No additional experiments, no reruns, no retuning, no new cohort construction, no temporal or
external validation, are required for the manuscript to be submittable as a study of
discrimination, calibration, fairness, and conformal reliability in a US adult NHANES cohort with
a partial temporal replication.
