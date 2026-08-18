# Multiple-Comparisons Protocol (Phase 2U)

**Generated:** 2026-08-18 — decided in advance, not after seeing results.

## Scope of Multiple Comparisons Anticipated

Phase 3 will involve: 4 model families × 4 primary fairness dimensions (sex, race/ethnicity [6
categories], age [3 categories], BMI [4 categories], i.e. 16 subgroup categories) × multiple metrics
(sensitivity primary, plus AUC/specificity/calibration secondary) × 2 outcome definitions (primary +
8.0kPa sensitivity) — a genuinely large comparison space if treated naively.

## Decision

> **PRIMARY correction: False Discovery Rate (FDR) control via Benjamini-Hochberg**, applied within each
> pre-defined family of comparisons separately (NOT pooled across everything):
> 1. One FDR family per (model family × fairness dimension) combination, across that dimension's
>    subgroup-vs-reference disparity tests (e.g. all race/ethnicity-vs-White sensitivity-disparity tests
>    for one model, corrected together).
> 2. Calibration-metric comparisons form their own separate FDR family, not pooled with discrimination
>    comparisons.

**Rationale for FDR over Bonferroni:** Bonferroni is appropriate for a small number of pre-specified
confirmatory tests; with 4 model families × up to 6 subgroup comparisons per dimension, Bonferroni's
family-wise error control would be overly conservative given the fairness analysis is explicitly
exploratory-leaning for lower-N subgroups (`fairness_subgroup_protocol.md`) — FDR control better matches
the goal of flagging plausible disparities for interpretation rather than requiring near-certainty on each
individual comparison.

## Distinguishing Primary from Exploratory Comparisons (the other required distinction)

Per `statistical_analysis_plan.md`, PRIMARY fairness comparisons (the 4 dimensions' named categories) are
FDR-corrected as above. EXPLORATORY comparisons (26 intersectional cells, `phase2_intersectional_feasibility.csv`)
are analyzed and reported **without** formal multiple-comparison correction, but are explicitly labeled
"exploratory, uncorrected" in every table/figure — correcting them alongside primary comparisons would
either dilute power on the primary comparisons (if pooled) or create a false impression of confirmatory
rigor on cells already known to have limited-precision/insufficient-evidence sample sizes (if corrected
alone).

## Hierarchical Structure (summary)

1. **Confirmatory tier (FDR-corrected):** primary fairness dimensions, per model, per metric family.
2. **Exploratory tier (uncorrected, clearly labeled):** intersectional analyses, all-ages sensitivity
   cohort comparisons, secondary-threshold comparisons.

This structure is fixed now and will not be renegotiated after Phase 3 results are available.
