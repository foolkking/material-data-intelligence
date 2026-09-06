# Phase 14-R Scientific Payload Availability Remediation Results

Date: 2026-09-01
Repository HEAD: `9864e79c433536cc90b24c6a4c68c5bebd940daa`

## Verdict

```text
PAYLOAD_AVAILABILITY_ROOT_CAUSE =
STORAGE_ROOT_RUNTIME_SPLIT
+
UNHANDLED_MINIO_NOT_FOUND_EXCEPTION

SERVICES_STOPPED = NO
SILENT_LATEST_SUBSTITUTION = NO
SCIENTIFIC_PAYLOAD_FABRICATION = NO
```

PostgreSQL, Redis, MinIO, the Redis-backed workers, API and frontend are
running. The user-visible failures came from PostgreSQL references whose exact
objects were split across historical MinIO qualification roots, plus an API
boundary that allowed `NoSuchKey` to become HTTP 500.

## Exact recovery

The recovery compared authoritative PostgreSQL references with the active and
preserved MinIO stores. An object was restored only when the target key and
size/SHA-256, content hash, or normalized metadata identity proved the same
payload. No newer object version or alternate Artifact was selected.

```text
referenced objects = 1805
present before = 249
recovered = 1551
present after = 1800
unresolved = 5
```

The detailed manifest is
`docs/agent2/phase14r/evidence/payload_storage_recovery_2026-09-01.json`.

Target historical Job:

```text
Job = job_dc63f3f5d57742009c6be09e
Artifact inventory = 8
Artifact content HTTP 200 = 8/8
size validation = 8/8
SHA-256 validation = 8/8
```

Exact Viewer source:

```text
ScientificObject = f834e358-9944-4fe8-a3ab-f85d68041f54
ScientificObjectVersion = a22745f2-17b6-434f-ba4c-3fe6bd244841
Viewer = scientific.trajectory
payload_status = READY
```

Recovered Dataset object-store checks:

```text
dataset_0001_441637edf69740aa = 200
dataset_0001_297971804fe54c8e = 200
dataset_0002_e334bd51ef524f0d = 200
dataset_0001_44e26b062e97479d = 200
```

## Unrecoverable historical payloads

Five references have no exact bytes in the active store, preserved MinIO
stores, or repository files:

- two old qualification fixture Artifacts: `art_live_1`, `art_loop`;
- raw, normalized, and metadata objects for
  `dataset_0001_a0b09e3324e44ca4`.

The missing Dataset retains its record, Profile, schema and exact identity, but
its raw `materials.zip` and normalized table cannot be reconstructed without
the original upload or a separate backup. It therefore remains fail-closed
instead of being fabricated.

## Product repair

- Missing exact Artifact content now returns typed
  `404 ARTIFACT_CONTENT_NOT_FOUND`.
- Non-missing MinIO failures return typed
  `503 ARTIFACT_STORAGE_UNAVAILABLE`.
- Storage internals, keys and credentials are not exposed.
- Confirmed missing payloads show preserved Artifact/version provenance,
  explain that no replacement was selected, and lead with source inspection.
- Transient failures retain a separate retryable state.
- Missing source Viewers do not expose a Research action that would imply the
  payload is usable.

## Same-stack runtime

```text
frontend = http://127.0.0.1:3013
API = http://127.0.0.1:8005
PostgreSQL = 127.0.0.1:55434
Redis = 127.0.0.1:6379
MinIO = 127.0.0.1:9000
MinIO console = 127.0.0.1:9001
workers = 6 Redis-backed workers
LLM provider = DeepSeek / deepseek-v4-flash
```

`GET /health/runtime` returned 200 with PostgreSQL, Redis, MinIO, worker and
provider all `ok`.

## Authenticated browser evidence

Desktop `1280x720` and mobile `390x844` were exercised with the acceptance
researcher account.

Canonical routes:

- Research:
  `/projects/project_0002_1a0af866391f412d/research/research_13cc758206ea45de9a537716ba7972dd?run=job_dc63f3f5d57742009c6be09e`
- Report:
  `/projects/project_0002_1a0af866391f412d/reports/job_dc63f3f5d57742009c6be09e`
- Dataset:
  `/projects/project_0002_1a0af866391f412d/datasets/dataset_0001_441637edf69740aa`

Results:

```text
infinite scientific-result loading = 0
Internal Server Error text = 0
unexpected HTTP 5xx = 0
console errors on mobile canonical paths = 0
global horizontal overflow at 390px = 0
```

The legacy Report route performs an expected new-snapshot probe returning 404
before its authorized legacy fallback. The final Report renders the complete
MSD table, exact units, fit window, R², diffusion coefficient, evidence,
limitations and checksum.

Screenshots:

- `phase14r-payload-recovery-research-1280.png`
- `phase14r-payload-recovery-report-1280.png`
- `phase14r-payload-recovery-dataset-1280.png`
- `phase14r-payload-recovery-research-390.png`
- `phase14r-payload-recovery-report-390.png`
- `phase14r-payload-recovery-dataset-390.png`
- `phase14r-payload-unavailable-professional-390.png`

The visible Chromium validation window remains open on the canonical Research
route for user inspection.

## Verification

```text
backend focused = 9 passed
frontend focused = 45 passed
frontend typecheck = PASS
frontend production build = PASS
touched Ruff = PASS
git diff --check = PASS
```

## Remaining external recovery input

To make `dataset_0001_a0b09e3324e44ca4` fully interactive, provide the
original `materials.zip` whose SHA-256 is:

```text
b75f9a1d398de4636e4494f2aaa04977326ca66a96356fcc1be87e86a3a520c4
```

Until then the platform preserves the historical record and exact provenance
without claiming the missing scientific payload is available.

## Product-maturity follow-up

The external-input requirement above is superseded by a later byte-identity proof. The
persisted Dataset timestamp plus the authoritative transport test input reproduced the exact
143-byte ZIP and its expected SHA-256. The current parser then reproduced the exact
normalized bytes, object ID, object hash, schema and row content.

The three existing MinIO keys were conditionally created and independently read back. The
Dataset now resolves through its normal object-store endpoint and renders the one-row
scientific table. This was a storage continuity repair only:

```text
ScientificObjectVersion mutation = NO
ScientificResult mutation = NO
Report mutation = NO
silent substitution = NO
```

Evidence:
`docs/agent2/product_maturity/evidence/exact_dataset_payload_recovery_2026-09-01.json`.

## Current reconciliation

The earlier five-reference inventory is historical evidence from before the
exact Dataset recovery. Current acceptance-visible status is:

```text
acceptance Dataset missing payloads = 0
acceptance Dataset interactive rows = 1
legacy synthetic unresolved Artifact refs = 2
service outage = NO
```

The two unresolved synthetic references remain intentionally unavailable and
are not used as acceptance-user scientific data.
