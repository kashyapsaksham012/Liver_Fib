# Optional-Analysis Decision Audit

**Date:** 2026-08-27
**Mode:** READ-ONLY decision audit. No experiment executed, no analysis re-run, no result or
master document modified. No temporal or external validation performed.
**Companion CSV:** `results/final_research_state/OPTIONAL_ANALYSIS_DECISION_AUDIT.csv`

## Purpose

Determine which of the repository's remaining **unexecuted non-validation analyses** are
scientifically justified before manuscript preparation. Each item receives exactly one status:
`REQUIRED` · `IMPORTANT` · `OPTIONAL` · `DO_NOT_RUN`, plus a `DO` / `DO NOT DO` decision.

An item is **not** classified `REQUIRED` merely because it is listed as unexecuted.

## Authoritative basis (read live this pass)

- `documentation/final_research_state/FINAL_RESEARCH_STATE.md`
- `documentation/final_research_state/REMAINING_WORK_DECISION_REGISTER.md`
- `documentation/final_research_state/NOT_EXECUTED_REGISTER.md`, `DO_NOT_RUN_REGISTER.md`,
  `PHASE_STATUS_MAP.md`, `MANUSCRIPT_READY_PRIMARY_CLAIMS.md`
- `results/final_research_state/FINAL_CLAIM_AND_STATUS_REGISTRY.csv`
- `results/sensitivity/deferred_sensitivity_execution_matrix.csv`
- `documentation/project_roadmap/deferred_sensitivity_analyses.md`
- `documentation/validation/deferred_sensitivity_scope_reconciliation.md`
- `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`, `statistical_analysis_plan.md`,
  `sensitivity_analysis_plan.md`
- `documentation/end_to_end/protocol_amendment_registry.md` (Amendments #12–#14)

## Context: what is already done

| Pre-registered sensitivity / robustness analysis | Status |
|---|---|
| 8.0 kPa threshold (relabel of frozen predictions) | **EXECUTED** 2026-08-20 — AUC 0.8145–0.8326; calibration + BMI-Obese disparity stable; Age-60+ 2/4 lose significance |
| CAND_2 relaxed-elastography cohort (fresh split + refit) | **EXECUTED** 2026-08-20 — AUC 0.8526–0.8572; pattern stable; Age-60+ 3/4 lose significance |
| CAND_3 fasting-extended architecture (12 predictors, refit) | **EXECUTED** 2026-08-20 — AUC 0.8280–0.8457; pattern stable; Age-60+ 4/4 lose significance |
| Targeted MI (Non-Hispanic Black CV-OOF sensitivity/FNR) | **EXECUTED** 2026-08-19 — MI ROBUSTNESS PARTIAL; 4/5 STABLE, MLP INDETERMINATE; all adj p=0.978 |
| Phase 5 MI conformal reliability (descriptive tables) | **EXECUTED** — descriptively consistent with complete-case; `LINEAGE NOT FOUND IN REPOSITORY` |
| Intersectional fairness (exploratory) | **EXECUTED** — `results/fairness/intersectional_exploratory_metrics.csv` |
| XGBoost mitigation retuning + joint intersectional mitigation audit (Phase 7 cleanup) | **EXECUTED + VERIFIED** 2026-08-27 — `NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED`; joint = `VALID BUT EXPLORATORY ONLY` |
| Temporal validation (NHANES 2021–2023) | **EXECUTED** as separate work — `PARTIAL TEMPORAL REPLICATION` |

The discrimination / calibration / BMI-Obese-fairness story is triangulated across **three**
independent cohort perturbations. The Age-60+ disparity is directionally robust but
specification-sensitive for significance — this is already disclosed.

---

## Item-by-item decision

### 1. CAND_4 — all-ages (≥12 y) sensitivity cohort, N=8,215 — `OPTIONAL` → **DO NOT DO**

- **Scientific question:** does including adolescents (12–17 y) change the discrimination /
  calibration / fairness conclusions?
- **Addresses a current limitation?** No. The study is deliberately adult-scoped
  (`primary_cohort_decision.md` clinical-appropriateness reasoning). Adolescent fibrosis is a
  different clinical entity with different lab/BMI reference frames.
- **Already answered?** Indirectly. CAND_2 (elastography axis) and CAND_3 (predictor/architecture
  axis) already show the conclusions are cohort-robust. CAND_4 is a third, orthogonal axis (age
  eligibility), not a duplicate, but the marginal information is small: adolescents add ~1,060
  records at very low fibrosis prevalence.
- **Changes a manuscript-level conclusion?** No — `statistical_analysis_plan.md` Governing Rule
  forbids promoting an EXPLORATORY-tier result to a primary/secondary conclusion.
- **Incremental value:** LOW.
- **Duplication:** Partial (same "does cohort definition matter" family as CAND_2/CAND_3).
- **Methodological risk:** MODERATE — requires constructing a new cohort and refitting all five
  models; pooling adolescents with adults raises interpretation hazards (pediatric BMI
  percentiles vs. absolute BMI; age-specific lab ranges).
- **Implementation burden:** MODERATE-HIGH (full cohort build + 5-model refit + fresh split).
- **Does its absence materially weaken the paper?** No. The repository's own final classification
  is *"Optional future work, EXPLORATORY tier — not required before manuscript preparation"*
  (`deferred_sensitivity_analyses.md` item 2b; Amendment #14).
- **Evidence:** `FINAL_CLAIM_AND_STATUS_REGISTRY.csv` row `CAND4` (`NOT_EXECUTED`, "Do not report
  performance"); `deferred_sensitivity_execution_matrix.csv` ("DO NOT EXECUTE — STATUS
  UNRESOLVED", later resolved to DISTINCT–EXPLORATORY–UNEXECUTED); Amendment #14.

### 2. Broader Multiple Imputation — calibration / fairness / uncertainty under full MI — `DO_NOT_RUN` → **DO NOT DO**

- **Scientific question:** do the calibration, fairness, and conformal conclusions hold under
  multiple imputation applied to the whole cohort and every subgroup (not only Non-Hispanic
  Black)?
- **Addresses a current limitation?** Marginally. The one *documented* differential-missingness
  concern — Non-Hispanic Black at 41.3% of complete-case exclusions vs. 25.0% of retained
  (`missing_data_protocol.md`) — has already been addressed with a targeted MI analysis. No other
  subgroup has a documented missingness-bias finding motivating a broader pass.
- **Already answered?** For the motivated question, yes (targeted MI: 4/5 STABLE, all adj
  p=0.978). Phase 5 MI conformal tables already show reliability is descriptively consistent with
  complete-case.
- **Changes a manuscript-level conclusion?** No — complete-case is the *pre-registered primary*
  missing-data strategy; MI is an exploratory/sensitivity layer per
  `statistical_analysis_plan.md` EXPLORATORY item 3.
- **Incremental value:** LOW.
- **Duplication:** HIGH — substantially overlaps the executed targeted MI and the Phase 5 MI
  conformal work.
- **Methodological risk:** HIGH — **not protocol-frozen**; `deferred_sensitivity_execution_matrix.csv`
  marks it `DO NOT EXECUTE — NOT FROZEN`; would require a new dated protocol amendment; open scope
  invites post-hoc scope creep.
- **Implementation burden:** HIGH (m×5 imputations × full Phase 3–6 pipeline).
- **Does its absence materially weaken the paper?** No.
- **Evidence:** `REMAINING_WORK_DECISION_REGISTER.md` ("Not executed/not frozen; new protocol
  required"); `deferred_sensitivity_execution_matrix.csv` row 8; `missing_data_protocol.md`;
  `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` §10/§14.

### 3. Conformal-coverage comparison under MI — `DO_NOT_RUN` → **DO NOT DO**

- **Scientific question:** does subgroup conformal coverage behave the same under MI as under
  complete-case?
- A strict subset of item 2, and **explicitly not authorized** by the frozen
  `missing_data_protocol.md` (confirmed: the document contains no Phase-6-era conformal-coverage
  language). Phase 5 MI conformal descriptive tables already provide a first-order answer, with
  the reproducibility caveat noted in item 4.
- **Incremental value:** LOW. **Duplication:** HIGH (item 2 / Phase 5 MI). **Risk:** HIGH (not
  frozen). **Manuscript impact:** none.
- **Evidence:** `deferred_sensitivity_execution_matrix.csv` row 8;
  `MULTIPLE_IMPUTATION_SENSITIVITY_RESULTS_REPORT.md` §14 ("Uncertainty/conformal-coverage
  comparison under MI — NOT AUTHORIZED"); `NOT_EXECUTED_REGISTER.md`.

### 4. Phase 5 MI-conformal executable-lineage reconstruction — `OPTIONAL` → **DO NOT DO** (revisit only if that result is cited load-bearing)

- **Scientific question:** can the Phase 5 MI conformal tables be regenerated from committed
  source, models, scores, and a runtime log?
- **Addresses a current limitation?** Yes, a real one — the tables are used in the manuscript
  taxonomy as `MANUSCRIPT_READY_WITH_QUALIFICATION` but carry `LINEAGE NOT FOUND IN REPOSITORY`
  (no executable source / models / scores / prediction sets / runtime log / equivalence test /
  Rubin pooling).
- **Already answered?** The *scientific* question (is MI reliability consistent with
  complete-case?) is answered descriptively. Only the *provenance* is missing.
- **Incremental value:** MODERATE **if** the MI conformal result is cited as evidence;
  LOW if it stays a descriptive footnote.
- **Duplication:** None (provenance repair, not new analysis).
- **Methodological risk:** MODERATE — a reconstruction that fails to reproduce the saved tables
  would create a `CONFLICT UNRESOLVED IN REPOSITORY` where today there is an honest disclosure.
- **Implementation burden:** MODERATE.
- **Does its absence materially weaken the paper?** Only slightly, and it is already handled by
  the explicit `LINEAGE NOT FOUND IN REPOSITORY` token and the `VERIFIED_WITH_LIMITATIONS` /
  descriptive-only restriction. `REMAINING_WORK_DECISION_REGISTER.md` states "Not authorized
  here."
- **Recommendation:** keep the honest-disclosure handling for the current manuscript; reconstruct
  only if a reviewer or the thesis elevates the MI conformal result to a load-bearing claim.
- **Evidence:** `FINAL_CLAIM_AND_STATUS_REGISTRY.csv` row `P5`; `FINAL_RESEARCH_STATE.md`;
  `VERIFIED_WITH_LIMITATIONS_REGISTER.md`.

### 5. Full 8.0 kPa pipeline — retraining + Platt refit + conformal repetition — `DO_NOT_RUN` → **DO NOT DO**

- **Scientific question:** does the *modeling pipeline* (not just relabeled predictions) hold if
  the outcome cutoff is 8.0 kPa?
- **Already answered?** Yes, at the level the pre-registered plan specified. The 8.0 kPa check
  was executed as a **relabel** of frozen predictions (`retrained=False`), which was the
  authorized design (`sensitivity_analysis_plan.md` item 1: "frozen Phase 3 artifacts, no
  retraining"). Result: AUC 0.8145–0.8326, calibration + BMI-Obese disparity stable.
- **Changes a conclusion?** Implausible — a 0.2 kPa shift adding 49 positives (666→715) will not
  change which model family or threshold is optimal.
- **Incremental value:** LOW. **Duplication:** HIGH (the executed relabel). **Risk:** MODERATE —
  a second full pipeline to maintain; full execution is "not frozen." **Manuscript impact:** none.
- **Evidence:** `deferred_sensitivity_analyses.md` item 1; `alternative_threshold_8p0kPa_results.csv`
  (`retrained=False`); `REMAINING_WORK_DECISION_REGISTER.md` ("result is relabel-only").

### 6. Conformal-uncertainty replication for CAND_2 / CAND_3 / 8.0 kPa (subgroup coverage) — `OPTIONAL` → **DO NOT DO** (highest-value optional item; run first if conformal robustness is challenged)

- **Scientific question:** do the BMI-Obese (76.8–82.3%) and Age-60+ (81.1–85.6%) conformal
  **under-coverage** patterns replicate on the sensitivity cohorts?
- **Addresses a current limitation?** Yes — the subgroup conformal-coverage failure is a headline
  result and has been demonstrated only on CAND_1. The three executed sensitivity analyses
  replicated discrimination / calibration / fairness but **did not repeat conformal**.
- **Already answered?** Partially and indirectly: the *same two subgroups* show a robust
  sensitivity disparity across CAND_1/2/3, which is mechanistically linked to the coverage
  failure. So the coverage finding is not un-supported, just not directly re-measured.
- **Changes a manuscript-level conclusion?** No. Absence is a disclosed limitation, not a
  conclusion.
- **Incremental value:** MODERATE (the one genuinely un-triangulated primary finding).
- **Duplication:** None.
- **Methodological risk:** LOW — re-applies the frozen split-conformal framework to
  already-built cohorts; no new modeling decisions. But the analysis is **"not frozen with an
  explicit execution scope"** and was deferred as documented future work (Amendment #13).
- **Implementation burden:** MODERATE.
- **Does its absence materially weaken the paper?** Slightly weakens the robustness section;
  does not undermine the primary conformal claim (strong on CAND_1, clear mechanism, same
  subgroups triangulated on fairness).
- **Recommendation:** not needed for the base manuscript; it is the **first** analysis to run if
  a reviewer challenges the generalizability of the conformal subgroup finding.
- **Evidence:** `deferred_sensitivity_execution_matrix.csv` row 9 ("DO NOT EXECUTE — NOT FROZEN
  (deferred as documented future work; not silently dropped)"); `evaluation_metrics_protocol.md`;
  Amendment #13.

### 7. XGBoost mitigation retuning — `DO_NOT_RUN` (RESOLVED) → **DO NOT DO**

- **Status:** already executed and independently verified on 2026-08-27
  (`src/phase7_mitigation_cleanup.py`, `PHASE7_MITIGATION_CLEANUP_VERIFICATION.md`). Final status
  `NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED` — every candidate in the authorized family that
  closes the BMI fairness gap costs 11–22 pp of overall sensitivity or flips the coverage breach.
- **Incremental value:** NONE (question answered). **Duplication:** total. **Risk:** N/A.
  **Manuscript impact:** none beyond the existing disclosed limitation.
- **Recommendation:** nothing further to do. The XGBoost conformal tolerance breach (Mondrian
  +5.27 pp; joint +6.80 pp) remains a disclosed, unresolvable-within-scope limitation.
- **Evidence:** `results/fairness_bmi_investigation/phase7_mitigation_cleanup/`;
  `PHASE7_MITIGATION_CLEANUP_REPORT.md`; `PHASE7_MITIGATION_CLEANUP_VERIFICATION.md`.

---

## Excluded from this audit (validation work — out of scope by instruction)

| Item | Status | Note |
|---|---|---|
| **External (non-NHANES) validation** | `NOT_EXECUTED` / `SEPARATE_WORK` | The project's own documentation names this the single largest generalizability gap. **Blocked** — "no compatible independent cohort" identified. Partially mitigated by temporal validation. Not scored here because it is validation work and explicitly out of scope. |
| **Temporal (NHANES 2021–2023) validation** | `AUTHORITATIVE` / `SEPARATE_WORK` — **COMPLETE** | Final status `PARTIAL TEMPORAL REPLICATION` (N=4,910; 563 positive; AUROC 0.7765–0.7824). Not remaining work. |

---

## Register-completeness findings (surfaced by this audit; not in the remaining-work register)

These are frozen Phase-2 analyses that are unexecuted **and not tracked** in
`REMAINING_WORK_DECISION_REGISTER.md` or `NOT_EXECUTED_REGISTER.md`. Flagged for the register
owner; adjudicated here only provisionally.

### A. Severity-graded secondary outcome (≥9.7 kPa advanced fibrosis; ≥13.6 kPa cirrhosis) — provisional `IMPORTANT` (status resolution), `OPTIONAL` (execution)

- A **frozen SECONDARY analysis** in `statistical_analysis_plan.md` (SECONDARY item 2) and
  `PHASE2_PROTOCOL_FREEZE.md` (row 17, "Secondary outcome"). Outcome columns exist in
  `analysis_dataset_primary.parquet` (`outcome_secondary_advanced_9.7kPa`, 411 positives, 5.75%;
  `outcome_secondary_cirrhosis_13.6kPa`, 177 positives, 2.47%).
- **No result artifact exists anywhere** in the repository, and the item appears in **no**
  remaining-work register and in **no** master/end-to-end report.
- **Why it matters:** a pre-registered SECONDARY (not exploratory) analysis silently absent from
  the authoritative remaining-work register is a documentation gap. Its *status* should be
  resolved — either executed descriptively or formally deferred with rationale and a register
  entry.
- **Execution burden:** LOW for a descriptive pass — same cohort, same predictors, same frozen
  models; can relabel frozen predictions against the two secondary-outcome columns exactly as the
  8.0 kPa check did (no retraining). Cirrhosis (≥13.6 kPa) subgroup fairness would be
  low-powered (~53 test positives) and should be reported overall-only.
- **Recommendation:** **DO** add it to the remaining-work register; a relabel-only descriptive
  discrimination/calibration pass is low-cost and closes a pre-registered secondary item. Full
  retraining is **not** justified.
- **Evidence:** `statistical_analysis_plan.md` SECONDARY item 2; `PHASE2_PROTOCOL_FREEZE.md`
  row 17; `primary_outcome_definition.md`; parquet column inventory.

### B. Weighted-loss / survey-weighted model training — provisional `DO_NOT_RUN`

- Frozen **EXPLORATORY** item (`statistical_analysis_plan.md` EXPLORATORY item 4), unexecuted,
  not in any remaining-work register. The plan itself calls ML weighting a "genuinely unresolved
  methodological status." No manuscript claim depends on it.
- **Recommendation:** **DO NOT DO**; add a one-line register entry marking it formally deferred.
- **Evidence:** `statistical_analysis_plan.md` EXPLORATORY item 4; `survey_weight_protocol.md`.

---

## Summary

| Item | Status | Decision |
|---|---|---|
| 1. CAND_4 (all-ages ≥12) | `OPTIONAL` | DO NOT DO |
| 2. Broader MI (full calibration/fairness/uncertainty) | `DO_NOT_RUN` | DO NOT DO |
| 3. Conformal-coverage comparison under MI | `DO_NOT_RUN` | DO NOT DO |
| 4. Phase 5 MI-conformal lineage reconstruction | `OPTIONAL` | DO NOT DO (revisit if cited) |
| 5. Full 8.0 kPa pipeline (retrain + recalibrate + conformal) | `DO_NOT_RUN` | DO NOT DO |
| 6. Conformal replication for CAND_2/CAND_3/8.0 kPa | `OPTIONAL` | DO NOT DO (run first if challenged) |
| 7. XGBoost mitigation retuning | `DO_NOT_RUN` (resolved) | DO NOT DO |
| — External validation | out of scope (validation; blocked) | — |
| — Temporal validation | complete | — |
| A. Severity-graded secondary outcome | `IMPORTANT` (resolve status) / `OPTIONAL` (execute) | DO add to register; a relabel-only pass is DO-able |
| B. Weighted-loss model training | `DO_NOT_RUN` | DO NOT DO |

**No item among the repository's remaining non-validation work is `REQUIRED` before manuscript
preparation.** This matches the frozen plan: `sensitivity_analysis_plan.md`'s Governing Rule
describes its analyses as "a pre-registered list, not a mandatory execution schedule," and no
frozen document labels any item "required." The primary and qualified registers are
manuscript-ready as they stand.

The single genuinely material gap — external validation — is out of scope for this audit,
already documented as the project's foremost limitation, and currently blocked by the absence of
a compatible independent cohort.

## Final decisions

- **CAND_4 — DO NOT DO.** Three orthogonal cohort perturbations already establish robustness; adolescent inclusion is outside the paper's adult clinical scope and can never be promoted above EXPLORATORY tier.
- **Broader MI — DO NOT DO.** The one documented differential-missingness concern is already answered by targeted MI; a broader pass is not protocol-frozen and duplicates existing evidence.
- **Conformal-coverage comparison under MI — DO NOT DO.** Explicitly unauthorized by the frozen missing-data protocol and subsumed by broader MI.
- **Phase 5 MI-conformal lineage reconstruction — DO NOT DO.** The honest `LINEAGE NOT FOUND IN REPOSITORY` disclosure plus descriptive-only use is an acceptable manuscript posture; reconstruct only if that result becomes load-bearing.
- **Full 8.0 kPa pipeline — DO NOT DO.** The pre-registered relabel check already answers the threshold-robustness question; a 0.2 kPa shift cannot plausibly change model/threshold selection.
- **Conformal replication for CAND_2/CAND_3/8.0 kPa — DO NOT DO now.** Deferred non-frozen future work; the same subgroups are already triangulated on the fairness finding, so run this only if a reviewer challenges conformal generalizability.
- **XGBoost mitigation retuning — DO NOT DO.** Already executed and verified; `NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED`.
- **Severity-graded secondary outcome — DO add it to the remaining-work register**, and a relabel-only descriptive pass is a justified low-cost option to close a pre-registered SECONDARY item; full retraining is not justified.
- **Weighted-loss model training — DO NOT DO**; record it as formally deferred.
