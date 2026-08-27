"""
Selective-deferral mitigation -- Phase 1-2 (Amendment #17).

Phase 1: build the leakage-safe development dataset (conformal-calibration
partition, N=1,002, x per-model nonconformity scores x subgroup labels).
Phase 2: reproduce the frozen subgroup conformal coverage on the calibration
partition; check the sub-amendment #17a trigger (subgroup cell sizes).

Reads only frozen artifacts (see PRE_EXECUTION_SNAPSHOT.md). No model loaded,
no test data touched, nothing frozen modified.

Outputs:
  results/selective_deferral/dev_calibration_scored.csv
  results/selective_deferral/phase1_2_leakage_and_cellsizes.csv
  results/selective_deferral/phase1_2_baseline_subgroup_coverage.csv
  documentation/selective_deferral_mitigation/PHASE1_2_DEV_AND_BASELINE.md
"""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/selective_deferral"
OUT.mkdir(parents=True, exist_ok=True)
MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
ALPHA = 0.10


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def ids(p):
    return set(pd.read_csv(ROOT / p)["SEQN"].astype("int64"))


# ---- Phase 1: partitions + leakage ------------------------------------------
cal_ids = ids("data/processed/splits/conformal_calibration_ids.csv")
pt_ids = ids("data/processed/splits/proper_train_ids.csv")
test_ids = ids("data/processed/splits/test_ids.csv")

leak = {
    "cal_n": len(cal_ids),
    "overlap_cal_propertrain": len(cal_ids & pt_ids),
    "overlap_cal_test": len(cal_ids & test_ids),
    "cal_ids_sha256": sha256("data/processed/splits/conformal_calibration_ids.csv"),
}
assert leak["overlap_cal_propertrain"] == 0, "LEAKAGE: calibration overlaps proper-train"
assert leak["overlap_cal_test"] == 0, "LEAKAGE: calibration overlaps locked test"

# ---- subgroup labels from the frozen dataset -------------------------------
df = pd.read_parquet(ROOT / "data/processed/analysis_dataset_primary.parquet")
df["SEQN"] = df["SEQN"].astype("int64")
lab = df.set_index("SEQN")[["age_group_final", "bmi_group_final", "RIAGENDR",
                            "RIDRETH3", "outcome_primary_8.2kPa"]]

# ---- per-model calibration scores + frozen thresholds ---------------------
thr = pd.read_csv(ROOT / "results/uncertainty/conformal_thresholds_by_model.csv")
qhat = dict(zip(thr["model"], thr["threshold"]))

rows = []
cov_rows = []
scored_frames = []
for m in MODELS:
    f = ROOT / f"results/uncertainty/calibration_scores_{m}.csv"
    s = pd.read_csv(f)
    s["SEQN"] = s["SEQN"].astype("int64")
    s = s.merge(lab, left_on="SEQN", right_index=True, how="left")
    assert s["age_group_final"].notna().all(), f"{m}: unmatched SEQN in calibration set"
    # consistency: true_target in scores == frozen outcome
    assert (s["true_target"].astype(int) == s["outcome_primary_8.2kPa"].astype(int)).all(), \
        f"{m}: true_target disagrees with frozen outcome"
    p = s["predicted_probability_positive"].to_numpy()
    q = qhat[m]
    # frozen split-conformal prediction sets on the calibration data
    incl_pos = (1.0 - p) <= q
    incl_neg = p <= q
    y = s["true_target"].astype(int).to_numpy()
    true_in_set = np.where(y == 1, incl_pos, incl_neg)
    s["_incl_pos"], s["_incl_neg"] = incl_pos, incl_neg
    s["_set_size"] = incl_pos.astype(int) + incl_neg.astype(int)
    s["_true_in_set"] = true_in_set
    s["_u"] = np.minimum(p, 1.0 - p)          # deferral uncertainty score (0=confident,0.5=max)
    s["model"] = m
    scored_frames.append(s)

    # baseline subgroup coverage on calibration data
    for dim, col in [("bmi", "bmi_group_final"), ("age", "age_group_final")]:
        for cat, g in s.groupby(col, observed=True):
            cov_rows.append({
                "model": m, "dimension": dim, "category": str(cat),
                "n": len(g), "n_positive": int(g["true_target"].sum()),
                "coverage_calibration": float(g["_true_in_set"].mean()),
                "singleton_rate": float((g["_set_size"] == 1).mean()),
                "mean_set_size": float(g["_set_size"].mean()),
            })
    cov_rows.append({
        "model": m, "dimension": "marginal", "category": "overall",
        "n": len(s), "n_positive": int(s["true_target"].sum()),
        "coverage_calibration": float(s["_true_in_set"].mean()),
        "singleton_rate": float((s["_set_size"] == 1).mean()),
        "mean_set_size": float(s["_set_size"].mean()),
    })
    rows.append({"model": m, "calibration_scores_sha256": sha256(f), "qhat": q})

scored = pd.concat(scored_frames, ignore_index=True)
scored.to_csv(OUT / "dev_calibration_scored.csv", index=False)
cov = pd.DataFrame(cov_rows)
cov.to_csv(OUT / "phase1_2_baseline_subgroup_coverage.csv", index=False)

# ---- sub-amendment #17a trigger check -------------------------------------
one = scored[scored["model"] == "logistic"]
cell = (one.groupby("bmi_group_final", observed=True)
        .agg(n=("SEQN", "size"), pos=("true_target", "sum")).reset_index())
cell_age = (one.groupby("age_group_final", observed=True)
            .agg(n=("SEQN", "size"), pos=("true_target", "sum")).reset_index())
cell_all = pd.concat([cell.rename(columns={"bmi_group_final": "group"}),
                      cell_age.rename(columns={"age_group_final": "group"})], ignore_index=True)
cell_all["dimension"] = ["bmi"] * len(cell) + ["age"] * len(cell_age)
obese = int(cell.loc[cell["bmi_group_final"] == "Obese", "n"].iloc[0])
obese_pos = int(cell.loc[cell["bmi_group_final"] == "Obese", "pos"].iloc[0])
age60 = int(cell_age.loc[cell_age["age_group_final"] == "60+", "n"].iloc[0])
age60_pos = int(cell_age.loc[cell_age["age_group_final"] == "60+", "pos"].iloc[0])
trigger_17a = (obese < 50 or obese_pos < 15 or age60 < 50 or age60_pos < 15)

# did the under-coverage reproduce on calibration data?
obese_cov = cov[(cov.dimension == "bmi") & (cov.category == "Obese")]["coverage_calibration"]
age60_cov = cov[(cov.dimension == "age") & (cov.category == "60+")]["coverage_calibration"]
repro = (obese_cov < 0.90).mean() >= 0.6 and (age60_cov < 0.90).mean() >= 0.6

pd.DataFrame([leak]).to_csv(OUT / "phase1_2_leakage_and_cellsizes.csv", index=False)

# ---- report --------------------------------------------------------------
md = ["# Phase 1-2 -- development partition & baseline reproduction (Amendment #17)", "",
      f"Leakage checks: calibration N={leak['cal_n']}; overlap with proper-train "
      f"{leak['overlap_cal_propertrain']}; overlap with locked test {leak['overlap_cal_test']}. "
      "Both must be 0 -- **PASS**.", "",
      "## Subgroup calibration-cell sizes (sub-amendment #17a trigger)", "",
      "| dimension | group | n | positives |", "|---|---|---:|---:|"]
for _, r in cell_all.iterrows():
    md.append(f"| {r['dimension']} | {r['group']} | {int(r['n'])} | {int(r['pos'])} |")
md += ["",
       f"BMI-Obese cell: n={obese}, pos={obese_pos}. Age-60+ cell: n={age60}, pos={age60_pos}.",
       f"**Sub-amendment #17a trigger (cell < 50 or positives < 15): "
       f"{'TRIGGERED' if trigger_17a else 'not triggered'}.**", ""]
if trigger_17a:
    md.append("> #17a requires the model-fitting stack (joblib/sklearn/xgboost/lightgbm), which "
              "is unavailable here. Recorded; the group-conditional quantile candidates (3b/3d) "
              "will be developed on the frozen partition and their small-cell limitation reported.")
md += ["", "## Baseline subgroup conformal coverage on the calibration partition", "",
       "(frozen threshold; should show BMI-Obese and Age-60+ below 0.90, as on the locked test)", "",
       "| model | dimension | category | n | coverage (calib) | singleton rate | mean set size |",
       "|---|---|---|---:|---:|---:|---:|"]
for _, r in cov.sort_values(["model", "dimension", "category"]).iterrows():
    md.append(f"| {r['model']} | {r['dimension']} | {r['category']} | {int(r['n'])} | "
              f"{r['coverage_calibration']:.3f} | {r['singleton_rate']:.3f} | {r['mean_set_size']:.3f} |")
md += ["",
       f"**Under-coverage reproduced on calibration data (BMI-Obese & Age-60+ < 0.90 for the "
       f"majority of models): {'YES' if repro else 'NO'}.**",
       "" if repro else "> NOT reproduced -> the calibration partition may be too small/unrepresentative; "
       "see the plan's DEVELOPMENT-STAGE NEGATIVE branch."]
(ROOT / "documentation/selective_deferral_mitigation/PHASE1_2_DEV_AND_BASELINE.md").write_text(
    "\n".join(md) + "\n")
print("\n".join(md[-40:]))
print(f"\nTRIGGER_17a={trigger_17a}  REPRODUCED={repro}")
