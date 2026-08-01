# Phase 10M-0 Workspace Panel Contract Proposal

Status: REVIEWER-SEALED RECOMMENDATION

```text
PANEL_CONTRACT_REQUIRED = YES
PANEL_CONTRACT_VERSION = 1.0
```

`WorkspacePanel 1.0` is a strict UI projection contract owned by the Workspace service. It does not replace Artifact, ToolCall, evidence, interpretation, report, or recipe contracts.

## Fields

- `panelId`: stable Workspace-local ID.
- `panelKind`: allowlisted `OVERVIEW`, `DATA`, `PLAN`, `EXECUTION`, `SCIENTIFIC_RESULT`, `FINDINGS`, `EVIDENCE`, `PROVENANCE`, `REPORT`.
- `title`: bounded inert text generated from repository metadata.
- exact source Artifact, Job, ToolCall, interpretation, report, and recipe refs.
- exact source identity and source-reference hash.
- `rendererContract`: allowlisted renderer key and version.
- loading/result/partial/error state using the Phase 10M projection taxonomy.
- accepted selection kinds and emitted exact selection kinds.
- evidence links and provenance refs.
- ordered bounded layout metadata.
- mobile presentation mode and accessible name.
- capability prerequisite and unsupported fallback.

## Rules

- A source artifact ref contains ID, checksum, contract/version, and media type.
- A renderer is selected from checked-in contract mapping, never artifact text or filename.
- A panel may load payload only through the existing authorized bounded artifact API.
- Invalid contracts use inert metadata/JSON fallback and `CONTRACT_UNSUPPORTED`; generic JSON is not a scientific renderer.
- Partial/failed source state remains visible and cannot be converted into `PRODUCED`.
- Selection propagation uses `WorkspaceSelectionContext 1.0` only.
- Layout has no execution, tool, plan, expression, path, URL, callback, HTML, or JavaScript fields.
- At most 32 panel records exist in one Workspace.

## Renderer ownership

Existing product components remain renderers after they are registered in a checked-in `WorkspaceRendererRegistry 1.0`. Each mapping declares exact artifact contracts, supported selection identities, lazy-loading boundary, text fallback, WebGL ownership, and cleanup hook. The registry is frontend presentation authority only and cannot validate or execute Tool Registry capabilities.

## State projections

Every panel provides accessible named representations for loading, result, partial, error, and unsupported states. Scientific charts and WebGL panels also provide contract-derived text/table alternatives. A failed panel cannot prevent unrelated panels from loading.
