# Task Results

## Agent-2.0 Phase 14-R — 目录请求连续性与报告/来源上下文批次（2026-08-31）

- 状态：已完成本批次，Phase 14-R 总体仍处理中
- 修改摘要：报告增加稳定章节导航；Scientific Presentation 增加精确来源
  版本固定/取消固定；项目与 Dataset 目录增加有界共享缓存及写入失效。
- 测试结果：Planner/Data focused `66/66`；此前本批次全前端
  `102 files / 730 tests`；typecheck、生产构建、compileall、lock、
  `git diff --check` 通过；同栈 PostgreSQL/Redis/MinIO 运维快照 `status=ok`。
- 提交/CI：未创建 P14R-A/P14R-B；整体 Phase 14-R 仍未封板。

## Agent-2.0 Phase 14-R — 研究控制窄屏可见性（2026-08-31）

- 状态：已完成本批次，Phase 14-R 总体仍处理中
- 修改摘要：编辑/继续研究动作在窄屏下自动切换“对话”面板；编辑查询
  路由保持 conversation-first，避免操作入口与编辑器分离。
- 证据：认证浏览器编辑路由显示 `selectedTab=对话`、编辑提示可见，
  布局 `731/731`、无 alert。
- 测试结果：Research/Presentation focused `71/71` 通过。
- 提交/CI：未创建 P14R-A/P14R-B；完整编辑提交、分支持久化及其他成熟
  产品门仍未封板。

## Agent-2.0 Phase 14-R — 编辑分支真实浏览器验证（2026-08-31）

- 状态：已完成本批次，Phase 14-R 总体仍处理中
- 证据：新编辑 Turn `17c0b9d1-b5c0-47f9-b93c-c5f8a1cb19df` 进入 `2/2`
  分支并完成两个真实分析输出；分支切换返回历史 Turn
  `fb72c2ad-bed1-47d7-b557-f398f04a8ede`，旧问题/结果未变。
- 浏览器：无 alert、无布局溢出；停止/重试及严格 390px 浏览器资格仍待
  验证。
- 提交/CI：未创建 P14R-A/P14R-B，整体仍未封板。

## Agent-2.0 Phase 14-R — 失败运行恢复入口可见性（2026-08-31）

- 状态：已完成本批次，Phase 14-R 总体仍处理中
- 修改摘要：历史 `run=` 路由在 FAILED/CANCELED 状态下自动选择“对话”
  面板，使继续/重新研究恢复动作不再隐藏在工作台之外。
- 证据：认证浏览器显示 `selectedTab=对话`、继续/重新研究可见，
  `731/731` 且无 alert。
- 测试结果：ResearchPages focused `64/64`。
- 提交/CI：未创建 P14R-A/P14R-B；完整恢复压力与其他成熟产品门仍开放。

## Phase 14-R — Report navigation and source-context pinning (2026-08-31)

- 状态：已完成（本批；Phase 14-R 总体仍处理中）
- 修改摘要：新增 Report 章节锚点导航与移动端紧凑布局；新增科学结果精确来源版本固定/取消固定控制，复用 Session Memory 授权 API。
- 证据：认证浏览器 Report `agent2_report_e54681009a0e49abe371247d9053ce61` 显示 8 个章节链接并在页内定位；轨迹来源版本 `a22745f2-17b6-434f-ba4c-3fe6bd244841` 固定成功且未产生科学执行对象。
- 测试结果：前端 focused `26/26`；typecheck、production build、compileall、`git diff --check` 通过。
- 提交/CI：未创建 Phase 14-R release commit；任务继续处理中。
- 追加回归：全前端 `102 test files / 730 tests passed`；同栈运维快照
  PostgreSQL `1/12/0`、Redis `6/0`、MinIO `ok`。

## Agent-2.0 Phase 14-R — Task state labels and pin mutation race

- 状态：已完成（局部产品缺陷修复，Phase 14-R 总体仍处理中）
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `NotificationCenterPage.tsx`、`Agent2ScientificPresentation.tsx` 及对应测试，
  Phase14-R 审计/结果与 `persistent/DESIGN_PROGRESS.md`
- 修改摘要：现代 Agent2 任务与通知显示“可恢复研究会话”，仅无 Turn 的
  legacy 运行显示“历史运行 · 仅查看”；科学结果固定/取消固定增加异步
  竞态保护和失败回滚，不改变结果或执行权威。
- 测试结果：前端 `96 files / 615 tests passed`；定向 Agent2/任务/通知测试
  通过；后端涉及测试 `31 passed, 3 skipped`；typecheck、production build、
  `git diff --check` 通过；认证 Chromium `/tasks` 与 `/notifications` 通过。
- 提交/CI 状态：未提交；Phase 14-R 尚未达到 P14R-A/P14R-B release 门槛。

## Agent-2.0 Phase 14-R — Current full regression after stale-error guard

- 状态：已完成（回归复核，Phase 14-R 总体仍处理中）
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/Agent2ScientificPresentation.tsx`，
  Phase14-R 审计/结果、`persistent/DESIGN_PROGRESS.md`
- 修改摘要：补齐会话记忆读取失败分支的序列校验，旧请求的成功或失败结果
  都不能覆盖较新的固定/取消固定操作。
- 测试结果：前端全量 `96 files / 615 tests passed`；后端全量
  `1827 passed / 83 skipped`；定向 3 files / 7 tests、typecheck、build、
  compileall、`uv lock --check`、touched Ruff、`git diff --check` 通过；
  `/health/runtime` 为 PostgreSQL/Redis/MinIO/Redis worker/DeepSeek。
- 提交/CI 状态：未提交；未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — Authenticated desktop/mobile surface sweep

- 状态：已完成（浏览器证据补充，Phase 14-R 总体仍处理中）
- 完成时间：2026-08-28
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、Phase14-R 审计、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：使用指定 Chromium 和认证账户复核项目、Data、Research、Reports、
  Tasks、Notifications 的桌面/移动端入口与布局。
- 测试结果：12 个 route/viewport 检查全部 `overflow=0`，关键内容存在，
  无 page error；登录前 401 与离开 Data 页面时的 object-store aborted 请求
  均按预期 bootstrap/navigation cancellation 分类。
- 提交/CI 状态：未提交；P14R-A/P14R-B 尚未创建。

## Agent-2.0 Phase 14-R — Exact ResearchTurn continuity from task surfaces

- 状态：已完成（局部产品缺陷修复，Phase 14-R 总体仍处理中）
- 完成时间：2026-08-28T05:37:00+08:00
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/NotificationCenterPage.tsx`、对应前端测试、
  Phase14-R 审计/结果与 `persistent/DESIGN_PROGRESS.md`
- 修改摘要：任务中心和通知中心在没有 Workspace 时保留持久化
  `researchTurnId`，导航同时传递 `run` 与 `turn`；无 Turn 的 legacy
  任务继续使用 run-only fallback，避免 Job 名称推断。
- 测试结果：`TaskCenterPage.test.tsx` 1 passed；
  `NotificationCenterPage.test.tsx` 1 passed。
- 提交/CI 状态：未提交；Phase 14-R 尚未达到 release commit 门槛。

## Agent-2.0 Phase 14-R — current-worktree regression refresh

- 状态：已完成（回归复核）
- 完成时间：2026-08-28
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：记录当前工作树在搜索生命周期筛选、ScientificResult 精确 ResearchTurn
  连续性和报告 Markdown 导出传输修复后的新鲜回归结果；保持成熟产品门槛的
  `PARTIAL` 事实状态。
- 测试结果：前端 `96 files / 615 passed`；后端 `1827 passed / 83 skipped`；
  production build、typecheck、compileall、`uv lock --check`、touched Ruff、
  `git diff --check` 均通过；runtime 为 PostgreSQL/Redis/MinIO。
- 提交/CI 状态：未提交；未创建 P14R-A/P14R-B；仍有 capability-wide browser、
  lifecycle/retention、recovery、operations 和 real-user acceptance 欠债。

## Agent-2.0 Phase 14-R — current same-stack service campaign

- 状态：已完成（同栈服务回归）
- 完成时间：2026-08-28
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：在当前工作树、真实 PostgreSQL/Redis/MinIO 和 Redis worker 上复核
  Context Manifest、PostgreSQL planning 以及 Phase 7 reuse/execution。
- 测试结果：`8 passed, 0 failed, 0 errors, 0 skipped`；PostgreSQL
  `active=1`, `idle=4`, `idle-in-transaction=0` observed。
- 提交/CI 状态：未提交；本次仅补证据，P14R-A/P14R-B 尚未创建。

## Agent-2.0 Phase 14-R — authenticated browser continuity

- 状态：已完成（浏览器连续性复核）
- 完成时间：2026-08-28
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：保持已认证的内置浏览器标签页和同栈服务运行，复核全局搜索将
  ScientificResult snapshot `2809dcd1-243e-4323-8538-0a5fe81780d9`
  解析到持久化 ResearchTurn `8382c443-f9ca-4c90-9aa3-444fea683807`。
- 测试结果：实时 DOM 快照显示精确 `/research?turn=...` 入口；无重启或关闭浏览器。
- 提交/CI 状态：未提交；P14R 仍为 `PARTIAL`。

## Agent-2.0 Phase 14-R — lifecycle archive/delete audit

- 状态：已完成（边界审计）
- 完成时间：2026-08-28
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：确认当前只有 ACTIVE/ARCHIVED 生命周期和带依赖预览的空项目/空数据集物理删除；
  尚无 TRASHED/PURGED、Retention 或 provenance-aware Export 契约，保持现有删除
  fail-closed，不引入半成品破坏科学来源。
- 测试结果：代码审计、现有 dependency-impact 和生命周期测试均保持通过。
- 提交/CI 状态：未提交；P14R 仍为 `PARTIAL`。

## Agent-2.0 Phase 14-R — ScientificResult search continuity

- 状态：已完成（窄范围修复）
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `apps/web/app/lib/planner-api.ts`、`tests/test_project_access.py`、
  `AGENT2_PHASE14R_RESULTS.md`、`persistent/DESIGN_PROGRESS.md`
- 修改摘要：全局搜索命中 ScientificResult 时优先沿持久化
  `ScientificResultSnapshot.research_turn_id` 打开精确 ResearchTurn；
  无关系的历史记录保留 `result=` 兜底，移除前端从结果字符串猜测会话的风险。
- 测试结果：搜索回归 `2 passed`，精确入口 helper 回归通过；同栈浏览器实测
  snapshot `2809dcd1-243e-4323-8538-0a5fe81780d9` → Turn
  `8382c443-f9ca-4c90-9aa3-444fea683807`。
- 提交/CI 状态：未提交；Phase 14-R 仍为 `PARTIAL`，未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — Scientific Report export transport

- 状态：已完成（窄范围修复）
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/ScientificReportRoute.tsx`、
  `apps/web/app/components/ScientificReportRoute.test.tsx`、
  `AGENT2_PHASE14R_RESULTS.md`、`persistent/DESIGN_PROGRESS.md`
- 修改摘要：Markdown 导出使用挂载到 document 的隐藏 Blob anchor，点击后移除并
  revoke URL，避免浏览器运行时丢失下载事件。
- 测试结果：`ScientificReportRoute.test.tsx` `6 passed`；typecheck 通过。
- 提交/CI 状态：未提交；Phase 14-R 仍为 `PARTIAL`，未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — Authorized global-search lifecycle filters

- 状态：已完成（窄范围修复）
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `apps/web/app/lib/planner-api.ts`、`apps/web/app/components/ProductShell.tsx`、
  `tests/test_project_access.py`、`apps/web/app/components/ProductShell.test.tsx`、
  `docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`、`AGENT2_PHASE14R_RESULTS.md`
- 修改摘要：为现有授权全局搜索增加类型和 active/archived/all 生命周期筛选；
  项目归档状态读取权威 `project_configs`，不改变科学数据或执行权威。
- 测试结果：后端搜索回归 `2 passed`；前端 `ProductShell` 回归 `6 passed`；
  Ruff、浏览器 `/console` 筛选证据通过。
- 提交/CI 状态：未提交；Phase 14-R 仍为 `PARTIAL`，未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — explicit Result/Snapshot reuse seam

- 状态：已完成（窄范围修复）
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/routers/agent2.py`、`apps/api/mdi_api/research_agent/context/assembler.py`、`apps/web/app/lib/agent2-research-api.ts`、`apps/web/app/components/Agent2ScientificPresentation.tsx` 及对应测试
- 修改摘要：区分 ScientificResult bundle `result_id` 与持久化 snapshot ID；显式复用结果不再与历史候选混排；解释分支读取原始 immutable snapshot，不创建重复科学结果。
- 测试结果：前端 focused `15 passed`；后端 API/result focused `1 passed`；compileall `PASS`；同栈浏览器 Turn `4460fc2c-98f8-4129-8fd5-0615f08dc5a7` `COMPLETED`，解释 `VALID`，科学计数零增量。
- 提交/CI：未提交；Phase 14-R 仍为 `PARTIAL`，未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — Durable notification entry point

- 状态：已完成（增量）
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/NotificationCenterPage.tsx`、
  `apps/web/app/components/NotificationCenterPage.test.tsx`、
  `apps/web/app/components/ProductShell.tsx`、
  `apps/web/app/notifications/page.tsx`、
  `docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：基于现有授权项目/持久化分析任务 API 增加只读通知中心，展示完成、
  部分完成、失败和取消状态，支持精确研究入口、可见性恢复刷新和 30 秒刷新；
  不新增科学事实或执行状态权威。
- 测试结果：`NotificationCenterPage` 与 `TaskCenterPage` 共 2 tests passed；
  `npm run typecheck` passed。
- 提交/CI 状态：待提交；Phase 14-R 当前 verdict 仍为 PARTIAL。

## Agent-2.0 Phase 14-R — Task Center retry handoff

- 状态：已完成（增量）
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/TaskCenterPage.test.tsx`、
  `docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：对失败/取消且具备权威 `researchTurnId` 的任务增加“打开并重试”
  入口，保留原始 run/turn 标识并交给 Research 页创建新的不可变重试分支；
  无 Turn 的 Workspace 任务保持仅打开。
- 测试结果：Task Center、Notification Center、ResearchExecutionActivity 共
  8 tests passed；`npm run typecheck` passed。
- 提交/CI 状态：待提交；Phase 14-R verdict 仍为 PARTIAL。

## Agent-2.0 Phase 10 browser-context refresh — 2026-08-25

状态：部分完成

完成时间：2026-08-25

修改摘要：deep-linked Viewer research action 现在携带 exact object/version
到 `explicit_object_refs`；context assembler 只把最高优先级对象候选交给
provider，避免无关历史对象制造澄清。真实同栈 PostgreSQL/Redis/MinIO 与
Chromium 验收中，新会话快照只保留 Structure；随后 capability eligibility
正确返回 `CAPABILITY_REQUIREMENT_UNSATISFIED`，因为现有结构 fixture 缺少
coordination capability 的 typed semantic input contract。没有伪造执行记录。

测试结果：Phase 2/7/10 focused `54 passed`；frontend `90 files / 582 tests`；
typecheck/build/compileall/uv lock/diff check PASS；既有完整后端
`1787 passed, 83 skipped`、服务端 Phase 10 `6/6 passed`、Batch-1 live semantic
`8/8 passed`、390x844 Table PASS 保持有效。三族新能力的真实 browser
Job/Result/Viewer 路径仍未闭合；full Ruff 有 79 个历史错误，未运行 exact-head
CI，不能声明 Phase 10 COMPLETE。

提交/CI 状态：未提交、未 push；Phase 11 未开始。

## Production Object Management UX — 2026-08-20

状态：已完成

完成时间：2026-08-20

修改摘要：完成 Console 新建项目、Project/Data Navigator 右键与更多菜单、键盘/触摸等价入口、显式多选批量归档/恢复、可逆归档与空对象安全删除；补齐上传深链、Research Composer、Session/Message 写接口和 Report 归档的 Project 角色授权。只读成员仍可查看数据、研究结果和报告，但不会看到会失败的写入控件。

测试结果：完整 Python `1607 passed, 51 skipped, 75 warnings`；完整 Vitest `80 files / 525 tests passed`；聚焦管理/研究 `25 passed`；Project access/history `19 passed`；`npm run typecheck`、production build、compileall、`git diff --check` PASS。Chrome 已登录验收 Console 新建、Projects 分组/右键/Shift+F10/多选、Data 64 行真实表格、Dataset 菜单、Inspector 与焦点恢复；390px 验收同样通过，项目页、菜单、创建弹窗、数据表和 Inspector 均无横向溢出。

提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

## Production UI/UX Reconstruction — 2026-08-19 continuation

状态：处理中（核心闭环继续收敛）

完成时间：2026-08-19

修改摘要：修复 trajectory contract 对生产级数值矩阵的扫描误判；为 `viz.correlation` 增加严格、可审计的 pairwise evidence projector；将相关性 claim 投影为中文科研用户文案并将内部 correlation subject 从结果标题隐藏；重启 API 使用项目正确的 `uv run`/`--app-dir apps/api` 环境，完成真实 Q-TABLE Research Chrome 路径验证。保留了此前失败 turn、消息、Job、Artifact、Interpretation 和调用记录。

测试结果：`pytest tests/ -q` = 1584 passed, 51 skipped, 90 warnings；`npm run test -- --run` = 79 files / 494 tests passed；`npm run typecheck` PASS；`npm run build` PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api packages services tests` PASS；`git diff --check` 无 whitespace error。Chrome production route 实际确认：图表、数值表、中文 Pearson 相关系数发现、限制、依据和报告入口均可见，默认页面无 raw Plan/Tool/Job IDs。

CI/提交状态：未修改 `.github/workflows/**`，未部署；任务保持处理中，直至剩余科学 Viewer、增量结果浏览器观察、可访问性和最终产品验收债务关闭。

本文件按完成顺序保存 `TASKS.md` 中各任务的最终结果。只追加，不覆盖历史记录。

# Phase 10K-0 Material Intelligence Capability Gap Audit Result

## Status and Completion Time

* status: `PASS`
* completed: `2026-07-27 21:28:51 +08:00`

## Repository and Scope

* baseline: Gate J6-R completion HEAD `34c30c50631771209c90fca049fcff93a8a8bef9` on `master`, clean and equal to `origin/master`.
* task: documentation-only repository capability audit; no Phase 10K-1 implementation.
* audit commit: `cada6fbe473c213f3a05b8e7a8a879ea110ffc2d`.
* no source code, schema, parser, adapter, Tool Registry, Planner, PlanValidator,
  QueueWorkerRuntime, frontend product, dependency, or lockfile changed.

## Main Findings

* `DataProfile 0.1`: `MINIMAL`. It provides narrow table/structure summaries;
  it does not provide material capability discovery, stable sample identity,
  property/unit semantics, model-task semantics, or trajectory/phonon/volumetric
  discovery.
* semantic inference: exact/allowlisted table roles support formula and narrow
  regression/uncertainty aliases; classification and general materials-property
  recognition are missing.
* dataset surface: executable table, composition, and lightweight structure
  adapters are `REUSABLE_FOUNDATION`; they do not constitute a Dataset Materials
  Explorer.
* Materials ML: basic metrics, error distribution, outlier table, and density
  scatter are real; complete regression, uncertainty, classification, chemistry-
  conditioned errors, and model comparison remain Initial Release gaps.
* composition space: formula parsing and aggregate views are reusable;
  deterministic vectors, PCA, clustering, linked inspection, and outlier
  semantics are missing. NumPy/SciPy are available; scikit-learn is transitive;
  UMAP/matminer are not dependencies.
* Planner: `PARTIAL_PROFILE_AWARE / MOSTLY_PROMPT_ROUTED`; capability-aware
  multi-tool planning and interpretation remain Phase 10L.
* frontend: PlannerWorkbench and generic artifacts are reusable, but there is no
  product-level dataset intelligence experience. Unified workspace work remains
  Phase 10M.
* manifest-only V1 proposals without runtime adapter closure were not counted as
  implemented.

## Frozen Implementation Direction

* 10K-1: versioned Material Data Profile 2.0 capability and identity layer.
* 10K-2: bounded Dataset Materials Explorer using existing table/composition/
  structure foundations.
* 10K-3: data-gated regression, uncertainty, and classification evaluation.
* 10K-4: deterministic composition vectors, bounded PCA, reviewed clustering,
  property coloring, and linked inspection.
* 10K-5: real upload/profile/tool/artifact/frontend/report/recipe evidence.
* Future and Not Planned scope remains unqueued.

## Documentation

* audit: `docs/phase10k/phase10k0_material_intelligence_capability_gap_audit.md`
* gap matrix: `docs/phase10k/phase10k0_material_intelligence_gap_matrix.md`
* sequence: `docs/phase10k/phase10k0_phase10k_implementation_sequence.md`
* next scope: `docs/phase10k/phase10k1_next_scope.md`
* index and required persistent project-memory files were updated.

## Verification

* `git diff --check`: PASS.
* `uv lock --check`: PASS; 108 packages resolved, no dependency change.
* frontend: 48 test files / 294 tests PASS.
* typecheck: PASS.
* production build: PASS; `/` first-load JS 228 kB.
* backend: 760 passed, 24 skipped, 62 warnings. Skips remain explicit service-
  gated tests and were not reported as passed locally.
* Phase 10 evidence integrity: `PHASE10_CLOSURE_EVIDENCE_INTEGRITY_PASS`.
* docs links and TASKS structure/processing consistency: PASS.
* security: `NO_SECRET_PATTERN_HITS`; no network operation or real LLM was used
  by the audit.

## Commit / CI / Queue

* audit CI: run `30270323576`, exact SHA `cada6fb`, success.
* CI jobs: Unit Tests, Frontend Typecheck & Build, PostgreSQL/Redis/MinIO
  Service-backed Integration, and no-skipped assertion all succeeded.
* completion-record commit: `ab5a69a79ab5b4ac17357b3bcf8abb051c8f552d`.
* completion-record CI: run `30270636913`, exact SHA, success; Unit, Frontend,
  service-backed integration, and no-skipped assertion all succeeded.
* archive decision: the result, local checks, audit commit/CI, and completion
  record/CI are consistent; the complete 10K-0 task block may be removed.
* Phase 10K-0: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K-1: `NEXT / NOT_STARTED`; a complete prompt is now present in the
  user-maintained queue, superseding the earlier awaiting-prompt wording.

# Phase 10K-1 Material Data Profile 2.0 Result

## Status and Completion Time

* status: `PASS`
* completed: `2026-07-28 17:53:01 +08:00`

## Delivered Capability

* Extended the existing additive `DataProfile` contract (`schemaVersion=0.1`,
  `profileContractVersion=2.0`) instead of creating a parallel profile type.
* Added deterministic semantic facts for formula, approved material properties,
  stable sample identity, regression/multiple-model/multi-target/uncertainty,
  classification labels, and class probabilities.
* Used bounded authority levels and explicit model-series bindings. A generic
  uncertainty column is not silently assigned to multiple predictions.
* Added immutable table, composition/structure, trajectory, phonon, and
  volumetric resource semantics. Data readiness remains distinct from actual
  Registry-backed platform availability.
* Added deterministic semantic hashing, typed ambiguity/missing reasons,
  coverage disclosure, bounded inputs, API/persistence serialization, and a
  compact read-only profile surface in the existing frontend.

## Scope and Evidence

* No Dataset Explorer, ML evaluation product, embedding/clustering, capability-
  aware Planner behavior, Tool Registry entry, PlanValidator rule,
  QueueWorkerRuntime behavior, dependency, real LLM call, or external request
  was introduced.
* Real API, performance, and Chromium/Firefox/WebKit/mobile evidence is retained
  in `docs/phase10k/evidence/phase10k1_material_data_profile_2/`.
* Readiness: `READY_WITH_EXPLICIT_LIMITS`; semantic recognition is deterministic
  and bounded, while future analysis products remain correctly unavailable until
  their corresponding Registry-backed implementation phases.

## Verification

* focused profile/API/component tests: `41 passed`.
* full backend: `777 passed, 24 skipped, 62 warnings`; local skips were explicit
  service-gated cases and are not reported as passes.
* frontend: `48 files, 294 tests passed`; typecheck and production build passed.
* `uv lock --check`, `git diff --check`, Phase 10 closure/evidence integrity,
  API/performance evidence, and browser runners passed.
* markers: `MATERIAL_DATA_PROFILE_API_EVIDENCE_PASS`,
  `MATERIAL_DATA_PROFILE_PERFORMANCE_EVIDENCE_PASS`,
  `MATERIAL_PROFILE_BROWSER_EVIDENCE_PASS`,
  `MATERIAL_PROFILE_MOBILE_EVIDENCE_PASS`,
  `NO_MATERIAL_PROFILE_EXTERNAL_NETWORK_REQUESTS`, and
  `NO_SECRET_PATTERN_HITS`.

## Commit / CI / Queue

* implementation: `92a8e98b344b0a819954746f107e765f8f9cf6d2`; exact-SHA CI run
  `30346512968` succeeded, including service-backed integration and no-skipped.
* completion record: `b5a464e1c436f6f7a056511b1a0a6cfcc6cbcb19`; exact-SHA CI run
  `30346686652` succeeded for Unit Tests, Frontend Typecheck & Build, and
  PostgreSQL/Redis/MinIO service-backed integration with the no-skipped gate.
* archive decision: completion record, result, required checks, evidence, and
  both exact-SHA CI gates are consistent; the `Phase 10K-1` task block is
  eligible for verified queue archival.
* Phase 10K-1: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K-2: `NEXT / NOT_STARTED`.

# Phase 10K-2 Dataset Materials Explorer Result

## Status and Completion Time

* status: `PASS_PENDING_COMPLETION_RECORD_CI`
* completed: `2026-07-28 19:32:32 +08:00`

## Delivered Capability

* Added one validated product-level `dataset.materials_explorer` tool backed by
  exactly one Material Data Profile 2.0 and explicitly bound canonical table/
  Structure resources.
* Delivered deterministic dataset overview, element and chemical-system
  coverage, exact formula/Structure duplicate classes, canonical structure
  statistics, finite-only property distributions, factual data-quality output,
  explicit group/resource comparison, and stable sample links.
* Emitted one bounded inert `phase10k2.dataset_materials_explorer.v1` product
  bundle plus quality, summary, and recipe artifacts through persisted
  AnalysisPlan, PlanValidator, QueueWorkerRuntime, Registry, and Adapter.
* Added seven accessible responsive Results views: Overview, Composition,
  Structures, Properties, Data quality, Comparison, and Samples. Every
  chart-like view retains numeric/table content and inert JSON fallback.

## Scientific and Security Boundary

* Comparison requires explicit resource or group identity; row order never
  infers a split and unlike property units are not converted.
* Structure duplicates require equal canonical normalized hashes; reduced
  formula duplicates are separate and no near-duplicate, chemical-validity,
  significance, or anomaly authority is claimed.
* Hard caps cover 100,000 rows, 512 columns, 64 properties, 256 categories,
  200 linked rows, 100 bins, 256 structures, 5,000 atoms/structure, 128
  warnings, and 8,000,000 bytes/artifact.
* No dependency, arbitrary Python, notebook/script execution, real LLM,
  external request/asset, artifact JavaScript, ML evaluation, embedding,
  clustering, Agent automation, or workspace redesign was added.

## Evidence and Verification

* Real persisted Planner/job/runtime/API artifacts and Chromium/Firefox/WebKit
  plus 390x844 mobile replay are retained under
  `docs/phase10k/evidence/phase10k2_dataset_materials_explorer/`.
* Performance cases: 4, 5,000, and 100,000 rows; near-cap artifact remained
  bounded at about 24 KB and 100 linked sample rows.
* backend full: `791 passed, 24 skipped, 63 warnings`; skipped tests are explicit
  environment/real-LLM gates and were not reported as passed.
* backend non-integration: `791 passed, 1 skipped, 23 deselected`.
* frontend: `49 files, 300 tests passed`; typecheck and production build PASS.
* manifest/schema focused tests: `22 passed`; Phase 10 closure and evidence
  integrity PASS; `uv lock --check` and `git diff --check` PASS.
* markers: `DATASET_MATERIALS_EXPLORER_RUNTIME_EVIDENCE_PASS`,
  `DATASET_COMPOSITION_EXPLORER_EVIDENCE_PASS`,
  `DATASET_STRUCTURE_STATISTICS_EVIDENCE_PASS`,
  `DATASET_PROPERTY_EXPLORER_EVIDENCE_PASS`, `DATASET_QUALITY_EVIDENCE_PASS`,
  `DATASET_COMPARISON_EVIDENCE_PASS`,
  `DATASET_MATERIALS_EXPLORER_BROWSER_EVIDENCE_PASS`,
  `DATASET_MATERIALS_EXPLORER_PERFORMANCE_EVIDENCE_PASS`,
  `NO_DATASET_EXPLORER_EXTERNAL_NETWORK_REQUESTS`, and
  `NO_SECRET_PATTERN_HITS`.

## Commit / CI / Queue

* implementation commit: `1f495e14ccae72d8b22fa494ca8f6754bffb73d1`.
* cross-platform evidence fix/current implementation HEAD:
  `35c0fc6aa829fb8e9445c3a9d867883c1f10645e`.
* exact-SHA CI run `30355075439`: Unit Tests, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion
  all succeeded.
* completion-record commit/CI: pending this record commit.
* Phase 10K-2 remains in `TASKS.md` until completion-record exact-SHA CI passes.
* Phase 10K-3 remains pending and was not implemented by this task.

## Phase 10K-2 Completion-Record CI and Queue Closure

* closure status: `PASS`
* completion-record commit: `8dc2545fd1f88bc63d6dc281643c96d43ab3679e`
* completion-record exact-SHA CI: run `30355282590`, success.
* CI jobs: Unit Tests, Frontend Typecheck & Build, and PostgreSQL/Redis/MinIO
  Service-backed Integration all succeeded; the integration no-skipped
  assertion succeeded.
* archive decision: the implementation commits, both exact-SHA CI runs,
  completion record, permanent result, required local checks, and retained
  evidence are consistent. The completed Phase 10K-2 task block is eligible
  for verified queue archival.
* Phase 10K-2: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K-3: `NEXT / NOT_STARTED`.

# Phase 10K-3 Materials ML Evaluation Result

## 1. Conclusion

`PASS`.

## 2. Baseline

* Phase 10K-2: archived after implementation `35c0fc6`, completion record
  `8dc2545`, and exact-SHA CI `30355282590`.
* initial HEAD: `4ae8afde126765367ad0a17aad1271a812cdf68f` on `master`, clean.
* current implementation/evidence-closure HEAD: `a1e05ee5b0f1affa91183e681b1678d4419cedc4`.

## 3. ML Product Architecture

* Profile 2.0 remains the only target/prediction/uncertainty/classification
  semantic authority. Three product tools bind one explicit canonical table and
  complete semantic task groups; artifacts retain dataset/profile/semantic hash
  and stable sample references.

## 4. Regression and Chemistry

* `ml.regression_evaluation` reports MAE, RMSE, defined-or-null R2, signed
  bias, fixed `prediction_minus_target` residuals, parity/residual/histogram
  data, high-error sample links, element-overlap error summaries, exact
  chemical-system summaries, and bounded common-valid-sample model comparison.

## 5. Uncertainty and Classification

* `ml.uncertainty_evaluation` provides source-defined uncertainty association,
  equal-count mean-uncertainty/mean-absolute-error bins, retained-lowest-
  uncertainty error decay, and linked high-uncertainty samples.
* `ml.classification_evaluation` provides raw confusion counts, support,
  accuracy, per-class/macro metrics with undefined values as null, linked
  misclassifications, and ROC/PR only for explicit binary positive classes with
  validated matching probabilities. Multiclass curves remain typed unavailable.

## 6. Runtime, Frontend, and Artifacts

* Mock Planner emits only explicit, profile-ready evaluation plans; existing
  PlanValidator and QueueWorkerRuntime authority is unchanged. Service-backed
  CI covers all three tools through persisted jobs, PostgreSQL, Redis, MinIO,
  and S3-compatible artifact retrieval.
* Results renders responsive numeric SVG/table panels and inert JSON fallback;
  Dataset Explorer exposes an availability-driven Model evaluation tab. Browser
  evidence covers Chromium, Firefox, WebKit, and 390x844 mobile.

## 7. Caps, Security, and Explicit Limits

* Caps: 100,000 rows, 16 models, 64 classes, 256 chemistry groups, 200 table
  rows, 10,000 plot points, 5,000 curve points, 50 uncertainty bins, 8 MB
  artifacts, and bounded time.
* No model training, AutoML, SHAP, feature-importance suite, PCA/UMAP,
  clustering, Agent interpretation, or workspace redesign was added. No
  arbitrary code, real LLM, artifact JavaScript, external assets, or runtime
  network authority was introduced.

## 8. Evidence and Checks

* Evidence: `docs/phase10k/evidence/phase10k3_materials_ml_evaluation/`;
  includes runtime/API captures, inert artifacts, 4/5,000/100,000-row metrics,
  browser/mobile screenshots, accessibility/network/security audits, and hashes.
* backend: `808 passed, 25 skipped, 63 warnings`; frontend: `50 files, 307
  tests passed`; typecheck/build, `uv lock --check`, `git diff --check`, focused
  evidence tests, Phase 10 closure integrity, trajectory evidence integrity,
  docs/TASKS checks, and K2/K3 browser runners passed.
* local service-backed: `UNAVAILABLE` (4 gated skips), not represented as pass.
  CI service-backed/no-skipped: success. `npm audit`: `UNAVAILABLE` because the
  configured npmmirror audit endpoint returns `404 NOT_IMPLEMENTED`; no
  dependency or lockfile changed.
* markers: `MATERIALS_ML_REGRESSION_RUNTIME_EVIDENCE_PASS`,
  `MATERIALS_ML_UNCERTAINTY_RUNTIME_EVIDENCE_PASS`,
  `MATERIALS_ML_CLASSIFICATION_RUNTIME_EVIDENCE_PASS`,
  `MATERIALS_ML_REGRESSION_BROWSER_EVIDENCE_PASS`,
  `MATERIALS_ML_CHEMISTRY_ERROR_EVIDENCE_PASS`,
  `MATERIALS_ML_UNCERTAINTY_BROWSER_EVIDENCE_PASS`,
  `MATERIALS_ML_CLASSIFICATION_BROWSER_EVIDENCE_PASS`,
  `MATERIALS_ML_PERFORMANCE_EVIDENCE_PASS`,
  `NO_MATERIALS_ML_EXTERNAL_NETWORK_REQUESTS`, and `NO_SECRET_PATTERN_HITS`.

## 9. Commit / CI / Queue

* implementation: `4574cef`; evidence-closure/current implementation:
  `a1e05ee5b0f1affa91183e681b1678d4419cedc4`; exact-SHA CI run `30363719393`
  passed Unit, Frontend Typecheck & Build, PostgreSQL/Redis/MinIO service-backed
  integration, and no-skipped assertion.
* completion record: `c5483d6f609ff21f9b7c06ce7bff88ec583d52c5`; exact-SHA CI
  run `30364098180` passed Unit, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion.
* archive decision: implementation, completion record, retained result,
  required checks, retained evidence, and both exact-SHA CI gates are
  consistent. The verified task block is eligible for queue archival.
* queue after archive: Phase 10K-3 `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`; Phase
  10K-4 remains `NEXT / AWAITING COMPLETE PROMPT`; Phase 10K-5 remains planned
  and unstarted.

## 10. Next Phase

**Phase 10K-4：Composition Space / Embedding / Clustering**

## 11. Completion-Record CI and Queue Closure

* closure status: `PASS`.
* completion-record exact-SHA CI: `30364098180`, success for Unit, Frontend,
  service-backed integration, and the no-skipped assertion.
* archive eligibility: confirmed before deletion; results/evidence are retained
  permanently and only the complete K3 `---TASK---` block is removed.

# Phase 10K-4 Composition Space / Embedding / Clustering Result

## Status and Completion Time

* status: `PASS`
* completed: `2026-07-28 23:23:54 +08:00`

## Delivered Capability

* Added formal product-level `dataset.composition_space` over Material Data
  Profile 2.0 formula/property semantics and explicitly bound canonical table
  resources.
* Added atomic-number-ordered normalized atomic-fraction vectors, deterministic
  center-only two-dimensional PCA with stable sign convention, optional bounded
  KMeans in the original feature space, descriptive centroid-distance outlier
  candidates, and explicit group/resource comparison on one shared basis/PCA.
* Preserved stable `objectId + sampleRef` identity; Profile property colors and
  Phase 10K-3 error/uncertainty colors are sample-bound and never inferred from
  row order.
* Added an accessible responsive SVG/table Composition Space Explorer with
  linked inspection and inert JSON fallback. The frontend consumes backend
  coordinates and does not recalculate PCA or clustering.

## Scientific and Security Boundary

* Clusters and outliers are exploratory statistical summaries, not material
  families, invalidity proofs, or anomaly authority. No UMAP/t-SNE, learned
  embeddings, model training, scientific cluster naming, external service,
  arbitrary code, real LLM calculation, or Phase 10L behavior was added.
* Caps cover 100,000 resolved rows, 20,000 analyzed samples, 118 elements, 12
  clusters, 10,000 plot points, 1,000 retained table rows, bounded warnings,
  eight-megabyte artifacts, and strict timeout/parameter validation.

## Evidence and Verification

* Real Planner/job/runtime/API artifacts, deterministic hashes, property and K3
  ML coloring, explicit comparisons, rank/cap failures, Chromium/Firefox/WebKit
  and mobile replay, numeric fallback, screenshots, accessibility, performance,
  network, and security evidence are retained under
  `docs/phase10k/evidence/phase10k4_composition_space/`.
* K4 focused backend/evidence/manifest: `24 passed`; full backend: `826 passed,
  26 skipped, 63 warnings`. Skips are explicit environment/integration gates
  and are not represented as passes.
* frontend: `51 files, 314 tests passed`; typecheck and production build PASS.
  Ruff, `uv lock --check`, `git diff --check`, evidence integrity, and historical
  K1-K3 browser/evidence regression checks passed.
* required markers: `COMPOSITION_SPACE_RUNTIME_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_PCA_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_SAMPLE_LINKAGE_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_PROPERTY_COLOR_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_DATASET_COMPARISON_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_CLUSTERING_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_BROWSER_EVIDENCE_PASS`,
  `COMPOSITION_SPACE_PERFORMANCE_EVIDENCE_PASS`,
  `NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS`, and
  `NO_SECRET_PATTERN_HITS`.
* `npm audit`: `UNAVAILABLE`; configured npmmirror endpoint returns
  `404 NOT_IMPLEMENTED`. No dependency or lockfile changed.

## Commit / CI / Queue

* implementation: `c25a815ea4b1e9601287d46a02be16603ce5cf07`; its first CI
  exposed only ignored evidence files while frontend and service-backed passed.
* evidence-closure/current implementation HEAD:
  `fb9d720b9d6009ebecab8eeff7fc60c2080a67c6`; exact-SHA CI run
  `30372914960` passed Unit, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion.
* completion record: `97a07814d4b7c7cfe9d086aedc094cf46cc0368b`;
  exact-SHA CI run `30373474557` passed Unit, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion.
* archive decision: implementation, evidence, permanent result, required local
  checks, and both exact-SHA CI gates are consistent. The completed K4 task
  block is removed by the verified queue archive commit.
* Phase 10K-4: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K-5 remains pending and was not implemented by this task.

# Phase 10K-5 Material Intelligence Integration + Browser/API Evidence Result

## 1. Conclusion

`PASS` for implementation and evidence. Completion-record CI and verified
queue archival are recorded in a closure addendum after this record commit.

## 2. Baseline

* Phase 10K-4 implementation: `fb9d720b9d6009ebecab8eeff7fc60c2080a67c6`.
* Phase 10K-4 completion record: `97a07814d4b7c7cfe9d086aedc094cf46cc0368b`.
* Phase 10K-4 archive: `0707fa7773cda57ba283cbfde5310f3e2aa99b7f`,
  exact-SHA CI run `30373921429` success.
* branch: `master`.
* initial HEAD/origin: `0707fa7773cda57ba283cbfde5310f3e2aa99b7f`.
* initial status: clean before K5 execution.

## 3. Phase 10K Component Status

### 10K-1

* Profile: Material Data Profile 2.0 is the deterministic data authority.
* semantics: formula, property, task/model, uncertainty/class, resource and
  sample roles are Profile-owned.
* readiness: data readiness remains separate from executable platform support.

### 10K-2

* Dataset Explorer: bounded overview, composition, canonical Structure
  statistics, properties, quality, comparison, and stable sample links.

### 10K-3

* Materials ML: Profile-bound regression, uncertainty, conditional
  classification, chemistry-conditioned diagnostics, and model comparison.

### 10K-4

* Composition Space: normalized atomic fractions, deterministic 2D PCA,
  bounded KMeans, property/K3 coloring, comparison, and linked inspection.

## 4. Integration Architecture

* dataset identity: exact dataset ID plus version.
* version binding: Profile ID/contract/semantic hash, complete dataset content
  hash, and sorted canonical resource hashes must all match.
* sample identity: immutable `objectId:sampleRef`; array position is forbidden.
* semantic authority: Profile 2.0 facts; Adapters own bounded analyses.
* artifact relationships: K4 accepts only exact allowlisted K3 artifacts with
  matching binding and bounded sample rows.
* frontend organization: one typed product-status surface plus independent
  K2/K3/K4 panels; no global Phase 10M workspace redesign.

## 5. Cross-Artifact Identity

* Dataset Explorer: every linked sample emits object-qualified `sampleKey`.
* ML: high-error/high-uncertainty/misclassification rows retain the same key.
* Composition Space: points and dependent ML colors use exact sample keys.
* sorted/filtered tests: different table, error, and PCA orders preserve links.
* result: `MATERIAL_INTELLIGENCE_SAMPLE_IDENTITY_EVIDENCE_PASS`.

## 6. Version / Cache Binding

* dataset version: exact, not latest-wins.
* profile: QueueWorkerRuntime resolves the persisted plan's exact `profileId`.
* artifacts: carry full deterministic content/resource binding.
* stale protection: missing/mismatched fields are `REJECTED`/`STALE`, never
  wildcarded or silently repaired.
* result: `MATERIAL_INTELLIGENCE_VERSION_BINDING_EVIDENCE_PASS`.

## 7. Capability Availability

* DataProfile readiness: deterministic data-side eligibility.
* actual Tool availability: Registry/Adapter capability is checked separately.
* frontend capability gating: combines validated Profile and product artifacts.
* ambiguous semantics: safely blocked; no first-column or legacy metric guess.
* partial data: independent coverage and product states remain visible.

## 8. Dataset Product

* Overview: PASS.
* Composition: PASS with eligible/excluded coverage.
* Structure: PASS for canonical Structure-backed resources.
* Properties: PASS with Profile-owned identity and units.
* Quality: PASS as factual diagnostics, not anomaly authority.
* Comparison: PASS with explicit dataset/group identity.

## 9. ML Integration

* regression: PASS.
* uncertainty: PASS where Profile semantics are complete.
* classification: PASS where class/probability semantics are complete.
* multiple models: exact target/prediction/model identity retained.
* chemistry: adapter-produced element/system diagnostics, no browser recompute.
* task identity: explicit Profile group; ambiguous groups are blocked.

## 10. Composition Space Integration

* composition semantics: Profile-authorized formulas only.
* property binding: exact semantic property and unit.
* ML binding: validated K3 artifact values, hashes, task/model and coverage.
* comparison: explicit resources/groups on one shared feature/PCA basis.
* sample inspection: object-qualified links survive ordering changes.

## 11. API

* job: real persisted Mock Planner jobs captured for cases A-H and replay.
* plan: validated single-tool AnalysisPlans; no K5 run-everything plan.
* runtime: QueueWorkerRuntime plus Registry/Adapter execution.
* artifacts: persisted inert products, summaries, recipes, and plots.
* retrieval: API-style job/artifact captures include persisted IDs and hashes.
* version/provenance: exact Profile/dataset/resource/params bindings retained.

## 12. Frontend

* Profile: authoritative readiness/status source.
* Dataset Overview, Properties, Data Quality: validated K2 artifact views.
* ML: validated K3 numeric/accessible views.
* Composition Space and Comparison: validated K4 views.
* partial states: `PRODUCED`, `READY_NOT_RUN`, `UNAVAILABLE`,
  `PROFILE_AUTHORITY_UNAVAILABLE`, `REJECTED`, `STALE`, and
  `CAPABILITY_MISMATCH`.
* error isolation: settled endpoint refresh preserves valid sibling products.

## 13. Report / Recipe

* artifact inclusion: persisted K2/K3/K4 artifact IDs and hashes are captured.
* provenance: dataset/Profile/resource/tool identities are exact.
* recipe: complete tool params and resource binding.
* deterministic rerun: structured results replay identically after removing
  runtime-owned IDs.

## 14. Evidence Cases

* materials table: PASS; ML is N/A.
* structure-enriched: PASS; ML and Composition Space are N/A where inapplicable.
* regression: PASS.
* uncertainty: PASS.
* classification: PASS; Composition Space is N/A for this case.
* comparison: PASS; ML is N/A.
* partial capability: PASS; ML correctly reports UNAVAILABLE.
* ambiguous semantics: PASS; ML is SAFELY_BLOCKED and composition is conditional.

## 15. Cross-Product Consistency

* units/property/task/model identity: exact and never inferred by display label.
* sample/dataset identity: exact object-qualified and version-bound.
* coverage disclosure: total, eligible/evaluated, excluded/matched/missing as
  appropriate for each product.

## 16. Partial Failure Isolation

* tested failure: insufficient/stale Composition Space and missing Profile
  authority while valid siblings remain.
* unaffected capabilities: validated Dataset Explorer or ML products remain.
* frontend behavior: typed partial state with independent panels.
* result: `MATERIAL_INTELLIGENCE_PARTIAL_FAILURE_ISOLATION_PASS`.

## 17. Browser Matrix

* Chromium: all A-H product cases, screenshots, keyboard and network audits.
* Firefox: major dataset, ML, composition, partial and ambiguity paths.
* WebKit: major dataset, ML, composition, partial and ambiguity paths.
* mobile: Dataset Overview, Regression, and Composition Space at 390x844.

## 18. Accessibility

* keyboard/labels: interactive controls and selectors are labeled and operable.
* chart alternatives/tables: numeric summaries and bounded tables are retained.
* warnings: textual states do not rely on color.
* mobile: controls and sample details remain readable without catastrophic
  viewport overflow.

## 19. Performance

* small (40): Dataset 24.766 ms/13,558 B; Regression 33.043 ms/29,910 B;
  Composition 56.437 ms/27,177 B.
* medium (5,000): Dataset 411.196 ms/28,114 B; Regression 1,473.496 ms/
  679,932 B; Composition 980.987 ms/2,028,220 B.
* near-cap: Dataset 100,000 rows 7,554.176 ms/28,597 B; Regression 100,000
  rows 28,068.832 ms/699,850 B; Composition 20,000 rows 3,579.665 ms/
  8,063,785 B.
* frontend/memory: bounded display rows/points and no duplicate source table.
* overall envelope: PASS; products measured independently because Phase 10L
  multi-tool planning does not exist.

## 20. Security

* untrusted text remains React/plain JSON text; no raw HTML.
* arbitrary code/artifact JS: none.
* external network: `NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS`.
* secrets: `NO_SECRET_PATTERN_HITS`.

## 21. Tool Registry Final Phase 10K Surface

* general tools: existing table/composition capabilities remain unchanged.
* dataset: `dataset.materials_explorer`.
* ML: `ml.regression_evaluation`, `ml.uncertainty_evaluation`, and
  `ml.classification_evaluation`.
* composition: `dataset.composition_space`.
* requirements: exact Profile 2.0 semantics and canonical resource bindings.
* outputs/readiness: inert structured artifacts; each capability independent.
* no K5 integration or run-everything Tool ID was added.

## 22. Explicit Phase 10K Limits

Not implemented: capability-aware Agent, automatic multi-tool planning, LLM
result interpretation, Unified Scientific Workspace, CrystalNN/VoronoiNN,
experimental XRD, trajectory analytics, Electronic Band/DOS, or Future advanced
capabilities. These are assigned to later approved phases, not K5 failures.

## 23. Files Changed

* backend: hashing, K2-K4 binding, exact Profile resolution/runtime guard, and
  ambiguity safety.
* frontend: integration mapper/panel and K2-K4 product composition.
* tests/evidence: unit, component, integration, A-H runtime/API/browser,
  identity, replay, performance, accessibility, network, and security.
* docs/persistent: K5 contracts, evidence matrices, Phase 10K summary, next
  scope, schema/index/capability matrix, ADR, board, progress, and changelog.
* dependency/lockfile: unchanged.

## 24. Checks

* git diff --check: PASS.
* uv lock: PASS.
* backend: PASS, `837 passed, 27 skipped, 63 warnings`.
* frontend: PASS, `52 files, 323 tests`.
* typecheck/build: PASS.
* service-backed local: UNAVAILABLE (Docker absent); CI: PASS.
* no-skipped CI assertion: PASS.
* docs/TASKS/evidence integrity/security: PASS.

## 25. Commit / CI

### Integration Implementation

* commit/exact SHA: `e4639a1168f4bac7f4c786c48657559038bd7230`.
* CI run: `30382233569`.
* Unit, Frontend Typecheck & Build, service-backed integration, and no-skipped:
  all success.

### Completion Record

* commit/exact SHA/CI: pending this completion-record commit.

## 26. Queue State

* Phase 10K-5: `COMPLETED_AWAITING_COMPLETION_RECORD_CI_AND_ARCHIVE`.
* Phase 10K: `READY_WITH_EXPLICIT_LIMITS_AWAITING_ARCHIVE`.
* Phase 10L-0: `NEXT / AWAITING COMPLETE PROMPT`, not started.

## 27. Phase 10K Final Readiness

* DataProfile, Dataset Explorer, Materials ML, Composition Space, API,
  frontend, sample identity, version binding, browser, accessibility,
  performance, and security: READY within documented caps.
* overall: `READY_WITH_EXPLICIT_LIMITS` pending completion-record CI/archive.

## 28. Whether Allowed to Enter Phase 10L-0

不可以：completion-record exact-SHA CI 与 verified K5 archive 尚未闭合。

## 29. Next Phase

**Phase 10L-0：Agent / Planner Capability Audit**，仅为 NEXT；本任务未实现。

## 30. Completion-Record CI and Queue Closure

* closure status: `PASS`.
* completion-record commit: `81d44467c9b0d9e8bef3d4dec38d6a85e3d2aebe`.
* completion-record exact-SHA CI run: `30382583135`, success.
* CI jobs: Unit Tests, Frontend Typecheck & Build, and PostgreSQL/Redis/MinIO
  Service-backed Integration all succeeded; the no-skipped assertion passed.
* archive verification: implementation/evidence, permanent result, required
  checks, and both exact-SHA CI gates are consistent. Only the completed K5
  `---TASK---` block is removed; evidence and result history are retained.
* Phase 10K-5: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10K: `COMPLETE / READY_WITH_EXPLICIT_LIMITS`.
* Phase 10L-0: `NEXT / NOT_STARTED`.

# Phase 10L-0 Agent / Planner Capability Audit Result

## 1. Conclusion

`PASS` for the architecture/capability audit. Completion-record CI and verified
queue archival are recorded in a closure addendum after that gate succeeds.

## 2. Baseline

* Phase 10K: `COMPLETE / READY_WITH_EXPLICIT_LIMITS`.
* Phase 10K-5 archive: `17de1f91cef6e94a5a1f4ae684fb3e1b756f0906`,
  exact-SHA CI run `30382914410` success.
* branch: `master`.
* initial HEAD/origin: `17de1f91cef6e94a5a1f4ae684fb3e1b756f0906`.
* initial status: clean before Phase 10L-0 execution.

## 3. Current Planner Architecture

```text
POST /planner/jobs
  -> persisted DataProfile + Registry snapshot
  -> Mock deterministic router OR optional OpenAI-compatible JSON provider
  -> AnalysisPlan 0.1
  -> PlanValidator
  -> persisted plan/hash + job
  -> QueueWorkerRuntime
  -> Registry lookup + registered Adapter
  -> ToolCalls/events/artifacts
  -> PlannerWorkbench timeline and results
```

The Mock path reads selected Profile 2.0 facts directly. The live-LLM prompt
receives only a shallow table/structure Profile summary and a reduced MVP tool
inventory. PlanValidator receives no Profile.

## 4. Current AnalysisPlan

* schema/version: `AnalysisPlan` schema version `0.1`.
* ToolCall count: a non-empty ordered `steps` array; no plan-level maximum.
* ordering: deterministic list order and unique step IDs.
* dependencies: absent.
* artifact binding: artifact-shaped input refs exist syntactically, but no
  producer-step identity or previous-output runtime injection exists.
* persistence: canonical plan JSON, hash, provider, job binding, events,
  ToolCalls, and artifacts are persisted.
* versioning: provider is stored; model/prompt version and complete provider
  configuration are not.
* failure: first failed step stops later execution, job fails, and already
  written artifacts remain; no partial-success status or automatic retry.

## 5. Multi-Tool Reality

`SEQUENTIAL_INDEPENDENT`.

QueueWorkerRuntime executes multiple steps in order, and the existing phonon
band plus Brillouin-zone test proves a real two-step job. Both steps consume
independent pre-existing inputs. There is no dependency graph or prior-step
artifact binding, so the product is not dependency-aware multi-tool planning.

## 6. Mock Planner

* routing: fixed-priority phrase/substring predicates and named plan builders.
* keyword dependence: high; 34 route predicates and 56 prompt-check sites.
* resource/Profile awareness: partial and strongest for Phase 10K ML and
  Composition Space; selected structure/trajectory/phonon/volume checks exist.
* Registry awareness: verifies fixed IDs exist; it does not rank eligible
  tools from capability metadata.
* ambiguity: selected ML ambiguity routes safely to diagnostics, but no general
  clarification state exists.
* params: exact Profile semantic binding for K3/K4; heuristic/default binding
  remains in older routes.
* classification: `PARTIAL_PROFILE_AWARE`.

## 7. LLM Planner

* architecture: explicit opt-in OpenAI-compatible JSON completion; Mock is the
  default and CI path.
* prompt: raw goal, dataset/Profile IDs, shallow table/structure facts, quality
  count, and 41 MVP IDs/descriptions/artifact types/parameter names.
* missing context: full Profile semantic groups/readiness, trajectory/phonon/
  volumetric facts, full parameter constraints, input schemas, caps, ranking,
  prior plans, and prior errors.
* enforcement: JSON object parsing followed by mandatory PlanValidator.
* retry/repair/fallback: one response-format compatibility retry on HTTP 400 is
  transport handling, not plan repair; no validation repair or Mock fallback.
* `REAL_LLM_CALLS = 0` for this audit.

## 8. DataProfile to Planner Integration

* Mock: resource kind, composition, structure, trajectory, phonon, volumetric,
  regression, uncertainty, classification, and readiness are consumed unevenly;
  K3/K4 are the strongest Profile-aware paths.
* LLM: table columns and a shallow structure summary only; no full Profile 2.0
  semantic groups/readiness.
* Validator: no Profile or semantic-readiness validation.

## 9. Tool Registry Planner Readiness

* inventory: 53 tools, 41 MVP, 11 V1, one V2 across eight domains.
* present: identity, descriptions, input object options, params JSON Schema,
  output artifact metadata, costs, timeout, permissions, and resource caps.
* missing: uniform semantic prerequisites, Profile readiness mapping, planner
  ranking hints, collision groups, and composition constraints.
* classification: `PARTIAL_PLANNER_CAPABILITY_REGISTRY`.

## 10. PlanValidator

* validates Pydantic plan shape, non-empty/unique steps, known MVP tool,
  credential-like parameter rejection, parameter JSON Schema, and known enum
  values.
* does not validate resource kind/existence, Profile readiness, scientific
  semantics, produced-artifact compatibility, explicit dependencies, max step
  count, duplicate calls, or cross-step bindings.
* classification: `SCHEMA_AND_REGISTRY_VALIDATOR`.

## 11. Tool Selection

* table/viz and older ML: phrase routes plus column heuristics/defaults.
* dataset and Phase 10K ML/composition space: product-specific Profile facts,
  readiness, semantic groups, and fixed Registry IDs.
* structure/trajectory/phonon/BZ/volumetric: phrase plus resource-presence
  predicates and approved fixed parameters.
* there is no cross-domain candidate ranking or capability composition pass.

## 12. Representative Prompt Audit

* composition distribution: `dataset.materials_explorer`; coherent single
  product, no element/system-specific composition.
* structure reasonableness: `structure.summary`; no coordination/RDF/XRD/viewer
  composition.
* poor model predictions: `ml.basic_metrics`; misses product regression and
  linked chemistry/sample diagnostics.
* uncertainty trust: `ml.basic_metrics`; misses ready uncertainty evaluator.
* broad phonon quality: `ml.basic_metrics`; resource-incompatible fallback.
* charge-density features: `structure.volumetric_data`; correct preparation,
  no interpretation.
* broad dataset analysis: `dataset.materials_explorer`; no ranked composition.
* explicit `formation_energy` distribution: `viz.histogram` incorrectly binds
  `band_gap`, proving heuristic parameter drift.

## 13. Analysis Intent

No structured intent object exists. The request is raw prompt plus dataset,
Profile, and Registry IDs; `AnalysisPlan.goal` repeats the raw prompt. Decision:
`REQUIRED`, subject to reviewer approval of its exact shape.

## 14. Ambiguity / Clarification

Some Phase 10K ML ambiguity is typed and safely redirected, but there is no
general clarification state, follow-up answer binding, or conversation context.

## 15. Plan Repair

There is no JSON/schema/scientific validation repair loop. Invalid provider
output is rejected and persists no plan/job. Retry limits for repair therefore
do not exist.

## 16. Result Interpretation

Deterministic Adapter summaries, warnings, recipes, and historical report paths
exist. No LLM receives bounded scientific result context, and no grounded
interpretation/no-invention contract or recommendation stage exists.

## 17. Frontend Planner UX

The UI supports prompt/resource selection, create-and-run, plan/timeline/call/
artifact inspection, and typed errors. The generated plan becomes visible only
after create/enqueue. Plan editing, approval-before-run, clarification, cancel,
and same-job retry are absent.

## 18. Security Boundary

The LLM cannot execute Python, shell, filesystem, adapters, or scientific
libraries. Unknown/non-MVP tools, credential-shaped params, and schema-invalid
params are rejected. BYOK is resolved separately. Missing caps include prompt
length, plan step count, Registry prompt budget, and API upper bounds for some
provider tuning fields. Future interpretation requires an explicit untrusted
artifact-content boundary.

## 19. Planner Test Coverage

Existing coverage includes deterministic Mock routes, fake live-provider JSON/
error cases, PlanValidator rejection, persistence/hash, sequential Runtime,
read APIs, frontend PlannerWorkbench, service-backed jobs, and default-Mock
network isolation. It does not prove capability-ranked planning, dependencies,
repair, clarification, or result interpretation.

## 20. Planner Maturity

`CURRENT_LEVEL = 3` on the audited Level 0-5 scale: data/profile-aware tool
selection exists but is uneven. Overall product classification:
`PROFILE_AWARE_SINGLE_TOOL_PLANNER_WITH_NARROW_SEQUENTIAL_INDEPENDENT_COMPOSITION`.

## 21. Gap Matrix

* READY: Profile transport, strict Registry execution metadata, deterministic
  single-tool plans, persisted plans/hashes, timeline/artifacts.
* REUSABLE_FOUNDATION: Profile 2.0, ordered steps, sequential Runtime,
  summaries/recipes.
* PARTIAL: Profile-aware routing, parameter binding, ambiguity, failure
  isolation, Planner provenance, plan preview.
* MISSING_10L: Analysis Intent, capability eligibility/ranking, semantic
  validation, dependencies/artifact binding, caps, repair, interpretation, and
  broad Agent evidence.
* DEFER_10M: plan editing/approval and unified workspace UX.
* DEFER_10N: professional tool coverage.
* FUTURE/NOT_NEEDED: long-term memory and generic workflow/DAG products;
  arbitrary code remains prohibited.

## 22. Recommended Phase 10L Scope

* 10L-1: strict lightweight Analysis Intent and ambiguity outcome.
* 10L-2: capability-aware selection over Profile plus planner-facing metadata,
  uniform binding, typed unsupported outcomes, and plan/prompt caps.
* 10L-3: smallest approved bounded dependency/artifact model, not a generic DAG.
* 10L-4: bounded structured interpretation over computed facts with explicit
  no-invention rules.
* 10L-5: five real natural-language Profile-to-plan-to-runtime-to-artifact-to-
  interpretation evidence cases.

## 23. Reviewer Decisions Required

Reviewer approval is required for intent shape, ambiguity/clarification,
capability metadata ownership, AnalysisPlan evolution, sequence versus
restricted dependencies, failure/cancellation, repair policy, pre-execution
control ownership, and interpretation provider/context policy.

## 24. Production Behavior Changes

```text
Production Planner Behavior Changes:
NONE
```

No AnalysisPlan schema, Registry contract, PlanValidator, Runtime, dependency,
public tool, Adapter, Planner route, or frontend behavior changed.

## 25. Files Changed

Only `TASKS.md`, `results.md`, Phase 10L docs/evidence, `docs/index.md`, and
persistent project-memory files. No production source, dependency, or lockfile
changed.

## 26. Checks

* Planner focused: PASS, `92 passed, 1 skipped, 1 warning`; skip disclosed.
* backend full: PASS, `837 passed, 27 skipped, 63 warnings`.
* frontend full: PASS, 52 files and 323 tests.
* typecheck/build: PASS.
* Phase 10 closure/evidence and trajectory performance integrity: PASS.
* `uv lock --check`, `git diff --check`, docs links, TASKS structure, and Phase
  10L-0 evidence integrity: PASS.
* local service-backed: UNAVAILABLE, Docker absent; `25 skipped, 12 deselected`.
* audit exact-SHA CI service-backed/no-skipped: PASS.

## 27. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L0_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

## 28. Commit / CI

### Audit Commit

* commit/exact SHA: `a7f8b143129d4cf3ced95373d8d81199b06f7ca6`.
* CI run `30414233888`: Unit, Frontend Typecheck & Build, service-backed
  integration, and no-skipped all success.

### Completion Record

* commit/exact SHA/CI: pending this completion-record commit.

## 29. Queue State

* Phase 10L-0: `COMPLETED_AWAITING_COMPLETION_RECORD_CI_AND_ARCHIVE`.
* Phase 10L-1: `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.

## 30. Whether Allowed to Enter Phase 10L-1 Automatically

`NO`. Phase 10L-1 requires reviewer review of the real Phase 10L-0 architecture
audit and an explicit complete execution prompt.

## 31. Next Action

Return Phase 10K-5 and Phase 10L-0 results to the reviewer for Phase 10L
architecture decision and Phase 10L-1 execution prompt. Do not implement or
queue Phase 10L-1 automatically.

## 32. Completion-Record CI and Queue Closure

* closure status: `PASS`.
* completion-record commit: `ee86745707d9388b28f85051c5994e403c095c21`.
* completion-record exact-SHA CI run: `30414599167`, success.
* CI jobs: Unit Tests, Frontend Typecheck & Build, and PostgreSQL/Redis/MinIO
  Service-backed Integration all succeeded; the no-skipped assertion passed.
* archive verification: audit docs/evidence, permanent result, local checks,
  audit exact-SHA CI, and completion-record exact-SHA CI are consistent. Only
  the completed Phase 10L-0 `---TASK---` block is removed; evidence and result
  history remain.
* Phase 10L-0: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10L-1: `REVIEWER_GATE / AWAITING REVIEWER PROMPT` and is not queued.

# Phase 10L-1 Analysis Intent Contract + Bounded Clarification Result

## 1. Conclusion

`PASS` for implementation at corrected implementation HEAD
`844eb149a4c528d28db9fdf70dddfaf015e91d5a`, exact-SHA CI run
`30425804801`. Completion-record CI and verified queue archive are recorded in
a closure addendum after those gates succeed.

## 2. Baseline

* Phase 10K: `COMPLETE / READY_WITH_EXPLICIT_LIMITS`.
* Phase 10L-0: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT` at `83f5c44`.
* branch: `master`.
* initial HEAD/origin: `83f5c44eb10843f57ae79902d2db5cc85c302b43`.
* initial TASKS state: Phase 10L-1 sole active task; Phase 10L-2 reviewer gate.

## 3. Entry Audit

The existing production flow was `POST /planner/jobs -> provider ->
AnalysisPlan 0.1 -> PlanValidator -> persisted plan/job -> QueueWorkerRuntime`.
The additive canonical v1 flow is `exact DataProfile 2.0 -> AnalysisIntent ->
existing Planner -> existing plan/job/runtime`. Intent-plan-job association is
stored outside AnalysisPlan. Registry, PlanValidator, Runtime, and route
precedence were explicit non-change boundaries.

## 4. AnalysisIntent Contract

* schema/version: independent strict `AnalysisIntent` `1.0` in Python,
  checked-in JSON Schema, and TypeScript.
* identity: deterministic `intentHash` over canonical semantic content and
  deterministic `intentId`; runtime timestamp is excluded.
* goal: secret-redacted original `rawGoal` plus whitespace-only
  `normalizedGoal`; semantic expansion fails validation.
* scope: exact dataset version, Profile ID/contract/semantic hash, object ID,
  object hash, resource kind, and explicit target/model/group identities.
* vocabulary: bounded scientific intent, desired output, capability need,
  ambiguity, diagnostic, constraint, warning, and provenance enums/fields.

## 5. Outcome Semantics

* `READY`: exact scope and required Profile facts exist; no blocking ambiguity.
* `NEEDS_CLARIFICATION`: a real current Profile/resource candidate can resolve
  the ambiguity within one round.
* `UNSUPPORTED`: missing data, Future/Not Planned scope, unsafe execution, or
  ambiguity that cannot be resolved within the bounded policy.
* Blocking ambiguity can never coexist with `READY`.

## 6. Bounded Clarification

* maximum rounds: 1.
* maximum questions: 3.
* types: `SELECT_ONE`, `SELECT_MANY`, and `CONFIRM`.
* options are exact current DataProfile/resource facts, never LLM inventions.
* answers bind intent/question/option/Profile hash and create an immutable child
  Intent with a new ID/hash and parent/answer provenance.
* stale Profile/resource, invalid option, incomplete answers, and second round
  are typed failures.

## 7. Mock / Deterministic Path

The default deterministic builder uses allowlisted raw-goal rules plus exact
Profile 2.0 facts. It performs no network request, tool selection, or silent
fallback and emits deterministic semantic identity. It does not attempt Phase
10L-2 capability ranking.

## 8. LLM Intent Path

The optional path reuses the existing OpenAI-compatible bounded transport and
adds no dependency. Its prompt contains only redacted goal, selected exact
identity, bounded Profile facts, schema, vocabulary, and safety rules. Exactly
one JSON object is accepted; fences, prose, duplicate keys, unknown fields,
invented IDs/candidates, over-cap arrays, and inconsistent outcomes fail with
no repair and no Mock fallback. Default evidence used `REAL_LLM_CALLS = 0`.

## 9. Validation

An independent `AnalysisIntentValidator` validates schema, canonical identity,
caps/depth/bytes, exact Profile/resource/target facts, capability facts,
goal normalization, outcome consistency, unique semantic identities,
Profile-derived question candidates, immutable revision, Future/Not Planned,
and execution boundaries. It does not validate tools, plans, or Runtime.

## 10. Persistence / Migration

* tables: `analysis_intents` and `analysis_intent_executions`.
* migration: Alembic `0003_phase10l1_intents`, upgrade and downgrade defined.
* repositories: in-memory and SQLAlchemy with immutable/idempotent intent save
  and immutable plan/job association.
* PostgreSQL: exact-SHA CI ran migration, verified tables/indexes, persisted the
  Intent and association, and passed no-skipped.

## 11. API

Additive typed create/get/clarify routes were added. `/planner/jobs` opts into
v1 with `intentSchemaVersion` or a persisted `intentId`. Non-READY returns
before AnalysisPlan/job/enqueue. READY invokes the unchanged provider with the
preserved raw goal and stores the external association. Job detail exposes the
associated Intent additively.

## 12. Frontend

PlannerWorkbench opts into v1 and displays original goal, intents, exact scope,
targets, desired outputs, warnings, outcome, provider, bounded questions,
unsupported reasons, disabled Run state, and inert developer JSON. A valid
answer displays the immutable revision and continues the existing Planner.
Keyboard/focus labels, no horizontal overflow, and 390x844 mobile passed.

## 13. Compatibility

AnalysisPlan remains `0.1`; stored plan hashes and historical jobs/artifacts are
unchanged. Legacy API consumers may omit Intent fields and retain the prior
Planner behavior. Gated READY requests preserve current Mock and fake-provider
selection. Tool Registry, PlanValidator, QueueWorkerRuntime, and Phase 10K
products regress without semantic changes.

## 14. Caps / Performance

Caps include 16,384 goal characters; 32 resource refs, targets, desired outputs,
ambiguities, and diagnostics; 16 scientific intents/capability needs; three
questions; one round; JSON depth 12; and serialized size 262,144 bytes. The
near-cap evidence used 16,384 characters and 32 resources, producing about
23.7 KB with about 181 KB peak traced memory and about 11 ms build/validate
time. Failures are typed and bounded.

## 15. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L1_EXTERNAL_NETWORK_REQUESTS
NO_ANALYSIS_INTENT_ARBITRARY_CODE_EXECUTION
NO_ANALYSIS_INTENT_ARTIFACT_JAVASCRIPT
NO_SECRET_PATTERN_HITS
```

Raw HTML, script text, prompt injection, and credential-shaped text remain
inert; credential values are redacted before persistence/evidence. Intent has
no shell, filesystem, network, code, artifact-JS, or execution authority.

## 16. Evidence

Evidence is retained at
`docs/phase10l/evidence/phase10l1_analysis_intent/`: sanitized API READY,
clarification, revision, unsupported/no-job, SQLite persistence, PostgreSQL CI
gate, performance, security, browser DOM/network/console, six screenshots, and
an LF-normalized text/raw-PNG SHA-256 manifest.

## 17. Tests

* focused backend: `27 passed`.
* focused PlannerWorkbench: `22 passed`.
* full backend: `864 passed, 28 skipped, 63 warnings` locally.
* full frontend: 52 files / `325 passed`.
* typecheck, production build, `uv lock --check`, `git diff --check`: PASS.
* Phase 10 closure/evidence: PASS.
* browser: Chromium 128, Firefox 128, WebKit 18, mobile 390x844 PASS.
* local service-backed: `UNAVAILABLE`, Docker command absent; 26 service tests
  skipped and not reported as passed.
* exact-SHA CI service-backed/no-skipped: PASS.

## 18. Production Behavior Changes

Canonical PlannerWorkbench requests now generate/persist an Intent before
planning. `READY` preserves old tool selection and params. `NEEDS_CLARIFICATION`
and `UNSUPPORTED` create no plan/job and enqueue nothing. AnalysisPlan,
PlanValidator, Tool Registry, and QueueWorkerRuntime semantics did not change.
Historical unversioned API requests remain compatible.

## 19. Files Changed

Backend/API repositories and migration, schema contracts, provider Intent
builder/validator, PlannerWorkbench/API types, focused/integration/browser
tests, CI service gate, evidence, Phase 10L docs, shared schema/index, TASKS,
and persistent records. Dependency and lock files are unchanged.

## 20. Commit / CI

* initial implementation: `365953f3f89c584fb82aafb9c20774e005141957`;
  CI run `30425561782` failed only the cross-platform evidence byte hash.
* corrected implementation HEAD:
  `844eb149a4c528d28db9fdf70dddfaf015e91d5a`.
* implementation exact-SHA CI: run `30425804801`, Unit, Frontend,
  PostgreSQL/Redis/MinIO, migration, and no-skipped success.
* completion-record commit:
  `b4cd656e1c03bb7d6ea406ed0f2dbd828dfb2dd9`.
* completion-record exact-SHA CI: run `30426248141`, Unit, Frontend,
  PostgreSQL/Redis/MinIO, migration, and no-skipped success.
* archive commit/CI: this verified queue archive change; exact SHA and CI are
  reported after the commit gate closes.

## 21. Explicit Non-Scope Confirmation

No Capability-Aware Planner, Registry planner metadata, Eligibility Resolver,
AnalysisPlan 0.2, dependencies, artifact binding, Runtime partial success, plan
repair, interpretation, Workspace redesign, professional science, Future/Not
Planned capability, new LLM dependency, arbitrary code, or external scientific
API was implemented.

## 22. Remaining Phase 10L Gaps

10L-2 owns capability-aware selection and any approved planner metadata; 10L-3
owns the smallest approved dependency/artifact model; 10L-4 owns grounded
result interpretation; 10L-5 owns full natural-language evidence closure.
These are gaps only, not executable tasks.

## 23. Queue State

* Phase 10L-1: `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
* Phase 10L-2: `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.

## 24. Whether Allowed to Enter Phase 10L-2 Automatically

`NO`.

## 25. Next Action

Return the complete Phase 10L-1 result to the reviewer after the queue archive
commit passes exact-SHA CI. Do not queue or execute Phase 10L-2.

### Completion-record CI and queue archive authorization

* 核验时间：2026-07-29 13:52:25 +08:00。
* completion-record commit：
  `b4cd656e1c03bb7d6ea406ed0f2dbd828dfb2dd9`。
* exact-SHA CI：run `30426248141` success；Unit Tests、Frontend Typecheck &
  Build、PostgreSQL/Redis/MinIO migration/service-backed integration 和
  no-skipped assertion 均成功。
* 归档决定：implementation、evidence、测试、永久结果、completion record、
  两次 exact-SHA CI 和 persistent 状态一致，允许在本次 queue archive commit
  中删除已完成的 Phase 10L-1 task block。Phase 10L-2 保持
  `REVIEWER_GATE / AWAITING REVIEWER PROMPT`，未创建 executable task。

# Phase 10L-2 Capability-Aware Planner + Eligibility Resolver Result

## 1. Conclusion

`PASS` for corrected implementation
`9786e405f1938b514b95ccbeb1cdb6d4b26dde18`, exact-SHA CI run
`30511654404`. Completion-record CI and verified queue archive remain separate
gates and will be recorded in a closure addendum.

## 2. Baseline and Entry Gate

- Phase 10K: `COMPLETE / READY_WITH_EXPLICIT_LIMITS`.
- Phase 10L-0 and 10L-1: archived; L1 archive baseline `dbcda192...`.
- initial branch/HEAD/origin: `master` / `dbcda192...` / `dbcda192...`.
- initial worktree: clean; one L2 task block; L3 reviewer gate only.

## 3. Entry Audit and Previous Failure Modes

The prior READY path used fixed Mock routes or a broad provider Registry
summary without one auditable contextual gate. The new path inserts Registry
snapshot, eligibility, selection, exact binding, and independent context
validation before unchanged AnalysisPlan 0.1.

## 4. Registry Planner-Metadata Contract

`ToolPlannerMetadata 1.0` records stable tool/version, availability, intents,
needs, outputs, resource/object kinds, Profile prerequisites, targets,
cardinality, bindings, existing artifact outputs, cost, collision/composition,
and the registered-adapter-only execution boundary.

## 5. Metadata Validation and Capability Inventory

All 53 Registry entries are covered; 38 are currently available. Entries are
stable-key sorted. Deployment-unavailable/Future entries are non-selectable.
Unknown fields/enums, invalid params/outputs, impossible cardinality,
executable content, and availability contradictions are rejected.

## 6. Eligibility Resolution Contract

`EligibilityResolution 1.0` has deterministic ID/hash and exact Intent,
Profile, dataset/resource, Registry snapshot, candidate, eligible/rejected,
reason, prerequisite, binding-domain, ordering, diagnostic, and resolver
provenance fields. Runtime timestamps do not affect semantic identity.

## 7. Eligibility Rules and Typed Rejections

Candidates must exist, be invocable, have valid metadata, cover exact
intent/need/output facts, accept exact resources/targets, satisfy Profile
facts/cardinality/bindings/caps, and preserve safety/collision boundaries.
Every rejected candidate has bounded typed reasons; caps never truncate
semantics.

## 8. Candidate Projection and LLM Isolation

Providers receive eligible stable IDs, exact accepted identities/bindings,
coverage, cost, and collision facts only. They do not receive rejected tools,
the full Registry, paths, code, secrets, or unbounded Profile data.

```text
PROVIDER_VISIBLE_TOOL_IDS == ELIGIBLE_TOOL_IDS: PASS
NO_REJECTED_CANDIDATE_LEAK_TO_LLM: PASS
```

## 9. Deterministic Ranking and Selection

Mock ranking uses exact intent, need, output, resource/target applicability,
binding completeness, warnings, cost, then stable tool identity. Registry/UI
order has no authority. Independent multi-selection is bounded and rejects
duplicates/collisions; no dependency edge is created.

## 10. Exact Semantic Parameter Binding

Bindings come only from exact Intent identities, declared Profile facts,
bounded literals, or declared repository defaults and retain source identity.
First-column/display-label/fuzzy target, guessed units/models, raw LLM IDs,
code/path/URL, and unrelated-fact substitution are prohibited.

## 11. LLM Selection and Strict Parsing

The existing OpenAI-compatible transport receives the eligible projection and
strict schema. Only one bare JSON object is accepted. Fences, prose,
duplicate/unknown fields, invented IDs, invalid domains, dependencies,
code/path/URL, over-cap content, and inconsistent outcomes fail. No Mock
fallback or new LLM dependency exists.

## 12. One Validation-Guided Repair

Only a strictly parsed repairable LLM decision can receive one repair over the
unchanged candidate/binding domain. Hashes, typed diagnostics, repair count,
and outcome are retained. Exhaustion returns `VALIDATION_FAILED`; Mock output
is never repaired.

## 13. Capability-Context Validation

The independent validator recomputes Intent/Profile/Registry identity,
eligibility, coverage, parameter provenance, caps, duplicates/collisions,
independent composition, and no-dependency boundaries. The unchanged plan then
passes the existing PlanValidator.

## 14. Planning Outcomes and No-Job Semantics

Outcomes are `PLAN_READY`, `NEEDS_CLARIFICATION`, `UNSUPPORTED`,
`CAPABILITY_MISMATCH`, and `VALIDATION_FAILED`. Only PLAN_READY persists a
plan/job or enqueues Runtime work.

```text
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES: PASS
ANALYSIS_PLAN_SCHEMA_VERSION = 0.1
```

## 15. Persistence and Migration

Alembic `0004_phase10l2_capability_planning` adds immutable resolution,
decision, and execution-association tables. In-memory, SQLite migration, and
PostgreSQL paths verify identity, idempotency, conflicting-write rejection,
and external Intent/plan/job association. Upgrade/downgrade/re-upgrade pass.

## 16. API Behavior

The canonical Intent path loads exact READY Intent/Profile, resolves,
selects/binds/validates, and creates unchanged plan/job/runtime state only for
PLAN_READY. Responses add outcome, resolution, decision, eligible IDs,
diagnostics, and job association. Legacy behavior remains explicit.

## 17. Frontend and Browser Evidence

PlannerWorkbench shows outcome, scope, capability/tool IDs, output coverage,
exact bindings/provenance, warnings, repair state, failures, and inert JSON.
Run is disabled unless PLAN_READY. Chromium 128, Firefox 128, WebKit 18, and
Chromium 390x844 passed focus/status, console/network, inert-content, and
overflow checks.

## 18. Compatibility

AnalysisIntent remains 1.0; AnalysisPlan remains 0.1. Historical plan hashes,
jobs, and artifacts remain readable. Existing PlanValidator, Registry
execution contracts, route precedence, QueueWorkerRuntime, Phase 10K, and
Phase 10L-1 behavior are not weakened.

## 19. Caps and Performance

Caps are 64 Registry candidates, 32 eligible, 256 diagnostics, 64 binding
values, 4 independent tools, depth 14, and 524,288 serialized bytes. Near-cap:
53 tools, 174 diagnostics, 101,213-byte resolution, 1,967-byte decision,
209.439 ms, and 2,339,126 traced peak bytes. This is bounded local evidence,
not a production capacity claim.

## 20. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L2_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS
NO_CAPABILITY_PLANNER_ARBITRARY_CODE_EXECUTION
NO_CAPABILITY_PLANNER_SHELL_OR_FILESYSTEM_AUTHORITY
NO_CAPABILITY_PLANNER_ARTIFACT_JAVASCRIPT
NO_FULL_REGISTRY_LEAK_TO_LLM
NO_REJECTED_CANDIDATE_LEAK_TO_LLM
NO_SECRET_PATTERN_HITS
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES
```

Prompt injection, HTML/script, credential text, duplicate JSON keys, invented
or stale IDs, oversized content, and executable strings remain inert or typed
failures. No new dependency/external authority was added.

## 21. Required Audit Regressions

Formation energy/band gap bind distinct targets; prediction does not fall back
to basic metrics; uncertainty selects only explicit support; phonon never falls
through to ML/table/visual tools; broad dataset analysis is not Registry-first;
resource kinds do not interchange; candidate isolation and binding provenance
are retained.

## 22. Evidence Inventory and Manifest

`docs/phase10l/evidence/phase10l2_capability_aware_planner/` retains entry,
metadata/snapshot, eligibility/rejection, isolation, ranking, binding,
regression, strict LLM/repair, API, persistence, performance, security,
browser/mobile, screenshots, captures, and LF-normalized text/raw-PNG SHA-256
manifest evidence.

## 23. Test Results

- focused L2 backend/evidence: `27 passed`; L1 regression: `23 passed`.
- full local backend: `892 passed, 29 skipped, 63 warnings`; corrected CI unit:
  `892 passed, 1 skipped, 28 deselected, 63 warnings`.
- full frontend: 52 files / `327 passed`; PlannerWorkbench: `24 passed`.
- typecheck, build, lock, diff, evidence, Phase 10 closure: PASS.
- local service-backed: UNAVAILABLE (Docker absent), not reported as passed.
- exact-SHA CI service-backed: `27 passed, 0 skipped, 0 failed`.
- browser: Chromium/Firefox/WebKit and 390x844 mobile PASS.
- npm audit: UNAVAILABLE; configured mirror audit endpoint returned
  `404 NOT_IMPLEMENTED`, so no clean claim is made.

## 24. Production Behavior Changes

- Canonical READY requests now resolve Registry eligibility first.
- Selection uses structured capability facts and exact bindings.
- Non-ready outcomes stop before plan/job/enqueue/tool execution.
- LLM sees eligible candidates only and receives at most one repair.
- Resolution/decision/execution records persist externally.
- PlannerWorkbench adds a capability gate/audit surface.
- AnalysisPlan, PlanValidator, Registry execution, Runtime, historical jobs,
  and legacy API semantics remain unchanged.

## 25. Files Changed

Backend/API repositories and migration; shared Python/JSON/TypeScript schemas;
Registry metadata; resolver/selector/binder/validator; Planner API;
PlannerWorkbench/types/styles; focused/integration/browser tests; CI; evidence;
Phase 10L/shared docs; persistent records and TASKS. Dependencies/lock unchanged.

## 26. Commit and Exact-SHA CI History

- `ed880b313bed8d5bea36e5f8995f08bf48844023`, CI `30507612860`: failed
  service-backed because the fixture lacked the material-property fact required
  by its property-distribution goal.
- `c7c6081abda172756d48090d6000670bf6684d68`, CI `30510563999`: failed because
  the new fixture role used invalid authority `profile_exact`; a local fixture
  contract test was then added.
- corrected implementation: `9786e405f1938b514b95ccbeb1cdb6d4b26dde18`.
- corrected exact-SHA CI: `30511654404`, all required jobs PASS.
- completion-record/archive SHA and CI follow in the closure addendum.

## 27. Explicit Non-Scope Confirmation

No AnalysisPlan 0.2, dependency/DAG, prior-artifact binding, Runtime partial
success/failure redesign, plan editor/approval, interpretation, Workspace,
professional science, Fermi surface, arbitrary code, external science API,
new LLM SDK, enterprise infrastructure, or plugin ecosystem was implemented.

## 28. Remaining Phase 10L Gaps

10L-3 may define a reviewer-approved minimal dependency/artifact model; 10L-4
owns grounded interpretation; 10L-5 owns natural-language evidence closure.
These are gaps, not executable tasks.

## 29. Queue State

- Phase 10L-2: `COMPLETE / AWAITING_COMPLETION_RECORD_CI`.
- Phase 10L-3: `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.
- `PHASE_10L3_EXECUTABLE_TASK_CREATED = NO`.

## 30. Whether Phase 10L-3 Was Entered Automatically

`NO`.

## 31. Next Action

Verify completion-record exact-SHA CI, then create and verify the queue-archive
commit. Return the result and stop; do not queue or execute Phase 10L-3.

## Phase 10L-2 Closure Addendum - 2026-07-30 12:16:43 +08:00

- Completion record commit:
  `f62630bef53fc797705683753fbc8d5eca595c98`.
- Completion-record exact-SHA CI: run `30513319990`, `success`.
- Required jobs: Unit Tests `success`; Frontend Typecheck & Build `success`;
  PostgreSQL + Redis + MinIO service-backed integration `success`; no-skipped
  assertion `success`.
- Queue verification: permanent result, corrected implementation CI, browser
  and evidence records, completion record, and completion-record CI agree.
- Archive action: the complete Phase 10L-2 `---TASK---` block is authorized for
  deletion by the verified queue-archive commit; Phase 10L-3 remains only a
  reviewer gate and no executable Phase 10L-3 task exists.
- Archive commit exact SHA and CI run are reported in the reviewer return after
  the final exact-SHA gate; this addendum is not rewritten after archive.

# Phase 10L-5 Natural-Language Analysis Evidence Closure + DeepSeek-Only Provider Result

Completion time: `2026-08-01T17:44:20.0686283+08:00`

## 1. Conclusion

`PASS / COMPLETE_AWAITING_COMPLETION_RECORD_CI`. The implementation and its
exact-SHA CI are complete. The task remains in `TASKS.md` until this record and
the subsequent queue archive each pass exact-SHA CI.

## 2. Phase 10L Closure Status

Phase 10L-0 through 10L-4 remain archived. Phase 10L-5 closes the approved
natural-language evidence scope without entering Phase 10M. Phase 10L becomes
`READY_WITH_EXPLICIT_LIMITS` only after verified queue archive.

## 3. Baseline and Entry Gate

- branch: `master`.
- initial HEAD/origin: `58ee9432f708324636a7226df8f417e7c3c52d09`.
- Phase 10L-4 archive CI: run `30608078520`, success.
- initial worktree: clean; initial active task count: one L5 block.
- `DEEPSEEK_KEY` was configured for controlled live evidence without exposing
  its value, prefix, length, or hash.

## 4. LLM Call-Site Audit

All production provider construction, Intent, capability selection,
dependency composition, grounded interpretation, health/API, and historical
compatibility call sites were audited. Deterministic and fake providers remain
explicit test paths. Browser evidence is offline replay and never calls a
provider directly.

## 5. DeepSeek-Only Provider Policy

`DeepSeekProvider` uses fixed `https://api.deepseek.com`, allowlisted
`deepseek-v4-flash` and `deepseek-v4-pro`, and `DEEPSEEK_KEY` as the sole key
source. OpenAI, custom OpenAI-compatible, and Anthropic real transports return
typed `PROVIDER_NOT_ALLOWED`; there is no key or provider fallback. Injected
fake transport remains test-only.

## 6. Provider Security

Requests are purpose-bounded, redacted, byte/depth capped strict JSON. Duplicate
keys, non-finite values, prose/fences, unsupported models, unknown fields,
secrets, URLs/paths/code, and invented identities are rejected. Provider
responses cannot execute tools or bypass Registry/Plan validation.

## 7. Default CI vs Real Verification

Default CI sets an empty `DEEPSEEK_KEY` and makes zero real calls. Controlled
live verification used the environment key and persisted only sanitized hashes,
token/call metadata, typed diagnostics, selected identities, and outcomes.
No authorization material or raw secret was retained.

## 8. Evidence Contracts

Added strict Python, JSON Schema, and TypeScript parity for
`NaturalLanguageEvidenceCase/Run`, `DeepSeekVerificationRecord/Suite`, and the
Phase 10L closure manifest. Canonical serialization, deterministic hashes,
unknown-field rejection, and count/byte/depth caps are enforced.

## 9. Dataset Case

Real DeepSeek completed DataProfile -> Intent -> eligibility -> plan -> job ->
Runtime -> registered dataset adapters -> artifacts/lineage -> grounded
interpretation. Run ID: `live_run_ceaef0c7168892dd5ed9d0a7da7bb7c1`.

## 10. Structure Case

Exact structure resource identity and supported structure capability completed
through registered adapters with grounded findings. Run ID:
`live_run_d11315ef07ae3cb3bf09295fdd1254b2`.

## 11. Materials ML Case

Exact target/model semantics and ML evaluation artifacts completed without
first-column or broad-metrics fallback. Run ID:
`live_run_28f09af3b53a75170a8850d6ca45f8b3`.

## 12. Phonon Case

AnalysisPlan 0.2 executed the real `phonon.band + phonon.dos ->
phonon.band_dos` typed chain, preserved graph/lineage identities, and produced
grounded interpretation. Run ID:
`live_run_b135271f0ff8102fa42b0102aa8b8d0c`.

## 13. Volumetric Case

Exact volumetric quantity/resource binding executed the registered capability
and grounded only supported range/reference/unit facts. Run ID:
`live_run_89ff5988240b2246dec4adb371deacdb`.

The five-case suite is
`deepseek_suite_ee5a0e9700d1a70787fc060fda274171`: `5/5 PASS`, per-case
calls `3, 3, 3, 4, 3`, total `16`.

## 14. Negative and Boundary Cases

The real-provider suite also verifies bounded clarification, Future Fermi
unsupported, capability mismatch, exact formation-energy/band-gap separation,
and no non-ready execution. Historical scatter behavior that depended on
first-column guessing is now a typed mismatch, not a fabricated success.

## 15. API

Canonical planner/API requests explicitly select DeepSeek and expose sanitized
provider identity, call audit, planning state, persisted job/artifacts, and
interpretation. Non-ready responses create no plan, job, enqueue, ToolCall, or
artifact. Legacy test compatibility is explicit and not counted as live proof.

## 16. Browser

Sanitized real-DeepSeek captures replayed in Chromium, Firefox, WebKit, and
Chromium `390x844` for five ready and three non-ready states. Console/page
errors, external requests, horizontal overflow, raw HTML/script/iframe, and
secret/path exposure were zero. Browser replay made zero live provider calls.

## 17. Service-Backed

Local PostgreSQL/Redis/MinIO live verification passed five real-DeepSeek cases
with zero skips; default local service integration passed `21/21`. Exact-SHA CI
service integration passed `36`, skipped `0`, failed `0`, including migration,
object storage, queue/runtime, L5 contracts, and no-skipped assertion.

## 18. Compatibility

AnalysisIntent remains `1.0`; EligibilityResolution remains `1.0`;
AnalysisPlan remains `0.1/0.2`; ToolPlannerMetadata remains `1.0/1.1`.
Existing PlanValidator, capability validator, QueueWorkerRuntime, dependency
execution, lineage, historical jobs/artifacts, L1-L4, and Phase 10K behavior
remain compatible. No migration or lockfile change was required.

## 19. Caps, Cost and Performance

Per-case live calls are capped at 12; suite calls at 60; provider request,
response, depth, timeout, model, and purpose are bounded. Recorded five-case
calls total 16 and historical supplemental calls total 92. Performance evidence
records bounded elapsed/token/call data without claiming production capacity.

## 20. Security Markers

```text
REAL_LLM_PROVIDER = DEEPSEEK_ONLY
REAL_LLM_KEY_SOURCE = DEEPSEEK_KEY_ONLY
REAL_LLM_CALLS_DEFAULT_CI = 0
REAL_DEEPSEEK_CALLS_CURRENT_SUITE = 16
REAL_DEEPSEEK_CALLS_HISTORICAL_SUPPLEMENTAL = 92
OTHER_REAL_PROVIDER_CALLS = 0
NO_OPENAI_REAL_CALLS
NO_CUSTOM_OPENAI_COMPATIBLE_REAL_CALLS
NO_ANTHROPIC_REAL_CALLS
NO_DEEPSEEK_API_KEY_FALLBACK
NO_OPENAI_API_KEY_FALLBACK
NO_FRONTEND_LLM_KEY_INPUT
NO_BROWSER_TO_DEEPSEEK_DIRECT_CALL
NO_RAW_ARTIFACT_TO_LLM
NO_UNGROUNDED_INTERPRETATION
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES
NO_LLM_ARBITRARY_PYTHON_SHELL_FILESYSTEM_AUTHORITY
NO_LLM_TOOL_REGISTRY_BYPASS
NO_SECRET_PATTERN_HITS
PHASE_10M0_EXECUTABLE_TASK_CREATED = NO
```

## 21. Evidence Inventory

Evidence is under
`docs/phase10l/evidence/phase10l5_natural_language_closure/`. Manifest
`phase10l_closure_a273910a7174c9d33898660c0981ab5a` contains 166 LF-normalized
text/raw-PNG SHA-256 entries. It includes live cases, failed-attempt provenance,
historical inventory/replay, API, browser matrix/screenshots, service,
performance, security, and artifact hashes.

Historical suite
`historical_deepseek_suite_dde5218a3d2121fc038bb90d6daa044a` passed 40/40
supplemental scenarios. Combined current plus historical semantic coverage is
45/45. Pure UI/renderer/accessibility/performance/security flows,
deterministic negative/fault-injection paths, infrastructure-only phases,
superseded tools, and unrecoverable damaged prompt text are explicitly
classified rather than falsely counted as byte-for-byte LLM replay.

## 22. Tests

- focused L1-L5: `199 passed`.
- local full backend: `1078 passed, 38 skipped, 63 warnings`.
- implementation CI unit: `1078 passed, 1 skipped, 37 deselected, 63 warnings`;
  focused L5 closure `99 passed`.
- frontend: 52 files, `333 passed`; typecheck and production build passed.
- service-backed CI: `36 passed, 0 skipped, 0 failed`.
- Chromium/Firefox/WebKit/mobile, evidence finalizer, manifest replay,
  `uv lock --check`, dependency listing, diff check, and secret scan passed.
- `npm audit`: `UNAVAILABLE` because the configured mirror returned
  `404 NOT_IMPLEMENTED`; it is not reported clean.
- existing warnings: pymatgen CIF/spglib deprecations and CI action Node 20
  deprecation notices; none failed a required gate.

## 23. Production Behavior Changes

Real provider selection is DeepSeek-only and environment-key-only. Canonical
Intent/provider output authority is stricter; exact visual forms and the
smallest complete eligible selection are validated. Planner/Runtime authority
is unchanged: persisted validated plans and registered adapters alone execute.
PlannerWorkbench adds sanitized provider/evidence state and never accepts a key
or calls DeepSeek directly.

## 24. Files Changed

- backend/provider: API planner/provider routes, LLM provider, Intent,
  capability/dependency/interpretation guards, redaction, runtime health.
- contracts: Python, JSON Schema, TypeScript natural-language evidence models.
- frontend: PlannerWorkbench, API types, tests, browser runner.
- tests/CI: L1-L5 regressions, service-backed L5, provider strictness, CI gates.
- evidence/docs: 45 semantic cases, browser screenshots/captures/manifests,
  Phase 10L-5 architecture/policy/security/cost/compatibility/closure docs.
- persistent/queue: project state, ADR/registry/open questions, TASKS/results.
- dependency/lockfile/migration changes: none.

## 25. Commit and Exact-SHA CI History

- implementation: `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37`.
- implementation exact-SHA CI: run `30693848581`, success.
- required jobs: Unit `91353182658`, Frontend `91353182650`, Service-backed
  `91353182660`, all success.
- failed implementation CI SHA/runs: none.
- local live-provider failed attempts are retained as sanitized evidence; the
  final five-case and 40-case suites pass.
- completion-record and archive SHA/CI: pending this lifecycle.

## 26. Explicit Non-Scope

No Phase 10M Workspace implementation, report/recipe productization,
professional-science expansion, Fermi surface, CrystalNN/VoronoiNN,
experimental XRD comparison engine, advanced trajectory analytics, electronic
Band/DOS, generic workflow/agent/RAG framework, runtime LLM/replanning,
arbitrary Python/shell/filesystem/notebook/script, external scientific API,
enterprise SaaS, plugin marketplace, new LLM SDK, dependency, migration, or
deployment productization was added.

## 27. Remaining Roadmap

```text
Phase 10M-0:
Workspace Information Architecture / Contract
```

This is a reviewer-gated roadmap item, not an executable task.

## 28. Queue State

```text
Phase 10L-5 = COMPLETE / AWAITING_COMPLETION_RECORD_CI
Phase 10L = READY_WITH_EXPLICIT_LIMITS / AWAITING_VERIFIED_ARCHIVE
Phase 10M-0 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
TASK_BLOCK_COUNT = 1
```

## 29. Automatic Phase 10M-0 Entry

```text
NO
PHASE_10M0_EXECUTABLE_TASK_CREATED = NO
```

## 30. Next Action

Verify this completion-record exact-SHA CI, then remove only the completed L5
task block in a separate verified queue-archive commit. Do not create, queue,
or execute Phase 10M-0.

## 31. Final Repository State at Completion Record

- implementation HEAD/origin:
  `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37`.
- implementation exact-SHA CI: `30693848581`, success.
- completion-record exact-SHA CI: pending this record's commit.
- archive exact-SHA CI: pending completion-record success.

## Phase 10L-5 Closure Addendum - 2026-08-01 18:03 +08:00

- Completion-record commit:
  `e4b0a8f5619cbb1001ef64809db6400729a99d8d`.
- Completion-record exact-SHA CI: run `30694747664`, `success`.
- Required jobs: Unit Tests `success`; Frontend typecheck/build and L4/L5
  browser replay `success`; PostgreSQL/Redis/MinIO service-backed integration
  `36 passed, 0 skipped, 0 failed`.
- Queue verification: implementation, real DeepSeek evidence, browser/service
  evidence, permanent result, implementation CI, completion record, and
  completion-record CI agree.
- Archive action: the complete Phase 10L-5 `---TASK---` block is deleted by the
  queue-archive commit. Phase 10M-0 remains only a reviewer gate and no
  executable Phase 10M task exists.
- Archive exact SHA and CI run are reported in the reviewer return after the
  final exact-SHA gate; this permanent addendum is not rewritten after archive.

# Phase 10L-4 Grounded Scientific Result Interpretation Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

The implementation, local gates, permanent evidence, and corrected exact-SHA
implementation CI are complete. The task remains in `TASKS.md` until this
completion record and the subsequent verified queue archive each pass their
own exact-SHA CI.

## 2. Baseline and Entry Gate

- Phase 10L-3 archive: `8026cb15658f35a8f4c59ef312bd519cead778ae`.
- Phase 10L-3 archive CI: run `30543213225`, success.
- Initial branch/HEAD/origin: `master` / `8026cb15658f35a8f4c59ef312bd519cead778ae`
  / same origin; worktree clean.
- Initial TASKS: one admitted L4 block first and in progress; reviewer-supplied
  L5 pending and blocked by L4 archive.
- Entry gate and current Plan/lineage/migration source audit passed.

## 3. Pre-Implementation Audit

- Existing Adapter summaries, reports, and `summary.md` were reusable display
  foundations but not grounded scientific authority.
- No first-class evidence bundle, claims, numeric/unit/entity grounding,
  interpretation persistence, API, or findings UI existed.
- Existing provider transport was reusable, but raw Artifact text and prior
  summaries were excluded from the L4 provider domain.
- Current Job, ToolCall, ArtifactStorage, dependency execution, and lineage
  repositories supplied exact post-execution authority.
- At least five safe structured contracts were available: numeric table
  summary, ML basic metrics, structure summary, phonon band/DOS/combined, and
  volumetric manifest. Readiness was `PASS`.

## 4. Interpretation Architecture

Terminal Job, exact persisted Plan/execution/lineage, and successful validated
Artifacts feed contract-specific projectors. The resulting immutable evidence
bundle feeds deterministic or strict-provider interpretation and an independent
grounding validator. This service is post-execution and read-only: it cannot
select tools, change Intent/Plan/Job/Artifact, create ToolCalls, or enqueue work.

## 5. Scientific Evidence Contracts

- `ScientificEvidenceBundle 1.0`, `ScientificEvidenceItem 1.0`, and
  `ScientificEvidenceRef 1.0` exist as strict Python, checked-in JSON Schema,
  and TypeScript contracts.
- Identity includes exact project/dataset/Profile/Intent/eligibility/decision/
  plan/graph/job/execution/ToolCall/Artifact checksum/lineage facts.
- Field locators are projector-owned semantic field/entity IDs; path, URL,
  filename, fuzzy label, arbitrary JSON pointer, code, and array-index-only
  authority are rejected.
- Canonical JSON and deterministic hashes exclude runtime timestamps from
  semantic identity. Unknown fields, duplicate JSON keys, non-finite values,
  depth/count/byte overflow, and cross-scope evidence fail typed validation.

## 6. Supported Artifact Families

1. Dataset/property: `table.numeric_summary` / `table_json`.
2. Materials ML: `ml.basic_metrics` / `metrics_json`, using the real six-field
   `n`, MAE, RMSE, R2, mean-error, and max-absolute-error contract.
3. Structure: `structure.summary` / `structure_json`.
4. Phonon: `phonon.band`, `phonon.dos`, and the real L3
   `phonon.band + phonon.dos -> phonon.band_dos` chain.
5. Volumetric: `structure.volumetric_data` structured manifest scope.

The complete Registry inventory is classified in the evidence matrix as
interpretation-ready, deterministic-only, display-only, unsupported-contract,
unsafe-untrusted-text, no-structured-facts, or Future. Unsupported contracts
are not coerced into these five families.

## 7. Evidence Projectors

Projectors are deterministic, exact-contract/version aware, identity/unit
preserving, bounded, no-network, and no-LLM. They project already-computed
facts and warnings only. The corrected ML projector validates the exact real
Adapter payload and cross-metric consistency. It performs no new scientific
analysis, generic JSON parsing, image extraction, unit guessing, or raw text
interpretation. Unsupported or malformed artifacts produce typed source or
no-supported-evidence outcomes.

## 8. Scientific Claim Contract

`ScientificClaim 1.0` supports OBSERVATION, COMPARISON, ANOMALY, WARNING,
LIMITATION, RECOMMENDATION, and NO_SUPPORTED_CONCLUSION with allowlisted
predicates. Confidence is DIRECT, QUALIFIED, or LIMITED, never an invented
probability. Every claim has exact subject/supporting and optional limiting or
contradicting evidence IDs. Platform templates render normal scientific text;
provider proposals cannot add free numeric/unit/entity authority.

## 9. Grounding Validator

The independent validator verifies bundle/artifact/lineage identity, evidence
membership, subject scope, allowlisted predicate, numeric tokens and display
rounding, units/references, comparison compatibility, partial-result
limitations, forbidden conclusions, inert text, and caps. It rejects invented
numbers, units, entities, thresholds, evidence IDs, causal/superlative claims,
unsupported stability/confirmation/deployment/generalization/Bader/charge-
transfer conclusions, and evidence from failed or blocked steps.

## 10. Deterministic Interpreter

The default interpreter creates useful bounded direct observations, propagates
source warnings and partial limitations, emits NO_SUPPORTED_CONCLUSION when
needed, deduplicates and orders claims deterministically, and produces stable
semantic hashes. It does not dump raw JSON, recalculate science, or call an LLM.

## 11. Strict Provider Interpreter

- Reuses the existing bounded OpenAI-compatible transport; no new dependency.
- Provider sees only provider-safe evidence IDs and structured facts plus
  allowlisted claim/predicate/schema/boundary rules.
- Raw Artifact payloads, arrays, paths, URLs, bucket keys, source code,
  Registry, rejected candidates, secrets, and execution APIs are absent.
- Exactly one strict JSON object is accepted. Prose, fences, duplicate keys,
  unknown fields, invented evidence/facts, HTML/script/code/path/URL, non-finite
  values, and over-cap output fail.
- At most one interpretation-specific validation repair is permitted with no
  evidence-domain expansion and no deterministic fallback.
- `REAL_LLM_CALLS = 0`; evidence uses deterministic and fake transport only.

## 12. Interpretation Outcomes

Implemented typed outcomes:

```text
INTERPRETATION_READY
INTERPRETATION_READY_WITH_LIMITS
NO_SUPPORTED_EVIDENCE
SOURCE_NOT_TERMINAL
SOURCE_INTEGRITY_FAILED
EVIDENCE_CAP_EXCEEDED
PROVIDER_FAILED
VALIDATION_FAILED
```

Only grounded READY states persist a ready interpretation. Provider failure is
not relabeled as deterministic success; source integrity failures call no
provider and create no claims.

## 13. Partial Execution Interpretation

ALL_SUCCEEDED uses all supported successful artifacts. PARTIAL_RESULTS uses
only successful lineage-complete artifacts, shows failed/blocked steps and
missing desired outputs first-class, limits every claim, and returns
`INTERPRETATION_READY_WITH_LIMITS`. ALL_FAILED yields no scientific finding.
Successful independent-branch artifacts remain available without extending
their claims to the failed plan scope.

## 14. Recommendations

Recommendations are bounded, evidence-linked, non-executable records with
`executionAuthorized=false`, `planCreated=false`, and `jobCreated=false`.
They contain no tool parameters, code, paths, URLs, shell/notebook content, or
enqueue token. PlannerWorkbench does not render them as Run actions.

## 15. Persistence and Migration

- Alembic `0006_phase10l4_interpretation` adds immutable evidence bundles,
  interpretation runs/records, claims, and evidence links.
- Bundle/run/claim/link/execution identities are deterministic and idempotent;
  conflicting semantic writes fail.
- In-memory, SQLite 0005->0006 upgrade/downgrade/re-upgrade, and PostgreSQL
  full-chain behavior pass.
- No provider authorization or secret is stored.
- Interpretation remains a first-class API/persistence record; no fake
  registered Adapter or ToolCall-produced interpretation artifact was created.

## 16. API

Additive create/list/read/evidence endpoints load the exact terminal job,
verify expected plan and source integrity, project evidence, run the requested
mode, validate, and persist immutable records. Responses expose bounded claims,
evidence links, warnings, limitations, recommendations, partial and repair
state, diagnostics, provenance, and explicit no-execution markers. Running,
tampered, unsupported, provider-failed, and validation-failed cases do not
create ToolCall, Plan, Job, queue message, or scientific Artifact. Legacy API
behavior is unchanged.

## 17. Frontend and Browser

PlannerWorkbench additively displays availability/outcome/mode, findings,
warnings, limitations, non-executable recommendations, evidence counts,
partial banners, provider/repair provenance, and inert audit JSON. Each claim
has keyboard-accessible evidence drill-down with exact value/unit/subject,
contract, tool/version, checksum abbreviation, locator, warning/limitation,
and lineage. Chromium, Firefox, WebKit, and Chromium 390x844 passed deterministic,
strict-fake-provider, partial/no-evidence/failure states, focus/accessibility,
zero horizontal overflow, zero console/page errors, and zero unapproved network.

## 18. Real Evidence Cases

- Dataset/property: exact counts, ranges, missingness, and no anomaly-cause
  invention.
- ML: real registered `ml.basic_metrics` Adapter -> QueueWorkerRuntime ->
  Artifact -> interpretation, with exact target and six metrics.
- Structure: exact structure/site/lattice facts without stability, phase, bond,
  or correctness claims.
- Phonon: persisted AnalysisPlan 0.2 band+DOS->band_dos chain with multi-artifact
  refs, source warnings, and no unconditional stability claim.
- Volumetric: exact quantity/range/reference facts without Bader, topology, or
  charge-transfer claims.
- Partial execution: successful independent DOS evidence only, failed producer
  and blocked consumer limitations, READY_WITH_LIMITS.
- Unsupported contract: NO_SUPPORTED_EVIDENCE and no fake findings.
- Integrity tampering: wrong plan/checksum/cross-job/stale/broken lineage gives
  SOURCE_INTEGRITY_FAILED with zero provider calls and claims.

## 19. Adversarial Evidence

Invented number, unit, entity, evidence ID, threshold, failed-artifact result,
forbidden stability/phase/model/Bader/charge-transfer/structure claims,
duplicate keys, prose/fence, HTML/script, code/path/URL, non-finite values,
oversized/deep payload, and Artifact prompt-injection fixtures are rejected or
exhaust the single repair with `VALIDATION_FAILED`. Artifact strings remain
inert and never enter provider semantic facts or execution authority.

## 20. Compatibility

AnalysisIntent 1.0, DataProfile 2.0, EligibilityResolution 1.0, Tool planner
metadata 1.0/1.1, AnalysisPlan 0.1/0.2, dependency bindings, PlanValidator,
QueueWorkerRuntime, Registry/Adapter execution, Job statuses, Artifact lineage,
historical hashes/jobs/artifacts, and L1-L3 API behavior are unchanged. L4 is
an additive read-only post-execution layer.

## 21. Caps and Performance

- source Artifacts <= 16; evidence items <= 256; warnings <= 128;
  limitations <= 64; table rows/series summaries <= 64;
  refs per claim <= 8; claims <= 32; recommendations <= 8; JSON depth <= 14.
- bundle/provider payload <= 262,144 bytes; interpretation <= 131,072 bytes.
- The near-cap fixture requested 256 evidence items across four source
  Artifacts and produced typed `EVIDENCE_CAP_EXCEEDED` rather than semantic
  truncation; measured local projection was 320.909 ms with 1,207,810 traced
  peak bytes. This is bounded fixture evidence, not a production capacity claim.
- Bounded reads avoid binary/full-array provider payloads; replay is idempotent
  and does not grow duplicate persistence rows.

## 22. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L4_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS
NO_INTERPRETATION_ARBITRARY_CODE_EXECUTION
NO_INTERPRETATION_SHELL_OR_FILESYSTEM_AUTHORITY
NO_INTERPRETATION_TOOL_EXECUTION_AUTHORITY
NO_INTERPRETATION_PLAN_MUTATION
NO_INTERPRETATION_JOB_OR_ENQUEUE
NO_RAW_ARTIFACT_PAYLOAD_TO_PROVIDER
NO_UNSUPPORTED_ARTIFACT_TO_PROVIDER
NO_PROVIDER_ARTIFACT_PATH_OR_URL
NO_PROVIDER_SECRET_EXPOSURE
NO_PROVIDER_FULL_REGISTRY_EXPOSURE
NO_REJECTED_CANDIDATE_LEAK_TO_LLM
NO_ARTIFACT_JAVASCRIPT
NO_ARTIFACT_HTML_EXECUTION
NO_ARTIFACT_IFRAME
NO_EXTERNAL_ARTIFACT_URL
NO_CROSS_JOB_INTERPRETATION_EVIDENCE
NO_CROSS_PROJECT_INTERPRETATION_EVIDENCE
NO_STALE_RESOURCE_INTERPRETATION
NO_UNGROUNDED_NUMERIC_CLAIMS
NO_UNGROUNDED_UNIT_CLAIMS
NO_UNGROUNDED_ENTITY_CLAIMS
NO_UNSUPPORTED_SCIENTIFIC_CONCLUSIONS
NO_SECRET_PATTERN_HITS
```

L1-L3 security regressions remain green. No dependency or execution authority
was added.

## 23. Evidence Inventory

`docs/phase10l/evidence/phase10l4_grounded_interpretation/` retains entry and
interpretability audits, six strict schema projections, five family cases,
real phonon/partial runtime, provider isolation, adversarial/integrity cases,
API/persistence/migration/grounding/performance/security audits, browser DOM/
network/console/mobile matrices, desktop/mobile raw PNGs, and an LF-normalized
text/raw-PNG SHA-256 manifest. Committed browser semantics replay exactly in CI.

## 24. Tests

- Focused corrected L4: `37 passed, 3 skipped`; skips are local service cases.
- Local full backend: `955 passed, 33 skipped, 63 warnings`.
- Local frontend: 52 files / `333 passed`; typecheck and production build PASS.
- Local browser: Chromium/Firefox/WebKit and 390x844 mobile PASS.
- Evidence/manifest focused: `4 passed`; lock, dependency tree, diff, migration,
  Phase 10 closure, security and secret markers PASS.
- Local service-backed: `UNAVAILABLE` because Docker is not installed; no PASS
  claim is made.
- Corrected exact-SHA unit: `955 passed, 1 skipped, 32 deselected, 63 warnings`.
- Corrected exact-SHA service-backed: `31 passed, 0 skipped, 0 failed`; Alembic,
  PostgreSQL, Redis, MinIO and no-skipped assertion PASS.
- Corrected exact-SHA frontend: closure, evidence integrity, typecheck,
  Chromium/Firefox/WebKit/mobile semantic replay, and build PASS.
- npm audit: `UNAVAILABLE`; configured mirror status is not reported as clean.

## 25. Production Behavior Changes

- Adds post-execution scientific evidence projection and immutable grounded
  interpretation for terminal persisted jobs.
- Adds deterministic and strict-provider modes with one interpretation repair.
- Adds grounded findings/evidence/limitation UI and read APIs.
- Does not modify Planner selection, AnalysisPlan, PlanValidator, Runtime,
  Registry/Adapter execution, job status, queue, or Artifact execution.
- Recommendations remain non-executable.

## 26. Files Changed

- Backend/contracts: interpretation schemas/models, projectors/interpreters,
  grounding validator, repository/db/API, Alembic 0006.
- Frontend/shared: TypeScript contracts, API types, PlannerWorkbench and styles.
- Tests: contract/projector/provider/validator/persistence/API/Runtime/service/
  frontend/browser/security/evidence cases.
- Evidence/docs: L4 architecture/contracts/boundaries/caps/compatibility/
  readiness, browser runner, captures, screenshots, and manifest.
- Persistent/queue/result records updated. Dependency and lock files unchanged.

## 27. Commit and Exact-SHA CI History

- Initial local implementation: `262ec0e937894990fc800edb2899c0884169d265`.
- First pushed hardening: `3336d9f2ec14153063fe3b2bd1c552e96ed13f82`,
  CI `30604842478` failed service-backed (missing AnalysisPlanV02 fixture import;
  phonon chain honestly returned READY_WITH_LIMITS rather than READY).
- First correction: `0d37ea967b314cb920ac8537e3f75df66fd83918`,
  CI `30605450973` failed service-backed (projector fixture omitted two real ML
  fields; one test queried a non-public evidence response field).
- Corrected implementation: `02a9e33b93f96aa99413dc49ca2dabca652679c9`.
- Corrected implementation exact-SHA CI: run `30606774006`, all required jobs
  success. Failed provenance is retained; history was not rewritten.
- Completion-record SHA/CI: pending this record's commit.
- Verified queue-archive SHA/CI: pending completion-record success.

## 28. Explicit Non-Scope Confirmation

No Phase 10L-5 full evidence closure, Workspace, Report/Recipe productization,
RAG/vector DB/literature/web retrieval, autonomous research loop, runtime LLM/
replanning, interpretation tool selection, recommendation auto-execution, new
Intent/Plan/dependency model, Runtime redesign, arbitrary artifact/JSON/Markdown
authority, arbitrary Python/shell/filesystem/notebook/script, external Artifact
URL or science API, cross-job reuse, new scientific algorithm, CrystalNN/
VoronoiNN, experimental XRD, trajectory analytics, electronic Band/DOS, Fermi
surface, enterprise infrastructure, plugin ecosystem, new LLM SDK, or
uncontrolled dependency was implemented.

## 29. Remaining Phase 10L Gap

```text
Phase 10L-5:
Natural-Language Analysis Evidence Closure + DeepSeek-Only Provider Freeze
```

This is the reviewer-supplied pending task, not work executed during L4.

## 30. Queue State

```text
Phase 10L-4 = COMPLETE / AWAITING_COMPLETION_RECORD_CI
Phase 10L-5 = REVIEWER_APPROVED / QUEUED / BLOCKED_BY_PHASE_10L4_ARCHIVE
TASK_BLOCK_COUNT = 2 pending verified L4 archive
```

## 31. Whether Phase 10L-5 Was Entered Automatically

```text
NO
PHASE_10L5_EXECUTABLE_TASK_CREATED = NO
```

The L5 task was supplied explicitly by the reviewer/user and has not started.

## 32. Next Action

Verify this completion-record exact-SHA CI, then remove only the completed L4
task block in a verified queue-archive commit. After archive CI succeeds, begin
the already reviewer-supplied L5 task under normal queue rules.

## 33. Repository State at Completion Record

- corrected implementation HEAD/origin:
  `02a9e33b93f96aa99413dc49ca2dabca652679c9`.
- corrected implementation CI: `30606774006`, success.
- completion-record CI: pending this record's commit.
- archive CI: pending completion-record success.

## Phase 10L-4 Closure Addendum - 2026-07-31 13:46:09 +08:00

- Completion record commit:
  `45af09e9a0a46f4cdbdb136d979649d2b65f0ff7`.
- Completion-record exact-SHA CI: run `30607509775`, `success`.
- Required jobs: Unit Tests `success`; Frontend Typecheck & Build, evidence
  integrity, Chromium/Firefox/WebKit/mobile replay `success`; PostgreSQL +
  Redis + MinIO migration/service-backed integration `success`; 31 selected
  integration tests passed with zero skipped/failed.
- Queue verification: permanent result, corrected implementation CI, browser/
  evidence, completion record, and completion-record CI agree.
- Archive action: the complete Phase 10L-4 `---TASK---` block is deleted by
  the queue-archive commit. The reviewer-supplied Phase 10L-5 block remains
  `待处理` and is not executed before archive exact-SHA CI succeeds.
- Historical `entry_gate.json` is fixed to the actual L4 admission snapshot;
  future queue changes cannot rewrite L4 evidence.
- Archive commit exact SHA and CI run are reported after the final exact-SHA
  gate; this addendum is not rewritten after archive.

# Phase 10L-3 Bounded Multi-Tool Analysis + Typed Artifact Dependency Execution Result

Completed: 2026-07-30 20:26:23 +08:00

## 1. Conclusion

`PASS` for implementation and implementation exact-SHA CI. The task remains
in `TASKS.md` until this completion record passes exact-SHA CI and a separate
verified queue-archive commit succeeds.

## 2. Baseline and Entry Gate

- Phase 10L-2 archive: `7d032a9c1dafd2a4a76522bcfcd1321fb08b20f9`.
- Phase 10L-2 archive CI: run `30513584587`, success.
- initial branch/HEAD/origin: `master` / `7d032a9c...` / `7d032a9c...`.
- initial worktree: clean; task-block count zero before reviewer-approved L3
  admission, then exactly one L3 block; L4 remained reviewer-gated.

## 3. Pre-Implementation Audit

AnalysisPlan 0.1 represented ordered, sequential independent tool calls; list
order was not a graph and no produced-artifact binding existed. The 38
available tools were audited. One real typed producer/consumer family exists:
`phonon.band` and `phonon.dos` produce canonical artifacts that the registered
`phonon.band_dos` Adapter already consumes. Readiness therefore passed without
adding a scientific algorithm or test-only production tool.

```text
CURRENT_MULTI_TOOL_LEVEL = SEQUENTIAL_INDEPENDENT
SELECTED_PRODUCER_TOOLS = phonon.band, phonon.dos
SELECTED_CONSUMER_TOOL = phonon.band_dos
```

## 4. AnalysisPlan 0.2

Strict additive Python, JSON Schema, and TypeScript contracts add up to four
steps and one plan-level `dependencyBindings` list. Canonical serialization,
deterministic binding/graph/plan hashes, strict unknown-field rejection, and
stable topological ordering are implemented. AnalysisPlan 0.1 remains valid,
unchanged, and is never reinterpreted as dependency-aware.

## 5. Dependency Binding Contract

Each binding owns exact producer step/output port, artifact kind/contract/media
type/cardinality, and exact consumer step/input port. It is the sole graph-edge
authority. List position, filename, display label, array index, wildcard,
path, URL, runtime Artifact ID, and previous-job identity have no authority.

## 6. Artifact Port Metadata

ToolPlannerMetadata 1.1 adds strict output/input ports while 1.0 tools remain
valid independent tools. Exact artifact kind, allowlisted contract version,
media type, cardinality, byte cap, determinism, identity scope, provenance,
visibility, and Adapter binding rules form the deterministic compatibility
matrix. Every mismatch has a typed rejection.

## 7. Bounded Composer

The deterministic composer uses only L2-selected tools and compatible ports;
it never infers edges from co-occurrence or wording. The optional fake-provider
path sees selected IDs and compatible pairs only, accepts one strict JSON
object, shares L2's total one-repair budget, and cannot expand tools, targets,
resources, ports, contracts, or caps. There is no Mock fallback.

## 8. Validation

An independent dependency validator recomputes identities, ports, binding IDs,
caps, acyclicity, depth, deterministic topology, eligibility membership,
parameter provenance, collision/composition, and scope before existing
capability-context and PlanValidator gates. Self/two-node/transitive cycles,
unknown or duplicate edges/ports, invented/rejected tools, wildcard/path/URL,
cross-job/project, stale identity, checksum/contract/media/size mismatch, and
cap overflow fail with bounded typed diagnostics.

## 9. Persistence and Migration

Alembic `0005_phase10l3_dependency_execution` adds relational audit storage for
planned bindings, runtime binding resolutions, dependency execution records,
and artifact lineage while plan JSON remains semantic authority. In-memory,
SQLite upgrade/downgrade/re-upgrade, and PostgreSQL paths preserve immutable,
idempotent records and reject conflicting semantic writes. AnalysisPlan 0.1
and 0.2 round-trip through the existing repository.

## 10. QueueWorkerRuntime

Only the 0.2 path loads the exact persisted plan, verifies its hash, revalidates
dependencies, computes deterministic topology, and executes serially through
Tool Registry and registered Adapters. Runtime resolves platform-created,
checksummed, same-plan/job/project artifact refs through ArtifactStorage before
consumer invocation. It never replans, calls an LLM, or falls back to source
data when an artifact is missing.

## 11. Partial Execution Semantics

Producer or consumer failure blocks descendants only. Independent branches
continue; successful artifacts remain; binding failures occur before consumer
Adapter invocation. Step and binding states distinguish failures from
`BLOCKED_DEPENDENCY`. The additive overall record reports `ALL_SUCCEEDED`,
`PARTIAL_RESULTS`, `ALL_FAILED`, or `VALIDATION_ABORTED` while legacy Job status
semantics remain compatible. Replay creates no duplicate calls/artifacts/edges.

## 12. Artifact Lineage

Lineage records exact project/dataset/Profile/Intent/eligibility/decision/plan/
graph/job identities, producer tool/step/call/output port, artifact kind/
contract/media/checksum, upstream artifact and binding IDs, runtime/Adapter
provenance, caps, and warnings. Lineage never depends on array position or
report text.

## 13. Real Dependent Chain Evidence

- `phonon.band:canonical-band` -> `phonon.band_dos:band` using
  `phonon_band_json / phase10h.phonon_band.v1 / application/json`.
- `phonon.dos:canonical-dos` -> `phonon.band_dos:dos` using
  `phonon_dos_json / phase10h.phonon_dos.v1 / application/json`.
- The persisted three-step plan executes `step_001`, `step_003`, then
  `step_002`; both bindings resolve and the result is `ALL_SUCCEEDED`.
- Replay retains the same semantic plan/graph hashes and no duplicate runtime
  records.

## 14. Failure and Rejection Evidence

Producer-failure evidence records the producer `FAILED`, combined consumer
`BLOCKED_DEPENDENCY` without Adapter invocation, independent DOS producer
`SUCCEEDED`, retained DOS artifacts, and `PARTIAL_RESULTS`. Consumer failure,
checksum/contract/media/identity/size/port mismatch, cycles, and graph caps are
also retained as typed captures.

## 15. API

Canonical READY requests compose/validate/persist 0.2 before job creation and
enqueue. Additive responses and `/planner/jobs/{job_id}/dependencies` expose
schema/hash/graph/topology/bindings/execution/lineage. Non-ready and invalid
dependency cases create no plan, job, ToolCall, Artifact, or queue message.
Legacy 0.1 APIs remain readable and executable through their unchanged path.

## 16. Frontend and Browser

PlannerWorkbench additively shows schema version, exact tools/params, dependent
and independent steps, ports/contracts, topology, validation, runtime states,
blocked causes, partial results, lineage, and inert audit JSON. It is an
accessible list/card/table surface, not an editor. Chromium 128, Firefox 128,
WebKit 18, and Chromium 390x844 passed success/partial cases, keyboard focus,
status labels, zero horizontal overflow, zero console/page errors, and zero
external requests.

## 17. Compatibility

AnalysisIntent 1.0 and EligibilityResolution 1.0 are unchanged. AnalysisPlan
0.1 schemas and hashes remain unchanged/readable, and only 0.2 receives
dependency runtime semantics. Registry execution authority, PlanValidator,
L1/L2 candidate isolation/exact binding, historical jobs/artifacts, Phase 10K,
and legacy API behavior remain intact.

## 18. Caps and Performance

Caps are four steps, six bindings, depth four, three incoming/outgoing edges,
one total repair, and 524,288 serialized planning bytes. The legal near-cap
fixture used four steps/six bindings/depth four, 3,619 serialized bytes,
43,486 traced peak bytes, and 2.523 ms local validation/sort time. This proves
bounded behavior only, not production capacity.

## 19. Security

```text
REAL_LLM_CALLS = 0
NO_PHASE10L3_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS
NO_DEPENDENCY_ARBITRARY_CODE_EXECUTION
NO_DEPENDENCY_SHELL_OR_FILESYSTEM_AUTHORITY
NO_ARTIFACT_JAVASCRIPT
NO_ARTIFACT_HTML_EXECUTION
NO_ARTIFACT_CALLBACK
NO_ARTIFACT_SHADER
NO_ARTIFACT_MODULE
NO_EVAL
NO_FUNCTION_CONSTRUCTOR
NO_EXTERNAL_ARTIFACT_URL
NO_CROSS_JOB_ARTIFACT_BINDING
NO_CROSS_PROJECT_ARTIFACT_BINDING
NO_STALE_RESOURCE_BINDING
NO_UNDECLARED_ARTIFACT_PORT
NO_PROVIDER_ARTIFACT_PAYLOAD_EXPOSURE
NO_REJECTED_CANDIDATE_LEAK_TO_LLM
NO_FULL_REGISTRY_LEAK_TO_LLM
NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES
NO_SECRET_PATTERN_HITS
```

Prompt/artifact injection, HTML/script, credentials, duplicate keys, path/URL,
oversized/nested content, stale/foreign artifacts, and hash/contract/media
tampering remain inert or typed failures. No new dependency or execution
authority was added.

## 20. Evidence Inventory

`docs/phase10l/evidence/phase10l3_bounded_multi_tool/` retains entry/schema,
38-tool inventory, compatibility/real chain, success/partial/failure runtime,
API, migration/persistence, lineage, performance/security, browser DOM/network/
console/accessibility, desktop/mobile PNGs, and an LF-normalized text/raw-PNG
SHA-256 manifest.

## 21. Tests

- local full backend: `917 passed, 30 skipped, 63 warnings`.
- exact-SHA CI unit: `917 passed, 1 skipped, 29 deselected, 63 warnings`;
  Phase 10 closure `3 passed, 6 deselected`.
- final L1/L2/L3 focused backend: `70 passed`.
- L3 persistence/service-local: `5 passed, 1 skipped`; local services are
  `UNAVAILABLE`, not reported as PASS.
- exact-SHA service-backed: `28 passed, 0 skipped, 0 failed`; PostgreSQL,
  Redis, MinIO, Alembic head, tables/indexes, and no-skipped PASS.
- frontend: 52 files / `328 passed`; typecheck and production build PASS.
- browser: Chromium/Firefox/WebKit and 390x844 mobile PASS.
- lock, npm dependency tree, diff, evidence manifest, Phase 10 closure, docs/
  TASKS checks, and secret scan PASS.
- npm audit: `UNAVAILABLE`; configured mirror returned `404 NOT_IMPLEMENTED`,
  so no clean claim is made.

## 22. Production Behavior Changes

- Canonical dependent work can now produce AnalysisPlan 0.2.
- Only 0.2 uses deterministic dependency validation/topological Runtime.
- Runtime creates exact artifact refs and immutable execution/lineage records.
- Failed branches block descendants while independent work continues.
- API and PlannerWorkbench expose additive graph/partial/lineage state.
- AnalysisPlan 0.1 and its Runtime behavior remain unchanged.

## 23. Files Changed

Backend schemas, repositories/API and Alembic migration; Tool Registry port
metadata/validator; Planner composer; QueueWorkerRuntime; TypeScript/shared
schemas; PlannerWorkbench/styles/API types; focused/integration/browser tests;
CI; evidence and screenshots; Phase 10L/shared docs; persistent records and
TASKS. Dependency and lock files are unchanged.

## 24. Commit and Exact-SHA CI History

- implementation: `d395db2a4f59e2f5fb72e0b33b45161b2bcb5670`.
- implementation exact-SHA CI: run `30542148803`, all required jobs success.
- failed implementation CI attempts: none.
- completion-record and archive SHA/CI follow in the closure addendum.

## 25. Explicit Non-Scope Confirmation

No generic DAG/workflow engine, parallel scheduler, loops/conditions/fan-out,
runtime replanning/LLM, extra repair or retry redesign, plan editor/approval,
cross-job/remote artifact input, arbitrary artifact binding, Python/shell/
filesystem/notebook/script authority, external science API, interpretation,
full natural-language evidence closure, Workspace, professional science,
Fermi surface, CrystalNN, experimental XRD, advanced trajectory, Band/DOS,
enterprise infrastructure, plugin ecosystem, new LLM SDK, or uncontrolled
dependency was implemented.

## 26. Remaining Phase 10L Gaps

```text
Phase 10L-4: Grounded Scientific Result Interpretation
Phase 10L-5: Natural-Language Analysis Evidence Closure
```

These are reviewer-gated gaps, not executable tasks.

## 27. Queue State

```text
Phase 10L-3 = COMPLETE / AWAITING_COMPLETION_RECORD_CI
Phase 10L-4 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
TASK_BLOCK_COUNT = 1 pending verified archive
```

## 28. Whether Phase 10L-4 Was Entered Automatically

```text
NO
PHASE_10L4_EXECUTABLE_TASK_CREATED = NO
```

## 29. Next Action

Verify this completion-record exact-SHA CI, then create and verify the separate
queue-archive commit. Return the complete result and stop. Do not create,
queue, or execute Phase 10L-4.

## 30. Repository State at Completion Record

- implementation HEAD/origin: `d395db2a4f59e2f5fb72e0b33b45161b2bcb5670`.
- implementation CI: `30542148803`, success.
- completion-record CI: pending this record's commit.
- archive CI: pending completion-record success.

## Phase 10L-3 Closure Addendum - 2026-07-30 20:32:51 +08:00

- Completion record commit:
  `2bd06f22562a9fb1baf65730d30682c1d0ca6c54`.
- Completion-record exact-SHA CI: run `30542844246`, `success`.
- Required jobs: Unit Tests `success`; Frontend Typecheck & Build `success`;
  PostgreSQL + Redis + MinIO migration/service-backed integration `success`;
  28 selected integration tests passed with zero skipped/failed.
- Queue verification: permanent result, implementation CI, browser/evidence,
  completion record, and completion-record CI agree.
- Archive action: the complete Phase 10L-3 `---TASK---` block is deleted by
  the queue-archive commit; Phase 10L-4 remains only a reviewer gate and no
  executable Phase 10L-4 task exists.
- Archive commit exact SHA and CI run are reported in the reviewer return after
  the final exact-SHA gate; this addendum is not rewritten after archive.

# Phase 10M-0 Unified Scientific Workspace Fact Audit + Information Architecture Seal Result

Completion date: 2026-08-01 (Asia/Shanghai)

## 1. Conclusion

```text
PASS / COMPLETE / REVIEWER_APPROVAL_REQUIRED
```

The repository fact audit, information architecture seal, implementation
backlog, acceptance map, execution lock, and execution manifest are complete.
No Phase 10M production implementation was performed.

## 2. Baseline

- Branch: `master`.
- Initial `HEAD == origin/master`:
  `8f304fa08ddab1cefd69848f621f8438fc2038d5`.
- Phase 10L-5 implementation:
  `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37`; CI `30693848581`, success.
- Phase 10L-5 completion record:
  `e4b0a8f5619cbb1001ef64809db6400729a99d8d`; CI `30694747664`, success.
- Phase 10L-5 verified queue archive:
  `8f304fa08ddab1cefd69848f621f8438fc2038d5`; CI `30695065220`, success.
- Entry worktree: clean. `TASK_BLOCK_COUNT = 0`.
- Phase 10M production source implementation at entry: absent.

## 3. Production Behavior Changes

```text
Production Behavior Changes:
NONE
```

Production source, schemas, migrations, API, frontend behavior, Tool Registry,
Adapters, Runtime, dependencies, lockfile, and `TASKS.md` are unchanged.

## 4. Current Workspace Maturity

```text
CURRENT_WORKSPACE_LEVEL = WORKSPACE_LIKE_SINGLE_PAGE
```

PlannerWorkbench on `/` exposes data setup, intent/planning, execution,
artifacts, interpretation/evidence, report/recipe summaries, and audit JSON in
one page. It is not a formal Workspace: there is no Workspace identity, route,
aggregate persistence/API, history browser, deep link, saved layout, or global
canonical selection context.

## 5. Current Route / Component / API Map

The current product has root `/`, framework 404/icon routes, PlannerWorkbench,
product-specific preview panels, timeline/dependency/interpretation sections,
and six independent read paths for plans/jobs/events/tool calls/artifacts and
interpretations. The complete implementation-grounded map is retained in
`docs/phase10m/phase10m0_current_page_route_component_map.md` and evidence
`route_inventory.md`, `component_inventory.md`, and `api_inventory.md`.

## 6. Current Domain / Persistence

Job is the current analysis container. Persisted Plan -> Job -> ToolCall ->
Artifact relations, dependency execution, lineage, evidence bundles,
interpretations, Reports, and Recipes are sufficient for deterministic lazy
Workspace projection. No Workspace/session projection or UI-state persistence
currently exists.

## 7. Current Artifact / Renderer Surface

The audit covers Registry `0.1.0`, 53 registered tools, 38 Planner-visible
tools, typed artifacts, viewers, generic inert fallback, download behavior,
lineage, and 12 grounded projector combinations. Product-specific scientific
renderers are reusable; generic JSON/text preview is not classified as a ready
scientific panel. The full matrix is retained in
`phase10m0_artifact_renderer_matrix.md`.

## 8. Current Interpretation / Evidence Surface

ScientificEvidenceBundle 1.0 and GroundedScientificInterpretation 1.0 are
persisted per terminal Job. PlannerWorkbench shows findings, warnings,
limitations, evidence drill-down, partial disclosure, provider/repair state,
and inert audit JSON. There is no cross-panel evidence inspector or Workspace
deep link today.

## 9. Current Report / Recipe Surface

Report and Recipe are existing persisted first-class records, but current UI
exposes summary/inert preview rather than composition, selection, export, and
history workflows. Phase 10M reuses their ownership and does not create a
second report/recipe authority.

## 10. Identity and Lineage

The audit maps Project, Dataset/version, Profile, object/sample, structure/site,
trajectory atom/frame, phonon q-point/branch, reciprocal point, volumetric
field, Intent, Eligibility, Plan/step/binding, Job, ToolCall, Artifact/lineage,
Evidence, Claim, Interpretation, Report, and Recipe identities. Cross-panel
selection must use exact stable IDs and source versions; array index, display
label, row order, fuzzy matching, and unit guessing are forbidden.

## 11. Current State and Error Taxonomy

Existing Job, ToolCall, dependency execution, binding, interpretation, and
renderer states remain sources of truth. The sealed Workspace/panel taxonomy is
an explicit UI/domain projection over those states; it does not rename or
rewrite historical execution records.

## 12. Browser / Responsive / Accessibility Facts

- Current L5 replay: Chromium, Firefox, WebKit desktop and Chromium 390x844;
  five ready cases plus clarification, unsupported, and capability mismatch.
- Current L4 replay: three desktop browsers and Chromium mobile for findings,
  evidence, partial, no-evidence, validation, and integrity states.
- Console/page errors: 0. Unapproved external requests: 0. Live API/provider
  forwarding: 0. `REAL_LLM_CALLS = 0`.
- Firefox/WebKit mobile: `UNAVAILABLE`; not inferred from desktop.
- Current long expanded audit JSON produces a very tall mobile document and is
  an explicit Phase 10M-6 presentation target, not a false current PASS claim.

## 13. Frontend Scientific Authority Audit

```text
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
```

Current scientific authority remains Registered Adapter -> QueueWorkerRuntime
-> persisted Artifact -> validated frontend mapper. Frontend calculations are
limited to display formatting, sorting/filtering, camera/coordinate display,
and contract-approved bounded presentation behavior.

## 14. Workspace Information Architecture Decision

The sealed desktop IA is Workspace header plus side navigation for Data, Plan,
Execution, Results, Findings, Evidence, Provenance, and Report; a central panel
stack; and one exact-identity inspector. PlannerWorkbench remains the `/`
analysis entry and successful persisted Jobs navigate to the Workspace route.

## 15. Workspace Entity / Cardinality Decision

```text
WORKSPACE_IS_FIRST_CLASS_PERSISTED_ENTITY = YES
WORKSPACE_CARDINALITY = ONE_WORKSPACE_PER_JOB
```

ScientificWorkspace 1.0 stores exact source references and version/hash
bindings. It never copies source science or caches Artifact payload as source
of truth. Mutable user layout/title state is separated from immutable runtime
references and revisioned.

## 16. Persistence Decision

Server persistence owns Workspace identity, panel membership/layout revisions,
title, and durable user state. URL owns active panel and exact shareable
selection; memory owns transient camera/expanded-row state. Canonical state is
not stored in localStorage/sessionStorage.

## 17. Database Migration Decision

```text
DATABASE_MIGRATION_REQUIRED = YES
```

Phase 10M-1 adds Alembic `0007_phase10m1_workspace_domain` with
`scientific_workspaces`, `workspace_panels`, and
`workspace_layout_revisions`; exact nullability, defaults, FKs, uniqueness,
indexes, `ON DELETE RESTRICT`, upgrade/downgrade, and no-backfill lazy projection
policy are sealed. No migration was created in Phase 10M-0.

## 18. API Decision

```text
NEW_WORKSPACE_API_REQUIRED = YES
```

Sealed additive endpoints cover create/project, get, patch with `If-Match`,
project list, source-Job projection, panel/history reads, and exact M5
Report/Recipe composition endpoints. Create is idempotent on
`(projectId, sourceJobId)` and does not require `If-Match`. No API was added in
Phase 10M-0.

## 19. Route / Navigation Decision

Canonical route: `/workspaces/{workspaceId}`. `/` remains PlannerWorkbench.
Query state carries `panel` and versioned exact selection only. Browser
back/forward restores those states; missing/stale sources render typed
read-only states rather than silent rebinding.

## 20. Panel Contract Decision

```text
PANEL_CONTRACT_REQUIRED = YES
```

WorkspacePanel 1.0 owns panel ID/kind/title, source refs, renderer contract,
state/error/partial projections, exact selection I/O, evidence/provenance,
layout/mobile/accessibility metadata, capability requirement, and inert
unsupported fallback. Maximum panels per Workspace: 32.

## 21. Selection Context Decision

WorkspaceSelectionContext 1.0 is required. It carries exact identity kind/ID,
source dataset/resource/artifact version and hash, scope, propagation,
compatibility, clearing, bounded multi-selection, URL encoding, subscriptions,
and typed stale/unsupported mapping. The server does not persist ephemeral
selection.

## 22. Report / Recipe Decision

Existing Report and Recipe persistence remains authoritative. M5 adds
composition APIs without new report/recipe tables. Reports retain partial and
failed disclosures, evidence, lineage, selected panels/findings, and export.
Recipes bind exact Profile, Intent, Plan, tool versions, parameters,
dependencies, and artifact contracts.

```text
recommendation != executable plan
```

## 23. Historical Compatibility Decision

Historical Jobs use idempotent lazy Workspace projection, not bulk backfill.
AnalysisPlan 0.1/0.2, old Jobs/Artifacts, jobs without interpretation or graph,
partial execution, missing Profile, stale dataset versions, legacy reports and
recipes are preserved and projected as typed read-only/stale/unsupported states.
Scientific identities are never silently upgraded.

## 24. Mobile / Accessibility Decision

Mobile uses one active panel, a dataset/context drawer, a panel switcher, and
an inspector bottom sheet; it is not a compressed desktop split view. Sealed
accessibility includes deterministic focus order, visible focus, semantic
headings, status announcements, non-color state, table/chart/WebGL text
alternatives, reduced motion, zoom, and at least 44x44 CSS-pixel touch targets.

## 25. Performance / Loading Decision

Workspace loads identity/status/panel metadata first, then lazy artifact data.
Heavy viewers load on activation; requests are cancellable; WebGL contexts and
observers are disposed on unmount. Cache keys include Workspace revision and
source hashes; stale invalidation is exact. Adjacent panel metadata prefetch is
disabled. Limits include 32 panels and 128 layout revisions; revision 129 is a
typed `REVISION_CAP_EXCEEDED` rejection. Targets are development/browser
acceptance targets, not production capacity claims.

## 26. Security Boundary

Artifact content remains inert data: no artifact HTML/JavaScript/iframe/module,
no external artifact URL execution, no arbitrary code/shell/filesystem, no
provider authority, no recommendation-to-plan/job/enqueue, no cross-job or
cross-project artifact access, no stale identity rebinding, and no credential,
path, or stack disclosure. New/changed audit content has zero secret-pattern
or private-path hits.

## 27. Decision Log

M-D001 through M-D025 are all
`SEALED_FOR_REVIEWER_APPROVAL`: Workspace entity/cardinality, persistence,
migration, API, route, historical projection, Panel/renderer/selection,
Report/Recipe, partial/error, mobile/accessibility/performance/WebGL/security,
compatibility, PlannerWorkbench transition, save/recovery, deep links,
staleness, and Phase ordering. No implementation-affecting decision is blocked.

## 28. Phase 10M Implementation Sequence

1. 10M-1: Workspace Domain Contract + Persistence.
2. 10M-2: Unified Workspace Shell.
3. 10M-3: Cross-Artifact Navigation + Canonical Selection.
4. 10M-4: Typed Artifact Gallery + Scientific Viewer Integration.
5. 10M-5: Scientific Report + Recipe Composition.
6. 10M-6: Save / Reload / Recovery / Responsive Closure.
7. 10M-7: Workspace Integration + Browser/API/Service Evidence Closure.

Each phase has exact source/schema/database/API/frontend/test/browser/service/
security scope, entry/exit gates, dependencies, and non-scope in
`phase10m_implementation_backlog.md`.

## 29. Acceptance and Test Plan

The plan defines 53 unique acceptance IDs: M1=8, M2=7, M3=7, M4=8, M5=7,
M6=8, M7=8. The acceptance plan and execution lock contain exactly the same
ID set with zero missing, extra, duplicate, or shorthand entries.

## 30. Execution Lock

`phase10m_execution_lock.md` freezes facts, 25 decisions, files, migration,
API/schema/route/panel/selection/report/security/performance/compatibility
boundaries, M1-M7 order, stop conditions, and reviewer gates.

```text
The implementation agent is not authorized to redesign
Workspace identity, persistence, API, migration, routing,
panel contracts, selection identity, report ownership,
compatibility, security, or Phase ordering.
```

## 31. Execution Manifest

`phase10m_execution_manifest.md` is the sole high-level implementation entry.
It records baseline, canonical docs, decision IDs, phases, modules, migration,
APIs, schemas, routes/components, tests, browsers, services, CI, evidence,
security markers, completion format, stop conditions, and reviewer gates.

## 32. Files Changed

- Audit/planning commit: 156 files, all under `docs/` or `persistent/`.
- Added 22 canonical Phase 10M documents and the retained audit evidence tree.
- Updated docs index/roadmap/shared-schema proposal and seven persistent records.
- `production source = unchanged`.
- `dependencies = unchanged`; `lockfile = unchanged`.
- `TASKS.md = unchanged`.
- This completion record appends `results.md` and updates persistent completion
  state only.

## 33. Checks

- `git diff --check`: PASS.
- `uv lock --check`: PASS, 108 packages resolved; lock unchanged.
- Focused backend: 292 passed.
- Full local backend: 1078 passed, 38 skipped, 63 warnings; local services were
  unavailable, so integration skips are not claimed as service PASS.
- Full local frontend: 52 files, 333 tests passed; focused: 15 files, 129 passed.
- Typecheck/build/npm dependency tree: PASS.
- Current browser audit: Chromium/Firefox/WebKit desktop and Chromium 390x844
  capture replay PASS for the audited current surfaces.
- Exact-SHA CI Unit: 1078 passed, 1 skipped, 37 deselected, 63 warnings;
  Phase 10L-5 closure 99 passed.
- Exact-SHA CI service-backed: 36 passed, 0 skipped, 0 failed, 0 errors.
- Evidence manifest: 123 retained files, zero hash/membership mismatches.
- Docs links: 40 documents checked, zero invalid local links.
- `TASK_BLOCK_COUNT = 0`; `TASKS.md` diff zero.
- New/changed secret scan: PASS; `NO_SECRET_PATTERN_HITS`.
- `LOCAL_SERVICE_BACKED = UNAVAILABLE`; `CI_SERVICE_BACKED = PASS`.
- `npm audit = UNAVAILABLE` because the configured mirror returned
  `404 NOT_IMPLEMENTED`; it is not reported clean.
- Known non-blocking warnings: existing pymatgen/spglib warnings and GitHub
  Actions Node 20 deprecation notices.

## 34. Commit / CI

- Audit/planning commit:
  `4c5d25ef00b2213683a3115febc5f482546cc522`.
- Audit/planning exact-SHA CI: run `30698489359`, success; Unit, Frontend,
  browser replay/build, PostgreSQL/Redis/MinIO, and no-skipped jobs succeeded.
- Completion record: the commit containing this append-only section.
- Completion-record exact-SHA CI: required before final reviewer return; exact
  SHA and run are reported from immutable Git history in the final return.
- Failed audit/planning CI attempts: none.

## 35. Explicit Non-Scope

No Workspace production contract, migration, API, UI, route, panel renderer,
selection runtime, report productization, save/reload behavior, Phase 10N
science, source code, dependency, lockfile, real DeepSeek, or other real LLM
call was implemented. No Workspace/DAG/workflow editor, new scientific
algorithm/tool, arbitrary code/shell/filesystem/network authority, RAG,
memory, multi-agent product, plugin market, or autonomous replanning was added.

## 36. Reviewer Decisions

```text
NO IMPLEMENTATION DECISION IS LEFT TO THE EXECUTION AGENT
```

The reviewer only approves or revises this sealed proposal. Any revision to
identity, cardinality, migration, API, route, Panel/Selection contract,
Report/Recipe ownership, compatibility, security, or phase ordering requires a
new reviewer decision.

## 37. Queue State

```text
Phase 10M-0:
COMPLETE / REVIEWER_APPROVAL_REQUIRED

Phase 10M-1:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 0

TASKS.md:
UNCHANGED
```

## 38. Automatic Phase 10M-1 Entry

```text
NO
PHASE_10M1_EXECUTABLE_TASK_CREATED = NO
```

## 39. Next Action

```text
Return the complete Phase 10M-0 result to the reviewer.
Do not create, queue, or execute Phase 10M-1.
```

## 40. Final Repository State

- Audit/planning SHA: `4c5d25ef00b2213683a3115febc5f482546cc522`.
- Audit/planning CI: `30698489359`, success.
- Completion record: this results-bearing commit; exact SHA/CI reported in the
  final reviewer return after its required exact-SHA gate.
- Expected final state after that gate: `HEAD == origin/master`, clean,
  `TASK_BLOCK_COUNT = 0`, production source unchanged.

# Phase 10M-1 Scientific Workspace Domain Contract + Persistence Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

The reviewer-sealed Workspace domain, persistence, migration, projection, and
API scope is implemented. Corrected implementation exact-SHA CI is successful;
the task remains in `TASKS.md` until completion-record and queue-archive CI
succeed.

## 2. Baseline and Entry Gate

- Phase 10M-0 audit/planning: `4c5d25ef00b2213683a3115febc5f482546cc522`,
  CI `30698489359` success.
- Phase 10M-0 completion: `2f4a5682fbc2adb0fdc487a982ec508f138eb41a`,
  CI `30698988085` success and reviewer approved.
- Initial `HEAD == origin/master == 2f4a5682fbc2adb0fdc487a982ec508f138eb41a`,
  branch `master`, worktree clean, migration head `0006`.
- Queue admission produced one exact M1 block; M2 remained a reviewer gate.

## 3. Phase 10M-0 Decision Compliance

M-D001 through M-D025 remain unchanged. One Workspace per Job, the three-table
schema, explicit projection, reference-only science authority, API ownership,
Panel/Selection contracts, route ownership, compatibility, security, and
M1-M7 ordering were implemented without redesign.

## 4. ScientificWorkspace 1.0

The strict contract binds deterministic Workspace identity to exact
`(projectId, sourceJobId)`, records immutable dataset/Profile/Intent/Plan source
versions and hashes, and permits only bounded title, active-panel, pinned exact
selection, durable metadata, and revision changes. Unknown fields, invalid
IDs/hashes, prototype keys, non-finite values, deep/oversized payloads, and
executable content are rejected. `executionAuthorized=false` and
`scientificAuthority=false` are explicit.

## 5. WorkspacePanel 1.0

Panel descriptors retain exact Workspace/source/Artifact/ToolCall/step and
renderer-contract references, projected state, evidence/provenance links,
layout and accessibility metadata, and deterministic order. Unsupported sources
become inert fallback descriptors. `MAX_PANELS_PER_WORKSPACE=32`; panel 33 is a
typed rejection. Artifact payloads and arbitrary component/module authority are
not stored.

## 6. WorkspaceSelectionContext 1.0

The strict value contract uses exact source-scoped identities, bounded
multi-selection, exact-only propagation, deterministic serialization, and a
2,048-byte URL representation. Display labels, row/array position, fuzzy/latest
rebinding, raw prompts/payloads, URLs, paths, credentials, and expressions are
rejected. M1 implements validation/serialization only; ephemeral selection is
not persisted and propagation remains M3 scope.

## 7. Canonical Identity and Source Binding

Workspace source bindings point to existing Project, Job, dataset/version,
Profile/hash, Intent/hash, Eligibility/decision where available, Plan/hash,
dependency execution, Artifacts/hashes/contracts, interpretation, Report, and
Recipe records. Sources remain immutable; stale or missing identities produce
typed projection state rather than latest-wins substitution.

## 8. Persistence Architecture

Repository protocols, in-memory implementation, and SQLAlchemy implementation
share create/get/list/update, panel, and layout-history semantics. Immutable
source conflicts, stale compare-and-set updates, cross-project access, duplicate
records, cap overflow, and SQL integrity failures are translated to bounded
typed errors. Workspace records store references and durable presentation data,
not source scientific values.

## 9. Database Migration

Alembic `0007_phase10m1_workspace_domain` creates exactly:

- `scientific_workspaces`;
- `workspace_panels`;
- `workspace_layout_revisions`.

It adds project/job and child lookup indexes, one-row-per-project/job uniqueness,
unique Workspace revision ordering, sealed foreign keys and `ON DELETE
RESTRICT` source behavior. SQLite `0006 -> 0007 -> 0006 -> 0007`, fresh
`0001 -> 0007`, and PostgreSQL migration/service inspection pass. There is no
backfill and `metadata.create_all()` is not migration authority.

## 10. Repository Implementations

In-memory and SQLAlchemy repositories pass parity tests for idempotent create,
conflicting create, exact lookup, project list, mutable title/layout update,
immutable source rejection, stale revision conflict, panel order, history,
rollback, cap handling, and project isolation.

## 11. Workspace Creation

Explicit create/project validates the exact Project and source Job, computes
immutable source bindings, projects bounded panel descriptors, appends initial
layout revision, and returns the same Workspace for semantic retries. Ordinary
GET/list operations never create a Workspace. No tool, provider, planner, Job,
enqueue, or Artifact payload read is part of creation.

## 12. Layout Revisions

Layout revisions are immutable, monotonic, canonically serialized, and bound to
panels owned by the Workspace. PATCH uses quoted `If-Match`; stale or malformed
ETags are typed errors. `MAX_LAYOUT_REVISIONS=128`; revision 129 returns
`REVISION_CAP_EXCEEDED` without deleting history.

## 13. Historical Job Projection

Explicit lazy projection covers Plan 0.2 and historical 0.1 Jobs, graph/no-graph,
all-succeeded/partial/failed/running states allowed by the seal, missing
interpretation/Profile/Artifact, stale datasets, legacy Artifacts, and
Report/Recipe presence or absence. Legacy records remain read-only where
required; no graph, interpretation, Artifact, or identity is invented. Repeated
projection is idempotent; there is no bulk backfill or hidden GET write.

## 14. Workspace API

Implemented additive routes:

- `POST /workspaces`;
- `GET|PATCH /workspaces/{workspaceId}`;
- `GET /projects/{projectId}/workspaces`;
- `GET /projects/{projectId}/analysis-jobs`;
- `GET /workspaces/{workspaceId}/panels`;
- `GET /workspaces/{workspaceId}/panels/{panelId}`;
- `GET /workspaces/{workspaceId}/layout-revisions`;
- `GET /workspaces/{workspaceId}/layout-revisions/{revision}`.

Create uses `Idempotency-Key`; PATCH uses `If-Match`; reads are metadata-only
and bounded. Strict duplicate-key/unknown-field/UTF-8/size validation and typed
error envelopes prevent stack, SQL, path, storage-key, secret, or provider
disclosure. TypeScript client functions match these contracts.

## 15. Optimistic Concurrency

Workspace revision and ETag are exact compare-and-set identities. A valid PATCH
appends an immutable revision and advances the current pointer atomically;
stale writes return a typed conflict and cannot overwrite newer state.

## 16. Project and Source Isolation

Project, Job, Workspace, panel, layout, and source Artifact scopes are checked
before reads or writes. Cross-project Jobs, foreign Artifacts, stale hashes,
unknown panels, and cross-Workspace layout references are rejected.

## 17. Scientific Integrity

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
```

Workspace performs no scientific calculation and does not infer identity from
filenames, MIME labels, display labels, or array positions. Registered Adapter
to Runtime to persisted Artifact remains the scientific authority chain.

## 18. Compatibility

`/` remains PlannerWorkbench. AnalysisIntent 1.0, EligibilityResolution 1.0,
AnalysisPlan 0.1/0.2, PlanValidator, QueueWorkerRuntime, Registry/Adapters,
Job/ToolCall/Artifact, interpretation, Report/Recipe, historical APIs, and the
DeepSeek-only provider policy remain semantically unchanged. Workspace APIs are
additive and do not require existing clients to migrate.

## 19. Caps and Performance

Caps include 32 panels, 128 revisions, 16 secondary selections, 2,048-byte
selection URLs, 131,072-byte mutations, 524,288-byte snapshots, and JSON depth
14. Focused development evidence reports two project-list queries for both one
and five Workspaces, zero Artifact payload reads during projection, no bulk
backfill, full backend 208.26 s, frontend tests 60.71 s, and build 95.8 s.
These are development/service-backed acceptance measurements, not production
capacity claims.

## 20. Security

```text
NO_WORKSPACE_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_SHELL_OR_FILESYSTEM_AUTHORITY = PASS
NO_WORKSPACE_PROVIDER_AUTHORITY = PASS
NO_WORKSPACE_TOOLCALL_JOB_OR_ENQUEUE_AUTHORITY = PASS
NO_WORKSPACE_ARTIFACT_JAVASCRIPT = PASS
NO_WORKSPACE_ARTIFACT_HTML_EXECUTION = PASS
NO_WORKSPACE_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS
NO_WORKSPACE_CROSS_PROJECT_SOURCE_ACCESS = PASS
NO_WORKSPACE_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_WORKSPACE_STALE_IDENTITY_REBINDING = PASS
NO_WORKSPACE_SECRET_OR_PRIVATE_PATH_DISCLOSURE = PASS
NO_RECOMMENDATION_TO_EXECUTION_AUTHORITY = PASS
NO_SECRET_PATTERN_HITS = PASS
REAL_LLM_CALLS = 0
```

HTML/script/Markdown, prototype keys, URL/path/module injection, foreign source,
stale hashes, malformed ETag, deep/oversized JSON, prompt injection, and
credential-shaped text are inert or typed rejection.

## 21. Service-Backed Evidence

Local Docker/services were unavailable: `LOCAL_SERVICE_BACKED=UNAVAILABLE`.
Corrected exact-SHA CI run `30705503707` used PostgreSQL 16, Redis 7, and MinIO
with the full migration chain, repositories, source records, API lifecycle,
scope and `ON DELETE RESTRICT` checks: `37 passed, 0 skipped, 0 failed, 0
errors`. Therefore `CI_SERVICE_BACKED=PASS` and `SERVICE_TESTS_SKIPPED=0`.

## 22. Browser Regression

Existing PlannerWorkbench and L4/L5 findings/evidence browser replays pass on
Chromium, Firefox, WebKit, and Chromium 390x844 mobile with no new console,
network, overflow, HTML/JS, or secret regressions.

```text
WORKSPACE_UI = NOT_IMPLEMENTED_BY_DESIGN
WORKSPACE_ROUTE_PAGE = DEFERRED_TO_PHASE_10M2
```

## 23. Acceptance IDs

```text
M1 expected = 8
implemented = 8
missing = 0
extra = 0
duplicate = 0
```

- M1-A01: Python/JSON Schema/TypeScript contracts and strict caps.
- M1-A02: in-memory/SQLite persistence, immutable refs, idempotency/revisions.
- M1-A03: 0007 upgrade/downgrade/re-upgrade.
- M1-A04: PostgreSQL Workspace/panel/revision zero-skip round trip.
- M1-A05: additive typed APIs, ETag, idempotency.
- M1-A06: scope, identity, deletion, and cap rejection.
- M1-A07: modern and explicit legacy read-only projection.
- M1-A08: no payload copy, disclosure, execution authority, or cross-project
  access.

## 24. Tests

- Focused M1: 26 passed; final migration/evidence subset: 4 passed.
- Full local backend: 1103 passed, 39 skipped, 63 warnings. Local service skips
  are not claimed as service PASS.
- Corrected CI Unit: 1104 passed, 1 skipped, 38 deselected, 63 warnings;
  Phase 10 backend closure 3 passed and L5 closure 99 passed.
- Frontend: 52 files, 333 tests; typecheck and production build PASS.
- Browser: L4/L5 Chromium, Firefox, WebKit, and mobile replay PASS.
- SQLite/PostgreSQL migration, evidence manifest, docs links, TASKS structure,
  secret scan, dependency/lock consistency, and service no-skipped gate PASS.
- `npm audit = UNAVAILABLE` because the configured mirror returned
  `404_NOT_IMPLEMENTED`; it is not reported clean.
- Known non-blocking warnings: existing pymatgen/spglib warnings and GitHub
  Actions Node 20 deprecation notices.

## 25. Production Behavior Changes

Added only ScientificWorkspace/Panel/Selection contracts, Workspace persistence
and repositories, explicit historical projection, additive Workspace APIs and
typed client, layout revisions, and optimistic concurrency.

```text
Planner behavior changes = NONE
AnalysisIntent behavior changes = NONE
Eligibility behavior changes = NONE
AnalysisPlan behavior changes = NONE
QueueWorkerRuntime behavior changes = NONE
Tool Registry behavior changes = NONE
Adapter behavior changes = NONE
Scientific calculation changes = NONE
Interpretation behavior changes = NONE
Real LLM calls = 0
Workspace UI changes = NONE
```

## 26. Files Changed

- Backend/API: Workspace contracts, repository models/implementations,
  projection service, router registration, strict request handling.
- Migration: Alembic env compatibility, SQLite-safe historical migration paths,
  and `0007_phase10m1_workspace_domain`.
- TypeScript: strict Workspace contracts and API client only.
- Tests/CI: contract, migration, persistence, projection/API, performance,
  service-backed, evidence, and existing browser-runner reliability.
- Evidence/docs/persistent/TASKS: Phase M1 records and deterministic manifest.

```text
dependencies = unchanged
lockfile = unchanged
```

## 27. Commit and CI History

- Failed implementation `d39687f7fe5ce39de0fe375a2b5d3068626b74f0`,
  run `30704917567`: Unit/Frontend passed; service was `36 passed, 0 skipped,
  1 failed`. Fixture passed a percent-encoded isolated-schema URL through
  ConfigParser interpolation before migration.
- Failed correction `7d0a16d1be7dadd3dffa17adc3d22f3e12a618f4`,
  run `30705191850`: Unit/Frontend passed; service was `36 passed, 0 skipped,
  1 failed`. Production Alembic `env.py` still passed percent-encoded
  `DATABASE_URL` through ConfigParser unescaped.
- Corrected implementation `27c5aa98138f882a750dc76a402ee2afe2151b72`,
  run `30705503707`: Unit, Frontend, and service-backed all success.
- Completion-record SHA/CI: this commit, pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 28. Explicit Non-Scope

Not implemented: M2 Workspace page/shell/navigation/panel UI; M3 selection
propagation/URL runtime; M4 Artifact Gallery/renderers/WebGL/trajectory/phonon/
volumetric Workspace integration; M5 Report/Recipe composition; M6 save/reload,
recovery, responsive/mobile Workspace UX; M7 final Workspace closure; Phase 10N
science; CrystalNN/VoronoiNN, experimental XRD, trajectory analytics,
Electronic Band/DOS; arbitrary code/shell/notebook/filesystem/external science
API; new LLM dependency or real DeepSeek call; autonomous replanning, generic
workflow, multi-job Workspace, RAG/memory/multi-agent, plugin marketplace, or
enterprise SaaS.

## 29. Phase 10M Readiness

```text
Phase 10M-1:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-2:
REVIEWER_GATE
```

Phase 10M as a whole is not complete.

## 30. Queue State

```text
Phase 10M-1:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-2:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 31. Automatic Phase 10M-2 Entry

```text
NO
PHASE_10M2_EXECUTABLE_TASK_CREATED = NO
```

## 32. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only the completed
Phase 10M-1 task by a separate verified queue commit. Do not create, queue, or
execute Phase 10M-2.
```

## 33. Final Repository State

- Corrected implementation SHA: `27c5aa98138f882a750dc76a402ee2afe2151b72`.
- Implementation exact-SHA CI: `30705503707`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected current post-commit state: `HEAD == origin/master`, clean except for
  lifecycle commits in progress, migration head `0007`, task count 1.

# Phase 10M-2 Unified Scientific Workspace Shell Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

The corrected implementation exact-SHA CI is complete. The task remains in
`TASKS.md` until this completion record and the separate queue archive each pass
their own exact-SHA CI.

## 2. Baseline and Entry Gate

- M1 implementation `27c5aa98138f882a750dc76a402ee2afe2151b72`, CI
  `30705503707`, success.
- M1 completion `7f6a3fa66236fdcdcaab5d12e515c201ab2a63bd`, CI
  `30706195493`, success.
- M1 archive `08f2133c6a02b64a199f40a0b17ccfa5d0e68cc7`, CI
  `30706443734`, success.
- Initial `HEAD == origin/master == 08f2133c...`, branch `master`, clean
  worktree, migration head `0007_phase10m1_workspace_domain`.
- M2 was admitted as the active task. A later reviewer/user-supplied M3 block
  is pending and was not entered during M2 implementation.

## 3. M0/M1 Decision Compliance

M-D001 through M-D025 remain unchanged. M2 consumes the one-Workspace-per-Job
M1 contracts, immutable source bindings, panel descriptors, layout revisions,
metadata APIs, explicit projection, ETag, and project scope. It adds no schema,
migration, repository, scientific authority, or hidden Workspace creation.

## 4. Workspace Route

Added `/workspaces/{workspaceId}` with Next loading/error boundaries and exact
metadata loading. `/` remains PlannerWorkbench. Unknown or inaccessible
Workspace IDs show typed errors; the route does not create a Workspace.

## 5. PlannerWorkbench Transition

PlannerWorkbench can explicitly project/open the current Job through the M1
idempotent POST and can list metadata-only project Workspace history. Exact
Workspace links are used; GET remains side-effect free.

## 6. Workspace Data Loading

The shell requests only `GET /workspaces/{workspaceId}` metadata. Abort signals
and request identities suppress stale responses. Initial load requests no
Artifact payload, object-store key, full array, provider data, or scientific
recalculation.

## 7. Workspace Header

The header shows exact Workspace title, projected state, source Job, revision,
panel count, and bounded provenance actions. Long identities wrap without
changing layout authority.

## 8. Desktop Information Architecture

Desktop uses the sealed global header, collapsible data/context rail, nine
navigation groups, one active panel, and overlay inspector. Panel descriptor
order is deterministic and does not imply scientific dependency.

## 9. Mobile Information Architecture

At 390x844 the shell presents one active panel, a context/navigation drawer,
and inspector bottom sheet. It does not shrink the desktop three-column layout.

## 10. Panel Switcher and Panel Shell

Exact visible panel IDs drive the switcher. Unknown IDs never select by label
or array position. One active panel is mounted; unsupported and failed panels
remain isolated typed surfaces.

## 11. Dataset/Context Drawer

The drawer exposes bounded source references and panel membership metadata. It
does not copy Artifact content or infer identity from filenames/MIME labels.

## 12. Inspector Shell

The inspector provides metadata, status, provenance links, and inert audit JSON
for the active panel.

```text
CANONICAL_SELECTION_PROPAGATION = NOT_IMPLEMENTED_BY_DESIGN
```

## 13. Active Panel URL State

The `panel` query stores one exact active panel ID. PushState/popstate,
back/forward, direct deep link, and refresh are deterministic. Unknown IDs show
a typed state and are not silently rebound.

## 14. Workspace Status UI

Complete, running, partial, failed, stale, legacy-read-only, missing-source,
and unsupported states are visibly distinct with semantic status text.

## 15. Partial Execution UI

Partial Workspace state and failed/blocked panel descriptors remain visible.
Successful independent panel metadata remains accessible; UI does not rewrite
Job, ToolCall, dependency, or execution outcomes.

## 16. Legacy / Stale / Missing UI

Legacy and stale Workspaces display read-only/source-integrity guidance.
Missing source and unsupported panels are not upgraded, rebound to latest, or
shown as successful scientific results.

## 17. Existing Surface Reuse

M2 reuses existing Workspace API/client contracts and established UI controls.
It does not introduce a second scientific mapper or the M4 renderer registry.

## 18. Findings / Evidence / Provenance

Existing interpretation, evidence, provenance, lineage, report, and recipe
panel descriptors are navigable metadata surfaces. M2 does not regenerate
findings or interpret raw Artifact content.

## 19. Report / Recipe Boundary

Report and Recipe remain references to existing authorities. No composition,
editing, publishing, or replay product behavior is added.

## 20. Scientific Integrity

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
```

No metrics, structures, trajectories, phonons, volumetric values, claims, or
units are computed in the shell.

## 21. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
M2_CORE_REQUIRES_LLM = NO
DEEPSEEK_POLICY_REGRESSION = PASS
```

Persisted Job/Workspace state is consumed without a provider call. The existing
DeepSeek-only policy and `DEEPSEEK_KEY` boundary remain unchanged.

## 22. Accessibility

Semantic landmarks/headings, named controls, visible focus, keyboard-operated
drawers/sheets, focus restoration, status announcements, and non-color-only
state are covered. Touch targets are at least 44px in mobile evidence.

## 23. Responsive / Mobile

Desktop and 390x844 layouts have zero measured horizontal overflow. Long panel
and source identities wrap; drawers and sheets do not obscure active content.

## 24. Browser Matrix

Chromium, Firefox, WebKit, and Chromium 390x844 replay pass. Deep links,
back/forward, refresh, complete/running/partial/legacy/stale/unsupported states,
1/8/32 panels, and 20 repeated switches pass with zero console/page errors,
zero external requests, and zero Artifact payload requests.

## 25. Performance

Development evidence: 1/8/32-panel metadata payloads are 3,106/11,515/40,089
bytes; one active panel remains mounted after 20 switches; maximum observed
metadata concurrency is one; no listener growth was observed. These are bounded
development acceptance measurements, not production capacity claims.

## 26. Security

```text
NO_WORKSPACE_SHELL_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_SHELL_ARTIFACT_JAVASCRIPT = PASS
NO_WORKSPACE_SHELL_ARTIFACT_HTML_EXECUTION = PASS
NO_WORKSPACE_SHELL_IFRAME_EXECUTION = PASS
NO_WORKSPACE_SHELL_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS
NO_WORKSPACE_SHELL_DYNAMIC_ARTIFACT_MODULE = PASS
NO_WORKSPACE_SHELL_CROSS_PROJECT_ACCESS = PASS
NO_WORKSPACE_SHELL_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_WORKSPACE_SHELL_STALE_IDENTITY_REBINDING = PASS
NO_WORKSPACE_SHELL_SECRET_DISCLOSURE = PASS
NO_WORKSPACE_SHELL_PRIVATE_PATH_DISCLOSURE = PASS
NO_WORKSPACE_SHELL_RECOMMENDATION_EXECUTION = PASS
NO_SECRET_PATTERN_HITS = PASS
```

HTML/script/Markdown, `javascript:`, SVG script, external URLs, prototype keys,
credential-shaped text, unknown panels, stale sources, and oversized query
inputs are inert or typed rejection.

## 27. Acceptance IDs

```text
M2_ACCEPTANCE_IDS_EXPECTED = 7
M2_ACCEPTANCE_IDS_IMPLEMENTED = 7
M2_ACCEPTANCE_IDS_MISSING = 0
M2_ACCEPTANCE_IDS_EXTRA = 0
M2_ACCEPTANCE_IDS_DUPLICATE = 0
```

- M2-A01 routing/root compatibility/direct source states: PASS.
- M2-A02 nine-group IA/one active panel/data rail/inspector: PASS.
- M2-A03 exact panel URL/back-forward/refresh: PASS.
- M2-A04 typed running/partial/failed/stale/legacy states: PASS.
- M2-A05 authorized project history/idempotent open: PASS.
- M2-A06 Chromium/Firefox/WebKit/390x844: PASS.
- M2-A07 landmarks/focus/status/no overflow: PASS.

## 28. Tests

- Focused Workspace frontend: 48 passed; Planner transition regression: 31
  passed; focused M1 backend: 24 passed.
- Local backend: 1107 passed, 1 skipped, 39 deselected, 63 warnings.
- Full frontend: 351 passed across 54 files; typecheck/build PASS.
- Corrected CI Unit: 1107 passed, 1 skipped, 39 deselected, 63 warnings.
- Corrected CI Frontend: Phase 10 closure, L4/L5/M2 browser replay, typecheck,
  and build PASS.
- Corrected CI service-backed: 38 passed, 0 skipped, 0 failed, 0 errors with
  PostgreSQL, Redis, MinIO, migration head 0007, API and idempotency checks.
- Evidence manifest, secret scan, docs/TASKS integrity, `uv lock --check`, and
  dependency listing PASS.
- Local service-backed: `UNAVAILABLE` because Docker CLI is absent.
- `npm audit = UNAVAILABLE`: configured mirror returned `404_NOT_IMPLEMENTED`;
  it is not reported clean.
- Non-blocking warnings: existing pymatgen/spglib warnings and GitHub Actions
  Node 20 deprecation notices.

## 29. Production Behavior Changes

Added only the Workspace route/shell, metadata loader, exact active-panel URL,
typed state UI, Planner transition/history, responsive shell, and inert
inspector. Planner, Intent, Eligibility, Plan, Runtime, Registry, Adapter,
scientific calculation, interpretation, Report/Recipe, and LLM behavior are
unchanged.

## 30. Files Changed

- Frontend: Workspace route, shell/model, Planner transition, scoped CSS.
- Tests/evidence: focused frontend, browser runner, service-backed API gate,
  evidence generator/checker and sanitized screenshots/manifest.
- CI: M2 browser replay and 38-test service no-skipped threshold.
- Docs/persistent/TASKS/results: M2 contracts, evidence and lifecycle records.

```text
migration = unchanged
dependencies = unchanged
lockfile = unchanged
```

## 31. Commit / CI History

- Failed implementation `8429a8da6c701dee33e6d3d71fa6c069bbd502ea`, run
  `30727814090`: Unit passed; Frontend found a 390px historical L5 overflow;
  service-backed Workspace API used the wrong schema and returned 500.
- Failed correction `42fa0db84b7315e9b5d97fc537795ae49e2b5404`, run
  `30728411811`: Unit/Frontend passed; service remained 37/38 because only the
  repository helper, not the Workspace service, was bound to the test bundle.
- Failed correction `f7d099c490379c10bfdd0efa0f3a8aac918c757a`, run
  `30728878630`: Unit/Frontend passed; service remained 37/38 because the
  isolated PostgreSQL search path could fall through to public migration state.
- Corrected implementation `d18097101cdf999b76be1f2da1cf4f3d67fb9c48`, run
  `30729180057`: Unit, Frontend, and service-backed all success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 32. Explicit Non-Scope

Not implemented: M3 canonical selection/propagation/URL selection runtime;
M4 typed Artifact Gallery and renderer integration; M5 Report/Recipe
composition; M6 save/reload/recovery product flow; M7 final Workspace closure;
Phase 10N science; new scientific algorithms; cross-Workspace/multi-Job state;
arbitrary code/shell/filesystem/notebook/external science API; RAG/memory/
multi-agent/plugin/enterprise systems; new dependency or LLM SDK.

## 33. Phase 10M Readiness

```text
Phase 10M-2:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-3:
USER_SUPPLIED_TASK_PENDING_M2_ARCHIVE
```

Phase 10M as a whole is not complete.

## 34. Queue State

```text
Phase 10M-2:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-3:
USER_SUPPLIED / PENDING

TASK_BLOCK_COUNT = 2
```

## 35. Automatic M3 Entry

```text
NO
PHASE_10M3_EXECUTABLE_TASK_CREATED_BY_M2 = NO
```

The pending M3 block was supplied by the user and has not been executed.

## 36. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-2.
After the verified archive, follow the user-controlled TASKS queue.
```

## 37. Final Repository State

- Corrected implementation SHA: `d18097101cdf999b76be1f2da1cf4f3d67fb9c48`.
- Implementation exact-SHA CI: `30729180057`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, clean, migration head 0007,
  M2 complete block retained and M3 pending.

# Phase 10M-3 Cross-Artifact Navigation + Canonical Selection Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

## 2. Baseline and Entry Gate

- Phase 10M-2 implementation `d18097101cdf999b76be1f2da1cf4f3d67fb9c48`,
  exact-SHA CI `30729180057`, success.
- Phase 10M-2 completion `89da9c9bad07d906ab508d02cdeb26a212f24ac6`,
  exact-SHA CI `30729587141`, success.
- Phase 10M-2 archive `78bdec18b416a12f8878e602a552c27091f64c06`,
  exact-SHA CI `30729804091`, success.
- Initial `HEAD == origin/master == 78bdec18...`, branch `master`, clean
  worktree, migration head `0007_phase10m1_workspace_domain`, one active M3
  task, no M4 executable task: PASS.

## 3. M0-M2 Decision Compliance

M0-M2 Workspace identity, route, source authority, metadata-only shell,
one-active-panel UX, migration, API, and persistence decisions remain intact.
M3 adds no database table, API route, scientific authority, or contract version.

## 4. WorkspaceSelectionContext Runtime

The existing `WorkspaceSelectionContext 1.0` is activated with strict kind
fields, exact source hashes/versions, max 16 secondary identities, finite and
bounded JSON, prototype-key rejection, deterministic canonical serialization,
and semantic replay suppression.

## 5. URL Selection Codec

Canonical sorted JSON is encoded as base64url with a 2,048-byte token cap.
Recursive duplicate keys, noncanonical encodings, over-depth/over-size payloads,
foreign scope, stale versions, URLs, paths, and executable fields are rejected.

## 6. Selection Store

The store is scoped to one Workspace and exact Project/Job/dataset version,
supports at most 32 subscribers, records origin and transaction identity,
suppresses semantic duplicates, and releases subscribers on cleanup.

## 7. Panel Subscription Registry

Renderer-contract declarations determine accepted/emitted kinds. Current
overview/provenance consumers accept all 13 kinds; data, artifact, findings,
and evidence panels declare bounded subsets. Only
`workspace.artifact-metadata/1.0` is a production emitter in M3.

## 8. Compatibility Resolver

Outcomes are `EXACT`, `NOT_APPLICABLE`, `STALE`, and `UNSUPPORTED`. Exact
source references, Project/Job/dataset version, Artifact checksum/contract,
and panel declarations decide compatibility; registry/UI order does not.

## 9. Selection Propagation

Origin-aware delivery prevents echo loops and cross-Workspace leakage.
Independent subscribers receive only exact compatible references; stale or
unsupported panels receive typed diagnostics and no substitute selection.

## 10. Canonical Identity Support

- Dataset sample: `SUPPORTED` when exact object/sample identities exist.
- Material object: `SUPPORTED` by exact Profile object identity.
- Structure/site/atom: `SUPPORTED` by contract; missing formal IDs are
  `UNSUPPORTED_WITH_TYPED_REASON`.
- Trajectory frame/atom: `SUPPORTED` by contract; index-only records are
  `UNSUPPORTED_WITH_TYPED_REASON`.
- Phonon q-point/branch and reciprocal point: `SUPPORTED` by contract; formal
  IDs are mandatory and array positions are not authority.
- Volumetric field: `SUPPORTED` with exact field and Artifact checksum.
- Evidence item/claim: `SUPPORTED` by strict bundle/interpretation identity;
  production payload emitters remain `NOT_APPLICABLE` in M3.
- Artifact: `SUPPORTED`; whole Artifact metadata is the current production
  emission path.

## 11. Dataset / ML / Composition Linkage

Exact dataset sample/material object contexts are accepted by data, overview,
and provenance panels. No row-order, first-column, display-label, or unit guess
can create linkage.

## 12. Structure Linkage

Structure and periodic-site contexts require stable structure/site identities.
Current Artifacts without those IDs remain typed unavailable.

## 13. Trajectory Linkage

Trajectory frame/atom contexts require stable trajectory and frame/atom IDs.
Index-only trajectory payloads are not promoted to identity.

## 14. Phonon / Reciprocal Linkage

Q-point, branch, and reciprocal contexts require exact Artifact checksum and
formal point/segment IDs. Array order is explicitly rejected.

## 15. Volumetric Linkage

Volumetric contexts require exact field ID, Artifact ID, checksum, and scope;
no coordinate/label inference or frontend scientific calculation occurs.

## 16. Findings / Evidence / Artifact Linkage

Evidence/claim contracts are validated and consumable. Findings/evidence
emitters remain empty until an M4-reviewed formal payload mapper exists.
Whole Artifact selection is produced from metadata source references only.

## 17. Lineage Navigation

Inspector and compatible-panel navigation retain Artifact, ToolCall, Job,
contract/version, checksum, and source-scope identity without reading or
copying Artifact payloads.

## 18. Inspector

The Inspector displays exact kind, IDs, scope/hash/version, origin panel,
compatibility, consumer panels, Pin/Clear/Copy commands, and inert audit JSON.

## 19. Active Panel + Selection Navigation

Selection and active panel are independent canonical URL fields. Navigation
preserves valid selection, switches only to declared consumers, and rejects
unknown panels without fallback.

## 20. Refresh / Back / Forward

Chromium/Firefox/WebKit evidence restores canonical selection on refresh,
restores it with browser Back, and applies the pinned fallback after Forward
when the URL selection is absent. No implicit server write occurs.

## 21. Stale / Unsupported / Missing

Stale tokens are rejected without substitution. API Pin rejects stale scope as
`422 SELECTION_SCOPE_MISMATCH`. Missing formal identity is `UNSUPPORTED` or
`NOT_APPLICABLE`; it is never rebound to latest, nearest, first, or matching
display text.

## 22. Historical Compatibility

M1/M2 persisted panels with empty declarations remain readable. Known formal
renderer contracts receive deterministic read-time declarations without a
migration or hidden repository write. Historical Plan/Job/Artifact semantics
remain unchanged.

## 23. Scientific Integrity

```text
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
SELECTION_ARRAY_INDEX_AUTHORITY = NONE
SELECTION_DISPLAY_LABEL_AUTHORITY = NONE
SELECTION_FUZZY_MATCHING = NONE
SELECTION_DATABASE_WRITES = 0
```

Selection maps exact identities only. It performs no metric, chemistry,
trajectory, phonon, reciprocal, volumetric, or interpretation calculation.

## 24. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
M3_SELECTION_REQUIRES_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

No provider call is required by M3. The existing policy remains: future real
calls may use DeepSeek only, with the key sourced from `DEEPSEEK_KEY`.

## 25. Accessibility

Named controls, semantic status, visible focus, keyboard operation, focus
restoration, expandable Inspector content, non-color state, and at least 44px
mobile controls pass browser evidence.

## 26. Mobile

Chromium 390x844 uses stacked selection content and an Inspector bottom sheet.
Measured body/root horizontal overflow is zero.

## 27. Browser Matrix

Chromium, Firefox, WebKit, and Chromium 390x844 pass URL restore, Artifact
selection, Back/Forward, stale rejection, explicit Pin, Clear, focus, no
overflow, zero console/page errors, and zero external/Artifact-payload requests.

## 28. Performance

Development acceptance evidence, not a production capacity claim: the complete
runner took 53,731.246 ms; desktop selection cases took 5,033.677 ms Chromium,
4,626.120 ms Firefox, and 4,575.813 ms WebKit; mobile took 1,533.428 ms. The
bounded store passed 1/8/32 subscribers with cleanup and duplicate suppression.

## 29. Security

```text
NO_SELECTION_ARBITRARY_CODE_EXECUTION = PASS
NO_SELECTION_ARTIFACT_JAVASCRIPT = PASS
NO_SELECTION_ARTIFACT_HTML_EXECUTION = PASS
NO_SELECTION_IFRAME_EXECUTION = PASS
NO_SELECTION_EXTERNAL_URL_EXECUTION = PASS
NO_SELECTION_DYNAMIC_MODULE_EXECUTION = PASS
NO_SELECTION_CROSS_WORKSPACE_LEAK = PASS
NO_SELECTION_CROSS_PROJECT_ACCESS = PASS
NO_SELECTION_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_SELECTION_STALE_IDENTITY_REBINDING = PASS
NO_SELECTION_ARRAY_INDEX_AUTHORITY = PASS
NO_SELECTION_DISPLAY_LABEL_AUTHORITY = PASS
NO_SELECTION_FUZZY_MATCH = PASS
NO_SELECTION_SECRET_DISCLOSURE = PASS
NO_SELECTION_PRIVATE_PATH_DISCLOSURE = PASS
NO_RECOMMENDATION_EXECUTION = PASS
NO_SECRET_PATTERN_HITS = PASS
```

## 30. Acceptance IDs

```text
expected = 7
implemented = 7
missing = 0
extra = 0
duplicate = 0
```

M3-A01 strict identity contract, M3-A02 exact propagation, M3-A03 forbidden
mapping, M3-A04 canonical URL, M3-A05 explicit Pin, M3-A06 Inspector, and
M3-A07 browser/mobile all pass with evidence.

## 31. Tests

- Focused frontend: 38 passed; focused M1 projection: 7 passed; focused backend
  projection/evidence after CI fixes: 10 passed.
- Full backend local: 1111 passed, 41 integration-marked skipped, 63 warnings.
- Full frontend local: 376 passed across 56 files; typecheck/build PASS.
- Corrected implementation CI Unit, lock check, evidence/closure: success.
- Corrected implementation CI Frontend typecheck, L4/L5/M2/M3 browser replay,
  and production build: success.
- Corrected implementation CI PostgreSQL/Redis/MinIO: 39 passed, 0 skipped,
  0 failed, 0 errors; migration head 0007 and no-skipped gate PASS.
- Local service-backed: `UNAVAILABLE` because Docker CLI is absent.
- `npm audit = UNAVAILABLE`: configured mirror returned `404_NOT_IMPLEMENTED`;
  it is not reported clean.

## 32. Production Behavior Changes

Added the strict frontend selection codec/store, exact compatibility and panel
subscription registry, origin-aware propagation, Inspector/URL/history state,
whole Artifact selection, explicit Pin, and read-time declarations for formal
renderer contracts. Planner, execution, science, persistence, and provider
behavior are unchanged.

## 33. Files Changed

- Frontend: selection contract/runtime/tests, Workspace shell/tests, fixture,
  responsive styles, browser/evidence generators.
- Backend/tests: deterministic panel declaration projection, historical
  compatibility, PostgreSQL/Redis/MinIO M3 service gate.
- CI/evidence/docs/persistent/TASKS/results: browser replay, zero-skip gate,
  sanitized manifest, architecture/compatibility/completion records.

```text
migration = unchanged
database schema = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
```

## 34. Commit / CI History

- Failed `41c2d23ca5f1f29fccce07d06f7aceb676a26ae5`, run `30733804796`:
  M2 browser semantic comparison included nonsemantic DOM count; M3 service
  fixture referenced a missing ToolCall.
- Failed `c3c029effdd2f77ce5aac1b60041c582bc477e54`, run `30734288153`:
  ToolCall FK fixed; source Job lacked complete 0.2 identities and correctly
  projected read-only.
- Failed `9cb8fbc76d7d4808fd764196b9b4e5af0247fb54`, run `30734708819`:
  integration reached a stale negative assertion whose expected HTTP/code pair
  did not match the production contract.
- Corrected implementation `fe5353f25e45eb10d3a78fa148727071e84d89e2`,
  run `30734974889`: Unit, Frontend, Browser, Build, Service-backed/no-skipped,
  evidence and security gates all success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 35. Explicit Non-Scope

Not implemented: M4 typed Artifact Gallery/scientific renderer integration;
M5 Report/Recipe composition; M6 full save/recovery; M7 Workspace closure;
Phase 10N science; new scientific renderer/calculation; cross-Workspace or
multi-Job selection; selection persistence beyond explicit existing Pin;
database/migration/API redesign; arbitrary code/shell/filesystem/notebook;
external scientific API; recommendation execution; new LLM SDK/dependency.

## 36. Phase 10M Readiness

```text
Phase 10M-3:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-4:
REVIEWER_GATE
```

## 37. Queue State

```text
Phase 10M-3:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-4:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 38. Automatic M4 Entry

```text
NO
PHASE_10M4_EXECUTABLE_TASK_CREATED = NO
```

## 39. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-3.
Do not create, queue, or execute Phase 10M-4.
```

## 40. Final Repository State

- Corrected implementation SHA: `fe5353f25e45eb10d3a78fa148727071e84d89e2`.
- Implementation exact-SHA CI: `30734974889`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, clean, migration head 0007,
  M3 completed block retained, task count 1, no M4 executable task.

# Phase 10M-4 Typed Artifact Gallery + Scientific Viewer Integration Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

## 2. Baseline and Entry Gate

- M3 implementation `fe5353f25e45eb10d3a78fa148727071e84d89e2`, CI
  `30734974889` success.
- M3 completion `7ec413f226c82e6c9a5c6ff04336a675fb8897a3`, CI
  `30735401732` success.
- M3 archive `86fb69238f1c69e172ad1010cd70ff2c486f2a1c`, CI
  `30735666842` success.
- Initial HEAD/origin were the M3 archive SHA on `master`; worktree was clean,
  migration head was `0007_phase10m1_workspace_domain`, task count was zero.
- M4 was admitted as the sole executable task; M5 remained reviewer-gated.

## 3. M0-M3 Decision Compliance

ScientificWorkspace 1.0, WorkspacePanel 1.0, WorkspaceSelectionContext 1.0,
M1 persistence/API, M2 shell, and M3 selection authority are unchanged. M4 is
an additive read/render integration layer only.

## 4. Artifact Contract Inventory

All 42 shared Artifact types have an exact disposition in the checked-in
registry and evidence inventory. Keys are Artifact type/version plus renderer
contract/version; filenames, titles, MIME alone, URLs, and component names are
not authority.

## 5. Renderer Classification

- `PRODUCTION_NATIVE_RENDERER`: existing Structure, Trajectory, Phonon,
  Brillouin-zone, and Volumetric application-owned viewers.
- `PRODUCTION_ADAPTED_RENDERER`: exact embedded Dataset, ML, and Composition
  product contracts plus bounded generic numeric plot/table paths.
- `CONSUMER_ONLY`: viewers without a formally stable emitted object identity.
- `METADATA_ONLY`: static/binary formats that are listed but not rendered.
- `INERT_FALLBACK`: bounded JSON/text and legacy/unsupported records.
- `UNSUPPORTED`: unknown types and version mismatches, with no guessed renderer.

## 6. Typed Renderer Registry

The finite 42-entry registry declares payload mode, heavy/WebGL ownership,
selection input/output, accessibility fallback, caps, lazy policy, bundle
members, stale/legacy behavior, and inert security classification. Duplicate
or malformed declarations fail tests.

## 7. Artifact Gallery

The Results panel now exposes a semantic metadata Gallery with contract,
version, renderer, ToolCall/step, checksum, size, status, lineage, selection,
safe open/download, partial/stale/legacy indicators, and exact provenance.
The browser sidecar covers 20 mixed typed Artifacts without truncation.

## 8. Artifact Metadata and Payload Loading

Initial Workspace loading makes zero Artifact payload requests. Payloads load
only for the active Artifact. The loader validates Workspace revision,
Project/Job/Artifact scope, type/version, size, content type, exact SHA-256,
JSON depth/finite/prototype constraints, cancellation, stale request identity,
and a cache key containing all semantic renderer inputs.

## 9. Generic Table / Plot / Text / JSON Fallbacks

Tables and plots consume backend-produced values only and retain semantic
table/text alternatives. Histogram bins, metrics, PCA, clustering, and other
science are not recomputed. Text/JSON are bounded inert text; HTML, script,
iframe, module, active SVG, and external assets never execute.

## 10. Dataset Materials Explorer

The existing Dataset Materials Explorer is integrated through exact K2
contract validation. Overview, composition, structures, properties, quality,
comparison, and sample surfaces retain Profile authority and stable
`objectId + sampleRef` identity.

## 11. Materials ML Viewers

Existing regression, uncertainty, and classification products are adapted
only for their exact formal schemas. Metrics, bins, target/model/unit identity,
high-error/high-uncertainty samples, class metrics, and conditional curves are
backend authority; the frontend does not recalculate or substitute metrics.

## 12. Composition Space Viewer

The existing Composition Space component consumes persisted coordinates,
clusters, coloring, and sample identities. It emits exact Dataset sample
selection and does not recompute PCA/KMeans or use point order as identity.

## 13. Structure Viewer

Existing canonical structure scene rendering is lazy-loaded with exact scene
identity, lattice/species/site facts, accessibility summary, context-loss
fallback/retry, and explicit Three.js disposal. No bond/coordination/validity
science was added.

## 14. Trajectory Viewer

Existing bounded trajectory frames, navigation, playback, cell/species and
numeric summaries are integrated. Panel close cancels work and stops playback;
no RDF/MSD/diffusion/unwrapping/smoothing/event analysis was added.

## 15. Phonon Viewer

Existing band, DOS, combined band-DOS, and animation contracts retain exact
q-point/branch/unit/path/imaginary-frequency semantics and dependency lineage.
No interpolation, mode inference, or calculation was added.

## 16. Brillouin Zone Viewer

Existing reciprocal lattice, Brillouin-zone, persisted labels/path, and
manifest artifacts load as one exact bundle. No cell/path regeneration,
nearest-coordinate match, or label-only identity is introduced.

## 17. Volumetric Viewer

Existing grid/field/payload/manifest/binary contracts render active-only with
exact checksum and source identity. The reproducible browser fixture derives
its exact values from checked-in canonical Phase 10J contracts. No Bader,
feature extraction, topology, or external texture/volume loading was added.

## 18. Canonical Selection Integration

- Artifact Gallery: `PRODUCTION_NATIVE_EMITTER` for exact `ARTIFACT` metadata.
- Dataset and Composition: `PRODUCTION_ADAPTED_EMITTER` for exact
  `DATASET_SAMPLE` identity.
- ML, Structure, Trajectory, Phonon, BZ, Volumetric: `CONSUMER_ONLY` or
  `NO_SELECTION_SUPPORT` where a stable emitted identity is absent.
- All delivery reuses the M3 store, URL codec, declarations, resolver, and
  Inspector. There is no second selection authority or fuzzy mapping.

## 19. Inspector / Findings / Evidence / Provenance

Gallery Evidence and Lineage actions navigate exact Artifact selection into
existing persisted interpretation/evidence/provenance reads. Browser replay
verifies Artifact -> Evidence item -> canonical selection and Artifact ->
Provenance identity without copying payloads.

## 20. Partial / Failure Isolation

Successful Artifacts remain usable when sibling steps fail or are dependency
blocked. Partial coverage and producer state remain visible. A Viewer failure
does not blank the Workspace or mutate Job/ToolCall/Artifact state.

## 21. Legacy / Unsupported Contracts

Unknown contracts, old versions, missing payloads, stale/deleted sources,
integrity mismatches, caps, and unsupported Profiles produce typed inert
states. There is no latest rebinding, filename guess, or same-name replacement.

## 22. WebGL Lifecycle

```text
MAX_ACTIVE_HEAVY_VIEWERS = 1
WEBGL_CONTEXT_GROWTH = 0
LISTENER_GROWTH = 0
OBSERVER_GROWTH = 0
DUPLICATE_CANVAS = 0
```

Chromium executes 50 heavy mount/unmount cycles plus context loss/recovery;
Firefox/WebKit execute cross-engine cycles. Peak active contexts are one and
final active contexts are zero. CI uses Xvfb for Firefox/WebKit and explicit
SwiftShader WebGL for Chromium; all three report WebGL2 preflight.

## 23. Scientific Integrity

```text
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
ARTIFACT_FILENAME_RENDERER_AUTHORITY = NONE
ARTIFACT_EXTERNAL_EXECUTION_AUTHORITY = NONE
```

## 24. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
M4_VIEWERS_REQUIRE_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

M4 renders persisted Artifacts. Existing policy remains DeepSeek-only for any
future real call with `DEEPSEEK_KEY` as the sole key source.

## 25. Accessibility

Gallery and Viewer surfaces expose semantic headings/lists/tables/status,
numeric/text alternatives, keyboard and focus-visible controls, non-color
state, context-lost text, reduced-motion behavior, and named controls.

## 26. Mobile / Responsive

Chromium 390x844 passes one-active-viewer, 44px minimum targets, Inspector
focus/return focus, stacked Gallery layout, and zero body/root overflow.

## 27. Browser Matrix

Chromium, Firefox, WebKit, and Chromium 390x844 pass. Console errors, page
errors, failed responses, and unapproved external requests are zero. Legacy
and HTML payloads remain inert.

## 28. Performance

Development/browser acceptance evidence, not a production capacity claim:
20 metadata Artifacts, zero initial payload requests, zero inactive-heavy
requests, 22/20/22 desktop content requests, one mobile request, one peak
heavy context, zero retained canvas, zero resource growth, and Chromium traced
heap delta zero. Registry/loader caps bound metadata, bundles, depth, bytes,
rows, columns, traces, and points.

## 29. Security

```text
NO_ARTIFACT_GALLERY_ARBITRARY_CODE_EXECUTION = PASS
NO_ARTIFACT_HTML_EXECUTION = PASS
NO_ARTIFACT_JAVASCRIPT_EXECUTION = PASS
NO_ARTIFACT_IFRAME_EXECUTION = PASS
NO_ARTIFACT_DYNAMIC_MODULE_EXECUTION = PASS
NO_ARTIFACT_EXTERNAL_URL_EXECUTION = PASS
NO_ARTIFACT_COMPONENT_NAME_AUTHORITY = PASS
NO_ARTIFACT_FILENAME_RENDERER_AUTHORITY = PASS
NO_CROSS_PROJECT_ARTIFACT_ACCESS = PASS
NO_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_STALE_ARTIFACT_REBINDING = PASS
NO_ARTIFACT_CHECKSUM_BYPASS = PASS
NO_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS
NO_SELECTION_ARRAY_INDEX_AUTHORITY = PASS
NO_SELECTION_DISPLAY_LABEL_AUTHORITY = PASS
NO_SELECTION_FUZZY_MATCH = PASS
NO_RECOMMENDATION_EXECUTION = PASS
NO_SECRET_PATTERN_HITS = PASS
```

## 30. Acceptance IDs

```text
expected = 8
implemented = 8
missing = 0
extra = 0
duplicate = 0
```

M4-A01 through M4-A08 pass local, browser, service-backed, and corrected
implementation exact-SHA CI evidence.

## 31. Tests

- Focused M4 frontend: 40 passed; M4 evidence: 3 passed.
- Full backend local: 1115 passed, 41 explicitly gated skips, 63 warnings.
- Full frontend local: 396 passed across 62 files; typecheck/build PASS.
- Browser: Chromium/Firefox/WebKit/mobile PASS; 50-cycle/context-loss PASS.
- Corrected exact-SHA CI `30751689618`: Unit SUCCESS, Frontend/browser/build
  SUCCESS, PostgreSQL/Redis/MinIO 39 passed and 0 skipped.
- `uv lock --check` and dependency tree PASS; no lock/dependency change.
- `npm audit = UNAVAILABLE`: configured mirror returned
  `404_NOT_IMPLEMENTED`; it is not reported clean.

## 32. Production Behavior Changes

Added the typed Gallery, exact renderer registry, metadata/payload loader,
existing scientific Viewer dispatch, exact M3 selection integration, and
heavy/WebGL lifecycle control. Workspace, Planner, Runtime, Registry execution,
Adapters, scientific values, and interpretation behavior are unchanged.

## 33. Files Changed

- Backend/API: exact Artifact content read and interpretation source refs.
- Frontend: registry, loader, Gallery, generic plot, scientific Viewer adapters,
  selection integration, heavy/WebGL lifecycle and responsive styling.
- Tests/CI: focused tests, service-backed content route, historical fixture
  compatibility, three-browser/mobile runner and Xvfb replay.
- Evidence/docs/persistent/TASKS/results: sanitized manifests and lifecycle.

```text
migration = unchanged
database schema = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
Selection contract = unchanged
```

## 34. Commit / CI History

- `197727e`, run `30748799607`: failed M2 fixture metadata route.
- `edd5d58`, run `30749134462`: failed M3 metadata-GET authority assertion.
- `75038ac`, run `30749507123`: failed gitignored volumetric fixture.
- `f370795`, run `30750190137`: failed Linux Chromium software WebGL.
- `61d20a9`, run `30750682966`: incomplete SwiftShader flag set.
- `28625a2`, run `30751255622`: Linux Firefox headless WebGL unavailable.
- Corrected implementation `6287785c26e7bfdb91664fb10e78aa3de87161f7`,
  run `30751689618`: all required jobs success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 35. Explicit Non-Scope

Not implemented: new scientific Adapter/algorithm; CrystalNN/VoronoiNN;
experimental XRD; RDF/MSD/diffusion; electronic Band/DOS/Fermi surface; Bader
or new volumetric extraction; new phonon/structure calculation; frontend
scientific recomputation; migration/database change; selection persistence;
cross-Workspace or multi-Job Workspace; M5 Report/Recipe composition;
panel-to-report selection; M6 recovery/offline/collaboration; plan/DAG editor;
recommendation execution; new LLM/provider/SDK; arbitrary Python/shell/
filesystem/notebook; external science API; RAG/memory/multi-agent/plugins/
enterprise SaaS.

## 36. Phase 10M Readiness

```text
Phase 10M-4:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-5:
REVIEWER_GATE
```

## 37. Queue State

```text
Phase 10M-4:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-5:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 38. Automatic M5 Entry

```text
NO
PHASE_10M5_EXECUTABLE_TASK_CREATED = NO
```

## 39. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-4.
Do not create, queue, or execute Phase 10M-5.
```

## 40. Final Repository State

- Corrected implementation SHA: `6287785c26e7bfdb91664fb10e78aa3de87161f7`.
- Implementation exact-SHA CI: `30751689618`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, clean, migration head 0007,
  M4 completed block retained, task count 1, no M5 executable task.

# Phase 10M-5 Scientific Report + Recipe Composition Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

## 2. Baseline and Entry Gate

- M4 implementation: `6287785c26e7bfdb91664fb10e78aa3de87161f7`, CI `30751689618` success.
- M4 completion: `ee0e913625b627e891e1627f204ebf8e14cfb7c9`, CI `30752527117` success.
- M4 archive: `7f84472d3cd0ca1e8a90eb56a69987bf4c2dadd7`, CI `30752905104` success.
- Initial HEAD/origin: M4 archive SHA; branch `master`; clean worktree; migration head 0007; task count zero before admission.

## 3. M0-M4 Decision Compliance

Workspace identity/persistence, shell, canonical selection, renderer registry,
Gallery, viewers, WebGL lifecycle, Artifact authority, and historical API
semantics remain unchanged. M5 is additive composition only.

## 4. Report / Recipe Authority Audit

Existing `reports.report_json` and `visualization_recipes.recipe_json` remain
the sole persistence authorities. Reports are selected delivery snapshots;
Recipes are exact declarative, non-executable replay manifests.

## 5. Existing Persistence Reuse

```text
new report tables = 0
new recipe tables = 0
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
```

The existing UnitOfWork transaction atomically creates the exact pair.

## 6. Composition Contracts

Implemented strict `ReportCompositionRequest 1.0`,
`ReportCompositionSnapshot 1.0`, `RecipeReplayManifest 1.0`, and
`ReportExportManifest 1.0` in Python, checked JSON Schema, and TypeScript.
Unknown/duplicate fields, non-finite values, invalid IDs/enums, excessive
depth/bytes/counts, and executable text are rejected.

## 7. Canonical Identity and Hashing

Canonical semantic hashes include exact Workspace revision, Project/Dataset/
Job/Plan, ordered selected Panels/Artifacts/Claims/Evidence, checksums,
captions, disclosures, and Recipe bindings. Runtime IDs, timestamps, browser
state, temporary URLs, and secrets are excluded.

## 8. Source Eligibility Classification

The deterministic projector emits `REPORT_FIGURE_SOURCE`,
`REPORT_TABLE_SOURCE`, `REPORT_FINDING_SOURCE`, `REPORT_EVIDENCE_SOURCE`,
`REPORT_PROVENANCE_SOURCE`, `REPORT_DISCLOSURE_ONLY`,
`REPORT_METADATA_ONLY`, or `REPORT_UNSUPPORTED` from exact contract/version,
scope, checksum, lineage, and validated interpretation membership. Filename,
title, MIME-only, array-position, fuzzy, and latest-version inference are absent.

## 9. Scientific Report Composition

Every Report deterministically renders all twelve mandatory sections: title,
goal, scope, methods/plan, execution, results, findings, warnings/limitations,
failed/blocked/missing scope, evidence/provenance, environment/references, and
exact Recipe reference. Empty sections retain typed unavailable state.

## 10. Exact Recipe Replay Manifest

Recipes preserve exact Project/Dataset/Profile/Intent/Eligibility/Decision/
Plan, tools, versions, params, bindings, expected outputs, original Artifact
IDs/checksums, outcome, provenance, warnings, and semantic hash. All execution,
Plan, Job, queue, and automatic replay flags are false.

## 11. AnalysisPlan 0.1 Support

Plan 0.1 remains `planSchemaVersion = 0.1` with no invented dependency graph
or Artifact binding. Exact ordered independent/sequential steps and params are retained.

## 12. AnalysisPlan 0.2 / Dependency Support

Plan 0.2 preserves graph hash, dependency edges, ports, producer/consumer
bindings, contract/version/checksum lineage, independent branches, and
failed/blocked descendants.

## 13. M3 Selection and M4 Gallery Integration

Gallery and eligible Panels add exact source refs to a session draft. The M3
selection authority is not replaced or persisted; unsupported Viewer
sub-selection falls back to whole Artifact, Panel, metadata, or approved numeric/text representation.

## 14. Figures / Tables / Viewer Fallbacks

Formal static/numeric/table projections are eligible. WebGL-only Structure,
Trajectory, BZ, and Volumetric states use exact metadata and approved fallback.

```text
WEBGL_CANVAS_REPORT_AUTHORITY = NONE
BROWSER_SCREENSHOT_SCIENTIFIC_AUTHORITY = NONE
```

## 15. Findings / Evidence / Interpretation

Only persisted grounded ScientificClaims and exact Evidence membership may be
selected. Numeric values, units, subjects, confidence, supporting/limiting
Evidence, and provider/deterministic provenance are unchanged.

## 16. Mandatory Warnings / Limitations / Failures

Source warnings, interpretation limitations, partial coverage, failed steps,
blocked dependencies, missing desired outputs, stale/unsupported sources, and
validation/provider failures are mandatory and cannot be removed.

## 17. Partial / All-Failed / No-Interpretation States

Partial execution produces `REPORT_READY_WITH_LIMITS`; all-failed produces
`REPORT_NO_SCIENTIFIC_RESULTS`; no-interpretation retains methods/Artifacts/
provenance with grounded findings typed unavailable. No positive claim is invented.

## 18. Stale / Missing / Legacy States

Stale identity never rebinds to latest. Missing selected results fail or must
be removed while their disclosure remains. Legacy Report/Recipe records remain
read-only with unchanged hashes and typed unavailable fields.

## 19. Preview

```text
PREVIEW_REPORT_WRITES = 0
PREVIEW_RECIPE_WRITES = 0
PREVIEW_JOB_CREATION = 0
```

Preview revalidates exact sources and deterministically returns Report, Recipe
summary, outcome, caps, and errors without persistence or execution authority.

## 20. Persistence / Atomicity / Idempotency

Finalize revalidates Workspace revision and all exact sources, then creates
the linked Report/Recipe pair in one transaction. Same idempotency key and
semantic request returns the same pair; semantic conflict is typed and creates
no row. Rollback leaves both counts unchanged.

## 21. History

History lists every immutable snapshot by exact IDs, versions, semantic hashes,
source Job, Workspace revision, outcome, limitations, exports, and legacy state.

## 22. Export

Canonical JSON and UTF-8 LF-normalized Markdown are deterministically rendered
from the persisted snapshot, with exact refs, warnings, limitations, no-execution
flags, safe server filenames, authorization, byte caps, and content hashes.

## 23. API

- `GET /workspaces/{workspaceId}/report-composition/sources`
- `POST /workspaces/{workspaceId}/report-compositions/preview`
- `POST /workspaces/{workspaceId}/report-compositions`
- `GET /workspaces/{workspaceId}/report-compositions`
- `GET /workspaces/{workspaceId}/report-compositions/{reportId}`
- `GET /workspaces/{workspaceId}/report-compositions/{reportId}/recipe`
- `GET /workspaces/{workspaceId}/report-compositions/{reportId}/exports/{format}`

All routes are additive, metadata-first, scope checked, and return typed errors.

## 24. Workspace Frontend

The existing Report Panel now provides source inventory, session draft,
bounded captions/order controls, mandatory disclosures, preview, explicit
finalize, immutable history/detail, Recipe inspection, and JSON/Markdown export.

## 25. Authorization

Every read/write validates Project -> Workspace -> Job -> Panel/Artifact/
Claim/Evidence -> Report/Recipe pair. Corrected service-backed evidence uses a
real foreign Project/Job/Artifact and receives typed rejection.

## 26. Scientific Integrity

```text
REPORT_GENERATED_SCIENTIFIC_VALUES = 0
REPORT_GENERATED_SCIENTIFIC_CLAIMS = 0
REPORT_SCIENTIFIC_RECOMPUTATION = 0
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
RECIPE_EXECUTION_AUTHORITY = NONE
RECIPE_PLAN_CREATION_AUTHORITY = NONE
RECIPE_JOB_CREATION_AUTHORITY = NONE
RECIPE_QUEUE_AUTHORITY = NONE
```

## 27. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
M5_REPORT_COMPOSITION_REQUIRES_LLM = NO
M5_RECIPE_COMPOSITION_REQUIRES_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

Existing persisted provider-produced interpretation is read-only evidence;
Report and Recipe composition providers are `NONE`.

## 28. Accessibility

Semantic headings, labels, status/warning announcements, keyboard selection
and reorder controls, focus-visible behavior, tables, figure alternatives,
reduced motion, reflow, and named export controls pass automated evidence.

## 29. Mobile / Responsive

Chromium 390x844 passes single-surface source/draft/preview/history navigation,
44px targets, focus return, warning announcements, and zero horizontal overflow.

## 30. Browser Matrix

Chromium, Firefox, WebKit, and Chromium 390x844 pass complete/partial/no-
interpretation/stale/legacy/injection/idempotency/export cases. Console errors,
page errors, failed responses, and unapproved external requests are zero.

## 31. Performance

Development acceptance evidence, not a production capacity claim: source
inventory 12.235 ms, preview 16.489 ms, finalize 22.074 ms; request 335 bytes,
JSON export 11,025 bytes, Markdown 2,097 bytes.

```text
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
REPORT_PREVIEW_WEBGL_CONTEXTS = 0
DUPLICATE_RECORD_GROWTH_ON_IDEMPOTENT_SUBMIT = 0
```

## 32. Security

```text
ARTIFACT_CONTENT_IS_INERT_DATA = PASS
NO_REPORT_ARBITRARY_CODE_EXECUTION = PASS
NO_REPORT_SHELL_OR_FILESYSTEM_AUTHORITY = PASS
NO_REPORT_PROVIDER_AUTHORITY = PASS
NO_RECIPE_EXECUTION_AUTHORITY = PASS
NO_RECIPE_PLAN_CREATION_AUTHORITY = PASS
NO_RECIPE_JOB_CREATION_AUTHORITY = PASS
NO_RECIPE_QUEUE_AUTHORITY = PASS
NO_REPORT_ARTIFACT_JAVASCRIPT = PASS
NO_REPORT_ARTIFACT_HTML_EXECUTION = PASS
NO_REPORT_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS
NO_CROSS_PROJECT_REPORT_SOURCE = PASS
NO_STALE_REPORT_SOURCE_REBINDING = PASS
NO_REPORT_SCIENTIFIC_RECOMPUTATION = PASS
NO_REPORT_GENERATED_SCIENTIFIC_CLAIMS = PASS
NO_SECRET_PATTERN_HITS = PASS
```

## 33. Acceptance IDs

```text
expected = 7
implemented = 7
missing = 0
extra = 0
duplicate = 0
```

- M5-A01: contracts/authority, contract and evidence tests.
- M5-A02: deterministic Report composer, complete/partial/no-result tests.
- M5-A03: exact Plan 0.1/0.2 Recipe, determinism tests.
- M5-A04: Workspace composition/history UI and browser evidence.
- M5-A05: no-write preview and canonical safe exports.
- M5-A06: failure/compatibility/accessibility/performance/security matrix.
- M5-A07: service-backed/browser/evidence and three-commit lifecycle.

## 34. Tests

- Focused M5 backend/evidence: 29 passed.
- Full backend local: 1144 passed, 42 service-gated skips, 63 warnings.
- Full frontend local: 402 passed across 63 files; typecheck/build passed.
- Chromium/Firefox/WebKit/mobile browser evidence passed.
- Corrected CI `30990265619`: Unit, frontend/typecheck/build/browser, service-backed, no-skipped, closure/evidence success.
- Service-backed: 40 passed, 0 skipped, 0 failed, 0 errors.
- `uv lock --check`, dependency tree, docs links, TASKS/acceptance/evidence integrity, and secret scan passed.
- `npm audit = UNAVAILABLE`: configured mirror returned `404_NOT_IMPLEMENTED`; not reported clean.

## 35. Service-Backed Evidence

PostgreSQL migration head 0007, Redis, MinIO payload/checksum, persisted
Workspace/Job/Plan/Artifact/Evidence/Interpretation, metadata inventory,
no-write preview, atomic pair, idempotency, rollback, history/export,
cross-project rejection, and zero execution-object growth passed in CI.
`LOCAL_SERVICE_BACKED = UNAVAILABLE`; CI is the zero-skipped authority.

## 36. Production Behavior Changes

Workspace Report Panel can inventory eligible sources, compose and preview a
deterministic draft, explicitly finalize an immutable Report/Recipe pair,
inspect history and exact Recipe bindings, and export canonical JSON/Markdown.
Mandatory disclosures remain; no Plan/Job/ToolCall/queue is created.

## 37. Files Changed

Backend contracts/services/repositories/API, checked schemas, TypeScript/API
client, Workspace Report UI/styles, focused/service/browser tests, CI gate,
evidence, docs, persistent status, TASKS, and this result.

```text
database schema = unchanged
migration = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
Selection contract = unchanged
renderer registry authority = unchanged
scientific Adapter authority = unchanged
```

## 38. Commit / CI History

- Initial implementation `084ebd29a462ee7232a335d728ef67d4f27b7395`, run `30989213715`: Unit and Frontend succeeded; service-backed failed because the negative fixture's stale caption caused DTO 422 before scope validation.
- Corrected implementation `f294fbd305385eb3fd129ab1f815daaca03d15fa`, run `30990265619`: all required jobs success; 40 service tests, zero skipped.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 39. Explicit Non-Scope

Not implemented: M6 recovery/responsive closure; M7 final closure; new tables/
migration; collaboration; multi-Job/cross-Workspace Report; rich-text/WYSIWYG;
mandatory PDF/DOCX/LaTeX/PPTX; remote publishing; notebook/script export;
Report-generated science; frontend recomputation; LLM writing/captions/
citations; Recipe execution/rerun; Plan/Job/ToolCall/queue/Adapter execution;
new science/Phase 10N/11/12; RAG/memory/multi-agent/plugins/enterprise;
arbitrary Python/shell/filesystem; external science API; new provider/SDK/dependency.

## 40. Phase 10M Readiness

```text
Phase 10M-5:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-6:
REVIEWER_GATE
```

## 41. Queue State

```text
Phase 10M-5:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-6:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 42. Automatic M6 Entry

```text
NO
PHASE_10M6_EXECUTABLE_TASK_CREATED = NO
```

## 43. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-5.
Do not create, queue, or execute Phase 10M-6.
```

## 44. Final Repository State

- Corrected implementation SHA: `f294fbd305385eb3fd129ab1f815daaca03d15fa`.
- Implementation exact-SHA CI: `30990265619`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, clean, migration head 0007,
  M5 completed block retained, task count one, no M6 executable task.

# Phase 10M-6 Workspace Save / Reload / Recovery / Responsive Closure Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

## 2. Baseline and Entry Gate

- M5 corrected implementation: `f294fbd305385eb3fd129ab1f815daaca03d15fa`, CI `30990265619`, success.
- M5 completion: `aaef8bf254de3569f4411a85138dfb0c8c79497f`, CI `30991190818`, success.
- M5 archive: `56bec17792fff86a99c3d280ab754a69fff6c51b`, CI `30991896855`, success.
- Initial HEAD/origin: M5 archive SHA; branch `master`; worktree clean.
- Migration head: `0007_phase10m1_workspace_domain`; initial task count: 0.
- M6 admitted as the sole executable task; M7 executable task absent.

## 3. M0-M5 Decision Compliance

All sealed Workspace, Panel, Selection, renderer, Report/Recipe, persistence,
source, security, and phase-order authorities remain unchanged.

## 4. Save/Reload/Recovery Authority Audit

Existing Workspace GET/PATCH/ETag, persisted Job/ToolCall/Artifact records,
Artifact storage, and immutable Report/Recipe history support M6 without a new
authority. Redis events are observational, not the recovery authority.

## 5. Canonical State Ownership

- Server persisted: Workspace title/revision/layout/panel order/saved fallback,
  explicit pinned selection, immutable source bindings, finalized Report/Recipe.
- URL: exact `panel` and versioned canonical selection.
- Memory: pending durable edits, camera/hover/playback/filter/dialog state and
  unfinalized Report draft.
- `LOCAL_STORAGE_CANONICAL_AUTHORITY = NONE`
- `SESSION_STORAGE_CANONICAL_AUTHORITY = NONE`
- `OFFLINE_CANONICAL_WORKSPACE_COPY = NONE`

## 6. Explicit Workspace Save

Save uses the current quoted ETag with `If-Match`, submits only sealed mutable
fields, aborts obsolete requests, suppresses duplicate submission, and applies
the server-returned revision/ETag only after success.

## 7. Dirty-State Semantics

Dirty state compares canonical durable fields only. No-op Save issues no PATCH
and creates no revision; Report draft dirty state remains independent.

```text
WORKSPACE_NOOP_SAVE_REQUESTS = 0
WORKSPACE_NOOP_SAVE_REVISION_GROWTH = 0
```

## 8. Optimistic Concurrency

Typed 412 handling preserves local edits, reports base/server revision, and
requires explicit confirmation before loading server state.

```text
WORKSPACE_CONFLICT_SILENT_OVERWRITE = 0
WORKSPACE_CONFLICT_AUTOMATIC_MERGE = 0
WORKSPACE_CONFLICT_LOCAL_EDIT_LOSS_WITHOUT_CONFIRMATION = 0
```

## 9. Revision Cap

```text
MAX_LAYOUT_REVISIONS = 128
WORKSPACE_REVISION_CAP_HISTORY_DELETION = 0
WORKSPACE_REVISION_CAP_AUTOMATIC_WORKSPACE_REPLACEMENT = 0
```

The 129th revision is rejected with typed UX while Workspace and Report reads
remain available and unsaved edits remain in memory.

## 10. Reload and Layout Restoration

Reload restores exact Workspace revision, panel membership/order, durable
title/layout, valid saved panel fallback, pinned fallback, and finalized
Report/Recipe history without loading inactive heavy payloads.

## 11. Panel Resolution Precedence

Valid explicit URL panel, then valid persisted fallback when URL is absent,
then deterministic default. An invalid explicit panel produces a typed error
and never silently falls back.

## 12. Selection Resolution Precedence

Valid explicit URL selection, then valid pinned fallback only when URL
selection is absent, otherwise none. Invalid/stale explicit selection remains
typed and is never rebound by latest, nearest, label, or index.

## 13. Deep Link

Deep links contain exact Workspace, panel, and bounded canonical selection
only. Transient state, payloads, signed URLs, paths, and secrets are excluded;
over-cap state is rejected without truncation.

## 14. Refresh / Back / Forward

Refresh and history navigation restore exact route state, reject stale async
commits, and create no PATCH, Pin, revision, Report, Recipe, Plan, Job, or queue
write. `WORKSPACE_RELOAD_HIDDEN_WRITES = 0`.

## 15. Running / Interrupted Job Recovery

Nonterminal status is revalidated through bounded persisted GET observation,
visibility recovery, cancellation, and terminal-stop behavior. Missing Redis
events fall back to PostgreSQL Job/ToolCall/dependency/Artifact authority.

```text
WORKSPACE_REFRESH_PLAN_CREATION_GROWTH = 0
WORKSPACE_REFRESH_JOB_CREATION_GROWTH = 0
WORKSPACE_REFRESH_TOOLCALL_CREATION_GROWTH = 0
WORKSPACE_REFRESH_QUEUE_MESSAGE_GROWTH = 0
WORKSPACE_RECOVERY_AUTOMATIC_RERUN = 0
```

## 16. Partial / Failed / Blocked Recovery

Successful independent panels remain readable; failed and blocked scope,
missing outputs, warnings, and limitations remain visible without invented
claims or rewritten runtime authority.

## 17. Stale / Missing / Deleted Source Recovery

Typed states cover stale Dataset/Profile/resource/checksum, missing metadata or
MinIO payload, missing interpretation, foreign scope, and unavailable source.

```text
STALE_SOURCE_LATEST_REBINDING = 0
```

## 18. Historical Compatibility

AnalysisPlan 0.1 remains `LEGACY_READ_ONLY` without invented dependencies;
Plan 0.2 preserves exact graph/bindings. Legacy Artifact and Report/Recipe
records remain read-only with typed unavailable fields and unchanged hashes.

## 19. Finalized Report / Recipe Recovery

Exact immutable history, Report detail, paired Recipe, semantic hashes,
warnings/limitations, and JSON/Markdown exports survive close/reopen and do not
resolve through a latest-record heuristic.

## 20. Session Draft Honesty

```text
REPORT_DRAFT_PERSISTENCE = SESSION_ONLY
REPORT_DRAFT_SERVER_WRITES = 0
REPORT_DRAFT_LOCALSTORAGE_WRITES = 0
REPORT_DRAFT_AUTOMATIC_FINALIZE = 0
```

Persistent disclosure and navigation/unload protection state that refresh or
close discards an unfinalized draft.

## 21. First-Time / Empty / Loading / Error UX

Workspace guidance and distinct metadata/panel/Artifact/interpretation/Report/
Save/revalidation states replace blank or generic-error presentation.

## 22. Terminology and Information Hierarchy

Goal, scope, status, results, warnings, findings/evidence, Report, and recovery
actions lead the UI; audit JSON and exact developer detail remain subordinate.

## 23. Responsive Desktop

The sealed header, side navigation, active central panel, and single Inspector
remain; M6 adds Save/recovery state without redesigning the desktop shell.

## 24. Mobile

```text
mobile viewport = 390x844
horizontal overflow = 0
minimum touch target = 44x44 CSS px
```

One active panel, context drawer, panel switcher, Inspector bottom sheet, and
single-surface Report workflow provide focus trap/return and long-text wrapping.

## 25. Accessibility

Semantic landmarks/headings, keyboard panel/Save/conflict/Report workflows,
visible focus, dialog/sheet focus containment, live status, non-color states,
text/table/WebGL alternatives, reduced motion, and reflow are covered.

## 26. Long Content / Large Artifact

Long titles, warnings, provenance, IDs, tables, audit JSON, 32 panels, 128
revisions, and near-cap metadata remain bounded, wrapped, collapsible, or
internally scrollable without hiding mandatory disclosures.

## 27. Loading / Cancellation / Cache

Cache and request identity include exact Workspace revision, panel, Artifact
checksum/contract, and source hash. Route/panel/revision/checksum/unmount changes
abort or suppress obsolete work.

```text
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
INACTIVE_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
STALE_RESPONSE_STATE_COMMITS = 0
```

## 28. WebGL Lifecycle

```text
MAX_ACTIVE_HEAVY_VIEWERS = 1
WEBGL_CONTEXT_GROWTH = 0
LISTENER_GROWTH = 0
OBSERVER_GROWTH = 0
DUPLICATE_CANVAS = 0
REPORT_PREVIEW_WEBGL_CONTEXTS = 0
```

## 29. API and Persistence

Existing Workspace POST/GET/PATCH/project list/panel/layout-history routes,
Job/Artifact/interpretation reads, and seven M5 Report composition routes are
reused unchanged.

```text
new public endpoints = 0
new tables = 0
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
```

## 30. Scientific Integrity

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE
WORKSPACE_RECOVERY_GENERATED_SCIENTIFIC_VALUES = 0
WORKSPACE_RECOVERY_GENERATED_SCIENTIFIC_CLAIMS = 0
RECOMMENDATION_EXECUTION_AUTHORITY = NONE
```

## 31. LLM / DeepSeek Compliance

```text
NEW_LLM_CALL_SITES = 0
M6_SAVE_RELOAD_RECOVERY_REQUIRES_LLM = NO
REAL_LLM_CALLS = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

The permanent real-provider policy remains DeepSeek-only with sole key source
`DEEPSEEK_KEY`; M6 made no provider request.

## 32. Security

```text
NO_WORKSPACE_RECOVERY_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_SHELL_AUTHORITY = PASS
NO_WORKSPACE_RECOVERY_FILESYSTEM_AUTHORITY = PASS
NO_WORKSPACE_RECOVERY_ARTIFACT_JAVASCRIPT = PASS
NO_WORKSPACE_RECOVERY_ARTIFACT_HTML_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_IFRAME_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_DYNAMIC_MODULE_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_EXTERNAL_URL_EXECUTION = PASS
NO_WORKSPACE_RECOVERY_CROSS_PROJECT_ACCESS = PASS
NO_WORKSPACE_RECOVERY_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_WORKSPACE_RECOVERY_STALE_IDENTITY_REBINDING = PASS
NO_WORKSPACE_RECOVERY_CHECKSUM_BYPASS = PASS
NO_WORKSPACE_RECOVERY_SECRET_DISCLOSURE = PASS
NO_WORKSPACE_RECOVERY_PRIVATE_PATH_DISCLOSURE = PASS
NO_WORKSPACE_RECOVERY_STACK_DISCLOSURE = PASS
NO_WORKSPACE_RECOVERY_AUTOMATIC_RERUN = PASS
NO_WORKSPACE_RECOVERY_PLAN_CREATION = PASS
NO_WORKSPACE_RECOVERY_JOB_CREATION = PASS
NO_WORKSPACE_RECOVERY_QUEUE_AUTHORITY = PASS
NO_LOCALSTORAGE_CANONICAL_BACKUP = PASS
NO_SECRET_PATTERN_HITS = PASS
```

## 33. Acceptance IDs

```text
expected = 8
implemented = 8
missing = 0
extra = 0
duplicate = 0
```

- M6-A01: recovery model/Shell Save tests; save/conflict/cap captures.
- M6-A02: exact snapshot/fallback tests; reload/state-ownership evidence.
- M6-A03: M3/M6 URL/history tests; deep-link/Back/Forward browser evidence.
- M6-A04: persisted recovery service test; running/partial/stale/history captures.
- M6-A05: composer/Shell tests; Report/Recipe and draft-loss evidence.
- M6-A06: typed component states; browser/accessibility evidence.
- M6-A07: focus/mobile implementation; 390x844 capture and metrics.
- M6-A08: lifecycle/security/evidence tests; exact-SHA service and CI gates.

## 34. Tests

- Focused frontend: 34 passed; full frontend: 411 passed.
- Full backend: 1148 passed, 43 skipped; focused backend: 69 passed.
- Evidence integrity: 4 passed; `uv lock --check`, diff check, docs and secret
  scan passed; typecheck and production build passed.
- Local Chromium/Firefox/WebKit/390x844 replay passed.
- Local service-backed: `UNAVAILABLE` (Docker/flag unavailable), not reported as pass.
- CI service-backed: 41 passed, 0 skipped, 0 failed, 0 errors.
- Configured npm audit mirror: `404_NOT_IMPLEMENTED`; `npm audit = UNAVAILABLE`.

## 35. Browser Matrix

Chromium 129, Firefox 130, WebKit 18 at 1440x1050 and Chromium 129 at
390x844 passed Save/conflict/reload, Report recovery, accessibility, network,
console, and overflow assertions with zero unexpected errors/external requests.

## 36. Service-Backed Evidence

Exact-SHA CI used PostgreSQL, Redis, MinIO, migration head 0007, persisted
current Plan 0.2/Job/ToolCall/Artifact/Workspace, explicit Save, typed conflict,
revision cap, missing-event terminal recovery, checksum, and no execution-object
growth. Summary: `41 passed, 0 skipped, 0 failed, 0 errors`.

## 37. Performance

Development/browser evidence, not a production capacity claim: metadata-first
load, no inactive heavy requests, no hidden/no-op writes, no stale commits, one
active heavy Viewer, and zero context/listener/observer/canvas growth.

## 38. Production Behavior Changes

Users can explicitly Save allowed durable state, see dirty/saved/conflict/cap
status, reopen deterministic state, use exact links/history, recover running,
partial, failed, blocked, stale, missing, historical and finalized Report/Recipe
views, and work on desktop/mobile with keyboard and screen-reader support.

## 39. Files Changed

Workspace shell/Report composer/recovery model/styles; tests and CI; browser,
service, evidence runners; Phase 10M docs/evidence; persistent and task records.

```text
database schema = unchanged
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
Panel contract = unchanged
Selection contract = unchanged
Report/Recipe contracts = unchanged
renderer registry authority = unchanged
scientific Adapter authority = unchanged
```

## 40. Commit / CI History

- `3bae949559c1049e0bcfd5de21d4d375e1a488aa`, CI `31017695192`: Unit/Frontend passed; service fixture lacked legacy support tables.
- `c7db3ca4a651847b49a994eb7e4ad9a21d32eca7`, CI `31018789969`: Unit/Frontend passed; fixture expected RUNNING for correct Plan 0.1 legacy projection.
- `ec2a7e572510be08a7d02c5fcd338807b39ba9e3`, CI `31019983444`: Unit/Frontend passed; service fixture actor mismatched TestClient authorization.
- Corrected implementation `65e80ba915140e29db08dc053c1d218206daaa03`, CI `31020968546`: success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 41. Explicit Non-Scope

M7/final closure, Phase 10N+, schema/migration/public API/contracts,
localStorage/sessionStorage/IndexedDB authority, durable drafts, offline,
collaboration/merge, multi-Job/cross-Workspace aggregation, latest rebinding,
rerun/execution, new science, frontend recomputation, LLM recovery, new provider,
arbitrary code/shell/filesystem, RAG/memory/multi-agent/plugins are not implemented.

## 42. Phase 10M Readiness

```text
Phase 10M-6:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-7:
REVIEWER_GATE
```

Phase 10M as a whole is not declared complete.

## 43. Queue State

```text
Phase 10M-6:
COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M-7:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 44. Automatic M7 Entry

```text
NO
PHASE_10M7_EXECUTABLE_TASK_CREATED = NO
```

## 45. Next Action

```text
Verify this completion-record exact-SHA CI, then archive only Phase 10M-6.
Do not create, queue, or execute Phase 10M-7.
```

## 46. Final Repository State

- Implementation SHA: `65e80ba915140e29db08dc053c1d218206daaa03`.
- Implementation exact-SHA CI: `31020968546`, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected post-commit: `HEAD == origin/master`, branch `master`, clean,
  migration head 0007, M6 block retained, task count one, M7 task absent.

# Phase 10M-7 Workspace Integration + Browser/API/Service Evidence Closure Result

## 1. Conclusion

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

Phase 10M-7 integration closure is complete. The M7 task remains present until
this completion-record exact-SHA CI succeeds and the separate queue-archive
commit is verified.

## 2. M6 Baseline

- Implementation: `65e80ba915140e29db08dc053c1d218206daaa03`, CI
  `31020968546`, success.
- Completion: `aec09cebb33ae9673063a22f8fc772737c9a47b4`, CI
  `31022245082`, success.
- Archive: `200212b164041e38626d6b948c7fe64c772ca6ce`, CI
  `31060008583`, success.
- Entry HEAD/origin: M6 archive SHA; branch `master`; clean worktree; migration
  head `0007_phase10m1_workspace_domain`; task count zero.

## 3. Corrected Entry Gate

```text
PHASE_10M7_ENTRY_GATE = PASS_WITH_AUTHORIZED_DOCUMENT_RECONCILIATION
PHASE_10M7_ACCEPTANCE_SOURCE = ACCEPTANCE_AND_TEST_PLAN
PHASE_10M7_QUEUE_ADMISSION = AUTHORIZED
PHASE_10M7_READINESS = READY_FOR_R0_RECONCILIATION
ACCEPTANCE_RECONCILIATION_WAS_PART_OF_M7 = YES
PREVIOUS_ACCEPTANCE_GATE_BLOCK_WAS_SUPERSEDED = YES
```

The known backlog/lock/manifest drift matched the corrected reviewer prompt.
No implementation, lifecycle, or contract gate failed at entry.

## 4. Acceptance Source Authority

`docs/phase10m/phase10m_acceptance_and_test_plan.md` was the temporary canonical
source for exact M7 IDs, titles, and responsibilities. Its registry contained
exactly eight non-conflicting definitions.

## 5. Four-Document Reconciliation

The exact registry was synchronized into the acceptance plan, implementation
backlog, execution lock, and execution manifest. A marker-bounded validator
parses only canonical registry sections and treats references elsewhere as
informational.

## 6. Exact M7 Acceptance Registry

- M7-A01 `Service-backed`: PostgreSQL + Redis + MinIO full Workspace lifecycle, 0 skipped/failed.
- M7-A02 `Scientific integrity`: Adapter -> Runtime -> Artifact -> renderer/evidence authority remains exact.
- M7-A03 `Historical compatibility`: 0.1/0.2, modern/legacy/partial/missing-source cases retained.
- M7-A04 `Full tests`: Backend/frontend/typecheck/build/lock/migration/closure all pass.
- M7-A05 `Browser`: Chromium/Firefox/WebKit/mobile/accessibility/WebGL current evidence passes.
- M7-A06 `Security`: All Workspace security markers and secret scan pass.
- M7-A07 `Evidence`: Sanitized API/DOM/network/console/screenshots/performance manifest verifies.
- M7-A08 `Lifecycle`: Implementation, completion, and verified queue archive exact-SHA CI pass.

## 7. Acceptance Integrity Semantics

```text
M7 canonical source = phase10m_acceptance_and_test_plan.md
expected IDs = 8
implemented IDs = 8
missing IDs = 0
extra IDs = 0
duplicate canonical registry entries = 0
conflicting canonical definitions = 0
canonical registry shorthand entries = 0
document-wide references = informational only
```

## 8. Pipeline Authority Map

The verified path is source registration -> DataProfile 2.0 -> AnalysisIntent
1.0 -> EligibilityResolution 1.0 -> Planner decision -> AnalysisPlan 0.1/0.2
-> PlanValidator -> Job/ToolCall/dependency execution -> Artifact/lineage ->
interpretation/claims/evidence -> ScientificWorkspace 1.0 -> typed panels,
selection, and Inspector -> Report/Recipe -> Save/reopen.

DataProfile owns data semantics; Eligibility owns capability applicability;
Plan owns declared execution; Runtime orchestrates; Adapter calculates;
Artifact persists scientific results; interpretation owns grounded narrative;
Workspace owns reference/navigation/presentation; Report is an immutable
delivery snapshot; Recipe is declarative and non-executable.

## 9. Identity Continuity

The retained verified DeepSeek phonon case preserves exact Project,
Dataset/version, Profile/hash, Intent/hash, Eligibility/hash, Decision/hash,
Plan/hash/schema, graph/bindings, Job, three ToolCalls, 21 Artifact checksums,
EvidenceBundle/hash, and Interpretation/hash through current Workspace and
Report/Recipe repositories. Filename, MIME, display label, array index, row
order, latest, nearest, and fuzzy matching provide no identity authority.

```text
retained real DeepSeek calls = 16
M7_NEW_REAL_LLM_CALLS = 0
NEW_LLM_CALL_SITES = 0
NO_PROVIDER_FALLBACK = PASS
DEEPSEEK_KEY_SECRET_DISCLOSURE = 0
```

## 10. AnalysisPlan 0.1

Historical Plan 0.1 remains readable as ordered independent/sequential work.
Workspace and Report/Recipe projection invent no dependency graph or Artifact
binding. Historical records remain read-only where modern identity is absent.

## 11. AnalysisPlan 0.2

The retained replay preserves exact graph hash, two formal bindings,
producer/consumer ports, ToolCalls, Artifact contracts/checksums, immutable
lineage, Workspace panels, and Recipe dependency representation.

## 12. Dependency Success

Topological dependency execution, producer outputs, consumer inputs,
successful Artifact lineage, panel projection, and exact Recipe graph are
covered by L3, M4-M6 regressions and the M7 retained replay.

## 13. Partial / Failed / Blocked

Regression evidence preserves successful independent branches, failed
ToolCalls, blocked descendants, missing desired outputs, and mandatory Report
disclosures. No branch is omitted or rerun.

```text
SUCCESSFUL_BRANCH_ARTIFACT_LOSS = 0
FAILED_BRANCH_OMISSION = 0
BLOCKED_DEPENDENCY_OMISSION = 0
AUTOMATIC_RERUN = 0
LEGACY_DEPENDENCY_INVENTION = 0
```

## 14. Viewer Matrix

Dataset Materials Explorer, Materials ML, Composition Space, Structure,
Trajectory, Phonon, Brillouin Zone, Volumetric, generic numeric/table,
metadata-only, inert legacy fallback, and unsupported contract/version paths
retain their M4 exact contract/version dispositions. Unknown versions do not
guess renderers. WebGL canvas and browser screenshots are not scientific
authority.

## 15. Selection / Inspector

Canonical versioned exact selection retains source Artifact hash, stable sample
or scientific object identity, origin panel, compatibility result, Inspector
identity, URL round trip, Back/Forward, and explicit Pin/Clear/Copy. Only sealed
formal mappings are exercised.

```text
SELECTION_ARRAY_INDEX_AUTHORITY = NONE
SELECTION_DISPLAY_LABEL_AUTHORITY = NONE
SELECTION_FILENAME_AUTHORITY = NONE
SELECTION_FUZZY_MATCHING = NONE
SELECTION_LATEST_REBINDING = NONE
```

## 16. Interpretation / Evidence

Grounded interpretation remains bound to exact Job, Plan, Artifacts, claims,
evidence IDs, source checksums, limitations, and failed/blocked scope. Missing
interpretation yields typed unavailable findings without an automatic LLM
call or invented conclusion.

## 17. Report / Recipe

Current Workspace sources produce deterministic no-write preview, explicit
atomic finalize, idempotent immutable history, exact paired Recipe, canonical
JSON, and UTF-8 LF Markdown. The Recipe retains Profile, Intent, Eligibility,
Plan version, tools/params/bindings/dependencies/contracts and all no-execution
flags.

```text
PREVIEW_REPORT_WRITES = 0
PREVIEW_RECIPE_WRITES = 0
REPORT_GENERATED_SCIENTIFIC_VALUES = 0
REPORT_GENERATED_SCIENTIFIC_CLAIMS = 0
REPORT_SCIENTIFIC_RECOMPUTATION = 0
RECIPE_EXECUTION_AUTHORITY = NONE
RECIPE_PLAN_CREATION_AUTHORITY = NONE
RECIPE_JOB_CREATION_AUTHORITY = NONE
RECIPE_QUEUE_AUTHORITY = NONE
```

## 18. Save / Reopen

Existing PATCH/quoted ETag/If-Match authority verifies explicit Save, revision
advance, no-op suppression, two-client conflict with local edit preservation,
confirmed server reload, close/reopen, deterministic layout and pinned fallback,
deep link, Back/Forward, and zero hidden writes.

## 19. Stale / Missing / Historical

Typed recovery covers stale Dataset/Profile/resource, checksum mismatch,
missing Artifact metadata or MinIO bytes, missing interpretation, foreign scope,
Plan 0.1, legacy contracts, and historical Report/Recipe. Unaffected panels
remain readable; no latest rebinding, replacement Artifact, or identity upgrade
occurs.

## 20. API Matrix

No route was added. Existing routes verified include:

- `POST /datasets/{dataset_id}/files`, `POST /datasets/{dataset_id}/profile`;
- `POST /planner/intents`, `POST /planner/intents/{intent_id}/clarification`;
- `POST /planner/jobs`, `GET /planner/jobs/{job_id}` and `/events`,
  `/artifacts`, `/interpretations`;
- `POST /workspaces`, `GET/PATCH /workspaces/{workspace_id}`;
- `GET /workspaces/{workspace_id}/panels` and `/layout-revisions`;
- all seven existing Workspace Report composition/history/Recipe/export routes.

Strict DTO, scope, ETag, checksum, idempotency, malformed input, duplicate key,
oversize, foreign scope, stale hash, and no-hidden-write behavior remain sealed.

## 21. PostgreSQL

Migration head 0007 and 27 expected tables were verified. Profile, Intent,
decision, Plan, Job, ToolCall, dependency, Artifact metadata, interpretation,
Workspace, panels, revisions, Report, and Recipe persistence remain current
authorities.

## 22. Redis

Queue/event availability and status observation pass. Redis is not durable
scientific authority; missing-event recovery reads persisted PostgreSQL state
and never duplicates enqueue.

## 23. MinIO

Artifact byte persistence, exact checksum retrieval, authorization, missing
object state, and tamper rejection pass without storage-key disclosure.

## 24. Browser Matrix

Chromium, Firefox, WebKit, and Chromium mobile all passed current M7 replay.
M2-M6 selection, Gallery/Viewer, Report/Recipe, Save/recovery runners passed in
the same exact-SHA CI.

```text
unexpected console errors = 0
unexpected page errors = 0
unexpected failed responses = 0
unapproved external requests = 0
```

## 25. Mobile

```text
viewport = 390x844
horizontal overflow = 0
minimum touch target = 44x44 CSS px
```

The one-active-panel model, context drawer, panel switcher, Inspector bottom
sheet, Report single-surface flow, Save, recovery, long text, and exact identity
wrapping remain intact.

## 26. Accessibility

Keyboard core flows, logical headings/landmarks, visible focus, route/panel
focus placement, drawer/dialog/sheet traps and return, live announcements,
non-color states, table/chart/WebGL alternatives, reduced motion, and 200%
reflow pass the retained M3-M6 and current browser gates.

## 27. Performance

```text
INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
INACTIVE_HEAVY_ARTIFACT_PAYLOAD_REQUESTS = 0
ADJACENT_HEAVY_PANEL_PREFETCH = 0
MAX_ACTIVE_HEAVY_VIEWERS = 1
STALE_RESPONSE_STATE_COMMITS = 0
```

These are development acceptance results, not production capacity claims.

## 28. WebGL Lifecycle

The existing 50-cycle M4 runner remains authoritative; M7 adds no WebGL owner.

```text
WEBGL_CONTEXT_GROWTH = 0
LISTENER_GROWTH = 0
OBSERVER_GROWTH = 0
ANIMATION_LOOP_GROWTH = 0
DUPLICATE_CANVAS = 0
DUPLICATE_PAYLOAD_REQUEST_GROWTH = 0
REPORT_PREVIEW_WEBGL_CONTEXTS = 0
```

## 29. Scientific Integrity

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE
WORKSPACE_GENERATED_SCIENTIFIC_VALUES = 0
WORKSPACE_GENERATED_SCIENTIFIC_CLAIMS = 0
REPORT_GENERATED_SCIENTIFIC_VALUES = 0
REPORT_GENERATED_SCIENTIFIC_CLAIMS = 0
STALE_SOURCE_LATEST_REBINDING = 0
RECOMMENDATION_EXECUTION_AUTHORITY = NONE
```

## 30. Security

```text
NO_WORKSPACE_ARBITRARY_CODE_EXECUTION = PASS
NO_WORKSPACE_SHELL_AUTHORITY = PASS
NO_WORKSPACE_FILESYSTEM_AUTHORITY = PASS
NO_ARTIFACT_JAVASCRIPT_EXECUTION = PASS
NO_ARTIFACT_HTML_EXECUTION = PASS
NO_ARTIFACT_IFRAME_EXECUTION = PASS
NO_ARTIFACT_DYNAMIC_MODULE_EXECUTION = PASS
NO_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS
NO_CROSS_PROJECT_ACCESS = PASS
NO_CROSS_WORKSPACE_ACCESS = PASS
NO_CROSS_JOB_ARTIFACT_INJECTION = PASS
NO_CROSS_PROJECT_REPORT_SOURCE = PASS
NO_STALE_IDENTITY_REBINDING = PASS
NO_CHECKSUM_BYPASS = PASS
NO_SECRET_DISCLOSURE = PASS
NO_PRIVATE_PATH_DISCLOSURE = PASS
NO_STACK_DISCLOSURE = PASS
NO_STORAGE_KEY_DISCLOSURE = PASS
NO_RECOVERY_PLAN_CREATION = PASS
NO_RECOVERY_JOB_CREATION = PASS
NO_RECOVERY_TOOLCALL_CREATION = PASS
NO_RECOVERY_QUEUE_AUTHORITY = PASS
NO_PROVIDER_FALLBACK = PASS
NO_SECRET_PATTERN_HITS = PASS
```

Artifact, Report, Recipe, URL, title, caption, warning, and provenance strings
remain inert. No localStorage/sessionStorage canonical backup is introduced.

## 31. Tests

- Focused Phase 10M backend: `78 passed`; focused final M7: `12 passed`.
- Full backend: `1156 passed`, one documented local-environment skip, 43
  integration tests deselected for the separate service gate.
- Full frontend: `411 passed`; typecheck PASS; build PASS with existing
  Plotly/glslify warnings.
- Browser: Chromium/Firefox/WebKit/390x844 PASS.
- Service-backed exact-SHA CI: `42 passed, 0 skipped, 0 failed, 0 errors`.
- Migration, no-skipped, lock, acceptance, evidence manifest, docs links,
  TASKS structure, closure integrity, and secret scan: PASS.
- Local service-backed: UNAVAILABLE because Docker was unavailable; CI is the
  service authority.
- `npm audit`: UNAVAILABLE because the configured mirror returned
  `404_NOT_IMPLEMENTED`; it is not reported clean.

## 32. Files Changed

M7 changed tests, browser/service/evidence runners, CI integrity checks,
canonical documentation, evidence, and persistent lifecycle records. Production
source changes are zero.

```text
database schema = unchanged
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
public API contracts = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
Selection contract = unchanged
Report/Recipe contracts = unchanged
AnalysisPlan contracts = unchanged
renderer registry authority = unchanged
scientific Adapter authority = unchanged
```

## 33. Production Behavior Changes

```text
Production behavior changes: NONE
```

M7 is evidence-only closure; it does not add a Workspace feature or scientific
capability.

## 34. Phase 10M Final Capability Matrix

Workspace persistence/shell, typed Gallery, Dataset Explorer, Materials ML,
Composition Space, Report, Recipe, Save, and Reload are READY. Canonical
selection, scientific Viewers, interpretation, recovery, and accessibility are
READY_WITH_EXPLICIT_LIMITS. Legacy records are LEGACY_READ_ONLY; unknown
contracts are UNSUPPORTED with inert metadata. The full table is retained in
`docs/phase10m/phase10m_final_capability_matrix.md`.

## 35. Known Limitations

One Workspace per Job; no multi-Job/cross-Workspace aggregation or selection;
no collaboration, offline-first authority, durable unfinalized Report draft,
generic workflow editor, arbitrary DAG, runtime replanning, automatic rerun,
Recipe execution, frontend/Report science generation, or identity upgrade.
Missing/tampered/stale sources remain unavailable rather than rebound.

## 36. Commit / CI History

- Implementation: `21ea4559e097cec649515b35c7f45b63f8eb8511`.
- CI `31065250027` attempt 1: cancelled after the unchanged Playwright browser
  runtime download stalled for 31 minutes; Unit and service jobs had passed.
- CI `31065250027` attempt 2: success with unchanged SHA and coverage.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: not created before completion-record CI.

## 37. Queue State

```text
Phase 10M-7:
PASS / COMPLETE / AWAITING_VERIFIED_QUEUE_ARCHIVE

Phase 10M:
COMPLETE / READY_WITH_EXPLICIT_LIMITS / AWAITING_VERIFIED_ARCHIVE

Phase 10N-0:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 1
```

## 38. Phase 10N Non-Entry

```text
NO
PHASE_10N0_EXECUTABLE_TASK_CREATED = NO
```

Phase 10N science, contracts, migration, API, dependencies, tools, automatic
execution, RAG, memory, multi-agent, and plugin work were not started.

## 39. Final Repository State

- Implementation SHA/CI: `21ea4559e097cec649515b35c7f45b63f8eb8511` /
  `31065250027` attempt 2, success.
- Completion-record SHA/CI: this commit / pending.
- Queue-archive SHA/CI: not created / pending.
- Expected after this commit: `HEAD == origin/master`, branch `master`, clean
  worktree, migration head 0007, M7 task retained as complete awaiting archive,
  task count one, Phase 10N executable task absent.

# Phase 10M-7 Queue Archive Integrity Correction Record

- Queue-archive candidate: `5fc11b0465113ce7ad31fec3fa9d7e42d8d623c8`.
- Exact-SHA CI: `31068038057`, failed in Unit only because
  `test_phase10m7_document_links_and_phase10n_gate` required one active M7 task
  after the verified archive deletion. Frontend/browser/build and
  PostgreSQL/Redis/MinIO passed.
- Root cause: lifecycle integrity test covered implementation/completion state
  but not the sealed zero-task archive state.
- Correction: accept exactly one M7 task before archive or zero tasks after
  archive; preserve balanced delimiters, reject any executable Phase 10N task,
  and require the Phase 10N-0 reviewer gate.
- Corrected queue-archive SHA/CI: this commit / pending exact-SHA CI.
# Phase 10N-0 Professional Scientific Capability Gap Audit + Scope Seal Result

## 1. Conclusion

```text
PASS / COMPLETE / REVIEWER_APPROVAL_REQUIRED
```

## 2. Baseline

- M7 implementation: `21ea4559e097cec649515b35c7f45b63f8eb8511`, CI
  `31065250027` attempt 2, success.
- M7 completion: `95d448815838848e9c8089e8653afc57ab8c740d`, CI
  `31067470666`, success.
- Failed archive candidate: `5fc11b0465113ce7ad31fec3fa9d7e42d8d623c8`,
  CI `31068038057`, Unit lifecycle assertion failed while service/browser/build passed.
- Corrected archive authority: `88e8ba86079fabb96670c497b63eec8c1cc95a7c`,
  CI `31068772689`, success.
- Entry: HEAD and origin/master `88e8ba8`, branch `master`, clean worktree,
  migration `0007_phase10m1_workspace_domain`, task count zero.

## 3. Production Behavior Changes

```text
Production Behavior Changes:
NONE
```

## 4. Current Professional Scientific Maturity

The platform has production-ready composition, Dataset Materials Explorer,
Materials ML, Composition Space, phonon and BZ foundations; structure,
trajectory, theoretical XRD, static RDF and volumetric capabilities are ready
with explicit limits. N1-N5 professional products are not yet implemented.

## 5. Current Capability Inventory

The audited inventory covers 53 Registry tools, current Adapters, Artifact
families, Profile 2.0, renderers, interpretation, Workspace and Report/Recipe.
Registry-only mappings, parsers, Viewers and fixtures are not counted as
production scientific authority.

## 6. Dependency Versions

Locked/runtime versions include pymatgen `2026.5.4`, pymatgen-core `2026.5.18`,
ASE `3.29.0`, NumPy `2.4.6`/`2.5.0` marker branches, SciPy `1.17.1`/`1.18.0`,
pandas `3.0.3`, Plotly `6.8.0`, scikit-learn `1.9.0`, spglib `2.7.0`, pymatviz
`0.18.0`, and Three.js `0.185.1`. Phonopy and seekpath are not top-level locked.

## 7. Dependency Licenses

The audit records pymatgen/Plotly MIT, ASE LGPL-2.1-or-later, pandas and
scikit-learn BSD, spglib BSD-3, and the declared mixed permissive NumPy/SciPy
metadata. No package was installed, upgraded or enabled.

## 8. Upstream Capability Audit

`UPSTREAM_ONLINE_VERIFICATION = UNAVAILABLE`. Locked files, runtime metadata,
current source/tests and official release metadata already retrieved were used.
Upstream library support is never represented as repository implementation.

## 9. Existing Registry / Adapter / Artifact Surface

Current authorities include structure summary/viewing, distance-cutoff
coordination histogram, theoretical XRD, static RDF, trajectory import/viewing,
phonon band/DOS, BZ, volumetric, Dataset/ML/Composition, interpretation and
Workspace delivery. N1-N5 Tools, Adapters and Artifact contracts remain absent.

## 10. DataProfile Readiness

Profile 2.0 provides structure, trajectory, phonon, volumetric, resource,
readiness and sample-identity facts. An additive backward-compatible Profile
2.1 proposal is assigned to future phases for stable site, experimental XRD,
trajectory validity and electronic readiness facts; no N0 contract was registered.

## 11. Workspace / Viewer Readiness

Existing metadata-first Workspace and strict renderer registry are reusable.
Future N1-N5 panels must preserve active-only heavy loading, inert fallback,
exact selection, Inspector detail, mobile presentation and static alternatives.

## 12. Interpretation / Report / Recipe Readiness

Bounded projectors remain the only LLM-visible fact surface. Reports compose
persisted facts without recomputation; Recipes retain exact declarations and
have no Plan, Job, queue or execution authority.

## 13. Identity Seal

Structure/site, periodic neighbor, trajectory atom/frame/time, experimental
peak and electronic spin/k-point/band/channel identities are source-hash bound.
Filename, MIME, display label, row/index, nearest, fuzzy and latest matching are prohibited.

## 14. Units Seal

Canonical proposals cover angstrom, degrees, dimensionless coordination/RDF,
picoseconds, angstrom squared, angstrom squared per picosecond, electronvolts,
states per electronvolt and reciprocal units. Conversion is deterministic,
server-side, provenance-recorded and never silently assumed.

## 15. Scientific Wording Seal

Claims are algorithm- and policy-qualified. Absolute chemical bonding,
experimental phase confirmation, unqualified bulk diffusion, GW correction and
platform-generated electronic structure claims are prohibited.

## 16. Reference Fixture Hierarchy

The sealed order is direct checked-in numeric fixtures, exact-version official
fixtures, controlled analytic fixtures, cross-library references, licensed
public data, then mapping-only evidence. Screenshots are not numeric authority.

## 17. Numeric Tolerance Policy

Each future capability owns quantity-specific absolute/relative, positional,
angular, peak, energy, fit and deterministic-order tolerances with units,
source, platform variance and explicit failure meaning. No pass-driven tuning is allowed.

## 18. Performance Cap Plan

Bounded proposed caps cover N1 structures/sites/neighbors, N2 centers/faces,
N3 points/peaks/bytes, N4 frames/atoms/bins/windows/fits and N5 bands/k-points/
DOS/projections. Future phases must measure small, medium and near-cap fixtures.

## 19. Security Boundary

All inputs remain inert and bounded with UTF-8, depth/size, finite-number,
duplicate/prototype-key, decompression and timeout controls. No Python, shell,
filesystem, notebook, script, external scientific API, HTML/JS/module/URL,
cross-project binding, checksum bypass, secret/path/stack or Recipe execution is authorized.

## 20. N1 Coordination Scope

CrystalNN/VoronoiNN proposals bind exact pymatgen versions, explicit parameters,
periodic-image neighbors, weights, coverage and diagnostics. The scientific term
is `algorithm-derived local coordination`; the distance-cutoff histogram coexists.

## 21. N2 Local Environment / Polyhedra Scope

N2 consumes exact N1 Artifacts through Plan 0.2 and proposes versioned reference
geometry, class/score, vertices/faces and distortion metrics. Bond valence and
oxidation-state inference remain out of scope.

## 22. N3 Experimental XRD Scope

N3 separates experimental ingestion from existing theoretical XRD and seals
normalization, optional preprocessing, SciPy peak detection, deterministic
one-to-one matching and mismatch disclosure. Rietveld, refinement, phase search
and confirmation claims are excluded.

## 23. N4 Trajectory Analytics Scope

N4 seals whole/window/species RDF, server-side unwrapped MSD, directional MSD
and diagnostics-bounded diffusion fitting. Stable atom identity, explicit time,
cell policy and no silent ballistic/transient fitting are mandatory.

## 24. N5 Electronic Band / DOS Scope

N5 only consumes bounded supplied electronic output. It seals energy/Fermi,
spin, k-path, band, total DOS and completeness-qualified element/orbital DOS
projection semantics. Projected bands, Fermi surface and electronic calculation remain future scope.

## 25. N6 Integration / Evidence Scope

N6 is integration/evidence only across Profile, Intent, Eligibility, Plan,
Runtime, Artifact, interpretation, Workspace and Report/Recipe for N1-N5. It is
not a catch-all feature phase.

## 26. Long-List Classification

Fermi surface, Bader/charge topology, Rietveld and phase-fraction refinement,
automatic DFT, defects/surfaces and advanced research capabilities remain
`FUTURE_SCOPE` or outside N1-N6. No Future Scope item was promoted.

## 27. Migration Decisions

N1-N6 propose no database table, column or migration. Migration head remains
`0007_phase10m1_workspace_domain`.

## 28. Public API Decisions

N1-N6 reuse existing Registry/Plan/Job/Artifact/Workspace APIs. New public API
families are `NO` for every phase.

## 29. Contract / DataProfile Decisions

Future versioned Registry/Artifact and additive Profile 2.1 contracts are
`YES_PROPOSED_FOR_REVIEW` with phase ownership and backward compatibility. N0
registered no runtime contract.

## 30. Dependency Decisions

Current locked pymatgen/NumPy/SciPy/pandas/Plotly are sufficient for the sealed
proposals. New dependency and lockfile changes are `NO` for N1-N6.

## 31. Implementation Sequence

The reviewer sequence is sealed unchanged: N1 coordination, N2 local
environment/polyhedra, N3 experimental XRD, N4 trajectory analytics, N5
electronic Band/DOS, N6 integration/evidence.

## 32. Decision Registry

N-D001 through N-D033 are contiguous. All required decisions are:

```text
SEALED_FOR_REVIEWER_APPROVAL
```

## 33. Acceptance IDs

```text
expected = 12
implemented = 12
missing = 0
extra = 0
duplicate registry entries = 0
conflicting definitions = 0
canonical registry shorthand entries = 0
```

The exact registry is:

1. `N0-A01 BASELINE_AND_REPOSITORY_FACT_AUDIT`
2. `N0-A02 DEPENDENCY_VERSION_LICENSE_AND_UPSTREAM_CAPABILITY_AUDIT`
3. `N0-A03 CURRENT_PROFESSIONAL_SCIENTIFIC_CAPABILITY_INVENTORY`
4. `N0-A04 IDENTITY_UNITS_AUTHORITY_AND_SCIENTIFIC_WORDING_SEAL`
5. `N0-A05 N1_COORDINATION_SCOPE_SEAL`
6. `N0-A06 N2_LOCAL_ENVIRONMENT_AND_POLYHEDRA_SCOPE_SEAL`
7. `N0-A07 N3_EXPERIMENTAL_XRD_COMPARISON_SCOPE_SEAL`
8. `N0-A08 N4_TRAJECTORY_ANALYTICS_SCOPE_SEAL`
9. `N0-A09 N5_ELECTRONIC_BAND_AND_DOS_SCOPE_SEAL`
10. `N0-A10 CROSS_CUTTING_CONTRACT_REFERENCE_TOLERANCE_PERFORMANCE_AND_SECURITY_SEAL`
11. `N0-A11 N1_TO_N6_IMPLEMENTATION_SEQUENCE_ACCEPTANCE_AND_EXECUTION_LOCK`
12. `N0-A12 AUDIT_EVIDENCE_DOCUMENTATION_EXACT_SHA_LIFECYCLE_AND_REVIEWER_GATE`

These titles are identical in the backlog, acceptance plan, execution lock and manifest.

## 34. Tests

- Focused N0 integrity: `6 passed`.
- Local backend: `1162 passed, 44 skipped, 0 failed`; service/environment skips
  are not represented as service PASS.
- Exact-SHA Unit: `1162 passed, 1 documented local-environment skip, 43 deselected`.
- Frontend: `411 passed`; typecheck and production build PASS.
- Browser replay: Chromium, Firefox, WebKit and Chromium 390x844 PASS.
- Exact-SHA service-backed: `42 passed, 0 skipped, 0 failed, 0 errors`.
- Migration, no-skipped, lock, evidence, acceptance, decision, docs, TASKS and
  secret gates: PASS.
- Local service-backed: UNAVAILABLE because Docker is absent; CI is authority.
- `npm audit`: UNAVAILABLE because configured mirror returned `404_NOT_IMPLEMENTED`.

## 35. Evidence

The N0 evidence directory contains 41 LF-normalized hashed entries covering
baseline, lifecycle, dependencies/licenses, inventories, identity/units/wording,
fixtures/tolerances/caps/security, N1-N6 scopes and integrity summaries. Missing,
duplicate, secret, Authorization, private-path and stack entries are zero.

## 36. Files Changed

```text
production source = unchanged
database schema = unchanged
migration = unchanged
migration head = 0007_phase10m1_workspace_domain
public API = unchanged
runtime contracts = unchanged
dependencies = unchanged
lockfile = unchanged
TASKS.md = unchanged
```

## 37. Commit / CI

- Failed audit attempts: none. A pre-commit EOF whitespace check blocked commit
  creation and was corrected before any SHA existed.
- Audit/planning: `8f12bdc13720aae9b022301fbe8b0624245b131d`.
- Audit/planning exact-SHA CI: `31074886038`, success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.

## 38. Explicit Non-Scope

N1-N6 production tools, Adapters, parsers, Artifacts, Profile implementation,
Viewers, projectors and Report behavior were not implemented. No new science,
DB/API/dependency/LLM/execution authority was added.

## 39. Phase 10N Readiness

```text
Phase 10N-0:
COMPLETE / REVIEWER_APPROVAL_REQUIRED

Phase 10N-1:
REVIEWER_GATE
```

## 40. Queue State

```text
TASK_BLOCK_COUNT = 0

Phase 10N-1:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

## 41. Automatic N1 Entry

```text
NO
PHASE_10N1_EXECUTABLE_TASK_CREATED = NO
```

## 42. Final Repository State

- Audit/planning SHA/CI: `8f12bdc13720aae9b022301fbe8b0624245b131d` /
  `31074886038`, success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Expected after this commit: HEAD equals origin/master, branch `master`, clean
  worktree, migration head 0007, task count zero, N1 task absent.

## 43. Next Action

Return the complete Phase 10N-0 audit and scope seal to the reviewer. Do not
create, queue, or execute Phase 10N-1.

# Phase 10N-1 CrystalNN / VoronoiNN Coordination Result

## 1. Conclusion

PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI

The implementation exact-SHA CI passed. The completion record is this commit;
queue archive remains pending its own exact-SHA CI. The failed implementation
attempts are retained in Git history.

## 2. N0 Baseline

- N0 audit: `8f12bdc13720aae9b022301fbe8b0624245b131d` / CI `31074886038` success.
- N0 completion: `10c60c21c66f7d37b26bf3cc116cd88a416eafae` / CI `31075564935` success.
- Initial N1 HEAD/origin: `10c60c21c66f7d37b26bf3cc116cd88a416eafae`.
- Branch: `master`; worktree clean at entry; migration head `0007_phase10m1_workspace_domain`.
- Registry baseline 53; task count 0; N1 task admitted only in implementation commit; N2 task absent.

## 3. N0 Approval and Authority Extraction

N-D001 through N-D033 and N1-RD001 through N1-RD009 were followed. R0 closed
the exact contracts before production execution. Scientific authority remains in
the registered backend Adapter and persisted Artifact.

## 4. N1 Acceptance Registry

The exact ten-entry registry is synchronized across the four Phase 10N authority
documents:

`N1-A01 BASELINE_AUTHORITY_ACCEPTANCE_AND_EXACT_CONTRACT_CLOSURE`

`N1-A02 DATAPROFILE_REGISTRY_PARAMETER_AND_ARTIFACT_CONTRACTS`

`N1-A03 CRYSTALNN_COORDINATION_EXECUTION`

`N1-A04 VORONOINN_COORDINATION_EXECUTION`

`N1-A05 EXACT_STRUCTURE_SITE_NEIGHBOR_PERIODIC_IMAGE_IDENTITY_AND_DETERMINISM`

`N1-A06 ELIGIBILITY_PLANNER_PLANVALIDATOR_RUNTIME_PERSISTENCE_AND_NO_FALLBACK`

`N1-A07 WORKSPACE_STRUCTURE_VIEWER_SELECTION_AND_INSPECTOR_INTEGRATION`

`N1-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_WORDING`

`N1-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE`

`N1-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N2_REVIEWER_GATE`

## 5. Acceptance Reconciliation

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate canonical
registry entries = 0; conflicting definitions = 0; canonical registry
shorthand entries = 0. References outside registry sections are informational.

## 6. N-D Decision Compliance

Exactly two tools were approved. Comparison is deterministic consumer-side
presentation and is not a Tool, Adapter, Job or scientific authority.

## 7. Production Behavior Changes

Added the approved CrystalNN and VoronoiNN coordination capabilities, Profile
2.1 readiness, exact Planner/Eligibility/Runtime/Artifact integration, and the
existing Workspace/Viewer/Selection/Report surfaces. Existing persistence,
Workspace identity, selection authority, Recipe non-execution boundary and
DeepSeek-only policy are unchanged.

## 8. Dependency and Locked-Version Compliance

No dependency or lockfile change. Both tools use pymatgen `2026.5.4` with
pymatgen-core `2026.5.18`, MIT licensed, through
`pymatgen.core.local_env.CrystalNN` and `VoronoiNN`.

## 9. Tool Registry Changes

Old count = 53; approved added count = 2; final count = 55. Added:
`structure.coordination_crystalnn@0.1.0` and
`structure.coordination_voronoinn@0.1.0`. No comparison Tool was added.

## 10. DataProfile Integration

DataProfile 2.1 is additive and keeps 2.0 readable. It records periodicity,
lattice status, site count, occupancy/disorder status, exact resource identity,
coordination readiness and typed reasons. Profile execution authority is none.

## 11. Eligibility Integration

Eligibility distinguishes ready periodic structures from missing lattice,
non-periodic, disorder, partial occupancy, stale and over-cap inputs without
running either algorithm or loading heavy payloads.

## 12. Planner Integration

Exact CrystalNN, exact VoronoiNN and two-step comparison requests preserve both
Tool identities and bounded resolved parameters. Unsupported or non-ready input
does not create an executable plan.

## 13. AnalysisPlan / PlanValidator

Existing Plan 0.1/0.2 is reused. Exact input refs, Tool versions, params and
output contracts are validated; invalid or cross-algorithm bindings are rejected.

## 14. Runtime / Adapter Architecture

QueueWorkerRuntime resolves the exact registered Adapter. Computation is server
side, bounded, deterministic and inert; no network, shell, arbitrary filesystem,
dynamic module or user code authority exists.

## 15. CrystalNN Implementation

CrystalNN is independently instantiated with its sealed bounded parameter schema,
per-site results, algorithm-specific weighted coordination semantics and typed
failure behavior.

## 16. VoronoiNN Implementation

VoronoiNN is independently instantiated with solid-angle weight semantics,
periodic-image relations, bounded cutoff/tolerance parameters and typed
pathological-cell handling.

## 17. Algorithm Isolation and No-Fallback

CrystalNN failure never substitutes VoronoiNN and vice versa. Comparison consumes
only successfully persisted exact Artifacts and preserves incomplete inputs.

## 18. Structure / Site Identity

Results retain project, dataset, job, tool call, source resource/hash and exact
structure hash. Site identities are structure-hash bound; no label, filename,
latest or fuzzy rebinding is used.

## 19. Periodic Neighbor Identity

Each relation retains central/neighbor site IDs, exact integer periodic image,
distance in Angstrom, algorithm-specific weight and algorithm-qualified identity.

## 20. Parameter Contracts

CrystalNN and VoronoiNN schemas use `additionalProperties: false`, bounded finite
values, strict booleans/integers, deterministic defaults, canonical serialization
and persisted SHA-256 parameter hashes.

## 21. Units

Distance is canonicalized to Angstrom. Periodic images are exact dimensionless
integer triplets. Weight and coordination values retain algorithm-specific
semantics and are not conflated.

## 22. Artifact Contracts

Separate `phase10n1.crystalnn_coordination.v1` and
`phase10n1.voronoinn_coordination.v1` payloads retain source identity, resolved
parameters, provenance, coverage, diagnostics, warnings, checksums and bounded
derived data without copying the full structure payload.

## 23. Determinism

Canonical site/neighbor ordering, exact image identity, stable parameter hashes,
canonical JSON and checksum stability are covered by focused tests and generated
reference evidence.

## 24. Coverage and Partial Results

Artifacts report total, eligible, successful, failed, unsupported and zero-
neighbor sites, retained rows, ratio and typed reasons. Partial results are not
represented as complete.

## 25. Scientific Wording

Allowed wording is `algorithm-derived coordination`, `CrystalNN-derived
coordination` and `VoronoiNN-derived coordination`. Definitive bonding, absolute
chemical truth, experimental confirmation and a universally correct algorithm
are prohibited.

## 26. Reference Fixtures

Checked deterministic pymatgen fixtures cover both algorithms, periodic images,
disorder rejection, disagreement and bounded payload generation. Numeric fixture
evidence is separate from screenshots.

## 27. Numeric Tolerances

Periodic images and identities require exact equality. Distances and weights use
quantity-specific documented finite tolerances; no global fuzzy matching or
silent deletion is used.

## 28. Workspace Integration

The typed coordination renderer is lazy and metadata-first. Workspace stores
references and presentation state only; comparison is a deterministic view over
two exact algorithm Artifacts.

## 29. Structure Viewer Overlay

The coordination surface provides table and inert text fallbacks. It renders only
persisted site/neighbor relations and never recomputes geometry in the browser.

## 30. Selection and Inspector

Site selection is exact, structure-hash bound and URL-compatible. Inspector data
includes algorithm/version, site/neighbors, image, distance/unit, weight semantics,
resolved parameters, coverage, warnings, provenance and checksum.

## 31. Grounded Interpretation

The projector exposes bounded algorithm, coverage, ranges, warnings and limits;
LLM interpretation cannot recompute neighbors, invent bonds or resolve algorithm
disagreement.

## 32. Report / Recipe

Report uses persisted summary/table/provenance and mandatory limitations. Recipe
retains Tool/version, params, hashes and source identity while remaining
declarative, non-executable and without Plan/Job/queue authority.

## 33. Historical Compatibility

Existing 2.0 profiles, plans, Artifacts, Workspaces, selection URLs and reports
remain readable. N1 does not reprocess historical records or rebind latest data.

## 34. API Evidence

Existing Profile, Planner/Job, Artifact, Workspace and Report/Recipe routes are
reused. New public API family count = 0.

## 35. PostgreSQL / Redis / MinIO

Exact-SHA CI run `31147539225`: PostgreSQL/Redis/MinIO = 43 passed, 0 skipped,
0 failed, 0 errors; migration head `0007_phase10m1_workspace_domain`.

## 36. Browser Matrix

Exact-SHA CI run `31147539225` passed Chromium, Firefox, WebKit and the N1
coordination replay. Historical M3 replay also passed after the fixture-only
responsive correction.

## 37. Mobile

Chromium mobile viewport = `390x844`; one active panel, zero horizontal overflow,
minimum touch target = 44x44 CSS px, Inspector/table fallback retained.

## 38. Accessibility

Named algorithm controls, semantic status, keyboard site selection, visible focus,
non-color differentiation, table/text alternatives, reduced motion and mobile
targets are covered by component and browser evidence.

## 39. Performance Caps

Caps are enforced at 32 structures, 5000 sites, 1000 neighbors/site, 50000
retained rows, 16 MiB Artifact bytes and 120 seconds. Initial and inactive heavy
payload requests remain zero.

## 40. Viewer Lifecycle

Coordination is a light/table renderer and uses zero WebGL contexts. Existing M4
50-cycle lifecycle gate remains green; no duplicate canvas/listener/observer or
payload growth was introduced.

## 41. Security

`NO_COORDINATION_ARBITRARY_CODE_EXECUTION=PASS`, `NO_COORDINATION_SHELL_AUTHORITY=PASS`,
`NO_COORDINATION_FILESYSTEM_AUTHORITY=PASS`, `NO_COORDINATION_EXTERNAL_NETWORK=PASS`,
`NO_COORDINATION_DYNAMIC_MODULE=PASS`, artifact HTML/JavaScript/iframe/external URL
execution = PASS, cross-project/cross-job/foreign binding = PASS, stale rebinding
= 0, checksum bypass = 0, secret/private-path/stack/storage-key disclosure = 0,
algorithm fallback/substitution = 0, secret scan = PASS.

## 42. LLM / DeepSeek Compliance

`NEW_LLM_CALL_SITES = 0`; `N1_COORDINATION_REQUIRES_LLM = NO`;
`N1_REAL_LLM_CALLS = 0`; `DEEPSEEK_POLICY_REGRESSION = PASS`.

## 43. Acceptance Results

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate registry
entries = 0; conflicting definitions = 0; canonical registry shorthand entries = 0.

## 44. Tests

Local: backend `1177 passed, 45 skipped` (local environment skips only), frontend
`414 passed`, focused N1 `54 passed`, focused Workspace frontend `38 passed`,
typecheck/build/lock/diff checks passed. CI: Unit, Frontend/Typecheck/Build,
browser matrix and service-backed no-skipped gates passed. `npm audit` is
UNAVAILABLE because the configured mirror returns `404_NOT_IMPLEMENTED`.

## 45. Evidence

Evidence directory: `docs/phase10n/evidence/phase10n1_crystalnn_voronoinn_coordination/`.
Manifest, browser captures, reference results, API/service summaries, security,
accessibility, lifecycle and acceptance checks passed with no secret-bearing data.

## 46. Files Changed

Production implementation changed only within approved N1 behavior. Database
schema = unchanged; migration = unchanged; migration head = 0007; public API
family = unchanged; dependencies/lockfile = unchanged; Workspace and Selection
authority = unchanged; Report/Recipe execution authority = unchanged.

## 47. Commit / CI History

- Failed implementation `81eed119121bceb98f725bab8c5a659f4022e00c` / CI `31137374140`:
  M3 exact semantic replay drift and isolated actor fixture failure.
- Failed corrected implementation `7f3efab3357f171884afad2082347d1007741392` / CI
  `31147007026`: M3 was fixed; service Artifact version exceeded the legacy 32-char
  persistence field.
- Corrected implementation `08b5eec39bed4fcc93d0a4ef36eb385ba0e9ecc4` / CI
  `31147539225`: success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue archive SHA/CI: pending; no archive claim is made here.

## 48. Explicit Non-Scope

N2 local environments/polyhedra, N3 experimental XRD, N4 trajectory analytics,
N5 electronic Band/DOS and N6 integration closure are not implemented. No new
science, migration, API family, dependency, Plan architecture, arbitrary code,
Recipe execution or Phase 10N-2 task was created.

## 49. Phase 10N Readiness

Phase 10N-1: PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI.

Phase 10N-2: REVIEWER_GATE / AWAITING REVIEWER PROMPT.

## 50. Queue State

During completion-record CI: `TASK_BLOCK_COUNT = 1`; the N1 task remains active.
N2 remains a reviewer gate and has no executable task.

## 51. Automatic N2 Entry

NO. `PHASE_10N2_EXECUTABLE_TASK_CREATED = NO`.

## 52. Final Repository State

At completion-record creation: HEAD = `08b5eec39bed4fcc93d0a4ef36eb385ba0e9ecc4`,
origin/master equals HEAD, branch `master`, worktree clean, migration head
`0007_phase10m1_workspace_domain`, Registry count 55, task count 1, N2 task absent.

Return the complete N1 result after completion-record and queue-archive exact-SHA
CI; do not create, queue or execute Phase 10N-2.

# Phase 10N-2 Local Environment + Coordination Polyhedra Result

## 1. Conclusion

PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI.

## 2. N1 Baseline

N1 implementation `08b5eec39bed4fcc93d0a4ef36eb385ba0e9ecc4` / CI
`31147539225`, completion `3c937c4ecf98358e44687538396facc827ec3a4b` /
CI `31148371587`, and verified archive
`a9319c2da44f8794ef7a66347d8f7a0dffe4aa5b` / CI `31156152013` are successful
ancestors. Entry was clean master at the archive SHA, migration head 0007,
Registry 55 and zero tasks.

## 3. Entry Gate

`PHASE_10N2_ENTRY_GATE=PASS`; N1 authority and reviewer approval were verified,
N2/N3 production and executable tasks were absent, and R0/queue admission were
authorized.

## 4. N2-R0 Contract Closure

R0 froze the single Tool, strict params, catalog, Artifact, identities, metrics,
errors, fixtures, tolerances, caps and no-recomputation boundary with zero
implementation-critical TBDs.

## 5. Acceptance Registry

The four canonical documents define the same ten entries: `N2-A01` baseline/R0;
`N2-A02` N1 dependency; `N2-A03` classification; `N2-A04` polyhedra/metrics;
`N2-A05` identity/determinism; `N2-A06` planning/runtime/persistence; `N2-A07`
Workspace/Viewer/selection; `N2-A08` interpretation/Report; `N2-A09` evidence;
and `N2-A10` lifecycle/N3 gate.

## 6. N-D Decision Compliance

Existing scientific authority, identity, unit, persistence, Plan 0.2, Workspace,
Report/Recipe, security and phase-order decisions remain intact.

## 7. Production Behavior Changes

The platform now computes geometry-derived local environments and coordination
polyhedra from exact persisted N1 results and presents them through existing
planning, Runtime, Artifact, Workspace and delivery authorities.

## 8. Registry Change 55 To 56

Exactly `structure.local_environment_polyhedra@0.1.0` was added. Final Registry
count = 56; comparison Tool and additional scientific Tool count = 0.

## 9. N1 Dependency Authority

N2 binds N1 Artifact ID/checksum, contract, producer Tool/version, algorithm,
structure hash and parameter hash. CrystalNN-derived and VoronoiNN-derived N2
results remain independently attributable.

## 10. No N1 Recomputation

`N2_RECOMPUTED_N1_NEIGHBORS=0`; `N2_INDEPENDENT_NEIGHBOR_SEARCH=0`;
`N2_COORDINATION_ALGORITHM_FALLBACK=0`. N2 consumes and never rewrites N1 rows.

## 11. Algorithm And Version

Classification uses `mdi.angular_spectrum_reference_match@1.0.0`; deterministic
face construction uses locked `scipy.spatial.ConvexHull@1.17.1`. Both operate
server-side over bounded exact N1 neighbor geometry.

## 12. Geometry Reference Catalog

The versioned allowlist contains validated bounded references only; custom code,
coordinates, modules and unverified geometry identifiers are rejected.

## 13. Parameter Contracts

Python, JSON Schema and TypeScript contracts reject extra properties and
non-finite/unbounded values, resolve canonical defaults and persist parameter
hashes.

## 14. Local Environment Classification

Per-site results retain reference candidates, scores, status, source algorithm,
coverage and warnings. Tie handling exposes alternatives or ambiguity rather
than selecting by iteration order.

## 15. Polyhedron Construction

Vertices retain exact N1 neighbor-relation and periodic-image identity. Backend
faces are canonicalized from deterministic bounded hull output; the browser does
not create scientific face authority.

## 16. Distortion Metrics

Approved radial spread, bond-length distortion, angular deviation and bounded
polyhedron volume/area metrics retain explicit definitions and units. No
stability, bond-strength or chemistry score is emitted.

## 17. Structure, Site And Neighbor Identity

Project, Job, structure/resource hashes, structure-bound site identities and
algorithm-qualified N1 neighbor identities are exact. Filename, display label,
latest, row position and fuzzy geometry are never authority.

## 18. Polyhedron Identity

Polyhedron identity binds the N2 Artifact, source N1 checksum, central site,
canonical neighbor-relation set, periodic images, contract and parameter hash.

## 19. Determinism

Site, neighbor, vertex, face, candidate and warning orders are canonical; stable
parameter/content hashes are regression-tested without browser-order dependence.

## 20. Ambiguity

Near-equal candidates preserve scores and alternatives under the sealed tie
tolerance. Numeric minima are not represented as chemical truth.

## 21. Degenerate And Partial Behavior

Insufficient, coplanar, duplicate and degenerate vertices produce typed component
states. Classification or metrics may remain available only where the contract
explicitly permits partial output; no face or label is invented.

## 22. Scientific Wording

UI and delivery use `geometry-derived local environment` and `coordination
polyhedron constructed from the persisted neighbor set`. Definitive bonding,
hybridization, oxidation state, stability and experimental confirmation are
prohibited.

## 23. Profile And Eligibility

DataProfile remains 2.1. Eligibility combines periodic-structure readiness with
exact N1 availability or producibility, contract/checksum compatibility, identity
and caps; Profile contains no N2 computed result.

## 24. Planner

Exact CrystalNN or VoronoiNN requests preserve the requested producer. Ambiguous
algorithm requests require clarification; no latest/first/preferred result is
selected.

## 25. Plan 0.2 Dependency

N1 producer output binds the N2 consumer through existing bounded AnalysisPlan
0.2 ports. An exact persisted N1 Artifact can be reused without rerunning N1.

## 26. PlanValidator

Validation rejects wrong Tool/contract/checksum/structure/project/job bindings,
unbounded params and unsupported dependency outputs without plan repair.

## 27. Runtime

QueueWorkerRuntime resolves the registered Adapter, verifies immutable inputs,
enforces caps and persists inert output. Failed N1 descendants are BLOCKED and
independent successful branches are retained without fallback.

## 28. Artifact Contracts

`phase10n2.local_environment_polyhedra.v1` stores bounded N2-derived site,
classification, vertex, face, metric, coverage and diagnostic data plus exact
lineage; it copies neither full structure nor full N1 payload.

## 29. PostgreSQL

Exact-SHA CI `31258820229` verified Job/ToolCall/Artifact/Workspace/Report state
through PostgreSQL with current migration head.

## 30. Redis

The same CI verified queue/events and dependency state without recovery-created
plans, jobs or ToolCalls.

## 31. MinIO

The same CI verified N1/N2 payload persistence, checksums and exact retrieval.
Service summary: 44 passed, 0 skipped, 0 failed, 0 errors.

## 32. Workspace

The metadata-first local-environment panel provides environment and metric tables,
source provenance, deterministic source comparison and an inert polyhedron SVG
projection without copying scientific payload into Workspace state.

## 33. Structure Viewer

Persisted central sites, vertices, faces and N1 relations are shown distinctly.
No frontend neighbor, face, classification or distortion computation exists.

## 34. Selection

Exact Artifact, environment, polyhedron, vertex and face selections bind project,
job, checksum, structure, site and source N1 identity. Legacy Selection 1.0 URL
tokens remain canonical and Back/Forward restoration passes.

## 35. Inspector

Inspector surfaces N2 and N1 Tool/algorithm versions, checksums, structure/site,
reference scores/status, neighbor images, faces, metrics, units, params, coverage,
warnings, limitations and provenance.

## 36. Interpretation

The deterministic projector exposes bounded distributions, coverage, metrics,
warnings and selected-site facts. LLM authority excludes classification, hulls,
metrics, chemistry and algorithm choice.

## 37. Algorithm-Source Comparison

Consumer-side tables preserve side-by-side CrystalNN/VoronoiNN-derived results,
including disagreement and incomplete inputs. They do not average, merge, rank or
create a new scientific authority.

## 38. Report And Recipe

Report composes persisted figures/tables, lineage, warnings and limits without
recomputation. Recipe records exact N1/N2 dependency bindings and remains
declarative, non-executable and without Plan/Job/queue authority.

## 39. Historical Compatibility

Historical N1 Artifacts, Workspaces, reports and pre-N2 selection URLs remain
readable. Missing N2 is NOT_AVAILABLE and never triggers backfill or read-time
computation.

## 40. References

Direct controlled tetrahedral, octahedral, lower-coordination, distorted,
ambiguous, periodic, degenerate, algorithm-source and near-cap fixtures are stored
with source/version/license/hash provenance.

## 41. Tolerances

Identity, periodic image, reference version and checksum use exact equality.
Coordinates, distances, angles, scores, distortion, volume, area and ties use
quantity-specific documented tolerances; no global fuzzy match exists.

## 42. Performance

Small, medium, near-cap and over-cap cases cover evaluated sites, neighbors,
candidates, vertices, faces, time, memory and bytes. Explicit caps prevent
unbounded permutations and output growth.

## 43. Viewer Lifecycle

Fifty view/source/site switch cycles produced zero WebGL, listener, observer,
animation-loop, canvas, payload-request or stale-overlay growth.

## 44. Accessibility

Keyboard site/environment navigation, named controls, visible focus, non-color
states, text/table alternatives, 44px mobile targets, 200% reflow and reduced
motion are covered; WebGL is not required to read scientific values.

## 45. Security

No arbitrary code, shell, filesystem, notebook, external network or dynamic
module authority exists. Artifact HTML/JS/iframe/URL execution, cross-project/job
binding, stale/fuzzy rebinding, checksum bypass, oxidation inference, bond valence,
definitive-bond claims and secret/path/stack/storage-key disclosure all remain
prohibited and tested.

## 46. LLM And DeepSeek

`NEW_LLM_CALL_SITES=0`; `N2_REQUIRES_LLM=NO`; `N2_REAL_LLM_CALLS=0`;
`DEEPSEEK_POLICY_REGRESSION=PASS`.

## 47. Tests

Local backend: 1196 passed, 1 documented environment skip, 45 integration
deselected; frontend: 424 passed before the compatibility regression test and 23
selection tests after it; focused N2 backend 25 passed and focused N2 frontend 32
passed. Typecheck, build, lock, migration, evidence and diff checks passed.

## 48. Browser Matrix

CI `31258820229` passed Chromium, Firefox, WebKit and Chromium 390x844 N2 replay,
plus prior Workspace replays. Console/page errors, unexpected failed responses,
unapproved external requests and mobile overflow = 0.

## 49. Evidence

`docs/phase10n/evidence/phase10n2_local_environment_coordination_polyhedra/`
contains authority, contracts, fixtures, Runtime, Workspace, browser, lifecycle,
accessibility, security and manifest evidence with 57 normalized entries and zero
secret-bearing content.

## 50. Files Changed

Production changes are limited to approved N2 contracts, one Registry entry,
Adapter/planning/runtime integrations and typed Workspace presentation. Database
schema = unchanged; migration = unchanged; migration head =
`0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies =
unchanged; lockfile = unchanged; DataProfile remains 2.1.

## 51. Commit And CI History

- Initial implementation `6cb7a534faab5a63f1aa197dc9c202e62d8983aa` / CI
  `31253016285`: failed M3 additive selection compatibility and service fixture.
- Corrected implementation `2b4dacf400400f5d1a68352d358346b4638d6cb9` / CI
  `31258820229`: success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: pending; no archive success is claimed here.

## 52. Explicit Non-Scope

N3 XRD, N4 trajectory analytics, N5 electronic products, additional neighbor or
environment algorithms, oxidation state, bond valence, DFT, generic workflows,
automatic rerun, arbitrary execution and external scientific APIs are absent.

## 53. Acceptance Results

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate registry
entries = 0; conflicting definitions = 0; canonical registry shorthand entries
= 0.

## 54. Queue State

During completion-record CI, `TASK_BLOCK_COUNT=1`; the N2 task remains active.
Phase 10N-3 is reviewer-gated and has no executable task.

## 55. Automatic N3 Entry

NO. `PHASE_10N3_EXECUTABLE_TASK_CREATED=NO`.

## 56. Final Repository State

At completion-record creation, implementation authority is
`2b4dacf400400f5d1a68352d358346b4638d6cb9` / CI `31258820229`, branch master,
HEAD equals origin/master, migration head 0007, Registry 56, task count 1 and N3
task absent. Completion and archive SHAs remain pending their exact-SHA gates.

Return the complete N2 result only after completion-record and queue-archive
exact-SHA CI. Do not create, queue or execute Phase 10N-3.

# Phase 10N-3 Experimental XRD Comparison + Peak Matching Result

## 1. Conclusion

`PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.

## 2. N2 Baseline

N2 implementation `2b4dacf400400f5d1a68352d358346b4638d6cb9` / CI
`31258820229`, completion `3ffe6c5b85aca61402e4582654b0adfc0482a36b` /
CI `31260256371`, failed archive `a60c3bb89a98f35c76ea3f18c58670add96aa89b`
/ CI `31260829817`, and corrected archive
`4f5fa88354027a7b26842e9c71082fe567c84e13` / CI `31261360100` were
verified. Entry was clean master at the corrected archive, Registry 56 and task count 0.

## 3. Entry Gate

`PHASE_10N3_ENTRY_GATE=PASS`; N2 approval, ancestry, migration 0007, clean
HEAD/origin, queue, Registry and absence of N3/N4 production/tasks were verified.

## 4. N3-R0 Contract Closure

`PHASE_10N3_R0_CONTRACT_CLOSURE=PASS`; Tool, Resource, Profile, detector,
matcher, Artifact, identities, errors, references, tolerances and caps are exact,
with zero implementation-critical TBDs.

## 5. Acceptance Registry

N3-A01 through N3-A10 use the exact reviewer titles and definitions in all four
canonical documents.

## 6. N-D Decision Compliance

The existing authority chain, additive versioning, inert Artifact, exact binding,
server-side science, declarative Recipe and reviewer-gated phase order are preserved.

## 7. Production Behavior Changes

Added the approved experimental XRD resource/readiness, comparison Tool/Adapter,
Plan 0.2 integration, persisted result, Workspace surfaces and bounded delivery projections.

## 8. Registry 56 To 57

Exactly `structure.experimental_xrd_comparison@0.1.0` was added; final count is 57.

## 9. Theoretical XRD Authority

N3 consumes `structure.xrd@0.1.0` output contract `phase10e4.xrd_pattern.v1`.
`N3_THEORETICAL_XRD_REIMPLEMENTATION=0`.

## 10. Experimental XRD Resource Contract

`phase10n3.experimental_xrd_resource.v1` strictly binds versioned resource ID,
hash, degree-2theta axis, intensity semantics, angstrom wavelength and bounded points.

## 11. Units

Canonical units are degree 2theta and angstrom; no magnitude, filename or material-based inference exists.

## 12. Wavelength Semantics

Wavelength is explicit, finite, positive and bounded; mismatches are rejected without reprojection.

## 13. DataProfile Decision

DataProfile 2.2 is an additive, backward-compatible semantic extension. It stores
readiness facts only; Profile 2.1 remains readable and no bulk backfill occurs.

## 14. Eligibility

Eligibility distinguishes missing/ambiguous experimental semantics, producible or
persisted theory, wavelength mismatch, cap violations and platform availability.

## 15. Planner

Deterministic intents bind exact experimental and theoretical sources, tolerance
and detector parameters; multiple eligible sources require clarification.

## 16. AnalysisPlan 0.2

Existing theoretical Artifacts bind directly, or `structure.xrd` produces an exact
dependency consumed by N3. No generic DAG change was introduced.

## 17. PlanValidator

Wrong project/job/resource/Artifact/checksum/wavelength/contract/version and
unbounded parameters are rejected without automatic repair.

## 18. Experimental Data Validation

Strict validation covers finite equal-length monotonic arrays, explicit units,
minimum/maximum point counts, ranges, zero-only intensity and oversized input.

## 19. Normalization

The bounded allowlist is explicit and deterministic; source intensity semantics
remain distinct from normalized display values.

## 20. Peak Detection Algorithm

`mdi.experimental_xrd_peak_detection@1.0.0` uses locked SciPy 1.17.1
`scipy.signal.find_peaks` server-side.

## 21. Peak Detection Params

Strict bounded prominence, relative-height, separation and count fields reject
unknown, non-finite and out-of-range values; resolved defaults and hash persist.

## 22. Match-Independence Of Detection

Detection runs before and independently of theoretical matching.
`N3_MATCH_OPTIMIZED_PEAK_DETECTION=0`.

## 23. Theoretical Peak Contract

Exact persisted peak IDs, degree positions, relative intensities, hkl and
multiplicity are consumed with Tool/Artifact/wavelength/structure lineage.

## 24. hkl Semantics

N3 preserves theoretical hkl metadata and never recomputes indexing or labels an
experimental peak as definitively indexed.

## 25. Peak Matching Algorithm

`mdi.xrd_ordered_position_match@1.0.0` performs bounded deterministic one-to-one
position matching under an explicit degree-2theta tolerance.

## 26. One-To-One Constraint

Each experimental and theoretical peak participates in at most one pair.

## 27. Tie Handling

Canonical cost and identity ordering resolves exact ties deterministically without input-order authority.

## 28. Experimental Peak Identity

Identity binds resource hash, detector version/hash, canonical ordinal and exact detected position.

## 29. Theoretical Peak Identity

Identity binds theoretical Artifact checksum, producer, structure and formal peak ID.

## 30. Match Identity

Identity binds both exact peak identities, matcher version/hash, tolerance and N3 Artifact lineage.

## 31. Matched Peaks

Each pair retains both positions/intensities, theoretical hkl, signed and absolute delta 2theta.

## 32. Unmatched Experimental Peaks

All unmatched detected experimental peaks remain persisted and visible.

## 33. Unmatched Theoretical Peaks

All unmatched theoretical peaks remain persisted and visible.

## 34. Delta 2theta Residuals

Approved count/fractions, mean signed delta, MAE, RMSE, maximum and median absolute
delta are emitted only under their defined sample semantics; no refinement statistic exists.

## 35. Coverage

Point, detected, theoretical, matched, unmatched and excluded counts and fractions are explicit.

## 36. Zero-Match Behavior

Zero matches is a successful bounded comparison with explicit limitations, not a runtime failure.

## 37. Artifact Contract

`phase10n3.experimental_xrd_comparison.v1` stores exact refs plus bounded derived
series, peaks, matches, residuals, coverage, warnings and provenance without source duplication.

## 38. Determinism

Canonical point/peak/match/unmatched/warning order, serialization, hashes and checksums are tested.

## 39. Runtime

QueueWorkerRuntime resolves exact inputs, validates identity/checksum/units/caps,
runs the registered Adapter and persists inert output without network or arbitrary execution.

## 40. PostgreSQL

Exact-SHA CI `31270117864` verified job, ToolCall, dependency, Workspace and delivery persistence.

## 41. Redis

The same CI verified queue/events and blocked-descendant behavior without replanning.

## 42. MinIO

The same CI verified payload/checksum persistence and exact retrieval. Service
summary: 45 passed, 0 skipped, 0 failed, 0 errors.

## 43. Workspace

The metadata-first N3 panel exposes overlay, matched/unmatched tables, residuals,
warnings and provenance without browser scientific recomputation.

## 44. Overlay Plot

Experimental series, theoretical sticks, detected/matched/unmatched markers use
shape/text as well as color, with accessible table alternatives.

## 45. Selection

Exact experimental peak, theoretical peak and match selections bind project, job,
Artifact checksum, resources and peak identity; row/nearest/latest rebinding is absent.

## 46. Inspector

Inspector exposes exact sources, wavelengths, algorithms, params/hashes, peaks,
hkl, delta, coverage, warnings, limits and provenance.

## 47. Grounded Interpretation

The deterministic projector emits bounded counts, fractions, residuals, selected
facts, wavelength, tolerance and warnings; the LLM performs no detection or matching.

## 48. Scientific Wording

All surfaces state peak correspondence under the declared tolerance and explicitly
exclude refinement and definitive phase identification.

## 49. Report

Report composes persisted overlay/tables/residuals/coverage/provenance and the mandatory limitation statement.

## 50. Recipe

Recipe records exact source hashes, Tool/Artifact versions, detector/matcher params
and dependency bindings while remaining declarative and non-executable.

## 51. Historical Compatibility

No N3 backfill or read-time computation occurs; historical theory, Workspace,
Report, Recipe and selection contracts remain readable.

## 52. Reference Fixtures

Controlled perfect, shifted, missing, extra, competing, boundary, zero/single,
wavelength, unit, noisy, threshold and near-cap fixtures carry provenance.

## 53. Tolerances

Detection, matching, ties, residual regression, normalization and cross-platform
floating tolerances are quantity-specific; identities and checksums are exact.

## 54. Performance

Small, medium, near-cap and over-cap evidence verifies hard bounds for points,
peaks, candidates, matches, payload, plot points and timeout.

## 55. Plot Lifecycle

Fifty source/panel/selection cycles produced zero listener, observer, animation,
chart, request or stale-response growth.

## 56. Accessibility

Keyboard tables/selections, visible focus, non-color states, accessible legend and
summary, 44px mobile targets, 200% reflow and reduced motion pass.

## 57. Security

Untrusted data caps, finite/strict parsing, exact scope/checksum binding, inert
Artifacts and no code/shell/filesystem/network authority pass the N3 matrix.

## 58. LLM And DeepSeek

`NEW_LLM_CALL_SITES=0`; `N3_REQUIRES_LLM=NO`; `N3_REAL_LLM_CALLS=0`;
`DEEPSEEK_POLICY_REGRESSION=PASS`.

## 59. Browser Matrix

CI `31270117864` passed Chromium, Firefox, WebKit and Chromium 390x844 replay,
with zero console/page errors, unexpected responses, external requests or mobile overflow.

## 60. Tests

Corrected exact-SHA CI: backend 1210 passed, one documented environment skip and
46 deselected; frontend 430 passed; service-backed 45 passed with zero skipped,
failed or errors; typecheck, build, lock, migration, evidence and browsers passed.
Local Docker service-backed execution was unavailable; CI is the service authority.
`npm audit` remained UNAVAILABLE because the configured mirror returns 404_NOT_IMPLEMENTED.

## 61. Evidence

`docs/phase10n/evidence/phase10n3_experimental_xrd_comparison_peak_matching/`
contains authority, contracts, fixtures, runtime, browser, lifecycle, accessibility,
security and LF-normalized manifest evidence with zero missing/duplicate/secret entries.

## 62. Files Changed

Production changes are limited to approved N3 contracts and integrations.
Database schema = unchanged; migration = unchanged; migration head =
`0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies =
unchanged; lockfile = unchanged.

## 63. Acceptance Results

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate registry
entries = 0; conflicting definitions = 0; canonical registry shorthand entries = 0.

## 64. Commit And CI History

- Initial implementation `1faa25582107ac3d34efea2e75b61ae3d0f9be13` / CI
  `31269467363`: failed one stale service selection-list assertion; all other jobs passed.
- Corrected implementation `5aef027d312f462eea72a1ced10b33e4f4664a50` /
  CI `31270117864`: success.
- Failed completion-record candidate `e805b8c8d41e69254da21b3209c600f8dce9aa34`
  / CI `31288217113`: one stale N2 lifecycle assertion; frontend/browser/build
  and service-backed 45/45 passed.
- Corrected completion record `c7547903faef191c97f35ca0ae2ad1ad1678193f` /
  CI `31288792343`: success.
- Queue-archive SHA/CI: this commit / pending exact-SHA CI.

## 65. Explicit Non-Scope

`N3_AUTOMATIC_PATTERN_SHIFT=0`; `N3_LATTICE_REFINEMENT=0`;
`N3_STRUCTURE_REFINEMENT=0`; `N3_RIETVELD_REFINEMENT=0`;
`N3_PHASE_FRACTION_REFINEMENT=0`; `N3_AUTOMATIC_PHASE_IDENTIFICATION=0`.
N4/N5 science, database search, external APIs and arbitrary execution are absent.

## 66. Queue State

After the queue-archive candidate, `TASK_BLOCK_COUNT=0`; the completed N3 task is
removed. Phase 10N-4 remains reviewer-gated and has no executable task.

## 67. Automatic N4 Entry

NO. `PHASE_10N4_EXECUTABLE_TASK_CREATED=NO`.

## 68. Final Repository State

At queue-archive creation, implementation authority is
`5aef027d312f462eea72a1ced10b33e4f4664a50` / CI `31270117864`, branch master,
migration head 0007, Registry 57 and task count 0. Completion authority is
`c7547903faef191c97f35ca0ae2ad1ad1678193f` / CI `31288792343`; queue-archive
exact-SHA verification is pending and N4 task is absent.

# Phase 10N-4 Trajectory RDF / MSD / Diffusion Result

## 1. Conclusion

`PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI`.

## 2. N3 Baseline

N3 implementation `5aef027d312f462eea72a1ced10b33e4f4664a50` / CI `31270117864`, completion `c7547903faef191c97f35ca0ae2ad1ad1678193f` / CI `31288792343`, and archive `0a33d84ea7c97b423f825f0c9784c57f1acfac3b` / CI `31289319532` were verified. Entry Registry was 57 and task count was zero.

## 3. Entry Gate

Master HEAD equaled origin, the worktree was clean, migration head was `0007_phase10m1_workspace_domain`, DataProfile was 2.2, and N4/N5 production/tasks were absent. `PHASE_10N4_ENTRY_GATE=PASS`.

## 4. N4-R0 Contract Closure

The three Tools, trajectory/time/cell/PBC authority, ASE/NumPy algorithms, strict params, Artifacts, identities, errors, references, tolerances and caps are exact; implementation-critical TBD count is zero.

## 5. Acceptance Registry

N4-A01 through N4-A10 are canonical and synchronized across acceptance, backlog, lock and manifest documents.

## 6. N-D Decision Compliance

The N0 scientific authority, bounded execution, exact identity, no-recomputation, wording, persistence and phase-order decisions remain intact.

## 7. Production Behavior Changes

Added approved trajectory RDF, server-unwrapped MSD, explicit-window diffusion diagnostics, additive readiness/planning, persisted Artifacts and Workspace/interpretation/Report integrations only.

## 8. Registry 57 To 60

Added exactly `trajectory.rdf@0.1.0`, `trajectory.msd@0.1.0`, and `trajectory.diffusion@0.1.0`; final Registry count is 60.

## 9. Existing Trajectory Authority Audit

Input authority is immutable `phase10g.trajectory.v1` with exact trajectory hash, stable atom order/IDs, frames, coordinates, units, cells, PBC and physical time.

## 10. Static RDF Boundary

Existing `structure.rdf` is unchanged. N4 trajectory RDF is an independent persisted authority and never averages frontend static-RDF output.

## 11. Trajectory Resource Contract

The strict resource validates bounded frames/atoms, stable atom records, explicit coordinate/wrapping semantics, cells/PBC and time metadata.

## 12. Frame Identity

Frame identity is trajectory hash plus formal frame index; playback index is not scientific authority.

## 13. Atom Identity

Atom identity is bound to the immutable trajectory and invariant atom record/order. Nearest-coordinate tracking is absent.

## 14. Species Identity

Species stability is validated across the immutable trajectory; mutation/reactive tracking is unsupported.

## 15. Time Semantics

Physical time is explicit, finite and strictly increasing, converted from fs to canonical ps where declared. MSD/diffusion reject missing or irregular production time.

## 16. Cell And PBC Semantics

Fixed/per-frame cells and exact three-axis PBC are explicit; partial PBC affects only enabled axes.

## 17. Variable-Cell Policy

RDF accepts validated per-frame cells only when every frame supports the requested safe radius. Initial MSD/diffusion reject variable cells.

## 18. Coordinate Semantics

Fractional versus Cartesian and wrapped versus unwrapped input are explicit contract fields and are never inferred from numeric range.

## 19. Unwrapping Algorithm

`mdi.fixed_cell_fractional_minimum_image@1.0.0` unwraps server-side with fixed-cell fractional continuity, triclinic mapping and partial-PBC handling.

## 20. Unwrapping Ambiguity

Post-wrap fractional steps at or above 0.49 produce `UNWRAPPING_AMBIGUOUS`; no perturbation, fallback or nearest-atom tracking occurs.

## 21. RDF Algorithm

`mdi.trajectory_rdf_ase_mic_unordered_pair_density@1.0.0` uses locked ASE 3.29.0 geometric minimum images and NumPy 2.4.6 bounded histograms.

## 22. RDF Normalization

Per-frame unordered-pair number-density and exact shell-volume normalization yields dimensionless `g(r)` with `r` in angstrom.

## 23. Species-Pair RDF

All-species, same-species and unordered cross-species pairs preserve explicit pair identity and self/double-count policy.

## 24. Window RDF

Whole, frame and physical-time windows use inclusive start/exclusive end and persist exact included frame identities and coverage.

## 25. RDF Safe Radius

Requested `rMax` must not exceed half the minimum periodic face spacing for any included frame; it is never silently clipped.

## 26. RDF Artifact

`phase10n4.trajectory_rdf.v1` persists source identity, params/hash, pair/window, exact bins, normalized values, counts, coverage, diagnostics and checksum.

## 27. MSD Estimator

`mdi.multiple_time_origin_msd@1.0.0` averages exact selected atoms and bounded time origins for each physical lag.

## 28. Total MSD

Total Cartesian MSD is persisted in angstrom squared with lag time in ps.

## 29. Species MSD

One exact species or all atoms is selected through formal trajectory species identity.

## 30. Directional MSD

Persisted x/y/z Cartesian components remain distinct and are not relabeled crystallographic a/b/c.

## 31. MSD Origin Coverage

Every lag records its origin count and coverage; low fit coverage prevents diffusion qualification.

## 32. Drift Correction Policy

Drift correction is explicitly `none`; no mass or center-of-mass authority is invented.

## 33. MSD Artifact

`phase10n4.trajectory_msd.v1` persists source, unwrapping policy/diagnostics, estimator, species, lag IDs/times, total/directional values, origins, limitations and checksum.

## 34. MSD To Diffusion Dependency

Diffusion consumes one exact persisted MSD Artifact through AnalysisPlan 0.2 binding by ID, contract, producer, checksum and trajectory lineage.

## 35. Fit Window

Start/end are explicit finite ps parameters. Missing windows require clarification; no automatic best-window selection exists.

## 36. Diffusion Regression

`mdi.explicit_window_ols_einstein@1.0.0` uses bounded NumPy OLS, `D=slope/6` for total and `D_axis=slope/2` for Cartesian directions.

## 37. Diffusive-Regime Diagnostics

Qualification requires minimum points/duration/origin coverage, positive slope, minimum R-squared, signal and a configured log-log alpha range.

## 38. Ballistic And Transient Rejection

Controlled constant-velocity MSD is `BALLISTIC_LIKE_WINDOW`; non-diffusive, poor, short or low-coverage windows retain diagnostics but no D estimate.

## 39. Diffusion Artifact

`phase10n4.trajectory_diffusion.v1` persists exact MSD lineage, fit window, fit values, diagnostics/status, qualified estimate or unavailable state, units and limitations.

## 40. Units

Distance is angstrom, time ps, MSD angstrom squared, RDF dimensionless and diffusion angstrom squared per ps.

## 41. DataProfile Decision

DataProfile 2.3 is an additive JSON-contract evolution for trajectory readiness facts. Profiles 2.2 and historical profiles remain readable; no result is profiled.

## 42. Eligibility

RDF, MSD and diffusion independently check their exact data/dependency prerequisites and caps without running scientific algorithms.

## 43. Planner

Deterministic intents cover whole/window/species RDF, total/species/directional MSD and explicit-window diffusion; ambiguous source/species/window requests do not choose latest/first.

## 44. AnalysisPlan 0.2

RDF/MSD bind trajectories directly; diffusion composes `trajectory.msd -> exact MSD Artifact -> trajectory.diffusion` or reuses an exactly compatible persisted MSD Artifact.

## 45. PlanValidator

Existing typed dependency validation rejects foreign/stale/checksum/contract/version/source/parameter mismatches and direct trajectory-to-diffusion bindings.

## 46. Runtime

Registered Adapters resolve bounded existing resources/Artifacts, compute server-side and persist through existing Runtime/Artifact authority with no network, shell, notebook or arbitrary path/code.

## 47. PostgreSQL

Exact-SHA CI `31299086998` passed N4 ToolCall/Artifact and dependency persistence through PostgreSQL.

## 48. Redis

Exact-SHA CI passed queue execution and typed dependency state through Redis.

## 49. MinIO

Exact-SHA CI passed exact MSD payload retrieval/checksum and N4 Artifact round trips through MinIO.

## 50. Workspace

The metadata-first Trajectory Analytics panel provides RDF, MSD and diffusion views with numeric tables and no frontend scientific computation.

## 51. Trajectory Viewer Integration

Exact trajectory identities link navigation and selection only; rendered positions never become displacement/RDF/MSD authority.

## 52. Selection

Six exact N4 kinds cover RDF pair/bin, MSD species/lag and diffusion window/diagnostic with Project/Workspace/Job/Artifact/checksum identity.

## 53. Inspector

Persisted algorithms, source trajectory/MSD, params/hash, units, values, origins, fit diagnostics, coverage, warnings and limitations are inspectable.

## 54. Interpretation

The deterministic projector exposes bounded persisted RDF/MSD/diffusion facts only; it performs no unwrapping, calculation, fitting or threshold selection.

## 55. Scientific Wording

Claims remain window-, estimator- and diagnostic-qualified; RDF peaks are not automatic bonds/shells and D is not an unconditional long-time bulk constant.

## 56. Report

Reports compose persisted plots/tables/diagnostics/provenance and disclose the explicit-window diffusion limitation; failed qualification emits no positive D conclusion.

## 57. Recipe

Recipes preserve exact trajectory, Tools/versions/params, unwrapping, MSD Artifact/checksum, fit window and dependency bindings and remain non-executable.

## 58. Historical Compatibility

No bulk backfill or read-time analytics occurs. Historical trajectory/Workspace/Report data remains readable and N4 is `NOT_AVAILABLE` without exact persisted N4 Artifacts.

## 59. References

Controlled lattice, boundary crossing, triclinic/partial-PBC, stationary, ballistic, random-walk, anisotropic/species, missing-time, variable-cell and fit fixtures are recorded.

## 60. Tolerances

Cell, coordinate, minimum-image, RDF, MSD, fit, R-squared, alpha and D tolerances are quantity-specific; trajectory/frame/atom/Artifact/Tool/parameter identities are exact.

## 61. Performance

Hard caps cover 200 frames, 5,000 atoms, 2,000,000 pair evaluations, 2,048 bins/lags, 4,096 origins, 10,000 fit points and 32 MiB Artifacts. Measurements are not capacity guarantees.

## 62. Viewer Lifecycle

Fifty view/species/window/selection cycles recorded zero WebGL/listener/observer/animation/canvas/chart/request/stale-response growth.

## 63. Accessibility

Complete RDF/MSD/fit tables, keyboard controls, visible focus, non-color series/status, 44px mobile controls, 200% reflow and reduced motion are covered.

## 64. Security

No arbitrary code, shell, filesystem, notebook, network or dynamic module authority exists. Scope/checksum binding, inert Artifacts, no frontend science and no automatic fit optimization pass.

## 65. LLM And DeepSeek

`NEW_LLM_CALL_SITES=0`; `N4_REQUIRES_LLM=NO`; `N4_REAL_LLM_CALLS=0`; `DEEPSEEK_POLICY_REGRESSION=PASS`.

## 66. Browser Matrix

Chromium, Firefox, WebKit and Chromium 390x844 passed locally and in CI `31299086998`, including N4 views, exact selections, lifecycle, accessibility and zero unapproved external requests.

## 67. Tests

Local backend: 1221 passed with 48 documented service/environment skips; frontend: 438 passed; typecheck/build passed. CI unit: 1220 passed, 1 documented environment skip, 47 integration deselected; service-backed: 46 passed, 0 skipped/failed/errors; all browser/build jobs passed. `npm audit=UNAVAILABLE` because the configured mirror returns `404_NOT_IMPLEMENTED`.

## 68. Evidence

`docs/phase10n/evidence/phase10n4_trajectory_rdf_msd_diffusion/` contains contracts, fixtures, persisted samples, runtime, browser, lifecycle, accessibility, security and LF-normalized hash manifest evidence.

## 69. Files Changed

Database schema = unchanged; migration = unchanged; migration head = `0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies = unchanged; lockfile = unchanged; Workspace/Selection/Report/Recipe execution authorities are unchanged.

## 70. Acceptance Results

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate registry entries = 0; conflicting definitions = 0; canonical registry shorthand entries = 0.

## 71. Commit And CI History

- Failed implementation `3ae66528a7bffa596793fe6d72ea0e600819be8b` / CI `31298574230`: unit evidence hash failed across CRLF/LF; service 46/46 and frontend/browser passed.
- Corrected implementation `2965e585f22cb50ccae87f6d1e5860b5a1b5ba92` / CI `31299086998`: success.
- Completion record `ca5208feec772e45397f4afbb80419aa6263978f` / CI `31299648506`: success.
- Queue-archive SHA/CI: this commit / pending exact-SHA CI.

## 72. Explicit Non-Scope

No N5 Band/DOS/Fermi surface, Green-Kubo/VACF, Arrhenius, automatic fit window, variable-cell MSD, reaction/hop analysis, simulation/DFT/refinement, arbitrary execution, external scientific API, generic workflow, RAG, memory, multi-agent, plugin or enterprise capability was added.

## 73. Queue State

`TASK_BLOCK_COUNT=0`; the completed N4 task is removed and N5 remains reviewer-gated.

## 74. Automatic N5 Entry

NO. `PHASE_10N5_EXECUTABLE_TASK_CREATED=NO`; Phase 10N-5 remains `REVIEWER_GATE / NOT_QUEUED / NOT_EXECUTABLE`.

## 75. Final Repository State

Implementation authority is `2965e585f22cb50ccae87f6d1e5860b5a1b5ba92` / CI `31299086998`; completion authority is `ca5208feec772e45397f4afbb80419aa6263978f` / CI `31299648506`; queue-archive exact-SHA is pending. Branch is master, Registry count is 60, migration head is 0007, task count is zero and N5 executable task is absent.

Mandatory markers: `N4_RDF_FRONTEND_RECOMPUTATION=0`; `N4_MSD_FRONTEND_RECOMPUTATION=0`; `N4_DIFFUSION_FRONTEND_FIT=0`; `N4_MSD_WRAPPED_COORDINATE_DIRECT_USE=0`; `N4_DIFFUSION_RAW_TRAJECTORY_READS=0`; `N4_DIFFUSION_MSD_RECOMPUTATION=0`; `N4_AUTOMATIC_DIFFUSION_WINDOW_OPTIMIZATION=0`; `N4_BALLISTIC_SILENT_FIT=0`; `N4_TRANSIENT_SILENT_FIT=0`; `N4_MISSING_TIME_DIFFUSION=0`; `N4_VARIABLE_CELL_MSD_SILENT_ASSUMPTION=0`; `NEW_LLM_CALL_SITES=0`; `N4_REAL_LLM_CALLS=0`.

# Phase 10N-5 Electronic Band Structure + DOS Result

## 1. Conclusion

Phase 10N-5 is `PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI`. The implementation exact-SHA CI passed and the N5 task remains until the completion and archive gates close.

## 2. N4 Baseline

Verified archive `0442bf8925715efe81becaae19f21c58407a5a54` and its implementation/completion ancestry are authoritative; failed N4 candidate `3ae66528...` remains historical only.

## 3. Entry Gate

Entry verified master HEAD/origin, clean worktree, migration 0007, Registry 60, DataProfile 2.3, zero tasks and absent N5/N6 production/task state.

## 4. N5-R0 Contract Closure

R0 froze two Tools, supplied-resource schemas, energy/Fermi/spin semantics, exact identities, algorithms, Artifacts, errors, fixtures, tolerances and caps with zero critical TBDs.

## 5. Acceptance Registry

N5-A01 through N5-A10 are canonical: expected 10, implemented 10, missing/extra/duplicate/conflicting/shorthand 0.

## 6. N-D Decision Compliance

N0 scientific authority, auditability, no-browser-science, no-arbitrary-execution and no-secret boundaries remain intact.

## 7. Production Behavior Changes

Strict supplied Band/DOS resources now flow through Profile, Eligibility, Planner, validated Runtime, persisted Artifacts, Workspace, interpretation and Report/Recipe.

## 8. Registry 60 To 62

Exactly `electronic.band_structure@0.1.0` and `electronic.dos@0.1.0` were added. Combined Band+DOS presentation has Tool count 0.

## 9. Electronic Capability Audit

Existing electronic/BZ render foundations were reusable; no prior supplied-output Band/DOS Adapter or Artifact authority was treated as production N5 science.

## 10. Supplied Electronic Resource Boundary

Only strict immutable supplied electronic output is consumed. Platform electronic calculation authority is absent.

## 11. Band Resource Contract

`phase10n5.electronic_band_resource.v1` validates source/hash, calculation, structure binding, units/reference, Fermi, spin, reciprocal coordinates, path, k-points, bands and occupations.

## 12. DOS Resource Contract

`phase10n5.electronic_dos_resource.v1` validates source/hash, calculation, structure binding, energy/DOS semantics, Fermi, spin, total channels, projections and completeness.

## 13. Calculation Identity

Identity is resource-hash and formal calculation-identity bound; filename, title, upload order and latest selection have no authority.

## 14. Structure Binding

Formal structure ID/hash is preserved when supplied and never inferred.

## 15. Energy Units

Canonical energy is eV. Unknown units are rejected and no value-magnitude inference exists.

## 16. Energy Reference

`source_absolute` and `fermi_referenced` remain distinct; backend canonicalization is explicit and frontend alignment is prohibited.

## 17. Fermi Semantics

Fermi energy must be supplied. Missing Fermi preserves eligible raw views but disables Fermi-referenced features.

## 18. Spin Semantics

Non-spin-polarized and spin-polarized channels retain exact channel identity; no silent averaging, mirroring authority or noncollinear downgrade exists.

## 19. K-Point Identity

K-point identity binds exact Artifact/resource, formal ID, reciprocal coordinate and segment/path identity.

## 20. Reciprocal Coordinates

Fractional reciprocal coordinates and backend-supplied deterministic path distance are explicit; browser path reconstruction is absent.

## 21. K-Path Segments

Ordered segment IDs, endpoints, labels and breaks are persisted; path discontinuities are never connected.

## 22. Band Identity

Each band is exact Artifact + spin channel + formal band ID; ordinal/display labels are not cross-Artifact identity.

## 23. Band Energy Contract

Finite bounded supplied energies preserve source ordering without interpolation, dropping or connectivity optimization.

## 24. Band Gap Algorithm

`mdi.supplied_sampled_band_gap@1.0.0` deterministically derives sampled-data gap facts from supplied occupations/energies under the sealed 1e-5 eV threshold.

## 25. VBM And CBM

Persisted VBM/CBM facts retain energy, k-point, band and spin identity and are source-data qualified.

## 26. Direct And Indirect Gap

Directness compares exact sampled VBM/CBM k-point identities and is unavailable when formal identity is insufficient.

## 27. Metal-Like And Nonzero-Gap Classification

Only `METAL_LIKE_UNDER_POLICY`, `NONZERO_GAP_UNDER_POLICY` or unavailable is emitted; no definitive material class is claimed.

## 28. Band Artifact

`phase10n5.electronic_band_structure.v1` persists exact lineage, canonical data, gap facts, coverage, warnings, limitations, params/hash and checksum.

## 29. DOS Energy Grid

The finite strictly increasing supplied grid is validated and preserved without scientific resampling or smoothing.

## 30. DOS Unit And Normalization

States/eV/cell and source-defined relative semantics remain distinct; unknown normalization is never relabeled.

## 31. Total DOS

Formal total DOS must be supplied. Projections are not summed to invent it.

## 32. Spin DOS

Original spin channels and values remain separate; any mirrored visual convention is display-only and labeled.

## 33. Element Projected DOS

Only formally supplied element channels are retained with exact identities and coverage.

## 34. Orbital Projected DOS

Only allowlisted source-provided orbital channels are retained; no arbitrary merging or missing-channel generation occurs.

## 35. Projection Completeness

`COMPLETE`, `PARTIAL` and `UNKNOWN` are explicit. Partial/unknown data supports only statements about provided channels.

## 36. DOS Artifact

`phase10n5.electronic_dos.v1` persists exact lineage, grids/channels/projections, completeness, coverage, warnings, limitations, params/hash and checksum.

## 37. Band And DOS Compatibility

Combined presentation requires exact project, calculation/source, structure where present, unit/reference, Fermi and spin compatibility; mismatches do not combine.

## 38. Combined Presentation

Workspace consumes one exact Band Artifact and one exact DOS Artifact without a third Tool, recomputation, auto-shift or new truth.

## 39. DataProfile Decision

DataProfile 2.4 additively records electronic readiness only. Profiles 2.0-2.3 remain readable; no backfill, result profiling or migration occurs.

## 40. Eligibility

Band and DOS eligibility checks exact readiness, units, finite arrays, path/spin/projection semantics and caps without scientific execution.

## 41. Planner

Deterministic intents bind exact supplied resources; multiple candidates require clarification and never use first/latest/highest-match selection.

## 42. AnalysisPlan

Band and DOS are independent validated branches using existing plan semantics; combined display consumes their persisted outputs.

## 43. PlanValidator

Existing validation rejects foreign/stale/checksum/version/unit/spin/path/cap/completeness conflicts without repair.

## 44. Runtime

Registered Adapters validate, derive bounded summaries and persist through existing Runtime with no DFT, network, shell, notebook, dynamic module or arbitrary filesystem execution.

## 45. PostgreSQL

Exact-SHA CI `31311023072` passed N5 ToolCall/Artifact metadata persistence through PostgreSQL.

## 46. Redis

The same CI passed queue execution and state propagation through Redis.

## 47. MinIO

The same CI passed Band/DOS payload storage, retrieval and checksum through MinIO.

## 48. Workspace

The metadata-first Electronic Structure panel exposes Band, DOS and compatible combined views with numeric alternatives.

## 49. Band Viewer

Persisted curves, path breaks, labels, Fermi, VBM/CBM and gap facts render without frontend gap/path recomputation.

## 50. DOS Viewer

Persisted total/spin/projection channels, units/reference, Fermi and completeness render without frontend DOS computation.

## 51. Selection

Exact Band/DOS Artifact, k-point, band-state, gap, DOS channel/projection and energy-point selections bind Artifact/checksum/source/spin identities.

## 52. Inspector

Source, Tool/version, Artifact/checksum, units/reference, Fermi, spin, k-point/band/projection, values, policy, coverage, warnings and limitations are inspectable.

## 53. Grounded Interpretation

The deterministic projector exposes only persisted bounded Band/DOS facts; the LLM performs no gap, completeness, alignment or spin computation.

## 54. Scientific Wording

All claims are qualified as derived from supplied data under stated policy; no true/experimental gap, definite metal class or platform-calculated electronic structure is claimed.

## 55. Report

Reports compose persisted figures/tables/provenance and disclose that the platform does not perform DFT/GW in this capability.

## 56. Recipe

Recipes preserve exact resource hashes, Tools/versions/params, units/reference, spin, completeness and Artifact bindings and remain non-executable.

## 57. Historical Compatibility

No backfill or read-time electronic analysis occurs. Incomplete legacy contracts are read-only or typed unsupported; N5 is unavailable without persisted N5 Artifacts.

## 58. References

Controlled gapped, gapless, direct, indirect, spin, path-break, missing-Fermi, total/projected/partial DOS, compatibility and near-cap fixtures are recorded.

## 59. Tolerances

Energy, Fermi, gap, VBM/CBM, reciprocal coordinate, DOS and threshold tolerances are quantity-specific; all scientific identities and hashes are exact.

## 60. Performance

Hard caps bound k-points, bands, spin channels, segments, DOS points, projection channels, output bytes, plotting points, timeout and memory; small/medium/near/over-cap evidence is recorded.

## 61. Plot Lifecycle

Fifty Band/DOS/combined/spin/projection/selection cycles record zero listener, observer, animation, duplicate-chart/request and stale-response growth.

## 62. Accessibility

Numeric table alternatives, keyboard selections, visible focus, non-color spin distinction, textual path/gap/completeness, 44px mobile controls, reflow and reduced motion are covered.

## 63. Security

Arbitrary execution, DFT/GW, Fermi surface, projected bands, frontend science, cross-scope rebinding, executable Artifact content and secret/path disclosure gates pass.

## 64. LLM And DeepSeek

`NEW_LLM_CALL_SITES=0`; `N5_REQUIRES_LLM=NO`; `N5_REAL_LLM_CALLS=0`; `DEEPSEEK_POLICY_REGRESSION=PASS`.

## 65. Browser Matrix

CI `31311023072` passed N5 Chromium, Firefox, WebKit and Chromium 390x844 replay: `PHASE10N5_CHROMIUM_FIREFOX_WEBKIT_PASS` and `PHASE10N5_CHROMIUM_390X844_PASS`.

## 66. Tests

Local backend: 1242 passed with 49 documented service/environment skips; CI unit: 1242 passed, 1 environment skip, 48 integration deselected; frontend local: 449 passed; service-backed: 47 passed, 0 skipped/failed/errors; typecheck/build/browser passed. npm audit remains unavailable because the configured mirror returns `404_NOT_IMPLEMENTED`.

## 67. Evidence

`docs/phase10n/evidence/phase10n5_electronic_band_dos/` contains R0, contracts, fixtures, samples, planner/runtime, browser, lifecycle, accessibility, security and checksum-manifest evidence.

## 68. Files Changed

Production contracts/Adapters/Profile/Registry/Planner/Runtime/Workspace/projector plus tests/docs/evidence changed. Database schema, migration, public API family, dependencies and lockfile are unchanged.

## 69. Acceptance Results

N5 acceptance is 10/10; Registry is 62; implementation-critical TBDs are zero.

## 70. Commit And CI History

- Implementation `34bcea5bd3672d91f3282e12dd5a0cb6b789f1ff` / exact-SHA CI `31311023072`: success.
- Failed completion candidate `49da783610887c29ee01307884f45f2d9096b287` / CI `31311662979`: unit job found two retained N1/N2 queue assertions that did not allow the approved N5 completion-waiting status; service-backed and frontend/browser/build jobs passed.
- Corrected completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: pending after completion CI.

## 71. Explicit Non-Scope

No N6, DFT/SCF/NSCF/GW/scissor, Band/DOS generation, Fermi surface, projected bands/fatbands, Wannier, transport, effective mass, charge/Bader/topology, arbitrary execution, external scientific API, generic workflow, RAG, memory, multi-agent, plugins or enterprise capability was added.

## 72. Queue State

`TASK_BLOCK_COUNT=1`; N5 remains retained until completion and archive exact-SHA CI pass.

## 73. Automatic N6 Entry

NO. `PHASE_10N6_EXECUTABLE_TASK_CREATED=NO`; Phase 10N-6 remains `REVIEWER_GATE / NOT_QUEUED / NOT_EXECUTABLE`.

## 74. Final Repository State

At completion-record creation: branch master, implementation authority `34bcea5bd3672d91f3282e12dd5a0cb6b789f1ff` / CI `31311023072`, Registry 62, migration head 0007, task count one retained N5 task, N6 executable task absent. Completion and archive exact-SHA authority remain pending.

Mandatory markers: `N5_PLATFORM_DFT_EXECUTION=0`; `N5_PLATFORM_GW_EXECUTION=0`; `N5_BAND_GENERATION_FROM_STRUCTURE=0`; `N5_DOS_GENERATION_FROM_STRUCTURE=0`; `N5_DOS_GENERATION_FROM_BANDS=0`; `N5_FERMI_SURFACE_GENERATION=0`; `N5_PROJECTED_BAND_ANALYSIS=0`; `N5_FRONTEND_BAND_GAP_RECOMPUTATION=0`; `N5_FRONTEND_DOS_RECOMPUTATION=0`; `N5_FRONTEND_ENERGY_ALIGNMENT_AUTHORITY=0`; `N5_FRONTEND_SPIN_MERGING_AUTHORITY=0`; `NEW_LLM_CALL_SITES=0`; `N5_REAL_LLM_CALLS=0`.

Boundary markers: database schema = unchanged; migration = unchanged; migration head = `0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies = unchanged; lockfile = unchanged; Registry count = 62.

# Phase 10N-6 Professional Capability Integration + Evidence Closure Result

## 1. Conclusion
N6 integration and evidence implementation is complete within sealed N1-N5 scientific contracts. Corrected implementation exact-SHA CI passed; completion-record and archive CI remain lifecycle gates.

## 2. N5 Baseline
Verified N5 archive `2496d7a9ceb61d016f0f8d6a7f3fdd4572df3295` / CI `31312979614` is the sole entry authority. Failed completion `49da783610887c29ee01307884f45f2d9096b287` is historical only.

## 3. Entry Gate
Master, HEAD/origin equality, clean worktree, ancestry, Registry 62, DataProfile 2.4, migration 0007 and zero queued tasks passed at entry.

## 4. N6-R0 Integration Closure
The nine-Tool inventory, integration/evidence matrices and zero-new-science boundary are exact; implementation-critical TBDs are zero.

## 5. Acceptance Registry
N6-A01 through N6-A10 are implemented exactly once in each canonical authority document: 10/10, missing/extra/duplicate/conflicting zero.

## 6. Phase 10N Tool Inventory
N1 contributes CrystalNN/VoronoiNN; N2 local environment; N3 XRD comparison; N4 RDF/MSD/diffusion; N5 Band/DOS: nine professional Tools total.

## 7. Registry 62 Preservation
`REGISTRY_BEFORE_N6 = 62`; `REGISTRY_AFTER_N6 = 62`; N6 adds no Tool.

## 8. DataProfile 2.4 Closure
Profiles 2.0-2.4 remain readable and 2.4 covers all approved readiness facts without results or backfill. `DATAPROFILE_BEFORE_N6 = 2.4`; `DATAPROFILE_AFTER_N6 = 2.4`.

## 9. N1-N5 Capability Matrix
Every professional Tool maps Profile facts, Eligibility, Planner metadata, ports, Adapter, Artifact, identity, units, renderer, selection, projector, Report/Recipe and evidence; unmapped Tools are zero.

## 10. AnalysisIntent Coverage
Coordination, local environment, XRD, RDF, MSD, diffusion, Band/gap, DOS/projected DOS and clarification/unsupported/mismatch routes are covered.

## 11. Eligibility Coverage
Exact prerequisites and typed unavailable/incompatible states are validated without executing scientific algorithms.

## 12. Planner Coverage
Capability-aware routing uses Intent, Profile, metadata, Eligibility and exact bindings; negative cross-domain routing passes.

## 13. Source Ambiguity Behavior
Multiple structures, XRD resources, trajectories or electronic resources produce clarification, never latest/first/best binding.

## 14. AnalysisPlan 0.1 Compatibility
Plan 0.1 remains readable and unchanged.

## 15. AnalysisPlan 0.2 Dependency Closure
N1-to-N2, theoretical-XRD-to-N3 and MSD-to-diffusion ports preserve producer output contract, checksum and consumer input identity.

## 16. PlanValidator Closure
Wrong scope, identity, checksum, Tool/contract version and stale/foreign sources are typed rejected without repair.

## 17. QueueWorkerRuntime Closure
Positive cases persist Intent, Eligibility, Plan, Job, ToolCall, Adapter output, Artifact, lineage and terminal state through the real Runtime.

## 18. Partial Execution Closure
Producer failure blocks descendants while independent branches remain available; no fallback, replan or silent rerun occurs.

## 19. Artifact Contract Inventory
All N1-N5 Artifact families expose exact type/version, producer, sources, params, units, coverage, warnings, limitations, checksum and lineage.

## 20. Artifact Lineage
Artifact dependencies are checksum-bound and source-scoped; recomputation does not cross sealed dependency boundaries.

## 21. Identity Matrix
Structure/site/neighbor/environment/polyhedron, XRD, trajectory and electronic identities are exact; array position, display label, filename, nearest/fuzzy and latest authority are none.

## 22. Unit Matrix
Angstrom, degree, dimensionless coordination/RDF, ps, angstrom^2, angstrom^2/ps, eV and source-qualified DOS/reciprocal semantics are explicit.

## 23. Scientific Wording Audit
Production wording remains algorithm/source/tolerance/window-qualified; definitive bonding, phase confirmation, unconditional diffusion and platform-DFT claims are rejected.

## 24. N1 Coordination E2E
Periodic structure through Profile/Intent/Eligibility/Planner/Runtime/Artifact/Workspace/interpretation/Report/Recipe passes.

## 25. N1 Algorithm Independence
CrystalNN and VoronoiNN remain distinct authorities with no merge, rank or winner selection.

## 26. N2 Local Environment E2E
Exact N1 Artifact dependency through polyhedron Artifact and delivery surfaces passes.

## 27. N1-to-N2 Dependency Integrity
`N2_RECOMPUTED_N1_NEIGHBORS = 0`; `N2_INDEPENDENT_NEIGHBOR_SEARCH = 0`; `N2_COORDINATION_ALGORITHM_FALLBACK = 0`.

## 28. N3 Experimental XRD E2E
Experimental resource plus exact theoretical Artifact produces matched/unmatched peaks, residuals and persisted delivery evidence.

## 29. N3 Zero-Match / Wavelength Negative Cases
Zero matches is a valid scientific result; wavelength mismatch is typed incompatible. `N3_THEORETICAL_XRD_REIMPLEMENTATION = 0`; `N3_AUTOMATIC_PATTERN_SHIFT = 0`; `N3_RIETVELD_REFINEMENT = 0`; `N3_AUTOMATIC_PHASE_IDENTIFICATION = 0`.

## 30. N4 RDF E2E
Exact trajectory species/window RDF passes Profile through Report/Recipe with persisted bins, normalization and coverage.

## 31. N4 MSD E2E
Server-side unwrapping, physical time, total/species/directional MSD and origin coverage pass.

## 32. N4 Diffusion E2E
Diffusion consumes exact persisted MSD with explicit fit window and diagnostics. `N4_DIFFUSION_RAW_TRAJECTORY_READS = 0`; `N4_DIFFUSION_MSD_RECOMPUTATION = 0`.

## 33. N4 Ballistic Negative Case
MSD remains valid while qualification is unavailable: `N4_MSD_WRAPPED_COORDINATE_DIRECT_USE = 0`; `N4_AUTOMATIC_DIFFUSION_WINDOW_OPTIMIZATION = 0`; `N4_BALLISTIC_SILENT_FIT = 0`; `N4_MISSING_TIME_DIFFUSION = 0`.

## 34. N5 Band E2E
Supplied Band Resource produces exact Band Artifact, sampled gap/VBM/CBM/directness/classification and delivery evidence.

## 35. N5 DOS E2E
Supplied DOS Resource preserves total/spin/projection completeness and exact delivery evidence.

## 36. N5 Band+DOS Combined Presentation
Compatible persisted Artifacts combine without a third Tool or browser alignment; incompatible sources do not combine.

## 37. Workspace Integration
Each Job retains one metadata-first Workspace; inactive heavy payload requests are zero and active loads are cancellable with stale suppression.

## 38. Canonical Selection
All stable selections are exact; renderers without stable identities remain consumer-only and prohibited cross-science mappings are absent.

## 39. Inspector
Professional panels expose Tool/version, Artifact/checksum, source hashes, algorithms, params, units, coverage, warnings, limitations and lineage.

## 40. Grounded Interpretation
Each Artifact family has deterministic bounded projection or an explicit disposition; providers receive facts rather than raw scientific authority.

## 41. Grounding Negative Cases
Invented values/units/entities/thresholds and bonding, confirmation, unqualified diffusion or platform-DFT claims are rejected.

## 42. Report Closure
Reports compose persisted facts with coverage/warnings/limitations/provenance. `REPORT_GENERATED_SCIENTIFIC_VALUES = 0`; `REPORT_GENERATED_SCIENTIFIC_CLAIMS = 0`; `REPORT_SCIENTIFIC_RECOMPUTATION = 0`.

## 43. Recipe Closure
Recipes preserve Profile/Intent/Eligibility/Plan/Tool/params/dependencies/contracts/sources and remain declarative. `RECIPE_EXECUTION_AUTHORITY = NONE`; plan/job/queue authority is none.

## 44. Historical Compatibility
Profiles 2.0-2.4, Plans 0.1/0.2, historical Jobs/Workspaces/Artifacts/Reports/Recipes remain readable without backfill or read-time science; historical rebinding is zero.

## 45. Phase 10K/L/M Regression
Generic Profile, Explorer, ML, Composition, Intent, Eligibility, Plans, interpretation, Workspace/selection/gallery and Report/Recipe regressions pass; one-Workspace-per-Job and migration authority are unchanged.

## 46. PostgreSQL
Exact-SHA CI persisted and scoped professional resources, ToolCalls, Artifacts, dependencies and Workspaces successfully.

## 47. Redis
Queue/runtime and dependency behavior passed service-backed closure.

## 48. MinIO
Artifact payload/checksum persistence and retrieval passed service-backed closure.

## 49. Browser Matrix
Chromium, Firefox and WebKit professional-family replays pass with zero console/page/unexpected-response/external-request errors.

## 50. Mobile
Chromium 390x844 covers structure, XRD, trajectory and electronic families without horizontal overflow.

## 51. Accessibility
Keyboard/focus, named controls, non-color state, tables/text alternatives, 44px targets, 200% reflow and reduced motion pass.

## 52. Performance
Small/medium/near-cap/over-cap evidence and bounded E2E timings/Artifact bytes/load/projection/report metrics are retained as development evidence, not an SLA.

## 53. Viewer Lifecycle
Fifty cross-panel cycles show zero WebGL/listener/observer/animation/canvas/chart/request/stale-response growth.

## 54. Security
Arbitrary code, shell/filesystem/notebook/network/dynamic module, executable Artifact content, cross-scope/stale/latest/fuzzy binding and secret/path/stack/storage disclosure gates pass.

## 55. LLM / DeepSeek
`N6_NEW_LLM_CALL_SITES = 0`; `N6_REAL_LLM_CALLS_DEFAULT_CI = 0`; N6 requires no LLM and DeepSeek policy regression passes.

## 56. References / Fixtures
N1-N5 retained references plus newly replayed critical positive and negative integration fixtures are inventoried in the N6 manifest.

## 57. Tolerance Closure
Existing quantity-specific tolerances are preserved; N6 changes no formula, threshold, default or scientific parameter.

## 58. Evidence Inventory
The N6 evidence tree contains baseline/R0/acceptance, capability/tool/Profile/Planner/Plan/Artifact/identity/unit matrices, E2E/negative/historical/delivery/service/browser/performance/accessibility/security records.

## 59. Evidence Manifest Integrity
Normalized manifest validation reports entries present, missing/extra/hash mismatch/secret-bearing evidence zero; screenshots are not numeric authority.

## 60. Documentation Closure
N6 contracts, matrices, evidence map, completion, final summary and Phase 11 reviewer gate are documented; canonical and persistent authorities are synchronized.

## 61. Files Changed
N6 changed integration tests, aggregate CI/browser/service gates, evidence and documentation only; no scientific production authority was added.

## 62. Production Behavior Changes
Linux browser-server process-group cleanup and CI build ordering prevent lifecycle resource accumulation without changing scientific behavior or test coverage.

## 63. Acceptance Results
N6 acceptance 10/10; backend 1252 passed, frontend 449 passed, service-backed 48 passed with zero skipped/failed/errors, browser/typecheck/build/lock/security/evidence passed. npm audit is UNAVAILABLE because the configured mirror returns `404_NOT_IMPLEMENTED`.

## 64. Phase 10N Final Readiness
Coordination, Local Environment/Polyhedra, Experimental XRD, trajectory RDF/MSD/Diffusion and electronic Band/DOS are each `READY_WITH_EXPLICIT_LIMITS`.

## 65. Commit / CI History
- Failed implementation `ea156ed898ce7c2ed539a026f2983b239e444d8a` / CI `31315296903`: build cancellation after accumulated browser servers; retained historical only.
- Corrected implementation `eda7cda4d14207abaf97a0a88cc263b0d1ad3319` / CI `31316556495`: success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Verified queue-archive SHA/CI: pending after completion CI.

## 66. Explicit Remaining Limits
No bond-valence/oxidation inference, Rietveld/refinement/phase fraction/automatic phase identification, unsupported variable-cell MSD, Green-Kubo/VACF/Arrhenius, DFT/GW/Fermi surface/projected bands/Bader/defects/surfaces, arbitrary execution, generic workflow or autonomous scientific agent.

## 67. Queue State
`TASK_BLOCK_COUNT = 1`; the completed N6 task remains until completion-record and archive exact-SHA CI pass.

## 68. Phase 11 Gate
Phase 11 is `REVIEWER_GATE / NOT QUEUED / NOT EXECUTABLE`; `PHASE11_EXECUTABLE_TASK_CREATED = NO`.

## 69. Final Repository State
At completion-record creation: master, implementation authority `eda7cda4d14207abaf97a0a88cc263b0d1ad3319` / CI `31316556495`, Registry 62, DataProfile 2.4, migration head 0007, one retained N6 task. The verified archive gate remains pending.

Mandatory N6 markers: `N6_NEW_SCIENTIFIC_TOOLS = 0`; `N6_NEW_SCIENTIFIC_ALGORITHMS = 0`; `N6_NEW_ARTIFACT_FAMILIES = 0`; `N6_NEW_DATAPROFILE_VERSION = 0`; `N6_NEW_PUBLIC_API_FAMILIES = 0`; `N6_NEW_DATABASE_MIGRATIONS = 0`; `N6_NEW_DEPENDENCIES = 0`; `N6_NEW_LLM_CALL_SITES = 0`; `N6_REAL_LLM_CALLS_DEFAULT_CI = 0`.

Authority markers: `FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE`; `FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE`; `WORKSPACE_SCIENTIFIC_AUTHORITY = NONE`; `REPORT_SCIENTIFIC_RECOMPUTATION = 0`; `RECIPE_EXECUTION_AUTHORITY = NONE`; `N5_PLATFORM_DFT_EXECUTION = 0`; `N5_PLATFORM_GW_EXECUTION = 0`; `N5_BAND_GENERATION_FROM_STRUCTURE = 0`; `N5_DOS_GENERATION_FROM_STRUCTURE = 0`; `N5_FERMI_SURFACE_GENERATION = 0`; `N5_PROJECTED_BAND_ANALYSIS = 0`.

Repository boundaries: database schema = unchanged; migration = unchanged; migration head = `0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies = unchanged; lockfile = unchanged; Registry count = 62; DataProfile = 2.4.

# Phase 11-0 Validation Baseline Reconciliation + Governance Seal Result

## 1. Conclusion
PASS. Phase 11-0 reconciled the current validation baseline and sealed governance without production scientific changes. Implementation `312fd4445d404f0f89c061fbdc055789912dc552` passed exact-SHA CI `31324356338`.

## 2. Phase 10N Baseline
N6 verified archive `d4d625b57449f9a451d5e27a6eb903625d221bc7` is the sole entry authority; failed N6 `ea156ed...` remains historical only.

## 3. Entry Gate
Master, clean entry worktree, `HEAD == origin/master`, N6 ancestry, Registry 62, DataProfile 2.4, migration 0007, and zero queued tasks passed before admission.

## 4. Gate J6-R Roadmap Authority Reconciliation
Repository/current reviewer authority supersedes stale phase-generated next-scope numbering without rewriting history.

## 5. Approved Phase 11 / 12 / 13 Roadmap
Phase 11 is scientific validation; Phase 12 is comprehensive UI/UX redesign; Phase 13 is final product closure. Old Phase 12 final-closure numbering is superseded.

## 6. Production Behavior Changes
`PRODUCTION_BEHAVIOR_CHANGES = NONE`; only docs, persistent state, evidence, deterministic audit tooling, and audit consistency tests changed.

## 7. Registry Inventory
All 62 live Registry entries were read from the three manifests and reconciled against Adapter declarations.

## 8. Registry Count 62 Verification
`REGISTRY_BEFORE_11_0 = 62`; `REGISTRY_AFTER_11_0 = 62`; unique rows 62; duplicate/unclassified rows 0.

## 9. Tool Role Classification
Rows cover scientific numeric/geometry/classification/transformation, data intelligence, materials ML, composition, visualization-data, product composition, presentation, and metadata/utility roles.

## 10. Validation Dimension Model
Software execution, scientific reference, numeric validation, Artifact contract, platform integration, browser presentation, reproducibility, and known limitations are independent axes.

## 11. Current Validation Level Distribution
28 rows are conservatively V2 controlled-reference and 34 V1 runtime/Artifact; Phase 11-0 promotes none to V3/V4.

## 12. Existing Evidence Inventory
Ten Phase 10 evidence roots were indexed with file, manifest, browser, service, and reference indicators.

## 13. Existing Reference Inventory
43 reference-like retained records were hashed and classified; no reference was downloaded.

## 14. Reference Provenance Classification
Analytic, official-library/project, independent cross-library, controlled synthetic, internal expected, mapping-only, and no-reference types are sealed.

## 15. Reference Independence Audit
Self-reference remains regression evidence only; reference authority follows provenance/hash/contract, not recency.

## 16. Existing Fixture Inventory
169 fixture records were indexed with stable path/hash and review disposition.

## 17. Fixture Immutability Policy
Authoritative fixtures cannot be overwritten in place; source/value/transformation changes require a new version.

## 18. Fixture License Status
Repository-internal versus `LICENSE_REVIEW_REQUIRED` is recorded; no legal status is inferred.

## 19. Official Example Historical Inventory
54 official/example records were indexed, including retained Phase 10F mappings.

## 20. Current Official Example Status
Records distinguish current, retained historical, mapping-only, extraction-required, and superseded status; none was executed here.

## 21. Input / Resource / Parser Inventory
Upload/sniffing, parser, Resource, Profile, Planner, Runtime, Workspace, caps, and negative paths were audited.

## 22. Supported Input Matrix
CSV/CIF/POSCAR are direct; canonical JSON, XYZ/EXTXYZ, volumetric, ZIP, and supplied electronic JSON are bounded; phonon direct upload is mapping-only; XLSX, Parquet, and LAMMPS trajectory are unsupported.

## 23. DataProfile 2.4 Input Coverage
Profile 2.4 remains unchanged and records readiness only, never validation results.

## 24. Planner / Eligibility Input Coverage
Support requires an actual parser/resource/profile path; library theoretical format support is insufficient.

## 25. Runtime / Workspace Input Coverage
Runtime and renderer disposition are separate from parsing and mapping status.

## 26. Scientific Numeric Validation Inventory
Numeric Tools retain analytic/controlled/internal distinctions and quantity-owned tolerances.

## 27. Scientific Geometry Validation Inventory
Structure, local geometry, reciprocal-cell, and periodic identity evidence remains explicit; independent gaps are assigned.

## 28. Product / Presentation Validation Inventory
These require contract, exact source, no recomputation, deterministic rendering, accessibility, and security rather than invented numeric benchmarks.

## 29. N1 Validation Baseline
CrystalNN/VoronoiNN algorithm identity, neighbors, weights, coordination, distance, determinism, and disagreement semantics are inventoried; mutual equality is not required.

## 30. N2 Validation Baseline
Exact N1 dependency, geometry, distortion, hull, tie, periodic identity, and synthetic controls are retained.

## 31. N3 Validation Baseline
Input validation, detection, normalization, one-to-one matching, ties, residuals, unmatched sets, zero-match, wavelength mismatch, and coverage are retained. Correspondence is not phase confirmation.

## 32. N4 Validation Baseline
Unwrapping, PBC, RDF, MSD, directional/origin coverage, diffusion diagnostics, ballistic rejection, random walk, missing time, and variable-cell policy are classified by evidence strength.

## 33. N5 Validation Baseline
Energy/Fermi/spin/path/band/gap/DOS/projection/compatibility controls validate supplied output, not platform DFT.

## 34. Earlier Initial-Release Science Validation Baseline
Composition, statistics, Dataset Explorer, ML, PCA/KMeans, structure summaries, static RDF/XRD, trajectory presentation, phonon, BZ, and volumetric capabilities are included.

## 35. Tolerance Inventory
Identity exactness plus N1-N5, phonon, and BZ quantity-specific policies are indexed.

## 36. Tolerance Ownership
Every tolerance records contract, metric, unit, provenance, reason, owner, justification, variance relevance, and review state.

## 37. Exact Identity Rules
Tool/version, hashes, checksums, Plan bindings, site/atom/frame/k-point/band/evidence identities remain exact.

## 38. Variance Classification
Only `EXACT`, `TOLERANCE_BOUNDED`, `DISPLAY_ONLY_VARIANCE`, `UNSUPPORTED_PLATFORM`, and `KNOWN_LIMITATION` are allowed.

## 39. Revalidation Triggers
Scientific versions/algorithms/default semantics/contracts/units/parsers/authority dependencies/fixtures/tolerances/identity changes invalidate relevant validation.

## 40. Locked Environment Policy
Primary scientific environment is the current repository lock; arbitrary dependency-version compatibility is not claimed.

## 41. Cross-Platform Target Matrix
Locked Linux CI and Windows are targets; macOS is not a current release target absent separate support evidence.

## 42. Browser Validation Boundary
Chromium, Firefox, WebKit, and 390x844 validate presentation/interaction/no recomputation, not numeric truth.

## 43. Service Validation Boundary
PostgreSQL/Redis/MinIO validate persistence, queue, Artifact storage, identity, lineage, scope, and checksum, not numeric truth.

## 44. Screenshot Authority Boundary
`SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE`.

## 45. Validation Gaps
Twelve concrete provenance, independent benchmark, variance, and honest coverage gaps were recorded; no catch-all gap exists.

## 46. Gap Prioritization
P0=0; release-relevant P1 and supporting P2 gaps are assigned to exact Phase 11 stages.

## 47. Phase 11-1 Backlog
Exact official/static sources, fixtures, source/license checksums, and transformation requirements are sealed; no numeric PASS is authorized.

## 48. Phase 11-2 Backlog
Exact Tool/version, fixture, expected invariant/value, unit, tolerance, positive/negative case, and 11-1 dependency fields are documented.

## 49. Phase 11-3 Matrix
Locked Linux/Windows scientific variance and four-browser presentation invariants use the sealed variance taxonomy.

## 50. Phase 11-4 Coverage Rules
`DIRECT_VERIFIED`, `OFFICIAL_DERIVED_VERIFIED`, `REFERENCE_VERIFIED`, `MAPPING_ONLY`, `EXTRACTION_REQUIRED`, `FUTURE_SCOPE`, and `UNSUPPORTED` have exact evidence criteria.

## 51. Phase 11-5 Closure Criteria
Reference, golden benchmark, tolerance, variance, Tool/input/example coverage, reproducibility, limitations, manifest, and acceptance deliverables are mandatory.

## 52. Phase 12 UI/UX Scope Seal
Phase 12 covers IA/design system/navigation/Planner/Workspace/viewers/findings/Inspector/Report/Recipe/responsive/accessibility only; new scientific authority defaults to zero.

## 53. Phase 13 Final Product Closure Scope Seal
Phase 13 covers fact alignment, integration gaps, seven E2E demos, docs/reproducibility, polish, regression, and archive/presentation.

## 54. Future Scope Guard
Fermi surface, projected bands, Rietveld, DFT/GW, Bader, defects/surfaces, advanced transport/trajectory science, and arbitrary Python remain unqueued.

## 55. Not Planned Guard
Generic workflow/DAG/notebook/replanning/RAG/plugins/SaaS/billing/enterprise/Kubernetes/distributed scheduler/KMS and unrestricted providers remain excluded.

## 56. Canonical Authority Order
Goal/requirements -> ROADMAP -> persistent state -> TASKS -> reviewer prompt -> generated next-scope suggestion.

## 57. Acceptance Registry
P11V0-A01 through P11V0-A10: expected/implemented 10/10; missing/extra/duplicate/conflicting/shorthand 0.

## 58. Evidence Inventory
Structured Registry, Artifact, input, parser, evidence, reference, fixture, official-example, tolerance, variance, gaps, levels, triggers, acceptance, and roadmap files are retained.

## 59. Evidence Manifest
Normalized manifest has entries >0, missing/hash/secret-bearing evidence 0; docs links and Phase 11 secret-pattern checks pass.

## 60. Documentation Changes
Phase 11 governance documents, ROADMAP, docs index, README, and shared-schema evidence-only boundary were updated.

## 61. Persistent State Changes
PROJECT_BRIEF, DESIGN_PROGRESS, TASK_BOARD, CHANGELOG, OPEN_QUESTIONS, ADRs, and Registry notes record Phase 10N completion and the new route.

## 62. Security
No arbitrary code/scientific shell generation/notebook/downloaded script/external scientific API/reference download/frontend recomputation/LLM authority; secret-pattern scan passed.

## 63. LLM / DeepSeek
`NEW_LLM_CALL_SITES = 0`; `PHASE11_0_REQUIRES_LLM = NO`; `REAL_LLM_CALLS = 0`; existing DeepSeek-only policy regressed only.

## 64. Database / API / Dependency Freeze
Database schema, migration 0007, public API family, dependencies, lockfile, Registry, and DataProfile are unchanged.

## 65. Tests
Local: backend 1263 passed; frontend 449 passed; typecheck/build/lock/diff/evidence passed. CI `31324356338` passed Unit, Frontend/browser/build, and service-backed jobs.

## 66. Browser Regression
Exact-SHA CI Frontend/browser replay job passed Chromium, Firefox, WebKit, and mobile retained matrix.

## 67. Service-Backed Regression
Exact-SHA CI PostgreSQL/Redis/MinIO job passed with its zero-skip gate.

## 68. npm Audit Status
`npm audit = UNAVAILABLE`; configured mirror returned `404_NOT_IMPLEMENTED`. Dependency lock consistency and security tests passed.

## 69. Files Changed
Docs, persistent state, evidence, one deterministic audit generator, and audit/TASKS compatibility tests only; production source changes 0.

## 70. Commit / CI History
Implementation `312fd4445d404f0f89c061fbdc055789912dc552` / CI `31324356338`: success. Completion record: this commit. Per explicit user direction, later documentation/queue commits are submitted without waiting for additional CI.

## 71. Queue State
At completion-record creation, exactly one completed Phase 11-0 task remains pending queue archive.

## 72. Automatic 11-1 Entry
`PHASE_11_1_EXECUTABLE_TASK_CREATED = NO`; Phase 11-1 remains reviewer-gated.

## 73. Final Repository State
Registry 62, DataProfile 2.4, migration 0007, master. Queue archive follows as a separate direct commit; Phase 12/13 remain approved roadmap only.

## 74. Reviewer Decision Required for 11-1
Phase 11-1 requires a new reviewer prompt before any reference acquisition, extraction, fixture consolidation, or task admission.

Mandatory markers: `PHASE11_0_NEW_SCIENTIFIC_TOOLS = 0`; `PHASE11_0_NEW_SCIENTIFIC_ALGORITHMS = 0`; `PHASE11_0_NEW_ARTIFACT_FAMILIES = 0`; `PHASE11_0_NEW_DATAPROFILE_VERSION = 0`; `PHASE11_0_NEW_ANALYSISPLAN_VERSION = 0`; `PHASE11_0_NEW_PUBLIC_API_FAMILIES = 0`; `PHASE11_0_NEW_DATABASE_MIGRATIONS = 0`; `PHASE11_0_NEW_DEPENDENCIES = 0`; `PHASE11_0_NEW_LLM_CALL_SITES = 0`; `PHASE11_0_REAL_LLM_CALLS = 0`; `PHASE11_0_EXTERNAL_REFERENCE_DOWNLOADS = 0`; `PHASE11_0_NOTEBOOK_EXECUTIONS = 0`; `PHASE11_0_DOWNLOADED_SCRIPT_EXECUTIONS = 0`.

Honesty markers: `BROWSER_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO`; `SERVICE_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO`; `FIXTURE_EXISTS_EQUALS_REFERENCE_VERIFIED = NO`; `MAPPING_EQUALS_VERIFIED = NO`; `SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO`; `LATEST_EVIDENCE_WINS_AUTHORITY = NO`; `GLOBAL_SCIENTIFIC_EPSILON = NONE`; `PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED`.

Roadmap markers: `PHASE_11 = SCIENTIFIC_VALIDATION`; `PHASE_12 = COMPREHENSIVE_UI_UX_PRODUCT_EXPERIENCE_REDESIGN`; `PHASE_13 = FINAL_PRODUCT_CLOSURE`; `OLD_PHASE12_FINAL_CLOSURE_NUMBERING = SUPERSEDED`; `FUTURE_SCOPE = DOCUMENTED_NOT_QUEUED`; `PHASE14 = NOT_CREATED`.

Queue archive addendum: completion record `dee197d39e194277351a34fcd063b3de97729534`; queue archive = this commit. `TASK_BLOCK_COUNT = 0`; Phase 11-1 remains `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 12/13 are roadmap-approved, not queued, and not executable. The implementation CI is the sole waited/verified CI per explicit user direction.

# Phase 11-1 Reference Provenance + Safe Fixture Consolidation Result

## 1. Conclusion
Reference and fixture inputs required for the approved Phase 11-2 benchmark scope are provenance-sealed and safely prepared. Scientific Tools are not declared validated in this phase.

## 2. Phase 11-0 Baseline
Entry authority is `ef40ade537820e88bbe2d259a9b4ccb9cd04ac1c`; Registry 62, DataProfile 2.4, migration 0007, and a clean queue baseline were verified.

## 3. Entry Gate
`PHASE_11_1_ENTRY_GATE = PASS`; the first task was admitted as the only active task.

## 4. Phase 11-0 Backlog Reconciliation
All 12 retained gap records were reconciled without downgrading priorities or changing scientific semantics. Actual retained counts are 46 reference-like, 170 fixtures, and 55 official/example records.

## 5. Production Behavior Changes
None. No production scientific source was changed.

## 6-15. Reference Acquisition, Version, Checksums, Retention, License
No external reference download was required. Existing repository evidence was reused with SHA-256 source identity, retained-evidence version pinning, raw-retention disposition, and explicit license/redistribution status. Official-example records remain reference-only where redistribution is unclear.

## 16-20. License Review, Reuse, Deduplication, Independence
Same checksums are classified as reused, not independent evidence. Same-library expected data is `SELF_REFERENCE`; official/example provenance with unresolved licensing is `UNRESOLVED`. No filename or recency authority is used.

## 21-30. Fixture Reuse, Identity, Checksums, Transformations
170 retained fixture records are reused without in-place rewrite. Twelve benchmark handoff views have distinct fixture identities and link back to retained source bytes. `P11TRANS-IDENTITY-001@1.0.0` is metadata-only, deterministic, and has `numericMutation=false`, `unitMutation=false`, and `orderingMutation=false`.

## 31-36. Capability Reference Preparation
N1 coordination, N2 geometry, N3 XRD, N4 trajectory, N5 electronic, phonon, volumetric, ML/composition, and earlier retained evidence are linked to typed provenance records. No numeric comparison was executed.

## 37. Official Example Reconciliation
55 official/example records remain retained historical mapping or reference-only evidence. `OFFICIAL_EXAMPLE_EXISTS != REFERENCE_VERIFIED`.

## 38. Input Support Non-Change Verification
Input verdicts are unchanged: CSV/CIF/POSCAR direct supported; canonical JSON, XYZ/EXTXYZ, volumetric, ZIP, and supplied electronic JSON supported with limits; phonon mapping-only; XLSX, Parquet, and LAMMPS trajectory unsupported.

## 39-41. Numeric, Level, and Coverage Boundaries
`PHASE11_1_NUMERIC_SCIENTIFIC_PASS_DECLARATIONS = 0`; validation-level promotions = 0; honest coverage promotions = 0. Phase 11-2 owns platform-output comparison.

## 42. Tolerance Non-Change
`TOLERANCE_CHANGES = 0`; the Phase 11-0 tolerance registry remains authoritative and pass-driven widening remains prohibited.

## 43-47. Gaps, Priorities, Unresolved Items
P0 remains 0. P1/P2 provenance, license, independent benchmark, variance, and coverage gaps remain typed in the generated unresolved matrix; no current scientific discrepancy was invented or hidden.

## 48-50. Phase 11-2 Benchmark Input Manifest
`phase11_2_benchmark_input_manifest.json` contains 12 exact handoff records, each with gap, Tool/version, reference, fixture/version/checksum, units, tolerance reference, case role, independence, readiness, and blocking reason. `IMPLEMENTATION_CRITICAL_TBD = 0`.

## 51-56. Registries and Evidence Manifest
Reference, fixture, checksum, license, raw-retention, transformation, independence, duplicate, official-example, acquisition, and benchmark manifests are under `docs/phase11/evidence/phase11_1_reference_provenance_safe_fixture/`. Manifest hashes and required-file checks passed.

## 57. Network Acquisition Audit
External downloads = 0; external scientific API calls = 0; downloaded scripts = 0; notebooks = 0; unapproved external requests = 0.

## 58-60. Security, LLM, Database/API/Dependencies
No arbitrary execution or LLM authority was added. Registry remains 62; DataProfile 2.4; migration 0007; database/API/dependencies/lockfile unchanged.

## 61. Registry / DataProfile Freeze
`REGISTRY_BEFORE_11_1 = 62`, `REGISTRY_AFTER_11_1 = 62`, `DATAPROFILE_BEFORE_11_1 = 2.4`, `DATAPROFILE_AFTER_11_1 = 2.4`.

## 62-65. Tests, Browser, Service, npm Audit
Focused governance/provenance tests passed (65 passed in the final focused set). Implementation CI `31327344030` passed Unit (1259 passed, 1 skipped), Service-backed, Frontend typecheck/build, and browser replay. Local full pytest timed out at 124 seconds without assertion output. npm audit remains subject to the repository mirror's existing unavailable policy and was not used as a PASS claim.

## 66. Files Changed
Added the Phase 11-1 evidence pack, provenance generator, tests, eight Phase 11 documents, canonical plan/lock/backlog updates, persistent state entries, and queue/result records. No production source, schema, migration, dependency, or lockfile changed.

## 67. Acceptance Registry
P11V1-A01 through P11V1-A10 are implemented exactly once; missing, extra, duplicate, conflicting, and shorthand counts are zero.

## 68-71. Commit, CI, Completion, Archive
Initial candidate `0ab99b9` failed historical queue assertions; `a9e15a3` was a fix-forward candidate with a syntax error; final implementation `cfb87369ac2af00f4a631654b841dffee8faf024` passed CI `31327344030`. Completion and queue archive are direct documentation/state commits per user instruction, with no additional CI wait.

## 72. Queue State
Phase 11-1 is completed and its block is pending archive; Phase 11-2 and Phase 11-3 remain queued in `TASKS.md` as reviewer prompts and are not executed in this task.

## 73. Phase 11-2 Gate
Phase 11-2 is reviewer-gated until a new reviewer authorization. Its benchmark inputs are prepared, but no scientific PASS is inferred.

## 74. Final Repository State
At implementation completion, `master` was pushed at `cfb87369ac2af00f4a631654b841dffee8faf024`, with Registry 62, DataProfile 2.4, migration 0007, and no production behavior change. The next queue operation is to archive only the completed Phase 11-1 block.
## Phase 11-2 Cross-Capability Golden Scientific Benchmark Suite Result

Status: PASS / COMPLETE / AWAITING VERIFIED QUEUE ARCHIVE

Phase 11-2 executed the sealed benchmark handoff from Phase 11-1 without changing production scientific authority. The implementation commit `5e2f5f07346b7c7d6b7e8d360289cce4ad95ac92` passed implementation CI `31328760532`.

### Baseline and Scope

- Phase 11-1 handoff: verified provenance, immutable fixture records, source hashes, transformation records, license dispositions, and quantity-specific tolerance ownership.
- Registry: `62` before and after. DataProfile: `2.4` before and after. Migration: `0007_phase10m1_workspace_domain` unchanged.
- Production source behavior, Registry semantics, Artifact families, DataProfile, AnalysisPlan, public APIs, dependencies, lockfile, and database schema were unchanged.
- No external reference download, notebook execution, downloaded script execution, external scientific API call, LLM call, or new scientific algorithm occurred.

### Acceptance Registry

`P11V2-A01` through `P11V2-A10` were reconciled with no missing, extra, duplicate, shorthand, or conflicting entries. The suite covers sealed handoff integrity, execution authority, expected/actual separation, invariant comparison, units and identity, positive/negative cases, Artifact/evidence integrity, honest validation-level reporting, and 11-3 handoff.

### Benchmark Outcome

The deterministic suite contains `12` benchmark records: `8` `PASS_INVARIANT`, `4` `NOT_APPLICABLE`, `0` failures, and `0` blocked cases. Aggregate status is `PASS_WITH_NONBLOCKING_LIMITATIONS`. Expected and actual records are separate, each comparison records the applicable tolerance ID and units, and every source/fixture hash is verified.

The eight passing cases validate sealed identity/unit/invariant replay through the registered-contract evidence path. Four official/reference-limited cases remain `NOT_APPLICABLE` because their retained records do not contain a bounded expected numeric value; no numeric claim is manufactured and no validation level is promoted. This is an explicit scientific limitation, not a regression failure. Phase 11-3 receives eight reproducibility-ready cases.

### Scientific Boundaries

The suite does not equate software regression with independent scientific validation. It does not treat fixture existence, mapping, screenshots, browser success, service persistence, or self-reference as independent numeric truth. It preserves algorithm-specific semantics: CrystalNN and VoronoiNN are not expected to agree; XRD correspondence is not phase confirmation; ballistic MSD is not diffusion; supplied electronic data is not platform DFT.

### Evidence and Verification

Evidence root: `docs/phase11/evidence/phase11_2_golden_scientific_benchmark/`. It contains the benchmark registry, expected/actual/comparison records, summary, manifest, discrepancy matrix, and 11-3 input handoff. Focused Phase 11 governance/provenance/benchmark tests passed: `69 passed`. Implementation CI `31328760532` passed unit tests, service-backed integration, frontend typecheck/build, and the repository browser/evidence gates.

Mandatory markers:

```text
PHASE11_2_NEW_SCIENTIFIC_TOOLS = 0
PHASE11_2_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE11_2_NEW_ARTIFACT_FAMILIES = 0
PHASE11_2_NEW_DATAPROFILE_VERSION = 0
PHASE11_2_NEW_ANALYSISPLAN_VERSION = 0
PHASE11_2_NEW_PUBLIC_API_FAMILIES = 0
PHASE11_2_NEW_DATABASE_MIGRATIONS = 0
PHASE11_2_NEW_DEPENDENCIES = 0
PHASE11_2_NEW_LLM_CALL_SITES = 0
PHASE11_2_REAL_LLM_CALLS = 0
PHASE11_2_EXTERNAL_REFERENCE_DOWNLOADS = 0
PHASE11_2_NOTEBOOK_EXECUTIONS = 0
REGISTRY_BEFORE_11_2 = 62
REGISTRY_AFTER_11_2 = 62
DATAPROFILE_BEFORE_11_2 = 2.4
DATAPROFILE_AFTER_11_2 = 2.4
```

### Queue State

Phase 11-2 is complete and awaits direct verified queue archive. Phase 11-3 remains reviewer-gated and is not executable until the next queue admission. No Phase 12 or Phase 13 task was created.
## Phase 11-3 Cross-Platform Reproducibility and Variance Characterization Result

Status: PASS / COMPLETE / AWAITING VERIFIED QUEUE ARCHIVE

Phase 11-3 used the sealed Phase 11-2 reproducibility handoff without changing production science. Corrected implementation `e89dfaf23e376a7ae79432f9806d7a4bd3eaecac` passed exact-SHA CI `31332350363` after retaining two failed historical candidates (`20fa30e`, `937b940`) and correcting only cross-platform evidence harness behavior.

### Scope and Environment

- Eight `PASS_INVARIANT` cases were admitted; the four Phase 11-2 reference-limited cases remained excluded.
- Linux `ubuntu-latest` and Windows `windows-latest` each replayed the sealed handoff under Python 3.11 and the unchanged `uv.lock`.
- The lock semantic hash canonicalizes LF/CRLF for text representation only. Fixture/resource scientific checksums remain exact.
- macOS remains `NOT_CURRENT_RELEASE_TARGET`.

### Results

Linux and Windows independently passed all eight sealed invariant reference checks. Cross-platform benchmark, reference, fixture, tolerance, and unit identities are exact; persisted invariant output hashes are exact. The input handoff contains no sealed numeric expected values, therefore numeric cross-platform comparison is `NOT_APPLICABLE` and no V4 validation level is promoted.

Browser evidence remains presentation-only across Chromium, Firefox, WebKit, and Chromium 390x844. It cannot establish numeric scientific truth and frontend scientific recomputation remains zero. PostgreSQL, Redis, and MinIO evidence remains persistence/lineage evidence rather than numeric validation.

### Evidence and Verification

Evidence root: `docs/phase11/evidence/phase11_3_cross_platform_reproducibility/`. It contains the environment, lock, identity, unit, variance, browser, limitation, security, no-mutation, and Phase 11-4 handoff records. The Phase 11-4 handoff is an input only, not a final coverage verdict.

Local verification: backend `1278 passed, 1 skipped, 49 deselected`; the skipped test is outside the required Phase 11-3 scientific matrix. Focused Phase 11 lifecycle/reproducibility tests: `74 passed`. Frontend: `449 passed`; typecheck and production build passed. CI `31332350363` passed all five required jobs: Linux replay, Windows replay, unit, service-backed integration, and frontend/browser/typecheck/build.

### Boundaries and Markers

```text
PHASE11_3_NEW_SCIENTIFIC_TOOLS = 0
PHASE11_3_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE11_3_NEW_ARTIFACT_FAMILIES = 0
PHASE11_3_NEW_DATAPROFILE_VERSION = 0
PHASE11_3_NEW_ANALYSISPLAN_VERSION = 0
PHASE11_3_NEW_PUBLIC_API_FAMILIES = 0
PHASE11_3_NEW_DATABASE_MIGRATIONS = 0
PHASE11_3_NEW_DEPENDENCIES = 0
PHASE11_3_NEW_LLM_CALL_SITES = 0
PHASE11_3_REAL_LLM_CALLS = 0
PHASE11_3_EXTERNAL_REFERENCE_DOWNLOADS = 0
PHASE11_3_EXTERNAL_SCIENTIFIC_API_CALLS = 0
PHASE11_3_SCIENTIFIC_TOLERANCE_CHANGES = 0
REGISTRY_BEFORE_11_3 = 62
REGISTRY_AFTER_11_3 = 62
DATAPROFILE_BEFORE_11_3 = 2.4
DATAPROFILE_AFTER_11_3 = 2.4
LINUX_EQUALS_SCIENTIFIC_TRUTH = NO
WINDOWS_EQUALS_SCIENTIFIC_TRUTH = NO
CROSS_PLATFORM_AGREEMENT_EQUALS_REFERENCE_PASS = NO
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
BROWSER_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
SERVICE_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

### Queue State

Phase 11-3 is complete pending direct queue archive. Phase 11-4 remains reviewer-gated, not queued, and not executable. No Phase 12 or Phase 13 task was created.

# Phase 11-4 Honest Tool / Input / Official-Example Coverage Matrix Result

## 1. Conclusion

Phase 11-4 completed the approved audit-only coverage reconciliation. The 62 live Registry Tools, 14
existing input families, and 55 retained official/example records are classified with explicit limits.
This is not Phase 11 closure; Phase 11-5 remains the reviewer-gated closure authority.

## 2. Baseline and lifecycle

Phase 11-3 verified archive authority was `70c2a46`. Implementation candidate `0d57a99` was retained as
historical failed CI candidate after run `31347561130` failed only on a CRLF/LF evidence-hash assertion.
Fix-forward implementation `09250b163cd3957815ce67238163225efc689d83` passed exact-SHA CI
`31348272583`: Linux replay PASS, Windows replay PASS, Unit PASS, service-backed PASS, and frontend
typecheck/build/browser PASS. No history was rewritten.

Entry facts: Registry `62`, DataProfile `2.4`, migration `0007_phase10m1_workspace_domain`, and no
production scientific source change. Local verification was `1282 passed, 50 skipped, 63 warnings`;
frontend was `449 passed`; typecheck, build, lock check, focused coverage tests (`4 passed`), and
queue-compatibility tests (`63 passed`) passed. The first local `uv run pytest` invocation had an existing
Windows import-collection issue; the canonical `uv run python -m pytest -q` command passed.

## 3. Coverage governance

The authoritative coverage taxonomy is `DIRECT_VERIFIED`, `OFFICIAL_DERIVED_VERIFIED`,
`REFERENCE_VERIFIED`, `MAPPING_ONLY`, `EXTRACTION_REQUIRED`, `FUTURE_SCOPE`, and `UNSUPPORTED`.
Coverage is separate from validation level, input support, browser status, service status, and
reproducibility. Browser screenshots, service persistence, fixtures, internal regression, and mapping are
not independent scientific numeric references. Self-reference is not independent cross-library evidence.

## 4. Reconciled inventory

- Tool matrix: 62 unique live Registry rows, all versions `0.1.0`, all classified `MAPPING_ONLY` for this
  coverage axis; no validation-level promotion and no V4 row.
- Input matrix: 14 rows; support verdicts unchanged. Ten input paths are `DIRECT_VERIFIED` on the
  input-path axis, one is `MAPPING_ONLY`, and three are `UNSUPPORTED`.
- Official/example matrix: 55 retained rows, all `MAPPING_ONLY`; no official-derived or independent
  scientific reference claim was added.
- Phase 11-2 reconciliation: 12 records, 8 `PASS_INVARIANT`, 4 `NOT_APPLICABLE`, 0 failures.
- Phase 11-3 reconciliation: 8 admitted cases, Linux/Windows invariant replay PASS, numeric cross-platform
  status `NOT_APPLICABLE`, V4 promotion `0`.
- Existing N1-N5 and earlier initial-release scientific capability coverage remains bounded by inherited
  Tool contracts, input support, validation level, references, tolerances, fixtures, and gap records.

## 5. Public claims and limitations

Allowed wording is limited to coverage classified from retained evidence and facts derived under the
stated contract. Do not claim all Tools are independently scientifically validated, all formats are
directly supported, all platforms have numeric reproducibility, or that mapping/fixtures/screenshots prove
scientific correctness. The complete public claim matrix, known limitations, support matrix, and remaining
gaps are in `docs/phase11/` and the Phase 11-4 evidence directory.

## 6. Handoff and freeze

The exact machine-readable handoff is
`docs/phase11/evidence/phase11_4_honest_tool_input_example_coverage/phase11_5_closure_input_manifest.json`.
It records zero P0 gaps, zero numeric cross-platform claims, zero V4 promotions, no reference/fixture/
expected-value/tolerance mutation, and no production authority change. Phase 11-1 through 11-5 scope,
Future Scope, Not Planned boundaries, security, LLM, dependency, migration, and lockfile policies remain
unchanged.

## 7. Mandatory markers

```text
PHASE11_4_NEW_SCIENTIFIC_TOOLS = 0
PHASE11_4_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE11_4_NEW_ARTIFACT_FAMILIES = 0
PHASE11_4_NEW_DATAPROFILE_VERSION = 0
PHASE11_4_NEW_ANALYSISPLAN_VERSION = 0
PHASE11_4_NEW_DATABASE_MIGRATIONS = 0
PHASE11_4_NEW_PUBLIC_API_FAMILIES = 0
PHASE11_4_NEW_DEPENDENCIES = 0
PHASE11_4_NEW_LLM_CALL_SITES = 0
PHASE11_4_REAL_LLM_CALLS = 0
PHASE11_4_EXTERNAL_REFERENCE_DOWNLOADS = 0
PHASE11_4_EXTERNAL_SCIENTIFIC_API_CALLS = 0
PHASE11_4_NEW_SCIENTIFIC_BENCHMARKS = 0
PHASE11_4_VALIDATION_LEVEL_PROMOTIONS = 0
PHASE11_4_VALIDATION_LEVEL_DEMOTIONS = 0
PHASE11_4_REFERENCE_MUTATIONS = 0
PHASE11_4_FIXTURE_MUTATIONS = 0
PHASE11_4_EXPECTED_VALUE_MUTATIONS = 0
PHASE11_4_TOLERANCE_CHANGES = 0
REGISTRY_BEFORE_11_4 = 62
REGISTRY_AFTER_11_4 = 62
DATAPROFILE_BEFORE_11_4 = 2.4
DATAPROFILE_AFTER_11_4 = 2.4
MIGRATION_AFTER_11_4 = 0007_phase10m1_workspace_domain
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

## 8. Queue state

Phase 11-4 is `PASS / HONEST_COVERAGE_SEALED / QUEUE_ARCHIVED` after the direct completion and archive
commits. Phase 11 remains `IN_PROGRESS / SCIENTIFIC_VALIDATION_AND_COVERAGE_COMPLETE / AWAITING_FINAL_CLOSURE`.
Phase 11-5 is `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 12 and Phase 13 are approved, not queued,
and not executable. No automatic Phase 14 exists.

# Phase 11-5 Scientific Validation Closure + Release Candidate Gate Result

## Conclusion

Phase 11 is `COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS` and
`SCIENTIFIC_VALIDATION_RELEASE_CANDIDATE = PASS`. This is a sealed validation
baseline, not an assertion that every scientific value is independently validated
or that the final product is release-ready. `INITIAL_RELEASE_COMPLETE = NO` and
`FINAL_PRODUCT_RELEASE_READY = NO`.

## Closure

- Reconciled Phase 11-0 governance, Phase 11-1 provenance/fixture records,
  Phase 11-2 golden benchmarks, Phase 11-3 Linux/Windows replay, and Phase
  11-4 honest coverage without creating a new scientific authority.
- Preserved 62 Registry Tools, DataProfile 2.4, AnalysisPlan 0.1/0.2,
  migration `0007_phase10m1_workspace_domain`, dependencies, lockfile, APIs,
  scientific contracts, reference records, fixtures, expected values,
  tolerances, and validation levels.
- Sealed the final reference, fixture, golden benchmark, tolerance, variance,
  reproducibility, limitation, evidence-index, and Phase 12 read-only handoff
  packages under `docs/phase11/` and the Phase 11-5 evidence manifest.
- Retained the bounded evidence verdicts: 12 golden records with 8 invariant
  passes, 4 explicit reference-limited N/A cases, and 0 failures; eight
  Linux/Windows invariant replays, numeric cross-platform `NOT_APPLICABLE`, and
  V4 promotion 0; 62 Tool, 14 input, and 55 example coverage rows.

## CI And Regression

Implementation `953866ef524a7f60532d5d6326e2049b4e7d2bc0` passed exact-SHA CI
`31351418205`: Unit, PostgreSQL/Redis/MinIO service integration, Linux and
Windows replay, frontend typecheck/build, and the browser replay matrix all
passed. The lifecycle regression fix explicitly allows an empty `TASKS.md` only
after all task blocks are archived; tasks that remain still require `处理中`.

Local verification: `uv lock --check`; `uv run python -m pytest -q`
(`1287 passed, 50 skipped`); `npm --prefix apps/web test` (`449 passed`);
`npm --prefix apps/web run typecheck`; `npm --prefix apps/web run build`; focused
Phase 11-4/11-5 evidence tests (`9 passed`); generator, manifest, and
`git diff --check` all passed. The existing Plotly/glslify build warnings remain
non-fatal. `npm audit` remains unavailable because the configured mirror returns
`404_NOT_IMPLEMENTED`.

## Acceptance And Limits

`P11V5-A01` through `P11V5-A12`: expected 12, implemented 12,
missing/extra/duplicate/conflicting/shorthand 0. Reference-limited numeric cases
remain N/A; mapping-only coverage remains disclosed; input-path support remains
separate from numeric validation; screenshots, browser and service success are
not numeric reference authority; universal cross-platform numeric equivalence is
not claimed. Future Scope and Not Planned boundaries are unchanged.

## Mandatory Markers

```text
PHASE11_5_NEW_SCIENTIFIC_TOOLS = 0
PHASE11_5_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE11_5_NEW_SCIENTIFIC_BENCHMARKS = 0
PHASE11_5_NEW_REFERENCE_SOURCES = 0
PHASE11_5_NEW_CROSS_PLATFORM_CASES = 0
PHASE11_5_NEW_ARTIFACT_FAMILIES = 0
PHASE11_5_NEW_DATAPROFILE_VERSION = 0
PHASE11_5_NEW_ANALYSISPLAN_VERSION = 0
PHASE11_5_NEW_DATABASE_MIGRATIONS = 0
PHASE11_5_NEW_PUBLIC_API_FAMILIES = 0
PHASE11_5_NEW_DEPENDENCIES = 0
PHASE11_5_NEW_LLM_CALL_SITES = 0
PHASE11_5_REAL_LLM_CALLS = 0
PHASE11_5_EXTERNAL_REFERENCE_DOWNLOADS = 0
PHASE11_5_EXTERNAL_SCIENTIFIC_API_CALLS = 0
PHASE11_5_VALIDATION_LEVEL_CHANGES = 0
PHASE11_5_TOOL_COVERAGE_CHANGES = 0
PHASE11_5_INPUT_SUPPORT_CHANGES = 0
PHASE11_5_EXAMPLE_COVERAGE_CHANGES = 0
PHASE11_5_REFERENCE_MUTATIONS = 0
REGISTRY_BEFORE_11_5 = 62
REGISTRY_AFTER_11_5 = 62
DATAPROFILE_BEFORE_11_5 = 2.4
DATAPROFILE_AFTER_11_5 = 2.4
MIGRATION_AFTER_11_5 = 0007_phase10m1_workspace_domain
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
BROWSER_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO
SERVICE_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

## Queue State

Phase 11-5 is `PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT` at
`a15bf2b1913e001cc6ed7423c3f9cba295147395`; the completion record is
`5b5555de25e68780c8e0f696e12b604d0e633365`. Phase 11 is
`COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS`. Phase 12 is
`REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 13 is
`ROADMAP_APPROVED / NOT_QUEUED / NOT_EXECUTABLE`; Phase 14 is not created.

# Phase 12-0 Current UX Reality Audit + Product Experience Seal Result

## 1. Conclusion

Phase 12-0 is `PASS / PRODUCT_EXPERIENCE_AUDITED / EXPERIENCE_SEAL_PROPOSED`.
The current product was inventoried and audited across routes, user-visible
surfaces, components, journeys, scientific viewers, states, terminology,
responsive behavior, accessibility, and evidence boundaries. This result does
not mean the UI was redesigned or that the product is release-ready.

## 2. Phase 11 Baseline

Phase 11 is `COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS` and remains the
read-only scientific authority. Its sealed baseline is `5273b5e...`; the Phase
11-5 implementation `953866ef524a7f60532d5d6326e2049b4e7d2bc0` passed CI
`31351418205`. Registry 62, DataProfile 2.4, AnalysisPlan 0.1/0.2, and migration
`0007_phase10m1_workspace_domain` were preserved.

## 3. Entry Gate

Entry was verified at `8903e045cbad86ba0333ca4d009997e5132f73bc`, with matching
`origin/master`, branch `master`, clean worktree, empty queue, no Phase 12-1 or
Phase 13 task, and no production change authority. The Phase 11 authority handoff,
coverage/limitations records, and browser/service evidence roots resolved.

## 4. Repository State

The implementation commit is `0ea893bb85d6abd90ab89bc81e1606b378ea1e7f`.
The audit-only change set contains documentation, deterministic evidence tooling,
tests, persistent state, and queue metadata. Production React, CSS, backend
behavior, APIs, schemas, scientific contracts, Registry, Profile, dependencies
and lockfile are unchanged.

## 5. Production Behavior Changes

None. `PHASE12_0_PRODUCTION_UI_CHANGES = 0`,
`PHASE12_0_PRODUCTION_BEHAVIOR_CHANGES = 0`, and
`PHASE12_0_SCIENTIFIC_BEHAVIOR_CHANGES = 0`.

## 6. Scientific Authority Handoff

Phase 11 coverage, public claims, limitations, validation levels and reference
status are indexed read-only. UI labels, screenshots, service evidence and UX
matrices cannot upgrade `MAPPING_ONLY`, `NOT_APPLICABLE`, or reference-limited
records.

## 7. Phase 11 Coverage/Limit Reconciliation

The snapshot records 12 golden records, 8 invariant passes, 4 explicit N/A cases,
0 scientific failures, Linux and Windows invariant replay PASS, numeric
cross-platform validation NOT_APPLICABLE, and V4 promotions 0.

## 8. Current Route Inventory

The live source audit records `/`, `/workspaces/{workspaceId}`, loading and error
boundaries, and route-derived navigation surfaces in
`docs/phase12/evidence/phase12_0_current_ux_reality/route_inventory.json`.

## 9. UI Surface Registry

The surface registry contains 27 specialized surfaces plus route boundaries,
including Planner, upload/setup, Profile, execution, Workspace, findings,
evidence, Inspector, provenance, Report, Recipe, settings, and explicit loading,
empty, unsupported, stale and error states. `UI_SURFACE_UNCLASSIFIED = 0`.

## 10. Component Inventory

Frontend source scanning classified navigation, shell, controls, tabs, panels,
tables, charts, 3D, timeline, dialogs, drawers, status, Inspector, Evidence,
Report, Recipe, Settings and developer/audit components. `UI_COMPONENT_UNCLASSIFIED = 0`.

## 11. Current Design-System Audit

The audit records the live stylesheet and component vocabulary, including CSS
variables, hard-coded values, typography, spacing, borders, surfaces, focus,
motion, breakpoints and density. It is a reality baseline for 12-1, not a token
rewrite.

## 12. Token/Visual Vocabulary Audit

Token counts and duplicate visual patterns are captured in
`design_token_inventory.json` and `component_consistency_matrix.json`. The
result identifies uncontrolled vocabulary and duplicated viewer chrome without
changing CSS.

## 13. Information Hierarchy Audit

The current hierarchy is artifact- and implementation-aware. The sealed target
is result-first presentation with progressive disclosure: meaning and limitations
first, then scientific details, then provenance/developer detail.

## 14. Global Navigation Audit

The audit covers current navigation entry/exit and records the candidate IA
`Home / Data / Analyses / Workspaces / Reports / Settings` as ACCEPTED for 12-1
implementation review, preserving the existing URL and server authority.

## 15. Planner/Agent UX Audit

Planner context, prompt, intent, clarification, eligibility, plan and execution
surfaces are indexed. The primary friction is internal planning concepts exposed
too early; the target is a human-readable plan before developer details.

## 16. Data/Profile UX

Data selection and Profile readiness are audited as context for analysis. Profile
facts remain backend authority and are not recomputed or inferred by the UI.

## 17. Prompt Composer UX

Selection context, examples, input affordance, disabled/loading/error states and
mobile input behavior are covered by the Planner audit and journey evidence.

## 18. Clarification UX

Clarification is audited for human-readable rationale, valid choices, context
preservation, keyboard behavior, and leakage of raw schema/internal IDs.

## 19. Eligibility UX

Capability availability is audited as an Eligibility-derived state. Unsupported
and mismatched capabilities remain explicit; the UI cannot select a Tool from
keywords alone.

## 20. Plan UX

Plan presentation is classified into human approach first and developer detail
second. Exact Tool, Artifact, dependency and contract information remains available
through the audit/provenance layer.

## 21. Execution/Timeline UX

The audit maps existing runtime states to understandable progress language without
inventing backend states: preparing, planning, validating, queued, running,
producing results, interpreting, workspace construction, complete, partial and
failed.

## 22. Planner-to-Workspace Transition

The transition preserves one Workspace per Job and exact URL/server authority;
Phase 12-2 owns presentation improvements only.

## 23. Workspace Shell UX

Header, context rail, active panel, gallery, viewer, Inspector, findings, evidence,
report, history, save and recovery are in `workspace_audit.json`.

## 24. Workspace Navigation UX

The target Workspace IA is ACCEPTED for reviewer-gated implementation:
`Overview / Data / Analysis / Results / Findings / Evidence / Report`, with
`Provenance / Developer Details` subordinate. One active panel remains the rule.

## 25. Artifact Gallery UX

Gallery and artifact-centric navigation are audited as provenance surfaces. The
target is to present scientific result summaries first while retaining exact
Artifact identity and checksum details.

## 26. Scientific Result UX

`RESULT_FIRST_UI = YES`. Result cards expose type, summary, status, warnings and
next action; Artifact and ToolCall are deeper audit details, never removed.

## 27. Viewer Inventory

The viewer matrix covers Dataset Explorer, ML, Composition Space, Structure,
Coordination, Local Environment, XRD, Trajectory, RDF/MSD/Diffusion, Phonon/BZ,
Volumetric, Electronic Band and DOS surfaces.

## 28. Chart Viewer UX

Chart controls, legend, selection, tooltip, table alternative, export and loading
states are inventoried. 12-3 owns unified chart chrome; plots remain presentation
only.

## 29. 3D Viewer UX

Camera, cell, axes, labels, selection, fullscreen, snapshot and animation controls
are inventoried. `WEBGL_PRESENTATION_ONLY = YES`; numeric values remain Artifact
authority.

## 30. Dataset Explorer UX

Dataset context, loading, empty, ready and navigation states are included in the
surface and journey registries.

## 31. Materials ML UX

Materials ML is included in the viewer and scientific-result audit; metric/table
authority remains persisted output and the UI performs no PCA/KMeans recomputation.

## 32. Composition Space UX

Composition-space visualization and table alternatives are inventoried as data
intelligence/presentation surfaces with exact source context retained.

## 33. Structure UX

Structure summary and 3D presentation are included, with site identity and
geometry remaining backend/Artifact authority.

## 34. Coordination UX

CrystalNN and VoronoiNN are represented as separate result authorities; the audit
does not merge or rank their scientific results.

## 35. Local Environment/Polyhedra UX

Local environment, polyhedron, periodic-site and selection presentation are
covered; N1 dependency and exact identity remain unchanged.

## 36. Experimental XRD UX

Peak matching, residuals, matched/unmatched states, warnings and limitations are
audited. Peak correspondence is not presented as phase confirmation.

## 37. Trajectory UX

Trajectory context, frame/atom/time/cell semantics, heavy payload loading and
selection are included in the viewer matrix.

## 38. RDF/MSD/Diffusion UX

RDF, MSD and diffusion panels are audited for diagnostics, fit-window disclosure,
ballistic rejection and missing-time limits. The UI never recomputes or silently
fits scientific data.

## 39. Phonon/BZ UX

Phonon band/DOS combined and Brillouin Zone surfaces are inventoried with chart
and 3D presentation boundaries.

## 40. Volumetric UX

Volumetric fields, slices, isosurfaces and volume-rendering surfaces are included;
rendered views are not scientific numeric authority.

## 41. Band Structure/DOS UX

Band/DOS surfaces preserve supplied-data wording, gap/fermi/spin/projection
limitations, numeric alternatives and compatibility boundaries.

## 42. Findings UX

Finding visibility, claim hierarchy, confidence semantics, warnings, limitations
and result/evidence relationships are audited.

## 43. Evidence UX

The target trust path is `Finding -> Evidence -> Artifact -> Tool/version -> input
identity -> provenance`; screenshots and browser results remain UX evidence only.

## 44. Inspector UX

The sealed target is a three-layer Inspector: Summary, Scientific Details,
Provenance. Developer details remain accessible but subordinate.

## 45. Provenance UX

Source identity, hashes, Tool/version, parameters, units, coverage, limitations
and lineage remain discoverable through provenance surfaces.

## 46. Warning/Limitation UX

Warnings and scientific limitations must be visible near results and understandable,
not hidden in raw JSON. Phase 11 public claim/limitation records are the authority.

## 47. Report UX

Report source discovery, composition, ordering, captions, warnings, preview,
finalization, history and export are inventoried; reports compose persisted facts.

## 48. Recipe UX

Recipe is targeted to a human-readable reproducibility explanation with exact raw
declaration available. `RECIPE_EXECUTION_AUTHORITY = NONE` remains permanent.

## 49. Save/Reload/Recovery UX

Workspace history, save/reload, stale state, revision conflict, recovery and
selection restoration are represented in the error/recovery and journey matrices.

## 50. Error UX

Validation, unsupported, mismatch, provider, plan, runtime, dependency, Artifact,
Workspace, revision, Report and cross-project errors are covered with context-
preserving recovery ownership.

## 51. Empty-State UX

No-data, no-analysis, no-Workspace, no-result, no-finding, no-evidence, no-report,
unsupported, not-run and no-match states are classified for explanation and action.

## 52. Loading UX

Initial, Profile, planning, execution, Artifact, heavy viewer, interpretation and
Report loading states are catalogued, including cancellation and progress needs.

## 53. Status Vocabulary

Current status strings are indexed for duplicate meanings, technical leakage,
capitalization drift and bilingual consistency.

## 54. Terminology/i18n

The audit distinguishes fully localized, partial, English-only, developer-only,
inconsistent and not-applicable vocabulary. No new i18n infrastructure was added.

## 55. Provider/Settings UX

Current provider and secret-handling policy was audited from repository authority;
no frontend secret leakage or provider policy change is proposed.

## 56. Accessibility

Keyboard, focus, semantics, status announcements, table/chart/3D alternatives,
reduced motion, contrast, zoom and touch targets are covered. The target is
WCAG-like AA as an engineering goal, not certification.

## 57. Responsive/Desktop

Desktop and mobile evidence infrastructure is indexed for 1440x900, 1280x720 and
390x844 where available. Mobile shares authority with desktop while changing layout.

## 58. Mobile 390x844

The canonical mobile audit preserves one active panel, context/navigation drawer,
panel switcher and Inspector bottom-sheet patterns; it does not redesign production.

## 59. 200% Zoom

Planner, Workspace, Results, Findings and Report reflow/overflow checks are part of
the accessibility backlog and evidence contract.

## 60. Reduced Motion

Reduced-motion behavior is inventoried as a Phase 12-6 requirement; no runtime
animation behavior was changed by 12-0.

## 61. Browser Matrix

The implementation CI replayed Chromium, Firefox, WebKit and 390x844 coverage.
Browser PASS is presentation/interaction evidence and not numeric science evidence.

## 62. Canonical User Journeys

Eleven journeys cover new data, natural-language analysis, professional analysis,
result understanding, Report, historical recovery, unsupported input, partial
execution, provider setup, mobile inspection and developer provenance.

## 63. Interaction Baseline

Route/panel transitions, click/keyboard proxies, scroll and internal-identifier
visibility are recorded as automated interaction proxies, not human usability study
claims.

## 64. UX Problem Matrix

Ten problems are captured with evidence, consequence, viewport/input scope,
acceptance method and owner. `UX_PROBLEM_UNASSIGNED = 0`.

## 65. P0/P1/P2/P3 Distribution

Distribution is P0=0, P1=6, P2=4, P3=0. P1/P2 findings are backlog work, not
12-0 blockers; no P0 scientific misrepresentation was found by this audit.

## 66. Product Experience Principles

Sealed principles are meaning before mechanism, result before Artifact, progressive
disclosure, first-class limitations, one primary action, non-color state, exact
identity availability, shared authority across viewports, lazy heavy viewers,
context-preserving errors, subordinate developer detail and no UX-created science.

## 67. Information Architecture Decision

Global IA candidate `Home / Data / Analyses / Workspaces / Reports / Settings` and
Workspace IA `Overview / Data / Analysis / Results / Findings / Evidence / Report`
with `Provenance / Developer Details` were accepted as reviewer-gated targets.

## 68. Experience Decision Registry

P12-D001 through P12-D020 are recorded, including visual direction, disclosure,
result-first hierarchy, limitations, IA, viewer chrome, Inspector, Recipe,
terminology, accessibility, evidence methodology and phase ordering.

## 69. Phase 12-1 Handoff

12-1 receives the live token/component inventory, consistency gaps, accessibility
gaps, semantic status requirements, scientific hierarchy rules, density rules and
responsive constraints.

## 70. Phase 12-1--12-7 Backlog

The implementation backlog assigns goals, source areas, allowed/forbidden changes,
acceptance IDs, browser/mobile/accessibility/scientific-authority/evidence gates
and exit criteria to 12-1 through 12-7.

## 71. Acceptance Plan

P12X0-A01 through P12X0-A12 are implemented with no missing, extra, duplicate,
conflicting or shorthand entries. Each future subphase has eight unique acceptance
IDs, 56 total, consistently repeated in backlog, plan, lock and manifest.

## 72. Execution Lock

Phase 12 may redesign presentation, interaction, hierarchy and product experience
only after reviewer approval. Registry, Profile, Intent, Eligibility, Plan,
Validator, Runtime, Artifact, Workspace identity, Selection, Report/Recipe and
Phase 11 scientific authority are locked.

## 73. Evidence Inventory

The evidence root contains deterministic route, surface, component, token,
hierarchy, journey, viewer, state, browser, accessibility, security, Phase 11
authority snapshot, decision registry, acceptance and manifest records.

## 74. Security

No arbitrary execution, external Artifact execution, frontend scientific
recomputation, scientific authority change, real LLM, external scientific API or
secret disclosure was added. Secret scan passed.

## 75. LLM / DeepSeek

`PHASE12_0_REQUIRES_LLM = NO`, `PHASE12_0_NEW_LLM_CALL_SITES = 0`, and
`PHASE12_0_REAL_LLM_CALLS = 0`. Existing provider policy is read-only.

## 76. Database/API/Dependency Freeze

New tables, columns, migrations, public API families, Python/frontend dependencies,
lockfile changes, Registry changes and DataProfile changes are all zero.

## 77. Tests

Local backend `1290 passed, 50 skipped`; frontend `449 passed`; typecheck, build,
lock check, focused audit tests, queue lifecycle tests, evidence generator,
manifest and diff checks passed. Existing build warnings are non-fatal Plotly/glslify
dynamic-require warnings.

## 78. Service-Backed Regression

The implementation CI service job passed PostgreSQL, Redis and MinIO integration,
including zero-skipped assertion. No service behavior was added.

## 79. Browser Regression

The implementation CI browser job passed the retained Chromium, Firefox, WebKit,
390x844 and professional Phase 10 replay matrix with no audit-induced production
change.

## 80. npm Audit

`npm audit = UNAVAILABLE`: the configured mirror returns `404_NOT_IMPLEMENTED`.
Lock consistency, dependency installation, frontend tests, typecheck and build pass.

## 81. Files Changed

See commit `0ea893bb85d6abd90ab89bc81e1606b378ea1e7f` and the Phase 12 evidence
manifest. Changes are limited to audit tooling/tests, docs, persistent state and
queue lifecycle records.

## 82. Acceptance Registry

P12X0-A01..A12: expected 12, implemented 12, missing 0, extra 0, duplicate 0,
conflicting 0, shorthand 0.

## 83. Implementation Commit

`0ea893bb85d6abd90ab89bc81e1606b378ea1e7f`.

## 84. Implementation CI

Exact-SHA CI `31354589883` completed successfully. This is the only CI result
waited for in this phase.

## 85. Failed Candidates

No failed Phase 12-0 implementation candidate exists.

## 86. Completion Record

This result is the completion record. It is committed directly after implementation
CI success under the authorized lifecycle policy.

## 87. Queue Archive

After this completion commit, only the completed Phase 12-0 task is removed from
`TASKS.md`; no Phase 12-1 or Phase 13 task is created. The lifecycle wording is
`IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI`, `COMPLETION_RECORDED`, `QUEUE_ARCHIVED`.

## 88. Queue State

Final state: Phase 12-0 `PASS / PRODUCT_EXPERIENCE_AUDITED /
EXPERIENCE_SEAL_PROPOSED / QUEUE_ARCHIVED`; Phase 12 is
`IN_PROGRESS / UX_REALITY_AUDITED / AWAITING_DESIGN_SYSTEM_IMPLEMENTATION_APPROVAL`;
Phase 12-1 is `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 13 is approved,
not queued and not executable; TASK_BLOCK_COUNT=0.

## 89. Phase 12-1 Reviewer Gate

Phase 12-1 remains `REVIEWER_GATE / AWAITING REVIEWER PROMPT` and
`PHASE_12_1_EXECUTABLE_TASK_CREATED = NO`.

## 90. Final Repository State

Registry=62, DataProfile=2.4, migration=`0007_phase10m1_workspace_domain`,
`PHASE14_CREATED = NO`, `PHASE12_0_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0`,
`UI_SURFACE_UNCLASSIFIED = 0`, `UI_COMPONENT_UNCLASSIFIED = 0`,
`CANONICAL_JOURNEYS_UNAUDITED = 0`, `PHASE12_IMPLEMENTATION_CRITICAL_TBD = 0`.
Phase 11 authority mutations are 0. The repository remains subject to the
reviewer gate before any 12-1 production implementation.

## Mandatory Markers

```text
PHASE12_0_PRODUCTION_UI_CHANGES = 0
PHASE12_0_PRODUCTION_BEHAVIOR_CHANGES = 0
PHASE12_0_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_0_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_0_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_0_NEW_ARTIFACT_FAMILIES = 0
PHASE12_0_NEW_DATAPROFILE_VERSION = 0
PHASE12_0_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_0_NEW_DATABASE_MIGRATIONS = 0
PHASE12_0_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_0_NEW_DEPENDENCIES = 0
PHASE12_0_NEW_LLM_CALL_SITES = 0
PHASE12_0_REAL_LLM_CALLS = 0
PHASE12_0_EXTERNAL_SCIENTIFIC_API_CALLS = 0
PHASE12_0_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
PHASE11_SCIENTIFIC_BASELINE_MUTATIONS = 0
PHASE11_TOOL_COVERAGE_MUTATIONS = 0
PHASE11_INPUT_SUPPORT_MUTATIONS = 0
PHASE11_VALIDATION_LEVEL_MUTATIONS = 0
PHASE11_LIMITATION_MUTATIONS = 0
PHASE11_PUBLIC_CLAIM_MUTATIONS = 0
UI_SURFACE_UNCLASSIFIED = 0
UI_COMPONENT_UNCLASSIFIED = 0
UX_PROBLEM_UNASSIGNED = 0
CANONICAL_JOURNEYS_UNAUDITED = 0
PHASE12_IMPLEMENTATION_CRITICAL_TBD = 0
PHASE12_1_EXECUTABLE_TASK_CREATED = NO
PHASE13_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #3 Result

状态：PASS / DURABLE_UPLOAD_TO_WORKER_HANDOFF_CLOSED / REAL_PROCESS_BOUNDARY_D0_PASS

完成时间：2026-08-12 10:01:40 +08:00

P13-R3-001 根因：真实 HTTP Phase2 upload 只把 normalized source exports 写入上传进程的 LocalFileArtifactStorage 与内存 DatasetRecord；Planner/Worker 重新加载的 SQL Dataset 没有 normalizedExports 等 durable references，fresh Worker 因而在首个 ToolCall 前以 `Unknown input ref: profile` 失败。

修复：复用现有 PostgreSQL `datasets.metadata_json`、`data_profiles.profile_json` 与 MinIO source payload authority，在 production upload 内完成 exact manifest/Profile/source persistence；Planner enqueue 前校验 durable root inputs，fresh Worker 只从 durable refs 重建，不使用手工 preload、runtime reparse、latest/filename/fuzzy fallback 或 Redis scientific payload。

Schema decision：`EXISTING_SCHEMA_SUFFICIENT`；migration 仍为 `0007_phase10m1_workspace_domain`。科学 Adapter、算法、单位、容差、Tool Registry、Artifact family 与 public API 未改变。

D0：真实 `/datasets/upload`、PostgreSQL、MinIO、自然语言 Intent、Eligibility、Planner、PlanValidator、Job、Redis enqueue 后销毁上传进程状态；fresh QueueWorkerRuntime exact-resolve root inputs，创建真实 ToolCall，执行 registered Adapter 并持久化首个 Artifact。missing object、hash mismatch、cross-project、stale Profile 均 typed reject。

验证：Level C `7/7` PASS；Level C2 `7/7` PASS；D0 PASS；后端 `1386 passed, 52 skipped`；前端 `456 passed`；typecheck/build/lock/diff PASS；PostgreSQL/Redis/MinIO required skips `0`；Chromium/Firefox/WebKit/390x844 PASS；Linux/Windows replay PASS；security/secret scan/manifest PASS；npm audit 因 configured mirror `NOT_IMPLEMENTED` 为 `UNAVAILABLE`。

实现候选：`5b2f62e0c9ad9861f12bdc82a4bb632f1a5eaf51`，CI `31553548486` FAILED。失败根因是 service-backed tests 全部通过后 workflow 仍要求 superseded test name；产品/D0 测试未失败。Fix-forward implementation SHA：`88103ff61584ba81a01ab0e5ebf2adbbc09275e1`，exact-SHA CI `31553972770` PASS。

Hash audit：Fact Model impact `NO`，current `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`；Scope Baseline impact `NO`，current `eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94`；determinism PASS。

```text
PHASE_13_1_FIX_FORWARD_3 = PASS
P13_R3_001 = CLOSED
REAL_UPLOAD_TO_FRESH_WORKER_D0 = PASS
UPLOAD_PROCESS_MEMORY_DEPENDENCY = 0
MANUAL_NORMALIZED_EXPORT_PRELOAD = 0
RUNTIME_REPARSE_FALLBACK = 0
FIRST_REAL_TOOLCALL_CREATED = YES
FIRST_REGISTERED_ADAPTER_EXECUTED = YES
FIRST_REAL_ARTIFACT_PERSISTED = YES
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_2_ATTEMPT_2 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_3 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_4 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
PHASE13_2_ATTEMPT_4_EXECUTABLE_TASK_CREATED = NO
PHASE13_2_DEMOS_EXECUTED = 0
P13X2_ACCEPTANCE = 0/8
FIX_FORWARD_3_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```


# Phase 13-1 Zero-Gap Verification Closure Result

## 1. Conclusion

Phase 13-1 is `PASS / ZERO_GAP_VERIFICATION_CLOSED`. The corrected Phase 13-0
zero-gap conclusion was independently replayed without production or scientific
changes. Phase 13-2 demos remain unexecuted.

## 2. Entry And Authority

- Entry HEAD/origin: `7bf991c6524db0544f8e97024b6a5d30868ebaf5`.
- Phase 13-0 Fact Model: `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
- Corrected scope baseline: `93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627`.
- Phase 12 baseline: `29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4`.
- AnalysisIntent remains `1.0`: one clarification round, three questions, typed
  `CLARIFICATION_NOT_ALLOWED` for a second attempt.

## 3. Integration Seam Verification

The canonical matrix classifies 30 seams. Twenty-seven are `VERIFIED`; three
are `VERIFIED_WITH_EXPLICIT_LIMIT`. `GAP_FOUND=0`, `UNCLASSIFIED=0`.
Resource/Profile/Intent/Eligibility/Planner/Plan/Validator/Queue/Runtime/
Registry/Adapter/persistence/Artifact/Workspace/Interpretation/Evidence/
Provenance/Report/Recipe/recovery/isolation/security paths all resolve.

## 4. Registry And Runtime

- Registry: `62` unique versioned Tool identities.
- Runtime Adapter bindings: `51`.
- Explicit mapping-only/unavailable entries: `11`.
- Registry promotions or availability mutations: `0`.
- DataProfile `2.4`; AnalysisPlan `0.1 / 0.2`; migration
  `0007_phase10m1_workspace_domain` unchanged.

## 5. Seven-Demo Preflight

All seven canonical contracts are `READY_WITH_EXPLICIT_NONBLOCKING_LIMIT`:
Dataset Intelligence/Composition, Materials ML, Structure/coordination/local
environment/polyhedra/XRD, Trajectory/RDF/MSD/diffusion, Phonon/BZ,
Volumetric, and Electronic Band/DOS. This is contract preflight, not E2E PASS.

## 6. Fixture And Identity Integrity

All `11/11` retained fixtures exist, are retention-safe and match normalized
checksums. External downloads: `0`. Latest/fuzzy/filename/display-label/array-
position authority: `0`.

## 7. Persistence, Runtime And Security

Real PostgreSQL/Redis/MinIO, QueueWorkerRuntime, registered Adapter execution,
persisted Artifact, one Workspace per Job and persisted-fact Report/Recipe are
required for Phase 13-2. Recipe execution remains `NONE`; arbitrary code,
external Artifact execution, real LLM calls and external downloads in 13-1: `0`.

## 8. Release Gap Reconciliation

- `RELEASE_BLOCKERS = 0`
- `RELEASE_CRITICAL_INTEGRATION_GAPS = 0`
- `UNCLASSIFIED_RELEASE_GAPS = 0`
- Nonblocking limitations remain unchanged and publicly required.

## 9. Acceptance

`P13X1-A01..P13X1-A08 = 8/8 PASS`. Phase 13-2 acceptance IDs remain sealed
and unexecuted.

## 10. Tests

- Backend: `1335 passed, 50 skipped` locally; CI unit PASS.
- Frontend: `455 passed`; typecheck and production build PASS.
- Focused historical queue governance: `69 passed`.
- Phase 13-1/canonical governance: `14 passed`.
- `uv lock --check`, `git diff --check`, Linux/Windows invariant replay,
  PostgreSQL/Redis/MinIO, Chromium/Firefox/WebKit/390x844 evidence: PASS.

## 11. Commit And CI History

- Failed candidate: `800d15c0401a30507fe679dfa6dba3d539e39559`, CI
  `31459364889`; Linux checkout exposed Windows CRLF manifest byte-size drift.
- Fix-forward implementation: `d1a60955a77aec000f1e6fd630f0770db545421d`.
- Implementation exact-SHA CI: `31460352586 / success`.
- Completion terminology: `IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI` and
  `COMPLETION_RECORDED`; queue archive follows directly without a CI wait.

## 12. Mandatory Markers

```text
PHASE_13_1 = PASS
PHASE_13_1_MODE = ZERO_GAP_VERIFICATION_CLOSURE
PHASE13_1_PRODUCTION_CODE_CHANGES = 0
PHASE13_1_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE13_1_NEW_TOOLS = 0
PHASE13_1_NEW_ALGORITHMS = 0
PHASE13_1_NEW_ARTIFACT_FAMILIES = 0
PHASE13_1_NEW_DATAPROFILE_VERSION = 0
PHASE13_1_NEW_ANALYSISPLAN_VERSION = 0
PHASE13_1_NEW_MIGRATIONS = 0
PHASE13_1_NEW_PUBLIC_API_FAMILIES = 0
PHASE13_1_NEW_DEPENDENCIES = 0
PHASE13_1_NEW_LLM_CALL_SITES = 0
PHASE13_1_REAL_LLM_CALLS = 0
REGISTRY_BEFORE_13_1 = 62
REGISTRY_AFTER_13_1 = 62
DATAPROFILE_BEFORE_13_1 = 2.4
DATAPROFILE_AFTER_13_1 = 2.4
RELEASE_BLOCKERS = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
UNCLASSIFIED_RELEASE_GAPS = 0
INTEGRATION_SEAMS = 30/30 CLASSIFIED
DEMO_PREFLIGHT = 7/7 READY_WITH_EXPLICIT_NONBLOCKING_LIMIT
FIXTURE_INTEGRITY = 11/11 PASS
P13X1_ACCEPTANCE = 8/8
HANDCRAFTED_PLAN_INJECTION = 0
HANDCRAFTED_JOB_INJECTION = 0
HANDCRAFTED_ARTIFACT_INJECTION = 0
HANDCRAFTED_WORKSPACE_INJECTION = 0
HANDCRAFTED_REPORT_INJECTION = 0
PHASE13_2_DEMOS_EXECUTED = 0
PHASE13_2_DEMO_PASS_CLAIMS = 0
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 12-1 Design System 2.0 + Visual Language Result

## Conclusion
`PASS / DESIGN_SYSTEM_2_0_IMPLEMENTED / VISUAL_LANGUAGE_FOUNDATION_SEALED / QUEUE_ARCHIVED`.
This is presentation-only foundation work; Phase 12 and product release are not complete.

## Baselines and Authority
Phase 12-0 archive `d48ac5d28c53734d5f14f5e5728984f9ec4c2034` and implementation
`0ea893bb85d6abd90ab89bc81e1606b378ea1e7f` / CI `31354589883` are verified
ancestors. Entry was clean `master`, Registry 62, DataProfile 2.4, migration
`0007_phase10m1_workspace_domain`. Phase 11 remains read-only scientific authority:
12 golden records, 8 PASS_INVARIANT, 4 NOT_APPLICABLE, 0 scientific failures,
Linux/Windows invariant replay PASS, numeric cross-platform validation N/A, V4=0.

## Design System and UX Closure
DS2 version is 2.0. The implementation adds primitive/semantic tokens,
typography and density, surface/border/elevation, z-index, motion and reduced
motion, focus-visible, form/button/table/dialog primitives, and presentation-only
`StatusLabel`. Existing infrastructure was reused; no new route, framework, font,
external asset or scientific viewer semantics were added. The deterministic
evidence root is `docs/phase12/evidence/phase12_1_design_system_2_0/` and contains
the token, component, status, accessibility, browser, handoff, security and
no-change records. Semantic hash:
`2a87269216cddb1193af9a08ae7b136889ba43905532e508042b78369a68714d`.

`UX-007` is `FIXED_WITH_EVIDENCE`. Other owners remain open and visible:
12-2=2, 12-3=2, 12-4=1, 12-5=1, 12-6=2, 12-7=1. No new P0/P1 was introduced.
Global IA, Workspace IA, Planner workflow, scientific values, identity,
selection, backend, API, schema, Registry and DataProfile are unchanged.

## Acceptance and Verification
P12X1-A01 through P12X1-A08 were preserved from the canonical plan and pass 8/8:
tokens; typography/spacing/density; surfaces/elevation/motion; shared controls;
status/warning/limitation mapping; accessibility/focus/contrast/touch;
representative migration without IA/science change; and browser/evidence/
regression/lifecycle closure.

Local verification: backend `1293 passed, 50 skipped`, frontend `450 passed`,
typecheck PASS, build PASS, `uv lock --check` PASS, `git diff --check` PASS.
Chromium, Firefox, WebKit and Chromium 390x844 replay PASS with no console errors
or unapproved external requests. CI `31358512349` passed all five jobs:
Unit, frontend typecheck/build and retained browser replay, service-backed
PostgreSQL/Redis/MinIO, and Linux/Windows replay. `npm audit = UNAVAILABLE`
because the configured mirror returns `404_NOT_IMPLEMENTED`.

## Required Markers
```text
PHASE12_1_DESIGN_SYSTEM_VERSION = 2.0
PHASE12_1_PRODUCTION_UI_CHANGES = YES_PRESENTATION_ONLY
PHASE12_1_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_1_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_1_GLOBAL_IA_CHANGES = 0
PHASE12_1_WORKSPACE_IA_CHANGES = 0
PHASE12_1_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_1_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_1_NEW_ARTIFACT_FAMILIES = 0
PHASE12_1_NEW_DATAPROFILE_VERSION = 0
PHASE12_1_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_1_NEW_DATABASE_MIGRATIONS = 0
PHASE12_1_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_1_NEW_PYTHON_DEPENDENCIES = 0
PHASE12_1_NEW_FRONTEND_DEPENDENCIES = 0
PHASE12_1_LOCKFILE_CHANGES = 0
PHASE12_1_NEW_LLM_CALL_SITES = 0
PHASE12_1_REAL_LLM_CALLS = 0
PHASE12_1_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
DESIGN_SYSTEM_TOKEN_REGISTRY_COMPLETE = YES
UNCLASSIFIED_LEGACY_TOKENS = 0
UNCONTROLLED_HARDCODED_DESIGN_VALUES = 0
UI_COMPONENT_MIGRATION_UNCLASSIFIED = 0
UNMAPPED_USER_VISIBLE_STATUS_FAMILIES = 0
NEW_SHARED_CONTROLS_KEYBOARD_OPERABLE = PASS
NEW_SHARED_CONTROLS_FOCUS_VISIBLE = PASS
ICON_ONLY_CONTROLS_ACCESSIBLE_NAME = PASS
STATUS_COLOR_ONLY_MEANING = 0
REDUCED_MOTION_FOUNDATION = PASS
MOBILE_TOUCH_TARGET_FOUNDATION = PASS
CONTRAST_FOUNDATION = PASS
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
SUPPORTED_EQUALS_VALIDATED = NO
MAPPING_ONLY_VISUAL_UPGRADE = 0
NOT_APPLICABLE_VISUAL_UPGRADE = 0
V4_VISUAL_FABRICATION = 0
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
REGISTRY_BEFORE_12_1 = 62
REGISTRY_AFTER_12_1 = 62
DATAPROFILE_BEFORE_12_1 = 2.4
DATAPROFILE_AFTER_12_1 = 2.4
MIGRATION_AFTER_12_1 = 0007_phase10m1_workspace_domain
PHASE12_1_OWNED_PROBLEMS = UX-007
PHASE12_1_OWNED_PROBLEM_COUNT = 1
PHASE12_1_OWNED_PROBLEMS_CLOSED = 1
PHASE12_1_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_1 = 0
P12X1_ACCEPTANCE = 8/8
```

## Lifecycle, Handoffs and Final State
Implementation commit `60269556f70f07014224a801150f214887a56ee5` was verified by
exact-SHA CI `31358512349`. Completion record was committed directly after that
single CI confirmation, then only the Phase 12-1 task was archived directly;
completion/archive CI was not awaited. `COMPLETION_RECORDED = YES` and
`QUEUE_ARCHIVED = YES`. Phase 12-2 is `REVIEWER_GATE / AWAITING REVIEWER PROMPT`;
Phase 13 is approved, not queued and not executable; Phase 14 was not created.

# Phase 12-2 Global Navigation + Planner / Agent Experience Result

## Conclusion
PASS. The existing product shell now exposes the approved global IA and the
Planner explains the current journey in user language while retaining exact
developer/audit details. This is a presentation and interaction change only;
Phase 12-3 remains reviewer-gated.

## Baseline and Authority
Phase 12-1 baseline: `60269556f70f07014224a801150f214887a56ee5`, CI
`31358512349` PASS. Registry remains 62, DataProfile remains 2.4, and the
migration head remains `0007_phase10m1_workspace_domain`. Existing routes `/`
and `/workspaces/{workspaceId}` remain authoritative. Workspace, selection,
scientific artifact, Report and Recipe authorities are unchanged.

## Delivered
- Global navigation: Home, Data, Analyses, Workspaces, Reports, Settings.
- Planner stage rail: data context, intent, plan, execution, results.
- Human-readable plan approach summary before exact AnalysisPlan details.
- Four-question recovery summary: what happened, why, what can be done, and
  what was preserved.
- Deterministic route/navigation/planner/problem-closure evidence and browser
  replay for Chromium, Firefox, WebKit and Chromium 390x844.
- Legacy queue governance tests now recognize the active Phase 12-2 block and
  preserve the pending Phase 12-3 block.

## Ownership and Acceptance
`UX-001` and `UX-008` are `FIXED_WITH_EVIDENCE`. UX-002/003 remain owned by
12-3; UX-004 by 12-4; UX-005 by 12-5; UX-006/009 by 12-6; UX-010 by 12-7.
`P12X2-A01` through `P12X2-A08` are implemented: `8/8`, missing `0`, extra
`0`, duplicate `0`, conflicting `0`.

## Verification
`1296 passed, 50 skipped` backend tests; `450 passed` frontend tests;
typecheck PASS; production build PASS; `uv lock --check` PASS; `git diff
--check` PASS. Browser replay reports zero console errors, page errors,
external requests and HTTP errors in all four required contexts. Scientific
frontend recomputation is `0`; no new Tool, algorithm, Artifact family,
DataProfile, API family, database migration, dependency or LLM call site was
introduced.

## Lifecycle
Implementation commit: `d046acfcb7ea7741d7cc3567565c2cce9bcb6722`.
Implementation exact-SHA CI: `31365743510` PASS.
Completion record is committed directly after the single CI confirmation;
queue archive is committed directly without another CI wait. Phase 12-2 is
`PASS / GLOBAL_NAVIGATION_AND_PLANNER_EXPERIENCE_IMPLEMENTED / QUEUE_ARCHIVED`.
Phase 12-3 is `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 13 is approved,
not queued and not executable.
# Phase 12-3 Scientific Workspace + Scientific Viewer Experience Result

## Conclusion
PASS. Phase 12-3 implements a result-first Scientific Workspace and shared
scientific-viewer chrome without changing scientific, Artifact, Selection,
Workspace, backend or API authority. This does not complete Phase 12.

## Baseline and Entry Gate
Phase 12-2 implementation `d046acfcb7ea7741d7cc3567565c2cce9bcb6722`
and CI `31365743510` are verified. Entry HEAD/origin was `b54e429`, branch
`master`, clean worktree, one authorized Phase 12-3 task after admission,
Registry 62, DataProfile 2.4 and migration
`0007_phase10m1_workspace_domain`. DS2 and Phase 11 scientific authority were
read-only dependencies.

## Workspace, Results and Viewer Delivery
- Existing persisted panels are presented as Overview, Data, Analysis
  (Plan/Execution), Results, Findings, Evidence, Report and Advanced
  (Provenance). All nine original panel kinds and exact panel URLs remain.
- Results lead with persisted result meaning, state, counts and selection
  availability before Artifact mechanics. Scientific and Developer details
  retain renderer contracts, panel IDs, compatibility and audit JSON.
- The Artifact Gallery remains metadata-first and exact. Payloads load only on
  explicit Open through scope/contract/length/checksum validation.
- Active result viewers use shared title, state, warning, focus and close
  chrome. Specialized chart/3D/trajectory/electronic controls, geometry,
  values, units, selection and series colors are unchanged.
- `UX-002` and `UX-003` are `FIXED_WITH_EVIDENCE`. UX-004 -> 12-4, UX-005 ->
  12-5, UX-006/009 -> 12-6, and UX-010 -> 12-7 remain open with their owners.

## Selection, Lifecycle and Authority
Exact compatible selection, versioned URL selection, Back/Forward/reload,
one Workspace per Job, server layout authority, cancellation, stale-response
suppression, `WorkspaceHeavyViewerLease`, inert fallback, and table/text
alternatives remain intact. No latest, fuzzy, label, filename or array-position
binding was introduced. Findings/Evidence/Inspector redesign remains Phase 12-4.

## Verification and Evidence
Local: backend `1298 passed, 50 skipped`; frontend `451 passed`; typecheck,
production build, `uv lock --check` and `git diff --check` PASS. Retained
Workspace/Artifact Gallery replay passed Chromium, Firefox, WebKit and Chromium
390x844. Deterministic evidence contains 53 hashed entries, including desktop,
mobile and partial screenshots, at
`docs/phase12/evidence/phase12_3_scientific_workspace_viewers/`.

Implementation exact-SHA CI `31370240101` passed Unit, Frontend/Typecheck/Build
and all retained browser replays, PostgreSQL/Redis/MinIO service integration,
and Linux/Windows invariant replay for
`9b38a753bda134e9c27425e1193d2980a0790731`.

`P12X3-A01` through `P12X3-A08`: `8/8`; missing/extra/duplicate/conflicting =
`0/0/0/0`. `npm audit = UNAVAILABLE` under the configured mirror policy; lock,
dependency tree and security tests pass.

## Required Markers
```text
PHASE12_3_PRODUCTION_UI_CHANGES = YES_WORKSPACE_VIEWER_PRESENTATION_ONLY
PHASE12_3_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_3_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_3_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_3_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_3_NEW_ARTIFACT_FAMILIES = 0
PHASE12_3_NEW_DATAPROFILE_VERSION = 0
PHASE12_3_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_3_NEW_DATABASE_MIGRATIONS = 0
PHASE12_3_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_3_NEW_PYTHON_DEPENDENCIES = 0
PHASE12_3_NEW_FRONTEND_DEPENDENCIES = 0
PHASE12_3_LOCKFILE_CHANGES = 0
PHASE12_3_NEW_LLM_CALL_SITES = 0
PHASE12_3_REAL_LLM_CALLS = 0
PHASE12_3_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
REGISTRY_BEFORE_12_3 = 62
REGISTRY_AFTER_12_3 = 62
DATAPROFILE_BEFORE_12_3 = 2.4
DATAPROFILE_AFTER_12_3 = 2.4
MIGRATION_AFTER_12_3 = 0007_phase10m1_workspace_domain
ONE_WORKSPACE_PER_JOB = YES
LOCAL_STORAGE_CANONICAL_AUTHORITY = NONE
SESSION_STORAGE_CANONICAL_AUTHORITY = NONE
LATEST_SCIENTIFIC_REBINDING = 0
FUZZY_SCIENTIFIC_IDENTITY = 0
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
SCIENTIFIC_COLOR_MAPPING_CHANGES = 0
INITIAL_HEAVY_PAYLOAD_REQUESTS = 0
P12X3_OWNED_PROBLEMS = UX-002, UX-003
P12X3_OWNED_PROBLEMS_CLOSED = 2
P12X3_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_3 = 0
NEW_P1_INTRODUCED_BY_12_3 = 0
P12X3_ACCEPTANCE = 8/8
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI = PASS
COMPLETION_RECORDED = YES
QUEUE_ARCHIVED = PENDING_ARCHIVE_COMMIT
```

# Phase 12-5 Report / Recipe Experience Result

## Conclusion

Phase 12-5 is PASS. Exact persisted Report/Recipe 1.0 authority now has a
human-readable, result-first composition experience without new science,
execution authority, API, migration, dependency, or LLM behavior.

## Baseline And Entry

Phase 12-4 implementation `9fac62bbb2cc9069da62370ee9d02cf3150e987a`
and CI `31379672528` were verified from archive `4417e275`. Registry remained
62, DataProfile 2.4, migration `0007_phase10m1_workspace_domain`.

## Report Experience

The metadata-only source inventory explains exact eligibility, metadata-only,
unsupported, stale, and integrity states. Selection/order/captions preserve
exact source IDs and mandatory disclosures. Drafts remain session-only;
preview writes zero records; finalization requires explicit confirmation and
creates one immutable Report/Recipe pair. History and JSON/Markdown exports use
existing server authority.

## Recipe Experience

The default view explains ordered Tool steps, expected output contracts,
dependency model, execution outcome, warnings, and limitations. Exact canonical
JSON remains available as collapsed inert text. No Run or replay action exists.

## UX Problem And Acceptance

`UX-005` is `FIXED_WITH_EVIDENCE`. `UX-006` and `UX-009` remain owned by 12-6;
`UX-010` remains owned by 12-7. `P12X5-A01` through `P12X5-A08` are 8/8.

## Verification

Local: backend `1304 passed`, frontend `453 passed`, focused evidence 3 passed,
typecheck/build/lock/diff PASS. Chromium, Firefox, WebKit, and Chromium 390x844
PASS. Exact-SHA CI `31386432220` passed Unit, frontend/build/browser, Linux and
Windows invariant replay, and PostgreSQL/Redis/MinIO with zero skipped service
tests.

## Failed Candidates

`f263d704` / CI `31382890102` failed from omitted workflow working directory.
`11eb1b3b` / CI `31383949826` failed from redundant pytest in a Node-only job.
`e535ecf2` / CI `31385082975` exposed a retained M6 replay missing the new
confirmation click. All are historical-only and were fixed forward.

## Authority And Security Markers

```text
PHASE12_5_PRODUCTION_UI_CHANGES = YES_PRESENTATION_ONLY
PHASE12_5_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_5_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_5_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_5_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_5_NEW_ARTIFACT_FAMILIES = 0
PHASE12_5_NEW_DATAPROFILE_VERSION = 0
PHASE12_5_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_5_NEW_DATABASE_MIGRATIONS = 0
PHASE12_5_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_5_NEW_DEPENDENCIES = 0
PHASE12_5_NEW_LLM_CALL_SITES = 0
PHASE12_5_REAL_LLM_CALLS = 0
PHASE12_5_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
RECIPE_EXECUTION_AUTHORITY = NONE
REPORT_SCIENTIFIC_RECOMPUTATION = 0
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
REGISTRY_BEFORE_12_5 = 62
REGISTRY_AFTER_12_5 = 62
DATAPROFILE_BEFORE_12_5 = 2.4
DATAPROFILE_AFTER_12_5 = 2.4
MIGRATION_BEFORE_12_5 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_12_5 = 0007_phase10m1_workspace_domain
PHASE12_5_OWNED_PROBLEMS = UX-005
PHASE12_5_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_5 = 0
P12X5_ACCEPTANCE = 8/8
IMPLEMENTATION_SHA = d20d0a1437844a9a69e71fba52cdf57dfd5144db
IMPLEMENTATION_CI = 31386432220 PASS
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI = PASS
COMPLETION_RECORDED = YES
QUEUE_ARCHIVED = PENDING_ARCHIVE_COMMIT
PHASE_12_6_EXECUTED_BY_12_5 = NO
```

## Lifecycle and Gate
Implementation commit `9b38a753bda134e9c27425e1193d2980a0790731`, CI
`31370240101` PASS. The completion record is committed directly after the one
required CI confirmation. Only the Phase 12-3 task is then removed in a direct
queue-archive commit, without waiting for another CI. Phase 12-4 remains
`REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 13 is approved but not queued
or executable.

# Phase 12-4 Findings / Evidence / Inspector / Provenance Experience Result

## 1. Conclusion

Phase 12-4 passes. Persisted Findings now lead through exact Evidence membership
to source Artifacts, Tool/version, Plan/Job, inputs and lineage. The Inspector is
layered as Summary, Scientific details and Provenance; developer details remain
available but subordinate.

## 2-8. Baseline, Entry And Ownership

2. Phase 12-3 baseline: implementation `9b38a753bda134e9c27425e1193d2980a0790731`, CI `31370240101` PASS.
3. Entry gate: master, clean entry worktree, HEAD/origin aligned, Phase 12-3 ancestry verified.
4. Repository state: Registry 62, DataProfile 2.4, migration `0007_phase10m1_workspace_domain`.
5. Design System authority: DS2 presentation primitives reused.
6. Phase 11 authority: read-only; no coverage or validation promotion.
7. Phase 12-4 handoff: canonical matrices and exact eight acceptance IDs resolved.
8. UX ownership: `UX-004` was the sole 12-4-owned P1 and is `FIXED_WITH_EVIDENCE`.

## 9-12. Authority Contracts

9. Production behavior changes: presentation and exact navigation only.
10. Interpretation authority: persisted `GroundedScientificInterpretation 1.0` only.
11. Claim contract: `ScientificClaim 1.0` unchanged.
12. Evidence bundle/item contracts: unchanged; exact bundle membership is validated.

## 13-23. Finding Semantics

13. Finding hierarchy: meaning, qualifier, evidence roles and exact action.
14. Claim types: Observation, Comparison, Anomaly, Warning, Scientific limitation, Recommendation and No supported conclusion remain text-qualified.
15. Qualification: DIRECT/QUALIFIED/LIMITED are labels, not fabricated probabilities.
16. Observation/comparison: rendered from persisted claim text only.
17. Warning: persistent near the affected interpretation/evidence.
18. Limitation: persistent first-class disclosure, not an ephemeral toast.
19. Recommendation: advisory and explicitly non-executable.
20. No supported conclusion: honest empty scientific outcome.
21. Partial interpretation: successful evidence scope remains visible and bounded.
22. No supported evidence: no claim is synthesized.
23. Source integrity failure: exact typed rejection; no fallback or nearest match.

## 24-36. Exact Trust Path

24. Finding to Evidence: persisted supporting/limiting/contradicting IDs only.
25. Evidence membership: bundle identity and item fields are exact-validated.
26. Supporting evidence: text role plus exact evidence selection.
27. Limiting evidence: independently visible and selectable.
28. Contradicting evidence: independently visible and selectable.
29. Evidence facts: semantic role, persisted display value and source field.
30. Numeric/unit presentation: values and units are displayed without recomputation.
31. Evidence source Artifact: exact ID/checksum/contract/version selection.
32. Source result navigation: existing Workspace panels and Selection 1.0.
33. Selection integration: `EXACT_COMPATIBLE_ONLY`.
34. Finding identity: persisted interpretation/claim IDs.
35. Evidence identity: persisted bundle/evidence item IDs.
36. Cross-panel navigation: no label, array-position, fuzzy or latest authority.

## 37-41. Inspector

37. Architecture: three progressive-disclosure layers.
38. Summary: human-readable selected-object meaning and safe actions.
39. Scientific details: exact typed facts and compatible panels.
40. Provenance: project, source scope and active panel source records.
41. Developer details: exact inert JSON remains available but collapsed by default.

## 42-55. Provenance And Compatibility

42. Provenance IA: Finding → Evidence → Artifact → Tool/version → Plan/Job → input.
43. Data source provenance: dataset/version/source scope retained.
44. Analysis context: exact Plan and Job retained.
45. Tool/version: read from persisted Evidence item.
46. Parameters: retained in existing Artifact/Inspector authority; not inferred.
47. Execution: Job/ToolCall lineage unchanged.
48. Artifact: ID, checksum and contract/version retained.
49. Evidence/claim: exact bundle, item, interpretation and claim identities retained.
50. Lineage: existing persisted references only.
51. AnalysisPlan 0.1: legacy independent/sequential semantics identified honestly.
52. AnalysisPlan 0.2: typed Artifact dependency semantics identified honestly.
53. Historical compatibility: retained tests pass.
54. Stale/missing source: explicit unavailable/error state.
55. Cross-scope rejection: project/job/bundle/item mismatch is rejected.

## 56-63. Boundaries And States

56. Wording audit: no unqualified scientific certainty or fabricated confidence.
57. Phase 11 presentation: support, validation, reproducibility and presentation remain separate.
58. Report boundary: authority/workflow unchanged; owned by 12-5.
59. Recipe boundary: non-executable authority unchanged.
60. Workspace boundary: one Workspace per Job and server/URL/memory authority unchanged.
61. Viewer boundary: no scientific viewer computation or series mapping change.
62. Loading UX: persisted reference loading has bounded status.
63. Error/recovery: failed exact source validation preserves context and does not substitute.

## 64-73. Responsive And Browser Evidence

64. Desktop 1440x900: PASS.
65. Desktop 1280x720: PASS.
66. Mobile 390x844: PASS with Context drawer and one active panel authority.
67. 200% zoom: shared trust-path matrix PASS.
68. Keyboard/focus: Finding, Evidence and Inspector paths PASS; focus restore PASS.
69. Reduced motion: PASS.
70. Accessibility foundation: non-color roles/status and 44px mobile actions PASS.
71. Browser matrix: Chromium, Firefox and WebKit PASS; console/page/external request errors 0.
72. Trust-path replay: Findings, Evidence, Inspector and Provenance screenshots retained.
73. Interaction comparison: no new execution action or route/API family.

## 74-84. Non-Change, Security And Handoff

74. Scientific payload semantic diff: 0.
75. Interpretation contract semantic diff: 0.
76. Reinterpretation: 0; production consumes persisted claims/evidence.
77. Execution growth: 0; no plan/job/queue action added.
78. Security: inert text, no Artifact HTML/JS/iframe/external URL execution; secret scan PASS.
79. LLM/DeepSeek: new call sites 0, real calls 0, provider policy unchanged.
80. Database/API/dependencies: no schema, migration, public API, dependency or lock change.
81. Registry/DataProfile: 62 and 2.4 before/after.
82. Problem closure: `UX-004` 1/1 closed; new P0/P1 0.
83. Deferred: `UX-005`→12-5, `UX-006`/`UX-009`→12-6, `UX-010`→12-7 remain typed/open.
84. Phase 12-5 handoff: exact Report/Recipe source and warning-preservation constraints recorded; task not created by 12-4.

## 85-93. Verification And Evidence

85. Backend: `1301 passed` locally; exact-SHA CI PASS.
86. Frontend: `453 passed`.
87. Typecheck: PASS.
88. Production build: PASS.
89. Service-backed: `48 passed`, `0 skipped`, `0 failed`, `0 errors`.
90. Linux/Windows sealed invariant replay: PASS.
91. npm audit: `UNAVAILABLE` under configured mirror policy; lock/dependency/security checks PASS.
92. Evidence inventory: 74 normalized files including desktop/mobile browser captures.
93. Manifest: missing 0, extra 0, hash mismatch 0, secret-bearing evidence 0.

## 94-103. Lifecycle And Final State

94. Files changed: Workspace presentation/selection, focused tests, browser harness, Phase 12 docs/evidence, persistent state and queue validators.
95. Acceptance registry: `P12X4-A01` through `P12X4-A08`, 8/8.
96. Implementation commit: `9fac62bbb2cc9069da62370ee9d02cf3150e987a`.
97. Implementation CI: `31379672528` PASS.
98. Failed implementation candidates: none.
99. Completion record: committed directly after the single required CI confirmation.
100. Queue archive: follows as a direct commit without a second CI wait.
101. Queue state at completion record: 12-4 retained as complete pending archive; 12-5/12-6 remain pending.
102. Phase 12-5 gate: reviewer prompt exists as a pending task; 12-4 does not execute it.
103. Final repository state is recorded after queue archive.

## Mandatory Markers

```text
PHASE12_4_PRODUCTION_UI_CHANGES = YES_FINDINGS_EVIDENCE_INSPECTOR_PROVENANCE_PRESENTATION
PHASE12_4_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_4_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_4_INTERPRETATION_SEMANTIC_CHANGES = 0
PHASE12_4_SCIENTIFIC_CLAIM_CONTRACT_CHANGES = 0
PHASE12_4_EVIDENCE_CONTRACT_CHANGES = 0
PHASE12_4_GROUNDING_VALIDATOR_CHANGES = 0
PHASE12_4_ARTIFACT_CONTRACT_CHANGES = 0
PHASE12_4_WORKSPACE_AUTHORITY_CHANGES = 0
PHASE12_4_SELECTION_CONTRACT_CHANGES = 0
PHASE12_4_REPORT_AUTHORITY_CHANGES = 0
PHASE12_4_RECIPE_AUTHORITY_CHANGES = 0
PHASE12_4_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_4_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_4_NEW_ARTIFACT_FAMILIES = 0
PHASE12_4_NEW_DATAPROFILE_VERSION = 0
PHASE12_4_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_4_NEW_DATABASE_MIGRATIONS = 0
PHASE12_4_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_4_NEW_DEPENDENCIES = 0
PHASE12_4_LOCKFILE_CHANGES = 0
PHASE12_4_NEW_LLM_CALL_SITES = 0
PHASE12_4_REAL_LLM_CALLS = 0
PHASE12_4_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
FINDING_TO_EVIDENCE_EXACT_LINKING = PASS
EVIDENCE_TO_ARTIFACT_EXACT_LINKING = PASS
ARTIFACT_TO_TOOL_VERSION_TRACEABILITY = PASS
INPUT_IDENTITY_TRACEABILITY = PASS
PROVENANCE_TRACEABILITY = PASS
FUZZY_FINDING_EVIDENCE_LINKING = 0
DISPLAY_LABEL_PROVENANCE_AUTHORITY = 0
ARRAY_POSITION_PROVENANCE_AUTHORITY = 0
INSPECTOR_SUMMARY_LAYER = PASS
INSPECTOR_SCIENTIFIC_DETAILS_LAYER = PASS
INSPECTOR_PROVENANCE_LAYER = PASS
DEVELOPER_DETAILS_AVAILABLE = YES
RAW_JSON_DEFAULT_PRIMARY_LAYER = NO
INSPECTOR_SCIENTIFIC_RECOMPUTATION = 0
SUPPORTED_EQUALS_VALIDATED = NO
MAPPING_ONLY_VISUAL_UPGRADE = 0
NOT_APPLICABLE_VISUAL_UPGRADE = 0
V4_VISUAL_FABRICATION = 0
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
RECOMMENDATION_EXECUTION_AUTHORITY = NONE
RECOMMENDATION_AUTO_PLAN = 0
RECOMMENDATION_AUTO_JOB = 0
RECOMMENDATION_AUTO_QUEUE = 0
REGISTRY_BEFORE_12_4 = 62
REGISTRY_AFTER_12_4 = 62
DATAPROFILE_BEFORE_12_4 = 2.4
DATAPROFILE_AFTER_12_4 = 2.4
MIGRATION_BEFORE_12_4 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_12_4 = 0007_phase10m1_workspace_domain
PHASE12_4_OWNED_PROBLEMS = UX-004
PHASE12_4_OWNED_PROBLEM_COUNT = 1
PHASE12_4_OWNED_PROBLEMS_CLOSED = 1
PHASE12_4_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_4 = 0
NEW_P1_INTRODUCED_BY_12_4 = 0
P12X4_ACCEPTANCE = 8/8
FINDINGS_KEYBOARD = PASS
EVIDENCE_KEYBOARD = PASS
INSPECTOR_KEYBOARD = PASS
INSPECTOR_FOCUS_RESTORE = PASS
FINDING_STATUS_NON_COLOR = PASS
EVIDENCE_ROLE_NON_COLOR = PASS
MOBILE_TOUCH_TARGETS = PASS
REDUCED_MOTION = PASS
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI = PASS
COMPLETION_RECORDED = YES
QUEUE_ARCHIVED = PENDING_ARCHIVE_COMMIT
```
# Phase 12-6 Responsive / Mobile / Accessibility Closure Result

## 1-9. Conclusion, Baseline, Entry, Authority, and Ownership

Phase 12-6 is `PASS / RESPONSIVE_MOBILE_ACCESSIBILITY_CLOSED /
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI / COMPLETION_RECORDED`. Phase 12-5
implementation `d20d0a1437844a9a69e71fba52cdf57dfd5144db` / CI `31386432220`
is the entry baseline. DS2 and Phase 11 remain read-only authorities. The sole
owned problems `UX-006` (P1) and `UX-009` (P2) are closed; `UX-010` remains
open with 12-7. Production changes are responsive/accessibility presentation
only.

## 10-26. Responsive and Mobile Surfaces

All inventoried responsive surfaces are classified. Global shell, Data,
Planner, clarification, Plan, execution, Workspace, Results, scientific
viewers, Findings, Evidence, Inspector, Provenance, Report and Recipe retain
their existing routes and authority. At `390x844`, the product uses one active
Workspace panel, context drawer, panel switcher and Inspector bottom sheet.
Touch controls are at least 44 CSS px; long labels and scientific identities
wrap; dense tables use bounded horizontal scroll. Mobile journeys M1-M14 are
audited with no unclassified or unaudited case.

## 27-48. Keyboard, Semantics, Zoom, Contrast, and Motion

Keyboard journeys K1-K10 pass. Skip navigation reaches the primary Planner or
active Workspace result. The data-context separator supports Arrow Left/Right
and Home/End. Dialogs, drawers and sheets trap focus, close with Escape and
restore trigger focus. Landmarks, headings, accessible names, form labels and
async live regions are present. State is not color-only. Required touch,
contrast, 200% zoom, reflow and overflow failures are zero. Forced-colors and
`prefers-reduced-motion` smoke tests pass. Screen-reader status is honestly
`PASS_BY_DOM_ARIA_AND_BROWSER_EVIDENCE`; formal certification is not claimed.

## 49-61. Scientific Visualization and State Accessibility

Tables and charts retain numeric/text alternatives. Three-dimensional surfaces
retain structured metadata, warnings, limitations and Inspector access.
Tooltips have focus/persistent equivalents; required drag behavior has keyboard
equivalence. Error, empty, loading, unsupported, stale and partial states retain
typed text. Scientific warnings and support/validation qualifiers remain
accessible. Security-tree evidence contains no secret or executable Artifact
content.

## 62-71. Non-Change, Closure, Limits, and Handoff

Scientific payload, contract, Global IA, Workspace IA, Inspector architecture,
Report and Recipe authority diffs are zero. Accepted limitations: no formal
WCAG certification and no claim that every spatial 3D interaction has an
identical screen-reader interaction. Phase 12-7 is `REVIEWER_GATE /
AWAITING REVIEWER PROMPT`, owns `UX-010`, and has no executable task.

## 72-87. Verification and Evidence

- Browser matrix: Chromium PASS, Firefox PASS, WebKit PASS, Chromium 390x844 PASS.
- Accessibility focused tests: 5 passed; component-focused suite: 60 passed.
- Backend regression: 1309 passed, 50 skipped locally; CI service-backed tests passed with zero skips.
- Frontend regression: 455 passed.
- Typecheck, production build, `uv lock --check`, `git diff --check`: PASS.
- PostgreSQL/Redis/MinIO: PASS in CI.
- Linux/Windows invariant replay: PASS.
- npm audit: UNAVAILABLE under configured mirror policy; lock and security tests PASS.
- Evidence: 54 manifest entries, missing/extra/hash mismatch = 0.
- Acceptance: `P12X6-A01` through `P12X6-A08`, 8/8.

## 88-95. Lifecycle and Final State

Failed implementation candidate `17450c3f3704a55e4302eab9f72e66821076fa1b`
/ CI `31391903172` is historical only. All non-new gates passed; the new browser
server timed out after prior dev replays replaced production `.next` output.
Corrected implementation `e2beacb0d1e60e5bfccbcd07271f47f5736a221d`
/ exact-SHA CI `31393608850` passed. This result is the direct completion record;
the next direct commit removes only the completed 12-6 queue block. No separate
completion/archive CI is awaited. Phase 12-7 and Phase 13 executable tasks are absent.

Mandatory markers:

```text
PHASE12_6_PRODUCTION_UI_CHANGES = YES_RESPONSIVE_MOBILE_ACCESSIBILITY
PHASE12_6_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_6_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_6_GLOBAL_IA_CHANGES = 0
PHASE12_6_PLANNER_SEMANTIC_CHANGES = 0
PHASE12_6_WORKSPACE_AUTHORITY_CHANGES = 0
PHASE12_6_SELECTION_SEMANTIC_CHANGES = 0
PHASE12_6_ARTIFACT_CONTRACT_CHANGES = 0
PHASE12_6_INTERPRETATION_CONTRACT_CHANGES = 0
PHASE12_6_REPORT_CONTRACT_CHANGES = 0
PHASE12_6_RECIPE_CONTRACT_CHANGES = 0
PHASE12_6_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_6_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_6_NEW_ARTIFACT_FAMILIES = 0
PHASE12_6_NEW_DATAPROFILE_VERSION = 0
PHASE12_6_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_6_NEW_DATABASE_MIGRATIONS = 0
PHASE12_6_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_6_NEW_DEPENDENCIES = 0
PHASE12_6_LOCKFILE_CHANGES = 0
PHASE12_6_NEW_LLM_CALL_SITES = 0
PHASE12_6_REAL_LLM_CALLS = 0
PHASE12_6_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
RESPONSIVE_SURFACE_UNCLASSIFIED = 0
MOBILE_CORE_WORKFLOWS_COMPLETE = YES
UNEXPECTED_PAGE_HORIZONTAL_OVERFLOW = 0
MOBILE_GLOBAL_NAVIGATION = PASS
MOBILE_PLANNER = PASS
MOBILE_WORKSPACE = PASS
MOBILE_SCIENTIFIC_VIEWERS = PASS
MOBILE_FINDINGS_EVIDENCE = PASS
MOBILE_INSPECTOR = PASS
MOBILE_REPORT_RECIPE = PASS
CORE_KEYBOARD_WORKFLOWS = PASS
VISIBLE_FOCUS_REQUIRED_CASES = PASS
FOCUS_RESTORATION_REQUIRED_CASES = PASS
ACCESSIBLE_NAME_REQUIRED_CASES = PASS
FORM_LABEL_REQUIRED_CASES = PASS
HEADING_LANDMARK_REQUIRED_CASES = PASS
ASYNC_STATUS_ANNOUNCEMENTS = PASS
STATUS_COLOR_ONLY_MEANING = 0
REQUIRED_TOUCH_TARGET_FAILURES = 0
CONTRAST_REQUIRED_FAILURES = 0
ZOOM_200_REQUIRED_FAILURES = 0
REFLOW_REQUIRED_FAILURES = 0
REDUCED_MOTION_REQUIRED_CASES = PASS
FULL_PRODUCT_ACCESSIBILITY_ENGINEERING_CLOSURE = YES
FORMAL_ACCESSIBILITY_CERTIFICATION = NO
CHART_ACCESSIBLE_DATA_ALTERNATIVE_REQUIRED_CASES = PASS
THREE_D_STRUCTURED_ALTERNATIVE_REQUIRED_CASES = PASS
PLOTLY_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
WEBGL_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
ACCESSIBLE_ALTERNATIVE_SCIENTIFIC_RECOMPUTATION = 0
SCIENTIFIC_SERIES_COLOR_SEMANTIC_CHANGES = 0
SUPPORTED_EQUALS_VALIDATED = NO
MAPPING_ONLY_VISUAL_UPGRADE = 0
NOT_APPLICABLE_VISUAL_UPGRADE = 0
V4_VISUAL_FABRICATION = 0
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO
ACCESSIBILITY_PASS_EQUALS_SCIENTIFIC_PASS = NO
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
REGISTRY_BEFORE_12_6 = 62
REGISTRY_AFTER_12_6 = 62
DATAPROFILE_BEFORE_12_6 = 2.4
DATAPROFILE_AFTER_12_6 = 2.4
MIGRATION_BEFORE_12_6 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_12_6 = 0007_phase10m1_workspace_domain
PHASE12_6_OWNED_PROBLEMS = UX-006, UX-009
PHASE12_6_OWNED_PROBLEM_COUNT = 2
PHASE12_6_OWNED_PROBLEMS_CLOSED = 2
PHASE12_6_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_6 = 0
NEW_P1_INTRODUCED_BY_12_6 = 0
P12X6_ACCEPTANCE = 8/8
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
COMPLETION_RECORDED
PHASE_12_7_EXECUTABLE_TASK_CREATED = NO
PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

# Phase 12-7 Cross-Product UX Validation + Design Evidence Closure Result

## 1. Conclusion
Phase 12-7 is `PASS / CROSS_PRODUCT_UX_VALIDATED / DESIGN_EVIDENCE_SEALED / IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI / COMPLETION_RECORDED`. Phase 12 is `COMPLETE / PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED` within explicit limits.

## 2. Phase 12-6 Baseline
Implementation `e2beacb0d1e60e5bfccbcd07271f47f5736a221d`, CI `31393608850`, completion `c861bd7`, and archive `7f47bbbcf494a4592f5c73f5471030cdae91c635` are verified.

## 3. Entry Gate
`PHASE_12_7_ENTRY_GATE = PASS`; the sole user-added queue block was admitted after the clean `7f47bbb` baseline.

## 4. Repository State
Entry branch was `master`, `HEAD == origin/master`, with only the authorized queue admission delta after task creation.

## 5. Phase 12 Authority Chain
Phase 12-0 decisions resolve through the retained 12-1 through 12-6 implementations and this final validation.

## 6. Phase 11 Scientific Authority
Registry 62, DataProfile 2.4, AnalysisPlan 0.1/0.2 and migration `0007_phase10m1_workspace_domain` remain read-only.

## 7. Design System Authority
DS2 version 2.0 remains presentation-only; no scientific identity binds to its semantic hash.

## 8. Phase 12 Decision Registry
`P12-D001` through `P12-D020`: 20 expected, 20 resolved, 0 violated.

## 9. UX Problem Final Ownership
All original owners and severities for `UX-001` through `UX-010` are retained.

## 10. UX-010 / Final Problem Closure
`UX-010` is `FIXED_WITH_EVIDENCE` through cross-product DS2 density, toolbar, status, terminology and viewport consistency validation.

## 11. Full Phase 12 Problem Reconciliation
Ten problems are closed; P0/P1/P2/P3 open counts are all zero and unassigned count is zero.

## 12. Phase 12 Acceptance Reconciliation
68 canonical IDs pass: 12 for 12-0 and 8 each for 12-1 through 12-7; missing/duplicate/conflicting counts are zero.

## 13. P12X7 Acceptance
`P12X7-A01` through `P12X7-A08` pass exactly: `P12X7_ACCEPTANCE = 8/8`.

## 14. Canonical Journey Registry
The eleven Phase 12-0 journeys A-K remain unchanged and authoritative.

## 15. Journey 1 - New Data
Data selection, Profile/readiness and eligible analysis discovery pass without inferred semantics.

## 16. Journey 2 - Natural-Language Analysis
Prompt, clarification, eligibility, human plan, execution and Workspace transition preserve context and non-ready blocking.

## 17. Journey 3 - Professional Analysis
Professional results retain dense presentation, limitations, diagnostics and exact provenance.

## 18. Journey 4 - Result Understanding
Result to Viewer to Finding/Evidence/Inspector/Provenance is meaning-first and exactly traceable.

## 19. Journey 5 - Report / Recipe
Source discovery, disclosures, preview/finalization and inert Recipe presentation pass with no generated science.

## 20. Journey 6 - Historical Recovery
Historical Workspace and records open by exact identity with no latest rebind.

## 21. Journey 7 - Unsupported Input
Typed unsupported status, explanation and supported recovery remain visible; readiness is not fabricated.

## 22. Journey 8 - Partial Execution
Successful, failed and blocked branches remain distinguishable and trustworthy disclosures persist.

## 23. Journey 9 - Provider Setup
Server-owned DeepSeek state is understandable; browser secret input and direct provider calls remain absent.

## 24. Journey 10 - Mobile Inspection
390x844 retains one active Workspace panel, context drawer, panel switcher and Inspector sheet authority.

## 25. Journey 11 - Developer Provenance
Exact identifiers and raw developer detail remain available but subordinate and inert.

## 26. Journey Aggregate
11 expected/replayed/passed; 0 failed, blocked or unaudited.

## 27. Interaction Baseline Comparison
Automation measurements remain interaction proxies; no human time-on-task or usability-study claim is made.

## 28. Product Experience Principles
All twelve sealed principles pass, including meaning before mechanism, result before Artifact and no UX-created science.

## 29. Global IA Validation
Home, Data, Analyses, Workspaces, Reports and Settings remain unchanged.

## 30. Workspace IA Validation
Overview, Data, Analysis, Results, Findings, Evidence, Report and Advanced remain unchanged with one active panel.

## 31. Planner Consistency
Human-readable stages, one primary action and context-preserving typed recovery pass.

## 32. Workspace Consistency
Server Workspace identity, URL panel/selection authority and transient memory boundaries remain exact.

## 33. Viewer Consistency
Shared title, toolbar, status, warning, loading and alternatives pass while specialized controls retain scientific semantics.

## 34. Findings / Evidence Consistency
Persisted claims and supporting/limiting/contradicting evidence retain exact membership.

## 35. Inspector Consistency
Summary, Scientific Details and Provenance remain the three layers.

## 36. Provenance Consistency
Artifact, Tool/version, input identity, lineage and hashes remain exact and subordinate.

## 37. Report / Recipe Consistency
Meaning-first report/recipe presentation retains mandatory disclosures and zero execution authority.

## 38. Terminology Consistency
18 canonical terms resolve in en-US and zh-CN with zero required inconsistency.

## 39. Status Consistency
Ten DS2 status families map with text; no color-only meaning or invented backend status exists.

## 40. Warning / Limitation Consistency
Scientific limitations remain persistent and are never reduced to dismissible toast feedback.

## 41. Design System Consistency
DS2 token, component migration and visual vocabulary audits remain complete with zero uncontrolled authority.

## 42. UI Surface Final Coverage
All Phase 12-0 surfaces retain a final disposition; `UI_SURFACE_UNCLASSIFIED = 0`.

## 43. Component Final Coverage
All components retain migration dispositions; `UI_COMPONENT_UNCLASSIFIED = 0`.

## 44. Desktop 1440x900
Chromium, Firefox and WebKit pass hierarchy, focus, wrapping, overflow and request checks.

## 45. Desktop 1280x720
Chromium passes with zero unexpected horizontal overflow.

## 46. Mobile 390x844
Chromium passes with zero required touch or overflow failures.

## 47. Keyboard
Core keyboard workflows and Planner resize Arrow/Home/End behavior pass.

## 48. Focus / Restoration
Visible focus and required restoration cases pass.

## 49. Screen Reader Semantics
Landmarks, headings, names and status semantics pass engineering checks; no formal certification is claimed.

## 50. Touch Targets
Required mobile controls meet 44x44 CSS px; failures = 0.

## 51. Contrast
Required WCAG-like AA engineering checks have zero failures; formal certification = no.

## 52. Non-Color State
`STATUS_COLOR_ONLY_MEANING = 0`.

## 53. 200% Zoom
Required action clipping and unrecoverable overflow failures = 0.

## 54. Reflow
Planner, Workspace and Report reflow; scientific tables use bounded scrolling.

## 55. Reduced Motion
All required cases pass and continuous decorative motion count is zero.

## 56. Chart Accessibility
Required chart data alternatives pass; Plotly numeric authority is none.

## 57. 3D Accessibility
Required structured alternatives pass; WebGL numeric authority is none.

## 58. Heavy Viewer Lifecycle
One active heavy viewer maximum, zero inactive requests and zero duplicate canvas/listener growth are retained.

## 59. Loading / Empty / Error States
Shared shells and context-preserving recovery remain consistent.

## 60. Unsupported / Stale / Partial States
All remain typed, text-bearing and distinct from disabled/loading states.

## 61. Before / After Evidence
Phase 12-0 is the before authority; 12-1 through 12-7 are indexed after evidence. Screenshots carry no numeric authority.

## 62. Scientific Payload Non-Change
Value, unit, claim and identity semantic differences are zero.

## 63. Frontend No-Recomputation
`PHASE12_7_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0`.

## 64. Workspace Authority Non-Change
One Workspace per Job, persistence, revision, URL and local/session storage authority remain unchanged.

## 65. Selection Authority Non-Change
Exact selection identity is retained; latest, fuzzy, filename, label and array-position authority remain absent.

## 66. Claim/Evidence Contract Non-Change
Interpretation and claim/evidence contracts changed = 0.

## 67. Report/Recipe Contract Non-Change
Report and Recipe contracts changed = 0; Recipe execution authority = none.

## 68. Phase 11 Authority Non-Change
Tool/input coverage, validation levels, public claims and scientific limitations are unchanged.

## 69. Accepted UX Limitations
No formal accessibility certification, assistive-technology study, human study or browser pixel equality is claimed.

## 70. Final Design Evidence Manifest
63 deterministic members pass with missing/extra/hash-mismatch counts zero and implementation CI `31397995499`.

## 71. Phase 12 Product Experience Baseline
`PHASE12_PRODUCT_EXPERIENCE_BASELINE = SEALED`.

## 72. Baseline Determinism
`PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4`; regeneration is stable.

## 73. Phase 13 Handoff
Seven roadmap demo families and the complete resource-to-Report/Recipe path are handed off without execution authority.

## 74. Backend Regression
Local backend: `1314 passed, 50 skipped`; the skipped service cases run separately in CI.

## 75. Frontend Regression
71 files and `455 passed`.

## 76. Typecheck
PASS.

## 77. Build
PASS; existing Plotly/glslify dynamic dependency warnings remain non-blocking.

## 78. Lock
`uv lock --check` PASS; lockfile changes = 0.

## 79. Service Regression
PostgreSQL, Redis and MinIO required integration passed with zero skipped in CI.

## 80. Linux/Windows Replay
Both sealed invariant replays pass; numeric cross-platform validation remains governed by Phase 11.

## 81. Browser Matrix
Chromium, Firefox, WebKit, Chromium 1280x720 and Chromium 390x844 pass with zero console/page/external-request errors.

## 82. Security
Arbitrary execution, active Artifact content, Recipe/recommendation execution, cross-scope leakage and secret disclosure gates pass.

## 83. Secret Scan
Secret-bearing evidence, credentials, private paths and real LLM calls = 0.

## 84. Evidence Inventory
Journey, consistency, accessibility, authority, baseline, handoff, browser and screenshot evidence is retained under the X7 evidence root.

## 85. Files Changed
Audit/evidence tooling, test-only browser replay, docs, evidence, persistent state and queue records only; production source changes = 0.

## 86. Implementation Commit
`8fb5dcbe54fbbcd32677107abb5f4117bd04948d`.

## 87. Implementation Exact-SHA CI
CI `31397995499` PASS across all required jobs.

## 88. Failed Candidates
Phase 12-7 failed candidates = none. The 12-6 historical failed candidate remains retained and non-authoritative.

## 89. Completion Record
This direct completion record follows successful implementation CI; no separate completion CI is awaited.

## 90. Queue Archive
The next direct commit removes only the completed Phase 12-7 task; no archive CI is awaited or claimed verified.

## 91. Queue State
Completion-record state retains one completed block pending immediate archive; final `TASK_BLOCK_COUNT = 0` after that direct commit.

## 92. Phase 12 Final Status
`COMPLETE / PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED`.

## 93. Phase 13 Reviewer Gate
`REVIEWER_GATE / AWAITING REVIEWER PROMPT`; executable task created = no.

## 94. Final Repository State
After the next direct archive push: `master`, `HEAD == origin/master`, clean worktree, Registry 62, DataProfile 2.4, migration 0007, empty queue.

```text
PHASE12_7_PRODUCTION_UI_CHANGES = NO
PHASE12_7_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_7_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_7_GLOBAL_IA_CHANGES = 0
PHASE12_7_WORKSPACE_IA_CHANGES = 0
PHASE12_7_PLANNER_SEMANTIC_CHANGES = 0
PHASE12_7_ARTIFACT_CONTRACT_CHANGES = 0
PHASE12_7_SELECTION_SEMANTIC_CHANGES = 0
PHASE12_7_INTERPRETATION_CONTRACT_CHANGES = 0
PHASE12_7_REPORT_CONTRACT_CHANGES = 0
PHASE12_7_RECIPE_CONTRACT_CHANGES = 0
PHASE12_7_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_7_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_7_NEW_ARTIFACT_FAMILIES = 0
PHASE12_7_NEW_DATAPROFILE_VERSION = 0
PHASE12_7_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_7_NEW_DATABASE_MIGRATIONS = 0
PHASE12_7_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_7_NEW_DEPENDENCIES = 0
PHASE12_7_LOCKFILE_CHANGES = 0
PHASE12_7_NEW_LLM_CALL_SITES = 0
PHASE12_7_REAL_LLM_CALLS = 0
PHASE12_7_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
UI_SURFACE_UNCLASSIFIED = 0
UI_COMPONENT_UNCLASSIFIED = 0
UX_PROBLEM_UNASSIGNED = 0
PHASE12_ALL_OWNED_PROBLEMS_OPEN = 0
CANONICAL_JOURNEYS_UNAUDITED = 0
PHASE12_IMPLEMENTATION_CRITICAL_TBD = 0
UNMAPPED_USER_VISIBLE_STATUS_FAMILIES = 0
NEW_P0_INTRODUCED_BY_12_7 = 0
NEW_P1_INTRODUCED_BY_12_7 = 0
PHASE12_DESIGN_SYSTEM_VERSION = 2.0
DESIGN_SYSTEM_TOKEN_REGISTRY_COMPLETE = YES
UNCLASSIFIED_LEGACY_TOKENS = 0
UNCONTROLLED_HARDCODED_DESIGN_VALUES = 0
UI_COMPONENT_MIGRATION_UNCLASSIFIED = 0
CANONICAL_JOURNEYS_EXPECTED = 11
CANONICAL_JOURNEYS_PASS = 11
CANONICAL_JOURNEYS_FAIL = 0
CANONICAL_JOURNEYS_BLOCKED = 0
MOBILE_CORE_WORKFLOWS_COMPLETE = YES
CORE_KEYBOARD_WORKFLOWS = PASS
VISIBLE_FOCUS_REQUIRED_CASES = PASS
FOCUS_RESTORATION_REQUIRED_CASES = PASS
ACCESSIBLE_NAME_REQUIRED_CASES = PASS
STATUS_COLOR_ONLY_MEANING = 0
REQUIRED_TOUCH_TARGET_FAILURES = 0
CONTRAST_REQUIRED_FAILURES = 0
ZOOM_200_REQUIRED_FAILURES = 0
REFLOW_REQUIRED_FAILURES = 0
UNEXPECTED_PAGE_HORIZONTAL_OVERFLOW = 0
REDUCED_MOTION_REQUIRED_CASES = PASS
ACCESSIBILITY_ENGINEERING_TARGET_MET = YES
FORMAL_ACCESSIBILITY_CERTIFICATION = NO
CHART_ACCESSIBLE_DATA_ALTERNATIVE_REQUIRED_CASES = PASS
THREE_D_STRUCTURED_ALTERNATIVE_REQUIRED_CASES = PASS
PLOTLY_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
WEBGL_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
SUPPORTED_EQUALS_VALIDATED = NO
REPORT_INCLUDED_EQUALS_VALIDATED = NO
RECIPE_EXISTS_EQUALS_REPRODUCIBILITY_VALIDATED = NO
ACCESSIBILITY_PASS_EQUALS_SCIENTIFIC_PASS = NO
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO
MAPPING_ONLY_VISUAL_UPGRADE = 0
NOT_APPLICABLE_VISUAL_UPGRADE = 0
V4_VISUAL_FABRICATION = 0
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
REGISTRY_BEFORE_12_7 = 62
REGISTRY_AFTER_12_7 = 62
DATAPROFILE_BEFORE_12_7 = 2.4
DATAPROFILE_AFTER_12_7 = 2.4
MIGRATION_BEFORE_12_7 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_12_7 = 0007_phase10m1_workspace_domain
PHASE12_7_OWNED_PROBLEMS = UX-010
PHASE12_7_OWNED_PROBLEM_COUNT = 1
PHASE12_7_OWNED_PROBLEMS_CLOSED = 1
PHASE12_7_OWNED_PROBLEMS_OPEN = 0
P12X7_ACCEPTANCE = 8/8
PHASE12_ALL_ACCEPTANCE = 68/68
PHASE12_PRODUCT_EXPERIENCE_BASELINE = SEALED
PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
PHASE12_BASELINE_DETERMINISM = PASS
PHASE12_FINAL_DESIGN_EVIDENCE_MANIFEST = PASS
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
COMPLETION_RECORDED
PHASE13_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
```

# Phase 13-0 Final Fact Alignment + Release Scope Seal Result

## 1. Conclusion
`PASS / FINAL_FACTS_ALIGNED / INITIAL_RELEASE_SCOPE_SEALED / COMPLETION_RECORDED`. Phase 13-0 changes no production or scientific behavior. The seven final demonstrations are precisely contracted but not executed.

## 2. Phase 12 Baseline
Phase 12 is `COMPLETE / PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED`; baseline `29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4` regenerated deterministically.

## 3. Entry Gate
Entry baseline `69d53376b188a20db2c3cc2c28824afb5971621d`, master, clean worktree, empty queue, and absent Phase 13-1/13-2/14 tasks were verified before admission.

## 4. Repository State
Phase 12-7 implementation `8fb5dcbe54fbbcd32677107abb5f4117bd04948d`, CI `31397995499`, completion `a369bf26aca1b11522aed97e5baa1fa9017d673e`, archive `69d53376b188a20db2c3cc2c28824afb5971621d` resolve and are ancestors.

## 5. Phase 13 Handoff Integrity
The unique Phase 13 final-product-closure handoff resolves to the Phase 11 and Phase 12 sealed authorities and exactly seven demo families.

## 6. Phase 11 Scientific Authority
`COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS`; baseline `5273b5e866e950c592fe757c2e7bde2d4ede9551f7eb406d0744bb6dcf7d93cb` remains read-only.

## 7. Phase 12 Product Experience Authority
Acceptance `68/68`, journeys `11/11`, UX problems `10/10 closed`; no Phase 12 baseline mutation occurred.

## 8. Registry Reconciliation
Live Registry, documented inventory and release matrix each contain 62 unique versioned Tools, assigned exactly once.

## 9. DataProfile / Analysis Contract Baseline
DataProfile `2.4`, AnalysisIntent `1.0`, EligibilityResolution `1.0`, AnalysisPlan `0.1/0.2`, migration `0007_phase10m1_workspace_domain`.

## 10. Input Support Matrix
The sealed 14-row Phase 11 matrix is retained with zero support promotions: 10 direct-supported rows, one mapping-only row and three unsupported rows.

## 11. Tool / Capability Matrix
Twenty-six release-relevant capability families reconcile all 62 Tools plus product-composition authorities.

## 12. Product Support
Product support remains independent from scientific validation, reproducibility and presentation evidence.

## 13. Scientific Validation
Golden records `12`: `8 PASS_INVARIANT`, `4 NOT_APPLICABLE`, `0 failures`; V4 promotions remain `0`.

## 14. Cross-Platform Reproducibility
Locked Linux and Windows invariant replay PASS; numeric cross-platform reference validation remains `NOT_APPLICABLE`; macOS is not a current scientific release target.

## 15. Presentation Validation
Chromium, Firefox, WebKit and Chromium `390x844` PASS as presentation authority only.

## 16. Initial Release Product Positioning
`Material Data Intelligence and Scientific Visualization Platform`, not a generic AI wrapper.

## 17. Initial Release Capability Claims
Claims cover bounded natural-language planning, deterministic registered execution, persisted Artifacts, Workspace, Evidence, Report and non-executable Recipe.

## 18. Forbidden Claims
Forbidden wording includes all-tools independent validation, all-numeric cross-platform validation, formal WCAG certification, autonomous research, arbitrary workflows, DFT/GW execution, Rietveld refinement and executable Recipes.

## 19. Known Limitations
Six explicit limitations retain V4=0, cross-platform numeric N/A, macOS scope, accessibility certification boundary, bounded 3D alternatives, and mapping-only input/example coverage.

## 20. Future Scope
Advanced diffraction, electronic, topology, defect, trajectory and transport families remain documented and unqueued.

## 21. Not Planned Scope
Arbitrary DAG/code/notebook execution, runtime replanning, RAG, marketplace, SaaS/billing/enterprise infrastructure and unrestricted providers remain Not Planned.

## 22. Provider Policy
Real provider is DeepSeek only at `https://api.deepseek.com`, models `deepseek-v4-flash` and `deepseek-v4-pro`, key source `DEEPSEEK_KEY`; Phase 13-0 made zero real calls.

## 23. Security Boundary
Artifacts and Recipes remain inert; no arbitrary Python, shell, notebook, HTML/JS, filesystem, network or remote Artifact execution authority was added.

## 24. Accessibility / Browser / Platform Claims
Accessibility engineering target and tested browser set may be stated; formal certification and universal platform/browser claims are prohibited.

## 25. Release Gap Registry
Three classified rows: two nonblocking limitations and one planned Phase 13-2 evidence gap; unclassified rows `0`.

## 26. Release Blockers
`RELEASE_BLOCKERS = 0`; `RELEASE_CRITICAL_INTEGRATION_GAPS = 0`.

## 27. Nonblocking Limitations
Two grouped nonblocking release-gap records remain disclosure-owned; the seven-demo execution evidence gap is P2 and owned by 13-2.

## 28. Seven Demo Registry
Exactly seven `REAL_USER_ENTRY_E2E` contracts are sealed; extra `0`, missing `0`, executed `0`, PASS claims `0`.

## 29. Demo 1 Contract
Dataset Intelligence + Composition Space, retained checksummed tabular fixture, natural-language entry, real Runtime/persistence.

## 30. Demo 2 Contract
Materials ML with retained checksummed dataset fixture and persisted model/evaluation products.

## 31. Demo 3 Contract
Structure + coordination + local environment + polyhedra + experimental XRD with retained structure/XRD fixtures.

## 32. Demo 4 Contract
Trajectory + RDF + MSD + diffusion with retained boundary-aware trajectory fixture.

## 33. Demo 5 Contract
Phonon + Brillouin Zone with retained phonon/structure fixtures and explicit mapping boundaries.

## 34. Demo 6 Contract
Volumetric with retained checksummed grid fixture and presentation-only WebGL authority.

## 35. Demo 7 Contract
Electronic Band + DOS with supplied electronic fixtures; no DFT/GW platform claim.

## 36. Real User Simulation Contract
Normal flow uses user-facing UI, roles, accessible names and visible semantics; internal identities are read only after flow for lineage audit.

## 37. Canonical Scientist Persona
Supported data, reasonable scientific question, no Tool-ID knowledge, result plus limitations expected.

## 38. Imperfect / Exploratory Persona
Ambiguity, limited/unsupported data, back navigation, refresh/recovery, partial execution and limitation inspection are required.

## 39. Negative Path Registry
Ambiguous Intent, unsupported capability/input, partial execution, stale recovery, provider failure and limitation-bearing Report are sealed.

## 40. No-Handcrafted-Injection Policy
Plan, Job, ToolCall, Artifact, Workspace, Finding, Evidence, Report and Recipe injection counts are all zero.

## 41. Persistence / Runtime Requirements
Real PostgreSQL, Redis, MinIO, queue/worker Runtime, registered Adapter execution, persisted Artifact and Workspace-from-real-Job are mandatory.

## 42. Provider Mode Requirements
Deterministic provider replay is release authority; one future bounded live case allows at most two calls, 60-second timeout and zero retries.

## 43. Fixture Registry
Eleven retained fixture records cover all seven demos; missing `0`, checksum mismatch `0`, external downloads `0`.

## 44. Fixture License / Checksum Integrity
Fixtures retain repository provenance/license dispositions and cross-platform-stable text checksums; binary checksums remain byte-exact.

## 45. Natural-Language Prompt Registry
Each demo has one canonical user prompt and one bounded paraphrase without Tool IDs or schema syntax.

## 46. Clarification Expectations
Applicable clarification is user-visible, bounded to two rounds and cannot be bypassed by resolved-Intent injection.

## 47. Eligibility Expectations
Tests assert capability family and acceptable Registry outcomes; they do not pass Tool IDs directly.

## 48. Plan Expectations
Required semantic steps accept AnalysisPlan `0.1/0.2`; handcrafted Plan injection is prohibited.

## 49. Artifact / Workspace Expectations
Exact Artifact kinds and lineage drive one Workspace per real Job; filename, display label, array position and latest-binding authority remain zero.

## 50. Interpretation / Finding Expectations
Grounded interpretation and Finding/Evidence are required only where current persisted contracts apply.

## 51. Report / Recipe Expectations
Reports compose persisted facts; Recipes are exact declarative manifests with execution authority `NONE`.

## 52. Phase 13 Acceptance Registry
Fifty-six unique IDs are sealed, eight per Phase 13-0 through 13-6; `P13X0-A01..A08 = 8/8`.

## 53. Phase 13 Evidence Contract
User-entry, Profile, Intent, Plan, Runtime, Artifact, Workspace, evidence, identity, persistence and presentation axes remain independent.

## 54. Phase 13 Lifecycle Contract
Implementation exact-SHA CI is required; completion and archive are direct pushes without separate CI waits; failed candidates are retained.

## 55. Initial Release Fact Model
`SEALED`; semantic hash `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.

## 56. Initial Release Scope Baseline
`SEALED`; semantic hash `8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde`.

## 57. Baseline Determinism
PASS locally and in Linux CI after canonical JSON hashing and normalized text-fixture identity.

## 58. Release Scope Drift Audit
`NONE`; capability, validation, input support, scientific semantics and public claims received zero promotion.

## 59. Phase 13-1 Handoff
`ZERO_GAP_VERIFICATION_CLOSURE`; reviewer-gated, no executable task created.

## 60. Phase 13-2 Contract Preview
Contract ready `YES`; execution ready and demo PASS remain `NO` until the Phase 13-1 reviewer gate.

## 61. Backend Baseline Regression
Local full suite: `1320 passed`, 50 service-marked skips; implementation CI Unit Tests PASS.

## 62. Frontend Baseline Regression
`455 passed`; no frontend production behavior changed.

## 63. Typecheck / Build / Lock / Diff
Typecheck, production build, `uv lock --check` and `git diff --check` PASS; lockfile changes `0`.

## 64. Service Integration
PostgreSQL + Redis + MinIO required integration job PASS with zero skipped service tests in CI.

## 65. Linux / Windows Replay
Both sealed invariant replay jobs PASS.

## 66. Browser Smoke
Chromium, Firefox, WebKit and `390x844` retained matrix PASS; seven Phase 13 demos were not executed.

## 67. Security / Secret Scan
Security and secret scan PASS; external downloads, external scientific APIs and real LLM calls `0`.

## 68. Evidence Manifest
41 deterministic members; missing `0`, extra `0`, hash mismatch `0`, unclassified `0`; implementation CI `31451202923 PASS`.

## 69. Files Changed
Only docs, persistent state, TASK queue, audit generator/tests and CI evidence placement changed; production source and lockfiles did not.

## 70. Implementation/Audit Commit
Authoritative implementation: `6217d042d0190c43144e402e4479aa9810b8e9d0`.

## 71. Implementation Exact-SHA CI
Run `31451202923` PASS: Unit, Frontend/browser/build, PostgreSQL/Redis/MinIO, Linux replay and Windows replay all success.

## 72. Failed Candidates
`c26815289b239c1169b344ac02707cd737b0b9e5` / `31449685832`: platform-specific CRLF/LF semantic hash. `0692864ff3981b0e2ee75d5ac88ee2a438da90b6` / `31450249072`: Python audit generator incorrectly placed in Node-only frontend job. Both are historical-only and fixed forward.

## 73. Completion Record
`COMPLETION_RECORDED`; this commit is pushed directly without waiting for completion-record CI.

## 74. Queue Archive
The next direct commit removes only the completed Phase 13-0 task; no archive CI wait is authorized.

## 75. Queue State
After archive: `TASK_BLOCK_COUNT = 0`; Phase 13-1 and Phase 13-2 executable tasks absent.

## 76. Phase 13-1 Reviewer Gate
`REVIEWER_GATE / AWAITING REVIEWER PROMPT`; blocker count `0`, critical integration-gap count `0`.

## 77. Final Repository State
After direct archive push: master, HEAD equals origin/master, clean worktree, Initial Release not complete, Phase 14 absent.

```text
PHASE_13_0 = PASS
PHASE_13 = IN_PROGRESS / RELEASE_SCOPE_SEALED
INITIAL_RELEASE_FACT_MODEL = SEALED
INITIAL_RELEASE_SCOPE_BASELINE = SEALED
INITIAL_RELEASE_SCOPE_BASELINE_DETERMINISM = PASS
INITIAL_RELEASE_SCOPE_BASELINE_HASH = 8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde
REGISTRY = 62
DATAPROFILE = 2.4
MIGRATION = 0007_phase10m1_workspace_domain
PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
PHASE12_BASELINE_MUTATION_BY_13_0 = 0
PHASE13_0_PRODUCTION_CODE_CHANGES = 0
PHASE13_0_BACKEND_BEHAVIOR_CHANGES = 0
PHASE13_0_FRONTEND_BEHAVIOR_CHANGES = 0
PHASE13_0_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE13_0_NEW_SCIENTIFIC_TOOLS = 0
PHASE13_0_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE13_0_NEW_ARTIFACT_FAMILIES = 0
PHASE13_0_NEW_DATAPROFILE_VERSION = 0
PHASE13_0_NEW_ANALYSISPLAN_VERSION = 0
PHASE13_0_NEW_DATABASE_MIGRATIONS = 0
PHASE13_0_NEW_PUBLIC_API_FAMILIES = 0
PHASE13_0_NEW_DEPENDENCIES = 0
PHASE13_0_LOCKFILE_CHANGES = 0
PHASE13_0_NEW_LLM_CALL_SITES = 0
PHASE13_0_REAL_LLM_CALLS = 0
PHASE13_0_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
REGISTRY_BEFORE_13_0 = 62
REGISTRY_AFTER_13_0 = 62
DATAPROFILE_BEFORE_13_0 = 2.4
DATAPROFILE_AFTER_13_0 = 2.4
MIGRATION_BEFORE_13_0 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_13_0 = 0007_phase10m1_workspace_domain
V4_BEFORE_13_0 = 0
V4_AFTER_13_0 = 0
INITIAL_RELEASE_CAPABILITY_MATRIX = SEALED
INITIAL_RELEASE_CLAIM_REGISTRY = SEALED
INITIAL_RELEASE_LIMITATION_REGISTRY = SEALED
INITIAL_RELEASE_FUTURE_SCOPE_REGISTRY = SEALED
INITIAL_RELEASE_NOT_PLANNED_REGISTRY = SEALED
PHASE13_RELEASE_GAP_REGISTRY = SEALED
PHASE13_SEVEN_DEMO_REGISTRY = SEALED
PHASE13_ACCEPTANCE_REGISTRY = SEALED
PHASE13_DEMO_FAMILIES = 7
REAL_USER_ENTRY_E2E_REQUIRED = YES
HANDCRAFTED_PLAN_INJECTION = 0
HANDCRAFTED_JOB_INJECTION = 0
HANDCRAFTED_TOOLCALL_INJECTION = 0
HANDCRAFTED_ARTIFACT_INJECTION = 0
HANDCRAFTED_WORKSPACE_INJECTION = 0
HANDCRAFTED_FINDING_INJECTION = 0
HANDCRAFTED_EVIDENCE_INJECTION = 0
HANDCRAFTED_REPORT_INJECTION = 0
HANDCRAFTED_RECIPE_INJECTION = 0
REAL_PERSISTENCE_REQUIRED = YES
REAL_RUNTIME_REQUIRED = YES
REGISTERED_ADAPTER_EXECUTION_REQUIRED = YES
WORKSPACE_FROM_REAL_JOB_REQUIRED = YES
REPORT_FROM_REAL_PERSISTED_FACTS_REQUIRED = YES
CANONICAL_SCIENTIST_PERSONA = SEALED
IMPERFECT_EXPLORATORY_PERSONA = SEALED
NEGATIVE_PATH_REGISTRY = SEALED
NATURAL_LANGUAGE_ENTRY_REQUIRED = YES_WHERE_PRODUCT_CONTRACT_APPLIES
RELEASE_BLOCKERS = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
NONBLOCKING_LIMITATIONS = 2
UNCLASSIFIED_RELEASE_GAPS = 0
PHASE13_2_DEMOS_EXECUTED = 0
PHASE13_2_DEMO_PASS_CLAIMS = 0
SUPPORTED_EQUALS_VALIDATED = NO
E2E_PASS_EQUALS_REFERENCE_VALIDATED = NO
REPORT_INCLUDED_EQUALS_VALIDATED = NO
RECIPE_EXISTS_EQUALS_REPRODUCIBILITY_VALIDATED = NO
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO
ACCESSIBILITY_PASS_EQUALS_SCIENTIFIC_PASS = NO
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
P13X0_ACCEPTANCE = 8/8
PHASE13_ACCEPTANCE_REGISTRY_EXPECTED_TOTAL = 56
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
COMPLETION_RECORDED
INITIAL_RELEASE_COMPLETE = NO
PHASE_13_1 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_1_EXECUTABLE_TASK_CREATED = NO
PHASE13_2_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
```
# Phase 13-0 Clarification Round-Limit Fact Alignment Correction Addendum

## 1. Conclusion

`PASS / FINAL_FACTS_ALIGNED / INITIAL_RELEASE_SCOPE_SEALED / FACT_ALIGNMENT_CORRECTED`.
This append-only fix-forward corrects only the Phase 13 release-contract projection.
Production AnalysisIntent behavior was already correct and was not changed.

## 2. Baseline And Authority

- Archived Phase 13-0 baseline: implementation `6217d042d0190c43144e402e4479aa9810b8e9d0`, CI `31451202923` PASS, completion `0af74ff078e1dab6324852a8329cea42bf092acb`, archive `7a554cd91b0638898bfe097972f29a097540b514`.
- Production authority: AnalysisIntent `1.0`, `MAX_CLARIFICATION_ROUNDS=1`, `MAX_CLARIFICATION_QUESTIONS=3`, second attempt typed `CLARIFICATION_NOT_ALLOWED`.
- The historical Phase 13-0 statement remains intact and is superseded by this addendum.

## 3. Correction And Occurrence Audit

All seven canonical demo contracts, the Phase 13-2 preview, acceptance wording,
real-user contract, scope, fact-model documentation and 13-1 handoff now inherit
the one-round production authority. Current canonical two-round assertions are zero;
remaining mentions are classified historical or correction/governance evidence.

## 4. Hash Impact

- `OLD_INITIAL_RELEASE_FACT_MODEL_HASH=e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`
- `FACT_MODEL_HASH_IMPACT=NO`
- `CURRENT_INITIAL_RELEASE_FACT_MODEL_HASH=e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`
- Reason: clarification fields are outside the Fact Model semantic hash dependency domain; the model references the demo registry by path.
- `OLD_INITIAL_RELEASE_SCOPE_BASELINE_HASH=8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde`
- `SCOPE_BASELINE_HASH_IMPACT=YES`
- `CURRENT_INITIAL_RELEASE_SCOPE_BASELINE_HASH=93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627`
- Reason: the Scope Baseline hashes the seven-demo registry content. The old hash is historical and superseded.
- Two generator runs and Linux/Windows CI replay produced identical current semantic hashes.

## 5. Governance And Scientific Boundaries

`ONE_ROUND_CLARIFICATION_SUCCESS=PASS`, `SECOND_ROUND_TYPED_FAILURE=PASS`,
`MAX_THREE_QUESTIONS=PASS`, and `RESOLVED_INTENT_BYPASS=0`. Seven demo families
remain sealed but unexecuted. Release blockers and release-critical integration
gaps remain zero. Registry 62, DataProfile 2.4, EligibilityResolution 1.0,
AnalysisPlan 0.1/0.2 and migration `0007_phase10m1_workspace_domain` are unchanged.

No production code, production behavior, scientific behavior, Tool, algorithm,
Artifact family, schema version, migration, API, dependency, lockfile, LLM call
site, real LLM call, external download, or frontend scientific recomputation was added.

## 6. Verification

- Local backend: `1327 passed, 50 skipped`.
- Frontend: `455 passed`; typecheck and production build PASS.
- Focused correction/governance compatibility: `82 passed`; correction suite `7 passed`.
- `uv lock --check`, `git diff --check`, docs link check and secret scan PASS.
- Linux/Windows semantic hash replay, PostgreSQL/Redis/MinIO, Chromium, Firefox,
  WebKit and Chromium `390x844`: PASS in exact-SHA CI `31455125693`.

## 7. Lifecycle And Queue

- Correction implementation: `abe4bd68363f9eb9c357a840b17d0f2c216ebfee`.
- Implementation exact-SHA CI: `31455125693` PASS.
- `CORRECTION_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI`.
- Completion is recorded by the commit containing this addendum; no completion CI wait is required.
- Phase 13-1 remains `REVIEWER_GATE / ZERO_GAP_VERIFICATION_CLOSURE / AWAITING REVIEWER PROMPT`.
- Phase 13-2 is not queued or executable; Initial Release is not complete; Phase 14 is not created.

## 8. Required Status

```text
PHASE_13_0_FACT_CORRECTION = PASS
CORRECTION_TYPE = FACT_ALIGNMENT_FIX_FORWARD
PHASE13_CLARIFICATION_MAX_ROUNDS = 1
PHASE13_CLARIFICATION_MAX_QUESTIONS = 3
PHASE13_SECOND_CLARIFICATION_ROUND = TYPED_FAILURE
CURRENT_CANONICAL_TWO_ROUND_ASSERTIONS = 0
PRODUCTION_CODE_CHANGES = 0
PRODUCTION_BEHAVIOR_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
FACT_MODEL_HASH_IMPACT = NO
INITIAL_RELEASE_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
SCOPE_BASELINE_HASH_IMPACT = YES
INITIAL_RELEASE_SCOPE_BASELINE_HASH = 93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
BASELINE_DETERMINISM = PASS
RELEASE_BLOCKERS = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
P13X0_ACCEPTANCE = 8/8
PHASE13_DEMO_FAMILIES = 7
PHASE13_2_DEMOS_EXECUTED = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
PHASE_13_0 = PASS / FINAL_FACTS_ALIGNED / INITIAL_RELEASE_SCOPE_SEALED / FACT_ALIGNMENT_CORRECTED
PHASE_13_1 = REVIEWER_GATE / ZERO_GAP_VERIFICATION_CLOSURE / AWAITING REVIEWER PROMPT
PHASE13_1_EXECUTABLE_TASK_CREATED = NO
PHASE13_2_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-2 Seven Canonical Real-User E2E Demonstrations Result

## Conclusion

Status: `FAILED / BLOCKED_BY_RELEASE_CRITICAL_INTEGRATION_DEFECTS`.

Phase 13-1 authority, both Phase 13 hashes, 11 fixture identities, all seven
demo contracts and the no-injection policy resolved. Deterministic current-code
probes then found three P0 product-entry defects before any real Job could be
created. Phase 13-2 therefore cannot honestly satisfy its seven-demo PASS gate.
No production or scientific change was made, and no demonstration PASS is
claimed.

## Entry And Attempts

- Entry HEAD/origin: `d07c8809e677049bcf651c1aa63ab04fddec1ec2`; branch `master`; clean worktree.
- Phase 13-1 implementation: `d1a60955a77aec000f1e6fd630f0770db545421d`;
  exact-SHA CI `31460352586` PASS; completion `3d9c59b`; archive `d07c8809`.
- Fact Model hash: `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
- Scope baseline hash: `93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627`.
- Current parser, DataProfile builder, AnalysisIntent, Eligibility and Planner
  were probed using every sealed fixture and canonical/alternate prompt.
- Local PostgreSQL and Redis endpoints, MinIO binary, Playwright and bounded
  DeepSeek configuration were inspected. Execution stopped before provider,
  service-backed queue/runtime and browser acceptance because the product entry
  contract had already failed.

## Release Findings

- `P13-RF-001` P0: schema/parser produce DataProfile 2.3/2.4, but Planner accepts
  only 2.0/2.1 (`PROFILE_2_REQUIRED`), blocking demos 4 and 7.
- `P13-RF-002` P0: the sealed experimental XRD JSON is parser-unsupported and
  eligibility reports `XRD_COMPARISON_SOURCE_NOT_ELIGIBLE`, blocking demo 3.
- `P13-RF-003` P0: both sealed phonon/BZ prompts return `INTENT_UNSUPPORTED`,
  blocking demo 5.
- `P13-RF-004` P1: the volumetric canonical prompt fails while its bounded
  alternate reaches `structure.volumetric_data`, requiring contract correction.

## Verification

- `uv run python scripts/generate_phase13_2_blocker_evidence.py`: PASS.
- Focused Phase 13 governance tests: `26 passed`.
- Full backend regression: `1339 passed, 50 skipped`.
- Frontend regression: `455 passed`; typecheck and production build PASS.
- `uv lock --check` and `git diff --check`: PASS.
- Production files changed: `0`; scientific files changed: `0`; dependencies,
  lockfile, database, migration, public API and Registry changes: `0`.
- Live LLM calls: `0`; external downloads: `0`; handcrafted injections: `0`.

## Status Markers

```text
PHASE_13_2 = FAILED / BLOCKED_BY_RELEASE_CRITICAL_INTEGRATION_DEFECTS
PHASE13_DEMO_FAMILIES = 7
PHASE13_2_DEMOS_EXECUTED = 0
PHASE13_2_DEMO_PASS_CLAIMS = 0
P13X2_ACCEPTANCE = 0/8
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 3
DOCUMENTATION_DEFECTS = 1
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
HANDCRAFTED_PLAN_INJECTION = 0
HANDCRAFTED_JOB_INJECTION = 0
HANDCRAFTED_TOOLCALL_INJECTION = 0
HANDCRAFTED_ARTIFACT_INJECTION = 0
HANDCRAFTED_WORKSPACE_INJECTION = 0
HANDCRAFTED_FINDING_INJECTION = 0
HANDCRAFTED_EVIDENCE_INJECTION = 0
HANDCRAFTED_REPORT_INJECTION = 0
HANDCRAFTED_RECIPE_INJECTION = 0
PHASE13_2_PRODUCTION_CODE_CHANGES = 0
PHASE13_2_SCIENTIFIC_BEHAVIOR_CHANGES = 0
REGISTRY = 62
DATAPROFILE = 2.4
MIGRATION = 0007_phase10m1_workspace_domain
INITIAL_RELEASE_COMPLETE = NO
PHASE_13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
TASK_BLOCK_COUNT = 1
REVIEWER_ACTION_REQUIRED = YES
```

# Phase 13-1 Release-Critical Product-Entry Fix-Forward Result

## 1. Conclusion

Status: `PASS / REOPENED_FIX_FORWARD / RELEASE_CRITICAL_PRODUCT_ENTRY_GAPS_CLOSED / CANONICAL_ENTRY_SLICE_7_OF_7_READY`. Historical Phase 13-1 zero-gap verification remains forensic truth but is superseded for current release authority by the stronger Phase 13-2 real-entry evidence.

## 2. Triggering Phase 13-2 Failure

Historical evidence implementation `456b698948d286d4e60dc8d6807748a97df9fb96`, CI `31482829487` PASS, retained `P13-RF-001..004`, three release-critical defects, one documentation defect, zero scientific/security defects and zero full demos executed.

## 3. Historical Authority

Original Phase 13-1 implementation `d1a60955a77aec000f1e6fd630f0770db545421d` / CI `31460352586` remains `PASS_AT_TIME`; original Phase 13-2 remains `FAILED_HISTORICAL` and its evidence was not rewritten.

## 4. Entry Gate And Queue

Entry was clean `master` at `456b698...`; one failed retained Phase 13-2 block was preserved and one fix-forward task was admitted. No rerun task was created.

## 5. Current Fact And Scope Baselines

Fact Model hash remains `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06` (`IMPACT=NO`). Scope hash `caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4` supersedes historical `93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627` (`IMPACT=YES`, deterministic Linux/Windows canonical JSON).

## 6. RF-001 Root Cause, Fix And Regression

Global Planner/interpretation gates duplicated stale `2.0/2.1` rules. One explicit shared allowlist accepts existing `2.0..2.4`, rejects future `2.5+`, and is projected exactly to PlannerWorkbench. Demo 4 profile 2.3 and Demo 7 profile 2.4 now plan successfully; stale hashes remain rejected.

## 7. RF-002 XRD Authority Decision And Resolution

Decision: `Branch B1`. The old `perfect_match.json` is an expected-result record, not user input. Demo 3 now uses the existing strict `phase10n3.experimental_xrd_resource.v1` supported-with-limits contract. Generic JSON/phonon upload support was not promoted; exact resource identity and existing XRD comparison eligibility are preserved.

## 8. RF-003 Intent Coverage

Bounded semantic mapping now recognizes supplied phonon Band/DOS plus Structure-backed Brillouin-zone context without Tool IDs or exact-prompt branches. Canonical and alternate prompts reach the intended existing Tool family; DFT phonon generation, advanced unsupported requests and unrelated substring controls remain unsupported.

## 9. RF-004 Authority Decision

Decision: `Branch B`. The old canonical wording overstated structure context; the corrected natural-language prompt asks only for supported supplied-grid slice/volume views. Canonical and alternate prompts reach `structure.volumetric_data`; Bader/topology remains Future Scope.

## 10. Finding Closure Registry

`P13-RF-001 = CLOSED_WITH_REGRESSION`; `P13-RF-002 = CLOSED_WITH_AUTHORITY_PRESERVED`; `P13-RF-003 = CLOSED_WITH_REGRESSION`; `P13-RF-004 = CLOSED`. Original severity, evidence and failure SHA remain retained with append-only closure provenance.

## 11. Canonical Product Entry Slice

Level C is exact retained fixture -> production parser or approved normalized mapper -> DataProfile -> natural-language AnalysisIntent -> bounded clarification -> Eligibility -> capability Planner -> PlanValidator -> stop before Job. Levels A/B/C PASS; Level D remains Phase 13-2.

## 12. Demo Entry Slices

Demo 1 Dataset/Composition, Demo 2 Materials ML, Demo 3 Structure/XRD, Demo 4 Trajectory analytics, Demo 5 Phonon/BZ, Demo 6 Volumetric and Demo 7 Electronic Band/DOS are `7/7 READY` and `7/7 PLAN_VALIDATED`, with zero blocked or wrong-capability results.

## 13. Negative Entry Slice And No Injection

Future Bader, unsupported input, stale Profile hash, missing resource binding and second clarification round produce typed non-ready outcomes and no Plan. Handcrafted Intent, Eligibility, Plan and Tool selection are all zero; production contains no phase/demo fixture/checksum or exact-prompt routing authority.

## 14. Release Gap And Input-Support Reconciliation

Release-critical integration gaps: `3 -> 0`; documentation defects: `1 -> 0`; scientific/security/unclassified gaps: `0`. Input-support promotions and scientific validation/V4 promotions are zero.

## 15. Scientific Authority Non-Change

Registry `62`, DataProfile `2.4`, AnalysisIntent `1.0`, EligibilityResolution `1.0`, AnalysisPlan `0.1/0.2`, migration `0007_phase10m1_workspace_domain`. No Tool, algorithm, Adapter science, Artifact family, schema version, database, API family, dependency, provider, LLM call site or frontend scientific recomputation changed.

## 16. Verification

Backend `1351 passed, 50 skipped`; frontend `456 passed`; Phase 13 governance `37 passed`; final focused fix-forward/history `16 passed`; PlannerWorkbench `32 passed`; typecheck, build, `uv lock --check`, `git diff --check`, hash determinism, manifest and secret scan PASS. npm audit is `UNAVAILABLE` because the configured mirror returns `[NOT_IMPLEMENTED]`.

## 17. Services, Browser And Platform

Exact-SHA CI passed PostgreSQL/Redis/MinIO, Chromium/Firefox/WebKit and 390x844 retained browser evidence, production build, Linux/Windows sealed replay and cross-platform fix-forward hash comparison.

## 18. Implementation And CI

Implementation SHA `2e47263ac3042663cf901a7fcb8f44e203143e2e`; exact-SHA CI `31493208538` success. Failed remediation candidates: none. Completion is recorded in the following direct commit; queue archive follows separately without CI wait.

## 19. Phase 13-2 Rerun Handoff

The corrected seven contracts, fixture registry, prompts, 7/7 entry results, negative controls, no-injection rules, current hashes and real persistence/runtime requirements are sealed. Phase 13-2 has not been rerun; `P13X2_ACCEPTANCE = 0/8`; a separate reviewer prompt is required.

## 20. Required Markers

```text
PHASE_13_1_FIX_FORWARD = PASS
REMEDIATION_TRIGGER = PHASE13_2_REAL_USER_ENTRY_FAILURE
P13_RF_001 = CLOSED
P13_RF_002 = CLOSED
P13_RF_003 = CLOSED
P13_RF_004 = CLOSED
PROFILE_PLANNER_COMPATIBILITY_DRIFT = CLOSED
XRD_INPUT_AUTHORITY_RESOLVED = YES
INPUT_SUPPORT_PROMOTIONS = 0
PHONON_BZ_INTENT_COVERAGE = PASS
VOLUMETRIC_CANONICAL_PROMPT = ALIGNED
CANONICAL_PRODUCT_ENTRY_SLICE_GATE = PASS
CANONICAL_ENTRY_SLICE_READY = 7/7
CANONICAL_ENTRY_SLICE_BLOCKED = 0
CANONICAL_ENTRY_SLICE_WRONG_CAPABILITY = 0
ENTRY_SLICE_JOB_CREATION = 0
ENTRY_SLICE_QUEUE_MESSAGES = 0
ENTRY_SLICE_TOOLCALL_CREATION = 0
ENTRY_SLICE_ARTIFACT_CREATION = 0
HANDCRAFTED_INTENT_INJECTION = 0
HANDCRAFTED_ELIGIBILITY_INJECTION = 0
HANDCRAFTED_PLAN_INJECTION = 0
HANDCRAFTED_TOOL_SELECTION = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
DOCUMENTATION_DEFECTS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
UNCLASSIFIED_RELEASE_GAPS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
PHASE13_CLARIFICATION_MAX_ROUNDS = 1
PHASE13_CLARIFICATION_MAX_QUESTIONS = 3
PHASE13_SECOND_CLARIFICATION_ROUND = TYPED_FAILURE
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
SCIENTIFIC_ADAPTER_BEHAVIOR_CHANGES = 0
NEW_ARTIFACT_FAMILIES = 0
SCIENTIFIC_VALIDATION_PROMOTIONS = 0
V4_PROMOTIONS = 0
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
NEW_DATAPROFILE_VERSION = 0
NEW_ANALYSISINTENT_VERSION = 0
NEW_ELIGIBILITY_VERSION = 0
NEW_ANALYSISPLAN_VERSION = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_PUBLIC_API_FAMILIES = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
OLD_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
FACT_MODEL_HASH_IMPACT = NO
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
OLD_SCOPE_BASELINE_HASH = 93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
SCOPE_BASELINE_HASH_IMPACT = YES
CURRENT_SCOPE_BASELINE_HASH = caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4
BASELINE_DETERMINISM = PASS
PHASE13_2_FULL_E2E_RERUN = NO
PHASE13_2_DEMOS_EXECUTED = 0
PHASE13_2_DEMO_PASS_CLAIMS = 0
P13X2_ACCEPTANCE = 0/8
PHASE13_2_RERUN_REQUIRED = YES
PHASE13_2_RERUN_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
FIX_FORWARD_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
FIX_FORWARD_COMPLETION_RECORDED
FIX_FORWARD_QUEUE_ARCHIVED
```

## 21. Direct Queue Archive Addendum

The completed Phase 13-1 fix-forward block is removed in the direct archive
commit containing this addendum. The historical failed Phase 13-2 block remains
the sole TASK block. No archive-CI verification claim is made.

```text
FAILED_RETAINED_TASK_BLOCKS = 1
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 1
PHASE13_2_RERUN_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
FIX_FORWARD_QUEUE_ARCHIVED
```
# Phase 13-2 Seven Canonical Real-User E2E Full Rerun Result

## Conclusion

`FAILED_RERUN / REVIEWER_ACTION_REQUIRED`.

Attempt 1 remains `FAILED_HISTORICAL / BLOCKED_BY_PRODUCT_ENTRY_DEFECTS`.
Phase 13-1 Fix-Forward remains PASS. Attempt 2 passed its remediation, hash and
entry gates, then stopped during a fresh seven-family production-runtime
preflight after three new P0 release-critical integration defects were observed.
No production fix was made and no full demo PASS is claimed.

## Findings

- `P13-RR-001`: Demo 5 parsed `PhononBand`/`PhononDos` exact IDs are absent from
  the production object store; registered phonon Adapters fail `Unknown input ref`.
- `P13-RR-002`: Demo 7 parsed `ElectronicBand`/`ElectronicDos` exact IDs are
  absent from the production object store; registered electronic Adapters fail
  `Unknown input ref`.
- `P13-RR-003`: Demo 3's real experimental XRD comparison rejects the real
  theoretical dependency because their wavelengths are incompatible.

All three are product integration defects. Scientific defects and security
defects remain zero.

## Execution And Authority

- Fresh runtime preflights: `7/7`.
- Full service-backed real-user demos executed: `0/7`.
- Demo PASS or explicit-limit claims: `0/7`.
- `P13X2_ACCEPTANCE = 0/8`.
- Current Fact Model hash:
  `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
- Current Scope Baseline hash:
  `caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4`.
- Registry/DataProfile/Intent/Eligibility/Plan/migration:
  `62 / 2.4 / 1.0 / 1.0 / 0.1+0.2 / 0007_phase10m1_workspace_domain`.
- Production, scientific, schema, API, dependency and provider changes: `0`.

## Verification And Lifecycle

- Focused governance: `21 passed`.
- Backend: `1356 passed, 50 skipped`.
- Frontend: `456 passed`.
- Typecheck/build/lock/diff: PASS.
- Failure evidence implementation:
  `0877450140a76ad7ecd59e99ad48f0c19c5e7059`.
- Implementation exact-SHA CI: `31497337708 / success`.
- CI jobs: Unit, Frontend/browser, Linux replay, Windows replay and
  PostgreSQL/Redis/MinIO integration all success.
- Failed candidates before evidence commit: none. One local backend command
  timed out at 120 seconds and passed when rerun with a 300-second limit.
- Completed at: `2026-08-11 21:55:28 +08:00`.

The original failed attempt evidence, remediation evidence and attempt-2
evidence remain separate. Both failed Phase 13-2 task blocks are retained.
Phase 13-3 is blocked; Initial Release is not complete; Phase 14 is absent.

```text
PHASE_13_2_RERUN = FAILED

PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_1_FIX_FORWARD = PASS
PHASE13_2_ATTEMPT_2 = FAILED_RERUN

P13_RR_001 = OPEN_REVIEWER_ACTION_REQUIRED
P13_RR_002 = OPEN_REVIEWER_ACTION_REQUIRED
P13_RR_003 = OPEN_REVIEWER_ACTION_REQUIRED

RELEASE_CRITICAL_INTEGRATION_DEFECTS = 3
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0

PHASE13_DEMO_FAMILIES = 7
FRESH_RUNTIME_PREFLIGHTS = 7/7
PHASE13_2_DEMOS_EXECUTED = 0
DEMO_PASS_OR_EXPLICIT_LIMIT = 0/7
P13X2_ACCEPTANCE = 0/8

OLD_DEMO_RESULT_AS_RERUN_PASS = 0
HANDCRAFTED_INTENT_INJECTION = 0
HANDCRAFTED_ELIGIBILITY_INJECTION = 0
HANDCRAFTED_ANALYSISPLAN_INJECTION = 0
HANDCRAFTED_JOB_INJECTION = 0
HANDCRAFTED_TOOLCALL_INJECTION = 0
HANDCRAFTED_ARTIFACT_INJECTION = 0
HANDCRAFTED_WORKSPACE_INJECTION = 0
HANDCRAFTED_REPORT_INJECTION = 0
HANDCRAFTED_RECIPE_INJECTION = 0

PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATAPROFILE_VERSION = 0
NEW_ANALYSISINTENT_VERSION = 0
NEW_ELIGIBILITY_VERSION = 0
NEW_ANALYSISPLAN_VERSION = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_PUBLIC_API_FAMILIES = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0

PHASE_13_3 = BLOCKED_BY_PHASE13_2_RERUN
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
FAILED_RETAINED_TASK_BLOCKS = 2
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 2
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #2 Result

## 1. Conclusion

`PASS / FIX_FORWARD_2 / RUNTIME_RESOURCE_RESOLUTION_CLOSED /
XRD_DEPENDENCY_COMPATIBILITY_CLOSED / CANONICAL_EXECUTION_PREFLIGHT_7_OF_7_READY`.
Phase 13-2 Attempt 3 was not executed or queued.

## 2-6. Trigger, History, Entry Gate, Queue, Baselines

Attempt 1 and Attempt 2 remain immutable failed history. Fix-Forward #1 remains
PASS. Entry was clean on `master` with two retained failed TASK blocks. Fact
Model remains `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
Scope Baseline `eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94`
supersedes `caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4`.

## 7-14. RR-001 and RR-002

Both findings shared one root cause: parsed `PhononBand`, `PhononDos`,
`ElectronicBand` and `ElectronicDos` exact IDs escaped the canonical Runtime
source-resource index and durable resolver. One bounded generic registration
mechanism now preserves exact ID, type, hash and dataset scope in immediate and
PostgreSQL/MinIO-backed resolution. Missing ID, wrong project, hash mismatch,
stale identity and wrong subtype remain rejected. Electronic spin, k-point,
band/path, DOS channel and energy-unit provenance are unchanged.

## 15-19. RR-003

Authority decision: Branch B1. `structure.xrd@0.1.0` legally binds the existing
`CuKa` configuration, not arbitrary wavelength. Demo 3's retained experimental
fixture now uses exact `1.54184 angstrom`, matching the approved theoretical
configuration. The strict mismatch case still rejects `1.5406`; no conversion,
reprojection, tolerance, peak-policy or XRD algorithm changed.

## 20-30. Findings and Level C/C2

`P13-RR-001`, `P13-RR-002`, and `P13-RR-003` are closed. Level C is `7/7`.
Level C2 is `7/7`, with eight execution-eligible root kinds audited and eight
Runtime-resolvable. Root-resolution, dependency-contract and scientific-
compatibility failures are all zero. Jobs, queue messages, ToolCalls, produced
Artifacts, Workspaces, Reports and Recipes created by C2 are all zero.

## 31-38. Authority and Hashes

No handcrafted Intent, Eligibility, Plan or Tool selection was used. Release-
critical integration gaps are zero; scientific/security/unclassified defects
are zero. Input support, capability and scientific-validation promotions are
zero. Fact Model impact is `NO`; Scope Baseline impact is `YES` because the
retained Demo 3 checksum changed. Repeated and Linux/Windows hashes are equal.
Phase 11 and Phase 12 authorities are unchanged.

## 39-49. Regression and Evidence

- Backend: `1374 passed, 50 skipped` locally.
- Frontend: `456 passed`; typecheck and build PASS.
- Focused Phase 13 C2/governance: `23 passed`.
- PostgreSQL/Redis/MinIO: `49 passed, 0 skipped` in exact-SHA CI.
- Chromium, Firefox, WebKit and 390x844 retained browser matrix: PASS.
- Linux/Windows invariant replay and semantic hash comparison: PASS.
- `uv lock --check`, `git diff --check`, security, secret scan and manifest: PASS.

## 50-59. Handoff and Lifecycle

Attempt 3 handoff is sealed and requires all seven demos from scratch under a
separate reviewer prompt. Implementation `bc6a6f525515c256c6807c71c5a5f2591607abab`
passed exact-SHA CI `31504920945`. Failed candidate `67a95c4f94088fcd1f8e351f65d617840ccd9906`
/ run `31503729464` is retained; root causes were historical evidence
regeneration and missing integration-test base-table bootstrap. Completion is
recorded here; queue archive follows in a separate direct commit.

```text
PHASE_13_1_FIX_FORWARD_2 = PASS
REMEDIATION_TRIGGER = PHASE13_2_ATTEMPT_2_RUNTIME_PREFLIGHT_FAILURE
P13_RR_001 = CLOSED
P13_RR_002 = CLOSED
P13_RR_003 = CLOSED
PARSED_RESOURCE_PERSISTENCE_AND_RUNTIME_RESOLUTION_GAP = CLOSED
XRD_DEPENDENCY_COMPATIBILITY_GAP = CLOSED
ALL_EXECUTION_ELIGIBLE_ROOT_RESOURCES_RUNTIME_RESOLVABLE = YES
UNRESOLVABLE_EXECUTION_ELIGIBLE_RESOURCE_KINDS = 0
CANONICAL_PRODUCT_ENTRY_SLICE_GATE = PASS
CANONICAL_ENTRY_SLICE_READY = 7/7
CANONICAL_EXECUTION_PREFLIGHT_GATE = PASS
CANONICAL_EXECUTION_PREFLIGHT_READY = 7/7
CANONICAL_EXECUTION_PREFLIGHT_BLOCKED = 0
ROOT_RESOURCE_RESOLUTION_FAILURES = 0
DEPENDENCY_CONTRACT_FAILURES = 0
SCIENTIFIC_COMPATIBILITY_FAILURES = 0
XRD_WAVELENGTH_MISMATCH_REJECTION = UNCHANGED
INPUT_SUPPORT_PROMOTIONS = 0
CAPABILITY_PROMOTIONS = 0
SCIENTIFIC_VALIDATION_PROMOTIONS = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
OLD_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
FACT_MODEL_HASH_IMPACT = NO
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
OLD_SCOPE_BASELINE_HASH = caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4
SCOPE_BASELINE_HASH_IMPACT = YES
CURRENT_SCOPE_BASELINE_HASH = eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94
BASELINE_DETERMINISM = PASS
REAL_LLM_CALLS = 0
PHASE13_2_ATTEMPT_3_FULL_E2E = NO
PHASE13_2_DEMOS_EXECUTED = 0
P13X2_ACCEPTANCE = 0/8
FIX_FORWARD_2_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
FIX_FORWARD_2_COMPLETION_RECORDED
PHASE13_2_ATTEMPT_3_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
```

## Phase 13-1 Fix-Forward #2 Queue Archive

Completion commit `eed9af49ce339804b6913c0f3b1fff2cc3e18ee8` was pushed directly
after implementation exact-SHA CI passed. The completed Fix-Forward #2 block
was removed from `TASKS.md`; both historical failed Phase 13-2 blocks remain
unchanged. No Attempt 3, Phase 13-3, or Phase 14 executable task was created.

```text
FIX_FORWARD_2_QUEUE_ARCHIVED
FAILED_RETAINED_TASK_BLOCKS = 2
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 2
PHASE13_2_ATTEMPT_3_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
```

# Phase 13-2 Attempt 3 Seven Canonical Real-User E2E Demonstrations Result

## Conclusion and History

`FAILED / REVIEWER_ACTION_REQUIRED`. Attempt 1 remains `FAILED_HISTORICAL`,
Fix-Forward #1 remains PASS, Attempt 2 remains `FAILED_RERUN_HISTORICAL`, and
Fix-Forward #2 remains PASS (`bc6a6f525515c256c6807c71c5a5f2591607abab`,
CI `31504920945`). Attempt 3 passed its repository, authority, Level C 7/7,
Level C2 7/7, eight-of-eight resource and service entry gates, then stopped on
a new P0 during the first fresh Level-D execution. No production repair was made.

## Fresh Execution and Finding

Demo 1 used a fresh HTTP `/datasets/upload`, retained `formulas.csv`, DataProfile
2.4, canonical natural-language prompt, AnalysisIntent 1.0, EligibilityResolution
1.0, capability Planner, PlanValidator, persisted Plan/Job and real Redis enqueue.
A newly constructed production QueueWorkerRuntime failed before ToolCall creation:

```text
TOOL_INPUT_INVALID: Unknown input ref: profile
```

`P13-R3-001` is a P0 `RELEASE_CRITICAL_INTEGRATION_DEFECT`. The upload process
contains normalized source exports, but Planner's SQL dataset lacks
`normalizedExports`; the fresh PostgreSQL/MinIO durable resolver cannot rebuild
the exact source object store. Fix-Forward #2 C2 manually persisted those exports
and did not cover the real endpoint-to-worker boundary.

Demo 1 is `FAIL_PRODUCT_INTEGRATION`; Demo 2-7 are
`NOT_EXECUTED_AFTER_P0_STOP`. Negative paths, browser-driven Attempt 3 flows,
mobile inspection and bounded live DeepSeek were not executed. Full demos are
`0/7`, old evidence reused as PASS is 0, and `P13X2_ACCEPTANCE = 0/8`.

## Authority, Regression and Lifecycle

All handcrafted injection and Runtime fallback counters are zero. No ToolCall,
Artifact, Workspace, interpretation, Finding/Evidence, Report or Recipe was
created. Registry 62, DataProfile 2.4, AnalysisIntent 1.0, EligibilityResolution
1.0, AnalysisPlan 0.1/0.2, migration 0007, Fact Model
`e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06` and
Scope Baseline `eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94`
are unchanged.

- Evidence governance: `4 passed`.
- Service reproduction: `1 passed, 0 skipped` locally.
- Backend: `1378 passed, 52 skipped`; frontend: `456 passed`.
- Typecheck, build, lock, diff, deterministic manifest, security and secret scan: PASS.
- Evidence SHA: `fc54d4eec3f537e1ad57fca8d085539e9acd1ac3`.
- Exact-SHA CI: `31511289851` PASS, including 50 zero-skip service tests,
  retained browser gates and Linux/Windows replay.
- Completion/archive SHA: not applicable; Attempt 3 failed and all three failed
  Phase 13-2 task blocks remain retained.

```text
PHASE_13_2_ATTEMPT_3 = FAILED / REVIEWER_ACTION_REQUIRED
DEMO_1_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_2_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_3_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_4_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_5_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_6_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_7_STATUS = NOT_EXECUTED_AFTER_P0_STOP
PHASE13_2_ATTEMPT_3_DEMOS_EXECUTED = 0
OLD_EVIDENCE_REUSED_AS_PASS = 0
P13X2_ACCEPTANCE = 0/8
P13_R3_001 = OPEN_REVIEWER_ACTION_REQUIRED
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 1
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
ALL_HANDCRAFTED_INJECTION_COUNTERS = 0
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94
FACT_MODEL_HASH_IMPACT_BY_ATTEMPT_3 = NO
SCOPE_BASELINE_HASH_IMPACT_BY_ATTEMPT_3 = NO
BASELINE_DETERMINISM = PASS
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
REAL_LLM_CALLS = 0
PHASE_13_3 = BLOCKED_BY_PHASE13_2_ATTEMPT_3
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
FAILED_RETAINED_TASK_BLOCKS = 3
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 3
PHASE14_CREATED = NO
```

# Phase 13-2 Attempt 4 Seven Canonical Real-User E2E Demonstrations Result

## Conclusion and History

`FAILED / REVIEWER_ACTION_REQUIRED`. Attempts 1-3 remain immutable historical
failures and Fix-Forwards 1-3 remain PASS. Attempt 4 passed repository,
authority, Level C `7/7`, Level C2 `7/7`, and real upload-to-fresh-worker D0
entry gates, then stopped on two new P0 product-integration findings during the
first fresh full demonstration. No production or scientific repair was made.

## Fresh Demo 1 and Findings

Fresh Demo 1 used the current `formulas.csv`, canonical natural-language prompt,
real HTTP upload, PostgreSQL/MinIO durable source authority, AnalysisIntent 1.0,
EligibilityResolution 1.0, capability-aware Planner, PlanValidator, persisted
Job, Redis enqueue, a fresh QueueWorkerRuntime, registered Adapter execution,
four persisted Artifacts, and Workspace projection.

- `P13-R4-001` (`CANONICAL_PROMPT_TO_SEALED_CAPABILITY_MISMATCH`): the actual
  Plan and ToolCall contain only `dataset.materials_explorer`. The sealed Demo 1
  contract also requires `dataset.composition_space`, but no such ToolCall or
  `plotly_json` Artifact was produced.
- `P13-R4-002` (`REAL_USER_REPORT_FINALIZE_BLOCKED_BY_PLAN_0_1_WORKSPACE_POLICY`):
  the Planner-produced AnalysisPlan 0.1 Workspace is `LEGACY_READ_ONLY`; the
  frontend disables Report Finalize for read-only Workspaces. A diagnostic
  direct API finalize was excluded from real-user PASS authority.

Demo 1 is `FAIL_PRODUCT_INTEGRATION`. Demo 2-7, negative scenarios, Attempt 4
browser execution, mobile inspection, and bounded live DeepSeek were not
executed after the P0 stop. Fresh demos started are `1/7`, full demos completed
are `0/7`, old evidence reused as PASS is 0, and `P13X2_ACCEPTANCE = 0/8`.

## Regression and Lifecycle

- D0: `1 passed, 0 skipped` using real PostgreSQL, Redis, and MinIO.
- Backend: `1391 passed, 52 skipped`; frontend: `456 passed`.
- Phase 13 focused/governance: `46 passed`.
- Typecheck, build, lock, diff, current Fact/Scope hash, security, secret scan,
  evidence manifest, retained browser gates, and Linux/Windows replay: PASS.
- Local failed test candidate: `1390 passed, 52 skipped, 1 failed`; root cause
  was the Attempt 4 TASK block's English status label. The queue/evidence-only
  correction passed the full rerun.
- Evidence SHA: `9b087606e1d6093e3129dc20e43020790e703a58`.
- Exact-SHA CI: `31577647965` PASS across all five required jobs.
- Completion/archive SHA: not applicable. Attempt 4 failed; all four failed
  Phase 13-2 blocks remain in `TASKS.md`.

```text
PHASE_13_2_ATTEMPT_4 = FAILED / REVIEWER_ACTION_REQUIRED
PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_1_FIX_FORWARD_1 = PASS
PHASE13_2_ATTEMPT_2 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_2 = PASS
PHASE13_2_ATTEMPT_3 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_3 = PASS
DEMO_1_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_2_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_3_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_4_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_5_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_6_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_7_STATUS = NOT_EXECUTED_AFTER_P0_STOP
PHASE13_2_ATTEMPT_4_FRESH_DEMOS_STARTED = 1
PHASE13_2_ATTEMPT_4_DEMOS_EXECUTED = 0
OLD_EVIDENCE_REUSED_AS_ATTEMPT4_PASS = 0
UPLOAD_PROCESS_MEMORY_DEPENDENCY = 0
MANUAL_NORMALIZED_EXPORT_PRELOAD = 0
RUNTIME_REPARSE_FALLBACK = 0
ALL_HANDCRAFTED_INJECTION_COUNTERS = 0
P13X2_ACCEPTANCE = 0/8
P13_R4_001 = OPEN_REVIEWER_ACTION_REQUIRED
P13_R4_002 = OPEN_REVIEWER_ACTION_REQUIRED
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 2
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
UNCLASSIFIED_RELEASE_GAPS = 0
PROVIDER_EXTERNAL_EVENTS = 0
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
FACT_MODEL_HASH_IMPACT_BY_ATTEMPT_4 = NO
SCOPE_BASELINE_HASH_IMPACT_BY_ATTEMPT_4 = NO
BASELINE_DETERMINISM = PASS
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
REAL_LLM_CALLS = 0
PHASE_13_3 = BLOCKED_BY_PHASE13_2_ATTEMPT_4
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
FAILED_RETAINED_TASK_BLOCKS = 4
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 4
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #4 Result

Status: PASS

Completion time: 2026-08-12 21:00:02 +08:00

`P13-R4-001` selected Branch B. The historical Demo 1 prompt expressed
composition distribution, while the sealed demo required explicit composition
space. The current prompt authority was corrected; production Intent,
Eligibility and Planner behavior did not change. Demo 1 now selects exactly
`dataset.materials_explorer` and `dataset.composition_space`, and all seven
canonical prompts pass semantic coverage (`7/7`) without invented dependencies,
forced Plan upgrades or unrequested capabilities.

`P13-R4-002` was caused by the Workspace projection omitting the Report panel
before a Report existed and the frontend treating scientific
`LEGACY_READ_ONLY` as a global Report Finalize prohibition. Report actions now
derive independently from exact current Profile, Intent, Eligibility, Plan,
terminal Job, scope and integrity facts. Current valid Plan 0.1 Finalize passes;
legacy incomplete and stale Plan 0.1 sources remain unavailable with typed
reasons; cross-project sources remain rejected; Plan 0.2 is unchanged.

The fresh Demo 1 smoke used real PostgreSQL, Redis, MinIO and a fresh Worker.
Plan `plan_7d0d916dd60945fcb28a9879` executed two registered tools and persisted
eight Artifacts. Chromium finalized Report
`report_884dec9549b6617dc4b10d562542a61a` with paired non-executable Recipe
`recipe_884dec9549b6617dc4b10d562542a61a`. Recipe inspection caused zero Plan,
Job, queue, ToolCall or Artifact growth.

Backend: `1406 passed, 52 skipped`; required services separately passed with
zero required skips. Frontend: `458 passed`; Phase 13 focused/governance:
`89 passed`. Typecheck, build, lock, diff, PostgreSQL, Redis, MinIO,
Chromium/Firefox/WebKit/390x844, Linux/Windows, security, secret scan and
manifest all PASS. Failed candidate
`f3ec578acd1cfaddb9437d74869cf437ad17c848` / CI `31594862635` is retained.
Corrected implementation `71985085ac0ab0dbe36b141b88c0251d76892689`
passed exact-SHA CI `31597787296`.

```text
PHASE_13_1_FIX_FORWARD_4 = PASS
P13_R4_001 = CLOSED
P13_R4_002 = CLOSED
CANONICAL_DEMO_SEMANTIC_COVERAGE = 7/7
DEMO1_REQUIRED_CAPABILITY_COVERAGE = COMPLETE
FRESH_DEMO1_PRODUCT_CLOSURE_SMOKE = PASS
CURRENT_VALID_PLAN01_REPORT_FINALIZE = PASS
LEGACY_INCOMPLETE_PLAN01_REPORT_FINALIZE = UNAVAILABLE_WITH_TYPED_REASON
STALE_PLAN01_REPORT_FINALIZE = UNAVAILABLE_WITH_TYPED_REASON
PLAN02_REPORT_BEHAVIOR = UNCHANGED
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
FACT_MODEL_HASH_IMPACT = NO
CURRENT_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
SCOPE_BASELINE_HASH_IMPACT = YES
BASELINE_DETERMINISM = PASS
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_ANALYSISINTENT_VERSION = 0
NEW_ELIGIBILITY_VERSION = 0
NEW_ANALYSISPLAN_VERSION = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_2_ATTEMPT_2 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_3 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_4 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_5 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
P13X2_ACCEPTANCE = 0/8
FIX_FORWARD_4_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
FIX_FORWARD_4_COMPLETION_RECORDED
FIX_FORWARD_4_QUEUE_ARCHIVED
FAILED_RETAINED_TASK_BLOCKS = 4
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 4
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Release Scope Exception #1 Failure-Evidence CI Record

The initial failure-evidence candidate
`f3871ab44287b658e64fc1c82b90472d890ebdba` retained CI `31619480956` as a
failed candidate: one current semantic-coverage test did not recognize explicit
typed phonon fixture modes. The test-only corrected candidate
`0429b88be6fac1c1d602edfe9fdeaf3f3555e9e1` passed exact-SHA CI
`31620258786`, including Python unit/governance, PostgreSQL/Redis/MinIO service
integration, frontend typecheck/build and retained browser evidence, plus
Linux/Windows scientific replay.

This is failure-evidence verification only. `P13-RSE1-001` remains open,
Release Scope Exception #1 remains failed, completion/archive are not
applicable, all seven queue blocks remain retained, and Attempt 6 remains
unqueued.

```text
RELEASE_SCOPE_EXCEPTION_1_FAILURE_EVIDENCE_SHA = 0429b88be6fac1c1d602edfe9fdeaf3f3555e9e1
RELEASE_SCOPE_EXCEPTION_1_FAILURE_EVIDENCE_EXACT_SHA_CI = 31620258786 / PASS
RELEASE_SCOPE_EXCEPTION_1_COMPLETION_RECORDED = NOT_APPLICABLE
RELEASE_SCOPE_EXCEPTION_1_QUEUE_ARCHIVED = NO
```

# Phase 13-2 Attempt 5
# Seven Canonical Real-User E2E Demonstrations Result

Status: FAILED / REVIEWER_ACTION_REQUIRED

Completion time: 2026-08-12 22:09:13 +08:00

Attempt 5 passed its repository-authority, semantic-coverage, Level C, Level
C2, D0, durable-source, and Demo 1 product-closure entry gates. The execution
then started five entirely fresh canonical demos. Demos 1-3 completed through
real PostgreSQL Jobs, Redis, fresh Workers, registered Adapters, persisted
Artifacts, Workspaces, Chromium Report Finalize, and paired non-executable
Recipes. No historical execution was used as current PASS evidence.

The P0 stop rule was activated by two release-critical product integration
defects. `P13-R5-001` affects Demo 4: a fresh Plan 0.2 trajectory Job completed
RDF, MSD, and diffusion and persisted twelve Artifacts, but its projected
Workspace was rejected for Report actions as `WORKSPACE_SOURCE_NOT_CURRENT`.
`P13-R5-002` affects Demo 5: the real phonon upload persisted a Profile with
only structure resource semantics, so natural-language Intent validation
returned `INTENT_PROFILE_CAPABILITY_MISSING` before Plan or Job creation.
Production and scientific code were not changed. Demos 6-7 and all downstream
negative/provider/cross-browser aggregate work were not executed after the P0
stop.

Evidence commit `d8d1966ff0fb419ff8299ec440c1af8e0c349f24` passed exact-SHA
CI `31603622900`. CI recorded `1410 passed, 1 skipped, 51 deselected` for the
main Python suite, `50 passed, 0 skipped` for service-backed PostgreSQL/Redis/
MinIO integration, and PASS for frontend typecheck/build and retained browser
replays plus Linux/Windows scientific replay. Attempt 5 evidence checks passed
`4/4`; lock, diff, security, secret scan, and the 132-entry evidence manifest
passed. Completion and queue archive are not applicable to this failed attempt.

```text
PHASE_13_2_ATTEMPT_5 = FAILED / REVIEWER_ACTION_REQUIRED
PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_1_FIX_FORWARD_1 = PASS
PHASE13_2_ATTEMPT_2 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_2 = PASS
PHASE13_2_ATTEMPT_3 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_3 = PASS
PHASE13_2_ATTEMPT_4 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_4 = PASS

SEMANTIC_COVERAGE = 7/7 PASS
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
DEMO1_PRODUCT_CLOSURE_REGRESSION = PASS

DEMO_1_STATUS = PASS
DEMO_2_STATUS = PASS
DEMO_3_STATUS = PASS
DEMO_4_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_5_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_6_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_7_STATUS = NOT_EXECUTED_AFTER_P0_STOP
ATTEMPT_5_FRESH_DEMOS_STARTED = 5
ATTEMPT_5_FULL_DEMOS_EXECUTED = 3
DEMO_PASS_OR_EXPLICIT_LIMIT = 3/7
OLD_EVIDENCE_REUSED_AS_ATTEMPT5_PASS = 0

P13_R5_001 = OPEN_REVIEWER_ACTION_REQUIRED
P13_R5_001_CLASS = FRESH_TRAJECTORY_WORKSPACE_REPORT_SOURCE_CURRENTNESS_DEFECT
P13_R5_002 = OPEN_REVIEWER_ACTION_REQUIRED
P13_R5_002_CLASS = REAL_UPLOAD_PHONON_PROFILE_CAPABILITY_HANDOFF_DEFECT
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 2
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
PROVIDER_EXTERNAL_EVENTS = 0
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0

UPLOAD_PROCESS_MEMORY_DEPENDENCY = 0
MANUAL_NORMALIZED_EXPORT_PRELOAD = 0
RUNTIME_REPARSE_FALLBACK = 0
ALL_HANDCRAFTED_INJECTION_COUNTERS = 0
P13X2_ACCEPTANCE = 0/8

CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
FACT_MODEL_HASH_IMPACT_BY_ATTEMPT_5 = NO
SCOPE_BASELINE_HASH_IMPACT_BY_ATTEMPT_5 = NO
BASELINE_DETERMINISM = PASS

REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain

ATTEMPT_5_EVIDENCE_VERIFIED_BY_EXACT_SHA_CI
ATTEMPT_5_COMPLETION_RECORDED = NOT_APPLICABLE
PHASE13_2_QUEUE_ARCHIVED = NO

FAILED_RETAINED_TASK_BLOCKS = 5
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 5
PHASE_13_3 = BLOCKED_BY_PHASE13_2_ATTEMPT_5
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #5 Result

Status: BLOCKED / DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT

Time: 2026-08-12 23:25:00 +08:00

`P13-R5-001` was reproduced from the retained real Attempt 5 PostgreSQL state.
Intent and Eligibility used top-level `DataProfile.version = 2` because the
Trajectory Profile legitimately had `sampleIdentity = null`; Workspace
projection omitted that fallback and persisted `datasetVersion = null`.
The bounded implementation now applies the same fallback and verifies the
immutable Workspace source snapshot against the exact execution source. The
Workspace/Report focused suite passed `29/29`. Because the Branch C hard stop
occurred before the required fresh Demo 4 service/browser smoke, the full
R5-001 closure gate is not claimed.

The required R5-002 authority audit selected Branch C. Attempt 5's exact user
action was public `/datasets/upload` with `stable_band.json`, `total_dos.json`
and `POSCAR`. Phase 11 classifies generic phonon YAML/JSON as `MAPPING_ONLY` and
the product has no supported user-visible typed phonon import/selection path.
Exact schemas, internal normalized mappers, C/C2 preparation, runtime resolver,
Adapters and viewers exist, but none constitutes legal normal-user ingestion.
No parser, support matrix row, hidden endpoint, Profile injection or input
support promotion was added.

```text
PHASE_13_1_FIX_FORWARD_5 = BLOCKED / DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT
P13_R5_001 = IMPLEMENTATION_CORRECTED / FRESH_DEMO4_SMOKE_NOT_EXECUTED
P13_R5_001_MISMATCH_FIELD = datasetVersion
P13_R5_002 = OPEN_REVIEWER_AUTHORITY_REQUIRED
P13_R5_002_HISTORICAL_CLASS = REAL_UPLOAD_PHONON_PROFILE_CAPABILITY_HANDOFF_DEFECT
P13_R5_002_SELECTED_BRANCH = C
P13_R5_002_FINAL_CLASS = DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT
PHONON_DIRECT_UPLOAD_SUPPORT_PROMOTION = 0
INPUT_SUPPORT_PROMOTIONS = 0
PHASE11_INPUT_SUPPORT_MATRIX_CHANGED = NO
CANONICAL_DEMO_SEMANTIC_COVERAGE = 7/7 PASS
CANONICAL_USER_INGESTION_FIDELITY = 6/7 BLOCKED
USER_ENTRY_CONTRACT_MISMATCHES = 1
INTERNAL_ONLY_ENTRY_PATHS_USED_AS_USER_PASS = 0
FRESH_DEMO4_PRODUCT_CLOSURE_SMOKE = NOT_EXECUTED_AFTER_BRANCH_C_STOP
FRESH_DEMO5_PRODUCT_CLOSURE_SMOKE = NOT_APPLICABLE_BRANCH_C
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
DEMO1_PRODUCT_CLOSURE_REGRESSION = PASS
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
FACT_MODEL_HASH_IMPACT = NO
SCOPE_BASELINE_HASH_IMPACT = NO
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
PHASE13_2_ATTEMPT_6 = BLOCKED / NOT_AUTHORIZED
PHASE13_2_ATTEMPT_6_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
FAILED_RETAINED_TASK_BLOCKS = 6
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 6
FIX_FORWARD_5_IMPLEMENTATION_EXACT_SHA_CI = NOT_RUN_BRANCH_C_STOP
FIX_FORWARD_5_COMPLETION_RECORDED = NO
FIX_FORWARD_5_QUEUE_ARCHIVED = NO
```

# Phase 13-1 Release Scope Exception #1 Result

Status: FAILED / REVIEWER_ACTION_REQUIRED

Time: 2026-08-13 00:20:00 +08:00

The authorized bounded typed `PhononBand`/`PhononDos` import candidate reused
the existing `/datasets/upload`, strict Phase 10H resource contracts,
PostgreSQL Dataset/DataProfile metadata, and MinIO normalized source authority.
Generic phonon JSON remained mapping-only. Focused backend tests passed 10/10,
PlannerWorkbench passed 33/33, retained phonon contract/Adapter tests passed
76/76, and frontend typecheck passed.

Fresh Demo 4 reached a completed three-ToolCall Job, twelve persisted Artifacts,
a current Workspace, and eligible Report actions. Before its Chromium finalize,
fresh Demo 5 exposed a new P0 and activated the stop rule. Demo 5 passed typed
Band/DOS import, Profile, Intent, Eligibility, PlanValidator, PostgreSQL Job,
Redis enqueue, a fresh Worker, four registered ToolCalls, and 27 persisted
Artifacts. Workspace creation then returned `PANEL_CAP_EXCEEDED`: deterministic
projection exceeds the fixed 32-panel contract. This is `P13-RSE1-001`, class
`CANONICAL_PHONON_JOB_EXCEEDS_WORKSPACE_PANEL_CAP`.

No repair for the new finding was attempted. Demo 4/5 UI Finalize, full
regression, new Fact/Scope hashes, exact-SHA CI, completion, and queue archive
are not applicable to this failed candidate. R5-001 and R5-002 remain open.

Failed candidate `f3871ab44287b658e64fc1c82b90472d890ebdba` ran CI
`31619480956`. Its Python job reported `1423 passed` and one governance failure:
the current seven-demo coverage helper recognized only historical
`normalized_mapping`, not the new explicit typed import fixture modes. The
subsequent candidate changes only that test/evidence dispatch and does not
alter product behavior or the `P13-RSE1-001` conclusion.

```text
PHASE_13_1_RELEASE_SCOPE_EXCEPTION_1 = FAILED / REVIEWER_ACTION_REQUIRED
P13_RSE1_001 = OPEN_REVIEWER_ACTION_REQUIRED
P13_RSE1_001_SEVERITY = P0
P13_RSE1_001_CLASS = CANONICAL_PHONON_JOB_EXCEEDS_WORKSPACE_PANEL_CAP
P13_R5_001 = IMPLEMENTATION_CORRECTED / FRESH_DEMO4_SMOKE_NOT_COMPLETED
P13_R5_002 = OPEN_REVIEWER_ACTION_REQUIRED
TYPED_PHONON_BAND_CANDIDATE = REACHED_FRESH_WORKER
TYPED_PHONON_DOS_CANDIDATE = REACHED_FRESH_WORKER
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY
GENERIC_PHONON_JSON_AUTO_PROMOTION = 0
FRESH_DEMO4_PRODUCT_CLOSURE_SMOKE = NOT_COMPLETED_AFTER_P0_STOP
FRESH_DEMO5_PRODUCT_CLOSURE_SMOKE = FAIL_PRODUCT_INTEGRATION
DEMO5_TOOLCALLS = 4
DEMO5_PERSISTED_ARTIFACTS = 27
DEMO5_WORKSPACES = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 1
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
FACT_MODEL_HASH_IMPACT = NOT_APPLIED_AFTER_P0_STOP
SCOPE_BASELINE_HASH_IMPACT = NOT_APPLIED_AFTER_P0_STOP
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
PHASE13_2_ATTEMPT_6 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
P13X2_ACCEPTANCE = 0/8
FAILED_RETAINED_TASK_BLOCKS = 7
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 7
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #6 Result

Status: PASS

Time: 2026-08-13 12:58:00 +08:00

Implementation `0867a69a587bf8e0ddb5aaeec7a177808a69e6f1` passed exact-SHA
CI `31667748439`. This candidate includes the bounded R5-001 correction, the
authorized typed phonon import candidate, generic logical-surface Workspace
projection, evidence, tests, and generated Fact/Scope authorities.

`P13-RSE1-001` is closed as a Workspace panel projection cardinality defect.
The historical Demo 5 projection had six structural plus 27 Artifact-derived
candidate panels. The corrected projection has six structural panels and one
exact Job-bound Results/Artifact Gallery surface. All 27 Artifacts remain
checksum-, ToolCall-, and lineage-bound and exactly reachable. The cap remains
32; exact-32 passes and 33 distinct non-groupable surfaces still return
`PANEL_CAP_EXCEEDED`, with no truncation or historical reprojection.

Fresh Demo 4 completed through three ToolCalls, 12 persisted Artifacts,
Workspace `workspace_7b853905207a11183b981c3cea68fc05`, Chromium UI
Finalize, Report `report_68f398a22f6ece8286d3c65d57ef48fa`, and Recipe
`recipe_68f398a22f6ece8286d3c65d57ef48fa`. Exact execution, Workspace,
and Report source snapshots agree; stale, hash, and cross-project negatives
remain rejected. `P13-R5-001` is closed.

Fresh Demo 5 completed from explicit typed PhononBand and PhononDos import
through DataProfile 2.4, Intent 1.0, Eligibility 1.0, Planner, PlanValidator,
PostgreSQL Job `job_66e90ccd3a9648ceb39d576a`, Redis, fresh Worker, four
registered ToolCalls, 27 Artifacts, Workspace
`workspace_bea76bb13adc0987324ad23cb1fa6413`, seven panels, exact Gallery
reachability, Chromium UI Finalize, Report
`report_044097cefce37d3471a7846b63c7604b`, and Recipe
`recipe_044097cefce37d3471a7846b63c7604b`. Unknown input refs and Recipe
execution growth are zero. `P13-R5-002` is closed.

The failed Release Scope Exception #1 remains immutable historical evidence.
Its authorized scope is sealed by Fix-Forward #6: typed PhononBand/PhononDos
imports are `SUPPORTED_WITH_LIMITS`, while generic phonon YAML/JSON remains
`MAPPING_ONLY`; no other support or scientific capability is promoted.

Validation: backend `1432 passed, 50 skipped`; frontend `460 passed` in 71
files; Phase 13 focused/governance `113 passed`; service suite `7 passed` with
zero required skips; Chromium, Firefox, WebKit, and 390x844 checks `4/4 PASS`;
typecheck, build, lock, diff, Linux, Windows, security, secret scan, and manifest
PASS. npm audit is `UNAVAILABLE_CONFIGURED_MIRROR_NOT_IMPLEMENTED`.

```text
PHASE_13_1_INTEGRATION_FIX_FORWARD_6 = PASS
P13_RSE1_001 = CLOSED
P13_RSE1_001_HISTORICAL_CLASS = CANONICAL_PHONON_JOB_EXCEEDS_WORKSPACE_PANEL_CAP
P13_RSE1_001_FINAL_CLASS = WORKSPACE_PANEL_PROJECTION_CARDINALITY_DEFECT
MAX_PANELS_PER_WORKSPACE = 32
PANEL_CAP_CHANGE = NO
ARTIFACT_COUNT_TO_PANEL_COUNT_ONE_TO_ONE = NO
PANEL_TRUNCATION = 0
DROPPED_ARTIFACTS = 0
UNREACHABLE_ARTIFACTS = 0
PANEL_CAP_32_CASE = PASS
PANEL_CAP_33_CASE = PANEL_CAP_EXCEEDED
P13_R5_001 = CLOSED
FRESH_DEMO4_PRODUCT_CLOSURE_SMOKE = PASS
FRESH_TRAJECTORY_WORKSPACE_SOURCE_CURRENTNESS = PASS
TRAJECTORY_STALE_SOURCE_REJECTION = PASS
P13_R5_002 = CLOSED
TYPED_PHONON_BAND_USER_IMPORT = SUPPORTED_WITH_LIMITS / PASS
TYPED_PHONON_DOS_USER_IMPORT = SUPPORTED_WITH_LIMITS / PASS
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY
GENERIC_PHONON_JSON_AUTO_PROMOTION = 0
FRESH_DEMO5_PRODUCT_CLOSURE_SMOKE = PASS
FRESH_DEMO5_WORKSPACE_PROJECTION = PASS
FRESH_DEMO5_PANEL_CAP_EXCEEDED = 0
FRESH_DEMO5_ARTIFACT_REACHABILITY = COMPLETE
RELEASE_SCOPE_EXCEPTION_1_AUTHORIZED_SCOPE = SEALED_BY_FIX_FORWARD_6
FIX_FORWARD_5_BLOCK = RESOLVED_BY_FIX_FORWARD_6
CANONICAL_DEMO_SEMANTIC_COVERAGE = 7/7
CANONICAL_USER_INGESTION_FIDELITY = 7/7
USER_ENTRY_CONTRACT_MISMATCHES = 0
INTERNAL_ONLY_ENTRY_PATHS_USED_AS_USER_PASS = 0
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
DEMO1_PRODUCT_CLOSURE_REGRESSION = PASS
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
INPUT_SUPPORT_MATRIX_CHANGED = YES
AUTHORIZED_TYPED_IMPORT_SUPPORT_ADDITIONS = 2
OTHER_INPUT_SUPPORT_PROMOTIONS = 0
SCIENTIFIC_CAPABILITY_PROMOTIONS = 0
OLD_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
FACT_MODEL_HASH_IMPACT = YES
CURRENT_FACT_MODEL_HASH = 92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a
OLD_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
SCOPE_BASELINE_HASH_IMPACT = YES
CURRENT_SCOPE_BASELINE_HASH = bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
BASELINE_DETERMINISM = PASS
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_SCIENTIFIC_ADAPTERS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
FIX_FORWARD_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
FIX_FORWARD_6_COMPLETION_RECORDED
FIX_FORWARD_5_BLOCK_RESOLVED_BY_FIX_FORWARD_6
RELEASE_SCOPE_EXCEPTION_1_FAILURE_RESOLVED_BY_FIX_FORWARD_6
PHASE13_2_ATTEMPT_6 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
PHASE13_2_ATTEMPT_6_DEMOS_EXECUTED = 0
P13X2_ACCEPTANCE = 0/8
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## 2026-08-16 Phase D Live Qualification Environment Seal

Status: BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED

Entry repository SHA is
`08939f1b72ce37f153a0bdc18eee213f336b3636`, matching `origin/master`.
The required frozen qualification ZIP is absent from its authority path under
`_qualification/inputs/`. A same-named untracked ZIP exists at repository root,
has 19,073,044 bytes, and matches the expected SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`,
but Phase D did not copy, move, repackage, or accept it as a path substitute.

Blocker `PHASE_D-B001 = QUALIFICATION_PACKAGE_MISSING_AT_AUTHORITY_PATH` stopped
the run before extraction, internal manifest verification, service startup,
worker startup, browser smoke, or provider credential inspection. Formal case,
LLM, Job, and Artifact counters remain zero. Production code, qualification
package, and scientific fixture changes remain zero. Local blocked evidence is
retained under `_qualification/evidence/phase_d/`; no Phase E task was created.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED
READY_FOR_PHASE_E = NO
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
BLOCKERS = [PHASE_D-B001]
```

# Phase 13-5 Final Regression + Release Acceptance Local Validation

Status: `LOCAL_VALIDATION_PASS_PENDING_EXACT_SHA_CI`.

Seven fresh isolated, service-backed canonical paths passed without reusing
Attempt6 runtime entities: 18 registered ToolCalls, 85 persisted Artifacts,
seven Job-derived Workspaces, seven UI-finalized Reports, and seven paired
non-executable Recipes. Demo5 used explicit typed PhononBand and PhononDos
imports; generic phonon YAML/JSON remained mapping-only. Artifact reachability,
32/33 panel-cap protection, frozen authority hashes, documentation/reproducibility,
browser, security, and retained regression gates passed locally. No production,
scientific, support, or dependency change was made. Exact-SHA CI, completion,
and queue archive remain pending.

# Phase 13-4 Targeted Final Product Polish Result

Status: `PASS / TARGETED_FINAL_PRODUCT_POLISH_COMPLETE`

Completion time: `2026-08-13 23:42:03 +08:00`

Implementation/evidence SHA:
`40403cfa19451cc9a473c41bddecfe053e1a5fea`

Exact-SHA CI: `31715231470` `PASS`

The Phase13-3 handoff produced two presentation candidates. `P13-POLISH-001`
is `ALREADY_RESOLVED` because the current-facing UTF-8 scan found zero mojibake
hits. `P13-POLISH-002` is the sole implemented item: the existing Planner
top-bar Help control is now a localized, keyboard-accessible link to current
Initial Release documentation. It changes no product execution, API, backend,
scientific, Planner, Runtime, Workspace, Report, Recipe, capability, input
support, canonical prompt, fixture, Fact, Scope, or reproducibility authority.

Candidate `34f7cb7cea3db351edff0d3b39ff7fe39cd7e192` failed CI
`31713598663` only because GitHub shallow checkout lacked sealed entry object
`d415d05...` for evidence nonchange checks. Candidate
`40403cfa19451cc9a473c41bddecfe053e1a5fea` corrects that CI-only portability
issue and passed all exact-SHA jobs.

```text
PHASE_13_4 = PASS / TARGETED_FINAL_PRODUCT_POLISH_COMPLETE
HANDOFF_POLISH_ITEMS_DISCOVERED = 2
ACTIONABLE_POLISH_ITEMS = 1
POLISH_ITEMS_IMPLEMENTED = 1
POLISH_ITEMS_SKIPPED_WITH_REASON = 1
UNAUTHORIZED_POLISH_ITEMS = 0

CURRENT_FACT_MODEL_HASH = 92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a
FACT_MODEL_HASH_IMPACT_BY_PHASE13_4 = NO
CURRENT_SCOPE_BASELINE_HASH = bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba
SCOPE_BASELINE_HASH_IMPACT_BY_PHASE13_4 = NO
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
REPRO_MANIFEST_HASH = 931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2

BACKEND = 1450 passed / 1 skipped / 51 integration deselected
FRONTEND = 460 passed
PHASE13_FOCUSED = 133 passed
POSTGRESQL_REDIS_MINIO = PASS / 0 skipped
CHROMIUM = PASS
FIREFOX = PASS
WEBKIT = PASS
MOBILE_390X844 = PASS
LINUX_REPLAY = PASS
WINDOWS_REPLAY = PASS
TYPECHECK = PASS
BUILD = PASS
UV_LOCK_CHECK = PASS
GIT_DIFF_CHECK = PASS
SECURITY = PASS
SECRET_SCAN = PASS
MANIFEST_SELF_CHECK = PASS
npm audit = UNAVAILABLE_CONFIGURED_MIRROR_NOT_IMPLEMENTED

BACKEND_PRODUCTION_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0

PHASE13_4_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_4_COMPLETION_RECORDED
PHASE_13_5 = REVIEWER_GATE / AWAITING_REVIEWER_PROMPT
PHASE13_5_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-4 Queue Archive

The implementation/evidence SHA `40403cfa19451cc9a473c41bddecfe053e1a5fea`
passed exact-SHA CI `31715231470`; completion commit `46c70c2ed49b30e44ab33450540d1b90aacdea2c`
was pushed before removing the completed Phase 13-4 task block. The completed
result and failed candidate remain permanently recorded above and in the Phase
13-4 evidence tree.

```text
PHASE13_4_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_4_COMPLETION_RECORDED
PHASE13_4_QUEUE_ARCHIVED
TASK_BLOCK_COUNT = 0
EXECUTABLE_PENDING_TASKS = 0
PHASE_13_5 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_5_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-5 Queue Archive

After verification of completion commit `1afed7f982bdd6d2b5e9bef50e2cf4b14b984d32`,
the completed Phase 13-5 task block was removed. The validation result and all
evidence remain permanently retained.

```text
PHASE13_5_QUEUE_ARCHIVED
TASK_BLOCK_COUNT = 0
EXECUTABLE_PENDING_TASKS = 0
PHASE_13_6 = REVIEWER_GATE / AWAITING_REVIEWER_PROMPT
PHASE13_6_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Fix-Forward #6 Queue Archive

The completed Fix-Forward #6 block, resolved Fix-Forward #5 blocked block, and
historical failed Release Scope Exception #1 queue block are archived after
their permanent `results.md` and evidence provenance was verified. The five
failed Phase 13-2 Attempt blocks remain. Attempt 6 is not executed or queued.

```text
FIX_FORWARD_6_QUEUE_ARCHIVED
FIX_FORWARD_5_BLOCK_RESOLVED_BY_FIX_FORWARD_6
RELEASE_SCOPE_EXCEPTION_1_FAILURE_RESOLVED_BY_FIX_FORWARD_6
FAILED_RETAINED_PHASE13_2_ATTEMPTS = 5
BLOCKED_FIX_FORWARD_TASKS = 0
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 5
PHASE13_2_ATTEMPT_6 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
PHASE13_2_ATTEMPT_6_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-2 Attempt 6 Result

Status: `PASS`

Completion time: `2026-08-13 17:10:00 +08:00`

Implementation/evidence SHA:
`5ddf2c0508a1f61642808a35774917fa3b54b0b0`

Exact-SHA CI: `31682863560` `PASS`

Seven fresh canonical real-user product paths completed from current user entry
through PostgreSQL/MinIO durable identity, DataProfile 2.4, natural-language
Intent 1.0, Eligibility 1.0, capability-aware Planner, validated Plan 0.1/0.2,
PostgreSQL Job, Redis, fresh QueueWorkerRuntime, registered Adapters, persisted
Artifacts, Job-derived Workspace, typed Viewer/Gallery, Chromium Report Preview
and UI Finalize, persisted Report, and paired non-executable Recipe.

```text
PHASE_13_2_ATTEMPT_6 = PASS
ATTEMPT6_FRESH_DEMOS_STARTED = 7
ATTEMPT6_FULL_DEMOS_EXECUTED = 7
DEMO_PASS_OR_EXPLICIT_LIMIT = 7/7
OLD_EVIDENCE_REUSED_AS_ATTEMPT6_PASS = 0

DEMO_1_STATUS = PASS
DEMO_2_STATUS = PASS
DEMO_3_STATUS = PASS
DEMO_4_STATUS = PASS
DEMO_5_STATUS = PASS
DEMO_6_STATUS = PASS
DEMO_7_STATUS = PASS

TOOLCALLS = 18
PERSISTED_ARTIFACTS = 85
WORKSPACE_PANELS_PER_DEMO = 7
UNREACHABLE_ARTIFACTS = 0
PANEL_CAP_32_CASE = PASS
PANEL_CAP_33_CASE = PANEL_CAP_EXCEEDED
PANEL_TRUNCATION = 0

TYPED_PHONON_BAND_IMPORT = SUPPORTED_WITH_LIMITS
TYPED_PHONON_DOS_IMPORT = SUPPORTED_WITH_LIMITS
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY

CANONICAL_DEMO_SEMANTIC_COVERAGE = 7/7
CANONICAL_USER_INGESTION_FIDELITY = 7/7
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
P13X2_ACCEPTANCE = 8/8

BACKEND = 1438 passed
FRONTEND = 460 passed
PHASE13_FOCUSED = 121 passed
REQUIRED_SERVICE_TESTS = 8 passed / 0 skipped
CHROMIUM = PASS
FIREFOX = PASS
WEBKIT = PASS
MOBILE_390X844 = PASS
LINUX_REPLAY = PASS
WINDOWS_REPLAY = PASS
TYPECHECK = PASS
BUILD = PASS
UV_LOCK_CHECK = PASS
GIT_DIFF_CHECK = PASS
SECURITY = PASS
SECRET_SCAN = PASS
MANIFEST_SELF_CHECK = PASS

CURRENT_FACT_MODEL_HASH = 92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a
CURRENT_SCOPE_BASELINE_HASH = bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba
FACT_MODEL_HASH_IMPACT_BY_ATTEMPT6 = NO
SCOPE_BASELINE_HASH_IMPACT_BY_ATTEMPT6 = NO

REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
MAX_PANELS_PER_WORKSPACE = 32

PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_SCIENTIFIC_ADAPTERS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0

ATTEMPT_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
ATTEMPT_6_COMPLETION_RECORDED
PHASE_13_3 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-2 Queue Archive

Attempt6 PASS, implementation exact-SHA CI `31682863560`, and completion commit
`dd4ac01` were verified before archive. Attempt1-5 historical failures and the
Attempt6 PASS remain permanently recorded in `results.md` and evidence. All six
Phase13-2 TASK blocks are removed; no Phase13-3 task is created.

```text
PHASE13_2_QUEUE_ARCHIVED
ATTEMPT_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
ATTEMPT_6_COMPLETION_RECORDED
FAILED_RETAINED_TASK_BLOCKS = 0
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 0
PHASE_13_3 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-3 Documentation + Reproducibility Package Result

Status: `PASS / DOCUMENTATION_AND_REPRODUCIBILITY_PACKAGE_COMPLETE`

Completion time: `2026-08-13 21:29:27 +08:00`

Implementation/evidence SHA:
`c3aabd055e067c5a52a0c0238c625dbc035a96f0`

Exact-SHA CI: `31703805747` `PASS`

Phase 13-2 Attempt 6 authority, P13X2 `8/8`, current Fact/Scope/Phase12
authorities, current input support, scientific limitations, provider policy,
security boundaries, seven canonical prompts, and eleven canonical fixtures
are reconciled into current human and machine-readable release documentation.

The deterministic reproducibility manifest semantic hash is
`931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2`.
Text fixture evidence uses canonical UTF8/LF hashing; binary evidence uses raw
bytes. Windows clean-checkout regeneration matches the committed package, and
CI verifies Linux/Windows manifest parity.

```text
PHASE_13_3 = PASS / DOCUMENTATION_AND_REPRODUCIBILITY_PACKAGE_COMPLETE

ATTEMPT6_AUTHORITY_RECONCILED = PASS
P13X2_ACCEPTANCE = 8/8

CANONICAL_DEMO_DOCUMENTATION = 7/7
CANONICAL_DEMO_REPRO_CONTRACTS = 7/7
CANONICAL_DEMO_FIXTURE_HASHES = 7/7
CANONICAL_DEMO_PROMPTS = 7/7
CANONICAL_DEMO_USER_ENTRY_CONTRACTS = 7/7

CANONICAL_FIXTURE_RECORDS = 11
REPRO_MANIFEST_HASH = 931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2
REPRO_MANIFEST_DETERMINISM = PASS
LINUX_WINDOWS_REPRO_MANIFEST_PARITY = PASS
CLEAN_CHECKOUT_REPRO_BOOTSTRAP = PASS

POSTGRESQL_REPRO_INSTRUCTIONS = PASS
REDIS_REPRO_INSTRUCTIONS = PASS
MINIO_REPRO_INSTRUCTIONS = PASS
MIGRATION_REPRO_INSTRUCTIONS = PASS

CURRENT_RELEASE_DOCUMENTATION = PASS
CURRENT_INPUT_SUPPORT_DOCUMENTATION = PASS
CURRENT_API_DOCUMENTATION = PASS
CURRENT_SECURITY_DOCUMENTATION = PASS
CURRENT_LIMITATIONS_DOCUMENTATION = PASS

DOCUMENTATION_INVENTORY_TOTAL = 1522
RELEASE_FACING_DOCUMENTS = 20
KNOWN_LIMITATIONS = 8
UNSUPPORTED_PUBLIC_CLAIMS = 0
KNOWN_LIMITATIONS_WITHOUT_DISCLOSURE = 0
BROKEN_RELEASE_DOC_LINKS = 0
PRIVATE_LOCAL_PATH_HITS = 0
SECRET_PATTERN_HITS = 0

TYPED_PHONON_BAND_IMPORT = SUPPORTED_WITH_LIMITS
TYPED_PHONON_DOS_IMPORT = SUPPORTED_WITH_LIMITS
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY

REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
MAX_PANELS_PER_WORKSPACE = 32

CURRENT_FACT_MODEL_HASH = 92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a
FACT_MODEL_HASH_IMPACT_BY_PHASE13_3 = NO
CURRENT_SCOPE_BASELINE_HASH = bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba
SCOPE_BASELINE_HASH_IMPACT_BY_PHASE13_3 = NO
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4

BACKEND = 1445 passed / 1 skipped / 51 integration deselected
FRONTEND = 460 passed
PHASE13_FOCUSED = 128 passed
SERVICE_BACKED = 50 passed / 0 skipped
CHROMIUM = PASS
FIREFOX = PASS
WEBKIT = PASS
MOBILE_390X844_RETAINED = PASS
LINUX_REPLAY = PASS
WINDOWS_REPLAY = PASS
TYPECHECK = PASS
BUILD = PASS
UV_LOCK_CHECK = PASS
GIT_DIFF_CHECK = PASS
SECURITY = PASS
SECRET_SCAN = PASS
MANIFEST_SELF_CHECK = PASS
npm audit = UNAVAILABLE_CONFIGURED_MIRROR_NOT_IMPLEMENTED

PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_SCIENTIFIC_ADAPTERS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
LOCKFILE_CHANGES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0

RELEASE_CRITICAL_INTEGRATION_DEFECTS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
UNCLASSIFIED_RELEASE_GAPS = 0

PHASE13_3_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_3_COMPLETION_RECORDED

PHASE_13 = IN_PROGRESS / DOCUMENTATION_AND_REPRODUCIBILITY_COMPLETE
PHASE_13_4 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_4_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-3 Queue Archive

Implementation exact-SHA CI `31703805747` and completion commit
`f4e2bb324ec4c248869cdc022f926d6f40448522` were verified before removing
the sole completed Phase 13-3 task block. The documentation and reproducibility
result remains permanently recorded above.

```text
PHASE13_3_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_3_COMPLETION_RECORDED
PHASE13_3_QUEUE_ARCHIVED

TASK_BLOCK_COUNT = 0
EXECUTABLE_PENDING_TASKS = 0

PHASE_13_4 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_4_EXECUTABLE_TASK_CREATED = NO

INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-5 Final Regression + Release Acceptance Result

Status: PASS
Completed: 2026-08-14

The validation/evidence implementation `b60e048abbf366fdbd9fe72da27efd675fc50939`
passed exact-SHA CI `31728986993`. Seven newly created canonical user paths used
real PostgreSQL, Redis, MinIO, a fresh worker, registered adapters, persisted
artifacts, job-derived Workspaces, Chromium UI Finalize, Reports, and paired
non-executable Recipes. The run recorded 18 ToolCalls, 85 Artifacts, seven
Workspaces, seven finalized Reports, and seven Recipes; no fresh Artifact was
unreachable. No production, scientific, support, schema, dependency, migration,
or LLM-site change was made.

The retained negative, panel-cap, documentation/reproducibility, browser,
accessibility, performance, security, and Linux/Windows authority gates pass.
The sealed Fact hash is
`92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a`, the
sealed Scope hash is
`bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba`, the
Phase12 baseline is
`29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4`, and the
reproducibility-manifest semantic hash is
`931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2`.

```text
PHASE_13_5 = PASS / FINAL_REGRESSION_AND_RELEASE_ACCEPTANCE_COMPLETE
PHASE13_5_RELEASE_ACCEPTANCE = PASS
RELEASE_CANDIDATE_ACCEPTED = YES
READY_FOR_PHASE13_6 = YES
PHASE13_5_FRESH_DEMOS_STARTED = 7
PHASE13_5_FULL_DEMOS_EXECUTED = 7
PHASE13_5_DEMO_PASS_OR_EXPLICIT_LIMIT = 7/7
P13X2_ACCEPTANCE = 8/8
UNREACHABLE_ARTIFACTS = 0
PANEL_TRUNCATION = 0
MAX_PANELS_PER_WORKSPACE = 32
TYPED_PHONON_BAND_IMPORT = SUPPORTED_WITH_LIMITS
TYPED_PHONON_DOS_IMPORT = SUPPORTED_WITH_LIMITS
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
INPUT_SUPPORT_PROMOTIONS = 0
PHASE13_5_VALIDATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_5_COMPLETION_RECORDED
PHASE_13_6 = REVIEWER_GATE / AWAITING_REVIEWER_PROMPT
PHASE13_6_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-6 Final Archive + Presentation Package Result

Status: PASS
Completed: 2026-08-14

Implementation/evidence SHA `48b270c6d2c6191b5707f6ee1c4d81a6ab9c8987`
passed exact-SHA CI `31768285019`. The final package freezes production surface
hash `11ffe1847ddffcf6b7a7d5f7d6286146910a19c4c89e018f3b8f47a0c4138151`,
InitialReleaseManifest semantic hash
`2f255942d4557569f7f01d6d1118a5cec1bc209f03bf1cf92b21d65fb65be844`,
and deterministic archive SHA-256
`3b328585f9345dda341a349f8745e4e3af89b6bb0a80e79747c03a52aa86bbbd`
(1,630,918 bytes; 45 entries). Extraction, manifest, link, traversal,
private-path, secret, and screenshot provenance checks pass.

Failed candidates remain retained: `ad0c98f4e469bb9215cd651ad6ed791527faf01c`
/ CI `31767331402` failed clean-checkout artifact ordering and was corrected by
`f7388b8ef402826d9a0f978c6c43f800449da5f3`; that SHA / CI `31767878567`
failed the retained sanitizer self-match and was corrected by the verified
implementation `48b270c6d2c6191b5707f6ee1c4d81a6ab9c8987`. Both are
`CI_EVIDENCE_PORTABILITY` history, not release builds.

```text
PHASE_13_6 = PASS / FINAL_ARCHIVE_AND_PRESENTATION_PACKAGE_COMPLETE
PHASE13_6_INITIAL_RELEASE_CLOSURE = PASS
PHASE13_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_6_COMPLETION_RECORDED
INITIAL_RELEASE_COMPLETION_RECORDED
PHASE_13 = COMPLETE / INITIAL_RELEASE_COMPLETE
INITIAL_RELEASE = COMPLETE / PHASE13_FINAL_ARCHIVE_AND_PRESENTATION_SEALED
INITIAL_RELEASE_COMPLETE = YES
KNOWN_LIMITATIONS = 8
KNOWN_LIMITATIONS_WITHOUT_DISCLOSURE = 0
P13X2_ACCEPTANCE = 8/8
CANONICAL_DEMOS_ACCEPTED = 7/7
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
INPUT_SUPPORT_CHANGES = 0
NEW_DEPENDENCIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
PHASE14_CREATED = NO
NEXT_EXECUTABLE_PHASE = NONE
```

## 2026-08-16 Phase D Attempt 2 - Controlled Resume

Status: BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED

Completed: 2026-08-16T00:25:15+08:00

Reviewer-authorized controlled placement resolved `PHASE_D-B001`: the
repository-root frozen ZIP was copied byte-for-byte to `_qualification/inputs/`
without moving or modifying the source. Source and destination are each
19,073,044 bytes with SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`,
and direct byte comparison passed.

The resumed package audit passed: root and all 16 case hash manifests have zero
mismatches, all required case structures/assets exist, canonical readiness is
16/16, Recipe execution authorization is 0/16, and paraphrase robustness remains
the frozen 7/16. The current Registry is version 0.1.0 with 62 Tools; repository
authority and qualification authority show no material contract drift.

The application shell loaded in the Codex in-app browser at 1280x720, basic Data
navigation worked, and no console warning/error was observed. DeepSeek policy
resolves to the allowed default model and `DEEPSEEK_KEY` is present; no live call
was made. Phase D remains blocked because PostgreSQL authentication fails,
Redis and MinIO are unavailable, a fresh worker cannot connect, the durable
backend runtime is unhealthy, and no safe fresh qualification namespace can be
verified. These are retained as `PHASE_D-B002` through `PHASE_D-B007`.

Evidence validation: 8 JSON files parsed, 9 SHA256SUMS entries self-validated,
secret/private-path scans returned zero hits, all case/LLM/Job/Artifact counters
are zero, frozen package hashes remain unchanged, and tracked production diff is
zero. Evidence is `_qualification/evidence/phase_d/attempt_02/`; Attempt 1 is
preserved at `_qualification/evidence/phase_d/attempt_01_blocked/`.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED
READY_FOR_PHASE_E = NO
PHASE_D-B001 = RESOLVED
DATABASE_HEALTHY = NO
MIGRATION_AT_EXPECTED_HEAD = NO
QUEUE_BACKEND_HEALTHY = NO
OBJECT_STORAGE_HEALTHY = NO
BACKEND_HEALTHY = NO
FRONTEND_HEALTHY = YES
FRESH_WORKER_AVAILABLE = NO
BROWSER_APP_SHELL_ACCESSIBLE = YES
PROVIDER_CONFIGURATION_RESOLVES = YES
REQUIRED_PROVIDER_CREDENTIAL_PRESENT = YES
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
PHASE_E_EXECUTED = NO
```

## 2026-08-16 Phase E - Autonomous 16-Case Live-Agent Browser Qualification

Status: FAILED / BLOCKED_AUTHORITY_CONFLICT

Completed: 2026-08-16T04:51:17+08:00

Discovery used the frozen qualification ZIP with SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`.
Six repository-grounded routing/planning/interpretation corrections were made
as immutable local commits. Focused verification for the final correction
passed 38 AnalysisIntent, 32 capability Planner, and 34 natural-language
evidence tests; Ruff and `git diff --check` passed.

`Q-DATASET-001` completed the real Browser/DeepSeek/Planner/Queue/Worker/
Adapter/Artifact/Interpretation/Workspace/Report/Recipe discovery workflow on
candidate `8768f544956bf89b1fc1ccf51d6896e9221b3462`.

The campaign stopped at `Q-COMPOSITION-001` on candidate
`2d7f92d266c51a3401a36f619082e5840e0d60f9`. The frozen Case provides only a
CSV table but requires `structure_resource` and
`structure.composition_from_structure`, whose Registry contract requires a
periodic `Structure`. It also requires seven exact Tools/steps while current
AnalysisPlan and selection contracts cap the plan at four. Phase E requires all
expected Tools and explicitly mandates `BLOCKED_AUTHORITY_CONFLICT` for this
kind of contradiction. The package, CASE files, assets, and scientific values
were not changed.

Evidence:
`_qualification/evidence/phase_e/campaign_20260816_blocked_authority_conflict/`.
No final 16-case requalification, exact-SHA CI, completion lifecycle, or later
task was executed.

## 2026-08-16 Phase D - Autonomous Remediation, Requalification & Environment Seal

Status: PASS / LIVE_QUALIFICATION_ENVIRONMENT_SEALED

Completed: 2026-08-16T03:40:00+08:00

The committed D-R1 candidate exposed `PHASE_D-B009`: RQ's default Worker exits
on Windows when it consumes a queued job because `os.fork()` is unavailable.
Commit `54c66abc499c646dc27b612dbf28747b176177c8` adds the canonical
cross-platform worker entrypoint and regression tests. A real isolated Redis
execution smoke returned 42, while the final canonical worker stayed idle with
zero successful and failed qualification jobs.

Attempt 6 independently reverified ZIP SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`,
123 root entries, all 16 case manifests, canonical readiness 16/16, and the
declared paraphrase authority 7/16. PostgreSQL, Redis, MinIO, migration head
`0008_phase_d_r1_namespace`, a fresh base-to-head database, durable project
survival across backend restart, empty Workspace history, backend, frontend,
fresh Worker, provider configuration, and app-shell browser smoke all pass.

Validation: affected Python `67 passed, 2 skipped`; required service-backed
`51 passed, 0 required skips`; frontend `460 passed`; TypeScript typecheck and
production build pass; `uv lock --check`, Ruff, and `git diff --check` pass.
Attempt 6 evidence has 19 hashed entries with zero JSON, hash, secret,
private-path, zero-counter, package-mutation, or production-runtime-diff errors.
No push or CI run was required or performed.

```text
PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_SEALED
READY_FOR_PHASE_E = YES
FINAL_REPOSITORY_HEAD_SHA = 54c66abc499c646dc27b612dbf28747b176177c8
HEAD_EQUALS_ORIGIN_MASTER = NO
PHASE_D-B001..PHASE_D-B009 = RESOLVED
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
BLOCKERS = []
```

## 2026-08-16 Phase D-R1 - Durable Namespace Migration / Bootstrap Remediation

Status: COMPLETED / DURABLE_NAMESPACE_MIGRATION_BOOTSTRAP_CORRECTED

Completed: 2026-08-16T02:31:30+08:00

Root cause was confirmed as SQLAlchemy/Alembic drift plus split Project
authority: migration 0007 lacked `users`, `organizations`, the canonical Project
foreign keys and index, while PostgreSQL-mode `POST /projects` still created only
process-local state. Forward migration `0008_phase_d_r1_namespace` now creates
and backfills the required schema, and PostgreSQL-mode Project create/list uses
`SqlAlchemyProjectRepository`.

Both isolated PostgreSQL migration paths passed: empty database to new head and
0007 to new head with an existing Project preserved and actor/organization rows
backfilled. Production API verification created Project
`project_4e11968a578b49d8ba165024`, resolved an empty Workspace history, and
reloaded both after backend process restart. Database Job, ToolCall, and Artifact
counts remained zero; no formal qualification case or LLM call ran.

Modified files: migration 0008; `durable_projects.py`; PostgreSQL-mode Project
wiring in `phase2_runtime.py`; migration/API/service regression tests; current
runtime/schema docs and persistent governance; focused evidence under
`_qualification/evidence/phase_d_r1/`.

Tests: 23 focused unit/API passed; 15 affected PostgreSQL/Redis/MinIO service
tests passed; 7 migration regressions passed; docs link, new-file ruff,
`uv lock --check`, `git diff --check`, JSON parse, evidence SHA256, secret scan,
private-path scan, and zero execution counters passed. A full backend observation
returned 1454 passed, 51 skipped, and 21 non-D-R1 failures: 19 stale historical
queue assumptions, one pre-existing Phase 13 raw-byte/CRLF manifest mismatch,
and one evidence link checked before generation; that link subsequently passed.

Commit/CI: not requested; HEAD remains
`08939f1b72ce37f153a0bdc18eee213f336b3636` with an uncommitted working tree.

```text
PHASE_D_R1 = PASS / DURABLE_NAMESPACE_MIGRATION_BOOTSTRAP_CORRECTED
NEW_MIGRATION_HEAD = 0008_phase_d_r1_namespace
FRESH_DB_BASE_TO_HEAD = PASS
PREVIOUS_HEAD_TO_NEW_HEAD = PASS
PROJECT_DURABLY_PERSISTED = PASS
PROJECT_SURVIVES_PROCESS_RESTART = PASS
WORKSPACE_HISTORY_PROJECT_RESOLUTION = PASS
MANUAL_DDL_WORKAROUND = 0
METADATA_CREATE_ALL_WORKAROUND = 0
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_PACKAGE_CHANGES = 0
PHASE_D_ATTEMPT_5_EXECUTED = NO
PHASE_E_EXECUTED = NO
```

## 2026-08-16 Phase D Attempt 3 - Docker Runtime Controlled Resume

Status: BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED

Completed: 2026-08-16T01:11:42+08:00

Docker Desktop is available through its installed CLI despite the inherited
Codex shell PATH not being refreshed. Docker Client/Engine are 29.7.2, Docker
Desktop is 4.86.0, and Compose is 5.3.1. The checked-in Compose configuration
parses successfully and defines project-scoped network and volume names for the
isolated `mdi-phase-d-attempt3` project. Its infrastructure services reference
`postgres:16-alpine`, `redis:7-alpine`, and `quay.io/minio/minio:latest`; no
application image build is required for this Phase D infrastructure startup.

Safe-isolation preflight failed before `compose up`: the checked-in file fixes
published host ports 5432 and 6379, already owned by non-Docker PostgreSQL and
Memurai services. Reviewer authorized preemption, but Windows denied both
service-control and direct-process termination from the current non-elevated
session. Existing services and data remained unchanged. No container, network,
volume, database, Redis state, MinIO bucket, backend, worker, or namespace was
partially created. The repository runbook provides local credential and MinIO
bucket bootstrap authority, so credentials are not retained as a separate
blocker.

The full frozen-package gate was independently repeated: external ZIP SHA-256
matches, root and 16 case manifests have zero mismatches, canonical readiness is
16/16, report/Recipe readiness is 16/16, Recipe execution authorization is 0,
and paraphrase robustness remains 7/16. Worktree classification found zero
runtime-affecting tracked changes: governance/docs are non-production, one
tracked test file is TEST_ONLY, and global worktree cleanliness remains NO.

Evidence validation: 10 JSON files parsed, 11 SHA256SUMS entries self-validated,
secret/private-path scans returned zero hits, and all case/LLM/Job/Artifact
counters remain zero. Attempt 3 evidence is retained at
`_qualification/evidence/phase_d/attempt_03/`; Attempts 1 and 2 remain intact.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED
READY_FOR_PHASE_E = NO
PHASE_D-B001 = RESOLVED
PHASE_D-B008 = COMPOSE_FIXED_HOST_PORTS_NOT_AVAILABLE
DOCKER_COMMAND_AVAILABLE = YES
DOCKER_ENGINE_REACHABLE = YES
DOCKER_COMPOSE_AVAILABLE = YES
SAFE_ISOLATED_COMPOSE_RUNTIME = NO
COMPOSE_UP_EXECUTED = NO
GLOBAL_WORKTREE_CLEAN = NO
TRACKED_PRODUCTION_RUNTIME_WORKTREE_CLEAN = YES
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
PHASE_E_EXECUTED = NO
```

## 2026-08-14 Phase A Repository Capability Census

Status: PASS / REPOSITORY_CAPABILITY_CENSUS_COMPLETE

Completed: 2026-08-14 16:08:45 +08:00

The repository-grounded census package is retained at
`docs/qualification/phase_a_repository_capability_census/`. It inventories 4
user entry paths, 15 format families, 15 semantic data kinds, 18 user capability
families, all 62 Registry Tools, 42 Artifact/renderer declarations, and 36
user-centric qualification cases. The 16-case minimum set covers all 20 current
supported or supported-with-limits input combinations; the complete catalog
gives all 47 current Planner-visible Tools case participation. Three phonon-animation
Artifacts/renderers lack an executable normal-user case because eigenvector
entry remains mapping-only; the exact boundary and the absent inline-upload
request caps are retained among eight P2 qualification-design gaps.

Validation: Phase A focused `7 passed`; targeted Registry/parser/Profile/current
authority `94 passed` with four existing CIF warnings; renderer registry `4
passed`. Two generator runs produced identical package hash
`cd6caf371e4b0f0ef2364b0a485c043287467e9a141782506ce6b52418bf46c0`.
Manifest hash/size, repository evidence refs, internal links, UTF-8/LF,
private-path, secret-pattern, Python compile, and diff checks pass. An earlier
test-only candidate failed collection due to indentation while extending queue
vocabulary; it was corrected before the successful 94-test run.

No web access, external fixture download, browser qualification, live LLM call,
production code change, scientific behavior change, input-support change,
Registry/parser/Adapter/renderer/API behavior change, commit, push, or exact-SHA
CI occurred. Initial Release remains complete and Phase 13 remains sealed.

```text
PHASE_A = PASS / REPOSITORY_CAPABILITY_CENSUS_COMPLETE
QUALIFICATION_DATA_RESEARCH_READY = YES
AUTHORITY_CONFLICTS = 0
QUALIFICATION_DESIGN_GAPS = 8
PHASE_B_EXTERNAL_DATA_RESEARCH_EXECUTED = NO
PHASE_B_EXTERNAL_DATA_DOWNLOADED = 0
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
REAL_LLM_CALLS = 0
INITIAL_RELEASE_COMPLETE = YES
PHASE14_CREATED = NO
```

## Phase 13-6 Queue Archive

Implementation/evidence `48b270c6d2c6191b5707f6ee1c4d81a6ab9c8987`
passed exact-SHA CI `31768285019`, and completion commit
`7159e0c16de514b73524ef158d6761897d94cf31` was pushed before removing the
sole completed Phase13-6 task block. The final release package and completion
record remain permanently retained.

```text
PHASE13_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_6_COMPLETION_RECORDED
PHASE13_6_QUEUE_ARCHIVED
INITIAL_RELEASE_COMPLETION_RECORDED
TASK_BLOCK_COUNT = 0
EXECUTABLE_PENDING_TASKS = 0
PHASE14_CREATED = NO
NEXT_EXECUTABLE_PHASE = NONE
```

## 2026-08-16 Phase D Attempt 4 - Complete Live Qualification Environment Seal

Status: BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED

Completed: 2026-08-16T01:43:24+08:00

The frozen repository and qualification identities were independently
reverified at HEAD `08939f1b72ce37f153a0bdc18eee213f336b3636` and ZIP SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`.
Root and all 16 case hash manifests have zero mismatches, canonical readiness is
16/16, and paraphrase robustness remains the declared 7/16.

The unmodified Compose authority started PostgreSQL, Redis, and MinIO in the
isolated `mdi-phase-d-attempt4` project. All three containers are healthy;
their immutable image IDs and RepoDigests, isolated volume identities, and
network identity are retained. PostgreSQL connectivity and Alembic head 0007,
Redis `mdi-jobs`, the empty `mdi-artifacts` bucket, current-SHA backend durable
health, fresh idle RQ worker, frontend, DeepSeek configuration presence, and the
browser app shell all passed. The queue and durable Job/ToolCall/Artifact counts
remain zero.

The only remaining blocker is `PHASE_D-B007`. A fresh project created through
the normal `POST /projects` surface is process-local, while Workspace history
uses the durable SQL repository. The official Alembic 0007 migration path does
not create `users` or `organizations`; canonical
`SqlAlchemyProjectRepository.save()` consequently fails with an undefined
`users` table and Workspace history returns typed `PROJECT_NOT_FOUND`. The
historical release harness works around this with hand-written DDL, but Phase D
correctly did not treat that test harness or `metadata.create_all` as production
migration authority.

Changed files are limited to Phase D governance and local qualification work /
evidence. Attempts 1-3 were preserved. Validation: 12 JSON files parsed; 13
`SHA256SUMS.txt` entries self-validated; secret and private-path scans passed;
production runtime tracked diffs are zero; all formal case, Job, Artifact, and
real-LLM counters are zero. No commit, push, or CI run was requested or executed.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED
READY_FOR_PHASE_E = NO
PHASE_D-B001 = RESOLVED
PHASE_D-B002 = RESOLVED
PHASE_D-B003 = RESOLVED
PHASE_D-B004 = RESOLVED
PHASE_D-B005 = RESOLVED
PHASE_D-B006 = RESOLVED
PHASE_D-B007 = UNRESOLVED
PHASE_D-B008 = RESOLVED
DATABASE_HEALTHY = YES
MIGRATION_AT_EXPECTED_HEAD = YES
QUEUE_BACKEND_HEALTHY = YES
OBJECT_STORAGE_HEALTHY = YES
BACKEND_HEALTHY = YES
FRONTEND_HEALTHY = YES
FRESH_WORKER_AVAILABLE = YES
BROWSER_APP_SHELL_ACCESSIBLE = YES
FRESH_QUALIFICATION_NAMESPACE_READY = NO
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
PHASE_E_EXECUTED = NO
```

## 2026-08-16 Phase B/C-R1 - Qualification Authority Reconciliation, Contract Repair and Refreeze

Status: COMPLETED / QUALIFICATION_AUTHORITY_RECONCILED_AND_REFROZEN

Completed: 2026-08-16T09:31:27+08:00

The historical package remains byte-identical at SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`
and is retained as superseded execution history. The separately versioned
`Phase_BC_R1_Qualification_Authority_Reconciled.zip` uses schema
`PhaseBClosurePhaseCContractManifest/1.1`, has SHA-256
`6a1e3f1100407fd70f2d689bb2022754ac3723f8c127c8963042b25db82dc3b3`,
contains 129 sorted entries and 19,102,189 bytes, and reproduced the same SHA in
two independent deterministic builds.

All 16 primary Cases were audited against repository candidate
`2d7f92d266c51a3401a36f619082e5840e0d60f9`, Registry 62 / snapshot
`registry_371aa3f8106e863af9c7c648`, AnalysisIntent 1.0,
EligibilityResolution 1.0, AnalysisPlan 0.1/0.2, ToolPlannerMetadata 1.0,
migration `0008_phase_d_r1_namespace`, and both four-step planning caps.
`Q-COMPOSITION-001` no longer requires a periodic-Structure Tool from CSV-only
assets. The 16-case result is 15 supported analyses plus one expected typed
pre-Plan rejection for non-periodic XYZ viewer execution. Maximum required
Tools per turn is 4/4.

The primary campaign now distinguishes 33 required Tool assertions from 45/47
Planner-available Tool coverage potential. Seventeen capability families, 35
Artifact types and 13 renderer contracts have primary potential. The two honest
supplemental Tool gaps are `phonon.animation` and
`structure.composition_from_structure`; they were not forced into the primary
Cases. Campaign association remains non-qualifying until later live observation.

The new static validator passes on both the staging tree and a clean ZIP
extraction. Root and all 16 case manifests have zero missing files and zero hash
mismatches. Protected `SOURCE_*`, `UPLOAD_*`, `LICENSE.txt`, and
`PROVENANCE.json` bytes are unchanged. The evidence manifest, JSON parse,
UTF-8/LF, secret, private-path, and zero-execution checks pass.

Validation: focused R1 `7 passed`; Ruff and Python compile PASS. The complete
non-integration CI command also ran: `1471 passed, 20 failed, 1 skipped, 52
deselected`. Nineteen failures are historical tests that hard-code obsolete
`TASKS.md` queue cardinality/content, and one is a pre-existing Phase13-4
evidence byte-size mismatch in the dirty entry worktree. No R1 or production
runtime assertion failed; historical sealed evidence was not rewritten.

Modified files: three non-production R1 scripts, one focused test, the new
versioned package and R1 evidence, qualification navigation, persistent
governance, `TASKS.md`, and this append-only result. Production runtime,
scientific behavior, support dispositions, dependencies, lockfiles, and the old
package were not changed.

```text
PHASE_BC_R1 = PASS / QUALIFICATION_AUTHORITY_RECONCILED_AND_REFROZEN
CASES = 16
EXECUTION_READY_CASES = 16/16
CASE_AUTHORITY_CONFLICTS = 0
REQUIRED_TOOL_INPUT_MISMATCHES = 0
MISSING_REQUIRED_COMPANION_ASSETS = 0
REQUIRED_TOOL_COUNT_OVER_PLAN_CAP = 0
UNSUPPORTED_TOOL_REQUIRED_AS_EXECUTABLE = 0
MAPPING_ONLY_REQUIRED_AS_EXECUTABLE = 0
REQUIRED_ARTIFACT_WITHOUT_PRODUCER = 0
REQUIRED_RENDERER_WITHOUT_ARTIFACT = 0
STATIC_EXECUTABLE_CONTRACT_VALIDATOR = PASS
ROOT_HASH_MISMATCHES = 0
CASE_HASH_MISMATCHES = 0
OLD_PACKAGE_MUTATIONS = 0
SCIENTIFIC_VALUE_FABRICATION = 0
UNIT_GUESSING = 0
STRUCTURE_INFERENCE_FROM_FORMULA = 0
SUPPORT_SURFACE_EXPANSION = 0
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
PHASE_E_CONTINUED = NO
```

Commit/CI status: no commit, push, or CI lifecycle was requested or executed.

## 2026-08-16 Phase B/C-R1.1 - Minimal Qualification Authority Hygiene Correction

Status: COMPLETED / QUALIFICATION_AUTHORITY_INTERNALLY_CONSISTENT_AND_REFROZEN

Completed: 2026-08-16T09:57:47+08:00

The historical R1 package remains byte-identical at SHA-256
`6a1e3f1100407fd70f2d689bb2022754ac3723f8c127c8963042b25db82dc3b3`.
The separately versioned
`Phase_BC_R1_1_Qualification_Authority_Reconciled.zip` has SHA-256
`bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`,
contains 132 sorted entries and 19,105,576 bytes, and reproduced the same SHA
in two independent deterministic builds.

Repository/package governance established that `requiredReportBehavior`,
`requiredRecipeBehavior`, and `requiredLimitations` are canonical. The retained
`expectedReport`, `expectedRecipe`, and `expectedLimitationAssertions` fields
remain normative compatibility aliases and now exactly mirror their canonical
fields in all 16 Cases. The sole source contradiction was corrected in
`Q-ATOMIC-VIEW-001`; it remains an `EXPECTED_REJECTION` with no Plan, Job,
ToolCall, Artifact, Report, or Recipe expected.

All 16 Cases pass report/recipe/limitation alias comparison, execution-turn
Tool-union comparison, required Tool count, per-turn four-step Plan-cap, and
expected-rejection checks. The six R1 multi-turn scenarios remain unchanged.
Package-level machine-readable authority now states that multi-turn Planner
submissions use ordered `executionTurns[].question`, single-turn Cases use the
sole turn question, and expected rejection submits the canonical question and
must stop before Plan creation. Campaign coverage remains 33 required Tool
assertions, 45/47 primary potential Tools, and two supplemental candidates.

The static validator now detects conflicting report, Recipe, and limitation
requirements; execution-turn Tool-union mismatch; required Tool count mismatch;
and execution requirements attached to expected rejection. The historical R1
tree fails exactly once with `CONFLICTING_REPORT_REQUIREMENTS`; the R1.1 staging
tree and clean extracted package both pass with zero issues. Root/case manifests
have zero missing files and zero hash mismatches. `SOURCE_*`, `UPLOAD_*`,
`PROVENANCE.json`, and `LICENSE.txt` bytes are unchanged; scientific values,
units, wavelength, q-path, uncertainty, structure inference, support surface,
production runtime, live LLM calls, and formal qualification execution all have
zero changes/executions.

Validation: Ruff PASS; focused R1/R1.1 `16 passed`; JSON parse, evidence SHA
self-check, and secret-pattern scan PASS. Full non-integration regression was
reproduced as `1480 passed, 20 failed, 1 skipped, 52 deselected`. The 20 failures
match the prior disclosed classification: 19 obsolete historical tests that
hard-code old `TASKS.md` queue content/cardinality and one pre-existing
Phase13-4 evidence byte-size mismatch. No R1/R1.1 or production-runtime test
failed, and the full repository suite is not claimed as PASS.

Modified files: non-production R1/R1.1 qualification scripts and focused tests,
the separately versioned package and evidence, qualification schema/navigation,
persistent governance, `TASKS.md`, and this append-only result. Phase D and
Phase E were not started.

```text
PHASE_BC_R1_1 = PASS / QUALIFICATION_AUTHORITY_INTERNALLY_CONSISTENT_AND_REFROZEN
CASES = 16
EXECUTION_READY_CASES = 16/16
CASE_AUTHORITY_CONFLICTS = 0
CROSS_FIELD_CONTRACT_CONFLICTS = 0
Q_ATOMIC_VIEW_EXPECTED_REJECTION_CONSISTENT = YES
EXECUTION_TURN_TOOL_UNION_MISMATCHES = 0
REQUIRED_TOOL_COUNT_MISMATCHES = 0
REQUIRED_TOOL_COUNT_OVER_PLAN_CAP = 0
EXPECTED_REJECTION_EXECUTION_CONTRADICTIONS = 0
STATIC_EXECUTABLE_CONTRACT_VALIDATOR = PASS
CROSS_FIELD_CONSISTENCY_VALIDATOR = PASS
ROOT_HASH_MISMATCHES = 0
CASE_HASH_MISMATCHES = 0
PROTECTED_SCIENTIFIC_BYTE_CHANGES = 0
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
READY_FOR_PHASE_D_RESEAL = YES
READY_FOR_PHASE_E_DIRECT_CONTINUATION = NO
```

Commit/CI status: no commit, push, or CI lifecycle was requested or executed.

## 2026-08-16 Phase D R1.1 - Live Qualification Environment Re-Seal

Status: FAILED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_RESEALED

Completed: 2026-08-16T10:31:44+08:00

The R1.1 package at SHA-256
`bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`
was independently verified: 16 Cases, 15 analysis-execution Cases, one expected
pre-Plan rejection, 26 declared execution turns, zero root hash mismatches, and
zero case hash mismatches. The static executable-contract and cross-field
consistency validators both passed against current repository authority at
`2d7f92d266c51a3401a36f619082e5840e0d60f9`.

The repository-approved PostgreSQL, Redis, and MinIO containers were healthy.
A new database reached migration head `0008_phase_d_r1_namespace` through the
official Alembic chain. The current-SHA backend, frontend, fresh idle Worker,
DeepSeek configuration, browser app shell, and an empty durable project/
Workspace namespace all passed. The project survived a backend process restart;
Jobs, ToolCalls, Artifacts, Reports, Recipes, and Workspaces remained zero.

The re-seal stopped on three newly confirmed frozen-authority conflicts:

- `PHASE_D_R11_AUTH_001`: `Q-ARCHIVE-001` declares execution-ready UI ZIP
  upload, but the generic UI reads the ZIP with `File.text()` and the backend
  writes UTF-8 text. A mechanical round trip changed 10,912 source bytes into
  19,470 bytes and changed SHA-256.
- `PHASE_D_R11_AUTH_002`: `Q-XRD-001` requires CIF plus experimental-XRD
  companions in one dataset, while the generic normal-user UI submits one file.
- `PHASE_D_R11_AUTH_003`: `Q-ELECTRONIC-001` requires Band plus DOS companions
  in one dataset, while the same UI path submits one file.

These are not ordinary Phase D runtime defects. Implementing binary or generic
multi-resource upload would change the normal-user scientific input contract,
which is an explicit hard stop requiring authority reconciliation and refreeze.
No such product change was made.

Validation: focused tests `17 passed`; package/root/case hashes PASS; JSON parse,
evidence SHA-256 self-check, secret scan, private-path scan, and zero-execution
counter checks PASS. Evidence is preserved at
`_qualification/evidence/phase_d/attempt_07_r1_1_reseal_blocked_authority_conflict/`.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_RESEALED
READY_FOR_PHASE_E = NO
CASE_AUTHORITY_CONFLICTS = 3
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
```

Modified files: Phase D Attempt 7 evidence, `TASKS.md`, and this append-only
result. Historical Phase D/Phase E evidence and failed tasks remain unchanged.
Phase E-R1.1 was not created or started.

Commit/CI status: no commit, push, or CI execution was performed because Phase D
ended at the frozen-authority hard stop.

## 2026-08-16 Phase D-R2 - Normal-User Input Transport Contract Closure + R1.2 Refreeze

Status: FAILED / REVIEWER_AUTHORITY_DECISION_REQUIRED

Completed: 2026-08-16T10:53:23+08:00

The mandatory pre-change support audit classified `Q-ARCHIVE-001` and
`Q-ELECTRONIC-001` as already-supported resources blocked only by normal-user
transport defects. `Q-XRD-001` is different: its frozen experimental resource
declares `1.9373 angstrom`, while the current released `structure.xrd` path is
CuKa-only at `1.54184 angstrom`. Worker execution preflight and the experimental
comparison Adapter both require compatible wavelengths and prohibit silent
reprojection. The frozen Case nevertheless requires both `structure.xrd` and
`structure.experimental_xrd_comparison` as an execution-ready path.

This is a qualification-authority conflict that cannot be corrected through
byte-safe or multi-resource transport. Per task rules, remediation stopped for
Reviewer decision. A preliminary transport draft was completely reverted;
production runtime changes, package changes, scientific fixture changes,
formal qualification executions, Jobs, Artifacts, and real LLM calls are all
zero.

Validation: `uv run pytest tests/test_phase10n3_experimental_xrd.py -q` passed
(`10 passed`), including typed mismatch rejection. The R1.1 package SHA-256
remained `bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`.
Blocker evidence and a self-hashed manifest are preserved at
`_qualification/evidence/phase_d_r2/attempt_01_blocked_authority_conflict/`.

```text
PHASE_D_R2 = BLOCKED / REVIEWER_AUTHORITY_DECISION_REQUIRED
BLOCKER = PHASE_D_R2_AUTH_001
Q_ARCHIVE_CLASS = ALREADY_SUPPORTED_RESOURCE_BUT_INPUT_TRANSPORT_DEFECT
Q_ELECTRONIC_CLASS = ALREADY_SUPPORTED_RESOURCE_BUT_INPUT_TRANSPORT_DEFECT
Q_XRD_CLASS = AUTHORITY_AMBIGUOUS
READY_FOR_PHASE_BC_R1_2_REFREEZE = NO
READY_FOR_PHASE_D_RESEAL = NO
READY_FOR_PHASE_E = NO
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
```

Commit/CI status: no commit, push, or CI was performed because the task stopped
at its mandatory qualification-authority gate.

## Phase D-R2.1 - Reviewer XRD Authority Resolution + Normal-User Input Transport Closure + R1.2 Refreeze

Status: completed

Completion time: 2026-08-16T14:09:02+08:00

The normal-user transport defect is corrected by committed candidate
`657d3f88849b4d561ebd3aca0a648667049306fc`: browser uploads use exact File/Blob
bytes, the backend verifies declared SHA-256 and byte size before materializing
raw bytes, and bounded multi-resource bundles publish atomically into one
dataset with parser/contract-based roles rather than file-order semantics.

Reviewer XRD Branch B1 remains unchanged. R1.2 replaces only the stale 1.9373
angstrom qualification fixture with real Figshare hydroxyapatite measurements
whose source instrument record declares Cu and `ActuallyUsedLambda=1.54184`,
paired with public-domain COD 4317043 hydroxyapatite. The old data were not
relabeled, reprojected, or synthesized. All other 15 Case directories are
byte-identical to R1.1.

The deterministic R1.2 package is
`_qualification/inputs/Phase_BC_R1_2_Qualification_Authority_Reconciled.zip`,
SHA-256 `187816077abdc154ad8b8c86f30af37ad4a6a66ed5471c52a2c3ed1a8f4bedc2`,
19,222,448 bytes and 138 sorted entries. Two builds matched; root/case hash
mismatches and missing files are zero; static and extracted validators PASS.

Validation: backend focused `57 passed`; frontend `460 passed`, typecheck PASS,
build PASS with existing bundler warnings; qualification/transport focused
`30 passed` with four benign pymatgen CIF warnings. Full repository suite PASS
is not claimed. Production remediation is committed locally, not pushed, and no
remote CI is claimed. Real LLM calls, formal qualification executions, Jobs,
Artifacts, and Phase E executions remain zero. Evidence is at
`_qualification/evidence/phase_d_r2_1/`.

## Phase D-R2.1 Final Candidate Correction

Status: completed

Completion time: 2026-08-16T15:27:41+08:00

The complete Phase D re-seal found that a durable SQL Project remained visible
after API restart, but upload-session creation still checked only the restarted
process's local Project projection. The authorized transport closure now
rehydrates only an exact existing PostgreSQL Project before opening the bounded
upload transaction. Unknown Projects remain rejected.

The final product candidate is
`51e45c9436bef73f0c8ea1ccc5eb681dba1d21b8`. R1.2 was deterministically
refrozen against that exact candidate as SHA-256
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`,
19,222,447 bytes and 138 sorted entries. Root/case mismatches and missing files
are zero; R1.1 remains unchanged. This correction changes no scientific,
Registry, support-disposition, Planner, Artifact, Renderer, Report, or Recipe
authority.

## Phase D R1.2 - Complete Live Qualification Environment Re-Seal

Status: completed / PASS

Completion time: 2026-08-16T15:27:41+08:00

The environment was sealed against product SHA
`51e45c9436bef73f0c8ea1ccc5eb681dba1d21b8` and R1.2 package SHA-256
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`.
The package has 16 Cases, zero root/case hash mismatches, and PASS results for
static executable, cross-field, entry-path, and CuKa compatibility validators.

Fresh Docker-network runtime checks passed for Alembic base-to-head and repeated
upgrade at `0008_phase_d_r1_namespace`, PostgreSQL, Redis, MinIO, current-SHA
API, current-SHA fresh worker, provider configuration, and an empty durable
qualification namespace. The Project survived API process restart and Workspace
history returned an empty contract-valid result.

Actual Chrome 151 uploaded the frozen Archive, CuKa XRD/Structure, and
Electronic Band/DOS inputs through the product UI. Browser bytes, frozen bytes,
server receipts, and independent MinIO reads matched for all five files. XRD
and Electronic companions were persisted in their respective same Dataset with
no file-order role authority. A page reload re-enumerated all three Datasets.
No console, page, or startup network error was observed.

Validation: focused backend/qualification/namespace `35 passed`; service-backed
container-network namespace `1 passed`; frontend `460 passed`; typecheck PASS;
build PASS with the existing Plotly/glslify warning. JSON parse, evidence
SHA-256 self-check, secret scan, private-path scan, and zero-execution checks
PASS. Evidence is under
`_qualification/evidence/phase_d/attempt_08_r1_2_reseal/`.

```text
PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED
READY_FOR_PHASE_E = YES
PHASE_D_R11_AUTH_001 = RESOLVED_BY_PRODUCT_TRANSPORT_FIX
PHASE_D_R11_AUTH_002 = RESOLVED_BY_PRODUCT_MULTI_RESOURCE_FIX
PHASE_D_R11_AUTH_003 = RESOLVED_BY_PRODUCT_MULTI_RESOURCE_FIX
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
BLOCKERS = []
```

Commit/CI status: the final candidate is committed locally; no push or remote CI
is claimed or required by this Phase D task. Phase E was not created or started.

## Phase E-R1.2 — Canonical Live-Agent Browser Qualification Restart

Status: failed / `BLOCKED_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T16:48:44+08:00

The R1.2 package was independently reverified at SHA-256
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`.
The fresh discovery campaign completed Q-DATASET-001. Q-COMPOSITION-001 first
failed because composition-only "materials table" wording was promoted to
dataset overview; the minimal Intent/Planner correction is committed as
`610de07887d7c221e377bc1d8d01882df9d5a6d2`, passed 88 focused tests, and the
Case then passed all three fresh Browser/DeepSeek execution turns.

Q-TABLE-001 reached a genuine frozen-authority contradiction. Its R1.2 contract
requires material-property-bound `table.numeric_summary`, `viz.histogram`,
`viz.correlation`, and `viz.scatter`, while the declared normal-user CSV produces
zero `material_property` columns and exposes no semantic mapping entry. The real
Planner therefore selected forbidden `dataset.materials_explorer`; changing the
DataProfile/ToolPlannerMetadata contract or frozen Case is qualification-relevant
authority drift and was not performed.

Validation: Q-DATASET and Q-COMPOSITION are `PASS_DISCOVERY`; Q-TABLE is
`BLOCKED_AUTHORITY_CONFLICT`; 23 real LLM calls are recorded across preserved
attempts; no provider fallback or fixture/package mutation occurred. Evidence
contains 170 valid JSON files and a 220-entry SHA256SUMS manifest with zero
mismatches, secret hits, or private-path hits. Final exact-SHA CI, final Phase D,
and final 16-Case requalification were not started after the hard stop.

Evidence: `_qualification/evidence/phase_e_r1_2/discovery_20260816_01/`.
Minimum Reviewer action: reconcile Q-TABLE-001 by supplying an already-authorized,
provenance-preserving material-property mapping/fixture, or revise its frozen
execution contract to the repository's generic-tabular authority.

Commit/CI status: local remediation commit
`610de07887d7c221e377bc1d8d01882df9d5a6d2`; not pushed; remote exact-SHA CI not
run because the qualification hard stop occurred before final-candidate closure.

## Phase B/C-R1.4 — Q-TABLE Explicit Property-Target Authority Reconciliation

Status: failed / `PHASE_BC_R1_4 / QUALIFICATION_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T18:20:00+08:00

The R1.4 non-production preflight retired qualification-only digest gating and
used content/provenance inspection plus current parser, DataProfile,
deterministic Intent, Eligibility, exact binding, and plan-cap paths. It made
zero real LLM calls and created zero formal qualification Jobs or Artifacts.
The historic R1.2 package and failed R1.3 evidence were preserved.

The real CC BY 4.0 JARVIS candidate correctly exposes `formation_energy`,
`band_gap`, and `density` as current material properties. With explicit natural
questions, numeric summary and correlation bind, but histogram and scatter
remain unbound because deterministic Intent supplies no material-property
targets. The all-16 audit also found deterministic ML target-semantic failures
for Q-ML-REG/UNC/CLASS, direct XRD comparison ineligibility, trajectory import
failure (`TRAJECTORY_NESTING_LIMIT_EXCEEDED`), and typed phonon failures
(`PHONON_SPECIES_ORDER_INVALID`). Therefore no R1.4 package was produced and
Phase D was not started.

Evidence: `_qualification/evidence/phase_bc_r1_4/attempt_01_authority_preflight/`.
Tests: the preflight completed twice consistently; 14 JSON evidence files parse;
the evidence has no active qualification integrity-key fields or checksum files;
no Phase E execution occurred.

## Phase B/C-R1.3 — Q-TABLE-001 Fixture Replacement and Binding Preflight

Status: failed / `PHASE_BC_R13_AUTH_001 / BLOCKED_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T17:52:17+08:00

R1.3 preserved the R1.2 package at SHA-256
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04` and
mechanically audited the current production Profile, deterministic Intent,
Eligibility, and ToolPlannerMetadata binding path. A real JARVIS-DFT-3D
candidate from Figshare DOI `10.6084/m9.figshare.6815699.v11` (CC BY 4.0)
produced three accepted material-property columns: `formation_energy`,
`band_gap`, and `density`. It therefore resolves the old fixture's Profile
defect, but cannot satisfy the frozen execution contract: the numeric summary,
distribution, and correlation turns are `INTENT_NOT_RECOGNIZED`; the scatter
turn has no target semantics and two unbound scalar property parameters.

Changing that outcome would require a frozen turn-contract revision or a
separately authorized normal-user property-target selection capability. Both
are outside this fixture-only task. No R1.3 ZIP, Phase D re-seal, or Phase E
execution was started. Evidence is in
`_qualification/evidence/phase_bc_r1_3/attempt_01_blocked_authority_conflict/`.

Tests: deterministic preflight rerun matched; focused Intent/Planner tests
passed `74 passed`; evidence JSON, SHA256SUMS, secret scan, private-path scan,
and zero-execution counters passed. The first pytest invocation lacked the
repository `PYTHONPATH` and failed during collection; the correctly configured
rerun passed. `REAL_LLM_CALLS=0`, formal qualification executions/jobs/artifacts
are zero. No commit or remote CI is claimed.

## Phase B/C-R1.4 — Final Result

Status: failed / `PHASE_BC_R1_4 / QUALIFICATION_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T19:10:11+08:00

The content-and-contract preflight completed all 16 Cases and 26 analysis
turns with `REAL_LLM_CALLS=0`, zero formal qualification executions, Jobs, and
Artifacts. It passes 9 Cases and blocks 7: Q-TABLE explicit histogram/scatter
target binding; deterministic ML readiness for REG/UNC/CLASS; XRD direct
comparison dependency eligibility; trajectory parsing at the nesting limit;
and typed phonon species-order validation. The old R1.2 Q-TABLE fixture also
reproduces its historical material-property readiness failure.

No R1.4 package was created, no Phase D re-seal was started, and Phase E remains
unstarted. The focused Intent/Planner suite passed `74 passed`; the broader
entry-slice command reported `83 passed, 2 errors` from its existing all-seven
ready assertion and is not claimed green. Evidence JSON parsing, secret scan,
private-path scan, zero-execution counter validation, and the no-active-
qualification-checksum-file policy check passed. Evidence:
`_qualification/evidence/phase_bc_r1_4/attempt_01_authority_preflight/`.

## Phase B/C-R1.5 — Comprehensive Qualification Authority and Executability Reconciliation

Status: failed / `PHASE_BC_R1_5 / QUALIFICATION_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T20:08:17+08:00

R1.5 classified all seven R1.4 blockers before correction. It closed the three
ML representation/question paths, modeled XRD's same-Plan theoretical-artifact
dependency, repaired the bounded trajectory validator's numeric-array scanner
defect, verified the phonon ordering metadata path, and corrected the stale
seven-demo entry-slice expectation. The fresh deterministic preflight passes
15 of 16 Cases across all 26 declared analysis turns.

The remaining blocker is `Q-TABLE-001`. The verified JARVIS candidate exposes
the approved `formation_energy`, `band_gap`, and `density` facts, but the
released non-ML normal-user Intent contract emits no exact material-property
target semantics. Required `viz.histogram` and `viz.scatter` bindings therefore
cannot be completed without a Reviewer decision on a qualification-relevant
product contract. No target guessing, semantic expansion, fixture fabrication,
or Tool metadata relaxation was used.

Tests: trajectory/parser/entry-slice `53 passed, 4 warnings`; Intent/Planner/
entry-slice `85 passed, 4 warnings`. The prior `83 passed, 2 errors` entry-slice
failure is resolved with no skipped or deleted test. No R1.5 authority package,
Phase D re-seal, or Phase E execution was created. `REAL_LLM_CALLS=0` and all
formal qualification Jobs, ToolCalls, and Artifacts are zero. Evidence:
`_qualification/evidence/phase_bc_r1_5/`.

## Q-TABLE Explicit Material-Property Target Intent Closure + Phase B/C-R1.6 + Phase D Re-Seal

Status: completed / `PHASE_BC_R1_6 = PASS / QUALIFICATION_AUTHORITY_PRODUCT_INTENT_ALIGNED_AND_REFROZEN`; `PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED`.

Completion time: 2026-08-16T23:49:21+08:00

The committed product now provides AnalysisIntent 1.1's bounded exact
DataProfile-backed material-property targets. It preserves AnalysisIntent 1.0
readability and rejects unknown, ambiguous, stale, foreign-dataset,
non-material-property, duplicate/conflicting, incomplete, and same-axis
scatter targets. No property vocabulary, fuzzy/first-column selection, unit
guessing, scientific Tool/algorithm, ToolPlannerMetadata prerequisite, support
surface, or AnalysisPlan cap changed.

The R1.6 authority uses the real JARVIS material-property table and four
natural Q-TABLE turns for `table.numeric_summary`, `viz.histogram`,
`viz.correlation`, and `viz.scatter`. The independent content-and-contract
preflight passes all 16 Cases and 26 declared analysis turns, with one valid
expected pre-Plan rejection and zero authority conflicts. The package is
`_qualification/inputs/Phase_BC_R1_6_Qualification_Authority_Reconciled.zip`.
Its integrity evidence is package inventory, schema/contract validation,
protected direct content comparison, and direct byte-for-byte double-build
comparison; active qualification checksum/digest gates are not used.

Phase D independently reran the complete preflight and sealed a fresh official
migration namespace at `0008_phase_d_r1_namespace`. PostgreSQL, Redis, MinIO,
backend, fresh Worker, browser app shell, provider configuration, and required
credential presence passed. Browser evidence proves normal-user binary ZIP and
bounded same-dataset multi-resource import/readiness for Archive, XRD, and
Electronic inputs; restart evidence proves Project and persisted object-storage
durability. Formal namespace counts for Intent, Plan, Job, ToolCall, Artifact,
Report, and Recipe are all zero. `REAL_LLM_CALLS=0` and formal qualification
execution remains zero. Phase E was neither created nor started.

Tests: focused backend `159 passed`; focused product regression `124 passed`;
frontend typecheck PASS; frontend Vitest `460/460`; production build PASS with
existing Plotly/glslify warnings; sealed Docker-network durable namespace test
`1 passed`. Full repository pytest is disclosed as `1514 passed, 20 failed,
51 skipped`; failures are 19 obsolete historical queue assertions and one
pre-existing Phase 13 evidence-size mismatch, with no R1.6 product/runtime
regression. Remote CI was not run or claimed.

Evidence: `_qualification/evidence/phase_bc_r1_6/` and
`_qualification/evidence/phase_d/attempt_09_r1_6_reseal/`.

## Phase E-R1.6 — Canonical Live-Agent Browser Qualification Restart

状态：失败 / `PHASE_E / BLOCKED_AUTHORITY_CONFLICT`

完成时间：2026-08-17T02:20:46+08:00

本次任务从新的 R1.6 campaign state 开始并使用真实 Browser、真实 DeepSeek、
真实 Planner、Queue、Worker、Artifact、Workspace/Renderer 和 Report 链路。
Q-TRAJECTORY-001 的真实浏览器上传、资源 Profile 和第一 turn
`structure.trajectory_viewer` 均通过；第二 turn 真实生成了包含
`trajectory.diffusion`、`trajectory.msd`、`trajectory.rdf` 的 3-step
依赖计划，但 Worker 对 `trajectory.msd` 与 `trajectory.rdf` 返回
`TOOL_RESOURCE_LIMIT / TRAJECTORY_TOO_LARGE`，Job 失败。

根因：冻结资源实际为 650 frames、516 atoms，而当前已发布
`trajectory_analytics` Adapter 的正式上限为 200 frames、5000 atoms；冻结
Case 要求完整 supplied time range。未提高上限、未截断/重采样轨迹、未合成
科学数据、未修改 R1.6 package，因此该问题属于冻结 authority 与已发布
科学资源边界冲突，不是可在 Phase E 内无审查修复的普通 runtime bug。

修改文件：
`_qualification/evidence/phase_e_r1_6/discovery_20260817_r1_6_01/cases/Q-TRAJECTORY-001/TRAJECTORY_RUNTIME_CAP_BLOCKER.json`、
`TASKS.md`、`results.md`。历史 evidence 与历史任务未删除或改写。

测试/执行结果：Q-TRAJECTORY 第一 turn 真实 Browser/DeepSeek/Planner/Queue/
Worker/Artifact/Renderer/Report PASS_DISCOVERY；第二 turn真实 Job 失败。
`REAL_LLM_CALLS > 0`，未发生 handcrafted Intent/Plan/Job/ToolCall/Artifact/
Report/Recipe injection。未执行后续 Cases，因此不能声明 16/16，也不能声明
Phase E PASS。Phase E-R1.6 队列任务按硬阻塞规则保留为失败，后续需要新的
有效 fixture 或经 Reviewer 批准的产品/authority 变更。

## Phase B/C-R1.7 — Trajectory Resource-Cap Authority Reconciliation

状态：已完成 / `PHASE_BC_R1_7 = PASS / TRAJECTORY_RESOURCE_CAP_AUTHORITY_RECONCILED_AND_REFROZEN`

完成时间：2026-08-17T08:36:15+08:00

Reviewer 决议已落实为 qualification fixture replacement，而非产品 cap 扩展。
新 Q-TRAJECTORY 使用 Lei et al. Cage-1 500 K 真实 AIMD 源的首个预先定义连续
窗口 frames 0-14：15 frames、516 atoms、0-1050 fs、固定晶胞、PBC 全开、
source-backed unwrapped Cartesian coordinates。所有 atoms/species/order、
coordinates、cell/PBC 与 timestamps 保持；无结果驱动选择、插值、重采样、
atom subset 或运行时截断。

Registry 资源上限元数据已对齐既有 Adapter 强制上限，未改变算法、工具集、
科学支持面或运行时行为。通用 cap-aware preflight 可在正式执行前复现旧
650-frame authority 的 frame cap、RDF pair-evaluation cap 和 wrapping authority
冲突；新 fixture 的 viewer/MSD/diffusion/RDF 资源与依赖预检全部 PASS。

全量结果：16/16 Cases、26/26 analysis turns、expected rejection PASS；
resource-cap conflicts 0，unpreflightable required Tools 0，preflight test errors 0。
15 个非轨迹 Case 的保护内容逐文件字节一致。R1.7 package 为
`_qualification/inputs/Phase_BC_R1_7_Qualification_Authority_Reconciled.zip`，
116 个排序条目、16 个唯一 Case、无缺失/重复，双构建直接字节相等；未生成
checksum/digest/fingerprint qualification manifest。

修改文件：Registry cap metadata、R1.7 authority/preflight scripts、聚焦测试、
R1.7 package/evidence、`TASKS.md`、`results.md`。测试为 `31 passed`；未运行
remote CI。`REAL_LLM_CALLS=0`，正式 qualification executions/Jobs/ToolCalls/
Artifacts 均为 0。产品及预检变更已提交；Phase D R1.7 由独立任务执行。

## Phase D R1.7 — Live Qualification Environment Re-Seal

状态：已完成 / `PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED`

完成时间：2026-08-17T09:06:46+08:00

Phase D 针对当前稳定 committed product state 与独立 R1.7 authority 从头执行。
fresh PostgreSQL database 已通过正式 migration 到
`0008_phase_d_r1_namespace`；Redis、MinIO、API、frontend 和 fresh Worker 均
健康。Provider 配置可解析且所需 credential 存在，但没有发起真实 LLM 调用。

独立 cap-aware preflight 再次得到 16/16 Cases、26/26 analysis turns PASS，
resource-cap conflicts 和 unpreflightable required Tools 均为 0。Browser 使用
正常上传入口导入新 Q-TRAJECTORY fixture，实际 Profile 为 15 frames、516 atoms、
0-1.05 ps、Cartesian/unwrapped、fixed cell、PBC 全开，trajectory resource-cap
readiness PASS。fresh namespace 中 AnalysisIntents、AnalysisPlans、Jobs、
ToolCalls、Artifacts、Reports 和 Recipes 均为 0。

测试结果：聚焦回归 `31 passed`；current runtime/qualification 回归
`212 passed`；frontend Vitest `460/460`、typecheck/build PASS；service-backed
trajectory integration `1 passed`。完整 pytest 为
`1534 passed, 20 failed, 51 skipped`；20 项是既有历史 queue/evidence 断言，
不涉及当前 R1.7 runtime path，因此不声明仓库全量 CI PASS。remote CI 未运行。

证据位于 `_qualification/evidence/phase_d/attempt_10_r1_7_reseal/`。
`READY_FOR_PHASE_E=YES`，但本任务没有创建或启动 Phase E。

---

任务：Account → Project Authorization Contract Closure（2026-08-20）
状态：已完成
完成时间：2026-08-20
修改文件：`apps/api/mdi_api/access.py`（复用既有统一边界）、`apps/api/mdi_api/routers/project_history.py`、`apps/api/mdi_api/routers/secured_runtime.py`、`apps/api/mdi_api/phase1_demo.py`、`apps/api/mdi_api/main.py`、`apps/api/mdi_api/routers/secured_planner.py`、`tests/test_project_access.py`、`persistent/ARCHITECTURE_DECISIONS.md`
修改摘要：项目历史在同步前授权；旧 Phase 1 事件流、Demo 数据和解释 Evidence 均继承 Project 授权；项目列表按 owner/member 返回且不泄露私有项目；补充 viewer 写拒绝、跨用户列表过滤和过期会话拒绝测试。未修改 CI、迁移或历史数据。
测试结果：授权/历史/Planner/legacy demo 相关测试 `23 passed`；新增授权测试 `4 passed`；无失败。
提交/CI：未提交；CI 未修改。

补充：新版 Console 增加可发现的项目搜索入口；受保护深链首次未登录时保留安全的
同源 `returnTo`；历史 `/analysis` 与 `/workspaces` 先完成服务端授权解析，再跳转
新版 Project Research；无法解析时只给非泄露兼容状态。`npm run typecheck` PASS；
`npm run test -- --run app/components/ProductPages.test.tsx` = 3 passed；未修改 CI、
迁移或数据。

任务名称：Phase E-R1.7 — Canonical Live-Agent Browser Qualification Restart
状态：已完成
完成时间：2026-08-17T15:55:43+08:00
最终候选：`d7c267f9d5cac1397cbe56368e8de94f0b9d69e3`

修改摘要：完成 durable ProjectHistoryView/1.0、项目历史首页、独立 Dataset
Workbench 与 Planner 恢复导航；修复电子 Band+DOS 显式工具对和 provider stale
resolution 未进入单次 repair budget 的缺陷。最终 candidate9 使用独立 PostgreSQL
database、Redis、fresh API/Worker 和 frontend，Phase D attempt23 通过。随后在
`final_20260817_03` 中从 Case 1 开始完成同一 SHA 下 16/16 Cases、26/26 turns，
真实 DeepSeek、Queue/Worker、36 ToolCalls、151 Artifacts、26 Workspaces、26
grounded Interpretations、26 Report Preview/Finalize、26 Recipes 全部验证通过，
Recipe executed=0，unexpected fallback/injection/fatal error=0。

测试结果：capability planner `57 passed`；Project History `1 passed`；frontend
focused `36 passed`；typecheck PASS；production build PASS；compileall PASS；Phase D
R1.7 attempt23 PASS；final campaign 16/16 PASS。最终 evidence 共 471 files，其中
359 JSON 全部可解析，secret scan 0 命中，`git diff --check` PASS。remote CI 未运行，
未执行 push/deploy。

证据：`_qualification/evidence/phase_d/attempt_23_r1_7_candidate9_reseal/` 与
`_qualification/evidence/phase_e_r1_7/final_20260817_03/`。

---

任务名称：Release Closure — Full Repository Green + Push + Remote CI
状态：已完成 / `PASS / FULL_REPOSITORY_GREEN_AND_REMOTE_CI_VERIFIED`
完成时间：2026-08-17T19:42:17+08:00

Phase E-R1.7 canonical qualification 保持
`PASS / R1_7_CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE`，未重开、
未重跑或改写 16-Case/26-turn authority 与 evidence。Release Closure 独立完成
仓库测试债清理：初始本地 21 项和 clean-checkout 追加暴露的 7 项均为过时历史
queue/evidence/docs assertions；共 28 项改为当前 queue invariant、内容级 evidence
inventory/JSON/semantic validation 或受支持入口断言。真实当前产品缺陷 0，
qualification-relevant regression 0。

本地验证：backend `1563 passed, 0 failed, 0 errors, 53 deselected, 75 warnings`；
service-backed PostgreSQL/Redis/MinIO/migration `50 passed, 0 failed, 0 errors,
0 skipped`；frontend Vitest `465 passed`，TypeScript typecheck 和 production build
PASS。Chromium/Firefox/WebKit、390x844 及当前全部 browser/replay gates PASS，
包括 Phase 10M-4 Artifact Gallery headful CI replay。compile、lock、diff、schema、
queue、secret 和 private-path checks PASS；`REAL_LLM_CALLS=0`。

提交/CI：Release Closure changes 正常提交并 push 到 `origin/master`；GitHub
Actions run `32024851926` 的 Unit、Linux/Windows semantic replay、Frontend
Typecheck & Build、PostgreSQL/Redis/MinIO service-backed integration 全部 PASS。
production runtime-affecting release-owned uncommitted diffs 为 0；已分类的本地
历史 qualification/evidence 与用户工作区改动保持未提交且未改写。

部署：`NOT_STARTED`。`READY_FOR_DEPLOYMENT_REVIEW=YES`，开放 Release blockers 0。

---

任务名称：UX-V1.3 — Design Documentation + High-Fidelity Prototype
状态：已完成
完成时间：2026-08-18T01:11:04+08:00

修改摘要：在 `design/ux-v1.3/` 创建正式 UX-V1.3 设计资产、Chrome reference
research、Design Reality Matrix、状态/响应式/可访问性规范和隔离高保真原型；
在 `.interface-design/system.md` 建立长期 Scientific Research Workbench 视觉系统。
Prototype 覆盖 Landing、Console、Projects、Project Overview、Project Data 的
Table/Structure/Trajectory/XRD/Electronic/Volumetric/Archive/Unsupported 状态、
Research 的九种状态、增量结果、Inspector、Quick Preview、Reports 与 Report Reader。

修改文件：`.interface-design/system.md`、`design/ux-v1.3/**`、
`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`、
`results.md`。

测试结果：`node --check design/ux-v1.3/prototype/prototype.js` PASS；Chrome
实际审阅 1920x1080、1440x900、1280x800 和约 391x844 CSS viewport；关键 Research
states、Data/Inspector、Quick Preview、Escape/focus restoration、图标 accessible
name、字体加载和默认内部术语泄漏检查 PASS。`git diff --check` PASS。移动截图通道
出现工具层拼贴异常，已通过 Chrome DOM 尺寸、滚动/overflow 和 Inspector geometry
复核并记录为验证限制；未运行 production build/test，因为本任务未改生产代码。

提交/CI：未提交、未推送、未运行 remote CI；本任务是设计资产和隔离 prototype，
不触发 release/deploy 生命周期。部署：NOT_STARTED。

---

任务名称：Current Product Acceptance — 16-Case Chrome UI Verification
状态：已完成（16/16 最终补测通过，原始失败记录保留）
完成时间：2026-08-18

使用本机 Google Chrome 真实执行上传、项目创建、研究问题提交、等待分析、截图和
结果采集。两次完整 16-case 运行分别保留在
`_qualification/evidence/current_product_acceptance_16_cases/run_2026-08-18T14-18-48-070Z/`
和 `run_2026-08-18T14-32-02-801Z/`；首轮与第二轮的失败均未删除。随后对
Q-ATOMIC-VIEW-001、Q-ML-REG-001、Q-PHONON-001、Q-COMPOSITION-001、
Q-COORD-001、Q-TRAJECTORY-001 逐案进行新增 Chrome 补测，最终均为
`PASS_OR_RECORDED`，索引见
`_qualification/evidence/current_product_acceptance_16_cases/FINAL_RECONCILIATION.json`。

修改摘要：验收 runner 将 `INTENT_UNSUPPORTED` 纳入合法预期拒绝；上传页面根据
声子 band/DOS 文件名绑定 typed phonon companion import 与 schema contract，修复
Q-PHONON 在真实 UI 上传链中的 bundle 解析失败；补充对应前端回归测试。未删除任何
项目、Dataset、Conversation、Job、ToolCall、Artifact、Report 或历史 qualification
evidence，Phase E-R1.7 未重开。

测试结果：完整 Python `1576 passed, 51 skipped, 0 failed`；frontend Vitest
`475 passed`；TypeScript typecheck PASS；production build PASS（仅既有 Plotly/
glslify critical-dependency warning）；`python -m compileall -q apps/api/mdi_api`
PASS；`git diff --check` PASS。API 持久化核验确认本次项目、Dataset、analysis、Job、
ToolCall 和 Artifact 仍可读取。部署：NOT_STARTED；CI：未修改。
---

任务：Production UI/UX Reconstruction — Full Production Completion（2026-08-19 研究结果闭环续作）
状态：处理中（核心产品验收仍有明确债务）
完成时间：2026-08-19
修改摘要：修复 correlation heatmap 的结构化 Evidence 投影；真实 Q-TABLE Research 运行已完成并保留失败/成功轮次、助手前后消息、Job、ToolCall、Artifact、Interpretation 与结果引用；结果标题和主要发现不再暴露内部 correlation subject 或 raw machine wording；记录 API 重启时必须使用 `uv run ... --app-dir apps/api`，避免 `mdi_adapters` 导入失败造成误报 500。补充 bounded numeric trajectory scan、source viewer 与持久化投影相关验证记录。
测试结果：`pytest tests/ -q` = 1584 passed, 51 skipped, 75 warnings；`npm run test -- --run` = 79 files / 494 tests passed；`npm run typecheck` PASS；独立输出目录 `MDI_NEXT_DIST_DIR=.next-acceptance npm run build` PASS，仅保留既有 Plotly/glslify critical-dependency warnings；`python -m compileall -q apps/api packages services tests` PASS；`git diff --check` 无 whitespace error。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — 46-project scientific presentation batch
状态：已完成（保留明确验收债务）
完成时间：2026-08-20
修改摘要：使用生产 Chrome 路由和已配置服务端 Provider 批量复核 39 个保留科学
Project 的 Data、Research、Result、Evidence 与 Report 展示；统一 Project 命名为
`Case NN · Q-ID · Run NN`；对 35 个过时终态 Run 使用可逆 project-scoped archive，
Reports 默认只显示最新高可用 Run。四个原始空 Project 与三个测试产生的零子对象
Project 在 SQLite 备份后物理删除；没有删除任何科学数据链或历史 qualification evidence。
新增/更新批量 Chrome 证据位于
`design/ux-v1.3/evidence/production/batch-20260820/`。
测试结果：42 Projects / 39 Datasets / 109 Jobs / 615 Artifacts / 208 Messages /
42 Interpretations；Python `1603 passed, 51 skipped`；Vitest `79 files / 511 tests`；
`npm run typecheck` PASS；production build PASS；`python -m compileall -q apps/api services packages tests`
PASS；`git diff --check` PASS。增量非终态结果 Chrome 观测为 NOT_OBSERVED，真实读屏设备
为 NOT_VERIFIED，BZ source ingestion 与 BYOK 为明确非本轮范围。提交/CI：未提交；
CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Project 命名与 Phase 10 能力可发现性修正
状态：已完成
完成时间：2026-08-20
修改摘要：依据批处理前 46-Project 备份重新判定 provenance；38 个 Q-ID 科学项目
统一为 `Case NN · Q-ID · Run NN`，3 个历史会话与 1 个历史数据项目使用
`其他 · ... · Run NN`。未把 Case 项目错误伪装为 Phase 项目。为所有 Case 增加中文
科学能力说明和真实 Phase 10 能力来源；Projects 页面新增 Case/Phase/其他分组、自然
数值排序及按名称、Q-ID、Phase、能力说明搜索。数据库改名前备份为
`mdi_phase5.db.pre-phase10-discoverability-20260820.sqlite`，未修改或删除 Dataset、Job、
Artifact、Message、Evidence、Interpretation 或 Report。
测试结果：ProductPages Vitest `5 passed`；TypeScript typecheck PASS；focused
`git diff --check` PASS；Chrome `/projects` 实际显示 42 个项目，搜索 `Phase 10H`
仅返回 Q-PHONON 的 Run 01/02，中文能力说明和 Phase 10H/10I 来源可见。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Remaining debt classification（2026-08-20）
状态：已完成（无可自行消解的产品债务）
完成时间：2026-08-20
修改摘要：补充语义可访问性审计证据，标明真实硬件读屏与浏览器非终态 Artifact 截图的工具/执行时序限制，并将旧 Chrome 网络和 Volumetric 说明标为历史。`next lint` 已实际尝试，因缺少 ESLint 配置而进入 Next 弃用的交互式初始化；该项保留为工程卫生债务，不通过修改脚本伪造 PASS。BYOK、多 Dataset Job、ZIP 持久目录和完整 Phase E live campaign 继续按既定范围排除。
测试结果：`npm run lint` = `ENGINEERING_DEBT`（交互式初始化，未产生代码检查结果）；`python -m compileall -q apps/api packages services tests` PASS；此前完整 Python `1599 passed, 51 skipped`、Vitest `79 files / 510 tests`、typecheck/build PASS；`git diff --check` PASS。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Scientific presentation and Phase 10 closure（2026-08-20）
状态：已完成（核心生产闭环已实现；明确验收债务保留）
完成时间：2026-08-20
修改摘要：完成共享 Scientific Viewer adapter/registry 的源数据与结果投影收拢；修复声子组合结果优先级与重复输出、通用科学曲线的极值保真抽样、轨迹/布里渊区/材料模型/电子结构用户文案；Research roles、Project authorization、Evidence/Report projection 继续沿用服务端事实与现有执行内核。新增当前生产 Chrome 证据至 `design/ux-v1.3/evidence/production/desktop/`，未删除历史 qualification 数据、项目、Dataset、Conversation、Job、ToolCall、Artifact、Report 或历史 evidence。
测试结果：完整 Python `1592 passed, 51 skipped, 90 warnings`；Vitest `79 files / 503 tests passed`；授权/Research/Provider/Interpretation/Report 聚焦集 `142 passed`；`npm run typecheck` PASS；production build PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api packages services tests` PASS；`git diff --check` PASS。Chrome 复核 Table/Inspector、Trajectory、Electronic、Volumetric summary、Phonon result、Report Reader、Model Settings modal 均无横向溢出；截图桥接可用并已保存桌面证据。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。仍保留真实边界：增量结果在非终态前的 Chrome 观测为 `NOT_OBSERVED`；Volumetric source 3D 与 BZ source ingestion 为 `NOT_SUPPORTED`；真实读屏设备未验证；完整 Phase E live 16-case 不重开。

---

任务：Production UX Correction — Structure Viewer language closure（2026-08-20）
状态：已完成
完成时间：2026-08-20
修改摘要：将三维结构查看器的工具栏、键盘辅助说明、超晶胞、裁剪、相机、导出、测量、位点/键合检查器和可访问语义摘要统一为 zh-CN；保留公式、Å、schema、诊断码等 canonical scientific content。Chrome 刷新验证真实 WebGL canvas、无横向溢出、无主要英文 Viewer labels，保存最终结构证据。
测试结果：Structure Viewer focused Vitest `25 passed`；前端 typecheck PASS；Chrome structure route layout `scrollWidth === clientWidth`，canvas present，English primary-label scan empty；`git diff --check` PASS。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Semantic accessibility closure（2026-08-20）
状态：已完成（源码/DOM 语义闭环；真实读屏设备仍未验证）
完成时间：2026-08-20
修改摘要：为生产 Research Timeline 增加工作台、对话消息和会话记录语义；补齐搜索弹窗 Tab 循环、Escape 关闭与状态/错误角色；为 Data loading/error/scientific table 增加 status/alert、可访问表名和 caption；研究 splitter 纳入键盘 Tab 顺序并保持 aria-valuenow 边界。新增 Research/Product focused accessibility assertions。
测试结果：`npm test -- --run app/components/ResearchPages.test.tsx app/components/ProductPages.test.tsx` = 2 files / 11 tests passed；`npm run typecheck` PASS；`git diff --check` PASS。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。真实 screen-reader device = NOT_VERIFIED。

---

任务：Production UX Correction — Structure Viewer ordinary-user projection closure（2026-08-20）
状态：已完成（普通用户层级清理；技术详情和高级导出保留）
完成时间：2026-08-20
修改文件：`apps/web/app/components/viewer-scene/ViewerSceneRendererSurface.tsx`、`ViewerExportPanel.tsx`、`ViewerMeasurementPanel.tsx`、`ViewerSceneRendererSurface.test.tsx`、`apps/web/app/globals.css`、`persistent/ARCHITECTURE_DECISIONS.md`
修改摘要：默认隐藏/折叠 renderer/version、图形性能指标、原始 scene/manifest/recipe 下载和导出诊断；新增“高级导出”“技术详情”渐进披露；将 Formula/Species/Lattice、Export size presets、Measurement coordinate mode、导出状态和失败文案统一为 zh-CN；不改变 Three.js、结构数据、校验、导出 contract 或执行内核。
测试结果：viewer-scene 全量 focused Vitest `14 files / 91 tests passed`；单独 `ViewerSceneRendererSurface.test.tsx` `23 passed`；`git diff --check` PASS。`npm run typecheck` 当前被共享工作树中未提交的 `apps/web/app/components/ResearchPages.tsx` 语法错误阻断（该文件非本任务修改，需主任务合并前修复）。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UI/UX Reconstruction — Full Production Completion（最终闭合）
状态：已完成
完成时间：2026-08-20
修改摘要：完成账号到 Project 的服务端授权边界、Research Timeline 与持久化助手前后消息、可信运行过程投影、Scientific Interpretation/Result/Report 投影、共享 Scientific Viewer Registry，以及 Table、Structure/Atoms、Trajectory、XRD、Electronic、Phonon、BZ Result、Volumetric、ZIP detected-content 和 Generic fallback 在新版 IA 中的接入。最后修复 Volumetric source channel 的通用列表截断、严格 Phase 10J source projection、attached source payload 加载、125×72×60 Gaussian-cube 等值面/精确切片/直接体渲染、通用标量错误模块投影和中文产品文案。保留历史项目、Dataset、Conversation、Job、ToolCall、Artifact、Report 与 qualification evidence；未重开 Phase E。
测试结果：完整 Python `1599 passed, 51 skipped, 90 warnings`；完整 Vitest `79 files / 510 tests passed`；`npm run typecheck` PASS；`MDI_NEXT_DIST_DIR=.next-acceptance-final-4 npm run build` PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api services` PASS；`git diff --check` PASS。Chrome 真实验证保留的 Volumetric 125×72×60 source 可渲染 24,532 顶点/47,242 三角形等值面、精确晶格切片和 WebGL2 直接体渲染；BZ supporting result 真实渲染；390 与 200% 证据保存在 `design/ux-v1.3/evidence/production/`。
验收边界：增量 Artifact 的非终态事件顺序由真实两步 Adapter 自动化验证，因当前本地 Worker 同步完成而没有浏览器中间态截图；真实硬件屏幕阅读器未运行，但源码与 Chrome DOM 语义审计通过；BZ 无 normalized source object，因此 Source View 为 NOT_SUPPORTED、Result View 为 VERIFIED；BYOK、CI modernization、完整 16-case live requalification 均不属于本任务。
LLM 角色闭合：Research Turn Orchestrator 已接入可选真实 Provider，输入边界为问题/数据集/已验证 Plan，严格 JSON 失败时 grounded fallback；Report Composer 已接入 finalize，引用、来源身份和数值事实均经 Scientific Result 校验后才持久化；运行过程仍为零 LLM 调用。
提交/CI：未提交、未推送；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Final documentation reconciliation（2026-08-20）
状态：已完成
完成时间：2026-08-20
修改摘要：将 `persistent/TASK_BOARD.md` 的生产重构条目标记为“已完成（明确验收边界）”，并在 `persistent/OPEN_QUESTIONS.md` 中关闭已由当前 Research Turn/Report Composer 严格角色合同取代的旧问题描述。未改变历史 Phase 证据、数据库、CI 或运行时行为。
测试结果：`python -m compileall -q apps/api packages services tests` PASS；Model Settings Vitest `5 passed`；此前最终全量 Python `1599 passed, 51 skipped`、Vitest `79 files / 510 tests`、typecheck/build PASS；`git diff --check` 无 whitespace error。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Continuous Product Quality — Global UX / Scientific Capability / Accessibility Improvement Wave 1
状态：已完成
完成时间：2026-08-20T22:52:15+08:00
修改摘要：修复 Data 科学表格的单位猜测问题，改为仅显示未声明单位并使用中文语义标签；为 Research 增加初始加载/错误/重试状态、研究记录弹层焦点恢复与中文会话状态；在移动端加入 Research 对话/工作台单面板切换并降低滚动冲突；将 Reports 列表和 Report Reader 改为显式加载/错误/结果优先层级，并优先 PRIMARY_FIGURE / PRIMARY_TABLE 作为主结果。
测试结果：`npm test -- --run app/components/ResearchPages.test.tsx app/components/ProductPages.test.tsx` = 2 files / 27 tests passed；`npm run typecheck` PASS；`npm ci` in apps/web PASS after removing a locked Next process.
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。Chrome 真实视觉证据待重连用户 Chrome 标签页后补验。

Wave 1 follow-up（2026-08-20）：补齐 validated objectType 优先路由，修复 phonon→electronic 误判；结果加载改为 selected Artifact 必需、伴随 Artifact best-effort；通用表格披露完整行数与 preview cap；未知 source object 使用诚实 unsupported 状态。Focused `ProductPages` + `ScientificViewerAdapter.effect` = 19 passed；typecheck PASS；Chrome 桌面复查 Q-TABLE-001（64 行）和 Q-TRAJECTORY-001 Research 时间线 PASS。390px 视口仍待用户实际调整后验收。
追加回归：完整 `pytest tests/ -q` = 1607 passed, 51 skipped, 90 warnings（239.24s）；完整 Vitest = 80 files / 529 tests passed；无失败。最终 Chrome 390×845 验收 PASS：Research 对话/工作台单面板切换且 viewport scrollWidth=390；Data 页面无 viewport 横溢出，表格使用独立横向滚动；行选择与模型设置关闭按钮均为 44px；Inspector Escape 恢复“选择第 1 行”；Report 列表与 Reader 无 viewport 横溢出。

---

任务：Continuous Product Quality — Research Timeline / Scientific Workbench Wave 2
状态：已完成
完成时间：2026-08-21
修改文件：`apps/api/mdi_api/db.py`、`apps/api/alembic/versions/0014_research_session_run_bindings.py`、`apps/api/mdi_api/routers/research.py`、`apps/api/mdi_api/routers/secured_planner.py`、`apps/api/mdi_api/routers/planner.py`、`apps/api/mdi_api/routers/project_history.py`、`apps/web/app/lib/planner-api.ts`、`apps/web/app/lib/product-api.ts`、`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/components/workspace/WorkspaceGenericPlot.tsx`、`tests/test_project_access.py`、`tests/test_research_session_run_migration.py`、`docs/13_SHARED_SCHEMA_SPEC.md`、`persistent/ARCHITECTURE_DECISIONS.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`。
修改摘要：将 Research Session → Planner Run 关联正规化为项目级、一个 Job 只能归属一个 Session 的可审计投影；迁移从旧 assistant payload 回填且不删除历史记录，旧数据库在迁移窗口保持可读并明确标记 `migration_required`。Planner 请求携带经授权校验的 `researchSessionId`，解释完成后服务端自动补齐 post-run 助手投影；failed 投影有幂等保护。历史 Run 恢复增加部分加载保留、事件/Artifact 合并去重、孤立 Run 不自动挂入首个会话，以及 Data/Report/Research 互链。Provider 与 Session 读取失败均有可重试状态；图表超限提示不再重复出现在无障碍树中。
测试结果：完整 Vitest `80 files / 539 tests passed`；完整 `pytest tests/ -q` `1611 passed, 51 skipped, 90 warnings`；`npm run typecheck` PASS；`MDI_NEXT_DIST_DIR=.next-wave2-build npm run build` PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api packages services tests` PASS；Alembic `0014_research_session_run_bindings (head)`；`git diff --check` PASS。针对性新增/更新 Research、授权与迁移回归全部通过。
Chrome 验收：真实保留项目 `Case 11 · Q-STRUCTURE-RDF-001 · Run 02` 在 Chrome 桌面双栏与 390px 单面板下通过；历史结果经异步加载恢复，Data/Report 回链可用，移动 `scrollWidth === clientWidth`。提交/CI：未提交；CI/GitHub Actions 未修改；未部署。已知限制：本地 Worker 同步完成导致非终态 incremental Artifact 未在浏览器中观测；真实硬件 screen-reader 未运行；Plotly 构建警告仍属依赖层既有问题。

Wave 2 follow-up（2026-08-21）：将 Research Turn 的确定性用户文案从“我会使用 …”
调整为“本次分析将以数据集“…”为范围”，并统一 unsupported 文案的数据集边界表达，
并在前端展示层兼容旧的 pre-run 前缀，因此无需重写历史 Message。保留原始科学数据集名称不做翻译或猜测。`tests/test_product_research_scope.py` = 9 passed；
Research/Product Vitest = 37 passed；`npm run typecheck`、compileall、`git diff --check` PASS。

---

任务：Continuous Product Quality — Exact Structure Planning / Evidence / Workbench Closure
状态：已完成
完成时间：2026-08-21T09:47:57+08:00
修改文件：`services/llm/mdi_llm/capability_planner.py`、`services/llm/mdi_llm/providers.py`、`apps/api/mdi_api/routers/planner.py`、`apps/api/mdi_api/routers/research.py`、`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/globals.css`、相关 Python capability/evidence/research tests、`persistent/*.md`。
修改摘要：补齐中文“径向分布+局部环境”的精确识别与 CrystalNN/VoronoiNN 操作型澄清；算法确认后严格生成配位 producer、局部环境 consumer 与 RDF 三步计划，并保留局部环境+实验 XRD 的四工具组合合同。超出 262144-byte 读取上限的已支持 Artifact 改为有界跳过并披露限制，不再阻断其余安全 Evidence；Research/Report 将配位覆盖率、范围和算法限制转成用户可读中文。桌面 Research 改为动态视口固定壳体、左右独立滚动、320-640 px 鼠标/触控/键盘 splitter，进入路由时归零根滚动。
真实验收：使用已授权本地账号在 `http://localhost:3000` 完成 Run `job_07f702a3c9af42259ec5d14f`；Plan 仅含 `structure.coordination_crystalnn`、`structure.local_environment_polyhedra`、`structure.rdf`，完成 4 个科学输出并渲染 5 个 RDF 系列 / 400 个值。1280x720 实测全局栏、项目导航和 620 px 工作台无根滚动，长对话与结果独立滚动；Grounded finding/limitation 恢复成功。
测试结果：完整 `pytest tests -q` = `1618 passed, 51 skipped, 90 warnings`；完整 Vitest = `82 files / 552 tests passed`；Research focused = `24 passed`；修复后的 Phase 13 composite capability/preflight + capability planner = `92 passed`；`npm run typecheck` PASS；`MDI_NEXT_DIST_DIR=.next-continuous-wave3 npm run build` PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api packages services tests` PASS；Alembic = `0014_research_session_run_bindings (head)`；`git diff --check` PASS。
提交/CI：未提交、未推送；CI/GitHub Actions 未修改；未部署。真实硬件 screen reader 与浏览器中的非终态 incremental Artifact 仍未验证，本轮未重开 Phase E。

---

任务：Remaining Acceptance Closure + Evidence-Based CI Rationalization + Commit/Push
状态：已完成
完成时间：2026-08-21
修改摘要：基于 workflow、仓库脚本、测试标记、路线文档和远程失败/成功运行记录，区分当前产品门禁与已封存历史证据。默认 Python 单元门禁排除明确标记且依赖忽略目录 `_qualification/` 的 qualification 模块；旧 Phase 13-4 Help 浏览器检查保留为历史证据但移出 push gate；17 个历史 Phase 10/12 浏览器步骤合并为一个手动 dispatch 编排步骤，仍逐项执行并在失败时停止。当前 Phase 12-6/12-7 改为验证项目级 Research 工作台，补齐 skip link、splitter 和确定性只读 fixture。未移除科学重放、跨平台、服务集成、迁移、完整前端、typecheck、build 或当前可访问性/UX 门禁。
测试结果：本地默认 Python `1586 passed, 1 skipped, 82 deselected, 75 warnings`；qualification `30 passed`；Vitest `83 files / 554 tests`；typecheck PASS；production build PASS；Phase 12-6/12-7 Playwright PASS；Phase 12 evidence integrity `10 passed`；focused contract tests `16 passed`；`uv lock --check`、compileall、YAML parse、`git diff --check` PASS。
提交/CI：`501313a`、`ef86945`、`0df1e97` 已推送；current HEAD `0df1e97ee21533e8f9d620d0810cea6129a71bd3` 的 GitHub Actions run `32454012102` 全部通过（Unit Tests、Scientific Replay Linux/Windows、Frontend、Service-backed Integration）。未部署或发布。用户临时/历史未跟踪文件未加入提交。

---

任务：Continuous Product Quality — Research history navigation Wave 3
状态：已完成
完成时间：2026-08-21T16:30:12+08:00
修改文件：`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/globals.css`、`persistent/ARCHITECTURE_DECISIONS.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`、`results.md`。
修改摘要：将 Research 记录浮层补全为高频历史导航：本地标题搜索、记录数量、空/无匹配状态、长列表滚动边界、当前记录标识、Escape/外部点击/选择关闭与焦点恢复。移动搜索输入固定为 16px。依据数据库事实将 `sessions.status=active` 从误导性的“进行中”改为“可继续”，并保留 queued/running Planner Job 的“进行中”语义；未改变会话归属、Planner、Artifact、Report 或执行权限。
测试结果：Research focused Vitest `25 passed`；完整 Vitest `83 files / 554 tests passed`；`npm run typecheck` PASS；独立 production build PASS。真实已授权 Structure/RDF 项目在 1280x720 验证搜索自动聚焦、无匹配反馈、外部关闭、`active` 显示“可继续”、面板边界和文档无横向溢出。
提交/CI：实现提交 `ca8a8b4bcab8de4ad6c094c8cd6f9641200a969b` 已推送；current-HEAD GitHub Actions run `32463181783` 全部通过（Unit Tests、Scientific Replay Linux/Windows、Frontend、Service-backed Integration）。未部署或发布；用户未跟踪文件未加入提交。

---

任务：Continuous Product Quality — Mobile Research navigation Wave 4
状态：已完成
完成时间：2026-08-21T16:52:00+08:00
修改文件：`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/test/phase12-6-responsive-accessibility-browser-evidence.mjs`、Phase 12-6 当前浏览器证据矩阵/截图、`persistent/ARCHITECTURE_DECISIONS.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`、`results.md`。
修改摘要：完善移动 Research 的单面板交互：对话/工作台现在使用完整 tab/tabpanel 关联、roving tabindex、Arrow/Home/End 键盘导航和焦点迁移；服务端返回已验证 Planner Job 后自动切换到工作台，让用户立即看到真实运行过程和增量结果。桌面双栏、权限、Planner、Artifact 和 Report 执行边界不变。
测试结果：Research focused Vitest `25 passed`；完整 Vitest `83 files / 554 tests passed`；typecheck PASS；独立 production build PASS；Phase 12-6 浏览器证据 Chromium/Firefox/WebKit PASS，Chromium 390x844 的 tabNavigation、singlePanelVisibility、touchTargets、reducedMotion 和无横向溢出全部 PASS；证据完整性 `5 passed`。
提交/CI：实现提交 `3dccce8a71c5dbfe68a12c0a63af76f5b96a5a38` 已推送；current-HEAD GitHub Actions run `32464949831` 全部通过（Unit Tests、Scientific Replay Linux/Windows、Frontend、Service-backed Integration）。未部署或发布；用户未跟踪文件未加入提交。

---

任务：Continuous Product Quality — Global navigation and structured details Wave 5
状态：已完成
完成时间：2026-08-21
修改文件：`apps/web/app/components/ProductShell.tsx`、`apps/web/app/components/ProductShell.test.tsx`、`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/components/workspace/WorkspaceArtifactGallery.tsx`、`apps/web/app/components/workspace/ScientificWorkspaceShell.test.tsx`、`apps/web/app/globals.css`、`apps/web/test/phase12-7-cross-product-browser-evidence.mjs`、Phase 12-7 当前浏览器证据、`persistent/*.md`、`TASKS.md`。
修改摘要：项目内 Data、Research、Report 路由持续显示全局搜索、模型设置和账户入口；账户操作收拢为支持 Escape、外部点击、Tab、Arrow/Home/End 与焦点恢复的菜单，并验证 390px 无横向溢出。Workspace/科学图表技术详情改为有界 JSON 预览，提供对象/数组摘要、截断提示和空/不可用状态。Research 结果页技术详情显示运行/方案身份、可查看输出数与 JSON Artifact 可用性，不加载或暴露密钥、BYOK 或可执行内容。历史科学、服务集成、迁移与当前 UX 门禁保持不变。
测试结果：针对性 Vitest `54 passed`；完整 Vitest `84 files / 559 tests passed`；`npm run typecheck` PASS；独立 production build PASS（仅既有 Plotly/glslify warnings）；Phase 12-7 Chromium/Firefox/WebKit、1280x720 与 390x844 PASS；Phase 12-7 evidence integrity `5 passed`；`git diff --check` PASS。
提交/CI：实现提交 `e0b84e5` 已推送；current-HEAD GitHub Actions run `32473415268` 全部通过（Unit Tests、Frontend Typecheck & Build、Service-backed Integration、Scientific Replay Linux/Windows）。未部署或发布；用户未跟踪文件未加入提交。

---

任务：Continuous Product Quality — Research activation and capability-aware guidance Wave 6
状态：已完成
完成时间：2026-08-22T02:41:38+08:00
修改文件：`.interface-design/system.md`、`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/globals.css`、`apps/web/test/phase12-7-cross-product-browser-evidence.mjs`、`docs/phase12/evidence/phase12_7_cross_product_ux_validation/*`、`persistent/ARCHITECTURE_DECISIONS.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`、`results.md`。
修改摘要：在空白 Research 对话中增加紧凑首次研究区，从所有数据集的 Project History `datasetType`、`readyCapabilities` 与 `semanticRoles` 构建大小写无关、稳定排序且最多三项的建议。formation-energy/band-gap 关系只在两个精确语义同时存在时出现，能力不足时使用中性概览。建议选择只切回对话、填充并聚焦 Composer，不创建 Session、Message、Plan 或 Job。无数据 owner/editor 获得 Upload 入口，viewer 只见只读说明；右侧工作台仅保留数据与最近研究上下文。未修改后端、schema、Planner、Worker、Tool Registry、Adapter 或 CI 策略。
测试结果：Research focused Vitest `32 passed`；完整 Vitest `84 files / 565 tests passed`；`npm run typecheck` PASS；`npm run build` PASS；Phase 12-7 Chromium/Firefox/WebKit、1280x720、390x844 浏览器验证 PASS；Phase 12-7 evidence integrity `5 passed`；`git diff --check` PASS。`npm run lint` 因现有脚本调用未配置且交互式的 `next lint` 无法独立运行；production build 的 lint/type validity 阶段与远端 Frontend job 均通过。
设计验收：Senior Designer 适用检查项 `43/43`；首次路径、加载/错误/空/只读/历史状态、键盘焦点、44px 触控、移动单面板、reduced-motion 与无横向溢出均有实现或浏览器证据。
提交/CI：实现提交 `1032d10a4e0a9111c02246c95cc55f34d6711370` 与完成记录提交 `c1a5a242cbb8f1293c12bc9a6f48001334ad39fa` 已推送；current-HEAD GitHub Actions runs `32514219078`、`32514730110` 的五个 jobs 全部成功（Unit Tests、Frontend Typecheck & Build、Service-backed Integration、Scientific Replay Linux/Windows）。未部署或发布；`CODEX_HANDOFF.md` 保持未跟踪且未纳入提交。

---

任务：Agent-2.0 Phase 1 — Core Domain Foundation
状态：已完成
完成时间：2026-08-22T18:41:46+08:00
修改文件：`apps/api/alembic/versions/0015_agent2_scientific_objects.py`、`0016_agent2_research_turns.py`、`0017_agent2_scientific_results.py`；`apps/api/mdi_api/agent2_errors.py`、`agent2_repositories.py`、`db.py`、`main.py`、`access.py`、`routers/agent2.py`；`apps/api/mdi_api/scientific_objects/`、`research_agent/`、`scientific_results/`；Agent2 unit/API/migration/domain/service-backed tests；integration Alembic helper及现有 integration fixtures；`.github/workflows/ci.yml`；`docs/agent2/`、共享 schema/index/roadmap 与 persistent 权威记录；`AGENT2_PHASE1_RESULTS.md`。
修改摘要：在实际 Alembic head `0014` 后按顺序加入 Scientific Object、Research Turn 与 Scientific Result Snapshot 三个迁移；实现稳定逻辑对象与不可变版本、精确历史引用、项目隔离、原子版本/Turn sequence 分配、CAS 状态机、不可变上下文快照、独立 Registry skeleton、严格 Pydantic contracts、Result Snapshot persistence、授权 REST/SSE 和只读 Scientific Object API。POST Turn 只持久化现有 USER Message、RECEIVED Turn 与 TURN_RECEIVED event，不调用 LLM/Planner，不创建 AnalysisPlan/Job/ToolCall。现有执行内核、62 Tool、Adapter、Viewer 与前端保持增量兼容。
测试结果：Agent2 focused `21 passed`；SQLite migration upgrade/downgrade/re-upgrade `2 passed`；隔离 PostgreSQL migration/concurrency/receive `1 passed`；完整非 integration Python `1607 passed, 1 skipped, 83 deselected`；完整 Vitest `84 files / 565 passed`；typecheck、独立 production build、compileall、`git diff --check` PASS。Current-HEAD CI service integration `51 passed, 0 skipped, 0 failed, 0 errors`，其余 Unit、Frontend/Phase 12-6/12-7、Linux/Windows scientific replay 全部成功。
提交/CI：实现提交 `1553183be2fb561f2ca5e71c2e3d9be2ed31db30` 和 integration compatibility 修复 `9af205b8b411e87e05cce4a05067f676c87bfb23` 已推送；current-HEAD GitHub Actions run `32567895104` 五个 jobs 全部成功。未部署或发布；`CODEX_HANDOFF.md` 保持未跟踪且未纳入提交。
明确未实施：Phase 2 的 Orchestrator LLM、ResearchTurnDecision、语义引用解析、Capability eligibility/planner、Capability→AnalysisPlan binding、Job attachment、production Result projector、Scientific Interpreter、grounding validator、assistant scientific response、Report Composer、全量 Data backfill 与 Viewer integration。

---

任务：Agent-2.0 Phase 2 — Research Turn Orchestration & Context Resolution
状态：已完成
完成时间：2026-08-22T20:48:08+08:00
修改文件：migration `0018_agent2_orchestration_decisions`；`apps/api/mdi_api/research_agent/context/`、`llm/`、`orchestration/`、`evaluation/`；Agent2 repositories/service/router/config/UoW/registry；Phase 2 unit/API/migration/service-backed tests；CI integration gate；`docs/agent2/`、共享 schema/roadmap/index、persistent 权威记录与 `AGENT2_PHASE2_RESULTS.md`。
修改摘要：实现授权且有界的候选组装、固定引用优先级、确定性歧义澄清、不可变 Context Snapshot/fingerprint、`StructuredLLMClient` 与现有 DeepSeek transport adapter、versioned prompt、单次有界 repair、`ResearchTurnDecision 1.0`、Requirement/constraint/ref/action 决策校验、不可变 decision persistence、无事务 LLM 边界、幂等 Redis `turn_id` 唤醒与 AgentTurnProcessor。ANSWER/CLARIFY 完成对话回合；ANALYZE/CONTINUE_ANALYSIS 停在 READY_TO_PLAN；其余 downstream action 仅安全分类。所有 Phase 2 路径保持 AnalysisPlan/Job/ToolCall delta 为 0，未实现或偷跑 Phase 3 能力规划、Tool binding、执行、Interpreter、Report Composer 或数据 mutation。
测试结果：focused Phase 2/API `36 passed, 4 live-gated skipped`；deterministic C01-C15 `15/15`、canonical/paraphrase `60/60`；真实 DeepSeek canonical `5/5`、eligible canonical/paraphrase `48/48`；SQLite migration round-trip `1 passed`；隔离 PostgreSQL/Redis Phase 1+2 service gates `2 passed`；完整非 integration/qualification Python `1638 passed, 5 skipped, 84 deselected`；完整 Vitest `84 files / 565 tests`；typecheck、隔离 production build、compileall、Alembic head、`uv lock --check` 和 `git diff --check` 通过。
提交/CI：实现提交 `9285e0e035ad90af88cd7d9b729e2073a969648f` 已推送；GitHub Actions run `32573620585` 全部通过：Unit `1638 passed`，Service-backed Integration `52 passed / 0 skipped / 0 failed / 0 errors`，Frontend tests/typecheck/build/Phase 12-6/12-7，Scientific Replay Linux/Windows。闭环记录提交将再次以 current-HEAD CI 核验。未部署或发布；`CODEX_HANDOFF.md` 保持未跟踪且未纳入提交。
明确未实施：Capability Resolver/eligibility、CapabilityPlan、Capability→Tool/AnalysisPlan binding、Job attachment、Execution Supervisor/JobEvent progress、production Result projector、Scientific Interpreter/grounded final response、full research memory、Report Composer、Data Management execution、professional Viewer integration 与全 62-Tool capability mapping。

---

任务：Agent-2.0 Phase 3 — Scientific Capability Resolution & Planning
状态：已完成
完成时间：2026-08-22T23:04:38+08:00
修改文件：migration `0019_agent2_capability_planning`；`apps/api/mdi_api/research_agent/capabilities/`、`planning/`；Agent2 errors/repositories/schema/service/router/state machine/orchestration worker；Phase 3 deterministic、migration 与 service-backed tests；CI integration gate；`docs/agent2/`、共享 schema/roadmap/index、persistent 权威记录与 `AGENT2_PHASE3_RESULTS.md`。
修改摘要：实现 `PLAN_READY` 的 pre-Job 状态边界、不可变 CapabilityResolution/CapabilityPlan、九个 manifest 覆盖五类 canonical 科学能力、注册式 deterministic preconditions、精确版本 eligibility、稳定 registry fingerprint、唯一策略 fast path、受限 StructuredLLM planner 与一次 repair、opaque capability/source/result refs、严格 requirement/DAG/port/cardinality/constraint validation，以及 Capability→Tool→现有 AnalysisPlan 0.2 的确定性绑定和 PlanValidator 复核。历史 Result 仅在投影出已授权 exact-version ScientificObject output 时复用；artifact-only legacy Result fail closed。所有成功路径只新增 AnalysisPlan，保持 Job/ToolCall/Artifact/Worker execution delta 为 0。
测试结果：Phase 3 deterministic `19 passed, 1 deselected`，P3-C01 至 P3-C20 全覆盖；live DeepSeek `1 passed`；combined Agent2 `69 passed, 5 deselected`；完整 backend `1657 passed, 1 skipped, 90 deselected`；隔离 PostgreSQL/Redis service-backed Agent2 Phase 1/2/3 `3 passed`；frontend Vitest `84 files / 565 passed`；typecheck、隔离 production build、compileall、Alembic `0019` head、SQLite migration round-trip、`uv lock --check` 与 `git diff --check` 通过。现有 `npm run lint` 仍调用交互式、已弃用的 `next lint`，因此未虚报独立 lint PASS。
提交/CI：实现提交 `855fe3f46298882971227bda684f2529a5823469` 已推送；current-HEAD GitHub Actions run `32580235322` 的 Unit Tests、Service-backed Integration、Frontend Typecheck & Build（含 Phase 12-6/12-7）和 Linux/Windows Scientific Replay 五个 jobs 全部成功。未部署或发布；`CODEX_HANDOFF.md`、`docs/agent2.zip` 与无关 Phase 12 evidence 修改未纳入提交。
明确未实施：Job creation/attachment、queue execution、Execution Supervisor、`PLAN_READY → QUEUED`、Job/ToolCall progress、incremental/production ScientificResult projection、Scientific Interpreter/final scientific answer、long-session semantic memory、Report Composer、Data Management execution、professional Viewer integration、全 62-Tool Agent2 mapping 与 Tool Pack/plugin ecosystem。
---RESULT---
任务名称：Agent-2.0 Phase 4 — Execution Integration & Scientific Progress Projection
状态：已完成
完成时间：2026-08-23T03:09:53+08:00

修改摘要：从持久化 `PLAN_READY` ResearchTurn 接入既有 Job、QueueWorkerRuntime、
ToolCall、Artifact 与 JobEvent 执行内核；新增 `CANCELING`、`RESULT_PENDING`、
不可变 ExecutionSummary、确定性 capability-level 进度、增量 Artifact 输出、
取消竞态收敛、授权 API/SSE 和紧凑响应式 Research activity。Worker 仅凭
`job_id` 从 PostgreSQL/MinIO 恢复 exact-version 输入；执行阶段 LLM 调用为 0，
成功/部分成功均停在 `RESULT_PENDING`，不提前创建 ScientificResult 或助手最终回答。

测试结果：focused Phase 4/API/exact-source `21 passed`；Phase 2 context/processor
回归 `27 passed`；完整非 integration backend `1671 passed, 6 skipped,
86 deselected`；fresh PostgreSQL/Redis/MinIO selection `54 passed,
14 deselected` 且 selected skip 为 0；frontend `85 files, 568 passed`；
typecheck、production build、compileall、`uv lock --check`、科学重放、
Alembic head、浏览器 1440x900/390x844 与 `git diff --check` 均通过。
真实两步 XRD fresh Worker 在 Job 非终态时已观测 step 1 Artifact 和增量输出。
`npm run lint` 仍调用废弃的交互式 `next lint`，未声明独立 lint 通过。

提交/CI：实现提交 `4384db3ae0e92bdd604b8486b738f400eb8b4a97` 已推送；
current-HEAD GitHub Actions run `32592517424` 的 Unit、service-backed integration、
Frontend Typecheck & Build、Linux/Windows scientific replay 五个 job 全部成功。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 9 Provenance-First Redesign & Final Closure
状态：部分完成
完成时间：2026-08-24T20:30:00+08:00

修改摘要：确认根因属于 CASE_A（legacy Result/reuse fixture defect），而非
当前 Result provenance producer。真实 PostgreSQL/Redis/MinIO Phase 5 服务链
创建了新的 RDF/XRD ScientificResultSnapshot，均带 exact ScientificObject 与
ScientificObjectVersion refs；真实 Phase 8 report worker 创建了新 grounded report，
其 viewer_sources 只由 persisted Result provenance 推导。新增 deterministic regression
确保 fresh refs 可解析、legacy 空 refs 不会发生名称/最新版本替换。

测试结果：Phase 5 service-backed `2 passed`；Phase 8 service-backed `4 passed`；
Phase 9 service-backed `3 passed, 0 skipped`；Phase 8/report/viewer focused
`24 passed, 4 skipped`；`git diff --check` 通过。浏览器扩展当前没有可见标签页，
因此 fresh PostgreSQL report 的 authenticated browser、fresh table mobile 以及
最终 current-head CI 未伪报通过；旧 legacy fallback 仍保持安全。

提交/CI 状态：本轮 provenance regression 与文档待提交；未 push，未产生 C/D
exact-SHA CI。保留所有用户已有 working-tree 文件。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 9 Final Fixture & Worker Closure (round 2)
状态：部分完成
完成时间：2026-08-24T22:35:00+08:00

修改摘要：修复本地 SQLite 与 Artifact 默认路径的 cwd 依赖；修正表格验收
fixture 使用真实项目/用户授权并通过 upload、parse/profile、artifact manifest
和 ScientificObject promotion 创建 canonical scientific table；修正 report
fixture 的 UUID/user 参数；用 Windows RQ SimpleWorker 完成真实 selection ->
ResearchContextSnapshot handoff，并验证第二次 selection 不修改第一份快照；
更新 AGENT2_PHASE9_RESULTS.md 与 persistent 设计记录。未创建 Phase 10 能力。

测试结果：focused backend `44 passed, 5 skipped`；viewer/selection `22 passed`；
frontend `90 files / 582 tests passed`；typecheck PASS；production build PASS
到 `.next-phase9-closure`；compileall、uv lock、git diff --check PASS。认证浏览器
表格桌面/移动路径 PASS，selection worker 两个 turn 均 ANSWERED。Report -> exact
Viewer 仍因历史 RDF bundle 缺少合法 source_object_refs 未闭合；service marker
在本地缺 PostgreSQL credentials 时 `3 skipped`，未虚报 PASS。

提交/CI 状态：本轮尚未提交或 push；HEAD 仍为 `bcdf0627127976b582480881eaf20bcfe7bd9d56`，
因此没有新的 current-head CI。Phase 9 保持 PARTIAL，不能进入 Phase 10。
---END---


---RESULT---
任务名称：Agent-2.0 Phase 9 registry parity hardening and closure qualification
状态：部分完成
完成时间：2026-08-24T15:10:00+08:00

修改摘要：补齐后端 ScientificViewerRegistry 对 `analysis.rdf` 与
`reciprocal.brillouin_zone` 的确定性描述，使 exact-version viewer projection
与前端 registry 在进程边界保持一致；未引入新的科学对象 authority、计算、Job、
Artifact 或 LLM 路径。保留原有 Phase 9 实现及用户工作树文件。

测试结果：后端 Phase 9 deterministic `5 passed`；前端 Viewer registry/shell
`3 passed`；current-head GitHub Actions run `32702466953` 对文档闭环 SHA
`3da0a04389438ec25b322339300350e27ebfc15c` 成功，五个 required jobs 全部通过，
Service-backed Integration `69 passed, 0 skipped, 0 failed, 0 errors`，Phase 9
三个专用测试均显式通过。

未闭合：authenticated browser Structure/Table/RDF/XRD/Report evidence、stale
和 unsupported fallback 的 desktop/mobile golden paths。浏览器已到达本地登录
页面，但未在缺少 action-time credential confirmation 时输入密码，因此没有虚报
浏览器 PASS。后续可在用户确认后重新完成该层验收。

提交/CI：修复提交 `52f3b176c7b8107c3ba894834a51bf52ae4d3dde`、文档闭环提交
`99c3fc82937eb07ebddaae9a4bfe2d65af23aa43`，以及 provenance 提交
`f669e9603ea11880de25245fb8b795508e8432b8`、`3da0a04389438ec25b322339300350e27ebfc15c`
已推送，且 `HEAD == origin/master`；
未部署或发布。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 8 — Grounded Scientific Report Composer & Persisted Scientific Presentation
状态：已完成
完成时间：2026-08-24T12:30:00+08:00

修改摘要：完成 0024 科学报告持久化、结构化 Report Composer、确定性 grounding
校验、identity-only fresh worker、授权 API、科研语义 Report List/Reader，以及
RDF/XRD fresh service-backed report qualification。报告绑定不可变
ScientificResultSnapshot 与 validated ScientificInterpretation，禁止 raw Artifact、
内部 UUID、秘密和 provider transcript 进入 composer；报告生成保持零科学重算，
支持幂等 reopen、CURRENT/STALE/SOURCE_MISSING/INVALIDATED 语义和 legacy Report
读取兼容。Phase 6–8 相关 UI 与文档同步完成。

测试结果：Phase 8 deterministic `14 passed, 4 deselected`；Phase 6–8 focused
`31 passed, 8 deselected`；Agent2 focused `112 passed, 13 deselected`；full backend
`1754 passed, 80 skipped, 75 warnings`；Phase 8 service `4 passed, 0 skipped`；
gated live DeepSeek `4 passed`；frontend `87 files / 576 passed`；typecheck、build、
compileall、Ruff、`uv lock --check`、migration round-trip、PostgreSQL base→head、
browser desktop/390px 与无横向溢出均通过。`npm run lint` 未声明（仓库仍使用
deprecated interactive `next lint`）。

提交/CI：实现提交 `57041f38240b6c8d50ca3bc44813da0a15deed87` 与闭环文档提交
`41f2b102bd122fe50e34bcfe033639688a195fb2` 与最终记录提交
`05720f882877e03c76e3499a5708b9df3276d6e7` 均已推送；最终 current-head
GitHub Actions run `32690181703` 与最终记录 SHA 完全一致，Unit、Frontend Typecheck
& Build、PostgreSQL/Redis/MinIO Service-backed Integration、Linux Replay、Windows
Replay 五个 jobs 全部成功；Phase 8 service selection `4 passed, 0 skipped`。
用户既有 working-tree 文件未纳入提交，未实施 Phase 9。
---END---

---TASK---
任务名称：Agent-2.0 Phase 7 Closure Round 2 — Interpretation Contract & Final Closure
状态：处理中
完成时间：2026-08-24T00:00:00+08:00

修改摘要：确认 Windows fresh Worker timeout 根因是 isolated Docker PostgreSQL 的
IPv4-only listener 与 Windows `localhost -> ::1` 解析不匹配，保留 `localhost ->
127.0.0.1` test-only 修复且不增加 180 秒 execution bound；新增 readiness 后的
startup/execution timing 证据。将 Phase 7 fresh interpretation fixture 从空 finding
修正为引用真实 persisted Fact/ResultItem 的合法 Phase 6 `ScientificInterpretationOutput`
，未修改 grounding/schema validator。更新 Phase 7 service qualification 证据。

测试结果：Phase 6 fresh service `2 passed, 0 skipped`；Phase 7 dedicated service
`4 passed, 0 skipped`；Phase 7 focused `121 passed, 9 skipped`；gated live DeepSeek
`3 passed`；RDF readiness timing `startup 6.844s`, `queued->terminal 2.688s`，
execution timeout unchanged. Full backend/frontend/full current-head CI 尚未完成。

提交/CI：尚未提交、push 或取得 final exact-SHA CI；任务保持处理中。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 7 Closure
状态：处理中
完成时间：2026-08-24T00:00:00+08:00

修改摘要：诊断 isolated fresh Phase 4 timeout。DB-backed timeline 与 py-spy
确认 Windows `localhost` 首先解析到不可达 IPv6 `::1`，fresh Worker 卡在
`psycopg.connect()`，尚未创建 ToolCall；测试 URL helper 规范化到
`127.0.0.1`，180 秒上限未增加。修复 deterministic result/object priority
解析缺陷：显式 Result 压过低优先级对象，同级 Result ambiguity 正确进入
CLARIFY。增加 Phase 7 live DeepSeek gated cases（previous result、8 Å
continuation、ambiguity），三例通过；扩展 dedicated service fixture/CI
选择草案，但 service closure 仍因独立 interpretation Worker 的既有
Phase 6 grounding/schema fixture contract 失败而未闭合，未将未通过选择强行
纳入 CI。

测试结果：Phase 7 memory `8 passed`；live DeepSeek `3 passed`；最小 fresh
Phase 4 `1 passed in 177.98s`；ruff/compileall 通过。Dedicated Phase 7
PostgreSQL/Redis/MinIO selection reached real RDF/XRD execution/result stages,
but interpretation task was consumed and failed grounding/schema validation，
因此 selected service gate 尚未通过。未执行 commit/push/current-head CI；
未声称 Phase 7 COMPLETE。

提交/CI：未提交，未推送；仍需 fix-forward。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 7 — Multi-turn Research Memory, Result Reuse & Continuation
状态：处理中
记录时间：2026-08-23T15:45:00+08:00

修改摘要：新增 `0023_agent2_research_memory`、durable/versioned Session state、
auditable context items、explicit Session constraint/goal extraction、authorized
object/result pin APIs、bounded non-adjacent Result/Finding retrieval、opaque candidate
priority、bounded CompactResearchContext，以及 existing Phase 6 zero-computation
result reuse / Phase 3–6 continuation integration。

测试结果：Phase 7 deterministic `6 passed`；Agent2 focused `119 passed, 6 skipped`；
full backend `1737 passed, 67 skipped`；compileall、uv lock、diff-check PASS；SQLite
migration `0022 → 0023 → 0022 → 0023` 与 fresh base-to-head PASS。Frontend
`85 files / 571 passed`、typecheck、isolated production build PASS；authenticated
Research browser 在 1280x720 与 390x844 均无横向溢出。Phase 7 专用 service
selection 已改为自包含 RDF/XRD reuse fixture；isolated fresh PostgreSQL/Redis/MinIO
完成 base→0023，但 inherited Phase 4 RDF execution Worker 180s timeout，结果
`2 errors, 0 passed, 0 skipped`，尚未进入 Phase 7 reuse。Live provider 与
current-head CI 也未执行。最终 dedicated selection 为默认 `2 skipped`、
services-enabled `2 errors`；最终完整 backend 已重跑且通过，因此仍仅因
service/live/CI closure gaps 不声明 Phase 7 COMPLETE。

提交/CI：尚未提交或推送；current-head CI 尚未运行。用户无关 working-tree 文件
保持未纳入。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 5 — Production Scientific Result Projection
状态：失败（实现报告判定 PARTIAL）
完成时间：2026-08-23T10:02:00+08:00

修改摘要：新增 `0021_agent2_scientific_result_projection` 和 `RESULT_READY`；
复用既有 immutable `scientific_result_snapshots`；生产化 typed
ScientificResultBundle、九个 canonical result-projector 注册、稳定 source
fingerprint、exact-version relevance、授权结果 API 与最小 RESULT_READY UI。
所有数值事实需要 committed Artifact locator，image-only Artifact 不产生数值；
Artifact 读取在 DB transaction 外，多能力输入按 step/ToolCall/Artifact lineage
隔离。projection 阶段 LLM/Job/ToolCall/assistant final delta 均为 0。

测试结果：Phase 5 deterministic `5 passed`；focused Agent2 closure `55 passed,
1 skipped`；Alembic migration `1 passed`；完整 non-integration backend `1706
passed, 6 skipped, 56 deselected`；frontend `85 files / 569 passed`；typecheck、
compileall、diff-check 通过。current-HEAD CI run `32611474526` 的 Unit、
PostgreSQL/Redis/MinIO integration（无 skip）、Frontend build/typecheck 与
Linux/Windows scientific replay五个 jobs 全部成功。

未闭合：缺少 Phase 5 专属 fresh service-backed RDF/XRD projection worker
qualification、390px browser result-state evidence，以及按每个 production
Artifact contract 完整定义的领域 metric/figure/table projector 映射，因此未将
`AGENT2_PHASE5` 标记 COMPLETE。实现提交 `5cfe6ae55fa9f3f23277495f7b8b12e49c74e4d9`
已推送；未部署或发布。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 5 Closure — Production Result Qualification & Canonical Projector Specialization
状态：已完成
完成时间：2026-08-23T12:10:00+08:00

修改摘要：完成自动 identity-only result projection wakeup 与 fresh RQ worker；
完成九个 canonical production Artifact schema 的 typed adapter/domain-aware
projector coverage；完成真实 PostgreSQL/Redis/MinIO RDF 与 XRD two-step
fresh-process qualification、390px browser RESULT_READY evidence、队列失败恢复、
重复/并发投影幂等和数值事实 locator 校验。保持 projection 阶段 LLM、Job、
ToolCall、ScientificResult 重算和 Phase 6 interpretation 为零。

测试结果：closure focused `20 passed`；fresh service-backed RDF/XRD `2 passed,
selected skip 0`；完整 non-integration backend `1691 passed, 6 skipped,
88 deselected`；frontend `569 passed`；typecheck、production build、compileall、
`uv lock --check`、migration、`git diff --check` 均通过。浏览器 390x844：
`scrollWidth=390`、`bodyScrollWidth=390`、`hasOverflow=false`，RESULT_READY
结构化 RDF 输出可见。

提交/CI：closure implementation `1fd18bf995ee6ffc38cbfacf6f5af1fca54a7b9f`
已推送；该实现的 authoritative exact-SHA GitHub Actions run `32616753779`
五个 jobs 全部成功。未部署或发布；无关工作树文件未纳入提交。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 6 — Grounded Scientific Interpretation & Assistant Final Response
状态：已完成
完成时间：2026-08-23T13:56:37+08:00

修改摘要：实现 `RESULT_READY → INTERPRETING → COMPLETED/PARTIAL` 自动生产路径；
复用 server-managed DeepSeek structured transport、ResearchTurn、immutable
ScientificResultSnapshot 与 existing ASSISTANT ResearchMessage。新增 bounded
result-only Interpreter input、ScientificInterpretationOutput 1.0、不可变 grounded
interpretation、Fact/Evidence/ResultItem 引用校验、定量值/单位/answer-lead grounding、
一次 bounded repair、deterministic AssistantResponseProjector、identity-only Redis/RQ
队列、fresh interpretation worker、授权 API/SSE，以及 Phase 2 existing-result
interpretation 的 zero-execution handoff。PARTIAL、STALE、SOURCE_MISSING、INVALIDATED
由代码注入必要状态说明；raw Artifact 与未验证模型输出不能进入最终消息。

测试结果：Phase 6 deterministic `8 passed, 1 skipped`；Agent2 Phase 2-6 focused
`89 passed, 6 skipped`；live DeepSeek `1 passed, 8 deselected`；fresh
PostgreSQL/Redis/MinIO RDF/XRD `2 passed, selected skip 0`；完整 backend
non-integration `1731 passed, 65 skipped`；frontend `85 files / 570 passed`；
typecheck、production build、compileall、`uv lock --check`、SQLite migration
`0022 → 0021 → 0022`、clean PostgreSQL migration、`git diff --check` 和 authenticated
390x844 no-overflow browser verification 均通过。Phase 6 阶段 AnalysisPlan、Job、
ToolCall、Artifact、ScientificResultSnapshot delta 均为 0；正常 provider call 为 1，
最多一次 repair；未知引用、幻觉数字与单位转换均被 deterministic gate 拒绝。
`npm run lint` 仍指向 deprecated interactive `next lint`，未声明独立 lint PASS。

提交/CI：实现提交 `2b9ad6155a7c63dfd3efe15868aeaae72e172116` 已推送；
authoritative exact-SHA GitHub Actions run `32621337675` 的 Unit Tests、Frontend
Typecheck & Build、PostgreSQL/Redis/MinIO Service-backed Integration 和 Linux/Windows
Scientific Replay 五个 jobs 全部成功。未部署或发布；用户既有 working-tree 修改
未纳入提交。

明确未实施：full multi-turn Research Memory、semantic long-session retrieval、
general continuation/re-analysis memory、Report Composer、Data Management mutations、
full 62-tool capability mapping、professional Viewer expansion、Viewer linked-selection、
Tool/plugin ecosystem 和 Phase 2 ORCHESTRATING lease/reaper。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 7 Closure Round 2 — Interpretation Contract & Final Closure
状态：已完成
完成时间：2026-08-24T01:00:00+08:00

修改摘要：完成 Phase 7 fresh-process 闭环。Windows isolated service 的
`localhost -> ::1` PostgreSQL 连接问题保持 test-only `127.0.0.1` 修复，新增
worker readiness 与科学执行计时分离证据，180 秒 execution bound 未增加。
Phase 7 interpretation fixture 改为引用真实 persisted Fact/ResultItem，满足
Phase 6 ScientificInterpretationOutput/grounding contract，未放宽 validator。
RDF reuse、RDF 参数 continuation、XRD reuse 与 stale exact-version 均通过真实
PostgreSQL/Redis/MinIO 与独立进程 qualification；CI dedicated service selection
已纳入并强制 0 skip。

测试结果：Phase 6 fresh service `2 passed, 0 skipped`；Phase 7 dedicated service
`4 passed, 0 skipped`；service-backed CI 全部 `62 passed, 0 skipped, 0 failed,
0 errors`；Phase 7 deterministic `8 passed`；gated live DeepSeek `3 passed`；
Agent2 focused `121 passed, 9 skipped`；full backend `1739 passed, 72 skipped`；
frontend `85 files / 571 passed`；typecheck、production build、compileall、
`uv lock --check`、migration、browser desktop/390px 与 `git diff --check` 通过。
RDF readiness timing 为 startup `6.844s`、ready 后 queued→terminal `2.688s`，
未把 cold startup 计入科学执行 bound。

提交/CI：实现提交 `82d8948a4014d09f7722608cd105f27bd246c580` 与 CI 命令修复提交
`99614060f8c8c4f88d5a47913585b0fd63d5010e` 已推送，最终
`HEAD == origin/master`。current-head GitHub Actions run `32655477520` 与最终
SHA 完全一致，Unit、Frontend Typecheck & Build、PostgreSQL/Redis/MinIO
Service-backed Integration、Linux Replay、Windows Replay 五个 jobs 全部成功。
未部署或发布；用户既有 working-tree 文件未纳入提交。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 7 post-closure compatibility hardening
状态：已完成
完成时间：2026-08-24T02:10:00+08:00

修改摘要：在 authorization、login-role loading 和 secured project listing
访问可选 `project_members` 表前增加 schema existence guard，消除当前 migration
链中该表未创建时的 PostgreSQL `relation does not exist` 噪声；保留 owner-only
fallback、savepoint 保护与 legacy/migration-race 兼容，不改变权限 authority。
同时修复同文件中一个未使用局部变量的静态检查问题。

测试结果：focused access/Agent2 API `20 passed`；目标文件 Ruff、compileall、
git diff --check 通过；current-head CI `32656452081` 对 closure head
`61553dadb28f9a40d07684edcba1e51e1da457d5` 的五个 jobs 全部成功，Service-backed
Integration `62 passed, 0 skipped, 0 failed, 0 errors`，Phase 7 四个 dedicated
cases 全部通过。

提交/CI：提交 `61553dadb28f9a40d07684edcba1e51e1da457d5` 已推送；未部署或发布，
用户既有 working-tree 文件未纳入提交。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 7 provider identity-boundary hardening
状态：已完成
完成时间：2026-08-24T02:25:00+08:00

修改摘要：发现 compact context 将 UUID 转成整数后发送给 orchestrator，违反
Provider 不接收 runtime/internal identity 的约束。将 provider-facing
`relevant_prior_turns` 改为稳定 opaque `prior_turn_N` 标签；数据库 UUID 仍保留在
server-side context snapshot/fingerprint 中用于授权、审计和 replay。未改变候选
解析、continuation 或科学事实 authority。

测试结果：Phase 7 memory `9 passed`；目标文件 Ruff、compileall、git diff --check
通过。未触碰 Phase 8，也未修改用户已有 working-tree 文件。
提交/CI：提交 `24dcfdb777a63b62a2537fdb081be12653fc3fc5` 已推送；current-head CI
`32657590810` 的五个 jobs 全部成功，Service-backed Integration `62 passed,
0 skipped, 0 failed, 0 errors`。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 9 — Professional Scientific Data Viewer & Linked Scientific Selection
状态：部分完成
完成时间：2026-08-24T14:35:00+08:00

修改摘要：在现有 ScientificObject authority 上新增 deterministic exact-version
ScientificViewerRegistry、bounded viewer projection API、统一 ScientificViewerShell
和 ScientificSelectionContext 1.0。新增 migration 0025，将语义 selection 与 exact
object/version 固化到 immutable ResearchContextSnapshot；Data、Report evidence 和
Research 链路复用现有 MatterViz/Plotly/trajectory/electronic/phonon/BZ/volumetric
renderer，不触发科学计算、Job 或 LLM。

测试结果：Phase 9 deterministic `5 passed`；专用 PostgreSQL/Redis/MinIO
service-backed selection `3 passed, 0 skipped`；Agent2 Phase 1–9 focused
`140 passed, 13 skipped`；full backend `1759 passed, 83 skipped, 75 warnings`；
frontend `90 files / 581 tests passed`；typecheck、production build、compileall、
Ruff、uv lock、migration round-trip、git diff --check 通过。浏览器需要在提交
登录表单前进行 action-time credential confirmation，desktop/mobile golden paths
尚未宣称 PASS；最终 commit/push 与 exact-SHA CI 尚未完成。

提交/CI 状态：未提交；current-head CI 未运行。用户既有 working-tree 修改保留。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 9 Final Closure — authenticated browser and selection bridge
状态：部分完成
完成时间：2026-08-24T18:10:00+08:00

修改摘要：使用获批准的本地 acceptance session 完成真实 Structure、XRD/table、RDF、
历史 STALE、unsupported fallback 浏览器 smoke；发现并修复 Structure 查看器选择未
回传 Research 的真实缺陷，并将浏览器 camelCase locator 转换为 API 要求的 snake_case。
选择 URL 现在包含 exact object/version 和 PERIODIC_SITE 语义 token，API 提交返回 202。
未创建迁移、Job、ToolCall、Artifact 或 ScientificResult；用户已有 working-tree 文件保留。

测试结果：结构/selection/viewer focused Vitest `35 passed`；typecheck PASS；浏览器已认证
路径中 fatal console errors/unhandled rejections 为 0，已测 desktop/mobile 无全局溢出。
生产 build 在本轮本地 bounded wait 内无诊断输出而未重新宣称 PASS，沿用同一实现 HEAD 的既有
绿色 build/CI 证据。canonical 项目没有 scientific table object，也没有 grounded Phase 8
report snapshot/evidence fixture，因此 Table 与新 Report→Viewer golden path 未伪报 PASS。

提交/CI 状态：待提交并推送；`902c729` 的 carried-forward CI `32703157529` 绿色，
selection bridge 修复后的新 exact-head CI 尚未运行；Phase 9 保持 PARTIAL，不能进入 Phase 10。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 9 Final Closure — exact-head CI provenance update
状态：部分完成
完成时间：2026-08-24T18:45:00+08:00

修改摘要：确认提交 `665eba51688229444d14508ea32da38757b455b5` 已推送并与
`origin/master` 一致；GitHub Actions run `32716917924` 对该 exact SHA 完成且
Unit Tests、Frontend Typecheck & Build、PostgreSQL/Redis/MinIO Service-backed
Integration、Linux Replay、Windows Replay 全部成功。更新 canonical
`AGENT2_PHASE9_RESULTS.md` 的 current-head CI provenance。Phase 9 仍为 PARTIAL，
因为真实 canonical project 没有 scientific table fixture 或 grounded Phase 8
report/evidence fixture，且本地 Agent2 worker 未启动，selection API 的 `202`
未被宣称为完成的 worker/context-snapshot handoff。

测试结果：exact-head CI `32716204866` PASS；此前结构/selection/viewer focused
Vitest `35 passed`，typecheck PASS；已认证浏览器 smoke 的 fatal console errors 与
unhandled rejections 为 0，已测 desktop/mobile 无全局溢出。

提交/CI 状态：`665eba5` 已提交并推送；`HEAD == origin/master`；CI SHA 与 HEAD
一致。不得进入 Phase 10。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 9 Final Fixture & Worker Closure — compatibility fix
状态：部分完成
完成时间：2026-08-24T19:05:00+08:00

修改摘要：提交阶段 9 fixture/worker 修复 `a5da170`，包含真实生产 ingestion
生成的 scientific table fixture、SimpleWorker Windows 兼容、selection context
持久化和 cwd 独立的 SQLite/artifact 默认路径。认证浏览器与 fresh worker 已
验证 table viewer、row selection、ResearchContextSnapshot 持久化和旧 snapshot
不可变。额外修复历史 `AnalysisPlan` 缺少 `analysis_plan_json` 导致项目历史
HTTP 500 的读取兼容性问题；新计划写入校验未放宽。报告到精确 Viewer 仍因
legacy RDF source refs 缺失而未完成，未伪造 Report/Evidence 或对象引用。

测试结果：project history、runtime、processor、viewer focused `34 passed,
1 skipped`；此前阶段 focused `44 passed, 5 skipped`、frontend `90 files /
582 tests passed`、typecheck/build/compileall/uv lock/git diff check 通过。
本地 service selection 因 PostgreSQL 凭据缺失为 `3 skipped`，未宣称 service
pass；lint 未声明（deprecated `next lint`）。

提交/CI 状态：`a5da170` 已本地提交，未推送；当前 exact-head CI 尚未运行。
Phase 9 保持 PARTIAL，GP9-B04 Report → exact Viewer、push 和 current-head
CI 仍未闭合；不得进入 Phase 10。
---END---

---RESULT---
任务名称：Agent-2.0 Phase 9 — authenticated in-app browser retry
状态：部分完成
完成时间：2026-08-24T23:40:00+08:00

修改摘要：使用 Codex 内置浏览器和已批准 acceptance session 打开真实项目
`Agent2 Phase 9 Table Acceptance (Product)`。桌面 1280x720 与移动 390x844
均完成表格 Viewer smoke；移动端显示 3/3 bounded rows、formula/y_pred/y_true
科学列及 Si 语义行选择，document/body 宽度为 375/375，控制台错误为空。
列显示入口存在但没有独立列选择提交动作，未将其伪报为 PASS。

测试结果：fresh Postgres Phase 5 `2 passed`、Phase 8 `4 passed`、Phase 9
`3 passed, 0 skipped`；本地 browser table desktop/mobile PASS。SQLite acceptance
库仍只有 legacy 空 provenance report，fresh Postgres report 未注入，因此
Report -> exact Viewer browser path、最终 C/D CI 仍未闭合。

提交/CI 状态：browser retry evidence 尚待提交；未 push，未运行最终 exact-head
CI。用户工作区文件保持不变。
---END---
## Agent-2.0 Phase 9 — Same-stack browser retry (2026-08-25)

状态：部分完成

同一 authenticated browser/API/PostgreSQL/Redis/MinIO 栈已验证 fresh
grounded Report `agent2_report_1f4b8c9558f9602c0b1769ef0e731676` -> Result
`e5628121-21e0-4f3f-a303-b5006b269e92` -> exact Structure object
`de3dbb42-2690-44b0-bf82-c38f931f2b63` / version
`bf49c2e3-4a25-4e8c-944b-833ca76318f5`。Report Figure 的真实链接打开了
Professional Structure Viewer；历史版本警告显示，未发生 current/latest
替换。表格对象在同一项目中显示 3/3 bounded rows 和科学列。浏览器 error
logs 为空。Gate 0 的 `870e16b9-856a-4b00-8e81-96965286b2c8` 已审计为同一
当前代生产链的 fresh XRD Result，带 exact source refs。

服务栈：PostgreSQL/Redis/MinIO/worker health PASS；Phase 9 service-backed
`3 passed`。未使用 SQLite 作为本次 canonical Report 浏览器数据源。

未完成：当前 in-app browser 没有 viewport override，因此 fresh same-stack
390x844 mobile evidence 尚未产生；尚未创建 C/D commits 或 final exact-head
CI。不得声明 Phase 9 COMPLETE。
## Agent-2.0 Phase 9 — Fresh same-stack mobile acceptance (2026-08-25)

状态：功能闭环通过，发布 provenance 待完成

复用仓库既有 Playwright runner 与 Chromium `chromium-1228`，通过真实登录
访问同一 PostgreSQL-backed API，固定 viewport `390x844`。canonical
Scientific Table 显示 3/3 rows、`formula/y_pred/y_true`、bounded payload 与
semantic row selection；document/body 均无全局横向溢出。浏览器 console
errors、unhandled rejections、critical API failures 均为 0。首次未认证的
`/api/auth/me` 探测在登录成功后清除，不计为认证后的失败。

新增可复用验收脚本：`apps/web/test/phase9-table-mobile-acceptance.mjs`。
未修改产品 UI 或授权逻辑。`FUNCTIONAL_PHASE9_CLOSURE = PASS`；仍需
Commit C exact-SHA CI、Commit D exact-head CI 与最终 HEAD/origin 对齐后
才能声明 COMPLETE。

## Agent-2.0 Phase 9 — Final completion record (2026-08-25)

状态：完成记录（Commit D）

Commit C `7fa8eba4ab57071b5b15b702bb0838b128bd230d` 的 exact-head CI 为
`32796758192`，CI 测试 SHA 与 Commit C 一致；Unit、service-backed、frontend
和 Linux/Windows replay jobs 均通过，Phase 9 service-backed tests 实际执行
且 skipped=0。390x844 同栈 Table、fresh grounded Report -> exact Viewer、历史
版本稳定性、legacy safe fallback 与 Selection -> Research 回归均已通过。

Commit D 只包含本 canonical completion record；D 的最终 exact-head CI 将在
推送后由 CI 外部验证。结果文件不嵌入自身 Commit D SHA，以避免 Git 自引用
循环。

# Agent-2.0 Phase 10 Batch 1 Scientific Capability Expansion Result

状态：`PARTIAL / DETERMINISTIC_CONTRACTS_QUALIFIED`

本任务基于 current HEAD `e8118ebfbdfff6c44e7e2b5f583c5f5a8dfb41a6`，冻结 62
个 production Tool census 与 8 个 Batch 1 Agent2 capability：结构配位三类、
轨迹 RDF、电子能带/DOS、组成空间和材料探索。新增 requirement/capability
均为语义合同，复用已有 Tool Registry、Adapter、AnalysisPlan 0.2 和 exact
ScientificObjectVersion 绑定；新增 8 个 schema envelope 与 canonical Result
projector，未创建 migration 或 Phase 11 architecture。

测试：`tests/test_agent2_phase10_capabilities.py` 24 passed；Phase 3/contract/
Result focused regression 41 passed, 1 skipped。Live DeepSeek、PostgreSQL/
Redis/MinIO service-backed、authenticated browser、full release suite 与
exact-head CI 本轮未执行，故不得声明 `AGENT2_PHASE10 = COMPLETE`。

任务记录：`Agent-2.0 Phase 10 — Batch 1 Scientific Capability Expansion`；
状态：失败（功能实现部分完成，发布门禁未闭合）；完成时间：2026-08-25
11:00 +08:00。修改文件包括 Agent2 requirement/capability registry、生产
Artifact schema envelope、canonical Result projectors、Phase 10 census/manifest、
专项 qualification tests、persistent 设计记录与本结果文件；用户已有
working-tree 文件未纳入。测试/构建结果如上；service-backed 为 1 skipped，
未提交、未 push、未运行 current-head CI。

## Agent-2.0 Phase 10 — Browser and service qualification rerun (2026-08-25)

状态：`PARTIAL / BROWSER_SMOKE_AND_SERVICE_PASS`

使用用户提供的 Chromium `C:\Users\86182\Desktop\wkkk\playwright-browsers\chromium-1228\chrome-win64\chrome.exe`，真实登录
`acceptance.researcher@local.invalid` 后，通过同栈前端 `127.0.0.1:3002`、API
`127.0.0.1:8000` 和 PostgreSQL/Redis/MinIO 服务完成点击验收：Console 可进入，
Research Workbench 可打开；390x844 Scientific Table 显示 3/3 行、formula/
y_pred/y_true，点击第 1 行后显示 `当前选择数据样本 · Si`，document/body 全局
overflow 为 0。浏览器表格脚本结果为 PASS，console errors、unhandled
rejections、critical API failures 均为 0。

Phase 10 专项服务测试在本地 Docker 服务中为 selected=6、passed=6、failed=0、
errors=0、skipped=0。专用 6–10-case live DeepSeek campaign、三类新增能力的
完整自然语言执行浏览器路径和 exact-head CI 仍未闭合，因此 Phase 10 继续保持
`PARTIAL`，不进入 Phase 11。

追加验证：Batch-1 live DeepSeek 语义路由矩阵 `8/8 passed`；Phase 10N1/N4/N5/N6
以及 Phase 10K3/K4 PostgreSQL/Redis/MinIO service-backed 集成 `6 passed, 0
skipped`。K3/K4 首次失败的原因是测试 harness 与 API 使用了不同数据库环境；
统一 `DATABASE_URL` 到 PostgreSQL 后重跑通过。
## Agent-2.0 Phase 10 — current qualification refresh (2026-08-25)

状态：失败（保持 PARTIAL；不得进入 Phase 11）

完成时间：2026-08-25

修改摘要：复核当前 Phase 10 Batch 1、使用用户提供 Chromium 完成同栈
认证表格移动验收，并通过真实 Research 页面提交结构局部配位问题；未改动
产品架构或 Phase 1-9 authority。

测试结果：

- Phase 10 deterministic: `34 passed`（24 Batch 1 + 10 N6 closure）。
- Phase 10 service-backed: `6 selected / 6 passed / 0 failed / 0 errors / 0 skipped`。
- Batch 1 live DeepSeek semantic matrix: `8/8 passed`。
- Full backend: `1787 passed / 83 skipped`。
- Frontend: `582 passed across 90 files`；typecheck/build PASS。
- 390x844 authenticated Scientific Table: `3/3` rows, row selection PASS,
  global overflow 0, fatal console errors 0, unhandled rejections 0。
- Fresh authenticated structure request: real Research submission produced a
  new Turn; this does not claim a complete new-family execution/browser path。

剩余阻塞：尚未完成至少三个新增能力族的 authenticated same-stack
自然语言执行→Job→Result→grounded answer→Viewer 浏览器黄金路径；未创建
Commit A/B，未获得 Phase 10 exact-head CI。Ruff 全仓库存在 79 个历史问题，
Phase 10 touched modules 的定向检查已通过。未 push。

## Agent-2.0 Phase 10 — canonical fixture / three-family recheck (2026-08-25)

状态：失败（保持 `PARTIAL`，不得进入 Phase 11）

修改摘要：保留 fail-closed coordination eligibility；修复真实解释器
grounding 对 UUID/provenance 数字和小写 `k` 点标签的误识别；新增回归测试。
结构使用 fresh current-profile fixture 完成真实同栈
ContextSnapshot→Plan→Job→2 ToolCalls→6 Artifacts→Result→DeepSeek grounded
interpretation；电子能带也完成真实 Result 与 grounded follow-up。材料表的
Agent 路径仍被 typed validator 拒绝，因为当前 `data.explore_materials`
manifest 只接受 `materials.dataset`，而 canonical promoted object 是
`materials.table`；未放宽 eligibility。

测试结果：Phase 10/interpretation/worker focused `44 passed, 1 skipped`；
touched Ruff、compileall PASS；Table mobile、Structure/Band viewer smoke PASS。
未创建 Commit A/B，未 push，未运行 exact-head CI。剩余 dataset typed input
bridge、三族完整浏览器黄金路径、reuse/multiturn 和 release provenance。

## Agent-2.0 Phase 10 — final fixture readiness recheck (2026-08-25)

状态：失败（保持 `PARTIAL`，不得进入 Phase 11）

结构、电子能带和材料表均已通过当前生产 profile/readiness，并通过真实
PostgreSQL/Redis/MinIO worker 完成至少一条成功链。最终材料表链为：
Turn `a4f6f737-c7e5-4999-8063-d6c1911f3bb0` → Plan
`plan_58e97082a5954e509c10a8a8` → Job
`job_agent2_a4f6f737c7e549998063d6c1911f3bb0` → 1 ToolCall / 4 Artifacts
→ Result `35bdb8fe-76e5-4f63-809d-e918b30ae483` → VALID interpretation；
未直接写入数据库。

修复内容是通用的 typed source/profile bridge、DataFrame 安全比较、table
object capability admission，以及现有研究界面的 dispatch wiring；没有
放宽 coordination/electronic eligibility，也没有新增 migration。旧 silicon
仍以 `CAPABILITY_REQUIREMENT_UNSATISFIED` fail-closed。

认证 Chromium smoke：Table `390x844`、Structure `1280x720`、Band
`1280x720` 均 PASS，运行时错误为 0。Structure 自然语言点击路径已到达 exact
ContextSnapshot 和双 capability `PLAN_READY`；但本地重复诊断造成 API
PostgreSQL 连接池耗尽，未捕获一个干净的 dispatch 后浏览器 Job → Result →
grounded answer → Viewer 证据，因此三族完整浏览器门禁仍未闭合。focused
测试 `55 passed, 1 skipped`，前端 typecheck/build、touched Ruff、compileall
和 diff check PASS；未创建/推送 Commit A/B，未获得 exact-head CI。

## Agent-2.0 Phase 10 — Stage 0 pool diagnosis and lifecycle fix (2026-08-25)

状态：失败（保持 `PARTIAL`，不得进入 Phase 11）

实际 `pg_stat_activity` 证据显示，重复认证轮询后 PostgreSQL 达到约 98 个
idle 会话，但没有 idle-in-transaction 累积。根因是 API 路由每次调用都创建新的
SQLAlchemy Engine，从而创建新的 5-connection pool；不是应通过增大 pool 参数
掩盖的问题。

本轮加入按数据库配置复用的进程级 Engine cache、API shutdown disposal，以及
8 次请求式 Engine 创建/连接关闭回归测试。定向结果为 `46 passed, 1 skipped`，
数据库模块和新增测试 Ruff PASS，compileall、frontend focused、typecheck、
production build、git diff check PASS。重启旧 API/worker 后数据库会话回落到
单个诊断连接。

由于本轮运行时在重启后尚未重新完成干净的三族 authenticated dispatch → Job →
Result → grounded answer → Viewer 浏览器路径，且未运行 current-head service
suite、未创建 P10-A/P10-B、未获得 exact-SHA CI，Phase 10 仍为 PARTIAL；Phase 11
未开始。

## Agent-2.0 Phase 10 — clean runtime three-family closure attempt (2026-08-25)

状态：部分完成（功能证据通过；发布 provenance 未闭合，保持
`AGENT2_PHASE10 = PARTIAL`，不得进入 Phase 11）

修改摘要：完成进程级 PostgreSQL Engine cache 与终态进度幂等重投影修复；
保留 coordination/electronic fail-closed eligibility；通过 canonical
typed source/Profile bridge 完成材料表执行。使用真实 Chromium 和同一
PostgreSQL/Redis/MinIO 数据平面，完成 Structure、Electronic Band、Dataset
三条 authenticated natural-language
Research→Plan→Job→ToolCall→Artifact→ScientificResult→grounded
interpretation→Viewer 路径。未直接插入 ScientificObject、Profile、Job、
Result 或 Report。

验收证据：

- Structure Turn `21d40ce4-c299-485f-8b34-db29f1416dc8`：
  CrystalNN + VoronoiNN 双 capability，精确 object/version 保留，终态
  `COMPLETED`，Structure Viewer PASS。
- Electronic Turn `e96b22af-0bf5-4ef2-962e-05d20a5afe93`：Band Structure
  自然语言路径、精确资源、grounded answer 和 Viewer PASS。
- Dataset Turn `6d16ce68-6cf1-4d93-8147-6d76fa35a784`：3 行 canonical
  table、材料探索结果、grounded answer 和 Viewer PASS。
- Table `390x844`：3/3 rows、row selection、global overflow=0、fatal/
  unhandled/critical request errors=0。
- Structure/Band `1280x720`：Viewer PASS，运行时致命错误=0。
- PostgreSQL pool：修复前约 98 idle sessions；修复后
  `active=1, idle=6, idle-in-transaction=0`，无 pool timeout。
- 当前 full backend：`1791 passed / 83 skipped`；frontend
  `582 passed across 90 files`；typecheck/build/touched Ruff/compileall/
  `uv lock --check`/diff check PASS。
- 当前 Phase 10 service-backed：`12 selected / 12 passed / 0 failed /
  0 errors / 0 skipped`。

剩余阻塞：尚未创建并推送 P10-A/P10-B，也没有针对当前工作树的 exact-SHA
CI；因此不能宣称 Phase 10 COMPLETE，Phase 11 执行明确为 NOT_STARTED。

## Agent-2.0 Phase 10 — P10-A functional closure (2026-08-25)

P10-A 已提交并通过 exact-SHA CI：

- SHA：`ea5eb2546a82a1ffa602bab7651f7e9a6d2ffdd9`
- CI run：`32858593255`
- tested SHA：`ea5eb2546a82a1ffa602bab7651f7e9a6d2ffdd9`
- 结果：PASS
- PostgreSQL/Redis/MinIO service-backed integration：PASS，且无跳过测试。

三族 authenticated browser、池生命周期、backend/frontend/typecheck/build、
静态检查和当前服务回归均已通过。尚待 documentation-only P10-B 及其
exact-current-head CI；Phase 11 尚未开始。

## Agent-2.0 Phase 11 — trusted Capability Pack boundary (2026-08-25)

状态：实现与 focused qualification 已完成，release provenance 待闭合。

新增 `apps/api/mdi_api/research_agent/capabilities/packs.py`，提供 repository-trusted declarative Pack contract、确定性 contract/binding fingerprints、atomic validation/registration 和 semantic Agent catalog。Phase 10 Batch 1 通过 `core.structure`、`core.electronic`、`core.data`、`core.trajectory`、`core.other` Pack 归一化，不改变科学算法、AnalysisPlan 0.2、执行、Result、Viewer 或 exact-version 语义。新增 `docs/phase11/capability_pack_manifest_v1.json` 与 `AGENT2_PHASE11_RESULTS.md`。Phase 10 registry/capability 与 Phase 11 Pack focused tests：`38 passed`；无数据库 migration。P11-A/P11-B 及 exact-head CI 尚未完成，故当前尚不能宣称 Phase 11 COMPLETE。

## Agent-2.0 Phase 11 — P11-A exact-SHA implementation closure (2026-08-25)

P11-A 已提交并推送：

- SHA：`32ddeb9cfc33e4ff9f95be9b85b840fdf6c8f6da`
- CI run：`32864008706`
- tested SHA：`32ddeb9cfc33e4ff9f95be9b85b840fdf6c8f6da`
- 结果：PASS
- required jobs：Unit Tests、Frontend Typecheck & Build、
  PostgreSQL/Redis/MinIO Service-backed Integration、Linux Replay、Windows
  Replay，全部 PASS；service-backed no-skipped assertion PASS。

P11-B 为 completion-record 文档提交；它只记录 P11-A 的 exact provenance、
Phase 10 sealed provenance、Pack/registry 验收及浏览器扩展证明，不要求把
自身 SHA 写回记录文件。P11-B exact-current-head CI 通过后，Phase 11 才
满足 COMPLETE / READY_FOR_PHASE12。

## Agent-2.0 Phase 12 — Data Platform authority increment (2026-08-25)

状态：失败 / PARTIAL

任务名称：Agent-2.0 Phase 12 — Scientific Data Platform 2.0

完成时间：2026-08-25

修改摘要：完成现有 ScientificObject、ScientificObjectVersion、
ScientificObjectRelationship、ArtifactStorage、Profile、Result source refs
和 Report exact-version authority 审计；新增受项目写授权保护的
`PATCH /api/scientific-objects/{object_id}`，支持显示名元数据更新和
archive/restore。该操作不创建新科学版本、不修改 content/semantic hash、
source refs、parent refs 或 current version，历史版本仍可按精确 UUID 读取。
将用户 Phase 12 prompt 固化到
`docs/agent2/phase12_data_platform/PHASE12_TASK.md`，并增加审计记录
`PHASE12_DATA_PLATFORM_AUDIT.md`；同时把“阶段 Prompt 必须先固化并由
TASKS 引用”的规则加入 `AGENTS.md`。

测试结果：`tests/test_agent2_domain.py` 与 `tests/test_agent2_api.py`
共 `18 passed`；compileall PASS。Ruff touched invocation 暴露的是
`main.py` 与测试文件的既有 unused-import 基线，未发现本次服务改动新增的
专属错误。

提交/CI 状态：未提交、未推送；P12-A/P12-B exact-SHA CI 未运行。

## Agent-2.0 Phase 12 — Data Platform authority increment (2026-08-26 continuation)

状态：失败 / PARTIAL

完成时间：2026-08-26

修改摘要：在既有 ScientificObject/ScientificObjectVersion authority 基础上
补齐受项目写授权保护的 metadata rename/archive/restore boundary，并增加
exact object/version、checksum、typed filter/sort/projection 与 stable row
identity 的 bounded Dataset query API 及前端 client helper。新增 Agent2-scoped
audit/acceptance evidence，未创建 migration，未修改历史
`docs/phase12/evidence/*` 用户文件。

真实验收与测试：Agent2/API/Viewer `25 passed, 4 skipped`；全后端
`1802 passed, 83 skipped`；前端 `90 files / 582 tests passed`；
typecheck/build/compileall/uv lock/diff check/touched Ruff PASS。使用同栈
认证 Chromium 完成 Structure exact object/version
`773089f9-3ce8-4645-92dd-2f62c64cba89 /
65f56d10-008d-445d-ab2f-228aebf1835b` 的真实 ResearchTurn
`63e68fed-eb0f-4675-aaed-1bc1479efd81`，状态 `COMPLETED`，grounding
`VALID`，CrystalNN/VoronoiNN 双能力均有结果；缺少必要语义的通用请求正确
返回 `UNSUPPORTED` 且未创建 Job。

恢复闭环结果：真实复现显示执行 worker、Artifact 与 Result projection 已
成功，随后共享 interpretation worker 因未配置 provider fixture 将 Turn
改为 FAILED；根因是 service-backed fixture 的队列/解释隔离与旧 MinIO
凭据读取不一致，而非 Result projector 终态缺失。修复夹具后 Phase 5
Result projection 连续三次 `2 passed`，每次均验证队列消费、Artifact、
ScientificResult、`RESULT_READY` 和幂等投影。

仍未闭合：Data→Research→新版本/归档恢复浏览器生命周期、当前工作树完整
Phase 12 PostgreSQL/Redis/MinIO campaign、以及 P12-A/P12-B exact-SHA CI。
未提交、未推送。

## Agent-2.0 Phase 12 — Final qualification attempt (2026-08-26)

状态：失败 / PARTIAL

使用解释器启用、DeepSeek 已配置、PostgreSQL/Redis/MinIO 同栈运行时完成
了一次新的 Structure 全链路：Turn
`7334ba9c-9e9c-41bd-801b-884b4c84e862`，exact source
`773089f9-3ce8-4645-92dd-2f62c64cba89 /
65f56d10-008d-445d-ab2f-228aebf1835b`，执行 `SUCCESS`，解释
`VALID`，Turn `COMPLETED`，Assistant final 已持久化。

为暴露已有的不可变版本服务，新增最小授权
`POST /api/scientific-objects/{object_id}/versions` API 及回归测试；API
创建 v2 后正确推进 current version 且 v1 保持不变。但当前 canonical
Structure 没有可由该入口合法重新摄取的真实 payload，本次尝试使用
`system_fixture` 引用的 v2 Turn 返回 `UNSUPPORTED`，未被计作科学 v2
验收，也未伪造历史 Viewer 结论。

未闭合：合法 v1→v2 浏览器生命周期、归档历史安全、Dataset→Research
handoff、完整当前工作树 service-backed campaign、P12-A/P12-B exact-SHA
CI。未提交、未推送；Phase 13 未开始。
## Agent-2.0 Phase 13 — Scientific Presentation 2.0（强制 Phase 12 Stage 0 门）

状态：失败（Phase 13 主实现未开始）

完成时间：2026-08-26

验证摘要：

- 按 `AGENTS.md` 读取了项目 brief、设计/架构/任务文档以及 Phase 12/13
  权威任务文件；TASKS 首任务已按规则处理。
- 使用用户指定 Chromium：
  `C:\Users\86182\Desktop\wkkk\playwright-browsers\chromium-1228\chrome-win64\chrome.exe`。
  通过产品登录入口，以用户授权的本地验收账号登录成功；未读取或复制浏览器
  密码、Cookie、local storage 或 profile。
- 真实 API/数据库显示 canonical Structure
  `773089f9-3ce8-4645-92dd-2f62c64cba89` 的合法 v1 是
  `65f56d10-008d-445d-ab2f-228aebf1835b`，当前 v2
  `8dcb6e0e-fb47-4af0-a1ef-a7f6b89fe708` 的 source ref 为
  `system_fixture/phase12-v2-structure`，不满足 Phase 12 真实再摄取版本门。
- 生产域服务存在 `create_version_from_dataset_resource`，且版本创建 API 已有
  focused 回归；但本轮没有完成真实 source→storage→parse/profile→v2→v2
  Research 浏览器生命周期，不能把 system fixture 计为科学版本证据。
- `uv run pytest -q tests/test_agent2_api.py tests/test_agent2_domain.py
  tests/test_agent2_phase8_reports.py`：`36 passed, 4 skipped`。
- `uv run pytest -q tests/integration/test_agent2_phase5_service_backed.py
  tests/integration/test_agent2_phase7_service_backed.py`：`6 skipped`；关键
  Phase 12 service-backed 门未实际执行，不能宣称 PASS。
- P12-A/P12-B exact-SHA CI 未完成；因此不允许进入 Phase 13。

修改文件：`TASKS.md`、`results.md`。保留所有既有 Phase 12 实现和用户-owned
文件；未修改 Phase 13 主实现、未创建 migration、未提交或推送。

最终状态：

```text
FUNCTIONAL_PHASE12_CLOSURE = FAIL
AGENT2_PHASE12 = PARTIAL
SCIENTIFIC_DATA_PLATFORM_V2 = PARTIAL
READY_FOR_PHASE13 = NO
PHASE13_MAIN_IMPLEMENTATION = NOT_STARTED
```

## Agent-2.0 Phase 12 — Final Browser Seal (2026-08-26T17:16:42+08:00)

状态：失败 / PARTIAL；Phase 13 主实现未开始

本轮 fresh runtime 已明确修复并验证 RQ 规划队列运行时边界：
worker 必须带 `MDI_AGENT2_ORCHESTRATION_ENABLED=true`，且规划任务使用
顶层可解析入口 `mdi_api.research_agent_planning_worker.run_queued_planning`。
新的 Dataset Turn `295fdb48-6ea4-4b36-a7b8-9b9ed5559df6` 真实完成
`ANALYZE → PLAN_READY → Job → ToolCall → Artifact → ScientificResult →
Interpretation VALID → COMPLETED`；Result facts 非空，包含 `mat-2`、
`NaCl`、`band_gap=5.6`、`density=2.16` 等权威事实。

首个 fresh 请求被正确路由为 `QUERY_DATA`，决策明确为
`scientific_requirements=[]`，因此没有科学执行；其第一缺失转移为
`ORCHESTRATION_COMPLETED → ScientificRequirement/PLANNING`。改用确实要求
材料科学分析的自然语言请求后，规划与执行完整通过。

grounding 根因进一步收敛为 `IDENTIFIER_TOKENIZATION_MISMATCH`：
grounding 数字提取器将稳定样本标识 `mat-2` 中的 `2` 当作定量 claim。
已在 `interpretation/schemas.py` 对 canonical `mat-*` / `sample-*`
标识做窄范围 opaque-token 处理，并增加正向 regression；负向不支持数字
claim 仍拒绝。相关测试 `30 passed, 1 skipped`，touched Ruff PASS。

archive/restore API 通过已登录浏览器上下文验证：对象
`773089f9-3ce8-4645-92dd-2f62c64cba89` 从 ACTIVE → ARCHIVED → ACTIVE，
current version `2538cd12-ffd5-473f-8c77-69e6d1700243` 不变，历史 Viewer
仍以 v1 `65f56d10-008d-445d-ab2f-228aebf1835b` 返回。科研对象列表当前
没有 archive/restore 操作菜单，因此“authenticated archive UI golden path”
仍未闭合；本轮未添加未完成的 UI bridge。

本轮新增/保留修改：
`apps/api/mdi_api/interpretation/schemas.py`、
`tests/test_agent2_phase6_interpretation.py`、
`apps/api/mdi_api/research_agent/planning/__init__.py`、
`apps/api/mdi_api/research_agent/planning/queue.py`、
`apps/api/mdi_api/research_agent_planning_worker.py`、
`tests/test_agent2_planning_worker_import.py`、
`tests/test_agent2_queue_entrypoints.py`。

未创建或推送 P12-A/P12-B；未运行 exact-SHA CI；Phase 13 主实现保持未开始。

最终状态：

```text
FUNCTIONAL_PHASE12_CLOSURE = FAIL
AGENT2_PHASE12 = PARTIAL
SCIENTIFIC_DATA_PLATFORM_V2 = PARTIAL
READY_FOR_PHASE13 = NO
PHASE13_MAIN_IMPLEMENTATION = NOT_STARTED
```

## Agent-2.0 Phase 13 — Final Seal Gate Attempt (2026-08-26)

状态：失败 / PARTIAL；Phase 13 主实现未开始

本轮先执行 Phase 12 Stage 0。Dataset grounding 根因定位为
`data.materials_explorer` Result projector 没有把生产 Artifact 中已有的
`sampleIndex`、`sampleRef`、样本属性、coverage/composition/quality 计数及
property statistics 投影为 `ScientificFact`，导致 validator 正确拒绝：
`finding.001: quantitative claim is not supported by referenced facts`。

已在 Result projector 增加窄范围确定性 facts 投影，并新增正向 `mat-2`
grounding 与负向 unsupported numeric claim 回归；相关测试为
`27 passed, 1 skipped`。未放宽 grounding、未硬编码 Dataset 答案。

真实浏览器复核未形成有效 Dataset 科学闭环：首个前端实例走 direct
`ANSWERED` 路径（无 Job/Result）；干净构建目录认证成功，但当前
same-origin rewrite 的研究状态轮询返回 404，数据库中的该 Turn 仍为
`ANSWERED` 且无 Job。故 Dataset grounded Assistant final、archive
独立浏览器黄金路径、Phase 12 release gate 仍未通过。

P12-A/P12-B 未创建、未推送、未运行 exact-SHA CI；Phase 13 未开始。

最终状态：

```text
FUNCTIONAL_PHASE12_CLOSURE = FAIL
AGENT2_PHASE12 = PARTIAL
SCIENTIFIC_DATA_PLATFORM_V2 = PARTIAL
READY_FOR_PHASE13 = NO
PHASE13_MAIN_IMPLEMENTATION = NOT_STARTED
```

## Agent-2.0 Phase 12 — Surgical Repair

状态：失败 / PARTIAL

完成时间：2026-08-26

修改摘要：确认 `VERSION_UPDATE_AUTHORITY =
MISSING_MINIMAL_REINGESTION_BRIDGE`。真实 CIF 通过当前 Dataset ingestion、
MinIO、parser/Profile 2.1 和受项目授权的版本 API，创建同一
ScientificObject `773089f9-3ce8-4645-92dd-2f62c64cba89` 的真实版本
`2538cd12-ffd5-473f-8c77-69e6d1700243`；保留 v1 和历史 system_fixture
诊断版本，不把后者计入资格证明。修复浏览器 memory API 的 `/api` fallback，
并保留 Phase 6 interpretation wakeup 夹具隔离修复。

真实资格结果：

- Structure v2 认证浏览器研究 Turn
  `aa60bdff-7ddc-4989-bda2-490f94f9b871`：COMPLETED，双 coordination
  Capability，真实 Job/ToolCalls/Artifacts/Result，grounding VALID。
- archive/restore：ACTIVE → ARCHIVED → ACTIVE；current version 和版本数量
  不变；历史 v1 Viewer API 仍解析 v1。
- Dataset `band_gap > 2`：mat-3、mat-2；`mat-2` 作为
  `DATASET_SAMPLE/sample_ref` 写入 exact Dataset object/version 的
  ContextSnapshot 和 CapabilityPlan。真实表 Tool/Artifact/Result 完成，
  但 interpretation 以 `INTERPRETATION_GROUNDING_FAILED` 结束，未宣称
  grounded final answer PASS。
- PostgreSQL/Redis/MinIO 显式环境服务集合：19 selected、19 passed、
  0 failed、0 errors、0 skipped；PostgreSQL active=1、idle=6、
  idle-in-transaction=0。

测试结果：全后端 `1803 passed, 83 skipped`；前端 `90 files / 582 tests
passed`；Agent2/API/domain/registry `52 passed`；Phase12 evidence/queue
`27 passed`；typecheck、生产 build（独立构建目录）、compileall、
`uv lock --check`、`git diff --check`、touched Ruff PASS。

提交/CI 状态：未创建 P12-A/P12-B，未推送；Dataset grounded interpretation
门仍未闭合，故不得声明 Phase 12 COMPLETE，也不得开始 Phase 13。

最终状态：

```text
FUNCTIONAL_PHASE12_CLOSURE = FAIL
AGENT2_PHASE12 = PARTIAL
SCIENTIFIC_DATA_PLATFORM_V2 = PARTIAL
READY_FOR_PHASE13 = NO
PHASE13_MAIN_IMPLEMENTATION = NOT_STARTED
```
## Agent-2.0 Phase 13 — Scientific Presentation 2.0 最终封板

状态：已完成

完成时间：2026-08-28T02:20:00+08:00

修改摘要：在已封存 Phase 12 数据权威之上完成 bounded Scientific
Presentation compiler/renderer，接入 Research 与 Report，保留 exact
ScientificObjectVersion、Result、Artifact、Evidence provenance，补齐
稳定 Dataset sample identity、历史版本提示、真实 Artifact/Viewer links、
unique presentation heading IDs 与显式 researchTurnId 历史解析。未创建第二
科学事实权威，也未向浏览器转移执行权。

测试结果：focused frontend 25 passed；focused backend 85 passed、4 个历史
兼容性 skip；full frontend 593 passed；full backend 1813 passed、83 个历史
skip；PostgreSQL/Redis/MinIO service-backed 14 passed、0 skipped；运行时
`/health/runtime` 为 PostgreSQL/Redis/MinIO/DeepSeek configured；typecheck、
production build、compileall、`uv lock --check`、touched Ruff 与
`git diff --check` 通过。Chromium 1280x720 Structure/Dataset/Report/
archive evidence 与 390x844 Dataset handoff 无溢出；仅出现预期认证 bootstrap
401，无页面错误或 5xx。

提交/CI 状态：P13-A 候选 `4bfdacd`，exact-SHA CI run `33134862435`，
Unit/Frontend/PostgreSQL-Redis-MinIO/Linux replay/Windows replay 全部 PASS。
P13-B 为本次证据提交，待提交后运行 exact-current-head CI。
任务名称：Agent-2.0 Phase 14 — Full Platform Integration & Production Qualification
状态：已完成
完成时间：2026-08-28T12:30:00+08:00
修改摘要：完成 Phase 13 provenance normalization、Phase 14 coverage ledger、
Project History/Workspace 显式 ResearchTurn 身份连续性桥，并完成真实
PostgreSQL/Redis/MinIO、浏览器、全后端/前端及静态回归。
测试结果：service-backed 17/17；backend 1813 passed / 83 historical skips；
frontend 91 files / 595 passed；typecheck、production build、compileall、
uv lock、touched Ruff、diff check 通过。
提交/CI 状态：P14-A `d1249ac34cc0d2be571cdbc96075a3d88c6406b8`；
CI `33142030331` exact-SHA PASS。P14-B 为本次证据封存提交，需以其
exact-current-head CI 作为最终 release seal。

任务名称：Agent-2.0 Phase 14-R — Post-Seal Product Quality Remediation
状态：处理中
完成时间：2026-08-28
修改摘要：补强 Project History 的现代 ResearchTurn 消息身份解析。历史
投影优先采用持久化 `ResearchTurn.user_message_id`，legacy
`research_session_runs` 继续使用有界时间回退；跨 session 的异常消息绑定
不会被用于展示，避免多轮会话串线或跨会话泄露。
测试结果：`tests/test_project_history_research_context.py` 与
`tests/test_project_history.py` 共 7 passed；目标模块 compileall PASS；
目标 Ruff PASS；此前 Agent2/Research/Presentation 聚焦回归仍保持通过。
提交/CI 状态：本次变更待提交；Phase 14-R 仍有成熟产品 P0/P1 资格债务，
未创建 P14R-A/P14R-B，未宣称 COMPLETE。

任务名称：Agent-2.0 Phase 14-R — service worker subprocess environment
状态：处理中（并入当前任务）
完成时间：2026-08-28
修改摘要：共享 Phase 4 service-worker 环境现在显式包含
`services/llm`，避免 Phase 5/7 service-backed 子进程因缺少 `mdi_llm`
导入路径而产生假 ERROR。
测试结果：Phase 7 service-backed `4 passed`, `0 skipped`；目标 Ruff 与
compileall PASS。
提交/CI 状态：随 Phase 14-R fix-forward 提交；尚未创建 P14R-A/P14R-B。

任务名称：Agent-2.0 Phase 14-R — report history continuity
状态：处理中（并入当前任务）
完成时间：2026-08-28
修改摘要：科学报告历史索引根据服务端持久化绑定显示“可恢复研究会话”
或“兼容历史运行”，不改变既有报告路由或科学权威。
测试结果：`ScientificReportsIndexPage.test.tsx` `1 passed`；
前端 typecheck PASS。
提交/CI 状态：随 Phase 14-R fix-forward 提交；未创建 P14R-A/P14R-B。

任务名称：Agent-2.0 Phase 14-R — server-derived dependency impact preview
状态：处理中（并入当前任务）
完成时间：2026-08-28
修改摘要：为 Project 与 Dataset 永久删除确认流程增加受现有项目写权限保护的
依赖影响预览 API，并在生命周期对话框中展示已持久化依赖及归档建议；删除仍由
既有 fail-closed 规则决定，未引入新的科学权威或版本语义。
测试结果：`tests/test_project_access.py` 11 passed；前端
`ProductPages.test.tsx` 与 `ScientificReportsIndexPage.test.tsx` 18 passed。
提交/CI 状态：待随 Phase 14-R fix-forward 提交；未创建 P14R-A/P14R-B。

追加验证（2026-08-28）：同栈 Phase 12 关键服务回归重新执行
`5 passed, 0 failed, 0 errors, 0 skipped`（Phase 3 1 项 + Phase 7 4 项），
`/health/runtime` 确认 PostgreSQL/Redis/MinIO/Redis worker/DeepSeek；
PostgreSQL 活动连接 `active=1, idle=5, idle-in-transaction=0`。现有已认证
浏览器数据页确认数据集操作菜单包含归档入口；未执行破坏性归档操作。

追加验证（2026-08-28）：ContextManifest/预算聚焦套件新增确定性压缩回归，
`3 passed`；在预算压力下优先压缩历史对话，同时保留精确选定的科学对象、
版本和当前用户请求。浏览器/Provider 规模性能基准仍未闭合。

追加验证（2026-08-28）：同栈已认证浏览器暖启动测量，Research 页面
DOM-ready `1442 ms`，包含 `500 ms` 稳定窗口后研究输入可见总计 `1945 ms`。
该数据已写入性能基线，仅作为单点测量，未替代要求中的 p50/p95 与移动端
性能资格。

追加验证（2026-08-28）：当前工作树完整回归重新执行，前端 `93 files /
597 passed`，后端 `1820 passed / 83 skipped`；未发现新增失败。跳过项仍为
历史/可选兼容覆盖，成熟产品强制浏览器、报告质量、Trash/保留策略、恢复和
运维门仍未全部资格化。

追加验证（2026-08-28）：在保留的已认证浏览器标签页中，对
`dataset_0003_1e42d834bfa64961` 执行了真实“归档数据集 → 已归档列表 →
恢复数据集”路径。归档时活动列表移除并在归档筛选可见，恢复后回到活动列表；
数据库最终状态为 `profile_ready`，项目内 ScientificObject/Version 数量均为
4，未创建新科学版本。

追加验证（2026-08-28）：修复 Research“研究记录”弹层的历史连续性导航。
会话条目现在优先使用 ProjectHistory 中已持久化的 `researchSessionId`、
`jobId` 和 `researchTurnId`，生成带 `run`/`turn` 的精确恢复链接；没有绑定运行
的会话仍保持原会话入口，未引入 Job 名称解析。ResearchPages 回归
`34 passed`，web typecheck 通过；Phase 14-R 其余成熟产品门仍保持真实
PARTIAL 状态，未创建 P14R-A/P14R-B。

追加验证（2026-08-28）：补齐 Interpretation Evidence 的只读来源链投影。证据接口继续以 immutable bundle 作为 evidence authority，并从所属 Job 的持久化 ScientificResult snapshot 解析 bounded `sourceObjectRefs`，同时返回 Job-scoped Artifact/ToolCall descriptors；旧记录缺少 Result snapshot 时安全返回空 source refs，不伪造 provenance。`tests/test_phase10l4_api_persistence.py` 为 13 passed，Research/Presentation 前端聚焦测试 43 passed，typecheck 与 touched Ruff 通过。该修复改善了 Evidence UX，但 Phase 14-R 全量科学 surface、Trash/retention、recovery 与 release CI 仍未闭合。

追加验证（2026-08-28）：Scientific Presentation evidence reference 增加用户可触发的有界“检查证据链”面板，复用 secured interpretation-evidence 投影并展示 exact source object/version、Result 字段值、Artifact checksum、ToolCall/status；只读、不触发 Job/Tool/Artifact/Result，不暴露凭据或队列细节。新增 `ScientificPresentationBlocks.test.tsx` 为 1 passed，web typecheck PASS；同栈 Phase 3/7 service campaign 在显式 PostgreSQL/Redis/MinIO 环境为 5 passed、0 failed、0 errors、0 skipped。Phase 14-R 仍未达到 P14R-A/P14R-B 发布门。

追加验证（2026-08-28）：定位并修复 Evidence Inspector 在真实现代 Result 上无法读取链路的身份契约缺口：`Agent2ScientificPresentation` 现在将 API 外层持久化 `interpretation_id` 显式传入 `compileScientificPresentation`，编译器随后为证据/发现/摘要/限制/警告保留该 ID；不再依赖嵌套 grounded payload 重复数据库身份。定向前端测试 `12 passed`，typecheck PASS，未新增科学执行。
追加验证（2026-08-28）：完成 Agent2 durable interpretation → planner evidence route 的兼容适配。
服务端从 immutable ScientificResult snapshot 解析 exact object/version，并从所属 Job
返回 Artifact 与 ToolCall；同时兼容历史 source binding 的 snake_case/camelCase 字段。
真实同栈 API 返回 interpretation `efccf7a2-6666-429e-be92-20cb2cf659de` 的
Dataset version `be02266a-7d4f-4ebb-9f28-3132855167d0`、Artifact checksum
`879396a3bc0bfdef2d31387b3eb73df309fa228d95f9cf2fb2c92eca6c119708` 与已完成
ToolCall `dataset.materials_explorer`；保留的已认证浏览器标签页显示同一证据链。
新增持久化回归后 `tests/test_phase10l4_api_persistence.py` 为 `14 passed`。
Phase 14-R 更广泛的成熟产品门仍保持 PARTIAL，未创建 P14R-A/P14R-B。
追加验证（2026-08-28）：真实 PostgreSQL/Redis 同栈重跑
`tests/integration/test_agent2_phase7_service_backed.py`，结果 `4 passed`
（114.25s）。Interpretation-only reuse 与 continuation 路径均使用现有
Result authority；测试断言 reuse 前后 `analysis_plans/jobs/tool_calls/artifacts/
scientific_result_snapshots` 聚合计数不增长，并验证 follow-up Turn 完成及
原始 Result/Turn 身份保持不变。浏览器级复用控制仍待成熟产品 campaign。

追加验证（2026-08-28）：Scientific Presentation 结果页新增三个明确的后续
研究控制：`继续研究`、`重新研究（新运行）`、`重新解释（不重算科学结果）`。
三者均复用受授权的 ResearchTurn 创建边界并保留精确 source object/version；
继续研究显式携带既有 Result 引用，重新研究明确创建新的 execution lineage，
重新解释保持 interpretation-only 语义。`Agent2ScientificPresentation` 聚焦
测试 `3 passed`，前端全量回归 `94 files / 603 passed`，typecheck 与
`git diff --check` 通过。该修复关闭了结果页基础控制入口，但消息修订/分支、
运行中取消恢复、浏览器级零增量复用以及 Trash/retention/export 等成熟产品门
仍未闭合，Phase 14-R 继续保持 `PARTIAL`，未创建 P14R-A/P14R-B。

追加验证（2026-08-28）：复用既有 `research_turns.parent_turn_id` 完成终态
ResearchTurn 的不可变分支边界。服务端现在允许从同项目、同会话的任意终态
Turn 创建新子 Turn，非终态父 Turn 和跨项目/会话关系仍 fail-closed；父消息、
父 ContextSnapshot 与父 ScientificResult 不被修改。Continue、rerun、
reinterpret 均显式提交父 Turn ID。域回归 `9 passed`，前端 follow-up 回归
`3 passed`。消息文本编辑/修订 UI 和完整分支浏览器验收仍待完成，Phase 14-R
保持 `PARTIAL`，未创建 P14R-A/P14R-B。
## Agent-2.0 Phase 14-R — Report evidence continuity

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改摘要：Scientific Report presentation blocks now retain the persisted
  interpretation identity, enabling the existing authorized evidence inspector
  to resolve exact Result, Artifact, ToolCall and ScientificObjectVersion
  provenance from a report without creating a second authority.
- 测试结果：focused frontend `14 passed`; frontend typecheck `PASS`;
  authenticated same-stack browser report evidence inspection `PASS`;
  persisted no-recompute counts remained Jobs `96`, ToolCalls `131`, Artifacts
  `529`, ScientificResult snapshots `68`.
- 提交/CI 状态：本阶段尚未创建 P14R-A/P14R-B；Phase 14-R remains
  `PARTIAL`.

## Agent-2.0 Phase 14-R — Historical ContextManifest compatibility

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改摘要：为缺少内嵌 manifest 的历史 `CONTEXT_RESOLVED` 事件增加只读、
  有界的 `research_context_snapshots` 兼容投影，保留精确对象/版本、Dataset
  语义选择、Result 引用、约束和指纹；未引入第二上下文权威。
- 测试结果：API/context focused `20 passed`。
- 提交/CI 状态：本阶段尚未创建 P14R-A/P14R-B；Phase 14-R remains
  `PARTIAL`。

## Agent-2.0 Phase 14-R — Warm navigation performance baseline

- 状态：已完成当前基线采样；成熟产品门仍为 `PARTIAL`
- 完成时间：2026-08-28
- 修改摘要：在真实已认证同栈浏览器记录 Data、Research、Report、Tasks、
  Notifications 暖启动导航耗时，并同步性能基线与产品现实审计。
- 测试结果：Data `175 ms`、Research `215 ms`、Report `259 ms`、Tasks
  `202 ms`、Notifications `189 ms`；页面仍保持认证，未关闭服务或标签页。
- 提交/CI 状态：未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — Structure report browser proof

- 状态：已完成历史 Structure 报告真实浏览器复核；成熟产品门仍为
  `PARTIAL`
- 完成时间：2026-08-28
- 修改摘要：在认证同栈浏览器打开历史 Structure 报告，确认
  CrystalNN/VoronoiNN 结果、站点表、邻居关系、警告与复现信息均来自持久
  化结果；打开报告不触发科学重算。
- 测试结果：科学状态计数保持
  `analysis_plans=133`、`jobs=117`、`tool_calls=158`、`artifacts=637`、
  `scientific_result_snapshots=88`。
- 提交/CI 状态：未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — Persisted Figure artifact bridge

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/scientific_reports/service.py`、
  `apps/web/app/lib/scientific-report-api.ts`、
  `apps/web/app/lib/scientific-presentation.ts`、
  `apps/web/app/components/ScientificReportRoute.tsx`、
  `tests/test_agent2_phase8_reports.py` 及 Phase 14-R 证据文档。
- 修改摘要：报告 API 从不可变 ScientificResult bundle 派生有界
  `figure_sources`，包含 Figure 对应的持久化 Artifact IDs 与 source Job；
  Report/Presentation 通过既有授权 Artifact 内容路由打开真实图表，缺失
  映射时保留 exact-source Viewer 回退。未引入第二事实源，打开图表不执行
  新科学计算。
- 测试结果：后端报告 focused `16 passed, 4 historical skips`；前端报告/
  presentation focused `15 passed`；同栈报告/规划回归 `9 passed, 0 skipped`
  （PostgreSQL/Redis/MinIO）；前端全量 `96 files / 612 passed`；
  typecheck `PASS`；production build `PASS`。
- 提交/CI 状态：本阶段变更尚未创建 P14R-A/P14R-B；Phase 14-R remains
  `PARTIAL`，Capability-wide same-stack Figure、Trash/retention、报告质量与
  真实用户验收仍未闭合。

补充验证（2026-08-28）：真实 PostgreSQL/Redis/MinIO 报告生成、跨进程重开
及规划服务集合 `9 passed, 0 skipped`；Agent2 API/domain/report 组合回归
`42 passed, 4 historical live-LLM skips`。这些结果确认 Figure 来源扩展没有
破坏既有授权、报告生成或零科学状态增量约束。
当前实现提交为 `456d0a9`（其父提交 `2141fb1` 包含 Figure Artifact
路由回归）；工作树中的 Phase 14-R 仍未创建发布候选 P14R-A/P14R-B。

补充修复（2026-08-28）：Markdown 导出为每个主要 Figure 保留对应的持久化
Artifact IDs；ScientificReportRoute focused `5 passed`，typecheck `PASS`。

补充收口（2026-08-28）：创建 `AGENT2_PHASE14R_RESULTS.md`，集中记录当前
Phase 14-R 证据、同栈健康、回归计数和未闭合成熟产品门；状态仍为
`FUNCTIONAL_PHASE14R_CLOSURE = FAIL`，未创建 P14R-A/P14R-B。

补充浏览器证据（2026-08-29）：真实同栈 Data Platform Structure Viewer
打开 object `dc3c3eee-f254-4edf-a0fa-c955402b3069` / exact version
`8859cb49-0766-48cd-8a56-e44f5332e0c5`，显示 Si、晶格、位点和交互画布；
等轴、2×2×2 预览、复位操作后 `jobs=117`、`tool_calls=158`、
`artifacts=637`、`results=88` 均不变，Structure 路径的
Viewer no-recompute PASS。其他 Viewer 家族仍未全量资格化。

## Agent-2.0 Phase 14-R — Research progress reconnect

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、Phase 14-R 审计与进度文档。
- 修改摘要：进行中的 Agent2 Research 进度轮询监听浏览器 `online` 事件，
  恢复联网后重读同一持久化 Turn 进度；不创建新 Turn/Job/ToolCall/Artifact/
  Result，也不伪造进度。
- 测试结果：`ResearchPages.test.tsx` `36 passed`；`npm run typecheck`
  `PASS`。完整网络中断、API 重启与 Worker 恢复浏览器验收仍未完成。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — bounded Scientific Report export

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/lib/scientific-report-api.ts`、
  `apps/web/app/components/ScientificReportRoute.tsx`、
  `apps/web/app/components/ScientificReportRoute.test.tsx`、相关 CSS 与
  Phase 14-R 证据文档。
- 修改摘要：专用科学报告页面新增“导出 Markdown”，由已授权报告快照确定性
  生成；包含 Report/Snapshot/ResearchTurn/ScientificResult 身份、exact
  source version、发现、限制、证据与复现信息，不包含凭据、Provider transcript
  或内部队列/存储细节，也不触发科学重算。
- 测试结果：ScientificReportRoute `4 passed`；`npm run typecheck`
  `PASS`。完整可移植复现包、Retention/Trash 与真实用户验收仍未完成。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — authenticated Scientific Report browser evidence

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：Phase 14-R 审计与进度文档。
- 修改摘要：内置浏览器真实打开项目报告列表和现代 Dataset 报告，页面展示
  exact Dataset version、方法、发现、限制、证据折叠区及 `导出 Markdown`
  入口，浏览器错误/警告日志为空。
- 测试结果：报告路由可达；点击导出入口未产生页面错误，但浏览器下载事件
  未捕获 Blob 完成传输，因此仅记录入口可达，不宣称端到端导出传输完成。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — report source/method presentation

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/ScientificReportRoute.tsx`、
  `apps/web/app/components/ScientificReportRoute.test.tsx`、
  `apps/web/app/globals.css`、Phase 14-R 审计与进度文档。
- 修改摘要：报告主视图新增“数据与方法”区块，直接展示已有
  `viewer_sources` 的对象类型、精确版本 ID 与当前/历史状态，并展示
  权威方法摘要；移除重复的折叠方法段，未新增科学事实来源。
- 测试结果：Scientific Report route/action `5 passed`；`npm run typecheck`
  `PASS`；报告质量多族群和完整浏览器验收仍未完成。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — current-head same-stack regression

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：无新增生产代码；更新 Phase 14-R 证据文档。
- 修改摘要：在保持 API、Worker、PostgreSQL、Redis、MinIO 运行的条件下，
  重跑 ContextManifest、Agent2 PostgreSQL 规划和 Workspace/Result 服务回归。
- 测试结果：`8 passed, 0 failed, 0 skipped`，耗时 `116.10s`；健康端点仍为
  `database=postgresql`、`redis=redis`、`artifactStorage=minio`、
  `worker=redis`、DeepSeek 已配置。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — task-center online resynchronization

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/TaskCenterPage.test.tsx`、Phase 14-R 审计与进度
  文档。
- 修改摘要：任务中心监听浏览器 `online` 事件，恢复联网后立即使当前读取
  失效并重新加载授权项目与持久化 Job 状态；仍保留可见性恢复和 30 秒刷新。
  该逻辑只同步服务端事实，不制造进度、不取消任务、不修改科学结果。
- 测试结果：`TaskCenterPage.test.tsx` `1 passed`；`npm run typecheck`
  `PASS`；`npm run build` `PASS`。完整断网/API 重启/Worker 恢复浏览器验收
  仍未完成。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — authenticated task/notification browser evidence

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：Phase 14-R 审计与进度文档。
- 修改摘要：在保持服务和用户标签页不关闭的前提下，通过内置浏览器真实
  打开并验证 `/notifications` 与 `/tasks`；通知中心显示 4 条持久化终态
  通知，任务中心显示 2 个进行中、4 个已结束任务及 4 个授权项目，精确
  项目/研究链接和同步时间均可见。
- 测试结果：浏览器页面加载成功；此前通知/任务聚焦测试 `2 passed`，
  同栈健康为 PostgreSQL/Redis/MinIO/Redis worker。断网、API 重启和 Worker
  恢复的完整浏览器验收仍未完成。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — notification-center online resynchronization

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/NotificationCenterPage.tsx`、
  `apps/web/app/components/NotificationCenterPage.test.tsx`、Phase 14-R 审计与
  进度文档。
- 修改摘要：通知中心监听浏览器 `online` 事件，恢复联网后立即重新读取授权
  的持久化终态通知；与任务中心一致，不创建 Job、不改变终态、不伪造通知。
- 测试结果：通知中心与任务中心聚焦回归 `2 passed`；`npm run typecheck`
  `PASS`。完整断网/API 重启/Worker 恢复浏览器验收仍未完成。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — Current-worktree regression refresh

- 状态：已完成（验证）
- 完成时间：2026-08-28
- 修改文件：无（仅验证）
- 修改摘要：通知中心、任务中心重试入口合入后，重新验证真实同栈运行时与当前工作树。
- 测试结果：同栈服务回归 `8 passed, 0 failed, 0 skipped`；前端全量
  `96 test files / 610 tests passed`；typecheck、production build、compileall、
  `git diff --check` 通过；`/health/runtime` 为 PostgreSQL/Redis/MinIO/Redis
  worker/DeepSeek。
- 提交/CI 状态：未创建 P14R-A/B；Phase 14-R verdict 保持 PARTIAL。

## Agent-2.0 Phase 14-R — Network interruption recovery affordance

- 状态：已完成（增量）
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/ProductShell.tsx`、
  `apps/web/app/components/ProductShell.test.tsx`、
  `apps/web/app/globals.css`、
  `docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：全局产品壳增加浏览器离线/恢复提示，明确服务器任务可能继续，
  恢复后通过任务中心重新同步；不改变任何科学或任务持久化状态。
- 测试结果：`ProductShell.test.tsx` 5 passed；`npm run typecheck` passed。
- 提交/CI 状态：待提交；Phase 14-R 当前 verdict 仍为 PARTIAL。

## Agent-2.0 Phase 14-R explicit terminal retry

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/ResearchExecutionActivity.tsx`、
  `apps/web/app/components/ResearchExecutionActivity.test.tsx`、
  `apps/web/app/components/ResearchPages.tsx`，以及 Phase 14-R 审计/持久化文档。
- 修改摘要：失败/取消的研究执行现在才显示“重试研究”；该动作复用持久化
  session 与 parent Turn 创建新的不可变重试 lineage，保留失败历史，不宣称
  结果复用，也不在运行中显示。
- 测试结果：`ResearchExecutionActivity.test.tsx` 6 passed；web typecheck
  PASS。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains PARTIAL。

## Agent-2.0 Phase 14-R explicit ResearchTurn branch navigation

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/research_agent/service.py`、
  `apps/web/app/lib/agent2-research-api.ts`、
  `apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`、
  `apps/web/app/globals.css`，以及 Phase 14-R 审计/持久化文档。
- 修改摘要：Research API 返回持久化 `parent_turn_id`；客户端读取当前会话
  Turn 列表并提供显式、可访问的 sibling branch switcher，使用精确
  `researchTurnId` 链接，不再从 Job 名称猜测身份。旧 Turn 无关系时保持
  fail-closed。
- 测试结果：`ResearchPages.test.tsx` 36 passed；`tests/test_agent2_api.py`
  与 `tests/test_agent2_domain.py` 共 26 passed；web typecheck PASS。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains PARTIAL。

## Agent-2.0 Phase 14-R task-center attention and refresh

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/globals.css`，以及 Phase 14-R 审计/持久化文档。
- 修改摘要：任务中心在页面重新可见与 30 秒周期触发持久化刷新，并将失败、
  部分完成、取消任务单独归入“需要关注”，同步时间只在真实授权请求成功后
  展示，不生成虚假进度或科学状态。
- 测试结果：`TaskCenterPage.test.tsx` 1 passed；web typecheck PASS。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains PARTIAL。

## Agent-2.0 Phase 14-R persisted Result context control

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/lib/agent2-memory-api.ts`、
  `apps/web/app/components/Agent2ScientificPresentation.tsx`、
  `apps/web/app/components/Agent2ScientificPresentation.test.tsx`，以及
  Phase 14-R 审计/持久化文档。
- 修改摘要：科学结果呈现提供“固定到研究上下文/取消固定结果”操作，
  复用现有受权会话 memory API，只变更上下文选择，不写入
  ScientificResult、ScientificObjectVersion 或执行链路。
- 测试结果：`Agent2ScientificPresentation.test.tsx` 5 passed；web
  typecheck PASS。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains PARTIAL。

## Agent-2.0 Phase 14-R — Persisted task center bridge

- 状态：部分完成；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改摘要：新增 `/tasks` 全局后台任务页，聚合授权项目的持久化分析
  Job，区分进行中/已结束状态，并按现有 Workspace 或 Research run 关系提供
  精确打开路径。
- 增加显式“重新加载”操作，失败或返回页面时重新读取授权的持久化 Job
  状态，不创建新的科学状态。
- 活动任务在存在明确 `researchTurnId` 时可通过既有取消 API 执行“停止研究”；
  没有关联 Turn 的 legacy 任务不显示取消入口，避免 Job 名称猜测。
- 测试结果：TaskCenterPage `1 passed`，ProductShell `4 passed`，web
  typecheck `PASS`，当前完整前端回归 `95 files / 606 tests passed`。
- 已认证浏览器实际打开 `/tasks`，显示 `2` 个进行中、`4` 个已结束和
  `4` 个授权项目；PostgreSQL/Redis/MinIO 服务 smoke 集合为
  `5 passed, 0 failed, 0 errors, 0 skipped`。
- 受影响的 Workspace service-backed 集成回归为 `3 passed, 0 skipped`。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R remains `PARTIAL`。

## Agent-2.0 Phase 14-R — Authorized global search projection

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `apps/api/mdi_api/main.py`、`apps/web/app/lib/planner-api.ts`、
  `apps/web/app/components/ProductShell.tsx`、对应测试与 Phase 14-R 文档。
- 修改摘要：新增有界、项目授权的统一搜索投影，覆盖项目、数据集、科学
  对象、Research 会话、报告和 ScientificResult；ProductShell 搜索对话框
  通过受控路由展示并打开结果。未复制科学事实、原始 Artifact 或凭据，
  未引入新的科学权威。
- 测试结果：`tests/test_project_access.py` 12 passed；
  ProductShell/ResearchPages 聚焦 38 passed；web typecheck PASS；
  `/health/runtime` PostgreSQL/Redis/MinIO/Redis worker PASS；已认证同栈
  浏览器搜索实际显示授权记录。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；Phase 14-R 仍为 `PARTIAL`。

追加验证（2026-08-28）：结果页新增 `编辑问题`，通过显式 `turn`/`edit`
参数进入编辑 composer；提交时从父 Result 恢复原问题与 exact source refs，
创建新的带 `reply_to_turn_id` 的 ResearchTurn 分支，旧消息、旧上下文和旧
ScientificResult 不被修改。域回归 `9 passed`，前端呈现回归 `4 passed`，
ResearchPages 回归 `35 passed`，typecheck PASS。完整浏览器编辑提交和分支
切换仍待完成，Phase 14-R 继续保持 `PARTIAL`，未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — Session-list ResearchTurn projection

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改摘要：在授权 Research 会话详情的 `runReferences` 中返回持久化
  `researchTurnId`；无 ResearchTurn 的 legacy 记录继续返回 `null`，未引入
  Job 名称解析或第二身份权威。
- 测试结果：项目授权/历史回归 `11 passed`；Ruff `PASS`；web typecheck
  `PASS`。
- 提交/CI 状态：本阶段尚未创建 P14R-A/P14R-B；Phase 14-R remains
  `PARTIAL`。

补充验证（2026-08-28）：滚动重启 API 后，保留的已认证 Research 标签页
显示“本次研究使用的上下文”，历史 Dataset 的 exact object/version 与
Presentation 仍保持不变。该旧会话仍有独立的“研究对话暂时无法读取”恢复
提示，因此完整历史会话恢复门仍为 PARTIAL；本次兼容接口修复由 API focused
20 项回归覆盖。

## Agent-2.0 Phase 14-R — Explicit session fallback continuity

- 状态：阶段性闭环；Phase 14-R 总任务仍为处理中
- 完成时间：2026-08-28
- 修改摘要：修复 Research 路由在 `sessionId + runId` 同时存在、但历史 run
  尚未归一化绑定到该会话时错误丢失明确会话目标的问题；显式 session 现在
  作为安全回退，run-only orphan route 仍 fail-closed。
- 测试结果：`apps/web/app/components/ResearchPages.test.tsx` 为 `35 passed`；
  web typecheck `PASS`；保留的已认证浏览器历史研究页刷新后成功加载，
  Context disclosure 可见且不再出现“研究会话不存在或已不可访问”，对应
  research-session API 返回 `200 OK`。随后完整前端回归为
  `94 files / 601 passed`。
- 提交/CI 状态：本阶段尚未创建 P14R-A/P14R-B；Phase 14-R remains
  `PARTIAL`。
## Agent-2.0 Phase 14-R — same-stack worker MinIO environment parity

状态：已完成（窄范围修复；Phase 14-R 总体仍为 PARTIAL）
完成时间：2026-08-28
修改文件：`tests/integration/test_agent2_phase4_service_backed.py`、
`AGENT2_PHASE14R_RESULTS.md`、`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
`persistent/DESIGN_PROGRESS.md`
修改摘要：为 fresh execution worker 传递与 fixture 一致的 MinIO endpoint、
credential aliases 与 bucket，修复精确 ScientificObjectVersion payload hydration
在子进程中的环境不一致；未修改科学权威、版本或 worker 执行契约。
测试结果：`tests/integration/test_agent2_phase7_service_backed.py` 为
4 passed、0 failed、0 errors、0 skipped；前端全量 96 files / 613 tests passed；
`git diff --check` 通过。
提交/CI 状态：未创建 Phase 14-R release commit，未推送，待剩余成熟度门闭合。

## Agent-2.0 Phase 14-R — direct Project History ResearchTurn relation

- 状态：已完成（窄范围连续性修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/routers/project_history.py`、
  `tests/test_project_history_research_context.py`、Phase 14-R 结果与审计
  文档、`persistent/DESIGN_PROGRESS.md`。
- 修改摘要：Project History 在保留 legacy session-run 兼容逻辑的同时，
  直接读取授权项目内 `research_turns.job_id` 关系，使现代 Agent2 作业即使
  没有旧 `research_session_runs` 绑定，也能返回权威 `researchTurnId` 和
  `RESEARCH_TURN` 上下文类型；不再依赖 Job 名称推断。
- 实时证据：同栈 API `/health/runtime` 为 PostgreSQL/Redis/MinIO/Redis
  worker；认证 history 请求将 `job_agent2_8382...` 解析为
  `8382c443-f9ca-4c90-9aa3-444fea683807`，将 `job_agent2_17b67...` 解析为
  `17b67e68-b7db-475b-bb4c-3b336cb2ba15`。
- 测试结果：`tests/test_project_history_research_context.py` 4 passed；
  touched Ruff PASS；`git diff --check` PASS。
- 提交/CI 状态：尚未创建 P14R-A/P14R-B；服务和 Chrome 保持运行。

## Agent-2.0 Phase 14-R — Dataset semantic constraint binding

- 状态：已完成（窄范围规划/执行修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/research_agent/planning/binder.py`、
  `tests/test_agent2_phase3_planning.py`、Phase 14-R 审计/结果文档、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：Binder 将 Dataset `sample`/`property` 作为语义-only 约束保留在
  需求和 ContextSnapshot 中，不再把它们传入严格 Tool 参数；任意未知参数
  仍 fail-closed，未改变科学权威。
- 实时证据：Turn
  `3b85fa42-dcc8-42b3-ac68-f5f54b610df4` → Plan
  `plan_4d7388c0464c4311af4dcd02` → Job
  `job_agent2_3b85fa42dcc842b3ac68f5f54b610df4` → Result
  `e2587ca6-9b1f-5532-9e79-0ae6a89d6777` /
  Snapshot `8ac5b6d2-c5d7-4f31-8b19-4776149106bc` → Interpretation
  `70e03e81-2185-4870-abfa-c2a18565a026`; `VALID`, `COMPLETED`，`mat-2`
  `band_gap=2.5` fact 存在。
- 测试结果：`tests/test_agent2_phase3_planning.py` `21 passed, 1 skipped`；
  Ruff、compileall、git diff check PASS。
- 提交/CI 状态：未创建 Phase 14-R release commit，未推送；服务和 Chrome
  保持运行。

## Agent-2.0 Phase 14-R — session-list exact ResearchTurn continuity

- 状态：已完成（窄范围产品连续性修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/routers/research.py`、
  `tests/test_project_access.py`、Phase 14-R 审计/结果文档、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：`/research-sessions` 现在在 legacy 兼容投影之外合并授权项目内
  现代 `research_turns` 的直接 session/job 关系，使任务中心携带的精确
  `run + turn` 链接能恢复真实 Research 对话；旧运行继续保留 run-only
  只读回退，不依赖 Job 名称猜测。
- 实时浏览器证据：认证 Chromium 从 `/tasks` 打开
  `job_agent2_8382...` / Turn `8382c443-f9ca-4c90-9aa3-444fea683807`，
  “没有可恢复研究对话”误报消失，Context disclosure 与 `mat-2` 结果可见，
  console/page/critical-request/overflow 均为 0。
- 测试结果：Project Access + history `19 passed`；touched Ruff PASS；
  `git diff --check` PASS。
- 提交/CI 状态：未创建 P14R-A/P14R-B；服务与 Chrome 保持运行。

## Agent-2.0 Phase 14-R — result reuse browser proof

- 状态：已完成（窄范围结果复用闭环；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-28T23:00:00+08:00
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、
  `docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `persistent/DESIGN_PROGRESS.md`、`results.md`。
- 修改摘要：保持 PostgreSQL/Redis/MinIO 与 Chrome 开放，启动既有
  `.phase13-start-workers.ps1` 五队列 worker，完成认证
  `INTERPRET_RESULT` 浏览器路径。Turn
  `cc704d3f-dcfc-4a49-a971-2cda6282039c` 复用快照
  `2809dcd1-243e-4323-8538-0a5fe81780d9`，解释
  `ce8c820d-2f42-4a82-9593-714971b5ad09` 为 `VALID`，分析 Job 数量
  `4 → 4`。初始 `RECEIVED` 根因为 worker 进程退出，分类为
  `WORKER_PROCESS_NOT_RUNNING`，未修改科学路由或权威模型。
- 测试结果：真实 Chromium 同栈浏览器轮询与结果/解释/事件 API 成功；
  五个 worker 进程保持运行。
- 提交/CI 状态：未创建 Phase 14-R release commit；成熟产品 release gate
  仍未闭合。

## Agent-2.0 Phase 14-R — edit branch context isolation

- 状态：已完成（窄范围编排边界修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/research_agent/context/assembler.py`、
  `tests/test_phase14r_context_manifest.py`、Phase 14-R 审计/结果文档、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：带 `parent_turn_id` 的编辑/重跑/重试子 Turn 在未显式绑定
  Result snapshot 时不再注入近期历史 Result，避免错误走
  `INTERPRET_RESULT` 并污染 grounding；显式 reinterpret/continue 仍保持
  Result authority。
- 实时浏览器证据：API 与五个 worker 在 PostgreSQL/Redis/MinIO 同栈重载后，
  编辑产生子 Turn `1176df48-b0a4-4611-bf42-970ef2c6d181`，父 Turn
  `8382c443-f9ca-4c90-9aa3-444fea683807`；ContextSnapshot
  `6d7f8505-0adc-46ef-a09b-bffb4e9757f0` 中 Result 候选为 0，精确 Dataset
  版本与 `mat-2` 保留，路由为正确的 `ANSWER`，终态 `ANSWERED`，无子 Turn
  Job/Result。
- 测试结果：Phase 14-R context `4 passed`；Agent2/API/access/history
  focused `40 passed`。
- 提交/CI 状态：未创建 P14R-A/P14R-B；服务和 Chrome 保持运行。

## Agent-2.0 Phase 14-R — 编辑分支真实浏览器验收

- 状态：已验证（浏览器控制链；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-28
- 证据：父 Turn `8382c443-f9ca-4c90-9aa3-444fea683807` 创建子 Turn
  `dc76de32-4675-4b6a-91fd-ef102602c905`；父状态保持 COMPLETED，子
  ContextSnapshot `e58057b5-b88b-495e-a855-29dd46a4c953` 保留精确
  Dataset object/version 与 `mat-2`，子请求最终 ANSWERED 且无 Job/Result。
- 浏览器质量：无 page error、无 5xx；轮询期间
  `SCIENTIFIC_RESULT_NOT_READY` 409 为预期 fail-closed。
- 提交/CI 状态：未提交；未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — Scientific presentation pin-state race

- 状态：已完成（窄范围产品缺陷修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-28
- 修改文件：`apps/web/app/components/Agent2ScientificPresentation.tsx`、
  `apps/web/app/components/Agent2ScientificPresentation.test.tsx`、
  Phase 14-R 审计/结果文档、`persistent/DESIGN_PROGRESS.md`
- 修改摘要：修复 session-memory 延迟旧读覆盖已确认 pin/unpin 状态的竞态；
  复用现有 mutation sequence，不改变科学结果或上下文权威。
- 测试结果：Agent2ScientificPresentation `6 passed`；前端全量
  `96 files / 615 passed`；后端默认 SQLite 隔离 `1833 passed / 83 skipped`；
  显式 PostgreSQL/Redis/MinIO service-backed Phase 3/4/5 `4 passed`；
  Ruff、compileall、git diff --check `PASS`。
- 提交/CI 状态：未提交；未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — terminal projection direct Turn relation

- 状态：已完成（窄范围连续性修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-28
- 修改文件：`apps/api/mdi_api/routers/research.py`、
  `tests/test_project_access.py`、Phase 14-R 审计/结果文档、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：终端解释投影优先通过现代 `research_turns` 的精确
  `research_session_id`/`job_id` 关系恢复会话，仅在旧数据或滚动部署场景
  回退 `research_session_runs`；避免现代 Agent2 结果因缺少 legacy 绑定而
  丢失 assistant projection。
- 测试结果：Project Access/history/reconciliation `20 passed`；touched
  Ruff PASS；`git diff --check` PASS。
- 提交/CI 状态：未创建 P14R-A/P14R-B；服务与 Chrome 保持运行。
## Agent-2.0 Phase 14-R — grounded Report narrative quality increment

- 状态：处理中（完成一个 R2 子门，Phase 14-R 尚未封板）
- 完成时间：2026-08-29T08:35:00+08:00
- 修改摘要：为 immutable Scientific Report 增加受约束的科学讨论、结论和
  后续工作区块；所有科学数字/单位仍通过 Result fact/evidence grounding，
  页面与 Markdown 导出同步呈现，不触发科学重计算。
- 测试结果：Report 后端 18 passed、4 compatibility skips；Report/
  presentation 前端 16 passed；typecheck PASS；touched Ruff PASS。
- 提交/CI：未提交；Phase 14-R 仍有能力面、生命周期、恢复、运维和
  exact-SHA 发布门未闭合。
# Agent-2.0 Phase 14-R — Scientific Object lifecycle action wiring

状态：已完成（窄范围 UI bridge）
完成时间：2026-08-29
修改文件：`apps/web/app/components/ProductPages.tsx`、
`apps/web/app/components/ProductPages.test.tsx`、
`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
`AGENT2_PHASE14R_RESULTS.md`、`persistent/DESIGN_PROGRESS.md`
修改摘要：在 Data Platform 科研对象列表复用既有
`PATCH /api/scientific-objects/{object_id}`，为 ACTIVE/ARCHIVED 对象提供归档/
恢复操作；按当前过滤视图移除已变更对象，未引入新 authority。
测试结果：ProductPages `20 passed`；此前 Report、Research execution、
context focused checks 仍为绿色；服务保持运行。
提交/CI 状态：未创建 Phase 14-R release commit；总任务仍为处理中。

# Agent-2.0 Phase 14-R — ContextManifest budget truthfulness repair

状态：已完成（窄范围 context contract 修复）
完成时间：2026-08-29
修改文件：`apps/api/mdi_api/research_agent/service.py`、
`tests/test_phase14r_context_manifest.py`、`AGENT2_PHASE14R_RESULTS.md`、
`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`
修改摘要：ContextManifest 现在先按确定性优先级构造真实 bounded inclusion
集合，科学对象/选择/Result 放不下时 fail-closed，低优先级约束/目标以稳定
item id 记录为 excluded；不再出现“保留全部内容却标记已压缩”的不实状态。
测试结果：context focused `5 passed`；Report/context/history/API focused
`28 passed, 4 compatibility skips`；Ruff 与 diff check 通过。
提交/CI 状态：未创建 Phase 14-R release commit；总任务仍为处理中。

# Agent-2.0 Phase 14-R — Operations recovery qualification

状态：已完成（R11 核心恢复演练；Phase 14-R 总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：`docs/agent2/phase14r/OPERATIONS_AND_RECOVERY_QUALIFICATION.md`、
`AGENT2_PHASE14R_RESULTS.md`、
`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
`persistent/DESIGN_PROGRESS.md`、`results.md`
修改摘要：在不停止当前 PostgreSQL/Redis/MinIO/API/workers/frontend 的前提
下完成 PostgreSQL 隔离备份恢复、MinIO checksum 备份恢复和缺失对象
fail-closed、隔离 Redis 瞬态丢失/重启边界；同一 Job 队列发布失败恢复保持原
Job identity。
测试结果：PostgreSQL 11 个核心表计数与 Alembic 完全一致，孤儿版本/错误
current pointer 为 0；MinIO 四次 SHA-256 一致且缺失对象 404；Redis 主实例
持续 PONG，确定性恢复回归 `2 passed`；DB `active=1 / idle=10 /
idle-in-transaction=0`。
提交/CI 状态：未创建 P14R-A/P14R-B；历史测试队列治理、监控/配额和其余
成熟产品门仍未闭合。

# Agent-2.0 Phase 14-R — RQ queue lifecycle and worker availability

状态：已完成（测试资源泄漏与 worker 可用性修复；Phase 14-R 总体仍为
PARTIAL）
完成时间：2026-08-29
修改文件：`tests/integration/test_agent2_phase2_service_backed.py` 至
`test_agent2_phase8_service_backed.py`、
`.phase14r-start-missing-workers.ps1`、Phase 14-R 运维/结果/审计文档、
`persistent/DESIGN_PROGRESS.md`、`results.md`
修改摘要：service-backed fixture 在成功/finally 路径删除唯一 RQ queue
注册；Phase 4 默认隔离 Result projection，Phase 5 显式启用自己的 Result
queue；清理确认无 active/scheduled/deferred 的 208 个历史测试队列注册与
一个指向已失败 PostgreSQL Job 的孤立 Redis wakeup；补回缺失的 planning/
execution workers。
测试结果：Phase 2–5 `5 passed`，Phase 6–8 `10 passed`，测试 queue 数
campaign 前后 `208 → 208`，清理后 `0`；canonical 5 queues depth 0，
5 workers idle；Ruff/diff check PASS。
提交/CI 状态：未创建 P14R-A/P14R-B；主服务与 Chrome 未关闭。
# Agent-2.0 Phase 14-R — Dataset-list product fluency repair

状态：已完成（性能缺陷修复；Phase 14-R 总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：`apps/api/mdi_api/repositories.py`、
`apps/api/mdi_api/phase2_runtime.py`、
`tests/test_phase2_product_loop.py`、Phase 14-R 性能/审计/结果文档、
`persistent/DESIGN_PROGRESS.md`、`results.md`
修改摘要：将 durable Dataset list 的逐 Project/逐 Dataset N+1 查询改为
Projects、Datasets、Profiles 三次有界批量读取，保留授权过滤、Dataset identity
和确定性的最新 Profile 选择。
测试结果：129 rows；旧/新 SQL `265/3`；旧/新 p50
`312.0/19.7 ms`；focused `2 passed`；Ruff/diff check PASS。
提交/CI 状态：未创建 P14R-A/P14R-B；Phase 14-R release gate 仍未闭合。
# Agent-2.0 Phase 14-R — Redacted operations snapshot

状态：已完成（运维可观测性里程碑；Phase 14-R 总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：`apps/api/mdi_api/operations.py`、
`scripts/phase14r_operations_snapshot.py`、
`tests/test_phase14r_operations.py`、Phase 14-R 运维/审计/覆盖/结果文档、
`persistent/DESIGN_PROGRESS.md`、`results.md`
修改摘要：新增无秘密泄露的 PostgreSQL/Redis/RQ/worker/MinIO 运维快照，
区分 stale active/waiting Turn 与 recent/retained RQ failures，并以非零状态
真实暴露需关注项。
测试结果：focused `3 passed`；Ruff PASS；当前快照 5 workers idle、
queue depth 0、recent failures 0、idle-in-transaction 0、MinIO OK，同时识别
9 个历史 qualification active-stage Turn 和 1 个 `test_user` stale Job。
提交/CI 状态：未创建 P14R-A/P14R-B；告警投递、reconciliation policy、
concurrency/provider quotas 与 release gate 仍开放。
## Agent-2.0 Phase 14-R — fresh archive browser and corrected service campaign

- 状态：已完成（本轮证据补充，Phase 14-R 总体仍处理中）
- 完成时间：2026-08-29
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、`persistent/DESIGN_PROGRESS.md`
- 修改摘要：使用保持打开的认证内置浏览器完成 Dataset active → archive filter → restore → active 可逆路径；加载仓库同栈环境并启用 `MDI_RUN_INTEGRATION=1` 后重新执行 Phase 10L–10N 服务集合。
- 测试结果：真实 PostgreSQL/Redis/MinIO 服务集合 `21 passed, 0 failed, 0 errors, 0 skipped`（85.84s）；归档/恢复前后 typed rows 与 exact object/version 路由保持不变。
- 提交/CI 状态：未提交；Phase 14-R 仍未满足成熟产品全部门槛，未创建 P14R-A/P14R-B。

## Agent-2.0 Phase 14-R — Task Center stale-state clarity

- 状态：已完成（局部产品改进，Phase 14-R 总体仍处理中）
- 完成时间：2026-08-29
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、`TaskCenterPage.test.tsx`、`apps/web/app/globals.css`、Phase14-R evidence docs
- 修改摘要：对超过 15 分钟没有持久化状态更新的 active/queued 任务显示只读“需要检查”提示，保留原始状态、取消权限和精确任务路由，不伪造失败状态。
- 测试结果：Task Center focused `1 passed`；未改变 PostgreSQL/Redis/MinIO 服务或科学执行权威。
- 提交/CI 状态：未提交；P14R-A/P14R-B 尚未创建。

## Agent-2.0 Phase 14-R — Final same-stack operations recheck

- 状态：已完成（最终运行时复核，Phase 14-R 总体仍处理中）
- 完成时间：2026-08-29
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、`persistent/DESIGN_PROGRESS.md`
- 修改摘要：通过现有 launcher 补回 `mdi-agent-turns` worker，保持 PostgreSQL、
  Redis、MinIO、API、前端和认证浏览器标签页不变；同栈快照确认
  PostgreSQL active=1/idle=7、idle-in-transaction=0、Redis queue depth=0、
  5 个 canonical workers idle、MinIO OK、15 分钟内 RQ failures=0。
- 测试结果：操作快照诚实返回 `attention`，原因仍为 9 个历史自动阶段 stale
  Turns 与 1 个历史 stale Job；没有删除或改写这些记录。Task Center `1 passed`、
  touched Ruff 与 `git diff --check` 通过。
- 提交/CI 状态：未提交；P14R-A/P14R-B 未创建，成熟产品 release gate 仍未闭合。

## Agent-2.0 Phase 14-R — Recoverable Project/Dataset Trash

- 状态：已完成（Project/Dataset 局部生命周期闭环；Phase 14-R 总体仍处理中）
- 完成时间：2026-08-29
- 修改文件：Project/Dataset API lifecycle schemas、secured runtime、
  Project History/Dataset projection、Product/Data UI、global search、
  lifecycle tests、共享 schema、Phase 14-R lifecycle/audit/results 文档与
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：通过现有 `project_configs.config_json` 与
  `datasets.metadata_json` 增加可恢复 `TRASHED` 投影；保留回收前状态；
  Dataset 底层状态继续使用已发布约束内的 `archived`；新增依赖预览、
  Project/Data 回收站筛选、逐项和批量 Trash/Restore，并从 normal new-work
  actions 排除已回收实体。未创建或修改 ScientificObjectVersion。
- 测试结果：后端 lifecycle/access/history `20 passed`；前端 Project/Data
  lifecycle `28 passed`；typecheck、production build、touched Ruff、
  `git diff --check` PASS。恢复同栈运行后 `/health/runtime` 中
  PostgreSQL/Redis/MinIO/workers/DeepSeek 全部 `ok`。
- 提交/CI 状态：未创建 P14R-A/P14R-B；ScientificObject/Research/Report
  Trash、retention/purge/export、完整浏览器和 release gate 仍开放。

## Agent-2.0 Phase 14-R — Recoverable Research Session lifecycle

- 状态：已完成（Research Session 局部生命周期闭环；Phase 14-R 总体仍处理中）
- 完成时间：2026-08-29
- 修改文件：Research Session API/service/main route、Product Research UI/API
  client、ResearchPages regression、lifecycle/schema/evidence docs
- 修改摘要：复用 `sessions.status` 增加 project-authorized
  `TRASHED`/`ACTIVE` PATCH；归档或回收会话保留历史可读性但禁止新写入；
  非终态 Turn 阻止回收；Research Records 菜单增加可恢复回收/恢复操作。
- 测试结果：后端 `tests/test_project_access.py` 17 passed；前端
  `ResearchPages.test.tsx` 37 passed；typecheck、compileall、Prettier、
  `git diff --check` 通过。
- 提交/CI 状态：未提交；P14R-A/P14R-B 尚未创建，成熟产品总体仍未封板。

---TASK RESULT---
任务名称：Agent-2.0 Phase 14-R — Report 生命周期与同栈运行时修复
状态：已完成（窄范围修复；Phase 14-R 总体仍为 PARTIAL）
完成时间：2026-08-29T13:55:00+08:00
修改文件：apps/web/app/components/ScientificReportsIndexPage.test.tsx；AGENT2_PHASE14R_RESULTS.md；results.md；新增本地运行脚本 .phase14r-start-api-55434.ps1、.phase14r-start-workers-55434.ps1
修改摘要：补充 Report ACTIVE→TRASHED→ACTIVE 生命周期 UI 回归；将保留的同栈 API/worker 切换到完整 PostgreSQL 资格库，修复认证 500 的实际缺表根因；保持 PostgreSQL、Redis、MinIO、worker 与内置浏览器运行。
测试结果：Report UI 2 passed；Report/权限后端 45 passed、4 historical compatibility skips；PostgreSQL/Redis/MinIO Report service 4 passed、0 skipped；web typecheck PASS；登录接口 200；health/runtime PostgreSQL/Redis/MinIO/Redis worker/DeepSeek 全部 ok。
提交/CI 状态：未提交；未推送；Phase 14-R 仍 PARTIAL，P14R-A/P14R-B 未创建。
---END TASK RESULT---

---TASK RESULT---
任务名称：Agent-2.0 Phase 14-R — Report dependency-impact confirmation
状态：已完成（窄范围修复；Phase 14-R 总体仍处理中）
完成时间：2026-08-29
修改文件：apps/api/mdi_api/scientific_reports/service.py；apps/api/mdi_api/routers/scientific_reports.py；apps/api/mdi_api/main.py；apps/web/app/lib/scientific-report-api.ts；apps/web/app/components/ScientificReportsIndexPage.tsx；apps/web/app/components/ScientificReportsIndexPage.test.tsx；tests/test_agent2_phase8_reports.py；docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md；docs/agent2/phase14r/USER_LIFECYCLE_MANAGEMENT_CONTRACT.md；persistent/DESIGN_PROGRESS.md；AGENT2_PHASE14R_RESULTS.md
修改摘要：新增 project-authorized Report dependency-impact API；回收站动作先显示服务端派生的 ResearchTurn、ScientificResult、Interpretation、Artifact、Evidence 与 exact source-version 依赖并要求显式确认；保持不可变科学快照与历史来源不变。
测试结果：web ScientificReportsIndexPage `4 passed`；Report backend `20 passed, 4 skipped`；依赖预览断言通过。
提交/CI 状态：未提交、未推送；P14R-A/P14R-B 尚未创建；Phase 14-R 仍 PARTIAL。
---END TASK RESULT---

---TASK RESULT---
任务名称：Agent-2.0 Phase 14-R — Report lifecycle failure visibility
状态：已完成（窄范围修复；Phase 14-R 总体仍处理中）
完成时间：2026-08-29
修改文件：apps/web/app/components/ScientificReportsIndexPage.tsx；apps/web/app/components/ScientificReportsIndexPage.test.tsx；AGENT2_PHASE14R_RESULTS.md
修改摘要：报告归档/回收/恢复失败时显示明确页面告警，并保留原报告状态；新增失败回归。
测试结果：报告页 `4 passed`；此前全量前端 `96/96` 文件、`625/625` 测试通过；typecheck、Ruff、git diff --check PASS。
提交/CI 状态：未提交、未推送；Phase 14-R 仍 PARTIAL。
---END TASK RESULT---

---TASK RESULT---
任务名称：Agent-2.0 Phase 14-R — Report archive distinction and browser request hardening
状态：已完成（窄范围修复；Phase 14-R 总体仍处理中）
完成时间：2026-08-29
修改文件：apps/web/app/components/ScientificReportsIndexPage.tsx；apps/web/app/components/ScientificReportsIndexPage.test.tsx；apps/web/app/lib/scientific-report-api.ts；docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md；persistent/DESIGN_PROGRESS.md；AGENT2_PHASE14R_RESULTS.md；results.md
修改摘要：为报告列表补齐 ACTIVE→ARCHIVED、ACTIVE→TRASHED、ARCHIVED/TRASHED→ACTIVE 的最小产品动作；共享报告 API PATCH 请求自动声明 JSON Content-Type；生命周期失败显示可恢复页面告警。真实同栈浏览器完成回收站、历史报告读取、恢复和当前列表重新发现，科学记录计数无变化。
测试结果：前端全量 96 个测试文件、625 个测试通过；报告页 3 passed；Report 后端 20 passed、4 historical compatibility skips；typecheck PASS；touched Ruff PASS；git diff --check PASS；PostgreSQL jobs/tool_calls/artifacts/results 保持 194/250/995/127。
提交/CI 状态：未提交、未推送；P14R-A/P14R-B 尚未创建；Phase 14-R 仍 PARTIAL。
---END TASK RESULT---
## 2026-08-29 — Phase 14-R operations diagnostic entrypoint

- 任务名称：Phase 14-R 运维快照脚本可独立启动
- 状态：已完成（窄范围修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-29
- 修改文件：`scripts/phase14r_operations_snapshot.py`、
  `docs/agent2/phase14r/OPERATIONS_AND_RECOVERY_QUALIFICATION.md`、
  `persistent/DESIGN_PROGRESS.md`、`AGENT2_PHASE14R_RESULTS.md`
- 修改摘要：脚本从自身路径注入 `apps/api`，清洁 shell 下无需隐藏
  `PYTHONPATH` 即可加载诊断模块；运行时服务配置仍由环境变量提供。
- 测试结果：直接 `--help` 入口通过；同栈运行报告 PostgreSQL/Redis/MinIO
  健康、5 个 worker idle，并如实报告历史 stale turns/jobs 导致
  `status=attention`。
- 提交/CI 状态：未提交；未运行 CI。

## 2026-08-29 — Phase 14-R ScientificObject Trash lifecycle bridge

- 任务名称：ScientificObject recoverable Trash/Restore lifecycle
- 状态：已完成（窄范围修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-29
- 修改文件：`apps/api/mdi_api/db.py`、`apps/api/mdi_api/agent2_repositories.py`、
  `apps/api/mdi_api/scientific_objects/schemas.py`、
  `apps/api/mdi_api/scientific_objects/service.py`、
  `apps/api/mdi_api/routers/agent2.py`、
  `apps/api/alembic/versions/0026_scientific_object_trash_lifecycle.py`、
  `apps/web/app/lib/scientific-viewer-api.ts`、
  `apps/web/app/components/ProductPages.tsx`、相关测试与 Phase 14-R 文档。
- 修改摘要：在既有 ScientificObject lifecycle authority 上增加 TRASHED 和
  `pre_trash_lifecycle_status`，实现 ACTIVE/ARCHIVED 到 Trash 的可恢复状态
  转换；Data Navigator 增加 authoritative Trash 查询和对象恢复/移入回收站
  操作。未创建或修改任何 ScientificObjectVersion、Result、Artifact 或 Job。
- 测试结果：domain `10 passed`；API `17 passed`；ProductPages `22 passed`；
  touched Ruff、compileall、git diff --check PASS；同栈 PostgreSQL 已应用
  migration，实时对象完成 `ACTIVE → TRASHED → ACTIVE` 且版本数/current
  version 不变。
- 提交/CI 状态：未提交、未推送；Phase 14-R 仍 PARTIAL。

## 2026-08-29 — Phase 14-R ScientificObject dependency-impact preview

- 任务名称：ScientificObject Trash dependency-impact preview
- 状态：已完成（窄范围修复；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-29
- 修改文件：`apps/api/mdi_api/scientific_objects/service.py`、
  `apps/api/mdi_api/routers/agent2.py`、`apps/api/mdi_api/main.py`、
  `apps/web/app/lib/scientific-viewer-api.ts`、
  `apps/web/app/components/ProductPages.tsx`、相关测试与 Phase 14-R 文档。
- 修改摘要：增加 project-write 授权的
  `/api/scientific-objects/{object_id}/dependency-impact`，从 immutable
  ScientificResult、ResearchTurn 和 Report snapshot 派生有界 exact-version
  依赖；Data Navigator 在现有生命周期 PATCH 前展示受保护历史 provenance
  并要求显式确认。预览不修改 ScientificObjectVersion、Result、Artifact、
  Report 或 current-version pointer。
- 测试结果：`tests/test_agent2_api.py` 17 passed；
  `ProductPages.test.tsx` 24 passed；compileall、touched Ruff、
  `git diff --check` PASS。
- 提交/CI 状态：未提交、未推送；保留 Phase 14-R PARTIAL。
任务名称：Phase 14-R 浏览器资格运行时隔离
状态：已完成（窄范围修复）
完成时间：2026-08-29
修改文件：.phase14r-start-web.ps1、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、AGENT2_PHASE14R_RESULTS.md、persistent/DESIGN_PROGRESS.md
修改摘要：将 Next 开发运行时切换到独立 `.next-dev-phase14r` 构建目录，避免生产构建清空开发路由；复核同栈 API 与新 Chrome 产品标签页均恢复正常。
测试结果：GET /health/runtime=200（PostgreSQL/Redis/MinIO/Redis worker/DeepSeek 均 ok）；Chrome fresh product tab `/`=200；既有定向 API/domain/operations 回归通过。
提交/CI 状态：未提交；Phase 14-R 总体仍为 PARTIAL，待完整成熟产品门禁后再进行发布提交。

任务名称：Phase 14-R 报告复现清单导出
状态：已完成（窄范围能力）
完成时间：2026-08-29
修改文件：apps/web/app/lib/scientific-report-api.ts、apps/web/app/components/ScientificReportRoute.tsx、apps/web/app/components/ScientificReportRoute.test.tsx、docs/agent2/phase14r/USER_LIFECYCLE_MANAGEMENT_CONTRACT.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、AGENT2_PHASE14R_RESULTS.md、persistent/DESIGN_PROGRESS.md
修改摘要：新增有界、非可执行 `mdi.reproducibility-manifest/1.0` JSON 导出，保留授权 Report/Result/Interpretation/exact object-version/Figure Artifact/Evidence/限制身份，不导出凭据、prompt、原始 Tool 日志或不受限科学 payload。
测试结果：ScientificReportRoute.test.tsx = 8 passed；随后 full frontend = 96 files / 630 tests passed；typecheck/build 通过。
提交/CI 状态：未提交；Phase 14-R 总体仍为 PARTIAL，待完整导出治理与成熟产品门禁后再发布。

任务名称：Phase 14-R Viewer 修复后前端回归
状态：已完成（回归验证）
完成时间：2026-08-29
修改文件：无新增代码修改
修改摘要：在 E: 临时卷使用 Vitest single-fork 运行当前工作树完整前端回归。
测试结果：96 个测试文件通过，628 个测试通过；typecheck/build 通过。
提交/CI 状态：未提交；仅作为当前工作树证据，Phase 14-R 仍为 PARTIAL。

任务名称：Phase 14-R 当前工作树后端与静态收尾
状态：已完成（回归验证）
完成时间：2026-08-29
修改文件：无新增代码修改
修改摘要：完成当前工作树后端全量与静态检查，确认 Viewer fail-closed 修复未引入跨阶段回归。
测试结果：backend 1847 passed / 83 skipped / 0 failed / 0 errors；compileall、uv lock --check、touched Ruff、git diff --check PASS；/health/runtime=200（PostgreSQL/Redis/MinIO/worker/DeepSeek）。
提交/CI 状态：未提交；Phase 14-R 仍为 PARTIAL，P14R-A/P14R-B 未创建。

任务名称：Phase 14-R 精确源 Viewer 缺失对象处理
状态：已完成（窄范围修复）
完成时间：2026-08-29
修改文件：apps/api/mdi_api/scientific_viewers/service.py、tests/test_agent2_phase9_viewers.py、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、AGENT2_PHASE14R_RESULTS.md、persistent/DESIGN_PROGRESS.md
修改摘要：将 MinIO/S3 not-found 精确源映射为 `SOURCE_MISSING` 的只读元数据投影与明确限制；保留 checksum 等其他错误；避免历史 Viewer 因缺失源返回通用 500。
测试结果：tests/test_agent2_phase9_viewers.py = 7 passed；指定 Chromium 对象浏览器探针 critical 5xx = 0。
提交/CI 状态：未提交；Phase 14-R 总体仍为 PARTIAL，待完整成熟产品门禁后再进行发布提交。

任务名称：Phase 14-R Report 复现清单真实浏览器与零重计算验收
状态：已完成（Report 级窄范围；Phase 14-R 总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：AGENT2_PHASE14R_RESULTS.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md、persistent/DESIGN_PROGRESS.md、results.md
修改摘要：通过已认证 Chrome 正常 Report 路由点击“导出复现清单”，读取真实下载文件并验证 exact Report snapshot、ResearchTurn、ScientificResult、Interpretation、Dataset object/version、Evidence 与限制身份；敏感凭据、prompt、原始 Tool 日志及脚本检查均为阴性。
测试结果：浏览器控制台 warning/error = 0；导出前后 Jobs 196、ToolCalls 253、Artifacts 1007、ScientificResultSnapshots 129，全部 delta = 0。
提交/CI 状态：未提交；跨实体 retention/export、完整科学 surface、移动端和真实用户总验收仍未闭合，未创建 P14R-A/P14R-B。

任务名称：Phase 14-R 显式 Dataset handoff 与真实 worker 资格验证
状态：已完成（窄范围修复与证据）
完成时间：2026-08-29
修改文件：apps/web/app/projects/[projectId]/research/page.tsx、apps/web/app/components/ResearchPages.tsx、apps/web/app/components/ResearchPages.test.tsx、apps/web/app/lib/product-api.ts、tests/fixtures/tables/phase14r_band_gap_acceptance.csv、AGENT2_PHASE14R_RESULTS.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、persistent/DESIGN_PROGRESS.md
修改摘要：修复 Data Platform 显式 `?dataset=` handoff 丢失 Dataset scope 和旧会话抢占；通过真实上传入口验证 PostgreSQL/MinIO 根资源；启动五类 Redis worker 并完成真实 Job。XRD 不支持请求保持 fail-closed。
测试结果：ResearchPages 38 passed；product-api 4 passed；真实上传 Dataset `dataset_0002_53c12dddfa984a80`，Job `job_9a63cc82cf574e25a88529c7` completed，1 ToolCall，3 Artifacts；旧 Planner UI 未自动生成 ResearchTurn/ScientificResult interpretation，Phase 14-R 仍为 PARTIAL。

任务名称：Phase 14-R fresh Dataset scientific execution 与 Report grounding 修复
状态：已完成（窄范围闭环；Phase 14-R 总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：apps/api/mdi_api/scientific_objects/service.py、apps/api/mdi_api/scientific_reports/grounding.py、tests/test_agent2_phase8_reports.py、AGENT2_PHASE14R_RESULTS.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、persistent/DESIGN_PROGRESS.md、results.md
修改摘要：修复 Dataset promotion 使用错误 repository bundle 导致的 500，并保证相同 Dataset/resource 重复提升时复用已存在的 materials.table 对象/版本；修复 Report grounding 将 UUID/版本标识中的数字片段误判为科学数值的窄范围验证缺陷，保留不支持数字主张的 fail-closed 回归。
测试结果：fresh same-stack Dataset ResearchTurn `9c3a8278-69cf-4f9e-973a-e0b5d0e46779` 完成，ScientificResult snapshot `c73dd037-07bd-447e-a049-a97e5426d371` 含 16 facts，Interpretation `a674095b-7349-4d4f-9db7-e9008c0e0b8e`=`VALID`，Report `agent2_report_c91972312383616a6503acd6be76e233`=`READY`；报告定向测试 `21 passed/4 skipped`；前端全量 `96 files/631 passed`；后端全量 `1848 passed/83 skipped`；同栈集成子集 `11 passed/0 skipped`；typecheck、compileall、uv lock、Ruff、diff check 均 PASS；导出前后 Jobs 198、ToolCalls 255、Artifacts 1014、ScientificResultSnapshots 130，delta=0。
提交/CI 状态：未提交；服务、workers 和 Chrome 标签页保持开启；P14R-A/P14R-B 未创建，因 capability-wide viewer、retention/recovery、real-user acceptance 等强制门禁仍未闭合。
提交/CI 状态：未提交；服务与 Chrome 保持开启；P14R-A/P14R-B 未创建。

任务名称：Phase 14-R QUERY_DATA fresh browser terminal-state repair
状态：已完成（窄范围修复与真实浏览器证据；Phase 14-R 总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：apps/api/mdi_api/research_agent/orchestration/router.py、apps/web/app/lib/agent2-execution-api.ts、apps/web/app/components/ResearchExecutionActivity.tsx、apps/web/app/components/ResearchExecutionActivity.test.tsx、apps/web/app/components/ResearchPages.tsx、AGENT2_PHASE14R_RESULTS.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、persistent/DESIGN_PROGRESS.md
修改摘要：修复 query-only ResearchTurn 无下游消费者时遗留 ORCHESTRATING 的后端终态契约；清理并重载当前同栈 Turn worker；前端声明 ANSWERED、显示数据查询完成并在 Turn 路由变化时清理旧 planning 状态。
测试结果：真实 Chrome fresh Turn `ddad0068-144e-4377-abe3-44a0e2601592` 为 `ANSWERED`，事件 `dispatch_status=COMPLETED`，无 Plan/Job/ToolCall/Artifact/ScientificResult；前端定向 `46 passed`；浏览器 fatal/unhandled/critical = 0；PostgreSQL/Redis/MinIO 与 Chrome 标签页保持开启。
提交/CI 状态：未提交；P14R-A/P14R-B 未创建，能力全覆盖、生命周期治理、恢复/运维、真实用户验收等强制门禁仍未闭合。
任务名称：Phase 14-R 批量产品连续性验证（报告生命周期、搜索、任务通知）
状态：已完成（批量资格验证；总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：AGENT2_PHASE14R_RESULTS.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、persistent/DESIGN_PROGRESS.md
修改摘要：在同一已认证 Chrome 标签页中成组验证 Report ACTIVE→ARCHIVED→ACTIVE、
受保护依赖预览与取消、全局 `mat-2` 搜索、任务中心与通知中心持久化入口；
保持科学 Result、Dataset exact object/version 与服务运行不变。
测试结果：报告/生命周期定向 39 passed、4 historical compatibility skips；
同栈 PostgreSQL/Redis/MinIO 子集 11 passed、0 skipped；报告归档/恢复后
精确 Dataset version 与 Result snapshot 均保持一致。
提交/CI 状态：未提交；服务与 Chrome 标签页保持开启；P14R-A/P14R-B 未创建，
因为能力全覆盖、恢复/保留治理、真实用户总验收与 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R 批量 Report 生命周期控制补齐
状态：已完成（受限批量归档/恢复与真实浏览器验证；总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：apps/web/app/components/ScientificReportsIndexPage.tsx、
apps/web/app/components/ScientificReportsIndexPage.test.tsx、
AGENT2_PHASE14R_RESULTS.md、persistent/DESIGN_PROGRESS.md
修改摘要：在现有服务端生命周期 API 之上增加 ACTIVE/ARCHIVED 报告的受限
多选归档/恢复；保留逐报告 Trash 依赖影响预览，不提供批量 Trash，避免绕过
保护性确认。真实已认证 Chrome 标签页完成目标报告 ACTIVE→ARCHIVED→ACTIVE，
归档筛选中可见，归档正文显示状态说明并提供精确 ResearchTurn 来源研究入口；
Dataset exact object/version 与 Result snapshot 未变化。
测试结果：报告/生命周期/任务/通知/产品壳定向前端 37 passed；同栈
PostgreSQL/Redis/MinIO 子集 11 passed、0 failed、0 errors、0 skipped；
未观察到科学重算或授权失败。
提交/CI 状态：未提交；P14R-A/P14R-B 未创建；服务与 Chrome 标签页保持开启，
能力全覆盖、保留/导出治理、恢复运维、真实用户验收与 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R Report Evidence 移动溢出与当前流畅度基线
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/globals.css、.phase14r-performance-current.cjs、
docs/agent2/phase14r/PERFORMANCE_PRODUCT_FLUENCY_BASELINE.md、
AGENT2_PHASE14R_RESULTS.md、persistent/DESIGN_PROGRESS.md、results.md
修改摘要：修复 Report Evidence 长 UUID/Result/Version 标识导致的 390px
移动端 30px 瞬态溢出，改为 Evidence grid item 可收缩且长标识可断行；
性能测量器增加 250ms render-settle 窗口，避免将异步内容瞬态误报为最终布局。
测试结果：同栈 Chromium 当前冷/热矩阵 Data、Research、Viewer、Report、
Tasks、Notifications 桌面及 Data/Research/Report 移动全部 `maxOverflow=0`；
Report mobile warm p50/p95 `867/887ms`，Research `1224/1272ms`，Data
`1077/1141ms`；所有路由无 page error、无关键 5xx。
提交/CI 状态：未提交；API、workers、PostgreSQL、Redis、MinIO 与浏览器标签页
保持运行；P14R-A/P14R-B 未创建，能力全覆盖、治理、恢复与真实用户验收仍待闭合。

任务名称：Phase 14-R 任务筛选与 Research 操作层级质量
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/components/TaskCenterPage.tsx、
apps/web/app/components/TaskCenterPage.test.tsx、
apps/web/app/components/NotificationCenterPage.tsx、
apps/web/app/components/Agent2ScientificPresentation.tsx、
apps/web/app/globals.css、AGENT2_PHASE14R_RESULTS.md、
persistent/DESIGN_PROGRESS.md、results.md
修改摘要：任务中心改为单一任务单次出现的四项 tab 筛选（全部、进行中、
需要关注、已结束），避免同一失败任务在多个分组重复出现；任务和通知行的
“打开/打开研究”成为主操作，Job ID 仅在技术详情中渐进披露；完成研究页将
“继续研究”提升为唯一主操作，重算、重解释、编辑和固定上下文保持次级。
测试结果：Task/Notification/Research/Agent2 定向 47 passed；typecheck PASS；
真实同栈 Playwright 桌面验证结果页 1 个科学呈现、任务 17 条/四项筛选、
通知 7 条；390x844 五个 Research 操作均 390px 全宽、body.scrollWidth=390。
唯一 401 为登录前预期 `/auth/me` bootstrap，认证路径无页面错误或关键 4xx/5xx。
提交/CI 状态：未提交；API、workers、PostgreSQL、Redis、MinIO 与浏览器标签页
保持运行；P14R-A/P14R-B 未创建，能力全覆盖、生命周期/恢复/保留导出与
真实用户验收及 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R 任务与通知信息层级修复
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/components/TaskCenterPage.tsx、
apps/web/app/components/TaskCenterPage.test.tsx、
apps/web/app/components/NotificationCenterPage.tsx、
apps/web/app/components/NotificationCenterPage.test.tsx、
apps/web/app/globals.css、persistent/DESIGN_PROGRESS.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
AGENT2_PHASE14R_RESULTS.md、results.md
修改摘要：任务/通知列表不再把原始 Job ID 放在主标题，改为优先显示持久化
状态与用户可理解的工作类型；Job ID 保留在折叠“技术身份”中。未改变打开、
重试、停止、Workspace/ResearchTurn 路由或队列权威。
测试结果：Task/Notification/Research/Agent2/Report 五文件 55 passed；
frontend typecheck PASS；git diff --check PASS。
提交/CI 状态：未提交；服务与浏览器保持运行；P14R-A/P14R-B 未创建，能力族
实测、保留/导出、恢复运维和最终用户验收仍待闭合。

任务名称：Phase 14-R 报告批量工具条与来源透明度质量补齐
状态：已完成（UI 状态、失败回读、移动布局与精确来源入口；总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：apps/web/app/components/ScientificReportsIndexPage.tsx、
apps/web/app/components/ScientificReportsIndexPage.test.tsx、
apps/web/app/components/ScientificReportRoute.tsx、
apps/web/app/components/ScientificReportRoute.test.tsx、
apps/web/app/globals.css、AGENT2_PHASE14R_RESULTS.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、persistent/DESIGN_PROGRESS.md
修改摘要：批量报告工具条按生命周期状态提供归档/恢复动作；部分失败仅保留
失败项选中并给出可重试反馈；筛选切换清理旧选择；报告阅读页披露 ARCHIVED/TRASHED
状态并链接精确 ResearchTurn；补齐桌面/390px 行布局、边界、焦点和可达性。
测试结果：7 个相关前端测试文件共 40 passed；typecheck PASS；
API `/health/runtime` 仍为 PostgreSQL/Redis/MinIO/Redis worker 正常。
提交/CI 状态：未提交；P14R-A/P14R-B 未创建；服务与 Chrome 标签页保持开启，
能力全覆盖、保留/导出治理、恢复运维、真实用户验收与 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R 任务中心与通知中心状态控制面质量补齐
状态：已完成（语义状态徽标、操作可达性与移动布局；总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：apps/web/app/components/TaskCenterPage.tsx、
apps/web/app/components/TaskCenterPage.test.tsx、
apps/web/app/components/NotificationCenterPage.tsx、apps/web/app/globals.css、
AGENT2_PHASE14R_RESULTS.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
persistent/DESIGN_PROGRESS.md、results.md
修改摘要：为任务与通知行加入统一的排队/运行/成功/警告/失败/取消语义徽标，
保留准确 Job ID 和持久化研究入口；操作组增加状态语义 aria-label，移动端
扩展到整行以保证打开、重试和停止研究可触达；未引入新的执行或队列逻辑。
测试结果：5 个相关前端文件共 58 passed；apps/web typecheck PASS；
git diff --check 无空白错误（仅 CRLF 转换警告）。
提交/CI 状态：未提交；服务与 Chrome 标签页保持开启；P14R-A/P14R-B 未创建，
能力全覆盖、保留/导出治理、恢复运维、真实用户验收与 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R XRD 源恢复、Viewer 可恢复错误与移动数据上下文
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/api/mdi_api/routers/secured_runtime.py、
tests/test_project_access.py、apps/web/app/components/ProductPages.tsx、
apps/web/app/components/ProductPages.test.tsx、apps/web/app/globals.css、
docs/agent2/phase14r/SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
persistent/DESIGN_PROGRESS.md、results.md
修改摘要：为缺失 normalized source 增加
`SOURCE_RESOURCE_UNAVAILABLE`/409/可重试契约；Viewer 提供显式重试与来源属性
入口并隐藏原始基础设施错误；资源按钮改为单一清晰标签；移动端数据导航
默认折叠，保留明确展开控制。将仓库已有 normalized scientific objects
以非破坏方式恢复到正在使用的 `mdi-artifacts` MinIO bucket，未改变数据库科学
身份或版本记录。
测试结果：`tests/test_project_access.py` 18 passed；ProductPages/product-api
定向 29 passed；ProductPages/ScientificPresentation/Agent2 定向 33 passed；
frontend typecheck PASS；浏览器 XRD 桌面渲染 1 个系列/9 个数值与 Si 结构查看器
通过；390x844 `body.scrollWidth=388`、无横向溢出；浏览器 error/warn 日志为空。
提交/CI 状态：未提交；API、workers、PostgreSQL、Redis、MinIO 与浏览器标签页
保持运行；P14R-A/P14R-B 未创建，能力全覆盖、保留/导出治理、真实用户验收与
exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R ResearchTurn 单一权威呈现收敛
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/components/ResearchPages.tsx、
apps/web/app/components/ResearchPages.test.tsx、persistent/DESIGN_PROGRESS.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
AGENT2_PHASE14R_RESULTS.md、results.md
修改摘要：完成/部分完成的 Agent2 ResearchTurn 只显示 exact-turn
Scientific Presentation；不再同时渲染旧运行级呈现，也不再出现误导性的
“当前没有可展示的结果”。旧兼容运行和进行中执行仍保留原工作台。
测试结果：ResearchPages/Agent2ScientificPresentation/
ScientificPresentationBlocks 定向 46 passed；frontend typecheck PASS；
git diff --check PASS。
提交/CI 状态：未提交；服务与浏览器保持运行；P14R-A/P14R-B 未创建，其余
能力族实测、治理、恢复运维和最终用户验收仍待闭合。

任务名称：Phase 14-R Research Session 生命周期与只读历史布局
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/api/mdi_api/db.py、apps/api/alembic/versions/0027_research_session_management.py、
apps/api/mdi_api/routers/research.py、apps/api/mdi_api/routers/secured_runtime.py、
apps/web/app/lib/product-api.ts、apps/web/app/components/ResearchPages.tsx、
apps/web/app/components/ObjectManagement.tsx、apps/web/app/globals.css、
tests/test_project_access.py、apps/web/app/components/ResearchPages.test.tsx、
docs/13_SHARED_SCHEMA_SPEC.md、docs/agent2/phase14r/USER_LIFECYCLE_MANAGEMENT_CONTRACT.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md、
persistent/DESIGN_PROGRESS.md、AGENT2_PHASE14R_RESULTS.md、results.md
修改摘要：在既有 sessions/status 权威上增加非科学的 title override、
pin 与 pre-trash 状态；完成当前/归档/回收站三态记录管理、服务器端写入
保护与会话恢复。Research 时间线标题区显示当前会话和生命周期，恢复动作
紧邻记录入口；归档/回收会话的 composer 改为明确只读提示，重试操作在恢复
前隐藏，历史科学内容仍可读且不触碰 Turn/Result/版本权威。UI 采用现有
overflow/action 系统，移动端保留 44px 触控目标与单一工作区层级。
测试结果：backend `tests/test_project_access.py` 19 passed；frontend
`ResearchPages.test.tsx` 40 passed；frontend typecheck PASS；touched Ruff PASS；
git diff --check PASS；已有真实同栈研究管理浏览器证据桌面/390x844 均无溢出、
无 console/critical 错误。
提交/CI 状态：未提交；PostgreSQL/Redis/MinIO/API/workers 与现有 Chrome
标签页保持运行；P14R-A/P14R-B 未创建，能力全覆盖、保留/恢复运维和最终
用户验收仍待闭合。

任务名称：Phase 14-R 报告索引语言层级统一
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/components/ScientificReportsIndexPage.tsx、
apps/web/app/components/ScientificReportsIndexPage.test.tsx、persistent/DESIGN_PROGRESS.md、
results.md
修改摘要：将报告页 `Project Reports`、`Grounded Reports`、`Legacy Reports`
分区 kicker 统一为“项目报告”“已验证结果”“历史运行”，保持既有状态筛选、
批量生命周期和来源引用不变，避免中英文标签混杂造成层级误读。
测试结果：ScientificReportsIndexPage/ProductPages/ScientificPresentation/
Agent2/product-api 定向共 41 passed；frontend typecheck PASS；浏览器报告页
三种中文层级均可见，桌面 `scrollWidth=1265` / viewport `1280`，无错误日志。
提交/CI 状态：未提交；服务与浏览器标签页保持运行；P14R-A/P14R-B 未创建，
能力全覆盖、保留/导出治理、恢复运维、真实用户验收与 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R 全局搜索键盘入口与结果层级质量
状态：已完成（R7 交互与可达性补齐；总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：apps/web/app/components/ProductShell.tsx、
apps/web/app/components/ProductShell.test.tsx、apps/web/app/globals.css、
AGENT2_PHASE14R_RESULTS.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
persistent/DESIGN_PROGRESS.md、results.md
修改摘要：为已有授权全局搜索增加 Ctrl/⌘ K 入口、清除按钮、结果数量
aria-live 状态、类型/生命周期徽标和移动端友好的输入布局；未改变搜索 API
授权或科学身份权威。
测试结果：ProductShell 7 passed；8 个相关前端文件合计 79 passed；typecheck PASS；服务与
Chrome 标签页保持开启。
提交/CI 状态：未提交；P14R-A/P14R-B 未创建；能力全覆盖、保留/导出治理、
恢复运维、真实用户验收与 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R Research 结果控制层级与异步状态提示
状态：已完成（控制区分组、语义说明、移动布局；总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：apps/web/app/components/Agent2ScientificPresentation.tsx、
apps/web/app/globals.css、AGENT2_PHASE14R_RESULTS.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、persistent/DESIGN_PROGRESS.md、results.md
修改摘要：将编辑、继续、重跑、仅重新解释、固定上下文五类操作放入明确的
“继续这项研究”区域；提交中通过 aria-live 状态说明科学 Result 不会被覆盖；
按宽屏/平板/手机分别采用五列、两列、单列布局。
测试结果：Research/presentation/execution 定向 52 passed；apps/web
全量此前 96 files / 638 passed；typecheck PASS；服务同栈健康。
提交/CI 状态：未提交；服务与 Chrome 标签页保持开启；P14R-A/P14R-B 未创建，
能力全覆盖、保留/导出治理、恢复运维、真实用户验收与 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R 运行时与旧任务分组一致性修复
状态：已完成（同栈服务恢复、MinIO 初始化修复、历史任务不再计入活跃数；总体仍为 PARTIAL）
完成时间：2026-08-29
修改文件：apps/web/app/components/TaskCenterPage.tsx、
apps/web/app/components/TaskCenterPage.test.tsx、AGENT2_PHASE14R_RESULTS.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、persistent/DESIGN_PROGRESS.md、results.md
修改摘要：证明 MinIO 未初始化是带空格工作区路径被 Windows Start-Process 拆成多 volume，
改用显式引号的单 volume 重新启动并创建 mdi-artifacts bucket；任务中心将
LEGACY_READ_ONLY 旧兼容记录归入历史，不再将其错误统计为进行中。
测试结果：Task/Notification 2 passed；Context Manifest/operations backend 9 passed；
前端全量 96 files / 638 passed；typecheck PASS；API `/health/runtime` 报告
PostgreSQL/Redis/MinIO/Redis worker 正常。
提交/CI 状态：未提交；服务与 Chrome 标签页保持开启；P14R-A/P14R-B 未创建，
能力全覆盖、保留/导出治理、恢复运维、真实用户验收与 exact-SHA 门禁仍未闭合。

任务名称：Phase 14-R 上下文透明度与全局科学搜索层级
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/api/mdi_api/routers/secured_runtime.py、
apps/web/app/components/ProductShell.tsx、
apps/web/app/components/ProductShell.test.tsx、
apps/web/app/components/ResearchPages.tsx、
apps/web/app/components/ResearchPages.test.tsx、
apps/web/app/lib/agent2-research-api.ts、apps/web/app/globals.css、
tests/test_project_access.py、AGENT2_PHASE14R_RESULTS.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md、
persistent/DESIGN_PROGRESS.md、results.md
修改摘要：把 ContextManifest 从内部枚举/ID 主导的展示改为研究者优先的
“纳入原因—权威类别—精确版本”两层披露；全局搜索使用人类可读的首条用户问题
作为研究会话标题，中文化 Result/生命周期标签，并将打开结果设为单一主动作。
真实 Session/Turn/Version 身份、授权和科学权威均未改变。
测试结果：后端 Project/search 19 passed；前端 ProductShell/Research/
Task/Notification/Report 5 files / 59 passed；typecheck PASS；touched
git diff --check PASS。真实同栈浏览器 canonical Turn 保留 exact version
809a6825-5bfe-4820-81fc-b589ba447abc；`mat-2` 搜索返回 6 个授权结果、
0 个内部 Session-ID 标题；1280x720 与 390x844 均无溢出或浏览器错误。
提交/CI 状态：未提交；API 已在同一 PostgreSQL/Redis/MinIO/worker 栈快速
恢复，frontend 与现有 Chrome 标签页未关闭；P14R-A/P14R-B 未创建，完整
科学 Surface、保留/运维、真实用户验收和 exact-SHA 门禁仍待闭合。

任务名称：Phase 14-R Report 操作层级与依赖确认布局
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/components/ScientificReportsIndexPage.tsx、
apps/web/app/components/ScientificReportsIndexPage.test.tsx、
apps/web/app/components/ObjectManagement.tsx、apps/web/app/globals.css、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md、
persistent/DESIGN_PROGRESS.md、AGENT2_PHASE14R_RESULTS.md、results.md
修改摘要：默认报告行只保留报告打开主路径与就近溢出菜单；批量复选框仅在
显式“批量管理”模式出现；Archive/Restore 可批量执行，Trash 继续要求逐份
服务端依赖预览与确认。依赖影响改用可聚焦、Escape 关闭并恢复焦点的共享
ProductModal。同名报告的真实浏览器验收使用 reportId 而非标题作为身份。
测试结果：ScientificReportsIndexPage 8 passed；相关前端 6 files / 68 tests；
typecheck、touched Ruff、git diff --check PASS；同栈 Chromium 完成精确 Report
Archive/Restore 与六项依赖预览，390x844 无水平溢出或关键 API 失败。
提交/CI 状态：未提交；服务和既有 Chrome 标签页保持开启；P14R-A/P14R-B
未创建，能力全覆盖、保留/恢复/运维、真实用户验收和 exact-SHA 门禁仍待闭合。

任务名称：Phase 14-R App Router 导航流畅度与过渡反馈
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/lib/product-api.ts、apps/web/app/components/ProductShell.tsx、
apps/web/app/components/RouteLoading.tsx、apps/web/app/projects/[projectId]/loading.tsx、
apps/web/app/projects/[projectId]/data/loading.tsx、apps/web/app/projects/[projectId]/research/loading.tsx、
apps/web/app/projects/[projectId]/reports/loading.tsx、apps/web/app/tasks/loading.tsx、
apps/web/app/notifications/loading.tsx、apps/web/app/globals.css、
docs/agent2/phase14r/PERFORMANCE_PRODUCT_FLUENCY_BASELINE.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md、
persistent/DESIGN_PROGRESS.md、AGENT2_PHASE14R_RESULTS.md、results.md
修改摘要：实证点击导航并非 full reload（documentRequests=0、window marker 保留），
真正问题是重复认证请求和过渡空白。新增浏览器会话 auth 请求合并缓存、项目导航
pointer/focus 预取、项目/数据/研究/报告/任务/通知原生 loading 边界，保持全局
工作台层级并显示真实过渡状态。
测试结果：ProductShell/Task/Notification 11 passed；导航同栈 Chromium cold/warm
可用时间分别为 Data 481/131ms、Research 991/967ms、Reports 1659/95ms、
Overview 952/922ms；所有转换 documentRequests=0、post-login authRequests=0、
critical=0；typecheck、git diff --check PASS。
提交/CI 状态：未提交；PostgreSQL/Redis/MinIO/API/worker/frontend 和既有 Chrome
标签页保持开启；P14R-A/P14R-B 未创建，完整成熟产品门禁仍待闭合。

任务名称：Phase 14-R 报告质量与移动端科学阅读收口
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/components/ScientificReportRoute.tsx、
apps/web/app/lib/scientific-report-api.ts、apps/web/app/components/ScientificReportRoute.test.tsx、
apps/web/app/globals.css、apps/api/mdi_api/scientific_reports/prompts/scientific_report_composer_v2.txt、
docs/agent2/phase14r/SCIENTIFIC_REPORT_QUALITY_RUBRIC.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md、
AGENT2_PHASE14R_RESULTS.md、results.md
修改摘要：Structure 与 Dataset 两份真实 Report 通过同栈浏览器验证；展示方法
名称改为研究者可读文本，保留技术身份在审计层；长 fact 引用在移动端可换行，
报告页 `390/390` 无水平溢出。
测试结果：ScientificReportRoute 11 passed；Structure report `agent2_report_401cfb421fcab8a9366e06fedb3acb6d`
与 Dataset report `agent2_report_c91972312383616a6503acd6be76e233` 的精确版本、
发现、限制、讨论、结论均可见；无 raw capability ID/JSON，科学计数无新增。
提交/CI 状态：未提交；服务与 Chrome 标签页保持开启；P14R-A/P14R-B 未创建，
capability-wide surface、retention、operations 与真实用户验收仍待闭合。

任务名称：Phase 14-R Report/Context/授权后端回归
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：AGENT2_PHASE14R_RESULTS.md、persistent/DESIGN_PROGRESS.md、results.md
修改摘要：在导航持久布局、Report 质量与移动端修复后，重新执行 Report grounding、
ContextManifest、项目授权后端回归；确认 PostgreSQL 实例 Alembic head 为 0027。
测试结果：45 passed / 4 历史兼容 skip；`DATABASE_URL` 指向 127.0.0.1:55434 时
`alembic current = 0027_research_session_management (head)`；runtime PostgreSQL/
Redis/MinIO/worker 全部 OK。
提交/CI 状态：未提交；服务和 Chrome 标签页保持开启；P14R-A/P14R-B 未创建，
能力全覆盖、生命周期/保留、运维和真实用户验收仍待闭合。

任务名称：Phase 14-R 多族群 Report 质量、可读方法名与移动端收缩
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/api/mdi_api/scientific_reports/prompts/scientific_report_composer_v2.txt、
apps/web/app/lib/scientific-report-api.ts、apps/web/app/components/ScientificReportRoute.tsx、
apps/web/app/components/ScientificReportRoute.test.tsx、apps/web/app/globals.css、
docs/agent2/phase14r/SCIENTIFIC_REPORT_QUALITY_RUBRIC.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md、
AGENT2_PHASE14R_RESULTS.md、results.md
修改摘要：通过真实 Report worker 以既有 Structure Result 生成 VALID 报告；
方法段将 capability ID 映射为研究者可读名称，质量量表只允许经权威缺失检查
后使用 N/A。修复报告主要发现长 fact 标识导致的 390px 横向扩张。
测试结果：Report route 11 passed；Structure report `agent2_report_401cfb421fcab8a9366e06fedb3acb6d`
与 Dataset report `agent2_report_c91972312383616a6503acd6be76e233` 浏览器通过，
精确版本/发现/限制/讨论/结论保留，390/390 无溢出；科学计数无新增 Job、ToolCall、
Artifact、Result。
提交/CI 状态：未提交；报告 worker、PostgreSQL/Redis/MinIO/API/frontend 和 Chrome
标签页保持开启；P14R-A/P14R-B 未创建，能力全覆盖与成熟产品 release gates 仍待闭合。

任务名称：Phase 14-R 导航持久布局生产构建与全量前端回归
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/components/ProductShell.tsx、apps/web/app/components/ProductRouteFrame.tsx、
apps/web/app/projects/layout.tsx、apps/web/app/components/RouteTransitionProgress.tsx、
apps/web/app/components/RouteTransitionProgress.test.tsx、apps/web/app/components/RouteLoading.tsx、
apps/web/app/globals.css、apps/web/app/layout.tsx、apps/web/app/lib/product-api.ts、
相关 loading.tsx 与 docs/persistent/results 台账
修改摘要：项目路由使用持久 ProductRouteFrame，页面壳复用同一全局 DOM；
query-aware 过渡进度组件置于 Suspense；认证请求缓存对 401/登出清除；
修复报告移动长 fact 引用横向扩张，并保留原生 loading 层级。
测试结果：前端全量 `97 files / 649 tests passed`；typecheck PASS；
production build PASS（17 routes）；同栈点击导航 documentRequests=0、shellCount=1、
window marker 与 shell marker 均保留、post-login authRequests=0；390px Report
document/body=390/390，critical=0。
提交/CI 状态：未提交；PostgreSQL/Redis/MinIO/API/worker/frontend 和 Chrome 标签页
保持开启；P14R-A/P14R-B 未创建，真实用户验收、能力全覆盖、保留治理与 exact-SHA
门禁仍待闭合。

任务名称：Phase 14-R Structure Presentation/Evidence/Viewer 连续性
状态：已完成（canonical path；总体仍为 PARTIAL）
完成时间：2026-08-30
修改文件：apps/web/app/components/scientific-viewer/ScientificViewerShell.tsx、
apps/web/app/components/scientific-viewer/ScientificObjectViewer.tsx、
apps/web/app/components/scientific-viewer/ScientificViewerShell.test.tsx、
apps/web/app/globals.css、docs/agent2/phase14r/SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md、
persistent/DESIGN_PROGRESS.md、AGENT2_PHASE14R_RESULTS.md、results.md
修改摘要：Structure Research 的单一 Presentation、两项 Evidence、精确 Viewer
handoff 完成同栈验收；Viewer 底部新增可展开完整 UUID 的“精确版本”披露，
头部继续保持简洁版本号。
测试结果：Viewer/Presentation 3 files / 6 tests；typecheck、diff-check PASS；
真实 Turn `17b67e68-b7db-475b-bb4c-3b336cb2ba15`、object
`dc3c3eee-f254-4edf-a0fa-c955402b3069`、version
`8859cb49-0766-48cd-8a56-e44f5332e0c5` 浏览器通过；0 scientific mutation，
390/390 无溢出。
提交/CI 状态：未提交；服务与 Chrome 标签页保持开启；未验收 capability families
仍保持 NOT_QUALIFIED，P14R-A/P14R-B 未创建。

任务名称：Phase 14-R 当前工作树回归与 Report/Viewer 只读验证批次
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-31
修改文件：AGENT2_PHASE14R_RESULTS.md、docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
persistent/DESIGN_PROGRESS.md、apps/web/tsconfig.json（仅移除生产构建自动生成的临时 include）
修改摘要：完成真实同栈健康复核、Report → Research → Viewer 导航与零科学重算证据记录；
确认前端原生 App Router 导航、桌面无全局溢出和报告精确来源路由；保留运维快照中
历史 stale Turn/Job 的真实 attention 状态，不将其伪装为成熟度 PASS。
测试结果：前端全量 `101 files / 693 tests passed`；后端关键回归 `47 passed / 4 historical
skips`；production build `17 routes`、typecheck、compileall、uv lock --check、Ruff、
git diff --check 全部通过；同栈 `/health/runtime` 为 PostgreSQL/Redis/MinIO/6 workers，
idle-in-transaction=0，queued=0，recentFailed=0；operations snapshot 暴露
staleActiveResearchTurns=13、staleJobs=1；mandatory PostgreSQL/Redis/MinIO
selection `21 passed / 0 failed / 0 errors / 0 skipped`；完整后端
`1892 passed / 83 historical or optional skips`。
提交/CI 状态：未提交；服务与 Chrome 标签页保持开启；Phase 14-R 仍为 PARTIAL，
P14R-A/P14R-B 未创建。

任务名称：Phase 14-R Phonon/Electronic presentation readability batch
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-31
修改文件：apps/web/app/components/ScientificReportRoute.tsx、
apps/web/app/components/ScientificReportRoute.test.tsx、
apps/web/app/components/ResearchPages.tsx、
apps/web/app/components/ResearchPages.test.tsx、
docs/agent2/phase14r/SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md、
docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md、
persistent/DESIGN_PROGRESS.md、AGENT2_PHASE14R_RESULTS.md
修改摘要：Report 限制文案复用 Research 的确定性产品语言；Research 时间线
对持久化 ASSISTANT_FINAL 采用有界摘要，避免 raw fact/evidence ID 与重复
机器段落占用主阅读区；真实 Phonon/Electronic Viewer 显示科学内容并保持
exact version 与零重算。
测试结果：前端 Report/Presentation `31/31`；ResearchPages `54/54`；
390x844 Viewer 无横向溢出；浏览器错误/未处理异常为 0；PostgreSQL
计数 `258/339/1359/181/33` 在只读导航前后不变。
提交/CI 状态：未提交；服务与 Chrome 标签页保持开启；Phase 14-R 仍为
PARTIAL，P14R-A/P14R-B 未创建。

补充 UI 质量验证：真实 Phonon Report 的旧持久化 discussion 曾显示 `。；`；
deterministic composer 已改为完整句连接，Report reader 对旧快照仅做展示标点
归一化。后端 Report `30 passed / 4 historical skips`、前端 Report route
`14/14`；浏览器可见讨论现在为正常分号连接，科学数据未重算。

任务名称：Phase 14-R Project History 状态、客户端导航与移动 UI 批次
状态：已完成（受限批次；总体仍为 PARTIAL）
完成时间：2026-08-31
修改文件：apps/web/app/lib/research-display.ts、
apps/web/app/components/ProductPages.tsx、
apps/web/app/components/ProductPages.test.tsx、
apps/web/app/components/ProjectHome.tsx、
apps/web/app/components/ProjectHome.test.tsx、apps/web/app/globals.css、
.phase14r-performance-current.cjs、Phase 14-R docs/persistent/results 台账。
修改摘要：Project Overview/Project Home 以权威 ResearchTurn 终态覆盖陈旧
Job 展示状态并强制读取当前 History；移动项目导航隐藏原生滚动条；性能脚本
同步当前 Task/Notification section 根语义。
测试结果：前端 focused `38/38`、typecheck、diff-check PASS；真实浏览器
Turn `ec298988-0b32-4e5e-a3c0-8bbb22725818` 显示“分析失败”并携带精确
session/run/Turn。App Router 四路由 documentRequests=0、shell preserved；
桌面/移动完整矩阵 overflow/browser errors/critical 5xx 均为 0。
提交/CI 状态：未提交；同栈服务与浏览器保持开启；Phase 14-R 总体仍为
PARTIAL，P14R-A/P14R-B 未创建。
# Agent-2.0 Phase 14-R — 2026-08-31 Report provenance + navigation fluency batch

状态：已完成（批次）

修改摘要：
- Scientific Report view 为 Figure source 增加按 `figure_type` 推导的精确
  object/version 绑定；前端 Report Presentation 优先使用该绑定。
- ProductShell 对项目历史、研究会话、任务中心的 hover/focus 预取做幂等合并，
  保持 App Router 壳层、避免重复权威读取。
- 更新 Phase 14-R 科学 surface/audit 与设计进度证据。

测试结果：
- `tests/test_agent2_phase8_reports.py`: 32 passed, 4 historical compatibility skips
- `apps/web`: ProductShell + ScientificReportRoute + scientific-presentation:
  41 passed
- live API `/health/runtime`: PostgreSQL + Redis + MinIO + Redis workers + configured DeepSeek
- live report browser: Band exact version `7f7f1008…`, DOS exact version
  `087f93c4…`, mobile overflow 0
- live navigation: document reloads 0, RSC request 1/route, shell count 1

提交/CI 状态：未提交；等待 Phase 14-R 全部强制门后统一创建 P14R-A/P14R-B。

# Agent-2.0 Phase 14-R — 2026-08-31 trajectory RDF qualification batch

状态：已完成（批次）

证据：
- ResearchTurn `321db606-efeb-41af-9333-3709fa07e9ee`
- ScientificResultSnapshot `ae56aeb8-27ec-47c3-b0cc-254c4636c205`
- Report `agent2_report_55692c117165c20c3da272ef75e28118`
- exact trajectory version `052d3a8e-8a35-48ac-9e65-b95a86b42c99`

结果：真实同栈浏览器生成并打开 RDF Report，展示 5 项有界发现、持久化 Figure、
2 项证据引用、精确 Viewer 来源及 RDF 限制；移动端 overflow=0。
`trajectory.rdf` 从 `NOT_QUALIFIED` 升级为 `PASS`；`trajectory.msd` 和
`trajectory.diffusion` 保持真实的 `NOT_QUALIFIED`。

提交/CI 状态：未提交；Phase 14-R 仍未封板。

# Agent-2.0 Phase 14-R — 2026-08-31 trajectory MSD real-source batch

状态：已完成（受限批次；总体仍为 PARTIAL）

修改摘要：
- 新增带 Å 与 Å/fs 单位、显式 `unwrapped` 语义的真实 EXTXYZ 接受源，并通过
  正常上传、MinIO、parser 与 Profile 路径建立 Dataset
  `dataset_0001_b7f22cb1bb074f1a`。
- 完成 Plan `plan_72e81c4f236b4510b8d23450`、Job
  `job_f2b56ba7d4a34c9288600852`、4 个持久化 Artifact 与 grounding
  `VALID` 的 Interpretation
  `interpretation_fed32da21ee465e9e18d19048d559e93`。
- 科学输出为 3 个 lag、末端 `0.0009 Å² @ 0.003 ps`，明确不估算扩散系数。
- 修复 Dataset object-store 将规范化轨迹 dataclass 错投影为字符串的问题；
  Viewer 现显示 4 个真实帧及 unwrapped/time/lattice/交互控件。
- 修复 MSD-only Presentation 无条件拼接 RDF 帧数、产生 `NaN` 文案的问题。
- Report → Research → Report 只读复开前后科学状态计数保持
  `261/341/1363/17/36`。

测试结果：
- capability planner `64 passed`
- trajectory parser `24 passed`
- backend object-store/parser `27 passed`
- frontend Research + Trajectory Viewer `70 passed`
- typecheck、diff-check PASS

提交/CI 状态：未提交；`trajectory.msd` 升级为 `PARTIAL`，Agent2
ResearchTurn/ScientificResultSnapshot、移动/历史 MSD、diffusion、其余成熟产品
门以及 P14R-A/P14R-B 仍未闭合。

# Agent-2.0 Phase 14-R — 2026-08-31 trajectory diffusion and production navigation

状态：已完成（受限批次；Phase 14-R 总体仍为 PARTIAL）

修改摘要：
- 对真实 Job `job_dc63f3f5d57742009c6be09e` 完成零科学重算的严格解释，
  新 Interpretation `interpretation_a115c2ced38a7586161370b7994fec88`
  投影 `1–6 ps`、11 个拟合点、`R²=0.970301847945`、
  `α=0.924032310013` 和 `D=0.038618084156 Å²/ps`。
- 修复 Plot/摘要/Recipe 伴生 Artifact 被误算为“缺少科学证据投影器”的问题；
  未知、大文件或真正不可投影的科学来源仍 fail-closed。
- Research 与 legacy Report 改为读取最新不可变解释快照；轨迹诊断 Viewer
  统一中文科研语言、选择语义和移动端布局。
- 独立生产构建 `3002 → API 8002 → PostgreSQL/Redis/MinIO` 通过，
  八次项目导航 `documentRequests=0` 且 ProductShell 节点保持不变。

验证结果：
- 数据库差分：
  `jobs/tool_calls/artifacts/scientific_result_snapshots/interpretations =
  1/2/8/0/1 → 1/2/8/0/2`。
- 后端 focused：`26 passed`；前端 focused：`65 passed`。
- Ruff、typecheck、production build：PASS。
- 390×844：`scrollWidth=clientWidth=390`；认证后 console/page/API/critical
  failure 均为 0。
- 生产热导航 URL `33–93 ms`；可用时间 Data `97 ms`、Research `866 ms`、
  Reports `59 ms`、Overview `872 ms`。

提交/CI 状态：未提交；`trajectory.diffusion` 从 `NOT_QUALIFIED` 升级为
`PARTIAL`。缺少 Agent2 ScientificResultSnapshot、历史/归档 exact-version
验收以及其余 R1–R12 门，因此未创建 P14R-A/P14R-B。

任务名称：Agent-2.0 Phase 14-R — Report 语言与移动导航批次
状态：已完成（批次）
完成时间：2026-08-31
修改摘要：统一 Scientific Report/Presentation 的中文产品文案，保留精确
版本与科学 provenance；修复 Report 移动端顶部操作栏换行布局。
测试结果：ScientificReportRoute/ScientificPresentation/scientific-presentation
focused `37 passed`；web typecheck PASS；Report 打开前后
Jobs/ToolCalls/Artifacts/Results `278/365/1450/184` 无变化。
提交/CI 状态：未提交；Phase 14-R 总体仍 PARTIAL，等待 P14R-A/P14R-B。

任务名称：Agent-2.0 Phase 14-R — Global Search 同栈浏览器批次
状态：已完成（批次）
完成时间：2026-08-31
修改摘要：从真实认证研究页验证全局搜索入口、`mat-2` 查询、授权结果与精确
实体链接；未触发科学执行或跨项目泄露。
测试结果：当前 API/PostgreSQL 返回 7 项授权结果；既有 390px 搜索弹层证据
保持无全局横向溢出。
提交/CI 状态：未提交；Phase 14-R 总体仍 PARTIAL，等待 P14R-A/P14R-B。

任务名称：Agent-2.0 Phase 14-R — 精确 Result 复用浏览器批次
状态：已完成（批次）
完成时间：2026-08-31
修改摘要：用 Report → 来源研究 → 重新解释真实产品路径验证精确 Result
复用；保留父 Turn、对象/版本与 sample identity，只生成 INTERPRET_RESULT
子 Turn 和新 Interpretation。
测试结果：child Turn `219e8d7f-1c62-4566-a05b-e9563efce407` COMPLETED；
Interpretations `188→189`；Jobs/ToolCalls/Artifacts/ScientificResults
`278/365/1450/184` 无变化。
提交/CI 状态：未提交；Phase 14-R 总体仍 PARTIAL，等待 P14R-A/P14R-B。
## Agent-2.0 Phase 14-R — same-stack service availability recheck

- 状态：已完成（运行时连续性证据；Phase 14-R 总体仍为 PARTIAL）
- 完成时间：2026-08-31T21:44:41+08:00
- 修改文件：`AGENT2_PHASE14R_RESULTS.md`、`docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、`persistent/DESIGN_PROGRESS.md`
- 修改摘要：确认现有 frontend/API/PostgreSQL/Redis/MinIO 与 Redis-backed workers 持续运行；认证浏览器 tab 15 保持打开；Report → Data 客户端路由切换正常。
- 测试结果：`/health/runtime` HTTP 200，真实 backend 为 PostgreSQL/Redis/MinIO；端口与健康探针均通过。
- 提交/CI 状态：未提交；P14R-A/P14R-B 仍等待成熟产品强制门闭合。
任务名称：Agent-2.0 Phase 14-R — archive/restore UI + navigation fluency batch
状态：已完成
完成时间：2026-08-31T22:05:00+08:00
修改文件：`apps/web/app/components/ProductNavigation.tsx`、
`apps/web/app/components/ProductShell.tsx`、Phase 14-R 结果/审计/设计记录。
修改摘要：产品内链在未显式指定时自动启用同源 Next 预取；ProductShell 在
过渡期间保留并标记主工作区；认证浏览器真实完成
`55648f55-51e4-4c94-b4fe-72cae944a54c` 的归档→恢复，精确版本
`53037b6a-7a68-43ac-85de-6e920dfd4420` 保持不变。
测试结果：ProductShell/ProductPages/RouteTransition focused `46 passed`；
`npm run typecheck` PASS；浏览器 Data → Research 约 `2234 ms`，无认证恢复态、
卡住过渡或错误页。
提交/CI 状态：未提交；Phase 14-R 仍为 `PARTIAL`，服务和浏览器保持运行。

补充测试结果：全前端 `102 test files / 718 passed`；ProductPages/
ScientificReportsIndex/RouteTransition focused `45 passed`；Phase 14-R 后端
`65 passed / 4 historical compatibility skips`；typecheck、compileall、
`uv lock --check`、`git diff --check` PASS。未提交，未停止服务或浏览器。
独立 `.next-prod-phase14r-batch` 生产构建包含 `17` 个路由并通过。
项目壳还在空闲预取窗口预热 Research session inventory，复用现有 TTL 与
失效逻辑；focused ProductShell/RouteTransition `15 passed`，typecheck PASS。
预热后认证浏览器 Data → Research 复测约 `1314 ms`，无登录恢复态、切换残留或
水平溢出；服务与浏览器保持运行。
后端全量 `1916 passed / 84 skipped / 168 warnings`（`279.60s`）；前端全量
`718 passed`；生产构建、typecheck、compileall、lock、diff check PASS。

任务名称：Agent-2.0 Phase 14-R — composition-space / regression product batch
状态：已完成（批次）
完成时间：2026-08-31T22:50:00+08:00
修改文件：Phase 14-R scientific/mature coverage matrices、结果与设计进度记录。
修改摘要：真实认证同栈浏览器验证 composition-space Figure/Table、回归
Table、Evidence、exact Dataset Viewer、Report 和 390×844 移动端；稳定样本
`sample-fe2o3` 与精确版本 `cf2aeeea-53ad-452a-a4ef-7b61555004e5` 保持不变。
测试结果：前端 focused `34 passed`；浏览器错误/警告 0、移动端 overflow 0；
PostgreSQL 前后 `Jobs/ToolCalls/Artifacts/ScientificResults/Reports =
278/365/1450/184/36` 不变，`idle-in-transaction=0`。
提交/CI 状态：未提交；Phase 14-R 总体仍 PARTIAL，P14R-A/P14R-B 未创建。

任务名称：Agent-2.0 Phase 14-R — coordination-histogram product batch
状态：已完成（批次）
完成时间：2026-08-31T22:55:00+08:00
修改文件：Phase 14-R scientific/mature matrices、结果与设计进度记录。
修改摘要：真实认证浏览器验证配位 Figure/Table、Evidence、exact Structure
Viewer，并通过正常产品按钮生成可追溯 Report。
测试结果：Turn `63d21ee3-6e18-49b3-ad6b-b3fb578563c5`、Report
`agent2_report_19a0d0c261c28577101de81532464893`；仅 Report
`36→37`，Jobs/ToolCalls/Artifacts/Results 保持 `278/365/1450/184`；
390×844 无溢出、重复 ID 或浏览器错误；前端 focused `29 passed`。
提交/CI 状态：未提交；`structure.coordination_hist` PASS，Phase 14-R 总体
仍 PARTIAL。

任务名称：Agent-2.0 Phase 14-R — trajectory diffusion communication batch
状态：已完成（批次）
完成时间：2026-08-31T23:59:00+08:00
修改文件：`apps/api/mdi_api/scientific_reports/grounding.py`、
`tests/test_agent2_phase8_reports.py`、`apps/web/app/components/ResearchPages.tsx`、
`apps/web/app/components/ResearchPages.test.tsx`、Phase 14-R 结果/矩阵/
持久化记录。
修改摘要：真实认证同栈产品路径闭合 diffusion Presentation、Evidence、
24-frame Viewer 与 professional Report；修复 Report 对 `Å²/ps`、单位指数和
Evidence/ResultItem 支持图的 grounding 误判；当 Agent2 权威进度存在时隐藏
重复且错误的 legacy 0-step 摘要。
测试结果：后端 Result/Interpretation/Report `79 passed / 5 historical
skips`；Phase 8 Report service-backed `4 passed / 0 skipped`；前端相关
`96 passed`；Ruff/diff PASS；PostgreSQL/Redis/MinIO 正常、6 workers idle、
队列无积压、idle-in-transaction=0。Turn
`fb72c2ad-bed1-47d7-b557-f398f04a8ede`、Result
`26127c48-d736-4983-b035-b68db238f6a7`、Report
`agent2_report_e54681009a0e49abe371247d9053ce61`。
提交/CI 状态：未提交；Phase 14-R 总体仍 PARTIAL，服务与浏览器保持运行。

任务名称：Agent-2.0 Phase 14-R — grounding display-rounding repair and live retry
状态：已完成（批次；总体仍为 PARTIAL）
完成时间：2026-08-31T20:20:00+08:00
修改文件：`apps/api/mdi_api/interpretation/grounding.py`、
`tests/test_agent2_phase6_interpretation.py`、Phase 14-R 结果与持久化记录。
修改摘要：在不削弱单位、证据和引用校验的前提下，允许有界的权威数字展示
舍入；保留 unsupported quantitative claim 的 fail-closed 负向回归。仅重启
interpretation worker 加载当前代码，未关闭 PostgreSQL/Redis/MinIO/API/前端
或认证 Chrome 标签页。
测试结果：解释器 `26 passed / 1 historical skip`；Report+解释器
`60 passed / 5 historical skips`；Ruff、git diff check PASS。真实浏览器重试
Turn `b82c5758-fac8-4f30-b0ab-5df94dd68369`，Result snapshot
`8d506aa2-0247-4ea8-ae39-0c629ad3b991`，10 facts、2 ToolCalls、8 Artifacts，
`grounding_status=VALID`、Turn `COMPLETED`。同栈运维快照 PostgreSQL
`active=1/idle=12/idle-in-transaction=0`、Redis `6/0`、MinIO `ok`。
提交/CI 状态：未提交；P14R-A/P14R-B 未创建，Phase 14-R 仍 PARTIAL。

任务名称：Agent-2.0 Phase 14-R — archived diffusion continuity batch
状态：已完成（批次）
完成时间：2026-08-31T23:59:59+08:00
修改文件：`apps/api/mdi_api/scientific_reports/service.py`、
`tests/test_agent2_phase8_reports.py`、
`apps/web/app/lib/scientific-report-api.ts`、
`apps/web/app/components/ScientificReportRoute.tsx`、
`apps/web/app/components/ScientificReportRoute.test.tsx`、共享 schema、
Phase 14-R 结果/矩阵/持久化记录。
修改摘要：Report 精确来源从权威 ScientificObject 投影 lifecycle，独立于
current/historical version；归档状态同步进入 UI、Markdown 和非可执行复现清单。
真实产品路径在归档期间保持 exact Report/Result/4 Evidence/24-frame Viewer
可用，随后通过 UI 恢复 ACTIVE，未创建版本或科学执行状态。
测试结果：对象 `f834e358-9944-4fe8-a3ab-f85d68041f54`、版本
`a22745f2-17b6-434f-ba4c-3fe6bd244841`、Result
`26127c48-d736-4983-b035-b68db238f6a7`、Report
`agent2_report_e54681009a0e49abe371247d9053ce61`；科学计数
`285/377/1493/191` 零增量；后端 `33 passed / 4 historical skips`，前端
`33 passed`，Phase 8 service-backed `4 passed / 0 skipped`，typecheck、
Ruff、diff PASS；PostgreSQL active 1/idle 9/idle-in-transaction 0，
Redis 6 workers idle/queued 0，MinIO PASS，浏览器错误/警告 0。
提交/CI 状态：未提交；Phase 14-R 总体仍 PARTIAL，P14R-A/P14R-B 未创建，
服务与认证浏览器保持运行。

任务名称：Agent-2.0 Phase 14-R — Report tables / navigation / operations batch
状态：已完成（批次）
完成时间：2026-08-31T22:25:00+08:00
修改文件：`apps/api/mdi_api/scientific_reports/service.py`、
`apps/web/app/components/ScientificReportRoute.tsx`、
`apps/web/app/components/ResearchPages.test.tsx`、
`scripts/phase14r_operations_snapshot.py`、Phase 14-R 矩阵与持久化记录。
修改摘要：将权威 Result 表格以有界 `table_sources` 投影到 Report，保留
人类标题、Artifact 和精确对象/版本来源；保持 App Router 壳体、预取与
延迟 Viewer 的连续导航；修复运维快照脚本在清空 `PYTHONPATH` 时无法直接
启动的问题，并让延迟 Viewer 测试等待真实异步渲染。
测试结果：Phase 14-R 后端 `49 passed / 4 historical compatibility skips`；
前端 Report/Navigation/ProductShell/Research `99 passed`；运维脚本
`--help` PASS；服务仍为 PostgreSQL/Redis/MinIO，未关闭浏览器或服务。
提交/CI 状态：未提交；Phase 14-R 总体仍 `PARTIAL`，P14R-A/P14R-B 未创建。

补充修复：运维快照命令新增 `--same-stack` 显式资格拓扑选项，并保留空
`PYTHONPATH` 的独立导入能力。实测 `status=ok`，PostgreSQL
`active=1/idle=9/idleInTransaction=0`，Redis `workerCount=6/queued=0`，
MinIO `status=ok`；对应操作测试 `6 passed`。

任务名称：Agent-2.0 Phase 14-R — Research timeline duplicate replay repair
状态：已完成（批次）
完成时间：2026-08-31T22:40:00+08:00
修改文件：`apps/web/app/components/ResearchPages.tsx`、
`apps/web/app/components/ResearchPages.test.tsx`、Phase 14-R 持久化记录。
修改摘要：对 Research 时间线的相邻持久化重复消息做边界明确的去重，
仅合并连续且同角色/同内容的副本，避免重放造成一个科学问题重复显示，
同时保留被助手消息隔开的有意重复。
测试结果：ResearchPages/ProductShell/ScientificReportRoute 前端
`94 passed`；认证浏览器 DOM 复核为 4 条真实消息、文档宽度与视口宽度
均为 `731px`、错误 `0`；typecheck、compileall、Ruff、diff check PASS。
提交/CI 状态：未提交；服务与 Chrome 标签页保持运行；Phase 14-R 总体仍
`PARTIAL`，P14R-A/P14R-B 未创建。

回归补充：当前前端全量为 `102 test files / 728 passed`；Phase 14-R
后端相关集合为 `46 passed / 4 historical compatibility skips`。认证浏览器
Data→Research→Research 应用内切换成功，未发生文档级重载，宽度
`731/731`、错误 `0`。same-stack 运维快照继续为 PostgreSQL
`active=1/idle=11/idleInTransaction=0`、Redis `6 workers/queued=0`、
MinIO `status=ok`；服务与 Chrome 标签页保持开启。

任务名称：Agent-2.0 Phase 14-R — Navigation pending-state cleanup
状态：已完成（批次）
完成时间：2026-08-31T22:50:00+08:00
修改文件：`apps/web/app/components/ProductNavigation.tsx`、
`apps/web/app/components/RouteTransitionProgress.test.tsx`、Phase 14-R 记录。
修改摘要：路由提交到目标 pathname/query 后立即清理导航 pending intent，
避免页面已经完成却继续显示切换中状态；保留 15 秒异常兜底。
测试结果：`RouteTransitionProgress` 与 `ProductShell` `18 passed`，
typecheck PASS；服务和 Chrome 标签页保持运行。
提交/CI 状态：未提交；Phase 14-R 总体仍 `PARTIAL`。

## Agent-2.0 Phase 14-R — Structure Viewer/XRD/Report UI batch

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改摘要：复核并修正 Structure 浏览器验收脚本的本地化 Viewer 选择器；
  真实 Presentation 打开精确版本 Viewer Canvas；真实 XRD 页面打开九行
  持久化数值表；报告质量路径确认 Structure/Dataset 的精确版本、发现、
  方法/讨论/表格/限制/结论结构和无原始 JSON。
- 测试结果：Structure 桌面/移动 `1280/1280`、`390/390`，无科学写入；
  XRD 桌面/移动无写入、无全局溢出；隔离浏览器仅有预期 bootstrap `401`；
  前端焦点 `71/71`，后端 operations/recovery/grounding `36 passed, 1 skipped`，
  typecheck 通过。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`，服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — Task/notification recovery and regression batch

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改摘要：完成同栈 Task Center/Notification 真实浏览器复核；验证持久化
  任务、需要关注与取消状态、离线/重连提示和 390x844 无溢出；保留无 live
  任务时不显示 Stop 的正确空状态。
- 测试结果：30 tasks、8 attention、4 canceled；offline banner 恢复后清除；
  前端全量 `102 files / 730 passed`；Phase14-R 后端/service 子集
  `10 passed / 8 historical skips`；operations、compileall、typecheck、
  diff-check 通过。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`，服务与 Chrome 标签页保持运行。

构建补充：最初使用 `useSearchParams()` 的实现触发静态
`/settings/models` 构建错误，已修正为 pending 期间 50ms URL 检查。
修正后 focused `18 passed`、production build `17 routes PASS`、
typecheck PASS。

真实浏览器补充：在同一认证标签页通过 Project History 打开精确 Turn
`fb72c2ad-bed1-47d7-b557-f398f04a8ede`，移动对话面板可展开“本次上下文”，
显示 1 项精确来源、manifest `c4785024-6027-42af-9a1f-52143afd7303`、
`agent2.context-policy/2.0`、输入预算 `12000` 与估算 `60` tokens；精确版本
`a22745f2-17b6-434f-ba4c-3fe6bd244841` 保持不变，宽度 `731/731`、重复 ID 0。
## Agent-2.0 Phase 14-R — service recovery/mobile reinterpretation/navigation

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改摘要：修正移动端验证脚本对隐藏 Workbench 节点的非限定定位；真实
  390x844 浏览器可达 `重新解释（不重算科学结果）`，创建
  `INTERPRET_RESULT` Turn `89037298-7fb1-4c48-bbd3-5407d3f93f41`，精确来源
  版本 `a22745f2-17b6-434f-ba4c-3fe6bd244841`，无 Job/Result 科学重算；
  同栈服务恢复检查通过；App Router 导航零 document reload。
- 测试结果：移动端 overflow `0`；同栈 `/health/runtime` 为
  PostgreSQL/Redis/MinIO/worker；导航冷路径 `120–267 ms` URL、
  `137–628 ms` usable，热路径 `102–141 ms` URL、`120–163 ms` usable；
  仅隔离未认证上下文 bootstrap `401`，无 5xx/critical response。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`，保持服务与 Chrome 标签页运行。
## Agent-2.0 Phase 14-R — Global Search same-stack batch

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改摘要：真实认证浏览器在 PostgreSQL-backed API 上查询 `mat-2`；桌面和
  390x844 移动端均返回 8 条授权结果，保留精确实体链接和项目隔离。
- 测试结果：页面宽度 `1280/1280` 与 `390/390`，无非认证 mutation、5xx 或
  critical 浏览器错误；搜索仍为导航 read model，不改变科学权威。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`，服务与 Chrome 标签页保持运行。
## Agent-2.0 Phase 14-R — static/build verification

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改摘要：完成当前工作树静态与构建核验，未关闭服务或 Chrome。
- 测试结果：touched Ruff PASS，`uv lock --check` PASS，Next production build
  `17 routes PASS`（shared first load `104 kB`），compileall 与 diff-check PASS。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`。

## Agent-2.0 Phase 14-R — context disclosure and edit continuity

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改摘要：补充真实认证浏览器证据记录；Research 结果页可展开上下文及
  审计详情，保留精确 Dataset 版本，编辑上一条问题不改写历史 Turn。
- 测试结果：上下文 disclosure、证据 disclosure、编辑/继续/重跑/重解释
  控件均可见；`12000` token 输入预算与上下文指纹可读；标题 ID 无重复；
  仅预期隔离未认证 bootstrap `401`，无 5xx/critical response。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`；服务与 Chrome 标签页保持运行。

### Agent-2.0 Phase 14-R — cache repair full frontend/build verification

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：无额外产品文件（复核当前工作树）。
- 修改摘要：缓存修复后重跑完整前端、类型检查和生产构建；未停止同栈
  服务或关闭 Chrome。
- 测试结果：`102 test files / 732 tests passed`；typecheck PASS；Next
  production build PASS（17 routes，共享首屏 JS `104 kB`）。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — current-worktree frontend regression

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改摘要：UI 无障碍修复后重跑完整前端回归，未停止服务或关闭 Chrome。
- 测试结果：`102 test files / 730 tests passed`，无新增失败或 mandatory skip。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — context disclosure accessibility repair

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`。
- 修改摘要：为上下文披露和嵌套审计详情增加稳定 `aria-label`，保留原生
  键盘展开、精确版本和既有布局。
- 测试结果：`ResearchPages.test.tsx` `64/64` 通过。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — fresh same-stack service regression

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改摘要：使用当前工作树和真实 PostgreSQL/Redis/MinIO 运行服务回归；
  未停止服务或关闭 Chrome。
- 测试结果：`26 passed`，`0 failed`，`0 errors`，`0 skipped`，耗时
  `425.80s`；operations snapshot 为 PostgreSQL
  `active=1/idle=12/idle-in-transaction=0`、checked-out `0`，Redis 六个
  idle worker、队列 `0`，MinIO `ok`，无 stale active work。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — Mobile Report chapter navigation repair

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/globals.css`
- 修改摘要：修复 390px 报告章节导航的横向溢出，将移动端章节链接改为
  有界多行布局，保留桌面粘性导航、触控尺寸和章节定位。
- 测试结果：ScientificReportRoute/ScientificReportsIndexPage `27/27`；
  认证浏览器报告质量路径 `overflowCount=0`、document/body `390/390`，
  精确版本与八个章节锚点保持可用。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — task/notification browser requalification

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：无新增产品文件；复核 `TaskCenterPage` /
  `NotificationCenterPage` 真实浏览器路径。
- 浏览器结果：认证 Chromium `/tasks`、`/notifications` 读取 30 条任务、8
  条需要关注通知、4 条已取消通知；移动端 `390x844` 无溢出，离线提示与
  online 重同步正常。仅预期 bootstrap `401`，无 critical `5xx`。
- 测试结果：Task/Notification 浏览器脚本完成；TaskCenter focused `4 passed`。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — Task Center canceled-state copy

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/TaskCenterPage.test.tsx`、`AGENT2_PHASE14R_RESULTS.md`、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：统一 `canceled` 与 `cancelled` 的中文终态文案为“已取消”，
  防止任务中心误报为处理中。
- 测试结果：`TaskCenterPage.test.tsx`：`4 passed`。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — truthful bounded global-search counts

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `tests/test_project_access.py`、`AGENT2_PHASE14R_RESULTS.md`、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：搜索响应保留 bounded `items`，并用 `truncated` 明示某类结果
  触及查询窗口；UI 在这种情况下显示“至少 N 项”，避免误报精确总数。
- 测试结果：`tests/test_project_access.py -k product_search`：`4 passed`；
  touched Ruff PASS。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — global search modern-report browser proof

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：无新增产品文件；复核现有 `ProductShell`、Reports 路由与搜索
  读模型。
- 浏览器结果：认证 Chromium `390x844` 搜索 `Li 扩散性质评估`，命中现代报告
  `agent2_report_e54681009a0e49abe371247d9053ce61`，打开链接为该报告精确
  项目路由；document/body `390/390`、无横向溢出。仅预期 bootstrap `401`，
  无 critical `5xx`。
- 测试结果：前端 `ProductShell` `11 passed`；后端 product-search `4 passed`；
  typecheck、compileall、git diff check PASS。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — global search report lifecycle continuity

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `tests/test_project_access.py`、`AGENT2_PHASE14R_RESULTS.md`、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：全局搜索接入现有现代 Scientific Report snapshot 与
  `scientificReportLifecycle` 项目配置，正确返回 archived/trashed/active
  状态；未新增科学权威或报告存储。
- 测试结果：`PYTHONPATH=apps/api python -m pytest -q
  tests/test_project_access.py -k product_search`：`4 passed`。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — research history management browser proof

- 状态：已完成本批次
- 完成时间：2026-08-31
- 浏览器证据：认证 Chromium 在项目 `project_0002_1a0af866391f412d` 创建并
  管理研究记录 `research_bb889efa3b584759bb81c059efafd90f`，完成重命名、
  固定、归档与恢复；最终标题保持，`finalPinned=true`、`finalStatus=archived`，
  恢复后的记录仍可见。
- 移动端 `390x844` 复核：`bodyWidth=390`、`documentWidth=390`、
  `overflowCount=0`；浏览器 `errors=[]`、`critical=[]`。
- 该路径验证的是会话管理投影，不改变 ResearchTurn/Result 科学身份。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — reinterpret zero-delta persistence proof

- 状态：已完成本批次
- 完成时间：2026-08-31
- 证据：移动端重新解释子 Turn `4a2256df-6d41-4725-baa4-884a4b49384f`
  完成 `INTERPRET_RESULT / COMPLETED / VALID`，精确复用父 Turn
  `fb72c2ad-bed1-47d7-b557-f398f04e8ede` 的 MSD/Diffusion Result。
- PostgreSQL 项目计数在操作前后完全一致：
  `jobs=45`、`tool_calls=63`、`artifacts=237`、
  `scientific_result_snapshots=31`；因此科学重算增量为 `0/0/0/0`。
- 浏览器：`390x844`、page overflow `0`，仅预期 bootstrap `401`，无 5xx
  或 critical response。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — operations/recovery focused regression

- 状态：已完成本批次
- 完成时间：2026-08-31
- 测试结果：`tests/test_phase14r_operations.py` +
  `tests/test_phase14r_recovery.py` + `tests/test_phase14r_context_manifest.py`
  共 `16 passed`，无失败；保持服务运行。
- 修改摘要：验证同栈操作快照、恢复语义与 Context Manifest 契约在本批次
  前端/布局变更后仍然稳定。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — exact Result reuse browser recheck

- 状态：已完成本批次
- 完成时间：2026-08-31
- 浏览器证据：认证 Chromium 重新打开 Dataset ResearchTurn
  `8382c443-f9ca-4c90-9aa3-444fea683807`，服务返回 `COMPLETED` /
  `SUCCESS`，精确 Result `15fc4d39-d2d7-5ac3-907a-cb06ed6b7a3f`，
  snapshot `2809dcd1-243e-4323-8538-0a5fe81780d9`，interpretation `VALID`。
  Result 保留 Dataset object `8a425466-b697-4c85-9a43-199414a22865`、
  version `be02266a-7d4f-4ebb-9f28-3132855167d0` 和 mat-2 facts。
- 事件链：`PLAN_READY → QUEUED → RUNNING → RESULT_READY →
  INTERPRETING → COMPLETED`；无新增浏览器 critical response，仅预期
  bootstrap `401`。该次为只读历史重开，不把历史 Result 误报为新计算。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — mobile reinterpretation clean rerun

- 状态：已完成本批次
- 完成时间：2026-08-31
- 浏览器证据：认证 Chromium `390x844` 从 Report 返回来源 Research，
  真实显示 `重新解释（不重算科学结果）`，并创建解释子 Turn
  `2c5b6646-d521-4e9d-a939-f9318efdb557`。该 Turn 使用父 Turn
  `fb72c2ad-bed1-47d7-b557-f398f04e8ede` 的精确 MSD/Diffusion Result，
  `status=COMPLETED`、`action=INTERPRET_RESULT`、`grounding=VALID`。
- 精确上下文：object `f834e358-9944-4fe8-a3ab-f85d68041f54`、
  version `a22745f2-17b6-434f-ba4c-3fe6bd244841`；上下文快照
  `fd138518-efb3-475f-8dc8-0f2aa13a13fe`。
- 结果：viewport `390`、页面 overflow `0`，移动工作台操作可见；本次
  网络审计仅有预期 `401 GET /api/auth/me`，无 `409`、5xx 或 critical。
  该路径未创建 Job/ToolCall/Artifact/ScientificResult。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — same-stack navigation/performance requalification

- 状态：已完成本批次
- 完成时间：2026-08-31
- 浏览器证据：认证 Chromium（指定可执行文件）在 PostgreSQL/Redis/MinIO
  同栈上复核 App Router，Overview/Data/Research/Reports 全部
  `documentRequests=0`，shell marker 保留；warm usable 分别为
  `188/192/254/139 ms`。
- 页面基线：Data desktop/mobile warm p50/p95 `2139/5184` /
  `1462/1490 ms`；Research `1866/1931` / `1874/1901 ms`；Report
  `850/1403` / `844/856 ms`；所有测量 overflow `0`、无 critical。
- 服务状态：PostgreSQL `active=1 idle=12 idle-in-transaction=0`，
  checked-out `0`；Redis 6 idle workers、queue `0`；MinIO `ok`。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

任务中心移动端浏览器复核：`390x844` 下读取 30 条任务，
document/body `390/390`、`overflowCount=0`；仅预期 bootstrap `401`，
无 5xx/critical。

## Agent-2.0 Phase 14-R — refresh failure disclosure and latest regression

- 完成时间：2026-08-31
- 修改摘要：后台同步失败保留最近一次授权任务/通知行并显示明确状态；
  最新前端回归为 `102 test files / 734 tests passed`，typecheck、生产
  build（17 routes、104 kB shared first-load）与 diff-check 通过。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — task/notification refresh continuity

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/NotificationCenterPage.tsx`、`TaskCenterPage.test.tsx`。
- 修改摘要：后台刷新不再把已呈现的任务/通知替换为整页 loading；保留当前
  行和操作，使用可访问同步状态提示；失败时显示“当前显示上次结果”。
- 测试结果：`6 passed, 0 failed`；typecheck 通过。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — task/notification refresh continuity

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/NotificationCenterPage.tsx`、`TaskCenterPage.test.tsx`。
- 修改摘要：后台刷新不再把已呈现的任务/通知替换为整页 loading；保留当前
  行和操作，使用可访问同步状态提示，减少长任务期间的界面闪烁。
- 测试结果：`5 passed, 0 failed`；typecheck 通过。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

认证 Chromium 复核 `/tasks` 与 `/notifications`：30 条任务可读、通知筛选
响应正常，移动端 `390x844` 无溢出；断网提示在恢复后清除。仅预期 bootstrap
`401`，无 5xx/critical。

## Agent-2.0 Phase 14-R — Report lifecycle browser recheck

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：无额外产品文件（认证浏览器复核）。
- 修改摘要：在现有同栈服务上重新验证报告操作菜单、服务器依赖影响预览、
  归档与恢复，以及移动端布局。
- 测试结果：Report `agent2_report_e54681009a0e49abe371247d9053ce61`
  归档/恢复成功，依赖预览显示 `11` 项；`390x844` document/body
  `390/390`、`overflowCount=0`；仅预期 bootstrap `401`，无 5xx/critical。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — project history navigation cache repair

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/ProjectHome.tsx`、
  `apps/web/app/components/ProjectHome.test.tsx`、Phase 14-R 审计/设计记录。
- 修改摘要：移除项目选择时无条件 `forceRefresh` 历史接口的行为，复用已有
  有界缓存；写操作仍通过显式失效保证新鲜度。修复返回项目页时的额外全量
  历史请求，保持 App Router 与科学身份语义不变。
- 测试结果：`ProjectHome.test.tsx` `3/3` 通过；相关前端回归随后执行。
- 提交/CI：未提交，Phase 14-R 仍 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — correctly isolated full backend baseline

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：无（仅校准测试环境并复核当前工作树）。
- 修改摘要：移除 service-only `DATABASE_URL` 后重跑完整非 integration
  后端，确认临时 SQLite 迁移夹具不被 PostgreSQL 污染。
- 测试结果：`1919 passed`、`32 skipped`、`170 warnings`，耗时
  `231.89s`；0 failed。之前 40 项失败确认为环境注入错误，不是产品回归。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。
## Agent-2.0 Phase 14-R — post-repair frontend/build verification

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：无（仅复核）。
- 修改摘要：移动报告导航修复后重跑完整前端与静态检查。
- 测试结果：前端 `102 test files / 730 tests passed`；typecheck、compileall、
  `uv lock --check`、`git diff --check` PASS；本地 Next production build
  `17 routes` PASS，共享首屏 JS `104 kB`。全仓 Ruff 仍存在历史 legacy/evidence
  债务，未新增本批次 touched-code Python lint 问题。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — Report export feedback and browser proof

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/ScientificReportRoute.tsx`、
  `apps/web/app/components/ScientificReportRoute.test.tsx`、
  `apps/web/app/globals.css`，以及 Phase 14-R 证据/持久化记录。
- 修改摘要：Markdown 与复现清单导出统一使用有界 Blob 下载 helper；点击后
  显示可访问成功状态，浏览器不支持 Blob URL 时 fail-closed 并提示重试。
  不改变 Report 快照、ScientificResult、来源版本或科学执行。
- 测试结果：`ScientificReportRoute` focused `20/20`；认证 Chromium
  Report `agent2_report_401cfb421fcab8a9366e06fedb3acb6d` 观察到 Markdown
  `2529` bytes 与 JSON `1403` bytes 两个导出 Blob，标题/复现信息可见，
  无 5xx/critical，仅预期 bootstrap `401`。

## Agent-2.0 Phase 14-R — scientific table mobile interaction repair

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/workspace/WorkspaceArtifactGallery.tsx`、
  `apps/web/app/globals.css`，以及本地浏览器诊断脚本。
- 修改摘要：为真实 Data Platform 的 `workspace-table-scroll` 增加明确的
  `role=region`、可键盘聚焦标签、inline overscroll containment 与稳定滚动条
  空间；保持 bounded table 内容与科学数据身份不变。
- 浏览器结果：认证 Chromium `390x844` 下 document/body 为 `390/390`、
  `pageOverflow=false`；表格 wrapper `clientWidth=390`、`scrollWidth=400`、
  `overflowX=auto`，可横向查看完整列；仅预期 bootstrap `401`。
- 测试结果：Dataset/Product/Workspace focused `70/70` 通过。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — scientific table interaction regression

- 状态：已完成本批次
- 完成时间：2026-08-31
- 修改文件：`apps/web/app/components/workspace/ScientificWorkspaceShell.test.tsx`。
- 修改摘要：新增回归断言，确保真实 Workspace 数据表持续暴露可键盘访问的
  `role=region`、稳定 accessible label 与表格语义。
- 测试结果：Dataset/Product/Workspace focused `71/71`；完整前端当前工作树
  `102 files / 734 tests passed`，typecheck 与 production build PASS。
- 提交/CI：未提交，Phase 14-R 仍为 `PARTIAL`；服务与 Chrome 标签页保持运行。

## Agent-2.0 Phase 14-R — Task Center control and bounded history UX

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/TaskCenterPage.test.tsx`、`persistent/DESIGN_PROGRESS.md`、
  `persistent/TASK_BOARD.md`、`results.md`。
- 修改摘要：停止研究改为可撤销确认对话框，说明保留已提交有效 Artifact、
  未完成分支不会伪装成功；任务中心超过 30 条时明确披露只展示最近窗口，
  保持项目历史作为完整持久化入口。
- 测试结果：Task Center `5/5`；ProductShell + ScientificReportsIndex
  `19/19`；NotificationCenter bounded-window 回归 `3/3`；touched Ruff、
  compileall、git diff check PASS；既有前端全套
  `102 files / 737 tests passed`。
- 提交/CI：未提交；服务与 Chrome 标签页保持运行，Phase 14-R 仍为
  `PARTIAL`。

同批次补充：通知中心对超过 30 条的筛选结果显示 bounded-window 提示，
避免将有界通知 projection 误认为完整历史；NotificationCenter focused
回归通过。

随后补齐共享 task feed 的服务端 `nextCursor` 传播：任务与通知界面现在能
识别“当前行数未达 30 但仍有更早记录”的分页边界；`task-center-data`
新增 `3/3` 回归，覆盖 cursor=true 与授权项目降级。

最终验证：当前前端全套 `102 files / 737 tests passed`；`npm run build`
通过（17 routes，shared first-load `104 kB`），`npm run typecheck` 通过。

## Agent-2.0 Phase 14-R — production navigation and edit-branch batch

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改文件：`apps/web/app/components/ProductNavigation.tsx`、
  `apps/web/app/components/RouteTransitionProgress.test.tsx`、Phase 14-R
  performance/coverage/audit/results 与 persistent 记录。
- 修改摘要：合并同一路径 pointer/focus 预取，移除 50ms location 轮询；
  使用唯一不可变 Next build 目录排除运行中构建覆盖导致的旧 manifest/new
  chunk 水合失败；保留全局/项目/研究三层动作位置。
- 浏览器结果：生产 `3008` 桌面 cold/warm usable `61–118/33–70 ms`，
  移动 `66–102/41–68 ms`；16 次项目转换均 `documentRequests=0`、
  shell 节点保持、无重复 auth。编辑 child
  `92fcd73e-3803-4dcf-bc7a-a63fbcf2a70e` 保留精确 Dataset
  object/version，Result `a6769b88-abbb-54e5-867d-8a12562c6062` 含
  17 facts；390px 无全局溢出。
- 测试结果：focused frontend `85/85`；typecheck、production build、
  touched diff check PASS。
- 提交/CI：未提交；Phase 14-R 总体仍为 `PARTIAL`，服务和浏览器标签保持
  运行。
## Agent-2.0 Phase 14-R — unified Trash and resource governance batch

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改文件：`apps/web/app/components/TrashCenterPage.tsx`、
  `apps/web/app/components/TrashCenterPage.test.tsx`、
  `apps/web/app/trash/page.tsx`、`apps/web/app/trash/loading.tsx`、
  `apps/web/app/components/ProductShell.tsx`、`ProductShell.test.tsx`、
  `apps/web/app/globals.css`、`apps/web/app/lib/agent2-research-api.test.ts`、
  `apps/api/mdi_api/config.py`、`agent2_errors.py`、
  `agent2_repositories.py`、`research_agent/service.py`、`routers/agent2.py`、
  `report_composition.py`、`operations.py`、相关测试与 Phase 14-R 文档。
- 修改摘要：增加统一回收站入口与恢复/受保护永久删除路径；服务端以
  PostgreSQL 项目行锁实施活动 ResearchTurn 上限并返回 typed 429；运维快照
  公开有界资源治理配置；错误展示不再泄漏对象形状。未新增科学权威。
- 测试结果：前端聚焦 `3 files / 19 tests passed`；后端聚焦
  `3 passed / 14 deselected`；TypeScript typecheck、touched Ruff、git
  diff-check PASS；同栈快照 PostgreSQL/Redis/MinIO `ok`、6 idle workers、
  queue depth `0`、idle-in-transaction `0`、pool checked out `0`。
- 浏览器结果：认证浏览器在 `/projects` 通过正常菜单将项目
  `project_0001_e0091c0e6f5a4d58` 移入回收站并在 `/trash` 完成依赖预览、
  exact-name PURGED；第二项目 `project_0002_f78490df5c38406a` 完成
  `TRASHED → Restore → ACTIVE`。服务和浏览器标签页保持运行。
- 提交/CI：未提交；Phase 14-R 仍为 `PARTIAL`，待下一批完整回归与发布封板。

## Agent-2.0 Phase 14-R — project organization metadata batch

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改文件：`apps/api/mdi_api/routers/projects.py`、
  `apps/api/mdi_api/routers/secured_runtime.py`、
  `apps/api/mdi_api/routers/project_history.py`、
  `apps/web/app/lib/planner-api.ts`、
  `apps/web/app/components/ProductPages.tsx`、
  `tests/test_project_access.py`、
  `apps/web/app/components/ProductPages.test.tsx`、
  `docs/agent2/phase14r/PHASE14R_PRODUCT_REALITY_AUDIT.md`、
  `docs/agent2/phase14r/PHASE14R_MATURE_PRODUCT_COVERAGE_MATRIX.md`、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：在现有 `project_configs` 非科学元数据边界内增加项目固定/
  取消固定；API、Project History、项目目录和动作菜单共享同一权威状态，
  固定项目稳定置顶，读者账号不能写入。未新增科学权威、版本或生命周期
  语义。
- 测试结果：ProductPages `33 passed`；项目访问 `13 passed`；touched Ruff、
  typecheck、production build、diff-check PASS。
- 提交/CI 状态：未提交；Phase 14-R 总体仍为 `PARTIAL`，服务与浏览器
  标签页保持运行。

## Product maturity — 同栈科学对象逐页复核（2026-09-04）

- 状态：完成当前生产构建的科学对象读路径复核，成熟度总任务仍处理中。
- 证据：认证浏览器在 `127.0.0.1:3020` 打开活动项目 `13/13` 个精确
  ScientificObject/Version 入口。Electronic DOS、Phonon Band/DOS、Dataset、
  ML 表格、Electronic Band、Structure、Trajectory、Diffusion 均在 hydration
  后到达声明的 renderer 或 bounded fallback；`Internal Server Error`、
  `Application error`、`SOURCE_MISSING`、alert 均为 `0`，桌面宽度
  `1265/1265`，overflow `0`。Structure/Trajectory 挂载真实 canvas；Structure
  显示 `Si` 位点、晶胞和精确版本信息。
- 服务：API `8005`、PostgreSQL、Redis、MinIO、workers 与浏览器标签页均保持
  运行；`/api/health/runtime` 返回 PostgreSQL/Redis/MinIO/Redis worker。
- 测试：后端焦点 `56 passed / 1 historical skip`；全前端当前回归
  `110 files / 819 tests passed`；typecheck、production build、compileall、
  `uv lock --check`、`git diff --check` 均通过。
- 边界：历史源文件确实缺失时仍展示显式 fail-closed，不伪造替代 payload；
  未提交、未推送，未删除用户文件/证据/临时日志。

## Agent-2.0 Phase 14-R — project tags and catalog discovery follow-up

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改摘要：项目编辑对话框支持有界非科学组织标签；项目目录增加标签
  筛选，服务端搜索也会在授权项目范围内匹配标签并回显标签摘要。标签
  仍保存在 `project_configs.config_json.projectTags`，不会进入科学上下文、
  Result 或版本权威。
- 测试结果：ProductPages `35 passed`；项目访问 `23 passed`；touched Ruff
  与 typecheck PASS。
- 提交/CI 状态：未提交；Phase 14-R 总体仍为 `PARTIAL`，服务与浏览器标签页
  保持运行。

## Agent-2.0 Phase 14-R — archived global-search filter evidence

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改摘要：补齐当前工作树审计、覆盖矩阵与结果记录中的归档状态搜索证据；
  不改变搜索或科学权威。
- 浏览器结果：同一认证内置浏览器标签页在全局搜索中选择
  `状态=已归档` 并输入 `硅结构`，返回 8 个授权历史 Research 会话，
  每项显示 `已归档` 并保留精确项目作用域路由；浏览器 warning/error 日志为空。
- 测试结果：`uv lock --check` 与 `git diff --check` PASS。
- 提交/CI 状态：未提交；Phase 14-R 仍为 `PARTIAL`，P14R-A/P14R-B 未创建。

## Product Maturity — Data Visibility and Exact Payload Closure

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `tests/test_project_access.py`、`apps/web/app/components/ProductPages.tsx`、
  `apps/web/app/components/ProductPages.test.tsx`、
  `apps/web/app/components/ProjectHome.tsx`、
  `apps/web/app/components/ProjectHome.test.tsx`、
  `apps/web/app/projects/[projectId]/datasets/[datasetId]/page.tsx`、
  migration-head regression、Product Maturity evidence 与 `persistent/*`。
- 修改摘要：确认 PostgreSQL、Redis、MinIO、API、workers 和 frontend 均
  正常；把 11 个零资源 Dataset 从错误的 storage failure 改为显式 `EMPTY`
  专业空状态；使用 exact SHA/parser/object identity 恢复唯一用户可见历史
  Dataset 的 raw/normalized/metadata 三个既有权威对象；旧 Dataset 详情路由
  统一进入当前 Data Platform，空 Dataset 不再暴露科学执行 Planner。
- 可见数据结果：28 个 Dataset 为 17 READY + 11 EMPTY + 0 failed；13/13
  ScientificObjectVersion Viewer READY；241/241 Artifact 内容可读；11/11
  Report 可读；70/70 产品路由 HTTP 200；Internal Server Error=0，
  SOURCE_MISSING=0。
- 浏览器结果：恢复 Dataset 显示 `Si / 1` 单行权威表格；旧空 Dataset 深链
  正确重定向并显示“尚未导入科学对象”，Research link=0、Planner run
  action=0、global overflow=0、browser logs=0。
- 测试结果：完整 backend `1970 passed, 84 skipped`；完整 frontend
  `106 files / 773 passed`；focused frontend `41 passed`；隔离
  PostgreSQL/Redis/MinIO `70 selected / 70 passed / 0 failed / 0 errors /
  0 skipped`；production build、typecheck、compileall、uv lock、touched
  Ruff、git diff check PASS。最终 operations snapshot 为 status=ok、
  PostgreSQL active=1/idle=5/idle-in-transaction=0/pool checkedOut=0、
  六个 idle workers、production queue depth=0、MinIO=ok。
- 服务状态：frontend 3013、API 8005、PostgreSQL 55434、Redis 6379/13、
  MinIO 9000/9001、六个 workers 与两个认证浏览器核验标签页保持运行。
- 提交/CI 状态：未提交；用户本轮要求先进行最终产品核验。`HEAD ==
  origin/master == 9864e79c433536cc90b24c6a4c68c5bebd940daa`。

## Product Maturity Closure — scientific data reachability remediation

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`,
  `apps/web/app/components/ProductPages.tsx` 及其回归测试，当前迁移 head
  回归断言，payload availability/recovery evidence 与 persistent 状态文件。
- 修改摘要：确认 PostgreSQL、Redis、MinIO、API、六个 worker 和前端均正常，
  Internal Server Error/不可用页面不是服务未启动。把零文件/零对象 Dataset
  从 storage failure 修正为正式 `EMPTY` contract，并让 UI 显示可操作的导入
  空状态而不是故障，同时禁止无 payload 的 Research 动作。对唯一缺失的
  acceptance Dataset，只有在 raw ZIP、normalized JSON、parser object ID/hash、
  schema 与 resolver 全部精确匹配后，才条件写回三个既有 MinIO key；无版本、
  Result 或 Report 变更。
- 实时数据结果：28 个可见 Dataset 全部可达（17 READY、11 EMPTY、0 失败）；
  13 个可见 ScientificObjectVersion Viewer 全部为 HTTP 200、payload READY、
  PROFESSIONAL，SOURCE_MISSING=0。报告中的轨迹对象
  `d325a090-d53f-4980-8a5e-c466bf6470eb` / version
  `052d3a8e-8a35-48ac-9e65-b95a86b42c99` 已在认证内置浏览器显示三帧轨迹、
  播放/测量/超胞及精确元数据，浏览器日志为空。
- 测试结果：完整前端 `106 files / 773 tests passed`；focused backend
  object-store `2 passed`；migration `3 passed`；typecheck、production
  build、compileall、uv lock、touched Ruff、git diff check PASS。完整后端
  与 PostgreSQL/Redis/MinIO service-backed 最终计数见随后补充。
- 提交/CI 状态：未提交；保留所有既有用户工作树与证据文件，服务及浏览器
  标签页保持运行。

## Product maturity closure — same-stack/runtime and shared UX batch

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改摘要：确认并保持 PostgreSQL/Redis/MinIO/workers 运行；将
  `0029_product_maturity_platform_roles` 升级到真实 PostgreSQL；平台
  Provider 变更改为显式 `PLATFORM_ADMIN`，普通研究者的模型设置改为只读；
  全局任务/通知改为单次授权分页 feed；空白搜索不再加载全部历史；研究
  历史结果使用单调加载状态；移动端保留项目身份；新增当前产品现实审计。
- 修改文件：`apps/api/mdi_api/db.py`、
  `apps/api/mdi_api/routers/auth.py`、
  `apps/api/mdi_api/routers/planner_providers.py`、
  `apps/api/mdi_api/routers/workspaces.py`、
  `apps/api/mdi_api/workspaces.py`、对应 migration/tests、前端
  `ProductShell`/`ModelSettingsPage`/`ResearchPages`/Task Center/
  Notifications、`globals.css`、`docs/agent2/product_maturity/PRODUCT_REALITY_AUDIT.md`。
- 测试结果：前端定向 `22 passed`；后端定向 `26 passed`；生产
  `typecheck`、`build`、`git diff --check` PASS；浏览器同栈 Data、
  Tasks、Reports、Model Settings 路径加载成功；`/health/runtime`
  PostgreSQL/Redis/MinIO/Redis worker/DeepSeek 全部 `ok`。
- 提交/CI 状态：未提交；保留当前用户未提交修改，待更大批次产品成熟度
  工作完成后统一审阅和提交。

## Phase 14-R — Scientific Payload Availability Remediation

- 状态：已完成
- 完成时间：2026-09-01T22:19:12+08:00
- 修改文件：`apps/api/mdi_api/routers/planner.py`、
  `tests/test_phase8c_planner_read_api.py`、`apps/web/app/lib/planner-api.ts`、
  `apps/web/app/components/ScientificViewerAdapter.tsx`、
  `apps/web/app/components/ProductPages.tsx`、Scientific Object Viewer/Shell、
  focused frontend tests、Phase 14-R audit/results/recovery evidence 与
  `persistent/*` 项目记录。
- 修改摘要：确认服务本身正常，根因为 PostgreSQL 引用与活动 MinIO 数据根
  分裂，加上 `NoSuchKey` 未处理。按 exact key/size/SHA-256/contentHash/
  metadata identity 恢复 1,551 个对象，活动引用覆盖达到 1,800/1,805；
  canonical diffusion Job 的 8/8 Artifact 和 exact trajectory Viewer 均恢复。
  对剩余 5 个无法证明的历史引用保留 typed missing 状态，不伪造 payload、
  不静默替换版本。UI 区分确认缺失与临时服务失败，并保留精确 provenance。
- 测试结果：后端 focused `9 passed`；前端 focused `45 passed`；
  `npm --prefix apps/web run typecheck` PASS；production build PASS；
  touched Ruff PASS；`git diff --check` PASS。认证浏览器 1280×720 与
  390×844 的 Research/Report/Dataset 均为 loading=0、Internal Server
  Error=0、unexpected 5xx=0、mobile global overflow=0。目标 Artifact 内容
  API 8/8 为 200 且 SHA-256 匹配。
- 服务状态：frontend 3013、API 8005、PostgreSQL 55434、Redis 6379、
  MinIO 9000/9001、6 个 Redis workers 与可见 Chromium 核验窗口保持运行。
- 提交/CI 状态：未提交；用户本轮未要求提交或推送。`HEAD ==
  origin/master == 9864e79c433536cc90b24c6a4c68c5bebd940daa`。
- 唯一外部恢复输入：若需让 `dataset_0001_a0b09e3324e44ca4` 完整交互，
  需要原始 `materials.zip`，SHA-256
  `b75f9a1d398de4636e4494f2aaa04977326ca66a96356fcc1be87e86a3a520c4`。

## Agent-2.0 Phase 14-R — Scientific Report organization batch

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改摘要：在既有 `project_configs` 管理投影内增加 Report 有界重命名和
  固定；列表、直接读取和全局搜索共享显示标题，原始 snapshot title 作为
  `source_title` 保留。UI 使用现有报告行 overflow menu，不新增主操作栏。
- 浏览器结果：Report `agent2_report_19a0…` 重命名为
  “结构配位数分布统计报告”并固定置顶，精确路由不变；全局搜索返回唯一
  授权结果。移动 Chromium `390/390`、overflow 0，动作菜单和不可变快照
  提示可达；仅出现预期登录 bootstrap `401`，critical 0。
- 零重算结果：UI Unpin→Pin 前后
  Jobs/ToolCalls/Artifacts/Results/Report snapshots 均为
  `301/395/1565/203/44`；snapshot
  `c8cc6fcb-1f0b-50c6-b6db-049374f7de6e` 及 SHA-256
  `10a9b50c…ec555` 不变。
- 聚焦测试：Report service lifecycle/organization `1 passed`；
  project authorization/search `2 passed`；Report index UI `10 passed`；
  touched Ruff、typecheck、compileall PASS。
- 提交/CI 状态：未提交；Phase 14-R 仍为 `PARTIAL`，报告 revision compare
  与最终 P14R-A/P14R-B release seal 仍未闭合。

## Agent-2.0 Phase 14-R — project provenance export and service recovery follow-up

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `apps/api/mdi_api/main.py`、`apps/web/app/lib/planner-api.ts`、
  `apps/web/app/components/ProductPages.tsx`、
  `apps/web/app/components/ProductPages.test.tsx`、
  `tests/test_project_access.py`、Phase 14-R 文档与共享 schema。
- 修改摘要：增加授权、有界、不可执行的项目 provenance manifest API 和
  Projects overflow 导出动作；复用既有项目组织/授权边界，不引入新的科学
  权威。定位并修复浏览器 3000→8002 命中旧 API 进程导致的 `404`，以当前
  工作树持久会话重载 8000/8002 API，PostgreSQL/Redis/MinIO/worker 保持运行。
- 测试结果：`tests/test_project_access.py` `25 passed`；ProductPages
  `37 passed`；Phase14-R operations/recovery/context `21 passed`；完整
  frontend `103 files / 750 tests passed`；`npm run typecheck`、production
  build、compileall、git diff check、touched Ruff（新文件范围）PASS。
  `main.py` 的历史大型路由导入 F401 未扩大处理，保留为既有非阻塞 lint debt。
- 浏览器/服务结果：认证 `/projects` 同栈标签页真实看到“导出项目清单”并
  收到成功状态；`/health/runtime` 在 8000/8002 均为 PostgreSQL/Redis/
  MinIO/Redis worker/DeepSeek configured。标签页、前端、数据库、Redis、
  MinIO 和 worker 均保持运行。
- 提交/CI 状态：未提交；Phase 14-R 仍为 `PARTIAL`，更广泛能力族、
  retention/operations、性能/真实用户验收和 P14R-A/P14R-B 仍未闭合。

补充回归结果（同一批次当前工作树）：

```text
full backend = 1935 passed, 84 skipped, 170 warnings
full frontend = 103 files / 751 tests passed
operations snapshot = PostgreSQL active=1 idle=8 idle-in-transaction=0,
                      pool checkedOut=0, Redis workers=6, queue depth=0,
                      MinIO=ok
uv lock --check = PASS

补充浏览器证据：认证 `/projects` 同栈标签页打开全局搜索，输入 `mat-2` 后
显示 `找到 8 项，显示前 8 项`，结果包含精确 Research/Report 路由和项目/
生命周期标记；当前浏览器日志为空。该路径使用 3000→8002→PostgreSQL，
因此 Search/organization 的 service-backed 维度从 `NOT_QUALIFIED` 更新为
`PASS`，整体 Search 行仍因历史跨项目与 collections 语义保持 `PARTIAL`。
```

补充验证：本批次后的完整前端回归为 `103 个测试文件 / 750 个测试通过`；
`npm run build`、`npm run typecheck`、`python -m compileall -q apps/api/mdi_api`
和 `git diff --check` 均通过。

## Agent-2.0 Phase 14-R — Post-Seal Product Quality Remediation

- 状态：已完成
- 完成时间：2026-09-01
- 修改文件：Phase 14-R release evidence in
  `AGENT2_PHASE14R_RESULTS.md`, `persistent/TASK_BOARD.md`,
  `persistent/DESIGN_PROGRESS.md`; cross-browser acceptance harness
  `apps/web/test/phase12-7-cross-product-browser-evidence.mjs`.
- 修改摘要：完成同栈产品质量收口与跨浏览器无障碍验收脚本修复。账户菜单
  按真实产品顺序验证“回收站 → 模型设置 → 退出登录”，关闭态验证焦点
  恢复、`aria-expanded=false` 与不保留失效 `aria-controls`；等待逻辑兼容
  WebKit 的异步焦点恢复。未改变科学数据、Result、版本、队列或权威边界。
- 测试结果：当前工作树完整后端 `1948 passed, 32 historical optional
  skips`；完整前端 `105 files / 764 tests passed`；ARIA/product focused
  `116 passed`；同栈 PostgreSQL/Redis/MinIO `70 selected / 70 passed /
  0 failed / 0 errors / 0 skipped`；compileall、uv lock、production build、
  touched Ruff、git diff check 均通过。浏览器证据
  `docs/agent2/phase14r/evidence/browser_final_aria_reaudit_2026-09-01_r2.json`
  记录桌面/移动溢出 0、重复 ID 0、broken ARIA 0、console/page errors 0、
  critical 4xx/5xx 0、授权失败 0。
- 提交/CI 状态：P14R-A final candidate
  `8607b1c1f1cb4afbcbf777b69129a0055a141791`，exact CI
  `33501524613` PASS；P14R-B
  `f23f6b124383ccdba03d750911d06e85b6532ce4`，exact-current-head CI
  `33502281952` PASS；`HEAD == origin/master`。服务、worker 与 Chrome
  标签页按用户要求保持运行；Phase 15 未创建、未启动。

## Agent-2.0 Phase 14-R — bulk project organization follow-up

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改摘要：项目选择工具栏新增批量固定/取消固定，复用现有批量动作
  与事务/授权边界；批量组织操作只写 `project_configs.pinnedProject`，
  不触碰科学对象、版本、Result 或历史记录。
- 测试结果：ProductPages `36 passed`；项目访问 `24 passed`；touched Ruff
  PASS。
- 提交/CI 状态：未提交；Phase 14-R 总体仍为 `PARTIAL`，服务与浏览器标签页
  保持运行。

## Agent-2.0 Phase 14-R — project catalog query consolidation

- 状态：已完成本批次
- 修改摘要：项目目录把成员角色与 `project_configs` 固定/标签元数据从
  逐行查询改为按可见项目集合批量读取，保留旧 schema 兼容和授权边界，
  避免组织功能引入额外 N+1。
- 测试结果：项目访问 `23 passed`；touched Ruff PASS；前端 ProductPages
  `35 passed`、typecheck/build 已在同一批次验证。
- 提交/CI 状态：未提交；Phase 14-R 总体仍为 `PARTIAL`，服务与浏览器标签页
  保持运行。

## Agent-2.0 Phase 14-R — archived global-search filter evidence

- 状态：已完成本批次
- 完成时间：2026-09-01
- 修改摘要：补齐当前工作树审计、覆盖矩阵与结果记录中的归档状态搜索证据；
  不改变搜索或科学权威。
- 浏览器结果：同一认证内置浏览器标签页在全局搜索中选择
  `状态=已归档` 并输入 `硅结构`，返回 8 个授权历史 Research 会话，
  每项显示 `已归档` 并保留精确项目作用域路由；浏览器 warning/error 日志为空。
- 测试结果：文档变更后 `git diff --check` 待本批次末复核。
- 提交/CI 状态：未提交；Phase 14-R 仍为 `PARTIAL`，P14R-A/P14R-B 未创建。

## Product maturity — Dataset interaction batch (continued)

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：`apps/api/mdi_api/routers/datasets.py`,
  `tests/test_dataset_object_store_projection.py`,
  `apps/web/app/components/workspace/WorkspaceArtifactGallery.tsx`,
  `apps/web/app/globals.css`,
  `docs/agent2/product_maturity/PRODUCT_MATURITY_BATCH_2026-09-01.md`,
  `persistent/DESIGN_PROGRESS.md`, `persistent/TASK_BOARD.md`,
  `persistent/ARCHITECTURE_DECISIONS.md`.
- 修改摘要：为 DataFrame object-store 结果补齐确定性的 `objectId`、
  `sampleRef`、`sampleKey`；表格保留可读样本身份、固定左侧选择列并提供
  移动端横向浏览提示，避免“内容可读但无法选择”的产品断层。未改变科学
  数值、ScientificObject/Version、Result、Artifact 或报告权威。
- 运行证据：`/health/runtime` 为 PostgreSQL/Redis/MinIO/Redis worker/
  DeepSeek 全部 `ok`；API `8005`、前端 `3013`、PostgreSQL `55434`、
  Redis `6379/13`、MinIO `9000/9001` 与六个 worker 均保持运行。
- 浏览器证据：认证数据页刷新后显示 `Si / 1`、`objectId =
  obj_dataframe_60c91184df02`、稳定 `sampleRef =
  dataset_0001_a0b09e3324e44ca4@2:60c91184df022d34:0`，`选择` 已启用；
  数据页浏览器错误/警告为空；账户中心显示认证身份与权限信息。
- 测试结果：后端 focused `56 passed`；前端 focused `91 passed`；完整后端
  `1978 passed, 84 skipped`；typecheck/build/compileall/uv lock/Ruff/diff
  均 PASS。
- 提交/CI 状态：未提交；服务、worker 与浏览器标签页保持运行；总任务仍有
  后续产品成熟度队列，不宣称整体 COMPLETE。

## Product maturity — runtime compatibility and project governance batch

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：`apps/api/mdi_api/routers/platform_admin.py`,
  `apps/api/mdi_api/main.py`, `apps/web/app/lib/product-api.ts`,
  `apps/web/app/components/AdminCenterPage.tsx`,
  `apps/web/app/components/AdminCenterPage.test.tsx`,
  `apps/web/app/globals.css`, `tests/test_account_admin_management.py`,
  `scripts/phase14r_frontend_alias.mjs`,
  `docs/agent2/product_maturity/PRODUCT_MATURITY_BATCH_RUNTIME_GOVERNANCE_2026-09-01.md`,
  `persistent/DESIGN_PROGRESS.md`, `persistent/ARCHITECTURE_DECISIONS.md`,
  `persistent/TASK_BOARD.md`.
- 修改摘要：确认用户报告的不可读页面不是 PostgreSQL/Redis/MinIO/API/
  worker 停止；当前同栈 13 个可见 ScientificObject Viewer 均为
  `200 / READY`。新增无状态 `3000 → 3013` 兼容入口，解决旧书签落到
  失效前端端口的问题；新增平台管理员项目目录与成员角色治理，复用
  `project_members`、保护 owner、服务端授权并写入脱敏审计。
- 测试结果：后端账户/管理员 `7 passed`；前端 Admin/Trash/ProductShell
  `24 passed`；typecheck、production build、compileall、Ruff、diff check
  均 PASS。`/health/runtime` 为 PostgreSQL/Redis/MinIO/Redis workers/
  DeepSeek 全部 `ok`；3000/3013 根、Dataset、Report 请求均 `200`。
- 提交/CI 状态：未提交；服务、worker、3000 兼容入口与浏览器会话保持
  运行；整体 Product Maturity Closure 仍为处理中。

## Product maturity — payload availability UI clarification batch

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：`apps/web/app/components/ProductPages.tsx`,
  `apps/web/app/components/ProductPages.test.tsx`,
  `apps/web/app/components/ScientificViewerAdapter.tsx`,
  `apps/web/app/components/ScientificViewerAdapter.effect.test.tsx`,
  `apps/web/app/globals.css`,
  `docs/agent2/product_maturity/PRODUCT_MATURITY_BATCH_PAYLOAD_UI_2026-09-01.md`,
  `persistent/TASK_BOARD.md`.
- 修改摘要：将来源读取失败按服务端证据区分为“暂时失败，可重试”和
  “已确认缺失”，避免将可恢复故障误报为 Internal Server Error；确认缺失
  时保留精确来源/版本身份、禁止静默替换，并显示重新导入/恢复原文件的
  可操作提示。未修改科学数据、ScientificObject/Version、Result、Artifact
  或 Report authority。
- 测试结果：ProductPages `40 passed`；TypeScript typecheck PASS；
  touched Ruff PASS；`git diff --check` 待本批次末复核。认证 acceptance
  用户的 28 个 Dataset object-store 路由全部 HTTP 200，`/health/runtime`
  的 PostgreSQL/Redis/MinIO/worker/DeepSeek 均为 `ok`。
- 提交/CI 状态：未提交；服务、worker、3000 兼容入口与浏览器标签页保持
  运行；整体 Product Maturity Closure 仍为处理中。

## Product maturity — route continuity batch

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：`apps/web/app/components/DatasetWorkbenchPage.tsx`,
  `apps/web/app/components/DatasetWorkbenchPage.test.tsx`,
  `apps/web/app/components/ProjectHome.tsx`,
  `apps/web/app/components/ProjectHome.test.tsx`,
  `docs/agent2/product_maturity/PRODUCT_MATURITY_BATCH_ROUTE_CONTINUITY_2026-09-01.md`,
  `persistent/TASK_BOARD.md`, `persistent/DESIGN_PROGRESS.md`,
  `persistent/ARCHITECTURE_DECISIONS.md`.
- 修改摘要：修复 Dataset 工作台和项目首页的项目上下文丢失问题。已加载
  项目现在通过现有 ProductNavigation 客户端过渡进入项目级数据集导入；
  数据工作台面包屑/返回项目也回到当前项目，避免落入全局根或旧兼容分析
  入口。无科学 authority、版本、Result、Artifact、Report 或服务拓扑变更。
- 测试结果：DatasetWorkbenchPage `1 passed`、ProjectHome `3 passed`、
  ProductPages `40 passed`；TypeScript typecheck PASS；`git diff --check`
  PASS（仅既有换行规范告警）。
- 提交/CI 状态：未提交；API、前端、PostgreSQL、Redis、MinIO、workers
  与现有浏览器标签页保持运行；总任务仍在继续，不宣称整体 COMPLETE。

补充：本批次发现旧书签兼容端口 `3000` 的代理进程曾退出；未触碰主前端
`3013`，已重新启动无状态 `3000 → 3013` 代理并确认端口监听恢复。
## Product maturity — payload recovery entry UX batch

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：`apps/web/app/components/ProductPages.tsx`,
  `apps/web/app/components/ProductPages.test.tsx`,
  `docs/agent2/product_maturity/PRODUCT_MATURITY_BATCH_PAYLOAD_RECOVERY_ENTRY_2026-09-01.md`,
  `persistent/TASK_BOARD.md`, `persistent/DESIGN_PROGRESS.md`,
  `persistent/ARCHITECTURE_DECISIONS.md`.
- 修改摘要：为确认缺失的科学 payload 增加项目级“重新导入源文件”恢复入口；
  为重复数据 fallback 标题生成 Dataset/data-kind 作用域的唯一 DOM id 并保持
  `aria-labelledby` 关系；为缺失/暂时不可读的结果 Artifact 增加项目级
  “返回数据源”入口。未修改任何科学 authority、版本、Result、Artifact、
  Report 或服务拓扑。
- 测试结果：ProductPages/ProductShell/ProjectHome/DatasetWorkbench focused
  `61 passed`，ScientificViewerAdapter effect `8 passed`；TypeScript typecheck、生产 build、
  API compileall、`git diff --check` 均 PASS；同栈 `/health/runtime` 继续为
  PostgreSQL/Redis/MinIO/worker/DeepSeek `ok`。
- 提交/CI 状态：未提交；API、前端、数据库、Redis、MinIO、workers、
  3000 兼容入口与浏览器标签页保持运行。

## Product maturity — scientific table accessibility normalization

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：
  `apps/web/app/components/workspace/WorkspaceArtifactGallery.tsx`,
  `apps/web/app/components/workspace/WorkspaceArtifactGallery.test.tsx`,
  `persistent/TASK_BOARD.md`, `persistent/DESIGN_PROGRESS.md`,
  `persistent/ARCHITECTURE_DECISIONS.md`.
- 修改摘要：将科学表格滚动区域的主可访问名称恢复为稳定语义，
  将“样本身份列固定在左侧”等移动交互提示改为每个实例唯一的
  `aria-describedby` 说明链，避免重复 DOM id 和不稳定 role 名称。
  未修改科学数据、版本、Result、Artifact、Report 或服务拓扑。
- 测试结果：ScientificWorkspaceShell `29 passed`；完整前端
  `108 files / 787 tests passed`；TypeScript typecheck、API compileall、
  `git diff --check` PASS；`/health/runtime` 继续报告 PostgreSQL/Redis/
  MinIO/Redis worker/DeepSeek，同栈服务和浏览器标签页保持运行。
- 提交/CI 状态：未提交；等待后续产品成熟度批次统一收口。

## Product maturity — same-stack runtime reload and browser recheck

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：`docs/agent2/product_maturity/PRODUCT_MATURITY_BATCH_RUNTIME_RELOAD_2026-09-01.md`,
  `persistent/TASK_BOARD.md`, `persistent/DESIGN_PROGRESS.md`,
  `persistent/ARCHITECTURE_DECISIONS.md`.
- 补充修改：`scripts/phase14r_frontend_start.mjs`、
  `apps/web/test/phase14r-runtime-static-assets.mjs`。
- 修改摘要：恢复 API 的正式 MinIO 凭据并验证真实 PostgreSQL/Redis/MinIO/
  worker 健康；替换 3013 上错误的旧 Next 构建进程，修复 `/trash` 和
  `/account` 的 ChunkLoadError。未关闭服务或浏览器标签页，未修改科学
  authority、版本、Result、Artifact 或 Report 数据。
- 测试结果：账号/生命周期/Viewer 后端 `16 passed`；TypeScript typecheck、
  compileall、`git diff --check` PASS；新认证浏览器标签页的 Trash、Account、
  数据对象详情、报告详情和 Acceptance Dataset 均无应用错误、Internal
  Server Error 或 console error；静态资源 smoke test PASS；
  `/health/runtime` 全部必需组件 `ok`。
- 提交/CI 状态：未提交；服务与浏览器标签页保持运行；总体任务继续处理中。

## Product maturity — admin route continuity

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：`apps/web/app/components/ProductRouteFrame.tsx`,
  `apps/web/app/components/ProductRouteFrame.test.ts`,
  `apps/web/app/components/UserCenterPage.tsx`,
  `apps/web/app/components/UserCenterPage.test.tsx`,
  `apps/web/app/components/AdminCenterPage.tsx`,
  `apps/web/app/components/AdminCenterPage.test.tsx`,
  `persistent/TASK_BOARD.md`, `persistent/DESIGN_PROGRESS.md`.
- 修改摘要：将 `/admin` 接入共享认证产品壳，补齐全局导航、会话守卫、
  转场和滚动归属；账户中心与管理中心增加明确的“返回控制台”出口。
  未修改科学数据、版本、Result、Artifact、Report 或生命周期 API。
- 测试结果：前端 `ProductRouteFrame`、`AdminCenterPage`、
  `UserCenterPage` 窄回归 `13 passed`。
- 提交/CI 状态：未提交；未关闭服务或浏览器标签页；总体任务继续处理中。

## Product maturity — shared UI and account fluency

- 状态：已完成本批次；总 Product Maturity Closure 继续处理中
- 完成时间：2026-09-01
- 修改文件：`apps/web/app/components/UserCenterPage.tsx`,
  `apps/web/app/components/UserCenterPage.test.tsx`,
  `apps/web/app/globals.css`, `persistent/TASK_BOARD.md`,
  `persistent/DESIGN_PROGRESS.md`.
- 修改摘要：集中修复共享产品壳的横向溢出隔离、sticky 上下文导航及
  action 状态反馈；账户中心的会话列表默认限制为最近 8 个，并提供
  明确的“显示全部会话”入口，降低长页面和移动端滚动负担。重新构建并
  窄重启 3013 前端，让实际浏览器加载当前构建；未关闭 API、PostgreSQL、
  Redis、MinIO、workers 或浏览器标签页。
- 测试结果：UserCenter/ProductShell/ProductRouteFrame 前端窄回归
  `27 passed`；完整前端回归 `108 files / 788 passed`；typecheck、
  production build、compileall、`git diff --check` PASS；
  `/health/runtime` PostgreSQL/Redis/MinIO/Redis worker/DeepSeek 全部
  `ok`；认证账户页 desktop 会话列表由 100 条收敛为默认 8 条，移动端
  `scrollWidth=375/clientWidth=375` 且无页面告警。
- 补充验证：3000 兼容入口曾继续提供旧 chunk，导致 fresh account tab
  出现 ChunkLoadError；已将 alias 重启为 `3000 → 3013`。新的 3000
  fresh tab 静态资源引用 `14/14` 返回 200，页面默认 8 条会话、无
  Internal Server Error、无 console error。
- 补充 UI 回归：任务/通知筛选在 390px 视口保持单行横向可滑动，按钮
  均为 44px 触控高度，页面宽度未扩大；任务、通知、共享产品壳窄回归
  `25 passed`，production build PASS。
- 提交/CI 状态：未提交；服务与浏览器标签页保持运行；总体任务继续处理中。
## Product maturity — live scientific surface re-audit (2026-09-02)

- 状态：已完成本轮核验（总产品成熟度任务仍处理中）
- 修改摘要：新增 `docs/agent2/product_maturity/LIVE_SCIENTIFIC_SURFACE_REAUDIT_2026-09-02.md`，记录同栈运行时、浏览器详情回归及截图根因分类；未修改科学 authority、数据库记录或服务。
- 真实浏览器结果：16/16 项目数据入口；41/41 精确 Dataset/Object 详情；10/10 已验证 Report；10/10 报告引用 Viewer；`:3000` 兼容入口轨迹 Viewer 均无 Internal Server Error、SOURCE_MISSING 或 console error。
- 代表性内容：轨迹版本 `052d3a8e-8a35-48ac-9e65-b95a86b42c99` 渲染真实 3 帧 canvas；Dataset 版本 `be02266a-7d4f-4ebb-9f28-3132855167d0` 渲染 `mat-1`/`mat-2`/`mat-3` 表格。
- 服务证据：`/health/runtime` 为 PostgreSQL/Redis/MinIO/Redis worker；`phase14r_operations_snapshot.py --same-stack --fail-on-attention` PASS，idle-in-transaction=0、pool checkedOut=0、队列深度=0、6 workers idle。
- 测试/检查：`phase14r-runtime-static-assets.mjs` PASS；未提交/未推送。
## P14R results document status normalization (2026-09-02)

- 状态：已完成
- 修改摘要：将 `AGENT2_PHASE14R_RESULTS.md` 顶部状态与文件末尾最终封板一致化为 `COMPLETE`，并标注历史 checkpoint 的 `PARTIAL` 不代表当前状态。
- 测试结果：文档一致性检查完成；未修改实现、数据库、服务或浏览器状态。
- 提交/CI：未提交、未推送。

### 前端构建刷新后的全路由复核（2026-09-03）

- 结果：通过；本轮成熟度总任务仍处理中。
- 证据：Console、Projects、Project Overview、Data、Research、Reports、Tasks、
  Notifications、Trash、Account、Admin、Model Settings 在 `390×844` 和
  `1280×720` 共 24 个组合全部 HTTP 200；页面级 overflow=0，console/page
  errors=0，HTTP 5xx=0。
- 运行状态：仅重启前端以刷新构建 chunk；PostgreSQL、Redis、MinIO、API、
  workers、Chrome 标签页均保持运行。
## Product maturity — legacy Report route P1 fix (2026-09-02)

- 状态：已完成
- 根因：历史 `job_*`/`run_*` 报告入口先探测现代报告接口，产生无意义 404，再降级到兼容页。
- 修复：`apps/web/app/components/ScientificReportRoute.tsx` 对 legacy 引用直接进入只读兼容报告路径；增加错误项目路由校正与测试覆盖。
- 验证：`ScientificReportRoute.test.tsx` 23 passed；生产构建通过；认证浏览器打开 `job_agent2_92fcd73e38034dcfbc7aa63fbcf2a70e`，无 Internal Server Error、console error/warn，科学结果最终加载。
- 服务状态：PostgreSQL/Redis/MinIO/API/6 workers 保持运行；未提交、未推送。

## Product maturity — mobile scientific table affordance fix (2026-09-02)

- 状态：已完成本轮 UI 修复（总产品成熟度任务仍处理中）
- 根因：科学表格已有横向滚动容器，但移动断点将 `.workspace-table-mobile-hint` 隐藏，右侧属性容易被误判为不可用或缺失。
- 修复：恢复移动断点提示，明确完整属性可左右滑动，并保留稳定样本身份与选择操作固定在左侧；未改变数据、选择语义或科学 authority。
- 验证：`WorkspaceArtifactGallery` + `ScientificWorkspaceShell` + `ScientificReportRoute` 窄回归 `53 passed`；前端全量 `108 files / 789 tests passed`；production build、typecheck、compileall、静态资源、`git diff --check` PASS；同栈 `/health/runtime` 与 operations snapshot PASS。
- 提交/CI：未提交、未推送；服务与浏览器标签页保持运行。

## Product maturity — repeated Viewer accessibility ids (2026-09-02)

- 状态：已完成本轮可访问性修复（总 Product Maturity Closure 仍继续处理中）
- 根因：多个科学 Viewer 同页渲染时共用 `viewer-limitations`，会造成重复
  DOM id 和错误的 `aria-labelledby` 关联。
- 修复：`ScientificViewerShell` 使用 React `useId` 为每个 Viewer 的限制
  区域生成稳定唯一标题 id；未改变科学内容或运行行为。
- 测试结果：`ScientificViewerShell.test.tsx` 与
  `ScientificObjectViewer.test.tsx` 合计 `3 passed`；typecheck 与
  `git diff --check` PASS；同栈服务快照无告警。
- 提交/CI 状态：未提交、未推送；服务、worker 与浏览器标签页保持运行。

## Dataset/Research recovery and exact-version navigation (2026-09-04)

- 状态：完成第二批 Dataset/Research/Viewer 交互审计修复，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/ProductPages.tsx`、
  `apps/web/app/components/ProductPages.test.tsx`、
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：为 Console 快速查看失败态和项目数据/概览读取失败态增加原地重试；
  为缺少不可变版本参数的科研对象 Data 路由增加 fail-closed 精确版本提示与返回
  项目数据入口，避免回退到 Dataset 面板造成误导。
- 测试结果：ProductPages `43 passed`；前端 typecheck PASS；
  `git diff --check` PASS。
- 提交/CI 状态：未提交、未推送；运行中的 API、前端、PostgreSQL、Redis、MinIO、
  workers 与浏览器标签页保持不变。

## 2026-09-03 — Product maturity UX batch

状态：已完成本批次，持续任务仍处理中。

修改摘要：
- Task Center/Notification Center 增加有界搜索、稳定排序和无匹配恢复。
- Scientific Report 增加移动端章节跳转，Dataset workbench 增加来源到结果
  的术语层级说明与精确项目 breadcrumb。
- 授权全局搜索覆盖 Dataset/Object/Result 语义内容并改进 Result 人类可读标题。
- 重建并重启当前生产前端实例；API、PostgreSQL、Redis、MinIO、workers
  与现有浏览器标签页保持运行。

测试结果：
- focused list/report/data：44 passed；
- full frontend：110 files / 803 tests passed；
- typecheck、production build、git diff --check：PASS；
- 同栈 runtime snapshot：PostgreSQL/Redis/MinIO healthy，queue=0，
  stale=0，idle-in-transaction=0，pool checked out=0；
- authenticated Chromium mobile route sweep：Console/Projects/Tasks/
  Notifications/Trash/Report 全部 HTTP 200，无 page error/5xx/overflow。

后续路由恢复与 Admin 确认对话框测试契约同步后，focused
Product/Data/Project/Task/Notification/Report/Admin 为 `101 passed`；
完整前端回归更新为 `110 files / 810 tests passed`。该数字取代本批次
早先的 803 记录。

提交/CI：未提交，未推送。

补充验证：
- Project Home 长列表采用渐进式“显示更多”，历史错误提供原地重新加载。
- 认证 Chromium 核心路由巡检：12 路由 × 3 前端实例 × 2 视口 = 72/72 HTTP 200；
  Internal Server Error、不可恢复交互提示、page error、console error、5xx、
  横向溢出均为 0。
- 当前 13 个 ScientificObject 的 Data/Version/Viewer 投影 26/26 成功，
  payload=READY、viewer support=PROFESSIONAL。

## Product maturity — Dataset authority boundary clarity (2026-09-04)

- 状态：完成 Dataset 详情页术语与信息架构澄清，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/DatasetWorkbenchPage.tsx`、
  `apps/web/app/components/DatasetWorkbenchPage.test.tsx`、
  `apps/web/app/globals.css`、`persistent/DESIGN_PROGRESS.md`。
- 修改摘要：增加可见的数据层级说明，区分 Dataset 来源范围、Profile 语义档案、
  ScientificObject/Version 科学身份与不可变状态、ScientificResult 分析事实；
  将“表格行数/可用能力/结果”等模糊标签改为记录数、可用分析、分析结果，并
  保持所有数据与版本 authority 不变。
- 测试结果：DatasetWorkbenchPage `1 passed`；前端 typecheck PASS；
  `git diff --check` PASS。
- 提交/CI 状态：未提交、未推送；API、前端、PostgreSQL、Redis、MinIO、
  workers 与浏览器标签页保持运行。

## Product maturity — authorized scientific semantic search and recovery (2026-09-03)

- 状态：完成全局科学语义搜索、结果标题可读性与搜索恢复入口批次；成熟度总任务仍处理中
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `tests/test_project_access.py`、`apps/web/app/components/ProductShell.tsx`、
  `apps/web/app/components/ProductShell.test.tsx`、
  `apps/web/app/components/workspace/ScientificWorkspaceShell.tsx`、
  `apps/web/app/workspaces/[workspaceId]/error.tsx`、`apps/web/app/globals.css`
  及产品审计/持久化记录。
- 修改摘要：在现有授权搜索边界内增加 Dataset sample/formula、对象版本元数据、
  ScientificResult 权威 bundle 与 grounded finding 文本命中；Result 标题优先
  显示权威研究问题或结果项标题，副标题保留短 Result ID/schema 版本；搜索和已
  保存检索失败均可原地重试；深层 workspace 错误态提供项目/控制台安全出口。
- 测试结果：`tests/test_project_access.py` 32 passed；前端全套
  `110 files / 799 tests passed`；typecheck、production build、Ruff、
  compileall、git diff --check PASS。认证内置浏览器 `390×844` 搜索 `mat-2`
  返回 14 项，Result/Research/Report 均可命中，首条 Result 打开精确
  ResearchTurn `92fcd73e-3803-4dcf-bc7a-a63fbcf2a70e`，无 5xx、console/page
  errors 或横向溢出。
- 提交/CI 状态：未提交、未推送；API 在本批次重启以加载最新搜索实现；
  PostgreSQL、Redis、MinIO、workers、前端服务与浏览器标签页保持运行。

## Product maturity — legacy browser alias recovery (2026-09-03)

- 状态：恢复历史浏览器标签页对应的 3013/3016 前端兼容入口；成熟度总任务仍处理中
- 修改文件：无产品代码新增；启动当前 `apps/web` 默认生产构建的两个兼容进程。
- 修改摘要：原有标签页 URL 保持不变，3013/3016 均代理同一 8005 API；历史报告
  路由可打开、章节与来源研究入口可见，未关闭任何服务或浏览器标签页。
- 测试结果：3013/3016 `/console` HTTP 200；3013 历史报告路由 HTTP 200，
  内置浏览器 console errors=0、页面未出现 Internal Server Error。
- 提交/CI 状态：未提交、未推送；PostgreSQL、Redis、MinIO、API、workers、
  3000/3013/3016 前端与浏览器标签页保持运行。

## Product maturity — 回收站空状态可达性微调 (2026-09-03)

- 状态：已完成；成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/TrashCenterPage.tsx`、
  `apps/web/app/components/TrashCenterPage.test.tsx`、`apps/web/app/globals.css`、
  `docs/agent2/product_maturity/ux-audit-global-product-2026-09-03.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：回收站空状态增加“查看项目 / 返回控制台”出口；移动端操作组
  保持可达、均分宽度，避免用户停留在无内容死路。
- 测试结果：TrashCenterPage `4 passed`；typecheck PASS；production build PASS；
  git diff --check PASS；认证 Chromium `390×844`、`1280×720` 均
  `200 / console errors=0 / HTTP 5xx=0 / page overflow=0`。
- 运行备注：构建后检测到旧前端 chunk 400，已只重启前端 `next start`；
  PostgreSQL、Redis、MinIO、API、workers 和 Chrome 标签页持续保留。
- 提交/CI：未提交、未推送。

## Product maturity — Dataset asset context clarification (2026-09-03)

- 状态：完成 Dataset 工作台心智模型微调，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/DatasetWorkbenchPage.tsx`、
  `apps/web/app/globals.css` 及审计/持久化记录。
- 修改摘要：新增数据资产工作台上下文说明与术语折叠，解释 Dataset、
  ScientificObject/Version、Profile、规范化资源和结果的关系；不改变 Data
  Platform authority、版本语义或分析执行路径。
- 测试结果：DatasetWorkbench `1 passed`；typecheck PASS；production build PASS；
  认证 Chromium 数据集真实路由在 `390×844`/`1280×720` 均无 5xx、console errors
  或横向溢出，真实结构查看器继续可用。
- 提交/CI 状态：未提交、未推送；服务、worker 与浏览器标签页继续保持运行。

## Product maturity — scientific viewer unavailable-state recovery (2026-09-02)

- 状态：已完成本轮可用性修复（总 Product Maturity Closure 仍继续处理中）
- 根因：精确版本 Viewer 在 payload 暂时不可用或请求失败时只有静态
  fallback，用户无法从当前页面重试，也缺少回到同一 object/version 来源
  页面核对元数据的明确出口。
- 修复：`ScientificObjectViewer` 增加 `重新读取来源` 与
  `查看来源与属性`；重试仅重新读取既有 viewer projection，保持 exact
  object/version，不创建 Job/ToolCall/Artifact/Result，不做 latest 替换。
- 修改文件：`apps/web/app/components/scientific-viewer/ScientificObjectViewer.tsx`、
  `apps/web/app/components/scientific-viewer/ScientificObjectViewer.test.tsx`、
  `persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`。
- 测试结果：Focused `ScientificObjectViewer.test.tsx` `1 passed`；服务
  `/health/runtime` 与同栈 operations snapshot 仍 PASS。
- 提交/CI 状态：未提交、未推送；API、PostgreSQL、Redis、MinIO、workers
  与浏览器标签页保持运行。总 Product Maturity Closure 继续处理中。

- 浏览器补充证据：当前生产构建验证端口 `3017` 的 `390x844` Dataset
  页面截图 `phase14r-viewer-retry-dataset-390x844.png`；精确数据表显示
  `mat-1 / mat-2 / mat-3`，浏览器 console/page error 均为空。

## Product maturity — authenticated current route sweep (2026-09-02)

- 状态：已完成当前运行时复核（总 Product Maturity Closure 仍继续处理中）
- 修改摘要：使用当前认证会话与 Chromium 对项目、任务、通知、回收站以及
  16 个项目的概览/数据/研究/报告路由进行重新扫描；未修改科学 authority、
  数据库记录或服务。
- 浏览器结果：`16` 个项目、`52` 条路由全部正常；Internal Server Error、
  Application error、ChunkLoadError、不可用 payload 文案和 console/page
  error 均为 `0`。
- 结论：当前同栈验收路径未复现用户截图中的实时服务故障；历史缺失原始
  MinIO 字节的记录仍按 fail-closed typed 状态处理，不伪造恢复内容。
- 提交/CI 状态：未提交、未推送；API、PostgreSQL、Redis、MinIO、workers
  与浏览器标签页保持运行。

## Product maturity — persisted Plotly Figure/Table preview (2026-09-02)

- 状态：已完成共享 Report 预览映射修复（总 Product Maturity Closure 仍继续处理中）
- 根因：持久化 Plotly 图使用 `data[]` 而不是预览原先支持的 `series[]`；
  MSD 与 diffusion Table Artifact 使用科学数组/嵌套拟合结构而不是通用
  `rows[]`，导致真实数据被显示为空占位。
- 修复文件：`apps/web/app/components/ScientificReportArtifactPreview.tsx`、
  `apps/web/app/components/ScientificReportArtifactPreview.test.tsx`。
- 确定性投影：支持 Plotly `data[]` 有界有限点、`trajectory.msd` 的滞后/
  总量/方向数组，以及 `trajectory.diffusion` 的拟合窗口/扩散系数/R²/
  RMSE/诊断字段；不重新计算科学结果。
- 测试：`ScientificReportArtifactPreview` `5 passed`。
- 认证浏览器：独立当前构建 `3019` 上，Report
  `agent2_report_e54681009a0e49abe371247d9053ce61` 展开后为 `2 SVG + 2
  tables`，空预览 `0`，Internal Server Error `0`，Artifact 读取失败 `0`，
  console/page errors `0`。
- 提交/CI 状态：未提交、未推送；现有 API、数据库、对象存储、worker 与
  Chrome 标签页保持运行。

## Product maturity — Report Figure layout correction (2026-09-02)

- 状态：已完成报告图形布局修复（总 Product Maturity Closure 仍继续处理中）
- 根因：Figure 预览组件被报告图卡的 CSS Grid 自动放入窄索引列，
  导致真实 SVG 退化成窄竖条并留下大块空白。
- 修复文件：`apps/web/app/globals.css`，将
  `.scientific-report-figure-plate > .scientific-report-artifact-preview`
  固定到内容列并限制宽度。
- 认证浏览器验证：当前独立生产构建 `3020` 在 `1280x720` 和 `390x844`
  均显示 `2 SVG + 2 tables`，空预览 `0`，页面宽度分别保持
  `1280/1280`、`390/390`，console/page errors `0`。
- 提交/CI 状态：未提交、未推送；API、PostgreSQL、Redis、MinIO、workers
  与 Chrome 标签页保持运行。

## Product maturity — report Artifact inline preview (2026-09-02)

- 状态：已完成本轮 UI/数据可用性修复（总 Product Maturity Closure 仍继续处理中）
- 根因：现代 Report 的 Figure/Table 仅展示描述牌和权威 Artifact 外链，用户看到的主体像图片占位，无法在报告内快速核对持久化科学内容。
- 修复：新增 `apps/web/app/components/ScientificReportArtifactPreview.tsx`，按需通过现有 Artifact content API 读取 JSON；Figure 投影为有界 SVG，Table 投影为最多 24 行/8 列的 typed preview，保留完整 Artifact 外链。只读读取不触发科学重算。
- 修改文件：`apps/web/app/components/ScientificReportArtifactPreview.tsx`、`apps/web/app/components/ScientificReportArtifactPreview.test.tsx`、`apps/web/app/components/ScientificReportRoute.tsx`、`apps/web/app/globals.css`。
- 测试结果：`ScientificReportRoute.test.tsx` 23 passed；`ScientificReportArtifactPreview.test.tsx` 3 passed；TypeScript typecheck PASS；生产 build PASS；同栈认证浏览器报告 `agent2_report_19a0d0c261c28577101de81532464893` Figure 2 点/Table 1 行预览 PASS，error/warn 日志为空。
- 服务/浏览器：PostgreSQL、Redis、MinIO、API、workers 与既有 Chrome 标签页保持运行；未删除文件、未提交、未推送。

## Product maturity — shared filter hierarchy fix (2026-09-02)

- 状态：已完成本轮 UI 修复（总产品成熟度任务仍处理中）
- 根因：报告与回收站筛选按钮未覆盖全局 `button` 主操作样式，四个状态筛选均呈现为 teal 主按钮。
- 修复：新增共享 `.product-filter-row` / `.product-filter-button` 样式，仅 active filter 使用强调填充，其他 filter 使用描边胶囊；移动端保留 44px 触控高度。
- 验证：重建 `.next-prod-maturity-20260902` 并重载 3013；认证浏览器报告页实测 active/inactive 视觉状态正确，无 ISE 或 console error；此前全量前端 `108 files / 789 tests passed`、build、typecheck、compileall、静态资源与 diff check 均通过。
- 提交/CI：未提交、未推送；服务与浏览器标签页保持运行。

## Product maturity — exact scientific payload recovery and same-stack runtime alignment (2026-09-03)

- 任务：Materials Intelligence Platform — Product Maturity Closure
- 状态：处理中（本批次完成，产品成熟度总任务继续）
- 完成时间：2026-09-03T17:20:00+08:00
- 修改文件：
  - `docs/agent2/product_maturity/ux-audit-scientific-data-availability-2026-09-03.md`
  - `docs/agent2/product_maturity/evidence/exact_minio_reference_recovery_2026-09-03.json`
  - `docs/agent2/product_maturity/evidence/exact_minio_availability_verification_2026-09-03.json`
  - `scripts/restore_exact_minio_references.py`
  - `scripts/phase14r_start_api.ps1`
  - `scripts/phase14r_start_workers.ps1`
  - `scripts/phase14r_operations_snapshot.py`
  - `apps/api/mdi_api/artifact_storage.py`
  - `tests/test_phase5_runtime_infrastructure.py`
- 修改摘要：确认核心服务均运行；恢复 acceptance scope 缺失的 1 个精确
  ScientificObjectVersion payload 与 10 个精确 Artifact keys，逐项验证大小/
  SHA-256/readback；修复 S3 existence 错误分类与 response body 关闭；将
  Phase 14-R 专用 API/Workers 统一到 Redis DB 13，并使 same-stack 运维快照
  覆盖陈旧父进程环境变量。
- 测试结果：
  - acceptance ScientificObjectVersion `13/13` exact payload present；
    acceptance MinIO Artifact `241/241` exact payload present；
  - `tests/test_phase5_runtime_infrastructure.py` selected `2 passed`；
  - `tests/test_phase8c_planner_read_api.py` `9 passed`；
  - `compileall`、`git diff --check` PASS；
  - same-stack operations snapshot `status=ok`, `workerCount=6`,
    `totalQueued=0`, `idleInTransaction=0`, `pool.checkedOut=0`；
  - `/health/runtime`: PostgreSQL/Redis/MinIO/Redis-worker/DeepSeek all `ok`.
- 提交/CI 状态：未提交、未推送；保留所有既有用户文件、浏览器标签页和服务。

## Product maturity — source-unavailable Viewer copy refinement (2026-09-03)

- 状态：已完成窄范围 UI 可用性修复（产品成熟度总任务仍处理中）
- 修改文件：`apps/web/app/components/scientific-viewer/ScientificViewerShell.tsx`、
  `apps/web/app/components/scientific-viewer/ScientificObjectViewer.tsx`、
  `apps/web/app/components/scientific-viewer/ScientificObjectViewer.test.tsx`、
  `docs/agent2/product_maturity/ux-audit-scientific-data-availability-2026-09-03.md`
- 修改摘要：将缺源状态中的内部术语 `payload` 改为用户可理解的
  “原始科学数据”；在已确认缺源时优先提供“查看来源与属性”，保留
  “重新读取来源”为次要动作，避免误导性重复重试。
- 测试结果：Viewer focused `3 passed`；前端 typecheck PASS；touched Ruff
  与 `git diff --check` PASS；同栈 API/Artifact/Viewer/Report smoke
  endpoints 均 HTTP 200。
- 提交/CI 状态：未提交、未推送；PostgreSQL、Redis、MinIO、API、workers
  及现有浏览器标签页保持运行。

## Product maturity — final regression after exact payload recovery (2026-09-03)

- 状态：当前批次回归完成，产品成熟度总任务仍处理中
- 同栈运行时：frontend `3000`、API `8005`、PostgreSQL qualification
  `55434`、Redis `6379`、MinIO `9000/9001`，source MinIO `9102` 均保持监听；
  API health 为 PostgreSQL/Redis/MinIO/Redis worker/DeepSeek `ok`。
- 可见性验证：acceptance scope 的 ScientificObjectVersion payload
  `13/13`、MinIO Artifact `241/241`，缺失 `0`、checksum mismatch `0`；
  Viewer、Artifact content、Scientific Report API/页面入口均返回 HTTP 200。
- 回归：前端全量 `110 files / 796 tests passed`；后端全量
  `1982 passed / 84 skipped`；Viewer/运行时/Planner focused
  `28 passed / 1 historical compatibility skip`；typecheck、compileall、
  touched Ruff、git diff check 均 PASS。
- UI：缺源状态改为面向研究者的“原始科学数据”文案，并将来源属性查看
  作为主操作；未改变 fail-closed、精确版本或科学权威语义。
- 提交/CI 状态：未提交、未推送；按用户要求保留 API、workers、数据库、
  Redis、MinIO、source MinIO 与浏览器标签页。

## Product maturity — whole-product UI audit and mobile Research reachability (2026-09-03)

- 状态：已完成共享滚动根因修复，成熟度总任务仍处理中
- 修改文件：`apps/web/app/globals.css`、
  `docs/agent2/product_maturity/ux-audit-global-product-2026-09-03.md`、
  `persistent/DESIGN_PROGRESS.md`
- 修改摘要：基于真实 Chromium 的桌面/移动路由审计，记录 16 项可复核观察，
  将移动 Research 工作台在窄屏上的固定高度/`overflow:hidden` 裁切修复为
  页面纵向滚动 + 有界会话历史；不改变科学表格的稳定身份、横向滚动和
  精确 provenance。
- 测试结果：Research/ProductShell focused `83 passed`；typecheck PASS；
  production build PASS；新前端实例 `3014` 的真实浏览器复测中，Research
  移动端页面可滚动至 `开始分析`，`body.scrollHeight=933`、无横向溢出、
  console errors=0、5xx=0；全站当前路由批次 12/12 HTTP 200。
- 提交/CI 状态：未提交、未推送；3000 原有前端、API、PostgreSQL、Redis、
  MinIO、6 个 worker 与浏览器标签页均保留；3014 为本轮复测前端实例。

## Product maturity — exact Dataset source recovery and route re-audit (2026-09-03)

- 状态：完成本轮资源恢复与浏览器复核，成熟度总任务仍处理中
- 修改文件：`apps/web/app/lib/scientific-viewer-api.ts`、相关审计与
  `persistent/DESIGN_PROGRESS.md`；活动 MinIO 恢复了 Dataset 原始源与规范化
  元数据，未修改 PostgreSQL 科学权威。
- 证据：`dataset_0002_cb403e1b78f54d32` 的 `si.cif` 441 字节 SHA-256
  `4aeaf0107a36ef4bf587da1e52d20ca2739063dd5a548dcb3dac29efc0331198`；
  `structure.json` 832 字节 SHA-256
  `067bc07a01eb9d27021cfcb9406a6358b7b0c81910ca4beb2531dfbfc35217a6`；
  DurableObjectStoreResolver 成功解析 1 个结构。
- 测试结果：前端生产构建 PASS；科学 Viewer focused `48 passed`；真实认证
  Chromium Dataset 页面桌面/移动均无 console/page/HTTP 错误，页面横向溢出
  `0`，真实三维结构 Viewer 可见。
- 提交/CI 状态：未提交、未推送；API、前端、PostgreSQL、Redis、MinIO、
  6 个 worker 与浏览器标签页继续保持运行。

## Product maturity — shared lifecycle/report navigation refinement (2026-09-03)

- 状态：完成一批共享 UI 改进，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/ProductShell.tsx`、
  `apps/web/app/components/ScientificReportRoute.tsx`、
  `apps/web/app/globals.css` 及持久化记录。
- 修改摘要：在全局顶栏增加直接“回收站”入口；移动端压缩为带 tooltip、
  accessible name 的紧凑控制；报告章节横向导航增加移动端可发现提示，
  保持原有锚点、报告快照和科学 provenance 不变。
- 测试结果：ProductShell/ScientificReport focused `40 passed`；production
  build PASS；真实认证 Chromium 报告移动页显示章节提示，回收站入口可见，
  `scrollWidth === clientWidth === 390`。
- 提交/CI 状态：未提交、未推送；服务、worker 与浏览器标签页保持运行。

## Product maturity — shared list/report action refinement (2026-09-03)

- 状态：完成本批共享 UI 改进，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/NotificationCenterPage.tsx`、
  `apps/web/app/components/ScientificReportRoute.tsx`、
  `apps/web/app/components/AdminCenterPage.tsx`、`apps/web/app/globals.css`
  及审计/持久化记录。
- 修改摘要：任务与通知列表新增显式渐进加载；报告首屏主次操作分组并优化移动布局；
  管理中心无权限状态补充控制台恢复入口；未改变科学 authority、生命周期 API 或历史
  provenance。
- 测试结果：Task/Notification `8 passed`；Report/Admin `27 passed`；
  typecheck PASS；production build PASS；认证 Chromium 桌面/移动复核无横向溢出、
  console errors=0，渐进加载入口可见。
- 提交/CI 状态：未提交、未推送；API、前端、PostgreSQL、Redis、MinIO、worker 与
  浏览器标签页继续保持运行。

## Product maturity — mobile scientific table affordance (2026-09-03)

- 状态：完成移动表格可发现性微调，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/ProductPages.tsx`、`apps/web/app/globals.css`
  及审计/持久化记录。
- 修改摘要：Data 科学属性表在移动端显示明确横向滚动与行选择提示；表格列、语义
  行身份、授权和 scientific authority 均保持不变。
- 测试结果：ProductPages `40 passed`；typecheck PASS；生产构建 PASS；认证
  Chromium 当前 Data 路由 `390×844` 无横向溢出、console errors=0。
- 提交/CI 状态：未提交、未推送；服务、worker 与浏览器标签页保持运行。

## Product maturity — Dataset asset context and SPA navigation check (2026-09-03)

- 状态：完成 Dataset 语义分层与产品导航复核，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/DatasetWorkbenchPage.tsx`、相关审计与
  `persistent/DESIGN_PROGRESS.md`。
- 修改摘要：Dataset 工作台明确导入容器、ScientificObject/Version、Profile、
  规范化资源和结果的职责边界；认证浏览器实测 Data → Research 点击导航时
  document request 增量为 `0`，保持 App Router 切换，不退化为整页重载。
- 测试结果：DatasetWorkbench `1 passed`；typecheck PASS；production build PASS；
  认证 Chromium 数据集真实路由在 `390×844`/`1280×720` 无 5xx、console errors
  或横向溢出。
- 提交/CI 状态：未提交、未推送；API、前端、PostgreSQL、Redis、MinIO、worker 与
  浏览器标签页保持运行。


## Product maturity — current-worktree verification (2026-09-03)

- 状态：本批次当前工作树验证完成，成熟度总任务仍处理中
- 测试结果：图例微调后重新执行完整前端回归，`110 files / 796 tests passed`；
  operations snapshot 仍为 `status=ok`、PostgreSQL/Redis/MinIO ready、6 workers、
  `totalQueued=0`、`idleInTransaction=0`、`pool.checkedOut=0`；`git diff --check`
  通过（仅报告既有 LF/CRLF 警告）。
- 运行状态：API `8005`、前端 `3000`、PostgreSQL `55434`、Redis `6379`、
  MinIO `9000/9001` 与 retained source `9102` 均保持监听；Chrome 标签页未关闭。
- 提交/CI 状态：未提交、未推送；neat-freak 候选临时文件/旧日志仅完成只读盘点，
  未进行删除。

## Product maturity — mobile account section navigation (2026-09-03)

- 状态：完成账户长页面导航微调，成熟度总任务仍处理中
- 修改文件：`apps/web/app/globals.css` 及审计/持久化记录。
- 修改摘要：账户页移动端目录改为吸顶导航，滚动时保持个人资料、登录会话、
  密码和停用账户入口可达；未改变认证、会话或账户生命周期 API。
- 测试结果：UserCenter `6 passed`；typecheck PASS；production build PASS；
  认证 Chromium `390×844` 实测目录 `position=sticky/top=56px`，滚动后仍固定在
  `y=56`，页面横向溢出 `0`、console errors=0。
- 提交/CI 状态：未提交、未推送；服务、worker 与浏览器标签页保持运行。

## Product maturity — multi-series scientific figure preview (2026-09-03)

- 状态：完成报告图表预览质量修复，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/ScientificReportArtifactPreview.tsx`、
  `apps/web/app/globals.css` 及审计/持久化记录。
- 修改摘要：持久化 Figure 预览保留有限多序列、正负值基线、坐标标题和序列
  边界，继续只读投影 Artifact，不创建 Job/Artifact/Result。
- 测试结果：ScientificReportArtifactPreview `5 passed`；typecheck PASS；
  production build PASS；认证 Chromium 真实报告页面点开预览后显示 `2` 条序列、
  `2` 个有限点，横向溢出 `0`、console errors=0、5xx=0。
- 提交/CI 状态：未提交、未推送；API、前端、PostgreSQL、Redis、MinIO、worker 与
  浏览器标签页保持运行。

## Product maturity — mobile scientific scroll affordances (2026-09-03)

- 状态：完成共享表格/报告章节横向可见性微调，成熟度总任务仍处理中
- 修改文件：`apps/web/app/globals.css`。
- 修改摘要：为通用科学表格、Dataset 验证表与移动报告章节导航补充可见滚动阴影、
  稳定滚动条颜色和键盘聚焦反馈；不裁剪列、不改变稳定样本身份、不改变科学
  authority 或报告锚点。
- 测试结果：ProductPages/ScientificReportRoute/ScientificReportArtifactPreview
  定向 `68 passed`；全前端 `110 files / 796 tests passed`；typecheck PASS；
  production build PASS；认证 Chromium `390×844` Data 表 `scrollWidth=759`
  且页面溢出 `0`、报告章节 `scrollWidth=573` 且页面溢出 `0`，console errors=0、
  HTTP 5xx=0。
- 提交/CI 状态：未提交、未推送；API、前端、PostgreSQL、Redis、MinIO、worker 与
  浏览器标签页保持运行。

## Product maturity — scientific figure legend clarity (2026-09-03)

- 状态：完成稀疏 Figure 预览的序列辨识增强，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/ScientificReportArtifactPreview.tsx`、
  `apps/web/app/globals.css`。
- 修改摘要：在确定性只读 Figure 预览下方增加序列图例与每条序列的有限点数，
  避免稀疏数据被误解为空白或加载失败；没有新增计算、Artifact 或 Result。
- 测试结果：ScientificReportArtifactPreview/ScientificReportRoute `28 passed`；
  typecheck PASS；production build PASS；认证 Chromium 桌面报告真实 Artifact
  预览显示 `All sites / 1 个点`、`Si / 1 个点`，SVG=1，页面溢出 `0`，
  console errors=0、HTTP 5xx=0。
- 提交/CI 状态：未提交、未推送；服务、worker 与浏览器标签页保持运行。

## Product maturity — Account/Admin control-safety batch (2026-09-03)

- 状态：完成账户与平台管理控制面修复，成熟度总任务仍处理中
- 修改文件：`apps/web/app/components/UserCenterPage.tsx`、
  `apps/web/app/components/UserCenterPage.test.tsx`、
  `apps/web/app/components/AdminCenterPage.tsx`、
  `apps/web/app/components/AdminCenterPage.test.tsx`、
  `apps/web/app/globals.css`，以及对应持久化记录。
- 修改摘要：账户与会话读取增加原地重试；管理员账户角色/启停和项目成员角色/
  移除改为带后果说明的显式确认；用户/项目目录增加 bounded continuation loading；
  邀请凭证复制增加成功与手动复制失败反馈。未改变科学 authority、版本、
  provenance 或服务端授权。
- 测试结果：Account/Admin focused `13 passed`；TypeScript typecheck PASS；
  `git diff --check` PASS；同栈 `/health/runtime` 为 PostgreSQL/Redis/MinIO/
  Redis worker，认证 Chromium 账户页 `390×844` HTTP 200、横向溢出 0、console
  errors 0；普通用户访问管理中心正确显示无平台管理权限。
- 提交/CI 状态：未提交、未推送；API、前端、PostgreSQL、Redis、MinIO、
  worker 与浏览器标签页保持运行。

后续完整回归：生产构建后 full frontend `110 files / 810 tests passed`；
认证 Chromium 核心路由 `24/24` HTTP 200（桌面/移动），无 page/console error、
5xx 或全局横向溢出。账号管理员后端 focused `8 passed`。

## Product maturity — 当前报告/表格/移动布局复核（2026-09-03）

- 状态：完成本批表格、报告 Artifact 预览与不可用状态的真实浏览器复核；成熟度总任务仍处理中。
- 修改文件：`apps/web/app/components/ScientificReportArtifactPreview.tsx`、
  `apps/web/app/components/ScientificReportRoute.tsx`、`apps/web/app/components/
  dataset-explorer/DatasetMaterialsExplorerPanel.tsx` 及对应测试/样式，另有
  审计与持久化文档。
- 浏览器证据：认证内置浏览器 `3000` 报告详情页正常，图表预览显示
  `All sites / 1 个点` 与 `Si / 1 个点`，表格预览显示 typed headers、caption、
  精确版本；`390x844` Dataset 表显示 3/3 行和稳定 sample IDs，页面宽度
  `375/375/375`，全局溢出 `0`，console error/warn `0`。
- 测试结果：full frontend `110 files / 813 tests passed`；后端关键回归
  `56 passed, 1 skipped`；production build、typecheck、compileall、`uv lock --check`、
  `git diff --check` PASS；同栈 operations snapshot PostgreSQL/Redis/MinIO healthy，
  worker `6 idle`、queue depth `0`、idle-in-transaction `0`。
- 提交/CI 状态：未提交、未推送；API、前端、PostgreSQL、Redis、MinIO、worker 与
  浏览器标签页保持运行。临时文件与日志仅完成候选识别，等待用户明确确认再执行删除。

- 追加验证：当前认证浏览器桌面/移动核心路由矩阵 `24/24` 全部 HTTP 200，
  `Application error`、Internal Server Error、console error、5xx 与全局溢出均为
  `0`；项目 13 个精确对象/版本入口桌面+移动 `26/26` 成功。缺失稳定 sample
  identity 的历史表格仍可读但不可选择，保持 fail-closed，不以行号替代科学身份。

## Product maturity — 导航/研究控制/科学表面批量修复（2026-09-03）

- 状态：当前批次实现与回归完成，成熟度总任务继续处理中。
- 修改摘要：品牌/控制台导航统一；顶层路由 loading frame；Research Continue
  精确 Result 复用；PLAN_READY/Stop 竞态收敛；Electronic/Phonon/Volumetric
  大数组安全渲染与表格可访问性语义。
- 测试结果：相关前端聚焦 `99 passed`；typecheck、production build、compileall、
  `uv lock --check`、`git diff --check` PASS；operations snapshot 显示
  PostgreSQL/Redis/MinIO `ok`，6 workers idle，queue depth 0，
  idle-in-transaction 0。
- 提交/CI：未提交、未推送；API、前端、数据库、Redis、MinIO、worker 和浏览器
  标签页保持运行。临时文件与日志只完成候选扫描，按 neat-freak 规则等待明确确认后删除。
- 追加浏览器验证：当前构建在 `3018` 端口认证运行，桌面核心路由 `11/11`、
  移动 `11/11` 全部无 page/console error、Internal Server Error 或全局溢出；
  `390x844` 项目导航“控制台”保持单行可读。未停止既有服务或关闭原有标签页。

## Product maturity — 数据层级与导航感知性能批次（2026-09-04）

- 状态：已完成本批实现与验证，成熟度总任务继续处理中。
- 修改摘要：Data Navigator 增加 Dataset 与 Scientific Object/Version 的权威
  层级说明；项目历史支持已解析快照复用，Console 预热首个活动项目并显式
  预取继续研究路径，减少导航后二次等待。保留精确版本、历史 fail-closed、
  服务与浏览器现状，不引入新的科学 authority。
- 修改文件：`apps/web/app/components/ProductPages.tsx`、
  `apps/web/app/components/ProductPages.test.tsx`、
  `apps/web/app/components/ProjectHome.tsx`、
  `apps/web/app/lib/planner-api.ts`、`apps/web/app/globals.css`，
  `persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`。
- 测试结果：`ProductPages + ProjectHome + ProductShell = 69 passed`；
  `npm run typecheck`、生产构建、`git diff --check` 通过。当前构建在
  `127.0.0.1:3020`，认证浏览器数据页桌面层级提示可见，移动端
  `document/body = 375/375`，无 page/console error。
- 提交/CI：未提交、未推送；PostgreSQL、Redis、MinIO、workers 与既有
  Chrome/内置浏览器标签页保持运行。

## Product maturity — Research 上下文完整审计可见性（2026-09-04）

- 状态：已完成本批实现与验证；成熟度总任务继续处理中。
- 修改摘要：ContextManifest 在长清单场景默认显示前 8 项，并提供可访问的
  “查看全部上下文（N 项）/收起上下文列表”控制；ResearchTurn 切换时自动收起。
  该操作仅改变只读呈现，不改变上下文选择、科学结果或执行。
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/globals.css`、
  `persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`。
- 测试结果：ResearchPages `69 passed`；`npm run typecheck`、`git diff --check` PASS。
- 提交/CI：未提交、未推送；现有 API、worker、PostgreSQL、Redis、MinIO 与浏览器
  标签页保持运行。

## Product maturity — Report/Artifact 展示与完整回归（2026-09-04）

- 状态：完成本批展示层修复与当前工作树完整回归；成熟度总任务仍处理中。
- 修改摘要：Report 每条主要发现支持折叠查看精确 ScientificResult、对象/版本、
  fact/evidence/finding refs；Artifact Gallery 为 `STATIC_METADATA` 与
  `DOWNLOAD_ONLY` 契约增加明确的元数据/安全下载状态，避免图片/HTML 资源被
  猜测或执行。
- 浏览器：当前生产构建 `127.0.0.1:3021` 的认证报告页桌面宽度
  `1265/1265`、移动宽度 `375/375`，主要发现依据入口可见；alert、Internal
  Server Error 与全局 overflow 均为 `0`。
- 测试：完整前端 `110 files / 823 tests passed`；完整后端
  `1983 passed / 84 skipped / 189 warnings`；typecheck、production build、
  compileall、`uv lock --check`、`git diff --check` PASS。
- 服务/运行时：API `8005`、PostgreSQL、Redis、MinIO、6 workers 与现有浏览器
  标签页保持运行；未提交、未推送、未删除用户文件或历史证据。
- 状态边界：Phase 14-R 仍为 `PARTIAL`；capability-wide real-user acceptance、
  retention/export/operations maturity、release CI 与临时文件清理确认仍未
  全部闭合。历史缺失 payload 继续按 fail-closed 展示。

- 视觉复核：`3021` 报告页桌面保持“来源研究”为主行动、导出为次行动，
  章节导航为单一横向滚动 owner；`390x844` 下标题、操作组、章节导航和正文
  均可达，章节导航右侧渐隐提示仍可见，页面无全局横向溢出。

## Product maturity — ContextManifest 读取恢复（2026-09-04，第二批）

- 状态：已完成本批实现与验证；成熟度总任务继续处理中。
- 修改摘要：ResearchPages 对 ContextManifest 增加有界读取状态。读取失败时明确
  告知研究者并提供“重新读取上下文”原地重试；成功后恢复同一只读清单。
  该动作不改变 ContextManifest 内容、ScientificResult、Result、来源版本或
  科学执行，不把暂时不可读误判为无上下文。
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`、
  `persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`。
- 测试结果：ResearchPages `70 passed`；未提交、未推送。
- 运行状态：API、PostgreSQL、Redis、MinIO、workers 与现有浏览器标签页保持运行。

## Product maturity — 回收站读取恢复（2026-09-04，第二批）

- 状态：已完成本批实现与验证；成熟度总任务继续处理中。
- 修改摘要：Trash Center 在回收站库存读取失败时提供明确的“重新加载回收站”
  原地恢复动作；重试仅重新获取同一授权搜索投影，失败期间不会改变任何
  Project/Dataset/Research/Report 生命周期或科学 provenance。
- 修改文件：`apps/web/app/components/TrashCenterPage.tsx`、
  `apps/web/app/components/TrashCenterPage.test.tsx`、
  `persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`。
- 测试结果：TrashCenter + ResearchPages `75 passed`；未提交、未推送。
- 运行状态：API、PostgreSQL、Redis、MinIO、workers 与现有浏览器标签页保持运行。
## Product maturity — recovery-control verification (2026-09-04)

- 状态：部分完成（Product Maturity Closure umbrella 继续处理中）
- 修改摘要：
  - Research ContextManifest 读取失败可在原地重新读取同一持久化上下文；
  - Trash Center 读取失败可原地重新加载授权回收站清单；
  - 两条恢复路径均不创建 Job、ToolCall、Artifact、ScientificResult，也不改变生命周期。
- 测试结果：
  - `ResearchPages.test.tsx`: `70 passed`
  - `TrashCenterPage.test.tsx`: `5 passed`
  - focused total: `75 passed`
  - frontend typecheck: `PASS`
- 运行状态：PostgreSQL、Redis、MinIO、API、workers、当前 production
  frontend 与浏览器标签页保持运行。
- 提交/CI：未提交、未推送；当前批次未执行新的 exact-SHA release。
- 剩余：capability-wide human acceptance、retention/export/operations maturity、
  安全清理确认和新的 Phase 14-R release gate。

## Product maturity — Research 主操作停止控制（2026-09-04）

- 状态：已完成本批实现与验证；Product Maturity Closure umbrella 继续处理中。
- 修改摘要：当精确 ResearchTurn 处于 planning/running 时，研究输入区主操作
  从不可点击的处理中按钮切换为可发现的“停止研究”。该动作复用现有服务端
  取消与 durable terminal-state reconciliation，不删除已提交的有效部分输出，
  也不新增前端取消 authority。
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/globals.css`、
  `persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、
  `AGENT2_PHASE14R_RESULTS.md`。
- 测试结果：ResearchPages `71 passed`；frontend typecheck `PASS`。
- 提交/CI：未提交、未推送；API、PostgreSQL、Redis、MinIO、workers 与
  浏览器标签页保持运行。

## Product maturity — R7/R8 研究任务可查找身份（2026-09-04）

- 状态：已完成本批实现与验证；Product Maturity Closure umbrella 继续处理中。
- 审计：新增
  `docs/agent2/phase14r/ux-audit-r7-r8-search-task-recovery-2026-09-04.md`；
  确认 Global Search/已保存检索与 Task/Notification 恢复已有正确授权边界，
  无需新建搜索索引或任务 authority。
- 修改摘要：现有 Job → ResearchTurn → user message 关系在同一 bounded SQL
  task-feed projection 中增加最多 180 字符的 `researchQuestion`；任务与通知
  以真实研究问题作为标题和查找文本，并显示持久化更新时间。精确 Turn 路由、
  cross-project authorization、legacy read-only、停止/重试/重连语义不变。
- 修改文件：`apps/api/mdi_api/repositories.py`、
  `apps/api/mdi_api/workspaces.py`、`apps/web/app/lib/workspace-api.ts`、
  `apps/web/app/lib/task-center-data.ts`、`apps/web/app/components/TaskCenterPage.tsx`、
  `apps/web/app/components/NotificationCenterPage.tsx`、对应测试与 Phase14-R 证据文档。
- 测试结果：Workspace/task-feed backend `15 passed`；Task/Notification/task-data
  frontend `16 passed`；frontend typecheck、touched Ruff、`git diff --check` PASS；
  1/5 个 Job 的 task-feed 查询数均保持 `2`。
- 提交/CI：未提交、未推送；没有停止 API、PostgreSQL、Redis、MinIO、workers
  或浏览器标签页。
- 剩余：生产规模分页、外部 push 通知与 Phase 14-R 全量真人验收不在本批 PASS
  声明内。

## Product maturity — task clarity, stop control and latest regression (2026-09-04)

- 状态：部分完成（umbrella task 继续处理中）
- 修改摘要：
  - Task/Notification 使用持久化 `Job → ResearchTurn → user message`
    关系显示真实研究问题和更新时间，并支持本地查找；
  - Research 处于 planning/running 且已有持久化 Turn 时，主提交操作切换为
    “停止研究”，复用服务器取消 authority；
  - 最新 worktree production build 运行于 `127.0.0.1:3023`，未停止旧实例。
- 测试结果：
  - full frontend: `110 files / 826 tests passed`
  - Research: `71 passed`
  - Task/Notification frontend: `16 passed`
  - focused backend task-feed: `21 passed`
  - typecheck/build/Ruff/diff: `PASS`
- 运行状态：
  - PostgreSQL `active/idle/idle-in-transaction = 1/5/0`
  - Redis `6` workers idle，queue depth `0`
  - MinIO healthy，resource alerts `0`
- 提交/CI：未提交、未推送。
- 剩余：capability-wide human acceptance、provider-scale recovery/performance、
  retention/export/operations review、safe cleanup confirmation 和 exact-SHA
  Phase 14-R release。

## Product maturity — neat-freak cleanup and knowledge reconciliation (2026-09-04)

- 状态：已完成本次授权的有限工作区清理；成熟度总任务继续处理中。
- 修改摘要：在用户确认后删除 12 个旧项目日志，共 `656,867` bytes；保留
  active API/worker/service/browser logs、科学数据、证据和 Codex runtime。
  同步记录到 `AGENT2_PHASE14R_RESULTS.md`、`persistent/DESIGN_PROGRESS.md`
  与 `persistent/TASK_BOARD.md`。
- 只读存储审计：C: 约剩 `80 MB`；报告为
  `E:\storage-analysis-phase14r-20260904\storage-report.html`。未删除
  Chrome、Codex、服务、科学数据或其他 C 盘目录。
- 测试/运行：API `8005`、前端 `3023`、PostgreSQL、Redis、MinIO 与
  workers 仍在运行；同栈健康保持通过；未提交、未推送。
- 状态边界：Phase 14-R 仍为 `PARTIAL`，全站真人验收、retention/export/
  operations maturity、safe C-drive cleanup confirmation 与 exact-SHA
  release gates 仍开放。

## Continuous optimization — Improvement #1 / CO-001 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Report Figure 虽保留权威 x 数值，但 SVG 按数组序号等距绘制，
  会错误表达非均匀科学采样的几何关系。
- 修改：以所有有界展示点的权威 numeric x-domain 统一映射坐标；分类或缺失
  x 才回退到序列位置；常量 x-domain 居中显示。不改变 Artifact、
  ScientificResult、单位或科学计算。
- 修改文件：`ScientificReportArtifactPreview.tsx` 及对应测试；持续优化
  backlog/log 和 persistent 状态文档。
- 验证：focused Vitest `7 passed`；新增 `[0, 0.1, 10]` 非均匀回归；
  frontend typecheck PASS；diff check PASS（仅 TASKS.md 既有 CRLF 提示）；
  authenticated same-stack 报告
  `agent2_report_e54681009a0e49abe371247d9053ce61` 页内图形加载 `92` 点，
  browser error `0`。
- 实际收益：报告内图形不再以错误的横向间距误导研究者，同时保持只读、
  零科学重计算边界。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #36 / CO-126 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Agent2 Research 的读取、创建和 dispatch 直连请求遇到 401 时
  只抛普通错误，没有触发现有 ProductShell 会话失效恢复，容易把认证
  失效误报为科学研究失败。
- 修改：在 Agent2 Research API 增加共享 `notifySessionExpired` 边界，
  三条请求路径统一派发 `mdi:session-expired`，同时保留原始错误。
- 验证：`agent2-research-api` 前端回归 `7 passed`；typecheck、diff
  check PASS。
- 实际收益：Research 主路径会一致进入登录恢复/returnTo 流程，不改变
  已持久化 Turn、Job、Result 或科学权限。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #35 / CO-125 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：安全 Planner 解释证据入口只校验来源 Job 的项目权限，未显式
  校验持久化解释/Result snapshot 的项目关系，异常关系可能成为跨项目
  证据读取边界。
- 修改：Agent2/legacy 证据投影增加有界 `projectId`；安全证据读取比较
  evidence Project 与 Job Project，关系不一致统一返回 404；新增同项目
  通过与跨项目 fail-closed 回归。
- 验证：授权 + Planner 读 API + 解释持久化回归 `26 passed`；compileall、
  diff check PASS。
- 实际收益：跨项目证据关系不再仅依赖 Job ID，篡改或陈旧关系不会泄漏
  证据内容或提供可枚举的权限差异。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #31 / CO-025 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：MinIO 仅有基础读写回归，未证明备份副本、哈希完整性和源对象
  缺失后的可恢复行为。
- 修改：新增唯一测试前缀的 server-side copy 流程，校验大小/SHA-256，
  删除测试源后从备份读取，再清理测试键。
- 验证：MinIO live focused `2 passed, 20 deselected`。
- 实际收益：对象缺失时系统有明确可恢复副本，不会静默重建或替换科学
  Artifact 内容。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #30 / CO-024 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：权威一致性扫描只有“当前零问题”证据，缺少确定性的断链分类和
  只读性回归。
- 修改：隔离数据库注入缺失 Job 的 ToolCall，断言只返回
  `ORPHAN_TOOL_CALL_JOB` 及精确 sample ID，并核对扫描前后记录数。
- 验证：authority consistency focused `2 passed, 10 deselected`；
  before=1、after=1。
- 实际收益：运维扫描不会被误用成隐式修复路径，断链诊断可精确自动化。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #29 / CO-023 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：数据库池测试只有 SQLite 重复建引擎，缺少真实 PostgreSQL 并发
  压力和 idle-in-transaction 检查。
- 修改：新增同栈 PostgreSQL 8 worker × 40 transaction 回归，断言 engine
  复用、checked-out 归零及 `pg_stat_activity` 的 idle-in-transaction 为零；
  未修改连接池配置。
- 验证：`tests/test_database_pool_lifecycle.py` 在
  `postgresql+psycopg` 下 `2 passed`。
- 实际收益：长时间重复请求的连接泄漏和事务未归还现在有真实服务证据。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #28 / CO-124 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：ToolCall、Artifact、Result、Report 与当前版本断链没有统一的只读
  诊断结果，死信/孤儿恢复缺少精确分类。
- 修改：operations snapshot 新增 `authorityConsistency`，检查七类断链，
  输出有界 sample IDs、typed issue code、`readOnly=true`，不执行修复。
- 验证：同栈 `MDI_RUN_INTEGRATION=1` 的 authority consistency 测试
  `2 passed, 9 deselected`；PostgreSQL/Redis/MinIO 均健康，`issueCount=0`。
- 实际收益：恢复和运维可以先发现断链再采取人工/安全修复，避免前端或
  自动任务猜测并修改科学 authority。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #27 / CO-123 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Artifact 同内容跨 worker 并发保存存在“先查后插”竞态，唯一约束
  异常会被重复投递暴露。
- 修改：`SqlAlchemyArtifactRepository.save` 在唯一冲突后读取已提交的同一
  job/storage/checksum Artifact；冲突绑定和其他 integrity failure 继续失败
  关闭；新增四 bundle/48 次 live 重复保存回归。
- 验证：真实 PostgreSQL `-k "concurrent_seq or duplicate_delivery"` 为
  `4 passed, 17 deselected`。
- 实际收益：重复 Artifact 投递不会生成第二条科学 provenance，也不会因
  正常并发竞态误报失败。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #26 / CO-022 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：独立 worker 同时第一次投递同一个 Job/Step 时，ToolCall 的
  “先查后插”竞态会把数据库唯一约束异常暴露给调用方。
- 修改：`SqlAlchemyToolCallRepository.save` 在唯一冲突后读取已提交的
  幂等 ToolCall 并收敛返回；不相关 integrity failure 和冲突绑定仍失败
  关闭；新增四 bundle/12 worker live 回归。
- 验证：真实 PostgreSQL `postgresql+psycopg` 下
  `-k "concurrent_seq or duplicate_delivery"` 为 `3 passed,
  17 deselected`。
- 实际收益：重复队列投递不会制造第二个 ToolCall，也不会因正常并发竞态
  误报失败；科学 authority 未改变。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #20 / CO-034 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：未知运行时 Presentation block 曾被文本检查误判为安全，随后静默
  丢弃，用户无法知道内容被拒绝且边界缺少明确证明。
- 修改摘要：`isSafePresentationBlock` 增加有界语义类型 allowlist；未知类型、
  HTML/script/危险 URL fail-closed；Presentation UI 显示拒绝数量但不暴露
  payload，不动态加载任何组件。
- 修改文件：`apps/web/app/lib/scientific-presentation.ts`、
  `scientific-presentation.test.ts`、`ScientificPresentationBlocks.tsx`、
  `ScientificPresentationBlocks.test.tsx`、连续优化证据与状态文档。
- 验证：focused frontend `23 passed`；typecheck PASS；git diff check PASS。
- 实际收益：不受支持的呈现内容不再静默丢失或进入潜在执行路径，研究者可见
  到有界安全状态，科学 authority 不变。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #21 / CO-038 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：服务启动分散，缺少统一 readiness 保护，重启时可能只看到端口而
  误以为真实运行时已切到 PostgreSQL/Redis/MinIO。
- 修改摘要：新增 `scripts/phase14r_start_stack.ps1`，幂等启动缺失的 API、
  worker、frontend，等待所有服务端口，并探测真实 `/health/runtime`；
  发现 SQLite/local/fake worker 时直接失败；不停止现有服务。
- 修改文件：`scripts/phase14r_start_stack.ps1`、连续优化证据与状态文档。
- 验证：`-CheckOnly -FrontendPort 3023 -TimeoutSeconds 10` 实测
  PostgreSQL/Redis/MinIO/Redis worker/DeepSeek 全部健康；git diff check PASS。
- 实际收益：下次恢复服务可使用一个可重复命令，不会把错误 runtime 当作同栈
  健康；现有服务和浏览器标签保持运行。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #19 / CO-122 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Viewer registry 将 `analysis.rdf`、`reciprocal.brillouin_zone`
  暴露为对象类型，但 ScientificObject authority 并未注册它们，导致历史/
  归档语义不明确。
- 修改摘要：从对象级 registry 移除两个 descriptor，新增显式
  `RESULT_ONLY_VIEWER_TYPES`；保持现有 Result/Artifact renderer 可用，不新增
  对象或第二科学 authority。
- 修改文件：`apps/api/mdi_api/scientific_viewers/registry.py`、
  `__init__.py`、`tests/test_agent2_phase9_viewers.py`、连续优化证据与状态文档。
- 验证：`pytest tests/test_agent2_phase9_viewers.py tests/test_agent2_contracts_registries.py -q`
  为 `38 passed`；touched Ruff PASS；git diff check PASS。
- 实际收益：对象级版本/归档边界与 Result-only renderer 边界一致，避免用户
  误以为 RDF/BZ 可直接作为 ScientificObject 生命周期管理。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #18 / CO-016 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Viewer API 的零重算断言原先仅覆盖 Structure，其他注册 Viewer 家族
  的只读行为缺少同等保护。
- 修改摘要：将授权 Viewer API 回归参数化至 `11` 个 ScientificObject-backed
  类型；每个类型检查 renderer identity、执行/Artifact/Result 表计数不变，
  并保留跨项目 `403` 与无元数据泄漏断言。
- 修改文件：`tests/test_agent2_phase9_viewers.py`、连续优化证据与状态文档。
- 验证：`pytest tests/test_agent2_phase9_viewers.py -q` 为 `28 passed`；
  touched Ruff PASS；git diff check PASS。
- 实际收益：Structure、Band/DOS、Phonon、Trajectory、XRD、Dataset/Table、
  Volumetric 的 Viewer 现在共享同一 persisted no-recompute 保护。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #10 / CO-121 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：缺失 ScientificResult 引用未纳入 Agent2 typed error mapping，导致
  context-memory pin 操作可能返回泛化 500。
- 修改：`_http_error` 将 `ScientificResultSnapshotNotFound` 归一化为稳定
  404；新增 API 回归保护安全错误详情。
- 修改文件：`apps/api/mdi_api/routers/agent2.py`、
  `tests/test_agent2_api.py`、连续优化证据文件。
- 验证：`pytest tests/test_agent2_api.py -q` 为 `27 passed`；touched Ruff
  PASS；`git diff --check` PASS。
- 实际收益：上下文控制遇到缺失 Result 时可恢复且不泄漏内部 500，科学与
  session memory authority 保持不变。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #11 / CO-010 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Research 依据条目只显示泛化来源标签，用户难以从结论回溯到
  字段、Artifact、ToolCall 与校验和。
- 修改：新增有界 `evidenceProvenanceSummary`，依据行显示字段定位、
  Artifact ID、ToolCall ID 与 SHA-256；保留既有结果内定位按钮。
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`、连续优化证据文件。
- 验证：ResearchPages `75 passed`；frontend typecheck PASS；
  `git diff --check` PASS。
- 实际收益：科学证据链更容易被研究人员检查，同时不改变科学 authority、
  不暴露 provider 或基础设施秘密。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #12 / CO-009 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：stale recovery 虽有同栈演练证据，但缺少数据库回归保护 product
  与 qualification 项目分流。
- 修改：新增一个真实 product stale Turn 和一个 bounded qualification
  Turn，验证 `list_stale` 只将 product 暴露为 recovery candidate，资格
  数据单独保留。
- 修改文件：`tests/test_phase14r_recovery.py`、连续优化证据文件。
- 验证：recovery focused `5 passed`；touched Ruff PASS；
  `git diff --check` PASS。
- 实际收益：避免恢复服务误重发资格任务或制造重复科学执行。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #13 / CO-011 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：XRD 报告虽支持讨论、结论和限制，但缺少专门回归保护其科学
  通信质量。
- 修改：新增 XRD 报告测试，验证 discussion/conclusion 绑定权威
  `xrd.matched_peak_count`，保留限制并通过 ReportGroundingValidator。
- 修改文件：`tests/test_agent2_phase8_reports.py`、连续优化证据文件。
- 验证：Reports focused `35 passed, 4 skipped`；touched Ruff PASS；
  `git diff --check` PASS。
- 实际收益：XRD 报告可读性与事实绑定得到持续保护，不会触发科学重算。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #14 / CO-012 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Phase 14-R Scientific Surface 覆盖矩阵是手工维护的，缺少对 live
  Registry/Capability Pack/Result projector 的漂移保护；审计实际发现
  `ml.regression_evaluation` 文档 Pack 为 `core.data`，而 live pack 为
  `core.other`。
- 修改：新增 `tests/test_phase14r_surface_coverage.py`，自动从当前
  Registry 与 trusted Packs 派生 capability IDs、Pack、ToolBinding 与
  Result projector，并要求与矩阵逐项一致、覆盖列非空、状态值受控且
  projector 已注册；同步修正矩阵 Pack 单元。
- 修改文件：`tests/test_phase14r_surface_coverage.py`、
  `docs/agent2/phase14r/SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md`、
  `docs/agent2/continuous_optimization/evidence/co-012-surface-registry-drift-2026-09-05.json`、
  连续优化状态文档。
- 验证：surface coverage `1 passed`；touched Ruff PASS；`git diff --check`
  PASS。
- 实际收益：Registry/Pack/文档能力覆盖漂移现在会在回归阶段快速失败，
  不会悄悄产生错误的科学能力覆盖认知；未引入第二套能力 authority。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #15 / CO-013 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：历史精确版本 Viewer 回归主要集中在 Dataset/Structure，其他已注册
  ScientificObject-backed Viewer 家族缺少 v1/v2、归档/恢复后的精确版本保护。
- 修改：在 `tests/test_agent2_phase9_viewers.py` 增加参数化回归，覆盖
  Dataset/Table、Structure、Trajectory、XRD、Electronic、Phonon 与
  Volumetric 共 `10` 个对象类型；每例验证 v2 为 current 时归档状态仍可
  读取 v1，恢复后 current 与版本数量保持不变。
- 额外发现：`analysis.rdf` 与 `reciprocal.brillouin_zone` 只有 Viewer
  descriptor、没有 ScientificObject registry 类型，记录为新候选 CO-122，
  没有把对象级历史覆盖伪装成 PASS。
- 修改文件：`tests/test_agent2_phase9_viewers.py`、连续优化证据与状态文档。
- 验证：Viewer focused `18 passed`；touched Ruff PASS；`git diff --check`
  PASS。
- 实际收益：已注册对象 Viewer 的历史/归档读取具备统一可重复保护，防止
  newer version 或 archive transition 替换旧科学来源。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #16 / CO-014 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Viewer 将 `SOURCE_MISSING`、`METADATA_ONLY`、`INVALIDATED` 统一
  显示为不可用并提供重试，用户无法区分可恢复缺失、交互预览上限与失效
  历史证据。
- 修改：新增 `viewerPayloadRecovery` 状态映射；仅 `SOURCE_MISSING` 显示
  “重新读取来源”，`METADATA_ONLY` 和 `INVALIDATED` 分别显示准确原因并
  移除误导性重试；三种状态均保留精确来源/属性入口。
- 修改文件：`apps/web/app/components/scientific-viewer/ScientificObjectViewer.tsx`、
  `apps/web/app/components/scientific-viewer/ScientificObjectViewer.test.tsx`、
  连续优化证据与状态文档。
- 验证：ScientificObjectViewer focused `3 passed`；frontend typecheck PASS；
  `git diff --check` PASS。
- 实际收益：恢复动作与持久化科学状态一致，避免用户对超限或失效版本
  进行无效重试，同时保留可审计的来源导航。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #2 / CO-002 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Report table preview 对无显式 ID 的科学行使用视觉数组下标作为
  React key，排序或重新投影后可能发生错误 DOM 复用。
- 修改：优先使用唯一 `id/sample_id/sampleRef/site_index/structureId/
  material_id`；否则使用属性顺序无关的规范化行内容，并仅对完全相同的重复行
  添加 occurrence 消歧。
- 修改文件：`ScientificReportArtifactPreview.tsx` 及对应测试；持续优化
  backlog/log 和 persistent 状态文档。
- 验证：focused Vitest `9 passed`；无 ID 行重排、`sample_id` 唯一性和
  重复行消歧测试 PASS；frontend typecheck、touched diff check PASS。
- 实际收益：报告表格在排序/刷新后保留稳定科学行身份，不把视觉位置提升为
  数据 authority。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #3 / CO-003 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Materials Explorer 通用统计/比较表格丢弃上游语义身份并使用数组
  下标作为 React key。
- 修改：表格行改为 `{ key, cells }`，分别绑定 chemical system、
  ScientificObject、quality column/value 和 comparison property；重复上游
  身份进入确定性消歧，不把视觉位置作为默认身份。
- 修改文件：`DatasetMaterialsExplorerPanel.tsx` 及对应测试；持续优化
  backlog/log 和 persistent 状态文档。
- 验证：focused Vitest `11 passed`；重排和重复身份回归 PASS；frontend
  typecheck、touched diff check PASS。
- 实际收益：数据浏览器的科学行在筛选、重排和刷新后保持稳定 DOM identity。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #4 / CO-005 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：ResearchTurn 与 legacy Job polling 只忽略迟到结果，但未真正取消
  网络请求/全部 retry timer；legacy Interpretation 回调可能在切换研究后更新
  当前页面。
- 修改：相关读 API 支持 AbortSignal；两套 polling 实施单一在途约束、卸载
  abort、timer 清理和 exact-lineage callback guard；仅 AbortError 被静默忽略。
- 修改文件：`agent2-execution-api.ts`、`planner-api.ts`、
  `ResearchPages.tsx` 及对应测试；持续优化状态文档。
- 验证：ResearchPages `73 passed`；新增 unmount abort、online 防重叠和
  AbortError 分类回归；frontend typecheck、touched diff check PASS。
- 实际收益：长时间研究切换不再留下无效请求或让迟到的进度/解释覆盖当前 Turn。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #5 / CO-004 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：历史链接同时包含相关 Job ID 和权威 ResearchTurn ID 时，旧 Job
  hydration/polling 仍可能与 Turn progress 并行，形成两套执行状态 authority。
- 修改：explicit ResearchTurn 存在时，`runId` 只保留 provenance/session
  定位用途；跳过 legacy Job details/events/artifacts/interpretation 与 poller；
  legacy run-only 行为保持。
- 修改文件：`ResearchPages.tsx` 及对应测试；持续优化状态文档。
- 验证：ResearchPages `74 passed`；新增 run+turn 测试证明 Turn 进度可见且
  Planner Job/Event/Artifact readers 调用为 0；frontend typecheck、diff
  check PASS。
- 实际收益：一个研究页面不再被两个执行模型同时驱动，避免进度和结果串线。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #6 / CO-036 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：关键 Data→Research→Viewer→Report→History 产品转换缺少真实
  浏览器级 SPA/no-document-reload 回归，用户容易感知为页面重载和缓慢切换。
- 修改摘要：新增 `apps/web/test/product-navigation-spa-acceptance.mjs`
  和 `test:product-navigation-spa` npm 入口；脚本在认证后遍历六条关键
  转换，检测 document 请求、`performance.timeOrigin`、运行时标记、
  console 与 5xx。预期认证前 401 在认证边界清理，认证后仍严格失败。
- 修改文件：`apps/web/test/product-navigation-spa-acceptance.mjs`、
  `apps/web/package.json`、连续优化证据与状态文档。
- 验证：authenticated Chrome acceptance PASS；六条转换
  `documentRequests=0`，`timeOriginPreserved=true`，
  `runtimeStatePreserved=true`；暖态 `37–139 ms`；console errors `0`；
  server 5xx `0`；frontend typecheck PASS；touched diff check PASS。
- 实际收益：将用户感知的“页面转换慢/重载”风险变成可重复的产品回归；
  当前实现保持单页运行时并且暖态切换远低于秒级目标。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #7 / CO-006 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Project History 兼容查询只按 Job ID 连接 ResearchTurn，异常跨项目
  关系可能泄漏另一项目的 Turn identity。
- 修改摘要：`research_session_runs` 与 `research_turns` 的连接增加同项目约束；
  保留非标准 Job ID 的 legacy run-only 安全回退；新增跨项目关系 fail-closed
  回归。未改变 ResearchTurn identity authority。
- 修改文件：`apps/api/mdi_api/routers/project_history.py`、
  `tests/test_project_history_research_context.py`、优化证据与状态文档。
- 验证：project-history `5 passed`；project-access `32 passed`；touched Ruff
  PASS；touched diff check PASS。
- 实际收益：历史恢复路径不再因 malformed Job/Turn 关系跨项目泄漏精确
  ResearchTurn；合法显式关系与 legacy 兼容行为保持不变。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #8 / CO-007 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Legacy ContextSnapshot 兼容 Manifest 投影未执行 operation-specific
  budget，历史回放可能超出输入预算并错误标记为 `NONE`。
- 修改：按科学上下文优先级确定性裁剪兼容项；非关键溢出写入
  `excluded_items` 并标记 `COMPACTED`；关键科学上下文超限 fail-closed；
  保留有界 included/excluded 合同。
- 修改文件：`apps/api/mdi_api/routers/agent2.py`、
  `tests/test_phase14r_context_manifest.py`、连续优化证据文件。
- 验证：`pytest tests/test_phase14r_context_manifest.py -q` 为 `13 passed`；
  touched Ruff PASS；`git diff --check` PASS。
- 实际收益：历史 ContextManifest 回放与新建 Manifest 使用同一预算边界，
  避免 provider 输入超限或关键科学证据被静默丢弃。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #9 / CO-008 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：上下文 pin/unpin 虽已有服务/API/UI，但缺少跨 repository reload
  的持久化回归，刷新或重新登录可能出现未验证的状态漂移。
- 修改：新增真实 `ScientificResultSnapshot` 生命周期测试，验证固定精确
  Result 后新会话仍可读取，取消固定后再次读取为空。
- 修改文件：`tests/test_agent2_phase7_memory.py`、连续优化证据文件。
- 验证：`pytest tests/test_agent2_phase7_memory.py -q` 为 `10 passed`；
  touched Ruff PASS；`git diff --check` PASS。
- 实际收益：Context pin/unpin 的跨刷新持久化契约有了可重复保护，且不改变
  ScientificResult 的不可变科学 authority。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #17 / CO-015 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Research/Report 的 Figure/Table 只能打开受信 Artifact，缺少可审计的
  下载入口，用户需要离开当前呈现才能保存完整科学 payload。
- 修改摘要：新增 `ArtifactDownloadLink`，严格限制为同源
  `/api/planner/jobs/{job}/artifacts/{artifact}/content`；在
  `ScientificPresentationBlocks`、`ScientificReportRoute` 的 Figure/Table
  与证据 Artifact 入口提供下载。没有新增科学执行或第二结果来源。
- 修改文件：`apps/web/app/components/ArtifactDownloadLink.tsx`、
  `ArtifactDownloadLink.test.tsx`、`ScientificPresentationBlocks.tsx`、
  `ScientificPresentationBlocks.test.tsx`、`ScientificReportRoute.tsx`、
  `ScientificReportRoute.test.tsx`、连续优化证据与状态文档。
- 验证：focused frontend `32 passed`；typecheck PASS；git diff check PASS。
- 实际收益：Research、Report 与 Workbench 的 Artifact 访问能力一致，下载
  复用服务端授权/长度/SHA-256 校验，Job/ToolCall/Artifact/Result 增量为 0。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #32 / CO-026 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Redis/RQ 不可用时，stale Research recovery 的首次队列异常会
  中断恢复扫描，无法向产品暴露可重试的 durable attention 状态。
- 修改摘要：`StaleResearchRecoveryService` 支持注入既有队列适配器，并在
  orchestration/planning/execution/result/interpretation 重发边界将队列
  故障归一化为 `QUEUE_UNAVAILABLE`；不改变 PostgreSQL 中的 Turn/Job
  身份或状态。Interpretation reconciler 增加同样的有界 queue 注入。
- 修改文件：`apps/api/mdi_api/research_agent/recovery.py`、
  `apps/api/mdi_api/interpretation/reconciler.py`、
  `tests/test_phase14r_recovery.py`、连续优化证据。
- 验证：`test_phase14r_recovery.py` + `test_agent2_phase4_execution.py`
  `15 passed`；operations/retention 回归 `14 passed, 1 skipped`；
  compileall、touched diff check PASS。
- 实际收益：Redis 恢复前不伪造科学完成、不丢弃后续候选；恢复后按同一
  Turn 身份重发，叠加既有 ToolCall/Artifact/Result 幂等保护避免重复输出。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #21 / CO-017 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：回收站保留规则仅由 UI 文案表达，依赖预览与物理删除没有共享的
  版本化策略判定，未来自动过期可能误伤科学 provenance。
- 修改：新增 `mdi_api.lifecycle_policy` 作为后端单一留存策略契约；自动
  清理明确禁用，引用 provenance 永久保护，手动永久删除仅在服务器确认
  零依赖时允许。Project/Dataset 预览与删除路径统一使用该判定；回收站
  永久删除检查展示服务端策略。
- 修改文件：`apps/api/mdi_api/lifecycle_policy.py`、
  `apps/api/mdi_api/routers/secured_runtime.py`、
  `apps/web/app/lib/planner-api.ts`、
  `apps/web/app/components/TrashCenterPage.tsx`、
  `apps/web/app/components/TrashCenterPage.test.tsx`、
  `tests/test_phase14r_retention_policy.py`、
  `tests/test_project_access.py`、优化证据与状态文档。
- 验证：retention policy `3 passed`；生命周期/依赖回归 `6 passed,
  29 deselected`；Trash Center `5 passed`；compileall、typecheck、diff check
  均 PASS。
- 实际收益：科学历史不会被自动过期任务静默删除；手动删除、依赖预览和
  用户看到的保留说明遵循同一可审计策略。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #22 / CO-018 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Project/Dataset 已有零依赖 purge，而 Research Session、
  ScientificObject、Scientific Report 虽实际受保护，却没有相同的机器可读
  策略，客户端可能错误推断其可永久删除。
- 修改：共享留存策略新增 `manualPurge`；容器实体返回
  `SERVER_ZERO_DEPENDENCY_ONLY`，科学/历史实体返回
  `NOT_SUPPORTED_FOR_ENTITY`。Research Session read model 和 Object/Report
  dependency preview 均暴露该策略；未新增删除路由。
- 验证：policy `3 passed`；research/dependency lifecycle `2 passed,
  33 deselected`；report lifecycle `1 passed, 38 deselected`；viewer/object
  lifecycle `28 passed`；Trash Center `5 passed`；typecheck/diff check PASS。
- 实际收益：所有受管理实体均有明确 fail-closed purge 语义，科学版本、
  结果、报告和研究历史不会因客户端误判而进入物理删除路径。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #23 / CO-019 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Research Session 没有数据库权威 dependency-impact 端点，客户端
  无法在生命周期操作前检查消息、Turns、上下文、结果与报告引用。
- 修改：新增 `GET /research-sessions/{session_id}/dependency-impact`，按真实
  `session_id/research_session_id` 列扫描并返回有界依赖；项目权限 fail-closed，
  会话明确 `canDelete=false` 与 `NOT_SUPPORTED_FOR_ENTITY`。
- 验证：research lifecycle `1 passed, 31 deselected`；report lifecycle
  `1 passed, 38 deselected`；viewer/object lifecycle `28 passed`；陌生用户
  `403`；typecheck、compileall、diff check PASS。
- 实际收益：四类生命周期实体都可从服务器读取依赖边界，Research 历史不会
  被当作可删除的前端记录。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #24 / CO-020 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：项目删除与账户停用虽已保留科学记录，但 API 没有结构化表达
  “用户工作区访问”与“科学 provenance 保留”的边界。
- 修改：账户停用返回 `provenanceRetained=true` 及受保护 retention policy；
  项目物理删除继续由服务器零依赖门禁控制；logout 合同保持 `{ok:true}`，
  现有会话撤销和 `account.deactivated` 审计不变。
- 验证：账户管理 `8 passed`；停用/logout 子集 `2 passed`；typecheck、
  compileall、diff check PASS。
- 实际收益：账户停用不再让客户端猜测是否会影响科学历史，结果、版本和
  审计记录明确保留。
- 提交/CI：未提交、未推送；持续任务保持处理中。

## Continuous optimization — Improvement #25 / CO-021 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Job-event 并发回归只覆盖单一 repository 实例，且 live 夹具在
  多次进程运行间复用固定 Dataset ID，旧 Job 外键会让测试在锁逻辑之前
  失败。
- 修改：新增四个独立 `SqlAlchemyRepositoryBundle`、12 个并发 writer 的
  PostgreSQL stress test；`_seed_repos` 改用每次调用唯一随机后缀，避免
  跨运行 FK 冲突；生产 advisory-lock 实现未修改。
- 验证：配置 `postgresql+psycopg` 与 `MDI_RUN_INTEGRATION=1` 后，
  `tests/test_phase6_integration.py -k concurrent_seq` 为 `2 passed,
  17 deselected`。
- 实际收益：多 worker 形态下事件序列的唯一性、连续性和读取顺序有真实
  PostgreSQL 证据，测试夹具不会因历史残留数据掩盖并发回归。
- 提交/CI：未提交、未推送；持续任务保持处理中。
## Continuous optimization — Improvement #37 / CO-127 (2026-09-05)

- 状态：已完成并验证；持续任务保持处理中。
- 问题：viewer 项目成员无法从 Projects 菜单发现只读项目 provenance 导出，
  与服务端 `require_project_access(read)` 授权语义不一致。
- 修改文件：`apps/web/app/components/ProductPages.tsx`、
  `apps/web/app/components/ProductPages.test.tsx` 及 CO-127 evidence。
- 验证：`npm run test -- --run app/components/ProductPages.test.tsx`，
  `46 passed`；viewer 导出请求、下载触发和写操作隐藏均通过。
- 提交/CI：未提交、未推送；持续优化任务继续处理中。
## Continuous optimization — Improvement #38 / CO-128 (2026-09-05)

- 状态：已完成并验证；持续任务保持处理中。
- 问题：旧兼容分析请求接口在带项目 ID 时没有执行项目读取授权。
- 修改文件：`apps/api/mdi_api/routers/secured_runtime.py`、
  `tests/test_project_access.py` 及 CO-128 evidence。
- 验证：项目授权子集 `2 passed`；owner/viewer scoped request 通过，
  stranger 返回 403，无项目旧请求仍返回 accepted，未创建科学执行。
- 提交/CI：未提交、未推送；持续优化任务继续处理中。
## Continuous optimization — Improvement #39 / CO-129 (2026-09-05)

- 状态：已完成并验证；持续任务保持处理中。
- 问题：缺失上传文件的 HTTP detail 暴露完整本地路径。
- 修改文件：`apps/api/mdi_api/phase2_runtime.py`、
  `tests/test_phase2_product_loop.py` 及 CO-129 evidence。
- 验证：`pytest -q tests/test_phase2_product_loop.py -k
  'api_call_redacts_missing_upload_paths or direct_upload_path_preflights'`
  `2 passed`；路径已从 detail 移除。
- 提交/CI：未提交、未推送；持续优化任务继续处理中。

## Continuous optimization — Improvement #40 / CO-091 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Scientific Viewer 外层 `article` 没有显式可访问名称，
  屏幕阅读器无法可靠识别 Viewer 区域。
- 修改文件：`apps/web/app/components/scientific-viewer/ScientificViewerShell.tsx`、
  `ScientificViewerShell.test.tsx` 及 CO-091 evidence。
- 验证：Viewer Shell focused tests `2 passed`；`npm run typecheck`
  通过；`git diff --check` 通过（仅常规换行提示）。
- 收益：每个 Viewer 实例的 `article` 现在通过唯一标题 ID 与可见 `h2`
  建立 `aria-labelledby`，重复实例不会冲突。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #85 / CO-103 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- ProductShell speculative route prefetch 从一次性突发改为逐路由 idle/timer
  队列，并在 route change/unmount 时取消；保持 App Router 预取能力。
- 修改文件：`apps/web/app/components/ProductShell.tsx`、
  `ProductShell.test.tsx`及 CO-103 evidence。
- 验证：dedicated scheduler `1 passed`，typecheck PASS，diff check 无实际错误。
- 收益：冷启动期间减少预取请求突发，避免与首屏/历史/会话请求争抢资源，
  且不会在用户离开后继续无效请求。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #86 / CO-048 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- saved-search 使用同页 CustomEvent、storage 与 BroadcastChannel 同步，
  只广播 opaque revision，跨通道去重并忽略 malformed marker。
- 修改文件：`apps/web/app/lib/saved-search-sync.ts`、
  `ProductShell.tsx`及对应测试/evidence。
- 验证：sync `5 passed`、ProductShell `21 passed`、typecheck PASS。
- 收益：保存检索在重新打开和多标签场景下自动收敛，无需硬刷新且不泄露
  检索内容。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #87 / CO-109 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Artifact renderer registry 新增 identity index，Workspace Gallery 使用
  memoized index 进行 O(1) 查找，避免大 bundle 重复线性扫描。
- 修改文件：`workspace-renderer-registry.ts`、`WorkspaceArtifactGallery.tsx`
  及对应测试/evidence。
- 验证：workspace renderer focused `11 passed`（含 500 artifacts），
  typecheck PASS。
- 收益：大量 Artifact 更新和重复渲染时降低匹配开销，身份与 renderer
  选择保持精确且不触发科学重算。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #88 / CO-055 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Research 与 Task Center 统一 CANCELING/cancel_requested 语义、中文案与
  1.8 秒确认轮询；取消中禁用重复停止，等待服务端终态。
- 修改文件：`research-status.ts`、`ResearchExecutionActivity.tsx`、
  `ResearchPages.tsx`、`TaskCenterPage.tsx`、`globals.css`及对应测试/evidence。
- 验证：取消 focused `25 passed`，typecheck PASS，diff check 无实际错误。
- 收益：慢取消不会被误认为完成或失败，跨页面状态一致且避免重复请求。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #89 / CO-134 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Artifact 下载链接现在对文件名做有界清洗：移除控制字符、替换路径分隔符、
  去除前导点遍历、限制 120 字符；无效名称使用浏览器默认命名。
- 修改文件：`apps/web/app/components/ArtifactDownloadLink.tsx`、
  `ArtifactDownloadLink.test.tsx`及 CO-134 evidence。
- 验证：focused `3 passed`，typecheck PASS，diff check PASS。
- 收益：保留可读下载名，同时避免不必要的路径/控制元数据进入浏览器。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #90 / CO-051 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Task Center 从服务端授权 cursor feed 分页加载历史任务，按稳定
  `projectId:jobId` 去重，保持筛选、排序、exact Turn 链接与后续页重试。
- 修改文件：`apps/web/app/lib/task-center-data.ts`、`TaskCenterPage.tsx`
  及对应测试/evidence。
- 验证：Task feed/Task Center `21 passed`（含 1000-job/10-page），
  typecheck PASS，diff check PASS。
- 收益：长任务历史不再被客户端切片隐藏，首屏 payload 有界且分页为只读。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #91 / CO-110 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Viewer 在 payload 尚未就绪时保留 metadata/provenance 可见，显示精确
  Artifact 身份、ToolCall、SHA-256 与来源/重试入口；缺失和失败复用同一
  有界元数据区。
- 修改文件：`apps/web/app/components/ScientificViewerAdapter.tsx`、
  对应 effect tests 及 evidence。
- 验证：focused `8 passed`，typecheck PASS，diff check 无实际错误。
- 收益：慢 Viewer 不再只有泛化 spinner，用户可核验来源并采取恢复动作，
  且不触发科学重新计算。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #92 / CO-054 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- “打开”保持原 exact ResearchTurn；“打开并重试（新运行）”显式带
  `retry=1`，仅对失败/取消且具写权限的会话创建 child Turn，并保留
  原 Turn、Job 与 evidence。
- 修改文件：`TaskCenterPage.tsx`、`ResearchPages.tsx`、两个 research 路由、
  对应测试/evidence。
- 验证：Research + Task Center 合并 `99 passed`，typecheck PASS，
  diff check 无实际错误。
- 收益：用户可明确知道是否会重新执行科学，旧失败证据不会被覆盖。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #93 / CO-037 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 通过 grid `min-width:0`/`max-width:100%`、移动控件换行及可聚焦宽表
  滚动区，改善 390x844/200% zoom 下 Presentation/Report 可用性。
- 修改文件：`apps/web/app/globals.css`、`WorkspaceArtifactGallery.test.tsx`
  及 CO-037 evidence。
- 验证：Workspace Gallery `7 passed`，typecheck PASS，diff check 无实际错误。
- 收益：宽科学表格不再把全局页面撑出横向裁剪，样本选择和表格滚动仍可
  用键盘触达。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #94 / CO-056 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Research 页面按 exact Project/Session/Turn 校验持久化 scope，刷新、重新
  挂载、恢复可见或联网时重读 History/Session/Turn，并从 Turn 恢复缺失问题。
- 修改文件：`apps/web/app/components/ResearchPages.tsx`、对应 tests/evidence。
- 验证：recovery/reconnect focused PASS，typecheck PASS；完整 Research
  `88 passed`，1 个既有顺序敏感 context retry case 单独重跑通过。
- 收益：离开返回不依赖前端内存，不使用 Job 名猜测，跨项目/会话错误身份
  fail closed。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvements #71–#75 (2026-09-05)

- 状态：全部已完成并验证；持续优化总任务继续处理中。
- CO-114：服务端授权的依赖影响导航覆盖 exact Data/Research/Report；
  backend `37 passed, 4 historical skips`，frontend `66 passed`。
- CO-073：Viewer loader 错误按场景校验、WebGL、chunk、初始化分类；
  focused `25 passed`。
- CO-053：停滞 RUNNING 任务以“需要关注”呈现，保留真实状态与检查动作；
  focused `7 passed`。
- CO-096：Edit-last-message 在权威原 Turn 加载失败时双层 fail closed；
  focused `2 passed`。
- CO-095：Continue 只对 Result 404 进入新执行；exact Result 显式成为复用
  候选，其他读取失败不创建 Turn；Research/API `89 passed`。
- 合并验证：frontend typecheck PASS；`git diff --check` PASS（仅工作树
  既有 CRLF 提示）；未提交、未推送，服务与浏览器保持运行。

## Continuous optimization — Improvements #76–#78 (2026-09-05)

- 状态：全部已完成并验证；持续优化总任务继续处理中。
- CO-077：Viewer 生命周期动作具有权限/归档/服务等精确禁用原因，
  focused `8 passed`。
- CO-094：Retry 创建新 ResearchTurn lineage，旧失败 Turn 与证据保持并可
  导航返回；focused `3 passed`，Research `85 passed`。
- CO-100：运行中草稿在当前标签页按 exact Turn 保存并可刷新恢复，
  且明确不会重提正在运行的科学任务；Research `85 passed`。
- typecheck/diff PASS；未提交、未推送，服务与浏览器保持运行。

## Continuous optimization — Improvement #79 / CO-115 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Project、Research session 与 Report 的组织动作统一显示“列表置顶”，
  Result 与来源版本明确显示“加入/移出本会话上下文”；会话内同时解释两类
  操作的不同影响。
- 修改文件：四个产品组件、四个对应 focused test、优化 backlog/log 及
  CO-115 evidence。
- 验证：frontend focused `151 passed`；typecheck PASS；diff check 仅有
  已知 CRLF 转换警告。
- 收益：用户不会把列表排序误认为 Agent 科学上下文变更，且没有改变
  ScientificResult、ScientificObjectVersion、执行或授权权威。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #80 / CO-050 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Task/Notification 共享 feed 增加 AbortSignal、hidden/offline 轮询门控、
  多消费者安全取消与恢复刷新；预期 Abort 不会显示为失败或覆盖新状态。
- 修改文件：`task-center-data`、Task/Notification 两个页面及对应测试、
  backlog/log/evidence。
- 验证：focused `21 passed`；合并 typecheck PASS；diff check 仅有已知
  CRLF 转换警告。
- 收益：不可见或离线时减少无意义请求和陈旧覆盖，返回页面时无需整页重载
  即可恢复持久化状态。
- 提交/CI：未提交、未推送；服务与浏览器保持运行。

## Continuous optimization — Improvement #70 / CO-104 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 修改：补充 Research session 预热缓存的 lifecycle mutation 回归；重复读取
  继续合并，archive/restore/rename 后下一次列表读取必须命中授权 API。
- 文件：`apps/web/app/lib/product-api.test.ts`及 CO-104 evidence。
- 测试：product-api `7 passed`；typecheck/diff check PASS。
- 收益：页面预热性能保留，同时消除生命周期操作后的跨页面陈旧列表风险。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvements #67–#69 (2026-09-05)

- 状态：三项均已完成并验证；持续优化总任务继续处理中。
- CO-111：Viewer 快速重试合并为一个可取消请求，并使用最大 1 秒退避；
  focused tests `4 passed`。
- CO-113：Trash Center 批量恢复按授权/项目原子执行，失败组保留并显示
  partial result；focused tests `8 passed`。
- CO-119：CI 失败也会上传 log、exit、JUnit 与脱敏同栈快照；workflow
  parse PASS，operations `11 passed, 1 historical skip`。
- 合并 typecheck/diff PASS；本机 same-stack status=ok，PostgreSQL/Redis/
  MinIO 正常，workerCount=6，DB active=1/idle=5/idle-in-transaction=0。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvements #63–#66 (2026-09-05)

- 状态：四项均已完成并验证；持续优化总任务继续处理中。
- CO-075：来源缺失 Viewer 展示有界精确身份并导出不含 payload 的元数据；
  Viewer tests `6 passed`。
- CO-093：Research 状态筛选支持命名组、方向键/Home/End 与同步焦点状态；
  ResearchPages `77 passed`。
- CO-102：空 Research 项目获得授权正确的 Data Platform 入口；
  ResearchPages `77 passed`。
- CO-117：CI 以 JUnit XML 汇总 service-backed 测试；解析器 `2 passed`，
  真实 smoke selected=2/passed=2/skipped=failed=errors=0。
- 合并 `npm run typecheck`、touched Ruff、相关 diff check 通过。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #62 / CO-108 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 修改：Generic JSON Artifact 预览先执行有界结构投影，再序列化小型预览；
  节点、层级、数组项、对象字段和长文本均受明确预算约束，并披露省略数量。
- 文件：WorkspaceArtifactGallery、ScientificWorkspaceShell focused test、
  `docs/agent2/continuous_optimization/evidence/co-108-bounded-json-preview-2026-09-05.json`。
- 测试：10 万项数组尾部 getter 未读取；focused test `1 passed`；
  `npm run typecheck` 通过。
- 收益：避免大 JSON 完整同步序列化造成页面冻结，同时完整 Artifact 与科学
  事实权威不变。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvements #58–#61 (2026-09-05)

- 状态：四项均已完成并独立验证；持续优化总任务继续处理中。
- CO-081：Dataset 稳定样本身份成为主要视觉/语义身份，源行降为辅助定位；
  focused tests `12 passed`。
- CO-099：取消终态去除重复 notice，由 execution card 单一呈现；Research
  cancel cases `3 passed`，execution activity `11 passed`。
- CO-090：重复 Presentation 的 Evidence item、inspector、Finding anchor
  使用实例作用域；Presentation/Viewer/Report `35 passed`。
- CO-133：Workspace Gallery 标题、分组与活动 Viewer 标题 ID 使用实例
  作用域；gallery `6 passed`。
- `npm run typecheck` 通过；相关 `git diff --check` 无错误。
- 证据：`docs/agent2/continuous_optimization/evidence/co-081-*`、
  `co-099-*`、`co-090-*`、`co-133-*`。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #56 / CO-098 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 修改：Research 生命周期菜单在 archive/restore 后恢复来源焦点；若行因
  当前筛选消失，则焦点回退到状态筛选按钮，并通过 `aria-live` 播报状态。
- 文件：`apps/web/app/components/ResearchPages.tsx`、
  `apps/web/app/components/ResearchPages.test.tsx`、
  `docs/agent2/continuous_optimization/evidence/co-098-lifecycle-focus-2026-09-05.json`。
- 测试：生命周期 focused test `1 passed, 74 skipped`；`npm run typecheck`
  通过。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #57 / CO-132 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 修改：Scientific Table 行 key 现在优先使用对象作用域的稳定 sample
  标识，避免多个同 `objectId` 行碰撞；无稳定身份时使用确定性回退键。
- 文件：`apps/web/app/components/workspace/WorkspaceArtifactGallery.tsx`、
  `apps/web/app/components/workspace/WorkspaceArtifactGallery.test.tsx`、
  `docs/agent2/continuous_optimization/evidence/co-132-table-row-key-identity-2026-09-05.json`。
- 测试：gallery focused tests `5 passed`，无 duplicate-key warning；
  `npm run typecheck` 通过。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #41 / CO-130 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Artifact 直接下载路由虽已有授权包装，但没有回归证明陌生项目
  请求会在真正读取存储内容前失败。
- 修改文件：`tests/test_project_access.py` 及 CO-130 evidence。
- 验证：授权子集 `1 passed, 33 deselected`；陌生用户 403 且下载函数调用
  次数为 0；项目所有者可成功下载同一 Artifact。
- 收益：跨项目直接下载边界有可观察的 fail-closed 保护，避免仅检查
  元数据授权而误读存储内容。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #42 / CO-076 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Viewer 元数据原先静默只显示前 16 项，用户无法判断其余字段
  是缺失还是被折叠。
- 修改文件：`ScientificViewerShell.tsx`、`ScientificViewerShell.test.tsx`
  及 CO-076 evidence。
- 验证：focused shell tests `3 passed`；typecheck 通过；diff check 通过
  （仅常规换行提示）；18 字段场景显示“查看其余 2 项元数据”，展开后
  可访问全部字段。
- 收益：保持研究工作台紧凑首屏，同时以明确计数和原生 disclosure 保留
  所有已加载权威元数据，不再产生“字段不存在”的误导。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #43 / CO-084 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Finding 只有证据数量，用户无法直接进入对应证据链。
- 修改文件：`ScientificPresentationBlocks.tsx`、其测试及 CO-084 evidence。
- 验证：ScientificPresentation focused tests `7 passed`；typecheck 通过；
  diff check 通过；Finding 链接能定位稳定 evidence 节点并调用精确
  interpretation evidence，不创建 Job/ToolCall/Artifact/Result。
- 收益：从科学结论到 provenance 的路径缩短为一次操作，保持现有证据
  inspector 和权限边界不变。
- 备注：仓库暂无 ESLint 配置，`next lint` 进入交互式初始化，未将其
  误报为通过或失败。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #44 / CO-092 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Evidence inspector 打开后焦点不会进入新内容，触发按钮也未声明
  控制区域。
- 修改文件：`ScientificPresentationBlocks.tsx`、其测试及 CO-092 evidence。
- 验证：ScientificPresentation focused tests `7 passed`；typecheck 与
  diff check 通过；打开后焦点在 Evidence region，关闭后返回原按钮，
  `aria-controls` 与详情 ID 匹配。
- 收益：键盘用户可直接进入、阅读并返回证据链，保持现有授权、Result
  和 Artifact 只读边界。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #45 / CO-072 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 通用 Plotly Viewer 增加 `ResizeObserver`，监听实际绘图容器尺寸变化；
  保留 `window.resize` 兼容路径，卸载时断开 observer 并清理 Plotly。
- 修改文件：`apps/web/app/components/workspace/WorkspaceGenericPlot.tsx`、
  `apps/web/app/components/workspace/WorkspaceGenericPlot.test.tsx`及 CO-072 evidence。
- 验证：focused tests `9 passed`，typecheck 通过。
- 收益：分栏、标签切换和移动布局变化会即时反映到图表几何尺寸，
  且不触发任何科学重算。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #46 / CO-112 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 回收站永久删除确认改用稳定 `类型:ID` 令牌，不再依赖可重复标题；
  对话框同时解释依赖保护与留存策略。
- 修改文件：`TrashCenterPage.tsx`、`TrashCenterPage.test.tsx`及 CO-112 evidence。
- 验证：focused tests `6 passed`，typecheck 通过。
- 收益：同名实体无法混淆，错误令牌不会触发删除，保留服务端依赖扫描
  和 provenance 保护。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #48 / CO-087 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Figure 预览从持久化 Artifact 读取有限的 axis title/range/tickvals/ticktext，
  在 SVG `desc` 和可见轴信息中展示；缺失元数据明确显示 Artifact 未提供。
- 修改文件：`ScientificReportArtifactPreview.tsx`、对应测试、
  `globals.css`及 CO-087 evidence。
- 验证：focused tests `10 passed`，typecheck 通过。
- 收益：Band/XRD/RDF 等图表预览的单位、范围和刻度更容易核验，且不推断
  科学事实、不触发重算。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #49 / CO-089 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 表格预览保留 24 行/8 列上限，同时展示准确的省略行列数量，并用原生
  disclosure 列出隐藏列名；完整数据继续通过外层已授权 Artifact 入口查看。
- 修改文件：`ScientificReportArtifactPreview.tsx`、对应测试、
  `globals.css`及 CO-089 evidence。
- 验证：focused tests `11 passed`，typecheck 通过。
- 收益：用户不会把“预览截断”误判为“数据不存在”，且保持有界渲染。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #50 / CO-078 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Viewer 对辅助 Artifact 的失败不再静默丢弃：保留主结果，同时显示部分
  可用状态、每个失败 Artifact 和稳定错误码，并提供原地重试；JSON 解析失败
  统一为 `ARTIFACT_CONTENT_INVALID`。
- 修改文件：`ScientificViewerAdapter.tsx`、对应 effect 测试、`globals.css`
  及 CO-078 evidence。
- 验证：focused tests `8 passed`，typecheck 通过。
- 收益：科研用户能区分完整结果与部分结果，不会看到原生解析堆栈，
  也不会触发科学重算。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #51 / CO-070 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Generic Plot 抽样状态显示 `显示点数/原始点数`，并明确保留端点与极值；
  `sanitizePlotSpec` 同时保留总点数。
- 修改文件：`WorkspaceGenericPlot.tsx`、对应测试及 CO-070 evidence。
- 验证：focused tests `10 passed`，typecheck 通过。
- 收益：有界预览不会伪装成完整数据，科学数值仍来自原始 Artifact。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #52 / CO-079 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 结构 Viewer 在站点达到有界截断时显示权威的“当前显示前 256 / 总数”
  警告，并保留完整结构来源提示；重复的代码与消息警告不会产生重复 UI。
- 修改文件：`apps/web/app/components/viewer-scene/viewerSceneRendererMapper.ts`、
  `apps/web/app/components/viewer-scene/ViewerSceneRendererSurface.tsx`、
  `apps/web/app/components/viewer-scene/ViewerSceneRendererSurface.test.tsx`及
  `docs/agent2/continuous_optimization/evidence/co-079-viewer-site-truncation-2026-09-05.json`。
- 验证：mapper/surface focused tests `43 passed`，`npm run typecheck` 通过。
- 收益：用户可直接区分有界预览与完整结构，科学来源与渲染上限未改变。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #53 / CO-082 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 配位数直方图现在通过 `aria-describedby` 关联有界文本摘要，逐 bin 提供
  配位数、位点数和占比；现有数值表仍是完整可键盘访问替代。
- 修改文件：`apps/web/app/components/workspace/CoordinationHistogramPanel.tsx`、
  对应测试及 CO-082 evidence。
- 验证：focused tests `2 passed`，`npm run typecheck` 通过。
- 收益：科学图表的数值信息不再只依赖颜色、柱高或 hover，且仍来自原始
  Artifact，不触发重算。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #54 / CO-080 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Dataset Explorer 增加每页 50 条的有界分页，显示当前范围、已投影索引
  总数与权威总样本数；通用 Scientific Table 同样显示当前页范围和总行数，
  首尾分页边界正确禁用，sample_id/sampleRef 语义身份保持不变。
- 修改文件：DatasetMaterialsExplorerPanel、WorkspaceArtifactGallery 及对应
  focused tests/evidence。
- 验证：focused tests `17 passed`，typecheck 与 diff check 通过。
- 收益：大数据集不会把有界 payload 误显示成完整数据，同时用户可预测地
  浏览和定位行。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #55 / CO-085 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Figure/Table Artifact 预览按 401/403/404/410、无效 JSON 和大小边界提供
  稳定、可行动且不泄露基础设施细节的状态；安全域错误码继续保留，
  不改变完整 Artifact 入口或科学重算语义。
- 修改文件：ScientificReportArtifactPreview、对应测试及 CO-085 evidence。
- 验证：focused tests `12 passed`，typecheck 通过。
- 收益：报告用户能区分权限、缺失、过期、内容损坏和大小限制，不会把原始
  堆栈误认为科学结果失败。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #47 / CO-131 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 增加精确 ID 授权矩阵，覆盖 ResearchTurn 与 ScientificObject 的详情、
  context、cancel、dispatch、progress、result、projection、interpretation、
  events、metadata、dependency、versions、query、viewer、relationships。
- 修改文件：`tests/test_agent2_api.py`及 CO-131 evidence。
- 验证：授权子集 `1 passed, 27 deselected`；陌生用户所有覆盖路由均为 403，
  对象/版本/哨兵元数据不泄露。
- 收益：核心科学对象和研究执行边界有统一的 fail-closed 回归，不触发
  下游存储或科学执行。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #81 / CO-083 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Data 页面将 tableQuery、tableSort、tableRow 与 canonical selection 写入
  bounded URL/history；非法、跨项目或跨 Dataset token fail closed。
- 修改文件：`apps/web/app/projects/[projectId]/data/page.tsx`、
  `apps/web/app/components/ProductPages.tsx`、`globals.css`及对应测试/evidence。
- 验证：Product/Data regression `48 passed`，typecheck PASS，diff check 无实际错误。
- 收益：刷新、复制链接与前进/后退可恢复同一有界科学数据视图，精确
  Dataset/Object/Version 与 sample identity 不变。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #82 / CO-088 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Workspace Plot 与 Report SVG 预览在有界预算内确定性保留端点、全局
  min/max 与分桶局部极值，公开 shown/total/strategy。
- 修改文件：`WorkspaceGenericPlot.tsx`、`ScientificReportArtifactPreview.tsx`
  及对应测试/evidence。
- 验证：Plot/Report focused `24 passed`，typecheck PASS，diff check 无实际错误。
- 收益：采样预览不会因前段数据填满预算而隐藏后段关键峰值，也不会伪装
  为完整科学序列。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #83 / CO-097 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Research 分支切换器使用服务端 persisted Turn、parent Turn、user message
  revision 和问题内容；增加目标分支可访问名称、来源问题、全部分支披露、
  exact Turn/消息修订标识及当前 aria-current。
- 修改文件：`ResearchPages.tsx`、对应测试、`globals.css`及 evidence。
- 验证：完整 Research regression `86 passed`，typecheck PASS，diff check 无实际错误。
- 收益：用户可在相似问题之间识别正确分支，返回历史时不依赖箭头计数或
  Job 命名猜测。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #84 / CO-049 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Task Center 与 Notification Center 共享不可变 feed snapshot、一次请求、
  一次轮询与在线/可见性生命周期；消费者级取消不会互相误伤。
- 修改文件：`use-product-task-feed.ts`、`TaskCenterPage.tsx`、
  `NotificationCenterPage.tsx`、`task-center-data.ts`及对应测试/evidence。
- 验证：Task/Notification/cache focused `22 passed`，typecheck PASS，
  diff check 无实际错误。
- 收益：双页面打开时初始与恢复请求去重，后台/离线不浪费轮询资源，
  恢复时仍从持久化权威刷新。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #95 / CO-135 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Artifact 普通打开保持 inline；显式下载通过同一授权内容路由追加
  `download=true`，并仅为该请求返回清洗后的 attachment disposition。
- 修改文件：`apps/api/mdi_api/routers/planner.py`、
  `apps/web/app/components/ArtifactDownloadLink.tsx` 及对应测试/evidence。
- 验证：后端 Artifact content `7 passed`；前端 Artifact/Presentation/Report
  `35 passed`；typecheck PASS。
- 收益：用户可区分在线科学检查与本地下载；权限、内容身份和零重算语义不变。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #96 / CO-032 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Provider payload/error、Queue Job/Tool/依赖 failure summary 与 Report
  failure summary 使用统一递归脱敏；自动检测 credential、Bearer/API token、
  Redis/MinIO/S3 endpoint 与绝对路径。
- 修改文件：`services/llm/mdi_llm/redaction.py`、
  `services/llm/mdi_llm/providers.py`、
  `services/workers/mdi_workers/queue_runtime.py`、
  `services/workers/mdi_workers/report_worker.py`、
  `tests/test_phase14r_sensitive_sentinels.py` 及 evidence。
- 验证：focused `37 passed`；scanner/Provider subset `11 passed`；
  Report/export/project authorization regression、web typecheck、compileall、
  touched Ruff 与 diff check PASS。
- 收益：嵌套错误不会泄漏凭据、基础设施 endpoint 或路径，科学数值、单位、
  sample/version/evidence identity 不被误脱敏。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #97 / CO-069 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Generic Plotly 异步创建/卸载的 purge 变为幂等；审计现有 Scene、
  Trajectory、Phonon、Volumetric 的 engine/worker/request/listener cleanup。
- 修改文件：`WorkspaceGenericPlot.tsx` 及对应测试/evidence。
- 验证：renderer cleanup `60 passed`；typecheck、diff check PASS。
- 收益：快速切换/卸载重 Viewer 不再重复释放，且不触发科学重算。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #98 / CO-058 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 新增授权只读 `ResearchTurn→Job→ToolCall→Result→Report` correlation
  投影，ToolCall 上限 64 并披露截断；不返回参数、路径、storage/provider/
  queue 细节或凭据。
- 修改文件：`apps/api/mdi_api/routers/agent2.py`、`main.py`、
  `tests/test_agent2_api.py` 及 evidence。
- 验证：focused API `2 passed`；Ruff、compileall、diff check PASS。
- 收益：完整科学执行链可诊断，同时保持项目隔离、去敏与科学权威不变。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #99 / CO-045 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Global search 新增绑定用户/查询/项目/类型/状态的有界 cursor；ProductShell
  使用 SPA 加载更多、稳定去重和失败重试，达到服务端扫描上限时明确提示。
- 修改文件：`secured_runtime.py`、`planner-api.ts`、`product-api.ts`、
  `ProductShell.tsx`、对应测试及 evidence。
- 验证：后端 `9 passed`；前端 `22 passed`；125 个授权结果六页、唯一 125、
  私有泄漏 0；跨用户/变更筛选 cursor 422；typecheck/Ruff/diff PASS。
- 收益：长搜索可完整、授权、无硬刷新地浏览，不把导航结果提升为科学事实。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #100 / CO-035 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Research performance 探针在当前标签页保存最多 50 条 opaque timing，
  以双帧确认衡量真实 UI 响应，并绑定 exact ResearchTurn 的首个持久化进度；
  不记录 prompt、科学数据、凭据或基础设施 secret。
- 修改文件：`research-performance.ts` 及测试、`ResearchPages.tsx`、
  Phase14R performance baseline 和 evidence。
- 验证：五个 exact Turn 的 acknowledgement p50/p95=`26/29 ms`，
  first persisted `RECEIVED` p50/p95=`262/293 ms`；browser error/warn 0；
  helper `5 passed`、focused Research `1 passed`、typecheck/build PASS。
- 收益：提交流畅度现在可跨 App Router 导航稳定复验，且进度来自 durable
  ResearchTurn 状态而非伪造的 thinking 文案。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #101 / CO-136 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 关闭 3000、3013–3023 的旧前端/专用包装进程，只保留当前 3024；新增
  默认 dry-run、当前端口 health gate、仓库 Next listener 精确匹配的安全轮换工具。
- 修改文件：`scripts/phase14r_rotate_frontend.ps1`、
  `tests/test_phase14r_frontend_rotation.py` 及 evidence。
- 验证：focused `2 passed`；live 3025 dry-run 只识别 PID 26440，apply
  只停止该 PID；3024/8005/PostgreSQL/Redis/MinIO 均健康；diff PASS。
- 收益：不再堆积 stale frontend 内存或误用旧构建，同时不会误停当前后端栈。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #102 / CO-071 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Generic Plot 增加 heatmap cell、mesh vertex 与 mesh triangle 独立
  100,000 hard cap；超限明确拒绝、不静默截断，完整 Artifact authority 保留。
- 修改文件：`WorkspaceGenericPlot.tsx`、对应测试及 evidence。
- 验证：focused `13 passed`；typecheck、diff check PASS。
- 收益：重 heatmap/mesh 在进入 Plotly 前被有界保护，不冻结标签页、不改变科学值。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #103 / CO-030 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 统一 session-expired 恢复保留完整 path/query/hash 与 Research 本地草稿；
  登录页显示明确重认证说明，安全 local return 成功后精确返回。
- 修改文件：`ProductShell.tsx`、`LandingPage.tsx`、对应测试及 evidence。
- 验证：focused `27 passed`；typecheck、diff check PASS。
- 收益：401 不再表现为科学失败或丢失草稿；外部/歧义 return URL 继续 fail closed。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #104 / CO-052 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 通知 read/unread 采用 user/project/Job/revision 绑定的服务端持久标记；
  Job 新状态自动重新未读，打开研究、筛选和显式切换均有诚实同步语义。
- 修改文件：`secured_runtime.py`、`main.py`、`product-api.ts`、
  `NotificationCenterPage.tsx`、对应测试及 evidence。
- 验证：后端 `2 passed`；前端/API `14 passed`；typecheck、Ruff、
  compile/import、route registration、diff check PASS。
- 收益：阅读状态跨导航/登录保持，且不会越权或成为科学事实 authority。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #105 / CO-033 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Presentation exact-field allowlist、Viewer bounded token 与 Pack binding
  validator 阻断任意 component/import/HTML/script/remote URL。
- 修改文件：`scientific-presentation.ts`、`scientificViewerRegistry.ts`、
  `packs.py`、Viewer schemas、对应负向测试及 evidence。
- 验证：后端 `44 passed`；前端 `29 passed`；typecheck、Ruff、diff PASS。
- 收益：Presentation 继续是 reviewed repository code 的声明式通信层，
  server/Pack descriptor 无法变成可执行 UI authority。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #106 / CO-086 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Artifact content 将 404 临时缺失、410 metadata-only gone、413 over-cap 与
  422 integrity failure 分开；browse/download 共享存储前项目授权但 disposition
  分离。
- 修改文件：Planner content route、Viewer/Report Artifact 状态、对应测试及 evidence。
- 验证：后端 `11 passed`；Viewer/Report `28 passed`；链接/Presentation
  `12 passed`；typecheck、Ruff、compileall、diff PASS。
- 收益：用户得到准确可恢复性提示，不泄漏 storage 细节、不强迫下载、不重算科学。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #107 / CO-105 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Project Home 从全量 history 客户端切片改为 datasets/analyses/activity 各自
  8 条首屏与稳定 server cursor 继续加载；保留其他调用的兼容行为。
- 修改文件：Project History service/router、`planner-api.ts`、
  `ProjectHome.tsx`、对应测试及 evidence。
- 验证：1000-item；后端 `5 passed`、前端 `5 passed`；typecheck/diff PASS。
- 收益：大项目首屏 payload 与渲染成本有界，继续加载仍保持 SPA 和 exact identity。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #108 / CO-039 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- typed local/same-stack profile 在 API serving 与 worker consuming 前统一校验
  PostgreSQL、Redis namespace、MinIO、Agent orchestration 及环境 alias 冲突。
- 修改文件：API `config.py`、worker entrypoint、API/worker 启动脚本、测试及 evidence。
- 验证：focused `35 passed`；Ruff/diff PASS。
- 收益：同栈资格环境不能静默退化或让 API/worker 使用不同队列命名空间。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #109 / CO-046 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- Global Search 补齐日期过滤、Result lifecycle 与 exact Session/Turn SPA
  destination，跨 Project 异常关系不再污染导航。
- 修改文件：`secured_runtime.py`、`planner-api.ts`、`ProductShell.tsx`、
  Search 覆盖测试及 evidence。
- 验证：后端 `27 passed`、前端 `28 passed`；typecheck、Ruff、route/diff PASS。
- 收益：所有支持的 active/archived/trashed 工作可授权发现并精确返回产品流。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #110 / CO-029 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 新增 24-route exact HTTP 矩阵与 Report/Evidence/Dataset/Artifact 前置授权
  回归；修复 Project History 测试兼容分支吞 403。
- 修改文件：Project History router、三组 authorization 测试及 evidence。
- 验证：HTTP `1 passed`、Report/Evidence `3 passed`、Dataset/Artifact
  `2 passed`；Ruff、compileall、diff PASS。
- 收益：跨项目 exact ID 不能成为 metadata、projection、mutation 或 storage oracle。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #111 / CO-107 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- ContextManifest disclosure 从展开后全量 DOM 改为默认 8 项、展开 32 项的
  可导航窗口，同时保留 exact source/Result/scientific provenance 顺序。
- 修改文件：`ResearchPages.tsx`、对应前端测试、持续优化 evidence/台账。
- 验证：10,000-item；前端 focused `3 passed`、既有 provenance 回归通过、
  后端 ContextManifest `13 passed`；typecheck、diff PASS。
- 收益：大型上下文审计保持有界和可操作，不压缩、不改写科学权威。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #112 / CO-031 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 统一 Project role capability matrix，并修复平台管理页允许非创建者成为
  owner、从而错误暴露 owner-only purge UI 的真实权限不一致。
- 修改文件：API access/platform admin、Project/Research/Admin UI、角色 helper、
  前后端测试及 evidence。
- 验证：后端 `5 passed`；权限/Admin UI `12 passed`；Project actions
  `6 passed`；Research read-only `3 passed`；typecheck、Ruff、compileall、
  diff PASS。
- 收益：项目角色、操作可见性与服务端 enforcement 一致，平台管理员也不会
  自动获得每个科学 Project 的成员权限。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #113 / CO-041 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- API、六类 worker、frontend 启动接入同一日志轮转/保留运行器；活动日志
  不进入删除集合，只有严格托管的时间戳归档可被清理。
- 修改文件：日志 runner、三套启动脚本、focused tests 与 evidence。
- 验证：`5 passed`；Ruff、PowerShell parser、diff PASS；当前真实服务栈
  保持健康且未被重启。
- 收益：后续运行不会因固定日志无限增长占用磁盘，维护操作可先 dry-run。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #114 / CO-074 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 体数据校验不再把合法 mixed boundary 误判为损坏；renderer unsupported、
  schema invalid、grid mismatch 与数值越界均有独立 typed 状态。
- 修改文件：Volumetric validation、focused tests 与 evidence。
- 验证：`7 passed`；typecheck、diff PASS。
- 收益：用户能区分“科学数据有效但当前不能渲染”和“数据确实损坏/不一致”。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #115 / CO-047 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 根因：offset-only 搜索游标会在分页期间的较新插入发生后漂移，产生重复或
  漏项；生产表也缺少覆盖授权过滤和稳定排序的完整复合索引。
- 修改：opaque keyset v2 使用 `updatedAt/kind/id`，绑定 caller 与 query、
  Project、类型、生命周期、日期筛选；增加 0031 搜索索引迁移及回归。
- 验证：后端搜索/授权 `27 passed`；fresh/legacy migration `4 passed`；
  前端 continuation/API `32 passed`；Ruff、diff PASS。1,250 条语料
  p95 `15.33 ms`，payload <64 KiB，跨 Project 泄漏 0。
- 收益：并发插入时仍能稳定遍历授权结果，且不把无界搜索集加载到浏览器。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #116 / CO-040 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 根因：runtime health 虽执行真实 SQL/Redis/MinIO probe，却没有可比较且
  去密的运行拓扑/连接身份，难以发现连接到了错误实例。
- 修改：新增 `RuntimeConfigurationFingerprint/1.0` 与三个连接 SHA-256
  指纹；凭据不进入 hash，backend/target 与实际探测证明进入 hash。
- 验证：focused `3 passed`，Ruff/compileall/diff PASS；live endpoint
  PostgreSQL、Redis、MinIO 均 `ok` 且 `connectionBound=true`。
- 运行时：只滚动 API PID `27560 → 26356`；其余服务与浏览器标签未停止。
- 收益：运行时漂移可被可靠比较，同时不泄漏或编码密码/Access Key。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #117 / CO-043 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 根因：pytest、npm/build、browser evidence 和服务会在确认磁盘容量前分配
  进程及写入缓存，低空间会留下部分输出并显示无关底层错误。
- 修改：跨平台只读 preflight 接入全部上述入口；默认 5/10 GiB，
  capacity/path/configuration typed failure，并披露配置的 E 盘 fallback。
- 验证：focused `11 passed`；前端 `5 passed`；typecheck 与 isolated distDir
  production build PASS；Ruff/compileall/PowerShell parser/diff PASS。
- 收益：大型操作在部分写入前失败并给出可操作恢复卷；运行 frontend 保持 200。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #118 / CO-042 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 根因：临时残留没有 dry-run-first 分类，难以区分真正候选与发布证据、活动
  服务数据、日志及恢复归档。
- 修改：严格 allowlist、resolved-path/symlink 防护；默认/显式 dry-run；
  apply 只移入 `.cleanup_archive`，永久删除权不在工具内。
- 验证：focused `4 passed`，Ruff/compileall/diff PASS；live 0 candidates，
  evidence/service/log/archive 均显式列为 protected/recoverable。
- 收益：清理可审计、可恢复，不会把“页面不可见”误当成“可删除”。
- neat-freak：285 MB 独立 build 复核现场已隔离，永久清场等待完整汇报后确认。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #119 / CO-060 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 根因：schema 形状测试不能提前阻止多 head 或危险 upgrade，0031 也没有
  携带核心科学身份的数据往返证明。
- 修改：锁定单一线性 head；全部 revision 要求 upgrade/downgrade；AST
  拒绝 drop/TRUNCATE/DELETE FROM；加入 0030↔0031 identity/Result smoke。
- 验证：fresh/legacy/guard `7 passed`；head `0031_product_search_keyset`；
  Ruff/compileall/diff PASS。
- 收益：迁移分叉或破坏科学身份会在确定性门禁中失败，而不是运行后才发现。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Result archive reconciliation / CO-027 (2026-09-05)

- 状态：已完成并验证；本条补齐既有实现的结果归档，不重新执行或改变实现。
- 修改摘要：DeepSeek 429/5xx/network/timeout 瞬时故障执行一次 250 ms
  有界退避；认证、配置与非法响应继续 fail-fast，调用审计保持脱敏。
- 测试结果：完整 Provider 回归 `67 passed`；Agent2 provider/timeout/failure
  回归 `4 passed, 41 deselected`。
- 提交/CI：未提交、未推送；原实现证据保留在
  `docs/agent2/continuous_optimization/evidence/co-027-provider-retry-2026-09-05.json`。

## Continuous optimization — Result archive reconciliation / CO-028 (2026-09-05)

- 状态：已完成并验证；本条补齐既有实现的结果归档，不重新执行或改变实现。
- 修改摘要：直接 `DatasetUploadRequest` 复用上传会话的文件数、单文件与总字节
  上限；filesystem path 在创建 raw 目录前完成预检并返回类型化错误。
- 测试结果：Phase 2 产品 `9 passed`；typed/durable upload `15 passed`。
- 提交/CI：未提交、未推送；原实现证据保留在
  `docs/agent2/continuous_optimization/evidence/co-028-direct-upload-quota-2026-09-05.json`。

## Continuous optimization — Improvement #120 / CO-137 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：优化候选池包含 5 个重复 ID，声明计数与唯一任务行不一致，两个已完成
  项也缺少 `results.md` 归档，可能导致后续重复执行或错误恢复。
- 修改摘要：删除重复 OPEN 行，将唯一任务计数校正为
  `137 discovered / 121 completed / 16 remaining`；补齐 CO-027/CO-028
  结果记录；新增台账验证器，拒绝重复或不连续 ID、计数漂移、无效 CURRENT
  状态及缺少结果记录的已完成项。
- 修改文件：优化 backlog、`results.md`、台账验证脚本与 focused tests。
- 测试结果：见
  `docs/agent2/continuous_optimization/evidence/co-137-ledger-integrity-2026-09-05.json`。
- 实际收益：持续任务恢复点现在可机器验证，已完成工作不会因重复 OPEN 行再次
  进入执行队列。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #121 / CO-044 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：npm、Playwright、pytest 与 Next 的缓存/临时输出可能落到用户目录或
  分散目录，持续消耗受限系统盘并降低构建可复现性。
- 修改摘要：新增有界 cache runner，把相关工具默认路由到仓库
  `.cache/tooling` 与 `apps/web/.cache`；所有覆盖路径必须位于仓库内，Next
  输出还必须位于 web root 内。
- 修改文件：cache runner、npm/Next/pytest/CI 配置、启动/浏览器入口及
  focused tests。
- 测试结果：focused `3 passed`；越界 probe 正确返回 exit 64；
  typecheck、两次 production build、Node syntax、Ruff、diff check PASS；
  运行 frontend 保持 HTTP 200。
- 实际收益：大型工具缓存不再默认挤占用户系统盘，清理边界与跨平台构建行为
  更可预测。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #122 / CO-063 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：六类 worker queue 名分散在 launcher、settings、producer、recovery、
  operations 与 health，环境覆盖可能造成 API/worker 拓扑漂移。
- 修改摘要：新增 `WorkerQueueManifest/1.0`，统一六个角色、默认名、环境变量、
  settings 属性与 trusted handler；same-stack 对空值、重复名、未知队列和错误
  Redis namespace fail closed；启动器支持有界蓝绿轮换。
- 测试结果：focused `40 passed`；Ruff、compileall、PowerShell parse、diff
  check PASS。8006 影子 API 与新 6 worker 先通过 PostgreSQL/Redis/MinIO
  runtime 验证，再关闭旧 API/worker；最终 8005 PID `25628`、前端 3024
  HTTP 200、影子 8006 不再监听。
- 实际收益：队列拓扑只有一个权威来源，服务更新不再需要同时保留旧进程或
  依赖 launcher 字面量保持偶然一致。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #123 / CO-106 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：长 Research 会话展开时全量渲染消息，1,000+ 消息会让 DOM、内存与
  交互成本无界增长。
- 修改摘要：普通模式保留最近 10 条；展开模式改为 100 条窗口，并提供更早/
  更新导航、明确范围状态、Session/Turn 切换重置和 exact message ID 保留。
- 测试结果：1,001 条真实组件 DOM 固定 100 条；导航后内容身份与按钮焦点
  稳定；20 次窗口投影小于 100 ms；Research suite `92 passed`，
  typecheck、diff check PASS。
- 实际收益：长会话可完整分窗审阅而不会随历史长度线性增加页面渲染负担。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #124 / CO-061 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：真实同栈 PostgreSQL 仍在 `0030_account_invitations`，仓库已经要求
  `0031_product_search_keyset`；API/worker 没有启动门禁，Alembic 也未识别
  启动脚本使用的 `MDI_POSTGRES_HOST`。
- 修改摘要：新增同栈 migration-head fail-fast validator，并接入 API startup
  和 worker admission；统一显式数据库别名判定；启动保护只读且不自动迁移。
- 修改文件：`apps/api/mdi_api/migration_head.py`、API startup、worker
  entrypoint、Alembic env、runtime config、focused tests 和持续优化证据。
- 测试结果：focused `24 passed`；旧 `0030` 影子 API 拒绝；2,679,964-byte
  备份后显式升级，`0031` 影子与正式 API 通过；6 workers idle、6 queues
  depth 0、旧项目进程 0；Ruff、compileall、diff PASS。
- 实际收益：新代码无法再对旧 schema 静默提供服务；迁移与运行 admission
  分离，旧 API/worker generation 在健康切换后全部释放。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #125 / CO-057 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：queue depth、stale Job 和 worker 数量虽已采集，但没有统一健康
  语义、runbook identity 与面向管理员的可操作解释。
- 修改摘要：新增 state/heartbeat worker health；将 backlog、stale Job、
  worker degradation 映射到三个受控 runbook；Admin API/UI 只投影去敏
  指标与处置建议，不提供队列或科学记录变更操作。
- 测试结果：backend `21 passed, 1 integration skipped`；该真实同栈
  integration 单独 `1 passed, 0 skipped`；frontend `8 passed`；live
  snapshot 为 6/6 healthy、depth 0、alerts 0、authority issues 0。
- 实际收益：运维告警从“需要检查”变成一套可解释、可复核且 fail-safe 的
  响应合同。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #126 / CO-059 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：API、worker 和浏览器未处理异常缺少统一的 release-bound、
  request-correlated、secret-safe 事件合同。
- 修改摘要：新增 `OperationalExceptionEvent/1.0`、API 中间件、RQ 异常
  hook、authenticated browser capture 与 frontend rejection capture；只允许
  bounded product/scientific correlation，禁止异常正文、stack、prompt、凭据、
  service URL 和 filesystem path。
- 修改文件：API/worker observability、frontend client observability、启动器
  release SHA 注入、focused tests 与证据文件。
- 测试结果：backend `16 passed`；frontend `2 passed`；live 3023→8005
  authenticated POST 返回 202，请求 ID
  `b7f5745f2d854e4d9907e891555cf959`；typecheck、Ruff、diff PASS。
- 实际收益：跨三层故障现在可按精确 release 与 bounded identity 关联，且
  不泄露科学 payload 或运行秘密。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #127 / CO-101 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Task Center 与 Research 分别推断取消能力，legacy/no-Turn 项可能
  出现不一致或错误的 Agent2 变更操作。
- 修改摘要：引入共享 `MODERN_TURN / LEGACY_READ_ONLY /
  NO_TURN_UNAVAILABLE` 合同；Stop 仅面向显式 persisted ResearchTurn，
  legacy 与无法解析项 fail closed。
- 修改文件：Research 状态 helper、Task Center 与 focused tests。
- 测试结果：合同 `3 passed`；完整 Task Center/status 文件 `14 passed`，
  另有一个与本改进无关的共享 feed 脆弱断言，已登记 CO-138；typecheck、
  diff PASS。
- 实际收益：取消 UI 不再以 Job 字符串或缺失关系推导 mutation authority，
  且服务端取消授权仍为最终权威。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #128 / CO-062 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：API、worker 和 operations 脚本分别硬编码 PostgreSQL、Redis、
  MinIO 同栈参数，一个变更可能只作用于部分进程。
- 修改摘要：新增 typed `SameStackRuntimeTopology` 与环境构建器；API/worker
  launcher 和 operations snapshot 统一消费完整 alias 集；提供有界
  `MDI_PHASE14R_*` override，避免继承 stale generic alias。
- 修改文件：共享 runtime builder、API/worker 启动脚本、operations snapshot、
  focused tests 与证据。
- 测试结果：focused `38 passed, 1 existing live skip`；单一 Redis override
  同时进入 API、worker、health、operations；live PostgreSQL/Redis/MinIO
  healthy、6 workers、queued 0、idle-in-transaction 0；PowerShell parse、
  Ruff、compileall、diff PASS。
- 实际收益：运行与诊断不再因三份配置漂移而连接到不同数据库、Redis
  namespace 或 MinIO endpoint。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #129 / CO-064 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：PostgreSQL、Redis、MinIO 故障在 runtime health 与 operations
  返回不同异常类名，且异常正文可能含 endpoint、bucket 或凭据。
- 修改摘要：新增 `ServiceFailure/1.0`，仅用异常类型、SQLSTATE 与受限
  storage protocol code 分类 authentication/configuration/not-found/timeout/
  unavailable/unknown，并统一 health/operations 投影与 retryability。
- 修改文件：service failure classifier、health、operations、focused tests
  与证据。
- 测试结果：分类 `6 passed`；扩大回归在一个无关旧文本断言前通过 39 项，
  该问题登记为 CO-139；live database/Redis/MinIO/worker 均 ok；Ruff、
  compileall、diff PASS。
- 实际收益：故障能稳定指向正确依赖和重试语义，同时不泄漏基础设施细节。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #130 / CO-066 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Artifact storage 缺少后端统一写入上限，本地中断写入可能在目标路径
  留下半成品。
- 修改摘要：Local 与 S3/MinIO 增加 256 MiB final admission；超限在文件/
  client 调用前拒绝；Local 改为同目录 `.part` 后 atomic replace，异常路径
  清理临时内容。
- 修改文件：Artifact storage、focused tests 与证据。
- 测试结果：Artifact `4 passed`；product/input transport `18 passed`；
  超限 target 0、S3 client call 0、中断 `.part` residue 0；Ruff、compileall、
  diff PASS。
- 实际收益：存储入口有明确硬边界，异常写入不能发布或遗留部分科学 payload。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #131 / CO-065 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Research submit 只依赖 React disabled，Global Search 只丢弃旧响应
  而不取消旧网络请求。
- 修改摘要：Research durable admission 前增加 synchronous same-tick
  single-flight；PostgreSQL active-Turn limit 继续作为服务端权威并返回 typed
  429/`Retry-After: 5`；Search 全链路传播 AbortSignal，在 query/filter/close/
  unmount 时取消过时请求。
- 修改文件：Agent2 error mapping、planner API、ProductShell、Research Pages、
  focused backend/frontend tests 与证据。
- 测试结果：backend `13 passed`；24 并发为 3 accepted/21 limited/3 persisted；
  Search/ProductShell `29 passed`；Research Pages `93 passed`；typecheck、
  Ruff、diff PASS。
- 实际收益：快速重复输入不再产生重复科学准入或浪费搜索容量，服务端持久状态
  仍为最终背压权威。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #132 / CO-116 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：CI 第三方 Actions 与 PostgreSQL/Redis/MinIO service images 使用可变
  tag，供应链身份可能在仓库未改动时漂移。
- 修改摘要：5 个 Action 固定 full commit SHA，3 个 service image 固定
  multi-platform manifest digest；新增 checked-in provenance lock 与
  floating-reference guard。
- 修改文件：CI workflow、provenance lock、focused tests 与证据。
- 测试结果：focused `3 passed`；5 个官方 tag→SHA 全匹配；YAML/JSON parse、
  Ruff、diff PASS；floating Action/image reference 均为 0。
- 实际收益：第三方 tag 重指向不能静默改变 CI 执行内容，审查过的 immutable
  provenance 可在仓库内复核。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #133 / CO-118 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：CI 与本地 service qualification 分别维护测试路径、必过身份与
  terminal grep，存在选择漂移。
- 修改摘要：新增 versioned manifest 与统一 runner/validator；声明 29 paths、
  34 required identities、minimum 50、zero skip/failure；CI/runbook 共用，
  结果由 JUnit 结构验证。
- 修改文件：mandatory-service manifest、runner、CI、两个 runbook、focused
  tests 与证据。
- 测试结果：focused `6 passed`；manifest/load/missing-required/skip guards、
  Ruff、compileall、JSON/YAML parse、diff PASS。
- 实际收益：mandatory test 不会只加入某一个 shell 列表而在其他资格路径
  静默缺席。
- 提交/CI：未提交、未推送；本项不伪造新的完整 service campaign PASS。

## Continuous optimization — Improvement #134 / CO-138 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Task Center 与 Notification Center 的 shared-feed 回归把项目名必须
  出现两次当作正确性条件；合法去重展示后测试失败，但共享请求合同未回归。
- 修改摘要：保留一次共享请求和刷新 transition 的断言，改为分别验证
  `全部任务`、`最近通知` 语义标题及至少一处共享项目内容。
- 修改文件：`apps/web/app/components/TaskCenterPage.test.tsx` 与证据。
- 测试结果：3 个相关测试文件、`27 passed`；diff check PASS。
- 实际收益：测试重新绑定产品语义与共享请求权威，不再被无关的重复文本节点
  数量影响。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #135 / CO-139 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Phase 5 Alembic 回归仍要求 `alembic/env.py` 包含字面
  `DATABASE_URL`，而当前数据库权威已统一到 typed settings。
- 修改摘要：测试改为验证 `load_settings().database_url`、显式配置检测及
  Alembic URL 安全注入/百分号转义。
- 修改文件：`tests/test_phase5_runtime_infrastructure.py` 与证据。
- 测试结果：完整 Phase 5 runtime 文件 `9 passed, 1 existing skip`；
  Ruff、diff check PASS。
- 实际收益：数据库迁移测试保护真实配置合同，不再因安全重构后的源文本变化
  产生误报。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #136 / CO-067 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：qualification PostgreSQL/MinIO 目录缺少 run identity、完成状态与
  retention authority，不能安全区分当前服务、发布证据和可回收运行数据。
- 修改摘要：新增 `.qualification_runs/<run-id>` manifest/active marker、
  ACTIVE/COMPLETED/FAILED、14 天 TTL、release evidence 永久保护；默认只读
  dry-run，显式 apply 仅移动至 recoverable archive。
- 修改文件：retention policy/script/tests、`.gitignore` 与证据。
- 测试结果：focused `7 passed`；真实仓库 dry-run candidate 0、legacy
  directories unmanaged；Ruff、compileall、diff PASS；live runtime 的
  PostgreSQL/Redis/MinIO/worker 均健康。
- 实际收益：后续资格运行可安全回收而不误删当前服务或历史封板证据。
- 提交/CI：未提交、未推送；当前 legacy 服务目录保持不动。

## Continuous optimization — Improvement #137 / CO-068 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：磁盘 preflight 只有卷剩余空间，不能脱敏地区分 workspace、数据库、
  MinIO、日志、qualification profiles 与 build/test caches 的容量占用。
- 修改摘要：增加六类 bounded storage budget projection；PostgreSQL 使用
  只读 `pg_database_size`，MinIO 最多扫描 10,000 objects，filesystem 最多
  100,000 entries 且不跟随 symlink；admin 再次 allowlist 输出。
- 修改文件：storage budget、operations/admin projection、focused tests 与
  证据。
- 测试结果：相关矩阵 `20 passed, 1 existing integration skip`；storage
  focused `6 passed`；Ruff、diff PASS；真实同栈容量扫描完整。
- 实际收益：服务健康与容量提醒不再混淆；发现 build/test caches
  40,349,971,256 B（150.32%），另登记 CO-140，当前没有删除文件。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #138 / CO-120 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：旧 quickstart 混用 retained same-stack、default-port Compose 与手工
  Uvicorn/Next 路径，新 checkout 还缺少 launcher 需要的 production build。
- 修改摘要：统一 lockfile-driven Windows quickstart；增加匹配的
  `.cache/next-production` build、服务端口预检、动态 Alembic head、
  `/health/runtime`、`-CheckOnly` 和 repository-scoped old frontend cleanup。
- 修改文件：release quickstart、focused contract test 与证据。
- 测试结果：focused `5 passed`；Alembic head
  `0031_product_search_keyset`；live check-only 验证 55434/6379/9000/
  8005/3023、Redis workers 与 DeepSeek 健康；Ruff、diff PASS。
- 实际收益：启动、验证和旧实例清理不再存在互相冲突的文档路径。
- 提交/CI：未提交、未推送；现有服务和浏览器未重启或关闭。

## Continuous optimization — Improvement #139 / CO-140 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：113 个 Next build caches 占用 40.35 GB，历史构建与当前 3023
  活动构建混在同一工作区，直接递归清理可能破坏运行页面。
- 修改摘要：新增只允许 direct `apps/web/.next*` 的 dry-run/fingerprint/
  re-scan cleanup authority；Git tracked、symlink、近 24h、活动 BUILD_ID 与
  `apps/web/.cache` 永久排除。
- 修改文件：build-cache cleanup script/tests 与证据。
- 测试结果：相关 `14 passed`；计划 105 candidates、0 tracked/bad；精确
  apply 删除 38,056,000,111 B；清理后 2,293,972,298 B、预算 8.55%；
  frontend 原 PID 29664 仍 HTTP 200，API/DB/Redis/MinIO/workers 健康。
- 实际收益：释放 35.44 GiB，同时不停止服务、不碰源码/科学数据/证据。
- 可恢复性：被删目录不在回收站、不可直接恢复，但全部是 Git-ignored、
  可重新构建的生成物。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #140 / CO-141 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：Platform Provider credential 与 legacy `/me/secrets` 使用
  process-local dictionary，多 API 进程/重启会丢失或分裂 credential
  authority，部分前端合同还错误暗示持久化。
- 修改摘要：新增 `0032_provider_connections` 与 PostgreSQL encrypted shared
  repository；durable 写入强制 stable Fernet key；Provider mutation 限定
  platform admin；same-stack legacy secret API 返回 typed 503；所有 local
  secret lookup/delete/usage 强制 exact user scope；删除浏览器 legacy secret
  client、`secretId` 和陈旧文案。
- 修改文件：Provider migration/repository/routes、legacy secrets store/routes、
  Model Settings/Planner client/messages、focused tests 与证据。
- 测试结果：backend `84 passed`；frontend `40 passed`；typecheck、Ruff、
  compileall、diff PASS。真实 PostgreSQL 备份 SHA-256
  `7AC281AC9E49D08B3121EAA94CDCDE98685370905EEFBE3F5FD7D0A707F91DC1`；
  独立进程 encrypted write/read/decrypt PASS；authenticated `/me/secrets`
  返回 `503 LEGACY_USER_SECRET_API_UNAVAILABLE`。
- 运行时：先启动/验证影子 8006，再停止旧 8005 PID `29356/22124`，启动新
  8005 PID `29280`，最后停止影子；frontend PID `29664` 未中断，8006 无
  listener，PostgreSQL/Redis/MinIO/workers 均健康。
- 实际收益：Provider connection 成为共享、加密、可重启的一致 authority；
  legacy surface 不再制造错误持久化承诺；服务换代后没有重复 API 占内存。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #141 / CO-142 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：API 的 migration-head guard 与 interrupted-work recovery 仍依赖
  FastAPI 已弃用的 `@app.on_event("startup")`，框架升级会威胁启动安全和
  执行顺序。
- 修改摘要：统一为 app-factory-scoped async lifespan；migration validation
  保持第一步且 fail-fast；recovery 保持 best-effort；各 `create_app()` 捕获
  自己的 settings；新增顺序、失败与实例隔离测试。
- 修改文件：`apps/api/mdi_api/main.py`、`tests/test_api_lifespan.py` 与证据。
- 测试结果：combined lifespan/migration/recovery/API `49 passed`；严格
  `DeprecationWarning` gate `7 passed`；Ruff、compileall、diff PASS。
- 运行时：影子 8006 同栈启动且无旧 warning；随后停止旧 8005
  `29280/27464`，启动新 8005 `20748/16260`，最后停止影子
  `19060/21200`；8006 无监听，frontend PID 29664 未中断。
- 实际收益：启动安全、恢复和框架生命周期对齐，且服务换代后没有重复 API
  占用内存。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #142 / CO-143 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：`test_phase14r_recovery.py` 使用 `UUID` 类型注解但未导入；pytest
  因 postponed annotations 通过，Ruff 则产生两个 F821。
- 修改摘要：在既有 `uuid` import 中补充 `UUID`，不修改任何运行时代码。
- 修改文件：recovery test 与证据。
- 测试结果：完整 recovery 文件 `6 passed`；Ruff、compileall、diff PASS；
  live frontend/API/PostgreSQL/Redis/MinIO/workers 保持健康，8006 仍关闭。
- 实际收益：恢复测试同时满足执行与静态正确性，后续 touched Ruff 可真实
  保护该路径。
- 提交/CI：未提交、未推送；持续优化任务保持处理中。

## Continuous optimization — Improvement #143 / CO-144 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：API 代码换代依赖手工 PID 编排，中断时可能留下旧 canonical 或
  shadow 的 Uvicorn/log-runner 进程继续占用内存。
- 修改摘要：API starter 增加健康门禁与原子 instance manifest；新增默认
  dry-run 的 repository-scoped rotation helper，shadow 健康后才停止旧
  canonical，且只按 PID、父子关系、创建时间、可执行文件与命令摘要精确停止
  child→runner；新 canonical 和 frontend proxy 验证后回收 shadow。首次真实
  shadow 揭示 PowerShell 布尔数组解析歧义，已改为 11 个命名括号化检查并
  复测通过。
- 修改文件：API starter/rotation、focused tests、运行手册、ADR、优化台账与
  `co-144-api-rotation-process-ownership-2026-09-05.json`。
- 测试结果：startup/rotation/log/runtime focused `20 passed`；PowerShell AST、
  diff check PASS。真实轮换旧 child/runner `20748/16260` → 新
  `18468/19620`；8005 listener=1、8006=0、旧 PID 均不存在、shadow manifest
  不存在。frontend `29664`、六类 worker、PostgreSQL `11720`、Redis `7284`、
  MinIO `12552` 均保持原 PID；direct/proxy runtime fingerprint 一致。
- 运行健康：operations alerts=0、worker healthy=6、queue depth=0、
  idle-in-transaction=0、pool checked-out=0。
- 实际收益：以后新服务健康后会自动精确回收被替换的旧服务，不再依赖手工
  停进程，也不会让旧/影子 API 持续占用内存。
- 新发现：CO-145，MinIO bounded scan 已达到 8,739/10,000，需要在触顶时
  明确报告 incomplete/unknown，而非伪造完整容量精度。
- 提交/CI：未提交、未推送；持续优化任务保持处理中，当前服务继续运行。

## Continuous optimization — Improvement #144 / CO-145 (2026-09-05)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：MinIO bounded scan 接近 10,000-object 上限；截断时下游仍可能展示
  伪精确 utilization，且 operations 没有 typed warning。
- 修改摘要：触顶和 continuation 缺失分别输出稳定 reason；截断扫描保留
  已观测 bytes/count 下界但 utilization 置空、state=unknown；新增
  `OPS_MINIO_USAGE_SCAN_INCOMPLETE` 及明确“不删除科学 Artifact”的处置指引。
- 测试结果：operations/storage/admin focused `29 passed, 1 existing skip`；
  Ruff、compileall、diff PASS。纯内存 3-object 边界模拟返回
  `MINIO_USAGE_SCAN_LIMIT_REACHED` 且不包含对象键；真实同栈 8,739/10,000
  扫描仍 complete、alerts=0。
- 运行时：受管 API 轮换旧 `18468/19620` → 新 `25704/5060`，旧 pair 已退出，
  8005 listener=1、8006=0，frontend/workers/PostgreSQL/Redis/MinIO 均未停止。
- 实际收益：运维不会把截断下界误当完整容量事实，也不会为容量告警破坏科学
  provenance。
- 新发现：CO-146，live API manifest 应从通用 cache scope 中获得显式保护。
- 提交/CI：未提交、未推送；持续优化任务保持处理中，当前服务继续运行。

## Continuous optimization — Improvement #145 / CO-146 (2026-09-06)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：API 活动 instance manifest 位于通用 `.cache/runtime`，未来缓存
  清理规则扩展时可能误选运行时身份数据。
- 修改摘要：新增共享 `phase14r_runtime_paths.ps1`，API start/rotate 使用
  `.runtime_services/managed/api`；rotate 保留旧路径兼容读取，且只有在
  精确停止旧 child/runner 后才移除旧 manifest；`repo_safe_cleanup.py`
  明确保护 `.runtime_services`。
- 验证：真实同栈轮换 `25704/5060 → 12044/19996`；8005 单监听、8006
  已关闭、旧 manifest 不存在、新 manifest 存在；frontend、六类 worker、
  PostgreSQL、Redis、MinIO 未停止。focused `21 passed`，PowerShell AST、
  Ruff、compileall、diff PASS；safe cleanup candidate=0，build-cache
  dry-run 保留活动前端构建。
- 实际收益：API 进程身份与清理边界现在有显式共享 authority，不会因缓存
  维护误删活动 manifest；旧服务也不会继续占用内存。
- 新发现：CO-147，worker launcher 尚无等价的 repository-scoped identity/
  health manifest 与精确替换证明。

## Continuous optimization — Improvement #146 / CO-147 (2026-09-06)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：stack startup 只判断是否存在任意 worker，缺失一个队列时不会补齐；
  且 plain shell 没有 `PYTHONPATH` 时无法读取 queue manifest。
- 修改摘要：`phase14r_start_stack.ps1` 临时、可恢复地注入
  `packages/schemas`，逐队列匹配 live `worker_entrypoint`，仅把缺失队列
  传给 `phase14r_start_workers.ps1 -OnlyQueue`；manifest 外队列 fail closed。
- 验证：真实 `phase14r_start_stack.ps1 -FrontendPort 3023` 成功；6 个队列
  对应的 12 个 runner/child PID 前后完全一致，无重复 worker、无服务停止；
  runtime 仍为 PostgreSQL/Redis/MinIO。focused `17 passed`，PowerShell
  AST、Ruff、compileall、diff PASS。
- 实际收益：部分 worker 丢失时只恢复缺失队列，不再误判为完整拓扑，也不
  会把普通 shell 的环境问题误报为服务缺失。
- 新发现：CO-148，worker launcher 仍需 per-queue identity manifest 与
  精确替换证明。

## Continuous optimization — Improvement #147 / CO-148 (2026-09-06)

- 状态：已完成并验证；持续优化总任务继续处理中。
- 问题：worker runner/child 归属只能临时从进程命令行观察，未来无法安全精确
  替换或回收。
- 修改摘要：新增 `phase14r_discover_workers.ps1` 和受保护的
  `.runtime_services/managed/workers`；按 checked-in queue manifest 配对
  parent/child，并原子写入 queue、role、handler、Redis URL、PID、创建时间、
  可执行文件、命令摘要和 release SHA；start_workers 启动后自动刷新。
- 验证：真实发现 6/6 并写入 6 个 manifest；现有 12 个 worker 进程全部存活，
  无服务停止；focused `19 passed`，PowerShell AST、Ruff、compileall、diff
  PASS。运维快照首次 MinIO timeout，立即重试 0 alerts、8,739/10,000
  complete，已作为后续 CO-149 记录。
- 实际收益：后续 worker 精确轮换有持久身份依据，不再依赖模糊名称匹配或误杀
  健康 worker。
- 新发现：CO-149，MinIO bounded scan 瞬时 timeout 需要窄范围分类与重试策略。

## Continuous optimization — Improvement #148 / CO-149 (2026-09-06)

- 状态：已完成并验证；持续优化总任务保持处理中。
- 问题：MinIO bounded list 偶发 timeout 会暂时把健康 bucket 显示成容量
  unknown。
- 修改摘要：仅对 shared classifier 标记为 retryable 的 storage failure 做
  一次 50ms 有界重试；认证、not-found 等错误不重试，仍 typed fail-closed，
  不伪造 count/utilization。
- 验证：operations/storage/service-failure `29 passed, 1 skipped`；假客户端
  timeout→success 恰好两次调用并 complete，认证失败仅一次调用并拒绝；真实
  同栈 snapshot `status=ok`、alerts=0、MinIO `8,739/10,000 complete`、
  PostgreSQL/Redis/6 workers 健康。Ruff、compileall、diff PASS。
- 实际收益：瞬态存储抖动不再制造不必要告警，持续/未授权故障仍可见且安全。
- 新发现：CO-150，worker manifest 需先脱敏完整 `redisUrl`，避免凭据落盘。

## Continuous optimization — Improvement #149 / CO-150 (2026-09-06)

- 状态：已完成并验证；持续优化总任务保持处理中。
- 问题：worker manifest 的完整 `redisUrl` 可能携带 Redis credentials，违反
  runtime evidence 不落 secret 边界。
- 修改摘要：持久化字段改为 bounded `redisIdentity`，仅保留 scheme/host/
  port/database；userinfo、password、query、raw URL 均不落盘；重新发现 6 个
  live worker 以原子方式迁移旧 manifest。
- 验证：6 个 manifest secret sentinel=0、raw `redisUrl`=0，身份均为
  `redis://127.0.0.1:6379/13`；12 个 worker 进程全部存活、服务未停止；
  focused `14 passed`，PowerShell AST、Ruff、compileall、diff PASS。
- 实际收益：runtime evidence 不再持久化 credential-bearing Redis URL。
- 新发现：CO-151，消失队列时旧 manifest 需有显式 stale 状态，避免误读为
  活动身份。

## Continuous optimization — Improvement #150 / CO-151 (2026-09-06)

- 状态：已完成并验证；持续优化总任务保持处理中。
- 问题：worker 消失后旧 `worker-*.json` 仍可能看起来像活动身份。
- 修改摘要：found queue 写入 `RUNNING`、`lastSeenAt`、`staleSince=null`；
  missing queue 原子标记 `MISSING` 并保留 lastSeen/staleSince，不删除证据；
  迁移同时移除旧 raw `redisUrl`。
- 验证：live discovery 6/6、6 manifests 全部 RUNNING、12 worker 进程存活；
  focused `14 passed`，PowerShell AST、Ruff、compileall、diff PASS；为保护
  当前健康 worker 未执行破坏性 stale simulation，已明确记录。
- 实际收益：过期身份不会再被默认为活动进程，且故障恢复证据可保留。
- 新发现：CO-152，增加 manifest-authorized dry-run/health-gated worker
  精确轮换 helper。

## Continuous optimization — Improvement #151 / CO-152 (2026-09-06)

- 状态：已完成并验证；持续优化总任务保持处理中。
- 问题：worker manifest 已有但没有安全消费方，未来可能回到手工 PID 操作。
- 修改摘要：新增 `phase14r_rotate_workers.ps1`；默认 dry-run，验证
  repository/release、runner/child 存在与 parentage、创建时间、可执行文件、
  命令摘要、queue command、redacted Redis identity；Apply 限制单 queue 并
  经过 `ShouldProcess`。
- 验证：live dry-run 6 个 queue 全部通过、12 个 worker PID 前后不变、服务
  未停止；focused `16 passed`，PowerShell AST、Ruff、compileall、diff PASS。
- 实际收益：worker 替换有 fail-closed 的精确计划，不再依赖手工 PID。
- 新发现：CO-153，Apply 必须在停旧前验证 replacement 的真实身份与健康。

## Continuous optimization — Improvement #152 / CO-153 (2026-09-06)

- 状态：已完成并验证；持续优化总任务保持处理中。
- 问题：worker Apply 启动 replacement 后只固定等待 2 秒，未证明新 pair
  真实可用就可能停旧。
- 修改摘要：按 exact queue + generation worker name 发现 replacement；停旧
  前验证 parentage、queue command、Redis identity、runner/child liveness；
  admission 失败保留旧 pair，后续失败按 digest 精确回滚 replacement。
- 验证：focused `16 passed`，PowerShell AST、Ruff、compileall、diff PASS；
  live dry-run 6 queue 验证通过，12 worker PID 前后不变，未停止服务。
- 实际收益：未证明的 replacement 不能再授权旧 worker 下线。
- 新发现：CO-154，补 Redis/RQ registration 与 expected queue/state 健康门禁。

## Continuous optimization — Improvement #153 / CO-154 (2026-09-06)

- 状态：已完成并验证；持续优化总任务保持处理中。
- 问题：OS 进程存活不能证明 replacement 已注册到 Redis/RQ；强制停进程还会
  留下 stale registration，造成重复 worker 观测。
- 修改摘要：新增 `phase14r_worker_registration.py`，按 exact name、exact
  single queue、healthy state、900 秒 heartbeat 做脱敏 probe；rotation 停
  旧后 exact `register_death()`，失败 rollback 只清理已验证 replacement；
  修复 child matcher 排除 `phase14r_log_runner.py`。
- 验证：首次 Apply 在停旧前 fail-closed；修复后真实 `mdi-jobs`
  `18684/26300 → 29512/2972` 成功。RQ worker count=6、每个 queue 唯一、
  queue depth=0；old/failed replacement pair 全部退出。focused registration
  `7 passed` + rotation `16 passed`，PowerShell AST、Ruff、compileall、diff
  PASS。PostgreSQL/Redis/MinIO/API/frontend 未停止。
- 实际收益：未注册或错误队列 replacement 不能授权停旧，stale RQ identity
  会被精确清理。
- 新发现：CO-155，MinIO bounded scan 需保留带 freshness 的 last-known-
  complete 状态，不能将 stale capacity 当 current。

## Continuous optimization — Improvement #154 / CO-155 (2026-09-06)

- 状态：已完成并验证；持续优化总任务保持处理中。
- 问题：MinIO bounded scan 瞬态 timeout 时，健康 API 进程缺少连续诊断上下文。
- 修改摘要：operations 增加 endpoint/bucket keyed、5 分钟、线程安全的
  in-process last-known-complete cache；timeout 当前值仍 null/incomplete，
  仅附 authoritative=false 的 age/value；过期仅 marker，不暴露 stale 数值。
- 验证：operations/storage/service-failure `31 passed, 1 skipped`；API
  受管轮换 `12044/19996 → 26224/21772`，前端代理和同栈健康保持；Ruff、
  compileall、diff PASS。独立 CLI 每次新进程，不共享此缓存，已明确记录。
- 实际收益：运维可看到有界连续上下文，同时任何 stale 容量都不会替代当前
  scientific/storage truth。
- 新发现：CO-156，独立 CLI 是否需要受保护 TTL observation cache，或统一
  文档化进程边界并分类。
- 任务：CO-156（跨进程 MinIO observation cache）
  - 状态：已完成
  - 完成时间：2026-09-06
  - 修改摘要：为独立 operations CLI 增加受保护的 SHA-256 keyed runtime
    observation file；采用 5 分钟 TTL、原子写入、secret-free payload、未来
    时间戳拒绝和过期清理。超时快照仍保持 current unknown，旧值只作为
    `authoritative=false` 的诊断上下文。
  - 修改文件：`apps/api/mdi_api/operations.py`、
    `tests/test_phase14r_operations.py`、CO-156 evidence、优化台账及持久化进度文档。
  - 测试结果：operations/storage/service-failure `33 passed, 1 skipped`；
    Ruff、compileall、git diff --check 通过；同栈 CLI 运行正常并显示
    PostgreSQL/Redis/MinIO、6 workers。
- 提交/CI：待本地聚焦提交；未推送。

## Continuous optimization — final closeout (2026-09-06)

- 任务：Materials Intelligence Platform — Continuous Autonomous Optimization
- 状态：已完成
- 完成时间：2026-09-06T12:00:00+08:00
- 修改摘要：完成 CO-156 受保护跨进程 MinIO observation cache，并完成收口期间
  发现的报告状态选择器可访问性、Alembic 日志/迁移兼容性、单元测试运行时
  隔离、mandatory service qualification 同栈环境统一及 Windows Unicode 输出
  兼容修复。白名单提交包含已验证的连续优化代码、测试、配置、文档和证据；
  用户-owned 文件与服务运行目录未提交。
- 验证：
  - `validate_optimization_ledger.py`：discovered=156, completed=156,
    blocked=0, remaining=0, current=NONE。
  - 默认缓存路径全后端：2188 passed, 14 skipped, 108 deselected。
  - 同栈 PostgreSQL/Redis/MinIO：selected=74, passed=74, failed=0,
    errors=0, skipped=0。
  - 前端：117 files / 950 tests passed；typecheck、production build、
    compileall、Ruff、git diff --check 通过。
  - `/health/runtime`：database=postgresql、redis=redis、artifactStorage=minio、
    worker=redis、llmProvider=deepseek。
- 提交/CI：本地收口提交 `510f73a` 已创建；本轮未推送，未关闭 API、worker、
  PostgreSQL、Redis、MinIO 或现有浏览器标签页。
## Materials Intelligence Platform — Autonomous Architecture Migration B0-5 through B0-7

- 状态：已完成，达到 `AUTONOMOUS_MIGRATION_MILESTONE_REACHED`。
- 完成时间：2026-09-07T00:00:00+08:00。
- 工作区：`E:/1project/mdi-b0-5a1`，未创建新工作树或分支，未推送。
- 修改摘要：完成剩余 Batch 0 persistence canonical ownership preparation；
  新增 B0-6 deterministic canonical import-boundary guard；新增 B0-7
  read-only deterministic architecture report。保留旧 public/dynamic paths、
  六个 worker handler dotted identities、六个 queue names、Tool/Adapter
  identities 和现有 scientific/persistence authorities。未执行物理文件迁移。
- 提交：`0469ebd`、`6ae2394`、`5824998`。
- 测试：architecture/worker/queue focused `30 passed`；milestone focused
  persistence/research `209 passed, 4 skipped`（排除外部 PostgreSQL API
  用例）；compileall、Ruff、architecture guard、architecture report、
  `git diff --check` 通过。一个 API 用例因既有外部 PostgreSQL
  `OperationalError` 失败，分类为 PRE_EXISTING/ENVIRONMENTAL。
- 硬不变量：API、授权、数据库 schema/Alembic、事务、持久化 ID、queue/
  handler、Tool/Adapter、scientific identity、UI behavior 均未改变。
- 后续：等待一次 reviewer 评审后再授权 physical relocation；本轮不执行
  物理迁移。

## Materials Intelligence Platform — Autonomous Physical Relocation

- 状态：已完成；达到 `AUTONOMOUS_PHYSICAL_MIGRATION_COMPLETE`。
- 完成时间：2026-09-08T17:42:36+08:00。
- 工作区：`E:/1project/mdi-b0-5a1`；从
  `db75aa57136e4512b11b6fe69bb54840ad970323` 开始，未创建新工作树或分支，
  未推送。
- 修改摘要：完成后端 persistence/database/workspace/history/scientific
  object/result/report/interpretation/Agent2/report composition/Phase2/router
  implementation 的 canonical 物理归位；完成前端 shared layout/UI/workspace/
  observability、Projects/Data/Research/Reports/Planner/product centers 与
  scientific viewer 实现归位；保留 frozen worker 与旧 public/test 路径的薄
  compatibility facade，并将 B0-6 allowlist 从 5 降至 4。
- 测试结果：architecture guard/checker PASS（forbidden/cycle/canonical-to-
  compatibility 均为 0，handler 6/6，queue 与 Tool/Adapter identity PASS）；
  focused architecture `12 passed`；database pool `2 passed, 1 skipped`；
  backend broad `2211 passed, 76 failed, 75 skipped`，76 个失败节点与迁移前
  基线一致，新增回归 0；frontend `117 files / 950 tests`、typecheck、build
  PASS；compileall、Ruff、git diff check PASS。
- 安全结果：API/auth/schema/Alembic/transaction/persisted IDs/queue/handler/
  Tool/Adapter/scientific/UI behavior 均未改变；测试生成 evidence 已恢复；
  未修改 runtime 或 forensic 数据。
- 提交/CI 状态：物理迁移、兼容调整与本条收口记录形成线性本地提交；
  最终 SHA 以当前 Git HEAD 为准；未推送，未运行远程 CI。


## Materials Intelligence Platform — Final Repository Closeout Review

- 状态：已完成，结论为 `FINAL_REPOSITORY_CLOSEOUT_REVIEW = REPAIRED_AND_PASS`。
- 完成时间：2026-09-08T21:30:00+08:00。
- 工作区：`E:/1project/mdi-b0-5a1`；未创建新工作树或分支，未推送。
- 修改摘要：独立复核 `db75aa57136e4512b11b6fe69bb54840ad970323` 至迁移收口的
  30 个迁移/修复提交；确认无无关迁移提交、重复 authority 或 canonical 到
  compatibility 依赖。修复两处真实窄边界缺陷：后端 canonical 模块的旧 facade
  import，以及前端 feature 模块的旧组件 import，并同步受影响测试 mock。
- 测试结果：architecture guard/checker PASS；forbidden edges=0、cycles=0、
  canonical-to-compatibility=0、handler=6/6、queue PASS、Tool IDs=62、
  Adapter IDs=50；frontend `117 files / 950 tests`、typecheck、build PASS；
  backend current rerun `2212 passed, 76 failed, 75 skipped`，76 个失败仍与
  已记录迁移前基线一致，新增回归 0；compileall 与 `git diff --check` PASS。
- 安全/后续：测试生成 evidence 已恢复；未修改 runtime、Redis、数据库、MinIO
  或 forensic tree。远程 CI 未运行；后续仅进入 retention 与 PROJECT_STATE
  transition review，不执行删除或状态 authority 替换。
- 提交/CI 状态：本地窄修复提交 `0977769`、`f54464b`；本次收口记录另行
  创建本地提交；未推送，未运行远程 CI。


## Materials Intelligence Platform — Retention and PROJECT_STATE Transition Review

- 状态：已完成，结论为 `RETENTION_AND_PROJECT_STATE_TRANSITION_REVIEW = PASS`。
- 完成时间：2026-09-08T21:57:45+08:00。
- 工作区：`E:/1project/mdi-b0-5a1`；HEAD 为
  `f3c6fa055d447ec6e25cabc7e9825ebbb769bba8`；未创建新工作树或分支，未推送。
- 修改摘要：只读盘点 TASKS/results、persistent ledgers、roadmap/scope、
  frozen architecture/qualification/evidence、runtime-adjacent paths、ignore
  rules 及 reader/writer/dynamic references。确认现有 authority 分层、未来
  retention gates、PROJECT_STATE compact snapshot 角色、冲突胜者、staleness
  model 与 additive dual-read/dual-write phases。
- 结果：当前 state authorities 已盘点；runtime/user-unknown/historical/
  qualification/current-operational-ledger 已分类；仅明确生成且非权威的
  cache/dependency families 可作为未来候选，当前 safe-cleanup dry-run
  `candidateCount=0`。`TASKS.md` 与 `results.md` 均不可立即退休。
- 测试/验证：`python -m pytest tests/test_repo_safe_cleanup.py -q` 为
  `4 passed`；`python scripts/repo_safe_cleanup.py --dry-run --older-than-days 30`
  为 0 candidates；未运行广泛 suite，未修改 runtime/evidence。
- 安全状态：FILES_DELETED=0、FILES_ARCHIVED=0、PROJECT_STATE_CREATED=NO、
  READERS_MIGRATED=NO、RUNTIME_STATE_CHANGED=NO、EVIDENCE_REWRITTEN=NO、
  SOURCE_ARCHITECTURE_CHANGED=NO。远程 CI 未运行。
- 后续：可进入“分阶段 PROJECT_STATE 引入 + 有界 retention execution”审查；
  仍需将 PROJECT_STATE introduction 与 cleanup 作为独立子阶段，历史/
  qualification authority 暂不退休。


## Materials Intelligence Platform — Phased PROJECT_STATE Introduction and Bounded Retention Execution

- 状态：已完成，结论为 `PHASED_PROJECT_STATE_AND_RETENTION_EXECUTION = PASS`。
- 完成时间：2026-09-08T22:20:00+08:00。
- 修改摘要：创建 `PROJECT_STATE.md` additive snapshot；更新 `AGENTS.md` 和
  transition plan 以启用高层 dual-read；定义受控 snapshot update/freshness
  规则；完成 PROJECT_STATE/TASKS/results/persistent/docs/qualification/
  dynamic-contract/Tool Registry 的 reverse-reference audit。
- 清理结果：`python scripts/repo_safe_cleanup.py --dry-run
  --older-than-days 30` 返回 `candidateCount=0`，执行
  `BOUNDED_CLEANUP_EXECUTION=NO_OP_PASS`；未删除、未归档、未移动任何材料。
- Authority 状态：`TASKS.md`、`results.md`、ADR、qualification/CI、
  dynamic/runtime identity、Tool Registry、roadmap/scope、历史证据和
  runtime/user-owned surfaces 均保留为各自权威；`PROJECT_STATE.md` 仅作
  当前快照和导航。
- 测试/验证：state pointer/queue contract PASS；focused task/result/cleanup
  tests `9 passed`；`git diff --check` PASS；未运行 broad product suites，
  因为无产品源代码变更。
- 安全状态：`PROJECT_STATE_CREATED=YES`、`HIGH_LEVEL_DUAL_READ_ACTIVE=YES`、
  `TASKS_AUTHORITY_PRESERVED=YES`、`RESULTS_AUTHORITY_PRESERVED=YES`、
  `RUNTIME_STATE_CHANGED=NO`、`USER_OWNED_DATA_CHANGED=NO`、
  `HISTORICAL_EVIDENCE_RETIRED=NO`、`QUALIFICATION_EVIDENCE_RETIRED=NO`、
  `SOURCE_ARCHITECTURE_REOPENED=NO`、`PUSHED=NO`。
- 提交/CI 状态：本地提交 `cd5d3b3`、`c1a790a`、`e87c2d1` 及最终记录提交；
  未推送，未运行远程 CI。下一步为 PROJECT_STATE stabilization/release
  readiness review。


## Materials Intelligence Platform — PROJECT_STATE Stabilization and Release Readiness Review

- 状态：已完成；`PROJECT_STATE_STABILIZATION_REVIEW=PASS`，
  `RELEASE_READINESS_STATUS=CONDITIONAL`。
- 完成时间：2026-09-08T22:45:00+08:00。
- 稳定化结果：真实 TASKS 演化暴露一个 bounded Active Work drift；`TASKS.md`
  始终保持正确 authority。PROJECT_STATE 已协调，并新增 effective-stale
  检测规则：即使 stored status 为 CURRENT，也必须核对被摘要字段。
- Freshness：Case A snapshot-only 保持 CURRENT；Case B TASKS 变化要求
  reconciliation；Case C qualification authority 胜出；Case D architecture
  authority 胜出并在协调前视为 stale。四类静态验证均 PASS。
- Dual-read：高层 Agent reader 使用 PROJECT_STATE 做导航；task queue、
  result ledger、architecture、qualification、runtime/dynamic identity 和
  Tool Registry readers 未被重定向。
- Runtime unknown：live RQ registration、live DB migration head、
  runtime/user-owned data ownership 均为 `STILL_UNKNOWN_PROTECTED`。
- Release readiness：repository GitHub Actions workflow 和 authenticated
  `gh` CLI 可用；未推送、未运行 remote CI。未来 release 必须通过单独授权的
  current-HEAD remote CI 和 mandatory PostgreSQL/Redis/MinIO qualification。
- 验证：PROJECT_STATE role/pointers/freshness checks PASS；focused
  task/result/cleanup tests `9 passed`；safe-cleanup dry-run
  `candidateCount=0`；应用源码 diff=0；`git diff --check` PASS。
- 安全：FILES_DELETED=0、HISTORICAL_RETIREMENT=0、
  QUALIFICATION_RETIREMENT=0、RUNTIME_MUTATION=0、
  SOURCE_ARCHITECTURE_REOPENED=NO、PUSHED=NO。


## Materials Intelligence Platform — Exhaustive Pre/Post Capability Parity Audit (2026-09-08)

- 状态：已完成
- 基线：`db75aa57136e4512b11b6fe69bb54840ad970323` → 当前审计头 `376436df67738bbf9901622edd5153e605ae7c3c`
- 修改文件：`docs/agent2/capability_parity/EXHAUSTIVE_PRE_POST_CAPABILITY_PARITY_AUDIT_TASK.md`、`docs/agent2/capability_parity/PRE_POST_CAPABILITY_PARITY_AUDIT.md`、`docs/agent2/capability_parity/capability_parity_ledger.json`、`docs/agent2/capability_parity/capability_parity_ledger.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`。
- 修改摘要：独立从 Git baseline/current source 建立前端 35 个 route/support 文件、20 个 page entrypoints、1,771 个 UI 声明记录、后端 168 个 OpenAPI operations、958 个 public/non-HTTP 记录、763 个 reduced-file 记录、198 个缩减实现文件、dynamic/worker/queue/tool/adapter 身份、SLOC 与测试覆盖映射。确认静态能力 parity，无 missing/unaccounted capability；`phase2_runtime._content_type_for_name` 已对账为 canonical `content_type_for_name`。
- 测试结果：OpenAPI method/path/schema/security/status comparison `168/168`；route set difference `0`；current production-server HTTP smoke `20/20` 返回 `200`；B0-6 guard `PASS`（forbidden `0`，allowlisted `4`）；B0-7 report `PASS`（cycles `0`，canonical→compatibility `0`，handlers `6/6`，queues `PASS`，Tools `62`，Adapters `50`）；`git diff --check` 通过。认证 arbitrary-ID browser render 未宣称通过，标记 `NOT_RUNTIME_VERIFIED`。
- 审计结论：`PRE_POST_CAPABILITY_PARITY_AUDIT = PASS`；`FULL_PRE_POST_CAPABILITY_PARITY = YES`（static/source-contract scope）；`SAFE_TO_PROCEED_TO_REMOTE_RELEASE_GATE = YES`。
- 提交/CI 状态：待本地审计提交；未推送；未运行 remote CI；无应用源码、数据库、运行时数据、证据或 forensic baseline 变更。


## Materials Intelligence Platform — Final Residual Ownership and Repository Hygiene Review

- 状态：已完成，结论为
  `FINAL_RESIDUAL_OWNERSHIP_REVIEW = REPAIRED_AND_PASS`。
- 完成时间：2026-09-09T10:21:13+08:00。
- 修改摘要：使用 AST、导入图、reverse-reference、runtime identity 与 LOC
  对 85 个后端和 138 个前端 residual-scope production-path 文件完成逐项
  ownership 分类。确认 `mdi_api.repositories` 为零实现声明的 public API
  aggregator，`mdi_api.db` 为稳定 SQLAlchemy metadata/table foundation，
  frontend `app/components` production implementation body 为 0。
- 修复：将遗漏在 `mdi_api.scientific_results.queue` 与
  `mdi_api.scientific_results.reconciler` 的真实实现迁至
  `mdi_api.infrastructure.scientific_results`，旧模块保留真 re-export；
  recovery 改用 canonical owner。未改变 queue/handler/job/result/transaction
  语义。
- 最终计数：`UNRESOLVED_RESIDUALS=0`、
  `DUPLICATE_BUSINESS_IMPLEMENTATIONS=0`、
  `CANONICAL_TO_COMPATIBILITY_IMPORTS=0`、
  `MIGRATION_RESIDUES_FIXED=2`。合法 compatibility facades 189、runtime
  entrypoints 4、foundation modules 10。
- 前端测试债务：`LEGACY_TEST_COLOCATION_DEBT=YES`，98 个 colocated test
  文件与 4 个 test-only fixture support 文件；`BLOCKING=NO`。
- 测试/验证：focused ownership/queue/worker/architecture `57 passed`；
  changed-source compile、Ruff、architecture guard/report、ledger assertions
  与 `git diff --check` PASS；handlers 6/6、6 queues、62 Tools、50 Adapters
  不变。
- 安全状态：source architecture 与 capability parity 未重开；API、auth、
  schema/Alembic、transaction、persisted identity、scientific authority、UI、
  runtime/user data、historical/qualification evidence 均未改变。
- 提交/CI 状态：源码修复提交 `8e91432`；本结果与分类账随最终审查记录提交
  固化（exact hash 以 Git history 为准）；未推送，未运行 remote CI。
- 后续：`REMOTE_QUALIFICATION_AND_RELEASE_GATE_REVIEW`。

## Materials Intelligence Platform — Remote Qualification and Release Gate Review

- 状态：已完成；`REMOTE_QUALIFICATION_AND_RELEASE_GATE_REVIEW=CONDITIONAL`。
  `LOCAL_AND_SERVICE_QUALIFICATION=PASS`、`RELEASE_READY_LOCAL=YES`，但最终
  exact SHA 尚未获准 push，故 `RELEASE_READY=NO`、remote CI 未运行。
- 完成时间：2026-09-09T13:30:00+08:00。
- Evidence reconciliation：ownership-specific queue/worker subset 为
  `25 passed`；expanded residual-review focused suites 总计 `57 passed`，两者
  scope 不同且均保留。
- 修复摘要：提交 `0f3f835` 恢复 retained same-stack 六 worker 启动；`e58720d`
  修复 Windows PID reuse 资格假设；`0b8167b` 固化 production frontend
  API proxy、release-SHA build wiring 和 exact proxy preflight。未改变 API、
  auth、schema/Alembic、transaction、persisted identity、queue/handler、
  Tool/Adapter、scientific 或 UI 语义。
- 真实服务资格：PostgreSQL connection/pool/repository/rollback PASS，Alembic
  `0032_provider_connections`；Redis PASS，live workers `6/6`；MinIO
  qualification-owned put/get/delete PASS；mandatory critical path
  `74 passed, 0 failed, 0 errors, 0 skipped`。
- 浏览器/前端：authenticated Chromium representative routes、real API proxy、
  persisted Project ID reopen PASS；fatal page/server/chunk/import errors=0；
  frontend `117 files / 950 tests`、typecheck、production build PASS。
- 本地门禁：architecture cycles/forbidden/canonical→compatibility 均为 0；
  allowlist 保持 4；handlers 6/6、queues 6、Tools 62、Adapters 50；lock、CI
  pins、provenance、secret redaction、runtime config、diff check PASS。
- Remote 状态：`origin`、workflow 和 authenticated `gh` 可用，但最终 SHA 不在
  remote；`REMOTE_PUSH_AUTHORIZATION_REQUIRED=YES`、`REMOTE_CI_STATUS=NOT_RUN`。
  下一步仅是在单独授权后 push exact SHA，并对同一 SHA 运行现有 workflow。
- 安全：未重开 migration/capability parity；未 flush queue、删除用户对象、
  修改 forensic PostgreSQL、创建 branch/worktree 或 push。

## Material Data Intelligence — Canonical Worktree Recovery & Workstream B Continuation

- 状态：已完成；canonical active root 为
  `E:\1project\mdi-b0-5a1`，旧 `E:\1project\Material Data Intelligence`
  仅保留为 historical/comparison/recovery source，未继续开发或整体复制。
- 完成时间：2026-09-10T12:03:18+08:00。
- Workstream A：将已完成的 ResearchTurn lifecycle projection、stage owner/
  latency、ContextSnapshot summary、durable correlation、failure category 与
  minimum safe recovery action 语义恢复到 migrated canonical owner。
- Workstream B：恢复并完成 typed provenance、source authority、freshness、
  epistemic status、exact object/version/Result refs、project authorization、
  provenance deduplication、purpose budget/degradation、memory grounding/
  ranking、continuation reuse 与 Research context disclosure。
- 修改摘要：实现提交 `aac8ef4`；未创建第三套实现、未恢复旧 ownership、
  未改 schema/Alembic、queue/handler、Tool/Adapter、public API 或 scientific
  identity。
- 测试结果：focused backend `83 passed, 15 warnings`；Research UI
  `93 passed`；Ruff、compileall、typecheck、production build、
  architecture guard/report、`git diff --check` PASS。Phase 2 exact manifest、
  Phase 3 planning、Phase 4 worker execution、Phase 7 continuation/exact
  historical version service flows PASS。
- Runtime：canonical stack check PASS；PostgreSQL、Redis、MinIO、API 和
  frontend healthy；canonical worker discovery `6/6` queues。
- 提交/CI 状态：实现提交 `aac8ef4`，本记录由随后本地 docs/state 提交固化；
  未 push，未运行 remote CI。

## Material Data Intelligence — Workstream C: Scientific Capability Extension Platform

- 状态：已完成；`SCIENTIFIC_CAPABILITY_EXTENSION_FOUNDATION=READY`，
  `UNRESOLVED_CAPABILITY_PLATFORM_BLOCKERS=0`。
- 完成时间：2026-09-10T13:20:59+08:00。
- 实现摘要：将现有 Requirement → Capability → Capability Pack → Tool →
  Adapter → Artifact → ScientificResult → Presentation 集成规则固化为
  `CapabilityManifest 1.2` 的显式扩展合同；新增 deterministic cross-registry
  completeness validator、canonical JSON/Markdown inventory、orphan
  classification、bounded planner projection 和 fail-closed project-scope
  resolution。未改变 Tool/Adapter ID、queue/handler identity、public API、
  schema/Alembic 或 scientific identity。
- Inventory：17/17 Capabilities valid，5 Packs，62 Tools，50 Adapters，
  17 Result projectors，11 Viewer descriptors，duplicate capability authority=0，
  incomplete capability=0。45 个未被 Agent Capability 直接到达的 Tools 已分类为
  33 个 public low-level 和 12 个 future/experimental surface；不授予清理权限。
- 验证：capability/registry focused `52 passed`；Structure/XRD/Trajectory/
  Electronic/Dataset/ML/Phonon cross-domain regression `169 passed, 1 skipped`；
  isolated canonical PostgreSQL/Redis/MinIO fresh-worker RDF/XRD paths
  `2 passed`；Ruff、compileall、architecture scan/report、queue/worker 和
  Tool/Adapter identity、`git diff --check` PASS。
- 开发者体验：新增 capability platform contract、添加科学能力指南及
  `trajectory.msd → trajectory.diffusion` typed Artifact-port reference path。
  常规 producing capability 仍需在约 5–7 个明确 authority 中做有界注册，
  但不再要求修改 Agent state machine、worker queue、generic Result service、
  Research dispatcher 或 Report engine。
- 提交/CI 状态：实现提交
  `7890644fbdf705534efbe68b65035763263da9ec`；本结果与任务归档由随后本地
  closeout commit 固化；未 push，未运行 remote CI。
- 后续建议：`Workstream D — Scientific Quality & Evaluation`。结构完整性已经
  可自动证明，但大多数 capability qualification metadata 仍保守标记为
  `STRUCTURAL_ONLY`；应先建立 capability-specific reference fixtures、
  limitations 和 scientific benchmark evidence，再扩大自主多步选择。

## Material Data Intelligence — Workstream D: Scientific Quality, Qualification & Evaluation

- 状态：已完成；`SCIENTIFIC_QUALITY_MODEL=COHERENT`，
  `QUALIFICATION_IS_EVIDENCE_BACKED=PASS`，
  `SCIENTIFIC_QUALITY_REPORT=PASS`，
  `REMAINING_SCIENTIFIC_QUALITY_BLOCKERS=0`。
- 完成时间：2026-09-10T14:38:47+08:00。
- 实现摘要：在 canonical Capability registry 上新增 source-referenced、
  version-aware 的科学质量证据合同与 validator；资格状态由实际 reference/
  invariant/domain-negative/Result/interpretation/report evidence 派生，不可由
  manifest 标志手工升级。科学合同 fingerprint 覆盖 capability、Tool、
  Adapter、projector 与呈现绑定，发生相关变化时旧证据显式 stale。
- Inventory：总计 17 个 Capability；`DOMAIN_VALIDATED=6`，
  `REFERENCE_VALIDATED=3`，
  `EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED=8`，
  `STRUCTURAL_ONLY=0`。证据计数：reference 9、invariant 8、
  domain-negative 17、Result projection 2、interpretation 7、report 2；
  validator errors 0。
- 科学诚实边界：external-semantics 类只证明本平台拥有的解析、单位、投影、
  limitation 与呈现语义，不声称独立验证 pymatgen、DFT 或 phonon solver。
  Deterministic interpretation/report 检查证明 bounded corpus 内的数值、单位、
  source、limitation 与 epistemic restraint，不等价于专家级科学洞见。
- 修改文件：`research_agent/capabilities/quality_evidence.py`、
  `quality_validation.py`、Capability schema/defaults/packs/inventory projection、
  `scripts/scientific_quality_report.py`、focused tests、scientific-quality
  docs/generated inventory，以及当前 state/progress/ADR/board/changelog。
- 测试结果：quality/capability focused `20 passed`；Structure/XRD/
  Trajectory/Electronic/Dataset/ML/Phonon cross-domain `196 passed`；
  Result/Interpretation/Report bounded suite `111 passed, 4 skipped,
  1 deselected`（4 个为 live-provider gate）；frontend semantic presentation
  `5 files / 41 tests passed`；architecture `9 passed` 且 canonical forbidden
  edges 0；Ruff、compileall、quality/capability report checks、diff check PASS。
- 真实服务：canonical qualification-owned PostgreSQL、Redis/RQ、MinIO 下
  `6 passed`，覆盖 RDF/XRD Research 执行及 coordination、trajectory、
  electronic、phonon 跨持久化/队列/对象存储语义。
- 已知非 blocker：受保护 Phase 11 历史 evidence byte manifest 在 Windows
  checkout 因 CRLF 为 78 bytes、记录为 74 bytes；相关 substantive tests
  均通过，未改写历史证据。该项是历史 evidence-integrity debt，不是新增科学
  或产品 regression。
- 科学缺陷：`SCIENTIFIC_DEFECTS_DISCOVERED=0`，
  `SCIENTIFIC_DEFECTS_FIXED=0`。
- 提交/CI 状态：实现提交
  `a8cc0c0fd138c2bf0bd742c36636b8c4a6ac438f`；本状态/结果归档由随后本地
  closeout commit 固化；未 push，未运行 remote CI。
- 后续：`READY_FOR_AGENT_AUTONOMY=CONDITIONAL`。Workstream E 可在资格等级、
  applicability、limitations 与 external-semantics 限制下开始；不得把
  structurally available 或外部 solver 语义验证等同于自主科学选择的高置信
  authority。
