# Phase 3 Pre-Remediation Snapshot

**Generated:** 2026-08-18 (Phase 3 Remediation, Part 3A) — the original report is archived alongside this
file as `PHASE3_REPORT_pre_remediation_20260818.md` and is NOT overwritten by this remediation; the
live `PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md` will be replaced with a remediated
version at the end of this pass.

## Git / Working-Tree State

- **Git commit (HEAD) at remediation start:** `b390fbeeda3dd85fcc20420dbd486990734bd418`
- **Working-tree status:** 54 modified/untracked files (all Phase 2/3 outputs generated since the last
  commit) — unchanged from before this remediation began; no commits made by this remediation pass.

## Artifact SHA-256 Hashes (as of remediation start)

| Artifact | SHA-256 |
|---|---|
| `data/processed/analysis_dataset_primary.parquet` | `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938` |
| `data/processed/splits/train_ids.csv` | `ae5c5124c4d47deb0c256747c591159afa2782304a9c54e29f7105c72e12ecb4` |
| `data/processed/splits/test_ids.csv` | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| `models/phase3/model_logistic_v1.joblib` | `ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5` |
| `models/phase3/model_random_forest_v1.joblib` | `37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a` |
| `models/phase3/model_xgboost_v1.joblib` | `8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4` |
| `models/phase3/model_lightgbm_v1.joblib` | `dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02` |
| `models/phase3/model_mlp_v1.joblib` | `4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc` |
| `results/predictions/test_predictions_logistic.csv` | `87fa5df55f55ae749e70205eaab0fb6a57b0650e25fa901a824b15ccd1a8cd45` |
| `results/predictions/test_predictions_random_forest.csv` | `25088452a18af7c6a88438049fff12b3346db7f9387051245059879bb76f373e` |
| `results/predictions/test_predictions_xgboost.csv` | `651ef1bcbbd2f36121a26f52508479349b25b526bc7563bef183efc7f5e57e4a` |
| `results/predictions/test_predictions_lightgbm.csv` | `eb9e7c78a6f3dc1c6854b7b7b6a66be64c0ae4910f7f7b69181d8a13c2d3e1ad` |
| `results/predictions/test_predictions_mlp.csv` | `a48b0a2d9d6c7c827adbc8e5682f512cf291042d75055c2ec6d33f8395d4bc51` |
| Original `PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md` | `42b63f53a062812251ab349cd173dd544361c574bb585869139702f45b237490` |

## Environment (as of remediation start)

- **Python:** 3.14.3 (project-local `.venv/`)
- **Packages (exact, `pip freeze`):** joblib==1.5.3, lightgbm==4.7.0, matplotlib==3.11.1, numpy==2.5.2,
  pandas==3.0.5, pyarrow==25.0.1, scikit-learn==1.9.0, scipy==1.18.0, seaborn==0.13.2, xgboost==3.4.1 —
  pinned in `requirements-phase3-lock.txt` (new deliverable; the prior `requirements-phase3.txt` used
  loose `>=` ranges only)
- **Random seed:** 42 (unchanged)
- **Protocol version:** `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`, zero amendments (Phase 3
  remediation may add Phase-3-specific methodological clarifications, logged separately — see
  `inference_methodology_amendment.md`, `threshold_selection_audit.md` — these are Phase 3
  implementation clarifications of protocol items Phase 2 explicitly deferred, not changes to any
  frozen Phase 2 decision)

## Scope of This Remediation Pass (confirmed before any change)

Audited, not blindly rebuilt: MLP class-imbalance asymmetry, CV-vs-"validation" terminology, threshold-
selection provenance, CI/bootstrap/FDR protocol status, model-selection/retention rule, model-
comparability assumptions, PR-AUC interpretation, hypothesis-language precision, reproducibility/
environment verification, and test-set-lock chronological integrity. Phase 1 and Phase 2 frozen
decisions (cohort N=7,153, outcome LUXSMED>=8.2kPa, 666 positive, 10 predictors, race/ethnicity
exclusion, complete-case missing-data strategy) are NOT reopened — Part 3B below re-confirms this
independently rather than assuming it.
