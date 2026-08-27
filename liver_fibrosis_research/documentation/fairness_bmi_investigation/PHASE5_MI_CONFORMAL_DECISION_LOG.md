# Phase 5 MI Conformal Decision Log

1. **Authoritative path verified.** Work was performed only in `/Users/sakshamkashyap/Desktop/Research /liver_fibrosis_research`; `src/mi_01_construct_and_diagnostics.py` exists.
2. **Lineage gate passed before test access.** Existing MI scripts, registry, diagnostics, five distinct dataset hashes, Amendment #12, frozen model artifacts, Phase 6 conformal protocol/artifacts, and the frozen partition records established the exact authorized lineage.
3. **Selection manifest frozen first.** `phase5_mi_selection_manifest.json` records the protocol, model set, fixed thresholds/selection rules, expected test hash, and planned single evaluation. It was written before reading the locked test IDs.
4. **Analysis executed once.** Each of five MI datasets used seed 42+i and training-only, pipeline-embedded IterativeImputer(BayesianRidge, sample_posterior=True). Frozen Phase 3 hyperparameters were reused without search. Each model was calibrated on the fixed 1,002-row calibration partition and evaluated once on the fixed 2,146-row test set.
5. **No invented pooling.** CSVs retain imputation index and seed. `phase5_mi_uncertainty.csv` contains descriptive means/ranges/SDs only; it is not Rubin pooling and is not inferential synthesis.
6. **Subgroups/cells.** All frozen Phase 5 dimensions and exactly the 26 pre-specified intersectional cells were evaluated. Small-cell precision limitations are retained rather than hidden.
7. **Scope discipline.** No Phase 0–4, Phase 7, master, primary complete-case, temporal, external, or prior exploratory artifacts were modified. The only writes were the new Phase 5 MI namespace and its requested documentation/figures.
8. **Evidence summary.** BMI-Obese undercoverage persisted across all five models and all five imputations; overall MI coverage remained close to frozen complete-case values, with model-dependent descriptive deltas. Non-Hispanic Black coverage is shown per imputation without a pooled claim.

Final conclusion: MI CONFORMAL RELIABILITY IS CONSISTENT WITH COMPLETE-CASE RESULTS
