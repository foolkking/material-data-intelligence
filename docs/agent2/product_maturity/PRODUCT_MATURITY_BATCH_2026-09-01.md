# Product Maturity Batch — 2026-09-01 (continued)

## Scope

This batch closes the remaining user-visible Dataset interaction seam after
the same-stack runtime and account/admin work. It does not change scientific
authority, object/version identity, Result records, or service topology.

## Runtime truth

The retained qualification stack was checked before browser verification:

```text
frontend       = http://127.0.0.1:3013 (PID 27228)
API            = http://127.0.0.1:8005 (PID 28296)
PostgreSQL     = 127.0.0.1:55434/mdi (PID 30020)
Redis          = 127.0.0.1:6379/13 (PID 7656)
MinIO          = 127.0.0.1:9000/9001 (PID 5840)
workers        = six Redis-backed workers
```

`GET /health/runtime` returned `200` with:

```text
database.backend       = postgresql
redis.backend          = redis
artifactStorage.backend= minio
worker.backend         = redis
llmProvider            = deepseek / deepseek-v4-flash / configured
```

This is not a stopped-service condition.

## Dataset interaction repair

The source Dataset object-store projection now adds deterministic, provenance
only row identity for DataFrame rows:

```text
objectId
sampleRef
sampleKey
```

Explicit `sampleRef`, `sample_id`, or `id` values are preserved. Otherwise the
identity is derived from the Dataset/version/object hash and row position by
the existing stable-sample policy. Scientific values are not changed.

The shared scientific table renderer:

- keeps `sampleRef` visible;
- hides only the technical `sampleKey` column;
- fixes identity/selection to the left on narrow layouts;
- exposes a horizontal-scroll affordance on mobile;
- enables keyboard-accessible `选择` only when durable identity exists;
- keeps sorting and pagination from changing semantic row identity.

## Live browser evidence

The authenticated persistent tab was refreshed without closing the tab or
restarting services:

```text
route =
/projects/project_0001_d286007db78e427e/data
?dataset=dataset_0001_a0b09e3324e44ca4
```

The rendered table showed:

```text
formula      = Si
value        = 1
objectId     = obj_dataframe_60c91184df02
sampleRef    = dataset_0001_a0b09e3324e44ca4@2:60c91184df022d34:0
selection    = enabled ("选择")
```

The account tab showed the authenticated acceptance identity and server
managed role/security state. Browser diagnostics for the refreshed Dataset
page returned no errors or warnings.

## Regression evidence

```text
backend focused       = 56 passed
frontend focused      = 91 passed
full backend          = 1978 passed, 84 skipped
frontend typecheck    = PASS
frontend build        = PASS
compileall            = PASS
uv lock --check       = PASS
touched Ruff          = PASS
git diff --check       = PASS
```

Existing full product and payload-availability evidence remains authoritative;
legacy synthetic payload references remain explicitly fail-closed rather than
being fabricated or substituted.

## Remaining product-maturity status

The service stack is healthy and the acceptance Dataset is interactive. The
broader Product Maturity Closure task remains in progress because unrelated
administrative/lifecycle maturity work and historical synthetic fixture
residue are still tracked separately. Phase 15 is not started.
