# Final Scientific Interpretation

Evidence-based, neutral synthesis of what this project found and did not find. Every figure below
is re-sourced in `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md`.

## 1. What the study found
Five model families (Logistic Regression, Random Forest, XGBoost, LightGBM, MLP), trained on 10
routine demographic/laboratory predictors from NHANES 2017–March 2020 (N=7,153, 9.31% prevalence),
discriminate significant liver fibrosis (`LUXSMED ≥ 8.2 kPa`) with AUCs of 0.8229–0.8429, with no
statistically significant pairwise difference after FDR correction. This alone would support only
a modest, familiar contribution (another liver-fibrosis ML benchmark). The study's substantive
findings come from looking past discrimination:

- **Calibration**: the four class-balanced models substantially overpredict risk in their raw
  output, a mathematically explainable artifact of training against an implicit 50:50 class prior
  on a 9.31%-prevalence outcome. Out-of-fold Platt recalibration, applied once to a locked test set,
  corrects this without affecting discrimination.
- **Fairness**: even after recalibration, sensitivity is substantially lower for Normal-BMI
  patients than Obese patients (27–48 percentage points, all 5 models) and, in 4 of 5 models, lower
  for patients 60+ than for patients 40–59.
- **Conformal uncertainty**: split conformal prediction achieves its 90% marginal coverage target
  overall, but coverage specifically fails for BMI-Obese (76.8–82.3%) and Age-60+ (81.1–85.6%)
  patients — the same two subgroups flagged by the fairness audit.
- **Mitigation**: group-wise (Mondrian) recalibration of the conformal thresholds for these two
  subgroups resolves 5 of 9 model×subgroup combinations, at the cost of a documented tolerance
  breach for XGBoost's overall coverage and an unresolved overlap-population precedence issue.
- **Generalization**: the same pipeline, retrained with an entire demographic subgroup
  (Non-Hispanic Black) withheld and then evaluated on that subgroup, shows a moderate discrimination
  drop (to AUC 0.77–0.79) and a materially less stable calibration than the primary cohort's
  recalibrated result.

## 2. What the study did not find
- No paper-worthy discrimination advantage of any single model family over the others.
- No evidence that BMI/Age fairness deficits or subgroup coverage failures were an artifact of
  complete-case exclusion, missing-data handling, the exact 8.2 kPa threshold, or the exact
  elastography-eligibility/fasting-cohort construction — every sensitivity variant tested reproduces
  the same qualitative pattern (see §9).
- No evidence, one way or the other, that the pipeline generalizes to a genuinely external
  (non-NHANES) population — this was never tested.

## 3. What calibration added
Without it, the raw probabilities from four of the five models would systematically over-refer
patients for further testing (over 60% of the test cohort assigned >30% raw risk in a population
with 9.32% true prevalence, per the recalibration comparison). Recalibration is not a cosmetic step
here — it changes which patients would be flagged in a plausible clinical deployment.

## 4. What fairness analysis found
Aggregate calibration and discrimination hide a specific, reproducible failure mode: the model is
least sensitive exactly in the two subgroups (older, higher-BMI patients) who are often at highest
underlying clinical risk for fibrosis progression. This is the study's central finding, not a
footnote.

## 5. What uncertainty analysis found
The same two subgroups that fail fairness also fail conformal coverage — the uncertainty estimates
are not a distinct, independently-corroborating red flag; they are measuring a correlated
consequence of the same underlying miscalibration/discrimination gap.

## 6. What mitigation achieved
A real, substantial, but incomplete fix: just over half (5/9) of the flagged combinations are
resolved, one model (XGBoost) trades a coverage fix for a marginal-coverage tolerance breach, and
the two target subgroups' 294-person overlap is currently resolved by an arbitrary rule-ordering
choice (Age overwrites BMI) rather than a genuine joint mitigation. This should be reported as
"partially effective, with two named residual problems," not as "fixed."

## 7. What generalization testing found
Moving to an entirely unseen demographic subgroup costs roughly 0.05 AUC and destabilizes
calibration considerably more than it costs discrimination — a caution against assuming this
model's reliability properties (let alone its raw probabilities) transport automatically to
populations not represented in training.

## 8. What multiple imputation showed
That the disproportionate exclusion of Non-Hispanic Black participants under complete-case analysis
(41.3% of exclusions vs. 25.0% of the retained cohort) did not measurably distort the study's
discrimination, calibration, or NHB-subgroup sensitivity findings — but this check did not, and was
not authorized to, test whether conformal-coverage findings for NHB are similarly robust. That
specific question remains open.

## 9. What threshold and cohort-construction sensitivity showed
Across three independently-derived variants (8.0 kPa threshold, CAND_2 relaxed-elastography cohort,
CAND_3 fasting-extended cohort), the BMI-Obese fairness disparity is stable in every one of 15
tested instances, and the Age-60+ disparity's *direction* never reverses — but its *statistical
significance* is lost in 9 of 12 instances where it held at the primary specification. The correct
reading is: the BMI finding is robust; the Age-60+ finding is a real, direction-consistent signal
whose statistical certainty is sensitive to exact sample composition, not a finding that
disappears or reverses under scrutiny.

## 10. What remains uncertain
- Whether conformal-coverage findings for the Non-Hispanic Black subgroup are robust to missing-data
  handling (not tested).
- Whether any of these findings generalize outside NHANES/the US population (not tested; no external
  dataset was ever obtained).
- Whether a genuinely joint (intersectional) mitigation strategy for the BMI×Age overlap population
  would perform differently than the current single-rule precedence (not implemented).
- Whether XGBoost's mitigation approach can be re-tuned to respect the marginal-coverage tolerance
  without abandoning its subgroup-coverage gains (not attempted).

## 11. What claims are appropriate for publication
Appropriate: "five common model families achieve comparable, unremarkable discrimination on this
task; the contribution is a joint calibration–fairness–uncertainty audit that finds a real,
reproducible subgroup reliability failure (older/obese patients) which aggregate metrics conceal,
and shows that group-wise mitigation partially, not fully, resolves it." Not appropriate without
qualification: "the model is fair," "the model achieves reliable subgroup coverage," "the Age-60+
finding is fully robust regardless of specification," "the mitigation fixed the coverage problem,"
or any claim of external validity beyond NHANES.
