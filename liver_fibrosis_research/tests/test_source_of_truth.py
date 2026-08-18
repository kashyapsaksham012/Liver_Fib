"""
Pre-Calibration source-of-truth duplication test.

Generated 2026-08-18 as part of the Pre-Calibration Closure audit. Purpose: several
scientific constants (primary predictor list, primary outcome threshold, MLP hyperparameter
grid) are independently re-typed as literals in multiple files rather than imported from a
single module (see results/pre_calibration/source_of_truth_matrix.csv for the full audit).
No active conflicts were found -- all copies currently agree -- but nothing previously
enforced that agreement automatically. This test makes that enforcement real: it fails loudly
if any copy is ever edited without updating the others.

This test does NOT re-verify claims already closed in prior audit passes (cohort counts,
84-configuration total, 7-amendment count, etc.) -- see FINAL_PRE_CALIBRATION_CLOSURE_REPORT.md
Part (B) for that prior evidence.
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

PASS = []
FAIL = []


def check(name, condition, detail=""):
    if condition:
        PASS.append(name)
    else:
        FAIL.append(f"{name}: {detail}")


def extract_list_literal(file_path, var_name):
    """Extract a top-level or in-function list-of-strings assignment via AST, robust to
    the assignment appearing inside a function body (not just module level)."""
    src = (SRC / file_path).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    if isinstance(node.value, ast.List):
                        return [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
    return None


def extract_scalar_literal(file_path, var_name):
    src = (SRC / file_path).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    if isinstance(node.value, ast.Constant):
                        return node.value.value
    return None


def extract_dict_literal(file_path, containing_key_snippet):
    """Extract a dict-literal grid assigned to `grid = {...}` whose source text contains
    containing_key_snippet, returning the raw source text of the dict for structural
    (not just value) comparison."""
    src = (SRC / file_path).read_text()
    tree = ast.parse(src)
    matches = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "grid" and isinstance(node.value, ast.Dict):
                    seg = ast.get_source_segment(src, node.value)
                    if containing_key_snippet in seg:
                        matches.append(seg)
    return matches


# --- Check 1: primary predictor list identical across all 5 independent copies ---
PREDICTOR_SITES = [
    ("phase2_02_outcome_predictors_leakage.py", "PRIMARY_PREDICTORS"),
    ("phase2_04_build_analysis_dataset.py", "PRIMARY_PREDICTORS"),
    ("phase2_05_premodeling_checklist.py", "predictors"),
    ("phase3_common.py", "PRIMARY_PREDICTORS"),
    ("phase3_10_handoff_reverification.py", "predictors"),
]
lists = {}
for fname, var in PREDICTOR_SITES:
    val = extract_list_literal(fname, var)
    check(f"predictor-list-extractable:{fname}", val is not None and len(val) == 10, f"got {val}")
    lists[fname] = val

reference = lists[PREDICTOR_SITES[0][0]]
for fname, _ in PREDICTOR_SITES[1:]:
    check(
        f"predictor-list-matches-reference:{fname}",
        lists[fname] == reference,
        f"{fname}={lists[fname]} vs reference({PREDICTOR_SITES[0][0]})={reference}",
    )

# --- Check 2: primary outcome threshold identical in the two independent definitions ---
t1 = extract_scalar_literal("phase2_02_outcome_predictors_leakage.py", "PRIMARY_THRESHOLD")
t2 = extract_scalar_literal("phase2_03_design_and_feasibility.py", "PRIMARY_THRESHOLD")
check("outcome-threshold-extractable", t1 is not None and t2 is not None, f"t1={t1} t2={t2}")
check("outcome-threshold-matches", t1 == t2 == 8.2, f"phase2_02={t1}, phase2_03={t2}, expected 8.2")

# --- Check 3: MLP hyperparameter grid identical between phase3_05 (primary) and phase3_13 (sensitivity) ---
grid_05 = extract_dict_literal("phase3_05_train_and_tune.py", "hidden_layer_sizes")
grid_13 = extract_dict_literal("phase3_13_imbalance_audit_and_mlp_sensitivity.py", "hidden_layer_sizes")
check("mlp-grid-found-phase3_05", len(grid_05) == 1, f"found {len(grid_05)} candidate grids")
check("mlp-grid-found-phase3_13", len(grid_13) == 1, f"found {len(grid_13)} candidate grids")
if grid_05 and grid_13:
    # Compare structurally (parsed values), not raw text, so whitespace differences don't false-fail
    d05 = ast.literal_eval(grid_05[0])
    d13 = ast.literal_eval(grid_13[0])
    check("mlp-grid-values-match", d05 == d13, f"phase3_05={d05} vs phase3_13={d13}")

# --- Check 4: variable metadata single-source (no second VAR_METADATA definition anywhere in src/) ---
sites_with_var_metadata = []
for f in SRC.glob("*.py"):
    if re.search(r"^VAR_METADATA\s*=", f.read_text(), re.MULTILINE):
        sites_with_var_metadata.append(f.name)
check(
    "var-metadata-single-source",
    sites_with_var_metadata == ["_common.py"],
    f"found VAR_METADATA defined in: {sites_with_var_metadata}",
)

# --- Check 5: cohort-mask historical scripts confirmed inert (not imported by any phase2_*/phase3_* script) ---
historical_scripts = ["03_audit_lux_demo_bmx.py", "12_subgroup_outcome_feasibility.py", "18_generate_phase1_report.py"]
live_scripts = [f for f in SRC.glob("phase2_*.py")] + [f for f in SRC.glob("phase3_*.py")]
referenced = []
for hist in historical_scripts:
    stem = hist.replace(".py", "")
    for live in live_scripts:
        if stem in live.read_text():
            referenced.append((hist, live.name))
check("historical-cohort-scripts-inert", referenced == [], f"unexpected references found: {referenced}")

print(f"\n{'='*70}\nSOURCE-OF-TRUTH TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name in PASS:
    print(f"  PASS: {name}")
for msg in FAIL:
    print(f"  FAIL: {msg}")

if FAIL:
    sys.exit(1)
print("\nALL SOURCE-OF-TRUTH CHECKS PASSED -- no active conflicts detected.")
sys.exit(0)
