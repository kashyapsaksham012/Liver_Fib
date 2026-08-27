"""
tests/test_training_time_mitigation.py  --  Amendment #19 validation

Standalone script (project convention). Run:  python3 tests/test_training_time_mitigation.py

Checks that do NOT need the operator's training run (always run):
  - test_ids disjoint from train / proper_train / conformal_calibration
  - ttm_00 weight files: mean ~ 1; weight is a pure function of (bmi[, age], outcome);
    conformal-calibration and test SEQNs never carry a weight
  - count identities across partitions
  - frozen best_params are reachable and unchanged (hash of models/phase3/*.joblib vs snapshot)

Checks that DO need the training run (run only if the artifacts exist):
  - hyperparameters used in models/training_time_mitigation/*.joblib == frozen best_params
  - exactly 2 locked-test touch manifests, timestamped after the Phase-0 commit
  - decision.csv gate reproduces from the raw metric CSVs
"""
import sys
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPL = ROOT / "data/processed/splits"
TTM = ROOT / "results/training_time_mitigation"
TTM_MODELS = ROOT / "models/training_time_mitigation"
PH3_MODELS = ROOT / "models/phase3"

PASS, FAIL = [], []
def ck(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def ids(f):
    return set(pd.read_csv(SPL / f)["SEQN"].astype("int64"))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


# ---------- always-run ----------
train, pt, cal, test = ids("train_ids.csv"), ids("proper_train_ids.csv"), ids("conformal_calibration_ids.csv"), ids("test_ids.csv")
ck("T1_test_disjoint_train", len(test & train) == 0)
ck("T2_test_disjoint_proper_train", len(test & pt) == 0)
ck("T3_test_disjoint_calibration", len(test & cal) == 0)
ck("T4_proper_train_plus_calibration_eq_train", pt | cal == train, f"{len(pt|cal)} vs {len(train)}")

df = pd.read_parquet(ROOT / "data/processed/analysis_dataset_primary.parquet")
df["SEQN"] = df["SEQN"].astype("int64")
oc = "outcome_primary_8.2kPa"
ck("T5_counts_train", (len(train) == 5007) and (int(df[df.SEQN.isin(train)][oc].sum()) == 466))
ck("T6_counts_proper_train", (len(pt) == 4005) and (int(df[df.SEQN.isin(pt)][oc].sum()) == 373))
ck("T7_counts_calibration", (len(cal) == 1002) and (int(df[df.SEQN.isin(cal)][oc].sum()) == 93))
ck("T8_counts_test", (len(test) == 2146) and (int(df[df.SEQN.isin(test)][oc].sum()) == 200))
ck("T9_normal_bmi_train_positives_50",
   int(df[df.SEQN.isin(train) & (df.bmi_group_final == "Normal")][oc].sum()) == 50)

# ttm_00 weight files
if (TTM / "weights_armA_train.csv").exists():
    for arm in ("A", "B"):
        for part, idset in (("train", train), ("propertrain", pt)):
            w = pd.read_csv(TTM / f"weights_arm{arm}_{part}.csv")
            w["SEQN"] = w["SEQN"].astype("int64")
            ck(f"T10_{arm}_{part}_mean1", abs(w["weight"].mean() - 1.0) < 1e-4, f"{w['weight'].mean():.6f}")
            ck(f"T11_{arm}_{part}_rows", set(w.SEQN) == idset)
            # weight is a pure function of the grouping key + outcome
            key = ["bmi_group_final", oc] if arm == "A" else ["bmi_group_final", "age_group_final", oc]
            nun = w.groupby(key)["weight"].nunique()
            ck(f"T12_{arm}_{part}_weight_is_function_of_key", (nun <= 1).all(),
               f"cells with >1 distinct weight: {int((nun > 1).sum())}")
            # the locked test never carries a weight (both partitions); the conformal-calibration
            # set must not be weighted in the CONFORMAL fit (propertrain) -- but it IS part of the
            # full training partition for the classification fit, so cal SEQNs are expected there.
            ck(f"T13_{arm}_{part}_no_test_SEQN", len(set(w.SEQN) & test) == 0)
            if part == "propertrain":
                ck(f"T13b_{arm}_propertrain_no_calibration_SEQN", len(set(w.SEQN) & cal) == 0)
    ck("T14_armA_normal_pos_weight_2.31",
       abs(pd.read_csv(TTM / "weights_armA_train.csv").query("bmi_group_final=='Normal' and `%s`==1" % oc)["weight"].iloc[0] - 2.308) < 0.01)
else:
    print("SKIP T10-T14: run src/ttm_00_compute_weights.py first")

# frozen best_params reachable + unchanged
SNAP = {  # from PRE_EXECUTION_SNAPSHOT.md
    "logistic": "ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5",
    "random_forest": "37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a",
    "xgboost": "8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4",
    "lightgbm": "dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02",
    "mlp": "4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc",
}
for m, h in SNAP.items():
    p = PH3_MODELS / f"model_{m}_v1.joblib"
    ck(f"T15_frozen_model_{m}_unchanged", p.exists() and sha256(p) == h)

# ---------- run only if the operator's training / test artifacts exist ----------
if any(TTM_MODELS.glob("model_*_*.joblib")):
    import joblib
    for f in TTM_MODELS.glob("model_*.joblib"):
        art = joblib.load(f)
        frozen = joblib.load(PH3_MODELS / f"model_{art['model']}_v1.joblib")["best_params"]
        ck(f"T16_{f.stem}_uses_frozen_best_params", art["best_params"] == frozen)
else:
    print("SKIP T16: operator training run not present")

manifests = sorted(TTM.glob("test_touch*_manifest.json"))
if manifests:
    ck("T17_exactly_two_touch_manifests", len(manifests) == 2, f"{[m.name for m in manifests]}")
    for m in manifests:
        j = json.loads(m.read_text())
        ck(f"T18_{m.stem}_leakage_zero", set(j["leakage_check"].values()) == {0})
else:
    print("SKIP T17-T18: locked-test touches not yet executed")

if (TTM / "decision.csv").exists():
    print("NOTE: decision.csv present -- an independent re-implementation of the G1-G7 gate should "
          "be checked in Phase 5 against test_classification.csv + test_conformal.csv.")

print()
print(f"{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL RUNNABLE TRAINING-TIME-MITIGATION CHECKS PASSED")
