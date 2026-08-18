"""
02_load_and_profile.py
Phase 1 Remediation - Load and Profile (sentinel-corrected).
Loads every file (with SAS special-missing sentinel correction applied), compiles the
complete variable dictionary, and generates column profiles in JSON format.

Produces:
  documentation/data_dictionary/complete_variable_dictionary.csv
  documentation/audit_reports/per_file_column_profiles/..._profile.json
"""

import os, sys, json, warnings
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import DICT_DIR, AUDIT_DIR, REQUIRED_FILES, VAR_METADATA, load_xpt

warnings.filterwarnings("ignore", category=FutureWarning)

PROF_DIR = AUDIT_DIR / "per_file_column_profiles"
PROF_DIR.mkdir(parents=True, exist_ok=True)

def profile_col(s):
    n = len(s)
    n_miss = int(s.isna().sum())
    n_obs = n - n_miss
    pct = round(100 * n_miss / n, 2) if n > 0 else 0.0
    dtype = str(s.dtype)

    if pd.api.types.is_numeric_dtype(s) and n_obs > 0:
        stats = s.describe().to_dict()
        uniq = int(s.nunique(dropna=True))
        return {
            "dtype": dtype, "n_obs": n_obs, "n_missing": n_miss, "pct_missing": pct,
            "min": round(float(stats.get("min", float("nan"))), 4),
            "max": round(float(stats.get("max", float("nan"))), 4),
            "mean": round(float(stats.get("mean", float("nan"))), 4),
            "median": round(float(stats.get("50%", float("nan"))), 4),
            "std": round(float(stats.get("std", float("nan"))), 4),
            "unique_values": uniq, "sample_values": None
        }
    else:
        vc = s.value_counts(dropna=False).head(10).to_dict()
        uniq = int(s.nunique(dropna=True))
        return {
            "dtype": dtype, "n_obs": n_obs, "n_missing": n_miss, "pct_missing": pct,
            "min": None, "max": None, "mean": None, "median": None, "std": None,
            "unique_values": uniq, "sample_values": str(vc)
        }

def main():
    print("=== Step 2 & 3: Load and Profile Column Metadata (sentinel-corrected) ===")
    all_vars = []

    for fname in REQUIRED_FILES:
        print(f"Profiling {fname} (sentinel-corrected load)...")
        df = load_xpt(fname)

        prof = {}
        for col in df.columns:
            col_prof = profile_col(df[col])
            prof[col] = col_prof

            meta = VAR_METADATA.get(col)
            if meta:
                role = meta["role"]
            elif col.endswith("LC"):
                role = "quality"  # NHANES detection-limit comment/flag code, not a lab concentration value
            elif col.startswith("LBX") or col.startswith("LBD"):
                role = "candidate_predictor"
            else:
                role = "unknown"

            all_vars.append({
                "source_file": fname, "variable": col, "dtype": col_prof["dtype"], "role": role,
                "n_obs": col_prof["n_obs"], "n_missing": col_prof["n_missing"], "pct_missing": col_prof["pct_missing"],
                "unique_values": col_prof["unique_values"], "min": col_prof["min"], "max": col_prof["max"],
                "mean": col_prof["mean"], "median": col_prof["median"], "std": col_prof["std"],
                "sample_values": col_prof["sample_values"]
            })

        jname = fname.replace(".", "_") + "_profile.json"
        with open(PROF_DIR / jname, "w") as jf:
            json.dump(prof, jf, indent=2, default=str)

    out_csv = DICT_DIR / "complete_variable_dictionary.csv"
    pd.DataFrame(all_vars).to_csv(out_csv, index=False)
    print(f"Saved complete variable dictionary to {out_csv}")
    print("[STEP 2 & 3 COMPLETE]")

if __name__ == "__main__":
    main()
