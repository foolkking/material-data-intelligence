# Phase 4：后端服务与数据库设计

## 1. 本阶段目标

定义 MVP 后端服务结构、REST/SSE API 草案、数据库实体、权限模型、多租户隔离、错误模型、Secret 和审计日志边界。Phase 4 以 Phase 2 的 FastAPI 模块化单体 + Celery Worker 架构为基础，给出可进入实现阶段的数据模型和接口边界。

## 2. 本阶段解决的问题

### 后端决策

| 问题 | 决策 |
|---|---|
| MVP 上传是否支持分片 | MVP 使用对象存储预签名直传 + 文件大小限制；分片/断点续传推迟到 V1。 |
| Artifact / Recipe 是否单独版本表 | MVP 使用不可变记录 + `version` 字段；复杂版本树/差异比较推迟到 V1。 |
| 权限模型 | 组织 + 项目 RBAC，项目成员角色控制数据、任务、Artifact、Recipe、配置和导出。 |
| API 错误格式 | 统一 Problem Details 风格错误模型，带 `code`、`message`、`details`、`request_id`。 |
| JobEvent 是否独立表 | 是。用于 Agent Timeline、进度推送、审计回放。 |

## 3. 设计原则

- API 层只做轻任务和编排，不直接执行材料计算。
- 所有实体必须带项目或组织边界，避免跨租户访问。
- Artifact 和 Recipe 默认不可变；重跑生成新版本或新记录。
- Secret 只保存加密引用，业务表不保存明文 Key。
- 状态必须可恢复：PostgreSQL 是事实来源，Redis 只是队列/缓存。
- 错误必须用户可读、机器可处理、可追踪。
- 审计日志覆盖上传、运行、导出、权限、Secret 使用和配置变更。

## 4. 核心模块

| 模块 | FastAPI 包边界 | 职责 |
|---|---|---|
| Auth | `app.auth` | 登录、token、当前用户、组织/项目上下文 |
| Project | `app.projects` | organization、project、membership、project config |
| Dataset | `app.datasets` | dataset、files、upload sessions、field mappings |
| Profile | `app.profiles` | data profile 查询、质量问题、推荐任务 |
| Jobs | `app.jobs` | job、job_events、SSE、cancel、retry |
| Agent | `app.agent` | analysis request、plan、report 调度 |
| Tools | `app.tools` | registry version、tool call metadata |
| Artifacts | `app.artifacts` | artifact metadata、signed URLs、report、recipe |
| Config | `app.configs` | user/project configs、style/material defaults |
| Secrets | `app.secrets` | encrypted secret references、BYOK metadata |
| Audit | `app.audit` | audit log writing and queries |
| Workers | `app.worker_tasks` | Celery task definitions and event emission |

## 5. 数据流 / 控制流

### 5.1 上传控制流

```text
POST /upload-sessions
  -> validate project permission
  -> create upload session
  -> return object storage upload URL

client uploads file to MinIO/S3

POST /upload-sessions/{id}/complete
  -> create files rows
  -> create parse job
  -> enqueue parse-worker
  -> return job id
```

### 5.2 分析控制流

```text
POST /analysis-requests
  -> validate dataset/profile/field mappings
  -> create analysis_request
  -> enqueue llm-worker plan task
  -> write job_events

POST /analysis-requests/{id}/run
  -> validate plan against Tool Registry
  -> create tool_calls
  -> enqueue viz/render workers
  -> write artifacts + recipe + report
```

### 5.3 SSE 事件流

```text
GET /jobs/{job_id}/events
  -> auth + project permission
  -> stream existing events since cursor
  -> stream new job_events
```

## 6. API 草案

### Auth / Current User

```http
GET /me
GET /me/config
PATCH /me/config
```

### Organization / Project

```http
POST /organizations
GET /organizations/{org_id}/projects
POST /projects
GET /projects/{project_id}
PATCH /projects/{project_id}
GET /projects/{project_id}/members
POST /projects/{project_id}/members
PATCH /projects/{project_id}/members/{user_id}
```

### Dataset / Files / Profile

```http
POST /projects/{project_id}/datasets
GET /datasets/{dataset_id}
GET /datasets/{dataset_id}/files
POST /datasets/{dataset_id}/upload-sessions
POST /upload-sessions/{session_id}/complete
POST /datasets/{dataset_id}/parse-jobs
GET /datasets/{dataset_id}/profile
PATCH /datasets/{dataset_id}/field-mappings
```

### Analysis / Jobs

```http
POST /analysis-requests
GET /analysis-requests/{request_id}
GET /analysis-requests/{request_id}/plan
POST /analysis-requests/{request_id}/run
GET /jobs/{job_id}
GET /jobs/{job_id}/events
POST /jobs/{job_id}/cancel
POST /jobs/{job_id}/retry
```

### Tool Calls / Artifacts / Recipes

```http
GET /jobs/{job_id}/tool-calls
GET /jobs/{job_id}/artifacts
GET /artifacts/{artifact_id}
GET /artifacts/{artifact_id}/download-url
POST /recipes
GET /recipes/{recipe_id}
POST /recipes/{recipe_id}/run
```

### Config / Secrets / Audit

```http
GET /projects/{project_id}/config
PATCH /projects/{project_id}/config
GET /projects/{project_id}/secrets
POST /projects/{project_id}/secrets
DELETE /secrets/{secret_id}
GET /projects/{project_id}/audit-logs
```

## 7. 核心 Schema 草案

```ts
type Role = "owner" | "admin" | "researcher" | "viewer";

type JobStatus =
  | "created"
  | "queued"
  | "running"
  | "partial_success"
  | "completed"
  | "failed"
  | "cancel_requested"
  | "cancelled";

type ApiError = {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  request_id: string;
};

type Permission = {
  action:
    | "project.read"
    | "dataset.upload"
    | "job.run"
    | "artifact.export"
    | "recipe.write"
    | "config.write"
    | "secret.manage"
    | "audit.read";
  projectId: string;
};
```

## 8. 数据库表草案

### Identity / Tenant

| 表 | 关键字段 |
|---|---|
| `users` | `id`、`email`、`display_name`、`status`、`created_at` |
| `organizations` | `id`、`name`、`plan`、`created_at` |
| `organization_members` | `org_id`、`user_id`、`role` |
| `projects` | `id`、`org_id`、`name`、`type`、`status`、`created_by` |
| `project_members` | `project_id`、`user_id`、`role` |

### Data

| 表 | 关键字段 |
|---|---|
| `datasets` | `id`、`project_id`、`name`、`dataset_type`、`status`、`profile_id` |
| `files` | `id`、`dataset_id`、`storage_key`、`file_name`、`detected_format`、`status`、`sha256`、`size_bytes` |
| `upload_sessions` | `id`、`dataset_id`、`status`、`expires_at`、`created_by` |
| `data_profiles` | `id`、`dataset_id`、`profile_json`、`n_files`、`n_valid`、`n_failed` |
| `field_mappings` | `id`、`dataset_id`、`mapping_json`、`confirmed_by` |
| `normalized_objects` | `id`、`dataset_id`、`object_type`、`storage_key`、`metadata_json` |

### Agent / Jobs / Tools

| 表 | 关键字段 |
|---|---|
| `sessions` | `id`、`project_id`、`dataset_id`、`created_by` |
| `messages` | `id`、`session_id`、`role`、`content`、`metadata_json` |
| `analysis_requests` | `id`、`project_id`、`dataset_id`、`prompt`、`status` |
| `analysis_plans` | `id`、`request_id`、`plan_json`、`validated_at`、`version` |
| `jobs` | `id`、`project_id`、`dataset_id`、`user_id`、`status`、`priority`、`resource_usage_json` |
| `job_events` | `id`、`job_id`、`event_type`、`status`、`message`、`payload_json` |
| `tool_calls` | `id`、`job_id`、`tool_id`、`input_json`、`params_json`、`status`、`output_artifact_id` |
| `tool_registry_versions` | `id`、`version`、`registry_json`、`created_at` |

### Artifacts / Recipes / Reports

| 表 | 关键字段 |
|---|---|
| `artifacts` | `id`、`project_id`、`job_id`、`tool_call_id`、`type`、`name`、`version`、`storage_key`、`preview_key`、`metadata_json` |
| `visualization_recipes` | `id`、`project_id`、`dataset_id`、`name`、`version`、`recipe_json`、`created_by` |
| `reports` | `id`、`project_id`、`job_id`、`version`、`markdown_key`、`html_key` |

### Config / Secret / Audit

| 表 | 关键字段 |
|---|---|
| `user_configs` | `user_id`、`config_json` |
| `project_configs` | `project_id`、`config_json` |
| `secrets` | `id`、`scope_type`、`scope_id`、`provider`、`encrypted_ref`、`status`、`last_used_at` |
| `audit_logs` | `id`、`org_id`、`project_id`、`actor_id`、`action`、`target_type`、`target_id`、`metadata_json` |

## 9. 权限模型与数据隔离

### 角色能力

| Role | 能力 |
|---|---|
| owner | 项目删除、成员管理、Secret 管理、配置、全部读写 |
| admin | 成员管理外的大部分项目读写、运行任务、导出 |
| researcher | 上传数据、运行分析、保存 Recipe、导出自己有权限的 Artifact |
| viewer | 查看 Data Profile、图表、报告和 Artifact，不运行高成本任务 |

### 隔离原则

- 所有项目资源必须带 `project_id`。
- 所有项目必须属于 `org_id`。
- API 查询默认追加当前用户可访问 project scope。
- Object Storage key 使用 `org/{org_id}/project/{project_id}/...` 前缀。
- Artifact 下载必须先查 PostgreSQL 权限，再生成短期签名 URL。
- Worker 只能通过 job payload 访问授权的 storage key。

## 10. 错误模型

```json
{
  "code": "DATASET_PROFILE_NOT_READY",
  "message": "Dataset profile is not ready yet.",
  "details": {
    "dataset_id": "ds_xxx",
    "current_status": "profiling"
  },
  "request_id": "req_xxx"
}
```

错误分类：

| 类别 | 示例 |
|---|---|
| Auth | `UNAUTHENTICATED`、`PERMISSION_DENIED` |
| Dataset | `UNSUPPORTED_FILE_TYPE`、`PARSE_FAILED` |
| Agent | `PLAN_VALIDATION_FAILED`、`LLM_PROVIDER_ERROR` |
| Tool | `TOOL_NOT_FOUND`、`PARAM_SCHEMA_INVALID`、`TOOL_TIMEOUT` |
| Artifact | `ARTIFACT_NOT_FOUND`、`EXPORT_FAILED` |
| System | `QUEUE_UNAVAILABLE`、`WORKER_CRASHED` |

## 11. 前端交互草案

后端需要支持 Phase 3 工作台：

- 左侧数据区：`datasets`、`files`、`data_profiles`、`field_mappings`。
- 中央图表：`artifacts`、`tool_calls`、signed artifact URL。
- 右侧 Agent：`sessions`、`messages`、`analysis_requests`、`analysis_plans`、`job_events`。
- 底部面板：`job_events`、`artifacts`、`recipes`、`reports`、`warnings`。

SSE 事件必须支持断线重连：

```http
GET /jobs/{job_id}/events?cursor=evt_xxx
```

## 12. 高并发、安全、扩展性考虑

### 高并发

- API 创建 Job 后立即返回，不等待 Worker。
- `jobs.status` 和 `job_events` 是前端状态事实来源。
- Worker 幂等：重复任务不能生成冲突状态，Artifact 用 hash/version 去重。
- 大文件上传走对象存储直传，不让 API 进程承载文件流。

### 安全

- Secret 加密存储，业务逻辑只拿临时解密值。
- Audit log 不记录明文 Secret、prompt 中敏感片段或原始文件内容。
- 所有下载 URL 短期有效。
- 文件上传限制类型、大小和对象 key。
- 权限检查在 API、Artifact URL、Worker job claim 三处执行。

### 扩展性

- V1 增加分片上传和断点续传。
- V1 增加 artifact version tree / comparison。
- V1 可拆分 Data / Agent / Visualization 独立服务。
- V2 接入组织级配额、计费、共享链接和外部协作者。

## 13. 本阶段产出的目标文件

```text
docs/04_BACKEND_SERVICE_DESIGN.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 14. 下一阶段任务

Phase 5：Agent 编排设计。

需要定义：

- Intent Agent。
- Data Agent。
- Visualization Planner。
- Execution Controller。
- Report Agent。
- JSON Plan Schema。
- Tool Calling 约束。
- 可审计过程展示。
- 不展示原始隐藏思维链的替代方案。

