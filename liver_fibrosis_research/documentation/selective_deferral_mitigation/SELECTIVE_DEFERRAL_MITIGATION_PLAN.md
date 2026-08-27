# Selective-Deferral Mitigation — plan and execution record

**Started 2026-08-27** under **Protocol Amendment #17** (`AMENDMENT_17_TEXT.md`). This is an
executing analysis, not a proposal.

## Goal

Turn "we identified a subgroup reliability failure we could not fix" into a **demonstrated (or
precisely bounded) mitigation**, by reframing the model as the *triage / defer* step of the
FIB-4 → VCTE pathway: uncertain cases are **deferred to elastography** (which the standard pathway
already does), so a deferral costs an *elastography referral*, not full-cohort specificity — which
is why the seven prior mitigations, judged against a classification gate, all failed.

## Non-negotiables (enforced by script order + this record)

- No retraining, no hyperparameter search, no new predictors/outcome. Works from the **frozen
  Phase-6 conformal artifacts** (`results/uncertainty/calibration_scores_*.csv`,
  `test_set_prediction_sets.csv`, `conformal_thresholds_by_model.csv`) — models are never loaded.
- Deferral rule developed on the **conformal-calibration partition only** (N = 1,002); frozen to a
  hashed manifest **before** any locked-test access.
- CAND_1 locked test (N = 2,146) accessed **once** (Phase 4).
- Acceptance gate (§Gate) fixed **before** Phase 4. **No post-hoc gate relaxation.**
- All five model families.
- Method is **not** novel (conformal + group-conditional deferral for clinical triage: *Sci Rep*
  2026, `10.1038/s41598-026-40637-w`). Application-level contribution only.
- Hazard to disprove, not assume: naive selective prediction can *magnify* subgroup gaps
  (Jones et al., *ICLR* 2021).

## Gate (pre-registered — fixed before Phase 4)

Retained (non-deferred) population, per model, "≥ 4/5" = at least four families.

| ID | Criterion |
|---|---|
| **G1** | BMI-Obese **and** Age-60+ retained conformal coverage ≥ 0.88 with Wilson-CI upper ≥ 0.90 (not significantly < 0.90 after BH-FDR), ≥ 4/5 models each |
| **G2** | Retained marginal coverage ∈ [0.88, 0.93], all 5 models |
| **G3** | Normal-BMI / Overweight / Age-18–39 retained coverage ≤ 0.95, ≥ 4/5 models (redistribution, not uniform deferral) |
| **G4** | Retained Normal-vs-Obese sensitivity gap ≤ 15 pp (STRONG: ≤ 10 pp), ≥ 4/5 models (baseline 27–48 pp) |
| **G5** | Retained Age-60+ vs 40–59 sensitivity gap not > 5 pp worse than frozen baseline, ≥ 4/5 |
| **G6** | Overall deferral (= referral) rate ≤ 40 % |
| **G7** | No subgroup deferral rate > 2.5× the overall rate |
| **G8** | Excess elastography referrals per 1,000 reported overall + per subgroup; flag (not fail) any subgroup > 400/1,000 |
| **G9** | G1/G2/G4 replicate on CAND_2 and CAND_3 with the transferred policy — **BLOCKED in this pass** (needs the CAND_2/CAND_3 model refit; joblib/sklearn/xgboost/lightgbm not available in this environment). Recorded as future work. |

## Verdict tiers (fixed)

| Verdict | Condition |
|---|---|
| **FULL SUCCESS** | G1–G7 on CAND_1 **and** G9 on both sensitivity cohorts |
| **QUALIFIED SUCCESS** | G1–G7 on CAND_1; G9 partial or (as here) not yet assessable; **or** G4 only in 10–15 pp |
| **PARTIAL SUCCESS** | G1–G3 met (coverage restored) but G4 not (gap only bounded to 15–25 pp), or single-attribute fixed / intersection not |
| **BOUNDED NEGATIVE** | G1–G7 unmeetable on CAND_1, or met only with deferral > 40 % / subgroup referrals > 400 per 1,000 |
| **DEVELOPMENT-STAGE NEGATIVE** | No candidate passes on the calibration partition (Phase 3); test never touched |

Every tier is publishable and every tier beats "no acceptable mitigation".

## Phases (checkbox = done)

- [x] **Phase 0** — Amendment #17, this plan, `PRE_EXECUTION_SNAPSHOT.md` (frozen-input hashes), gate fixed.
- [x] **Phase 1–2** — `src/deferral_01_dev_and_baseline.py`. Leakage checks PASS (0 overlap with
      proper-train / locked test). Sub-amendment #17a **not** triggered (BMI-Obese calib cell
      n=407, Age-60+ n=339). The subgroup under-coverage **reproduces** on the calibration
      partition (BMI-Obese 0.79–0.82, Age-60+ 0.83–0.86; marginal 0.900–0.901).
      → `PHASE1_2_DEV_AND_BASELINE.md`
- [x] **Phase 3** — `src/deferral_02_rule_development.py`. Candidates 3a / 3b / 3d / 3e on the
      calibration partition. **Verdict: DEVELOPMENT-STAGE NEGATIVE** — no candidate meets the full
      pre-registered core gate (G1∧G2∧G3∧G6∧G7). Per the plan, **the locked test was not
      touched.** Characterised, not blank (see §Result). → `PHASE3_RULE_DEVELOPMENT.md`
- [ ] **Phase 4** — **SKIPPED** per the pre-registration (development-stage negative ⇒ no
      locked-test access).
- [ ] **Phase 5** — not applicable (no rule to replicate).
- [ ] **Phase 6** — diagnostics: expand the mechanism (see §Result); trade-off curves for 3d;
      the levelling-down argument; comparison to the 7 prior mitigations. → `PHASE6_DIAGNOSTICS.md`
- [ ] **Phase 7** — fold the characterised negative into the manuscript (it *sharpens* §3.7 / §4,
      it does not soften it) + register updates.
- [ ] **Phase 8** — validation tests + Amendment #17 closure.

## Result (Phase 3, 2026-08-27)

**DEVELOPMENT-STAGE NEGATIVE — but a sharper, mechanism-explained one than the study's current
"no acceptable mitigation".** On the calibration partition:

1. **Deferring uncertain cases makes coverage *worse* (3a).** In BMI-Obese and Age-60+, conformal
   coverage is carried by the two-class {pos,neg} prediction sets (which always contain the
   truth); the misses are wrong *singletons*. Deferring the two-class sets drops retained
   BMI-Obese coverage to 0.58–0.82.
2. **Deferring weak singletons (3b)** lifts the under-covered groups toward 0.90 only at a
   15–40 % deferral rate, fails G2 (retained marginal coverage rises), and degenerates for the
   near-singleton MLP (defers ~95 % of obese cases).
3. **Group-conditional (Mondrian) conformal (3d) restores BMI-Obese and Age-60+ coverage to
   ≥ 0.88 for all 5 model families with zero deferral** — an improvement on Project Phase 7's
   5/9 targets — **but necessarily raises retained marginal coverage to 0.94–0.95** (G2 fail) and
   leaves the well-served subgroups above 0.95 (G3 fail). Forcing marginal coverage back to target
   would require deliberately under-covering the well-served subgroups: *levelling down*, the
   fairness anti-pattern documented for coverage-equalising conformal methods (arXiv:2412.07879;
   ICLR 2025).

**The publishable finding:** on this task, (a) subgroup-safe and target-level marginal conformal
coverage cannot be jointly achieved by any pre-registered post-hoc method without levelling down
the well-served subgroups; and (b) the subgroup under-coverage is not concentrated in
flagged-uncertain cases — so selective deferral cannot fix it — but in *confidently-wrong
singleton predictions* in the obese and older groups, i.e. a failure of the model's
within-subgroup score ordering that a post-hoc decision layer cannot repair. A true fix would
require intervening in training (reweighting, subgroup-aware objectives), which is outside the
frozen scope and is stated as future work.

## Candidate deferral rules (fixed in Phase 0 — none may be added later)

- **3a** — defer if the conformal prediction set is `{positive, negative}` (ambiguous / size 2).
- **3b** — defer case *i* in group *g* if `nonconformity_of_more_likely_class(i) > τ_g`, where
  `τ_g` is the smallest threshold making retained conformal coverage in group *g* ≥ 0.90 on the
  calibration partition. Overlap (Obese ∩ 60+): take the larger (more conservative) `τ_g`.
- **3c** — 3b, then additionally defer the lowest-`P(positive)` retained **positives** in the
  deficit group (Normal-BMI) until the calibration-partition retained Normal-vs-Obese sensitivity
  gap ≤ 15 pp.
- **3d** — group-conditional (Mondrian) calibration quantiles `q̂_g` for the prediction sets
  (tightening the over-covered groups), then defer only the residual two-class sets.

Selection tiebreak (fixed): lowest overall deferral rate; then smallest Normal-vs-Obese gap.
