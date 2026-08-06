# Phase 10M Execution Lock

Status: REVIEWER-SEALED RECOMMENDATION

The implementation agent is not authorized to redesign Workspace identity, persistence, API, migration, routing, panel contracts, selection identity, report ownership, compatibility, security, or Phase ordering.

## Confirmed facts

Phase 10L is archived. The current product is `WORKSPACE_LIKE_SINGLE_PAGE`, not a formal Workspace. Job is the current analysis container; PlannerWorkbench has one root route and in-memory UI state. Current scientific records, artifact lineage, interpretation, Report, and Recipe persistence are reusable authorities. There is no Workspace table, API, route, history surface, global exact selection, or layout recovery.

## Locked implementation boundaries

Implementation agents may choose local names that follow repository conventions, query organization, component file splits, and test-helper structure. They may not change the sealed semantics, caps, endpoint behavior, route, table ownership, source authority, phase boundaries, or security markers. A conflict with current implementation truth, migration head, authorization model, or exact scientific identity requires stopping and returning evidence to the reviewer.

## Decision log

Every row contains the decision, evidence/rationale, rejected alternatives, affected scope and migration/API impact, acceptance/compatibility/security requirement, and status.

| ID | Decision | Evidence and rationale | Rejected alternatives | Scope and impact | Acceptance, compatibility, security | Status |
| --- | --- | --- | --- | --- | --- | --- |
| M-D001 | Persist `ScientificWorkspace 1.0` | Current UI state is volatile and six reads do not form recoverable identity | Pure client projection; Job mutation | New Workspace contracts/repository/table/API | M1-A01, M1-A02; source refs immutable; no payload copy | SEALED_FOR_REVIEWER_APPROVAL |
| M-D002 | One Workspace per Job | Job already binds exact plan/execution/artifacts/interpretation | Per dataset; multi-Job session | Unique project+source Job | M1-A02; historical Job identity preserved | SEALED_FOR_REVIEWER_APPROVAL |
| M-D003 | Workspace owns presentation state only | Existing repositories own scientific facts | Copy artifacts/evidence into Workspace | Store refs, layout, title, selection | M1-A01, M1-A02, M1-A08; no competing scientific authority | SEALED_FOR_REVIEWER_APPROVAL |
| M-D004 | Migration `0007` with three tables; source and Job deletion use `ON DELETE RESTRICT` | No existing table owns recoverable layout/panels; tombstone refs must remain valid | metadata.create_all; JSON on Job; cascading Job delete | Workspace/panel/revision tables; physical source deletion rejected | M1-A03, M1-A04; exact columns/FKs; downgrade; 129th revision typed reject | SEALED_FOR_REVIEWER_APPROVAL |
| M-D005 | Add bounded Workspace aggregate APIs with `Idempotency-Key`, `If-Match`, and fixed HTTP errors | Current independent reads cannot provide atomic revision/projection | Frontend joins only; API replacement | POST/GET/PATCH/list/history routes and fixed M5 report/recipe routes | M1-A05, M1-A06; auth, ETag, 201/200/304/400/401/403/404/409/410/412/415/422 | SEALED_FOR_REVIEWER_APPROVAL |
| M-D006 | Route `/workspaces/{workspaceId}` | Root is PlannerWorkbench and has no deep identity | Replace `/`; query-only Job route | New additive route | M2-A01, M2-A03; old URL preserved | SEALED_FOR_REVIEWER_APPROVAL |
| M-D007 | Lazy historical Job projection | Exact records exist; no Workspace rows exist | Bulk backfill; scientific reconstruction | POST projection + history list | M1-A07, M2-A05; legacy read-only | SEALED_FOR_REVIEWER_APPROVAL |
| M-D008 | Strict `WorkspacePanel 1.0` | Existing components lack common source/state/selection contract | Unstructured component props | Panel schema/repository/UI projection | M1-A01, M4-A01; no artifact authority | SEALED_FOR_REVIEWER_APPROVAL |
| M-D009 | Checked-in renderer registry | Current mappings are distributed across components | Artifact filename/content dispatch | Frontend presentation registry | M4-A01, M4-A02, M4-A03; inert fallback | SEALED_FOR_REVIEWER_APPROVAL |
| M-D010 | `WorkspaceSelectionContext 1.0` | Exact identities exist locally but no shared context | Array/display/fuzzy mapping | Contract, URL codec, inspector | M3-A01, M3-A02, M3-A03, M3-A04, M3-A05, M3-A06, M3-A07; scope/auth validation | SEALED_FOR_REVIEWER_APPROVAL |
| M-D011 | Reuse Report persistence with versioned composition | Report table/repository already exist | New duplicate report table | report_json + additive API/UI; no report migration | M5-A01, M5-A02, M5-A03, M5-A07; exact evidence/lineage | SEALED_FOR_REVIEWER_APPROVAL |
| M-D012 | Reuse Recipe persistence with `WorkspaceRecipe 1.0` | Recipe table already owns replay metadata | Workspace-embedded executable recipe | recipe_json + reviewed replay; no recipe migration | M5-A04, M5-A05, M5-A06, M5-A07; no silent upgrade/execution | SEALED_FOR_REVIEWER_APPROVAL |
| M-D013 | Project partial state from execution records | L3 has exact failed/blocked/independent states | Collapse to Job failed; hide branches | Workspace/panel status projection | M2-A04, M5-A02; successful sources only | SEALED_FOR_REVIEWER_APPROVAL |
| M-D014 | Use sealed projection taxonomy | Existing enums differ by domain and must remain compatible | New global runtime enum | UI projection only except panel state contract | M2-A04, M6-A03; no status mutation | SEALED_FOR_REVIEWER_APPROVAL |
| M-D015 | Mobile single-panel + drawer + bottom sheet | 390x844 cannot sustain data/main/inspector columns | Shrunk desktop grid; read-only mobile | Responsive shell/components | M2-A06, M2-A07, M6-A05, M6-A06 | SEALED_FOR_REVIEWER_APPROVAL |
| M-D016 | Accessible semantic alternatives are mandatory | Current product has mixed chart/WebGL surfaces | Canvas-only or color-only state | Shell and every renderer contract | M2-A07, M4-A07, M6-A06 | SEALED_FOR_REVIEWER_APPROVAL |
| M-D017 | Metadata-first, active-panel lazy loading; projection cache YES; adjacent metadata prefetch NO | Current artifact families include large arrays/WebGL | Eager aggregate payload; adjacent prefetch | Snapshot API, panel loaders, cache | M4-A06, M6-A07; bounded requests and invalidation | SEALED_FOR_REVIEWER_APPROVAL |
| M-D018 | Renderer owns explicit WebGL lifecycle | Current Three.js views allocate contexts/resources | Persistent hidden canvases | dispose/context-loss hooks | M4-A07, M6-A08; no artifact modules | SEALED_FOR_REVIEWER_APPROVAL |
| M-D019 | Artifact remains inert; Workspace has no execution authority | Existing security model prohibits browser/provider authority | Active HTML/SVG/URL/code artifacts | API/renderers/downloads | M1-A08, M7-A06; all security markers | SEALED_FOR_REVIEWER_APPROVAL |
| M-D020 | Preserve/project/read-only; never silently migrate science | Historical contracts and hashes are audit records | Auto-upgrade identity/plan/artifact | Compatibility adapters and typed state | M1-A07, M7-A03; exact historical hashes | SEALED_FOR_REVIEWER_APPROVAL |
| M-D021 | Keep PlannerWorkbench as entry, Workspace as persisted result | PlannerWorkbench already owns canonical analysis creation | Replace planner with Workspace editor | `/` plus explicit open command | M2-A01, M2-A05; no plan/runtime change | SEALED_FOR_REVIEWER_APPROVAL |
| M-D022 | Server state + append-only revisions; transient view in memory | Current state disappears on reload | localStorage authority; scientific snapshots | Workspace tables/PATCH/recovery; 129th save rejected | M6-A01, M6-A02; optimistic conflict and `REVISION_CAP_EXCEEDED` | SEALED_FOR_REVIEWER_APPROVAL |
| M-D023 | URL stores panel and bounded exact selection | Current URL has no recoverable state | Full Workspace JSON; artifact payload | query codec <=2,048 bytes | M2-A03, M3-A04; auth/stale rejection | SEALED_FOR_REVIEWER_APPROVAL |
| M-D024 | Preserve tombstone/stale source refs | Source deletion/version change must remain auditable | Cascade Workspace delete; remap latest | Status projection/read-only panels | M6-A03; no stale identity rebinding | SEALED_FOR_REVIEWER_APPROVAL |
| M-D025 | Execute M1 through M7 in sealed order | Contracts precede shell, selection, renderers, delivery, closure | Parallel architecture streams; one large phase | Seven reviewer-gated phases | M1-A01, M1-A02, M1-A03, M1-A04, M1-A05, M1-A06, M1-A07, M1-A08, M2-A01, M2-A02, M2-A03, M2-A04, M2-A05, M2-A06, M2-A07, M3-A01, M3-A02, M3-A03, M3-A04, M3-A05, M3-A06, M3-A07, M4-A01, M4-A02, M4-A03, M4-A04, M4-A05, M4-A06, M4-A07, M4-A08, M5-A01, M5-A02, M5-A03, M5-A04, M5-A05, M5-A06, M5-A07, M6-A01, M6-A02, M6-A03, M6-A04, M6-A05, M6-A06, M6-A07, M6-A08, M7-A01, M7-A02, M7-A03, M7-A04, M7-A05, M7-A06, M7-A07, M7-A08; exact-SHA lifecycle | SEALED_FOR_REVIEWER_APPROVAL |

<!-- phase10m7-acceptance-registry:start -->
## Canonical Phase 10M-7 Acceptance Registry

| ID | Canonical title | Canonical responsibility |
| --- | --- | --- |
| M7-A01 | Service-backed | PostgreSQL + Redis + MinIO full Workspace lifecycle, 0 skipped/failed |
| M7-A02 | Scientific integrity | Adapter -> Runtime -> Artifact -> renderer/evidence authority remains exact |
| M7-A03 | Historical compatibility | 0.1/0.2, modern/legacy/partial/missing-source cases retained |
| M7-A04 | Full tests | Backend/frontend/typecheck/build/lock/migration/closure all pass |
| M7-A05 | Browser | Chromium/Firefox/WebKit/mobile/accessibility/WebGL current evidence passes |
| M7-A06 | Security | All Workspace security markers and secret scan pass |
| M7-A07 | Evidence | Sanitized API/DOM/network/console/screenshots/performance manifest verifies |
| M7-A08 | Lifecycle | Implementation, completion, and verified queue archive exact-SHA CI pass |
<!-- phase10m7-acceptance-registry:end -->

## Stop conditions

Stop and return to the reviewer for: a required scientific identity absent from current authority; migration conflict with a newer head; authorization model unable to protect source refs; need to modify Intent/Plan/Runtime/Artifact semantics; need for active artifact content; phase overlap that changes a sealed decision; or Phase 10N scientific expansion.

No Phase 10M phase starts automatically. Phase 10N remains outside this lock.
