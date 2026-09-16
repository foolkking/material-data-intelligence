# Method Comparison and Inference Policy

## Method is scientific context

A numeric label alone does not make two Results comparable. Claim assessment
uses the method and condition information already attached to Results and
LiteratureEvidence, including source/version, quantity semantics, units,
normalization, material/system, composition, phase, temperature, pressure,
time/length scale, data population and method identity where available.

The allowed comparison statuses are:

- `DIRECTLY_COMPARABLE` — compatible quantity, units, conditions and method
  context are available;
- `COMPARABLE_WITH_QUALIFIERS` — a comparison is useful but a recorded
  difference (for example temperature) limits its interpretation;
- `COMPLEMENTARY` — the methods answer related but non-interchangeable
  questions;
- `METHOD_DEPENDENT_DIFFERENCE` — differing definitions/algorithms plausibly
  explain differing observations;
- `NOT_COMPARABLE` — a direct scientific comparison is not warranted;
- `INSUFFICIENT_METHOD_METADATA` — the available evidence cannot establish
  compatibility.

There is no global method-quality score. Experimental, MD, DFT, coordination,
RDF, XRD, ML, phonon, primary-study and review evidence are evaluated for the
specific claim’s directness, scope, conditions, limitations and lineage.

## Inference boundaries

### Association, mechanism and causation

Co-occurrence supports at most association unless a causal-design authority is
explicitly present. A transport result plus a coordination/RDF result may make
a structural mechanism **consistent with** the evidence or motivate a
hypothesis. It does not establish that coordination caused transport.

### Generalization

Claims are limited to the material, data split, conditions and methods actually
represented. A cluster is exploratory structure, not a material family; an
outlier is not invalid material evidence. ML subgroup error is an association
within the evaluated split, not proof that chemistry causes failure or that the
model generalizes outside coverage.

### Method-dependent domains

- Coordination values from CrystalNN, VoronoiNN and cutoff definitions are not
  averaged into a single “true” value without an authorized deterministic
  derivation and a scientific contract supporting it.
- XRD peak-position agreement can support a configured comparison. It does not
  by itself establish phase identity, phase purity, or agreement in all
  broadening/measurement details.
- A supplied electronic or phonon Result retains the external-implementation
  semantics boundary. A negative phonon frequency is an observed output; it
  does not universally establish physical instability without appropriate
  convergence, finite-size and condition evidence.

### Literature boundaries

A review can provide background or field synthesis but is not automatically an
independent replication of a primary study. Preprint and published versions are
related work, not two independent studies. `ABSTRACT_ONLY` evidence is limited
to what the retrieved abstract actually reports.

## Derived values

The LLM must not calculate differences, ratios, percentages, averages or unit
conversions in prose. A derived quantitative claim is permitted only after a
narrow deterministic derived-fact authority has recorded input evidence refs,
input values/units, operation/formula version, output unit/value and rounding
policy. Workstream I validates and rejects unauthorized derived numeric claims;
it does not create a shortcut that mutates upstream ScientificResults.

## Required scientific wording

Use wording consistent with assessed status: “shows” for direct observation,
“within the evaluated scope” for scoped support, “is consistent with” or “may”
for tentative mechanisms, and “cannot establish” for insufficient evidence.
The validator enforces epistemic relations and required qualifiers, not fixed
phrases.
