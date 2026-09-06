# Scientific Data Availability UX Audit — 2026-09-03

## Scope and evidence

This audit covers the authenticated scientific-data and Artifact paths reported
by the user as:

- `Internal Server Error`;
- `当前解析资源暂时无法读取`;
- `原始来源当前不可访问`;
- a metadata-only Viewer with no interactive scientific payload.

Evidence was collected from the current same-stack runtime, PostgreSQL
authorities, the active MinIO bucket, retained qualification object stores, API
health, RQ worker registration, and the authenticated browser at
`http://127.0.0.1:3000`.

## Executive summary

The platform services are running. PostgreSQL, Redis, MinIO, API, workers and
frontend are reachable, and `/health/runtime` reports PostgreSQL, Redis-backed
work, MinIO artifact storage and the configured provider.

The user-visible failure has two narrower causes:

1. eleven exact MinIO keys referenced by the acceptance researcher's
   PostgreSQL authority are absent from the active object store;
2. the local launch scripts and the operational worker snapshot disagree about
   the Redis database, so an otherwise healthy worker fleet can be reported as
   unavailable or receive work on the wrong queue namespace.

The missing bytes are recoverable without scientific substitution. Exact
copies exist in retained repository qualification stores or under another
current key, and every candidate matches the authoritative SHA-256 and byte
size.

## What already works

- Missing payloads fail closed; no newer ScientificObjectVersion is silently
  selected.
- Exact ScientificObject, ScientificObjectVersion, Result and Artifact
  metadata remain readable.
- The Viewer provides retry and source/provenance actions.
- The active MinIO bucket contains more than 8,700 objects; this is not a
  bucket-wide outage.
- The authenticated product shell and healthy Dataset routes render normally.

## Findings

### F1 — Blocker — Eleven exact referenced payloads are absent from active MinIO

Category: scientific content availability
Confidence: high

The acceptance-owned scope contains one unavailable ScientificObjectVersion
payload and ten unavailable Artifact payloads. Their PostgreSQL rows remain
intact and each row identifies an exact storage key, checksum and byte size.

Impact:

- a Structure Viewer can show only provenance metadata;
- scientific tables, summaries, recipes and quality artifacts cannot open;
- Reports referencing those artifacts lose their professional inspection path.

Remediation:

- restore only byte-identical payloads;
- verify every source and target against the authoritative SHA-256 and size;
- retain all database identities and exact-version references;
- record a machine-readable recovery manifest.

### F2 — High — Stored availability can disagree with durable object existence

Category: trust / state integrity
Confidence: high

The unavailable ScientificObjectVersion is marked `AVAILABLE` in PostgreSQL
while its exact active MinIO key returns `NoSuchKey`.

Impact:

- discovery looks healthy until content is opened;
- availability errors are encountered one record at a time;
- users cannot distinguish a service outage from an exact-object durability
  problem.

Remediation:

- add or reuse a provider-aware integrity check that reconciles referenced
  objects against the declared storage provider;
- treat the database availability state as a product state, not proof that a
  byte object still exists;
- never synthesize or substitute missing scientific content.

### F3 — High — Redis database drift splits operational truth

Category: runtime reliability
Confidence: high

The current API/worker launchers use Redis database `0`, while the retained
same-stack operations qualification expects database `13`.

Impact:

- the health endpoint can report Redis-backed execution while operational
  inspection sees zero workers;
- API and workers can silently join different queue namespaces after a
  restart;
- recovery and acceptance evidence become unreliable.

Remediation:

- resolve one repository-authoritative Redis database for the qualification
  stack;
- make API, all workers and the operations snapshot use that value;
- make launch scripts idempotent and verify registered workers after startup.

### F4 — Medium — The unavailable state is scientifically safe but not fully actionable

Category: error-state UX
Confidence: high

The current Viewer correctly states that metadata remains readable and no
replacement source is selected. However, `重新加载` remains visually prominent
even when the exact object is durably absent, and the body mixes Chinese with
the implementation term `payload`.

Impact:

- users may retry indefinitely;
- the difference between a transient fetch failure and a missing exact object
  is unclear;
- the state is trustworthy but not yet professional.

Remediation:

- use `科学数据内容` or `原始科学数据` instead of `payload` in user-facing copy;
- make source/provenance inspection the primary action for confirmed
  unavailability;
- reserve retry primacy for transient storage failures;
- restore normal content automatically when exact bytes become available.

### F5 — Medium — Multiple stale development entry points create false outage reports

Category: navigation / runtime continuity
Confidence: high

Older browser tabs still reference stopped development ports while the
canonical frontend is healthy on port `3000`.

Impact:

- users can interpret a stale tab as a product outage;
- acceptance work is split across inconsistent runtimes.

Remediation:

- preserve the canonical `3000` entry point across rebuilds;
- keep the current authenticated tab open;
- make local stack startup repeatable without clearing the running frontend
  output directory.

## Unified remediation

The repair is one bounded availability batch:

```text
authoritative PostgreSQL reference
→ locate exact retained bytes
→ verify SHA-256 and size
→ restore the same MinIO key
→ reconcile runtime queue configuration
→ re-open Viewer / Artifact / Report
→ verify desktop and mobile
```

Rejected alternatives:

- replacing an unavailable historical payload with the latest version;
- regenerating scientific values from UI metadata;
- changing database identities;
- hiding the error behind unconditional retry;
- spoofing health or worker status;
- creating another Viewer or storage authority.

## Acceptance criteria

```text
acceptance ScientificObjectVersion payloads present = 13 / 13
acceptance Artifact payloads present = 241 / 241
checksum mismatches = 0
silent latest substitution = NO
API / worker Redis namespace = identical
registered workers = expected fleet
Viewer / Figure / Table / Report paths = readable
desktop and mobile critical errors = 0
```

## Resolution evidence — 2026-09-03

The availability repair was executed against the current acceptance scope.

```text
runtime database = PostgreSQL
runtime redis = Redis / DB 13
runtime artifact storage = MinIO / mdi-artifacts
runtime workers = 6
queue depth = 0 on all 6 queues
idle-in-transaction = 0
pool timeouts = 0
```

Exact-byte verification:

```text
ScientificObjectVersion payloads present = 13 / 13
acceptance Artifact payloads present = 241 / 241
missing exact payloads = 0
checksum mismatches = 0
```

The repaired paths were re-opened through the API after runtime alignment:

```text
Artifact content endpoint = HTTP 200
exact version Viewer endpoint = HTTP 200
```

The exact references were restored under their original MinIO keys. No
ScientificObject, ScientificObjectVersion, Result, or source reference was
rewritten, and no newer version was substituted. The recovery evidence is
recorded in:

```text
docs/agent2/product_maturity/evidence/exact_minio_reference_recovery_2026-09-03.json
docs/agent2/product_maturity/evidence/exact_minio_availability_verification_2026-09-03.json
```

The remaining historical generated-test placeholders outside the acceptance
scope were intentionally not synthesized; they have no authoritative source
bytes and must remain fail-closed.
