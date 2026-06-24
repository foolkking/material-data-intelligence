# Phase 10：用户配置、安全与专业扩展

## 1. 本阶段目标

定义平台的用户配置、项目配置、材料分析默认参数、图表风格配置、LLM Key / BYOK、Secret 管理、沙箱执行、文件安全、Prompt injection 防护、权限与审计，以及插件化材料领域扩展机制。

Phase 10 的目标是把系统从“能运行的分析工具”提升为“可多用户使用、可配置、可审计、可扩展的材料分析平台”。

## 2. 本阶段解决的问题

### Phase 10 决策

| 问题 | 决策 |
|---|---|
| MVP 沙箱执行 | 使用 Docker/容器化 Worker 沙箱 + 每 job 临时目录 + CPU/内存/超时限制；进程级隔离不足。 |
| BYOK 范围 | MVP 支持用户级 BYOK；组织级共享 Key 推迟到 V1。 |
| Secret 存储 | 使用 envelope encryption，数据库只保存加密引用和 metadata，不保存明文。 |
| Prompt injection | MVP 使用规则检测 + 上下文隔离 + Plan Validator；模型辅助检测推迟到 V1。 |
| 插件扩展 | 插件必须声明工具、权限、资源、网络和 Secret 需求；默认无网络、无 Secret、无 shell。 |
| 配置优先级 | 系统默认 < 用户配置 < 项目配置 < 单次 Recipe/Job 参数。 |

## 3. 设计原则

- 安全默认开启：不依赖用户主动配置安全策略。
- 最小权限：用户、项目、Worker、插件、Secret 都只拿到必要权限。
- 配置可追溯：影响结果的配置必须写入 Recipe / Artifact metadata。
- Secret 不外泄：不进入 prompt、日志、Artifact、导出包或前端响应。
- 沙箱内执行：材料解析、可视化、导出在受控 Worker 环境执行。
- 插件显式授权：任何网络、Secret、文件系统扩展能力都必须声明并由管理员启用。
- 审计完整：上传、运行、导出、Secret 使用、权限变更、配置变更都进入 audit log。

## 4. 核心模块

| 模块 | 职责 |
|---|---|
| User Config Service | 用户主题、语言、默认模型、导出偏好 |
| Project Config Service | 项目单位、字段默认值、预算、材料参数、图表风格 |
| Secret Service | BYOK、外部 API Key、加密、轮换、访问审计 |
| Policy Engine | RBAC、预算、资源限制、工具权限 |
| Sandbox Manager | Worker 容器、临时目录、资源限制、网络策略 |
| File Security Scanner | 文件类型、大小、压缩包、路径穿越、危险内容 |
| Prompt Guard | prompt injection 检测、上下文隔离、风险事件 |
| Audit Service | 结构化审计日志 |
| Plugin Manager | 插件 manifest、工具注册、权限声明、启用/禁用 |

## 5. 配置模型

### 配置优先级

```text
system defaults
  < user_config
  < project_config
  < recipe/job params
```

### 用户配置

```json
{
  "theme": "dark",
  "language": "zh-CN",
  "default_llm_provider": "openai-compatible",
  "default_model": "project-default",
  "default_download_formats": ["html", "json", "png"],
  "max_cost_per_job": 2.0
}
```

### 项目配置

```json
{
  "project_domain": "battery_materials",
  "default_units": {
    "energy": "eV",
    "length": "angstrom",
    "pressure": "GPa"
  },
  "default_columns": {
    "formula": "formula",
    "target": "y_true",
    "prediction": "y_pred",
    "uncertainty": "y_std"
  },
  "budget": {
    "max_cost_per_job": 5.0,
    "max_concurrent_jobs": 3
  }
}
```

### 材料分析配置

```json
{
  "xrd_wavelength": "CuKa",
  "rdf_cutoff": 10.0,
  "rdf_bins": 200,
  "neighbor_strategy": "CrystalNN",
  "show_bonds": true,
  "show_cell": true,
  "composition_embedding": "magpie",
  "projection": "umap"
}
```

### 可视化风格配置

```json
{
  "plotly_template": "plotly_dark",
  "font_family": "Inter",
  "figure_width": 900,
  "figure_height": 600,
  "color_scale": "Viridis",
  "paper_export_style": "nature"
}
```

## 6. Secret 与 BYOK

### MVP 范围

- 用户级 BYOK。
- LLM Secret 按 job runner 解析，项目配置不能直接绑定另一个用户的 BYOK 明文或引用。
- 组织级共享 Key 推迟到 V1。
- 系统托管模型 Key 可由部署管理员配置，不暴露给项目成员。

### LLM Secret 解析优先级

MVP 按以下顺序解析 LLM 执行配置：

1. `job_runner_user_secret`：运行该 Job 的用户自己的 BYOK。
2. `project_default_system_provider`：项目允许的系统托管 provider profile。
3. `system_hosted_key`：部署级默认托管 Key，受组织/项目预算限制。

项目配置可以声明 provider policy、模型类别和预算，但不能引用其他成员的用户级 BYOK。Owner 离开项目或撤销 Secret 时，不影响历史 Recipe 的结构，但后续重跑必须由新的 job runner 重新解析可用 provider。

```ts
type LlmExecutionProfile = {
  providerPolicy: "runner_user_byok" | "system_hosted" | "project_default";
  provider?: string;
  model?: string;
  maxCostPerJob: number;
};

type RecipeEnvironment = {
  llmProviderRequirement?: "openai-compatible";
  modelClass?: "reasoning" | "general";
};
```

### Secret 存储原则

- 数据库保存 `encrypted_ref`、provider、scope、status、last_used_at。
- 明文只在 Worker 调用外部服务时短暂解密。
- Secret 不进入 prompt、日志、JobEvent、Artifact、Recipe、Report、导出包。
- 所有 Secret 使用写 audit log。

```ts
type SecretRef = {
  id: string;
  scopeType: "user" | "project" | "organization" | "system";
  scopeId: string;
  provider: "openai" | "anthropic" | "gemini" | "deepseek" | "custom";
  status: "active" | "revoked" | "expired";
  encryptedRef: string;
  lastUsedAt?: string;
};
```

## 7. 沙箱执行

### MVP 策略

Worker 在容器中执行：

- 每 job 独立临时目录。
- 只挂载必要输入文件。
- 默认禁止 shell。
- 默认禁止外部网络；LLM Worker 例外，但只允许访问配置 provider。
- CPU / 内存 / 运行时间限制。
- 任务结束清理临时目录。

### 不允许

- 任意系统命令。
- 任意本地路径读取。
- 任意网络访问。
- 插件默认访问 Secret。
- 将 Secret 写入文件或 Artifact。

## 8. 文件安全

### 检查项

| 风险 | 防护 |
|---|---|
| 超大文件 | size limit |
| zip bomb | expanded size / file count / depth limit |
| path traversal | normalize path + reject `../` |
| 伪装扩展名 | magic bytes + content sniffing |
| 解析器卡死 | timeout |
| 恶意 HTML/JS artifact | sandboxed iframe + CSP |
| CSV/JSON prompt injection | data/instruction separation |

### 文件处理原则

- raw file 只读。
- normalized object 是派生产物。
- file name 展示前转义。
- 解析失败不阻止成功文件继续分析。

## 9. Prompt injection 防护

### MVP 防护层

1. 上下文隔离：用户 prompt、Data Profile、Tool Registry、系统策略分开。
2. 规则检测：识别要求忽略规则、读取 Secret、执行 shell、访问任意路径等。
3. Plan Validator：即使 LLM 输出危险计划，也无法通过 Schema/Tool 校验。
4. Timeline warning：可疑输入对用户可见。
5. Audit log：高风险事件进入审计。

### V1

- 模型辅助检测。
- 数据源引用追踪。
- Prompt injection 测试集。

## 10. 权限与审计

### 权限

继续采用 Phase 4 的 organization + project RBAC：

| Role | 关键权限 |
|---|---|
| owner | Secret 管理、成员管理、删除、全部读写 |
| admin | 配置、运行、导出、Recipe 管理 |
| researcher | 上传、运行、保存 Recipe、导出 |
| viewer | 查看 profile、artifact、report |

### 审计事件

必须审计：

- 登录和权限变更。
- 文件上传和删除。
- Job run/cancel/retry。
- ToolCall execution。
- Artifact export/download。
- Recipe create/run。
- Secret create/use/revoke。
- Project config change。
- Plugin enable/disable。
- Prompt injection warning/block。

## 11. 插件化材料领域扩展

### 插件 manifest

```json
{
  "plugin_id": "materials.vasp",
  "name": "VASP Analysis Tools",
  "version": "0.1.0",
  "tools": ["vasp.energy_convergence"],
  "permissions": {
    "network": false,
    "secret_access": false,
    "shell": false,
    "max_timeout_sec": 300
  }
}
```

### 插件默认策略

- 默认禁用。
- 项目管理员启用。
- 必须声明工具 Schema。
- 必须声明资源需求。
- 必须通过沙箱运行。
- 必须输出标准 Artifact。

## 12. 数据流 / 控制流

### BYOK 调用流

```text
User configures Secret
  -> Secret encrypted
  -> Project config stores provider policy, not another user SecretRef
  -> LLM job starts
  -> Resolve Secret from job runner user or allowed system provider
  -> Worker requests temporary decrypted value
  -> Provider call
  -> Secret released
  -> audit_logs secret.used
```

### 安全执行流

```text
ToolCall
  -> Policy Engine
  -> Resource Guard
  -> Sandbox Manager
  -> Worker executes Adapter
  -> Artifact Exporter
  -> Audit log
```

## 13. API / Schema 草案

```http
GET /me/config
PATCH /me/config
GET /projects/{project_id}/config
PATCH /projects/{project_id}/config
GET /projects/{project_id}/llm-policy
PATCH /projects/{project_id}/llm-policy
GET /me/secrets
POST /me/secrets
DELETE /me/secrets/{secret_id}
GET /projects/{project_id}/audit-logs
GET /plugins
POST /projects/{project_id}/plugins/{plugin_id}/enable
POST /projects/{project_id}/plugins/{plugin_id}/disable
```

MVP Secret API 只管理当前用户 BYOK。项目配置只保存 provider policy、模型类别、预算和 system-hosted provider 开关；项目级共享 Secret API 推迟到 V1。

```ts
type ProjectSecurityConfig = {
  allowExternalNetwork: boolean;
  maxConcurrentJobs: number;
  maxCostPerJob: number;
  maxUploadSizeMb: number;
  enabledPlugins: string[];
  defaultSandboxProfile: "strict" | "standard";
};
```

## 14. 数据库表草案

| 表 | 关键字段 |
|---|---|
| `user_configs` | `user_id`、`config_json` |
| `project_configs` | `project_id`、`config_json`、`updated_by` |
| `secrets` | `scope_type`、`scope_id`、`provider`、`encrypted_ref`、`status` |
| `audit_logs` | `actor_id`、`action`、`target_type`、`target_id`、`metadata_json` |
| `plugins` | `plugin_id`、`name`、`version`、`manifest_json` |
| `plugin_tools` | `plugin_id`、`tool_id`、`schema_json` |
| `project_plugins` | `project_id`、`plugin_id`、`status`、`enabled_by` |
| `security_events` | `project_id`、`event_type`、`severity`、`payload_json` |

## 15. 前端交互草案

- Settings 页面分为 Profile、Project、LLM Keys、Security、Plugins、Audit。
- BYOK 表单只允许创建/撤销，不显示明文。
- Secret 创建后只显示 provider、scope、last used、status。
- Project security 显示上传限制、预算、并发、插件状态。
- Audit log 支持按 actor/action/time 过滤。
- Prompt injection warning 出现在 Agent Timeline 和 Warnings 面板。

## 16. 高并发、安全、扩展性考虑

### 高并发

- Secret 解密短时缓存仅限 Worker 内存，不跨任务共享。
- Audit log 异步写入但不能丢失关键事件。
- Plugin 工具按 costLevel 和 sandbox profile 限流。

### 安全

- Container sandbox 是 MVP 默认。
- Secret never logs。
- Artifact HTML sandbox。
- File parser timeout。
- Plugin no shell/network/secret by default。

### 扩展性

- V1 组织级 BYOK。
- V1 模型辅助 prompt injection 检测。
- V1 公开分享安全策略。
- V2 插件市场和组织级插件白名单。

## 17. 本阶段产出的目标文件

```text
docs/10_USER_CONFIG_AND_SECURITY.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 18. 下一阶段任务

Phase 11：MVP Roadmap 与开发计划。

需要定义：

- MVP 范围。
- V1 范围。
- V2 范围。
- 任务拆解。
- 技术栈选择。
- 优先级。
- 风险清单。
- 验收标准。
