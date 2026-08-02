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
