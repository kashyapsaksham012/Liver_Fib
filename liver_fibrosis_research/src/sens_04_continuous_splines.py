"""
sens_04_continuous_splines.py
Diagnostic Analysis 1 (Three-Diagnostics Protocol Freeze, 2026-08-25): continuous BMI and Age
relationships to sensitivity, conformal coverage, calibration, and prediction-set efficiency.

SECONDARY / DIAGNOSTIC / SUPPLEMENTARY. Does not modify or replace any frozen Phase 1-8 result.

SUPERSEDES a prior same-named script found on 2026-08-25 whose docstring claimed OOF-only fitting
but whose actual code fit every spline model on `test_df` (the locked test set) directly -- a
confirmed test-set-fitting violation, documented in
results/diagnostics/TEST_SET_CONTAMINATION_AUDIT.md. That prior file/output is not used as a
source for this implementation.

Restricted cubic spline (Harrell's RCS), 4 knots at the 5th/35th/65th/95th percentiles of the
covariate's TRAINING-partition distribution, frozen in
documentation/diagnostics/THREE_DIAGNOSTICS_PROTOCOL_FREEZE.md before this script was written.
Splines are FIT exclusively on out-of-fold training predictions. The locked test set is used only
to (a) apply the already-frozen spline coefficients for a predicted curve, and (b) report purely
descriptive decile-binned empirical rates -- no fitting or decision-making occurs on test data.

TEST LABELS USED FOR FITTING: NO.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression, LinearRegression

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
PRED_DIR = ROOT / "results" / "predictions"
DIAG_DIR = ROOT / "results" / "diagnostics"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
RUN_TS = datetime.now(timezone.utc).isoformat()


def wilson_ci(k, n, level=0.95):
    if n == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def rcs_basis(x, knots):
    """Harrell's restricted cubic spline basis. Returns array (n, k-1): [x, spline_2, ..., spline_{k-1}]."""
    k = len(knots)
    x = np.asarray(x, dtype=float)
    cols = [x.copy()]

    def pos_cube(v):
        return np.where(v > 0, v, 0.0) ** 3

    t_last = knots[-1]
    t_secondlast = knots[-2]
    denom = t_last - t_secondlast
    for j in range(k - 2):
        tj = knots[j]
        term = (
            pos_cube(x - tj)
            - pos_cube(x - t_secondlast) * (t_last - tj) / denom
            + pos_cube(x - t_last) * (t_secondlast - tj) / denom
        )
        scale = (t_last - knots[0]) ** 2
        cols.append(term / scale)
    return np.column_stack(cols)


def frozen_knots(train_covariate):
    return np.percentile(train_covariate, [5, 35, 65, 95])


def decile_bins(covariate, n_bins=10):
    return np.unique(np.percentile(covariate, np.linspace(0, 100, n_bins + 1)))


master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
train_ids = set(pd.read_csv(SPLIT_DIR / "train_ids.csv")["SEQN"])
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
if master[master["SEQN"].isin(test_ids)].shape[0] != 2146:
    raise SystemExit("FAIL: test partition size mismatch -- STOP, do not proceed")

cov_map = master.set_index("SEQN")[["RIDAGEYR", "BMXBMI"]]

global_thresholds = pd.read_csv(ROOT / "results" / "tables" / "phase3_threshold_selection.csv")
name_col = "model_name" if "model_name" in global_thresholds.columns else global_thresholds.columns[0]
thr_map = global_thresholds.set_index(name_col)["threshold"]

conformal_thresholds = pd.read_csv(ROOT / "results" / "uncertainty" / "conformal_thresholds_by_model.csv").set_index("model")["threshold"]
recal_test = pd.read_csv(ROOT / "results" / "calibration" / "test_set_recalibrated_predictions.csv")
test_pred_sets = pd.read_csv(ROOT / "results" / "uncertainty" / "test_set_prediction_sets.csv")


def build_oof_frame(model):
    df = pd.read_csv(PRED_DIR / f"validation_predictions_{model}.csv")
    df = df.join(cov_map, on="SEQN")
    thr = thr_map[model]
    cth = conformal_thresholds[model]
    df["pred_positive_global_thr"] = (df["predicted_probability"] >= thr).astype(int)
    include_pos = (1 - df["predicted_probability"]) <= cth
    include_neg = df["predicted_probability"] <= cth
    df["set_size_oof"] = include_pos.astype(int) + include_neg.astype(int)
    df["true_in_set_oof"] = np.where(df["true_target"] == 1, include_pos, include_neg).astype(int)
    return df


def build_test_frame(model):
    df = pd.read_csv(PRED_DIR / f"test_predictions_{model}.csv")
    df = df.join(cov_map, on="SEQN")
    tps = test_pred_sets[test_pred_sets["model"] == model][["SEQN", "set_size", "true_in_set"]]
    df = df.merge(tps, on="SEQN", how="left")
    recal_m = recal_test[recal_test["model"] == model][["SEQN", "recalibrated_predicted_probability"]]
    df = df.merge(recal_m, on="SEQN", how="left")
    return df


def fit_binary_spline(oof_df, outcome_col, covariate_col, knots):
    X = rcs_basis(oof_df[covariate_col].values, knots)
    y = oof_df[outcome_col].values
    if len(np.unique(y)) < 2:
        return None
    model = LogisticRegression(C=1e6, max_iter=2000)
    model.fit(X, y)
    return model


def fit_linear_spline(oof_df, outcome_col, covariate_col, knots):
    X = rcs_basis(oof_df[covariate_col].values, knots)
    y = oof_df[outcome_col].values
    model = LinearRegression()
    model.fit(X, y)
    return model


def describe_deciles(test_df_, covariate_col, event_col):
    edges = decile_bins(test_df_[covariate_col], n_bins=10)
    rows = []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        mask = (test_df_[covariate_col] >= lo) & (test_df_[covariate_col] <= hi) if i == len(edges) - 2 else (test_df_[covariate_col] >= lo) & (test_df_[covariate_col] < hi)
        sub = test_df_[mask]
        n = len(sub)
        if n == 0:
            continue
        k = int(sub[event_col].sum())
        rate = k / n
        lo_ci, hi_ci = wilson_ci(k, n)
        rows.append({
            "bin_index": i, "bin_low": round(float(lo), 3), "bin_high": round(float(hi), 3),
            "n": n, "n_events": k, "rate": round(rate, 6),
            "ci_lower": round(lo_ci, 6) if lo_ci is not None else None,
            "ci_upper": round(hi_ci, 6) if hi_ci is not None else None,
            "sparse_cell": bool(k < 10 or (n - k) < 10),
        })
    return rows


all_rows = {"bmi": [], "age": []}
fine_age_rows = []

for cov_name, cov_col in [("bmi", "BMXBMI"), ("age", "RIDAGEYR")]:
    train_cov = master[master["SEQN"].isin(train_ids)][cov_col].values
    knots = frozen_knots(train_cov)

    for model in MODEL_NAMES:
        oof = build_oof_frame(model)
        test = build_test_frame(model)

        oof_pos = oof[oof["true_target"] == 1]
        sens_model = fit_binary_spline(oof_pos, "pred_positive_global_thr", cov_col, knots)
        cov_model = fit_binary_spline(oof, "true_in_set_oof", cov_col, knots)
        eff_model = fit_linear_spline(oof, "set_size_oof", cov_col, knots)

        grid = np.linspace(train_cov.min(), train_cov.max(), 40)
        Xg = rcs_basis(grid, knots)
        sens_curve = sens_model.predict_proba(Xg)[:, 1] if sens_model is not None else np.full(len(grid), np.nan)
        cov_curve = cov_model.predict_proba(Xg)[:, 1]
        eff_curve = eff_model.predict(Xg)

        thr = thr_map[model]
        test["pred_positive_global_thr"] = (test["predicted_probability"] >= thr).astype(int)
        test_pos = test[test["true_target"] == 1]

        sens_deciles = describe_deciles(test_pos, cov_col, "pred_positive_global_thr") if len(test_pos) else []
        cov_deciles = describe_deciles(test, cov_col, "true_in_set")

        edges = decile_bins(test[cov_col], n_bins=10)
        calib_rows = []
        for i in range(len(edges) - 1):
            lo, hi = edges[i], edges[i + 1]
            mask = (test[cov_col] >= lo) & (test[cov_col] <= hi) if i == len(edges) - 2 else (test[cov_col] >= lo) & (test[cov_col] < hi)
            sub = test[mask]
            if len(sub) == 0:
                continue
            calib_rows.append({
                "bin_index": i, "n": len(sub),
                "mean_recalibrated_predicted_prob": round(float(sub["recalibrated_predicted_probability"].mean()), 6),
                "observed_event_rate": round(float(sub["true_target"].mean()), 6),
                "overprediction_gap": round(float(sub["recalibrated_predicted_probability"].mean() - sub["true_target"].mean()), 6),
            })

        for gi, gval in enumerate(grid):
            all_rows[cov_name].append({
                "generated": RUN_TS, "model": model, "covariate": cov_name,
                "grid_value": round(float(gval), 4),
                "fitted_sensitivity_curve": round(float(sens_curve[gi]), 6) if not np.isnan(sens_curve[gi]) else None,
                "fitted_coverage_curve": round(float(cov_curve[gi]), 6),
                "fitted_mean_set_size_curve": round(float(eff_curve[gi]), 6),
                "knots": ";".join(f"{k:.3f}" for k in knots),
                "fitting_data": "OOF training predictions (validation_predictions_<model>.csv)",
                "test_labels_used_for_fitting": "NO",
            })

        for r in sens_deciles:
            r2 = dict(r); r2.update({"generated": RUN_TS, "model": model, "covariate": cov_name, "estimand": "sensitivity", "source": "test_set_descriptive_decile"})
            all_rows[cov_name].append(r2)
        for r in cov_deciles:
            r2 = dict(r); r2.update({"generated": RUN_TS, "model": model, "covariate": cov_name, "estimand": "coverage", "source": "test_set_descriptive_decile"})
            all_rows[cov_name].append(r2)
        for r in calib_rows:
            r2 = dict(r); r2.update({"generated": RUN_TS, "model": model, "covariate": cov_name, "estimand": "calibration_diagnostic", "source": "test_set_descriptive_decile"})
            all_rows[cov_name].append(r2)

        if cov_name == "age":
            for band_lo, band_hi, label in [(60, 69, "60-69"), (70, 80, "70-80")]:
                band_test = test[(test["RIDAGEYR"] >= band_lo) & (test["RIDAGEYR"] <= band_hi)]
                band_test_pos = band_test[band_test["true_target"] == 1]
                n = len(band_test); n_pos = int(band_test["true_target"].sum())
                if len(band_test_pos):
                    k_sens = int(band_test_pos["pred_positive_global_thr"].sum())
                    sens_rate = k_sens / len(band_test_pos)
                    s_lo, s_hi = wilson_ci(k_sens, len(band_test_pos))
                else:
                    sens_rate, s_lo, s_hi, k_sens = None, None, None, 0
                k_cov = int(band_test["true_in_set"].sum())
                cov_rate = k_cov / n if n else None
                c_lo, c_hi = wilson_ci(k_cov, n) if n else (None, None)
                fine_age_rows.append({
                    "generated": RUN_TS, "model": model, "age_band": label,
                    "n": n, "n_positive": n_pos, "n_positive_for_sensitivity": len(band_test_pos),
                    "sensitivity": round(sens_rate, 6) if sens_rate is not None else None,
                    "sensitivity_ci_lower": round(s_lo, 6) if s_lo is not None else None,
                    "sensitivity_ci_upper": round(s_hi, 6) if s_hi is not None else None,
                    "coverage": round(cov_rate, 6) if cov_rate is not None else None,
                    "coverage_ci_lower": round(c_lo, 6) if c_lo is not None else None,
                    "coverage_ci_upper": round(c_hi, 6) if c_hi is not None else None,
                    "sparse_cell": bool(len(band_test_pos) < 10 or n_pos < 10),
                    "note": "NHANES tops-codes RIDAGEYR at 80; '70-80' is the full upper range, not unbounded",
                })

pd.DataFrame(all_rows["bmi"]).to_csv(DIAG_DIR / "continuous_bmi_metrics.csv", index=False)
pd.DataFrame(all_rows["age"]).to_csv(DIAG_DIR / "continuous_age_metrics.csv", index=False)
pd.DataFrame(fine_age_rows).to_csv(DIAG_DIR / "fine_age_band_metrics.csv", index=False)

print("Wrote continuous_bmi_metrics.csv:", len(all_rows["bmi"]), "rows")
print("Wrote continuous_age_metrics.csv:", len(all_rows["age"]), "rows")
print("Wrote fine_age_band_metrics.csv:", len(fine_age_rows), "rows")
