# Phase 6 8.0-kPa Robustness — Read-Only Final Audit

**Repository:** `/Users/sakshamkashyap/Desktop/Research /liver_fibrosis_research`  
**Audit mode:** read-only. No experiment, rerun, repair, or overwrite was performed.  
**Decision:** **B — accepted with documented limitations**

## Scope and authority

Inspected the actual `src/run_phase6_8kpa_robustness.py`, the Phase 6 canonical and legacy
outputs, both Phase 6 reports, manifests/lineage, primary 8.2-kPa result artifacts, governing
protocols, prior Phase 6 sources, legacy 8.0 sensitivity artifacts, and repository
preservation state. The full 8.0-kPa namespace is treated as a separate robustness analysis;
the older `results/sensitivity/*8p0kPa*` files are relabel-only outputs and are not silently
merged with it.

## Verified implementation and cohort

- The only intended analytical change is the outcome threshold: valid VCTE
  (`LUAXSTAT==1`) with `LUXSMED>=8.0` instead of `>=8.2` (source lines 204–215).
- Independent live derivation confirms **N=7,153**, all 7,153 VCTE-valid, 8.2-kPa positives
  **666 (9.310779%)**, 8.0-kPa positives **715 (9.995806%)**, and **49** changed labels
  (0.685027%). The 8.0 label agrees with the pre-existing sensitivity column.
- Ten frozen predictors and the five model families (logistic, random forest, XGBoost,
  LightGBM, MLP) are unchanged. Proper-train/calibration/test partitions are 4,005/1,002/2,146
  and are pairwise disjoint.
- Each model obtains inherited Phase 3 parameters, five-fold stratified OOF predictions,
  OOF Youden threshold and Platt parameters, a proper-train final fit, split-conformal
  calibration, locked-test metrics, demographic fairness, age, BMI×Age, calibration, and
  conformal outputs (lines 247–299 and 337–463). Durable Phase-6 model files are not saved;
  only in-memory pickle hashes are recorded.

## Leakage and test-order determination

**Static evidence: PASS.** The pre-test manifest is written before labels, training, OOF,
calibration, or test data are read; all selections are frozen at lines 301–322, and the first
test-ID read is line 325. The code also checks test size and partition overlap.

**Runtime evidence: LIMITED.** There is no runtime event log or independently recorded file
access trace. The manifest asserts one post-selection test touch and its locked-test hash
matches live `test_ids.csv`, but this remains self-authored metadata. Filesystem times place
canonical test outputs at approximately 18:56:53 UTC, the final manifest at 18:58:22 UTC, and
legacy aliases/manifests at approximately 18:59:07 UTC. This is a provenance warning, not
proof of leakage. `documentation/phase3/test_set_lock.md` is hash-registered, but its embedded
test hash is stale (`b7fe...`) versus the live/Phase-6 hash
`a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779`.

## Outputs, aliases, and integrity

The script writes nine canonical CSVs and three figures, including
`phase6_8kpa_baseline_test_metrics.csv`, `phase6_8kpa_calibration_test_metrics.csv`,
`phase6_8kpa_fairness_metrics.csv`, `phase6_8kpa_conformal_metrics.csv`,
`phase6_8kpa_consolidated_comparison.csv`, OOF, development, calibration, and label-audit
files. Manifest and live SHA-256 checks agree for all nine canonical CSVs, all three figures,
the listed inputs, and all six authoritative 8.2 artifacts.

The following later files are aliases or extracts, not names written by the actual script:

- `phase6_8kpa_baseline_results.csv`,
  `phase6_8kpa_calibration_results.csv`, `phase6_8kpa_cohort.csv`,
  `phase6_8kpa_fairness_results.csv`, `phase6_8kpa_conformal_results.csv`, and
  `phase6_8kpa_vs_82_comparison.csv` are byte-identical to their canonical counterparts.
- `phase6_8kpa_age_results.csv` and `phase6_8kpa_bmi_age_results.csv` are exact filtered
  extracts of the canonical fairness table.
- `phase6_8kpa_lineage.json` and `phase6_8kpa_selection_manifest.json` are byte-identical
  copies of `phase6_8kpa_manifest.json`.

These later aliases are not output-hash-listed by the manifest and have later filesystem times.
The current robustness report also differs from its manifest-recorded documentation hash
(the live report points to `phase6_8kpa_lineage.json`, while the source writes
`phase6_8kpa_manifest.json`). No repair was made.

## Metrics and inference

The saved comparison is arithmetically coherent and descriptive:

- 8.0-kPa test AUROC is **0.8075–0.8308** versus authoritative 8.2-kPa
  **0.8229–0.8429**; sensitivity is **0.7385–0.8486** and specificity
  **0.6338–0.7723**.
- BMI-Obese minus Normal sensitivity disparity is **36.7–55.0 percentage points** at 8.0
  kPa, larger in every model than the 8.2 comparison. Age-60+ minus 40–59 disparity is
  **−7.4 to −2.0 points**.
- Overall conformal coverage is **89.1426–90.6337%**; BMI-Obese coverage is
  **79.0487–82.2197%**; Age-60+ coverage is **83.5358–85.0202%**. The saved Wilson intervals
  and BH-adjusted subgroup binomial fields support proportion descriptions only.
- Bootstrap intervals support the recorded AUROC and sensitivity quantities. The consolidated
  comparison does not compute paired/joint 8.2-versus-8.0 intervals, calibration intervals,
  or equivalence/stability tests. No equivalence, unchanged, causal, or deployment claim is
  supported.

The requested `N0` check is not independently expressible: no `N0` field or Phase 6 protocol
definition exists (**N0: NOT FOUND IN REPOSITORY**). Ten BMI×Age fairness rows have zero
positives and are retained as `insufficient evidence`; no overall conformal row has 100%
coverage, and no claim of `N0=0` is invented. Overall empty-set rate is zero for four models;
MLP is 1.5377%, so empty sets are not universally zero.

## Lineage limitations and missing links

Available input/output hashes, runtime metadata, frozen selections, and locked-test hash are
internally consistent for the canonical run. The Phase 6 source itself is not included in its
own source-hash list, no durable retrained model artifacts or calibration-score/prediction-set
files are retained, and no runtime event log exists. The exact required missing tokens are:

- Frozen 8.2 protocol commit: **NOT FOUND IN REPOSITORY**
- Frozen 8.2 model-artifact manifest: **NOT FOUND IN REPOSITORY**

The governing uncertainty and evaluation protocols are present and hash-verified, but the
8.2 frozen protocol commit/model-manifest links are absent. The legacy relabel-only
`sens_03_alternative_threshold.py` explicitly says `retrained=False`; it must not be used as
evidence that the new full retraining did not occur.

## Claim-level disposition

The claim matrix and lineage table are delivered with this audit. The defensible conclusion is
that the descriptive 8.0-kPa results show threshold-sensitive changes, especially larger
BMI-related operating-point disparities, while conformal subgroup undercoverage persists.
The conclusion is accepted with limitations (**B**), not A, because runtime ordering,
8.2 provenance links, durable model lineage, alias provenance, and comparative inference are
incomplete. There is no material implementation defect requiring C.

## Preservation

No tracked prior artifact was modified. Primary 8.2 results, Phase 0–5/7 artifacts,
external-validation notes, master/final-state documents, legacy 8.0 sensitivity files, and the
Phase 6 canonical namespace remain in their original paths. This audit creates only the four
requested files.
