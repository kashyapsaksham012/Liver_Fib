# Temporal execution log (append-only, machine-written)

Every run of a script that reads the 2021-2023 primary outcome. Reproducibility re-runs are deterministic (seed 42) and add a row here without changing any result. Curated summary: `TEMPORAL_TOUCH_LOG.md`.

| UTC | script | cohort SHA (16) | nature |
|---|---|---|---|
| 2026-09-04T09:54:47.446705+00:00 | t03_apply_and_evaluate.py | cohort SHA 59daca140e683d66 | single non-iterative evaluation of frozen phase3 + phase6-refit models on the 2021-2023 primary outcome (raw predictors, no crosswalk). Discrimination, calibration, fairness, conformal, dissociation, matched-stiffness shortcut. Leakage: temporal cohort SEQN disjoint from 2017-2020 by construction (different cycle).
