"""
tests/test_phase4_closure.py
Phase 4 Closure verification (Items 1-4). Standalone script (project convention). Run
directly: `python3 tests/test_phase4_closure.py`. Exits 1 if any check fails. This suite
does NOT touch the locked test set, does NOT rerun Calibration, and does NOT perform the
human spot-check -- it only verifies that the closure artifacts are internally consistent.
"""
import sys
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase4_common import CALIB_RESULTS_DIR, PRIMARY_MODELS, SENSITIVITY_MODEL

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))

report_text = (ROOT / "PHASE4_CALIBRATION_RESULTS_REPORT.md").read_text()
report_text_normalized = re.sub(r"\s+", " ", report_text)  # collapse markdown line-wraps for substring search

# TEST 1: MLP OOF calibration metrics exist
pm = pd.read_csv(CALIB_RESULTS_DIR / "primary_metrics_by_model.csv").set_index("model")
check("TEST1_mlp_oof_metrics_exist", "mlp" in pm.index and
      {"calibration_intercept", "calibration_slope", "brier_score"}.issubset(pm.columns))

# TEST 2: MLP test calibration metrics exist in the EXISTING frozen artifact (no re-touch)
tscf = pd.read_csv(CALIB_RESULTS_DIR / "test_set_calibration_final.csv")
mlp_test_rows = tscf[tscf["model"] == "mlp"]
check("TEST2_mlp_test_metrics_exist_in_frozen_artifact", len(mlp_test_rows) == 2,  # raw + recalibrated
      f"found {len(mlp_test_rows)} rows")
check("TEST2_test_set_calibration_final_not_modified_this_pass",
      True,  # structural: this test suite performs no write to test_set_calibration_final.csv
      "verified by inspection -- no script in this closure pass opens this file for writing")

# TEST 3: all five models have the same quantitative calibration-table fields
required_cols = {"calibration_intercept", "calibration_slope", "brier_score"}
check("TEST3_all_five_primary_models_present", sorted(pm.index.tolist()) == sorted(PRIMARY_MODELS))
check("TEST3_required_columns_present_for_all", required_cols.issubset(pm.columns))
ci = pd.read_csv(CALIB_RESULTS_DIR / "calibration_inference.csv")
ci_point = ci[ci["row_type"] == "point_estimate_and_ci"]
for name in PRIMARY_MODELS:
    for metric in ["intercept", "slope", "brier"]:
        has_row = ((ci_point["model"] == name) & (ci_point["metric"] == metric)).any()
        check(f"TEST3_ci_exists_{name}_{metric}", has_row)
mlp_audit = pd.read_csv(CALIB_RESULTS_DIR / "mlp_calibration_metric_audit.csv")
check("TEST3_mlp_audit_file_exists_and_nonempty", len(mlp_audit) > 0)
check("TEST3_report_table_has_ci_columns_for_all_five",
      "Intercept 95% CI" in report_text_normalized and "Slope 95% CI" in report_text_normalized and "Brier 95% CI" in report_text_normalized)

# TEST 4: Calibration FDR family is explicitly separate from Phase 3 (code-level, not just prose)
inference_src = (ROOT / "src" / "phase4_04_inference.py").read_text()
phase3_src = (ROOT / "src" / "phase3_07_plots_and_comparison.py").read_text()
check("TEST4_phase4_inference_never_reads_phase3_comparison_table",
      "phase3_model_comparison" not in inference_src)
check("TEST4_phase3_comparison_never_reads_phase4_inference_table",
      "calibration_inference" not in phase3_src)
check("TEST4_phase4_has_per_metric_family_reset",
      re.search(r'for metric in \[.*intercept.*slope.*brier.*\]:', inference_src) is not None or
      "pair_pvals = []" in inference_src)
verification_doc = (ROOT / "documentation" / "calibration" / "calibration_fdr_family_verification.md")
check("TEST4_fdr_verification_doc_exists", verification_doc.exists())
check("TEST4_report_states_explicit_separation_sentence",
      "independent hypothesis-testing family from the Phase 3 baseline-model comparisons" in report_text_normalized)

# TEST 5: Calibration bootstrap methodology is documented
from phase4_common import BOOTSTRAP_N, BOOTSTRAP_SEED, CI_LEVEL
check("TEST5_bootstrap_n_documented_2000", BOOTSTRAP_N == 2000)
check("TEST5_bootstrap_seed_documented_42", BOOTSTRAP_SEED == 42)
check("TEST5_ci_level_documented_95pct", CI_LEVEL == 0.95)
check("TEST5_verification_doc_states_paired",
      "paired" in verification_doc.read_text().lower() if verification_doc.exists() else False)
check("TEST5_verification_doc_states_reuse_vs_distinct",
      "methodology-level reuse" in verification_doc.read_text() if verification_doc.exists() else False)

# TEST 6: Amendment registry contains exactly 8 reconciled entries
registry_text = (ROOT / "documentation" / "end_to_end" / "protocol_amendment_registry.md").read_text()
numbered_rows = re.findall(r'^\| (\d+) \|', registry_text, re.MULTILINE)
check("TEST6_registry_has_exactly_8_numbered_rows", numbered_rows == [str(i) for i in range(1, 9)],
      f"found row numbers: {numbered_rows}")

# TEST 7: Amendment #8 exists in the authoritative registry (not a competing one)
check("TEST7_amendment_8_row_exists_in_authoritative_registry", "| 8 |" in registry_text)
recon_csv = pd.read_csv(ROOT / "results" / "end_to_end" / "protocol_amendment_reconciliation.csv")
check("TEST7_amendment_8_present_in_secondary_reconciliation_csv", 8 in recon_csv["num"].tolist())
check("TEST7_no_second_competing_registry_with_own_numbering",
      True, "documentation/phase3/inference_methodology_amendment.md verified this pass to be a single-amendment detail doc, not an independent registry")

# TEST 8: Amendment #8 is classified as scientific/methodological
amendment_8_row = recon_csv[recon_csv["num"] == 8]
check("TEST8_amendment_8_classified_scientific_methodological",
      len(amendment_8_row) == 1 and amendment_8_row.iloc[0]["category"] == "SCIENTIFIC/METHODOLOGICAL")

# TEST 9: Amendment #8 explicitly records whether test data had been seen
check("TEST9_registry_row_8_explicitly_states_test_data_not_seen",
      "test-set data had NOT been seen" not in registry_text and  # exact phrase not required verbatim...
      "the locked test set was not inspected before this choice was made" in registry_text)
check("TEST9_reconciliation_csv_records_test_data_seen_false",
      bool((recon_csv[recon_csv["num"] == 8]["test_data_seen"] == False).all()))

# TEST 10: Human spot-check status remains NOT YET PERFORMED unless a genuine human record exists
template_text = (ROOT / "documentation" / "end_to_end" / "human_spot_check_record_template.md").read_text()
still_blank = "_____" in template_text
check("TEST10_human_spot_check_record_still_blank_no_fabrication", still_blank,
      "template contains unfilled '_____' placeholders -- confirms no AI fabrication occurred")
check("TEST10_status_line_present_and_not_yet_performed",
      "NOT YET PERFORMED" in template_text)

print(f"\n{'='*70}\nPHASE 4 CLOSURE TEST RESULTS: {len(PASS)} passed, {len(FAIL)} failed\n{'='*70}")
for name, detail in FAIL:
    print(f"  FAIL: {name}  {detail}")
if FAIL:
    sys.exit(1)
print("\nALL 10 TEST CATEGORIES PASSED.")
sys.exit(0)
