# Hyperparameter Configuration Count Verification

**Generated:** 2026-08-18 (final end-to-end audit) — this is a **live AST parse of the source
code**, not a read of any CSV the training script itself produced (which would be circular).

## Method

Used Python's `ast` module to parse `src/phase3_05_train_and_tune.py`'s `build_pipeline()`
function directly, extracting each model branch's literal `grid` dict and `search_type, n_iter`
assignment as actual parsed syntax nodes (`ast.literal_eval`), not string matching or eyeballing.
For each model: `full_grid_size` = product of all grid dimension lengths; `evaluated_configs` =
`full_grid_size` if `search_type=="grid"` (exhaustive), else `min(n_iter, full_grid_size)` for
`"randomized"` (`RandomizedSearchCV` evaluates exactly `n_iter` draws, capped at the full space).

## Result

| Model | Full grid size (all possible combos) | Search type | n_iter | **Evaluated configs** |
|---|---|---|---|---|
| logistic | 6 | grid (exhaustive) | — | **6** |
| random_forest | 36 (3×4×3) | randomized | 20 | **20** |
| xgboost | 108 (3×4×3×3) | randomized | 20 | **20** |
| lightgbm | 108 (3×4×3×3) | randomized | 20 | **20** |
| mlp | 18 (3×3×2) | grid (exhaustive) | — | **18** |
| **TOTAL** | | | | **84** |

## Independent cross-check against the actual `cv_results_` output

`results/tables/phase3_hyperparameter_search_registry.csv` (built from each search object's
`cv_results_`, i.e. what `GridSearchCV`/`RandomizedSearchCV` actually evaluated at runtime) has
**exactly 84 rows**, with **per-model row counts matching the AST-parsed expectation exactly**:
logistic=6, random_forest=20, xgboost=20, lightgbm=20, mlp=18.

## Conclusion

**`actual_configuration_count == 84` — CONFIRMED, via two independent methods that agree exactly:**
(1) static AST parse of the grid-definition source code, entirely independent of any file the
training script wrote; (2) the row count of the actual runtime search-result log. **The figure "84"
in the Phase 3 reports was correct — not a manually transcribed or unverified number.**
