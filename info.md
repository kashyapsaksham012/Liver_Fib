Now that you have downloaded the required NHANES files, you are at the point where the research should be frozen into a clear thesis plan. Based on the literature review, the two PDFs, and the discussion we had about novelty, I recommend not changing the topic again. The most important thing now is to define exactly what your contribution is and then execute it systematically.

Your research is not about creating the most accurate liver fibrosis model. That area is already crowded. Your research is about whether liver fibrosis ML models are reliable and equitable across different patient groups.

Here is the complete sequence you should follow.

Final research title

I recommend using this title:

Fairness, Calibration, and Uncertainty in Machine Learning-Based Liver Fibrosis Risk Prediction Across Demographic Groups

This title is strong because every word has a purpose.

Phrase

	

Meaning




Fairness

	

Does the model work equally well for different patient groups?




Calibration

	

Do predicted probabilities match actual observed risk?




Uncertainty

	

Does the model communicate how confident it is?




Machine Learning-Based

	

You will use standard ML models.




Liver Fibrosis Risk Prediction

	

Your clinical problem.




Across Demographic Groups

	

Sex, age, race/ethnicity, BMI, depending on available data.

An alternative title, if you want something slightly more attractive for publication, is:

Trustworthy AI for Liver Fibrosis: Evaluating Fairness, Calibration, and Predictive Uncertainty Using Public Health Data

The central idea of your thesis

The thesis can be summarized in one sentence:

Existing machine-learning studies on liver fibrosis mainly try to maximize accuracy, but they rarely investigate whether the models are equally reliable, well-calibrated, and trustworthy across different demographic groups.

That is the central motivation.

What is the actual research gap?

This is the most important section of your thesis.

What researchers have already done

Many studies have already:

used blood tests,

trained Logistic Regression,

Random Forest,

XGBoost,

LightGBM,

neural networks,

compared AUC,

compared accuracy,

compared sensitivity and specificity.

Therefore, these are not your novelty.

What has also already been done

A previous study found that liver-disease ML models trained on ILPD showed sex-related bias, with substantially more missed cases among women than men.

Another recent liver-disease study used conformal prediction to quantify uncertainty.

Therefore, you must not claim:

"Nobody studied fairness."

"Nobody studied sex bias."

"Nobody studied uncertainty."

Those claims would be incorrect.

The remaining gap

The gap is the integrated evaluation of liver fibrosis prediction models.

Your thesis asks:

When a machine-learning model predicts liver fibrosis risk, is it simultaneously accurate, calibrated, fair across demographic groups, and honest about its uncertainty?

The literature review suggests that these dimensions have generally been studied separately rather than together in a fibrosis-specific public-data study.

That is the contribution you should test—not assume.

The conceptual framework of your thesis

Your entire thesis revolves around four pillars.

Trustworthy AI for liver fibrosis

1. Discrimination

Can the model distinguish patients with fibrosis from those without it?

Metrics: ROC-AUC, PR-AUC, sensitivity, specificity.

2. Calibration

If the model says 70% risk, is the observed risk close to 70%?

Metrics: Brier score, calibration slope, calibration intercept, calibration curves.

3. Fairness

Does the model perform similarly across sex, age, race/ethnicity, and BMI groups?

Metrics: subgroup AUC, sensitivity, specificity, false-negative rate, false-positive rate, group calibration.

4. Uncertainty

Does the model tell us when it is uncertain?

Methods: conformal prediction, ensembles, MC dropout.

These four pillars—not a new classifier—are the core contribution of the thesis.

This framework is the heart of your research.

The exact research questions
Primary Research Question 1

How accurately can standard machine-learning models predict significant liver fibrosis using routine demographic and laboratory variables?

This establishes the baseline.

Primary Research Question 2

Are the predicted fibrosis risks well calibrated overall and within demographic subgroups?

This asks whether the probabilities can be trusted.

Primary Research Question 3

Do machine-learning models exhibit differences in predictive performance or error rates across demographic groups such as sex, age, race/ethnicity, and BMI?

This is your fairness question.

Primary Research Question 4

Can predictive uncertainty be quantified reliably, and does uncertainty coverage remain consistent across demographic groups?

This is your uncertainty question.

Secondary Research Question

If disparities are detected, can post-hoc calibration or fairness mitigation methods reduce them without causing unacceptable losses in overall predictive performance?

This makes your research stronger because you move beyond merely identifying problems.

Hypotheses

You should define hypotheses before running the experiments.

H1 — Accuracy

Standard ML models will achieve moderate discrimination for significant fibrosis prediction.

H2 — Calibration

At least some models will show imperfect calibration even if their AUC is acceptable.

H3 — Fairness

One or more demographic subgroups will show differences in false-negative rates, sensitivity, or calibration.

H4 — Uncertainty

Conformal prediction will achieve coverage close to the nominal target overall, but subgroup-specific coverage may differ.

H5 — Mitigation

Calibration or fairness interventions will reduce some disparities but may introduce trade-offs with overall discrimination or other performance metrics.

These hypotheses make the thesis scientifically structured.

The dataset you have downloaded

Your primary dataset is NHANES 2017–March 2020 pre-pandemic.

You downloaded several files because NHANES stores different kinds of information separately.

P_LUX

This is your most important file.

It contains:

FibroScan liver stiffness,

CAP,

quality information,

participant ID (SEQN).

The liver stiffness measurement is used to define the fibrosis-related outcome.

P_DEMO

This contains:

age,

sex,

race/ethnicity,

survey weights,

participant ID.

These variables are essential for the fairness analysis.

P_BMX

This contains:

height,

weight,

BMI,

body measurements.

BMI can be used both as a predictor and as a subgroup variable.

Laboratory files

These provide predictors such as:

AST,

ALT,

bilirubin,

albumin,

platelets,

glucose,

lipids,

other routine laboratory variables.

Phase 1 — Data assembly

This is your first real research phase.

Step 1.1

Load every XPT file into Python.

Use:

pandas,

pd.read_sas().

Step 1.2

Inspect every dataset.

For each file, record:

number of rows,

number of columns,

column names,

missing values,

variable types.

Create a data dictionary.

Step 1.3

Merge the datasets.

The common key is:

SEQN

Merge:

P_LUX

P_DEMO

P_BMX

laboratory files

This creates one row per participant.

Deliverable

A merged dataset with all candidate variables.

Phase 2 — Dataset feasibility audit

Do not train any ML model yet.

This phase is essential.

Check:

How many participants have valid FibroScan?

How many have all required laboratory values?

What percentage of values are missing?

How many males/females?

How many people in each race/ethnicity category?

How many BMI groups?

How many fibrosis-positive participants under each candidate threshold?

Create tables and plots.

Deliverables

Table 1: cohort characteristics

Missing-data table

Fibrosis prevalence table

Flow diagram of included/excluded participants

Phase 3 — Define the outcome

Your primary outcome is:

Significant liver fibrosis

Using the liver stiffness measurement from P_LUX.

You should predefine the threshold before modeling.

A reasonable primary analysis may use a clinically justified threshold, while sensitivity analyses should test nearby plausible cutoffs or alternative outcome formulations.

The important scientific principle is:

Do not change the threshold after seeing which one gives the best ML performance.

That would introduce bias.

Deliverable

A written outcome-definition protocol.

Phase 4 — Select predictors

Use only variables available before the outcome is known.

Potential predictors include:

Demographics

age

sex

BMI

Laboratory variables

AST

ALT

bilirubin

albumin

platelets

alkaline phosphatase

glucose

lipids

You must carefully check for target leakage.

For example, if your outcome is derived from a measurement that is directly or indirectly reused as a predictor, that would invalidate the experiment.

Deliverable

Final predictor list.

Phase 5 — Data preprocessing

This phase includes:

Missing values

Choose a predefined strategy such as:

median imputation,

or multiple imputation if justified.

Categorical variables

Encode them appropriately.

Scaling

Standardize variables for models like:

Logistic Regression

Neural Network

Tree models generally do not require scaling.

Class imbalance

First inspect the prevalence.

Do not automatically apply SMOTE.

For a clinical prediction study, it is often preferable to:

use class weights,

or evaluate the natural prevalence,

rather than synthetically changing the population before testing.

If you test SMOTE, treat it as a sensitivity experiment, not necessarily the primary analysis.

Phase 6 — Train baseline models

Use standard models.

The models themselves are not your novelty.

Train:

Model 1

Logistic Regression

Model 2

Random Forest

Model 3

XGBoost

Model 4

LightGBM

Model 5

Simple MLP neural network

Use the same predictor set for all models.

This ensures a fair comparison.

Phase 7 — Validation strategy

Split the data before preprocessing.

Recommended:

70% training

30% test

Use stratification on the outcome.

Within the training set:

perform 5-fold cross-validation,

tune hyperparameters,

freeze the final model.

The test set should remain untouched until the final evaluation.

This is critical to avoid optimistic bias.

Phase 8 — Evaluate discrimination

This answers:

"How well does the model separate patients with fibrosis from those without?"

Calculate:

ROC-AUC

Overall ranking ability.

PR-AUC

Especially useful if fibrosis prevalence is low.

Sensitivity

How many fibrosis-positive patients are detected?

Specificity

How many fibrosis-negative patients are correctly identified?

Precision

Of those predicted positive, how many are truly positive?

F1-score

Balances precision and recall.

Create:

ROC curves,

PR curves,

confusion matrices.

Phase 9 — Evaluate calibration

This is one of your core contributions.

Imagine the model predicts:

20%

40%

60%

80%

risk.

You ask whether the observed fibrosis rates are approximately:

20%

40%

60%

80%.

Calculate:

Brier Score

Overall probability accuracy.

Calibration intercept

Checks whether predictions are systematically too high or too low.

Calibration slope

Checks whether probabilities are too extreme or too conservative.

ECE

Expected Calibration Error.

Create calibration plots.

This section should receive significant attention in your thesis because many ML papers underreport calibration.

Phase 10 — Fairness audit

This is your most important phase.

Analyze performance separately for:

Sex

male

female

Age

For example:

younger adults

middle-aged adults

older adults

Define these groups before analysis.

Race/ethnicity

Use NHANES categories, but combine categories only if sample sizes are too small and document the decision.

BMI

For example:

normal

overweight

obese

Again, define these before analysis.

For each subgroup, calculate:

Metric

	

Why




AUC

	

Overall discrimination




Sensitivity

	

Ability to detect fibrosis




Specificity

	

Ability to exclude fibrosis




FNR

	

Missed disease




FPR

	

False alarms




Calibration slope

	

Probability reliability




Calibration intercept

	

Systematic over/underprediction

Then compare the groups.

Example:

Metric

	

Male

	

Female

	

Difference




AUC

	

0.84

	

0.82

	

-0.02




Sensitivity

	

0.88

	

0.76

	

-0.12




FNR

	

0.12

	

0.24

	

+0.12

This tells a much richer story than overall AUC.

Phase 11 — Statistical testing

Do not just say:

"Female sensitivity was lower."

Test whether the difference is likely to be due to chance.

Use:

Bootstrap confidence intervals

For differences in:

AUC

sensitivity

specificity

FNR

Permutation tests

For subgroup disparities.

Multiple-comparison correction

Because you will test many groups and many metrics.

Use:

FDR, or

Bonferroni

and report which correction was used.

Phase 12 — Uncertainty quantification

This is your third major contribution.

Primary method

Use split conformal prediction.

For example:

target coverage = 90%

Then ask:

Did it actually cover about 90% of true outcomes?

What was the average size of the prediction sets?

Did coverage differ between males and females?

Did coverage differ between age groups?

This last question is especially interesting.

You can also use:

model ensembles,

MC dropout for the neural network,

but I recommend making conformal prediction the primary uncertainty method because it is easier to explain and evaluate.

Phase 13 — Mitigation

Only do this if you detect meaningful disparities.

Possible methods:

Group-wise calibration

Calibrate predicted probabilities separately by group.

Threshold adjustment

Choose thresholds to reduce disparities in sensitivity or FNR.

Reweighting

Give underrepresented groups more influence during training.

Then compare:

Before mitigation

versus

After mitigation

on:

AUC

sensitivity

FNR disparity

calibration

uncertainty coverage

This is where you discuss trade-offs.

For example:

FNR disparity decreased from 15 percentage points to 5 percentage points, but overall AUC decreased by 0.01.

That is a scientifically meaningful result.

Phase 14 — Generalization

If your NHANES data support it, perform a temporal or subgroup validation.

For example:

train on one portion/cycle,

test on another.

Or perform subgroup holdout experiments.

Ask:

Does performance drop?

Which groups are most affected?

Does calibration remain stable?

This strengthens the thesis.

Phase 15 — Reproducibility

Your project should be reproducible.

Keep:

project/
├── data_raw/
├── data_processed/
├── notebooks/
├── src/
│   ├── data.py
│   ├── models.py
│   ├── fairness.py
│   ├── calibration.py
│   └── uncertainty.py
├── results/
├── figures/
├── tables/
├── requirements.txt
└── README.md

Record:

Python version,

package versions,

random seeds,

exact NHANES files,

preprocessing decisions.

What your thesis chapters should be
Chapter 1 — Introduction

Cover:

liver fibrosis,

why early detection matters,

AI in liver disease,

why accuracy alone is insufficient,

fairness,

calibration,

uncertainty,

research gap,

objectives.

Chapter 2 — Literature Review

Organize by themes:

traditional fibrosis ML,

cirrhosis/HCC prediction,

longitudinal models,

fairness studies,

calibration,

uncertainty,

research gap.

Chapter 3 — Methodology

Include:

datasets,

inclusion/exclusion,

outcome definition,

predictors,

preprocessing,

models,

validation,

metrics,

fairness analysis,

uncertainty,

statistics.

Chapter 4 — Results

Present in this order:

cohort characteristics,

overall model performance,

calibration,

subgroup fairness,

uncertainty,

mitigation,

generalization.

Chapter 5 — Discussion

Discuss:

what worked,

where disparities appeared,

whether calibration improved,

uncertainty results,

clinical implications,

comparison with previous studies,

limitations.

Chapter 6 — Conclusion

Summarize:

the main findings,

contribution,

future work.

Your timeline

Phase

	

Work




Month 1

	

Data download and merging




Month 2

	

Feasibility audit and outcome definition




Month 3

	

Preprocessing and baseline models




Month 4

	

Model tuning and discrimination




Month 5

	

Calibration analysis




Month 6

	

Fairness audit




Month 7

	

Uncertainty quantification




Month 8

	

Mitigation




Month 9

	

Generalization and robustness




Month 10

	

Thesis writing

What you should focus on most

Do not spend 80% of your thesis comparing algorithms.

Your thesis should approximately emphasize:

Section

	

Importance




Dataset and clinical outcome

	

20%




Baseline ML

	

15%




Calibration

	

20%




Fairness

	

30%




Uncertainty

	

10%




Mitigation/generalization

	

5%

The fairness and calibration sections should be the strongest parts because they represent the central contribution.

Your exact novelty claim

Do not write:

"This is the first study of fairness in liver AI."

That would be incorrect.

Instead, after your final targeted literature verification, your thesis should use wording along these lines:

This study evaluates liver fibrosis prediction models from a trustworthy-AI perspective by jointly assessing predictive discrimination, calibration, demographic subgroup performance, and predictive uncertainty using public data. While previous work has separately reported sex-related bias in liver-disease machine learning models and uncertainty quantification in related liver-risk prediction tasks, the integrated evaluation of these reliability dimensions in fibrosis-specific risk prediction remains insufficiently studied.

That is a much more defensible research position.

The complete sequence in one line

Literature gap → Download NHANES → Merge datasets → Feasibility audit → Freeze outcome → Select predictors → Preprocess → Train baseline models → Evaluate discrimination → Evaluate calibration → Audit fairness across demographic groups → Quantify uncertainty → Mitigate disparities if found → Test generalization → Write thesis.

That is the sequence you should follow from this point onward. If you follow it without skipping phases—especially the feasibility audit and outcome-definition step before modeling—you will have a research project that is much stronger than a standard "compare XGBoost vs Random Forest" liver-disease thesis.
