"""
phase5_01_subgroup_feasibility.py
Phase 5 Part 3: subgroup data integrity + feasibility table, for (A) the full primary cohort
(N=7,153) and (B) the locked test set (N=2,146). No fairness metric is computed here -- only
counts and precision-tier classification.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase5_common import (
    FAIR_RESULTS_DIR, DIMENSIONS, precision_tier, load_demographics, NOW, fail,
)
from phase3_common import SPLIT_DIR, PRIMARY_OUTCOME_COL

demo = load_demographics()
if demo["SEQN"].nunique() != len(demo):
    fail(f"Duplicate SEQN in demographic source: {len(demo)} rows, {demo['SEQN'].nunique()} unique")
if demo[PRIMARY_OUTCOME_COL].isna().any():
    fail("Missing outcome values in primary cohort")
for dim, spec in DIMENSIONS.items():
    n_missing = demo[spec["col"]].isna().sum()
    if n_missing > 0:
        fail(f"Missing {spec['col']} values found ({n_missing}) -- frozen protocol states 0 missing expected")

test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"].tolist())
if len(test_ids) != 2146:
    fail(f"Test-set ID count mismatch: expected 2146, found {len(test_ids)}")

rows = []
for population_label, pop_df in [("full_primary_cohort", demo), ("locked_test_set", demo[demo["SEQN"].isin(test_ids)])]:
    if population_label == "locked_test_set" and len(pop_df) != 2146:
        fail(f"Locked test-set demographic join produced {len(pop_df)} rows, expected 2146")
    for dim, spec in DIMENSIONS.items():
        pop_df = pop_df.copy()
        pop_df["_bin"] = pop_df[spec["col"]].apply(spec["map_fn"])
        for bin_name, g in pop_df.groupby("_bin", observed=True):
            n = len(g)
            n_pos = int((g[PRIMARY_OUTCOME_COL] == 1).sum())
            n_neg = int((g[PRIMARY_OUTCOME_COL] == 0).sum())
            rows.append({
                "generated": NOW, "population": population_label, "dimension": dim, "category": bin_name,
                "is_reference_group": bin_name == spec["reference"],
                "n": n, "n_positive": n_pos, "n_negative": n_neg,
                "prevalence_pct": round(100 * n_pos / n, 4) if n else None,
                "precision_tier": precision_tier(n_pos, n_neg),
            })

out = pd.DataFrame(rows)
out.to_csv(FAIR_RESULTS_DIR / "subgroup_feasibility_table.csv", index=False)
print(out.to_string(index=False))
print(f"\nSaved results/fairness/subgroup_feasibility_table.csv ({len(out)} rows)")

# Cross-check against fairness_subgroup_protocol.md's frozen full-cohort counts
EXPECTED_FULL_COHORT = {
    ("sex", "Male"): (3531, 394), ("sex", "Female"): (3622, 272),
    ("race_ethnicity", "Mexican American"): (902, 94), ("race_ethnicity", "Other Hispanic"): (754, 69),
    ("race_ethnicity", "Non-Hispanic White"): (2484, 237), ("race_ethnicity", "Non-Hispanic Black"): (1787, 177),
    ("race_ethnicity", "Non-Hispanic Asian"): (866, 52), ("race_ethnicity", "Other Race / Multi-Racial"): (360, 37),
    ("age", "18-39"): (2423, 122), ("age", "40-59"): (2318, 221), ("age", "60+"): (2412, 323),
    ("bmi", "Underweight"): (109, 5), ("bmi", "Normal"): (1802, 72), ("bmi", "Overweight"): (2316, 121),
    ("bmi", "Obese"): (2926, 468),
}
full = out[out["population"] == "full_primary_cohort"].set_index(["dimension", "category"])
mismatches = []
for (dim, cat), (exp_n, exp_pos) in EXPECTED_FULL_COHORT.items():
    row = full.loc[(dim, cat)]
    if int(row["n"]) != exp_n or int(row["n_positive"]) != exp_pos:
        mismatches.append((dim, cat, exp_n, exp_pos, int(row["n"]), int(row["n_positive"])))
if mismatches:
    fail(f"Live-computed subgroup counts do not match fairness_subgroup_protocol.md's frozen counts: {mismatches}")
print("\nPASS: all live-computed full-cohort subgroup counts match fairness_subgroup_protocol.md exactly.")
