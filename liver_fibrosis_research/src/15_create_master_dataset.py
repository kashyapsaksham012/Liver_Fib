"""
15_create_master_dataset.py
Phase 1 Remediation - Error 6 & 10 fixes:
  - Master data dictionary now sourced entirely from the verified VAR_METADATA in
    _common.py (official NHANES codebook descriptions, units, source files, doc URLs).
  - NEW: variable_source_verification.csv -- one row per retained variable with its
    exact official meaning, verification status, and source URL.
  - survey_design_notes.md rewritten with the OFFICIAL NHANES weighting-tutorial quote
    (verified, not inferred): "you must use the weight of the smallest subpopulation
    that includes all the variables you want to include in your analysis," with
    NHANES's own worked fasting-weight example cited directly.

Produces:
  documentation/data_dictionary/phase1_master_data_dictionary.csv
  documentation/data_dictionary/variable_source_verification.csv
  documentation/source_metadata/survey_design_notes.md
"""

import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, DICT_DIR, META_DIR, NOW, VAR_METADATA

def main():
    print("=== Step 19, 22 & 23: Master Data Dictionary & Survey Notes (Remediated) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    n_total = len(master)

    dd_rows, verif_rows = [], []
    for col in master.columns:
        nm = int(master[col].isna().sum())
        pct = round(100 * nm / n_total, 2)
        dtype = str(master[col].dtype)
        r_str = "-"
        if pd.api.types.is_numeric_dtype(master[col]):
            c_min, c_max = master[col].min(), master[col].max()
            if pd.notna(c_min):
                r_str = f"{c_min:.2f} - {c_max:.2f}"

        meta = VAR_METADATA.get(col)
        if meta:
            desc, src, unit, role, notes = meta["desc"], meta["src"], meta["unit"], meta["role"], meta["notes"]
            doc_url = meta.get("doc_url", "-")
            official = meta.get("official", False)
            qual_restr = meta.get("quality_restriction") or "-"
            phase2_use = "Retain"
        else:
            desc, src, unit, notes, doc_url, official, qual_restr = col, "merged (not in curated dictionary)", "-", "", "-", False, "-"
            if col.endswith("LC"):
                role = "quality"  # NHANES detection-limit comment/flag code, not a lab concentration value
            elif col.startswith("LBX") or col.startswith("LBD"):
                role = "candidate_predictor"
            else:
                role = "auxiliary_unreviewed"
            phase2_use = "Evaluate"

        dd_rows.append({
            "original_variable_name": col, "readable_description": desc, "source_file": src, "unit": unit,
            "type": dtype, "role": role, "n_obs": n_total - nm, "n_missing": nm, "missing_pct": pct,
            "observed_range": r_str, "candidate_phase2_use": phase2_use, "notes": notes,
            "quality_restriction": qual_restr, "official_source_url": doc_url,
            "unresolved_questions": "Final inclusion criteria pending Phase 2 predictor feasibility"
        })

        verif_rows.append({
            "variable": col, "official_description": desc, "official_unit": unit, "source_xpt_file": src,
            "data_type": dtype, "verified_against_official_documentation": official,
            "documentation_source_url": doc_url, "coding_notes": notes, "quality_restriction": qual_restr,
            "verification_date": "2026-08-18"
        })

    pd.DataFrame(dd_rows).to_csv(DICT_DIR / "phase1_master_data_dictionary.csv", index=False)
    pd.DataFrame(verif_rows).to_csv(DICT_DIR / "variable_source_verification.csv", index=False)
    n_unverified = sum(1 for r in verif_rows if not r["verified_against_official_documentation"])
    print(f"  Saved phase1_master_data_dictionary.csv ({len(dd_rows)} variables).")
    print(f"  Saved variable_source_verification.csv ({len(verif_rows)} variables, "
          f"{n_unverified} not yet verified against an official source -- flagged for Phase 2 follow-up).")

    with open(META_DIR / "survey_design_notes.md", "w") as f:
        f.write(f"# NHANES Survey Design Metadata & Guidelines (Remediated)\n\n**Generated:** {NOW}\n\n")
        f.write("NHANES uses a complex, multistage, probability sampling design. Any representative prevalence "
                "estimate or statistical test must incorporate survey weights, primary sampling units (PSU), "
                "and strata to avoid biased estimates.\n\n")
        f.write("## Preserved Survey Design Variables in Master Dataset (NOT yet applied to any analysis)\n\n")
        f.write("- **`WTMECPRP`**: Full-sample 2-cycle MEC Exam Weight. Required for elastography (FibroScan) "
                "analysis since it is a MEC exam component.\n")
        f.write("- **`WTINTPRP`**: Full-sample 2-cycle Interview Weight. Use only for interview-only variables.\n")
        f.write("- **`WTSAFPRP`**: Fasting Subsample Weight (confirmed correct name for this cycle). Required "
                "if analysis is restricted to the fasting subsample (glucose/triglycerides).\n")
        f.write("- **`SDMVPSU`** / **`SDMVSTRA`**: Masked variance pseudo-PSU / pseudo-stratum, for Taylor-series "
                "variance estimation under the masked complex design.\n\n")

        f.write("## Official NHANES Weight-Selection Rule (verified quote, NHANES Weighting Tutorial)\n\n")
        f.write("> \"You must use the weight of the smallest subpopulation that includes all the variables you "
                "want to include in your analysis.\" NHANES's own worked example uses exactly this project's "
                "scenario: triglycerides are measured on a fasting MEC subsample, so \"the fasting subsample is "
                "the smallest subsample in the analysis and you would use the AM fasting weights.\"\n\n")
        f.write("**Direct application to this project:** any analysis combining FibroScan/MEC-exam variables "
                "with glucose or triglycerides must use `WTSAFPRP`, not `WTMECPRP`. Analyses that exclude the "
                "fasting-only labs may use `WTMECPRP`. This rule is sourced from NHANES's own tutorial, not "
                "inferred by this project.\n\n")

        f.write("## Phase 2 Methodological Guidelines (still open decisions)\n\n")
        f.write("1. **Weight selection** follows the rule above once the final predictor set (broad vs. "
                "fasting-extended, see broad_vs_fasting_cohort.md) is locked.\n")
        f.write("2. **ML training vs. weighting:** Official NHANES materials are SILENT on whether/how survey "
                "weights should be used inside predictive model training (vs. reserved for population-"
                "representative estimation and variance calculation). This is a genuinely open methodological "
                "question that NHANES documentation does not resolve -- it must be answered from general "
                "survey-statistics/ML methodology literature in Phase 2, not attributed to NHANES guidance.\n")
        f.write("3. **Design variables** (`SDMVPSU`/`SDMVSTRA`) should be used for any variance/CI estimation "
                "that claims population representativeness; not required for internal train/test ML validation "
                "splits, which is a separate concern from population inference.\n")

    print("  Saved survey_design_notes.md (with verified official weighting-tutorial citation).")
    print("[STEP 19, 22 & 23 COMPLETE]")

if __name__ == "__main__":
    main()
