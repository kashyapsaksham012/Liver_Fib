"""
sens_13_secondary_severity_outcomes.py

Pre-registered SECONDARY analysis (frozen in documentation/phase2/statistical_analysis_plan.md
SECONDARY item 2; documentation/phase2/primary_outcome_definition.md; PHASE2_PROTOCOL_FREEZE.md
row 17): severity-graded outcomes
    - Advanced fibrosis  : LUXSMED >= 9.7 kPa  (outcome_secondary_advanced_9.7kPa)
    - Cirrhosis          : LUXSMED >= 13.6 kPa (outcome_secondary_cirrhosis_13.6kPa)

RELABEL-ONLY DESCRIPTIVE PASS. Mirrors sens_03 (8.0 kPa). No model is refit, no Platt
recalibration parameter is re-fit, no conformal calibration is repeated, and the locked test set
is never re-accessed for any model fitting. Primary cohort (CAND_1, N=7,153), primary 10
predictors, frozen Phase 3 models and frozen Phase 4 Platt parameters. Only the outcome label and
downstream descriptive metrics change.

Rationale for relabel-only rather than per-outcome retraining: recorded in the 2026-08-27
pre-manuscript freeze audit (documentation/final_research_audit/FINAL_REMAINING_WORK_REGISTER.md
item 10) and protocol amendment registry. A severity-threshold shift that adds no new predictors
cannot change model-family or preprocessing selection; full per-outcome retraining is not
justified and is not executed here.

Scope of reporting:
    - >= 9.7 kPa  : discrimination + calibration (raw and frozen-Platt) + BMI/Age sensitivity
                    disparity (descriptive; low power - ~124 test positives).
    - >= 13.6 kPa : discrimination + calibration ONLY (overall). No subgroup fairness -
                    ~59 test positives is too few for any subgroup statement.

Outputs:
    results/sensitivity/secondary_severity_outcomes_results.csv
    results/sensitivity/secondary_severity_outcomes_9p7_bmi_age_fairness.csv
    results/sensitivity/secondary_severity_outcomes_lineage.json
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, roc_auc_score,
                             roc_curve)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import MODEL_NAMES, PROC_DIR, ROOT

RESULTS_DIR = ROOT / "results" / "sensitivity"
PRED_DIR = ROOT / "results" / "predictions"
RECAL_TEST = ROOT / "results" / "calibration" / "test_set_recalibrated_predictions.csv"
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 42
CI_LEVEL = 0.95
EPS = 1e-12

OUTCOMES = [
    ("advanced_9.7kPa", "outcome_secondary_advanced_9.7kPa", "9.7kPa", True),
    ("cirrhosis_13.6kPa", "outcome_secondary_cirrhosis_13.6kPa", "13.6kPa", False),
]


def logit(p):
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def calibration_in_the_large(y, p):
    """Intercept + slope of logit(true) ~ logit(p); the primary study's convention (phase4)."""
    z = logit(p).reshape(-1, 1)
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(z, y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])


def ece_decile(y, p, n_bins=10):
    p = np.asarray(p, dtype=float)
    y = np.asarray(y, dtype=float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    ece = 0.0
    for b in range(n_bins):
        m = idx == b
        if not m.any():
            continue
        ece += (m.mean()) * abs(y[m].mean() - p[m].mean())
    return float(ece)


def youden_j_threshold(y, p):
    fpr, tpr, thr = roc_curve(y, p)
    return float(thr[np.argmax(tpr - fpr)])


def operating_point(y, yhat):
    tp = int(((y == 1) & (yhat == 1)).sum())
    fn = int(((y == 1) & (yhat == 0)).sum())
    tn = int(((y == 0) & (yhat == 0)).sum())
    fp = int(((y == 0) & (yhat == 1)).sum())
    return {
        "sensitivity": tp / (tp + fn) if (tp + fn) else None,
        "specificity": tn / (tn + fp) if (tn + fp) else None,
        "ppv": tp / (tp + fp) if (tp + fp) else None,
        "npv": tn / (tn + fn) if (tn + fn) else None,
    }


def boot_auc_ci(y, p, rng):
    vals = []
    for _ in range(BOOTSTRAP_N):
        idx = rng.integers(0, len(y), size=len(y))
        yb, pb = y[idx], p[idx]
        if len(np.unique(yb)) < 2:
            continue
        vals.append(roc_auc_score(yb, pb))
    a = 1 - CI_LEVEL
    lo, hi = np.percentile(vals, [100 * a / 2, 100 * (1 - a / 2)])
    return float(lo), float(hi), len(vals)


def bmi_age_sensitivity_disparity(df, y, yhat, rng):
    rows = []
    dims = [("bmi", "bmi_group_final", "Obese", "Normal"),
            ("age", "age_group_final", "60+", "40-59")]
    for dim, col, tgt, ref in dims:
        tm = (df[col] == tgt).values
        rm = (df[col] == ref).values
        y_t, yh_t = y[tm], yhat[tm]
        y_r, yh_r = y[rm], yhat[rm]
        n_t_pos, n_r_pos = int((y_t == 1).sum()), int((y_r == 1).sum())
        base = {"dimension": dim, "target_category": tgt, "reference_category": ref,
                "target_n": int(tm.sum()), "target_n_positive": n_t_pos,
                "reference_n": int(rm.sum()), "reference_n_positive": n_r_pos}
        if n_t_pos == 0 or n_r_pos == 0:
            rows.append({**base, "target_sensitivity": None, "reference_sensitivity": None,
                         "absolute_disparity_pp": None, "ci_lower_pp": None, "ci_upper_pp": None})
            continue
        s_t = (yh_t[y_t == 1] == 1).mean()
        s_r = (yh_r[y_r == 1] == 1).mean()
        diffs = []
        for _ in range(BOOTSTRAP_N):
            it = rng.integers(0, len(y_t), size=len(y_t))
            ir = rng.integers(0, len(y_r), size=len(y_r))
            yb_t, yhb_t = y_t[it], yh_t[it]
            yb_r, yhb_r = y_r[ir], yh_r[ir]
            if (yb_t == 1).sum() == 0 or (yb_r == 1).sum() == 0:
                continue
            diffs.append(100 * ((yhb_t[yb_t == 1] == 1).mean() - (yhb_r[yb_r == 1] == 1).mean()))
        a = 1 - CI_LEVEL
        lo, hi = np.percentile(diffs, [100 * a / 2, 100 * (1 - a / 2)]) if diffs else (None, None)
        rows.append({**base, "target_sensitivity": round(float(s_t), 6),
                     "reference_sensitivity": round(float(s_r), 6),
                     "absolute_disparity_pp": round(100 * float(s_t - s_r), 4),
                     "ci_lower_pp": round(float(lo), 4) if lo is not None else None,
                     "ci_upper_pp": round(float(hi), 4) if hi is not None else None})
    return rows


def main():
    primary = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    groups = primary.set_index("SEQN")[["bmi_group_final", "age_group_final"]]
    recal_all = pd.read_csv(RECAL_TEST)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    results, fair_rows = [], []

    for out_key, out_col, thr_tag, do_fairness in OUTCOMES:
        omap = primary.set_index("SEQN")[out_col]
        for name in MODEL_NAMES:
            oof = pd.read_csv(PRED_DIR / f"validation_predictions_{name}.csv")
            oof["y"] = oof["SEQN"].map(omap)
            threshold = youden_j_threshold(oof["y"].values, oof["predicted_probability"].values)

            test = pd.read_csv(PRED_DIR / f"test_predictions_{name}.csv")
            test["y"] = test["SEQN"].map(omap).astype(int)
            test = test.join(groups, on="SEQN")
            y = test["y"].values
            p_raw = test["predicted_probability"].values
            yhat = (p_raw >= threshold).astype(int)

            rc = recal_all[recal_all["model"] == name].set_index("SEQN")
            p_cal = test["SEQN"].map(rc["recalibrated_predicted_probability"]).values

            auc = roc_auc_score(y, p_raw)
            auc_lo, auc_hi, nb = boot_auc_ci(y, p_raw, rng)
            op = operating_point(y, yhat)
            raw_int, raw_slope = calibration_in_the_large(y, p_raw)
            cal_int, cal_slope = calibration_in_the_large(y, p_cal)

            results.append({
                "outcome": out_key, "outcome_threshold": thr_tag, "model": name,
                "test_n": len(test), "test_n_positive": int(y.sum()),
                "test_prevalence": round(float(y.mean()), 6),
                "youden_threshold_oof": round(threshold, 6),
                "roc_auc": round(float(auc), 6),
                "roc_auc_ci_lower": round(auc_lo, 6), "roc_auc_ci_upper": round(auc_hi, 6),
                "pr_auc": round(float(average_precision_score(y, p_raw)), 6),
                "sensitivity": round(op["sensitivity"], 6) if op["sensitivity"] is not None else None,
                "specificity": round(op["specificity"], 6) if op["specificity"] is not None else None,
                "ppv": round(op["ppv"], 6) if op["ppv"] is not None else None,
                "npv": round(op["npv"], 6) if op["npv"] is not None else None,
                "raw_calibration_intercept": round(raw_int, 6),
                "raw_calibration_slope": round(raw_slope, 6),
                "raw_brier": round(float(brier_score_loss(y, p_raw)), 6),
                "raw_ece_decile": round(ece_decile(y, p_raw), 6),
                "platt_recal_calibration_intercept": round(cal_int, 6),
                "platt_recal_calibration_slope": round(cal_slope, 6),
                "platt_recal_brier": round(float(brier_score_loss(y, p_cal)), 6),
                "platt_recal_ece_decile": round(ece_decile(y, p_cal), 6),
                "bootstrap_n_valid_auc": nb,
                "retrained": False, "platt_refit": False, "conformal_repeated": False,
                "test_set_reaccessed_for_model_fitting": False,
            })
            print(f"{out_key:>18} | {name:>14} | thr={threshold:.4f} AUC={auc:.4f} "
                  f"sens={op['sensitivity']:.3f} spec={op['specificity']:.3f} "
                  f"raw_int={raw_int:+.3f} recal_int={cal_int:+.3f}")

            if do_fairness:
                for r in bmi_age_sensitivity_disparity(test, y, yhat, rng):
                    fair_rows.append({"outcome": out_key, "outcome_threshold": thr_tag,
                                      "model": name, **r})

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    res_df = pd.DataFrame(results)
    res_path = RESULTS_DIR / "secondary_severity_outcomes_results.csv"
    res_df.to_csv(res_path, index=False)

    fair_df = pd.DataFrame(fair_rows)
    fair_path = RESULTS_DIR / "secondary_severity_outcomes_9p7_bmi_age_fairness.csv"
    fair_df.to_csv(fair_path, index=False)

    lineage = {
        "analysis": "Pre-registered SECONDARY: severity-graded outcomes (>=9.7 kPa advanced "
                    "fibrosis, >=13.6 kPa cirrhosis)",
        "mode": "RELABEL-ONLY DESCRIPTIVE PASS (mirrors sens_03 8.0 kPa)",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": "src/sens_13_secondary_severity_outcomes.py",
        "preregistration": [
            "documentation/phase2/statistical_analysis_plan.md SECONDARY item 2",
            "documentation/phase2/primary_outcome_definition.md",
            "documentation/phase2/PHASE2_PROTOCOL_FREEZE.md row 17",
        ],
        "inputs": {
            "cohort": "data/processed/analysis_dataset_primary.parquet (CAND_1, N=7,153)",
            "outcome_columns": ["outcome_secondary_advanced_9.7kPa (411 pos, 5.75%)",
                                "outcome_secondary_cirrhosis_13.6kPa (177 pos, 2.47%)"],
            "frozen_oof_predictions": "results/predictions/validation_predictions_<model>.csv",
            "frozen_test_predictions": "results/predictions/test_predictions_<model>.csv",
            "frozen_platt_recalibrated_test": "results/calibration/test_set_recalibrated_predictions.csv",
            "models": MODEL_NAMES,
        },
        "not_done": [
            "No model retraining", "No Platt re-fit (frozen 8.2 kPa params applied unchanged)",
            "No conformal calibration repetition",
            "No subgroup fairness for >=13.6 kPa (test positives ~59, insufficient)",
            "No FDR correction (descriptive secondary pass; CI-only, matching sens_03)",
        ],
        "test_lock": {"test_reaccessed_for_model_fitting": False,
                      "youden_thresholds_rederived_on": "frozen OOF predictions, relabeled"},
        "outputs": [str(res_path.relative_to(ROOT)), str(fair_path.relative_to(ROOT))],
    }
    lin_path = RESULTS_DIR / "secondary_severity_outcomes_lineage.json"
    lin_path.write_text(json.dumps(lineage, indent=2))

    print(f"\nSaved {res_path.relative_to(ROOT)} ({len(res_df)} rows)")
    print(f"Saved {fair_path.relative_to(ROOT)} ({len(fair_df)} rows)")
    print(f"Saved {lin_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
