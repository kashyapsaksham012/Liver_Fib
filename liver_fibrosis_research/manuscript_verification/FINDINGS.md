# Manuscript number-verification — findings & resolution log

Target: `documentation/manuscript/MANUSCRIPT_DRAFT.md`.
Run: `python3 manuscript_verification/verify.py --strict`

## Current state

**43 / 43 numeric checks PASS. Hedge scan clean.** `--strict` exit 0.

Every headline number in the repo manuscript reconciles exactly with the frozen
result artifact it cites — discrimination, calibration, the BMI-Obese sensitivity
gap, conformal coverage (marginal / subgroup / intersectional), the NHB holdout,
the severity-graded secondary outcomes, the training-time-mitigation verdict, and
predictor importance.

## Issues found on the first run and how they were resolved

### 1. §3.11 predictor-importance sentence overstated → FIXED

- **Was:** "ALT, AST, BMI, and age were the top four predictors across all five
  families (permutation importance and standardised logistic coefficients)."
- **Artifact:** true for logistic (by coefficient), XGBoost and LightGBM. For
  **random forest** HDL (#4) displaces AST (#5); for the **perceptron** the order
  is BMI, AST, age, albumin (ALT is #9).
- **Now:** §3.11 rewritten to state exactly that — BMI first in every family and
  by logistic coefficient; age second in four of five; the top-four = {BMI, age,
  ALT, AST} for logistic/XGBoost/LightGBM only; RF and MLP deviations named.
- **Checks:** `INT-01-BMI-TOP1`, `INT-01-BMI-COEF-TOP1`, `INT-01-TOP4-BOOSTING`,
  `INT-01-RF-HDL` — all pass against the corrected wording.

### 2. Nine draft-state hedges in the prose → RESOLVED

| was | action |
|---|---|
| "Still outstanding for submission" checklist in the draft body (v3 changelog) | replaced with a pointer to `SUBMISSION_CHECKLIST.md` + `PDF_REPO_RECONCILIATION.md` |
| refs 4, 5, 13, 14 `[author list to confirm]` | bylines filled (web lookup, Sept 2026; `reference_bylines.md`) |
| ref 2 `[author list to confirm]` | first three authors filled; full list flagged (OA HTML) |
| refs 7, 20 `[author list to confirm]` | publisher pages 403'd; kept as explicit "byline to confirm — see reference_bylines.md" |
| ref 4 year "2020" | corrected to **2022;34(1):98–103** (PubMed 32976186) |
| Appendix B "A full TRIPOD+AI checklist is to be completed and submitted" | → "The completed TRIPOD+AI checklist is provided as a supplement" (consistent with the Declarations, which already commit to this) |

Still genuinely open (tracked, not hidden): refs 7 and 20 full bylines; ref 13
journal page range; the official TRIPOD+AI form with page numbers
(`SUBMISSION_CHECKLIST.md` A9); the two-screener literature search (A-list); the
participant flow diagram (A5).

## Pinned against the desktop PDF's errors

Two check groups deliberately encode the correct value so a rebuilt PDF cannot
reintroduce the PDF's mistakes:

- `GEN-01-INTERCEPT` — NHB holdout calibration intercepts are **−0.58 to −2.17
  (raw; no recalibration)**. PDF §IV-G had "−0.38 to −0.18" + a hedge.
- `SECOUT-01-RELABEL-ONLY` / `-NO-REFIT` / `-NO-TESTACCESS` — the severity
  outcomes are relabel-only (Amendment #15): `retrained`, `platt_refit`,
  `conformal_repeated`, `test_set_reaccessed_for_model_fitting` all `False` for
  all 10 rows. PDF §IV-H said the execution status was uncertain.

Full PDF↔repo divergence list: `PDF_REPO_RECONCILIATION.md`.
