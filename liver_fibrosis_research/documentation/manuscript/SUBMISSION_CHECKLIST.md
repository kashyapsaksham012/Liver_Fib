# Submission checklist — Track 2.5

**Date:** 2026-08-27. What has to be true before the manuscript goes to a journal, plus drafts of
the boilerplate the author must finalise. Target venue and ladder: `TARGET_VENUE_DECISION.md`.

---

## A. Blocking — must be done

| # | Item | Owner | Status |
|---|---|---|---|
| A1 | Amendment #19 executed and folded into the manuscript (§2.8b, §3.7b, Table 4, §4, §5, abstract) → **v5** | author runs; then integrate | ⏳ pending Track 1 |
| A2 | `experiment/training-time-mitigation` merged into `consolidation/evidence-freeze` | — | ⏳ after A1 |
| A3 | Reference list: paste remaining full author bylines (rows marked *[author list to confirm]* in `REFERENCE_VERIFICATION.md`); retrieve the *CHEST* 2026 byline | author / co-author | ⏳ |
| A4 | Full-text re-check of the two flagged claims: ref [1] calibration wording, ref [23] subgroup-coverage claim | co-author | ⏳ |
| A5 | Participant **flow diagram** (item 17a) built from the §2.1 counts | author (figure tool) | ❌ |
| A6 | Figures 1–5 + S1–S2 assembled / relabelled to the target journal's style (PNGs exist; no re-computation) | author (figure tool) | ❌ |
| A7 | Funding, conflicts, ethics, protocol statements added (drafts below) | author | ❌ |
| A8 | "Data and code availability" paragraph added (draft below) | author | ❌ |
| A9 | TRIPOD+AI checklist transcribed onto the official form with page numbers (`TRIPOD_AI_CHECKLIST.md` is the map) | author | ⏳ |
| A10 | One other person reads every Results number against the CSVs and the whole manuscript against `DO_NOT_CLAIM.md` | co-author / trusted reader | ❌ |
| A11 | Preprint posted to **medRxiv** (v5) | author | ⏳ after A1–A9 |

## B. Strongly recommended

- B1 A second screener re-runs the literature search with recorded PubMed/Embase hit counts
  (`LITERATURE_SEARCH_RECORD.md` §"what a co-author still needs to do").
- B2 Re-scan the 2026 conformal-fairness literature immediately before submission (fast-moving).
- B3 Language/copy edit pass (the draft is dense; tighten §3 and §4).
- B4 Decide author list — if it stays single-author, the cover letter should note the internal
  audit trail (multiple documented review passes) as the substitute for co-author review, and
  A10 becomes essential.

---

## C. Boilerplate drafts (author to finalise)

### Funding
> This research received no specific grant from any funding agency in the public, commercial, or
> not-for-profit sectors. The author is an independent researcher and self-funded this work.

### Competing interests
> The author declares no competing interests.

### Ethics approval and consent
> This is a secondary analysis of the publicly available, de-identified National Health and
> Nutrition Examination Survey (NHANES) 2017–March 2020 data. The NHANES protocol was approved by
> the National Center for Health Statistics (NCHS) Research Ethics Review Board, and all
> participants provided written informed consent. No additional ethical approval was required for
> this analysis of public data.

### Protocol / pre-registration
> The analysis protocol — cohort definition, primary outcome (`LUXSMED ≥ 8.2 kPa`), the ten
> predictors, the fairness dimensions, the conformal target, and the multiplicity strategy — was
> frozen before any model was trained (hash-verified). All subsequent deviations are recorded as
> dated protocol amendments (20 in total). The protocol, amendment registry, and a machine-readable
> claim registry are provided with the code (below). The study was not registered on a public
> trial/registry platform, as it is a methodological analysis of existing public data rather than a
> prospective clinical study.

### Data and code availability
> The NHANES 2017–March 2020 public-use files are available from the NCHS
> (https://www.cdc.gov/nchs/nhanes/). All analysis code, the frozen analysis protocol and amendment
> registry, the pinned computational environment, per-participant split membership (by NHANES
> respondent sequence number), model-to-script lineage, frozen artefact hashes, and the full
> results tables are available at <REPOSITORY URL / Zenodo DOI — author to create a public release
> and archive a versioned snapshot>. No individual-level data are redistributed; the code
> regenerates every result from the public NHANES files.

### Cover letter — skeleton
> Dear Editors,
>
> We submit "Discrimination and aggregate calibration are insufficient evidence of subgroup-safe
> reliability: a calibration–fairness–uncertainty audit of routine-data models for significant
> liver fibrosis" for consideration as [Original Research / Methodological Article].
>
> Routine-data machine-learning models for liver-fibrosis triage are proliferating and are almost
> always evaluated on discrimination and, at best, aggregate calibration. Using one pre-registered,
> hash-frozen NHANES cohort, we show that five common model families reach that evaluation bar yet
> still (i) under-detect normal-weight patients by 27–48 percentage points of sensitivity, in every
> model and every sensitivity cohort, tracking a body-mass risk shortcut; and (ii) provide
> split-conformal prediction sets whose marginal coverage meets target while subgroup coverage for
> obese and older patients falls well below it. No post-hoc mitigation we tested — group-wise
> conformal recalibration, subgroup thresholds, subgroup calibration, equalized-odds
> post-processing, model retuning, joint intersectional calibration, or selective deferral —
> produced an acceptable multi-metric fix[, and a pre-registered training-time reweighting
> intervention <RESULT>].
>
> The contribution is methodological: a model that passes discrimination and aggregate-calibration
> review is not thereby subgroup-safe, and conformal prediction's marginal guarantee does not close
> that gap. We report this as an audit, not a deployable model; external validation has not been
> performed and is stated as the foremost limitation. The work follows TRIPOD+AI (checklist
> enclosed). The author is an independent researcher; the full analysis protocol, code, and a
> documented multi-pass internal audit trail accompany the submission.
>
> The work has not been published elsewhere and is not under consideration by another journal.
> [A preprint is available at medRxiv: <DOI>.]
>
> Yours sincerely, <name>, Independent Researcher, <city, country>

---

## D. Order of operations

1. Track 1 result → integrate → **v5** (A1).
2. Merge branches (A2).
3. A3, A4, A7, A8, A9 (text — a day).
4. A5, A6 (figures — author's tool).
5. A10 (co-author read) — do not skip.
6. Create the public code release + Zenodo DOI; fill the availability paragraph.
7. medRxiv (A11).
8. Submit to JAMIA (`TARGET_VENUE_DECISION.md`).
