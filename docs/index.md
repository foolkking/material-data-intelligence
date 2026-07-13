# 文档索引

## Phase 10F-25 Clipping, Cell, and Camera Controls

`phase10f/phase10f25_clipping_cell_camera.md` is the implementation entry point. The clipping, camera, cell display, security, and evidence documents define bounded renderer-local view controls and their three-browser closure.

## Phase 10F-24 Supercell Productization

`phase10f/phase10f24_supercell_productization.md` is the entry point. The adjacent display-contract, identity, bond-replication, performance, persistence, security, evidence, and readiness documents record the implementation and closure.

本目录保存“材料数据智能分析与可视化平台”的分阶段设计文档。阅读顺序建议从 Phase 0 到 Phase 12；`docs/11_MATERIAL_DOMAIN_EXTENSIONS.md` 是专业材料领域扩展补充文件，不改变 `docs/12_MVP_ROADMAP.md` 的 Phase 11 开发路线编号。

## 核心设计文档

| 文件 | 主题 |
|---|---|
| [`phase10f/phase10f25_clipping_cell_camera.md`](phase10f/phase10f25_clipping_cell_camera.md) | Axis clipping, cell/axes display, camera presets, and readiness |
| [`phase10f/phase10f25_clipping_contract.md`](phase10f/phase10f25_clipping_contract.md) | Bounded clipping semantics and picking gate |
| [`phase10f/phase10f25_camera_contract.md`](phase10f/phase10f25_camera_contract.md) | Deterministic presets and inert camera state |
| [`phase10f/phase10f25_cell_display_contract.md`](phase10f/phase10f25_cell_display_contract.md) | Unit cell, supercell boundary, and lattice axes |
| [`phase10f/phase10f25_security.md`](phase10f/phase10f25_security.md) | View-control trust and resource boundaries |
| [`phase10f/phase10f25_evidence.md`](phase10f/phase10f25_evidence.md) | Chromium, Firefox, WebKit, and mobile evidence |
| [`phase10f/evidence/phase10f25_clipping_cell_camera/`](phase10f/evidence/phase10f25_clipping_cell_camera/) | Browser matrices, contracts, screenshots, hashes, and audits |
| [`00_PROJECT_GOAL.md`](00_PROJECT_GOAL.md) | 项目目标、边界、核心用户、MVP 和长期方向 |
| [`01_PRODUCT_REQUIREMENTS.md`](01_PRODUCT_REQUIREMENTS.md) | 产品需求、用户角色、使用流程和验收标准 |
| [`02_SYSTEM_ARCHITECTURE.md`](02_SYSTEM_ARCHITECTURE.md) | 总体架构、服务边界、同步/异步边界和部署拓扑 |
| [`03_FRONTEND_WORKSPACE_DESIGN.md`](03_FRONTEND_WORKSPACE_DESIGN.md) | Phase 9C AI 分析助手工作台：顶部全局栏、左侧数据上下文、主体三 Tab |
| [`03A_FRONTEND_COMPONENT_SPEC.md`](03A_FRONTEND_COMPONENT_SPEC.md) | Phase 9C 组件树、职责和实现边界 |
| [`03B_FRONTEND_STATE_AND_INTERACTION.md`](03B_FRONTEND_STATE_AND_INTERACTION.md) | Phase 9C 状态切片、主体 Tab、chunk selection、SSE 事件投影 |
| [`04_BACKEND_SERVICE_DESIGN.md`](04_BACKEND_SERVICE_DESIGN.md) | 后端 API、数据库实体、权限、错误模型和数据隔离 |
| [`05_AGENT_ORCHESTRATION_DESIGN.md`](05_AGENT_ORCHESTRATION_DESIGN.md) | Agent 编排、JSON Plan、Tool Calling 约束和审计过程 |
| [`06_TOOL_REGISTRY_AND_ADAPTER.md`](06_TOOL_REGISTRY_AND_ADAPTER.md) | Tool Registry、Adapter、Schema、Artifact、缓存和插件扩展 |
| [`07_DATA_PIPELINE_DESIGN.md`](07_DATA_PIPELINE_DESIGN.md) | 文件解析、格式识别、标准对象、Data Profile 和质量检查 |
| [`08_JOB_QUEUE_AND_CONCURRENCY.md`](08_JOB_QUEUE_AND_CONCURRENCY.md) | Job Queue、Worker Pool、SSE、缓存、降采样和资源限制 |
| [`09_ARTIFACT_AND_RECIPE_SYSTEM.md`](09_ARTIFACT_AND_RECIPE_SYSTEM.md) | Artifact、Recipe、Report、版本管理、复现和导出 |
| [`10_USER_CONFIG_AND_SECURITY.md`](10_USER_CONFIG_AND_SECURITY.md) | 用户配置、BYOK、Secret、沙箱、Prompt injection、权限和审计 |
| [`11_MATERIAL_DOMAIN_EXTENSIONS.md`](11_MATERIAL_DOMAIN_EXTENSIONS.md) | 材料结构、声子、电子结构、VASP/LAMMPS、外部生态和插件扩展 |
| [`12_MVP_ROADMAP.md`](12_MVP_ROADMAP.md) | MVP/V1/V2 范围、任务拆解、风险、验收标准和实现顺序 |
| [`13_SHARED_SCHEMA_SPEC.md`](13_SHARED_SCHEMA_SPEC.md) | 跨前端、后端、Worker、Agent 和工具注册表的共享 Schema |
| [`14_PYMATVIZ_CAPABILITY_INVENTORY.md`](14_PYMATVIZ_CAPABILITY_INVENTORY.md) | pymatviz 原始能力、平台 Tool ID、Adapter、Agent 任务和前端展示模块的映射清单 |
| [`15_ADAPTER_IMPLEMENTATION_PLAN.md`](15_ADAPTER_IMPLEMENTATION_PLAN.md) | BaseToolAdapter、执行流程、MVP Adapter 顺序和测试要求 |

## 持久化状态文件

持久化状态在 `../persistent/` 中维护：

| 文件 | 目的 |
|---|---|
| `PROJECT_BRIEF.md` | 长期项目目标和不可变约束 |
| `DESIGN_PROGRESS.md` | 当前阶段、已完成内容和下一步 |
| `TASK_BOARD.md` | 任务看板 |
| `ARCHITECTURE_DECISIONS.md` | 架构决策 ADR |
| `TOOL_REGISTRY_NOTES.md` | 工具注册表持续记录 |
| `OPEN_QUESTIONS.md` | 未决产品/架构/安全问题 |
| `CHANGELOG.md` | 文档变更记录 |

## Runtime Runbooks

| File | Topic |
|---|---|
| [`16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md`](16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md) | Phase 5 PostgreSQL, Redis/RQ, MinIO, Alembic, and integration-test operations |

## Phase 10F Static Structure Physics Closure

| File | Topic |
|---|---|
| [`phase10f/phase10f_static_structure_physics_closure.md`](phase10f/phase10f_static_structure_physics_closure.md) | Static structure physics closure for coordination histogram, XRD, and RDF |
| [`phase10f/phase10f_next_scope_decision_matrix.md`](phase10f/phase10f_next_scope_decision_matrix.md) | Phase 10F next-scope decision matrix |
| [`phase10f/phase10f1_next_scope_prompt.md`](phase10f/phase10f1_next_scope_prompt.md) | Copyable Phase 10F-1 prompt |
| [`phase10f/phase10f1_official_examples_direct_verification.md`](phase10f/phase10f1_official_examples_direct_verification.md) | Phase 10F-1 official examples direct verification audit |
| [`phase10f/official_examples_direct_verification/`](phase10f/official_examples_direct_verification/) | Phase 10F-1 case-selection, verification matrix, artifact, API, and security evidence |
| [`phase10f/phase10f2_next_scope_prompt.md`](phase10f/phase10f2_next_scope_prompt.md) | Copyable Phase 10F-2 coverage-gap prompt |
| [`phase10f/phase10f2_official_coverage_gap_analysis.md`](phase10f/phase10f2_official_coverage_gap_analysis.md) | Phase 10F-2 official static physics coverage-gap analysis |
| [`phase10f/phase10f2_coverage_gap_matrix.md`](phase10f/phase10f2_coverage_gap_matrix.md) | Phase 10F-2 static physics official coverage gap matrix |
| [`phase10f/phase10f2_direct_uploadable_fixture_proposal.md`](phase10f/phase10f2_direct_uploadable_fixture_proposal.md) | Phase 10F-2 direct-uploadable fixture proposal |
| [`phase10f/phase10f2_expected_contract_authoring_plan.md`](phase10f/phase10f2_expected_contract_authoring_plan.md) | Phase 10F-2 expected contract authoring plan |
| [`phase10f/phase10f3_next_scope_prompt.md`](phase10f/phase10f3_next_scope_prompt.md) | Copyable Phase 10F-3 fixture-pack planning prompt |
| [`phase10f/phase10f3_static_physics_fixture_pack_planning.md`](phase10f/phase10f3_static_physics_fixture_pack_planning.md) | Phase 10F-3 static physics direct-uploadable fixture pack planning |
| [`phase10f/phase10f3_fixture_candidate_matrix.md`](phase10f/phase10f3_fixture_candidate_matrix.md) | Phase 10F-3 fixture candidate matrix |
| [`phase10f/phase10f3_fixture_provenance_policy.md`](phase10f/phase10f3_fixture_provenance_policy.md) | Phase 10F-3 fixture provenance policy |
| [`phase10f/phase10f3_expected_contract_templates.md`](phase10f/phase10f3_expected_contract_templates.md) | Phase 10F-3 expected contract templates |
| [`phase10f/phase10f3_numeric_tolerance_policy.md`](phase10f/phase10f3_numeric_tolerance_policy.md) | Phase 10F-3 numeric tolerance policy |
| [`phase10f/phase10f3_fixture_replay_protocol.md`](phase10f/phase10f3_fixture_replay_protocol.md) | Phase 10F-3 future fixture replay protocol |
| [`phase10f/phase10f4_next_scope_prompt.md`](phase10f/phase10f4_next_scope_prompt.md) | Copyable Phase 10F-4 fixture-pack construction prompt |
| [`phase10f/phase10f4_static_physics_fixture_pack_construction.md`](phase10f/phase10f4_static_physics_fixture_pack_construction.md) | Phase 10F-4 static physics fixture pack construction |
| [`phase10f/static_physics_fixture_pack/`](phase10f/static_physics_fixture_pack/) | Phase 10F-4 candidate direct-uploadable static physics fixture pack |
| [`phase10f/phase10f5_next_scope_prompt.md`](phase10f/phase10f5_next_scope_prompt.md) | Copyable Phase 10F-5 fixture-pack replay verification prompt |
| [`phase10f/phase10f5_static_physics_fixture_pack_replay_verification.md`](phase10f/phase10f5_static_physics_fixture_pack_replay_verification.md) | Phase 10F-5 static physics fixture pack replay verification |
| [`phase10f/static_physics_fixture_pack_replay/`](phase10f/static_physics_fixture_pack_replay/) | Phase 10F-5 fixture-pack validation, replay, artifact, numeric, and security evidence |
| [`phase10f/phase10f6_next_scope_prompt.md`](phase10f/phase10f6_next_scope_prompt.md) | Copyable Phase 10F-6 fixture-pack evidence closure prompt |
| [`phase10f/phase10f6_static_physics_fixture_pack_evidence_closure.md`](phase10f/phase10f6_static_physics_fixture_pack_evidence_closure.md) | Phase 10F-6 fixture-pack evidence closure |
| [`phase10f/phase10f6_evidence_boundary_matrix.md`](phase10f/phase10f6_evidence_boundary_matrix.md) | Phase 10F-6 fixture-pack vs official PASS boundary matrix |
| [`phase10f/phase10f6_next_scope_decision_matrix.md`](phase10f/phase10f6_next_scope_decision_matrix.md) | Phase 10F-6 next-scope decision matrix |
| [`phase10f/phase10f7_next_scope_prompt.md`](phase10f/phase10f7_next_scope_prompt.md) | Copyable Phase 10F-7 advanced viewer readiness planning prompt |
| [`phase10f/phase10f7_advanced_viewer_readiness.md`](phase10f/phase10f7_advanced_viewer_readiness.md) | Phase 10F-7 advanced structure viewer readiness assessment |
| [`phase10f/phase10f7_viewer_artifact_contract_proposal.md`](phase10f/phase10f7_viewer_artifact_contract_proposal.md) | Phase 10F-7 future inert viewer artifact contract proposal |
| [`phase10f/phase10f7_renderer_architecture_assessment.md`](phase10f/phase10f7_renderer_architecture_assessment.md) | Phase 10F-7 renderer architecture assessment |
| [`phase10f/phase10f7_viewer_security_boundary.md`](phase10f/phase10f7_viewer_security_boundary.md) | Phase 10F-7 viewer security boundary |
| [`phase10f/phase10f7_viewer_input_caps.md`](phase10f/phase10f7_viewer_input_caps.md) | Phase 10F-7 viewer input and size caps |
| [`phase10f/phase10f7_viewer_routing_policy.md`](phase10f/phase10f7_viewer_routing_policy.md) | Phase 10F-7 future viewer routing policy |
| [`phase10f/phase10f7_viewer_browser_evidence_model.md`](phase10f/phase10f7_viewer_browser_evidence_model.md) | Phase 10F-7 future viewer browser evidence model |
| [`phase10f/phase10f7_viewer_readiness_matrix.md`](phase10f/phase10f7_viewer_readiness_matrix.md) | Phase 10F-7 viewer readiness matrix |
| [`phase10f/phase10f8_next_scope_prompt.md`](phase10f/phase10f8_next_scope_prompt.md) | Copyable Phase 10F-8 viewer scene artifact contract planning prompt |
| [`phase10f/phase10f8_viewer_scene_artifact_contract_planning.md`](phase10f/phase10f8_viewer_scene_artifact_contract_planning.md) | Phase 10F-8 viewer scene artifact contract planning |
| [`phase10f/phase10f8_viewer_scene_json_contract.md`](phase10f/phase10f8_viewer_scene_json_contract.md) | Phase 10F-8 inert viewer scene JSON contract |
| [`phase10f/phase10f8_viewer_scene_manifest_contract.md`](phase10f/phase10f8_viewer_scene_manifest_contract.md) | Phase 10F-8 viewer scene manifest contract |
| [`phase10f/phase10f8_viewer_scene_validation_contract.md`](phase10f/phase10f8_viewer_scene_validation_contract.md) | Phase 10F-8 viewer scene validation contract |
| [`phase10f/phase10f8_viewer_scene_security_contract.md`](phase10f/phase10f8_viewer_scene_security_contract.md) | Phase 10F-8 viewer scene security contract |
| [`phase10f/phase10f8_viewer_scene_browser_evidence_contract.md`](phase10f/phase10f8_viewer_scene_browser_evidence_contract.md) | Phase 10F-8 JSON-only browser evidence contract |
| [`phase10f/phase10f8_viewer_scene_versioning_strategy.md`](phase10f/phase10f8_viewer_scene_versioning_strategy.md) | Phase 10F-8 viewer scene versioning strategy |
| [`phase10f/phase10f8_viewer_scene_contract_readiness_matrix.md`](phase10f/phase10f8_viewer_scene_contract_readiness_matrix.md) | Phase 10F-8 viewer scene contract readiness matrix |
| [`phase10f/phase10f9_next_scope_prompt.md`](phase10f/phase10f9_next_scope_prompt.md) | Copyable Phase 10F-9 JSON preview evidence / contract fixture planning prompt |
| [`phase10f/fixtures/viewer_scene_v1/`](phase10f/fixtures/viewer_scene_v1/) | Phase 10F-9 inert viewer_scene.v1 fixture pack, manifests, and expected results |
| [`phase10f/phase10f9_viewer_scene_contract_fixture_implementation.md`](phase10f/phase10f9_viewer_scene_contract_fixture_implementation.md) | Phase 10F-9 viewer scene contract fixture and validator implementation |
| [`phase10f/phase10f9_viewer_scene_fixture_matrix.md`](phase10f/phase10f9_viewer_scene_fixture_matrix.md) | Phase 10F-9 viewer scene fixture matrix |
| [`phase10f/phase10f9_viewer_scene_validator_result.md`](phase10f/phase10f9_viewer_scene_validator_result.md) | Phase 10F-9 viewer scene validator result |
| [`phase10f/phase10f9_viewer_scene_manifest_fixtures.md`](phase10f/phase10f9_viewer_scene_manifest_fixtures.md) | Phase 10F-9 viewer scene manifest fixtures |
| [`phase10f/phase10f9_viewer_scene_security_evidence.md`](phase10f/phase10f9_viewer_scene_security_evidence.md) | Phase 10F-9 viewer scene fixture security evidence |
| [`phase10f/phase10f9_viewer_scene_evidence_closure.md`](phase10f/phase10f9_viewer_scene_evidence_closure.md) | Phase 10F-9 viewer scene evidence closure |
| [`phase10f/phase10f10_next_scope.md`](phase10f/phase10f10_next_scope.md) | Phase 10F-10 next scope note |
| [`phase10f/phase10f10_viewer_scene_json_preview_surface_implementation.md`](phase10f/phase10f10_viewer_scene_json_preview_surface_implementation.md) | Phase 10F-10 viewer_scene.v1 JSON-only preview surface implementation |
| [`phase10f/phase10f10_viewer_scene_json_preview_evidence.md`](phase10f/phase10f10_viewer_scene_json_preview_evidence.md) | Phase 10F-10 fixture-backed JSON-only preview evidence |
| [`phase10f/phase10f10_viewer_scene_preview_security_evidence.md`](phase10f/phase10f10_viewer_scene_preview_security_evidence.md) | Phase 10F-10 JSON-only preview security evidence |
| [`phase10f/phase10f10_viewer_scene_browser_api_evidence.md`](phase10f/phase10f10_viewer_scene_browser_api_evidence.md) | Phase 10F-10 frontend/API evidence boundary |
| [`phase10f/phase10f10_viewer_scene_readiness_matrix.md`](phase10f/phase10f10_viewer_scene_readiness_matrix.md) | Phase 10F-10 viewer_scene preview readiness matrix |
| [`phase10f/evidence/phase10f10_viewer_scene_json_preview/`](phase10f/evidence/phase10f10_viewer_scene_json_preview/) | Phase 10F-10 small text evidence for JSON-only preview |
| [`phase10f/phase10f11_next_scope.md`](phase10f/phase10f11_next_scope.md) | Phase 10F-11 next-scope options |
| [`phase10f/phase10f11_viewer_scene_real_browser_evidence.md`](phase10f/phase10f11_viewer_scene_real_browser_evidence.md) | Phase 10F-11 real browser evidence for viewer_scene JSON-only preview |
| [`phase10f/phase10f11_viewer_scene_browser_security_evidence.md`](phase10f/phase10f11_viewer_scene_browser_security_evidence.md) | Phase 10F-11 browser security evidence for viewer_scene preview |
| [`phase10f/phase10f11_viewer_scene_evidence_replay.md`](phase10f/phase10f11_viewer_scene_evidence_replay.md) | Phase 10F-11 real browser evidence replay command |
| [`phase10f/phase10f11_viewer_scene_readiness_matrix.md`](phase10f/phase10f11_viewer_scene_readiness_matrix.md) | Phase 10F-11 viewer_scene browser evidence readiness matrix |
| [`phase10f/evidence/phase10f11_viewer_scene_real_browser/`](phase10f/evidence/phase10f11_viewer_scene_real_browser/) | Phase 10F-11 screenshots, DOM snapshot, and network audit |
| [`phase10f/phase10f12_next_scope.md`](phase10f/phase10f12_next_scope.md) | Phase 10F-12 reviewer-selected next-scope options |
| [`phase10f/phase10f12_viewer_scene_minimal_adapter_implementation.md`](phase10f/phase10f12_viewer_scene_minimal_adapter_implementation.md) | Phase 10F-12 minimal `structure.viewer_scene` adapter implementation |
| [`phase10f/phase10f12_viewer_scene_adapter_contract_audit.md`](phase10f/phase10f12_viewer_scene_adapter_contract_audit.md) | Phase 10F-12 viewer scene adapter contract audit |
| [`phase10f/phase10f12_viewer_scene_adapter_execution_evidence.md`](phase10f/phase10f12_viewer_scene_adapter_execution_evidence.md) | Phase 10F-12 adapter execution evidence |
| [`phase10f/phase10f12_viewer_scene_adapter_security_evidence.md`](phase10f/phase10f12_viewer_scene_adapter_security_evidence.md) | Phase 10F-12 adapter security evidence |
| [`phase10f/phase10f12_viewer_scene_adapter_readiness_matrix.md`](phase10f/phase10f12_viewer_scene_adapter_readiness_matrix.md) | Phase 10F-12 viewer scene adapter readiness matrix |
| [`phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/`](phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/) | Phase 10F-12 generated adapter execution, validator, preview, and security evidence |
| [`phase10f/phase10f13_viewer_scene_live_adapter_browser_api_evidence.md`](phase10f/phase10f13_viewer_scene_live_adapter_browser_api_evidence.md) | Phase 10F-13 live adapter browser/API evidence |
| [`phase10f/phase10f13_viewer_scene_live_browser_security_audit.md`](phase10f/phase10f13_viewer_scene_live_browser_security_audit.md) | Phase 10F-13 live browser security audit |
| [`phase10f/phase10f13_viewer_schema_compatibility_audit.md`](phase10f/phase10f13_viewer_schema_compatibility_audit.md) | Phase 10F-13 old/new viewer schema compatibility audit |
| [`phase10f/phase10f13_renderer_handoff_readiness_matrix.md`](phase10f/phase10f13_renderer_handoff_readiness_matrix.md) | Phase 10F-13 renderer handoff readiness matrix |
| [`phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser/`](phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser/) | Phase 10F-13 live adapter Chrome screenshots, API captures, DOM, console, and network evidence |
| [`phase10f/phase10f14_renderer_integrated_plan.md`](phase10f/phase10f14_renderer_integrated_plan.md) | Phase 10F-14 integrated renderer plan and candidate review |
| [`phase10f/phase10f14_renderer_dependency_decision.md`](phase10f/phase10f14_renderer_dependency_decision.md) | Selected Three.js dependency decision |
| [`phase10f/phase10f14_renderer_architecture.md`](phase10f/phase10f14_renderer_architecture.md) | Validation, mapper, engine, and React architecture |
| [`phase10f/phase10f14_renderer_api_contract.md`](phase10f/phase10f14_renderer_api_contract.md) | Internal validated renderer API contract |
| [`phase10f/phase10f14_renderer_state_machine.md`](phase10f/phase10f14_renderer_state_machine.md) | Renderer state and fallback model |
| [`phase10f/phase10f14_renderer_resource_policy.md`](phase10f/phase10f14_renderer_resource_policy.md) | Renderer caps and resource policy |
| [`phase10f/phase10f14_renderer_implementation.md`](phase10f/phase10f14_renderer_implementation.md) | Minimal interactive renderer implementation |
| [`phase10f/phase10f14_renderer_lifecycle.md`](phase10f/phase10f14_renderer_lifecycle.md) | Renderer ownership, disposal, and context loss |
| [`phase10f/phase10f14_renderer_fallback_behavior.md`](phase10f/phase10f14_renderer_fallback_behavior.md) | Invalid, unsupported, initialization, and context fallback |
| [`phase10f/phase10f14_renderer_code_review.md`](phase10f/phase10f14_renderer_code_review.md) | Formal code and lifecycle review |
| [`phase10f/phase10f14_renderer_dependency_audit.md`](phase10f/phase10f14_renderer_dependency_audit.md) | Dependency and npm audit findings |
| [`phase10f/phase10f14_renderer_bundle_audit.md`](phase10f/phase10f14_renderer_bundle_audit.md) | Production bundle and lazy chunk audit |
| [`phase10f/phase10f14_renderer_contract_compatibility_audit.md`](phase10f/phase10f14_renderer_contract_compatibility_audit.md) | Canonical and Phase 10D compatibility review |
| [`phase10f/phase10f14_renderer_ui_review.md`](phase10f/phase10f14_renderer_ui_review.md) | UI and screenshot review |
| [`phase10f/phase10f14_renderer_threat_model.md`](phase10f/phase10f14_renderer_threat_model.md) | Renderer threat model and trust boundary |
| [`phase10f/phase10f14_renderer_security_review.md`](phase10f/phase10f14_renderer_security_review.md) | Injection, disclosure, and lifecycle security review |
| [`phase10f/phase10f14_renderer_dependency_security.md`](phase10f/phase10f14_renderer_dependency_security.md) | Renderer dependency security result |
| [`phase10f/phase10f14_renderer_network_isolation.md`](phase10f/phase10f14_renderer_network_isolation.md) | Renderer network-isolation evidence |
| [`phase10f/phase10f14_renderer_resource_dos_review.md`](phase10f/phase10f14_renderer_resource_dos_review.md) | GPU/resource denial-of-service review |
| [`phase10f/phase10f14_renderer_browser_evidence.md`](phase10f/phase10f14_renderer_browser_evidence.md) | Real Chrome, interaction, WebGL, console, and network evidence |
| [`phase10f/phase10f14_renderer_readiness_matrix.md`](phase10f/phase10f14_renderer_readiness_matrix.md) | Phase 10F-14 readiness decisions |
| [`phase10f/evidence/phase10f14_viewer_scene_renderer_foundation/`](phase10f/evidence/phase10f14_viewer_scene_renderer_foundation/) | Live adapter artifacts, WebGL snapshots, interactions, and screenshots |
| [`phase10f/phase10f15_integrated_plan.md`](phase10f/phase10f15_integrated_plan.md) | Production minimal viewer integrated plan |
| [`phase10f/phase10f15_viewer_tool_inventory.md`](phase10f/phase10f15_viewer_tool_inventory.md) | Viewer tool and schema inventory |
| [`phase10f/phase10f15_tool_consolidation_decision.md`](phase10f/phase10f15_tool_consolidation_decision.md) | Formal viewer identity decision |
| [`phase10f/phase10f15_legacy_schema_policy.md`](phase10f/phase10f15_legacy_schema_policy.md) | Phase 10D retention and migration policy |
| [`phase10f/phase10f15_cap_alignment.md`](phase10f/phase10f15_cap_alignment.md) | Validator, adapter, and renderer cap alignment |
| [`phase10f/phase10f15_production_renderer_implementation.md`](phase10f/phase10f15_production_renderer_implementation.md) | Production renderer hardening implementation |
| [`phase10f/phase10f15_instancing_and_performance.md`](phase10f/phase10f15_instancing_and_performance.md) | Instancing and bounded performance evidence |
| [`phase10f/phase10f15_browser_compatibility.md`](phase10f/phase10f15_browser_compatibility.md) | Chromium, Firefox, and WebKit compatibility |
| [`phase10f/phase10f15_mobile_and_resize.md`](phase10f/phase10f15_mobile_and_resize.md) | Mobile, touch, DPR, and resize baseline |
| [`phase10f/phase10f15_accessibility.md`](phase10f/phase10f15_accessibility.md) | Minimal viewer accessibility baseline |
| [`phase10f/phase10f15_dependency_audit_closure.md`](phase10f/phase10f15_dependency_audit_closure.md) | Dependency, npm audit, and bundle disposition |
| [`phase10f/phase10f15_security_review.md`](phase10f/phase10f15_security_review.md) | Formal viewer security review |
| [`phase10f/phase10f15_browser_api_evidence.md`](phase10f/phase10f15_browser_api_evidence.md) | Live formal-tool browser/API evidence |
| [`phase10f/phase10f15_readiness_matrix.md`](phase10f/phase10f15_readiness_matrix.md) | Phase 10F-15 production readiness decisions |
| [`phase10f/evidence/phase10f15_production_minimal_structure_viewer/`](phase10f/evidence/phase10f15_production_minimal_structure_viewer/) | Formal jobs, artifacts, metrics, browser matrix, security evidence, and screenshots |
| [`phase10f/phase10f16_integrated_plan.md`](phase10f/phase10f16_integrated_plan.md) | Scientific inspection integrated plan |
| [`phase10f/phase10f16_atom_picking_design.md`](phase10f/phase10f16_atom_picking_design.md) | Instanced atom picking and highlight design |
| [`phase10f/phase10f16_site_inspector_contract.md`](phase10f/phase10f16_site_inspector_contract.md) | Site inspector field and inference boundary |
| [`phase10f/phase10f16_measurement_semantics.md`](phase10f/phase10f16_measurement_semantics.md) | Distance, angle, and signed dihedral semantics |
| [`phase10f/phase10f16_renderer_export_policy.md`](phase10f/phase10f16_renderer_export_policy.md) | Local PNG and artifact download policy |
| [`phase10f/phase10f16_legacy_guidance_policy.md`](phase10f/phase10f16_legacy_guidance_policy.md) | Legacy JSON-only guidance policy |
| [`phase10f/phase10f16_npm_audit_disposition.md`](phase10f/phase10f16_npm_audit_disposition.md) | Seven-finding npm audit disposition |
| [`phase10f/phase10f16_implementation.md`](phase10f/phase10f16_implementation.md) | Scientific inspection implementation |
| [`phase10f/phase10f16_audit_review.md`](phase10f/phase10f16_audit_review.md) | Picking, measurement, export, lifecycle audit |
| [`phase10f/phase10f16_security_review.md`](phase10f/phase10f16_security_review.md) | Inspection and export security review |
| [`phase10f/phase10f16_browser_api_evidence.md`](phase10f/phase10f16_browser_api_evidence.md) | Live job and multi-browser inspection evidence |
| [`phase10f/phase10f16_readiness_matrix.md`](phase10f/phase10f16_readiness_matrix.md) | Scientific inspection readiness decisions |
| [`phase10f/evidence/phase10f16_scientific_structure_inspection/`](phase10f/evidence/phase10f16_scientific_structure_inspection/) | Live artifacts, measurements, PNG, browser and security evidence |
| [`phase10f/phase10f17_integrated_plan.md`](phase10f/phase10f17_integrated_plan.md) | Periodic inspection integrated plan |
| [`phase10f/phase10f17_periodic_identity_contract.md`](phase10f/phase10f17_periodic_identity_contract.md) | Canonical site plus image-offset identity |
| [`phase10f/phase10f17_lattice_math_policy.md`](phase10f/phase10f17_lattice_math_policy.md) | Row-vector lattice conversion and rejection policy |
| [`phase10f/phase10f17_minimum_image_algorithm.md`](phase10f/phase10f17_minimum_image_algorithm.md) | Bounded exact minimum-image search |
| [`phase10f/phase10f17_periodic_measurement_semantics.md`](phase10f/phase10f17_periodic_measurement_semantics.md) | Periodic distance, angle, and dihedral rules |
| [`phase10f/phase10f17_supercell_policy.md`](phase10f/phase10f17_supercell_policy.md) | Renderer-local bounded supercell policy |
| [`phase10f/phase10f17_periodic_bond_audit.md`](phase10f/phase10f17_periodic_bond_audit.md) | Same-cell replication and cross-boundary contract gap |
| [`phase10f/phase10f17_resource_cap_plan.md`](phase10f/phase10f17_resource_cap_plan.md) | Derived periodic resource caps |
| [`phase10f/phase10f17_implementation.md`](phase10f/phase10f17_implementation.md) | Periodic renderer implementation summary |
| [`phase10f/phase10f17_mathematical_audit.md`](phase10f/phase10f17_mathematical_audit.md) | Triclinic reference audit |
| [`phase10f/phase10f17_performance_review.md`](phase10f/phase10f17_performance_review.md) | Supercell performance review |
| [`phase10f/phase10f17_security_review.md`](phase10f/phase10f17_security_review.md) | Numeric, GPU, and network security review |
| [`phase10f/phase10f17_browser_api_evidence.md`](phase10f/phase10f17_browser_api_evidence.md) | Live browser/API evidence procedure |
| [`phase10f/phase10f17_readiness_matrix.md`](phase10f/phase10f17_readiness_matrix.md) | Phase 10F-17 readiness decisions |
| [`phase10f/evidence/phase10f17_periodic_crystal_inspection/`](phase10f/evidence/phase10f17_periodic_crystal_inspection/) | Live artifacts, references, metrics, browser and screenshot evidence |
| [`phase10f/phase10f18_integrated_plan.md`](phase10f/phase10f18_integrated_plan.md) | Canonical periodic bond topology closure plan |
| [`phase10f/phase10f18_periodic_bond_schema_decision.md`](phase10f/phase10f18_periodic_bond_schema_decision.md) | v2 schema and v1 compatibility decision |
| [`phase10f/phase10f18_periodic_bond_identity.md`](phase10f/phase10f18_periodic_bond_identity.md) | Stable periodic endpoint identity and deduplication |
| [`phase10f/phase10f18_topology_generation_policy.md`](phase10f/phase10f18_topology_generation_policy.md) | Bounded non-authoritative adapter topology policy |
| [`phase10f/phase10f18_security_review.md`](phase10f/phase10f18_security_review.md) | Numeric, injection, GPU, and network review |
| [`phase10f/phase10f18_readiness_matrix.md`](phase10f/phase10f18_readiness_matrix.md) | Phase 10F-18 readiness decisions |
| [`phase10f/evidence/phase10f18_periodic_bond_topology/`](phase10f/evidence/phase10f18_periodic_bond_topology/) | Live jobs, v2 artifacts, browser matrix, metrics, and screenshots |
| [`phase10f/phase10f19_periodic_scene_integration.md`](phase10f/phase10f19_periodic_scene_integration.md) | Periodic scene capability, manifest, preview, and validation hardening |
| [`phase10f/evidence/phase10f19_periodic_scene_integration/`](phase10f/evidence/phase10f19_periodic_scene_integration/) | Adapter artifacts, validation output, topology captures, and security evidence |
| [`phase10f/phase10f20_legacy_viewer_schema_migration.md`](phase10f/phase10f20_legacy_viewer_schema_migration.md) | Executable legacy compatibility and producer policy |
| [`phase10f/phase10f20_viewer_schema_compatibility_matrix.md`](phase10f/phase10f20_viewer_schema_compatibility_matrix.md) | Scene and manifest lifecycle matrix |
| [`phase10f/phase10f20_viewer_schema_deprecation_policy.md`](phase10f/phase10f20_viewer_schema_deprecation_policy.md) | Read-only retention and removal prerequisites |
| [`phase10f/phase10f20_viewer_schema_migration_decision.md`](phase10f/phase10f20_viewer_schema_migration_decision.md) | No-inference migration decision |
| [`phase10f/phase10f20_viewer_schema_security_evidence.md`](phase10f/phase10f20_viewer_schema_security_evidence.md) | Compatibility security boundary |
| [`phase10f/phase10f20_viewer_schema_readiness_matrix.md`](phase10f/phase10f20_viewer_schema_readiness_matrix.md) | Phase 10F-20 readiness decisions |
| [`phase10f/evidence/phase10f20_legacy_viewer_schema_migration/`](phase10f/evidence/phase10f20_legacy_viewer_schema_migration/) | Compatibility, renderer gate, preview, and security captures |
| [`phase10f/phase10f21_viewer_performance_hardening.md`](phase10f/phase10f21_viewer_performance_hardening.md) | Renderer performance architecture and implementation |
| [`phase10f/phase10f21_viewer_performance_budget.md`](phase10f/phase10f21_viewer_performance_budget.md) | Application-owned resource budgets |
| [`phase10f/phase10f21_viewer_large_scene_policy.md`](phase10f/phase10f21_viewer_large_scene_policy.md) | Interactive, degraded, and refused behavior |
| [`phase10f/phase10f21_viewer_lifecycle_contract.md`](phase10f/phase10f21_viewer_lifecycle_contract.md) | Demand rendering, stale protection, and cleanup |
| [`phase10f/phase10f21_viewer_performance_evidence.md`](phase10f/phase10f21_viewer_performance_evidence.md) | Multi-browser performance evidence |
| [`phase10f/phase10f21_viewer_performance_security.md`](phase10f/phase10f21_viewer_performance_security.md) | Resource and threshold security review |
| [`phase10f/phase10f21_viewer_performance_readiness_matrix.md`](phase10f/phase10f21_viewer_performance_readiness_matrix.md) | Performance readiness decisions |
| [`phase10f/evidence/phase10f21_viewer_performance_hardening/`](phase10f/evidence/phase10f21_viewer_performance_hardening/) | Budgets, metrics, lifecycle, browser, bundle, and security captures |
| [`phase10f/phase10f22_viewer_accessibility_hardening.md`](phase10f/phase10f22_viewer_accessibility_hardening.md) | Keyboard, semantic, focus, mobile, and visual accessibility hardening |
| [`phase10f/phase10f22_viewer_keyboard_contract.md`](phase10f/phase10f22_viewer_keyboard_contract.md) | Bounded application-owned viewer keyboard contract |
| [`phase10f/phase10f22_viewer_semantic_scene_contract.md`](phase10f/phase10f22_viewer_semantic_scene_contract.md) | Screen-reader scene and topology summary |
| [`phase10f/phase10f22_viewer_mobile_interaction_contract.md`](phase10f/phase10f22_viewer_mobile_interaction_contract.md) | Touch, scroll, target-size, and orientation policy |
| [`phase10f/phase10f22_viewer_cross_browser_matrix.md`](phase10f/phase10f22_viewer_cross_browser_matrix.md) | Chromium, Firefox, and WebKit accessibility matrix |
| [`phase10f/phase10f22_viewer_accessibility_security.md`](phase10f/phase10f22_viewer_accessibility_security.md) | Accessibility metadata and event security boundary |
| [`phase10f/phase10f22_viewer_accessibility_evidence.md`](phase10f/phase10f22_viewer_accessibility_evidence.md) | Real browser accessibility evidence procedure |
| [`phase10f/phase10f22_viewer_accessibility_readiness_matrix.md`](phase10f/phase10f22_viewer_accessibility_readiness_matrix.md) | Phase 10F-22 readiness decisions |
| [`phase10f/evidence/phase10f22_viewer_accessibility_mobile_cross_browser/`](phase10f/evidence/phase10f22_viewer_accessibility_mobile_cross_browser/) | Keyboard, semantic, mobile, contrast, zoom, browser, and security captures |
| [`phase10f/phase10f23_advanced_picking_measurement.md`](phase10f/phase10f23_advanced_picking_measurement.md) | Atom/bond picking and bounded measurement implementation |
| [`phase10f/phase10f23_selection_identity_contract.md`](phase10f/phase10f23_selection_identity_contract.md) | Periodic atom and canonical bond selection identity |
| [`phase10f/phase10f23_periodic_measurement_contract.md`](phase10f/phase10f23_periodic_measurement_contract.md) | Explicit-image and minimum-image measurement policy |
| [`phase10f/phase10f23_measurement_mathematics.md`](phase10f/phase10f23_measurement_mathematics.md) | Distance, angle, dihedral, and reference policy |
| [`phase10f/phase10f23_measurement_security.md`](phase10f/phase10f23_measurement_security.md) | Picking, cap, artifact, and network security |
| [`phase10f/phase10f23_measurement_evidence.md`](phase10f/phase10f23_measurement_evidence.md) | Three-browser and mobile evidence procedure |
| [`phase10f/phase10f23_measurement_readiness_matrix.md`](phase10f/phase10f23_measurement_readiness_matrix.md) | Phase 10F-23 readiness decisions |
| [`phase10f/evidence/phase10f23_advanced_picking_measurement/`](phase10f/evidence/phase10f23_advanced_picking_measurement/) | Picking, math, artifact, browser, screenshot, and security evidence |
| [`phase10f/phase10f26_scientific_export.md`](phase10f/phase10f26_scientific_export.md) | Scientific export architecture and scope |
| [`phase10f/phase10f26_export_contract.md`](phase10f/phase10f26_export_contract.md) | Strict request and inert view-state contract |
| [`phase10f/phase10f26_png_export.md`](phase10f/phase10f26_png_export.md) | PNG, background, high-DPI, and restoration policy |
| [`phase10f/phase10f26_export_manifest.md`](phase10f/phase10f26_export_manifest.md) | Ordered SHA-256 export manifest |
| [`phase10f/phase10f26_export_security.md`](phase10f/phase10f26_export_security.md) | Export threat model and controls |
| [`phase10f/phase10f26_pdf_readiness.md`](phase10f/phase10f26_pdf_readiness.md) | PDF deferred-by-design decision |
| [`phase10f/phase10f26_export_evidence.md`](phase10f/phase10f26_export_evidence.md) | Live three-browser and mobile export evidence |
| [`phase10f/phase10f26_export_readiness_matrix.md`](phase10f/phase10f26_export_readiness_matrix.md) | Export readiness decisions |
| [`phase10f/evidence/phase10f26_scientific_export/`](phase10f/evidence/phase10f26_scientific_export/) | Live artifacts, PNGs, reports, manifests, browser and security captures |
