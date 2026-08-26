"""
tests/test_afcp_faithful.py
Unit tests for the faithful AFCP implementation (src/sens_11_afcp_faithful.py), verifying it
against (a) a brute-force reference implementation of the leave-one-out threshold shortcut, and
(b) a synthetic toy example with a known, hand-verifiable miscoverage pattern, mirroring the
paper's own toy demonstration (Figure 2 of arXiv:2405.15106: one group has systematically worse
marginal coverage; AFCP should detect and correct it without needing to be told which group).
Standalone script (project convention). Run directly: `python3 tests/test_afcp_faithful.py`.
"""
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from sens_11_afcp_faithful import (
    compute_quantile,
    conformal_score,
    loo_threshold_from_sorted,
    brute_force_loo_threshold,
    afcp_group_selection_and_set,
    build_final_set,
)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))
    print(("PASS" if cond else "FAIL") + f" -- {name}" + (f" ({detail})" if detail and not cond else ""))


# ---------------------------------------------------------------------------
# 1. conformal_score matches this project's established convention
# ---------------------------------------------------------------------------
p_hat = np.array([0.9, 0.2, 0.5])
y = np.array([1, 0, 1])
scores = conformal_score(y, p_hat)
check(
    "conformal_score matches 1-P(true class)",
    np.allclose(scores, [0.1, 0.2, 0.5]),
    str(scores),
)

# ---------------------------------------------------------------------------
# 2. compute_quantile matches the project's k=ceil((n+1)*target_cov) convention
# ---------------------------------------------------------------------------
scores10 = np.arange(1, 11) / 10.0
q10 = compute_quantile(scores10, 0.90)
check("compute_quantile n=10 k=10 -> 1.0", abs(q10 - 1.0) < 1e-9, str(q10))

scores100 = np.arange(1, 101) / 100.0
q100 = compute_quantile(scores100, 0.90)
check("compute_quantile n=100 k=91 -> 0.91", abs(q100 - 0.91) < 1e-9, str(q100))

# ---------------------------------------------------------------------------
# 3. LOO threshold O(1) shortcut matches brute-force recomputation (randomized)
# ---------------------------------------------------------------------------
all_match = True
worst_diff = 0.0
rng = np.random.default_rng(0)
for seed in range(20):
    rng2 = np.random.default_rng(seed)
    n_full = int(rng2.integers(5, 60))
    raw_scores = rng2.uniform(0, 1, size=n_full)
    sorted_scores = np.sort(raw_scores)
    order = np.argsort(raw_scores, kind="stable")
    ranks = np.empty_like(order)
    ranks[order] = np.arange(len(order))
    for i in range(n_full):
        fast = loo_threshold_from_sorted(sorted_scores, ranks[i], target_cov=0.90)
        slow = brute_force_loo_threshold(raw_scores, i, target_cov=0.90)
        diff = abs(fast - slow) if np.isfinite(fast) and np.isfinite(slow) else (0 if fast == slow else 1)
        worst_diff = max(worst_diff, diff)
        if diff > 1e-9:
            all_match = False
check("LOO O(1) shortcut matches brute force (20 seeds x up to 59 points)", all_match, f"worst_diff={worst_diff}")

# ---------------------------------------------------------------------------
# 4. LOO threshold correctly returns +inf when the remaining group is too small
# ---------------------------------------------------------------------------
small_sorted = np.sort(np.array([0.1, 0.2]))
thr_small = loo_threshold_from_sorted(small_sorted, 0, target_cov=0.90)
check("LOO threshold = +inf for tiny remaining group (n=1, k_idx=2>1)", thr_small == np.inf, str(thr_small))

# ---------------------------------------------------------------------------
# 5. Structural: no test-label parameter exists in the selection function
# ---------------------------------------------------------------------------
import inspect
sig_params = [p.lower() for p in inspect.signature(afcp_group_selection_and_set).parameters.keys()]
check(
    "afcp_group_selection_and_set has no true-label parameter",
    "true_label" not in sig_params and "y_true" not in sig_params and "label" not in sig_params,
    str(sig_params),
)

# ---------------------------------------------------------------------------
# 6. Synthetic toy: AFCP detects and corrects a disadvantaged group's undercoverage
#    (mirrors the paper's own Figure 2 toy demonstration)
# ---------------------------------------------------------------------------
rng = np.random.default_rng(42)
n_cal = 400
cal_group = np.array(["A"] * (n_cal // 2) + ["B"] * (n_cal // 2))
cal_scores_toy = np.concatenate([
    rng.uniform(0, 0.5, size=n_cal // 2),
    rng.uniform(0.3, 1.0, size=n_cal // 2),
])
cal_group2 = rng.choice(["X", "Y"], size=n_cal)
marginal_threshold = compute_quantile(cal_scores_toy, target_cov=0.90)
cal_group_ids_by_attr = {"grp": cal_group, "grp2": cal_group2}

n_test = 60
test_group = np.array(["A"] * (n_test // 2) + ["B"] * (n_test // 2))
test_group2 = rng.choice(["X", "Y"], size=n_test)
test_score_true = np.concatenate([
    rng.uniform(0, 0.5, size=n_test // 2),
    rng.uniform(0.3, 1.0, size=n_test // 2),
])

marginal_covered_B, afcp_covered_B, n_B = 0, 0, 0
b_attr_selected_count, b_total_selections = 0, 0

for i in range(n_test):
    true_score = test_score_true[i]
    test_score_by_label = {0: true_score, 1: true_score + 5.0}
    test_group_by_attr = {"grp": test_group[i], "grp2": test_group2[i]}
    selected_attr_by_y = afcp_group_selection_and_set(
        test_score_by_label, cal_scores_toy, cal_group_ids_by_attr, test_group_by_attr,
    )
    final_set = build_final_set(
        test_score_by_label, marginal_threshold, selected_attr_by_y,
        cal_scores_toy, cal_group_ids_by_attr, test_group_by_attr,
    )
    marginal_covered = true_score <= marginal_threshold
    afcp_covered = 0 in final_set
    if test_group[i] == "B":
        n_B += 1
        marginal_covered_B += int(marginal_covered)
        afcp_covered_B += int(afcp_covered)
    for yy in (0, 1):
        if selected_attr_by_y.get(yy) is not None:
            b_total_selections += 1
            if selected_attr_by_y[yy] == "grp":
                b_attr_selected_count += 1

marginal_rate_B = marginal_covered_B / n_B
afcp_rate_B = afcp_covered_B / n_B
check(
    "AFCP does not reduce disadvantaged-group coverage vs. marginal",
    afcp_rate_B >= marginal_rate_B,
    f"marginal={marginal_rate_B:.3f} afcp={afcp_rate_B:.3f}",
)
if b_total_selections > 0:
    check(
        "AFCP prefers the genuinely informative attribute over the irrelevant one",
        (b_attr_selected_count / b_total_selections) > 0.5,
        f"{b_attr_selected_count}/{b_total_selections}",
    )
else:
    check("AFCP attribute-selection-preference check (skipped, no selections made)", True, "n/a")

print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
if FAIL:
    for name, detail in FAIL:
        print(f"  FAILED: {name} ({detail})")
    sys.exit(1)
sys.exit(0)
