"""
phase6_02_conformal_refit.py
Phase 6 Part 5: conformal-valid model refit. Uses build_pipeline() imported DIRECTLY from the
frozen src/phase3_05_train_and_tune.py -- not reimplemented -- to guarantee identical
preprocessing/estimator construction. Applies each model's exact frozen best_params (extracted
live from the Phase 3 model artifacts, not retyped from memory). Refits on
proper_train_ids.csv ONLY. NO hyperparameter search occurs here.

Original Phase 3 artifacts (models/phase3/*.joblib) are never read for writing, only for
extracting best_params/seed/predictors. Refit artifacts are saved to a distinct directory
(models/phase6_conformal_refit/) with distinct filenames.
"""
import sys
import time
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, SPLIT_DIR, MODEL_DIR, RANDOM_SEED, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES
from phase3_common import load_primary_dataset, fail
from phase3_05_train_and_tune import build_pipeline  # reuse the frozen pipeline-construction function directly

REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"
REFIT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = ROOT / "results" / "uncertainty"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

master = load_primary_dataset()
proper_train_ids = set(pd.read_csv(SPLIT_DIR / "proper_train_ids.csv")["SEQN"])
train_df = master[master["SEQN"].isin(proper_train_ids)].reset_index(drop=True)
if len(train_df) != 4005:
    fail(f"proper_train join produced {len(train_df)} rows, expected 4005")

X = train_df[PRIMARY_PREDICTORS]
y = train_df[PRIMARY_OUTCOME_COL].values
n_pos, n_neg = int(y.sum()), int((y == 0).sum())
print(f"proper_train: N={len(train_df)}, positives={n_pos}, negatives={n_neg}")

registry_rows = []
for name in MODEL_NAMES:
    original = joblib.load(MODEL_DIR / f"model_{name}_v1.joblib")
    best_params = original["best_params"]
    original_seed = original["seed"]
    original_predictors = original["predictors"]

    if original_predictors != PRIMARY_PREDICTORS:
        fail(f"{name}: original model's predictor list does not match frozen PRIMARY_PREDICTORS")
    if original_seed != RANDOM_SEED:
        fail(f"{name}: original model's seed ({original_seed}) does not match frozen RANDOM_SEED ({RANDOM_SEED})")

    t0 = time.time()
    pipe, grid, search_type, n_iter = build_pipeline(name, n_neg, n_pos)  # identical construction to Phase 3
    pipe.set_params(**best_params)  # apply the EXACT frozen best hyperparameters -- no search
    pipe.fit(X, y)
    fit_seconds = time.time() - t0

    proba = pipe.predict_proba(X)[:, 1]
    finite_ok = np.isfinite(proba).all()
    range_ok = ((proba >= 0) & (proba <= 1)).all()

    out_path = REFIT_DIR / f"model_{name}_proper_train_refit.joblib"
    joblib.dump({"pipeline": pipe, "predictors": PRIMARY_PREDICTORS, "seed": RANDOM_SEED,
                 "best_params": best_params, "proper_train_n": len(train_df),
                 "proper_train_positives": n_pos, "proper_train_negatives": n_neg}, out_path)

    registry_rows.append({
        "model": name, "proper_training_n": len(train_df), "proper_training_positives": n_pos,
        "proper_training_negatives": n_neg, "predictors": "|".join(PRIMARY_PREDICTORS),
        "hyperparameters": str(best_params), "preprocessing": "ColumnTransformer(impute=median" +
            (", scale=StandardScaler)" if name in ("logistic", "mlp") else ")"),
        "seed": RANDOM_SEED, "artifact_path": str(out_path.relative_to(ROOT)),
        "artifact_hash": sha256(out_path), "fit_seconds": round(fit_seconds, 3),
        "validation_finite_outputs": bool(finite_ok), "validation_probability_range_0_1": bool(range_ok),
        "validation_feature_count": len(PRIMARY_PREDICTORS), "validation_feature_order_matches_frozen": True,
        "validation_status": "PASS" if (finite_ok and range_ok) else "FAIL",
    })
    print(f"{name}: refit complete in {fit_seconds:.2f}s, finite={finite_ok}, range_ok={range_ok}")

registry = pd.DataFrame(registry_rows)
registry.to_csv(RESULTS_DIR / "conformal_model_refit_registry.csv", index=False)
print(f"\nSaved results/uncertainty/conformal_model_refit_registry.csv")

if (registry["validation_status"] != "PASS").any():
    fail("One or more refit models failed validation -- see conformal_model_refit_registry.csv")
print("\nPASS: all 5 conformal-valid refit models fitted successfully on proper_train_ids.csv only, validated (no test-set use).")
