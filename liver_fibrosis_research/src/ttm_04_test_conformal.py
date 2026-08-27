"""
ttm_04_test_conformal.py  --  Amendment #19, Phase 2.2  (LOCKED-TEST TOUCH #2)

The SECOND of the two Amendment-#19 locked-test touches. Mirrors
src/phase6_04_final_test_touch.py exactly, over both arms, using the reweighted proper-train
models (ttm_02) and the per-arm conformal thresholds (ttm_02). All decisions frozen:
nonconformity score 1 - P(true class), Wilson 95% CIs, one-sample binomial vs 0.90, BH-FDR
per (arm x model x dimension).

Run after ttm_00, ttm_02. Env: MLP_FALLBACK=1 if ttm_01 flagged MLP unstable.

Outputs (results/training_time_mitigation/):
  test_conformal_{arm}.csv                (marginal + subgroup coverage)
  test_conformal_intersectional_{arm}.csv (Obese n 60+)
  test_conformal_prediction_sets.csv      (per participant, per arm x model)
  test_touch2_manifest.json
"""
import os
import sys
import json
import datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import ROOT, PROC_DIR, SPLIT_DIR, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES
from phase5_common import SEX_MAP, RACE_MAP_RIDRETH3, bin_age, bin_bmi

OUT = ROOT / "results" / "training_time_mitigation"
MODELS_OUT = ROOT / "models" / "training_time_mitigation"
ARMS = ["A", "B"]
MLP_FALLBACK = os.environ.get("MLP_FALLBACK", "0") == "1"

BASE_BMI_OBESE_COV = {"logistic": 0.8233, "random_forest": 0.8018, "xgboost": 0.7678,
                      "lightgbm": 0.7916, "mlp": 0.8086}
BASE_AGE60_COV = {"logistic": 0.8489, "random_forest": 0.8556, "xgboost": 0.8111,
                  "lightgbm": 0.8475, "mlp": 0.8381}
BASE_MARGINAL = {"logistic": 0.9082, "random_forest": 0.8961, "xgboost": 0.8812,
                 "lightgbm": 0.8961, "mlp": 0.8919}


def wilson(k, n, level=0.95):
    if n == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    ph = k / n
    den = 1 + z**2 / n
    c = (ph + z**2 / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def bh_group(pvals):
    p = np.asarray(pvals, float)
    m = len(p)
    o = np.argsort(p)
    r = p[o]
    adj = np.minimum.accumulate((r * m / (np.arange(m) + 1))[::-1])[::-1].clip(0, 1)
    out = np.empty(m)
    out[o] = adj
    return out


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
    cov_rows, inter_rows, pset_records = [], [], []

    pset_frames = []
    for arm in ARMS:
        thr = pd.read_csv(OUT / f"conformal_thresholds_arm{arm}.csv").set_index("model")["threshold"].to_dict()
        inf = []  # (model, dimension, category, raw_p) for BH
        for name in models:
            art = joblib.load(MODELS_OUT / f"model_{arm}_{name}_proper_train.joblib")
            p_pos = art["pipeline"].predict_proba(X)[:, 1]
            t = thr[name]
            inc_pos = (1 - p_pos) <= t
            inc_neg = p_pos <= t
            size = inc_pos.astype(int) + inc_neg.astype(int)
            covered = np.where(y == 1, inc_pos, inc_neg)

            n = len(y); k = int(covered.sum()); cov = k / n
            lo, hi = wilson(k, n)
            cov_rows.append({"touch_utc": touch_ts, "arm": arm, "model": name, "scope": "marginal",
                             "category": "ALL", "n": n, "n_positive": int(y.sum()),
                             "coverage": round(cov, 6), "wilson_lo": round(lo, 6), "wilson_hi": round(hi, 6),
                             "mean_set_size": round(float(size.mean()), 6),
                             "singleton_rate": round(float((size == 1).mean()), 6),
                             "delta_vs_baseline": round(cov - BASE_MARGINAL[name], 6),
                             "raw_p_vs_0.90": round(stats.binomtest(k, n, 0.90).pvalue, 8),
                             "bh_fdr_p": None, "significant_after_fdr_0.05": None})

            pset_frames.append(pd.DataFrame({
                "SEQN": te["SEQN"].values, "arm": arm, "model": name, "true_target": y,
                "p_pos": p_pos, "include_negative": inc_neg, "include_positive": inc_pos,
                "set_size": size, "covered": covered, "_bmi": te["_bmi"].values,
                "_age": te["_age"].values, "_sex": te["_sex"].values, "_race": te["_race"].values}))

            for dim, col in [("bmi", "_bmi"), ("age", "_age"), ("sex", "_sex"), ("race", "_race")]:
                for cat in te[col].dropna().unique():
                    m = (te[col] == cat).values
                    sn = int(m.sum()); sk = int(covered[m].sum())
                    sc = sk / sn if sn else None
                    slo, shi = wilson(sk, sn)
                    rp = stats.binomtest(sk, sn, 0.90).pvalue if sn else 1.0
                    inf.append((name, dim, cat, rp))
                    cov_rows.append({"touch_utc": touch_ts, "arm": arm, "model": name, "scope": "subgroup",
                                     "category": f"{dim}:{cat}", "n": sn,
                                     "n_positive": int((y[m] == 1).sum()),
                                     "coverage": round(sc, 6), "wilson_lo": round(slo, 6), "wilson_hi": round(shi, 6),
                                     "mean_set_size": round(float(size[m].mean()), 6),
                                     "singleton_rate": round(float((size[m] == 1).mean()), 6),
                                     "delta_vs_baseline": (round(sc - BASE_BMI_OBESE_COV[name], 6) if (dim == "bmi" and cat == "Obese")
                                                           else round(sc - BASE_AGE60_COV[name], 6) if (dim == "age" and cat == "60+")
                                                           else None),
                                     "raw_p_vs_0.90": round(rp, 8), "bh_fdr_p": None,
                                     "significant_after_fdr_0.05": None})

            # intersection Obese n 60+
            mi = ((te["_bmi"] == "Obese") & (te["_age"] == "60+")).values
            ni = int(mi.sum()); ki = int(covered[mi].sum())
            ilo, ihi = wilson(ki, ni)
            inter_rows.append({"touch_utc": touch_ts, "arm": arm, "model": name, "n": ni,
                               "n_positive": int((y[mi] == 1).sum()), "coverage": round(ki / ni, 6),
                               "wilson_lo": round(ilo, 6), "wilson_hi": round(ihi, 6)})
            print(f"[arm {arm}] {name}: marginal {cov:.4f}  BMI-Obese {covered[(te._bmi=='Obese').values].mean():.4f}  "
                  f"Age-60+ {covered[(te._age=='60+').values].mean():.4f}")

        # BH-FDR within (arm x model x dimension)
        idf = pd.DataFrame(inf, columns=["model", "dimension", "category", "raw_p"])
        adj = {}
        for (mdl, dim), g in idf.groupby(["model", "dimension"]):
            a = bh_group(g["raw_p"].values)
            for cat, av in zip(g["category"].values, a):
                adj[(mdl, dim, cat)] = float(av)
        for r in cov_rows:
            if r["arm"] == arm and r["scope"] == "subgroup":
                dim, cat = r["category"].split(":", 1)
                ap = adj.get((r["model"], dim, cat))
                r["bh_fdr_p"] = round(ap, 6) if ap is not None else None
                r["significant_after_fdr_0.05"] = bool(ap < 0.05) if ap is not None else None

    pd.DataFrame(cov_rows).to_csv(OUT / "test_conformal.csv", index=False)
    pd.DataFrame(inter_rows).to_csv(OUT / "test_conformal_intersectional.csv", index=False)
    pd.concat(pset_frames, ignore_index=True).to_csv(OUT / "test_conformal_prediction_sets.csv", index=False)
    (OUT / "test_touch2_manifest.json").write_text(json.dumps(
        {"touch_utc": touch_ts, "script": "ttm_04_test_conformal.py", "leakage_check": leak,
         "arms": ARMS, "models": models, "mlp_fallback": MLP_FALLBACK}, indent=2))
    print(f"\nLOCKED-TEST TOUCH #2 complete: {touch_ts}. Do not re-run.")


if __name__ == "__main__":
    main()
