# Adapter Implementation Plan

## 1. Adapter 实现原则

Adapter 是本平台把自然语言分析计划转换为真实材料可视化执行的唯一受控入口。

实现原则：

- 不要修改 pymatviz 源码。
- 不要让 LLM 直接调用 pymatviz。
- 不要让 LLM 直接执行任意 Python。
- Adapter 是唯一允许把 ToolCall 转换为真实函数调用的地方。
- 所有 Adapter 必须经过输入解析、参数校验、执行、Artifact 导出、错误标准化。
- Adapter 只能接受 `ToolExecutionRequest` 中的 `inputRefs`、`params` 和 `artifactTypes`，不能接受任意文件路径或未注册工具名。
- Adapter 必须把 `toolId`、`toolVersion`、`adapterVersion`、输入 hash、参数 hash 和依赖版本写入 Artifact metadata / provenance。

## 2. BaseToolAdapter 接口

```python
class BaseToolAdapter:
    tool_id: str

    def prepare(self, context, input_refs, params):
        """Resolve dataset references and validate input objects."""

    def run(self, prepared, params):
        """Call pymatviz / MatterViz / Plotly / platform builtin logic."""

    def export(self, result, artifact_types):
        """Export standardized artifacts and metadata."""
```

建议实现时把 `context` 设计为只读执行上下文，至少包含：

```python
class ToolExecutionContext:
    job_id: str
    project_id: str
    dataset_id: str
    tool_id: str
    tool_version: str
    adapter_version: str
    registry_version: str
    object_store: object
    artifact_service: object
    logger: object
    resource_limits: dict
```

## 3. Adapter 执行流程

```text
ToolExecutionRequest
  -> Tool Registry lookup
  -> Input Resolver
  -> Param Validator
  -> Cache lookup
  -> Adapter.prepare()
  -> Adapter.run()
  -> Adapter.export()
  -> Artifact Service
  -> ToolCall status update
  -> JobEvent artifact.ready
```

失败路径：

```text
Adapter.prepare()/run()/export() error
  -> Error Normalizer
  -> ToolCall status=failed
  -> JobEvent status=error
  -> optional retry policy
```

## 4. MVP Adapter 实现顺序

1. `composition.ptable_heatmap`
2. `structure.structure_3d`
3. `structure.viewer_3d`
4. `composition.elements_hist`
5. `composition.chem_sys_treemap`
6. `structure.coordination_hist`
7. `ml.density_scatter`
8. `ml.error_distribution`
9. `ml.basic_metrics`
10. `ml.outlier_table`

理由：

- 先实现 pymatviz 原生 Plotly 工具。
- 再实现 MatterViz 3D 工具。
- 再实现平台内置 ML 分析工具。
- 最后补齐完整 MVP 端到端链路。

实际开发可采用两段式验收：

- 第一段：`ptable_heatmap`、`structure_3d`、`viewer_3d` 跑通 Tool Registry -> Adapter -> Artifact。
- 第二段：补齐 10 个 MVP 工具，并完成 composition、structure、ml 三类端到端 demo。

## 5. 每个 Adapter 的测试要求

### 单元测试

每个 Adapter 至少覆盖：

- 输入解析正确。
- 参数校验正确。
- 错误输入能标准化报错。
- 输出 `artifact_types` 符合 manifest。
- 不接受任意本地路径、未注册参数或 Secret 字段。
- 大数据 / 大结构触发 resource limit 或 LOD 策略。

### 集成测试

每个 MVP Adapter 至少覆盖：

- 使用最小 CIF / POSCAR / CSV fixture。
- 能生成标准 Artifact。
- 能写入 ToolCall 和 JobEvent。
- Artifact metadata 包含工具版本、Adapter 版本、输入 hash、参数 hash 和依赖版本。
- 失败时写入标准 `ToolError`，普通用户日志不暴露内部路径或完整堆栈。

### Smoke test

依赖版本升级后必须运行：

```text
load manifests
  -> validate every tool against shared schema
  -> instantiate adapter class
  -> execute minimal fixture
  -> export canonical artifacts
```

## 6. MVP Adapter 输入与输出摘要

| Tool ID | implementationSource | Adapter | 输入 | 必需 Artifact |
|---|---|---|---|---|
| `composition.ptable_heatmap` | `pymatviz` | `PTableHeatmapAdapter` | formula / `Composition[]` / `ElementValueMap` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` |
| `structure.structure_3d` | `pymatviz` | `Structure3DAdapter` | periodic `Structure` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` |
| `structure.viewer_3d` | `matterviz` | `StructureViewer3DAdapter` | `Structure` | `matterviz_html`、`structure_json`、`summary_md`、`recipe_json` |
| `composition.elements_hist` | `pymatviz` | `ElementsHistAdapter` | formula / `Composition[]` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` |
| `composition.chem_sys_treemap` | `pymatviz` | `ChemSysTreemapAdapter` | formula / `Composition[]` / `Structure[]` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` |
| `structure.coordination_hist` | `pymatviz_composed` | `CoordinationHistAdapter` | periodic `Structure[]` | `table_json`、`plotly_json`、`summary_md`、`recipe_json` |
| `ml.density_scatter` | `pymatviz` | `DensityScatterAdapter` | DataFrame target/prediction | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` |
| `ml.error_distribution` | `plotly_custom` | `ErrorDistributionAdapter` | DataFrame target/prediction | `plotly_json`、`plotly_html`、`preview_png`、`metrics_json`、`table_json`、`summary_md`、`recipe_json` |
| `ml.basic_metrics` | `platform_builtin` | `BasicMetricsAdapter` | DataFrame target/prediction | `metrics_json`、`summary_md`、`recipe_json` |
| `ml.outlier_table` | `platform_builtin` | `OutlierTableAdapter` | DataFrame target/prediction | `table_json`、`table_csv`、`summary_md`、`recipe_json` |

## 7. Adapter 目录建议

```text
workers/
  tool_adapters/
    base.py
    registry_loader.py
    input_resolver.py
    param_validator.py
    artifact_exporter.py
    pymatviz/
      ptable_heatmap.py
      elements_hist.py
      chem_sys_treemap.py
      structure_3d.py
      coordination_hist.py
      density_scatter.py
    matterviz/
      structure_viewer_3d.py
    platform_builtin/
      error_distribution.py
      basic_metrics.py
      outlier_table.py
```

正式代码结构可随 monorepo 实现调整，但 manifest loader、BaseToolAdapter、Input Resolver、Artifact Exporter 和 Error Normalizer 必须保持独立边界。

## 8. 与共享 Schema 的关系

- `ToolExecutionRequest`、`ArtifactType`、`DisplayTarget`、`ImplementationSource`、`InputRef` 以 `docs/13_SHARED_SCHEMA_SPEC.md` 为准。
- manifest 中的 `artifact_types` 在加载后映射为 `RegisteredTool.artifactTypes`。
- manifest 中的 `implementation_source` 在加载后映射为 `RegisteredTool.implementationSource`。
- Adapter 测试必须验证 manifest 字段可转换为共享 Schema 字段。
