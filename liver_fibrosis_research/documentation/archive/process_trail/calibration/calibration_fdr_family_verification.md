# Calibration FDR-Family Verification

**Generated:** 2026-08-19, live, per Item 2 of the Phase 4 Closure task. This is a code-level
verification, not a restated prose claim — every assertion below is backed by the cited file
and line range, inspected live this pass.

## 3A. Actual artifacts inspected

- `results/calibration/calibration_inference.csv` (Calibration's inference output)
- `src/phase4_04_inference.py` (Calibration's inference code — the actual implementation)
- `src/phase3_07_plots_and_comparison.py` (Phase 3's model-comparison FDR code, for contrast)
- `results/tables/phase3_model_comparison.csv` (Phase 3's inference output, for contrast)
- `documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md` §12–13 (frozen inference/FDR
  decisions)
- `documentation/end_to_end/protocol_amendment_registry.md` (Amendment #2, the origin of the
  bootstrap methodology both phases use)

No filename was assumed — all six were opened and read this pass.

## 3B. Calibration comparison family, answered from the code

| Question | Answer (from `src/phase4_04_inference.py`) |
|---|---|
| 1. What hypotheses were compared? | For each pair of models and each metric: H0 = point-estimate difference (model_a − model_b) = 0, tested via the paired bootstrap distribution of that difference |
| 2. Which models were compared? | The 5 primary models only (`PRIMARY_MODELS` imported from `phase4_common.py`) — MLP_balanced is never included in `PRIMARY_MODELS`, confirmed by import and by the prior closure pass's TEST13 |
| 3. Which metrics were compared? | 3 separate families: calibration intercept, calibration slope, Brier score (the `for metric in ["intercept", "slope", "brier"]:` loop, line 77) |
| 4. How many pairwise comparisons? | C(5,2) = 10 pairs per metric × 3 metrics = 30 total pairwise rows (confirmed: `calibration_inference.csv` contains exactly 30 `pairwise_comparison` rows) |
| 5. Which p-values were adjusted? | The two-sided bootstrap p-value for each of the 10 pairs, computed independently within each metric's loop iteration (`pair_pvals` list, re-initialized at line 78 on every metric iteration) |
| 6. Which FDR method? | Benjamini-Hochberg step-up procedure, hand-implemented identically to Phase 3's own implementation (lines 92–99) — same mathematical procedure, independently applied |
| 7. Alpha/threshold? | 0.05 (`significant_after_fdr_0.05` column; `bh_fdr_adjusted_p < 0.05`) |
| 8. Bootstrap count? | n = 2,000 (`BOOTSTRAP_N`, `phase4_common.py`) |
| 9. Seed? | 42 (`BOOTSTRAP_SEED = RANDOM_SEED`, `phase4_common.py`) — the single frozen project seed, not a new value |
| 10. Paired? | Yes — one `rng.integers(0, n, size=n)` draw per bootstrap iteration, the SAME resampled index array applied to every model within that iteration (line 51 in the bootstrap loop), confirmed structurally |
| 11. Applied only to Calibration comparisons? | Yes — see §3C/3D below |

## 3C. Explicit separation verification: Calibration FDR family ≠ Phase 3 FDR family

**Phase 3's family** (`src/phase3_07_plots_and_comparison.py`, lines 91–113): a single family of
`pairs = list(combinations(MODEL_NAMES, 2))` (10 pairs), one metric only (ROC-AUC), one
`raw_p` list, one BH correction pass, written to `results/tables/phase3_model_comparison.csv`.

**Calibration's families** (`src/phase4_04_inference.py`, lines 76–99): three separate
families, each built inside its own iteration of `for metric in ["intercept", "slope", "brier"]:`
— `pair_pvals = []` is re-initialized at the top of every iteration (line 78), so the BH
correction at lines 92–99 is computed fresh, independently, per metric. Output written to
`results/calibration/calibration_inference.csv`, an entirely different file.

**No code path reads from, writes to, or combines both files' p-value arrays.** Verified by
inspecting both scripts end-to-end this pass — neither imports the other, neither references
the other's output file, and `phase4_04_inference.py` does not read `phase3_model_comparison.csv`
or any Phase 3 table at any point.

**Result: confirmed separate.** Calibration's 3 families (30 total pairwise tests, 10 per
metric) are structurally, computationally, and file-wise disjoint from Phase 3's single 10-pair
AUC family. No pooling occurred.

## 3D. Exact locations

| | File | Object | Lines |
|---|---|---|---|
| Phase 3 family | `src/phase3_07_plots_and_comparison.py` | `pairs`, `raw_p`, `fdr_adj` (single AUC family) | ~91–113 |
| Calibration families | `src/phase4_04_inference.py` | `for metric in [...]:` loop; `pair_pvals`, `adj_pvals` (re-initialized per metric) | 77–99 |

## 3E. Bootstrap methodology — explicit statement

**Both.** Calibration deliberately **reused** Phase 3's bootstrap *methodology* (n=2,000,
seed=42, paired resampling, 95% percentile CIs, Benjamini-Hochberg FDR) — this reuse is
disclosed explicitly in the frozen protocol itself (`CALIBRATION_PROTOCOL_FREEZE.md` §12: "this
method was not itself pre-specified in Phase 2's `statistical_analysis_plan.md`... it was
introduced as Phase 3 Amendment #2... Adopting the same method here for calibration CIs is a
deliberate consistency choice, made explicitly rather than silently"). But Calibration computes
and FDR-corrects its own **three separate hypothesis families** (intercept, slope, Brier),
structurally disjoint from Phase 3's single AUC family — the *procedure* is shared, the *family
of tests being jointly corrected* is not. This is neither pure "reuse Phase 3's methodology
unchanged" nor pure "an entirely distinct Phase 4 methodology" — it is methodology-level reuse
with family-level independence, and is stated precisely as such rather than forced into either
binary option.

## 3F. Was anything actually pooled incorrectly?

**No.** No evidence of pooling was found. This is not a methodological issue requiring a STOP —
the separation the Phase 4 report already claimed in prose is code-verified as genuine.

## Conclusion

The wording already present in `PHASE4_CALIBRATION_RESULTS_REPORT.md` §17 — "Benjamini-Hochberg
FDR, applied separately within each metric's family of 10 pairwise comparisons... not pooled
with Phase 3's discrimination-comparison family or any future Fairness-phase family" — is
**code-supported and accurate**, confirmed by this pass's live inspection of both scripts. No
correction to that sentence was required; this document exists to make the verification
explicit and traceable rather than to change the finding.
