# Phase 14-R — Scientific Payload Availability Remediation

Date: 2026-09-01

## Objective

Diagnose and repair user-visible scientific content that currently fails with
`Internal Server Error`, `SOURCE_MISSING`, unavailable object-store payloads,
or metadata-only Viewer fallbacks.

## Required sequence

1. Verify the same-stack PostgreSQL/Redis/MinIO/API/workers/frontend runtime.
2. Audit PostgreSQL references against actual MinIO objects.
3. Recover exact matching payloads from existing repository-owned qualification
   storage only when checksum, size, project, job, and artifact identities
   prove an unambiguous match.
4. Never substitute a newer scientific version or a different Artifact.
5. Convert unrecoverable object-storage misses into bounded typed API responses,
   never unhandled 500 errors.
6. Present a professional, actionable Viewer state that preserves metadata,
   exact provenance, limitations, and legitimate recovery actions.
7. Verify authenticated desktop/mobile user paths and focused backend/frontend
   regressions.

## Frozen boundaries

- Do not stop the currently running services or close Chrome.
- Do not modify scientific values, Result authority, or version identity.
- Do not fabricate or regenerate missing scientific payloads.
- Do not replace historical exact-version references with current versions.
- Preserve unrelated worktree modifications and user-owned evidence.
