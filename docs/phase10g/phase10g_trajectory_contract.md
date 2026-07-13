# Phase 10G Trajectory Contract

Phase 10G defines an inert, deterministic trajectory data family. It implements contract validation, small fixtures, summary/manifest validation, independent TypeScript comparison, caps, and security evidence. It does not parse trajectory files, register a tool, execute an adapter, or render/play frames.

The family is `phase10g.trajectory.v1`, `phase10g.trajectory_frame.v1`, `phase10g.trajectory_summary.v1`, and `phase10g.trajectory_manifest.v1`. JSON is the v1 interchange representation. Large indexed/chunked storage is reserved for a later parser/runtime phase.

Every frame uses stable integer atom identities and contiguous zero-based frame identity. Static `viewer_scene` remains unchanged; a future viewer may derive a static display scene from a validated frame, but that derivative is never trajectory authority.

Implementation: `mdi_artifact_core.trajectory_contract`. Independent reference: `apps/web/app/lib/trajectoryContract.ts`. Fixtures and generated evidence are under `docs/phase10g/`.
