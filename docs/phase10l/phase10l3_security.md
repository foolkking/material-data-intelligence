# Phase 10L-3 Security Boundary

Status: contract implemented; required automated security evidence remains
pending until the Phase 10L-3 evidence gate runs.

## No New Authority

Dependency planning and artifact lineage are inert data operations. They grant
no Python, shell, filesystem, SQL, URL, callback, HTML, JavaScript, shader,
module, network, or external-science authority. Execution remains:

```text
validated persisted plan -> QueueWorkerRuntime -> Tool Registry -> Adapter
```

## Provider Isolation

The optional composition provider receives only exact selected tool IDs,
compatible pair IDs, ports, artifact kinds, contract versions, media types,
and bounded validation diagnostics. It does not receive rejected candidates,
the full Registry, artifact bytes, runtime Artifact IDs, paths, URLs, object
store coordinates, source code, or secrets.

The provider must return one bare strict JSON object matching
`DependencyCompositionProposal 1.0`. Markdown, prose wrappers, duplicate keys,
unknown fields, stale matrix identity, invented pairs, or out-of-domain pairs
fail. At most the remaining shared Phase 10L-2 repair budget may be used; there
is no Mock fallback.

## Runtime Artifact Boundary

- Only same-project, same-dataset, same-job, same-plan artifacts are accepted.
- Contract, media type, provenance, size, byte length, and SHA-256 are checked
  before materialization and before consumer Adapter invocation.
- Bytes are read only through ArtifactStorage and materialized as strict inert
  JSON.
- User/provider JSON cannot create `ResolvedArtifactInputRef`.
- Local paths, bucket keys, presigned URLs, external URLs, prior-job IDs, and
  foreign project artifacts are not Adapter authority.
- Artifact content is never sent to the composition provider.

## Required Closure Markers

The final evidence gate must establish, rather than merely document:

```text
REAL_LLM_CALLS = 0
NO_PHASE10L3_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS
NO_DEPENDENCY_ARBITRARY_CODE_EXECUTION
NO_DEPENDENCY_SHELL_OR_FILESYSTEM_AUTHORITY
NO_ARTIFACT_JAVASCRIPT
NO_ARTIFACT_HTML_EXECUTION
NO_ARTIFACT_CALLBACK
NO_ARTIFACT_SHADER
NO_ARTIFACT_MODULE
NO_EVAL
NO_FUNCTION_CONSTRUCTOR
NO_EXTERNAL_ARTIFACT_URL
NO_CROSS_JOB_ARTIFACT_BINDING
NO_CROSS_PROJECT_ARTIFACT_BINDING
NO_STALE_RESOURCE_BINDING
NO_UNDECLARED_ARTIFACT_PORT
NO_PROVIDER_ARTIFACT_PAYLOAD_EXPOSURE
NO_REJECTED_CANDIDATE_LEAK_TO_LLM
NO_FULL_REGISTRY_LEAK_TO_LLM
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES
NO_SECRET_PATTERN_HITS
```

Until generated evidence verifies these markers, their status is `PENDING`,
not PASS.
