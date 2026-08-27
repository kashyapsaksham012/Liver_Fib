# Phase 4 Corrected Final Post-Audit

**Scope:** Read-only audit of the corrected Phase 4 subgroup-calibration execution. No
experiment was rerun and no existing script, result, calibration method/parameter, prior
Phase 4, exploratory, Phase 0–3, Phase 7, or master artifact was modified.

## Final decision: B

**B — the corrected conclusion is accepted with documented limitations.** The main conclusion,
that no acceptable subgroup-calibration improvement was demonstrated for the BMI fairness/
reliability objective, is supported by the corrected development and locked-test files. This
is not an A because prospective provenance for the new selection gate, runtime test-access
proof, formal comparative inference, and one duplicate output's generation record remain
limited. It is not C: the material defects identified in the historical run were corrected.

## Materials inspected

- Corrected source: `src/run_phase4_corrected_subgroup_calibration.py`
- Corrected namespace: `results/fairness_bmi_investigation/phase4_corrected/`
- Corrected report, decision log, and correction record in
  `documentation/fairness_bmi_investigation/`
- Frozen protocol and data-flow records:
  `documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md`,
  `phase4_pre_execution_snapshot.md`, `phase4_calibration_data_flow.md`
- Locked-test protection record:
  `results/calibration/phase4_test_set_protection_audit.md`
- Historical run:
  `src/run_phase4_subgroup_calibration.py` and
  `results/fairness_bmi_investigation/phase4_subgroup_calibration/`
- Prior exploratory artifact:
  `src/sens_05_subgroup_recalibration.py` and
  `results/diagnostics/stage0/subgroup_recalibration_metrics.csv`
- Phase 0/3 lineage records and the conformal protocol.

## Direct findings

### Protocol, ECE, and model scope

The corrected script uses the five frozen primary models, ten frozen predictors, primary
outcome, BMI/age definitions, and frozen raw-probability thresholds. Its ECE implementation
uses ten equal-frequency risk deciles (`ece_equal_frequency`, lines 98–116), matching the
frozen calibration protocol. `ece_validation.csv` contains 11/11 `PASS` rows; the maximum
implementation/reference difference is approximately `1.04e-17`. This is an implementation
and protocol check, not an inferential test of candidate superiority. The calibration-detail
file also records intercept, slope, Brier, and ECE for every overall, BMI, age, and BMI×Age
scope; overall OOF evaluation intercepts range from 0.016 to 0.186 and slopes from 1.037 to
1.098 across candidate rows.

### Separation, mappings, and fallback

OOF rows are sorted by `SEQN` and split into 2,504 fit and 2,503 evaluation participants
(236 and 230 positives, respectively). The conformal-development comparison uses 501 fit and
501 evaluation participants (40 and 53 positives). Platt maps are fit on the relevant fit
partition and applied to the separate evaluation partition.

The corrected conformal output explicitly records `map_applied_to_fit=True` and
`map_applied_to_eval=True` for all ten rows. The global arm is labeled
`GLOBAL_PLATT_FIT_APPLIED`; the subgroup arm is
`SUBGROUP_PLATT_WITH_EXPLICIT_FALLBACK`. Cell requirements are `n >= 20`, positive count
`>= 10`, and negative count `>= 10`; non-estimable cells fall back BMI-first, then age, then
global. Source-count fields expose the fallback rather than silently hiding it. The
BMI×Age rows are therefore descriptive under this precedence rule, not estimates from a
jointly fitted intersectional calibrator.

### Selection rule and exact choices

The implemented gate is: subgroup ECE must improve; Brier must be no more than 0.01 worse;
overall sensitivity and specificity must be within five percentage points; and the absolute
Age-60-versus-Age-40 sensitivity gap must not increase by more than five percentage points.
The exact OOF choices are:

| Model | Choice | Global ECE | Subgroup ECE | Global Brier | Subgroup Brier | Reason |
|---|---|---:|---:|---:|---:|---|
| logistic | `global_platt` | 0.011405 | 0.012541 | 0.070526 | 0.070422 | Subgroup ECE worsened |
| random_forest | `subgroup_platt_bmi_age` | 0.012617 | 0.009186 | 0.070515 | 0.070438 | ECE improved; safety constraints unchanged |
| xgboost | `subgroup_platt_bmi_age` | 0.011953 | 0.011650 | 0.070135 | 0.070099 | ECE improved; safety constraints unchanged |
| lightgbm | `subgroup_platt_bmi_age` | 0.010716 | 0.008069 | 0.069982 | 0.070004 | ECE improved; Brier increase is far below +0.01 |
| mlp | `global_platt` | 0.009280 | 0.010509 | 0.069849 | 0.069771 | Subgroup ECE worsened |

The gate is arithmetically reproducible from the corrected comparison file. However, the
repository does not provide a separate prospective freeze for this new subgroup-analysis
gate; its historical pre-specification cannot be independently established.

### Fairness, age, and BMI×Age results

Because classification uses the unchanged raw prediction against the frozen threshold,
probability transformations do not change classification decisions. OOF Obese-minus-Normal
sensitivity gaps are 50.40, 39.86, 37.95, 38.62, and 39.88 percentage points for Logistic,
Random Forest, XGBoost, LightGBM, and MLP, identical for both candidates. Locked-test gaps
are 47.66, 31.62, 31.36, 27.08, and 39.03 percentage points; every selected-vs-global
change is 0.000 pp.

Locked-test Age-60-minus-Age-40 sensitivity gaps are −8.55, −13.16, −11.24, −14.15, and
−14.67 percentage points in the same model order. The corrected output includes all
BMI×Age scopes. For the Obese×60+ intersection, the locked-test scope is `n=294` with
61 positives; its metrics are produced under the documented BMI-first/age-second fallback,
not a joint map. No corrected output supplies a formal p-value or comparative CI for
candidate differences, so no significance or equivalence claim is made.

### Conformal comparison

The corrected conformal comparison is a valid same-framework development comparison because
both arms fit and apply their maps before recomputing the finite-sample split-conformal
threshold:

| Model | Global coverage | Subgroup coverage | Global mean set size | Subgroup mean set size |
|---|---:|---:|---:|---:|
| logistic | 0.8862 | 0.8882 | 0.9601 | 0.9621 |
| random_forest | 0.8862 | 0.8862 | 0.9721 | 0.9721 |
| xgboost | 0.8782 | 0.8802 | 0.9601 | 0.9601 |
| lightgbm | 0.8782 | 0.8842 | 0.9521 | 0.9641 |
| mlp | 0.8902 | 0.8902 | 0.9681 | 0.9681 |

The file provides Wilson intervals for these descriptive development estimates; it does not
establish population-level subgroup coverage or comparative significance. The conformal
development sample is 501/501, smaller than the eventual locked test, and is not a substitute
for external validation.

### Locked-test order and runtime proof

Static inspection verifies the intended order: OOF development and conformal comparison
precede selection; the selection manifest is written at line 650; test IDs and test
prediction files are first loaded at lines 653 and 660. The source therefore protects the
test from fitting and selection in the recorded control flow. The lineage runtime metadata
records start/finish times and explicitly says runtime event logging was unavailable.
Consequently, exact runtime access order is **partially**, not independently, proven.

### Lineage and preservation

The corrected lineage records hashes for the script, primary dataset, split files, OOF and
test predictions, conformal refit joblibs, protocol, manifest, corrected outputs, and
figures. The hashes match the current files for those listed artifacts. One additional file,
`phase4_corrected_ece_validation.csv`, exists and is byte-identical to `ece_validation.csv`
and is listed in the lineage JSON, but it is not in the current script's `outputs` list and
the script does not write it. Its content is harmlessly duplicative, but its generation
provenance is not established; this is a lineage limitation.

The historical Phase 4 namespace and the prior exploratory artifact remain present, with
distinct source scripts and hashes. The corrected run does not merge, relabel, or overwrite
them. The prior exploratory result remains a separate, narrower artifact (reported coverage
change range −0.54 to +0.68 percentage points) and is not used as evidence for the corrected
conformal comparator.

## Claim disposition

| Claim | Status |
|---|---|
| Corrected ECE follows the frozen ten equal-frequency-bin definition | Supported |
| Both conformal arms actually map probabilities | Supported |
| Fit/evaluation separation and explicit cell fallback are implemented | Supported |
| Test access follows selection in source control flow | Partially supported: no runtime event log |
| Exact choices follow the coded gate | Supported arithmetically; prospective freeze not independently proven |
| Subgroup calibration improves BMI classification fairness | Not supported; decisions and gaps are unchanged |
| Corrected candidate differences are statistically significant/equivalent | Not supported; no such inference was produced |
| BMI×Age received joint intersectional calibration | Not supported |
| Prior artifacts were preserved and separated | Supported |
| “No acceptable subgroup-calibration improvement identified” | Supported with the stated BMI/reliability scope |

**Conclusion:** Decision **B**. The corrected Phase 4 conclusion may be retained with the
limitations above; it must not be expanded into a claim of universal fairness, joint
intersectional mitigation, statistical superiority, or external validity.
