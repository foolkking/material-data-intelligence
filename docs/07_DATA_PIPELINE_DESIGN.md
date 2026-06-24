# Phase 7：数据解析与 Data Profile 设计

## 1. 本阶段目标

定义材料数据文件的上传后解析流程、格式识别、材料对象标准化、Data Profile JSON Schema、数据质量检查、结构异常检查和推荐任务生成。Phase 7 的目标是让系统在 Agent 规划前先用确定性程序理解数据，而不是让 LLM 直接猜测文件内容。

## 2. 本阶段解决的问题

### 数据管线定位

Data Pipeline 负责把用户上传的原始文件转成平台可识别、可查询、可分析、可复现的标准对象和 Data Profile。

```text
Raw File
  -> Format Detection
  -> Safe Parse
  -> Normalized Object
  -> Data Profile
  -> Quality Issues
  -> Recommended Tasks
  -> Agent Planning Context
```

### Phase 7 决策

| 问题 | 决策 |
|---|---|
| MVP 支持 phonon 数据吗 | 不作为 MVP 执行能力；保留识别和 profile 扩展点，V1 实现解析与图表。 |
| VASP / LAMMPS 支持阶段 | VASP 输出和 LAMMPS dump 推迟到 V2；MVP 只识别为 unsupported / future extension。 |
| 代表性 3D 结构如何选择 | MVP 采用规则采样：小/中/大原子数、不同化学体系、异常结构优先；聚类代表点推迟到 V1。 |
| composition clustering 默认 | MVP 不实现 composition clustering；V1 默认 Magpie + PCA baseline，UMAP 作为可选高级投影。 |
| Profile 是否可覆盖 | Data Profile 不覆盖历史版本；新解析生成新 profile version。 |

## 3. 设计原则

- 解析先于 Agent：Agent 只读取 Data Profile 和确认后的字段映射。
- 安全解析：限制文件大小、压缩包展开大小、路径穿越、解析超时。
- 原始数据只读：raw file 不修改，所有派生产物写 normalized object。
- 标准对象优先：Structure、Composition、DataFrame、Trajectory、Phonon 对象统一引用。
- Profile 可版本化：重新解析、字段映射修正和配置变化会产生新 profile version。
- 部分成功可用：批量文件中部分失败不阻止成功文件进入分析。
- Warning 可追踪：质量问题写入 profile 和 job_events。

## 4. 核心模块

| 模块 | 职责 |
|---|---|
| Format Detector | 基于扩展名、magic bytes、内容特征识别文件类型 |
| Archive Extractor | 安全解压 ZIP / tar.gz，限制层级、大小和路径 |
| Parser Registry | 将格式映射到解析器 |
| Structure Parser | CIF、POSCAR/CONTCAR、XYZ/EXTXYZ 到 Structure / Atoms，并记录周期性边界 |
| Table Parser | CSV 到 DataFrame；Excel / Parquet 进入 V1 |
| JSON Parser | JSON limited 到 Structure / DataFrame / dict |
| Phonon Detector | phonopy.yaml / band.yaml / DOS 识别和未来解析扩展 |
| Object Normalizer | 统一转成平台 normalized object |
| Profile Builder | 生成 Data Profile |
| Quality Checker | 缺失、重复、短键、异常晶格、字段缺失等检查 |
| Task Recommender | 根据 profile 推荐 composition / structure / ml 等任务 |

## 5. 文件类型与解析策略

| 类型 | MVP 行为 | 标准对象 |
|---|---|---|
| CIF | 解析 | `Structure[]` |
| POSCAR / CONTCAR | 解析 | `Structure[]` |
| XYZ | MVP 基础支持：解析为 `Atoms` / molecule-like object；无 lattice 时不进入周期结构工具 | `Atoms[]` |
| EXTXYZ | MVP 基础支持：若包含 `Lattice=` 可转为周期 `Structure`；若含 energy / forces 可进入 trajectory-like profile；完整轨迹工具 V1 | `Atoms[]` / `Structure[]` |
| CSV | 解析 | `DataFrame` |
| JSON limited | 仅识别 pymatgen Structure JSON、Materials Project-like structure dict、simple table JSON；任意嵌套业务 JSON 进入 V1/自定义 parser | `Structure` / `DataFrame` / `dict` |
| ZIP | MVP 容器格式：安全解压并递归识别，内部只处理 MVP 支持的文件 | mixed dataset |
| Excel / Parquet | V1 | `DataFrame` |
| ASE trajectory | V1 | `Trajectory` |
| phonopy.yaml / band.yaml / DOS | V1 | `PhononBand` / `PhononDos` |
| VASP 输出 | V2 | future |
| LAMMPS dump | V2 | future |

## 6. 格式识别

识别顺序：

```text
file extension
  -> magic bytes / MIME
  -> content sniffing
  -> parser trial in safe mode
  -> unknown / unsupported
```

内容特征示例：

| 格式 | 特征 |
|---|---|
| CIF | `_cell_length_a`、`loop_`、`_atom_site_` |
| POSCAR | 第 2 行 scale、晶格矩阵、元素/数量行 |
| XYZ | 第一行为整数 atom count |
| EXTXYZ | XYZ comment 包含 `Lattice=` 或 properties |
| CSV | delimiter、header、consistent rows |
| phonopy.yaml | `phonopy`、`phonon`、`nqpoint` 等 yaml keys |

## 7. 标准化对象

```ts
type NormalizedObject = {
  id: string;
  datasetId: string;
  objectType:
    | "Structure"
    | "Composition"
    | "Atoms"
    | "Molecule"
    | "DataFrame"
    | "Trajectory"
    | "PhononBand"
    | "PhononDos"
    | "RawUnsupported";
  sourceFileIds: string[];
  storageKey: string;
  metadata: Record<string, unknown>;
  hash: string;
};
```

标准化策略：

- `pymatgen.Structure` 是周期结构的优先内部表示。
- `ASE Atoms` 可保留原始对象信息；plain XYZ 无 lattice 时不能被隐式当作周期晶体结构。
- EXTXYZ 包含 `Lattice=` 时可转为周期 `Structure`；包含 energy / forces 时记录 frame/property metadata，完整 trajectory 执行工具进入 V1。
- `pandas.DataFrame` 使用 Arrow/Parquet 或 pickle-free 安全格式保存派生产物。
- `Composition` 从 formula、Structure 或表格列派生。
- phonon / trajectory object type 保留扩展点。

## 8. Data Profile JSON Schema

```ts
type DataProfile = {
  schemaVersion: "0.1";
  profileId: string;
  datasetId: string;
  version: string;
  datasetType:
    | "structure_collection"
    | "ml_results"
    | "mixed_material_dataset"
    | "trajectory"
    | "phonon"
    | "unknown";
  files: FileProfile[];
  objects: ObjectProfile[];
  structureSummary?: StructureSummary;
  tableSummary?: TableSummary;
  phononSummary?: Record<string, unknown>;
  trajectorySummary?: Record<string, unknown>;
  qualityIssues: QualityIssue[];
  recommendedTasks: RecommendedTask[];
  createdAt: string;
};

type FileProfile = {
  fileId: string;
  fileName: string;
  detectedFormat: string;
  parseStatus: "success" | "partial" | "failed" | "unsupported";
  errorCode?: string;
  errorMessage?: string;
};

type ObjectProfile = {
  objectId: string;
  objectType: MaterialObjectType;
  count: number;
  sourceFileIds: string[];
  periodicity?: "periodic" | "non_periodic" | "mixed" | "unknown";
};
```

### StructureSummary

```ts
type StructureSummary = {
  nStructures: number;
  formulaStats: {
    total: number;
    uniqueCount: number;
    topFormulas: Array<{ formula: string; count: number }>;
    formulasObjectRef?: string;
  };
  elements: string[];
  chemicalSystemStats: {
    uniqueCount: number;
    topChemicalSystems: Array<{ chemSys: string; count: number }>;
  };
  atomCountStats: { min: number; median: number; max: number };
  latticeStats?: Record<string, { min: number; median: number; max: number }>;
  spacegroupDistribution?: Record<string, number>;
  hasForces: boolean;
  hasMagmoms: boolean;
  representativeStructureIds: string[];
};
```

Data Profile 只保存轻量摘要。完整公式列表、结构集合、表格全量数据进入 normalized object / object storage，前端需要时分页加载或按对象引用读取。

### TableSummary

```ts
type TableSummary = {
  nRows: number;
  nColumns: number;
  columns: Array<{
    name: string;
    dtype: "string" | "number" | "boolean" | "category" | "datetime" | "unknown";
    inferredRole?: FieldRole;
    missingCount: number;
    uniqueCount?: number;
  }>;
  inferredTask?: "regression" | "classification" | "unknown";
};
```

### RecommendedTask

```ts
type RecommendedTask = {
  taskId: string;
  label: string;
  stage: "mvp" | "v1" | "v2";
  taskType:
    | "composition_overview"
    | "structure_quality"
    | "ml_evaluation"
    | "phonon_analysis"
    | "trajectory_viewer"
    | "domain_extension";
  availableNow: boolean;
  requiredTools: string[];
  reason: string;
};
```

## 9. 数据质量检查

| 检查 | 数据类型 | 输出 |
|---|---|---|
| parse failures | all | failed file list |
| missing values | table | column missing counts |
| duplicate rows | table | duplicate count |
| formula parse failure | table/composition | invalid formula list |
| target/prediction missing | ml table | field mapping warning |
| abnormal atom count | structure | warning |
| short bonds | structure | warning/error |
| abnormal volume per atom | structure | warning |
| missing lattice | structure | unsupported or molecule warning |
| unknown elements | composition/structure | error |

QualityIssue：

```ts
type QualityIssue = {
  severity: "info" | "warning" | "error";
  code: string;
  message: string;
  refs: Array<{ type: "file" | "object" | "row" | "column" | "artifact"; id: string }>;
};
```

## 10. 异常结构检查

MVP 检查：

- 原子数为 0 或过大。
- 晶格体积异常。
- 最短原子距离低于元素无关安全阈值。
- 重复位点。
- 结构解析失败。
- 非周期对象用于周期结构工具时 warning。

V1 检查：

- 元素对 covalent/ionic 半径短键阈值。
- CrystalNN 配位异常。
- 氧化态和电荷平衡。
- symmetry consistency。
- RDF/XRD 指纹异常。

## 11. 代表结构选择

MVP 使用规则采样：

1. 每个主要 chemical system 至少一个。
2. 小/中/大 atom count 各选代表。
3. 含 warning 的异常结构优先加入。
4. 总数默认 3-8 个，受项目配置限制。

V1 使用组成 embedding / 聚类选择代表点。

## 12. 推荐任务生成

| Profile 条件 | 推荐任务 | Stage | MVP 行为 |
|---|---|---|---|
| formulas / Composition 可用 | composition overview | MVP | 可自动规划 |
| Structure[] 可用 | structure quality / 3D viewer | MVP | 可自动规划 |
| Structure[] + enough count | spacegroup distribution | MVP/V1 | MVP 从 Data Profile 展示；V1 可升级为工具 |
| DataFrame 含 target/prediction | ml evaluation | MVP | 可自动规划 |
| DataFrame 含 uncertainty | uncertainty calibration | V1 | MVP 中只显示为后续能力，不自动规划 |
| phonon object available | phonon band/DOS | V1 | MVP 中提示“已识别，V1 支持” |
| trajectory available | trajectory viewer | V1 | MVP 中只展示首末帧/抽样帧 |

推荐任务只作为 Agent planning context，不自动执行。MVP Planner 只能选择 `availableNow = true` 的任务；V1/V2 任务可在 UI 中显示为 planned capability，并用 `reason` 说明当前不可运行原因。

示例：

```json
{
  "taskId": "structure.spacegroup_distribution",
  "label": "Space group distribution",
  "stage": "v1",
  "taskType": "structure_quality",
  "availableNow": false,
  "requiredTools": ["structure.spacegroup_bar"],
  "reason": "Structure[] is available, but spacegroup visualization is planned for V1."
}
```

## 13. 数据流 / 控制流

```text
Upload complete
  -> parse job queued
  -> archive extraction
  -> format detection
  -> parser registry
  -> normalized object storage
  -> profile builder
  -> quality checker
  -> task recommender
  -> profile.ready event
```

## 14. API / Schema 草案

```http
POST /datasets/{dataset_id}/parse-jobs
GET /datasets/{dataset_id}/profile
GET /datasets/{dataset_id}/quality-issues
GET /datasets/{dataset_id}/normalized-objects
PATCH /datasets/{dataset_id}/field-mappings
POST /datasets/{dataset_id}/profiles/{profile_id}/rebuild
```

## 15. 数据库表草案

| 表 | 关键字段 |
|---|---|
| `files` | `detected_format`、`parse_status`、`sha256`、`size_bytes` |
| `normalized_objects` | `object_type`、`storage_key`、`metadata_json`、`hash` |
| `data_profiles` | `version`、`profile_json`、`n_valid`、`n_failed` |
| `field_mappings` | `mapping_json`、`confirmed_by`、`confirmed_at` |
| `quality_issues` | `dataset_id`、`profile_id`、`severity`、`code`、`refs_json` |

## 16. 前端交互草案

- 上传后左侧面板显示 profiling skeleton。
- 解析完成后显示 Profile Summary。
- 部分失败时显示 failed files，但成功对象可继续分析。
- 字段映射需要用户确认或使用系统推断。
- Quality Issues 可点击定位文件、结构或表格列。
- Recommended Tasks 可一键填入 Agent prompt。

## 17. 高并发、安全、扩展性考虑

### 高并发

- 解析任务按文件拆分，可批量并行。
- 大 ZIP 先建立 manifest，再逐个解析。
- Profile Builder 汇总 normalized object metadata。
- 解析结果按 file hash 和 parser version 缓存。

### 安全

- 限制压缩包层级、展开大小、文件数量。
- 防止 zip slip / path traversal。
- 禁止解析器访问任意外部路径。
- 解析超时和内存限制。
- 原始文件只读，派生产物单独写入。

### 扩展性

- Parser Registry 支持新增 VASP、LAMMPS、phonopy、trajectory parser。
- Data Profile schema versioned。
- Field mapping 可随项目配置学习默认列名。
- V1 可加入更强材料异常检测。

## 18. 本阶段产出的目标文件

```text
docs/07_DATA_PIPELINE_DESIGN.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 19. 下一阶段任务

Phase 8：高并发任务系统与流畅展示设计。

需要定义：

- Job Queue。
- Worker Pool。
- WebSocket / SSE。
- 任务事件流。
- 缓存。
- 大数据降采样。
- 3D LOD。
- 资源限制。
- 多用户并发。
- 可观测性。
