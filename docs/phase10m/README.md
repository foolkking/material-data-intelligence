# Phase 10M Unified Scientific Workspace

Status: Phase 10M-0 audit and information architecture are sealed for reviewer approval. No Phase 10M production implementation is included.

## Reading order

1. [Fact audit](phase10m0_workspace_fact_audit.md)
2. [Information architecture](phase10m0_workspace_information_architecture.md)
3. [Domain contract proposal](phase10m0_workspace_domain_contract_proposal.md)
4. [Persistence, API, and migration decision](phase10m0_workspace_persistence_api_migration_decision.md)
5. [Decision log and execution lock](phase10m_execution_lock.md)
6. [Implementation backlog](phase10m_implementation_backlog.md)
7. [Acceptance and test plan](phase10m_acceptance_and_test_plan.md)
8. [Execution manifest](phase10m_execution_manifest.md)

## Status vocabulary

- **CONFIRMED CURRENT FACT**: verified in current source, schema, migration, tests, or current browser replay.
- **CONFIRMED CURRENT LIMITATION**: verified absence or bounded behavior in the current product.
- **PROPOSED PHASE 10M DECISION**: exact production change for a future Phase 10M implementation.
- **REVIEWER-SEALED RECOMMENDATION**: architecture choice presented for approval; implementation agents may not redesign it.
- **UNRESOLVED BLOCKER**: none affecting Phase 10M-1.
- **FUTURE SCOPE**: Phase 10N or later work excluded from Phase 10M.

Production source, dependencies, lockfiles, migrations, APIs, frontend behavior, and `TASKS.md` are unchanged by Phase 10M-0.
