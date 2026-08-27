# Literature review and novelty positioning

**Compiled 2026-08-27** to ground the Introduction and Discussion of `MANUSCRIPT_DRAFT.md` and to
fix the study's novelty claim to exactly what the evidence supports.

---

## 1. Search protocol

**Databases / sources queried (via web):** PubMed, Google Scholar, arXiv, IEEE Xplore / ACM
Digital Library, and the major biomedical/AI venue sites (BMJ, Lancet Digital Health, npj Digital
Medicine, JAMIA, JBI, Frontiers, BMC, NeurIPS/ICLR/ICML proceedings).

**Date range:** emphasis on 2019–2026; foundational methods papers included regardless of date.
**Date conducted:** 2026-08-27 (single pass; a formal PRISMA-style search is still advisable
before thesis submission).

**Query families (Boolean, run in several phrasings):**

1. `(liver fibrosis OR MASLD OR NAFLD) AND machine learning AND (NHANES OR "transient elastography" OR VCTE OR "routine blood")`
2. `(FIB-4 OR "NAFLD fibrosis score" OR APRI) AND (body mass index OR lean OR obese) AND (sensitivity OR diagnostic accuracy) AND (subgroup OR systematic review)`
3. `(algorithmic fairness OR bias) AND (liver disease OR hepatology) AND machine learning AND (subgroup OR false negative OR sex OR race)`
4. `class imbalance AND (clinical prediction OR risk model) AND (calibration OR recalibration OR overprediction)`
5. `conformal prediction AND (clinical OR medical OR "risk prediction") AND (coverage OR uncertainty)`
6. `conformal prediction AND (fairness OR "equalized coverage" OR "conditional coverage" OR subgroup)`
7. `(algorithmic fairness OR "subgroup net benefit") AND "clinical prediction" AND (TRIPOD OR reporting OR "decision curve")`
8. `(selective prediction OR "learning to defer" OR "reject option") AND fairness AND clinical`
9. `(large language model OR "foundation model") AND (liver fibrosis OR MASLD) AND prediction`

**Limitations of this search:** English only; no grey literature beyond preprints; paywalled
full texts were read from abstract + open-access mirrors where available; not dual-screened.

---

## 2. Findings by theme

### 2.1 Machine learning for liver fibrosis from routine data — the crowded core

| Work | Data / outcome | Method | Key result | Overlap with this study |
|---|---|---|---|---|
| **Zhou et al., *Front Med* 2026** (`10.3389/fmed.2026.1736295`) | **NHANES 2017–2020, LUXSMED > 8 kPa**, ~6,164; external validation on a Chinese hospital cohort (n≈684) | 29 models benchmarked → Gamboost; 8 routine predictors | AUC 0.824 (train) / 0.872 (internal test) / 0.848 (external); **raw Brier 0.148–0.158 corrected to 0.073 by a Bayesian prevalence prior-correction**; outperforms FIB-4/APRI/NFS | **Nearest neighbour.** Same dataset, same outcome, overlapping predictors, and **it already publishes the class-imbalance/prevalence calibration finding.** No systematic fairness audit, no conformal prediction, no mitigation. |
| ML risk stratification of MASLD using VCTE, **NHANES 2021–2023** (*BMC Gastroenterol* 2025, `10.1186/s12876-025-03850-x`) | NHANES 2021–2023, VCTE (CAP + LSM) | ML risk stratification; top-10 predictors include age, sex, race, BMI, waist circumference | Risk-stratification model; predictor list overlaps ours | Same later cycle our (now separately reported) temporal analysis used; not a fairness/uncertainty study. |
| Insulin-resistance-index ML for liver stiffness, NHANES (`PMC9537573`) | NHANES, LSM | ML + IR indices | AUC ≈ 0.74–0.8 | Same data type; aggregate metrics only. |
| Steatosis/fibrosis from clinical variables, large national survey (`PMC10232144`) | NHANES | ML | aggregate performance | Same data type; aggregate metrics only. |
| **Fibro-Predict** (*Sci Rep* 2025, `10.1038/s41598-025-17534-9`) | Israeli EHR, 5-year advanced-fibrosis trajectory | XGBoost | temporally **and** externally (prospective, with elastography) validated | Different data, outcome (trajectory), and country; **demonstrates external validation is feasible** for routine-bloods fibrosis models. |
| **LiverRisk conformal** (arXiv:2606.09860, 2026) | Guangzhou multicenter NAFLD cohort (n=2,187 + 412 external) | Gradient boosting **+ split conformal** | AUROC 0.912 / 0.891; conformal marginal coverage 91.3% at 90% nominal; **"coverage at or above nominal in all subgroups examined"** | Different cohort and outcome (NAFLD, not VCTE-fibrosis); **reports the opposite of our subgroup finding** (no subgroup under-coverage), on non-NHANES data. |
| **CDSS for hepatic fibrosis in general practice** (*ACM TCH* 2025, `10.1145/3788673`) | Australian general-practice EHR, 15 yr, HSI/FIB-4-derived labels | ML CDSS | stratified fairness analysis by **age and gender** | EHR (not VCTE); label is a score, not elastography; fairness axis is age/sex, not BMI; no conformal. |
| **LLM proof-of-concept** (`PMC12955738`, 2026); LLM + tabular-foundation-model benchmark (arXiv:2605.20523, 2026); LLMs on MASLD narratives (arXiv:2512.11544) | routine variables / clinical text | GPT-4, GPT-3.5, TabPFN-class models | comparable to FIB-4 in proof-of-concept | LLM/foundation-model prediction of fibrosis is **already an active, published direction.** |

### 2.2 Non-invasive fibrosis scores by BMI — the clinical baseline for our body-mass finding

- **FIB-4 and NFS "fail" at BMI extremes** — Eyraud et al. / "Accuracy of FIB-4 and NFS in MAFLD according to BMI: failure in the prediction of advanced fibrosis in lean and morbidly obese individuals" (*Eur J Gastroenterol Hepatol* 2020, PubMed 32976186).
- **NFS sensitivity is specifically low in lean patients** — 54.4% vs FIB-4's 81.8% at the standard cut-points in lean NAFLD (*PMC10436134* / PubMed 37589973; HCPLive summary). FIB-4 sensitivity is roughly BMI-invariant.
- **Non-invasive scores in NAFLD with/without morbid obesity** — *Int J Obes* 2021 (`10.1038/s41366-021-00881-8`).
- **Low accuracy of FIB-4/NFS for population-level screening** — Graupera et al. (*Clin Gastroenterol Hepatol* 2021, ScienceDirect S1542356521013586).
- **Diabetes and obesity reduce FIB-4 accuracy in MASLD referral pathways** — *JHEP Reports* 2026 (`S2589-5559(26)00005-4`).
- **Two-step FIB-4 → VCTE/ELF referral pathways** are standard of care and cut unnecessary referrals ~80% — *J Hepatol* 2019 (`S0168-8278(19)30227-2`); *Sci Rep* 2024 (`10.1038/s41598-024-62549-3`); "FIB-4 first" (`PMC6771169`); 3-step approach (`PMC9616882`).

**Implication:** the direction of our BMI finding (worse detection in normal-weight than obese)
is *consistent with* the known NFS limitation — NFS-type models encode BMI/diabetes as positive
predictors, so a lean case with fibrosis is scored low. A reviewer will raise this. We must cite
it and frame our contribution as: the pattern persists in modern multi-model ML on population
VCTE data where BMI is one of ten features and race is excluded, and it co-occurs with a conformal
coverage failure.

### 2.3 Class-imbalance correction miscalibrates — the citation for our calibration result

- **van den Goorbergh, van Smeden, Timmerman, Van Calster.** "The harm of class imbalance
  corrections for risk prediction models: illustration and simulation using logistic regression."
  *JAMIA* 2022;29(9):1525–1534 (`10.1093/jamia/ocac093`). **All imbalance corrections →
  overestimation of minority-class probability and poor calibration, no discrimination gain; the
  same sensitivity/specificity is obtained by simply shifting the threshold.**
- **Carriero et al.** "The Harms of Class Imbalance Corrections for Machine-Learning-Based
  Prediction Models: A Simulation Study." *Statistics in Medicine* 2025 (`10.1002/sim.10320`).
- "Class imbalance correction in AI models leads to miscalibrated clinical predictions: a
  real-world evaluation." medRxiv 2026.
- Resampling-for-imbalance scoping review — *PLoS One* 2025 (`PMC12582444`).

**Implication:** our calibration finding is a **replication**, not a discovery. The class-weight /
`scale_pos_weight` shift we observe (OOF intercepts −2.24 to −2.05, matching
`log(0.0931/0.9069) ≈ −2.27`) is exactly the van den Goorbergh mechanism, and the OOF-Platt fix is
their recommended remedy. Cite it; do not claim novelty here.

### 2.4 Conformal prediction in clinical AI — framing for the uncertainty section

- **"Conformal Prediction in Clinical Artificial Intelligence."** *CHEST* 2025 (review).
- Angelopoulos & Bates. "A Gentle Introduction to Conformal Prediction and Distribution-Free
  Uncertainty Quantification" (tutorial).
- Vovk, Gammerman, Shafer. *Algorithmic Learning in a Random World* (foundational).
- Angelopoulos, Bates, Fisch, Lei, Schuster. "Conformal Risk Control." *ICLR* 2024.
- Clinical examples: two-stage conformal for Parkinson's medication needs (arXiv:2508.10284);
  conformal risk control for radiotherapy QA (arXiv:2501.08963).

### 2.5 Marginal vs conditional/subgroup coverage — our core methodological point is established

- **Barber, Candès, Ramdas, Tibshirani.** "The limits of distribution-free conditional predictive
  inference." *Information and Inference* 2021 (arXiv:1903.04684). **Exact conditional coverage is
  impossible distribution-free** — subgroup deviations from marginal coverage are expected.
- **Romano, Barber, Sabbatti, Candès.** "With malice toward none: Assessing uncertainty via
  equalized coverage." *Harvard Data Science Review* 2020. The classic group-balanced conformal
  method (our Mondrian analysis is in this family).
- **"Conformal Prediction Sets Can Cause Disparate Impact."** *ICLR* 2025 — enforcing equalized
  coverage can *increase* downstream decision unfairness.
- **"Conformal Classification with Equalized Coverage for Adaptively Selected Groups."** *NeurIPS*
  2024.
- **Zhou & Sesia.** Adaptively Fair Conformal Prediction (AFCP), 2024 — our exploratory faithful-AFCP
  arm.
- "A Generic Framework for Conformal Fairness" (2025); "Conditional Coverage Diagnostics for
  Conformal Prediction" (2025).

**Implication:** "marginal coverage does not imply subgroup coverage" is a **known theoretical
result**, not our finding. Our contribution is the **empirical demonstration on this clinical
task** — which specific subgroups fail, that it is triangulated across cohort constructions, and
that no tested mitigation is acceptable + generalisable.

### 2.6 Fairness of clinical prediction models — evaluation and reporting

- **Collins et al.** "TRIPOD+AI statement." *BMJ* 2024 (PubMed 38626948) — subgroup performance
  reporting with CIs is now an expected item.
- **"Understanding algorithmic fairness for clinical prediction in terms of subgroup net benefit
  and health equity."** arXiv:2412.07879 (Cambridge / THIS Institute, Dec 2024) — decision-curve
  net benefit adapted to subgroups; maximin-subgroup-NB Pareto front; warns against "levelling
  down."
- **"Critical appraisal of fairness metrics for AI-based clinical prediction models: a scoping
  review."** *Lancet Digit Health* family, 2026 (ScienceDirect S2589750026000245).
- Pfohl et al. "Net benefit, calibration, threshold selection, and training objectives for
  algorithmic fairness in healthcare."
- **Straw & Wu.** "Investigating for bias in healthcare algorithms: a sex-stratified analysis of
  supervised ML models in liver disease prediction." *BMJ Health Care Inform* 2022 (`PMC9039354`)
  — RF / LR false-negative-rate disparity of −21% / −24% for female patients on the ILPD dataset.
  **The closest fairness-audit analog** — but sex only, ILPD (not NHANES), no calibration/conformal.

### 2.7 Selective prediction / learning to defer + fairness — for the future-work section

- **"Conformal selective prediction with cost-aware deferral for safe clinical triage under
  distribution shift."** *Sci Rep* 2026 (`10.1038/s41598-026-40637-w`) — calibrated probs +
  conformal + cost-aware deferral + group-conditional Mondrian + shift-robust conformal; reports
  near-nominal validity across age and BMI strata on sepsis.
- **Jones et al.** "Selective Classification Can Magnify Disparities Across Groups." *ICLR* 2021 —
  abstention can *widen* subgroup gaps.
- **Schreuder & Chzhen.** "Classification with abstention but without disparities." *UAI* 2021.
- **Madras, Pitassi, Zemel.** "Predict Responsibly: Improving Fairness and Accuracy by Learning to
  Defer." *NeurIPS* 2018.
- Mozannar & Sontag. "Consistent Estimators for Learning to Defer to an Expert." *ICML* 2020.
- "Achieving Fairness Without Harm via Selective Demographic Experts" (2025).

---

## 3. Positioning — Already done / Related but different / Distinctive

### Already published (claim as replication or background, NOT novelty)

1. NHANES routine-data ML for VCTE-defined significant fibrosis, AUROC ≈ 0.82–0.87, with FIB-4/APRI/NFS comparison (Zhou 2026; others).
2. Class-imbalance correction → probability over-estimation, fixed by post-hoc recalibration (van den Goorbergh 2022; Carriero 2025) — **also already shown on this exact dataset/outcome** (Zhou 2026).
3. Split conformal prediction applied to liver-disease risk (LiverRisk, 2026).
4. "Marginal coverage ≠ conditional/subgroup coverage" as a theoretical fact (Barber et al. 2021) and the disparate-impact risk of equalizing it (ICLR 2025).
5. BMI-dependent performance of non-invasive fibrosis assessment; lean under-detection by NFS-type models.
6. Fairness auditing of liver-disease ML (Straw & Wu 2022, for sex).

### Related but different (cite, distinguish)

- LiverRisk conformal — different cohort/outcome, and finds *no* subgroup coverage failure.
- Fibro-Predict — EHR, trajectory outcome, externally validated; shows the external-validation path.
- AFCP / equalized-coverage / net-benefit-fairness — method papers, not applied to this task.
- Conformal selective deferral for triage (Sci Rep 2026) — same method stack, different disease, and it *achieves* near-nominal subgroup validity.

### Distinctive to this study (supported by the evidence)

1. **A single pre-registered, hash-frozen protocol that holds discrimination, aggregate
   calibration, a multi-axis subgroup fairness audit (sex, race, age band, BMI band), split-conformal
   *subgroup* coverage, and a structured multi-strategy mitigation battery to the same standard**,
   on one NHANES VCTE-fibrosis cohort. No single prior paper combines all of these for this task.
2. **The specific empirical result** that split-conformal *subgroup* coverage fails for BMI-obese
   (76.8–82.3%) and age-60+ (81.1–85.6%) while marginal coverage holds and normal-weight/younger
   participants over-cover — on NHANES routine-data fibrosis models — **triangulated across three
   independently constructed cohorts and an alternative outcome threshold.** (LiverRisk reports the
   opposite on a different cohort; no one has shown it on this task.)
3. **The negative mitigation result**: seven threshold-/calibration-/conformal-based strategies,
   each failing a pre-specified multi-metric acceptance gate for this specific reliability–fairness
   failure. Negative, but not previously reported for this problem.
4. **The rigor and transparency itself** (frozen protocol, hash lineage, OOF-only calibration,
   contamination audits, project-wide FDR) — above the norm for NHANES-fibrosis ML.

### The honest one-sentence novelty claim

> A pre-registered, triangulated reliability audit showing that, on the standard NHANES
> routine-data fibrosis task — where discrimination and (per prior work) prevalence-corrected
> calibration are already adequate — split-conformal reliability still fails for identifiable
> demographic subgroups (obese and older patients; normal-weight patients for detection) in a way
> that resists a structured battery of mitigations.

Do **not** claim: first fairness study in liver AI; first to study calibration or uncertainty in
fibrosis prediction; a novel calibration finding; a novel conformal method; any external
validation.

---

## 4. Reference list (for the manuscript — verify each before submission)

Clinical / prediction-model:

1. Zhou et al. Integrative and interpretable machine learning framework for early non-invasive detection of clinically significant liver fibrosis. *Front Med* 2026. doi:10.3389/fmed.2026.1736295
2. Machine learning-based risk stratification of MASLD using VCTE: NHANES 2021–2023. *BMC Gastroenterol* 2025. doi:10.1186/s12876-025-03850-x
3. Fibro-Predict: a machine learning risk score for advanced liver fibrosis in the general population using Israeli EHRs. *Sci Rep* 2025. doi:10.1038/s41598-025-17534-9
4. Eyraud et al. Accuracy of FIB-4 and NFS in MAFLD according to BMI: failure in lean and morbidly obese individuals. *Eur J Gastroenterol Hepatol* 2020. PMID:32976186
5. Diagnostic performance of FIB-4 and NFS in lean adults with NAFLD. 2023. PMID:37589973 / PMC10436134
6. Graupera et al. Low accuracy of FIB-4 and NAFLD Fibrosis Scores for screening for liver fibrosis in the population. *Clin Gastroenterol Hepatol* 2021.
7. Diabetes and obesity reduce FIB-4 accuracy in MASLD referral pathways. *JHEP Rep* 2026.
8. Srivastava et al. Prospective evaluation of a primary-care referral pathway for NAFLD. *J Hepatol* 2019.
9. Collins et al. TRIPOD+AI statement. *BMJ* 2024. PMID:38626948

Fairness / calibration / methods:

10. van den Goorbergh et al. The harm of class imbalance corrections for risk prediction models. *JAMIA* 2022;29(9):1525–34. doi:10.1093/jamia/ocac093
11. Carriero et al. The harms of class imbalance corrections for machine-learning-based prediction models: a simulation study. *Stat Med* 2025. doi:10.1002/sim.10320
12. Straw & Wu. Investigating for bias in healthcare algorithms: a sex-stratified analysis of ML models in liver disease prediction. *BMJ Health Care Inform* 2022. PMC9039354
13. Understanding algorithmic fairness for clinical prediction in terms of subgroup net benefit and health equity. arXiv:2412.07879, 2024.
14. Critical appraisal of fairness metrics for AI-based clinical prediction models: a scoping review. *Lancet Digit Health* 2026.

Conformal prediction:

15. Vovk, Gammerman, Shafer. *Algorithmic Learning in a Random World*. Springer, 2005.
16. Angelopoulos & Bates. A gentle introduction to conformal prediction and distribution-free uncertainty quantification. 2021/2023.
17. Barber, Candès, Ramdas, Tibshirani. The limits of distribution-free conditional predictive inference. *Inf Inference* 2021. arXiv:1903.04684
18. Romano, Barber, Sabbatti, Candès. With malice toward none: assessing uncertainty via equalized coverage. *Harv Data Sci Rev* 2020.
19. Angelopoulos et al. Conformal risk control. *ICLR* 2024.
20. Conformal prediction in clinical artificial intelligence. *CHEST* 2025.
21. Conformal prediction sets can cause disparate impact. *ICLR* 2025.
22. Conformal classification with equalized coverage for adaptively selected groups. *NeurIPS* 2024.
23. Zhou & Sesia. Adaptively fair conformal prediction (AFCP). 2024.
24. Conformal risk prediction for NAFLD using gradient boosting with distribution-free coverages (LiverRisk). arXiv:2606.09860, 2026.

Selective prediction / deferral (future work):

25. Jones et al. Selective classification can magnify disparities across groups. *ICLR* 2021.
26. Schreuder & Chzhen. Classification with abstention but without disparities. *UAI* 2021.
27. Madras, Pitassi, Zemel. Predict responsibly: improving fairness and accuracy by learning to defer. *NeurIPS* 2018.
28. Conformal selective prediction with cost-aware deferral for safe clinical triage under distribution shift. *Sci Rep* 2026. doi:10.1038/s41598-026-40637-w

**Before submission:** run a proper PubMed + IEEE/ACM + arXiv systematic search with dual
screening, verify every DOI/PMID above, and add any 2026 work that appears in the interim.
