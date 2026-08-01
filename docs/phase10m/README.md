# Phase 10M Unified Scientific Workspace

Status: Phase 10M-1 implementation is in progress. Contracts, migration,
repositories, explicit historical projection, and additive APIs are present in
the worktree; exact-SHA CI, service-backed evidence, completion, and queue
archive remain required before this phase can be called archived.

## Reading order

1. [Fact audit](phase10m0_workspace_fact_audit.md)
2. [Information architecture](phase10m0_workspace_information_architecture.md)
3. [Domain contract proposal](phase10m0_workspace_domain_contract_proposal.md)
4. [Persistence, API, and migration decision](phase10m0_workspace_persistence_api_migration_decision.md)
5. [Decision log and execution lock](phase10m_execution_lock.md)
6. [Implementation backlog](phase10m_implementation_backlog.md)
7. [Acceptance and test plan](phase10m_acceptance_and_test_plan.md)
8. [Execution manifest](phase10m_execution_manifest.md)
9. [M1 domain contract](phase10m1_workspace_domain_contract.md)
10. [M1 persistence](phase10m1_workspace_persistence.md)
11. [M1 API](phase10m1_workspace_api.md)
12. [M1 historical projection](phase10m1_historical_job_projection.md)
13. [M1 evidence](phase10m1_evidence.md)

## Status vocabulary

- **CONFIRMED CURRENT FACT**: verified in current source, schema, migration, tests, or current browser replay.
- **CONFIRMED CURRENT LIMITATION**: verified absence or bounded behavior in the current product.
- **PROPOSED PHASE 10M DECISION**: exact production change for a future Phase 10M implementation.
- **REVIEWER-SEALED RECOMMENDATION**: architecture choice presented for approval; implementation agents may not redesign it.
- **UNRESOLVED BLOCKER**: none affecting Phase 10M-1.
- **FUTURE SCOPE**: Phase 10N or later work excluded from Phase 10M.

Phase 10M-0 remains the sealed architecture authority. Phase 10M-1 is the
sole active implementation task. The Workspace page and M2 presentation
surface are intentionally deferred.
