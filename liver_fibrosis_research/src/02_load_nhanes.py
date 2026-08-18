"""
02_load_nhanes.py  –  Phase 1 Step 2 & 3
Load every XPT file, produce per-file column profiles and the complete variable dictionary.

Outputs:
  documentation/data_dictionary/complete_variable_dictionary.csv
  documentation/audit_reports/per_file_column_profiles/  (one JSON per file)
"""

import json, datetime, warnings
import pandas as pd
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT    = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "NHANES_2017_2020"
DICT_DIR = ROOT / "documentation" / "data_dictionary"
PROF_DIR = ROOT / "documentation" / "audit_reports" / "per_file_column_profiles"
DICT_DIR.mkdir(parents=True, exist_ok=True)
PROF_DIR.mkdir(parents=True, exist_ok=True)

# Role mapping hints
ROLE_MAP = {
    "SEQN": "id_key",
    # LUX
    "LUXSMED": "candidate_outcome", "LUXSIQR": "quality", "LUXCAPM": "candidate_outcome",
    "LUXSCOR": "quality", "LUXS": "quality",
    # DEMO
    "RIDAGEYR": "demographic", "RIAGENDR": "demographic",
    "RIDRETH3": "demographic", "RIDRETH1": "demographic",
    "WTMECPRP": "survey_weight", "WTINTPRP": "survey_weight",
    "SDMVPSU": "survey_design", "SDMVSTRA": "survey_design",
    # BMX
    "BMXBMI": "candidate_predictor", "BMXWT": "candidate_predictor",
    "BMXHT": "candidate_predictor",
}

def profile_column(s: pd.Series):
    n      = len(s)
    n_miss = int(s.isna().sum())
    n_obs  = n - n_miss
    pct    = round(100*n_miss/n, 2) if n > 0 else 0
    dtype  = str(s.dtype)
    if pd.api.types.is_numeric_dtype(s) and n_obs > 0:
        stats = s.describe().to_dict()
        uniq  = int(s.nunique(dropna=True))
        return dict(dtype=dtype, n_obs=n_obs, n_missing=n_miss, pct_missing=pct,
                    min=round(stats.get("min",float("nan")),4),
                    max=round(stats.get("max",float("nan")),4),
                    mean=round(stats.get("mean",float("nan")),4),
                    median=round(stats.get("50%",float("nan")),4),
                    std=round(stats.get("std",float("nan")),4),
                    unique_values=uniq, sample_values=None)
    else:
        vc   = s.value_counts(dropna=False).head(10).to_dict()
        uniq = int(s.nunique(dropna=True))
        return dict(dtype=dtype, n_obs=n_obs, n_missing=n_miss, pct_missing=pct,
                    min=None, max=None, mean=None, median=None, std=None,
                    unique_values=uniq, sample_values=str(vc))

all_rows = []

files = sorted(RAW_DIR.glob("*.xpt")) + sorted(RAW_DIR.glob("*.XPT"))
files = list({p.name:p for p in files}.values())

for path in files:
    fname = path.name
    print(f"\nLoading {fname} ...")
    df = pd.read_sas(path, format="xport", encoding="utf-8")
    print(f"  Shape: {df.shape}")

    profile = {}
    for col in df.columns:
        profile[col] = profile_column(df[col])

    # save per-file JSON profile
    jpath = PROF_DIR / f"{fname.replace('.','_')}_profile.json"
    with open(jpath,"w") as jf:
        json.dump(profile, jf, indent=2, default=str)

    for col, info in profile.items():
        role = ROLE_MAP.get(col, "")
        # Infer role from prefix if not in map
        if not role:
            for pfx, r in [("LUXS","quality"),("LUX","candidate_outcome"),
                           ("WTM","survey_weight"),("WTI","survey_weight"),
                           ("SDM","survey_design"),("RID","demographic"),
                           ("RIA","demographic"),("BMX","candidate_predictor")]:
                if col.startswith(pfx): role = r; break
        all_rows.append({
            "dataset": fname,
            "variable": col,
            "dtype": info["dtype"],
            "role": role or "unknown",
            "n_obs": info["n_obs"],
            "n_missing": info["n_missing"],
            "pct_missing": info["pct_missing"],
            "unique_values": info["unique_values"],
            "min": info["min"],
            "max": info["max"],
            "mean": info["mean"],
            "median": info["median"],
            "std": info["std"],
            "sample_values": info["sample_values"],
        })

out = DICT_DIR / "complete_variable_dictionary.csv"
pd.DataFrame(all_rows).to_csv(out, index=False)
print(f"\nSaved → {out}  ({len(all_rows)} variables)")
print("[STEP 2–3 COMPLETE]")
