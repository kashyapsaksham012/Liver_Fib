"""
svy_01_prevalence.py
C6/E3 addendum -- survey-weighted sensitivity check (documentation/manuscript/REVISION_PLAN.md,
Change Table C13, New Analysis Queue E3). NOT part of the frozen protocol; adds a robustness
check ALONGSIDE the primary (unweighted, case-level) analysis, replaces nothing.

Re-estimates the marginal prevalence of significant fibrosis using the NHANES complex survey
design: MEC exam weight (WTMECPRP -- correct here because VCTE/LUX is a MEC-collected exam),
masked pseudo-stratum (SDMVSTRA), and masked pseudo-PSU (SDMVPSU), via Taylor-series
linearization (the standard NHANES-recommended method; samplics.TaylorEstimator implements it).
Uses the full frozen primary cohort (N=7,153) -- this is a population question, not tied to the
train/test split.

Output: results/sensitivity/survey_weighted/svy_prevalence.csv
"""
import sys
from pathlib import Path
import pandas as pd
from samplics.estimation import TaylorEstimator
from samplics.utils.types import PopParam

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, PROC_DIR, PRIMARY_OUTCOME_COL, fail

OUT_DIR = ROOT / "results" / "sensitivity" / "survey_weighted"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
if len(df) != 7153:
    fail(f"Primary dataset has {len(df)} rows, expected 7153")
if df[["WTMECPRP", "SDMVPSU", "SDMVSTRA"]].isna().any().any():
    fail("Missing design variables in the frozen primary cohort -- unexpected")

unweighted_prev = df[PRIMARY_OUTCOME_COL].mean()

est = TaylorEstimator(param=PopParam.prop)
est.estimate(
    y=df[PRIMARY_OUTCOME_COL].values,
    samp_weight=df["WTMECPRP"].values,
    stratum=df["SDMVSTRA"].values,
    psu=df["SDMVPSU"].values,
    remove_nan=True,
)
res = est.to_dataframe()
print(res.to_string(index=False))

pos_row = res[res["_level"] == 1].iloc[0]
weighted_prev = float(pos_row["_estimate"])
weighted_lci, weighted_uci, weighted_se = float(pos_row["_lci"]), float(pos_row["_uci"]), float(pos_row["_stderror"])

out = pd.DataFrame([{
    "cohort_n": len(df), "design": "WTMECPRP (MEC exam weight) x SDMVSTRA x SDMVPSU, Taylor linearization",
    "unweighted_prevalence_pct": round(float(unweighted_prev) * 100, 4),
    "weighted_prevalence_pct": round(weighted_prev * 100, 4),
    "weighted_se_pct": round(weighted_se * 100, 4),
    "weighted_95ci_low_pct": round(weighted_lci * 100, 4),
    "weighted_95ci_high_pct": round(weighted_uci * 100, 4),
    "unweighted_estimate_inside_weighted_ci": bool(weighted_lci <= unweighted_prev <= weighted_uci),
}])
out.to_csv(OUT_DIR / "svy_prevalence_summary.csv", index=False)
res.to_csv(OUT_DIR / "svy_prevalence_full_output.csv", index=False)

print(f"\nUnweighted prevalence: {unweighted_prev*100:.4f}%")
print("Full Taylor-linearization output (all levels/CI) saved to svy_prevalence_full_output.csv")
print("Saved results/sensitivity/survey_weighted/svy_prevalence_summary.csv")
