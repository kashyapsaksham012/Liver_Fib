"""
ttm_02_conformal_refit_reweighted.py  --  Amendment #19, Phase 1.4

Refit the five families on the PROPER-TRAIN subset (N = 4,005) with subgroup instance
reweighting (Arm A and Arm B weights recomputed on proper-train by ttm_00), then derive the
split-conformal threshold on the UNWEIGHTED conformal-calibration set (N = 1,002).

Mirrors src/phase6_02_conformal_refit.py + src/phase6_03_conformal_calibration.py exactly,
adding only `est__sample_weight` (LR/RF/XGB/LGBM) or weighted resampling (MLP, rng 42) to the
proper-train fit. The conformal-calibration set and the locked test are NEVER weighted.
THE LOCKED TEST SET IS NEVER LOADED IN THIS SCRIPT.

Run after ttm_00 (and ttm_01, for the MLP_FALLBACK flag consistency).

Outputs (results/training_time_mitigation/):
  conformal_calibration_scores_{arm}_{model}.csv   (SEQN, true_target, p_pos, nonconformity)
  conformal_thresholds_{arm}.csv
Models (models/training_time_mitigation/):
  model_{arm}_{model}_proper_train.joblib
"""
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (ROOT, PROC_DIR, SPLIT_DIR, MODEL_DIR, RANDOM_SEED,
                           PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES)
from phase3_05_train_and_tune import build_pipeline
from ttm_01_train_reweighted import (load_frozen_best_params, make_estimator_pipeline,
                                     fit_with_weights, WEIGHT_CAPABLE)

OUT = ROOT / "results" / "training_time_mitigation"
MODELS_OUT = ROOT / "models" / "training_time_mitigation"
ARMS = ["A", "B"]
TARGET_COVERAGE = 0.90
ALPHA = 1 - TARGET_COVERAGE
MLP_FALLBACK = os.environ.get("MLP_FALLBACK", "0") == "1"


def main():
    best_params = load_frozen_best_params()
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    df["SEQN"] = df["SEQN"].astype("int64")

    pt_ids = set(pd.read_csv(SPLIT_DIR / "proper_train_ids.csv")["SEQN"].astype("int64"))
    cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"].astype("int64"))
    test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"].astype("int64"))
    assert pt_ids.isdisjoint(cal_ids) and pt_ids.isdisjoint(test_ids) and cal_ids.isdisjoint(test_ids)

    pt = df[df.SEQN.isin(pt_ids)].reset_index(drop=True)
    cal = df[df.SEQN.isin(cal_ids)].reset_index(drop=True)
    assert len(pt) == 4005 and int(pt[PRIMARY_OUTCOME_COL].sum()) == 373
    assert len(cal) == 1002 and int(cal[PRIMARY_OUTCOME_COL].sum()) == 93

    Xpt, ypt = pt[PRIMARY_PREDICTORS], pt[PRIMARY_OUTCOME_COL].astype(int)
    n_pos, n_neg = int(ypt.sum()), int((ypt == 0).sum())
    Xcal = cal[PRIMARY_PREDICTORS]
    ycal = cal[PRIMARY_OUTCOME_COL].values
    n_cal = len(cal)
    k = int(np.ceil((n_cal + 1) * (1 - ALPHA)))  # = 903

    for arm in ARMS:
        wdf = pd.read_csv(OUT / f"weights_arm{arm}_propertrain.csv")
        wdf["SEQN"] = wdf["SEQN"].astype("int64")
        w = pt[["SEQN"]].merge(wdf[["SEQN", "weight"]], on="SEQN", how="left")["weight"].to_numpy()
        assert np.isfinite(w).all() and abs(w.mean() - 1.0) < 1e-6

        rows = []
        for name in MODEL_NAMES:
            if name == "mlp" and MLP_FALLBACK:
                print(f"[arm {arm}] mlp: FALLBACK -- skipped")
                continue
            pipe = make_estimator_pipeline(name, n_neg, n_pos, best_params[name])
            if name in ("xgboost", "lightgbm"):
                pipe.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
            rng = np.random.default_rng(RANDOM_SEED)
            pipe = fit_with_weights(name, pipe, Xpt, ypt, w, rng)
            joblib.dump({"pipeline": pipe, "arm": arm, "model": name, "predictors": PRIMARY_PREDICTORS,
                         "seed": RANDOM_SEED, "best_params": best_params[name],
                         "weight_scheme": f"kamiran_calders_arm{arm}", "proper_train_n": len(pt),
                         "mlp_handling": "weighted_resample_rng42" if name == "mlp" else "native_sample_weight"},
                        MODELS_OUT / f"model_{arm}_{name}_proper_train.joblib")

            p_pos = pipe.predict_proba(Xcal)[:, 1]
            assert np.isfinite(p_pos).all() and ((p_pos >= 0) & (p_pos <= 1)).all()
            p_true = np.where(ycal == 1, p_pos, 1 - p_pos)
            scores = 1 - p_true
            sorted_s = np.sort(scores)
            threshold = float(sorted_s[k - 1]) if k <= n_cal else np.inf

            pd.DataFrame({"SEQN": cal["SEQN"].values, "true_target": ycal,
                          "predicted_probability_positive": p_pos,
                          "nonconformity_score": scores}).to_csv(
                OUT / f"conformal_calibration_scores_{arm}_{name}.csv", index=False)

            rows.append({"arm": arm, "model": name, "calibration_n": n_cal,
                         "k_finite_sample": k, "quantile_level": round(k / n_cal, 6),
                         "threshold": round(threshold, 6),
                         "score_definition": "1 - P(y=true_class | x)"})
            print(f"[arm {arm}] {name}: conformal threshold q_hat = {threshold:.6f}")

        pd.DataFrame(rows).to_csv(OUT / f"conformal_thresholds_arm{arm}.csv", index=False)

    print(f"\nWrote {OUT}/conformal_thresholds_arm{{A,B}}.csv and per-model calibration scores.")
    print("Conformal-calibration and locked-test rows were NEVER weighted. Test set NOT loaded.")


if __name__ == "__main__":
    main()
