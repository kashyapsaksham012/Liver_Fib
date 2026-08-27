"""
Manuscript prep (post evidence-freeze, descriptive only).

Builds Table 1 (baseline characteristics of the primary analytic cohort, N=7,153,
overall and by significant-fibrosis status) from the FROZEN analysis dataset.

Reads only `data/processed/analysis_dataset_primary.parquet`. Computes no model,
no prediction, no analysis result -- descriptive summary statistics only.
Outputs:
  results/tables/manuscript_table1_by_fibrosis.csv
  results/tables/manuscript_table1_by_fibrosis.md

Not a protocol amendment: no frozen artifact is modified and no inferential
result is produced.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_parquet(ROOT / "data/processed/analysis_dataset_primary.parquet")

OUT = "outcome_primary_8.2kPa"
pos = df[df[OUT] == 1]
neg = df[df[OUT] == 0]

CONT = [
    ("RIDAGEYR", "Age, years"),
    ("BMXBMI", "Body-mass index, kg/m^2"),
    ("LBXSATSI", "ALT, U/L"),
    ("LBXSASSI", "AST, U/L"),
    ("LBXSAL", "Albumin, g/dL"),
    ("LBXSAPSI", "Alkaline phosphatase, IU/L"),
    ("LBXSTB", "Total bilirubin, mg/dL"),
    ("LBXPLTSI", "Platelet count, 10^9/L"),
    ("LBDHDD", "HDL cholesterol, mg/dL"),
    ("LUXSMED", "Liver stiffness (VCTE), kPa"),
]
SEX = {1: "Male", 2: "Female"}
RETH = {1: "Mexican American", 2: "Other Hispanic", 3: "Non-Hispanic White",
        4: "Non-Hispanic Black", 6: "Non-Hispanic Asian", 7: "Other / multi-racial"}


def fmt_cont(s):
    return f"{s.mean():.1f} ({s.std():.1f})"


def fmt_med(s):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    return f"{s.median():.1f} [{q1:.1f}-{q3:.1f}]"


def fmt_cat(s, level):
    n = int((s == level).sum())
    return f"{n} ({100 * n / len(s):.1f})"


rows = []
rows.append(["N", f"{len(df)}", f"{len(neg)}", f"{len(pos)}", ""])
rows.append(["Significant fibrosis (>= 8.2 kPa), n (%)",
             fmt_cat(df[OUT], 1), "0 (0.0)", f"{len(pos)} (100.0)", ""])

# continuous: mean (SD) + Welch t-test
for col, label in CONT:
    a, b = neg[col].dropna(), pos[col].dropna()
    p = stats.ttest_ind(a, b, equal_var=False).pvalue
    rows.append([f"{label}, mean (SD)", fmt_cont(df[col].dropna()),
                 fmt_cont(a), fmt_cont(b), f"{p:.3g}"])

# sex
p = stats.chi2_contingency(pd.crosstab(df["RIAGENDR"], df[OUT]))[1]
rows.append(["Sex, n (%)", "", "", "", f"{p:.3g}"])
for k, name in SEX.items():
    rows.append([f"  {name}", fmt_cat(df["RIAGENDR"], k),
                 fmt_cat(neg["RIAGENDR"], k), fmt_cat(pos["RIAGENDR"], k), ""])

# race/ethnicity
p = stats.chi2_contingency(pd.crosstab(df["RIDRETH3"], df[OUT]))[1]
rows.append(["Race / ethnicity, n (%)", "", "", "", f"{p:.3g}"])
for k, name in RETH.items():
    rows.append([f"  {name}", fmt_cat(df["RIDRETH3"], k),
                 fmt_cat(neg["RIDRETH3"], k), fmt_cat(pos["RIDRETH3"], k), ""])

# age band
p = stats.chi2_contingency(pd.crosstab(df["age_group_final"], df[OUT]))[1]
rows.append(["Age band, n (%)", "", "", "", f"{p:.3g}"])
for lvl in df["age_group_final"].cat.categories:
    rows.append([f"  {lvl}", fmt_cat(df["age_group_final"], lvl),
                 fmt_cat(neg["age_group_final"], lvl), fmt_cat(pos["age_group_final"], lvl), ""])

# bmi band
p = stats.chi2_contingency(pd.crosstab(df["bmi_group_final"], df[OUT]))[1]
rows.append(["BMI band, n (%)", "", "", "", f"{p:.3g}"])
for lvl in df["bmi_group_final"].cat.categories:
    rows.append([f"  {lvl}", fmt_cat(df["bmi_group_final"], lvl),
                 fmt_cat(neg["bmi_group_final"], lvl), fmt_cat(pos["bmi_group_final"], lvl), ""])

out = pd.DataFrame(rows, columns=["Characteristic", "Overall (N=7,153)",
                                  f"No fibrosis (n={len(neg)})",
                                  f"Significant fibrosis (n={len(pos)})",
                                  "p"])
out.to_csv(ROOT / "results/tables/manuscript_table1_by_fibrosis.csv", index=False)

md = ["# Table 1 - Baseline characteristics of the primary analytic cohort",
      "",
      f"Primary cohort N = {len(df)} ({len(pos)} with significant fibrosis; "
      f"{100*len(pos)/len(df):.2f}% prevalence). Continuous variables: mean (SD); "
      "Welch t-test. Categorical: n (%); chi-square. Liver stiffness (VCTE) is the "
      "outcome measurement, shown for description only.",
      "",
      "| " + " | ".join(out.columns) + " |",
      "|" + "|".join(["---"] * len(out.columns)) + "|"]
for _, r in out.iterrows():
    md.append("| " + " | ".join(str(x) for x in r) + " |")
(ROOT / "results/tables/manuscript_table1_by_fibrosis.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
