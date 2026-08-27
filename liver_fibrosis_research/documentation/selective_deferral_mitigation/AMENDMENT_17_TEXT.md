# Protocol Amendment #17

**Date:** 2026-08-27
**Title:** Selective-deferral mitigation of the subgroup conformal-reliability failure.

**Change.** The FDR-gated Mondrian mitigation (Project Phase 7) and the structured mitigation
battery (BMI-investigation Phases 3–7) evaluated interventions against an acceptance gate that
assumes the model issues a final classification, so any subgroup-specific threshold shift is
charged as a full-cohort specificity loss; none produced an acceptable multi-metric fix. This
amendment adds a **post-hoc selective-deferral decision layer** on top of the frozen five model
families and the frozen split-conformal calibration set. Cases whose conformal prediction set is
ambiguous, or whose nonconformity score exceeds a group-conditional threshold, are **deferred to
vibration-controlled transient elastography**, mirroring the first step of the standard FIB-4 →
VCTE referral pathway. Because a deferral costs an elastography referral rather than full-cohort
specificity, the acceptance gate is re-specified (retained-population subgroup conformal coverage
and sensitivity gap; deferral-rate equity; an elastography-referral budget) and pre-registered in
full in `SELECTIVE_DEFERRAL_MITIGATION_PLAN.md` §Gate **before any locked-test access**.

**What does not change.** No model is retrained; no hyperparameter is searched; no predictor or
outcome is added or altered. The analysis operates entirely on the frozen Phase-6 conformal
artifacts (`results/uncertainty/calibration_scores_*.csv`, `test_set_prediction_sets.csv`,
`conformal_thresholds_by_model.csv`); the frozen models are not loaded. The deferral rule is
developed on the conformal-calibration partition (N = 1,002) only, frozen with a hashed manifest,
and confirmed on the CAND_1 locked test **once**.

**Verdict.** Read mechanically off the pre-registered gate: FULL / QUALIFIED / PARTIAL SUCCESS, or
BOUNDED NEGATIVE, or DEVELOPMENT-STAGE NEGATIVE. Whichever it is, it is reported without gate
relaxation. `DO_NOT_CLAIM.md` is updated to forbid overclaiming the tier.

**Scope note.** CAND_2 / CAND_3 replication (gate criterion G9) requires re-deriving each cohort's
conformal machinery, which needs the model-fitting stack; that stack is not available in the
current environment. The CAND_1 result is therefore a QUALIFIED SUCCESS at best in this pass, with
G9 replication recorded as the single remaining step.

**Method novelty.** None claimed. The stack (calibrated probabilities + split conformal +
group-conditional / cost-aware deferral for clinical triage) is published — *Sci Rep* 2026,
`10.1038/s41598-026-40637-w`. This is an application-level contribution on the routine-data
fibrosis-triage task.

**Test-set touches.** One additional touch of the CAND_1 locked test (Phase 4). Recorded in
`documentation/phase3/test_set_lock.md` and this registry. The project-wide pooled-FDR family
count is updated in Phase 8.

**Sub-amendment #17a (conditional, not triggered unless stated in `PHASE1_2_DEV_AND_BASELINE.md`).**
If a subgroup calibration cell is < 50 cases or < 15 positives, or the subgroup under-coverage
does not reproduce on the calibration partition, re-split the training partition 70/30 into
proper-train / conformal-calibration and refit the five models with the frozen Phase-3
hyperparameters (no search) to give the subgroups adequate calibration points. Requires the
model-fitting stack; deferred if unavailable.
