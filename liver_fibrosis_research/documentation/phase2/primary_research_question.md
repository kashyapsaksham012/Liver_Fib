# Primary Research Question (Phase 2B)

**Generated:** 2026-08-18

## Primary Research Question

> In adults from the NHANES 2017–March 2020 pre-pandemic sample with a quality-valid transient
> elastography exam, how accurately, how well-calibrated, how fairly across demographic subgroups, and
> how appropriately uncertainty-aware are standard machine-learning models that predict significant
> liver fibrosis (VCTE-defined, LUXSMED ≥ 8.2 kPa) using routinely available demographic, anthropometric,
> and laboratory predictors?

### Elements

- **POPULATION:** Adults (age ≥ 18y) with a non-missing LUXSMED, an NHANES-official quality-valid
  elastography exam (`LUAXSTAT==1`), and complete broad-laboratory + BMI + sex data (primary cohort,
  N=7,153 — see `primary_cohort_decision.md`).
- **PREDICTORS:** Age, sex, BMI, ALT, AST, albumin, ALP, total bilirubin, platelets, HDL cholesterol —
  10 variables available from a single non-fasting clinical visit (see `phase2_predictor_registry.csv`).
- **TARGET:** Binary significant-fibrosis outcome, LUXSMED ≥ 8.2 kPa (see `primary_outcome_definition.md`).
- **TIME/SETTING:** All predictors are assumed available at the same clinical encounter as, and
  logically prior to, the elastography exam that generates the outcome label (see
  `prediction_time_and_leakage_protocol.md`) — i.e. a cross-sectional "if I had routine labs and
  demographics for this patient today, could I flag elevated fibrosis risk before ordering elastography."
- **COMPARISON:** Standard ML model family (Logistic Regression, Random Forest, XGBoost/LightGBM, simple
  MLP — per the original research plan, `info.md` Phase 6); models are not this project's novelty and are
  not compared against each other as a primary aim.
- **EVALUATION:** Discrimination (ROC-AUC primary), calibration (intercept/slope/Brier), fairness
  (subgroup AUC/sensitivity/FNR/calibration disparity), and uncertainty (conformal prediction coverage) —
  see `evaluation_metrics_protocol.md`, `fairness_definition.md`, `uncertainty_protocol.md`.

## Secondary Research Questions

1. Does restricting the elastography-quality requirement to `LUAXSTAT==1` (vs. accepting any non-missing
   LUXSMED) materially change the analytical population's composition or conclusions? (sensitivity cohort)
2. Does extending the predictor set to fasting glucose and triglycerides (secondary architecture, N=3,582)
   change discrimination/calibration/fairness conclusions relative to the broad-lab-only primary architecture?
3. Are conclusions robust to the exact significant-fibrosis threshold (8.0 vs. 8.2 kPa) or to using
   advanced-fibrosis (≥9.7 kPa) / cirrhosis (≥13.6 kPa) as alternative severity-graded outcomes?
4. Does including adolescents (12–17y, P_LUX's own target population) change feasibility or conclusions
   relative to the adult-only primary population?

## Primary Hypothesis

**H1 (accuracy):** Standard ML models will achieve moderate discrimination (ROC-AUC in the 0.75–0.85
range) for significant fibrosis using routine demographic and laboratory variables, consistent with
prior liver-fibrosis ML literature using similar non-invasive predictor panels.

**H2 (calibration):** At least one model will show measurable miscalibration (calibration slope
meaningfully different from 1, or calibration intercept meaningfully different from 0) even where
discrimination (AUC) appears acceptable.

**H3 (fairness):** At least one demographic subgroup (sex, race/ethnicity, age, or BMI group) will show a
statistically and/or clinically meaningful difference in sensitivity, false-negative rate, or calibration
relative to the reference group.

## Secondary Hypotheses

**H4 (uncertainty):** Split conformal prediction will achieve empirical coverage close to its nominal
target (e.g. 90%) in the overall primary cohort, but subgroup-specific coverage may deviate from nominal,
particularly for lower-N subgroups (e.g. Non-Hispanic Asian, N=866 in the primary cohort; Underweight
BMI, N=109).

**H5 (mitigation, only if H3 is confirmed):** Post-hoc calibration or fairness-mitigation methods will
reduce identified disparities but may trade off against overall discrimination or calibration.

## Estimand / Target Quantity

The primary estimand is the **model-predicted probability of significant liver fibrosis (LUXSMED ≥ 8.2
kPa) at the time of a routine clinical visit**, evaluated against the observed elastography-derived label,
in the target population of NHANES-representative U.S. adults undergoing routine laboratory evaluation.
This is a **prediction estimand**, not a causal estimand — no causal claim about any predictor's effect on
fibrosis risk is made or supported by this study design (non-negotiable rule 17).
