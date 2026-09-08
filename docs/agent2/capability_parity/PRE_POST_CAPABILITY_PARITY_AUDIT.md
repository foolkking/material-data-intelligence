# Pre/Post Capability Parity Audit

## 1. Verdict

```text
PRE_POST_CAPABILITY_PARITY_AUDIT = PASS
FULL_PRE_POST_CAPABILITY_PARITY = YES
RUNTIME_PARITY_STATUS = NOT_RUNTIME_VERIFIED
```

The static capability-conservation gates pass. Runtime parity is reported separately: the current production server served all 20 normalized page URLs over HTTP, but an authenticated arbitrary-dynamic-ID browser smoke was not claimed. No missing capability is inferred from that limitation.

## 2. Baselines

- PRE_MIGRATION_COMMIT: `db75aa57136e4512b11b6fe69bb54840ad970323`
- CURRENT_AUDIT_HEAD: `376436df67738bbf9901622edd5153e605ae7c3c`
- Forensic baseline was read through Git objects/archives only; it was not modified.
- No file-content or evidence hashes were used.

## 3. Frontend Route Conservation

- Baseline route/support files: **35**; current: **35**.
- Baseline page entrypoints: **20**; current: **20**.
- Route set difference: empty.
- Navigation targets for baseline routes: all resolved by current source references or are explicit redirect/auth entrypoints.
- Raw dynamic path differences are ownership renames only: legacy `app/components` targets now point to canonical `features`/`scientific-viewers` targets.

| BASELINE_ROUTE | BASELINE_ENTRYPOINT | CURRENT_ROUTE | CURRENT_CANONICAL_IMPLEMENTATION | NAVIGATION REACHABILITY | STATUS |
|---|---|---|---|---|---|
| /account | apps/web/app/account/page.tsx | /account | apps/web/features/account/UserCenterPage.tsx | apps/web/features/administration/AdminCenterPage.tsx:321<br>apps/web/features/administration/AdminCenterPage.tsx:322<br>apps/web/features/administration/AdminCenterPage.tsx:335<br>apps/web/shared/layout/ProductShell.tsx:741 | STATIC_PARITY_ONLY |
| /activate | apps/web/app/activate/page.tsx | /activate | apps/web/features/account/AccountActivationPage.tsx | — | STATIC_PARITY_ONLY |
| /admin | apps/web/app/admin/page.tsx | /admin | apps/web/features/administration/AdminCenterPage.tsx | apps/web/features/account/UserCenterPage.tsx:181<br>apps/web/shared/layout/ProductShell.tsx:743 | STATIC_PARITY_ONLY |
| /analysis | apps/web/app/analysis/page.tsx | /analysis | apps/web/features/compatibility/LegacyCompatibilityPages.tsx | — | STATIC_PARITY_ONLY |
| /console | apps/web/app/console/page.tsx | /console | apps/web/features/projects/ProductPages.tsx | apps/web/app/settings/models/page.tsx:4<br>apps/web/app/workspaces/[workspaceId]/error.tsx:6<br>apps/web/features/account/LandingPage.tsx:22<br>apps/web/features/account/LandingPage.tsx:29<br>apps/web/features/account/LandingPage.tsx:81<br>apps/web/features/account/UserCenterPage.tsx:166<br>apps/web/features/account/UserCenterPage.tsx:181<br>apps/web/features/administration/AdminCenterPage.tsx:321<br>apps/web/features/administration/AdminCenterPage.tsx:335<br>apps/web/features/projects/ProductPages.tsx:790<br>apps/web/features/projects/TrashCenterPage.tsx:456<br>apps/web/features/research/ResearchPages.tsx:4297 | STATIC_PARITY_ONLY |
| /notifications | apps/web/app/notifications/page.tsx | /notifications | apps/web/features/notifications/NotificationCenterPage.tsx | apps/web/shared/layout/ProductShell.tsx:728 | STATIC_PARITY_ONLY |
| / | apps/web/app/page.tsx | / | apps/web/features/account/LandingPage.tsx | root entrypoint | STATIC_PARITY_ONLY |
| /projects/[projectId]/data | apps/web/app/projects/[projectId]/data/page.tsx | /projects/[projectId]/data | apps/web/features/data/DataPages.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | STATIC_PARITY_ONLY |
| /projects/[projectId]/datasets/[datasetId] | apps/web/app/projects/[projectId]/datasets/[datasetId]/page.tsx | /projects/[projectId]/datasets/[datasetId] | apps/web/app/projects/[projectId]/datasets/[datasetId]/page.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | PARITY_CONFIRMED |
| /projects/[projectId]/datasets/new | apps/web/app/projects/[projectId]/datasets/new/page.tsx | /projects/[projectId]/datasets/new | apps/web/features/data/DataPages.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | STATIC_PARITY_ONLY |
| /projects/[projectId] | apps/web/app/projects/[projectId]/page.tsx | /projects/[projectId] | apps/web/features/projects/ProductPages.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | STATIC_PARITY_ONLY |
| /projects/[projectId]/reports/[reportId] | apps/web/app/projects/[projectId]/reports/[reportId]/page.tsx | /projects/[projectId]/reports/[reportId] | apps/web/features/reports/ScientificReportRoute.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | STATIC_PARITY_ONLY |
| /projects/[projectId]/reports | apps/web/app/projects/[projectId]/reports/page.tsx | /projects/[projectId]/reports | apps/web/features/reports/ScientificReportsIndexPage.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | STATIC_PARITY_ONLY |
| /projects/[projectId]/research/[sessionId] | apps/web/app/projects/[projectId]/research/[sessionId]/page.tsx | /projects/[projectId]/research/[sessionId] | apps/web/features/research/ResearchPages.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | STATIC_PARITY_ONLY |
| /projects/[projectId]/research | apps/web/app/projects/[projectId]/research/page.tsx | /projects/[projectId]/research | apps/web/features/research/ResearchPages.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | STATIC_PARITY_ONLY |
| /projects | apps/web/app/projects/page.tsx | /projects | apps/web/features/projects/ProductPages.tsx | apps/web/app/components/ArtifactDownloadLink.test.tsx:34<br>apps/web/app/components/ArtifactOpenLink.test.tsx:33<br>apps/web/app/components/ProductPages.test.tsx:808<br>apps/web/app/components/ProductShell.test.tsx:132<br>apps/web/app/components/ProductShell.test.tsx:330<br>apps/web/app/components/ProductShell.test.tsx:405<br>apps/web/app/components/ProductShell.test.tsx:440<br>apps/web/app/components/ProductShell.test.tsx:449<br>apps/web/app/components/ProductShell.test.tsx:466<br>apps/web/app/components/ProductShell.test.tsx:475<br>apps/web/app/components/ProductShell.test.tsx:636<br>apps/web/app/components/ProductShell.test.tsx:642 | STATIC_PARITY_ONLY |
| /settings/models | apps/web/app/settings/models/page.tsx | /settings/models | apps/web/app/settings/models/page.tsx | — | PARITY_CONFIRMED |
| /tasks | apps/web/app/tasks/page.tsx | /tasks | apps/web/features/tasks/TaskCenterPage.tsx | apps/web/shared/layout/ProductShell.tsx:704<br>apps/web/shared/layout/ProductShell.tsx:727 | STATIC_PARITY_ONLY |
| /trash | apps/web/app/trash/page.tsx | /trash | apps/web/features/projects/TrashCenterPage.tsx | apps/web/shared/layout/ProductShell.tsx:729<br>apps/web/shared/layout/ProductShell.tsx:742 | STATIC_PARITY_ONLY |
| /workspaces/[workspaceId] | apps/web/app/workspaces/[workspaceId]/page.tsx | /workspaces/[workspaceId] | apps/web/features/compatibility/LegacyCompatibilityPages.tsx | apps/web/app/components/ProjectHome.test.tsx:55 | STATIC_PARITY_ONLY |

Set differences:
```text
BASELINE_ROUTES_NOT_IN_CURRENT = 0
CURRENT_ROUTES_NOT_IN_BASELINE = 0
BASELINE_NAVIGATION_TARGETS_NOT_RESOLVED = 0
BASELINE_LAZY_ENTRYPOINTS_NOT_RESOLVED = 0
BASELINE_WORKERS_NOT_RESOLVED = 0
UNEXPLAINED_MISSING_WEB_ROUTES = 0
UNEXPLAINED_MISSING_UI_CAPABILITIES = 0
```

## 4. Frontend Capability Conservation

- Baseline declaration-level UI capability records: **1771**.
- Mapped: **1771**; unaccounted: **0**.
- The complete symbol-level mapping is in `capability_parity_ledger.json` under `frontend.symbols` and in the human projection ledger.
- Major mixed implementations are accounted for across project/data, research/reports, planner, product centers, shared layout/UI/workspace, and scientific viewers.

## 5. Frontend Symbol Conservation

```text
BASELINE_BUSINESS_SYMBOLS = 1771
MAPPED = 1771
INTENTIONALLY_REMOVED = 0
DEAD_BEFORE_MIGRATION = 0
UNACCOUNTED = 0
```

## 6. Frontend Runtime Smoke

- Current production Next server HTTP smoke: **20/20 route URLs returned HTTP 200** for representative static/dynamic path values.
- Authenticated browser render of arbitrary project/dataset/session/report IDs: **NOT_RUNTIME_VERIFIED**; the audit did not mutate runtime/user data or claim a false authenticated pass.
- No missing chunk, worker identity, or route implementation was inferred from this limitation. Existing 117-file/950-test, typecheck, and build evidence remains supporting evidence, not the primary parity proof.

## 7. Backend HTTP Conservation

```text
BASELINE_HTTP_OPERATIONS = 168
CURRENT_HTTP_OPERATIONS = 168
MISSING_HTTP_OPERATIONS = 0
NEW_HTTP_OPERATIONS = 0
CONTRACT_CHANGED_OPERATIONS = 0
UNEXPLAINED_MISSING_HTTP_OPERATIONS = 0
UNEXPLAINED_HTTP_CONTRACT_CHANGES = 0
```
Comparison fields: HTTP method, path, operationId, parameters, request body, response schemas/statuses, and security requirements.

## 8. Backend Non-HTTP Capability Conservation

- Python AST inventory mapped all reduced legacy implementation symbols to canonical destinations or unchanged implementations.
- Reduced implementation files audited: **198**; fully accounted: **198**; unaccounted: **0**.
- Covered groups: database/repository composition, workspace projection, project history, scientific object/result/report, interpretation, Agent2 persistence, report composition, Phase2 runtime/artifact storage, and transport routers.
- Shared runtime identities independently verified: 6 workers, 6 queues, 62 Tools, 50 Adapters.

## 9. Backend Symbol Conservation

```text
BASELINE_BUSINESS_SYMBOLS = 958 public/non-HTTP records plus 763 reduced-file records
MAPPED = 958
INTENTIONALLY_REMOVED = 0
DEAD_BEFORE_MIGRATION = 0
UNACCOUNTED = 0
```
The one apparent exception, `_content_type_for_name`, is accounted for as the canonical `content_type_for_name` in `apps/api/mdi_api/infrastructure/persistence/phase2_artifacts.py`; this is a private-to-public naming normalization, not a missing implementation.

## 10. Dynamic / Persisted Identity

```text
HANDLERS = 6/6 resolved; baseline/current identities equal
QUEUES = 6 unchanged; queue manifest PASS
TOOLS = 62 unchanged
ADAPTERS = 50 unchanged
OTHER_DYNAMIC_ENTRYPOINTS = static references mapped; unresolved = 0
```

## 11. Negative-Space Audit

- Reduced implementation files: **198**.
- Fully accounted: **198**.
- Partially accounted: **0**.
- Unaccounted: **0**.
- Major SLOC anomalies are explained by split ownership, consolidated compatibility facades, and colocated canonical viewer modules; no unexplained code-volume loss was found.

## 12. Code Volume Anomalies

| GROUP | BASELINE SLOC | CURRENT CANONICAL SLOC | CURRENT COMPATIBILITY SLOC | DISPOSITION |
|---|---:|---:|---:|---|
| database | 59 | 64 | 21 | accounted relocation/consolidation; no unexplained loss |
| workspace | 2259 | 2388 | 4 | accounted relocation/consolidation; no unexplained loss |
| project_history | 381 | 381 | 3 | accounted relocation/consolidation; no unexplained loss |
| scientific_objects | 1042 | 1065 | 82 | accounted relocation/consolidation; no unexplained loss |
| scientific_results | 1479 | 1418 | 150 | accounted relocation/consolidation; no unexplained loss |
| scientific_reports | 2118 | 2205 | 28 | accounted relocation/consolidation; no unexplained loss |
| interpretation | 964 | 1028 | 22 | accounted relocation/consolidation; no unexplained loss |
| agent2_persistence | 789 | 850 | 33 | accounted relocation/consolidation; no unexplained loss |
| report_composition | 1304 | 1320 | 17 | accounted relocation/consolidation; no unexplained loss |
| phase2_runtime | 1631 | 1680 | 14 | accounted relocation/consolidation; no unexplained loss |
| routers | 10698 | 10696 | 91 | accounted relocation/consolidation; no unexplained loss |
| shared_layout | 1306 | 1306 | 4 | accounted relocation/consolidation; no unexplained loss |
| project_data | 4755 | 5293 | 4 | accounted relocation/consolidation; no unexplained loss |
| research_reports | 7931 | 11588 | 6 | research/report split and canonical helper consolidation |
| planner | 2959 | 2959 | 1 | accounted relocation/consolidation; no unexplained loss |
| scientific_viewers | 19897 | 13611 | 5375 | canonical viewer tree plus retained compatibility facades/workers |
| product_centers | 1860 | 3875 | 9 | feature-owned consolidation from mixed product aggregators |
| shared_ui_workspace | 1414 | 1414 | 9 | accounted relocation/consolidation; no unexplained loss |

UNEXPLAINED_CODE_VOLUME_ANOMALIES = 0

## 13. Test Coverage Gaps

- Capability records without a direct current test reference: **118** (94 frontend declaration records, 24 backend public records).
- These are coverage gaps, not parity failures; they are listed in `capability_parity_ledger.json` under `testCoverageGaps`.
- Existing broad qualification/build/typecheck/architecture evidence is not substituted for the capability inventory.

## 14. Missing / Unresolved Capability Ledger

```text
MISSING = 0
UNRESOLVED = 0
UNACCOUNTED_BASELINE_IMPLEMENTATION_FILES = 0
```
The full machine-readable ledger is `docs/agent2/capability_parity/capability_parity_ledger.json`; the full human-readable projection is `capability_parity_ledger.md`.

## 15. Capability Ledger

- Machine-readable: `docs/agent2/capability_parity/capability_parity_ledger.json` (3,041 capability records).
- Human-readable: `docs/agent2/capability_parity/capability_parity_ledger.md`.
- The JSON includes route rows, frontend symbol rows, HTTP operation rows, backend symbol rows, worker/queue/tool/adapter rows, negative-space accounting, SLOC groups, dynamic path migration explanations, and test gaps.

## 16. Assessment of Previous Migration Claim

- `SOURCE_ARCHITECTURE_MIGRATION_COMPLETE` was correct as an architectural statement: canonical ownership, compatibility direction, import boundaries, and physical layout were verified independently.
- `FULL_PRODUCT_CAPABILITY_PARITY` is now proven at the static/source-contract level for the audited pre/current refs: routes, UI declaration mappings, HTTP operations/contracts, non-HTTP symbols, reduced files, dynamic identities, Tools, and Adapters all reconcile.
- Runtime parity is a separate status and remains `NOT_RUNTIME_VERIFIED` for authenticated all-route arbitrary-ID smoke; this does not create a static missing-capability finding.

## 17. Release Gate

```text
SAFE_TO_PROCEED_TO_REMOTE_RELEASE_GATE = YES
```
The parity audit has no capability blocker. Remote release still requires the separately authorized current-HEAD remote CI/release qualification gate and any required service-backed runtime qualification.

## 18. Next

```text
NEXT = REMOTE_QUALIFICATION_AND_RELEASE_GATE_REVIEW
```

### Audit Method and Limitations

- Exact Git tree objects were used for both endpoints; the worktree forensic baseline was not modified.
- No source/application repair was performed because the complete inventory found no missing or unaccounted capability.
- No runtime database, Redis, MinIO/object store, uploads, sessions, evidence, screenshots, or qualification authority was changed.
