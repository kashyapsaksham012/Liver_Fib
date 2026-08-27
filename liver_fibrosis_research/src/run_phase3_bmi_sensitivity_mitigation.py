"""Separate Phase 3 BMI-sensitivity mitigation protocol.

Candidate parameters are derived from OOF predictions only. Existing Phase 7 conformal
artifacts are read-only prior work and are not used as the BMI-sensitivity solution.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             roc_auc_score, confusion_matrix)

ROOT = Path(__file__).resolve().parents[1]
DATA, PRED = ROOT / "data" / "processed", ROOT / "results" / "predictions"
OUT, FIG = ROOT / "results" / "fairness_bmi_investigation", ROOT / "results" / "fairness_bmi_investigation" / "figures" / "phase3"
OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
MODELS = ["logistic", "random_forest", "xgboost", "lightgbm", "mlp"]
THR = {"logistic": .5173, "random_forest": .4499, "xgboost": .4108, "lightgbm": .4988, "mlp": .1065}

def wilson(k, n):
    if n == 0: return (np.nan, np.nan)
    z = norm.ppf(.975); p = k/n; den = 1 + z*z/n
    c = (p + z*z/(2*n))/den
    h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return max(0, c-h), min(1, c+h)

def cal_fit(p, y):
    p = np.asarray(p); y = np.asarray(y)
    z = np.log(np.clip(p, 1e-12, 1-1e-12) / np.clip(1-p, 1e-12, 1))
    m = LogisticRegression(C=1e10, solver="lbfgs", max_iter=5000).fit(z.reshape(-1, 1), y)
    return m

def cal_apply(m, p):
    p = np.asarray(p)
    z = np.log(np.clip(p, 1e-12, 1-1e-12) / np.clip(1-p, 1e-12, 1))
    return m.predict_proba(z.reshape(-1, 1))[:, 1]

def youden(y, p):
    from sklearn.metrics import roc_curve
    fpr, tpr, t = roc_curve(y, p)
    return float(t[np.argmax(tpr-fpr)])

def metric(y, p, t):
    pred = p >= t; tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    n, pos = len(y), int(y.sum()); neg = n-pos
    return {"n": n, "positive_n": pos, "negative_n": neg, "prevalence": pos/n,
            "sensitivity": tp/pos if pos else np.nan, "specificity": tn/neg if neg else np.nan,
            "ppv": tp/(tp+fp) if tp+fp else np.nan, "npv": tn/(tn+fn) if tn+fn else np.nan,
            "tp": int(tp), "fn": int(fn), "tn": int(tn), "fp": int(fp)}

def ece(y, p):
    out = 0
    for lo, hi in zip(np.linspace(0,1,11)[:-1], np.linspace(0,1,11)[1:]):
        m = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        if m.any(): out += m.mean()*abs(y[m].mean()-p[m].mean())
    return out

def main():
    master = pd.read_parquet(DATA/"analysis_dataset_primary.parquet")
    train_ids = set(pd.read_csv(DATA/"splits/train_ids.csv").SEQN)
    test_ids = set(pd.read_csv(DATA/"splits/test_ids.csv").SEQN)
    if train_ids & test_ids: raise RuntimeError("train/test overlap")
    meta = master[["SEQN","outcome_primary_8.2kPa","bmi_group_final","age_group_final"]].copy()
    meta["y"] = meta["outcome_primary_8.2kPa"].astype(int)
    valid = meta.bmi_group_final.isin(["Normal","Obese"])
    meta = meta[valid].copy()
    oofs, tests = {}, {}
    for model in MODELS:
        o = pd.read_csv(PRED/f"validation_predictions_{model}.csv").merge(meta, on="SEQN", validate="one_to_one")
        t = pd.read_csv(PRED/f"test_predictions_{model}.csv").merge(meta, on="SEQN", validate="one_to_one")
        if not set(o.SEQN).issubset(train_ids) or not set(t.SEQN).issubset(test_ids): raise RuntimeError("split lineage failure")
        oofs[model], tests[model] = o, t

    # The candidate rules are frozen here, before any locked-test evaluation:
    # baseline; BMI-specific Youden; BMI-specific Platt + global transformed Youden;
    # BMI×age Youden; combined BMI-specific Platt + BMI-specific Youden.
    candidates = ["original_frozen", "bmi_youden", "bmi_platt_global_youden", "bmi_age_youden", "bmi_platt_youden"]
    params, rows = {}, []
    for model in MODELS:
        o = oofs[model]; y = o.y.to_numpy(); p = o.predicted_probability.to_numpy()
        pars = {"global_threshold": THR[model]}
        bmi_thr = {g: youden(o[o.bmi_group_final==g].y, o[o.bmi_group_final==g].predicted_probability) for g in ["Normal","Obese"]}
        pars["bmi_thresholds"] = bmi_thr
        bmi_cal = {g: cal_fit(o[o.bmi_group_final==g].predicted_probability, o[o.bmi_group_final==g].y) for g in ["Normal","Obese"]}
        pc = p.copy()
        for g in ["Normal","Obese"]:
            m = o.bmi_group_final.to_numpy()==g; pc[m] = cal_apply(bmi_cal[g], p[m])
        pars["bmi_platt_global_threshold"] = youden(y, pc); pars["bmi_cal"] = bmi_cal
        ba_thr = {}
        for age in ["18-39","40-59","60+"]:
            for bmi in ["Normal","Obese"]:
                z=o[(o.age_group_final==age)&(o.bmi_group_final==bmi)]
                ba_thr[(age,bmi)] = youden(z.y, z.predicted_probability) if z.y.nunique()==2 and z.y.sum()>=10 and (len(z)-z.y.sum())>=10 else None
        pars["bmi_age_thresholds"] = ba_thr
        pars["bmi_platt_thresholds"] = {g: youden(o[o.bmi_group_final==g].y, pc[o.bmi_group_final.to_numpy()==g]) for g in ["Normal","Obese"]}
        params[model] = pars

    def scores(model, d, candidate):
        p = d.predicted_probability.to_numpy(); y = d.y.to_numpy()
        par = params[model]; outp = p.copy(); outt = np.full(len(d), par["global_threshold"])
        if candidate == "original_frozen": return outp, outt
        if candidate == "bmi_youden":
            for g in ["Normal","Obese"]: outt[d.bmi_group_final.to_numpy()==g] = par["bmi_thresholds"][g]
        elif candidate == "bmi_platt_global_youden":
            for g in ["Normal","Obese"]:
                m = d.bmi_group_final.to_numpy()==g; outp[m] = cal_apply(par["bmi_cal"][g], outp[m])
            outt[:] = par["bmi_platt_global_threshold"]
        elif candidate == "bmi_age_youden":
            for age in ["18-39","40-59","60+"]:
                for g in ["Normal","Obese"]:
                    m = (d.age_group_final==age).to_numpy() & (d.bmi_group_final==g).to_numpy()
                    if par["bmi_age_thresholds"][(age,g)] is not None: outt[m] = par["bmi_age_thresholds"][(age,g)]
        elif candidate == "bmi_platt_youden":
            for g in ["Normal","Obese"]:
                m = d.bmi_group_final.to_numpy()==g; outp[m] = cal_apply(par["bmi_cal"][g], outp[m]); outt[m] = par["bmi_platt_thresholds"][g]
        return outp, outt

    def evaluate(model, d, candidate, phase):
        p, ts = scores(model, d, candidate); y = d.y.to_numpy()
        def add(scope, mask):
            z = metric(y[mask], p[mask], ts[mask][0] if np.all(ts[mask]==ts[mask][0]) else np.nan)
            # metric with varying cell thresholds:
            pred = p[mask] >= ts[mask]; yy=y[mask]; tn,fp,fn,tp=confusion_matrix(yy,pred,labels=[0,1]).ravel()
            pos=int(yy.sum()); neg=len(yy)-pos
            z.update(sensitivity=tp/pos if pos else np.nan, specificity=tn/neg if neg else np.nan,
                     ppv=tp/(tp+fp) if tp+fp else np.nan, npv=tn/(tn+fn) if tn+fn else np.nan,
                     fnr=fn/pos if pos else np.nan,
                     tp=int(tp),fn=int(fn),tn=int(tn),fp=int(fp))
            cal_int=cal_slope=np.nan
            if len(np.unique(yy))==2:
                cm=cal_fit(p[mask],yy); cal_int=float(cm.intercept_[0]); cal_slope=float(cm.coef_[0][0])
            z.update(model=model, candidate=candidate, phase=phase, scope=scope,
                     auroc=roc_auc_score(yy,p[mask]) if len(np.unique(yy))==2 else np.nan,
                     pr_auc=average_precision_score(yy,p[mask]) if len(np.unique(yy))==2 else np.nan,
                     brier=brier_score_loss(yy,p[mask]), ece=ece(yy,p[mask]),
                     calibration_intercept=cal_int, calibration_slope=cal_slope,
                     threshold_min=float(np.min(ts[mask])), threshold_max=float(np.max(ts[mask])))
            lo,hi=wilson(int(tp),pos); z.update(sensitivity_ci_low=lo,sensitivity_ci_high=hi)
            rows.append(z)
        add("ALL", np.ones(len(d),dtype=bool))
        for g in ["Normal","Obese"]: add(f"BMI_{g}", (d.bmi_group_final==g).to_numpy())
        for a in ["18-39","40-59","60+"]: add(f"AGE_{a}", (d.age_group_final==a).to_numpy())
        for a in ["18-39","40-59","60+"]:
            for g in ["Normal","Obese"]: add(f"BMIxAGE_{g}_{a}", ((d.bmi_group_final==g)&(d.age_group_final==a)).to_numpy())

    # OOF candidate comparison and pre-test selection.
    for model in MODELS:
        for c in candidates: evaluate(model,oofs[model],c,"OOF")
    oof_df=pd.DataFrame(rows)
    comp=[]
    for model in MODELS:
        for c in candidates:
            z=oof_df[(oof_df.model==model)&(oof_df.candidate==c)]
            n=float(z.loc[z.scope=="BMI_Normal","sensitivity"].iloc[0]); ob=float(z.loc[z.scope=="BMI_Obese","sensitivity"].iloc[0])
            allr=z.loc[z.scope=="ALL"].iloc[0]; agegap=abs(float(z.loc[z.scope=="AGE_60+","sensitivity"].iloc[0])-float(z.loc[z.scope=="AGE_40-59","sensitivity"].iloc[0]))
            comp.append({"model":model,"candidate":c,"phase":"OOF","normal_sensitivity":n,"obese_sensitivity":ob,
                "obese_minus_normal_gap_pp":(ob-n)*100,"overall_sensitivity":allr.sensitivity,"overall_specificity":allr.specificity,
                "auroc":allr.auroc,"pr_auc":allr.pr_auc,"brier":allr.brier,"ece":allr.ece,"age_60_minus_40_gap_pp":agegap*100})
    comp=pd.DataFrame(comp)
    chosen={}
    for model in MODELS:
        base=comp[(comp.model==model)&(comp.candidate=="original_frozen")].iloc[0]
        eligible=comp[(comp.model==model)&(comp.overall_specificity >= base.overall_specificity-.05)&
                      (comp.overall_sensitivity >= base.overall_sensitivity-.05)&
                      (comp.brier <= base.brier+.01)&(comp.age_60_minus_40_gap_pp <= base.age_60_minus_40_gap_pp+5)]
        chosen[model] = (eligible.assign(abs_gap=eligible.obese_minus_normal_gap_pp.abs())
                         .sort_values(["abs_gap","overall_specificity"],ascending=[True,False]).candidate.iloc[0]
                         if len(eligible) else "original_frozen")
    comp["selection_status"]=comp.apply(lambda r:"SELECTED_OOF" if chosen[r.model]==r.candidate else "NOT_SELECTED",axis=1)
    comp.to_csv(OUT/"phase3_mitigation_comparison.csv",index=False)
    oof_df.to_csv(OUT/"phase3_candidate_mitigation_results.csv",index=False)

    # One confirmatory locked-test evaluation after selection was frozen.
    test_rows=[]; old_rows=len(rows)
    for model in MODELS:
        for c in ["original_frozen",chosen[model]] if chosen[model]!="original_frozen" else ["original_frozen"]:
            before=len(rows); evaluate(model,tests[model],c,"LOCKED_TEST"); test_rows.extend(rows[before:])
    test_df=pd.DataFrame(test_rows); test_df.to_csv(OUT/"phase3_locked_test_confirmation.csv",index=False)
    trade=[]
    for model in MODELS:
        c=chosen[model]
        b=comp[(comp.model==model)&(comp.candidate=="original_frozen")].iloc[0]
        q=comp[(comp.model==model)&(comp.candidate==c)].iloc[0]
        trade.append({"model":model,"selected_candidate":c,"oof_gap_change_pp":q.obese_minus_normal_gap_pp-b.obese_minus_normal_gap_pp,
                      "oof_specificity_change_pp":(q.overall_specificity-b.overall_specificity)*100,
                      "oof_auroc_change":q.auroc-b.auroc,"oof_brier_change":q.brier-b.brier,
                      "selection_gate":"specificity >= baseline-5pp; sensitivity >= baseline-5pp; Brier <= baseline+0.01; Age60-vs40 gap <= baseline+5pp"})
    pd.DataFrame(trade).to_csv(OUT/"phase3_tradeoff_analysis.csv",index=False)
    lineage={"oof_hashes":{m:hashlib.sha256((PRED/f"validation_predictions_{m}.csv").read_bytes()).hexdigest() for m in MODELS},
             "test_hashes":{m:hashlib.sha256((PRED/f"test_predictions_{m}.csv").read_bytes()).hexdigest() for m in MODELS},
             "selection_rule":"predefined multi-metric OOF gate; locked test evaluated once after selection",
             "chosen":chosen,"old_phase7_separate":True}
    (OUT/"phase3_lineage.json").write_text(json.dumps(lineage,indent=2,default=str))
    # simple trade-off figure
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,5)); x=np.arange(len(MODELS)); basev=[]; selv=[]
    for m in MODELS:
        basev.append(comp[(comp.model==m)&(comp.candidate=="original_frozen")].obese_minus_normal_gap_pp.iloc[0])
        selv.append(comp[(comp.model==m)&(comp.candidate==chosen[m])].obese_minus_normal_gap_pp.iloc[0])
    ax.bar(x-.18,basev,.36,label="Original"); ax.bar(x+.18,selv,.36,label="Selected"); ax.axhline(0,color="k",lw=.7)
    ax.set_xticks(x,MODELS,rotation=20); ax.set_ylabel("Obese - Normal sensitivity (pp)"); ax.set_title("OOF BMI sensitivity gap")
    ax.legend(); fig.tight_layout(); fig.savefig(FIG/"oof_gap_original_vs_selected.png",dpi=160); plt.close(fig)
    return chosen

if __name__=="__main__":
    print(main())
