# Liver Fibrosis ML Reliability Study — repository root

[![tests](https://github.com/kashyapsaksham012/Liver_Fib/actions/workflows/tests.yml/badge.svg)](https://github.com/kashyapsaksham012/Liver_Fib/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Evidence freeze](https://img.shields.io/badge/evidence--freeze-2026--08--27-blue)](https://github.com/kashyapsaksham012/Liver_Fib/releases/tag/evidence-freeze)

This repository contains a single research project: a calibration / fairness / uncertainty
audit of routine-data machine-learning models for **significant liver fibrosis**, built on
NHANES 2017–March 2020. The study is complete and frozen at its pre-manuscript evidence
freeze (git tag `evidence-freeze`).

**The project lives in [`liver_fibrosis_research/`](liver_fibrosis_research/).**
Everything at this top level is orientation only.

## Where to start

1. [`liver_fibrosis_research/documentation/START_HERE.md`](liver_fibrosis_research/documentation/START_HERE.md)
   — **read first, before citing any number.** The research question, cohort, and models, plus
   the documentation authority order, what is superseded, and the four adjudicated internal
   conflicts (C1–C4).
2. [`liver_fibrosis_research/documentation/final_audit/REPRODUCIBILITY.md`](liver_fibrosis_research/documentation/final_audit/REPRODUCIBILITY.md)
   — environment, seeds, input data, and the exact script run order.
3. [`liver_fibrosis_research/documentation/manuscript/MANUSCRIPT_DRAFT.md`](liver_fibrosis_research/documentation/manuscript/MANUSCRIPT_DRAFT.md)
   — working draft (v5), every numeric claim traced to a frozen result artifact.

`info.md` (this directory) is the original research brief the project was scoped from —
kept as historical context, not a current source.

## Paper → repository map

**For a reviewer with `main.pdf` open.** This traces the camera-ready 4-page conference
manuscript (`main.tex`/`main.pdf`, root of this repo) section-by-section to the exact script,
results file, or documentation that produced each claim, table, and figure. Table/figure
references use the manuscript's own `\label{}` names so they match regardless of final print
numbering.

**Verify before citing anything below** — two commands, both read-only:
```bash
cd liver_fibrosis_research
python3 manuscript_verification/verify.py --strict   # expect 59/59
for t in tests/test_*.py; do .venv/bin/python "$t" || echo "FAILED: $t"; done   # expect 18/18
```

Note: this traces the short **camera-ready** manuscript (1 figure, 5 tables). The fuller
**journal draft** (`liver_fibrosis_research/documentation/manuscript/MANUSCRIPT_DRAFT.md`) cites
a larger 8-figure panel per `liver_fibrosis_research/SUBMISSION_PACKAGE.md` — don't expect the
figure list below to match that document.

All paths below are relative to `liver_fibrosis_research/` unless stated otherwise.

### Methods

| Manuscript subsection | Repository path(s) |
|---|---|
| Cohort and Outcome (10,409→7,153 funnel, `LUXSMED≥8.2kPa`, 10 frozen predictors, leakage audit) | `src/01_data_inventory.py` … `15_create_master_dataset.py`; `PHASE1_DATA_ASSEMBLY_REPORT.md`; `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`, `primary_outcome_definition.md`, `prediction_time_and_leakage_protocol.md` |
| — NHB differential-exclusion motivation | `src/mi_01_construct_and_diagnostics.py`; `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` |
| Models and Partitions (5 families, 70/30 split seed 42, N=5,007/2,146) | `src/phase3_02_target_and_features.py`, `phase3_03_split_and_lock.py`, `phase3_05_train_and_tune.py`; `data/processed/splits/`; `models/phase3/`; `PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md` |
| Evaluation (bootstrap CIs, BH-FDR, Platt, split-conformal) | `src/phase3_06_threshold_and_test_eval.py`; `src/phase4_02_primary_metrics.py`, `phase4_05_recalibration.py`; `src/phase6_02_conformal_refit.py`, `phase6_03_conformal_calibration.py` |
| Mitigation and Diagnostics (Mondrian, deferral, reweighting, splines/thresholds/Platt diagnostics, VCTE bias) | Mondrian: `src/phase7_*.py`, `results/mitigation/`. Deferral: `src/deferral_01_dev_and_baseline.py`, `deferral_02_rule_development.py`, `results/selective_deferral/`. Reweighting: `src/ttm_*.py`, `results/training_time_mitigation/`. Diagnostics: `src/sens_04_continuous_splines.py`, `sens_06_group_specific_thresholds.py`, `sens_05_subgroup_recalibration.py`. Matched-stiffness / VCTE bias: `src/cb_05_matched_stiffness.py`, `src/prepub_02_vcte_bias_sensitivity.py` |
| Robustness (8.0kPa threshold, relaxed/fasting cohorts, MI, conformal replication) | `src/sens_01_construct_cohorts.py`, `sens_02_train_evaluate.py`, `sens_03_alternative_threshold.py`, `sens_14_conformal_replication_sensitivity_cohorts.py`; `src/mi_*.py`; `results/sensitivity/` |
| Temporal Validation Cohort | entire [`temporal_validation_2021_2023/`](temporal_validation_2021_2023/) module — own `PROTOCOL_FREEZE.md`, `src/`, `results/`, `figures/` |

### Results

| Manuscript table/figure | Repository path(s) |
|---|---|
| Discrimination and Calibration — Tables `tab:disc`, `tab:calib` | `results/tables/phase3_final_baseline_results.csv`, `phase3_model_comparison_fdr.csv`; `results/calibration/primary_metrics_by_model.csv`, `test_set_calibration_final.csv` |
| Fairness — Table `tab:fair` | `results/fairness/fairness_inference.csv` |
| Conformal Coverage — Table `tab:cov`, Fig. `fig:cov` | `results/uncertainty/marginal_coverage_test_set.csv`, `subgroup_coverage.csv`, `intersectional_coverage_ci.csv`. Figure: `manuscript_figures/main/fig4a_subgroup_coverage_xgboost.png` ← generated by `src/phase6_07_figures.py` from `results/uncertainty/figures/` |
| — dependence-aware co-occurrence permutation test (p=0.12) | `src/rel_01_cooccurrence_analysis.py`, `results/reliability_extension/cooccurrence_correlation_results.csv` |
| Mechanism (splines, per-subgroup thresholds/Platt, matched-stiffness, measurement-bias relabeling) | `results/diagnostics/continuous_age_metrics.csv`; `results/sensitivity/` (group-specific thresholds/recalibration); `results/prepublication_fixes/` (matched-stiffness / VCTE-bias outputs) |
| Mitigation — Table `tab:mit` | `results/mitigation/`, `results/selective_deferral/`, `results/training_time_mitigation/` (per-intervention CSVs backing each row) |
| Robustness and Generalization — sensitivity cohorts, MI, NHB holdout, equal-opportunity postprocessing, predictor importance, **FIB-4 comparison** | Sensitivity: `results/sensitivity/`. MI: `results/sensitivity/` MI outputs + `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md`. NHB holdout: `src/phase8_01_partition_and_leakage_check.py`, `phase8_02_train_and_holdout_evaluate.py`, `models/phase8_holdout/`, `PHASE8_SUBGROUP_HOLDOUT_GENERALIZATION_RESULTS_REPORT.md`. Equal-opportunity postprocessing: `src/sens_07_fairness_postprocessing.py`, `sens_09_correct_fairness_postprocessing.py`, `results/diagnostics/stage1/` (see its README — superseded vs. corrected file). Predictor importance: `results/tables/interpretability_permutation_importance.csv`. **FIB-4**: `src/cb_01_compute_fib4.py` … `cb_06_calibration.py`, `results/clinical_baselines/` (11 files: discrimination, fairness, coverage, matched-stiffness) |
| Temporal Validation (NHANES 2021–2023) — drift, decomposition, BMI gap, coverage, dissociation | `temporal_validation_2021_2023/results/`, `temporal_validation_2021_2023/figures/figT1–T6.{png,pdf}`, `temporal_validation_2021_2023/documentation/TEMPORAL_VALIDATION_REPORT.md` |

### Discussion / Limitations / Conclusion / Declarations

| Manuscript section | Repository path(s) |
|---|---|
| Limitations — survey-weighted check (43–65% BMI-gap attenuation) | `src/svy_01_prevalence.py`, `svy_02_bmi_sensitivity.py`; `documentation/sensitivity/SURVEY_WEIGHTED_REPORT.md` |
| "We claim none of the following…" | `documentation/final_research_audit/DO_NOT_CLAIM.md` (35 items — machine-checked negative-claims list) |
| Conclusion's "per-claim provenance registry" + "automated verification suite" | `documentation/final_research_audit/AUTHORITATIVE_RESULTS.md`; `manuscript_verification/verify.py` + `checks.py` (59 checks) |
| "667 checks across 18 scripts, zero failures" | `tests/` — run via the loop in `tests/README.md` |
| Declarations → Protocol (20 amendments) | `documentation/end_to_end/protocol_amendment_registry.md` |
| Declarations → Data and code | root [`CITATION.cff`](../CITATION.cff), [`LICENSE`](../LICENSE); `data/raw/NHANES_2017_2020/` |



## Model card / datasheet / citation

- [`liver_fibrosis_research/MODEL_CARD.md`](liver_fibrosis_research/MODEL_CARD.md) — intended
  use, performance, and the fairness/reliability limitations, grounded in the frozen results.
- [`liver_fibrosis_research/DATASHEET.md`](liver_fibrosis_research/DATASHEET.md) — the NHANES
  analysis cohort: composition, collection, preprocessing, known caveats.
- [`CITATION.cff`](CITATION.cff) — machine-readable citation (GitHub's "Cite this repository").
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — read before opening a PR; the core study is a frozen,
  append-only evidentiary ledger, not a conventional codebase.

## Environment setup

```bash
cd liver_fibrosis_research
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-phase3-lock.txt   # authoritative pinned versions
```

`requirements-phase3-lock.txt` is the exact lock file used for the frozen results.
`requirements.txt` is the same dependency set unpinned. A single seed (`random_state=42`)
is used throughout. Raw NHANES `.xpt` inputs are public CDC/NCHS files and are included
under `liver_fibrosis_research/data/raw/NHANES_2017_2020/`.

## Branch map

| Branch | Purpose |
|---|---|
| `consolidation/evidence-freeze` | **Authoritative working branch.** All study work landed here; it carries the latest commit. |
| `main` | Release branch. `consolidation/evidence-freeze` is merged into it via pull request (last done in PR #3); its tree is identical to the evidence-freeze branch at each merge point. |
| `experiment/training-time-mitigation` | Amendment #19 work branch (subgroup-reweighting mitigation, verdict negative); its result was consolidated back into the evidence freeze. Kept for provenance. |
| `temporal-validation-standalone` | A NHANES 2021–2023 temporal evaluation that was **split into a separate manuscript** and removed from this study's scope. Not part of this repository's evidence base. |

Tags: `evidence-freeze` (pre-manuscript freeze), `pre-handover-cleanup-2026-08-28`
(state immediately before this repository tidy-up).

## Not tracked here

- `liver_fibrosis_research/.venv/` — local virtual environment, rebuild from the lock file.
- `NHANES 2021–2023 temporal validation dataset/` — raw inputs for the separate
  temporal-validation manuscript; gitignored, not part of this study.

## Known follow-ups for a new maintainer

- ~~Four of the 17 scripts in `liver_fibrosis_research/tests/` reference documentation paths
  that the 2026-08-27 consolidation moved...~~ **Resolved.** The `_doc()` fallback-path helper
  (documented in `liver_fibrosis_research/tests/README.md`, "2026-08-28 maintenance") already
  fixes this. Verified 2026-09-28: all 18 scripts in `liver_fibrosis_research/tests/` pass with
  0 failures (`for t in liver_fibrosis_research/tests/test_*.py; do .venv/bin/python "$t"; done`).
  This bullet was stale — left here so the "it used to be broken" history isn't lost.
- No external (non-NHANES) validation has been performed — the study's foremost stated
  limitation.
- `requirements.txt` and `requirements-phase3.txt` look like avoidable duplicates but are
  **not safe to collapse**: both are named explicitly, by filename, in the frozen
  `liver_fibrosis_research/documentation/final_audit/REPRODUCIBILITY.md` ("`requirements.txt`
  and `requirements-phase3.txt` are the unpinned/earlier variants") as historical artifacts of
  what was actually installed at each stage. Deleting or rewriting either breaks that
  documented, frozen claim's verifiability. `requirements-phase3-lock.txt` remains the
  authoritative file to install from; leave the other two as read-only history.
