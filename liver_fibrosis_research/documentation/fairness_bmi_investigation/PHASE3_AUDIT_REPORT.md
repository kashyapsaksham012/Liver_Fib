# Phase 3 BMI-Sensitivity Mitigation Post-Audit

## Final audit decision

**C. PHASE 3 REQUIRES CORRECTION / RE-EXECUTION**

This is an audit conclusion only. No mitigation experiment was rerun and no primary or Phase 7
artifact was modified.

## Material findings

### 1. The claimed overall metrics are not full-cohort metrics

`run_phase3_bmi_sensitivity_mitigation.py:66–75` filters metadata to `bmi_group_final` in
`Normal, Obese` before merging either OOF or test predictions. The primary training partition
contains 5,007 participants: Normal 1,240, Obese 2,043, Overweight 1,643, and Underweight 81.
The locked test contains 2,146 participants: Normal 562, Obese 883, Overweight 673, and
Underweight 28. Consequently, every `ALL` metric, selection-gate metric, calibration metric,
AUROC/PR-AUC summary, and trade-off comparison in Phase 3 is for the Normal/Obese subset, not
the primary cohort. The report calls these values “overall” without disclosing this
restriction. The selection rule therefore did not test the stated overall-performance
objective.

### 2. Test data are loaded before selection in the execution path

At lines 70–75, test predictions are read and merged before candidate parameter construction
and selection at lines 77–174. The code does not use test labels to derive thresholds, but it
does access and retain test-linked outcomes before the selection step. This violates the
requested sequencing requirement that the locked test be accessed only after the mitigation
protocol is frozen. There is no evidence of numerical post-test optimization, but the
protection claim is not fully compliant.

### 3. OOF calibration evaluation is optimistic

BMI-specific Platt models are fitted on each BMI group’s OOF predictions at lines 87–91 and
then evaluated on those same OOF rows. The transformed global threshold is also derived from
those same fitted rows. This is allowed as development data in a broad sense, but it is not
cross-fitted or independently evaluated; calibration and candidate comparisons are therefore
optimistic. The report does not disclose this limitation.

### 4. Uncertainty and multiplicity are incomplete

Sensitivity Wilson intervals are present. The implementation does not provide confidence
intervals for sensitivity-gap changes, specificity changes, calibration changes, or candidate
selection comparisons. It performs no hypothesis tests or BH-FDR adjustment for the new
candidate comparisons. No unsupported significance claim was found, but the requested
uncertainty/multiple-comparison coverage is incomplete.

### 5. Conformal reliability is not evaluated for probability-calibration candidates

The classification-only threshold candidates do not alter probabilities, so conformal metrics
are not applicable to those candidates. However, BMI-Platt candidates do alter probabilities.
The Phase 3 output does not recompute or compare conformal coverage/set size for those
candidates. The report’s blanket “NOT APPLICABLE” statement is too broad; this is a documented
scope gap. Existing Phase 7 Mondrian results remain separate and authoritative for conformal
under-coverage.

## What was verified

- Candidate names and their implementation are traceable to the Phase 3 script.
- BMI-specific thresholds and BMI × Age thresholds are derived from OOF predictions.
- Candidate selection occurs before the code writes/reads the locked-test evaluation results.
- The output files are reproducible from the recorded script and source files for the
  restricted Normal/Obese analysis.
- Phase 2 provides a reasonable rationale for threshold, calibration, and BMI × Age candidates.
- Sparse-cell handling is implemented through fallback for cells lacking at least 10 positive
  and 10 negative OOF observations, although the output does not provide a separate cell
  audit table.
- Existing Phase 7 protocol and results remain separate, unchanged, and not presented as the
  BMI-sensitivity solution.
- No primary cohort, outcome, predictor registry, model artifact, baseline result, or master
  report modification was observed.

## Claim-level result

The complete claim matrix is `phase3_audit_claim_matrix.csv`; artifact lineage is in
`phase3_audit_lineage.csv`. The central conclusion **“NO ACCEPTABLE MITIGATION IDENTIFIED”**
is reproducible only for the restricted analysis. It is not authoritative for the stated
full-cohort objective because candidate selection used incomplete “overall” metrics and the
locked-test access order was noncompliant.

## Required correction

Phase 3 must be re-executed only after correcting the data-flow order and cohort scope:

1. Keep all development and test predictions separate and do not load test-linked data until
   selection is frozen.
2. Compute overall metrics on the full primary cohort while retaining Normal-BMI, Obese,
   Age, and BMI × Age subgroup metrics.
3. Use independent/cross-fitted development predictions for calibration candidate assessment,
   or explicitly label same-OOF calibration estimates as exploratory.
4. Add gap/trade-off uncertainty and document the multiplicity strategy.
5. Evaluate conformal reliability for any candidate that changes probability outputs, or
   explicitly exclude such candidates before protocol freeze.

No correction was performed during this audit.
