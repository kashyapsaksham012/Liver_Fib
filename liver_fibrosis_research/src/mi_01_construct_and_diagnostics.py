"""
mi_01_construct_and_diagnostics.py
Multiple-imputation sensitivity analysis, Part 6: construct m=5 imputed datasets (Amendment
#12: IterativeImputer(BayesianRidge()), seed=42+i) on the full N=7,768 quality-valid adult pool,
and report diagnostics (missingness before/after, imputed-value distributions).

IMPORTANT SCOPE NOTE: these are STATIC datasets, each imputer fit on the FULL pool at once, used
ONLY for descriptive diagnostics in this script (missingness patterns, imputed-value ranges).
They are NOT used for the leakage-safety-critical model-refit/prediction step -- that step
(mi_02_black_subgroup_comparison.py) fits a fresh IterativeImputer inside each CV fold's training
portion only, exactly mirroring the leakage-safe Pipeline pattern already established in Phase 3.
This separation is deliberate and is restated in mi_02 to avoid any ambiguity.

Does NOT touch the locked test set. Outcome (LUXSMED) is never imputed (0% missing) and is never
used as an imputation predictor, per the frozen protocol's "outcome-independent" requirement.
"""
import sys
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import INT_DIR
from _cohorts import COHORT_3B_ADULT_OF_QUALITY_VALID
from phase3_common import ROOT, PRIMARY_PREDICTORS, RANDOM_SEED

RESULTS_DIR = ROOT / "results" / "sensitivity"
M_IMPUTATIONS = 5

def sha256_df(df):
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()

master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
mask, meta = COHORT_3B_ADULT_OF_QUALITY_VALID(master)
pool = master[mask].reset_index(drop=True).copy()
if len(pool) != 7768:
    print(f"PHASE 8-PRE STOP CONDITION: pool N={len(pool)}, expected 7768"); sys.exit(1)

pool["outcome_primary_8.2kPa"] = (pool["LUXSMED"] >= 8.2).astype(int)

missing_before = pool[PRIMARY_PREDICTORS].isna().sum()
print("=== Missingness BEFORE imputation (full pool, N=7768) ===")
print(missing_before.to_string())

diagnostics_rows = []
hashes = []
for i in range(M_IMPUTATIONS):
    seed = RANDOM_SEED + i
    X = pool[PRIMARY_PREDICTORS].copy()
    imputer = IterativeImputer(estimator=BayesianRidge(), random_state=seed, max_iter=10, sample_posterior=True)
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=PRIMARY_PREDICTORS, index=X.index)

    missing_after = X_imputed.isna().sum().sum()
    n_iter_run = imputer.n_iter_

    imputed_df = pool[["SEQN", "outcome_primary_8.2kPa"]].join(X_imputed)
    out_path = RESULTS_DIR / f"mi_imputed_dataset_{i}.csv"
    imputed_df.to_csv(out_path, index=False)
    file_hash = hashlib.sha256(out_path.read_bytes()).hexdigest()
    hashes.append(file_hash)

    for col in PRIMARY_PREDICTORS:
        n_imputed = int(pool[col].isna().sum())
        if n_imputed == 0:
            continue
        original_vals = pool.loc[pool[col].notna(), col]
        imputed_vals = X_imputed.loc[pool[col].isna(), col]
        diagnostics_rows.append({
            "imputation_index": i, "seed": seed, "variable": col,
            "n_missing_imputed": n_imputed,
            "observed_mean": round(original_vals.mean(), 4), "observed_std": round(original_vals.std(), 4),
            "imputed_mean": round(imputed_vals.mean(), 4), "imputed_std": round(imputed_vals.std(), 4),
            "imputer_n_iter": n_iter_run, "missing_after_imputation": int(missing_after),
        })
    print(f"Imputation {i} (seed={seed}): complete, n_iter={n_iter_run}, missing_after={missing_after}, saved to {out_path.name} (hash {file_hash[:12]}...)")

diag_out = pd.DataFrame(diagnostics_rows)
diag_out.to_csv(RESULTS_DIR / "multiple_imputation_diagnostics.csv", index=False)

registry_rows = []
for i in range(M_IMPUTATIONS):
    registry_rows.append({
        "imputation_index": i, "seed": RANDOM_SEED + i, "method": "IterativeImputer(estimator=BayesianRidge())",
        "pool_n": len(pool), "predictors_imputed": "|".join([c for c in PRIMARY_PREDICTORS if pool[c].isna().any()]),
        "predictors_not_imputed": "|".join([c for c in PRIMARY_PREDICTORS if not pool[c].isna().any()]),
        "outcome_used_as_imputation_predictor": False,
        "file_path": f"results/sensitivity/mi_imputed_dataset_{i}.csv", "file_sha256": hashes[i],
        "max_iter": 10, "sample_posterior": True,
    })
pd.DataFrame(registry_rows).to_csv(RESULTS_DIR / "multiple_imputation_registry.csv", index=False)

print(f"\nSaved results/sensitivity/multiple_imputation_diagnostics.csv ({len(diag_out)} rows)")
print(f"Saved results/sensitivity/multiple_imputation_registry.csv ({M_IMPUTATIONS} imputations)")
print("\nNote: these are static, full-pool-fit imputed datasets for DIAGNOSTIC purposes only.")
print("The leakage-safe model-refit/prediction step fits imputation fresh inside each CV fold.")
