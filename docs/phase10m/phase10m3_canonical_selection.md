# Phase 10M-3 Canonical Selection Runtime

Status: IMPLEMENTATION EXACT-SHA CI PASSED / COMPLETION-RECORD CI PENDING.

Phase 10M-3 activates the existing `WorkspaceSelectionContext 1.0` contract in
the `/workspaces/{workspaceId}` shell. A Workspace-scoped store validates exact
identity, project, Job, dataset version, and source-scope hash before publishing
to bounded panel subscribers. Equality is canonical JSON equality, not object
reference, row position, display text, or fuzzy matching.

The runtime supports all 13 sealed selection kinds. It does not claim that every
current Artifact exposes every object identity: missing site, atom, frame,
q-point, branch, or region identity remains `UNSUPPORTED`/`NOT_APPLICABLE`.
Whole Artifact selection is the only production panel emission implemented in
M3 because it can be constructed from exact `WorkspaceSourceRef` metadata.

Selection is transient in React memory and the URL. Persistence occurs only
through the existing explicit Workspace PATCH/ETag Pin command. Selection has
no ToolCall, Job, enqueue, provider, Artifact-payload, or scientific authority.

Hard caps: 16 secondary refs, 32 subscribers/panels, 2,048 URL-token bytes,
131,072 canonical context bytes, and JSON depth 14.
