"""Phase 3 — population / predictor / lab-method drift audit.

Descriptive only. Compares the 2021-2023 cohort to the frozen 2017-2020 analysis
dataset. Builds the evidence base for "transport failure vs population change" and
flags lab-method changes. No outcome-conditional modelling.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from _thelpers import REPO, TV, PREDICTORS, LAB_PREDICTORS

OUT = TV / "results"
OUT.mkdir(parents=True, exist_ok=True)

# NHANES analytic-note continuity, 2017-March 2020 -> Aug 2021-Aug 2023.
# Verify each against the NHANES lab documentation before the write-up; this is
# the starting map from the temporal-validation-standalone branch + NHANES docs.
LAB_METHOD_NOTES = {
    "LBXSATSI": "ALT — NHANES moved the biochemistry profile to the Roche Cobas c501/6000 "
                "platform for the 2021-2023 cycle; the standalone branch built an ALT crosswalk. "
                "PRIMARY analysis uses raw values; crosswalk = sensitivity only. VERIFY analytic note.",
    "LBXSASSI": "AST — same platform change as ALT. VERIFY analytic note for a method/units shift.",
    "LBXSAL":   "Albumin — VERIFY (BCG vs BCP method history in NHANES).",
    "LBXSAPSI": "Alkaline phosphatase — VERIFY analytic note.",
    "LBXSTB":   "Total bilirubin — VERIFY analytic note.",
    "LBXPLTSI": "Platelets (CBC) — Sysmex analyzer; generally stable across cycles. VERIFY.",
    "LBDHDD":   "HDL cholesterol — VERIFY analytic note.",
}


def smd(a, b):
    """standardized mean difference"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    sp = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return (b.mean() - a.mean()) / sp if sp > 0 else 0.0


def ks(a, b):
    from scipy.stats import ks_2samp
    return float(ks_2samp(a, b).statistic)


def main():
    old = pd.read_parquet(REPO / "data" / "processed" / "analysis_dataset_primary.parquet")
    new = pd.read_parquet(TV / "data" / "processed" / "temporal_cohort_2021_2023.parquet")

    rows = []
    for col in PREDICTORS:
        a, b = old[col].dropna().values, new[col].dropna().values
        rows.append({
            "predictor": col,
            "mean_2017_2020": round(float(a.mean()), 3),
            "mean_2021_2023": round(float(b.mean()), 3),
            "sd_2017_2020": round(float(a.std(ddof=1)), 3),
            "sd_2021_2023": round(float(b.std(ddof=1)), 3),
            "standardized_mean_diff": round(smd(a, b), 3),
            "ks_distance": round(ks(a, b), 3),
            "lab_method_note": LAB_METHOD_NOTES.get(col, "demographic/anthropometric — no lab-method concern"),
        })
    drift = pd.DataFrame(rows)
    drift.to_csv(OUT / "temporal_predictor_drift.csv", index=False)

    # composition drift
    comp_rows = []
    for dim, col in [("age_band", "age_group_final"), ("bmi_band", "bmi_group_final"),
                     ("sex", "RIAGENDR"), ("race", "RIDRETH3")]:
        oc = old[col].value_counts(normalize=True).sort_index()
        nc = new[col if col != "RIDRETH3" else "RIDRETH3"].value_counts(normalize=True).sort_index()
        for cat in sorted(set(oc.index) | set(nc.index)):
            comp_rows.append({
                "dimension": dim, "category": str(cat),
                "pct_2017_2020": round(100 * oc.get(cat, 0), 2),
                "pct_2021_2023": round(100 * nc.get(cat, 0), 2),
            })
    comp = pd.DataFrame(comp_rows)
    comp.to_csv(OUT / "temporal_composition_drift.csv", index=False)

    # outcome / stiffness drift
    od = pd.DataFrame([{
        "metric": "prevalence_pct",
        "value_2017_2020": round(100 * old["outcome_primary_8.2kPa"].mean(), 3),
        "value_2021_2023": round(100 * new["outcome_primary_8.2kPa"].mean(), 3),
    }, {
        "metric": "mean_LUXSMED_kPa",
        "value_2017_2020": round(float(old["LUXSMED"].mean()), 3),
        "value_2021_2023": round(float(new["LUXSMED"].mean()), 3),
    }, {
        "metric": "median_LUXSMED_kPa",
        "value_2017_2020": round(float(old["LUXSMED"].median()), 3),
        "value_2021_2023": round(float(new["LUXSMED"].median()), 3),
    }])
    od.to_csv(OUT / "temporal_outcome_drift.csv", index=False)

    # markdown report
    md = ["# Temporal drift audit — NHANES 2021-2023 vs frozen 2017-March 2020", "",
          "Descriptive, pre-touch. Positive standardized mean difference = higher in 2021-2023.", "",
          "## Predictor distribution drift", "",
          drift[["predictor", "mean_2017_2020", "mean_2021_2023", "standardized_mean_diff", "ks_distance"]]
          .to_markdown(index=False), "",
          "**|SMD| > 0.2 or KS > 0.1 flags a material shift.** Any such shift on a *lab* "
          "predictor must be checked against the NHANES analytic note for a method change "
          "before interpreting a discrimination drop.", "",
          "## Lab-method continuity (to verify against NHANES analytic notes)", ""]
    for k, v in LAB_METHOD_NOTES.items():
        md.append(f"- **{k}** — {v}")
    md += ["", "## Composition drift", "", comp.to_markdown(index=False), "",
           "## Outcome / stiffness drift", "", od.to_markdown(index=False), "",
           "## Reading", "",
           f"- Outcome prevalence rose {od.loc[0,'value_2017_2020']}% -> {od.loc[0,'value_2021_2023']}% "
           "(consistent with post-pandemic metabolic shift).",
           "- A materially higher BMI / ALT / AST distribution in 2021-2023 means a later-cycle "
           "AUROC drop is confounded between *model non-transport* and *genuine population change* "
           "(and, for the enzymes, a possible analyzer change). This is stated as a limitation, "
           "not resolved."]
    (TV / "documentation" / "TEMPORAL_DRIFT_AUDIT.md").write_text("\n".join(md) + "\n")

    print(drift[["predictor", "mean_2017_2020", "mean_2021_2023", "standardized_mean_diff", "ks_distance"]].to_string(index=False))
    print()
    print(od.to_string(index=False))
    flagged = drift[(drift.standardized_mean_diff.abs() > 0.2) | (drift.ks_distance > 0.1)]
    print("\nFLAGGED (|SMD|>0.2 or KS>0.1):", list(flagged.predictor) or "none")
    print(f"\nwrote {OUT/'temporal_predictor_drift.csv'}, temporal_composition_drift.csv, temporal_outcome_drift.csv")
    print(f"wrote {TV/'documentation'/'TEMPORAL_DRIFT_AUDIT.md'}")


if __name__ == "__main__":
    main()
