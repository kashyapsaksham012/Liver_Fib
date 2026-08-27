# Phase 5 MI Conformal Analysis — Read-Only Final Audit

**Authoritative repository:** `/Users/sakshamkashyap/Desktop/Research /liver_fibrosis_research`  
**Audit mode:** read-only; no Phase 5 source, result, protocol, split, model, or prior-phase
artifact was rerun, modified, or overwritten. This audit created only the four files named in
the task.

## Final decision: B

**B — the stated conclusion is accepted with documented limitations.** The available Phase 5
MI conformal tables consistently support a *descriptive* statement that MI reliability is
similar to the frozen complete-case conformal results. The conclusion is not an equivalence
claim: there is no formal MI-versus-complete-case comparative test, no Rubin-style pooling for
prediction-set outcomes, no runtime event log, and no executable source that produces the Phase
5 MI conformal namespace. These limitations prevent an A-level reproducibility/provenance
finding, but do not overturn the descriptive conclusion supported by the saved tables.

## Materials inspected

- `documentation/fairness_bmi_investigation/PHASE5_MI_CONFORMAL_REPORT.md`
- `documentation/fairness_bmi_investigation/PHASE5_MI_CONFORMAL_DECISION_LOG.md`
- `documentation/fairness/phase5_pre_execution_snapshot.md`
- `documentation/sensitivity/mi_protocol_extraction_and_gaps.md`
- `documentation/sensitivity/multiple_imputation_pre_execution_snapshot.md`
- `documentation/phase2/missing_data_protocol.md`,
  `documentation/phase2/sensitivity_analysis_plan.md`, and
  `documentation/phase2/uncertainty_protocol.md`
- `results/fairness_bmi_investigation/phase5_mi_conformal/` (all seven files)
- `results/fairness_bmi_investigation/phase5_mi_conformal_figures/` (five figures)
- `results/sensitivity/multiple_imputation_registry.csv`,
  `multiple_imputation_diagnostics.csv`, and `mi_model_protocol_decision.csv`
- `src/mi_01_construct_and_diagnostics.py`,
  `src/mi_02_black_subgroup_comparison.py`, and
  `src/mi_03_black_subgroup_inference.py`
- Complete-case conformal authority:
  `src/phase6_02_conformal_refit.py`, `src/phase6_03_conformal_calibration.py`,
  `src/phase6_04_final_test_touch.py`, the Phase 6 refit/threshold registries, and
  `results/uncertainty/{marginal_coverage_test_set,subgroup_coverage,coverage_inference}.csv`
- Historical MI commits B/C/D (`4802602`, `f73ef91`, `adc9328`) and preservation-related
  history.

## Protocol and lineage findings

### Exact five-dataset MI protocol

The selection manifest and MI registry agree on exactly five datasets, indices 0–4, seeds
42–46, `IterativeImputer(estimator=BayesianRidge(), max_iter=10,
sample_posterior=True)`, the ten frozen predictors, outcome exclusion from the imputation
matrix, pool N=7,768, complete-case N=7,153, and 615 excluded participants. The five static
MI dataset hashes are distinct and match the registry. Diagnostic files confirm zero missing
values after imputation.

The static datasets were fit on the full pool and are explicitly documented as diagnostic-only.
The available MI modeling source (`mi_02_black_subgroup_comparison.py`) instead embeds a fresh
imputer inside each CV training fold. This is the correct leakage-safe pattern for its
CV-OOF comparison, but it is not a source implementation of the reported MI conformal run.

### Fold-embedded leakage safety

`mi_02_black_subgroup_comparison.py` uses `Pipeline`/`ColumnTransformer` and fits
`IterativeImputer` within each fold; it does not load or reference the locked test set.
This supports leakage safety for the recorded MI CV-OOF comparison. The Phase 5 MI conformal
tables claim expanded proper training (N=4,620), fixed calibration (N=1,002), and test
(N=2,146), but no MI conformal script, MI refit model, MI calibration-score file, or
per-participant MI prediction-set file is present. Therefore fold-embedded safety for the
reported conformal execution is **not independently demonstrated**.

### Comparator fidelity

The complete-case authority is internally coherent: Phase 6 refits the five frozen model
families on proper-train N=4,005, calibrates on N=1,002, uses the standard score
`1 - P(y=true_class | x)`, applies the finite-sample corrected order statistic, and evaluates
once on the locked test N=2,146. The Phase 5 MI tables use the same nominal 90% target, score
definition, Wilson 95% intervals, five model families, and fixed partition counts as stated
in the manifest. This is adequate for a descriptive comparator, subject to the missing MI
execution artifacts noted above.

### Per-imputation calculations and pooling

The overall table has 25 rows (5 imputations × 5 models); the subgroup table has 375 rows
(5 × 5 × 15 categories); the intersectional table has 650 rows (5 × 5 × 26 cells). Coverage
equals `covered_n / n` to floating-point precision in all three tables, and MI-minus-complete-
case differences equal the recorded arithmetic differences. The uncertainty table reports
means, ranges, and between-imputation SDs only. No unsupported pooled inferential estimate is
presented. This is methodologically appropriate for the stated descriptive comparison, but
does not establish equivalence.

### Subgroups, intersectional cells, and sparse cells

All four frozen dimensions are represented: sex (2 categories), race/ethnicity (6), age (3),
and BMI (4). Precision tiers and counts are retained, including insufficient-evidence
Underweight cells. The intersectional table contains exactly the 26 pre-specified
Sex×Race/Ethnicity, Sex×Age, and Sex×BMI cells per imputation/model; it does not invent
Race×BMI or Race×Age cells. Intersectional rows are labeled exploratory and uncorrected.
Subgroup rows contain Wilson intervals and per-imputation BH-FDR fields; no subgroup result is
treated as conditional conformal validity.

### Locked-test order and runtime proof

The manifest asserts that selection preceded test access, records the expected locked-test
hash `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779`, and states one
official evaluation. The locked-test file currently matches that hash, and the complete-case
authority independently preserves the same test partition. However, there is no MI conformal
runtime event log or executable source establishing the asserted order.

There is also a provenance warning: filesystem mtimes show the five MI conformal CSVs at
23:31:12 local time and the manifest/lineage files at approximately 23:33:57/23:33:58,
whereas the manifest's internal `created_utc` converts to approximately 23:30:24 local.
This inconsistency is not proof of test leakage, but it means runtime ordering is only
partially supported by self-authored metadata and cannot be independently proven.

### Model/conformal artifacts and source availability

The complete-case Phase 6 model and calibration artifacts exist and are hash-registered.
No corresponding MI conformal model artifacts, calibration scores, test prediction sets, or
source script are present. The three available MI scripts cover full-pool diagnostics,
fold-embedded CV-OOF MI-versus-complete-case discrimination, and Non-Hispanic Black
sensitivity inference; none writes the Phase 5 MI conformal output filenames. The two hashes
listed under `outputs_sha256` cover only the overall and subgroup CSVs; intersectional,
uncertainty, versus-complete-case, manifest, and lineage files are not hash-listed there.
These are material reproducibility and lineage limitations.

## Results verified from saved tables

| Model | MI coverage range | MI descriptive mean | Complete-case coverage | Mean difference |
|---|---:|---:|---:|---:|
| Logistic | 90.587–91.100% | 90.867% | 90.820% | +0.047 pp |
| Random forest | 88.444–89.655% | 89.077% | 89.609% | −0.531 pp |
| XGBoost | 88.583–89.609% | 89.087% | 88.117% | +0.969 pp |
| LightGBM | 88.910–89.935% | 89.562% | 89.609% | −0.047 pp |
| MLP | 88.956–89.981% | 89.450% | 89.189% | +0.261 pp |

The arithmetic was independently checked from the saved counts. BMI-Obese coverage is below
the 90% target for every model and every imputation; this is a persistent subgroup reliability
finding, not evidence that the overall MI conclusion fails. Non-Hispanic Black coverage is
reported for all five imputations and remains in the model-specific ranges documented in the
report (approximately 87.1–89.8%). No formal pooled Black-subgroup claim is made.

The saved tables therefore support: (1) the direction and scale of overall MI changes are
small-to-moderate and model-dependent; (2) the major BMI-Obese undercoverage pattern persists;
and (3) the MI results are descriptively close to the complete-case authority. They do not
support equivalence, superiority, causal explanation, or population-level conditional
coverage.

## Limitations and impact on the main conclusion

1. **No executable MI conformal source is present.** Impact: prevents independent rerun and
   exact verification of model fitting, imputation placement, threshold calculation, and test
   scoring. It weakens reproducibility but does not contradict the arithmetic of the saved
   outputs.
2. **No MI conformal model, calibration-score, or per-participant prediction-set artifacts.**
   Impact: prevents independent audit of per-imputation score/threshold/set construction and
   weakens the independent-evaluation determination. It does not change the observed table
   comparisons.
3. **No runtime event log.** Impact: the manifest's one-touch and pre-test selection claims
   are not independently time-proven.
4. **Manifest/output timestamp inconsistency.** Impact: further downgrades locked-test order
   from proven to partially supported; it is not evidence of contamination by itself.
5. **No formal MI-versus-complete-case comparative inference or equivalence test.** Impact:
   the conclusion must remain descriptive “consistent with,” not “equivalent,” “unchanged,”
   or “statistically indistinguishable.”
6. **No Rubin-style pooling for prediction sets.** Impact: between-imputation summaries are
   descriptive only and cannot be interpreted as a pooled inferential estimate.
7. **Wilson intervals and binomial tests describe test-set proportions, not exchangeability
   proof or conditional subgroup validity.** Impact: subgroup coverage remains precision-
   limited and exploratory.
8. **Sparse and insufficient-evidence cells are retained.** Impact: intersectional and
   Underweight observations cannot support stable subgroup conclusions; they do not affect
   the overall five-model descriptive comparison.
9. **MI protocol specifics were resolved by Amendment #12 rather than fully specified in the
   original Phase 2 documents.** Impact: the executed values are traceable, but prospective
   protocol certainty is weaker than for a fully frozen primary analysis.
10. **MI is an exploratory sensitivity analysis, not the primary complete-case analysis.**
    Impact: it cannot replace the primary result or establish external validity.

None of these limitations reverses the main descriptive conclusion from the saved tables.
Together they require decision **B**, rather than A, and prohibit stronger equivalence or
confirmatory language.

## Historical phrase preservation

The historical MI report at commit `adc9328` retains its prior wording, including
`MI ROBUSTNESS PARTIAL` and `MULTIPLE IMPUTATION COMPLETE — NON-HISPANIC BLACK ROBUSTNESS
ASSESSED`. This audit does not silently rewrite that history. The current
`PHASE5_MI_CONFORMAL_REPORT.md` and selection manifest use the exact allowed conclusion:

> **MI CONFORMAL RELIABILITY IS CONSISTENT WITH COMPLETE-CASE RESULTS**

## Preservation determination

The Phase 0–4, Phase 7, primary/master, external, and prior MI artifacts inspected
remain in their original paths. The Phase 5 MI conformal outputs are in a distinct namespace
and were not merged into complete-case Phase 6 outputs. This audit did not alter any of those
artifacts.

