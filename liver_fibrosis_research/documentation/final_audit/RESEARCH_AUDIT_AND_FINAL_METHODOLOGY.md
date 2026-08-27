# Research Audit and Final Methodology

**Status:** Consolidation document. Produced by re-verifying every numeric claim below directly
against the repository's own frozen result files and source code — not by trusting any external
summary, including a prior independent audit conducted in a separate tool session on this same
repository. Where that external audit's claims disagreed with the repository, the discrepancy is
recorded explicitly in Part I rather than silently corrected.

This document is a **synthesis and index**, not a replacement for the phase-by-phase reports it
points to. Every number here is sourced; where a number could not be independently re-derived from
a raw file in this pass, it is labeled "per `<report>`" rather than presented as freshly verified.

---

## A. Research objective

> In adults with a quality-valid transient elastography (VCTE/FibroScan) exam, how accurately,
> fairly, and reliably can routine demographic, laboratory, and clinical predictors identify
> significant liver fibrosis (`LUXSMED ≥ 8.2 kPa`) — and specifically, do class-imbalance training
> techniques, demographic subgroup boundaries, and split-conformal uncertainty guarantees hold up
> once probability calibration, subgroup fairness, and prediction-set coverage are examined, not
> just discrimination (AUC)?

The study's stated novelty is not raw discrimination — five model families land within a narrow,
statistically indistinguishable AUC band (0.8229–0.8429, see Part B.3) — but the finding that a
model can look acceptable on AUC and even on aggregate calibration while still failing coverage
guarantees for identifiable demographic subgroups, and that group-wise mitigation can partially,
not fully, repair this.

## B. Phase-by-phase methodology and verified results

### B.1 — Phase 1: Data assembly
- Source: NHANES 2017–March 2020 pre-pandemic combined release (`P_DEMO`, `P_BMX`, `P_BIOPRO`,
  `P_CBC`, `P_GLU`, `P_TRIGLY`, `P_HDL`, `P_LUX`).
- Anchor cohort (transient elastography attempted, non-missing outcome): N=10,409.
- Full detail: `../../PHASE1_DATA_ASSEMBLY_REPORT.md`.

### B.2 — Phase 2: Protocol freeze
- Primary cohort: `CAND_1_QUALITYVALID_ADULT_BROAD`, N=7,153, 666 positive (9.31% prevalence).
- Outcome: `LUXSMED ≥ 8.2 kPa` on a quality-valid exam (`LUAXSTAT==1`), binary. Threshold sourced
  from a 2024 VCTE-vs-MRE meta-analysis Youden cutoff, frozen **before** any model was trained —
  see `../phase2/primary_outcome_definition.md`.
- Predictors (10, frozen before training): `RIDAGEYR`, `RIAGENDR`, `BMXBMI`, `LBXSATSI` (ALT),
  `LBXSASSI` (AST), `LBXSAL` (albumin), `LBXSAPSI` (ALP), `LBXSTB` (bilirubin), `LBXPLTSI`
  (platelets), `LBDHDD` (HDL) — `../../results/tables/phase2_predictor_registry.csv`.
- Race/ethnicity (`RIDRETH1`/`RIDRETH3`) is **excluded as a model input** and **retained only for
  post-hoc fairness stratification** — an explicit, separately-documented design decision, not an
  oversight (`phase2_predictor_registry.csv` inclusion-decision column).
- Selection-bias finding, frozen at protocol time: Non-Hispanic Black participants are 41.30% of
  cohort exclusions vs. 24.98% of the retained cohort — **VERIFIED** live from `_cohorts.py` +
  master parquet in this audit pass.
- Full detail: `../../PHASE2_ANALYTICAL_PROTOCOL_AND_FEASIBILITY_REPORT.md`.

### B.3 — Phase 3: Baseline models
70/30 stratified split (train N=5,007 / locked test N=2,146, both ≈9.31% prevalence), 5-fold
`StratifiedKFold(shuffle=True, random_state=42)` for tuning, five model families evaluated
head-to-head. **All figures below re-verified in this audit directly against
`results/tables/phase3_final_baseline_results.csv` and `phase3_model_comparison_fdr.csv`** — exact
match, no discrepancy:

| Model | Test AUC | Youden threshold | Class-imbalance handling |
|---|---:|---:|---|
| Logistic Regression | 0.8334 | 0.5173 | `class_weight="balanced"` |
| Random Forest | 0.8343 | 0.4499 | `class_weight="balanced"` |
| XGBoost | 0.8429 | 0.4108 | `scale_pos_weight` (≈9.74) |
| LightGBM | 0.8394 | 0.4988 | `scale_pos_weight` (≈9.74) |
| MLP | 0.8229 | 0.1065 | none (sklearn `MLPClassifier` has no native weighting API) |

No pairwise model comparison was significant after Benjamini–Hochberg FDR correction (10/10 pairs,
`significant_after_fdr_0.05 = False`). A sensitivity variant, **MLP Balanced** (`RandomOverSampler`
inside an `imblearn` training-fold-only pipeline), was run to isolate whether the probability
distortion in B.4 is caused by balancing itself, independent of *how* it's implemented — see B.4.
`results/model_comparison/` does **not exist** in this repository; this is the corrected location
for anyone (human or AI) looking for final Phase 3 numbers.
Full detail: `../../PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md`.

### B.4 — Phase 4: Calibration and recalibration
**Finding:** the four class-balanced models (LR, RF, XGBoost, LightGBM) show severe raw
overprediction — OOF calibration intercepts of −1.86 to −2.24 (`results/calibration/
primary_metrics_by_model.csv`, N=5,007, re-verified exact match in this audit). The unweighted MLP
does not (intercept −0.28). When oversampling is introduced into MLP as a sensitivity check
(MLP Balanced), the same distortion reappears (OOF intercept ≈ −2.16, per
`PHASE4_CALIBRATION_RESULTS_REPORT.md` — this specific model's own dedicated calibration-metrics
row was not re-located in `primary_metrics_by_model.csv` during this audit pass and should be
treated as "per report" rather than freshly re-verified from a raw CSV; see Part I).

**Mechanism:** class balancing trains the model against an implicit 50:50 prior; the true
population prior is ≈9.31%. The Bayesian log-odds correction for this prior mismatch is
log(0.0931/0.9069) ≈ −2.27 — matching the observed intercepts almost exactly. This is presented in
the frozen report as the primary explanation, not a certainty about every last percentage point of
the shift (secondary contributors such as Random Forest's bagging-induced slope compression are
also noted).

**Correction:** Platt (logistic) recalibration — `LogisticRegression(C=1e10)` fit on `logit(p_raw)`
against OOF labels only — fit exclusively on out-of-fold predictions, frozen, then applied once to
the locked test set. Isotonic regression was considered and rejected (Amendment #8) given only 466
OOF positive cases, which would produce unstable step-function artifacts.

**Locked test-set result** (N=2,146, re-verified exact match against
`results/calibration/test_set_calibration_final.csv`):

| Model | Raw intercept → Recal. | Raw Brier → Recal. | Raw ECE → Recal. | AUC (unchanged) |
|---|---|---|---|---:|
| Logistic | −2.2602 → −0.1537 | 0.1755 → 0.0705 | 0.2967 → 0.0172 | 0.8334 |
| Random Forest | −1.9679 → +0.0238 | 0.1458 → 0.0709 | 0.2452 → 0.0113 | 0.8343 |
| XGBoost | −2.1629 → +0.1241 | 0.1557 → 0.0694 | 0.2572 → 0.0152 | 0.8429 |
| LightGBM | −2.1846 → +0.1418 | 0.1603 → 0.0696 | 0.2638 → 0.0143 | 0.8394 |
| MLP | −0.4354 → −0.1189 | 0.0716 → 0.0715 | 0.0290 → 0.0264 | 0.8229 |

AUC is unchanged by construction (Platt scaling is a monotonic transform of the logit). **The
Platt-recalibrated test probabilities are the correct baseline to carry forward into fairness and
uncertainty analysis** — this is stated in the frozen Phase 4 report and is consistent with how
Phases 5–7 actually use these predictions.
Full detail: `../../PHASE4_CALIBRATION_RESULTS_REPORT.md`, `../../PHASE4_CLOSURE_VERIFICATION_REPORT.md`.

### B.5 — Phase 5: Demographic fairness
Subgroup dimensions: sex, race/ethnicity (`RIDRETH3`), age band (18–39/40–59/60+), BMI band
(Underweight/Normal/Overweight/Obese). Metric: sensitivity (true-positive rate) disparity vs. a
reference subgroup, tested with bootstrap CIs and Benjamini–Hochberg FDR correction within each
model×dimension family.

- **BMI**: Normal-BMI sensitivity is 27.1–48.0 percentage points lower than Obese-BMI, FDR-significant
  in **all 5 models** (p ≤ 0.006). BMI-Underweight showed a nominally large FDR-flagged deficit but
  is excluded from interpretation — it contains only 1 positive case, insufficient for any
  conclusion.
- **Age**: Age-60+ sensitivity is lower than Age-40–59 in all 5 models, but is FDR-significant in
  **only 4 of 5** — Random Forest (−13.2pp), XGBoost (−11.2pp), LightGBM (−14.1pp), and MLP
  (−14.7pp). **Logistic Regression's Age-60+ disparity does not reach FDR significance.** This
  detail matters directly for Phase 7 (B.7): Logistic receives no Age-based mitigation rule because
  Age was never flagged significant for it in the first place, not because of an oversight.
- Selection-bias finding (B.2) is a *cohort-composition* fact, separate from the *model-fairness*
  finding above — the two must not be conflated into one claim.
Full detail: `../../PHASE5_FAIRNESS_RESULTS_REPORT.md`.

### B.6 — Phase 6: Split conformal prediction
Architecture: proper-train N=4,005 (373 positive, 9.313%) → conformal-calibration N=1,002 (93
positive, 9.281%) → locked test N=2,146. Nominal target 90%; calibration quantile index k=903
(⌈(n+1)(1−α)⌉ on the N=1,002 calibration set — k and N are different quantities, not conflicting
figures).

- Marginal (overall) coverage: 88.12%–90.82% across the 5 models — acceptable.
- **Subgroup coverage failure**: BMI-Obese falls to 76.8%–82.3%, Age-60+ falls to 81.1%–85.6%, both
  with Wilson CIs excluding the 90% target, across all 5 models. This is the central empirical
  finding motivating Phase 7.
- Efficiency: MLP achieves 96.9% singleton prediction sets; the class-weighted models produce far
  more ambiguous "both classes possible" (doubleton) sets, 23.2%–43.2% of the time — a direct
  downstream consequence of the raw miscalibration in B.4 (better-calibrated probabilities produce
  tighter, more useful conformal sets; conformal coverage itself does not *require* calibration to
  be valid, but its *efficiency* does benefit from it).
Full detail: `../../PHASE6_UNCERTAINTY_RESULTS_REPORT.md`, `../../PHASE6_CLOSURE_CLARIFICATION_REPORT.md`.

### B.7 — Phase 7: Mondrian (group-wise) mitigation
Mitigation was applied **only** to the two subgroup-dimension combinations that were FDR-significant
in **both** Phase 5 and Phase 6: BMI-Obese and Age-60+ (per-model, so Logistic — which had no
significant Age-60+ finding — received a BMI-only rule, not an Age rule).

- **5 of 9** qualifying model×subgroup combinations achieved nominal coverage after mitigation; the
  remaining 4 did not: RF/Obese, XGBoost/Obese, LightGBM/Obese, LightGBM/60+.
- XGBoost's overall marginal coverage rose to 93.4% post-mitigation (+5.27pp over its Phase 6
  baseline), which **breaches** the study's own pre-specified ±5pp marginal-coverage tolerance —
  documented as a genuine limitation, not smoothed over.
- **Overlap correction (verified this audit — the pasted-transcript version of this fact was
  imprecise and must not be repeated as stated):** the BMI-Obese ∩ Age-60+ intersection is **294
  people (13.7% of the test set)**, not 62%. The figure "62%" refers to a *different* quantity —
  the 1,330 people (62.0%) who fall into **at least one** of the two target groups (589 Obese-only +
  447 Age-only + 294 both). Reporting "294 people (~62%)" as a single fact, as an external summary
  of this repository did, incorrectly implies the intersection itself is 62% of the cohort.
- For the 294-person overlap population, the actual mitigation code
  (`src/phase7_04_final_test_touch.py`, `TARGET_COMBINATIONS` list iterated with `after_in_set[mask]
  = sub_in_set`) applies rules in list order — BMI first, Age second — so the **Age-60+ rule
  silently overwrites the BMI-Obese rule** for anyone in both groups. This is a single-rule
  last-write-wins precedence, not a genuine joint/intersectional mitigation, and is documented as
  such in `../mitigation/phase7_bmi_age_overlap_interpretation.md`.
Full detail: `../../PHASE7_MITIGATION_RESULTS_REPORT.md`.

### B.8 — Phase 8: Subgroup-holdout generalization
Non-Hispanic Black participants (N=1,787, 177 positive, 9.905%) withheld entirely from training;
models retrained on the remaining N=5,366 (489 positive, 9.113%) and evaluated on the holdout.

- Discrimination attenuates from the primary 0.8229–0.8429 range to **0.7719–0.7893** on the
  unseen subgroup.
- Calibration becomes materially unstable on the holdout: intercepts −0.577 to −2.169, slopes
  0.636–0.972 (all below 1, i.e. systematic overprediction) — worse and more variable than the
  primary-cohort recalibrated results in B.4.
- Temporal (cross-cycle) external validation was determined infeasible: `SDDSRVYR` is constant
  (66.0) across every record in this NHANES release, so no independent time-split exists within
  the data itself. **No external, non-NHANES validation has been performed at any point in this
  project** — this remains the single most important unaddressed generalization question (see
  `../reliability_extension/external_validation_future_work.md`).
Full detail: `../../PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md`.

## C. Sensitivity analyses actually completed (see `REMAINING_ANALYSES_AND_RESEARCH_STATUS.md` for
the authoritative status table)

Three deferred sensitivity analyses plus a targeted multiple-imputation check were **fully executed
with results**, not merely dataset-constructed — this corrects a scope-framing gap in a prior
external summary of this repository, which implied CAND_2/CAND_3 might still be dataset-only:

1. **8.0 kPa alternative threshold** (same cohort, relabeled outcome only — no retraining/recalibration/
   conformal repeated): AUC 0.8145–0.8326; BMI-Obese disparity strengthens to 35.1–51.6pp
   (still 5/5 significant); Age-60+ direction stays negative in 5/5 but significance drops to only
   2/5 (LightGBM, MLP).
2. **CAND_2, relaxed elastography eligibility** (N=7,639, 804 positive, independently re-split and
   retrained): test AUC 0.8526–0.8572.
3. **CAND_3, fasting-extended architecture** (N=3,582, 319 positive, 12 predictors incl. fasting
   glucose/triglycerides, independently re-split and retrained): test AUC 0.8280–0.8457.
4. **Multiple imputation for the Non-Hispanic Black selection-bias concern** (B.2): recovers 615
   complete-case-excluded participants (MI pool N=7,768) via `IterativeImputer(BayesianRidge,
   sample_posterior=True)`, m=5, fold-embedded, predictive pooling. Overall AUC changes are <0.007
   for all 5 models; NHB-subgroup sensitivity changes are small and none are FDR-significant
   (adjusted p=0.978 for all 5 models — a genuine, verified artifact of BH correction on a 5-member
   family where no unadjusted p-value is small enough to escape the correction ceiling, not a
   coincidence or an error).

**Cross-cutting finding, programmatically compared across all three non-MI sensitivity variants**
(`results/sensitivity/primary_vs_sensitivity_comparison.csv`, 60 rows): the BMI-Obese disparity is
**stable in 15/15** instances across all three sensitivity checks; the Age-60+ disparity's
*direction* never reverses in any instance, but its *statistical significance* is lost in 9 of the
12 instances where it was significant at the primary specification. This is a broader, more
specific finding than "the 8.0 kPa check alone weakens Age-60+ significance" — the attenuation
reproduces across independently-constructed cohorts (CAND_2, CAND_3) and the alternative threshold
alike, which argues the effect is a genuine small-subsample precision issue rather than an artifact
of any one sensitivity design.

Full detail: `../../DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md`,
`../../MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`, `../../MI_CLOSURE_RECONCILIATION_REPORT.md`.

## D. Data lineage (summary — full lineage table in `DATA_AND_RESULT_LINEAGE.csv`)

```
Raw NHANES 2017–March 2020 (.xpt)
  → Phase 1 assembly (N=10,409 elastography-attempted anchor cohort)
  → Phase 2 cohort/outcome/predictor freeze (CAND_1 primary, N=7,153, 9.31% prevalence)
  → Phase 3 70/30 split (train N=5,007 / locked test N=2,146) + 5-fold CV tuning
  → Phase 4 OOF Platt recalibration, applied once to locked test
  → Phase 5 fairness audit on locked (recalibrated) test predictions
  → Phase 6 conformal refit (proper-train N=4,005 / calibration N=1,002) + locked test
  → Phase 7 Mondrian mitigation on the Phase 6 architecture, targeted subgroups only
  → Phase 8 NHB holdout retrain (N=5,366 train / N=1,787 holdout)
  → Sensitivity analyses: 8.0kPa relabel, CAND_2 relaxed-elastography, CAND_3 fasting-extended,
    NHB multiple imputation — each independently constructed/evaluated against the Phase 2–3
    protocol, not silently folded into primary numbers
```

## E. Model lineage (summary — full table in `MODEL_LINEAGE.csv`)

Each of the 5 primary models: 10-predictor input → `SimpleImputer`/`ColumnTransformer`/
`StandardScaler` (LR, MLP only — tree models unscaled) fit strictly inside CV training folds →
class-imbalance handling per B.3 → CV-tuned hyperparameters → OOF probabilities → Platt
recalibration (B.4) → Youden threshold (B.3, re-derived from CV OOF, not from the test set) →
fairness audit (B.5) → conformal refit + calibration (B.6) → Mondrian mitigation where qualifying
(B.7) → NHB holdout retrain (B.8).

## F. Validation architecture

70/30 train/test split → 5-fold `StratifiedKFold` for tuning and OOF generation → locked test set
touched exactly once for final confirmatory evaluation at each phase that needs it (Phase 3
discrimination, Phase 4 recalibration, Phase 5 fairness, Phase 6/7 conformal coverage) → a further
80/20 split of the training partition for Phase 6/7's proper-train/conformal-calibration
architecture → an entirely separate NHB-holdout retrain for Phase 8. No nested double-dipping of
the locked test set was found in this or the prior audit.

## G. Leakage controls (all independently re-verified against source in this audit pass)

| Control | Verified against |
|---|---|
| Preprocessing (imputation, scaling) fit only inside training folds | `phase3_05_train_and_tune.py` |
| Class-imbalance handling (weights/`scale_pos_weight`) applied inside training folds only | `phase3_05_train_and_tune.py` L46–67 |
| `RandomOverSampler` inside `imblearn.Pipeline`, training-fold-only, no SMOTE anywhere in `src/` | `phase3_13_imbalance_audit_and_mlp_sensitivity.py` L96/105 |
| Platt parameters fit on OOF only, frozen before touching test | `phase4_05_recalibration.py` L36–48 |
| Conformal refit models fit on `proper_train_ids.csv` only; quantile thresholds from `conformal_calibration_ids.csv` only | Phase 6 scripts |
| NHB holdout: preprocessing and Youden thresholds re-derived strictly within the holdout-training subset | Phase 8 scripts |
| MI: `IterativeImputer` fit inside CV training folds only; locked test set never loaded in MI construction/evaluation scripts | `mi_02_black_subgroup_comparison.py` |

## H. Isotonic-regression decision (methodology note)

Isotonic regression was explicitly considered and rejected in favor of Platt scaling, on the
grounds that with only 466 OOF positive cases, a non-parametric step function risks unstable,
clinically meaningless step artifacts, while a 2-parameter logistic transform is far less
overfitting-prone at this sample size. Recorded as Protocol Amendment #8
(`../end_to_end/protocol_amendment_registry.md`) and `../../PHASE4_CALIBRATION_RESULTS_REPORT.md`.

## I. Discrepancies found during this audit (not silently corrected — recorded per Rule 32 of the
governing task)

An external AI tool's independent summary of this repository (produced in a separate session, not
part of this repository's own record) was checked number-by-number against the repo in this audit
pass. Almost everything in it matched exactly. Three points did not, and are corrected here:

1. **Age-60+ FDR significance was described as "4/5 models" in one place and implicitly as "all
   models" elsewhere in that external summary.** The repository's own frozen number is **4 of 5**
   (Logistic Regression's Age-60+ disparity is not FDR-significant) — see B.5. This matters because
   it directly explains why Phase 7 gives Logistic no Age-based mitigation rule.
2. **The BMI-Obese ∩ Age-60+ overlap was described as "294 people (~62% of the cohort)."** These are
   two different quantities: 294 people is 13.7% of the test set (the true intersection); 62% (1,330
   people) is the union — anyone in *either* target group. See B.7.
3. **CAND_2 (relaxed elastography) and CAND_3 (fasting-extended) were implied to be dataset-
   construction-only, with results status uncertain.** Both are **fully executed** with independent
   retraining, discrimination, calibration, and BMI/Age fairness comparisons — see Part C.

No other numeric claim checked in this audit (Phase 3 AUCs/thresholds, Phase 4 raw and recalibrated
calibration metrics, Phase 5 BMI disparities, Phase 6 coverage figures, Phase 7's 5/9 resolution
list and XGBoost tolerance breach, Phase 8 holdout metrics, and all MI/threshold sensitivity
figures) showed any discrepancy against the repository's own frozen result files. One number — the
MLP Balanced sensitivity model's own dedicated OOF calibration row — was not re-located in a raw
CSV during this pass and is sourced to `PHASE4_CALIBRATION_RESULTS_REPORT.md` rather than presented
as freshly re-verified; see `FINAL_CLAIM_AUDIT.md` for its status label.
