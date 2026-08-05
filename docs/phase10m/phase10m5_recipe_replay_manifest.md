# Phase 10M-5 Recipe Replay Manifest

`RecipeReplayManifest 1.0` preserves exact Project, Dataset/version/hash,
Profile, Intent, Eligibility, Planner decision, Plan, steps, tools/adapters,
parameters, resources, expected outputs, original Artifact checksums, execution
outcome, provider/environment provenance, warnings, and limitations.

For AnalysisPlan 0.1 it records `planSchemaVersion = 0.1` and
`dependencyModel = NONE_OR_SEQUENTIAL_INDEPENDENT`; no graph or binding is
invented. For AnalysisPlan 0.2 it records the exact graph hash, ordered typed
dependencies, producer/consumer ports, Artifact bindings, blocked descendants,
independent branches, and partial outcome.

All replay authority flags are fixed false:

```text
executionAuthorized = false
planCreated = false
jobCreated = false
queueMessageCreated = false
automaticReplay = false
```

The Recipe is an immutable declaration for a future separately authorized
workflow. M5 never invokes Planner, Runtime, Registry, Adapter, or queue.
