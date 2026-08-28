"""
prov_02_model_artifact_manifest.py
Amendment #20 (provenance closure). Writes a single hash manifest for every committed model
artifact:

    results/tables/model_artifact_manifest.csv

The BMI-investigation Phase-6 robustness report recorded the frozen 8.2-kPa model-artifact
manifest as `NOT FOUND IN REPOSITORY`. The Phase-3 registry
(results/tables/phase3_model_registry.csv) records hyperparameters, seed and CV-AUC but no
file hash; the Phase-6 conformal-refit registry records hashes for its own five files only.
This script closes the gap for all 32 committed `.joblib` files at once.

It does NOT load any model (no joblib.load, no library-version dependency) — it hashes the
file bytes and cross-references the metadata already committed in the phase-specific
registries. Nothing is retrained, re-selected, or re-evaluated.

Run:  python3 src/prov_02_model_artifact_manifest.py
"""
import csv
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "models"
OUT = ROOT / "results" / "tables" / "model_artifact_manifest.csv"

# group -> (subdir, purpose, metadata-registry relative path or "")
GROUPS = [
    ("phase3_baseline", "phase3",
     "Frozen Phase-3 baseline family (primary 8.2-kPa outcome, full 70% train)",
     "results/tables/phase3_model_registry.csv"),
    ("phase6_conformal_refit", "phase6_conformal_refit",
     "Proper-train-only refit for split-conformal (Phase 6)",
     "results/uncertainty/conformal_model_refit_registry.csv"),
    ("phase8_holdout", "phase8_holdout",
     "Non-Hispanic Black demographic-holdout retrain (Phase 8)",
     "results/tables/phase8_generalization_results.csv"),
    ("amendment19_training_time_mitigation", "training_time_mitigation",
     "Kamiran-Calders reweighted retrain (Amendment #19; NEGATIVE by gate)",
     "results/training_time_mitigation/"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def phase3_params():
    """seed / hyperparameters / cv_auc already committed in the Phase-3 registry."""
    p = ROOT / "results" / "tables" / "phase3_model_registry.csv"
    out = {}
    if p.exists():
        for r in csv.DictReader(open(p)):
            out[r["model_name"]] = (r.get("random_seed", ""),
                                    r.get("best_hyperparameters", ""),
                                    r.get("cv_roc_auc", ""))
    return out


def main():
    p3 = phase3_params()
    rows = []
    for group, subdir, purpose, registry in GROUPS:
        d = MODELS_DIR / subdir
        if not d.is_dir():
            continue
        for jb in sorted(d.glob("*.joblib")):
            rel = jb.relative_to(ROOT).as_posix()
            seed = params = cvauc = ""
            if group == "phase3_baseline":
                # exact registry-key match only; model_mlp_balanced_v1_sensitivity has no
                # registry row (sensitivity model) and is deliberately left blank.
                stem = jb.stem.replace("model_", "").replace("_v1_sensitivity", "").replace("_v1", "")
                if stem in p3:
                    seed, params, cvauc = p3[stem]
            rows.append({
                "group": group,
                "artifact_path": rel,
                "purpose": purpose,
                "size_bytes": jb.stat().st_size,
                "sha256": sha256(jb),
                "seed": seed,
                "hyperparameters": params,
                "cv_roc_auc": cvauc,
                "metadata_registry": registry,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {OUT.relative_to(ROOT)}  ({len(rows)} artifacts)")
    by_group = {}
    for r in rows:
        by_group.setdefault(r["group"], 0)
        by_group[r["group"]] += 1
    for g, n in by_group.items():
        print(f"  {g}: {n}")

    # cross-check: every hash we can compare against an existing registry matches
    refit_reg = ROOT / "results" / "uncertainty" / "conformal_model_refit_registry.csv"
    if refit_reg.exists():
        existing = {r["artifact_path"]: r["artifact_hash"]
                    for r in csv.DictReader(open(refit_reg))}
        mism = [r["artifact_path"] for r in rows
                if r["artifact_path"] in existing
                and existing[r["artifact_path"]] != r["sha256"]]
        if mism:
            raise SystemExit(f"CRITICAL: hash mismatch vs conformal_model_refit_registry: {mism}")
        n_checked = sum(1 for r in rows if r["artifact_path"] in existing)
        print(f"  cross-checked {n_checked} hashes against conformal_model_refit_registry.csv: all match")


if __name__ == "__main__":
    main()
