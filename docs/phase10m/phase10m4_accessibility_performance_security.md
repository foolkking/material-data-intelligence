# Phase 10M-4 Accessibility, Performance, and Security

Status: local implementation and browser replay are complete; exact-SHA CI and
service-backed closure are pending.

## Accessibility and Responsive Behavior

The Gallery uses semantic controls and labeled renderer/status metadata. Charts
retain numeric/table fallbacks, and WebGL products retain textual summaries and
typed status. The mobile 390x844 replay verifies one active viewer, a 44 CSS
pixel minimum touch target, Inspector close focus and return focus, and zero
horizontal overflow. No state is communicated by color alone.

## Loading and Performance

Initial Workspace loading issues zero Artifact content requests. Only an
active/open Artifact can load payload. Loader cache identity includes Workspace
ID/revision, Artifact ID/checksum/type/version, and renderer contract/version.
Changing source identity aborts or suppresses stale work.

Current local browser evidence covers 21 metadata records, Dataset, ML,
Composition, Structure, Trajectory, Phonon, Brillouin-zone, Volumetric, generic
table, legacy, HTML-inert, context-loss, 50 Chromium heavy switches, and mobile.
The replay records at most one active canvas and no unbounded canvas growth.
The measurements are development/browser acceptance evidence, not a production
capacity claim.

## Security Invariants

```text
NO_ARTIFACT_GALLERY_ARBITRARY_CODE_EXECUTION
NO_ARTIFACT_HTML_EXECUTION
NO_ARTIFACT_JAVASCRIPT_EXECUTION
NO_ARTIFACT_IFRAME_EXECUTION
NO_ARTIFACT_DYNAMIC_MODULE_EXECUTION
NO_ARTIFACT_EXTERNAL_URL_EXECUTION
NO_ARTIFACT_COMPONENT_NAME_AUTHORITY
NO_ARTIFACT_FILENAME_RENDERER_AUTHORITY
NO_CROSS_PROJECT_ARTIFACT_ACCESS
NO_CROSS_JOB_ARTIFACT_INJECTION
NO_STALE_ARTIFACT_REBINDING
NO_ARTIFACT_CHECKSUM_BYPASS
NO_FRONTEND_SCIENTIFIC_RECOMPUTATION
NO_SELECTION_ARRAY_INDEX_AUTHORITY
NO_SELECTION_DISPLAY_LABEL_AUTHORITY
NO_SELECTION_FUZZY_MATCH
NO_RECOMMENDATION_EXECUTION
```

Payload loading requires exact Workspace/Project/Job/Artifact scope, a valid
SHA-256 identity, bounded length, exact contract/version, safe content type,
and abort support. JSON rejects excessive depth, prototype-pollution keys, and
non-finite values. HTML, JavaScript, SVG scripts, iframes, data/external URLs,
dynamic modules, and artifact-provided component names are never executed.

M4 introduces no LLM call site. Local tests and browser replay use
`REAL_LLM_CALLS = 0`. The permanent policy remains DeepSeek-only for any future
real call, through the existing transport with `DEEPSEEK_KEY` as the sole key
source. Artifact renderers have no provider authority.
