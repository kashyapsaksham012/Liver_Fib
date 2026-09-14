# FIB-4 clinical-baseline addendum — verification report

**Status: NEW ANALYSIS, NOT YET FOLDED INTO ANY MANUSCRIPT.** Executed on explicit request
(New Analysis Queue E1/E2, `documentation/manuscript/REVISION_PLAN.md`), addressing Change
Table item C11 (no external clinical baseline). Per that request: **no manuscript claim has
been changed as a result of this analysis** — this document reports what was run and what
came out, for independent review before any manuscript text is touched.

No frozen artifact, split file, model, or prior result was modified. No new NHANES data was
pulled — all four FIB-4 inputs were already frozen predictors. Full run log:
`logs/cb_fib4_baseline_run.log`. All scripts: `src/cb_01_compute_fib4.py` through
`src/cb_05_matched_stiffness.py`. All outputs: `results/clinical_baselines/`.

## 1. What was computed

FIB-4 = (RIDAGEYR × LBXSASSI) / (LBXPLTSI × √LBXSATSI), for all N=7,153 participants in the
frozen primary cohort, using the frozen `analysis_dataset_primary.parquet` and the existing
frozen split files (`train_ids.csv` N=5,007, `proper_train_ids.csv` N=4,005,
`conformal_calibration_ids.csv` N=1,002, `test_ids.csv` N=2,146) verbatim — no new split was
created, and split disjointness/coverage was re-verified programmatically before use
(`cb_01_compute_fib4.py`, fails loudly on any mismatch; it passed).

**E1 — discrimination, calibration, BMI/age-subgroup sensitivity, and conformal coverage**, run through
the closest available analog of the exact pipeline already used for the five ML models:

- **Discrimination** (`cb_02_discrimination.py`): mirrors `phase3_06_threshold_and_test_eval.py`
  exactly — Youden's J threshold, 2,000-resample percentile bootstrap (seed 42), locked test
  set touched once. FIB-4 needs no fitting (it is a fixed formula), so there is no OOF/CV step;
  the threshold is selected directly on the training partition (N=5,007) using the raw score,
  which is the direct analog of "threshold from training data only, test never touched."
- **Calibration** (`cb_06_calibration.py`): mirrors `phase4_09_final_test_set_calibration.py`
  exactly — calibration-in-the-large (intercept + slope via an unregularized logistic
  regression of y on logit(p)), Brier score, and 10-bin decile ECE, for a "raw" and a
  "recalibrated" variant on the locked test set. "Raw" is the same auxiliary univariate
  logistic used for conformal coverage (fit on `proper_train_ids` only). "Recalibrated" is a
  second-stage calibration-in-the-large correction fit on `conformal_calibration_ids`
  (N=1,002, held out from the auxiliary fit) — the same role the OOF-fit Platt transform
  plays for the five ML models. Unlike the ML models, this correction **did not improve**
  calibration (see 2f) — reported as found, not adjusted after the fact.
- **Subgroup sensitivity** (`cb_03_fairness.py`): mirrors `phase5_04_inference.py` exactly —
  same stratified-within-subgroup bootstrap (n=2,000, seed 42 + per-comparison offset), same
  BH-FDR within each dimension family, same 10pp meaningful-difference rule. Run for all four
  dimensions (bmi, age, sex, race_ethnicity), not only BMI, since the cost was negligible once
  the harness was built and it lets age be checked the same way.
- **Conformal coverage** (`cb_04_conformal.py`): mirrors `phase6_02/03/04` exactly for
  partition discipline (fit-equivalent on `proper_train_ids` only, calibrate on
  `conformal_calibration_ids` only, one single locked-test touch), **with one necessary
  addition, stated plainly**: split-conformal needs a class probability to form the
  nonconformity score 1−p̂(true class), and FIB-4 has no native probability. The minimal fix is
  a univariate logistic mapping p̂ = sigmoid(b0 + b1·FIB4), fit **only on `proper_train_ids`**
  (same partition the five ML models were refit on for their own conformal analysis). This
  does not modify FIB-4 itself; it is the auxiliary step required to apply split-conformal to
  any non-probabilistic score. Every FIB-4 conformal number below inherits this caveat and is
  labeled "FIB-4 (+ auxiliary univariate logistic)" throughout.

**E2 — matched-stiffness regression** (`cb_05_matched_stiffness.py`): mirrors
`prepub_02_vcte_bias_sensitivity.py`'s C4 exactly — same band (8.2 ≤ LUXSMED < 12 kPa), same
Normal/Obese-only restriction, same locked test set, same OLS specification
(score ~ 1 + LUXSMED + is_obese). Band size (N=102, Normal=15, Obese=87) matches the five
ML models' identical band exactly, confirming the population restriction is reproduced
correctly. Reported for two dependent variables: the raw FIB-4 score (native units, no
auxiliary fit) and the auxiliary-logistic probability (same units as the ML models' 0.19–0.33
result, for direct comparison, inheriting the E1 conformal caveat).

## 2. Results

### 2a. Discrimination (locked test, N=2,146)

| Score | AUROC (95% CI) | PR-AUC (95% CI) | Sens. | Spec. | PPV | NPV |
|---|---|---|---|---|---|---|
| FIB-4 | 0.638 (0.597, 0.680) | 0.177 (0.142, 0.232) | 0.600 | 0.610 | 0.137 | 0.937 |
| Logistic | 0.833 | 0.373 | 0.750 | — | — | — |
| Random Forest | 0.834 | 0.351 | 0.790 | — | — | — |
| XGBoost | 0.843 | 0.372 | 0.845 | — | — | — |
| LightGBM | 0.839 | 0.373 | 0.795 | — | — | — |
| MLP | 0.823 | 0.365 | 0.815 | — | — | — |

FIB-4's AUROC (0.638) is far below all five ML models (0.823–0.843) on this cohort — consistent
with the pre-existing literature cited in the manuscript's Introduction (FIB-4's modest
discrimination for advanced fibrosis in general-population screening), now demonstrated on the
identical cohort/split rather than only cited.

### 2b0. Calibration (locked test, N=2,146)

| Score | Variant | Intercept | Slope | Brier | ECE |
|---|---|---|---|---|---|
| FIB-4 | raw (auxiliary logistic, fit on proper_train only) | −0.845 | 0.630 | 0.0832 | 0.0138 |
| FIB-4 | recalibrated (2nd-stage correction fit on calibration partition) | +6.431 | 3.831 | 0.0837 | 0.0295 |
| Logistic | raw | −2.260 | 0.996 | 0.175 | 0.297 |
| Logistic | recalibrated (OOF Platt) | −0.154 | 0.939 | 0.071 | 0.017 |
| RF / XGBoost / LightGBM / MLP | raw | −2.19 to −0.44 | 0.93–1.28 | 0.146–0.175 | 0.245–0.297 |
| RF / XGBoost / LightGBM / MLP | recalibrated (OOF Platt) | +0.02 to +0.14 | 1.07–1.13 | 0.069–0.071 | 0.011–0.026 |

**FIB-4's "raw" calibration (ECE 0.0138) is already better than every one of the five ML
models' raw output, and lands inside the range of their *recalibrated* (post-Platt) output**
(0.011–0.026). This has a clean mechanistic explanation, not a surprising one: the five ML
models used class weighting / `scale_pos_weight` to handle the 9.3%-prevalence imbalance
during training, which induces the severe over-prediction their raw calibration shows
(intercepts −2.26 to −0.44) — that is what Platt scaling corrects. FIB-4's auxiliary logistic
was fit with **no class weighting**, directly by maximum likelihood on the natural class
distribution, so there is no comparable induced miscalibration for a second stage to correct.

**The attempted second-stage "recalibration" made FIB-4's calibration worse, not better**
(ECE 0.0138 → 0.0295; intercept/slope moved sharply away from 0/1) — reported here rather than
discarded. The most likely cause: composing two logit-linear transforms is nearly equivalent
to refitting the same one-parameter mapping on a much smaller, noisier sample
(N=1,002, ~93 positives, vs. 4,005 for the original fit), so the correction adds sampling
noise without correcting a real, systematic bias — because none was there to correct. The
honest reading is that **FIB-4's raw auxiliary-logistic probability is the better-calibrated
of the two FIB-4 variants**, and the "recalibrated" row should not be treated as an
improvement or used for comparison against the ML models' recalibrated numbers.

### 2b. BMI-subgroup sensitivity disparity (Obese vs. Normal reference)

| Score | Obese sens. | Normal sens. | Disparity (Obese − Normal, pp) | Significant (FDR<0.05) |
|---|---|---|---|---|
| FIB-4 | 0.521 | 0.773 | **−25.1** | Yes (q=0.027) |
| Logistic | 0.886 | 0.409 | +47.7 | Yes |
| Random Forest | 0.907 | 0.591 | +31.6 | Yes |
| XGBoost | 0.950 | 0.636 | +31.4 | Yes |
| LightGBM | 0.907 | 0.636 | +27.1 | Yes |
| MLP | — | — | +39.0 | Yes |

**Direction reverses.** All five ML models under-detect Normal-BMI relative to Obese; FIB-4
does the opposite on this cohort — it under-detects Obese relative to Normal. (ML-model rows
recomputed here in the same "Obese minus Normal" orientation as the FIB-4 row for direct
comparability; the manuscript's Table III reports the same five numbers in the opposite,
"Normal minus Obese," orientation, e.g. logistic there reads "−47.66" for the same fact
reported here as "+47.7." No manuscript number is disputed by this — it is a sign-convention
difference, flagged so the two tables aren't misread side by side.)

### 2c. Age-subgroup sensitivity disparity (60+ vs. 40–59 reference)

| Score | 60+ sens. | 40–59 sens. | Disparity (60+ − 40–59, pp) | Significant |
|---|---|---|---|---|
| FIB-4 | 0.832 | 0.500 | **+33.2** | Yes (q<0.001) |
| Logistic | — | — | −8.6 (ns, q=0.195) | No |
| Random Forest | — | — | −13.2 | Yes |
| XGBoost | — | — | −11.2 | Yes |
| LightGBM | — | — | −14.2 | Yes |
| MLP | — | — | −14.7 | Yes |

FIB-4 detects older participants *more* sensitively, unsurprising on inspection — age is a
direct multiplicative term in the FIB-4 formula's numerator, so higher age mechanically raises
the score at any fixed AST/platelet/ALT profile. The five ML models show the opposite pattern
(age 60+ under-detected). This is a different mechanism from the BMI reversal above (FIB-4's
age behavior is explainable directly from its formula; its BMI behavior is not, since BMI does
not appear in the FIB-4 formula at all).

### 2d. Conformal coverage (90% target, locked test)

| Score | Marginal | Obese | Normal | Age 60+ | Age 40–59 |
|---|---|---|---|---|---|
| FIB-4 (+ aux. logistic) | 89.6% (CI incl. 90%) | **84.1%*** | 93.8%* | **83.8%*** | 89.5% (ns) |
| Logistic | 90.8% | 82.3%* | 96.8%* | 84.9%* | 91.9% |
| Random Forest | 89.6% | 80.2%* | 96.4%* | 85.6%* | 89.3% |
| XGBoost | 88.1%* | 76.8%* | 96.1%* | 81.1%* | 89.0% |
| LightGBM | 89.6% | 79.2%* | 97.0%* | 84.8%* | 90.1% |
| MLP | 89.2% | 80.9%* | 95.4%* | 83.8%* | 88.4% |

\* Wilson 95% CI excludes 90% target, BH-significant.

**Direction matches, magnitude is similar.** Unlike the sensitivity result (2b), FIB-4's
conformal-coverage pattern lands on the *same* subgroups as all five ML models: Obese
under-covers, Normal over-covers, age 60+ under-covers — and FIB-4's age-60+ figure (83.8%)
falls squarely inside the ML models' own range (81.1–85.6%). This holds even though FIB-4's
underlying sensitivity disparity runs in the opposite direction from the ML models (2b) — i.e.
the fairness/coverage dissociation the manuscript reports for the ML models is not obviously
undone by using a completely different, non-learned score.

### 2e. Matched-stiffness regression (8.2–12 kPa band, N=102: Normal=15, Obese=87)

| Score | Dependent variable | β(is_obese) | p-value | Direction |
|---|---|---|---|---|
| FIB-4 | raw score (native units) | **−0.776** | 1.5×10⁻⁴ | Obese **lower** |
| FIB-4 | auxiliary probability | **−0.073** | 3.7×10⁻⁵ | Obese **lower** |
| Logistic | predicted probability | +0.332 | <0.001 | Obese higher |
| Random Forest | predicted probability | +0.254 | <0.001 | Obese higher |
| XGBoost | predicted probability | +0.267 | <0.001 | Obese higher |
| LightGBM | predicted probability | +0.278 | <0.001 | Obese higher |
| MLP | predicted probability | +0.191 | <0.001 | Obese higher |

**This is the sharpest result in the addendum.** At *identical measured liver stiffness*, all
five ML models assign obese participants a higher score than normal-weight participants
(the manuscript's "shortcut" finding). FIB-4, on the same participants, in the same band, does
the **opposite** and is itself statistically significant (p<0.001 both dependent-variable
versions): obese participants get a *lower* FIB-4 score than normal-weight participants at the
same measured stiffness. The BMI-conditioned shortcut the manuscript reports is therefore not
a property this cohort's standard-of-care score shares — on this specific test, FIB-4 points
the other way.

## 3. What this does and does not establish

- It directly answers Change Table item C11: the manuscript's implicit comparator (FIB-4) has
  now been computed on the identical cohort/split, not merely cited.
- The calibration result (2b0) is a third instance of the same reversal pattern as 2b/2e:
  FIB-4's raw output is *better* calibrated than the ML models' raw output, for a specific,
  identifiable reason (no class-weighting was used to fit it). This is not evidence FIB-4 is
  a better model overall — its discrimination (2a) is far worse — only that calibration and
  discrimination are dissociable for FIB-4 too, echoing the manuscript's own point that
  aggregate metrics don't move together.
- The clean reversal in 2b and 2e is a genuine, unexpected finding, not a confirmation of "FIB-4
  has the same problem" — it is closer to the opposite. Any manuscript language drafted from
  this needs to say what was actually found, not what might have been anticipated.
- 2d (conformal coverage) suggests the coverage-side dissociation may be a more general property
  of this cohort/outcome than of any specific learned model, since a non-learned score
  reproduces it — but this is a single non-ML comparator, not a proof of generality, and the
  auxiliary-logistic caveat (Section 1) applies to every conformal number for FIB-4.
- Small-cell caveats already flagged in the manuscript apply here too: the matched-stiffness
  band has only 15 Normal-BMI participants; several race/sex/age FIB-4 subgroup cells are in
  the "limited precision" or "insufficient evidence" tier (see full CSVs).
- The NAFLD Fibrosis Score (E4 in the Revision Plan) was not attempted — it requires a
  glucose/diabetes field absent from the frozen processed dataset, a genuine new-data-pull, out
  of scope for this request.

## 4. File inventory

```
results/clinical_baselines/
  fib4_scores.csv                    per-participant FIB-4 + split membership (N=7,153)
  fib4_discrimination.csv            E1 discrimination table (Section 2a)
  fib4_test_predictions.csv          per-participant test-set FIB-4 prediction (threshold-based)
  fib4_calibration.csv               E1 calibration table (Section 2b0)
  fib4_calibration_curve_data.csv    E1 decile calibration-curve data underlying the ECE figures
  fib4_fairness_inference.csv        E1 full subgroup sensitivity table, all 4 dimensions (2b, 2c + sex/race)
  fib4_conformal_threshold.csv       E1 conformal calibration threshold
  fib4_marginal_coverage.csv         E1 marginal coverage (Section 2d)
  fib4_subgroup_coverage.csv         E1 full subgroup coverage table, all 4 dimensions (2d + sex/race)
  fib4_test_prediction_sets.csv      per-participant conformal set membership + auxiliary probability
  fib4_matched_stiffness.csv         E2 matched-stiffness regression (Section 2e)
logs/cb_fib4_baseline_run.log        full stdout of an end-to-end fresh run (seed 42, reproducible)
src/cb_01_compute_fib4.py .. cb_05_matched_stiffness.py
```

## 5. Next step

This is a verification artifact, not manuscript text. Before anything from this report is
quoted in `research_doc (4).pdf`, the revision plan, or `MANUSCRIPT_DRAFT.md`, it should be
independently checked — ideally by re-running `logs/cb_fib4_baseline_run.log`'s commands from a
clean checkout and confirming the numbers reproduce exactly (seed 42 throughout; they should).
