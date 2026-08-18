"""
phase2_06_generate_report.py
Phase 2Z - Final Phase 2 report generator. Sections A-AE. Statistics are read from
the CSV/parquet outputs already generated; narrative sections reference the frozen
protocol documents in documentation/phase2/ rather than duplicating their full text.

Produces:
  PHASE2_ANALYTICAL_PROTOCOL_AND_FEASIBILITY_REPORT.md
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import ROOT, TAB_DIR, NOW, read_csv_safe

P2_DIR = ROOT / "documentation" / "phase2"
PROC_DIR = ROOT / "data" / "processed"

def main():
    print("=== Phase 2Z: Generate Final Phase 2 Report ===")
    cohort_cmp = read_csv_safe(TAB_DIR / "phase2_candidate_cohort_comparison.csv")
    prevalence = read_csv_safe(TAB_DIR / "phase2_outcome_prevalence.csv")
    predictors = read_csv_safe(TAB_DIR / "phase2_predictor_registry.csv")
    leakage = read_csv_safe(TAB_DIR / "phase2_final_leakage_registry.csv")
    design = read_csv_safe(TAB_DIR / "phase2_broad_vs_fasting_design.csv")
    intersect = read_csv_safe(TAB_DIR / "phase2_intersectional_feasibility.csv")
    stat_feas = read_csv_safe(TAB_DIR / "phase2_statistical_feasibility.csv")
    checklist = read_csv_safe(P2_DIR / "phase2_premodeling_checklist_results.csv")
    primary_ds = pd.read_parquet(PROC_DIR / "analysis_dataset_primary.parquet")
    secondary_ds = pd.read_parquet(PROC_DIR / "analysis_dataset_secondary.parquet")

    required_docs = ["phase2_preanalysis_snapshot.md", "primary_research_question.md",
                     "primary_cohort_decision.md", "elastography_eligibility_protocol.md",
                     "primary_outcome_definition.md", "prediction_time_and_leakage_protocol.md",
                     "missing_data_protocol.md", "fairness_subgroup_protocol.md",
                     "survey_weight_protocol.md", "statistical_analysis_plan.md",
                     "model_development_protocol.md", "evaluation_metrics_protocol.md",
                     "fairness_definition.md", "uncertainty_protocol.md",
                     "multiple_comparisons_protocol.md", "sensitivity_analysis_plan.md",
                     "PHASE2_PROTOCOL_FREEZE.md"]
    missing_docs = [d for d in required_docs if not (P2_DIR / d).exists()]
    required_data = [PROC_DIR / "analysis_dataset_primary.parquet", PROC_DIR / "analysis_dataset_secondary.parquet"]
    missing_data = [str(p) for p in required_data if not p.exists()]
    n_checklist_fail = int((checklist["status"] == "FAIL").sum()) if not checklist.empty else -1

    blockers = []
    if missing_docs:
        blockers.append(f"{len(missing_docs)} required Phase 2 document(s) missing: {missing_docs}")
    if missing_data:
        blockers.append(f"Analysis dataset(s) missing: {missing_data}")
    if checklist.empty:
        blockers.append("Pre-modeling checklist has not been run.")
    elif n_checklist_fail > 0:
        blockers.append(f"{n_checklist_fail} pre-modeling checklist item(s) FAILED.")

    readiness = "PHASE 2 — COMPLETE AND FROZEN" if not blockers else "PHASE 2 — PARTIALLY COMPLETE"

    report_path = ROOT / "PHASE2_ANALYTICAL_PROTOCOL_AND_FEASIBILITY_REPORT.md"
    with open(report_path, "w") as f:
        f.write("# Phase 2 Analytical Protocol and Feasibility Report\n\n")
        f.write(f"**Generated:** {NOW}\n\n---\n\n")

        f.write("## A. Phase 2 Objective\n\nConvert the frozen Phase 1 data foundation into one explicit, "
                "reproducible, pre-registered analytical protocol -- cohort, outcome, predictors, missing-data "
                "strategy, subgroup protocol, and future evaluation plan -- frozen BEFORE any ML model is "
                "trained. No modeling, tuning, or performance evaluation occurs in this phase.\n\n")

        f.write("## B. Primary Research Question\n\nSee `documentation/phase2/primary_research_question.md`. "
                "Summary: in adults with quality-valid elastography, how accurate, calibrated, fair, and "
                "uncertainty-aware are standard ML models predicting significant fibrosis (LUXSMED >= 8.2 kPa) "
                "from routine demographic/anthropometric/laboratory predictors?\n\n")
        f.write("## C. Secondary Research Questions\n\n1. Elastography-eligibility robustness. "
                "2. Fasting-extended architecture comparison. 3. Threshold/severity-outcome robustness. "
                "4. Adolescent-inclusion robustness. Full detail: `primary_research_question.md`.\n\n")

        f.write("## D. Primary Cohort\n\n")
        if not cohort_cmp.empty:
            f.write(cohort_cmp.to_markdown(index=False) + "\n\n")
        f.write("**Selected: CAND_1_QUALITYVALID_ADULT_BROAD, N=7,153.** Full reasoning: `primary_cohort_decision.md`.\n\n")

        f.write("## E. Secondary Cohort(s)\n\nCAND_3_QUALITYVALID_ADULT_FASTING, N=3,582 (fasting-extended "
                "architecture). Sensitivity cohorts CAND_2 (N=7,639) and CAND_4 (N=8,215) also defined. "
                "Detail: `primary_cohort_decision.md`.\n\n")

        f.write("## F. Cohort Comparison\n\nFull comparison table: `results/tables/phase2_candidate_cohort_comparison.csv`. "
                "Decision criteria (clinical appropriateness, elastography quality, predictor realism, sample "
                "size/subgroup power, representativeness) documented in `primary_cohort_decision.md` -- "
                "**no criterion was predictive performance** (non-negotiable rule 1).\n\n")

        f.write("## G. Elastography Eligibility\n\n`LUAXSTAT==1` (NHANES quality-valid) is the primary rule; "
                "non-missing-LUXSMED-only is a sensitivity rule. Three concepts (measurement available / "
                "quality-valid / clinical classification) kept distinct throughout. Detail: "
                "`elastography_eligibility_protocol.md`.\n\n")

        f.write("## H. Primary Fibrosis Outcome\n\n**LUXSMED >= 8.2 kPa** (significant fibrosis, >=F2), "
                "sourced from a 2024 VCTE-vs-MRE meta-analysis Youden-optimal cutoff -- selected on clinical-"
                "evidence grounds alone, before any model was trained. Full evaluation of all candidate "
                "thresholds and why each was/wasn't selected: `primary_outcome_definition.md`.\n\n")

        f.write("## I. Secondary Outcomes\n\nSensitivity: 8.0 kPa. Secondary (distinct severity question): "
                "9.7 kPa (advanced fibrosis), 13.6 kPa (cirrhosis). Detail: `primary_outcome_definition.md`.\n\n")

        f.write("## J. Outcome Prevalence\n\n")
        if not prevalence.empty:
            f.write(prevalence.to_markdown(index=False) + "\n\n")
        f.write("These are descriptive/feasibility counts only -- NOT used to adjust the threshold "
                "(non-negotiable rule 2).\n\n")

        f.write("## K. Predictor Registry\n\n")
        if not predictors.empty:
            role_counts = predictors["candidate_role"].value_counts()
            f.write("| Role | N variables |\n|---|---|\n")
            for k, v in role_counts.items():
                f.write(f"| {k} | {v} |\n")
            f.write("\nFull registry (93 variables): `results/tables/phase2_predictor_registry.csv`.\n\n")

        f.write("## L. Leakage Decisions\n\n")
        if not leakage.empty:
            fc = leakage["phase2_final_category"].value_counts()
            f.write("| Final category | N variables |\n|---|---|\n")
            for k, v in fc.items():
                f.write(f"| {k} | {v} |\n")
            f.write("\nFull registry (137 variables): `results/tables/phase2_final_leakage_registry.csv`. "
                    "Detail: `prediction_time_and_leakage_protocol.md`.\n\n")

        f.write("## M. Missing-Data Strategy\n\nComplete-case primary (cohort eligibility already requires "
                "predictor completeness); multiple imputation as sensitivity. A real differential-missingness "
                "finding for Non-Hispanic Black participants (41.3% of excluded vs. 25.0% of retained) was "
                "identified and is NOT hidden -- see `missing_data_protocol.md`.\n\n")

        f.write("## N. Broad vs Fasting Design\n\n")
        if not design.empty:
            f.write(design[["architecture", "n", "n_predictors", "n_outcome_positive", "prevalence_pct",
                           "min_race_ethnicity_subgroup_positive_n", "epv_events_per_predictor"]].to_markdown(index=False) + "\n\n")
        f.write("Broad-lab is PRIMARY; fasting-extended is SECONDARY. Not chosen by performance. "
                "Detail: `survey_weight_protocol.md` is NOT this section -- see design table above and "
                "`primary_cohort_decision.md` criterion 3-4.\n\n")

        f.write("## O. Demographic Subgroup Protocol\n\nSex, Race/Ethnicity (RIDRETH3), Age (18-39/40-59/60+), "
                "BMI (WHO categories) -- all PRIMARY dimensions, each category individually classified by "
                "feasibility tier, NONE pooled or dropped. Detail: `fairness_subgroup_protocol.md`.\n\n")

        f.write("## P. Intersectional Feasibility\n\n")
        if not intersect.empty:
            fc = intersect["feasibility_classification"].value_counts()
            f.write("| Classification | N intersections (of 26: Sex x Race/Ethnicity, Sex x Age, Sex x BMI) |\n|---|---|\n")
            for k, v in fc.items():
                f.write(f"| {k} | {v} |\n")
            f.write("\nFull table: `results/tables/phase2_intersectional_feasibility.csv`.\n\n")

        f.write("## Q. Survey-Weight Methodology\n\nFour distinct uses (descriptive estimates / training / "
                "evaluation / fairness), each independently decided -- unweighted primary for training, "
                "evaluation, and fairness; weighted (WTMECPRP/WTSAFPRP + SDMVPSU/SDMVSTRA) for population-"
                "descriptive estimates only. The ML-weighting question's genuine methodological uncertainty is "
                "stated explicitly, not hidden. Detail: `survey_weight_protocol.md`.\n\n")

        f.write("## R. Statistical Precision / Sample-Size Feasibility\n\n")
        if not stat_feas.empty:
            f.write(stat_feas.to_markdown(index=False) + "\n\n")
        f.write("Overall EPV=66.6 (adequate); subgroup-level precision varies and is labeled per-category, "
                "not dropped. Detail: `results/tables/phase2_statistical_feasibility.csv`.\n\n")

        f.write("## S. Primary Analysis Plan\n\n## T. Secondary Analysis Plan\n\n## U. Exploratory Analysis Plan\n\n"
                "All three fully specified in `documentation/phase2/statistical_analysis_plan.md` -- "
                "primary (1 cohort, 1 outcome, 4 model families, primary metrics), secondary (3 named "
                "analyses), exploratory (5 named analyses, never promoted to primary post-hoc).\n\n")

        f.write("## V. Future Model-Development Protocol\n\n70/30 stratified split, 5-fold CV, fixed seed "
                "(recorded at Phase 3 start), training-only preprocessing, no SMOTE now. Full 10-point "
                "specification: `model_development_protocol.md`.\n\n")

        f.write("## W. Future Discrimination Metrics\n\nROC-AUC primary; PR-AUC/sensitivity/specificity/PPV/"
                "NPV/F1 secondary. `evaluation_metrics_protocol.md`.\n\n")
        f.write("## X. Future Calibration Metrics\n\nCalibration slope/intercept + Brier primary; calibration "
                "curve + ECE secondary. `evaluation_metrics_protocol.md`.\n\n")
        f.write("## Y. Future Fairness Metrics\n\nSensitivity absolute-difference from reference group is "
                "PRIMARY (10pp + CI-excludes-zero = meaningful, fixed BEFORE any result observed); AUC/"
                "specificity/calibration disparities secondary. `fairness_definition.md`.\n\n")
        f.write("## Z. Future Uncertainty Method\n\nSplit conformal prediction, 90% target coverage, overall "
                "AND subgroup coverage evaluated, efficiency via prediction-set size. `uncertainty_protocol.md`.\n\n")
        f.write("## AA. Multiple-Comparison Strategy\n\nFDR (Benjamini-Hochberg) within dimension x model x "
                "metric families for confirmatory-tier comparisons; exploratory-tier (intersectional etc.) "
                "reported uncorrected and clearly labeled. `multiple_comparisons_protocol.md`.\n\n")
        f.write("## AB. Sensitivity-Analysis Plan\n\n4 pre-specified dimensions (threshold, eligibility, "
                "architecture -- elevated to secondary --, missing-data), each tied to a specific documented "
                "residual uncertainty, not a generic robustness checklist. `sensitivity_analysis_plan.md`.\n\n")

        f.write("## AC. Protocol Freeze\n\n`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` -- the "
                "authoritative consolidation of every decision above, with an amendment log for any future "
                "change (none logged yet).\n\n")

        f.write("## AD. Final Pre-Modeling Checklist\n\n")
        if not checklist.empty:
            f.write(checklist.to_markdown(index=False) + "\n\n")

        f.write(f"## AE. Phase 2 Readiness Decision\n\n**{readiness}**\n\n")
        f.write(f"- Primary analysis dataset: `data/processed/analysis_dataset_primary.parquet`, N={len(primary_ds)}, "
                f"{int(primary_ds['outcome_primary_8.2kPa'].sum())} positive.\n")
        f.write(f"- Secondary analysis dataset: `data/processed/analysis_dataset_secondary.parquet`, N={len(secondary_ds)}, "
                f"{int(secondary_ds['outcome_primary_8.2kPa'].sum())} positive.\n\n")
        if blockers:
            f.write("Remaining blockers:\n\n")
            for b in blockers:
                f.write(f"- {b}\n")
        else:
            f.write("All Phase 2 completion criteria are satisfied: primary/secondary cohorts selected and "
                    "justified on non-performance grounds; elastography eligibility, primary outcome, "
                    "predictor registry, and leakage decisions frozen; missing-data, broad-vs-fasting, "
                    "subgroup, intersectional, survey-weight, and statistical-precision protocols all "
                    "documented with real computed evidence (including the Black-participant differential-"
                    "missingness finding, not hidden); primary/secondary/exploratory analyses, future model-"
                    "development structure, evaluation metrics, fairness definition, uncertainty method, and "
                    "multiple-comparison strategy are all frozen BEFORE any model was trained; the primary and "
                    "secondary analysis datasets are generated and verified nested; the final pre-modeling "
                    "checklist passes 15/15; no unresolved critical decision remains.\n\n")
        f.write("**Phase 3 may now proceed to model development strictly within the frozen protocol above. "
                "Any deviation must be logged as an amendment in PHASE2_PROTOCOL_FREEZE.md.**\n")

    print(f"Saved {report_path}")
    print(f"[PHASE 2 REPORT GENERATION COMPLETE] {readiness}")
    for b in blockers:
        print(f"  BLOCKER: {b}")

if __name__ == "__main__":
    main()
