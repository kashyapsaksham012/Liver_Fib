"""
_common.py
Shared utilities for the Phase 1 remediation pipeline. Single source of truth for:
  - safe XPT loading with SAS special-missing sentinel correction (see SENTINEL below)
  - cohort-flow arithmetic assertions (before - excluded = after, fails loudly)
  - verified variable metadata (source: official NHANES 2017-March 2020 codebooks,
    see documentation/source_metadata/phase1_references.md for exact URLs)
  - laboratory clinical reference ranges used only for plausibility flagging
  - candidate outcome cutpoints (labeled candidate/provisional throughout)

Not a script — imported by 01..18.
"""

import sys
import datetime
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "NHANES_2017_2020"
INT_DIR = ROOT / "data" / "interim"
AUDIT_DIR = ROOT / "documentation" / "audit_reports"
DICT_DIR = ROOT / "documentation" / "data_dictionary"
META_DIR = ROOT / "documentation" / "source_metadata"
FIG_DIR = ROOT / "results" / "figures"
TAB_DIR = ROOT / "results" / "tables"
for d in (AUDIT_DIR, DICT_DIR, META_DIR, FIG_DIR, TAB_DIR, INT_DIR):
    d.mkdir(parents=True, exist_ok=True)

NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

REQUIRED_FILES = [
    "P_LUX.xpt", "P_DEMO.xpt", "P_BMX.xpt", "P_BIOPRO.xpt",
    "P_CBC.xpt", "P_GLU.xpt", "P_TRIGLY.xpt", "P_HDL.xpt"
]

# ──────────────────────────────────────────────────────────────────────────
# SAS SPECIAL-MISSING SENTINEL FIX
#
# pandas.read_sas(..., format="xport") correctly converts the plain SAS
# numeric missing value "." to NaN, but does NOT convert SAS's *extended*
# special-missing codes (.A-.Z, ._). Those leak through as the literal
# denormalized IEEE-754 double 5.397605346934028e-79 (confirmed empirically
# against the raw 2017-March 2020 XPT files on 2026-08-18: found in
# P_LUX.LUXSIQR/LUXSIQRM/LUXCPIQR/LUANMVGP/LUANMTGP, P_DEMO.RIDAGEYR/
# RIDAGEMN/WTMECPRP/INDFMPIR, P_BIOPRO.LBDSATLC/LBDSGTLC/LBDSTBLC,
# P_CBC.LBXEOPCT/LBDEONO/LBDBANO/LBXNRBC, P_GLU.WTSAFPRP, P_TRIGLY.WTSAFPRP
# -- 43,311 cells across 18 (file, column) pairs in the full raw releases).
# Undetected, this silently corrupts min/mean/percentile statistics and
# UNDER-COUNTS missingness (pandas .isna() does not flag it) wherever it
# survives. See documentation/audit_reports/special_missing_code_audit.csv
# for the full scan and documentation/audit_reports/transformation_log.md
# for the exact rows affected inside the analytical (P_LUX-anchored) cohort.
SENTINEL = 5.397605346934028e-79
SENTINEL_BAND = (1e-80, 1e-70)  # generous band around the exact float to catch any bit-noise


def _fix_sentinel(df, source_name, log_rows):
    """Recode the SAS special-missing sentinel to NaN in every numeric column. Returns count fixed."""
    n_fixed_total = 0
    for col in df.columns:
        s = df[col]
        if not pd.api.types.is_numeric_dtype(s):
            continue
        mask = (s.abs() > SENTINEL_BAND[0]) & (s.abs() < SENTINEL_BAND[1])
        n = int(mask.sum())
        if n > 0:
            df.loc[mask, col] = pd.NA if pd.api.types.is_extension_array_dtype(s) else float("nan")
            n_fixed_total += n
            log_rows.append({
                "source_file": source_name, "variable": col,
                "n_sentinel_recoded_to_nan": n, "sentinel_value": SENTINEL,
                "timestamp": NOW
            })
    return n_fixed_total


_SENTINEL_LOG = []  # module-level accumulator; callers can read via get_sentinel_log()


def load_xpt(name, raw_dir=None):
    """Load one NHANES XPT file, fix SEQN dtype, and recode the SAS special-missing sentinel."""
    raw_dir = raw_dir or RAW_DIR
    path = raw_dir / name
    df = pd.read_sas(path, format="xport", encoding="utf-8")
    _fix_sentinel(df, name, _SENTINEL_LOG)
    if "SEQN" in df.columns:
        df["SEQN"] = pd.to_numeric(df["SEQN"], errors="coerce").astype("Int64")
    return df


def get_sentinel_log():
    return pd.DataFrame(_SENTINEL_LOG) if _SENTINEL_LOG else pd.DataFrame(
        columns=["source_file", "variable", "n_sentinel_recoded_to_nan", "sentinel_value", "timestamp"])


# ──────────────────────────────────────────────────────────────────────────
# COHORT-FLOW ARITHMETIC ASSERTION (Error 1 / Error 14 / TEST 7)
class CohortFlowError(AssertionError):
    pass


def assert_flow(n_before, n_excluded, n_after, step_label):
    """Fail loudly (raise) unless n_before - n_excluded == n_after. No silent patching."""
    if n_before - n_excluded != n_after:
        raise CohortFlowError(
            f"COHORT-FLOW ARITHMETIC FAILURE at step '{step_label}': "
            f"N_before({n_before}) - N_excluded({n_excluded}) = {n_before - n_excluded} "
            f"!= N_after({n_after}). Pipeline halted; fix the underlying computation."
        )
    return True


# ──────────────────────────────────────────────────────────────────────────
# VERIFIED VARIABLE METADATA — single source of truth
# (used by the master dictionary, the report, and variable_source_verification.csv)
# doc_url uses the verified live NHANES pattern:
#   https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/<FILE>.htm
# (the pattern https://wwwn.cdc.gov/Nchs/Nhanes/2017-2020/<FILE>.htm used in the
#  prior Phase 1 draft 404s and was never actually verified against a live source).
_DOC = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/{}.htm"

VAR_METADATA = {
    "SEQN": dict(desc="Respondent sequence number", src="P_DEMO.xpt (primary)", unit="-",
                 role="id_key", official=True, notes="Unique participant identifier; merge key.",
                 doc_url=_DOC.format("P_DEMO"), quality_restriction=None),

    # ---- P_LUX: outcome + quality ----
    "LUXSMED": dict(desc="Median liver stiffness (E), transient elastography", src="P_LUX.xpt", unit="kPa",
                    role="candidate_outcome", official=True,
                    notes="Non-missing whenever an attempt produced a numeric median, regardless of exam "
                          "completeness (LUAXSTAT). See LUAXSTAT for the official quality-valid flag; "
                          "do not treat non-missing LUXSMED alone as a quality-valid measurement.",
                    doc_url=_DOC.format("P_LUX"), quality_restriction="Use jointly with LUAXSTAT==1 for a quality-valid subset.",
                    observed_range_source="P_LUX.xpt (own data)"),
    "LUXCAPM": dict(desc="Median Controlled Attenuation Parameter (CAP)", src="P_LUX.xpt", unit="dB/m",
                    role="candidate_outcome", official=True,
                    notes="Candidate steatosis outcome; same quality caveat as LUXSMED applies (pair with LUAXSTAT).",
                    doc_url=_DOC.format("P_LUX"), quality_restriction="Use jointly with LUAXSTAT==1."),
    "LUXSIQR": dict(desc="Interquartile range of stiffness measures (IQRe)", src="P_LUX.xpt", unit="kPa",
                    role="quality", official=True,
                    notes="27 rows in the raw file carried the unconverted SAS special-missing sentinel; "
                          "corrected to NaN by this pipeline (see special_missing_code_audit.csv).",
                    doc_url=_DOC.format("P_LUX"), quality_restriction=None),
    "LUXSIQRM": dict(desc="Ratio of stiffness IQR to median E (IQRe/Med)", src="P_LUX.xpt", unit="%",
                     role="quality", official=True,
                     notes="This is the exact variable NHANES uses (<30%) as one of the three official "
                           "components of LUAXSTAT==1 ('Complete'). 12 rows carried the sentinel artifact; corrected.",
                     doc_url=_DOC.format("P_LUX"), quality_restriction="NHANES 'Complete' requires IQRe/Med < 30%."),
    "LUXCPIQR": dict(desc="Interquartile range of CAP measures", src="P_LUX.xpt", unit="dB/m",
                     role="quality", official=True,
                     notes="80 rows carried the sentinel artifact; corrected to NaN by this pipeline.",
                     doc_url=_DOC.format("P_LUX"), quality_restriction=None),
    "LUAXSTAT": dict(desc="Elastography exam status", src="P_LUX.xpt", unit="categorical(1-4)",
                     role="quality", official=True,
                     notes="OFFICIAL NHANES DEFINITION (verified from live codebook 2026-08-18): "
                           "1=Complete [fasting >=3h, >=10 complete stiffness measures, IQRe/Med <30%], "
                           "2=Partial, 3=Ineligible, 4=Not done. LUAXSTAT==1 IS the NHANES-sanctioned "
                           "quality-valid-exam definition; it is not a threshold this project invented.",
                     doc_url=_DOC.format("P_LUX"), quality_restriction="Use LUAXSTAT==1 to define 'NHANES quality-valid exam'."),
    "LUARXNC": dict(desc="Reason exam partial", src="P_LUX.xpt", unit="categorical",
                    role="quality", official=True,
                    notes="1=Fasting <3h, 2=Unable to obtain >=10 valid measures, 3=IQRe/Med >30%.",
                    doc_url=_DOC.format("P_LUX"), quality_restriction=None),
    "LUARXND": dict(desc="Reason exam not done", src="P_LUX.xpt", unit="categorical",
                    role="quality", official=True, notes="1=Refusal, 2=Limited time, 3=Other.",
                    doc_url=_DOC.format("P_LUX"), quality_restriction=None),
    "LUARXIN": dict(desc="Reason ineligible", src="P_LUX.xpt", unit="categorical",
                    role="quality", official=True, notes="1=Pregnant/could not test, 2=Other (e.g., implant/insulin pump).",
                    doc_url=_DOC.format("P_LUX"), quality_restriction=None),
    "LUANMVGP": dict(desc="Number of complete stiffness measures, final probe", src="P_LUX.xpt", unit="count",
                     role="quality", official=True,
                     notes="Directly relevant to the '>=10 valid measures' component of LUAXSTAT==1; "
                           "not previously ingested by the pipeline. 2 rows carried the sentinel artifact.",
                     doc_url=_DOC.format("P_LUX"), quality_restriction=None),
    "LUANMTGP": dict(desc="Number of stiffness measures attempted, final probe", src="P_LUX.xpt", unit="count",
                     role="quality", official=True,
                     notes="Not previously ingested by the pipeline. 671 rows carried the sentinel artifact "
                           "(this column is mostly populated only when an exam was attempted).",
                     doc_url=_DOC.format("P_LUX"), quality_restriction=None),

    # ---- P_DEMO: demographics, weights, design ----
    "RIDAGEYR": dict(desc="Age at screening (years)", src="P_DEMO.xpt", unit="years",
                     role="demographic", official=True,
                     notes="Topcoded at 80 (participants 80+ recorded as 80). Not affected by the sentinel "
                           "bug within the P_LUX-anchored cohort (verified: 0 sentinel rows among N=10,409).",
                     doc_url=_DOC.format("P_DEMO"), quality_restriction="Topcoded at 80y."),
    "RIAGENDR": dict(desc="Gender", src="P_DEMO.xpt", unit="categorical(1=Male,2=Female)",
                     role="demographic", official=True, notes="No special missing codes documented.",
                     doc_url=_DOC.format("P_DEMO"), quality_restriction=None),
    "RIDRETH1": dict(desc="Race/Hispanic origin (5 categories)", src="P_DEMO.xpt", unit="categorical",
                     role="demographic", official=True,
                     notes="1=Mexican American,2=Other Hispanic,3=NH White,4=NH Black,5=Other/Multi-racial. "
                          "Non-Hispanic Asian participants are folded into category 5 and are NOT separately "
                          "identifiable in this variable. See documentation/audit_reports/race_ethnicity_verification.md.",
                     doc_url=_DOC.format("P_DEMO"), quality_restriction=None),
    "RIDRETH3": dict(desc="Race/Hispanic origin (6 categories, incl. NH Asian)", src="P_DEMO.xpt", unit="categorical",
                     role="demographic", official=True,
                     notes="1=Mexican American,2=Other Hispanic,3=NH White,4=NH Black,6=NH Asian,7=Other/Multi-racial. "
                          "Preserves Non-Hispanic Asian (n=1,638 in full P_DEMO) as a distinct category. "
                          "RECOMMENDED primary race/ethnicity variable for the Phase 2 fairness analysis "
                          "(see race_ethnicity_verification.md for full justification) -- decision documented "
                          "here, not silently made; both variables are retained.",
                     doc_url=_DOC.format("P_DEMO"), quality_restriction=None),
    "WTMECPRP": dict(desc="Full-sample 2-cycle MEC exam weight", src="P_DEMO.xpt", unit="weight",
                     role="survey_weight", official=True,
                     notes="Applies to the pre-pandemic 2017-March 2020 combined MEC-examined sample. "
                           "0 for interview-only (non-MEC) respondents in the full P_DEMO file; not an issue "
                           "for our P_LUX-anchored cohort (all rows have a valid MEC exam by construction).",
                     doc_url=_DOC.format("P_DEMO"), quality_restriction="NOT yet applied to any analysis in Phase 1 (deferred)."),
    "WTINTPRP": dict(desc="Full-sample 2-cycle interview weight", src="P_DEMO.xpt", unit="weight",
                     role="survey_weight", official=True, notes="Use only for interview-only variables.",
                     doc_url=_DOC.format("P_DEMO"), quality_restriction="NOT yet applied to any analysis in Phase 1 (deferred)."),
    "WTSAFPRP": dict(desc="Fasting subsample weight (2-cycle)", src="P_GLU.xpt / P_TRIGLY.xpt", unit="weight",
                     role="survey_weight", official=True,
                     notes="Confirmed correct variable name for the 2017-March 2020 pre-pandemic release "
                          "(naming diverges from single-cycle WTSAF2YR convention used in 2011-2016 releases). "
                          "Set to 0 for fasting-eligible participants who gave no specimen or did not meet the "
                          "8-24h fasting window -- 0 is a documented, meaningful code, not a data error.",
                     doc_url=_DOC.format("P_GLU"), quality_restriction="NOT yet applied to any analysis in Phase 1 (deferred)."),
    "SDMVPSU": dict(desc="Masked variance pseudo-PSU", src="P_DEMO.xpt", unit="-",
                    role="survey_design", official=True, notes="Values 1-3; used for Taylor-series variance estimation.",
                    doc_url=_DOC.format("P_DEMO"), quality_restriction=None),
    "SDMVSTRA": dict(desc="Masked variance pseudo-stratum", src="P_DEMO.xpt", unit="-",
                     role="survey_design", official=True, notes="Values 149-172 (24 masked strata this cycle).",
                     doc_url=_DOC.format("P_DEMO"), quality_restriction=None),

    # ---- P_BMX ----
    "BMXBMI": dict(desc="Body Mass Index", src="P_BMX.xpt", unit="kg/m^2",
                  role="candidate_predictor", official=True,
                  notes="NHANES-documented observed range 11.9-92.3 (ages 2-150 target pop). NHANES does not "
                        "define an implausibility cutoff itself ('unusual values ... typically extremely short, "
                        "tall, over/underweight' -- qualitative note only); any numeric plausibility bound used "
                        "here is an external convention, documented as such.",
                  doc_url=_DOC.format("P_BMX"), quality_restriction=None),
    "BMXWT": dict(desc="Weight", src="P_BMX.xpt", unit="kg", role="candidate_predictor", official=True,
                 notes="NHANES-documented observed range 3.2-254.3 kg.", doc_url=_DOC.format("P_BMX"), quality_restriction=None),
    "BMXHT": dict(desc="Standing height", src="P_BMX.xpt", unit="cm", role="candidate_predictor", official=True,
                 notes="NHANES-documented observed range 78.3-199.6 cm; not collected for participants measured recumbent only.",
                 doc_url=_DOC.format("P_BMX"), quality_restriction=None),
    "BMDSTATS": dict(desc="Body Measures component status code", src="P_BMX.xpt", unit="categorical(1-4)",
                     role="quality", official=True,
                     notes="1=Complete data for age group, 2=Partial (height/weight only), 3=Other partial, "
                          "4=No body measures data. The official BMX completeness flag; not previously used "
                          "by this pipeline to qualify BMXBMI/BMXWT/BMXHT completeness.",
                     doc_url=_DOC.format("P_BMX"), quality_restriction="Use to distinguish complete vs partial anthropometry."),
    "BMIWT": dict(desc="Weight comment code", src="P_BMX.xpt", unit="categorical",
                 role="quality", official=True, notes="1=Could not obtain, 3=Clothing, 4=Medical appliance.",
                 doc_url=_DOC.format("P_BMX"), quality_restriction=None),
    "BMIHT": dict(desc="Standing height comment code", src="P_BMX.xpt", unit="categorical",
                 role="quality", official=True, notes="1=Could not obtain, 3=Not straight.",
                 doc_url=_DOC.format("P_BMX"), quality_restriction=None),

    # ---- Laboratory files ----
    "LBXSATSI": dict(desc="Alanine Aminotransferase (ALT)", src="P_BIOPRO.xpt", unit="U/L",
                     role="candidate_predictor", official=True,
                     notes="LLOD=3 U/L. NHANES-observed range in this release: 2-682 U/L.",
                     doc_url=_DOC.format("P_BIOPRO"), quality_restriction=None),
    "LBXSASSI": dict(desc="Aspartate Aminotransferase (AST)", src="P_BIOPRO.xpt", unit="U/L",
                     role="candidate_predictor", official=True,
                     notes="LLOD=3 U/L. NHANES-observed range: 6-489 U/L.",
                     doc_url=_DOC.format("P_BIOPRO"), quality_restriction=None),
    "LBXSAL": dict(desc="Albumin, refrigerated serum", src="P_BIOPRO.xpt", unit="g/dL",
                   role="candidate_predictor", official=True, notes="LLOD=0.3 g/dL. NHANES-observed range: 2.1-5.4 g/dL.",
                   doc_url=_DOC.format("P_BIOPRO"), quality_restriction=None),
    "LBXSAPSI": dict(desc="Alkaline Phosphatase (ALP)", src="P_BIOPRO.xpt", unit="IU/L",
                     role="candidate_predictor", official=True, notes="LLOD=2 IU/L. NHANES-observed range: 16-638 IU/L.",
                     doc_url=_DOC.format("P_BIOPRO"), quality_restriction=None),
    "LBXSTB": dict(desc="Total Bilirubin", src="P_BIOPRO.xpt", unit="mg/dL",
                   role="candidate_predictor", official=True, notes="LLOD=0.1 mg/dL. NHANES-observed range: 0.1-3.8 mg/dL.",
                   doc_url=_DOC.format("P_BIOPRO"), quality_restriction=None),
    "LBXSGL": dict(desc="Glucose, serum (non-fasting, full biochemistry sample)", src="P_BIOPRO.xpt", unit="mg/dL",
                   role="candidate_predictor_broad", official=True,
                   notes="Available on the broad MEC biochemistry sample WITHOUT the fasting-subsample "
                         "restriction that applies to LBXGLU (P_GLU). Not used by the prior pipeline; "
                         "flagged here as a candidate broad-cohort alternative to fasting glucose for Phase 2 "
                         "to consider -- decision deferred, not made here.",
                   doc_url=_DOC.format("P_BIOPRO"), quality_restriction="Non-fasting; distinct from LBXGLU."),
    "LBXPLTSI": dict(desc="Platelet count", src="P_CBC.xpt", unit="1000 cells/uL",
                     role="candidate_predictor", official=True, notes="NHANES-observed range: 8-1021 (10^9/L).",
                     doc_url=_DOC.format("P_CBC"), quality_restriction=None),
    "LBXGLU": dict(desc="Fasting Glucose", src="P_GLU.xpt", unit="mg/dL",
                   role="candidate_predictor_fasting", official=True,
                   notes="FASTING-SUBSAMPLE ONLY: morning-session MEC examinees who fasted 8-<24h. "
                         "NHANES-observed range: 47-524 mg/dL.",
                   doc_url=_DOC.format("P_GLU"), quality_restriction="Fasting subsample only; pair with WTSAFPRP."),
    "LBXTR": dict(desc="Triglycerides", src="P_TRIGLY.xpt", unit="mg/dL",
                  role="candidate_predictor_fasting", official=True,
                  notes="FASTING-SUBSAMPLE ONLY (same morning-fasting subsample as LBXGLU). "
                        "NHANES-observed range: 10-2684 mg/dL.",
                  doc_url=_DOC.format("P_TRIGLY"), quality_restriction="Fasting subsample only; pair with WTSAFPRP."),
    "LBDHDD": dict(desc="Direct HDL-Cholesterol", src="P_HDL.xpt", unit="mg/dL",
                   role="candidate_predictor", official=True,
                   notes="LLOD=3 mg/dL. NOT fasting-restricted (available on the broader MEC sample). "
                         "NHANES-observed range: 5-189 mg/dL.",
                   doc_url=_DOC.format("P_HDL"), quality_restriction=None),
}

# ──────────────────────────────────────────────────────────────────────────
# Laboratory plausibility reference ranges (Error 4) — EXTERNAL CLINICAL
# REFERENCE, not an NHANES-defined rule and not a disease threshold.
# Used only to FLAG values for review; never to silently delete anything.
LAB_REFERENCE_RANGES = {
    # var: (clinically-typical low, clinically-typical high, unit, source)
    "LBXSATSI": (7, 56, "U/L", "General clinical chemistry reference interval (adult); NHANES-observed range 2-682 U/L is the more defensible outlier bound for this sampled population."),
    "LBXSASSI": (10, 40, "U/L", "General clinical chemistry reference interval (adult); NHANES-observed range 6-489 U/L."),
    "LBXSAL":   (3.4, 5.0, "g/dL", "General clinical chemistry reference interval (adult); NHANES-observed range 2.1-5.4 g/dL."),
    "LBXSAPSI": (25, 100, "IU/L", "General clinical chemistry reference interval (adult); NHANES-observed range 16-638 IU/L."),
    "LBXSTB":   (0.2, 1.2, "mg/dL", "General clinical chemistry reference interval (adult); NHANES-observed range 0.1-3.8 mg/dL."),
    "LBXPLTSI": (150, 450, "10^9/L", "Standard hematology reference interval (adult); NHANES-observed range 8-1021."),
    "LBXGLU":   (70, 99, "mg/dL", "Normal FASTING glucose reference interval (ADA); values 100-125 = prediabetes range, >=126 = diabetes range -- clinically plausible, not implausible, and must NOT be flagged as an error."),
    "LBXTR":    (0, 150, "mg/dL", "Normal fasting triglyceride reference interval (NCEP ATP III); values above reflect real hypertriglyceridemia, not error, up to extreme biological outliers."),
    "LBDHDD":   (40, 60, "mg/dL", "General adult HDL reference interval (sex-specific cutpoints of >40 men/>50 women simplified to a symmetric flag band here); NHANES-observed range 5-189 mg/dL."),
}

# ──────────────────────────────────────────────────────────────────────────
# CANDIDATE OUTCOME CUTPOINTS (Part 8) — EXTERNAL CLINICAL LITERATURE,
# explicitly NOT an NHANES-defined rule, NOT finalized, NOT to be chosen by
# ML performance. See documentation/source_metadata/phase1_references.md.
CANDIDATE_THRESHOLDS = [
    dict(kpa=7.0, label="General cutoff (literature range, low end)", citation="literature range, non-specific"),
    dict(kpa=7.5, label="General cutoff (literature range)", citation="literature range, non-specific"),
    dict(kpa=8.0, label="Candidate: significant fibrosis (>=F2), lower literature estimate", citation="Multiple NAFLD/MASLD VCTE studies; see phase1_references.md"),
    dict(kpa=8.2, label="Candidate: significant fibrosis (>=F2), meta-analytic Youden-optimal cutoff", citation="VCTE-vs-MRE meta-analysis, PMC11493355 (2024)"),
    dict(kpa=9.0, label="General cutoff (literature range)", citation="literature range, non-specific"),
    dict(kpa=9.7, label="Candidate: advanced fibrosis (>=F3), meta-analytic Youden-optimal cutoff", citation="VCTE-vs-MRE meta-analysis, PMC11493355 (2024)"),
    dict(kpa=10.0, label="Candidate: advanced fibrosis (>=F3) / cACLD rule-of-thumb, commonly-cited round number", citation="Widely used practical rule-of-thumb; literature range for advanced fibrosis spans 6.8-13.6 kPa (e-cmh.org editorial)"),
    dict(kpa=12.0, label="Candidate: cirrhosis (F4), commonly-cited round number", citation="Widely used practical rule-of-thumb"),
    dict(kpa=13.6, label="Candidate: cirrhosis (F4), meta-analytic Youden-optimal cutoff", citation="VCTE-vs-MRE meta-analysis, PMC11493355 (2024)"),
]

RACE_MAP_RIDRETH1 = {1.0: "Mexican American", 2.0: "Other Hispanic", 3.0: "Non-Hispanic White",
                     4.0: "Non-Hispanic Black", 5.0: "Other Race / Multi-Racial"}
RACE_MAP_RIDRETH3 = {1.0: "Mexican American", 2.0: "Other Hispanic", 3.0: "Non-Hispanic White",
                     4.0: "Non-Hispanic Black", 6.0: "Non-Hispanic Asian", 7.0: "Other Race / Multi-Racial"}
SEX_MAP = {1.0: "Male", 2.0: "Female"}

CORE_LABS_BROAD = ["LBXSATSI", "LBXSASSI", "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD"]
CORE_LABS_FASTING = ["LBXGLU", "LBXTR"]


def read_csv_safe(path):
    return pd.read_csv(path) if Path(path).exists() else pd.DataFrame()


def fail(msg):
    print(f"CRITICAL STOP CONDITION: {msg}")
    sys.exit(1)
