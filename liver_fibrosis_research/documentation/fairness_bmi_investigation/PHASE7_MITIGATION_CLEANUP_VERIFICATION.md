# Phase 7 Mitigation Cleanup — Independent Verification

**Date:** 2026-08-27
**Scope:** Verify the pre-existing Phase 7 mitigation cleanup (`src/phase7_mitigation_cleanup.py`
and `results/fairness_bmi_investigation/phase7_mitigation_cleanup/`, timestamped 2026-08-27
09:28–09:29 IST). This document does **not** modify, overwrite, or reclassify any existing
Phase 0–6, historical Phase 7, joint, or master artifact. It adds an audit record only.

---

## 1. Reproducibility

`src/phase7_mitigation_cleanup.py` was re-executed under the project venv
(`.venv/bin/python`, Python 3.14.7) with all declared inputs present and hash-verified.

| Output file | Re-run vs. existing |
|---|---|
| `phase7_xgb_retuning_results.csv` | **byte-identical** (sha256 `550ad27c…`) |
| `phase7_xgb_comparison.csv` | **byte-identical** (`abadb104…`) |
| `phase7_tradeoff_analysis.csv` | **byte-identical** (`cc8b556b…`) |
| `phase7_joint_mitigation_audit.csv` | **byte-identical** (`c0684a8b…`) |
| `phase7_joint_mitigation_results.csv` | **byte-identical** (`b15debdc…`) |
| `phase7_locked_test_confirmation.csv` | **byte-identical** (`5bd011da…`) |
| `phase7_selection_manifest.json` | identical except `created_utc` timestamp |
| `phase7_lineage.json` | identical except `runtime` wall-clock block |

All numeric results, the selection decision, and every recorded input hash reproduce exactly.
The two timestamp-only differences were reverted; the working tree is unchanged by this
verification. **Verdict: fully reproducible.**

---

## 2. Locked-test protection — verified

Source-order check of `phase7_mitigation_cleanup.py`:

1. OOF development: reads `results/predictions/validation_predictions_xgboost.csv`, sorts by
   `SEQN`, splits even-index → `fit` / odd-index → `eval`. All candidate parameters (Youden
   thresholds, Platt maps) are fit on `fit` only; metrics computed on the disjoint `eval` half.
2. Conformal development: reads `data/processed/splits/conformal_calibration_ids.csv` only
   (calibration partition, not test), split fit/eval by the same parity rule.
3. `chosen` candidate/status is computed (line ~403) purely from OOF + calibration frames.
4. `phase7_selection_manifest.json` is written (line ~464).
5. **Only then** are `results/uncertainty/test_set_prediction_sets.csv` and
   `results/predictions/test_predictions_xgboost.csv` read (line ~468+), for one confirmatory
   evaluation.
6. `phase7_lineage.json` and the reports are written last.

`test_access` in the manifest reads *"NOT YET ACCESSED DURING DEVELOPMENT; this manifest freezes
selection before test loading"*, and `test_order` records the sequence above. No test label
informs selection. **Verdict: locked-test protection intact.**

Recorded test-access order (from manifest / lineage):
`OOF development evaluation → calibration development evaluation → selection manifest written →
single locked-test confirmation → lineage hashes and reports written.`

---

## 3. XGBoost retuning — verification

### 3.1 The previously documented tolerance breach — quantified

The Phase 7 issue being addressed is XGBoost's **post-mitigation marginal conformal
coverage overshoot** under group-wise (Mondrian) recalibration:

| Source | XGBoost marginal coverage | Change | Tolerance |
|---|---|---|---|
| `results/mitigation/marginal_coverage_before_after.csv` | 0.8812 → **0.9338** | **+5.27 pp** | `within_5pp_tolerance = False` (only model failing) |
| `documentation/MASTER_RESEARCH_RESULTS.md` §189 (FDR-gated variant) | → **93.85%** | — | stated as `> 93.0% limit` |

The two project artifacts cite slightly different post-mitigation values (93.38% vs 93.85%) for
different Mondrian variants; this pre-existing inconsistency is **not** introduced by the cleanup.
Either way, XGBoost is the single model breaching the ±5 pp change tolerance. The cleanup report
does not cite this specific number and should — see §5.

### 3.2 Candidate family — authorized only

Candidates are exactly the five from the previously authorized Phase 3 corrected BMI mitigation
family: `original_frozen`, `bmi_thresholding`, `bmi_platt_calibration`, `bmi_age_thresholding`,
`combined_bmi_platt_thresholding`. The manifest records
`authorized_framework_source = src/run_phase3_corrected_bmi_mitigation.py` with its sha256.
No new algorithm, model, predictor, outcome, or threshold definition. **Verified.**

### 3.3 Multi-metric selection gate (OOF development half)

| candidate | overall sens | overall spec | BMI Obese−Normal gap | Age 60+−40–59 gap | conformal marginal drift | framework gate | eligible |
|---|---|---|---|---|---|---|---|
| original_frozen | 0.813 | 0.692 | +37.9 pp | 1.25 pp | 0.0 pp | pass (ref) | ref |
| bmi_thresholding | 0.700 (**−11.3 pp**) | 0.748 | +2.0 pp | 0.18 pp | 0.0 pp | **FAIL** (sens) | no |
| bmi_platt_calibration | 0.761 (**−5.2 pp**) | 0.582 (**−11.0 pp**) | +31.8 pp | 1.96 pp | **−5.79 pp** | **FAIL** (sens, spec, conformal) | no |
| bmi_age_thresholding | 0.596 (**−21.7 pp**) | 0.813 | +7.1 pp | 3.21 pp | 0.0 pp | **FAIL** (sens) | no |
| combined_bmi_platt_thresholding | 0.700 (**−11.3 pp**) | 0.748 | +2.0 pp | 0.18 pp | **−5.79 pp** | **FAIL** (sens, conformal) | no |

The gate (sensitivity ≥ original − 5 pp; specificity ≥ original − 5 pp; Brier ≤ original + 0.01;
age gap ≤ original + 5 pp; |conformal marginal drift| ≤ 5 pp) is a genuine multi-metric trade-off
check, not single-metric optimization. Every candidate that closes the BMI-Obese/Normal
sensitivity gap does so by **dragging Obese sensitivity down** to the Normal level (≈0.72), not by
raising Normal sensitivity — a net loss of 11–22 pp of overall sensitivity. No candidate is
selection-eligible.

`bmi_platt_calibration` and `combined_bmi_platt_thresholding` additionally *undershoot* conformal
marginal coverage by 5.79 pp — trading one tolerance breach for the opposite one.

### 3.4 Locked-test confirmation

Because no retuned candidate is eligible, the single confirmatory touch evaluates
`original_frozen` on the locked test. It reproduces the frozen Phase 6 XGBoost baseline exactly
(overall conformal coverage 0.8812, matching `marginal_coverage_before_after.csv`;
AUROC 0.8429). `test_labels_used_for_selection = NO` on every row.

### 3.5 XGBoost verdict

`NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED` is **correct and well-supported**. The negative
result is honest: within the authorized candidate family, XGBoost's coverage-tolerance breach
cannot be resolved without an unacceptable sensitivity or opposite-direction coverage cost.

**Residual limitation:** the OOF development half (~2,503 rows) yields small intersectional cells
(BMI-Obese ∩ Age-60+ ≈ 326, ~70 positives), so subgroup point estimates on the development half
are noisy. The *decision* rests on well-powered overall sensitivity/specificity, so this does not
undermine the conclusion, but subgroup dev numbers should not be read as precise.

---

## 4. Joint intersectional mitigation — verification

### 4.1 It is genuinely joint, not sequential

`results/mitigation/joint_intersectional_mitigation.csv` derives a **single split-conformal
quantile from the joint (BMI=Obese AND Age=60+) calibration slice, N=138**
(`joint_threshold_quantile_level = 0.913043`). Its `precedence_rule` field: intersection members
use the joint threshold; BMI-Obese-only members use the BMI marginal threshold; Age-60+-only
members use the Age marginal threshold; "This REPLACES the prior sequential last-write-wins
precedence for the intersection population only."

This is mechanically distinct from the sequential BMI-first/Age-second scheme audited separately
in `src/phase7_06_threshold_precedence_audit.py` ("Age OVERWRITES BMI, last-write-wins"). The
cleanup's `implementation_assessment = "GENUINE JOINT ... not sequential BMI-first/Age-second"`
is **correct**. The distinction is preserved, not conflated.

### 4.2 Cell composition and coverage (from the source artifact)

| model | cal N | pos | neg | test N | intersection coverage (95% CI) | mean set size | marginal Δ vs baseline | within ±5 pp |
|---|---|---|---|---|---|---|---|---|
| logistic | 138 | 30 | 108 | 294 | 0.949 (0.918–0.969) | 1.89 | +4.33 pp | yes |
| random_forest | 138 | 30 | 108 | 294 | 0.932 (0.897–0.956) | 1.86 | +4.94 pp | yes |
| **xgboost** | 138 | 30 | 108 | 294 | 0.918 (0.881–0.945) | 1.85 | **+6.80 pp** | **no** |
| **lightgbm** | 138 | 30 | 108 | 294 | 0.925 (0.889–0.950) | 1.85 | **+5.50 pp** | **no** |
| mlp | 138 | 30 | 108 | 294 | 0.908 (0.870–0.936) | 1.32 | +4.89 pp | yes |

The cleanup audit reproduces every one of these figures. The XGBoost (+6.80 pp) and LightGBM
(+5.50 pp) marginal-coverage breaches are the "previously documented" joint breaches referenced in
the task; both are disclosed, unchanged, in `phase7_joint_mitigation_audit.csv`.

### 4.3 Reproducibility — LIMITED

- The CSV carries provenance metadata (`provenance_method`, `provenance_source`,
  `provenance_generated_utc = 2026-08-24T12:42`) and is classified in
  `documentation/MASTER_RESEARCH_RESULTS.md` (rows 30–32) and
  `results/diagnostics/FINAL_EXPERIMENTAL_EVIDENCE_LINEAGE.md` (Claim 6.2) as
  **`EXPLORATORY / VALID SECONDARY METHOD`**, "executed during P0/P1 remediation pass".
- **No committed generating script writes this file.** Confirmed by exhaustive search of `src/`;
  the only script referencing it is `phase7_mitigation_cleanup.py` itself (which reads it).
  A related but distinct prespecified re-derivation exists
  (`src/sens_12_m4b_n0_prespecified.py`, "Method (c)", finite-sample corrected), producing
  `results/uncertainty/improved_intersectional_conformal_results.csv` — numerically different
  (up to 4.08 pp), and reconciled as code-valid divergence in master row 32.
- The cleanup's `reproducibility_assessment = "LIMITED: source/method/provenance are present;
  generating script, selection manifest, and runtime log are NOT FOUND IN REPOSITORY"` is
  **accurate**.

### 4.4 Metrics not available

`phase7_joint_mitigation_audit.csv` correctly records `singleton_rate`, `doubleton_rate`,
`calibration_metrics_status`, `fairness_metrics_status` as `NOT FOUND IN REPOSITORY` — the source
artifact genuinely contains only coverage, CI, and mean set size, not per-set-size breakdown,
calibration (intercept/slope/ECE), or BMI/Age fairness deltas for the joint scheme.

### 4.5 Sample-size caveat

N=138 calibration (30 positive) and N=294 test (61 positive) is genuinely sparse. At target
coverage 0.90 the implied quantile level is 0.913; coverage estimates carry ±3–4 pp binomial
uncertainty (see master row 47: LightGBM's 89.46% "miss" is 2 cases of 294). Point estimates
should not be over-interpreted. The `EXPLORATORY_ONLY` status reflects this.

### 4.6 Joint verdict

The cleanup's status `EXPLORATORY_GENUINE_JOINT` maps to
**`JOINT MITIGATION VALID BUT EXPLORATORY ONLY`** and is **defensible and consistent with the
project's own prior classification**. A stricter reading ("REQUIRES CORRECTION / RE-EXECUTION")
is arguable purely on the missing generating script, but: (a) the numbers reproduce from the
frozen artifact, (b) the method is fully specified in provenance + master documentation, (c) an
independent prespecified re-derivation (Method c) already exists and agrees qualitatively. The
exploratory-only ceiling already prevents any load-bearing use. Recommend **retaining
`VALID BUT EXPLORATORY ONLY`** and, as optional hardening, committing a named re-derivation
script if the joint result is ever cited in a manuscript.

---

## 5. Discrepancies / gaps found (none material to the two verdicts)

1. **Report does not quantify the original XGBoost Phase 7 breach.** `PHASE7_MITIGATION_CLEANUP_REPORT.md`
   references "±5 pp marginal tolerance" only in the joint context. The Mondrian XGBoost breach
   (+5.27 pp, `marginal_coverage_before_after.csv`) — the actual motivation for the retuning —
   should be stated explicitly. Quantified here in §3.1.
2. **Pre-existing cross-artifact inconsistency** (93.38% vs 93.85% post-Mondrian XGBoost
   coverage) between `marginal_coverage_before_after.csv` and `MASTER_RESEARCH_RESULTS.md` §189.
   Not caused by the cleanup; flagged for the master-report owner.
3. **`phase7_joint_mitigation_audit.csv` header typo:** `reproducibility_assessment` value reads
   "source/method/provenance are present" — fine — but the free-text is embedded with stray
   whitespace from CSV quoting. Cosmetic only.
4. The cleanup writes its report/decision-log into `documentation/fairness_bmi_investigation/`
   each run (overwriting its *own* prior copies, byte-identical). It does **not** touch any
   historical Phase 7, Phase 0–6, master, or joint artifact. Preservation requirement satisfied.

No discrepancy changes either final status.

---

## 6. Final status (verified)

| Item | Status | Verification |
|---|---|---|
| **XGBoost mitigation** | `NO ACCEPTABLE XGBOOST RETUNING IDENTIFIED` | **CONFIRMED** — reproducible; authorized candidate family only; locked-test untouched during selection; every eligible-gap candidate fails the multi-metric gate by 11–22 pp sensitivity or opposite-direction coverage. |
| **Joint mitigation** | `EXPLORATORY_GENUINE_JOINT` → **`JOINT MITIGATION VALID BUT EXPLORATORY ONLY`** | **CONFIRMED** — genuinely joint (N=138 direct slice), not sequential; numbers reproduce from frozen artifact; reproducibility LIMITED (no committed generator); N=138/294 too sparse for primary use; XGBoost +6.80 pp and LightGBM +5.50 pp marginal breaches disclosed. |

## 7. Remaining limitations (unchanged by this work)

- No committed script regenerates `joint_intersectional_mitigation.csv` from raw inputs.
- Joint calibration cell (N=138; 30 pos) and joint test cell (N=294; 61 pos) are small;
  coverage CIs are wide (~±3–4 pp).
- Joint scheme has no calibration or fairness metrics recorded; only coverage / set size.
- XGBoost's conformal marginal-coverage tolerance breach (Mondrian +5.27 pp; joint +6.80 pp)
  is **unresolved** and remains a disclosed limitation — no authorized intervention removes it.
- OOF development half is a single 50/50 parity split; subgroup development estimates are noisy.
- No external or out-of-sample validation was performed (out of scope per project documentation).
