# Socio-Conformal Novelty Threat Report

**Paper Title:** Socio-Conformal Calibration in Complex Survey Data: Marginal Validity Is Not Enough for Subgroup Reliability  
**Authors:** Amir Rafe, Subasish Das  
**arXiv Identifier:** 2605.05562 (submitted to NeurIPS 2026)  
**Audit Date:** 2026-08-25  

---

## 1. Scientific Overview & Key Summary
Das and Rafe (2026) investigate the application of conformal prediction to survey-based social measurement, specifically focusing on AI-attitude forecasting using the Pew American Trends Panel (ATP Wave 152) data. The core of their argument is that **nominal marginal validity** (conformal prediction's standard global guarantee) is insufficient for ensuring subgroup reliability and fairness across diverse population groups.

The paper is critical of "vanilla" Mondrian (group-conditional) conformal prediction. When subgroups are small (e.g., "Black non-Hispanic | College+"), Mondrian cells suffer from **calibration-cell fragmentation (the thin-cell problem)**, leading to highly unstable, high-variance conformal thresholds. This variance manifests as severe prediction set-size perturbations.

To resolve this, the authors propose a **regularized Mondrian conformal prediction** approach based on **James-Stein shrinkage**. The subgroup conformal thresholds are shrunk toward the global aggregate threshold in proportion to cell size and threshold variance. In their XGBoost experiments, this regularized shrinkage approach reduced the maximum set-size perturbation from +0.442 to +0.159 while yielding a superior coverage-to-set-size efficiency profile.

---

## 2. Extraction & Audit Matrix

| Question | Paper Details | Relevance to Liver-Fibrosis Project |
| :--- | :--- | :--- |
| **Scientific Question** | How to guarantee reliable, fair subgroup-level uncertainty bounds in survey-based social forecasting under complex splits? | We similarly examine subgroup coverage validity (under-coverage of Obese and Age 60+ groups) in clinical prediction. |
| **Dataset Type** | Social survey data (Pew American Trends Panel ATP Wave 152, ordinal outcomes). | Clinical survey data (NHANES, binary outcome `LUXSMED` transient elastography). |
| **Complex-Survey Weights** | Explicitly discussed; marginal vs. subgroup weights and complex sampling structures affect cell density. | NHANES uses complex survey weights (`WTMECPRP`, `SDMVPSU`, `SDMVSTRA`), which we leverage in our baseline statistics but not in base classifier losses. |
| **Conformal Method** | Ordinal conformal prediction (for 5-level Likert scale outcomes). | Binary split-conformal prediction (nonconformity score = $1 - P(y=\text{true\_class} \mid x)$). |
| **Subgroup Reliability** | Explicitly analyzed; marginal coverage hides extreme subgroup-level under-coverage. | Identical premise: marginal 90% coverage hides severe under-coverage in Obese (82%) and Age 60+ (84%) groups. |
| **Intersectional Groups** | Analyzed (e.g., joint groups such as "Black non-Hispanic | College+"). | We analyze intersectional groups (e.g., Obese × Age 60+) and identify severe coverage gaps. |
| **Thin-Cell/Sample-Size Issue** | Major focus: vanilla Mondrian on thin cells creates threshold instability and huge set-size variance. | We observe this limit: Normal BMI (N_pos=22) and Underweight (N_pos=0 in calibration) are too thin for separate Mondrian calibration. |
| **Proposed Mitigation** | Regularized Mondrian conformal prediction using James-Stein shrinkage. | We proposed FDR-gated Mondrian conformal mitigation (targeting only groups with statistically significant under-coverage). |
| **Efficiency Metrics** | Set size, singleton rate, and set-size perturbation. | Mean set size, singleton rate, and doubleton rate. |

---

## 3. Novelty Threat Assessment
**NOVELTY THREAT = LOW**

### Why the Threat is Low:
1. **Application Context:** Das & Rafe focus on survey-based social measurement (Likert scale attitudes toward AI, ordinal outcomes). Our study is a clinical diagnostics pipeline (biomarkers and clinical predictors mapping to physical liver stiffness).
2. **Conformal Formulation:** They use *ordinal* conformal prediction. We use *binary classification* split-conformal prediction.
3. **Mitigation Machinery:** They propose a *regularized shrinkage estimator* for Mondrian thresholds to resolve thin-cell variance. We propose a *multiple-testing FDR-gated Mondrian framework* that dynamically determines which subgroups require separate conformal thresholds based on statistical significance testing.
4. **Core Novelty Claim Safety:**
   - **Candidate 1 (Model-family-dependent fairness-coverage coupling):** This relationship is completely untouched by Das & Rafe.
   - **Candidate 2 (Model-family-dependent intersectional mechanism):** Completely untouched.
   - **Candidate 4 (Calibration sufficiency):** We show that Platt recalibration is necessary but insufficient for subgroup conformal coverage. Das & Rafe argue a similar philosophical point (marginal is not enough for subgroups) but do not evaluate Platt scaling vs. conformal calibration or base-classifier class-balancing.

---

## 4. Manuscript Integration Plan
- **Introduction:** Cite Das & Rafe (arXiv:2605.05562) when introducing the limitations of marginal conformal prediction (e.g., "While marginal validity provides aggregate guarantees, it fails to ensure reliability within demographic subgroups, a phenomenon recently demonstrated in social survey contexts [Das & Rafe, 2026]...").
- **Methods (Mitigation):** Contrast our FDR-gated targeting against their James-Stein shrinkage approach to justify why we use a multiple-testing significance gate to control thin-cell false discoveries rather than shrinkage.
- **Discussion:** Address the thin-cell problem. Cite their findings regarding threshold variance in smaller demographic splits to contextualize our decision to defer Mondrian conformal prediction on Underweight and Normal-BMI groups.
