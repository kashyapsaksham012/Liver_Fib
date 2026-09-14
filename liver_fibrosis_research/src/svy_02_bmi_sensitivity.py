"""
svy_02_bmi_sensitivity.py
C6/E3 addendum (part 2) -- survey-weighted BMI-subgroup sensitivity disparity, run ALONGSIDE
(not replacing) the primary unweighted fairness_inference.csv result.

Sensitivity within a subgroup is a domain ratio: sum(w * true_positive_and_predicted_positive)
/ sum(w * true_positive), restricted to the domain {locked test set} x {BMI subgroup}. This is
estimated via samplics.TaylorEstimator(param="ratio") with a `domain` argument, using the FULL
frozen primary cohort's stratum/PSU structure (N=7,153, all 24 strata have >=2 PSUs) rather than
subsetting the design object to the 2,146-row test set -- subsetting a design object before
estimation is a known way to bias domain variance downward; passing the full design with a
domain indicator is the standard correct method (NHANES analytic guidelines; R survey::svyby /
Stata svy: subpop use the same principle).

Limitation stated here, not hidden: each domain (Normal, Obese) is estimated independently.
This gives a valid design-based CI for each subgroup's weighted sensitivity, but NOT a formal
design-based CI for the Obese-minus-Normal DIFFERENCE, which would require a custom Taylor
delta-method covariance term between the two domains under the shared design (beyond what this
off-the-shelf domain/ratio estimator directly outputs). The point-estimate gap and whether the
two domains' CIs overlap are reported instead, as a sensitivity check on direction/magnitude,
not as a formal significance test on the gap itself.

Output: results/sensitivity/survey_weighted/svy_bmi_sensitivity.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from samplics.estimation import TaylorEstimator
from samplics.utils.types import PopParam

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, PROC_DIR, SPLIT_DIR, PRED_DIR, PRIMARY_OUTCOME_COL, MODEL_NAMES, fail

OUT_DIR = ROOT / "results" / "sensitivity" / "survey_weighted"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
if len(df) != 7153:
    fail(f"Primary dataset has {len(df)} rows, expected 7153")
test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])

rows = []
for model in MODEL_NAMES:
    pred = pd.read_csv(PRED_DIR / f"test_predictions_{model}.csv")[["SEQN", "predicted_class"]]
    merged = df.merge(pred, on="SEQN", how="left")
    merged["predicted_class"] = merged["predicted_class"].fillna(0).astype(int)
    merged["is_test"] = merged["SEQN"].isin(test_ids)

    # Only Normal/Obese-in-test are reported; every other row (non-test, or test but
    # Underweight/Overweight) is pooled into a single "OTHER" domain. This is purely a
    # bucketing convenience for the domains we report -- it does not affect the Normal/Obese
    # domain estimates, which depend only on their own indicator, not on how the remainder is
    # split up. (Splitting the remainder into several thin domains, e.g. Underweight-in-test
    # with 1 positive, crashed the archived samplics library on a zero-ratio internal
    # calculation unrelated to the domains actually reported here.)
    is_reported_bmi = merged["bmi_group_final"].isin(["Normal", "Obese"])
    merged["domain_label"] = np.where(merged["is_test"] & is_reported_bmi,
                                       merged["bmi_group_final"].astype(str), "OTHER")
    y = ((merged[PRIMARY_OUTCOME_COL] == 1) & (merged["predicted_class"] == 1)).astype(int).values
    x = (merged[PRIMARY_OUTCOME_COL] == 1).astype(int).values

    est = TaylorEstimator(param=PopParam.ratio)
    est.estimate(
        y=y, x=x, samp_weight=merged["WTMECPRP"].values,
        stratum=merged["SDMVSTRA"].values, psu=merged["SDMVPSU"].values,
        domain=merged["domain_label"].values, remove_nan=True,
    )
    res = est.to_dataframe()

    for bmi_cat in ["Normal", "Obese"]:
        r = res[res["_domain"] == bmi_cat]
        if len(r) == 0:
            continue
        r = r.iloc[0]
        # unweighted sensitivity, same domain, for direct side-by-side comparison
        dom_mask = (merged["is_test"]) & (merged["bmi_group_final"] == bmi_cat)
        sub = merged[dom_mask]
        unw_sens = float(((sub[PRIMARY_OUTCOME_COL] == 1) & (sub["predicted_class"] == 1)).sum() /
                          (sub[PRIMARY_OUTCOME_COL] == 1).sum())
        rows.append({
            "model": model, "bmi_group": bmi_cat,
            "n_test_domain": int(dom_mask.sum()), "n_test_domain_positive": int((sub[PRIMARY_OUTCOME_COL] == 1).sum()),
            "unweighted_sensitivity": round(unw_sens, 6),
            "weighted_sensitivity": round(float(r["_estimate"]), 6),
            "weighted_se": round(float(r["_stderror"]), 6),
            "weighted_95ci_low": round(float(r["_lci"]), 6),
            "weighted_95ci_high": round(float(r["_uci"]), 6),
        })

out = pd.DataFrame(rows)
out.to_csv(OUT_DIR / "svy_bmi_sensitivity.csv", index=False)
print(out.to_string(index=False))

# Point-estimate gap, weighted vs unweighted, per model (Obese minus Normal, matching cb_03's orientation)
gap_rows = []
for model in MODEL_NAMES:
    m = out[out["model"] == model].set_index("bmi_group")
    if not {"Normal", "Obese"}.issubset(m.index):
        continue
    gap_rows.append({
        "model": model,
        "unweighted_gap_obese_minus_normal_pp": round((m.loc["Obese", "unweighted_sensitivity"] -
                                                         m.loc["Normal", "unweighted_sensitivity"]) * 100, 4),
        "weighted_gap_obese_minus_normal_pp": round((m.loc["Obese", "weighted_sensitivity"] -
                                                       m.loc["Normal", "weighted_sensitivity"]) * 100, 4),
        "weighted_cis_overlap": bool(m.loc["Obese", "weighted_95ci_low"] <= m.loc["Normal", "weighted_95ci_high"] and
                                      m.loc["Normal", "weighted_95ci_low"] <= m.loc["Obese", "weighted_95ci_high"]),
    })
gap_out = pd.DataFrame(gap_rows)
gap_out.to_csv(OUT_DIR / "svy_bmi_sensitivity_gap_summary.csv", index=False)
print("\n" + gap_out.to_string(index=False))
print("\nSaved results/sensitivity/survey_weighted/svy_bmi_sensitivity.csv")
print("Saved results/sensitivity/survey_weighted/svy_bmi_sensitivity_gap_summary.csv")
