# Figure audit — all 85 PNGs in the repository

I opened and read every figure category in `results/**`. This file records the
verdict for each, the reason, and — importantly — **the figures that visually
tell a different story than the paper's conclusion**, which is what you were
worried about.

Verdicts: ✅ KEEP (paper) · 🟨 KEEP but rework · 📎 SUPPLEMENT only · 🗑 DO NOT USE · ♻ DUPLICATE

---

## 1. The figures that contradict / undercut the paper's conclusion

> **STATUS: both FIXED.** Replacements regenerated from the frozen CSVs by
> `manuscript_figures/regenerate_figures.py`:
> - `main/fig3_sensitivity_by_bmi_band.png` (replaces the forest plot)
> - `supplement/cooccurrence_descriptive.png` (replaces the scatter)
>
> The originals stay in `results/` (frozen, untouched); the old curated copy of
> the forest plot is in `_superseded_reference/`. The analysis below is why.

### 🟨→✅ `results/fairness/figures/sensitivity_disparity_*.png` (5 files)

These are the ones the manuscript currently points at for **Figure 3 — the
headline BMI finding**. Two problems:

1. **They frame the finding backwards.** The paper's conclusion is *"normal-weight
   patients are under-detected."* These plots put **`bmi: Obese +48 pp` (red,
   significant) at the very top** of the forest plot. A reader glancing at the
   figure sees "Obese does great," not "Normal-weight is missed." Same number,
   opposite emphasis — the reference group is Normal, so the bar is Obese-minus-
   Normal and it's positive.
2. **They prominently plot a cell the paper explicitly excludes.** `bmi:
   Underweight` shows as a big red **−41 to −63 pp significant** bar. The paper
   says Underweight has **1 test positive** and is "excluded from interpretation
   by protocol." Leaving it in the figure as a significant result invites a
   reviewer question and muddies the message.
3. Titles are truncated ("...locked test se").
4. They are a *generic all-subgroups forest plot* (sex, race, age, BMI vs each
   reference), not the "sensitivity **by BMI band**" the Figure 3 spec asks for.

**FIXED → `main/fig3_sensitivity_by_bmi_band.png`.** Grouped bars, sensitivity
per BMI band ordered Normal → Overweight → Obese, Wilson 95% CIs (`wilson_ci()`
formula copied from `src/phase6_04_final_test_touch.py`). The eye now reads
"sensitivity rises with BMI → lean patients are missed." Underweight dropped,
footnoted. Obese−Normal gap + BH significance printed under each model. Cross-
checked on run: Normal-BMI sensitivity 0.41/0.59/0.64/0.64/0.55; Obese
0.89/0.91/0.95/0.91/0.94 — matches `subgroup_discrimination_metrics.csv`.
Pair it with `fig3_mechanism_positivecase_scores_xgboost.png` as Fig 3b.

### 📎→✅ `results/reliability_extension/cooccurrence_scatter.png`

Scatter of |fairness disparity| vs |conformal coverage deficit|, 55 model×subgroup
points. **Visually it looks like a clean positive correlation** (the Obese and
60+ points cluster upper-right). But your own `RELIABILITY_EXTENSION_RESULTS_REPORT.md`
says the dependence-aware permutation test gives **p = 0.12 — the general
association is NOT statistically supported**. The manuscript v5 correctly leads
with *dissociation*, not convergence.

**FIXED → `supplement/cooccurrence_descriptive.png`:** same 55 points, all grey
with no trend line; only the BMI-Obese (5) and Age-60+ (5) points highlighted and
labelled; a boxed annotation states the pooled ρ = 0.41 / naïve p = 0.002 **and**
the dependence-aware permutation p = 0.12 ("a general fairness–coverage
association is NOT supported"), and that the two highlighted cells fail on both
axes only by their own per-subgroup FDR tests. Still **supplement, not main
paper** — but it can no longer be misread as a general correlation.

---

## 2. Main-paper figures

| slot | file(s) | verdict | note |
|---|---|---|---|
| **Fig 1** discrimination | `results/figures/phase3_roc_combined.png`, `phase3_pr_combined.png` | ✅ KEEP | AUCs on the plot (0.833/0.834/0.843/0.839/0.823) match `phase3_final_baseline_results.csv` exactly. PR baseline label reads "0.093" (test prevalence 9.32%) — fine, or relabel. Assemble as a 2-panel figure. |
| **Fig 2** calibration | `main/fig2_calibration_raw_vs_recalibrated.png` (regenerated) | ✅ KEEP | 2-panel raw vs OOF-Platt on the **locked test set**, all five models, from the frozen `curve_data_test_set_final.csv` (10 decile bins) + `test_set_calibration_final.csv` (ECE). Left: class-weighted models sit far below the diagonal (ECE 0.245–0.297); right: on the diagonal (ECE 0.011–0.017); MLP close either way. Replaces the raw-OOF-only `calibration_curve_*.png` (which stay as a per-model supplement). |
| **Fig 3a** BMI detection gap | `main/fig3_sensitivity_by_bmi_band.png` (regenerated) | ✅ KEEP | Replaces the forest plot (§1 FIXED). Sensitivity per BMI band, Normal → Overweight → Obese, Wilson 95% CIs, Obese−Normal gap annotated. |
| **Fig 3b** mechanism | `.../phase2/*_positive_scores.png` | ✅ KEEP | Score-distribution histogram of fibrosis-positive Normal-BMI vs Obese cases with the frozen threshold: Normal-BMI positives pile up left of the threshold, Obese positives right of it — the mechanism the paper describes. |
| **Fig 4a** subgroup coverage | `results/uncertainty/figures/subgroup_coverage_*.png` (5) | ✅ KEEP | Clean and on-message: BMI-Obese (~0.77) and Age-60+ (~0.81) at the bottom in red (CI excludes 90%), Normal/Overweight/18–39 over-covering at top, marginal line drawn. Fixes needed: title truncation; the legend box overlaps the "bmi: Obese" point — move it. |
| **Fig 4b** intersection + mitigation | `results/uncertainty/figures/intersectional_coverage_by_model.png` | ✅ KEEP | Baseline (0.65–0.75) vs after group-wise Mondrian (0.76–0.84) for the Obese∩60+ cell — **both bars below the 90% line**, so it correctly shows the mitigation is *partial*. Values match `intersectional_coverage_ci.csv`. On-figure source citation. Excellent honesty figure. |
| **Fig 5a/b** fairness–specificity trade-off | `results/figures/figure1_bmi_fairness_vs_specificity_pareto.png`, `figure2_age_...png` | 🟨 KEEP w/ caution | Base models vs a "fairness-constrained" variant: reducing the BMI gap costs 5–15 pp specificity (arrows down-left). Content is fine and matches the trade-off story. **Confirm what the "fairness-constrained variant" is** (`src/tradeoff_05_generate_figures.py`) and that it is a mitigation the manuscript still reports (not one Amendment #20 cut). Internal title says "Figure 1/2" — relabel. |
| **Fig S1** stiffness distributions | `results/figures/liver_stiffness_by_{bmi_group,age,sex,race_ethnicity}.png` | 📎 SUPPLEMENT | EDA-quality: y-axis capped (~11 kPa, so the fibrosis tail to ~75 kPa is hidden), titles say "Provisional" / "DESCRIPTIVE ONLY". Usable as a 4-panel supplement; regenerate with full range + cleaner styling for publication. |

---

## 3. M4b / joint-conformal figures — 🗑 DO NOT USE (Amendment #20 removed the method)

| file | what it is |
|---|---|
| `results/figures/figure3_coverage_vs_set_size_tradeoff.png` | M1–M4b intersectional coverage vs set size. Legend says **"M4b (Shrinkage N0=100)"** — and `DO_NOT_CLAIM.md` #12 says N0=100 is superseded by N0=0. This was former Supplementary S1; Amendment #20 removed it. |
| `results/figures/figure4_m4b_shrinkage_sensitivity.png` | 4-panel "M4b Precision-Weighted Shrinkage Sensitivity to N0". Entirely about the cut M4b method. |
| `results/figures/figure5_lightgbm_failure_diagnostics.png` | Despite the filename, the title is "M4b Intersectional Coverage across Models (LightGBM Deficit Audit)" — an M4b figure showing the disclosed LightGBM breach (87.07%). |

The MI-conformal figures fall in the same bucket:

| `results/fairness_bmi_investigation/phase5_mi_conformal_figures/phase5_mi_coverage_*.png` (5) | 🗑 | MI **conformal** extension — Amendment #20 removed it (`LINEAGE NOT FOUND`). |

---

## 4. Supplement / appendix candidates (keep in repo, not main paper)

| file(s) | verdict | note |
|---|---|---|
| `results/reliability_extension/dca_curves.png` | 📎 | Decision-curve analysis, 3 panels (population / Obese / 60+). Clean. Exploratory clinical-utility extension (registry: `DCA-01 = EXPLORATORY_ONLY`). |
| `.../figures/phase2/*_roc_bmi.png` (5) | 📎 | Per-BMI-band ROC. Supports "discrimination holds within BMI bands". |
| `.../figures/phase2/*_calibration_bmi.png` (5) | 📎 | Per-BMI-band calibration. Supports §5 [C2] "aggregate recalibration did not extend to subgroups". |
| `.../figures/phase2/*_threshold_sensitivity.png` (5) | 📎 | Sensitivity/specificity vs threshold, by BMI band — supports the "threshold-driven BMI gap" mechanism. |
| `.../figures/phase2/predictor_distributions_bmi.png` | 📎 | Predictor distributions across BMI bands. Context. |
| `.../phase3_corrected_figures/corrected_oof_gap.png` | 📎 | BMI-sensitivity mitigation dev result ("no acceptable mitigation"). |
| `.../phase4_corrected_figures/phase4_corrected_ece_comparison.png`, `..._fairness_gaps.png` | 📎 | Corrected subgroup-calibration ("Decision B — no improvement"). |
| `.../phase6_8kpa_figures/phase6_8kpa_{auc_comparison,bmi_age_sensitivity,conformal_coverage}.png` | 📎 | 8.0-kPa robustness. `bmi_age_sensitivity` is weak (shows only target-group sensitivity, no reference) — redesign if used. |
| `results/figures/missingness_{heatmap,barchart}.png` | 📎 | Directly relevant to the §2.1 differential Non-Hispanic Black exclusion — a good supplement. |
| `results/figures/{laboratory_distributions,candidate_predictor_correlation_matrix,LUXSMED_distribution,LUXCAPM_distribution,P_LUX_*}.png` | 📎 / skip | Phase-1 EDA. Keep for the code release; not paper figures. |

---

## 5. Duplicates & redundant per-model files

| item | action |
|---|---|
| `results/fairness_bmi_investigation/phase6_8kpa_robustness/phase6_8kpa_figures/*` | ♻ **byte-identical** to `.../phase6_8kpa_figures/*` (verified with `cmp`). Delete one copy. |
| `results/fairness_bmi_investigation/phase4_figures/phase4_ece_comparison.png` | ♻ superseded by `phase4_corrected_figures/`. Use the corrected one. |
| `results/figures/phase3_roc_{model}.png`, `phase3_pr_{model}.png` (10) | 📎 per-model companions to the combined Fig 1 panels. Optional supplement, otherwise skip. |
| `results/calibration/figures/calibration_curve_mlp_balanced.png` | 🗑 the MLP **oversampling sensitivity** model, not a primary model. Do not use. |
| `results/fairness_bmi_investigation/figures/phase3/oof_gap_original_vs_selected.png` | ♻ superseded by `phase3_corrected_figures/corrected_oof_gap.png`. |

---

## 6. Count

85 PNGs → **8 in `manuscript_figures/main/`** (Fig 1a/b, 2, 3a/3b, 4a, 4b, 5a/5b)
plus Fig S1 (×4 in supplement), ~20 reasonable supplement material, ~15
DO-NOT-USE (M4b / MI-conformal / superseded / duplicate), the rest Phase-1 EDA
kept for the code release.

Three of the eight `main/` figures were regenerated from frozen CSVs
(`regenerate_figures.py`): **Fig 2** (raw-vs-recalibrated calibration — the repo
had no such figure), **Fig 3a** (BMI-band sensitivity — replaces the
misleading forest plot), and the supplement **co-occurrence** figure. The other
five are unchanged copies of committed PNGs.
