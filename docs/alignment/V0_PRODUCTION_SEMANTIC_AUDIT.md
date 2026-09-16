# V0 Production Semantic Code-Diff Audit

- Repository: `E:\1project\mdi-b0-5a1`
- HEAD: `2727e94ba6adaaf0c6ff9914f8137d130b34c777`
- Modified production files reviewed: **56**
- Confirmed remaining reviewer/expert scope-drift code: **0**
- Authority-boundary defects found/fixed: **1 / 1**
- Secondary LLM review runtime calls: **0**
- J evaluation production dependencies: **0**
- J frozen evidence modified: **NO**

## Audit table

| File | H/I/J change role | Decision | Current behavior / correction |
|---|---|---|---|
| `apps/api/alembic/versions/0033_scientific_knowledge.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/application/interpretation/grounding.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds or carries deterministic/structured ClaimSupportAssessment into one grounded interpretation path with bounded repair and fail-closed validation. |
| `apps/api/mdi_api/application/scientific_knowledge/__init__.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/application/scientific_knowledge/ports.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/application/scientific_knowledge/service.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/application/scientific_knowledge/synthesis.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/application/scientific_reasoning/__init__.py` | `TERMINOLOGY_CORRECTION` | **MODIFY** | Package is named as a deterministic claim-support assessment package; behavior is unchanged. |
| `apps/api/mdi_api/application/scientific_reasoning/assessment.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds or carries deterministic/structured ClaimSupportAssessment into one grounded interpretation path with bounded repair and fail-closed validation. |
| `apps/api/mdi_api/application/scientific_reports/assembler.py` | `VALID_V0_EVOLUTION` | **KEEP** | Preserves report composition, grounding, literature citations and presentation/provenance projections without creating report authority. |
| `apps/api/mdi_api/application/scientific_reports/grounded.py` | `VALID_V0_EVOLUTION` | **KEEP** | Preserves report composition, grounding, literature citations and presentation/provenance projections without creating report authority. |
| `apps/api/mdi_api/application/scientific_reports/grounding.py` | `VALID_V0_EVOLUTION` | **KEEP** | Preserves report composition, grounding, literature citations and presentation/provenance projections without creating report authority. |
| `apps/api/mdi_api/db.py` | `VALID_V0_EVOLUTION` | **KEEP** | Registers H persistence/routes/runtime wiring while preserving existing ScientificResult, Report, Context and lifecycle authorities. |
| `apps/api/mdi_api/domain/interpretation/contracts.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds or carries deterministic/structured ClaimSupportAssessment into one grounded interpretation path with bounded repair and fail-closed validation. |
| `apps/api/mdi_api/domain/scientific_knowledge/__init__.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/domain/scientific_knowledge/contracts.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/domain/scientific_reasoning/__init__.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds or carries deterministic/structured ClaimSupportAssessment into one grounded interpretation path with bounded repair and fail-closed validation. |
| `apps/api/mdi_api/domain/scientific_reasoning/contracts.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds or carries deterministic/structured ClaimSupportAssessment into one grounded interpretation path with bounded repair and fail-closed validation. |
| `apps/api/mdi_api/domain/scientific_reports/contracts.py` | `VALID_V0_EVOLUTION` | **KEEP** | Preserves report composition, grounding, literature citations and presentation/provenance projections without creating report authority. |
| `apps/api/mdi_api/infrastructure/interpretation/service.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds or carries deterministic/structured ClaimSupportAssessment into one grounded interpretation path with bounded repair and fail-closed validation. |
| `apps/api/mdi_api/infrastructure/persistence/agent2_bundle.py` | `VALID_V0_EVOLUTION` | **KEEP** | Registers H persistence/routes/runtime wiring while preserving existing ScientificResult, Report, Context and lifecycle authorities. |
| `apps/api/mdi_api/infrastructure/persistence/scientific_knowledge.py` | `VALID_V0_EVOLUTION` | **KEEP** | Supports the H/I/J-era bounded scientific product evolution; semantic review found no reviewer/expert runtime behavior. |
| `apps/api/mdi_api/infrastructure/scientific_knowledge/__init__.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/infrastructure/scientific_knowledge/providers.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/api/mdi_api/infrastructure/scientific_reports/service.py` | `AUTHORITY_BOUNDARY_CORRECTION` | **MODIFY** | Report generation persists the interpretation as a bounded communication input; its manifest entry is now explicitly INTERPRETATION/DERIVED_SUMMARY rather than a ScientificResult. |
| `apps/api/mdi_api/main.py` | `VALID_V0_EVOLUTION` | **KEEP** | Registers H persistence/routes/runtime wiring while preserving existing ScientificResult, Report, Context and lifecycle authorities. |
| `apps/api/mdi_api/research_agent/context/manifest.py` | `AUTHORITY_BOUNDARY_CORRECTION` | **MODIFY** | Context manifests accept an explicit non-authoritative INTERPRETATION kind and reject incompatible authority/kind combinations. |
| `apps/api/mdi_api/research_agent/context/provenance.py` | `VALID_V0_EVOLUTION` | **KEEP** | Preserves bounded ContextSnapshot provenance, source classes, exact identities and evidence-state projections. |
| `apps/api/mdi_api/research_agent/context/schemas.py` | `AUTHORITY_BOUNDARY_CORRECTION` | **MODIFY** | Context manifests accept an explicit non-authoritative INTERPRETATION kind and reject incompatible authority/kind combinations. |
| `apps/api/mdi_api/research_agent/lifecycle.py` | `VALID_V0_EVOLUTION` | **KEEP** | Maintains durable Research lifecycle, structured provider ingress, result reuse, source/version display and bounded autonomy integration. |
| `apps/api/mdi_api/research_agent/llm/structured_client.py` | `VALID_V0_EVOLUTION` | **KEEP** | Maintains durable Research lifecycle, structured provider ingress, result reuse, source/version display and bounded autonomy integration. |
| `apps/api/mdi_api/research_agent/strategy/evidence.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds bounded evidence-state, evidence-gap, hypothesis and literature strategy semantics without direct arbitrary tool execution. |
| `apps/api/mdi_api/research_agent/strategy/schemas.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds bounded evidence-state, evidence-gap, hypothesis and literature strategy semantics without direct arbitrary tool execution. |
| `apps/api/mdi_api/research_agent/strategy/validation.py` | `VALID_V0_EVOLUTION` | **KEEP** | Adds bounded evidence-state, evidence-gap, hypothesis and literature strategy semantics without direct arbitrary tool execution. |
| `apps/api/mdi_api/transport/routers/agent2.py` | `VALID_V0_EVOLUTION` | **KEEP** | Maintains durable Research lifecycle, structured provider ingress, result reuse, source/version display and bounded autonomy integration. |
| `apps/api/mdi_api/transport/routers/research.py` | `VALID_V0_EVOLUTION` | **KEEP** | Maintains durable Research lifecycle, structured provider ingress, result reuse, source/version display and bounded autonomy integration. |
| `apps/api/mdi_api/transport/routers/scientific_knowledge.py` | `VALID_V0_EVOLUTION` | **KEEP** | Implements bounded scholarly literature identity, snapshot, evidence, provider access, grounding and report/context integration. |
| `apps/web/app/globals.css` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/app/lib/agent2-execution-api.ts` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/app/lib/agent2-research-api.ts` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/app/lib/planner-api.ts` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/app/lib/scientific-knowledge-api.ts` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/app/lib/scientific-presentation.ts` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/features/notifications/NotificationCenterPage.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/features/reports/ReportPages.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/features/research/Agent2ScientificPresentation.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/features/research/LiteratureEvidencePanel.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/features/research/ResearchExecutionActivity.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/features/research/ResearchPages.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/features/research/ScientificPresentationBlocks.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/features/tasks/TaskCenterPage.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/next-env.d.ts` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/scientific-viewers/ScientificViewerAdapter.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/scientific-viewers/composition-space/CompositionSpaceExplorerPanel.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/shared/layout/ProductShell.tsx` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `apps/web/shared/product-labels.ts` | `VALID_V0_EVOLUTION` | **KEEP** | Scientist-facing Research/Workbench/literature/provenance presentation and typed client contracts; no scientific computation or reviewer control path. |
| `services/llm/mdi_llm/providers.py` | `VALID_V0_EVOLUTION` | **KEEP** | Allowlist includes the H literature-synthesis purpose alongside existing bounded LLM purposes; no critic/judge purpose. |

## Semantic conclusions

- H literature identity, snapshot, evidence scope, provider allowlist, citation lineage and report integration remain valid V0 evolution.
- I ClaimSupportAssessment remains a deterministic/structured scientific guard. It is not a reviewer Agent and does not add a second scientific truth authority.
- STRICT_PROVIDER is one primary grounded interpretation provider path with strict structured output, deterministic grounding, and at most one bounded contract repair. It is not a second scientific reviewer.
- J scripts, packets, hashes and frozen responses are evaluation-only and are not imported by `apps/` or `services/` runtime code.
- One real defect was corrected: report interpretation prose was previously labeled as `SCIENTIFIC_RESULT`; it is now `INTERPRETATION` with `DERIVED_SUMMARY` authority and manifest compatibility checks.

## Production LLM call-site inventory

| Responsibility | Confirmed runtime call sites | Result |
|---|---|---|
| Research orchestration | intent extraction, capability planning, dependency planning, research-turn strategy | KEEP; structured planning only |
| Scientific interpretation | `strict_provider_interpret` / grounded interpretation service | KEEP; one primary provider call plus at most one bounded contract repair |
| Report composition | report composer client/service | KEEP; report remains communication output |
| Literature synthesis | bounded literature synthesis provider | KEEP; evidence-grounded and source-validated |
| Scientific reviewer / critic / judge | none | `0` active calls |

The checked runtime roots under `apps/` and `services/` contain no imports of
J review packets, reviewer scores, reviewer assignments, or scientist-evaluation
runtime modules.
