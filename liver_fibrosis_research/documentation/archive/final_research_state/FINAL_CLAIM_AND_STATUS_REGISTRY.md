# Final Claim and Status Registry

**Repository:** `liver_fibrosis_research`  
**Mode:** read-only consolidation. No pre-existing artifact was modified.

## Authority hierarchy

1. Result artifacts explicitly identified as final/frozen/authoritative.
2. Final audits/attestations, with later reconciliation only where explicitly documented.
3. Protocol, lineage, audit, and source-script records.
4. Historical/stale reports are preserved and cannot override documented reconciliation.
5. Recency alone never establishes authority.

Machine registry: `results/final_research_state/FINAL_CLAIM_AND_STATUS_REGISTRY.csv`. Required missing-evidence tokens are `NOT FOUND IN REPOSITORY`, `CONFLICT UNRESOLVED IN REPOSITORY`, and `LINEAGE NOT FOUND IN REPOSITORY`.

## Exact authority taxonomy

`AUTHORITATIVE`; `VERIFIED_WITH_LIMITATIONS`; `EXPLORATORY`; `SUPERSEDED`; `NOT_EXECUTED`; `SEPARATE_WORK`. Legacy labels in source artifacts are preserved, not silently rewritten.

## Exact manuscript taxonomy

`MANUSCRIPT_READY`; `MANUSCRIPT_READY_WITH_QUALIFICATION`; `EXPLORATORY_ONLY`; `NOT_USABLE`; `NOT_EXECUTED`; `SEPARATE_WORK`.

## Required domains A–AB

The CSV contains one row for every required domain A through AB, plus detailed claim rows for primary results, corrected/invalid BMI work, Phase 5 MI, Project Phase 7, temporal/external work, AFCP, joint mitigation, and M4b. Domains follow `documentation/end_to_end/archive/END_TO_END_REPORT_v1_20260818.md` / the final master synthesis: objective, protocol, handoffs, cohort/outcome/predictor consistency, leakage, inference, reproducibility, dependency, tests, and remaining issues.

## Critical decisions

Historical Phase 3 and Phase 4 BMI-calibration outputs are `SUPERSEDED`; current corrected Phase 3 and Phase 4 are separate `VERIFIED_WITH_LIMITATIONS`. Phase 5 MI conformal is `VERIFIED_WITH_LIMITATIONS`; its descriptive conclusion is accepted, but executable lineage is `LINEAGE NOT FOUND IN REPOSITORY`. Project Phase 7 retains its original FDR-gated Mondrian conformal objective and is not a BMI classification-mitigation result. Temporal validation is completed separate work with final status **PARTIAL TEMPORAL REPLICATION**, not unfinished non-validation work and not external validation. External validation is separate and `NOT_EXECUTED`.
