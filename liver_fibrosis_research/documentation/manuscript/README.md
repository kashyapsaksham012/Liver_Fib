# documentation/manuscript/

- `MANUSCRIPT_DRAFT.md` — working draft (**v4**, 2026-08-27) of the primary manuscript.
- `LITERATURE_REVIEW.md` — search record, findings by theme, novelty positioning
  (Already done / Related but different / Distinctive), DOI-verification status, and the
  target-venue recommendation (§5).
- `RELATED_WORK_SCAN.md` — the exhaustive annotated catalogue (~80 papers, 13 themes A–M),
  each with what it did and a relevance tag. The starting bibliography; still needs a formal
  PRISMA search on top.
- `RESULTS_VERIFICATION.md` — second-reader log: every §3 / Tables 1–5 number checked against the
  frozen artifacts (one error found and fixed; remaining items for a co-author).
- `REFERENCE_VERIFICATION.md` — **Track 2.2**: all 28 references checked against primary sources.
  Material findings: ref 1 is **Cao et al.** not "Zhou et al."; refs 22+23 are one paper (merged);
  several metadata fixes. A co-author still needs full author bylines + the CHEST 2026 byline.
- `LITERATURE_SEARCH_RECORD.md` — **Track 2.3**: the documented single-reviewer search (databases,
  query strings, date, flow). Found and added ref 28 (Rafe & Das, arXiv:2605.05562 — the same
  marginal-vs-subgroup coverage phenomenon in survey-based social measurement; strengthens §4.1).
  Novelty claim stands.
- `TRIPOD_AI_CHECKLIST.md` — **Track 2.4**: item-by-item map of the manuscript to TRIPOD+AI, with
  the ~6 small gaps to close (blinding sentences, flow figure, declarations — most now done).
- `TARGET_VENUE_DECISION.md` — **Track 2.1**: recommendation = medRxiv preprint → **JAMIA**
  primary (no mandatory APC), then JBI → PLOS Digital Health (APC waiver) → JMIR AI.
- `SUBMISSION_CHECKLIST.md` — **Track 2.5**: blocking items, boilerplate drafts (funding, ethics,
  data/code availability, cover letter), order of operations.

**Grounding.** Every numeric claim traces to a frozen result artifact via
`results/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv` (Appendix A of the draft). The
framing, prohibited claims, and mandatory limitations follow:

- `documentation/final_research_audit/MANUSCRIPT_FRAMING_GUIDANCE.md` — BMI is the sole subgroup
  headline; the age-60+ *sensitivity* disparity is a secondary observation; the age-60+
  *conformal* under-coverage is retained at full strength.
- `documentation/final_research_audit/DO_NOT_CLAIM.md` — claims the evidence does not support.
- `documentation/final_research_audit/FINAL_LIMITATIONS_REGISTER.md` — the minimum limitations
  set. **Draft §5 reproduces every ID in that register's mandated minimum set**, tagged inline
  (D1, E1, E3, E4, I1, J1, J3, J4, A1, B1, B2, C1, C3, F1, F2, G1, plus C2/B3/A2/A5/D4/F3/J2/J5).
- `documentation/final_research_audit/CONFLICT_ADJUDICATIONS.md` — C1–C4, all resolved.
- `documentation/final_research_audit/AUTHORITATIVE_RESULTS.md` — the verified numbers and their
  recommended wording.
- `documentation/prepublication_fixes/` — Amendment #18: `AMENDMENT_18_CLOSURE.md`,
  `FIX1_MODEL_FIT_ALIGNMENT.md`, `FIX2_VCTE_BIAS_SENSITIVITY.md`; the two model fits, the
  reference-standard measurement-bias sensitivity analysis, and the mitigation-narrative
  consolidation folded into v4.

**Status.** Draft v4 for the authors.

*Done:* literature-grounded Introduction (`[n]` markers) and §4.1 relation-to-prior-work;
**28-item reference list, all verified against primary sources** (`REFERENCE_VERIFICATION.md`);
Tables 1–5 rendered from the frozen artifacts; every figure exists as a committed PNG (§Figures);
TRIPOD+AI checklist (`TRIPOD_AI_CHECKLIST.md`) + Declarations section (funding/ethics/conflicts/
protocol/data-availability); a full second-reader number check (`RESULTS_VERIFICATION.md`, incl.
Amendment #18 addendum); documented literature search (`LITERATURE_SEARCH_RECORD.md`);
target-venue decision (`TARGET_VENUE_DECISION.md`).
**v3 → v4 (Amendment #18):** §2.7b, §3.4b, §3.4c, Table 4/§3.7, abstract/§4/§4.1/§5.
**v4 (Track 2, 2026-08-27):** references verified + corrected (Cao not Zhou; 22+23 merged; +ref 28
from the search); new §2.13 (related-work search); Declarations section; TRIPOD blinding /
sample-size sentences; §4.1 gains the survey-data parallel [28].

*Before submission (`SUBMISSION_CHECKLIST.md`):* fold in Amendment #19 → v5; merge the experiment
branch; paste remaining author bylines; full-text re-check of the ref [1] / ref [23] claims;
participant flow diagram + figure panel assembly; a co-author repeating `RESULTS_VERIFICATION.md`
and a final read against `DO_NOT_CLAIM.md`; create the public code release + archival DOI;
post to medRxiv; submit to JAMIA.

**Not a deployable-model paper.** The framing is a methodological/reliability audit:
discrimination plus aggregate calibration are insufficient evidence of subgroup-safe reliability.
