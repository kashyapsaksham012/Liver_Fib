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

## Chronological proof (file-system timestamps, not calendar-date-only)

Because every phase of this project happened within a single working session, calendar dates alone
(all "2026-08-18") cannot distinguish ordering. Actual file modification timestamps do:

| File | Timestamp |
|---|---|
| `documentation/phase2/fairness_subgroup_protocol.md` (bins frozen) | **14:21:08** |
| `documentation/phase2/PHASE2_PROTOCOL_FREEZE.md` (Phase 2 closure) | 14:24:20 |
| `PHASE2_ANALYTICAL_PROTOCOL_AND_FEASIBILITY_REPORT.md` (Phase 2 report) | 14:28:41 |
| `src/phase3_common.py` (first Phase 3 code, defines the primary predictor/target constants) | 14:43:04 |
| `src/phase3_05_train_and_tune.py` (first model actually trained) | 14:48:34 |
| `PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md` (test-set results first reported) | 17:01:17 |

**The subgroup bins were written to disk 22 minutes before the first Phase 3 code file even
existed, and ~2 hours 40 minutes before any test-set outcome was visible.** This is direct,
file-system-level evidence against hindsight bias, not an assertion.

## Conclusion

No action required beyond this citation. `documentation/phase2/fairness_subgroup_protocol.md` is
the authoritative, dated, pre-Phase-3-freeze source for all subgroup bin boundaries and the
race/ethnicity non-collapsing decision — cite it directly in the Fairness-phase methods section.
