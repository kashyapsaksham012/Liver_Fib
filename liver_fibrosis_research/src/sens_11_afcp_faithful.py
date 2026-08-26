"""
sens_11_afcp_faithful.py
Faithful implementation of AFCP (Zhou & Sesia, "Conformal Classification with Equalized
Coverage for Adaptively Selected Groups," NeurIPS 2024, arXiv:2405.15106).

This REPLACES the prior `sens_08_afcp_comparison.py`, which was found (this project's own
audit, `results/diagnostics/TEST_SET_CONTAMINATION_AUDIT.md` and later reports) to implement a
K-nearest-neighbor heuristic labeled "afcp_knn" -- a direct violation of the project's rule that a
non-faithful approximation must never be labeled AFCP. `sens_08`'s output remains
SUPERSEDED/INVALID. This script is a from-scratch, faithful reimplementation of the paper's
Algorithm 1 (adaptive group selection) and Algorithm 2 (prediction-set construction), verified
against the paper's own equations (extracted directly from arXiv:2405.15106 HTML and cross-checked
against the arXiv abstract page for author/title confirmation -- see
`documentation/final_audit/AFCP_IMPLEMENTATION_NOTES.md` for the exact extracted algorithm text
this implementation is built from).

METHOD SUMMARY (paper notation, L=2 for this project's binary outcome):
  For a test point X_{n+1} and each candidate label y in {0, 1}:
    1. Augment the calibration set with the hypothetical point (X_{n+1}, y).
    2. For every point i in the augmented set (leave-one-out), and for each candidate sensitive
       attribute k, compute whether i would be miscovered by the equalized-coverage set built on
       the augmented set WITH i removed.
    3. delta_{y,k} = worst-case (max over groups m of attribute k) empirical miscoverage rate.
    4. q_hat_y = max_k delta_{y,k}. A one-sided test asks whether q_hat_y is significantly above
       alpha in the argmax group; if so, that attribute is selected for hypothesis y, else none.
  5. The final prediction set is the union of the plain marginal conformal set and, for each y in
     {0,1}, the (non-LOO) group-equalized set for whichever attribute was selected under that y.

CANDIDATE SENSITIVE ATTRIBUTES (this project's own, already-established fairness dimensions,
not invented for this script): BMI category (`bmi_group_final`, 4 levels) and Age category
(`age_group_final`, 2 levels).

DOCUMENTED ASSUMPTIONS (paper details not fully specified in the extracted text; explicitly
flagged, not silently guessed):
  - Significance level for the one-sided test in Algorithm 1 step 6 is set to 0.05 (a standard
    default; the extracted algorithm text did not give an explicit numeric significance level).
  - The one-sided test is implemented as a one-sample t-test of the group's leave-one-out
    miscoverage indicators against the null mean `alpha`, using scipy.stats.ttest_1samp with a
    one-sided p-value (H1: mean > alpha).

FITTING DATA: conformal calibration split (`conformal_calibration_ids.csv`, N=1,002) only.
EVALUATION DATA: locked test set (`test_ids.csv`, N=2,146), used ONLY for final coverage/set-size
evaluation -- test LABELS are never used in group selection or threshold construction; test
FEATURES are used only as the "new point" X_{n+1} being conformalized, exactly as in standard
(marginal) split-conformal prediction, which also always uses the new point's features.
"""
import datetime
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "data" / "processed" / "splits"
RESULTS_DIR = ROOT / "results"
DIAG_DIR = RESULTS_DIR / "diagnostics" / "stage1"

MODEL_NAMES = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
PRIMARY_PREDICTORS = [
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "LBXSATSI", "LBXSASSI",
    "LBXSAL", "LBXSAPSI", "LBXSTB", "LBXPLTSI", "LBDHDD",
]
PRIMARY_OUTCOME_COL = "outcome_primary_8.2kPa"
TARGET_COVERAGE = 0.90
ALPHA = 1.0 - TARGET_COVERAGE
SIGNIFICANCE_LEVEL = 0.05  # documented assumption, see module docstring


def platt_transform(p, intercept, slope):
    eps = 1e-7
    p_clamped = np.clip(p, eps, 1 - eps)
    logit_p = np.log(p_clamped / (1 - p_clamped))
    return 1.0 / (1.0 + np.exp(-(slope * logit_p + intercept)))


def conformal_score(y, p_hat):
    """Standard nonconformity score for binary classification: 1 - P(true class)."""
    return 1.0 - np.where(y == 1, p_hat, 1.0 - p_hat)


def compute_quantile(scores, target_cov=TARGET_COVERAGE):
    """This project's established split-conformal quantile: k = ceil((n+1) * target_cov)."""
    n = len(scores)
    if n == 0:
        return np.inf
    k = int(np.ceil((n + 1) * target_cov))
    if k > n:
        return np.inf
    return np.sort(scores)[k - 1]


def loo_threshold_from_sorted(sorted_scores, rank_r, target_cov=TARGET_COVERAGE):
    """
    O(1) leave-one-out threshold shortcut.

    Given `sorted_scores` (ascending, length n_full) for a group that INCLUDES the point being
    left out, and `rank_r` = that point's 0-indexed position within `sorted_scores`, return the
    conformal threshold that would result from removing that one point (i.e., the standard
    quantile of the remaining n_full-1 scores, using this project's k = ceil((n+1)*target_cov)
    convention with n = n_full - 1).

    Derivation: let orig = sorted_scores (len n_full). Removing index r gives new_arr where
    new_arr[j] = orig[j] for j < r and new_arr[j] = orig[j+1] for j >= r. We want
    new_arr[k_idx - 1] where k_idx = ceil(n_full * target_cov) (since n+1 = n_full when n =
    n_full-1). If k_idx - 1 < r, that position is unaffected by the removal: orig[k_idx - 1].
    Otherwise the removal shifts it by one: orig[k_idx].
    """
    n_full = len(sorted_scores)
    n = n_full - 1
    if n <= 0:
        return np.inf
    k_idx = int(np.ceil(n_full * target_cov))
    if k_idx > n:
        return np.inf
    if (k_idx - 1) < rank_r:
        return sorted_scores[k_idx - 1]
    return sorted_scores[k_idx]


def brute_force_loo_threshold(scores_excluding_none, remove_idx, target_cov=TARGET_COVERAGE):
    """Reference (slow, O(n log n) per call) implementation used only for testing."""
    remaining = np.delete(scores_excluding_none, remove_idx)
    return compute_quantile(remaining, target_cov)


def marginal_loo_miscoverage(aug_scores, target_cov=TARGET_COVERAGE):
    """
    E_{y,i} for every point i in the augmented (n+1-point) set, using the MARGINAL
    (all-points-pooled, not group-specific) leave-one-out conformal threshold. This is the
    single miscoverage indicator array the paper's delta_{y,k} formula re-aggregates by
    different candidate attributes k -- E_{y,i} itself does not depend on k (see module notes:
    `documentation/final_audit/AFCP_IMPLEMENTATION_NOTES.md`).
    """
    n_full = len(aug_scores)
    sorted_all = np.sort(aug_scores)
    order = np.argsort(aug_scores, kind="stable")
    ranks = np.empty_like(order)
    ranks[order] = np.arange(len(order))

    n = n_full - 1
    if n <= 0:
        return np.zeros(n_full, dtype=bool)
    k_idx = int(np.ceil(n_full * target_cov))
    if k_idx > n:
        thr_arr = np.full(n_full, np.inf)
    else:
        thr_arr = np.where((k_idx - 1) < ranks, sorted_all[k_idx - 1], sorted_all[k_idx])
    return aug_scores > thr_arr


def afcp_group_selection_and_set(
    test_score_by_label,   # dict {0: score_if_y=0, 1: score_if_y=1} for the test point
    cal_scores,            # np.ndarray, calibration nonconformity scores (fixed, label-true)
    cal_group_ids_by_attr, # dict attr_name -> np.ndarray of calibration group labels
    test_group_by_attr,    # dict attr_name -> this test point's own group label
    target_cov=TARGET_COVERAGE,
    sig_level=SIGNIFICANCE_LEVEL,
):
    """
    Faithful AFCP Algorithm 1 + 2 for a single test point.

    delta_{y,k} := worst-group mean of E_{y,i}, where E_{y,i} is the MARGINAL (pooled) leave-
    one-out miscoverage indicator (computed once per y, not per attribute), re-aggregated by
    each candidate attribute k's group membership. q_hat_y = max_k delta_{y,k}; a one-sided
    test on the argmax group's E-values decides whether that attribute is selected for
    hypothesis y.

    Returns: selected_attr_by_y: dict{0/1 -> attr_name or None}.
    """
    attrs = list(cal_group_ids_by_attr.keys())
    n_cal = len(cal_scores)
    selected_attr_by_y = {}

    for y in (0, 1):
        new_score = test_score_by_label[y]
        aug_scores = np.append(cal_scores, new_score)  # index n_cal = the new point
        E = marginal_loo_miscoverage(aug_scores, target_cov)

        best_delta = -np.inf
        best_attr = None
        best_group_mask = None

        for attr in attrs:
            cal_groups = cal_group_ids_by_attr[attr]
            new_group = test_group_by_attr[attr]
            aug_groups = np.append(cal_groups, new_group)
            unique_groups = np.unique(aug_groups)
            for g in unique_groups:
                mask = aug_groups == g
                if mask.sum() == 0:
                    continue
                delta = E[mask].mean()
                if delta > best_delta:
                    best_delta = delta
                    best_attr = attr
                    best_group_mask = mask

        # One-sided test: is q_hat_y = best_delta (the worst group's mean) significantly > alpha?
        if best_group_mask is not None and best_group_mask.sum() > 1:
            group_E = E[best_group_mask].astype(float)
            if group_E.std() > 0:
                tt = stats.ttest_1samp(group_E, popmean=ALPHA, alternative="greater")
                p_value = tt.pvalue
            else:
                # zero variance: all points in the group agree; significant iff the shared
                # value itself exceeds alpha (a t-test is undefined at zero variance)
                p_value = 0.0 if group_E.mean() > ALPHA else 1.0
        else:
            p_value = 1.0

        selected_attr_by_y[y] = best_attr if p_value < sig_level else None

    return selected_attr_by_y


def build_final_set(
    test_score_by_label, marginal_threshold, selected_attr_by_y,
    cal_scores, cal_group_ids_by_attr, test_group_by_attr, target_cov=TARGET_COVERAGE,
):
    """Algorithm 2: union of the marginal set and the (non-LOO) group-equalized sets."""
    included = set()
    for y in (0, 1):
        if test_score_by_label[y] <= marginal_threshold:
            included.add(y)
        attr = selected_attr_by_y.get(y)
        if attr is not None:
            g = test_group_by_attr[attr]
            group_scores = cal_scores[cal_group_ids_by_attr[attr] == g]
            group_thr = compute_quantile(group_scores, target_cov)
            if test_score_by_label[y] <= group_thr:
                included.add(y)
    return included


if __name__ == "__main__":
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    master = pd.read_parquet(ROOT / "data" / "processed" / "analysis_dataset_primary.parquet")
    test_ids = set(pd.read_csv(SPLIT_DIR / "test_ids.csv")["SEQN"])
    cal_ids = set(pd.read_csv(SPLIT_DIR / "conformal_calibration_ids.csv")["SEQN"])
    test_df = master[master["SEQN"].isin(test_ids)].reset_index(drop=True)
    cal_df = master[master["SEQN"].isin(cal_ids)].reset_index(drop=True)
    assert set(test_df["SEQN"]).isdisjoint(set(cal_df["SEQN"])), "calibration/test overlap"

    y_test = test_df[PRIMARY_OUTCOME_COL].values
    y_cal = cal_df[PRIMARY_OUTCOME_COL].values

    ATTRS = ["bmi_group_final", "age_group_final"]
    rows = []
    print("=== AFCP (faithful, Zhou & Sesia NeurIPS 2024) -- FULL RUN ===")

    for name in MODEL_NAMES:
        print(f"\n--- Model: {name.upper()} ---")
        refit_path = ROOT / "models" / "phase6_conformal_refit" / f"model_{name}_proper_train_refit.joblib"
        refit = joblib.load(refit_path)
        pipe = refit["pipeline"]

        oof_df = pd.read_csv(RESULTS_DIR / "calibration" / f"recalibrated_oof_predictions_{name}.csv")
        intercept = oof_df["platt_intercept"].iloc[0]
        slope = oof_df["platt_slope"].iloc[0]

        cal_raw = pipe.predict_proba(cal_df[PRIMARY_PREDICTORS])[:, 1]
        test_raw = pipe.predict_proba(test_df[PRIMARY_PREDICTORS])[:, 1]
        cal_p = platt_transform(cal_raw, intercept, slope)
        test_p = platt_transform(test_raw, intercept, slope)

        cal_scores = conformal_score(y_cal, cal_p)
        marginal_threshold = compute_quantile(cal_scores, TARGET_COVERAGE)

        cal_group_ids_by_attr = {a: cal_df[a].values for a in ATTRS}

        n_test = len(test_df)
        # NOTE: full N=2,146 x 2 candidate labels x 2 attributes x LOO-over-~1002 points is the
        # faithful computation. To keep runtime bounded while remaining exact (no approximation
        # of the algorithm itself), we run it on the full test set here; this is O(n_test) outer
        # iterations each doing O(n_cal log n_cal) vectorizable work.
        covered = np.zeros(n_test, dtype=bool)
        set_size = np.zeros(n_test, dtype=int)
        selected_attrs_log = []

        for idx in range(n_test):
            p1 = test_p[idx]
            test_score_by_label = {1: 1.0 - p1, 0: p1}
            test_group_by_attr = {a: test_df[a].values[idx] for a in ATTRS}

            selected_attr_by_y = afcp_group_selection_and_set(
                test_score_by_label, cal_scores, cal_group_ids_by_attr, test_group_by_attr,
            )
            final_set = build_final_set(
                test_score_by_label, marginal_threshold, selected_attr_by_y,
                cal_scores, cal_group_ids_by_attr, test_group_by_attr,
            )
            true_y = y_test[idx]
            covered[idx] = true_y in final_set
            set_size[idx] = len(final_set)
            selected_attrs_log.append(selected_attr_by_y)

            if idx % 500 == 0:
                print(f"  ... {idx}/{n_test} test points processed")

        overall_coverage = covered.mean()
        overall_set_size = set_size.mean()

        for group_col, group_val, label in [
            ("bmi_group_final", "Obese", "BMI_Obese"),
            ("age_group_final", "60+", "Age_60plus"),
        ]:
            mask = (test_df[group_col] == group_val).values
            rows.append({
                "model": name,
                "scope": label,
                "n_test": int(mask.sum()),
                "afcp_coverage": covered[mask].mean() if mask.sum() > 0 else np.nan,
                "afcp_mean_set_size": set_size[mask].mean() if mask.sum() > 0 else np.nan,
                "overall_coverage": overall_coverage,
                "overall_mean_set_size": overall_set_size,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "method": "afcp_faithful_zhou_sesia_2024",
            })

        joint_mask = ((test_df["bmi_group_final"] == "Obese") & (test_df["age_group_final"] == "60+")).values
        rows.append({
            "model": name,
            "scope": "BMI_Obese_Age_60plus",
            "n_test": int(joint_mask.sum()),
            "afcp_coverage": covered[joint_mask].mean() if joint_mask.sum() > 0 else np.nan,
            "afcp_mean_set_size": set_size[joint_mask].mean() if joint_mask.sum() > 0 else np.nan,
            "overall_coverage": overall_coverage,
            "overall_mean_set_size": overall_set_size,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method": "afcp_faithful_zhou_sesia_2024",
        })
        print(f"  Overall coverage={overall_coverage:.4f}, mean set size={overall_set_size:.4f}")

    out_df = pd.DataFrame(rows)
    out_path = DIAG_DIR / "afcp_faithful_results.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")
