# Primary Clinical Outcome Definition (Phase 2E)

**Generated:** 2026-08-18 — **HIGH-STAKES DECISION, FROZEN BEFORE ANY MODEL IS TRAINED.**

## Evaluation of Candidate Thresholds

Phase 1 counted 9 candidate cutpoints descriptively (7.0–13.6 kPa) without endorsing any of them. Phase 2
now evaluates their clinical justification, per the evidence gathered in
`documentation/source_metadata/phase1_references.md`:

| Candidate | Clinical meaning | Evidence quality | Notes |
|---|---|---|---|
| 7.0 / 7.5 / 9.0 kPa | "General cutoff" round numbers | Non-specific literature range | No single dedicated source; excluded as candidates for the primary label |
| **8.0 kPa** | Significant fibrosis (≥F2), commonly-used round number | Widely cited across the VCTE literature but not tied to one rigorously derived estimate | Retained as SENSITIVITY threshold |
| **8.2 kPa** | Significant fibrosis (≥F2) | **Youden-optimal cutoff from a 2024 systematic review/meta-analysis of VCTE vs. MRE in NAFLD/MASLD** (PMC11493355): AUROC 0.87 (95% CI 0.84–0.90) for the ≥F3 comparator population underlying the same analysis, sensitivity 0.81, specificity 0.79 for advanced fibrosis at the paired 9.7 kPa cutoff | **Selected as PRIMARY** |
| **9.7 kPa** | Advanced fibrosis (≥F3) | Same meta-analysis, Youden-optimal | Retained as a distinct SECONDARY (severity-graded) outcome, not a sensitivity variant of the primary question |
| 10.0 kPa | Advanced fibrosis / "clinically significant advanced chronic liver disease" (cACLD) rule-of-thumb | Practical round-number heuristic; literature range for advanced fibrosis spans 6.8–13.6 kPa per an editorial on cutoff heterogeneity (e-cmh.org) | Not selected; 9.7 kPa preferred as the more rigorously derived estimate for the same clinical concept |
| 12.0 kPa | Cirrhosis (F4) round number | Practical heuristic | Not selected |
| **13.6 kPa** | Cirrhosis (F4) | Same meta-analysis, Youden-optimal | Retained as a distinct SECONDARY (severity-graded) outcome |

**A NHANES-specific paper using this exact 2017–March 2020 release** (Luo et al., *J Hepatology* 2024)
was identified but its exact fibrosis-kPa cutoff choice could not be independently confirmed (fulltext
access blocked during Phase 1 research) — noted for Phase 3 follow-up if a direct comparison to that
paper's reported prevalence becomes relevant, but not used to select the threshold here.

## Decision

> **PRIMARY OUTCOME: Significant liver fibrosis, defined as `LUXSMED ≥ 8.2 kPa`, measured on a
> quality-valid (`LUAXSTAT==1`) elastography exam, binary (positive/negative).**

**Unit:** kPa (kilopascals), median liver stiffness by VCTE.
**Population/context:** General U.S. adult population (NHANES-representative), not a referred
hepatology-clinic population — the meta-analytic cutoff was derived predominantly from
NAFLD/MASLD-referred cohorts, which may have higher pretest fibrosis probability than a general
population sample; this is a **named limitation**, not grounds to pick a different, less-evidenced cutoff.
**Expected prevalence in the primary cohort:** 9.31% (666/7,153 — see `phase2_outcome_prevalence.csv`).

## Secondary / Sensitivity Outcomes (frozen now, not decided post-hoc)

- **SENSITIVITY (same clinical concept, alternate cutpoint):** `LUXSMED ≥ 8.0 kPa`. Assesses robustness of
  conclusions to the primary threshold's exact value given the two cutpoints differ by only 0.2 kPa;
  provides comparability with the majority of prior VCTE literature that uses this round number.
- **SECONDARY (distinct, ordinal severity question):** `LUXSMED ≥ 9.7 kPa` (advanced fibrosis, ≥F3) and
  `LUXSMED ≥ 13.6 kPa` (cirrhosis, F4). These are not sensitivity analyses of the primary question — they
  answer a different clinical question (fibrosis *severity* staging rather than significant-fibrosis
  detection) and will be analyzed as a distinct ordinal/multi-threshold secondary outcome in Phase 3.

## Non-Negotiable Constraints Honored

This threshold was selected using only clinical-literature evidence gathered before this document was
written. It was **not** selected by, and will **not** later be changed based on, class balance, AUC,
subgroup balance, or any other model-performance consideration (non-negotiable rules 2 and 4). Any future
change to this definition after model training begins must be logged as an explicit protocol amendment in
`PHASE2_PROTOCOL_FREEZE.md`.
