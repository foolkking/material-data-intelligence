# Phase 10K-3 Classification Evaluation Contract

`phase10k3.materials_ml_classification.v1` binds one complete Profile 2.0
classification group containing explicit actual and predicted labels. Missing
label pairs are excluded with disclosed coverage. Source label spelling and
case are preserved. Probability-column and requested-positive labels may match
case-insensitively only when the source mapping is unique; ambiguity is rejected.
The product stores sorted
class identity, raw confusion counts, accuracy, macro precision/recall/F1,
per-class support/precision/recall/F1, and bounded linked misclassifications.

ROC and precision-recall curves are supported only for exactly two classes,
an explicit positive class, and its explicitly bound normalized probability
column. The adapter validates every probability in `[0,1]` and each available
row sum within tolerance. It reports typed unavailable states for missing
probabilities, absent/unknown positive class, invalid normalization, multiclass
input, or single-class truth. It never invents scores from hard labels.

Macro metrics are unweighted means over defined class metrics. Precision,
recall, or F1 with a zero denominator is typed null and omitted from that macro
denominator; `zeroDivisionPolicy=undefined_null`, class support, and raw
confusion counts remain visible. These diagnostics do not establish scientific
validity, causal quality, or deployment fitness.
