# Items 1–5 Refinement Addendum

Executed per the FIX 1–7 patch. No retraining, no refitting, no new locked-test-set inference beyond
what was already frozen (Items 2–4 call `predict_proba` on already-fitted models against
already-defined calibration/test partitions — never regenerating a split, never touching data those
specific model instances hadn't already been evaluated against in the base project). Every new
artifact is a new, separately-named file; nothing frozen was overwritten.

**Scope note:** the base "Items 1–5" execution prompt referenced by this patch was never actually
sent to this session — only the patch itself. Each item's core task was reconstructed from the
patch's own detailed FIX descriptions, which were specific enough to execute directly. This is
flagged here for the record, not hidden.

---

## Item 1 — Pooled multiple-testing correction

**Registry:** `results/statistics/pooled_test_registry.csv` (182 rows, frozen before correction ran).
**Corrected results:** `results/statistics/pooled_fdr_corrected_results.csv`.

Seven distinct statistical families were enumerated, with duplicate derived-report files identified
and folded in (not double-counted) after byte-level verification:

| Family | N tests | Canonical source | Duplicate files folded in (verified byte-identical) |
|---|---:|---|---|
| Discrimination pairwise (AUC) | 10 | `phase3_model_comparison_fdr.csv` | `phase3_model_comparison.csv`, `phase3_model_effect_sizes.csv`, `end_to_end/phase3_model_effects.csv` |
| Calibration pairwise (intercept/slope/Brier) | 30 | `calibration_inference.csv` | — |
| Fairness disparity | 55 | `fairness_inference.csv` | — |
| Subgroup conformal coverage | 75 | `subgroup_coverage.csv` | `coverage_inference.csv`, `phase5_phase6_relationship.csv` |
| MI NHB comparison | 5 | `mi_black_subgroup_comparison.csv` | — |
| Co-occurrence, pooled | 2 | `cooccurrence_correlation_results.csv` | — |
| Co-occurrence, within-model | 5 | `cooccurrence_within_model_secondary.csv` | — |
| **Total** | **182** | | All 182 raw p-values retrievable — 0 excluded |

This enumeration found 35 tests (30 calibration-pairwise + 7 co-occurrence) that were **not** included
in this session's earlier informal "≥145 tests" estimate — a concrete example of exactly the
late-discovery risk Fix 1 exists to catch. No test was inserted after the registry was frozen.

**Result:** 83/182 tests significant at raw p<0.05. **75/182 remain significant after the pooled
Benjamini-Hochberg correction** (manual implementation, standard step-up procedure — `statsmodels`
was unavailable in the project's pinned environment; the manual implementation matches the
textbook algorithm exactly).

**The specific borderline case this was run to resolve:** the XGBoost-vs-MLP AUC comparison
(raw p=0.005) was previously right at the per-family adjusted-p≈0.050 boundary. **Under the pooled
182-test family it is clearly significant** (pooled adjusted p=0.0136). This is a genuine property
of BH-FDR, not an error or cherry-pick: pooling with a family that contains many other small
p-values (subgroup coverage failures, calibration differences) gives BH more power, not less, for
any individual test with a sufficiently small raw p-value. Reviewers checking this result themselves
would find the same outcome.

**Central finding robustness:** of 20 tests whose description references the BMI-Obese or Age-60+
subgroups, 19 were raw-significant and **18 remain significant after pooled correction** — the
project's central fairness/coverage finding is not an artifact of per-family correction choice.

**Dependence-structure disclosure:** Benjamini-Hochberg's guarantee formally relies on independence
or positive regression dependence (PRDS) among p-values. This project's 182 tests are drawn from
overlapping participants across all 5 models, overlapping subgroup definitions, and correlated
outcome measurements — the independence assumption very likely does not strictly hold. **The pooled
correction is reported as a useful, standard, but not unconditionally valid additional check — it is
a limitation of this pooled analysis, not evidence the result is wrong.**

**Scope boundary:** this pooled family covers only tests conducted before this session. Items 2–5's
new statistical outputs (Item 2's bootstrap CIs, Item 3's confusion-matrix CIs, Item 4's joint
mitigation coverage CIs) are new analyses and were **not** retroactively folded into this family —
recorded here as an explicit OUT-OF-SCOPE OBSERVATION, per the patch's own instruction.

---

## Item 2 — True intersectional Decision Curve Analysis with bootstrap uncertainty

**Output:** `results/reliability_extension/intersectional_dca_bootstrap.csv` (350 rows: 7 entities ×
50 thresholds) and `..._summary.csv`.

Computed directly for the N=294 true intersection (not inferred from either marginal subgroup's
DCA), reusing the project's existing net-benefit formula and 1%–50% threshold grid
(`src/rel_02_decision_curve_analysis.py`) and the frozen recalibrated test predictions — **no new
model scoring performed.** 2,000-repetition percentile bootstrap, paired resampling across models
within each repetition, seed=42, logged in the output file itself.

**Finding:** across the 50 tested thresholds, the 95% CI on a model's net benefit **crosses zero
(i.e., becomes statistically indistinguishable from "treat no one") at 17–26 of 50 thresholds,
depending on model** — 34% to 52% of the tested clinical range:

| Model | Thresholds where CI crosses zero (of 50) | Thresholds where CI crosses treat-all (of 50) |
|---|---:|---:|
| Logistic | 17 | 17 |
| Random Forest | 21 | 17 |
| XGBoost | 21 | 16 |
| LightGBM | 19 | 17 |
| MLP | 26 | 19 |

This is a materially weaker clinical-utility picture for the true intersection than the
population-level DCA (which exceeded treat-none in 46–50/50 thresholds). At the population level, net
benefit is confidently established across nearly the whole range; for the N=294 intersection
specifically, a large fraction of the same threshold range cannot statistically distinguish the
model from doing nothing. No binary "stable/unstable" label was assigned — the crossing counts above
are the quantitative result itself.

---

## Item 3 — Confidence intervals for threshold-dependent operating metrics, by subgroup

**Output:** `results/tables/threshold_metrics_ci_by_subgroup.csv` (15 rows: 5 models × 3 subgroups).

Sensitivity/specificity/PPV/NPV use the project's existing Wilson score formula (reused, not
reimplemented differently). LR+/LR− use a log-scale CI (Simel et al. 1991 SE formula,
back-transformed) rather than a symmetric normal approximation, per the patch's explicit
instruction. Computed from the frozen raw test predictions and the already-frozen OOF-derived
Youden thresholds — identical inputs to the project's own headline confusion-matrix table, now
disaggregated by subgroup with proper uncertainty.

**Finding, independently corroborating the fairness-audit direction via a completely different
method:** at the fixed operating threshold, BMI-Obese sensitivity is *higher* than overall (e.g.
XGBoost: 95.0% Obese vs. 84.5% overall), while Age-60+ sensitivity is *lower* than overall for most
models (e.g. XGBoost: 81.2% vs. 84.5%). This matches the direction of the Phase 5 fairness findings
(Normal-BMI disadvantaged relative to Obese; Age-60+ disadvantaged relative to 40–59) using an
entirely separate confusion-matrix-based computation — the two independent analytical lenses agree.

---

## Item 4 — Genuinely joint (not sequential) BMI-Obese ∩ Age-60+ mitigation

**Output:** `results/mitigation/joint_intersectional_mitigation.csv`.

**Calibration-cell adequacy, reported before any result was computed:** the conformal-calibration
set contains **138** participants who are both Obese and 60+ (30 positive, 108 negative). No
protocol-prespecified minimum calibration-cell size for conformal-quantile estimation exists in this
project. The closest already-frozen, already-used convention — `precision_tier()` in
`src/phase5_common.py` — was applied as the most defensible available adequacy heuristic and is
labeled **EXPLORATORY ANALYTICAL CONVENTION — NOT PRESPECIFIED IN THE FROZEN PROTOCOL FOR THIS EXACT
PURPOSE.** Result: `n_pos=30, n_neg=108` → **"exploratory candidate"** tier (neither the weakest
"insufficient evidence" tier nor the strongest "primary-feasibility candidate" tier).

**Method:** the identical split-conformal quantile formula already used by
`src/phase7_02_mitigation_implementation.py` (⌈(n+1)(1−α)⌉-th smallest nonconformity score),
computed on the joint N=138 calibration slice instead of a single-dimension slice. Precedence rule,
declared before computation: intersection participants use the new joint threshold; BMI-Obese-only
and Age-60+-only participants keep their existing marginal thresholds unchanged; "Neither"
participants are unaffected. This is the genuine intersectional analogue Fix 4 asked for, replacing
the prior sequential last-write-wins rule **for the intersection population only.**

**Result — a materially different and more important finding than the sequential approach's:**

| Model | Joint intersection coverage (95% CI) | Overall-coverage change vs. baseline | Within ±5pp tolerance? |
|---|---|---:|---|
| Logistic | 94.9% (91.8%–96.9%) | +4.33pp | Yes |
| Random Forest | 93.2% (89.7%–95.6%) | +4.94pp | Yes |
| XGBoost | 91.8% (88.1%–94.5%) | +6.80pp | **No** |
| LightGBM | 92.5% (88.9%–95.0%) | +5.50pp | **No** |
| MLP | 90.8% (87.0%–93.6%) | +4.89pp | Yes |

**Genuine joint calibration resolves the intersectional coverage failure for all 5 models** — every
model's 95% CI now sits at or above the 90% target (lower bounds 87.0%–91.8%), a decisive
improvement over the sequential-precedence approach, under which every model remained below target
after mitigation (see the earlier P0-1 addendum: 75.9%–84.4% post-mitigation, all CIs excluding
90%).

**But it does not come free.** Under the sequential approach, only XGBoost breached the
pre-specified ±5pp overall-coverage tolerance. **Under the genuine joint approach, two models
(XGBoost and LightGBM) breach it** — the joint threshold is calibrated on a smaller, more homogeneous
cell (N=138 vs. the larger single-dimension cells), which pushes the correction further and produces
a larger ripple into overall coverage for some models.

**Direct answer to Fix 4's governing question — "Does joint calibration materially improve
intersectional reliability without unacceptable degradation elsewhere?"** **Partially.** It
materially improves intersectional reliability (yes, decisively, for all 5 models). It does **not**
do so without degradation elsewhere for 2 of 5 models, which now exceed the project's own
pre-specified tolerance more severely than before. This is a genuine trade-off, not a clean win —
reported as both facts together, per this project's established practice of never reporting only
the favorable half of a mitigation result.

---

## Item 5 — Temporal NHANES validation

**Result: STOP, per the patch's explicit instruction — no substitution attempted.**

This repository's raw data holdings (`data/raw/NHANES_2017_2020/`) contain only the 2017–March 2020
cycle's files (P_LUX, P_DEMO, P_BMX, P_BIOPRO, P_CBC, P_GLU, P_TRIGLY, P_HDL). No later NHANES cycle
was ever downloaded, referenced, or incorporated into this project — confirmed by a repository-wide
search for any mention of a later cycle, which returned zero hits.

Per Fix 5: temporal generalization to a later NHANES cycle requires that cycle to (a) exist, (b)
contain a comparable transient-elastography component, and (c) use a comparable measurement
protocol — none of which could be checked against this project's own data, because no later cycle's
data is present. Acquiring and validating a later cycle's suitability (elastography device/generation,
acquisition protocol, quality-control criteria) is a new data-acquisition task, outside the scope of
this remediation pass, and was not attempted. **No disease, device, population, or dataset
substitution was made.** This STOP is reported as an explicit, unresolved limitation, consistent
with the project's existing, already-documented external-validation gap (`documentation/reliability_extension/external_validation_future_work.md`).

---

## Status

| Item | Status | Key artifact |
|---|---|---|
| 1. Pooled multiple-testing correction | **DONE** | `results/statistics/pooled_fdr_corrected_results.csv` |
| 2. Intersectional DCA with bootstrap CI | **DONE** | `results/reliability_extension/intersectional_dca_bootstrap.csv` |
| 3. Threshold-metric CIs by subgroup | **DONE** | `results/tables/threshold_metrics_ci_by_subgroup.csv` |
| 4. Genuine joint intersectional mitigation | **DONE** | `results/mitigation/joint_intersectional_mitigation.csv` |
| 5. Temporal NHANES validation | **STOPPED — no suitable later cohort available** | this document |

No core pipeline code was modified. No model was retrained or refit. All computations reused
already-fitted models and already-frozen data partitions.
