"""
ttm_00_compute_weights.py  --  Amendment #19, Phase 1.1

Compute Kamiran & Calders reweighing weights for the training-time mitigation.

For participant i with subgroup g_i and primary outcome y_i, computed on the FITTING
partition only:

    w_i = n(g_i) * n(y_i) / ( N * n(g_i, y_i) )        then rescaled so mean(w_i) = 1

making g (BMI band, Arm A; or BMI x age cell, Arm B) statistically independent of the
outcome in the reweighted fitting distribution.

Fitting partitions:
  - full training partition  (train_ids.csv,        N = 5,007)  -> classification fits (ttm_01)
  - proper-train subset      (proper_train_ids.csv, N = 4,005)  -> conformal fits      (ttm_02)

Arm A: g = bmi_group_final (4 levels).
Arm B: g = (bmi_group_final, age_group_final) (12 cells); a cell with < 10 positive
       members falls back to its Arm-A (BMI-marginal) weight.

Weights use y -> fitting-time only; inference never uses them. Weights are NEVER applied
to the conformal-calibration set or the locked test.

Needs only pandas + numpy (no scikit-learn). Reproducible (no randomness).

Outputs (results/training_time_mitigation/):
  weights_armA_train.csv        weights_armA_propertrain.csv
  weights_armB_train.csv        weights_armB_propertrain.csv
  weights_summary.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "training_time_mitigation"
OUT.mkdir(parents=True, exist_ok=True)

OUTCOME = "outcome_primary_8.2kPa"
BMI_COL = "bmi_group_final"
AGE_COL = "age_group_final"
MIN_POS_ARM_B = 10  # a BMI x age cell with fewer positives falls back to the Arm-A weight

EXPECT = {  # (N, positives) -- asserted; from PRE_EXECUTION_SNAPSHOT.md
    "train": (5007, 466),
    "propertrain": (4005, 373),
}


def load_partition(which):
    df = pd.read_parquet(ROOT / "data/processed/analysis_dataset_primary.parquet")
    df["SEQN"] = df["SEQN"].astype("int64")
    id_file = {"train": "train_ids.csv", "propertrain": "proper_train_ids.csv"}[which]
    ids = set(pd.read_csv(ROOT / "data/processed/splits" / id_file)["SEQN"].astype("int64"))
    d = df[df.SEQN.isin(ids)][["SEQN", BMI_COL, AGE_COL, OUTCOME]].reset_index(drop=True)
    n, pos = EXPECT[which]
    assert len(d) == n, f"{which}: N={len(d)} expected {n}"
    assert int(d[OUTCOME].sum()) == pos, f"{which}: positives={int(d[OUTCOME].sum())} expected {pos}"
    assert d[BMI_COL].notna().all() and d[AGE_COL].notna().all(), f"{which}: missing subgroup labels"
    return d


def kamiran_calders(d, group_series):
    """w_i = n(g_i)*n(y_i) / (N * n(g_i, y_i)), rescaled to mean 1."""
    N = len(d)
    y = d[OUTCOME].to_numpy()
    g = group_series.to_numpy()
    n_g = pd.Series(g).value_counts().to_dict()
    n_y = {0: int((y == 0).sum()), 1: int((y == 1).sum())}
    gy = pd.DataFrame({"g": g, "y": y}).value_counts().to_dict()  # {(g, y): count}
    w = np.array([n_g[gi] * n_y[yi] / (N * gy[(gi, yi)]) for gi, yi in zip(g, y)], dtype=float)
    return w / w.mean()


def ess(w):
    return float(w.sum() ** 2 / (w ** 2).sum())


def compute_arm(d, arm):
    if arm == "A":
        w = kamiran_calders(d, d[BMI_COL])
    else:
        cell = d[BMI_COL].astype(str) + " x " + d[AGE_COL].astype(str)
        pos_by_cell = d.groupby(cell)[OUTCOME].sum()
        weak = set(pos_by_cell[pos_by_cell < MIN_POS_ARM_B].index)
        w_full = kamiran_calders(d, cell)
        w_bmi = kamiran_calders(d, d[BMI_COL])
        w = np.where(cell.isin(weak).to_numpy(), w_bmi, w_full)
        w = w / w.mean()
    out = d.copy()
    out["weight"] = np.round(w, 8)
    return out, w


def main():
    summary = []
    for which in ("train", "propertrain"):
        d = load_partition(which)
        for arm in ("A", "B"):
            out, w = compute_arm(d, arm)
            path = OUT / f"weights_arm{arm}_{which}.csv"
            out.to_csv(path, index=False)
            # per-subgroup ESS (BMI x class)
            rows = []
            for bmi in ["Underweight", "Normal", "Overweight", "Obese"]:
                for y in (0, 1):
                    m = (d[BMI_COL] == bmi).to_numpy() & (d[OUTCOME].to_numpy() == y)
                    if m.sum() == 0:
                        continue
                    rows.append({"partition": which, "arm": arm, "bmi": bmi, "class": y,
                                 "n": int(m.sum()), "w_mean": round(float(w[m].mean()), 4),
                                 "cell_ess": round(ess(w[m]), 1)})
            summary.extend(rows)
            ds_ess = ess(w)
            flag = ""
            nb_pos = w[(d[BMI_COL] == "Normal").to_numpy() & (d[OUTCOME].to_numpy() == 1)]
            if ess(nb_pos) < 15:
                flag += "NORMAL_BMI_POS_ESS<15 "
            if ds_ess < 0.70 * len(d):
                flag += "DATASET_ESS<0.70N "
            print(f"[arm {arm} / {which}] N={len(d)}  dataset ESS={ds_ess:.0f} ({100*ds_ess/len(d):.1f}%)  "
                  f"w range [{w.min():.3f}, {w.max():.3f}]  Normal-BMI pos w_mean={nb_pos.mean():.3f}  {flag or 'OK'}")
            summary.append({"partition": which, "arm": arm, "bmi": "__DATASET__", "class": -1,
                            "n": len(d), "w_mean": 1.0, "cell_ess": round(ds_ess, 1), "flag": flag.strip()})
    pd.DataFrame(summary).to_csv(OUT / "weights_summary.csv", index=False)
    print(f"\nWrote {OUT}/weights_arm{{A,B}}_{{train,propertrain}}.csv and weights_summary.csv")


if __name__ == "__main__":
    main()
