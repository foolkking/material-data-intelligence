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

Current sealed implementation proves rename/archive/restore for projects,
datasets and scientific objects. Trash/purge, dependency preview, retention
policy and mature bulk management remain open Phase 14-R work.

