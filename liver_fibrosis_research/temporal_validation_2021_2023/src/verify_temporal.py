"""Number-verification harness for the temporal validation.

Re-derives the numbers quoted in MANUSCRIPT_SECTION_temporal.md straight from the
result CSVs and asserts them. Run after t01–t04. Non-zero exit on any failure.
"""
from __future__ import annotations

import sys

import pandas as pd

from _thelpers import TV

R = TV / "results"
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))


def main():
    coh = pd.read_json(TV / "data" / "processed" / "cohort_build_manifest.json", typ="series")
    check("cohort N = 4910", coh["N"] == 4910, f"got {coh['N']}")
    check("cohort positives = 563", coh["n_positive"] == 563, f"got {coh['n_positive']}")
    check("prevalence 11.4-11.5%", 11.4 <= coh["prevalence_pct"] <= 11.5, f"got {coh['prevalence_pct']}")

    dc = pd.read_csv(R / "temporal_discrimination_calibration_results.csv")
    raw = dc[dc.variant == "raw"]
    check("AUROC band 0.775-0.783", raw.auroc.min() >= 0.775 and raw.auroc.max() <= 0.783,
          f"{raw.auroc.min():.4f}-{raw.auroc.max():.4f}")
    check("AUROC delta -0.04 to -0.07", raw.auroc_delta.min() >= -0.07 and raw.auroc_delta.max() <= -0.04,
          f"{raw.auroc_delta.min():.4f}-{raw.auroc_delta.max():.4f}")
    recal = dc[dc.variant == "recalibrated"]
    check("recal intercepts within +-0.5", recal.calib_intercept.abs().max() <= 0.5,
          f"max |int| {recal.calib_intercept.abs().max():.3f}")

    fa = pd.read_csv(R / "temporal_fairness_results.csv")
    bmi = fa[(fa.dimension == "bmi") & (fa.category == "Obese")]
    check("BMI-Obese gap band 62-73 pp", bmi.absolute_disparity_pp.min() >= 62 and bmi.absolute_disparity_pp.max() <= 73,
          f"{bmi.absolute_disparity_pp.min():.1f}-{bmi.absolute_disparity_pp.max():.1f}")
    check("BMI-Obese gap BH-significant 5/5", int(bmi["significant_after_fdr_0.05"].sum()) == 5)
    check("BMI-Obese gap larger than 2017-2020 in 5/5",
          int((bmi.absolute_disparity_pp.values > bmi.disparity_pp_2017_2020.values).sum()) == 5)
    age = fa[(fa.dimension == "age") & (fa.category == "60+")]
    check("Age-60+ sensitivity reversed (all positive)", int((age.absolute_disparity_pp > 0).sum()) == 5,
          f"{age.absolute_disparity_pp.min():.1f}-{age.absolute_disparity_pp.max():.1f}")

    co = pd.read_csv(R / "temporal_conformal_results.csv")
    marg = co[co.scope == "marginal"]
    check("marginal coverage 0.87-0.91", marg.empirical_coverage.min() >= 0.87 and marg.empirical_coverage.max() <= 0.91,
          f"{marg.empirical_coverage.min():.3f}-{marg.empirical_coverage.max():.3f}")
    ob = co[co.scope == "bmi_Obese"]
    check("BMI-Obese coverage 0.75-0.82", ob.empirical_coverage.min() >= 0.75 and ob.empirical_coverage.max() <= 0.82,
          f"{ob.empirical_coverage.min():.3f}-{ob.empirical_coverage.max():.3f}")
    check("BMI-Obese under-coverage BH-significant 5/5", int(ob["significant_after_fdr_0.05"].sum()) == 5)
    inter = co[co.scope == "Obese_x_60plus"]
    check("intersection coverage 0.68-0.76", inter.empirical_coverage.min() >= 0.68 and inter.empirical_coverage.max() <= 0.76,
          f"{inter.empirical_coverage.min():.3f}-{inter.empirical_coverage.max():.3f}")
    check("intersection N = 788", int(inter.n.iloc[0]) == 788, f"got {int(inter.n.iloc[0])}")

    di = pd.read_csv(R / "temporal_dissociation.csv")
    check("dissociation replicated 5/5", int(di.dissociation_replicated.sum()) == 5)

    sc = pd.read_csv(R / "temporal_matched_stiffness_shortcut.csv")
    check("shortcut coefficient band 0.20-0.41", sc.beta_is_obese.min() >= 0.20 and sc.beta_is_obese.max() <= 0.41,
          f"{sc.beta_is_obese.min():.3f}-{sc.beta_is_obese.max():.3f}")
    check("shortcut p<0.05 in 5/5", int((sc.p_value < 0.05).sum()) == 5)

    # --- drop decomposition (t05) ---
    if (R / "temporal_drop_covariate_shift.csv").exists():
        cs = pd.read_csv(R / "temporal_drop_covariate_shift.csv")
        check("covariate-shift reweighting recovers <30% of the AUROC drop (concept drift)",
              cs.fraction_of_drop_recovered.mean() < 0.30,
              f"mean {cs.fraction_of_drop_recovered.mean():.2f}")
        sci = pd.read_csv(R / "temporal_drop_slice_ci.csv").set_index("slice")
        check("Normal-BMI within-slice AUROC drop CI excludes 0",
              sci.loc["bmi=Normal", "ci_high"] < 0,
              f"CI [{sci.loc['bmi=Normal','ci_low']}, {sci.loc['bmi=Normal','ci_high']}]")
        check("Age-60+ within-slice AUROC unchanged (CI includes 0)",
              sci.loc["age=60+", "ci_low"] < 0 < sci.loc["age=60+", "ci_high"])
        at = pd.read_csv(R / "temporal_drop_predictor_attribution.csv")
        check("no single predictor recovers >0.01 AUROC",
              at.groupby("predictor").auroc_recovery.mean().abs().max() < 0.01)

    # print
    n_ok = sum(1 for _, ok, _ in CHECKS if ok)
    print("=" * 66)
    print("TEMPORAL VALIDATION — NUMBER VERIFICATION")
    print("=" * 66)
    for name, ok, detail in CHECKS:
        print(f"[{'ok ' if ok else 'FAIL'}] {name}" + (f"   ({detail})" if detail and not ok else ""))
    print("-" * 66)
    print(f"  {n_ok}/{len(CHECKS)} passed")
    sys.exit(0 if n_ok == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
