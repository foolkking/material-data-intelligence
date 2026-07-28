# Phase 10K-4 Composition Feature Contract

## Canonical input and identity

Formula identity comes exclusively from a complete Profile 2.0
`material_formula` binding. Each valid formula is parsed through the existing
application composition semantics backed by `pymatgen.core.Composition`.
Samples retain `objectId`, `rowIndex`, and the Profile stable `sampleRef`; the
combined `sampleKey` is `objectId:sampleRef`. Invalid formulas are excluded with
counts and bounded examples, never silently dropped.

## Feature representation

The canonical feature is a normalized atomic-fraction vector. For each sample,
each positive finite element amount is divided by the total amount. Missing
elements are zero. Fractional/non-integer occupancies are valid. The shared
element basis is ordered by atomic number and recorded in the artifact.

Projection coordinates are not canonical material identity.

## PCA

PCA is two-dimensional, center-only, unscaled, and uses full SVD. At least
three valid samples and centered rank two are required. Each component uses the
deterministic sign rule `largest_absolute_loading_is_positive`. Components,
mean, rank, explained-variance ratios, and cumulative variance are persisted.

## Clustering

Optional KMeans uses the normalized fraction matrix, never PCA coordinates.
The seed, initialization count, iteration cap, tolerance, inertia, and
iteration count are persisted. Labels are reindexed by lexicographic centroid
order. A cluster means only a descriptive composition cluster; it is not a
material family, phase, bond environment, structure class, or scientific truth.

## Comparison and coloring

Comparison requires two named resources or two values from one explicit group
column. One shared element basis and one combined PCA fit are used and labeled
`exploratory_combined_projection`; no training-safety claim is made. Property
colors come only from Profile `material_property` semantics with compatible
units. ML error/uncertainty colors require an explicit Phase 10K-3 artifact and
match `objectId + sampleRef`; they are not recomputed in the frontend.

Outlier candidates rank Euclidean distance to the combined feature centroid.
They are descriptive composition-space candidates, not invalid materials.
