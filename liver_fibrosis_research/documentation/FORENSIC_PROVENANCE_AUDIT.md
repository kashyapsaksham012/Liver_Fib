# Forensic Research Provenance, Timeline, Reproducibility & Scientific-Integrity Audit

**Generated:** 2026-08-18 18:xx (this audit)

## Auditor disclosure (required for honesty, not optional)

**This audit was performed by the same AI agent (me) that executed Phases 1–3 of this project,
in the same conversation session.** I have direct, live shell/filesystem/git access to the actual
repository — every command below was actually executed, with real output pasted verbatim, not
simulated or inferred. But I am not an independent third party: I cannot verify my own
uncommitted, pre-bulk-commit actions from outside my own operation of the agent. Where this
limits an evidence level, it is stated explicitly rather than glossed over.

---

## FAST TIMELINE TRIAGE (real command output)

```
$ find data/raw data/interim data/processed results models documentation src -maxdepth 2 -type f -exec stat -f "%SB %N" -t "%Y-%m-%d %H:%M:%S" {} \;
```
Earliest artifact: `data/raw/NHANES_2017_2020/P_BMX.xpt` — **2026-08-18 11:18:28**
Latest artifact: `documentation/phase3/phase3_verification_log.md` — **2026-08-18 18:00:30**

**Every artifact in every major directory — raw data, interim data, processed data, results,
models, documentation, source code — has a birth-timestamp on the single calendar day
2026-08-18, spanning under 7 hours.** No artifact predates this window. This triage result alone
is strong (though Level C, not definitive) grounds to proceed with the full audit rather than
accept the project's phase labels as implying separate, temporally-distinct research phases.

---

## PHASE 1 — REPOSITORY STATE (real output)

```
$ git status
On branch main
Your branch is ahead of 'origin/main' by 2 commits.
nothing to commit, working tree clean

$ git branch -a
* main
  remotes/origin/main

$ git remote -v
origin  https://github.com/kashyapsaksham012/Liver_Fib.git (fetch/push)
```

## PHASE 2 — COMPLETE GIT HISTORY (real output, full log)

```
$ git log --all --date=iso --pretty=fuller
```

| Commit | AuthorDate | CommitDate | Message |
|---|---|---|---|
| `44a77a1` | 2026-08-18 11:01:53 +0530 | same | first commit |
| `f7b84c3` | 2026-08-18 11:05:25 +0530 | same | add research info plan |
| `53ce947` | 2026-08-18 11:28:40 +0530 | same | Phase 1: data assembly pipeline, audit reports, master dataset |
| `b390fbe` | 2026-08-18 14:08:58 +0530 | same | Phase 1 closure: remediated pipeline, canonical cohorts, 24 validation tests passed |
| `c9c6ee3` | 2026-08-18 17:57:33 +0530 | same | Phase 2 protocol freeze, Phase 3 baseline ML, and Phase 3 remediation/closure |
| `d218152` | 2026-08-18 18:01:12 +0530 | same | Withdraw mtime-based provenance claim; replace with real git evidence |

**Reflog cross-check** (`git reflog --date=iso`): every entry is a plain sequential `commit:`
action; timestamps match commit dates exactly; no `rebase`, `reset --hard`, or force-push
markers. **No evidence of history rewriting.**

### CRITICAL STRUCTURAL FINDING

**The entire repository's history spans 6 commits over ~7 hours on a single day.** More
importantly: **`c9c6ee3` is a single bulk commit containing ALL of Phase 2 (protocol freeze) AND
Phase 3 (baseline ML + full remediation) simultaneously.** This means:

- Git *can* prove: Phase 1 (`53ce947`/`b390fbe`) was committed, and therefore existed, before
  `c9c6ee3` (Phase 2+3+remediation).
- Git *cannot* prove: that Phase 2's protocol decisions (outcome threshold, predictor list,
  fairness bins, etc.) were finalized before Phase 3's model training began, because both are
  inside the same commit. **No sub-commit chronology is available from git for this boundary.**

### Artifact Git-evidence table

| Artifact | Git evidence | Earliest commit | Evidence strength | Notes |
|---|---|---|---|---|
| `data/interim/nhanes_master_phase1.parquet` (Phase 1 master data) | Tracked | `53ce947` | **Level A** (direct commit) | Predates all Phase 2/3 work by 3 commits and ~6.5h |
| `documentation/phase2/fairness_subgroup_protocol.md` | Tracked | `c9c6ee3` (first appearance) | **Level A for "exists"; NOT Level A for "predates Phase 3 training"** | Same commit as all Phase 3 model artifacts — see structural finding above |
| `src/phase3_05_train_and_tune.py` (model training) | Tracked | `c9c6ee3` (same commit as above) | Level A for "exists" | — |
| `results/predictions/test_predictions_*.csv` | Tracked | `c9c6ee3` (same commit) | Level A for "exists" | — |
| `documentation/phase3/conformal_calibration_protocol.md` | Tracked | `c9c6ee3` | Level A for "exists" | Written same session as split-reservation script |

---

## PHASE 3 — FILESYSTEM ARTIFACT TIMELINE (real output, key transitions)

| Artifact | Birth time (real, live) | What it represents |
|---|---|---|
| `P_BMX.xpt` etc. (raw NHANES) | 11:18–12:00 | Raw data acquisition |
| `nhanes_master_phase1.parquet` | 11:28:15 | Phase 1 merged dataset |
| `fairness_subgroup_protocol.md` | 14:21:08 (per prior mtime check, corroborating only) | Phase 2 fairness bins written |
| `analysis_dataset_primary.parquet` | 14:25:25 | Phase 2 analysis dataset generated |
| `test_ids.csv` | 14:45:56 | Test set locked |
| `model_logistic_v1.joblib` … `model_mlp_v1.joblib` | 14:48:59–14:49:36 | 5 baseline models fit |
| `model_mlp_balanced_v1_sensitivity.joblib` | 16:50:46 | Remediation sensitivity model |
| `proper_train_ids.csv` / `conformal_calibration_ids.csv` | 17:47:19 | Conformal split reserved (this verification pass) |

**Standing caveat, restated per the evidence hierarchy: this table is Level C (filesystem
metadata) corroboration only.** It is internally consistent with the documented sequence
(data → protocol → split → training → remediation → conformal reservation) and shows no
contradiction, but mtimes are not cryptographically tamper-proof and are not independently
verifiable by a third party from outside this session.

---

## PHASE 4 — MASTER DOCUMENT AUDIT (real grep output)

```
$ grep -n "Generated:" PHASE1_DATA_ASSEMBLY_REPORT.md PHASE2_ANALYTICAL_PROTOCOL_AND_FEASIBILITY_REPORT.md PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md
PHASE1_DATA_ASSEMBLY_REPORT.md:3:**Generated:** 2026-08-18 13:27:50
PHASE2_ANALYTICAL_PROTOCOL_AND_FEASIBILITY_REPORT.md:3:**Generated:** 2026-08-18 14:28:41
PHASE3_MODEL_DEVELOPMENT_AND_BASELINE_RESULTS_REPORT.md:3:**Generated:** 2026-08-18 17:01:16

$ grep -rn -i "over the past|weeks ago|months ago|previously conducted|extended period" *.md documentation/
(no matches)
```

**Finding: no document falsely claims an extended timeline.** All three "Generated" timestamps
are self-consistent with each other, with the git commits, and with the filesystem triage — and
no document contains language implying the work spanned more than one day. The real
documentation problem is not fabricated dates; it is the **"Phase 1/2/3" labeling scheme
itself**, which invites a reader to assume three temporally-separated research phases (as in a
typical multi-week thesis timeline) when in fact all three occurred in one continuous ~7-hour
session. This is a legitimate framing risk, addressed in Recommendations below.

---

## PHASE 6/13/14 — FROZEN-DECISION, LEAKAGE, AND POST-HOC-POSSIBILITY AUDIT

For each decision, classified per the required evidence labels. **Given the structural finding
above (Phase 2+3 in one commit), NO decision below can be rated VERIFIED-PREEXISTING purely
from git.** Where code structure provides independent proof of leakage-safety (a stronger claim
than mere temporal ordering), that is stated separately and is Level A regardless of commit
granularity, because it proves a structural impossibility, not merely a claimed chronology.

| Decision | Evidence label | Basis |
|---|---|---|
| Outcome threshold (LUXSMED≥8.2kPa) defined before model training | **CURRENTLY-DOCUMENTED-ONLY** | No git commit boundary separates protocol doc from training code; mtime-consistent only (Level C) |
| Primary predictor list (10 vars) fixed before training | **CURRENTLY-DOCUMENTED-ONLY** | Same limitation |
| Fairness subgroup bins fixed before any fairness result | **CURRENTLY-DOCUMENTED-ONLY** (downgraded from a prior, now-withdrawn stronger claim — see `subgroup_definitions_verification.md`) | No fairness analysis has been run at all yet (Phase 4/5/6 not started), so there is no fairness *result* these bins could have been reverse-engineered from — this somewhat mitigates but does not eliminate the provenance gap |
| **Test set never used in hyperparameter search** | **VERIFIED — Level A, structural** | `grep -n "test_ids" src/phase3_05_train_and_tune.py` → **zero matches** (exit code 1, confirmed live above). This is not a chronology claim; it is proof the training script cannot structurally reference test data, regardless of when it was written or committed. |
| **Threshold (Youden's J) computed before test set is loaded** | **VERIFIED — Level A, structural** | Live line-number check: `youdens_j_threshold(...)` at line 55, `test_ids.csv` load at line 65, same script, sequential execution — the test set literally does not exist in memory yet when the threshold is computed. |
| **Train/test/calibration partitions are disjoint** | **VERIFIED — Level A, reproduced live** | Direct set-intersection recomputation this session: all pairwise overlaps = 0 |
| **All 5 discrimination metrics reproduce from raw predictions** | **VERIFIED — Level A, reproduced live** | Recomputed AUC/PR-AUC/sensitivity/specificity for all 5 models from `test_predictions_*.csv`, bypassing every summary table — exact match |
| **44/44 tests pass** | **VERIFIED — Level A, executed live this session** | Both suites re-run in this exact audit, 20/20 + 24/24 |
| Class-imbalance policy (weights, not SMOTE) applied consistently except MLP | **VERIFIED — Level A** | Directly inspected `phase3_model_registry.csv` and model-fitting code; MLP exception is a real, disclosed sklearn API constraint, not a hidden inconsistency |
| Conformal calibration set (N=1,002) disjoint from locked test set | **VERIFIED — Level A, reproduced live** | Set-intersection = 0, this session |
| **Models used for the eventual conformal step are validly unseen by the calibration set** | **CONTRADICTED-IF-MISUSED / currently POST-HOC-POSSIBLE-PREVENTED-BY-DOCUMENTATION** | The 5 frozen Phase 3 models were fit on the FULL 5,007-row training partition, which *includes* the 1,002 calibration rows reserved today. Those specific artifacts are **not valid** for direct use in split conformal prediction (calibration data must be unseen by the scoring model). This is explicitly flagged in `conformal_calibration_protocol.md` as a mandatory refit-on-`proper_train_ids.csv` requirement before any conformal code runs. As of this audit, **that refit has not yet been performed** — it is correctly documented as required, not yet executed. |

### Post-hoc-possible flags

No evidence of post-hoc selection was found for: outcome threshold, predictor list, model
hyperparameters (structurally proven test-isolated above), or the classification threshold
(structurally proven test-isolated above). **Fairness bins and the outcome threshold remain
`CURRENTLY-DOCUMENTED-ONLY`** rather than cleared, because — per the finding above — no
commit-level boundary exists to rule out that they were adjusted during the same working
session in which downstream code was also being written, even though no result yet exists that
could have motivated such an adjustment (fairness/calibration have not been run).

---

## PHASE 15 — PHASE-CLOSURE STATUS

| Phase | Claimed status | Verified status | Basis |
|---|---|---|---|
| Project Phase 1 (Data) | COMPLETE AND FROZEN | **CLOSED WITH DOCUMENTED PROVENANCE LIMITATIONS** | Artifacts exist, reproducible, committed in its own distinct commit (`53ce947`/`b390fbe`) before all downstream work — the strongest provenance in the project |
| Project Phase 2 (Protocol) | COMPLETE AND FROZEN | **CLOSED WITH DOCUMENTED PROVENANCE LIMITATIONS** | Documents exist and are internally consistent; NOT separately committed from Phase 3 — see structural finding |
| Project Phase 3 (Baseline ML) | COMPLETE AND FROZEN | **CLOSED WITH DOCUMENTED PROVENANCE LIMITATIONS** | Discrimination results independently reproduced live (Level A); leakage-safety structurally proven (Level A); chronology relative to Phase 2 not separately provable (Level C only) |
| Calibration / Fairness / Uncertainty | NOT STARTED | **CONFIRMED NOT STARTED** | No calibration metric, fairness metric, or conformal coverage number exists anywhere in the repository (grep-confirmed: no fairness/calibration result files exist) |

None of the three phases qualifies for the strictest "CLOSED — VERIFIED" tier, because that tier
requires provenance adequacy that bulk same-session commits cannot supply. All three are honestly
"CLOSED WITH DOCUMENTED PROVENANCE LIMITATIONS" — the science is internally consistent and
independently reproducible from artifacts, but the historical chronology claims rest on weaker
evidence than a properly incrementally-committed project would have.

---

## PHASE 16 — TRUE TIMELINE RECONSTRUCTION

| Phase | Claimed date | Earliest execution evidence | Earliest final-methodology evidence | Result evidence | Git evidence | Confidence |
|---|---|---|---|---|---|---|
| Data assembly | 2026-08-18 | 11:18:28 (raw file birth) | 11:28:40 (`53ce947` commit) | `nhanes_master_phase1.parquet` | **Level A** (own commit) | High |
| Protocol freeze | 2026-08-18 | ~14:08–14:28 (mtime range) | 14:28:41 (report `Generated:`) | Protocol markdown files | Level C only (bundled in `c9c6ee3`) | Moderate |
| Baseline ML | 2026-08-18 | 14:43–14:49 (script/model mtimes) | 17:01:16 (report `Generated:`) | Test predictions, reproduced live | Level C only (bundled in `c9c6ee3`) | Moderate |
| Remediation/closure | 2026-08-18 | ~16:50–18:01 | 18:01:12 (`d218152` commit) | This audit | **Level A** (own + prior commit) | High |

---

## PHASE 17 — TRUE PROJECT STATUS

> ### STATUS D — Most execution appears to have occurred recently (today), and previous "Phase N complete and frozen" language, while not factually false about content, requires the chronology caveat established in this audit.

**Why not Status B:** Status B implies genuine research spread over time with merely-late Git
hygiene. That is not what the evidence shows — filesystem birth times, commit dates, and report
`Generated:` timestamps are unanimous and consistent: this is a single ~7-hour working session.

**Why not Status C:** Status C implies some phases were only planned/documented without
execution. That is not supported either — Phase 1 through 3 all have real, independently
reproducible artifacts (raw data merged, models actually trained, test predictions actually
scored, 44 tests actually passing on live re-run).

**Why Status D, specifically:** the work is real and reproducible, but it was executed in one
continuous same-day session, not across the multi-week timeline a "Phase 1 → Phase 2 → Phase 3"
thesis structure conventionally implies. This does not mean the science is invalid — it means the
project's own phase-freeze language needs a chronology disclaimer, which this audit now supplies.

---

## PHASE 18 — WHAT IS NOT A PROBLEM

- **Same-day execution is not, by itself, a scientific integrity violation.** Nothing in the
  scientific method requires phases to be separated by calendar time — it requires that later
  information not leak into earlier decisions. That specific claim (test-set isolation) was
  independently, structurally verified above (Level A), separate from the timeline question.
- **Bulk commits are a provenance weakness, not proof of misconduct.** No evidence of
  backdating, rewritten history, or fabricated results was found — reflog is clean, all
  timestamps are mutually consistent, and 44/44 tests plus 5/5 models' metrics reproduce exactly
  live.
- **The MLP class-imbalance asymmety and the not-yet-performed conformal refit are already
  self-disclosed** in the project's own documentation, not concealed findings of this audit.
- **A missing separate validation partition is a documented, intentional design choice**
  (CV-based development, per the frozen protocol), not an undisclosed gap.

---

## PHASE 19 — RECOVERY PLAN / REMEDIATION (priority-ordered)

| Priority | Issue | Evidence | Required action |
|---|---|---|---|
| **P1** | Phase 2/3 protocol decisions cannot be shown, via git, to predate downstream code | Structural finding above | Going forward: commit Phase 2 protocol documents in their OWN commit, separately and BEFORE writing any Phase 3 code — do this for Calibration/Fairness/Uncertainty starting now |
| **P1** | Conformal-valid models not yet refit on `proper_train_ids.csv` | `conformal_calibration_protocol.md` explicitly flags this as outstanding | Refit all 5 model families on the 4,005-row proper-train partition using frozen hyperparameters BEFORE any conformal code runs; save as separately-versioned artifacts |
| **P2** | "Phase 1/2/3 complete and frozen" language invites a multi-week-timeline misreading | Phase 4 audit above | Add a one-line chronology disclaimer to each phase report: "executed YYYY-MM-DD in a single working session; see FORENSIC_PROVENANCE_AUDIT.md for full provenance" |
| **P3** | 2 commits (`c9c6ee3`, `d218152`) are local-only, not pushed to `origin/main` | `git log origin/main -1` shows origin still at `b390fbe` | Push to origin (requires explicit user confirmation — not done automatically by this audit) |
| **P3** | No experiment manifest file exists yet | This audit | Create `EXPERIMENT_MANIFEST.md` per Phase 21 template below |

---

## PHASE 20/21 — FUTURE VERSION-CONTROL PROTOCOL & MANIFEST

**Adopted rule starting now:** every future phase (Calibration, Fairness, Uncertainty) gets (1) a
phase-start commit of its frozen protocol document, standing alone, BEFORE any phase-specific
code is written, and (2) a phase-close commit after results are produced — never bundled
together. This is the single concrete fix that would allow the *next* phase to earn a true
"CLOSED — VERIFIED" rating instead of "CLOSED WITH DOCUMENTED PROVENANCE LIMITATIONS."

### Experiment manifest (live values, this session)

| Field | Value |
|---|---|
| Git commit (HEAD) | `d218152` |
| Python version | 3.14.3 |
| Key packages | scikit-learn==1.9.0, xgboost==3.4.1, lightgbm==4.7.0, imbalanced-learn==0.14.2 (see `requirements-phase3-lock.txt`) |
| OS | macOS (Darwin), arm64 |
| Random seed | 42 |
| Cohort N / prevalence | 7,153 / 9.31% |
| Train / test N | 5,007 / 2,146 |
| Proper-train / calibration N | 4,005 / 1,002 |
| Feature list | RIDAGEYR, RIAGENDR, BMXBMI, LBXSATSI, LBXSASSI, LBXSAL, LBXSAPSI, LBXSTB, LBXPLTSI, LBDHDD |
| Outcome | LUXSMED ≥ 8.2 kPa |
| Test ROC-AUC range | 0.8229–0.8429 (reproduced live) |
| Execution date | 2026-08-18 |

---

## PHASE 22 — FINAL AUDIT VERDICT

See the chat response accompanying this file for the required numbered sections
(Executive Verdict, Timeline, Git Provenance, Frozen Decisions, Scientific Integrity,
Reproducibility, Critical Problems, GO/NO-GO).
