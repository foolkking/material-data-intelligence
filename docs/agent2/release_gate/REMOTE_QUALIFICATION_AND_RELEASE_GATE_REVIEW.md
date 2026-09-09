# Remote Qualification and Release Gate Review

Date: 2026-09-09  
Mode: exact-SHA local/service qualification with remote push prohibited

## 1. Decision

```text
REMOTE_QUALIFICATION_AND_RELEASE_GATE_REVIEW = CONDITIONAL
LOCAL_AND_SERVICE_QUALIFICATION = PASS
RELEASE_READY_LOCAL = YES
RELEASE_READY = NO

REMOTE_PUSH_REQUIRED = YES
REMOTE_PUSH_AUTHORIZATION_REQUIRED = YES
REMOTE_CI_STATUS = NOT_RUN
```

The source/physical architecture migration, capability-parity audit, and
residual-ownership review remain closed. The only unsatisfied release gate is
exact-SHA remote availability and GitHub Actions qualification. No push was
authorized or performed.

The source candidate qualified by the product, service, browser, build, and
static checks below is `0b8167b329f2b7c3e27cb49e527d498fb9730e56`.
The documentation/state closeout commit that contains this record becomes the
final release-candidate SHA. It must be re-resolved from `git rev-parse HEAD`
and used for the final local runtime marker checks and any later remote CI.
This avoids a self-referential commit-hash loop without allowing an older SHA
to stand in for the final release candidate.

## 2. Evidence Reconciliation

The previously reported focused-test totals describe different scopes:

```text
OWNERSHIP_SPECIFIC_TESTS = 25 passed
TOTAL_FOCUSED_RESIDUAL_REVIEW_TESTS = 57 passed
```

The 25-test set covers ownership-specific queue/worker behavior. The 57-test
total is the expanded residual-review set that also includes architecture and
compatibility-focused suites. Neither result supersedes the other.

## 3. Local Release Preflight

```text
git diff --check = PASS
architecture guard = PASS
cycles = 0
forbidden edges = 0
canonical -> compatibility edges = 0
allowlisted frozen edges = 4
dynamic contract errors = 0
public surface errors = 0
handlers = 6/6
queues = 6 unchanged
tools = 62
adapters = 50
focused release/identity tests = PASS
```

The four allowlisted edges are the accepted provider/research/LLM integration
boundaries. No migration- or release-specific exception was added.

## 4. Bounded Release Repairs

Three cohesive fix-forward commits were required during qualification:

| Commit | Purpose |
|---|---|
| `0f3f835` | Restore all six worker launches in the retained same-stack startup path and align quick-start instructions with the current topology. |
| `e58720d` | Make Windows service qualification validate process identity without assuming operating-system PID non-reuse. |
| `0b8167b` | Build the production frontend with its explicit API proxy target and release SHA, verify that proxy through the stack preflight, and stabilize generated Next TypeScript paths across Windows/POSIX forms. |

These changes affect release startup/configuration and qualification only.
They do not change API, authorization, schema/Alembic, transaction, persisted
identity, queue/handler, Tool/Adapter, scientific, or UI semantics.

## 5. PostgreSQL Qualification

A qualification-owned PostgreSQL 17.10 instance was used on
`127.0.0.1:55434`; the unrelated local PostgreSQL listener on port 5432 was
not changed.

```text
connection = PASS
pool lifecycle = PASS
migration head = 0032_provider_connections
expected migration head = 0032_provider_connections
schema identity = PASS
repository read/write = PASS
transaction rollback = PASS
DATABASE_MIGRATION_HEAD = PASS
```

The service-backed campaign used a fresh qualification database. No user or
forensic database was reset or migrated.

## 6. Redis and Worker Qualification

The retained Redis-compatible service was used through an isolated
qualification database for the full campaign and database 13 for the managed
same-stack runtime.

```text
Redis connectivity = PASS
queue names = 6 unchanged
persisted handler resolution = 6/6
live worker registration = 6/6
registered worker state = healthy/idle
queue depth at closeout observation = 0
LIVE_WORKER_REGISTRATION = PASS
```

No queue was flushed and no persisted job was migrated or deleted.

## 7. MinIO Qualification

A qualification-owned bucket and uniquely named disposable object were used.

```text
connectivity = PASS
bucket access = PASS
put/get/delete qualification object = PASS
Artifact locator/read behavior = PASS
MINIO_QUALIFICATION = PASS
```

No user object was deleted or overwritten.

## 8. Service-Backed Critical Path

The mandatory real-service suite completed:

```text
selected = 74
passed = 74
failed = 0
errors = 0
skipped = 0
deselected = 14
```

It exercised real PostgreSQL, Redis, MinIO, and subprocess workers across:

```text
Project -> Dataset/Data -> Research/Planning -> Job/Tool execution
-> Artifact -> ScientificResult -> Interpretation -> Report
-> Workspace/reopen
```

Stable IDs, exact-version ScientificObject behavior, Artifact locator
grounding, Result provenance, Report grounding, queue dispatch, worker
completion, rollback, and reopen/reuse paths passed.

## 9. Authenticated Browser Runtime

A bounded authenticated Chromium smoke used the existing Playwright runtime
and qualification-owned account/project data. The repository was not given a
new browser-test dependency.

```text
login = PASS
real frontend API proxy = PASS
persisted project ID reopen = PASS
fatal page errors = 0
server response errors = 0
chunk/import failures = 0
AUTHENTICATED_BROWSER_RUNTIME_PARITY = PASS
```

Rendered routes:

- `/projects`
- `/projects/<qualification-project-id>`
- `/projects/<qualification-project-id>/data`
- `/projects/<qualification-project-id>/research`
- `/projects/<qualification-project-id>/reports`
- `/tasks`
- `/notifications`

The pre-authentication 401 and navigation-cancelled React Server Component
prefetches were expected and non-fatal. Browser upload was not claimed by this
bounded smoke; Dataset ingestion and the release-critical data path are covered
by the 74-test real-service campaign.

## 10. Regression and Build State

```text
backend accepted broad baseline = 2212 passed, 76 failed, 75 skipped
new backend regressions = 0
mandatory service suite = PASS
frontend unit tests = 117 files / 950 tests PASS
frontend typecheck = PASS
production build = PASS
static asset route check = PASS
uv lock --check = PASS
PowerShell parse = PASS
```

The broad backend suite was not repeated after release-startup-only fixes.
The 76 accepted failures remain historical/environmental baseline failures;
focused and mandatory real-service checks found no new regression.

## 11. Supply Chain and Provenance

```text
dependency lock state = PASS
GitHub Actions references = commit pinned
PostgreSQL/Redis/MinIO CI images = digest pinned
provenance lock agreement = PASS
runtime configuration validation = PASS
secret redaction = PASS
release SHA exposure = PASS after exact-SHA production build/runtime rotation
```

No secret value is stored in this record.

## 12. Remote Exact-SHA Gate

The GitHub remote, workflows, and authenticated `gh` CLI are available.
The final local release candidate is not present on the remote because push
authorization was explicitly withheld.

```text
REMOTE_CONTAINS_EXACT_SHA = NO
REMOTE_CI_STATUS = NOT_RUN
REMOTE_CI_SHA = NONE
REMOTE_PUSH_REQUIRED = YES
REMOTE_PUSH_AUTHORIZATION_REQUIRED = YES
```

The minimum future action is a separately authorized push that makes the exact
final release-candidate SHA reachable on the configured remote, followed by the
existing CI workflow on that same SHA. A result for any older SHA is not
release qualification.

## 13. Final Classification

```text
SOURCE_ARCHITECTURE_MIGRATION_COMPLETE = YES
PHYSICAL_OWNERSHIP_MIGRATION_COMPLETE = YES
FULL_PRE_POST_CAPABILITY_PARITY = YES
MIGRATION_PHASE = CLOSED

LOCAL_RELEASE_PREFLIGHT = PASS
POSTGRES_QUALIFICATION = PASS
DATABASE_MIGRATION_HEAD = PASS
REDIS_QUALIFICATION = PASS
LIVE_WORKER_REGISTRATION = PASS
MINIO_QUALIFICATION = PASS
SERVICE_BACKED_CRITICAL_PATH = PASS
AUTHENTICATED_BROWSER_RUNTIME_PARITY = PASS
BACKEND_REGRESSION_STATUS = PASS
FRONTEND_TESTS = PASS
FRONTEND_TYPECHECK = PASS
PRODUCTION_BUILD = PASS

NEW_RELEASE_BLOCKERS = 1
UNRESOLVED_RUNTIME_BLOCKERS = 0
```

The one release blocker is procedural and remote: the final exact SHA has not
been pushed and therefore cannot yet receive exact-SHA remote CI. It is not a
migration, product-capability, or local-runtime defect.
