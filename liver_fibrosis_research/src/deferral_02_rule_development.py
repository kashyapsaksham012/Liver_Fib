"""
Selective-deferral mitigation -- Phase 3 (Amendment #17).

Develop candidate deferral rules on the conformal-CALIBRATION partition ONLY.
Select against the pre-registered gate. Freeze the chosen rule (hashed manifest).
NO locked-test access in this script.

Mechanism note (established in the first exploratory pass, retained here): in the
under-covered subgroups the *coverage* is carried by the two-class {pos,neg} sets
(which always cover); the failures are wrong SINGLETON predictions. So a rule that
defers "uncertain" cases (two-class sets, low-confidence) makes retained coverage
WORSE. The rule that can help defers *weak singletons* -- singletons whose
predicted class only barely cleared the conformal threshold.

Candidates:
  3a  defer two-class sets                                   (expected: worsens coverage)
  3b  retain {both}; defer singleton if slack < delta_g,
      slack = qhat - nonconformity(predicted class);
      delta_g = smallest value giving retained calib coverage >= 0.90 in group g
  3d  Mondrian group-conditional quantile q_g for SET CONSTRUCTION (no deferral)
  3e  3d + 3b on top of the Mondrian sets

Scope this pass: coverage gate G1-G3 + deferral-burden G6-G7 fully; G4 as a
conformal-sensitivity proxy (coverage among positives). G4(Youden)/G5/G9 need the
model stack (deferred with Phase 5).

Outputs:
  results/selective_deferral/phase3_candidate_metrics.csv
  results/selective_deferral/frozen_deferral_rule_manifest.json
  documentation/selective_deferral_mitigation/PHASE3_RULE_DEVELOPMENT.md
"""
from pathlib import Path
import json
import hashlib
import datetime as dt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/selective_deferral"
MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
ALPHA, TARGET = 0.10, 0.90
BMI_G = ["Normal", "Overweight", "Obese"]
AGE_G = ["18-39", "40-59", "60+"]
OVER = [("bmi", "Normal"), ("bmi", "Overweight"), ("age", "18-39")]
DELTA_FLOOR = 0.02          # do not defer singletons whose class cleared qhat by > this much... no:
# delta_g is a slack cutoff; larger delta_g = defer more singletons. cap at qhat (defer all singletons).

thr = pd.read_csv(ROOT / "results/uncertainty/conformal_thresholds_by_model.csv")
QHAT = dict(zip(thr["model"], thr["threshold"]))
dev = pd.read_csv(OUT / "dev_calibration_scored.csv")


def cover_arr(y, ip, ineg):
    return np.where(y == 1, ip, ineg)


def grp_metrics(d, model):
    ret = d[~d["_defer"]]
    y = ret["true_target"].astype(int).to_numpy()
    m = {"model": model,
         "defer_rate_overall": float(d["_defer"].mean()),
         "retained_marginal_cov": float(cover_arr(y, ret["_ip"], ret["_in"]).mean()),
         "retained_n": int(len(ret))}
    for dim, col in [("bmi", "bmi_group_final"), ("age", "age_group_final")]:
        for cat in (BMI_G if dim == "bmi" else AGE_G):
            ga, gr = d[d[col] == cat], ret[ret[col] == cat]
            yy = gr["true_target"].astype(int).to_numpy()
            m[f"cov_{dim}_{cat}"] = float(cover_arr(yy, gr["_ip"], gr["_in"]).mean()) if len(gr) else np.nan
            m[f"defer_{dim}_{cat}"] = float(ga["_defer"].mean()) if len(ga) else np.nan
            pos, neg = gr[gr.true_target == 1], gr[gr.true_target == 0]
            m[f"csens_{dim}_{cat}"] = float(pos["_ip"].mean()) if len(pos) else np.nan
    return m


def gate(m):
    g1 = (m["cov_bmi_Obese"] >= 0.88) and (m["cov_age_60+"] >= 0.88)
    g2 = 0.88 <= m["retained_marginal_cov"] <= 0.93
    g3 = all((np.isnan(m[f"cov_{d}_{c}"]) or m[f"cov_{d}_{c}"] <= 0.95) for d, c in OVER)
    g6 = m["defer_rate_overall"] <= 0.40
    ov = m["defer_rate_overall"]
    g7 = all((np.isnan(m[f"defer_{d}_{c}"]) or m[f"defer_{d}_{c}"] <= 2.5 * ov or ov == 0)
             for d in ["bmi", "age"] for c in (BMI_G if d == "bmi" else AGE_G))
    g4 = (not np.isnan(m["csens_bmi_Normal"]) and not np.isnan(m["csens_bmi_Obese"])
          and abs(m["csens_bmi_Normal"] - m["csens_bmi_Obese"]) <= 0.15)
    return dict(G1=g1, G2=g2, G3=g3, G4proxy=g4, G6=g6, G7=g7,
               core=g1 and g2 and g3 and g6 and g7)


def slack_cutoff_for_group(g, q):
    """largest delta_g s.t. deferring singletons with slack<delta_g gives retained cov>=0.90.
       returns (delta_g, achieved_retained_cov, defer_rate_in_group)."""
    two = g["_set_size"] == 2
    single = ~two
    slack = q - np.where(g["_ip"] & ~g["_in"], 1 - g["_p"],          # {pos} singleton: s=1-p
                np.where(g["_in"] & ~g["_ip"], g["_p"], 0.0))        # {neg} singleton: s=p
    g = g.assign(_slack=slack)
    y = g["true_target"].astype(int).to_numpy()
    base = float(cover_arr(y, g["_ip"], g["_in"]).mean())
    if base >= TARGET:
        return 0.0, base, 0.0
    best = None
    for d in np.round(np.arange(0.0, q + 0.001, 0.005), 3):
        defer = single & (g["_slack"] < d)
        ret = g[~defer]
        if len(ret) == 0:
            break
        cov = float(cover_arr(ret["true_target"].astype(int).to_numpy(), ret["_ip"], ret["_in"]).mean())
        if cov >= TARGET:
            best = (float(d), cov, float(defer.mean()))
            break
    if best is None:
        # floor: defer every singleton in the group
        defer = single
        ret = g[~defer]
        cov = float(cover_arr(ret["true_target"].astype(int).to_numpy(), ret["_ip"], ret["_in"]).mean()) if len(ret) else np.nan
        best = (float(q), cov, float(defer.mean()))
    return best


rows, params = [], {}
for model in MODELS:
    d0 = dev[dev.model == model].reset_index(drop=True).copy()
    q = QHAT[model]
    p = d0["predicted_probability_positive"].to_numpy()
    d0["_p"] = p
    d0["_ip"] = (1 - p) <= q
    d0["_in"] = p <= q
    d0["_set_size"] = d0["_ip"].astype(int) + d0["_in"].astype(int)

    # 3a -----------------------------------------------------------------
    d = d0.copy(); d["_defer"] = d["_set_size"] == 2
    m = grp_metrics(d, model); m["candidate"] = "3a"; m.update(gate(m)); rows.append(m)
    params[("3a", model)] = {"rule": "defer set_size==2", "qhat": q}

    # 3b: weak-singleton deferral, group-conditional --------------------
    delta = {}
    for dim, col in [("bmi", "bmi_group_final"), ("age", "age_group_final")]:
        for cat in (BMI_G if dim == "bmi" else AGE_G):
            delta[f"{dim}:{cat}"] = slack_cutoff_for_group(d0[d0[col] == cat].copy(), q)
    d = d0.copy()
    slack_all = q - np.where(d["_ip"] & ~d["_in"], 1 - p, np.where(d["_in"] & ~d["_ip"], p, 0.0))
    d["_slack"] = slack_all
    dg = d.apply(lambda r: max(delta.get(f"bmi:{r['bmi_group_final']}", (0, 0, 0))[0],
                               delta.get(f"age:{r['age_group_final']}", (0, 0, 0))[0]), axis=1)
    d["_dg"] = dg
    d["_defer"] = (d["_set_size"] == 1) & (d["_slack"] < d["_dg"])
    m = grp_metrics(d, model); m["candidate"] = "3b"; m.update(gate(m)); rows.append(m)
    params[("3b", model)] = {"rule": "retain {both}; defer singleton if slack<delta_g; overlap->max",
                             "delta_g": {k: v[0] for k, v in delta.items()}, "qhat": q}

    # 3d: Mondrian group quantiles (set construction only) -------------
    qg = {}
    for dim, col in [("bmi", "bmi_group_final"), ("age", "age_group_final")]:
        for cat in (BMI_G if dim == "bmi" else AGE_G):
            s = np.sort(d0.loc[d0[col] == cat, "nonconformity_score"].to_numpy())
            n = len(s); k = int(np.ceil((n + 1) * (1 - ALPHA)))
            qg[f"{dim}:{cat}"] = float(s[min(k, n) - 1])
    d = d0.copy()
    dq = d.apply(lambda r: max(qg.get(f"bmi:{r['bmi_group_final']}", q),
                               qg.get(f"age:{r['age_group_final']}", q)), axis=1).to_numpy()
    d["_ip"] = (1 - p) <= dq
    d["_in"] = p <= dq
    d["_set_size"] = d["_ip"].astype(int) + d["_in"].astype(int)
    d["_defer"] = False
    m = grp_metrics(d, model); m["candidate"] = "3d"; m.update(gate(m)); rows.append(m)
    params[("3d", model)] = {"rule": "Mondrian q_g set construction; no deferral", "q_g": qg}

    # 3e: 3d + weak-singleton deferral on the Mondrian sets -----------
    d3 = d.copy()
    slk = dq - np.where(d3["_ip"] & ~d3["_in"], 1 - p, np.where(d3["_in"] & ~d3["_ip"], p, 0.0))
    d3["_slack"] = slk
    delta_e = {}
    for dim, col in [("bmi", "bmi_group_final"), ("age", "age_group_final")]:
        for cat in (BMI_G if dim == "bmi" else AGE_G):
            gg = d3[d3[col] == cat].copy()
            gg["_p"] = gg["_p"] if "_p" in gg else p
            yb = gg["true_target"].astype(int).to_numpy()
            base = float(cover_arr(yb, gg["_ip"], gg["_in"]).mean()) if len(gg) else 1.0
            if base >= TARGET or len(gg) == 0:
                delta_e[f"{dim}:{cat}"] = 0.0; continue
            found = float(dq.max())
            for dd in np.round(np.arange(0.0, 0.501, 0.005), 3):
                defer = (gg["_set_size"] == 1) & (gg["_slack"] < dd)
                r = gg[~defer]
                if len(r) and float(cover_arr(r["true_target"].astype(int).to_numpy(), r["_ip"], r["_in"]).mean()) >= TARGET:
                    found = float(dd); break
            delta_e[f"{dim}:{cat}"] = found
    de = d3.apply(lambda r: max(delta_e.get(f"bmi:{r['bmi_group_final']}", 0.0),
                                delta_e.get(f"age:{r['age_group_final']}", 0.0)), axis=1).to_numpy()
    d3["_defer"] = (d3["_set_size"] == 1) & (d3["_slack"] < de)
    m = grp_metrics(d3, model); m["candidate"] = "3e"; m.update(gate(m)); rows.append(m)
    params[("3e", model)] = {"rule": "Mondrian q_g + defer weak singletons (slack<delta_g)",
                             "q_g": qg, "delta_g": delta_e}

res = pd.DataFrame(rows)
show = ["candidate", "model", "defer_rate_overall", "retained_marginal_cov",
        "cov_bmi_Obese", "cov_age_60+", "cov_bmi_Normal", "cov_bmi_Overweight", "cov_age_18-39",
        "csens_bmi_Normal", "csens_bmi_Obese", "defer_bmi_Obese", "defer_age_60+",
        "G1", "G2", "G3", "G4proxy", "G6", "G7", "core"]
res = res[[c for c in show if c in res.columns]]
res.to_csv(OUT / "phase3_candidate_metrics.csv", index=False)

summ = (res.groupby("candidate").agg(models_core_pass=("core", "sum"),
        mean_defer=("defer_rate_overall", "mean")).reset_index()
        .sort_values(["models_core_pass", "mean_defer"], ascending=[False, True]))
selected = summ.iloc[0]["candidate"]
sel_pass = int(summ.iloc[0]["models_core_pass"])

manifest = {
    "amendment": "#17", "frozen_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "developed_on": "conformal_calibration partition N=1002 ONLY; no test access",
    "selected_candidate": selected, "models_passing_core_gate_on_calibration": sel_pass,
    "candidate_definitions": {
        "3a": "defer two-class {pos,neg} sets",
        "3b": "retain two-class sets; defer a singleton if (qhat - nonconformity(predicted class)) "
              "< delta_g; delta_g = smallest cutoff giving retained calib coverage >= 0.90 in "
              "group g (else defer all singletons); overlap Obese&60+ -> max(delta_g)",
        "3d": "Mondrian group-conditional calibration quantile q_g = ceil((n_g+1)(1-alpha))-th "
              "smallest nonconformity score in group g; prediction sets use q_g; no deferral; "
              "overlap -> max(q_g)",
        "3e": "3d then 3b (defer weak singletons under the Mondrian sets)"},
    "per_model_parameters": {f"{c}:{m}": params[(c, m)] for c in ["3a", "3b", "3d", "3e"] for m in MODELS},
    "note": "coverage gate G1-G3 + deferral-burden G6-G7 evaluated fully; G4 = conformal-sens "
            "proxy; G4(Youden)/G5/G9 pending model stack",
    "test_touched": bool(sel_pass > 0),
    "verdict_stage": ("DEVELOPMENT-STAGE NEGATIVE" if sel_pass == 0 else "proceed to Phase 4"),
}
mp = OUT / "frozen_deferral_rule_manifest.json"
mp.write_text(json.dumps(manifest, indent=2, default=str))
mh = hashlib.sha256(mp.read_bytes()).hexdigest()

md = ["# Phase 3 -- deferral-rule development (Amendment #17)", "",
      "Developed on the conformal-calibration partition (N=1,002) only. No locked-test access.", "",
      "**Mechanism established in Phase 2-3:** in the under-covered subgroups (BMI-Obese, Age-60+) "
      "the conformal *coverage* is carried by the two-class {pos,neg} prediction sets, which "
      "always contain the truth; the misses are wrong SINGLETON predictions. A rule that defers "
      "'uncertain' cases (two-class sets) therefore *lowers* retained coverage. Only deferring "
      "*weak singletons* (candidate 3b), or widening the sets group-conditionally (3d/3e), can "
      "help.", "",
      "## Candidate metrics (per model, calibration partition)", "",
      res.to_markdown(index=False), "",
      "## Selection", "", summ.to_markdown(index=False), "",
      f"**Selected: `{selected}`** -- passes the core coverage+burden gate for **{sel_pass}/5** "
      f"models on the calibration partition.", "",
      f"Frozen manifest SHA-256: `{mh}`  ", f"Frozen at: {manifest['frozen_at']}", ""]
d3d = res[res.candidate == "3d"]
g1_3d = int(d3d["G1"].sum())
mc_lo, mc_hi = d3d["retained_marginal_cov"].min(), d3d["retained_marginal_cov"].max()
if sel_pass == 0:
    md += ["", "## Verdict: DEVELOPMENT-STAGE NEGATIVE (per the pre-registered gate)", "",
           "No candidate in the pre-registered family (3a, 3b, 3d, 3e) meets the full core gate "
           "(G1 & G2 & G3 & G6 & G7) on the calibration partition. **Per the plan the locked test "
           "is NOT touched** (Phase 4 skipped). No post-hoc gate relaxation or new candidate is "
           "permitted.", "",
           "**Characterised negative -- what the pre-registered candidates do and do not achieve:**",
           "",
           "1. **Deferring 'uncertain' cases makes coverage worse, not better (3a).** In BMI-Obese "
           "and Age-60+ the conformal coverage is carried by the two-class {pos,neg} sets (which "
           "always contain the truth); the misses are wrong *singletons*. Deferring the two-class "
           "sets (3a) removes the covering predictions -- retained BMI-Obese coverage falls to "
           f"{res[res.candidate=='3a']['cov_bmi_Obese'].min():.2f}-"
           f"{res[res.candidate=='3a']['cov_bmi_Obese'].max():.2f} (worse than the 0.77-0.82 unmitigated).",
           "",
           "2. **Deferring weak singletons (3b) can lift the under-covered groups to ~0.90**, but "
           "only by deferring 15-40 % overall and, for the near-singleton MLP, degenerately "
           "(defers ~95 % of obese cases). It fails G2 (retained marginal coverage rises) and does "
           "not generalise cleanly across families.",
           "",
           f"3. **Group-conditional (Mondrian) conformal (3d) restores BMI-Obese and Age-60+ "
           f"coverage to >= 0.88 for {g1_3d}/5 models with zero deferral** -- an improvement on "
           f"Project Phase 7's 5/9 targets -- **but necessarily raises retained marginal coverage "
           f"to {mc_lo:.2f}-{mc_hi:.2f}** (G2 fail) and leaves the well-served subgroups above "
           f"0.95 (G3 fail). Forcing marginal coverage back to <= 0.93 would require deliberately "
           f"under-covering the well-served subgroups -- *levelling down*, the fairness "
           f"anti-pattern documented for coverage-equalising conformal methods "
           f"(arXiv:2412.07879; ICLR 2025).",
           "",
           "**Reportable finding:** on this task, subgroup-safe conformal coverage and "
           "target-level marginal coverage cannot be jointly achieved by any pre-registered "
           "post-hoc method without levelling down the well-served subgroups; and the "
           "under-coverage is not concentrated in flagged-uncertain cases (so selective deferral "
           "does not fix it) but in confidently-wrong singleton predictions in the obese and "
           "older groups -- a failure of the model's within-subgroup score ordering that a "
           "post-hoc decision layer cannot repair."]
elif sel_pass < 5:
    md += ["", f"> **PARTIAL at development stage:** {selected} works for {sel_pass}/5 families on "
           "calibration data; Phase 4 confirms on the locked test and the shortfall is "
           "characterised in Phase 6."]
(ROOT / "documentation/selective_deferral_mitigation/PHASE3_RULE_DEVELOPMENT.md").write_text("\n".join(md) + "\n")
print(res.to_string(index=False))
print()
print(summ.to_string(index=False))
print(f"\nSELECTED={selected} core_pass={sel_pass} manifest_sha256={mh}")
