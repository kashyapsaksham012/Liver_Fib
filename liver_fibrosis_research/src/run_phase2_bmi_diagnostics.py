"""Phase 2 BMI mechanism diagnostics using training-partition OOF predictions only."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, ttest_ind
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve,
)
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
PRED = ROOT / "results" / "predictions"
OUT = ROOT / "results" / "fairness_bmi_investigation"
FIG = OUT / "figures" / "phase2"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
DISPLAY = {"logistic": "Logistic Regression", "random_forest": "Random Forest",
           "xgboost": "XGBoost", "lightgbm": "LightGBM", "mlp": "MLP"}
THRESHOLDS = {"logistic": 0.5173, "random_forest": 0.4499, "xgboost": 0.4108,
              "lightgbm": 0.4988, "mlp": 0.1065}
PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
              "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
LABELS = {"RIDAGEYR": "Age", "RIAGENDR": "Sex", "BMXBMI": "BMI",
          "LBXSATSI": "ALT", "LBXSASSI": "AST", "LBXSAL": "Albumin",
          "LBXSAPSI": "AlkPhos", "LBXSTB": "Bilirubin", "LBXPLTSI": "Platelets",
          "LBDHDD": "HDL"}
SEED = 20260301

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def metrics(y, p, threshold):
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    n = len(y)
    pos = int(y.sum())
    neg = n - pos
    return dict(n=n, positives=pos, negatives=neg, prevalence=pos / n,
                sensitivity=tp / pos if pos else np.nan,
                specificity=tn / neg if neg else np.nan,
                fnr=fn / pos if pos else np.nan, fpr=fp / neg if neg else np.nan,
                ppv=tp / (tp + fp) if tp + fp else np.nan,
                npv=tn / (tn + fn) if tn + fn else np.nan,
                tp=int(tp), fn=int(fn), tn=int(tn), fp=int(fp))

def boot_ci(fn, n=500):
    rng = np.random.default_rng(SEED)
    vals = []
    for _ in range(n):
        v = fn(rng)
        if np.isfinite(v):
            vals.append(v)
    return (np.quantile(vals, .025), np.quantile(vals, .975)) if vals else (np.nan, np.nan)

def fdr(pvals):
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(np.nan_to_num(p, nan=1.0))
    q = np.full(len(p), np.nan)
    valid = np.isfinite(p)
    pv = p[order]
    ranks = np.arange(1, len(p) + 1)
    adj = np.minimum.accumulate((pv * len(p) / ranks)[::-1])[::-1]
    q[order] = np.minimum(adj, 1.0)
    q[~valid] = np.nan
    return q

def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        if mask.any():
            total += mask.mean() * abs(y[mask].mean() - p[mask].mean())
    return total

def main():
    cohort = pd.read_parquet(DATA / "analysis_dataset_primary.parquet")
    val_ids = set(pd.read_csv(DATA / "splits" / "validation_ids.csv")["SEQN"])
    oof = {}
    for model in MODELS:
        path = PRED / f"validation_predictions_{model}.csv"
        d = pd.read_csv(path)
        if len(d) != 5007 or set(d.SEQN) != val_ids:
            raise RuntimeError(f"OOF lineage failure for {model}")
        oof[model] = cohort.merge(d, on="SEQN", validate="one_to_one")
        if not np.array_equal(oof[model]["outcome_primary_8.2kPa"], oof[model].true_target):
            raise RuntimeError(f"Outcome mismatch for {model}")
    base = oof["logistic"].drop(columns=["predicted_probability", "true_target"]).copy()
    base["true_target"] = base["outcome_primary_8.2kPa"].astype(int)
    base["bmi_group"] = pd.cut(base.BMXBMI, [0, 18.5, 24.9, 29.9, 200],
                               labels=["Underweight", "Normal", "Overweight", "Obese"])
    base["age_group"] = pd.cut(base.RIDAGEYR, [18, 39, 59, 120],
                               labels=["18-39", "40-59", "60+"])
    base["bmi_binary"] = base.bmi_group.map({"Obese": "Obese", "Normal": "Normal-BMI"})
    base = base[base.bmi_binary.notna()].copy()

    threshold_rows = []
    grid = np.round(np.linspace(0, 1, 101), 2)
    for model in MODELS:
        d = base[["SEQN", "true_target", "bmi_binary"]].merge(
            oof[model][["SEQN", "predicted_probability"]], on="SEQN")
        for t in grid:
            for group in ["Normal-BMI", "Obese"]:
                m = metrics(d.loc[d.bmi_binary == group, "true_target"].to_numpy(),
                             d.loc[d.bmi_binary == group, "predicted_probability"].to_numpy(), t)
                threshold_rows.append({"model": DISPLAY[model], "model_key": model,
                    "threshold": t, "bmi_group": group, **m})
    threshold = pd.DataFrame(threshold_rows)
    for metric in ["sensitivity", "specificity"]:
        key = threshold.pivot_table(index=["model_key", "threshold"], columns="bmi_group", values=metric)
        diff = (key["Obese"] - key["Normal-BMI"]).rename(f"obese_minus_normal_{metric}").reset_index()
        threshold = threshold.merge(diff, on=["model_key", "threshold"], how="left")
    threshold.to_csv(OUT / "phase2_oof_threshold_grid.csv", index=False)

    disc_rows, positive_rows, negative_rows, crossing_rows, cal_rows = [], [], [], [], []
    for model in MODELS:
        d = base.merge(oof[model][["SEQN", "predicted_probability"]], on="SEQN")
        for group in ["Normal-BMI", "Obese"]:
            z = d[d.bmi_binary == group]
            y, p = z.true_target.to_numpy(), z.predicted_probability.to_numpy()
            auc = roc_auc_score(y, p)
            ap = average_precision_score(y, p)
            def auc_boot(r):
                idx = r.choice(len(y), len(y), True)
                return roc_auc_score(y[idx], p[idx]) if len(np.unique(y[idx])) == 2 else np.nan
            ci = boot_ci(auc_boot)
            disc_rows.append({"model": DISPLAY[model], "model_key": model, "bmi_group": group,
                "n": len(y), "positives": int(y.sum()), "auroc": auc, "auroc_ci_low": ci[0],
                "auroc_ci_high": ci[1], "pr_auc": ap, "frozen_threshold": THRESHOLDS[model]})
            for outcome, label in [(1, "positive_fibrosis"), (0, "negative_no_fibrosis")]:
                s = z.loc[z.true_target == outcome, "predicted_probability"].to_numpy()
                positive_rows.append({"model": DISPLAY[model], "model_key": model,
                    "case_type": label, "bmi_group": group, "n": len(s),
                    "median": np.median(s), "q25": np.quantile(s, .25), "q75": np.quantile(s, .75),
                    "q05": np.quantile(s, .05), "q95": np.quantile(s, .95),
                    "mean": np.mean(s), "sd": np.std(s, ddof=1)})
            zpos = d[(d.bmi_binary == group) & (d.true_target == 1)]
            cm = metrics(zpos.true_target.to_numpy(), zpos.predicted_probability.to_numpy(),
                         THRESHOLDS[model])
            crossing_rows.append({"model": DISPLAY[model], "model_key": model, "bmi_group": group,
                "positive_n": len(zpos), "below_threshold_n": int((zpos.predicted_probability < THRESHOLDS[model]).sum()),
                "below_threshold_proportion": float((zpos.predicted_probability < THRESHOLDS[model]).mean()),
                "above_or_equal_threshold_n": int((zpos.predicted_probability >= THRESHOLDS[model]).sum()),
                "above_or_equal_threshold_proportion": float((zpos.predicted_probability >= THRESHOLDS[model]).mean()),
                "false_negative_rate": cm["fnr"], "threshold": THRESHOLDS[model]})
            for group in ["Normal-BMI", "Obese"]:
                zc = d[d.bmi_binary == group]
                y, p = zc.true_target.to_numpy(), zc.predicted_probability.to_numpy()
                logit = np.log(np.clip(p, 1e-12, 1-1e-12) / np.clip(1-p, 1e-12, 1))
                reg = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000)
                reg.fit(logit.reshape(-1, 1), y)
                cal_rows.append({"model": DISPLAY[model], "model_key": model, "bmi_group": group,
                    "n": len(y), "calibration_intercept": reg.intercept_[0],
                    "calibration_slope": reg.coef_[0][0], "brier": brier_score_loss(y, p),
                    "ece_10_equal_width": ece(y, p)})
        # diagnostic plots
        fig, ax = plt.subplots(figsize=(7, 5))
        for group, color in [("Normal-BMI", "tab:blue"), ("Obese", "tab:orange")]:
            q = threshold[(threshold.model_key == model) & (threshold.bmi_group == group)]
            ax.plot(q.threshold, q.sensitivity, label=f"{group} sensitivity", color=color)
        ax.axvline(THRESHOLDS[model], color="black", ls="--", label="frozen threshold")
        ax.set(xlabel="Probability threshold", ylabel="Sensitivity", title=f"{DISPLAY[model]}: OOF threshold diagnostic")
        ax.legend(); fig.tight_layout(); fig.savefig(FIG / f"{model}_threshold_sensitivity.png", dpi=160); plt.close(fig)
        fig, ax = plt.subplots(figsize=(7, 5))
        for group, color in [("Normal-BMI", "tab:blue"), ("Obese", "tab:orange")]:
            z = d[d.bmi_binary == group]; fpr, tpr, _ = roc_curve(z.true_target, z.predicted_probability)
            ax.plot(fpr, tpr, label=group)
        ax.plot([0,1],[0,1], "k:")
        ax.set(xlabel="False-positive rate", ylabel="True-positive rate", title=f"{DISPLAY[model]}: OOF ROC by BMI")
        ax.legend(); fig.tight_layout(); fig.savefig(FIG / f"{model}_roc_bmi.png", dpi=160); plt.close(fig)
        fig, ax = plt.subplots(figsize=(7, 5))
        for group, color in [("Normal-BMI", "tab:blue"), ("Obese", "tab:orange")]:
            z = d[d.bmi_binary == group]
            ax.hist(z.loc[z.true_target == 1, "predicted_probability"], bins=20, alpha=.45,
                    density=True, label=f"{group} fibrosis", color=color)
        ax.axvline(THRESHOLDS[model], color="black", ls="--", label="frozen threshold")
        ax.set(xlabel="OOF predicted probability", ylabel="Density", title=f"{DISPLAY[model]}: positive-case scores")
        ax.legend(); fig.tight_layout(); fig.savefig(FIG / f"{model}_positive_scores.png", dpi=160); plt.close(fig)
        fig, ax = plt.subplots(figsize=(6, 5))
        for group, color in [("Normal-BMI", "tab:blue"), ("Obese", "tab:orange")]:
            z = d[d.bmi_binary == group]
            order = np.argsort(z.predicted_probability.to_numpy())
            ax.plot(z.predicted_probability.to_numpy()[order],
                    z.true_target.to_numpy()[order], ".", alpha=.12, color=color, label=group)
        ax.plot([0, 1], [0, 1], "k:", alpha=.5)
        ax.set(xlabel="Predicted probability", ylabel="Observed outcome", title=f"{DISPLAY[model]}: BMI calibration scatter")
        ax.legend(); fig.tight_layout(); fig.savefig(FIG / f"{model}_calibration_bmi.png", dpi=160); plt.close(fig)
    disc = pd.DataFrame(disc_rows)
    disc["auroc_group_difference"] = disc.groupby("model_key").auroc.transform(
        lambda x: x.iloc[-1] - x.iloc[0] if len(x) == 2 else np.nan)
    disc.to_csv(OUT / "phase2_subgroup_discrimination.csv", index=False)
    scores = pd.DataFrame(positive_rows)
    for case_type in ["positive_fibrosis", "negative_no_fibrosis"]:
        for model in MODELS:
            a = d = base.merge(oof[model][["SEQN", "predicted_probability"]], on="SEQN")
            a = d[(d.bmi_binary == "Normal-BMI") & (d.true_target == (1 if case_type == "positive_fibrosis" else 0))].predicted_probability
            b = d[(d.bmi_binary == "Obese") & (d.true_target == (1 if case_type == "positive_fibrosis" else 0))].predicted_probability
            pval = mannwhitneyu(a, b, alternative="two-sided").pvalue
            u = mannwhitneyu(a, b, alternative="two-sided")
            effect = 2 * u.statistic / (len(a) * len(b)) - 1
            mask = (scores.model_key == model) & (scores.case_type == case_type)
            scores.loc[mask, "normal_vs_obese_p"] = pval
            scores.loc[mask, "rank_biserial_effect_obese_vs_normal"] = effect
    scores.to_csv(OUT / "phase2_positive_case_scores.csv", index=False)
    scores.query("case_type == 'negative_no_fibrosis'").to_csv(OUT / "phase2_negative_case_scores.csv", index=False)
    pd.DataFrame(crossing_rows).to_csv(OUT / "phase2_threshold_crossing.csv", index=False)
    pd.DataFrame(cal_rows).to_csv(OUT / "phase2_calibration_by_bmi.csv", index=False)

    pred_rows = []
    for var in PREDICTORS:
        a, b = base[base.bmi_binary=="Normal-BMI"][var].dropna(), base[base.bmi_binary=="Obese"][var].dropna()
        pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1))/2)
        pred_rows.extend([
            {"predictor": LABELS[var], "predictor_code": var, "bmi_group": "Normal-BMI", "n": len(a),
             "mean": a.mean(), "sd": a.std(ddof=1), "median": a.median(), "q25": a.quantile(.25), "q75": a.quantile(.75)},
            {"predictor": LABELS[var], "predictor_code": var, "bmi_group": "Obese", "n": len(b),
             "mean": b.mean(), "sd": b.std(ddof=1), "median": b.median(), "q25": b.quantile(.25), "q75": b.quantile(.75),
             "standardized_mean_difference": (b.mean()-a.mean())/pooled if pooled else np.nan,
             "welch_p": ttest_ind(a, b, equal_var=False).pvalue},
        ])
    pd.DataFrame(pred_rows).to_csv(OUT / "phase2_predictor_distributions.csv", index=False)
    fig, axes = plt.subplots(2, 5, figsize=(16, 6))
    for ax, var in zip(axes.ravel(), PREDICTORS):
        for group, color in [("Normal-BMI", "tab:blue"), ("Obese", "tab:orange")]:
            ax.hist(base.loc[base.bmi_binary == group, var].dropna(), bins=20, alpha=.4,
                    density=True, label=group, color=color)
        ax.set_title(LABELS[var], fontsize=9)
    axes[0, 0].legend(fontsize=8); fig.tight_layout()
    fig.savefig(FIG / "predictor_distributions_bmi.png", dpi=160); plt.close(fig)

    age_rows = []
    for model in MODELS:
        d = base.merge(oof[model][["SEQN", "predicted_probability"]], on="SEQN")
        for age in ["18-39", "40-59", "60+"]:
            for group in ["Normal-BMI", "Obese"]:
                z = d[(d.age_group == age) & (d.bmi_binary == group)]
                y, p = z.true_target.to_numpy(), z.predicted_probability.to_numpy()
                m = metrics(y, p, THRESHOLDS[model]) if len(z) else {}
                age_rows.append({"model": DISPLAY[model], "model_key": model, "age_group": age,
                    "bmi_group": group, "n": len(z), "positive_n": int(y.sum()) if len(z) else 0,
                    "prevalence": y.mean() if len(z) else np.nan,
                    "sensitivity": m.get("sensitivity", np.nan), "specificity": m.get("specificity", np.nan),
                    "false_negative_rate": m.get("fnr", np.nan),
                    "auroc": roc_auc_score(y,p) if len(np.unique(y))==2 else np.nan,
                    "stability_flag": "UNSTABLE_SMALL_CELL" if len(z)<100 or y.sum()<10 or (len(z)-y.sum())<10 else "ESTIMABLE"})
    pd.DataFrame(age_rows).to_csv(OUT / "phase2_bmi_age_analysis.csv", index=False)

    lineage = {"oof_files": {m: sha256(PRED / f"validation_predictions_{m}.csv") for m in MODELS},
               "cohort_file": sha256(DATA / "analysis_dataset_primary.parquet"),
               "n_oof": 5007, "bmi_definition": "pd.cut bins [0,18.5,24.9,29.9,200], right-inclusive",
               "age_definition": "pd.cut bins [18,39,59,120], labels 18-39/40-59/60+",
               "threshold_grid": "0.00 through 1.00 inclusive, step 0.01; no threshold selected"}
    (OUT / "phase2_lineage.json").write_text(json.dumps(lineage, indent=2))

if __name__ == "__main__":
    main()
