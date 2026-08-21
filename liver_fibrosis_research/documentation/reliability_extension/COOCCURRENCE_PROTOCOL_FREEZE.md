# Co-occurrence Analysis (Analysis A) — Protocol Freeze

**Frozen live, before the primary correlation is computed.** This document is committed standalone (Commit A), before any correlation code runs, per the project's established amendment-discipline precedent (never insert a methodological decision into the same commit as its result).

## 3.1 Unit of analysis

One **model × subgroup** combination. The dataset is the full inner join of every non-reference-group row in `results/fairness/fairness_inference.csv` (the only rows for which a disparity value exists, by construction — see rationale below) against `results/uncertainty/coverage_inference.csv` on (`model`, `dimension`, `category`). This yields **N=55** observations (5 models × 11 non-reference categories: 1 sex + 5 race/ethnicity + 2 age + 3 BMI), covering **all 4 pre-specified fairness dimensions and every non-reference category** — not limited to BMI-Obese or Age-60+, and no category is excluded at this stage.

**Why reference-group categories are not included as separate points:** `fairness_inference.csv` does not store a disparity value for reference-group rows (Male, Age 40–59, BMI-Normal, Non-Hispanic White) — by definition, a group's disparity *from itself* is 0 and was never computed or stored as a distinct estimate in Phase 5. Including a fabricated "0 disparity" point for reference groups would require inventing a value not present in the frozen source, which this protocol explicitly forbids. The reference groups' *coverage* values remain fully available in `coverage_inference.csv` and are reported descriptively in the full analysis table, but they do not enter the correlation because there is no corresponding fairness-disparity value to pair them with.

## 3.2 Fairness variable

`X_signed` = `absolute_disparity_pp` as stored verbatim in `fairness_inference.csv` (this column, despite its name, is **signed** — confirmed by direct inspection, e.g. Female/Logistic = −3.15pp). `X` = `|X_signed|`, the **primary correlation variable**.

**Rationale for using magnitude, not signed value:** the coverage-deficit variable (3.3) is inherently a magnitude (a subgroup can be under- or over-covered relative to 90%, and both directions represent a "coverage reliability problem" in the sense the original study cares about — Phase 6 flagged both directions of significant deviation). Correlating a signed fairness disparity against a signed coverage deviation would conflate two different hypotheses (do the disparities point the same *direction* vs. are they both simply *large*). This protocol's hypothesis (3.6) concerns whether large fairness problems co-occur with large coverage problems, not whether they point the same way — magnitude is therefore the scientifically correct primary variable. Both signed values are retained in the analysis table for descriptive interpretation.

## 3.3 Uncertainty variable

`Y_signed` = `empirical_coverage×100 − 90` (percentage points, signed). `Y` = `|Y_signed|`, the **primary correlation variable**, using the already-stored `empirical_coverage` from `coverage_inference.csv`. No alternative uncertainty metric is substituted.

## 3.4 Dependence structure

The 55 observations are **not independent**: each of the 5 models contributes 11 observations (one per category), and each of the 11 categories contributes 5 observations (one per model). The natural clustering unit is **category** (a subgroup's fairness/coverage profile across 5 models plausibly shares common cause — the same underlying population, the same sample-size/precision constraints), giving **11 clusters of 5 observations each**.

**Frozen inferential plan:**
1. **Primary descriptive analysis:** Spearman rank correlation on all 55 pooled observations (rationale: 3.5).
2. **Dependence-aware sensitivity analysis:** a **category-block permutation test** — the pairing between each category's 5-model fairness-vector and its 5-model coverage-vector is permuted as an intact block (i.e., category labels on one side are shuffled relative to the other, preserving each category's internal 5-model structure), Spearman rho recomputed on each of 10,000 Monte Carlo permutations (seed=42, reproducible), yielding an empirical permutation p-value. This is the simplest approach that directly respects the category-clustering structure without fitting an unstable mixed-effects model on only 11 clusters. A formal multilevel/mixed model is explicitly **not** used, given 11 clusters is too small a number of top-level units to reliably estimate additional variance-component parameters — this limitation is stated in the final report, not hidden.

## 3.5 Primary statistical test

**Spearman rank correlation.** Rationale, stated before calculation: (a) disparity and coverage-deficit magnitudes are bounded-below-at-zero, right-skewed quantities, unlikely to be normally distributed; (b) N=55 (and the true independent-cluster count of 11) is modest; (c) the scientific hypothesis concerns a monotonic relationship (larger fairness problems associated with larger coverage problems), not a specific linear functional form.

## 3.6 Hypothesis

**H0:** No monotonic relationship between fairness-disparity magnitude and coverage-deficit magnitude across the evaluated model×subgroup combinations. **H1:** A positive monotonic relationship exists. Two-sided significance test at α=0.05 (consistent with the project's convention throughout), with the *direction* of any significant result interpreted per the outcome rules in Part 5 of the governing task. A negative or null result is not reinterpreted to preserve the original narrow finding.

## 3.7 Precision-limited subgroups

Using the already-computed `precision_tier` column in `fairness_inference.csv` (frozen Phase 5 heuristic, not redefined here): categories classified **"insufficient evidence"** or **"limited precision"** are identified explicitly (this includes, at minimum, BMI-Underweight [n_positive=1, "insufficient evidence"], Non-Hispanic Asian [n_positive=14, "limited precision"], Other Hispanic [n_positive=26, "limited precision"], Other Race/Multi-Racial [n_positive=11, "limited precision"] — full list reported in the results table, not decided further here).

**Frozen decision (before computing any correlation):** (A) **all 55 pre-specified observations remain in the primary analysis** — no observation is excluded from the primary result regardless of precision tier; (B) a **separate, clearly labeled sensitivity analysis** excludes all "insufficient evidence" and "limited precision" tier observations and reports the Spearman result on the remaining, higher-precision subset. Both versions are reported; neither replaces the other.

## 3.8 Cross-model and cross-subgroup checks (secondary)

- **Within-model** (across the 11 categories, N=11 per model): computed for all 5 models, since N=11 is minimally sufficient for a descriptive rank correlation, but explicitly labeled low-power/descriptive-only.
- **Within-subgroup** (across the 5 models, N=5 per category): **not computed as a formal correlation** — N=5 is too small to support any meaningful rank-correlation inference (fewer than the minimum conventionally required for Spearman significance testing) and would only invite a spurious-precision illusion. This decision is frozen here, before any data are examined, consistent with the instruction not to invent an underpowered test merely because the structure permits it.

## 3.9 Multiple testing

Three distinct families, none merged, none used to cherry-pick a favorable p-value:
1. **Primary family (1 test):** pooled Spearman rho + cluster-permutation p-value. No correction needed (single test).
2. **Precision-limited sensitivity (1 test):** Spearman rho on the precision-filtered subset. Reported as a sensitivity check, not pooled with the primary family's inference.
3. **Within-model secondary family (5 tests):** one Spearman rho per model. Benjamini-Hochberg FDR applied within this family of 5, kept structurally separate from every other phase's FDR family (Phase 3/4/5/6/7 conventions), consistent with this project's established discipline.

No p-value from any family is used to select which result to report as "the" finding — all are reported together in the final table.
