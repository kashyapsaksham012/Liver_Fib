# Phase Numbering Crosswalk

**Generated:** 2026-08-18

**Purpose:** This project uses TWO different phase-numbering systems that must never be
conflated without explicit disambiguation:

1. **Project-record numbering** (this codebase's actual freeze structure — "Phase 1," "Phase 2,"
   "Phase 3" as used in `PHASE1_DATA_ASSEMBLY_REPORT.md`, `PHASE2_ANALYTICAL_PROTOCOL_AND_FEASIBILITY_REPORT.md`,
   `PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md`) — 3 phases completed so far.
2. **Mentor's research-plan numbering** (`info.md`, the original 15-phase thesis plan) — 15
   phases, of which only a subset map cleanly onto each project-record phase.

**Rule going forward:** every phase report in this project must state which system it uses in
its title/header. Project-record reports use "Phase N" alone; any reference to the mentor's
plan must say "mentor Phase N" explicitly, never bare "Phase N" when ambiguity is possible.

## Crosswalk Table

| Project-record phase | Status | Mentor `info.md` phase(s) covered | Mentor phase title(s) |
|---|---|---|---|
| **Project Phase 1** — Data Assembly & Remediation | COMPLETE AND FROZEN | Mentor Phase 1 (fully) + Mentor Phase 2 (fully, as feasibility/cohort-flow/subgroup-feasibility audits) | "Data assembly" + "Dataset feasibility audit" |
| **Project Phase 2** — Analytical Protocol & Feasibility Freeze | COMPLETE AND FROZEN | Mentor Phase 3 (outcome definition — protocol only) + Mentor Phase 4 (predictor selection — protocol only) + Mentor Phase 5 (preprocessing — protocol only, not executed) + Mentor Phase 7 (validation strategy — protocol only) + partial Mentor Phase 9/10/11/12 (calibration/fairness/statistical-testing/uncertainty METRIC DEFINITIONS only, not execution) | "Define the outcome" + "Select predictors" + "Data preprocessing" (protocol) + "Validation strategy" (protocol) + partial "Evaluate calibration" / "Fairness audit" / "Statistical testing" / "Uncertainty quantification" (definitions only) |
| **Project Phase 3** — Model Development & Baseline Results (original + remediation) | COMPLETE AND FROZEN | Mentor Phase 5 (preprocessing — EXECUTED) + Mentor Phase 6 (train baseline models) + Mentor Phase 7 (validation strategy — EXECUTED) + Mentor Phase 8 (evaluate discrimination) | "Data preprocessing" (execution) + "Train baseline models" + "Validation strategy" (execution) + "Evaluate discrimination" |
| **Project Phase 4** (not yet started) — Calibration | NOT STARTED | Mentor Phase 9 | "Evaluate calibration" |
| **Project Phase 5** (not yet started) — Fairness | NOT STARTED | Mentor Phase 10 (+ relevant parts of Mentor Phase 11, statistical testing of subgroup disparities) | "Fairness audit" (+ "Statistical testing") |
| **Project Phase 6** (not yet started) — Uncertainty | NOT STARTED | Mentor Phase 12 | "Uncertainty quantification" |
| **Project Phase 7** (not yet started, conditional) — Mitigation | NOT STARTED (only if disparities found) | Mentor Phase 13 | "Mitigation" |
| **Project Phase 8** (not yet started) — Generalization | NOT STARTED | Mentor Phase 14 | "Generalization" |
| (ongoing, not a discrete future phase) — Reproducibility | CONTINUOUSLY APPLIED since Project Phase 1 | Mentor Phase 15 | "Reproducibility" |

## Notes

- Mentor Phase 11 ("Statistical testing") is split across two project phases: its
  multiple-comparison/FDR machinery was already built and used in Project Phase 3 (baseline
  model comparison — see `documentation/phase3/inference_methodology_amendment.md`); its
  application to subgroup fairness disparities belongs to the future Project Phase 5 (Fairness).
- Mentor Phase 15 ("Reproducibility") is not treated as a discrete future project phase because
  reproducibility requirements (seed recording, environment pinning, hash verification, clean
  reruns) have been enforced continuously since Project Phase 1 and are re-verified at every
  phase freeze — see `documentation/phase3/reproducibility_registry.md` and
  `reproducibility_audit.md` for the most recent instance.
- This table itself is the single source of truth for phase-number disambiguation. Any future
  document that needs to reference both systems should cite this file rather than restating
  the mapping.
