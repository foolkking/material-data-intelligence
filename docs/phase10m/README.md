# Phase 10M Unified Scientific Workspace

Status: Phase 10M-1 through Phase 10M-3 are archived. Phase 10M-4 typed
Artifact Gallery and scientific viewer integration is complete at corrected
implementation `6287785c` with exact-SHA CI `30751689618` success;
completion-record and queue-archive exact-SHA CI remain required.

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
19. [M3 canonical selection](phase10m3_canonical_selection.md)
20. [M3 identity compatibility](phase10m3_identity_compatibility.md)
21. [M3 panel subscriptions](phase10m3_panel_subscriptions.md)
22. [M3 URL navigation](phase10m3_url_navigation.md)
23. [M3 Inspector](phase10m3_inspector.md)
24. [M3 accessibility/performance/security](phase10m3_accessibility_performance_security.md)
25. [M3 evidence](phase10m3_evidence.md)
26. [M4 Artifact Gallery](phase10m4_artifact_gallery.md)
27. [M4 renderer registry](phase10m4_renderer_registry.md)
28. [M4 scientific viewers](phase10m4_scientific_viewers.md)
29. [M4 selection integration](phase10m4_selection_integration.md)
30. [M4 WebGL lifecycle](phase10m4_webgl_lifecycle.md)
31. [M4 accessibility/performance/security](phase10m4_accessibility_performance_security.md)
32. [M4 evidence](phase10m4_evidence.md)
33. [M4 completion state](phase10m4_completion.md)
34. [M5 reviewer gate](phase10m5_next_scope.md)

## Status vocabulary

- **CONFIRMED CURRENT FACT**: verified in current source, schema, migration, tests, or current browser replay.
- **CONFIRMED CURRENT LIMITATION**: verified absence or bounded behavior in the current product.
- **PROPOSED PHASE 10M DECISION**: exact production change for a future Phase 10M implementation.
- **REVIEWER-SEALED RECOMMENDATION**: architecture choice presented for approval; implementation agents may not redesign it.
- **UNRESOLVED BLOCKER**: none affecting Phase 10M-1.
- **FUTURE SCOPE**: Phase 10N or later work excluded from Phase 10M.

Phase 10M-0 remains the sealed architecture authority. M1 owns the persisted
domain and API, M2 owns the metadata shell, and M3 activates exact canonical
selection. M4 adds application-owned exact contract-to-renderer mapping,
metadata-first Gallery loading, existing viewer integration, and bounded WebGL
lifecycle without changing those contracts. M5 remains reviewer-gated.
