"""Generate outcome-free temporal probabilities using only Phase 3 frozen artifacts.

This program deliberately does not open temporal XPT files, outcomes, labels,
thresholds, calibrators, conformal objects, or M4b material.  It loads only the
prepared feature-only CSV and the five original Phase 3 frozen pipelines.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import joblib
import lightgbm
import numpy as np
import pandas as pd
import sklearn
import xgboost


ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "processed" / "temporal_validation" / "temporal_validation_input_cobas6000_alt.csv"
INPUT_MANIFEST = ROOT / "data" / "processed" / "temporal_validation" / "temporal_validation_input_cobas6000_alt_manifest.json"
MODEL_DIR = ROOT / "models" / "phase3"
OUTPUT_DIR = ROOT / "results" / "temporal_validation" / "predictions"
PREDICTION_MANIFEST = OUTPUT_DIR / "temporal_prediction_manifest.json"

MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PREDICTORS = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL",
    "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD",
]
FORBIDDEN = {"LUXSMED", "outcome_primary_8.2kPa", "outcome", "label", "target"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source_manifest = json.loads(INPUT_MANIFEST.read_text(encoding="utf-8"))
    if source_manifest["n_rows"] != 4910 or source_manifest["n_unique_seqn"] != 4910:
        raise ValueError("Input manifest does not attest to the frozen 4,910-person cohort.")
    if source_manifest["only_transformation"]["variable"] != "LBXSATSI":
        raise ValueError("Input manifest does not attest that ALT is the only transformation.")
    if any(source_manifest[key] for key in ("raw_xpt_modified", "model_artifacts_modified", "cohort_membership_changed", "temporal_outcomes_used_for_bridge_or_model_parameters")):
        raise ValueError("Input manifest reports a prohibited modification or outcome use.")

    data = pd.read_csv(INPUT)
    if len(data) != 4910 or data["SEQN"].nunique() != 4910 or data["SEQN"].duplicated().any():
        raise ValueError("Temporal input does not contain exactly 4,910 unique participants.")
    if data.columns.tolist() != ["SEQN", *PREDICTORS]:
        raise ValueError("Temporal input columns are not exactly SEQN plus the frozen predictor order.")
    if FORBIDDEN & set(data.columns) or data[PREDICTORS].isna().any().any():
        raise ValueError("Temporal input contains an outcome/label or missing predictor value.")

    X = data[PREDICTORS]
    master = pd.DataFrame({"SEQN": data["SEQN"]})
    model_records = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in MODELS:
        artifact_path = MODEL_DIR / f"model_{name}_v1.joblib"
        artifact = joblib.load(artifact_path)
        if artifact["predictors"] != PREDICTORS or artifact["seed"] != 42:
            raise ValueError(f"{name}: artifact predictor registry or seed is not frozen-compatible.")
        pipeline = artifact["pipeline"]
        transformer = pipeline.named_steps["pre"].transformers_[0]
        if list(transformer[2]) != PREDICTORS:
            raise ValueError(f"{name}: embedded preprocessing order does not match the frozen registry.")

        probability = pipeline.predict_proba(X)[:, 1]
        if len(probability) != 4910 or not np.isfinite(probability).all() or ((probability < 0) | (probability > 1)).any():
            raise ValueError(f"{name}: invalid frozen-pipeline output.")
        per_model = pd.DataFrame({"SEQN": data["SEQN"], "predicted_probability": probability})
        if per_model["SEQN"].duplicated().any() or per_model.isna().any().any():
            raise ValueError(f"{name}: output identifier or probability integrity failure.")
        output_path = OUTPUT_DIR / f"temporal_predictions_{name}.csv"
        per_model.to_csv(output_path, index=False)
        master[f"{name}_probability"] = probability
        preprocessing_steps = list(transformer[1].named_steps)
        model_records.append({
            "model": name,
            "artifact": str(artifact_path.relative_to(ROOT)),
            "artifact_sha256": sha256(artifact_path),
            "best_params": artifact["best_params"],
            "preprocessing_steps": preprocessing_steps,
            "output": str(output_path.relative_to(ROOT)),
            "output_sha256": sha256(output_path),
            "n_predictions": len(probability),
            "n_unique_seqn": int(per_model["SEQN"].nunique()),
        })

    if master["SEQN"].duplicated().any() or master.isna().any().any() or not np.isfinite(master.drop(columns="SEQN").to_numpy()).all():
        raise ValueError("Master prediction table integrity failure.")
    master_path = OUTPUT_DIR / "temporal_predictions_master.csv"
    master.to_csv(master_path, index=False)
    manifest = {
        "purpose": "Frozen-model probability generation only; no outcome-based evaluation.",
        "input": str(INPUT.relative_to(ROOT)),
        "input_sha256": sha256(INPUT),
        "input_rows": len(data),
        "input_unique_seqn": int(data["SEQN"].nunique()),
        "predictor_order": PREDICTORS,
        "temporal_outcome_or_label_columns_accessed": False,
        "retraining_refitting_tuning_recalibration_or_model_selection": False,
        "thresholds_conformal_parameters_and_m4b_n0_accessed": False,
        "environment": {
            "python": platform.python_version(), "scikit_learn": sklearn.__version__,
            "xgboost": xgboost.__version__, "lightgbm": lightgbm.__version__,
        },
        "models": model_records,
        "master_output": str(master_path.relative_to(ROOT)),
        "master_output_sha256": sha256(master_path),
        "master_columns": master.columns.tolist(),
        "integrity": {
            "master_rows": len(master), "master_unique_seqn": int(master["SEQN"].nunique()),
            "all_probabilities_finite": True, "all_probabilities_in_0_1": True,
            "duplicate_seqn": False, "missing_predictions": False,
        },
    }
    PREDICTION_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
