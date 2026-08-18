# Phase 1 — Data Assembly, Remediation & Closure

## Project
Fairness, Calibration, and Uncertainty in Machine Learning-Based Liver Fibrosis Risk Prediction Across Demographic Groups

## Data Source
NHANES 2017–March 2020 Pre-Pandemic Combined Release
https://wwwn.cdc.gov/nchs/nhanes/

## Phase 1 Objective
Construct a clean, traceable, participant-level analytical dataset. No modeling.

## Status
**PHASE 1 — COMPLETE AND FROZEN** (see `PHASE1_DATA_ASSEMBLY_REPORT.md` Section V for the current
readiness decision, computed programmatically, and `documentation/audit_reports/internal_validation_results.csv`
for all 24 automated test results). Every named data-feasibility cohort is defined exactly once in
`src/_cohorts.py` — the single canonical source every script imports from.

## How to Run

```bash
cd liver_fibrosis_research
pip install -r requirements.txt

python src/01_data_inventory.py              # Raw file inventory, readability & release-consistency checks
python src/02_load_and_profile.py            # Load + complete variable dictionary + per-file JSON profiles
python src/03_audit_lux_demo_bmx.py          # P_LUX / P_DEMO / P_BMX dedicated audits (official quality def.)
python src/04_audit_laboratory.py            # Laboratory file audits (fasting-subsample structure documented)
python src/05_merge_nhanes.py                # SEQN linkage audit + merge + sentinel-fix transformation log
python src/06_missingness_audit.py           # Missingness analysis (overall + by group)
python src/07_quality_and_plausibility_audit.py  # Canonical, arithmetically-verified cohort flow (uses _cohorts.py)
python src/08_subgroup_feasibility.py        # Subgroup feasibility, Stage A (total N)
python src/09_laboratory_plausibility_audit.py   # Comprehensive laboratory plausibility audit
python src/10_special_missing_code_audit.py  # SAS special-missing sentinel audit
python src/11_race_ethnicity_verification.py # RIDRETH1 vs RIDRETH3 evidence-based comparison
python src/12_subgroup_outcome_feasibility.py    # Subgroup feasibility, Stage B (outcome-positive N + classification)
python src/13_broad_vs_fasting_cohort.py     # Broad-lab vs fasting-subsample candidate cohorts (canonical)
python src/14_comprehensive_leakage_audit.py # Leakage classification for every candidate variable
python src/15_create_master_dataset.py       # Master data dictionary + variable source verification
python src/16_table1_and_figures.py          # Descriptive Table 1 + required figure set
python src/19_cohort_reconciliation.py       # Discrepancy tracing + cohort definition table + reconciled counts
python src/20_denominator_registry.py        # Denominator registry for every reported statistic
python src/21_phase2_open_decisions.py       # Phase 2 open-decisions document
python src/17_validation_tests.py            # Automated internal validation tests (24 tests, halts on failure)
python src/18_generate_phase1_report.py      # Final Phase 1 report (MUST run last -- depends on 19/20/21 outputs)
```

**Note on order:** `18_generate_phase1_report.py` reads outputs from `19`, `20`, and `21`, so those three
must run before it. `17_validation_tests.py` should also run after `19` so the closure-specific tests
(TEST17-24) can check the discrepancy-trace and reconciled-counts files.

## Output Directory
- `data/interim/nhanes_master_phase1.parquet` — master dataset
- `documentation/audit_reports/` — all audit reports, including `archive/` (pre-closure snapshots)
- `documentation/data_dictionary/` — data dictionary + variable source verification
- `documentation/source_metadata/` — survey design notes, references, LUX quality-rule source
- `results/figures/`, `results/tables/` — descriptive plots, Table 1, cohort definition/reconciliation tables
- `PHASE1_DATA_ASSEMBLY_REPORT.md` — final Phase 1 report (sections A–V)

## Canonical Cohort Definitions
Every named data-feasibility cohort (source, non-missing-outcome, quality-valid, adult subsets, broad-lab,
fasting-extended, etc.) is defined exactly once in `src/_cohorts.py`. No other script may recompute a
cohort mask independently — see `results/tables/phase1_cohort_definition_table.md` for the full registry
and `documentation/audit_reports/phase1_denominator_registry.csv` for every reported statistic's exact
numerator/denominator/source.

## CRITICAL NOTES
- Do NOT modify files under `data/raw/`
- Do NOT begin modeling until Phase 2
- Do NOT select fibrosis threshold based on ML performance
- Unverified auxiliary variables must NOT enter modeling or scientific derived outcomes without source
  verification (enforced programmatically — see Report Section M, TEST22/TEST23)
- All candidate outcome thresholds, quality-inclusion criteria, adult-only restriction, predictor set,
  and race/ethnicity grouping remain OPEN Phase 2 decisions — see
  `documentation/audit_reports/phase2_open_decisions.md` and Report Section T
