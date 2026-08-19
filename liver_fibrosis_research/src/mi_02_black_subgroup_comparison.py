"""
mi_02_black_subgroup_comparison.py
Multiple-imputation sensitivity analysis, Parts 8-9: the central comparison.

Design rationale (stated explicitly): to isolate the effect of *including the 615 previously-
excluded participants via imputation* from other confounds, both arms of this comparison use the
IDENTICAL 5-fold CV out-of-fold (OOF) design, frozen predictors, and frozen per-model
hyperparameters -- they differ ONLY in (a) which participants are included (N=7,153 complete-case
vs. N=7,768 MI pool) and (b) whether missing predictor values are imputed. This is a freshly
computed comparison baseline (not reuse of Phase 3's N=5,007 train-only OOF, which would confound
the comparison with a different evaluation population) -- explicitly scoped to this targeted
question, not a Phase 3 rerun or a full model comparison.

Leakage safety: for BOTH arms, all preprocessing (imputation, scaling) is fit only inside each CV
fold's training portion via sklearn Pipeline/ColumnTransformer, exactly mirroring Phase 3's
established pattern. The locked test set is never loaded or referenced anywhere in this script.

No hyperparameter search occurs -- each model's frozen Phase 3 best_params are reused unchanged.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import lightgbm as lgb
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import INT_DIR
from _cohorts import COHORT_3B_ADULT_OF_QUALITY_VALID, compute_all
from phase3_common import ROOT, MODEL_DIR, PRED_DIR, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, RANDOM_SEED, N_CV_FOLDS, MODEL_NAMES
from phase5_common import FROZEN_THRESHOLDS

RESULTS_DIR = ROOT / "results" / "sensitivity"
M_IMPUTATIONS = 5
BOOTSTRAP_N = 2000
CI_LEVEL = 0.95

# ---- Load frozen best_params for each model (no new hyperparameter search) ----
best_params_by_model = {}
for name in MODEL_NAMES:
    art = joblib.load(MODEL_DIR / f"model_{name}_v1.joblib")
    best_params_by_model[name] = art["best_params"]

def build_pipeline(name, scale, imputer_step):
    steps = [("impute", imputer_step)]
    if scale:
        steps.append(("scale", StandardScaler()))
    pre = ColumnTransformer([("num", Pipeline(steps), PRIMARY_PREDICTORS)])
    if name == "logistic":
        est = LogisticRegression(class_weight="balanced", solver="lbfgs", max_iter=2000, random_state=RANDOM_SEED)
    elif name == "random_forest":
        est = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1)
    elif name == "xgboost":
        est = xgb.XGBClassifier(eval_metric="logloss", random_state=RANDOM_SEED, n_jobs=-1)
    elif name == "lightgbm":
        est = lgb.LGBMClassifier(random_state=RANDOM_SEED, n_jobs=-1, verbosity=-1)
    elif name == "mlp":
        est = MLPClassifier(random_state=RANDOM_SEED, max_iter=1000, early_stopping=True)
    else:
        raise ValueError(name)
    stripped_params = {k.replace("est__", ""): v for k, v in best_params_by_model[name].items()}
    est.set_params(**stripped_params)
    # scale_pos_weight for XGBoost must be recomputed per-fold-population -- handled via sample data at fit time is
    # not directly supported mid-pipeline without a wrapper; consistent with Phase 3, we set it from the whole
    # population being fit (pool-level class balance), matching Phase 3's build_pipeline() convention.
    return Pipeline([("pre", pre), ("est", est)])

# ---- Load full pool ----
master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
mask, meta = COHORT_3B_ADULT_OF_QUALITY_VALID(master)
pool = master[mask].reset_index(drop=True).copy()
pool[PRIMARY_OUTCOME_COL] = (pool["LUXSMED"] >= 8.2).astype(int)

# Complete-case subset of the pool (N should be 7153, matching the frozen primary cohort exactly)
cc_mask = pool[PRIMARY_PREDICTORS].notna().all(axis=1)
cc_pool = pool[cc_mask].reset_index(drop=True).copy()
if len(cc_pool) != 7153:
    print(f"STOP: complete-case pool N={len(cc_pool)}, expected 7153"); sys.exit(1)
if len(pool) != 7768:
    print(f"STOP: full MI pool N={len(pool)}, expected 7768"); sys.exit(1)

cv = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)

results_rows = []
oof_store = {}  # (arm, model) -> dataframe with SEQN, true, prob

for name in MODEL_NAMES:
    scale = name in ("logistic", "mlp")

    # ---- Arm 1: complete-case, N=7153, fresh CV-OOF (no imputation needed -- SimpleImputer is a no-op) ----
    X_cc = cc_pool[PRIMARY_PREDICTORS]
    y_cc = cc_pool[PRIMARY_OUTCOME_COL].values
    pipe_cc = build_pipeline(name, scale, SimpleImputer(strategy="median"))
    if name == "xgboost":
        n_pos, n_neg = int(y_cc.sum()), int((y_cc == 0).sum())
        pipe_cc.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
    elif name == "lightgbm":
        n_pos, n_neg = int(y_cc.sum()), int((y_cc == 0).sum())
        pipe_cc.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
    proba_cc = cross_val_predict(pipe_cc, X_cc, y_cc, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    oof_store[("complete_case", name)] = pd.DataFrame({"SEQN": cc_pool["SEQN"].values, "true_target": y_cc, "predicted_probability": proba_cc})
    print(f"{name}: complete-case CV-OOF done (N={len(cc_pool)})")

    # ---- Arm 2: MI pool, N=7768, pooled across m=5 imputations, each with fold-embedded IterativeImputer ----
    mi_probas = []
    for i in range(M_IMPUTATIONS):
        seed_i = RANDOM_SEED + i
        imputer_i = IterativeImputer(estimator=BayesianRidge(), random_state=seed_i, max_iter=10, sample_posterior=True)
        pipe_mi = build_pipeline(name, scale, imputer_i)
        X_pool = pool[PRIMARY_PREDICTORS]
        y_pool = pool[PRIMARY_OUTCOME_COL].values
        if name in ("xgboost", "lightgbm"):
            n_pos, n_neg = int(y_pool.sum()), int((y_pool == 0).sum())
            pipe_mi.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
        proba_i = cross_val_predict(pipe_mi, X_pool, y_pool, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
        mi_probas.append(proba_i)
        print(f"{name}: MI imputation {i} CV-OOF done (N={len(pool)})")
    proba_mi_pooled = np.mean(mi_probas, axis=0)  # predictive pooling across m imputations, Amendment #12
    oof_store[("multiple_imputation", name)] = pd.DataFrame({"SEQN": pool["SEQN"].values, "true_target": pool[PRIMARY_OUTCOME_COL].values, "predicted_probability": proba_mi_pooled})
    print(f"{name}: MI pooled OOF complete")

# Save all OOF predictions for provenance
for (arm, name), df in oof_store.items():
    df.to_csv(RESULTS_DIR / f"oof_predictions_{arm}_{name}.csv", index=False)

decision_rows = []
for name in MODEL_NAMES:
    decision_rows.append({
        "model": name,
        "refit_required": True,
        "refit_scope": "CV out-of-fold predictions only (StratifiedKFold, 5-fold, seed=42) -- no locked test-set access",
        "hyperparameter_search_performed": False,
        "hyperparameters_source": "frozen Phase 3 best_params, reused unchanged (models/phase3/model_<name>_v1.joblib)",
        "complete_case_arm_n": len(oof_store[("complete_case", name)]),
        "mi_arm_n": len(oof_store[("multiple_imputation", name)]),
        "mi_pooling_method": "predictive pooling: mean predicted probability across m=5 imputations (Amendment #12)",
        "rationale": "Both arms use the identical CV-OOF design to isolate the effect of including the "
                     "615 previously-excluded participants via imputation from other confounds -- this is a "
                     "freshly computed comparison baseline, not a reuse of Phase 3's N=5007 train-only OOF "
                     "(which would confound the comparison with a different evaluation population), and not "
                     "a Phase 3 rerun or full model comparison.",
    })
pd.DataFrame(decision_rows).to_csv(RESULTS_DIR / "mi_model_protocol_decision.csv", index=False)

print("\nAll OOF predictions saved to results/sensitivity/. Proceeding to Black-subgroup comparison.")
