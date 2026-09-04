"""Phase 0-2 — hash the frozen inputs, build the pooled 2017-2023 cohort, split.

Reads:  ../data/processed/analysis_dataset_primary.parquet   (2017-2020 CAND_1)
        ../temporal_validation_2021_2023/data/processed/temporal_cohort_2021_2023.parquet
Writes: pooled_model_update_2017_2023/{FROZEN_ARTIFACT_MANIFEST.csv,
        data/processed/pooled_cohort_2017_2023.parquet, splits, manifest}
Nothing in the frozen tree or the temporal module is modified.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from _phelpers import (REPO, PU, TV, PREDICTORS, RACE_MAP, SEED, sha256,
                       age_band, bmi_band)

OUT = PU / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

FROZEN = [
    *[f"models/phase3/model_{m}_v1.joblib" for m in
      ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]],
    "data/processed/analysis_dataset_primary.parquet",
    "results/tables/phase3_final_baseline_results.csv",
    "results/fairness/fairness_inference.csv",
    "results/fairness/subgroup_discrimination_metrics.csv",
    "results/uncertainty/subgroup_coverage.csv",
    "results/uncertainty/marginal_coverage_test_set.csv",
    "results/prepublication_fixes/fix2_bmi_shortcut_check.csv",
]


def manifest():
    rows = []
    for a in FROZEN:
        p = REPO / a
        if p.exists():
            rows.append({"artifact": a, "sha256": sha256(p), "bytes": p.stat().st_size})
    # also hash the temporal cohort (read-only input from the sibling study)
    tvc = TV / "data" / "processed" / "temporal_cohort_2021_2023.parquet"
    rows.append({"artifact": "../temporal_validation_2021_2023/data/processed/temporal_cohort_2021_2023.parquet",
                 "sha256": sha256(tvc), "bytes": tvc.stat().st_size})
    pd.DataFrame(rows).to_csv(PU / "FROZEN_ARTIFACT_MANIFEST.csv", index=False)
    print(f"hashed {len(rows)} frozen inputs")


def main():
    manifest()

    old = pd.read_parquet(REPO / "data" / "processed" / "analysis_dataset_primary.parquet")
    new = pd.read_parquet(TV / "data" / "processed" / "temporal_cohort_2021_2023.parquet")

    keep = ["SEQN"] + PREDICTORS + ["RIDRETH3", "LUXSMED", "outcome_primary_8.2kPa"]
    old_s = old[keep].copy(); old_s["cycle"] = "2017-2020"
    new_s = new[keep].copy(); new_s["cycle"] = "2021-2023"
    pool = pd.concat([old_s, new_s], ignore_index=True)
    assert pool["SEQN"].is_unique, "SEQN collision between cycles"

    pool["age_group_final"] = age_band(pool["RIDAGEYR"].values)
    pool["bmi_group_final"] = bmi_band(pool["BMXBMI"].values)
    pool["race_label"] = pool["RIDRETH3"].map(RACE_MAP)
    pool["_stratum"] = pool["cycle"] + "_" + pool["outcome_primary_8.2kPa"].astype(str)

    tr_idx, te_idx = train_test_split(pool.index, test_size=0.30, random_state=SEED,
                                      stratify=pool["_stratum"])
    pool["split"] = "train"
    pool.loc[te_idx, "split"] = "test"

    parquet = OUT / "pooled_cohort_2017_2023.parquet"
    pool.drop(columns="_stratum").to_parquet(parquet, index=False)
    pool.loc[pool.split == "train", ["SEQN"]].to_csv(OUT / "pooled_train_ids.csv", index=False)
    pool.loc[pool.split == "test", ["SEQN"]].to_csv(OUT / "pooled_test_ids.csv", index=False)

    def cell(df):
        return {"N": len(df), "pos": int(df["outcome_primary_8.2kPa"].sum()),
                "prev_pct": round(100 * df["outcome_primary_8.2kPa"].mean(), 3)}

    man = {
        "pooled_cohort": "NHANES 2017-March 2020 CAND_1 + NHANES 2021-2023 CAND_1",
        "N_total": len(pool), "n_positive": int(pool["outcome_primary_8.2kPa"].sum()),
        "prevalence_pct": round(100 * pool["outcome_primary_8.2kPa"].mean(), 3),
        "by_cycle": {
            "2017-2020": cell(pool[pool.cycle == "2017-2020"]),
            "2021-2023": cell(pool[pool.cycle == "2021-2023"]),
        },
        "split": {
            "train": cell(pool[pool.split == "train"]),
            "test": cell(pool[pool.split == "test"]),
        },
        "test_by_cycle": {
            "2017-2020": cell(pool[(pool.split == "test") & (pool.cycle == "2017-2020")]),
            "2021-2023": cell(pool[(pool.split == "test") & (pool.cycle == "2021-2023")]),
        },
        "stratified_on": "cycle x outcome", "seed": SEED,
        "outcome_used_for_decisions": False,
        "parquet_sha256": sha256(parquet),
    }
    (OUT / "pooled_cohort_manifest.json").write_text(json.dumps(man, indent=2))

    print(json.dumps(man, indent=2))
    print(f"\nwrote {parquet}")


if __name__ == "__main__":
    main()
