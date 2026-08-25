"""
sens_05_subgroup_recalibration.py
Diagnostic Analysis 3 (Three-Diagnostics Protocol Freeze, 2026-08-25): subgroup-specific Platt
recalibration for BMI-Obese and Age-60+, evaluated both for probability calibration (primary v1
model family) and for conformal coverage (proper_train_refit model family, with full nonconformity
score and quantile re-derivation -- no reuse of old conformal scores/thresholds).

SECONDARY / DIAGNOSTIC / SUPPLEMENTARY. Does not modify or replace any frozen Phase 1-8 result.

SUPERSEDES a prior same-named script found on 2026-08-25 with two confirmed defects: (1) its
"global_platt" calibration_intercept/slope columns reported the RAW pre-Platt intercept/slope
(e.g. -2.2425 for logistic), not a post-recalibration calibration metric -- independently confirmed
against results/calibration/primary_metrics_by_model.csv; (2) its subgroup-sensitivity computation
applied a Youden threshold derived for RAW probabilities to Platt-RECALIBRATED probabilities (a
scale mismatch), producing implausible near-zero sensitivities. Documented in
results/diagnostics/TEST_SET_CONTAMINATION_AUDIT.md. That prior file/output is not used as a source
for this implementation.

FITTING DATA (calibration-metric arm): OOF training predictions (primary v1 model family),
filtered per subgroup.
CALIBRATION DATA (conformal arm): conformal_calibration_ids.csv, filtered per subgroup
(proper_train_refit model family) -- the project's own designated calibration-fitting venue.
EVALUATION DATA: locked test set, both arms.
TEST LABELS USED FOR FITTING: NO.
"""
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import joblib
from scipy import stats
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
PRED_DIR = ROOT / "results" / "predictions"
DIAG_DIR = ROOT / "results" / "diagnostics"
DIAG_DIR.mkdir(parents=True, exist_ok=True)
REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PRIMARY_PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
OUTCOME = "outcome_primary_8.2kPa"
ALPHA = 0.10
RUN_TS = datetime.now(timezone.utc).isoformat()

TARGET_SUBGROUPS = [("bmi", "bmi_group_final", "Obese"), ("age", "age_group_final", "60+")]


def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def logit(p):
    p = np.clip(p, 1e-7, 1 - 1e-7)
    return np.log(p / (1 - p))


def fit_platt(raw_p, y):
    """Identical pattern to src/phase4_05_recalibration.py: unpenalized logistic on logit(p_raw)."""
    z = logit(raw_p).reshape(-1, 1)
    m = LogisticRegression(C=1e10, solver="lbfgs")
    m.fit(z, y)
    return m


def apply_platt(model, raw_p):
    z = logit(raw_p).reshape(-1, 1)
    return model.predict_proba(z)[:, 1]


def calibration_diagnostic(p, y):
    """calibration-in-the-large intercept/slope (same pattern as phase4_02_primary_metrics.py),
    plus Brier score."""
    z = logit(p).reshape(-1, 1)
    if len(np.unique(y)) < 2:
        return None, None, float(np.mean((p - y) ** 2))
    m = LogisticRegression(C=1e10, solver="lbfgs")
    m.fit(z, y)
    return float(m.intercept_[0]), float(m.coef_[0][0]), float(np.mean((p - y) ** 2))


master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])
if not cal_ids.isdisjoint(test_ids):
    raise SystemExit("FAIL: conformal calibration / test overlap -- STOP")

cov_map = master.set_index("SEQN")[["bmi_group_final", "age_group_final"]]
recal_test_global = pd.read_csv(ROOT / "results" / "calibration" / "test_set_recalibrated_predictions.csv")
baseline_subgroup_cov = pd.read_csv(ROOT / "results" / "uncertainty" / "subgroup_coverage.csv")

calib_rows = []
conformal_rows = []

for model in MODEL_NAMES:
    # ============ ARM A: calibration-metric comparison, primary v1 model family ============
    oof = pd.read_csv(PRED_DIR / f"validation_predictions_{model}.csv").join(cov_map, on="SEQN")
    test = pd.read_csv(PRED_DIR / f"test_predictions_{model}.csv").join(cov_map, on="SEQN")
    global_recal_m = recal_test_global[recal_test_global["model"] == model][["SEQN", "recalibrated_predicted_probability"]]
    test = test.merge(global_recal_m, on="SEQN", how="left")

    for dim, col, cat in TARGET_SUBGROUPS:
        oof_sg = oof[oof[col] == cat]
        n_oof_pos = int(oof_sg["true_target"].sum())
        n_oof_neg = len(oof_sg) - n_oof_pos
        test_sg = test[test[col] == cat]
        n_test = len(test_sg)
        n_test_pos = int(test_sg["true_target"].sum())

        if n_oof_pos < 10 or n_oof_neg < 10:
            calib_rows.append({
                "generated": RUN_TS, "model": model, "dimension": dim, "category": cat,
                "status": "insufficient_evidence_not_fit", "n_oof": len(oof_sg), "n_oof_positive": n_oof_pos,
            })
            continue

        platt_sg = fit_platt(oof_sg["predicted_probability"].values, oof_sg["true_target"].values)
        test_sg_recal = apply_platt(platt_sg, test_sg["predicted_probability"].values)

        before_intercept, before_slope, before_brier = calibration_diagnostic(
            test_sg["recalibrated_predicted_probability"].values, test_sg["true_target"].values)
        after_intercept, after_slope, after_brier = calibration_diagnostic(
            test_sg_recal, test_sg["true_target"].values)

        calib_rows.append({
            "generated": RUN_TS, "model": model, "dimension": dim, "category": cat,
            "status": "fit", "n_test": n_test, "n_test_positive": n_test_pos,
            "n_oof_fit": len(oof_sg), "n_oof_fit_positive": n_oof_pos,
            "before_method": "existing_global_platt_applied_to_subgroup_rows",
            "before_intercept": round(before_intercept, 6) if before_intercept is not None else None,
            "before_slope": round(before_slope, 6) if before_slope is not None else None,
            "before_brier": round(before_brier, 6),
            "after_method": "new_subgroup_specific_platt_fit_on_subgroup_oof",
            "after_intercept": round(after_intercept, 6) if after_intercept is not None else None,
            "after_slope": round(after_slope, 6) if after_slope is not None else None,
            "after_brier": round(after_brier, 6),
            "sg_platt_coef": round(float(platt_sg.coef_[0][0]), 6),
            "sg_platt_intercept": round(float(platt_sg.intercept_[0]), 6),
            "fitting_test_labels_used": "NO",
        })

    # ============ ARM B: conformal-coverage comparison, proper_train_refit model family ============
    refit = joblib.load(REFIT_DIR / f"model_{model}_proper_train_refit.joblib")
    pipe = refit["pipeline"]

    cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)
    test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
    cal_raw = pipe.predict_proba(cal_df[PRIMARY_PREDICTORS])[:, 1]
    test_raw = pipe.predict_proba(test_df[PRIMARY_PREDICTORS])[:, 1]

    for dim, col, cat in TARGET_SUBGROUPS:
        cal_mask = (cal_df[col] == cat).values
        test_mask = (test_df[col] == cat).values
        n_cal_sg = int(cal_mask.sum())
        cal_y_sg = cal_df.loc[cal_mask, OUTCOME].values
        n_cal_sg_pos = int(cal_y_sg.sum())

        baseline_row = baseline_subgroup_cov[
            (baseline_subgroup_cov["model"] == model) & (baseline_subgroup_cov["category"] == cat)
        ]
        baseline_cov = float(baseline_row["empirical_coverage"].values[0]) if len(baseline_row) else None

        if n_cal_sg_pos < 10 or (n_cal_sg - n_cal_sg_pos) < 10:
            conformal_rows.append({
                "generated": RUN_TS, "model": model, "dimension": dim, "category": cat,
                "status": "insufficient_evidence_not_fit", "n_calibration": n_cal_sg, "n_calibration_positive": n_cal_sg_pos,
                "baseline_coverage_raw_uncalibrated": baseline_cov,
            })
            continue

        platt_sg_conformal = fit_platt(cal_raw[cal_mask], cal_y_sg)
        cal_sg_recal = apply_platt(platt_sg_conformal, cal_raw[cal_mask])

        # NEW nonconformity scores, subgroup-cell-only, mirroring phase7_02's exact quantile formula
        proba_true_class = np.where(cal_y_sg == 1, cal_sg_recal, 1 - cal_sg_recal)
        scores = 1 - proba_true_class
        k = int(np.ceil((n_cal_sg + 1) * (1 - ALPHA)))
        sorted_scores = np.sort(scores)
        new_threshold = float(sorted_scores[k - 1]) if k <= n_cal_sg else np.inf

        test_sg_recal = apply_platt(platt_sg_conformal, test_raw[test_mask])
        y_test_sg = test_df.loc[test_mask, OUTCOME].values
        include_pos = (1 - test_sg_recal) <= new_threshold
        include_neg = test_sg_recal <= new_threshold
        set_size = include_pos.astype(int) + include_neg.astype(int)
        true_in_set = np.where(y_test_sg == 1, include_pos, include_neg)
        n_test_sg = int(test_mask.sum())
        covered = int(true_in_set.sum())
        new_coverage = covered / n_test_sg
        ci_lo, ci_hi = wilson_ci(covered, n_test_sg)

        conformal_rows.append({
            "generated": RUN_TS, "model": model, "dimension": dim, "category": cat,
            "status": "fit",
            "n_calibration": n_cal_sg, "n_calibration_positive": n_cal_sg_pos,
            "n_test": n_test_sg, "n_test_positive": int(y_test_sg.sum()),
            "sg_platt_intercept": round(float(platt_sg_conformal.intercept_[0]), 6),
            "sg_platt_coef": round(float(platt_sg_conformal.coef_[0][0]), 6),
            "new_conformal_quantile_level": round(k / n_cal_sg, 6),
            "new_conformal_threshold": round(new_threshold, 6) if new_threshold != np.inf else "inf",
            "baseline_coverage_raw_uncalibrated": baseline_cov,
            "coverage_after_subgroup_recalibration": round(new_coverage, 6),
            "coverage_ci_lower": round(ci_lo, 6) if ci_lo is not None else None,
            "coverage_ci_upper": round(ci_hi, 6) if ci_hi is not None else None,
            "coverage_change_pp": round((new_coverage - baseline_cov) * 100, 4) if baseline_cov is not None else None,
            "mean_set_size_after": round(float(set_size.mean()), 6),
            "singleton_rate_after": round(float((set_size == 1).mean()), 6),
            "doubleton_rate_after": round(float((set_size == 2).mean()), 6),
            "fitting_test_labels_used": "NO",
        })

pd.DataFrame(calib_rows).to_csv(DIAG_DIR / "subgroup_recalibration_metrics.csv", index=False)
pd.DataFrame(conformal_rows).to_csv(DIAG_DIR / "subgroup_recalibration_conformal_metrics.csv", index=False)
print("Wrote subgroup_recalibration_metrics.csv:", len(calib_rows), "rows")
print("Wrote subgroup_recalibration_conformal_metrics.csv:", len(conformal_rows), "rows")
print()
print(pd.DataFrame(conformal_rows)[["model", "dimension", "category", "status", "baseline_coverage_raw_uncalibrated", "coverage_after_subgroup_recalibration", "coverage_change_pp"]].to_string(index=False))
