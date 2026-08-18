"""
phase3_common.py
Shared constants and utilities for Phase 3 (model development). Every value here is
either copied verbatim from the frozen Phase 2 protocol or is a Phase-3-start
decision explicitly recorded in documentation/phase3/phase3_pre_modeling_snapshot.md.
Not a script -- imported by phase3_0*.py.
"""
import sys
import datetime
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT  # reuse the Phase 1/2 project-root resolver

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

PROC_DIR = ROOT / "data" / "processed"
SPLIT_DIR = PROC_DIR / "splits"
MODEL_DIR = ROOT / "models" / "phase3"
PRED_DIR = ROOT / "results" / "predictions"
TAB_DIR = ROOT / "results" / "tables"
FIG_DIR = ROOT / "results" / "figures"
DOC_DIR = ROOT / "documentation" / "phase3"
for d in (SPLIT_DIR, MODEL_DIR, PRED_DIR, TAB_DIR, FIG_DIR, DOC_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Frozen from documentation/phase2/PHASE2_PROTOCOL_FREEZE.md — DO NOT MODIFY ────────
PRIMARY_COHORT_N = 7153
PRIMARY_OUTCOME_COL = "outcome_primary_8.2kPa"
PRIMARY_OUTCOME_POSITIVE_N = 666
PRIMARY_PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL",
                     "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
FORBIDDEN_VARS = ["LUXSMED", "LUXCAPM", "LUXSIQR", "LUXSIQRM", "LUXCPIQR", "LUAXSTAT",
                 "LUARXNC", "LUARXND", "LUARXIN", "LUANMVGP", "LUANMTGP",
                 "BMDSTATS", "BMIWT", "BMIHT", "RIDRETH1", "RIDRETH3",
                 "WTMECPRP", "WTINTPRP", "WTSAFPRP", "SDMVPSU", "SDMVSTRA", "SEQN"]
ID_COL = "SEQN"
STRATIFICATION_METADATA_COLS = ["RIDRETH1", "RIDRETH3"]  # retained for fairness, never as predictors
FAIRNESS_METADATA_COLS = ["RIDRETH1", "RIDRETH3", "WTMECPRP", "WTINTPRP", "WTSAFPRP", "SDMVPSU", "SDMVSTRA"]

# ── Fixed at Phase 3 start (documentation/phase3/phase3_pre_modeling_snapshot.md) ─────
RANDOM_SEED = 42
TRAIN_FRACTION = 0.70  # 70/30 train/test, stratified on PRIMARY_OUTCOME_COL (frozen: model_development_protocol.md)
N_CV_FOLDS = 5          # 5-fold stratified CV within training (frozen: model_development_protocol.md)
MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]

def load_primary_dataset():
    df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    return df

def load_split_ids():
    train = pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"].tolist()
    val = pd.read_csv(SPLIT_DIR / "validation_ids.csv")["SEQN"].tolist()
    test = pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"].tolist()
    return train, val, test

def fail(msg):
    print(f"CRITICAL STOP CONDITION: {msg}")
    sys.exit(1)
