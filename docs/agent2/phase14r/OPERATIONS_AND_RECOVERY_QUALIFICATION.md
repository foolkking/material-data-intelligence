# Operations and Recovery Qualification

Phase 14-R must qualify the existing service topology rather than introduce a
new deployment platform:

```text
PostgreSQL = scientific identity/state/provenance authority
Redis = queue/cache/transient state
MinIO = source and Artifact bytes
API + real workers + configured provider
```

Required drills:

* PostgreSQL backup/restore followed by scientific identity and provenance
  integrity checks.
* MinIO source/Artifact backup, checksum validation, restore and bounded
  missing-object behavior.
* Redis restart/loss with PostgreSQL/MinIO retained; queued work must recover
  or surface a truthful failure without changing scientific authority.
* Health/queue/worker/pool monitoring, stuck-job visibility and bounded
  upload/Dataset/Artifact/concurrency/provider resource limits.

Current Phase 14 seal proves runtime health and DB pool snapshots but does not
provide a fresh Phase 14-R backup/restore drill, alerting campaign or quota
evidence. Status: `NOT_QUALIFIED`.

