# Phase 13-1 Durable Upload/Worker Fix-Forward #3

`P13-R3-001` was caused by the real HTTP upload retaining normalized source exports only in the Phase 2 process-local runtime. The Planner persisted a SQL Dataset without those exact durable refs, so a fresh worker could not reconstruct `profile` or the normalized table before its first ToolCall.

The correction reuses the existing authority: PostgreSQL `datasets.metadata_json` stores the normalized source manifest, `data_profiles.profile_json` stores DataProfile 2.4, and MinIO/ArtifactStorage stores the exact normalized payload and metadata bytes. Upload verifies exact ID, semantic object hash, storage checksum and project/dataset scope before the endpoint succeeds. Executable Planner jobs fail before persistence/enqueue when durable root resolution is unavailable.

No schema, migration, parser science, Planner selection, Adapter, Tool, Artifact family, input support or capability changed. Fact Model `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06` and Scope Baseline `eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94` remain unchanged.
