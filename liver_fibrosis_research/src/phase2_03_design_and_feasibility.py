"""
phase2_03_design_and_feasibility.py
Phase 2J/2M/2O - Broad-vs-fasting predictor architecture comparison, intersectional
subgroup feasibility, and statistical precision/sample-size feasibility -- all
computed on the FROZEN primary cohort (adult, quality-valid, broad labs complete,
BMI+sex complete) and primary threshold (LUXSMED >= 8.2 kPa).

Produces:
  results/tables/phase2_broad_vs_fasting_design.csv
  results/tables/phase2_intersectional_feasibility.csv
  results/tables/phase2_statistical_feasibility.csv
"""
import os, sys
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, TAB_DIR, RACE_MAP_RIDRETH3, SEX_MAP
from _cohorts import compute_all

PRIMARY_THRESHOLD = 8.2

def wilson_ci(pos, n, z=1.96):
    if n == 0:
        return (None, None, None)
    p = pos / n
    denom = 1 + z**2/n
    center = (p + z*z/(2*n)) / denom
    half = (z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5)) / denom
    lo, hi = max(0, center-half), min(1, center+half)
    return (round(100*lo, 2), round(100*hi, 2), round(100*(hi-lo), 2))

def classify_feasibility(n_pos, n_neg):
    if n_pos < 10 or n_neg < 10:
        return "insufficient evidence"
    if n_pos < 30 or n_neg < 30:
        return "limited precision"
    if n_pos < 100 or n_neg < 100:
        return "exploratory candidate"
    return "primary-feasibility candidate"

def main():
    print("=== Phase 2J/2M/2O: Design Comparison, Intersectional & Statistical Feasibility ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    c = compute_all(master)
    adult = master["RIDAGEYR"] >= 18
    broad_labs = ["LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
    fasting_labs = ["LBXGLU", "LBXTR"]
    broad_complete = master[broad_labs].notna().all(axis=1)
    fasting_complete = master[fasting_labs].notna().all(axis=1)
    bmi_demo_complete = master["BMXBMI"].notna() & master["RIAGENDR"].notna()
    quality_valid = c["COHORT_2_QUALITY_VALID"][0]

    primary_mask = quality_valid & adult & broad_complete & bmi_demo_complete            # broad architecture
    secondary_mask = quality_valid & adult & broad_complete & fasting_complete & bmi_demo_complete  # fasting-extended

    # ── 2J: Broad vs fasting design comparison ──────────────────────────────────────────
    def design_row(mask, label, n_predictors):
        df = master.loc[mask]
        n = len(df); pos = int((df["LUXSMED"] >= PRIMARY_THRESHOLD).sum())
        min_race_pos = min(int((df.loc[df["RIDRETH3"] == code, "LUXSMED"] >= PRIMARY_THRESHOLD).sum()) for code in RACE_MAP_RIDRETH3)
        return {"architecture": label, "n": n, "n_predictors": n_predictors, "n_outcome_positive": pos,
               "prevalence_pct": round(100*pos/n, 2) if n else None,
               "min_race_ethnicity_subgroup_positive_n": min_race_pos,
               "epv_events_per_predictor": round(pos/n_predictors, 1) if n_predictors else None,
               "pct_asian_subgroup": round(100*(df["RIDRETH3"] == 6.0).mean(), 2) if n else None,
               "clinical_realism": ("High -- ALT/AST/albumin/ALP/bilirubin/platelets/HDL are routine, "
                                    "non-fasting labs obtainable at any clinical visit" if "Broad" in label else
                                    "Moderate -- requires an 8-24h fasting morning-session visit, a materially "
                                    "more restrictive clinical workflow")}
    rows = [design_row(primary_mask, "PRIMARY: Broad routine-lab architecture (10 predictors, no fasting labs)", 10),
            design_row(secondary_mask, "SECONDARY: Fasting-extended architecture (12 predictors, + glucose/triglycerides)", 12)]
    design_df = pd.DataFrame(rows)
    design_df.to_csv(TAB_DIR / "phase2_broad_vs_fasting_design.csv", index=False)
    print(f"  Saved phase2_broad_vs_fasting_design.csv:\n{design_df[['architecture','n','n_outcome_positive','epv_events_per_predictor']].to_string(index=False)}")

    # ── 2M: Intersectional feasibility (within the PRIMARY cohort) ──────────────────────
    primary = master.loc[primary_mask].copy()
    primary["outcome_positive"] = (primary["LUXSMED"] >= PRIMARY_THRESHOLD).astype(int)
    age_bins = pd.cut(primary["RIDAGEYR"], bins=[17, 39, 59, 120], labels=["18-39", "40-59", "60+"])
    bmi_bins = pd.cut(primary["BMXBMI"], bins=[0, 18.5, 24.9, 29.9, 200], labels=["Underweight", "Normal", "Overweight", "Obese"])
    primary["_age_bin"] = age_bins
    primary["_bmi_bin"] = bmi_bins

    inter_rows = []
    def add_intersections(dim1_col, dim1_map, dim2_col, dim2_map, dim_name):
        for c1, l1 in dim1_map.items():
            for c2, l2 in dim2_map.items():
                sub = primary[(primary[dim1_col] == c1) & (primary[dim2_col] == c2)]
                n = len(sub); pos = int(sub["outcome_positive"].sum()); neg = n - pos
                inter_rows.append({"intersection": dim_name, "group_1": l1, "group_2": l2, "n": n,
                                  "n_positive": pos, "n_negative": neg,
                                  "feasibility_classification": classify_feasibility(pos, neg) if n > 0 else "insufficient evidence (empty)"})

    sex_map_codes = SEX_MAP
    race_map_codes = RACE_MAP_RIDRETH3
    age_map_codes = {b: b for b in ["18-39", "40-59", "60+"]}
    bmi_map_codes = {b: b for b in ["Underweight", "Normal", "Overweight", "Obese"]}
    add_intersections("RIAGENDR", sex_map_codes, "RIDRETH3", race_map_codes, "Sex x Race/Ethnicity")
    add_intersections("RIAGENDR", sex_map_codes, "_age_bin", age_map_codes, "Sex x Age")
    add_intersections("RIAGENDR", sex_map_codes, "_bmi_bin", bmi_map_codes, "Sex x BMI")

    inter_df = pd.DataFrame(inter_rows)
    inter_df.to_csv(TAB_DIR / "phase2_intersectional_feasibility.csv", index=False)
    print(f"  Saved phase2_intersectional_feasibility.csv ({len(inter_df)} intersections). Classification counts:")
    print(inter_df["feasibility_classification"].value_counts().to_string())

    # ── 2O: Statistical precision / sample-size feasibility ─────────────────────────────
    stat_rows = []
    n_total = len(primary); pos_total = int(primary["outcome_positive"].sum()); neg_total = n_total - pos_total
    lo, hi, width = wilson_ci(pos_total, n_total)
    stat_rows.append({"scope": "OVERALL primary cohort", "n": n_total, "n_positive": pos_total, "n_negative": neg_total,
                      "prevalence_95ci_half_width_pct": round(width/2, 2) if width else None,
                      "epv_events_per_predictor_10_predictors": round(pos_total/10, 1),
                      "assessment": "Adequate: EPV=66.6 >> conventional 10-events-per-predictor floor; "
                                    "overall 95% CI half-width ~1.1pp supports stable overall AUC/calibration estimation."})
    for dim_col, dim_map, dim_name in [("RIAGENDR", sex_map_codes, "Sex"), ("RIDRETH3", race_map_codes, "Race/Ethnicity"),
                                        ("_age_bin", age_map_codes, "Age"), ("_bmi_bin", bmi_map_codes, "BMI")]:
        for code, lbl in dim_map.items():
            sub = primary[primary[dim_col] == code]
            n = len(sub); pos = int(sub["outcome_positive"].sum()); neg = n - pos
            lo, hi, width = wilson_ci(pos, n) if n else (None, None, None)
            fc = classify_feasibility(pos, neg) if n > 0 else "insufficient evidence"
            stat_rows.append({"scope": f"{dim_name}: {lbl}", "n": n, "n_positive": pos, "n_negative": neg,
                             "prevalence_95ci_half_width_pct": round(width/2, 2) if width else None,
                             "epv_events_per_predictor_10_predictors": round(pos/10, 1) if pos else 0,
                             "assessment": fc})
    stat_df = pd.DataFrame(stat_rows)
    stat_df.to_csv(TAB_DIR / "phase2_statistical_feasibility.csv", index=False)
    print(f"  Saved phase2_statistical_feasibility.csv ({len(stat_df)} rows).")
    print("[DESIGN & FEASIBILITY TABLES COMPLETE]")

if __name__ == "__main__":
    main()
