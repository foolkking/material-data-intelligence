# Agent 2.0 Scientific Viewer Contract

Phase 9 uses the existing `ScientificObject` and `ScientificObjectVersion` as
the data authority. `ScientificViewerRegistry` resolves a trusted internal
viewer descriptor deterministically from object type, schema version and
semantic role. The backend viewer endpoint authorizes the exact object/version
before reading a bounded normalized payload; it never invokes Redis, a Job, a
ToolCall or an LLM.

## Viewer projection boundary

`ScientificViewerProjection 1.0` contains display name/version, canonical
scientific metadata, source references, payload status, limitations and a
bounded family-specific payload. Large tables, trajectories and volumetric
arrays are capped or represented as metadata-only states. Missing or
invalidated sources remain readable as historical metadata and are never
silently replaced by a same-name current object.

Data, Result and Report reuse the same renderer grammar. The existing
Workspace/Artifact renderers remain compatibility implementations and advanced
technical views; they are not a second scientific authority.

## Scientific selection

`ScientificSelectionContext 1.0` is the semantic interaction contract:

- exact `ScientificObjectRef` (project, object and version)
- trusted viewer id and selection type
- bounded scalar `semantic_locator` (site, peak, frame, row, interval, etc.)
- human display label and optional evidence locator

When a selection starts a ResearchTurn it is validated against the project and
version, then persisted in the immutable `ResearchContextSnapshot` through
`scientific_selections_json` (`0025_agent2_scientific_selection`). Later UI
selections cannot mutate an earlier Turn. Provider context uses opaque
selection labels; UUIDs, Artifact identities and DOM indexes never cross that
boundary.

## Linked selection

`SelectionLinkResolver` is deterministic. It reports `LINKED`, `PARTIAL`,
`UNSUPPORTED` or `NOT_FOUND` for compatible mappings such as structure to site
metadata, XRD peak to peak table/evidence, RDF range to a grounded finding,
and Report evidence to the exact source viewer. Unsupported mappings disclose
that precise highlighting is unavailable rather than guessing.

## Product surface

Project Data is data-first: context browser on the left and a large scientific
viewer on the right. The viewer shell presents scientific metadata,
limitations/relevance, one primary “研究此数据” action and progressive
technical details. Research, Result and Report links carry exact source
identity and bounded selection context. Mobile layouts stack the context and
viewer without global horizontal overflow; tables may scroll only inside their
own bounded container.
