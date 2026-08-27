"""Phase 4 subgroup-calibration reliability investigation.

Development is independent OOF fit/evaluation data. Test files are opened only after the
selection manifest is written. Prior exploratory outputs are read-only and not overwritten.
"""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score
import joblib

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"/"processed"; PRED=ROOT/"results"/"predictions"
OUT=ROOT/"results"/"fairness_bmi_investigation"/"phase4_subgroup_calibration"; FIG=ROOT/"results"/"fairness_bmi_investigation"/"phase4_figures"
OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
MODELS=["logistic","random_forest","xgboost","lightgbm","mlp"]; SEED=20260826
FROZEN={"logistic":.5173,"random_forest":.4499,"xgboost":.4108,"lightgbm":.4988,"mlp":.1065}
FEATURES=["RIDAGEYR","RIAGENDR","BMXBMI","LBXSATSI","LBXSASSI","LBXSAL","LBXSAPSI","LBXSTB","LBXPLTSI","LBDHDD"]

def wilson(k,n):
    if not n:return(np.nan,np.nan)
    z=norm.ppf(.975);p=k/n;den=1+z*z/n;c=(p+z*z/(2*n))/den;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n));return(max(0,c-h),min(1,c+h))
def logit(p):
    p=np.asarray(p);return np.log(np.clip(p,1e-12,1-1e-12)/np.clip(1-p,1e-12,1))
def fit(p,y):return LogisticRegression(C=1e10,solver="lbfgs",max_iter=5000).fit(logit(p).reshape(-1,1),np.asarray(y))
def apply(m,p):return m.predict_proba(logit(p).reshape(-1,1))[:,1]
def ece(y,p):
    z=0
    for lo,hi in zip(np.linspace(0,1,11)[:-1],np.linspace(0,1,11)[1:]):
        m=(p>=lo)&((p<hi) if hi<1 else (p<=hi))
        if m.any():z+=m.mean()*abs(y[m].mean()-p[m].mean())
    return z
def metrics(y,p,decision=None):
    pred=p>=.5 if decision is None else np.asarray(decision).astype(bool)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel();pos=int(y.sum());neg=len(y)-pos
    cal=fit(p,y) if len(np.unique(y))==2 else None
    return dict(n=len(y),positive_n=pos,negative_n=neg,prevalence=pos/len(y),sensitivity=tp/pos if pos else np.nan,
      specificity=tn/neg if neg else np.nan,ppv=tp/(tp+fp) if tp+fp else np.nan,npv=tn/(tn+fn) if tn+fn else np.nan,
      auroc=roc_auc_score(y,p) if len(np.unique(y))==2 else np.nan,pr_auc=average_precision_score(y,p) if len(np.unique(y))==2 else np.nan,
      brier=brier_score_loss(y,p),ece=ece(y,p),calibration_intercept=float(cal.intercept_[0]) if cal else np.nan,
      calibration_slope=float(cal.coef_[0][0]) if cal else np.nan,tp=int(tp),fp=int(fp),tn=int(tn),fn=int(fn))

def main():
    # Only OOF-linked development metadata are loaded before selection.
    oof={}; ids=None
    for m in MODELS:
        d=pd.read_csv(PRED/f"validation_predictions_{m}.csv");oof[m]=d;ids=d[["SEQN"]] if ids is None else ids.merge(d[["SEQN"]],on="SEQN")
    ids=ids.drop_duplicates()
    master=pd.read_parquet(DATA/"analysis_dataset_primary.parquet",filters=[("SEQN","in",ids.SEQN.tolist())])
    meta=ids.merge(master[["SEQN","outcome_primary_8.2kPa","bmi_group_final","age_group_final"]],on="SEQN",validate="one_to_one")
    meta["y"]=meta["outcome_primary_8.2kPa"].astype(int);meta=meta.sort_values("SEQN").reset_index(drop=True);meta["part"]=np.where(np.arange(len(meta))%2==0,"fit","eval")
    candidates=["global_platt","subgroup_platt_bmi_age"]; rows=[]; comp=[]
    cal_params={}
    for model in MODELS:
        d=meta.merge(oof[model],on="SEQN",validate="one_to_one"); f=d[d.part=="fit"];ev=d[d.part=="eval"]
        global_cal=fit(f.predicted_probability,f.y); params={"global":global_cal,"cells":{}}
        for dim,vals in [("bmi_group_final",["Underweight","Normal","Overweight","Obese"]),("age_group_final",["18-39","40-59","60+"])]:
            for v in vals:
                z=f[f[dim]==v]
                if len(z)>=20 and z.y.sum()>=10 and len(z)-z.y.sum()>=10: params["cells"][(dim,v)]=fit(z.predicted_probability,z.y)
        cal_params[model]=params
        for cand in candidates:
            p=ev.predicted_probability.to_numpy().copy()
            if cand=="global_platt":p=apply(global_cal,p)
            else:
                for i,(b,a) in enumerate(zip(ev.bmi_group_final,ev.age_group_final)):
                    # Prefer BMI cell, then age cell, otherwise global; no sparse cell is fitted.
                    cm=params["cells"].get(("bmi_group_final",b),params["cells"].get(("age_group_final",a),global_cal))
                    p[i]=apply(cm,[p[i]])[0]
            for scope,mask in [("OVERALL",np.ones(len(ev),bool))]+[(f"BMI_{v}",(ev.bmi_group_final==v).to_numpy()) for v in ["Underweight","Normal","Overweight","Obese"]]+[(f"AGE_{v}",(ev.age_group_final==v).to_numpy()) for v in ["18-39","40-59","60+"]]+[(f"BMIxAGE_{b}_{a}",((ev.bmi_group_final==b)&(ev.age_group_final==a)).to_numpy()) for b in ["Underweight","Normal","Overweight","Obese"] for a in ["18-39","40-59","60+"]]:
                y=ev.y.to_numpy()[mask];pp=p[mask];decision=ev.predicted_probability.to_numpy()[mask]>=FROZEN[model];z=metrics(y,pp,decision);z.update(model=model,candidate=cand,phase="OOF_EVAL",scope=scope,
                  sensitivity_ci_low=wilson(z["tp"],z["positive_n"])[0],sensitivity_ci_high=wilson(z["tp"],z["positive_n"])[1],
                  cell_status="UNSTABLE_SMALL_CELL" if z["positive_n"]<10 or z["negative_n"]<10 else "ESTIMABLE",
                  conformal_status="EVALUATED_SEPARATELY" if cand=="subgroup_platt_bmi_age" else "PROBABILITIES_GLOBAL_PLATT")
                rows.append(z)
            r=pd.DataFrame(rows[-(1+4+3+12):]);n=r[r.scope=="BMI_Normal"].iloc[0];o=r[r.scope=="BMI_Obese"].iloc[0];allr=r[r.scope=="OVERALL"].iloc[0];age=r[r.scope=="AGE_60+"].iloc[0];mid=r[r.scope=="AGE_40-59"].iloc[0]
            comp.append({"model":model,"candidate":cand,"phase":"OOF_EVAL","normal_sensitivity":n.sensitivity,"obese_sensitivity":o.sensitivity,"bmi_gap_pp":(o.sensitivity-n.sensitivity)*100,
              "overall_sensitivity":allr.sensitivity,"overall_specificity":allr.specificity,"auroc":allr.auroc,"pr_auc":allr.pr_auc,"brier":allr.brier,"ece":allr.ece,
              "age_60_minus_40_gap_pp":(age.sensitivity-mid.sensitivity)*100})
    result=pd.DataFrame(rows);comparison=pd.DataFrame(comp)
    chosen={}
    for model in MODELS:
        b=comparison[(comparison.model==model)&(comparison.candidate=="global_platt")].iloc[0]
        q=comparison[(comparison.model==model)&(comparison.candidate=="subgroup_platt_bmi_age")].iloc[0]
        # Predefined safety gate; subgroup method is accepted only when reliability improves
        # without a >5pp safety/fairness deterioration. Otherwise retain global calibration.
        improve=(q.ece < b.ece and q.brier <= b.brier+.01 and q.overall_sensitivity >= b.overall_sensitivity-.05 and q.overall_specificity >= b.overall_specificity-.05 and abs(q.age_60_minus_40_gap_pp)<=abs(b.age_60_minus_40_gap_pp)+5)
        chosen[model]="subgroup_platt_bmi_age" if improve else "global_platt"
    comparison["selection_status"]=comparison.apply(lambda r:"SELECTED_OOF" if chosen[r.model]==r.candidate else "NOT_SELECTED",axis=1)
    result.to_csv(OUT/"phase4_calibration_results.csv",index=False);comparison.to_csv(OUT/"phase4_subgroup_calibration_results.csv",index=False)
    # Independent conformal development comparison, before any test access.
    cal_ids=pd.read_csv(DATA/"splits/conformal_calibration_ids.csv").SEQN; cmaster=pd.read_parquet(DATA/"analysis_dataset_primary.parquet",filters=[("SEQN","in",cal_ids.tolist())]);cmaster=cmaster.sort_values("SEQN");cmaster["part"]=np.where(np.arange(len(cmaster))%2==0,"fit","eval")
    conf=[];refit=ROOT/"models"/"phase6_conformal_refit"
    for model in MODELS:
        pipe=joblib.load(refit/f"model_{model}_proper_train_refit.joblib")["pipeline"];cf=cmaster[cmaster.part=="fit"];ce=cmaster[cmaster.part=="eval"];pf=pipe.predict_proba(cf[FEATURES])[:,1];pe=pipe.predict_proba(ce[FEATURES])[:,1]
        for cand in candidates:
            if cand=="subgroup_platt_bmi_age":
                for g in ["Underweight","Normal","Overweight","Obese"]:
                    z=cf[cf.bmi_group_final==g]
                    if len(z)>=20 and z["outcome_primary_8.2kPa"].sum()>=10 and len(z)-z["outcome_primary_8.2kPa"].sum()>=10:
                        mm=fit(pf[cf.bmi_group_final.to_numpy()==g],z["outcome_primary_8.2kPa"]);pf[cf.bmi_group_final.to_numpy()==g]=apply(mm,pf[cf.bmi_group_final.to_numpy()==g]);pe[ce.bmi_group_final.to_numpy()==g]=apply(mm,pe[ce.bmi_group_final.to_numpy()==g])
            s=1-np.where(cf["outcome_primary_8.2kPa"].to_numpy()==1,pf,1-pf);k=int(np.ceil((len(s)+1)*.9));q=float(np.sort(s)[k-1]);y=ce["outcome_primary_8.2kPa"].to_numpy();inc=np.where(y==1,(1-pe)<=q,pe<=q);size=((1-pe)<=q).astype(int)+(pe<=q).astype(int)
            conf.append({"model":model,"candidate":cand,"phase":"CONFORMAL_DEV_SPLIT","fit_n":len(cf),"eval_n":len(ce),"coverage":inc.mean(),"mean_set_size":size.mean(),"singleton_rate":(size==1).mean(),"doubleton_rate":(size==2).mean(),"status":"EVALUATED"})
    pd.DataFrame(conf).to_csv(OUT/"phase4_conformal_comparison.csv",index=False)
    manifest={"seed":SEED,"development_split":"OOF sorted SEQN even fit / odd evaluation","candidates":candidates,"selection_rule":"subgroup selected only if ECE improves, Brier within +0.01, overall sensitivity/specificity within 5pp, and Age60-vs40 gap within +5pp","chosen":chosen,"calibration_cells":"BMI/age cells require >=20 rows and >=10 positives and negatives; otherwise global fallback","test_access":"manifest written before test files loaded"}
    (OUT/"phase4_selection_manifest.json").write_text(json.dumps(manifest,indent=2))
    lineage={"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"oof_hashes":{m:hashlib.sha256((PRED/f"validation_predictions_{m}.csv").read_bytes()).hexdigest() for m in MODELS},"selection_manifest":"written before test access","prior_exploratory_artifact":"results/diagnostics/stage0/subgroup_recalibration_metrics.csv","prior_result_unchanged":True}
    # Locked test confirmation, opened only after manifest.
    test_ids=pd.read_csv(DATA/"splits/test_ids.csv").SEQN;tm=pd.read_parquet(DATA/"analysis_dataset_primary.parquet",filters=[("SEQN","in",test_ids.tolist())])
    tr=[]
    for model in MODELS:
        td=tm.merge(pd.read_csv(PRED/f"test_predictions_{model}.csv"),on="SEQN",validate="one_to_one");f=meta.merge(oof[model],on="SEQN");global_cal=fit(f[f.part=="fit"].predicted_probability,f[f.part=="fit"].y);cand=chosen[model]
        for label in ["global_platt",cand] if cand!="global_platt" else ["global_platt"]:
            p=td.predicted_probability.to_numpy().copy()
            if label=="global_platt":
                p=apply(global_cal,p)
            if label=="subgroup_platt_bmi_age":
                for i,(b,a) in enumerate(zip(td.bmi_group_final,td.age_group_final)):
                    cm=cal_params[model]["cells"].get(("bmi_group_final",b),cal_params[model]["cells"].get(("age_group_final",a),global_cal))
                    p[i]=apply(cm,[p[i]])[0]
            y=td["outcome_primary_8.2kPa"].to_numpy();z=metrics(y,p,td.predicted_probability.to_numpy()>=FROZEN[model]);z.update(model=model,candidate=label,phase="LOCKED_TEST_CONFIRMATION",scope="OVERALL",sensitivity_ci_low=wilson(z["tp"],z["positive_n"])[0],sensitivity_ci_high=wilson(z["tp"],z["positive_n"])[1])
            tr.append(z)
            for scope,mask in [("BMI_Normal",td.bmi_group_final=="Normal"),("BMI_Obese",td.bmi_group_final=="Obese")]+[(f"AGE_{a}",td.age_group_final==a) for a in ["18-39","40-59","60+"]]:
                yy=y[mask];pp=p[mask];zz=metrics(yy,pp,td.predicted_probability.to_numpy()[mask]>=FROZEN[model]);zz.update(model=model,candidate=label,phase="LOCKED_TEST_CONFIRMATION",scope=scope,sensitivity_ci_low=wilson(zz["tp"],zz["positive_n"])[0],sensitivity_ci_high=wilson(zz["tp"],zz["positive_n"])[1]);tr.append(zz)
    pd.DataFrame(tr).to_csv(OUT/"phase4_locked_test_confirmation.csv",index=False)
    (OUT/"phase4_lineage.json").write_text(json.dumps(lineage,indent=2))
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,5));x=np.arange(len(MODELS));b=[];s=[]
    for m in MODELS:
        b.append(comparison[(comparison.model==m)&(comparison.candidate=="global_platt")].ece.iloc[0]);s.append(comparison[(comparison.model==m)&(comparison.candidate=="subgroup_platt_bmi_age")].ece.iloc[0])
    ax.bar(x-.18,b,.36,label="Global Platt");ax.bar(x+.18,s,.36,label="Subgroup Platt");ax.set_xticks(x,MODELS,rotation=20);ax.set_ylabel("OOF evaluation ECE");ax.legend();fig.tight_layout();fig.savefig(FIG/"phase4_ece_comparison.png",dpi=160);plt.close(fig)
if __name__=="__main__":main()
