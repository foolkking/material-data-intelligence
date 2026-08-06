# Service-Backed Closure

The exact-SHA CI gate runs the existing L1-L5, M1, M5, M6 service cases plus `test_phase10m7_postgres_redis_minio_workspace_integration_closure`. It requires PostgreSQL, Redis, MinIO, migration head 0007, at least 41 passing tests, zero skipped, zero failed, and the named M7 test PASS.

`LOCAL_SERVICE_BACKED = UNAVAILABLE` unless `MDI_RUN_INTEGRATION=1` and all three local services are configured. Local unavailability is not recorded as PASS.
