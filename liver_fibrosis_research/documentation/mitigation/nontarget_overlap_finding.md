# Unanticipated Finding: Cross-Dimensional Target-Subgroup Overlap

**Generated:** 2026-08-19, live, immediately after the single official Phase 7 test-set touch.
This document exists specifically so this finding is not buried — per this task's own Part 8A
("If a non-target subgroup worsens: that is a real result. Do NOT omit it") and Part 10
("A mitigation that... is a valid scientific outcome... report that honestly").

## What the protocol expected

`MITIGATION_PROTOCOL_FREEZE.md` §9 stated: "Mondrian conformal prediction is expected, by
construction, to leave non-target subgroups' thresholds completely unchanged (they still use the
original global per-model threshold) — this is an empirical check confirming that expectation,
not assumed."

**This expectation was checked empirically and found to be incomplete.** It correctly
anticipated that a person's threshold assignment depends only on their OWN target-subgroup
membership — that part is true and verified. What it failed to anticipate is that `sex`,
`race_ethnicity`, `age`, and `bmi` are four **independent, overlapping** dimensions, not one
partition — a participant can simultaneously be, e.g., Male AND BMI-Obese, or Age-60+ AND
BMI-Normal. When tabulating "non-target subgroup" coverage by dimensions *other than* the one
being mitigated, those tabulations still include participants who *are* in a target category
along a *different* dimension and therefore *did* receive a new threshold.

## Quantified overlap (live-computed this pass, from the already-frozen test-set touch output)

| Quantity | N | % of test set (2,146) |
|---|---|---|
| BMI-Obese | 883 | 41.1% |
| Age-60+ | 741 | 34.5% |
| Both simultaneously | 294 | 13.7% |
| At least one target category (union) | 1,330 | **62.0%** |
| Neither (truly unaffected by any group-specific threshold) | 816 | 38.0% |

**62% of the test set received a group-specific (not the original global) threshold for at least
one model**, far more than the "2 narrow target subgroups" framing in the protocol suggested.
This directly explains two downstream observations:

1. **Every** non-target-dimension category (sex, race/ethnicity, non-Obese BMI, non-60+ age)
   showed a coverage *increase* after mitigation (`results/mitigation/
   nontarget_subgroup_protection.csv`, 59/66 rows changed, all positive) — because each such
   category's aggregate coverage is a mixture of touched (target-overlapping) and untouched
   members, and the touched members' coverage rose.
2. **Marginal (overall) coverage** rose for all 5 models (2.9–5.3 percentage points) — XGBoost's
   change (+5.27pp) exceeds the protocol's pre-specified ±5pp tolerance (§8) — a direct
   consequence of the same broad overlap, not an isolated anomaly.

## Implementation detail disclosed: overlap tie-breaking

For the 294 participants who are both BMI-Obese and Age-60+ simultaneously, in models where both
dimensions are targets (Random Forest, XGBoost, LightGBM, MLP — Logistic targets BMI-Obese only),
`src/phase7_04_final_test_touch.py` applies each target dimension's threshold in the order the
dimensions are iterated (`bmi` then `age`), so the **age-specific threshold takes precedence**
for the overlapping 294 participants (last-write-wins). This tie-breaking rule was not
pre-specified in the protocol, because the protocol did not anticipate needing one. It is
disclosed here as an implementation detail discovered necessary during the single test-set
touch, not chosen after seeing results to produce a favorable outcome — the rule is simple,
deterministic, and was not tuned.

## Was the pre-specified non-target-protection *criterion* actually violated?

**No — the literal, pre-specified criterion held.** §8 of the protocol defined non-target
protection narrowly: "No non-target subgroup may develop a **new** FDR-significant
**under-90%** deviation that was not already present pre-mitigation." Every non-target-dimension
coverage change observed was an *increase* (coverage moved further above 90%, not below) — no
non-target category newly fell under 90%. The literal criterion is satisfied. What is
**incorrect**, and is corrected here, is the protocol's *causal explanation* for why that
criterion would hold ("thresholds completely unchanged for non-target subgroups") — the true
mechanism is broader cross-dimensional bleed-through, not isolation. The practical outcome
(no non-target subgroup develops new under-coverage) happens to still be true, but not for the
reason originally stated.

## What this means for interpretation

The marginal-coverage tolerance breach for XGBoost (§8's ±5pp check) is the more consequential
downstream effect of this overlap, and is reported as a genuine, pre-specified trade-off
violation for that one model — not hidden, not used to retroactively loosen the tolerance. See
`PHASE7_MITIGATION_RESULTS_REPORT.md` for the full trade-off analysis.
