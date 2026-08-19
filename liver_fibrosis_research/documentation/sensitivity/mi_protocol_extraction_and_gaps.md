# Frozen Multiple-Imputation Protocol — Extraction and Gap Analysis

**Generated:** 2026-08-19, live, per Part 3. Read in full: `documentation/phase2/
missing_data_protocol.md`, `documentation/phase2/sensitivity_analysis_plan.md`,
`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`, `documentation/phase2/statistical_analysis_plan.md`,
`documentation/phase2/model_development_protocol.md`. No other document adds MI-specific detail
(confirmed via `grep -rln "MICE\|multiple imputation" documentation/`).

## Extracted (frozen, present in the actual documents)

| # | Item | Frozen value | Source |
|---|---|---|---|
| 1 | Variables to be imputed | `BMXBMI` + 7 broad-lab predictors (`LBXSATSI`, `LBXSASSI`, `LBXSAL`, `LBXSAPSI`, `LBXSTB`, `LBXPLTSI`, `LBDHDD`) — the ones with missingness in the pool | `missing_data_protocol.md` (implied by "predictors imputed"), confirmed by live missingness check this pass |
| 2 | Variables NOT imputed | `RIDAGEYR`, `RIAGENDR` (0% missing in pool by cohort construction); outcome `LUXSMED` (0% missing, never imputed) | Live missingness check |
| 4 | Imputation method (family) | "MICE-style" | `missing_data_protocol.md` |
| 5 | Predictor matrix | "other predictors + outcome-independent auxiliary variables only" — outcome must NOT be used to impute predictors | `missing_data_protocol.md` |
| 9 | Outcome handling | Never imputed (0% missing); computed from `LUXSMED` after predictor imputation, exactly as in the primary analysis | `missing_data_protocol.md` + `primary_outcome_definition.md` |
| 10 | Demographic-variable treatment | Fully observed, used as imputation predictors, not imputed themselves | Live check |
| 16 | Test-set handling | Imputation models "must be fit on training data only... never refit or re-parameterized using validation/test rows" | `missing_data_protocol.md` §Leakage-Safety Requirements |
| — | Scientific classification | **Exploratory** (not primary, not secondary) | `statistical_analysis_plan.md` §Exploratory Analyses item 3 |
| — | Purpose | Test whether the differential-missingness pattern changes the Black-subgroup fairness conclusion | `missing_data_protocol.md` §Sensitivity Analysis |
| — | Pool | Full adult quality-valid pool, `COHORT_3B_ADULT_OF_QUALITY_VALID`, N=7,768 | `missing_data_protocol.md`, live-reproduced exactly this pass |

## Genuine gaps (not specified anywhere in the frozen documentation)

| # | Item | Status |
|---|---|---|
| 3 | Number of imputations (m) | **UNSPECIFIED** |
| 4b | Concrete imputation algorithm/estimator (only the "MICE-style" family is named) | **UNSPECIFIED** |
| 11 | Random seed(s) | **UNSPECIFIED** |
| 12 | Pooling method | Not explicitly named, but "MICE-style" conventionally implies Rubin's rules for parameter pooling — treated as strongly implied, not invented from nothing, but still disclosed explicitly below since this analysis pools *predictions*, not regression parameters, which is a related but distinct convention |
| 13 | Model-refit requirement | **UNSPECIFIED** — no document states whether/how the 5 models should be refit for this sensitivity check |
| 14 | Subgroup-analysis requirement | Partially specified (targets Black-subgroup fairness; does not mention uncertainty at all — Phase 6 postdates this document) |
| 15 | Uncertainty-analysis requirement | **UNSPECIFIED / NOT AUTHORIZED** — `missing_data_protocol.md` predates Phase 6 entirely and never mentions conformal prediction or coverage |
| 17 | Statistical inference for the CC-vs-MI comparison | **UNSPECIFIED** |
| 18 | Stopping criteria | Not numerically specified in the frozen protocol (this task's own Part 16 A–F classification framework is used as the interpretation schema, supplied by this task, not invented here) |

## Resolution

Per this task's own Part 24 ("If the frozen MI protocol itself requires an amendment: create the
amendment BEFORE execution and commit it separately") and this project's established, repeatedly
successful discipline (Phase 4 Amendment #8, Phase 6 Amendments #10–11) of
resolving genuine Phase-2 gaps via a dated, justified, pre-committed amendment rather than either
(a) silently inventing an unstated method or (b) hard-stopping a well-motivated, narrowly-scoped
analysis over gaps that have a clear, standard, low-controversy resolution — the items above are
resolved via **Amendment #12**, logged in `documentation/end_to_end/protocol_amendment_registry.md`
and committed standalone, before any imputation is constructed. **Uncertainty-analysis
comparison (item 15) is explicitly NOT authorized** by the frozen protocol and is therefore
**not performed** in this pass, per Part 10's conditional framing ("If explicitly authorized").
