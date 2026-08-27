"""Prepare isolated Phase 3 temporal-validation inputs; no evaluation is performed."""
from pathlib import Path
import hashlib
import json

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
TEMP = ROOT / "results" / "temporal_validation"
PRED_DIR = TEMP / "predictions"
MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
FEATURES = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
    "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD",
]
COHORT = ROOT / "data" / "processed" / "temporal_validation" / "temporal_validation_input_cobas6000_alt.csv"
LABELS = TEMP / "temporal_validation_labels_demographics.csv"
BMX = ROOT.parent / "NHANES 2021–2023 temporal validation dataset" / "BMX_L.xpt"
DEMO = ROOT.parent / "NHANES 2021–2023 temporal validation dataset" / "DEMO_L.xpt"
REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"
PLATT_DIR = ROOT / "results" / "calibration"
CONFORMAL = ROOT / "results" / "uncertainty" / "conformal_thresholds_by_model.csv"
M4B_FINAL = ROOT / "results" / "tables" / "m4b_prespecified_n0_final_results.csv"
M4B_QUANTILES = ROOT / "results" / "tables" / "m4b_lightgbm_failure_analysis.csv"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assert_ids(frame, name):
    if len(frame) != 4910:
        raise RuntimeError(f"{name}: expected 4910 rows, found {len(frame)}")
    if frame["SEQN"].isna().any() or frame["SEQN"].duplicated().any() or frame["SEQN"].nunique() != 4910:
        raise RuntimeError(f"{name}: SEQN integrity failure")


def relative(path):
    return str(Path(path).relative_to(ROOT))


def main():
    fairness_out = TEMP / "temporal_validation_fairness_demographics.csv"
    fairness_manifest = TEMP / "temporal_validation_fairness_demographics_manifest.json"
    fairness_audit = TEMP / "TEMPORAL_FAIRNESS_DEMOGRAPHICS_AUDIT.md"
    conformal_manifest = TEMP / "temporal_conformal_refit_prediction_manifest.json"
    conformal_audit = TEMP / "TEMPORAL_CONFORMAL_INPUT_AUDIT.md"
    prediction_out = {name: TEMP / f"temporal_conformal_refit_predictions_{name}.csv" for name in MODELS}
    outputs = [fairness_out, fairness_manifest, fairness_audit, conformal_manifest, conformal_audit, *prediction_out.values()]
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise RuntimeError("Refusing to overwrite existing temporal-validation outputs: " + ", ".join(existing))

    frozen_watch = [COHORT, LABELS, *PRED_DIR.glob("temporal_predictions_*.csv"), *REFIT_DIR.glob("model_*_proper_train_refit.joblib"), CONFORMAL, M4B_FINAL, M4B_QUANTILES]
    hashes_before = {str(path): sha256(path) for path in frozen_watch}

    labels = pd.read_csv(LABELS, usecols=["SEQN"])
    cohort = pd.read_csv(COHORT, usecols=["SEQN", *FEATURES])
    assert_ids(labels, "temporal labels anchor")
    assert_ids(cohort, "temporal frozen predictor cohort")
    labels["SEQN"] = labels["SEQN"].astype("int64")
    cohort["SEQN"] = cohort["SEQN"].astype("int64")
    if set(labels["SEQN"]) != set(cohort["SEQN"]):
        raise RuntimeError("Labels anchor and frozen predictor cohort have non-identical SEQNs")

    bmx = pd.read_sas(BMX, format="xport", encoding="utf-8")[["SEQN", "BMXBMI"]]
    demo = pd.read_sas(DEMO, format="xport", encoding="utf-8")[["SEQN", "RIDAGEYR", "RIAGENDR"]]
    for source, name in ((bmx, "BMX_L"), (demo, "DEMO_L")):
        if source["SEQN"].isna().any() or source["SEQN"].duplicated().any():
            raise RuntimeError(f"{name}: duplicate or missing source SEQN")
        source["SEQN"] = source["SEQN"].astype("int64")
    fairness = labels.merge(bmx, on="SEQN", how="left", validate="one_to_one").merge(demo, on="SEQN", how="left", validate="one_to_one")
    fairness = fairness[["SEQN", "BMXBMI", "RIDAGEYR", "RIAGENDR"]]
    assert_ids(fairness, "fairness demographics output")
    if set(fairness["SEQN"]) != set(labels["SEQN"]):
        raise RuntimeError("Fairness output SEQNs differ from temporal labels anchor")
    missing = {column: int(fairness[column].isna().sum()) for column in ["BMXBMI", "RIDAGEYR", "RIAGENDR"]}
    if any(missing.values()):
        raise RuntimeError(f"Missing frozen-cohort fairness demographics: {missing}")
    fairness.to_csv(fairness_out, index=False)

    fairness_info = {
        "purpose": "Temporal fairness-demographic attachment only; no evaluation performed.",
        "source_files_used": {"anchor": relative(LABELS), "BMX_L": str(BMX.relative_to(ROOT.parent)), "DEMO_L": str(DEMO.relative_to(ROOT.parent))},
        "source_sha256": {"anchor": sha256(LABELS), "BMX_L": sha256(BMX), "DEMO_L": sha256(DEMO)},
        "output_file": relative(fairness_out), "output_sha256": sha256(fairness_out),
        "columns": list(fairness.columns),
        "validation": {"rows": 4910, "unique_seqn": 4910, "duplicate_seqn": 0, "missing_seqn": 0, "exact_seqn_match_to_anchor": True, "matched_from_BMX_L": 4910, "matched_from_DEMO_L": 4910, "unmatched_seqn": [], "missingness": missing},
        "integrity": {"cohort_rebuilt_or_redefined": False, "predictors_modified": False, "outcomes_modified": False, "models_modified": False, "evaluation_performed": False},
    }
    fairness_manifest.write_text(json.dumps(fairness_info, indent=2) + "\n", encoding="utf-8")
    fairness_audit.write_text(
        "# Temporal fairness demographics audit\n\n"
        "This preparation attached original NHANES variables only; no evaluation was performed.\n\n"
        "- Source files: `BMX_L.xpt` (`SEQN`, `BMXBMI`) and `DEMO_L.xpt` (`SEQN`, `RIDAGEYR`, `RIAGENDR`).\n"
        "- Cohort anchor: existing `temporal_validation_labels_demographics.csv`.\n"
        "- Rows / unique SEQNs / duplicate SEQNs / missing SEQNs: 4910 / 4910 / 0 / 0.\n"
        "- Matched from BMX_L / DEMO_L: 4910 / 4910; unmatched: none.\n"
        f"- Missing BMXBMI / RIDAGEYR / RIAGENDR: {missing['BMXBMI']} / {missing['RIDAGEYR']} / {missing['RIAGENDR']}.\n"
        "- The 4,910-person cohort, predictors, outcomes, models, and existing prediction files were not changed.\n",
        encoding="utf-8",
    )

    threshold_frame = pd.read_csv(CONFORMAL).set_index("model")
    m4b_final = pd.read_csv(M4B_FINAL).set_index("model")
    m4b_quantiles = pd.read_csv(M4B_QUANTILES).set_index("model")
    records, platt_parameters = [], {}
    for name in MODELS:
        artifact = REFIT_DIR / f"model_{name}_proper_train_refit.joblib"
        frozen = joblib.load(artifact)
        if frozen["predictors"] != FEATURES or frozen["proper_train_n"] != 4005:
            raise RuntimeError(f"{name}: Phase 6 artifact provenance validation failed")
        probabilities = frozen["pipeline"].predict_proba(cohort[FEATURES])[:, 1]
        if len(probabilities) != 4910 or not np.isfinite(probabilities).all() or ((probabilities < 0) | (probabilities > 1)).any():
            raise RuntimeError(f"{name}: invalid Phase 6 conformal-refit predictions")
        platt = pd.read_csv(PLATT_DIR / f"recalibrated_oof_predictions_{name}.csv", usecols=["platt_intercept", "platt_slope"])
        if platt["platt_intercept"].nunique() != 1 or platt["platt_slope"].nunique() != 1:
            raise RuntimeError(f"{name}: Platt parameters are not frozen constants")
        intercept, slope = float(platt["platt_intercept"].iloc[0]), float(platt["platt_slope"].iloc[0])
        clipped = np.clip(probabilities, 1e-7, 1 - 1e-7)
        platt_probability = 1.0 / (1.0 + np.exp(-(slope * np.log(clipped / (1.0 - clipped)) + intercept)))
        output = pd.DataFrame({"SEQN": cohort["SEQN"], "conformal_refit_probability": probabilities, "platt_recalibrated_probability": platt_probability})
        assert_ids(output, f"{name} conformal refit prediction output")
        if output[["conformal_refit_probability", "platt_recalibrated_probability"]].isna().any().any() or not np.isfinite(output[["conformal_refit_probability", "platt_recalibrated_probability"]].to_numpy()).all():
            raise RuntimeError(f"{name}: missing or non-finite prediction output")
        output.to_csv(prediction_out[name], index=False)
        platt_parameters[name] = {"intercept": intercept, "slope": slope, "source": relative(PLATT_DIR / f"recalibrated_oof_predictions_{name}.csv"), "sha256": sha256(PLATT_DIR / f"recalibrated_oof_predictions_{name}.csv")}
        records.append({"model": name, "prediction_file": relative(prediction_out[name]), "prediction_sha256": sha256(prediction_out[name]), "n_predictions": 4910, "unique_seqn": 4910, "missing_predictions": False, "finite_predictions": True, "probability_range_0_1": True, "artifact": relative(artifact), "artifact_sha256": sha256(artifact), "artifact_registry_sha256": None, "frozen_global_conformal_threshold": float(threshold_frame.loc[name, "threshold"]), "m4b_n0": 0, "m4b_q_global": float(m4b_quantiles.loc[name, "q_global_cal"]), "m4b_q_obese": float(m4b_quantiles.loc[name, "q_obese_cal"]), "m4b_q_age60": float(m4b_quantiles.loc[name, "q_age60_cal"]), "m4b_q_joint": float(m4b_quantiles.loc[name, "q_joint_cal"]), "m4b_q_m4b_n0": float(m4b_final.loc[name, "q_m4b_cal"])})

    hashes_after = {str(path): sha256(path) for path in frozen_watch}
    if hashes_before != hashes_after:
        raise RuntimeError("A frozen cohort, model, primary artifact, or existing temporal prediction changed")
    conformal_info = {
        "purpose": "Frozen Phase 6 conformal-refit probability preparation only; no coverage or other evaluation performed.",
        "frozen_temporal_predictor_input": {"path": relative(COHORT), "sha256": sha256(COHORT), "rows": 4910, "unique_seqn": 4910},
        "source_artifacts": {"conformal_thresholds": {"path": relative(CONFORMAL), "sha256": sha256(CONFORMAL)}, "m4b_final_N0_0": {"path": relative(M4B_FINAL), "sha256": sha256(M4B_FINAL)}, "m4b_quantiles": {"path": relative(M4B_QUANTILES), "sha256": sha256(M4B_QUANTILES)}},
        "platt_parameters": platt_parameters, "models": records,
        "integrity": {"all_outputs_exactly_match_4910_anchor_seqns": True, "no_temporal_outcomes_or_demographics_used_for_parameters": True, "retraining_refitting_recalibration_tuning_or_quantile_recomputation": False, "N0": 0, "frozen_inputs_unchanged_before_after": True, "evaluation_performed": False},
    }
    conformal_manifest.write_text(json.dumps(conformal_info, indent=2) + "\n", encoding="utf-8")
    lines = ["# Temporal frozen conformal input audit", "", "No Phase 3 evaluation was performed.", "", "## Frozen sources", "", f"- Phase 6 refit artifacts: `{relative(REFIT_DIR)}/model_<model>_proper_train_refit.joblib`.", f"- Platt constants: `{relative(PLATT_DIR)}/recalibrated_oof_predictions_<model>.csv`.", f"- Global conformal thresholds: `{relative(CONFORMAL)}`.", f"- Final N0=0 M4b configuration: `{relative(M4B_FINAL)}`; group/joint quantiles: `{relative(M4B_QUANTILES)}`.", "", "## Generated conformal inputs", ""]
    for record in records:
        lines.append(f"- `{record['model']}`: 4,910 predictions, 4,910 unique SEQNs, no missing/dropped values, finite probabilities in [0,1]; artifact SHA-256 `{record['artifact_sha256']}`.")
    lines.extend(["", "The exact frozen Phase 6 pipeline preprocessing was applied through the loaded refit artifacts. No training, refitting, parameter fitting, quantile recomputation, outcome use, demographic use, threshold tuning, N0 selection, or coverage evaluation occurred. Existing temporal prediction files and all frozen sources had identical before/after SHA-256 hashes."])
    conformal_audit.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Preparation complete; created:")
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
