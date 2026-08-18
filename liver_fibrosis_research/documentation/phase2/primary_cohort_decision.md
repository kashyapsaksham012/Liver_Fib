# Primary Cohort Decision (Phase 2C)

**Generated:** 2026-08-18

## Candidates Evaluated

Four candidate cohorts were built by composing frozen Phase 1 canonical cohort masks
(`src/_cohorts.py`) — no new independent filtering logic was invented. Full comparison table:
`results/tables/phase2_candidate_cohort_comparison.csv`.

| Candidate | Definition | N | Outcome+ (8.2kPa) | Min race/ethnicity subgroup positive N |
|---|---|---|---|---|
| CAND_1 | Adult + LUAXSTAT==1 + broad labs complete + BMI/sex complete | 7,153 | 666 (9.31%) | 37 |
| CAND_2 | Adult + non-missing LUXSMED (any completeness) + broad labs + BMI/sex complete | 7,639 | 804 (10.52%) | 40 |
| CAND_3 | Adult + LUAXSTAT==1 + broad labs + fasting labs + BMI/sex complete | 3,582 | 319 (8.91%) | 16 |
| CAND_4 | LUAXSTAT==1 + broad labs + BMI/sex complete, NO adult restriction (ages 12-150) | 8,215 | 702 (8.55%) | 41 |

## Decision Criteria (per Phase 2C instructions — explicitly NOT predictive performance)

1. **Clinical appropriateness.** Liver fibrosis risk-prediction models in the reference literature (the
   VCTE meta-analysis and NHANES-specific studies cited in `phase1_references.md`) are adult-focused;
   pediatric/adolescent liver enzyme reference ranges, body composition, and fibrosis biology differ
   materially from adults, and the original research plan (`info.md`, Phase 4) explicitly assumes
   adult-only clinical reference values. → favors CAND_1/CAND_2/CAND_3 over CAND_4.
2. **Elastography quality.** `LUAXSTAT==1` is the NHANES-official, rigorously defined "Complete" exam
   status (fasting≥3h, ≥10 measures, IQRe/median<30% — verified in Phase 1). Using it as the primary
   eligibility rule minimizes measurement noise in the outcome label itself, which matters more for a
   fibrosis-severity measurement than for most simpler exam completions. → favors CAND_1/CAND_3/CAND_4
   over CAND_2.
3. **Predictor availability / clinical realism.** Broad routine labs (no fasting requirement) are
   obtainable at any clinical visit; fasting labs require a dedicated 8–24h-fast morning-session visit,
   a materially more restrictive real-world workflow. → favors CAND_1/CAND_2/CAND_4 over CAND_3.
4. **Sample size and subgroup outcome-positive counts.** CAND_1 (N=7,153, min subgroup+=37) is smaller
   than CAND_2/CAND_4 but the difference is modest (both add ~500-1,000 participants of lower measurement
   quality or including minors) and CAND_1's subgroup counts remain in the "exploratory-to-primary"
   feasibility band for every race/ethnicity group (see `phase2_statistical_feasibility.csv`). CAND_3
   (fasting-extended) has a materially worse profile (min subgroup+=16, "limited precision" tier),
   confirming the fasting restriction is too costly to be the *primary* architecture.
5. **Representativeness.** CAND_1 retains 100% of the P_LUX target adult population's demographic
   spread proportionally (no evidence of differential composition change beyond the modest 7.9%
   complete-case-vs-quality-valid-adult reduction — see `missing_data_protocol.md`).

## Decision

> **PRIMARY ANALYTICAL COHORT = CAND_1_QUALITYVALID_ADULT_BROAD (N=7,153).**
> Adults (≥18y), NHANES quality-valid elastography (`LUAXSTAT==1`), all 7 broad routine labs
> non-missing, BMI and sex non-missing.

> **SECONDARY COHORT = CAND_3_QUALITYVALID_ADULT_FASTING (N=3,582).**
> Adds fasting glucose and triglycerides. Used for the fasting-extended secondary predictor
> architecture (`phase2_broad_vs_fasting_design.csv`) — evaluated in parallel, not chosen between by
> performance.

> **SENSITIVITY COHORTS:**
> - CAND_2 (N=7,639) — tests robustness to the elastography-eligibility rule (`LUAXSTAT==1` vs.
>   non-missing-only).
> - CAND_4 (N=8,215) — tests robustness to the adult-only restriction.

This decision was made entirely on the five criteria above; no model was trained, tuned, or evaluated to
inform it, per non-negotiable rules 1 and 4.
