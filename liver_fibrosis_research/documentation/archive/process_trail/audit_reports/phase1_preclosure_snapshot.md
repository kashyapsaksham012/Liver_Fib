# Phase 1 Pre-Closure Snapshot

**Generated:** 2026-08-18 (Phase 1 Closure, Part A)
**Purpose:** Record the exact state of the project immediately before the Phase 1 closure/reconciliation
pass began, so all prior evidence remains traceable and nothing is silently overwritten.

## Git State

- **Last commit (HEAD) at start of this closure pass:** `53ce94784c425e30942c22e32481187b7e516ab4` — "Phase 1: data assembly pipeline, audit reports, master dataset"
- **Working tree status:** the working tree already contained substantial uncommitted remediation work from the prior (pre-closure) Phase 1 remediation pass (91 modified/added files per `git status`) — this closure pass builds on that uncommitted state, per instruction not to restart the pipeline unnecessarily. No commits were made by this closure pass (per standing instruction to only commit when explicitly asked).

## Prior Report Checksum (archived before regeneration)

- **File:** `PHASE1_DATA_ASSEMBLY_REPORT.md` (pre-closure version)
- **SHA-256:** `ff3d5229786dcf72714c03c4277069d28d087852c35795cd426dee157fac7a04`
- **Archived copy:** `documentation/audit_reports/archive/PHASE1_DATA_ASSEMBLY_REPORT_pre_closure_20260818.md`
- Also archived: `archive/cohort_flow_pre_closure.csv`, `archive/broad_vs_fasting_cohort_pre_closure.csv` (the two files containing the numbers later reconciled in Closure Phases C/D).

## Issues Identified At Pre-Closure (from the prior report and user audit)

1. Fasting cohort count conflict: 4,376 (cohort_flow.csv, "fasting labs available" branch) vs 4,336
   (broad_vs_fasting_cohort.csv, "Cohort B") — same ambiguous label, two different filter sets.
2. Broad cohort count conflict: 8,880 (Cohort A) vs 8,805 ("combined broad cohort") — same issue.
3. No single canonical cohort-definition module existed; each script recomputed masks independently.
4. `phase2_open_decisions.md` and `phase1_denominator_registry.csv` did not yet exist as dedicated files
   (the prior report's Section S covered open decisions only as an unstructured bullet list).
5. Subgroup outcome feasibility used only a text caveat, not a structured feasibility classification
   (primary/exploratory/limited-precision/insufficient).

## Disposition

All prior audit outputs (raw file inventory, SEQN linkage, merge audit, special-missing-code audit,
laboratory plausibility audit, leakage audit, race/ethnicity verification, Table 1, all figures, all
internal validation tests) were reviewed and found NOT to require rework — they are retained unchanged
by this closure pass except where explicitly noted below. Only the cohort-flow and broad-vs-fasting
scripts (07, 13) were restructured to resolve the two traced discrepancies, plus new deliverables added
per the closure requirements (cohort definition table, denominator registry, discrepancy trace tables,
Phase 2 open-decisions document, LUX quality-rule source document, enhanced subgroup feasibility
classification).
