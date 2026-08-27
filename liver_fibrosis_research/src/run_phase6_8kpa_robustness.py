"""Phase 6: fully retrained 8.0-kPa robustness pipeline.

This is intentionally a separate namespace and does not write any pre-existing
Phase 3-8 artifact.  The locked test set is opened only after the pre-test
selection manifest has been written.
"""
from __future__ import annotations

import hashlib
import json
import pickle
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import (  # noqa: E402
    MODEL_DIR,
    MODEL_NAMES,
    N_CV_FOLDS,
    PRIMARY_PREDICTORS,
    RANDOM_SEED,
    SPLIT_DIR,
)
from phase3_05_train_and_tune import build_pipeline  # noqa: E402
from phase5_common import (  # noqa: E402
    RACE_MAP_RIDRETH3,
    SEX_MAP,
    bin_age,
    bin_bmi,
    precision_tier,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "fairness_bmi_investigation" / "phase6_8kpa_robustness"
FIG = OUT / "phase6_8kpa_figures"
DOC = ROOT / "documentation" / "fairness_bmi_investigation"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
DOC.mkdir(parents=True, exist_ok=True)

TARGET_COVERAGE = 0.90
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 42
CI_LEVEL = 0.95
EPS = 1e-12
MANIFEST_PATH = OUT / "phase6_8kpa_manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def logit(p):
    p = np.clip(np.asarray(p), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-np.asarray(z)))


def cal_in_the_large(y, p):
    reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
    reg.fit(logit(p).reshape(-1, 1), y)
    return float(reg.intercept_[0]), float(reg.coef_[0][0])


def youden_threshold(y, p):
    fpr, tpr, thresholds = roc_curve(y, p)
    return float(thresholds[np.argmax(tpr - fpr)])


def wilson(k, n):
    if n == 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - (1 - CI_LEVEL) / 2)
    phat = k / n
    den = 1 + z * z / n
    ctr = (phat + z * z / (2 * n)) / den
    half = z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / den
    return (max(0.0, ctr - half), min(1.0, ctr + half))


def bootstrap_metric(y, p, yhat, metric, rng):
    values = []
    for _ in range(BOOTSTRAP_N):
        idx = rng.integers(0, len(y), len(y))
        yb, pb, hb = y[idx], p[idx], yhat[idx]
        if metric == "auc":
            if len(np.unique(yb)) > 1:
                values.append(roc_auc_score(yb, pb))
        elif metric == "sensitivity":
            pos = yb == 1
            if pos.sum():
                values.append(float(hb[pos].mean()))
    if not values:
        return (np.nan, np.nan)
    return tuple(np.percentile(values, [2.5, 97.5]))


def ece(y, p):
    try:
        bins = pd.qcut(p, q=10, duplicates="drop")
    except ValueError:
        return np.nan
    d = pd.DataFrame({"y": y, "p": p, "bin": bins})
    g = d.groupby("bin", observed=True).agg(n=("y", "size"), p=("p", "mean"), y=("y", "mean"))
    return float((g["n"] / len(d) * (g["p"] - g["y"]).abs()).sum())


def write_csv(name, frame):
    path = OUT / name
    frame.to_csv(path, index=False)
    return path


def source_hashes():
    paths = [
        ROOT / "data" / "processed" / "analysis_dataset_primary.parquet",
        ROOT / "data" / "interim" / "nhanes_master_phase1.parquet",
        ROOT / "data" / "processed" / "splits" / "proper_train_ids.csv",
        ROOT / "data" / "processed" / "splits" / "conformal_calibration_ids.csv",
        ROOT / "src" / "phase3_common.py",
        ROOT / "src" / "phase3_05_train_and_tune.py",
        ROOT / "src" / "phase5_common.py",
        ROOT / "documentation" / "phase2" / "uncertainty_protocol.md",
        ROOT / "documentation" / "phase2" / "evaluation_metrics_protocol.md",
        ROOT / "documentation" / "phase3" / "test_set_lock.md",
    ]
    result = {}
    for p in paths:
        result[str(p.relative_to(ROOT))] = sha256(p) if p.exists() else "NOT FOUND IN REPOSITORY"
    return result


def main():
    started = time.time()
    generated = datetime.now(timezone.utc).isoformat()

    # No test IDs, test metadata, test outcomes, or test predictions are read
    # before this manifest is written.
    manifest = {
        "analysis": "Phase 6 FULL 8.0-kPa ROBUSTNESS PIPELINE",
        "generated_utc": generated,
        "repository_root": str(ROOT),
        "namespace": str(OUT.relative_to(ROOT)),
        "status_before_test_touch": "PROTOCOL_AND_SELECTION_NOT_YET_COMPLETE",
        "outcome_definition": "valid VCTE (LUAXSTAT==1) AND LUXSMED>=8.0 kPa",
        "primary_outcome_definition": "valid VCTE (LUAXSTAT==1) AND LUXSMED>=8.2 kPa",
        "predictors": PRIMARY_PREDICTORS,
        "models": MODEL_NAMES,
        "random_seed": RANDOM_SEED,
        "cv": f"{N_CV_FOLDS}-fold StratifiedKFold(shuffle=True, random_state={RANDOM_SEED})",
        "development_protocol": "proper_train only for OOF, final fit; conformal_calibration only for split-conformal q",
        "calibration_protocol": "approved OOF Platt transform: logistic regression of y on logit(raw probability)",
        "conformal_protocol": "binary split-conformal score 1-P(true class), finite-sample corrected 90% quantile",
        "threshold_protocol": "Youden J from development OOF predictions; no test-driven selection",
        "test_protocol": "locked test set read exactly once after this manifest and all selections are frozen",
        "test_access_sequence": ["NOT ACCESSED BEFORE MANIFEST"],
        "preexisting_artifacts": {
            "primary_8p2_results": "results/tables/phase3_overall_discrimination.csv",
            "primary_8p2_calibration": "results/calibration/test_set_calibration_final.csv",
            "primary_8p2_fairness": "results/fairness/subgroup_discrimination_metrics.csv",
            "primary_8p2_conformal": "results/uncertainty/subgroup_coverage.csv",
        },
        "source_hashes": source_hashes(),
        "missing_lineage_links": {
            "frozen_8p2_protocol_commit": "NOT FOUND IN REPOSITORY",
            "frozen_8p2_model_artifact_manifest": "NOT FOUND IN REPOSITORY",
        },
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "working_directory_required": str(ROOT),
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    # Construct the new labels independently from the interim VCTE source.
    primary = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
    interim = pd.read_parquet(ROOT / "data" / "interim" / "nhanes_master_phase1.parquet",
                              columns=["SEQN", "LUAXSTAT", "LUXSMED"])
    labels = primary[["SEQN", "outcome_primary_8.2kPa"]].merge(interim, on="SEQN", how="left", validate="one_to_one")
    valid = labels["LUAXSTAT"].eq(1) & labels["LUXSMED"].notna()
    labels["outcome_8.0kPa_new"] = (valid & (labels["LUXSMED"] >= 8.0)).astype(int)
    labels["outcome_8.2kPa_rederived"] = (valid & (labels["LUXSMED"] >= 8.2)).astype(int)
    if labels["outcome_8.2kPa_rederived"].tolist() != primary["outcome_primary_8.2kPa"].tolist():
        raise RuntimeError("8.2 label re-derivation does not match the frozen primary labels")
    if not (labels["outcome_8.0kPa_new"].values == primary["outcome_sensitivity_8.0kPa"].values).all():
        raise RuntimeError("independently derived 8.0 labels do not match the existing sensitivity column")

    n = len(labels)
    pos80 = int(labels["outcome_8.0kPa_new"].sum())
    pos82 = int(labels["outcome_8.2kPa_rederived"].sum())
    changed = int((labels["outcome_8.0kPa_new"] != labels["outcome_8.2kPa_rederived"]).sum())
    cohort_row = {
        "cohort": "CAND_1 quality-valid adult broad-lab cohort",
        "n": n,
        "valid_vcte_n": int(valid.sum()),
        "outcome_8.2_positive_n": pos82,
        "outcome_8.2_prevalence_pct": round(100 * pos82 / n, 6),
        "outcome_8.0_positive_n": pos80,
        "outcome_8.0_prevalence_pct": round(100 * pos80 / n, 6),
        "labels_differ_n": changed,
        "labels_differ_pct": round(100 * changed / n, 6),
        "new_outcome_source": "interim/nhanes_master_phase1.parquet: LUAXSTAT==1 and LUXSMED>=8.0",
        "eight_point_two_source": "interim/nhanes_master_phase1.parquet: LUAXSTAT==1 and LUXSMED>=8.2",
        "existing_sensitivity_column_agrees": True,
    }
    write_csv("phase6_8kpa_cohort_label_audit.csv", pd.DataFrame([cohort_row]))

    label_map = labels.set_index("SEQN")["outcome_8.0kPa_new"]
    primary = primary.copy()
    primary["outcome_8.0kPa_new"] = primary["SEQN"].map(label_map).astype(int)
    proper_ids = pd.read_csv(SPLIT_DIR / "proper_train_ids.csv")["SEQN"]
    cal_ids = pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"]
    proper = primary[primary.SEQN.isin(proper_ids)].reset_index(drop=True)
    cal = primary[primary.SEQN.isin(cal_ids)].reset_index(drop=True)
    if len(proper) != 4005 or len(cal) != 1002 or set(proper.SEQN) & set(cal.SEQN):
        raise RuntimeError("development partition integrity failure")

    best_params = {}
    for model in MODEL_NAMES:
        artifact = joblib.load(MODEL_DIR / f"model_{model}_v1.joblib")
        best_params[model] = artifact["best_params"]

    cv = StratifiedKFold(n_splits=N_CV_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    oof_rows, dev_rows, conformal_rows = [], [], []
    fitted, thresholds, platt = {}, {}, {}
    for model in MODEL_NAMES:
        y = proper["outcome_8.0kPa_new"].to_numpy()
        n_pos, n_neg = int(y.sum()), int((y == 0).sum())
        pipe, _, _, _ = build_pipeline(model, n_neg, n_pos)
        pipe.set_params(**best_params[model])
        oof = cross_val_predict(pipe, proper[PRIMARY_PREDICTORS], y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
        threshold = youden_threshold(y, oof)
        intercept, slope = cal_in_the_large(y, oof)
        thresholds[model] = threshold
        platt[model] = (intercept, slope)
        oof_rows.append(pd.DataFrame({
            "model": model, "SEQN": proper.SEQN, "true_target_8.0kPa": y,
            "raw_oof_probability": oof, "oof_classification_threshold": threshold,
            "platt_intercept": intercept, "platt_slope": slope,
        }))

        final_pipe, _, _, _ = build_pipeline(model, n_neg, n_pos)
        final_pipe.set_params(**best_params[model])
        final_pipe.fit(proper[PRIMARY_PREDICTORS], y)
        fitted[model] = final_pipe
        cal_p = final_pipe.predict_proba(cal[PRIMARY_PREDICTORS])[:, 1]
        y_cal = cal["outcome_8.0kPa_new"].to_numpy()
        score = 1 - np.where(y_cal == 1, cal_p, 1 - cal_p)
        k = int(np.ceil((len(score) + 1) * TARGET_COVERAGE))
        q = float(np.sort(score)[k - 1]) if k <= len(score) else float("inf")
        conformal_rows.append({
            "model": model, "proper_train_n": len(proper), "proper_train_positive_n": n_pos,
            "conformal_calibration_n": len(cal), "conformal_calibration_positive_n": int(y_cal.sum()),
            "target_coverage": TARGET_COVERAGE, "finite_sample_k": k,
            "quantile_level": k / len(score) if k <= len(score) else 1.0,
            "conformal_threshold": q, "score_definition": "1-P(true class)",
        })
        dev_rows.append({
            "model": model, "proper_train_n": len(proper), "proper_train_positive_n": n_pos,
            "proper_train_negative_n": n_neg, "best_params_source": f"models/phase3/model_{model}_v1.joblib",
            "best_params": json.dumps(best_params[model], default=str, sort_keys=True),
            "threshold": threshold, "platt_intercept": intercept, "platt_slope": slope,
            "oof_auc": roc_auc_score(y, oof), "model_pickle_sha256": hashlib.sha256(pickle.dumps(final_pipe)).hexdigest(),
            "test_used_for_selection": False,
        })

    write_csv("phase6_8kpa_oof_predictions.csv", pd.concat(oof_rows, ignore_index=True))
    write_csv("phase6_8kpa_calibration_development.csv", pd.DataFrame(dev_rows))
    conformal_df = pd.DataFrame(conformal_rows)
    write_csv("phase6_8kpa_conformal_calibration.csv", conformal_df)

    # Freeze all selections, still before any test ID or test metadata is read.
    manifest.update({
        "status_before_test_touch": "FROZEN",
        "selection_frozen_utc": datetime.now(timezone.utc).isoformat(),
        "selection_manifest_statement": "All model configurations, OOF thresholds, OOF Platt parameters, and conformal thresholds frozen before test access.",
        "development_partitions": {
            "proper_train_ids_sha256": sha256(SPLIT_DIR / "proper_train_ids.csv"),
            "conformal_calibration_ids_sha256": sha256(SPLIT_DIR / "conformal_calibration_ids.csv"),
            "proper_train_n": len(proper), "conformal_calibration_n": len(cal),
        },
        "frozen_selections": {
            model: {
                "best_params": best_params[model],
                "oof_threshold": thresholds[model],
                "platt_intercept": platt[model][0],
                "platt_slope": platt[model][1],
                "conformal_threshold": float(conformal_df.loc[conformal_df.model == model, "conformal_threshold"].iloc[0]),
            } for model in MODEL_NAMES
        },
        "test_access_sequence": ["NOT ACCESSED BEFORE MANIFEST", "ACCESS AUTHORIZED NOW"],
    })
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, default=str))

    # The sole official test touch begins here.
    test_ids = pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"]
    test = primary[primary.SEQN.isin(test_ids)].reset_index(drop=True)
    if len(test) != 2146 or set(test.SEQN) & set(proper.SEQN) or set(test.SEQN) & set(cal.SEQN):
        raise RuntimeError("locked test partition integrity failure")
    test["_sex"] = test.RIAGENDR.map(SEX_MAP)
    test["_race"] = test.RIDRETH3.map(RACE_MAP_RIDRETH3)
    test["_age"] = test.RIDAGEYR.map(bin_age)
    test["_bmi"] = test.BMXBMI.map(bin_bmi)
    y_test = test["outcome_8.0kPa_new"].to_numpy()
    test_rows, cal_test_rows, fair_rows, conf_rows = [], [], [], []
    prediction_store = {}
    conformal_thresholds = conformal_df.set_index("model")["conformal_threshold"].to_dict()
    for model in MODEL_NAMES:
        pipe = fitted[model]
        p = pipe.predict_proba(test[PRIMARY_PREDICTORS])[:, 1]
        yhat = (p >= thresholds[model]).astype(int)
        prediction_store[model] = (p, yhat)
        auc = roc_auc_score(y_test, p)
        ap = average_precision_score(y_test, p)
        tp = int(((y_test == 1) & (yhat == 1)).sum())
        fn = int(((y_test == 1) & (yhat == 0)).sum())
        tn = int(((y_test == 0) & (yhat == 0)).sum())
        fp = int(((y_test == 0) & (yhat == 1)).sum())
        rng = np.random.default_rng(BOOTSTRAP_SEED)
        auc_lo, auc_hi = bootstrap_metric(y_test, p, yhat, "auc", rng)
        sens_lo, sens_hi = bootstrap_metric(y_test, p, yhat, "sensitivity", rng)
        test_rows.append({
            "model": model, "n": len(test), "positive_n": int(y_test.sum()),
            "prevalence_pct": 100 * y_test.mean(), "threshold": thresholds[model],
            "roc_auc": auc, "roc_auc_ci_lower": auc_lo, "roc_auc_ci_upper": auc_hi,
            "pr_auc": ap, "sensitivity": tp / (tp + fn), "sensitivity_ci_lower": sens_lo,
            "sensitivity_ci_upper": sens_hi, "specificity": tn / (tn + fp),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn, "bootstrap_n": BOOTSTRAP_N,
            "test_used_for_selection": False,
        })
        intercept_raw, slope_raw = cal_in_the_large(y_test, p)
        pint, pslope = platt[model]
        p_recal = sigmoid(pint + pslope * logit(p))
        ri, rs = cal_in_the_large(y_test, p_recal)
        for variant, probs, ci, sl in [
            ("raw", p, intercept_raw, slope_raw),
            ("recalibrated", p_recal, ri, rs),
        ]:
            cal_test_rows.append({
                "model": model, "variant": variant, "n": len(test),
                "calibration_intercept": ci, "calibration_slope": sl,
                "brier_score": brier_score_loss(y_test, probs), "ece": ece(y_test, probs),
                "platt_source": "OOF proper_train only" if variant == "recalibrated" else "not applicable",
            })

        q = conformal_thresholds[model]
        include_pos = (1 - p) <= q
        include_neg = p <= q
        sets = np.where(y_test == 1, include_pos, include_neg)
        size = include_pos.astype(int) + include_neg.astype(int)
        lo, hi = wilson(int(sets.sum()), len(sets))
        conf_rows.append({
            "model": model, "dimension": "overall", "category": "all",
            "n": len(test), "positive_n": int(y_test.sum()), "negative_n": int((y_test == 0).sum()),
            "empirical_coverage": sets.mean(), "ci_lower": lo, "ci_upper": hi,
            "coverage_minus_target": sets.mean() - TARGET_COVERAGE,
            "mean_set_size": size.mean(), "singleton_rate": (size == 1).mean(),
            "ambiguous_rate": (size == 2).mean(), "empty_set_rate": (size == 0).mean(),
            "conformal_threshold": q, "inference_status": "Wilson CI; no equivalence claim",
        })

        dim_specs = [("sex", "_sex"), ("race_ethnicity", "_race"), ("age", "_age"), ("bmi", "_bmi")]
        for dim, col in dim_specs:
            for cat in pd.unique(test[col].dropna()):
                mask = test[col].to_numpy() == cat
                yg, pg, hg = y_test[mask], p[mask], yhat[mask]
                pos, neg = int(yg.sum()), int((yg == 0).sum())
                sens = float(hg[yg == 1].mean()) if pos else np.nan
                spec = float((hg[yg == 0] == 0).mean()) if neg else np.nan
                auc_g = roc_auc_score(yg, pg) if pos and neg else np.nan
                fair_rows.append({
                    "model": model, "dimension": dim, "category": cat,
                    "reference_category": {"bmi": "Normal", "age": "40-59"}.get(dim, ""),
                    "n": len(yg), "positive_n": pos, "negative_n": neg,
                    "precision_tier": precision_tier(pos, neg), "roc_auc": auc_g,
                    "sensitivity": sens, "specificity": spec,
                    "fnr": 1 - sens if pos else np.nan, "fpr": 1 - spec if neg else np.nan,
                    "threshold": thresholds[model],
                })
                if pos:
                    c_lo, c_hi = wilson(int((hg[yg == 1] == 1).sum()), pos)
                else:
                    c_lo, c_hi = (np.nan, np.nan)
                conf_rows.append({
                    "model": model, "dimension": dim, "category": cat, "n": len(yg),
                    "positive_n": pos, "negative_n": neg, "empirical_coverage": sets[mask].mean(),
                    "ci_lower": wilson(int(sets[mask].sum()), len(yg))[0],
                    "ci_upper": wilson(int(sets[mask].sum()), len(yg))[1],
                    "coverage_minus_target": sets[mask].mean() - TARGET_COVERAGE,
                    "mean_set_size": size[mask].mean(), "singleton_rate": (size[mask] == 1).mean(),
                    "ambiguous_rate": (size[mask] == 2).mean(), "empty_set_rate": (size[mask] == 0).mean(),
                    "conformal_threshold": q, "inference_status": "Wilson CI; BH-FDR applied to standard dimensions",
                })

        # Required BMI x Age cells, descriptive intersectional metrics.
        for bmi in ["Underweight", "Normal", "Overweight", "Obese"]:
            for age in ["18-39", "40-59", "60+"]:
                mask = (test["_bmi"] == bmi).to_numpy() & (test["_age"] == age).to_numpy()
                if not mask.any():
                    continue
                yg, pg, hg = y_test[mask], p[mask], yhat[mask]
                pos, neg = int(yg.sum()), int((yg == 0).sum())
                sens = float(hg[yg == 1].mean()) if pos else np.nan
                fair_rows.append({
                    "model": model, "dimension": "bmi_age", "category": f"{bmi} x {age}",
                    "reference_category": "descriptive intersectional cell", "n": len(yg),
                    "positive_n": pos, "negative_n": neg, "precision_tier": precision_tier(pos, neg),
                    "roc_auc": roc_auc_score(yg, pg) if pos and neg else np.nan,
                    "sensitivity": sens, "specificity": float((hg[yg == 0] == 0).mean()) if neg else np.nan,
                    "fnr": 1 - sens if pos else np.nan,
                    "fpr": float((hg[yg == 0] == 1).mean()) if neg else np.nan,
                    "threshold": thresholds[model],
                })

        # Keep per-participant values in memory only; no extra result artifact is needed.

    fair_df = pd.DataFrame(fair_rows)
    conf_df = pd.DataFrame(conf_rows)
    # BH-FDR is restricted to the pre-specified standard subgroup dimensions.
    conf_df["raw_p_binomial_vs_90pct"] = np.nan
    conf_df["bh_fdr_adjusted_p"] = np.nan
    for (model, dim), idx in conf_df[conf_df.dimension.isin(["sex", "race_ethnicity", "age", "bmi"])].groupby(["model", "dimension"]).groups.items():
        vals = []
        for i in idx:
            r = conf_df.loc[i]
            vals.append(stats.binomtest(int(round(r.empirical_coverage * r.n)), int(r.n), TARGET_COVERAGE).pvalue)
        adj = stats.false_discovery_control(vals, method="bh") if hasattr(stats, "false_discovery_control") else np.minimum(1, np.array(vals) * len(vals) / np.arange(1, len(vals) + 1))
        for i, raw_p, adj_p in zip(idx, vals, adj):
            conf_df.loc[i, "raw_p_binomial_vs_90pct"] = raw_p
            conf_df.loc[i, "bh_fdr_adjusted_p"] = adj_p
    write_csv("phase6_8kpa_baseline_test_metrics.csv", pd.DataFrame(test_rows))
    write_csv("phase6_8kpa_calibration_test_metrics.csv", pd.DataFrame(cal_test_rows))
    write_csv("phase6_8kpa_fairness_metrics.csv", fair_df)
    write_csv("phase6_8kpa_conformal_metrics.csv", conf_df)

    # Exact requested consolidated comparison schema.
    auth = {}
    auth_paths = {
        "baseline": ROOT / "results" / "tables" / "phase3_overall_discrimination.csv",
        "calibration": ROOT / "results" / "calibration" / "test_set_calibration_final.csv",
        "fairness": ROOT / "results" / "fairness" / "subgroup_discrimination_metrics.csv",
        "conformal": ROOT / "results" / "uncertainty" / "subgroup_coverage.csv",
        "marginal_conformal": ROOT / "results" / "uncertainty" / "marginal_coverage_test_set.csv",
    }
    for key, path in auth_paths.items():
        auth[key] = pd.read_csv(path) if path.exists() else None

    comparison = []
    def add(metric, model, old, new, ci, interpretation):
        oldv, newv = (float(old) if pd.notna(old) else np.nan), (float(new) if pd.notna(new) else np.nan)
        comparison.append({
            "Metric": metric, "Model": model, "8.2-kPa result": oldv,
            "8.0-kPa result": newv, "Difference": newv - oldv if np.isfinite(oldv) else np.nan,
            "95% CI": ci, "Interpretation": interpretation,
        })
    for row in test_rows:
        model = row["model"]
        old = auth["baseline"].query("model_name == @model").iloc[0]
        add("ROC-AUC", model, old.roc_auc, row["roc_auc"],
            f"8.2 [{old.roc_auc_95ci_low:.4f}, {old.roc_auc_95ci_high:.4f}]; 8.0 [{row['roc_auc_ci_lower']:.4f}, {row['roc_auc_ci_upper']:.4f}]",
            "Descriptive threshold robustness comparison; no equivalence claim")
        add("PR-AUC", model, old.pr_auc, row["pr_auc"], "8.2 CI and 8.0 CI not jointly recomputed in this comparison", "Descriptive")
        add("Sensitivity", model, old.sensitivity, row["sensitivity"], "Bootstrap CIs reported in source tables", "Operating-point comparison; thresholds independently OOF-derived")
        add("Specificity", model, old.specificity, row["specificity"], "Bootstrap CIs reported in source tables", "Operating-point comparison; thresholds independently OOF-derived")
        old_cal = auth["calibration"].query("model == @model and variant == 'recalibrated'").iloc[0]
        new_cal = next(x for x in cal_test_rows if x["model"] == model and x["variant"] == "recalibrated")
        for metric, col in [("Recalibrated calibration intercept", "calibration_intercept"), ("Recalibrated calibration slope", "calibration_slope"), ("Recalibrated Brier score", "brier_score"), ("Recalibrated ECE", "ece")]:
            add(metric, model, old_cal[col], new_cal[col], "Not computed under the frozen calibration protocol", "Descriptive calibration robustness comparison")
        for dim, cat, label in [("bmi", "Obese", "BMI-Obese sensitivity"), ("age", "60+", "Age-60+ sensitivity")]:
            old_rows = auth["fairness"].query("model == @model and dimension == @dim and category == @cat")
            refcat = "Normal" if dim == "bmi" else "40-59"
            ref_old = auth["fairness"].query("model == @model and dimension == @dim and category == @refcat")
            new_rows = fair_df.query("model == @model and dimension == @dim and category == @cat")
            new_ref = fair_df.query("model == @model and dimension == @dim and category == @refcat")
            if len(old_rows) and len(ref_old) and len(new_rows) and len(new_ref):
                old_d = 100 * (float(old_rows.iloc[0].sensitivity) - float(ref_old.iloc[0].sensitivity))
                new_d = 100 * (float(new_rows.iloc[0].sensitivity) - float(new_ref.iloc[0].sensitivity))
                add(label + " disparity (pp)", model, old_d, new_d, "Bootstrap disparity CIs are not encoded in the authoritative 8.2 CSV", "Direction and magnitude compared descriptively; no equivalence claim")
        old_m = auth["marginal_conformal"].query("model == @model").iloc[0]
        new_m = conf_df.query("model == @model and dimension == 'overall'").iloc[0]
        add("Marginal conformal coverage", model, old_m.empirical_coverage, new_m.empirical_coverage,
            f"8.2 [{old_m.ci_lower:.4f}, {old_m.ci_upper:.4f}]; 8.0 [{new_m.ci_lower:.4f}, {new_m.ci_upper:.4f}]",
            "Wilson interval comparison; no equivalence claim")
        for dim, cat, label in [("bmi", "Obese", "BMI-Obese conformal coverage"), ("age", "60+", "Age-60+ conformal coverage")]:
            old_s = auth["conformal"].query("model == @model and dimension == @dim and category == @cat")
            new_s = conf_df.query("model == @model and dimension == @dim and category == @cat")
            if len(old_s) and len(new_s):
                add(label, model, old_s.iloc[0].empirical_coverage, new_s.iloc[0].empirical_coverage,
                    f"8.2 [{old_s.iloc[0].ci_lower:.4f}, {old_s.iloc[0].ci_upper:.4f}]; 8.0 [{new_s.iloc[0].ci_lower:.4f}, {new_s.iloc[0].ci_upper:.4f}]",
                    "Wilson interval comparison; no equivalence claim")
    comp = pd.DataFrame(comparison)
    write_csv("phase6_8kpa_consolidated_comparison.csv", comp)

    # Figures are generated from saved tables, not from any pre-existing artifact.
    bm = pd.DataFrame(test_rows)
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(MODEL_NAMES))
    ax.errorbar(x - .12, bm.roc_auc, yerr=[bm.roc_auc - bm.roc_auc_ci_lower, bm.roc_auc_ci_upper - bm.roc_auc], fmt="o", label="8.0-kPa")
    old_auc = auth["baseline"].set_index("model_name").loc[MODEL_NAMES]
    ax.plot(x + .12, old_auc.roc_auc, "s", label="8.2-kPa")
    ax.set_xticks(x); ax.set_xticklabels(MODEL_NAMES, rotation=20); ax.set_ylabel("ROC-AUC")
    ax.set_title("Retrained 8.0-kPa vs authoritative 8.2-kPa discrimination")
    ax.legend(); fig.tight_layout(); fig.savefig(FIG / "phase6_8kpa_auc_comparison.png", dpi=160); plt.close(fig)

    f = fair_df.query("dimension in ['bmi','age'] and category in ['Obese','60+']")
    fig, ax = plt.subplots(figsize=(8, 4))
    for dim, color in [("bmi", "#b2182b"), ("age", "#2166ac")]:
        q = f[f.dimension == dim]
        ax.plot(q.model, q.sensitivity, "o-", label=f"{dim} target sensitivity", color=color)
    ax.set_ylim(0, 1.05); ax.set_ylabel("Sensitivity"); ax.set_title("8.0-kPa BMI/Age target-group sensitivity")
    ax.legend(); fig.tight_layout(); fig.savefig(FIG / "phase6_8kpa_bmi_age_sensitivity.png", dpi=160); plt.close(fig)

    q = conf_df.query("dimension == 'overall'")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.errorbar(q.model, q.empirical_coverage, yerr=[q.empirical_coverage - q.ci_lower, q.ci_upper - q.empirical_coverage], fmt="o")
    ax.axhline(TARGET_COVERAGE, color="black", linestyle="--"); ax.set_ylim(.7, 1.0)
    ax.set_ylabel("Coverage"); ax.set_title("8.0-kPa marginal conformal coverage (95% Wilson CI)")
    fig.tight_layout(); fig.savefig(FIG / "phase6_8kpa_conformal_coverage.png", dpi=160); plt.close(fig)

    # Complete the manifest only after all outputs exist; the recorded selection
    # freeze remains the pre-test snapshot above.
    output_paths = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != MANIFEST_PATH.name)
    manifest.update({
        "status": "COMPLETE",
        "test_accessed_utc": datetime.now(timezone.utc).isoformat(),
        "test_access_sequence": ["NOT ACCESSED BEFORE MANIFEST", "ACCESS AUTHORIZED NOW", "ONE LOCKED TEST TOUCH COMPLETE"],
        "locked_test_ids_sha256": sha256(SPLIT_DIR / "test_ids.csv"),
        "locked_test_n": len(test),
        "locked_test_positive_n_8.0": int(y_test.sum()),
        "locked_test_prevalence_pct_8.0": 100 * y_test.mean(),
        "output_hashes": {str(p.relative_to(ROOT)): sha256(p) for p in output_paths},
        "figure_hashes": {str(p.relative_to(ROOT)): sha256(p) for p in sorted(FIG.glob("*"))},
        "runtime_seconds": round(time.time() - started, 3),
    })
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, default=str))

    # Documentation is deliberately explicit about unavailable lineage links.
    bmi_disp = comp[comp.Metric == "BMI-Obese sensitivity disparity (pp)"].Difference
    age_disp = comp[comp.Metric == "Age-60+ sensitivity disparity (pp)"].Difference
    robust_bmi = bool(len(bmi_disp) and (bmi_disp.abs() < 10).mean() < 0.5)  # descriptive aid only
    age_changed = bool(len(age_disp) and (age_disp.abs() > 2).any())
    conclusion = "SOME MAJOR FINDINGS ARE THRESHOLD-SENSITIVE" if (age_changed or not robust_bmi) else "MAJOR FINDINGS ROBUST TO 8.0-kPa THRESHOLD"
    report = f"""# Phase 6 Full 8.0-kPa Robustness Report

## Scope
New outcome: valid VCTE (`LUAXSTAT==1`) and `LUXSMED>=8.0 kPa`. The same quality-valid
adult broad-lab CAND_1 cohort, ten frozen predictors, five frozen model families, inherited
hyperparameters, development partitions, OOF Platt calibration, and split-conformal method
were used. No external or out-of-sample validation was performed, and no mitigation was introduced.

## Cohort and label verification
The cohort contains **N={n}**, with 8.2-kPa positives **{pos82} ({100*pos82/n:.4f}%)** and
8.0-kPa positives **{pos80} ({100*pos80/n:.4f}%)**. Labels differ for **{changed}** participants.
The independently derived 8.0 label agrees with the pre-existing sensitivity column; that
column was not used as the outcome source.

## Leakage and test protection
All configurations, OOF Youden thresholds, OOF Platt parameters, and conformal thresholds were
written to the selection manifest before reading any test IDs, metadata, outcomes, or predictions.
The locked test set was touched exactly once afterward; it was not used for tuning or selection.

## Results
See `phase6_8kpa_consolidated_comparison.csv` for the exact columns
`Metric, Model, 8.2-kPa result, 8.0-kPa result, Difference, 95% CI, Interpretation`.
BMI, age, BMI×Age intersectional cells, calibration, and conformal coverage are reported in
the dedicated result tables. Wilson/bootstrap methods are used only for the corresponding
supported quantities; no equivalence claim is made.

## Lineage limitations
Frozen 8.2 protocol commit: **NOT FOUND IN REPOSITORY**.
Frozen 8.2 model-artifact manifest: **NOT FOUND IN REPOSITORY**.
Complete available input/output hashes and runtime metadata are in `phase6_8kpa_manifest.json`.

## Final conclusion
{conclusion}
"""
    (DOC / "PHASE6_8KPA_ROBUSTNESS_REPORT.md").write_text(report)
    (DOC / "PHASE6_8KPA_DECISION_LOG.md").write_text(
        f"""# Phase 6 8.0-kPa Decision Log

- New analysis namespace: `{OUT.relative_to(ROOT)}`; pre-existing artifacts were read-only.
- Outcome frozen before test access: `LUAXSTAT==1 and LUXSMED>=8.0`.
- Cohort: N={n}; 8.2 positives={pos82}; 8.0 positives={pos80}; changed labels={changed}.
- Five models were retrained with Phase 3 frozen configurations; no hyperparameter search occurred.
- OOF thresholds and approved OOF Platt calibration were frozen before test access.
- Conformal calibration used the frozen 90% split-conformal score and finite-sample correction.
- Locked test set was used exactly once after all development decisions.
- No external or out-of-sample validation and no mitigation.
- Missing lineage links: frozen 8.2 protocol commit — NOT FOUND IN REPOSITORY; frozen 8.2
  model-artifact manifest — NOT FOUND IN REPOSITORY.

## Final conclusion
{conclusion}
"""
    )
    print(f"Phase 6 8.0-kPa robustness complete: N={n}, positives={pos80}, changed labels={changed}")
    print(f"Final conclusion: {conclusion}")


if __name__ == "__main__":
    main()
