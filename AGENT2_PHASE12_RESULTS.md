# Agent-2.0 Phase 12 — Scientific Data Platform 2.0

## Release closure

```text
FUNCTIONAL_PHASE12_CLOSURE = PASS
AGENT2_PHASE12 = COMPLETE
SCIENTIFIC_DATA_PLATFORM_V2 = COMPLETE
READY_FOR_PHASE13 = YES
PHASE13_MAIN_IMPLEMENTATION = NOT_STARTED
```

P12-A implementation commit:

```text
1ccf20811e4e600e140f154ee919d531c7cc9bbf
```

P12-A exact-SHA CI:

```text
run = 32957756692
tested SHA = 1ccf20811e4e600e140f154ee919d531c7cc9bbf
result = PASS
```

Required CI jobs passed:

- Unit Tests (Python 3.11)
- Frontend Typecheck & Build
- PostgreSQL/Redis/MinIO Service-backed Integration
- Phase 11-3 Scientific Replay (Linux)
- Phase 11-3 Scientific Replay (Windows)

The P12-B SHA is the commit containing this completion record; it is
intentionally not embedded here to avoid a self-referential commit hash.

## Final archive discovery UI closure (2026-08-27)

The existing exact Scientific Object Viewer action remains the lifecycle
mutation authority and uses `PATCH /api/scientific-objects/{object_id}` with
project-write authorization. The Data Platform list now requests
`lifecycle_status=ACTIVE` for normal discovery and
`lifecycle_status=ARCHIVED` for the archived view. An explicitly addressed
`object`/`version` route intentionally omits the filter so authorized
historical Results and Viewers remain resolvable while archived.

Authenticated Chromium verified ACTIVE → ARCHIVED → ACTIVE on the canonical
Structure/data object. ScientificObject identity, current version, version
count, and historical exact-version Viewer resolution were unchanged. Archive
and restore created no ScientificObjectVersion. P12-A UI closure commit:

```text
40ebb4d65c76ef0c44fdde2923c901c97efa2257
```

Exact-SHA CI:

```text
run = 33038096797
tested SHA = 40ebb4d65c76ef0c44fdde2923c901c97efa2257
result = PASS
```

## Data authority

`ScientificObject` remains the logical scientific identity and
`ScientificObjectVersion` remains immutable scientific state. PostgreSQL is
the authority for identities, exact versions, profiles, relationships,
lifecycle state, and result source references; MinIO stores bytes and
artifacts; Redis is transient queue/cache infrastructure.

The production re-ingestion bridge is:

```text
POST /api/scientific-objects/{object_id}/versions
→ Dataset/resource ingestion
→ MinIO
→ parser
→ Profile 2.1
→ ScientificObjectService.create_version_from_dataset_resource
→ immutable version + atomic current-version advancement
```

No duplicate authority or in-place scientific mutation was introduced.
Historical references never substitute the latest version.

## Canonical lifecycle evidence

- Structure object: `773089f9-3ce8-4645-92dd-2f62c64cba89`
- v1: `65f56d10-008d-445d-ab2f-228aebf1835b`
- production v2: `2538cd12-ffd5-473f-8c77-69e6d1700243`
- historical Results/Viewers remain exact-v1; new work resolves exact-v2
- `SYSTEM_FIXTURE_FINAL_V2 = NO`
- `SILENT_LATEST_SUBSTITUTION = NO`

Authenticated Structure and Dataset research paths completed through
Plan → Job → ToolCall → Artifact → ScientificResult → grounded
interpretation → terminal Turn. Dataset projector facts are authoritative;
unsupported numeric claims remain rejected by grounding validation.

Archive/restore browser proof completed:

```text
ACTIVE → ARCHIVED → ACTIVE
version count = 3 → 3
current version unchanged
historical v1 Viewer remains addressable while archived
ARCHIVE_CREATED_VERSION = NO
RESTORE_CREATED_VERSION = NO
```

## Qualification

- Backend: `1808 passed, 83 skipped`
- Frontend: `90 files, 582 tests passed`
- Typecheck: PASS
- Production build: PASS
- Compileall: PASS
- `uv lock --check`: PASS
- `git diff --check`: PASS
- Touched Ruff: PASS
- Mandatory PostgreSQL/Redis/MinIO service campaign: selected `19`,
  passed `19`, failed `0`, errors `0`, skipped `0`
- DB pool evidence: active `1`, idle `6`, idle-in-transaction `0`,
  pool timeouts `0`

## Preserved user-owned files

Legacy and unrelated worktree files were intentionally excluded from P12-A
and remain preserved, including `AGENT2_PHASE6_RESULTS.md`, `AGENTS.md`,
`TASKS.md`, `CODEX_HANDOFF.md`, `docs/agent2.zip`,
`.phase12_upload_result.json`, `artifacts_phase13_preflight.png`,
`phase13_logged_in_home.png`, `docs/phase12/evidence/**`, and other
pre-existing modifications.

Phase 13 implementation was not started in the Phase 12 closure commit.
