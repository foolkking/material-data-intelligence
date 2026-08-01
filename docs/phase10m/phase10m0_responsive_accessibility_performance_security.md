# Phase 10M-0 Responsive, Accessibility, Performance, and Security Seal

Status: REVIEWER-SEALED RECOMMENDATION
Targets below are development acceptance and browser evidence targets, not production capacity claims.

## Desktop and mobile

Desktop uses the Phase 9C global header, collapsible/resizable data rail, Workspace secondary navigation, one active main panel, and contextual overlay inspector. Scientific panels own internal scrolling; the page has no nested horizontal scroll. Fullscreen remains an explicit user action.

At 390x844, exactly one panel is visible, data context is a drawer, panel navigation is a labelled switcher, inspector is a bottom sheet, and tables become semantic stacked records. Touch targets are at least 44x44 CSS pixels.

## Accessibility

- deterministic heading hierarchy and landmarks;
- logical keyboard focus order and visible focus;
- focus restoration after drawers, inspector, and fullscreen;
- status updates through bounded live regions;
- warnings and partial states use icon/text, never color alone;
- charts expose contract-derived table/text alternatives;
- WebGL exposes a scientific text fallback and does not trap focus;
- reduced-motion disables nonessential animation;
- 200% browser zoom remains usable without document horizontal overflow;
- semantic controls and accessible names for every panel action.

Empty, loading, partial, stale, unsupported, blocked, and failed states use typed messages with source identity and next safe navigation action. They never collapse into `Something went wrong`.

## Loading and performance

- Initial `GET /workspaces/{id}` is metadata-first and at most 524,288 bytes.
- Only the active panel loads a scientific payload; adjacent metadata prefetch is disabled.
- At most four concurrent Workspace data requests run per browser tab.
- Artifact metadata precedes content; binary/large-array content is streamed or range-loaded through existing storage abstractions.
- Requests are cancellable on panel/source changes.
- SSE remains execution-state authority while a Job is active; completed workspaces stop polling.
- WebGL/canvas panels dispose controls, buffers, textures, object URLs, observers, and animation frames on unmount/context loss.
- Trajectory and volumetric panels keep existing caps and never preload all frames/voxels solely for Workspace navigation.
- Browser cache keys include Workspace revision and source hash.

```text
WORKSPACE_PROJECTION_CACHE_ENABLED = YES
WORKSPACE_ADJACENT_METADATA_PREFETCH = NO
```

Browser evidence targets:

- metadata snapshot response within 2 s on seeded local service-backed fixtures;
- active non-WebGL panel interactive within 3 s after metadata on seeded fixtures;
- no monotonic request, canvas, WebGL-context, object-URL, or listener growth across 20 panel switches;
- no document-level horizontal overflow at 390x844 and 200% zoom;
- no unbounded payload, recursion, polling, or prefetch.

## Security boundary

Artifact content is inert data. Workspace has no tool, plan, provider, queue, shell, filesystem, network callback, or scientific computation authority.

Required future markers:

```text
NO_WORKSPACE_ARBITRARY_CODE_EXECUTION
NO_WORKSPACE_SHELL_OR_FILESYSTEM_AUTHORITY
NO_ARTIFACT_JAVASCRIPT
NO_ARTIFACT_HTML_EXECUTION
NO_ARTIFACT_IFRAME
NO_EXTERNAL_ARTIFACT_URL_EXECUTION
NO_UNSAFE_SVG_EXECUTION
NO_ARTIFACT_MODULE_OR_SHADER_AUTHORITY
NO_INTERPRETATION_RECOMMENDATION_EXECUTION
NO_WORKSPACE_PLAN_JOB_OR_ENQUEUE_AUTHORITY
NO_CROSS_JOB_OR_CROSS_PROJECT_ARTIFACT_ACCESS
NO_STALE_IDENTITY_REBINDING
NO_SECRET_PATH_OR_STACK_DISCLOSURE
NO_FRONTEND_SCIENTIFIC_AUTHORITY
```

Markdown disables raw HTML and active external links. Downloads use server-authorized inert responses with nosniff/content-disposition controls. User/artifact prompt-injection text is rendered as text and never becomes an instruction. Three.js accepts only checked-in renderer code and validated bounded data; artifact-provided modules, shaders, URLs, and callbacks are rejected.
