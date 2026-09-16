# Literature Evidence and Citation

## Candidate versus evidence

Provider search returns `LiteratureSearchCandidate` records. A candidate is
discovery metadata only. It becomes usable evidence only through an explicit,
Project-authorized selection that creates `LiteratureEvidence`.

The selection records:

```text
Project / optional ResearchTurn
exact LiteratureWork
exact LiteratureSnapshot
evidence scope
support type
purpose
exact passage and anchor where applicable
numeric claims
claim refs
source-content hash
selector and timestamp
```

## Claim support

Support types are explicit:

```text
MENTIONED
SUPPORTING
CONTRADICTING
BACKGROUND
MIXED
DISCUSSES_RETRACTION
```

A citation attached to prose is not sufficient. Research and Report
projections retain machine-readable evidence and claim refs. Numeric literature
claims retain quantity, value, unit, system, method, and conditions. Their
value and unit must occur in the selected passage.

For an internal-vs-literature comparison, deterministic compatibility checks
quantity and unit semantics and disclose missing or differing conditions. The
current unit bridge explicitly supports energy, length, time, temperature, and
diffusion units including `Å²/ps`, `cm²/s`, and `m²/s`.

## Publication status

Retracted or withdrawn works cannot be ordinary supporting evidence. They may
only be retained when the research subject is the retraction/history itself.
Corrections and preprint/publication relations remain linked and version
specific. Paper count and citation count are not truth weighting.

## Deterministic bibliography

Citation text is rendered from the immutable snapshot:

```text
authors · year · title · venue · DOI/arXiv/provider identity
```

The model does not generate bibliographic identity. Reports persist the exact
snapshot and evidence identity used at generation time. A later status change
is displayed separately and never silently replaces historical report
evidence.

## Bounded synthesis

The literature synthesis provider receives only:

- the current scientific question;
- bounded selected passages and deterministic citation text;
- opaque `literature_n` refs;
- optional bounded `result_n` summaries;
- publication/scope/support metadata.

It returns structured claims, contradictions, and limitations. Deterministic
validation rejects invented evidence/Result refs and unsupported numeric
claims in summaries, claims, contradictions, or limitations. The provider may
repeat only exact numeric tokens from authorized evidence; it may not calculate
or state a new difference, ratio, percentage, conversion, range, or average.
At most one validation-guided repair is allowed. External text is marked
untrusted and cannot alter policy.

## Validation

Run:

```text
python scripts/scientific_knowledge_report.py --check
```

Default execution is deterministic and offline. Explicit live qualification:

```text
python scripts/scientific_knowledge_report.py \
  --check --live-providers --live-llm
```

The generated evidence is:

```text
docs/scientific-knowledge/generated/literature_integration_evaluation.json
```
