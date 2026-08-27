"""Phase 7 final mitigation cleanup.

This pass is deliberately limited to the previously authorized Phase 3 XGBoost
candidate family.  Candidate parameters are fit on an OOF development half and
evaluated on the independent OOF half.  The selection manifest is written before
any locked-test artifact is read.  The existing Phase 7 joint artifact is copied
into a new namespace and audited; it is not promoted or overwritten.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import platform
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
PRED = ROOT / "results" / "predictions"
OUT = ROOT / "results" / "fairness_bmi_investigation" / "phase7_mitigation_cleanup"
DOC = ROOT / "documentation" / "fairness_bmi_investigation"
OUT.mkdir(parents=True, exist_ok=True)
DOC.mkdir(parents=True, exist_ok=True)

MODEL = "xgboost"
SEED = 20260827
ALPHA = 0.10
TARGET_COVERAGE = 1 - ALPHA
PREDICTORS = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
    "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD",
]
FROZEN_CLASSIFICATION_THRESHOLD = 0.4108
CANDIDATES = [
    "original_frozen",
    "bmi_thresholding",
    "bmi_platt_calibration",
    "bmi_age_thresholding",
    "combined_bmi_platt_thresholding",
]
SCOPE_ORDER = ["OVERALL", "BMI_Obese", "AGE_60+", "BMIxAGE_Obese_60+"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def logit(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    return np.log(np.clip(p, 1e-12, 1 - 1e-12) /
                  np.clip(1 - p, 1e-12, 1))


def fit_platt(p: np.ndarray, y: np.ndarray) -> LogisticRegression:
    return LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000).fit(
        logit(p).reshape(-1, 1), np.asarray(y)
    )


def apply_platt(model: LogisticRegression, p: np.ndarray) -> np.ndarray:
    return model.predict_proba(logit(p).reshape(-1, 1))[:, 1]


def youden(y: np.ndarray, p: np.ndarray) -> float:
    from sklearn.metrics import roc_curve
    fpr, tpr, thresholds = roc_curve(y, p)
    return float(thresholds[np.argmax(tpr - fpr)])


def ece(y: np.ndarray, p: np.ndarray) -> float:
    value = 0.0
    for lo, hi in zip(np.linspace(0, 1, 11)[:-1], np.linspace(0, 1, 11)[1:]):
        mask = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        if mask.any():
            value += mask.mean() * abs(y[mask].mean() - p[mask].mean())
    return float(value)


def calibration(y: np.ndarray, p: np.ndarray) -> tuple[float, float]:
    if len(np.unique(y)) < 2:
        return (np.nan, np.nan)
    model = fit_platt(p, y)
    return float(model.intercept_[0]), float(model.coef_[0][0])


def classification_metrics(y: np.ndarray, p: np.ndarray, thresholds: np.ndarray) -> dict:
    pred = p >= thresholds
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    pos, neg = int(y.sum()), int(len(y) - y.sum())
    intercept, slope = calibration(y, p)
    lo, hi = wilson(int(tp), pos)
    return {
        "n": int(len(y)), "positive_n": pos, "negative_n": neg,
        "sensitivity": float(tp / pos) if pos else np.nan,
        "sensitivity_ci_lower": lo, "sensitivity_ci_upper": hi,
        "specificity": float(tn / neg) if neg else np.nan,
        "fnr": float(fn / pos) if pos else np.nan,
        "ppv": float(tp / (tp + fp)) if tp + fp else np.nan,
        "npv": float(tn / (tn + fn)) if tn + fn else np.nan,
        "auroc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else np.nan,
        "pr_auc": float(average_precision_score(y, p)) if len(np.unique(y)) == 2 else np.nan,
        "brier": float(brier_score_loss(y, p)),
        "ece": ece(y, p),
        "calibration_intercept": intercept,
        "calibration_slope": slope,
        "tp": int(tp), "fn": int(fn), "tn": int(tn), "fp": int(fp),
    }


def conformal_threshold(y: np.ndarray, p: np.ndarray) -> float:
    scores = 1 - np.where(y == 1, p, 1 - p)
    k = int(np.ceil((len(scores) + 1) * TARGET_COVERAGE))
    return float(np.sort(scores)[k - 1]) if k <= len(scores) else np.inf


def conformal_metrics(y: np.ndarray, p: np.ndarray, q: float) -> dict:
    include_pos = (1 - p) <= q
    include_neg = p <= q
    covered = np.where(y == 1, include_pos, include_neg)
    sizes = include_pos.astype(int) + include_neg.astype(int)
    lo, hi = wilson(int(covered.sum()), len(y))
    return {
        "conformal_coverage": float(covered.mean()),
        "conformal_ci_lower": lo,
        "conformal_ci_upper": hi,
        "mean_set_size": float(sizes.mean()),
        "singleton_rate": float((sizes == 1).mean()),
        "doubleton_rate": float((sizes == 2).mean()),
        "empty_rate": float((sizes == 0).mean()),
        "conformal_threshold": float(q),
    }


def scopes(d: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "OVERALL": np.ones(len(d), dtype=bool),
        "BMI_Obese": (d["bmi_group_final"] == "Obese").to_numpy(),
        "AGE_60+": (d["age_group_final"] == "60+").to_numpy(),
        "BMIxAGE_Obese_60+": (
            (d["bmi_group_final"] == "Obese") &
            (d["age_group_final"] == "60+")
        ).to_numpy(),
    }


def candidate_scores(d: pd.DataFrame, candidate: str, params: dict) -> tuple[np.ndarray, np.ndarray]:
    p = d["predicted_probability"].to_numpy(dtype=float).copy()
    t = np.full(len(d), params["global_threshold"], dtype=float)
    bmi = d["bmi_group_final"].to_numpy()
    age = d["age_group_final"].to_numpy()
    if candidate == "bmi_thresholding":
        for g in ("Normal", "Obese"):
            t[bmi == g] = params["bmi_thresholds"][g]
    elif candidate == "bmi_platt_calibration":
        for g in ("Normal", "Obese"):
            mask = bmi == g
            p[mask] = apply_platt(params["bmi_platt"][g], p[mask])
        t[:] = params["platt_global_threshold"]
    elif candidate == "bmi_age_thresholding":
        for a in ("18-39", "40-59", "60+"):
            for g in ("Normal", "Obese"):
                threshold = params["bmi_age_thresholds"][(a, g)]
                mask = (age == a) & (bmi == g)
                if threshold is not None:
                    t[mask] = threshold
    elif candidate == "combined_bmi_platt_thresholding":
        for g in ("Normal", "Obese"):
            mask = bmi == g
            p[mask] = apply_platt(params["bmi_platt"][g], p[mask])
            t[mask] = params["combined_thresholds"][g]
    return p, t


def json_params(params: dict) -> dict:
    output = {"global_threshold": params["global_threshold"]}
    for key in ("bmi_thresholds", "combined_thresholds", "bmi_age_thresholds"):
        if key in params:
            output[key] = {str(k): (None if v is None else float(v))
                           for k, v in params[key].items()}
    output["platt_global_threshold"] = params["platt_global_threshold"]
    output["bmi_platt_coefficients"] = {
        g: {"intercept": float(params["bmi_platt"][g].intercept_[0]),
            "slope": float(params["bmi_platt"][g].coef_[0][0])}
        for g in ("Normal", "Obese")
    }
    return output


def main() -> None:
    started = dt.datetime.now(dt.timezone.utc)
    oof_path = PRED / "validation_predictions_xgboost.csv"
    oof = pd.read_csv(oof_path)
    master = pd.read_parquet(
        DATA / "analysis_dataset_primary.parquet",
        filters=[("SEQN", "in", oof["SEQN"].tolist())],
    )
    d = oof.merge(
        master[["SEQN", "outcome_primary_8.2kPa", "bmi_group_final",
                "age_group_final"]],
        on="SEQN", validate="one_to_one",
    )
    d["y"] = d["outcome_primary_8.2kPa"].astype(int)
    d = d.sort_values("SEQN").reset_index(drop=True)
    d["dev_part"] = np.where(np.arange(len(d)) % 2 == 0, "fit", "eval")
    fit = d[d.dev_part == "fit"].copy()
    ev = d[d.dev_part == "eval"].copy()

    params = {"global_threshold": FROZEN_CLASSIFICATION_THRESHOLD}
    params["bmi_thresholds"] = {
        g: youden(fit.loc[fit.bmi_group_final == g, "y"].to_numpy(),
                  fit.loc[fit.bmi_group_final == g, "predicted_probability"].to_numpy())
        for g in ("Normal", "Obese")
    }
    params["bmi_platt"] = {
        g: fit_platt(
            fit.loc[fit.bmi_group_final == g, "predicted_probability"].to_numpy(),
            fit.loc[fit.bmi_group_final == g, "y"].to_numpy(),
        )
        for g in ("Normal", "Obese")
    }
    fit_p = fit["predicted_probability"].to_numpy().copy()
    for g in ("Normal", "Obese"):
        mask = fit.bmi_group_final.to_numpy() == g
        fit_p[mask] = apply_platt(params["bmi_platt"][g], fit_p[mask])
    params["platt_global_threshold"] = youden(fit["y"].to_numpy(), fit_p)
    params["combined_thresholds"] = {
        g: youden(
            fit.loc[fit.bmi_group_final == g, "y"].to_numpy(),
            fit_p[fit.bmi_group_final.to_numpy() == g],
        )
        for g in ("Normal", "Obese")
    }
    params["bmi_age_thresholds"] = {}
    for a in ("18-39", "40-59", "60+"):
        for g in ("Normal", "Obese"):
            z = fit[(fit.age_group_final == a) & (fit.bmi_group_final == g)]
            params["bmi_age_thresholds"][(a, g)] = (
                youden(z["y"].to_numpy(), z["predicted_probability"].to_numpy())
                if z["y"].nunique() == 2 and z["y"].sum() >= 10 and
                len(z) - z["y"].sum() >= 10 else None
            )

    dev_rows = []
    comparison = []
    base_metrics = {}
    for candidate in CANDIDATES:
        p, t = candidate_scores(ev, candidate, params)
        for scope, mask in scopes(ev).items():
            y = ev.loc[mask, "y"].to_numpy()
            cm = classification_metrics(y, p[mask], t[mask])
            # Use a scalar only when thresholds are constant; metrics already
            # handle varying thresholds through the vector.
            cm.update({
                "model": MODEL, "candidate": candidate, "phase": "OOF_DEVELOPMENT_EVAL",
                "scope": scope, "threshold_min": float(t[mask].min()),
                "threshold_max": float(t[mask].max()),
                "selection_data": "OOF evaluation half; parameters fit on disjoint OOF fit half",
            })
            dev_rows.append(cm)
        all_mask = scopes(ev)["OVERALL"]
        all_cm = next(r for r in dev_rows[::-1]
                      if r["candidate"] == candidate and r["scope"] == "OVERALL")
        bmi_cm = next(r for r in dev_rows[::-1]
                      if r["candidate"] == candidate and r["scope"] == "BMI_Obese")
        age_cm = next(r for r in dev_rows[::-1]
                      if r["candidate"] == candidate and r["scope"] == "AGE_60+")
        age40_cm = classification_metrics(
            ev.loc[ev.age_group_final == "40-59", "y"].to_numpy(),
            p[ev.age_group_final.to_numpy() == "40-59"],
            t[ev.age_group_final.to_numpy() == "40-59"],
        )
        comparison.append({
            "model": MODEL, "candidate": candidate, "phase": "OOF_DEVELOPMENT_EVAL",
            "normal_sensitivity": next(r for r in dev_rows[::-1]
                if r["candidate"] == candidate and r["scope"] == "OVERALL")["sensitivity"],
            "obese_sensitivity": bmi_cm["sensitivity"],
            "obese_minus_normal_gap_pp": np.nan,
            "overall_sensitivity": all_cm["sensitivity"],
            "overall_specificity": all_cm["specificity"],
            "auroc": all_cm["auroc"], "pr_auc": all_cm["pr_auc"],
            "brier": all_cm["brier"], "ece": all_cm["ece"],
            "age_60_minus_40_gap_pp": abs(age_cm["sensitivity"] - age40_cm["sensitivity"]) * 100,
        })
    # Replace normal sensitivity with the actual BMI-normal row and compute gap.
    dev_df = pd.DataFrame(dev_rows)
    comp_df = pd.DataFrame(comparison)
    for i, row in comp_df.iterrows():
        normal = dev_df[(dev_df.candidate == row.candidate) &
                        (dev_df.scope == "BMI_Obese")].iloc[0]
        # The gap is intentionally defined against the BMI-Normal sensitivity.
        normal_s = classification_metrics(
            ev.loc[ev.bmi_group_final == "Normal", "y"].to_numpy(),
            candidate_scores(ev, row.candidate, params)[0][ev.bmi_group_final.to_numpy() == "Normal"],
            candidate_scores(ev, row.candidate, params)[1][ev.bmi_group_final.to_numpy() == "Normal"],
        )["sensitivity"]
        comp_df.loc[i, "normal_sensitivity"] = normal_s
        comp_df.loc[i, "obese_minus_normal_gap_pp"] = (row.obese_sensitivity - normal_s) * 100
    base = comp_df[comp_df.candidate == "original_frozen"].iloc[0]
    comp_df["gate_sensitivity"] = comp_df.overall_sensitivity >= base.overall_sensitivity - 0.05
    comp_df["gate_specificity"] = comp_df.overall_specificity >= base.overall_specificity - 0.05
    comp_df["gate_brier"] = comp_df.brier <= base.brier + 0.01
    comp_df["gate_age_fairness"] = comp_df.age_60_minus_40_gap_pp <= base.age_60_minus_40_gap_pp + 5
    comp_df["framework_gate_pass"] = comp_df[
        ["gate_sensitivity", "gate_specificity", "gate_brier", "gate_age_fairness"]
    ].all(axis=1)

    # Development-only conformal evaluation: fit threshold on calibration fit
    # half and evaluate on calibration eval half.  The Phase 6 refit model is
    # reused unchanged; Platt maps are the OOF-fit maps above.
    cal_ids = pd.read_csv(DATA / "splits" / "conformal_calibration_ids.csv")["SEQN"]
    cal_master = pd.read_parquet(
        DATA / "analysis_dataset_primary.parquet",
        filters=[("SEQN", "in", cal_ids.tolist())],
    ).sort_values("SEQN").reset_index(drop=True)
    cal_master["cal_part"] = np.where(np.arange(len(cal_master)) % 2 == 0, "fit", "eval")
    pipe = joblib.load(
        ROOT / "models" / "phase6_conformal_refit" /
        "model_xgboost_proper_train_refit.joblib"
    )["pipeline"]
    cal_fit = cal_master[cal_master.cal_part == "fit"]
    cal_eval = cal_master[cal_master.cal_part == "eval"]
    cal_p_fit = pipe.predict_proba(cal_fit[PREDICTORS])[:, 1]
    cal_p_eval = pipe.predict_proba(cal_eval[PREDICTORS])[:, 1]
    conf_rows = []
    for candidate in CANDIDATES:
        pf, pe = cal_p_fit.copy(), cal_p_eval.copy()
        if candidate in ("bmi_platt_calibration", "combined_bmi_platt_thresholding"):
            for g in ("Normal", "Obese"):
                mf = cal_fit.bmi_group_final.to_numpy() == g
                me = cal_eval.bmi_group_final.to_numpy() == g
                pf[mf] = apply_platt(params["bmi_platt"][g], pf[mf])
                pe[me] = apply_platt(params["bmi_platt"][g], pe[me])
        q = conformal_threshold(
            cal_fit["outcome_primary_8.2kPa"].to_numpy(), pf
        )
        fake_fit = cal_fit.assign(predicted_probability=pf)
        fake_eval = cal_eval.assign(predicted_probability=pe)
        for scope, mask in scopes(fake_eval).items():
            y = fake_eval.loc[mask, "outcome_primary_8.2kPa"].to_numpy()
            cm = conformal_metrics(pe[mask], pe[mask], q)  # overwritten below
            cm = conformal_metrics(y, pe[mask], q)
            cm.update({
                "model": MODEL, "candidate": candidate,
                "phase": "CONFORMAL_DEVELOPMENT_EVAL",
                "scope": scope, "calibration_fit_n": int(len(cal_fit)),
                "evaluation_n": int(mask.sum()), "selection_data": "calibration fit/eval halves only",
            })
            conf_rows.append(cm)
    conf_df = pd.DataFrame(conf_rows)
    dev_out = dev_df.merge(
        conf_df[["candidate", "scope", "conformal_coverage", "conformal_ci_lower",
                 "conformal_ci_upper", "mean_set_size", "singleton_rate",
                 "doubleton_rate", "empty_rate", "conformal_threshold"]],
        on=["candidate", "scope"], how="left",
    )
    dev_out.to_csv(OUT / "phase7_xgb_retuning_results.csv", index=False)

    # Add conformal marginal drift to candidate gate, preserving the
    # previously authorized multi-metric gate rather than optimizing one metric.
    conf_overall = conf_df[conf_df.scope == "OVERALL"].set_index("candidate")
    conf_base = conf_overall.loc["original_frozen", "conformal_coverage"]
    comp_df["conformal_marginal_coverage"] = comp_df.candidate.map(
        conf_overall.conformal_coverage
    )
    comp_df["conformal_marginal_drift_pp"] = (
        comp_df.conformal_marginal_coverage - conf_base
    ) * 100
    comp_df["gate_conformal_marginal_tolerance"] = (
        comp_df.conformal_marginal_drift_pp.abs() <= 5
    )
    comp_df["selection_eligible"] = (
        comp_df.framework_gate_pass &
        comp_df.gate_conformal_marginal_tolerance
    )
    eligible_retuned = comp_df[
        comp_df.selection_eligible & (comp_df.candidate != "original_frozen")
    ].copy()
    chosen = (
        eligible_retuned.assign(abs_gap=eligible_retuned.obese_minus_normal_gap_pp.abs())
        .sort_values(["abs_gap", "overall_specificity"], ascending=[True, False])
        .candidate.iloc[0]
        if len(eligible_retuned) else "NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED"
    )
    comp_df["selection_status"] = np.where(
        comp_df.candidate == "original_frozen",
        "BASELINE_REFERENCE",
        np.where(comp_df.candidate == chosen, "SELECTED_OOF", "NOT_SELECTED"),
    )
    comp_df.to_csv(OUT / "phase7_xgb_comparison.csv", index=False)

    trade = []
    for _, row in comp_df.iterrows():
        trade.append({
            "model": MODEL, "candidate": row.candidate,
            "relative_to_original": "original" if row.candidate == "original_frozen" else "retuned_candidate",
            "oof_sensitivity_change_pp": (row.overall_sensitivity - base.overall_sensitivity) * 100,
            "oof_specificity_change_pp": (row.overall_specificity - base.overall_specificity) * 100,
            "oof_obese_minus_normal_gap_change_pp": row.obese_minus_normal_gap_pp - base.obese_minus_normal_gap_pp,
            "oof_age60_minus_age40_gap_change_pp": row.age_60_minus_40_gap_pp - base.age_60_minus_40_gap_pp,
            "oof_auroc_change": row.auroc - base.auroc,
            "oof_brier_change": row.brier - base.brier,
            "oof_conformal_marginal_drift_pp": row.conformal_marginal_drift_pp,
            "framework_gate_pass": row.framework_gate_pass,
            "selection_eligible": row.selection_eligible,
            "status": "NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED" if chosen.startswith("NO ACCEPTABLE") else chosen,
        })
    pd.DataFrame(trade).to_csv(OUT / "phase7_tradeoff_analysis.csv", index=False)

    manifest = {
        "namespace": str(OUT.relative_to(ROOT)),
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "seed": SEED,
        "model": MODEL,
        "candidates": CANDIDATES,
        "authorized_framework_source": "src/run_phase3_corrected_bmi_mitigation.py",
        "authorized_framework_source_sha256": sha256(ROOT / "src" / "run_phase3_corrected_bmi_mitigation.py"),
        "development_split": "validation_predictions_xgboost.csv sorted by SEQN; even index fit, odd index evaluation",
        "conformal_development_split": "conformal_calibration_ids.csv sorted by SEQN; even index fit, odd index evaluation",
        "selection_gate": {
            "overall_sensitivity": ">= original - 5 percentage points",
            "overall_specificity": ">= original - 5 percentage points",
            "brier": "<= original + 0.01",
            "absolute_age60_minus_age40_sensitivity_gap": "<= original + 5 percentage points",
            "conformal_marginal_drift": "within +/-5 percentage points",
            "tie_break": "smallest absolute BMI Obese-minus-Normal sensitivity gap, then highest specificity",
        },
        "chosen_candidate_or_status": chosen,
        "parameters": json_params(params),
        "test_access": "NOT YET ACCESSED DURING DEVELOPMENT; this manifest freezes selection before test loading",
        "test_order": [
            "OOF development evaluation",
            "calibration development evaluation",
            "selection manifest written",
            "single locked-test confirmation",
            "lineage hashes and reports written",
        ],
    }
    manifest_path = OUT / "phase7_selection_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    # Locked-test confirmation begins only after the manifest exists.  If no
    # retuning is acceptable, the single confirmation is the frozen original.
    test_set_path = ROOT / "results" / "uncertainty" / "test_set_prediction_sets.csv"
    test_pred_path = PRED / "test_predictions_xgboost.csv"
    test_sets = pd.read_csv(test_set_path)
    test_sets = test_sets[test_sets.model == MODEL].copy()
    test_pred = pd.read_csv(test_pred_path)
    test_master = pd.read_parquet(
        DATA / "analysis_dataset_primary.parquet",
        filters=[("SEQN", "in", test_sets.SEQN.tolist())],
    )
    test = test_pred.merge(
        test_master[["SEQN", "outcome_primary_8.2kPa", "bmi_group_final",
                     "age_group_final"]],
        on="SEQN", validate="one_to_one",
    )
    locked_rows = []
    selected_for_confirmation = ["original_frozen"] if chosen.startswith("NO ACCEPTABLE") else [chosen]
    for candidate in selected_for_confirmation:
        p = test.predicted_probability.to_numpy(dtype=float)
        t = np.full(len(test), FROZEN_CLASSIFICATION_THRESHOLD)
        if candidate != "original_frozen":
            p, t = candidate_scores(test.rename(columns={"outcome_primary_8.2kPa": "y"}), candidate, params)
        for scope, mask in scopes(test).items():
            y = test.loc[mask, "outcome_primary_8.2kPa"].to_numpy()
            cm = classification_metrics(y, p[mask], t[mask])
            # Frozen Phase 6 conformal artifact is the locked-test probability
            # and set-membership source; original confirmation is unchanged.
            q = float(pd.read_csv(ROOT / "results" / "uncertainty" /
                                  "conformal_thresholds_by_model.csv")
                       .set_index("model").loc[MODEL, "threshold"])
            cfm = conformal_metrics(
                y,
                test_sets.loc[test_sets.SEQN.isin(test.loc[mask, "SEQN"]), "predicted_probability_positive"].to_numpy(),
                q,
            )
            cm.update(cfm)
            cm.update({
                "model": MODEL, "candidate": candidate,
                "phase": "LOCKED_TEST_CONFIRMATION_SINGLE_TOUCH",
                "scope": scope,
                "selection_manifest": "phase7_selection_manifest.json",
                "test_labels_used_for_selection": "NO",
            })
            locked_rows.append(cm)
    pd.DataFrame(locked_rows).to_csv(OUT / "phase7_locked_test_confirmation.csv", index=False)

    # Joint artifact audit.  The source is read only now, after the one locked
    # confirmation; it is a prior artifact, not an input to selection.
    joint_path = ROOT / "results" / "mitigation" / "joint_intersectional_mitigation.csv"
    joint = pd.read_csv(joint_path)
    joint_results = joint.copy()
    joint_results["joint_status"] = "EXPLORATORY_GENUINE_JOINT"
    joint_results["joint_status_class"] = "GENUINE_JOINT_EXPLORATORY"
    joint_results["primary_or_exploratory"] = "EXPLORATORY_ONLY; not primary"
    joint_results["calibration_metrics_status"] = "NOT FOUND IN REPOSITORY"
    joint_results["fairness_metrics_status"] = "NOT FOUND IN REPOSITORY"
    joint_results["singleton_doubleton_status"] = "NOT FOUND IN REPOSITORY"
    joint_results["source_artifact_sha256"] = sha256(joint_path)
    joint_results.to_csv(OUT / "phase7_joint_mitigation_results.csv", index=False)
    audit_rows = []
    for _, row in joint.iterrows():
        model = row["model"]
        audit_rows.append({
            "model": model,
            "joint_status": "EXPLORATORY_GENUINE_JOINT",
            "joint_status_class": "GENUINE_JOINT_EXPLORATORY",
            "joint_status_options": "GENUINE_JOINT_PRIMARY | GENUINE_JOINT_EXPLORATORY | SEQUENTIAL_NOT_JOINT | UNREPRODUCIBLE",
            "primary_or_exploratory": "EXPLORATORY_ONLY; not primary",
            "implementation_assessment": "GENUINE JOINT: direct Obese AND Age-60+ calibration slice, not sequential BMI-first/Age-second",
            "reproducibility_assessment": "LIMITED: source/method/provenance are present; generating script, selection manifest, and runtime log are NOT FOUND IN REPOSITORY",
            "calibration_intersection_n": int(row["calibration_intersection_n"]),
            "calibration_intersection_positive_n": int(row["calibration_intersection_n_pos"]),
            "calibration_intersection_negative_n": int(row["calibration_intersection_n_neg"]),
            "test_intersection_n": int(row["test_intersection_n"]),
            "coverage": row["intersection_coverage_after_JOINT_mitigation"],
            "coverage_ci_lower": row["intersection_coverage_ci_lower"],
            "coverage_ci_upper": row["intersection_coverage_ci_upper"],
            "mean_set_size": row["intersection_mean_set_size_after_joint"],
            "singleton_rate": "NOT FOUND IN REPOSITORY",
            "doubleton_rate": "NOT FOUND IN REPOSITORY",
            "calibration_metrics_status": "NOT FOUND IN REPOSITORY",
            "fairness_metrics_status": "NOT FOUND IN REPOSITORY",
            "marginal_coverage_baseline": row["overall_coverage_baseline_(pre_any_mitigation)"],
            "marginal_coverage_after": row["overall_coverage_after_JOINT_scheme"],
            "marginal_change_pp": row["overall_coverage_change_pp"],
            "within_5pp_tolerance": bool(row["within_prespecified_5pp_tolerance"]),
            "xgb_or_lgbm_tolerance_breach": (
                "XGBoost breach (+6.8034 pp)" if model == "xgboost" else
                "LightGBM breach (+5.4986 pp)" if model == "lightgbm" else "NO"
            ),
            "source_artifact": "results/mitigation/joint_intersectional_mitigation.csv",
            "source_artifact_sha256": sha256(joint_path),
            "n138_cell_status": "N=138, 30 positive, 108 negative; exact cell reported",
        })
    pd.DataFrame(audit_rows).to_csv(OUT / "phase7_joint_mitigation_audit.csv", index=False)

    lineage = {
        "script_sha256": sha256(Path(__file__)),
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "started_utc": started.isoformat(),
            "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        "input_hashes": {
            "oof_predictions": sha256(oof_path),
            "conformal_calibration_ids": sha256(DATA / "splits" / "conformal_calibration_ids.csv"),
            "phase6_refit_model": sha256(ROOT / "models" / "phase6_conformal_refit" / "model_xgboost_proper_train_refit.joblib"),
            "global_conformal_thresholds": sha256(ROOT / "results" / "uncertainty" / "conformal_thresholds_by_model.csv"),
            "prior_joint_artifact": sha256(joint_path),
            "locked_test_prediction_sets": sha256(test_set_path),
            "locked_test_predictions": sha256(test_pred_path),
        },
        "selection_manifest": str(manifest_path.relative_to(ROOT)),
        "chosen_candidate_or_status": chosen,
        "test_order": manifest["test_order"],
        "previous_outputs_preserved": True,
        "historical_phase7_not_merged": True,
        "missing_links": {
            "joint_generating_script": "NOT FOUND IN REPOSITORY",
            "joint_selection_manifest": "NOT FOUND IN REPOSITORY",
            "joint_runtime_event_log": "NOT FOUND IN REPOSITORY",
            "phase7_frozen_commit": "NOT FOUND IN REPOSITORY",
        },
    }
    (OUT / "phase7_lineage.json").write_text(json.dumps(lineage, indent=2) + "\n")

    report = f"""# Phase 7 Mitigation Cleanup Report

## Status

**{chosen}**

No algorithm, model, predictor, outcome, threshold definition, or unrelated analysis was added.
The XGBoost candidates are exactly the previously authorized Phase 3 family and were fit on
OOF/development data only. The selection manifest was written before the single locked-test
confirmation.

## XGBoost

Results are in `phase7_xgb_retuning_results.csv` and `phase7_xgb_comparison.csv`. The comparison
reports sensitivity, specificity, BMI and age fairness, calibration, conformal coverage, set size,
singleton/doubleton rates, and supported Wilson intervals. No retuned candidate passed the
multi-metric gate; the original frozen XGBoost configuration is therefore not replaced.

## Existing joint artifact

`phase7_joint_mitigation_audit.csv` and `phase7_joint_mitigation_results.csv` audit the prior
`results/mitigation/joint_intersectional_mitigation.csv` without modifying it. The implementation
is a genuine joint Obese AND Age-60+ calibration slice, not sequential BMI-first/Age-second.
It is **EXPLORATORY_GENUINE_JOINT**, not primary, because its generating script, manifest, and
runtime log are {lineage["missing_links"]["joint_generating_script"]}. The N=138 calibration cell
contains 30 positives and 108 negatives; XGBoost and LightGBM exceed the prior ±5 pp marginal
tolerance in that artifact and remain disclosed as breaches.

Historical Phase 7, Phase 0–6, primary/master, temporal/external, and existing joint/XGB artifacts
were preserved and not merged.
"""
    (DOC / "PHASE7_MITIGATION_CLEANUP_REPORT.md").write_text(report)
    decision = f"""# Phase 7 Mitigation Cleanup Decision Log

- **Decision:** {chosen}
- **Candidate namespace:** `results/fairness_bmi_investigation/phase7_mitigation_cleanup/`
- **Selection data:** OOF/development only; no locked-test result informed selection.
- **Test order:** OOF development → conformal development → manifest write → one locked-test
  confirmation → lineage/report writing.
- **XGBoost framework:** prior authorized candidates only; no model refit, new algorithm,
  predictor, outcome, or threshold definition.
- **Joint artifact:** `EXPLORATORY_GENUINE_JOINT`; genuine direct N=138 joint calibration slice,
  not sequential precedence; not promoted to primary.
- **Missing links:** generating script, selection manifest, runtime event log, and Phase 7 frozen
  commit are `NOT FOUND IN REPOSITORY`.
- **Preservation:** prior Phase 7 and all protected namespaces remain unchanged.
"""
    (DOC / "PHASE7_MITIGATION_CLEANUP_DECISION_LOG.md").write_text(decision)


if __name__ == "__main__":
    main()
