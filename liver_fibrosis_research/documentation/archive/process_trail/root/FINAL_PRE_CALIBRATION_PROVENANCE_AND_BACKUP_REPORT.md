# Final Pre-Calibration Provenance and Backup Report

**Generated:** 2026-08-18, live, in a session with continuous direct git/filesystem/network
access throughout this task.

This task's purpose was **not** another scientific audit of Phases 1-3. It was to protect the
research history, protect the frozen Calibration protocol, verify the remote backup, and preserve
the human-verification boundary. All Phase 1-3 findings referenced below are prior evidence,
not re-derived here.

## 1. Repository Access

Confirmed real, live access: `git status`, `git log`, `git branch`, `git remote`, `git fetch`,
`git ls-remote`, `git push`, and file/hash inspection all executed with real output shown
throughout this task. No step was simulated.

## 2. Pre-Push Snapshot

Recorded in `documentation/provenance/pre_push_snapshot.md` before any push occurred. Key finding
disclosed there: a live `git fetch` revealed `origin/main` was actually at `5c31e5e`, not `b390fbe`
as the carried-forward prior understanding stated — a correction, not a re-audit, disclosed
transparently rather than silently absorbed.

## 3. Current Branch

`main` (confirmed via `git branch --show-current` and `git symbolic-ref --short HEAD`, both
agreeing).

## 4. Current HEAD

Before push: `b3669b198d42b33214e30b8dd12c73643c52a66a`. This did not change during the task —
the push transmitted existing commits, it did not create new ones (aside from the provenance
documentation committed as part of this task, see §9).

## 5. Remote Configuration

Single remote, `origin` -> `https://github.com/kashyapsaksham012/Liver_Fib.git` (no credentials
embedded in the URL). No ambiguity in remote selection — Part 6's "identify the intended
authoritative remote" reduces trivially to the only remote configured. Upstream tracking was
already established: `main` -> `origin/main`.

## 6. Frozen Commit Registry

Full registry: `results/provenance/frozen_commit_registry.csv` (12 commits, from `f7b84c3` through
`b3669b1`). Each row's `commit_hash`, `subject`, and reachability were live-verified via
`git rev-parse`, `git show`, and `git merge-base --is-ancestor` — none were assumed from the task
prompt's "known examples," which were treated only as a starting hypothesis to check, per Part 3's
explicit instruction not to assume them.

## 7. Working-Tree Status

**CLEAN** at task start (0 uncommitted, 0 untracked). This task itself then added new provenance
documentation (this report and its supporting files); those additions are disclosed and committed
transparently (§9), not silently folded into the pre-existing history.

## 8. Sensitive/Raw-Data Push Safety

- **Secrets scan:** zero matches for `.env`, credentials, tokens, `.pem`, `id_rsa`, `.key` files
  anywhere in tracked files.
- **Raw NHANES data:** the 8 `.xpt` source files under `data/raw/NHANES_2017_2020/` are tracked,
  but were **already present on `origin/main`** before this task began (inherited from `b390fbe`/
  `53ce947`, both pre-existing remote commits) — this task's push did not introduce them. NHANES
  is CDC-published, public-domain, de-identified survey data, not regulated PHI, which is why this
  is disclosed as a factual finding rather than escalated as a governance emergency; no cleanup
  action was taken or required.
  This governance question was not decided by this task — it was already decided (by whoever
  performed the earlier push) before this session began.
- **New push contents:** verified via `git diff --stat origin/main..HEAD` before pushing — all 33
  changed files were documentation, CSV/markdown audit artifacts, and one Python test file. Zero
  files under `data/raw/`, `.env`, or any credential pattern were part of the 6 pending commits.

**Conclusion: push was safe.** No new sensitive-data or raw-data exposure was introduced by this
task.

## 9. Remote Verification

**REMOTE BACKUP = VERIFIED.** Full detail: `results/provenance/remote_backup_verification.md`.
Two independent live checks after `git push origin main`:
1. `git fetch origin` + `git rev-parse HEAD` vs `git rev-parse origin/main` -> exact match
   (`b3669b198d42b33214e30b8dd12c73643c52a66a`).
2. `git ls-remote origin refs/heads/main` (a direct query to GitHub's server, bypassing any local
   cache) -> same hash, confirmed independently.

All named frozen commits (`194aa69`, `2436d95`, `cf44f44`, `b3669b1`, plus `d02a4bb` and `45e86ce`)
confirmed reachable on `origin/main` via `git merge-base --is-ancestor`.

No tag was created (no established tagging convention exists in this repository; none of this
task's four objectives strictly required one) — disclosed explicitly, not silently skipped.

## 10. Local/Remote Consistency

**LOCAL HEAD = REMOTE HEAD**, confirmed by the two independent checks in §9. No divergence, no
force-push was needed or used, and none is required going forward given the fast-forward push
succeeded cleanly.

## 11. Calibration Protocol Commit

| Field | Live-verified value |
|---|---|
| Commit hash | `2436d9554647c65af43e7d8cc61cdfeed9fb9a6a` |
| Commit timestamp | 2026-08-18 20:52:52 +0530 |
| Protocol document checksum (recomputed live this task) | `3c843ad02cd91736a597ad3256a6c6309ffac2819a882c72f77b9220c64fca1d` — matches the value recorded at commit time in `calibration_protocol_commit_record.md` exactly |
| Remote verification | VERIFIED — reachable on `origin/main` |

This commit contains exactly one file (`documentation/calibration/CALIBRATION_PROTOCOL_FREEZE.md`),
no implementation code, confirmed both at the time it was created and again independently this
task.

## 12. Human Spot-Check Status

**HUMAN SPOT-CHECK — NOT YET PERFORMED.** Instructions (`documentation/end_to_end/
human_spot_check.md`) already prefer locked test-set integrity as the primary target, per the
prior task. This task added `documentation/end_to_end/human_spot_check_record_template.md`, a
structured record the researcher fills in personally after running the command in their own
terminal. This AI has not run the check on the researcher's behalf and does not claim it complete.

## 13. Provenance State

Full detail: `documentation/provenance/pre_calibration_provenance_state.md`. Summary: local
frozen history (12 commits) + verified remote backup + standalone Calibration protocol commit
(commit-level provable) + source-of-truth drift tests (16/16 passing) + archived Phase 1-3
evidence + disclosed historical provenance limitation (Phase 2/3 bundled commit, unresolved but
non-blocking) + human spot-check pending.

## 14. Remaining Risks

- Sub-commit chronology within `c9c6ee3` (Phase 2/Phase 3 bundled) remains Tier D provenance —
  unresolved, non-blocking, previously disclosed, unchanged by this task.
- Raw NHANES data and the ~6 MB interim master CSV are present on the public remote — pre-existing,
  not introduced by this task, and not a regulated-data concern given NHANES's public-domain
  status, but noted here as an ongoing repository-governance fact the researcher should be aware
  of if repository visibility (public/private) is ever reconsidered.
- Human spot-check remains unperformed — expected and non-blocking per this task's own rules.

No risk identified rises to a level requiring escalation beyond disclosure.

## 15. Readiness for Calibration

**READY FOR CALIBRATION — HUMAN SPOT-CHECK PENDING**

Basis: frozen history has been safely pushed and independently verified on the remote (two
separate live checks, including a direct server-side query); the Calibration protocol is
committed standalone and confirmed present both locally and remotely; no sensitive data was
newly exposed by this task; local and remote commits match exactly (`b3669b1` = `b3669b1`); and
the human spot-check has correctly not been performed by this AI and remains an open item for the
researcher, which per this task's own Part 18 rule does not block this status.
