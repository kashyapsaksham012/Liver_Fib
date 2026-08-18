# Human-Independent Spot Check (Required, Not Optional)

**Generated:** 2026-08-18 — this audit, and every audit before it in this project, was performed
by the same AI agent that also executed the pipeline being audited. **No AI-generated check in
this repository is independent of the AI that wrote the code it is checking.** The only genuinely
independent verification available is one performed by you, manually, outside this session.

> **Update, 2026-08-18 (Pre-Calibration Closure pass):** the recommended primary target below has
> changed from the hyperparameter count to **locked test-set integrity**. The hyperparameter count
> (84) has since been independently, programmatically re-verified twice by this AI (AST-parsed
> from source and cross-checked against the runtime registry), so it is no longer the check most
> in need of a genuinely human, non-AI eye. Test-set integrity has not been spot-checked by a human
> at all yet, and touching the test set incorrectly is the single highest-consequence class of error
> in this project (it would silently invalidate every locked discrimination/calibration result). The
> original hyperparameter-count instructions are retained below, unmodified, as a secondary option —
> nothing is deleted, per this project's standing rule against silently rewriting prior guidance.

## Primary recommended check: **locked test-set integrity (N = 2,146)**

Chosen because it has not yet been independently spot-checked by a human, and because an error in
the test set (wrong size, accidental overlap with training, accidental modification after locking)
would be the most consequential possible failure mode — it would silently invalidate every
discrimination result already reported, and every future calibration/fairness/uncertainty result
computed on it.

### Manual method (do this yourself, in a fresh terminal, not by asking an AI to do it for you)

```bash
cd liver_fibrosis_research
wc -l data/processed/splits/test_ids.csv
shasum -a 256 data/processed/splits/test_ids.csv
```

- Expect `wc -l` to report **2147** lines (2,146 data rows + 1 header row).
- Record the SHA-256 hash yourself and compare it against the value below, computed live by this
  AI immediately before writing this document. If your hash matches, you have independently
  confirmed the file has not changed since this audit inspected it — a direct, byte-level
  reproducibility check, not a claim you have to trust.

| Field | Value |
|---|---|
| Selected number | Locked test-set row count |
| Manual method | `wc -l` + `shasum -a 256` on `test_ids.csv`, run by hand |
| Expected row count | 2,146 data rows (2,147 including header) |
| This audit's live-computed SHA-256 | `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| **You must fill in:** your manually-observed hash | _____ |
| Match? | _____ |

### Optional second check under this target: independent participant-count recount

```bash
python3 -c "import pandas as pd; print(len(pd.read_csv('data/processed/splits/test_ids.csv')))"
```
Expect **2146**.

---

## Secondary (previously primary) check: hyperparameter configuration count = 84

Retained unmodified from the prior audit pass. Chosen originally because it is the most
mechanically verifiable by hand (a small arithmetic exercise) and because it was the specific
number this audit was most explicitly instructed to stop trusting on prose alone. Still a valid,
useful check — just no longer the top-priority one, since it has already been independently
re-derived twice by this AI (see `results/pre_calibration/source_of_truth_matrix.csv` and the
prior end-to-end audit's AST-parse verification) whereas the test-set hash above has not.

## Manual method (do this yourself, in a fresh terminal, not by asking an AI to do it for you)

```bash
cd liver_fibrosis_research
grep -A 3 '"logistic"' src/phase3_05_train_and_tune.py | grep 'grid ='
grep -A 4 '"random_forest"' src/phase3_05_train_and_tune.py | grep 'grid ='
grep -A 5 '"xgboost"' src/phase3_05_train_and_tune.py | grep -A1 'grid ='
grep -A 5 '"lightgbm"' src/phase3_05_train_and_tune.py | grep -A1 'grid ='
grep -A 4 '"mlp"' src/phase3_05_train_and_tune.py | grep -A1 'grid ='
```

Then by hand:
- logistic: `est__C` has 6 values, grid search (exhaustive) → **6**
- random_forest: 3 × 4 × 3 = 36 possible, but `n_iter=20` (randomized, capped) → **20**
- xgboost: 3 × 4 × 3 × 3 = 108 possible, `n_iter=20` → **20**
- lightgbm: same as xgboost → **20**
- mlp: 3 × 3 × 2 = 18 possible, grid search (exhaustive) → **18**
- Sum: 6 + 20 + 20 + 20 + 18 = **84**

Then independently confirm against the actual runtime log:
```bash
wc -l results/tables/phase3_hyperparameter_search_registry.csv
```
Expect 85 (84 data rows + 1 header).

| Field | Value |
|---|---|
| Selected number | Hyperparameter configuration count |
| Manual method | Hand-count grid dimensions from source code + arithmetic |
| Expected result | 84 |
| This audit's automated result | 84 (AST-parsed) |
| **You must fill in:** your manually-observed result | _____ |
| Match? | _____ |

## Second recommended check (optional, for extra confidence): **test N = 2,146**

```bash
python3 -c "import pandas as pd; print(len(pd.read_csv('data/processed/splits/test_ids.csv')))"
```
This is a single-line, trivially independent command you can run yourself and compare against the
`2,146` figure claimed throughout this audit.

## Why this section exists

An AI audit of an AI's own work, however rigorous in its methodology, cannot substitute for a
human independently reproducing at least one number by their own hand. This document is that
explicit invitation — please actually run at least the first command block yourself before
treating this audit's "84" as settled.

**Status, as of the Pre-Calibration Closure pass (2026-08-18): HUMAN SPOT-CHECK — NOT YET
PERFORMED.** Neither the primary (test-set hash) nor secondary (hyperparameter count) check has
been executed by a human yet. This status must remain exactly as stated until a human — not this
AI — actually runs the commands above in their own terminal and fills in the blank fields. This
AI must not, and does not, claim to have performed this check on the user's behalf; doing so
would defeat the entire purpose of an independent check.
