# 文档索引

本目录保存“材料数据智能分析与可视化平台”的分阶段设计文档。阅读顺序建议从 Phase 0 到 Phase 12；`docs/11_MATERIAL_DOMAIN_EXTENSIONS.md` 是专业材料领域扩展补充文件，不改变 `docs/12_MVP_ROADMAP.md` 的 Phase 11 开发路线编号。

## 核心设计文档

| 文件 | 主题 |
|---|---|
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
