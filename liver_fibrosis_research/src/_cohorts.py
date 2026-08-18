"""
_cohorts.py
Phase 1 Closure — SINGLE CANONICAL SOURCE OF TRUTH for every named data-feasibility
cohort used anywhere in this pipeline (report, tables, figures, validation tests).

Why this file exists: prior to closure, scripts 07 (cohort_flow) and 13
(broad_vs_fasting_cohort) each independently recomputed "the fasting cohort" and
"the broad cohort" with subtly different filter sets, producing two different,
individually-correct-but-differently-defined numbers (4,376 vs 4,336; 8,880 vs
8,805) under the same loose label. Both were traced exactly (see
results/tables/fasting_cohort_discrepancy.csv and broad_cohort_discrepancy.csv) and
confirmed to be legitimate distinct cohorts, not bugs. Going forward, EVERY script
that needs one of these populations MUST import it from here — never recompute it
locally — so this exact failure mode is architecturally prevented, not just patched.

Each cohort is a function `mask, meta = COHORT_X(master)` returning a boolean Series
(index-aligned to `master`) and a metadata dict fully describing the definition.
"""

import pandas as pd
from _common import CORE_LABS_BROAD, CORE_LABS_FASTING


def COHORT_0_SOURCE(master):
    mask = pd.Series(True, index=master.index)
    meta = dict(name="COHORT_0_SOURCE", purpose="Root cohort denominator: every P_LUX-examined participant",
                source_population="P_LUX (all rows)", inclusion="None (source population)", exclusion="None",
                required_variables="-", requires_nonmissing_luxsmed=False, requires_quality_valid=False,
                requires_adult=False, requires_bmi=False, requires_broad_labs=False, requires_fasting_labs=False)
    return mask, meta


def COHORT_1_NONMISSING_LUX(master):
    mask = master["LUXSMED"].notna()
    meta = dict(name="COHORT_1_NONMISSING_LUX",
                purpose="Participants with a non-missing liver stiffness value, ANY exam completeness "
                        "(NOT the NHANES quality-valid definition -- see COHORT_2)",
                source_population="COHORT_0_SOURCE", inclusion="LUXSMED is not null",
                exclusion="LUXSMED missing (LUAXSTAT in {3='Ineligible',4='Not done'}, or {2='Partial'} with no numeric result)",
                required_variables="LUXSMED", requires_nonmissing_luxsmed=True, requires_quality_valid=False,
                requires_adult=False, requires_bmi=False, requires_broad_labs=False, requires_fasting_labs=False)
    return mask, meta


def COHORT_2_QUALITY_VALID(master):
    mask = master["LUAXSTAT"] == 1.0
    meta = dict(name="COHORT_2_QUALITY_VALID",
                purpose="OFFICIAL NHANES quality-valid elastography exam ('Complete')",
                source_population="COHORT_0_SOURCE", inclusion="LUAXSTAT == 1",
                exclusion="LUAXSTAT in {2,3,4}",
                required_variables="LUAXSTAT (official definition: fasting>=3h, >=10 complete stiffness "
                                    "measures, IQRe/median<30% -- verified against the live P_LUX codebook, "
                                    "see documentation/source_metadata/lux_quality_rule_source.md)",
                requires_nonmissing_luxsmed=True, requires_quality_valid=True, requires_adult=False,
                requires_bmi=False, requires_broad_labs=False, requires_fasting_labs=False)
    return mask, meta


def COHORT_3A_ADULT_OF_NONMISSING(master):
    base_mask, _ = COHORT_1_NONMISSING_LUX(master)
    mask = base_mask & (master["RIDAGEYR"] >= 18)
    meta = dict(name="COHORT_3A_ADULT_OF_NONMISSING",
                purpose="Adults (>=18y) among the non-missing-LUXSMED population",
                source_population="COHORT_1_NONMISSING_LUX", inclusion="LUXSMED not null AND RIDAGEYR>=18",
                exclusion="RIDAGEYR<18, among Cohort 1", required_variables="LUXSMED, RIDAGEYR",
                requires_nonmissing_luxsmed=True, requires_quality_valid=False, requires_adult=True,
                requires_bmi=False, requires_broad_labs=False, requires_fasting_labs=False)
    return mask, meta


def COHORT_3B_ADULT_OF_QUALITY_VALID(master):
    base_mask, _ = COHORT_2_QUALITY_VALID(master)
    mask = base_mask & (master["RIDAGEYR"] >= 18)
    meta = dict(name="COHORT_3B_ADULT_OF_QUALITY_VALID",
                purpose="Adults (>=18y) among the NHANES quality-valid (LUAXSTAT==1) population -- "
                        "distinct from COHORT_3A because quality-valid (N=9,023) is not the same population "
                        "as non-missing LUXSMED (N=9,700) (Issue 6)",
                source_population="COHORT_2_QUALITY_VALID", inclusion="LUAXSTAT==1 AND RIDAGEYR>=18",
                exclusion="RIDAGEYR<18, among Cohort 2", required_variables="LUAXSTAT, RIDAGEYR",
                requires_nonmissing_luxsmed=True, requires_quality_valid=True, requires_adult=True,
                requires_bmi=False, requires_broad_labs=False, requires_fasting_labs=False)
    return mask, meta


def COHORT_A_BROAD_LAB(master):
    base_mask, _ = COHORT_1_NONMISSING_LUX(master)
    mask = base_mask & master[CORE_LABS_BROAD].notna().all(axis=1)
    meta = dict(name="COHORT_A_BROAD_LAB",
                purpose="Candidate broad routine-laboratory predictor cohort. Does NOT require BMI or "
                        "demographic completeness (see COHORT_A_PLUS_DEMO_BMI for that stricter nesting).",
                source_population="COHORT_1_NONMISSING_LUX",
                inclusion=f"LUXSMED not null AND all of {CORE_LABS_BROAD} non-missing",
                exclusion="Missing >=1 broad lab, among Cohort 1", required_variables=", ".join(CORE_LABS_BROAD),
                requires_nonmissing_luxsmed=True, requires_quality_valid=False, requires_adult=False,
                requires_bmi=False, requires_broad_labs=True, requires_fasting_labs=False)
    return mask, meta


def COHORT_A_PLUS_DEMO_BMI(master):
    a_mask, _ = COHORT_A_BROAD_LAB(master)
    mask = a_mask & master["RIAGENDR"].notna() & master["BMXBMI"].notna()
    meta = dict(name="COHORT_A_PLUS_DEMO_BMI",
                purpose="Cohort A (broad labs) FURTHER RESTRICTED to complete demographics AND BMI. "
                        "Strictly nested inside Cohort A. In this dataset the entire A-vs-this gap (75 "
                        "participants, verified) is driven by missing BMI; demographics are essentially "
                        "complete within Cohort A. NOT a separate lab-availability concept -- a stricter "
                        "predictor-completeness nesting of Cohort A. Renamed from the ambiguous prior label "
                        "'combined broad cohort' (Issue 2/Closure Phase D).",
                source_population="COHORT_A_BROAD_LAB",
                inclusion="Cohort A AND RIAGENDR not null AND BMXBMI not null",
                exclusion="Missing BMI (or demo), among Cohort A",
                required_variables=", ".join(CORE_LABS_BROAD) + ", RIAGENDR, BMXBMI",
                requires_nonmissing_luxsmed=True, requires_quality_valid=False, requires_adult=False,
                requires_bmi=True, requires_broad_labs=True, requires_fasting_labs=False)
    return mask, meta


def COHORT_FASTING_LABS_ONLY(master):
    base_mask, _ = COHORT_1_NONMISSING_LUX(master)
    mask = base_mask & master[CORE_LABS_FASTING].notna().all(axis=1)
    meta = dict(name="COHORT_FASTING_LABS_ONLY",
                purpose="Participants with the fasting-subsample labs (glucose, triglycerides) present, "
                        "REGARDLESS of broad-lab completeness. This is NOT the same population as "
                        "COHORT_B_FASTING_EXTENDED (which additionally requires the broad labs) -- the two "
                        "were previously conflated under one ambiguous 'fasting cohort' label (Issue 1). "
                        "Renamed from the prior 'fasting labs available (branch)' cohort_flow step.",
                source_population="COHORT_1_NONMISSING_LUX",
                inclusion=f"LUXSMED not null AND all of {CORE_LABS_FASTING} non-missing",
                exclusion="Missing >=1 fasting lab, among Cohort 1", required_variables=", ".join(CORE_LABS_FASTING),
                requires_nonmissing_luxsmed=True, requires_quality_valid=False, requires_adult=False,
                requires_bmi=False, requires_broad_labs=False, requires_fasting_labs=True)
    return mask, meta


def COHORT_B_FASTING_EXTENDED(master):
    a_mask, _ = COHORT_A_BROAD_LAB(master)
    mask = a_mask & master[CORE_LABS_FASTING].notna().all(axis=1)
    meta = dict(name="COHORT_B_FASTING_EXTENDED",
                purpose="THE canonical 'Cohort B': the full fasting-extended candidate predictor cohort -- "
                        "requires BOTH the broad labs (Cohort A) AND the fasting-subsample labs (glucose, "
                        "triglycerides). This is the population usable if the eventual Phase 2 predictor set "
                        "includes fasting glucose/triglycerides. Strict subset of both COHORT_A_BROAD_LAB and "
                        "COHORT_FASTING_LABS_ONLY (asserted in verify_cohort_relationships()).",
                source_population="COHORT_A_BROAD_LAB",
                inclusion=f"Cohort A AND all of {CORE_LABS_FASTING} non-missing",
                exclusion="Missing >=1 broad OR fasting lab, among Cohort 1",
                required_variables=", ".join(CORE_LABS_BROAD + CORE_LABS_FASTING),
                requires_nonmissing_luxsmed=True, requires_quality_valid=False, requires_adult=False,
                requires_bmi=False, requires_broad_labs=True, requires_fasting_labs=True)
    return mask, meta


ALL_COHORTS = [
    COHORT_0_SOURCE, COHORT_1_NONMISSING_LUX, COHORT_2_QUALITY_VALID,
    COHORT_3A_ADULT_OF_NONMISSING, COHORT_3B_ADULT_OF_QUALITY_VALID,
    COHORT_A_BROAD_LAB, COHORT_A_PLUS_DEMO_BMI,
    COHORT_FASTING_LABS_ONLY, COHORT_B_FASTING_EXTENDED,
]


def compute_all(master):
    """Return {cohort_name: (mask, meta, n)} for every canonical cohort."""
    out = {}
    for fn in ALL_COHORTS:
        mask, meta = fn(master)
        out[meta["name"]] = (mask, meta, int(mask.sum()))
    return out


class CohortRelationshipError(AssertionError):
    pass


def verify_cohort_relationships(master):
    """Automated consistency assertions preventing the Issue 1 / Issue 2 discrepancy class from recurring.
    Raises loudly (does not silently pass) if any relationship is violated."""
    c = compute_all(master)

    def subset_of(child, parent):
        cm = c[child][0]
        pm = c[parent][0]
        n_violating = int((cm & ~pm).sum())
        if n_violating != 0:
            raise CohortRelationshipError(
                f"COHORT RELATIONSHIP FAILURE: {child} (N={c[child][2]}) is not a subset of {parent} "
                f"(N={c[parent][2]}) -- {n_violating} participants in {child} are missing from {parent}.")

    subset_of("COHORT_2_QUALITY_VALID", "COHORT_1_NONMISSING_LUX")
    subset_of("COHORT_3A_ADULT_OF_NONMISSING", "COHORT_1_NONMISSING_LUX")
    subset_of("COHORT_3B_ADULT_OF_QUALITY_VALID", "COHORT_2_QUALITY_VALID")
    subset_of("COHORT_A_BROAD_LAB", "COHORT_1_NONMISSING_LUX")
    subset_of("COHORT_A_PLUS_DEMO_BMI", "COHORT_A_BROAD_LAB")
    subset_of("COHORT_FASTING_LABS_ONLY", "COHORT_1_NONMISSING_LUX")
    subset_of("COHORT_B_FASTING_EXTENDED", "COHORT_A_BROAD_LAB")
    subset_of("COHORT_B_FASTING_EXTENDED", "COHORT_FASTING_LABS_ONLY")

    # The exact discrepancy-explaining identity: Cohort B is EXACTLY the intersection of Cohort A and the
    # fasting-only cohort -- if this ever stops being true, the two numbers could silently diverge again.
    b_mask = c["COHORT_B_FASTING_EXTENDED"][0]
    intersection_mask = c["COHORT_A_BROAD_LAB"][0] & c["COHORT_FASTING_LABS_ONLY"][0]
    if not (b_mask == intersection_mask).all():
        raise CohortRelationshipError(
            "COHORT RELATIONSHIP FAILURE: COHORT_B_FASTING_EXTENDED is no longer exactly "
            "(COHORT_A_BROAD_LAB AND COHORT_FASTING_LABS_ONLY) -- re-trace the discrepancy.")

    return c
