"""Phase 8 — THE TOUCH. Score the pooled locked test set once with the updated
models and evaluate discrimination / calibration / fairness / conformal /
dissociation / matched-stiffness shortcut. Report overall and on the 2021-2023
test slice, with Δ vs frozen 2017-2020 and temporal 2021-2023.
"""
from __future__ import annotations

import datetime as dt
import json

import joblib
import numpy as np
import pandas as pd
from scipy import stats as sps
from sklearn.metrics import roc_auc_score, average_precision_score

from _phelpers import (PU, REPO, TV, MODELS, PREDICTORS, RACE_MAP, SEED,
                       load_frozen, platt_apply, calibration_in_the_large,
                       ece_decile, brier, wilson_ci, bh_fdr, sha256)

DATA = PU / "data" / "processed"
MDIR = PU / "models"
RES = PU / "results"
P = json.loads((RES / "pooled_frozen_params.json").read_text())


def boot_ci(fn, *a, n=2000, seed=SEED):
    rng = np.random.default_rng(seed); N = len(a[0]); v = []
    for _ in range(n):
        idx = rng.integers(0, N, N)
        try:
            v.append(fn(*[x[idx] for x in a]))
        except Exception:
            pass
    return float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))


def score(df):
    out = {}
    for m in MODELS:
        full = joblib.load(MDIR / f"pooled_{m}.joblib")
        p_raw = full["pipeline"].predict_proba(df[PREDICTORS])[:, 1]
        a, b = P[m]["platt_intercept"], P[m]["platt_slope"]
        conf = joblib.load(MDIR / f"pooled_{m}_conformal_refit.joblib")
        p_conf = conf["pipeline"].predict_proba(df[PREDICTORS])[:, 1]
        out[m] = dict(p_raw=p_raw, p_recal=platt_apply(p_raw, a, b),
                      y_pred=(p_raw >= P[m]["youden_threshold"]).astype(int), p_conf=p_conf)
    return out


def discrimination(df, S, tag):
    y = df["outcome_primary_8.2kPa"].values
    fro = load_frozen("results/tables/phase3_final_baseline_results.csv").set_index("model_name")
    tv = pd.read_csv(TV / "results" / "temporal_discrimination_calibration_results.csv")
    tv = tv[tv.variant == "raw"].set_index("model")
    rows = []
    for m in MODELS:
        s = S[m]
        au = roc_auc_score(y, s["p_raw"]); pr = average_precision_score(y, s["p_raw"])
        lo, hi = boot_ci(lambda yy, pp: roc_auc_score(yy, pp), y, s["p_raw"])
        yp = s["y_pred"]
        tp = int(((yp == 1) & (y == 1)).sum()); fn = int(((yp == 0) & (y == 1)).sum())
        tn = int(((yp == 0) & (y == 0)).sum()); fp = int(((yp == 1) & (y == 0)).sum())
        inter, slope = calibration_in_the_large(y, s["p_recal"])
        rows.append(dict(tag=tag, model=m, n=len(y),
                         auroc=round(au, 4), auroc_ci_low=round(lo, 4), auroc_ci_high=round(hi, 4),
                         pr_auc=round(pr, 4),
                         sensitivity=round(tp / (tp + fn), 4), specificity=round(tn / (tn + fp), 4),
                         recal_intercept=round(inter, 4), recal_slope=round(slope, 4),
                         recal_ece=round(ece_decile(y, s["p_recal"]), 4),
                         recal_brier=round(brier(y, s["p_recal"]), 4),
                         auroc_frozen_2017_2020=round(float(fro.loc[m, "test_roc_auc"]), 4),
                         auroc_temporal_2021_2023=round(float(tv.loc[m, "auroc"]), 4)))
    return pd.DataFrame(rows)


def fairness(df, S, tag):
    y = df["outcome_primary_8.2kPa"].values
    fro = load_frozen("results/fairness/fairness_inference.csv")
    dims = {"bmi": ("bmi_group_final", "Normal", ["Obese", "Overweight"]),
            "age": ("age_group_final", "40-59", ["18-39", "60+"]),
            "sex": ("RIAGENDR", 1.0, [2.0]),
            "race_ethnicity": ("race_label", "Non-Hispanic White",
                               [v for v in RACE_MAP.values() if v != "Non-Hispanic White"])}
    rows = []
    for m in MODELS:
        yp = S[m]["y_pred"]
        for dim, (col, ref, cats) in dims.items():
            rm = (df[col] == ref).values
            rs = yp[(y == 1) & rm].mean() if ((y == 1) & rm).any() else np.nan
            fam_p, fr = [], []
            for cat in cats:
                mk = (df[col] == cat).values
                npos = int((y[mk] == 1).sum())
                if npos < 5:
                    continue
                ss = yp[(y == 1) & mk].mean()
                disp = 100 * (ss - rs)
                rng = np.random.default_rng(SEED)
                bs = []
                for _ in range(2000):
                    idx = rng.integers(0, len(y), len(y))
                    a_ = yp[idx][(y[idx] == 1) & mk[idx]]
                    b_ = yp[idx][(y[idx] == 1) & rm[idx]]
                    if len(a_) and len(b_):
                        bs.append(100 * (a_.mean() - b_.mean()))
                bs = np.array(bs)
                pb = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
                fam_p.append(pb)
                fr.append(dict(tag=tag, model=m, dimension=dim, category=str(cat),
                               n_positive=npos, subgroup_sensitivity=round(ss, 4),
                               reference_sensitivity=round(rs, 4),
                               absolute_disparity_pp=round(disp, 4),
                               ci_lower_pp=round(np.nanpercentile(bs, 2.5), 4),
                               ci_upper_pp=round(np.nanpercentile(bs, 97.5), 4),
                               raw_p=round(pb, 4)))
            for r, q in zip(fr, bh_fdr(fam_p) if fam_p else []):
                r["bh_fdr_adjusted_p"] = round(float(q), 4)
                r["significant_after_fdr_0.05"] = bool(q <= 0.05)
                fm = fro[(fro.model == m) & (fro.dimension == r["dimension"]) &
                         (fro.category == r["category"])]
                if len(fm):
                    r["disparity_frozen_2017_2020"] = round(float(fm.iloc[0]["absolute_disparity_pp"]), 4)
                rows.append(r)
    return pd.DataFrame(rows)


def conformal(df, S, tag):
    y = df["outcome_primary_8.2kPa"].values
    fs = load_frozen("results/uncertainty/subgroup_coverage.csv")
    fmg = load_frozen("results/uncertainty/marginal_coverage_test_set.csv").set_index("model")
    obese = (df["bmi_group_final"] == "Obese").values
    a60 = (df["age_group_final"] == "60+").values
    groups = {"marginal": np.ones(len(y), bool), "bmi_Obese": obese, "age_60plus": a60,
              "Obese_x_60plus": obese & a60}
    rows = []
    for m in MODELS:
        thr = P[m]["conformal_threshold"]; p = S[m]["p_conf"]
        inc_pos = (1 - p) <= thr; inc_neg = p <= thr
        covered = np.where(y == 1, inc_pos, inc_neg)
        ss = inc_pos.astype(int) + inc_neg.astype(int)
        fam_p, fr = [], []
        for g, gm in groups.items():
            n = int(gm.sum()); k = int(covered[gm].sum())
            lo, hi = wilson_ci(k, n)
            pb = sps.binomtest(k, n, 0.90).pvalue
            fam_p.append(pb)
            fr.append(dict(tag=tag, model=m, scope=g, n=n, coverage=round(k / n, 4),
                           ci_lower=round(lo, 4), ci_upper=round(hi, 4),
                           mean_set_size=round(float(ss[gm].mean()), 4),
                           raw_p=round(pb, 5)))
        for r, q in zip(fr, bh_fdr(fam_p)):
            r["bh_fdr_adjusted_p"] = round(float(q), 5)
            r["ci_excludes_90"] = bool(r["ci_upper"] < 0.90 or r["ci_lower"] > 0.90)
            r["significant_after_fdr_0.05"] = bool(q <= 0.05)
            if r["scope"] in ("bmi_Obese", "age_60plus"):
                cat = "Obese" if r["scope"] == "bmi_Obese" else "60+"
                fm = fs[(fs.model == m) & (fs.category == cat)]
                if len(fm):
                    r["coverage_frozen_2017_2020"] = round(float(fm.iloc[0]["empirical_coverage"]), 4)
            elif r["scope"] == "marginal":
                r["coverage_frozen_2017_2020"] = round(float(fmg.loc[m, "empirical_coverage"]), 4)
            rows.append(r)
    return pd.DataFrame(rows)


def shortcut(df, S, tag):
    fz = load_frozen("results/prepublication_fixes/fix2_bmi_shortcut_check.csv").set_index("model")
    b = df[(df["LUXSMED"] >= 8.2) & (df["LUXSMED"] <= 12)].copy()
    b["is_obese"] = (b["bmi_group_final"] == "Obese").astype(int)
    sub = b[b["bmi_group_final"].isin(["Obese", "Normal"])].copy()
    rows = []
    for m in MODELS:
        yv = S[m]["p_raw"][sub.index.values].astype(float)
        X = np.column_stack([np.ones(len(sub)), sub["is_obese"].values.astype(float),
                             sub["LUXSMED"].values.astype(float)])
        bh, *_ = np.linalg.lstsq(X, yv, rcond=None)
        resid = yv - X @ bh; dof = len(sub) - 3
        se = np.sqrt(np.diag((resid @ resid) / dof * np.linalg.inv(X.T @ X)))
        t = bh[1] / se[1]; pval = 2 * sps.t.sf(abs(t), dof)
        rows.append(dict(tag=tag, model=m, n=len(sub), n_obese=int(sub.is_obese.sum()),
                         beta_is_obese=round(float(bh[1]), 4), p_value=round(float(pval), 5),
                         beta_frozen_2017_2020=round(float(fz.loc[m, "beta_is_obese"]), 4)))
    return pd.DataFrame(rows)


def main():
    pool = pd.read_parquet(DATA / "pooled_cohort_2017_2023.parquet")
    te = pool[pool.split == "test"].reset_index(drop=True)
    te21 = te[te.cycle == "2021-2023"].reset_index(drop=True)

    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    (PU / "documentation").mkdir(exist_ok=True)
    log = PU / "documentation" / "POOLED_TOUCH_LOG.md"
    log.write_text(
        "# Pooled locked-test touch log\n\n"
        f"| {ts} | p02_evaluate.py | cohort SHA "
        f"{sha256(DATA / 'pooled_cohort_2017_2023.parquet')[:16]} | single non-iterative "
        "evaluation of the pooled-retrained models (frozen hyperparameters) on the pooled "
        "locked test set (N=3,619; 2021-2023 slice N=1,473). Discrimination, calibration, "
        "fairness, conformal, dissociation, matched-stiffness shortcut. |\n\n"
        "Leakage: pooled test SEQNs are disjoint from the pooled train partition by "
        "construction; no participant appears in both.\n\nNo frozen artifact was written.\n")

    S = score(te); S21 = score(te21)
    parts = {
        "discrimination": pd.concat([discrimination(te, S, "pooled_test_all"),
                                     discrimination(te21, S21, "pooled_test_2021_2023")]),
        "fairness": pd.concat([fairness(te, S, "pooled_test_all"),
                               fairness(te21, S21, "pooled_test_2021_2023")]),
        "conformal": pd.concat([conformal(te, S, "pooled_test_all"),
                                conformal(te21, S21, "pooled_test_2021_2023")]),
        "shortcut": pd.concat([shortcut(te, S, "pooled_test_all"),
                               shortcut(te21, S21, "pooled_test_2021_2023")]),
    }
    for k, v in parts.items():
        v.to_csv(RES / f"pooled_{k}_results.csv", index=False)

    d = parts["discrimination"]
    print("\n=== DISCRIMINATION ===")
    print(d[["tag", "model", "auroc", "auroc_frozen_2017_2020", "auroc_temporal_2021_2023",
             "sensitivity", "recal_intercept"]].to_string(index=False))
    f = parts["fairness"]
    print("\n=== BMI Obese vs Normal sensitivity gap ===")
    print(f[(f.dimension == "bmi") & (f.category == "Obese")]
          [["tag", "model", "absolute_disparity_pp", "disparity_frozen_2017_2020",
            "bh_fdr_adjusted_p", "significant_after_fdr_0.05"]].to_string(index=False))
    c = parts["conformal"]
    print("\n=== CONFORMAL ===")
    print(c[c.scope.isin(["marginal", "bmi_Obese", "age_60plus", "Obese_x_60plus"])]
          [["tag", "model", "scope", "coverage", "coverage_frozen_2017_2020", "ci_excludes_90",
            "significant_after_fdr_0.05"]].to_string(index=False))
    s = parts["shortcut"]
    print("\n=== MATCHED-STIFFNESS SHORTCUT ===")
    print(s[["tag", "model", "beta_is_obese", "beta_frozen_2017_2020", "p_value"]].to_string(index=False))


if __name__ == "__main__":
    main()
