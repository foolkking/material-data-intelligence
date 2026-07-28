# Phase 10K-3 Uncertainty Evaluation Contract

`phase10k3.materials_ml_uncertainty.v1` requires one complete Profile 2.0
regression series with exactly one explicit uncertainty binding. It does not
pair an unscoped or ambiguous column by proximity or row order.

Finite non-negative uncertainty, target, and prediction values form the aligned
diagnostic set. The product records Pearson and tie-aware Spearman association
against absolute error, equal-count reliability bins, and a deterministic
retained-error curve ordered from lowest uncertainty upward. High-uncertainty
rows preserve stable sample/formula identity.

When Profile 2.0 does not provide an uncertainty-kind authority, the artifact
uses `source_defined_uncertainty`; it does not relabel the values as standard
deviation, variance, interval, or calibrated probability. Reliability bins are
descriptive diagnostics and are explicitly not proof of calibration.
