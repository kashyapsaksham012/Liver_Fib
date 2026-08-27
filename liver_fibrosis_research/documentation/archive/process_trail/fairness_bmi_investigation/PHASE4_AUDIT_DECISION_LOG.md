# Phase 4 Subgroup Calibration Audit Decision Log

| Item | Audit decision | Evidence |
|---|---|---|
| Final disposition | **C. PHASE 4 REQUIRES CORRECTION / RE-EXECUTION** | Equal-width ECE is used in the selection gate despite the frozen equal-frequency-decile protocol; the conformal `global_platt` arm is raw, not globally Platt-calibrated. |
| Audit mode | Read-only; no rerun | Only the four requested audit artifacts were created by this audit. |
| Frozen model set | Verified | Script lines 18-20 uses the five primary models and ten frozen predictors; MLP-balanced is excluded. |
| Frozen thresholds | Verified as carried forward | Script line 19 records the five thresholds; test decisions use raw predictions against those thresholds at lines 123 and 126. |
| OOF data separation | Verified in control flow | OOF files and linked primary metadata are loaded before selection; deterministic sorted-SEQN even/odd fit/evaluation split at lines 45-57. |
| OOF calibration fitting | Verified | Global and estimable cell Platt maps fit on the OOF fit half only at lines 58-63. |
| Sparse-cell handling | Verified with limitation | Cells require at least 20 rows and 10 positive/10 negative observations; output flags 35 unstable rows. |
| ECE protocol compliance | **Not verified / fails** | `ece()` uses ten equal-width bins (`np.linspace(0,1,11)`) at lines 29-34; the frozen protocol requires ten equal-frequency risk deciles. |
| Selection implementation | Arithmetic reproducible, decision invalid for frozen protocol | Gate is implemented at lines 84-90 and selects LightGBM subgroup calibration, but its ECE input is non-conforming and the gate does not require BMI-gap improvement. |
| Locked-test ordering | Static ordering verified; runtime proof incomplete | Manifest write is line 108; test IDs/predictions are first loaded at lines 111-114. No run-event log or timestamped access record exists. |
| Locked-test fitting protection | No evidence of test-label fitting | Test rows are scored after candidate selection; no test labels enter `fit()` in the test block. |
| Locked-test confirmation | Partly supported | Expected N=2,146 and 200 positives are present; LightGBM subgroup and global classifications are unchanged. Exact runtime sequencing is not independently recorded. |
| Conformal comparison labels | **Not supported as labelled** | Lines 97-105 leave `pf`/`pe` raw for the `global_platt` row; only the subgroup arm applies a map. |
| Prior exploratory artifact | Preserved and not merged | Prior `stage0/subgroup_recalibration_metrics.csv` remains separate; its maximum reported coverage change is 0.68 pp. |
| Lineage | Incomplete | `phase4_lineage.json` hashes the script and OOF predictions only; test, dataset, split, refit-model, manifest, output, environment, and runtime hashes/events are absent. |
| Prior/master/Phase 7 artifacts | Not modified by this audit | Audit writes only the four requested files under the fairness-BMI investigation paths. |

## Required future correction (not performed here)

An authorized future run would need to use the frozen ECE binning, explicitly label or correct
the conformal comparator, record complete input/output hashes and execution events, and state
whether the selection rule is intended to optimize calibration only or BMI fairness. This log
does not authorize that work.
