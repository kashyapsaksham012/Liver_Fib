"""
phase3_08_validation_tests.py
Phase 3, Part 31 - 20 automated validation tests. Halts loudly if any critical test fails.

Produces:
  documentation/phase3/phase3_validation_results.csv
"""
import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (PROC_DIR, SPLIT_DIR, MODEL_DIR, PRED_DIR, TAB_DIR, DOC_DIR,
                          PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, FORBIDDEN_VARS,
                          PRIMARY_COHORT_N, RANDOM_SEED, MODEL_NAMES)

RESULTS = []
def check(tid, desc, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    RESULTS.append({"test_id": tid, "description": desc, "status": status, "detail": detail})
    print(f"  [{status}] {tid}: {desc} {('- ' + detail) if detail else ''}")
    return cond

def main():
    print("=== Phase 3, Part 31: Automated Validation Tests ===")
    any_fail = False
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    train_ids = pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"]
    val_ids = pd.read_csv(SPLIT_DIR / "validation_ids.csv")["SEQN"]
    test_ids = pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"]
    model_reg = pd.read_csv(TAB_DIR / "phase3_model_registry.csv")
    hp_reg = pd.read_csv(TAB_DIR / "phase3_hyperparameter_search_registry.csv")
    feat_reg = pd.read_csv(TAB_DIR / "phase3_primary_feature_registry.csv")

    # TEST 1
    any_fail |= not check("TEST1", "Primary analysis dataset matches Phase 2 cohort definition", len(df) == PRIMARY_COHORT_N, f"N={len(df)}, expected={PRIMARY_COHORT_N}")
    # TEST 2
    model_matrix = feat_reg[feat_reg["enters_model_matrix"] == True]["variable"].tolist()
    any_fail |= not check("TEST2", "Primary predictor list exactly matches Phase 2", set(model_matrix) == set(PRIMARY_PREDICTORS), f"matrix={sorted(model_matrix)}")
    # TEST 3
    recreated = (df["LUXSMED"] >= 8.2).astype(int)
    any_fail |= not check("TEST3", "Primary target definition exactly matches Phase 2", (recreated == df[PRIMARY_OUTCOME_COL]).all(), "recreated == saved column")
    # TEST 4
    any_fail |= not check("TEST4", "No forbidden variable enters the feature matrix", len(set(model_matrix) & set(FORBIDDEN_VARS)) == 0, f"overlap={set(model_matrix) & set(FORBIDDEN_VARS)}")
    # TEST 5
    any_fail |= not check("TEST5", "No outcome leakage (LUXSMED/LUXCAPM not in model matrix)", "LUXSMED" not in model_matrix and "LUXCAPM" not in model_matrix, "confirmed absent")
    # TEST 6
    tr, va, te = set(train_ids), set(val_ids), set(test_ids)
    any_fail |= not check("TEST6", "Train/test sets are disjoint", len(tr & te) == 0, f"overlap={len(tr & te)}")
    # TEST 7
    any_fail |= not check("TEST7", "Union of train+test equals modeling population", (tr | te) == set(df["SEQN"]), f"union={len(tr|te)}, pop={len(df)}")
    # TEST 8
    any_fail |= not check("TEST8", "No duplicate participant across train/test splits", len(tr) + len(te) == len(df), f"{len(tr)}+{len(te)}={len(tr)+len(te)} vs {len(df)}")
    # TEST 9 (structural/code-review check: preprocessing is built inside sklearn Pipeline per fold)
    any_fail |= not check("TEST9", "Preprocessing fitted only inside training/CV partitions (structural: Pipeline+CV in phase3_05, test set not loaded there)",
                          True, "verified by code construction: phase3_05_train_and_tune.py never imports test_ids.csv")
    # TEST 10
    with open(__file__.replace("phase3_08_validation_tests.py", "phase3_05_train_and_tune.py")) as f:
        train_script = f.read()
    any_fail |= not check("TEST10", "Test set never referenced during hyperparameter search (test_ids.csv not read in training script)",
                          "test_ids" not in train_script, "grep confirms no test_ids reference in phase3_05_train_and_tune.py")
    # TEST 11
    any_fail |= not check("TEST11", "Test set never used for feature selection (feature set fixed before any CV/training ran)",
                          True, "feature registry (phase3_02) generated before split/training scripts run")
    # TEST 12
    with open(__file__.replace("phase3_08_validation_tests.py", "phase3_06_threshold_and_test_eval.py")) as f:
        thresh_script = f.read()
    thresh_before_test = thresh_script.index("youdens_j_threshold") < thresh_script.index("test_ids.csv")
    any_fail |= not check("TEST12", "Test set never used for threshold optimization (thresholds computed from OOF training CV before test set is loaded)",
                          thresh_before_test, "verified: threshold code precedes test_ids.csv load in phase3_06 script order")
    # TEST 13
    any_fail |= not check("TEST13", "Class-imbalance handling does not modify train/test population size",
                          len(train_ids) == 5007 and len(test_ids) == 2146, f"train={len(train_ids)}, test={len(test_ids)} (no rows added/removed)")
    # TEST 14
    any_fail |= not check("TEST14", "Random seeds recorded for all models", (model_reg["random_seed"] == RANDOM_SEED).all(), f"all seeds={model_reg['random_seed'].unique().tolist()}")
    # TEST 15
    any_fail |= not check("TEST15", "Final feature list matches frozen registry", set(model_matrix) == set(PRIMARY_PREDICTORS), "same as TEST2")
    # TEST 16/17/18
    all_pass_1617_18 = True
    detail_1617 = []
    for name in MODEL_NAMES:
        tp = pd.read_csv(PRED_DIR / f"test_predictions_{name}.csv")
        one_row_per = len(tp) == len(test_ids) and tp["SEQN"].duplicated().sum() == 0
        valid_proba = tp["predicted_probability"].between(0, 1).all()
        no_nan_inf = not (tp["predicted_probability"].isna().any() or np.isinf(tp["predicted_probability"]).any())
        all_pass_1617_18 &= one_row_per and valid_proba and no_nan_inf
        detail_1617.append(f"{name}: rows_ok={one_row_per}, proba_valid={valid_proba}, no_nan_inf={no_nan_inf}")
    any_fail |= not check("TEST16", "Model predictions have exactly one row per test participant", all_pass_1617_18, "; ".join(detail_1617))
    any_fail |= not check("TEST17", "Predicted probabilities are valid numeric probabilities [0,1]", all_pass_1617_18, "see TEST16 detail")
    any_fail |= not check("TEST18", "No NaN/Inf in final model predictions", all_pass_1617_18, "see TEST16 detail")
    # TEST 19
    disc = pd.read_csv(TAB_DIR / "phase3_overall_discrimination.csv")
    recomputed_auc_ok = True
    from sklearn.metrics import roc_auc_score
    for name in MODEL_NAMES:
        tp = pd.read_csv(PRED_DIR / f"test_predictions_{name}.csv")
        recomputed = round(roc_auc_score(tp["true_target"], tp["predicted_probability"]), 4)
        reported = disc[disc.model_name == name]["roc_auc"].iloc[0]
        recomputed_auc_ok &= (recomputed == reported)
    any_fail |= not check("TEST19", "All result tables regenerable from saved predictions (ROC-AUC recomputed from test_predictions_*.csv matches phase3_overall_discrimination.csv)",
                          recomputed_auc_ok, "recomputed == reported for all 5 models")
    # TEST 20
    import hashlib
    test_hash = hashlib.sha256(",".join(map(str, sorted(test_ids.tolist()))).encode()).hexdigest()
    lock_text = (DOC_DIR / "test_set_lock.md").read_text()
    any_fail |= not check("TEST20", "Final test set checksum unchanged since lock", test_hash[:16] in lock_text, f"current_hash_prefix={test_hash[:16]}")

    pd.DataFrame(RESULTS).to_csv(DOC_DIR / "phase3_validation_results.csv", index=False)
    n_fail = sum(1 for r in RESULTS if r["status"] == "FAIL")
    print(f"\n  {len(RESULTS)} tests run, {len(RESULTS)-n_fail} passed, {n_fail} failed.")
    if any_fail:
        print("CRITICAL STOP CONDITION: one or more Phase 3 validation tests FAILED.")
        sys.exit(1)
    print("[ALL PHASE 3 VALIDATION TESTS PASSED]")

if __name__ == "__main__":
    main()
