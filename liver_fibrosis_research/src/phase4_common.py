"""
phase4_common.py
Shared constants and utilities for Phase 4 (Calibration). Every value here is copied
verbatim from documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md (frozen 2436d95).
Not a script -- imported by phase4_0*.py. Does not modify or re-derive any Phase 3 value;
imports phase3_common.py directly for those.
"""
import sys
import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import (
    ROOT, PROC_DIR, SPLIT_DIR, MODEL_DIR, PRED_DIR,
    PRIMARY_COHORT_N, PRIMARY_OUTCOME_COL, PRIMARY_OUTCOME_POSITIVE_N,
    PRIMARY_PREDICTORS, RANDOM_SEED, MODEL_NAMES, ID_COL,
)

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

CALIB_DOC_DIR = ROOT / "documentation" / "calibration"
CALIB_RESULTS_DIR = ROOT / "results" / "calibration"
CALIB_FIG_DIR = CALIB_RESULTS_DIR / "figures"
CALIB_CURVE_DATA_DIR = CALIB_RESULTS_DIR / "curve_data"
for d in (CALIB_DOC_DIR, CALIB_RESULTS_DIR, CALIB_FIG_DIR, CALIB_CURVE_DATA_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Frozen from documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md, commit 2436d95 ──
CALIBRATION_PROTOCOL_COMMIT = "2436d9554647c65af43e7d8cc61cdfeed9fb9a6a"
CALIBRATION_PROTOCOL_CHECKSUM = "3c843ad02cd91736a597ad3256a6c6309ffac2819a882c72f77b9220c64fca1d"

# Model set (§5) -- 5 primary models, evaluated as frozen best_estimator_ artifacts only
PRIMARY_MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
SENSITIVITY_MODEL = "mlp_balanced"  # explicitly NOT primary (§5, §14)

MODEL_ARTIFACT_FILES = {
    "logistic": "model_logistic_v1.joblib",
    "random_forest": "model_random_forest_v1.joblib",
    "xgboost": "model_xgboost_v1.joblib",
    "lightgbm": "model_lightgbm_v1.joblib",
    "mlp": "model_mlp_v1.joblib",
    "mlp_balanced": "model_mlp_balanced_v1_sensitivity.joblib",
}

# Calibration-data separation (§6): OOF (development, repeatable) + locked test (confirmatory, one-time)
OOF_PREDICTION_FILE = lambda name: PRED_DIR / f"validation_predictions_{name}.csv"
TEST_PREDICTION_FILE = lambda name: PRED_DIR / f"test_predictions_{name}.csv"

# §12 -- CI method
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = RANDOM_SEED  # reuse the frozen project seed for reproducibility, not a new choice
CI_LEVEL = 0.95

# §9 -- calibration curve binning
N_CALIBRATION_BINS = 10  # equal-frequency (decile) bins

def fail(msg):
    print(f"PHASE 4 STOP CONDITION: {msg}")
    sys.exit(1)

def load_oof_predictions(name):
    df = pd.read_csv(OOF_PREDICTION_FILE(name))
    expected_cols = {"SEQN", "true_target", "predicted_probability"}
    if not expected_cols.issubset(df.columns):
        fail(f"OOF prediction file for {name} missing expected columns: {expected_cols - set(df.columns)}")
    return df

def load_test_predictions(name):
    df = pd.read_csv(TEST_PREDICTION_FILE(name))
    expected_cols = {"SEQN", "true_target", "predicted_probability"}
    if not expected_cols.issubset(df.columns):
        fail(f"Test prediction file for {name} missing expected columns: {expected_cols - set(df.columns)}")
    return df
