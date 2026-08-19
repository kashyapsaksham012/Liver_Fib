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
| Date performed | **NOT SUPPLIED** — the researcher-supplied result (below) did not include a date; not fabricated by this session |
| Researcher (name) | **NOT SUPPLIED** — not fabricated by this session |
| Check selected | (x) Primary: test-set SHA-256 |
| Exact command run | `wc -l data/processed/splits/test_ids.csv` and `shasum -a 256 data/processed/splits/test_ids.csv` (as specified in `human_spot_check.md`) |
| Expected result (from `human_spot_check.md`) | 2,147 total lines (2,146 data rows + header); SHA-256 `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| Observed result (as reported to this session by the researcher) | Total file lines = 2147; data rows = 2146; SHA-256 = `a9e54315fb928342ed54f9b5bf940aa21106326c7e783c9089f44672a6624779` |
| PASS / FAIL | PASS (observed hash matches expected exactly, as reported) |
| Notes | **This entry was transcribed by an AI session from a result the researcher reported in a prompt, not typed into this file by the researcher's own hand.** Per the record's own governing rule ("no AI session may mark this PASS... on the researcher's behalf"), the AI is not the one asserting PASS — it is transcribing an assertion the researcher already made. The Date and Researcher-name fields could not be completed because they were not supplied, and were deliberately left unfabricated rather than guessed. |

## Status

**HUMAN SPOT-CHECK COMPLETED INDEPENDENTLY, BUT REPOSITORY RECORD INCOMPLETE.**

The researcher reported having personally run the check and observed a PASS result matching the
expected SHA-256 exactly. That result is transcribed above. However, this record is not fully
complete: the researcher's name and the date performed were not supplied and have not been
fabricated. The record should be completed by the researcher directly (filling in the two
remaining fields, or overwriting this entry in their own words) to be considered a fully
self-contained, independently verifiable record. No AI session performed, re-performed, or
independently verified this check — the underlying verification remains the researcher's own.
