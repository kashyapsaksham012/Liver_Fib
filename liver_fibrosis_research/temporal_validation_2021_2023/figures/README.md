# Temporal-validation evidence figures

Six figures for the manuscript's temporal-validation section (§3.12 / §3.7c).
Generated from the frozen result CSVs of `temporal_validation_2021_2023/` and
`pooled_model_update_2017_2023/` (plus read-only reads of the frozen
`results/uncertainty/*` for the 2017–2020 conformal comparison in T3).

```bash
python3 temporal_validation_2021_2023/figures/make_temporal_figures.py
```
Each figure is written as `.png` (200 dpi) and `.pdf`.

| file | shows | manuscript use |
|---|---|---|
| **figT1_replication_summary** | each finding × verdict (5/6 core replicated; discrimination attenuated; age-60+ sensitivity not replicated as pre-registered) | §3.12 headline figure — one glance = "the reliability findings held" |
| **figT2_bmi_gap_across_tiers** | Obese−Normal sensitivity gap per model: development (27–48 pp) → 2021–2023 frozen model (63–72 pp) → 2021–2023 after pooled retrain (38–69 pp) | §3.7c — "replicates, widens, not resolved by updating" |
| **figT3_conformal_two_cycles** | marginal / BMI-Obese / Age-60+ / Obese∩60+ coverage, 2017–2020 vs 2021–2023, per model | §3.12 — "marginal on target both cycles; subgroups under-cover both cycles" |
| **figT4_auroc_decline_decomposed** | (a) within-band AUROC old vs new — Normal-BMI 0.82→0.62, Obese/60+ unchanged; (b) covariate-shift reweighting recovers only ~17% | §3.12 — the decline is concept drift, concentrated in the paper's subgroup |
| **figT5_shortcut_across_tiers** | matched-stiffness `obese` OLS coefficient at 2017–2020 / temporal / pooled, per model (all p < 0.001) | §3.4 / §3.7c — the mechanism is stable across every evidence tier |
| **figT6_nothing_fixes_it** | every intervention (post-hoc battery, Mondrian, selective deferral, training-time reweighting, model updating) × verdict | §3.7 / §6 — "the failure is structural" summary figure |

## Sources (every number traces)

- T1 ← `temporal_validation_2021_2023/results/temporal_replication_verdicts.csv`
- T2 ← `temporal_fairness_results.csv` + `pooled_model_update_2017_2023/results/pooled_fairness_results.csv` (2021–2023 slice)
- T3 ← `temporal_conformal_results.csv` + frozen `results/uncertainty/{marginal_coverage_test_set,subgroup_coverage,intersectional_coverage_ci}.csv`
- T4 ← `temporal_drop_slice_matched.csv`, `temporal_drop_covariate_shift.csv`
- T5 ← `temporal_matched_stiffness_shortcut.csv` + `pooled_shortcut_results.csv`
- T6 ← the frozen mitigation registry (`FINAL_SCIENTIFIC_FINDINGS.md` §14) + `pooled_verdicts.csv`

Pinned by `../src/verify_temporal.py` (22/22) and `../../pooled_model_update_2017_2023/src/verify_pooled.py` (16/16).
