# Final Residual Ownership and Repository Hygiene Review

Review date: 2026-09-09

## 1. Verdict

```text
FINAL_RESIDUAL_OWNERSHIP_REVIEW = REPAIRED_AND_PASS
PHYSICAL_OWNERSHIP_MIGRATION_COMPLETE = YES

DUPLICATE_BUSINESS_IMPLEMENTATIONS = 0
UNRESOLVED_RESIDUALS = 0
MIGRATION_RESIDUES_FIXED = 2

LEGITIMATE_COMPATIBILITY_FACADES = 189
LEGITIMATE_RUNTIME_ENTRYPOINTS = 4
LEGITIMATE_FOUNDATION_MODULES = 10

CANONICAL_TO_COMPATIBILITY_IMPORTS = 0

SOURCE_ARCHITECTURE_MIGRATION_REOPENED = NO
CAPABILITY_PARITY_REOPENED = NO
```

The accepted capability-parity conclusion remains valid. This review found no
new missing route, API operation, dynamic entrypoint, Tool, Adapter, or product
capability. It found one bounded physical-ownership omission consisting of two
scientific-result runtime files, corrected it mechanically, and retained every
old public/runtime identity.

## 2. Review Scope and Method

- Current source was inspected with Python AST, import-graph, reverse-reference,
  public-symbol, dynamic-contract, worker/queue, and source-volume scans.
- The classified residual scope contains 85 backend files and 138 frontend
  production-path files.
- Tests are not treated as production implementations. Test-only fixture
  support under `apps/web/app/components` is reported separately.
- The complete per-file classification is recorded in:
  - `docs/agent2/residual_ownership/residual_ownership_ledger.json`
  - `docs/agent2/residual_ownership/residual_ownership_ledger.md`

## 3. Priority Conclusions

### `apps/api/mdi_api/repositories.py`

Classification: `LEGITIMATE_PUBLIC_API_AGGREGATOR`.

- Current size: 240 LOC.
- AST declarations: zero classes, functions, or async functions.
- The file consists of imports/aliases preserving repository protocols,
  implementations, bundles, private patch targets, workspace errors, and plan
  integrity helper identities.
- Canonical implementation lives under capability application ports and
  `mdi_api.infrastructure.persistence`.
- The old path remains heavily used by tests, scripts, workers, and UoW
  compatibility. Removing it now would be a public/test contract break.
- No repository implementation body remains in the file.

### `apps/api/mdi_api/db.py`

Classification: `LEGITIMATE_FOUNDATION_MODULE`.

- Current size: 1,273 LOC, unchanged by physical relocation.
- AST declarations: zero classes/functions; 63 metadata/table/group
  assignments.
- Imports are limited to SQLAlchemy schema primitives.
- It is the single SQLAlchemy `MetaData`, table, index, constraint, and
  persisted schema identity authority used by Alembic, canonical persistence
  repositories, direct runtime queries, and schema tests.
- Moving or splitting it would risk metadata/table identity and migration
  compatibility without improving implementation ownership. Repository,
  transaction, application, service, and transport behavior are absent.

### `apps/api/mdi_api/scientific_results/queue.py`

Classification after repair: `LEGITIMATE_COMPATIBILITY_FACADE`.

- Before this review it still held the concrete disabled/in-memory/RQ queue
  implementations and settings factory, contrary to the frozen
  `scientific_results/* -> application + infrastructure + shim` disposition.
- Canonical authority is now
  `mdi_api.infrastructure.scientific_results.queue`.
- The old module is a three-line true re-export; all six queue symbols preserve
  Python object identity.
- The persisted handler remains
  `mdi_api.scientific_results.worker.run_queued_result_projection`; the queue
  remains `mdi-agent-results`.
- `scientific_results/worker.py` itself is separately classified
  `LEGITIMATE_RUNTIME_ENTRYPOINT`, because its frozen dotted path is persisted
  and dynamically resolved.

## 4. Repaired Residue

| Legacy path | Previous problem | Canonical owner | Final disposition |
|---|---|---|---|
| `mdi_api.scientific_results.queue` | Concrete queue adapters/factory remained in compatibility package | `mdi_api.infrastructure.scientific_results.queue` | true compatibility re-export |
| `mdi_api.scientific_results.reconciler` | Concrete reconciliation service remained in compatibility package | `mdi_api.infrastructure.scientific_results.reconciler` | true compatibility re-export |

`mdi_api.research_agent.recovery` now imports both implementations from their
canonical infrastructure owners. No behavior, signature, queue name, handler
string, job ID, transaction boundary, or result identity changed.

## 5. Classification Summary

| Classification | Count | Typical contents |
|---|---:|---|
| `LEGITIMATE_CANONICAL_AUTHORITY` | 8 | retained single-owner product/runtime capabilities not assigned a facade move |
| `LEGITIMATE_RUNTIME_ENTRYPOINT` | 4 | ASGI app and frozen RQ dotted-path entrypoints |
| `LEGITIMATE_COMPATIBILITY_FACADE` | 189 | Python aliases/re-exports and frontend legacy component re-exports |
| `LEGITIMATE_PUBLIC_API_AGGREGATOR` | 7 | repository/package export surfaces |
| `LEGITIMATE_FOUNDATION_MODULE` | 10 | schema, configuration, transaction-support, identity and shared contract foundations |
| `TEMPORARY_COMPATIBILITY_WITH_JUSTIFICATION` | 5 | bounded provider catalogue placement plus four test-only frontend fixture helpers |
| `MIGRATION_RESIDUE_REQUIRING_FIX` | 0 after repair | none |
| `UNRESOLVED` | 0 | none |

The provider-connection module remains the sole implementation authority behind
the existing bounded B0-6 provider catalogue edge. It is explicit compatibility
debt, not a duplicate implementation and not a newly introduced migration
exception.

## 6. Frontend Residual Review

```text
app/components non-test source files = 138
pure compatibility re-exports = 134
test-only fixture support files = 4
production implementation bodies = 0
canonical -> app/components imports = 0
```

The four fixture files are referenced only by colocated tests. They do not own
production behavior and are not imported by routes, features, shared modules,
or scientific viewers.

```text
LEGACY_TEST_COLOCATION_DEBT = YES
BLOCKING = NO
```

There are 98 colocated frontend test files (19,370 LOC). Moving them solely for
directory aesthetics would create test-path churn without changing product
ownership, so this review leaves them intact.

## 7. Duplicate and Direction Checks

- No legacy file and canonical file both retain the same business
  implementation body.
- Same-name AST candidates were inspected; the only general name collision was
  unrelated `summarize_plan` behavior in distinct Phase 1 and Phase 2 scopes.
- Canonical backend layers have zero imports of the enumerated compatibility
  modules.
- Frontend `features`, `scientific-viewers`, and `shared` have zero imports of
  `app/components` compatibility surfaces.
- Legacy facades import canonical owners; the reverse direction is absent.

## 8. Source-Volume Sanity

Source volume was used only as an anomaly detector.

```text
Frontend legacy production paths:
36,417 LOC at physical-migration baseline
270 LOC current, including 130 LOC of test-only fixture support

Frontend canonical features/viewers/shared:
36,479 LOC current

Backend manifest legacy groups:
25,799 LOC at physical-migration baseline
771 LOC current after repair

Backend canonical application/domain/infrastructure/bootstrap/transport:
31,931 LOC current
```

The contraction is explained by implementation transfer to canonical owners,
not code loss. `db.py` remains stable by design as the schema foundation.

## 9. Runtime and Public Identity

```text
HANDLER_RESOLUTION = 6/6
QUEUE_IDENTITY = PASS
QUEUE_NAMES = 6 unchanged
TOOL_IDS = 62 unchanged
ADAPTER_IDS = 50 unchanged
PUBLIC_SYMBOL_IDENTITY = preserved for repaired queue/reconciler surfaces
```

The four B0-6 allowlisted edges remain the same bounded pre-existing
provider/research/LLM boundaries. No allowlist entry was added for this repair.

## 10. Verification

- Python compile of changed scientific-result/recovery modules: PASS.
- Ruff on changed Python/test files: PASS.
- Focused queue/reconciler/worker tests: 25 passed.
- Scientific-result legacy/canonical symbol identity: PASS.
- Architecture guard: PASS, forbidden edges 0, allowlisted edges 4.
- Architecture report: PASS, cycles 0, canonical-to-compatibility 0,
  handlers 6/6, queue identity PASS, Tools 62, Adapters 50.
- `git diff --check`: PASS.
- Broad capability parity and broad product suites were not rerun because the
  complete parity audit is accepted and the repair is a behavior-preserving
  ownership relocation covered by focused tests.

## 11. Hard Invariants

```text
API_CONTRACT_CHANGED = NO
AUTHORIZATION_CHANGED = NO
DATABASE_SCHEMA_CHANGED = NO
ALEMBIC_CHANGED = NO
TRANSACTION_SEMANTICS_CHANGED = NO
PERSISTED_IDENTITY_CHANGED = NO
QUEUE_IDENTITY_CHANGED = NO
HANDLER_IDENTITY_CHANGED = NO
TOOL_IDENTITY_CHANGED = NO
ADAPTER_IDENTITY_CHANGED = NO
SCIENTIFIC_AUTHORITY_CHANGED = NO
UI_BEHAVIOR_CHANGED = NO
RUNTIME_OR_USER_DATA_CHANGED = NO
HISTORICAL_OR_QUALIFICATION_EVIDENCE_CHANGED = NO
```

## 12. Closeout

```text
SOURCE_ARCHITECTURE_MIGRATION_COMPLETE = YES
PHYSICAL_OWNERSHIP_MIGRATION_COMPLETE = YES
FULL_PRE_POST_CAPABILITY_PARITY = YES
MIGRATION_PHASE = CLOSED

NEXT = REMOTE_QUALIFICATION_AND_RELEASE_GATE_REVIEW
PUSHED = NO
```
