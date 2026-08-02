# Phase 10M Unified Scientific Workspace

Status: Phase 10M-1 is archived. Phase 10M-2 Workspace shell implementation is
active and its exact-SHA lifecycle remains required before archive.

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
14. [M2 Workspace shell](phase10m2_workspace_shell.md)
15. [M2 route and navigation](phase10m2_route_and_navigation.md)
16. [M2 state UI](phase10m2_workspace_state_ui.md)
17. [M2 responsive/accessibility](phase10m2_responsive_accessibility.md)
18. [M2 evidence](phase10m2_evidence.md)

## Status vocabulary

- **CONFIRMED CURRENT FACT**: verified in current source, schema, migration, tests, or current browser replay.
- **CONFIRMED CURRENT LIMITATION**: verified absence or bounded behavior in the current product.
- **PROPOSED PHASE 10M DECISION**: exact production change for a future Phase 10M implementation.
- **REVIEWER-SEALED RECOMMENDATION**: architecture choice presented for approval; implementation agents may not redesign it.
- **UNRESOLVED BLOCKER**: none affecting Phase 10M-1.
- **FUTURE SCOPE**: Phase 10N or later work excluded from Phase 10M.

Phase 10M-0 remains the sealed architecture authority. M1 owns the persisted
domain and API. M2 adds only the route and metadata shell; exact selection and
typed scientific rendering remain M3 and M4 scope.
