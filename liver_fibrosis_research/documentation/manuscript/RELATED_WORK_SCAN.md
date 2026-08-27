# Related-work scan — comprehensive catalogue

**Compiled 2026-08-27 by web search** (PubMed/PMC, Google Scholar, arXiv, journal sites; ~30
queries across every dimension of the study). This is an exhaustive *scan*, **not** a PRISMA
systematic review — web search is US-indexed, returns titles/abstracts not full database records,
and was single-screened. Treat it as the starting bibliography; a formal search is still required
before submission (see `LITERATURE_REVIEW.md` §4–5 for the positioning and venue call).

Every entry states **what the paper actually did** (from its abstract / accessible text) and a
**relevance tag**:
`DIRECT` (same problem/data) · `CLOSE` (same task, different data) · `BACKGROUND` (clinical
context) · `METHODS` (a method you use) · `ADJACENT` (nearby, different) · `FRAMING` (reporting /
trustworthy-AI).

Where a DOI/PMID is shown it was seen in a search result; **all identifiers still need
verification**. "not verified" = the work exists but I could not pin the identifier here.

---

## A. NHANES + VCTE + machine learning for liver fibrosis / steatosis — DIRECT

| # | Work | What it did | Tag |
|---|---|---|---|
| A1 | **Cao et al. Integrative and interpretable ML framework for early non-invasive detection of clinically significant liver fibrosis. *Front Med* 2026.** doi:10.3389/fmed.2026.1736295 | **NHANES 2017–2020, LUXSMED > 8 kPa**, N≈6,164; 8 routine predictors; 29 models benchmarked → Gamboost. AUC 0.824 train / 0.872 internal test / 0.848 external (Chinese hospital cohort n≈684). **Raw Brier 0.148–0.158 → 0.073 after a Bayesian prevalence prior-correction.** Beats FIB-4/APRI/NFS. No fairness audit, no conformal, no mitigation. | **DIRECT — nearest neighbour; publishes your calibration finding on your exact data/outcome.** |
| A2 | ML-based risk stratification & prediction of MASLD using VCTE: **NHANES 2021–2023**. *BMC Gastroenterol* 2025. doi:10.1186/s12876-025-03850-x | NHANES 2021–2023, VCTE (CAP + LSM); LASSO + random-forest feature selection; top-10 predictors include age, sex, race, BMI, waist circumference, HbA1c, lymphocytes, education. Risk-stratification model. | DIRECT — same later cycle your (separately reported) temporal analysis used. |
| A3 | ML models including insulin-resistance indexes for predicting liver stiffness in the US population: data from NHANES. *PMC9537573*. | NHANES; XGBoost etc. predict LSM from demographics + blood + IR indices; RF feature selection best (~86% accuracy). | DIRECT — aggregate metrics only. |
| A4 | Liu L, Lin J, et al. **Automated machine learning models for NAFLD assessed by controlled attenuation parameter from NHANES 2017–2020.** *Digit Health* 2024. doi:10.1177/20552076241272535 | NHANES 2017–2020; **7 ML methods — XGBoost, LightGBM, MLP, Random Forest, SVM, KNN, logistic regression** (the same family you use); outcome is CAP-defined steatosis (not fibrosis). AutoML. | DIRECT (data + model set) — but steatosis outcome, not fibrosis. |
| A5 | Huang et al. Visualization of covariance importance in a machine-learning model for **advanced liver fibrosis** in a nationally representative sample. *JGH Open* 2025. doi:10.1002/jgh3.70200 | NHANES; ML for advanced fibrosis; SHAP-style importance. | DIRECT — advanced-fibrosis outcome. |
| A6 | **ML-based prediction of MASLD using NHANES data.** *PLoS One* (2025/26). e.g. `10.1371/journal.pone.0335656` and `10.1371/journal.pone.0319851` ("…including NHHR"). | NHANES; ML for MASLD presence; LASSO/Boruta feature selection; interpretable models. | CLOSE — MASLD (steatosis) outcome, not fibrosis. |
| A7 | **ML-based biomarker identification for early diagnosis of MASLD.** *J Clin Endocrinol Metab* 2025;110(11):e3866. PMID 39980343 | NHANES-based; ML biomarker panel for early MASLD. | CLOSE — MASLD, not fibrosis. |
| A8 | ML prediction of MAFLD risk in American adults using **body composition**; explainable SHAP analysis. *Front Nutr* 2025. doi:10.3389/fnut.2025.1616229 | NHANES; body-composition predictors; SHAP. | ADJACENT. |
| A9 | Association of waist-to-height ratio with NAFLD and fibrosis by VCTE: **NHANES 2017–2020**. *PMC12778146*. | NHANES 2017–2020 VCTE; epidemiological association (not an ML model). | BACKGROUND. |
| A10 | Prevalence of MASLD and fibrosis by transient elastography in **US adolescents**, NHANES 2017–2023. *PMC12751582*. | NHANES adolescents; prevalence. | BACKGROUND (your study is adult-only; relevant to the deferred CAND_4). |

## B. ML for liver fibrosis from routine / blood data — non-NHANES — CLOSE

| # | Work | What it did | Tag |
|---|---|---|---|
| B1 | **Fibro-Predict: an ML risk score for advanced liver fibrosis in the general population using Israeli EHRs.** *Sci Rep* 2025. doi:10.1038/s41598-025-17534-9 (PMC12399762) | Nationwide Israeli EHR; XGBoost predicting 5-year advanced-fibrosis diagnosis from routine blood tests; **validated temporally *and* externally (prospective, with elastography).** | CLOSE — shows external validation is feasible for routine-bloods fibrosis models. |
| B2 | **Development and validation of an ensemble ML framework for detection of all-cause advanced hepatic fibrosis: a retrospective cohort study.** *Lancet Digit Health* 2021. PIIS2589-7500(21)00270-3 | Large retrospective cohort; ensemble ML; **superior to APRI, FIB-4, NFS with no indeterminate classifications**, comparable to an expert panel. | CLOSE — the prominent "ML beats the serum scores" paper. |
| B3 | New non-invasive tests **FIB-9 / FIB-11 / FIB-12** by multi-targeted ML. *J Hepatol* 2024. S0168-8278(24)02753-3 | Multi-targeted ML method; FIB-9 (9 common markers), FIB-11 (+2 specialised), FIB-12 (+LSM); FIB-12 best. | CLOSE. |
| B4 | Development and validation of an ML-based model for prediction of liver fibrosis and MASH. PMID 40299904 | ML for fibrosis + MASH from clinical/epidemiological data. | CLOSE. |
| B5 | ML models for predicting **significant liver fibrosis in patients with severe obesity and NAFLD.** ResearchGate 385246560 (2024). | Bariatric/severe-obesity cohort; ML for significant fibrosis. | CLOSE — the obese end of the BMI spectrum. |
| B6 | Interpretable ML model for significant liver fibrosis in comorbid **chronic hepatitis B + NAFLD.** *BMC Gastroenterol* 2025. doi:10.1186/s12876-025-04594-4 | Retrospective dev+validation; interpretable ML; significant fibrosis. | ADJACENT (CHB+NAFLD population). |
| B7 | ML risk score for advanced liver fibrosis in a **Chinese T2DM population** (lean NAFLD). PMC12289481. | Interpretable ML; RF best; AUC 0.739 train / 0.789 internal validation; lean NAFLD in T2DM. | ADJACENT — lean-NAFLD focus. |
| B8 | ALADDIN study — ML web calculator for **moderate fibrosis** using routine labs ± VCTE. | ML calculator; routine parameters with/without VCTE. | CLOSE. |
| B9 | Comparison of ML models and the Fatty Liver Index in predicting **lean fatty liver.** *Diagnostics* 2023. doi:10.3390/diagnostics13081407 (PMC10137474) | Builds ML models specifically for the lean population to predict steatosis. | ADJACENT — lean, steatosis. |
| B10 | LASSO-derived model for prediction of **lean-NAFLD** in routine health check-ups. PMC10878349. | LASSO logistic model; lean NAFLD; steatosis outcome. | ADJACENT. |
| B11 | **Commercial ML NITs:** LiverPRO (Evido/Echosens, Denmark), LIVERFASt (Fibronostics, US), LiverAdvisor/LiverRisk-type tools. | Marketed routine-biomarker fibrosis/inflammation predictors. | BACKGROUND — the commercial landscape. |

## C. Non-invasive serum scores (FIB-4 / NFS / APRI) — accuracy and BMI/subgroup behaviour — BACKGROUND for the body-mass finding

| # | Work | What it did | Tag |
|---|---|---|---|
| C1 | Eyraud et al. Accuracy of FIB-4 and NFS in MAFLD **according to BMI: failure in lean and morbidly obese individuals.** *Eur J Gastroenterol Hepatol* 2020. PMID 32976186 | Both FIB-4 and NFS fail to discriminate advanced fibrosis at the BMI extremes; NFS especially weak in lean. | **BACKGROUND — the closest clinical analog of your BMI finding.** |
| C2 | Diagnostic performance of FIB-4 and NFS in **lean adults with NAFLD.** 2023. PMID 37589973 (PMC10436134) | NFS sensitivity ≈ 54% vs FIB-4 ≈ 82% at standard cut-points in lean NAFLD; FIB-4 roughly BMI-invariant. | BACKGROUND. |
| C3 | Graupera et al. **Low accuracy of FIB-4 and NAFLD Fibrosis Scores for screening for liver fibrosis in the population.** *Clin Gastroenterol Hepatol* 2021. S1542356521013586 | Population-based screening; both scores have low accuracy at the general-population level. | BACKGROUND. |
| C4 | Performance of non-invasive fibrosis scores in NAFLD **with and without morbid obesity.** *Int J Obes* 2021. doi:10.1038/s41366-021-00881-8 | Scores by obesity status; NFS overestimates in morbid obesity. | BACKGROUND. |
| C5 | **Diabetes and obesity reduce FIB-4 accuracy in MASLD referral pathways.** *JHEP Rep* 2026. S2589-5559(26)00005-4 | Modern referral-pathway data; diabetes and obesity degrade FIB-4 performance. | BACKGROUND. |
| C6 | Lee J, et al. Prognostic accuracy of FIB-4, NFS and APRI for NAFLD-related events: a **systematic review.** *Liver Int* 2021. doi:10.1111/liv.14669 (PMC7898346) | Systematic review; AUCs 0.69–0.92 for events; FIB-4/NFS > APRI for mortality; inconsistent for fibrosis-stage change. | BACKGROUND. |
| C7 | Srivastava et al. Prospective evaluation of a **primary-care referral pathway** for NAFLD. *J Hepatol* 2019. doi:10.1016/j.jhep.2019.03.033 | Two-step FIB-4 → ELF pathway; ~80% fewer unnecessary referrals; 5× more advanced-fibrosis cases detected. | BACKGROUND — the clinical workflow your model would feed. |
| C8 | Automatically-calculated **FIB-4 first, then ELF** to screen primary-care patients. *Sci Rep* 2024. doi:10.1038/s41598-024-62549-3 | Sequential two-step screening in primary care. | BACKGROUND. |
| C9 | "FIB-4 First" strategy on a NAFLD referral pathway. PMC6771169. | Implementation study of FIB-4-first triage. | BACKGROUND. |
| C10 | 3-step approach to predict advanced fibrosis in NAFLD: impact on diagnosis, burden, cost. PMC9616882. | Sequential 3-step non-invasive strategy. | BACKGROUND. |

## D. VCTE / FibroScan measurement properties and BMI — BACKGROUND (a measurement-bias caveat for your outcome)

| # | Work | What it did | Tag |
|---|---|---|---|
| D1 | Wong VW-S, et al. FibroScan (VCTE): where does it stand in US practice. *Clin Gastroenterol Hepatol* 2015. S1542-3565(14)00818-0 | Review; **BMI negatively affects TE — obesity produces falsely increased LSM; standard M probe unreliable at BMI ≥ 28**; XL-probe failure 1.1% vs M-probe 16% at BMI > 28. | **BACKGROUND — important: VCTE may over-read stiffness in obese participants, which could bias the "obese" outcome labels upward and partly explain higher model sensitivity there. Discuss in Limitations.** |
| D2 | MR elastography vs VCTE for hepatic fibrosis in **severe to morbid obesity.** *Radiology* 2017. PMID 27861111 (PMC5395333) | Head-to-head in severe obesity; MRE greater success rate than VCTE; both perform well when successful. | BACKGROUND. |
| D3 | Utility and diagnostic accuracy of transient elastography in adults with **morbid obesity**: a prospective study. PMC8911197. | VCTE accuracy specifically in morbid obesity. | BACKGROUND. |
| D4 | Skin-capsular distance (SCD) affects LSM accuracy in obesity **more than BMI itself.** (obesity-VCTE literature) | SCD is the dominant confounder of LSM in obese patients. | BACKGROUND. |

## E. NHANES fibrosis / steatosis epidemiology — BACKGROUND (prevalence anchors)

| # | Work | What it did | Tag |
|---|---|---|---|
| E1 | Kardashian A, et al. Prevalence of fatty liver disease and fibrosis by transient elastography in US adults, **2017–2018.** *Clin Gastroenterol Hepatol* 2021. PMID 32801011 | NHANES 2017–2018; national prevalence of steatosis and fibrosis by VCTE. | BACKGROUND. |
| E2 | **Prepandemic prevalence estimates of fatty liver disease and fibrosis defined by liver elastography in the US** (NHANES 2017–March 2020). *Dig Dis Sci* 2022. doi:10.1007/s10620-022-07707-1 (medRxiv 2022.04.05.22273458) | NHANES 2017–March 2020 — the exact cycle you use; weighted prevalence estimates of steatosis and fibrosis. | **BACKGROUND — your prevalence citation.** |

## F. Fairness / bias in liver-disease and related clinical ML — DIRECT (the fairness angle)

| # | Work | What it did | Tag |
|---|---|---|---|
| F1 | **Straw I, Wu H. Investigating for bias in healthcare algorithms: a sex-stratified analysis of supervised ML models in liver disease prediction.** *BMJ Health Care Inform* 2022;29(1):e100457. doi:10.1136/bmjhci-2021-100457 | ILPD dataset; RF and LR classifiers under-perform for women; **false-negative-rate disparity up to −21% (RF) / −24% (LR)**; argues for sex-stratified modelling. | **DIRECT — the closest fairness-audit analog (sex, ILPD, no calibration/conformal).** |
| F2 | AI predicts **sex-specific risk of MASLD.** *Biol Sex Differ* 2026. doi:10.1186/s13293-026-00917-6 | ML for MASLD with explicit sex-specific modelling; metabolic traits stronger in women, hepatic/lipid markers in men; argues for sex-specific data processing. | DIRECT — fairness-adjacent MASLD ML. |
| F3 | Assessing fairness in ML models: racial bias using **matched counterparts** in mortality prediction for chronic-disease patients (incl. **chronic liver disease** 1-year mortality). *J Biomed Inform* 2024. S1532046424000959 (PMC11272432) | Separate models per outcome; compares performance Black vs White; matched-counterpart design. | CLOSE — liver-disease mortality, not fibrosis. |
| F4 | Sex and gender differences in MASLD: pathophysiology, clinical implications. *Metab Target Organ Damage* 2025. | Narrative review of sex/gender in MASLD. | BACKGROUND. |
| F5 | **FairLogue: a toolkit for intersectional fairness analysis in clinical ML models.** arXiv:2604.04858 (2026). | Tooling for intersectional subgroup fairness auditing. | METHODS. |
| F6 | Integrating group and individual fairness in clinical AI: a post-hoc, model-agnostic **fairness-auditing framework.** medRxiv 2025.09.03.25334999. | Post-hoc model-agnostic fairness audit combining group + individual fairness. | METHODS. |

## G. Fairness of clinical prediction models — methods and frameworks — METHODS

| # | Work | What it did | Tag |
|---|---|---|---|
| G1 | **Pfohl SR, et al. An empirical characterization of fair machine learning for clinical risk prediction.** *J Biomed Inform* 2021. arXiv:2007.10306, PMID 33220494 | Empirical study of fairness constraints vs performance across clinical prediction tasks; group-calibration tension. | **METHODS — a core reference for framing subgroup fairness of risk models.** |
| G2 | **Understanding algorithmic fairness for clinical prediction in terms of subgroup net benefit and health equity.** arXiv:2412.07879 (Cambridge / THIS Institute, Dec 2024). | Adapts decision-curve net benefit to subgroups; maximin-subgroup-NB Pareto front; warns against "levelling down". | **METHODS — the fairness criterion to use instead of coverage/error parity.** |
| G3 | **Critical appraisal of fairness metrics for AI-based clinical prediction models: a scoping review.** *Lancet Digit Health* 2026. S2589750026000245 (arXiv:2506.17035). | Scoping review of fairness metrics in clinical prediction AI; gaps in UQ, intersectionality, real-world applicability. | METHODS / FRAMING. |
| G4 | Pfohl SR, et al. Net benefit, calibration, threshold selection, and training objectives for algorithmic fairness in healthcare. *ACM FAccT* 2022. | Decision-analytic view of fairness; threshold + calibration + net benefit. | METHODS. |
| G5 | **"Is this model reliable for everyone? Testing for strong calibration."** arXiv:2307.15247. | Statistical test for strong (subgroup-conditional) calibration. | METHODS — for the subgroup-calibration claim. |
| G6 | Improving calibration and subgroup equity in diabetes readmission prediction via **causal reweighting** of LSTM models. *J Biomed Inform* 2026. S235291482600050X. | In-processing reweighting to jointly improve calibration + subgroup equity. | METHODS — a mitigation approach. |
| G7 | Evaluating the impact of data biases on algorithmic fairness and clinical utility of ML models for prolonged opioid-use prediction. *JAMIA Open* 2025. ooaf115. | Data-bias → fairness/utility effects in a clinical prediction model. | METHODS. |
| G8 | **Yang J, et al. Algorithmic fairness and bias mitigation for clinical machine learning with deep reinforcement learning.** *Nat Mach Intell* 2023. doi:10.1038/s42256-023-00697-3 (PMC10442224) | RL-based in-processing bias mitigation for clinical ML. | METHODS. |
| G9 | Evaluating algorithmic fairness in the presence of **clinical guidelines**: ASCVD risk estimation. medRxiv 2021.11.08.21266076. | Fairness assessment anchored to a guideline threshold. | METHODS. |
| G10 | Stability of clinical prediction models developed using statistical or ML methods. PMC10952221. | Model-stability / instability across resamples. | METHODS (relates to your single-split limitation). |

## H. Calibration and class imbalance in clinical ML — METHODS (your calibration finding)

| # | Work | What it did | Tag |
|---|---|---|---|
| H1 | **van den Goorbergh R, van Smeden M, Timmerman D, Van Calster B. The harm of class imbalance corrections for risk prediction models: illustration and simulation using logistic regression.** *JAMIA* 2022;29(9):1525–1534. doi:10.1093/jamia/ocac093 (arXiv:2202.09101) | Simulation + illustration: **all imbalance corrections (undersampling, oversampling, SMOTE) → overestimated minority-class probability and poor calibration, no discrimination gain; the same sensitivity/specificity comes from just shifting the threshold.** | **METHODS — the citation that makes your calibration result a replication.** |
| H2 | **Carriero A, et al. The harms of class imbalance corrections for ML-based prediction models: a simulation study.** *Stat Med* 2025. doi:10.1002/sim.10320 | Broader-scope simulation confirming H1 across ML methods. | METHODS. |
| H3 | Class imbalance correction in AI models leads to **miscalibrated clinical predictions: a real-world evaluation.** medRxiv 2026. | Real-world (not simulation) demonstration of imbalance-correction miscalibration. | METHODS — directly parallels your empirical result. |
| H4 | Resampling methods for class imbalance in clinical prediction models: a scoping review protocol. *PLoS One* 2025. PMC12582444. | Scoping-review protocol of resampling practice. | METHODS. |

## I. Conformal prediction — foundational and clinical — METHODS (your uncertainty layer)

| # | Work | What it did | Tag |
|---|---|---|---|
| I1 | Vovk V, Gammerman A, Shafer G. *Algorithmic Learning in a Random World.* Springer, 2005 (2nd ed. 2022). | The foundational text on conformal prediction. | METHODS. |
| I2 | Angelopoulos AN, Bates S. A gentle introduction to conformal prediction and distribution-free uncertainty quantification. 2021/2023. | The standard tutorial; split conformal, coverage guarantee. | METHODS. |
| I3 | **Angelopoulos AN, Bates S, Fisch A, Lei L, Schuster T. Conformal risk control.** *ICLR* 2024. (arXiv:2208.02814) | Generalises split conformal to control the expectation of any monotone loss. | METHODS. |
| I4 | **"Conformal prediction in clinical artificial intelligence."** *CHEST* 2025 (article S0012-3692(25)05184-0). | Clinical-audience review of conformal prediction for clinical AI. | METHODS / FRAMING — a clinical citation for the method. |
| I5 | Trustworthy clinical AI: a unified review of **uncertainty quantification** in DL for medical image analysis. *Artif Intell Med* 2024. doi:10.1016/j.artmed.2024.102830 (arXiv:2210.03736), PMID 38553168 | Review of UQ methods (Bayesian, ensembles, MC-dropout, conformal) in clinical DL. | METHODS / FRAMING. |
| I6 | Uncertainty quantification for machine learning in healthcare: a survey. arXiv:2505.02874 (2025). | Broad UQ-for-healthcare survey. | FRAMING. |
| I7 | "Clinical AI tools must convey predictive uncertainty for each individual patient." *Nat Med* 2023. doi:10.1038/s41591-023-02562-7 | Opinion: individual-level uncertainty is a clinical requirement. | FRAMING. |
| I8 | Two-stage conformal prediction for **Parkinson's** medication needs. arXiv:2508.10284. | Clinical conformal example. | ADJACENT. |
| I9 | Development and validation of an interpretable conformal predictor for **sepsis mortality risk.** *JMIR* 2024;26:e50369. | Clinical conformal risk model. | ADJACENT. |

## J. Conformal prediction fairness / conditional (subgroup) coverage — METHODS (your central methodological point)

| # | Work | What it did | Tag |
|---|---|---|---|
| J1 | **Barber RF, Candès EJ, Ramdas A, Tibshirani RJ. The limits of distribution-free conditional predictive inference.** *Inf Inference* 2021. arXiv:1903.04684 | **Proves exact conditional (subgroup) coverage is impossible distribution-free** — subgroup deviations from marginal coverage are expected. | **METHODS — the theoretical basis of your finding.** |
| J2 | **Romano Y, Barber RF, Sabatti C, Candès EJ. With malice toward none: assessing uncertainty via equalized coverage.** *Harv Data Sci Rev* 2020. | The classic group-balanced (equalized) conformal method — your Mondrian arm is in this family. | METHODS. |
| J3 | **"Conformal prediction sets can cause disparate impact."** *ICLR* 2025 (Cresswell et al.). OpenReview fZK6AQXlUU | Human-subject study: **enforcing equalized coverage can *increase* downstream decision unfairness**, more than marginal coverage does. | **METHODS — why you should not just "equalize coverage".** |
| J4 | "Conformal classification with **equalized coverage for adaptively selected groups**." *NeurIPS* 2024. arXiv:2405.15106 | Group-conditional coverage for adaptively selected subgroups; scaling issues with many attributes. | METHODS. |
| J5 | **Zhou & Sesia. Adaptively fair conformal prediction (AFCP).** 2024. | Adaptively identifies disadvantaged subgroups where bias concentrates — your exploratory faithful-AFCP arm. | METHODS. |
| J6 | "A generic framework for conformal fairness." arXiv:2505.16115 (2025). | Formalises fair prediction sets via disparity in *conditional* coverage between sensitive groups. | METHODS. |
| J7 | "Fair conformal classification via learning representation-…" arXiv:2605.12195; "Counterfactually fair conformal prediction" arXiv:2510.08724; "Beyond procedure: substantive fairness in conformal prediction" arXiv:2602.16794; "FedCF: fair federated conformal prediction" arXiv:2509.22907. | The 2025–26 fair-conformal method literature (representation learning, counterfactual, federated). | METHODS — cite as "an active methods area". |
| J8 | Jung et al. 2022; Gibbs, Cherian, Candès — conditional conformal / group-conditional coverage. | Methods for approximate conditional coverage. | METHODS. |
| J9 | "Conditional coverage diagnostics for conformal prediction." arXiv (2025). | Diagnostics for whether conditional coverage holds. | METHODS. |
| J10 | **Conformal risk prediction for NAFLD using gradient boosting with distribution-free coverages (LiverRisk).** arXiv:2606.09860 (2026). | Guangzhou NAFLD cohort (n=2,187 + 412 external); GBDT + split conformal; marginal coverage 91.3% at 90%; **"coverage at or above nominal in all subgroups examined."** | **METHODS / ADJACENT — the only liver-disease conformal paper, and it reports the *opposite* of your subgroup finding on a different cohort.** |
| J11 | "On some practical challenges of conformal prediction." arXiv:2510.10324 (2025). | Practitioner cautions incl. the marginal-vs-conditional gap. | METHODS. |

## K. Selective prediction / learning to defer + fairness — FUTURE WORK (the AI-extension direction)

| # | Work | What it did | Tag |
|---|---|---|---|
| K1 | **Jones E, Sagawa S, Koh PW, Kumar A, Liang P. Selective classification can magnify disparities across groups.** *ICLR* 2021. | Abstaining on low-confidence cases can *widen* subgroup accuracy gaps; margin-distribution analysis. | **FUTURE WORK — the risk to flag if you pursue deferral.** |
| K2 | Schreuder N, Chzhen E. Classification with abstention but without disparities. *UAI* 2021. | Abstention method that controls group-wise reject rates to avoid disparate impact. | FUTURE WORK. |
| K3 | Shah A, Bu Y, et al. Selective regression under fairness criteria. *ICML* 2022. arXiv:2110.15403 | Fairness-constrained selective regression. | FUTURE WORK. |
| K4 | Madras D, Pitassi T, Zemel R. Predict responsibly: improving fairness and accuracy by learning to defer. *NeurIPS* 2018. | Learning-to-defer that passes cases to a downstream decision-maker to improve fairness + accuracy. | FUTURE WORK. |
| K5 | Mozannar H, Sontag D. Consistent estimators for learning to defer to an expert. *ICML* 2020. | Consistent surrogate losses for learn-to-defer. | FUTURE WORK. |
| K6 | **"Conformal selective prediction with cost-aware deferral for safe clinical triage under distribution shift."** *Sci Rep* 2026. doi:10.1038/s41598-026-40637-w | Calibrated probs + conformal + cost-aware deferral + group-conditional Mondrian + shift-robust conformal; **near-nominal validity across age and BMI strata** on sepsis triage. | **FUTURE WORK — the method stack, already published for clinical triage.** |
| K7 | "Cost-sensitive conformal prediction and human-in-the-loop abstention for imbalanced high-stakes decision support: a multi-domain benchmark." arXiv:2607.27143 (2026). | Cost-sensitive conformal + HITL abstention benchmark. | FUTURE WORK. |
| K8 | "Achieving fairness without harm via selective demographic experts." 2025 (PMC13056391). | Group-specific representations + no-harm-constrained selective use of demographic experts. | FUTURE WORK. |

## L. LLMs / foundation models for liver fibrosis — ADJACENT (a crowded, fast-moving space)

| # | Work | What it did | Tag |
|---|---|---|---|
| L1 | **Using large language models to predict advanced liver fibrosis in MASLD: a proof-of-concept analysis.** 2026. PMC12955738 | GPT-based LLMs predict advanced fibrosis from structured NHANES variables; interpretable rationale. | ADJACENT — LLM-as-predictor on NHANES-style data already done. |
| L2 | Performance of ChatGPT-4.0 in predicting advanced liver fibrosis in MASLD. Research Square rs-6928883 (2026). | ChatGPT-4.0: **accuracy 76.25%, AUROC 0.763, sens 65%, spec 80%**; inputs = ethnicity, MASLD dx, age, sex, BMI, diabetes, hypertension, albumin, AST, ALT, platelets. | ADJACENT. |
| L3 | **Machine-learning-enhanced non-invasive testing for MASLD fibrosis: shallow-deep NNs vs FIB-4, tabular foundation models, and LLMs.** arXiv:2605.20523 (2026). | Head-to-head: NNs, **tabular foundation models (TabPFN-class)**, and LLMs vs FIB-4 for MASLD fibrosis. | ADJACENT — foundation-model comparison already done. |
| L4 | **Njei B, et al. Large language models for diagnosis and prognosis of chronic liver diseases: a systematic review.** *Health Sci Rep* 2026. doi:10.1002/hsr2.72476 | Systematic review of LLM applications in chronic liver disease, incl. fibrosis staging. | ADJACENT / FRAMING. |
| L5 | AI-MASLD: metabolic dysfunction and steatosis information from LLMs in **unstructured clinical narratives.** arXiv:2512.11544 (2025). | LLMs extracting MASLD/fibrosis signal from free text. | ADJACENT. |
| L6 | "CURA: clinical uncertainty risk alignment for language-model-based risk prediction." arXiv:2604.14651 (2026). | Uncertainty alignment for LLM risk prediction. | ADJACENT. |

## M. Trustworthy-AI evaluation frameworks and reporting — FRAMING

| # | Work | What it did | Tag |
|---|---|---|---|
| M1 | **Collins GS, et al. TRIPOD+AI statement.** *BMJ* 2024. PMID 38626948 | Updated reporting guideline for clinical prediction models using regression or ML; subgroup performance with CIs now an expected item. | **FRAMING — the checklist to submit against.** |
| M2 | TRIAGE: Trustworthy Reporting and Assessment for Clinical Gain and Effectiveness of AI Models. *Diagnostics* 2026. doi:10.3390/diagnostics16050666 | Evaluation framework aligning AI testing to clinical use cases (screening, triage, second reading); integrates ROC/PR/lift/gain + calibration + DCA. | FRAMING. |
| M3 | FAIR-AI: a practical framework for appropriate implementation and review of AI in healthcare. *npj Digit Med* 2025. doi:10.1038/s41746-025-01900-y | Implementation/review framework; beyond AUC → calibration, F-score, DCA. | FRAMING. |
| M4 | RISED: a pre-deployment evaluation framework for high-stakes AI decision-support (applied to **NHANES 2021–2023**). arXiv (2026). | Structured pre-deployment numerical evidence complementing TRIPOD+AI, FUTURE-AI, Fairlearn. | FRAMING. |
| M5 | Ethics of trustworthy AI in healthcare: challenges, principles, practical pathways. *Neurocomputing* 2025. S0925231225026141. | Principles/pathways review. | FRAMING. |
| M6 | Auditing fairness in clinical AI systems using provenance-based simulation: a comparative and regulatory perspective. 2026. PMC13106396. | Provenance-based fairness-audit simulation. | FRAMING. |

---

## Bottom line for the write-up

**Nothing found supersedes the whole study**, but each component has prior work:

- **Your task and model set** (NHANES + VCTE + LR/RF/XGB/LGBM/MLP) are used in **A1, A4** and others — this is a crowded core; the models are not the contribution.
- **Your calibration finding** is published: **H1/H2** (general) and **A1** (same NHANES cohort + outcome, corrected there by a prevalence prior-shift). Frame as replication.
- **Your body-mass finding** is directionally consistent with **C1/C2** (NFS fails in lean) and complicated by **D1** (VCTE over-reads LSM in obesity — a measurement-bias caveat you must add to Limitations).
- **Marginal ≠ subgroup coverage** is a theorem (**J1**) and equalizing it can backfire (**J3**); **J10** reports no subgroup failure on a different liver cohort. Your empirical demonstration on this task, triangulated across cohorts, with a negative mitigation result, is the distinctive part.
- **The fairness-audit analog** is **F1** (sex, ILPD) and **F2** (sex, MASLD). None combine calibration + conformal + a mitigation battery on VCTE fibrosis.
- **LLM/foundation-model prediction of fibrosis** (**L1–L5**) is already active — do not pitch that as the novel extension.

Defensible one-sentence novelty claim: see `LITERATURE_REVIEW.md` §3.
