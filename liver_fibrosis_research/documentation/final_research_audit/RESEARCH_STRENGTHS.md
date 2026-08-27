# RESEARCH STRENGTHS

Read-only audit, 2026-08-27. Only evidence-supported strengths. Methodology is not converted into
claims of clinical validity.

---

## 1. Genuinely frozen primary design

The outcome threshold (`LUXSMED ≥ 8.2 kPa`, from a 2024 VCTE-vs-MRE meta-analysis Youden cutoff)
and the ten predictors were fixed **before any model was trained**, and the protocol freeze is
recorded (`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`,
`documentation/phase2/primary_outcome_definition.md`,
`results/tables/phase2_predictor_registry.csv`). The BMI-investigation Phase 0 lineage audit
re-verified the frozen state against SHA-256 hashes with no discrepancy
(`PHASE0_LINEAGE_AUDIT.md`).

## 2. Multiple model families compared head-to-head with multiple-testing control

Five families (linear, three tree ensembles, neural net) evaluated on one locked test set with
Benjamini–Hochberg FDR on 10 pairwise comparisons, and a project-wide 182-test pooled FDR
(`results/tables/phase3_model_comparison_fdr.csv`,
`results/statistics/pooled_fdr_corrected_results.csv`). The conclusion is stated as
indistinguishability, not a spurious winner.

## 3. Out-of-fold-only calibration with a locked test touched once per phase

Platt parameters fit on OOF predictions only, frozen, then applied once to the locked test
(`src/phase4_05_recalibration.py`). The locked test is touched exactly once at each phase that
needs it (Phase 3 discrimination, Phase 4 recalibration, Phase 5 fairness, Phase 6/7 coverage),
with a further 80/20 split of the training partition for the conformal proper-train/calibration
architecture. No nested double-dipping of the locked test was found in this or prior audits
(`MASTER_END_TO_END_RESEARCH_REPORT.md` §F, `results/end_to_end/test_set_contamination_audit.md`,
8/8 contamination pathways PASS).

## 4. An explicit, pre-specified fairness audit that produced a real negative-for-the-model finding

Fairness dimensions (sex, race/ethnicity, age band, BMI band), disparity metric, bootstrap CIs,
and within-family FDR were all pre-specified (`documentation/phase2/fairness_subgroup_protocol.md`).
The audit surfaced a large, reproducible BMI sensitivity deficit that the study did not
minimise — and correctly separated it from the cohort-level differential-missingness fact.

## 5. Uncertainty quantification that exposed what AUC and aggregate calibration hid

Split conformal prediction (`documentation/phase2/uncertainty_protocol.md`,
`src/phase6_*`) is the mechanism by which the study's central contribution emerges: a model can
look acceptable on discrimination and aggregate calibration and still under-cover identifiable
subgroups (BMI-Obese 76.8–82.3%, Age-60+ 81.1–85.6%; `results/uncertainty/subgroup_coverage.csv`).

## 6. Mechanism-focused BMI investigation that reproduced its own prior result first

The BMI follow-up (Phases 0–7) began by independently **reproducing** the disparity
(`PHASE1_REPRODUCTION.md`: counts exact, inference within rounding, all 5 models REPRODUCED)
before diagnosing it (`PHASE2_DIAGNOSTIC_REPORT.md`: score-distribution + threshold mechanism,
explicitly non-causal) and then honestly reporting **NO ACCEPTABLE MITIGATION IDENTIFIED**
across a structured set of candidates.

## 7. Mitigation was tested rigorously and reported honestly

Mondrian (Project Phase 7), BMI thresholding / BMI-Platt / BMI×Age thresholds / combined
(corrected Phase 3), subgroup calibration (corrected Phase 4), group Youden thresholds, Equal
Opportunity, XGBoost retuning, joint conformal (Methods b/c, M4b), and conformal selective
deferral (Amendment #17) were all evaluated against pre-declared multi-metric gates. Partial
successes (Mondrian 5/9; a re-run reaching 5/5 only by over-covering) and failures (everything
else, including selective deferral) are labelled as such, and a documented tolerance breach
(XGBoost +5.27 pp) is disclosed rather than smoothed over. The selective-deferral analysis stopped
at the pre-registered gate on the calibration partition and did not touch the locked test — and
produced a genuine mechanistic result (the under-coverage is confidently-scored wrong singletons,
so post-hoc deferral cannot help; a training-time fix is indicated).

## 8. Sensitivity analyses triangulate the core findings across independent axes

Three independent cohort/threshold perturbations — 8.0-kPa relabel, CAND_2 relaxed elastography
(fresh fit), CAND_3 fasting-extended 12-predictor (fresh fit) — plus a fold-embedded targeted MI
and a full-pipeline 8.0-kPa re-run. The BMI-Obese disparity is stable 15/15; the discrimination
and calibration stories reproduce (`results/sensitivity/primary_vs_sensitivity_comparison.csv`).

## 9. Threshold robustness was tested at the full-pipeline level

The BMI-investigation Phase 6 re-ran OOF Platt and split conformal at 8.0 kPa and reached an
honest verdict ("SOME MAJOR FINDINGS ARE THRESHOLD-SENSITIVE") rather than asserting invariance.

## 10. Preservation and audit discipline

Superseded and invalid work (historical Phase 3/4, KNN-AFCP, N0=100, leakage-prone early
diagnostic scripts) is preserved on disk and explicitly demarcated
(`SUPERSEDED_INVALID_REGISTER.md`, `CHANGELOG_RESEARCH.md`). Multiple independent audit passes
(BMI-investigation Phase 0; end-to-end; contamination audit;
`INDEPENDENT_VERIFICATION_ATTESTATION_2026-08-25.md`; the `final_research_state` consolidation;
this audit) cross-check the numbers, and documented conflicts are labelled
`CONFLICT UNRESOLVED IN REPOSITORY` rather than silently resolved.

## 11. Reproducibility infrastructure

Frozen environment / package locks, seed recording, split ID files, model lineage
(`results/tables/model_lineage.csv`), result-to-script-to-data lineage
(`results/tables/data_and_result_lineage.csv`), frozen file hashes
(`results/diagnostics/frozen_file_hashes.json`), and an internal validation suite reporting
44/44 tests passed (`documentation/audit_reports/internal_validation_results.csv`).

## 12. Clinically grounded predictor set and interpretability

Ten low-cost routine primary-care variables; the top four features (ALT, AST, BMI, Age) are
consistent across all five families and physiologically sensible
(`results/tables/interpretability_permutation_importance.csv`).

---

**Bottom line:** the methodological rigor, transparency, and self-auditing are the strongest
aspects of this work and are exactly what make its negative findings (subgroup coverage failure,
no acceptable BMI mitigation) credible.
