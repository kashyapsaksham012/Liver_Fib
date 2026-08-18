# Phase 1 — Data Assembly

## Project
Fairness, Calibration, and Uncertainty in Machine Learning-Based Liver Fibrosis Risk Prediction Across Demographic Groups

## Data Source
NHANES 2017–March 2020 Pre-Pandemic Combined Release  
https://wwwn.cdc.gov/nchs/nhanes/

## Phase 1 Objective
Construct a clean, traceable, participant-level analytical dataset. No modeling.

## How to Run

```bash
cd liver_fibrosis_research
pip install -r requirements.txt

python src/01_data_inventory.py    # File inventory
python src/02_load_nhanes.py       # Load + variable dictionary
python src/03_audit_files.py       # Per-file audits
python src/04_merge_nhanes.py      # SEQN-based merge
python src/05_missingness_audit.py # Missingness analysis
python src/06_quality_audit.py     # Plausibility + cohort flow
python src/07_create_master_dataset.py  # Data dictionary + final report
```

## Output Directory
- `data/interim/nhanes_master_phase1.parquet` — master dataset
- `documentation/audit_reports/` — all audit reports
- `documentation/data_dictionary/` — data dictionary
- `results/figures/` — descriptive plots
- `PHASE1_DATA_ASSEMBLY_REPORT.md` — final Phase 1 report

## CRITICAL NOTES
- Do NOT modify files under `data/raw/`
- Do NOT begin modeling until Phase 2
- Do NOT select fibrosis threshold based on ML performance
- Laboratory files must be downloaded before Phase 1 is complete

## Required Lab Files (not yet downloaded)
| File | Component | Key Variables |
|---|---|---|
| P_BIOPRO.XPT | Biochemistry | AST, ALT, Albumin, Bilirubin |
| P_CBC.XPT | Blood Count | Platelets |
| P_GLU.XPT | Glucose | Fasting glucose |
| P_TRIGLY.XPT | Lipids | Triglycerides |
| P_HDL.XPT | Lipids | HDL |
