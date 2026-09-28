# Model card

Covers the five frozen tier-1 baseline models (Phase 3) and their Phase 4/6 calibration and
conformal wrappers. Numbers below are pulled directly from the cited frozen artifacts; if this
file and a CSV under `results/` ever disagree, the CSV is correct — see
`documentation/START_HERE.md` for the authority order. Anything not stated here as supported
should be assumed unsupported; the exhaustive list of claims this evidence base does **not**
support is `documentation/final_research_audit/DO_NOT_CLAIM.md`.

## Model details

- **Task:** binary classification — significant liver fibrosis (`LUXSMED >= 8.2 kPa` on VCTE,
  ≈F2+), threshold selected on clinical-evidence grounds (2024 VCTE-vs-MRE meta-analysis) before
  any model was trained.
- **Families (5, independently fit):** logistic regression, random forest, XGBoost, LightGBM,
  MLP. No family is claimed superior — 0/10 pairwise AUROC comparisons are FDR-significant
  (`results/tables/phase3_model_comparison_fdr.csv`).
- **Inputs (10 frozen predictors, zero missingness by cohort construction):** age (`RIDAGEYR`),
  sex (`RIAGENDR`), BMI (`BMXBMI`), ALT (`LBXSATSI`), AST (`LBXSASSI`), albumin (`LBXSAL`),
  alkaline phosphatase (`LBXSAPSI`), total bilirubin (`LBXSTB`), platelet count (`LBXPLTSI`),
  HDL cholesterol (`LBDHDD`) — all available at a routine outpatient visit, none derived from or
  encoding the elastography outcome (`documentation/phase2/prediction_time_and_leakage_protocol.md`).
  Race/ethnicity and BMI/age themselves are **not** predictors used for stratification-only
  fairness analysis, not model inputs beyond BMI/age already listed.
- **Training data:** NHANES 2017–March 2020, quality-valid elastography cohort, N=7,153
  (666 positive / 6,487 negative), seed=42, 70/30 split → train N=5,007, locked test N=2,146
  (`PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md` §identical-conditions table).
- **Calibration:** class-balanced training causes severe raw over-prediction (OOF intercepts
  −2.24 to −1.86); a single OOF-fit Platt scaling pass restores aggregate calibration on the
  locked test set (ECE 0.011–0.026, Brier 0.069–0.072) **without changing AUROC**
  (`results/calibration/primary_metrics_by_model.csv`).
- **Uncertainty:** split-conformal prediction sets at α=0.10, refit on a proper-train partition
  disjoint from the calibration/test split (`models/phase6_conformal_refit/`).
- **License:** MIT (repository root `LICENSE`); NHANES source data is public domain (CDC/NCHS).

## Intended use

Research artifact for a methodological audit of ML reliability practice in clinical prediction —
**not** a validated clinical decision-support tool. Appropriate uses: reproducing the study,
extending the fairness/calibration/uncertainty audit methodology to other models or cohorts,
teaching material on subgroup reliability auditing.

## Out-of-scope / do-not-use

- **Not for clinical deployment or individual patient risk assessment.** No external
  (non-NHANES) validation has been performed — the study's stated foremost limitation
  (`documentation/START_HERE.md`).
- **Not validated as fair or equitable.** See "Known limitations" below — this is the study's
  central finding, not a caveat.
- Do not use the *unmitigated* raw model scores for any threshold decision without the Phase 4
  Platt recalibration applied.

## Performance (locked test set, N=2,146)

| Metric | Range across 5 families | Source |
|---|---|---|
| AUROC | 0.8229–0.8429 | `results/tables/phase3_final_baseline_results.csv` |
| PR-AUC | ≈0.35–0.37 (prevalence ≈9.3%) | same |
| ECE, post-calibration | 0.011–0.026 | `results/calibration/test_set_calibration_final.csv` |
| Brier, post-calibration | 0.069–0.072 | same |
| Marginal conformal coverage (target 90%) | 88.12–90.82% | `results/uncertainty/marginal_coverage_test_set.csv` |

## Known limitations (fairness and reliability — the study's core findings, not edge cases)

1. **BMI-sensitivity disparity — the single most robust finding in the study.** Normal-BMI
   sensitivity is 27.1–47.7 percentage points lower than Obese, in all 5 models,
   FDR-significant, independently reproduced across 3 sensitivity cohorts (15/15)
   (`results/fairness/fairness_inference.csv`). **No tested mitigation** — Mondrian conformal
   recalibration, group thresholds, Equal Opportunity postprocessing, XGBoost retuning,
   training-time subgroup reweighting, selective deferral — resolved it
   (`documentation/final_research_audit/FINAL_SCIENTIFIC_FINDINGS.md` §7).
2. **Subgroup conformal under-coverage.** Marginal coverage meets the 90% target overall, but
   BMI-Obese (76.8–82.3%) and Age-60+ (81.1–85.6%) under-cover in every model — marginal
   validity is a mathematical guarantee, subgroup adequacy is not
   (`results/uncertainty/subgroup_coverage.csv`).
3. **Age-60+ sensitivity deficit** is directionally consistent (−8.6 to −14.7 pp) but
   statistically fragile (significant in 4/5 models, not Logistic) and non-monotonic
   (peaks ≈65y) — treat as a secondary, not headline, finding.
4. **Sex and race/ethnicity** showed no FDR-significant sensitivity/AUROC disparity in the
   primary complete-case test set — do **not** generalize this to "the model is fair"; it is
   not fair with respect to BMI and age.
5. **Temporal attenuation.** Applied unchanged to NHANES Aug 2021–Aug 2023, discrimination
   drops ~0.05 AUROC (concept drift concentrated in normal-weight participants); the BMI
   mechanism, conformal under-coverage, and matched-stiffness shortcut all replicate 5/5
   (`temporal_validation_2021_2023/README.md` — verdict: PARTIAL TEMPORAL REPLICATION).
6. **Retraining on the pooled 2017–2023 cohort does not fix any of the above** — verdict:
   the failure is structural, not a staleness artifact (`pooled_model_update_2017_2023/README.md`).

## How to reproduce

`documentation/final_audit/REPRODUCIBILITY.md` — exact environment, seeds, script run order.
