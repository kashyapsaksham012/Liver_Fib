"""
sens_12_m4b_n0_prespecified.py
Genuinely pre-specified N0 selection for the M4b shrinkage-weighted conformal quantile, replacing
the sweep-then-declare-locked framing of `src/tradeoff_02_m4b_sensitivity_and_lock.py` (audited
and found NOT verifiable as pre-specified: `documentation/final_audit/
FINAL_NUMERICAL_AND_M4B_AUDIT.md`, Audit 2B).

PROTOCOL: `documentation/diagnostics/M4B_N0_SELECTION_PROTOCOL_FREEZE.md`, frozen before this
script was run. N0 is selected via 5-fold stratified cross-validation WITHIN the conformal
calibration split (N=1,002) only; the locked test set is used exactly once, after N0* is fixed,
for final reporting.

FITTING/SELECTION DATA: conformal_calibration_ids.csv (N=1,002) only.
EVALUATION DATA: test_ids.csv (N=2,146), touched only in the final step, after N0* is fixed.
TEST LABELS USED FOR N0 SELECTION: NO.
"""
import datetime
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
DIAG_DIR = RESULTS_DIR / "diagnostics" / "stage1"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
DIAG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PRIMARY_PREDICTORS = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
    "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD",
]
PRIMARY_OUTCOME_COL = "outcome_primary_8.2kPa"
TARGET_COVERAGE = 0.90
N0_GRID = [0, 10, 25, 50, 75, 100, 150, 200, 300, 500]  # frozen in the protocol, reused as-is
N_FOLDS = 5
CV_SEED = 42
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def platt_transform(p, intercept, slope):
    eps = 1e-7
    p_clamped = np.clip(p, eps, 1 - eps)
    logit_p = np.log(p_clamped / (1 - p_clamped))
    return 1.0 / (1.0 + np.exp(-(slope * logit_p + intercept)))


def conformal_score(y, p_hat):
    return 1.0 - np.where(y == 1, p_hat, 1.0 - p_hat)


def compute_quantile(scores, target_cov=TARGET_COVERAGE):
    n = len(scores)
    if n == 0:
        return 1.0
    k = int(np.ceil((n + 1) * target_cov))
    k = min(max(1, k), n)
    return np.sort(scores)[k - 1]


def wilson_ci(k, n, level=0.95):
    if n == 0 or np.isnan(n):
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def stratified_folds(joint_mask, n_folds, seed):
    """5-fold split stratified by joint-cell membership, without sklearn dependency issues."""
    rng = np.random.default_rng(seed)
    idx_pos = np.where(joint_mask)[0]
    idx_neg = np.where(~joint_mask)[0]
    rng.shuffle(idx_pos)
    rng.shuffle(idx_neg)
    pos_folds = np.array_split(idx_pos, n_folds)
    neg_folds = np.array_split(idx_neg, n_folds)
    folds = [np.concatenate([pos_folds[f], neg_folds[f]]) for f in range(n_folds)]
    return folds


print("=== M4b N0 SELECTION (pre-specified, calibration-only cross-validation) ===")
master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])
test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)
assert set(test_df["SEQN"]).isdisjoint(set(cal_df["SEQN"]))

y_test = test_df[PRIMARY_OUTCOME_COL].values
y_cal = cal_df[PRIMARY_OUTCOME_COL].values

cal_obese_mask = (cal_df["bmi_group_final"] == "Obese").values
cal_age60_mask = (cal_df["age_group_final"] == "60+").values
cal_joint_mask = cal_obese_mask & cal_age60_mask

test_obese_mask = (test_df["bmi_group_final"] == "Obese").values
test_age60_mask = (test_df["age_group_final"] == "60+").values
test_joint_mask = test_obese_mask & test_age60_mask

folds = stratified_folds(cal_joint_mask, N_FOLDS, CV_SEED)

model_scores = {}  # name -> {intercept, slope, cal_p (over cal_df)}
for name in MODEL_NAMES:
    refit_path = ROOT / "models" / "phase6_conformal_refit" / f"model_{name}_proper_train_refit.joblib"
    refit = joblib.load(refit_path)
    pipe = refit["pipeline"]
    oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{name}.csv")
    intercept, slope = oof_df["platt_intercept"].iloc[0], oof_df["platt_slope"].iloc[0]
    cal_raw = pipe.predict_proba(cal_df[PRIMARY_PREDICTORS])[:, 1]
    cal_p = platt_transform(cal_raw, intercept, slope)
    cal_scores_full = conformal_score(y_cal, cal_p)
    model_scores[name] = cal_scores_full

# --- Step 1-3: cross-validated coverage/drift per (model, N0) ---
cv_rows = []
for n0 in N0_GRID:
    for name in MODEL_NAMES:
        cal_scores_full = model_scores[name]
        fold_covs, fold_drifts = [], []
        for f in range(N_FOLDS):
            val_idx = folds[f]
            fit_idx = np.concatenate([folds[g] for g in range(N_FOLDS) if g != f])

            fit_scores = cal_scores_full[fit_idx]
            fit_obese = cal_obese_mask[fit_idx]
            fit_age60 = cal_age60_mask[fit_idx]
            fit_joint = cal_joint_mask[fit_idx]

            q_m1 = compute_quantile(fit_scores, TARGET_COVERAGE)
            q_obese = compute_quantile(fit_scores[fit_obese], TARGET_COVERAGE) if fit_obese.sum() > 0 else q_m1
            q_age60 = compute_quantile(fit_scores[fit_age60], TARGET_COVERAGE) if fit_age60.sum() > 0 else q_m1
            n_joint_fit = int(fit_joint.sum())
            q_joint = compute_quantile(fit_scores[fit_joint], TARGET_COVERAGE) if n_joint_fit > 0 else q_m1
            q_envelope = max(q_obese, q_age60)
            w = n_joint_fit / (n_joint_fit + n0) if (n_joint_fit + n0) > 0 else 0.0
            q_m4b = w * q_joint + (1.0 - w) * q_envelope

            val_scores = cal_scores_full[val_idx]
            val_obese = cal_obese_mask[val_idx]
            val_age60 = cal_age60_mask[val_idx]
            val_joint = cal_joint_mask[val_idx]

            thresh_m1_val = np.full(len(val_idx), q_m1)
            thresh_m4b_val = np.full(len(val_idx), q_m1)
            thresh_m4b_val[val_obese] = q_obese
            thresh_m4b_val[val_age60] = q_age60
            thresh_m4b_val[val_joint] = q_m4b

            m1_cov_val = float((val_scores <= thresh_m1_val).mean())
            m4b_cov_val = float((val_scores <= thresh_m4b_val).mean())
            drift_val = (m4b_cov_val - m1_cov_val) * 100.0

            if val_joint.sum() > 0:
                inter_cov_val = float((val_scores[val_joint] <= thresh_m4b_val[val_joint]).mean())
                fold_covs.append(inter_cov_val)
            fold_drifts.append(drift_val)

        cv_coverage = float(np.mean(fold_covs)) if fold_covs else np.nan
        cv_drift = float(np.mean(fold_drifts))
        cv_rows.append({
            "N0": n0, "model": name,
            "cv_intersectional_coverage": round(cv_coverage, 4) if not np.isnan(cv_coverage) else np.nan,
            "cv_marginal_drift_pp": round(cv_drift, 2),
            "cv_meets_target": (not np.isnan(cv_coverage)) and cv_coverage >= 0.90 and abs(cv_drift) <= 5.0,
        })

cv_df = pd.DataFrame(cv_rows)
cv_df.to_csv(DIAG_DIR / "m4b_n0_cv_selection.csv", index=False)
print(f"Saved CV selection table: {DIAG_DIR / 'm4b_n0_cv_selection.csv'}")

# --- Step 4-5: selection rule ---
selected_n0 = None
for n0 in N0_GRID:  # ascending, so first hit is the smallest qualifying N0
    subset = cv_df[cv_df["N0"] == n0]
    if subset["cv_meets_target"].all() and len(subset) == len(MODEL_NAMES):
        selected_n0 = n0
        break

fallback_used = False
if selected_n0 is None:
    fallback_used = True
    penalties = {}
    for n0 in N0_GRID:
        subset = cv_df[cv_df["N0"] == n0]
        worst = 0.0
        for _, row in subset.iterrows():
            cov = row["cv_intersectional_coverage"]
            drift = row["cv_marginal_drift_pp"]
            if np.isnan(cov):
                continue
            pen = max(0.0, 0.90 - cov) + max(0.0, abs(drift) - 5.0) / 5.0
            worst = max(worst, pen)
        penalties[n0] = worst
    selected_n0 = min(penalties, key=penalties.get)

print(f"\nSelected N0* = {selected_n0} (fallback_used={fallback_used})")
print("Per the frozen protocol, this N0 is now applied ONCE to the full calibration set and "
      "evaluated ONCE on the locked test set.")

# --- Step 6: final fit on full calibration set, evaluate once on test set ---
final_rows = []
for name in MODEL_NAMES:
    cal_scores_full = model_scores[name]
    refit_path = ROOT / "models" / "phase6_conformal_refit" / f"model_{name}_proper_train_refit.joblib"
    refit = joblib.load(refit_path)
    pipe = refit["pipeline"]
    oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{name}.csv")
    intercept, slope = oof_df["platt_intercept"].iloc[0], oof_df["platt_slope"].iloc[0]
    test_raw = pipe.predict_proba(test_df[PRIMARY_PREDICTORS])[:, 1]
    test_p = platt_transform(test_raw, intercept, slope)
    test_scores = conformal_score(y_test, test_p)

    q_m1 = compute_quantile(cal_scores_full, TARGET_COVERAGE)
    q_obese = compute_quantile(cal_scores_full[cal_obese_mask], TARGET_COVERAGE)
    q_age60 = compute_quantile(cal_scores_full[cal_age60_mask], TARGET_COVERAGE)
    n_joint_cal = int(cal_joint_mask.sum())
    q_joint = compute_quantile(cal_scores_full[cal_joint_mask], TARGET_COVERAGE)
    q_envelope = max(q_obese, q_age60)
    w = n_joint_cal / (n_joint_cal + selected_n0) if (n_joint_cal + selected_n0) > 0 else 0.0
    q_m4b = w * q_joint + (1.0 - w) * q_envelope

    thresh_m1 = np.full(len(test_df), q_m1)
    thresh_m4b = np.full(len(test_df), q_m1)
    thresh_m4b[test_obese_mask] = q_obese
    thresh_m4b[test_age60_mask] = q_age60
    thresh_m4b[test_joint_mask] = q_m4b

    m1_cov = float((test_scores <= thresh_m1).mean())
    covered = test_scores <= thresh_m4b
    marg_cov = float(covered.mean())
    marg_drift_pp = (marg_cov - m1_cov) * 100.0
    inter_cov = float(covered[test_joint_mask].mean())
    k_inter = int(covered[test_joint_mask].sum())
    n_inter = int(test_joint_mask.sum())
    lo, hi = wilson_ci(k_inter, n_inter)

    final_rows.append({
        "generated": TIMESTAMP,
        "model": name,
        "N0_selected": selected_n0,
        "selection_method": "5fold_CV_on_calibration_only" if not fallback_used else "5fold_CV_fallback_penalty",
        "shrinkage_weight_w": round(w, 4),
        "q_joint_cal": round(q_joint, 4),
        "q_envelope_cal": round(q_envelope, 4),
        "q_m4b_cal": round(q_m4b, 4),
        "intersectional_coverage": round(inter_cov, 4),
        "intersectional_ci_lower": round(float(lo), 4),
        "intersectional_ci_upper": round(float(hi), 4),
        "marginal_coverage": round(marg_cov, 4),
        "marginal_drift_pp": round(marg_drift_pp, 2),
        "meets_target_90": (inter_cov >= 0.90) and (abs(marg_drift_pp) <= 5.0),
        "test_labels_used_for_n0_selection": "NO",
    })
    print(f"{name}: N0*={selected_n0} intersectional_coverage={inter_cov:.4f} drift={marg_drift_pp:.2f}pp")

final_df = pd.DataFrame(final_rows)
out_path = TABLES_DIR / "m4b_prespecified_n0_final_results.csv"
final_df.to_csv(out_path, index=False)
print(f"\nSaved final (single-evaluation) results: {out_path}")
