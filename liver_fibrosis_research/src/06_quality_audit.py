"""
06_quality_audit.py  –  Phase 1 Steps 14–16
Plausibility audit, outlier detection, liver stiffness descriptive plots,
cohort flow documentation.

Outputs:
  documentation/audit_reports/plausibility_audit.csv
  documentation/audit_reports/cohort_flow.csv
  documentation/audit_reports/cohort_flow.md
  results/figures/liver_stiffness_by_sex.png
  results/figures/liver_stiffness_by_age.png
"""

import datetime, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT    = Path(__file__).resolve().parent.parent
INT_DIR = ROOT / "data" / "interim"
AUD_DIR = ROOT / "documentation" / "audit_reports"
FIG_DIR = ROOT / "results" / "figures"
AUD_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
print(f"Loaded master: {master.shape}")

# ── Identify key variables ────────────────────────────────────────────────────
stiff_var = next((c for c in master.columns if c in ("LUXSMED",)), None) or \
            next((c for c in master.columns if "LUXS" in c and pd.api.types.is_numeric_dtype(master[c])), None)
cap_var   = next((c for c in master.columns if "LUXCAPM" in c), None)
bmi_var   = next((c for c in master.columns if c == "BMXBMI"), None)
ht_var    = next((c for c in master.columns if c == "BMXHT"), None)
wt_var    = next((c for c in master.columns if c == "BMXWT"), None)
age_var   = next((c for c in master.columns if c == "RIDAGEYR"), None)
sex_var   = next((c for c in master.columns if c == "RIAGENDR"), None)

print(f"  Key vars → stiffness:{stiff_var} | CAP:{cap_var} | BMI:{bmi_var} | age:{age_var} | sex:{sex_var}")

# ── Plausibility audit ────────────────────────────────────────────────────────
plaus_rows = []

def flag(var, condition_desc, mask, proposed_action, justification):
    n = int(mask.sum())
    if n > 0:
        plaus_rows.append({"variable":var, "suspected_issue":condition_desc,
                           "observation_count":n,
                           "proposed_action":proposed_action,
                           "justification":justification})
        print(f"  PLAUSIBILITY FLAG [{var}] {condition_desc}: {n} records")

if stiff_var and stiff_var in master.columns:
    sv = master[stiff_var]
    flag(stiff_var, "Stiffness < 1.5 kPa (below device floor)",
         sv < 1.5, "Exclude – device minimum", "FibroScan minimum reliable measurement")
    flag(stiff_var, "Stiffness > 75 kPa (upper device limit)",
         sv > 75, "Review – may be valid biological extreme", "FibroScan upper limit ~75 kPa")
    flag(stiff_var, "Negative stiffness",
         sv < 0,  "Exclude – impossible value", "Stiffness cannot be negative")

if bmi_var and bmi_var in master.columns:
    bv = master[bmi_var]
    flag(bmi_var, "BMI < 10 (implausible for adults)",
         bv < 10,  "Investigate – do not auto-remove", "May reflect measurement error or age issue")
    flag(bmi_var, "BMI > 80 (extreme outlier)",
         bv > 80,  "Investigate – do not auto-remove", "Possible but unusual; confirm with height/weight")

if ht_var and ht_var in master.columns:
    hv = master[ht_var]
    flag(ht_var, "Height < 130 cm",
         hv < 130, "Investigate", "Participants should be adults; check age linkage")
    flag(ht_var, "Height > 220 cm",
         hv > 220, "Investigate", "Biologically implausible for most adults")

if age_var and age_var in master.columns:
    av = master[age_var]
    flag(age_var, "Age < 18",
         av < 18, "Potentially exclude – adults only study", "FibroScan reference values are adult-specific")

pd.DataFrame(plaus_rows).to_csv(AUD_DIR / "plausibility_audit.csv", index=False)
print(f"  Saved plausibility_audit.csv ({len(plaus_rows)} flags)")

# ── Liver stiffness plots by demographic ─────────────────────────────────────
if stiff_var and sex_var and stiff_var in master.columns and sex_var in master.columns:
    sv_clean = master[[stiff_var, sex_var, age_var or stiff_var]].dropna(subset=[stiff_var])
    sex_labels = {1.0:"Male", 2.0:"Female"}
    sv_clean["Sex"] = sv_clean[sex_var].map(sex_labels)

    fig, axes = plt.subplots(1,2, figsize=(14,5))
    for ax, (label, grp) in zip(axes, sv_clean.groupby("Sex")):
        ax.hist(grp[stiff_var], bins=50, color="#1976D2" if label=="Male" else "#E91E63", edgecolor="white", alpha=0.8)
        ax.set_title(f"Liver Stiffness – {label}")
        ax.set_xlabel("kPa"); ax.set_ylabel("Count")
    plt.suptitle("Liver Stiffness Distribution by Sex (Descriptive Only – Phase 1)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "liver_stiffness_by_sex.png", dpi=150)
    plt.close()
    print("  Saved liver_stiffness_by_sex.png")

if stiff_var and age_var and stiff_var in master.columns and age_var in master.columns:
    ag = master[[stiff_var, age_var]].dropna()
    fig, ax = plt.subplots(figsize=(10,5))
    sc = ax.scatter(ag[age_var], ag[stiff_var], alpha=0.3, s=8, c="#7B1FA2")
    ax.set_xlabel("Age (years)"); ax.set_ylabel("Liver Stiffness (kPa)")
    ax.set_title("Liver Stiffness vs Age (Descriptive – Phase 1)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "liver_stiffness_by_age.png", dpi=150)
    plt.close()
    print("  Saved liver_stiffness_by_age.png")

# ── Cohort flow ───────────────────────────────────────────────────────────────
n_lux_total = master.shape[0]
n_valid_stiff = int(master[stiff_var].notna().sum()) if stiff_var else 0
n_adult       = int((master[age_var] >= 18).sum()) if age_var else "N/A"
n_has_demo    = int(master[sex_var].notna().sum())  if sex_var else "N/A"
n_has_bmi     = int(master[bmi_var].notna().sum())  if bmi_var else "N/A"

flow_records = [
    {"step":"P_LUX total participants",             "n":n_lux_total, "excluded":0,    "reason":"Starting cohort"},
    {"step":"Valid liver stiffness measurement",    "n":n_valid_stiff, "excluded":n_lux_total-n_valid_stiff, "reason":"Missing/invalid FibroScan"},
    {"step":"Age ≥ 18 (adults only – candidate)",  "n":n_adult,      "excluded":"TBD","reason":"Pending Phase 2 outcome definition"},
    {"step":"Demographic data available",           "n":n_has_demo,   "excluded":"TBD","reason":"Required for fairness analysis"},
    {"step":"BMI available",                        "n":n_has_bmi,    "excluded":"TBD","reason":"Candidate predictor/subgroup"},
    {"step":"Laboratory data available",            "n":"PENDING",    "excluded":"PENDING","reason":"Lab files not yet downloaded"},
]

pd.DataFrame(flow_records).to_csv(AUD_DIR / "cohort_flow.csv", index=False)

with open(AUD_DIR / "cohort_flow.md","w") as f:
    f.write(f"# Cohort Flow — Phase 1 (Candidate)\n\n**Generated:** {NOW}\n\n")
    f.write("> NOTE: This is a CANDIDATE cohort flow. Final exclusion criteria "
            "and the exact cohort N will be defined in Phase 2.\n\n")
    f.write("```\n")
    for r in flow_records:
        f.write(f"  {r['step']}\n")
        f.write(f"    N = {r['n']} | Excluded = {r['excluded']} | Reason: {r['reason']}\n")
        f.write("    ↓\n")
    f.write("  [FINAL COHORT: defined in Phase 2]\n```\n\n")
    f.write("\n## Outstanding Decisions for Phase 2\n\n")
    f.write("- Define exact fibrosis outcome threshold (e.g., ≥ 8 kPa)\n")
    f.write("- Confirm adult-only restriction and age floor\n")
    f.write("- Define FibroScan quality/IQR inclusion criteria\n")
    f.write("- Handle laboratory missingness (imputation strategy)\n")
    f.write("- Define race/ethnicity groupings for fairness analysis\n")
    f.write("- Define BMI category cutpoints\n")
    f.write("- Decide whether to apply NHANES survey weights to prevalence estimates\n")

print(f"  Saved cohort_flow.csv and cohort_flow.md")
print("[STEP 6 (QUALITY AUDIT) COMPLETE]")
