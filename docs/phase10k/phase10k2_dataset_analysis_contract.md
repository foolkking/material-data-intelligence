# Phase 10K-2 Dataset Analysis Contract

## Identity and authority

The product binds `datasetId`, dataset version, Profile 2.0 ID and semantic
hash, a content hash derived from sorted profiled object IDs/hashes, the primary
table object ID, and every resource binding. Material Data Profile 2.0 is the
only semantic-role authority. The adapter records `roleInferenceRepeated=false`.

## Composition

Element rows distinguish `materialsContainingElement`, total stoichiometric
amount, and fractional amount. Chemical systems use canonical sorted element
identity from the existing composition parser. Formula coverage denominators
are total rows, non-null formulas, valid formulas, and invalid formulas. Equal
reduced formula is an exact formula duplicate only.

## Structures

Structure statistics consume canonical pymatgen Structure resources. Site
count, volume in A^3, density in g/cm^3, lattice lengths/angles, space group,
and crystal system retain their stated source/derived semantics. Symmetry uses
the explicit `symprec` parameter and a fixed 5-degree angle tolerance. Failure
is a warning. Equal normalized object hash is the only exact structure
duplicate rule.

## Properties and quality

Only Profile 2.0 `material_property` numeric columns are analyzed. Units are
shown only when declared. Missing values and non-finite values have separate
counts. Statistics use finite values only: min, quartiles, median, max, mean,
sample standard deviation, and bounded NumPy histogram bins. The optional
1.5-IQR list is labeled `statistical_candidate_only`.

Quality reports Profile warnings, semantic-column missing/non-finite counts,
invalid formulas, duplicate explicit identity values, duplicate reduced
formulas, and the number of materialized sample links. No quality score,
near-duplicate claim, anomaly model, or chemical validity verdict exists.

## Determinism and truncation

Object IDs, elements, systems, properties, warnings, duplicate groups, and
sample rows have stable ordering. Top-category and table bounds are explicit in
the artifact. Truncation never changes a denominator. Inputs are immutable;
artifacts, summary, and recipe contain provenance but no executable content.
