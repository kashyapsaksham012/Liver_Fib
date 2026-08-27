# Operator execution guide — Amendment #19 Phases 1–2

The pre-registration (Phase 0) is committed. Phases 1–2 need `scikit-learn 1.9.0`, `xgboost 3.4.1`,
`lightgbm 4.7.0`, `imbalanced-learn 0.14.2` (see `requirements-phase3-lock.txt`) — not available in
the plan-authoring environment. Run these on the full pinned environment, in order. **Do not edit
the scripts after reading a locked-test result.** If something fails, fix and re-run *before* any
`ttm_03` / `ttm_04` run — those are the two locked-test touches and must each run exactly once.

```
# --- Phase 1 (no locked-test access) ---
python3 src/ttm_00_compute_weights.py            # weights (already runs; pure pandas)
python3 src/ttm_01_train_reweighted.py           # retrain 5 families x 2 arms; OOF; thresholds; diagnostic
python3 src/ttm_02_conformal_refit_reweighted.py # proper-train refit x 2 arms; conformal thresholds

# inspect the Phase-1 mechanism diagnostic BEFORE touching the test:
#   results/training_time_mitigation/phase1_mechanism_diagnostic.csv
# If within-Normal-BMI OOF AUROC does not rise for any model AND score separation does not widen,
# the Phase-2 verdict is expected to be NEGATIVE (no efficacy) -- still run Phase 2 for the record.

# --- MLP stability gate (ttm_01 prints this) ---
# ttm_01 runs a 3-seed OOF-AUROC check for MLP. If SD > 0.01 it prints
#   "mlp: UNSTABLE ... set MLP_FALLBACK=1 and re-run".
# Then re-run Phase 1 and all of Phase 2 with:  export MLP_FALLBACK=1
# (MLP is then reported "not applicable in the frozen implementation"; the gate's ">=4/5"
#  thresholds become ">=3/4", as pre-registered in AMENDMENT_19_TEXT.md.)

# --- Phase 2 (the two locked-test touches) ---
python3 src/ttm_03_test_classification.py        # LOCKED-TEST TOUCH #1
python3 src/ttm_04_test_conformal.py             # LOCKED-TEST TOUCH #2

# --- validate ---
python3 tests/test_training_time_mitigation.py   # T16-T18 now run
```

Then send back (or commit on this branch) the contents of `results/training_time_mitigation/`:
`phase1_mechanism_diagnostic.csv`, `youden_thresholds_arm{A,B}.csv`, `platt_params_arm{A,B}.csv`,
`conformal_thresholds_arm{A,B}.csv`, `test_classification.csv`, `test_subgroup_sensitivity.csv`,
`test_conformal.csv`, `test_conformal_intersectional.csv`, `test_touch{1,2}_manifest.json`.
Phases 3–5 (gate application, comparison, manuscript, closure) run from those CSVs.

## What each script does / does not touch

| script | reads | writes | locked test? |
|---|---|---|---|
| `ttm_00` | parquet, `train_ids`, `proper_train_ids` | `weights_arm{A,B}_{train,propertrain}.csv` | no |
| `ttm_01` | parquet, `train_ids`, `models/phase3/*.joblib` (best_params only), baseline OOF | OOF preds, thresholds, Platt params, `model_{arm}_{model}.joblib`, mechanism diagnostic | **no** — asserts test set never loaded |
| `ttm_02` | parquet, `proper_train_ids`, `conformal_calibration_ids`, best_params | conformal calibration scores, `conformal_thresholds_arm{A,B}.csv`, `model_{arm}_{model}_proper_train.joblib` | **no** |
| `ttm_03` | `test_ids`, `model_{arm}_{model}.joblib`, thresholds, Platt | `test_classification.csv`, `test_subgroup_sensitivity.csv`, `test_touch1_manifest.json` | **TOUCH #1** |
| `ttm_04` | `test_ids`, `model_{arm}_{model}_proper_train.joblib`, `conformal_thresholds_arm*` | `test_conformal.csv`, intersectional, prediction sets, `test_touch2_manifest.json` | **TOUCH #2** |

## Pre-registered gate (from `TRAINING_TIME_MITIGATION_PLAN.md` §0.3.6) — reference

G1 sensitivity efficacy · G2 coverage efficacy · G3 marginal ∈ [0.87, 0.93] · G4 AUROC within −0.02
· G5 Brier within +0.01 · G6 no age-gap / sex / race harm · G7 overall sens+spec within 5 pp.
SUCCESS = G1–G7 all pass (arm A). PARTIAL = exactly one of G1/G2 + G3–G7. NEGATIVE (cost) = an
efficacy gate passes but a cost gate fails. NEGATIVE (no efficacy) = neither G1 nor G2.
