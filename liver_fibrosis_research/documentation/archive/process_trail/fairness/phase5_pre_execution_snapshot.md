# Phase 5 (Fairness) — Pre-Execution Snapshot

**Timestamp (live):** 2026-08-19 12:26:38 +0530

## Git state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `ac5d54b4db51f32126cb08c9a6c3cca1483627fb` |
| Working tree | 1 modified file (`documentation/end_to_end/human_spot_check_record_template.md`, Part 1 of this task — transcribing the researcher-reported spot-check result, committed separately before Fairness work begins) |
| Upstream | `origin/main`, up to date as of last push (`ac5d54b`) |

## Frozen document hashes (SHA-256, live-computed)

| File | SHA-256 |
|---|---|
| `documentation/phase2/fairness_subgroup_protocol.md` | `0c1cf80360b10572c003f8a27406a6499d64804f4680b5c038c1ac85aeb9634b` |
| `documentation/phase2/fairness_definition.md` | `9cd818dcbc99fb6b630efe248e1e1d694f31cea902905052152f0aa64288f68d` |
| `documentation/phase2/multiple_comparisons_protocol.md` | `e3dff665b1b7be931e85fa96aed44951e5c1994c9a49a7c9f247b15e6d7b10b4` |
| `documentation/phase2/evaluation_metrics_protocol.md` | `d8396ac10f3222023ac3e7164f39046b2e99f31fb487be1634db23f6e1d214ad` |
| `documentation/phase2/statistical_analysis_plan.md` | `433fdb1e25a4c8ed7464d18a270cb3b6961b9dfd34988934056055ee116fef8f` |
| `documentation/phase2/sensitivity_analysis_plan.md` | `0110c749578212022305ba1abcbb279c3256d35f269ad2e0ddff08709984606b` |

## Frozen Phase 3 model hashes (re-verified live, matching prior Phase 4 record exactly — no drift)

| Model | SHA-256 |
|---|---|
| Logistic | `ca312c8162aa01f65a93284ce29f58d9056a9c0b2cf5f7c56175b39e224ef9d5` |
| Random Forest | `37ba542322a2fd4eca821e20f906c415a249e5410a74c1766f80aeda3e8da08a` |
| XGBoost | `8e2b3244d3bb5e5b425e330019e6a4e9850b368a647cb4423c40a80b29a48ec4` |
| LightGBM | `dc9d494ad363b0ef388189bb323b223a7496515618fa4f2dc9060ed2ebd75b02` |
| MLP | `4d760b5a0eec1205f625fedc5c6e17f1ea2349faf1fbd85fb9a1820383f773cc` |

## Phase 4 result hashes (read-only inputs to Phase 5, not modified)

| File | SHA-256 |
|---|---|
| `results/calibration/test_set_calibration_final.csv` | `165df2eea4ba26068787cfc0a15fe7782de576c9d495ca28b6222e4d685ad0ce` |
| `results/calibration/test_set_recalibrated_predictions.csv` | `a945825b6d927c9e7f0194e8b27197ec7aeee959c034ec7a7511ee8e5d250dda` |

## Test-set hash

`a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` — matches both the
Pre-Calibration Closure record and the researcher's independently-reported human spot-check
result exactly.

## Demographic metadata

`data/processed/analysis_dataset_primary.parquet` (SHA-256
`1c1f16a44e3abf91c9d1d72d255e2dcf5be19a73f6bfe450dd52cb2812023938`), confirmed to contain
`SEQN`, `RIDRETH3`, `RIDAGEYR`, `RIAGENDR`, `BMXBMI`, `outcome_primary_8.2kPa` — N=7,153 rows,
matching the frozen primary cohort exactly.

## Environment

Python 3.14.3, scikit-learn 1.9.0, xgboost 3.4.1, lightgbm 4.7.0, numpy 2.5.2, pandas 3.0.5 —
unchanged from Phase 4 (matches `requirements-phase3-lock.txt`).

## Frozen fairness protocol — extracted decisions (read in full this pass, not from memory)

Read live in full: `fairness_subgroup_protocol.md`, `fairness_definition.md`,
`multiple_comparisons_protocol.md`, `evaluation_metrics_protocol.md` (§Discrimination,
§Calibration, §Fairness), `statistical_analysis_plan.md`, `sensitivity_analysis_plan.md`.

**Subgroup dimensions and bins (`fairness_subgroup_protocol.md`, all PRIMARY status):**
- Sex (`RIAGENDR`): Male (N=3,531, 394+), Female (N=3,622, 272+)
- Race/Ethnicity (`RIDRETH3`, NOT RIDRETH1): Mexican American (902, 94+), Other Hispanic (754,
  69+), Non-Hispanic White (2,484, 237+), Non-Hispanic Black (1,787, 177+), Non-Hispanic Asian
  (866, 52+, exploratory-tier), Other/Multi-Racial (360, 37+, exploratory-tier)
- Age (`RIDAGEYR` binned): 18–39 (2,423, 122+), 40–59 (2,318, 221+), 60+ (2,412, 323+)
- BMI (`BMXBMI` binned, WHO categories): Underweight <18.5 (109, 5+, insufficient-evidence
  tier), Normal 18.5–24.9 (1,802, 72+), Overweight 25–29.9 (2,316, 121+), Obese ≥30 (2,926, 468+)

**Precision-tier thresholds (frozen heuristic):** insufficient evidence (pos or neg N < 10);
limited precision ([10,30)); exploratory candidate ([30,100)); primary-feasibility candidate
(both ≥ 100). No subgroup is ever pooled, dropped, or redefined.

**Primary fairness metric (`fairness_definition.md`):** sensitivity, absolute disparity
(subgroup − reference), bootstrap 95% CI (n=2,000, stratified within subgroup, around the
difference itself). Meaningful-difference tolerance: ≥10 percentage points AND CI excludes
zero.

**Secondary fairness metrics (`evaluation_metrics_protocol.md` + `fairness_definition.md`):**
ROC-AUC, specificity, FNR, FPR, calibration slope/intercept — computed for every category in
every primary dimension. PPV/NPV are **not** in this frozen list and are not computed as
fairness metrics (protocol-fidelity decision, not an oversight).

**Reference groups (fixed, `evaluation_metrics_protocol.md`):** Male (sex), Non-Hispanic White
(race/ethnicity), 40–59 (age), Normal BMI (BMI).

**Disparity type:** absolute difference = PRIMARY; relative (ratio) = SECONDARY, only where the
reference rate is not near zero.

**Discrimination evaluation population (`evaluation_metrics_protocol.md` §Discrimination):**
"primary cohort test set, and separately per fairness subgroup" — subgroup discrimination is
evaluated on the **locked test set**, at the frozen Phase 3 model-specific threshold (never
subgroup-optimized).

**Multiple-comparison strategy (`multiple_comparisons_protocol.md`):** Benjamini-Hochberg FDR,
one family per (model × fairness dimension) combination, corrected separately from Phase 3's
discrimination family and Phase 4's three calibration families. Calibration-metric fairness
comparisons form their own separate family, not pooled with sensitivity-disparity comparisons.
Exploratory intersectional comparisons: reported **without** formal correction, explicitly
labeled "exploratory, uncorrected."

**Pre-specified exploratory intersectional cells (`statistical_analysis_plan.md`,
`results/tables/phase2_intersectional_feasibility.csv`):** exactly 26 cells (Sex×Race/Ethnicity,
Sex×Age, Sex×BMI only — no Race×BMI or Race×Age cells were pre-specified), pre-classified: 6
primary-feasibility, 14 exploratory, 3 limited-precision, 3 insufficient-evidence. Only these 26
pre-specified cells will be used; none will be invented.

**Pre-specified sensitivity analyses (`sensitivity_analysis_plan.md`):** 4 formal Phase 3-level
robustness checks (alternative 8.0kPa threshold, CAND_2 cohort, fasting-extended architecture,
multiple-imputation) — **none of these have corresponding trained-model artifacts** (no Phase 3
model was ever trained/evaluated under any of these 4 alternative conditions, confirmed by
absence of any such prediction files under `results/predictions/`). Executing them now would
require retraining, which Phase 5 explicitly forbids. This is a genuine, pre-existing gap
carried forward as a disclosed limitation, not newly created or silently skipped.

**Subgroup calibration:** explicitly authorized as a secondary fairness metric
(`evaluation_metrics_protocol.md`: "calibration slope/intercept... computed for every category
in every primary fairness dimension").

**Raw vs. recalibrated fairness comparison:** not addressed by any frozen Phase 2 document
(recalibration postdates Phase 2 entirely — it is a Phase 4 amendment). This is a genuinely open
decision; if pursued in Phase 5, it will be logged as a dated amendment to the continuous
authoritative registry, exactly as Phase 4's Amendment #8 was, not silently added.
