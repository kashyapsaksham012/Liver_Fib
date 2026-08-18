# Elastography Eligibility Protocol (Phase 2D)

**Generated:** 2026-08-18

## Three Distinct Concepts (kept separate throughout, per instruction)

1. **Measurement available** = `LUXSMED` is non-missing (`COHORT_1_NONMISSING_LUX`, N=9,700 in the full
   Phase 1 cohort). Any exam completeness, including Partial (`LUAXSTAT==2`) exams that still produced a
   numeric median.
2. **Measurement quality-valid** = `LUAXSTAT==1` (`COHORT_2_QUALITY_VALID`, N=9,023). The NHANES-official
   "Complete" definition, verified against the live P_LUX codebook in Phase 1
   (`documentation/source_metadata/lux_quality_rule_source.md`): fasting ≥3h, ≥10 complete stiffness
   measures, and stiffness IQR/median (`LUXSIQRM`) <30%.
3. **Clinical fibrosis classification** = whether the quality-valid `LUXSMED` value meets a chosen
   clinical severity threshold (e.g. ≥8.2 kPa for significant fibrosis). This is entirely separate from
   (1) and (2) and is addressed in `primary_outcome_definition.md`.

## Decision

> **PRIMARY eligibility rule: `LUAXSTAT == 1` (quality-valid).**

**Rationale:** NHANES designed this flag specifically to certify exam reliability against known VCTE
failure modes (insufficient fasting, too few valid measures, excessive measurement variability). Using it
directly reuses NHANES's own quality-assurance computation rather than re-deriving an equivalent rule from
`LUANMVGP`/`LUXSIQRM` independently (which would risk disagreeing with NHANES's own fasting-time
component, for which this dataset has no standalone variable). This was already established and cited in
`documentation/source_metadata/lux_quality_rule_source.md` during Phase 1 closure; Phase 2 confirms it as
the primary rule rather than merely documenting it as an option.

> **SENSITIVITY eligibility rule: non-missing `LUXSMED`, any completeness (CAND_2 sensitivity cohort).**

**Rationale:** Tests whether admitting the 677 additional Partial-exam participants (who still produced a
numeric stiffness value) meaningfully changes the analysis. If results are materially unchanged, this
strengthens confidence that the quality-valid restriction is not overly conservative; if they differ, it
flags a genuine measurement-quality effect worth reporting.

## Application

- The primary analytical population (`primary_cohort_decision.md`) applies `LUAXSTAT==1` at the exam
  level BEFORE age or predictor-completeness filters are applied, consistent with the frozen Phase 1
  cohort-flow ordering (Section F, Step 1b in `PHASE1_DATA_ASSEMBLY_REPORT.md`).
- No participant is excluded from the eligible pool based on their `LUXSMED` value itself (that would be
  outcome-based selection, not eligibility) — only on exam completeness/quality flags, which are
  determined independently of the resulting stiffness value.
