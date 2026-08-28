"""
prov_01_derive_intersectional_coverage_ci.py
Amendment #20 (provenance closure). Regenerates

    results/uncertainty/intersectional_coverage_ci.csv

from artifacts that DO have a committed generating script, and asserts the result is
byte-identical to the committed file. The committed CSV had entered the repository via a
bulk "finalize" commit (142595d) with only a `ci_method` note and no producer script; this
closes that gap without changing a single value.

Inputs (both frozen, both with committed lineage):
  - results/mitigation/bmi_age_overlap_four_way_analysis.csv
      Written by src/phase7_05_bmi_age_overlap_analysis.py, which re-partitions the frozen
      Phase-6 "Commit C" artifact results/uncertainty/test_set_prediction_sets.csv
      (src/phase6_04_final_test_touch.py; raw refit-model probabilities, frozen global
      split-conformal threshold, NO Platt recalibration) into the four BMI x Age cells.
      Its "Intersection (Obese AND 60+)" rows carry `baseline_coverage` (global threshold)
      and `mitigated_coverage` (frozen Phase-7 Mondrian recalibration) for N = 294.
  - The Wilson score interval, identical formula to src/phase6_04_final_test_touch.py
    wilson_ci() (Amendment #10), reused here for consistency.

This script loads no model, reopens no test data, and computes no coverage proportion: the
covered counts are read from the frozen four-way file. It only derives the integer covered
count (coverage x N, rounded) and the Wilson CI, then formats the CSV.

Run:  python3 src/prov_01_derive_intersectional_coverage_ci.py [--write]
      (without --write it verifies only; with --write it also rewrites the file in place,
       which is a no-op when the check passes)
"""
import sys
import csv
import math
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOURWAY = ROOT / "results" / "mitigation" / "bmi_age_overlap_four_way_analysis.csv"
TARGET = ROOT / "results" / "uncertainty" / "intersectional_coverage_ci.csv"

CI_LEVEL = 0.95
MODEL_ORDER = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
INTERSECTION_LABEL = "Intersection (Obese AND 60+)"
CI_METHOD = ("Wilson score interval, 95% (same formula as phase6_04_final_test_touch.py "
             "wilson_ci(), reused for consistency)")


def _z(level):
    try:
        from scipy import stats  # matches phase6_04_final_test_touch.py exactly
        return float(stats.norm.ppf(1 - (1 - level) / 2))
    except Exception:
        # scipy.stats.norm.ppf(0.975); the constant is what scipy returns.
        print("  (scipy unavailable — using the constant z_{0.975} = 1.959963984540054)")
        return 1.959963984540054


Z = _z(CI_LEVEL)


def wilson_ci(k, n):
    """Identical to src/phase6_04_final_test_touch.py wilson_ci()."""
    if n == 0:
        return (None, None)
    phat = k / n
    denom = 1 + Z ** 2 / n
    center = (phat + Z ** 2 / (2 * n)) / denom
    half = (Z * math.sqrt(phat * (1 - phat) / n + Z ** 2 / (4 * n ** 2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def build():
    fourway = {}
    with open(FOURWAY) as f:
        for r in csv.DictReader(f):
            if r["subgroup_category"] == INTERSECTION_LABEL:
                fourway[r["model"]] = r
    missing = [m for m in MODEL_ORDER if m not in fourway]
    if missing:
        sys.exit(f"CRITICAL: intersection rows missing for {missing} in {FOURWAY.name}")

    lines = ["model,stage,n,n_covered,coverage,ci_lower,ci_upper,ci_method"]
    for m in MODEL_ORDER:
        r = fourway[m]
        n = int(r["n"])
        for stage, key in (("baseline", "baseline_coverage"),
                           ("post_mitigation", "mitigated_coverage")):
            k = round(float(r[key]) * n)          # frozen covered count
            cov = round(k / n, 6)
            lo, hi = wilson_ci(k, n)
            lines.append(f'{m},{stage},{n},{k},{cov},{round(lo, 6)},{round(hi, 6)},"{CI_METHOD}"')
    return "\n".join(lines) + "\n"


def main():
    derived = build()
    frozen = TARGET.read_bytes()
    d_hash = hashlib.sha256(derived.encode()).hexdigest()
    f_hash = hashlib.sha256(frozen).hexdigest()

    print(f"derived  sha256: {d_hash}")
    print(f"frozen   sha256: {f_hash}")

    if derived.encode() == frozen:
        print("PASS: derivation is BYTE-IDENTICAL to the committed "
              "results/uncertainty/intersectional_coverage_ci.csv")
        if "--write" in sys.argv:
            TARGET.write_text(derived)
            print("  (--write: file rewritten in place; no-op, identical bytes)")
        return 0

    print("FAIL: derivation does not match the committed file.")
    for i, (a, b) in enumerate(zip(frozen.decode().splitlines(), derived.splitlines())):
        if a != b:
            print(f"  line {i}:\n    frozen : {a}\n    derived: {b}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
