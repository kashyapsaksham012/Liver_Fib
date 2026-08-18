"""
21_phase2_open_decisions.py
Phase 1 Closure - Issue 15: formal Phase 2 open-decisions document. Each item has a
question, the evidence Phase 1 gathered, what Phase 1 established, and what Phase 2
must still decide. These decisions are deliberately NOT made here (Non-negotiable
rule 15: do not make a downstream methodological decision just to force Phase 1 closed).

Produces:
  documentation/audit_reports/phase2_open_decisions.md
"""

import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, NOW
from _cohorts import compute_all

DECISIONS = [
    dict(question="What is the final significant-fibrosis outcome threshold (LUXSMED cutpoint)?",
         evidence="9 candidate cutpoints (7.0-13.6 kPa) counted against BOTH the non-missing and "
                  "quality-valid denominators; external literature cites 8.2/9.7/13.6 kPa (meta-analytic "
                  "Youden-optimal) and notes 6.8-13.6 kPa variability across studies (see phase1_references.md).",
         established="Descriptive counts at every candidate cutpoint, cited literature range, provisional "
                     "labeling maintained throughout.",
         must_decide="Pre-specify ONE threshold (or a small ordinal set) BEFORE seeing any model performance."),

    dict(question="Should the analytical cohort require LUAXSTAT==1 (quality-valid) or accept any non-missing LUXSMED?",
         evidence="Non-missing LUXSMED N=9,700 vs quality-valid N=9,023 (677-participant gap, all from "
                  "Partial (LUAXSTAT=2) exams). Both counted through the full cohort-flow and threshold tables.",
         established="Both populations fully characterized and kept distinct at every step; neither is used "
                     "as the master dataset's implicit filter.",
         must_decide="Choose the inclusion rule for the primary analysis (a sensitivity analysis using the "
                     "other population is a reasonable complement, not a requirement)."),

    dict(question="Should the adult-only (18+) restriction be applied?",
         evidence="Adults among non-missing LUXSMED = 8,318; among quality-valid = 7,768. Under-18 counts "
                  "reported both ways.",
         established="Both age-restricted and unrestricted counts available for either denominator.",
         must_decide="Confirm adult-only restriction (P_LUX's own target population is 12-150, i.e. includes "
                     "adolescents by design) and document the clinical/statistical rationale."),

    dict(question="Which predictor set: Cohort A (broad labs, N=8,880) or Cohort B (fasting-extended, N=4,336)?",
         evidence="Full demographic/quality-valid composition comparison in broad_vs_fasting_cohort.csv/.md; "
                  "Cohort B is a strict subset of Cohort A (asserted programmatically).",
         established="Both cohorts fully characterized descriptively; no performance comparison run (by design).",
         must_decide="Choose predictor set on scientific/study-design grounds -- e.g. whether fasting "
                     "glucose/triglycerides' added metabolic signal justifies the ~2,300-participant reduction "
                     "vs. losing that signal but keeping a larger, more representative sample."),

    dict(question="What is the final missing-data strategy for retained predictors?",
         evidence="Full missingness table (missingness_overall.csv, missingness_by_group.csv) and the "
                  "laboratory_plausibility_audit.csv flag inventory.",
         established="Missingness fully characterized overall and by demographic group; no imputation performed.",
         must_decide="Lock imputation method (e.g. median vs. multiple imputation) and pre-register it before modeling."),

    dict(question="RIDRETH1 (5-category) or RIDRETH3 (6-category, incl. Non-Hispanic Asian)?",
         evidence="race_ethnicity_verification.md: RIDRETH3 preserves Non-Hispanic Asian (N=1,061 in-cohort) "
                  "as distinct; RIDRETH1 folds it into 'Other'. Both retained unmodified in the master dataset.",
         established="Evidence-based recommendation (RIDRETH3) documented, not silently applied.",
         must_decide="Confirm RIDRETH3 as primary fairness-analysis variable (or justify otherwise) in the Phase 2 protocol."),

    dict(question="What are the final age and BMI subgroup bins?",
         evidence="Provisional bins used throughout (Under18/18-39/40-59/60+; Underweight/Normal/Overweight/Obese) "
                  "with outcome-positive/negative counts per bin in subgroup_outcome_feasibility.csv.",
         established="Provisional bins clearly labeled as such everywhere; counts available to inform final choice.",
         must_decide="Pre-specify final bins (may differ from the provisional ones, e.g. finer age strata) before analysis."),

    dict(question="What survey-weight strategy applies to ML training and evaluation?",
         evidence="Official NHANES weighting-tutorial rule verified and quoted (survey_design_notes.md): use "
                  "the weight of the smallest subpopulation included (WTSAFPRP if fasting labs are used). "
                  "NHANES documentation is explicitly SILENT on whether/how to use weights inside ML training.",
         established="Weight variables preserved unmodified; the population-representative-estimation rule is "
                     "documented and cited; the ML-training question is explicitly flagged as unresolved by "
                     "NHANES itself, not answered by this project.",
         must_decide="Decide (from general survey-statistics/ML literature, not NHANES guidance) whether/how "
                     "to incorporate weights into model training vs. reserve them for variance/CI estimation."),

    dict(question="What are the final fairness metrics and subgroup comparison groups?",
         evidence="subgroup_outcome_feasibility.csv provides total/outcome-positive/outcome-negative N for "
                  "sex, RIDRETH3, provisional age bins, and provisional BMI bins, with an explicit feasibility "
                  "classification per group (see Section O / Issue 12).",
         established="Descriptive feasibility fully characterized; small groups (e.g. Non-Hispanic Asian "
                     "outcome-positive N=62, Underweight BMI outcome-positive N=13) explicitly flagged as "
                     "lower-precision, NOT dropped or pooled.",
         must_decide="Select final fairness metrics (AUC, sensitivity, FNR, calibration slope/intercept, etc.) "
                     "and decide whether/how to handle low-precision subgroups (report wide CIs vs. pool vs. exclude)."),

    dict(question="What uncertainty-quantification method will be used?",
         evidence="None generated in Phase 1 by design (out of scope).",
         established="N/A -- explicitly deferred.",
         must_decide="Select and pre-register the uncertainty method (e.g. conformal prediction) per the "
                     "original research plan (info.md Phase 12)."),

    dict(question="What is the final train/validation/test split strategy?",
         evidence="None generated in Phase 1 by design (out of scope); cohort sizes for candidate populations "
                  "are available to plan split sizes.",
         established="Candidate population sizes documented for split-size planning.",
         must_decide="Lock the split strategy (e.g. 70/30 stratified, or cycle-based) before any model training."),
]

def main():
    print("=== Phase 2 Open Decisions Document (Issue 15) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    with open(AUDIT_DIR / "phase2_open_decisions.md", "w") as f:
        f.write(f"# Phase 2 Open Decisions\n\n**Generated:** {NOW}\n\n")
        f.write("These decisions are deliberately NOT made in Phase 1. Making any of them now merely to "
                "declare Phase 1 'finished' would violate the non-negotiable rule against forcing closure "
                "through premature methodological decisions. Phase 1's job was to gather the evidence needed "
                "to make each decision well -- that evidence is linked below.\n\n")
        for i, d in enumerate(DECISIONS, 1):
            f.write(f"## {i}. {d['question']}\n\n")
            f.write(f"**Evidence gathered in Phase 1:** {d['evidence']}\n\n")
            f.write(f"**What Phase 1 established:** {d['established']}\n\n")
            f.write(f"**What Phase 2 must decide:** {d['must_decide']}\n\n")
    print(f"  Saved phase2_open_decisions.md ({len(DECISIONS)} decisions documented).")
    print("[PHASE 2 OPEN DECISIONS COMPLETE]")

if __name__ == "__main__":
    main()
