# Race/Ethnicity Variable Verification: RIDRETH1 vs RIDRETH3

**Generated:** 2026-08-18 13:27:26

## Official definitions (verified against live P_DEMO codebook, https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm)

- **RIDRETH1** -- 'Recode of reported race and Hispanic origin information', 5 categories: 1=Mexican American, 2=Other Hispanic, 3=Non-Hispanic White, 4=Non-Hispanic Black, 5=Other Race - Including Multi-Racial. **Non-Hispanic Asian participants are folded into category 5** and are not separately identifiable.
- **RIDRETH3** -- Same recode 'with Non-Hispanic Asian Category', 6 categories: 1=Mexican American, 2=Other Hispanic, 3=Non-Hispanic White, 4=Non-Hispanic Black, 6=Non-Hispanic Asian, 7=Other Race - Including Multi-Racial. **Preserves Non-Hispanic Asian as a distinct, analyzable category.**

> The NHANES codebook itself does not issue a directive to prefer one variable over the other -- this is a study-design choice. What the codebook does establish as fact is the category structure above, which is what determines the fairness-analysis implication below.

## Empirical cross-tabulation in this project's master dataset (N=10409)

|   RIDRETH1 |   1.0 |   2.0 |   3.0 |   4.0 |   6.0 |   7.0 |
|-----------:|------:|------:|------:|------:|------:|------:|
|          1 |  1273 |     0 |     0 |     0 |     0 |     0 |
|          2 |     0 |  1054 |     0 |     0 |     0 |     0 |
|          3 |     0 |     0 |  3519 |     0 |     0 |     0 |
|          4 |     0 |     0 |     0 |  2762 |     0 |     0 |
|          5 |     0 |     0 |     0 |     0 |  1225 |   576 |

- RIDRETH1 category 5 ('Other Race/Multi-Racial'): N=1801
- This same population splits under RIDRETH3 into: category 6 ('Non-Hispanic Asian'), N=1225, and category 7 ('Other Race/Multi-Racial'), N=576

**Confirmed empirically: RIDRETH1 statistically erases the Non-Hispanic Asian subgroup by merging it into 'Other'; RIDRETH3 keeps it distinguishable at N=1225, well above the N>=100 total-sample-size feasibility bar (though see subgroup_outcome_feasibility.csv for the outcome-positive-count caveat, which still applies to this subgroup).**

## Recommendation for Phase 2 (documented here, not silently decided)

Use **RIDRETH3** as the PRIMARY race/ethnicity variable for the fairness analysis, because it is strictly more granular than RIDRETH1 and preserves a demographic group (Non-Hispanic Asian) that this study's stated fairness objective explicitly cares about. RIDRETH1 is retained in the master dataset for comparability with the substantial body of prior NHANES-based clinical literature that reports RIDRETH1 categories, but should not be the primary subgroup variable for the fairness analysis itself.

**This is a recommendation, not a Phase 1 finalization.** Whether to also collapse or retain small categories, and which variable to use for any specific downstream analysis, remains a Phase 2 protocol decision. No race/ethnicity category has been silently collapsed by this remediation -- both RIDRETH1 and RIDRETH3, with their full native category sets, are preserved unmodified in `nhanes_master_phase1.parquet`.
