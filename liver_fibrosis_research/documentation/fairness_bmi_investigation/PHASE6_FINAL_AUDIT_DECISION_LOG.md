# Phase 6 8.0-kPa Robustness — Final Audit Decision Log

**Mode:** read-only final audit; no rerun, experiment, repair, or pre-existing artifact
modification.

| Audit item | Decision | Evidence / limitation |
|---|---|---|
| Overall disposition | **B — accepted with limitations** | Saved full-pipeline tables support a descriptive threshold-robustness conclusion; runtime, lineage, alias, and comparative-inference gaps remain. |
| Only intentional analytical change | PASS | Source derives `LUAXSTAT==1 and LUXSMED>=8.0`; frozen 8.2 labels and existing 8.0 sensitivity labels independently agree. |
| Cohort and labels | PASS | N=7,153; 8.2 positives=666 (9.310779%); 8.0 positives=715 (9.995806%); changed labels=49. |
| Frozen predictors/models | PASS | Ten predictors and all five model families are retained; inherited Phase 3 parameters are loaded without search. |
| Partition integrity | PASS | Proper-train=4,005, conformal calibration=1,002, locked test=2,146; live ID hashes match and all pairwise overlaps are zero. |
| Full pipeline coverage | PASS WITH LIMITATION | Static source covers outcome, training, OOF, calibration, test, fairness, age, BMI×Age, and conformal stages. No durable Phase-6 model files are retained. |
| Static leakage/test order | PASS | Manifest write and selection freeze precede the first `test_ids.csv` read in source order. |
| Runtime leakage/test order | PARTIALLY SUPPORTED | No runtime event log or access trace; manifest assertion and matching test hash are not independent runtime proof. |
| Outcome/test metrics | SUPPORTED DESCRIPTIVELY | AUROC, PR-AUC, sensitivity, specificity, confusion counts, bootstrap intervals, calibration, and conformal tables are arithmetically coherent. |
| Threshold-sensitive fairness conclusion | SUPPORTED WITH SCOPE | BMI-Obese sensitivity disparity increases in all five models; age disparity changes are descriptive and not equivalence/significance claims. |
| Conformal subgroup conclusion | SUPPORTED DESCRIPTIVELY | Overall coverage is near 90%; BMI-Obese and Age-60+ undercoverage persists; Wilson/BH fields do not establish conditional validity. |
| `N0` requirement | NOT INDEPENDENTLY ESTABLISHED | `N0` is not a defined Phase-6 field/protocol: **NOT FOUND IN REPOSITORY**. Zero-positive sparse cells exist; no 100%-coverage row exists. |
| Inference | RESTRICTED | Bootstrap/Wilson methods support recorded quantities; no paired 8.2-vs-8.0 CI, equivalence test, or formal stability test is present. |
| Canonical hash integrity | PASS | Manifest-listed canonical outputs, figures, inputs, and authoritative 8.2 hashes match live SHA-256 values. |
| Alias/output provenance | PARTIAL | Legacy aliases are byte-identical or exact extracts, but are not written by the actual script, are later-timestamped, and are not manifest hash-listed. |
| Documentation hash integrity | PARTIAL | Decision-log hash matches its manifest record; live robustness-report hash does not, because its manifest filename reference differs. |
| 8.2 lineage links | PARTIAL | Frozen 8.2 protocol commit — **NOT FOUND IN REPOSITORY**; frozen 8.2 model-artifact manifest — **NOT FOUND IN REPOSITORY**. |
| Legacy 8.0 outputs | PRESERVED / DISTINCT | `results/sensitivity/*8p0kPa*` is relabel-only (`retrained=False`) and remains separate from the full retraining namespace. |
| Phase 0–5/7, external, primary/master preservation | PASS | No tracked prior artifact was modified; audit writes only the four requested files. |

## Final decision

**B.** Retain the full 8.0-kPa conclusion as a descriptive robustness finding:
**SOME MAJOR FINDINGS ARE THRESHOLD-SENSITIVE**. Do not upgrade it to equivalence,
statistical indistinguishability, universally valid subgroup coverage, or runtime-proven
test-order protection. Decision C is not warranted because no material implementation defect
was found in the actual pipeline logic.
