# Phase 6：工具注册表与 Adapter 设计

## 1. 本阶段目标

定义 Tool Registry、Tool Schema、Adapter 层、输入校验、输出 Artifact、错误标准化、缓存策略、pymatviz 函数封装、MatterViz 3D Viewer 封装和专业材料工具扩展机制。该设计是 Agent JSON Plan 能安全执行的核心边界。

## 2. 本阶段解决的问题

### Tool Registry 定位

Tool Registry 是系统唯一允许执行材料分析与可视化工具的入口。Agent 不能直接调用 Python 函数、shell、文件系统或网络，只能引用 Registry 中注册的 `tool_id` 和符合 Schema 的参数。

### Phase 6 决策

| 问题 | 决策 |
|---|---|
| pymatviz 函数 Schema 如何维护 | MVP 采用手写 Schema + 单元测试；后续评估半自动提取函数签名。 |
| MatterViz Widget 如何保存 | MVP 必须输出 `viewer.html` + `metadata.json` + `recipe.json`；`snapshot.png` 和 `structure.json` 为可选输出，通过 sandboxed iframe 展示。 |
| Plotly JSON 与 HTML 如何统一 | 每个 Plotly 工具必须输出 `figure.json`，可选 `figure.html` 和 `preview.png`。 |
| 大型 3D 结构如何降级 | Adapter 根据 atom count / frame count 自动设置 LOD、关闭 bonds 或抽帧。 |
| 工具错误如何标准化 | 统一 `ToolError`，区分 validation/runtime/resource/export/cache 错误。 |
| MVP 是否支持 phonon | Phonon 工具进入 V1；MVP 只保留 Schema 和扩展点。 |

## 3. 设计原则

- Registry 是执行白名单。
- Adapter 隔离上游库变化。
- 输入输出强类型化。
- 工具默认异步执行。
- Artifact 标准化、可复现、可导出。
- 错误可分类、可重试、可展示。
- 缓存由数据 hash、工具版本和参数 hash 决定。
- 专业材料扩展通过插件注册，不修改 Agent 核心。

## 4. 核心模块

| 模块 | 职责 |
|---|---|
| Tool Registry | 保存工具定义、版本、分类、Schema、成本、权限和 Adapter |
| Tool Adapter | 将标准输入转换为 pymatviz / MatterViz / Plotly 调用 |
| Input Resolver | 根据 `inputRefs` 读取 Data Profile、normalized objects、DataFrame columns、Artifact |
| Param Validator | JSON Schema 校验参数、默认值、范围和枚举 |
| Execution Wrapper | 超时、资源限制、日志、异常捕获、cache lookup |
| Artifact Exporter | 输出 Plotly JSON/HTML/PNG、MatterViz HTML、metrics/table、summary、recipe；snapshot/SVG/PDF 按阶段启用 |
| Error Normalizer | 将 Python/library 异常转成标准 ToolError |
| Plugin Loader | 加载专业扩展工具定义和 Adapter |

## 5. Tool Schema

共享枚举以 `docs/13_SHARED_SCHEMA_SPEC.md` 为准。本文件只保留 Tool Registry 侧的关键结构和示例。

```ts
type RegisteredTool = {
  toolId: string;
  name: string;
  category: ToolCategory;
  domain: ToolDomain;
  implementationSource: ImplementationSource;
  description: string;
  version: string;
  adapter: string;
  inputSchema: ToolInputSchema;
  paramsSchema: Record<string, unknown>;
  outputSchema: ToolOutputSchema;
  artifactFormats: ArtifactType[];
  costLevel: "low" | "medium" | "high";
  defaultTimeoutSec: number;
  maxTimeoutSec: number;
  cachePolicy: "reuse" | "refresh" | "no_cache";
  permissions: string[];
  resourceLimits: {
    maxRows?: number;
    maxStructures?: number;
    maxAtomsPerStructure?: number;
    maxFrames?: number;
  };
};

type ToolInputSchema = {
  inputOptions: ToolInputOption[];
  periodicity?: StructurePeriodicityRequirement;
};

type ToolInputOption = {
  name: string;
  requiredObjectTypes?: MaterialObjectType[];
  requiredFields?: Array<{
    role: FieldRole;
    dtype?: "string" | "number" | "category";
  }>;
  description: string;
};

type ToolOutputSchema = {
  primaryArtifactType: ArtifactType;
  secondaryArtifactTypes: ArtifactType[];
  displayTarget: DisplayTarget;
};
```

`ToolInputSchema.inputOptions` 表达 OR 关系。例如 `composition.ptable_heatmap` 可接受 formula 列、`Composition[]` 或 element-value mapping：

```json
{
  "toolId": "composition.ptable_heatmap",
  "inputSchema": {
    "inputOptions": [
      {
        "name": "formula_column",
        "requiredFields": [{ "role": "formula", "dtype": "string" }],
        "description": "Use formulas from a table column."
      },
      {
        "name": "composition_objects",
        "requiredObjectTypes": ["Composition"],
        "description": "Use normalized Composition objects."
      },
      {
        "name": "element_value_map",
        "requiredObjectTypes": ["ElementValueMap"],
        "description": "Use element-to-value mapping."
      }
    ]
  }
}
```

## 6. MVP Tool Set

| Tool ID | Adapter | 输入 | 输出 |
|---|---|---|---|
| `composition.ptable_heatmap` | `PTableHeatmapAdapter` | formulas / Composition[] / element values | Plotly JSON/HTML/PNG |
| `composition.elements_hist` | `ElementsHistAdapter` | formulas / Composition[] | Plotly JSON/HTML/PNG |
| `composition.chem_sys_treemap` | `ChemSysTreemapAdapter` | formulas / Structure[] / Composition[] | Plotly JSON/HTML/PNG |
| `structure.structure_3d` | `Structure3DAdapter` | Structure / Structure[] | Plotly JSON/HTML/PNG |
| `structure.viewer_3d` | `MatterVizStructureAdapter` | Structure | MatterViz HTML/metadata，snapshot 可选 |
| `structure.coordination_hist` | `CoordinationHistAdapter` | Structure[] | Plotly JSON/HTML/PNG |
| `ml.density_scatter` | `DensityScatterAdapter` | DataFrame with target/prediction | Plotly JSON/HTML/PNG |
| `ml.error_distribution` | `ErrorDistributionAdapter` | DataFrame with target/prediction | Plotly JSON/HTML/PNG + metrics JSON + outlier table |
| `ml.basic_metrics` | `BasicMetricsAdapter` | DataFrame with target/prediction | metrics JSON + summary |
| `ml.outlier_table` | `OutlierTableAdapter` | DataFrame with target/prediction | table JSON/CSV |

V1 扩展：`structure.rdf`、`structure.xrd`、`structure.spacegroup_bar`、`composition.cluster_2d/3d`、`ml.parity_plot`、`ml.uncertainty_calibration`、`ml.error_by_element`、`ml.error_by_chem_sys`、`phonon.band`、`phonon.dos`、`trajectory.viewer`。

V2 扩展：VASP/LAMMPS 专业工具、电子结构工具、生成材料评估工具和外部生态插件。

## 7. Adapter 执行流程

```text
ToolExecutionRequest
  -> Tool Registry lookup
  -> Input Resolver
  -> Param Validator
  -> Cache lookup
  -> Adapter.run()
  -> Artifact Exporter
  -> ToolCall status update
  -> JobEvent artifact.ready
```

Adapter 接口：

```ts
interface ToolAdapter {
  toolId: string;
  prepare(inputRefs: InputRef[], params: Record<string, unknown>): PreparedInput;
  run(input: PreparedInput, params: Record<string, unknown>): ToolResult;
  export(result: ToolResult, formats: ArtifactType[]): ArtifactDraft[];
}
```

Python 实现可采用抽象基类：

```python
class BaseToolAdapter:
    tool_id: str

    def prepare(self, context, input_refs, params): ...
    def run(self, prepared, params): ...
    def export(self, result, formats): ...
```

## 8. 输入校验

### 校验层级

| 层级 | 校验内容 |
|---|---|
| Plan validation | tool exists、inputRefs exist、params schema |
| Input resolution | normalized object exists、field mapping confirmed |
| Domain validation | Structure periodicity、DataFrame numeric columns、atom/frame limits |
| Resource validation | rows、structures、atoms、frames、timeout、cost |
| Security validation | no arbitrary paths、no secrets、no unauthorized artifact refs |

### 示例

`ml.density_scatter` 必须满足：

- DataFrame 可用。
- target 和 prediction 字段已映射。
- 字段为 numeric。
- 行数超过阈值时自动启用 density / binning。

`structure.viewer_3d` 必须满足：

- Structure 可用。
- 原子数不超过硬限制。
- 超过 LOD 阈值时关闭 bonds 或采样。

`structure.xrd` 等周期结构工具必须满足：

- `inputSchema.periodicity = "periodic_required"`。
- plain XYZ 或无 lattice 的 `Atoms` 不允许进入该工具。
- EXTXYZ 只有在包含 `Lattice=` 并成功标准化为周期结构后才可用。

## 9. Artifact 输出标准

### Plotly 工具

每个 Plotly Adapter 必须输出：

```text
figure.json
summary.md
recipe.json
```

可选输出：

```text
figure.html
preview.png
figure.svg
figure.pdf
```

MVP 中 `figure.svg` / `figure.pdf` 不作为 render-worker 必做能力，进入 V1 论文图导出链路。

### MatterViz 工具

每个 MatterViz Adapter 必须输出：

```text
viewer.html
metadata.json
recipe.json
```

可选输出：

```text
snapshot.png
structure.json
```

### Artifact metadata

```ts
type ArtifactMetadata = {
  toolId: string;
  toolVersion: string;
  adapterVersion: string;
  inputHashes: string[];
  paramsHash: string;
  pymatvizVersion?: string;
  mattervizVersion?: string;
  plotlyVersion?: string;
  createdAt: string;
};
```

## 10. 错误标准化

```ts
type ToolError = {
  code:
    | "TOOL_INPUT_INVALID"
    | "TOOL_PARAM_INVALID"
    | "TOOL_RESOURCE_LIMIT"
    | "TOOL_RUNTIME_ERROR"
    | "TOOL_EXPORT_FAILED"
    | "TOOL_TIMEOUT"
    | "TOOL_CACHE_ERROR";
  message: string;
  retryable: boolean;
  stepId?: string;
  toolId: string;
  details?: Record<string, unknown>;
};
```

错误展示原则：

- 用户看到可理解 message。
- Timeline 显示 warning/error。
- Logs 保留技术摘要。
- 不暴露内部路径、Secret、完整堆栈给普通用户。

## 11. 缓存策略

缓存 key：

```text
tool:{tool_id}:{tool_version}:{adapter_version}:{input_hash}:{params_hash}:{style_hash}
```

可缓存：

- parsed normalized object。
- Data Profile。
- Plotly figure JSON。
- HTML artifact。
- preview image。
- report fragment。

不默认缓存：

- 含临时 Secret 的外部 API 调用结果。
- 明确 `no_cache` 的工具。
- 用户要求 refresh 的工具。

## 12. pymatviz 封装原则

- Adapter 不直接暴露 pymatviz 原始参数全集，只暴露平台批准参数。
- 参数命名尽量领域语义化，例如 `colorBy`、`countMode`、`neighborStrategy`。
- 默认值来自项目配置和工具定义。
- 所有函数版本写入 Artifact metadata。
- 上游异常转成 ToolError。

示例：

```json
{
  "tool_id": "structure.coordination_hist",
  "params": {
    "neighborStrategy": "CrystalNN",
    "splitMode": "by_element"
  }
}
```

## 13. MatterViz 3D Viewer 封装

MVP 封装策略：

- 输入：单个 Structure 或代表结构集合。
- 输出：`viewer.html`、`metadata.json`、`recipe.json`。
- 可选输出：`snapshot.png`、`structure.json`。
- 展示：前端 sandboxed iframe。
- 大结构：自动 LOD。
- 默认不开启 trajectory 全帧播放。

Viewer metadata：

```json
{
  "formula": "LiFePO4",
  "n_atoms": 28,
  "spacegroup": "Pnma",
  "show_bonds": true,
  "show_cell": true,
  "lod": "full"
}
```

## 14. 专业扩展机制

插件工具必须提供：

- manifest。
- tool schema。
- adapter class。
- version。
- artifact formats。
- resource limits。
- security declaration。

```json
{
  "plugin_id": "materials.vasp",
  "tools": [
    {
      "tool_id": "vasp.energy_convergence",
      "category": "analysis",
      "domain": "simulation",
      "implementationSource": "plugin",
      "adapter": "VaspEnergyConvergenceAdapter"
    }
  ]
}
```

插件默认不可访问网络、Secret 或任意文件路径，除非明确声明并由项目管理员启用。

## 15. 数据流 / 控制流

```text
AnalysisPlan.step
  -> ToolCall row
  -> ToolExecutionRequest
  -> Registry lookup
  -> Adapter execution
  -> Artifact rows
  -> JobEvents
  -> Frontend chart cards
```

## 16. API / Schema 草案

```http
GET /tools
GET /tools/{tool_id}
GET /tool-registry/versions/current
POST /tool-calls/{tool_call_id}/retry
```

```ts
type ToolRegistryView = {
  version: string;
  tools: RegisteredTool[];
};

type ToolExecutionRequest = {
  jobId: string;
  stepId: string;
  toolId: string;
  inputRefs: InputRef[];
  params: Record<string, unknown>;
  artifactFormats: ArtifactType[];
};
```

## 17. 数据库表草案

| 表 | 关键字段 |
|---|---|
| `tool_registry_versions` | `id`、`version`、`registry_json`、`created_at` |
| `tool_calls` | `tool_id`、`tool_version`、`adapter_version`、`input_json`、`params_json`、`status` |
| `artifacts` | `tool_call_id`、`type`、`version`、`storage_key`、`metadata_json` |
| `plugins` | `id`、`name`、`status`、`manifest_json` |
| `plugin_tools` | `plugin_id`、`tool_id`、`schema_json`、`status` |

## 18. 前端交互草案

- Agent Plan 显示 tool_id、purpose、key params。
- Tool detail 可查看输入要求、参数说明、输出格式。
- ToolCall 面板显示 cache hit/miss、runtime、artifact links。
- 失败工具显示重试按钮和错误解释。
- Expert/V1 模式允许从 Registry 中浏览工具并构造 Recipe。

## 19. 高并发、安全、扩展性考虑

### 高并发

- Tool execution 在 worker queue 中执行。
- 重工具按 costLevel 分队列或限流。
- 资源限制在执行前校验，执行时二次保护。
- 缓存命中直接返回 Artifact，不排队重算。

### 安全

- Tool Registry 是唯一执行白名单。
- Adapter 不接受任意文件路径。
- 插件默认无网络、无 Secret、无 shell。
- Artifact HTML 必须通过 sandboxed iframe 展示。
- 参数和输入引用进入审计日志，但不包含 Secret。

### 扩展性

- 支持新增材料领域插件。
- 支持未来自动生成部分 Schema。
- 支持按项目启用/禁用工具。
- 支持组织级工具版本锁定。

## 20. 本阶段产出的目标文件

```text
docs/06_TOOL_REGISTRY_AND_ADAPTER.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/TOOL_REGISTRY_NOTES.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 21. 下一阶段任务

Phase 7：数据解析与 Data Profile 设计。

需要定义：

- 文件解析流程。
- 格式识别。
- Structure / Composition / DataFrame / phonon / trajectory 标准化。
- Data Profile JSON Schema。
- 数据质量检查。
- 异常结构检查。
