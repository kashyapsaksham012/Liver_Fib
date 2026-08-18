"""
07_quality_and_plausibility_audit.py
Phase 1 Remediation - Corrected Cohort Flow, Plausibility (demographic/LUX vars),
Descriptive Outcome Plots.

FIXES APPLIED (see PHASE1_DATA_ASSEMBLY_REPORT.md section U for full audit trail):
  - Error 1: every cohort-flow transition is now verified with assert_flow()
    (before - excluded == after); the pipeline halts loudly on any mismatch
    instead of writing "TBD" placeholders that could hide an inconsistency.
  - Error 2/3: "non-missing LUXSMED" and "LUAXSTAT==1 (NHANES quality-valid)"
    are tracked as two distinct columns at every cohort stage, never conflated.
  - Error 9: the fasting-lab subset is reported as a separate branch, not
    chained into the main sequential exclusion flow.
  - Part 8: candidate outcome cutpoints are sourced from _common.CANDIDATE_THRESHOLDS
    (external clinical literature, explicitly labeled candidate/provisional).

Produces:
  documentation/audit_reports/plausibility_audit.csv
  documentation/audit_reports/cohort_flow.csv
  documentation/audit_reports/cohort_flow.md
  results/figures/liver_stiffness_by_sex.png
  results/figures/liver_stiffness_by_age.png
"""

import os, sys, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(__file__))
from _common import INT_DIR, AUDIT_DIR, FIG_DIR, NOW, assert_flow, CANDIDATE_THRESHOLDS, CORE_LABS_BROAD, CORE_LABS_FASTING, SEX_MAP
from _cohorts import verify_cohort_relationships

warnings.filterwarnings("ignore", category=FutureWarning)

def main():
    print("=== Step 11, 14, 17, 18 & 20: Quality, Plausibility & CORRECTED Cohort Flow ===")

    master = pd.read_parquet(INT_DIR / "nhanes_master_phase1.parquet")
    n_total = len(master)

    # ── Plausibility Audit (demographic / anthropometric / LUX only; labs -> script 09) ──
    plaus_rows = []
    def flag(var, cond_name, mask, action, justification):
        n = int(mask.sum())
        if n > 0:
            plaus_rows.append({"variable": var, "suspected_issue": cond_name, "observation_count": n,
                               "proposed_action": action, "justification": justification})
            print(f"  Plausibility Flag: {var} | {cond_name} | count={n}")

    flag("LUXSMED", "Stiffness < 1.5 kPa (below NHANES-documented observed min of 1.6)", master["LUXSMED"] < 1.5, "Investigate", "Below NHANES's own documented observed range for this release")
    flag("LUXSMED", "Stiffness > 75.0 kPa (at/above NHANES-documented observed max)", master["LUXSMED"] > 75.0, "Review", "May represent biological extreme or device ceiling artifact")
    flag("LUXSMED", "Negative Stiffness", master["LUXSMED"] < 0, "Exclude", "Physically impossible stiffness measurement")
    flag("BMXBMI", "BMI < 10 (implausible for the sampled age range)", master["BMXBMI"] < 10, "Investigate", "Implausible BMI; NHANES itself gives no numeric cutoff, this is an external convention")
    flag("BMXBMI", "BMI > 80 (extreme outlier, near NHANES-documented observed max of 92.3)", master["BMXBMI"] > 80, "Review", "Extreme biological value; verify height/weight jointly, not evidence of error by itself")
    flag("BMXHT", "Height < 130 cm", master["BMXHT"] < 130, "Investigate", "Usually reflects younger adolescents in the 12-17y P_LUX-eligible range; check age jointly")
    flag("RIDAGEYR", "Age < 18", master["RIDAGEYR"] < 18, "Not excluded in Phase 1", "Adult-only restriction is a Phase 2 protocol decision, not applied here")
    pd.DataFrame(plaus_rows).to_csv(AUDIT_DIR / "plausibility_audit.csv", index=False)
    print("  Saved plausibility_audit.csv.")

    # ── CORRECTED Cohort Flow — now driven ENTIRELY by the canonical _cohorts module ──
    # (Phase 1 Closure: this replaces locally-recomputed masks with the single source of
    # truth in _cohorts.py, so this script and 13_broad_vs_fasting_cohort.py can never
    # again define "the fasting cohort" / "the broad cohort" differently -- see
    # verify_cohort_relationships() below and results/tables/*_discrepancy.csv for the
    # traced Issue 1 / Issue 2 reconciliation.)
    cohorts = verify_cohort_relationships(master)  # raises loudly if any relationship breaks

    def valid_quality_pct(mask):
        pop = master.loc[mask]
        return round(100 * (pop["LUAXSTAT"] == 1.0).sum() / len(pop), 2) if len(pop) else 0.0

    flow = []

    def add_step(step_label, before_name, after_name, reason):
        n_before = cohorts[before_name][2] if before_name else cohorts[after_name][2]
        after_mask = cohorts[after_name][0]
        before_mask = cohorts[before_name][0] if before_name else after_mask
        n_after = cohorts[after_name][2]
        n_excl = int((before_mask & ~after_mask).sum()) if before_name else 0
        assert_flow(n_before, n_excl, n_after, step_label)
        flow.append({"step": step_label, "cohort_id": after_name, "n_before": n_before, "n_excluded": n_excl,
                    "n_after": n_after, "pct_LUAXSTAT_eq_1": valid_quality_pct(after_mask), "reason": reason})

    add_step("0. P_LUX Total Participants (source cohort denominator)", None, "COHORT_0_SOURCE",
              "Root cohort; every subsequent row is a subset of this population")
    add_step("1. Non-missing LUXSMED (NOTE: non-missingness, NOT the NHANES quality-valid flag)",
              "COHORT_0_SOURCE", "COHORT_1_NONMISSING_LUX",
              "Missing/invalid FibroScan attempt (LUAXSTAT in {3,4}, or {2} with no numeric result)")
    add_step("1b. NHANES Quality-Valid Elastography (LUAXSTAT==1), among Step 1 (Issue 3)",
              "COHORT_1_NONMISSING_LUX", "COHORT_2_QUALITY_VALID",
              "Official NHANES 'Complete' definition (fasting>=3h, >=10 complete measures, IQRe/Med<30%) -- "
              "see documentation/source_metadata/lux_quality_rule_source.md. These 677 participants have a "
              "non-missing LUXSMED from a Partial (LUAXSTAT=2) exam that does not meet the full quality bar.")
    add_step("2a. Adult Participants (Age>=18), among Step 1 (non-missing LUXSMED)",
              "COHORT_1_NONMISSING_LUX", "COHORT_3A_ADULT_OF_NONMISSING",
              "CANDIDATE Phase 2 restriction, reported for descriptive flow accounting only")
    add_step("2b. Adult Participants (Age>=18), among Step 1b (quality-valid) (Issue 6)",
              "COHORT_2_QUALITY_VALID", "COHORT_3B_ADULT_OF_QUALITY_VALID",
              "Reported separately because the quality-valid population (9,023) is NOT the same as the "
              "non-missing population (9,700) -- the two adult counts are not assumed identical")
    add_step("3. Demographics Available (RIAGENDR non-missing), among Step 1", "COHORT_1_NONMISSING_LUX",
              "COHORT_1_NONMISSING_LUX", "Fairness analysis requirement")  # RIAGENDR is 100% complete; see TEST below
    add_step("4a. Broad Routine-Lab Predictors Available (Cohort A), among Step 1",
              "COHORT_1_NONMISSING_LUX", "COHORT_A_BROAD_LAB",
              f"Candidate broad-lab predictor cohort ({', '.join(CORE_LABS_BROAD)} all non-missing); "
              "does NOT require BMI/demographics (Issue 9: renamed for clarity, was 'Step 5')")
    add_step("4b. Cohort A FURTHER restricted to complete demographics + BMI (Issue 2/9)",
              "COHORT_A_BROAD_LAB", "COHORT_A_PLUS_DEMO_BMI",
              "Strict nesting inside Cohort A. NOT a separate lab-availability concept, and NOT the same "
              "population as Cohort A (75-participant gap, entirely explained by missing BMI -- see "
              "results/tables/broad_cohort_discrepancy.csv). Renamed from ambiguous 'combined broad cohort'.")
    add_step("5a. Fasting-Subsample Labs Available ONLY (glucose+triglycerides, broad NOT required)",
              "COHORT_1_NONMISSING_LUX", "COHORT_FASTING_LABS_ONLY",
              "[BRANCH, not chained into the main flow] Renamed from ambiguous 'fasting labs available' -- "
              "see results/tables/fasting_cohort_discrepancy.csv for why this differs from Cohort B below")
    add_step("5b. Cohort B = Fasting-Extended (Cohort A AND fasting labs) (Issue 1, THE canonical 'Cohort B')",
              "COHORT_A_BROAD_LAB", "COHORT_B_FASTING_EXTENDED",
              "Requires BOTH broad labs (Cohort A) AND fasting labs. Exactly the intersection of Step 4a and "
              "Step 5a (asserted programmatically in _cohorts.verify_cohort_relationships) -- this IS the "
              "authoritative Cohort B number used everywhere else in this pipeline (4,336, not 4,376).")

    # TEST-style explicit check backing the "3. Demographics Available" step's shortcut above
    assert master.loc[cohorts["COHORT_1_NONMISSING_LUX"][0], "RIAGENDR"].isna().sum() == 0, \
        "RIAGENDR is not actually 100% complete within Cohort 1 -- Step 3 shortcut is invalid, fix required."

    flow_df = pd.DataFrame(flow)
    flow_df.to_csv(AUDIT_DIR / "cohort_flow.csv", index=False)

    with open(AUDIT_DIR / "cohort_flow.md", "w") as f:
        f.write(f"# Candidate Cohort Flow — Phase 1 CLOSURE (Canonical, Arithmetically Verified)\n\n**Generated:** {NOW}\n\n")
        f.write("> Every row below satisfies `n_before - n_excluded == n_after` (asserted programmatically). "
                "Every named cohort is defined EXACTLY ONCE in `src/_cohorts.py` and imported here -- this "
                "script no longer recomputes any mask locally, closing the discrepancy class documented in "
                "`results/tables/fasting_cohort_discrepancy.csv` and `broad_cohort_discrepancy.csv`. Steps "
                "2a/2b, 4a/4b, and 5a/5b are branches computed independently against their stated parent "
                "population, NOT chained sequentially, so no single combination is silently pre-selected as "
                "'the' final cohort.\n\n")
        f.write("| Step | Cohort ID | N Before | N Excluded | N After | % LUAXSTAT==1 in result | Reason |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in flow:
            f.write(f"| {r['step']} | `{r['cohort_id']}` | {r['n_before']} | {r['n_excluded']} | {r['n_after']} | {r['pct_LUAXSTAT_eq_1']}% | {r['reason']} |\n")
        f.write("\n**Final inclusion/exclusion logic, adult-only decision, and quality-valid-only decision all "
                "remain OPEN Phase 2 protocol decisions. No cohort defined above is asserted to be final.**\n")
    print("  Saved cohort_flow.csv and cohort_flow.md (canonical cohorts, all transitions arithmetically verified).")

    # ── Descriptive Liver Stiffness Plots (LUXSMED by sex / age) ─────────────────────
    if "RIAGENDR" in master.columns and "LUXSMED" in master.columns:
        sv_clean = master[["LUXSMED", "RIAGENDR", "RIDAGEYR"]].dropna(subset=["LUXSMED"]).copy()
        sv_clean["Sex"] = sv_clean["RIAGENDR"].map(SEX_MAP)
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        for ax, (lbl, grp) in zip(axes, sv_clean.groupby("Sex")):
            ax.hist(grp["LUXSMED"], bins=50, color="#1E88E5" if lbl == "Male" else "#D81B60", edgecolor="white", alpha=0.8)
            ax.set_title(f"Liver Stiffness Distribution (non-missing LUXSMED) - {lbl}")
            ax.set_xlabel("kPa"); ax.set_ylabel("Count")
        plt.suptitle("Liver Stiffness by Sex (DESCRIPTIVE ONLY -- Phase 1; no model exists, this is not 'bias')")
        plt.tight_layout(); plt.savefig(FIG_DIR / "liver_stiffness_by_sex.png", dpi=150); plt.close()
        print("  Saved liver_stiffness_by_sex.png.")

    if "RIDAGEYR" in master.columns and "LUXSMED" in master.columns:
        ag = master[["LUXSMED", "RIDAGEYR"]].dropna()
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(ag["RIDAGEYR"], ag["LUXSMED"], alpha=0.25, s=6, color="#8E24AA")
        ax.set_xlabel("Age (years, topcoded at 80)"); ax.set_ylabel("Liver Stiffness (kPa)")
        ax.set_title("Liver Stiffness vs Age (DESCRIPTIVE ONLY -- Phase 1)")
        plt.tight_layout(); plt.savefig(FIG_DIR / "liver_stiffness_by_age.png", dpi=150); plt.close()
        print("  Saved liver_stiffness_by_age.png.")

    print("[STEP 11, 14, 17, 18 & 20 COMPLETE]")

if __name__ == "__main__":
    main()
