# Phase 10L-3 AnalysisPlan 0.2 Contract

Status: implementation contract; exact-SHA verification remains pending.

## Additive Versioning

`AnalysisPlan 0.1` remains readable and retains its existing hash and
execution semantics. `AnalysisPlan 0.2` is additive and is emitted only by the
canonical Intent/capability-aware path when selected tools have an exact typed
artifact dependency. There is no implicit 0.1-to-0.2 migration.

An independent selection with no compatible dependency pair remains a valid
0.1 plan. In particular, a list of 0.1 steps is never reinterpreted as a graph.

## Shape

AnalysisPlan 0.2 reuses the existing strict `AnalysisStep` and
`ExpectedArtifact` contracts and adds:

```json
{
  "schemaVersion": "0.2",
  "graphHash": "<sha256>",
  "dependencyBindings": []
}
```

The inherited fields remain `goal`, `datasetId`, `profileId`,
`toolRegistryVersion`, `assumptions`, `warnings`, `steps`, and
`expectedArtifacts`.

For 0.2, artifact dependencies may not appear in step `inputRefs`. The only
authoritative artifact dependency representation is the plan-level
`dependencyBindings` array. Runtime creates the internal artifact input refs
only after a producer succeeds and the stored artifact passes all binding
checks.

## Identity

- Binding IDs are deterministic over all semantic binding fields other than
  `bindingId`.
- `graphHash` is SHA-256 over canonically sorted dependency bindings.
- The plan hash is SHA-256 over the full canonical 0.2 plan.
- Canonical JSON uses UTF-8, sorted keys, compact separators, unescaped
  Unicode, and rejects non-finite values.
- Timestamps, database IDs, ToolCall IDs, and runtime Artifact IDs do not
  influence plan or graph semantic identity.

## Validation

The strict model rejects unknown fields, duplicate step IDs, artifact
`inputRefs`, a mismatched graph hash, cycles, unknown steps, duplicate
bindings, duplicate consumer ports, graph depth overflow, incoming/outgoing
overflow, oversized JSON, and non-finite values. The independent dependency
validator then recomputes Registry port compatibility and exact L2 tool
membership. The unchanged PlanValidator remains the final tool/parameter gate.

## Caps

| Item | Limit |
|---|---:|
| Steps | 4 |
| Dependency bindings | 6 |
| Graph depth | 4 |
| Incoming bindings per step | 3 |
| Outgoing bindings per step | 3 |
| JSON depth | 14 |
| Serialized planning payload | 524,288 bytes |

Overflow is a typed validation failure. The implementation does not truncate
steps or bindings to force a plan to fit.

## Checked Authorities

- Python: `mdi_schemas.dependency_planning.AnalysisPlanV02`
- JSON Schema: `packages/schemas/json/dependency-planning-v1.schema.json`
- TypeScript: `packages/schemas/src/index.ts`
- Plan hash: repository canonical plan hashing with an additive 0.2 branch
