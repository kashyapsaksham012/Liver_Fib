# Prediction-Time Availability & Leakage Protocol (Phase 2H/2I)

**Generated:** 2026-08-18

## Prediction-Time Definition

> **The model predicts at the moment a patient presents for a routine clinical evaluation with
> demographic information and a standard (non-fasting) laboratory panel, BEFORE any elastography
> examination is performed or known.** This mirrors the clinical use case: flagging elevated fibrosis
> risk from labs a clinician already has, to help decide whether elastography or further workup is
> warranted.

## Per-Predictor Evaluation (finalizing the Phase 1 leakage pre-screen)

Every one of the 10 primary predictors was evaluated against the six Phase 2H questions. Full table:
`results/tables/phase2_final_leakage_registry.csv` (137 variables) and
`results/tables/phase2_predictor_registry.csv` (93 variables with Phase 2 role classification).

| Predictor | Available before elastography? | Derived from outcome? | Encodes FibroScan directly? | Decision |
|---|---|---|---|---|
| RIDAGEYR, RIAGENDR, BMXBMI | Yes (interview/anthropometric, independent exam component) | No | No | ELIGIBLE |
| LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD | Yes (biochemistry/CBC/lipid panel, independent exam component) | No | No | ELIGIBLE |
| LBXGLU, LBXTR | Yes, but fasting-restricted (SECONDARY architecture only) | No | No | ELIGIBLE (secondary) |
| LUXSMED, LUXCAPM | N/A — this IS / directly relates to the outcome measurement | Yes | Yes | **OUTCOME ONLY — excluded** |
| LUAXSTAT, LUXSIQR, LUXSIQRM, LUXCPIQR, LUANMVGP, LUANMTGP | Available at exam time but describes the elastography exam's *own quality*, not an independent clinical measurement | No, but measured in the same exam as the outcome | Indirectly (quality of the outcome measurement itself) | **QUALITY/EXCLUSION ONLY — excluded from predictors, used only for cohort eligibility** |
| BMDSTATS, BMIWT, BMIHT | Anthropometric exam completeness/comment flags | No | No | **QUALITY/EXCLUSION ONLY — excluded** (measurement-quality flags, not clinical predictors) |
| RIDRETH1, RIDRETH3 | Yes | No | No | **SENSITIVITY-ONLY — excluded from the predictor set** (see rationale below), retained for fairness stratification |
| WTMECPRP, WTINTPRP, WTSAFPRP, SDMVPSU, SDMVSTRA | Yes | No | No | **QUALITY/EXCLUSION ONLY — excluded** (survey design/weight variables, not clinical predictors; see `survey_weight_protocol.md`) |
| 64 auxiliary LBX*/LBD* labs not in the curated Phase 1 dictionary | Unknown — not individually source-verified | Unknown | Unknown | **REQUIRES FURTHER VERIFICATION — excluded** (protection rule, Issue 13) |

### Why race/ethnicity is excluded as a model INPUT but retained for fairness EVALUATION

Race/ethnicity is available before prediction and is not outcome-derived, so it is not "leakage" in the
technical sense. It is excluded from the predictor set as a **deliberate fairness-by-design choice**: a
model trained directly on race/ethnicity risks learning a demographic proxy rather than the underlying
biology, and complicates the interpretation of subgroup fairness metrics (a model can be "fair" by
construction if it literally sees group membership and adjusts, which begs the fairness question this
thesis is asking). This decision is revisited, not silently fixed forever — see `sensitivity_analysis_plan.md`.

## No Variable May Enter the Primary Model Until Eligible

The primary predictor set is exactly the 10 variables in `primary_research_question.md` /
`phase2_predictor_registry.csv` marked `PRIMARY MODEL CANDIDATE`. No other variable — including any of
the 64 unverified auxiliary labs — may be added without a documented protocol amendment plus source
verification (enforced by the same TEST22/TEST23-style logic used in Phase 1 closure).
