# RESEARCH WEAKNESSES

Read-only audit, 2026-08-27. Genuine weaknesses remaining **after** all completed analyses,
prioritised by scientific importance. A weakness is not listed merely because an optional
analysis was skipped.

---

## Tier 1 — material, must be prominent in the manuscript

### W1. No external or out-of-sample validation

The models have never been evaluated on an independent non-NHANES population, and no compatible
cohort has been identified (`external_validation_future_work.md`). No later-cycle (temporal) or
independent-cohort evaluation is within the scope of this study. Generalizability beyond the
NHANES 2017–March 2020 development setting is essentially unestablished. (A NHANES 2021–2023
temporal evaluation was completed and split into a separate manuscript — preserved on the
`temporal-validation-standalone` git branch — and is not part of this study's evidence base.)

### W2. No acceptable mitigation for the reliability–fairness failure

Every intervention tested (Mondrian, corrected BMI mitigation, corrected subgroup calibration,
group thresholds, Equal Opportunity, XGBoost retuning, joint conformal, Amendment #17 conformal
selective deferral, and Amendment #19 training-time subgroup reweighting) either fails the
pre-specified multi-metric gate, does not generalize across model families, breaches the
marginal-coverage tolerance, or restores subgroup coverage only at a cost (Mondrian re-run —
marginal over-coverage; training-time reweighting — a discrimination and specificity cost).
Selective deferral showed the under-coverage is confidently-scored wrong singletons, not
flagged-uncertain cases. The **Amendment #19 training-time reweighting** then confirmed that this
score-ordering failure *is* training-time-addressable — it removed the body-mass shortcut and
**halved** the sensitivity gap — but not without lowering test AUROC by 0.02–0.03 and specificity
by up to 12 pp (and it did not restore subgroup coverage to nominal or help the age gap; a joint
BMI×age arm worsened the age gap). The study identifies a problem it can **reduce but not solve
within scope** (`FINAL_SCIENTIFIC_FINDINGS.md` §14). The remaining paths — more lean-fibrosis
data, richer features, or an explicitly accepted performance–equity trade — are honest but limit
the translational contribution.

### W3. The subgroup conformal-coverage failure — measured on one cohort → **RESOLVED 2026-08-27**

> **UPDATE 2026-08-27 (Amendment #16):** replicated on CAND_2 and CAND_3 (8.0 kPa was already
> done). Marginal coverage meets target on both; **BMI-Obese under-covers in 5/5 models on both
> cohorts** (FDR-significant); Age-60+ under-covers in direction on both (FDR-significant 5/5
> CAND_2, 2/5 CAND_3). The finding is now triangulated across four constructions. This W3 concern
> is closed for BMI-Obese; the Age-60+ conformal component retains the same
> direction-robust/significance-fragile character as the Age-60+ sensitivity finding. See
> `documentation/sensitivity/CONFORMAL_REPLICATION_SENSITIVITY_COHORTS_RESULTS_REPORT.md`.


BMI-Obese (76.8–82.3%) and Age-60+ (81.1–85.6%) under-coverage is demonstrated only on CAND_1.
The three sensitivity analyses replicated discrimination / calibration / fairness but **did not
repeat the conformal analysis** (`OPTIONAL_ANALYSIS_DECISION_AUDIT.md` item 6). The finding is
mechanistically plausible and the same subgroups are triangulated on fairness, but the coverage
result itself is un-triangulated.

### W4. Modest absolute performance at low prevalence

AUROC ≈0.82–0.84, PR-AUC ≈0.35, prevalence 9.31%. The models are not accurate enough to be a
stand-alone diagnostic, and the manuscript must not imply otherwise.

## Tier 2 — real, require careful wording

### W5. The Age-60+ finding is statistically fragile

Significant in 4/5 primary models, lost in 9/12 sensitivity-cohort instances, and the underlying
age effect is non-monotonic. It is close to a null result under several specifications.

### W6. Class-balancing artifact required a post-hoc fix

Four of five models are unusable in raw form and depend on an OOF Platt recalibration step whose
mechanism is explained but not exhaustively decomposed. A reviewer may question the choice to
class-balance at all, given a 2-parameter recalibration is then mandatory.

### W7. Missing-data handling is narrow

Complete-case is primary; the only MI work targets the Non-Hispanic Black selection question, and
its conformal extension (BMI-inv Phase 5) carries `LINEAGE NOT FOUND IN REPOSITORY`. Other
subgroups' missingness is not probed, and no whole-cohort MI exists (correctly — it is not
protocol-frozen — but it remains a gap a reviewer may raise).

### W8. Intersectional and small-subgroup cells are underpowered

The BMI-Obese ∩ Age-60+ cell (N=294, 61 positives) and the joint calibration cell (N=138, 30
positives) support only descriptive statements. Normal-BMI rests on 22 test positives;
Underweight (1 positive) is uninterpretable.

### W9. Single reference standard, single survey program, cross-sectional

The outcome is VCTE-defined significant fibrosis (not biopsy), from one US pre-pandemic survey
release, evaluated cross-sectionally.

## Tier 3 — documentation / provenance

### W10. Two master syntheses disagree on the conformal subgroup result

`documentation/MASTER_RESEARCH_RESULTS.md` (§2 items 26–27, §3.5) states *Normal-BMI*
under-covers with different numbers; the raw CSVs and `MASTER_END_TO_END_RESEARCH_REPORT.md`
state *BMI-Obese* under-covers (76.8–82.3%). The raw artifact resolves it, but an uncorrected
conflict between two "master" documents is a hazard for anyone (or any future AI pass) that reads
the wrong one. **Flagged for the register owner.**

### W11. Several provenance gaps are disclosed but unrepaired

Phase 5 MI conformal lineage; frozen 8.2-kPa protocol commit / model-artifact manifest; joint
mitigation generating pipeline; corrected Phase 4 runtime event log; one dependency-graph
transcription gap. Each is honestly labelled, none is load-bearing for a primary claim, but they
accumulate.

### W12. Unresolved status conflicts

Joint-mitigation execution status vs stale status CSV (`CONFLICT UNRESOLVED IN REPOSITORY`);
faithful-AFCP final narrative status (`CONFLICT UNRESOLVED IN REPOSITORY`); CAND_4 frozen
tracking tier (documentation tension). None affects results; all should be adjudicated on paper.

### W13. Two pre-registered analyses are silently untracked

Severity-graded secondary outcomes (≥9.7 / ≥13.6 kPa) and survey-weighted training are frozen
SECONDARY/EXPLORATORY items with **no result artifact and no remaining-work register entry**
(`OPTIONAL_ANALYSIS_DECISION_AUDIT.md` §A/§B). A reviewer could flag the omission of a
pre-registered secondary outcome.

## Tier 4 — design choices a reviewer may contest (not defects)

- Adult-only scope (adolescents excluded).
- OOF Youden thresholds adopted via protocol amendment rather than pre-registered.
- Single 70/30 split rather than repeated / nested resampling of the locked test.
- Race/ethnicity excluded from model input (defensible and documented, but debated in the
  literature).

---

## Priority order for the write-up

Address W1–W4 head-on in the abstract and discussion; W5–W9 in the limitations section with the
wording in `FINAL_LIMITATIONS_REGISTER.md`; W10–W13 are for the register owner to clean up before
submission and do not block the manuscript.
