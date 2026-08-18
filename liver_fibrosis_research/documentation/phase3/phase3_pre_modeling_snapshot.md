# Phase 3 Pre-Modeling Snapshot

**Generated:** 2026-08-18 (Phase 3, Part 2)

## Version / Environment Record

- **Git commit (HEAD) at Phase 3 start:** `b390fbeeda3dd85fcc20420dbd486990734bd418`
- **Phase 2 protocol freeze checksum:** `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` SHA-256 =
  `8fa176f2b43e91fcf6ad23afd33f25a59625f66afe65817e61db709b7143b801`
- **Primary analysis dataset checksum:** `data/processed/analysis_dataset_primary.parquet` SHA-256 =
  `1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938`
- **Python version:** 3.14 (project-local virtual environment `.venv/`, created for Phase 3 — the
  Phase 1/2 pipeline used the system Homebrew Python 3.14.3 directly since it needed no ML libraries;
  Phase 3 requires scikit-learn/XGBoost/LightGBM, which are isolated into `.venv/` rather than installed
  into the system Python)
- **Package versions:** scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0, pandas 3.0.5, numpy 2.5.2,
  scipy 1.18.0 (see `requirements-phase3.txt`)
- **Operating environment:** macOS (Darwin), arm64 (Apple Silicon)
- **Execution date:** 2026-08-18
- **Random-seed configuration:** `RANDOM_SEED = 42`, fixed now for the train/test split, CV fold
  assignment, and all stochastic model components (Random Forest, XGBoost, LightGBM, MLP
  initialization) — per the deferral explicitly noted in `documentation/phase2/model_development_protocol.md`
  Part 4 ("a single fixed seed will be recorded ... at the start of Phase 3").
- **Phase 2 protocol version:** the frozen `PHASE2_PROTOCOL_FREEZE.md` as of Phase 2 closure, zero
  amendments logged.

## Environment Setup Note (disclosed transparently)

Installing XGBoost required the OpenMP runtime (`libomp`) via Homebrew, since it was not already present
on this machine. Running `brew install libomp` triggered Homebrew's automatic `autoremove` step, which
**unintentionally uninstalled `mongosh`** (MongoDB Shell, unrelated to this project) because it was
flagged as an unneeded dependency at that moment. This was noticed immediately and corrected by
reinstalling `mongosh` (now v2.9.2, previously v2.8.2) before continuing. This is disclosed here for
full transparency, per the project's reproducibility standard — it is not a project-scientific decision,
but it is a real side effect of this session's environment setup and should not be silently omitted.

## Scope Confirmation

Phase 3 will train baseline models, perform cross-validated hyperparameter search, and produce locked
test-set discrimination results only. It will NOT perform calibration fitting, fairness optimization,
conformal prediction, or uncertainty modeling — those remain designated later phases, per the governing
instructions.
