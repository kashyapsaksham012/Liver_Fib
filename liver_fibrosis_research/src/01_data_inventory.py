"""
01_data_inventory.py
Phase 1 Remediation - Raw File Inventory + Release Consistency + Readability Verification.

Produces:
  documentation/audit_reports/raw_file_inventory.csv
  documentation/audit_reports/raw_file_inventory.md
"""

import os, sys, csv, hashlib, datetime
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from _common import ROOT, RAW_DIR, AUDIT_DIR, REQUIRED_FILES, load_xpt, fail, NOW

def get_md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=== Step 1: Raw File Inventory, Readability & Release Consistency ===")

    missing_files = []
    for f in REQUIRED_FILES:
        p = RAW_DIR / f
        if not p.exists():
            p_upper = RAW_DIR / f.replace(".xpt", ".XPT")
            if p_upper.exists():
                os.rename(p_upper, p)
            else:
                missing_files.append(f)
    if missing_files:
        fail(f"The following required files are missing: {missing_files}. "
             f"Place them in data/raw/NHANES_2017_2020/ before continuing.")

    records = []
    release_cycles = set()
    for fname in REQUIRED_FILES:
        path = RAW_DIR / fname
        stat = path.stat()
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        checksum = get_md5(path)

        # Verify readability: must parse as a genuine SAS XPORT transport file, not HTML/error page.
        with open(path, "rb") as fh:
            header = fh.read(80)
        looks_like_xpt = header[:8] in (b"HEADER R", b"header r") or b"LIBRARY" in header.upper() or header[:1] != b"<"
        looks_like_html = header.strip().lower().startswith(b"<!doctype") or header.strip().lower().startswith(b"<html")

        try:
            df = load_xpt(fname)
            rows, cols = df.shape
            has_seqn = "SEQN" in df.columns
            if has_seqn:
                seqn_unique = int(df["SEQN"].nunique())
                seqn_missing = int(df["SEQN"].isna().sum())
                seqn_dups = int(rows - seqn_unique)
            else:
                seqn_unique = seqn_missing = seqn_dups = "N/A"
            err = None
            if "SDDSRVYR" in df.columns:
                release_cycles.update(df["SDDSRVYR"].dropna().unique().tolist())
        except Exception as e:
            rows = cols = has_seqn = seqn_unique = seqn_missing = seqn_dups = "N/A"
            err = str(e)

        records.append({
            "filename": fname, "extension": path.suffix.upper(),
            "size_bytes": stat.st_size, "size_human": f"{stat.st_size/1e6:.2f} MB",
            "file_modified": mtime, "md5_checksum": checksum,
            "rows": rows, "columns": cols, "has_seqn": has_seqn,
            "seqn_unique": seqn_unique, "seqn_missing": seqn_missing, "seqn_duplicates": seqn_dups,
            "looks_like_valid_xpt": looks_like_xpt and not looks_like_html,
            "load_error": err
        })
        print(f"  {fname}: {rows} rows x {cols} cols | Unique SEQN={seqn_unique} | dups={seqn_dups} | "
              f"valid_xpt_header={looks_like_xpt and not looks_like_html}")

    for r in records:
        if not r["looks_like_valid_xpt"] or r["load_error"]:
            fail(f"File {r['filename']} failed readability/format verification "
                 f"(valid_xpt_header={r['looks_like_valid_xpt']}, error={r['load_error']}).")

    if len(release_cycles) > 1:
        print(f"  NOTE: multiple SDDSRVYR release-cycle codes observed across files: {release_cycles}")
    print(f"  Release cycle consistency: SDDSRVYR = {release_cycles} across all files with that field "
          f"(single value expected for the 2017-March 2020 pre-pandemic combined release).")

    csv_path = AUDIT_DIR / "raw_file_inventory.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    md_path = AUDIT_DIR / "raw_file_inventory.md"
    with open(md_path, "w") as f:
        f.write("# Raw File Inventory\n\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Source Directory:** `{RAW_DIR}`  \n")
        f.write(f"**Files Found & Audited:** {len(records)}  \n")
        f.write(f"**Release cycle (SDDSRVYR) consistency:** {sorted(release_cycles)} "
                f"(single value = consistent release)\n\n")
        f.write("| Filename | Size | Rows | Cols | SEQN Found | Unique SEQN | Valid XPT Header | Load Status |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in records:
            status = "OK" if not r["load_error"] else f"ERROR: {r['load_error']}"
            f.write(f"| {r['filename']} | {r['size_human']} | {r['rows']} | {r['columns']} | "
                    f"{r['has_seqn']} | {r['seqn_unique']} | {r['looks_like_valid_xpt']} | {status} |\n")

    print("[STEP 1 COMPLETE]")

if __name__ == "__main__":
    main()
