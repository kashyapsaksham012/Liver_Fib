# Inference Methodology Amendment (Phase 3)

**Generated:** 2026-08-18 16:59:59

## Status: explicit Phase 3 methodological amendment

`documentation/phase2/evaluation_metrics_protocol.md` and `documentation/phase2/multiple_comparisons_protocol.md` establish general conventions (2,000-resample bootstrap for fairness disparities; FDR/Benjamini-Hochberg for subgroup comparisons) but do NOT explicitly freeze a Phase-3-specific procedure for comparing the baseline models' overall discrimination. **This was NOT pre-registered as a Phase 2 decision -- it is a Phase 3 methodological clarification that extends the closest existing Phase 2 convention, adopted BEFORE any test-set comparison was computed, and documented here transparently rather than presented as if it had been frozen in Phase 2.**

## Full specification

- **Bootstrap design:** percentile bootstrap, resampling test-set ROWS (not folds), with replacement.
- **Number of resamples:** 2000.
- **Resampling unit:** one participant (SEQN) per draw; identical resampled index applied across all models being compared in a given pairwise test, so the comparison is PAIRED (same resampled participants for both models in each bootstrap iteration) -- this is necessary because all models' predictions come from the same test participants and are therefore correlated; an unpaired method would overstate the variance of the difference.
- **Stratification:** none applied within the bootstrap resampling itself (natural test-set class distribution is preserved on average; any resample lacking both classes is discarded from that metric's distribution).
- **Confidence level:** 95% (2.5th/97.5th percentile).
- **Metric-specific CI procedure:** ROC-AUC and PR-AUC each get their own bootstrap distribution (metric recomputed per resample, not derived from a single CI formula shared across metrics).
- **FDR correction method:** Benjamini-Hochberg, applied to the two-sided bootstrap p-values (`p = 2*min(P(diff<=0), P(diff>=0))`) from the pairwise AUC-difference tests.
- **Family of comparisons (Part 3N):** the 10 pairwise model-vs-model ROC-AUC comparisons on the SAME locked test set. **This family is BASELINE MODEL COMPARISONS ONLY** -- it does NOT include any subgroup/fairness comparison, which belongs to its own separately-corrected family in the designated later fairness phase (per `multiple_comparisons_protocol.md`'s explicit family-separation rule).
- **Random seed:** 42.
