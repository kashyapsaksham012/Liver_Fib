"""Number-verification harness for the pooled model-update re-audit."""
from __future__ import annotations

import json
import sys

import pandas as pd

from _phelpers import PU

R = PU / "results"
C = []


def ck(name, ok, detail=""):
    C.append((name, bool(ok), detail))


def main():
    coh = json.loads((PU / "data" / "processed" / "pooled_cohort_manifest.json").read_text())
    ck("pooled N = 12063", coh["N_total"] == 12063, str(coh["N_total"]))
    ck("pooled positives = 1229", coh["n_positive"] == 1229)
    ck("test 2021-2023 slice N = 1473", coh["test_by_cycle"]["2021-2023"]["N"] == 1473)

    d = pd.read_csv(R / "pooled_discrimination_results.csv")
    da = d[d.tag == "pooled_test_all"]; d21 = d[d.tag == "pooled_test_2021_2023"]
    ck("pooled-test AUROC band 0.80-0.82", da.auroc.min() >= 0.80 and da.auroc.max() <= 0.82,
       f"{da.auroc.min():.3f}-{da.auroc.max():.3f}")
    ck("2021-2023 slice AUROC still < 0.80 (updating did not recover it)",
       d21.auroc.max() < 0.80, f"max {d21.auroc.max():.3f}")

    f = pd.read_csv(R / "pooled_fairness_results.csv")
    bmi = f[(f.tag == "pooled_test_all") & (f.dimension == "bmi") & (f.category == "Obese")]
    ck("BMI-Obese gap still positive 5/5", int((bmi.absolute_disparity_pp > 0).sum()) == 5)
    ck("BMI-Obese gap still BH-significant 5/5", int(bmi["significant_after_fdr_0.05"].sum()) == 5)
    ck("BMI-Obese gap band 30-60 pp", bmi.absolute_disparity_pp.min() >= 30 and bmi.absolute_disparity_pp.max() <= 60,
       f"{bmi.absolute_disparity_pp.min():.0f}-{bmi.absolute_disparity_pp.max():.0f}")

    c = pd.read_csv(R / "pooled_conformal_results.csv")
    ob = c[(c.tag == "pooled_test_all") & (c.scope == "bmi_Obese")]
    ck("BMI-Obese conformal under-coverage persists 5/5",
       int((ob["ci_excludes_90"] & (ob.coverage < 0.90)).sum()) == 5)
    ck("BMI-Obese coverage band 0.75-0.83", ob.coverage.min() >= 0.75 and ob.coverage.max() <= 0.83,
       f"{ob.coverage.min():.3f}-{ob.coverage.max():.3f}")
    mg = c[(c.tag == "pooled_test_all") & (c.scope == "marginal")]
    ck("marginal coverage 0.87-0.91", mg.coverage.min() >= 0.87 and mg.coverage.max() <= 0.91,
       f"{mg.coverage.min():.3f}-{mg.coverage.max():.3f}")

    s = pd.read_csv(R / "pooled_shortcut_results.csv")
    sa = s[s.tag == "pooled_test_all"]
    ck("matched-stiffness shortcut persists (p<0.05 5/5)", int((sa.p_value < 0.05).sum()) == 5)
    ck("shortcut coefficient positive 5/5", int((sa.beta_is_obese > 0).sum()) == 5)

    v = pd.read_csv(R / "pooled_verdicts.csv").set_index("question")
    ck("verdict: body-mass gap NOT RESOLVED", v.loc["Body-mass detection gap", "verdict"] == "NOT RESOLVED")
    ck("verdict: conformal under-coverage NOT RESOLVED",
       v.loc["BMI-Obese conformal under-coverage", "verdict"] == "NOT RESOLVED")
    ck("verdict: shortcut NOT RESOLVED",
       v.loc["Matched-stiffness body-mass shortcut", "verdict"] == "NOT RESOLVED")

    n_ok = sum(1 for _, ok, _ in C if ok)
    print("=" * 64)
    print("POOLED MODEL-UPDATE RE-AUDIT — NUMBER VERIFICATION")
    print("=" * 64)
    for name, ok, detail in C:
        print(f"[{'ok ' if ok else 'FAIL'}] {name}" + (f"   ({detail})" if detail and not ok else ""))
    print("-" * 64)
    print(f"  {n_ok}/{len(C)} passed")
    sys.exit(0 if n_ok == len(C) else 1)


if __name__ == "__main__":
    main()
