# Scientist Research Experience

Date: 2026-09-10  
Authority: canonical product behavior in `E:\1project\mdi-b0-5a1`

## Mental model

The default Research experience is organized as:

```text
Research question
→ relevant scientific sources
→ observable research progress
→ ScientificResults and evidence
→ findings and interpretation
→ limitations / unresolved questions
→ optional next research
```

Lifecycle, Tool, Adapter, Artifact, ContextSnapshot, and worker identities remain
available only through advanced provenance. They are not the primary product
language.

## Research timeline

The conversation pane owns scientist-facing progress. It exposes:

- the main research question and current subquestion;
- analyses selected and a bounded explanation of why;
- durable Results as they become available;
- evidence gaps and scientific stop reasons;
- failed, partial, cancelled, and recovered states;
- a compact Research Map derived from strategy/evidence projections.

Completed operational detail collapses. Hidden reasoning, prompts, queue
internals, and model scratchpads are never shown.

## Research Map

The map is a read-only projection over Workstream F evidence state. It may show:

- resolved questions;
- partially addressed or limited questions;
- unresolved evidence gaps;
- contradictory evidence;
- hypotheses with explicit non-authoritative status;
- Result references and material limitations.

It does not create scientific conclusions. `ScientificResult` remains the
scientific fact authority.

## Findings, evidence, hypotheses, and limitations

- **Finding** is scientist-facing language grounded in Result evidence.
- **Evidence** is the Result/table/figure/source lineage supporting a finding.
- **Interpretation** explains Result meaning within recorded limits.
- **Hypothesis** is tentative and visually separated from findings. It retains
  status and limitations and never receives success styling merely because it
  exists.
- **Limitation** is shown near the finding whenever it materially changes what
  may be concluded.

## Source and provenance disclosure

Default presentation uses scientific labels, source type, and version number.
Identity-shaped fixture/database names are replaced by neutral labels such as
`材料研究项目` and `当前项目材料数据`.

Technical identities remain available through closed disclosures:

- exact ScientificObjectVersion;
- Capability and Tool/Adapter versions;
- Artifact and Result identities;
- method parameters;
- qualification fingerprint;
- Context source references.

## Comparison

Comparison is permitted only when authoritative compatibility semantics exist
for quantity, units, method, normalization, conditions, and source type.
Capability-specific comparison viewers remain the current product path. The
browser does not calculate compatibility or scientific normalizations.

## Historical and long-running research

Research is reopened from durable ResearchSession/ResearchTurn/Job state.
Completed Results remain usable after failure or cancellation. A historical
pre-ResearchTurn run is labelled honestly as read-only and does not receive an
invented research question or branch.

## Mobile and accessibility

At approximately 390×844, Research uses one primary pane with explicit
conversation/workbench switching. New surfaces preserve semantic headings,
keyboard controls, visible status text, non-color-only states, and bounded
tables/viewers. No frontend scientific computation was added.

## Known limitations

- Generic cross-domain Result comparison is not a universal browser feature;
  current comparisons use authoritative capability/viewer-specific contracts.
- Pre-ResearchTurn historical runs cannot reconstruct missing questions or
  branches.
- Several specialist viewers retain English scientific labels; this does not
  change scientific semantics but remains localization polish.

