# Service State

```text
LOCAL_SERVICE_BACKED = UNAVAILABLE
REASON = docker command is not installed or not on PATH
LOCAL_SERVICE_BACKED_PASS_CLAIMED = NO
```

Phase 10L-5 archive exact-SHA CI `30695065220` previously passed the
PostgreSQL + Redis + MinIO service job and no-skipped assertion at archive SHA
`8f304fa08ddab1cefd69848f621f8438fc2038d5`.

Phase 10M-0 audit/planning and completion SHAs each require their own exact-SHA
CI service-backed success. Historical success is entry evidence, not a
substitute for those pending runs.
