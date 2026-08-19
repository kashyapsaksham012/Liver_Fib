"""
phase5_common.py
Shared constants and utilities for Phase 5 (Fairness). Every value here is copied verbatim
from the frozen Phase 2 fairness documents (fairness_subgroup_protocol.md, fairness_definition.md,
multiple_comparisons_protocol.md, evaluation_metrics_protocol.md, statistical_analysis_plan.md),
read live in full this pass -- see documentation/fairness/phase5_pre_execution_snapshot.md.
Not a script -- imported by phase5_0*.py.
"""
import sys
import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, PROC_DIR, SPLIT_DIR, MODEL_DIR, PRED_DIR, PRIMARY_PREDICTORS, PRIMARY_OUTCOME_COL
from phase4_common import CALIBRATION_PROTOCOL_COMMIT  # unrelated constant, imported only to confirm cross-phase module chain works

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

FAIR_DOC_DIR = ROOT / "documentation" / "fairness"
FAIR_RESULTS_DIR = ROOT / "results" / "fairness"
FAIR_FIG_DIR = FAIR_RESULTS_DIR / "figures"
FAIR_CURVE_DATA_DIR = FAIR_RESULTS_DIR / "curve_data"
for d in (FAIR_DOC_DIR, FAIR_RESULTS_DIR, FAIR_FIG_DIR, FAIR_CURVE_DATA_DIR):
    d.mkdir(parents=True, exist_ok=True)

PRIMARY_MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]

# ── Frozen thresholds from Phase 3 (test-set operating point per model, Youden's J on OOF) ──
# Source: results/tables/phase3_overall_discrimination.csv (frozen, read-only)
FROZEN_THRESHOLDS = {
    "logistic": 0.5173, "random_forest": 0.4499, "xgboost": 0.4108,
    "lightgbm": 0.4988, "mlp": 0.1065,
}

# ── Subgroup dimensions and bins (fairness_subgroup_protocol.md) ──
SEX_MAP = {1.0: "Male", 2.0: "Female"}
RACE_MAP_RIDRETH3 = {1.0: "Mexican American", 2.0: "Other Hispanic", 3.0: "Non-Hispanic White",
                     4.0: "Non-Hispanic Black", 6.0: "Non-Hispanic Asian", 7.0: "Other Race / Multi-Racial"}

_AGE_BINS = [17, 39, 59, 120]
_AGE_LABELS = ["18-39", "40-59", "60+"]

def bin_age(age):
    # Matches the canonical binning in phase2_04_build_analysis_dataset.py exactly:
    # pd.cut(..., bins=[17, 39, 59, 120]). Integer ages make this equivalent to the
    # hand-rolled <=39/<=59/else version, but pd.cut is used directly to eliminate any
    # boundary-convention risk, after the BMI boundary mismatch found in this same pass.
    if age < 18:
        return None  # structurally empty in the adult-only primary cohort
    result = pd.cut(pd.Series([age]), bins=_AGE_BINS, labels=_AGE_LABELS)[0]
    return None if pd.isna(result) else str(result)

_BMI_BINS = [0, 18.5, 24.9, 29.9, 200]
_BMI_LABELS = ["Underweight", "Normal", "Overweight", "Obese"]

def bin_bmi(bmi):
    # Must match the canonical binning in phase2_04_build_analysis_dataset.py exactly:
    # pd.cut(..., bins=[0, 18.5, 24.9, 29.9, 200]) is right-inclusive by default, so
    # BMI == 18.5 falls into "Underweight", not "Normal". A naive `< 18.5` here would
    # misclassify the 7 participants with BMXBMI == 18.5 exactly (root-caused this pass:
    # phase5_01 initially found Underweight=102/Normal=1809 vs. the frozen 109/1802 --
    # traced to this boundary-convention mismatch, not a data error).
    result = pd.cut(pd.Series([bmi]), bins=_BMI_BINS, labels=_BMI_LABELS)[0]
    return None if pd.isna(result) else str(result)

DIMENSIONS = {
    "sex": {"col": "RIAGENDR", "map_fn": lambda v: SEX_MAP.get(v), "reference": "Male"},
    "race_ethnicity": {"col": "RIDRETH3", "map_fn": lambda v: RACE_MAP_RIDRETH3.get(v), "reference": "Non-Hispanic White"},
    "age": {"col": "RIDAGEYR", "map_fn": bin_age, "reference": "40-59"},
    "bmi": {"col": "BMXBMI", "map_fn": bin_bmi, "reference": "Normal"},
}

# ── Precision tiers (frozen heuristic, fairness_subgroup_protocol.md) ──
def precision_tier(n_pos, n_neg):
    if n_pos < 10 or n_neg < 10:
        return "insufficient evidence"
    if n_pos < 30 or n_neg < 30:
        return "limited precision"
    if n_pos < 100 or n_neg < 100:
        return "exploratory candidate"
    return "primary-feasibility candidate"

# ── Primary/secondary fairness metrics (fairness_definition.md, evaluation_metrics_protocol.md) ──
PRIMARY_FAIRNESS_METRIC = "sensitivity"
SECONDARY_FAIRNESS_METRICS = ["roc_auc", "specificity", "fnr", "fpr", "calibration_intercept", "calibration_slope"]
MEANINGFUL_DIFFERENCE_PP = 10.0  # percentage points, frozen tolerance

# ── Inference (fairness_definition.md: bootstrap 2000, stratified within subgroup) ──
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 42  # frozen project seed, reused deliberately (same discipline as Phase 4)
CI_LEVEL = 0.95

# ── Pre-specified exploratory intersectional cells ──
INTERSECTIONAL_FEASIBILITY_FILE = ROOT / "results" / "tables" / "phase2_intersectional_feasibility.csv"

def load_demographics():
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    return df[["SEQN", "RIAGENDR", "RIDRETH3", "RIDAGEYR", "BMXBMI", PRIMARY_OUTCOME_COL]].copy()

def fail(msg):
    print(f"PHASE 5 STOP CONDITION: {msg}")
    sys.exit(1)
