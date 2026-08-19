# Phase 6 Multiple-Imputation Claim Trace

**Generated:** 2026-08-19, live, per Part 2 of the Phase 6 Closure-Clarification task.

## 1. Exact file path

`PHASE6_UNCERTAINTY_RESULTS_REPORT.md`

## 2. Exact line location

Lines 210–231, section header `## 19. Deferred Analyses`. The specific disputed sentence
fragment ("much milder") is on **line 227**.

## 3. Exact quoted text (verbatim, unparaphrased)

> "- **Multiple-imputation**: also requires retraining, so it cannot be executed here either. But
> its *interpretive* relevance to Phase 6 is real and is stated explicitly, not silently
> dropped: the complete-case exclusion disparity (41.3% of exclusions vs. 25.0% of retained
> participants were Non-Hispanic Black, Phase 2 `missing_data_protocol.md`) means the test-set
> population itself may under-represent this group relative to the full source population. This
> pass checked whether Non-Hispanic Black subgroup *coverage* shows a comparable breakdown to
> BMI-Obese/Age-60+: it does **not** — coverage ranges 86.9%–88.7% across the 5 models, only
> 1 of 5 (XGBoost) has a CI excluding 90%, a much milder deviation
> (`results/uncertainty/phase5_phase6_relationship.csv`). This is a distinct mechanism from the
> selection-disparity question: within-sample coverage behavior (measured here) is not the same
> as whether the sample itself is representative (the open multiple-imputation question) — both
> are reported, kept separate, and neither is used to explain the other."

## 4. Commit containing the statement

`a62ab686668d264396889908de2ac3c129dad3d4` — "Phase 6 Uncertainty: subgroup relationship +
validation tests + final report (Commit D)". Confirmed via `git log -S"much milder deviation"
--oneline -- PHASE6_UNCERTAINTY_RESULTS_REPORT.md`: this is the **only** commit that has ever
touched this string — the sentence was introduced whole in Commit D, not edited afterward.

## 5. What the passage itself explicitly cites as its evidence source

The passage cites exactly one artifact: `results/uncertainty/phase5_phase6_relationship.csv`.
It does **not** cite any multiple-imputation-specific dataset, model, or calibration artifact.
Traced further in Part 3.
