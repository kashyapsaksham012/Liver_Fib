"""
phase4_08_artifact_manifest.py
Phase 4 Part 29: manifest of every Calibration artifact, with SHA-256 hash, source script,
model, protocol version, and commit-group (A = pre-test-set work, B = test-set-touch work;
actual commit hashes for each group are recorded in PHASE4_CALIBRATION_RESULTS_REPORT.md
once the commits exist, since a manifest cannot contain the hash of the commit it is itself
part of). Re-run after the test-set touch to append Group-B rows.
"""
import sys
import hashlib
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_common import ROOT, CALIB_RESULTS_DIR, CALIB_DOC_DIR, CALIBRATION_PROTOCOL_COMMIT, NOW

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

SOURCE_MAP = {
    "phase4_prediction_input_audit.csv": "src/phase4_01_prediction_input_audit.py",
    "phase4_test_set_protection_audit.md": "src/phase4_02_primary_metrics.py (audit doc authored manually, verified by all scripts' data-source discipline)",
    "primary_metrics_by_model.csv": "src/phase4_02_primary_metrics.py",
    "brier_scores.csv": "src/phase4_02_primary_metrics.py",
    "ece_secondary_metric.csv": "src/phase4_03_curves_and_ece.py",
    "calibration_inference.csv": "src/phase4_04_inference.py",
    "recalibration_pre_post_comparison.csv": "src/phase4_05_recalibration.py",
    "probability_distribution_diagnostics.csv": "src/phase4_07_probability_diagnostics.py",
}

rows = []
for f in sorted(CALIB_RESULTS_DIR.rglob("*")):
    if f.is_dir() or f.name == "calibration_artifact_manifest.csv":
        continue
    rel = f.relative_to(ROOT)
    is_test_touch = "test_set_calibration_final" in f.name
    source = SOURCE_MAP.get(f.name, "src/phase4_03_curves_and_ece.py" if "curve_data" in str(f) or "calibration_curve_" in f.name
                              else "src/phase4_05_recalibration.py" if "recalibrated_oof_predictions" in f.name
                              else "src/phase4_09_final_test_set_calibration.py" if is_test_touch
                              else "unknown -- verify")
    rows.append({
        "generated": NOW, "path": str(rel), "sha256": sha256(f),
        "model": next((m for m in ["logistic", "random_forest", "xgboost", "lightgbm", "mlp_balanced", "mlp"] if m in f.name), "all_models"),
        "protocol_commit": CALIBRATION_PROTOCOL_COMMIT,
        "commit_group": "B (test-set touch)" if is_test_touch else "A (pre-test-set work)",
        "source_script": source,
    })

for f in sorted(CALIB_DOC_DIR.glob("*.md")):
    if f.name == "calibration_protocol_commit_record.md" or f.name == "CALIBRATION_PROTOCOL_FREEZE.md":
        continue
    rel = f.relative_to(ROOT)
    rows.append({
        "generated": NOW, "path": str(rel), "sha256": sha256(f), "model": "n/a (documentation)",
        "protocol_commit": CALIBRATION_PROTOCOL_COMMIT, "commit_group": "A (pre-test-set work)",
        "source_script": "manually authored, verified against live command output",
    })

out = pd.DataFrame(rows).sort_values(["commit_group", "path"]).reset_index(drop=True)
out.to_csv(CALIB_RESULTS_DIR / "calibration_artifact_manifest.csv", index=False)
print(out.to_string(index=False))
print(f"\nSaved results/calibration/calibration_artifact_manifest.csv ({len(out)} artifacts)")
