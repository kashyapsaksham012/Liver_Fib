# Submission package

The curated view of what leaves this repository — for the preprint, the journal,
and the archival code release. **Nothing here is moved or copied yet**; this is
the manifest. Build the actual bundle from it when submitting.

Target venue ladder (`documentation/manuscript/TARGET_VENUE_DECISION.md`):
medRxiv preprint → **JAMIA** → JBI → PLOS Digital Health. Parallel 4-page version →
ML4H / CHIL.

---

## A. The manuscript

| item | source | status |
|---|---|---|
| Main text | `documentation/manuscript/MANUSCRIPT_DRAFT.md` (v5.1) | draft; needs the temporal + pooled sections folded in (below) and compression |
| Temporal validation §2.10a + §3.12 + abstract + limitations | `temporal_validation_2021_2023/MANUSCRIPT_SECTION_temporal.md` | ready to paste |
| Model-update re-audit §2.8c + §3.7c + abstract + limitations | `pooled_model_update_2017_2023/MANUSCRIPT_SECTION_pooled.md` | ready to paste |
| Reference list (28) | `documentation/manuscript/MANUSCRIPT_DRAFT.md` §References + `manuscript_verification/reference_bylines.md` | refs 7, 20 bylines still open |
| TRIPOD+AI checklist | `documentation/manuscript/TRIPOD_AI_CHECKLIST.md` | crosswalk done; official form pending |
| Declarations (funding / competing / ethics / protocol) | `documentation/manuscript/MANUSCRIPT_DRAFT.md` Declarations + `SUBMISSION_CHECKLIST.md` §C | funding/affiliation decision open (R9) |

## B. Figures (to the journal's panel spec)

| # | files | from |
|---|---|---|
| 1a/1b discrimination | `manuscript_figures/main/fig1a_*`, `fig1b_*` | frozen |
| 2 calibration raw vs recal | `manuscript_figures/main/fig2_*` | regenerated |
| 3a BMI-band sensitivity | `manuscript_figures/main/fig3_sensitivity_by_bmi_band.png` | regenerated |
| 3b mechanism (score distributions) | `manuscript_figures/main/fig3_mechanism_*` | frozen |
| 4a subgroup conformal coverage | `manuscript_figures/main/fig4a_*` | frozen |
| 4b intersectional coverage + Mondrian | `manuscript_figures/main/fig4b_*` | frozen |
| 5a/5b fairness–specificity Pareto | `manuscript_figures/main/fig5a_*`, `fig5b_*` | frozen |
| T1–T6 temporal validation | `temporal_validation_2021_2023/figures/figT1..T6.{png,pdf}` | regenerated |
| S1 stiffness distributions | `manuscript_figures/supplement/stiffness_by_*` | frozen (regenerate for publication styling) |
| participant flow diagram | **to build** from `documentation/manuscript/MANUSCRIPT_DRAFT.md` §2.1 counts | — |

**Do not include:** `manuscript_figures/_superseded_reference/*`, any M4b / MI-conformal
figure (`results/figures/figure3_*,figure4_*,figure5_*`, `results/fairness_bmi_investigation/phase5_mi_conformal_figures/*`),
`manuscript_figures/supplement/cooccurrence_descriptive.png` in the main paper
(supplement only, with the "permutation p = 0.12" caption).

## C. Supplementary material

- TRIPOD+AI completed checklist
- Protocol freeze + the 20-amendment registry (`documentation/phase2/PHASE2_PROTOCOL_FREEZE.md`, `documentation/end_to_end/protocol_amendment_registry.md`)
- The three tier protocols (`temporal_validation_2021_2023/PROTOCOL_FREEZE.md`, `pooled_model_update_2017_2023/PROTOCOL_FREEZE.md`)
- Supplement figures (`manuscript_figures/supplement/`)
- Full results tables (`results/tables/`, the temporal + pooled `results/*.csv`)
- Literature search record (`documentation/manuscript/LITERATURE_SEARCH_RECORD.md`)

## D. Code + data release (archival DOI — Zenodo)

Deposit the whole repository **as-is** (it is already reproducible), plus:

| add | why |
|---|---|
| `REPOSITORY_MAP.md`, this file | navigation for external readers |
| `requirements-phase3-lock.txt` | the pinned environment (present) |
| a top-level `reproduce.sh` | one script: env build → tier-1 pipeline → tier-4 → tier-5 → all verify harnesses |
| per-participant split membership by SEQN | already in `data/processed/splits/` and the tier-4/5 `data/processed/` |
| model-to-script lineage + artifact hashes | `results/tables/{model_lineage,model_artifact_manifest}.csv` + the tier-4/5 `FROZEN_ARTIFACT_MANIFEST.csv` |

No individual-level NHANES data is redistributed — the raw `.xpt` files are public
CDC/NCHS downloads and the code regenerates every result from them.

## E. Pre-submission checklist (blocking)

From `documentation/manuscript/SUBMISSION_CHECKLIST.md` §A, still open:

1. Fold `MANUSCRIPT_SECTION_temporal.md` + `MANUSCRIPT_SECTION_pooled.md` into the main text; compress to venue length; **one thesis**.
2. Fill reference bylines for [7] and [20]; two-screener literature search with recorded hit counts.
3. Participant flow diagram.
4. Resolve the funding/affiliation statement (R9 in `PDF_REPO_RECONCILIATION.md`).
5. Complete the official TRIPOD+AI form with page numbers.
6. A second reader repeats `manuscript_verification/verify.py` and reads the whole text against `DO_NOT_CLAIM.md`.
7. Check the NHANES 2021–2023 elastography documentation for a device/protocol change (affects the §3.12 concept-drift interpretation).
8. Public repo + Zenodo DOI; medRxiv post.

## F. What is deliberately NOT in scope

- No external (non-NHANES) validation — stated as the foremost limitation.
- No temporal claim beyond "later NHANES cycle" (not external / geographic).
- No deployable-model or clinical-readiness claim.
- M4b joint-cell conformal and the MI-conformal extension (removed, Amendment #20).
