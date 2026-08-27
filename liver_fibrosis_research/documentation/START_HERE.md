# START HERE — Documentation Authority Map

**Created:** 2026-08-27 (repository consolidation / pre-manuscript evidence freeze)
**Purpose:** This repository accumulated several overlapping "final" audit layers produced by
successive review passes. This file is the single entry point: it fixes the reading order, the
authority hierarchy, the disposition of superseded material, and the four documented unresolved
conflicts. Read this before citing any number from any other document.

---

## 1. Authority hierarchy (highest wins on any disagreement)

1. **Raw frozen result artifacts** — `results/**/*.csv`, `*.json`, `data/processed/splits/*`,
   `results/tables/model_lineage.csv`. A number in a prose document that disagrees with the raw
   artifact it cites is wrong; the artifact governs.
2. **`documentation/final_research_audit/`** (2026-08-27) — the newest end-to-end audit. Its
   `FINAL_RESEARCH_AUDIT.md` is the master synthesis; the companion registers
   (`AUTHORITATIVE_RESULTS.md`, `VERIFIED_WITH_LIMITATIONS.md`, `EXPLORATORY_RESULTS.md`,
   `SUPERSEDED_INVALID_RESULTS.md`, `DO_NOT_CLAIM.md`, `FINAL_LIMITATIONS_REGISTER.md`,
   `FINAL_REMAINING_WORK_REGISTER.md`, `FINAL_SCIENTIFIC_FINDINGS.md`, `RESEARCH_STRENGTHS.md`,
   `RESEARCH_WEAKNESSES.md`, `MANUSCRIPT_READINESS_ASSESSMENT.md`,
   `FINAL_RESEARCH_QUALITY_ASSESSMENT.md`) are its typed breakdowns.
   Machine-readable claim registry: `results/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv`.
3. **`documentation/final_audit/MASTER_END_TO_END_RESEARCH_REPORT.md`** — narrative history from
   data assembly through temporal validation. Consistent with (2); use for context and phase
   detail.
4. **`documentation/final_audit/` — 5 active files** (2026-08-24/25) —
   `MASTER_END_TO_END_RESEARCH_REPORT.md` (narrative history),
   `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md`, `INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`,
   `REPRODUCIBILITY.md`, `CHANGELOG_RESEARCH.md`. Earlier consolidation layer; still cited by (2).
   Superseded only where (2) explicitly reconciles a point.
5. **`documentation/archive/`** — superseded synthesis layers, moved 2026-08-27 to keep the active
   tree legible; nothing deleted (see `documentation/archive/README.md`):
   - `archive/final_research_state/` (14 files) — the register set that (2) consolidates and
     supersedes. Where `final_research_audit/` documents cite `documentation/final_research_state/…`,
     read it as `documentation/archive/final_research_state/…`.
   - `archive/final_audit/` (10 files) — superseded synthesis fragments (`FINAL_CLAIM_AUDIT.md`,
     `FINAL_RESEARCH_ARCHITECTURE.md`, `FINAL_RESEARCH_STATUS.md`,
     `FINAL_SCIENTIFIC_INTERPRETATION.md`, `FINAL_SCIENTIFIC_STATUS_RECONCILIATION.md`,
     `REMAINING_ANALYSES_AND_RESEARCH_STATUS.md`, `ITEMS_1_5_REFINEMENT_ADDENDUM.md`,
     `P0_P1_REMEDIATION_ADDENDUM.md`, both `COMPLETE_END_TO_END_*` reports).
6. **Phase-by-phase reports** at the project root (`PHASE1_DATA_ASSEMBLY_REPORT.md` …
   `PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md`, plus the `*_CLOSURE_*`,
   `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md`, `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`,
   `MI_CLOSURE_RECONCILIATION_REPORT.md`, `RELIABILITY_EXTENSION_RESULTS_REPORT.md`,
   `CAND4_CLASSIFICATION_RESOLUTION_REPORT.md`, `END_TO_END_PHASE1_TO_PHASE3_VERIFICATION_REPORT.md`,
   `FINAL_PRE_CALIBRATION_*`). The primary detailed record of each phase. Frozen; append-only.
7. **Follow-up investigation phase reports** — `documentation/fairness_bmi_investigation/`
   (BMI follow-up Phases 0–7) and `results/temporal_validation/PHASE*` (NHANES 2021–2023 temporal
   validation). Authoritative for their own scope; each carries its own decision log.
8. **Protocol freezes / pre-registration** — `documentation/phase2/` (`PHASE2_PROTOCOL_FREEZE.md`,
   `primary_outcome_definition.md`, `statistical_analysis_plan.md`, `sensitivity_analysis_plan.md`,
   `fairness_subgroup_protocol.md`, `missing_data_protocol.md`, `uncertainty_protocol.md`),
   `documentation/end_to_end/protocol_amendment_registry.md` (15 amendments). These define what
   was pre-specified; they are not result documents.
9. **Historical / superseded / exploratory** — `exploratory_posthoc*/`, `exploratory_602020/`,
   `documentation/**/archive/`, and anything self-labelled SUPERSEDED / INVALID / EXPLORATORY.
   Preserved for transparency; never a manuscript source.

Recency alone never confers authority. A later artifact supersedes an earlier one only where a
document in tier 2–4 explicitly records the reconciliation.

## 2. Recommended reading order

1. This file.
2. `documentation/final_research_audit/FINAL_RESEARCH_AUDIT.md` (master synthesis).
3. `documentation/final_research_audit/FINAL_SCIENTIFIC_FINDINGS.md` +
   `MANUSCRIPT_READINESS_ASSESSMENT.md` + `DO_NOT_CLAIM.md`.
4. `documentation/final_audit/MASTER_END_TO_END_RESEARCH_REPORT.md` for phase-level narrative.
5. Individual phase reports / investigation reports as needed for method detail.

## 3. Superseded and removed

- **`documentation/archive/` — superseded synthesis layers moved there 2026-08-27** (not deleted):
  the whole `final_research_state/` register set and 10 superseded `final_audit/` fragments. See
  `documentation/archive/README.md`. Citations elsewhere to `documentation/final_research_state/…`
  now resolve at `documentation/archive/final_research_state/…`.
- **`documentation/MASTER_RESEARCH_RESULTS.md` — DELETED in this consolidation (recoverable from
  git history at `4ad991a`).** It contained verified factual errors against the raw artifacts:
  it named *Normal-BMI* as the under-covered conformal subgroup (raw data: Normal-BMI **over**-covers
  ~0.96–0.97; **BMI-Obese** under-covers 0.768–0.823), gave marginal coverage as 89.00–90.12%
  (raw: 88.12–90.82%), and listed Phase 3 operating-point sensitivity/specificity and Phase 7
  mitigation targets that do not match `results/tables/phase3_final_baseline_results.csv` or
  `results/mitigation/`. Do not restore or cite it. Its correct replacements are tiers 2–3 above.
- **`results/tables/final_research_status.csv` is STALE on three rows** (kept unedited per the
  append-only convention): "Intersectional (joint) Mondrian mitigation — NOT EXECUTED" (it *was*
  executed, exploratory only — conflict C2 below); "Temporal (cross-cycle) validation — NOT
  EXECUTED / infeasible" (NHANES 2021–2023 temporal validation *is* complete — see §5);
  CAND_4 remains correctly NOT EXECUTED. Use `documentation/final_research_audit/` for current
  status.

## 4. The four documented unresolved conflicts (adjudications)

These are recorded as `CONFLICT UNRESOLVED IN REPOSITORY` in the audit trail. One-line
manuscript-level dispositions:

- **C1 — conformal subgroup under-coverage (which BMI group, and the numbers).** RESOLVED against
  the raw artifact: `results/uncertainty/subgroup_coverage.csv` +
  `results/uncertainty/marginal_coverage_test_set.csv` — **BMI-Obese under-covers (0.768–0.823),
  Age-60+ under-covers (0.811–0.856), marginal coverage 0.881–0.908.** The now-deleted
  `MASTER_RESEARCH_RESULTS.md` was the only source that said otherwise.
- **C2 — joint intersectional Mondrian mitigation execution status.** It **was executed** (2026-08-24,
  `results/mitigation/joint_intersectional_mitigation.csv`) and is **EXPLORATORY ONLY** — never a
  primary result. The stale status CSV row is superseded by the dated artifact + the BMI-investigation
  Phase 7 cleanup audit. It fails the marginal-coverage tolerance for XGBoost/LightGBM and does not
  replicate temporally (1/5 models).
- **C3 — faithful-AFCP final narrative status.** The old KNN-approximation AFCP is **INVALID — do
  not cite**. Faithful AFCP is **EXPLORATORY**. **No AFCP-superiority claim is permitted** under
  either label.
- **C4 — CAND_4 tracking tier.** Classified **DISTINCT — EXPLORATORY — UNEXECUTED** (Amendment #14).
  Immaterial to results: no CAND_4 model, prediction, or result artifact exists. Do not report
  CAND_4 performance.

## 5. Validation boundary (state explicitly in any write-up)

- **NHANES 2021–2023 temporal validation — SEPARATE WORK, COMPLETE.** N=4,910; 563 positives
  (11.47%); frozen models/thresholds/conformal params, no temporal refit. Result:
  **PARTIAL TEMPORAL REPLICATION** (discrimination AUROC → 0.777–0.782; BMI-Obese sensitivity
  disparity persisted and enlarged; Age-60+ disparity shrank/reversed; subgroup + intersectional
  conformal under-coverage persisted; frozen N0=0 M4b held for 1/5 models vs 4/5 originally).
  Source: `results/temporal_validation/PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md`.
- **External (non-NHANES) validation — NOT PERFORMED / NOT FEASIBLE within current evidence.** No
  compatible independent cohort identified. The project's foremost generalizability limitation.
- The **Non-Hispanic Black subgroup holdout (Phase 8)** is a *within-NHANES demographic holdout*.
  Neither it nor the 2021–2023 temporal work is external validation. Do not describe either as such.

## 6. Freeze

This consolidation is tagged as the pre-manuscript evidence freeze. After this point, the
analysis set is closed: no rerun, retuning, recalibration, or re-selection of any Phase 0–8,
BMI-investigation, temporal, or sensitivity artifact without a new dated protocol amendment.
Remaining permitted work is enumerated in
`documentation/final_research_audit/FINAL_REMAINING_WORK_REGISTER.md`.
