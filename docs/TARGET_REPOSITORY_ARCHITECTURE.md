# Target Repository Architecture

**Previous freeze:** `FROZEN_BASELINE_V1`
**Current:** `FROZEN_BASELINE_V2`
**Amendment date:** 2026-09-06
**Baseline:** `268106e7634472cc8a815e27a8bf3d3eda16be1d` on `master`
**Freeze status:** `ARCHITECTURE_FREEZE_AMENDED_PENDING_BASELINE_COMMIT`
**Physical file moves authorized:** `NO`

V2 corrects V1's geometry-as-behavior classification, whole-file migration model, compatibility ownership, frontend source boundary, and unresolved dependency ordering. It freezes an architecture target and Batch 0 prerequisites only. It does not authorize source changes, cleanup, runtime mutation, or physical relocation.

## Architectural Decision

The target separates canonical implementation from compatibility identities:

```text
bootstrap/composition
    -> transport adapters
    -> application use cases and ports
    -> domain policies/contracts
    <- infrastructure implementations selected by bootstrap

legacy public/dynamic path -> thin compatibility facade -> canonical symbol
```

Compatibility may import and re-export canonical symbols or adapt a legacy signature. Canonical implementation must never depend on compatibility, and compatibility must not become the permanent owner of historical business logic.

## Target Repository Shape

Legend: `KEEP` preserves path/public identity; `MOVE` is a later candidate; `REVIEW` requires symbol extraction or Batch 0 first; `IMMUTABLE/HISTORICAL` is excluded from this migration.

```text
apps/
├── api/
│   ├── mdi_api/
│   │   ├── bootstrap/                  # MOVE/REVIEW: composition, startup, config wiring
│   │   ├── transport/
│   │   │   ├── http/                   # MOVE/REVIEW: thin FastAPI routers/dependencies
│   │   │   └── queue/                  # REVIEW: handler adapters, never queue identity owner
│   │   ├── application/
│   │   │   ├── projects/
│   │   │   ├── research/
│   │   │   ├── scientific_objects/
│   │   │   ├── scientific_results/
│   │   │   ├── scientific_reports/
│   │   │   └── workspaces/
│   │   ├── domain/                     # pure types, policies, ports, state semantics
│   │   │   ├── projects/
│   │   │   ├── research/
│   │   │   ├── scientific_objects/
│   │   │   ├── scientific_results/
│   │   │   ├── scientific_reports/
│   │   │   └── workspaces/
│   │   ├── infrastructure/
│   │   │   ├── persistence/
│   │   │   ├── storage/
│   │   │   └── providers/
│   │   └── compatibility/              # future thin facades only
│   └── alembic/                        # IMMUTABLE/HISTORICAL revision identity
└── web/
    ├── app/                             # KEEP: thin Next App Router tree only
    ├── features/
    │   ├── projects/
    │   ├── data/
    │   ├── research/
    │   ├── reports/
    │   ├── tasks/
    │   ├── notifications/
    │   ├── account/
    │   └── administration/
    ├── scientific-viewers/             # viewer families and worker-co-located assets
    ├── shared/
    │   ├── layout/
    │   ├── ui/
    │   ├── api/
    │   ├── hooks/
    │   ├── types/
    │   └── utils/
    └── styles/                          # later CSS ownership target; no change in freeze

packages/
├── adapters/                            # KEEP path/public/scientific identity
├── artifact-core/                       # KEEP
├── material-parsers/                    # KEEP
├── schemas/                             # KEEP shared/persisted contracts
└── tool-registry/                       # KEEP path/public/tool identity

services/
├── llm/                                 # KEEP provider boundary
└── workers/                             # KEEP runtime/role paths; normalize dependencies first

config/, scripts/                        # KEEP runtime, CI, qualification and retention authorities
docs/, persistent/, design/             # documentation/evidence governance, not source layers
.runtime_services/, _qualification/,
.qualification_runs/, Data/, caches      # runtime/evidence authorities, not source architecture
```

## Frontend Freeze Decision

`FRONTEND_TARGET_ARCHITECTURE = THIN_APP_ROUTES_PLUS_EXTERNAL_FEATURES`.

Evidence supporting the decision:

- Existing `app/**/page.tsx` files already mainly compose route parameters and component imports.
- Next App Router permits application modules outside `app/`; no repository configuration requires feature code to remain under `app`.
- Current `tsconfig.json` uses bundler resolution and relative imports; aliases may be introduced later but are not a prerequisite to the target.
- Global CSS remains imported by the root layout; its future path is an implementation batch concern.
- `"use client"` boundaries remain on feature components; server route files stay thin.
- Dynamic viewer imports and `new URL(..., import.meta.url)` workers require cohesive moves and same-batch reference updates; they do not block the target.

Routes, redirects, query parameters, server/client semantics, dist directories, and build identities remain unchanged.

## Canonical Ownership Rules

| Layer | Owns | Excludes |
|---|---|---|
| Bootstrap | concrete composition, startup, configuration selection | business policy |
| Transport | HTTP/RQ input adaptation and response mapping | repository/database internals |
| Application | use-case orchestration, transactions, async submission, stable ports | FastAPI, raw SQL, provider SDK details |
| Domain | identity, state semantics, pure policy, ports | config globals, filesystem, queues, transport |
| Infrastructure | DB, object store, provider, repository implementations | route policy or feature state |
| Compatibility | old import/dotted identities and signature adapters | canonical business implementation |
| Frontend routes | URL composition and route parameter adaptation | feature behavior |
| Frontend features | feature state/pages/workbenches | unrelated feature internals |
| Shared frontend | genuinely cross-feature primitives/layout/API contracts | feature-owned orchestration |
| Scientific viewers | specialized viewers and co-located workers | global shell policy |

## Stable Boundaries

`packages/*` and `services/*` remain at their current paths. `KEEP` means preserve path and public identity, not preserve every internal dependency. The Tool Registry ↔ Adapter Registry composition cycle and worker imports of API internals are Batch 0 normalization subjects.

The following remain immutable for this migration: API/schema/migration identities; URLs; authorization; queue names and roles; handler resolvability; Tool and Adapter identities; ScientificObject/Version/Result/Artifact/Report authority; ResearchTurn semantics; runtime topology; release/qualification authorities.

## Migration Sequence

1. Commit/approve this V2 freeze at an exact SHA in a clean worktree.
2. Execute approved Batch 0 dependency-normalization tasks independently.
3. Recompute public exports, import graph, dynamic contracts, and tests.
4. Approve one symbol group or cohesive frontend group for relocation.
5. Introduce canonical implementation while retaining old-path shims.
6. Verify invariants and runtime contracts; rollback the batch on failure.
7. Consider shim deprecation only in a separately approved phase.

No row in `FILE_MOVE_MANIFEST.md` is ready for physical movement at this freeze.
