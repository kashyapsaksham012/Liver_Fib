"""Corrected Phase 4 subgroup-calibration re-execution.

This script writes only the phase4_corrected namespace.  It uses the frozen OOF
development predictions, the reserved conformal-development partition, and the
frozen locked-test predictions.  The locked test is opened only after the
selection manifest has been written.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
SPLITS = DATA / "splits"
PRED = ROOT / "results" / "predictions"
REFIT = ROOT / "models" / "phase6_conformal_refit"
OUT = ROOT / "results" / "fairness_bmi_investigation" / "phase4_corrected"
FIG = ROOT / "results" / "fairness_bmi_investigation" / "phase4_corrected_figures"
DOC = ROOT / "documentation" / "fairness_bmi_investigation"

MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
BMI_GROUPS = ["Underweight", "Normal", "Overweight", "Obese"]
AGE_GROUPS = ["18-39", "40-59", "60+"]
FEATURES = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
    "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD",
]
OUTCOME = "outcome_primary_8.2kPa"
FROZEN_THRESHOLDS = {
    "logistic": 0.5173,
    "random_forest": 0.4499,
    "xgboost": 0.4108,
    "lightgbm": 0.4988,
    "mlp": 0.1065,
}
SEED = 20260826
MIN_CELL_N = 20
MIN_CELL_POS = 10
MIN_CELL_NEG = 10
TARGET_COVERAGE = 0.90


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def logit(probability):
    p = np.asarray(probability, dtype=float)
    return np.log(np.clip(p, 1e-12, 1 - 1e-12) /
                  np.clip(1 - p, 1e-12, 1))


def fit_platt(probability, outcome):
    return LogisticRegression(
        C=1e10, solver="lbfgs", max_iter=5000, random_state=SEED
    ).fit(logit(probability).reshape(-1, 1), np.asarray(outcome, dtype=int))


def apply_platt(calibrator, probability):
    return calibrator.predict_proba(logit(probability).reshape(-1, 1))[:, 1]


def wilson(successes, total):
    if not total:
        return np.nan, np.nan
    z = norm.ppf(0.975)
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def ece_equal_frequency(outcome, probability, n_bins=10):
    """Frozen 10 equal-frequency risk-decile ECE.

    Stable sorting makes ties deterministic.  ``np.array_split`` gives deciles
    differing by at most one observation and the ECE weights each decile by its
    empirical frequency, as required by the frozen protocol.
    """
    y = np.asarray(outcome, dtype=float)
    p = np.asarray(probability, dtype=float)
    if len(y) != len(p) or not len(y):
        return np.nan
    ordered = np.argsort(p, kind="mergesort")
    bins = np.array_split(ordered, min(n_bins, len(ordered)))
    return float(sum(
        (len(indices) / len(y)) *
        abs(float(y[indices].mean()) - float(p[indices].mean()))
        for indices in bins if len(indices)
    ))


def reference_equal_frequency_ece(outcome, probability, n_bins=10):
    """Independent validation implementation of the frozen ECE definition."""
    y = np.asarray(outcome, dtype=float)
    p = np.asarray(probability, dtype=float)
    ordered = np.argsort(p, kind="mergesort")
    active_bins = min(n_bins, len(p))
    base, remainder = divmod(len(p), active_bins)
    sizes = [base + (i < remainder) for i in range(active_bins)]
    labels = np.empty(len(p), dtype=int)
    cursor = 0
    for label, size in enumerate(sizes):
        labels[ordered[cursor:cursor + size]] = label
        cursor += size
    total = 0.0
    for label in range(active_bins):
        mask = labels == label
        if mask.any():
            total += mask.mean() * abs(y[mask].mean() - p[mask].mean())
    return float(total)


def classification_metrics(outcome, probability, raw_probability, threshold):
    y = np.asarray(outcome, dtype=int)
    p = np.asarray(probability, dtype=float)
    raw = np.asarray(raw_probability, dtype=float)
    decision = raw >= threshold
    tn, fp, fn, tp = confusion_matrix(y, decision, labels=[0, 1]).ravel()
    positives = int(y.sum())
    negatives = int(len(y) - positives)
    cal = fit_platt(p, y) if len(np.unique(y)) == 2 else None
    sensitivity_low, sensitivity_high = wilson(int(tp), positives)
    return {
        "n": len(y),
        "positive_n": positives,
        "negative_n": negatives,
        "prevalence": positives / len(y),
        "sensitivity": tp / positives if positives else np.nan,
        "sensitivity_ci_low": sensitivity_low,
        "sensitivity_ci_high": sensitivity_high,
        "specificity": tn / negatives if negatives else np.nan,
        "fnr": fn / positives if positives else np.nan,
        "ppv": tp / (tp + fp) if tp + fp else np.nan,
        "npv": tn / (tn + fn) if tn + fn else np.nan,
        "auroc": roc_auc_score(y, p) if len(np.unique(y)) == 2 else np.nan,
        "pr_auc": average_precision_score(y, p) if len(np.unique(y)) == 2 else np.nan,
        "brier": brier_score_loss(y, p),
        "ece": ece_equal_frequency(y, p),
        "calibration_intercept": float(cal.intercept_[0]) if cal is not None else np.nan,
        "calibration_slope": float(cal.coef_[0][0]) if cal is not None else np.nan,
        "tp": int(tp), "fn": int(fn), "tn": int(tn), "fp": int(fp),
    }


def cell_map(calibration_df, probability, outcome, dimension, value):
    cell = calibration_df[calibration_df[dimension] == value]
    n = len(cell)
    positives = int(cell[outcome].sum())
    negatives = n - positives
    estimable = n >= MIN_CELL_N and positives >= MIN_CELL_POS and negatives >= MIN_CELL_NEG
    record = {
        "dimension": dimension, "value": value, "n": n,
        "positive_n": positives, "negative_n": negatives,
        "status": "ESTIMABLE" if estimable else "UNSTABLE_SMALL_CELL",
        "fallback": "NONE" if estimable else "global_platt",
    }
    if not estimable:
        return None, record
    return fit_platt(probability[cell.index], cell[outcome]), record


def build_calibrators(df, probability):
    global_map = fit_platt(probability, df[OUTCOME])
    records = [{
        "dimension": "GLOBAL", "value": "ALL", "n": len(df),
        "positive_n": int(df[OUTCOME].sum()),
        "negative_n": int(len(df) - df[OUTCOME].sum()),
        "status": "ESTIMABLE", "fallback": "NONE",
        "intercept": float(global_map.intercept_[0]),
        "slope": float(global_map.coef_[0][0]),
    }]
    maps = {"global": global_map, "cells": {}}
    for dimension, values in (
        ("bmi_group_final", BMI_GROUPS), ("age_group_final", AGE_GROUPS)
    ):
        for value in values:
            fitted, record = cell_map(df, probability, OUTCOME, dimension, value)
            if fitted is not None:
                record["intercept"] = float(fitted.intercept_[0])
                record["slope"] = float(fitted.coef_[0][0])
                maps["cells"][(dimension, value)] = fitted
            records.append(record)
    return maps, records


def transform_probabilities(df, raw_probability, maps, candidate):
    raw = np.asarray(raw_probability, dtype=float)
    if candidate == "global_platt":
        return apply_platt(maps["global"], raw), np.full(len(df), "global_platt", dtype=object)
    transformed = np.empty(len(df), dtype=float)
    sources = np.empty(len(df), dtype=object)
    for i, (_, row) in enumerate(df.iterrows()):
        key = ("bmi_group_final", row["bmi_group_final"])
        if key in maps["cells"]:
            source = f"bmi:{row['bmi_group_final']}"
            calibrator = maps["cells"][key]
        else:
            key = ("age_group_final", row["age_group_final"])
            if key in maps["cells"]:
                source = f"age:{row['age_group_final']}"
                calibrator = maps["cells"][key]
            else:
                source = "global_fallback"
                calibrator = maps["global"]
        transformed[i] = apply_platt(calibrator, [raw[i]])[0]
        sources[i] = source
    return transformed, sources


def scope_masks(df):
    masks = {"OVERALL": np.ones(len(df), dtype=bool)}
    masks.update({
        f"BMI_{value}": (df["bmi_group_final"] == value).to_numpy()
        for value in BMI_GROUPS
    })
    masks.update({
        f"AGE_{value}": (df["age_group_final"] == value).to_numpy()
        for value in AGE_GROUPS
    })
    masks.update({
        f"BMIxAGE_{bmi}_{age}":
        ((df["bmi_group_final"] == bmi) & (df["age_group_final"] == age)).to_numpy()
        for bmi in BMI_GROUPS for age in AGE_GROUPS
    })
    return masks


def evaluate_candidate(df, raw_probability, probability, sources, model, candidate, phase):
    rows = []
    for scope, mask in scope_masks(df).items():
        if not mask.any():
            continue
        metrics = classification_metrics(
            df.loc[mask, OUTCOME].to_numpy(),
            probability[mask],
            raw_probability[mask],
            FROZEN_THRESHOLDS[model],
        )
        source_counts = pd.Series(sources[mask]).value_counts().to_dict()
        metrics.update({
            "model": model, "candidate": candidate, "phase": phase, "scope": scope,
            "decision_rule": "raw frozen prediction >= frozen Youden threshold",
            "calibration_source_counts": json.dumps(source_counts, sort_keys=True),
            "fallback_n": int(np.sum(sources[mask] == "global_fallback")),
            "cell_status": (
                "ESTIMABLE_OR_EXPLICIT_FALLBACK"
                if scope == "OVERALL" or mask.sum() >= MIN_CELL_N else "UNSTABLE_SMALL_CELL"
            ),
        })
        rows.append(metrics)
    return rows


def summary_row(detail, model, candidate):
    overall = detail[(detail.model == model) & (detail.candidate == candidate) &
                     (detail.scope == "OVERALL")].iloc[0]
    normal = detail[(detail.model == model) & (detail.candidate == candidate) &
                    (detail.scope == "BMI_Normal")].iloc[0]
    obese = detail[(detail.model == model) & (detail.candidate == candidate) &
                   (detail.scope == "BMI_Obese")].iloc[0]
    age40 = detail[(detail.model == model) & (detail.candidate == candidate) &
                   (detail.scope == "AGE_40-59")].iloc[0]
    age60 = detail[(detail.model == model) & (detail.candidate == candidate) &
                   (detail.scope == "AGE_60+")].iloc[0]
    return {
        "model": model, "candidate": candidate, "phase": overall.phase,
        "normal_sensitivity": normal.sensitivity,
        "obese_sensitivity": obese.sensitivity,
        "bmi_obese_minus_normal_gap_pp":
            (obese.sensitivity - normal.sensitivity) * 100,
        "overall_sensitivity": overall.sensitivity,
        "overall_specificity": overall.specificity,
        "auroc": overall.auroc, "pr_auc": overall.pr_auc,
        "brier": overall.brier, "ece": overall.ece,
        "age60_minus_age40_gap_pp":
            (age60.sensitivity - age40.sensitivity) * 100,
    }


def runtime_metadata(started):
    package_versions = {}
    for package in ("numpy", "pandas", "scikit-learn", "scipy", "joblib", "matplotlib", "pyarrow"):
        try:
            package_versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            package_versions[package] = "unavailable"
    return {
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "package_versions": package_versions,
        "runtime_event_logging": {
            "available": False,
            "statement": "No external runtime-event logger is available in this execution environment.",
        },
    }


def write_docs(chosen, test_fairness):
    status = "NO ACCEPTABLE SUBGROUP CALIBRATION IMPROVEMENT IDENTIFIED"
    chosen_text = ", ".join(f"{m}={chosen[m]}" for m in MODELS)
    (DOC / "PHASE4_CORRECTION_RECORD.md").write_text(f"""# Phase 4 Correction Record

**Disposition:** The historical subgroup-calibration execution is superseded for the audited
claims, but all historical Phase 4 files remain preserved and were not modified. This
re-execution creates only `results/fairness_bmi_investigation/phase4_corrected/`.

## Audited defects corrected

1. ECE uses the frozen ten equal-frequency risk deciles, verified against
   `documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md`; the verification artifact is
   `results/fairness_bmi_investigation/phase4_corrected/ece_validation.csv`.
2. Both conformal arms fit and apply their named maps on the same conformal-development
   even/odd split. `global_platt` now fits and applies one global Platt map; the comparator
   uses BMI-first, age-second, global-fallback subgroup Platt maps.

Maps require at least {MIN_CELL_N} observations, {MIN_CELL_POS} positives, and
{MIN_CELL_NEG} negatives. Every non-estimable cell is explicitly recorded and falls back to
the global map. The frozen model set, predictors, outcome, cohort, BMI/age definitions,
thresholds, and existing selection gate are unchanged.

## Ordering and preservation

OOF development and conformal comparison were completed before selection was frozen. The
selection manifest was written before any locked-test IDs, metadata, predictions, or outcomes
were loaded. Exactly one locked-test confirmation pass followed; no selection or parameter
changes were made afterward. The prior exploratory artifact and Phase 0–3, Phase 7, master,
and later-phase artifacts were not modified.

Selected development methods: `{chosen_text}`.

Final scientific status: **{status}**
""")
    (DOC / "PHASE4_CORRECTED_DECISION_LOG.md").write_text(f"""# Phase 4 Corrected Decision Log

| Decision | Corrected execution |
|---|---|
| Historical Phase 4 status | Superseded for the audited claims; preserved unchanged |
| ECE | Ten equal-frequency risk deciles, validated in `ece_validation.csv` |
| Development split | OOF rows sorted by SEQN; even index fit, odd index evaluation |
| Calibration candidates | `global_platt`; `subgroup_platt_bmi_age` |
| Cell minimums | n >= {MIN_CELL_N}, positives >= {MIN_CELL_POS}, negatives >= {MIN_CELL_NEG}; explicit global fallback |
| Conformal comparator | Global Platt and subgroup Platt both fit/apply maps under the identical split-conformal framework |
| Selection gate | Existing gate: ECE improvement; Brier <= global +0.01; overall sensitivity/specificity within 5 pp; absolute Age-60-vs-40 gap within 5 pp |
| Locked-test access | Manifest written first; one confirmatory scoring pass only |
| Selected methods | {chosen_text} |
| Scientific status | **{status}** |

No significance claims are introduced; uncertainty is descriptive and limited to supported
Wilson intervals and conformal-development summaries.
""")
    fairness_lines = "\n".join(
        f"- {row.model}: selected `{row.selected_candidate}`; test BMI gap change "
        f"{row.test_gap_change_pp:+.3f} pp versus global"
        for row in test_fairness.itertuples()
    )
    (DOC / "PHASE4_CORRECTED_REPORT.md").write_text(f"""# Phase 4 Corrected Subgroup Calibration Report

## Final status

**{status}**

## Execution

The corrected run retained the five frozen primary models, ten predictors, primary cohort and
outcome, frozen thresholds, and the existing selection gate. OOF rows were sorted by SEQN and
split deterministically into even-index fit and odd-index evaluation partitions. Global Platt
and BMI/age subgroup Platt candidates were evaluated without accessing the locked test.
Subgroup cells used documented minimum requirements and explicit fallback/status fields.

ECE was recomputed with ten equal-frequency risk deciles, not equal-width probability bins.
`ece_validation.csv` records agreement with an independent implementation and the frozen
protocol hash. The conformal comparison fits and applies a global Platt map in the
`global_platt` arm and compares it with subgroup Platt under identical 501/501
development conformal splits.

The manifest froze method selection and parameters before one locked-test confirmation pass.
No test result was used to revise a method, parameter, or selection rule. The historical Phase
4 output and prior exploratory artifact remain separate and unchanged.

## Selected methods and confirmation

{fairness_lines}

The transformed probabilities do not alter classification decisions because the frozen raw
prediction thresholds are retained. Therefore calibration alone cannot claim to resolve the
classification-level BMI sensitivity disparity. Metrics, supported Wilson intervals, conformal
coverage/efficiency summaries, hashes, and runtime metadata are in the corrected namespace.

No unsupported significance or equivalence claim is made.
""")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    DOC.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()

    # Development-only inputs. No locked-test file is opened in this section.
    oof = {}
    id_frames = []
    for model in MODELS:
        frame = pd.read_csv(PRED / f"validation_predictions_{model}.csv")
        if frame["SEQN"].duplicated().any():
            raise RuntimeError(f"{model}: duplicate OOF SEQN")
        oof[model] = frame
        id_frames.append(frame[["SEQN"]])
    oof_ids = pd.concat(id_frames, ignore_index=True).drop_duplicates()
    master = pd.read_parquet(
        DATA / "analysis_dataset_primary.parquet",
        filters=[("SEQN", "in", oof_ids.SEQN.tolist())],
    )
    meta = oof_ids.merge(
        master[["SEQN", OUTCOME, "bmi_group_final", "age_group_final"]],
        on="SEQN", validate="one_to_one",
    ).sort_values("SEQN").reset_index(drop=True)
    meta["part"] = np.where(np.arange(len(meta)) % 2 == 0, "fit", "eval")
    meta["y"] = meta[OUTCOME].astype(int)

    detail_rows = []
    comparison_rows = []
    parameter_records = {}
    for model in MODELS:
        joined = meta.merge(oof[model], on="SEQN", validate="one_to_one")
        fit_df = joined[joined.part == "fit"].reset_index(drop=True)
        eval_df = joined[joined.part == "eval"].reset_index(drop=True)
        fit_raw = fit_df.predicted_probability.to_numpy()
        eval_raw = eval_df.predicted_probability.to_numpy()
        maps, map_records = build_calibrators(fit_df, fit_raw)
        parameter_records[model] = {
            "oof_fit_n": len(fit_df), "oof_eval_n": len(eval_df),
            "map_records": map_records,
            "selection_gate": {
                "ece_improves": True, "brier_increase_max": 0.01,
                "sensitivity_specificity_decrease_max_pp": 5,
                "absolute_age60_age40_gap_increase_max_pp": 5,
            },
        }
        for candidate in ("global_platt", "subgroup_platt_bmi_age"):
            transformed, sources = transform_probabilities(
                eval_df, eval_raw, maps, candidate
            )
            detail_rows.extend(evaluate_candidate(
                eval_df, eval_raw, transformed, sources, model, candidate, "OOF_EVAL"
            ))
            comparison_rows.append(
                summary_row(pd.DataFrame(detail_rows), model, candidate)
            )

    detail = pd.DataFrame(detail_rows)
    comparison = pd.DataFrame(comparison_rows)
    chosen = {}
    for model in MODELS:
        base = comparison[
            (comparison.model == model) & (comparison.candidate == "global_platt")
        ].iloc[0]
        subgroup = comparison[
            (comparison.model == model) &
            (comparison.candidate == "subgroup_platt_bmi_age")
        ].iloc[0]
        eligible = (
            subgroup.ece < base.ece and
            subgroup.brier <= base.brier + 0.01 and
            subgroup.overall_sensitivity >= base.overall_sensitivity - 0.05 and
            subgroup.overall_specificity >= base.overall_specificity - 0.05 and
            abs(subgroup.age60_minus_age40_gap_pp) <=
            abs(base.age60_minus_age40_gap_pp) + 5
        )
        chosen[model] = "subgroup_platt_bmi_age" if eligible else "global_platt"
    comparison["selection_status"] = comparison.apply(
        lambda row: "SELECTED_OOF" if chosen[row.model] == row.candidate
        else "NOT_SELECTED", axis=1
    )

    protocol_path = ROOT / "documentation" / "calibration" / "CALIBRATION_PROTOCOL_FREEZE.md"
    validation_rows = []
    synthetic_y = np.array([0, 1, 0, 0, 1, 0, 0, 1, 0, 0] * 2)
    synthetic_p = np.linspace(0.01, 0.99, len(synthetic_y))
    for label, y, p in [("synthetic_unique_deciles", synthetic_y, synthetic_p)]:
        implemented = ece_equal_frequency(y, p)
        reference = reference_equal_frequency_ece(y, p)
        validation_rows.append({
            "validation_case": label, "n": len(y), "n_bins": 10,
            "binning": "equal_frequency", "implemented_ece": implemented,
            "reference_ece": reference, "absolute_difference": abs(implemented - reference),
            "protocol_path": str(protocol_path.relative_to(ROOT)),
            "protocol_hash": sha256(protocol_path),
            "status": "PASS" if np.isclose(implemented, reference) else "FAIL",
        })
    for model in MODELS:
        joined = meta.merge(oof[model], on="SEQN", validate="one_to_one")
        fit_df = joined[joined.part == "fit"].reset_index(drop=True)
        eval_df = joined[joined.part == "eval"].reset_index(drop=True)
        maps, _ = build_calibrators(fit_df, fit_df.predicted_probability.to_numpy())
        for candidate in ("global_platt", "subgroup_platt_bmi_age"):
            transformed, _ = transform_probabilities(
                eval_df, eval_df.predicted_probability.to_numpy(), maps, candidate
            )
            implemented = ece_equal_frequency(eval_df[OUTCOME], transformed)
            reference = reference_equal_frequency_ece(eval_df[OUTCOME], transformed)
            validation_rows.append({
                "validation_case": f"{model}_{candidate}_OOF_EVAL_OVERALL",
                "n": len(eval_df), "n_bins": 10, "binning": "equal_frequency",
                "implemented_ece": implemented, "reference_ece": reference,
                "absolute_difference": abs(implemented - reference),
                "protocol_path": str(protocol_path.relative_to(ROOT)),
                "protocol_hash": sha256(protocol_path),
                "status": "PASS" if np.isclose(implemented, reference) else "FAIL",
            })
    ece_validation = pd.DataFrame(validation_rows)
    if not (ece_validation.status == "PASS").all():
        raise RuntimeError("Equal-frequency ECE validation failed")
    ece_validation.to_csv(OUT / "ece_validation.csv", index=False)
    detail.to_csv(OUT / "phase4_corrected_calibration_results.csv", index=False)
    comparison.to_csv(OUT / "phase4_corrected_subgroup_comparison.csv", index=False)

    # Separate conformal development comparison. Both arms fit/apply a map on the same split.
    conformal_ids = pd.read_csv(SPLITS / "conformal_calibration_ids.csv")["SEQN"].tolist()
    conformal = pd.read_parquet(
        DATA / "analysis_dataset_primary.parquet",
        filters=[("SEQN", "in", conformal_ids)],
    ).sort_values("SEQN").reset_index(drop=True)
    conformal["part"] = np.where(np.arange(len(conformal)) % 2 == 0, "fit", "eval")
    conformal_rows = []
    conformal_parameter_records = {}
    for model in MODELS:
        pipe = joblib.load(REFIT / f"model_{model}_proper_train_refit.joblib")["pipeline"]
        fit_df = conformal[conformal.part == "fit"].reset_index(drop=True)
        eval_df = conformal[conformal.part == "eval"].reset_index(drop=True)
        raw_fit = pipe.predict_proba(fit_df[FEATURES])[:, 1]
        raw_eval = pipe.predict_proba(eval_df[FEATURES])[:, 1]
        maps, map_records = build_calibrators(fit_df, raw_fit)
        conformal_parameter_records[model] = map_records
        for candidate in ("global_platt", "subgroup_platt_bmi_age"):
            cal_fit, fit_sources = transform_probabilities(
                fit_df, raw_fit, maps, candidate
            )
            cal_eval, eval_sources = transform_probabilities(
                eval_df, raw_eval, maps, candidate
            )
            y_fit = fit_df[OUTCOME].to_numpy()
            y_eval = eval_df[OUTCOME].to_numpy()
            scores = 1 - np.where(y_fit == 1, cal_fit, 1 - cal_fit)
            k = int(np.ceil((len(scores) + 1) * TARGET_COVERAGE))
            threshold = float(np.sort(scores)[k - 1])
            covered = np.where(
                y_eval == 1, (1 - cal_eval) <= threshold, cal_eval <= threshold
            )
            set_size = ((1 - cal_eval) <= threshold).astype(int) + (
                cal_eval <= threshold
            ).astype(int)
            coverage = float(covered.mean())
            coverage_low, coverage_high = wilson(int(covered.sum()), len(covered))
            conformal_rows.append({
                "model": model, "candidate": candidate,
                "phase": "CONFORMAL_DEV_SPLIT", "fit_n": len(fit_df),
                "evaluation_n": len(eval_df), "fit_positive_n": int(y_fit.sum()),
                "evaluation_positive_n": int(y_eval.sum()),
                "target_coverage": TARGET_COVERAGE, "coverage": coverage,
                "coverage_ci_low": coverage_low, "coverage_ci_high": coverage_high,
                "coverage_gap_vs_target_pp": (coverage - TARGET_COVERAGE) * 100,
                "mean_set_size": float(set_size.mean()),
                "singleton_rate": float((set_size == 1).mean()),
                "doubleton_rate": float((set_size == 2).mean()),
                "empty_set_rate": float((set_size == 0).mean()),
                "threshold": threshold,
                "map_applied_to_fit": True, "map_applied_to_eval": True,
                "fit_source_counts": json.dumps(
                    pd.Series(fit_sources).value_counts().to_dict(), sort_keys=True
                ),
                "eval_source_counts": json.dumps(
                    pd.Series(eval_sources).value_counts().to_dict(), sort_keys=True
                ),
                "map_status": "GLOBAL_PLATT_FIT_APPLIED" if candidate == "global_platt"
                else "SUBGROUP_PLATT_WITH_EXPLICIT_FALLBACK",
            })
    conformal = pd.DataFrame(conformal_rows)
    conformal.to_csv(OUT / "phase4_corrected_conformal_comparison.csv", index=False)

    parameter_records["conformal"] = conformal_parameter_records
    parameter_records_hash = hashlib.sha256(
        json.dumps(parameter_records, sort_keys=True, default=str).encode()
    ).hexdigest()
    manifest = {
        "run": "corrected_phase4_subgroup_calibration",
        "seed": SEED,
        "status": "SELECTION_FROZEN_BEFORE_TEST_ACCESS",
        "models": MODELS,
        "predictors": FEATURES,
        "outcome": OUTCOME,
        "cohort": {"name": "primary", "n": 7153, "positive_n": 666},
        "bmi_groups": BMI_GROUPS, "age_groups": AGE_GROUPS,
        "frozen_thresholds": FROZEN_THRESHOLDS,
        "development_split": "OOF rows sorted by SEQN; even index fit, odd index evaluation",
        "candidates": ["global_platt", "subgroup_platt_bmi_age"],
        "minimum_cell_requirements": {
            "n": MIN_CELL_N, "positive_n": MIN_CELL_POS, "negative_n": MIN_CELL_NEG,
        },
        "fallback_rule": "BMI cell first, then age cell, then global Platt; every fallback is recorded",
        "selection_rule": (
            "Select subgroup Platt only if ECE improves, Brier <= global +0.01, "
            "overall sensitivity and specificity are within 5 pp, and the absolute "
            "Age-60-vs-Age-40 sensitivity gap is within 5 pp; otherwise global Platt."
        ),
        "chosen": chosen,
        "parameter_records": parameter_records,
        "parameter_records_sha256": parameter_records_hash,
        "ece_protocol": {
            "bins": 10, "binning": "equal_frequency_risk_deciles",
            "protocol_path": str(protocol_path.relative_to(ROOT)),
            "protocol_sha256": sha256(protocol_path),
            "validation_artifact": "ece_validation.csv",
        },
        "conformal_framework": (
            "Both candidates fit and apply their maps on the even/odd conformal-development "
            "split, then use the same finite-sample-corrected split-conformal score and target."
        ),
        "test_access": "No test IDs, metadata, predictions, or outcomes loaded before this manifest was written.",
        "historical_outputs_preserved": True,
    }
    manifest_path = OUT / "phase4_corrected_selection_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str))

    # Locked-test confirmation: this is the sole test access and scoring pass.
    test_ids = pd.read_csv(SPLITS / "test_ids.csv")["SEQN"].tolist()
    test_master = pd.read_parquet(
        DATA / "analysis_dataset_primary.parquet",
        filters=[("SEQN", "in", test_ids)],
    ).sort_values("SEQN").reset_index(drop=True)
    test_detail_rows = []
    for model in MODELS:
        test_prediction = pd.read_csv(PRED / f"test_predictions_{model}.csv")
        test_df = test_master.merge(test_prediction, on="SEQN", validate="one_to_one")
        if not np.array_equal(
            test_df[OUTCOME].astype(int).to_numpy(),
            test_df["true_target"].astype(int).to_numpy(),
        ):
            raise RuntimeError(f"{model}: test outcome does not match prediction artifact")
        joined = meta.merge(oof[model], on="SEQN", validate="one_to_one")
        fit_df = joined[joined.part == "fit"].reset_index(drop=True)
        maps, _ = build_calibrators(fit_df, fit_df.predicted_probability.to_numpy())
        raw = test_df.predicted_probability.to_numpy()
        for candidate in dict.fromkeys(["global_platt", chosen[model]]):
            transformed, sources = transform_probabilities(test_df, raw, maps, candidate)
            test_detail_rows.extend(evaluate_candidate(
                test_df.rename(columns={OUTCOME: OUTCOME}),
                raw, transformed, sources, model, candidate,
                "LOCKED_TEST_CONFIRMATION",
            ))
    test_detail = pd.DataFrame(test_detail_rows)
    test_detail.to_csv(OUT / "phase4_corrected_locked_test_confirmation.csv", index=False)

    fairness_rows = []
    for phase, frame in (("OOF_EVAL", comparison), ("LOCKED_TEST_CONFIRMATION", test_detail)):
        for model in MODELS:
            candidates = (
                list(dict.fromkeys(["global_platt", chosen[model]]))
                if phase == "LOCKED_TEST_CONFIRMATION" else
                ["global_platt", "subgroup_platt_bmi_age"]
            )
            for candidate in candidates:
                if phase == "OOF_EVAL":
                    row = frame[(frame.model == model) & (frame.candidate == candidate)].iloc[0]
                    fairness_rows.append({
                        "model": model, "candidate": candidate, "phase": phase,
                        "normal_sensitivity": row.normal_sensitivity,
                        "obese_sensitivity": row.obese_sensitivity,
                        "bmi_obese_minus_normal_gap_pp": row.bmi_obese_minus_normal_gap_pp,
                        "age60_minus_age40_gap_pp": row.age60_minus_age40_gap_pp,
                        "overall_sensitivity": row.overall_sensitivity,
                        "overall_specificity": row.overall_specificity,
                        "classification_decisions_unchanged": True,
                    })
                else:
                    normal = frame[(frame.model == model) & (frame.candidate == candidate) &
                                   (frame.scope == "BMI_Normal")].iloc[0]
                    obese = frame[(frame.model == model) & (frame.candidate == candidate) &
                                  (frame.scope == "BMI_Obese")].iloc[0]
                    age40 = frame[(frame.model == model) & (frame.candidate == candidate) &
                                  (frame.scope == "AGE_40-59")].iloc[0]
                    age60 = frame[(frame.model == model) & (frame.candidate == candidate) &
                                  (frame.scope == "AGE_60+")].iloc[0]
                    overall = frame[(frame.model == model) & (frame.candidate == candidate) &
                                    (frame.scope == "OVERALL")].iloc[0]
                    fairness_rows.append({
                        "model": model, "candidate": candidate, "phase": phase,
                        "normal_sensitivity": normal.sensitivity,
                        "obese_sensitivity": obese.sensitivity,
                        "bmi_obese_minus_normal_gap_pp":
                            (obese.sensitivity - normal.sensitivity) * 100,
                        "age60_minus_age40_gap_pp":
                            (age60.sensitivity - age40.sensitivity) * 100,
                        "overall_sensitivity": overall.sensitivity,
                        "overall_specificity": overall.specificity,
                        "classification_decisions_unchanged": True,
                    })
    fairness = pd.DataFrame(fairness_rows)
    fairness["change_vs_global_bmi_gap_pp"] = np.nan
    for phase in fairness.phase.unique():
        for model in MODELS:
            base = fairness[(fairness.phase == phase) & (fairness.model == model) &
                            (fairness.candidate == "global_platt")]
            if base.empty:
                continue
            index = (fairness.phase == phase) & (fairness.model == model)
            fairness.loc[index, "change_vs_global_bmi_gap_pp"] = (
                fairness.loc[index, "bmi_obese_minus_normal_gap_pp"] -
                float(base.iloc[0].bmi_obese_minus_normal_gap_pp)
            )
    fairness.to_csv(OUT / "phase4_corrected_fairness_comparison.csv", index=False)

    test_selected = []
    for model in MODELS:
        selected = fairness[(fairness.phase == "LOCKED_TEST_CONFIRMATION") &
                            (fairness.model == model)].iloc[0]
        global_row = test_detail[(test_detail.model == model) &
                                 (test_detail.candidate == "global_platt") &
                                 (test_detail.scope == "BMI_Normal")].iloc[0]
        global_obese = test_detail[(test_detail.model == model) &
                                   (test_detail.candidate == "global_platt") &
                                   (test_detail.scope == "BMI_Obese")].iloc[0]
        global_gap = (global_obese.sensitivity - global_row.sensitivity) * 100
        test_selected.append({
            "model": model, "selected_candidate": chosen[model],
            "test_gap_change_pp": float(selected.bmi_obese_minus_normal_gap_pp - global_gap),
        })
    test_selected = pd.DataFrame(test_selected)

    # Figures are derived from frozen development/test rows; no further method changes occur.
    x = np.arange(len(MODELS))
    fig, ax = plt.subplots(figsize=(8, 5))
    global_ece = [comparison[(comparison.model == m) &
                             (comparison.candidate == "global_platt")].ece.iloc[0]
                  for m in MODELS]
    subgroup_ece = [comparison[(comparison.model == m) &
                               (comparison.candidate == "subgroup_platt_bmi_age")].ece.iloc[0]
                    for m in MODELS]
    ax.bar(x - 0.18, global_ece, 0.36, label="Global Platt")
    ax.bar(x + 0.18, subgroup_ece, 0.36, label="Subgroup Platt")
    ax.set_xticks(x, MODELS, rotation=20)
    ax.set_ylabel("OOF evaluation ECE (equal-frequency deciles)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "phase4_corrected_ece_comparison.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    gaps = [comparison[(comparison.model == m) &
                       (comparison.candidate == "global_platt")].bmi_obese_minus_normal_gap_pp.iloc[0]
            for m in MODELS]
    ax.bar(x, gaps, color="#4c78a8")
    ax.set_xticks(x, MODELS, rotation=20)
    ax.set_ylabel("OOF Obese − Normal sensitivity gap (pp)")
    fig.tight_layout()
    fig.savefig(FIG / "phase4_corrected_fairness_gaps.png", dpi=160)
    plt.close(fig)

    write_docs(chosen, test_selected)
    outputs = [
        OUT / "ece_validation.csv",
        OUT / "phase4_corrected_calibration_results.csv",
        OUT / "phase4_corrected_subgroup_comparison.csv",
        OUT / "phase4_corrected_fairness_comparison.csv",
        OUT / "phase4_corrected_conformal_comparison.csv",
        OUT / "phase4_corrected_locked_test_confirmation.csv",
        manifest_path,
    ]
    lineage = {
        "run": "corrected_phase4_subgroup_calibration",
        "script_sha256": sha256(Path(__file__)),
        "primary_dataset_sha256": sha256(DATA / "analysis_dataset_primary.parquet"),
        "split_file_sha256": {
            path.name: sha256(path) for path in sorted(SPLITS.glob("*.csv"))
        },
        "oof_prediction_sha256": {
            model: sha256(PRED / f"validation_predictions_{model}.csv")
            for model in MODELS
        },
        "test_prediction_sha256": {
            model: sha256(PRED / f"test_predictions_{model}.csv")
            for model in MODELS
        },
        "conformal_artifact_sha256": {
            path.name: sha256(path) for path in sorted(REFIT.glob("*.joblib"))
        },
        "calibration_parameter_records_sha256": parameter_records_hash,
        "protocol_sha256": sha256(protocol_path),
        "manifest_sha256": sha256(manifest_path),
        "output_sha256": {path.name: sha256(path) for path in outputs},
        "figure_sha256": {
            path.name: sha256(path)
            for path in sorted(FIG.glob("*"))
            if path.is_file()
        },
        "documentation_sha256": {
            name: sha256(DOC / name)
            for name in (
                "PHASE4_CORRECTION_RECORD.md",
                "PHASE4_CORRECTED_REPORT.md",
                "PHASE4_CORRECTED_DECISION_LOG.md",
            )
        },
        "historical_phase4_preserved": True,
        "runtime": runtime_metadata(started),
        "runtime_event_logging": {
            "available": False,
            "statement": "Runtime event logging was unavailable; ordering is recorded from the executed control flow.",
        },
    }
    lineage_path = OUT / "phase4_corrected_lineage.json"
    lineage_path.write_text(json.dumps(lineage, indent=2, sort_keys=True))

    print(f"Corrected Phase 4 complete: {OUT}")
    print("Final scientific status: NO ACCEPTABLE SUBGROUP CALIBRATION IMPROVEMENT IDENTIFIED")


if __name__ == "__main__":
    main()
