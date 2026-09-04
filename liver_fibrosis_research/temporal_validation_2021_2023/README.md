# Temporal validation — NHANES 2021–2023

A later-cycle application of the **frozen** `evidence-freeze` models to NHANES
August 2021–August 2023. Separate evidence tier; supersedes nothing; nothing in
the frozen tree is modified.

**Verdict: PARTIAL TEMPORAL REPLICATION (5/6 core findings).** The two primary
findings and the proposed mechanism replicated across an independently assembled
later cycle; raw discrimination attenuated ~0.05 AUROC.

## Run order

```bash
cd temporal_validation_2021_2023/src
python t00_manifest.py            # hash every frozen artifact used
python t01_build_cohort.py        # frozen CAND_1 eligibility -> N=4,910
python t02_drift_audit.py         # population / predictor / lab-method drift
python t03_apply_and_evaluate.py  # THE TOUCH: frozen models -> all metrics
python t04_synthesize.py          # classify vs pre-registered verdicts
python t05_drop_decomposition.py  # covariate-shift vs concept drift; where the drift is
python verify_temporal.py         # 22/22 number checks
```
Environment: `../.venv` (the project lock file). No new dependencies.

## Files

| | |
|---|---|
| `PROTOCOL_FREEZE.md` | pre-registration — hypotheses, frozen artifacts, eligibility, metrics, replication verdicts, boundary rules. **Frozen before the outcome was touched.** |
| `FROZEN_ARTIFACT_MANIFEST.csv` | SHA-256 of all 21 frozen inputs; `_thelpers.load_frozen()` refuses any that changed |
| `data/processed/temporal_cohort_2021_2023.parquet` + manifest | the reconstructed cohort |
| `results/temporal_*.csv` | discrimination/calibration, fairness, conformal, dissociation, matched-stiffness, drift, replication verdicts |
| `documentation/TEMPORAL_TOUCH_LOG.md` | the single outcome touch, logged |
| `documentation/TEMPORAL_DRIFT_AUDIT.md` | population & lab-method drift |
| `documentation/TEMPORAL_VALIDATION_REPORT.md` | the synthesis |
| `documentation/LIMITATIONS_ADDENDUM.md` | limitations for the write-up |
| `documentation/RECONCILIATION_vs_branch.md` | this run vs the `temporal-validation-standalone` branch |
| `MANUSCRIPT_SECTION_temporal.md` | drop-in abstract sentence + §2.10a + §3.12 + limitation + DO_NOT_CLAIM additions |

## Headline numbers (verified)

| finding | 2017–March 2020 | 2021–2023 | verdict |
|---|---|---|---|
| cohort / prevalence | 7,153 / 9.31% | 4,910 / 11.47% | — |
| AUROC (5 models) | 0.823–0.843 | 0.776–0.782 (Δ −0.04 to −0.06) | ATTENUATED |
| frozen-Platt intercept | −0.15 to +0.14 | −0.11 to +0.22 | REPLICATED (mild over-correction) |
| **Normal-vs-Obese sensitivity gap** | 27–48 pp, 5/5 sig | **63–72 pp, 5/5 sig** | **STRENGTHENED** |
| **marginal / BMI-Obese / Age-60+ / ∩ coverage** | .88–.91 / .77–.82 / .81–.86 / .65–.75 | **.88–.90 / .76–.81 / .85–.88 / .69–.75** | **REPLICATED** |
| **matched-stiffness `obese` coefficient** | 0.19–0.33, p<.001 5/5 | **0.21–0.34, p<.001 5/5** | **REPLICATED (stronger)** |
| **fairness–reliability dissociation** | present | **present 5/5** | **REPLICATED** |
| Age-60+ *sensitivity* deficit | −9 to −15 pp, 4/5 sig | +3 to +10 pp (reversed), 1/5 sig | NOT REPLICATED (anticipated) |
| **AUROC-decline decomposition** | — | concept drift (reweighting recovers ~17%); concentrated in **Normal-BMI (AUROC 0.82→0.62, CI excl. 0)** and 40–59; Obese/60+ unchanged | targeted degradation of the paper's subgroup |

## Boundary

Temporal validation within one survey programme — **not** external, geographic,
or independent-cohort validation. Development cycle pre-pandemic, validation cycle
post-pandemic; the AUROC decline is confounded between model non-transport and a
genuinely shifted population (older, higher prevalence, an alkaline-phosphatase
analyzer change). No model updating, clinical-readiness, or causal claim. No
`evidence-freeze` result was changed.
