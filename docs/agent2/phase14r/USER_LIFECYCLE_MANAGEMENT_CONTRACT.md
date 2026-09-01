# User Content and Lifecycle Management Contract

Lifecycle states are explicit and distinct:

* `ACTIVE`: available to normal workflows.
* `ARCHIVED`: retained and historically addressable, excluded from default
  active selection.
* `TRASHED`: user-requested deletion intent, recoverable while retention
  policy permits.
* `PURGED`: irreversible only after authorization and dependency checks.

ScientificObject and ScientificObjectVersion authority remains unchanged.
Versions referenced by Results, Artifacts, Evidence or Reports are protected
from destructive deletion. Metadata rename does not mutate scientific state.

Every destructive action must use a server-derived dependency impact preview,
authorization, explicit confirmation and an auditable result. Bulk operations
must apply the same policy per entity. Archive/restore never creates a
ScientificObjectVersion. Orphan cleanup is based on persisted references, not
frontend visibility.

Current Phase 14-R implementation proves rename/archive/restore for projects,
datasets and scientific objects. Projects and Datasets additionally project a
recoverable `TRASHED` state through their existing metadata authorities, while
ScientificObject now persists the same state in its lifecycle authority with a
bounded pre-Trash marker:

* Project trash metadata is stored in `project_configs.config_json`.
* Dataset trash metadata is stored in `datasets.metadata_json`; the underlying
  database status remains `archived` so no released scientific-state
  constraint is widened.
* Both entities retain the lifecycle state that preceded Trash and restore to
  it deterministically.
* Normal Console/Data discovery and new Research actions exclude trashed
  entities, while their historical project/data routes remain readable.
* The Project and Dataset product surfaces expose dedicated Trash filters,
  per-row Trash/Restore actions and bounded bulk Trash/Restore.
* Global search accepts `status=trashed` but continues to enforce normal
  project authorization.

ScientificObject Trash/Restore uses the existing authorized metadata PATCH and
preserves the prior ACTIVE/ARCHIVED state without creating a scientific
version. The Data Navigator exposes ACTIVE, ARCHIVED and Trash filters and
reversible object actions; historical versions remain addressable while an
object is trashed.

The lifecycle UI receives a bounded server-derived dependency preview before
Trash or permanent-delete confirmation. Physical delete remains restricted to
owner-authorized empty Projects/Datasets and fails closed when persisted
dependencies exist. Retention expiry, purge execution, export governance and
cross-entity mature bulk management remain open Phase 14-R work.

Research Sessions now have a bounded recoverable lifecycle through the
existing `sessions.status` authority. Project-write users can call
`PATCH /research-sessions/{session_id}` with `lifecycle=TRASHED` or
`lifecycle=ACTIVE`. Archived or trashed sessions remain readable for history
and exact-result provenance, but new Messages and ResearchTurns fail closed
until restoration. A non-terminal ResearchTurn blocks Trash. The Research
Records popover exposes the same reversible action with retention-aware
confirmation. No Turn, Result, Artifact, Evidence, ScientificObject, or
ScientificObjectVersion is deleted or mutated.

The session management projection also supports a bounded title override and
pin state for organization. Renaming changes only the navigation/search label;
it never changes the historical user question or any scientific descendant.
Pinned sessions sort first in the Research Records popover and authorized
global search. When an archived or trashed session is opened directly, the
timeline header shows its state, places Restore beside the Research Records
entry point, keeps the historical workbench readable, and replaces the composer
with an explicit read-only explanation. Retry controls are likewise withheld
until the session is restored, so the UI cannot imply that a historical record
is writable.

Scientific Reports also expose a recoverable communication-layer lifecycle.
The immutable Report snapshot remains unchanged; project-scoped lifecycle
metadata is stored under
`project_configs.config_json.scientificReportLifecycle`. Project-write users
may move a Report between `ACTIVE`, `ARCHIVED`, and `TRASHED`; `ACTIVE` removes
the overlay entry. Trashed and archived Reports remain directly readable by
their exact Report/Result/Interpretation/source-version identities. The report
index exposes current, archived, Trash, and all filters plus reversible
Trash/Restore actions. These actions create no Job, ToolCall, Artifact,
ScientificResult, ScientificObject, or ScientificObjectVersion.

Before a Report is moved to `TRASHED`, the index requests the secured
`GET /api/scientific-reports/{report_id}/dependency-impact` projection and
requires explicit confirmation after showing bounded ResearchTurn,
ScientificResult, Interpretation, Artifact, Evidence and exact source-version
references. The preview is derived server-side from the immutable report
snapshot and states that historical provenance remains protected.

ScientificObject lifecycle previews use the same server-derived boundary:
`GET /api/scientific-objects/{object_id}/dependency-impact` is write-authorized
for the owning project and returns bounded exact-version dependencies
(ScientificResults, ResearchTurns, and report snapshots) plus protected
historical-provenance flags. The preview is informational only; it does not
mutate the object, versions, current-version pointer, Results, Artifacts, or
Reports. The existing `PATCH /api/scientific-objects/{object_id}` remains the
single lifecycle mutation authority and still requires explicit UI
confirmation.

## Reproducibility manifest export

Scientific Report pages provide a bounded, non-executable JSON
`mdi.reproducibility-manifest/1.0` export alongside Markdown. It contains the
authorized Report/snapshot/ResearchTurn/ScientificResult/Interpretation
identities, exact object/version references, persisted Figure Artifact IDs,
Evidence/Data source refs, limitations and omitted-supporting-item markers.
It never exports provider prompts, credentials, raw Tool logs, arbitrary code
or unbounded source payloads. Export is a presentation/read operation and
does not create Jobs, ToolCalls, Artifacts or ScientificResults.

## Unified Trash Center and retention boundary (2026-09-01)

The authenticated product now exposes a single `/trash` management surface
from the account menu. It reads the authorized `GET /search?status=trashed`
projection and presents bounded restore actions for Project, Dataset,
ScientificObject, Research Session and Report records. Restore delegates to
the existing lifecycle authority for each entity; it never reconstructs or
rewrites a scientific descendant.

Permanent deletion is deliberately narrower than restore. The Trash Center
requests the existing server-derived dependency impact projection before
offering a destructive action. Only owner-authorized empty Projects and
Datasets with `canDelete=true` expose permanent deletion, and the user must
type the exact display name. Protected content has no destructive control and
continues to disclose that historical provenance remains available. There is
no automatic expiry job in the current product; this is an explicit
retention boundary rather than an implicit data-loss timer.

Browser evidence used disposable, empty projects only:

```text
project_0001_e0091c0e6f5a4d58
TRASHED → dependency preview canDelete=true → exact-name PURGED

project_0002_f78490df5c38406a
TRASHED → Trash Center Restore → ACTIVE
```

No ScientificObjectVersion, ScientificResult, Artifact or historical
Research record was used as a purge target.

## Report organization metadata (2026-09-01)

Finalized Scientific Report snapshots remain immutable. Users with project
write access may change only bounded catalog metadata:

```text
Rename display title
Pin / unpin
Archive
Trash
Restore
Export
```

Rename and pin are stored in the existing project configuration overlay and
never rewrite the Report snapshot. `source_title` preserves the original
snapshot title for audit and reproducibility, while `title` is the authorized
display projection. Pinning changes only list ordering. The existing overflow
menu owns these secondary actions; report reading, Evidence and source
navigation remain the primary workflow.

## Atomic Research and Report bulk management

The earlier cross-entity bulk-management gap is closed for the two remaining
high-value catalog surfaces:

```text
Research Sessions:
  PIN / UNPIN / ARCHIVE / RESTORE / TRASH

Scientific Reports:
  ARCHIVE / RESTORE
```

Both endpoints accept bounded, deduplicated identities and validate every
record against one authorized Project before entering one database
transaction. A missing, unauthorized or cross-project identity rejects the
whole request. Research Session destructive transitions also reject the whole
batch when any selected Session owns a non-terminal ResearchTurn. The frontend
submits one atomic request and leaves the full selection intact after failure
so the user can understand and correct the blocked batch.

No bulk lifecycle action creates or mutates:

```text
ResearchTurn
Job
ToolCall
Artifact
ScientificResult
ScientificObject
ScientificObjectVersion
immutable Scientific Report snapshot
```

## Scientific Report revision lifecycle

Editing a finalized Report creates a new immutable revision rather than
rewriting the source snapshot. The revision retains the exact
ResearchTurn/Result/Interpretation/object-version references and records a
bounded parent/child revision identity. The Report reader exposes revision
history and comparison beside the document navigation rather than as a
separate scientific authority.

Revision creation, listing and comparison are communication-layer operations:

```text
Job delta = 0
ToolCall delta = 0
Artifact delta = 0
ScientificResult delta = 0
```

The existing Report overflow/index surface owns archive, restore, rename,
pinning and selection actions; the Report reader owns revision inspection and
comparison. This keeps organization controls near the entity they affect
without turning the scientific document body into an action dashboard.
