# Phase 4 Subgroup Calibration Post-Audit

**Audit scope:** read-only post-audit of the Phase 4 subgroup-calibration execution, its
inputs and outputs, the prior exploratory subgroup-recalibration artifact, frozen-state
documentation, and the locked-test boundary. No calibration was rerun and no prior, master,
or Phase 7 artifact was modified.

## Decision

**C. PHASE 4 REQUIRES CORRECTION / RE-EXECUTION.**

This is an audit disposition only; re-execution was **not** performed. The core OOF probability
comparisons and the observed lack of classification-level BMI improvement are reproducible from
the recorded files, but the recorded Phase 4 result cannot be accepted as a fully protocol-
conforming selection analysis.

The decision is driven by two material findings:

1. The frozen calibration protocol specifies ten equal-frequency risk deciles, but
   `run_phase4_subgroup_calibration.py:29-34` computes ECE with ten equal-width bins
   (`0.0, 0.1, ..., 1.0`). ECE is used in the selection gate at lines 84-90, so this is
   selection-critical rather than a presentation-only difference.
2. The conformal comparison labels one arm `global_platt`, but lines 97-105 never fit or apply
   a global Platt map in that arm. It uses raw proper-train-refit probabilities. Consequently,
   the reported conformal comparison is not a valid global-Platt-versus-subgroup-Platt
   comparison.

## Materials inspected

- Script: `src/run_phase4_subgroup_calibration.py` (SHA-256
  `38834cbf525fabc42d3055e52890e5f34f87ad51ce1c2393c677b127c933145a`).
- Existing report and decision log:
  `documentation/fairness_bmi_investigation/PHASE4_SUBGROUP_CALIBRATION_REPORT.md` and
  `PHASE4_DECISION_LOG.md`.
- All Phase 4 subgroup-calibration outputs:
  `phase4_calibration_results.csv`, `phase4_subgroup_calibration_results.csv`,
  `phase4_fairness_comparison.csv`, `phase4_conformal_comparison.csv`,
  `phase4_locked_test_confirmation.csv`, `phase4_selection_manifest.json`,
  `phase4_lineage.json`, and `phase4_figures/phase4_ece_comparison.png`.
- Frozen-state material:
  `documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md`,
  `phase4_pre_execution_snapshot.md`, `phase4_calibration_data_flow.md`,
  `results/calibration/phase4_test_set_protection_audit.md`, and
  `phase4_prediction_input_audit.csv`.
- Prior exploratory artifact:
  `results/diagnostics/stage0/subgroup_recalibration_metrics.csv` and its source
  `src/sens_05_subgroup_recalibration.py`.

## Execution-order audit

The script's control flow is ordered as follows:

1. Load the five OOF prediction files and OOF-linked primary-cohort metadata
   (`run_phase4_subgroup_calibration.py:45-53`).
2. Fit/evaluate global and subgroup Platt candidates on an even/odd split of OOF rows
   (`:54-92`).
3. Run the separate conformal development comparison using the reserved conformal-calibration
   input (`:93-106`).
4. Write `phase4_selection_manifest.json` (`:107-108`).
5. Only then load `test_ids.csv`, test metadata, and `test_predictions_<model>.csv`
   (`:110-127`).

Thus, the source code supports the claimed *intended* ordering: selection precedes test-file
loading. The manifest has no timestamp, execution log, or runtime event record, so the audit
can verify static ordering but cannot independently prove the actual runtime order beyond the
result timestamps and file presence. The older 2026-08-19 protection audit documents the
original project Phase 4, not this 2026-08-26 subgroup-calibration run.

## Data and metric findings

- OOF inputs contain 5,007 unique participants and 466 positives; the script's independent
  evaluation half contains 2,503 participants and 230 positives. The fit half contains 2,504
  participants and 236 positives.
- The five frozen model families and frozen thresholds are carried forward. The classification
  decision is based on the original raw prediction and threshold, while calibration metrics
  use transformed probabilities.
- Sparse-cell fallback is implemented and visible in the output. The OOF evaluation output has
  35 `UNSTABLE_SMALL_CELL` rows (principally underweight and young/normal BMI×age cells) and
  65 estimable rows per candidate. No sparse cell is silently presented as a stable estimate.
- The OOF comparison selects global Platt for Logistic, Random Forest, XGBoost, and MLP, and
  subgroup Platt for LightGBM. The selected LightGBM candidate has lower OOF ECE
  (0.009485 vs 0.011516) and essentially unchanged Brier score (0.070004 vs 0.069982), but
  that ECE uses the non-frozen equal-width bins.
- The fixed threshold means classification counts do not change under probability
  transformation. OOF BMI sensitivity gaps are therefore unchanged: 50.40, 39.86, 37.95,
  38.62, and 39.88 percentage points for Logistic, Random Forest, XGBoost, LightGBM, and MLP.
- Locked-test confirmation likewise shows no BMI classification improvement. The Normal-versus-
  Obese sensitivity gaps are approximately 47.66, 31.62, 31.36, 27.08, and 39.03 percentage
  points, respectively. For LightGBM, the selected subgroup map worsens test Brier from
  0.069667 to 0.069980 and ECE from 0.015320 to 0.015698 while leaving sensitivity and
  specificity unchanged.

These results support the narrow statement that the tested probability transformations did not
resolve the BMI classification disparity. They do not support calling the selected LightGBM
method a fairness improvement, and they do not support a protocol-conforming ECE-based selection
claim.

## Selection-rule audit

The manifest records this rule: subgroup calibration is selected only if ECE improves, Brier is
within +0.01, overall sensitivity and specificity are within five percentage points, and the
Age-60-versus-40 sensitivity gap is within five percentage points. The code implements that
rule.

However:

- No independent pre-execution freeze for this new subgroup analysis was found. The rule is
  recorded in the script and post hoc manifest, so historical pre-specification cannot be
  independently established from strong repository provenance.
- The rule has no required improvement in the BMI sensitivity gap. Because the frozen
  classification decisions are deliberately unchanged, the rule can select a subgroup
  calibrator without improving the stated BMI fairness target. LightGBM is the concrete example.
- The rule's ECE component is computed with the wrong binning relative to the frozen calibration
  protocol. This makes the selection result invalid as a protocol-conforming decision even
  though the arithmetic is internally reproducible.

## Conformal comparison audit

`phase4_conformal_comparison.csv` contains ten rows, with 501 fit and 501 evaluation
participants per model/candidate. The subgroup arm applies BMI-cell maps, but the
`global_platt` arm does not fit or apply a global map; it passes raw `pf`/`pe` directly to the
nonconformity calculation. The reported values (for example Logistic 0.9222 versus 0.8842
coverage) therefore cannot be interpreted as a Platt-versus-subgroup-Platt comparison.

This new comparison is also not interchangeable with the prior exploratory artifact. The prior
artifact used the designated conformal calibration set and proper-train-refit models, reports
coverage changes no larger than 0.68 percentage points, and remains unchanged. The differing
split and the new arm-label defect require the two artifacts to remain separate.

## Lineage and locked-test protection

The new `phase4_lineage.json` records the script hash and five OOF prediction hashes and states
that the prior artifact was not overwritten. It does **not** record hashes for the primary
parquet, split files, test prediction files, conformal refit joblibs, manifest, or output files;
it also lacks environment, runtime, and execution-event metadata. Lineage is therefore useful
but incomplete.

Static code inspection verifies that test predictions are loaded only after the manifest write.
The frozen input audit verifies valid OOF/test shapes, IDs, probabilities, and labels, and the
locked-test output has the expected 2,146 participants and 200 positives. There is no new
runtime access log proving that this exact run obeyed the source-code order. No evidence was
found that test labels were used to fit a calibrator; the test set is used for confirmatory
scoring only in the recorded control flow.

## Final audit conclusion

The recorded analysis is reproducible as an exploratory, limited comparison, but it is not a
fully valid Phase 4 selection execution. The equal-width ECE selection defect and the
mislabelled conformal comparator must be corrected in a future authorized re-execution. This
audit does not perform that re-execution and does not alter any existing calibration, prior,
master, Phase 7, or later-phase artifact.
