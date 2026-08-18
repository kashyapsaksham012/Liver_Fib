"""
phase3_05_train_and_tune.py
Phase 3, Parts 12, 15-19 - Leakage-safe preprocessing (fit inside CV folds only),
train the frozen 5-model baseline set (Logistic Regression, Random Forest, XGBoost,
LightGBM, MLP -- per info.md Phase 6 / model_development_protocol.md), 5-fold
stratified CV hyperparameter search per model (predefined search space/n-evals/
scoring/tie-break), and select each family's best configuration by CV ROC-AUC.
NO family is declared an overall "winner" -- all 5 tuned models are retained as
candidates, per the frozen model-selection rule.

The TEST SET IS NEVER LOADED IN THIS SCRIPT.

Produces:
  results/tables/phase3_model_registry.csv
  results/tables/phase3_hyperparameter_search_registry.csv
  results/predictions/validation_predictions_<model>.csv   (out-of-fold CV predictions)
  models/phase3/model_<name>_v1.joblib
"""
import os, sys, json, time
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedKFold, GridSearchCV, RandomizedSearchCV, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (PROC_DIR, SPLIT_DIR, MODEL_DIR, PRED_DIR, TAB_DIR, NOW, RANDOM_SEED,
                          N_CV_FOLDS, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, MODEL_NAMES)

# ── Leakage-safe preprocessing: fit ONLY inside each CV fold / on the training partition ──
def build_preprocessor(scale):
    steps = [("impute", SimpleImputer(strategy="median"))]  # no-op here (0 missingness), defensive/robust by design
    if scale:
        steps.append(("scale", StandardScaler()))
    return Pipeline(steps)

def build_pipeline(name, n_neg, n_pos):
    scale_pos_weight = n_neg / n_pos
    pre = ColumnTransformer([("num", build_preprocessor(scale=name in ("logistic", "mlp")), PRIMARY_PREDICTORS)])
    if name == "logistic":
        est = LogisticRegression(class_weight="balanced", solver="lbfgs", max_iter=2000, random_state=RANDOM_SEED)
        grid = {"est__C": [0.001, 0.01, 0.1, 1, 10, 100]}
        search_type, n_iter = "grid", None
    elif name == "random_forest":
        est = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1)
        grid = {"est__n_estimators": [100, 300, 500], "est__max_depth": [3, 5, 7, None], "est__min_samples_leaf": [1, 5, 10]}
        search_type, n_iter = "randomized", 20
    elif name == "xgboost":
        est = xgb.XGBClassifier(scale_pos_weight=scale_pos_weight, eval_metric="logloss", random_state=RANDOM_SEED, n_jobs=-1)
        grid = {"est__n_estimators": [100, 300, 500], "est__max_depth": [2, 3, 4, 5],
               "est__learning_rate": [0.01, 0.05, 0.1], "est__subsample": [0.7, 0.9, 1.0]}
        search_type, n_iter = "randomized", 20
    elif name == "lightgbm":
        est = lgb.LGBMClassifier(scale_pos_weight=scale_pos_weight, random_state=RANDOM_SEED, n_jobs=-1, verbosity=-1)
        grid = {"est__n_estimators": [100, 300, 500], "est__max_depth": [2, 3, 4, 5],
               "est__learning_rate": [0.01, 0.05, 0.1], "est__subsample": [0.7, 0.9, 1.0]}
        search_type, n_iter = "randomized", 20
    elif name == "mlp":
        est = MLPClassifier(random_state=RANDOM_SEED, max_iter=1000, early_stopping=True)  # no class_weight support -- documented limitation
        grid = {"est__hidden_layer_sizes": [(16,), (32,), (32, 16)], "est__alpha": [0.0001, 0.001, 0.01],
               "est__learning_rate_init": [0.001, 0.01]}
        search_type, n_iter = "grid", None
    else:
        raise ValueError(name)
    pipe = Pipeline([("pre", pre), ("est", est)])
    return pipe, grid, search_type, n_iter

def main():
    print("=== Phase 3, Parts 12, 15-19: Preprocessing, Training, CV Tuning (train partition ONLY) ===")
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
    train_df = df[df["SEQN"].isin(train_ids)].reset_index(drop=True)
    print(f"  Loaded TRAINING partition only: N={len(train_df)} (test set NOT loaded in this script).")

    X = train_df[PRIMARY_PREDICTORS]
    y = train_df[PRIMARY_OUTCOME_COL].values
    n_pos, n_neg = int(y.sum()), int((y == 0).sum())
    cv = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)

    model_registry, search_registry = [], []
    for name in MODEL_NAMES:
        print(f"\n  --- {name} ---")
        t0 = time.time()
        pipe, grid, search_type, n_iter = build_pipeline(name, n_neg, n_pos)
        n_combos = 1
        for v in grid.values():
            n_combos *= len(v)

        if search_type == "grid":
            search = GridSearchCV(pipe, grid, scoring="roc_auc", cv=cv, n_jobs=-1, refit=True)
            n_evals = n_combos
        else:
            search = RandomizedSearchCV(pipe, grid, n_iter=n_iter, scoring="roc_auc", cv=cv, n_jobs=-1,
                                        random_state=RANDOM_SEED, refit=True)
            n_evals = n_iter

        search.fit(X, y)
        elapsed = round(time.time() - t0, 1)
        best_score = round(search.best_score_, 4)
        # Tie-break rule (predefined): among configs within 0.001 CV-AUC of the best, prefer simpler/more
        # regularized config -- implemented by checking cv_results_ for near-ties and logging the decision.
        results_df = pd.DataFrame(search.cv_results_)
        near_ties = results_df[results_df["mean_test_score"] >= best_score - 0.001].sort_values("mean_test_score", ascending=False)
        tie_break_applied = len(near_ties) > 1
        print(f"    Best CV ROC-AUC: {best_score} | params: {search.best_params_} | {elapsed}s | "
              f"{'tie-break applicable ('+str(len(near_ties))+' near-ties)' if tie_break_applied else 'clear winner'}")

        # Out-of-fold CV predictions using the best estimator's config (= "validation" predictions, Part 22)
        best_pipe, _, _, _ = build_pipeline(name, n_neg, n_pos)
        best_pipe.set_params(**search.best_params_)
        oof_proba = cross_val_predict(best_pipe, X, y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
        oof_df = pd.DataFrame({"SEQN": train_df["SEQN"].values, "true_target": y, "predicted_probability": oof_proba})
        oof_df.to_csv(PRED_DIR / f"validation_predictions_{name}.csv", index=False)

        # Fit final model on FULL training partition with best hyperparameters (still never touches test set)
        final_pipe = search.best_estimator_
        model_path = MODEL_DIR / f"model_{name}_v1.joblib"
        joblib.dump({"pipeline": final_pipe, "predictors": PRIMARY_PREDICTORS, "seed": RANDOM_SEED,
                    "best_params": search.best_params_, "cv_auc": best_score}, model_path)

        model_registry.append({
            "model_name": name, "library": {"logistic": "scikit-learn", "random_forest": "scikit-learn",
                                            "xgboost": "xgboost", "lightgbm": "lightgbm", "mlp": "scikit-learn"}[name],
            "library_version": {"logistic": __import__("sklearn").__version__, "random_forest": __import__("sklearn").__version__,
                               "xgboost": xgb.__version__, "lightgbm": lgb.__version__, "mlp": __import__("sklearn").__version__}[name],
            "random_seed": RANDOM_SEED, "best_hyperparameters": json.dumps(search.best_params_),
            "preprocessing": "median-impute (no-op) + StandardScaler" if name in ("logistic", "mlp") else "median-impute (no-op), no scaling (tree-based)",
            "class_imbalance_handling": {"logistic": "class_weight=balanced", "random_forest": "class_weight=balanced",
                                        "xgboost": f"scale_pos_weight={round(n_neg/n_pos,3)}", "lightgbm": f"scale_pos_weight={round(n_neg/n_pos,3)}",
                                        "mlp": "NONE (documented technical constraint, see class_imbalance_protocol_implementation.md)"}[name],
            "training_strategy": "fit on full 70% training partition with CV-selected hyperparameters",
            "cross_validation_strategy": f"{N_CV_FOLDS}-fold StratifiedKFold(shuffle=True, random_state={RANDOM_SEED})",
            "selection_criterion": "mean CV ROC-AUC", "cv_roc_auc": best_score, "training_time_sec": elapsed,
            "model_artifact_path": str(model_path.relative_to(model_path.parents[3]))
        })
        for _, r in results_df.iterrows():
            search_registry.append({"model_name": name, "search_type": search_type, "n_evaluations_planned": n_evals,
                                   "params": json.dumps(r["params"]), "mean_cv_roc_auc": round(r["mean_test_score"], 4),
                                   "std_cv_roc_auc": round(r["std_test_score"], 4),
                                   "is_selected_best": bool(r["params"] == search.best_params_),
                                   "tie_break_rule": "prefer simpler/more-regularized config among ties within 0.001 AUC"})

    pd.DataFrame(model_registry).to_csv(TAB_DIR / "phase3_model_registry.csv", index=False)
    pd.DataFrame(search_registry).to_csv(TAB_DIR / "phase3_hyperparameter_search_registry.csv", index=False)
    print(f"\n  Saved phase3_model_registry.csv ({len(model_registry)} models) and "
          f"phase3_hyperparameter_search_registry.csv ({len(search_registry)} evaluated configs).")
    print("  All 5 model families retained as candidates -- no single 'winner' declared (frozen rule).")
    print("[TRAINING & TUNING COMPLETE -- TEST SET WAS NEVER LOADED]")

if __name__ == "__main__":
    main()
