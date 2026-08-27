"""Build a prediction-input-only temporal cohort with CDC's ALT bridge.

This script does not load model artifacts, calculate predictions, or write outcomes.
It reads the six temporal XPT files and writes a new, feature-only CSV.  The raw
XPT files and the unbridged source values are never changed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
TEMPORAL_DIR = ROOT.parent / "NHANES 2021–2023 temporal validation dataset"
OUTPUT_DIR = ROOT / "data" / "processed" / "temporal_validation"
OUTPUT_CSV = OUTPUT_DIR / "temporal_validation_input_cobas6000_alt.csv"
MANIFEST_JSON = OUTPUT_DIR / "temporal_validation_input_cobas6000_alt_manifest.json"

FEATURES = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL",
    "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD",
]
SENTINEL_BAND = (1e-80, 1e-70)


def read_xpt(filename: str, columns: list[str]) -> pd.DataFrame:
    frame = pd.read_sas(TEMPORAL_DIR / filename, format="xport", encoding="utf-8")[columns]
    for column in frame.select_dtypes(include="number"):
        values = frame[column]
        frame.loc[(values.abs() > SENTINEL_BAND[0]) & (values.abs() < SENTINEL_BAND[1]), column] = np.nan
    frame["SEQN"] = pd.to_numeric(frame["SEQN"], errors="raise").astype("Int64")
    if frame["SEQN"].duplicated().any():
        raise ValueError(f"Duplicate SEQN in {filename}")
    return frame


def main() -> None:
    # Only the original cohort-membership predicates are used. LUXSMED values and
    # outcome labels are deliberately excluded from the output.
    lux = read_xpt("LUX_L.xpt", ["SEQN", "LUAXSTAT", "LUXSMED"])
    demo = read_xpt("DEMO_L.xpt", ["SEQN", "RIDAGEYR", "RIAGENDR"])
    bmx = read_xpt("BMX_L.xpt", ["SEQN", "BMXBMI"])
    biopro = read_xpt("BIOPRO_L.xpt", ["SEQN", "LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB"])
    cbc = read_xpt("CBC_L.xpt", ["SEQN", "LBXPLTSI"])
    hdl = read_xpt("HDL_L.xpt", ["SEQN", "LBDHDD"])

    merged = lux
    for frame in (demo, bmx, biopro, cbc, hdl):
        merged = merged.merge(frame, on="SEQN", how="left", validate="one_to_one")

    eligible = (
        merged["LUXSMED"].notna()
        & merged["LUAXSTAT"].eq(1)
        & merged["RIDAGEYR"].ge(18)
        & merged[FEATURES].notna().all(axis=1)
    )
    prediction_input = merged.loc[eligible, ["SEQN", *FEATURES]].copy()
    if len(prediction_input) != 4910 or prediction_input["SEQN"].nunique() != 4910:
        raise ValueError("Frozen temporal cohort identity/count changed; no output written.")

    raw_alt = prediction_input["LBXSATSI"].copy()
    # CDC BIOPRO_L backward equation: Cobas 8000 -> Cobas 6000.
    prediction_input["LBXSATSI"] = -1.529 + 1.035 * raw_alt

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prediction_input.to_csv(OUTPUT_CSV, index=False)
    output_hash = hashlib.sha256(OUTPUT_CSV.read_bytes()).hexdigest()
    manifest = {
        "purpose": "Prediction-input-only temporal-validation copy; no predictions were run.",
        "n_rows": len(prediction_input),
        "n_unique_seqn": int(prediction_input["SEQN"].nunique()),
        "columns": ["SEQN", *FEATURES],
        "outcome_columns_written": [],
        "raw_xpt_modified": False,
        "model_artifacts_modified": False,
        "cohort_membership_changed": False,
        "temporal_outcomes_used_for_bridge_or_model_parameters": False,
        "only_transformation": {
            "variable": "LBXSATSI",
            "direction": "Cobas 8000 to Cobas 6000",
            "formula": "Y_Cobas6000 = -1.529 + 1.035 * X_Cobas8000",
            "raw_min": float(raw_alt.min()),
            "raw_max": float(raw_alt.max()),
            "bridged_min": float(prediction_input["LBXSATSI"].min()),
            "bridged_max": float(prediction_input["LBXSATSI"].max()),
        },
        "sha256": output_hash,
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
