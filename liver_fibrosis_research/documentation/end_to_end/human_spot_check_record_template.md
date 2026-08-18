# Human Spot-Check Record Template

**Purpose:** a genuinely independent verification, performed by a human researcher — not an AI —
outside this session. See `documentation/end_to_end/human_spot_check.md` for the full rationale,
target selection, and exact commands. This template is where you record what you personally
observed when you ran them.

## Before you start

1. Open a **fresh, independent terminal** (not one an AI is controlling or has driven).
2. Do **not** ask an AI assistant to run the command for you and report the result back — that
   defeats the purpose of an independent check.
3. `cd` to the repository yourself:
   ```
   cd "/Users/sakshamkashyap/Desktop/Research /liver_fibrosis_research"
   ```
4. Run the exact command(s) shown in `human_spot_check.md` for your selected check.
5. Read the terminal output yourself.
6. Compare it against the expected value recorded in `human_spot_check.md`.
7. Fill in every field below yourself.

## Record

| Field | Value |
|---|---|
| Date performed | _____ |
| Researcher (name) | _____ |
| Check selected | ( ) Primary: test-set SHA-256 &nbsp; ( ) Primary: test-set N=2,146 &nbsp; ( ) Secondary: 84 hyperparameter configs &nbsp; ( ) Other (specify): _____ |
| Exact command run | _____ |
| Expected result (from `human_spot_check.md`) | _____ |
| Observed result (paste your actual terminal output) | _____ |
| PASS / FAIL | _____ |
| Notes (anything unexpected, environment differences, etc.) | _____ |

## Status until this record is filled in

**HUMAN SPOT-CHECK — NOT YET PERFORMED.**

This status is not changed by any AI session. It changes only when a human researcher fills in
the table above with a real, personally-observed result and the record is committed. No AI
session may mark this PASS, FAIL, or "performed" on the researcher's behalf.
