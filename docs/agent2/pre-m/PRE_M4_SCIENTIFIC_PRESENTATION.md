# Pre-M4 Scientific Presentation

Status: `PASS_WITH_EXPLICIT_LIMITS`  
Date: 2026-09-11

## Presentation LOD

```text
PRESENTATION_LOD MUST NOT CHANGE SCIENTIFIC_RESULT
```

Current scientific viewers and Artifact previews retain canonical payloads and
use bounded presentation projections. Pre-M added explicit visible/total
denominators for:

- electronic band series, band-state rows, DOS channels and DOS rows;
- experimental XRD peak correspondences;
- local-environment sites;
- coordination neighbor relations;
- generic plot/table/text Artifact previews.

The browser performs no scientific resampling for execution. Plot display
sampling is labeled as presentation-only and never feeds an AnalysisPlan.

## Viewer and linked-selection boundaries

Existing family viewers preserve title/source/state/limitation, reset/inspect/
select/clear/export affordances and domain controls. Heavy viewers remain lazy
and capped to one active heavy lease where required.

```text
VIEWING_FOCUS != RESEARCH_CONTEXT
RESEARCH_CONTEXT != ANALYSIS_INPUT
```

Only exact compatible mappings propagate linked selection. Any selection that
changes computation must enter a validated AnalysisPlan.

## Report and provider visibility

Reports remain persisted scientific communication: question, conclusion,
findings, evidence, nearby limitations, figures, methods, literature,
unresolved questions and reproducibility. Report prose is not later scientific
evidence and cannot strengthen ClaimSupport.

Provider/model identity remains low-emphasis in ordinary scientist views and
auditable in advanced provenance. API keys, hidden prompts/reasoning and raw
retry traces are never shown.

## Verification

- Focused viewer tests: `23 passed`.
- Report route/access tests: `39 passed`.
- Frontend typecheck and production build: PASS.
- Frontend scientific recomputation detected by browser evidence: `0`.
