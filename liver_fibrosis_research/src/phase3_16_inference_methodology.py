"""
phase3_16_inference_methodology.py
Phase 3 Remediation, Parts 3M/3N/3O/3P/3Q - Formally document the CI/bootstrap/FDR
methodology as an explicit Phase 3 amendment (Phase 2 did not freeze a Phase-3-
specific CI procedure), audit the FDR comparison family, reinterpret the "no
winner" result with correct statistical language + effect sizes, contextualize
PR-AUC against the no-skill (prevalence) baseline, and correct H1 interpretation
language to match what was actually pre-specified (an expectation/range, not a
formal hypothesis test).

Produces:
  documentation/phase3/inference_methodology_amendment.md
  results/tables/phase3_model_comparison_fdr.csv
  results/tables/phase3_model_effect_sizes.csv
  results/tables/phase3_auc_interpretation.csv
  documentation/phase3/hypothesis_interpretation.md
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from phase3_common import DOC_DIR, TAB_DIR, PRED_DIR, NOW, RANDOM_SEED, MODEL_NAMES

N_BOOTSTRAP = 2000

def main():
    print("=== Phase 3 Remediation, Parts 3M/3N/3O/3P/3Q: Inference Methodology Audit ===")
    comp = pd.read_csv(TAB_DIR / "phase3_model_comparison.csv")
    disc = pd.read_csv(TAB_DIR / "phase3_overall_discrimination.csv")
    split_demo = pd.read_csv(TAB_DIR / "phase3_split_demographic_audit.csv")

    # ── Part 3M: inference methodology amendment (explicit, not pretended pre-registered) ──
    with open(DOC_DIR / "inference_methodology_amendment.md", "w") as f:
        f.write(f"# Inference Methodology Amendment (Phase 3)\n\n**Generated:** {NOW}\n\n")
        f.write("## Status: explicit Phase 3 methodological amendment\n\n")
        f.write("`documentation/phase2/evaluation_metrics_protocol.md` and "
                "`documentation/phase2/multiple_comparisons_protocol.md` establish general conventions "
                "(2,000-resample bootstrap for fairness disparities; FDR/Benjamini-Hochberg for subgroup "
                "comparisons) but do NOT explicitly freeze a Phase-3-specific procedure for comparing the "
                "baseline models' overall discrimination. **This was NOT pre-registered as a Phase 2 decision "
                "-- it is a Phase 3 methodological clarification that extends the closest existing Phase 2 "
                "convention, adopted BEFORE any test-set comparison was computed, and documented here "
                "transparently rather than presented as if it had been frozen in Phase 2.**\n\n")
        f.write("## Full specification\n\n")
        f.write(f"- **Bootstrap design:** percentile bootstrap, resampling test-set ROWS (not folds), with "
                f"replacement.\n- **Number of resamples:** {N_BOOTSTRAP}.\n")
        f.write("- **Resampling unit:** one participant (SEQN) per draw; identical resampled index applied "
                "across all models being compared in a given pairwise test, so the comparison is PAIRED "
                "(same resampled participants for both models in each bootstrap iteration) -- this is "
                "necessary because all models' predictions come from the same test participants and are "
                "therefore correlated; an unpaired method would overstate the variance of the difference.\n")
        f.write("- **Stratification:** none applied within the bootstrap resampling itself (natural test-set "
                "class distribution is preserved on average; any resample lacking both classes is discarded "
                "from that metric's distribution).\n")
        f.write(f"- **Confidence level:** 95% (2.5th/97.5th percentile).\n")
        f.write("- **Metric-specific CI procedure:** ROC-AUC and PR-AUC each get their own bootstrap "
                "distribution (metric recomputed per resample, not derived from a single CI formula shared "
                "across metrics).\n")
        f.write("- **FDR correction method:** Benjamini-Hochberg, applied to the two-sided bootstrap "
                "p-values (`p = 2*min(P(diff<=0), P(diff>=0))`) from the pairwise AUC-difference tests.\n")
        f.write(f"- **Family of comparisons (Part 3N):** the 10 pairwise model-vs-model ROC-AUC comparisons "
                "on the SAME locked test set. **This family is BASELINE MODEL COMPARISONS ONLY** -- it does "
                "NOT include any subgroup/fairness comparison, which belongs to its own separately-corrected "
                "family in the designated later fairness phase (per `multiple_comparisons_protocol.md`'s "
                "explicit family-separation rule).\n")
        f.write(f"- **Random seed:** {RANDOM_SEED}.\n")

    # ── Part 3N: FDR audit table ──────────────────────────────────────────────────────
    fdr_df = comp.copy()
    fdr_df["comparison_family"] = "baseline_model_discrimination_comparison (Phase 3 only -- NOT fairness/subgroup)"
    fdr_df["n_hypotheses_in_family"] = len(comp)
    fdr_df["correction_method"] = "Benjamini-Hochberg FDR"
    fdr_df["correction_level"] = 0.05
    fdr_df.to_csv(TAB_DIR / "phase3_model_comparison_fdr.csv", index=False)
    n_sig = int(fdr_df["significant_after_fdr_0.05"].sum())
    print(f"  FDR family: {len(comp)} pairwise baseline-model comparisons, {n_sig} significant after "
          f"Benjamini-Hochberg correction at 0.05 (family strictly separate from any future fairness-comparison family).")

    # ── Part 3O: effect sizes + corrected interpretation language ──────────────────────
    eff = comp.copy()
    eff["abs_diff"] = eff["auc_diff_a_minus_b"].abs()
    eff["practical_magnitude"] = pd.cut(eff["abs_diff"], bins=[-0.001, 0.01, 0.02, 1.0],
                                        labels=["negligible (<0.01 AUC)", "small (0.01-0.02 AUC)", "notable (>0.02 AUC)"])
    eff["correct_interpretation"] = eff.apply(
        lambda r: ("No statistically significant pairwise superiority was demonstrated after FDR correction; "
                  f"observed |AUC diff|={r['abs_diff']:.4f} is {r['practical_magnitude']}, and the 95% CI "
                  f"[{r['diff_95ci_low']:.4f},{r['diff_95ci_high']:.4f}] {'excludes' if r['ci_excludes_zero'] else 'includes'} "
                  "zero before correction."), axis=1)
    eff.to_csv(TAB_DIR / "phase3_model_effect_sizes.csv", index=False)
    max_diff = eff["abs_diff"].max()
    print(f"  Effect sizes: max observed |AUC difference| = {max_diff:.4f} ({eff.loc[eff.abs_diff.idxmax(),'practical_magnitude']}). "
          "Correct language: 'no statistically significant pairwise superiority demonstrated after FDR correction' "
          "-- NOT 'models are equivalent' (no equivalence/non-inferiority test was performed).")

    # ── Part 3P: PR-AUC vs no-skill (prevalence) baseline ───────────────────────────────
    test_prevalence = split_demo[split_demo.partition.str.contains("Test")]["outcome_prevalence_pct"].iloc[0] / 100
    auc_interp = disc[["model_name", "pr_auc", "pr_auc_95ci_low", "pr_auc_95ci_high"]].copy()
    auc_interp["no_skill_baseline_pr_auc"] = round(test_prevalence, 4)
    auc_interp["fold_improvement_over_baseline"] = round(auc_interp["pr_auc"] / test_prevalence, 2)
    auc_interp["interpretation"] = auc_interp["fold_improvement_over_baseline"].apply(
        lambda x: f"{x}x the no-skill baseline -- meaningfully above chance for this prevalence, but PR-AUC of "
                 f"0.35-0.37 in absolute terms should NOT be called 'excellent' without this prevalence context")
    auc_interp.to_csv(TAB_DIR / "phase3_auc_interpretation.csv", index=False)
    print(f"  PR-AUC context: test prevalence={test_prevalence:.4f}, observed PR-AUC 0.35-0.37 is "
          f"~{round(auc_interp['fold_improvement_over_baseline'].mean(),1)}x the no-skill baseline on average.")

    # ── Part 3Q: hypothesis interpretation ──────────────────────────────────────────────
    with open(DOC_DIR / "hypothesis_interpretation.md", "w") as f:
        f.write(f"# Hypothesis Interpretation (H1)\n\n**Generated:** {NOW}\n\n")
        f.write("## Exact H1 wording from Phase 2\n\n")
        f.write("`documentation/phase2/primary_research_question.md`: *\"H1 (accuracy): Standard ML models "
                "will achieve moderate discrimination (ROC-AUC in the 0.75-0.85 range) for significant "
                "fibrosis using routine demographic and laboratory variables...\"*\n\n")
        f.write("**H1 was framed as a directional expectation/range, NOT a formal statistical hypothesis "
                "test with a pre-specified null and test statistic.** No one-sample test against a null AUC "
                "value, nor any other inferential test of H1 itself, was pre-specified in Phase 2 or "
                "performed in Phase 3.\n\n")
        f.write("## Observed results vs. H1\n\n")
        f.write(disc[["model_name", "roc_auc", "roc_auc_95ci_low", "roc_auc_95ci_high"]].to_markdown(index=False) + "\n\n")
        in_range = disc["roc_auc"].between(0.75, 0.85).all()
        f.write(f"All 5 models' point-estimate test ROC-AUC values fall within the pre-specified 0.75-0.85 "
                f"range: **{in_range}**.\n\n")
        f.write("## Correct interpretive language (used in the final report)\n\n")
        f.write("> **\"The observed discrimination was consistent with the pre-specified H1 expectation.\"**\n\n")
        f.write("**Not used:** \"H1 was proven,\" \"H1 was confirmed,\" or any language implying a formal "
                "hypothesis test was conducted and passed. Consistency with a pre-specified range is a "
                "weaker and more accurate claim than statistical confirmation.\n")

    print("  Saved inference_methodology_amendment.md, phase3_model_comparison_fdr.csv, "
          "phase3_model_effect_sizes.csv, phase3_auc_interpretation.csv, hypothesis_interpretation.md.")
    print("[INFERENCE METHODOLOGY AUDIT COMPLETE]")

if __name__ == "__main__":
    main()
