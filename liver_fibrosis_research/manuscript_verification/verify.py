#!/usr/bin/env python3
"""
Manuscript number-verification harness
======================================

Purpose
-------
For every numeric claim registered in `checks.py`, open the frozen result
artifact it cites, extract the value the same way the manuscript should have,
and assert it matches what the manuscript prints (within a stated tolerance).

Also scans a manuscript file for draft-state hedges ("should confirm",
"needs regeneration", "[author list to confirm]", TODO, ...).

Design
------
- Standard library only (csv, re, json, argparse, pathlib). No pandas, no yaml.
- Read-only. Touches nothing in `results/`, `data/`, `models/`, `documentation/`.
- Non-zero exit code if any check FAILs or ERRORs (use in CI / pre-commit).

Usage
-----
    python3 manuscript_verification/verify.py
    python3 manuscript_verification/verify.py --manuscript documentation/manuscript/MANUSCRIPT_DRAFT.md
    python3 manuscript_verification/verify.py --strict      # also fail on hedges
    python3 manuscript_verification/verify.py --only DISC-01,GEN-01
    python3 manuscript_verification/verify.py --json

Extend
------
Add entries to CHECKS in `checks.py`. Each entry documents one manuscript
sentence. See the docstring there for the schema and the supported `kind`s.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(__file__).resolve().parent / "report"

# --------------------------------------------------------------------------- #
# CSV helpers
# --------------------------------------------------------------------------- #

_NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?$")
_TRUE = {"true", "1", "yes", "y", "t"}
_FALSE = {"false", "0", "no", "n", "f"}


def _to_float(x):
    if x is None:
        return None
    s = str(x).strip().strip('"').strip()
    if s == "" or s.lower() in {"na", "nan", "none", "null"}:
        return None
    s = s.replace(",", "")
    if _NUM_RE.match(s):
        return float(s)
    return None


def _to_bool(x):
    s = str(x).strip().strip('"').strip().lower()
    if s in _TRUE:
        return True
    if s in _FALSE:
        return False
    return None


def _norm(x):
    return str(x).strip().strip('"').strip().lower()


def load_rows(rel_path: str):
    p = REPO_ROOT / rel_path
    if not p.exists():
        raise FileNotFoundError(rel_path)
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def apply_filter(rows, flt):
    """flt: {column: value | [values]}. Case-insensitive string match, with a
    numeric fallback so 0.9 matches "0.90"."""
    if not flt:
        return rows
    out = []
    for r in rows:
        ok = True
        for col, want in flt.items():
            if col not in r:
                ok = False
                break
            have = r[col]
            wants = want if isinstance(want, (list, tuple)) else [want]
            matched = False
            for w in wants:
                if _norm(have) == _norm(w):
                    matched = True
                    break
                hv, wv = _to_float(have), _to_float(w)
                if hv is not None and wv is not None and abs(hv - wv) < 1e-9:
                    matched = True
                    break
            if not matched:
                ok = False
                break
        if ok:
            out.append(r)
    return out


def _col_values(rows, column, abs_value=False):
    vals = []
    for r in rows:
        v = _to_float(r.get(column))
        if v is None:
            raise ValueError(f"non-numeric / missing value in column '{column}'")
        vals.append(abs(v) if abs_value else v)
    return vals


# --------------------------------------------------------------------------- #
# Check kinds
# --------------------------------------------------------------------------- #

def _fmt(v):
    return f"{v:.4g}" if isinstance(v, float) else str(v)


def run_check(chk: dict):
    """Return (status, manuscript_str, artifact_str, detail).
    status in {PASS, FAIL, ERROR}."""
    kind = chk["kind"]
    sources = chk["source"]
    if isinstance(sources, str):
        sources = [sources]

    try:
        # Most checks read one source; multi-source checks name the primary first.
        rows = load_rows(sources[0])
        rows = apply_filter(rows, chk.get("filter"))
        tol = float(chk.get("tol", 0.01))

        if not rows and kind not in {"count"}:
            return ("ERROR", str(chk.get("expected")), "0 rows after filter",
                    f"filter {chk.get('filter')} matched no rows in {sources[0]}")

        # ---------------- band ----------------
        if kind == "band":
            vals = _col_values(rows, chk["column"], chk.get("abs_value", False))
            lo, hi = min(vals), max(vals)
            exp_lo, exp_hi = chk["expected"]["low"], chk["expected"]["high"]
            ok = abs(lo - exp_lo) <= tol and abs(hi - exp_hi) <= tol
            return (("PASS" if ok else "FAIL"),
                    f"{exp_lo}–{exp_hi}",
                    f"{lo:.4f}–{hi:.4f}  (n={len(vals)})",
                    f"tol={tol}")

        # ---------------- all_in_range ----------------
        if kind == "all_in_range":
            vals = _col_values(rows, chk["column"], chk.get("abs_value", False))
            lo, hi = chk["expected"]["low"], chk["expected"]["high"]
            bad = [v for v in vals if not (lo - tol <= v <= hi + tol)]
            return (("PASS" if not bad else "FAIL"),
                    f"all in [{lo}, {hi}]",
                    f"range {min(vals):.4f}–{max(vals):.4f}, n={len(vals)}"
                    + ("" if not bad else f", OUT: {[round(b,4) for b in bad]}"),
                    f"tol={tol}")

        # ---------------- scalar ----------------
        if kind == "scalar":
            vals = _col_values(rows, chk["column"], chk.get("abs_value", False))
            uniq = sorted(set(round(v, 6) for v in vals))
            exp = float(chk["expected"])
            if len(uniq) != 1:
                return ("FAIL", str(exp), f"{len(uniq)} distinct values: {uniq}",
                        "expected a single value after filter")
            ok = abs(uniq[0] - exp) <= tol
            return (("PASS" if ok else "FAIL"), str(exp), f"{uniq[0]:.6g}",
                    f"tol={tol}")

        # ---------------- per_key_scalar ----------------
        if kind == "per_key_scalar":
            key_col = chk["key_column"]
            col = chk["column"]
            fails = []
            checked = 0
            for key, exp in chk["expected"].items():
                sub = [r for r in rows if _norm(r.get(key_col)) == _norm(key)]
                if not sub:
                    fails.append(f"{key}: no row")
                    continue
                v = _to_float(sub[0].get(col))
                if chk.get("abs_value"):
                    v = abs(v) if v is not None else None
                checked += 1
                if v is None or abs(v - float(exp)) > tol:
                    fails.append(f"{key}: want {exp}, got {_fmt(v)}")
            return (("PASS" if not fails else "FAIL"),
                    "; ".join(f"{k}={v}" for k, v in chk["expected"].items()),
                    f"{checked}/{len(chk['expected'])} matched"
                    + ("" if not fails else "  | " + "; ".join(fails)),
                    f"tol={tol}")

        # ---------------- count ----------------
        if kind == "count":
            where_true = chk.get("where_true")   # bool column
            where_false = chk.get("where_false")
            if where_true:
                m = [r for r in rows if _to_bool(r.get(where_true)) is True]
            elif where_false:
                m = [r for r in rows if _to_bool(r.get(where_false)) is False]
            else:
                m = rows
            exp = chk["expected"]
            got = len(m)
            detail = ""
            if "of" in chk:
                detail = f" of {len(rows)} rows"
                if chk["of"] != len(rows):
                    return ("FAIL", f"{exp} of {chk['of']}",
                            f"{got} of {len(rows)}",
                            "row-count denominator changed")
            ok = got == exp
            return (("PASS" if ok else "FAIL"), f"{exp}{detail}",
                    f"{got}{detail}", "")

        # ---------------- bool_all ----------------
        if kind == "bool_all":
            col = chk["column"]
            exp = bool(chk["expected"])
            got = [(_to_bool(r.get(col))) for r in rows]
            bad = sum(1 for g in got if g is not exp)
            return (("PASS" if bad == 0 else "FAIL"),
                    f"all {col} == {exp} (n={len(got)})",
                    f"{len(got)-bad}/{len(got)} == {exp}", "")

        # ---------------- sign_all ----------------
        if kind == "sign_all":
            vals = _col_values(rows, chk["column"])
            want = chk["expected"]  # "neg" or "pos"
            if want == "neg":
                bad = [v for v in vals if v >= 0]
            else:
                bad = [v for v in vals if v <= 0]
            return (("PASS" if not bad else "FAIL"),
                    f"all {want} (n={len(vals)})",
                    f"{len(vals)-len(bad)}/{len(vals)} {want}"
                    + ("" if not bad else f", violations: {[round(b,3) for b in bad]}"),
                    "")

        # ---------------- topk_set ----------------
        if kind == "topk_set":
            gcol = chk.get("group_column")  # None -> treat all rows as one group
            scol = chk["sort_column"]
            lcol = chk["label_column"]
            k = int(chk["k"])
            exp = set(_norm(x) for x in chk["expected"])
            abs_sort = chk.get("abs_value_sort", False)
            groups = {}
            for r in rows:
                groups.setdefault(r.get(gcol) if gcol else "__all__", []).append(r)
            fails = []

            def _sortkey(r):
                v = _to_float(r.get(scol))
                if v is None:
                    return float("-inf")
                return abs(v) if abs_sort else v

            for g, grows in groups.items():
                grows.sort(key=_sortkey, reverse=True)
                topset = set(_norm(r.get(lcol)) for r in grows[:k])
                if topset != exp:
                    fails.append(f"{g}: {sorted(topset)}")
            scope = f"every {gcol}" if gcol else "the ranking"
            return (("PASS" if not fails else "FAIL"),
                    f"top-{k} == {sorted(exp)} for {scope}",
                    f"{len(groups)-len(fails)}/{len(groups)} groups match"
                    + ("" if not fails else "  | " + "; ".join(fails)),
                    "")

        return ("ERROR", "", "", f"unknown check kind '{kind}'")

    except FileNotFoundError as e:
        return ("ERROR", "", "", f"source artifact not found: {e}")
    except (KeyError, ValueError) as e:
        return ("ERROR", "", "", f"{type(e).__name__}: {e}")


# --------------------------------------------------------------------------- #
# Hedge scan
# --------------------------------------------------------------------------- #

HEDGE_PATTERNS = [
    r"should (?:be )?(?:confirm|regenerat|re-?run|verif)",
    r"needs? (?:to be |updating|regeneration|regenerating|a rerun|re-?run)",
    r"before (?:inclusion|a? ?final|submission|treating (?:them|it) as final)",
    r"to be (?:confirmed|completed|added|done|finalis|finaliz)",
    r"\[author list to confirm\]",
    r"\bTODO\b|\bFIXME\b|\bXXX\b",
    r"we recommend confirming",
    r"internal inconsistency|cross-?check source",
    r"a separate summary document",
    r"placeholder|tbd\b|to be determined",
    r"figure should be regenerated",
    r"not yet (?:run|executed|computed|verified)",
]
_HEDGE_RE = re.compile("|".join(f"(?:{p})" for p in HEDGE_PATTERNS), re.IGNORECASE)

# lines that are allowed to mention these words (changelog / provenance prose)
HEDGE_ALLOW_SUBSTR = [
    "a co-author should repeat",   # explicit process note in the ref-verification pointer
]


def scan_hedges(manuscript_path: Path):
    if not manuscript_path.exists():
        return None
    hits = []
    for i, line in enumerate(manuscript_path.read_text(encoding="utf-8").splitlines(), 1):
        if _HEDGE_RE.search(line):
            if any(s in line for s in HEDGE_ALLOW_SUBSTR):
                continue
            hits.append((i, line.strip()))
    return hits


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manuscript", default="documentation/manuscript/MANUSCRIPT_DRAFT.md",
                    help="manuscript file to hedge-scan (repo-relative)")
    ap.add_argument("--only", default="", help="comma-separated check ids to run")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if hedges are found too")
    ap.add_argument("--json", action="store_true", help="also print machine-readable JSON")
    ap.add_argument("--no-write", action="store_true", help="don't write report/ files")
    args = ap.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from checks import CHECKS  # noqa: E402

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    checks = [c for c in CHECKS if not only or c["id"] in only]

    results = []
    for chk in checks:
        status, man, art, detail = run_check(chk)
        results.append({
            "id": chk["id"],
            "claim_id": chk.get("claim_id", ""),
            "section": chk.get("section", ""),
            "statement": chk.get("statement", ""),
            "source": chk["source"] if isinstance(chk["source"], str) else "; ".join(chk["source"]),
            "status": status,
            "manuscript_says": man,
            "artifact_says": art,
            "detail": detail,
        })

    n_pass = sum(r["status"] == "PASS" for r in results)
    n_fail = sum(r["status"] == "FAIL" for r in results)
    n_err = sum(r["status"] == "ERROR" for r in results)

    # ---- console ----
    ICON = {"PASS": "  ok ", "FAIL": " FAIL", "ERROR": " ERR "}
    print("\n" + "=" * 78)
    print("MANUSCRIPT NUMBER VERIFICATION")
    print("=" * 78)
    for r in results:
        print(f"[{ICON[r['status']]}] {r['id']:<14} {r['section']}")
        print(f"          claim : {r['statement']}")
        print(f"          says  : {r['manuscript_says']}")
        print(f"          found : {r['artifact_says']}")
        if r["status"] != "PASS":
            print(f"          source: {r['source']}")
            if r["detail"]:
                print(f"          note  : {r['detail']}")
    print("-" * 78)
    print(f"  {n_pass} passed   {n_fail} failed   {n_err} error   ({len(results)} checks)")

    # ---- hedge scan ----
    hedge_hits = scan_hedges(REPO_ROOT / args.manuscript)
    print("-" * 78)
    if hedge_hits is None:
        print(f"  hedge scan: SKIPPED (manuscript not found: {args.manuscript})")
    elif not hedge_hits:
        print(f"  hedge scan: clean ({args.manuscript})")
    else:
        print(f"  hedge scan: {len(hedge_hits)} draft-state phrase(s) in {args.manuscript}")
        for ln, text in hedge_hits:
            print(f"     L{ln}: {text[:140]}")
    print("=" * 78 + "\n")

    # ---- files ----
    if not args.no_write:
        OUT_DIR.mkdir(exist_ok=True)
        with (OUT_DIR / "verification_report.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)
        md = ["# Manuscript number-verification report", "",
              f"- checks: **{len(results)}**  |  passed: **{n_pass}**  |  "
              f"failed: **{n_fail}**  |  error: **{n_err}**", ""]
        md += ["| id | section | status | manuscript says | artifact says | source |",
               "|---|---|---|---|---|---|"]
        for r in results:
            md.append(f"| {r['id']} | {r['section']} | **{r['status']}** | "
                      f"{r['manuscript_says']} | {r['artifact_says']} | `{r['source']}` |")
        md += ["", "## Hedge scan", ""]
        if hedge_hits is None:
            md.append(f"skipped — `{args.manuscript}` not found")
        elif not hedge_hits:
            md.append(f"clean — no draft-state phrases in `{args.manuscript}`")
        else:
            md.append(f"`{args.manuscript}` — {len(hedge_hits)} phrase(s):\n")
            for ln, text in hedge_hits:
                md.append(f"- **L{ln}** — {text}")
        (OUT_DIR / "verification_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"  wrote {OUT_DIR/'verification_report.md'}")
        print(f"  wrote {OUT_DIR/'verification_report.csv'}\n")

    if args.json:
        print(json.dumps({"summary": {"pass": n_pass, "fail": n_fail, "error": n_err},
                          "results": results,
                          "hedges": hedge_hits or []}, indent=2))

    bad = n_fail + n_err + (len(hedge_hits or []) if args.strict else 0)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
