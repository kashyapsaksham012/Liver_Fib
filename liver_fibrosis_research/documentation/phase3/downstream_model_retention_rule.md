# Downstream Model-Retention Rule

**Generated:** 2026-08-18 17:00:00

## What Phase 2 froze

`documentation/phase2/model_development_protocol.md`, Part 7 (Model selection rule): *"Best cross-validated ROC-AUC within each model family selects that family's hyperparameters; no family is declared 'the' final model in Phase 2 ... Phase 3 will report all four families'"* [sic — five, including MLP] *"calibration/fairness/uncertainty profiles rather than picking one 'winner' on discrimination alone."*

**This IS a pre-specified retention rule, written and frozen in Phase 2 -- before any Phase 3 model was trained.** It directly answers Part 3X's question: Option A ("Retain all model families for later calibration/fairness/uncertainty evaluation") applies, and it applies because Phase 2 said so, not because this remediation is choosing it now to avoid picking a winner.

## Confirmation this was not violated

No script anywhere in Phase 3 (original or remediated) drops, deprioritizes, or silently excludes any of the 5 original model families based on test-set discrimination. The FDR-corrected model comparison (Section W of the final report) is diagnostic/descriptive, not a filtering step.
