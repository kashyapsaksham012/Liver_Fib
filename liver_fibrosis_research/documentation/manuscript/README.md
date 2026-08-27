# documentation/manuscript/

- `MANUSCRIPT_DRAFT.md` — working draft (**v3**, 2026-08-27) of the primary manuscript.
- `LITERATURE_REVIEW.md` — search record, findings by theme, novelty positioning
  (Already done / Related but different / Distinctive), DOI-verification status, and the
  target-venue recommendation (§5).
- `RESULTS_VERIFICATION.md` — second-reader log: every §3 / Tables 1–5 number checked against the
  frozen artifacts (one error found and fixed; remaining items for a co-author).

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

**Status.** Draft v3 for the authors.

*Done:* literature-grounded Introduction (`[n]` markers) and §4.1 relation-to-prior-work; working
28-item reference list; Tables 1–5 rendered from the frozen artifacts (Table 1 via
`src/manuscript_01_table1.py`, a read-only descriptive script); every figure already exists as a
committed PNG (§Figures); TRIPOD+AI crosswalk (Appendix B); a full second-reader number check
(`RESULTS_VERIFICATION.md` — one error found and fixed); DOI verification for 10/28 references;
target-venue recommendation (`LITERATURE_REVIEW.md` §5 — JAMIA / JBI / npj Digital Medicine /
PLOS Digital Health; **not** hepatology).

*Before submission:* a formal PRISMA-style systematic search (documented query, two screeners,
flow diagram) and DOI/PMID + author verification of the remaining references; panel assembly /
relabelling of the figures to the chosen journal's style; a human co-author repeating the
`RESULTS_VERIFICATION.md` pass and a final read against `DO_NOT_CLAIM.md`; journal choice and
reformatting.

**Not a deployable-model paper.** The framing is a methodological/reliability audit:
discrimination plus aggregate calibration are insufficient evidence of subgroup-safe reliability.
