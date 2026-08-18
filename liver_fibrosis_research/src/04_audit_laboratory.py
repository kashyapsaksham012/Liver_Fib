"""
04_audit_laboratory.py
Phase 1 Remediation - Dedicated audit of laboratory XPT files (sentinel-corrected).
Documents the fasting-subsample structure of P_GLU/P_TRIGLY explicitly (Error 9 groundwork).

Produces:
  documentation/audit_reports/laboratory_audit_report.md
  documentation/audit_reports/laboratory_inventory.csv
"""

import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import AUDIT_DIR, NOW, load_xpt, VAR_METADATA

LAB_FILES = ["P_BIOPRO.xpt", "P_CBC.xpt", "P_GLU.xpt", "P_TRIGLY.xpt", "P_HDL.xpt"]
LAB_KEY_VARS = {
    "P_BIOPRO.xpt": ["LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXSGL"],
    "P_CBC.xpt":    ["LBXPLTSI"],
    "P_GLU.xpt":    ["LBXGLU", "WTSAFPRP"],
    "P_TRIGLY.xpt": ["LBXTR", "WTSAFPRP"],
    "P_HDL.xpt":    ["LBDHDD"]
}
FASTING_FILES = {"P_GLU.xpt", "P_TRIGLY.xpt"}

def main():
    print("=== Step 9: Dedicated Audit of Laboratory Datasets (Remediated) ===")

    lux = load_xpt("P_LUX.xpt")
    lux_seqns = set(lux["SEQN"].dropna())
    print(f"Loaded P_LUX: N={len(lux_seqns)} unique participants (denominator for overlap %).")

    lab_inventory = []
    with open(AUDIT_DIR / "laboratory_audit_report.md", "w") as f:
        f.write(f"# Laboratory File Audit Report (Remediated)\n\n**Generated:** {NOW}\n\n")
        f.write("Profiles the five required NHANES 2017-March 2020 pre-pandemic laboratory files, "
                "sentinel-corrected. Fasting-subsample structure documented explicitly per component.\n\n")

        for name in LAB_FILES:
            print(f"Auditing lab file: {name}...")
            is_fasting = name in FASTING_FILES
            try:
                ldf = load_xpt(name)
                rows, cols = ldf.shape
                unique_seqn = ldf["SEQN"].nunique()
                missing_seqn = ldf["SEQN"].isna().sum()
                dup_seqn = rows - unique_seqn
                lab_seqns = set(ldf["SEQN"].dropna())
                overlap = len(lux_seqns.intersection(lab_seqns))
                overlap_pct = round(100 * overlap / len(lux_seqns), 2) if lux_seqns else 0.0

                f.write(f"## {name} {'[FASTING SUBSAMPLE ONLY]' if is_fasting else '[Broad MEC sample]'}\n\n")
                f.write(f"- **Dimensions:** {rows} rows x {cols} columns\n")
                f.write(f"- **Unique SEQN:** {unique_seqn}\n- **Missing SEQN:** {missing_seqn}\n")
                f.write(f"- **Duplicate SEQN:** {dup_seqn}\n")
                f.write(f"- **Overlap with P_LUX cohort:** {overlap} participants ({overlap_pct}% of P_LUX N={len(lux_seqns)})\n\n")

                if is_fasting:
                    f.write("> **Fasting subsample caveat (verified from official NHANES documentation):** "
                            "eligibility requires age 12+, examination in the morning session, and a fast of "
                            "8 to <24 hours. This is a materially smaller and non-random subpopulation of the "
                            "full P_LUX/MEC cohort, not just 'extra missingness'. The paired weight variable "
                            "`WTSAFPRP` is 0 (not merely missing) for fasting-eligible participants who gave no "
                            "specimen or did not meet the fasting window -- a documented, meaningful code.\n\n")
                    if "WTSAFPRP" in ldf.columns:
                        n_zero = int((ldf["WTSAFPRP"] == 0).sum())
                        f.write(f"- **`WTSAFPRP == 0` count in this file:** {n_zero} "
                                f"(fasting-eligible but excluded from valid fasting analysis)\n\n")

                f.write("### Target Variables Profile\n\n")
                f.write("| Variable | Official Description | Unit | Valid Obs | Missing | Missing % | Min | Max | Mean |\n")
                f.write("|---|---|---|---|---|---|---|---|---|\n")
                for var in ldf.columns:
                    v_obs = int(ldf[var].notna().sum()); v_miss = int(ldf[var].isna().sum())
                    v_miss_pct = round(100 * v_miss / rows, 2)
                    v_min = v_max = v_mean = "N/A"
                    if pd.api.types.is_numeric_dtype(ldf[var]) and v_obs > 0:
                        v_min = f"{ldf[var].min():.2f}"; v_max = f"{ldf[var].max():.2f}"; v_mean = f"{ldf[var].mean():.2f}"
                    is_key = var in LAB_KEY_VARS.get(name, [])
                    role = VAR_METADATA.get(var, {}).get("role", "auxiliary_lab" if not is_key else "candidate_predictor")
                    desc = VAR_METADATA.get(var, {}).get("desc", "-")
                    lab_inventory.append({
                        "source_file": name, "variable": var, "rows": rows, "unique_seqn": unique_seqn,
                        "overlap_with_lux": overlap, "overlap_pct": overlap_pct, "n_obs": v_obs, "n_missing": v_miss,
                        "pct_missing": v_miss_pct, "min": v_min, "max": v_max, "mean": v_mean,
                        "is_key_variable": is_key, "is_fasting_subsample": is_fasting
                    })
                    if is_key or var == "SEQN":
                        f.write(f"| `{var}` | {desc} | - | {v_obs} | {v_miss} | {v_miss_pct}% | {v_min} | {v_max} | {v_mean} |\n")
                f.write("\n---\n\n")
            except Exception as e:
                f.write(f"## {name}\n\n**Error Loading File:** {e}\n\n---\n\n")
                print(f"  Error auditing {name}: {e}")

    pd.DataFrame(lab_inventory).to_csv(AUDIT_DIR / "laboratory_inventory.csv", index=False)
    print("Saved laboratory inventory CSV.")
    print("[STEP 9 COMPLETE]")

if __name__ == "__main__":
    main()
