# Autonomous Physical Relocation Task

- Authorization: `PHYSICAL_FILE_MOVE_AUTHORIZED = YES`
- Execution mode: continuous physical relocation, one active worktree, linear local history.
- Worktree: `E:/1project/mdi-b0-5a1`
- Start commit: `db75aa57136e4512b11b6fe69bb54840ad970323`
- No new worktree, branch, push, hash checks, runtime-data cleanup, schema/Alembic changes, or identity migration.

## Required invariants

Preserve API routes/contracts/auth semantics, database schema and Alembic identity, transaction semantics, persisted IDs, Tool/Adapter IDs, ScientificObject/Version/Result/Report/Artifact authority, six queue names, six persisted worker handler dotted paths, worker CLI identities, and UI behavior.

## Migration model

Move only cohesive canonical implementation groups. Legacy paths remain thin compatibility facades when static, dynamic, monkeypatch, test, launcher, or public compatibility references require them. Canonical modules must not import compatibility facades. Run the existing B0-6 guard and B0-7 checker after every cohesive commit. Do not change their allowlists to hide new violations.

## Required sequence

1. Capture the one pre-move backend baseline already recorded at this commit: `2185 passed, 76 failed, 75 skipped`; classify only changed-scope regressions as blocking.
2. Physically separate database engine lifecycle into `mdi_api.infrastructure.persistence.engine` and repository composition into `mdi_api.bootstrap.repository_factory`, preserving `mdi_api.database` compatibility.
3. Continue through the remaining backend ownership groups using already established canonical ownership, then frontend feature/shared/viewer groups, reducing legacy implementations without breaking frozen paths.
4. At meaningful backend/frontend milestones run focused qualification and finally the broadest safe repository qualification.
5. Stop only at `AUTONOMOUS_PHYSICAL_MIGRATION_COMPLETE` or a real semantic/identity/compatibility blocker; do not begin forensic cleanup or Project State transition.

## Acceptance

At completion: architecture guard pass, checker pass, zero cycles, zero forbidden edges, zero dynamic/public-surface errors, six handlers resolvable, queue identities unchanged, Tool/Adapter inventories unchanged, no new backend/frontend regressions, clean worktree, and no pushed commits.
