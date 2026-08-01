# Phase 10M-1 Historical Job Projection

Status: current projection-service sidecar. This is an implementation
description, not a completion record.

## Explicit projection

`WorkspaceProjectionService` in `apps/api/mdi_api/workspaces.py` performs the
explicit Job-to-Workspace projection. The operation loads the exact Project
and Job, verifies project scope, collects available source metadata, derives
bounded panel descriptors, and creates or returns the single Workspace for
that `(projectId, sourceJobId)` pair.

Ordinary Job reads and project Job listing expose whether a Workspace exists;
they do not perform a hidden write. There is no application-startup backfill
and no migration-time historical scan.

## Source collection

The projection uses source identifiers and hashes from existing Project,
Dataset, DataProfile, AnalysisIntent, EligibilityResolution, selection
decision, AnalysisPlan, Job, ToolCall, Artifact metadata, dependency
execution, Interpretation, Report, and Recipe repositories when available.
It does not read ArtifactStorage bodies to create a Workspace. Artifact
metadata is projected only as bounded reference information.

Modern identity chains preserve Plan 0.1 or 0.2 as stored. Missing modern
identity is not silently repaired or rebound to the latest source. Historical
Jobs may project as read-only when exact modern identity is unavailable.

## Projected states

The service currently distinguishes source and execution conditions including:

- `RUNNING` and `COMPLETE` for corresponding current Job states;
- `PARTIAL_RESULTS` for partial execution;
- `FAILED` for failed source execution;
- `LEGACY_READ_ONLY` when historical identity is insufficient for a modern
  editable projection;
- `STALE` when stored source identity no longer matches current source facts;
- `SOURCE_MISSING` when the retained source Job is unavailable;
- `UNSUPPORTED` for unsupported source or panel contracts.

Panel states are reprojected from the current source snapshot. Missing or
unsupported interpretation/artifact sources do not become empty successful
panels. Unsafe HTML/JavaScript-like artifact contracts use the inert fallback
renderer contract; paths, storage keys, and payload text are not emitted.

Successful source references remain auditable while stale, missing, legacy,
partial, and blocked conditions remain visible. The projection does not alter
Job, ToolCall, Artifact, Plan, Interpretation, Report, or Recipe status.

## Verification state

The focused projection/API test file and full local backend regression cover
modern idempotency, Plan 0.1 legacy, Plan 0.2 exact identity, partial, stale,
missing-source, unsupported-artifact, metadata-only, and no-hidden-write
cases. PostgreSQL service-backed projection and exact-SHA CI remain
**PENDING**.
