"""
phase6_01_partition_audit.py
Phase 6 Part 3-4: verify proper_train / conformal_calibration / test partitions -- exact
counts, pairwise disjointness, positives/negatives, and the frozen test-set hash. STOP on any
overlap or hash mismatch.
"""
import sys
import hashlib
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, SPLIT_DIR, PRIMARY_OUTCOME_COL
from phase3_common import load_primary_dataset, fail

EXPECTED_TEST_HASH = "a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# Part 4: test-set hash verification FIRST
live_test_hash = sha256(SPLIT_DIR / "test_ids.csv")
if live_test_hash != EXPECTED_TEST_HASH:
    fail(f"TEST SET HASH MISMATCH: expected {EXPECTED_TEST_HASH}, got {live_test_hash}")
print(f"Test-set hash VERIFIED: {live_test_hash}")

master = load_primary_dataset()
master_idx = master.set_index("SEQN")

partitions = {}
for name, fname, expected_n in [
    ("proper_train", "proper_train_ids.csv", 4005),
    ("conformal_calibration", "conformal_calibration_ids.csv", 1002),
    ("test", "test_ids.csv", 2146),
]:
    ids = pd.read_csv(SPLIT_DIR / fname)["SEQN"]
    if len(ids) != ids.nunique():
        fail(f"{name}: duplicate SEQN within partition file")
    if len(ids) != expected_n:
        fail(f"{name}: expected N={expected_n}, found N={len(ids)}")
    partitions[name] = set(ids.tolist())

rows = []
for name in partitions:
    ids = partitions[name]
    outcomes = master_idx.loc[list(ids), PRIMARY_OUTCOME_COL]
    n_pos = int((outcomes == 1).sum())
    n_neg = int((outcomes == 0).sum())
    rows.append({
        "partition": name, "file": f"data/processed/splits/{'proper_train_ids.csv' if name=='proper_train' else name+'_ids.csv'}",
        "sha256": sha256(SPLIT_DIR / (f"proper_train_ids.csv" if name == "proper_train" else f"{name}_ids.csv")),
        "n": len(ids), "positives": n_pos, "negatives": n_neg,
    })

overlap_pt_cc = partitions["proper_train"] & partitions["conformal_calibration"]
overlap_pt_test = partitions["proper_train"] & partitions["test"]
overlap_cc_test = partitions["conformal_calibration"] & partitions["test"]

for row in rows:
    row["overlap_with_proper_train"] = "n/a" if row["partition"] == "proper_train" else len(partitions["proper_train"] & partitions[row["partition"]])
    row["overlap_with_conformal_calibration"] = "n/a" if row["partition"] == "conformal_calibration" else len(partitions["conformal_calibration"] & partitions[row["partition"]])
    row["overlap_with_test"] = "n/a" if row["partition"] == "test" else len(partitions["test"] & partitions[row["partition"]])
    row["verification_status"] = "PASS"

out = pd.DataFrame(rows)
out.to_csv(ROOT / "results" / "uncertainty" / "phase6_partition_audit.csv", index=False)
print(out.to_string(index=False))

if overlap_pt_cc or overlap_pt_test or overlap_cc_test:
    fail(f"PARTITION OVERLAP DETECTED: pt∩cc={len(overlap_pt_cc)}, pt∩test={len(overlap_pt_test)}, cc∩test={len(overlap_cc_test)}")

print("\nPASS: proper_train, conformal_calibration, and test are pairwise disjoint, all counts match expected values.")
print(f"proper_train: N={len(partitions['proper_train'])}, conformal_calibration: N={len(partitions['conformal_calibration'])}, test: N={len(partitions['test'])}")
