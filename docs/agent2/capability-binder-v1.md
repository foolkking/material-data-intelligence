# Capability Binder 1.0

The Binder is deterministic implementation selection:

```text
validated CapabilityPlan
  -> stable ToolBinding priority and Tool ID order
  -> exact Tool version constraint
  -> existing typed artifact port compatibility
  -> AnalysisPlan 0.2
  -> existing dependency validator and PlanValidator
```

Source inputs keep the exact `ScientificObjectVersion` ID from the immutable
context snapshot. The root dataset is derived from that version's authorized
source resource refs; its persisted DataProfile is required. User constraints
override capability/tool defaults through explicit parameter mappings (for
example `cutoff_angstrom` to `r_max_angstrom`).

The Binder does not create a Job, ToolCall, Artifact or runtime identity.
Cross-Job historical Result artifact reuse is not bound in Phase 3 because the
existing AnalysisPlan 0.2 contract permits only same-plan typed dependency
bindings and explicitly forbids predeclared runtime Artifact IDs.
