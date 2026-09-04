"""Phase 0-1 — freeze the frozen-artifact hash manifest.

Run once, before anything else. Writes FROZEN_ARTIFACT_MANIFEST.csv with the
SHA-256 of every frozen artifact the temporal validation will read. From then on
_thelpers.load_frozen() refuses to load any of them if the hash has changed.
"""
from __future__ import annotations

import pandas as pd

from _thelpers import REPO, TV, MODELS, sha256

FROZEN_ARTIFACTS = [
    # scoring models
    *[f"models/phase3/model_{m}_v1.joblib" for m in MODELS],
    *[f"models/phase6_conformal_refit/model_{m}_proper_train_refit.joblib" for m in MODELS],
    # parameter sources
    "results/tables/phase3_final_baseline_results.csv",
    "results/calibration/test_set_recalibrated_predictions.csv",
    "results/uncertainty/conformal_thresholds_by_model.csv",
    # 2017-2020 comparison values
    "results/calibration/test_set_calibration_final.csv",
    "results/fairness/fairness_inference.csv",
    "results/uncertainty/subgroup_coverage.csv",
    "results/uncertainty/marginal_coverage_test_set.csv",
    "results/uncertainty/intersectional_coverage_ci.csv",
    "results/fairness/subgroup_discrimination_metrics.csv",
    "results/prepublication_fixes/fix2_bmi_shortcut_check.csv",
    # protocol reference
    "data/processed/analysis_dataset_primary.parquet",
]


def main():
    rows = []
    missing = []
    for a in FROZEN_ARTIFACTS:
        p = REPO / a
        if not p.exists():
            missing.append(a)
            continue
        rows.append({"artifact": a, "sha256": sha256(p), "bytes": p.stat().st_size})
    df = pd.DataFrame(rows)
    out = TV / "FROZEN_ARTIFACT_MANIFEST.csv"
    df.to_csv(out, index=False)
    print(f"wrote {out} — {len(df)} artifacts hashed")
    if missing:
        print("MISSING (investigate before proceeding):")
        for m in missing:
            print("  ", m)


if __name__ == "__main__":
    main()
