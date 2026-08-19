# MI Closure Reconciliation — Pre-Closure Snapshot

**Generated:** 2026-08-19, live, before any file in this closure task was modified. This snapshot
precedes `MI_CLOSURE_RECONCILIATION_REPORT.md` and is not overwritten by any earlier snapshot
(`documentation/sensitivity/multiple_imputation_pre_execution_snapshot.md` remains a separate,
independent record of the original MI task's pre-execution state).

| Item | Value |
|---|---|
| Git HEAD | `adc9328b3b448d43baa89182e7672a2a22c574ba` |
| Branch | `main` |
| Working-tree status | Clean (no uncommitted changes) |
| Deferred roadmap SHA-256 | `a8f328413973dc839b9243c1b343613ae6a3b6ba3cef3f1a21e29f81fdb1b2f9` |
| Original Phase-2 sensitivity-plan SHA-256 (`documentation/phase2/sensitivity_analysis_plan.md`) | `0110c749578212022305ba1abcbb279c3256d35f269ad2e0ddff08709984606b` |
| MI Commit B | `4802602b6b0888b99b184e7ee9666211530ff832` |
| MI Commit C | `f73ef9154a8e23d4aaa9701675b08aefe8434db6` |
| MI Commit D | `adc9328b3b448d43baa89182e7672a2a22c574ba` |
| MI final-report SHA-256 | `5ceca9ceb30b1056685d944bdcb83c032eae434a8629453576838819f23a7d9d` |
| Amendment-registry SHA-256 | `789a897f345cebefa6d7726c79b6bfaa7c09615ab1c7448d6cc1a809e6ea5f8e` |
| Locked test-set (`data/processed/splits/test_ids.csv`) SHA-256 | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |

The test-set hash above is identical to the value recorded and verified in Phase 6
(`tests/test_uncertainty_pipeline.py` TEST4: `t_row["sha256"] == "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779"`), confirming the locked test set is byte-identical to its Phase-6-frozen state as of this closure task's start — before any Part 6 (test-set-touch audit) investigation below.
