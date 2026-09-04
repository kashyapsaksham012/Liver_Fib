"""Phase 3-7 — retrain the five families on the pooled training partition with the
frozen hyperparameters, derive OOF predictions, Youden thresholds, OOF Platt
parameters, and the split-conformal refit + nonconformity quantile.

Locked test is NOT touched here.
"""
from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split

from _phelpers import (PU, MODELS, PREDICTORS, SEED, ALPHA, make_pipeline, platt_fit)

DATA = PU / "data" / "processed"
MDIR = PU / "models"; MDIR.mkdir(exist_ok=True)
RES = PU / "results"; RES.mkdir(exist_ok=True)


def youden_threshold(y, p):
    from sklearn.metrics import roc_curve
    fpr, tpr, thr = roc_curve(y, p)
    return float(thr[np.argmax(tpr - fpr)])


def main():
    pool = pd.read_parquet(DATA / "pooled_cohort_2017_2023.parquet")
    tr = pool[pool.split == "train"].reset_index(drop=True)
    Xtr, ytr = tr[PREDICTORS], tr["outcome_primary_8.2kPa"].values
    spw = (ytr == 0).sum() / (ytr == 1).sum()   # scale_pos_weight for xgb/lgbm
    print(f"train N={len(tr)}  pos={ytr.sum()}  scale_pos_weight={spw:.4f}")

    skf = StratifiedKFold(5, shuffle=True, random_state=SEED)
    oof = pd.DataFrame({"SEQN": tr["SEQN"], "y": ytr})
    params = {}

    for m in MODELS:
        # full-train fit (fairness / discrimination / calibration)
        pipe = make_pipeline(m, scale_pos_weight=spw)
        pipe.fit(Xtr, ytr)
        joblib.dump({"pipeline": pipe, "predictors": PREDICTORS, "seed": SEED,
                     "scale_pos_weight": spw, "trained_on": "pooled 2017-2023 train N=%d" % len(tr)},
                    MDIR / f"pooled_{m}.joblib")

        # OOF predictions
        oof_p = np.zeros(len(tr))
        for k, (i, j) in enumerate(skf.split(Xtr, ytr)):
            f = make_pipeline(m, scale_pos_weight=(ytr[i] == 0).sum() / (ytr[i] == 1).sum()
                              if m in ("xgboost", "lightgbm") else None)
            f.fit(Xtr.iloc[i], ytr[i])
            oof_p[j] = f.predict_proba(Xtr.iloc[j])[:, 1]
        oof[m] = oof_p

        thr = youden_threshold(ytr, oof_p)
        a, b = platt_fit(ytr, oof_p)

        # conformal: 80/20 stratified split of the training partition
        pt, cal = train_test_split(np.arange(len(tr)), test_size=0.20, random_state=SEED,
                                   stratify=ytr)
        cpipe = make_pipeline(m, scale_pos_weight=(ytr[pt] == 0).sum() / (ytr[pt] == 1).sum()
                              if m in ("xgboost", "lightgbm") else None)
        cpipe.fit(Xtr.iloc[pt], ytr[pt])
        joblib.dump({"pipeline": cpipe, "predictors": PREDICTORS, "proper_train_n": len(pt)},
                    MDIR / f"pooled_{m}_conformal_refit.joblib")
        p_cal = cpipe.predict_proba(Xtr.iloc[cal])[:, 1]
        y_cal = ytr[cal]
        # nonconformity score of the true class
        s_cal = np.where(y_cal == 1, 1 - p_cal, p_cal)
        n_cal = len(s_cal)
        kk = int(np.ceil((n_cal + 1) * (1 - ALPHA)))
        q = float(np.sort(s_cal)[min(kk, n_cal) - 1])

        params[m] = {"youden_threshold": round(thr, 6),
                     "platt_intercept": round(a, 6), "platt_slope": round(b, 6),
                     "conformal_n_cal": n_cal, "conformal_k": kk,
                     "conformal_threshold": round(q, 6)}
        print(f"  {m}: thr={thr:.4f}  platt=({a:.3f},{b:.3f})  conf_q={q:.4f}")

    oof.to_csv(RES / "pooled_oof_predictions.csv", index=False)
    (RES / "pooled_frozen_params.json").write_text(json.dumps(params, indent=2))
    print(f"\nwrote {MDIR}/pooled_*.joblib, {RES}/pooled_oof_predictions.csv, pooled_frozen_params.json")


if __name__ == "__main__":
    main()
