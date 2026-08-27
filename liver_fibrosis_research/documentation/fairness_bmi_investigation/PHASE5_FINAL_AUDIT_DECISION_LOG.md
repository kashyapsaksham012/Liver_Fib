# Phase 5 MI Conformal Final Audit Decision Log

**Mode:** read-only final audit; no rerun and no existing artifact modification.

| Audit item | Decision | Evidence / limitation |
|---|---|---|
| Overall disposition | **B — accepted with limitations** | Saved MI tables support a descriptive consistency conclusion; source/runtime and comparative-inference gaps remain. |
| Exact MI protocol | PASS | Manifest/registry show exactly 5 datasets, seeds 42–46, BayesianRidge IterativeImputer, 10 predictors, outcome excluded, N=7,768 pool. |
| Distinct imputations | PASS | Five registry hashes exist, match files, and are distinct; diagnostics show zero missing after imputation. |
| Static MI diagnostics scope | PASS WITH LIMITATION | `mi_01` explicitly fits full-pool static datasets for diagnostics only; they are not valid evidence of leakage-safe conformal fitting. |
| Fold-embedded MI preprocessing | PASS FOR CV-OOF ONLY | `mi_02` embeds IterativeImputer inside each fold and does not reference test IDs. No MI conformal implementation is available to verify the reported refit. |
| Frozen model families/parameters | PARTIAL | Manifest claims frozen five families and unchanged Phase 3 parameters; `mi_02` supports this for CV-OOF, but no MI conformal model artifacts/source are present. |
| Complete-case comparator | PASS | Phase 6 refit/calibration/test artifacts provide a coherent independent complete-case authority: 4,005/1,002/2,146. |
| Per-imputation conformal results | PARTIAL | 25 overall rows and 375 subgroup rows are internally arithmetical; thresholds and covered counts exist, but no per-participant or calibration-score artifacts permit independent reconstruction. |
| No unsupported pooling | PASS | MI outputs retain imputation index; uncertainty table labels means/ranges/SDs descriptive and explicitly denies inferential pooling. |
| Subgroup metrics | PASS WITH LIMITATION | All 15 categories across sex, race/ethnicity, age, and BMI are present per model/imputation with Wilson intervals and FDR fields; conditional validity is not established. |
| Intersectional scope | PASS WITH LIMITATION | Exactly 26 pre-specified cells per model/imputation are present; rows are exploratory/uncorrected and sparse tiers are retained. |
| Sparse-cell handling | PASS | Insufficient-evidence and limited-precision tiers are visible; no cells are silently dropped or redefined. |
| Uncertainty/efficiency metrics | PASS DESCRIPTIVELY | Coverage, set size, singleton, ambiguous, empty-set rates, and thresholds are reported; between-imputation summaries are descriptive only. |
| Five-imputation consistency | PASS DESCRIPTIVELY | Overall ranges and persistent Obese undercoverage agree across all five imputations; this is not a formal stability/equivalence test. |
| Locked-test partition | PARTIAL | Expected/live hash agrees and manifest asserts one post-selection evaluation, but no runtime event log or MI source proves order. |
| Runtime-order evidence | LIMITED | Filesystem mtimes place output CSVs before manifest/lineage writes, while internal manifest time is earlier; this inconsistency weakens, but does not prove, contamination. |
| Statistical support | RESTRICTED | Wilson intervals/binomial fields support proportion descriptions; no MI-vs-CC comparative CI, equivalence test, or Rubin pooling exists. |
| Main conclusion | SUPPORTED WITH SCOPE | “MI conformal reliability is consistent with complete-case results” is supportable descriptively, not as equivalence or statistical indistinguishability. |
| Historical phrase handling | PASS | Prior report wording remains unchanged; current report uses the exact allowed conclusion and does not silently rewrite history. |
| Preservation | PASS | No inspected prior-phase, primary/master, temporal/external, Phase 7, or complete-case authority artifact was overwritten or merged. |

## Final decision

**B.** Retain the current conclusion with the explicit limits above. Do not claim formal
equivalence, pooled MI inference, conditional subgroup validity, or independently proven
runtime test-order protection.

