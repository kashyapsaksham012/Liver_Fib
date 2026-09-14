# Survey-weighted sensitivity check — verification report (C6 / E3)

**Status: NEW ANALYSIS, NOT YET FOLDED INTO ANY MANUSCRIPT.** Run on explicit request
(`documentation/manuscript/REVISION_PLAN.md`, Change Table C13, New Analysis Queue E3),
addressing Review Item C6 (unweighted analysis of a complex survey design, undisclosed).
**No manuscript claim has been changed.** No frozen artifact, split file, or model was
modified. Full run log: `logs/svy_weighted_run.log`. Scripts: `src/svy_01_prevalence.py`,
`src/svy_02_bmi_sensitivity.py`. Outputs: `results/sensitivity/survey_weighted/`.

## 1. What was computed and why

NHANES 2017–March 2020 is a stratified, multistage probability sample. The frozen primary
cohort already carries the design variables needed to account for this: `WTMECPRP` (MEC exam
weight — the correct weight here, since VCTE/`LUX` is a MEC-collected exam), `SDMVSTRA`
(masked pseudo-stratum, 24 levels), and `SDMVPSU` (masked pseudo-PSU, coded 1–3 within each
stratum; every stratum in the full N=7,153 cohort has ≥2 PSUs, so no singleton-stratum
handling was needed). None of this was previously applied — the manuscript's primary analysis
is, correctly, an unweighted case-level audit, but that choice was never stated.

This check re-estimates two primary-analysis numbers using Taylor-series linearization (the
standard NHANES-recommended design-based variance method), via `samplics.TaylorEstimator`,
**reported alongside — not replacing — the unweighted primary result**:

1. **Marginal prevalence** of significant fibrosis, full cohort (N=7,153) — a straightforward
   design-based proportion.
2. **BMI-subgroup sensitivity** (Obese vs. Normal), all five models, locked test set — a
   design-based domain *ratio* estimate (weighted true-positives-detected ÷ weighted
   true-positives), using the domain-indicator method (full N=7,153 stratum/PSU structure
   retained, with a domain label marking test-set × BMI-subgroup membership) rather than
   restricting the design object to the 2,146-row test set. Subsetting a design object before
   estimation is a known way to understate domain variance; the domain-indicator method is the
   standard correct alternative (this is what R's `survey::svyby` and Stata's `svy: subpop` do
   internally).

**Stated limitation, not hidden:** each BMI domain (Normal, Obese) is estimated
independently. This gives a valid design-based CI for each subgroup's weighted sensitivity,
but *not* a formal design-based CI for the Obese-minus-Normal difference itself, which would
need a custom delta-method covariance term between the two domains under the shared design —
beyond what this off-the-shelf ratio/domain estimator directly outputs. The point-estimate gap
and whether the two domains' 95% CIs overlap are reported as a qualitative read on
robustness, not as a formal significance test on the gap.

## 2. Results

### 2a. Marginal prevalence

| | Estimate | 95% CI |
|---|---|---|
| Unweighted (primary, case-level) | 9.31% | — |
| Survey-weighted (MEC exam weight × stratum × PSU) | **8.30%** | 7.00%–9.81% |

The unweighted estimate falls inside the weighted CI, but the point estimate shifts down about
one percentage point when reweighted to be population-representative. This is expected and
unsurprising for a case-level model-development cohort — it is exactly the kind of shift the
Limitations sentence (below) should disclose, not something requiring a manuscript
re-derivation, since the primary analysis was never framed as a population-prevalence claim.

### 2b. BMI-subgroup sensitivity disparity (Obese minus Normal, pp)

| Model | Unweighted gap | Weighted gap | Weighted 95% CIs overlap? |
|---|---|---|---|
| Logistic | +47.66 | **+20.91** | Yes |
| Random Forest | +31.62 | **+11.43** | Yes |
| XGBoost | +31.36 | **+14.19** | Yes |
| LightGBM | +27.08 | **+9.50** | Yes |
| MLP | +39.03 | **+22.13** | Yes |

**This is the result that needs careful, honest handling — not a "nothing changed" or "the
finding disappears" summary.** Three things are simultaneously true:

- **Direction is stable.** All five models still detect Obese participants more sensitively
  than Normal-BMI participants under population weighting. The disparity does not reverse or
  vanish.
- **Magnitude attenuates substantially.** The weighted point-estimate gap is roughly 35–65%
  smaller than the unweighted gap for every model (e.g. logistic 47.7 → 20.9 pp; LightGBM
  27.1 → 9.5 pp).
- **Precision drops sharply.** The weighted CIs are wide (Normal-BMI's weighted sensitivity CI
  spans roughly 42–102 percentage points for some models) because the weighted estimator's
  effective sample size for a 22-positive domain, once weight variability is accounted for, is
  much smaller than 22. Under the (conservative) CI-overlap heuristic used here, the Obese and
  Normal weighted CIs overlap for every model — meaning this check cannot, on its own,
  distinguish the weighted disparity from zero at conventional confidence, even though the
  unweighted, larger-effective-n analysis clearly can (FDR q ≤ 0.006 for all five).

The honest reading: this is not evidence the primary finding is wrong, and not evidence it is
unaffected by weighting — it is evidence that the *unweighted, case-level* analysis is the
right primary lens for a risk-model audit (as the manuscript implicitly assumes), because that
is where this cohort's power actually lives; the survey-weighted version of the same question
is directionally consistent but far less precise on a subgroup this thin (Normal-BMI, 22 test
positives), which is itself informative about why this is presented as a supplementary
sensitivity check rather than promoted to the primary analysis.

## 3. Suggested manuscript disclosure

Minimum (Limitations), regardless of whether the full check above is cited:

> All estimates are unweighted, case-level analyses; NHANES design variables (MEC exam weight,
> masked pseudo-stratum, and pseudo-PSU) are present in the analytic file but were not applied,
> consistent with an in-sample risk-model audit rather than a population-prevalence estimate.

If citing this check specifically:

> A survey-weighted sensitivity check (design-based Taylor linearization; MEC exam weight,
> masked stratum, masked PSU) found the marginal prevalence estimate shifted from 9.31% to
> 8.30% (95% CI 7.00–9.81%) and the BMI-subgroup sensitivity disparity attenuated by roughly
> 35–65% in magnitude while preserving direction in all five models; the weighted comparison
> is imprecise on this cohort's 22 Normal-BMI test positives and its confidence intervals
> overlap, so it is reported as a directionally-consistent robustness check rather than a
> replacement for the primary unweighted analysis.

## 4. File inventory

```
results/sensitivity/survey_weighted/
  svy_prevalence_summary.csv          Section 2a headline numbers
  svy_prevalence_full_output.csv      full Taylor-linearization output (both outcome levels)
  svy_bmi_sensitivity.csv             per-model, per-domain weighted + unweighted sensitivity + CI
  svy_bmi_sensitivity_gap_summary.csv Section 2b headline gap comparison
logs/svy_weighted_run.log             full stdout of an end-to-end run (reproducibility-verified
                                       bit-for-bit against a second independent run)
src/svy_01_prevalence.py, src/svy_02_bmi_sensitivity.py
```

## 5. Notes on the tooling

`samplics==0.6.0` was already declared in `requirements.txt` (committed 2026-08-28) but not
previously installed in this project's `.venv` — it was installed now to run this check. The
package emits a deprecation notice ("samplics is archived... migrate to 'svy'"); the Taylor
linearization method it implements is standard and stable, so this does not affect the
validity of the numbers above, but a future re-run should note the package may need to migrate
to its suggested replacement if `samplics` becomes uninstallable.
