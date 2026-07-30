# Phase 10L-2 Security and Caps

## Hard Caps

The shared contract bounds the Registry snapshot at 64 tools, eligible set at
32, diagnostics at 256, binding-domain values at 64 per parameter, independent
selected tools at 4, JSON depth at 14, and serialized contract content at
524,288 bytes. Existing stricter AnalysisPlan, Registry, API, and provider
transport caps remain authoritative. Overflow is typed failure; semantic
collections are never truncated to force a selection.

The deterministic near-cap capture evaluates all 53 current entries, records
174 diagnostics and two eligible candidates, and selects one tool. The
resolution is 101,213 bytes and the decision 1,967 bytes. The measured local
resolve/select/bind/validate wall time is 205.819 ms with 2,339,126 peak bytes
reported by `tracemalloc`. These are bounded local evidence, not production
capacity claims.

## Security Boundary

Planner metadata, resolution, selection, binding, validation, and repair are
inert data transformations. They grant no tool execution, shell, filesystem,
network, SQL, URL, callback, HTML, script, shader, or artifact-JavaScript
authority. Tool execution remains behind validated AnalysisPlan, Registry, and
QueueWorkerRuntime.

The provider projection excludes the full Registry and every rejected tool.
Strict JSON parsing rejects duplicate keys, wrappers, unknown fields, invented
IDs, oversized payloads, and executable-shaped values. Prompt-injection and
HTML/script text remain inert; credential-shaped content is not persisted in
evidence or provider context.

Default evidence markers are:

```text
REAL_LLM_CALLS = 0
NO_PHASE10L2_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS
NO_CAPABILITY_PLANNER_ARBITRARY_CODE_EXECUTION
NO_CAPABILITY_PLANNER_SHELL_OR_FILESYSTEM_AUTHORITY
NO_CAPABILITY_PLANNER_ARTIFACT_JAVASCRIPT
NO_FULL_REGISTRY_LEAK_TO_LLM
NO_REJECTED_CANDIDATE_LEAK_TO_LLM
NO_SECRET_PATTERN_HITS
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES
```
