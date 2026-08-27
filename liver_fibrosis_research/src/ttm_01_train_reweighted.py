"""
ttm_01_train_reweighted.py  --  Amendment #19, Phase 1.2 / 1.3 / 1.5

Retrain the five frozen model families on the FULL training partition (N = 5,007) with
subgroup instance reweighting (Kamiran & Calders reweighing, from ttm_00), for both arms.
Then derive Youden thresholds and OOF Platt parameters on the new out-of-fold predictions,
and run the pre-test mechanism diagnostic (§1.5).

NON-NEGOTIABLES (Amendment #19):
  - frozen Phase-3 best_params, extracted live from models/phase3/model_{name}_v1.joblib
  - NO hyperparameter search
  - build_pipeline() imported directly from src/phase3_05_train_and_tune.py
  - 5-fold StratifiedKFold(shuffle=True, random_state=42) -- the frozen CV design
  - base class-imbalance handling KEPT; subgroup weights applied ON TOP via sample_weight
  - MLP has no sample_weight -> weighted resampling strictly inside each training fold
    (np.random.default_rng(42)); early_stopping=True kept to match the frozen MLP and
    Amendment #3. If OOF AUROC SD across seeds {42,43,44} > 0.01 the operator sets
    MLP_FALLBACK=1 and MLP is reported "not applicable in the frozen implementation".
  - THE LOCKED TEST SET IS NEVER LOADED IN THIS SCRIPT.

Run:  python3 src/ttm_00_compute_weights.py   (first)
      python3 src/ttm_01_train_reweighted.py

Outputs (results/training_time_mitigation/):
  oof_predictions_{arm}_{model}.csv          (SEQN, true_target, predicted_probability)
  youden_thresholds_{arm}.csv
  platt_params_{arm}.csv
  phase1_mechanism_diagnostic.csv
Models (models/training_time_mitigation/):
  model_{arm}_{model}.joblib
"""
import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (ROOT, PROC_DIR, SPLIT_DIR, MODEL_DIR, PRED_DIR, RANDOM_SEED,
                           N_CV_FOLDS, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES)
from phase3_05_train_and_tune import build_pipeline  # frozen pipeline construction

OUT = ROOT / "results" / "training_time_mitigation"
MODELS_OUT = ROOT / "models" / "training_time_mitigation"
MODELS_OUT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

ARMS = ["A", "B"]
WEIGHT_CAPABLE = {"logistic", "random_forest", "xgboost", "lightgbm"}
MLP_FALLBACK = os.environ.get("MLP_FALLBACK", "0") == "1"
MLP_SEEDS = [42, 43, 44]
EPS = 1e-12


def logit(p):
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def fit_platt(y, p):
    """Frozen Phase-4 method: LogisticRegression(C=1e10) of y on logit(p)."""
    z = logit(np.asarray(p)).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])


def youden_j(y, p):
    fpr, tpr, thr = roc_curve(y, p)
    return float(thr[np.argmax(tpr - fpr)])


def load_frozen_best_params():
    bp = {}
    for name in MODEL_NAMES:
        art = joblib.load(MODEL_DIR / f"model_{name}_v1.joblib")
        if art["predictors"] != PRIMARY_PREDICTORS:
            raise SystemExit(f"{name}: frozen model predictor list mismatch")
        if art["seed"] != RANDOM_SEED:
            raise SystemExit(f"{name}: frozen model seed mismatch")
        bp[name] = art["best_params"]
    return bp


def weighted_resample_idx(y, w, rng):
    """Expand indices so row i appears ~ w_i / min(w) times (floor + Bernoulli remainder).
    Implements weighted ERM by resampling; keeps y binary. Used for MLP only."""
    ratio = w / w.min()
    base = np.floor(ratio).astype(int)
    frac = ratio - base
    extra = (rng.random(len(w)) < frac).astype(int)
    counts = base + extra
    return np.repeat(np.arange(len(y)), counts)


def make_estimator_pipeline(name, n_neg, n_pos, best_params):
    pipe, _, _, _ = build_pipeline(name, n_neg, n_pos)
    pipe.set_params(**best_params)
    return pipe


def fit_with_weights(name, pipe, X, y, w, rng):
    """LR/RF/XGB/LGBM: native sample_weight. MLP: weighted resampling (rng)."""
    if name in WEIGHT_CAPABLE:
        pipe.fit(X, y, est__sample_weight=w)
        return pipe
    # MLP
    idx = weighted_resample_idx(y.values if hasattr(y, "values") else y, w, rng)
    Xr = X.iloc[idx].reset_index(drop=True)
    yr = (y.values if hasattr(y, "values") else y)[idx]
    pipe.fit(Xr, yr)
    return pipe


def oof_predict(name, X, y, w, best_params, n_neg, n_pos, mlp_seed=RANDOM_SEED):
    cv = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    oof = np.full(len(y), np.nan)
    rng = np.random.default_rng(mlp_seed)
    yv = y.values if hasattr(y, "values") else y
    for tr_idx, te_idx in cv.split(X, yv):
        pipe = make_estimator_pipeline(name, n_neg, n_pos, best_params)
        Xtr, ytr, wtr = X.iloc[tr_idx], yv[tr_idx], w[tr_idx]
        # xgb/lgb scale_pos_weight from THIS fold's class counts (mirrors sens_02 / frozen behaviour)
        if name in ("xgboost", "lightgbm"):
            fp, fn = int(ytr.sum()), int((ytr == 0).sum())
            pipe.named_steps["est"].set_params(scale_pos_weight=fn / fp)
        pipe = fit_with_weights(name, pipe, Xtr, pd.Series(ytr), wtr, rng)
        oof[te_idx] = pipe.predict_proba(X.iloc[te_idx])[:, 1]
    assert np.isfinite(oof).all()
    return oof


def bmi_shortcut_coef(df_scores):
    """OLS predicted_probability ~ LUXSMED + is_obese in the 8.2-12 kPa band (Amdt #18 C4)."""
    b = df_scores[(df_scores.LUXSMED >= 8.2) & (df_scores.LUXSMED < 12) &
                  df_scores.bmi_group_final.isin(["Normal", "Obese"])].copy()
    if len(b) < 20:
        return np.nan
    b["is_obese"] = (b.bmi_group_final == "Obese").astype(float)
    Xd = np.column_stack([np.ones(len(b)), b.LUXSMED.to_numpy(), b.is_obese.to_numpy()])
    beta, *_ = np.linalg.lstsq(Xd, b.predicted_probability.to_numpy(), rcond=None)
    return float(beta[2])


def main():
    best_params = load_frozen_best_params()
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    df["SEQN"] = df["SEQN"].astype("int64")
    train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"].astype("int64"))
    tr = df[df.SEQN.isin(train_ids)].reset_index(drop=True)
    assert len(tr) == 5007 and int(tr[PRIMARY_OUTCOME_COL].sum()) == 466

    X = tr[PRIMARY_PREDICTORS]
    y = tr[PRIMARY_OUTCOME_COL].astype(int)
    n_pos, n_neg = int(y.sum()), int((y == 0).sum())

    # baseline OOF (frozen) for the mechanism diagnostic
    base_oof = {m: pd.read_csv(PRED_DIR / f"validation_predictions_{m}.csv").set_index("SEQN")
                for m in MODEL_NAMES}

    diag_rows = []
    for arm in ARMS:
        wdf = pd.read_csv(OUT / f"weights_arm{arm}_train.csv")
        wdf["SEQN"] = wdf["SEQN"].astype("int64")
        w = tr[["SEQN"]].merge(wdf[["SEQN", "weight"]], on="SEQN", how="left")["weight"].to_numpy()
        assert np.isfinite(w).all(), f"arm {arm}: weight join produced NaN"
        assert abs(w.mean() - 1.0) < 1e-6, f"arm {arm}: weights not mean-1 ({w.mean():.6f})"

        youden, platt = {}, {}
        for name in MODEL_NAMES:
            if name == "mlp" and MLP_FALLBACK:
                print(f"[arm {arm}] mlp: FALLBACK -- not applicable in frozen implementation, skipped")
                continue

            if name == "mlp":
                # 3-seed stability check on OOF AUROC
                aucs = []
                for s in MLP_SEEDS:
                    o = oof_predict(name, X, y, w, best_params[name], n_neg, n_pos, mlp_seed=s)
                    aucs.append(roc_auc_score(y, o))
                sd = float(np.std(aucs))
                print(f"[arm {arm}] mlp 3-seed OOF AUROC = {[round(a,4) for a in aucs]}  SD={sd:.4f}")
                if sd > 0.01:
                    print(f"[arm {arm}] mlp: UNSTABLE (SD>{0.01}); set MLP_FALLBACK=1 and re-run. Skipping mlp for now.")
                    diag_rows.append({"arm": arm, "model": "mlp", "note": f"UNSTABLE OOF AUROC SD={sd:.4f}"})
                    continue

            oof = oof_predict(name, X, y, w, best_params[name], n_neg, n_pos)
            oof_df = pd.DataFrame({"SEQN": tr["SEQN"].values, "true_target": y.values,
                                   "predicted_probability": oof})
            oof_df.to_csv(OUT / f"oof_predictions_{arm}_{name}.csv", index=False)

            youden[name] = youden_j(y.values, oof)
            platt[name] = fit_platt(y.values, oof)

            # final model on full training partition, with weights
            final = make_estimator_pipeline(name, n_neg, n_pos, best_params[name])
            if name in ("xgboost", "lightgbm"):
                final.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
            rng = np.random.default_rng(RANDOM_SEED)
            final = fit_with_weights(name, final, X, y, w, rng)
            joblib.dump({"pipeline": final, "arm": arm, "model": name, "predictors": PRIMARY_PREDICTORS,
                         "seed": RANDOM_SEED, "best_params": best_params[name],
                         "weight_scheme": f"kamiran_calders_arm{arm}", "train_n": len(tr),
                         "youden_threshold": youden[name], "platt": platt[name],
                         "mlp_handling": "weighted_resample_rng42" if name == "mlp" else "native_sample_weight"},
                        MODELS_OUT / f"model_{arm}_{name}.joblib")

            # --- §1.5 mechanism diagnostic (OOF only) ---
            m_tr = tr.copy()
            m_tr["predicted_probability"] = oof
            nb = m_tr[m_tr.bmi_group_final == "Normal"]
            nb_auc = roc_auc_score(nb[PRIMARY_OUTCOME_COL], nb["predicted_probability"]) if nb[PRIMARY_OUTCOME_COL].nunique() > 1 else np.nan
            base = base_oof[name].reindex(tr["SEQN"].values)["predicted_probability"].to_numpy()
            m_base = tr.copy(); m_base["predicted_probability"] = base
            nbb = m_base[m_base.bmi_group_final == "Normal"]
            nb_auc_base = roc_auc_score(nbb[PRIMARY_OUTCOME_COL], nbb["predicted_probability"]) if nbb[PRIMARY_OUTCOME_COL].nunique() > 1 else np.nan
            sep = (nb.loc[nb[PRIMARY_OUTCOME_COL] == 1, "predicted_probability"].median()
                   - nb.loc[nb[PRIMARY_OUTCOME_COL] == 0, "predicted_probability"].median())
            sep_base = (nbb.loc[nbb[PRIMARY_OUTCOME_COL] == 1, "predicted_probability"].median()
                        - nbb.loc[nbb[PRIMARY_OUTCOME_COL] == 0, "predicted_probability"].median())
            diag_rows.append({
                "arm": arm, "model": name,
                "normal_bmi_oof_auc_baseline": round(float(nb_auc_base), 4),
                "normal_bmi_oof_auc_reweighted": round(float(nb_auc), 4),
                "normal_bmi_oof_auc_delta": round(float(nb_auc - nb_auc_base), 4),
                "normal_bmi_score_separation_baseline": round(float(sep_base), 4),
                "normal_bmi_score_separation_reweighted": round(float(sep), 4),
                "bmi_shortcut_coef_baseline": round(bmi_shortcut_coef(m_base), 4),
                "bmi_shortcut_coef_reweighted": round(bmi_shortcut_coef(m_tr), 4),
                "youden_threshold": round(youden[name], 4),
                "platt_intercept": round(platt[name][0], 4), "platt_slope": round(platt[name][1], 4),
            })
            print(f"[arm {arm}] {name}: Normal-BMI OOF AUC {nb_auc_base:.4f} -> {nb_auc:.4f}  "
                  f"(shortcut coef {bmi_shortcut_coef(m_base):.3f} -> {bmi_shortcut_coef(m_tr):.3f})")

        if youden:
            pd.DataFrame([{"model": k, "youden_threshold": v} for k, v in youden.items()]).to_csv(
                OUT / f"youden_thresholds_arm{arm}.csv", index=False)
            pd.DataFrame([{"model": k, "platt_intercept": v[0], "platt_slope": v[1]} for k, v in platt.items()]).to_csv(
                OUT / f"platt_params_arm{arm}.csv", index=False)

    pd.DataFrame(diag_rows).to_csv(OUT / "phase1_mechanism_diagnostic.csv", index=False)
    print(f"\nWrote {OUT}/phase1_mechanism_diagnostic.csv and per-arm OOF / threshold / platt files.")
    print("THE LOCKED TEST SET WAS NEVER LOADED IN THIS SCRIPT.")


if __name__ == "__main__":
    main()
