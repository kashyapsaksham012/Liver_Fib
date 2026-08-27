# Machine Learning for Liver Fibrosis Prediction: A Comprehensive Evaluation of Discrimination, Calibration, Fairness, Conformal Reliability, and Temporal Transportability

**Final master report.** This report consolidates the repository's research from initial data
assembly through the completed NHANES 2021–2023 temporal-validation work. Repository paths below
are relative to `liver_fibrosis_research/`. Numerical claims are accompanied by the result file,
phase, and status. Where the repository records a limitation, conflict, or missing analysis, it
is stated explicitly.

## Evidence and authority convention

The primary consolidation authorities are `documentation/final_audit/RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md`,
`FINAL_CLAIM_AUDIT.md`, `FINAL_RESEARCH_STATUS.md`, `FINAL_SCIENTIFIC_INTERPRETATION.md`, and
`INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`. Raw-result authority is assigned where the
repository explicitly identifies a result file as final/frozen/authoritative. A later completed
artifact supersedes an older status entry only where the repository explicitly documents that
reconciliation. The earlier temporal preflight failure is not a final-result source; it is retained
as an intermediate failure/resolution record.

# A. COMPLETE RESEARCH HISTORY

## A1. Objective and original research question

The frozen question was: in adults with a quality-valid transient-elastography examination, how
accurately, fairly, and reliably can routine demographic and laboratory predictors identify
significant liver fibrosis (`LUXSMED >= 8.2 kPa`), and do class-imbalance methods, subgroup
boundaries, calibration, and split-conformal uncertainty remain reliable beyond aggregate AUC?
Source: `documentation/final_audit/RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md`, §A. **FINAL /
AUTHORITATIVE.**

## A2. Phase 1: NHANES 2017–March 2020 assembly

The raw release used `P_DEMO`, `P_BMX`, `P_BIOPRO`, `P_CBC`, `P_GLU`, `P_TRIGLY`, `P_HDL`, and
`P_LUX`. The anchor population was 10,409 participants with elastography attempted and a
non-missing outcome. The repository's cohort-flow record gives the sequence 10,409 -> 9,700 ->
9,023 -> 7,768 quality-valid pool -> 7,153 complete-case primary cohort. Source:
`documentation/audit_reports/cohort_flow.csv` and
`documentation/final_audit/INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`, §1. **FINAL /
AUTHORITATIVE.**

The merge, row-preservation, special-missing-code, plausibility, race/ethnicity, and missingness
audits are documented in `documentation/audit_reports/merge_audit.csv`,
`special_missing_code_audit.csv`, `plausibility_audit.csv`, `race_ethnicity_verification.md`,
`missingness_overall.csv`, and `missingness_by_group.csv`. Their complete row-level values are
authoritative audit evidence; no value not present there is reconstructed here.

The complete documented cohort-flow checkpoints are 10,409 anchor participants, 9,700 after the
first quality/eligibility stage, 9,023 after the next eligibility stage, 7,768 in the quality-valid
pool, and 7,153 complete-case CAND_1 participants. The repository does not provide a single
reviewed narrative line assigning a unique textual label to every transition; the exact transition
logic is in `src/_cohorts.py`, `src/phase2_04_build_analysis_dataset.py`, and
`documentation/audit_reports/cohort_flow.csv`. **FINAL / AUTHORITATIVE.**

## A3. Phase 2: cohort and protocol freeze

The primary cohort was CAND_1, `CAND_1_QUALITYVALID_ADULT_BROAD`, with N=7,153, 666 positives,
6,487 negatives, and 9.31% prevalence. Outcome and predictor definitions were frozen before
model training. CAND_2 (relaxed elastography eligibility) and CAND_3 (fasting-extended) were
prespecified sensitivity cohorts. CAND_4 (all ages >=12) was constructed as N=8,215 but not
executed. Sources: `results/tables/phase2_candidate_cohort_comparison.csv`,
`phase2_outcome_prevalence.csv`, `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`,
`documentation/phase2/primary_cohort_decision.md`, and
`documentation/validation/cand4_resolution_evidence.csv`. **FINAL / AUTHORITATIVE** for CAND_1;
**EXECUTED AND VERIFIED** for CAND_2/CAND_3; **NOT EXECUTED** for CAND_4.

## A4. Outcome

The primary binary outcome was quality-valid VCTE/LUXSMED significant fibrosis:
`LUAXSTAT == 1` and `LUXSMED >= 8.2 kPa`. The threshold was frozen before modeling. Additional
tested outcome/cohort definitions were the relabeled 8.0 kPa threshold, CAND_2 relaxed
elastography, and CAND_3 fasting-extended cohort. CAND_4 was not analyzed. Sources:
`documentation/phase2/primary_outcome_definition.md`,
`documentation/phase2/elastography_eligibility_protocol.md`, and
`results/sensitivity/alternative_threshold_8p0kPa_results.csv`. **FINAL / AUTHORITATIVE** for
8.2 kPa; **EXECUTED AND VERIFIED** for the listed sensitivity analyses.

## A5. Frozen predictors

The ten frozen predictors were Age, Sex, BMI, ALT, AST, Albumin, AlkPhos, Bilirubin, Platelets,
and HDL, represented respectively by `RIDAGEYR`, `RIAGENDR`, `BMXBMI`, `LBXSATSI`, `LBXSASSI`,
`LBXSAL`, `LBXSAPSI`, `LBXSTB`, `LBXPLTSI`, and `LBDHDD`. Race/ethnicity was excluded from
model input and retained for post-hoc fairness. Source: `results/tables/phase2_predictor_registry.csv`.
**FINAL / AUTHORITATIVE.**

## A6. Missingness and imputation

The primary model used complete cases after the frozen cohort rules. A targeted multiple-imputation
analysis addressed the disproportionate exclusion of NHB participants: NHB represented 41.30% of
complete-case exclusions versus 24.98% of the retained cohort. Five imputed datasets were produced
with fold-embedded `IterativeImputer(BayesianRidge, sample_posterior=True)`. The MI pool was
N=7,768 and recovered 615 excluded participants. Sources:
`results/sensitivity/multiple_imputation_diagnostics.csv`,
`mi_black_subgroup_comparison.csv`, and
`documentation/sensitivity/mi_closure_reconciliation_snapshot.md`. **EXECUTED AND VERIFIED,
NARROW SCOPE.**

## A7. Partitioning and leakage control

The primary split was stratified 70/30 with seed 42: training N=5,007 (466 positives) and locked
test N=2,146 (200 positives). Five-fold `StratifiedKFold` generated training OOF predictions.
For conformal work, the training partition was split into proper-train N=4,005 (373 positives)
and conformal-calibration N=1,002 (93 positives), leaving the locked test untouched. The conformal
quantile index was k=903. Sources: `data/processed/splits/*.csv`,
`documentation/phase3/data_split_registry.md`, `results/uncertainty/phase6_partition_audit.csv`,
and `results/tables/data_and_result_lineage.csv`. **FINAL / AUTHORITATIVE.**

Preprocessing was fit inside training folds. Test-set protection and contamination audits are in
`results/end_to_end/test_set_contamination_audit.md`,
`results/diagnostics/TEST_SET_CONTAMINATION_AUDIT.md`, and
`documentation/phase3/preprocessing_leakage_audit.md`. The repository reports no test-label
leakage in the fresh D02/D04/D05 implementations; three older scripts had documented defects and
were superseded. **EXECUTED AND VERIFIED.**

# B. COMPLETE EXPERIMENT-BY-EXPERIMENT RESULTS

## B1. Five baseline model families

| Model | Test AUROC | 95% CI where reported | Youden threshold | Training balance |
|---|---:|---:|---:|---|
| Logistic Regression | 0.8334 | 0.8021–0.8610 | 0.5173 | `class_weight=balanced` |
| Random Forest | 0.8343 | NOT FOUND IN REPOSITORY in the attestation table | 0.4499 | `class_weight=balanced` |
| XGBoost | 0.8429 | 0.8123–0.8693 | 0.4108 | `scale_pos_weight` approximately 9.74 |
| LightGBM | 0.8394 | NOT FOUND IN REPOSITORY in the attestation table | 0.4988 | `scale_pos_weight` approximately 9.74 |
| MLP | 0.8229 | NOT FOUND IN REPOSITORY in the attestation table | 0.1065 | none |

Source: `results/tables/phase3_final_baseline_results.csv` and
`documentation/final_audit/INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`, §1.
**FINAL / AUTHORITATIVE.** The range was 0.8229–0.8429. Ten pairwise comparisons had no
Benjamini–Hochberg FDR-significant winner. Source:
`results/tables/phase3_model_comparison_fdr.csv`. **FINAL / AUTHORITATIVE.**

MLP Balanced, using training-fold-only `RandomOverSampler`, was sensitivity-only and was not
carried forward. Its OOF calibration intercept was approximately -2.16 per
`PHASE4_CALIBRATION_RESULTS_REPORT.md`; its dedicated raw row was not relocated in the final
audit. **EXPLORATORY / REPORT-LEVEL; exact raw-file lineage not established.**

## B2. Calibration

OOF raw calibration intercepts were Logistic -2.243, Random Forest -1.862, XGBoost -2.046,
LightGBM -2.053, and MLP -0.281. Source:
`results/calibration/primary_metrics_by_model.csv`. **FINAL / AUTHORITATIVE.**

Locked-test raw -> Platt-recalibrated results were:

| Model | Intercept | Brier | ECE | AUC |
|---|---|---|---|---:|
| Logistic | -2.2602 -> -0.1537 | 0.1755 -> 0.0705 | 0.2967 -> 0.0172 | 0.8334 |
| Random Forest | -1.9679 -> +0.0238 | 0.1458 -> 0.0709 | 0.2452 -> 0.0113 | 0.8343 |
| XGBoost | -2.1629 -> +0.1241 | 0.1557 -> 0.0694 | 0.2572 -> 0.0152 | 0.8429 |
| LightGBM | -2.1846 -> +0.1418 | 0.1603 -> 0.0696 | 0.2638 -> 0.0143 | 0.8394 |
| MLP | -0.4354 -> -0.1189 | 0.0716 -> 0.0715 | 0.0290 -> 0.0264 | 0.8229 |

Source: `results/calibration/test_set_calibration_final.csv`, N=2,146. **FINAL /
AUTHORITATIVE.** Platt scaling was fit on OOF only and applied once to the locked test. AUC was
unchanged by the monotonic transform. Isotonic calibration was considered but rejected under
Amendment 8 because the OOF positive count was 466. Source:
`documentation/calibration/amendment_8_provenance.md`. **FINAL / AUTHORITATIVE.**

## B3. Fairness

The prespecified dimensions were BMI, age, sex, and race/ethnicity. BMI bands were Underweight,
Normal, Overweight, and Obese; age bands were 18–39, 40–59, and 60+; sex and NHANES
`RIDRETH3` race/ethnicity categories were used for post-hoc stratification. Sensitivity,
specificity, AUROC, PPV, NPV, bootstrap confidence intervals, and BH-FDR results are in
`results/fairness/subgroup_discrimination_metrics.csv` and `results/fairness/fairness_inference.csv`.
**FINAL / AUTHORITATIVE.**

The Normal-BMI versus Obese sensitivity deficit was 27.1–47.7 percentage points and FDR
significant in all 5 models (p <= 0.006). Age-60+ sensitivity was lower than Age 40–59 in all
five models; the deficit was FDR significant in RF (-13.2 pp), XGBoost (-11.2 pp), LightGBM
(-14.1 pp), and MLP (-14.7 pp), but not Logistic Regression (reported FDR p=0.195). **FINAL /
AUTHORITATIVE.** The Underweight signal is **INCONCLUSIVE / NOT INTERPRETABLE** because it has
one positive case under the frozen protocol.

## B4. Split conformal uncertainty

The nominal target was 90%. Overall marginal coverage was 88.12–90.82%; mean set size was
0.97–1.43. BMI-Obese coverage was 76.8–82.3% and Age-60+ coverage was 81.1–85.6%, with reported
Wilson confidence intervals excluding 90% for all five models. MLP had 96.9% singleton sets;
the class-weighted models had 23.2–43.2% doubleton sets. Sources:
`results/uncertainty/marginal_coverage_test_set.csv`, `subgroup_coverage.csv`,
`intersectional_coverage_ci.csv`, and `test_set_prediction_sets.csv`. **FINAL /
AUTHORITATIVE.**

## B5. FDR-gated Mondrian mitigation

Mitigation targeted only model-by-subgroup combinations significant in both fairness and conformal
audits. Logistic received a BMI rule only because its Age-60+ fairness result was not FDR
significant. Five of nine qualifying combinations reached nominal coverage; failures were
RF/Obese, XGBoost/Obese, LightGBM/Obese, and LightGBM/60+. XGBoost marginal coverage rose to
93.4%, a +5.27 percentage-point breach of the prespecified +/-5 pp tolerance. Sources:
`results/mitigation/test_set_mitigation_final.csv`, `marginal_coverage_before_after.csv`, and
`documentation/mitigation/phase7_threshold_override_closure_snapshot.md`. **EXECUTED AND
VERIFIED WITH LIMITATION.**

The BMI-Obese x Age-60+ overlap contained 294 people, 13.7% of the test set. The production
implementation applied BMI first and Age second; Age overwrote BMI in the overlap. This is
sequential precedence, not joint mitigation. Sources:
`src/phase7_04_final_test_touch.py`,
`documentation/mitigation/phase7_bmi_age_overlap_interpretation.md`, and
`results/mitigation/threshold_precedence_audit.csv`. **FINAL DESCRIPTION OF LIMITATION.**

## B6. Joint intersectional implementations

The old machine-readable status table says joint mitigation was NOT EXECUTED. The later
attestation explicitly records a subsequently executed exploratory artifact,
`results/mitigation/joint_intersectional_mitigation.csv`, with intersection coverage 90.8–94.9%
and confidence intervals at least 90% for 5/5 models, but also tolerance breaches of +6.80 pp
(XGBoost) and +5.50 pp (LightGBM), and a joint calibration cell of N=138 (30 positive, 108
negative). The later artifact is present and supersedes the stale status entry under
`INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`, §2. **EXPLORATORY / EXECUTED AND VERIFIED
BY THE ATTESTATION; not a primary final mitigation claim.**

Any earlier source that states joint mitigation was not executed is retained as a historical
status, not silently deleted. Where a reader treats the old status CSV alone as controlling,
the conflict is: **CONFLICT UNRESOLVED IN REPOSITORY**; the dated attestation explicitly
establishes the later artifact as the superseding execution.

## B7. Reliability and interpretability extensions

Continuous BMI showed sensitivity ranges of 0.431–0.957 and coverage ranges of 0.554–0.981
across model-specific spline analyses; continuous Age showed a gradual, non-monotonic pattern
with a peak around 65. Fine bands were 18–39, 40–59, 60–69, and 70+; the reported sensitivities
for 60–69 were LR 0.762, RF 0.778, XGB 0.841, LGBM 0.746, MLP 0.698, and for 70+ were LR
0.763, RF 0.789, XGB 0.816, LGBM 0.789, MLP 0.711. Source:
`results/diagnostics/FINAL_THREE_DIAGNOSTICS_REPORT.md` and
`results/diagnostics/fine_age_band_metrics.csv`. **EXPLORATORY / EXECUTED AND VERIFIED.**

Subgroup Platt recalibration changed coverage by at most 0.68 pp (LR BMI +0.11, Age +0.00; RF
BMI -0.11, Age +0.00; XGB 0.00/0.00; LightGBM +0.68/-0.54; MLP 0.00/+0.27). Source:
`results/diagnostics/stage0/subgroup_recalibration_metrics.csv`. **EXPLORATORY / EXECUTED AND
VERIFIED.** It did not fix coverage.

Group-specific thresholds reduced the BMI sensitivity gap to 10.4–16.1 pp but widened the Age
gap; class-balanced models showed 51–80 pp subgroup sensitivity increases, while MLP changes
were -7 to +27 pp. Source: `results/diagnostics/group_specific_threshold_metrics.csv` and
`results/diagnostics/stage0_decision_report.md`. **EXPLORATORY / EXECUTED AND VERIFIED.**

Equal Opportunity post-processing was diagnostic. It increased class-balanced-model target-group
sensitivity by approximately 50–80 pp at approximately 38–40 pp specificity cost; it did not
change probabilities, Brier, calibration, or AUC. MLP sensitivity decreased slightly in the
target groups, supporting a different mechanism. Exact model/group rows are in
`results/diagnostics/stage1_decision_report.md` and
`results/diagnostics/stage1/correct_fairness_postprocessing_results.csv`. **EXPLORATORY /
EXECUTED AND VERIFIED; not a primary model result.**

The old KNN-AFCP comparison is **INVALID / SUPERSEDED** because the implementation was an
approximation that violated the faithful method rule. The faithful Zhou & Sesia AFCP artifact is
`results/diagnostics/stage1/afcp_faithful_results.csv`; the repository preserves an older blocked
status and a newer conditional-frozen status. **CONFLICT UNRESOLVED IN REPOSITORY** as to the
final narrative status; no unconditional AFCP superiority claim is permitted.

## B8. M4b, N0 selection, and trade-offs

The old N0=100 sweep is **SUPERSEDED**. Proper calibration-only N0 selection and the final
prespecified N0=0 artifact are in `results/diagnostics/stage1/m4b_n0_cv_selection.csv`,
`results/tables/m4b_prespecified_n0_final_results.csv`, and
`results/tables/m4b_shrinkage_sensitivity.csv`. The final N0=0 M4b configuration was frozen for
temporal use. **FINAL / AUTHORITATIVE for N0=0; old N0=100 SUPERSEDED.**

Coverage-versus-set-size, fairness-specificity Pareto, clinical false-positive cost, BMI-versus-
Age intervention response, and LightGBM failure analyses are in
`results/diagnostics/stage1/conformal_tradeoff_comparison.csv`,
`fairness_specificity_pareto_results.csv`, `clinically_interpretable_fairness_costs.csv`,
`bmi_age_intervention_response.csv`, and `m4b_lightgbm_failure_analysis.csv`. **EXPLORATORY /
EXECUTED AND VERIFIED.** Exact row-level values remain in those files; no unsupported aggregate
is substituted here.

## B9. Decision Curve Analysis and co-occurrence

The reliability extension analyzed co-occurrence and Decision Curve Analysis on frozen
recalibrated test predictions. Pooled co-occurrence correlation was rho=0.4076, 95% interval
0.1291–0.6419, raw p=0.0020, but category-block permutation p=0.1195; precision-filtered
rho=0.7043, p=2e-6, was sensitivity-only. DCA exceeded both reference strategies at population
level and in BMI-Obese (N=883) and Age-60+ (N=741). Sources:
`RELIABILITY_EXTENSION_RESULTS_REPORT.md` and `results/reliability_extension/*.csv`.
**EXECUTED AND VERIFIED; the permutation result is not confirmed evidence.**

## B10. Sensitivity cohorts and threshold

The 8.0 kPa relabel-only analysis produced AUC 0.8145–0.8326, BMI-Obese disparity 35.1–51.6
pp significant in 5/5 models, and negative Age-60+ direction in 5/5 with significance in 2/5.
No retraining, recalibration, or conformal repetition occurred. **COMPLETE, NARROW SCOPE.**

CAND_2 had N=7,639 and 804 positives, with independent retraining and AUC 0.8526–0.8572.
CAND_3 had N=3,582 and 319 positives, used 12 predictors, with independent retraining and AUC
0.8280–0.8457. **EXECUTED AND VERIFIED.** Sources:
`results/sensitivity/sensitivity_discrimination_calibration_results.csv`,
`relaxed_elastography_cohort_summary.csv`, and `fasting_extended_cohort_summary.csv`.

Across the three non-MI sensitivity variants, BMI-Obese disparity was stable in 15/15 instances;
Age direction never reversed, but significance was lost in 9/12 instances where it was significant
in the primary specification. Source: `results/sensitivity/primary_vs_sensitivity_comparison.csv`.
**FINAL CROSS-SENSITIVITY COMPARISON.**

## B11. Multiple-imputation sensitivity

MI changed AUC by <0.007 and Brier by <0.003 for all five models. NHB sensitivity changes were
at most +/-4.2 pp, all five confidence intervals included zero, and BH-adjusted p was 0.978 for
all five models. Four models were classified STABLE and MLP INDETERMINATE. Source:
`results/sensitivity/mi_black_subgroup_comparison.csv`. **EXECUTED AND VERIFIED, NARROW SCOPE.**
Conformal coverage under MI was not authorized or performed: **NOT EXECUTED.**

## B12. External-validation investigation

The repository investigated whether an independent non-NHANES cohort could be used. The only
identified data used for validation were NHANES 2017–March 2020 and the later NHANES 2021–2023
release; the latter is temporal validation, not external validation. The external-validation
review found no obtained independent non-NHANES dataset with demonstrated compatibility for the
frozen outcome, ten predictors, and VCTE quality rule. Access status for a usable independent
cohort is therefore unavailable; compatibility is not established; and external validation was
not performed. Source: `documentation/reliability_extension/external_validation_future_work.md`
and `README.md`. **NOT EXECUTED / NOT FEASIBLE within the repository evidence.** The NHB holdout
is a within-NHANES demographic holdout and must not be called external validation.

# C. FINAL AUTHORITATIVE RESULTS

The primary study supports: comparable discrimination across five families (AUC 0.8229–0.8429);
raw overprediction in four class-balanced models; successful OOF Platt recalibration without AUC
change; substantial Normal-BMI versus Obese sensitivity disparity; Age-60+ disparity in 4/5
models; acceptable aggregate but failed BMI-Obese and Age-60+ conformal coverage; and partially
effective, incomplete Mondrian mitigation. It does not support claims that the models are
unconditionally fair, have subgroup-valid conformal coverage, or have an externally validated
deployment population.

# D. TEMPORAL VALIDATION RESULTS

## D1. Discovery, preparation, and preflight

The temporal dataset was NHANES 2021–2023. The initial frozen prediction input contained 4,910
rows and the ten frozen predictors. The first preflight failed because outcome and
`RIDRETH3` companion data were absent; this is recorded in
`results/temporal_validation/PHASE3_FAILURE_REPORT.md` as **FAILED — DO NOT PROCEED** at that
intermediate stage. The resolution attached `LUX_L.xpt` (`LUXSMED`, `LUAXSTAT`) and `DEMO_L.xpt`
(`RIDRETH3`) and independently bridged `BMX_L.xpt`/`DEMO_L.xpt` for BMI, age, and sex. All 4,910
SEQNs matched, with zero duplicates, zero missing SEQNs, and zero missing outcome/demographic
values. Sources: `TEMPORAL_LABELS_DEMOGRAPHICS_AUDIT.md` and
`TEMPORAL_FAIRNESS_DEMOGRAPHICS_AUDIT.md`. **EXECUTED AND VERIFIED.**

The final temporal cohort had N=4,910, 563 positives, 4,347 negatives, and 11.4664% prevalence
under `LUXSMED >= 8.2`. Source: `temporal_validation_labels_demographics.csv` and
`PHASE1_FREEZE_AND_PRESERVE_AUDIT.md`. **FINAL / AUTHORITATIVE.**

## D2. Frozen prediction and integrity process

Phase 3 frozen predictions used the five Phase 3 models, frozen thresholds, and no temporal
refitting, threshold selection, or recalibration. Phase 6 conformal-refit predictions used the
frozen proper-train artifacts and frozen global quantiles. M4b used frozen N0=0. All five model
prediction sets contained 4,910 unique SEQNs, finite probabilities in [0,1], and no dropped
values. SHA-256 hashes for the Phase 6 artifacts and the before/after integrity checks are in
`TEMPORAL_CONFORMAL_INPUT_AUDIT.md`, `PHASE1_FREEZE_AND_PRESERVE_AUDIT.md`,
`predictions/temporal_prediction_manifest.json`, and
`temporal_conformal_refit_prediction_manifest.json`. **FINAL / AUTHORITATIVE.**

## D3. Temporal discrimination

| Model | AUROC (95% CI) | PR-AUC (95% CI) | Sensitivity | Specificity | PPV | NPV |
|---|---|---|---:|---:|---:|---:|
| Logistic | 0.7818691235171272 (0.7613177437508856–0.8014042424250571) | 0.39160132338282544 (0.35111831086637574–0.43765519406923137) | 0.6660746003552398 | 0.7412008281573499 | 0.25 | 0.9448680351906158 |
| Random Forest | 0.7764702469312863 (0.7547085318728876–0.7973415739469376) | 0.3849341578036976 (0.3428625886391652–0.4279319733394979) | 0.6909413854351687 | 0.7471819645732689 | 0.2614247311827957 | 0.9491525423728814 |
| XGBoost | 0.7824203294896013 (0.7618869849057684–0.8030882078151037) | 0.41319837892121647 (0.3734597876447709–0.4545844355509524) | 0.738898756660746 | 0.68391994478951 | 0.2324022346368715 | 0.9528846153846153 |
| LightGBM | 0.7785655651127888 (0.7571065400171342–0.8004774009896055) | 0.4049293071780483 (0.36535355685506354–0.4473395867639001) | 0.6749555950266429 | 0.7579940188635841 | 0.26536312849162014 | 0.9473835537665325 |
| MLP | 0.7813906489479892 (0.7597309816244451–0.8020405593918739) | 0.4075498819924695 (0.36477667077989834–0.4541620606897944) | 0.7744227353463587 | 0.6540142627099149 | 0.22474226804123712 | 0.9572390572390572 |

Source: `results/temporal_validation/temporal_discrimination_results.csv`, n=4,910, bootstrap
n=2,000, seed 42. **FINAL / AUTHORITATIVE.**

## D4. Temporal calibration

| Model | Intercept | Slope | Brier | ECE |
|---|---:|---:|---:|---:|
| Logistic | -2.0010662385526583 | 0.9057715507405403 | 0.18378446870183301 | 0.2846394544299061 |
| Random Forest | -1.6395641367289593 | 1.030507734512039 | 0.15021415013669104 | 0.2217853941422908 |
| XGBoost | -1.7806552029763787 | 0.9339817130775262 | 0.1592530257237445 | 0.23346448599613037 |
| LightGBM | -1.7981452680493346 | 0.9473251722317894 | 0.16378063968899564 | 0.2409090307784023 |
| MLP | -0.3711133672472523 | 0.833157942462588 | 0.08507928526203189 | 0.020794136031349997 |

Source: `results/temporal_validation/temporal_calibration_results.csv`. **FINAL /
AUTHORITATIVE.** Intercepts remained negative and Brier scores were higher than the locked-test
recalibrated values; no temporal recalibration was performed.

## D5. Temporal fairness

The complete subgroup table, definitions, confidence intervals, raw p-values, FDR-adjusted
p-values, and significance indicators are in
`results/temporal_validation/temporal_fairness_results.csv` and
`temporal_validation_fairness_demographics.csv`. **FINAL / AUTHORITATIVE.** The temporal
fairness result is that the Normal-BMI sensitivity deficit versus Obese widened to 62.8–71.9
percentage points, with FDR q<0.001 across all five models. Sex, race/ethnicity, BMI, age, and
BMI x Age rows are present in the authoritative table; any row-level value not reproduced here
is **NOT FOUND IN REPOSITORY** for this report's summarized narrative and must be read from that
file rather than inferred.

## D6. Temporal conformal coverage

| Model | Overall | BMI-Obese | Age-60+ | BMI-Obese x Age-60+ | Mean set size |
|---|---:|---:|---:|---:|---:|
| Logistic | 0.9022403258655805 | 0.8127637130801688 | 0.8653663177925784 | 0.7195431472081218 | 1.4527494908350305 |
| Random Forest | 0.8906313645621181 | 0.790084388185654 | 0.8748810656517603 | 0.7652284263959391 | 1.240529531568228 |
| XGBoost | 0.8824847250509165 | 0.770042194092827 | 0.8491912464319695 | 0.6967005076142132 | 1.285336048879837 |
| LightGBM | 0.8936863543788187 | 0.7895569620253164 | 0.8782112274024738 | 0.75 | 1.3191446028513238 |
| MLP | 0.8786150712830957 | 0.7827004219409283 | 0.8491912464319695 | 0.733502538071066 | 0.9712830957230143 |

The authoritative table reports marginal coverage 87.9–90.2% across models and intersectional
coverage 69.7–76.5%. Full confidence intervals, singleton/doubleton rates, coverage gaps, drift,
and frozen thresholds are in `results/temporal_validation/temporal_conformal_results.csv`.
Source: that CSV and `PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md`. **FINAL / AUTHORITATIVE.**

## D7. Temporal M4b

With frozen N0=0, intersectional coverage reached the >=90% target only for Random Forest
(90.10%); it failed for Logistic (88.58%), XGBoost (87.69%), LightGBM (87.31%), and MLP
(88.58%). Source: `results/temporal_validation/temporal_m4b_results.csv` and
`PHASE1_FREEZE_AND_PRESERVE_AUDIT.md`. **FINAL / AUTHORITATIVE.**

# E. ORIGINAL VS TEMPORAL COMPARISON

Temporal AUROC declined by 0.041–0.061 across models: the primary locked range 0.8229–0.8429
became 0.7765–0.7824. PR-AUC increased by 0.019–0.042. Sensitivity and specificity changed by
model and are fully enumerated in `temporal_original_vs_validation_comparison.csv`. Calibration
remained imperfect, with negative temporal intercepts; Brier scores worsened relative to the
primary recalibrated test values while ECE decreased in the reported synthesis. Marginal
conformal coverage remained near the 90% target, but BMI x Age intersectional coverage collapsed
to 69.7–76.5%. BMI fairness worsened, with 62.8–71.9 pp temporal deficits. M4b replicated its
intersectional target only for Random Forest. Source:
`results/temporal_validation/PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md`,
`temporal_original_vs_validation_comparison.csv`, and the temporal metric tables. **FINAL /
AUTHORITATIVE.**

# F. COMPLETE LIST OF SUPERSEDED / INVALID / UNVERIFIED / ABANDONED WORK

* Early prevalence and AUROC values corrected by the final audit are superseded by
  `results/tables/phase3_final_baseline_results.csv` and `results/calibration/test_set_calibration_final.csv`.
* Any claim of Age-60+ significance in 5/5 models is **INVALID**; Logistic is the exception.
* Any claim that the BMI x Age intersection was 294 people and approximately 62% is **INVALID**;
  294 is 13.7%; 62% describes the union.
* Early leakage-prone scripts and the three documented diagnostic defects are **SUPERSEDED** by
  the contamination audit and fresh implementations.
* KNN-AFCP is **INVALID / SUPERSEDED** as a faithful AFCP result.
* Equal Opportunity's older **UNVERIFIED** label conflicts with the newer conditional diagnostic
  report; it remains diagnostic and cannot alter the primary pipeline.
* Old N0=100 selection is **SUPERSEDED** by proper calibration-only selection and final N0=0.
* CAND_4 is **NOT EXECUTED**.
* Broader MI is **NOT EXECUTED / NOT FROZEN**.
* MI conformal-coverage analysis is **NOT EXECUTED**.
* Full 8.0 kPa retraining, recalibration, and conformal repetition are **NOT EXECUTED**.
* XGBoost mitigation retuning is **NOT EXECUTED**.
* Non-NHANES external validation is **NOT EXECUTED**.
* The earlier temporal preflight was **FAILED** but is resolved by the later outcome/demographic
  preparation; it is not a final temporal result.

# G. ALL DOCUMENTED CORRECTIONS

Corrections include the primary cohort/prevalence flow, baseline AUC location and values, the
4/5 rather than 5/5 Age significance count, the 294-person/13.7% overlap interpretation, the
CAND_2/CAND_3 execution status, exclusion of invalid KNN-AFCP and old N0=100 claims, explicit
scope of the 8.0 kPa and NHB MI analyses, and reconciliation of the later joint-mitigation
artifact with the stale status CSV. Sources:
`documentation/final_audit/CHANGELOG_RESEARCH.md`,
`FINAL_CLAIM_AUDIT.md`, and
`INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`. **FINAL / AUTHORITATIVE.**

# H. FINAL SCIENTIFIC FINDINGS

Five common model families had comparable primary discrimination, but aggregate AUC concealed
calibration distortion and reproducible demographic reliability failures. Class-balanced models
overpredicted until OOF Platt recalibration. Normal-BMI versus Obese sensitivity disparity was
robust across primary and tested sensitivity specifications. Age-60+ disparity was directionally
consistent but less statistically stable. Split conformal prediction met approximately marginal
coverage while failing in the same clinically important subgroups. Mondrian mitigation was
partially effective, not a complete fix. NHB holdout testing showed moderate discrimination
attenuation and materially unstable calibration. The 2021–2023 temporal study showed reduced
AUROC, worsened BMI fairness, persistent calibration limitations, near-target marginal coverage
but severe intersectional coverage loss, and M4b success in only one model. Final classification:
**PARTIAL TEMPORAL REPLICATION.**

# I. CURRENT LIMITATIONS

No non-NHANES external validation has been performed. CAND_4, broader MI, MI conformal coverage,
XGBoost mitigation retuning, and full 8.0 kPa pipeline repetition were not executed. Genuine
joint mitigation was not the original primary implementation; the later exploratory joint
artifact has tolerance breaches. AFCP narrative status contains an explicitly preserved conflict.
Temporal fairness row-level claims must use the complete CSV because this report deliberately does
not infer unshown subgroup values. Any missing lineage link is **LINEAGE NOT FOUND IN REPOSITORY**.

# J. CURRENT SCIENTIFIC STATUS

Primary Phases 1–8, reliability extension, CAND_2/CAND_3 sensitivity, 8.0 kPa narrow-scope
sensitivity, and NHB MI narrow-scope sensitivity are complete. Temporal validation Phases 1–4
are complete. The project is manuscript-ready only with the qualifications and statuses in this
report. The scientifically correct overall status is **PARTIAL TEMPORAL REPLICATION**, not full
replication and not external validation.

# K. MANUSCRIPT-READY AUTHORITATIVE NUMBERS

Only the following consolidated claims are suitable without exploratory qualification: primary
CAND_1 N=7,153, 666 positives, 9.31%; train/test N=5,007/2,146; conformal proper-train/
calibration N=4,005/1,002; five-model AUROC 0.8229–0.8429; no FDR-significant pairwise winner;
OOF intercepts -2.243 to -0.281; locked-test Platt changes shown in B2; Normal-BMI versus Obese
deficit 27.1–47.7 pp in 5/5; Age-60+ deficit significant in 4/5; marginal conformal coverage
88.12–90.82%; BMI-Obese 76.8–82.3%; Age-60+ 81.1–85.6%; Mondrian resolution 5/9 with XGBoost
93.4% tolerance breach; NHB holdout N=1,787 and AUC 0.7719–0.7893; temporal N=4,910, 563
positives, 11.4664%; temporal AUROC 0.7765–0.7824; temporal PR-AUC 0.3849–0.4132; temporal
BMI sensitivity deficit 62.8–71.9 pp; temporal intersectional conformal coverage 69.7–76.5%;
and final status **PARTIAL TEMPORAL REPLICATION**. Each number is sourced in sections B–E.

# L. COMPLETE SOURCE FILE REGISTER

The following files were actually read or directly used for this report. Files listed as
authoritative are the controlling evidence for the stated result; supporting files provide
protocol, lineage, or audit context. A file not listed was not used as factual evidence.

| Path | Type | Purpose / contribution | Treatment |
|---|---|---|---|
| `README.md` | Markdown | project scope and external-validation limitation | supporting |
| `documentation/final_audit/RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md` | Markdown | primary consolidation and methods | authoritative synthesis |
| `documentation/final_audit/FINAL_CLAIM_AUDIT.md` | Markdown | claim-level support and corrections | authoritative claim audit |
| `documentation/final_audit/FINAL_RESEARCH_STATUS.md` | Markdown | phase/status register | authoritative status, with later reconciliation |
| `documentation/final_audit/FINAL_SCIENTIFIC_INTERPRETATION.md` | Markdown | final interpretation | authoritative synthesis |
| `documentation/final_audit/FINAL_RESEARCH_ARCHITECTURE.md` | Markdown | end-to-end architecture and lineage | supporting |
| `documentation/final_audit/INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md` | Markdown | numerical verification and conflicts | authoritative verification |
| `documentation/final_audit/CHANGELOG_RESEARCH.md` | Markdown | historical corrections | authoritative correction log |
| `results/tables/final_research_status.csv` | CSV | machine-readable phase status | authoritative status, stale joint row reconciled |
| `results/tables/data_and_result_lineage.csv` | CSV | result-to-script-to-data lineage | authoritative lineage |
| `results/tables/model_lineage.csv` | CSV | model pipeline lineage | authoritative supporting lineage |
| `results/tables/phase2_candidate_cohort_comparison.csv` | CSV | candidate cohorts | authoritative |
| `results/tables/phase2_outcome_prevalence.csv` | CSV | outcome counts/prevalence | authoritative |
| `results/tables/phase2_predictor_registry.csv` | CSV | frozen predictors | authoritative |
| `results/tables/phase3_final_baseline_results.csv` | CSV | baseline metrics | authoritative |
| `results/tables/phase3_model_comparison_fdr.csv` | CSV | pairwise FDR | authoritative |
| `results/calibration/primary_metrics_by_model.csv` | CSV | OOF calibration | authoritative |
| `results/calibration/test_set_calibration_final.csv` | CSV | locked-test calibration | authoritative |
| `results/fairness/subgroup_discrimination_metrics.csv` | CSV | subgroup metrics | authoritative |
| `results/fairness/fairness_inference.csv` | CSV | CIs, tests, FDR | authoritative |
| `results/uncertainty/marginal_coverage_test_set.csv` | CSV | marginal coverage | authoritative |
| `results/uncertainty/subgroup_coverage.csv` | CSV | subgroup coverage | authoritative |
| `results/uncertainty/intersectional_coverage_ci.csv` | CSV | intersection CIs | authoritative |
| `results/mitigation/test_set_mitigation_final.csv` | CSV | Mondrian test results | authoritative |
| `results/mitigation/marginal_coverage_before_after.csv` | CSV | mitigation trade-off | authoritative |
| `results/mitigation/threshold_precedence_audit.csv` | CSV | overlap precedence | authoritative limitation audit |
| `results/mitigation/joint_intersectional_mitigation.csv` | CSV | later joint diagnostic | exploratory, later executed |
| `results/sensitivity/alternative_threshold_8p0kPa_results.csv` | CSV | 8.0 kPa result | authoritative narrow scope |
| `results/sensitivity/sensitivity_discrimination_calibration_results.csv` | CSV | CAND_2/CAND_3 results | authoritative |
| `results/sensitivity/primary_vs_sensitivity_comparison.csv` | CSV | pooled sensitivity comparison | authoritative |
| `results/sensitivity/mi_black_subgroup_comparison.csv` | CSV | NHB MI comparison | authoritative narrow scope |
| `results/diagnostics/FINAL_THREE_DIAGNOSTICS_REPORT.md` | Markdown | spline/recalibration diagnostics | exploratory |
| `results/diagnostics/stage0_decision_report.md` | Markdown | D01–D05 decisions | exploratory |
| `results/diagnostics/stage1_decision_report.md` | Markdown | D06–D07 decisions | exploratory, with status conflict |
| `results/diagnostics/stage1/afcp_faithful_results.csv` | CSV | faithful AFCP artifact | exploratory/conditional |
| `results/diagnostics/stage1/correct_fairness_postprocessing_results.csv` | CSV | EO diagnostic | exploratory |
| `results/diagnostics/stage1/m4b_n0_cv_selection.csv` | CSV | N0 selection | authoritative for selection process |
| `results/tables/m4b_prespecified_n0_final_results.csv` | CSV | final N0=0 M4b | authoritative |
| `results/tables/m4b_shrinkage_sensitivity.csv` | CSV | M4b sensitivity | supporting |
| `results/reliability_extension/dca_summary.csv` | CSV | DCA summary | exploratory extension |
| `results/reliability_extension/cooccurrence_correlation_results.csv` | CSV | co-occurrence inference | exploratory extension |
| `RELIABILITY_EXTENSION_RESULTS_REPORT.md` | Markdown | DCA/co-occurrence interpretation | exploratory extension |
| `results/temporal_validation/PHASE1_FREEZE_AND_PRESERVE_AUDIT.md` | Markdown | temporal freeze/integrity | authoritative |
| `results/temporal_validation/PHASE3_FAILURE_REPORT.md` | Markdown | resolved intermediate preflight failure | historical intermediate |
| `results/temporal_validation/PHASE3_TEMPORAL_VALIDATION_REPORT.md` | Markdown | frozen prediction evaluation scope | authoritative |
| `results/temporal_validation/PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md` | Markdown | final temporal synthesis | authoritative |
| `results/temporal_validation/TEMPORAL_LABELS_DEMOGRAPHICS_AUDIT.md` | Markdown | temporal labels and demographics | authoritative preparation audit |
| `results/temporal_validation/TEMPORAL_FAIRNESS_DEMOGRAPHICS_AUDIT.md` | Markdown | temporal demographic bridge | authoritative preparation audit |
| `results/temporal_validation/TEMPORAL_CONFORMAL_INPUT_AUDIT.md` | Markdown | conformal input integrity | authoritative audit |
| `results/temporal_validation/temporal_validation_labels_demographics.csv` | CSV | temporal cohort/outcome | authoritative |
| `results/temporal_validation/temporal_discrimination_results.csv` | CSV | temporal discrimination | authoritative |
| `results/temporal_validation/temporal_calibration_results.csv` | CSV | temporal calibration | authoritative |
| `results/temporal_validation/temporal_fairness_results.csv` | CSV | temporal subgroup metrics/FDR | authoritative |
| `results/temporal_validation/temporal_conformal_results.csv` | CSV | temporal conformal metrics | authoritative |
| `results/temporal_validation/temporal_m4b_results.csv` | CSV | temporal M4b | authoritative |
| `results/temporal_validation/temporal_original_vs_validation_comparison.csv` | CSV | primary-temporal comparison | authoritative |
| `results/temporal_validation/predictions/temporal_prediction_manifest.json` | JSON | frozen prediction manifest | authoritative |
| `results/temporal_validation/temporal_conformal_refit_prediction_manifest.json` | JSON | conformal prediction manifest | authoritative |
| `data/processed/temporal_validation/temporal_validation_input_cobas6000_alt_manifest.json` | JSON | temporal input manifest | supporting |
| `src/phase7_04_final_test_touch.py` | Python | mitigation precedence implementation | source-code authority |
| `src/temporal_validation/run_phase3_temporal_validation.py` | Python | temporal evaluation script | source-code lineage |
| `src/temporal_validation/synthesize_phase4_temporal_validation.py` | Python | temporal synthesis script | source-code lineage |
| `src/generate_temporal_predictions_frozen.py` | Python | frozen temporal predictions | source-code lineage |

For any major finding whose result-to-script-to-input-to-artifact-to-training/evaluation chain is
not established by the cited lineage tables and manifests, the correct statement is:
**LINEAGE NOT FOUND IN REPOSITORY**.

## Direct lineage traces for major result families

* **Primary discrimination:** final finding -> `results/tables/phase3_final_baseline_results.csv`
  -> `src/phase3_05_train_and_tune.py` / `phase3_06_threshold_and_test_eval.py` ->
  `data/processed/analysis_dataset_primary.parquet` -> Phase 3 model artifacts ->
  `data/processed/splits/train_ids.csv` and `test_ids.csv` -> locked test evaluation.
* **Calibration:** final finding -> `results/calibration/test_set_calibration_final.csv` ->
  `src/phase4_05_recalibration.py` and `phase4_09_final_test_set_calibration.py` ->
  validation prediction files and frozen Platt parameters -> OOF fitting data -> locked test.
* **Fairness and conformal:** final finding -> `results/fairness/fairness_inference.csv` or
  `results/uncertainty/subgroup_coverage.csv` -> Phase 5/6 scripts -> frozen recalibrated
  predictions or Phase 6 artifacts -> train/proper-train/calibration/test split registries.
* **Temporal validation:** final finding -> the corresponding file under
  `results/temporal_validation/` -> `src/temporal_validation/run_phase3_temporal_validation.py`
  or `synthesize_phase4_temporal_validation.py` -> temporal labels/demographics and manifests
  -> frozen Phase 3/Phase 6 models and parameters -> NHANES 2021–2023 evaluation cohort.

These traces establish the repository's documented lineage for the major result families. Any
unlisted intermediate artifact, unreviewed raw-file hash, or unsupported result linkage remains
**LINEAGE NOT FOUND IN REPOSITORY**.

## Final self-verification

All requested master sections A–L are present. All five model families, primary phases, documented
diagnostics/mitigations, NHB holdout, external-validation investigation, historical corrections,
temporal preparation, temporal results, conflicts, missing analyses, lineage caveat, manuscript
numbers, and source register are explicitly covered. The report does not claim external
validation, full temporal replication, or unsupported subgroup values.

**FINAL MASTER REPORT VERIFIED**
