# FINAL RESEARCH QUALITY ASSESSMENT

Read-only audit, 2026-08-27. The repository has **no pre-existing numeric scoring framework**
(status registers use categorical labels only), so this assessment uses the qualitative
categories **STRONG · ADEQUATE WITH LIMITATIONS · LIMITED · INSUFFICIENT**. No numeric scores are
assigned.

---

| Dimension | Rating | Basis |
|---|---|---|
| Methodological rigor | **STRONG** | Frozen pre-training protocol (outcome threshold + predictors + cohort), verified by hash lineage; OOF-only calibration; locked test touched once per phase; pre-specified fairness dimensions and metrics; pre-specified conformal target; FDR at analysis and project level; multiple independent audit passes; disciplined preservation and demarcation of superseded/invalid work. |
| Internal validity | **STRONG** | No test-label leakage found in fresh pathways (contamination audit 8/8 PASS); three early diagnostic scripts with documented defects superseded, not used; partitions disjoint and prevalence-stratified; thresholds and calibration params derived from OOF only; BMI disparity independently reproduced before diagnosis. |
| Reproducibility | **ADEQUATE WITH LIMITATIONS** | Strong infrastructure (split IDs, model/result lineage, frozen hashes, env locks, 44/44 internal tests). Disclosed gaps: Phase 5 MI conformal `LINEAGE NOT FOUND`; frozen 8.2-kPa protocol commit / model manifest `NOT FOUND`; joint mitigation generating pipeline `NOT FOUND`; corrected Phase 4 runtime log absent; one dependency-graph transcription gap. None is load-bearing for a primary claim. This audit was read-only and did not re-execute the primary code tree. |
| Statistical completeness | **ADEQUATE WITH LIMITATIONS** | Bootstrap and Wilson-score CIs and BH-FDR throughout; pooled 182-test FDR. Weak spots: no candidate-vs-candidate inference for mitigation (descriptive gates only — appropriate for "no acceptable mitigation" conclusions); MI relies on correction-ceiling p-values. (Conformal subgroup finding re-measured on 8.0 kPa / CAND_2 / CAND_3 — Amendment #16 — BMI-Obese robust; Age-60+ direction robust, significance power-sensitive.) |
| Fairness evidence | **ADEQUATE WITH LIMITATIONS** | BMI disparity: STRONG (5/5, reproduced, triangulated across 3 cohorts, mechanism diagnosed). Age disparity: LIMITED (4/5, specification-sensitive, non-monotonic). Mitigation: no acceptable fix identified — honestly reported. Sex/race: no significant disparity in primary complete-case test set (in-distribution only). |
| Uncertainty evidence | **ADEQUATE WITH LIMITATIONS** | Marginal conformal validity: STRONG (guaranteed + empirically met). Subgroup coverage failure: STRONG as a *finding*, now replicated on 8.0 kPa / CAND_2 / CAND_3 (Amendment #16 — BMI-Obese robust; Age-60+ direction robust). Intersectional coverage: LIMITED (descriptive, N=294). Mitigation of coverage (Mondrian): PARTIALLY EFFECTIVE with a disclosed tolerance breach. Joint/M4b/AFCP: EXPLORATORY, do not achieve acceptable subgroup/intersectional validity. |
| Robustness | **ADEQUATE WITH LIMITATIONS** | Discrimination, calibration correction, and the BMI-Obese disparity robust across 8.0 kPa, CAND_2, CAND_3, full-pipeline 8.0-kPa re-run, and targeted MI. The full 8.0-kPa re-run's own verdict is "some major findings are threshold-sensitive" (Age significance, some conformal detail). Conformal subgroup coverage re-measured on 8.0 kPa / CAND_2 / CAND_3 (Amendment #16): BMI-Obese under-coverage robust across all four constructions; Age-60+ direction robust, significance power-sensitive. |
| Transportability | **LIMITED** | No out-of-sample (later-cycle or independent-cohort) evaluation is within the scope of this study. Phase 8 NHB holdout is within-NHANES. No non-NHANES external validation; no compatible cohort identified. |
| Manuscript readiness | **ADEQUATE WITH LIMITATIONS** | Ready to draft with the mandated qualifications; one documentation conflict (C1) and two untracked pre-registered analyses (secondary outcomes, weighted training) are author-side housekeeping, not blocking. See `MANUSCRIPT_READINESS_ASSESSMENT.md`. |

---

## Composite characterisation

**The study is methodologically strong and internally valid; its reproducibility, statistical
completeness, fairness/uncertainty evidence, and robustness are adequate with clearly disclosed
limitations; and its transportability is limited.**

The work's value is not a deployable model — discrimination is modest, no reliability–fairness
mitigation succeeded, and no out-of-sample evaluation has been performed — but a rigorously
demonstrated methodological point: discrimination plus aggregate calibration are insufficient evidence of
subgroup-safe reliability, and the specific subgroups that fail (obese, older, and their
intersection) are identifiable, reproducible, mechanism-linked, and resistant to the mitigation
strategies tested. That contribution is well supported by the repository's evidence.

## What would raise each "ADEQUATE WITH LIMITATIONS" / "LIMITED" rating

- **Reproducibility → STRONG:** reconstruct the Phase 5 MI conformal pipeline; locate the frozen
  8.2-kPa protocol commit / model manifest; commit the joint-mitigation generating script.
- **Statistical completeness → STRONG:** add candidate-vs-candidate comparative inference for the
  mitigation analyses (if any mitigation is ever re-opened).
- **Uncertainty / robustness → STRONG:** ~~run the conformal subgroup-coverage replication on
  CAND_2 / CAND_3 / 8.0 kPa~~ **DONE 2026-08-27 (Amendment #16)** — BMI-Obese under-coverage
  replicates robustly across all four constructions; Age-60+ direction robust, significance
  power-sensitive on the smaller CAND_3.
- **Transportability → ADEQUATE:** obtain and analyse any compatible independent non-NHANES
  cohort (SEPARATE WORK; currently blocked).

None of these is required for manuscript submission.
