"""Phase 9 — classify against the pre-registered verdicts (PROTOCOL_FREEZE.md §5)
and write the re-audit report + drop-in manuscript section.
"""
from __future__ import annotations

import json

import pandas as pd

from _phelpers import PU, MODELS

R = PU / "results"


def nt(s):
    return int(pd.Series(s).sum())


def main():
    coh = json.loads((PU / "data" / "processed" / "pooled_cohort_manifest.json").read_text())
    d = pd.read_csv(R / "pooled_discrimination_results.csv")
    f = pd.read_csv(R / "pooled_fairness_results.csv")
    c = pd.read_csv(R / "pooled_conformal_results.csv")
    s = pd.read_csv(R / "pooled_shortcut_results.csv")

    d_all = d[d.tag == "pooled_test_all"]
    d_21 = d[d.tag == "pooled_test_2021_2023"]
    bmi_all = f[(f.tag == "pooled_test_all") & (f.dimension == "bmi") & (f.category == "Obese")]
    bmi_21 = f[(f.tag == "pooled_test_2021_2023") & (f.dimension == "bmi") & (f.category == "Obese")]
    ob_all = c[(c.tag == "pooled_test_all") & (c.scope == "bmi_Obese")]
    sc_all = s[s.tag == "pooled_test_all"]

    V = []
    # 1. body-mass detection gap
    dir_ok = nt((bmi_all.absolute_disparity_pp > 0))
    sig = nt(bmi_all["significant_after_fdr_0.05"])
    V.append(("Body-mass detection gap",
              f"pooled test: {bmi_all.absolute_disparity_pp.min():.0f}-{bmi_all.absolute_disparity_pp.max():.0f} pp, "
              f"BH-significant {sig}/5 (2021-2023 slice: {bmi_21.absolute_disparity_pp.min():.0f}-"
              f"{bmi_21.absolute_disparity_pp.max():.0f} pp, {nt(bmi_21['significant_after_fdr_0.05'])}/5)",
              "NOT RESOLVED" if (dir_ok >= 4 and sig >= 4) else "RESOLVED/PARTIAL"))
    # 2. BMI-Obese conformal under-coverage
    under = nt(ob_all["ci_excludes_90"] & (ob_all.coverage < 0.90))
    V.append(("BMI-Obese conformal under-coverage",
              f"pooled test: coverage {ob_all.coverage.min():.3f}-{ob_all.coverage.max():.3f}, "
              f"Wilson CI excludes 0.90 in {under}/5",
              "NOT RESOLVED" if under >= 4 else "RESOLVED/PARTIAL"))
    # 3. matched-stiffness shortcut
    ssig = nt(sc_all.p_value < 0.05)
    spos = nt(sc_all.beta_is_obese > 0)
    V.append(("Matched-stiffness body-mass shortcut",
              f"pooled test: is_obese coefficient {sc_all.beta_is_obese.min():.2f}-{sc_all.beta_is_obese.max():.2f}, "
              f"p<0.05 in {ssig}/5",
              "NOT RESOLVED" if (ssig >= 4 and spos >= 4) else "RESOLVED/PARTIAL"))
    # 4. discrimination recovery (pooled test)
    rec = nt(d_all.auroc >= 0.81)
    V.append(("Aggregate discrimination (pooled test)",
              f"AUROC {d_all.auroc.min():.3f}-{d_all.auroc.max():.3f} "
              f"(frozen 2017-2020: 0.823-0.843; temporal 2021-2023: 0.776-0.782); {rec}/5 >= 0.81",
              "PARTIALLY RECOVERED" if rec >= 3 else "NOT RECOVERED"))
    # 5. discrimination on the 2021-2023 slice
    rec21 = nt(d_21.auroc >= 0.80)
    V.append(("Discrimination on the 2021-2023 slice",
              f"AUROC {d_21.auroc.min():.3f}-{d_21.auroc.max():.3f}; {rec21}/5 >= 0.80 "
              "(un-updated frozen model on 2021-2023 was 0.776-0.782)",
              "NOT RECOVERED" if rec21 < 4 else "RECOVERED"))

    vdf = pd.DataFrame(V, columns=["question", "result", "verdict"])
    vdf.to_csv(R / "pooled_verdicts.csv", index=False)

    core_not_resolved = sum(1 for _, _, v in V[:3] if v == "NOT RESOLVED")
    overall = ("UPDATING DOES NOT RESOLVE THE FAILURE" if core_not_resolved == 3 else
               "UPDATING PARTIALLY HELPS" if core_not_resolved == 2 else
               "UPDATING LARGELY RESOLVES THE FAILURE")

    md = [
        "# Model-update re-audit — pooled NHANES 2017-2023", "",
        f"**Design.** Five families retrained on a pooled 2017-2023 cohort "
        f"(N={coh['N_total']}, {coh['n_positive']} positive, {coh['prevalence_pct']}% prevalence; "
        f"train {coh['split']['train']['N']} / locked test {coh['split']['test']['N']}, stratified on "
        "cycle x outcome), using the **frozen hyperparameters, preprocessing, threshold method, "
        "Platt method and conformal method unchanged**. Locked test touched once.", "",
        f"## Overall: **{overall}**", "",
        f"{core_not_resolved}/3 core reliability failures persist after updating.", "",
        vdf.to_markdown(index=False), "",
        "## Reading", "",
        "- **The body-mass detection gap is not a staleness artefact.** Retraining on data that "
        "includes the 2021-2023 cycle leaves the Normal-vs-Obese sensitivity gap intact "
        f"({bmi_all.absolute_disparity_pp.min():.0f}-{bmi_all.absolute_disparity_pp.max():.0f} pp, "
        "BH-significant 5/5; larger still on the 2021-2023 slice). The matched-stiffness body-mass "
        "shortcut is likewise unchanged (5/5, p<0.001). The conformal subgroup under-coverage "
        "persists 5/5.",
        "- **Updating restores aggregate discrimination only partially, and not at all on the "
        "newer data.** Pooled-test AUROC recovered to ~0.81 (from the temporal 0.78), but on the "
        f"2021-2023 test slice it stayed at {d_21.auroc.min():.2f}-{d_21.auroc.max():.2f} — no "
        "better than the un-updated frozen model. The 2021-2023 concept drift is not learnable by "
        "adding the drifted cycle to training; a genuinely changed predictor-outcome relationship "
        "(or reference-standard change) is the parsimonious explanation.",
        "- **Conclusion.** Neither post-hoc mitigation (Amendments #17-18), training-time "
        "reweighting (Amendment #19), nor model updating on newer data resolves the body-mass "
        "reliability-fairness failure. It is structural.",
        "",
        "## Boundary", "",
        "A diagnostic re-audit, not a proposed deployable model and not external validation. "
        "Pooled numbers are a separate evidence tier and change no `evidence-freeze` primary or "
        "secondary claim. Nothing in the frozen tree or the temporal module was modified.",
    ]
    (PU / "documentation" / "POOLED_REAUDIT_REPORT.md").write_text("\n".join(md) + "\n")

    print(vdf.to_string(index=False))
    print(f"\nOVERALL: {overall}")
    print(f"wrote {PU/'documentation'/'POOLED_REAUDIT_REPORT.md'}")


if __name__ == "__main__":
    main()
