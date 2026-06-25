# Phase 9：Artifact、Recipe 与报告系统

## 1. 本阶段目标

定义平台中 Artifact、Recipe 和 Report 的类型、存储路径、版本管理、复现流程、导出策略、访问控制和前端展示方式。该系统保证每次材料数据分析不只是“一次性出图”，而是可保存、可审计、可复现、可导出、可迁移到新数据集的科研工作流资产。

## 2. 本阶段解决的问题

### 核心定位

```text
ToolCall
  -> Artifact
  -> Recipe
  -> Report
  -> Re-run / Export / Share
```

Artifact 是工具输出的可访问产物；Recipe 是复现分析流程的结构化配置；Report 是面向人阅读的分析总结。三者都必须与 Job、ToolCall、Data Profile、Tool Registry version 和项目权限关联。

### Phase 9 决策

| 问题 | 决策 |
|---|---|
| Plotly canonical artifact | `figure.json` 是 canonical；HTML/PNG preview 是 MVP 派生产物；SVG/PDF 进入 V1。 |
| MatterViz canonical artifact | `viewer.html` + `metadata.json` 是 canonical；`snapshot.png` 是预览。 |
| Report canonical artifact | Markdown 是 canonical；HTML 是派生产物；PDF 推迟到 V1。 |
| Recipe 是否可变 | Recipe 不原地修改；编辑或重跑生成新 version。 |
| MVP 是否公开分享 | 不支持公开分享；只支持项目成员访问和授权导出。 |
| Export package | MVP 支持按 Job 打包下载 artifacts + recipe + report。 |

## 3. 设计原则

- Artifact 不覆盖：重跑生成新 Artifact/version。
- Recipe 可迁移：输入用逻辑引用和字段角色，不绑定一次性临时路径。
- Report 可追溯：报告引用 Artifact、ToolCall、Data Profile 和 Recipe。
- Canonical first：每类产物先定义 canonical，再定义派生导出。
- 权限优先：Artifact 下载必须经过项目权限校验。
- 可复现优先：保存工具版本、参数、输入 hash、环境版本和 schema version。
- 导出可脱敏：导出包不能包含 Secret、内部路径或隐藏思维链。

## 4. 核心模块

| 模块 | 职责 |
|---|---|
| Artifact Service | 保存 Artifact 元数据、签名 URL、版本、预览、下载 |
| Artifact Exporter | 将 ToolResult 导出为 JSON/HTML/PNG/viewer/metrics/table/report；SVG/PDF 进入 V1 |
| Recipe Service | 保存 Recipe、版本、输入绑定、重跑和迁移 |
| Report Service | 生成 Markdown/HTML 报告、插入图表引用 |
| Export Service | 生成 Job export package |
| Access Controller | 校验项目权限、导出权限和分享策略 |
| Provenance Builder | 记录数据、工具、参数、版本和环境 |

## 5. Artifact 类型

| 类型 | 文件 | Canonical | 用途 |
|---|---|---|---|
| Plotly Figure | `figure.json` | 是 | 前端渲染、复现、重新导出 |
| Plotly HTML | `figure.html` | 否 | iframe 交互展示 |
| Preview Image | `preview.png` | 否 | 卡片缩略图 |
| Paper Export | `figure.svg` / `figure.pdf` | 否 | 论文/报告导出，V1 完善 |
| MatterViz Viewer | `viewer.html` | 是 | 3D 结构交互查看 |
| MatterViz Snapshot | `snapshot.png` | 否 | 3D 预览，MVP 可选 |
| Structure JSON | `structure.json` | 可选 | 结构元数据/复现 |
| Metrics JSON | `metrics.json` | 是 | MAE、RMSE、R2、error stats 等结构化指标 |
| Table JSON | `table.json` | 是 | outlier table、failed files、quality issues 小表预览 |
| Table CSV | `table.csv` | 否 | 用户下载表格 |
| Quality Issues JSON | `quality_issues.json` | 是 | 结构质量、解析失败、字段问题 |
| Report Markdown | `report.md` | 是 | 人类可读报告源 |
| Report HTML | `report.html` | 否 | 前端展示 |
| Recipe JSON | `recipe.json` | 是 | 复现流程 |
| Execution Plan | `analysis_plan.json` | 是 | Agent 输出记录 |

## 6. 对象存储路径

路径规则：

```text
org/{org_id}/project/{project_id}/dataset/{dataset_id}/
  raw/{file_id}/{filename}
  normalized/{object_id}/metadata.json
  normalized/{object_id}/data.parquet
  normalized/{object_id}/structures.jsonl
  normalized/{object_id}/structure_{idx}.json
  jobs/{job_id}/
    tool_calls/{tool_call_id}/
      artifacts/{artifact_id}/figure.json
      artifacts/{artifact_id}/figure.html
      artifacts/{artifact_id}/preview.png
    reports/{report_id}/report.md
    reports/{report_id}/report.html
    recipes/{recipe_id}/recipe.json
```

原则：

- storage key 不包含用户输入的原始路径。
- 下载文件名可读，但对象 key 使用 UUID。
- 所有访问通过 Artifact Service 生成短期签名 URL。
- Structure collection 使用 jsonl / compressed JSON；DataFrame 使用 parquet；Composition list 使用 jsonl。
- Metrics 和小表可用 JSON；大表使用 parquet + preview JSON，不把几十万行表格写成单个大型 JSON。

## 7. Artifact 元数据

Artifact 的正式字段以 `docs/13_SHARED_SCHEMA_SPEC.md` 中的 `Artifact` 和 `ArtifactMetadata` 为准。

本阶段只补充 Artifact Service 的存储路径、导出策略、权限策略和生命周期管理，避免和共享 Schema 重复维护。

## 8. Recipe JSON

Recipe 是可复现流程，不是 UI 布局。

```ts
type VisualizationRecipe = {
  schemaVersion: "0.1";
  recipeId: string;
  name: string;
  version: string;
  projectId: string;
  sourceJobId?: string;
  sourcePlanId?: string;
  inputRequirements: Array<{
    role: "structures" | "formulas" | "dataframe" | "target" | "prediction" | "uncertainty";
    objectType?: string;
    fieldRole?: string;
    required: boolean;
  }>;
  steps: Array<{
    stepId: string;
    toolId: string;
    toolVersion: string;
    inputBindings: Record<string, string>;
    params: Record<string, unknown>;
    artifactTypes: ArtifactType[];
  }>;
  style?: Record<string, unknown>;
  environment: {
    pythonVersion?: string;
    pymatvizVersion?: string;
    pymatgenVersion?: string;
    aseVersion?: string;
    plotlyVersion?: string;
    mattervizVersion?: string;
    llmProviderRequirement?: "openai-compatible";
    modelClass?: "reasoning" | "general";
  };
};
```

Recipe 不保存具体 `SecretRef`、用户 BYOK ID 或系统 Key 引用，只保存 provider 能力需求和模型类别。重跑时由当前 job runner 的权限和项目策略重新解析可用 LLM 执行配置。

## 9. Recipe 复现流程

```text
User selects Recipe
  -> choose target Dataset
  -> system checks inputRequirements
  -> resolve field mappings
  -> validate tools and params
  -> create new AnalysisPlan
  -> enqueue Job
  -> generate new Artifacts and Report
```

校验失败示例：

- 新数据集没有 `formula`。
- 没有 `target/prediction` 字段。
- 当前 Tool Registry 不包含旧 tool version。
- 结构数量超过当前资源限制。

## 10. Report 系统

### Report 结构

```text
Title
Dataset Summary
Analysis Goal
Generated Visualizations
Key Findings
Warnings and Limitations
Tool Calls and Parameters
Reproducibility
Next Steps
```

### Report 输入

- Data Profile。
- Analysis Plan。
- ToolCall 列表。
- Artifact metadata。
- Quality Issues。
- Result Explainer 输出。
- Recipe link。

### Report 输出

MVP：

- `report.md` canonical。
- `report.html` 展示。

V1：

- `report.pdf`。
- 论文图导出包。
- 分享链接。

## 11. 版本管理

MVP：

- Artifact / Recipe / Report 不覆盖。
- 使用 `version` 字段和 `source_*` 引用。
- 重跑生成新记录。

V1：

- `artifact_versions` / `recipe_versions`。
- diff 视图。
- report revision history。

## 12. 分享与导出

### MVP

- 项目成员内访问。
- 授权用户可下载单个 Artifact。
- 授权用户可下载 Job export package。
- 不支持公开链接。

### Export package 内容

```text
manifest.json
analysis_plan.json
recipe.json
report.md
report.html
artifacts/
  figure.json
  figure.html
  preview.png
  viewer.html
  snapshot.png   # optional in MVP
  metrics.json
  table.json
  quality_issues.json
```

`manifest.json` 记录：

- project/dataset/job metadata。
- artifact list。
- tool versions。
- hashes。
- generated_at。

## 13. 数据流 / 控制流

```text
ToolResult
  -> Artifact Exporter
  -> Object Storage
  -> artifacts row
  -> job_events artifact.ready
  -> Report Service reads artifact metadata
  -> report.md/report.html
  -> Recipe Service saves recipe.json
```

## 14. API / Schema 草案

```http
GET /jobs/{job_id}/artifacts
GET /artifacts/{artifact_id}
GET /artifacts/{artifact_id}/download-url
POST /jobs/{job_id}/export-package
GET /recipes/{recipe_id}
POST /recipes
POST /recipes/{recipe_id}/run
GET /reports/{report_id}
```

## 15. 数据库表草案

| 表 | 关键字段 |
|---|---|
| `artifacts` | `type`、`version`、`storage_key`、`preview_key`、`content_hash`、`metadata_json` |
| `visualization_recipes` | `version`、`recipe_json`、`source_job_id`、`created_by` |
| `reports` | `version`、`markdown_key`、`html_key`、`source_job_id` |
| `export_packages` | `job_id`、`storage_key`、`manifest_json`、`expires_at` |
| `artifact_access_logs` | `artifact_id`、`actor_id`、`action`、`created_at` |

## 16. 前端交互草案

- Chart Card 显示 Artifact 状态、预览、导出按钮。
- Bottom Artifact Tab 显示全部产物列表。
- Recipe Tab 显示复现流程、输入要求、参数和版本。
- Report Tab 显示 HTML 报告。
- Export 按钮触发后台生成 export package。
- Re-run Recipe 时弹出目标 Dataset 选择和输入映射确认。

## 17. 高并发、安全、扩展性考虑

### 高并发

- Artifact 写入对象存储，不经过 API 内存中转。
- Export package 异步生成。
- 大 Artifact 下载走签名 URL。
- Report 生成进入 `export` 或 `llm` queue。

### 安全

- Artifact 访问必须校验项目权限。
- 导出包不包含 Secret、内部绝对路径、隐藏思维链。
- HTML Artifact 使用 sandboxed iframe。
- Export package 可设置过期时间。
- 访问记录进入 audit log。

### 扩展性

- V1 支持 PDF。
- V1 支持公开分享链接和过期策略。
- V1 支持 Artifact/Recipe diff。
- V2 支持团队 Recipe 库和模板市场。

## 18. 本阶段产出的目标文件

```text
docs/09_ARTIFACT_AND_RECIPE_SYSTEM.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 19. 下一阶段任务

Phase 10：用户配置、安全与专业扩展。

需要定义：

- 用户配置。
- 项目配置。
- LLM Key / BYOK。
- Secret 管理。
- 沙箱执行。
- 文件安全。
- Prompt injection 防护。
- 权限与审计。
- 插件化材料领域扩展。
## Phase 4 Addendum: artifact metadata consistency

- Artifact repository writes now validate the storage provider before metadata
  is persisted. `local` may omit `bucket`; `s3` and `minio` require `bucket`.
- Artifact metadata must include `storage_provider`, `bucket`, `storage_key`,
  `content_type`, `size_bytes`, `sha256`, `preview_key`, and `created_at`
  whenever the field is applicable to the provider.
- Duplicate artifact metadata writes are idempotent for the same
  `(job_id, storage_key, sha256)` tuple. Repeated worker attempts should return
  the stable artifact row instead of creating uncontrolled duplicates.
- `signed_url()` for the S3/MinIO mapping remains a placeholder in this phase;
  live client calls and presigned URL generation are reserved for the next
  storage-runtime phase.
