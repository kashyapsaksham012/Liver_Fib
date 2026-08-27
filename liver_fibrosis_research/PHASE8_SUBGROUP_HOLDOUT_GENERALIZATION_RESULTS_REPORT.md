# Phase 8 (Generalization) — Subgroup-Holdout Results Report

**Project Phase 8 = Mentor Phase 14 = "Generalization"**

## 1. Official Project Phase 8 definition

`documentation/phase_numbering_crosswalk.md` (row 9): Project Phase 8 = Mentor Phase 14 =
"Generalization." Mentor `info.md` text, quoted in full: *"If your NHANES data support it, perform
a temporal or subgroup validation. For example: train on one portion/cycle, test on another. Or
perform subgroup holdout experiments. Ask: Does performance drop? Which groups are most affected?
Does calibration remain stable?"* No external, independently-sourced dataset is named anywhere in
this text.

## 2. Mentor/project numbering reconciliation

Confirmed via the crosswalk's own governing statement: "This table itself is the single source of
truth for phase-number disambiguation." No discrepancy found — Project Phase 8's title
("Generalization") matches Mentor Phase 14's title exactly.

## 3. Phase 7 handoff status

Phase 7 (Mitigation) completed with documented limitations: partial coverage mitigation (5/9
target combinations fully resolved, 4/9 improved but not fully resolved), no genuine dual BMI+Age
mitigation, XGBoost exceeded its ±5pp marginal-coverage tolerance, prediction-set efficiency
decreased. Non-Hispanic Black was never a Phase 7 mitigation target (confirmed: zero rows for this
category in `results/mitigation/test_set_mitigation_final.csv`).

## 4. Validation objective

Determine whether the 5 frozen model families can generalize to Non-Hispanic Black participants
when that entire subgroup is completely absent from model training — a genuine unseen-group
transportability question, distinct from every prior phase.

## 5. Validation design

**Subgroup-holdout**, the only mentor-authorized design that is data-feasible (Section 6). Not
external validation, not a sensitivity cohort, not an internal train/test re-split of the same
kind Phase 3 already performed.

## 6. Dataset independence — within-release time-split infeasibility

A within-release (cross-cycle) time split, the mentor's other named option, is **not feasible**:
`SDDSRVYR` (NHANES release-cycle code) is a single constant value (66.0) across the entire
2017–March 2020 pre-pandemic combined release used by this project (all 15,560 `P_DEMO.xpt` rows);
no sub-cycle or exam-date variable distinguishing 2017–2018 from 2019–March 2020 participants
exists in any of the 8 raw source files. This is deliberate on NHANES's part (the 2019–March 2020
portion was never independently fielded as a nationally-representative cycle). Full evidence:
`documentation/validation/phase8_pre_execution_snapshot.md`.

## 7. Data harmonization

Not applicable — Phase 8 operates entirely on the already-frozen primary cohort
(`data/processed/analysis_dataset_primary.parquet`, N=7,153), the same 10 frozen predictors, and
the same frozen outcome definition (`LUXSMED ≥ 8.2 kPa`). No external data, no harmonization step,
no variable-definition mapping is required.

## 8. Cohort comparability (training vs. holdout population shift)

`results/validation/phase8_population_shift.csv`, computed live: standardized mean differences
between the training population (N=5,366, Non-Hispanic Black excluded) and the holdout population
(N=1,787, entirely Non-Hispanic Black) are small-to-moderate for every predictor — largest at
albumin (LBXSAL, SMD=−0.44) and BMI (SMD=+0.25); age (SMD=−0.01) and sex (49.9% vs. 47.9% male)
are nearly balanced. Outcome prevalence: training 9.11%, holdout 9.90%. No extreme population
shift exists that would alone explain a large performance change.

## 9. Outcome comparability

Identical — the outcome (`outcome_primary_8.2kPa`) is computed from the same frozen definition for
both populations; no redefinition occurred.

## 10. Predictor comparability

Identical — all 10 frozen predictors (`RIDAGEYR, RIAGENDR, BMXBMI, LBXSATSI, LBXSASSI, LBXSAL,
LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD`), 0% missing in both populations (verified live; the primary
cohort is complete-case by construction).

## 11. Primary discrimination validation (Non-Hispanic Black holdout, N=1,787, 177 positive)

| Model | Threshold | ROC-AUC | 95% CI | PR-AUC | Sensitivity | Specificity |
|---|---|---|---|---|---|---|
| logistic | 0.4555 | 0.7743 | [0.7345, 0.8128] | 0.3513 | 0.7345 | 0.6634 |
| random_forest | 0.4264 | 0.7878 | [0.7515, 0.8229] | 0.3282 | 0.7458 | 0.7149 |
| xgboost | 0.4587 | 0.7893 | [0.7516, 0.8249] | 0.3273 | 0.7345 | 0.7043 |
| lightgbm | 0.5104 | 0.7881 | [0.7507, 0.8247] | 0.3464 | 0.7006 | 0.7516 |
| mlp | 0.0949 | 0.7719 | [0.7334, 0.8092] | 0.3500 | 0.6893 | 0.7360 |

Thresholds were re-derived via the same frozen Youden's-J-on-CV-OOF method Phase 3 originally used
(Amendment #1), computed on the training population only — they differ from Phase 3's original
threshold values because the underlying model weights differ (a different training population).

**Does performance drop?** Yes, measurably: comparing against Phase 3's original full-population
test AUC (`results/tables/phase3_overall_discrimination.csv`), every model's original point
estimate falls outside its Phase 8 holdout 95% CI:

| Model | Phase 3 full-population test AUC | Phase 8 NHB-holdout AUC | Drop |
|---|---|---|---|
| logistic | 0.8334 | 0.7743 | −0.0591 |
| random_forest | 0.8343 | 0.7878 | −0.0465 |
| xgboost | 0.8429 | 0.7893 | −0.0536 |
| lightgbm | 0.8394 | 0.7881 | −0.0513 |
| mlp | 0.8229 | 0.7719 | −0.0510 |

Discrimination is retained (all 5 models remain well above chance, AUC 0.77–0.79) but is
consistently, measurably attenuated relative to full-population performance.

## 12. Calibration validation

Mentor-authorized ("Does calibration remain stable?"). Calibration-in-the-large (logit-scale
regression, the same frozen method as Phase 4) on the raw, non-recalibrated Phase 8 models:

| Model | Intercept | Slope | Brier |
|---|---|---|---|
| logistic | −2.169 | 0.774 | 0.186 |
| random_forest | −1.886 | 0.972 | 0.154 |
| xgboost | −2.049 | 0.845 | 0.172 |
| lightgbm | −2.037 | 0.846 | 0.171 |
| mlp | −0.577 | 0.636 | 0.078 |

Calibration is **not** stable: all 5 models show a substantial negative intercept, meaning
predicted risk systematically overstates observed risk on the unseen holdout subgroup. Slopes
below 1 for all models (most pronounced for MLP, 0.636) indicate overconfident/too-extreme
probabilities. No recalibration was performed — this is an assessment, not a fix, consistent with
the mentor's question and this project's scope discipline.

## 13. Fairness validation

Not re-run as a separate Phase 5-style analysis (Section 19 of the protocol freeze) — Phase 8's
holdout design already answers "which groups are most affected" at the model level: comparing the
5 models' generalization to Non-Hispanic Black shows tree-ensemble models (random_forest, xgboost,
lightgbm) attenuate somewhat more than logistic or MLP relative to their same-subgroup in-training
baseline (Section 16).

## 14. Uncertainty validation

**Not authorized.** The mentor's Phase 14 text does not mention uncertainty or conformal
prediction anywhere (unlike calibration, named explicitly). Per this project's established
discipline (the identical determination was made for the targeted MI sensitivity analysis),
uncertainty/conformal evaluation is explicitly skipped, not silently omitted.

## 15. Phase 7 mitigation validation

**Not applicable and not authorized.** Non-Hispanic Black was never a Phase 7 mitigation target
(confirmed: zero rows in `test_set_mitigation_final.csv`); the mentor's Phase 14 text does not
mention mitigation.

## 16. Generalization matrix

`results/validation/phase8_generalization_results.csv` (full detail). Classification uses two
baselines: (1) Phase 3's full-population test AUC (has a bootstrap CI) and (2) Phase 5's
Non-Hispanic Black in-training subgroup AUC on the locked test set (same subgroup, but
represented during training, N=550 of the test set) — the cleanest isolation of "what changes when
this specific group is entirely absent from training."

| Model | AUC drop vs. Phase 3 full pop. | AUC drop vs. Phase 5 NHB in-training | Classification |
|---|---|---|---|
| logistic | −0.0591 | −0.0169 | MODERATE GENERALIZATION |
| random_forest | −0.0465 | −0.0334 | MODERATE GENERALIZATION |
| xgboost | −0.0536 | −0.0356 | MODERATE GENERALIZATION |
| lightgbm | −0.0513 | −0.0281 | MODERATE GENERALIZATION |
| mlp | −0.0510 | **+0.0005** | **MODEL-SPECIFIC GENERALIZATION** |

MLP is the only model whose Non-Hispanic Black AUC does not meaningfully change between being
represented in training (Phase 5, 0.7714) and being entirely absent from training (Phase 8,
0.7719) — a genuinely distinct pattern from the other 4 models, all of which show a real
(1.7–3.6 AUC-point) decline attributable to the subgroup's absence. This is reported as an
observation, not a causal claim about *why* MLP behaves differently.

## 17. Population-shift analysis

See Section 8. SMDs are small-to-moderate for all predictors; the observed AUC decline is not
attributable to an extreme population shift alone, though moderate shifts in albumin and BMI
likely contribute some part of the effect alongside genuine unseen-group generalization
difficulty. This report does not attempt to decompose the two.

## 18. Negative findings

Calibration does **not** remain stable (Section 12) — this is a genuine negative finding, retained
and reported prominently, not hidden. Discrimination, while retained, is not preserved at the
original full-population level for any of the 5 models.

## 19. Non-Hispanic Black interpretation — MI relationship, explicitly separated

**MI finding (targeted sensitivity analysis, already complete):** Including the 615 previously
complete-case-excluded participants via multiple imputation did not materially change the
Non-Hispanic Black fairness result — 4/5 models classified STABLE UNDER MI, MLP INDETERMINATE, no
significant difference after BH-FDR correction (adjusted p=0.978 for all models). MI ROBUSTNESS
PARTIAL.

**Phase 8 holdout finding (this report):** Can the model generalize to Non-Hispanic Black
participants when that entire subgroup is completely absent from training? Answer: discrimination
degrades moderately (4/5 models) or not meaningfully (MLP) relative to the same-subgroup
in-training baseline; calibration degrades substantially for all 5 models.

These are related but categorically distinct experiments: MI asked whether *including*
previously-excluded participants changes the result; Phase 8 asks whether the model can generalize
to a group with *zero* representation in training. No result from one experiment is used to
adjust, override, or reinterpret the other.

## 20. Precision limitations

Holdout N=1,787 with 177 positive events classifies as "primary-feasibility candidate" under the
frozen `phase5_common.precision_tier` heuristic — the highest precision tier, adequate for the
bootstrap CIs reported. The Phase 5 in-training NHB baseline (N=550, 50 positive) used for the
Section 16 comparison has no available CI in its source artifact
(`subgroup_discrimination_metrics.csv` records point estimates only); that comparison is reported
descriptively, not as a formally inferential test.

## 21. Reproducibility

One isolated clean rerun (to a scratch directory, script logic unchanged) reproduced every
threshold, AUC, sensitivity, and calibration value exactly (byte-identical to 4+ decimal places)
to the committed run — confirming full determinism under the fixed seed (42) used throughout.

## 22. Automated tests

`tests/test_phase8_subgroup_holdout.py`: 35 live checks covering official-definition verification,
within-release time-split infeasibility documentation, candidate-matrix existence, prior-commitment transparency
(PATH B, not presented as discovery), commit-ordering (protocol before training), training/holdout
disjointness and complete subgroup exclusion, no leakage into preprocessing/tuning/threshold
selection, frozen predictor/outcome/model-family preservation, count accuracy, no post-hoc tuning,
model-hash integrity, and Phase 3–7 artifact immutability. **All 35 passed.**

## 23. Git/provenance

- Commit A (`77e2b1c`): candidate decision + protocol freeze — no training code or model exists at
  this commit.
- Commit B (`6fb7e93`): participant partition + leakage verification.
- Commit C (`279b672`): five-model retraining + holdout evaluation.
- Commit D (this report + tests + handoff): recorded and pushed below.

## 24. Remaining limitations

- Subgroup holdout is **not** external validation; generalization to other institutions,
  countries, or clinical settings is not established by this experiment.
- NHANES elastography (`LUXSMED`) remains a surrogate outcome context, not biopsy-confirmed
  histology — this limitation is unaffected by Phase 8 and applies identically to all reported
  numbers.
- Excluding an entire subgroup changes both training size (−25.0%) and positive-event count
  (−26.6%); while feasibility was confirmed (Section 20), some residual effect of the smaller,
  differently-composed training set on model behavior cannot be fully separated from the
  unseen-group generalization effect itself.
- Calibration degradation was assessed but not corrected — no recalibration was attempted or
  authorized in this phase.
- Two other protocol-relevant candidates (BMI-Obese, Age-60+) were evaluated for feasibility but
  not executed as primary holdout experiments, due to severe (BMI-Obese: 70.27%) or substantial
  (Age-60+: 48.50%) positive-case reduction in the remaining training population — documented as
  open future work, not dismissed.

## 25. Phase 9 handoff

Per the mentor's own final-principle guidance and this task's Part 31 ("Unless Phase 8 reveals a
genuine methodological problem requiring follow-up, this is intended to be the final major new
experimental phase... Move toward final synthesis, robustness interpretation, literature-based
novelty verification, and thesis/manuscript integration"): **Phase 8 does not reveal a
methodological problem requiring a new experimental phase.** It reveals a genuine, honestly-reported
generalization limitation (moderate discrimination attenuation, calibration instability for the
excluded subgroup) that belongs in the thesis's limitations and discussion sections, not in a new
Phase 9 experiment. Whoever begins Phase 9 (synthesis/manuscript integration) should: (a) cite this
report's Section 16 matrix as evidence for the thesis's generalization-limitation discussion; (b)
preserve the MI-vs-holdout distinction (Section 19) precisely — do not conflate the two; (c) not
initiate BMI-Obese or Age-60+ holdout experiments without a fresh, explicit protocol decision,
since both showed a severe training-integrity confound in Section 20's feasibility assessment;
(d) not claim external validity, novelty, or biopsy-confirmed generalizability anywhere in the
manuscript without separate, explicit literature-grounded support.

## Final Status

**PHASE 8 COMPLETE WITH DOCUMENTED LIMITATIONS — SUBGROUP GENERALIZATION ASSESSED**
