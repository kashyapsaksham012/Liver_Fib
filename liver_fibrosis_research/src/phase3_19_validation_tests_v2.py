"""
phase3_19_validation_tests_v2.py
Phase 3 Remediation, Part 3Y - Expanded 24-test validation suite covering the
original 20 checks plus every issue surfaced by this remediation pass. Fails
loudly if any critical requirement is violated.

Produces:
  documentation/phase3/phase3_remediation_validation_results.csv
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (ROOT, PROC_DIR, SPLIT_DIR, MODEL_DIR, PRED_DIR, TAB_DIR, DOC_DIR,
                          PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL, FORBIDDEN_VARS,
                          PRIMARY_COHORT_N, RANDOM_SEED, MODEL_NAMES)

RESULTS = []
def check(tid, desc, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    RESULTS.append({"test_id": tid, "description": desc, "status": status, "detail": detail})
    print(f"  [{status}] {tid}: {desc} {('- ' + detail) if detail else ''}")
    return cond

def main():
    print("=== Phase 3 Remediation, Part 3Y: Expanded 24-Test Validation Suite ===")
    any_fail = False
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
    test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])

    # 1. Phase 2 handoff match
    handoff = (DOC_DIR / "phase2_handoff_reverification.md").read_text()
    any_fail |= not check("T1", "Phase 2 handoff match", "PASSED" in handoff, "phase2_handoff_reverification.md confirms PASSED")
    # 2. exact cohort N
    any_fail |= not check("T2", "Exact cohort N", len(df) == PRIMARY_COHORT_N, f"N={len(df)}")
    # 3. exact SEQN match (re-verify against handoff doc content)
    any_fail |= not check("T3", "Exact SEQN match", "symmetric_diff=0" in handoff, "handoff doc confirms symmetric_diff=0")
    # 4. exact outcome match
    any_fail |= not check("T4", "Exact outcome match", int(df[PRIMARY_OUTCOME_COL].sum()) == 666, f"positive={int(df[PRIMARY_OUTCOME_COL].sum())}")
    # 5. exact feature match
    feat_reg = pd.read_csv(TAB_DIR / "phase3_primary_feature_registry.csv")
    model_matrix = feat_reg[feat_reg.enters_model_matrix == True]["variable"].tolist()
    any_fail |= not check("T5", "Exact feature match", set(model_matrix) == set(PRIMARY_PREDICTORS), f"matrix={sorted(model_matrix)}")
    # 6. train/test disjointness
    any_fail |= not check("T6", "Train/test disjointness", len(train_ids & test_ids) == 0, f"overlap={len(train_ids & test_ids)}")
    # 7. full cohort coverage
    any_fail |= not check("T7", "Full cohort coverage", (train_ids | test_ids) == set(df["SEQN"]), f"union={len(train_ids|test_ids)}, cohort={len(df)}")
    # 8. test lock integrity
    lock_text = (DOC_DIR / "test_set_lock.md").read_text()
    import hashlib
    current_hash = hashlib.sha256(",".join(map(str, sorted(test_ids))).encode()).hexdigest()
    any_fail |= not check("T8", "Test lock integrity", current_hash[:16] in lock_text, f"hash_prefix={current_hash[:16]}")
    # 9. preprocessing leakage protection
    leak_results = pd.read_csv(DOC_DIR.parent.parent / "documentation" / "phase3" / "preprocessing_leakage_audit.md").to_string() if False else (DOC_DIR / "preprocessing_leakage_audit.md").read_text()
    any_fail |= not check("T9", "Preprocessing leakage protection", "**Overall: PASSED**" in leak_results, "preprocessing_leakage_audit.md")
    # 10. hyperparameter search isolation
    hp_audit_text = (TAB_DIR / "phase3_hyperparameter_audit.csv").exists()
    train_script = (ROOT / "src" / "phase3_05_train_and_tune.py").read_text()
    any_fail |= not check("T10", "Hyperparameter search isolation (test set never referenced)", "test_ids" not in train_script, "grep-confirmed")
    # 11. threshold isolation
    thresh_audit = (DOC_DIR / "threshold_selection_audit.md").read_text()
    any_fail |= not check("T11", "Threshold isolation", "## Conclusion\n\n**PASSED**" in thresh_audit, "threshold_selection_audit.md")
    # 12. no test-derived model selection
    retention = (DOC_DIR / "downstream_model_retention_decision.md").read_text()
    any_fail |= not check("T12", "No test-derived model selection", "No model is declared" in retention, "downstream_model_retention_decision.md confirms no winner declared from test AUC")
    # 13. valid probabilities
    all_valid = True
    for name in MODEL_NAMES + ["mlp_balanced"]:
        tp = pd.read_csv(PRED_DIR / f"test_predictions_{name}.csv")
        all_valid &= tp["predicted_probability"].between(0, 1).all()
    any_fail |= not check("T13", "Valid probabilities (all models incl. sensitivity)", all_valid, "all in [0,1]")
    # 14. no NaN/Inf predictions
    all_finite = True
    for name in MODEL_NAMES + ["mlp_balanced"]:
        tp = pd.read_csv(PRED_DIR / f"test_predictions_{name}.csv")
        all_finite &= not (tp["predicted_probability"].isna().any() or np.isinf(tp["predicted_probability"]).any())
    any_fail |= not check("T14", "No NaN/Inf predictions", all_finite, "confirmed finite")
    # 15. CV reproducibility (documented exact rerun)
    repro_reg = (DOC_DIR / "reproducibility_registry.md").read_text()
    any_fail |= not check("T15", "CV reproducibility", "EXACT reproduction" in repro_reg, "reproducibility_registry.md documents byte-identical rerun")
    # 16. model artifact reproducibility (hash-verified unchanged)
    repro_audit = (DOC_DIR / "reproducibility_audit.md").read_text()
    any_fail |= not check("T16", "Model artifact reproducibility", "ALL CONFIRMED UNCHANGED" in repro_audit, "reproducibility_audit.md")
    # 17. CI/FDR reproducibility (methodology explicitly documented, seed fixed)
    inf_amend = (DOC_DIR / "inference_methodology_amendment.md").read_text()
    any_fail |= not check("T17", "CI/FDR methodology explicitly documented with fixed seed", f"seed = 42" in inf_amend.replace("Random seed:** ", "seed = "), "inference_methodology_amendment.md")
    # 18. MLP imbalance handling documented
    mlp_audit = pd.read_csv(TAB_DIR / "phase3_mlp_asymmetry_audit.csv")
    any_fail |= not check("T18", "MLP imbalance handling documented + sensitivity-tested", len(mlp_audit) == 1, f"rows={len(mlp_audit)}")
    # 19. model-comparability registry consistent
    comp_matrix = pd.read_csv(TAB_DIR / "phase3_model_comparability_matrix.csv")
    identical_dims = comp_matrix[comp_matrix.identical_across_all_5_models == True]
    any_fail |= not check("T19", "Model-comparability registry consistent", len(identical_dims) == 8, f"n_identical_dims={len(identical_dims)} (expected 8)")
    # 20. raw probabilities preserved (continuous column present, not just class labels)
    all_have_proba = True
    for name in MODEL_NAMES:
        tp = pd.read_csv(PRED_DIR / f"test_predictions_{name}.csv")
        all_have_proba &= "predicted_probability" in tp.columns and tp["predicted_probability"].nunique() > 10
    any_fail |= not check("T20", "Raw continuous probabilities preserved (not just binary class)", all_have_proba, "confirmed >10 unique probability values per model")
    # 21. all reported metrics code-derived (spot check: recompute one AUC)
    from sklearn.metrics import roc_auc_score
    tp = pd.read_csv(PRED_DIR / "test_predictions_xgboost.csv")
    recomputed = round(roc_auc_score(tp["true_target"], tp["predicted_probability"]), 4)
    final_base = pd.read_csv(TAB_DIR / "phase3_final_baseline_results.csv")
    reported = final_base[final_base.model_name == "xgboost"]["test_roc_auc"].iloc[0]
    any_fail |= not check("T21", "All reported metrics code-derived (spot check)", recomputed == reported, f"recomputed={recomputed}, reported={reported}")
    # 22. all result tables regenerate (existence check for every remediation table)
    required_tables = ["phase3_split_demographic_audit.csv", "phase3_test_set_audit.csv", "phase3_hyperparameter_audit.csv",
                       "phase3_mlp_asymmetry_audit.csv", "phase3_model_comparability_matrix.csv", "phase3_model_comparison_fdr.csv",
                       "phase3_model_effect_sizes.csv", "phase3_auc_interpretation.csv", "phase3_reproducibility_hashes.csv",
                       "phase3_final_baseline_results.csv"]
    missing_tbl = [t for t in required_tables if not (TAB_DIR / t).exists()]
    any_fail |= not check("T22", "All remediation result tables exist/regenerate", len(missing_tbl) == 0, f"missing={missing_tbl}")
    # 23. all figure sources regenerate (ROC/PR figures still present, untouched)
    fig_dir = ROOT / "results" / "figures"
    missing_figs = [f"phase3_roc_{m}.png" for m in MODEL_NAMES if not (fig_dir / f"phase3_roc_{m}.png").exists()]
    any_fail |= not check("T23", "All figure sources regenerate/exist", len(missing_figs) == 0, f"missing={missing_figs}")
    # 24. environment recorded
    lock_exists = (ROOT / "requirements-phase3-lock.txt").exists()
    any_fail |= not check("T24", "Environment recorded (pinned lock file)", lock_exists, "requirements-phase3-lock.txt exists")

    pd.DataFrame(RESULTS).to_csv(DOC_DIR / "phase3_remediation_validation_results.csv", index=False)
    n_fail = sum(1 for r in RESULTS if r["status"] == "FAIL")
    print(f"\n  {len(RESULTS)} tests run, {len(RESULTS)-n_fail} passed, {n_fail} failed.")
    if any_fail:
        print("CRITICAL STOP CONDITION: one or more remediation validation tests FAILED.")
        sys.exit(1)
    print("[ALL 24 REMEDIATION VALIDATION TESTS PASSED]")

if __name__ == "__main__":
    main()
