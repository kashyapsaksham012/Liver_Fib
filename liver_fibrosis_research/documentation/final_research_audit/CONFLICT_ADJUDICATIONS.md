# Conflict Adjudications — C1–C4

**Date:** 2026-08-27 · **Status:** AUTHORITATIVE · **Type:** decision record (no analysis, no
rerun, no artifact modified).

The end-to-end audit (`FINAL_RESEARCH_AUDIT.md` §CONFLICTS, §9) recorded four points as
`CONFLICT UNRESOLVED IN REPOSITORY`. Per the project's append-only convention, the frozen documents
that carry that token are **not** edited. **This file is the resolution layer**: it adjudicates
each conflict with a single-sentence decision and its basis. After this date, C1–C4 are
**RESOLVED**; any document still showing `CONFLICT UNRESOLVED` for one of these four items is
superseded by the corresponding entry below.

---

## C1 — Conformal subgroup under-coverage: which BMI group fails, and the numbers

- **Conflict:** the deleted `documentation/MASTER_RESEARCH_RESULTS.md` (items 26–27, §3.5) named
  *Normal-BMI* as the under-covered conformal subgroup with marginal coverage 89.00–90.12%; every
  other source and the raw CSVs name *BMI-Obese*.
- **DECISION:** the raw frozen artifacts govern — **BMI-Obese** under-covers (empirical coverage
  0.768–0.823, Wilson CIs exclude 0.90, all 5 models), **Age-60+** under-covers (0.811–0.856),
  Normal-BMI and Overweight **over-cover** (~0.96–0.97), and marginal coverage is **0.881–0.908**.
- **Basis:** `results/uncertainty/subgroup_coverage.csv`, `results/uncertainty/marginal_coverage_test_set.csv`
  (verified from raw CSV in the 2026-08-27 audit and this consolidation); the sole dissenting
  source contained transcription errors across multiple sections and was deleted in the
  pre-manuscript consolidation (recoverable from git history at `4ad991a`).
- **STATUS: RESOLVED.**

## C2 — Joint (intersectional) Mondrian mitigation: execution status

- **Conflict:** `results/tables/final_research_status.csv` marks joint intersectional mitigation
  `NOT EXECUTED`; a dated artifact and the BMI-investigation Phase 7 cleanup document it as
  executed.
- **DECISION:** joint intersectional mitigation **was executed** (2026-08-24) and is classified
  **EXPLORATORY ONLY** — it is never a primary or secondary result; the stale status-CSV row is
  superseded.
- **Basis:** `results/mitigation/joint_intersectional_mitigation.csv` (generated 2026-08-24T12:42
  UTC), `INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`,
  `documentation/fairness_bmi_investigation/PHASE7_MITIGATION_CLEANUP_VERIFICATION.md`; the method
  breaches the ±5 pp marginal-coverage tolerance for XGBoost/LightGBM, which is itself part of why
  it stays exploratory.
- **STATUS: RESOLVED.** (`results/tables/final_research_status.csv` remains unedited per the
  append-only convention; treat its joint-mitigation row as stale — see `START_HERE.md` §3.)

## C3 — Faithful-AFCP final narrative status

- **Conflict:** an older status marks the AFCP work "blocked / rule-violating (KNN approximation)";
  a newer status marks it "conditional-frozen exploratory."
- **DECISION:** the KNN-approximation AFCP is **INVALID and must not be cited**; the faithful-AFCP
  re-implementation is **EXPLORATORY**, and **no AFCP-superiority or AFCP-adequacy claim is
  permitted** under either label.
- **Basis:** `results/diagnostics/stage1_decision_report.md`, `src/sens_11_afcp_faithful.py`,
  `results/diagnostics/stage1/afcp_faithful_results.csv`; both statuses agree that AFCP is not a
  usable result, so the narrative-label dispute has no effect on any manuscript claim.
- **STATUS: RESOLVED.**

## C4 — CAND_4 (all-ages ≥12 y) tracking tier

- **Conflict:** `sensitivity_analysis_plan.md` folds CAND_4 under item 2; `statistical_analysis_plan.md`
  tracks it as a distinct EXPLORATORY item.
- **DECISION:** CAND_4 is **DISTINCT — EXPLORATORY — UNEXECUTED** (Protocol Amendment #14); it has
  no model, prediction, or result artifact, and its performance must not be reported.
- **Basis:** `documentation/end_to_end/protocol_amendment_registry.md` #14;
  `documentation/validation/cand4_resolution_evidence.csv`; the dispute is a documentation-tier
  question only and is immaterial to results because CAND_4 was never executed.
- **STATUS: RESOLVED.**

---

## Effect on other documents

- `START_HERE.md` §4 carries the same four one-line dispositions and now points here.
- `FINAL_RESEARCH_AUDIT.md` §CONFLICTS / §9, `MASTER_END_TO_END_RESEARCH_REPORT.md`, and
  `FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` retain their original `CONFLICT UNRESOLVED` wording
  (append-only) but are superseded on these four points by this file.
- No scientific number changes. C1 fixes a description; C2–C4 fix status/tier labels.
