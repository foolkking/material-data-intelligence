# TOOL_REGISTRY_NOTES

## External Capability Baseline

官方来源核对基线：

- pymatviz：materials informatics visualization toolkit；当前规划基线按 `0.18.x`、Python `>=3.11` 处理，正式实现前需要再次锁版本。
- pymatviz 输出以 Plotly Figure、HTML、图片、widget/export 为核心。
- MatterViz / anywidget 路线用于更接近浏览器原生的 3D 结构、轨迹和交互材料 UI。
- 平台不直接暴露 pymatviz 原始函数给 Agent；必须通过 Tool Registry + Adapter。
- `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md` 是 pymatviz 原始能力到平台 Tool ID 的能力清单。
- `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md` 是 Adapter 实现顺序、接口和测试要求基线。

## Manifest-based Registry Baseline

正式实现时，Tool Registry 的首批工具来源为：

| Manifest | 作用 |
|---|---|
| `tool_registry/pymatviz_manifest.yaml` | pymatviz 原生 Plotly 能力，例如 `ptable_heatmap`、`structure_3d`、`coordination_hist`、`density_scatter` |
| `tool_registry/matterviz_manifest.yaml` | MatterViz / widget 能力，例如 `StructureWidget` 和 `TrajectoryWidget` |
| `tool_registry/platform_builtin_manifest.yaml` | 平台内置分析和自定义 Plotly 能力，例如 `basic_metrics`、`outlier_table`、`error_distribution` |

每个 manifest tool entry 必须能映射到共享 Schema 中的 `RegisteredTool`，并保留：

- `tool_id`
- `implementation_source`
- `adapter`
- `display_target`
- `artifact_types`
- `stage`
- source package / source function / source class，如适用

`stage` 必须使用共享 Schema 允许的值：`mvp`、`v1`、`v2`。跨阶段探索能力不得写成组合枚举；例如 `structure.chem_env_sunburst` 默认登记为 `v2`，late V1 exploratory 只写入 `notes`。

## MVP Tool Source Split

| MVP Tool ID | Source |
|---|---|
| `composition.ptable_heatmap` | pymatviz `ptable_heatmap` |
| `composition.elements_hist` | pymatviz `elements_hist` |
| `composition.chem_sys_treemap` | pymatviz `chem_sys_treemap` |
| `structure.structure_3d` | pymatviz `structure_3d` |
| `structure.viewer_3d` | MatterViz / pymatviz `StructureWidget` |
| `structure.coordination_hist` | pymatviz `coordination_hist` |
| `ml.density_scatter` | pymatviz `density_scatter` |
| `ml.error_distribution` | platform `plotly_custom` |
| `ml.basic_metrics` | platform builtin |
| `ml.outlier_table` | platform builtin |

## Initial Categories

### composition

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `composition.cluster_2d`
- `composition.cluster_3d`

### structure

- `structure.viewer_3d`
- `structure.structure_3d`
- `structure.rdf`
- `structure.xrd`
- `structure.coordination_hist`
- `structure.spacegroup_bar`

### trajectory

- `trajectory.viewer`
- `trajectory.energy_curve`
- `trajectory.force_curve`

### phonon

- `phonon.band`
- `phonon.dos`
- `phonon.band_dos`

### ml

- `ml.parity_plot`
- `ml.density_scatter`
- `ml.error_distribution`
- `ml.basic_metrics`
- `ml.outlier_table`
- `ml.uncertainty_calibration`
- `ml.confusion_matrix`
- `ml.error_by_element`
- `ml.error_by_chem_sys`

## Accepted Data Forms

| 数据类别 | 典型 Python 形式 | 平台标准化目标 |
|---|---|---|
| 化学式 / 组成 | string formula、`pymatgen.Composition` | `Composition[]`、formula column |
| 晶体结构 | `pymatgen.Structure`、`IStructure`、`ASE Atoms`、`PhonopyAtoms` | `Structure[]` + structure metadata |
| 结构文件 | CIF、POSCAR、CONTCAR、JSON limited | parsed structure collection |
| 表格数据 | `pandas.DataFrame` | typed dataframe + inferred field roles |
| 数值数组 | numpy/list/Series | metric arrays or chart series |
| 声子数据 | pymatgen / phonopy band、DOS objects | phonon band/DOS profile |
| 轨迹数据 | ASE traj、EXTXYZ、pymatgen trajectory JSON、XDATCAR | trajectory frames + per-frame properties |
| 模型结果 | `y_true`、`y_pred`、`y_std`、labels、probabilities | ML evaluation dataset |

## Data to Visualization Mapping

| 输入 | Tool IDs | 产物 |
|---|---|---|
| 化学式列表 | `composition.ptable_heatmap`、`composition.elements_hist`、`composition.chem_sys_treemap` | 周期表热力图、元素直方图、化学体系 treemap |
| 化学式 + 性质 | `composition.cluster_2d`、`composition.cluster_3d` | 组成嵌入 2D/3D 聚类图 |
| Structure collection | `structure.structure_3d`、`structure.viewer_3d`、`structure.spacegroup_bar` | Plotly 3D、MatterViz 3D、空间群分布 |
| Structure + local geometry | `structure.rdf`、`structure.xrd`、`structure.coordination_hist` | RDF、XRD、配位数分布 |
| Structure + force/magmom | `structure.structure_3d`、`trajectory.viewer` | 带向量箭头结构图、轨迹/优化过程 |
| phonopy / pymatgen phonon | `phonon.band`、`phonon.dos`、`phonon.band_dos` | 声子能带、声子 DOS、组合图 |
| `y_true` / `y_pred` | MVP：`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`；V1：`ml.parity_plot` | density scatter、误差分布、指标、离群表 |
| `y_true` / `y_pred` / `y_std` | `ml.uncertainty_calibration` | 不确定性校准、error decay |
| 分类标签 | `ml.confusion_matrix` | 混淆矩阵、分类指标图 |

## MVP Tool Set

MVP 优先封装以下工具，保证“结构数据 + 预测结果表格”两条核心路径闭环：

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `structure.structure_3d`
- `structure.viewer_3d`
- `structure.coordination_hist`
- `ml.density_scatter`
- `ml.error_distribution`
- `ml.basic_metrics`
- `ml.outlier_table`

V1/V2 再扩展：

- `structure.rdf`
- `structure.xrd`
- `structure.spacegroup_bar`
- `composition.cluster_2d`
- `composition.cluster_3d`
- `ml.parity_plot`
- `phonon.band`
- `phonon.dos`
- `trajectory.viewer`
- `ml.uncertainty_calibration`
- `ml.error_by_element`
- `ml.error_by_chem_sys`

## 3D Rendering Routes

| 路线 | 适用场景 | 产物 |
|---|---|---|
| Plotly `structure_3d` | 快速结构图、图表卡片、HTML 交互图 | MVP：Plotly JSON、HTML、PNG preview；V1：SVG/PDF 论文图 |
| MatterViz `StructureWidget` | 浏览器结构查看、交互检查、材料 Viewer | viewer HTML、metadata、optional snapshot |
| MatterViz `TrajectoryWidget` | MD / relaxation 轨迹、帧属性曲线、force vectors | V1：trajectory HTML、optional snapshot、per-frame metadata |

所有 3D 工具必须支持结构大小分级策略：小结构完整显示，中结构默认减少 bonds，大结构启用 LOD / 抽样 / 手动展开，trajectory 默认抽帧。

## Tool Schema Draft

Phase 6 已将 Tool Schema 固化到 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`，共享枚举和跨模块类型收敛到 `docs/13_SHARED_SCHEMA_SPEC.md`。后续实现以这两个文档为准。

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
  inputSchema: ToolInputSchema; // uses inputOptions OR semantics
  paramsSchema: Record<string, unknown>;
  artifactTypes: ArtifactType[];
  costLevel: "low" | "medium" | "high";
  timeoutSec: number;
  cachePolicy: "reuse" | "refresh" | "no_cache";
};
```

## Artifact Requirements

每个工具输出不只保存最终图，还要保存复现与审计所需材料：

| Artifact | 说明 |
|---|---|
| `figure.json` | Plotly Figure JSON 或等价结构化图表描述 |
| `figure.html` | 可交互 HTML |
| `preview.png` | 卡片预览图 |
| `figure.svg` / `figure.pdf` | 论文/报告导出，V1 |
| `viewer.html` | MatterViz / 3D viewer HTML |
| `metadata.json` | MatterViz viewer 元数据 |
| `structure.json` | 标准化结构或结构引用 |
| `metrics.json` | MAE、RMSE、R2、error stats 等结构化指标 |
| `table.json` | outlier table、failed files、quality issues 等小表 |
| `table.csv` | 用户下载表格 |
| `quality_issues.json` | 解析失败、字段问题、结构质量问题 |
| `summary.md` | 图表解释、数据来源、关键参数 |
| `recipe.json` | 复现该工具调用的输入引用、参数、版本 |

## Agent Display Contract

前端展示的是结构化可审计过程，不展示 LLM 原始隐藏思维链：

```text
Data Detection -> Data Quality -> Plan Generated -> Tool Started -> Artifact Ready -> Result Explanation
```

每个 ToolCall 至少展示：

- 为什么选择该工具。
- 使用哪些输入数据。
- 关键参数是什么。
- 输出了哪些 Artifact。
- 是否命中缓存。
- 是否有 Warning / Error。

## Open Tool Design Issues

- V1 是否将 pymatviz 函数签名半自动转换为 Tool Schema？
- V1 phonon、trajectory 工具的首批 Tool ID 如何排序？
- V2 VASP、LAMMPS 工具的首批 Tool ID 如何排序？
- Expert 模式是否允许用户编辑 Recipe 和受限 Python 代码片段？
