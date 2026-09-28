# Repository map

**One place to understand what is where and why.** This repository holds one
research programme — a calibration / fairness / uncertainty audit of routine-data
ML for significant liver fibrosis — plus its post-freeze extensions. The core
study is frozen at git tag `evidence-freeze`; the extensions are separate,
individually pre-registered studies that add evidence tiers on top of it without
touching it.

> **Read `documentation/START_HERE.md` first** for the frozen study's internal
> authority order, superseded material, and the four adjudicated conflicts. This
> file is the map *above* that — the whole repository, all tiers.

---

## 1. The five evidence tiers

Everything in the repository belongs to exactly one tier. Higher-numbered tiers
**never modify** lower ones; each has its own frozen protocol and its own
number-verification harness.

| tier | what | status | location | protocol |
|---|---|---|---|---|
| **1 — Frozen primary study** | NHANES 2017–March 2020 audit, Phases 1–8: data assembly → protocol freeze → 5-family baseline → OOF Platt calibration → fairness audit → split-conformal → Mondrian mitigation → NHB subgroup holdout | **FROZEN** (`evidence-freeze`) — read-only | `src/`, `results/`, `models/phase3,phase6_conformal_refit,phase8_holdout/`, `documentation/`, root `PHASE*_REPORT.md` | `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` |
| **2 — Frozen follow-up (Amendments #14–20)** | BMI-fairness sub-investigation (its own Phases 0–7); 3 sensitivity cohorts (8.0 kPa, CAND_2, CAND_3); targeted NHB multiple imputation; reliability extension (co-occurrence + DCA); conformal replication (#16); selective-deferral mitigation (#17); pre-publication fixes (#18); training-time reweighting (#19); provenance closure (#20) | **FROZEN** — read-only | `src/` (`sens_*`, `mi_*`, `deferral_*`, `ttm_*`, `prepub_*`, `prov_*`, `phase7_*`, `rel_*`, `tradeoff_*`), `results/{sensitivity,fairness_bmi_investigation,selective_deferral,training_time_mitigation,prepublication_fixes,reliability_extension,provenance}/`, `models/training_time_mitigation/`, `documentation/{sensitivity,fairness_bmi_investigation,...}/`, root `DEFERRED_*`, `MULTIPLE_IMPUTATION_*`, `RELIABILITY_EXTENSION_*` reports | `documentation/end_to_end/protocol_amendment_registry.md` (20 amendments) |
| **3 — Manuscript + verification tooling** | The working manuscript, its number-verification harness, the curated figure set, the PDF↔repo reconciliation. Adds **no scientific claim** — it checks and packages tiers 1–2. | active (this session) | `documentation/manuscript/`, `manuscript_verification/`, `manuscript_figures/` | — |
| **4 — Temporal evaluation** | Frozen models applied unchanged to NHANES **August 2021–August 2023**. Discrimination attenuated (~0.05, decomposed → concept drift concentrated in normal-weight); **BMI dissociation, conformal split, and matched-stiffness mechanism replicated 5/5**; age-60+ sensitivity reversed (pre-registered as fragile). Verdict: PARTIAL TEMPORAL REPLICATION. | complete (this session) — separate tier, supersedes nothing | `temporal_validation_2021_2023/` | `temporal_validation_2021_2023/PROTOCOL_FREEZE.md` |
| **5 — Model-update re-audit** | Five families retrained on the **pooled 2017–2023** cohort with the frozen hyperparameters. All three core reliability failures persist; discrimination on the 2021–2023 slice unchanged from the un-updated model. Verdict: **UPDATING DOES NOT RESOLVE THE FAILURE — it is structural.** | complete (this session) — separate tier | `pooled_model_update_2017_2023/` | `pooled_model_update_2017_2023/PROTOCOL_FREEZE.md` |

**Preservation rule.** No file under tier 1 or tier 2 (`src/`, `results/`,
`models/phase*`, `data/processed/splits/`, `documentation/` phase & audit trees,
the root phase reports) is moved, renamed, or edited. Scripts hard-code paths,
frozen artifacts are hash-verified, and the credibility of the study rests on this
being demonstrably append-only. Reorganising it would break the reproducibility
lineage and the test suite. The navigation problem is solved by *this file*, not
by moving anything.

---

## 2. Physical layout

```
liver_fibrosis_research/
│
├── README.md                     one-paragraph orientation (top-level)
├── REPOSITORY_MAP.md             ← you are here
├── SUBMISSION_PACKAGE.md         what actually goes to the preprint / journal / DOI
├── MODEL_CARD.md  DATASHEET.md   intended use / limitations; cohort composition (added 2026-09-28)
├── requirements-phase3-lock.txt  authoritative pinned environment
│
├── PHASE1..8_*_REPORT.md         tier 1 — per-phase primary records (root, frozen)
├── DEFERRED_* / MULTIPLE_IMPUTATION_* / RELIABILITY_EXTENSION_* _REPORT.md
│                                 tier 2 — follow-up records (root, frozen)
│
├── src/          (139 files)     tier 1+2 analysis scripts. Naming:
│     ├── NN_*.py                    Phase 1 data assembly / audit (01–21)
│     ├── phase2_*  phase3_*         protocol freeze / baseline modelling
│     ├── phase4_*  phase5_*         calibration / fairness
│     ├── phase6_*  phase7_*  phase8_*   conformal / mitigation / holdout
│     ├── sens_*  mi_*               sensitivity cohorts / multiple imputation
│     ├── deferral_*  ttm_*  prepub_*  prov_*   Amendments #17–20
│     ├── rel_*  tradeoff_*          reliability extension / exploratory tracks
│     └── _common.py  phase{3,4,5,6}_common.py   shared helpers
│
├── results/      (470 files)     tier 1+2 frozen artifacts (the authority — a
│                                 prose number that disagrees with these is wrong)
│     ├── tables/  predictions/  calibration/  fairness/  uncertainty/
│     ├── mitigation/  validation/  sensitivity/  reliability_extension/
│     ├── fairness_bmi_investigation/  selective_deferral/  training_time_mitigation/
│     ├── prepublication_fixes/  provenance/  diagnostics/  figures/
│     └── final_research_audit/  final_research_state/   claim registries
│
├── models/       (32 .joblib)    frozen fitted pipelines
│     ├── phase3/                    full-train fit (discrimination / fairness)
│     ├── phase6_conformal_refit/    proper-train fit (conformal)
│     ├── phase8_holdout/            NHB-withheld refit
│     └── training_time_mitigation/  Amendment #19 refits
│
├── data/
│     ├── raw/NHANES_2017_2020/     public CDC .xpt inputs (tier 1)
│     ├── interim/  processed/      merged + analysis datasets, split IDs
│     └── (../../NHANES 2021–2023 temporal validation dataset/  — tier 4 input, gitignored)
│
├── documentation/  (261 files)   tier 1+2 prose. Key sub-trees:
│     ├── START_HERE.md             authority map for the frozen study — READ FIRST
│     ├── phase2/  phase3/          protocol freezes / design docs
│     ├── final_research_audit/     master synthesis + typed claim registers
│     ├── final_audit/              narrative history + REPRODUCIBILITY.md
│     ├── manuscript/               MANUSCRIPT_DRAFT.md (v5.1) + lit review + checklists
│     ├── end_to_end/               protocol_amendment_registry.md (20 amendments)
│     ├── {sensitivity,fairness_bmi_investigation,selective_deferral,
│     │    training_time_mitigation,prepublication_fixes,reliability_extension,
│     │    provenance,uncertainty,fairness,calibration,validation}/
│     └── archive/                  ~77 process-trail files (moved 2026-08-27, nothing deleted)
│
├── tests/        (18 scripts)     internal validation suite for tiers 1+2
│
├── manuscript_verification/       TIER 3 — number-verification harness (59 checks),
│     │                            PDF↔repo reconciliation, reference bylines
│     ├── verify.py  checks.py
│     ├── FINDINGS.md  PDF_REPO_RECONCILIATION.md  reference_bylines.md  figure_manifest.csv
│     └── report/
│
├── manuscript_figures/            TIER 3 — the curated figure set for the paper
│     ├── main/            (9)        Fig 1a/1b, 2, 3a/3b, 4a/4b, 5a/5b
│     ├── supplement/      (28)       per-model sets, DCA, stiffness, missingness, cooccurrence
│     ├── _superseded_reference/      the 2 old misleading figures (do not use)
│     ├── FIGURE_AUDIT.md  regenerate_figures.py  figure_manifest.csv
│
├── temporal_validation_2021_2023/ TIER 4 — full module (own protocol, src, results, figures)
│     ├── PROTOCOL_FREEZE.md  FROZEN_ARTIFACT_MANIFEST.csv  MANUSCRIPT_SECTION_temporal.md
│     ├── src/ (t00..t05, verify_temporal.py)   data/processed/   results/
│     ├── figures/ (figT1..T6, .png + .pdf both tracked)
│     └── documentation/ (protocol, drift audit, drop decomposition, synthesis, limitations, touch log)
│
└── pooled_model_update_2017_2023/ TIER 5 — full module (own protocol, src, results, models)
      ├── PROTOCOL_FREEZE.md  FROZEN_ARTIFACT_MANIFEST.csv  MANUSCRIPT_SECTION_pooled.md
      ├── src/ (p00..p03, verify_pooled.py)   data/processed/   models/ (10 pooled .joblib)
      ├── results/   documentation/ (report, touch log)
```

Empty stubs kept for compatibility: `notebooks/`, `exploratory_602020/`. `logs/` is no longer
empty — it holds `cb_fib4_baseline_run.log` and `svy_weighted_run.log`, run logs from the
post-freeze FIB-4 and survey-weighted addenda.

---

## 3. "Where is …?"

| I want | go to |
|---|---|
| The research question, cohort, models | `documentation/START_HERE.md` §1 ; `documentation/final_research_audit/FINAL_RESEARCH_AUDIT.md` §1–2 |
| The headline findings, verified | `documentation/final_research_audit/FINAL_SCIENTIFIC_FINDINGS.md` |
| The working paper | `documentation/manuscript/MANUSCRIPT_DRAFT.md` (v5.1) |
| Whether a manuscript number is right | `python3 manuscript_verification/verify.py` (43/43) |
| Any raw result number | `results/**/*.csv` — these are the authority |
| How to reproduce a phase | `documentation/final_audit/REPRODUCIBILITY.md` |
| What must NOT be claimed | `documentation/final_research_audit/DO_NOT_CLAIM.md` (35 items) |
| The 20 protocol amendments | `documentation/end_to_end/protocol_amendment_registry.md` |
| Figures for the paper | `manuscript_figures/README.md` → `main/` + `supplement/` |
| Does it hold on newer data? | `temporal_validation_2021_2023/README.md` |
| Does keeping the model current fix it? | `pooled_model_update_2017_2023/README.md` |
| The temporal evidence figures | `temporal_validation_2021_2023/figures/README.md` |
| Differences between the PDF and this repo | `manuscript_verification/PDF_REPO_RECONCILIATION.md` |
| What to send to the journal | `SUBMISSION_PACKAGE.md` |
| Model card (intended use, performance, limitations) | `MODEL_CARD.md` |
| Dataset datasheet (cohort composition, caveats) | `DATASHEET.md` |
| How to cite this work | root [`CITATION.cff`](../CITATION.cff) |
| Which file backs a specific sentence/table/figure in main.pdf | root [`README.md`](../README.md) § "Paper → repository map" |

---

## 4. Reading order (first time)

1. `documentation/START_HERE.md`
2. `documentation/final_research_audit/FINAL_RESEARCH_AUDIT.md` + `FINAL_SCIENTIFIC_FINDINGS.md`
3. `documentation/manuscript/MANUSCRIPT_DRAFT.md`
4. `temporal_validation_2021_2023/documentation/TEMPORAL_VALIDATION_REPORT.md`
5. `pooled_model_update_2017_2023/documentation/POOLED_REAUDIT_REPORT.md`
6. This file's tier table + `SUBMISSION_PACKAGE.md`

---

## 5. Verification harnesses (run any time; all read-only)

| tier | command | expect |
|---|---|---|
| 1–3 | `python3 manuscript_verification/verify.py --strict` | 43 pass, hedge scan clean |
| 4 | `python3 temporal_validation_2021_2023/src/verify_temporal.py` | 22/22 |
| 5 | `python3 pooled_model_update_2017_2023/src/verify_pooled.py` | 16/16 |
| 1–2 | `python3 tests/<script>.py` (18 scripts) | see `tests/README.md` (4 have known moved-path issues, logic unaffected) |
