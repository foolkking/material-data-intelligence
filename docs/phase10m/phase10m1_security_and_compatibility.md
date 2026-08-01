# Phase 10M-1 Security and Compatibility

Status: local security/compatibility gates pass. Service-backed evidence and
exact-SHA CI remain **PENDING**.

## Authority boundary

Workspace is a presentation and persistence organization layer. It has no
ToolCall, Job, Plan, queue, provider, scientific calculation, or
interpretation authority. Creating or patching a Workspace cannot execute a
tool, invoke an LLM, mutate a Job, enqueue work, or publish a scientific
result.

`REAL_LLM_CALLS = 0` for this M1 implementation path.

## Input and rendering safety

Workspace contracts reject unknown fields, prototype-pollution keys,
non-finite values, unsafe URL/path/module-like text, oversized/deep JSON,
duplicate selection identities, and out-of-scope source references. Titles,
notes, warnings, and panel text are inert validated text. Panel renderer
contracts are allowlisted; arbitrary component paths and executable content
are not accepted.

Workspace snapshots contain source references and bounded metadata only. The
projection does not copy Artifact payloads or expose storage keys, bucket
names, local paths, credentials, Authorization headers, provider prompts, or
raw Artifact bodies.

Project ownership/scope is checked by the current API access mechanism. Source
references are immutable; stale identities are projected as stale/read-only
rather than rebound to a latest version. Cross-project Job/Artifact sources
are rejected.

## Compatibility guarantees

The implementation is additive. AnalysisIntent 1.0, EligibilityResolution
1.0, AnalysisPlan 0.1/0.2, PlanValidator, QueueWorkerRuntime, Tool Registry,
Adapters, Job/ToolCall/Artifact semantics, Interpretation, Report, Recipe,
and the root PlannerWorkbench remain outside Workspace mutation paths.

Historical Jobs are lazily projected only by an explicit operation. Existing
records are not rewritten, and missing modern identity produces a typed
legacy/read-only or unsupported state instead of silent scientific upgrade.

No Workspace page, `/workspaces/{workspaceId}` UI, selection propagation,
renderer integration, Report/Recipe composition, or mobile Workspace UI is
implemented by M1 design.

## Verification markers

The following are verified local implementation markers; exact-SHA CI remains
the release gate:

```text
NO_WORKSPACE_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_SHELL_OR_FILESYSTEM_AUTHORITY = PASS
NO_WORKSPACE_PROVIDER_AUTHORITY = PASS
NO_WORKSPACE_TOOLCALL_JOB_OR_ENQUEUE_AUTHORITY = PASS
NO_WORKSPACE_ARTIFACT_PAYLOAD_COPY = PASS
NO_WORKSPACE_CROSS_PROJECT_SOURCE_ACCESS = PASS
NO_WORKSPACE_STALE_IDENTITY_REBINDING = PASS
NO_SECRET_PATTERN_HITS = PASS
REAL_LLM_CALLS = 0
```
