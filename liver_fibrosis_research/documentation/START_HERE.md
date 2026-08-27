# START HERE — Documentation Authority Map

**Created:** 2026-08-27 (repository consolidation / pre-manuscript evidence freeze)
**Purpose:** This repository accumulated several overlapping "final" audit layers produced by
successive review passes. This file is the single entry point: it fixes the reading order, the
authority hierarchy, the disposition of superseded material, and the four documented unresolved
conflicts. Read this before citing any number from any other document.

**Documentation cleanup (2026-08-27):** ~77 process-trail files (pre-execution snapshots, decision
logs, correction/closure/reconciliation records, superseded per-phase reports) were moved to
`documentation/archive/process_trail/` — nothing deleted. The active tree below is now ~115
markdown files; anything self-labelled a *snapshot*, *decision log*, *correction record*, or
*closure/verification report* is process history, not a source. Links to old paths resolve under
`documentation/archive/process_trail/<original-path>` (see `documentation/archive/README.md`).

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
   data assembly through the sensitivity suite. Consistent with (2); use for context and phase
   detail.
4. **`documentation/final_audit/` — 5 active files** (2026-08-24/25) —
   `MASTER_END_TO_END_RESEARCH_REPORT.md` (narrative history),
   `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md`, `INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`,
   `REPRODUCIBILITY.md`, `CHANGELOG_RESEARCH.md`. Earlier consolidation layer; still cited by (2).
   Superseded only where (2) explicitly reconciles a point.
5. **`documentation/archive/`** — superseded synthesis layers and the process trail, moved
   2026-08-27 to keep the active tree legible; nothing deleted (see `documentation/archive/README.md`):
   - `archive/process_trail/` (~77 files) — pre-execution snapshots, decision logs, correction /
     closure / reconciliation / verification records, and superseded per-phase reports. Links to
     old paths resolve here under the original relative path (repo-root files under `root/`).
   - `archive/final_research_state/` (14 files) — the register set that (2) consolidates and
     supersedes. Where `final_research_audit/` documents cite `documentation/final_research_state/…`,
     read it as `documentation/archive/final_research_state/…`.
   - `archive/final_audit/` (10 files) — superseded synthesis fragments (`FINAL_CLAIM_AUDIT.md`,
     `FINAL_RESEARCH_ARCHITECTURE.md`, `FINAL_RESEARCH_STATUS.md`,
     `FINAL_SCIENTIFIC_INTERPRETATION.md`, `FINAL_SCIENTIFIC_STATUS_RECONCILIATION.md`,
     `REMAINING_ANALYSES_AND_RESEARCH_STATUS.md`, `ITEMS_1_5_REFINEMENT_ADDENDUM.md`,
     `P0_P1_REMEDIATION_ADDENDUM.md`, both `COMPLETE_END_TO_END_*` reports).
6. **Phase-by-phase results reports** at the project root — `PHASE1_DATA_ASSEMBLY_REPORT.md` …
   `PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md`, plus
   `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md`, `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`,
   `RELIABILITY_EXTENSION_RESULTS_REPORT.md`, and the two
   `documentation/sensitivity/*_RESULTS_REPORT.md`. The primary detailed record of each phase.
   (The `*_CLOSURE_*`, `*_RECONCILIATION_*`, `*_VERIFICATION_*` and `FINAL_PRE_CALIBRATION_*`
   housekeeping reports were moved to `documentation/archive/process_trail/root/`.)
7. **Follow-up investigation reports** — `documentation/fairness_bmi_investigation/` (~8 current
   reports: `PHASE0_LINEAGE_AUDIT`, `PHASE1_REPRODUCTION`, `PHASE2_DIAGNOSTIC_REPORT`,
   `phase3_corrected/PHASE3_CORRECTED_MITIGATION_REPORT`, `PHASE4_CORRECTED_FINAL_AUDIT_REPORT`,
   `PHASE5_MI_CONFORMAL_REPORT`, `PHASE6_8KPA_ROBUSTNESS_REPORT`,
   `PHASE7_MITIGATION_CLEANUP_REPORT`). Authoritative for their own scope. The decision logs and
   superseded/audit-of-audit reports are in `documentation/archive/process_trail/fairness_bmi_investigation/`.
8. **Protocol freezes / pre-registration** — `documentation/phase2/` (16 protocol files:
   `PHASE2_PROTOCOL_FREEZE.md`, `primary_outcome_definition.md`, `statistical_analysis_plan.md`,
   `sensitivity_analysis_plan.md`, `fairness_subgroup_protocol.md`, `missing_data_protocol.md`,
   `uncertainty_protocol.md`, …), the `documentation/phase3/` design/protocol files, and
   `documentation/end_to_end/protocol_amendment_registry.md` (16 amendments). These define what
   was pre-specified; they are not result documents.
9. **Historical / superseded / exploratory / process** — `documentation/archive/` (including
   `process_trail/`), `documentation/**/archive/`, and anything self-labelled SUPERSEDED / INVALID
   / EXPLORATORY / snapshot / decision log. Preserved for transparency; never a manuscript source.

Recency alone never confers authority. A later artifact supersedes an earlier one only where a
document in tier 2–4 explicitly records the reconciliation.

## 2. Recommended reading order

1. This file.
2. `documentation/final_research_audit/FINAL_RESEARCH_AUDIT.md` (master synthesis).
3. `documentation/final_research_audit/FINAL_SCIENTIFIC_FINDINGS.md` +
   `MANUSCRIPT_READINESS_ASSESSMENT.md` + `MANUSCRIPT_FRAMING_GUIDANCE.md` + `DO_NOT_CLAIM.md`.
4. `documentation/final_research_audit/CONFLICT_ADJUDICATIONS.md` (C1–C4, resolved 2026-08-27).
5. `documentation/manuscript/MANUSCRIPT_DRAFT.md` — the working draft, with every claim traced to
   a registry `claim_id`.
6. `documentation/final_audit/MASTER_END_TO_END_RESEARCH_REPORT.md` for phase-level narrative.
7. Individual phase reports / investigation reports as needed for method detail.

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
- **`results/tables/final_research_status.csv` is STALE on one row** (kept unedited per the
  append-only convention): "Intersectional (joint) Mondrian mitigation — NOT EXECUTED" (it *was*
  executed, exploratory only — conflict C2 below). CAND_4 remains correctly NOT EXECUTED. Use
  `documentation/final_research_audit/` for current status.

## 4. The four conflicts — ADJUDICATED 2026-08-27 (RESOLVED)

Recorded as `CONFLICT UNRESOLVED IN REPOSITORY` in the audit trail; formally resolved in
`documentation/final_research_audit/CONFLICT_ADJUDICATIONS.md`. One-line dispositions:

- **C1 — conformal subgroup under-coverage (which BMI group, and the numbers).** RESOLVED against
  the raw artifact: `results/uncertainty/subgroup_coverage.csv` +
  `results/uncertainty/marginal_coverage_test_set.csv` — **BMI-Obese under-covers (0.768–0.823),
  Age-60+ under-covers (0.811–0.856), marginal coverage 0.881–0.908.** The now-deleted
  `MASTER_RESEARCH_RESULTS.md` was the only source that said otherwise.
- **C2 — joint intersectional Mondrian mitigation execution status.** It **was executed** (2026-08-24,
  `results/mitigation/joint_intersectional_mitigation.csv`) and is **EXPLORATORY ONLY** — never a
  primary result. The stale status CSV row is superseded by the dated artifact + the BMI-investigation
  Phase 7 cleanup audit. It fails the marginal-coverage tolerance for XGBoost/LightGBM.
- **C3 — faithful-AFCP final narrative status.** The old KNN-approximation AFCP is **INVALID — do
  not cite**. Faithful AFCP is **EXPLORATORY**. **No AFCP-superiority claim is permitted** under
  either label.
- **C4 — CAND_4 tracking tier.** Classified **DISTINCT — EXPLORATORY — UNEXECUTED** (Amendment #14).
  Immaterial to results: no CAND_4 model, prediction, or result artifact exists. Do not report
  CAND_4 performance.

## 5. Validation boundary (state explicitly in any write-up)

- **No out-of-sample evaluation is in scope for this study.** There is no later-cycle (temporal)
  analysis and no independent-cohort analysis. A NHANES 2021–2023 temporal evaluation was carried
  out but has been **split into a separate manuscript** and removed from this repository (preserved
  on the `temporal-validation-standalone` git branch); it is **not** part of this study's evidence
  base and must not be cited here.
- **External (non-NHANES) validation — NOT PERFORMED / NOT FEASIBLE within current evidence.** No
  compatible independent cohort identified. The project's foremost generalizability limitation.
- The **Non-Hispanic Black subgroup holdout (Phase 8)** is a *within-NHANES demographic holdout*,
  not external validation. Do not describe it as such.

## 6. Manuscript framing (headline discipline)

Full guidance: `documentation/final_research_audit/MANUSCRIPT_FRAMING_GUIDANCE.md`. In brief:

- **Headline = the normal-weight (Normal-BMI) under-detection finding** plus the methodological
  marginal-vs-subgroup conformal-coverage contrast. Nothing else carries the abstract.
- **The Age-60+ *sensitivity* disparity is a secondary observation**, not a co-headline: Results
  body and Limitations only, always stated with its fragility (4/5 models; significance lost 9/12
  under alternative specifications; non-monotonic). Never paired with the BMI finding as "two
  subgroup failures."
- **The Age-60+ *conformal* under-coverage stays at full strength** in the conformal results
  (5/5 models, CIs exclude 90%). It is a different, firmer finding than the sensitivity disparity
  — keep the two explicitly distinct in the text.

## 7. Executed during / after consolidation (2026-08-27)

- **Amendment #15 — pre-registered SECONDARY severity-graded outcomes (≥9.7 kPa, ≥13.6 kPa),
  relabel-only descriptive pass.** Closes the one pre-registered analysis that had no result
  artifact. Discrimination comparable to the primary outcome; the frozen 8.2-kPa Platt
  recalibration does **not** transport to the rarer outcomes; BMI-Obese disparity direction
  preserved but underpowered (Normal-BMI n=11 test positives); ≥13.6 kPa reported overall-only.
  Not a deployable severity-staging claim.
  Report: `documentation/sensitivity/SECONDARY_SEVERITY_GRADED_OUTCOMES_RESULTS_REPORT.md`;
  results: `results/sensitivity/secondary_severity_outcomes_*`.
- **C1–C4 conflict adjudications** — `CONFLICT_ADJUDICATIONS.md` (all four RESOLVED).
- **Manuscript framing decision** — `MANUSCRIPT_FRAMING_GUIDANCE.md` (Age-60+ sensitivity demoted
  to secondary observation).
- **Amendment #16 — conformal subgroup-coverage replication on CAND_2 / CAND_3** (8.0 kPa was
  already done). The CAND_1 marginal-vs-subgroup coverage pattern **replicates**: BMI-Obese
  under-covers in 5/5 models on both new cohorts (FDR-significant); Age-60+ under-covers in
  direction on both (FDR-significant 5/5 CAND_2, 2/5 CAND_3). The one previously un-triangulated
  primary finding is now triangulated across four constructions.
  Report: `documentation/sensitivity/CONFORMAL_REPLICATION_SENSITIVITY_COHORTS_RESULTS_REPORT.md`.

## 8. Freeze

This consolidation is tagged as the pre-manuscript evidence freeze (`evidence-freeze`). After
this point the analysis set is closed: no rerun, retuning, recalibration, or re-selection of any
Phase 0–8, BMI-investigation, or sensitivity artifact without a new dated protocol
amendment. Remaining permitted work is enumerated in
`documentation/final_research_audit/FINAL_REMAINING_WORK_REGISTER.md`.

> **Scope note (temporal validation split out):** a NHANES 2021–2023 temporal evaluation was
> completed and then moved to a **separate manuscript**. All temporal code, results, and documents
> were removed from this repository and preserved on the `temporal-validation-standalone` git
> branch. This study's scope is the frozen NHANES 2017–March 2020 analysis only; no temporal or
> external out-of-sample result is part of its evidence base.
