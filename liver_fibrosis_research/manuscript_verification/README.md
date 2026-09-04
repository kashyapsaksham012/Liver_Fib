# Manuscript number-verification harness

**Step 1 of the "fix the paper's internal problems" plan.** A read-only checker
that pins every numeric claim in the manuscript to the frozen result artifact it
must come from, and flags draft-state hedges in the prose.

Nothing here modifies `results/`, `data/`, `models/`, or `documentation/`. It is
safe to run at any time and is meant to run in CI / as a pre-commit hook so a
number can never silently drift from its artifact again.

## Run

```bash
python3 manuscript_verification/verify.py                 # all checks + hedge scan
python3 manuscript_verification/verify.py --strict        # also non-zero exit on hedges
python3 manuscript_verification/verify.py --only INT-01-TOP4,GEN-01-INTERCEPT
python3 manuscript_verification/verify.py --manuscript documentation/manuscript/MANUSCRIPT_DRAFT.md
python3 manuscript_verification/verify.py --json          # machine-readable
```

Exit code is non-zero if any check FAILs or ERRORs (or, with `--strict`, if the
hedge scan finds anything). Reports are written to `report/`.

## Files

| file | what |
|---|---|
| `verify.py` | engine + hedge scanner + reporter. Stdlib only. |
| `checks.py` | the check definitions — **edit this to add claims**. Schema in its docstring. |
| `report/verification_report.md` / `.csv` | generated on each run |
| `FINDINGS.md` | what the first run turned up and how each item was resolved |
| `PDF_REPO_RECONCILIATION.md` | every place the desktop PDF diverges from the repo manuscript, with the correct value + source — for the PDF rebuild |
| `figure_manifest.csv` | each manuscript figure → source artifact → committed PNG → status (flags the M4b figures Amendment #20 removed) |
| `reference_bylines.md` | resolved `[author list to confirm]` markers (web lookup, needs co-author verification) |

## What it covers now

43 checks over the manuscript's `MANUSCRIPT_READY` claims and the cohort numbers:
cohort N / positives / prevalence; discrimination band + per-model AUROC + PR-AUC
+ the 0/10 FDR result; OOF and locked-test calibration (raw and recalibrated);
the BMI-Obese sensitivity gap (band, q-values, 5/5 significance) and the
matched-stiffness shortcut; the Age-60+ secondary observation (band, direction,
4/5 significance); marginal / BMI-Obese / Age-60+ / intersectional conformal
coverage and the over-covering subgroups; the NHB holdout (AUROC, **raw**
calibration intercepts and slopes); the severity-graded secondary outcomes
(AUROC bands **and** the relabel-only flags that resolve the "was it executed?"
question); the training-time-mitigation verdict and its costs; and predictor
importance.

Two checks are deliberately pinned to values the **desktop PDF got wrong**, so a
rebuilt manuscript can't reintroduce them:

- `GEN-01-INTERCEPT` — NHB holdout calibration intercepts are **-0.58 to -2.17
  (raw, no recalibration performed)**. The PDF §IV-G printed "-0.38 to -0.18" and
  hedged about "a separate summary document".
- `SECOUT-01-RELABEL-ONLY` / `-NO-REFIT` / `-NO-TESTACCESS` — the severity
  outcomes were a relabel-only pass (Amendment #15): no retrain, no Platt refit,
  no conformal repeat, locked test not re-accessed. The PDF §IV-H said the
  execution status was uncertain.

## Extending

Add a dict to `CHECKS` in `checks.py`. Copy the nearest example, point `source`
at the artifact, and paste the number your manuscript prints. If the check
FAILs, exactly one of {manuscript, artifact} is wrong — and post-`evidence-freeze`
the artifact wins, so the manuscript gets corrected.
