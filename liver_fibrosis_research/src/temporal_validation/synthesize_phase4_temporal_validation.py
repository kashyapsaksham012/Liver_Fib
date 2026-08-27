"""Read-only Phase 4 synthesis of completed Phase 3 outputs."""
from pathlib import Path
import pandas as pd

R=Path(__file__).resolve().parents[2]; T=R/'results/temporal_validation'
OUTCSV=T/'PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.csv'; OUTMD=T/'PHASE4_TEMPORAL_VALIDATION_SYNTHESIS.md'
if OUTCSV.exists() or OUTMD.exists(): raise RuntimeError('Refusing to overwrite an existing Phase 4 synthesis')
comp=pd.read_csv(T/'temporal_original_vs_validation_comparison.csv')
d=pd.read_csv(T/'temporal_discrimination_results.csv').set_index('model')
od=pd.read_csv(R/'results/tables/phase3_overall_discrimination.csv').set_index('model_name')
f=pd.read_csv(T/'temporal_fairness_results.csv'); c=pd.read_csv(T/'temporal_conformal_results.csv'); m=pd.read_csv(T/'temporal_m4b_results.csv')
models=['logistic','random_forest','xgboost','lightgbm','mlp']
domain={'AUROC':'Discrimination','PR-AUC':'Discrimination','sensitivity':'Discrimination','specificity':'Discrimination','PPV':'Discrimination','NPV':'Discrimination','calibration intercept':'Calibration','calibration slope':'Calibration','ECE':'Calibration','Brier':'Calibration','BMI sensitivity gap':'Fairness','Age sensitivity gap':'Fairness','overall conformal coverage':'Conformal','BMI coverage':'Conformal','Age 60+ coverage':'Conformal','BMI x Age baseline coverage':'Conformal','M4b intersectional coverage':'M4b','M4b mean set size':'M4b','prevalence':'Cohort'}
# add the two requested threshold metrics absent from the Phase 3 master comparison
add=[]
for x in models:
 for metric in ['PPV','NPV']:
  key=metric.lower(); a=float(od.loc[x,key]); b=float(d.loc[x,key]); add.append({'model':x,'metric':metric,'locked_test_2017_2020':a,'temporal_validation_2021_2023':b,'difference':b-a})
comp=pd.concat([comp,pd.DataFrame(add)],ignore_index=True); comp['domain']=comp.metric.map(domain)
def direction(r):
 if abs(r.difference)<1e-12:return 'STABLE'
 if r.metric in ['Brier','ECE','M4b mean set size']: return 'IMPROVED' if r.difference<0 else 'WORSENED'
 if r.metric in ['BMI sensitivity gap','Age sensitivity gap']: return 'WORSENED' if abs(r.temporal_validation_2021_2023)>abs(r.locked_test_2017_2020) else 'IMPROVED'
 return 'IMPROVED' if r.difference>0 else 'WORSENED'
comp['point_estimate_direction']=comp.apply(direction,axis=1)
classes=pd.DataFrame([{'model':'ALL','metric':'domain classification','locked_test_2017_2020':None,'temporal_validation_2021_2023':v,'difference':None,'domain':k,'point_estimate_direction':v} for k,v in {'Discrimination':'MIXED','Calibration':'MIXED','Fairness':'WORSENED','Conformal reliability':'MIXED','M4b performance':'WORSENED','Overall temporal study':'PARTIAL TEMPORAL REPLICATION'}.items()])
pd.concat([comp,classes],ignore_index=True).to_csv(OUTCSV,index=False)
def table(df,cols): return df[cols].to_markdown(index=False,floatfmt='.4f')
bmi=f[(f.dimension=='bmi')&(f.category=='Obese')][['model','n','n_positive','sensitivity','absolute_sensitivity_gap_pp','bh_fdr_adjusted_p','significant_after_fdr_0_05']]
age=f[(f.dimension=='age')&(f.category=='60+')][['model','n','n_positive','sensitivity','absolute_sensitivity_gap_pp','bh_fdr_adjusted_p','significant_after_fdr_0_05']]
co=c[c.scope.isin(['overall','bmi_obese','age_60plus','bmi_obese_x_age_60plus'])][['model','scope','coverage','coverage_ci_lower','coverage_ci_upper','mean_set_size','singleton_rate','doubleton_rate']]
mm=m[m.scope.isin(['overall','bmi_obese','age_60plus','bmi_obese_x_age_60plus'])][['model','scope','coverage','coverage_ci_lower','coverage_ci_upper','mean_set_size','singleton_rate','doubleton_rate','intersection_target_ge_90_maintained']]
perf=comp[comp.domain.isin(['Discrimination','Calibration'])][['model','metric','locked_test_2017_2020','temporal_validation_2021_2023','difference','point_estimate_direction']]
md=f'''# Phase 4 temporal-validation synthesis

## Design and verification

This synthesis reads completed Phase 3 artifacts only. The frozen five-model design, frozen thresholds, frozen Phase 6 conformal parameters, and frozen N0=0 M4b configuration were retained. The temporal cohort had **4,910** participants, **563** outcomes and **4,347** non-outcomes (prevalence **11.4664%**). Phase 3 input hashes and its before/after checks confirm exact SEQN matching and no modification of frozen inputs.

## Model performance

{table(perf,['model','metric','locked_test_2017_2020','temporal_validation_2021_2023','difference','point_estimate_direction'])}

AUROC declined for every model (about 0.041–0.064), while PR-AUC increased for every model. Threshold sensitivity/specificity changes were model-dependent. Thus discrimination is **MIXED**, not evidence that any model is generally better. Raw Brier score rose for every model, whereas ECE decreased; calibration intercepts remained negative and slopes were below 1. Calibration is **MIXED** and raw probability calibration still requires caution.

## Fairness

### BMI: obese versus normal reference

{table(bmi,list(bmi.columns))}

### Age: 60+ versus 40–59 reference

{table(age,list(age.columns))}

The original BMI sensitivity disparity remained and was substantially larger temporally: obese-versus-normal gaps were 62.8–71.9 percentage points, FDR-significant for all five models. The age 60+ disparity changed direction: 60+ sensitivity was modestly higher than 40–59 (3.3–10.0 points), statistically significant only for logistic regression. Lower sensitivity among ages 18–39 was significant for logistic regression, random forest, XGBoost, and MLP. Sex findings were mixed (female sensitivity lower and FDR-significant for logistic regression and XGBoost); race/ethnicity contrasts were not FDR-significant. BMI × Age remains problematic descriptively: obese 60+ sensitivity was very high but paired with low specificity, while normal-BMI cells had markedly low sensitivity; these exploratory cells were not given new post-hoc FDR claims.

Fairness is **WORSENED** overall because the pre-specified BMI gap persisted and enlarged. Sex/race stability is **MIXED**.

## Conformal transportability

{table(co,list(co.columns))}

Marginal coverage stayed near 90% (87.9%–90.2%), but BMI-obese coverage was 77.0%–81.3%, age-60+ coverage 84.9%–87.8%, and the BMI-obese × age-60+ intersection was 69.7%–76.5%. Hence the original pattern—acceptable-looking global coverage masking subgroup undercoverage—persists. Intersectional baseline coverage was somewhat higher for several models than in the locked test but remains far below 90%. Conformal reliability is **MIXED**, not stable subgroup transportability.

## Frozen M4b (N0 = 0)

{table(mm,list(mm.columns))}

The ≥90% temporal intersectional target held **only for random forest** (90.1%). It did not hold for logistic regression (88.6%), XGBoost (87.7%), LightGBM (87.3%), or MLP (88.6%). The same models therefore did not succeed as in the original N0=0 report: original success was four of five (all except LightGBM), versus one of five temporally. LightGBM remained below target. Overall set sizes were lower temporally (about 1.06–1.09), but this efficiency gain came with loss of intersectional target attainment, so the M4b trade-off did not remain similar. M4b performance is **WORSENED**.

## Main scientific story and interpretation

- Reasonable rank discrimination remains present, but AUROC decreased in all five models; temporal discrimination is mixed.
- The evidence continues to show that raw probabilities are not well calibrated; temporal Brier deterioration prevents any claim of calibration improvement despite lower ECE.
- BMI sensitivity disparity is reproduced and stronger. Age effects are not reproduced in the same direction: 60+ disparity is smaller/reversed, while lower sensitivity in 18–39 is evident in most models.
- Global conformal coverage continues to conceal substantial BMI, age, and intersectional undercoverage.
- The frozen N0=0 M4b configuration no longer delivers its intersectional target for most models; no tuning or replacement was performed.

## Paper-level conclusion and limitations

The overall classification is **PARTIAL TEMPORAL REPLICATION**. The temporal data reproduce useful discrimination, persistent calibration concerns, severe BMI-related disparity, and the central limitation of marginal conformal coverage. They do not reproduce reliable N0=0 M4b intersectional protection for most models, and age-related patterns changed. This is a later-cohort evaluation using frozen models and does not establish clinical readiness, causal explanations, broad external generalization, or a basis for model updating. Differences in cohort composition and outcome prevalence are observed facts here, not explanations for performance change.

No Phase 3 result was overwritten or recalculated; no primary research artifact was changed.
'''
OUTMD.write_text(md)
print(OUTCSV); print(OUTMD)
