# Phase 3 Correction Record

| Audit finding | OLD PROBLEM | CORRECTION | VERIFICATION |
|---|---|---|---|
| Full-cohort metrics | “Overall” values excluded Overweight and Underweight participants | Corrected runner loads only OOF-linked development metadata, retains all four BMI groups, and labels subgroup rows separately | Corrected candidate output contains `OVERALL`, `BMI_Underweight`, `BMI_Normal`, `BMI_Overweight`, and `BMI_Obese`; source cohort is 5,007 OOF rows |
| Test-set access order | Test predictions/labels were loaded before selection | Corrected runner writes the selection manifest before reading `test_ids.csv`, test metadata, or test prediction files | `phase3_corrected_selection_manifest.json` records the frozen choice; test-loading code occurs afterward |
| Calibration independence | Platt calibration was fit and evaluated on the same OOF rows | Corrected runner fits BMI Platt maps on even-index OOF rows and evaluates candidates on odd-index rows | Candidate outputs identify `OOF_EVAL`; manifest records the deterministic fit/evaluation split |
| Gap/trade-off uncertainty | Major gap and trade-off results lacked uncertainty | Corrected runner adds 400-resample BMI-gap bootstrap intervals and Wilson sensitivity intervals | `gap_ci_low_pp`, `gap_ci_high_pp`, and sensitivity CI columns are present |
| Multiplicity | No explicit candidate-comparison family or correction statement | Candidate family and descriptive interpretation are frozen in the decision log; no unsupported significance claims are made | Report states the family and avoids significance claims |
| Conformal effects | Probability-changing candidates were labeled broadly not applicable | Corrected runner evaluates transformed probabilities with independent split-conformal development data | `phase3_corrected_conformal_development.csv` contains all five candidates per model |
| Small cells | Sparse-cell handling was not independently audited | Corrected runner records BMI × Age cells and uses explicit <10 positive/negative fallback for threshold derivation | BMI × Age rows are included in candidate results; fallback is encoded in the runner |

No prior Phase 3, Phase 7, primary, Phase 0, Phase 1, or Phase 2 artifact was overwritten.
