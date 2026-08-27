"""
ttm_05_apply_gate.py  --  Amendment #19, Phase 2.3

Apply the pre-registered G1-G7 gate (TRAINING_TIME_MITIGATION_PLAN.md §0.3.6) MECHANICALLY to
the two locked-test-touch outputs. No judgement, no post-hoc threshold changes. Reads only:
  results/training_time_mitigation/test_classification.csv
  results/training_time_mitigation/test_subgroup_sensitivity.csv
  results/training_time_mitigation/test_conformal.csv

Writes:
  results/training_time_mitigation/gate_detail.csv   (per arm x gate: pass/fail + the numbers)
  results/training_time_mitigation/decision.csv      (per arm: verdict; overall verdict)

Pure pandas. Deterministic. Run after ttm_03 + ttm_04.
"""
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TTM = ROOT / "results" / "training_time_mitigation"
MLP_FALLBACK = os.environ.get("MLP_FALLBACK", "0") == "1"
N_REQ = 3 if MLP_FALLBACK else 4          # ">= 4/5" -> ">= 3/4" under MLP fallback
N_ALL = 4 if MLP_FALLBACK else 5

# frozen baseline (PRE_EXECUTION_SNAPSHOT.md §0.3.5)
BASE = pd.DataFrame({
    "model": ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"],
    "obese_minus_normal_pp": [47.6623, 31.6234, 31.3636, 27.0779, 39.0260],
    "age60_minus_4059_pp": [-8.5509, -13.1563, -11.2361, -14.1464, -14.6715],
    "auroc": [0.8334, 0.8343, 0.8429, 0.8394, 0.8229],
    "sens": [0.750, 0.790, 0.845, 0.795, 0.815],
    "spec": [0.7621, 0.7359, 0.6773, 0.7492, 0.6644],
    "brier_recal": [0.071, 0.071, 0.069, 0.070, 0.071],   # test_set_calibration_final.csv recal Brier
}).set_index("model")


def main():
    cls = pd.read_csv(TTM / "test_classification.csv")
    sub = pd.read_csv(TTM / "test_subgroup_sensitivity.csv")
    con = pd.read_csv(TTM / "test_conformal.csv")

    detail, decisions = [], []
    arms = sorted(cls["arm"].unique())
    for arm in arms:
        c = cls[cls.arm == arm].set_index("model")
        s = sub[sub.arm == arm]
        cv = con[con.arm == arm]
        models = list(c.index)

        def add(gate, passed, note):
            detail.append({"arm": arm, "gate": gate, "pass": bool(passed), "note": note})
            return bool(passed)

        # --- G1: sensitivity efficacy ---
        g1_ok = 0
        g1_notes = []
        for m in models:
            row = s[(s.model == m) & (s.dimension == "bmi") & (s.category == "Obese")]
            if row.empty:
                continue
            new_gap = abs(float(row["disparity_pp"].iloc[0]))     # |Obese - Normal|
            base_gap = abs(BASE.loc[m, "obese_minus_normal_pp"])
            reduced = new_gap <= 0.5 * base_gap
            small = new_gap < 15.0
            if reduced and small:
                g1_ok += 1
            g1_notes.append(f"{m}:{base_gap:.1f}->{new_gap:.1f}")
        G1 = add("G1_sensitivity_efficacy", g1_ok >= N_REQ, f"{g1_ok}/{N_ALL} models; " + ", ".join(g1_notes))

        # --- G2: coverage efficacy ---
        g2_ok = 0
        g2_notes = []
        for m in models:
            ob = cv[(cv.model == m) & (cv.category == "bmi:Obese")]
            ag = cv[(cv.model == m) & (cv.category == "age:60+")]
            if ob.empty or ag.empty:
                continue
            ob_c, ob_lo = float(ob["coverage"].iloc[0]), float(ob["wilson_lo"].iloc[0])
            ag_c = float(ag["coverage"].iloc[0])
            if ob_c >= 0.88 and ob_lo >= 0.85 and ag_c >= 0.88:
                g2_ok += 1
            g2_notes.append(f"{m}:Ob={ob_c:.3f}(lo{ob_lo:.3f}),60+={ag_c:.3f}")
        # G2 requires >=N_REQ on BOTH obese and 60+; the per-model AND above enforces it
        G2 = add("G2_coverage_efficacy", g2_ok >= N_REQ, f"{g2_ok}/{N_ALL} models; " + ", ".join(g2_notes))

        # --- G3: no marginal breach ---
        marg = cv[cv.scope == "marginal"].set_index("model")["coverage"]
        g3_ok = int(((marg >= 0.87) & (marg <= 0.93)).sum())
        G3 = add("G3_marginal_in_0.87_0.93", g3_ok == N_ALL,
                 "; ".join(f"{m}:{marg[m]:.3f}" for m in models))

        # --- G4: discrimination ---
        g4_ok = 0
        for m in models:
            if float(c.loc[m, "test_auroc"]) >= BASE.loc[m, "auroc"] - 0.02:
                g4_ok += 1
        G4 = add("G4_auroc_within_-0.02", g4_ok >= N_REQ,
                 "; ".join(f"{m}:{float(c.loc[m,'test_auroc']):.4f}(base {BASE.loc[m,'auroc']:.4f})" for m in models))

        # --- G5: calibration ---
        g5_ok = 0
        for m in models:
            if float(c.loc[m, "brier_recal"]) <= BASE.loc[m, "brier_recal"] + 0.01:
                g5_ok += 1
        G5 = add("G5_brier_within_+0.01", g5_ok >= N_REQ,
                 "; ".join(f"{m}:{float(c.loc[m,'brier_recal']):.4f}" for m in models))

        # --- G6: no other-subgroup harm ---
        g6_age_ok = 0
        for m in models:
            row = s[(s.model == m) & (s.dimension == "age") & (s.category == "60+")]
            if row.empty:
                continue
            new_age = float(row["disparity_pp"].iloc[0])           # 60+ minus 40-59, negative = worse
            base_age = BASE.loc[m, "age60_minus_4059_pp"]
            if new_age >= base_age - 5.0:                          # not worsened by > 5 pp
                g6_age_ok += 1
        # no sex/race subgroup newly BH-significant
        newly_sig = s[(s.dimension.isin(["sex", "race"])) & (s["significant_after_fdr_0.05"] == True)]
        G6 = add("G6_no_other_subgroup_harm", (g6_age_ok >= N_REQ) and newly_sig.empty,
                 f"age not-worsened {g6_age_ok}/{N_ALL}; newly-sig sex/race rows: {len(newly_sig)}")

        # --- G7: overall performance ---
        g7_ok = 0
        for m in models:
            ds = abs(float(c.loc[m, "sensitivity"]) - BASE.loc[m, "sens"])
            dp = abs(float(c.loc[m, "specificity"]) - BASE.loc[m, "spec"])
            if ds <= 0.05 and dp <= 0.05:
                g7_ok += 1
        G7 = add("G7_overall_sens_spec_within_5pp", g7_ok >= N_REQ,
                 "; ".join(f"{m}:Δsens{float(c.loc[m,'sensitivity'])-BASE.loc[m,'sens']:+.3f},Δspec{float(c.loc[m,'specificity'])-BASE.loc[m,'spec']:+.3f}" for m in models))

        cost_ok = G3 and G4 and G5 and G6 and G7
        if G1 and G2 and cost_ok:
            verdict = "SUCCESS"
        elif (G1 ^ G2) and cost_ok:
            verdict = "PARTIAL"
        elif (G1 or G2) and not cost_ok:
            verdict = "NEGATIVE (cost)"
        else:
            verdict = "NEGATIVE (no efficacy)"
        decisions.append({"arm": arm, "G1": G1, "G2": G2, "G3": G3, "G4": G4, "G5": G5,
                          "G6": G6, "G7": G7, "verdict": verdict})
        print(f"arm {arm}: G1={G1} G2={G2} G3={G3} G4={G4} G5={G5} G6={G6} G7={G7}  ->  {verdict}")

    dec = pd.DataFrame(decisions)
    # overall = the arm-A verdict (primary); arm B can only add nuance
    overall = dec[dec.arm == "A"]["verdict"].iloc[0] if "A" in dec.arm.values else dec["verdict"].iloc[0]
    dec.loc[len(dec)] = {"arm": "OVERALL", **{g: None for g in ["G1","G2","G3","G4","G5","G6","G7"]},
                         "verdict": overall}
    pd.DataFrame(detail).to_csv(TTM / "gate_detail.csv", index=False)
    dec.to_csv(TTM / "decision.csv", index=False)
    print(f"\nOVERALL (arm A primary): {overall}")
    print(f"Wrote {TTM}/gate_detail.csv and decision.csv")


if __name__ == "__main__":
    main()
