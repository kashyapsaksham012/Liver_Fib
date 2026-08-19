"""
phase6_06_artifact_manifest.py
Phase 6 Part 22: manifest of every Uncertainty artifact with SHA-256 hash.
"""
import sys
import hashlib
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase3_common import ROOT

RESULTS_DIR = ROOT / "results" / "uncertainty"
REFIT_DIR = ROOT / "models" / "phase6_conformal_refit"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

rows = []
for f in sorted(RESULTS_DIR.rglob("*")):
    if f.is_dir() or f.name == "uncertainty_artifact_manifest.csv":
        continue
    rows.append({"path": str(f.relative_to(ROOT)), "sha256": sha256(f), "category": "results"})
for f in sorted(REFIT_DIR.glob("*.joblib")):
    rows.append({"path": str(f.relative_to(ROOT)), "sha256": sha256(f), "category": "refit_model"})

out = pd.DataFrame(rows)
out.to_csv(RESULTS_DIR / "uncertainty_artifact_manifest.csv", index=False)
print(f"Saved results/uncertainty/uncertainty_artifact_manifest.csv ({len(out)} artifacts)")
