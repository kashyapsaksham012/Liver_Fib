# Target-venue decision memo — Track 2.1

**Date:** 2026-08-27. A recommendation for the author to act on. Supersedes the shortlist in
`LITERATURE_REVIEW.md` §5 with a concrete first choice + a fallback ladder, weighted for the
actual constraints: **solo unaffiliated researcher, self-funded, no external validation, a
negative/methodological result.**

---

## The three constraints that drive the choice

1. **Cost.** No funding → an article-processing charge (APC) comes out of pocket. This rules
   *nothing* out but reorders the list: journals with a no-fee route rank higher.
2. **"No external validation" desk-reject risk.** Higher-impact venues (npj Digital Medicine,
   *Lancet Digital Health*) are likely to desk-reject or demand validation you have decided not to
   pursue. Lower risk at methods/informatics venues that publish reliability audits.
3. **Negative-result framing.** The contribution is "aggregate metrics are insufficient evidence
   of subgroup safety + no post-hoc fix". Venues with an explicit negative/replication policy are
   safer.

---

## Recommendation

### Preprint first (do this regardless): **medRxiv**
- Establishes the work and its date before any journal decision. Free.
- List yourself as "Independent Researcher" with city/country — medRxiv accepts unaffiliated
  authors; one author needs to be the corresponding author, which is you.
- Post the preprint *after* the Amendment #19 result is folded in (v5), not before — so the
  preprint is the complete story.

### Primary journal: **JAMIA** (Journal of the American Medical Informatics Association)
- **Fit:** publishes fairness/calibration audits of clinical prediction models; reference [10]
  (the class-imbalance–calibration paper you replicate) is theirs; reviewer pool is the right one.
- **Cost:** Oxford offers a **subscription track with no mandatory APC** (you only pay if you opt
  into open access). This is the single biggest reason it ranks first for a self-funded author.
- **Format:** TRIPOD+AI expected — you have the checklist (Track 2.4). Original research, ~4,000
  words + structured abstract.
- **Risk:** competitive; a reviewer may still push on external validation. Mitigation: the
  abstract and §5 already state it as the foremost limitation, and the contribution is explicitly
  methodological, not a deployable model.

### Fallback ladder (in order)

1. **Journal of Biomedical Informatics** (Elsevier) — methods-forward, publishes subgroup-reliability
   and conformal-in-clinical work; subscription track with no mandatory APC; slightly lower bar
   than JAMIA. Reformatting from JAMIA is light.
2. **PLOS Digital Health** — **explicit negative-results / limitation-focused policy**, open
   access (~USD 2,500 APC **with a fee-assistance/waiver programme for unfunded authors — apply**),
   fast, fully OA visibility. Strong fit for the framing; the APC waiver makes it viable.
3. **JMIR AI** or **JMIR Medical Informatics** — receptive to methods + negative results, fast
   review, APC ~USD 1,500–2,000 (lower than PLOS), waivers available. Good if speed matters.
4. **BMJ Health & Care Informatics** — reference [12] (Straw & Wu, the closest fairness-audit
   analog) is theirs; open access, APC, shorter-format friendly.

### Do not submit to
*Hepatology*, *J Hepatol*, *Clin Gastroenterol Hepatol*, *BMC Gastroenterology*,
*npj Digital Medicine*, *Lancet Digital Health* — they will treat this as a prediction-model
paper and reject on modest discrimination + no external validation. (npj/Lancet DH also carry the
highest APCs.)

### Optional parallel track: a workshop paper
**ML4H** (Machine Learning for Health, a NeurIPS workshop; typically submits ~Sept, non-archival
or lightly archival) or **ACM CHIL** (archival, ~Feb deadline). A 4-page version gets methods-
audience feedback and a citable artefact months before the journal decision. Negative results are
welcome at both. This does **not** preclude the journal submission (workshop versions are not
"prior publication" for these venues, but confirm the target journal's policy).

---

## Suggested sequence

1. Fold in Amendment #19 → manuscript v5 (Track 3).
2. Post v5 to **medRxiv**.
3. Submit to **JAMIA**. If ML4H's deadline is near, submit a 4-page version there in parallel.
4. On rejection: JBI → PLOS Digital Health (apply for the APC waiver) → JMIR AI.

## Author-affiliation note

Every venue above accepts unaffiliated authors listed as "Independent Researcher". State it
plainly in the byline and the cover letter; do not obscure it. A clean, well-audited solo
methodological paper is a credible submission — the rigor of the protocol is what carries it.
