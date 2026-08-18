"""
phase2_02_outcome_predictors_leakage.py
Phase 2F/2G/2I - Outcome prevalence (primary cohort x primary threshold), final
predictor registry, and final leakage registry. Builds on the frozen Phase 1
leakage pre-screen (preliminary_leakage_audit.csv) -- finalizes rather than
re-derives it.

PRIMARY COHORT (frozen by documentation/phase2/primary_cohort_decision.md):
  CAND_1_QUALITYVALID_ADULT_BROAD = adult AND LUAXSTAT==1 AND broad labs complete
  AND BMI+sex non-missing. N=7,153 (see phase2_candidate_cohort_comparison.csv).
PRIMARY OUTCOME (frozen by documentation/phase2/primary_outcome_definition.md):
  LUXSMED >= 8.2 kPa (significant fibrosis, >=F2).

Produces:
  results/tables/phase2_outcome_prevalence.csv
  results/tables/phase2_predictor_registry.csv
  results/tables/phase2_final_leakage_registry.csv
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, TAB_DIR, VAR_METADATA, RACE_MAP_RIDRETH3, SEX_MAP, read_csv_safe
from _cohorts import compute_all

PRIMARY_THRESHOLD = 8.2

def wilson_ci(pos, n, z=1.96):
    if n == 0:
        return (None, None)
    p = pos / n
    denom = 1 + z**2/n
    center = (p + z*z/(2*n)) / denom
    half = (z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5)) / denom
    return (round(100*max(0, center-half), 2), round(100*min(1, center+half), 2))

def main():
    print("=== Phase 2F/2G/2I: Outcome Prevalence, Predictor Registry, Final Leakage Registry ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    c = compute_all(master)
    adult = master["RIDAGEYR"] >= 18
    broad_labs = ["LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
    broad_complete = master[broad_labs].notna().all(axis=1)
    bmi_demo_complete = master["BMXBMI"].notna() & master["RIAGENDR"].notna()
    primary_mask = c["COHORT_2_QUALITY_VALID"][0] & adult & broad_complete & bmi_demo_complete
    primary = master.loc[primary_mask].copy()
    primary["outcome_positive"] = (primary["LUXSMED"] >= PRIMARY_THRESHOLD).astype(int)
    n_total = len(primary)

    # ── 2F: Outcome prevalence, overall + by subgroup ───────────────────────────────────
    rows = []
    def add_row(category, label, sub):
        n = len(sub); pos = int(sub["outcome_positive"].sum()); neg = n - pos
        lo, hi = wilson_ci(pos, n)
        rows.append({"category": category, "group_label": label, "n": n, "n_positive": pos, "n_negative": neg,
                    "prevalence_pct": round(100*pos/n, 2) if n else None,
                    "prevalence_95ci_low_pct": lo, "prevalence_95ci_high_pct": hi})

    add_row("OVERALL", "Primary cohort (all)", primary)
    for code, lbl in SEX_MAP.items():
        add_row("Sex", lbl, primary[primary["RIAGENDR"] == code])
    for code, lbl in RACE_MAP_RIDRETH3.items():
        add_row("Race_Ethnicity_RIDRETH3", lbl, primary[primary["RIDRETH3"] == code])
    age_bins = pd.cut(primary["RIDAGEYR"], bins=[17, 39, 59, 120], labels=["18-39", "40-59", "60+"])
    for lbl in ["18-39", "40-59", "60+"]:
        add_row("Age_Group_Final", lbl, primary[age_bins == lbl])
    bmi_bins = pd.cut(primary["BMXBMI"], bins=[0, 18.5, 24.9, 29.9, 200], labels=["Underweight", "Normal", "Overweight", "Obese"])
    for lbl in ["Underweight", "Normal", "Overweight", "Obese"]:
        add_row("BMI_Group_Final", lbl, primary[bmi_bins == lbl])

    prev_df = pd.DataFrame(rows)
    prev_df.to_csv(TAB_DIR / "phase2_outcome_prevalence.csv", index=False)
    print(f"  Saved phase2_outcome_prevalence.csv ({len(prev_df)} rows). Overall prevalence: "
          f"{prev_df.iloc[0]['n_positive']}/{prev_df.iloc[0]['n']} = {prev_df.iloc[0]['prevalence_pct']}%")

    # ── 2G: Final predictor registry ────────────────────────────────────────────────────
    leakage = read_csv_safe(AUDIT_DIR / "preliminary_leakage_audit.csv")
    verif = read_csv_safe(AUDIT_DIR.parent / "data_dictionary" / "variable_source_verification.csv")

    def leak_class(var):
        row = leakage[leakage["variable"] == var]
        return row["classification"].iloc[0] if len(row) else "not_screened"

    def is_verified(var):
        row = verif[verif["variable"] == var]
        return bool(row["verified_against_official_documentation"].iloc[0]) if len(row) else False

    PRIMARY_PREDICTORS = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL",
                         "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
    SECONDARY_ONLY_PREDICTORS = ["LBXGLU", "LBXTR"]  # fasting-extended architecture only
    QUALITY_EXCLUSION_VARS = ["LUAXSTAT", "LUXSIQR", "LUXSIQRM", "LUXCPIQR", "BMDSTATS", "BMIWT", "BMIHT"]
    OUTCOME_VARS = ["LUXSMED", "LUXCAPM"]
    SENSITIVITY_DEMOGRAPHIC = ["RIDRETH1", "RIDRETH3"]

    reg_rows = []
    def reg(var, role, rationale):
        meta = VAR_METADATA.get(var, {})
        n_miss = int(master[var].isna().sum()) if var in master.columns else None
        reg_rows.append({
            "variable": var, "source_file": meta.get("src", "-"), "unit": meta.get("unit", "-"),
            "clinical_rationale": meta.get("desc", var), "missingness_pct_full_master": round(100*n_miss/len(master), 2) if n_miss is not None else None,
            "candidate_role": role, "leakage_assessment": leak_class(var),
            "verified_against_official_source": is_verified(var), "inclusion_decision": rationale.split("|")[0],
            "rationale": rationale.split("|")[1] if "|" in rationale else rationale
        })

    for v in PRIMARY_PREDICTORS:
        reg(v, "PRIMARY MODEL CANDIDATE", "INCLUDED (primary architecture)|Routinely available at clinical "
            "evaluation time, biologically plausible predictor of liver fibrosis, non-missing by cohort construction")
    for v in SECONDARY_ONLY_PREDICTORS:
        reg(v, "SECONDARY MODEL CANDIDATE", "INCLUDED (secondary/fasting-extended architecture only)|Fasting-"
            "subsample restricted; adds metabolic signal but reduces N materially (see broad_vs_fasting_design.csv)")
    for v in QUALITY_EXCLUSION_VARS:
        reg(v, "QUALITY/EXCLUSION VARIABLE", "EXCLUDED from predictor set|Used only for cohort eligibility "
            "(elastography quality-valid definition or BMX completeness), not appropriate as a prediction-time feature")
    for v in OUTCOME_VARS:
        reg(v, "OUTCOME-ONLY", "EXCLUDED from predictor set|Directly IS or duplicates the outcome measurement")
    for v in SENSITIVITY_DEMOGRAPHIC:
        reg(v, "SENSITIVITY-ONLY (fairness subgroup variable, not a model predictor)",
            "EXCLUDED from predictor set, RETAINED for subgroup/fairness analysis|Race/ethnicity is a fairness-"
            "analysis stratification variable, not included as a model input to avoid encoding demographic "
            "proxies directly into the risk score without explicit justification (deferred to Phase 2S)")

    # Remaining LBX/LBD auxiliary labs not in VAR_METADATA -> REQUIRES FURTHER VERIFICATION
    reviewed = set(PRIMARY_PREDICTORS + SECONDARY_ONLY_PREDICTORS + QUALITY_EXCLUSION_VARS + OUTCOME_VARS + SENSITIVITY_DEMOGRAPHIC + ["SEQN", "WTMECPRP", "WTINTPRP", "WTSAFPRP", "SDMVPSU", "SDMVSTRA"])
    aux = [c for c in master.columns if c not in reviewed and (c.startswith("LBX") or c.startswith("LBD"))]
    for v in aux:
        reg(v, "REQUIRES FURTHER VERIFICATION", "EXCLUDED (unverified)|Not individually verified against official "
            "NHANES documentation in Phase 1/2; protection rule (Issue 13) prohibits modeling use without verification")
    for v in ["SEQN", "WTMECPRP", "WTINTPRP", "WTSAFPRP", "SDMVPSU", "SDMVSTRA"]:
        reg(v, "QUALITY/EXCLUSION VARIABLE", "EXCLUDED from predictor set|Identifier or survey design/weight "
            "variable; not a clinical predictor (see survey_weight_protocol.md for weight usage)")

    pred_df = pd.DataFrame(reg_rows)
    pred_df.to_csv(TAB_DIR / "phase2_predictor_registry.csv", index=False)
    print(f"  Saved phase2_predictor_registry.csv ({len(pred_df)} variables classified).")
    print("  Role counts:\n" + pred_df["candidate_role"].value_counts().to_string())

    # ── 2I: Final leakage registry (finalizes the Phase 1 pre-screen into Phase 2 categories) ──
    final_map = {"outcome_only": "OUTCOME ONLY", "quality_only": "QUALITY/EXCLUSION ONLY",
                "likely_eligible": "ELIGIBLE PREDICTOR", "uncertain_phase2_decision": "UNCERTAIN/DEFERRED"}
    leak_final = leakage.copy()
    leak_final["phase2_final_category"] = leak_final["classification"].map(final_map).fillna("UNCERTAIN/DEFERRED")
    # Override: any variable Phase 2 explicitly excluded as sensitivity-only/unverified gets flagged distinctly
    override_excluded = set(SENSITIVITY_DEMOGRAPHIC) | set(aux)
    leak_final.loc[leak_final["variable"].isin(override_excluded), "phase2_final_category"] = "UNCERTAIN/DEFERRED"
    leak_final["phase2_disposition"] = leak_final["variable"].map(
        {v: "INCLUDED (primary)" for v in PRIMARY_PREDICTORS} |
        {v: "INCLUDED (secondary only)" for v in SECONDARY_ONLY_PREDICTORS} |
        {v: "EXCLUDED (quality/eligibility use only)" for v in QUALITY_EXCLUSION_VARS} |
        {v: "EXCLUDED (is the outcome)" for v in OUTCOME_VARS} |
        {v: "EXCLUDED from predictors (fairness variable)" for v in SENSITIVITY_DEMOGRAPHIC}
    ).fillna("EXCLUDED (not in finalized predictor set)")
    leak_final.to_csv(TAB_DIR / "phase2_final_leakage_registry.csv", index=False)
    print(f"  Saved phase2_final_leakage_registry.csv ({len(leak_final)} variables).")
    print("[OUTCOME/PREDICTOR/LEAKAGE FINALIZATION COMPLETE]")

if __name__ == "__main__":
    main()
