# FINAL END-TO-END RESEARCH AUDIT — MASTER SYNTHESIS

**Repository:** `liver_fibrosis_research` (authoritative working tree:
`/Users/sakshamkashyap/Desktop/Research /liver_fibrosis_research`)
**Audit date:** 2026-08-27
**Mode:** READ-ONLY. No experiment was run, no model was generated, no existing result,
protocol, historical artifact, or master report was modified. External
validation was **not** performed, and no out-of-sample (later-cycle or independent-cohort)
evaluation is within the scope of this study. This document and its companions under
`documentation/final_research_audit/` and `results/final_research_audit/` are the only new files.

> **Scope note:** a NHANES 2021–2023 temporal evaluation was completed and then split into a
> separate manuscript; all temporal code, results, and documents were removed from this repository
> (preserved on the `temporal-validation-standalone` git branch) and are not part of this study.

**Git state at audit:** `HEAD = 4ad991a`. The consolidation layers
`documentation/final_audit/MASTER_END_TO_END_RESEARCH_REPORT.md`,
`documentation/final_research_state/*`, and `results/final_research_state/*` are present in the
working tree as uncommitted work and were treated as the current authoritative consolidation
where they agree with raw artifacts.

---

## 0. Source-of-truth resolution used by this audit

Authority order applied (highest first):

1. Raw frozen result artifacts (`results/**/*.csv`, `*.json`, split ID files, model lineage).
2. `documentation/final_audit/MASTER_END_TO_END_RESEARCH_REPORT.md` and the
   `documentation/final_research_state/` + `results/final_research_state/` registers, **only where
   they agree with (1)**.
3. Phase-level reports and decision logs (`documentation/fairness_bmi_investigation/*`,
   `documentation/**`), protocol freezes, lineage JSON.
4. `documentation/MASTER_RESEARCH_RESULTS.md` — used as historical synthesis; **superseded** on
   the one point where it disagrees with raw artifacts (see §CONFLICTS).
5. Archived / pre-closure / historical exploratory artifacts — only where self-labelled.

Recency alone was never used to assign authority.

### CONFLICTS identified in the repository

| # | Conflict | Sources | Resolution |
|---|---|---|---|
| C1 | **Conformal subgroup under-coverage: which BMI group fails, and the numbers.** `documentation/MASTER_RESEARCH_RESULTS.md` §2 items 26–27 and §3.5 state *Normal-BMI* coverage fails (81.04–82.65%), Age-60+ 84.40–85.80%, marginal 89.00–90.12%. `MASTER_END_TO_END_RESEARCH_REPORT.md` §B4, the `final_research_state` registers, and `results/final_research_state/FINAL_CLAIM_AND_STATUS_REGISTRY.csv` state *BMI-Obese* coverage fails (76.8–82.3%), Age-60+ 81.1–85.6%, marginal 88.12–90.82%. | raw `results/uncertainty/subgroup_coverage.csv`, `results/uncertainty/marginal_coverage_test_set.csv` | **RESOLVED against the raw artifact.** The raw CSVs show BMI-**Obese** is the under-covered group (empirical coverage 0.7678 XGB → 0.8233 logistic; `ci_excludes_target=True`, FDR-significant, all 5 models), while Normal-BMI / Overweight **over-cover** (0.95–0.97). Marginal coverage is 0.8812 (XGB) → 0.9082 (logistic). The `MASTER_END_TO_END` / `final_research_state` values are correct; `MASTER_RESEARCH_RESULTS.md` items 26–27 / §3.5 are **erroneous / SUPERSEDED** for the conformal-coverage claim. Every other `MASTER_RESEARCH_RESULTS.md` figure spot-checked (baseline AUROC, calibration, BMI sensitivity gaps, intersectional coverage 64.97–75.17%) reconciles with raw artifacts and the other master report. |
| C2 | **Joint intersectional mitigation execution status.** `results/tables/final_research_status.csv` (stale) marks joint mitigation `NOT EXECUTED`; `INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md` and `results/mitigation/joint_intersectional_mitigation.csv` document it as executed exploratory work. | as cited | Repository explicitly records this as **CONFLICT UNRESOLVED IN REPOSITORY**, with the dated attestation establishing the later artifact as the superseding execution. The joint artifact is **EXPLORATORY only**, never primary. This audit preserves that disposition. |
| C3 | **Faithful AFCP narrative status.** An older status marks AFCP work blocked; a newer status marks it conditional-frozen exploratory. | `results/diagnostics/stage1_decision_report.md`, `FINAL_CLAIM_AND_STATUS_REGISTRY.csv` row `AFCP` | Repository records **CONFLICT UNRESOLVED IN REPOSITORY** for the final narrative label. Disposition: the old KNN-AFCP is INVALID/SUPERSEDED; faithful AFCP is EXPLORATORY; **no unconditional AFCP-superiority claim is permitted** either way. Audit preserves this. |
| C4 | **CAND_4 frozen tracking status.** `sensitivity_analysis_plan.md` folds CAND_4 under item 2; `statistical_analysis_plan.md` tracks CAND_4 as a distinct EXPLORATORY item. | `documentation/validation/cand4_resolution_evidence.csv` | Documentation tension confirmed in the repo's own evidence file; immaterial to results because **CAND_4 was never executed** (no model/prediction/result artifact exists). Disposition: CAND_4 `NOT_EXECUTED`. |

> **ADJUDICATED 2026-08-27 → C1–C4 RESOLVED.** Formal one-sentence decisions and their bases are
> recorded in `documentation/final_research_audit/CONFLICT_ADJUDICATIONS.md`. The tables and lists
> in this document retain their original `CONFLICT UNRESOLVED` wording (append-only) but are
> superseded on these four points by that file: C1 the raw artifact governs (BMI-Obese
> under-covers); C2 executed, EXPLORATORY only; C3 KNN-AFCP INVALID / faithful AFCP EXPLORATORY,
> no superiority claim; C4 CAND_4 DISTINCT–EXPLORATORY–UNEXECUTED (Amendment #14). No scientific
> number changes.

No other numeric claim checked in this audit (Phase 1 cohort flow, Phase 3 AUROC/thresholds,
Phase 4 raw & recalibrated calibration, Phase 5 BMI/Age fairness, Phase 6 intersectional coverage,
Phase 7 Mondrian 5/9 + XGBoost breach, Phase 8 holdout, MI, 8.0 kPa) showed a
discrepancy against the repository's frozen result files.

---

## 1. Research objective

In adults with a quality-valid transient-elastography exam, how accurately, fairly, and
reliably can routine demographic and laboratory predictors identify significant liver fibrosis
(`LUXSMED ≥ 8.2 kPa` with `LUAXSTAT == 1`) — and does a model that looks acceptable on
discrimination and aggregate calibration still fail reliability guarantees for specific
demographic subgroups, and can group-wise mitigation repair that?
Source: `documentation/phase2/primary_research_question.md`,
`documentation/final_audit/MASTER_END_TO_END_RESEARCH_REPORT.md` §A1. **AUTHORITATIVE.**

## 2. Frozen primary study (verified)

| Element | Frozen value | Verified against |
|---|---|---|
| Cohort | `CAND_1_QUALITYVALID_ADULT_BROAD` | `results/tables/phase2_candidate_cohort_comparison.csv`, `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` |
| N | 7,153 | `results/tables/phase2_outcome_prevalence.csv`; `phase1_reproduction` join = 7,153 |
| Positives / negatives | 666 / 6,487 | same |
| Prevalence | 9.31% (9.3108%) | same; `PHASE6_8KPA_ROBUSTNESS_REPORT.md` cohort-audit |
| Outcome | `LUXSMED ≥ 8.2 kPa`, valid VCTE (`LUAXSTAT==1`); frozen before training | `documentation/phase2/primary_outcome_definition.md` |
| Train / test | 5,007 / 2,146 (466 / 200 positives; ≈9.31% each) | `data/processed/splits/*`, `FINAL_CLAIM_AND_STATUS_REGISTRY.csv` row O |
| Conformal proper-train / calibration | 4,005 / 1,002 (373 / 93 positives); quantile index k=903 | `results/uncertainty/phase6_partition_audit.csv`, `MASTER_END_TO_END` §A7 |
| Ten predictors | Age, Sex, BMI, ALT, AST, Albumin, AlkPhos, Bilirubin, Platelets, HDL (`RIDAGEYR RIAGENDR BMXBMI LBXSATSI LBXSASSI LBXSAL LBXSAPSI LBXSTB LBXPLTSI LBDHDD`); race/ethnicity excluded from input, retained for post-hoc fairness | `results/tables/phase2_predictor_registry.csv` |
| Five model families | Logistic Regression, Random Forest, XGBoost, LightGBM, MLP | `results/tables/phase3_final_baseline_results.csv` |

These definitions were not modified by this audit.

## 3. What was completed

**Project pipeline (Phases 1–8), all complete and frozen:** data assembly & remediation (1);
analytical protocol / outcome / predictor / cohort freeze (2); five-family baseline modelling &
discrimination (3); OOF Platt calibration (4); demographic fairness audit (5); split-conformal
uncertainty (6); FDR-gated Mondrian mitigation (7); Non-Hispanic Black subgroup-holdout
generalization (8).

**BMI-fairness follow-up investigation (its own Phases 0–7), all complete:** lineage audit (0);
BMI disparity reproduction (1); BMI mechanism diagnosis (2); corrected BMI-sensitivity
mitigation (3); corrected subgroup calibration (4); MI conformal reliability sensitivity (5);
full 8.0-kPa robustness (6); mitigation cleanup — XGBoost retuning + joint-mitigation audit (7).

**Sensitivity / robustness, executed:** 8.0-kPa threshold (relabel-only); CAND_2
relaxed-elastography (fresh fit); CAND_3 fasting-extended 12-predictor (fresh fit); targeted
Non-Hispanic Black multiple imputation; project-wide 182-test pooled FDR.

**Exploratory diagnostic tracks (stage 0 / stage 1), executed:** continuous BMI/Age splines,
fine age bands, subgroup recalibration + re-quantiling, group-specific thresholds, Equal
Opportunity post-processing, faithful AFCP, joint intersectional conformal methods, M4b N0
selection + trade-offs, fairness–specificity Pareto, clinical false-positive costs, LightGBM
failure analysis, co-occurrence, Decision Curve Analysis, interpretability.

**Constructed but not executed:** CAND_4 all-ages (≥12 y) cohort, N=8,215.
**Not executed:** broader (whole-cohort) MI; MI conformal-coverage comparison; full 8.0-kPa
retraining/recalibration/conformal repetition; conformal replication on CAND_2/CAND_3/8.0 kPa;
severity-graded secondary outcomes (≥9.7 / ≥13.6 kPa); survey-weighted training.
**Not executed / not feasible:** non-NHANES external validation; any later-cycle (temporal)
evaluation (a NHANES 2021–2023 temporal analysis was completed and split into a separate
manuscript — see the scope note at the top of this document).

## 4. What went well

See `RESEARCH_STRENGTHS.md`. In brief: a genuinely frozen primary design (outcome threshold and
predictors fixed before training, verified by hash lineage); five model families compared
head-to-head with FDR control; OOF-only Platt calibration with a locked test touched once per
phase; an explicit, pre-specified fairness audit that produced a real negative-for-the-model
finding; split-conformal uncertainty quantification exposing subgroup failures that AUC and
aggregate calibration hid; a mechanism-focused BMI investigation that reproduced its own prior
result before diagnosing it; disciplined preservation of superseded/invalid work with explicit
demarcation; multiple independent audit and reconciliation passes.

## 5. Strongest scientific findings (CONFIRMED)

1. **Comparable discrimination across five model families.** Test AUROC 0.8229–0.8429; 0/10
   pairwise comparisons FDR-significant. `results/tables/phase3_final_baseline_results.csv`,
   `phase3_model_comparison_fdr.csv`.
2. **Class-balancing induces raw over-prediction, fully corrected by OOF Platt scaling without
   changing AUROC.** OOF intercepts −2.24 to −1.86 for the four class-balanced models (MLP
   −0.28); locked-test ECE 0.2452–0.2967 → 0.0113–0.0264; AUROC unchanged.
   `results/calibration/primary_metrics_by_model.csv`, `test_set_calibration_final.csv`.
3. **Large Normal-BMI vs Obese sensitivity deficit, all five models.** 27.1–47.7 pp lower
   sensitivity in Normal-BMI, FDR-significant (p ≤ 0.006) in 5/5; reproduced independently
   (`PHASE1_REPRODUCTION.md`) and stable across all three sensitivity cohorts (15/15).
   `results/fairness/fairness_inference.csv`, `results/sensitivity/primary_vs_sensitivity_comparison.csv`.
4. **Marginal conformal coverage near target while BMI-Obese and Age-60+ subgroup coverage
   fail.** Marginal 88.12–90.82%; BMI-Obese 76.8–82.3%; Age-60+ 81.1–85.6%; Wilson CIs exclude
   90% for all five models. `results/uncertainty/subgroup_coverage.csv`,
   `marginal_coverage_test_set.csv`.
5. **Within-NHANES demographic transportability loss on a withheld Non-Hispanic Black subgroup.**
   AUROC 0.8229–0.8429 → 0.7719–0.7893; calibration materially less stable.
   `results/validation/phase8_generalization_results.csv`.

## 6. Findings supported with limitations (SUPPORTED WITH LIMITATIONS)

See `VERIFIED_WITH_LIMITATIONS.md`. Summary:

- **Age-60+ sensitivity deficit.** Direction negative in 5/5 primary models; FDR-significant in
  **4/5** (not Logistic). Direction never reverses across sensitivity cohorts, but significance
  is lost in 9/12 instances — **directionally robust, significance specification-sensitive.**
- **Project Phase 7 Mondrian mitigation.** 5/9 qualifying model×subgroup targets reached nominal
  coverage; RF/Obese, XGBoost/Obese, LightGBM/Obese, LightGBM/60+ did not; XGBoost marginal
  coverage rose to 93.4% — a **+5.27 pp breach** of the pre-specified ±5 pp tolerance; the
  BMI-Obese ∩ Age-60+ overlap (294 people, 13.7% of test) received **last-write-wins Age-over-BMI
  precedence, not joint mitigation.**
- **Corrected BMI-investigation Phase 3 (BMI-sensitivity mitigation).** Independent full-cohort
  OOF development → **NO ACCEPTABLE MITIGATION IDENTIFIED**; only MLP received a candidate
  (BMI-specific Platt), reducing the locked-test BMI gap 39.03 → 34.48 pp; no formal candidate
  inference.
- **Corrected BMI-investigation Phase 4 (subgroup calibration).** Decision **B** — **no acceptable
  subgroup-calibration improvement** for the BMI fairness/reliability objective; frozen raw-scale
  classifications and gaps unchanged; no joint intersectional calibrator; runtime access order
  only partially proven; one duplicate output lacks generation provenance.
- **BMI-investigation Phase 5 MI conformal.** Saved tables descriptively support **"MI conformal
  reliability is consistent with complete-case results"**; BMI-Obese under-coverage persists
  under MI; **executable lineage = `LINEAGE NOT FOUND IN REPOSITORY`**; no equivalence test, no
  Rubin pooling.
- **BMI-investigation Phase 6 8.0-kPa robustness (relabel + fresh Platt + fresh conformal on the
  same cohort).** Final conclusion **"SOME MAJOR FINDINGS ARE THRESHOLD-SENSITIVE"**; frozen 8.2
  protocol commit and model-artifact manifest = `NOT FOUND IN REPOSITORY`.
- **BMI-investigation Phase 7 XGBoost retuning / joint audit.** **NO ACCEPTABLE XGBOOST RETUNING
  IDENTIFIED**; joint artifact re-audited as `EXPLORATORY_GENUINE_JOINT` with generating
  script/manifest/runtime log `NOT FOUND IN REPOSITORY` and disclosed XGBoost/LightGBM tolerance
  breaches.
- **NHB targeted MI (whole-model).** ΔAUROC < 0.007, ΔBrier < 0.003; NHB sensitivity changes
  ≤ ±4.2 pp, all CIs include 0, BH-adjusted p = 0.978 for all five models (correction-ceiling
  artifact); 4/5 STABLE, MLP INDETERMINATE. Narrow scope: NHB selection-bias question only.

## 7. Failed / insufficient mitigation attempts

See `EXPLORATORY_RESULTS.md` and `VERIFIED_WITH_LIMITATIONS.md`. Consolidated in
`FINAL_SCIENTIFIC_FINDINGS.md` §Mitigation:

| Intervention | Objective | Outcome | Disposition |
|---|---|---|---|
| Mondrian (Project Phase 7) | restore subgroup conformal coverage | 5/9 targets; XGBoost marginal breach; sequential precedence in overlap | **PARTIALLY EFFECTIVE** |
| Corrected BMI-sensitivity mitigation (thresholding / BMI-Platt / BMI×Age thresholds / combined) | close Normal-BMI sensitivity gap | none passed the multi-metric gate across families | **NO ACCEPTABLE MITIGATION** |
| Corrected subgroup calibration | improve subgroup reliability/fairness via calibration | ECE improved for 3 models; classifications and gaps unchanged; no reliability improvement | **NO ACCEPTABLE MITIGATION** |
| Group-specific Youden thresholds (D05/D07) | equalize subgroup sensitivity | BMI gap halved but **Age gap worsened 26–133%**; ~38–40 pp specificity cost | **EXPLORATORY — Two-Mechanism finding, not a fix** |
| Equal Opportunity post-processing (D06) | equalize TPR | ~50–80 pp target-group sensitivity gain at ~38–40 pp specificity cost; ~399 excess FP per 1,000 normal-weight screened | **EXPLORATORY — clinically unacceptable** |
| XGBoost mitigation retuning (BMI-inv Phase 7) | remove XGBoost coverage-tolerance breach | every gap-closing candidate costs 11–22 pp overall sensitivity or flips the breach | **NO ACCEPTABLE RETUNING** |
| Joint intersectional conformal (Method b / c / M4b N0=0) | restore BMI-Obese ∩ Age-60+ coverage | intersectional coverage ≥ 90% for 4–5/5 models on CAND_1, but XGBoost/LightGBM breach ±5 pp marginal tolerance | **EXPLORATORY / VALID SECONDARY METHOD only** |

**No intervention resolved the BMI classification (sensitivity) disparity. No BMI-sensitivity
mitigation with an acceptable multi-metric profile was identified.**

## 8. Robustness findings

- **8.2 kPa is PRIMARY. 8.0 kPa is a sensitivity / robustness analysis** and does not replace it.
- 8.0-kPa relabel: AUROC 0.8145–0.8326; BMI-Obese disparity **strengthens** to 35.1–51.6 pp
  (5/5 significant); Age-60+ direction negative 5/5, significant only 2/5.
- 8.0-kPa full pipeline (BMI-inv Phase 6): **SOME MAJOR FINDINGS ARE THRESHOLD-SENSITIVE**
  (discrimination and BMI-Obese disparity robust; Age-60+ significance and some conformal detail
  threshold-sensitive; see `phase6_8kpa_vs_82_comparison.csv`).
- CAND_2 (N=7,639): AUROC 0.8526–0.8572; pattern stable; Age-60+ loses significance 3/4.
- CAND_3 (N=3,582, 12 predictors): AUROC 0.8280–0.8457; pattern stable; Age-60+ loses
  significance 4/4.
- Cross-sensitivity: BMI-Obese disparity **stable 15/15**; Age-60+ direction never reverses,
  significance lost 9/12. `results/sensitivity/primary_vs_sensitivity_comparison.csv`.
- Pooled 182-test FDR: headline findings survive at q < 0.05.
- **Threshold-robustness verdicts:** discrimination = ROBUST (magnitude drifts by cohort);
  BMI-Obese sensitivity disparity = ROBUST (magnitude changed, direction fixed); calibration
  correction = ROBUST; Age-60+ disparity significance = THRESHOLD-SENSITIVE /
  SPECIFICATION-SENSITIVE; marginal conformal validity = ROBUST by construction.
- **Conformal subgroup replication (Amendment #16, executed 2026-08-27):** replicated on CAND_2
  and CAND_3 (8.0 kPa already done). BMI-Obese under-coverage = **ROBUST** (5/5 models, CI
  excludes 0.90, FDR-significant on both new cohorts); Age-60+ under-coverage = **direction
  ROBUST, significance power-sensitive** (5/5 FDR-significant CAND_2, 2/5 CAND_3); marginal-vs-
  subgroup contrast replicates. `documentation/sensitivity/CONFORMAL_REPLICATION_SENSITIVITY_COHORTS_RESULTS_REPORT.md`.

## 9. Remaining unresolved issues

1. No non-NHANES external validation (SEPARATE WORK; blocked — no compatible cohort).
2. No acceptable mitigation for the BMI-Obese / Normal-BMI reliability–fairness problem.
3. XGBoost conformal marginal-coverage tolerance breach after mitigation (Mondrian +5.27 pp;
   joint +6.80 pp) — unresolvable within the authorized candidate family.
4. BMI-Obese ∩ Age-60+ intersectional population has no primary joint mitigation; the joint
   methods are exploratory only.
5. Phase 5 MI conformal `LINEAGE NOT FOUND IN REPOSITORY` (descriptive-only handling accepted).
6. Frozen 8.2-kPa protocol commit / model-artifact manifest `NOT FOUND IN REPOSITORY`
   (BMI-inv Phase 6 lineage limitation).
7. AFCP final narrative status — **ADJUDICATED 2026-08-27 (C3, RESOLVED):** KNN-AFCP INVALID,
   faithful AFCP EXPLORATORY, no superiority claim permitted. See `CONFLICT_ADJUDICATIONS.md`.
8. Joint-mitigation execution status vs stale status CSV — **ADJUDICATED 2026-08-27 (C2,
   RESOLVED):** executed 2026-08-24, EXPLORATORY only; stale CSV row superseded. See
   `CONFLICT_ADJUDICATIONS.md`.
9. Conformal subgroup-coverage generalization to CAND_2/CAND_3/8.0 kPa not directly measured.
10. `documentation/MASTER_RESEARCH_RESULTS.md` conformal-coverage section (items 26–27, §3.5)
    is inconsistent with the raw CSVs — **flagged for correction by the register owner; not
    modified by this audit.**

## 10. Unexecuted analyses (full register: `FINAL_REMAINING_WORK_REGISTER.md`)

CAND_4 all-ages; broader whole-cohort MI; MI conformal-coverage comparison; full 8.0-kPa
pipeline; conformal replication on CAND_2/CAND_3/8.0 kPa; severity-graded secondary outcomes
(≥9.7 / ≥13.6 kPa); survey-weighted / weighted-loss training; Phase 5 MI conformal
lineage reconstruction.

## 11. REQUIRED non-validation work

**None.** No repository document labels any remaining non-validation analysis "required", and the
frozen `sensitivity_analysis_plan.md` Governing Rule states its analyses are "a pre-registered
list, not a mandatory execution schedule." The discrimination / calibration / BMI-fairness story
is triangulated across three independent cohort perturbations.

## 12. IMPORTANT work

- **Resolve the status of the pre-registered severity-graded secondary outcomes** (≥9.7 kPa
  advanced fibrosis, 411 positives; ≥13.6 kPa cirrhosis, 177 positives). These are a frozen
  SECONDARY analysis (`statistical_analysis_plan.md` SECONDARY item 2,
  `PHASE2_PROTOCOL_FREEZE.md` row 17) with **no result artifact and no register entry** anywhere.
  Recommendation: add to the remaining-work register and run a **relabel-only descriptive
  discrimination/calibration pass** (no retraining); cirrhosis subgroup fairness would be
  low-powered (~53 test positives) and should be reported overall-only. Full retraining is not
  justified. *(Status resolution = IMPORTANT; execution = OPTIONAL.)*
  **DONE 2026-08-27 (Amendment #15):** executed as a relabel-only descriptive pass —
  `src/sens_13_secondary_severity_outcomes.py`,
  `documentation/sensitivity/SECONDARY_SEVERITY_GRADED_OUTCOMES_RESULTS_REPORT.md`. Discrimination
  comparable to primary; frozen 8.2-kPa recalibration does not transport to the rarer outcomes;
  BMI-Obese disparity direction preserved but underpowered (Normal-BMI n=11 test positives);
  ≥13.6 kPa reported overall-only. Not a deployable severity-staging claim.
- **`documentation/MASTER_RESEARCH_RESULTS.md`** — **DONE 2026-08-27:** deleted in the
  pre-manuscript consolidation (verified factual errors incl. conflict C1; recoverable from git
  history). Superseded by `MASTER_END_TO_END_RESEARCH_REPORT.md` + `final_research_audit/`. See
  `documentation/START_HERE.md`.

## 13. OPTIONAL work

- Conformal subgroup-coverage replication on CAND_2 / CAND_3 / 8.0 kPa — **DONE 2026-08-27
  (Amendment #16).** Pattern replicates: marginal coverage on target both cohorts; BMI-Obese
  under-covers 5/5 models both cohorts (FDR-significant); Age-60+ under-covers in direction both,
  FDR-significant 5/5 CAND_2 and 2/5 CAND_3. The finding is triangulated across four constructions.
  `documentation/sensitivity/CONFORMAL_REPLICATION_SENSITIVITY_COHORTS_RESULTS_REPORT.md`.
- Phase 5 MI conformal executable-lineage reconstruction — only if that result becomes a
  load-bearing manuscript claim.
- CAND_4 all-ages — EXPLORATORY tier only; cannot be promoted to a primary/secondary conclusion.

## 14. DO-NOT-RUN work

Broader whole-cohort MI (not protocol-frozen); MI conformal-coverage comparison (explicitly
unauthorized by the frozen `missing_data_protocol.md`); full 8.0-kPa retraining pipeline
(duplicates the authorized relabel); XGBoost mitigation retuning (already executed and verified —
`NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED`); survey-weighted training (frozen EXPLORATORY,
unresolved methodology, no dependent claim); any rerun / retuning / recalibration / re-selection
of Phase 0–8, BMI-investigation, master, historical-invalid, or corrected-phase
artifacts.

## 15. Out-of-sample evaluation status

**NO OUT-OF-SAMPLE EVALUATION IS IN SCOPE FOR THIS STUDY.** There is no later-cycle (temporal)
analysis and no independent-cohort analysis in this repository. A NHANES 2021–2023 temporal
evaluation was completed and then **split into a separate manuscript**; all temporal code,
results, and documents were removed from this repository and preserved on the
`temporal-validation-standalone` git branch. It is not part of this study's evidence base.

## 16. External-validation status

**EXTERNAL VALIDATION — NOT EXECUTED / NOT FEASIBLE within repository evidence.**
No obtained independent non-NHANES cohort with demonstrated compatibility for the frozen outcome,
ten predictors, and VCTE quality rule. The Non-Hispanic Black holdout (Phase 8) is a
within-NHANES demographic holdout and **must not** be called external validation. Source:
`documentation/reliability_extension/external_validation_future_work.md`,
`FINAL_CLAIM_AND_STATUS_REGISTRY.csv` row `EXT`.

## 17. Manuscript-ready claims

The claims in `MANUSCRIPT_READY_PRIMARY_CLAIMS.md` / this audit's
`results/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` rows with
`manuscript_status = MANUSCRIPT_READY`: CAND_1 composition; five-family AUROC band and no
FDR-significant winner; raw over-prediction + OOF Platt correction without AUROC change;
Normal-BMI vs Obese sensitivity deficit 27.1–47.7 pp in 5/5; marginal-vs-subgroup conformal
coverage split (BMI-Obese and Age-60+ fail); interpretability (ALT/AST/BMI/Age top features).
Everything else is `MANUSCRIPT_READY_WITH_QUALIFICATION`, `EXPLORATORY_ONLY`, `NOT_USABLE`, or
`SEPARATE_WORK`.

**Framing decision (2026-08-27, `MANUSCRIPT_FRAMING_GUIDANCE.md`):** the headline is the
Normal-BMI under-detection finding and the marginal-vs-subgroup conformal-coverage contrast. The
**Age-60+ *sensitivity* disparity is a secondary observation** — Results body and Limitations
only, never the abstract, always stated with its fragility; it is not a co-headline with BMI. The
**Age-60+ *conformal* under-coverage stays at full strength** in the conformal results (a
different, firmer finding). Keep the two Age-60+ findings explicitly distinct.

## 18. Required manuscript limitations

Full register: `FINAL_LIMITATIONS_REGISTER.md`. Minimum set that must appear: no external or
out-of-sample (later-cycle / independent-cohort) validation; Age-60+ significance is
specification-sensitive; Phase 7 mitigation is partial (5/9), with an XGBoost coverage breach and
sequential (not joint) overlap handling; no acceptable BMI-sensitivity mitigation was found;
conformal subgroup coverage is empirical and not a conditional-validity guarantee; conformal
subgroup coverage was primarily measured on CAND_1 and replicated on 8.0 kPa / CAND_2 / CAND_3
(Amendment #16 — BMI-Obese robust; Age-60+ direction robust, significance power-sensitive on the
smaller CAND_3); MI is narrow-scope (NHB) and the MI conformal
tables lack executable lineage; NHB holdout is within-NHANES; single survey program, single
country, cross-sectional VCTE reference standard (not biopsy); Underweight-BMI is uninterpretable
(1 positive); small subgroup / intersectional cells limit precision; class-balancing artifact
required post-hoc recalibration.

## 19. Final scientific interpretation

Five routine-data model families reach a comparable, modest-to-strong discrimination ceiling for
significant fibrosis (AUROC ~0.82–0.84) and, after a required OOF recalibration, are
well-calibrated in aggregate. That aggregate adequacy conceals a reproducible, mechanism-linked
reliability failure concentrated in the same clinically important groups: normal-weight patients
are under-detected (low sensitivity), and Obese and 60+ patients receive conformal prediction
sets that under-cover the truth. Threshold tuning helps the BMI sensitivity gap (a
score-distribution/threshold mechanism) but harms the Age gap (a different, non-threshold
mechanism), and no calibration-, threshold-, or conformal-based intervention tested produced an
acceptable fix. Group-wise Mondrian conformal mitigation is a genuine but partial repair. The
BMI disparity is the most robust finding in the study — reproduced and stable across three
sensitivity cohorts. The Age-60+ disparity is
directionally consistent but statistically fragile. Transportability is limited: withholding a
demographic subgroup from training degrades discrimination and calibration on that subgroup, and
no later-cycle or independent-cohort evaluation is in scope. The
study's contribution is the demonstration that discrimination + aggregate calibration are
insufficient reliability evidence for subgroup-safe clinical deployment, not a deployable model.

## 20. Final recommendation

**B — MANUSCRIPT-READY WITH SPECIFIED QUALIFICATIONS.**

The scientific state is stable and internally consistent (one documentation conflict, C1, is
flagged for the register owner and does not affect any result). No required non-validation work
remains. The manuscript can be written now, provided it (i) carries the limitations in §18,
(ii) frames every non-primary result at its register tier, (iii) explicitly notes that **no
external or out-of-sample validation has been performed**, and (iv) makes none of the claims in
`DO_NOT_CLAIM.md`.

---

## Validation boundary

**EXTERNAL VALIDATION — NOT PERFORMED.** No out-of-sample (later-cycle or independent-cohort)
evaluation is in scope for this study.

## Preservation attestation

No primary result, Phase 0–8 artifact, BMI-investigation artifact, historical or exploratory
artifact, master report, or external-validation file was modified. Only the
files under `documentation/final_research_audit/` and `results/final_research_audit/` were
created.

**END — FINAL END-TO-END RESEARCH AUDIT.**
