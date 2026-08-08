PostgreSQL/Redis/MinIO service-backed N2 closure is owned by the integration
runner. Required result: passed > 43, skipped = 0, failed = 0, errors = 0.
Coverage includes exact N1 binding, N2 persistence, checksum, queue state,
Workspace projection, Report/Recipe and foreign-scope rejection.

`LOCAL_SERVICE_BACKED = UNAVAILABLE`: Docker is not installed in the local
environment. Local import/collection and deterministic execution passed; the new
integration case is locally skipped and is not represented as PASS. Exact-SHA CI
must run at least 44 service tests with zero skipped and explicitly pass
`test_phase10n2_postgres_redis_minio_exact_n1_dependency_closure`.
