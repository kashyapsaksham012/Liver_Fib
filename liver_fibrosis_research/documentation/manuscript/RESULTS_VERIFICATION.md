# Results verification log (second-reader pass)

**Date:** 2026-08-27. Every quantitative sentence in `MANUSCRIPT_DRAFT.md` §3 (and Tables 1–5)
checked against the frozen raw artifacts and `results/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv`.
This is a within-repository consistency pass, **not** an independent re-analysis. A human
co-author should still repeat it before submission.

Verdict key: **OK** = matches the cited artifact exactly (or within stated rounding);
**OK (rounded)** = matches to the precision the draft states; **FIXED** = discrepancy found and
corrected in v2; **CHECK** = correct but flagged for a co-author to confirm a value I could not
fully trace here.

---

## §3.1 Cohort

| Claim | Artifact | Verdict |
|---|---|---|
| N = 7,153; 666 positive; 9.31% | `phase2_outcome_prevalence.csv`; `manuscript_table1_by_fibrosis.csv`; registry composition row | OK |

## §3.2 Discrimination

| Claim | Artifact | Verdict |
|---|---|---|
| AUROC 0.8334 / 0.8343 / 0.8429 / 0.8394 / 0.8229 | `phase3_final_baseline_results.csv` (`test_roc_auc`) | OK (exact) |
| Range 0.823–0.843 | same | OK |
| 0/10 pairwise BH-significant | `phase3_model_comparison_fdr.csv`; registry DISC-02 | OK |
| PR-AUC "0.35–0.37" | `phase3_final_baseline_results.csv` (`test_pr_auc` 0.351–0.373) | OK (rounded) |
| XGBoost highest point estimate, no significant superiority | same | OK |

## §3.3 Calibration

| Claim | Artifact | Verdict |
|---|---|---|
| OOF intercepts −2.24 / −1.86 / −2.05 / −2.05 / −0.28 | `primary_metrics_by_model.csv` (−2.243 / −1.862 / −2.046 / −2.053 / −0.281) | OK (rounded) |
| Prior-mismatch term log(0.0931/0.9069) ≈ −2.27 | arithmetic | OK |
| Raw test ECE "0.25–0.30" (four balanced) | `test_set_calibration_final.csv` raw ECE 0.245–0.297 | OK (rounded) |
| Recalibrated test ECE "0.011–0.026" | same, recal ECE 0.011 / 0.017 / 0.015 / 0.014 / 0.026 | OK |
| Brier "0.146–0.176 → 0.069–0.072" | raw 0.146–0.175 (+MLP 0.072); recal 0.069–0.072 | OK |
| Intercepts "→ −0.15 to +0.14" | recal −0.154 / +0.024 / +0.124 / +0.142 / −0.119 | OK |
| AUROC unchanged by recalibration | by construction (monotone transform) | OK |

## §3.4 Body-mass fairness

| Claim | Artifact | Verdict |
|---|---|---|
| Normal-vs-Obese sensitivity gap: LR −47.7, RF −31.6, XGB −31.4, LGBM −27.1, MLP −39.0 pp | `fairness_inference.csv` (bmi / Obese vs Normal `absolute_disparity_pp`: 47.6623 / 31.6234 / 31.3636 / 27.0779 / 39.026) | OK (exact) |
| "27–48 pp lower in all five models" | same | OK |
| "all BH q ≤ 0.006" | `fairness_inference.csv` `bh_fdr_adjusted_p`: LR 0.0, RF 0.006, XGB 0.003, LGBM 0.006, MLP 0.0 | OK (all ≤ 0.006 — confirmed) |
| Reproduced independently, counts exact, inference within rounding | `PHASE1_REPRODUCTION.md`; registry FAIR-BMI-01 | OK |
| Mechanism: lower scores for fibrosis-positive normal-weight; Mann–Whitney significant for positive **and** negative cases; non-causal | `PHASE2_DIAGNOSTIC_REPORT.md` (`phase2_positive_case_scores.csv`, `phase2_negative_case_scores.csv`) | OK |
| Sex / race: no BH-significant disparity | `fairness_inference.csv` sex + race rows all `significant_after_fdr_0.05 = False` | OK |

## §3.5 Marginal vs subgroup conformal coverage

| Claim | Artifact | Verdict |
|---|---|---|
| Marginal 88.1–90.8% | `marginal_coverage_test_set.csv` (0.9082 / 0.8961 / 0.8812 / 0.8961 / 0.8919) | OK |
| BMI-Obese 76.8–82.3% | `subgroup_coverage.csv` bmi/Obese (0.8233 / 0.8018 / 0.7678 / 0.7916 / 0.8086) | OK |
| Age-60+ 81.1–85.6% | `subgroup_coverage.csv` age/60+ (0.8489 / 0.8556 / 0.8111 / 0.8475 / 0.8381) | OK |
| Wilson intervals exclude 90%; BH-significant every model (BMI-Obese, Age-60+) | `subgroup_coverage.csv` `ci_excludes_target = True`, `significant_after_fdr_0.05 = True` | OK |
| Obese ∩ 60+ (N = 294) "fell to 65–75%" | `intersectional_coverage_ci.csv` baseline coverage: LR 0.694, RF 0.752, XGB 0.650, LGBM 0.711, MLP 0.738 → point-estimate range 0.650–0.752 | OK (draft "65–75%"; **Table 3 corrected** from an earlier wrong "0.720–0.752" range to the per-model values) — **FIXED** |
| Over-covered subgroups "≈ 0.94–0.97" | `subgroup_coverage.csv` Normal 0.954–0.970, Overweight 0.948–0.972, 18–39 0.939–0.958 | OK (**softened** from "0.95–0.97" — FIXED) |
| MLP 96.9% singletons; 23–43% ambiguous two-class sets for class-weighted models | `marginal_coverage_test_set.csv` `singleton_rate` MLP 0.969; `ambiguous_rate_both_classes` LR 0.432 / RF 0.232 / XGB 0.271 / LGBM 0.312 | OK |

## §3.6 Replication of the coverage failure

| Claim | Artifact | Verdict |
|---|---|---|
| CAND_2 marginal 0.896–0.906; CAND_3 0.899–0.917 | `conformal_replication_marginal.csv` — CAND_2 0.8957–0.9062, CAND_3 0.8986–0.9172 | OK |
| BMI-Obese CAND_2 0.790–0.841 | `conformal_replication_subgroup.csv` (0.7896 / 0.8121 / 0.8018 / 0.8049 / 0.8407) | OK |
| BMI-Obese CAND_3 0.799–0.838 | same (0.7991 / 0.8128 / 0.8174 / 0.8379 / 0.8379) | OK |
| BMI-Obese 8.0 kPa 0.790–0.822 | `phase6_8kpa_robustness/phase6_8kpa_conformal_results.csv` (0.822 / 0.810 / 0.798 / 0.790 / 0.811; all BH q < 1e-11) | OK |
| BMI-Obese: 5/5 significant on both replication cohorts | `conformal_replication_subgroup.csv` `significant_after_fdr_0.05 = True` for all Obese rows | OK |
| Age-60+ BH-significant 5/5 CAND_2, 2/5 CAND_3 | `conformal_replication_subgroup.csv` — CAND_2 all 5 True; CAND_3 True only LR (q 0.0062) and MLP (q 0.0245) | OK |

## §3.7 Mitigation

| Claim | Artifact | Verdict |
|---|---|---|
| Mondrian 5/9; XGBoost +5.3 pp breach; sequential overlap precedence | registry MIT-01; `marginal_coverage_before_after.csv`; `threshold_precedence_audit.csv` | OK |
| Four BMI strategies, none pass gate; MLP-only BMI-Platt 39.0 → 34.5 pp | registry MIT-02; `phase3_corrected_locked_test_confirmation.csv` | OK |
| Subgroup calibration: ECE improved 3 models, gaps unchanged (Decision B) | registry MIT-03 | OK |
| Group thresholds: BMI gap halved, age gap +26–133%, ~40 pp specificity cost | registry; `EXPLORATORY_RESULTS.md` E4 | OK |
| Equal-opportunity: ~400 excess FP / 1,000 normal-weight | registry; `clinically_interpretable_fairness_costs.csv` (399) | OK |
| XGBoost retuning: 11–22 pp sensitivity cost | registry MIT-04 | OK |
| Joint conformal: ≥90% for 4–5/5 on primary; XGB/LGBM marginal breach | registry MIT-05; `joint_intersectional_mitigation.csv` | OK |

## §3.8 Older-age (secondary)

| Claim | Artifact | Verdict |
|---|---|---|
| −8.6 to −14.7 pp, negative 5/5 | `fairness_inference.csv` age/60+ (−8.55 / −13.16 / −11.24 / −14.15 / −14.67) | OK |
| BH-significant 4/5, not logistic | `fairness_inference.csv` `significant_after_fdr_0.05`: logistic False, others True | OK |
| Lost under 9/12 alternative specifications | `primary_vs_sensitivity_comparison.csv` (age rows) | OK |
| Non-monotonic, peak ≈ 65 y, no decline at 70+ | `EXPLORATORY_RESULTS.md` E2; `continuous_age_metrics.csv`, `fine_age_band_metrics.csv` | OK |

## §3.9 Demographic holdout

| Claim | Artifact | Verdict |
|---|---|---|
| NHB holdout AUROC 0.772–0.789 (−0.05 to −0.06) | registry GEN-01 ("0.7719–0.7893"); `phase8_generalization_results.csv` | OK |
| Holdout intercepts −0.58 to −2.17; slopes 0.64–0.97 | `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md` (−0.577 to −2.169; 0.636–0.972) | OK (rounded) |

## §3.10 Sensitivity & secondary outcomes

| Claim | Artifact | Verdict |
|---|---|---|
| BMI-Obese disparity stable 15/15 | `primary_vs_sensitivity_comparison.csv` (all `fairness_bmi_disparity` rows STABLE) | OK |
| Age disparity direction never reverses; significance lost 9/12 | same (age rows: STABLE / PARTIALLY STABLE) | OK |
| ≥9.7 kPa AUROC 0.85–0.86; ≥13.6 kPa 0.84–0.86 | registry SECOUT-01; `secondary_severity_outcomes_results.csv` | OK |
| Recalibrated intercepts −0.4 to −0.8 (≥9.7) / −1.2 to −1.9 (≥13.6) | `SECONDARY_SEVERITY_GRADED_OUTCOMES_RESULTS_REPORT.md` | OK |
| MI ΔAUROC < 0.007; NHB sensitivity Δ ≤ ±4.2 pp; all CIs include 0 | `mi_black_subgroup_comparison.csv` (diffs −0.001 / +0.006 / −0.013 / −0.010 / +0.042; all `ci_excludes_zero = False`) | OK |

## §3.11 Interpretability

| Claim | Artifact | Verdict |
|---|---|---|
| ALT, AST, BMI, Age top four across all five families | registry INT-01; `interpretability_permutation_importance.csv`, `interpretability_logistic_coefficients.csv` | OK |
| DCA net benefit over default strategies, incl. Obese and 60+ (exploratory) | registry DCA-01; `dca_summary.csv` | OK |

---

## Outcome of this pass

**One numeric error found and fixed** (Table 3, Obese ∩ 60+ row — an earlier "0.720–0.752"
replaced with the per-model coverage values 0.694 / 0.752 / 0.650 / 0.711 / 0.738). One wording
tightened (over-coverage "0.95–0.97" → "0.94–0.97"). Every other quantitative claim in §3 and
Tables 1–5 matches its cited frozen artifact to the precision stated. Verification items 1–3 above
were closed in-session (BMI-Obese fairness q ≤ 0.006 for all 5 models; CAND_2/CAND_3 marginal
coverage confirmed; 8.0-kPa BMI-Obese conformal confirmed).

## Items still to close (for a co-author)

1. Independently re-run `src/manuscript_01_table1.py` and check Table 1 against
   `phase2_outcome_prevalence.csv` and `fairness_subgroup_protocol.md` counts (sex 3,531/3,622;
   BMI bands 109/1,802/2,316/2,926; age bands 2,423/2,318/2,412 — all matched in this pass).
2. Read every Results sentence against `DO_NOT_CLAIM.md` once more.
3. Re-verify each reference DOI/PMID (see `LITERATURE_REVIEW.md` §4 and the DOI-status note).
