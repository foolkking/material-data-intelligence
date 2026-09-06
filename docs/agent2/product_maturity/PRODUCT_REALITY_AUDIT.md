# Product Reality Audit — 2026-09-01

This is the current evidence-led audit for the continuing Product Maturity
Closure task. It records observed runtime behavior, not historical claims.

## Runtime truth

The retained same-stack runtime is healthy:

| Service | Endpoint/process | Observed state |
| --- | --- | --- |
| Frontend | `http://127.0.0.1:3013` | listening, production Next build |
| API | `http://127.0.0.1:8005` | listening, current worktree |
| PostgreSQL | `127.0.0.1:55434/mdi` | connected; Alembic head `0029_product_maturity_platform_roles` |
| Redis | `127.0.0.1:6379/13` | connected |
| MinIO | `127.0.0.1:9000`, bucket `mdi-artifacts` | connected |
| Workers | Redis-backed worker set | running |
| LLM | DeepSeek server-managed configuration | configured |

`GET /health/runtime` reports PostgreSQL, Redis, MinIO, Redis worker and a
configured DeepSeek provider. No service was stopped during this audit.

## User-visible observations

### PASS

- Data Platform dataset table renders real rows, typed columns and stable
  `sample_id` values.
- Current scientific reports open through the normal project route and expose
  findings, methods, figures, tables, exact source version and artifact links.
- Task Center now loads through one authorized bounded feed request rather than
  enumerating every project from the browser.
- Global search does not issue an unbounded empty query; it waits for a query or
  explicit filter.
- Mobile project navigation retains a visible project identity row.
- Ordinary researchers see server-managed model configuration as read-only;
  mutation authority is restricted to `PLATFORM_ADMIN` on the server and in UI.
- Authenticated users now have a bounded `/account` User Center reachable from
  the account menu. It reuses `/auth/me`, displays the authenticated identity
  and effective platform/project roles, and provides normal links back to
  Projects, Notifications and Trash without exposing secrets or internal
  session tokens.
- Research historical loading uses a monotonic “reading persisted result” state
  instead of publishing a false empty-result state during resolution.
- Browser audit recorded zero duplicate IDs, broken ARIA references and global
  overflow on the sampled desktop/mobile routes.

### PARTIAL / bounded unavailable data

- Two legacy synthetic qualification Artifact references have no recoverable
  exact bytes in the retained repository, active object storage or preserved
  evidence. These records are outside the acceptance user's visible scientific
  scope and remain fail-closed; they do not substitute another version or
  fabricate content.
- The previously reported acceptance Dataset payload gap is closed by exact
  byte/checksum/parser identity recovery. Its normal object-store route now
  renders the persisted row and stable sample identity.
- Legacy seeded jobs with no persisted result remain historical metadata-only
  records. They are visible in Task Center and can be opened for status/history,
  but cannot display scientific payload that was never persisted.
- A legacy report probe may return a typed 404 before the canonical report
  fallback succeeds. This is an expected compatibility probe, not an internal
  server error; the canonical report routes tested in this audit load normally.

## Authorization boundary

`users.platform_role` is now an explicit persisted authority with values
`USER` and `PLATFORM_ADMIN`. Existing users default to `USER`. Project
ownership or membership does not grant platform-administrator authority.
Provider configure, model-group update and delete routes fail closed with
`403 PLATFORM_ADMIN_REQUIRED` for ordinary users. Provider list/status/resolve/
test remain readable where authorized.

## Focused verification

- Frontend Model Settings/ProductShell: `22 passed`.
- Backend provider/platform-role/workspace/migration tests: `26 passed`.
- Frontend production `typecheck`: PASS.
- Frontend production build: PASS.
- `git diff --check`: PASS.
- Live browser Data Platform, Task Center, Report and Model Settings routes:
  loaded successfully against the current same-stack runtime.
- User Center and shared route-frame tests: `6 passed`.

## Next product-maturity work

The next batch must continue the global product work: explicit User Center and
administrator surfaces, account lifecycle/audit semantics, route continuity,
and a second desktop/mobile browser sweep. Missing exact historical bytes remain
an evidence/data-retention limitation rather than a safe implementation target.

## 2026-09-01 accessibility regression closure

The validated scientific table scroll region now exposes a stable accessible
name (`已验证的数据表，可横向滚动查看完整列`) and links the mobile/sample
identity guidance through a per-instance `aria-describedby` target generated
with `useId`. This keeps repeated table renderers addressable without duplicate
DOM ids or unstable role names.

Current verification:

- ScientificWorkspaceShell focused: `29 passed`.
- Full frontend: `108 files / 787 tests passed`.
- Product-maturity backend/data projection subset: `13 passed`.
- TypeScript typecheck, production build, API compileall and `git diff --check`:
  `PASS`.
- `/health/runtime`: PostgreSQL, Redis, MinIO, Redis-backed worker and
  configured DeepSeek provider all `ok`.

The umbrella Product Maturity Closure remains in progress; this entry closes
the current accessibility regression only.

## 2026-09-02 report scientific payload readability

Current same-stack authenticated report verification found that modern reports
could open persisted Figure/Table links but initially presented only a
description plate in the report body. This was a presentation usability gap,
not a storage outage. The report reader now provides an explicit on-demand
read-only preview backed by the existing Artifact content endpoint:

- Figure: deterministic SVG projection of finite persisted series.
- Table: bounded preview of at most 24 rows and 8 columns with researcher-readable
  labels (`配位数`, `元素`, `邻居距离 (Å)`, etc.), while raw keys remain in
  the column title and the full Artifact link remains available.
- Failed payload reads remain visible as a typed error; no scientific success
  is fabricated and no Job/ToolCall/Artifact/ScientificResult is created.

Current verification on report
`agent2_report_19a0d0c261c28577101de81532464893`:

```text
Figure preview = 2 finite persisted points
Table preview = 1 persisted row / 8 typed columns
browser error/warn = 0
ScientificReportArtifactPreview tests = 3 passed
ScientificReportRoute tests = 23 passed
frontend full regression = 109 files / 792 tests passed
typecheck/build = PASS
```
## 2026-09-02 — Viewer recovery and repeated-instance accessibility

The exact-version Scientific Object Viewer now exposes retry/source navigation
for unavailable payloads, and repeated Viewer shells use unique limitation
heading IDs. These are presentation-only recovery and accessibility bridges:
they preserve the authoritative object/version and do not create scientific
execution records.
