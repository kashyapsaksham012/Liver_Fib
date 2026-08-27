"""
ttm_03_test_classification.py  --  Amendment #19, Phase 2.1  (LOCKED-TEST TOUCH #1)

The FIRST of the two Amendment-#19 locked-test touches. All decisions are frozen: the
reweighted models (ttm_01), their Youden thresholds and OOF Platt parameters (ttm_01), the
subgroup bins (phase5_common), the bootstrap procedure (2,000 resamples, seed 42), and the
BH-FDR family (one per arm x model x dimension). This single script:
  1. Loads the locked test set once and scores it with the reweighted final models.
  2. Computes discrimination + calibration (raw and OOF-Platt-recalibrated).
  3. Computes subgroup sensitivity (BMI, age, sex, race) with bootstrap CIs and BH-FDR.
  4. Writes deltas vs the frozen baseline.
No inspect-modify-rerun iteration follows this script.

Run after ttm_00, ttm_01. Env: MLP_FALLBACK=1 if ttm_01 flagged MLP unstable.

Outputs (results/training_time_mitigation/):
  test_classification_{arm}.csv
  test_subgroup_sensitivity_{arm}.csv
  test_touch1_manifest.json
"""
import os
import sys
import json
import datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import ROOT, PROC_DIR, SPLIT_DIR, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES
from phase5_common import SEX_MAP, RACE_MAP_RIDRETH3, bin_age, bin_bmi

OUT = ROOT / "results" / "training_time_mitigation"
MODELS_OUT = ROOT / "models" / "training_time_mitigation"
ARMS = ["A", "B"]
NBOOT = 2000
SEED = 42
EPS = 1e-12
MLP_FALLBACK = os.environ.get("MLP_FALLBACK", "0") == "1"

# frozen baseline (PRE_EXECUTION_SNAPSHOT.md §0.3.5) -- Obese-minus-Normal sensitivity disparity (pp)
BASE_OBESE_MINUS_NORMAL = {"logistic": 47.6623, "random_forest": 31.6234, "xgboost": 31.3636,
                           "lightgbm": 27.0779, "mlp": 39.0260}
BASE_AGE60_MINUS_4059 = {"logistic": -8.5509, "random_forest": -13.1563, "xgboost": -11.2361,
                         "lightgbm": -14.1464, "mlp": -14.6715}
BASE_AUROC = {"logistic": 0.8334, "random_forest": 0.8343, "xgboost": 0.8429,
              "lightgbm": 0.8394, "mlp": 0.8229}
BASE_SENS = {"logistic": 0.750, "random_forest": 0.790, "xgboost": 0.845, "lightgbm": 0.795, "mlp": 0.815}
BASE_SPEC = {"logistic": 0.7621, "random_forest": 0.7359, "xgboost": 0.6773, "lightgbm": 0.7492, "mlp": 0.6644}


def logit(p):
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def cal_in_large(y, p):
    z = logit(np.asarray(p)).reshape(-1, 1)
    r = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000).fit(z, y)
    return float(r.intercept_[0]), float(r.coef_[0][0])


def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    e, n = 0.0, len(y)
    for i in range(bins):
        m = (p >= edges[i]) & (p < edges[i + 1]) if i < bins - 1 else (p >= edges[i]) & (p <= edges[i + 1])
        if m.sum():
            e += m.sum() / n * abs(y[m].mean() - p[m].mean())
    return float(e)


def bh(pvals):
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adj = ranked * m / (np.arange(m) + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1].clip(0, 1)
    out = np.empty(m)
    out[order] = adj
    return out


def boot_sens_gap(y_t, yhat_t, y_r, yhat_r, rng):
    d = []
    for _ in range(NBOOT):
        it = rng.integers(0, len(y_t), len(y_t))
        ir = rng.integers(0, len(y_r), len(y_r))
        yt, ht = y_t[it], yhat_t[it]
        yr, hr = y_r[ir], yhat_r[ir]
        if (yt == 1).sum() == 0 or (yr == 1).sum() == 0:
            continue
        d.append(100 * ((ht[yt == 1] == 1).mean() - (hr[yr == 1] == 1).mean()))
    return (np.percentile(d, 2.5), np.percentile(d, 97.5)) if d else (np.nan, np.nan)


def main():
    train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"].astype("int64"))
    pt_ids = set(pd.read_csv(SPLIT_DIR / "proper_train_ids.csv")["SEQN"].astype("int64"))
    cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"].astype("int64"))
    test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"].astype("int64"))
    leak = {"test_x_train": len(test_ids & train_ids), "test_x_propertrain": len(test_ids & pt_ids),
            "test_x_calibration": len(test_ids & cal_ids)}
    assert set(leak.values()) == {0}, f"LEAKAGE {leak}"

    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    df["SEQN"] = df["SEQN"].astype("int64")
    te = df[df.SEQN.isin(test_ids)].reset_index(drop=True)
    assert len(te) == 2146 and int(te[PRIMARY_OUTCOME_COL].sum()) == 200
    te["_sex"] = te["RIAGENDR"].map(SEX_MAP)
    te["_race"] = te["RIDRETH3"].map(RACE_MAP_RIDRETH3)
    te["_age"] = te["RIDAGEYR"].apply(bin_age)
    te["_bmi"] = te["BMXBMI"].apply(bin_bmi)
    X = te[PRIMARY_PREDICTORS]
    y = te[PRIMARY_OUTCOME_COL].values

    models = [m for m in MODEL_NAMES if not (m == "mlp" and MLP_FALLBACK)]
    touch_ts = dt.datetime.now(dt.timezone.utc).isoformat()
    disc_rows, sub_rows = [], []

    for arm in ARMS:
        yth = pd.read_csv(OUT / f"youden_thresholds_arm{arm}.csv").set_index("model")["youden_threshold"].to_dict()
        plt = pd.read_csv(OUT / f"platt_params_arm{arm}.csv").set_index("model")
        for name in models:
            art = joblib.load(MODELS_OUT / f"model_{arm}_{name}.joblib")
            p_raw = art["pipeline"].predict_proba(X)[:, 1]
            tau = yth[name]
            yhat = (p_raw >= tau).astype(int)
            b0, b1 = float(plt.loc[name, "platt_intercept"]), float(plt.loc[name, "platt_slope"])
            p_recal = sigmoid(b0 + b1 * logit(p_raw))

            rng = np.random.default_rng(SEED)
            auc = roc_auc_score(y, p_raw)
            ab = [roc_auc_score(y[i], p_raw[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(NBOOT))
                  if len(np.unique(y[i])) == 2]
            tp = int(((y == 1) & (yhat == 1)).sum()); fn = int(((y == 1) & (yhat == 0)).sum())
            tn = int(((y == 0) & (yhat == 0)).sum()); fp = int(((y == 0) & (yhat == 1)).sum())
            sens, spec = tp / (tp + fn), tn / (tn + fp)
            i_raw, s_raw = cal_in_large(y, p_raw)
            i_rec, s_rec = cal_in_large(y, p_recal)
            disc_rows.append({
                "touch_utc": touch_ts, "arm": arm, "model": name, "n": len(y),
                "test_auroc": round(auc, 6), "auroc_ci_lo": round(np.percentile(ab, 2.5), 6),
                "auroc_ci_hi": round(np.percentile(ab, 97.5), 6),
                "test_pr_auc": round(average_precision_score(y, p_raw), 6),
                "sensitivity": round(sens, 6), "specificity": round(spec, 6),
                "youden_threshold": round(tau, 6),
                "calib_intercept_raw": round(i_raw, 4), "calib_slope_raw": round(s_raw, 4),
                "calib_intercept_recal": round(i_rec, 4), "calib_slope_recal": round(s_rec, 4),
                "brier_raw": round(brier_score_loss(y, p_raw), 6),
                "brier_recal": round(brier_score_loss(y, p_recal), 6),
                "ece_raw": round(ece(y, p_raw), 6), "ece_recal": round(ece(y, p_recal), 6),
                "delta_auroc_vs_baseline": round(auc - BASE_AUROC[name], 6),
                "delta_sens_vs_baseline": round(sens - BASE_SENS[name], 6),
                "delta_spec_vs_baseline": round(spec - BASE_SPEC[name], 6),
            })

            # subgroup sensitivity + BH-FDR per (arm, model, dimension)
            for dim, col, ref in [("bmi", "_bmi", "Normal"), ("age", "_age", "40-59"),
                                  ("sex", "_sex", "Male"), ("race", "_race", "Non-Hispanic White")]:
                cats = [c for c in te[col].dropna().unique() if c != ref]
                rmask = (te[col] == ref).values
                yr, hr = y[rmask], yhat[rmask]
                pv = []
                tmp = []
                for cat in cats:
                    tmask = (te[col] == cat).values
                    yt, ht = y[tmask], yhat[tmask]
                    npos_t, npos_r = int((yt == 1).sum()), int((yr == 1).sum())
                    if npos_t == 0 or npos_r == 0:
                        tmp.append((cat, npos_t, np.nan, np.nan, np.nan, np.nan, np.nan)); pv.append(1.0); continue
                    st = (ht[yt == 1] == 1).mean(); sr = (hr[yr == 1] == 1).mean()
                    rng2 = np.random.default_rng(SEED)
                    lo, hi = boot_sens_gap(yt, ht, yr, hr, rng2)
                    # bootstrap p: fraction of resamples with gap crossing 0
                    d = []
                    for _ in range(NBOOT):
                        it = rng2.integers(0, len(yt), len(yt)); ir = rng2.integers(0, len(yr), len(yr))
                        if (yt[it] == 1).sum() == 0 or (yr[ir] == 1).sum() == 0:
                            continue
                        d.append((ht[it][yt[it] == 1] == 1).mean() - (hr[ir][yr[ir] == 1] == 1).mean())
                    d = np.array(d)
                    raw_p = 2 * min((d <= 0).mean(), (d >= 0).mean()) if len(d) else 1.0
                    pv.append(raw_p)
                    tmp.append((cat, npos_t, round(st, 6), round(sr, 6), round(100 * (st - sr), 4),
                                round(lo, 4), round(hi, 4)))
                adj = bh(pv)
                for (cat, npos_t, st, sr, gap, lo, hi), a, rp in zip(tmp, adj, pv):
                    sub_rows.append({
                        "touch_utc": touch_ts, "arm": arm, "model": name, "dimension": dim,
                        "category": cat, "reference": ref, "n_positive_target": npos_t,
                        "subgroup_sensitivity": st, "reference_sensitivity": sr,
                        "disparity_pp": gap, "ci_lo_pp": lo, "ci_hi_pp": hi,
                        "raw_p": round(float(rp), 6), "bh_fdr_p": round(float(a), 6),
                        "significant_after_fdr_0.05": bool(a < 0.05),
                        "delta_vs_baseline_pp": (round(gap - BASE_OBESE_MINUS_NORMAL[name], 4) if (dim == "bmi" and cat == "Obese")
                                                 else round(gap - BASE_AGE60_MINUS_4059[name], 4) if (dim == "age" and cat == "60+")
                                                 else None),
                    })
            print(f"[arm {arm}] {name}: AUROC {auc:.4f} (Δ{auc-BASE_AUROC[name]:+.4f}), sens {sens:.3f}, spec {spec:.3f}")

    pd.DataFrame(disc_rows).to_csv(OUT / "test_classification.csv", index=False)
    pd.DataFrame(sub_rows).to_csv(OUT / "test_subgroup_sensitivity.csv", index=False)
    (OUT / "test_touch1_manifest.json").write_text(json.dumps(
        {"touch_utc": touch_ts, "script": "ttm_03_test_classification.py", "leakage_check": leak,
         "arms": ARMS, "models": models, "mlp_fallback": MLP_FALLBACK}, indent=2))
    print(f"\nLOCKED-TEST TOUCH #1 complete: {touch_ts}. Do not re-run.")


if __name__ == "__main__":
    main()
