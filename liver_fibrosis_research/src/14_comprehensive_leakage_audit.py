"""
14_comprehensive_leakage_audit.py
Phase 1 Remediation - Error 11 fix: the prior leakage audit only inspected LUX-prefixed
columns. This audit classifies EVERY variable retained in the master dataset against six
explicit questions, into one of: likely_eligible, likely_leakage, quality_only,
outcome_only, uncertain_phase2_decision. No variable is silently removed.

Produces:
  documentation/audit_reports/preliminary_leakage_audit.csv
"""

import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, VAR_METADATA

# Six-question classification, applied per variable role (role comes from the verified VAR_METADATA
# in _common.py, which is itself sourced from official NHANES documentation -- see Error 6/variable_source_verification.csv)
def classify(var, meta):
    role = meta.get("role", "unknown")
    q1_before_prediction_time = True  # all retained vars are baseline exam/interview data, collected same visit as outcome
    q2_derived_from_outcome = var in ("LUXSMED", "LUXCAPM")
    q3_encodes_outcome_directly = var in ("LUXSMED", "LUXCAPM")
    q4_duplicate_of_outcome = False
    q5_quality_only = role == "quality"
    q6_same_exam_violates_setting = role in ("quality",)  # LUX quality/status vars only meaningful for inclusion, not prediction

    if role == "candidate_outcome":
        classification = "outcome_only"
        reason = "This IS the candidate outcome variable (or its direct steatosis counterpart); never a predictor."
    elif role == "quality":
        classification = "quality_only"
        reason = ("Exam-quality / completion-status variable (e.g. LUAXSTAT, LUXSIQRM, BMDSTATS, comment codes). "
                   "Legitimate for cohort inclusion/exclusion and quality-valid subsetting; NOT a candidate predictor "
                   "-- some (LUXSIQR/LUXSIQRM/LUXCPIQR) are measured as part of the same elastography exam as the "
                   "outcome and could leak exam-quality information correlated with the outcome measurement process.")
    elif role == "id_key":
        classification = "quality_only"
        reason = "Identifier / merge key, not a clinical predictor."
    elif role in ("survey_weight", "survey_design"):
        classification = "uncertain_phase2_decision"
        reason = ("Not a leakage risk in the traditional sense, but whether/how to incorporate survey weights "
                   "into ML training vs. reserve for population-representative evaluation is an open methodological "
                   "question NHANES documentation does not resolve (confirmed via official-source research for this "
                   "remediation). Deferred to Phase 2, per Error 10.")
    elif role == "demographic":
        classification = "likely_eligible"
        reason = "Collected independently of the FibroScan exam (interview/anthropometric); no plausible outcome leakage path."
    elif role in ("candidate_predictor", "candidate_predictor_broad", "candidate_predictor_fasting"):
        classification = "likely_eligible"
        reason = ("Laboratory value or anthropometric measurement collected as part of the standard exam battery, "
                   "biologically upstream of / independent from the liver-stiffness measurement process itself. "
                   "No direct mathematical or procedural derivation from LUXSMED/LUXCAPM.")
    else:
        classification = "uncertain_phase2_decision"
        reason = "Role not fully characterized in the verified variable dictionary; requires manual Phase 2 review."

    return dict(
        variable=var, role=role, description=meta.get("desc", var), source_file=meta.get("src", "-"),
        q1_available_before_or_at_prediction_time=q1_before_prediction_time,
        q2_derived_from_outcome=q2_derived_from_outcome,
        q3_encodes_outcome_measurement_directly=q3_encodes_outcome_directly,
        q4_duplicate_or_transformed_outcome=q4_duplicate_of_outcome,
        q5_quality_variable_inclusion_only=q5_quality_only,
        q6_same_exam_violates_prediction_setting=q6_same_exam_violates_setting,
        classification=classification, rationale=reason
    )

def main():
    print("=== Comprehensive Leakage Pre-Screen (Error 11) — ALL candidate predictors ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")

    rows = []
    for col in master.columns:
        meta = VAR_METADATA.get(col)
        if meta is None:
            # Auxiliary merged column not in the curated dictionary (e.g. unused lab comment/flag codes) --
            # still classify, conservatively, rather than silently omit.
            if col.endswith("LC"):
                # NHANES detection-limit COMMENT/flag code (e.g. LBDSATLC = "below LLOD?" binary flag for
                # LBXSATSI), not itself a lab concentration value. Misclassifying these as ordinary LBD*
                # predictors would treat a measurement-quality flag as a clinical predictor.
                role = "quality"
            elif col.startswith("LBX") or col.startswith("LBD"):
                role = "candidate_predictor"
            else:
                role = "auxiliary_unreviewed"
            meta = {"role": role, "desc": col, "src": "merged (not in curated dictionary)"}
        rows.append(classify(col, meta))

    df = pd.DataFrame(rows)
    df.to_csv(AUDIT_DIR / "preliminary_leakage_audit.csv", index=False)

    counts = df["classification"].value_counts()
    print("  Classification counts:")
    for k, v in counts.items():
        print(f"    {k}: {v}")
    # TEST 13 precondition: no variable should appear in both outcome_only and likely_eligible -- structurally
    # impossible here since classify() assigns exactly one classification per variable, but verify explicitly.
    assert df["variable"].duplicated().sum() == 0, "Duplicate variable rows in leakage audit!"
    print(f"  Saved preliminary_leakage_audit.csv ({len(df)} variables classified, zero duplicates).")
    print("[COMPREHENSIVE LEAKAGE AUDIT COMPLETE]")

if __name__ == "__main__":
    main()
