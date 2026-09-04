"""Phases 4-6 — apply frozen models to the 2021-2023 cohort (THE TOUCH),
then compute discrimination / calibration / fairness / conformal, the dissociation
check, and the matched-stiffness shortcut replication.

PRIMARY = raw 2021-2023 predictor values, no crosswalk. Frozen models, frozen
thresholds, frozen Platt params, frozen conformal quantile — all loaded via
_thelpers.load_frozen() with hash verification. Nothing is refit.
"""
from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

from _thelpers import (REPO, TV, MODELS, PREDICTORS, YOUDEN, PLATT, CONF_THR, RACE_MAP,
                       load_frozen, platt_apply, wilson_ci, calibration_in_the_large,
                       ece_decile, brier, boot_ci, bh_fdr, touch_log, SEED)

OUT = TV / "results"


def score_all(df):
    """returns dict model -> {p_raw, p_recal, y_pred, p_conf_raw}"""
    X = df[PREDICTORS]
    res = {}
    for m in MODELS:
        full = load_frozen(f"models/phase3/model_{m}_v1.joblib", binary=True)
        p_raw = full["pipeline"].predict_proba(X[full["predictors"]])[:, 1]
        b0, b1 = PLATT[m]
        p_recal = platt_apply(p_raw, b0, b1)
        y_pred = (p_raw >= YOUDEN[m]).astype(int)
        conf = load_frozen(f"models/phase6_conformal_refit/model_{m}_proper_train_refit.joblib", binary=True)
        p_conf = conf["pipeline"].predict_proba(X[conf["predictors"]])[:, 1]
        res[m] = dict(p_raw=p_raw, p_recal=p_recal, y_pred=y_pred, p_conf=p_conf)
    return res


# ---------------- discrimination + calibration ----------------

def discrimination_calibration(df, S):
    y = df["outcome_primary_8.2kPa"].values
    frozen = load_frozen("results/tables/phase3_final_baseline_results.csv").set_index("model_name")
    fcal = load_frozen("results/calibration/test_set_calibration_final.csv")
    rows = []
    for m in MODELS:
        s = S[m]
        auroc = roc_auc_score(y, s["p_raw"]); prauc = average_precision_score(y, s["p_raw"])
        a_lo, a_hi = boot_ci(lambda yy, pp: roc_auc_score(yy, pp), y, s["p_raw"])
        yp = s["y_pred"]
        tp = int(((yp == 1) & (y == 1)).sum()); tn = int(((yp == 0) & (y == 0)).sum())
        fp = int(((yp == 1) & (y == 0)).sum()); fn = int(((yp == 0) & (y == 1)).sum())
        sens = tp / (tp + fn); spec = tn / (tn + fp)
        ppv = tp / (tp + fp) if tp + fp else float("nan"); npv = tn / (tn + fn) if tn + fn else float("nan")
        for variant, p in [("raw", s["p_raw"]), ("recalibrated", s["p_recal"])]:
            inter, slope = calibration_in_the_large(y, p)
            fr = fcal[(fcal.model == m) & (fcal.variant == variant)].iloc[0]
            rows.append(dict(
                model=m, variant=variant, n=len(y),
                auroc=round(auroc, 4), auroc_ci_low=round(a_lo, 4), auroc_ci_high=round(a_hi, 4),
                pr_auc=round(prauc, 4),
                sensitivity=round(sens, 4), specificity=round(spec, 4),
                ppv=round(ppv, 4), npv=round(npv, 4),
                calib_intercept=round(inter, 4), calib_slope=round(slope, 4),
                ece=round(ece_decile(y, p), 4), brier=round(brier(y, p), 4),
                auroc_2017_2020=round(float(frozen.loc[m, "test_roc_auc"]), 4),
                auroc_delta=round(auroc - float(frozen.loc[m, "test_roc_auc"]), 4),
                calib_intercept_2017_2020=round(float(fr["calibration_intercept"]), 4),
                ece_2017_2020=round(float(fr["ece"]), 4),
            ))
    d = pd.DataFrame(rows)
    d.to_csv(OUT / "temporal_discrimination_calibration_results.csv", index=False)
    return d


# ---------------- fairness ----------------

def _sens(y, yp):
    pos = y == 1
    return yp[pos].mean() if pos.any() else float("nan")


def fairness(df, S):
    y = df["outcome_primary_8.2kPa"].values
    froz = load_frozen("results/fairness/fairness_inference.csv")
    dims = {
        "bmi": ("bmi_group_final", "Normal", ["Obese", "Overweight", "Underweight"]),
        "age": ("age_group_final", "40-59", ["18-39", "60+"]),
        "sex": ("RIAGENDR", 1.0, [2.0]),
        "race_ethnicity": ("race_label", "Non-Hispanic White",
                           [v for v in RACE_MAP.values() if v != "Non-Hispanic White"]),
    }
    rows = []
    for m in MODELS:
        yp = S[m]["y_pred"]
        for dim, (col, ref, cats) in dims.items():
            ref_mask = (df[col] == ref).values
            ref_sens = _sens(y[ref_mask], yp[ref_mask])
            fam_p = []
            fam_rows = []
            for cat in cats:
                mask = (df[col] == cat).values
                npos = int((y[mask] == 1).sum())
                if npos == 0:
                    continue
                sub_sens = _sens(y[mask], yp[mask])
                disp = 100 * (sub_sens - ref_sens)
                # bootstrap CI + p on the disparity
                def stat(idx):
                    yy, pp, mm, rr = y[idx], yp[idx], mask[idx], ref_mask[idx]
                    a = pp[(yy == 1) & mm].mean() if ((yy == 1) & mm).any() else np.nan
                    b = pp[(yy == 1) & rr].mean() if ((yy == 1) & rr).any() else np.nan
                    return 100 * (a - b)
                rng = np.random.default_rng(SEED)
                bs = np.array([stat(rng.integers(0, len(y), len(y))) for _ in range(2000)])
                lo, hi = np.nanpercentile(bs, 2.5), np.nanpercentile(bs, 97.5)
                p_boot = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
                fam_p.append(p_boot)
                fam_rows.append(dict(model=m, dimension=dim, category=str(cat), reference=str(ref),
                                     n=int(mask.sum()), n_positive=npos,
                                     subgroup_sensitivity=round(sub_sens, 4),
                                     reference_sensitivity=round(ref_sens, 4),
                                     absolute_disparity_pp=round(disp, 4),
                                     ci_lower_pp=round(lo, 4), ci_upper_pp=round(hi, 4),
                                     raw_p_bootstrap=round(p_boot, 4)))
            adj = bh_fdr(fam_p) if fam_p else []
            for r, q in zip(fam_rows, adj):
                r["bh_fdr_adjusted_p"] = round(float(q), 4)
                r["significant_after_fdr_0.05"] = bool(q <= 0.05)
                # frozen comparison
                fm = froz[(froz.model == m) & (froz.dimension == r["dimension"]) &
                          (froz.category == r["category"])]
                if len(fm):
                    r["disparity_pp_2017_2020"] = round(float(fm.iloc[0]["absolute_disparity_pp"]), 4)
                    r["significant_2017_2020"] = bool(fm.iloc[0]["significant_after_fdr_0.05"])
                rows.append(r)
    d = pd.DataFrame(rows)
    d.to_csv(OUT / "temporal_fairness_results.csv", index=False)
    return d


# ---------------- conformal ----------------

def conformal(df, S):
    y = df["outcome_primary_8.2kPa"].values
    froz_sub = load_frozen("results/uncertainty/subgroup_coverage.csv")
    froz_marg = load_frozen("results/uncertainty/marginal_coverage_test_set.csv").set_index("model")
    obese = (df["bmi_group_final"] == "Obese").values
    age60 = (df["age_group_final"] == "60+").values
    groups = {"marginal": np.ones(len(y), bool), "bmi_Obese": obese,
              "age_60plus": age60, "Obese_x_60plus": obese & age60}
    rows = []
    for m in MODELS:
        thr = CONF_THR[m]
        p = S[m]["p_conf"]
        # prediction set: include positive if (1-p)<=thr; include negative if p<=thr
        inc_pos = (1 - p) <= thr
        inc_neg = p <= thr
        covered = np.where(y == 1, inc_pos, inc_neg)
        set_size = inc_pos.astype(int) + inc_neg.astype(int)
        fam_p = []
        fam_rows = []
        for gname, gmask in groups.items():
            n = int(gmask.sum()); k = int(covered[gmask].sum())
            cov = k / n
            lo, hi = wilson_ci(k, n)
            from scipy.stats import binomtest
            pb = binomtest(k, n, 0.90).pvalue
            fam_p.append(pb)
            fam_rows.append(dict(model=m, scope=gname, n=n, covered=k,
                                 empirical_coverage=round(cov, 4),
                                 ci_lower=round(lo, 4), ci_upper=round(hi, 4),
                                 mean_set_size=round(float(set_size[gmask].mean()), 4),
                                 singleton_rate=round(float((set_size[gmask] == 1).mean()), 4),
                                 raw_p_binomial_vs_90=round(pb, 5)))
        adj = bh_fdr(fam_p)
        for r, q in zip(fam_rows, adj):
            r["bh_fdr_adjusted_p"] = round(float(q), 5)
            r["ci_excludes_90"] = bool(r["ci_upper"] < 0.90 or r["ci_lower"] > 0.90)
            r["significant_after_fdr_0.05"] = bool(q <= 0.05)
            if r["scope"] in ("bmi_Obese", "age_60plus"):
                cat = "Obese" if r["scope"] == "bmi_Obese" else "60+"
                fm = froz_sub[(froz_sub.model == m) & (froz_sub.category == cat)]
                if len(fm):
                    r["coverage_2017_2020"] = round(float(fm.iloc[0]["empirical_coverage"]), 4)
            elif r["scope"] == "marginal":
                r["coverage_2017_2020"] = round(float(froz_marg.loc[m, "empirical_coverage"]), 4)
            rows.append(r)
    d = pd.DataFrame(rows)
    d.to_csv(OUT / "temporal_conformal_results.csv", index=False)
    return d


# ---------------- dissociation + matched-stiffness shortcut ----------------

def dissociation_and_shortcut(df, S, fair_df, conf_df):
    y = df["outcome_primary_8.2kPa"].values
    # dissociation: is BMI-Obese fairness-FAVORABLE (higher sens than Normal) AND
    # reliability-UNFAVORABLE (conformal coverage below target)?
    diss = []
    for m in MODELS:
        f = fair_df[(fair_df.model == m) & (fair_df.dimension == "bmi") & (fair_df.category == "Obese")]
        c = conf_df[(conf_df.model == m) & (conf_df.scope == "bmi_Obese")]
        if not len(f) or not len(c):
            continue
        obese_fav = float(f.iloc[0]["absolute_disparity_pp"]) > 0   # Obese sens > Normal sens
        obese_unreliable = bool(c.iloc[0]["ci_excludes_90"]) and float(c.iloc[0]["empirical_coverage"]) < 0.90
        diss.append(dict(model=m,
                         obese_minus_normal_sensitivity_pp=round(float(f.iloc[0]["absolute_disparity_pp"]), 2),
                         obese_conformal_coverage=round(float(c.iloc[0]["empirical_coverage"]), 4),
                         fairness_favorable_to_obese=obese_fav,
                         reliability_unfavorable_to_obese=obese_unreliable,
                         dissociation_replicated=bool(obese_fav and obese_unreliable)))
    diss_df = pd.DataFrame(diss)
    diss_df.to_csv(OUT / "temporal_dissociation.csv", index=False)

    # matched-stiffness shortcut: among LUXSMED in 8.2-12 kPa, OLS raw_score ~ is_obese + LUXSMED
    from scipy import stats as sps
    band = df[(df["LUXSMED"] >= 8.2) & (df["LUXSMED"] <= 12)].copy()
    band["is_obese"] = (band["bmi_group_final"] == "Obese").astype(int)
    band["is_normal"] = (band["bmi_group_final"] == "Normal").astype(int)
    sub = band[(band["is_obese"] == 1) | (band["is_normal"] == 1)].copy()
    froz_sc = load_frozen("results/prepublication_fixes/fix2_bmi_shortcut_check.csv").set_index("model")
    sc_rows = []
    for m in MODELS:
        yv = S[m]["p_raw"][sub.index.values].astype(float)
        Xd = np.column_stack([np.ones(len(sub)),
                              sub["is_obese"].values.astype(float),
                              sub["LUXSMED"].values.astype(float)])
        beta_hat, *_ = np.linalg.lstsq(Xd, yv, rcond=None)
        resid = yv - Xd @ beta_hat
        dof = len(sub) - Xd.shape[1]
        sigma2 = (resid @ resid) / dof
        cov = sigma2 * np.linalg.inv(Xd.T @ Xd)
        se = np.sqrt(np.diag(cov))
        t = beta_hat[1] / se[1]
        pval = 2 * sps.t.sf(abs(t), dof)
        sc_rows.append(dict(model=m, n_band=len(sub),
                            n_obese=int(sub.is_obese.sum()), n_normal=int(sub.is_normal.sum()),
                            beta_is_obese=round(float(beta_hat[1]), 4), p_value=round(float(pval), 5),
                            beta_is_obese_2017_2020=round(float(froz_sc.loc[m, "beta_is_obese"]), 4)))
    sc_df = pd.DataFrame(sc_rows)
    sc_df.to_csv(OUT / "temporal_matched_stiffness_shortcut.csv", index=False)
    return diss_df, sc_df


def main():
    df = pd.read_parquet(TV / "data" / "processed" / "temporal_cohort_2021_2023.parquet")
    S = score_all(df)

    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    from _thelpers import sha256
    ohash = sha256(TV / "data" / "processed" / "temporal_cohort_2021_2023.parquet")
    touch_log(f"| {ts} | t03_apply_and_evaluate.py | cohort SHA {ohash[:16]} | "
              "single non-iterative evaluation of frozen phase3 + phase6-refit models on the "
              "2021-2023 primary outcome (raw predictors, no crosswalk). Discrimination, "
              "calibration, fairness, conformal, dissociation, matched-stiffness shortcut. "
              "Leakage: temporal cohort SEQN disjoint from 2017-2020 by construction (different cycle).")

    dc = discrimination_calibration(df, S)
    fa = fairness(df, S)
    co = conformal(df, S)
    di, sc = dissociation_and_shortcut(df, S, fa, co)

    print("\n=== DISCRIMINATION (raw) ===")
    print(dc[dc.variant == "raw"][["model", "auroc", "auroc_2017_2020", "auroc_delta",
                                   "sensitivity", "specificity"]].to_string(index=False))
    print("\n=== CALIBRATION (recalibrated) ===")
    print(dc[dc.variant == "recalibrated"][["model", "calib_intercept", "calib_intercept_2017_2020",
                                            "calib_slope", "ece", "brier"]].to_string(index=False))
    print("\n=== FAIRNESS: BMI Obese vs Normal ===")
    print(fa[(fa.dimension == "bmi") & (fa.category == "Obese")]
          [["model", "absolute_disparity_pp", "disparity_pp_2017_2020",
            "bh_fdr_adjusted_p", "significant_after_fdr_0.05"]].to_string(index=False))
    print("\n=== FAIRNESS: Age 60+ vs 40-59 ===")
    print(fa[(fa.dimension == "age") & (fa.category == "60+")]
          [["model", "absolute_disparity_pp", "disparity_pp_2017_2020",
            "bh_fdr_adjusted_p", "significant_after_fdr_0.05"]].to_string(index=False))
    print("\n=== CONFORMAL ===")
    print(co[co.scope.isin(["marginal", "bmi_Obese", "age_60plus", "Obese_x_60plus"])]
          [["model", "scope", "empirical_coverage", "coverage_2017_2020", "ci_excludes_90",
            "significant_after_fdr_0.05"]].to_string(index=False))
    print("\n=== DISSOCIATION (BMI-Obese) ===")
    print(di.to_string(index=False))
    print("\n=== MATCHED-STIFFNESS SHORTCUT ===")
    print(sc.to_string(index=False))


if __name__ == "__main__":
    main()
