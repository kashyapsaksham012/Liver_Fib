"""
phase8_01_partition_and_leakage_check.py
Phase 8 (Generalization) Parts 9-11: final feasibility gate, participant partition, leakage
verification. Training population = primary cohort minus Non-Hispanic Black (frozen decision,
PHASE8_SUBGROUP_HOLDOUT_PROTOCOL_FREEZE.md). Holdout population = Non-Hispanic Black only.

Does not modify data/processed/splits/test_ids.csv (Phase 3's locked test set) -- Phase 8 is a
self-contained retrain+holdout-evaluation experiment operating on the full N=7,153 primary cohort;
it does not reuse or reference the Phase 3 test set for its own evaluation.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, PROC_DIR, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL

RESULTS_DIR = ROOT / "results" / "validation"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
if len(df) != 7153:
    print(f"PHASE 8 STOP CONDITION: primary cohort N={len(df)}, expected 7153"); sys.exit(1)

holdout_mask = df["RIDRETH3"] == 4.0
holdout = df[holdout_mask].reset_index(drop=True)
training = df[~holdout_mask].reset_index(drop=True)

# Final feasibility gate (Part 9)
n_hold, pos_hold, neg_hold = len(holdout), int(holdout[PRIMARY_OUTCOME_COL].sum()), int((holdout[PRIMARY_OUTCOME_COL] == 0).sum())
n_train, pos_train, neg_train = len(training), int(training[PRIMARY_OUTCOME_COL].sum()), int((training[PRIMARY_OUTCOME_COL] == 0).sum())

print("=== Part 9: Final feasibility gate ===")
print(f"Holdout (Non-Hispanic Black):     N={n_hold}, positive={pos_hold}, negative={neg_hold}")
print(f"Remaining training:               N={n_train}, positive={pos_train}, negative={neg_train}")
feasibility = "FEASIBLE" if (n_hold == 1787 and pos_hold == 177 and n_train == 5366 and pos_train == 489) else "STOP -- COUNTS DO NOT MATCH FROZEN PROTOCOL"
print(f"Classification: {feasibility}")
if feasibility != "FEASIBLE":
    sys.exit(1)

# Part 10: participant partition
training[["SEQN"]].to_csv(RESULTS_DIR / "phase8_training_ids.csv", index=False)
holdout[["SEQN"]].to_csv(RESULTS_DIR / "phase8_holdout_ids.csv", index=False)

# Part 11: absolute holdout isolation -- verify disjointness and complete exclusion
train_ids = set(training["SEQN"])
hold_ids = set(holdout["SEQN"])
overlap = train_ids & hold_ids
if overlap:
    print(f"PHASE 8 STOP CONDITION: training/holdout overlap, N={len(overlap)}"); sys.exit(1)
if (training["RIDRETH3"] == 4.0).any():
    print("PHASE 8 STOP CONDITION: Non-Hispanic Black participant found in training population"); sys.exit(1)
if not (holdout["RIDRETH3"] == 4.0).all():
    print("PHASE 8 STOP CONDITION: non-Black participant found in holdout population"); sys.exit(1)

# Confirm Phase 3 locked test set is untouched by this script
test_ids_path = ROOT / "data" / "processed" / "splits" / "test_ids.csv"
import hashlib
test_hash = hashlib.sha256(test_ids_path.read_bytes()).hexdigest()
expected = "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779"
print(f"\nPhase 3 locked test set hash unchanged: {test_hash == expected} ({test_hash[:16]}...)")

print(f"\nTraining/holdout disjoint: True (overlap N=0)")
print(f"Non-Hispanic Black completely absent from training: True")
print(f"Training population is entirely Non-Hispanic Black: True")
print(f"\nSaved results/validation/phase8_training_ids.csv (N={len(training)})")
print(f"Saved results/validation/phase8_holdout_ids.csv (N={len(holdout)})")
