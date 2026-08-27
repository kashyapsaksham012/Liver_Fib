# FINAL LIMITATIONS REGISTER

Read-only audit, 2026-08-27. Severity: **HIGH** (affects a primary conclusion / must be
prominent), **MODERATE** (qualifies a finding), **LOW** (disclosure completeness).
"Affects interpretation?" = whether omitting it would let a reader over-read the results.

---

## A. Statistical

| ID | Limitation | Evidence | Severity | Affects interpretation? | Manuscript wording |
|---|---|---|---|---|---|
| A1 | Age-60+ disparity significance is specification-sensitive (4/5 primary; lost in 9/12 sensitivity-cohort instances) | `fairness_inference.csv`, `primary_vs_sensitivity_comparison.csv` | MODERATE | Yes | "The older-age sensitivity deficit was directionally consistent but statistically significant in four of five models and not robust to alternative specifications." |
| A2 | No formal comparative inference (p-values / CIs) for corrected Phase 3 / Phase 4 mitigation candidate differences | `PHASE3_CORRECTED_MITIGATION_REPORT.md`, `PHASE4_CORRECTED_FINAL_AUDIT_REPORT.md` | MODERATE | Yes | "Mitigation candidates were compared descriptively against a pre-specified gate; no candidate-vs-candidate significance test was performed." |
| A3 | Co-occurrence of the fairness and coverage flags is not a confirmed association (permutation p=0.1195) | `RELIABILITY_EXTENSION_RESULTS_REPORT.md` | LOW | Yes (if cited) | "The apparent co-occurrence of the two subgroup failures was not statistically confirmed under a category-block permutation test." |
| A4 | BH-FDR ceiling: NHB MI adjusted p=0.978 for all 5 models is a correction artifact, not evidence of no effect | `mi_black_subgroup_comparison.csv` | LOW | Yes | "The adjusted p-values reflect the correction ceiling on a five-member test family and should not be read as evidence of equivalence." |
| A5 | No statistical test of 8.0 vs 8.2 kPa equivalence | `PHASE6_8KPA_ROBUSTNESS_REPORT.md` | LOW | Yes | "The 8.0-kPa analysis is a sensitivity check, not an equivalence test." |
| A6 | The subgroup fairness audit uses the full-train fit; the conformal analysis uses the proper-train-refit fit (the conformal architecture needs a disjoint calibration set). Amendment #18 (Fix 1) confirms the body-mass sensitivity gap is present in both fits (−27 to −42 pp, 5/5; STRENGTHENING), so the two findings concern the same subgroup failure. | `documentation/prepublication_fixes/FIX1_MODEL_FIT_ALIGNMENT.md`; `results/prepublication_fixes/fix1_*.csv` | LOW | Yes | "The fairness audit and the conformal analysis use two related fits of each model; a sensitivity analysis confirmed the body-mass sensitivity deficit in both, so they describe the same subgroup failure." |

## B. Sample size / power

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| B1 | Only 666 positives (9.31%); modest PR-AUC (~0.35) | `phase2_outcome_prevalence.csv`, `phase3_final_baseline_results.csv` | MODERATE | Yes | "Low outcome prevalence limits positive predictive value and the precision of subgroup estimates." |
| B2 | Normal-BMI test cell has 22 positives; Underweight has 1 (uninterpretable, excluded) | `phase1_bmi_reproduction.csv`, `subgroup_coverage.csv` | MODERATE | Yes | "Subgroup sensitivity estimates for normal-weight participants rest on 22 test-set cases; the underweight category (one positive) is not interpretable." |
| B3 | BMI-Obese ∩ Age-60+ intersection cell N=294 (35 positives); joint calibration cell N=138 (30 positives) | `intersectional_coverage_ci.csv`, `PHASE7_MITIGATION_CLEANUP_REPORT.md` | MODERATE | Yes | "Intersectional coverage estimates and any joint calibration rest on a few hundred participants and ~30 events." |
| B4 | CAND_3 (fasting-extended) N=3,582 halves the sample | `fasting_extended_cohort_summary.csv` | LOW | No | "The fasting-extended sensitivity cohort is roughly half the primary size." |
| B5 | Cirrhosis secondary outcome (~53 test positives) would be low-powered for subgroup fairness | `OPTIONAL_ANALYSIS_DECISION_AUDIT.md` | LOW | No | (only relevant if secondary outcomes are run) |

## C. Calibration

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| C1 | Raw probabilities from four of five models require post-hoc OOF Platt recalibration; without it they are unusable | `primary_metrics_by_model.csv`, `test_set_calibration_final.csv` | MODERATE | Yes | "Class-balanced models are not usable without out-of-fold recalibration; this step is mandatory, not optional." |
| C2 | Aggregate calibration adequacy does not extend to subgroups | `PHASE2_DIAGNOSTIC_REPORT.md`, `subgroup_recalibration_metrics.csv` | MODERATE | Yes | "Recalibration restored aggregate but not subgroup-level calibration behaviour." |
| C4 | Isotonic calibration was not adopted (466 OOF positives); Platt is a 2-parameter approximation | `amendment_8_provenance.md` | LOW | No | "Platt scaling was chosen over isotonic regression given the limited number of positive cases." |

## D. Fairness

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| D1 | **No acceptable mitigation for the BMI-Obese / Normal-BMI reliability–fairness problem.** Includes conformal selective deferral (Amendment #17): no pre-registered candidate met the gate; the under-coverage is confidently-scored wrong singletons, not flagged-uncertain cases. Group-conditional recalibration restores subgroup coverage only by over-covering the well-served subgroups. A training-time intervention was not attempted (frozen scope). | `PHASE3_CORRECTED_MITIGATION_REPORT.md`, `PHASE4_CORRECTED_FINAL_AUDIT_REPORT.md`, `phase7_mitigation_cleanup/`, `documentation/selective_deferral_mitigation/*` | HIGH | Yes | "No calibration-, threshold-, conformal-, or selective-deferral-based intervention tested produced an acceptable multi-metric fix for the BMI-related reliability failure; the residual under-coverage is a within-subgroup score-ordering problem that points to a training-time remedy." |
| D2 | BMI disparity mechanism is empirical/associational, not causal | `PHASE2_DIAGNOSTIC_REPORT.md` | MODERATE | Yes | "The mechanism is a score-distribution difference with a threshold component; a causal interpretation is not supported." |
| D3 | Fairness stratification uses NHANES `RIDRETH3` categories; race/ethnicity excluded from model input by design | `phase2_predictor_registry.csv` | LOW | No | "Race/ethnicity was used only for post-hoc stratification, an explicit design choice." |
| D4 | Cohort-level differential missingness (NHB 41.3% of exclusions vs 25.0% retained) is separate from the model-fairness findings and only partially probed (targeted MI) | `missingness_by_group.csv`, `mi_black_subgroup_comparison.csv` | MODERATE | Yes | "Complete-case exclusion disproportionately affected Non-Hispanic Black participants; a targeted imputation analysis addressed this specific concern only." |

## E. Conformal

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| E1 | Only *marginal* coverage is guaranteed; subgroup/intersectional coverage fails and is not a conditional-validity guarantee | `subgroup_coverage.csv`, `intersectional_coverage_ci.csv` | HIGH | Yes | "Split conformal provides a marginal coverage guarantee only; subgroup coverage was empirically deficient." |
| E2 | ~~Subgroup conformal coverage measured on CAND_1 only~~ **REPLICATED 2026-08-27 (Amendment #16)** on 8.0 kPa / CAND_2 / CAND_3 | `CONFORMAL_REPLICATION_SENSITIVITY_COHORTS_RESULTS_REPORT.md` | LOW (downgraded) | Yes | "The subgroup coverage failure was demonstrated on the primary cohort and replicated on two independently constructed sensitivity cohorts and an alternative threshold: BMI-Obese under-coverage was robust throughout; the older-age component was direction-robust with power-sensitive significance." |
| E3 | Mondrian mitigation leaves 4/9 targets unresolved and breaches the XGBoost marginal tolerance (+5.27 pp); an Amendment #17 re-run reaches 5/5 subgroup targets with zero deferral but over-covers marginally (retained marginal coverage 0.94–0.95) — restoring target marginal coverage would require *levelling down* the well-served subgroups | `marginal_coverage_before_after.csv`, `results/selective_deferral/phase3_candidate_metrics.csv` | MODERATE | Yes | "Group-wise mitigation was partial: it either breached the marginal-coverage tolerance for one model or restored subgroup coverage only by over-covering the better-served subgroups." |
| E4 | Intersectional overlap uses sequential (Age-over-BMI) precedence, not joint mitigation | `threshold_precedence_audit.csv` | MODERATE | Yes | "In the overlap population, single-attribute rules were applied sequentially rather than jointly." |
| E6 | AFCP final narrative status unresolved | `stage1_decision_report.md` | LOW | No | (omit AFCP or label it exploratory) |

## F. Multiple imputation

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| F1 | MI scope is the Non-Hispanic Black selection question only; complete-case is the pre-registered primary strategy | `missing_data_protocol.md`, `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` | MODERATE | Yes | "Multiple imputation was applied only to the differential Non-Hispanic Black exclusion; the primary analysis is complete-case." |
| F2 | Phase 5 MI conformal tables have no executable lineage | `phase5_mi_lineage.json`, `PHASE5_MI_CONFORMAL_REPORT.md` | MODERATE | Yes (if cited) | "The multiple-imputation conformal analysis is descriptive; its pipeline could not be fully reconstructed from committed artifacts." |
| F3 | No Rubin pooling / equivalence testing for MI outputs | `PHASE5_MI_CONFORMAL_REPORT.md` | LOW | Yes | "No pooled inferential estimate is reported for the imputation analyses." |

## G. Threshold sensitivity

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| G1 | Some major findings (Age-60+ significance; some conformal detail) are threshold-sensitive between 8.0 and 8.2 kPa | `PHASE6_8KPA_ROBUSTNESS_REPORT.md`, `phase6_8kpa_vs_82_comparison.csv` | MODERATE | Yes | "An 8.0-kPa cutoff preserved discrimination and the obese-BMI disparity but altered the older-age disparity's significance." |
| G2 | 8.0-kPa deferred-plan analysis is relabel-only (no fresh hyperparameter search / model fit) | `alternative_threshold_8p0kPa_results.csv` (`retrained=False`) | LOW | No | "The pre-registered threshold check relabelled frozen predictions." |

## H. Lineage / reproducibility

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| H1 | Phase 5 MI conformal: `LINEAGE NOT FOUND IN REPOSITORY` | `phase5_mi_lineage.json` | MODERATE | Yes (if cited) | see F2 |
| H2 | Frozen 8.2-kPa protocol commit and model-artifact manifest `NOT FOUND IN REPOSITORY` (BMI-inv Phase 6) | `PHASE6_8KPA_ROBUSTNESS_REPORT.md` | LOW | No | "Some upstream protocol-freeze commits could not be located." |
| H3 | Joint mitigation generating script/manifest/runtime log `NOT FOUND IN REPOSITORY`; stale status-CSV conflict | `PHASE7_MITIGATION_CLEANUP_REPORT.md`, `FINAL_CLAIM_AND_STATUS_REGISTRY.csv` row JOINT | LOW | No (exploratory) | "The joint calibration artifact lacks a committed generating pipeline." |
| H4 | Corrected Phase 4 runtime test-access order only partially proven (no runtime event log); one duplicate output lacks generation provenance | `PHASE4_CORRECTED_FINAL_AUDIT_REPORT.md` | LOW | No | "Static control-flow, not a runtime log, establishes the corrected Phase 4 test-access order." |
| H5 | One manual constants-transcription gap in the dependency graph | `research_pipeline_dependency_graph.md` | LOW | No | — |
| H6 | Two master syntheses disagree on conformal subgroup coverage (conflict C1); raw CSV resolves it | `MASTER_RESEARCH_RESULTS.md` vs `MASTER_END_TO_END_RESEARCH_REPORT.md` | LOW | Yes (for whoever reads the wrong doc) | (cite raw CSV + MASTER_END_TO_END) |
| H7 | Adoption of OOF Youden thresholds recorded as a protocol amendment (post-hoc procedure formalised) | `threshold_selection_audit.md` | LOW | No | "Operating thresholds were derived from out-of-fold predictions and their adoption documented as a protocol amendment." |

## I. Out-of-sample evaluation

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| I1 | No later-cycle (temporal) or independent-cohort evaluation is within the scope of this study; generalizability beyond the NHANES 2017–March 2020 development setting is unestablished. (A NHANES 2021–2023 temporal evaluation was completed and split into a separate manuscript — preserved on the `temporal-validation-standalone` git branch — and is not part of this study's evidence base.) | — | HIGH | Yes | "The models were not evaluated on any later survey cycle or independent population; transportability is unestablished." |

## J. External validity

| ID | Limitation | Evidence | Severity | Affects interpretation? | Wording |
|---|---|---|---|---|---|
| J1 | **No non-NHANES external validation ever performed** | `external_validation_future_work.md`, `README.md` | HIGH | Yes | "The models have not been validated on any independent, non-NHANES population; this is the study's foremost limitation." |
| J2 | Single survey program, single country (US), single pre-pandemic release for the primary analysis | `PHASE2_PROTOCOL_FREEZE.md` | MODERATE | Yes | "All primary analyses use one US survey release." |
| J3 | VCTE (`LUXSMED`) is the reference standard, not liver biopsy; VCTE over-reads stiffness at high BMI, so some obese "positive" labels near 8.2 kPa may be inflated. **Amendment #18 sensitivity analysis:** relabelling at ≥9.7/10/12/13.6 kPa left obese sensitivity + obese conformal coverage stable (Δ≈0.03), BMI-Obese under-coverage persisted/worsened, and a matched-stiffness check showed obese get +0.19–0.33 predicted probability at identical stiffness (p<0.001, 5/5) — evidence *against* a pure measurement artefact — but Normal-BMI has only 7 fibrosis-positive test cases at ≥12 kPa so a residual contribution cannot be formally excluded (verdict **V3**). | `primary_outcome_definition.md`; `documentation/prepublication_fixes/FIX2_VCTE_BIAS_SENSITIVITY.md`; `results/prepublication_fixes/fix2_*.csv` | MODERATE | Yes | "The outcome is elastography-defined significant fibrosis, not histology. VCTE over-reads stiffness at high BMI; a sensitivity analysis at stricter stiffness thresholds and a matched-stiffness comparison argued against measurement bias explaining the body-mass disparity (obese detection and coverage were stable, and obese participants received higher scores at identical stiffness), but the normal-weight side was underpowered and a residual measurement contribution could not be excluded — a histology- or MRE-referenced cohort would be required to resolve it." |
| J4 | Phase 8 NHB holdout is a within-NHANES demographic holdout, not external validation | `PHASE8_SUBGROUP_HOLDOUT_PROTOCOL_FREEZE.md` | MODERATE | Yes | "The demographic holdout is internal to NHANES." |
| J5 | Adult-scoped; adolescents (CAND_4) not analysed | `primary_cohort_decision.md` | LOW | No | "Findings apply to adults." |

---

## Minimum limitations set for the manuscript (must all appear)

D1, E1, E3, E4, I1, J1, J3, J4, A1, B1, B2, C1, F1, F2, G1, plus the general
class-balancing-artifact disclosure (C1) and the underweight-uninterpretable note (B2). E2 is now
a completeness note only (the replication was done — Amendment #16 — and is a strength, not a gap).
