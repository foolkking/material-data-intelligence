---TASK---
状态：已完成

# Phase 10M-2 Reviewer Prompt

## Unified Scientific Workspace Shell

你现在执行：

# Phase 10M-2：Unified Scientific Workspace Shell

本阶段是 Phase 10M Unified Scientific Workspace 的正式前端产品壳实现阶段。

本阶段建立：

```text
/workspaces/{workspaceId}
```

对应的统一科学 Workspace 页面，包括：

* Workspace 路由；
* Workspace 数据加载；
* 页面整体信息架构；
* Workspace Header；
* desktop navigation；
* mobile navigation；
* panel switcher；
* panel shell；
* dataset/context drawer；
  -基础 inspector shell；
* Workspace 状态与错误投影；
  -历史 Job 只读状态；
* partial execution 可见性；
* findings/evidence/provenance 的导航入口；
  -从 PlannerWorkbench 进入 Workspace；
  -浏览器 back/forward；
  -页面级 loading、empty、error、stale、unsupported 状态；
* responsive 和 accessibility 基础闭环。

本阶段不实现：

* Phase 10M-3 canonical selection propagation；
* 跨 panel scientific identity 联动；
* Phase 10M-4 typed scientific Artifact Gallery；
* 新科学 renderer；
* WebGL viewer 的 Workspace 深度集成；
* Phase 10M-5 Report/Recipe composition；
* Phase 10M-6 完整 save/recovery 产品闭环；
* Phase 10M-7 最终集成闭合。

本阶段不得重新设计 Phase 10M-0 和 10M-1 已经冻结、实现并归档的 Workspace 合同、持久化、API、迁移、Panel 合同或 Selection 合同。

---

# 0. Reviewer-Authorized Baseline

Phase 10M-1 已完成并归档。

权威结果：

```text
Phase 10M-1:
PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT

corrected implementation:
27c5aa98138f882a750dc76a402ee2afe2151b72

implementation exact-SHA CI:
30705503707 success

completion record:
7f6a3fa...
completion exact-SHA CI:
30706195493 success

queue archive:
08f2133c6a02b64a199f40a0b17ccfa5d0e68cc7

queue archive exact-SHA CI:
30706443734 success

final HEAD:
08f2133c6a02b64a199f40a0b17ccfa5d0e68cc7

branch:
master

migration head:
0007_phase10m1_workspace_domain

TASK_BLOCK_COUNT:
0
```

开始时必须从当前 repository 和 immutable history 恢复完整 completion-record SHA，不得依赖上面的缩写。

Phase 10M-1 已实现：

```text
ScientificWorkspace 1.0
WorkspacePanel 1.0
WorkspaceSelectionContext 1.0
scientific_workspaces
workspace_panels
workspace_layout_revisions
explicit idempotent Job -> Workspace projection
Workspace repositories
Workspace APIs
If-Match optimistic concurrency
layout revision history
historical Job projection
TypeScript Workspace API client
```

已确认：

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
WORKSPACE_UI = NOT_IMPLEMENTED_BY_DESIGN
```

当前唯一允许进入的阶段：

```text
Phase 10M-2:
Unified Scientific Workspace Shell

Phase 10M-3:
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

---

# 1. Permanent DeepSeek-Only LLM Policy

本节从当前阶段开始，适用于本阶段及所有后续阶段。

任何阶段、测试、证据 runner、CLI、API、浏览器 E2E、developer tool 或产品路径，只要实际进行真实 LLM 调用，就必须遵守以下规则。

## 1.1 唯一真实 Provider

```text
provider = DEEPSEEK
base_url = https://api.deepseek.com
api_key_env = DEEPSEEK_KEY
```

只允许使用仓库已经实现并经过 Phase 10L-5 验证的 `DeepSeekProvider` 和现有 OpenAI-compatible transport。

不得新增 DeepSeek SDK。

不得使用：

```text
OpenAI
Anthropic
custom OpenAI-compatible endpoint
Azure OpenAI
local real model
other hosted provider
```

## 1.2 Key 唯一来源

只允许读取：

```text
DEEPSEEK_KEY
```

不得 fallback 到：

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
ANTHROPIC_API_KEY
LLM_API_KEY
SecretStore
database
frontend form
localStorage
sessionStorage
command-line literal
plaintext config
```

不得复制 `DEEPSEEK_KEY` 到另一个变量。

不得记录：

* key 值；
* key 长度；
* prefix；
* suffix；
* hash；
* fingerprint；
* Authorization header；
* environment dump。

只允许记录：

```text
configured = true
```

或：

```text
configured = false
```

## 1.3 无静默降级

`DEEPSEEK_KEY` 缺失：

```text
DEEPSEEK_NOT_CONFIGURED
no request
no fallback
```

真实 DeepSeek 调用失败：

```text
DEEPSEEK_PROVIDER_FAILED
no provider fallback
no Mock fallback
no Deterministic fallback
```

不得为了让 evidence PASS，自动切换到：

* Mock；
* Fake；
* Deterministic；
* OpenAI；
* Anthropic；
* custom endpoint；
* 其他模型。

## 1.4 默认 CI 与真实验证

普通 unit、frontend、service-backed CI 可以继续使用：

```text
Fake DeepSeek transport
deterministic fixtures
REAL_LLM_CALLS = 0
```

普通 CI 不得依赖 secret。

但是：

```text
任何被本阶段声明为“真实 LLM 产品证据”的案例
都必须使用真实 DeepSeek 和环境变量 DEEPSEEK_KEY。
```

不得使用 Mock/Fake 结果冒充真实 LLM evidence。

## 1.5 M2 的具体规则

M2 的核心 Workspace shell 不需要新增 LLM call site。

因此期望：

```text
NEW_LLM_CALL_SITES = 0
```

如果 M2 的真实浏览器案例只打开已经存在的 Workspace，则可以：

```text
REAL_LLM_CALLS = 0
```

如果 M2 的浏览器/API E2E 从自然语言请求开始，并实际生成新 Job 和 Workspace，则该案例必须：

```text
use real DeepSeek
read only DEEPSEEK_KEY
persist only sanitized provider evidence
```

不得使用 Mock Planner 创建新 Job，然后把该路径描述为真实自然语言 Workspace E2E。

## 1.6 Provider Safety

真实 DeepSeek 响应仍然：

* 无直接工具执行权；
* 无 Workspace mutation 权；
* 无 Job/enqueue 权；
* 必须经过 Intent、Eligibility、Plan 和 Runtime 验证；
* 不得改变 Workspace route、panel 或 layout；
* 不得输出或保存 secret；
* 不得通过 recommendation 触发执行。

---

# 2. Canonical Product Goal

项目是：

```text
Material Data Intelligence & Visualization Platform
材料数据智能分析与可视化平台
```

Workspace 用户链路：

```text
Natural-Language Analysis
    ↓
Persisted Job
    ↓
ScientificWorkspace 1.0
    ↓
/workspaces/{workspaceId}
    ↓
Data / Plan / Execution / Results
    ↓
Findings / Evidence / Provenance
    ↓
Report / Recipe
```

M2 的目标是让 Workspace 成为正式用户页面，而不是继续让用户只面对 PlannerWorkbench 的调试式结果堆叠。

---

# 3. Phase 10M-2 Exact Goal

完成后，用户必须能够：

1. 从现有 PlannerWorkbench 成功分析结果进入 Workspace；
2. 通过 `/workspaces/{workspaceId}` 直接打开 Workspace；
3. 刷新页面后重新读取 Workspace identity 和 panel metadata；
4. 查看 Workspace title、Job 状态、数据上下文和版本；
5. 查看 Plan、Execution、Results、Findings、Evidence、Provenance 和 Report/Recipe 的导航入口；
6. 在 desktop 使用正式 Workspace shell；
7. 在 mobile 使用单 active panel、context drawer、panel switcher 和 inspector bottom sheet；
8. 看到 running、partial、failed、stale、legacy 和 unsupported 状态；
9. 通过 panel switcher 查看每个 `WorkspacePanel 1.0` descriptor；
10. 在未实现专业 renderer 时看到诚实的 inert fallback；
11. 使用 back/forward 恢复 active panel；
12. 不产生新的科学计算；
13. 不复制 Artifact payload；
14. 不修改 Job、Plan、Artifact 或 interpretation；
15. 不实现 M3 selection propagation。

M2 完成标准：

```text
一个已经存在的 Workspace
可以通过正式 URL 打开，
并以统一页面壳展示其分析上下文、状态、panel 结构和科学结果入口。
```

---

# 4. Required Canonical Documents

实现前完整阅读：

```text
docs/phase10m/README.md
docs/phase10m/phase10m0_workspace_information_architecture.md
docs/phase10m/phase10m0_workspace_domain_contract_proposal.md
docs/phase10m/phase10m0_workspace_panel_contract_proposal.md
docs/phase10m/phase10m0_workspace_selection_context_decision.md
docs/phase10m/phase10m0_state_and_error_taxonomy.md
docs/phase10m/phase10m0_responsive_accessibility_performance_security.md
docs/phase10m/phase10m0_compatibility_strategy.md
docs/phase10m/phase10m_implementation_backlog.md
docs/phase10m/phase10m_acceptance_and_test_plan.md
docs/phase10m/phase10m_execution_lock.md
docs/phase10m/phase10m_execution_manifest.md
docs/phase10m/phase10m_execution_agent_handoff.md
docs/phase10m/phase10m2_next_scope.md
```

完整阅读 M1 实现文档：

```text
docs/phase10m/phase10m1_workspace_domain_contract.md
docs/phase10m/phase10m1_workspace_persistence.md
docs/phase10m/phase10m1_workspace_api.md
docs/phase10m/phase10m1_historical_job_projection.md
docs/phase10m/phase10m1_security_and_compatibility.md
docs/phase10m/phase10m1_evidence.md
docs/phase10m/phase10m1_completion.md
```

同时阅读：

```text
README.md
AGENTS.md
MASTER_PROMPT.md
docs/index.md
docs/ROADMAP.md
docs/13_SHARED_SCHEMA_SPEC.md
persistent/PROJECT_BRIEF.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/ARCHITECTURE_DECISIONS.md
results.md
TASKS.md
```

并阅读当前真实：

* Next.js route structure；
* PlannerWorkbench；
* Workspace API client；
* frontend query/data-loading conventions；
* Artifact preview components；
* interpretation/finding/evidence components；
* report/recipe components；
* current responsive CSS；
* current browser runners；
* current accessibility test style；
* DeepSeek provider policy和 L5 evidence。

---

# 5. Queue Admission

本 Prompt 是唯一授权的 Phase 10M-2 executable task。

Entry Gate 通过后：

## 若 TASKS 中不存在 M2 block

将本完整 Prompt 加入 `TASKS.md`：

```text
---TASK---
状态：处理中
# Phase 10M-2
Unified Scientific Workspace Shell
[本完整 Prompt]
---END TASK---
```

## 若已存在一个完全一致的 M2 block

不得重复创建，只确认状态为处理中。

以下情况立即停止：

* 多个 active task；
* M2 block 内容不一致；
* M1 task 未归档；
* M3 task 已出现；
* unknown task；
* task block 残缺；
* Phase 10M-1 archive 不在祖先链。

必须确认：

```text
ACTIVE_EXECUTABLE_TASK_COUNT = 1
ACTIVE_TASK = Phase 10M-2

Phase 10M-3 =
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

---

# 6. Entry Gate

进入：

```powershell
cd "E:\1project\Material Data Intelligence"
```

运行：

```powershell
pwd
git remote -v
git branch --show-current
git status --short
git rev-parse HEAD
git rev-parse origin/master
git log --oneline -35
git diff --stat
git diff --check
```

验证 M1：

```powershell
git merge-base --is-ancestor 27c5aa98138f882a750dc76a402ee2afe2151b72 HEAD
git merge-base --is-ancestor 08f2133c6a02b64a199f40a0b17ccfa5d0e68cc7 HEAD
```

检查 migration：

```powershell
rg -n "0007_phase10m1_workspace_domain|scientific_workspaces|workspace_panels|workspace_layout_revisions" apps packages tests
```

检查状态：

```powershell
rg -n "Phase 10M-1|Phase 10M-2|Phase 10M-3|TASK_BLOCK_COUNT" results.md TASKS.md docs/phase10m persistent
```

检查 LLM policy：

```powershell
rg -n "DEEPSEEK_KEY|DeepSeekProvider|PROVIDER_NOT_ALLOWED|DEEPSEEK_NOT_CONFIGURED|REAL_LLM_CALLS" apps packages tests docs
```

必须确认：

```text
repository = Material Data Intelligence
branch = master
HEAD == origin/master
worktree = clean
HEAD descends from M1 implementation
HEAD descends from M1 archive
M1 archive CI = success
migration head = 0007
M2 not previously implemented
M3 not queued
DeepSeek-only provider policy remains intact
no unknown source changes
```

如果当前 HEAD 高于 `08f2133...`，只有在以下全部成立时继续：

* HEAD 与 origin 一致；
* 工作区 clean；
* 新提交是 reviewer 已知变更；
* 未包含 M2 source implementation；
* 未改变 M0/M1 contract；
* 未改变 DeepSeek-only provider policy；
* 无 unknown task。

失败输出：

```text
PHASE_10M2_ENTRY_GATE = FAIL
NO_WORKSPACE_UI_CHANGES
NO_ROUTE_CHANGES
NO_LLM_CALLS
NO_PHASE_10M3_ENTRY
```

---

# 7. Pre-Implementation Audit

写代码前必须审计真实前端。

至少运行：

```powershell
rg -n "PlannerWorkbench|Workspace|workspace" apps/web
rg -n "page.tsx|layout.tsx|not-found|error.tsx|loading.tsx" apps/web
rg -n "getWorkspace|createWorkspace|patchWorkspace|listWorkspace|workspaceApi" apps/web
rg -n "Artifact|Finding|Evidence|Interpretation|Report|Recipe|Provenance" apps/web
rg -n "JobTimeline|ToolCall|AnalysisPlan|Dependency|Lineage" apps/web
rg -n "useSearchParams|useRouter|router.push|router.replace|popstate" apps/web
rg -n "drawer|sheet|dialog|tabs|navigation|sidebar|panel" apps/web
rg -n "aria-|role=|tabIndex|focus|keyboard|reduced-motion" apps/web
rg -n "mobile|responsive|media query|390" apps/web
rg -n "DEEPSEEK_KEY|provider|DeepSeek" apps/web apps/api
```

输出：

# Phase 10M-2 Entry Gate + Pre-Implementation Audit

至少包含：

## 7.1 Baseline

* HEAD/origin；
* M1 lifecycle；
* migration head；
* task state；
* current frontend tests。

## 7.2 Existing Route Structure

* `/`；
* API routes；
* error/loading/not-found boundaries；
* current deep-link behavior。

## 7.3 Existing Workspace Client

* M1 API client；
* data types；
* response models；
* ETag handling；
* panel metadata。

## 7.4 Reusable Components

分别判断：

```text
REUSE
ADAPT
WRAP
DO_NOT_REUSE
```

覆盖：

* PlannerWorkbench header；
* Job timeline；
* Plan view；
* Artifact views；
* Interpretation；
* Evidence；
* Report/Recipe；
* developer JSON；
* dialogs/drawers；
* mobile navigation。

## 7.5 LLM Call-Site Impact

必须输出：

```text
M2_REQUIRES_NEW_LLM_CALL_SITE = NO
```

若真实代码表明必须新增 LLM call site，停止并返回 reviewer。

不得自行新增。

## 7.6 Readiness

```text
PHASE_10M2_IMPLEMENTATION_READINESS =
READY
or BLOCKED
```

---

# 8. Acceptance IDs

开始实施前，从以下文件恢复 M2 的 exact acceptance ID 集合：

```text
docs/phase10m/phase10m_acceptance_and_test_plan.md
docs/phase10m/phase10m_implementation_backlog.md
docs/phase10m/phase10m_execution_lock.md
```

输出：

| Acceptance ID | Requirement | Implementation | Test | Evidence |
| ------------- | ----------- | -------------- | ---- | -------- |

根据已封板计划，期望数量为：

```text
M2_ACCEPTANCE_IDS_EXPECTED = 7
```

必须确认三份 canonical 文档完全一致。

最终必须：

```text
M2_ACCEPTANCE_IDS_IMPLEMENTED = 7
M2_ACCEPTANCE_IDS_MISSING = 0
M2_ACCEPTANCE_IDS_EXTRA = 0
M2_ACCEPTANCE_IDS_DUPLICATE = 0
```

如果实际 canonical 文档中 M2 数量不是 7，但三份文件彼此一致：

* 使用文档真实数量；
* 在 Pre-Implementation Audit 中明确差异；
* 不自行修改数量。

如果三份文件不一致，立即 BLOCKED。

---

# 9. Frozen Implementation Order

必须按顺序实施：

```text
1. Entry and frontend audit
2. Route and page boundaries
3. Workspace data loader
4. Workspace status projection UI
5. Workspace header
6. Desktop shell/navigation
7. Mobile shell/navigation
8. Panel switcher and panel shell
9. Dataset/context drawer
10. Inspector shell
11. Existing result-surface adapters
12. PlannerWorkbench transition
13. URL active-panel state
14. Loading/error/stale/legacy states
15. Accessibility
16. Responsive behavior
17. Browser evidence
18. Full regression
19. Implementation exact-SHA CI
20. Completion-record CI
21. Queue archive CI
22. Stop for reviewer
```

不得先写大量 CSS，再临时决定路由和数据流。

---

# 10. Canonical Route

必须实现：

```text
/workspaces/{workspaceId}
```

`/` 继续保留当前 PlannerWorkbench。

不得：

* 把 Workspace 页面改成 `/jobs/{jobId}`；
* 把 Workspace 路由嵌入 `/planner`；
* 使用 source Job ID 代替 Workspace ID；
* 将 Workspace ID 存在 localStorage；
* 通过 URL 传入 Artifact payload；
* 使用动态任意 component route。

## 10.1 Route Files

遵循当前 Next.js 真实结构实现：

* page；
* loading；
* error；
* not-found；

仅在当前项目风格需要时添加。

不得创建平行 router framework。

## 10.2 Workspace Not Found

不存在 Workspace：

```text
WORKSPACE_NOT_FOUND
```

显示：

* 清晰标题；
* typed explanation；
* 返回 PlannerWorkbench；
* 不泄露内部路径；
* 不自动根据同名 Job 创建 Workspace。

## 10.3 Source Job Candidate

若用户只有 Job ID，但 Workspace 尚未投影：

* 只能通过已有显式 M1 projection API 创建；
* 不允许普通 GET 隐式写入；
* UI 必须明确“创建 Workspace”是写操作；
* 创建成功后导航到正式 Workspace route。

不得自动静默创建。

---

# 11. PlannerWorkbench Transition

现有 `/` PlannerWorkbench 必须保持兼容。

成功创建或加载持久化 Job 后，提供明确入口：

```text
Open Workspace
```

或 repository 当前 sealed equivalent。

要求：

* 使用 Workspace projection/create API；
* 幂等；
* 成功后导航到 `/workspaces/{workspaceId}`；
* 创建失败显示 typed error；
* 不修改 Job；
* 不重新运行分析；
* 不重复创建 Workspace；
* 不依赖 local state 中的临时 Job 对象；
* refresh 后仍可打开。

不得把所有 PlannerWorkbench 内容一次性删除。

M2 只添加正式过渡入口。

---

# 12. Workspace Data Loading

页面初次加载必须先获取：

```text
Workspace identity
Workspace revision / ETag
Workspace status
source bindings summary
panel metadata
```

不得初次加载：

* 所有 Artifact payload；
* 所有大型 JSON；
* trajectory frames；
* volumetric grids；
* WebGL geometry；
  -完整 report export；
  -所有 layout revisions；
  -未激活 panel 的重型数据。

必须实现：

```text
metadata first
panel data on demand
```

M2 可以加载已有轻量结果摘要，但不得完成 M4 的重型 renderer 重构。

## 12.1 Request Cancellation

Workspace route切换、panel切换或 unmount 时：

* 取消过期请求；
* 忽略 stale response；
* 不覆盖新 Workspace 状态；
* 不造成 setState-after-unmount；
* 不重试不可恢复 4xx。

## 12.2 Cache Identity

缓存 key 必须至少包含：

```text
workspaceId
workspace revision
relevant source hash
panelId
```

不得只按 panel kind 或 Artifact filename 缓存。

---

# 13. Workspace Header

正式 Header 至少显示：

* Workspace title；
* projected Workspace status；
* source dataset/resource；
* source Job；
* original goal 的安全摘要；
* Profile/version；
* Plan schema；
* partial/stale/legacy indicator；
* current revision；
  -返回 Planner；
* Report/Recipe 入口占位或现有只读入口。

不得显示：

* secret；
* provider key；
* Authorization；
  -本机路径；
* bucket key；
* stack trace；
  -原始无限长度 prompt。

长文本必须截断并可安全展开。

---

# 14. Desktop Information Architecture

desktop 必须使用 Phase 10M-0 已封板的信息架构。

不得重新设计。

至少提供以下一级区域：

```text
Data
Plan
Execution
Results
Findings
Evidence
Provenance
Report
```

如果 sealed IA 使用不同的精确 label，以 canonical 文档为准。

## 14.1 Navigation

desktop 使用 sealed：

* primary Workspace navigation；
* panel switcher；
* content region；
* inspector region。

必须支持：

* keyboard navigation；
* active state；
* disabled/unavailable state；
* status badge；
* partial/error indicator；
* screen reader label。

## 14.2 Panel Shell

Panel shell 必须消费 `WorkspacePanel 1.0`。

至少展示：

* panel title；
* panel kind；
* projected state；
* source identity；
* renderer contract；
* warnings；
* evidence/provenance availability；
* unsupported fallback；
* loading/error state。

不得根据 title 或 filename 猜 renderer。

M2 允许复用已有组件呈现轻量内容。

M2 不允许构建 M4 的统一 typed renderer registry。

---

# 15. Mobile Information Architecture

mobile 必须严格实现 sealed 模式：

```text
one active panel
dataset/context drawer
panel switcher
inspector bottom sheet
```

不得把 desktop 三栏布局压缩到 390px。

要求：

* active panel 占主内容区；
* context 使用 drawer；
* panel list 使用可访问 switcher；
* inspector 使用 bottom sheet；
* touch target 至少 44×44 CSS px；
* 无水平页面溢出；
* sticky 元素不遮挡内容；
* keyboard和 screen reader仍可使用；
* bottom sheet可关闭并恢复焦点；
* drawer打开时背景不可误操作。

M2 实现 inspector shell，不实现 M3 的 scientific selection content。

---

# 16. Inspector Shell

M2 的 inspector 只建立容器和基础状态。

允许显示：

* 当前 active panel metadata；
* source Artifact identity；
* source Job/ToolCall；
* renderer contract；
* evidence/provenance links；
* selected item placeholder；
* no-selection state。

不得实现：

* sample/site/atom/q-point/frame propagation；
* cross-panel lookup；
* fuzzy matching；
* array-index linking；
* scientific entity comparison。

必须明确：

```text
CANONICAL_SELECTION_PROPAGATION =
DEFERRED_TO_PHASE_10M3
```

---

# 17. Active Panel URL State

M2 实现 query 中的 active panel：

```text
?panel={panelId}
```

精确格式以 sealed contract 为准。

要求：

* panel ID 必须属于 Workspace；
* unknown panel typed fallback；
* stale panel不自动匹配同名 panel；
* back/forward恢复 active panel；
* refresh恢复 active panel；
* default panel deterministic；
* URL 不保存 layout；
* URL 不保存 Artifact payload；
* URL 不保存 prompt；
* URL 不保存 secret；
* URL 不保存未经验证的 arbitrary JSON。

M2 不实现完整 Selection URL runtime。

可以保留已验证的空 selection 或 pass-through parser，但不得传播跨 panel selection。

---

# 18. Workspace and Panel States

必须实现 Phase 10M-0 / M1 已冻结的状态投影。

至少覆盖：

## Workspace

```text
INITIALIZING
READY
RUNNING
PARTIAL_RESULTS
COMPLETE
FAILED
STALE
SOURCE_MISSING
LEGACY_READ_ONLY
UNSUPPORTED
```

使用真实 sealed enum 名称。

## Panel

```text
NOT_APPLICABLE
READY_NOT_RUN
LOADING
PRODUCED
PARTIAL
UNAVAILABLE
FAILED
BLOCKED_BY_DEPENDENCY
STALE
CAP_EXCEEDED
CONTRACT_UNSUPPORTED
SOURCE_DELETED
PROFILE_AUTHORITY_UNAVAILABLE
```

不得创建意义重复的新状态。

## 18.1 Partial Execution

partial Workspace 必须：

* 明确显示已成功 panel；
* 明确显示 failed panel；
* 明确显示 blocked-by-dependency panel；
* 不让一个 panel 失败导致整个页面白屏；
* 保留已有 Artifact；
* 不把 partial写成 complete；
* 不隐藏失败步骤；
* 不自动重试。

## 18.2 Legacy

历史 Plan 0.1 或缺少新字段的 Job：

* typed legacy/read-only；
* 显示已有内容；
* 不伪造 dependency graph；
* 不伪造 interpretation；
* 不升级 source identities。

## 18.3 Stale / Missing

必须分别显示：

* stale dataset；
* missing Profile；
* missing Artifact；
* deleted source；
* unsupported contract。

不得把它们统一成 generic error。

---

# 19. Existing Surface Integration

M2 应复用已有：

* Plan view；
* Job timeline；
* ToolCall list；
* Artifact summary；
* finding summary；
* evidence list；
* provenance；
* report/recipe summary。

复用原则：

```text
wrap existing validated component
do not fork scientific logic
do not recompute data
do not copy payload
```

允许为了 Workspace shell：

* 添加 adapter component；
* 添加 view model mapper；
* 添加 error boundary；
* 添加 lazy wrapper；
* 添加 responsive wrapper。

不得：

* 复制已有科学计算；
* 修改 Artifact contract；
* 修改 interpretation contract；
* 修改 Job/ToolCall state；
* 重写 Report/Recipe persistence；
* 根据显示 label创建新的 scientific fact。

---

# 20. Scientific Artifact Boundary

M2 不是 M4。

M2 只需要保证所有 panel 有诚实容器。

对于已存在的正式 renderer，可以复用。

对于尚未统一集成的类型，显示：

```text
typed metadata
safe summary
numeric/table fallback when already available
inert JSON fallback
download link through existing authorized API
```

不得：

* 执行 Artifact HTML；
* 执行 Artifact JS；
* iframe；
  -动态 module import from Artifact；
  -加载 Artifact external URL；
  -从 Artifact指定 texture；
  -将 JSON 直接 `dangerouslySetInnerHTML`；
  -新建 generic WebGL renderer；
  -前端重新计算科学结果。

必须保持：

```text
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
```

---

# 21. Findings / Evidence / Provenance Navigation

M2 必须提供正式导航区域，但不修改 L4 contracts。

## Findings

显示：

* finding/claim summary；
* interpretation status；
* partial disclosure；
* warning；
* recommendation 是 non-executable。

## Evidence

显示：

* evidence IDs；
* source Artifact refs；
* field locators；
* units/entities；
* integrity status；
* unavailable/unsupported state。

## Provenance

显示：

* Project；
* dataset/version；
* Profile/hash；
* Intent；
* Eligibility；
* Plan/hash；
* Job；
* ToolCall；
* Artifact/hash；
* lineage；
* interpretation；
* Workspace revision。

M2 不实现复杂图谱或跨选择。

---

# 22. Report / Recipe Boundary

M2 只提供：

* 已有 Report 只读入口；
* 已有 Recipe 只读入口；
* unavailable/legacy 状态；
* future composition affordance 的非执行占位。

不得实现 M5：

* panel selection for report；
* finding selection；
* report composition mutation；
* recipe composition；
* report export redesign；
  -新的 Report/Recipe tables；
* recommendation conversion。

必须保持：

```text
recommendation != executable plan
```

---

# 23. Save / Layout Boundary

M1 已实现 revision persistence。

M2 可以：

* 读取 current layout；
* 渲染 sealed default layout；
* 支持极小范围、已封板的 durable UI mutation；
* 使用 `If-Match` 提交 Workspace title或已批准的基础布局字段。

不得提前实现 M6 的完整：

* drag/drop layout editor；
* autosave recovery；
* offline state；
* conflict resolution UI suite；
* interrupted session recovery；
* deleted-source recovery workflow；
* full layout customization；
* localStorage canonical backup。

如果 M2 需要提交任何 mutation：

* 必须使用 M1 API；
* 必须使用 quoted ETag / `If-Match`；
* 409/412 conflict 显示 typed state；
* 不覆盖 server的新 revision。

---

# 24. Loading, Empty and Error UX

必须实现明确状态。

## Loading

分别处理：

* route loading；
* Workspace metadata loading；
* panel loading；
* Artifact summary loading；
* interpretation loading。

不得用一个全屏 spinner阻塞所有独立 panel。

## Empty

分别处理：

* Workspace无 panel；
  -无 Artifact；
  -无 interpretation；
  -无 report；
  -无 recipe；
  -无 evidence；
  -未开始执行。

## Error

至少：

* Workspace not found；
* Project/source forbidden；
* API unavailable；
* stale ETag；
* panel contract unsupported；
* source missing；
* Artifact unavailable；
* interpretation integrity failure；
* malformed URL panel。

不得统一显示：

```text
Something went wrong
```

---

# 25. Accessibility

必须满足：

* semantic landmarks；
* deterministic heading hierarchy；
* skip-to-content；
* keyboard navigation；
* visible focus；
* active panel announcement；
* status live region；
* error association；
* drawer focus trap；
* bottom-sheet focus trap；
* return focus；
* non-color status；
* chart/table fallback；
* WebGL text fallback；
* reduced motion；
* zoom 200%；
* 44×44 touch target；
* no inaccessible icon-only control；
* accessible panel names；
* accessible loading state；
* accessible stale/partial warnings。

必须测试：

* Tab；
* Shift+Tab；
* Enter；
* Space；
* Escape；
* arrow navigation，在组件语义适用时。

---

# 26. Responsive and Browser Requirements

必须覆盖：

```text
Chromium desktop
Firefox desktop
WebKit desktop
Chromium 390x844 mobile
```

建议补一个中等 viewport，但不替代上述矩阵。

必须验证：

* `/workspaces/{id}`；
* navigation；
* panel switch；
* context drawer；
* inspector bottom sheet；
* partial state；
* error state；
* legacy state；
* long title；
* long warning；
* no horizontal overflow；
* focus；
* back/forward；
* refresh；
* network；
* console。

不得只使用静态截图。

必须通过真实页面和真实 Workspace API。

---

# 27. M2 Browser Evidence Cases

至少包含：

## Case A — Completed Current Workspace

* Plan 0.2；
* completed；
  -多个 panels；
* findings/evidence available；
* desktop + mobile。

## Case B — Running Workspace

* running status；
  -部分 panels loading/ready；
  -页面不崩溃。

## Case C — Partial Results

* succeeded panel；
* failed panel；
* blocked dependency；
* clear disclosure。

## Case D — Legacy Workspace

* Plan 0.1 或无 graph；
* read-only；
  -无伪造字段。

## Case E — Stale / Missing Source

* typed stale/missing；
* no latest rebinding。

## Case F — Unsupported Panel

* inert fallback；
* no arbitrary execution。

## Case G — Planner → Workspace Transition

* existing Job；
* explicit Workspace projection；
* route navigation；
* idempotent retry。

### DeepSeek Requirement for Case G

如果 Case G 创建一个新的自然语言分析 Job：

```text
REAL_DEEPSEEK_REQUIRED = YES
provider = DEEPSEEK
key source = DEEPSEEK_KEY
```

如果 Case G 使用已存在且经过真实 DeepSeek 验证的 Job：

* 必须保留原 provider provenance；
* 不得写成“本阶段新调用”；
* 可以 `REAL_LLM_CALLS = 0`；
* 必须明确使用 existing persisted Job。

如果使用新 Mock Job：

* 只能写成 deterministic UI case；
* 不得写成真实 LLM E2E。

---

# 28. DeepSeek Evidence Requirements

本阶段若产生真实 LLM 调用，必须建立 sanitized evidence，至少记录：

* configured: true；
* provider: DEEPSEEK；
* allowlisted model；
* allowlisted purpose；
* request count；
* response status；
* latency；
* sanitized token counts；
* Intent ID/hash；
* Plan ID/hash；
* Job ID；
* Workspace ID；
* no-secret marker。

不得记录：

* raw key；
* key hash；
* Authorization；
* raw environment；
* full raw provider payload，除非已严格脱敏且现有 policy允许；
* private filesystem path。

必须运行 secret scan。

若本阶段无真实调用：

```text
REAL_LLM_CALLS = 0
M2_NEW_LLM_CALL_SITES = 0
DEEPSEEK_POLICY_REGRESSION = PASS
```

---

# 29. Security

必须证明：

```text
NO_WORKSPACE_SHELL_ARBITRARY_CODE_EXECUTION
NO_WORKSPACE_SHELL_ARTIFACT_JAVASCRIPT
NO_WORKSPACE_SHELL_ARTIFACT_HTML_EXECUTION
NO_WORKSPACE_SHELL_IFRAME_EXECUTION
NO_WORKSPACE_SHELL_EXTERNAL_ARTIFACT_URL_EXECUTION
NO_WORKSPACE_SHELL_DYNAMIC_ARTIFACT_MODULE
NO_WORKSPACE_SHELL_CROSS_PROJECT_ACCESS
NO_WORKSPACE_SHELL_CROSS_JOB_ARTIFACT_INJECTION
NO_WORKSPACE_SHELL_STALE_IDENTITY_REBINDING
NO_WORKSPACE_SHELL_SECRET_DISCLOSURE
NO_WORKSPACE_SHELL_PRIVATE_PATH_DISCLOSURE
NO_WORKSPACE_SHELL_RECOMMENDATION_EXECUTION
NO_SECRET_PATTERN_HITS
```

测试：

* malicious title；
* malicious panel title；
* script/HTML；
* markdown injection；
* external URL；
* `javascript:`；
* SVG script；
* prototype keys；
* oversized query；
* unknown panel ID；
* cross-project Workspace；
* stale Artifact；
* deleted source；
* API stack/path；
* credential-shaped text；
* long prompt；
* malformed ETag；
* malicious error string。

---

# 30. Performance

M2 性能目标是页面壳和 metadata 加载。

至少测量：

* 1 panel；
* 8 panels；
* 32 panels；
* completed；
* partial；
* legacy；
* long metadata；
* repeated panel switching；
* route back/forward；
* mobile；
* memory after repeated mount/unmount。

必须证明：

* initial route不读取全部 Artifact payload；
* inactive heavy panels不加载重型数据；
* metadata response有界；
* no unbounded parallel fetch；
* panel switching取消 stale request；
* no obvious listener leak；
* no unbounded DOM growth；
* 32 panel switcher仍可用；
* mobile无灾难性 overflow。

数字必须称为：

```text
development/browser acceptance evidence
not a production capacity claim
```

---

# 31. Testing Requirements

## 31.1 Unit / Component

覆盖：

* route param；
* Workspace loader；
* header；
* navigation；
* panel switcher；
* panel shell；
* status projection；
* partial state；
* stale state；
* legacy state；
* unsupported state；
* drawer；
* bottom sheet；
* inspector shell；
* URL active panel；
* invalid panel；
* back/forward；
* cancellation；
* error boundary；
* security rendering；
* accessibility。

## 31.2 Integration

覆盖：

* M1 API client；
* real Workspace API；
* Job projection；
* metadata load；
* panel metadata；
* ETag；
* current layout；
* no hidden create on GET；
* Planner transition；
* no Artifact payload copy。

## 31.3 Browser

覆盖第 27 节。

## 31.4 Regression

运行：

* M1 focused tests；
* Phase 10K frontend；
* Phase 10L PlannerWorkbench；
* interpretation/evidence；
* report/recipe；
* current viewer；
* full backend；
* full frontend；
* typecheck；
* production build；
* service-backed；
* no-skipped；
* evidence integrity；
* docs links；
* secret scan；
* DeepSeek provider policy regression。

---

# 32. Service-Backed Evidence

CI 必须使用：

```text
PostgreSQL
Redis
MinIO
migration head 0007
```

至少验证：

* persisted Workspace读取；
* explicit projection；
* panel list；
* current layout；
* ETag；
* Planner → Workspace transition；
* Artifact metadata authorization；
* historical case；
* no hidden GET write；
* no skipped service tests。

要求：

```text
CI_SERVICE_BACKED = PASS
SERVICE_TESTS_SKIPPED = 0
```

本地服务不可用：

```text
LOCAL_SERVICE_BACKED = UNAVAILABLE
```

不得写本地 PASS。

---

# 33. Production Behavior Changes

允许：

```text
new /workspaces/{workspaceId} route
Workspace shell
Workspace navigation
Workspace header
Workspace panel containers
Workspace state and error surfaces
PlannerWorkbench -> Workspace transition
active panel URL state
mobile drawer / switcher / inspector shell
```

必须保持：

```text
Workspace contracts unchanged
Workspace migration unchanged
Workspace persistence semantics unchanged
Workspace API semantics unchanged
AnalysisIntent unchanged
Eligibility unchanged
AnalysisPlan unchanged
QueueWorkerRuntime unchanged
Tool Registry unchanged
Adapters unchanged
scientific calculations unchanged
interpretation contracts unchanged
Report/Recipe persistence unchanged
DeepSeek provider policy unchanged
```

---

# 34. Explicit Non-Scope

不得实现：

* M3 canonical selection propagation；
* cross-panel sample/site/atom/q-point/frame linking；
* scientific inspector content；
* Artifact relationship graph；
* M4 typed renderer registry；
* renderer rewrites；
* new WebGL；
* trajectory Workspace renderer；
* phonon Workspace renderer；
* Brillouin Workspace renderer；
* volumetric Workspace renderer；
* M5 Report composition；
* Recipe composition；
* panel-to-report selection；
* M6 full save/recovery；
* offline；
* collaborative Workspace；
* multi-Job Workspace；
* plan editor；
* DAG editor；
* recommendation execution；
* new LLM call site；
* new provider；
* new SDK；
* arbitrary Python；
* shell；
* notebook；
* filesystem；
* external science API；
* Phase 10N science；
* CrystalNN；
* VoronoiNN；
* experimental XRD；
* trajectory analytics；
* electronic Band/DOS；
* RAG；
* memory；
* multi-agent；
* plugin marketplace；
* enterprise SaaS。

---

# 35. Evidence Directory

创建：

```text
docs/phase10m/evidence/phase10m2_workspace_shell/
```

至少包含：

```text
baseline.txt
entry_gate.txt
m1_archive_verification.txt
acceptance_mapping.json
route_inventory.json
workspace_api_cases.json
planner_transition.json
completed_workspace.json
running_workspace.json
partial_workspace.json
legacy_workspace.json
stale_missing_workspace.json
unsupported_panel.json
active_panel_url.json
back_forward.json
refresh.json
accessibility.json
responsive.json
performance.json
security.json
deepseek_policy_regression.json
real_deepseek_evidence.json
browser_chromium/
browser_firefox/
browser_webkit/
browser_mobile/
network_summary.json
console_summary.json
screenshots/
test_summary.txt
secret_scan.txt
file_manifest.json
```

`real_deepseek_evidence.json`：

* 若有真实调用，保存严格脱敏记录；
* 若无调用，保存：

```json
{
  "realLlmCalls": 0,
  "newLlmCallSites": 0,
  "reason": "Phase 10M-2 consumes persisted Workspace and Job state",
  "deepSeekPolicyRegression": "PASS"
}
```

不得保存 secret。

---

# 36. Documentation Updates

更新：

```text
docs/phase10m/README.md
docs/phase10m/phase10m2_workspace_shell.md
docs/phase10m/phase10m2_route_and_navigation.md
docs/phase10m/phase10m2_workspace_state_ui.md
docs/phase10m/phase10m2_responsive_accessibility.md
docs/phase10m/phase10m2_security_performance.md
docs/phase10m/phase10m2_evidence.md
docs/phase10m/phase10m2_completion.md
docs/phase10m/phase10m3_next_scope.md
docs/index.md
docs/ROADMAP.md
```

更新：

```text
persistent/PROJECT_BRIEF.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/ARCHITECTURE_DECISIONS.md
```

增加永久 LLM 政策说明：

```text
All future real LLM calls use DeepSeek only.
The only API key source is DEEPSEEK_KEY.
No provider or Mock fallback is allowed for real-call evidence.
```

不得在 persistent 中记录 key。

不得把 M3–M7 写成已实现。

---

# 37. Verification Commands

至少执行：

```powershell
git diff --check
uv lock --check
```

frontend：

```powershell
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

backend：

```powershell
uv run python -m pytest -q
```

运行 focused：

```text
M1 Workspace API regression
M2 route
M2 Workspace loader
M2 shell components
M2 navigation
M2 status/error
M2 responsive
M2 accessibility
M2 security
M2 browser
DeepSeek provider policy regression
```

运行：

```text
Chromium runner
Firefox runner
WebKit runner
390x844 mobile runner
service-backed integration
no-skipped assertion
Phase 10 closure integrity
Phase 10K integrity
Phase 10L integrity
Phase 10M acceptance integrity
Phase 10M evidence integrity
docs links
TASKS structure
secret scan
```

`npm audit` 不可用时：

```text
npm audit = UNAVAILABLE
```

不得写 clean。

---

# 38. Commit / CI Lifecycle

## 38.1 Implementation Commit

包含：

* route；
* Workspace shell；
* navigation；
* panel shell；
* state/error UI；
* Planner transition；
* URL active panel；
* responsive/accessibility；
* tests；
* browser runners；
* evidence；
* docs；
* persistent；
* TASKS 保持 M2 处理中。

提交、push，并等待 exact-SHA CI。

必须成功：

```text
Unit
Frontend tests
Typecheck
Build
Browser
Service-backed
No-skipped
Evidence integrity
Secret scan
```

真实 DeepSeek gate：

* 本阶段若有真实调用，必须单独验证并留脱敏 evidence；
* 缺失或失败时，不得用 Mock 替代；
* 若 M2 本身不调用 LLM，记录 0，不强制无意义调用。

## 38.2 Completion-Record Commit

只有 implementation exact-SHA CI 成功后：

* 将完整 M2 result 追加到 `results.md`；
* 更新 persistent；
* TASKS 标记完成、等待归档；
* 不删除 M2 block；
* commit；
* push；
* 验证 completion exact-SHA CI。

## 38.3 Queue Archive

只有 completion-record CI 成功后：

* 核对 implementation/result/evidence/CI；
* 删除且只删除 M2 task block；
* 保留 M3 reviewer gate；
* commit；
* push；
* 验证 archive exact-SHA CI。

最终：

```text
Phase 10M-2:
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT

Phase 10M-3:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 0
```

不得自动进入 M3。

---

# 39. Required Final Result Format

追加：

# Phase 10M-2 Unified Scientific Workspace Shell Result

## 1. Conclusion

archive 前：

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

archive 后 reviewer return：

```text
PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT
```

或：

```text
BLOCKED
```

## 2. Baseline and Entry Gate

* M1 implementation/completion/archive；
* CI；
* initial HEAD/origin；
* migration head；
* worktree；
* task state。

## 3. M0/M1 Decision Compliance

## 4. Workspace Route

## 5. PlannerWorkbench Transition

## 6. Workspace Data Loading

## 7. Workspace Header

## 8. Desktop Information Architecture

## 9. Mobile Information Architecture

## 10. Panel Switcher and Panel Shell

## 11. Dataset/Context Drawer

## 12. Inspector Shell

必须写：

```text
CANONICAL_SELECTION_PROPAGATION =
NOT_IMPLEMENTED_BY_DESIGN
```

## 13. Active Panel URL State

## 14. Workspace Status UI

## 15. Partial Execution UI

## 16. Legacy / Stale / Missing UI

## 17. Existing Surface Reuse

## 18. Findings / Evidence / Provenance

## 19. Report / Recipe Boundary

## 20. Scientific Integrity

必须写：

```text
WORKSPACE_COPIED_ARTIFACT_PAYLOADS = 0
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
```

## 21. LLM / DeepSeek Compliance

必须写：

```text
NEW_LLM_CALL_SITES =
0
```

并写：

```text
REAL_LLM_CALLS =
真实数量
```

若大于 0：

```text
REAL_PROVIDER = DEEPSEEK
API_KEY_SOURCE = DEEPSEEK_KEY
OTHER_REAL_PROVIDERS = 0
REAL_LLM_FALLBACKS = 0
```

若等于 0：

```text
M2_CORE_REQUIRES_LLM = NO
DEEPSEEK_POLICY_REGRESSION = PASS
```

## 22. Accessibility

## 23. Responsive / Mobile

## 24. Browser Matrix

## 25. Performance

## 26. Security

## 27. Acceptance IDs

```text
expected
implemented
missing
extra
duplicate
```

## 28. Tests

* focused；
* full backend；
* frontend；
* typecheck；
* build；
* browser；
* service；
* no-skipped；
* evidence；
* docs；
* secret；
* npm audit。

## 29. Production Behavior Changes

## 30. Files Changed

必须写：

```text
migration = unchanged
dependencies = unchanged
lockfile = unchanged
```

除非真实 M2 sealed scope明确要求其他内容；不得新增 migration。

## 31. Commit / CI History

* failed attempts；
* corrected implementation；
* implementation CI；
* completion；
* completion CI；
* archive；
* archive CI。

## 32. Explicit Non-Scope

逐项确认 M3–M7 和 10N 未实现。

## 33. Phase 10M Readiness

```text
Phase 10M-2:
READY_WITH_EXPLICIT_LIMITS

Phase 10M-3:
REVIEWER_GATE
```

## 34. Queue State

```text
Phase 10M-2:
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT

Phase 10M-3:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 0
```

## 35. Automatic M3 Entry

```text
NO
PHASE_10M3_EXECUTABLE_TASK_CREATED = NO
```

## 36. Next Action

```text
Return the complete Phase 10M-2 result to the reviewer.
Do not create, queue, or execute Phase 10M-3.
```

## 37. Final Repository State

* HEAD；
* origin；
* clean；
* migration head；
* implementation CI；
* completion CI；
* archive CI；
* task count。

---

# 40. PASS Gate

M2 只有全部满足才能 PASS：

* M1 archive verified；
* migration head 0007；
* M0/M1 decisions unchanged；
* `/workspaces/{workspaceId}` implemented；
* `/` PlannerWorkbench preserved；
* explicit Planner → Workspace transition；
* no hidden Workspace creation on GET；
* metadata-first loading；
* no initial full Artifact payload load；
* Workspace header；
* desktop IA；
* mobile one-panel IA；
* panel switcher；
* panel shell；
* context drawer；
* inspector shell；
* active panel URL；
* back/forward；
* refresh；
* partial execution；
* legacy；
* stale；
* missing；
* unsupported；
* panel failure isolation；
* findings/evidence/provenance navigation；
* Report/Recipe boundary；
* no scientific recomputation；
* no Artifact payload copy；
* no M3 selection propagation；
* accessibility；
* responsive；
* browser matrix；
* performance；
* security markers；
* exact M2 acceptance IDs；
* M1 regression；
* full backend；
* frontend；
* typecheck/build；
* service-backed zero skipped；
* evidence manifest；
* secret scan；
* DeepSeek policy regression；
* any real LLM call uses real DeepSeek and only `DEEPSEEK_KEY`；
* no provider fallback；
* implementation CI；
* completion CI；
* archive CI；
* clean repository；
* M3 not queued。

---

# 41. BLOCKED Gate

停止并返回 reviewer，如果：

* M1 archive无法确认；
* M2 acceptance文档不一致；
* Workspace API不足且需要重设计 M1；
* 需要新 migration；
* 需要改变 Workspace cardinality；
* 需要改变 Panel合同；
* 需要改变 Selection合同；
* 需要新增 LLM call site；
* 需要修改 DeepSeek-only policy；
* 需要复制 Artifact payload；
* 需要前端重新计算科学结果；
* 需要提前实现 M3/M4；
* route与 sealed IA冲突；
* service-backed全部 skipped；
* browser核心案例失败；
  -真实 LLM evidence 使用了 Mock/Fake；
  -真实调用未使用 `DEEPSEEK_KEY`；
* secret可能泄露；
* exact-SHA CI无法闭合；
* queue状态异常。

不得临场重设计继续执行。

---

# 42. Reviewer Gate After M2

M2 完成、completion 和 archive全部通过后停止。

下一阶段：

```text
Phase 10M-3:
Cross-Artifact Navigation + Canonical Selection
```

必须基于 M2 的真实：

* route；
* shell；
* panel containers；
* mobile layout；
* inspector shell；
* URL active panel；
* browser evidence；
* error states；

重新生成完整 Prompt。

执行智能体不得自动进入 M3。

---

# 43. 现在开始

第一步不是写 JSX 或 CSS。

先输出：

```text
Phase 10M-2 Entry Gate + Pre-Implementation Audit
```

确认：

1. repository；
2. HEAD/origin；
3. M1 implementation/completion/archive SHA 与 CI；
4. migration head；
5. worktree；
6. task count；
7. exact M2 acceptance IDs；
8. current frontend route；
9. reusable components；
10. Workspace API client；
11. M2 不需要新增 LLM call site；
12. DeepSeek-only policy完整；
13. 是否具备按 execution lock 实施的条件。

Entry Gate 和 Pre-Implementation Audit 均 PASS 后，才允许修改生产代码。

完成 Phase 10M-2 后，返回完整 result，然后停止。

不得创建、排队或执行 Phase 10M-3。

## 完成记录

- 完成时间：2026-08-02 10:45:52 +08:00
- 修改文件：Workspace route/shell/model/tests、PlannerWorkbench transition、
  responsive CSS、browser/evidence runners、service-backed integration、CI、
  Phase 10M docs/evidence、persistent records、`results.md`、`TASKS.md`。
- 修改摘要：实现 metadata-only Unified Scientific Workspace shell、sealed
  nine-group IA、exact active-panel URL、desktop/mobile context and inspector、
  typed source states、Planner Workspace transition/history，以及 additive
  browser/service evidence；未改变 M1 contracts、migration、scientific
  authority、Runtime 或 LLM policy。
- 测试结果：local backend `1107 passed, 1 skipped, 39 deselected`；frontend
  `351 passed`；Chromium/Firefox/WebKit/390x844 PASS；corrected implementation
  `d18097101cdf999b76be1f2da1cf4f3d67fb9c48` exact-SHA CI `30729180057`
  success，service-backed `38 passed, 0 skipped, 0 failed, 0 errors`。
- 生命周期：completion-record exact-SHA CI 与 verified queue archive 待完成；
  在两者完成前不得删除本 block。用户提供的 M3 block 保持待处理。

---END---


---TASK---
 状态：待处理

# Phase 10M-3 Reviewer Prompt

## Cross-Artifact Navigation + Canonical Selection

你现在执行：

# Phase 10M-3：Cross-Artifact Navigation + Canonical Selection

本阶段是 Phase 10M Unified Scientific Workspace 的跨 Artifact 导航和规范化科学对象选择阶段。

本阶段必须在 Phase 10M-2 完成、completion-record CI 成功、queue-archive CI 成功后才能开始。

本阶段实现：

1. `WorkspaceSelectionContext 1.0` 前端运行时；
2. 规范化 selection store；
3. versioned selection URL 编码和解析；
   4.浏览器 refresh、back、forward 恢复；
4. Panel selection input/output subscription；
5. exact identity compatibility resolver；
   7.跨 Panel selection propagation；
6. Workspace Inspector 的正式 selection 内容；
   9.跨 Artifact 导航；
7. selection 来源、兼容性、stale 和 unsupported 状态；
8. dataset sample、material object、structure/site/atom、trajectory、phonon、reciprocal、volumetric、evidence、claim 和 Artifact 身份的 bounded 支持；
9. desktop/mobile selection UX；
10. accessibility、browser、performance 和 security evidence。

本阶段不实现：

* Phase 10M-4 typed Artifact Gallery 重构；
* 新科学 Renderer；
* 新 WebGL 计算或 viewer；
* 前端科学计算；
* Phase 10M-5 Report/Recipe composition；
* Phase 10M-6 完整 save/recovery；
* 新 Workspace 数据库表；
* selection 服务器持久化；
* selection 作为 Job、Plan 或科学 authority；
* recommendation 自动执行。

---

# 0. Conditional Entry Baseline

本 Prompt 可以在 Phase 10M-2 执行前预先提供，但不得提前执行。

开始 M3 时，不得假设 M2 已通过。

必须从真实仓库恢复：

```text
Phase 10M-2 implementation SHA
Phase 10M-2 implementation exact-SHA CI
Phase 10M-2 completion-record SHA
Phase 10M-2 completion-record exact-SHA CI
Phase 10M-2 queue-archive SHA
Phase 10M-2 queue-archive exact-SHA CI
Phase 10M-2 final result
Phase 10M-2 final acceptance state
Phase 10M-2 final browser evidence
Phase 10M-2 final repository state
```

只有以下全部成立才允许进入：

```text
Phase 10M-2 = ARCHIVED_BY_VERIFIED_QUEUE_COMMIT
Phase 10M-2 implementation CI = success
Phase 10M-2 completion CI = success
Phase 10M-2 archive CI = success
Phase 10M-2 acceptance IDs = complete
Phase 10M-2 browser matrix = pass
HEAD == origin/master
HEAD == Phase 10M-2 archive SHA
worktree = clean
migration head = 0007_phase10m1_workspace_domain
TASK_BLOCK_COUNT = 0
Phase 10M-3 not previously implemented
Phase 10M-4 not queued
```

如果任一条件不满足：

```text
PHASE_10M3_ENTRY_GATE = FAIL
NO_SELECTION_RUNTIME_CHANGES
NO_URL_SELECTION_CHANGES
NO_PANEL_SUBSCRIPTION_CHANGES
NO_PHASE_10M4_ENTRY
```

不得使用 M1 archive `08f2133...` 代替 M2 archive。

---

# 1. Reviewer-Frozen Architecture

Phase 10M-0 已冻结，Phase 10M-1 已实现，Phase 10M-2 应已经实现：

```text
ScientificWorkspace 1.0
WorkspacePanel 1.0
WorkspaceSelectionContext 1.0 contract
/workspaces/{workspaceId}
Workspace shell
Workspace Header
desktop navigation
mobile one-panel layout
panel switcher
dataset/context drawer
inspector shell
active panel URL state
partial/legacy/stale/unsupported UI
PlannerWorkbench -> Workspace transition
```

M3 不得重新设计：

* Workspace identity；
* one-Workspace-per-Job；
  -三表数据库设计；
* migration 0007；
* Workspace API；
* Workspace route；
* Panel contract；
* Selection contract；
* mobile IA；
* Inspector placement；
* active panel URL；
* Report/Recipe ownership；
* security boundary；
* M1–M7 顺序。

M3 只把已经存在的 `WorkspaceSelectionContext 1.0` 从合同变为正式前端交互运行时。

---

# 2. Permanent DeepSeek-Only Policy

本节适用于 M3 以及后续所有阶段。

## 2.1 唯一真实 Provider

所有真实 LLM 调用必须：

```text
provider = DEEPSEEK
transport = existing OpenAI-compatible transport
base_url = https://api.deepseek.com
api_key_env = DEEPSEEK_KEY
```

只允许仓库已经验证的 `DeepSeekProvider`。

不得新增 SDK。

不得使用：

```text
OpenAI
Anthropic
Azure OpenAI
custom OpenAI-compatible endpoint
local real provider
other hosted provider
```

## 2.2 唯一 Key 来源

只允许读取：

```text
DEEPSEEK_KEY
```

不得 fallback 到：

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
ANTHROPIC_API_KEY
LLM_API_KEY
SecretStore
database
frontend input
localStorage
sessionStorage
plaintext config
command-line literal
```

不得输出或持久化：

* key；
  -长度；
* prefix；
* suffix；
* hash；
* fingerprint；
* Authorization header；
* environment dump。

只允许记录：

```text
configured = true
```

或：

```text
configured = false
```

## 2.3 无 Fallback

`DEEPSEEK_KEY` 缺失：

```text
DEEPSEEK_NOT_CONFIGURED
no request
no fallback
```

调用失败：

```text
DEEPSEEK_PROVIDER_FAILED
no Mock fallback
no Deterministic fallback
no alternate provider
```

## 2.4 M3 的预期

M3 的 selection runtime 不需要新增 LLM call site。

必须预期：

```text
M3_REQUIRES_NEW_LLM_CALL_SITE = NO
NEW_LLM_CALL_SITES = 0
```

普通 M3 unit、frontend、browser、service-backed CI：

```text
REAL_LLM_CALLS = 0
```

如果 M3 的 E2E 从自然语言输入开始并创建新 Job：

* 必须真实调用 DeepSeek；
* API key 只能来自 `DEEPSEEK_KEY`；
* 不得使用 Mock/Fake 冒充真实链路；
* 必须保存严格脱敏的 provider evidence；
* selection 功能仍不得直接调用 LLM。

可以使用已经由真实 DeepSeek 创建并持久化的历史 Job/Workspace进行 selection browser evidence，此时：

```text
M3_NEW_REAL_LLM_CALLS = 0
PERSISTED_PROVIDER_PROVENANCE = DEEPSEEK
```

---

# 3. Canonical M3 Goal

M3 完成后的用户链路：

```text
用户在一个 Workspace Panel 中选择科学对象
    ↓
生成严格 WorkspaceSelectionContext 1.0
    ↓
验证 exact identity / version / hash / scope
    ↓
写入 URL query 和内存 selection state
    ↓
兼容 Panel 接收选择
    ↓
不兼容 Panel 显示 typed unsupported
    ↓
Inspector 显示规范化对象身份和来源
    ↓
Findings / Evidence / Provenance 可精确跳转
```

选择必须依赖正式身份，而不是显示层猜测。

允许的 selection 来源只能是：

-正式 Artifact；
-正式 panel mapper；
-正式 evidence/claim；
-正式 Workspace source bindings；
-正式稳定 object/sample/site/atom/q-point/frame 等身份。

---

# 4. Required Documents

开始前完整阅读：

```text
docs/phase10m/README.md
docs/phase10m/phase10m0_identity_and_lineage_map.md
docs/phase10m/phase10m0_workspace_panel_contract_proposal.md
docs/phase10m/phase10m0_workspace_selection_context_decision.md
docs/phase10m/phase10m0_workspace_information_architecture.md
docs/phase10m/phase10m0_state_and_error_taxonomy.md
docs/phase10m/phase10m0_responsive_accessibility_performance_security.md
docs/phase10m/phase10m0_compatibility_strategy.md
docs/phase10m/phase10m_implementation_backlog.md
docs/phase10m/phase10m_acceptance_and_test_plan.md
docs/phase10m/phase10m_execution_lock.md
docs/phase10m/phase10m_execution_manifest.md
docs/phase10m/phase10m_execution_agent_handoff.md
docs/phase10m/phase10m3_next_scope.md
```

完整阅读 M1：

```text
docs/phase10m/phase10m1_workspace_domain_contract.md
docs/phase10m/phase10m1_workspace_api.md
docs/phase10m/phase10m1_historical_job_projection.md
docs/phase10m/phase10m1_security_and_compatibility.md
docs/phase10m/phase10m1_completion.md
```

完整阅读 M2：

```text
docs/phase10m/phase10m2_workspace_shell.md
docs/phase10m/phase10m2_route_and_navigation.md
docs/phase10m/phase10m2_workspace_state_ui.md
docs/phase10m/phase10m2_responsive_accessibility.md
docs/phase10m/phase10m2_security_performance.md
docs/phase10m/phase10m2_evidence.md
docs/phase10m/phase10m2_completion.md
docs/phase10m/phase10m3_next_scope.md
```

如果文件名不同，以 Phase 10M README 和 execution manifest 的当前索引为准。

同时阅读：

```text
README.md
AGENTS.md
MASTER_PROMPT.md
docs/index.md
docs/ROADMAP.md
docs/13_SHARED_SCHEMA_SPEC.md
persistent/PROJECT_BRIEF.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/ARCHITECTURE_DECISIONS.md
results.md
TASKS.md
```

必须阅读当前真实：

* `WorkspaceSelectionContext 1.0` Python/JSON Schema/TypeScript；
* WorkspacePanel selection input/output declarations；
* M2 selection placeholder；
* M2 inspector shell；
* M2 URL active-panel parser；
* Dataset Explorer sample identity；
* Materials ML linked sample identity；
* Composition Space point identity；
* Structure site/atom identity；
* trajectory frame/atom identity；
* phonon q-point/branch identity；
* Brillouin reciprocal identity；
* volumetric identity；
* EvidenceItem identity；
* ScientificClaim identity；
* Artifact lineage identity；
* browser routing tests；
* history/back-forward tests。

---

# 5. Queue Admission

本 Prompt 只有在 M2 verified archive 后才可入队。

## 状态 A：TASKS 中不存在 M3

Entry Gate 通过后，将本完整 Prompt 加入：

```text
---TASK---
状态：处理中
# Phase 10M-3
Cross-Artifact Navigation + Canonical Selection
[本完整 Prompt]
---END TASK---
```

## 状态 B：已存在唯一且语义完全一致的 M3 task

不得重复创建，只确认处理中。

以下任一情况停止：

* M2 task 尚未归档；
  -多个 active task；
* M3 task 内容不同；
* M4 task 已存在；
* unknown task；
* task block 残缺；
* M2 archive CI未成功；
  -当前代码已存在无记录 M3 实现。

入队后必须：

```text
ACTIVE_EXECUTABLE_TASK_COUNT = 1
ACTIVE_TASK = Phase 10M-3

Phase 10M-4 =
REVIEWER_GATE / AWAITING REVIEWER PROMPT
```

---

# 6. Entry Gate Commands

进入：

```powershell
cd "E:\1project\Material Data Intelligence"
```

运行：

```powershell
pwd
git remote -v
git branch --show-current
git status --short
git rev-parse HEAD
git rev-parse origin/master
git log --oneline -40
git diff --stat
git diff --check
```

恢复 M2：

```powershell
rg -n "Phase 10M-2|Phase 10M-3|Phase 10M-4|TASK_BLOCK_COUNT" results.md TASKS.md docs/phase10m persistent
```

检查 M1/M2基础：

```powershell
rg -n "ScientificWorkspace|WorkspacePanel|WorkspaceSelectionContext" apps packages tests
rg -n "workspaces/\\[|/workspaces/|workspaceId" apps/web
rg -n "panel=|selection=|useSearchParams|URLSearchParams" apps/web
rg -n "Inspector|inspector|PanelSwitcher|WorkspaceShell" apps/web
```

检查 DeepSeek：

```powershell
rg -n "DEEPSEEK_KEY|DeepSeekProvider|PROVIDER_NOT_ALLOWED|DEEPSEEK_NOT_CONFIGURED|REAL_LLM_CALLS" apps packages tests docs
```

必须恢复 M2 完整三阶段 SHA 和 CI，不得猜测。

---

# 7. Pre-Implementation Audit

修改代码前输出：

# Phase 10M-3 Entry Gate + Pre-Implementation Audit

至少包含：

## 7.1 Baseline

* M2 implementation/completion/archive SHA；
  -三次 CI；
* HEAD/origin；
* worktree；
* migration head；
* task state；
* M2 acceptance state；
* M2 browser state。

## 7.2 Current Selection Contract

列出 `WorkspaceSelectionContext 1.0` 的真实字段：

* schema version；
* identity kind；
* identity ID；
* source dataset/resource/artifact；
* source version/hash；
* scope；
* multi-selection；
* propagation；
* compatibility；
* clearing；
* URL representation；
* stale/unsupported；
* caps。

不得根据 Prompt 自行发明字段。

## 7.3 Current Panel Contract

建立：

| Panel kind | Declared selection inputs | Declared selection outputs | Current renderer | Current identity support | M3 action |
| ---------- | ------------------------- | -------------------------- | ---------------- | ------------------------ | --------- |

## 7.4 Current Identity Producers

建立：

| Identity kind | Producer Artifact/Panel | Exact fields | Version/hash | Stable across sorting | Stable across reload | Current authority |
| ------------- | ----------------------- | ------------ | ------------ | --------------------- | -------------------- | ----------------- |

## 7.5 Current Identity Consumers

建立：

| Identity kind | Consumer Panel | Exact accepted scope | Compatibility rule | Unsupported behavior |
| ------------- | -------------- | -------------------- | ------------------ | -------------------- |

## 7.6 Existing Navigation

审计：

* active panel；
* Inspector shell；
* evidence link；
* finding link；
* provenance；
* current URL；
* back/forward；
* mobile bottom sheet；
* panel activation。

## 7.7 M3 LLM Impact

必须：

```text
M3_REQUIRES_NEW_LLM_CALL_SITE = NO
```

若需要新增，立即 BLOCKED。

## 7.8 Readiness

```text
PHASE_10M3_IMPLEMENTATION_READINESS =
READY
or BLOCKED
```

---

# 8. Acceptance IDs

必须从以下三份 canonical 文档恢复 M3 exact acceptance IDs：

```text
docs/phase10m/phase10m_acceptance_and_test_plan.md
docs/phase10m/phase10m_implementation_backlog.md
docs/phase10m/phase10m_execution_lock.md
```

不得假设数量。

输出：

| Acceptance ID | Requirement | Implementation | Test | Evidence |
| ------------- | ----------- | -------------- | ---- | -------- |

三份文档必须拥有完全相同的 M3 ID 集合。

最终要求：

```text
M3_ACCEPTANCE_IDS_IMPLEMENTED = M3_ACCEPTANCE_IDS_EXPECTED
M3_ACCEPTANCE_IDS_MISSING = 0
M3_ACCEPTANCE_IDS_EXTRA = 0
M3_ACCEPTANCE_IDS_DUPLICATE = 0
```

如果集合不一致：

```text
PHASE_10M3_ACCEPTANCE_GATE = FAIL
```

不得自行修正文档后继续。

---

# 9. Frozen Implementation Order

必须按顺序：

```text
1. Entry and identity audit
2. Selection contract parity verification
3. URL selection codec
4. Selection validator
5. Selection store
6. Panel subscription registry
7. Compatibility resolver
8. Selection propagation runtime
9. Active-panel navigation integration
10. Inspector selection view
11. Findings/Evidence/Provenance navigation
12. Dataset/ML/Composition Space linkage
13. Structure/trajectory/phonon/volumetric bounded linkage
14. stale/unsupported/missing behavior
15. mobile interaction
16. accessibility
17. performance and leak tests
18. browser evidence
19. full regression
20. implementation exact-SHA CI
21. completion-record exact-SHA CI
22. queue-archive exact-SHA CI
23. stop for reviewer
```

不得先为每个 Renderer写特殊事件逻辑，再临时抽象 selection。

---

# 10. No Database or Migration Change

M3 必须保持：

```text
DATABASE_MIGRATION_REQUIRED = NO
migration head = 0007_phase10m1_workspace_domain
```

Selection 是 ephemeral state。

不得写入：

* `scientific_workspaces`；
* `workspace_panels`；
* `workspace_layout_revisions`；
  -新表；
* Project metadata；
* Job metadata；
* Report；
* Recipe；
* Artifact。

不得：

* 新增 migration 0008；
* 使用 localStorage作为 canonical state；
* 使用 sessionStorage作为 canonical state；
  -服务器保存 active scientific selection；
  -把 selection 放入 Workspace title/metadata；
  -把 selection 作为 layout revision。

如果真实 M3 sealed 文档明确要求新的只读 API，必须先核对 exact decision。

若需要新 persistence 或 migration才能实现，停止返回 reviewer。

---

# 11. WorkspaceSelectionContext Runtime

必须复用已实现的 `WorkspaceSelectionContext 1.0`。

不得创建：

```text
SelectionContext 2.0
GlobalSelection
ViewerSelection
CrossFilterSelection
```

等平行 authority。

前端运行时至少包括：

* strict parse；
* strict validation；
* canonical serialize；
* deterministic equality；
* source/version/hash comparison；
* bounded multi-selection；
* typed clear；
* typed stale；
* typed unsupported；
* compatible subscriptions；
* source provenance；
* active origin panel；
* navigation reason；
* URL representation。

不得通过 JavaScript object reference identity 判断相等。

必须通过合同的 canonical semantic identity。

---

# 12. Supported Selection Identity Kinds

必须从当前 contract 读取 exact enum。

候选范围包括但不限于：

```text
DATASET_SAMPLE
MATERIAL_OBJECT
STRUCTURE
PERIODIC_SITE
ATOM
TRAJECTORY_ATOM
TRAJECTORY_FRAME
PHONON_Q_POINT
PHONON_BRANCH
RECIPROCAL_POINT
VOLUMETRIC_FIELD
VOLUMETRIC_REGION
EVIDENCE_ITEM
SCIENTIFIC_CLAIM
ARTIFACT
```

只能实现 contract 当前正式允许的 identity kind。

不得因为 Prompt 列出候选而修改 enum。

对于当前正式 Artifact 尚未提供稳定身份的对象：

```text
IDENTITY_NOT_AVAILABLE
```

或 contract 中 sealed typed equivalent。

不得猜测身份。

---

# 13. Canonical Identity Requirements

每次 selection 必须包含合同要求的：

* exact kind；
* exact identity ID；
* exact source scope；
* dataset/resource version；
* Artifact ID；
* Artifact hash或source hash；
* object/sample/site/atom/frame/q-point等必要键；
* selection contract version。

必须禁止：

```text
array index
row index
plot point index
DOM index
display label
formatted formula alone
filename
panel title
sort order
filter order
visual coordinates
floating-point nearest match
fuzzy string match
latest version
same numeric value assumption
```

显示坐标只可用于定位 UI，不可成为 scientific identity。

---

# 14. Stable Sample Identity

Dataset、ML 和 Composition Space 必须复用：

```text
objectId + sampleRef
```

或当前实现的正式 `sampleKey` equivalent。

必须证明：

```text
Dataset Explorer sample
→ ML high-error / uncertainty / misclassification
→ Composition Space point
→ Inspector
```

在以下情况下仍指向同一对象：

-排序变化；
-筛选变化；
-不同 table order；
-不同 plot point order；
-refresh；
-back/forward；
-Workspace重新加载。

不得使用行号。

不得把 formula 当唯一 sample identity。

---

# 15. Structure / Site / Atom Identity

必须审计当前正式 structure Artifact 提供的身份。

只有在当前 contract正式支持时实现：

* structure identity；
* periodic site；
* atom；
* periodic image；
* source structure hash；
* species；
* index作为合同组成部分时的精确 scope。

如果 site index 只在单一结构版本内有意义，selection必须带：

* structure ID；
* structure hash/version；
* site index；
* periodic image，如果需要。

不得跨不同 structure hash复用 site index。

不得通过空间最近邻猜 site identity。

M3 不新增 CrystalNN/VoronoiNN 或局域环境算法。

---

# 16. Trajectory Identity

只有当前 trajectory Artifact 已提供正式稳定身份时实现：

* trajectory ID/hash；
* atom identity；
* frame identity；
* time identity；
* species；
* periodic/unwrapped scope。

不得：

* 将 frame array position作为跨版本 identity；
  -在变胞轨迹中猜坐标对应；
  -用最近位置匹配 atom；
  -前端重算 trajectory identity；
  -实现 RDF/MSD。

不支持时显示 typed unavailable。

---

# 17. Phonon and Reciprocal Identity

只有当前 contract支持时实现：

* phonon q-point；
* q-point index加graph/source hash；
* phonon branch；
* reciprocal-space point；
* BZ path label；
* combined band/DOS Artifact；
* producer/consumer lineage。

必须证明：

```text
phonon band q-point
→ combined phonon result
→ evidence item
→ scientific claim
```

不得：

-根据 q-point label 单独匹配；
-根据相近浮点坐标 fuzzy match；
-根据 plot index匹配 branch；
-把 electronic band和phonon band identity混用。

---

# 18. Volumetric Identity

只能使用当前正式 volumetric contract定义的：

* field identity；
* quantity；
* source volume hash；
* region/feature identity；
* bounded grid/region reference。

不得：

-把 voxel array index作为跨 Artifact identity，除非 contract正式规定完整 grid scope；
-根据颜色或等值面猜 region；
-前端重新计算 volumetric features；
-把不同 quantity/unit的场互相选择。

不兼容时 typed unsupported。

---

# 19. Evidence and Claim Identity

必须支持精确导航：

```text
ScientificClaim
→ EvidenceItem
→ Artifact
→ exact field locator
```

以及反向导航：

```text
Artifact / selected scientific object
→ supporting EvidenceItem
→ claims
```

必须使用：

* claim ID；
* evidence ID；
* Artifact ID/hash；
* field locator；
* entity identity；
* unit；
* interpretation ID/hash。

不得：

-根据 claim text匹配；
-根据相同数字匹配；
-根据单位和数值猜 evidence；
-将 recommendation作为 selection authority；
-修改 grounded interpretation。

---

# 20. URL Selection State

M3 必须实现 versioned exact selection query。

精确 query key和编码格式以 contract/sealed文档为准。

候选形式：

```text
?panel={panelId}&selection={versionedCanonicalEncoding}
```

不得自行选择另一格式。

URL selection必须：

* canonical；
* versioned；
* bounded；
* deterministic；
  -可 round-trip；
  -可 share；
* refresh恢复；
* back/forward恢复；
* invalid input typed reject；
* stale input typed stale；
* unknown version typed unsupported；
* no silent repair；
* no latest rebinding。

URL不得包含：

* Artifact payload；
* raw dataset rows；
* full coordinates array；
* raw user prompt；
* provider response；
* secret；
* Authorization；
* file path；
* external URL；
* executable code；
* oversized JSON；
  -完整 evidence bundle。

---

# 21. Selection Store

必须使用一个正式 selection runtime/store。

要求：

-一个 Workspace scope；
-当前 selection；

* origin panel；
* previous valid selection，在sealed UX要求时；
* subscribers；
* typed clear；
* URL synchronization；
* stale response protection；
* no cross-Workspace leakage；
* cleanup on unmount；
* no listener leak；
* deterministic updates；
* no infinite propagation loop；
* no duplicate update storm。

切换 Workspace 时必须清除不兼容 selection。

不得把 Workspace A selection应用到 Workspace B。

---

# 22. Panel Subscription Registry

Panel必须通过 `WorkspacePanel 1.0` 的 selection declarations订阅。

不得在代码中形成无限增长的：

```text
if panelKind === ...
```

特殊传播链。

允许有 bounded adapter registry，但它必须：

* keyed by formal panel/renderer contract；
  -声明 accepted identity kinds；
  -声明 emitted identity kinds；
  -声明 compatibility；
  -声明 mapping function；
  -声明 unsupported behavior；
  -无科学计算；
  -无模糊匹配；
  -无外部调用；
* deterministic。

M3 registry不是 M4 typed renderer registry。

它只负责 selection identity mapping，不负责绘图或科学内容渲染。

---

# 23. Compatibility Resolver

必须实现正式、纯函数或可审计的 compatibility resolver。

输入至少包括：

* Workspace；
* source selection；
* origin panel；
* target panel；
* target selection inputs；
* dataset/resource scope；
* source version/hash；
* Artifact identity；
* selection kind。

输出只能是类似：

```text
COMPATIBLE_EXACT
COMPATIBLE_SAME_OBJECT
NOT_APPLICABLE
UNSUPPORTED_IDENTITY
SOURCE_SCOPE_MISMATCH
SOURCE_VERSION_MISMATCH
ARTIFACT_HASH_MISMATCH
STALE_SELECTION
TARGET_NOT_READY
TARGET_SOURCE_MISSING
```

使用合同/sealed文档中的真实 enum。

不得：

-自动转换单位；

* fuzzy match；
* nearest-neighbor match；
* label match；
* row-order match；
  -跨 dataset猜映射；
  -跨 structure hash猜 site；
  -跨 Job使用同名 Artifact；
  -从旧 selection升级到 latest。

---

# 24. Selection Propagation

传播流程：

```text
Panel emits exact selection
    ↓
selection validator
    ↓
canonical store
    ↓
URL update
    ↓
compatibility resolver
    ↓
compatible target subscribers
    ↓
target panel highlight/navigation
    ↓
Inspector update
```

要求：

* origin panel不会收到无限 echo；
  -相同 selection不重复发布；
  -切换 active panel不改变 selection identity；
* target不兼容时不清除全局 selection，除非用户明确 clear；
* target显示 typed unavailable；
* failed panel不影响其他 compatible panel；
* stale selection保留诊断但不传播；
* user clear同步 URL和所有 subscribers。

---

# 25. Inspector Implementation

M2 inspector shell在 M3 中成为正式 selection inspector。

至少显示：

* identity kind；
* exact ID；
* display label，作为显示而非 authority；
* source dataset/resource；
* source version/hash；
* origin panel；
* source Artifact；
* source Job/ToolCall；
* compatible panels；
* incompatible panels及原因；
* evidence links；
* claim links；
* provenance；
* stale/unsupported状态；
* clear action；
* copy shareable Workspace URL。

不得显示：

* secret；
* private path；
* raw Artifact payload；
* unbounded JSON；
* provider prompt；
* executable link；
* scientific inference that is not persisted。

Mobile 使用 M2 bottom sheet。

Desktop 使用 sealed inspector region。

---

# 26. Cross-Panel Navigation

至少实现并验证当前真实支持的以下链路。

## 26.1 Dataset Intelligence Chain

```text
Dataset sample
→ Dataset detail/row
→ ML evaluation linked sample
→ Composition Space point
→ Inspector
```

## 26.2 Structure Chain

```text
Dataset structure sample
→ Structure panel
→ exact site/atom，当正式 identity可用
→ Inspector
```

## 26.3 Interpretation Chain

```text
Finding/claim
→ EvidenceItem
→ Artifact
→ source panel
```

## 26.4 Lineage Chain

```text
consumer Artifact
→ producer Artifact
→ producer ToolCall/step
→ dependency binding
```

## 26.5 Phonon Chain

仅在正式 identity支持时：

```text
q-point / branch
→ combined band/DOS
→ evidence
→ claim
```

## 26.6 Volumetric Chain

仅在正式 identity支持时：

```text
volumetric feature/region
→ Artifact
→ evidence/claim
```

不支持的链路必须诚实标记。

不得伪造全部链路都可用。

---

# 27. Active Panel Navigation

当用户从 Inspector、Finding、Evidence 或 Lineage 跳转到另一个 panel：

-更新 `panel` query；
-保留兼容 selection；

* browser history行为可预测；
* back返回原 panel和selection；
* target panel不存在时 typed error；
* target panel stale时不重绑；
* target panel lazy loading；
  -不加载所有 inactive heavy panels。

Panel navigation和selection navigation必须区分。

---

# 28. Selection Clearing

必须支持：

-用户显式 clear；

* source Workspace变化；
* source version/hash失效；
* invalid URL；
* deleted Artifact；
* panel contract不支持旧 selection版本。

不得因为：

-切换 panel；
-关闭 Inspector；
-打开 drawer；
-临时 loading；

自动清除有效 selection。

Clear必须：

-清除 URL selection；
-通知 subscribers；
-保留 active panel；
-恢复 no-selection Inspector；
-无残留 highlight；
-无 stale listener。

---

# 29. Historical and Legacy Behavior

Plan 0.1、无 graph、无 interpretation或旧 Artifact的 Workspace：

-可以使用当前正式存在的 identity；
-不可伪造新 identity；
-不可升级 source hash；
-不可假设 selection input/output；
-unsupported panel显示 typed状态；
-旧 selection URL未知版本必须拒绝；
-历史 Workspace read-only不阻止纯前端 selection；
-selection不得修改 Workspace source。

---

# 30. M3 API Boundary

M3原则上使用现有 M1/M2 API和 Artifact read APIs。

不得新增：

* selection persistence API；
* selection history table；
* selection analytics endpoint；
* cross-filter query engine；
* arbitrary identity resolution endpoint；
* fuzzy search service。

如果 exact sealed M3文档已经定义 additive read-only identity lookup endpoint，可以按文档实现。

如果实现需要未封板的新 API：

```text
PHASE_10M3_API_SCOPE_BLOCKED = YES
```

停止并返回 reviewer。

不得临场设计。

---

# 31. Scientific Integrity

必须保持：

```text
Registered Adapter
→ QueueWorkerRuntime
→ persisted Artifact
→ validated frontend mapper
→ canonical selection identity
```

M3 只能选择和导航。

不得计算：

* ML metrics；
* residuals；
* chemistry；
* PCA；
* clustering；
* XRD；
* RDF；
* MSD；
* coordination；
* trajectory unwrap；
* phonon；
* BZ；
* volumetric feature；
* scientific claim；
* unit conversion。

允许：

* UI highlight；
* scroll/focus；
  -选择 exact row；
  -选择 exact point；
  -选择 exact site；
  -相机聚焦到已经有 identity的对象；
  -显示已有 scientific values。

---

# 32. Security Boundary

必须证明：

```text
NO_SELECTION_ARBITRARY_CODE_EXECUTION
NO_SELECTION_ARTIFACT_JAVASCRIPT
NO_SELECTION_ARTIFACT_HTML_EXECUTION
NO_SELECTION_IFRAME_EXECUTION
NO_SELECTION_EXTERNAL_URL_EXECUTION
NO_SELECTION_DYNAMIC_MODULE_EXECUTION
NO_SELECTION_CROSS_WORKSPACE_LEAK
NO_SELECTION_CROSS_PROJECT_ACCESS
NO_SELECTION_CROSS_JOB_ARTIFACT_INJECTION
NO_SELECTION_STALE_IDENTITY_REBINDING
NO_SELECTION_ARRAY_INDEX_AUTHORITY
NO_SELECTION_DISPLAY_LABEL_AUTHORITY
NO_SELECTION_FUZZY_MATCH
NO_SELECTION_SECRET_DISCLOSURE
NO_SELECTION_PRIVATE_PATH_DISCLOSURE
NO_RECOMMENDATION_EXECUTION
NO_SECRET_PATTERN_HITS
```

测试：

* malicious URL selection；
* script/HTML；
* `javascript:`；
* external URL；
* prototype keys；
* deep JSON；
* oversized selection；
* invalid version；
* unknown identity kind；
* invalid hash；
* cross-Workspace；
* cross-Project；
* foreign Artifact；
* stale dataset；
* stale structure；
* malformed multi-selection；
* duplicate identities；
* credential-shaped text；
* path/stack disclosure。

---

# 33. Accessibility

必须支持：

* keyboard selection；
* visible selected state；
* `aria-selected`或对应语义；
* selection change announcement；
* Inspector heading；
* compatibility warning announcement；
* focus target after navigation；
* return focus；
* clear action keyboard accessible；
* mobile bottom sheet focus trap；
* non-color highlighting；
* table row alternative；
* chart point list/table alternative；
* WebGL selection text alternative；
* reduced motion；
* 200% zoom；
* 44×44 touch targets。

不得只通过颜色表示选中。

---

# 34. Mobile Behavior

沿用 M2：

```text
one active panel
context drawer
panel switcher
inspector bottom sheet
```

M3 mobile必须：

-允许在 active panel选择；
-打开 Inspector bottom sheet；
-通过 Inspector导航到 compatible panel；
-切换 panel后保留 selection；

* clear selection；
* back/forward恢复；
  -无水平溢出；
  -不同时渲染所有 heavy panel；
  -焦点恢复；
  -触摸目标合规。

不得创建压缩版 desktop split view。

---

# 35. Performance

至少测试：

* 1 selection subscriber；
* 8 subscribers；
* 32 panels；
* rapid selection changes；
* repeated panel switching；
* back/forward；
* invalid selection；
* stale selection；
* 32-item bounded multi-selection，如果 contract允许；
* repeated mount/unmount；
* mobile；
* long Workspace session。

必须证明：

-无无限传播循环；
-无 listener leak；
-无 unbounded history growth；
-相同 selection无重复 rerender storm；
-URL bounded；

* stale request被取消或忽略；
* selection不触发全量 Artifact fetch；
* inactive heavy panels不加载；
* Inspector payload bounded；
* 32 panels仍可用。

数字必须称为：

```text
development/browser acceptance evidence
not a production capacity claim
```

---

# 36. Browser Evidence Cases

至少覆盖：

## Case A — Dataset/ML/Composition Sample Link

选择一个真实 sample：

```text
Dataset Explorer
→ ML
→ Composition Space
→ Inspector
```

验证排序和筛选变化。

## Case B — Finding to Evidence to Artifact

```text
Claim
→ Evidence
→ Artifact
→ source panel
```

## Case C — Dependency Lineage

```text
consumer Artifact
→ producer Artifact
→ producer step
```

## Case D — Structure Identity

真实支持时验证 structure/site/atom。

不支持时验证 typed unavailable，不得伪造 PASS。

## Case E — Phonon Identity

真实支持时验证 q-point/branch链。

不支持时 typed unavailable。

## Case F — Stale Selection

修改或加载不匹配 version/hash：

```text
STALE_SELECTION
no propagation
no rebinding
```

## Case G — Unsupported Target Panel

selection保留，target显示不兼容原因。

## Case H — URL Round Trip

* direct link；
* refresh；
* back；
* forward；
* clear；
* invalid URL。

## Case I — Mobile

-选择；

* Inspector bottom sheet；
  -导航；
* clear；
  -焦点；
  -无 overflow。

浏览器矩阵：

```text
Chromium
Firefox
WebKit
Chromium 390x844
```

---

# 37. DeepSeek Browser Case Policy

M3 selection本身不得调用 LLM。

如果 browser evidence使用已经存在的真实 DeepSeek Workspace：

```text
REAL_LLM_CALLS_THIS_PHASE = 0
SOURCE_JOB_PROVIDER = DEEPSEEK
```

如果新建自然语言 Job：

```text
REAL_LLM_CALLS_THIS_PHASE > 0
REAL_PROVIDER = DEEPSEEK
API_KEY_SOURCE = DEEPSEEK_KEY
OTHER_REAL_PROVIDER_CALLS = 0
REAL_PROVIDER_FALLBACKS = 0
```

如果使用 Mock/Fake Job：

-只能标记为 deterministic selection fixture；
-不得标记为真实自然语言链路；
-不得覆盖真实 DeepSeek证据要求。

---

# 38. Required Tests

## 38.1 Contract and Codec

覆盖：

* selection parse；
* serialize；
* round-trip；
* canonical equality；
* version；
* caps；
* unknown fields；
* invalid identity；
* invalid source；
* invalid hash；
* duplicate multi-selection；
* invalid URL；
* oversized URL。

## 38.2 Store

覆盖：

* set；
* same-selection no-op；
* clear；
* subscriber；
* unsubscribe；
* unmount cleanup；
* Workspace切换；
* origin panel；
* no echo loop；
* rapid updates；
* stale update。

## 38.3 Compatibility Resolver

覆盖：

* exact；
* same sample；
* same structure；
* version mismatch；
* hash mismatch；
* scope mismatch；
* target unsupported；
* panel not ready；
* source missing；
* stale；
* legacy。

## 38.4 Panel Integration

覆盖当前真实支持的：

* Dataset；
* ML；
* Composition Space；
* Structure；
* trajectory；
* phonon；
* BZ；
* volumetric；
* findings；
* evidence；
* provenance；
* lineage。

不支持者测试 typed unavailable。

## 38.5 URL and Navigation

覆盖：

* active panel + selection；
* refresh；
* back；
* forward；
* clear；
* unknown panel；
* invalid selection；
* target navigation；
* history bounded。

## 38.6 Inspector

覆盖：

* no selection；
* exact selection；
* source；
* compatibility；
* evidence；
* provenance；
* stale；
* unsupported；
* mobile；
* accessibility。

## 38.7 Security

覆盖第 32 节。

## 38.8 Regression

运行：

* M1 Workspace contract/API；
* M2 Workspace shell；
* Phase 10K linked identity；
* Phase 10L lineage/evidence；
* full backend；
* full frontend；
* typecheck；
* build；
* browser；
* service-backed；
* no-skipped；
* evidence integrity；
* docs links；
* secret scan；
* DeepSeek policy regression。

---

# 39. Service-Backed Evidence

M3 主要是前端运行时，但 service-backed CI仍必须证明 source identities来自真实持久化记录。

使用：

```text
PostgreSQL
Redis
MinIO
migration head 0007
```

至少验证：

* persisted Workspace；
* persisted panels；
* persisted Job；
* persisted Artifact metadata；
* lineage；
* evidence；
* interpretation；
* selection不会写数据库；
  -普通 selection不创建 layout revision；
* no hidden Workspace patch；
* no skipped service tests。

要求：

```text
CI_SERVICE_BACKED = PASS
SERVICE_TESTS_SKIPPED = 0
SELECTION_DATABASE_WRITES = 0
```

本地 Docker不可用：

```text
LOCAL_SERVICE_BACKED = UNAVAILABLE
```

不得写本地 PASS。

---

# 40. Evidence Directory

创建：

```text
docs/phase10m/evidence/phase10m3_canonical_selection/
```

至少包含：

```text
baseline.txt
entry_gate.txt
m2_archive_verification.txt
acceptance_mapping.json
selection_contract_snapshot.json
identity_producer_matrix.json
identity_consumer_matrix.json
panel_subscription_matrix.json
selection_codec_cases.json
selection_store_cases.json
compatibility_cases.json
dataset_ml_composition_case.json
finding_evidence_artifact_case.json
lineage_case.json
structure_case.json
trajectory_case.json
phonon_case.json
volumetric_case.json
stale_selection.json
unsupported_selection.json
url_roundtrip.json
back_forward.json
mobile_selection.json
accessibility.json
performance.json
security.json
database_write_audit.json
deepseek_policy_regression.json
real_deepseek_evidence.json
browser_chromium/
browser_firefox/
browser_webkit/
browser_mobile/
network_summary.json
console_summary.json
screenshots/
test_summary.txt
secret_scan.txt
file_manifest.json
```

若无本阶段真实调用：

```json
{
  "realLlmCalls": 0,
  "newLlmCallSites": 0,
  "reason": "Canonical selection consumes persisted Workspace and Artifact identities",
  "deepSeekPolicyRegression": "PASS"
}
```

Evidence不得包含：

* secret；
* Authorization；
* private path；
* raw Artifact payload；
* unbounded dataset rows；
* raw environment；
* provider key metadata。

---

# 41. Documentation Updates

更新：

```text
docs/phase10m/README.md
docs/phase10m/phase10m3_canonical_selection.md
docs/phase10m/phase10m3_identity_compatibility.md
docs/phase10m/phase10m3_panel_subscriptions.md
docs/phase10m/phase10m3_url_navigation.md
docs/phase10m/phase10m3_inspector.md
docs/phase10m/phase10m3_accessibility_performance_security.md
docs/phase10m/phase10m3_evidence.md
docs/phase10m/phase10m3_completion.md
docs/phase10m/phase10m4_next_scope.md
docs/index.md
docs/ROADMAP.md
docs/13_SHARED_SCHEMA_SPEC.md
```

更新：

```text
persistent/PROJECT_BRIEF.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/CHANGELOG.md
persistent/OPEN_QUESTIONS.md
persistent/ARCHITECTURE_DECISIONS.md
```

必须记录永久规则：

```text
All future real LLM calls use DeepSeek only.
The sole key source is DEEPSEEK_KEY.
Selection runtime itself has no LLM authority.
```

不得记录 key。

不得把 M4–M7 或 10N写成已实现。

---

# 42. Production Behavior Changes

允许：

```text
WorkspaceSelectionContext runtime
selection URL codec
selection state store
panel subscription registry
identity compatibility resolver
cross-panel selection propagation
selection-aware Inspector
finding/evidence/artifact navigation
lineage navigation
selection accessibility/mobile behavior
```

必须保持：

```text
ScientificWorkspace contract unchanged
WorkspacePanel contract unchanged
WorkspaceSelectionContext contract version unchanged
Workspace migration unchanged
Workspace persistence unchanged
Workspace API semantics unchanged
Workspace route unchanged
AnalysisIntent unchanged
Eligibility unchanged
AnalysisPlan unchanged
QueueWorkerRuntime unchanged
Tool Registry unchanged
Adapters unchanged
Artifact contracts unchanged
Interpretation contracts unchanged
Report/Recipe persistence unchanged
DeepSeek-only policy unchanged
```

---

# 43. Explicit Non-Scope

本阶段不实现：

-新 migration；
-selection服务器持久化；
-selection history数据库；
-多用户协作 selection；
-annotation/comment系统；
-跨 Workspace selection；
-多 Job Workspace；
-M4 typed Artifact renderer registry；
-科学 Renderer重写；
-新 WebGL viewer；
-trajectory analytics；
-phonon计算；
-volumetric计算；
-前端 scientific recomputation；
-M5 Report composition；
-Recipe composition；
-M6 layout editor；
-offline recovery；
-recommendation execution；
-plan editor；
-DAG editor；
-new LLM call site；
-new provider；
-new LLM SDK；
-arbitrary Python；
-shell；
-notebook；
-filesystem；
-external science API；
-CrystalNN；
-VoronoiNN；
-experimental XRD；
-electronic Band/DOS；
-RAG；
-memory；
-multi-agent；
-plugin marketplace；
-enterprise SaaS。

---

# 44. Verification Commands

至少运行：

```powershell
git diff --check
uv lock --check
```

frontend：

```powershell
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
```

backend：

```powershell
uv run python -m pytest -q
```

focused：

```text
M1 Workspace contract/API regression
M2 Workspace shell regression
M3 selection contract
M3 URL codec
M3 selection store
M3 compatibility resolver
M3 panel subscriptions
M3 Inspector
M3 cross-navigation
M3 accessibility
M3 security
M3 browser
DeepSeek provider policy regression
```

运行：

```text
Chromium
Firefox
WebKit
390x844 mobile
PostgreSQL/Redis/MinIO service-backed
no-skipped assertion
Phase 10 closure integrity
Phase 10K evidence integrity
Phase 10L evidence integrity
Phase 10M acceptance integrity
Phase 10M evidence integrity
docs links
TASKS structure
secret scan
```

`npm audit`服务不可用时：

```text
npm audit = UNAVAILABLE
```

不得写 clean。

---

# 45. Commit and CI Lifecycle

## 45.1 Implementation Commit

包含：

* selection runtime；
* URL codec；
* store；
* subscriptions；
* compatibility resolver；
* Inspector；
* panel integrations；
* tests；
* browser runners；
* evidence；
* docs；
* persistent；
* TASKS保持 M3处理中。

不得在 implementation commit追加最终 completion result。

push并等待 exact-SHA CI。

必须成功：

```text
Unit
Frontend
Typecheck
Build
Browser
Service-backed
No-skipped
Evidence integrity
Secret scan
```

失败时：

-记录 failed SHA/CI；
-只修复 M3范围；
-不得放宽 identity/security；
-不得进入 M4。

## 45.2 Completion-Record Commit

只有 implementation exact-SHA CI成功后：

-完整 result追加到 `results.md`；
-更新 persistent；
-TASKS标记完成等待归档；
-不删除 task；
-commit/push；
-等待 completion exact-SHA CI。

## 45.3 Queue Archive

只有 completion CI成功后：

-验证 result/evidence/CI；
-删除且只删除 M3 task；
-保留 M4 reviewer gate；
-commit/push；
-等待 archive exact-SHA CI。

最终：

```text
Phase 10M-3:
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT

Phase 10M-4:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 0
```

不得自动进入 M4。

---

# 46. Required Final Result Format

追加：

# Phase 10M-3 Cross-Artifact Navigation + Canonical Selection Result

## 1. Conclusion

archive前：

```text
PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI
```

archive后：

```text
PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT
```

或：

```text
BLOCKED
```

## 2. Baseline and Entry Gate

* M2 implementation；
* M2 completion；
* M2 archive；
  -三次 CI；
* initial HEAD/origin；
* worktree；
* migration；
* task。

## 3. M0–M2 Decision Compliance

## 4. WorkspaceSelectionContext Runtime

## 5. URL Selection Codec

## 6. Selection Store

## 7. Panel Subscription Registry

## 8. Compatibility Resolver

## 9. Selection Propagation

## 10. Canonical Identity Support

逐项列：

* dataset sample；
* material object；
* structure；
* site；
* atom；
* trajectory；
* q-point；
* branch；
* reciprocal；
* volumetric；
* evidence；
* claim；
* Artifact。

每项必须写：

```text
SUPPORTED
UNSUPPORTED_WITH_TYPED_REASON
NOT_APPLICABLE
```

## 11. Dataset / ML / Composition Linkage

## 12. Structure Linkage

## 13. Trajectory Linkage

## 14. Phonon / Reciprocal Linkage

## 15. Volumetric Linkage

## 16. Findings / Evidence / Artifact Linkage

## 17. Lineage Navigation

## 18. Inspector

## 19. Active Panel + Selection Navigation

## 20. Refresh / Back / Forward

## 21. Stale / Unsupported / Missing

## 22. Historical Compatibility

## 23. Scientific Integrity

必须写：

```text
FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE
SELECTION_ARRAY_INDEX_AUTHORITY = NONE
SELECTION_DISPLAY_LABEL_AUTHORITY = NONE
SELECTION_FUZZY_MATCHING = NONE
SELECTION_DATABASE_WRITES = 0
```

## 24. LLM / DeepSeek Compliance

必须写：

```text
NEW_LLM_CALL_SITES = 0
M3_SELECTION_REQUIRES_LLM = NO
REAL_LLM_CALLS = 实际数量
DEEPSEEK_POLICY_REGRESSION = PASS
```

若真实调用大于零：

```text
REAL_PROVIDER = DEEPSEEK
API_KEY_SOURCE = DEEPSEEK_KEY
OTHER_REAL_PROVIDER_CALLS = 0
REAL_PROVIDER_FALLBACKS = 0
```

## 25. Accessibility

## 26. Mobile

## 27. Browser Matrix

## 28. Performance

## 29. Security

列出全部 markers。

## 30. Acceptance IDs

```text
expected =
implemented =
missing = 0
extra = 0
duplicate = 0
```

## 31. Tests

* focused；
* full backend；
* frontend；
* typecheck；
* build；
* browser；
* service；
* no-skipped；
* evidence；
* docs；
* secret；
* npm audit。

## 32. Production Behavior Changes

## 33. Files Changed

必须写：

```text
migration = unchanged
database schema = unchanged
dependencies = unchanged
lockfile = unchanged
Workspace contracts = unchanged
```

## 34. Commit / CI History

* failed attempts；
* corrected implementation；
* implementation CI；
* completion；
* completion CI；
* archive；
* archive CI。

## 35. Explicit Non-Scope

确认 M4–M7和10N未实现。

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
ARCHIVED_BY_VERIFIED_QUEUE_COMMIT

Phase 10M-4:
REVIEWER_GATE / AWAITING REVIEWER PROMPT

TASK_BLOCK_COUNT = 0
```

## 38. Automatic M4 Entry

```text
NO
PHASE_10M4_EXECUTABLE_TASK_CREATED = NO
```

## 39. Next Action

```text
Return the complete Phase 10M-3 result to the reviewer.
Do not create, queue, or execute Phase 10M-4.
```

## 40. Final Repository State

* HEAD；
* origin；
* clean；
* migration head；
* implementation CI；
* completion CI；
* archive CI；
* task count。

---

# 47. PASS Gate

M3 只有全部满足才能 PASS：

* M2 verified archive；
* M2 browser/acceptance完整；
* M0–M2 decisions unchanged；
* Selection contract version unchanged；
* canonical URL codec；
* strict validation；
* selection store；
* cleanup；
* panel subscriptions；
* compatibility resolver；
* cross-panel propagation；
* no echo loop；
* no cross-Workspace leakage；
* stable sample identity；
* exact structure/site/atom scope；
* exact trajectory scope；
* exact phonon scope；
* exact volumetric scope；
* claim/evidence/artifact linking；
* lineage navigation；
* Inspector；
* active panel integration；
* refresh/back/forward；
* typed stale；
* typed unsupported；
* no fuzzy matching；
* no row-order matching；
* no display-label authority；
* no database write；
* no migration；
* no Artifact payload copy；
* no frontend scientific recomputation；
* accessibility；
* mobile；
  -browser matrix；
* performance；
* security；
* exact acceptance IDs；
* M1/M2 regression；
* full backend；
* frontend；
* typecheck/build；
* service-backed zero skipped；
* evidence manifest；
* secret scan；
* DeepSeek policy regression；
  -真实 LLM调用仅使用 DeepSeek和 `DEEPSEEK_KEY`；
* implementation CI；
* completion CI；
* archive CI；
* clean repository；
* M4未创建。

---

# 48. BLOCKED Gate

停止返回 reviewer，如果：

* M2未完整归档；
* M2结果不可信；
* M3 acceptance文档不一致；
* Selection contract不足且需重设计；
* Panel contract缺少必要selection声明且需重设计；
  -需要新 migration；
  -需要服务器持久化selection；
  -需要未封板 API；
* identity只能通过行号/label/fuzzy匹配；
  -需要前端科学计算；
  -需要修改Artifact contract；
  -需要提前进入M4；
  -需要新增LLM call site；
  -需要修改DeepSeek policy；
  -真实 LLM evidence未使用 `DEEPSEEK_KEY`；
  -存在secret风险；
  -service-backed全部 skipped；
  -browser关键链路失败；
  -exact-SHA CI无法闭合；
  -queue异常。

不得自行改变架构继续。

---

# 49. Reviewer Gate After M3

M3 implementation、completion、archive全部通过后停止。

下一阶段：

```text
Phase 10M-4:
Typed Artifact Gallery + Scientific Viewer Integration
```

M4必须基于 M3 的真实：

* supported identity kinds；
* unsupported identity kinds；
* panel subscriptions；
* selection compatibility；
* Inspector；
* browser behavior；
* WebGL需求；
* performance；
  -具体 Renderer gaps；

重新生成 Prompt。

不得提前创建或执行 M4。

---

# 50. 现在开始

第一步不是编写 selection store。

先输出：

```text
Phase 10M-3 Entry Gate + Pre-Implementation Audit
```

必须确认：

1. M2三阶段 SHA 和 CI；
2. M2 archive；
3. HEAD/origin；
4. worktree；
5. migration head；
6. task count；
7. M3 acceptance IDs；
8. Selection contract exact字段；
9. Panel selection declarations；
10. identity producers；
11. identity consumers；
12. M2 inspector和URL现状；
13. M3不需要新 LLM call site；
14. DeepSeek-only policy完整；
    15.无新 migration/API架构需求；
    16.具备实施条件。

只有 Entry Gate 与 Pre-Implementation Audit 都 PASS，才允许修改生产代码。

完成 Phase 10M-3 后，返回完整 result，然后停止。

不得创建、排队或执行 Phase 10M-4。

---END---
