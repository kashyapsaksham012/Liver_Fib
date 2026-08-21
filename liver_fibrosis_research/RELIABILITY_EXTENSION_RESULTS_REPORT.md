# Reliability Extension Results Report

## 1. Executive Summary

**Primary co-occurrence result (read this first):** Pooled Spearman correlation between subgroup fairness-disparity magnitude and subgroup conformal-coverage-deficit magnitude, across **N=55** model×subgroup observations (all 4 fairness dimensions, all 11 non-reference categories, no cherry-picking): **ρ = 0.408, 95% bootstrap CI [0.129, 0.642], raw p = 0.0020** (nominally significant under a naive independence assumption). The pre-specified, dependence-aware **category-block permutation test** (10,000 resamples, seed=42, respecting the true 11-cluster structure since 5 models share each subgroup) gives **permutation p = 0.1195 — does not confirm significance**. Precision-filtered sensitivity (N=35, excluding 20 insufficient-evidence/limited-precision observations): ρ = 0.704, p = 0.000002 — substantially stronger.

**What this allows us to claim about the central fairness–uncertainty story:** the naive pooled test is directionally positive and nominally significant, but the more defensible dependence-aware test does not confirm a broad, statistically-supported relationship once known non-independence is properly accounted for. The already-established, narrow finding — that BMI-Obese and Age-60+ specifically show both problems — is **unchanged and remains supported on its own terms** (Phase 5/6's own independent per-subgroup FDR tests). This extension neither proves nor disproves a *general* rule across all subgroups; it shows the general rule is **suggestive, not confirmed**.

**DCA result:** all 5 models exceed both "treat/refer all" and "treat/refer none" across nearly the entire pre-specified 1–50% threshold range, at the population level and in both reliable subgroup analyses (BMI-Obese N=883/140 positive; Age-60+ N=741/101 positive).

## 2. Scope and Non-Goals

Exactly two new analyses were authorized and performed: (A) co-occurrence correlation; (B) Decision Curve Analysis. No model was retrained, no hyperparameter tuned, no cohort/outcome/predictor changed, no new prediction generated, no external dataset used, no analysis chosen after seeing its result. Full non-goal list: `documentation/reliability_extension/pre_execution_snapshot.md`.

## 3. Repository/Provenance Snapshot

Git HEAD at task start: `ad4fb230706536edb66bb663a4e2620bcf5ba726`, branch `main`, clean working tree (aside from pre-existing, unrelated untracked literature-review files from an earlier task). Full snapshot: `documentation/reliability_extension/pre_execution_snapshot.md`.

## 4. Frozen Source-Artifact Verification

`fairness_inference.csv`, `coverage_inference.csv`, and `test_set_recalibrated_predictions.csv` each confirmed touched by exactly one commit in git history — a single, final test-set touch each, no later correction or supersession. Hashes recorded in Section 3's snapshot document.

## 5. Co-occurrence Protocol

Frozen in full, before any correlation was computed: `documentation/reliability_extension/COOCCURRENCE_PROTOCOL_FREEZE.md`, committed standalone (Commit A, `1876858`). Unit of analysis = model×subgroup (N=55); X = |fairness disparity|, Y = |coverage − 90%|; primary test = pooled Spearman; dependence-aware sensitivity = category-block permutation; precision-limited observations retained in the primary, excluded only in a separate labeled sensitivity run; within-subgroup correlations (N=5 each) explicitly not computed as pre-decided (too underpowered).

## 6. Statistical-Dependence Considerations

55 observations cluster into 11 independent subgroup-categories (5 models each) — not 55 independent points. A full mixed-effects model was explicitly not fit (11 clusters is too few to reliably estimate additional variance components); instead, a category-block Monte Carlo permutation test (10,000 resamples, seed=42) directly tests the null of no association while preserving each category's internal 5-model structure. This is the simplest defensible dependence-aware method, chosen and frozen before the correlation was computed.

## 7. Co-occurrence Dataset

`results/reliability_extension/cooccurrence_analysis_table.csv`, N=55 rows, covering sex (1 non-reference category), race/ethnicity (5), age (2), BMI (3), each × 5 models. Reference-group categories (Male, Age 40–59, BMI-Normal, Non-Hispanic White) are not included as correlation points because Phase 5 never computed or stored a disparity value for a group's disparity from itself (rationale: protocol §3.1) — their coverage values remain visible in the full table for descriptive context.

## 8. Primary Correlation Result

| Statistic | Value |
|---|---|
| N | 55 |
| Spearman ρ | 0.4076 |
| 95% bootstrap CI | [0.1291, 0.6419] |
| Raw p (naive, iid assumption) | 0.002012 |
| Category-block permutation p (dependence-aware) | **0.1195** |

**Interpretation, per the frozen outcome rules (Outcome B):** "The observed direction is consistent with the proposed relationship, but the available data do not establish a statistically supported association" once the known clustering is properly accounted for. The naive p-value is not treated as the final word — it is reported transparently alongside the more defensible permutation result, not hidden or superseded silently.

## 9. Precision-Limited Sensitivity Result

Precision-limited categories (per the frozen Phase 5 `precision_tier`, "insufficient evidence" or "limited precision"): Non-Hispanic Asian (n_positive=14), Other Hispanic (26), Other Race/Multi-Racial (11), BMI-Underweight (1) — 4 categories × 5 models = 20 excluded observations. Remaining N=35: **ρ = 0.7043, raw p = 0.000002** — substantially stronger than the primary. This is reported as a separate, clearly-labeled sensitivity result, **not substituted for the primary N=55 result**. It suggests that low-precision subgroups (where both the fairness estimate and the coverage estimate are individually noisier) add substantial scatter to the pooled relationship, and that the relationship is considerably cleaner among higher-precision subgroups — an honest, informative pattern, not evidence used to override the primary finding.

## 10. Within-Model/Within-Subgroup Secondary Results

**Within-model** (N=11 per model, BH-FDR family of 5): Logistic ρ=0.582 (raw p=0.060), LightGBM ρ=0.491 (p=0.125), MLP ρ=0.473 (p=0.142), Random Forest ρ=0.355 (p=0.285), XGBoost ρ=0.227 (p=0.502). **All 5 correlations are positive** (directionally consistent), but **none is individually significant after BH-FDR correction** (all adjusted p ≥ 0.24). **Within-subgroup** correlations (N=5 per subgroup) were **not computed**, per the protocol frozen before any data were examined — N=5 is too small to support meaningful rank-correlation inference.

## 11. Scatter Plot

`results/reliability_extension/cooccurrence_scatter.png` — all 55 points shown, colored by precision tier, with every BMI-Obese and Age-60+ point individually labeled by model. No point is hidden or omitted from the visualization.

## 12. Interpretation of Co-occurrence Hypothesis

**Claim A** ("BMI-Obese and Age-60+ specifically show both fairness and coverage problems") remains fully supported — unchanged, since it rests on Phase 5/6's own independent, already-frozen per-subgroup FDR tests, not on this extension. **Claim B** ("fairness-disparity magnitude and coverage-deficit magnitude are broadly, statistically associated across all evaluated subgroups") is **not established** by the primary, dependence-aware test (permutation p=0.12), though the direction is consistently positive across every secondary check performed (pooled, precision-filtered, and all 5 within-model correlations). Correlation, even where nominally observed, is explicitly not interpreted as evidence of a causal mechanism in either direction.

## 13. DCA Methodology

Standard net-benefit formula: NB = (TP/n) − (FP/n)×(pt/(1−pt)), computed at each threshold pt for each model, compared against "treat/refer all" (NB = prevalence − (1−prevalence)×(pt/(1−pt))) and "treat/refer none" (NB=0). No custom metric invented.

## 14. Probability Source

**Recalibrated** predicted probabilities (`results/calibration/test_set_recalibrated_predictions.csv`, Platt-type, Phase 4/Amendment #8), frozen before any curve was computed. **Rationale:** DCA's net-benefit formula treats the classification threshold as a literal risk probability. Phase 4 established that raw probabilities for 4/5 models substantially overstate risk (calibration intercept −1.86 to −2.26); using raw, poorly-calibrated probabilities would make the threshold axis not correspond to actual risk for those models — a known, standard methodological requirement of DCA in the literature (Vickers & Elkin). This choice was not selected because it produces a more favorable curve — it was frozen based on the pre-existing, independently-established Phase 4 calibration finding.

## 15. Threshold-Range Justification

**1%–50%**, in 1pp steps (50 thresholds). No project-specific or literature-derived clinical threshold range exists anywhere in this project's documentation (confirmed by search this pass) — this range is an explicit, labeled analytical choice, not selected to make any model look more or less useful, and covers well below, at, and well above the 9.31% outcome prevalence.

## 16. Population DCA Results

All 5 models exceed "treat/refer all" at 49–50 of 50 thresholds (only occasionally missing the very lowest, 1%, threshold for Logistic/MLP) and exceed "treat/refer none" at all 50 thresholds. At threshold=10%: net benefit 0.040–0.049 across models vs. treat-all's −0.008 (treat-all has *negative* net benefit at this threshold, since referring literally everyone at a 10% risk cutoff wastes far more resources than it correctly identifies, given 9.31% prevalence). Full table: `results/reliability_extension/dca_summary.csv`.

## 17. BMI-Obese DCA

N=883, 140 positive — classified DCA-reliable (≥20 positive events). All 5 models exceed treat-all at 49–50/50 thresholds and treat-none at 45–50/50 thresholds. At threshold=10%: net benefit 0.086–0.099 vs. treat-all's 0.065 — a real, positive margin over the reference strategy in this higher-prevalence subgroup.

## 18. Age-60+ DCA

N=741, 101 positive — classified DCA-reliable (≥20 positive events). All 5 models exceed treat-all at 47–49/50 thresholds and treat-none at 40–50/50 thresholds. At threshold=10%: net benefit 0.060–0.065 vs. treat-all's 0.040.

## 19. Clinical Utility Interpretation

The models show **potential clinical utility over the reference strategies within the evaluated dataset and threshold range**, broadly across nearly the full 1–50% range, at the population level and in both reliable subgroup analyses. **This does not mean the model is clinically ready, safe for deployment, or externally validated** — those claims are explicitly not made anywhere in this report.

## 20. External-Validation Future Work

Not performed in this task; documented explicitly as necessary future work, not as evidence that it is unnecessary. Full statement: `documentation/reliability_extension/external_validation_future_work.md`.

## 21. Integrated Scientific Interpretation

1. **Does fairness disparity correlate with coverage deficit?** Directionally, yes (positive in every version of the test run). 2. **Is the association statistically supported?** Only under the naive (dependence-ignoring) test; the dependence-aware test does not confirm it. 3. **Does it remain after the precision-limited sensitivity analysis?** The association strengthens, not weakens, when precision-limited subgroups are excluded. 4. **Present within models?** Directionally yes for all 5, none individually significant after FDR. 5. **Present within subgroups?** Not tested (underpowered by design). 6. **Do BMI-Obese/Age-60+ behave differently from the broader pattern?** No — they are consistent with, not exceptional to, the broader positive-but-unconfirmed pattern; their own significance rests on Phase 5/6's independent tests, not on this correlation. 7. **Clinical utility for those groups?** Positive net benefit over both reference strategies across nearly the full threshold range in both subgroups. 8. **Does uncertainty-based evidence identify groups with weaker utility?** DCA does not identify a subgroup with meaningfully reduced clinical utility relative to the population — the fairness/coverage problems identified in Phase 5/6 do not translate into a detectable DCA utility deficit for these two groups within this analysis. 9. **Does DCA strengthen the real-world usefulness story?** Yes, within the stated limits (Section 19). 10. **Does DCA reveal limitations?** Yes — see Section 23.

## 22. Negative/Unfavorable Findings

The primary, dependence-aware co-occurrence test (permutation p=0.12) **does not** support a broad, statistically-confirmed relationship — reported prominently, not minimized. Within-model correlations are directionally positive but individually non-significant for all 5 models after correction. No DCA subgroup or model showed negative net benefit anywhere in the tested range, but this itself is reported honestly as a limit of what this specific analysis can detect (Section 23), not oversold as a universally positive result.

## 23. Limitations

The true independent-cluster count (11) is small, limiting the statistical power of any dependence-aware test — a null permutation result at this scale should not be read as strong evidence of *no* relationship, only as insufficient evidence *for* one. Within-subgroup correlations were not attempted due to inadequate power (N=5). DCA reflects potential utility only within this dataset, this threshold range, and using recalibrated (not raw) probabilities — it is not a deployment-readiness claim. No external validation was performed (Section 20). The DCA subgroup analysis measures whether net benefit is positive, not whether it is *equal* across subgroups — it was not designed to, and does not, directly re-test the Phase 5/6 fairness/coverage disparities in decision-curve terms.

## 24. Reproducibility

Isolated clean rerun of the co-occurrence analysis script reproduced the correlation coefficient, confidence interval, both p-values, and the full within-model table exactly (byte-identical) to the committed run. DCA involves no stochastic elements (pure deterministic arithmetic on fixed, frozen inputs) and is reproducible by construction.

## 25. Tests

`tests/test_reliability_extension.py`: 29 live checks (no model retraining, no new predictions generated, locked test IDs unchanged, full N=55 dataset with no cherry-picking, precision flags preserved, documented recalibrated probability source, Phase 1–8 artifact immutability, commit-ordering discipline, DCA reliability flags and reference strategies present). **All 29 passed.**

## 26. Git/Provenance

| Commit | Subject |
|---|---|
| `1876858` | Commit A — pre-execution snapshot + co-occurrence protocol freeze |
| `c302553` | Commit B — co-occurrence analysis executed |
| `0165021` | Commit C — Decision Curve Analysis executed |
| *(Commit D, immediately after this report)* | External-validation documentation + tests + final report |

Pushed and independently verified via both `git fetch`+`rev-parse` and `git ls-remote`.

## 27. Change to Central Research Narrative

**Thesis-impact classification: 2 — SUPPORTS THE CENTRAL CLAIM BUT DOES NOT BROADEN IT.**

The specific BMI-Obese/Age-60+ co-occurrence observation remains supported as an empirical finding — unchanged, resting on its own already-frozen Phase 5/6 statistical tests. The data from this extension do **not** justify claiming that fairness disparity and coverage deficit are broadly, statistically correlated across all subgroups — the dependence-aware primary test does not confirm this, even though every directional signal (pooled, precision-filtered, within-model) points positively. The correct, honest thesis language is: "the co-occurrence observed in the two headline subgroups is consistent with, but not proven to generalize as, a broader pattern across all evaluated demographic subgroups."

## 28. Final Decision

**Analysis A: A2 — CO-OCCURRENCE ASSOCIATION SUGGESTIVE BUT NOT STATISTICALLY SUPPORTED.**

**Analysis B: B1 — CLINICAL UTILITY SUPPORTED OVER REFERENCE STRATEGIES** (broadly across the tested range, population-level and in both reliable subgroups; not a deployment-readiness claim).

## Final Project-Level Status

**RELIABILITY EXTENSION COMPLETE — MIXED RESULTS, HONESTLY REPORTED**
