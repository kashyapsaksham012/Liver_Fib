"""Shared helpers for the pooled 2017-2023 model-update re-audit.

READ-ONLY on the frozen tree and on temporal_validation_2021_2023/. New models are
written only under pooled_model_update_2017_2023/models/.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PU = HERE.parent                       # pooled_model_update_2017_2023/
REPO = PU.parent                       # liver_fibrosis_research/
TV = REPO / "temporal_validation_2021_2023"

MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
              "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
RACE_MAP = {1: "Mexican American", 2: "Other Hispanic", 3: "Non-Hispanic White",
            4: "Non-Hispanic Black", 6: "Non-Hispanic Asian", 7: "Other Race / Multi-Racial"}
SEED = 42
Z = 1.959963984540054
ALPHA = 0.10

_MANIFEST = PU / "FROZEN_ARTIFACT_MANIFEST.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_frozen(rel_to_repo: str, *, binary=False):
    p = REPO / rel_to_repo
    if not p.exists():
        raise FileNotFoundError(rel_to_repo)
    if _MANIFEST.exists():
        man = pd.read_csv(_MANIFEST).set_index("artifact")["sha256"].to_dict()
        if rel_to_repo in man and sha256(p) != man[rel_to_repo]:
            raise RuntimeError(f"HASH MISMATCH {rel_to_repo} — frozen tree changed. STOP.")
    if binary:
        import joblib
        return joblib.load(p)
    return pd.read_csv(p)


# ---- frozen model recipe (verified against models/phase3/*.joblib) ----

def make_pipeline(name: str, *, scale_pos_weight: float | None = None):
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler

    scaled = name in ("logistic", "mlp")
    steps = [("impute", SimpleImputer(strategy="median"))]
    if scaled:
        steps.append(("scale", StandardScaler()))
    num = Pipeline(steps)
    pre = ColumnTransformer([("num", num, PREDICTORS)], remainder="drop")

    if name == "logistic":
        from sklearn.linear_model import LogisticRegression
        est = LogisticRegression(C=0.01, class_weight="balanced", solver="lbfgs",
                                 max_iter=2000, random_state=SEED)
    elif name == "random_forest":
        from sklearn.ensemble import RandomForestClassifier
        est = RandomForestClassifier(n_estimators=100, max_depth=7, min_samples_leaf=5,
                                     class_weight="balanced", random_state=SEED, n_jobs=-1)
    elif name == "xgboost":
        from xgboost import XGBClassifier
        est = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.7,
                            scale_pos_weight=scale_pos_weight, objective="binary:logistic",
                            eval_metric="logloss", random_state=SEED, n_jobs=-1)
    elif name == "lightgbm":
        from lightgbm import LGBMClassifier
        est = LGBMClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.7,
                             scale_pos_weight=scale_pos_weight, random_state=SEED, n_jobs=-1,
                             verbose=-1)
    elif name == "mlp":
        from sklearn.neural_network import MLPClassifier
        est = MLPClassifier(hidden_layer_sizes=(32, 16), alpha=0.01, learning_rate_init=0.01,
                            early_stopping=True, n_iter_no_change=10, max_iter=1000,
                            solver="adam", random_state=SEED)
    else:
        raise ValueError(name)
    from sklearn.pipeline import Pipeline as P
    return P([("pre", pre), ("est", est)])


# ---- metrics (identical formulas to the frozen study / temporal module) ----

def platt_fit(y, p):
    from scipy.optimize import minimize
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    lg = np.log(p / (1 - p)); y = np.asarray(y, int)

    def nll(par):
        a, b = par
        z = a + b * lg
        return -np.sum(y * z - np.log1p(np.exp(z)))
    r = minimize(nll, [0.0, 1.0], method="Nelder-Mead")
    return float(r.x[0]), float(r.x[1])


def platt_apply(p, a, b):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    z = a + b * np.log(p / (1 - p))
    return 1 / (1 + np.exp(-z))


def calibration_in_the_large(y, p):
    from scipy.optimize import minimize, minimize_scalar
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    lg = np.log(p / (1 - p)); y = np.asarray(y, int)
    slope = float(minimize(lambda par: -np.sum(y * (par[0] + par[1] * lg)
                                                - np.log1p(np.exp(par[0] + par[1] * lg))),
                           [0.0, 1.0], method="Nelder-Mead").x[1])
    a = float(minimize_scalar(lambda a: -np.sum(y * (a + lg) - np.log1p(np.exp(a + lg)))).x)
    return a, slope


def ece_decile(y, p, bins=10):
    y = np.asarray(y, int); p = np.asarray(p, float)
    o = np.argsort(p); y, p = y[o], p[o]; n = len(y)
    edges = np.linspace(0, n, bins + 1).astype(int); e = 0.0
    for i in range(bins):
        s, en = edges[i], edges[i + 1]
        if en > s:
            e += (en - s) / n * abs(p[s:en].mean() - y[s:en].mean())
    return float(e)


def brier(y, p):
    return float(np.mean((np.asarray(p, float) - np.asarray(y, int)) ** 2))


def wilson_ci(k, n, z=Z):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n; d = 1 + z**2 / n
    c = (ph + z**2 / (2 * n)) / d
    h = (z * np.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2))) / d
    return (max(0.0, c - h), min(1.0, c + h))


def bh_fdr(pv):
    p = np.asarray(pv, float); n = len(p)
    order = np.argsort(p); adj = np.empty(n); prev = 1.0
    for rank, i in enumerate(order[::-1]):
        prev = min(prev, p[i] * n / (n - rank)); adj[i] = prev
    return adj


def age_band(a):
    return np.where(a < 40, "18-39", np.where(a < 60, "40-59", "60+"))


def bmi_band(b):
    return np.where(b < 18.5, "Underweight", np.where(b < 25, "Normal",
           np.where(b < 30, "Overweight", "Obese")))
