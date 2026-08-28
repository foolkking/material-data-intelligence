# Agent-2.0 Phase 14 — Full Platform Coverage Matrix

Qualification date: 2026-08-28

Status vocabulary: `PASS`, `N/A`, `NOT_QUALIFIED`. A surface is marked
`PASS` only when a persisted contract, deterministic regression, service-backed
run, or authenticated browser capture provides concrete evidence.

| Area | Entry point / authority | Desktop | Mobile | Service-backed | Security / historical | Regression evidence | Status |
|---|---|---:|---:|---:|---:|---:|---|
| Authentication | `/auth/login`, authenticated Chromium | PASS | PASS | PASS | project session | API/browser smoke | PASS |
| Projects / authorization | `/projects`, `require_project_access` | PASS | PASS | PASS | cross-project tests | `test_project_access.py` | PASS |
| Data Platform | `/api/projects/{project_id}/scientific-objects`, Data UI | PASS | PASS | PASS | archive-aware | Phase 12/13 acceptance | PASS |
| ScientificObject discovery | `scientific_objects` | PASS | PASS | PASS | project scoped | Agent2 API/domain tests | PASS |
| Version history | `scientific_object_versions` | PASS | PASS | PASS | exact refs | Phase 12 lifecycle evidence | PASS |
| Ingestion / storage | `/datasets/upload`, MinIO | PASS | N/A | PASS | checksum scoped | Phase 13 service upload tests | PASS |
| Re-ingestion / v2 | `/api/scientific-objects/{id}/versions` | PASS | N/A | PASS | immutable v1/v2 | Phase 12 production bridge | PASS |
| Dataset typed query | `.../versions/{version}/query` | PASS | PASS | PASS | bounded/no SQL | Dataset explorer tests/browser | PASS |
| Stable sample selection | `sample_id` / semantic locator | PASS | PASS | PASS | exact object/version | Dataset handoff evidence | PASS |
| Data → Research | Data selection → Research route | PASS | PASS | PASS | exact context refs | Phase 12/13 browser evidence | PASS |
| Research Timeline | `/projects/{id}/research` | PASS | PASS | PASS | explicit Turn relation | Research page tests | PASS |
| ResearchTurn / Context | `research_turns`, snapshots | PASS | PASS | PASS | exact source refs | Agent2 contract tests | PASS |
| Capability eligibility | trusted Pack registry | PASS | N/A | PASS | fail-closed | Phase 11 Pack tests | PASS |
| Capability planning | `/planner/analysis-plans/{id}` | PASS | N/A | PASS | validated plan | Agent2 planning tests | PASS |
| Job / worker | Redis/RQ + `jobs` | PASS | N/A | PASS | terminal ownership | service-backed 19/19 | PASS |
| ToolCall / Artifact | `/jobs/{id}/tool-calls`, MinIO | PASS | N/A | PASS | project scoped | Phase 2–13 tests | PASS |
| ScientificResult | `/api/research/turns/{id}/result` | PASS | PASS | PASS | exact source refs | Agent2 result tests | PASS |
| Interpretation | `/api/research/turns/{id}/interpretation` | PASS | PASS | PASS | grounding fail-closed | Phase 13 grounding tests | PASS |
| Scientific Presentation | deterministic bounded compiler | PASS | PASS | PASS | no mutation | 25 frontend / 85 backend | PASS |
| Structure Viewer | exact-version viewer route | PASS | PASS | PASS | zero recompute | viewer/service tests | PASS |
| Band / DOS Viewer | persisted electronic artifacts | PASS | PASS | PASS | exact artifact refs | Phase 10N5 service tests | PASS |
| Scientific Table / Materials Explorer | Dataset table projection | PASS | PASS | PASS | stable row identity | Dataset UI tests | PASS |
| Figure | persisted Artifact descriptor | PASS | PASS | PASS | no rerun | presentation tests | PASS |
| Evidence | Result → ToolCall/Artifact/source | PASS | PASS | PASS | cross-project fail-closed | workspace/evidence tests | PASS |
| Scientific Report | `/api/scientific-reports/{id}` | PASS | PASS | PASS | snapshot exact refs | report tests/browser capture | PASS |
| Project History | `/projects/{id}/history` | PASS | PASS | PASS | explicit `researchTurnId` | history tests | PASS |
| Historical Result reopening | history → exact Turn/Result | PASS | PASS | PASS | v1 preserved | Phase 12/13 evidence | PASS |
| Historical Viewer / Report | exact source refs | PASS | PASS | PASS | archived access | archive/report tests | PASS |
| Archive / Restore | object/run lifecycle API/UI | PASS | PASS | PASS | no version creation | archive final evidence | PASS |
| Exact Result reuse | existing Result identity | PASS | PASS | PASS | zero scientific delta | Agent2 reuse regression | PASS |
| Capability Packs | `core.structure`, `core.electronic`, `core.data`, `core.trajectory`, `core.other` | PASS | N/A | PASS | no raw Tool/UI injection | Pack regression | PASS |
| Unsupported execution | eligibility rejection | PASS | N/A | PASS | zero child records | Silicon regression | PASS |
| Desktop UX | authenticated Chromium 1280×720 | PASS | N/A | N/A | console clean | phase13 captures | PASS |
| Mobile UX | authenticated Chromium 390×844 | N/A | PASS | N/A | overflow zero | mobile capture | PASS |
| Runtime topology | `/health/runtime` | N/A | N/A | PASS | truthful backend report | live health check | PASS |
| CI qualification | `.github/workflows/ci.yml` | N/A | N/A | PASS | exact SHA | P13 CI history/current run | PASS |

## Cross-surface identity ledger

The qualified paths preserve the following authorities:

```text
Project → ScientificObject → ScientificObjectVersion
Dataset row → sample_id / semantic locator
Research handoff → ResearchTurn → ContextSnapshot
Turn → Job → ToolCall → Artifact → ScientificResult
ScientificResult → Presentation / Viewer / Evidence / Report
History → explicit researchTurnId → exact Turn
```

No frontend-only identifier is treated as scientific authority. The legacy
`job_agent2_<uuid>` parser remains compatibility-only for historical rows that
lack a persisted relation.
