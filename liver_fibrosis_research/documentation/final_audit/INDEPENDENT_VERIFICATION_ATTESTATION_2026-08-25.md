# Independent Verification Attestation — 2026-08-25

SECONDARY / AUDIT documentation. No pipeline code modified, no model retrained or refit, no new
test-set scoring performed. This pass independently re-read primary frozen artifacts directly
(not via any intermediary summary) and cross-checked every headline number cited in the
end-to-end reports.

## 1. Scope of direct verification (all values below read from the raw files themselves)

| Claim | Primary artifact re-read | Match? |
|---|---|---|
| Cohort flow 10,409 → 9,700 → 9,023 → 7,768 pool → 7,153 complete-case; merge row-preservation invariant at 10,409 | `PHASE1_DATA_ASSEMBLY_REPORT.md` §D–F | Yes |
| Baseline test AUCs: LR 0.8334 [0.8021–0.8610], RF 0.8343, XGB 0.8429 [0.8123–0.8693], LGBM 0.8394, MLP 0.8229; Youden thresholds 0.5173/0.4499/0.4108/0.4988/0.1065 | `results/tables/phase3_final_baseline_results.csv` | Yes |
| No pairwise AUC difference significant after per-family BH-FDR (family=10) | `results/tables/phase3_model_comparison_fdr.csv` | Yes |
| OOF calibration intercepts −2.243/−1.862/−2.046/−2.053/−0.281 | `results/calibration/primary_metrics_by_model.csv` | Yes |
| Test raw vs recalibrated intercepts (raw −2.260…−0.435 → recal −0.154…+0.142); Brier 0.145–0.175 → 0.069–0.071; ECE 0.245–0.297 → 0.011–0.017 | `results/calibration/test_set_calibration_final.csv` | Yes |
| Fairness disparities incl. Normal-BMI deficits 27.1–47.7 pp (FDR-sig all 5 models); Age-60+ deficits FDR-sig in 4/5 (LR exception, p_fdr=0.195) | `results/fairness/fairness_inference.csv` (all 55 rows) | Yes |
| Marginal conformal coverage 88.12–90.82%; mean set sizes 0.97–1.43; MLP empty-set rate 3.12% | `results/uncertainty/marginal_coverage_before_after.csv`, `subgroup_coverage.csv` | Yes |
| Sequential mitigation: intersection baseline 64.97–75.17% → post 75.85–84.35%, all post CIs < 90% | `results/mitigation/test_set_mitigation_final.csv`, `results/uncertainty/intersectional_coverage_ci.csv` | Yes |
| Joint mitigation (exploratory): intersection 90.8–94.9% post, CIs ≥ 90% for 5/5; tolerance breach XGB +6.80pp, LGBM +5.50pp; joint calibration cell N=138 (30 pos / 108 neg) | `results/mitigation/joint_intersectional_mitigation.csv` | Yes |
| NHB holdout AUC 0.7719–0.7893 [CIs], prevalence 9.90%; covariate shifts BMI SMD +0.25, albumin −0.44 | `results/validation/phase8_generalization_results.csv`, `phase8_population_shift.csv` | Yes |
| Pooled registry N=182 tests across 7 families; 83 raw-significant → 75 after pooled BH-FDR; XGB-vs-MLP pooled adjusted p=0.0136; 18/20 BMI/Age subgroup tests remain significant | `results/statistics/pooled_test_registry.csv`, `pooled_fdr_corrected_results.csv`, `ITEMS_1_5_REFINEMENT_ADDENDUM.md` | Yes (registry row count and corrected file present; family table matches addendum) |
| MI sensitivity: NHB sensitivity change ≤ ±4.2pp, CI includes zero for 5/5; Class A (STABLE) ×4, Class F (INDETERMINATE, MLP) ×1; BH-adjusted p=0.978 all rows | `results/sensitivity/mi_black_subgroup_comparison.csv` | Yes |
| Sensitivity cohorts STABLE: CAND_2 relaxed-elastography AUC deltas +0.013…+0.034; CAND_3 fasting-extended −0.008…+0.011; 8.0 kPa threshold −0.009…−0.008 (test positives 218) | `results/sensitivity/primary_vs_sensitivity_comparison.csv`, `alternative_threshold_8p0kPa_results.csv` | Yes |
| Reliability extension: pooled ρ=0.4076 [0.1291, 0.6419] raw p=0.0020 but category-block permutation p=0.1195 (not confirmed); precision-filtered ρ=0.7043 p=2e-6 (labeled sensitivity only); DCA exceeds both reference strategies at population level and in BMI-Obese (N=883) / Age-60+ (N=741) | `RELIABILITY_EXTENSION_RESULTS_REPORT.md` §1, §8–10, §16–18 | Report-level verified; underlying CSVs present (`dca_summary.csv`, co-occurrence tables) |
| Diagnostics: BMI continuous gradient (no cutpoint artifact); Age non-monotonic (peak ≈65); group-specific thresholds shrink BMI gap to 10.4–16.1pp but widen Age gap; subgroup Platt recalibration changes coverage ≤ 0.68pp | `results/diagnostics/FINAL_THREE_DIAGNOSTICS_REPORT.md`, `stage0_decision_report.md`, `stage1_decision_report.md` | Report-level verified; CSVs present under `results/diagnostics/stage0/` |
| Contamination audit verdict: no test-label leakage in fresh D02/D04/D05 implementations; three superseded scripts had computation/labeling defects (documented, not hidden) | `results/diagnostics/TEST_SET_CONTAMINATION_AUDIT.md` | Yes |
| Interpretability: standardized logistic coefficients (BMI +0.746, Age +0.526 top-2); permutation importance top-2 = BMI/Age in RF/XGB/LGBM, BMI/AST then Age in MLP | `documentation/final_audit/P0_P1_REMEDIATION_ADDENDUM.md` P0-2; CSVs under `results/tables/interpretability_*.csv` | Yes |

## 2. Status-table conflicts found and their disposition

1. **`results/tables/final_research_status.csv` lists "Intersectional (joint) Mondrian mitigation:
   NOT EXECUTED."** Superseded by later execution on 2026-08-24 (`joint_intersectional_mitigation.csv`,
   generated 2026-08-24T12:42 UTC) documented in `ITEMS_1_5_REFINEMENT_ADDENDUM.md` Item 4 and
   reconciled narratively in `FINAL_SCIENTIFIC_STATUS_RECONCILIATION.md`. Per project convention the
   status CSV is not edited; readers must consult the reconciliation document.
2. **`COMPLETE_END_TO_END_LIVER_FIBROSIS_RESEARCH_REPORT.md` marked several artifacts "(uncommitted)"
   / "Untracked"** (compiled at HEAD=`1be2523`). Commit `142595d` has since tracked them (verified via
   `git ls-files`; 568 tracked files). Metadata annotations corrected inline on 2026-08-25 with a dated
   banner; no scientific claim was altered.
3. **UNRESOLVED between summary documents (flagged, not silently reconciled):** the older report marks
   D06 (Equal Opportunity post-processing) as UNVERIFIED and D07 (AFCP comparison) as BLOCKED/rule-
   violating (KNN approximation), while `stage1_decision_report.md` and the newer
   `COMPLETE_END_TO_END_EXPERIMENTAL_REPORT.md` treat D01–D08 as complete with a conditional freeze.
   The later documents govern the working narrative; the older flags are preserved above per the
   append-only record convention.

## 3. Result of this pass

Every headline number in the end-to-end reports that could be checked against a primary frozen
artifact matched exactly. No discrepancy in any scientific number was found between the reports and
the raw result files. Corrections made in this pass are limited to version-control metadata
(item 2) plus this attestation and a changelog entry.
