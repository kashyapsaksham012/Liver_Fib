# Phase 3 Audit Decision Log

| Audit question | Decision |
|---|---|
| Methodological validity | PARTIAL: candidate logic is traceable, but overall metrics use only Normal/Obese |
| Reproducibility | REPRODUCIBLE for the restricted analysis; not reproducible as claimed full-cohort analysis |
| OOF protection | Threshold parameters use OOF; calibration candidates are evaluated on their fitting OOF rows |
| Locked-test protection | INCOMPLETE: test predictions and linked labels are loaded before candidate selection |
| Candidate rationale | VERIFIED: each candidate is supported by Phase 2 mechanisms |
| Selection framework | Defensible multi-metric gate, but applied to restricted “overall” metrics |
| Statistical inference | Sensitivity Wilson intervals verified; gap/trade-off CIs and FDR correction absent |
| Small cells | BMI × Age estimates are present; sparse handling is implicit in fallback logic and needs clearer audit output |
| Phase 7 separation | VERIFIED: prior Mondrian conformal work remains separate and unchanged |
| Primary-result protection | VERIFIED: no primary artifacts or master report were modified |
| Final conclusion | UNSUPPORTED as an authoritative full-cohort conclusion |
| Final status | **C. PHASE 3 REQUIRES CORRECTION / RE-EXECUTION** |

## No rerun performed

This audit did not rerun mitigation, tune thresholds, select new candidates, access temporal or
external data, or modify any authoritative result.
