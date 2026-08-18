# Human-Independent Spot Check (Required, Not Optional)

**Generated:** 2026-08-18 — this audit, and every audit before it in this project, was performed
by the same AI agent that also executed the pipeline being audited. **No AI-generated check in
this repository is independent of the AI that wrote the code it is checking.** The only genuinely
independent verification available is one performed by you, manually, outside this session.

## Recommended number to verify: **hyperparameter configuration count = 84**

Chosen because it is the most mechanically verifiable by hand (a small arithmetic exercise) and
because it was the specific number this audit was most explicitly instructed to stop trusting on
prose alone.

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
