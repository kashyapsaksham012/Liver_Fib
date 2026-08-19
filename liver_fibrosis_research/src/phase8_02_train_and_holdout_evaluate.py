"""
phase8_02_train_and_holdout_evaluate.py
Phase 8 (Generalization) Parts 12-17: retrain the 5 frozen model families on the training
population (Non-Hispanic Black entirely excluded), derive a per-model classification threshold
via the same frozen Youden's-J-on-CV-OOF method applied to the training population only, then
evaluate the fully-unseen Non-Hispanic Black holdout population.

Hyperparameters: reused unchanged from Phase 3's frozen best_params (PHASE8_SUBGROUP_HOLDOUT_
PROTOCOL_FREEZE.md Section 7) -- no hyperparameter search occurs here.

Preprocessing (StandardScaler where used) is fit only on the training population. Imputation is a
structural no-op (0% missingness in the primary cohort). The holdout population never enters
threshold derivation, preprocessing fitting, or model fitting.
"""
import sys
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
import xgboost as xgb
import lightgbm as lgb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import INT_DIR
from phase3_common import ROOT, PROC_DIR, MODEL_DIR, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, RANDOM_SEED, N_CV_FOLDS, MODEL_NAMES

RESULTS_DIR = ROOT / "results" / "validation"
PHASE8_MODEL_DIR = ROOT / "models" / "phase8_holdout"
PHASE8_MODEL_DIR.mkdir(parents=True, exist_ok=True)
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 42
CI_LEVEL = 0.95
EPS = 1e-12

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def logit(p):
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))

def calibration_in_the_large(y, p):
    z = logit(np.asarray(p)).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])

def youden_j_threshold(y, p):
    from sklearn.metrics import roc_curve
    fpr, tpr, thr = roc_curve(y, p)
    j = tpr - fpr
    return float(thr[np.argmax(j)])

# ---- Load frozen best_params (no new hyperparameter search) ----
best_params_by_model = {}
for name in MODEL_NAMES:
    art = joblib.load(MODEL_DIR / f"model_{name}_v1.joblib")
    best_params_by_model[name] = art["best_params"]

def build_pipeline(name, scale):
    steps = [("impute", SimpleImputer(strategy="median"))]  # structural no-op, 0% missingness
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
    return Pipeline([("pre", pre), ("est", est)])

# ---- Load partitions ----
master = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
train_ids = pd.read_csv(RESULTS_DIR / "phase8_training_ids.csv")["SEQN"]
hold_ids = pd.read_csv(RESULTS_DIR / "phase8_holdout_ids.csv")["SEQN"]
training = master[master["SEQN"].isin(train_ids)].reset_index(drop=True)
holdout = master[master["SEQN"].isin(hold_ids)].reset_index(drop=True)
if len(training) != 5366 or len(holdout) != 1787:
    print(f"PHASE 8 STOP CONDITION: training N={len(training)}, holdout N={len(holdout)}"); sys.exit(1)

X_train, y_train = training[PRIMARY_PREDICTORS], training[PRIMARY_OUTCOME_COL].values
X_hold, y_hold = holdout[PRIMARY_PREDICTORS], holdout[PRIMARY_OUTCOME_COL].values

cv = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)

training_registry_rows, protocol_matrix_rows, results_rows = [], [], []

for name in MODEL_NAMES:
    scale = name in ("logistic", "mlp")

    # ---- Threshold derivation: Youden's J on training-population CV-OOF (never touches holdout) ----
    pipe_oof = build_pipeline(name, scale)
    if name in ("xgboost", "lightgbm"):
        n_pos, n_neg = int(y_train.sum()), int((y_train == 0).sum())
        pipe_oof.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
    oof_proba = cross_val_predict(pipe_oof, X_train, y_train, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    threshold = youden_j_threshold(y_train, oof_proba)

    # ---- Final fit on the FULL training population ----
    pipe_final = build_pipeline(name, scale)
    if name in ("xgboost", "lightgbm"):
        n_pos, n_neg = int(y_train.sum()), int((y_train == 0).sum())
        pipe_final.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
    pipe_final.fit(X_train, y_train)

    model_path = PHASE8_MODEL_DIR / f"model_{name}_phase8_holdout.joblib"
    joblib.dump({"pipeline": pipe_final, "threshold": threshold, "best_params": best_params_by_model[name]}, model_path)
    model_hash = sha256_bytes(model_path.read_bytes())

    training_registry_rows.append({
        "model": name, "seed": RANDOM_SEED, "training_n": len(training),
        "training_positive_n": int(y_train.sum()), "training_negative_n": int((y_train == 0).sum()),
        "hyperparameter_source": "frozen Phase 3 best_params, reused unchanged",
        "preprocessing_source": "fit on Phase 8 training population only (StandardScaler where used; imputation is a structural no-op)",
        "threshold_derivation": "Youden's J on 5-fold StratifiedKFold(seed=42) CV-OOF, training population only",
        "threshold": round(threshold, 6),
        "model_path": f"models/phase8_holdout/model_{name}_phase8_holdout.joblib",
        "model_sha256": model_hash,
    })
    protocol_matrix_rows.append({
        "model": name, "hyperparameter_policy": "A: reuse Phase 3 frozen best_params unchanged",
        "hyperparameter_search_performed": False, "holdout_used_in_tuning": False,
        "holdout_used_in_threshold_selection": False, "holdout_used_in_preprocessing_fit": False,
    })

    # ---- Primary + secondary holdout evaluation (Non-Hispanic Black, N=1787) ----
    p_hold = pipe_final.predict_proba(X_hold)[:, 1]
    yhat_hold = (p_hold >= threshold).astype(int)
    auc = roc_auc_score(y_hold, p_hold)
    pr_auc = average_precision_score(y_hold, p_hold)
    tp = int(((y_hold == 1) & (yhat_hold == 1)).sum()); fn = int(((y_hold == 1) & (yhat_hold == 0)).sum())
    tn = int(((y_hold == 0) & (yhat_hold == 0)).sum()); fp = int(((y_hold == 0) & (yhat_hold == 1)).sum())
    sens = tp / (tp + fn) if (tp + fn) else None
    spec = tn / (tn + fp) if (tn + fp) else None
    intercept, slope = calibration_in_the_large(y_hold, p_hold)
    brier = brier_score_loss(y_hold, p_hold)

    # Bootstrap CI (n=2000, seed=42) for AUC and sensitivity
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    auc_boot, sens_boot = [], []
    for _ in range(BOOTSTRAP_N):
        idx = rng.integers(0, len(y_hold), size=len(y_hold))
        yb, pb, yhb = y_hold[idx], p_hold[idx], yhat_hold[idx]
        if len(np.unique(yb)) < 2:
            continue
        auc_boot.append(roc_auc_score(yb, pb))
        tp_b, fn_b = int(((yb == 1) & (yhb == 1)).sum()), int(((yb == 1) & (yhb == 0)).sum())
        if (tp_b + fn_b) > 0:
            sens_boot.append(tp_b / (tp_b + fn_b))
    alpha = 1 - CI_LEVEL
    auc_lo, auc_hi = np.percentile(auc_boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    sens_lo, sens_hi = np.percentile(sens_boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])

    results_rows.append({
        "model": name, "holdout_subgroup": "Non-Hispanic Black", "holdout_n": len(holdout),
        "holdout_positive_n": int(y_hold.sum()), "holdout_negative_n": int((y_hold == 0).sum()),
        "holdout_prevalence_pct": round(100 * y_hold.mean(), 4), "threshold": round(threshold, 6),
        "roc_auc": round(auc, 6), "roc_auc_ci_lower": round(auc_lo, 6), "roc_auc_ci_upper": round(auc_hi, 6),
        "pr_auc": round(pr_auc, 6), "sensitivity": round(sens, 6) if sens is not None else None,
        "sensitivity_ci_lower": round(sens_lo, 6), "sensitivity_ci_upper": round(sens_hi, 6),
        "specificity": round(spec, 6) if spec is not None else None,
        "calibration_intercept": round(intercept, 6), "calibration_slope": round(slope, 6),
        "brier_score": round(brier, 6), "bootstrap_n": BOOTSTRAP_N, "bootstrap_n_valid_auc": len(auc_boot),
    })
    print(f"{name}: threshold={threshold:.4f}, holdout AUC={auc:.4f}, sensitivity={sens:.4f}, calib intercept={intercept:.4f}, slope={slope:.4f}")

pd.DataFrame(training_registry_rows).to_csv(RESULTS_DIR / "phase8_training_registry.csv", index=False)
pd.DataFrame(protocol_matrix_rows).to_csv(RESULTS_DIR / "phase8_model_protocol_matrix.csv", index=False)
pd.DataFrame(results_rows).to_csv(RESULTS_DIR / "phase8_generalization_results.csv", index=False)

print(f"\nSaved results/validation/phase8_training_registry.csv ({len(training_registry_rows)} rows)")
print(f"Saved results/validation/phase8_model_protocol_matrix.csv ({len(protocol_matrix_rows)} rows)")
print(f"Saved results/validation/phase8_generalization_results.csv ({len(results_rows)} rows)")
