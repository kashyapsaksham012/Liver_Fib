"""
tests/test_prov_closure.py
Amendment #20 provenance-closure checks. Standalone script (project convention):
`python3 tests/test_prov_closure.py`; exits 1 if any check fails.

  1. src/prov_01 regenerates results/uncertainty/intersectional_coverage_ci.csv byte-identically.
  2. results/tables/model_artifact_manifest.csv covers every committed models/**/*.joblib,
     hashes match on disk, and the five phase-6 entries match conformal_model_refit_registry.csv.
"""
import sys
import csv
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))


# ── 1. intersectional_coverage_ci.csv derivation is byte-identical ──────────────
r = subprocess.run([sys.executable, str(ROOT / "src" / "prov_01_derive_intersectional_coverage_ci.py")],
                   capture_output=True, text=True)
check("prov_01_runs_clean", r.returncode == 0, r.stdout + r.stderr)
check("prov_01_reports_byte_identical", "BYTE-IDENTICAL" in r.stdout, r.stdout)

# ── 2. model_artifact_manifest.csv ────────────────────────────────────────────
MAN = ROOT / "results" / "tables" / "model_artifact_manifest.csv"
check("manifest_exists", MAN.exists())
if MAN.exists():
    rows = list(csv.DictReader(open(MAN)))
    manifest_paths = {row["artifact_path"] for row in rows}

    disk_joblibs = {p.relative_to(ROOT).as_posix()
                    for p in (ROOT / "models").rglob("*.joblib")}
    check("manifest_covers_all_joblibs", manifest_paths == disk_joblibs,
          f"only_in_manifest={manifest_paths - disk_joblibs} ; "
          f"only_on_disk={disk_joblibs - manifest_paths}")

    bad_hash = []
    for row in rows:
        p = ROOT / row["artifact_path"]
        if not p.exists():
            bad_hash.append(f"{row['artifact_path']} MISSING")
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != row["sha256"]:
            bad_hash.append(f"{row['artifact_path']} hash drift")
        if str(p.stat().st_size) != str(row["size_bytes"]):
            bad_hash.append(f"{row['artifact_path']} size drift")
    check("manifest_hashes_and_sizes_current", not bad_hash, "; ".join(bad_hash))

    refit_reg = ROOT / "results" / "uncertainty" / "conformal_model_refit_registry.csv"
    if refit_reg.exists():
        existing = {rr["artifact_path"]: rr["artifact_hash"]
                    for rr in csv.DictReader(open(refit_reg))}
        man = {row["artifact_path"]: row["sha256"] for row in rows}
        mism = [k for k in existing if k in man and existing[k] != man[k]]
        check("manifest_matches_conformal_refit_registry", not mism, str(mism))

    check("phase3_baseline_rows_have_seed_42",
          all(row["seed"] == "42" for row in rows
              if row["group"] == "phase3_baseline" and "mlp_balanced" not in row["artifact_path"]))

# ── report ────────────────────────────────────────────────────────────────────
print("PROVENANCE-CLOSURE TEST RESULTS: "
      f"{len(PASS)} passed, {len(FAIL)} failed")
print("=" * 70)
for n, d in PASS:
    print(f"  PASS: {n}")
for n, d in FAIL:
    print(f"  FAIL: {n}" + (f"  --  {d[:300]}" if d else ""))

sys.exit(1 if FAIL else 0)
