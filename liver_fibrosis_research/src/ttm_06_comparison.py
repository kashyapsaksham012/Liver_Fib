"""
ttm_06_comparison.py  --  Amendment #19, Phase 3.1 / 3.2 / 3.3

Assemble the manuscript-facing comparison: frozen baseline -> post-hoc mitigation battery
(from the existing manuscript Table 4, transcribed) -> Arm A -> Arm B, on one metric grid;
plus the mechanism comparison (score ordering vs threshold) and the cost accounting.

Pure pandas. Run after ttm_03 + ttm_04 (+ ttm_05).

Outputs (results/training_time_mitigation/):
  comparison_vs_battery.csv
  mechanism_comparison.csv
  cost_accounting.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TTM = ROOT / "results" / "training_time_mitigation"

BASE = pd.DataFrame({
    "model": ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"],
    "obese_minus_normal_pp": [47.6623, 31.6234, 31.3636, 27.0779, 39.0260],
    "auroc": [0.8334, 0.8343, 0.8429, 0.8394, 0.8229],
    "sens": [0.750, 0.790, 0.845, 0.795, 0.815],
    "spec": [0.7621, 0.7359, 0.6773, 0.7492, 0.6644],
    "bmi_obese_cov": [0.8233, 0.8018, 0.7678, 0.7916, 0.8086],
    "age60_cov": [0.8489, 0.8556, 0.8111, 0.8475, 0.8381],
    "marginal_cov": [0.9082, 0.8961, 0.8812, 0.8961, 0.8919],
}).set_index("model")

# post-hoc battery -- median across the 5 models, transcribed from the frozen manuscript Table 4 /
# FINAL_SCIENTIFIC_FINDINGS.md §14 (for the comparison column only; not recomputed here).
BATTERY = [
    {"method": "Subgroup Youden thresholds (exploratory)", "obese_minus_normal_pp": "~ +14 to +16 (halved)",
     "bmi_obese_cov": "n/a", "age60_cov": "n/a", "marginal_cov": "n/a",
     "cost": "age gap +26-133%; ~40 pp specificity cost", "disposition": "EXPLORATORY"},
    {"method": "Subgroup calibration", "obese_minus_normal_pp": "unchanged",
     "bmi_obese_cov": "unchanged", "age60_cov": "unchanged", "marginal_cov": "unchanged",
     "cost": "ECE improved 3/5; decisions unchanged", "disposition": "NO ACCEPTABLE MITIGATION"},
    {"method": "Mondrian conformal (Project Phase 7)", "obese_minus_normal_pp": "n/a (coverage-only)",
     "bmi_obese_cov": ">= 0.88 for 5/9 targets", "age60_cov": "partial", "marginal_cov": "XGB 0.934 (+5.3 pp breach)",
     "cost": "4/9 unresolved; marginal breach", "disposition": "PARTIALLY EFFECTIVE"},
    {"method": "Mondrian re-run (Amendment #17, 3d)", "obese_minus_normal_pp": "n/a",
     "bmi_obese_cov": ">= 0.88 for 5/5", "age60_cov": ">= 0.88 for 5/5", "marginal_cov": "0.94-0.95 (over-covers)",
     "cost": "levelling down required for target marginal", "disposition": "PARTIALLY EFFECTIVE"},
    {"method": "Equalized-odds post-processing (exploratory)", "obese_minus_normal_pp": "~ 0 (equalised)",
     "bmi_obese_cov": "n/a", "age60_cov": "n/a", "marginal_cov": "n/a",
     "cost": "~40 pp specificity; ~399 excess FP / 1,000 normal-weight", "disposition": "EXPLORATORY (clinically unacceptable)"},
    {"method": "XGBoost retuning", "obese_minus_normal_pp": "n/a",
     "bmi_obese_cov": "no breach removed w/o cost", "age60_cov": "n/a", "marginal_cov": "n/a",
     "cost": "11-22 pp sensitivity cost", "disposition": "NO ACCEPTABLE RETUNING"},
    {"method": "Joint intersectional conformal (exploratory)", "obese_minus_normal_pp": "n/a",
     "bmi_obese_cov": "n/a", "age60_cov": "n/a", "marginal_cov": "XGB/LGBM breach ±5 pp",
     "cost": "cell N=138", "disposition": "EXPLORATORY"},
    {"method": "Conformal selective deferral (Amendment #17)", "obese_minus_normal_pp": "n/a",
     "bmi_obese_cov": "lowered (deferring uncertain sets)", "age60_cov": "lowered", "marginal_cov": "n/a",
     "cost": "no candidate meets the gate", "disposition": "NO IMPROVEMENT"},
]


def main():
    cls = pd.read_csv(TTM / "test_classification.csv")
    sub = pd.read_csv(TTM / "test_subgroup_sensitivity.csv")
    con = pd.read_csv(TTM / "test_conformal.csv")
    diag = pd.read_csv(TTM / "phase1_mechanism_diagnostic.csv")

    rows = []
    # baseline row (median across models)
    rows.append({"stage": "frozen baseline", "arm": "", "method": "baseline",
                 "obese_minus_normal_pp": round(BASE["obese_minus_normal_pp"].median(), 2),
                 "bmi_obese_cov": round(BASE["bmi_obese_cov"].median(), 4),
                 "age60_cov": round(BASE["age60_cov"].median(), 4),
                 "marginal_cov": round(BASE["marginal_cov"].median(), 4),
                 "overall_sens": round(BASE["sens"].median(), 3),
                 "overall_spec": round(BASE["spec"].median(), 3),
                 "auroc": round(BASE["auroc"].median(), 4), "disposition": "-"})
    for b in BATTERY:
        rows.append({"stage": "post-hoc battery", "arm": "", "method": b["method"],
                     "obese_minus_normal_pp": b["obese_minus_normal_pp"],
                     "bmi_obese_cov": b["bmi_obese_cov"], "age60_cov": b["age60_cov"],
                     "marginal_cov": b["marginal_cov"], "overall_sens": "", "overall_spec": "",
                     "auroc": "", "disposition": b["disposition"]})
    # arms (median across models)
    dec = pd.read_csv(TTM / "decision.csv").set_index("arm")["verdict"].to_dict() if (TTM / "decision.csv").exists() else {}
    for arm in sorted(cls["arm"].unique()):
        c = cls[cls.arm == arm]
        s = sub[(sub.arm == arm) & (sub.dimension == "bmi") & (sub.category == "Obese")]
        cob = con[(con.arm == arm) & (con.category == "bmi:Obese")]
        cag = con[(con.arm == arm) & (con.category == "age:60+")]
        cmar = con[(con.arm == arm) & (con.scope == "marginal")]
        rows.append({"stage": "training-time", "arm": arm,
                     "method": f"subgroup reweighing (arm {arm})",
                     "obese_minus_normal_pp": round(s["disparity_pp"].median(), 2),
                     "bmi_obese_cov": round(cob["coverage"].median(), 4),
                     "age60_cov": round(cag["coverage"].median(), 4),
                     "marginal_cov": round(cmar["coverage"].median(), 4),
                     "overall_sens": round(c["sensitivity"].median(), 3),
                     "overall_spec": round(c["specificity"].median(), 3),
                     "auroc": round(c["test_auroc"].median(), 4),
                     "disposition": dec.get(arm, "see decision.csv")})
    pd.DataFrame(rows).to_csv(TTM / "comparison_vs_battery.csv", index=False)

    # mechanism: did within-Normal-BMI test AUROC rise? did the shortcut coef shrink?
    mech = []
    for _, r in diag.iterrows():
        mech.append({"arm": r["arm"], "model": r["model"],
                     "normal_bmi_oof_auc_delta": r.get("normal_bmi_oof_auc_delta"),
                     "score_separation_delta": round(float(r.get("normal_bmi_score_separation_reweighted", np.nan))
                                                     - float(r.get("normal_bmi_score_separation_baseline", np.nan)), 4)
                     if pd.notna(r.get("normal_bmi_score_separation_reweighted")) else None,
                     "shortcut_coef_baseline": r.get("bmi_shortcut_coef_baseline"),
                     "shortcut_coef_reweighted": r.get("bmi_shortcut_coef_reweighted"),
                     "interpretation": "score ordering improved" if (pd.notna(r.get("normal_bmi_oof_auc_delta"))
                                       and float(r["normal_bmi_oof_auc_delta"]) > 0.01)
                                       else "threshold shift only / no ordering gain"})
    pd.DataFrame(mech).to_csv(TTM / "mechanism_comparison.csv", index=False)

    # cost accounting per arm x model
    cost = []
    for _, r in cls.iterrows():
        cost.append({"arm": r["arm"], "model": r["model"],
                     "delta_auroc": r["delta_auroc_vs_baseline"],
                     "delta_sens": r["delta_sens_vs_baseline"],
                     "delta_spec": r["delta_spec_vs_baseline"],
                     "delta_brier_recal": round(float(r["brier_recal"]) -
                        {"logistic":0.071,"random_forest":0.071,"xgboost":0.069,"lightgbm":0.070,"mlp":0.071}[r["model"]], 4)})
    pd.DataFrame(cost).to_csv(TTM / "cost_accounting.csv", index=False)

    print("Wrote comparison_vs_battery.csv, mechanism_comparison.csv, cost_accounting.csv")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
