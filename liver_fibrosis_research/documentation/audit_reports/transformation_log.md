# Transformation Log

**Generated:** 2026-08-18 13:27:21

| Variable | Original | Transformation | Reason | Result | Timestamp |
|---|---|---|---|---|---|
| ALL::numeric columns | raw SAS xport (may contain unconverted special-missing sentinel 5.397605346934028e-79) | recode SAS special-missing sentinel to NaN | Prevent silent corruption of min/mean/missingness statistics | sentinel recoded to NaN; see special_missing_code_audit.csv for exact scope | 2026-08-18 13:27:21 |
| P_LUX.xpt::SEQN | float64 (SAS) | convert to Int64 | Ensure integer key consistency | Int64 | 2026-08-18 13:27:21 |
| P_DEMO.xpt::SEQN | float64 (SAS) | convert to Int64 | Ensure integer key consistency | Int64 | 2026-08-18 13:27:21 |
| P_BMX.xpt::SEQN | float64 (SAS) | convert to Int64 | Ensure integer key consistency | Int64 | 2026-08-18 13:27:21 |
| P_BIOPRO.xpt::SEQN | float64 (SAS) | convert to Int64 | Ensure integer key consistency | Int64 | 2026-08-18 13:27:21 |
| P_CBC.xpt::SEQN | float64 (SAS) | convert to Int64 | Ensure integer key consistency | Int64 | 2026-08-18 13:27:21 |
| P_GLU.xpt::SEQN | float64 (SAS) | convert to Int64 | Ensure integer key consistency | Int64 | 2026-08-18 13:27:21 |
| P_TRIGLY.xpt::SEQN | float64 (SAS) | convert to Int64 | Ensure integer key consistency | Int64 | 2026-08-18 13:27:21 |
| P_HDL.xpt::SEQN | float64 (SAS) | convert to Int64 | Ensure integer key consistency | Int64 | 2026-08-18 13:27:21 |
