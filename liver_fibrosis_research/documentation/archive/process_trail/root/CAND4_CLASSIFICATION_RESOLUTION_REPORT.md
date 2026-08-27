# CAND_4 Classification Resolution Report

**This is a documentation/scientific-integrity audit only. No cohort was built, no model was
trained, no test set was touched, and no completed sensitivity analysis was rerun.**

## 1. Executive verdict

**RESOLVED — CAND_4 DISTINCT EXPLORATORY ITEM — UNEXECUTED.**

CAND_4 ("all-ages 12+," N=8,215) is classified as a distinct, EXPLORATORY-tier sensitivity cohort,
separate from CAND_2 (elastography eligibility), based on converging Level-1 evidence: (a)
`statistical_analysis_plan.md` explicitly and independently tracks CAND_4 as its own item, in its
own evidentiary tier, with its own stated scientific purpose; (b) the two cohorts' actual mask
definitions (`primary_cohort_decision.md`) perturb orthogonal eligibility dimensions — CAND_2
varies elastography quality only, CAND_4 varies age eligibility only. CAND_4 remains unexecuted;
this resolution changes only its documentation classification, not its execution status.

## 2. Scope of this task

Determine the correct protocol classification of CAND_4 only. Explicitly out of scope: executing
CAND_4, rerunning any of the three completed deferred sensitivity analyses (relaxed elastography,
fasting-extended, 8.0-vs-8.2kPa threshold) or the completed Non-Hispanic Black MI analysis,
modifying any historical Phase 2 document, or changing any completed scientific result.

## 3. Source documents inspected

| Document | Path | Role |
|---|---|---|
| Document A | `documentation/phase2/sensitivity_analysis_plan.md` | Claims CAND_4 is folded into item 2 |
| Document B | `documentation/phase2/statistical_analysis_plan.md` | Independently tracks CAND_4 as a separate EXPLORATORY item |
| `primary_cohort_decision.md` | `documentation/phase2/primary_cohort_decision.md` | Authoritative cohort-mask definitions for CAND_1–4 |
| `PHASE2_PROTOCOL_FREEZE.md` | `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` | Consolidation — lists CAND_2/CAND_4 with apparent parity, does not resolve the conflict |
| Roadmap | `documentation/project_roadmap/deferred_sensitivity_analyses.md` | Current tracking document, updated this task |
| Amendment registry | `documentation/end_to_end/protocol_amendment_registry.md` | Continuous registry, 13 existing amendments verified live, Amendment #14 added |
| Prior resolution | `MI_CLOSURE_RECONCILIATION_REPORT.md` §5 | Earlier, now-superseded conclusion |
| No dedicated CAND_4 file | — | Confirmed absent via `find . -iname "*cand4*" -o -iname "*allages*"` |

All paths verified to exist and were read directly this pass, not assumed or recalled from memory.

## 4. Exact conflicting passages

**Document A** (`sensitivity_analysis_plan.md`), item 2's own definition:
> "Alternative elastography eligibility: CAND_2 (non-missing-only, N=7,639) vs. primary CAND_1
> (quality-valid, N=7,153). Justified because Phase 1 explicitly could not assume these two
> populations behave identically."

**Document A**, the folding claim (under "Explicitly NOT Selected as Formal Sensitivity Analyses"):
> "All-ages (12-17y) cohort — already covered as a sensitivity cohort under item 2's broader
> 'cohort robustness' umbrella and separately listed as CAND_4 in `primary_cohort_decision.md`;
> not duplicated as a fifth item here."

**Document B** (`statistical_analysis_plan.md`), SECONDARY item 3:
> "Elastography-eligibility sensitivity cohort: CAND_2 (N=7,639, non-missing-only eligibility) —
> same primary predictors/outcome, compared to primary-cohort results."

**Document B**, EXPLORATORY item 2 (separately numbered, different tier):
> "All-ages sensitivity cohort: CAND_4 (N=8,215, includes ages 12-17) — exploratory check of
> whether adolescent inclusion changes conclusions; not primary because of the
> clinical-appropriateness reasoning in `primary_cohort_decision.md`."

Both documents are headed "Generated: 2026-08-18." Document A's item 2 is defined narrowly around
elastography-quality eligibility only — its own text contains no reference to age. Document B
treats CAND_2 and CAND_4 as fully separate list items, in different tiers (SECONDARY vs.
EXPLORATORY), each with its own scientific-purpose sentence.

## 5. CAND_2 definition

Per `primary_cohort_decision.md`: "Adult + non-missing LUXSMED (any completeness) + broad labs +
BMI/sex complete." N=7,639. Relative to CAND_1, **only** the elastography-quality rule changes
(`LUAXSTAT==1` → any non-missing); the adult-only (age ≥18) restriction is **unchanged**.

## 6. CAND_4 definition

Per `primary_cohort_decision.md`: "LUAXSTAT==1 + broad labs + BMI/sex complete, NO adult
restriction (ages 12-150)." N=8,215. Relative to CAND_1, **only** the age restriction changes
(adult-only → none); the elastography-quality rule (`LUAXSTAT==1`) is **unchanged** — identical to
CAND_1's own rule.

Full side-by-side table: `documentation/validation/cand4_definition_comparison.csv`.

**Direct answer to the required classification test:** yes, CAND_4 changes age eligibility while
CAND_2 changes elastography-quality eligibility — confirmed by the cohort masks themselves, not
by interpretation of prose. They are orthogonal, single-axis perturbations of CAND_1.

## 7. Git precedence audit

`git log --follow -p` for both Document A and Document B shows exactly one commit each:
`c9c6ee3ceeefad0957797bed75abedd827567595`, 2026-08-18 17:57:33 +0530, author Saksham Kashyap —
the same commit for both files. Neither file has been modified since. **Outcome: both were
introduced in the same freeze commit; no later authoritative amendment resolved them before this
task. No historical precedence is recoverable from the available version history.** (Outcome B
per this task's own Part 4 taxonomy.)

## 8. Scientific-merit comparison

| Test question | Answer |
|---|---|
| Do CAND_2 and CAND_4 change the same eligibility dimension? | **No** — elastography-quality vs. age, respectively |
| Do they answer the same scientific question? | **No** — "is the quality-completeness rule robust?" vs. "does adolescent inclusion change conclusions?" |
| Do they arise from the same Phase 2 decision? | No — the elastography-eligibility protocol and the adult-only restriction are two separately documented Phase 2 decisions (`elastography_eligibility_protocol.md` vs. the age-restriction reasoning in `primary_cohort_decision.md`'s decision criterion 1, "clinical appropriateness") |
| Would combining them produce a scientifically meaningful single analysis? | Not without a new, explicitly designed joint experiment — no such design exists in any frozen document |
| Does the original protocol explicitly define the combination? | No — Document A merely asserts the fold without defining what a combined analysis would measure |
| Does the cohort architecture support the claimed combination? | No — CAND_2 and CAND_4 are not nested; combining them (relaxing both dimensions simultaneously) would be a novel, undefined CAND_5, not what either document describes |

## 9. Previous incorrect resolution

`MI_CLOSURE_RECONCILIATION_REPORT.md` §5 (2026-08-19) concluded: "Phase 2 deliberately grouped it
under item 2 (cohort-eligibility robustness) rather than tracking it as an independent item, and
this grouping is documented in the frozen source itself (not inferred or asserted after the
fact)." This conclusion cited only `sensitivity_analysis_plan.md` and `primary_cohort_decision.md`
— it did **not** inspect `statistical_analysis_plan.md`, which independently and explicitly
tracks CAND_4 as a separate EXPLORATORY item. **This audit corrects that gap.** Per the
Historical-Integrity Rule governing this task, `MI_CLOSURE_RECONCILIATION_REPORT.md`'s original
text is **not edited, deleted, or backdated** — it remains as evidence of what was actually
concluded at the time, with the correction recorded separately in Amendment #14 and in this
report.

## 10. Current classification decision

**Category A — DISTINCT FORMALLY TRACKED EXPLORATORY/SENSITIVITY ANALYSIS**, specifically at the
**EXPLORATORY** tier (matching Document B's own explicit label, not the higher SECONDARY tier
CAND_2/item 3 occupy). This is not "Category B — genuinely subsumed": no evidence establishes
that CAND_2 and CAND_4 were intentionally combined into one analysis — the only source claiming
this (Document A's single sentence) is contradicted by its own item-2 definition and by Document
B's explicit separate tracking, and no cohort architecture or analysis design exists anywhere for
a genuinely combined CAND_2+CAND_4 experiment.

## 11. CAND_4 execution-status verification

Repository-wide search (`find . -iname "*cand4*" -o -iname "*allages*"`; `grep` for `CAND_4` in
every CSV under `results/`) found **zero** cohort files, model artifacts, prediction files, metric
files, or reports for CAND_4. The only repository occurrences of "CAND_4" are documentation
references and one tracking-matrix row (`results/sensitivity/deferred_sensitivity_execution_
matrix.csv`, added by the prior deferred-sensitivity-analysis task, explicitly marked `DO NOT
EXECUTE — STATUS UNRESOLVED` at that time) — not execution evidence. **CAND_4 REMAINS
UNEXECUTED.**

## 12. Impact on completed sensitivity analyses

None. Verified directly: `src/sens_02_train_evaluate.py` and `src/sens_03_alternative_threshold.py`
contain no CAND_4 identifier; their results
(`results/sensitivity/sensitivity_discrimination_calibration_results.csv`,
`alternative_threshold_8p0kPa_results.csv`, `primary_vs_sensitivity_comparison.csv`) are
byte-unchanged (spot-check hashes recorded, unchanged from their Commit C/D state); their Git
commits (`f6b17e6`, `9d7abb0`, `3ab927b`) remain valid. Neither CAND_2's nor CAND_3's construction
or execution required any CAND_4 classification decision.

## 13. Search for stale Scenario-C references

Searched the full repository for "Scenario C," "folded into item 2," "cohort robustness," and
related terms. The literal phrase "Scenario C" does not appear anywhere in the repository (the
earlier closure task used different, though substantively similar, phrasing — "deliberately
grouped... not an omission" — not the letter-coded "Scenario A/B/C" terminology). "Folded into
item 2" appears in three documents: `DEFERRED_SENSITIVITY_ANALYSIS_RESULTS_REPORT.md`,
`MI_CLOSURE_RECONCILIATION_REPORT.md`, and `documentation/validation/
deferred_sensitivity_scope_reconciliation.md` — all of which already correctly describe this as a
conflict/inconsistency requiring resolution (the deferred-sensitivity task had already reached
"UNRESOLVED" as its interim conclusion, one step short of this task's fuller mechanistic
resolution). No document was found asserting CAND_4 was already executed, completed, or
intentionally subsumed as an established fact beyond what is corrected here.

## 14. Amendment registry entry

**Amendment #14**, added to `documentation/end_to_end/protocol_amendment_registry.md` (verified
live: 13 existing amendments before this task, confirmed via `grep -c "^| [0-9]"`). Full text
records: the conflict description, exact source passages, document dates, Git precedence finding,
the CAND_2-vs-CAND_4 scientific comparison, the final classification, the previous resolution and
why it is superseded, confirmation that original documents were not rewritten, confirmation that
CAND_4 remains unexecuted, and confirmation that the three completed sensitivity analyses are
unaffected. `results/end_to_end/protocol_amendment_reconciliation.csv` updated in sync (row 14).

## 15. Roadmap correction

`documentation/project_roadmap/deferred_sensitivity_analyses.md` updated: items 1–3 corrected to
**EXECUTED** (reflecting the prior deferred-sensitivity-analysis task, which this roadmap had not
yet been updated to show); item 2 narrowed to CAND_2 only; a new **item 2b** created specifically
for CAND_4, classified DISTINCT — EXPLORATORY — UNEXECUTED, pointing to Amendment #14 and this
report. The original 2026-08-19 reconciliation note is preserved in place (not deleted) with an
explicit "SUPERSEDED, see below" marker, consistent with the Historical-Integrity Rule for this
living tracking document (distinct from the frozen Phase 2 source documents, which were not
touched).

## 16. Final CAND_4 status

**DISTINCT — EXPLORATORY — UNEXECUTED.**

## 17. Scientific implications

CAND_4 is **not** part of the completed sensitivity evidence and does **not** contribute to the
current robustness claim ("main findings partially robust," `DEFERRED_SENSITIVITY_ANALYSIS_
RESULTS_REPORT.md`) — that claim rests entirely on the three items actually executed (alternative
threshold, CAND_2, CAND_3). CAND_4 does **not** need to be executed before manuscript preparation
— its EXPLORATORY tier means it was never required for the primary or secondary conclusions, and
this task does not find new evidence changing that. It is legitimate, optional future work, should
a researcher wish to test whether adolescent inclusion changes the study's conclusions. **The
documentation classification question (resolved here) and the scientific-necessity question
(whether to ever run it) are kept separate, per this task's own governing principle** — resolving
the former does not create an obligation to pursue the latter.

## 18. Remaining open questions

- Document A's own internal tension (a narrow item-2 definition alongside a broader,
  unsubstantiated "umbrella" claim) is disclosed but not itself corrected in Document A, per the
  Historical-Integrity Rule — a future researcher reading Document A in isolation would still see
  the original, uncorrected claim; they must consult Amendment #14 or this report for the
  correction.
- No formal decision has been made about whether CAND_4 will ever be executed — that remains
  entirely open, separately-scoped future work.

## 19. Reproducibility/provenance record

This task performed no model training, no cohort construction, and no test-set access — there is
no computational result to reproduce. Provenance is recorded through: (a) the exact git commit
hash and timestamp for both conflicting documents (Section 7), (b) the verified amendment count
before this task (13) and after (14), (c) hash spot-checks confirming the three completed
sensitivity analyses' result files are unchanged (Section 12), and (d) the evidence table
(`documentation/validation/cand4_resolution_evidence.csv`) tracing every claim in this report to
its exact source.

## 20. Final closure statement

CAND_4 remains, as it was before this task, genuinely unexecuted. What has changed is that its
documentation status is now resolved with a full, disclosed evidence trail: it is a distinct,
EXPLORATORY-tier item, not a component folded into CAND_2's already-completed elastography
analysis. No historical document was altered. No prior conclusion was silently erased — the
earlier, incomplete resolution is explicitly marked superseded, with the reason stated. No
scientific result changed. This resolves a documentation-integrity gap, not a scientific finding.
