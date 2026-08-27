"""Corrected Phase 3 BMI-sensitivity mitigation re-execution.

No locked-test file is opened until OOF development, candidate comparison, and selection
are complete. The previous Phase 3 outputs are historical and are not read or overwritten.
"""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             confusion_matrix, roc_auc_score)
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATA, PRED = ROOT/"data"/"processed", ROOT/"results"/"predictions"
OUT = ROOT/"results"/"fairness_bmi_investigation"/"phase3_corrected"
FIG = ROOT/"results"/"fairness_bmi_investigation"/"phase3_corrected_figures"
OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
MODELS = ["logistic","random_forest","xgboost","lightgbm","mlp"]
FROZEN = {"logistic":.5173,"random_forest":.4499,"xgboost":.4108,"lightgbm":.4988,"mlp":.1065}
CANDIDATES = ["original_frozen","bmi_thresholding","bmi_platt_calibration",
              "bmi_age_thresholding","combined_bmi_platt_thresholding"]
SEED = 20260826

def wilson(k,n):
    if not n: return (np.nan,np.nan)
    z=norm.ppf(.975); p=k/n; den=1+z*z/n
    c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0,c-h),min(1,c+h)
def logit(p):
    p=np.asarray(p); return np.log(np.clip(p,1e-12,1-1e-12)/np.clip(1-p,1e-12,1))
def fit_platt(p,y):
    return LogisticRegression(C=1e10,solver="lbfgs",max_iter=5000).fit(logit(p).reshape(-1,1),np.asarray(y))
def apply_platt(m,p): return m.predict_proba(logit(p).reshape(-1,1))[:,1]
def youden(y,p):
    from sklearn.metrics import roc_curve
    f,t,thr=roc_curve(y,p); return float(thr[np.argmax(t-f)])
def ece(y,p):
    out=0
    for lo,hi in zip(np.linspace(0,1,11)[:-1],np.linspace(0,1,11)[1:]):
        m=(p>=lo)&((p<hi) if hi<1 else (p<=hi))
        if m.any(): out += m.mean()*abs(y[m].mean()-p[m].mean())
    return out
def metric(y,p,t):
    pred=p>=t; tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    pos=int(y.sum()); neg=len(y)-pos
    return dict(n=len(y),positive_n=pos,negative_n=neg,prevalence=pos/len(y),
      sensitivity=tp/pos if pos else np.nan,specificity=tn/neg if neg else np.nan,
      fnr=fn/pos if pos else np.nan,ppv=tp/(tp+fp) if tp+fp else np.nan,
      npv=tn/(tn+fn) if tn+fn else np.nan,tp=int(tp),fn=int(fn),tn=int(tn),fp=int(fp))
def bootstrap_gap(d,p,t,n=400):
    d=d.reset_index(drop=True)
    rng=np.random.default_rng(SEED); vals=[]; ds=[]; ss=[]
    a=d[d.bmi_group_final=="Normal"]; b=d[d.bmi_group_final=="Obese"]
    for _ in range(n):
        ia=rng.integers(len(a),size=len(a)); ib=rng.integers(len(b),size=len(b))
        ma=metric(a.y.to_numpy()[ia],p[a.index.to_numpy()[ia]],t[a.index.to_numpy()[ia]])
        mb=metric(b.y.to_numpy()[ib],p[b.index.to_numpy()[ib]],t[b.index.to_numpy()[ib]])
        if np.isfinite(ma["sensitivity"]) and np.isfinite(mb["sensitivity"]):
            vals.append((mb["sensitivity"]-ma["sensitivity"])*100)
    return (float(np.quantile(vals,.025)),float(np.quantile(vals,.975))) if vals else (np.nan,np.nan)

def main():
    # Development-only load: OOF files and metadata linked exclusively to OOF IDs.
    oof={}; meta_parts=[]
    for model in MODELS:
        pth=PRED/f"validation_predictions_{model}.csv"; d=pd.read_csv(pth)
        oof[model]=d; meta_parts.append(d[["SEQN"]])
    ids=pd.concat(meta_parts).drop_duplicates()
    master=pd.read_parquet(DATA/"analysis_dataset_primary.parquet",
                           filters=[("SEQN","in",ids.SEQN.tolist())])
    meta=ids.merge(master[["SEQN","outcome_primary_8.2kPa","bmi_group_final","age_group_final"]],on="SEQN",validate="one_to_one")
    meta["y"]=meta["outcome_primary_8.2kPa"].astype(int)
    # Deterministic independent development split; no test IDs or test files are read.
    meta=meta.sort_values("SEQN").reset_index(drop=True)
    meta["dev_part"]=np.where(np.arange(len(meta))%2==0,"fit","eval")
    params={}; rows=[]; comparison=[]
    for model in MODELS:
        d=meta.merge(oof[model],on="SEQN",validate="one_to_one")
        fit=d[d.dev_part=="fit"]; ev=d[d.dev_part=="eval"]
        par={"global_threshold":FROZEN[model]}
        par["bmi_thresholds"]={g:youden(fit[fit.bmi_group_final==g].y,fit[fit.bmi_group_final==g].predicted_probability) for g in ["Normal","Obese"]}
        par["bmi_platt"]={g:fit_platt(fit[fit.bmi_group_final==g].predicted_probability,fit[fit.bmi_group_final==g].y) for g in ["Normal","Obese"]}
        pf=fit.predicted_probability.to_numpy(); pe=ev.predicted_probability.to_numpy()
        pf_cal=pf.copy()
        for g in ["Normal","Obese"]:
            m=(fit.bmi_group_final==g).to_numpy(); pf_cal[m]=apply_platt(par["bmi_platt"][g],pf[m])
        par["platt_global_threshold"]=youden(fit.y,pf_cal)
        par["combined_thresholds"]={g:youden(fit[fit.bmi_group_final==g].y,pf_cal[fit.bmi_group_final.to_numpy()==g]) for g in ["Normal","Obese"]}
        par["bmi_age_thresholds"]={}
        for age in ["18-39","40-59","60+"]:
            for g in ["Normal","Obese"]:
                z=fit[(fit.age_group_final==age)&(fit.bmi_group_final==g)]
                par["bmi_age_thresholds"][(age,g)]=youden(z.y,z.predicted_probability) if z.y.nunique()==2 and z.y.sum()>=10 and len(z)-z.y.sum()>=10 else None
        params[model]=par
        for cand in CANDIDATES:
            p=pe.copy(); t=np.full(len(ev),par["global_threshold"])
            if cand=="bmi_thresholding":
                for g in ["Normal","Obese"]: t[ev.bmi_group_final.to_numpy()==g]=par["bmi_thresholds"][g]
            elif cand=="bmi_platt_calibration":
                for g in ["Normal","Obese"]:
                    m=(ev.bmi_group_final==g).to_numpy(); p[m]=apply_platt(par["bmi_platt"][g],p[m])
                t[:]=par["platt_global_threshold"]
            elif cand=="bmi_age_thresholding":
                for age in ["18-39","40-59","60+"]:
                    for g in ["Normal","Obese"]:
                        m=((ev.age_group_final==age)&(ev.bmi_group_final==g)).to_numpy()
                        if par["bmi_age_thresholds"][(age,g)] is not None: t[m]=par["bmi_age_thresholds"][(age,g)]
            elif cand=="combined_bmi_platt_thresholding":
                for g in ["Normal","Obese"]:
                    m=(ev.bmi_group_final==g).to_numpy(); p[m]=apply_platt(par["bmi_platt"][g],p[m]); t[m]=par["combined_thresholds"][g]
            for scope,mask in [("OVERALL",np.ones(len(ev),bool)),
                               ("BMI_Normal",(ev.bmi_group_final=="Normal").to_numpy()),
                               ("BMI_Obese",(ev.bmi_group_final=="Obese").to_numpy()),
                               ("BMI_Underweight",(ev.bmi_group_final=="Underweight").to_numpy()),
                               ("BMI_Overweight",(ev.bmi_group_final=="Overweight").to_numpy())]+[
                               (f"AGE_{a}",(ev.age_group_final==a).to_numpy()) for a in ["18-39","40-59","60+"]]+[
                               (f"BMIxAGE_{g}_{a}",((ev.bmi_group_final==g)&(ev.age_group_final==a)).to_numpy()) for g in ["Normal","Obese"] for a in ["18-39","40-59","60+"]]:
                y=ev.y.to_numpy()[mask]; pp=p[mask]; tt=t[mask]
                z=metric(y,pp,tt[0] if np.all(tt==tt[0]) else np.nan)
                pred=pp>=tt; tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel(); pos=int(y.sum()); neg=len(y)-pos
                z.update(sensitivity=tp/pos if pos else np.nan,specificity=tn/neg if neg else np.nan,
                         fnr=fn/pos if pos else np.nan,ppv=tp/(tp+fp) if tp+fp else np.nan,npv=tn/(tn+fn) if tn+fn else np.nan,
                         tp=int(tp),fp=int(fp),tn=int(tn),fn=int(fn),model=model,candidate=cand,phase="OOF_EVAL",scope=scope,
                         auroc=roc_auc_score(y,pp) if len(np.unique(y))==2 else np.nan,pr_auc=average_precision_score(y,pp) if len(np.unique(y))==2 else np.nan,
                         brier=brier_score_loss(y,pp),ece=ece(y,pp),threshold_min=float(tt.min()),threshold_max=float(tt.max()),
                         sensitivity_ci_low=wilson(int(tp),pos)[0],sensitivity_ci_high=wilson(int(tp),pos)[1],
                         gap_ci_low=np.nan,gap_ci_high=np.nan,conformal_status="UNCHANGED_THRESHOLD_ONLY" if cand in ["original_frozen","bmi_thresholding","bmi_age_thresholding"] else "EVALUATED_SEPARATELY")
                rows.append(z)
            # Main comparison uses full-cohort OVERALL plus BMI groups.
            rr=pd.DataFrame(rows[-(5+3+6):]); n=rr[rr.scope=="BMI_Normal"].iloc[0]; o=rr[rr.scope=="BMI_Obese"].iloc[0]; allr=rr[rr.scope=="OVERALL"].iloc[0]
            lo,hi=bootstrap_gap(ev,p,t); comparison.append({"model":model,"candidate":cand,"phase":"OOF_EVAL",
              "normal_sensitivity":n.sensitivity,"obese_sensitivity":o.sensitivity,"obese_minus_normal_gap_pp":(o.sensitivity-n.sensitivity)*100,
              "gap_ci_low_pp":lo,"gap_ci_high_pp":hi,"overall_sensitivity":allr.sensitivity,"overall_specificity":allr.specificity,
              "auroc":allr.auroc,"pr_auc":allr.pr_auc,"brier":allr.brier,"ece":allr.ece,
              "age_60_minus_40_gap_pp":abs(float(rr[rr.scope=="AGE_60+"].sensitivity.iloc[0])-float(rr[rr.scope=="AGE_40-59"].sensitivity.iloc[0]))*100})
    result=pd.DataFrame(rows); comp=pd.DataFrame(comparison)
    chosen={}
    for model in MODELS:
        base=comp[(comp.model==model)&(comp.candidate=="original_frozen")].iloc[0]
        eligible=comp[(comp.model==model)&(comp.overall_sensitivity>=base.overall_sensitivity-.05)&
          (comp.overall_specificity>=base.overall_specificity-.05)&(comp.brier<=base.brier+.01)&
          (comp.age_60_minus_40_gap_pp<=base.age_60_minus_40_gap_pp+5)]
        chosen[model]=(eligible.assign(abs_gap=eligible.obese_minus_normal_gap_pp.abs()).sort_values(["abs_gap","overall_specificity"],ascending=[True,False]).candidate.iloc[0] if len(eligible) else "original_frozen")
    comp["selection_status"]=comp.apply(lambda r:"SELECTED_OOF" if chosen[r.model]==r.candidate else "NOT_SELECTED",axis=1)
    result.to_csv(OUT/"phase3_corrected_candidate_mitigation_results.csv",index=False)
    comp.to_csv(OUT/"phase3_corrected_mitigation_comparison.csv",index=False)

    # Development conformal split check, performed before any test access.
    conf_rows=[]; cal_ids=pd.read_csv(DATA/"splits/conformal_calibration_ids.csv").SEQN
    cal_master=pd.read_parquet(DATA/"analysis_dataset_primary.parquet",
                               filters=[("SEQN","in",cal_ids.tolist())])
    cal=cal_master.copy().sort_values("SEQN"); cal["part"]=np.where(np.arange(len(cal))%2==0,"fit","eval")
    refit=ROOT/"models"/"phase6_conformal_refit"
    for model in MODELS:
        pipe=joblib.load(refit/f"model_{model}_proper_train_refit.joblib")["pipeline"]
        for cand in CANDIDATES:
            cf=cal[cal.part=="fit"]; ce=cal[cal.part=="eval"]; pf=pipe.predict_proba(cf[["RIDAGEYR","RIAGENDR","BMXBMI","LBXSATSI","LBXSASSI","LBXSAL","LBXSAPSI","LBXSTB","LBXPLTSI","LBDHDD"]])[:,1]; pe=pipe.predict_proba(ce[["RIDAGEYR","RIAGENDR","BMXBMI","LBXSATSI","LBXSASSI","LBXSAL","LBXSAPSI","LBXSTB","LBXPLTSI","LBDHDD"]])[:,1]
            # Probability-changing candidates use the OOF-fitted BMI Platt maps; thresholds do not affect sets.
            if cand in ["bmi_platt_calibration","combined_bmi_platt_thresholding"]:
                pf2,p2=pf.copy(),pe.copy()
                for g in ["Normal","Obese"]:
                    mf=(cf.bmi_group_final==g).to_numpy(); me=(ce.bmi_group_final==g).to_numpy()
                    pf2[mf]=apply_platt(params[model]["bmi_platt"][g],pf[mf]); p2[me]=apply_platt(params[model]["bmi_platt"][g],pe[me])
                pf,pe=pf2,p2
            scores=1-np.where(cf["outcome_primary_8.2kPa"].to_numpy()==1,pf,1-pf); k=int(np.ceil((len(scores)+1)*.9)); q=float(np.sort(scores)[k-1])
            true=ce["outcome_primary_8.2kPa"].to_numpy(); inc=np.where(true==1,(1-pe)<=q,pe<=q); size=((1-pe)<=q).astype(int)+(pe<=q).astype(int)
            conf_rows.append({"model":model,"candidate":cand,"phase":"CONFORMAL_DEV_SPLIT","calibration_fit_n":len(cf),"evaluation_n":len(ce),"coverage":float(inc.mean()),"mean_set_size":float(size.mean()),"singleton_rate":float((size==1).mean()),"doubleton_rate":float((size==2).mean()),"threshold":q,"status":"EVALUATED"})
    pd.DataFrame(conf_rows).to_csv(OUT/"phase3_corrected_conformal_development.csv",index=False)
    # Freeze manifest before loading any test file.
    manifest={"seed":SEED,"development_split":"OOF rows sorted by SEQN; even index fit, odd index independent evaluation",
      "selection_gate":"full-cohort sensitivity/specificity >= baseline-5pp; Brier <= baseline+0.01; Age60-vs40 gap <= baseline+5pp; then smallest absolute BMI gap",
      "chosen":chosen,"parameters":{m:{
          k:(v if not isinstance(v,dict) else {str(a):str(b) for a,b in v.items()})
          for k,v in params[m].items()
          if k != "bmi_platt"} | {
          "bmi_platt_coefficients": {
              g: {"intercept": float(params[m]["bmi_platt"][g].intercept_[0]),
                  "slope": float(params[m]["bmi_platt"][g].coef_[0][0])}
              for g in ["Normal","Obese"]}}
          for m in MODELS},
      "test_access":"NOT YET ACCESSED DURING DEVELOPMENT; this manifest freezes selection before test loading"}
    (OUT/"phase3_corrected_selection_manifest.json").write_text(json.dumps(manifest,indent=2,default=str))

    # Only now load locked-test predictions and metadata.
    test_ids=pd.read_csv(DATA/"splits/test_ids.csv").SEQN
    test_master=pd.read_parquet(DATA/"analysis_dataset_primary.parquet",
                                filters=[("SEQN","in",test_ids.tolist())]).copy()
    test_rows=[]
    for model in MODELS:
        td=test_master.merge(pd.read_csv(PRED/f"test_predictions_{model}.csv"),on="SEQN",validate="one_to_one")
        for cand in ["original_frozen",chosen[model]]:
            p=td.predicted_probability.to_numpy().copy(); t=np.full(len(td),params[model]["global_threshold"])
            if cand=="bmi_thresholding":
                for g in ["Normal","Obese"]: t[td.bmi_group_final.to_numpy()==g]=params[model]["bmi_thresholds"][g]
            elif cand=="bmi_platt_calibration":
                for g in ["Normal","Obese"]:
                    m=(td.bmi_group_final==g).to_numpy(); p[m]=apply_platt(params[model]["bmi_platt"][g],p[m])
                t[:]=params[model]["platt_global_threshold"]
            elif cand=="bmi_age_thresholding":
                for age in ["18-39","40-59","60+"]:
                    for g in ["Normal","Obese"]:
                        m=((td.age_group_final==age)&(td.bmi_group_final==g)).to_numpy()
                        if params[model]["bmi_age_thresholds"][(age,g)] is not None: t[m]=params[model]["bmi_age_thresholds"][(age,g)]
            elif cand=="combined_bmi_platt_thresholding":
                for g in ["Normal","Obese"]:
                    m=(td.bmi_group_final==g).to_numpy(); p[m]=apply_platt(params[model]["bmi_platt"][g],p[m]); t[m]=params[model]["combined_thresholds"][g]
            y=td["outcome_primary_8.2kPa"].to_numpy()
            for scope,mask in [("OVERALL",np.ones(len(td),bool)),("BMI_Normal",(td.bmi_group_final=="Normal").to_numpy()),("BMI_Obese",(td.bmi_group_final=="Obese").to_numpy())]+[(f"AGE_{a}",(td.age_group_final==a).to_numpy()) for a in ["18-39","40-59","60+"]]+[(f"BMIxAGE_{g}_{a}",((td.bmi_group_final==g)&(td.age_group_final==a)).to_numpy()) for g in ["Normal","Obese"] for a in ["18-39","40-59","60+"]]:
                yy=y[mask]; pp=p[mask]; tt=t[mask]; pred=pp>=tt; tn,fp,fn,tp=confusion_matrix(yy,pred,labels=[0,1]).ravel(); pos=int(yy.sum()); neg=len(yy)-pos; lo,hi=wilson(int(tp),pos)
                test_rows.append({"model":model,"candidate":cand,"phase":"LOCKED_TEST_CONFIRMATION","scope":scope,"n":len(yy),"positive_n":pos,"negative_n":neg,"sensitivity":tp/pos if pos else np.nan,"sensitivity_ci_low":lo,"sensitivity_ci_high":hi,"specificity":tn/neg if neg else np.nan,"fnr":fn/pos if pos else np.nan,"ppv":tp/(tp+fp) if tp+fp else np.nan,"npv":tn/(tn+fn) if tn+fn else np.nan,"auroc":roc_auc_score(yy,pp) if len(np.unique(yy))==2 else np.nan,"pr_auc":average_precision_score(yy,pp) if len(np.unique(yy))==2 else np.nan,"brier":brier_score_loss(yy,pp),"ece":ece(yy,pp),"calibration_intercept":float(fit_platt(pp,yy).intercept_[0]) if len(np.unique(yy))==2 else np.nan,"calibration_slope":float(fit_platt(pp,yy).coef_[0][0]) if len(np.unique(yy))==2 else np.nan,"tp":int(tp),"fn":int(fn),"tn":int(tn),"fp":int(fp),"conformal_status":"SEE_PHASE7_FOR_UNCHANGED_THRESHOLD; PROBABILITY_CANDIDATE_DEVELOPMENT_REPORTED_SEPARATELY"})
    test_out=pd.DataFrame(test_rows); test_out.to_csv(OUT/"phase3_corrected_locked_test_confirmation.csv",index=False)
    trade=[]
    for model in MODELS:
        cand=chosen[model]; b=comp[(comp.model==model)&(comp.candidate=="original_frozen")].iloc[0]; q=comp[(comp.model==model)&(comp.candidate==cand)].iloc[0]
        trade.append({"model":model,"selected_candidate":cand,"oof_gap_change_pp":q.obese_minus_normal_gap_pp-b.obese_minus_normal_gap_pp,"oof_gap_ci_low_pp":q.gap_ci_low_pp,"oof_gap_ci_high_pp":q.gap_ci_high_pp,"oof_sensitivity_change_pp":(q.overall_sensitivity-b.overall_sensitivity)*100,"oof_specificity_change_pp":(q.overall_specificity-b.overall_specificity)*100,"oof_auroc_change":q.auroc-b.auroc,"oof_brier_change":q.brier-b.brier,"selection_gate":manifest["selection_gate"]})
    pd.DataFrame(trade).to_csv(OUT/"phase3_corrected_tradeoff_analysis.csv",index=False)
    lineage={"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"oof_hashes":{m:hashlib.sha256((PRED/f"validation_predictions_{m}.csv").read_bytes()).hexdigest() for m in MODELS},"test_hashes":{m:hashlib.sha256((PRED/f"test_predictions_{m}.csv").read_bytes()).hexdigest() for m in MODELS},"selection_manifest":"written before test load","previous_outputs_preserved":True}
    (OUT/"phase3_corrected_lineage.json").write_text(json.dumps(lineage,indent=2))
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,5)); x=np.arange(len(MODELS)); b=[];s=[]
    for m in MODELS:
        b.append(comp[(comp.model==m)&(comp.candidate=="original_frozen")].obese_minus_normal_gap_pp.iloc[0]); s.append(comp[(comp.model==m)&(comp.candidate==chosen[m])].obese_minus_normal_gap_pp.iloc[0])
    ax.bar(x-.18,b,.36,label="Original"); ax.bar(x+.18,s,.36,label="Selected"); ax.set_xticks(x,MODELS,rotation=20); ax.set_ylabel("Obese - Normal sensitivity (pp)"); ax.legend(); fig.tight_layout(); fig.savefig(FIG/"corrected_oof_gap.png",dpi=160); plt.close(fig)
    return chosen
if __name__=="__main__": print(main())
