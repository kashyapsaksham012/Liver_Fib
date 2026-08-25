# Three Diagnostics — Protocol Freeze

**No result from any of these three analyses was inspected or used to choose the analysis
specification before this protocol freeze.**

**Pre-existing-file disclosure:** `results/diagnostics/stage0/` and `stage1/` already contained
files matching or overlapping these analysis names (`continuous_spline_curves.csv`,
`finer_age_bands.csv`, `group_specific_threshold_metrics.csv`, `subgroup_recalibration_metrics.csv`,
plus a Socio-Conformal literature audit, fairness post-processing, and an AFCP comparison),
generated 2026-08-25 12:15–12:35, all untracked in git. On inspection, the subgroup-recalibration
output contained a verifiable error (its "global_platt" calibration intercept for Logistic,
−2.2425, is the RAW pre-Platt intercept, not a post-recalibration value — independently confirmed
against `results/calibration/primary_metrics_by_model.csv` multiple times this session), and the
overall generation speed (a claimed full-paper literature read in ~2 minutes) is not consistent
with the rigor this project otherwise applies. Per explicit user decision, this pre-existing work
is **not used as a source, not built upon, and not treated as authoritative** for this protocol or
its execution. It has **not been deleted** — it remains on disk, untracked, unresolved, for the
user to dispose of at their discretion. Where this document's required output filenames coincide
with pre-existing (distrusted) files under `src/` (`sens_04_continuous_splines.py`,
`sens_05_subgroup_recalibration.py`, `sens_06_group_specific_thresholds.py`), those files are
overwritten with fresh implementations under this protocol, since the task explicitly calls for a
from-scratch redo at these canonical paths — this supersession is recorded here, not silent.

---

## Analysis 1 — Continuous BMI / Age

**Estimands:**
- Sensitivity: among test participants with true outcome = 1, P(model predicts positive |
  continuous covariate), using each model's existing frozen global Youden threshold (no new
  threshold fitting in this analysis).
- Conformal coverage: P(true class ∈ conformal prediction set | continuous covariate), using the
  existing frozen Phase 6 baseline (unmitigated) global conformal threshold per model.
- Calibration diagnostic: decile-binned comparison of mean recalibrated predicted probability vs.
  observed event rate, within covariate deciles — a binned observed-vs-predicted diagnostic, not a
  bare residual plot, computed on the same population as the sensitivity/coverage curves.
- Efficiency: mean conformal prediction-set size by covariate decile, using the existing frozen
  Phase 6 baseline set-size indicator per participant.

**Smoothing method:** restricted cubic spline (RCS), Harrell's standard convention: **4 knots**,
placed at the **5th, 35th, 65th, and 95th percentiles of the covariate's distribution in the
TRAINING partition** (`train_ids.csv`, N=5,007) — never the test set. This knot rule is fixed now,
for both BMI and Age, and will not be altered after any result is seen.

**Fitting data:** the RCS-basis logistic (for binary estimands: sensitivity, coverage) or linear
(for the continuous estimand: mean set size) model is fit on **out-of-fold training predictions**
(`results/predictions/validation_predictions_<model>.csv`, joined to the covariate from
`analysis_dataset_primary.parquet`) — i.e., the same population and predictions already used
throughout this project for OOF-based decisions (Youden thresholds, Platt calibration).

**Evaluation data:** the frozen OOF-fit RCS coefficients are applied, unchanged, to the **locked
test set's** own covariate range to produce the smooth predicted curve there; the test set's own
raw decile-binned empirical rates (Wilson CI) are reported alongside as a purely descriptive
companion — no new fitting, no new decision, occurs on test data.

**Age finer bands:** 60–69 and 70–80 (NHANES tops-codes age at 80 in this release — confirmed
earlier this session against `documentation/audit_reports/P_DEMO_audit_report.md` — so "70+" is
"70–80" in this dataset, not unbounded). These are pre-defined; no other band boundary will be
tried.

**Sparse-region rule:** any decile bin with fewer than 10 positive or 10 negative outcomes is
flagged `sparse_cell=True` in the output and is not used to support a strong claim, per the
project's own existing `precision_tier` convention (`src/phase5_common.py`).

**Predefined interpretation framework:** the categorical finding is judged "compatible with a
continuous gradient" if the RCS-fitted curve is monotonic (or near-monotonic, allowing for CI-width
tolerance) across the categorical cut-point; "compatible with a threshold/nonlinear transition" if
the curve is flat away from the cut-point and changes sharply near it; "not clearly supported" if
the smooth curve's CI is too wide to distinguish either pattern given the observed support.

---

## Analysis 2 — Group-Specific Decision Thresholds

**Subgroup definitions:** the project's existing frozen BMI categories (Underweight, Normal,
Overweight, Obese) and Age categories (18–39, 40–59, 60+) — unchanged, not merged, not
re-defined.

**Threshold method:** Youden's J, identical formula and implementation pattern to
`phase3_06_threshold_and_test_eval.py`'s `youdens_j_threshold()`, applied to each subgroup's own
out-of-fold training predictions and labels (`validation_predictions_<model>.csv`, filtered to
subgroup membership via the covariate in `analysis_dataset_primary.parquet`).

**Fitting data:** OOF training predictions, filtered per subgroup. **Evaluation data:** the locked
test set, using each participant's own subgroup-specific frozen threshold in place of the global
one.

**Metrics:** sensitivity, specificity, FNR, sensitivity disparity (vs. the same reference groups
used in Phase 5: Normal-BMI reference for BMI, Age 40–59 reference for Age), 95% Wilson CIs, event
counts, compared against the existing global-threshold baseline (already established in
`results/tables/phase3_overall_discrimination.csv` and `results/fairness/fairness_inference.csv`).

**Explicit distinction:** this analysis studies operating-point/threshold effects only. It is not a
calibration experiment and predicted probabilities are not altered.

---

## Analysis 3 — Subgroup-Specific Platt Recalibration

**Subgroups:** BMI-Obese and Age-60+ only (the two FDR-significant-in-both-Phase-5-and-6 groups
already targeted by the existing Phase 7 mitigation) — no new subgroup is introduced.

**Two separate, necessarily distinct sub-pipelines, because the project's own architecture uses two
different fitted-model families for point-prediction/calibration vs. conformal purposes — this is
not a new design choice, it reflects the existing frozen architecture:**

1. **Calibration-metric comparison** (intercept/slope/Brier/ECE): uses the **primary v1 model**
   family (the same models behind the existing global Platt recalibration). Subgroup-specific Platt
   parameters are fit on that subgroup's **out-of-fold training predictions** only, frozen, then
   applied to that subgroup's locked-test rows. Compared against the existing global Platt result
   (already established, `results/calibration/test_set_calibration_final.csv`) for the same
   subgroup.
2. **Conformal-coverage comparison**: uses the **proper_train_refit model** family (the models
   actually behind the Phase 6/7 conformal pipeline, fit on `proper_train_ids.csv`, N=4,005).
   Subgroup-specific Platt parameters are fit on that subgroup's rows within the
   **conformal-calibration set** (`conformal_calibration_ids.csv`, N=1,002) — the project's own
   designated calibration-fitting venue, never the test set. These parameters are applied to
   recalibrate that subgroup's calibration-set probabilities, from which a **new** nonconformity
   quantile threshold is derived (identical quantile formula to
   `phase7_02_mitigation_implementation.py`), applied finally to that subgroup's locked-test rows.
   Compared against the existing Phase 6 baseline (raw, non-recalibrated) subgroup coverage.

**Critical conformal rule, honored exactly:** old conformal scores/quantiles are never reused
unchanged for the recalibrated pipeline — new nonconformity scores and a new quantile are derived
from the recalibrated calibration-set probabilities before any test-set evaluation.

**Metrics:** calibration intercept/slope/Brier/ECE; subgroup sensitivity; marginal, subgroup, and
(where the subgroup itself is the true intersection) intersectional coverage; mean set size,
singleton rate, doubleton rate — before (existing baseline) vs. after (subgroup recalibration).

**Predefined interpretation framework:** subgroup recalibration is judged to "materially improve"
a metric if the post-recalibration point estimate moves by an absolute amount that would change
which side of the relevant frozen threshold it falls on (e.g., coverage crossing from
significantly-below-90% to a CI that includes 90%), not merely by any nonzero amount. No numeric
percentage-point threshold is invented beyond this rule, since no protocol-prespecified numeric
materiality threshold exists for this specific comparison — this is stated explicitly rather than
fabricating one.

---

## Statement required by the governing protocol

No result from Analysis 1, 2, or 3 was computed, inspected, or used to select any part of this
specification before this document was written and saved.
