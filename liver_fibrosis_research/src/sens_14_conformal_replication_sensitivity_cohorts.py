"""
sens_14_conformal_replication_sensitivity_cohorts.py

Conformal subgroup-coverage REPLICATION on the CAND_2 and CAND_3 sensitivity cohorts
(Protocol Amendment #16). Amendment #13 executed discrimination / calibration / fairness for
CAND_2 and CAND_3 and explicitly DEFERRED the conformal replication as documented future work.
This script closes that gap.

The primary study's split-conformal architecture (Phase 6, src/phase6_02..04) is reproduced
UNCHANGED on each sensitivity cohort:
  - fresh 70/30 stratified split (seed=42) -- identical to sens_02 (Amendment #13)
  - 80/20 stratified split (seed=42) of the training partition -> proper-train / conformal-cal
    (Phase 6 Amendment #4 design)
  - refit the 5 model families on proper-train ONLY, with the frozen Phase 3 best_params
    (no hyperparameter search); CAND_3 keeps its 12-predictor fasting-extended architecture
  - nonconformity score 1 - P(true class | x); threshold = k-th smallest calibration score,
    k = ceil((n_cal + 1) * (1 - alpha)), alpha = 0.10 (frozen)
  - prediction sets on the cohort's own locked test; marginal + BMI + Age subgroup coverage;
    Wilson 95% CIs; one-sample binomial test vs 0.90; BH-FDR within each (model x dimension)
    family (Phase 6 Amendment #11 convention)

Pre-specified targets: BMI-Obese and Age-60+ (the two subgroups that under-cover on CAND_1).
Other categories are computed for complete BH families and context, not for new claims.
The locked CAND_1 Phase 3/6 test set is never loaded here. No CAND_1 artifact is modified.

Outputs:
  results/sensitivity/conformal_replication_marginal.csv
  results/sensitivity/conformal_replication_subgroup.csv
  results/sensitivity/conformal_replication_thresholds.csv
  results/sensitivity/conformal_replication_lineage.json
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import (MODEL_DIR, MODEL_NAMES, PRIMARY_OUTCOME_COL, PROC_DIR,
                           RANDOM_SEED, ROOT, TRAIN_FRACTION)

RESULTS_DIR = ROOT / "results" / "sensitivity"
TARGET_COVERAGE = 0.90
ALPHA = 1 - TARGET_COVERAGE
CI_LEVEL = 0.95
CALIB_FRACTION = 0.20  # of the training partition -> conformal-calibration (Phase 6 Amendment #4)

PRIMARY_PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL",
                      "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
FASTING_EXTRA = ["LBXGLU", "LBXTR"]

COHORTS = [
    ("CAND_2", "analysis_dataset_cand2_relaxed_elastography.parquet", PRIMARY_PREDICTORS, 7639),
    ("CAND_3", "analysis_dataset_secondary.parquet", PRIMARY_PREDICTORS + FASTING_EXTRA, 3582),
]
TARGETS = {("bmi", "Obese"), ("age", "60+")}

_best_params = {}
for _n in MODEL_NAMES:
    _best_params[_n] = joblib.load(MODEL_DIR / f"model_{_n}_v1.joblib")["best_params"]


def build_pipeline(name, scale, predictors):
    steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scale", StandardScaler()))
    pre = ColumnTransformer([("num", Pipeline(steps), predictors)])
    if name == "logistic":
        est = LogisticRegression(class_weight="balanced", solver="lbfgs", max_iter=2000,
                                 random_state=RANDOM_SEED)
    elif name == "random_forest":
        est = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1)
    elif name == "xgboost":
        est = xgb.XGBClassifier(eval_metric="logloss", random_state=RANDOM_SEED, n_jobs=-1)
    elif name == "lightgbm":
        est = lgb.LGBMClassifier(random_state=RANDOM_SEED, n_jobs=-1, verbosity=-1)
    elif name == "mlp":
        est = MLPClassifier(random_state=RANDOM_SEED, max_iter=1000, early_stopping=True)
    else:
        raise ValueError(name)
    est.set_params(**{k.replace("est__", ""): v for k, v in _best_params[name].items()})
    return Pipeline([("pre", pre), ("est", est)])


def wilson_ci(k, n, level=CI_LEVEL):
    if n == 0:
        return (None, None)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    phat = k / n
    denom = 1 + z ** 2 / n
    center = (phat + z ** 2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z ** 2 / (4 * n ** 2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def bh_fdr(pvals):
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(ranked, 0, 1)
    return out


def run_cohort(cohort, parquet, predictors, expected_n):
    df = pd.read_parquet(PROC_DIR / parquet)
    if len(df) != expected_n:
        sys.exit(f"STOP: {cohort} N={len(df)}, expected {expected_n}")
    y_all = df[PRIMARY_OUTCOME_COL].values

    train_df, test_df = train_test_split(df, test_size=1 - TRAIN_FRACTION,
                                         stratify=y_all, random_state=RANDOM_SEED)
    proper_df, calib_df = train_test_split(train_df, test_size=CALIB_FRACTION,
                                           stratify=train_df[PRIMARY_OUTCOME_COL],
                                           random_state=RANDOM_SEED)
    proper_df = proper_df.reset_index(drop=True)
    calib_df = calib_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)
    print(f"\n=== {cohort}: N={len(df)} | proper-train={len(proper_df)} "
          f"calib={len(calib_df)} test={len(test_df)} | test prev="
          f"{test_df[PRIMARY_OUTCOME_COL].mean():.4f} ===")

    y_proper = proper_df[PRIMARY_OUTCOME_COL].values
    y_calib = calib_df[PRIMARY_OUTCOME_COL].values
    y_test = test_df[PRIMARY_OUTCOME_COL].values
    n_cal = len(calib_df)
    k = int(np.ceil((n_cal + 1) * (1 - ALPHA)))

    thr_rows, marg_rows, sub_rows = [], [], []
    for name in MODEL_NAMES:
        scale = name in ("logistic", "mlp")
        pipe = build_pipeline(name, scale, predictors)
        if name in ("xgboost", "lightgbm"):
            n_pos, n_neg = int(y_proper.sum()), int((y_proper == 0).sum())
            pipe.named_steps["est"].set_params(scale_pos_weight=n_neg / n_pos)
        pipe.fit(proper_df[predictors], y_proper)

        p_cal = pipe.predict_proba(calib_df[predictors])[:, 1]
        scores = 1 - np.where(y_calib == 1, p_cal, 1 - p_cal)
        sorted_scores = np.sort(scores)
        threshold = float("inf") if k > n_cal else float(sorted_scores[k - 1])
        thr_rows.append({"cohort": cohort, "model": name, "calibration_n": n_cal,
                         "calibration_positives": int(y_calib.sum()),
                         "quantile_k": k, "quantile_level": round(k / n_cal, 6),
                         "threshold": round(threshold, 6)})

        p_test = pipe.predict_proba(test_df[predictors])[:, 1]
        include_pos = (1 - p_test) <= threshold
        include_neg = p_test <= threshold
        set_size = include_pos.astype(int) + include_neg.astype(int)
        true_in_set = np.where(y_test == 1, include_pos, include_neg)

        n = len(test_df)
        cov = int(true_in_set.sum()) / n
        lo, hi = wilson_ci(int(true_in_set.sum()), n)
        marg_rows.append({"cohort": cohort, "model": name, "n": n,
                          "n_positive": int(y_test.sum()), "target_coverage": TARGET_COVERAGE,
                          "empirical_coverage": round(cov, 6),
                          "ci_lower": round(lo, 6), "ci_upper": round(hi, 6),
                          "coverage_minus_target": round(cov - TARGET_COVERAGE, 6),
                          "mean_set_size": round(float(set_size.mean()), 6),
                          "singleton_rate": round(float((set_size == 1).mean()), 6),
                          "doubleton_rate": round(float((set_size == 2).mean()), 6),
                          "empty_set_rate": round(float((set_size == 0).mean()), 6),
                          "threshold_used": round(threshold, 6)})

        for dim, col in [("bmi", "bmi_group_final"), ("age", "age_group_final")]:
            cats = [c for c in test_df[col].dropna().unique()]
            raw_p, staged = [], []
            for cat in cats:
                m = (test_df[col].values == cat)
                sn = int(m.sum())
                sy = y_test[m]
                sc = int(true_in_set[m].sum())
                scov = sc / sn if sn else None
                slo, shi = wilson_ci(sc, sn)
                pv = stats.binomtest(sc, sn, TARGET_COVERAGE).pvalue if sn else None
                raw_p.append(pv if pv is not None else 1.0)
                staged.append({
                    "cohort": cohort, "model": name, "dimension": dim, "category": cat,
                    "is_prespecified_target": (dim, cat) in TARGETS,
                    "n": sn, "n_positive": int((sy == 1).sum()), "n_negative": int((sy == 0).sum()),
                    "empirical_coverage": round(scov, 6) if scov is not None else None,
                    "ci_lower": round(slo, 6) if slo is not None else None,
                    "ci_upper": round(shi, 6) if shi is not None else None,
                    "ci_excludes_target": (shi is not None and shi < TARGET_COVERAGE)
                                          or (slo is not None and slo > TARGET_COVERAGE),
                    "coverage_minus_target": round(scov - TARGET_COVERAGE, 6) if scov is not None else None,
                    "raw_p_binomial_vs_90pct": pv,
                })
            adj = bh_fdr(raw_p)
            for s, a in zip(staged, adj):
                s["bh_fdr_adjusted_p"] = round(float(a), 6)
                s["significant_after_fdr_0.05"] = bool(a < 0.05)
                sub_rows.append(s)

    return thr_rows, marg_rows, sub_rows


def main():
    all_thr, all_marg, all_sub = [], [], []
    for cohort, parquet, predictors, n in COHORTS:
        t, m, s = run_cohort(cohort, parquet, predictors, n)
        all_thr += t
        all_marg += m
        all_sub += s

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_thr).to_csv(RESULTS_DIR / "conformal_replication_thresholds.csv", index=False)
    pd.DataFrame(all_marg).to_csv(RESULTS_DIR / "conformal_replication_marginal.csv", index=False)
    pd.DataFrame(all_sub).to_csv(RESULTS_DIR / "conformal_replication_subgroup.csv", index=False)

    tgt = pd.DataFrame([r for r in all_sub if r["is_prespecified_target"]])
    print("\n--- Pre-specified targets (BMI-Obese, Age-60+) ---")
    print(tgt[["cohort", "model", "dimension", "category", "n", "empirical_coverage",
               "ci_lower", "ci_upper", "ci_excludes_target", "bh_fdr_adjusted_p"]].to_string(index=False))

    lineage = {
        "analysis": "Conformal subgroup-coverage replication on CAND_2 and CAND_3 (Amendment #16)",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script": "src/sens_14_conformal_replication_sensitivity_cohorts.py",
        "mirrors": "src/phase6_02_conformal_refit.py, phase6_03_conformal_calibration.py, phase6_04_final_test_touch.py",
        "method": {
            "split": "fresh 70/30 stratified (seed=42), then 80/20 stratified (seed=42) of train -> proper-train/conformal-cal",
            "refit": "5 frozen model families on proper-train only, frozen Phase 3 best_params, no search",
            "nonconformity_score": "1 - P(true class | x)",
            "threshold": "k-th smallest calibration score, k = ceil((n_cal+1)*(1-alpha)), alpha=0.10",
            "inference": "Wilson 95% CI; one-sample binomial vs 0.90; BH-FDR within each (model x dimension) family",
        },
        "prespecified_targets": ["BMI-Obese", "Age-60+"],
        "cohorts": {c[0]: c[1] for c in COHORTS},
        "not_done": [
            "8.0 kPa conformal replication -- ALREADY EXECUTED (BMI-investigation Phase 6, "
            "results/fairness_bmi_investigation/phase6_8kpa_robustness/phase6_8kpa_conformal_results.csv)",
            "No CAND_1 artifact loaded or modified", "No hyperparameter search", "No FDR pooling across cohorts",
        ],
        "outputs": ["results/sensitivity/conformal_replication_marginal.csv",
                    "results/sensitivity/conformal_replication_subgroup.csv",
                    "results/sensitivity/conformal_replication_thresholds.csv"],
    }
    (RESULTS_DIR / "conformal_replication_lineage.json").write_text(json.dumps(lineage, indent=2))
    print("\nSaved results/sensitivity/conformal_replication_{marginal,subgroup,thresholds}.csv + _lineage.json")


if __name__ == "__main__":
    main()
