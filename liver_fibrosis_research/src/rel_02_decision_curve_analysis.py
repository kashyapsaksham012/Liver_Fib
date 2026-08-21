"""
rel_02_decision_curve_analysis.py
Reliability Extension, Analysis B: Decision Curve Analysis (DCA), population-level and for the two
headline subgroups (BMI-Obese, Age-60+). Uses the already-frozen, recalibrated locked test-set
predicted probabilities (results/calibration/test_set_recalibrated_predictions.csv) -- no model is
retrained, no prediction is regenerated.

Probability source: RECALIBRATED (Platt-type, Phase 4, Amendment #8), frozen choice, documented
rationale (see documentation/reliability_extension/pre_execution_snapshot.md and the final report):
DCA's net-benefit formula treats the classification threshold as a literal risk probability: NB =
(TP/n) - (FP/n)*(pt/(1-pt)). Phase 4 established that raw probabilities for 4/5 models substantially
overstate risk (intercept -1.86 to -2.26); using raw probabilities would make the threshold axis not
correspond to actual risk for those models, which is a known, standard methodological requirement of
DCA (Vickers & Elkin). This choice is frozen before computing any curve -- not selected because it
produces a nicer result.

Threshold range: 1%-50%, frozen as an explicit analytical choice (no project-specific or literature-
derived range exists in this project's documentation -- confirmed by search this pass).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, MODEL_NAMES

RESULTS_DIR = ROOT / "results" / "reliability_extension"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
THRESH_MIN, THRESH_MAX, THRESH_STEP = 0.01, 0.50, 0.01

recal = pd.read_csv(ROOT / "results" / "calibration" / "test_set_recalibrated_predictions.csv")
primary = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
group_map = primary.set_index("SEQN")[["bmi_group_final", "age_group_final"]]

thresholds = np.round(np.arange(THRESH_MIN, THRESH_MAX + 1e-9, THRESH_STEP), 4)

def net_benefit(y, p, pt):
    n = len(y)
    yhat = (p >= pt).astype(int)
    tp = int(((y == 1) & (yhat == 1)).sum())
    fp = int(((y == 0) & (yhat == 1)).sum())
    return (tp / n) - (fp / n) * (pt / (1 - pt))

def treat_all_nb(y, pt):
    prev = y.mean()
    return prev - (1 - prev) * (pt / (1 - pt))

def dca_for_population(df, label):
    rows = []
    y = df["true_target"].values
    n = len(df)
    for pt in thresholds:
        ta = treat_all_nb(y, pt)
        rows.append({"population": label, "model": "TREAT_ALL", "threshold": pt, "n": n, "net_benefit": ta})
        rows.append({"population": label, "model": "TREAT_NONE", "threshold": pt, "n": n, "net_benefit": 0.0})
    for m in MODEL_NAMES:
        sub = df[df["model"] == m]
        y_m = sub["true_target"].values
        p_m = sub["recalibrated_predicted_probability"].values
        for pt in thresholds:
            nb = net_benefit(y_m, p_m, pt)
            rows.append({"population": label, "model": m, "threshold": pt, "n": len(sub), "net_benefit": nb})
    return rows

all_rows = []
all_rows += dca_for_population(recal, "population")

recal_j = recal.merge(group_map, left_on="SEQN", right_index=True, how="left")

bmi_obese = recal_j[recal_j["bmi_group_final"] == "Obese"]
age_60 = recal_j[recal_j["age_group_final"] == "60+"]

n_bmi = bmi_obese[bmi_obese["model"] == "logistic"].shape[0]
pos_bmi = int(bmi_obese[bmi_obese["model"] == "logistic"]["true_target"].sum())
n_age = age_60[age_60["model"] == "logistic"].shape[0]
pos_age = int(age_60[age_60["model"] == "logistic"]["true_target"].sum())
print(f"BMI-Obese test subset: N={n_bmi}, positive={pos_bmi}")
print(f"Age-60+ test subset: N={n_age}, positive={pos_age}")

MIN_RELIABLE_POSITIVES = 20
bmi_reliable = pos_bmi >= MIN_RELIABLE_POSITIVES
age_reliable = pos_age >= MIN_RELIABLE_POSITIVES
print(f"BMI-Obese DCA reliable (>= {MIN_RELIABLE_POSITIVES} positives)? {bmi_reliable}")
print(f"Age-60+ DCA reliable (>= {MIN_RELIABLE_POSITIVES} positives)? {age_reliable}")

if bmi_reliable:
    all_rows += dca_for_population(bmi_obese, "bmi_obese")
if age_reliable:
    all_rows += dca_for_population(age_60, "age_60plus")

out = pd.DataFrame(all_rows)
out.to_csv(RESULTS_DIR / "dca_results.csv", index=False)
print(f"\nSaved dca_results.csv ({len(out)} rows)")

with open(RESULTS_DIR / "dca_reliability_flags.txt", "w") as f:
    f.write(f"BMI-Obese: N={n_bmi}, positive={pos_bmi}, reliable={bmi_reliable}\n")
    f.write(f"Age-60+: N={n_age}, positive={pos_age}, reliable={age_reliable}\n")
    if not bmi_reliable:
        f.write("BMI-Obese SUBGROUP DCA NOT RELIABLE AT THIS SAMPLE SIZE\n")
    if not age_reliable:
        f.write("Age-60+ SUBGROUP DCA NOT RELIABLE AT THIS SAMPLE SIZE\n")
print("Saved dca_reliability_flags.txt")
