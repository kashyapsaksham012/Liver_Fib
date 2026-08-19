"""
phase4_06_probability_diagnostics.py
Phase 4 Part 16: probability distribution diagnostics for raw OOF predictions. Diagnostic
only -- not used as a model-selection criterion. Computed from the OOF tier only.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_common import CALIB_RESULTS_DIR, PRIMARY_MODELS, SENSITIVITY_MODEL, load_oof_predictions, NOW

rows = []
for name in PRIMARY_MODELS + [SENSITIVITY_MODEL]:
    df = load_oof_predictions(name)
    p = df["predicted_probability"].values
    rows.append({
        "generated": NOW, "model": name,
        "status": "PRIMARY" if name in PRIMARY_MODELS else "SENSITIVITY (MLP_balanced, not primary)",
        "min": round(float(p.min()), 6), "p1": round(float(np.percentile(p, 1)), 6),
        "p5": round(float(np.percentile(p, 5)), 6), "p25": round(float(np.percentile(p, 25)), 6),
        "median": round(float(np.median(p)), 6), "p75": round(float(np.percentile(p, 75)), 6),
        "p95": round(float(np.percentile(p, 95)), 6), "p99": round(float(np.percentile(p, 99)), 6),
        "max": round(float(p.max()), 6), "mean": round(float(p.mean()), 6), "sd": round(float(p.std()), 6),
        "n_below_0.01": int((p < 0.01).sum()), "n_above_0.99": int((p > 0.99).sum()),
        "n_unique_values": int(np.unique(p).size),
    })
out = pd.DataFrame(rows)
out.to_csv(CALIB_RESULTS_DIR / "probability_distribution_diagnostics.csv", index=False)
print(out.to_string(index=False))
print("\nThese are diagnostic observations only -- not used as a model-selection criterion.")
print("Saved results/calibration/probability_distribution_diagnostics.csv")
