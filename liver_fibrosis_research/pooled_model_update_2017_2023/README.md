# Model-update re-audit — pooled NHANES 2017–2023

Answers the reviewer question *"does keeping the model current fix the reliability
failure?"* Five families retrained on the **pooled 2017–2023 cohort** with the
**frozen hyperparameters unchanged**, then the full audit re-run.

**Verdict: UPDATING DOES NOT RESOLVE THE FAILURE.** All three core reliability
failures persist; discrimination on the newer cycle is unchanged from the
un-updated model.

Separate evidence tier. Nothing in `evidence-freeze` or
`temporal_validation_2021_2023/` is modified.

## Run order

```bash
cd pooled_model_update_2017_2023/src
python p00_cohort.py           # hash frozen inputs; pool + split (N=12,063; test 3,619)
python p01_train_calibrate.py  # retrain 5 families, frozen hyperparams; OOF, threshold, Platt, conformal
python p02_evaluate.py         # THE TOUCH: score pooled locked test; all metrics x {overall, 2021-2023 slice}
python p03_synthesize.py       # classify vs pre-registered verdicts
python verify_pooled.py        # 16/16 number checks
```
Env: `../.venv`. Runtime ~15 s.

## Headline (verified)

| | frozen 2017–2020 | temporal 2021–2023 (un-updated) | **pooled re-audit** |
|---|---|---|---|
| AUROC, all-test | 0.82–0.84 | 0.78 | 0.81 (partial recovery) |
| **AUROC, 2021–2023 slice** | — | 0.776–0.782 | **0.773–0.787 — no recovery** |
| **Normal-vs-Obese sensitivity gap** | 27–48 pp, 5/5 sig | 63–72 pp, 5/5 sig | **32–57 pp, 5/5 sig** → NOT RESOLVED |
| **BMI-Obese conformal coverage** | 0.77–0.82, 5/5 under | 0.76–0.81, 5/5 under | **0.78–0.82, 5/5 under** → NOT RESOLVED |
| **matched-stiffness shortcut** | 0.19–0.33, p<.001 5/5 | 0.21–0.34, p<.001 5/5 | **0.11–0.35, p<.001 5/5** → NOT RESOLVED |

## What this establishes

No approach — post-hoc recalibration, subgroup thresholds, equalised-odds
post-processing, conformal group-wise recalibration, conformal selective deferral
(Amendment #17), training-time subgroup reweighting (Amendment #19), or **model
updating on newer data** — resolves the body-mass reliability–fairness failure.
The failure survives every intervention in the frozen model-development toolkit,
replicates temporally, and widens over time. **It is structural.**

Files: `PROTOCOL_FREEZE.md`, `FROZEN_ARTIFACT_MANIFEST.csv`,
`data/processed/pooled_cohort_2017_2023.parquet` (+ split IDs, manifest),
`models/pooled_*.joblib`, `results/pooled_*_results.csv`, `results/pooled_verdicts.csv`,
`documentation/{POOLED_REAUDIT_REPORT,POOLED_TOUCH_LOG}.md`,
`MANUSCRIPT_SECTION_pooled.md`, `src/verify_pooled.py`.
