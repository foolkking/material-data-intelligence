# 专业材料领域扩展设计

## 1. 本阶段目标

补齐材料领域长期扩展设计，明确结构、计算材料、声子/电子结构、材料机器学习、生成材料评估、外部生态集成和插件机制如何在现有 Data Pipeline、Tool Registry、Agent Plan、Artifact、Recipe 和安全边界内演进。

本文件是 Phase 0-10 设计的领域扩展补充文件，不改变 Phase 11 `docs/12_MVP_ROADMAP.md` 的开发计划编号。

## 2. 本阶段解决的问题

- 哪些材料专业能力属于 MVP、V1、V2。
- 新领域工具如何接入 Parser Registry、Object Normalizer 和 Tool Registry。
- 如何避免为了接入专业工具而让 LLM 获得任意代码执行能力。
- 如何让 Materials Project、OPTIMADE、AiiDA、atomate2、VASP、LAMMPS 等生态成为受控扩展，而不是破坏平台边界。

## 3. 设计原则

- 先标准化对象，再调用工具：所有扩展必须先进入 Structure、Composition、DataFrame、Phonon、Trajectory、ElectronicStructure 等标准对象或对象引用。
- 只扩展 Tool Registry，不绕过 Execution Controller。
- 专业工具默认异步执行，并保存 Artifact、Recipe、ToolCall 和审计日志。
- 插件默认最小权限：无网络、无 Secret、无 shell，除非 manifest 显式声明并被管理员启用。
- MVP 聚焦结构数据和预测结果表格闭环；高级材料工具按 V1/V2 分批接入。

## 4. 核心模块

| 模块 | 扩展职责 |
|---|---|
| Parser Registry | 新增 VASP、LAMMPS、phonopy、trajectory、external API payload parser |
| Object Normalizer | 将外部对象转为平台标准对象引用 |
| Data Profile Builder | 增加声子、轨迹、电子结构、计算输出和外部数据库画像 |
| Tool Registry | 注册专业材料工具、Schema、版本、权限、成本和 Artifact 类型 |
| Plugin Manager | 管理插件 manifest、启用范围、权限和版本 |
| Execution Controller | 校验领域工具调用、预算、资源、输入和 Secret 引用 |
| Artifact Service | 保存专业图表、viewer、计算摘要、报告和 Recipe |

## 5. 材料结构扩展

### 能力范围

| 能力 | 阶段 | 说明 |
|---|---|---|
| 元素分布、化学体系分布 | MVP | composition 工具核心闭环 |
| 代表性 3D 结构 | MVP | 规则采样，默认 3-8 个 |
| 空间群分布 | V1 | `structure.spacegroup_bar` |
| RDF / XRD | V1 | `structure.rdf`、`structure.xrd` |
| 结构聚类代表点 | V1 | composition/structure embedding |
| 缺陷、表面、晶界结构分析 | V2 | 专业插件接入 |

### 结构对象扩展 Schema 草案

```ts
type StructureExtensionProfile = {
  structureCount: number;
  formulaSystems: string[];
  spacegroupDistribution?: Record<string, number>;
  atomCountStats: { min: number; median: number; max: number };
  dimensionality?: Array<"0d" | "1d" | "2d" | "3d" | "unknown">;
  representativeStructureRefs: string[];
  qualityIssues: Array<{
    code: string;
    severity: "info" | "warning" | "error";
    structureRef?: string;
    message: string;
  }>;
};
```

## 6. 计算材料扩展

### VASP

VASP 输出推迟到 V2。优先解析顺序建议：

1. `vasprun.xml`：结构、能量、力、DOS、band、参数。
2. `OUTCAR`：补充收敛、磁矩、力、警告。
3. `XDATCAR`：结构轨迹。
4. `DOSCAR` / `EIGENVAL`：电子结构专门路径。

### LAMMPS

LAMMPS dump 推迟到 V2。优先支持：

- dump trajectory frames。
- per-atom property columns。
- thermo log。
- RDF / MSD / energy curve 等派生分析。

### 计算输出 Profile 草案

```ts
type SimulationProfile = {
  engine: "vasp" | "lammps" | "unknown";
  runType?: "static" | "relax" | "md" | "band" | "dos";
  structures?: string[];
  trajectoryRef?: string;
  energySeriesRef?: string;
  forceStats?: { maxForce?: number; rmsForce?: number };
  convergence?: { electronic?: boolean; ionic?: boolean };
  warnings: string[];
};
```

## 7. 声子与电子结构扩展

### Phonon

Phonon 工具进入 V1，MVP 只保留识别和 Schema 扩展点。

| Tool ID | 阶段 | 输入 | 输出 |
|---|---|---|---|
| `phonon.band` | V1 | `PhononBand` | Plotly JSON + 交互展示产物 + PNG preview |
| `phonon.dos` | V1 | `PhononDos` | Plotly JSON + 交互展示产物 + PNG preview |
| `phonon.band_dos` | V1 | `PhononBand` + `PhononDos` | combined figure |

### Electronic Structure

电子结构建议进入 V2，优先以 parser/plugin 接入：

- band structure。
- DOS / projected DOS。
- Fermi level、band gap、direct/indirect gap。
- orbital / element projected summaries。

## 8. 机器学习材料扩展

MVP 支持预测结果表格的基础误差分析；V1 扩展领域分组和不确定性：

| 能力 | 阶段 | Tool ID |
|---|---|---|
| density scatter | MVP | `ml.density_scatter` |
| error distribution | MVP | `ml.error_distribution` |
| parity plot | V1 | `ml.parity_plot` |
| uncertainty calibration | V1 | `ml.uncertainty_calibration` |
| error by element | V1 | `ml.error_by_element` |
| error by chemical system | V1 | `ml.error_by_chem_sys` |
| generated-material screening dashboard | V2 | plugin |

### 领域字段映射

```ts
type MaterialMlFieldRoles = {
  formula?: string;
  structureId?: string;
  target?: string;
  prediction?: string;
  uncertainty?: string;
  split?: string;
  modelId?: string;
  labels?: string[];
};
```

## 9. 生成材料评估扩展

生成材料评估进入 V2 或插件阶段。推荐能力：

- composition validity。
- structure validity。
- charge neutrality and oxidation-state checks。
- novelty / duplicate detection against project dataset。
- diversity over chemical systems。
- property target hit-rate。
- representative generated structures viewer。

所有生成材料评估必须记录 reference dataset、去重策略、fingerprint 或 embedding 版本，避免报告不可复现。

## 10. 外部生态集成

| 生态 | 阶段 | 集成方式 | 安全边界 |
|---|---|---|---|
| Materials Project | V1/V2 | Connector + Secret | BYOK/API key 加密引用 |
| OPTIMADE | V1/V2 | Connector | endpoint allowlist |
| AiiDA | V2 | Project connector/plugin | 项目级凭据与只读优先 |
| atomate2 | V2 | Workflow metadata import | 不在平台内直接跑计算 |
| internal database | V2 | Organization plugin | 管理员启用，最小权限 |

外部集成默认只导入元数据和结构对象，不默认触发外部计算任务。

## 11. 插件机制

插件 manifest 必须声明：

```ts
type MaterialPluginManifest = {
  pluginId: string;
  name: string;
  version: string;
  domain: ToolDomain;
  tools: Array<{
    toolId: string;
    category: ToolCategory;
    domain: ToolDomain;
    implementationSource: "plugin";
    inputSchema: ToolInputSchema;
    paramsSchema: Record<string, unknown>;
    artifactTypes: ArtifactType[];
    timeoutSec: number;
    costLevel: "low" | "medium" | "high";
  }>;
  permissions: {
    network: false | { allowlist: string[] };
    secrets: string[];
    shell: false;
    filesystem: "job_tmp_only";
  };
};
```

插件启用流程：

```text
Admin uploads/enables plugin
  -> manifest validation
  -> tool schema validation
  -> sandbox policy validation
  -> project-level enablement
  -> Tool Registry registration
  -> audit log
```

## 12. 数据流 / 控制流

```text
Uploaded / imported material data
  -> Parser Registry
  -> Object Normalizer
  -> Data Profile extension
  -> Agent reads profile + registry summary
  -> JSON Plan with registered domain tools
  -> Execution Controller validation
  -> Worker sandbox execution
  -> Artifact / Recipe / Report
```

## 13. API / Schema 草案

```ts
type DomainExtensionCapability = {
  capabilityId: string;
  domain: ToolDomain;
  stage: "mvp" | "v1" | "v2" | "plugin";
  toolIds: string[];
  inputOptions: ToolInputOption[];
  requiredSecrets?: string[];
};
```

`ToolDomain` 和 `ToolInputOption` 以 `docs/13_SHARED_SCHEMA_SPEC.md` 为准。插件扩展不能回退到单一 `requiredObjectTypes`，必须支持多输入方案和周期性结构约束。

## 14. 数据库表草案

| 表 | 目的 |
|---|---|
| `plugin_manifests` | 插件 manifest、版本、状态 |
| `plugin_tools` | 插件贡献的 Tool Registry 条目 |
| `external_connectors` | 外部材料数据库连接配置 |
| `domain_profiles` | phonon/electronic/simulation 等扩展画像 |
| `domain_artifacts` | 专业材料 Artifact 元数据扩展 |

这些表可以在 V1/V2 引入；MVP 只需保证核心表结构允许扩展 metadata。

## 15. 前端交互草案

- Data Profile 面板增加 domain badges：structure、ml、phonon、trajectory、simulation、external。
- Tool recommendations 标记能力阶段：available、planned、requires plugin、unsupported。
- Artifact 面板按领域筛选图表、viewer、report 和 recipe。
- Project Settings 增加插件启用、外部 connector 和 Secret 绑定。

## 16. 高并发、安全、扩展性考虑

- Phonon、trajectory、VASP/LAMMPS 解析默认进入专用队列，避免阻塞 MVP 结构/表格任务。
- 大 trajectory 默认抽帧，长 band/DOS 数据默认下采样或懒加载。
- 外部 API connector 必须走 rate limit、budget、allowlist 和 audit log。
- 插件工具必须使用 job 临时目录、资源限制、超时和无默认网络策略。
- 专业扩展不得把 Secret、内部路径、隐藏思维链写入 Artifact 或导出包。

## 17. 本阶段产出的目标文件

```text
docs/11_MATERIAL_DOMAIN_EXTENSIONS.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
persistent/ARCHITECTURE_DECISIONS.md
persistent/OPEN_QUESTIONS.md
persistent/CHANGELOG.md
```

## 18. 下一阶段任务

继续按 `docs/12_MVP_ROADMAP.md` 进入代码实现准备。实现阶段优先级仍为：

1. 基础设施与 schema。
2. 上传、解析和 Data Profile。
3. Tool Registry 与 MVP Adapter。
4. Job Queue、SSE 和 Artifact。
5. 前端工作台。
6. Agent Plan + Validator。
7. Recipe / Report / Security。
