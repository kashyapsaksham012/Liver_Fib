"""
cb_05_matched_stiffness.py
E2: matched-stiffness regression for FIB-4, mirroring prepub_02_vcte_bias_sensitivity.py's
C4 exactly -- same band (8.2 <= LUXSMED < 12 kPa), same groups (Normal, Obese only), same
locked-test-set restriction, same OLS specification (score ~ 1 + LUXSMED + is_obese) and the
same t-test on the is_obese coefficient.

Two dependent-variable versions are reported, both from the identical band/sample:
  (a) raw FIB-4 score (native units) -- the primary, assumption-free version; FIB-4's native
      scale is not directly comparable in magnitude to the ML models' 0.19-0.33 probability-
      unit result, so this number should not be quoted side-by-side with that range without
      the unit noted.
  (b) the auxiliary-logistic probability from cb_04 (same probability units as the five ML
      models) -- included only so a same-units comparison is possible; it inherits
      cb_04's auxiliary-fit caveat.

Output: results/clinical_baselines/fib4_matched_stiffness.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT

OUT_DIR = ROOT / "results" / "clinical_baselines"
scores = pd.read_csv(OUT_DIR / "fib4_scores.csv")
test = scores[scores["split"] == "test"].copy()
pred_sets = pd.read_csv(OUT_DIR / "fib4_test_prediction_sets.csv")[["SEQN", "auxiliary_probability"]]
test = test.merge(pred_sets, on="SEQN", how="inner")
assert len(test) == 2146

band = test[(test.LUXSMED >= 8.2) & (test.LUXSMED < 12) &
            test.bmi_group_final.isin(["Normal", "Obese"])].copy()
band["is_obese"] = (band.bmi_group_final == "Obese").astype(int)
print(f"Matched-stiffness band (8.2-12 kPa, Normal+Obese, locked test set): N={len(band)} "
      f"(Normal={int((band.is_obese==0).sum())}, Obese={int((band.is_obese==1).sum())})")

def ols_is_obese(y, band):
    X = np.column_stack([np.ones(len(band)), band["LUXSMED"].to_numpy(), band["is_obese"].to_numpy()])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(band) - 3
    se = np.sqrt(np.sum(resid**2) / dof * np.diag(np.linalg.inv(X.T @ X)))
    t_obese = beta[2] / se[2]
    p_obese = 2 * (1 - stats.t.cdf(abs(t_obese), dof))
    return beta[2], se[2], t_obese, p_obese

rows = []
for label, col in [("fib4_raw_score", "fib4"), ("auxiliary_probability", "auxiliary_probability")]:
    y = band[col].to_numpy()
    beta_obese, se, t, p = ols_is_obese(y, band)
    band[f"lsm_bin"] = pd.cut(band["LUXSMED"], bins=np.arange(8.0, 12.5, 0.5))
    binned = band.groupby(["lsm_bin", "bmi_group_final"], observed=True)[col].mean().unstack()
    mean_diff = float((binned.get("Obese") - binned.get("Normal")).mean()) if "Obese" in binned and "Normal" in binned else np.nan
    rows.append({
        "score_name": "FIB-4", "dependent_variable": label, "n_band": len(band),
        "beta_is_obese": round(float(beta_obese), 4), "se": round(float(se), 4),
        "t": round(float(t), 2), "p_value": round(float(p), 6),
        "mean_diff_obese_minus_normal_matched_stiffness_binned": round(mean_diff, 4),
    })
    print(f"[{label}] beta_is_obese={beta_obese:.4f} (SE={se:.4f}, t={t:.2f}, p={p:.2e}), "
          f"binned mean diff={mean_diff:.4f}")

pd.DataFrame(rows).to_csv(OUT_DIR / "fib4_matched_stiffness.csv", index=False)
print("\nSaved results/clinical_baselines/fib4_matched_stiffness.csv")
