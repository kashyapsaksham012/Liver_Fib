"""
generate_table8_csv.py
Save Table 8 (M4b Prior Art Comparison) to CSV format
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = ROOT / "results" / "tables"
DIAG_DIR = ROOT / "results" / "diagnostics" / "stage1"

rows = [
    {
        "method_name": "M1: Global Split-Conformal Baseline",
        "core_formulation": "q_global = Quantile_{1-alpha}({s_i})",
        "structural_similarities": "Computes nonconformity scores on calibration split",
        "critical_differences": "Uniform threshold; ignores intersectional disparities",
        "relationship_and_classification": "Baseline comparison model"
    },
    {
        "method_name": "M2: Sequential Mondrian",
        "core_formulation": "q(x) = q_{S(x)}",
        "structural_similarities": "Demographic subgroup conditional quantile fitting",
        "critical_differences": "Single-dimension grouping only; ignores interaction",
        "relationship_and_classification": "Precedence baseline"
    },
    {
        "method_name": "M3: Pure Joint Intersectional",
        "core_formulation": "q_joint = Quantile_{1-alpha}({s_i | i in c})",
        "structural_similarities": "Exact intersectional cell targeting (N_c=138)",
        "critical_differences": "High quantile variance; unstable in small cells",
        "relationship_and_classification": "Unregularized precursor"
    },
    {
        "method_name": "Hierarchical Empirical Bayes Conformal",
        "core_formulation": "q_c = w_c * q_c^{emp} + (1-w_c) * q_global",
        "structural_similarities": "Precision-weighted shrinkage (w = N_c / (N_c + N_0))",
        "critical_differences": "Shrinks toward global marginal quantile q_global",
        "relationship_and_classification": "Methodological inspiration"
    },
    {
        "method_name": "Enveloped Mondrian (M4a)",
        "core_formulation": "q_env = max(q_BMI, q_Age)",
        "structural_similarities": "Uses component subgroup maximum quantile",
        "critical_differences": "Constant prior weight; no joint sample updates",
        "relationship_and_classification": "Base prior for M4b"
    },
    {
        "method_name": "M4b: Precision-Weighted Shrinkage",
        "core_formulation": "q_M4b = w * q_joint + (1-w) * max(q_BMI, q_Age)",
        "structural_similarities": "Integrates joint sample size N_c and single-dimension prior",
        "critical_differences": "Shrinks toward single-dimension envelope instead of global",
        "relationship_and_classification": "Domain-adapted empirical Bayes extension"
    }
]

df_table8 = pd.DataFrame(rows)
df_table8.to_csv(TABLES_DIR / "m4b_prior_art_comparison.csv", index=False)
df_table8.to_csv(DIAG_DIR / "m4b_prior_art_comparison.csv", index=False)

print("Saved Table 8 CSV to results/tables/m4b_prior_art_comparison.csv")
