# Phase 10M Unified Scientific Workspace

Status: Phase 10M-1 through Phase 10M-6 are archived. Phase 10M-7 corrected
entry, acceptance reconciliation, integration closure, and implementation
exact-SHA CI are complete. Completion-record and queue-archive exact-SHA CI
remain. Phase 10N-0 is reviewer-gated, not queued, and not executable.

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
34. [M5 entry audit](phase10m5_report_recipe_entry_audit.md)
35. [M5 authority map](phase10m5_report_recipe_authority_map.md)
36. [M5 composition contracts](phase10m5_composition_contracts.md)
37. [M5 Report content](phase10m5_report_content_contract.md)
38. [M5 Recipe manifest](phase10m5_recipe_replay_manifest.md)
39. [M5 source eligibility](phase10m5_source_eligibility_matrix.md)
40. [M5 API](phase10m5_api_contract.md)
41. [M5 Workspace UI](phase10m5_workspace_ui_contract.md)
42. [M5 export](phase10m5_export_contract.md)
43. [M5 compatibility/failures](phase10m5_compatibility_and_failure_matrix.md)
44. [M5 security/authorization](phase10m5_security_and_authorization.md)
45. [M5 acceptance/evidence](phase10m5_acceptance_evidence_map.md)
46. [M5 completion state](phase10m5_completion.md)
47. [M5 completion state](phase10m5_completion.md)
48. [M6 entry audit](phase10m6_entry_audit.md)
49. [M6 state ownership](phase10m6_state_ownership.md)
50. [M6 Save and concurrency](phase10m6_save_and_concurrency.md)
51. [M6 reload and layout restoration](phase10m6_reload_and_layout_restoration.md)
52. [M6 deep link and history](phase10m6_deep_link_and_history.md)
53. [M6 Job and source recovery](phase10m6_job_and_source_recovery.md)
54. [M6 Report/Recipe recovery](phase10m6_report_recipe_recovery.md)
55. [M6 responsive/mobile/accessibility](phase10m6_responsive_mobile_accessibility.md)
56. [M6 performance and lifecycle](phase10m6_performance_and_lifecycle.md)
57. [M6 security and compatibility](phase10m6_security_and_compatibility.md)
58. [M6 acceptance/evidence](phase10m6_acceptance_evidence_map.md)
59. [M7 reviewer gate](phase10m6_next_scope.md)
60. [M7 corrected entry audit](phase10m7_entry_audit.md)
61. [M7 acceptance reconciliation](phase10m7_acceptance_reconciliation.md)
62. [M7 integration scenarios](phase10m7_integration_scenario_matrix.md)
63. [M7 API/service closure](phase10m7_api_service_closure.md)
64. [M7 browser/mobile/accessibility](phase10m7_browser_mobile_accessibility.md)
65. [M7 performance/lifecycle/security](phase10m7_performance_lifecycle_security.md)
66. [M7 acceptance/evidence](phase10m7_acceptance_evidence_map.md)
67. [Final capability matrix](phase10m_final_capability_matrix.md)
68. [Final known limitations](phase10m_final_known_limitations.md)
69. [Prepared completion record](phase10m_completion.md)
70. [Phase 10N-0 reviewer gate](phase10n0_next_scope.md)

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
lifecycle without changing those contracts. M5 reuses existing Report/Recipe
persistence for deterministic composition and has no execution or LLM authority.
M6 closes explicit durable Save, deterministic reload, exact navigation,
persisted Job/source recovery, finalized delivery recovery, session-draft
honesty, and responsive/accessibility behavior without changing prior
contracts. M7 reconciles its canonical registry and closes current integration,
browser, service, evidence, identity-continuity, lifecycle, and Phase 10M
documentation without adding product authority.
