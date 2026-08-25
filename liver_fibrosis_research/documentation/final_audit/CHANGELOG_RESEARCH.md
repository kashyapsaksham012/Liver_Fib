# Research Changelog

Actual methodological changes only. AI-assisted conversations, external audit sessions, and
literature searches are not recorded here as scientific evidence — only what they caused to be
verified, documented, or (where applicable) changed in the repository itself.

## 2026-08-25 — Independent verification pass + version-control metadata corrections
- **Added**: `documentation/final_audit/INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md` — a
  direct re-read of primary frozen artifacts (baseline results, calibration, fairness, conformal,
  mitigation, holdout, sensitivity, MI, reliability-extension, diagnostics) cross-checking every
  headline number cited in the end-to-end reports. All scientific numbers matched exactly.
- **Corrected (metadata only)**: `COMPLETE_END_TO_END_LIVER_FIBROSIS_RESEARCH_REPORT.md` — the
  "(uncommitted)"/"Untracked" annotations for `joint_intersectional_mitigation.csv`,
  `pooled_fdr_corrected_results.csv`, `intersectional_coverage_ci.csv`, `interpretability_*.csv`,
  `FINAL_EXPERIMENTAL_EVIDENCE_LINEAGE.md`, `sens_07/sens_08`, and `ANALYSIS_MANIFEST_FINAL.csv`
  were stale: commit `142595d` has since committed all of them. A dated correction banner was
  inserted and the four inline labels updated. No scientific claim was altered.
- **Flagged, not reconciled**: the older summary's D06=UNVERIFIED / D07=BLOCKED status vs. the
  later `stage1_decision_report.md` / `COMPLETE_END_TO_END_EXPERIMENTAL_REPORT.md` treating
  D01–D08 as complete; disposition documented in the attestation §2.3.
- **Noted**: `results/tables/final_research_status.csv` row for joint intersectional mitigation
  ("NOT EXECUTED") is superseded by its 2026-08-24 execution (`ITEMS_1_5_REFINEMENT_ADDENDUM.md`
  Item 4 + `FINAL_SCIENTIFIC_STATUS_RECONCILIATION.md`); left unedited per append-only convention.
- **No core pipeline code was modified.** No model retrained or refit; no new test-set scoring.

## 2026-08-24 — Final audit documentation consolidation
- **Added**: `documentation/final_audit/` — `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md`,
  `FINAL_CLAIM_AUDIT.md`, `FINAL_RESEARCH_ARCHITECTURE.md`, `FINAL_RESEARCH_STATUS.md`,
  `REPRODUCIBILITY.md`, `FINAL_SCIENTIFIC_INTERPRETATION.md`,
  `REMAINING_ANALYSES_AND_RESEARCH_STATUS.md`, this changelog.
- **Added**: `results/tables/final_research_status.csv`, `results/tables/data_and_result_lineage.csv`,
  `results/tables/model_lineage.csv`.
- **Added**: `README.md` at the project root, summarizing the research overview and linking to the
  detailed phase reports and the final-audit set.
- **Reason**: consolidate the research record established across Phases 1–8 and all sensitivity
  analyses into a single, cross-linked, independently re-verified index, following an external
  (separate-tool) audit session whose numeric claims needed independent confirmation against this
  repository's own frozen files before being trusted.
- **Verification performed**: every specific number in the external audit session's summary was
  re-checked directly against raw result CSVs and source scripts in this repository (not against
  the external summary's own narrative). Three discrepancies were found and are corrected in
  `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md` Part I: (1) the Age-60+ Phase 5 fairness deficit is
  FDR-significant in 4 of 5 models, not all 5 (Logistic Regression is the exception); (2) the
  BMI-Obese ∩ Age-60+ overlap population is 294 people (13.7% of the test set), not "294 people
  (~62%)" — 62% (1,330 people) is a different quantity, the *union* of the two target groups, not
  their intersection; (3) the CAND_2 (relaxed elastography) and CAND_3 (fasting-extended)
  sensitivity analyses are fully executed with independent retraining and results, not merely
  constructed datasets awaiting analysis.
- **No core pipeline code was modified.** No script under `src/` was changed. No previously
  reported result was altered, recomputed, or reinterpreted beyond the three corrections above,
  which affect only how existing frozen numbers are *described*, not the numbers themselves.
- **No git commit was made as part of this pass** — file creation only, pending explicit
  confirmation to commit.

## Prior history (as found, not re-created here)
The repository's own commit history and existing `PHASE*_REPORT.md`, `*_CLOSURE*.md`,
`CAND4_CLASSIFICATION_RESOLUTION_REPORT.md`, `MI_CLOSURE_RECONCILIATION_REPORT.md`, and
`RELIABILITY_EXTENSION_RESULTS_REPORT.md` files, along with
`documentation/end_to_end/protocol_amendment_registry.md` (14 amendments as of this pass), remain
the authoritative record of every methodological decision, amendment, and closure made before this
consolidation. This changelog does not re-narrate that history; it records only what changed in
this pass.
