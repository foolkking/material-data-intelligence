# Phase 10K-3 Regression Evaluation Contract

`phase10k3.materials_ml_regression.v1` binds one or more complete Profile 2.0
regression series from one canonical table. A task retains its profile group,
series, target, prediction, optional uncertainty, property unit, semantic hash,
and stable sample reference.

Only rows with finite target and prediction enter metrics. Coverage reports
total, evaluated, missing, and non-finite/invalid counts separately. Residual is
fixed as `prediction - target`; the artifact stores MAE, MSE, RMSE, mean signed
error, median absolute error, and R2. R2 is null when target variance is zero.

Parity/residual points, histogram bins, and linked high-error rows are
deterministic and bounded. Element groups may overlap; chemical-system groups
use Profile-bound formula parsing and exact sorted element systems. The default
small-group threshold is three samples; smaller groups remain visible with a
`smallGroup` flag and are never presented as statistically significant. Multi-model
comparison uses the intersection of valid samples for a shared target and
discloses `common_valid_samples`.
