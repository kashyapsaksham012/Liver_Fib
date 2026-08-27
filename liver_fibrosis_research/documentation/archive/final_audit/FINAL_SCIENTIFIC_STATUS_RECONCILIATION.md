# Final Scientific Status — Reconciliation

Reconciles two changed findings produced this session (Item 1, pooled multiple-testing correction;
Item 4, genuine joint intersectional mitigation — see `ITEMS_1_5_REFINEMENT_ADDENDUM.md`) against
every prior report in this project, including `RESEARCH_AUDIT_AND_FINAL_METHODOLOGY.md`,
`FINAL_SCIENTIFIC_INTERPRETATION.md`, `P0_P1_REMEDIATION_ADDENDUM.md`, and the published
final-gate-audit and model-report-card artifacts.

**No prior document is edited, deleted, or backdated.** Consistent with this project's own
historical-integrity practice (see `MI_CLOSURE_RECONCILIATION_REPORT.md` §5 and
`CAND4_CLASSIFICATION_RESOLUTION_REPORT.md` for precedent), this document records what changed and
why, separately from the original text.

## Overall verdict: unchanged

Both changes are net-neutral-to-positive for the project. Neither triggers any hard-gate violation.
The Final Gate Audit's verdict — **B: scientifically sound, with material limitations that are
correctly disclosed** — stands.

## Change 1 — Discrimination: pooled correction adds a nuance, doesn't overturn the primary result

**Prior wording:** "No statistically significant pairwise superiority after FDR correction," with
the XGBoost-vs-MLP comparison noted as sitting near the significance boundary under the primary
per-family (10-test) correction.

**What changed:** a pooled Benjamini-Hochberg correction across all 182 formal tests conducted in
this project (frozen registry: `results/statistics/pooled_test_registry.csv`) finds the
XGBoost-vs-MLP AUC difference significant (pooled adjusted p=0.0136).

**Reconciled position:** the primary, prespecified per-family analysis remains the project's primary
result and is unchanged — no significant pairwise winner under that scope. The pooled analysis is a
supplementary, exploratory robustness check (not itself prespecified) that suggests XGBoost may have
a small, real discrimination edge over MLP specifically. This does not license selecting XGBoost as
"the best model" — MLP retains the best raw calibration and conformal efficiency, and the project's
model-selection philosophy was never AUC-only. Both results should be reported together.

**Also confirmed:** 18 of 20 tests referencing the BMI-Obese/Age-60+ subgroups remain significant
under the same pooled correction — the central fairness/coverage finding is now known to be robust
to the strictest multiple-testing scrutiny applied in this project, not merely assumed to be.

## Change 2 — Mitigation: two methods now exist, with different, non-conflatable results

**Prior wording** (`P0_P1_REMEDIATION_ADDENDUM.md`, P1-2): mitigation "did NOT resolve the problem
for any model" — post-mitigation coverage remained below the 90% target for the true intersection,
all 5 models.

**What changed:** a genuinely joint (not sequential-precedence) calibration threshold, computed
directly from the N=138 intersection-only calibration cell, resolves the intersectional coverage
problem for all 5 models (post-mitigation 95% CIs 87.0%–95.6%, point estimates 90.8%–94.9%) —
see `results/mitigation/joint_intersectional_mitigation.csv`.

**Reconciled position — both facts stand, describing different methods:**
1. The project's actually-implemented, frozen Phase 7 method (sequential precedence — the last
   applicable single-dimension threshold wins for participants in both target groups) genuinely does
   not resolve the intersectional problem for any model. **This is unchanged and not retracted.**
2. A separate, new, exploratory joint-calibration method — not yet integrated into the frozen
   pipeline, and calibrated on an "exploratory candidate"-tier sample (N=138, not the project's
   highest-confidence precision tier) — does resolve the problem for all 5 models, at a documented
   cost: 2 of 5 models (XGBoost, LightGBM) now breach the project's own ±5pp overall-coverage
   tolerance, versus 1 of 5 under the sequential method.

**Any future reference to "mitigation results" must specify which method** — the two now produce
materially different, both scientifically valid, answers to "did mitigation work?"

## Updated safe-claims wording (supersedes the equivalent lines in `P0_P1_REMEDIATION_ADDENDUM.md`)

> No model shows a significant discrimination advantage under the primary per-family analysis; a
> supplementary pooled analysis suggests XGBoost may have a small, real edge over MLP specifically,
> which does not change the multi-criteria conclusion that no single model dominates overall.

> The project's implemented mitigation method did not resolve the intersectional coverage problem
> for any model; a separate, exploratory joint-calibration method does resolve it for all five, at
> the cost of a larger overall-coverage tolerance breach in two of five models.

## What did not change

Leakage control, data quality, discrimination-reporting infrastructure, calibration methodology,
threshold-selection process, DCA methodology, interpretability, reproducibility core, PROBAST+AI and
TRIPOD+AI ratings, the marginal BMI-Obese/Age-60+ fairness findings (now additionally confirmed
robust, not weakened), the absence of external validation, and the Item 5 STOP result (no later
NHANES cycle available in this repository) — all stand exactly as previously reported.

## Open decision arising from this reconciliation

Whether to adopt the joint mitigation method in place of the sequential one is a genuine,
unresolved engineering/scientific judgment call: it trades a fully-resolved intersectional problem
for a larger overall-coverage side effect in two models instead of one. This reconciliation does not
resolve that decision — it documents that the choice is now evidence-backed rather than
hypothetical.
