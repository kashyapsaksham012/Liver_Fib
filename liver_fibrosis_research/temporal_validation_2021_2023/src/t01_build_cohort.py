"""Phase 2 — build the NHANES 2021-2023 temporal cohort.

Applies the frozen CAND_1 eligibility rule. Derives the outcome column but marks
it sealed (outcome_used_for_decisions: false). No frozen artifact is written.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from _thelpers import RAW, TV, PREDICTORS, age_band, bmi_band, RACE_MAP, sha256

OUT = TV / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def read_xpt(name):
    return pd.read_sas(RAW / f"{name}_L.xpt")


def main():
    demo = read_xpt("DEMO")[["SEQN", "RIDAGEYR", "RIAGENDR", "RIDRETH3", "SDDSRVYR", "RIDSTATR"]]
    bmx = read_xpt("BMX")[["SEQN", "BMXBMI"]]
    bio = read_xpt("BIOPRO")[["SEQN", "LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB"]]
    cbc = read_xpt("CBC")[["SEQN", "LBXPLTSI"]]
    hdl = read_xpt("HDL")[["SEQN", "LBDHDD"]]
    lux = read_xpt("LUX")[["SEQN", "LUAXSTAT", "LUXSMED", "LUXSIQR"]]

    df = demo.merge(lux, on="SEQN", how="left")
    for extra in (bmx, bio, cbc, hdl):
        df = df.merge(extra, on="SEQN", how="left")

    flow = {"0_demo_total": len(df)}

    # 1. elastography attempted + non-missing stiffness
    df = df[df["LUXSMED"].notna()].copy()
    flow["1_nonmissing_LUXSMED"] = len(df)

    # 2. quality-valid exam
    df = df[df["LUAXSTAT"] == 1].copy()
    flow["2_LUAXSTAT_eq_1"] = len(df)

    # 3. adult
    df = df[df["RIDAGEYR"] >= 18].copy()
    flow["3_adult"] = len(df)

    # 4. complete on all 10 predictors
    df = df[df[PREDICTORS].notna().all(axis=1)].copy()
    flow["4_complete_predictors_CAND1"] = len(df)

    df = df.reset_index(drop=True)

    # sealed outcome + bands
    df["outcome_primary_8.2kPa"] = ((df["LUXSMED"] >= 8.2) & (df["LUAXSTAT"] == 1)).astype(int)
    df["age_group_final"] = age_band(df["RIDAGEYR"].values)
    df["bmi_group_final"] = bmi_band(df["BMXBMI"].values)
    df["race_label"] = df["RIDRETH3"].map(RACE_MAP)

    n_pos = int(df["outcome_primary_8.2kPa"].sum())
    prev = n_pos / len(df)

    parquet = OUT / "temporal_cohort_2021_2023.parquet"
    df.to_parquet(parquet, index=False)

    manifest = {
        "cohort": "NHANES 2021-2023 (_L), frozen CAND_1 eligibility",
        "cohort_flow": flow,
        "N": len(df),
        "n_positive": n_pos,
        "n_negative": len(df) - n_pos,
        "prevalence_pct": round(100 * prev, 4),
        "prevalence_2017_2020_pct": 9.3108,
        "outcome_definition": "LUXSMED >= 8.2 kPa AND LUAXSTAT == 1",
        "outcome_used_for_decisions": False,
        "missing_data_strategy": "complete-case (matches frozen primary)",
        "survey_weights_used": False,
        "predictors": PREDICTORS,
        "parquet_sha256": sha256(parquet),
        "subgroup_cells": {
            "bmi_band": df.groupby("bmi_group_final")["outcome_primary_8.2kPa"].agg(["count", "sum"]).to_dict("index"),
            "age_band": df.groupby("age_group_final")["outcome_primary_8.2kPa"].agg(["count", "sum"]).to_dict("index"),
            "sex": df.groupby("RIAGENDR")["outcome_primary_8.2kPa"].agg(["count", "sum"]).to_dict("index"),
            "race": df.groupby("race_label")["outcome_primary_8.2kPa"].agg(["count", "sum"]).to_dict("index"),
        },
    }
    (OUT / "cohort_build_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))

    print("cohort flow:")
    for k, v in flow.items():
        print(f"  {k}: {v}")
    print(f"\nN = {len(df)}  positives = {n_pos}  prevalence = {prev*100:.2f}%  (2017-2020: 9.31%)")
    print("\nBMI-band positives:", {k: int(v) for k, v in df.groupby('bmi_group_final')['outcome_primary_8.2kPa'].sum().items()})
    print("age-band positives:", {k: int(v) for k, v in df.groupby('age_group_final')['outcome_primary_8.2kPa'].sum().items()})
    print(f"\nwrote {parquet}")


if __name__ == "__main__":
    main()
