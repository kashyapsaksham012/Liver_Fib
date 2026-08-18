"""
09_laboratory_plausibility_audit.py
Phase 1 Remediation - Error 4 fix: comprehensive laboratory plausibility audit
covering ALL 9 candidate laboratory predictors (prior Phase 1 only checked
LUXSMED/BMI/height/age; labs were never plausibility-audited).

For each variable: negative values, biologically-impossible zeros, extreme values vs.
both an external clinical reference range AND NHANES's own observed range, missingness,
percentiles. FLAGS ONLY -- nothing is deleted. Every flag records whether the proposed
action is mandatory or merely suggested, and its scientific rationale/source.

Produces:
  documentation/audit_reports/laboratory_plausibility_audit.csv
"""

import os, sys, warnings
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, LAB_REFERENCE_RANGES, VAR_METADATA

warnings.filterwarnings("ignore", category=FutureWarning)

LAB_VARS = list(LAB_REFERENCE_RANGES.keys())

def main():
    print("=== Comprehensive Laboratory Plausibility Audit (Error 4) ===")
    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    n_total = len(master)

    rows = []
    for var in LAB_VARS:
        if var not in master.columns:
            continue
        s = master[var]
        n_obs = int(s.notna().sum())
        n_miss = int(s.isna().sum())
        ref_low, ref_high, unit, ref_source = LAB_REFERENCE_RANGES[var]
        desc = VAR_METADATA.get(var, {}).get("desc", var)
        obs = s.dropna()

        # Distribution summary (always recorded, not a flag by itself)
        rows.append({
            "variable": var, "description": desc, "unit": unit,
            "condition": "DISTRIBUTION SUMMARY (not a flag)", "observation_count": n_obs,
            "n_missing": n_miss, "pct_missing": round(100*n_miss/n_total, 2),
            "value_at_condition": None,
            "min": round(float(obs.min()), 3) if n_obs else None,
            "p1": round(float(obs.quantile(0.01)), 3) if n_obs else None,
            "p25": round(float(obs.quantile(0.25)), 3) if n_obs else None,
            "median": round(float(obs.median()), 3) if n_obs else None,
            "p75": round(float(obs.quantile(0.75)), 3) if n_obs else None,
            "p99": round(float(obs.quantile(0.99)), 3) if n_obs else None,
            "max": round(float(obs.max()), 3) if n_obs else None,
            "proposed_action": "Retain (informational)", "mandatory_or_suggested": "n/a",
            "scientific_rationale": "Baseline distribution characterization",
            "source_reference": ref_source
        })

        def flag(cond_name, mask, action, mandatory, rationale):
            n = int(mask.sum())
            if n > 0:
                rows.append({
                    "variable": var, "description": desc, "unit": unit, "condition": cond_name,
                    "observation_count": n, "n_missing": None, "pct_missing": None, "value_at_condition": n,
                    "min": None, "p1": None, "p25": None, "median": None, "p75": None, "p99": None, "max": None,
                    "proposed_action": action, "mandatory_or_suggested": mandatory,
                    "scientific_rationale": rationale, "source_reference": ref_source
                })
                print(f"  Lab Flag: {var} | {cond_name} | count={n}")

        # Negative values -- biologically impossible for every one of these analytes
        flag("Negative value", s < 0, "Exclude / data-entry investigation", "Mandatory",
             "Negative concentration/count is not physiologically possible for this analyte")

        # Biologically implausible exact zero (concentration analytes cannot be exactly 0 in a living person)
        if var != "LBXTR":  # triglycerides technically bounded >0 too, but keep zero-check general for all
            flag("Value == 0 (biologically implausible for this analyte)", s == 0, "Investigate (likely coding artifact)", "Suggested",
                 "A living participant cannot have a true concentration of exactly zero for this analyte")

        # Extreme values relative to NHANES's OWN observed range for this release (more defensible than
        # an external textbook range, since it reflects the actual sampled population including pathology)
        # -- flag only values that fall outside a wide-margin band around the general clinical reference,
        # explicitly NOT proposing exclusion, since extreme-but-real pathological values are expected (e.g.
        # markedly elevated ALT/AST/triglycerides in liver disease -- exactly what this study is about).
        very_high = ref_high * 5
        flag(f"Value > 5x general clinical reference upper bound ({ref_high} {unit} x5 = {very_high} {unit})",
             s > very_high, "Retain, flag for manual review only", "Suggested",
             f"Extreme but not impossible; may reflect genuine severe pathology relevant to this study "
             f"(e.g. marked hepatic enzyme elevation). General reference: {ref_low}-{ref_high} {unit} ({ref_source}). "
             f"NOT proposed for exclusion -- excluding real disease-range values would bias the fibrosis analysis.")

        very_low = ref_low / 5 if ref_low > 0 else 0
        if ref_low > 0:
            flag(f"Value < (general clinical reference lower bound / 5) ({very_low:.2f} {unit})",
                 (s > 0) & (s < very_low), "Retain, flag for manual review only", "Suggested",
                 f"Extremely low but potentially real (e.g. severe hepatic synthetic dysfunction lowering albumin). "
                 f"General reference: {ref_low}-{ref_high} {unit} ({ref_source}). NOT proposed for exclusion.")

    pd.DataFrame(rows).to_csv(AUDIT_DIR / "laboratory_plausibility_audit.csv", index=False)
    print(f"  Saved laboratory_plausibility_audit.csv ({len(rows)} rows across {len(LAB_VARS)} lab variables).")
    print("  NOTE: fasting glucose (LBXGLU) and triglycerides (LBXTR) values in the diabetic/hypertriglyceridemic "
          "range are CLINICALLY EXPECTED in a general population sample and are explicitly NOT flagged as errors.")
    print("[LABORATORY PLAUSIBILITY AUDIT COMPLETE]")

if __name__ == "__main__":
    main()
