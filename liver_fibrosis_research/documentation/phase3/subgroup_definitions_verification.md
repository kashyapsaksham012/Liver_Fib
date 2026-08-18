# Subgroup Bin Pre-Specification Verification

**Generated:** 2026-08-18 (Phase 3 Closure Verification, Item 3)

## Finding: CONFIRMED — no redefinition needed. Exact bins are a pre-existing, pre-Phase-3-freeze artifact.

**Source document:** `documentation/phase2/fairness_subgroup_protocol.md` (read directly for this
verification, not recalled from memory or from a prior summary).

## Exact frozen bin boundaries (quoted directly from the file)

| Dimension | Variable | Exact categories | Precision-tier handling |
|---|---|---|---|
| Sex | `RIAGENDR` | Male, Female | Both primary-feasibility tier |
| Race/Ethnicity | `RIDRETH3` (not RIDRETH1) | Mexican American, Other Hispanic, Non-Hispanic White, Non-Hispanic Black, Non-Hispanic Asian, Other/Multi-Racial — **all 6 native NHANES categories, NONE collapsed** | Non-Hispanic Asian and Other/Multi-Racial explicitly labeled exploratory tier, reported (not dropped/pooled) |
| Age | `RIDAGEYR`, binned | **18–39, 40–59, 60+** | All three primary-feasibility tier |
| BMI | `BMXBMI`, binned | **Underweight <18.5, Normal 18.5–24.9, Overweight 25–29.9, Obese ≥30** (standard WHO categories) | Underweight explicitly labeled insufficient-evidence tier, reported (not dropped/pooled) |

## Race/ethnicity collapsing rule — explicit answer

The mentor plan's original instruction ("combine categories only if sample sizes are too small and
document the decision") was answered by an explicit Phase 2 decision: **no categories were
combined.** All 6 native RIDRETH3 categories are retained. Smallness is handled instead by an
explicit precision-tier classification system (insufficient evidence / limited precision /
exploratory candidate / primary-feasibility candidate — frozen thresholds also stated directly in
`fairness_subgroup_protocol.md`), which is the documented alternative to pooling, chosen and
justified in Phase 2. There is no "collapsing threshold" left undefined — the decision was to not
collapse at all.

## CORRECTION (superseding the original version of this section): mtime claim withdrawn

The original version of this document cited filesystem `mtime` (last-modified timestamp) as
"chronological proof." **That claim is withdrawn.** `mtime` records only when the filesystem
last wrote the file — it proves nothing about content finalization, is trivially alterable by
`touch`, `git checkout`, copying, or a re-save on open, and is not evidence a reviewer should
accept as provenance. This correction was made after being challenged to produce real
version-control evidence instead.

## Actual git provenance check (commands run, real output)

```
$ git log --follow -p -- documentation/phase2/fairness_subgroup_protocol.md
(no output)

$ git log --oneline --all
b390fbe Phase 1 closure: remediated pipeline, canonical cohorts, 24 validation tests passed
53ce947 Phase 1: data assembly pipeline, audit reports, master dataset
f7b84c3 add research info plan
44a77a1 first commit

$ git ls-files | grep fairness_subgroup_protocol
(no output -- file was not tracked)
```

**Finding: no version-control history exists for this file at all.** It was never committed
prior to this verification pass. The entire repository had only 4 commits, the most recent
covering Phase 1 only — none of Phase 2 or Phase 3's work (including this file) had ever been
committed. This is a real gap, not a documentation nuance.

## Best available corroboration (weaker than a commit, stated with its actual limitations)

No commit, chat log with independent timestamps, or dated external draft exists that predates
this file. The only available corroborating record is this project's own conversation
transcript: the subgroup-bin content was authored during a distinct, complete conversational
turn (responding to a "PHASE 2" request) that concluded before a separate, later conversational
turn (responding to a "PHASE 3" request) began and produced any model-training code. This is
**weaker evidence than a version-control commit** — it carries no independent cryptographic
timestamp authority, and the user reading this is the only party who can verify it (by
reviewing their own copy of the conversation). It is **not** claimed to be equivalent to commit
provenance, and it is not used here to assert the bins "cannot have been influenced by Phase 3
results" with the same confidence a commit hash would provide.

## Remediation taken (not merely noted)

1. **The mtime claim is withdrawn**, per the correction above.
2. **The file (and the entire uncommitted Phase 2/3 working tree) has been committed to git**,
   closing the "no version control" gap going forward: commit `c9c6ee3ceeefad0957797bed75abedd827567595`,
   author date `2026-08-18 17:57:33 +0530`. **This commit does NOT retroactively prove the
   subgroup bins predate Phase 3 model training** — all of Phase 2 and Phase 3's work was
   committed together, today, for the first time. It only means that from this commit forward,
   any further change to this file will have real, independently verifiable commit-level
   provenance (author, date, diff), and this exact class of problem cannot recur for future
   phases.
3. Per the instruction for when no strong corroboration exists: **the honest status of the
   subgroup bins is that they cannot be proven, by version-control evidence, to predate Phase 3
   model training.** The conversation-turn ordering above is offered as partial, weaker context,
   not as proof. Readers (including a thesis committee) should treat the bin boundaries as
   **effectively frozen as of this verification pass** (commit `c9c6ee3`) rather than as
   provably pre-Phase-3.

## Conclusion

`documentation/phase2/fairness_subgroup_protocol.md` remains the authoritative source for the
exact bin boundaries and the race/ethnicity non-collapsing decision — its CONTENT (Section
above) is unaffected by this correction. What changed is only the strength of claim about WHEN
it was decided: downgraded from "proven to predate Phase 3" to "not provably dated before Phase
3 by any available strong evidence; now version-controlled from this point forward." Cite the
file directly for the bin-boundary CONTENT in the Fairness-phase methods section; do not cite
this document (or that section) as proof of timing — cite commit `c9c6ee3` and its date instead
for any timing claim, and state that timing plainly as "frozen as of this verification pass,"
not "pre-specified before Phase 3."
