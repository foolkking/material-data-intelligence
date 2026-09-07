# Import Boundary Rules

**Previous freeze:** `FROZEN_BASELINE_V1`
**Current:** `FROZEN_BASELINE_V2`
**Amendment date:** 2026-09-06
**Freeze status:** `ARCHITECTURE_FREEZE_AMENDED_PENDING_BASELINE_COMMIT`

These are target dependency rules. Current violations are classified and assigned to Batch 0; this document does not change imports.

## Direction

```text
bootstrap/composition root
  composes transport + concrete infrastructure

transport -> application -> domain contracts/ports
                              ^
                              |
                    infrastructure implements

legacy path -> compatibility facade -> canonical implementation
```

Domain may define pure ports. Application coordinates those ports and must not select concrete implementations. Infrastructure implements ports. Bootstrap selects implementations. Transport adapts inputs and calls application boundaries.

## Allowed and Forbidden Imports

| From | Allowed | Forbidden |
|---|---|---|
| `bootstrap` | transport, application, domain, infrastructure, stable packages | duplicated business policy |
| `transport` | application interfaces, shared schemas, transport auth contracts | DB sessions, concrete repositories, provider SDKs, private infrastructure helpers |
| `application` | domain types/ports, stable schemas, abstract queue/storage/provider ports | routers/FastAPI, concrete DB/storage/provider implementations, UI |
| `domain` | pure domain types/policies/ports and stable value schemas | config globals, DB/session, filesystem, RQ/FastAPI, bootstrap, transport, UI |
| `infrastructure` | domain/application ports, stable schemas, implementation libraries | transport composition, route-specific policy, compatibility |
| `compatibility` | canonical modules and stable schemas | owning business logic or being imported by canonical modules |
| `services/workers` | worker runtime, stable application-facing entrypoints, schemas | arbitrary `mdi_api` internals or route/private helpers |
| frontend route | feature entrypoint and shared route/layout contracts | feature implementation internals beyond its entrypoint |
| frontend feature | own feature modules, shared API/UI/layout/types, viewer public boundary | unrelated feature internals or server-only secrets |
| frontend shared | generic cross-feature primitives | feature-specific state/orchestration |
| scientific viewer | viewer contracts, engines and co-located workers | shell/navigation or unrelated feature policy |

## Current Classified Violations

| ID | Current edge | Classification | Required disposition |
|---|---|---|---|
| `IB-001` | `report_composition -> routers.planner._select_planner_provider` | `REVERSE_LAYER_DEPENDENCY` | Batch 0 extracts provider selection to an application/provider boundary; router and composition both call it. |
| `IB-002` | `research_agent.service -> routers.auth.CurrentUser` | `REVERSE_LAYER_DEPENDENCY` | Introduce a transport-neutral actor/auth context contract; router adapts `CurrentUser`. |
| `IB-003` | `tool-registry.planner_metadata -> adapters.registry` and `adapters.executor -> tool-registry` | `CYCLE` / composition dependency | Bootstrap supplies adapter metadata/registry to Tool Registry-facing planning logic; identities remain stable. |
| `IB-004` | `services/workers -> mdi_api` persistence/services/config internals | `IMPLEMENTATION_LEAK` | Preserve RQ handlers, route calls through stable application entrypoints, and reduce internals incrementally. |
| `IB-005` | research/application modules -> concrete config/database globals | `IMPLEMENTATION_LEAK` | Define ports/services and compose concrete implementations at bootstrap. |
| `IB-006` | routers construct/use repositories and private helpers | `TRANSPORT_LEAK` | Extract application boundaries before router relocation. |
| `IB-007` | mixed root modules contain ports plus implementations | `MIXED_LAYER` | Split by symbol group; no whole-file move. |

No source exception is approved as target architecture merely because it exists today.

## Stable Package Rules

- `packages/schemas`: shared DTOs, queue names, persisted contract shapes; no application orchestration.
- `packages/tool-registry`: tool identity, manifest loading, validation; no arbitrary execution authority.
- `packages/adapters`: scientific adapter authority; identity and semantics immutable.
- `packages/artifact-core`: artifact contract authority.
- `packages/material-parsers`: parser boundary, not UI or queue orchestration.
- `services/llm`: provider clients and role-bounded model interactions.
- `services/workers`: worker runtime adapters and stable handler entrypoints.

Path stability does not exempt internal package edges from Batch 0 normalization.

## Compatibility Rules

1. Old public or dotted paths remain resolvable when marked `KEEP_OLD_PATH` or `SHIM_OLD_PATH`.
2. A shim imports/re-exports canonical symbols or adapts legacy signatures only.
3. Canonical code must not import compatibility code; enforce this with a future static guard.
4. Public exports include module constants, externally imported functions/classes, `__all__`, patch targets, FastAPI dependencies, and dynamic handlers.
5. A moved worker implementation is reached through the old queue handler shim until a separately approved persisted-contract migration.
6. Removal requires a compatibility period, zero remaining readers, and separate approval.

## Report Provider Selection Freeze

- `CURRENT_OWNER`: private `_select_planner_provider` in `mdi_api.routers.planner`.
- `CURRENT_CALLERS`: planner transport and `report_composition._provider_report_projection`.
- `PROPOSED_OWNER`: stable application/provider-selection service or bootstrap-selected provider boundary.
- `TARGET_CALLERS`: planner router and report composition application service.
- `PUBLIC_CONTRACT`: provider selection result/error semantics; no new API surface required.
- `BEHAVIOR_INVARIANT`: same provider eligibility, configuration, fallback, authorization/secrets handling, and report output semantics.
- `BATCH0_VERIFICATION`: focused unit tests, import graph absence of application→router edge, unchanged report/planner contracts.

## Future Static Gates

- Reject canonical→compatibility, domain→transport/bootstrap/infrastructure, and application→concrete-infrastructure edges.
- Detect import graph cycles at module and package levels, including lazy imports.
- Compare public export surfaces pre/post.
- Scan dotted handlers, importlib/`__import__`, command paths, dynamic imports, worker URLs, CI/qualification/test path strings.
- Compare queue names and handlers byte-for-byte.

Physical relocation remains unauthorized.
