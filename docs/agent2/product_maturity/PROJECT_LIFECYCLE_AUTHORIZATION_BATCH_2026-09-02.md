# Product Maturity — Project Lifecycle Authorization Batch

Date: 2026-09-02

## Finding

Project access already uses two compatible authorities:

- `projects.created_by` for backwards-compatible ownership;
- `project_members.role` for explicit collaborator access.

The durable project repository previously persisted only the first authority.
That left newly-created projects without an explicit owner membership, so
membership-scoped list/search and future collaborator operations could observe
an incomplete lifecycle boundary.

## Bounded repair

`SqlAlchemyProjectRepository.save()` now:

1. performs an upsert for project metadata rather than deleting/reinserting an
   existing project row;
2. preserves child scientific records and existing membership rows on re-save;
3. creates the creator's explicit `project_members` row with role `owner` when
   a new project is persisted.

This is organizational authorization metadata only. It does not change
ScientificObject, ScientificObjectVersion, ScientificResult, Artifact, or
source-version authority.

## Security and lifecycle invariants

- Project owner access remains valid through `created_by`.
- New projects participate in the same membership boundary as existing
  projects.
- Re-saving metadata cannot remove scientific descendants or collaborator
  memberships.
- No scientific version is created, mutated, or substituted.
- Existing project authorization checks remain server-side.

## Evidence

Focused regression:

```text
python -m pytest tests/test_product_maturity_project_lifecycle.py tests/test_phase6_integration.py -q
3 passed, 16 skipped
```

The skipped cases are pre-existing optional service-backed Phase 6 checks;
the lifecycle regression itself passes and does not rely on a skip.
