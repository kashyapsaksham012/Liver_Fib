# Reference verification — Track 2.2

**Date:** 2026-08-27. Each of the 28 manuscript references checked against the primary source
(journal page, PubMed, arXiv, or conference proceedings) via web lookup this pass. This is a
single-reviewer verification; a co-author should still repeat it.

Legend: **OK** = title, authors, venue, year, and identifier all confirmed · **FIX** = a concrete
error found (detailed) · **FILL** = real paper, identifier to be pasted in · **READ** = claim the
manuscript makes about this paper needs a full-text check before submission.

---

## ⚠️ Material findings (must be actioned)

### F1 — Reference 1 is **Cao et al.**, not "Zhou et al." (HIGH)
`doi:10.3389/fmed.2026.1736295` — *Frontiers in Medicine* 2026;13:1736295, published 23 Jun 2026.
**First author: Dong Cao** (full byline: Cao D, Wang J, Hou C, Zeng J, Tian B, Liu Y, Luo X, Tian J,
Zhou M, Li P, Fang H, Liu Z, Gong Z, +4). "Zhou" (Mingbo Zhou) is the **9th** author.
- The manuscript, `LITERATURE_REVIEW.md`, `RELATED_WORK_SCAN.md`, `DO_NOT_CLAIM.md`,
  `START_HERE.md`, `FINAL_SCIENTIFIC_FINDINGS.md`, and every register that names the
  nearest-neighbour paper as **"Zhou et al. Front Med 2026"** must be corrected to **"Cao et al."**
  (~15 occurrences). `grep -rn "Zhou et al" documentation/` to find them all.
- Likely origin of the slip: reference 23 is "**Zhou** & Sesia" (Yanfei Zhou), a different paper.

### F2 — Reference 1: calibration claim is grounded, but re-confirm the cut-point wording (MEDIUM · READ)
Manuscript §4.1 states this has "already been shown on the same NHANES cohort and outcome,
corrected there by a Bayesian prevalence prior-shift rather than out-of-fold Platt scaling [1]".
The repo's own full-text scan (`RELATED_WORK_SCAN.md` A1, `LITERATURE_REVIEW.md` line 41) records
that Cao et al. **do** correct raw Brier 0.148–0.158 → 0.073 via a Bayesian prevalence
prior-correction — so the "replication" framing is supported by that scan. Two residual points to
confirm on a final read: (a) Cao's cut-point is **> 8 kPa**, ours is **≥ 8.2 kPa** (§4.1 says
"same … outcome" — tighten to "closely comparable outcome"); (b) Cao's N ≈ 6,164 vs our 7,153
(different cleaning), so "same NHANES cohort" overstates — say "the same NHANES release".

### F3 — References 22 and 23 are the **same paper** (MEDIUM)
Both are: **Yanfei Zhou & Matteo Sesia**, "Conformal Classification with Equalized Coverage for
Adaptively Selected Groups", arXiv:2405.15106, **NeurIPS 2024**. "AFCP" is the method name in that
paper. **Merge 22 and 23 into one reference**; renumber 24–28 → 23–27. Update the in-text markers
(current [22], [23]) accordingly. The KNN-AFCP vs faithful-AFCP distinction in
`EXPLORATORY_RESULTS.md` E7 is about *our* two implementations of this one method, not two papers.

---

## Per-reference table

| # | Manuscript citation | Verdict | Confirmed identifier / correction |
|---|---|---|---|
| 1 | "Zhou et al. … *Front Med* 2026" | **FIX (F1, F2)** | **Cao D** et al. *Front Med* 2026;13:1736295. doi:10.3389/fmed.2026.1736295. NHANES 2017–2020; VCTE > 8 kPa; AUROC 0.82–0.87; external Chinese cohort; no fairness/conformal. |
| 2 | "…MASLD using VCTE: NHANES 2021–2023. *BMC Gastroenterol* 2025" | **FIX (title)** | *BMC Gastroenterol* 2025;25:255. doi:10.1186/s12876-025-03850-x. Actual title says **"metabolic dysfunction-associated fatty liver disease"** (MAFLD), not MASLD. |
| 3 | "Fibro-Predict … *Sci Rep* 2025" | **OK** | *Sci Rep* 2025;15:32035. doi:10.1038/s41598-025-17534-9. PMID 40887472. PMC12399762. Title has no hyphen: "Fibro predict…". |
| 4 | "Accuracy of FIB-4 and NFS in MAFLD according to BMI… *Eur J Gastroenterol Hepatol* 2020. PMID:32976186" | **OK** | PMID 32976186. doi:10.1097/MEG.0000000000001946. 560 biopsy-proven MAFLD; FIB-4 and NFS both fail in lean **and** morbidly obese. |
| 5 | "Diagnostic performance of FIB-4 and NFS in lean adults with NAFLD. 2023. PMID:37589973" | **FILL** | *JAMA Netw Open* 2023;6(8):e2328692. PMID 37589973. PMC10436134. (Asia, 6 centres, biopsy-proven; NFS sensitivity unacceptable in lean, FIB-4 robust.) |
| 6 | "Graupera et al. … *Clin Gastroenterol Hepatol* 2021" | **FIX (year)** | *Clin Gastroenterol Hepatol* **2022**;20(11):2567–2576. doi:10.1016/j.cgh.2021.12.034. PMID 34971806. |
| 7 | "Diabetes and obesity reduce FIB-4 accuracy in MASLD referral pathways. *JHEP Rep* 2026" | **FILL** | *JHEP Rep* 2026. doi:10.1016/j.jhepr.2026.101735 (S2589-5559(26)00005-4). Supports our BMI finding: "Diabetes/BMI ≥ 30 increase the risk of ≥ 8 kPa stiffness even at FIB-4 < 1.30 … fast-track to elastography." |
| 8 | "Srivastava et al. … primary-care referral pathway for NAFLD. *J Hepatol* 2019" | **OK** | *J Hepatol* 2019;71(2):371–378. PMID 30965069. doi:10.1016/j.jhep.2019.03.033. FIB-4→ELF pathway; 81 % fewer referrals, 5× more advanced-fibrosis cases. Our "roughly 80 %" is accurate. |
| 9 | "Collins et al. TRIPOD+AI statement. *BMJ* 2024. PMID:38626948" | **FILL** | *BMJ* 2024;385:e078378. doi:10.1136/bmj-2023-078378. PMID 38626948. PMC11025451. Authors: Collins GS, Moons KGM, Dhiman P, Riley RD, Beam AL, Van Calster B, et al. |
| 10 | "van den Goorbergh et al. … *JAMIA* 2022;29(9):1525–34. doi:10.1093/jamia/ocac093" | **OK** | Confirmed. Also arXiv:2202.09101. Authors: van den Goorbergh R, van Smeden M, Timmerman D, Van Calster B. |
| 11 | "Carriero et al. … *Stat Med* 2025. doi:10.1002/sim.10320" | **OK** | *Stat Med* 2025;44(3-4):e10320. arXiv:2404.19494. Authors: Carriero A, Luijken K, de Hond A, Moons KGM, van Calster B, van Smeden M. |
| 12 | "Straw & Wu … *BMJ Health Care Inform* 2022. doi:10.1136/bmjhci-2021-100457" | **OK** | *BMJ Health Care Inform* 2022;29(1):e100457. PMC9039354. Isabel Straw, Honghan Wu. Dataset = Indian Liver Patient Dataset (not NHANES) — manuscript already distinguishes this. |
| 13 | "Understanding algorithmic fairness … subgroup net benefit … arXiv:2412.07879, 2024" | **FIX (now published)** | Now **peer-reviewed: *Epidemiology* 2026 (May issue)**, journals.lww.com/epidem/…/2026/05000. arXiv:2412.07879. **Cite the *Epidemiology* version.** This is the "levelling down" source — the abstract uses that exact phrase. Update the arXiv-only citation in `DO_NOT_CLAIM.md` and the deferral reports too. |
| 14 | "Critical appraisal of fairness metrics … *Lancet Digit Health* 2026" | **FILL** | *Lancet Digit Health* 2026 (S2589-7500(26)00024-5). arXiv:2506.17035. 42 studies, 63 fairness metrics; "over-reliance on threshold-dependent metrics". |
| 15 | "Vovk, Gammerman, Shafer. *Algorithmic Learning in a Random World*. Springer, 2005" | **OK (canonical)** | Springer 2005 (2nd ed. 2022, ISBN 978-3-031-06648-1). Standard textbook. |
| 16 | "Angelopoulos & Bates. A gentle introduction to conformal prediction… 2021/2023" | **OK** | arXiv:2107.07511 (2021). Also *Found Trends Mach Learn* 16(4):494–591 (2023). Anastasios N. Angelopoulos, Stephen Bates. |
| 17 | "Barber, Candès, Ramdas, Tibshirani. The limits of distribution-free conditional predictive inference. *Inf Inference* 2021. arXiv:1903.04684" | **OK** | *Inf Inference* 2021;10(2):455–482. doi:10.1093/imaiai/iaaa017. arXiv:1903.04684. Confirmed the impossibility-of-exact-conditional-coverage result. |
| 18 | "Romano, Barber, Sabbatti, Candès. With malice toward none… *Harv Data Sci Rev* 2020" | **FIX (spelling)** | "**Sabatti**" (Chiara Sabatti), not "Sabbatti". *Harv Data Sci Rev* 2020;2(2). doi:10.1162/99608f92.03f00592. |
| 19 | "Angelopoulos et al. Conformal risk control. *ICLR* 2024" | **FILL** | ICLR 2024. arXiv:2208.02814. Authors: Angelopoulos AN, Bates S, Fisch A, Lei L, Schuster T. |
| 20 | "Conformal prediction in clinical artificial intelligence. *CHEST* 2025" | **FIX (year) + FILL (authors)** | *CHEST* **2026** (in print; article S0012-3692(25)05184-0, online 2025). **Author list still not retrieved** — get it from the full text before submission. |
| 21 | "Conformal prediction sets can cause disparate impact. *ICLR* 2025" | **FILL** | ICLR 2025 (Spotlight). arXiv:2410.01888. OpenReview fZK6AQXlUU. Authors: Cresswell JC, Kumar B, Sui Y, Belbahri M. Finding: Equalized Coverage **increases** disparate impact vs marginal; equalize *set sizes* instead. |
| 22 | "Conformal classification with equalized coverage for adaptively selected groups. *NeurIPS* 2024" | **FIX (F3 — merge with 23)** | = ref 23. Yanfei Zhou, Matteo Sesia. arXiv:2405.15106. NeurIPS 2024. OpenReview 3pWHKxK1sC. |
| 23 | "Zhou & Sesia. Adaptively fair conformal prediction (AFCP). 2024" | **FIX (F3 — merge with 22)** | Same paper as 22. "AFCP" is its method name. |
| 24 | "Conformal risk prediction for NAFLD … (LiverRisk). arXiv:2606.09860, 2026" | **FILL + READ** | arXiv:2606.09860 (2026). **Xinze Zhang** (USC). "LiverRisk": GBDT + conformal, MI-based stability selection. **READ:** manuscript §4.1 claims this "reported coverage at or above nominal in every subgroup examined [24]" — the abstract only asserts *marginal* coverage. Verify the subgroup claim in the full text or soften to "did not report a subgroup coverage failure". |
| 25 | "Jones et al. Selective classification can magnify disparities across groups. *ICLR* 2021" | **OK** | ICLR 2021. arXiv:2010.14134. Authors: Jones E, Sagawa S, Koh PW, Kumar A, Liang P. |
| 26 | "Schreuder & Chzhen. Classification with abstention but without disparities. *UAI* 2021" | **OK** | UAI 2021, PMLR v161. arXiv:2102.12258. Nicolas Schreuder, Evgenii Chzhen. |
| 27 | "Madras, Pitassi, Zemel. Predict responsibly: improving fairness and accuracy by learning to defer. *NeurIPS* 2018" | **OK (canonical)** | NeurIPS 2018. arXiv:1711.06664. David Madras, Toniann Pitassi, Richard Zemel. |
| 28 | "Conformal selective prediction with cost-aware deferral… *Sci Rep* 2026. doi:10.1038/s41598-026-40637-w" | **OK** | *Sci Rep* 2026. doi:10.1038/s41598-026-40637-w. Authors: Kwon H, Kim DJ. Sepsis triage; split conformal + gender-stratified Mondrian + importance-weighted + cost-aware deferral. Matches our "application-level precedent" framing. |

---

## Actions for the manuscript

1. **F1** — global `Zhou et al.` → `Cao et al.` for ref 1 across `documentation/` (not ref 23's "Zhou & Sesia").
2. **F2** — read Cao et al. in full; rewrite the §4.1 sentence about their calibration handling.
3. **F3** — merge refs 22 + 23; renumber 24–28 → 23–27; fix in-text markers.
4. Apply the small FIXes: ref 2 title (MAFLD), ref 6 year (2022), ref 13 (cite *Epidemiology* 2026), ref 18 spelling (Sabatti), ref 20 year (2026).
5. Paste identifiers for the FILL rows (5, 7, 9, 14, 19, 20, 21, 24) into the reference list.
6. **F2 / ref 24 READ** — both are claims in §4.1 about what a cited paper found; verify against full text before submission.
7. New reference-list count after the merge: **27**.

## Not done (needs a human / a systematic search)

Full author lists for every reference; the CHEST 2026 review's byline; a documented multi-database
search (Track 2.3); confirming refs 15/19/27 identifiers by opening the arXiv/Springer pages (they
are canonical works — low risk).
