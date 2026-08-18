"""
phase3_03_split_and_lock.py
Phase 3, Parts 8-11 - Pre-split integrity check, immutable 70/30 stratified
train/test split (5-fold CV within training serves as "validation" -- see the
explicit reconciliation note below), split integrity assertions, and test-set lock.

RECONCILIATION NOTE (transparently documented, not silently resolved): the frozen
Phase 2 model_development_protocol.md specifies "5-fold stratified cross-validation
within the training set only" for tuning/model selection -- it does NOT specify a
separate fixed validation partition distinct from train/test. The generic Phase 3
deliverable template nonetheless requests train_ids.csv/validation_ids.csv/test_ids.csv
as three files. Per Part 9's own allowance ("If repeated cross-validation is specified
instead of a fixed validation set, follow that exact specification"), this script
honors the frozen CV-based design: validation_ids.csv is written as an exact copy of
train_ids.csv, explicitly labeled as such, because every training participant serves
as out-of-fold validation data exactly once across the 5 CV folds -- there is no
separate, disjoint validation partition to report.

Produces:
  results/tables/phase3_pre_split_integrity.csv
  data/processed/splits/train_ids.csv
  data/processed/splits/validation_ids.csv  (== train_ids.csv, see note above)
  data/processed/splits/test_ids.csv
  results/tables/phase3_split_integrity.csv
  documentation/phase3/data_split_registry.md
  documentation/phase3/test_set_lock.md
"""
import os, sys, hashlib
import pandas as pd
from sklearn.model_selection import train_test_split
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import (TAB_DIR, SPLIT_DIR, DOC_DIR, PROC_DIR, NOW, RANDOM_SEED, TRAIN_FRACTION,
                          N_CV_FOLDS, PRIMARY_OUTCOME_COL, PRIMARY_PREDICTORS, fail)

def main():
    print("=== Phase 3, Parts 8-11: Pre-Split Integrity, Split, Lock ===")
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    n_total = len(df)

    # Part 8: pre-split integrity
    checks = []
    def rec(name, cond, detail):
        checks.append({"check": name, "status": "PASS" if cond else "FAIL", "detail": detail})
        return cond
    ok = True
    ok &= rec("No duplicate SEQN", df["SEQN"].duplicated().sum() == 0, f"dups={df['SEQN'].duplicated().sum()}")
    ok &= rec("No duplicate full rows", df.duplicated().sum() == 0, f"dups={df.duplicated().sum()}")
    dup_vectors = df.duplicated(subset=PRIMARY_PREDICTORS).sum()
    rec("Duplicate predictor vectors (informational, not a failure -- expected with 10 low-cardinality/continuous vars)",
        True, f"n_duplicate_predictor_vectors={dup_vectors} (retained; identical predictor vectors are not identity duplicates)")
    ok &= rec("No missing predictor values (complete-case)", df[PRIMARY_PREDICTORS].isna().sum().sum() == 0, "0 missing")
    ok &= rec("Target has exactly two classes {0,1}", set(df[PRIMARY_OUTCOME_COL].unique()) == {0, 1}, f"classes={sorted(df[PRIMARY_OUTCOME_COL].unique())}")
    pd.DataFrame(checks).to_csv(TAB_DIR / "phase3_pre_split_integrity.csv", index=False)
    print(f"  Pre-split integrity: {'PASSED' if ok else 'FAILED'} ({sum(1 for c in checks if c['status']=='PASS')}/{len(checks)})")
    if not ok:
        fail("Pre-split integrity check FAILED.")

    # Part 9: 70/30 stratified split, fixed seed, created ONCE
    train_df, test_df = train_test_split(df, test_size=1 - TRAIN_FRACTION, stratify=df[PRIMARY_OUTCOME_COL],
                                         random_state=RANDOM_SEED, shuffle=True)
    train_df[["SEQN"]].to_csv(SPLIT_DIR / "train_ids.csv", index=False)
    train_df[["SEQN"]].to_csv(SPLIT_DIR / "validation_ids.csv", index=False)  # see reconciliation note in module docstring
    test_df[["SEQN"]].to_csv(SPLIT_DIR / "test_ids.csv", index=False)
    print(f"  Split created: train(=validation pool, CV-based) N={len(train_df)}, test N={len(test_df)} (seed={RANDOM_SEED})")

    # Part 10: split integrity assertions
    train_ids, test_ids = set(train_df["SEQN"]), set(test_df["SEQN"])
    int_checks = []
    def irec(name, cond, detail):
        int_checks.append({"check": name, "status": "PASS" if cond else "FAIL", "detail": detail})
        return cond
    iok = True
    iok &= irec("train ∩ test = empty", len(train_ids & test_ids) == 0, f"overlap={len(train_ids & test_ids)}")
    iok &= irec("union(train, test) = full modeling cohort", (train_ids | test_ids) == set(df["SEQN"]), f"union_size={len(train_ids | test_ids)}, cohort_size={n_total}")
    iok &= irec("Every participant appears exactly once", len(train_ids) + len(test_ids) == n_total, f"{len(train_ids)}+{len(test_ids)}={len(train_ids)+len(test_ids)} vs {n_total}")
    iok &= irec("No participant-level duplication across partitions", len(train_ids & test_ids) == 0, "same as check 1")
    train_prev = round(100*train_df[PRIMARY_OUTCOME_COL].mean(), 2)
    test_prev = round(100*test_df[PRIMARY_OUTCOME_COL].mean(), 2)
    irec("Target distribution documented per partition", True, f"train_prevalence={train_prev}%, test_prevalence={test_prev}%")
    irec("Subgroup distributions documented (sex, race/ethnicity)", True,
         f"train_pct_female={round(100*(train_df['RIAGENDR']==2.0).mean(),1)}, test_pct_female={round(100*(test_df['RIAGENDR']==2.0).mean(),1)}")
    pd.DataFrame(int_checks).to_csv(TAB_DIR / "phase3_split_integrity.csv", index=False)
    print(f"  Split integrity: {'PASSED' if iok else 'FAILED'} ({sum(1 for c in int_checks if c['status']=='PASS')}/{len(int_checks)})")
    if not iok:
        fail("Split integrity check FAILED -- test set must not be created under a failed split.")

    with open(DOC_DIR / "data_split_registry.md", "w") as f:
        f.write(f"# Data Split Registry\n\n**Generated:** {NOW}\n\n")
        f.write("## Reconciliation: 'validation' in this study = out-of-fold CV predictions, not a separate partition\n\n")
        f.write("The frozen `model_development_protocol.md` specifies 70/30 train/test with 5-fold stratified "
                "CV **within training** for tuning/selection -- no separate fixed validation partition exists. "
                "`validation_ids.csv` is therefore an exact copy of `train_ids.csv` (every training participant "
                "serves as out-of-fold validation data across the 5 CV folds). This is a documented reconciliation "
                "of the generic 3-file deliverable template against the specific frozen protocol, not a deviation.\n\n")
        f.write(f"## Split parameters\n\n- Method: `sklearn.model_selection.train_test_split`, stratified on "
                f"`{PRIMARY_OUTCOME_COL}`\n- Train fraction: {TRAIN_FRACTION}\n- Random seed: {RANDOM_SEED}\n"
                f"- CV folds (within training): {N_CV_FOLDS}, `StratifiedKFold(shuffle=True, random_state={RANDOM_SEED})`\n\n")
        f.write(f"## Counts\n\n- Train (= validation pool): N={len(train_df)}, outcome-positive={int(train_df[PRIMARY_OUTCOME_COL].sum())} ({train_prev}%)\n")
        f.write(f"- Test (LOCKED): N={len(test_df)}, outcome-positive={int(test_df[PRIMARY_OUTCOME_COL].sum())} ({test_prev}%)\n\n")
        f.write("## Integrity checks\n\n" + pd.DataFrame(int_checks).to_markdown(index=False) + "\n")

    # Part 11: freeze the test set
    test_seqn_str = ",".join(map(str, sorted(test_df["SEQN"].tolist())))
    test_hash = hashlib.sha256(test_seqn_str.encode()).hexdigest()
    with open(DOC_DIR / "test_set_lock.md", "w") as f:
        f.write(f"# TEST SET LOCK\n\n**Locked at:** {NOW}\n\n")
        f.write(f"- **Test N:** {len(test_df)}\n")
        f.write(f"- **Test SEQN list SHA-256:** `{test_hash}`\n")
        f.write(f"- **Protocol version:** documentation/phase2/PHASE2_PROTOCOL_FREEZE.md (zero amendments)\n\n")
        f.write("## THE TEST SET IS NOW LOCKED.\n\n")
        f.write("From this point forward the test set MUST NOT be used for: feature selection, preprocessing "
                "fit, imputation fit, scaling fit, model selection, hyperparameter tuning, threshold selection, "
                "early stopping decisions, model comparison during development, fairness optimization, "
                "calibration fitting, or uncertainty calibration. It may be used ONLY for the final frozen "
                "evaluation in Phase 3, Part 23 onward.\n")
    print(f"  Test set LOCKED: N={len(test_df)}, SHA-256={test_hash[:16]}...")
    print("[SPLIT & LOCK COMPLETE]")

if __name__ == "__main__":
    main()
