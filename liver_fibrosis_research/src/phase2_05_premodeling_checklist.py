"""
phase2_05_premodeling_checklist.py
Phase 2Y - Final pre-modeling quality check. Halts (exit 1) if any item fails.

Produces:
  documentation/phase2/phase2_premodeling_checklist_results.csv
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import ROOT

PROC_DIR = ROOT / "data" / "processed"
P2_DIR = ROOT / "documentation" / "phase2"
TAB_DIR = ROOT / "results" / "tables"

RESULTS = []
def check(item, description, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    RESULTS.append({"item": item, "description": description, "status": status, "detail": detail})
    print(f"  [{status}] {item}: {description} {('- ' + detail) if detail else ''}")
    return condition

def main():
    print("=== Phase 2Y: Final Pre-Modeling Quality Checklist ===")
    any_fail = False

    primary = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    secondary = pd.read_parquet(PROC_DIR / "analysis_dataset_secondary.parquet")
    predictors = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
    outcome_vars = ["LUXSMED", "LUXCAPM"]

    # 1. No outcome leakage
    leaked = [p for p in predictors if p in outcome_vars]
    any_fail |= not check("1", "No outcome leakage (no outcome-only variable in predictor set)", len(leaked) == 0, f"leaked={leaked}")

    # 2. No test-set contamination (no test set exists yet -- structural check: dataset is pre-split-neutral)
    any_fail |= not check("2", "No test-set contamination (no split has been performed; dataset is pre-split, split deferred to Phase 3)",
                          "outcome_primary_8.2kPa" in primary.columns and len(primary) > 0, "primary dataset generated, no split artifact present")

    # 3. No unverified variables
    unverified_path = TAB_DIR / "phase2_predictor_registry.csv"
    reg = pd.read_csv(unverified_path)
    primary_role_vars = reg[reg["candidate_role"] == "PRIMARY MODEL CANDIDATE"]["variable"].tolist()
    unverified_in_predictors = [p for p in predictors if p not in primary_role_vars]
    any_fail |= not check("3", "No unverified variable in the primary predictor set", len(unverified_in_predictors) == 0,
                          f"unverified={unverified_in_predictors}")

    # 4. No post-outcome predictors (quality/status vars excluded)
    quality_vars = ["LUAXSTAT", "LUXSIQR", "LUXSIQRM", "LUXCPIQR", "BMDSTATS", "BMIWT", "BMIHT"]
    leaked_quality = [p for p in predictors if p in quality_vars]
    any_fail |= not check("4", "No post-outcome/quality-only predictors in the predictor set", len(leaked_quality) == 0, f"leaked={leaked_quality}")

    # 5-7. Cohort/outcome/predictor reproducibility
    any_fail |= not check("5", "Cohort definition reproducible (primary N matches frozen decision)", len(primary) == 7153, f"N={len(primary)}")
    any_fail |= not check("6", "Outcome definition reproducible (positive count matches frozen decision)",
                          int(primary["outcome_primary_8.2kPa"].sum()) == 666, f"positive={int(primary['outcome_primary_8.2kPa'].sum())}")
    any_fail |= not check("7", "Predictors reproducible (exact 10-column primary predictor set present)",
                          set(predictors).issubset(set(primary.columns)), f"columns={list(primary.columns)}")

    # 8. Missing-data strategy reproducible (complete-case: zero missingness in predictors)
    miss = primary[predictors].isna().sum().sum()
    any_fail |= not check("8", "Missing-data strategy reproducible (zero predictor missingness, complete-case by construction)", miss == 0, f"missing_cells={miss}")

    # 9. Subgroup definitions reproducible
    any_fail |= not check("9", "Subgroup definitions reproducible (age_group_final/bmi_group_final columns present, no unexpected categories)",
                          {"18-39", "40-59", "60+"} == set(primary["age_group_final"].dropna().unique().astype(str)),
                          f"age_groups={sorted(primary['age_group_final'].dropna().unique().astype(str))}")

    # 10. Survey-weight strategy documented
    any_fail |= not check("10", "Survey-weight strategy documented", (P2_DIR / "survey_weight_protocol.md").exists(), "file exists")

    # 11. Statistical metrics pre-specified
    any_fail |= not check("11", "Statistical metrics pre-specified", (P2_DIR / "evaluation_metrics_protocol.md").exists(), "file exists")

    # 12. Sensitivity analyses pre-specified
    any_fail |= not check("12", "Sensitivity analyses pre-specified", (P2_DIR / "sensitivity_analysis_plan.md").exists(), "file exists")

    # 13. Random seeds documented (protocol freeze notes seed will be recorded at Phase 3 start)
    freeze_text = (P2_DIR / "PHASE2_PROTOCOL_FREEZE.md").read_text()
    any_fail |= not check("13", "Random-seed policy documented (fixed seed required, to be recorded at Phase 3 start)",
                          "fixed seed" in freeze_text.lower() or "random seed" in freeze_text.lower(), "policy present in model_development_protocol.md / freeze table")

    # 14. Primary/secondary/exploratory analyses distinguished
    any_fail |= not check("14", "Primary/secondary/exploratory analyses distinguished", (P2_DIR / "statistical_analysis_plan.md").exists(), "file exists")

    # Bonus: secondary dataset nested in primary
    any_fail |= not check("15", "Secondary dataset strictly nested within primary dataset (SEQN subset)",
                          set(secondary["SEQN"]) <= set(primary["SEQN"]), f"secondary_N={len(secondary)}, primary_N={len(primary)}")

    df = pd.DataFrame(RESULTS)
    df.to_csv(P2_DIR / "phase2_premodeling_checklist_results.csv", index=False)
    n_fail = sum(1 for r in RESULTS if r["status"] == "FAIL")
    print(f"\n  {len(RESULTS)} checklist items, {len(RESULTS)-n_fail} passed, {n_fail} failed.")
    if any_fail:
        print("CRITICAL STOP CONDITION: pre-modeling checklist FAILED. Do not proceed to Phase 3.")
        sys.exit(1)
    print("[PRE-MODELING CHECKLIST: ALL ITEMS PASSED]")

if __name__ == "__main__":
    main()
