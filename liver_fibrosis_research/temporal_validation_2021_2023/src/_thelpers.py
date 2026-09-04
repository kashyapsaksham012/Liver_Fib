"""Shared helpers for the NHANES 2021-2023 temporal validation.

READ-ONLY on the frozen tree. All frozen artifacts are loaded through
`load_frozen()`, which verifies the file's SHA-256 against
FROZEN_ARTIFACT_MANIFEST.csv (once it exists).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TV = HERE.parent                      # temporal_validation_2021_2023/
REPO = TV.parent                      # liver_fibrosis_research/
RAW = REPO.parent / "NHANES 2021–2023 temporal validation dataset"

MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
              "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
LAB_PREDICTORS = ["LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]

# frozen operating thresholds (Youden on OOF) — from phase3_final_baseline_results.csv
YOUDEN = {"logistic": 0.5173, "random_forest": 0.4499, "xgboost": 0.4108,
          "lightgbm": 0.4988, "mlp": 0.1065}
# frozen Platt (intercept, slope) fit on OOF in phase4_05
PLATT = {"logistic": (-2.242509, 1.060614), "random_forest": (-1.86245, 1.198516),
         "xgboost": (-2.046007, 1.03932), "lightgbm": (-2.053483, 1.06221),
         "mlp": (-0.280858, 0.829627)}
# frozen split-conformal nonconformity thresholds — conformal_thresholds_by_model.csv
CONF_THR = {"logistic": 0.672744, "random_forest": 0.607211, "xgboost": 0.653193,
            "lightgbm": 0.656959, "mlp": 0.377967}

RACE_MAP = {1: "Mexican American", 2: "Other Hispanic", 3: "Non-Hispanic White",
            4: "Non-Hispanic Black", 6: "Non-Hispanic Asian", 7: "Other Race / Multi-Racial"}

SEED = 42
Z = 1.959963984540054   # norm.ppf(0.975)

_MANIFEST = TV / "FROZEN_ARTIFACT_MANIFEST.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_frozen(rel_to_repo: str, *, binary=False):
    """Load a frozen artifact by path relative to liver_fibrosis_research/,
    asserting its hash against FROZEN_ARTIFACT_MANIFEST.csv if that file exists."""
    p = REPO / rel_to_repo
    if not p.exists():
        raise FileNotFoundError(rel_to_repo)
    if _MANIFEST.exists():
        man = pd.read_csv(_MANIFEST).set_index("artifact")["sha256"].to_dict()
        if rel_to_repo in man:
            got = sha256(p)
            if got != man[rel_to_repo]:
                raise RuntimeError(
                    f"HASH MISMATCH for {rel_to_repo}\n  manifest: {man[rel_to_repo]}\n  on disk : {got}\n"
                    "The frozen tree has changed since the protocol was frozen. STOP.")
    if binary:
        import joblib
        return joblib.load(p)
    return pd.read_csv(p)


def platt_apply(p_raw, intercept, slope):
    """recalibrated = sigmoid(intercept + slope * logit(p_raw)); matches Amendment #8."""
    p = np.clip(np.asarray(p_raw, float), 1e-6, 1 - 1e-6)
    z = intercept + slope * np.log(p / (1 - p))
    return 1 / (1 + np.exp(-z))


def wilson_ci(k, n, z=Z):
    """Exact formula copied from src/phase6_04_final_test_touch.py."""
    if n == 0:
        return (float("nan"), float("nan"))
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def calibration_in_the_large(y, p):
    """intercept & slope of logistic recalibration fit; matches Phase 4 method.
    slope  = coef from logistic regression of y on logit(p);
    intercept = MLE of a in  y ~ Bernoulli(sigmoid(a + logit(p)))  (slope fixed at 1).
    """
    from scipy.optimize import minimize_scalar
    from scipy.optimize import minimize
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    lg = np.log(p / (1 - p))
    y = np.asarray(y, int)

    def nll_bs(params):
        b0, b1 = params
        z = b0 + b1 * lg
        return -np.sum(y * z - np.log1p(np.exp(z)))
    res = minimize(nll_bs, x0=[0.0, 1.0], method="Nelder-Mead")
    slope = float(res.x[1])

    def nll_a(a):
        z = a + lg
        return -np.sum(y * z - np.log1p(np.exp(z)))
    a = float(minimize_scalar(nll_a).x)
    return a, slope


def ece_decile(y, p, bins=10):
    y = np.asarray(y, int); p = np.asarray(p, float)
    order = np.argsort(p)
    y, p = y[order], p[order]
    n = len(y)
    edges = np.linspace(0, n, bins + 1).astype(int)
    e = 0.0
    for i in range(bins):
        s, en = edges[i], edges[i + 1]
        if en <= s:
            continue
        e += (en - s) / n * abs(p[s:en].mean() - y[s:en].mean())
    return float(e)


def brier(y, p):
    return float(np.mean((np.asarray(p, float) - np.asarray(y, int)) ** 2))


def boot_ci(fn, *arrays, n=2000, seed=SEED, alpha=0.05):
    rng = np.random.default_rng(seed)
    N = len(arrays[0])
    vals = []
    for _ in range(n):
        idx = rng.integers(0, N, N)
        try:
            vals.append(fn(*[a[idx] for a in arrays]))
        except Exception:
            pass
    vals = np.array(vals)
    return (float(np.nanpercentile(vals, 100 * alpha / 2)),
            float(np.nanpercentile(vals, 100 * (1 - alpha / 2))))


def bh_fdr(pvals):
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    adj = np.empty(n)
    prev = 1.0
    for rank, i in enumerate(order[::-1]):
        r = n - rank
        prev = min(prev, p[i] * n / r)
        adj[i] = prev
    return adj


def age_band(a):
    return np.where(a < 40, "18-39", np.where(a < 60, "40-59", "60+"))


def bmi_band(b):
    return np.where(b < 18.5, "Underweight",
           np.where(b < 25, "Normal",
           np.where(b < 30, "Overweight", "Obese")))


def touch_log(entry: str):
    """Append-only machine execution log. The curated human summary is
    documentation/TEMPORAL_TOUCH_LOG.md, maintained by hand."""
    p = TV / "documentation" / "TEMPORAL_EXECUTION_LOG.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("# Temporal execution log (append-only, machine-written)\n\n"
                     "Every run of a script that reads the 2021-2023 primary outcome. "
                     "Reproducibility re-runs are deterministic (seed 42) and add a row "
                     "here without changing any result. Curated summary: `TEMPORAL_TOUCH_LOG.md`.\n\n"
                     "| UTC | script | cohort SHA (16) | nature |\n|---|---|---|---|\n")
    with open(p, "a") as f:
        f.write(entry.rstrip() + "\n")
