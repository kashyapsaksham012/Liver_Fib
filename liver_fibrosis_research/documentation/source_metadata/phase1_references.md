# Phase 1 References

**Generated:** 2026-08-18 (Phase 1 Remediation)

All sources below were consulted directly (fetched and read, not assumed) during this remediation.
LEVEL 1/2 = official CDC/NCHS NHANES documentation. LEVEL 4 = peer-reviewed clinical literature,
used only where NHANES documentation does not define a clinical interpretation, and never
presented as NHANES-official.

---

## LEVEL 1/2 — Official CDC/NCHS NHANES Documentation

### P_LUX (Liver Ultrasound Transient Elastography)
- **Source:** NHANES 2017-March 2020 P_LUX Data Documentation, Codebook, and Frequencies
- **URL:** https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_LUX.htm
- **Date accessed:** 2026-08-18
- **Purpose:** Verify LUXSMED/LUXCAPM/LUXSIQR/LUXSIQRM/LUXCPIQR/LUAXSTAT/LUARXNC/LUARXND/LUARXIN/
  LUANMVGP/LUANMTGP/LUAPNME definitions, official quality-valid exam criteria, target population.
- **Exact claims supported:** LUAXSTAT==1 ("Complete") is officially defined as fasting >=3h, >=10
  complete stiffness measures, and IQRe/median <30%; target population ages 12-150; LUAXSTAT code
  distribution (1=Complete 9,023; 2=Partial 748; 3=Ineligible 386; 4=Not done 252); LUARXNC/LUARXND/
  LUARXIN sub-reason codes.
- **Note:** the URL pattern `wwwn.cdc.gov/Nchs/Nhanes/2017-2020/<FILE>.htm`, present in the prior
  (unremediated) Phase 1 materials, 404s and was never actually verified against a live page. The
  correct, verified pattern is `wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/<FILE>.htm`.

### P_DEMO (Demographics)
- **Source:** NHANES 2017-March 2020 P_DEMO Data Documentation, Codebook, and Frequencies
- **URL:** https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm
- **Date accessed:** 2026-08-18
- **Purpose:** Verify RIDAGEYR/RIAGENDR/RIDRETH1/RIDRETH3/WTINTPRP/WTMECPRP/SDMVPSU/SDMVSTRA
  definitions and category structure.
- **Exact claims supported:** RIDAGEYR topcoded at 80; RIDRETH1 folds Non-Hispanic Asian into
  "Other Race"; RIDRETH3 preserves Non-Hispanic Asian as category 6; WTMECPRP/WTINTPRP ranges and
  meaning; SDMVPSU (values 1-3) / SDMVSTRA (values 149-172, 24 masked strata) for this cycle.

### P_BMX (Body Measures)
- **Source:** NHANES 2017-March 2020 P_BMX Data Documentation, Codebook, and Frequencies
- **URL:** https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.htm
- **Date accessed:** 2026-08-18
- **Purpose:** Verify BMXBMI/BMXWT/BMXHT definitions, BMDSTATS completion-status codes, BMIWT/BMIHT
  comment codes, and whether NHANES defines an implausibility cutoff itself.
- **Exact claims supported:** BMDSTATS 1-4 completion codes; BMIWT/BMIHT comment-code meanings;
  NHANES-documented observed ranges (BMI 11.9-92.3, weight 3.2-254.3kg, height 78.3-199.6cm);
  NHANES's own qualitative-only guidance on "unusual" values (no numeric cutoff defined by NHANES).

### P_BIOPRO, P_CBC, P_GLU, P_TRIGLY, P_HDL (Laboratory files)
- **Source:** NHANES 2017-March 2020 Data Documentation, Codebook, and Frequencies for each component
- **URLs:** https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BIOPRO.htm ,
  .../P_CBC.htm , .../P_GLU.htm , .../P_TRIGLY.htm , .../P_HDL.htm
- **Date accessed:** 2026-08-18
- **Purpose:** Verify all 9 candidate laboratory variable names/units/LLODs; confirm P_GLU/P_TRIGLY
  fasting-subsample eligibility rules and the WTSAFPRP weight variable; check for special missing codes.
- **Exact claims supported:** all 9 variable names (LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB,
  LBXPLTSI, LBXGLU, LBXTR, LBDHDD) confirmed correct as spelled; P_GLU/P_TRIGLY fasting eligibility
  (age 12+, morning session, 8-<24h fast); WTSAFPRP confirmed as the correct 2017-March 2020 fasting
  weight name (=0 for fasting-eligible-but-excluded participants, a documented code, not an error);
  NHANES-documented observed ranges used as plausibility bounds (e.g. ALT 2-682 U/L, AST 6-489 U/L).

### NHANES Weighting Tutorial
- **Source:** NCHS/NHANES Analytic Guidance — "Module 3: Weighting"
- **URL:** https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx
- **Date accessed:** 2026-08-18
- **Purpose:** Determine the official rule for selecting among WTMECPRP/WTINTPRP/WTSAFPRP when an
  analysis mixes MEC-exam and fasting-subsample variables (Error 10).
- **Exact claim supported (direct quote):** "You must use the weight of the smallest subpopulation
  that includes all the variables you want to include in your analysis." NHANES's own worked example
  is triglycerides + MEC data, concluding the fasting subsample weight must be used — directly
  analogous to this project's FibroScan + fasting-glucose/triglycerides scenario.

---

## LEVEL 4 — External Clinical / Peer-Reviewed Literature (NOT NHANES-official; used only for
clinical interpretation where NHANES documentation is silent, per Part 8's instruction)

### VCTE fibrosis-stage cutpoint meta-analysis
- **Source:** Systematic review / meta-analysis of Vibration-Controlled Transient Elastography (VCTE)
  vs. MR Elastography for liver fibrosis staging in NAFLD/MASLD (2024)
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11493355/
- **Date accessed:** 2026-08-18
- **Purpose:** Source candidate (NOT final) kPa cutpoints for significant fibrosis, advanced fibrosis,
  and cirrhosis, for descriptive/feasibility reporting only.
- **Exact claims supported:** Youden-optimal cutoffs reported: significant fibrosis (>=F2) 8.2 kPa;
  advanced fibrosis (>=F3) 9.7 kPa; cirrhosis (F4) 13.6 kPa; advanced-fibrosis AUROC 0.87 (95% CI
  0.84-0.90), sensitivity 0.81, specificity 0.79.

### Editorial on VCTE cutoff heterogeneity
- **Source:** "Towards unification of liver stiffness measurement cutoffs" (editorial)
- **URL:** e-cmh.org (Clinical and Molecular Hepatology)
- **Date accessed:** 2026-08-18
- **Purpose:** Document that no single VCTE cutoff is a universal standard.
- **Exact claim supported:** advanced-fibrosis cutoff varies 6.8-13.6 kPa across studies; ~10 kPa is a
  commonly-used practical "clinically significant advanced chronic liver disease" (cACLD) rule of
  thumb, not a precise histology-matched cutoff.

### NHANES 2017-March 2020-specific fibrosis prevalence study
- **Source:** Luo N, Zhang X, Huang J, Chen H, Tang H. "Prevalence of steatotic liver disease and
  associated fibrosis in the United States: Results from NHANES 2017-March 2020." *Journal of
  Hepatology* (2024).
- **URL:** https://www.journal-of-hepatology.eu/article/S0168-8278(23)05072-9/fulltext (fulltext
  access returned 403 during this remediation; only abstract-level CAP/steatosis cutoffs, not the
  exact fibrosis-kPa cutoff used, could be independently confirmed)
- **Date accessed:** 2026-08-18
- **Purpose:** Identify a study using this exact NHANES release for VCTE-based fibrosis prevalence.
- **Status:** cited for completeness; its precise fibrosis threshold choice is UNCONFIRMED by this
  remediation and should be fulltext-verified in Phase 2 before being relied upon.

### General clinical chemistry / hematology reference intervals
- **Source:** General clinical chemistry reference literature (used for `LAB_REFERENCE_RANGES` in
  `src/_common.py`, laboratory plausibility flagging only — NOT a disease threshold)
- **Date accessed:** 2026-08-18
- **Purpose:** Provide an external comparison band for the laboratory plausibility audit
  (`laboratory_plausibility_audit.csv`). NHANES's own observed ranges for this release (documented
  above) were treated as the more defensible bound for this sampled population, per the official
  P_BMX guidance that unusual-but-real values are expected in a general population sample.
- **Note:** platelet reference range and the P_HDL assay-generation-by-cycle mapping were NOT
  independently re-verified against a primary clinical source during this remediation; flagged as an
  open item for Phase 2 if platelet/HDL comparability across cycles becomes analytically relevant.
