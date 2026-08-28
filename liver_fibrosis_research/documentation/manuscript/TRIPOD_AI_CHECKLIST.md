# TRIPOD+AI checklist — Track 2.4

**Date:** 2026-08-27. Item-by-item mapping of the manuscript to the TRIPOD+AI 2024 reporting
checklist (Collins et al., *BMJ* 2024;385:e078378, ref [9]). This is a working map; before
submission, transcribe the "where addressed" column onto the **official TRIPOD+AI checklist PDF**
(equator-network.org) with final page numbers, and have a co-author confirm each.

Study type for TRIPOD+AI purposes: **model development with internal validation only** (no
external validation — declared). Section numbers refer to `MANUSCRIPT_DRAFT.md` v4+.

| # | Item (abbreviated) | Where addressed | Status |
|---|---|---|---|
| **Title & abstract** | | | |
| 1 | Title identifies study as developing/validating a prediction model, the target population, and the outcome | Title | ✅ |
| 2 | Structured abstract: objectives, data, methods, results, conclusions; states model type and that it is an audit not a deployable model | Structured abstract | ✅ |
| **Introduction** | | | |
| 3a | Background: rationale, existing models, why this study | §1 ¶1–3 (with refs [1,2,4–8,10–13,15–17,21,23]) | ✅ |
| 3b | Objectives / research question | §1 final ¶ | ✅ |
| **Methods — source of data** | | | |
| 4a | Study design / data source | §2.1 (NHANES 2017–March 2020 combined release; cross-sectional survey) | ✅ |
| 4b | Dates of participant recruitment, follow-up, outcome | §2.1 (2017–March 2020 pre-pandemic release); cross-sectional, no follow-up | ✅ |
| **Methods — participants** | | | |
| 5a | Eligibility criteria; setting | §2.1 (VCTE attempted + valid exam + adult + complete predictors; cohort flow 10,409→7,153) | ✅ |
| 5b | Details of treatments/interventions received | n/a (observational, no intervention) | ✅ n/a |
| 5c | Data pre-processing (incl. handling of images/text/AI-specific inputs) | §2.3–2.4 (10 tabular predictors; median-impute no-op; StandardScaler for LR/MLP), §2.12 | ✅ |
| **Methods — outcome** | | | |
| 6a | Outcome definition, how/when measured; **frozen before modelling** | §2.2 (`LUXSMED ≥ 8.2 kPa`; Youden-optimal from 2024 VCTE-vs-MRE meta-analysis; fixed pre-training) | ✅ |
| 6b | Outcome assessment blinded to predictors? | §2.2 — VCTE is instrument-measured, independent of the model inputs; state explicitly | ⚠️ add one sentence |
| **Methods — predictors** | | | |
| 7a | Predictor definitions, how/when measured; **frozen**; prediction horizon | §2.3 (ten routine variables; prediction time = pre-elastography; frozen); race/ethnicity excluded from input by design | ✅ |
| 7b | Predictor assessment blinded to outcome? | §2.3 / §2.4 — labs measured independently of VCTE; state explicitly | ⚠️ add one sentence |
| **Methods — sample size** | | | |
| 8 | How sample size was determined; events-per-variable | §2.4 (466 training positives; 200 test); Limitation B1 (§5) | ✅ (no formal a-priori calculation — state that) |
| **Methods — missing data** | | | |
| 9 | How missing data handled (development and validation) | §2.1 (complete-case by construction), §2.9 (targeted multiple imputation for the NHB selection question); Limitations F1–F3, D4 | ✅ |
| **Methods — analytical methods** | | | |
| 10 | Model-building: algorithms, predictor selection, internal validation resampling | §2.4 (5 families; 5-fold CV within training; single locked 70/30 split), §2.7/§2.7b (80/20 proper-train/calibration sub-split) | ✅ |
| 11 | Model output (probability / class / set) and how it maps to a decision | §2.4 (probabilities; Youden threshold), §2.5 (recalibration), §2.7 (conformal prediction sets) | ✅ |
| 12a | How AI-specific choices were made: hyperparameter tuning, architecture | §2.4 (5-fold CV grid/random search within training; frozen `best_params`) | ✅ |
| 12b | Handling of class imbalance | §2.4 (`class_weight='balanced'` / `scale_pos_weight`; MLP unweighted, Amendment #3 sensitivity); §3.3 (the calibration consequence) | ✅ |
| **Methods — model performance & evaluation** | | | |
| 13a | Performance measures (discrimination, calibration), with rationale | §2.5, §2.11, §3.2–3.3 (AUROC, PR-AUC; calibration-in-the-large, ECE, Brier) | ✅ |
| 13b | Model performance **by subgroup** (fairness) | §2.6, §3.4, §3.4b, §3.4c, §3.8; §2.7/§3.5–3.6 (subgroup conformal coverage) | ✅ |
| 13c | Uncertainty quantification of predictions | §2.7, §3.5–3.6 (split conformal; marginal + subgroup + intersectional coverage) | ✅ |
| **Methods — model updating** | | | |
| 14 | Any model updating from validation results | §2.5 (out-of-fold Platt recalibration — the only "update", pre-registered); no post-hoc model updating | ✅ |
| **Methods — fairness / equity** | | | |
| 15a | Definition of fairness used; protected attributes; rationale | §2.6 (sex, race/ethnicity, age band, BMI band; subgroup sensitivity difference from a reference); §4.1 | ✅ |
| 15b | Whether/how the model may affect health equity; underserved groups | §3.4, §4, §5 (D1, D4); §3.11 (DCA subgroup net benefit, exploratory) | ✅ |
| 15c | Mitigation of identified bias | §2.8, §3.7, §3.7b, Table 4 (post-hoc battery + selective deferral + training-time reweighting) | ✅ |
| **Methods — risk of bias / other** | | | |
| 16 | Multiplicity / multiple testing | §2.11 (within-family BH-FDR; project-wide 182-test pooled correction) | ✅ |
| **Results — participants** | | | |
| 17a | Flow of participants (cohort flow diagram) | §2.1 (10,409→9,700→9,023→7,768→7,153); Table 1 | ⚠️ add a flow **figure** (currently prose only) |
| 17b | Baseline characteristics incl. by outcome and by key subgroup | Table 1 (by fibrosis status and BMI band) | ✅ |
| 17c | Number of outcome events | §3.1 (666 positives, 9.31%); Table 1 | ✅ |
| **Results — model** | | | |
| 18 | Full model specification (or where to obtain it) + code availability | §2.12; Appendix B; `documentation/final_audit/REPRODUCIBILITY.md`; model lineage CSVs | ⚠️ add explicit "code and frozen artefacts available at <repo/DOI>" statement |
| 19a | Model performance: discrimination + calibration with CIs | §3.2–3.3, Table 2, Figures 1–2 | ✅ |
| 19b | Model performance by subgroup, with CIs | §3.4–3.6, §3.8, Table 3, Figures 3–4; §3.4b, §3.4c | ✅ |
| 19c | Model outputs for representative cases / decision-curve analysis | §3.11 (DCA, exploratory), Figure 5 | ✅ (labelled exploratory) |
| **Results — model updating** | | | |
| 20 | Results of any model updating | §3.3 (recalibration effect); §3.10 (recalibration does not transport to secondary outcomes) | ✅ |
| **Discussion** | | | |
| 21 | Interpretation, in context of objectives and prior evidence | §4, §4.1 | ✅ |
| 22 | Limitations (data, methods, **fairness**, generalisability) | §5 (indexed to `FINAL_LIMITATIONS_REGISTER.md`; every mandated ID present) | ✅ |
| 23 | Clinical implications / intended use / what is NOT claimed | §4 (methodological contribution, not a deployable model), §6, Appendix A "Claims explicitly not made" | ✅ |
| **Other information** | | | |
| 24 | Supplementary information / where the protocol, code, data are | §2.12; Appendix A/B; needs a consolidated "Data and code availability" paragraph | ⚠️ add the paragraph (see `SUBMISSION_CHECKLIST.md`) |
| 25 | Funding | Appendix B placeholder → **author to complete** (state: no funding / independent researcher) | ❌ GAP |
| 26 | Conflicts of interest | Appendix B placeholder → **author to complete** (state: none) | ❌ GAP |
| 27a | Protocol / pre-registration and where to access | §2.11–2.12; `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`, `documentation/end_to_end/protocol_amendment_registry.md` (20 amendments) — add a sentence pointing to these | ⚠️ add a "the analysis protocol was frozen before modelling; amendments are logged in <ref>" sentence |
| 27b | Ethical approval / participant consent | NHANES is public de-identified data; NCHS Research Ethics Review Board approval + participant consent are documented by NCHS — **author to add one sentence** | ❌ GAP |

---

## Summary of gaps to close before submission

**Add (small, author writes):**
- §2.2 / §2.3 — one sentence each on outcome/predictor measurement being mutually blind (6b, 7b).
- §2.8 — one sentence that sample size was not formally pre-calculated (8).
- Funding statement: "This research received no specific grant… The author is an independent
  researcher." (25)
- Conflicts: "The author declares no competing interests." (26)
- Ethics: "This analysis used the publicly available, de-identified NHANES 2017–March 2020 data;
  the NHANES protocol was approved by the NCHS Research Ethics Review Board and all participants
  provided written informed consent. No additional ethical approval was required for this
  secondary analysis." (27b)
- Protocol sentence pointing to `PHASE2_PROTOCOL_FREEZE.md` + the amendment registry (27a).
- "Data and code availability" paragraph (24, 18) — see `SUBMISSION_CHECKLIST.md`.

**Add (needs a figure):**
- **Participant flow diagram** (item 17a) — currently prose. One simple box-and-arrow figure
  from the 10,409→…→7,153 counts already in §2.1.

Everything else is already in the manuscript.
