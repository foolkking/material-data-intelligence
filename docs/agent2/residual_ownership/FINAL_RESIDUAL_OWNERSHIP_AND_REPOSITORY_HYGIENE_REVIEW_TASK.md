# FINAL_RESIDUAL_OWNERSHIP_AND_REPOSITORY_HYGIENE_REVIEW

## Mode

Final source-ownership closeout after accepted architecture migration and
pre/post capability parity. Do not rerun the migration or reopen parity unless
new concrete contradictory evidence is found.

## Accepted baseline

```text
SOURCE_ARCHITECTURE_MIGRATION_COMPLETE = YES
FULL_PRE_POST_CAPABILITY_PARITY = YES
STATIC_SOURCE_CONTRACT_PARITY = PASS

UNEXPLAINED_MISSING_WEB_ROUTES = 0
UNEXPLAINED_MISSING_UI_CAPABILITIES = 0
UNACCOUNTED_FRONTEND_BUSINESS_SYMBOLS = 0
UNEXPLAINED_MISSING_HTTP_OPERATIONS = 0
UNEXPLAINED_HTTP_CONTRACT_CHANGES = 0
UNACCOUNTED_BACKEND_BUSINESS_SYMBOLS = 0
UNRESOLVED_DYNAMIC_ENTRYPOINTS = 0

HANDLERS = 6/6
QUEUES = 6 unchanged
TOOLS = 62 unchanged
ADAPTERS = 50 unchanged

CAPABILITY_PARITY_AUDIT_COMMIT =
6d2dbe5199a156f9d20ce4be91b0accbd4c61db4

MIGRATION_BASELINE =
db75aa57136e4512b11b6fe69bb54840ad970323
```

No push, branch, or worktree creation is authorized.

## Objective

Classify every remaining legacy-looking production source as exactly one:

```text
LEGITIMATE_CANONICAL_AUTHORITY
LEGITIMATE_RUNTIME_ENTRYPOINT
LEGITIMATE_COMPATIBILITY_FACADE
LEGITIMATE_PUBLIC_API_AGGREGATOR
LEGITIMATE_FOUNDATION_MODULE
TEMPORARY_COMPATIBILITY_WITH_JUSTIFICATION
MIGRATION_RESIDUE_REQUIRING_FIX
UNRESOLVED
```

Required for PASS:

```text
UNRESOLVED = 0
DUPLICATE_BUSINESS_IMPLEMENTATIONS = 0
CANONICAL_TO_COMPATIBILITY_IMPORTS = 0
```

## Priority files

### `apps/api/mdi_api/repositories.py`

Determine whether its remaining body is limited to compatibility exports,
protocol/type aliases, bundle/factory forwarding, backwards-compatible
constructors, identity-preserving exports, or intentionally stable public API.
Any real application/domain/persistence/bootstrap implementation residue must
move to the established canonical owner while the old module remains
compatible.

### `apps/api/mdi_api/db.py`

Inspect every responsibility. Preserve a cohesive schema/foundation authority
for SQLAlchemy table/model metadata, persisted identities, database contracts,
and migration-compatible declarations. Move only clearly separable repository,
application, transaction composition, service, runtime, or transport behavior.
Do not split schema authority for directory aesthetics.

### Scientific Result runtime files

Inspect:

```text
apps/api/mdi_api/scientific_results/queue.py
apps/api/mdi_api/scientific_results/reconciler.py
apps/api/mdi_api/scientific_results/worker.py
```

Verify the dynamic contract manifest, queue manifest, frozen handler paths,
tests, and actual imports. Stable persisted/dynamic runtime identities are
legitimate runtime entrypoints. A stable entrypoint may forward to canonical
implementation, but its dotted identity must remain unchanged.

## Systematic residual scan

Scan production files under:

```text
apps/api/mdi_api/*.py
apps/api/mdi_api/routers/*
apps/api/mdi_api/interpretation/*
apps/api/mdi_api/scientific_objects/*
apps/api/mdi_api/scientific_results/*
apps/api/mdi_api/scientific_reports/*
apps/web/app/components/*
```

For each file record LOC, import/export form, AST declarations and executable
bodies, canonical imports, reverse references, classification, rationale, and
whether a fix is required. Tests are not production residue.

## Facade rule

A clean facade may contain imports/re-exports, `__all__`, aliases, thin
identity-preserving wrappers/delegators, compatibility constructors, and stable
runtime forwarding. Classification must be based on ownership and AST, not a
LOC threshold.

## Frontend rule

Canonical ownership remains in `features/*`, `scientific-viewers/*`, and
`shared/*`. Production implementation bodies remaining under
`apps/web/app/components/*` must be zero, excluding legitimate thin facades or
wrappers. Report old test colocation separately as
`LEGACY_TEST_COLOCATION_DEBT`, normally non-blocking. Do not bulk-move tests for
appearance.

## Duplication and import direction

Detect any simultaneous legacy real implementation plus canonical real
implementation using AST, symbol bodies, import graphs, and reverse references.
File-name similarity alone is not duplication.

Required:

```text
DUPLICATE_BUSINESS_IMPLEMENTATIONS = 0
CANONICAL_TO_COMPATIBILITY_IMPORTS = 0
```

## LOC sanity

Use source statistics only as an anomaly detector. Reconcile legacy
implementation drain with canonical implementation gain. Do not treat total
repository size or raw qualification/artifact/cache volume as capability
evidence.

## Autonomous narrow repair

If a definite mechanical ownership residue is found, move implementation to an
existing canonical owner, reduce the old path to re-export/delegation, update
imports, preserve public/dynamic identity, test, and create cohesive local
commit(s). Do not stop for ordinary shared helpers or facade choices.

Block only for schema semantics, persisted identity, dynamic handler identity,
transaction semantics, public API, scientific authority, security, or
ambiguous runtime/user/history deletion.

## Verification

If source is unchanged, run focused architecture/ownership checks. If source
changes, additionally run dynamic contract, worker/queue, affected backend or
frontend focused tests, and frontend typecheck where applicable. Run broad
regression only for a broad ownership change. Existing environmental failures
are non-blocking unless a new regression appears.

## Prohibitions

Do not rerun the full capability parity audit, redo migration, change schema or
Alembic, delete runtime/user/historical/qualification data, clean the forensic
baseline, create branch/worktree, push, or refactor merely to reduce LOC.

## Required result

```text
FINAL_RESIDUAL_OWNERSHIP_REVIEW = PASS | REPAIRED_AND_PASS | FAIL
PHYSICAL_OWNERSHIP_MIGRATION_COMPLETE = YES | NO
DUPLICATE_BUSINESS_IMPLEMENTATIONS = <count>
UNRESOLVED_RESIDUALS = <count>
MIGRATION_RESIDUES_FIXED = <count>
LEGITIMATE_COMPATIBILITY_FACADES = <count>
LEGITIMATE_RUNTIME_ENTRYPOINTS = <count>
LEGITIMATE_FOUNDATION_MODULES = <count>
CANONICAL_TO_COMPATIBILITY_IMPORTS = <count>
SOURCE_ARCHITECTURE_MIGRATION_REOPENED = NO
CAPABILITY_PARITY_REOPENED = NO
```

Report explicit conclusions for `repositories.py`, `db.py`, and
`scientific_results/queue.py`, legacy test-colocation debt, all changed files,
and commits.

On PASS or REPAIRED_AND_PASS record:

```text
SOURCE_ARCHITECTURE_MIGRATION_COMPLETE = YES
PHYSICAL_OWNERSHIP_MIGRATION_COMPLETE = YES
FULL_PRE_POST_CAPABILITY_PARITY = YES
MIGRATION_PHASE = CLOSED
NEXT = REMOTE_QUALIFICATION_AND_RELEASE_GATE_REVIEW
```

Do not push.
