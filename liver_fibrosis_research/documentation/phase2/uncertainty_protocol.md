# Future Uncertainty Analysis Protocol (Phase 2T)

**Generated:** 2026-08-18 — method frozen; NOT run in Phase 2.

## Method Selected: Split Conformal Prediction

**Why:** Chosen over model ensembles or MC dropout per the original research plan's own recommendation
(`info.md` Phase 12: "I recommend making conformal prediction the primary uncertainty method because it
is easier to explain and evaluate"), and because it provides a distribution-free, finite-sample coverage
guarantee that does not depend on a specific model family — important given Phase 3 will evaluate multiple
model families (`model_development_protocol.md`) without designating one as final.

## Specification

- **Calibration/training split:** Within the training portion of the 70/30 split
  (`model_development_protocol.md`), reserve a further split (e.g. 80% proper-train / 20% conformal
  calibration, exact proportion to be fixed in Phase 3 alongside the random seed) — the conformal
  calibration set must be disjoint from both the model-fitting data and the final locked test set.
- **Conformity score:** `1 − P̂(y=fibrosis-positive | x)` for the true class (standard non-conformity
  score for binary classification), computed from each candidate model's predicted probability.
- **Target coverage:** 90% (nominal), matching the original research plan's example
  (`info.md` Phase 12).
- **Prediction-set construction:** Standard split-conformal quantile procedure on the calibration set's
  non-conformity scores, applied to test-set predictions to produce a prediction set (which may contain
  {positive}, {negative}, {positive, negative}, or in principle ∅ under some conformal variants —
  the exact variant, e.g. APS vs. standard, to be fixed in Phase 3 implementation).
- **Overall coverage evaluation:** Empirical proportion of test-set true labels contained in their
  prediction set, compared to the 90% nominal target.
- **Subgroup coverage evaluation:** Same empirical coverage computed separately within every primary
  fairness subgroup (`fairness_subgroup_protocol.md`) — this is one of the thesis's stated novel
  contributions (whether uncertainty coverage itself varies by demographic group) and must not be skipped
  or treated as secondary.
- **Efficiency/size metric:** Average prediction-set size (or, for a continuous risk-score conformal
  interval variant, average interval width) — reported alongside coverage, since a trivially wide/uninformative
  prediction set can achieve high coverage without being useful.

## Assumptions and Limitations (documented now, not discovered post-hoc)

- Split conformal's marginal coverage guarantee holds under the exchangeability assumption; it does NOT
  by itself guarantee subgroup-conditional coverage — subgroup coverage deviations are an expected and
  scientifically interesting possible finding (H4 in `primary_research_question.md`), not evidence the
  method failed.
- The calibration-set size directly limits achievable coverage precision for smaller subgroups; this
  compounds the sample-size caveats already documented in `phase2_statistical_feasibility.csv` for the
  same subgroups.
