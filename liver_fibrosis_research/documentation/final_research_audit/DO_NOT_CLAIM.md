# DO NOT CLAIM

Read-only audit, 2026-08-27. Claims that the repository's evidence does **not** support. This
consolidates `documentation/final_research_state/DO_NOT_CLAIM.md` and adds items found in this
audit. Required missing-evidence tokens: `NOT FOUND IN REPOSITORY`,
`CONFLICT UNRESOLVED IN REPOSITORY`, `LINEAGE NOT FOUND IN REPOSITORY`.

---

## Fairness

1. **Do not claim the models are fair, unbiased, or equitable.** Sex and race/ethnicity showed
   no FDR-significant sensitivity/AUROC disparity in the primary complete-case test set, but BMI
   and age disparities are large and reproduced. "Universal fairness" is contradicted by the
   study's own primary finding.
2. **Do not claim BMI fairness was solved / mitigated / resolved.** Final status: **NO
   ACCEPTABLE BMI-SENSITIVITY MITIGATION IDENTIFIED** (`PHASE3_CORRECTED_MITIGATION_REPORT.md`).
3. **Do not claim subgroup calibration solved (or improved) BMI fairness.** Decision B: no
   acceptable subgroup-calibration improvement; classification decisions unchanged
   (`PHASE4_CORRECTED_FINAL_AUDIT_REPORT.md`).
4. **Do not claim Project Phase 7 resolved the BMI classification (sensitivity) disparity.**
   Phase 7 targets conformal coverage only, and only partially (5/9).
5. **Do not claim Age-60+ significance in 5/5 models.** It is 4/5; Logistic is not
   FDR-significant.
6. **Do not claim a monotone "older is worse" age gradient.** The age effect is non-monotonic
   (peak ≈65 y).
6a. **Do not present the Age-60+ *sensitivity* disparity in the abstract or as a co-headline with
    the BMI finding.** Framing decision 2026-08-27 (`MANUSCRIPT_FRAMING_GUIDANCE.md`): it is a
    secondary observation (Results body + Limitations only). The Age-60+ *conformal
    under-coverage* is separate and is retained at full strength.

## Calibration

7. **Do not claim universal or subgroup-level calibration adequacy.** OOF Platt fixes *aggregate*
   calibration; subgroup calibration metrics differ and subgroup conformal coverage still fails.

## Conformal

8. **Do not claim conditional / subgroup / intersectional conformal validity.** Only *marginal*
   coverage is guaranteed; BMI-Obese, Age-60+, and the Obese∩60+ intersection all under-cover.
9. **Do not claim any conformal mitigation method (Mondrian, joint, M4b, AFCP) achieves subgroup
   or intersectional validity.** All either miss targets, breach the marginal tolerance, or fail
   temporally.
10. **Do not claim faithful AFCP superiority.** **Do not cite the KNN-AFCP result at all**
    (INVALID). C3 adjudicated 2026-08-27 (`CONFLICT_ADJUDICATIONS.md`): faithful AFCP is
    EXPLORATORY; no AFCP-superiority or AFCP-adequacy claim is permitted.
11. **Do not present the exploratory joint mitigation as a primary result** or as a solution to
    the intersectional coverage problem. C2 adjudicated 2026-08-27: executed 2026-08-24,
    EXPLORATORY only.
12. **Do not report N0=100 as the M4b parameter** (SUPERSEDED by N0=0).
13. **Do not use the conformal-coverage numbers or the "Normal-BMI under-covers" statement from
    `documentation/MASTER_RESEARCH_RESULTS.md`** (items 26–27, §3.5) — they are erroneous
    (conflict C1). Use `results/uncertainty/subgroup_coverage.csv` +
    `marginal_coverage_test_set.csv` + `MASTER_END_TO_END_RESEARCH_REPORT.md`: BMI-**Obese**
    under-covers (76.8–82.3%).

## Multiple imputation

14. **Do not claim MI and complete-case results are equivalent** (no equivalence test; BH
    q=0.978 is a correction-ceiling artifact).
15. **Do not report pooled (Rubin) inferential estimates for the MI conformal work** — the
    protocol defines none.
16. **Do not cite the MI conformal tables as load-bearing evidence** —
    `LINEAGE NOT FOUND IN REPOSITORY`; descriptive-only use.
17. **Do not extend the targeted NHB MI conclusion to the whole cohort or other subgroups.**

## Threshold

18. **Do not claim 8.0 kPa and 8.2 kPa are statistically indistinguishable** (never tested).
19. **Do not replace the primary 8.2-kPa analysis with 8.0-kPa results.** 8.0 kPa is a
    sensitivity analysis; the full re-run's verdict is "SOME MAJOR FINDINGS ARE
    THRESHOLD-SENSITIVE".

## Discrimination

20. **Do not claim XGBoost (or any family) is the best / superior model** — 0/10 pairwise
    comparisons significant after FDR.
21. **Do not claim strong, excellent, or clinical-grade discrimination.** AUROC ≈0.82–0.84,
    PR-AUC ≈0.35, at 9.31% prevalence.

## Validation & transportability

22. **Do not claim external validation.** None was performed; no compatible cohort exists.
23. **Do not claim full temporal replication.** Status: **PARTIAL TEMPORAL REPLICATION**.
24. **Do not call the Non-Hispanic Black holdout (Phase 8) external validation.** It is a
    within-NHANES demographic holdout.
25. **Do not call the NHANES 2021–2023 temporal work external validation.**
26. **Do not claim the models are deployment-ready or clinically validated.**

## Causal & mechanistic

27. **Do not make causal claims** about why any disparity exists. The BMI mechanism is a "mixed
    empirical mechanism" (score-distribution + threshold), explicitly non-causal
    (`PHASE2_DIAGNOSTIC_REPORT.md`).
28. **Do not claim a proven BMI×Age interaction** — the pattern is "compatible with effect
    modification" only; young Normal-BMI cells are unstable.
29. **Do not attribute the temporal performance drop to a specific cause.** The root-cause
    analysis supports only **SUPPORTED ASSOCIATIONS** (prevalence increase, composition/fairness
    drift), and explicitly `NOT SUPPORTED` for any single-cause mechanism
    (`PHASE3_5_ROOT_CAUSE_DRIFT_TO_PERFORMANCE_REPORT.md`).

## Cohort scope

30. **Do not report CAND_4 (all-ages) performance** — constructed only, `NOT_EXECUTED`. C4
    adjudicated 2026-08-27: DISTINCT — EXPLORATORY — UNEXECUTED (Amendment #14).
31. **Do not report advanced-fibrosis (≥9.7 kPa) or cirrhosis (≥13.6 kPa) results as deployable
    severity-staging model performance.** Executed 2026-08-27 as a **relabel-only descriptive
    pass** (Amendment #15) — discrimination and calibration only, on frozen 8.2-kPa models; no
    per-outcome retraining or recalibration. Report only at that scope
    (`SECONDARY_SEVERITY_GRADED_OUTCOMES_RESULTS_REPORT.md`).
32. **Do not describe the BMI-Obese ∩ Age-60+ overlap as ~62% of the cohort** — it is 294 people
    (13.7% of the test set); 62% is the *union*.

## Historical / invalid

33. **Do not cite the historical baseline AUROCs 0.8407/0.8354/0.8348/0.8184** or CAND_2/CAND_3
    prevalences 9.49%/9.13% — transcription errors, SUPERSEDED.
34. **Do not report the historical BMI-investigation Phase 3 or Phase 4 conclusions** —
    SUPERSEDED by the corrected runs.

## Data / provenance discipline

35. **Do not invent missing p-values, confidence intervals, subgroup values, or lineage.** Use
    the exact tokens `NOT FOUND IN REPOSITORY`, `CONFLICT UNRESOLVED IN REPOSITORY`,
    `LINEAGE NOT FOUND IN REPOSITORY`.
