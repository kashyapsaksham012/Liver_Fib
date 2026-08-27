# Literature search record — Track 2.3

**Date of search:** 2026-08-27. **Reviewer:** single (the author). This is a **structured
single-reviewer search**, not a PRISMA systematic review (which requires ≥ 2 independent
screeners). The manuscript describes it as such — do **not** claim PRISMA compliance.

Builds on the earlier ~80-paper annotated scan in `RELATED_WORK_SCAN.md` (13 themes, A–M) and the
positioning in `LITERATURE_REVIEW.md`. Purpose of this pass: (a) a documented, repeatable query
set; (b) a check for anything published since the earlier scan that changes the novelty claim.

---

## Databases / sources searched

| Source | How | Coverage |
|---|---|---|
| PubMed / MEDLINE | web (pubmed.ncbi.nlm.nih.gov) | clinical prediction, fibrosis scores, fairness in clinical AI |
| arXiv | web (arxiv.org listings + search) | conformal prediction, algorithmic fairness, selective prediction |
| Google Scholar / general web | WebSearch | cross-cutting; catches conference papers (ICLR/NeurIPS/UAI), preprints, and 2026 work |
| Journal tables of contents | direct | JAMIA, J Biomed Inform, Lancet Digit Health, npj Digit Med, Sci Rep, Front Med, BMC Gastroenterol |

No Embase / IEEE Xplore / ACM DL institutional access (independent researcher). ACM/IEEE
conference papers were reached via arXiv and Google Scholar instead — a known limitation of this
search.

## Query strings (as run 2026-08-27)

**Clinical / prediction-model:**
- `NHANES liver fibrosis machine learning vibration-controlled transient elastography`
- `NHANES liver fibrosis machine learning (fairness OR bias OR subgroup OR conformal) 2025 2026`
- `FIB-4 NAFLD fibrosis score body mass index lean obese accuracy`
- `class imbalance correction calibration clinical prediction model`

**Fairness / methods:**
- `algorithmic fairness clinical prediction model subgroup net benefit health equity`
- `fairness metrics clinical AI scoping review`
- `selective classification / learning to defer fairness disparities`

**Conformal prediction:**
- `conformal prediction clinical (subgroup coverage OR conditional coverage) fairness`
- `Mondrian conformal equalized coverage clinical`
- `conformal prediction sets disparate impact`
- `conformal prediction "marginal validity" "subgroup" survey data`

## Results of the "has anything changed?" check

| Finding | Effect on the paper |
|---|---|
| **Cao et al.**, *Front Med* 2026;13:1736295 (ref 1) — the nearest-neighbour NHANES routine-data VCTE fibrosis model — **confirmed** as first-authored by Cao (not "Zhou"); does a Bayesian prevalence prior-correction; **no** fairness audit, **no** conformal, **no** mitigation. | Novelty claim intact. Author-name corrected (`REFERENCE_VERIFICATION.md` F1). |
| **Rafe & Das**, "Socio-conformal calibration in complex survey data: marginal validity is not enough for subgroup reliability", arXiv:2605.05562, May 2026. Pew American Trends Panel (attitudes, not clinical); ordinal conformal; standard split conformal → nominal marginal coverage but **~13 pp weighted subgroup gaps**; Mondrian vs regularized-Mondrian comparison; survey-weighted evaluation. | **RELATED BUT DIFFERENT — added as ref 28.** Same phenomenon, different field/data/model → *strengthens* our point that it is not task-specific. Cited in §4.1. Does **not** scoop: different domain, not clinical, not NHANES, not a fairness+calibration+mitigation audit. Also relevant to our deferred survey-weighted-training item. |
| Refs 22 + 23 are one paper (Zhou Y & Sesia M, AFCP, NeurIPS 2024). | Merged (`REFERENCE_VERIFICATION.md` F3). |
| Ref 13 ("Understanding algorithmic fairness … subgroup net benefit") now peer-reviewed in *Epidemiology* 2026. | Citation updated from arXiv-only. |
| Ref 7 (*JHEP Rep* 2026, "Diabetes and obesity reduce FIB-4 accuracy") — explicitly: BMI ≥ 30 raises ≥ 8 kPa risk even at FIB-4 < 1.30; fast-track to elastography. | Supports the body-mass finding and the FIB-4→VCTE framing; already cited [7]. |
| No 2025–2026 paper found that performs a *combined* discrimination + aggregate-calibration + pre-specified multi-axis subgroup fairness audit + split-conformal subgroup coverage + structured mitigation battery on a routine-data fibrosis model (or any single clinical prediction task) under one frozen protocol. | **The one-sentence novelty claim in `LITERATURE_REVIEW.md` §3 stands.** |

## Flow (this pass)

- Records from the earlier scan: ~80 (`RELATED_WORK_SCAN.md`).
- New records screened this pass (2026-08-27 searches, titles/abstracts): ~40.
- New records added to the reference list: **1** (ref 28, Rafe & Das).
- New records noted as supporting context, not cited: several 2026 conformal-fairness preprints
  (e.g. "Beyond Procedure: Substantive Fairness in Conformal Prediction" arXiv:2602.16794;
  "Kandinsky Conformal Prediction" arXiv:2502.17264) — methods-side, not clinical, not
  load-bearing.

## What a co-author still needs to do before submission

1. Re-run these queries in **PubMed and Embase with recorded hit counts** and a second screener.
2. A formal **PRISMA-style flow diagram** if the target journal requires it (JAMIA does not
   mandate one for a non-review article, but include a search paragraph in Methods).
3. Set a **search cut-off date** and re-scan once more immediately before submission (the 2026
   conformal-fairness literature is moving fast).
4. Forward/backward citation chase on refs 1, 13, 21, 22, 28.
