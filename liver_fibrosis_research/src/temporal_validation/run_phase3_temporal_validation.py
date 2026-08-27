"""Frozen-input Phase 3 temporal evaluation. No fitting, selection, or updating."""
from pathlib import Path
import hashlib, json, zlib
import numpy as np, pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix
from sklearn.linear_model import LogisticRegression
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]; T=ROOT/'results/temporal_validation'; P=T/'predictions'
M=['logistic','random_forest','xgboost','lightgbm','mlp']; TH={'logistic':.5173,'random_forest':.4499,'xgboost':.4108,'lightgbm':.4988,'mlp':.1065}
RACE={1.:'Mexican American',2.:'Other Hispanic',3.:'Non-Hispanic White',4.:'Non-Hispanic Black',6.:'Non-Hispanic Asian',7.:'Other Race / Multi-Racial'}; SEX={1.:'Male',2.:'Female'}
OUT=['temporal_discrimination_results.csv','temporal_calibration_results.csv','temporal_fairness_results.csv','temporal_conformal_results.csv','temporal_m4b_results.csv','temporal_original_vs_validation_comparison.csv','PHASE3_TEMPORAL_VALIDATION_REPORT.md','PHASE3_TEMPORAL_VALIDATION_MANIFEST.json']
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wil(k,n):
 z=stats.norm.ppf(.975); q=k/n; d=1+z*z/n; return ((q+z*z/(2*n)-z*np.sqrt(q*(1-q)/n+z*z/(4*n*n)))/d,(q+z*z/(2*n)+z*np.sqrt(q*(1-q)/n+z*z/(4*n*n)))/d)
def bins(x):
 return pd.qcut(x,10,duplicates='drop')
def cal(y,p):
 z=np.log(np.clip(p,1e-12,1-1e-12)/np.clip(1-p,1e-12,1-1e-12)); lr=LogisticRegression(C=1e10,solver='lbfgs',max_iter=5000).fit(z.reshape(-1,1),y)
 d=pd.DataFrame({'p':p,'y':y,'bin':bins(p)}).groupby('bin',observed=True).agg(n=('y','size'),mean_p=('p','mean'),obs=('y','mean')).reset_index(drop=True); d.insert(0,'bin_index',range(1,len(d)+1)); e=float((d.n/len(y)*(d.mean_p-d.obs).abs()).sum())
 return lr.intercept_[0],lr.coef_[0,0],brier_score_loss(y,p),e,d
def age(x): return '18-39' if x<=39 else ('40-59' if x<=59 else '60+')
def bmi(x): return 'Underweight' if x<=18.5 else ('Normal' if x<=24.9 else ('Overweight' if x<=29.9 else 'Obese'))
def tier(a,b): return 'insufficient evidence' if a<10 or b<10 else ('limited precision' if a<30 or b<30 else ('exploratory candidate' if a<100 or b<100 else 'primary-feasibility candidate'))
def bh(p):
 n=len(p); o=np.argsort(p); r=np.array(p)[o]*n/np.arange(1,n+1); r=np.minimum.accumulate(r[::-1])[::-1]; out=np.empty(n); out[o]=np.clip(r,0,1); return out
def boot_auc(y,p,fn,seed):
 rng=np.random.default_rng(seed); vals=[]
 for _ in range(2000):
  i=rng.integers(0,len(y),len(y));
  if len(np.unique(y[i]))==2: vals.append(fn(y[i],p[i]))
 return np.percentile(vals,[2.5,97.5])
def sens(y,pred): return np.mean(pred[y==1]) if np.any(y==1) else np.nan
def main():
 # frozen inputs watched before/after
 labels=T/'temporal_validation_labels_demographics.csv'; fair=T/'temporal_validation_fairness_demographics.csv'; cp={x:T/f'temporal_conformal_refit_predictions_{x}.csv' for x in M}
 sources=[labels,fair,*[P/f'temporal_predictions_{x}.csv' for x in M],*cp.values(),ROOT/'results/uncertainty/conformal_thresholds_by_model.csv',ROOT/'results/tables/m4b_lightgbm_failure_analysis.csv',ROOT/'results/tables/m4b_prespecified_n0_final_results.csv',ROOT/'results/tables/phase3_overall_discrimination.csv',ROOT/'results/calibration/test_set_calibration_final.csv',ROOT/'results/fairness/subgroup_discrimination_metrics.csv',ROOT/'results/uncertainty/marginal_coverage_test_set.csv',ROOT/'results/uncertainty/subgroup_coverage.csv',ROOT/'results/uncertainty/intersectional_coverage_ci.csv',ROOT/'results/tables/m4b_shrinkage_sensitivity.csv']
 before={str(x):h(x) for x in sources}
 lab=pd.read_csv(labels); dem=pd.read_csv(fair); base=lab.merge(dem,on='SEQN',validate='one_to_one');
 if len(base)!=4910 or base.SEQN.nunique()!=4910 or base.isna().any().any() or not ((base.outcome==(base.LUXSMED>=8.2).astype(int)).all()) or base.outcome.sum()!=563: raise RuntimeError('Temporal input integrity failed')
 base['sex']=base.RIAGENDR.map(SEX); base['race_ethnicity']=base.RIDRETH3.map(RACE); base['age']=base.RIDAGEYR.map(age); base['bmi']=base.BMXBMI.map(bmi); base['bmi_x_age']=base.bmi+' x '+base.age
 probs={};
 for x in M:
  q=pd.read_csv(P/f'temporal_predictions_{x}.csv');
  if len(q)!=4910 or q.SEQN.nunique()!=4910 or q.predicted_probability.isna().any() or set(q.SEQN)!=set(base.SEQN): raise RuntimeError(f'{x} primary prediction integrity failed')
  probs[x]=base.merge(q,on='SEQN',validate='one_to_one')
 # discrimination + raw calibration
 disc=[]; cr=[]; curves=[]
 for j,x in enumerate(M):
  d=probs[x]; y=d.outcome.to_numpy(); p=d.predicted_probability.to_numpy(); pr=(p>=TH[x]).astype(int); tn,fp,fn,tp=confusion_matrix(y,pr,labels=[0,1]).ravel(); au=roc_auc_score(y,p); ap=average_precision_score(y,p); aci=boot_auc(y,p,roc_auc_score,42+j); pci=boot_auc(y,p,average_precision_score,142+j)
  disc.append(dict(model=x,n=4910,threshold=TH[x],auroc=au,auroc_ci_lower=aci[0],auroc_ci_upper=aci[1],pr_auc=ap,pr_auc_ci_lower=pci[0],pr_auc_ci_upper=pci[1],sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),ppv=tp/(tp+fp),npv=tn/(tn+fn),tp=tp,tn=tn,fp=fp,fn=fn,ci_method='percentile bootstrap, n=2000, seed=42'))
  a,s,b,e,c=cal(y,p); cr.append(dict(record_type='metric',model=x,variant='raw_frozen_phase3_probability',n=4910,calibration_intercept=a,calibration_slope=s,brier_score=b,ece=e,n_bins_achieved=len(c),binning_degenerate=len(c)!=10)); c['record_type']='calibration_curve'; c['model']=x; c['variant']='raw_frozen_phase3_probability'; curves.append(c)
  plt.figure(figsize=(5,5)); plt.plot([0,1],[0,1],'--',color='gray'); plt.plot(c.mean_p,c.obs,'o-'); plt.xlabel('Mean predicted probability'); plt.ylabel('Observed event rate'); plt.title(f'Temporal calibration: {x}'); plt.xlim(0,1); plt.ylim(0,1); plt.tight_layout(); (T/'figures').mkdir(exist_ok=True); plt.savefig(T/'figures'/f'temporal_calibration_curve_{x}.png',dpi=150); plt.close()
 # fairness point metrics and formal inference only for original four dimensions
 fr=[]
 refs={'sex':'Male','race_ethnicity':'Non-Hispanic White','age':'40-59','bmi':'Normal'}
 for x in M:
  d=probs[x].copy(); d['pred']=(d.predicted_probability>=TH[x]).astype(int)
  for dim in ['sex','race_ethnicity','age','bmi','bmi_x_age']:
   cats=sorted(d[dim].dropna().unique()); ref=refs.get(dim); pending=[]
   for cat in cats:
    z=d[d[dim]==cat]; y=z.outcome.to_numpy(); pr=z.pred.to_numpy(); n=len(z); pos=int(y.sum()); neg=n-pos; se=sens(y,pr); sp=np.mean(pr[y==0]==0) if neg else np.nan; au=roc_auc_score(y,z.predicted_probability) if pos and neg else np.nan; lo,hi=wil(int(pr[y==1].sum()),pos) if pos else (np.nan,np.nan)
    row=dict(model=x,dimension=dim,category=cat,reference_group=ref,is_reference=(cat==ref),n=n,n_positive=pos,n_negative=neg,precision_tier=tier(pos,neg),sensitivity=se,sensitivity_ci_lower=lo,sensitivity_ci_upper=hi,specificity=sp,auroc=au,absolute_sensitivity_gap_pp=np.nan, gap_ci_lower_pp=np.nan,gap_ci_upper_pp=np.nan,raw_p_bootstrap=np.nan,bh_fdr_adjusted_p=np.nan,significant_after_fdr_0_05=np.nan,fdr_protocol='BH within model x dimension; BMI x Age exploratory/unadjusted')
    if ref and cat!=ref: pending.append((row,z))
    fr.append(row)
   if ref:
    rz=d[d[dim]==ref]; ry=rz.outcome.to_numpy(); rp=rz.pred.to_numpy(); pvals=[]; metas=[]
    for row,z in pending:
     zy=z.outcome.to_numpy(); zp=z.pred.to_numpy(); rng=np.random.default_rng(42+zlib.crc32(f'{x}|{dim}|{row["category"]}'.encode())%1000000); dif=[]
     for _ in range(2000):
      ii=rng.integers(0,len(ry),len(ry)); jj=rng.integers(0,len(zy),len(zy));
      if ry[ii].sum() and zy[jj].sum(): dif.append(sens(zy[jj],zp[jj])-sens(ry[ii],rp[ii]))
     dif=np.array(dif); gap=sens(zy,zp)-sens(ry,rp); pv=min(2*min(np.mean(dif<=0),np.mean(dif>=0)),1); pvals.append(pv); metas.append((row,gap,np.percentile(dif,[2.5,97.5]),pv))
    for (row,gap,ci,pv),adj in zip(metas,bh(pvals)):
     row.update(absolute_sensitivity_gap_pp=100*gap,gap_ci_lower_pp=100*ci[0],gap_ci_upper_pp=100*ci[1],raw_p_bootstrap=pv,bh_fdr_adjusted_p=adj,significant_after_fdr_0_05=adj<.05)
 # conformal baseline and M4b
 ct=pd.read_csv(ROOT/'results/uncertainty/conformal_thresholds_by_model.csv').set_index('model'); mq=pd.read_csv(ROOT/'results/tables/m4b_lightgbm_failure_analysis.csv').set_index('model'); mf=pd.read_csv(ROOT/'results/tables/m4b_prespecified_n0_final_results.csv').set_index('model'); con=[]; m4=[]
 for x in M:
  d=base.merge(pd.read_csv(cp[x]),on='SEQN',validate='one_to_one'); p=d.conformal_refit_probability.to_numpy(); y=d.outcome.to_numpy(); q=float(ct.loc[x,'threshold']); inc1=(1-p)<=q; inc0=p<=q; size=inc1.astype(int)+inc0.astype(int); cov=np.where(y==1,inc1,inc0); orig=float(pd.read_csv(ROOT/'results/uncertainty/marginal_coverage_test_set.csv').set_index('model').loc[x,'empirical_coverage'])
  for label,mask in [('overall',np.ones(len(d),bool)),('bmi_obese',(d.bmi=='Obese').to_numpy()),('age_60plus',(d.age=='60+').to_numpy()),('bmi_obese_x_age_60plus',((d.bmi=='Obese')&(d.age=='60+')).to_numpy())]:
   k=int(cov[mask].sum()); n=int(mask.sum()); lo,hi=wil(k,n); con.append(dict(model=x,scope=label,n=n,n_covered=k,coverage=k/n,coverage_ci_lower=lo,coverage_ci_upper=hi,mean_set_size=float(size[mask].mean()),singleton_rate=float((size[mask]==1).mean()),doubleton_rate=float((size[mask]==2).mean()),coverage_gap_vs_overall_pp=100*(k/n-cov.mean()),marginal_coverage_drift_vs_locked_test_pp=100*(cov.mean()-orig),frozen_threshold=q))
  qs=np.full(len(d),float(mq.loc[x,'q_global_cal'])); ob=(d.bmi=='Obese').to_numpy(); ag=(d.age=='60+').to_numpy(); jo=ob&ag; qs[ob]=float(mq.loc[x,'q_obese_cal']); qs[ag]=float(mq.loc[x,'q_age60_cal']); qs[jo]=float(mf.loc[x,'q_m4b_cal']); pp=d.platt_recalibrated_probability.to_numpy(); i1=(1-pp)<=qs; i0=pp<=qs; ss=i1.astype(int)+i0.astype(int); cv=np.where(y==1,i1,i0); origm=float(mf.loc[x,'marginal_coverage'])
  for label,mask in [('overall',np.ones(len(d),bool)),('bmi_obese',ob),('age_60plus',ag),('bmi_obese_x_age_60plus',jo)]:
   k=int(cv[mask].sum()); n=int(mask.sum()); lo,hi=wil(k,n); m4.append(dict(model=x,scope=label,n=n,n_covered=k,coverage=k/n,coverage_ci_lower=lo,coverage_ci_upper=hi,mean_set_size=float(ss[mask].mean()),singleton_rate=float((ss[mask]==1).mean()),doubleton_rate=float((ss[mask]==2).mean()),m4b_n0=0,marginal_coverage_drift_vs_locked_test_pp=100*(cv.mean()-origm),intersection_target_ge_90_maintained=(cv[jo].mean()>=.9)))
 # comparison long table
 D=pd.DataFrame(disc).set_index('model'); C=pd.DataFrame(cr).query("record_type=='metric'").set_index('model'); F=pd.DataFrame(fr); CO=pd.DataFrame(con); MM=pd.DataFrame(m4); od=pd.read_csv(ROOT/'results/tables/phase3_overall_discrimination.csv').set_index('model_name'); oc=pd.read_csv(ROOT/'results/calibration/test_set_calibration_final.csv').query("variant=='raw'").set_index('model'); of=pd.read_csv(ROOT/'results/fairness/subgroup_discrimination_metrics.csv'); om=pd.read_csv(ROOT/'results/uncertainty/marginal_coverage_test_set.csv').set_index('model'); os=pd.read_csv(ROOT/'results/uncertainty/subgroup_coverage.csv'); oi=pd.read_csv(ROOT/'results/uncertainty/intersectional_coverage_ci.csv'); ms=pd.read_csv(ROOT/'results/tables/m4b_shrinkage_sensitivity.csv').query('N0==0').set_index('model')
 comp=[]
 for x in M:
  metrics={'AUROC':(od.loc[x,'roc_auc'],D.loc[x,'auroc']),'PR-AUC':(od.loc[x,'pr_auc'],D.loc[x,'pr_auc']),'sensitivity':(od.loc[x,'sensitivity'],D.loc[x,'sensitivity']),'specificity':(od.loc[x,'specificity'],D.loc[x,'specificity']),'calibration intercept':(oc.loc[x,'calibration_intercept'],C.loc[x,'calibration_intercept']),'calibration slope':(oc.loc[x,'calibration_slope'],C.loc[x,'calibration_slope']),'ECE':(oc.loc[x,'ece'],C.loc[x,'ece']),'Brier':(oc.loc[x,'brier_score'],C.loc[x,'brier_score']),'BMI sensitivity gap':(100*(of[(of.model==x)&(of.dimension=='bmi')&(of.category=='Obese')].sensitivity.iloc[0]-of[(of.model==x)&(of.dimension=='bmi')&(of.category=='Normal')].sensitivity.iloc[0]),F[(F.model==x)&(F.dimension=='bmi')&(F.category=='Obese')].absolute_sensitivity_gap_pp.iloc[0]),'Age sensitivity gap':(100*(of[(of.model==x)&(of.dimension=='age')&(of.category=='60+')].sensitivity.iloc[0]-of[(of.model==x)&(of.dimension=='age')&(of.category=='40-59')].sensitivity.iloc[0]),F[(F.model==x)&(F.dimension=='age')&(F.category=='60+')].absolute_sensitivity_gap_pp.iloc[0]),'overall conformal coverage':(om.loc[x,'empirical_coverage'],CO[(CO.model==x)&(CO.scope=='overall')].coverage.iloc[0]),'BMI coverage':(os[(os.model==x)&(os.dimension=='bmi')&(os.category=='Obese')].empirical_coverage.iloc[0],CO[(CO.model==x)&(CO.scope=='bmi_obese')].coverage.iloc[0]),'Age 60+ coverage':(os[(os.model==x)&(os.dimension=='age')&(os.category=='60+')].empirical_coverage.iloc[0],CO[(CO.model==x)&(CO.scope=='age_60plus')].coverage.iloc[0]),'BMI x Age baseline coverage':(oi[(oi.model==x)&(oi.stage=='baseline')].coverage.iloc[0],CO[(CO.model==x)&(CO.scope=='bmi_obese_x_age_60plus')].coverage.iloc[0]),'M4b intersectional coverage':(mf.loc[x,'intersectional_coverage'],MM[(MM.model==x)&(MM.scope=='bmi_obese_x_age_60plus')].coverage.iloc[0]),'M4b mean set size':(ms.loc[x,'mean_set_size'],MM[(MM.model==x)&(MM.scope=='overall')].mean_set_size.iloc[0]),'prevalence':(200/2146,563/4910)}
  comp += [dict(model=x,metric=k,locked_test_2017_2020=a,temporal_validation_2021_2023=b,difference=b-a) for k,(a,b) in metrics.items()]
 # write outcomes; existing report/manifest replaced as explicitly requested final outputs
 pd.DataFrame(disc).to_csv(T/OUT[0],index=False); pd.concat([pd.DataFrame(cr),pd.concat(curves,ignore_index=True)],ignore_index=True).to_csv(T/OUT[1],index=False); pd.DataFrame(fr).to_csv(T/OUT[2],index=False); pd.DataFrame(con).to_csv(T/OUT[3],index=False); pd.DataFrame(m4).to_csv(T/OUT[4],index=False); pd.DataFrame(comp).to_csv(T/OUT[5],index=False)
 after={str(x):h(x) for x in sources}
 if before!=after: raise RuntimeError('Frozen input changed unexpectedly')
 report='# Phase 3 temporal validation report\n\n**Scope:** frozen-model temporal evaluation only; no model updating, threshold selection, recalibration, conformal fitting, quantile recomputation, or N0 selection occurred.\n\n## Cohort\n\nThe temporal cohort contains 4,910 participants, 563 outcomes (11.4664%) and 4,347 non-outcomes. All required input SEQNs matched exactly.\n\n## Interpretation\n\nResults are reported in the accompanying tables. They quantify performance change on this later NHANES cohort under the frozen protocol; they do not by themselves establish clinical readiness or broader external generalization. Any adverse discrimination, calibration, fairness, or coverage changes are retained without mitigation or model modification.\n\n## Reproducibility\n\nDiscrimination CIs use 2,000 percentile bootstrap resamples. Fairness sensitivity-gap CIs use the original 2,000 resamples and BH-FDR within each model × original subgroup dimension; BMI × Age cells remain exploratory, as in the original protocol. Coverage CIs are 95% Wilson intervals. Calibration uses raw frozen Phase 3 probabilities and frozen 10-quantile-bin ECE. Conformal uses Phase 6 refit probabilities and frozen thresholds. M4b applies the frozen N0=0 group/joint quantiles.\n'
 (T/OUT[6]).write_text(report)
 manifest={'status':'COMPLETE','integrity':{'n':4910,'positives':563,'negatives':4347,'prevalence':563/4910,'all_seqns_exact_match':True,'frozen_sources_unchanged_before_after':True},'method':{'thresholds':TH,'bootstrap_n':2000,'fdr':'BH within model x original dimension','conformal':'frozen Phase 6 refit probabilities and thresholds','m4b_N0':0},'input_hashes':before,'outputs':{x:h(T/x) for x in OUT[:-1]},'figures':{str(x.relative_to(T)):h(x) for x in (T/'figures').glob('temporal_calibration_curve_*.png')}}
 (T/OUT[7]).write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__': main()
