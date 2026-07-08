# pymatviz Capability Inventory

## 1. 项目与 pymatviz 的关系

本项目是材料数据智能分析与可视化平台，不是简单的 pymatviz Web UI，也不是让 LLM 直接写 Python 调用 pymatviz 的工具。

核心关系如下：

```text
pymatviz 是本项目的 primary visualization kernel。
pymatgen / ASE / phonopy 是 material object kernel。
Tool Registry + Adapter 是 LLM 可安全调用的能力抽象层。
Agent 只生成 JSON Plan，不直接执行任意 Python。
前端工作台负责展示 Plotly 图表、MatterViz 3D 模型、Artifact、Recipe、Report 和 Agent Timeline。
```

平台把 pymatviz 的原始函数、MatterViz widget、Plotly 自定义图和平台内置分析能力统一抽象成可注册、可校验、可审计、可复现的 `tool_id`。Agent 只能选择 Tool Registry 中存在且当前数据满足输入约束的工具。

## 2. pymatviz 能力分层

```text
Level 0：pymatviz 原始函数 / 类
Level 1：Capability Descriptor
Level 2：Platform Adapter
Level 3：Tool Registry tool_id
Level 4：Agent 可选择任务
Level 5：前端展示模块
```

示例：

```text
pmv.ptable_heatmap(...)
  -> Periodic Table Heatmap Capability
  -> PTableHeatmapAdapter
  -> composition.ptable_heatmap
  -> 元素分布 / 组成分析
  -> Composition Tab / Periodic Table Card
```

另一个示例：

```text
StructureWidget(...)
  -> Interactive Structure Viewer Capability
  -> StructureViewer3DAdapter
  -> structure.viewer_3d
  -> 代表性 3D 结构查看
  -> Structure Tab / 3D Viewer Card
```

## 3. pymatviz 能力分类

| 类别 | 适合材料数据 | 典型输入 | 输出 | 阶段 | Agent 是否可直接选择 | 预处理 | 缓存 / 降采样 / LOD |
|---|---|---|---|---|---|---|---|
| Periodic Table | 化学式、组成、元素属性、元素频次 | formula column、`Composition[]`、element-value map | 周期表 heatmap、hist、scatter、split heatmap | MVP / V1 | 是，需 Tool Registry 校验 | 元素解析、Composition 标准化、缺失元素处理 | 大表先聚合元素计数；缓存聚合结果和 Plotly JSON |
| Composition / Chemical System | 组成集合、化学体系分布、材料空间探索 | formula、`Composition[]`、`Structure[]`、composition features | chem system treemap、composition clustering 2D/3D | MVP / V1 | 是，聚类类工具 V1 | 化学体系归一化、feature extraction、可选 Magpie/PCA | 大集合抽样 / PCA baseline；缓存 feature matrix 和投影 |
| Structure 2D / 3D | 周期晶体结构、代表结构、结构异常样本 | `Structure`、`Structure[]`、周期 `Atoms` | Plotly 3D structure、2D projection、结构卡片 | MVP / V1 | 是，必须验证 periodicity 和 atom limit | pymatgen Structure 标准化、代表结构选择、可选 spacegroup | 大结构启用 LOD；缓存 structure JSON / figure JSON |
| MatterViz Widgets | 浏览器交互式结构、轨迹、材料 viewer | `Structure`、trajectory frames | MatterViz HTML、widget snapshot、viewer metadata | MVP / V1 | 是，Adapter 生成 sandboxed artifact | viewer state、结构 metadata、LOD 参数 | 大结构降级 bonds/cell/vector；trajectory 抽帧 |
| Phonon | phonopy / pymatgen 声子 band/DOS | `PhononBand`、`PhononDos`、phonopy.yaml、band.yaml | phonon band、DOS、band+DOS | V1 | 是，MVP 只推荐为后续能力 | phonopy 解析、路径和单位标准化 | 缓存解析对象和 Plotly JSON |
| RDF / XRD / Local Environment | 周期结构集合、局部环境、晶体衍射 | periodic `Structure[]` | RDF、XRD pattern、coordination hist、chem env sunburst | MVP / V1 / V2 | coordination MVP；RDF/XRD V1 | 周期性校验、neighbor strategy、局部环境计算 | 大集合抽样；缓存邻居图和衍射结果 |
| ML Evaluation / Regression / Classification | 预测结果 CSV、目标值、预测值、不确定性、标签 | `DataFrame` with target/prediction/label | density scatter、error distribution、metrics、outlier table、parity、calibration、confusion matrix | MVP / V1 | 是，字段映射必须确认 | numeric field validation、error column、outlier ranking | 大表降采样 / binning；metrics 和 top-k 表缓存 |
| General Plotly Utilities | 平台自定义统计图、表格派生图、报告图 | `DataFrame`、arrays、aggregations | Plotly JSON/HTML/PNG | MVP / V1 | 是，作为 platform_builtin 或 plotly_custom | 数据聚合、schema 校验 | 大数据预聚合；HTML/PNG 按需渲染 |
| Export / Widget Rendering | Artifact 导出、HTML 渲染、截图、论文图 | Plotly Figure、MatterViz viewer、report | HTML、PNG preview、SVG/PDF、snapshot | MVP / V1 | 否，通常由 Adapter/Artifact Service 内部调用 | sandbox render、脱敏、权限检查 | PNG preview MVP；SVG/PDF 和稳定 snapshot V1 |

## 4. 原始 pymatviz 能力到平台 Tool ID 的映射表

| pymatviz source function/class | 平台 Tool ID | 阶段 | implementationSource | Adapter 名称 | 输入对象 | 输出 Artifact | displayTarget | Agent 可调用 | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| `ptable_heatmap` | `composition.ptable_heatmap` | MVP | `pymatviz` | `PTableHeatmapAdapter` | `Composition[]`、formula column、`ElementValueMap` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `composition` | 是 | 元素分布和元素属性热力图入口 |
| `elements_hist` | `composition.elements_hist` | MVP | `pymatviz` | `ElementsHistAdapter` | `Composition[]`、formula column | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `composition` | 是 | 结构集合和表格组成数据的元素频次 |
| `chem_sys_treemap` | `composition.chem_sys_treemap` | MVP | `pymatviz` | `ChemSysTreemapAdapter` | `Composition[]`、`Structure[]`、formula column | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `composition` | 是 | 化学体系分布 |
| `structure_3d` | `structure.structure_3d` | MVP | `pymatviz` | `Structure3DAdapter` | periodic `Structure` / `Structure[]` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `structure` | 是 | Plotly 3D 结构图；大结构启用 LOD |
| `StructureWidget` / MatterViz | `structure.viewer_3d` | MVP | `matterviz` | `StructureViewer3DAdapter` | `Structure` | `matterviz_html`、`structure_json`、`summary_md`、`recipe_json`，可选 `matterviz_snapshot_png` | `structure` | 是 | MatterViz 交互式 3D viewer |
| deterministic coordination histogram | `structure.coordination_hist` | MVP | `pymatviz_composed` | `CoordinationHistAdapter` | periodic `Structure[]` | `table_json`、`plotly_json`、`summary_md`、`recipe_json` | `structure` | 是 | Phase 10E-1 static coordination-number histogram; no advanced local-environment classification |
| `density_scatter` | `ml.density_scatter` | MVP | `pymatviz` | `DensityScatterAdapter` | `DataFrame` target/prediction | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `ml` | 是 | 回归预测结果可视化 |
| platform error histogram | `ml.error_distribution` | MVP | `plotly_custom` | `ErrorDistributionAdapter` | `DataFrame` target/prediction | `plotly_json`、`plotly_html`、`preview_png`、`metrics_json`、`table_json`、`summary_md`、`recipe_json` | `ml` | 是 | 可由 Plotly 自定义实现，不要求 pymatviz 原生函数 |
| platform metrics | `ml.basic_metrics` | MVP | `platform_builtin` | `BasicMetricsAdapter` | `DataFrame` target/prediction | `metrics_json`、`summary_md`、`recipe_json` | `ml` | 是 | MAE/RMSE/R2 等结构化指标 |
| platform outlier ranking | `ml.outlier_table` | MVP | `platform_builtin` | `OutlierTableAdapter` | `DataFrame` target/prediction | `table_json`、`table_csv`、`summary_md`、`recipe_json` | `ml` | 是 | Top-K 误差样本和下载表 |
| `ptable_hists` | `composition.ptable_hists` | V1 | `pymatviz` | `PTableHistsAdapter` | `DataFrame` / element distributions | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `composition` | 是 | 多元素直方图矩阵 |
| `ptable_scatter` | `composition.ptable_scatter` | V1 | `pymatviz` | `PTableScatterAdapter` | element-value pairs | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `composition` | 是 | 元素属性散点 |
| `ptable_heatmap_splits` | `composition.ptable_heatmap_splits` | V1 | `pymatviz` | `PTableHeatmapSplitsAdapter` | multiple element-value maps | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `composition` | 是 | 多指标周期表切片 |
| `cluster_compositions` | `composition.cluster_2d` / `composition.cluster_3d` | V1 | `pymatviz_composed` | `CompositionClusterAdapter` | `Composition[]`、formula column、properties | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `composition` | 是 | 默认 Magpie + PCA baseline，UMAP 可选 |
| `structure_2d` | `structure.structure_2d` | V1 | `pymatviz` | `Structure2DAdapter` | periodic `Structure` | `plotly_json` / image artifact、`summary_md`、`recipe_json` | `structure` | 是 | 论文式结构投影图 |
| `TrajectoryWidget` | `trajectory.viewer` | V1 | `matterviz` | `TrajectoryViewerAdapter` | `Trajectory`、sampled frames | `matterviz_html`、`summary_md`、`recipe_json` | `trajectory` | 是 | trajectory 深度支持进入 V1 |
| `phonon_bands` | `phonon.band` | V1 | `pymatviz` | `PhononBandAdapter` | `PhononBand` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `phonon` | 是 | V1 优先 phonopy.yaml + band.yaml |
| `phonon_dos` | `phonon.dos` | V1 | `pymatviz` | `PhononDosAdapter` | `PhononDos` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `phonon` | 是 | DOS 第二批接入 |
| `phonon_bands_and_dos` | `phonon.band_dos` | V1 | `pymatviz` | `PhononBandDosAdapter` | `PhononBand` + `PhononDos` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `phonon` | 是 | 组合视图 |
| `xrd_pattern` | `structure.xrd` | V1 | `pymatviz` | `XrdPatternAdapter` | periodic `Structure` / `Structure[]` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `structure` | 是 | 必须 periodic_required |
| `element_pair_rdfs` / `full_rdf` | `structure.rdf` | V1 | `pymatviz` | `RdfAdapter` | periodic `Structure[]` | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `structure` | 是 | 大集合抽样，缓存 RDF bins |
| `chem_env_sunburst` | `structure.chem_env_sunburst` | V2 | `pymatviz` | `ChemEnvSunburstAdapter` | periodic `Structure[]` + local env | `plotly_json`、`plotly_html`、`preview_png`、`summary_md`、`recipe_json` | `structure` | 是，默认 V2 | late V1 exploratory；default V2，依赖局部环境分析质量 |

## 5. Capability 标准描述格式

```yaml
capability_id:
source:
  package:
  module:
  function_or_class:
platform:
  tool_id:
  adapter:
  implementation_source:
  stage:
inputs:
  accepted_objects:
  accepted_fields:
  file_sources:
params:
  allowed_agent_params:
  system_fixed_params:
  default_params:
outputs:
  artifact_types:
  display_target:
runtime:
  estimated_cost:
  cache_policy:
  timeout_sec:
  concurrency_class:
safety:
  agent_callable:
  requires_validation:
  notes:
```

### 5.1 `composition.ptable_heatmap`

```yaml
capability_id: periodic_table_heatmap
source:
  package: pymatviz
  module: pymatviz
  function_or_class: ptable_heatmap
platform:
  tool_id: composition.ptable_heatmap
  adapter: PTableHeatmapAdapter
  implementation_source: pymatviz
  stage: mvp
inputs:
  accepted_objects:
    - Composition
    - ElementValueMap
    - DataFrame
  accepted_fields:
    - formula
  file_sources:
    - CIF
    - POSCAR/CONTCAR
    - CSV
    - JSON limited
    - ZIP container
params:
  allowed_agent_params:
    - countMode
    - colorScale
    - normalize
    - title
  system_fixed_params:
    - sanitize_formula=true
    - max_elements=118
  default_params:
    countMode: occurrence
    colorScale: Viridis
    normalize: false
outputs:
  artifact_types:
    - plotly_json
    - plotly_html
    - preview_png
    - summary_md
    - recipe_json
  display_target: composition
runtime:
  estimated_cost: low
  cache_policy: reuse
  timeout_sec: 30
  concurrency_class: viz-light
safety:
  agent_callable: true
  requires_validation:
    - input_refs_exist
    - formulas_parseable
    - params_schema_valid
  notes: Agent 只能选择 count/normalize/style 等平台批准参数，不能传任意 pymatviz kwargs。
```

### 5.2 `structure.structure_3d`

```yaml
capability_id: plotly_structure_3d
source:
  package: pymatviz
  module: pymatviz
  function_or_class: structure_3d
platform:
  tool_id: structure.structure_3d
  adapter: Structure3DAdapter
  implementation_source: pymatviz
  stage: mvp
inputs:
  accepted_objects:
    - Structure
  accepted_fields:
    - structure_id
  file_sources:
    - CIF
    - POSCAR/CONTCAR
    - pymatgen Structure JSON
    - EXTXYZ with lattice
params:
  allowed_agent_params:
    - colorBy
    - showCell
    - showBonds
    - selectedStructureIds
    - maxStructures
  system_fixed_params:
    - periodicity=periodic_required
    - max_atoms_per_structure
    - lod_policy
  default_params:
    colorBy: element
    showCell: true
    showBonds: auto
    maxStructures: 4
outputs:
  artifact_types:
    - plotly_json
    - plotly_html
    - preview_png
    - summary_md
    - recipe_json
  display_target: structure
runtime:
  estimated_cost: medium
  cache_policy: reuse
  timeout_sec: 60
  concurrency_class: viz-3d
safety:
  agent_callable: true
  requires_validation:
    - structure_object_exists
    - periodicity_valid
    - atom_limit_valid
    - representative_selection_valid
  notes: plain XYZ 不允许进入该工具；无 lattice 的 Atoms 只能进入非周期 preview 或 composition 工具。
```

### 5.3 `structure.viewer_3d`

```yaml
capability_id: matterviz_structure_viewer
source:
  package: pymatviz
  module: pymatviz widgets / MatterViz
  function_or_class: StructureWidget
platform:
  tool_id: structure.viewer_3d
  adapter: StructureViewer3DAdapter
  implementation_source: matterviz
  stage: mvp
inputs:
  accepted_objects:
    - Structure
  accepted_fields:
    - structure_id
  file_sources:
    - CIF
    - POSCAR/CONTCAR
    - pymatgen Structure JSON
    - EXTXYZ with lattice
params:
  allowed_agent_params:
    - selectedStructureId
    - showCell
    - showBonds
    - cameraPreset
  system_fixed_params:
    - sandboxed_iframe=true
    - max_atoms_per_structure
    - lod_policy
  default_params:
    showCell: true
    showBonds: auto
    cameraPreset: auto
outputs:
  artifact_types:
    - matterviz_html
    - structure_json
    - summary_md
    - recipe_json
  optional_artifact_types:
    - matterviz_snapshot_png
  display_target: structure
runtime:
  estimated_cost: medium
  cache_policy: reuse
  timeout_sec: 90
  concurrency_class: render-3d
safety:
  agent_callable: true
  requires_validation:
    - structure_object_exists
    - atom_limit_valid
    - artifact_html_sandboxed
  notes: MVP 不强制 snapshot；稳定截图、多角度导出和论文风格结构图进入 V1。
```

## 6. 实现前锁定事项

- `tool_registry/pymatviz_manifest.yaml` 是 pymatviz 原生 Plotly 能力的初始注册来源。
- `tool_registry/matterviz_manifest.yaml` 是 MatterViz / widget 能力的初始注册来源。
- `tool_registry/platform_builtin_manifest.yaml` 是平台内置分析与自定义 Plotly 能力的初始注册来源。
- 正式代码中的 `RegisteredTool`、`ArtifactType`、`DisplayTarget`、`ImplementationSource` 必须以 `docs/13_SHARED_SCHEMA_SPEC.md` 为准。
- 实现阶段需要在依赖锁定时再次核对 pymatviz 具体版本和函数签名，并把版本写入 Artifact provenance。
