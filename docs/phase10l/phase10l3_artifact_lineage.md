# Phase 10L-3 Artifact Lineage

## Contract

Each artifact produced during 0.2 execution receives one immutable
`ArtifactLineageRecord 1.0`. It binds:

- project, dataset/version, and Profile ID/hash;
- Intent, EligibilityResolution, and capability decision ID/hash when present;
- plan ID/hash/schema, graph hash, and job ID;
- producer step, ToolCall, tool/version, and output port;
- artifact ID, kind, contract version, media type, and content hash;
- upstream artifact IDs/hashes and binding IDs;
- Adapter/runtime version, warnings, caps, and creation time.

The lineage hash excludes `createdAt`; the deterministic lineage ID derives
from that semantic hash. Runtime and database IDs do not become plan identity.

## Traversal

Persisted records support:

```text
artifact -> producer ToolCall -> producer step -> plan
artifact -> upstream artifact hashes and binding IDs
consumer ToolCall -> runtime binding resolution -> exact source artifact
```

Array position, UI order, report prose, filenames, or display labels are not
lineage authority.

## Persistence

Alembic revision `0005_phase10l3_dependency` adds:

- `plan_dependency_bindings` for queryable copies of plan-source bindings;
- `runtime_artifact_binding_resolutions` for per-job resolution results;
- `dependency_execution_records` for final graph execution state;
- `artifact_lineage_records` for one immutable lineage record per Artifact.

The AnalysisPlan 0.2 JSON remains the semantic source of truth for planned
bindings. Relational rows are immutable audit/index records and cannot create a
second graph definition.
