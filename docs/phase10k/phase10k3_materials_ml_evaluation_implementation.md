# Phase 10K-3 Materials ML Evaluation Implementation

Status: IMPLEMENTATION_CI_PASSED, pending completion-record CI and verified
queue closure.

The CI integration gate executes regression, uncertainty, and classification
through persisted jobs and S3-compatible artifact storage; local in-memory
runtime evidence remains separate from that service-backed authority.

## Product boundary

Three non-overlapping product capabilities consume only complete Material Data
Profile 2.0 semantic groups and explicitly bound canonical tables:

- `ml.regression_evaluation`
- `ml.uncertainty_evaluation`
- `ml.classification_evaluation`

Each runs through validated AnalysisPlan, QueueWorkerRuntime, Registry, and a
deterministic adapter. Outputs are bounded inert JSON, Markdown summary, and
recipe artifacts. Existing atomic V1 ML manifest identities are not execution
aliases for these products.

## Delivered behavior

Regression includes finite aligned-sample metrics, parity and residual data,
largest errors with stable material sample identity, overlapping element and
exact chemical-system groups, and common-valid-sample model comparison.
Uncertainty includes explicit series binding, association diagnostics,
equal-count reliability bins, lowest-uncertainty-first retained-error curves,
and linked high-uncertainty samples. Classification includes raw confusion
counts, accuracy, macro/per-class metrics, linked misclassifications, and
binary ROC/PR only when an explicit positive class and normalized matching
probability are available.

The Results workspace renders responsive SVG/table products with accessible
numeric fallbacks. The Dataset Explorer adds a truthful Model evaluation
readiness tab driven by Profile 2.0 availability facts.

## Security and limits

The hard data cap is 100,000 rows. Models, classes, chemistry groups, display
rows, plot points, curve points, bins, artifact bytes, and execution time are
independently bounded. Inputs are finite-checked; ambiguous/incomplete semantic
groups and invalid uncertainty/probability values fail with typed errors.
Artifacts cannot carry JavaScript, URLs, external assets, callbacks, or code.
No dependency, training, arbitrary Python, real LLM, or network authority was
added.

## Explicit limits

Residual is always `prediction - target`. R2 is undefined for zero target
variance. Chemistry-conditioned diagnostics are descriptive and overlapping,
not causal or significance claims. Uncertainty reliability is a supplied-data
diagnostic, not calibration authority. Multiclass ROC/PR and probability
calibration are deferred. Embedding/clustering belongs to Phase 10K-4;
capability-aware multi-tool planning belongs to Phase 10L.
