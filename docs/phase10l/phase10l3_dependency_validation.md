# Phase 10L-3 Dependency Validation

## Validation Order

The canonical request path preserves Phase 10L-1 and 10L-2 validation, then
applies these additional gates:

1. Parse strict AnalysisPlan 0.2 and verify its plan hash.
2. Verify exact L2 selected-tool membership.
3. Rebuild ToolArtifactPortMetadata 1.1 for those selected tools.
4. Recompute the exact Registry compatibility matrix.
5. Recompute every binding identity and the graph hash.
6. Validate step, port, contract, media, cardinality, and scope facts.
7. Reject duplicate consumer ports, cycles, and all graph cap overflows.
8. Compute deterministic topological order.
9. Run the existing capability-context checks.
10. Run the existing PlanValidator for tools and ordinary parameters.

Runtime repeats strict plan parsing, plan-hash verification, dependency
validation, and PlanValidator before invoking any Adapter. Runtime validation
does not repair or reinterpret persisted plans.

## Typed Diagnostics

The contract includes bounded diagnostics for missing ports, artifact kind,
contract version, media type, cardinality, identity scope, resource version,
size, determinism, trust, base-resource availability, visibility, composition
permission, cycles, caps, unknown steps, duplicates, selected-tool mismatch,
invalid binding identity, invalid graph identity, and external authority.

Schema-level graph failures are currently surfaced through the bounded
`GRAPH_CAP_EXCEEDED` validation envelope with the strict model error preserved
in the message. Callers must use the typed top-level planning outcome and must
not infer success from an empty diagnostic array.

## Failure Effects

Planning-time invalid dependency content yields `VALIDATION_FAILED` and cannot
create a plan, job, queue message, ToolCall, or Artifact. If persisted state is
tampered with after planning, Runtime writes a `VALIDATION_ABORTED` dependency
execution record, marks every step `NOT_STARTED`, invokes no Adapter, and
finalizes the job as failed.

No invalid 0.2 plan is downgraded to 0.1.
