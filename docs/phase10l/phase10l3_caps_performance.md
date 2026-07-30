# Phase 10L-3 Caps and Performance

Status: hard caps and local bounded measurements are recorded. Exact-SHA CI is
still required; the measurements are not a production capacity claim.

## Hard Caps

| Surface | Limit |
|---|---:|
| Plan steps | 4 |
| Dependency bindings | 6 |
| Graph depth | 4 |
| Incoming bindings per step | 3 |
| Outgoing bindings per step | 3 |
| Artifact ports per tool collection | 16 |
| Dependency diagnostics | 128 |
| Planning JSON depth | 14 |
| Serialized dependency planning payload | 524,288 bytes |
| Phonon dependency artifact per port | 16,000,000 bytes |
| Runtime absolute artifact check | 268,435,456 bytes |
| Total shared L2/L3 repair attempts | 1 |

Existing stricter Registry, provider, API, ArtifactStorage, Adapter, and
AnalysisPlan limits remain authoritative. Cap overflow fails; it does not
truncate a Registry matrix, binding list, graph, diagnostic, or artifact.

## Complexity

The graph is capped at four nodes. Topological ordering and descendant state
propagation use bounded in-memory structures and stable sorting; no graph or
workflow dependency is added. Runtime resolves one artifact at a time and
loads bytes only for the current binding. It does not preload all artifacts or
recursively traverse an unbounded graph.

## Local Near-Cap Measurement

The retained deterministic probe uses four steps and all six legal bindings:

| Measurement | Result |
|---|---:|
| Serialized AnalysisPlan 0.2 | 3,619 bytes |
| Validation + stable topological sort | 2.545 ms |
| Tracemalloc peak | 43,486 bytes |
| Graph depth | 4 |
| Topological order | `step_0 -> step_1 -> step_2 -> step_3` |

The exact values are machine-local and retained in
`evidence/phase10l3_bounded_multi_tool/performance_audit.md` with plan and graph
hashes.

## Closure Measurements

The evidence phase must record, using the actual implementation:

- four-step near-cap graph and maximum valid binding coverage;
- contract/metadata validation, matrix, composition, and graph validation
  wall time;
- serialized plan, matrix, execution record, and lineage sizes;
- runtime Artifact resolution size and memory behavior;
- ToolCall, Artifact, binding-resolution, and lineage row counts;
- replay behavior without monotonic duplicate growth;
- typed over-cap rejection before unbounded allocation.

Generator/manifest and browser rendering are complete locally. Full regression
and exact-SHA CI remain closure requirements.
