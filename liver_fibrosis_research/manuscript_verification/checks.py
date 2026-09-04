"""
Check definitions for the manuscript number-verification harness.
=================================================================

Each dict in CHECKS pins ONE numeric sentence in the manuscript to the frozen
result artifact it must come from.  `verify.py` runs them.

Schema
------
id            : short unique label for this check
claim_id      : matching row in results/final_research_audit/FINAL_MANUSCRIPT_CLAIM_REGISTRY.csv
section       : where the number appears in the manuscript
statement     : the manuscript sentence being verified (human readable)
source        : repo-relative path to the artifact (str) or [primary, ...] list
kind          : one of  band | all_in_range | scalar | per_key_scalar | count |
                        bool_all | sign_all | topk_set
filter        : {column: value | [values]}  applied before extraction (optional)
tol           : numeric tolerance (default 0.01)
abs_value     : take abs() of extracted values before comparing (optional)

kind-specific keys
------------------
band            : column, expected={low, high}      -> min≈low and max≈high
all_in_range    : column, expected={low, high}      -> every value in [low, high]
scalar          : column, expected=<number>         -> one distinct value ≈ expected
per_key_scalar  : key_column, column, expected={key: value, ...}
count           : expected=<int>, of=<int?>, where_true=<bool col?> / where_false=<bool col?>
bool_all        : column, expected=<bool>
sign_all        : column, expected="neg" | "pos"
topk_set        : group_column, sort_column, label_column, k, expected=[labels...]

Adding a check: copy the closest example below, point it at the artifact,
paste the number your manuscript prints. If it FAILs, one of the two is wrong.
"""

MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]

CHECKS = [

    # ===================================================================== #
    # Cohort  (§3.1, §2.4, Table 1)
    # ===================================================================== #
    {
        "id": "COHORT-N",
        "claim_id": "-",
        "section": "§3.1 / abstract",
        "statement": "primary cohort N = 7,153; 666 positive; 9.31% prevalence",
        "source": "results/tables/phase2_outcome_prevalence.csv",
        "filter": {"category": "OVERALL"},
        "kind": "per_key_scalar",
        "key_column": "group_label",
        "column": "n",
        "expected": {"Primary cohort (all)": 7153},
        "tol": 0,
    },
    {
        "id": "COHORT-POS",
        "claim_id": "-",
        "section": "§3.1",
        "statement": "666 significant-fibrosis cases in the primary cohort",
        "source": "results/tables/phase2_outcome_prevalence.csv",
        "filter": {"category": "OVERALL"},
        "kind": "scalar",
        "column": "n_positive",
        "expected": 666,
        "tol": 0,
    },
    {
        "id": "COHORT-PREV",
        "claim_id": "-",
        "section": "§3.1 / abstract",
        "statement": "prevalence of significant fibrosis 9.31%",
        "source": "results/tables/phase2_outcome_prevalence.csv",
        "filter": {"category": "OVERALL"},
        "kind": "scalar",
        "column": "prevalence_pct",
        "expected": 9.31,
        "tol": 0.02,
    },

    # ===================================================================== #
    # Discrimination  (§3.2, Table 2)
    # ===================================================================== #
    {
        "id": "DISC-01-BAND",
        "claim_id": "DISC-01",
        "section": "§3.2 / abstract",
        "statement": "test AUROC 0.823–0.843 across five model families",
        "source": "results/tables/phase3_final_baseline_results.csv",
        "kind": "band",
        "column": "test_roc_auc",
        "expected": {"low": 0.8229, "high": 0.8429},
        "tol": 0.001,
    },
    {
        "id": "DISC-01-PERMODEL",
        "claim_id": "DISC-01",
        "section": "§3.2",
        "statement": "AUROC: logistic .833, RF .834, XGB .843, LGBM .839, MLP .823",
        "source": "results/tables/phase3_final_baseline_results.csv",
        "kind": "per_key_scalar",
        "key_column": "model_name",
        "column": "test_roc_auc",
        "expected": {"logistic": 0.8334, "random_forest": 0.8343, "xgboost": 0.8429,
                     "lightgbm": 0.8394, "mlp": 0.8229},
        "tol": 0.001,
    },
    {
        "id": "DISC-01-PRAUC",
        "claim_id": "DISC-01",
        "section": "§3.2 / abstract",
        "statement": "PR-AUC 0.35–0.37 at 9.31% prevalence",
        "source": "results/tables/phase3_final_baseline_results.csv",
        "kind": "band",
        "column": "test_pr_auc",
        "expected": {"low": 0.3508, "high": 0.3729},
        "tol": 0.003,
    },
    {
        "id": "DISC-02-FDR",
        "claim_id": "DISC-02",
        "section": "§3.2 / abstract",
        "statement": "0 of 10 pairwise AUROC comparisons significant after BH-FDR",
        "source": "results/tables/phase3_model_comparison_fdr.csv",
        "kind": "count",
        "where_true": "significant_after_fdr_0.05",
        "expected": 0,
        "of": 10,
    },

    # ===================================================================== #
    # Calibration  (§3.3, Table 2)
    # ===================================================================== #
    {
        "id": "CAL-OOF-INTERCEPT",
        "claim_id": "CAL-01",
        "section": "§3.3",
        "statement": "OOF calibration intercepts -2.24 to -1.86 for the 4 class-balanced models",
        "source": "results/calibration/primary_metrics_by_model.csv",
        "filter": {"model": ["logistic", "random_forest", "xgboost", "lightgbm"]},
        "kind": "all_in_range",
        "column": "calibration_intercept",
        "expected": {"low": -2.26, "high": -1.86},
        "tol": 0.01,
    },
    {
        "id": "CAL-OOF-MLP",
        "claim_id": "CAL-01",
        "section": "§3.3",
        "statement": "unweighted perceptron OOF intercept -0.28",
        "source": "results/calibration/primary_metrics_by_model.csv",
        "filter": {"model": "mlp"},
        "kind": "scalar",
        "column": "calibration_intercept",
        "expected": -0.281,
        "tol": 0.01,
    },
    {
        "id": "CAL-TEST-ECE-RAW",
        "claim_id": "CAL-01",
        "section": "§3.3 / abstract",
        "statement": "raw test ECE 0.24–0.30 (class-balanced models)",
        "source": "results/calibration/test_set_calibration_final.csv",
        "filter": {"variant": "raw",
                   "model": ["logistic", "random_forest", "xgboost", "lightgbm"]},
        "kind": "all_in_range",
        "column": "ece",
        "expected": {"low": 0.24, "high": 0.30},
        "tol": 0.005,
    },
    {
        "id": "CAL-TEST-ECE-RECAL",
        "claim_id": "CAL-01",
        "section": "§3.3 / abstract",
        "statement": "recalibrated test ECE 0.011–0.026",
        "source": "results/calibration/test_set_calibration_final.csv",
        "filter": {"variant": "recalibrated"},
        "kind": "band",
        "column": "ece",
        "expected": {"low": 0.0113, "high": 0.0264},
        "tol": 0.002,
    },
    {
        "id": "CAL-TEST-INTERCEPT-RECAL",
        "claim_id": "CAL-01",
        "section": "§3.3",
        "statement": "recalibrated test intercepts -0.15 to +0.14",
        "source": "results/calibration/test_set_calibration_final.csv",
        "filter": {"variant": "recalibrated"},
        "kind": "band",
        "column": "calibration_intercept",
        "expected": {"low": -0.154, "high": 0.142},
        "tol": 0.01,
    },

    # ===================================================================== #
    # Body-mass fairness  (§3.4, Figure 3)
    # ===================================================================== #
    {
        "id": "FAIR-BMI-01-BAND",
        "claim_id": "FAIR-BMI-01",
        "section": "§3.4 / abstract",
        "statement": "Normal-vs-Obese sensitivity gap 27–48 pp in all 5 models",
        "source": "results/fairness/fairness_inference.csv",
        "filter": {"dimension": "bmi", "category": "Obese"},
        "kind": "band",
        "column": "absolute_disparity_pp",
        "abs_value": True,
        "expected": {"low": 27.08, "high": 47.66},
        "tol": 0.2,
    },
    {
        "id": "FAIR-BMI-01-Q",
        "claim_id": "FAIR-BMI-01",
        "section": "§3.4",
        "statement": "all five BMI-Obese disparities BH q <= 0.006",
        "source": "results/fairness/fairness_inference.csv",
        "filter": {"dimension": "bmi", "category": "Obese"},
        "kind": "all_in_range",
        "column": "bh_fdr_adjusted_p",
        "expected": {"low": 0.0, "high": 0.006},
        "tol": 0.0005,
    },
    {
        "id": "FAIR-BMI-01-SIG",
        "claim_id": "FAIR-BMI-01",
        "section": "§3.4",
        "statement": "BMI-Obese sensitivity disparity BH-significant in 5/5 models",
        "source": "results/fairness/fairness_inference.csv",
        "filter": {"dimension": "bmi", "category": "Obese"},
        "kind": "count",
        "where_true": "significant_after_fdr_0.05",
        "expected": 5,
        "of": 5,
    },
    {
        "id": "FAIR-BMI-04-SHORTCUT",
        "claim_id": "FAIR-BMI-04",
        "section": "§3.4 / abstract",
        "statement": "matched-stiffness obese probability +0.19–0.33 higher, p<0.001 all 5",
        "source": "results/prepublication_fixes/fix2_bmi_shortcut_check.csv",
        "kind": "band",
        "column": "beta_is_obese",
        "expected": {"low": 0.1906, "high": 0.3319},
        "tol": 0.005,
    },
    {
        "id": "FAIR-BMI-04-P",
        "claim_id": "FAIR-BMI-04",
        "section": "§3.4",
        "statement": "matched-stiffness OLS obese coefficient p < 0.001 in all 5 models",
        "source": "results/prepublication_fixes/fix2_bmi_shortcut_check.csv",
        "kind": "all_in_range",
        "column": "p_value",
        "expected": {"low": 0.0, "high": 0.001},
        "tol": 0.0,
    },

    # ===================================================================== #
    # Age  (§3.8) -- secondary observation
    # ===================================================================== #
    {
        "id": "FAIR-AGE-01-BAND",
        "claim_id": "FAIR-AGE-01",
        "section": "§3.8",
        "statement": "Age-60+ sensitivity deficit -8.6 to -14.7 pp",
        "source": "results/fairness/fairness_inference.csv",
        "filter": {"dimension": "age", "category": "60+"},
        "kind": "band",
        "column": "absolute_disparity_pp",
        "abs_value": True,
        "expected": {"low": 8.55, "high": 14.67},
        "tol": 0.15,
    },
    {
        "id": "FAIR-AGE-01-DIR",
        "claim_id": "FAIR-AGE-01",
        "section": "§3.8",
        "statement": "Age-60+ sensitivity deficit negative in all five models",
        "source": "results/fairness/fairness_inference.csv",
        "filter": {"dimension": "age", "category": "60+"},
        "kind": "sign_all",
        "column": "absolute_disparity_pp",
        "expected": "neg",
    },
    {
        "id": "FAIR-AGE-01-SIG",
        "claim_id": "FAIR-AGE-01",
        "section": "§3.8 / abstract",
        "statement": "Age-60+ sensitivity deficit BH-significant in 4/5 models (not logistic)",
        "source": "results/fairness/fairness_inference.csv",
        "filter": {"dimension": "age", "category": "60+"},
        "kind": "count",
        "where_true": "significant_after_fdr_0.05",
        "expected": 4,
        "of": 5,
    },

    # ===================================================================== #
    # Conformal coverage  (§3.5, Table 3)
    # ===================================================================== #
    {
        "id": "CONF-01-MARGINAL",
        "claim_id": "CONF-01",
        "section": "§3.5 / abstract",
        "statement": "marginal conformal coverage 88.1–90.8%",
        "source": "results/uncertainty/marginal_coverage_test_set.csv",
        "kind": "band",
        "column": "empirical_coverage",
        "expected": {"low": 0.8812, "high": 0.9082},
        "tol": 0.002,
    },
    {
        "id": "CONF-02-BMI-OBESE",
        "claim_id": "CONF-02",
        "section": "§3.5 / abstract",
        "statement": "BMI-Obese conformal coverage 76.8–82.3%",
        "source": "results/uncertainty/subgroup_coverage.csv",
        "filter": {"dimension": "bmi", "category": "Obese"},
        "kind": "band",
        "column": "empirical_coverage",
        "expected": {"low": 0.7678, "high": 0.8233},
        "tol": 0.003,
    },
    {
        "id": "CONF-02-BMI-OBESE-SIG",
        "claim_id": "CONF-02",
        "section": "§3.5",
        "statement": "BMI-Obese under-coverage: CI excludes 0.90 for all 5 models",
        "source": "results/uncertainty/subgroup_coverage.csv",
        "filter": {"dimension": "bmi", "category": "Obese"},
        "kind": "bool_all",
        "column": "ci_excludes_target",
        "expected": True,
    },
    {
        "id": "CONF-02-AGE-60",
        "claim_id": "CONF-02",
        "section": "§3.5 / abstract",
        "statement": "Age-60+ conformal coverage 81.1–85.6%",
        "source": "results/uncertainty/subgroup_coverage.csv",
        "filter": {"dimension": "age", "category": "60+"},
        "kind": "band",
        "column": "empirical_coverage",
        "expected": {"low": 0.8111, "high": 0.8556},
        "tol": 0.003,
    },
    {
        "id": "CONF-02-AGE-60-SIG",
        "claim_id": "CONF-02",
        "section": "§3.5",
        "statement": "Age-60+ under-coverage BH-significant in 5/5 models (CAND_1)",
        "source": "results/uncertainty/subgroup_coverage.csv",
        "filter": {"dimension": "age", "category": "60+"},
        "kind": "count",
        "where_true": "significant_after_fdr_0.05",
        "expected": 5,
        "of": 5,
    },
    {
        "id": "CONF-02-OVERCOVER",
        "claim_id": "CONF-02",
        "section": "§3.5",
        "statement": "Normal-BMI and Overweight over-cover (all >= 0.94)",
        "source": "results/uncertainty/subgroup_coverage.csv",
        "filter": {"dimension": "bmi", "category": ["Normal", "Overweight"]},
        "kind": "all_in_range",
        "column": "empirical_coverage",
        "expected": {"low": 0.94, "high": 1.0},
        "tol": 0.005,
    },
    {
        "id": "CONF-03-INTERSECTION",
        "claim_id": "CONF-03",
        "section": "§3.5 / abstract",
        "statement": "Obese-and-60+ intersection (N=294) coverage 65–75%",
        "source": "results/uncertainty/intersectional_coverage_ci.csv",
        "filter": {"stage": "baseline"},
        "kind": "band",
        "column": "coverage",
        "expected": {"low": 0.6497, "high": 0.7517},
        "tol": 0.005,
    },
    {
        "id": "CONF-03-N",
        "claim_id": "CONF-03",
        "section": "§3.5 / §5",
        "statement": "intersectional cell N = 294 (not 62% of the cohort)",
        "source": "results/uncertainty/intersectional_coverage_ci.csv",
        "filter": {"stage": "baseline"},
        "kind": "scalar",
        "column": "n",
        "expected": 294,
        "tol": 0,
    },

    # ===================================================================== #
    # Demographic holdout  (§3.9)  -- pins the value the desktop PDF got wrong
    # ===================================================================== #
    {
        "id": "GEN-01-AUROC",
        "claim_id": "GEN-01",
        "section": "§3.9",
        "statement": "NHB holdout AUROC 0.772–0.789",
        "source": "results/validation/phase8_generalization_results.csv",
        "kind": "band",
        "column": "roc_auc",
        "expected": {"low": 0.7719, "high": 0.7893},
        "tol": 0.002,
    },
    {
        "id": "GEN-01-INTERCEPT",
        "claim_id": "GEN-01",
        "section": "§3.9  [PDF §IV-G was wrong here]",
        "statement": "NHB holdout calibration intercepts -0.58 to -2.17 (RAW, no recalibration)",
        "source": "results/validation/phase8_generalization_results.csv",
        "kind": "band",
        "column": "calibration_intercept",
        "expected": {"low": -2.169, "high": -0.577},
        "tol": 0.01,
    },
    {
        "id": "GEN-01-SLOPE",
        "claim_id": "GEN-01",
        "section": "§3.9",
        "statement": "NHB holdout calibration slopes 0.64–0.97",
        "source": "results/validation/phase8_generalization_results.csv",
        "kind": "band",
        "column": "calibration_slope",
        "expected": {"low": 0.636, "high": 0.972},
        "tol": 0.01,
    },

    # ===================================================================== #
    # Sensitivity / secondary outcomes  (§3.10)
    # ===================================================================== #
    {
        "id": "SECOUT-01-9p7",
        "claim_id": "SECOUT-01",
        "section": "§3.10",
        "statement": "advanced fibrosis >=9.7 kPa: AUROC 0.85–0.86",
        "source": "results/sensitivity/secondary_severity_outcomes_results.csv",
        "filter": {"outcome": "advanced_9.7kPa"},
        "kind": "all_in_range",
        "column": "roc_auc",
        "expected": {"low": 0.845, "high": 0.862},
        "tol": 0.003,
    },
    {
        "id": "SECOUT-01-13p6",
        "claim_id": "SECOUT-01",
        "section": "§3.10",
        "statement": "cirrhosis >=13.6 kPa: AUROC 0.84–0.86",
        "source": "results/sensitivity/secondary_severity_outcomes_results.csv",
        "filter": {"outcome": "cirrhosis_13.6kPa"},
        "kind": "all_in_range",
        "column": "roc_auc",
        "expected": {"low": 0.840, "high": 0.862},
        "tol": 0.003,
    },
    {
        "id": "SECOUT-01-RELABEL-ONLY",
        "claim_id": "SECOUT-01",
        "section": "§2.9  [resolves PDF §IV-H 'was it executed?' hedge]",
        "statement": "severity outcomes were RELABEL-ONLY: no retrain, no Platt refit, "
                     "no conformal repeat, test set not re-accessed for fitting (Amendment #15)",
        "source": "results/sensitivity/secondary_severity_outcomes_results.csv",
        "kind": "bool_all",
        "column": "retrained",
        "expected": False,
    },
    {
        "id": "SECOUT-01-NO-REFIT",
        "claim_id": "SECOUT-01",
        "section": "§2.9",
        "statement": "severity outcomes: Platt parameters not re-fit",
        "source": "results/sensitivity/secondary_severity_outcomes_results.csv",
        "kind": "bool_all",
        "column": "platt_refit",
        "expected": False,
    },
    {
        "id": "SECOUT-01-NO-TESTACCESS",
        "claim_id": "SECOUT-01",
        "section": "§2.9",
        "statement": "severity outcomes: locked test not re-accessed for model fitting",
        "source": "results/sensitivity/secondary_severity_outcomes_results.csv",
        "kind": "bool_all",
        "column": "test_set_reaccessed_for_model_fitting",
        "expected": False,
    },

    # ===================================================================== #
    # Training-time mitigation  (§3.7b, Table 4)  -- Amendment #19
    # ===================================================================== #
    {
        "id": "MIT-07-VERDICT",
        "claim_id": "MIT-07",
        "section": "§3.7b / abstract",
        "statement": "training-time reweighting verdict: NEGATIVE (no efficacy), both arms",
        "source": "results/training_time_mitigation/decision.csv",
        "kind": "per_key_scalar",
        "key_column": "arm",
        "column": "verdict",
        "expected": {},   # placeholder; string verdicts checked via MIT-07-VERDICT-STR
        "tol": 0,
        "skip": True,
    },
    {
        "id": "MIT-07-BMI-GAP-REDUCED",
        "claim_id": "MIT-07",
        "section": "§3.7b",
        "statement": "after reweighting, Normal-vs-Obese gap +14 to +17 pp (Arm A, 4 families)",
        "source": "results/training_time_mitigation/test_subgroup_sensitivity.csv",
        "filter": {"arm": "A", "dimension": "bmi", "category": "Obese"},
        "kind": "band",
        "column": "disparity_pp",
        "expected": {"low": 14.0, "high": 17.5},
        "tol": 1.0,
    },
    {
        "id": "MIT-07-BMI-GAP-NS",
        "claim_id": "MIT-07",
        "section": "§3.7b",
        "statement": "after reweighting, BMI-Obese gap no longer BH-significant (Arm A)",
        "source": "results/training_time_mitigation/test_subgroup_sensitivity.csv",
        "filter": {"arm": "A", "dimension": "bmi", "category": "Obese"},
        "kind": "count",
        "where_true": "significant_after_fdr_0.05",
        "expected": 0,
    },
    {
        "id": "MIT-07-NEW-SEX-DISPARITY",
        "claim_id": "MIT-07",
        "section": "§3.7b / DO_NOT_CLAIM 9d",
        "statement": "reweighting created a new BH-significant logistic Female sensitivity disparity",
        "source": "results/training_time_mitigation/test_subgroup_sensitivity.csv",
        "filter": {"arm": "A", "model": "logistic", "dimension": "sex", "category": "Female"},
        "kind": "scalar",
        "column": "disparity_pp",
        "expected": -15.09,
        "tol": 0.2,
    },

    # ===================================================================== #
    # Interpretability  (§3.11)
    # ===================================================================== #
    # --- §3.11 rewritten 2026 to match the artifacts exactly; these checks
    #     verify the corrected sentence, component by component. ---
    {
        "id": "INT-01-BMI-TOP1",
        "claim_id": "INT-01",
        "section": "§3.11",
        "statement": "BMI ranks first by permutation importance in every model family",
        "source": "results/tables/interpretability_permutation_importance.csv",
        "kind": "topk_set",
        "group_column": "model",
        "sort_column": "importance_mean_auc_drop",
        "label_column": "predictor",
        "k": 1,
        "expected": ["BMXBMI"],
    },
    {
        "id": "INT-01-BMI-COEF-TOP1",
        "claim_id": "INT-01",
        "section": "§3.11",
        "statement": "BMI has the largest standardised logistic-regression coefficient",
        "source": "results/tables/interpretability_logistic_coefficients.csv",
        "kind": "topk_set",
        # no group_column -> whole file is one ranking
        "sort_column": "standardized_coefficient",
        "label_column": "predictor",
        "k": 1,
        "abs_value_sort": True,
        "expected": ["BMXBMI"],
    },
    {
        "id": "INT-01-TOP4-BOOSTING",
        "claim_id": "INT-01",
        "section": "§3.11",
        "statement": "top four for XGBoost and LightGBM = {BMI, age, ALT, AST} (perm. importance)",
        "source": "results/tables/interpretability_permutation_importance.csv",
        "filter": {"model": ["xgboost", "lightgbm"]},
        "kind": "topk_set",
        "group_column": "model",
        "sort_column": "importance_mean_auc_drop",
        "label_column": "predictor",
        "k": 4,
        "expected": ["RIDAGEYR", "BMXBMI", "LBXSATSI", "LBXSASSI"],
    },
    {
        "id": "INT-01-RF-HDL",
        "claim_id": "INT-01",
        "section": "§3.11",
        "statement": "for random forest, HDL is in the top four and AST is not (perm. importance)",
        "source": "results/tables/interpretability_permutation_importance.csv",
        "filter": {"model": "random_forest"},
        "kind": "topk_set",
        "group_column": "model",
        "sort_column": "importance_mean_auc_drop",
        "label_column": "predictor",
        "k": 4,
        "expected": ["RIDAGEYR", "BMXBMI", "LBXSATSI", "LBDHDD"],
    },
]

# Drop entries flagged skip=True (kept in-file as templates)
CHECKS = [c for c in CHECKS if not c.get("skip")]
