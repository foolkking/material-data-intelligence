# Phase 10L-3 Dependency Runtime Execution

## Runtime Flow

For a persisted AnalysisPlan 0.2, QueueWorkerRuntime:

```text
load exact job and persisted plan
  -> parse 0.2 and verify plan hash
  -> rerun dependency validator and PlanValidator
  -> compute deterministic topological order
  -> resolve each ready step's incoming artifact bindings
  -> execute the registered Adapter serially
  -> persist output artifacts and lineage
  -> persist binding resolutions and final execution record
  -> finalize job status and event summary
```

The 0.1 branch remains the existing independent step loop. Runtime does not
reinterpret 0.1 ordering as dependencies.

## Runtime Artifact Resolution

The plan stores only planned step/port/contract identities. After the producer
completes, Runtime constructs `ResolvedArtifactInputRef 1.0` from platform
records. Resolution requires exact:

- current project, dataset, job, plan ID, and plan hash;
- producer step, ToolCall, declared output port, and one matching Artifact;
- artifact kind, contract version, media type, and required provenance;
- size within producer, consumer, and platform caps;
- stored byte length and SHA-256 checksum;
- inert JSON materialization through ArtifactStorage.

The internal reference uses a platform-created `resolved:<bindingId>` object
key. It is not accepted from user or provider JSON and exposes no local path,
bucket key, presigned URL, or external fetch authority. The resulting role and
object type come from the declared consumer input port before the registered
Adapter validates its ordinary input contract.

## Idempotency

ToolCall persistence uses job/step identity, Artifact persistence uses stable
storage/checksum facts, and dependency execution, resolution, and lineage
records reject conflicting writes. A terminal dependency execution is returned
without rerunning Adapters. This is bounded replay idempotency, not a new retry
engine.

## Execution Authority

Only QueueWorkerRuntime invokes a Registry-resolved Adapter. Neither the
composer, provider, dependency record, artifact payload, frontend, nor API read
surface can execute tools or code.
