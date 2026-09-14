"""
cb_02_discrimination.py
E1 (part 1): FIB-4 discrimination on the locked test set, mirroring phase3_06's method
exactly -- Youden's J threshold selected on the TRAINING partition only, locked test set
touched only once, afterward, to compute AUROC/PR-AUC with the same 2000-resample
percentile bootstrap (seed 42) and the same confusion-matrix-derived metrics.

FIB-4 is a fixed formula, not a fitted model, so there is no OOF/CV step to select the
threshold from (nothing is being trained). The direct analog of "threshold from training
data, never touching test" is: compute Youden's J directly on the full training partition
(train_ids.csv, N=5007) using the raw FIB-4 score, then apply that one threshold to the
locked test set. AUROC/PR-AUC themselves need no threshold and are computed directly on the
locked test set's continuous FIB-4 score.

Output: results/clinical_baselines/fib4_discrimination.csv
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve, confusion_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT, RANDOM_SEED, PRIMARY_OUTCOME_COL
from phase3_06_threshold_and_test_eval import youdens_j_threshold, bootstrap_ci, N_BOOTSTRAP

OUT_DIR = ROOT / "results" / "clinical_baselines"
scores = pd.read_csv(OUT_DIR / "fib4_scores.csv")

train = scores[scores["split"].isin(["proper_train", "conformal_calibration"])]
test = scores[scores["split"] == "test"]
assert len(train) == 5007 and len(test) == 2146

threshold = youdens_j_threshold(train[PRIMARY_OUTCOME_COL].values, train["fib4"].values)
print(f"FIB-4 Youden threshold (from training partition, N={len(train)}): {threshold:.4f}")

y_test = test[PRIMARY_OUTCOME_COL].values
score_test = test["fib4"].values
pred_class = (score_test >= threshold).astype(int)

auc = roc_auc_score(y_test, score_test)
pr_auc = average_precision_score(y_test, score_test)
tn, fp, fn, tp = confusion_matrix(y_test, pred_class).ravel()
sens = tp / (tp + fn) if (tp + fn) else np.nan
spec = tn / (tn + fp) if (tn + fp) else np.nan
ppv = tp / (tp + fp) if (tp + fp) else np.nan
npv = tn / (tn + fn) if (tn + fn) else np.nan
f1 = 2 * ppv * sens / (ppv + sens) if (ppv and sens and (ppv + sens)) else np.nan

auc_lo, auc_hi = bootstrap_ci(y_test, score_test, roc_auc_score, n_boot=N_BOOTSTRAP, seed=RANDOM_SEED)
prauc_lo, prauc_hi = bootstrap_ci(y_test, score_test, average_precision_score, n_boot=N_BOOTSTRAP, seed=RANDOM_SEED)

row = {
    "score_name": "FIB-4", "test_n": len(test), "threshold": round(threshold, 4),
    "roc_auc": round(auc, 4), "roc_auc_95ci_low": auc_lo, "roc_auc_95ci_high": auc_hi,
    "pr_auc": round(pr_auc, 4), "pr_auc_95ci_low": prauc_lo, "pr_auc_95ci_high": prauc_hi,
    "sensitivity": round(sens, 4), "specificity": round(spec, 4), "ppv": round(ppv, 4),
    "npv": round(npv, 4), "f1": round(f1, 4), "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
    "ci_method": f"percentile bootstrap, n={N_BOOTSTRAP} resamples, seed={RANDOM_SEED}",
    "threshold_method": "Youden's J on raw FIB-4 score, training partition (N=5007) only, test set not accessed",
}
pd.DataFrame([row]).to_csv(OUT_DIR / "fib4_discrimination.csv", index=False)

# also save per-participant test predictions, mirroring test_predictions_<model>.csv format
pred_df = pd.DataFrame({"SEQN": test["SEQN"].values, "true_target": y_test,
                         "fib4_score": score_test, "predicted_class": pred_class,
                         "threshold_used": threshold})
pred_df.to_csv(OUT_DIR / "fib4_test_predictions.csv", index=False)

print(f"FIB-4: TEST ROC-AUC={auc:.4f} [{auc_lo},{auc_hi}], PR-AUC={pr_auc:.4f} [{prauc_lo},{prauc_hi}], "
      f"sens={sens:.3f}, spec={spec:.3f}, ppv={ppv:.3f}, npv={npv:.3f}")
print("Saved results/clinical_baselines/fib4_discrimination.csv")
print("Saved results/clinical_baselines/fib4_test_predictions.csv")
