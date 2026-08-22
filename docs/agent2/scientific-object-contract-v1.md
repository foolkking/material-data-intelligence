# Scientific Object Contract v1

Agent 2.0 adds a deterministic scientific identity layer above existing
Dataset, Resource, Artifact, and Tool records. It does not reinterpret or
backfill historical records automatically.

## Identity

`ScientificObject` is the stable logical identity. `ScientificObjectVersion`
is immutable content. A version is addressed by `(scientific_object_id,
version_no)` and retains exact source-resource and parent-version references;
updating the logical object's `current_version_id` never changes historical
references.

The existing repository uses string project/user identifiers, so the new
object and version primary keys are UUIDs while `project_id` and
`created_by_user_id` retain the established string types.

| Entity | Required contract |
|---|---|
| Object | `id`, `project_id`, `kind`, namespaced `object_type`, `display_name`, lifecycle, `current_version_id`, `row_version` |
| Version | `id`, logical object id, `version_no >= 1`, schema version, source/parent refs, payload `StorageRef`, content/semantic hashes, canonical metadata, availability |
| Relationship | project, source/target version, namespaced relation type, metadata; self edges and duplicate edges are rejected |

Stable kinds are `DATASET`, `TABLE`, `COMPOSITION`, `STRUCTURE`,
`TRAJECTORY`, `DIFFRACTION`, `ELECTRONIC`, `PHONON`, `VOLUMETRIC`,
`MODEL_RESULT`, `PROPERTY_DATA`, and `GENERIC`. Concrete types remain
namespaced, for example `structure.crystal` and
`electronic.band_structure`.

## Validation and authorization

The service checks registry membership, kind/type compatibility, non-empty
hashes, project ownership of source and parent references, exact version
ownership, and parent-graph cycles. The server re-authorizes every
`ScientificObjectRef`; client-supplied `project_id` is never trusted.

## Read API

- `GET /api/projects/{project_id}/scientific-objects`
- `GET /api/scientific-objects/{object_id}`
- `GET /api/scientific-objects/{object_id}/versions`
- `GET /api/scientific-objects/{object_id}/versions/{version_id}`
- `GET /api/scientific-objects/{object_id}/relationships`

The list endpoint supports `kind`, `object_type`, `lifecycle_status`,
case-insensitive `search`, bounded `limit`, and UUID cursor pagination.

## Phase 1 boundary

Creation/versioning is available to the repository/service foundation and
tests. Full Data Management CRUD and historical Dataset/Artifact backfill are
not implemented in this phase.
