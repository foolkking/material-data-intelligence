# Scientific Payload Availability UX Audit

Date: 2026-09-01
Platform: authenticated scientific web application
Primary audience: materials researchers and project collaborators
Trust level: high; scientific identity, version, and provenance must remain exact

## Scope and evidence

This audit covers the scientific content paths shown by users as:

- `Internal Server Error` while opening persisted Artifact content;
- `当前解析资源暂时无法读取`;
- `原始来源当前不可访问`;
- metadata-only Viewer state with no interactive payload.

Evidence inspected:

- live same-stack runtime diagnostics;
- API request/error logs;
- PostgreSQL Artifact and scientific-version storage references;
- active MinIO storage;
- preserved repository-owned historical MinIO qualification storage;
- existing Viewer, Artifact content, and frontend fallback implementations.

The runtime itself is healthy:

```text
PostgreSQL = running
Redis = running
MinIO = running
API = running
worker = Redis-backed
frontend = running
```

The defect is storage continuity and error-boundary behavior, not a stopped
service.

## Executive summary

The current product correctly preserves metadata and exact version identity when
source bytes are unavailable. It does not silently replace a missing historical
source with a newer version. That is scientifically correct.

However, two product-quality failures remain:

1. persisted PostgreSQL references point to payloads absent from the currently
   active MinIO data directory even though exact copies exist in preserved
   repository-owned MinIO qualification storage;
2. the authenticated Artifact content endpoint allows MinIO `NoSuchKey` to
   escape as HTTP 500 instead of returning a bounded, typed unavailable state.

The recovery strategy is:

```text
exact PostgreSQL reference
→ locate the identical historical object key
→ verify size and SHA-256
→ restore the exact bytes to the active bucket
→ retain object/version/Artifact identity unchanged
```

No scientific payload may be fabricated, regenerated, or replaced with a newer
version.

## Findings

### F1 — Blocker — Active storage is incomplete relative to authoritative references

Category: Data/state continuity
Confidence: high

API logs show repeated MinIO `NoSuchKey` failures for persisted Artifact keys.
The corresponding exact job/object directories exist in the preserved
`.phase14r-minio-single4` storage but not in active `.phase13-minio-data2`.

Impact:

- real scientific Artifacts cannot open;
- Figure/Table/Viewer content can appear unavailable;
- researchers cannot inspect persisted scientific work despite intact metadata.

Remediation:

- run a complete PostgreSQL-reference-to-MinIO inventory;
- restore only byte-identical objects whose key, size, SHA-256, project, job,
  and Artifact identity match;
- record all restored and unresolved references.

### F2 — High — Missing MinIO Artifact becomes an unhandled server error

Category: Error handling / trust
Confidence: high

`get_planner_job_artifact_content` validates content after retrieval but does not
translate MinIO `NoSuchKey`/`NoSuchBucket`/`NotFound` into a typed application
response. The exception therefore becomes HTTP 500.

Impact:

- the UI cannot distinguish unavailable source bytes from a broken server;
- the user sees a generic internal error;
- retrying suggests a transient failure even when the object is absent.

Remediation:

- map only recognized storage-missing errors to a bounded 404/410 response;
- preserve other storage failures as operational errors;
- add deterministic tests for local and MinIO missing-object behavior.

### F3 — High — Primary recovery action is misleading for confirmed missing bytes

Category: Content / recovery state
Confidence: high

The existing state preserves provenance and explains that metadata remains
available, but presents `重新加载` as the strongest action. Reloading cannot
repair a confirmed missing storage object.

Impact:

- repeated no-op retries;
- uncertainty about whether the scientific record itself is lost;
- reduced trust in the Viewer.

Remediation:

- keep retry for genuinely transient fetch failures;
- for confirmed source absence, lead with `查看来源与属性`;
- clearly distinguish `暂时加载失败` from `原始 payload 当前不可用`;
- state that no replacement version was selected;
- expose a bounded source/recovery status without operational secrets.

### F4 — Medium — Availability is discovered too late

Category: Information architecture / observability
Confidence: medium-high

Availability is primarily discovered only when the user opens content. There is
no consolidated operational inventory connecting persisted references to
storage availability.

Impact:

- broken records remain latent;
- users encounter failures one by one;
- operators cannot quantify recovery completeness.

Remediation:

- add a bounded audit utility or qualification check that reports referenced,
  present, recoverable, and unresolved objects;
- do not turn this into a second scientific authority or expose credentials.

## What already works

- PostgreSQL, Redis, MinIO, API, worker, and frontend are live.
- Exact ScientificObject and ScientificObjectVersion metadata remain readable.
- Missing source states do not silently resolve to the latest version.
- Viewer fallback retains provenance and communicates a limitation.
- The existing design system already provides restrained scientific states and
  should be reused instead of introducing a parallel UI framework.

## Professional UX direction

The final state should distinguish:

```text
TRANSIENT_FETCH_FAILURE
→ retry is primary

SOURCE_PAYLOAD_UNAVAILABLE
→ provenance/source details are primary
→ retry is secondary
→ exact-version preservation is explicit

PAYLOAD_RECOVERED
→ normal Viewer/Figure/Table content
→ no warning residue
```

Layout should preserve the Phase 9C workbench baseline: global context at the
top, collapsible data context at the left, and one active scientific workspace.
The remediation should remain compact, technical, and evidence-oriented rather
than becoming a decorative dashboard.

## Rejected alternatives

- substituting the current object version for a missing historical version;
- regenerating scientific payloads merely to make a page render;
- treating all MinIO errors as missing objects;
- hard-coding health output or hiding failures behind retries;
- adding another storage or Viewer architecture.

## Resolution

Completed on 2026-09-01.

- Restored 1,551 exact or deterministically validated objects to the active
  bucket; 1,800 of 1,805 referenced objects are now present.
- The canonical diffusion Job has 8/8 Artifact payloads available with exact
  size and SHA-256 validation.
- MinIO `NoSuchKey` and local missing-file errors are typed 404 responses;
  operational storage failures are typed 503 responses.
- Desktop and mobile Research, Report and Dataset paths contain no infinite
  result loading, Internal Server Error, unexpected 5xx, or global overflow.
- Five references remain unavailable because no exact bytes exist in any known
  store. They retain a professional fail-closed state and exact provenance.

See `PAYLOAD_AVAILABILITY_REMEDIATION_RESULTS.md` and the recovery manifest for
the complete identities and validation evidence.
