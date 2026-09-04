# manuscript_figures/ — the figures to actually put in the paper

Curated from the 85 PNGs in `results/**`. Full reasoning + the "which figures
mislead" analysis is in **`FIGURE_AUDIT.md`** — read that once.

Most files here are an unchanged **copy** of a frozen `results/` artifact. Two
were **regenerated** from the frozen CSVs by `regenerate_figures.py` because their
originals told a different story than the manuscript text — see the next section.

```
main/                  → paper body (all 8 ready to use)
supplement/            → appendix / supplementary material
_superseded_reference/ → the OLD misleading Fig 3, kept only for before/after
```

Three figures in `main/` were regenerated from frozen CSVs by
`regenerate_figures.py` (nothing recomputed — the CSVs are Phase-3/4/5 outputs):
`fig2_calibration_raw_vs_recalibrated.png`, `fig3_sensitivity_by_bmi_band.png`,
and `supplement/cooccurrence_descriptive.png`.

## The 2 "misleading figure" fixes — DONE

| original (problem) | replacement | what changed |
|---|---|---|
| `results/fairness/figures/sensitivity_disparity_*.png` — put **"Obese +48 pp"** at the top of a forest plot (reads as "obese detected great", the opposite of the paper's point), plotted the **excluded Underweight cell** (n = 1) as a big significant bar, and was a generic all-subgroup plot | **`main/fig3_sensitivity_by_bmi_band.png`** | grouped bars, sensitivity per BMI band ordered **Normal → Overweight → Obese**, so the eye reads *sensitivity rising with BMI = lean patients missed*; Wilson 95% CIs (same formula as the conformal analysis); Underweight dropped and stated in a footnote; Obese−Normal gap + BH significance annotated per model |
| `results/reliability_extension/cooccurrence_scatter.png` — looked like a clean positive correlation | **`supplement/cooccurrence_descriptive.png`** | all 55 points grey, no trend line; only BMI-Obese and Age-60+ highlighted; a prominent box states the pooled ρ = 0.41 has **dependence-aware permutation p = 0.12 — a general association is NOT supported** |

Old versions: `_superseded_reference/` (Fig 3) — do not use. Regenerate with
`python3 manuscript_figures/regenerate_figures.py` (reads only frozen CSVs).

## `main/` — put these in the paper

| file | paper slot | caption seed | verified against |
|---|---|---|---|
| `fig1a_discrimination_roc.png` | **Fig 1a** | ROC curves, five model families, locked test set (N = 2,146). AUROC 0.823–0.843; no pairwise difference significant after BH-FDR. | `phase3_final_baseline_results.csv` ✓ |
| `fig1b_discrimination_pr.png` | **Fig 1b** | Precision–recall curves, same models. PR-AUC 0.35–0.37 against a 9.3% prevalence baseline. | same ✓ |
| `fig2_calibration_raw_vs_recalibrated.png` | **Fig 2** | Calibration curves on the locked test set, raw vs out-of-fold Platt, all five models. Class-weighted models over-predict raw (ECE 0.245–0.297); one Platt step restores calibration (ECE 0.011–0.017); the unweighted MLP is close either way; AUROC unchanged. | `curve_data_test_set_final.csv`, `test_set_calibration_final.csv` ✓ (regenerated) |
| `fig3_sensitivity_by_bmi_band.png` | **Fig 3a** | Sensitivity for significant fibrosis by BMI band, five models, Wilson 95% CIs. Sensitivity rises monotonically with BMI in every model; Obese−Normal +27 to +48 pp, all q ≤ 0.006. Underweight (n = 1) excluded. | `subgroup_discrimination_metrics.csv`, `fairness_inference.csv` ✓ (regenerated) |
| `fig3_mechanism_positivecase_scores_xgboost.png` | **Fig 3b (mechanism)** | Model scores for *fibrosis-positive* participants, normal-weight vs obese, with the frozen operating threshold. Positive normal-weight cases sit disproportionately below threshold — the mechanism of the detection gap. | `fairness_inference.csv` / Phase-2 diagnostic ✓ |
| `fig4a_subgroup_coverage_xgboost.png` | **Fig 4a** | Split-conformal coverage by subgroup vs the 90% target (XGBoost shown; all five in supplement). BMI-obese and age-60+ under-cover; normal-weight/overweight/younger over-cover. | `subgroup_coverage.csv`, `marginal_coverage_test_set.csv` ✓ |
| `fig4b_intersectional_coverage_baseline_vs_mondrian.png` | **Fig 4b** | Coverage of the obese ∩ age-60+ cell (N = 294): baseline 0.65–0.75, and after group-wise Mondrian recalibration 0.76–0.84 — still below target. | `intersectional_coverage_ci.csv` ✓ |
| `fig5a_bmi_fairness_specificity_pareto.png` | **Fig 5a** | BMI sensitivity disparity vs overall specificity, base vs fairness-constrained models. Closing the gap costs 5–15 pp specificity. | `results/mitigation/*` — confirm the "fairness-constrained" arm's provenance |
| `fig5b_age_fairness_specificity_pareto.png` | **Fig 5b** | Same for the age gap — the age gap barely responds, evidence of a different mechanism. | same |

## `supplement/` — appendix / supplementary

- `cooccurrence_descriptive.png` — the honest version of the fairness-vs-coverage scatter (regenerated). Use only if a reviewer asks about co-occurrence; the caption must keep the "permutation p = 0.12, not a general association" framing.
- `subgroup_coverage_{5 models}.png` — the other four models for Fig 4a
- `bmi_age_sensitivity_disparity_{5 models}.png` — the full all-subgroup fairness forest plots. Same framing caveat as the old Fig 3 (Obese at top, Underweight plotted): only use in an appendix, with a caption that points the reader to Fig 3a for the interpretation.
- `calibration_curve_oof_{5 models}.png` — raw OOF calibration, per model
- `mechanism_positivecase_scores_{5 models}.png` — the Fig 3b mechanism panel for all five
- `decision_curve_analysis.png` — exploratory clinical-utility (DCA)
- `stiffness_by_{bmi_band,age,sex,race_ethnicity}.png` — Fig S1 (regenerate: axes are capped, titles say "Provisional")
- `missingness_{heatmap,barchart}.png` — supports the §2.1 differential-exclusion limitation

## Do NOT use (not copied here — see `FIGURE_AUDIT.md` §3, §5)

- `results/figures/figure3_coverage_vs_set_size_tradeoff.png`, `figure4_m4b_shrinkage_sensitivity.png`, `figure5_lightgbm_failure_diagnostics.png` — **M4b method, removed by Amendment #20** (and N0=100 is superseded)
- `results/fairness_bmi_investigation/phase5_mi_conformal_figures/*` — **MI-conformal, removed by Amendment #20**
- `results/reliability_extension/cooccurrence_scatter.png` — visually implies a co-occurrence correlation that is **not significant** (permutation p = 0.12); keep out of the main paper
- `results/calibration/figures/calibration_curve_mlp_balanced.png` — sensitivity model, not primary
- `.../phase6_8kpa_robustness/phase6_8kpa_figures/*` — byte-identical duplicate of `.../phase6_8kpa_figures/*`

## If I were you — how I'd triage 85 figures down to a paper set

1. **Start from the claims, not the files.** The paper makes ~7 claims that need
   a picture: discrimination is comparable; calibration is fixed by one step;
   normal-weight is under-detected *and here's why*; conformal coverage fails for
   obese/older and their intersection; mitigation is partial. One figure per
   claim. Everything else is supplement or cut.
2. **For each claim, ask: does the figure say what the sentence says?** That is
   where two of yours failed — the BMI forest plot emphasises the wrong group,
   and the co-occurrence scatter shows a pattern the statistics don't support.
   A figure that a reviewer reads as contradicting your text is worse than no
   figure.
3. **Cut anything tied to a retracted analysis.** Amendment #20 removed M4b and
   MI-conformal — that's 8 figures gone immediately, no judgement call.
4. **De-duplicate.** Identical copies, superseded "corrected" pairs, per-model
   files that duplicate a combined panel — pick one.
5. **EDA figures are for the code release, not the paper.** Distributions,
   correlation matrices, missingness — unless a specific limitation sentence
   needs one (missingness does, for the NHB-exclusion point).
6. **Whatever survives, regenerate at submission** with consistent fonts, no
   truncated titles, no notes-to-self in captions, journal color palette. The
   content is frozen; only the rendering changes.
