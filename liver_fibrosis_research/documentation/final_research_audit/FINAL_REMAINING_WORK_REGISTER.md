# FINAL REMAINING-WORK REGISTER

Read-only audit, 2026-08-27. Only genuinely unexecuted work is listed. Each item gets exactly one
status: **REQUIRED** · **IMPORTANT** · **OPTIONAL** · **DO_NOT_RUN** · **SEPARATE_WORK**.
An item is not REQUIRED merely because it is unfinished. Basis:
`documentation/final_research_state/REMAINING_WORK_DECISION_REGISTER.md`,
`NOT_EXECUTED_REGISTER.md`, `OPTIONAL_ANALYSIS_DECISION_AUDIT.md`,
`results/sensitivity/deferred_sensitivity_execution_matrix.csv`,
`documentation/phase2/statistical_analysis_plan.md`, `sensitivity_analysis_plan.md`,
`PHASE2_PROTOCOL_FREEZE.md`, `documentation/end_to_end/protocol_amendment_registry.md`.

---

## 1. CAND_4 — all-ages (≥12 y) sensitivity cohort, N=8,215 — **OPTIONAL → DO NOT DO**

- **Scientific question:** does including adolescents (12–17 y) change discrimination /
  calibration / fairness conclusions?
- **Existing evidence:** CAND_2 (elastography-eligibility axis) and CAND_3
  (predictor/architecture axis) already show the conclusions are cohort-robust; the study is
  deliberately adult-scoped (`primary_cohort_decision.md`); adolescent fibrosis uses different
  BMI/lab reference frames.
- **Incremental value:** LOW. **Duplication:** partial (same "does cohort definition matter"
  family). **Manuscript impact:** NONE — `statistical_analysis_plan.md` Governing Rule forbids
  promoting an EXPLORATORY-tier result to a conclusion.
- **Methodological risk:** MODERATE (new cohort build + 5-model refit + fresh split; pooling
  adolescents with adults raises interpretation hazards).
- **Recommendation:** DO NOT DO before manuscript. EXPLORATORY future work only.
- **Evidence:** `FINAL_CLAIM_AND_STATUS_REGISTRY.csv` row `CAND4` (`NOT_EXECUTED`);
  `cand4_resolution_evidence.csv`; Amendment #14.

### CAND_4 DECISION: **CAND_4 OPTIONAL** (execution: DO NOT DO)

## 2. Broader (whole-cohort) multiple imputation — **DO_NOT_RUN → DO NOT DO**

- **Scientific question:** do calibration / fairness / conformal conclusions hold under MI
  applied to the whole cohort and all subgroups?
- **Existing evidence:** the one documented differential-missingness concern (Non-Hispanic Black,
  41.3% vs 25.0%) is already answered by targeted MI (4/5 STABLE, MLP INDETERMINATE, all adj
  p=0.978); Phase 5 MI conformal tables descriptively consistent with complete-case; complete
  case is the **pre-registered primary** missing-data strategy.
- **Incremental value:** LOW. **Duplication:** HIGH. **Manuscript impact:** NONE.
- **Methodological risk:** HIGH — **not protocol-frozen**
  (`deferred_sensitivity_execution_matrix.csv` row 8: "DO NOT EXECUTE — NOT FROZEN"); would need
  a new dated amendment; open scope invites post-hoc scope creep.
- **Recommendation:** DO NOT DO.

### BROADER MI DECISION: **BROADER MI DO_NOT_RUN**

## 3. Conformal-coverage comparison under MI — **DO_NOT_RUN → DO NOT DO**

- Strict subset of item 2 and **explicitly not authorized** by the frozen
  `missing_data_protocol.md`; `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` §14 marks it
  "NOT AUTHORIZED". Phase 5 MI conformal tables already give a first-order descriptive answer.
- Incremental value LOW; duplication HIGH; risk HIGH; manuscript impact NONE.

## 4. Phase 5 MI-conformal executable-lineage reconstruction — **OPTIONAL → DO NOT DO (revisit only if cited load-bearing)**

- **Scientific question:** can the Phase 5 MI conformal tables be regenerated from committed
  source / models / scores / runtime log?
- **Existing evidence:** the *scientific* question is answered descriptively; only *provenance*
  is missing (`LINEAGE NOT FOUND IN REPOSITORY`).
- **Incremental value:** MODERATE if the MI conformal result is cited as evidence; LOW if it
  stays a descriptive footnote. **Duplication:** none (provenance repair).
- **Methodological risk:** MODERATE — a reconstruction that fails to reproduce the saved tables
  would convert an honest disclosure into a `CONFLICT UNRESOLVED IN REPOSITORY`.
- **Recommendation:** keep the honest `LINEAGE NOT FOUND` + descriptive-only handling for the
  current manuscript; reconstruct only if a reviewer or the thesis elevates the MI conformal
  result to a load-bearing claim.

## 5. Full 8.0-kPa pipeline (retrain + Platt refit + conformal repetition on relabeled outcome, using CAND_1) — **DO_NOT_RUN → DO NOT DO**

- **Note:** the BMI-investigation Phase 6 8.0-kPa report *did* re-run OOF Platt and split
  conformal on the 8.0-kPa relabel of CAND_1 with inherited hyperparameters (no fresh
  hyperparameter search / no fresh model fit). A *further* full retraining pipeline is what
  remains unexecuted.
- **Existing evidence:** the pre-registered authorized design was a **relabel** of frozen
  predictions (`sensitivity_analysis_plan.md` item 1: "frozen Phase 3 artifacts, no
  retraining"), executed; plus the BMI-inv Phase 6 re-calibration/conformal pass. AUC
  0.8145–0.8326; discrimination + BMI-Obese disparity stable; Age-60+ significance
  threshold-sensitive.
- **Incremental value:** LOW (a 0.2-kPa shift adding 49 positives cannot plausibly change
  model/threshold selection). **Duplication:** HIGH. **Risk:** MODERATE (a second full pipeline
  to maintain; not frozen). **Manuscript impact:** NONE.
- **Recommendation:** DO NOT DO.

## 6. Conformal-uncertainty replication for CAND_2 / CAND_3 / 8.0 kPa (subgroup coverage) — **OPTIONAL → DO NOT DO now (highest-value optional item)**

- **Scientific question:** do the BMI-Obese (76.8–82.3%) and Age-60+ (81.1–85.6%) conformal
  **under-coverage** patterns replicate on the sensitivity cohorts?
- **Existing evidence:** the subgroup conformal failure is a headline result demonstrated on
  CAND_1 only; the three executed sensitivity analyses replicated discrimination / calibration /
  fairness but **did not repeat conformal**. Indirect support: the same two subgroups show a
  robust sensitivity disparity across CAND_1/2/3, mechanistically linked to the coverage failure.
- **Incremental value:** MODERATE (the one genuinely un-triangulated primary finding).
  **Duplication:** none. **Methodological risk:** LOW–MODERATE — re-applies the frozen
  split-conformal framework to already-built cohorts, but the analysis is **not frozen with an
  explicit execution scope** (deferred future work, Amendment #13).
- **Recommendation:** not needed for the base manuscript; **run this FIRST** if a reviewer
  challenges the generalizability of the conformal subgroup finding.

- **UPDATE 2026-08-27 — EXECUTED (CAND_2, CAND_3) under Protocol Amendment #16.** The 8.0-kPa
  conformal replication was already done (BMI-investigation Phase 6). Script
  `src/sens_14_conformal_replication_sensitivity_cohorts.py`; results
  `results/sensitivity/conformal_replication_*.{csv,json}`; report
  `documentation/sensitivity/CONFORMAL_REPLICATION_SENSITIVITY_COHORTS_RESULTS_REPORT.md`.
  **The CAND_1 pattern replicates:** marginal coverage meets target on both cohorts (0.896–0.917);
  **BMI-Obese under-covers in 5/5 models on both** (CI excludes 0.90, FDR-significant throughout);
  **Age-60+ under-covers in direction in 5/5 on both**, FDR-significant 5/5 on CAND_2 and 2/5 on
  CAND_3 (small Age-60+ cell). BMI-Normal/Overweight/Age-18–39 over-cover, as on CAND_1. The
  subgroup conformal-coverage finding — and specifically BMI-Obese under-coverage — is now
  triangulated across CAND_1 / 8.0 kPa / CAND_2 / CAND_3. Status: **EXECUTED — robustness check,
  not a new primary result; CAND_1 numbers unchanged.**

## 7. XGBoost mitigation retuning — **DO_NOT_RUN (RESOLVED) → DO NOT DO**

- **Status:** already executed and independently verified 2026-08-27
  (`src/phase7_mitigation_cleanup.py`, `PHASE7_MITIGATION_CLEANUP_VERIFICATION.md`) →
  **NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED**. Nothing further to do. The XGBoost conformal
  tolerance breach (Mondrian +5.27 pp; joint +6.80 pp) remains a disclosed,
  unresolvable-within-scope limitation.

## 8. Joint-mitigation hardening / re-freeze — **DO_NOT_RUN → DO NOT DO**

- The joint intersectional artifact is EXPLORATORY with generating lineage
  `NOT FOUND IN REPOSITORY` and its own tolerance breaches. No
  authorized protocol exists to "harden" it, and it is not a manuscript-primary object.
  Preserve as exploratory; do not attempt to promote or re-derive it here.

## 9. AFCP cleanup / narrative-status resolution — **OPTIONAL → DO NOT DO (documentation only)**

- The faithful-AFCP final narrative status is `CONFLICT UNRESOLVED IN REPOSITORY` (blocked vs
  conditional-frozen). This is a **documentation** decision, not an experiment. It has no effect
  on manuscript claims because **no AFCP-superiority claim is permitted** under either label.
  Recommendation: the register owner may add a one-line adjudication; no analysis is needed.

## 10. Severity-graded secondary outcomes (≥9.7 kPa advanced fibrosis, 411 positives, 5.75%; ≥13.6 kPa cirrhosis, 177 positives, 2.47%) — **IMPORTANT (status resolution) / OPTIONAL (execution) → DO add to register; a relabel-only pass is DO-able**

- **Register-completeness finding.** This is a **frozen SECONDARY analysis**
  (`statistical_analysis_plan.md` SECONDARY item 2, `PHASE2_PROTOCOL_FREEZE.md` row 17). Outcome
  columns exist in `analysis_dataset_primary.parquet`
  (`outcome_secondary_advanced_9.7kPa`, `outcome_secondary_cirrhosis_13.6kPa`). **No result
  artifact exists anywhere, and the item is in no remaining-work register and no master report.**
- **Scientific question:** do discrimination / calibration / fairness conclusions hold for
  advanced-fibrosis and cirrhosis outcome definitions?
- **Incremental value:** MODERATE — a pre-registered SECONDARY outcome currently has no result
  and no tracked status; a reviewer could flag the silent omission.
- **Execution burden:** LOW for a relabel-only descriptive discrimination/calibration pass (same
  cohort, same predictors, frozen models, no retraining — exactly as the 8.0-kPa check).
  Cirrhosis subgroup fairness would be low-powered (~53 test positives) and should be
  overall-only.
- **Recommendation:** **DO** add this item to the remaining-work register; a relabel-only
  descriptive pass is a justified low-cost option to close a pre-registered SECONDARY item.
  **Full retraining is NOT justified.**

- **UPDATE 2026-08-27 — EXECUTED (relabel-only descriptive pass).** Done under Protocol
  Amendment #15. Script `src/sens_13_secondary_severity_outcomes.py`; results
  `results/sensitivity/secondary_severity_outcomes_*.{csv,json}`; report
  `documentation/sensitivity/SECONDARY_SEVERITY_GRADED_OUTCOMES_RESULTS_REPORT.md`. Findings:
  discrimination comparable to the primary 8.2-kPa outcome for both cutpoints (AUROC 0.85–0.86
  ≥9.7 kPa; 0.84–0.86 ≥13.6 kPa; no model-family separation); raw over-prediction worsens at the
  lower prevalences; **the frozen 8.2-kPa Platt recalibration does not transport** (recalibrated
  intercepts −0.4 to −0.8 for ≥9.7 kPa, −1.2 to −1.9 for ≥13.6 kPa); BMI-Obese-vs-Normal
  sensitivity disparity direction preserved in 5/5 models for ≥9.7 kPa but **not independently
  powered** (Normal-BMI n=11 test positives; only logistic's CI excludes 0); Age-60+ remains
  fragile. ≥13.6 kPa reported overall-only (59 test positives). Status: **EXECUTED — relabel-only,
  descriptive; not a deployable severity-staging model claim.** No per-outcome retraining or
  recalibration performed.

## 11. Survey-weighted / weighted-loss model training — **DO_NOT_RUN → FORMALLY DEFERRED 2026-08-27**

- Frozen **EXPLORATORY** item (`statistical_analysis_plan.md` EXPLORATORY item 4).
- **REGISTER ENTRY (2026-08-27):** **NOT EXECUTED — FORMALLY DEFERRED.** Not executed, not
  planned, and no manuscript claim depends on it. The frozen plan itself records ML
  survey-weighting as a "genuinely unresolved methodological status"
  (`survey_weight_protocol.md`). Complete-case, unweighted training is the pre-registered
  primary strategy. Revisit only under a new dated protocol amendment. The manuscript notes it as
  a pre-registered exploratory item that was deferred (`MANUSCRIPT_DRAFT.md` §5).
- This closes the second of the two previously-untracked pre-registered items (the first,
  severity-graded secondary outcomes, is EXECUTED — item 10, Amendment #15).

---

## Summary table

| # | Item | Status | Decision |
|---|---|---|---|
| 1 | CAND_4 all-ages (≥12) | OPTIONAL | DO NOT DO |
| 2 | Broader whole-cohort MI | DO_NOT_RUN | DO NOT DO |
| 3 | Conformal-coverage comparison under MI | DO_NOT_RUN | DO NOT DO |
| 4 | Phase 5 MI-conformal lineage reconstruction | OPTIONAL | DO NOT DO (revisit if cited) |
| 5 | Full 8.0-kPa retraining pipeline | DO_NOT_RUN | DO NOT DO |
| 6 | Conformal replication CAND_2/CAND_3/8.0 kPa | OPTIONAL | **EXECUTED 2026-08-27 (Amendment #16; 8.0 kPa was already done)** — pattern replicates; see item 6 UPDATE |
| 7 | XGBoost mitigation retuning | DO_NOT_RUN (resolved) | DO NOT DO |
| 8 | Joint-mitigation hardening | DO_NOT_RUN | DO NOT DO |
| 9 | AFCP narrative-status resolution | OPTIONAL (docs only) | DO NOT DO (adjudicate on paper) |
| 10 | Severity-graded secondary outcomes | IMPORTANT (status) / OPTIONAL (execute) | **EXECUTED 2026-08-27 (relabel-only, Amendment #15)** — see item 10 UPDATE |
| 11 | Survey-weighted / weighted-loss training | DO_NOT_RUN | **NOT EXECUTED — FORMALLY DEFERRED 2026-08-27** (see item 11 entry) |
| — | Temporal validation (NHANES 2021–2023) | SPLIT INTO A SEPARATE MANUSCRIPT | removed from this repo; preserved on the `temporal-validation-standalone` branch; not part of this study |
| — | External (non-NHANES) validation | NOT EXECUTED / blocked | top future priority; out of scope here |

**No item among the repository's remaining non-validation work is REQUIRED before manuscript
preparation.** The single genuinely material gap — external validation — is SEPARATE WORK,
already disclosed as the project's foremost limitation, and currently blocked by the absence of a
compatible independent cohort.

## Other unexecuted analyses found during this audit (not previously in the remaining-work register)

| Item | Where frozen | Result artifact? | Disposition |
|---|---|---|---|
| Severity-graded secondary outcomes (≥9.7, ≥13.6 kPa) | `statistical_analysis_plan.md` SECONDARY item 2; `PHASE2_PROTOCOL_FREEZE.md` row 17 | **`results/sensitivity/secondary_severity_outcomes_*` (Amendment #15, 2026-08-27)** | see item 10 UPDATE — EXECUTED relabel-only |
| Survey-weighted / weighted-loss training | `statistical_analysis_plan.md` EXPLORATORY item 4; `survey_weight_protocol.md` | NONE | **NOT EXECUTED — FORMALLY DEFERRED 2026-08-27** (item 11) |
| F3+ / F4 stage-specific modelling beyond relabel | `primary_outcome_definition.md` (noted as unexecuted) | NONE | subsumed by item 10; DO NOT DO beyond relabel |

None of these were executed. None is REQUIRED. Two (secondary outcomes, weighted training) are
now flagged for register entry.
