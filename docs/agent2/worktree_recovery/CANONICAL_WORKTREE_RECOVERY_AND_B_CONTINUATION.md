# Canonical Worktree Recovery & Workstream B Continuation

状态：处理中

## Canonical root

Active engineering, testing, documentation, and service verification must run
from `E:\1project\mdi-b0-5a1`.

`E:\1project\Material Data Intelligence` is historical source material and an
in-progress change source only. Its dirty tree is not applied wholesale.

## Recovery scope

Semantically reconcile the valid Workstream A lifecycle/recovery behavior and
the already implemented Workstream B context/memory provenance behavior into
the migrated canonical owners. Preserve existing API, authorization, schema,
queue, worker, Tool, Adapter, scientific identity, and compatibility contracts.

## Continuation rule

Classify old-tree work as completed, implemented-but-unverified, in-progress,
or not started. Keep valid completed behavior, adapt it to canonical owners,
verify it in this tree, and continue Workstream B from the first genuinely
unfinished requirement. Do not restart migration, A, B, or the system review.

## Required evidence

- canonical API, worker, and frontend verification uses this root;
- no whole-tree copy or unrelated dirty-tree change is applied;
- no duplicate business implementation is created;
- focused lifecycle, context, memory, authorization, exact-version, and
  service-backed checks are run where practical;
- persistent task/progress/results authorities record the reconciliation.
