# 共享 Schema 规范

## 1. 本阶段目标

收敛前端、后端、Worker、Agent 和 Tool Registry 共同使用的核心类型，避免每个设计文件重复定义不同版本的 `ArtifactType`、`DisplayTarget`、`ToolCategory`、`DataProfile`、`AnalysisPlan`、`JobEvent` 和 `Recipe`。

本文件是实现阶段的类型基线。后续代码应优先从本文件拆分 JSON Schema，再派生 TypeScript 类型和 Python Pydantic model。

## 2. 设计原则

- 单一命名源：跨服务枚举只在本文件定义。
- JSON Schema first：前端 TypeScript 和后端 Python model 都从共享 JSON Schema 派生。
- 轻量 Profile：Data Profile 存摘要，完整大列表进入 normalized object / object storage。
- Artifact 一等化：图、表格、指标、质量问题、报告和 Recipe 都是 Artifact。
- Secret 不入 Schema 产物：Recipe 和 Artifact 只保存 provider requirement，不保存具体 SecretRef。

## 3. 共享枚举

```ts
type ArtifactType =
  | "plotly_json"
  | "plotly_html"
  | "preview_png"
  | "figure_svg"
  | "figure_pdf"
  | "matterviz_html"
  | "matterviz_snapshot_png"
  | "structure_json"
  | "metrics_json"
  | "table_json"
  | "table_csv"
  | "quality_issues_json"
  | "summary_md"
  | "report_md"
  | "report_html"
  | "recipe_json"
  | "analysis_plan_json";

type DisplayTarget =
  | "overview"
  | "composition"
  | "structure"
  | "trajectory"
  | "phonon"
  | "ml"
  | "artifacts"
  | "report";

type ToolCategory =
  | "visualization"
  | "analysis"
  | "parser"
  | "report"
  | "utility";

type ToolDomain =
  | "composition"
  | "structure"
  | "trajectory"
  | "phonon"
  | "electronic"
  | "simulation"
  | "ml"
  | "generation"
  | "external";

type ImplementationSource =
  | "pymatviz"
  | "pymatviz_composed"
  | "matterviz"
  | "plotly_custom"
  | "platform_builtin"
  | "plugin";

type MaterialObjectType =
  | "Composition"
  | "Structure"
  | "Atoms"
  | "DataFrame"
  | "PhononBand"
  | "PhononDos"
  | "Trajectory"
  | "ElementValueMap"
  | "RawUnsupported";

type FieldRole =
  | "formula"
  | "target"
  | "prediction"
  | "uncertainty"
  | "label"
  | "structure_id";

type StructurePeriodicityRequirement =
  | "periodic_required"
  | "non_periodic_allowed"
  | "any";
```

## 4. Data Asset 与 Normalized Object

```ts
type DataAsset = {
  id: string;
  projectId: string;
  datasetId: string;
  fileName: string;
  mediaType: string;
  detectedFormat:
    | "cif"
    | "poscar"
    | "xyz"
    | "extxyz"
    | "csv"
    | "json_limited"
    | "phonopy"
    | "trajectory"
    | "archive"
    | "unknown";
  storageKey: string;
  status: "uploaded" | "parsing" | "profile_ready" | "failed" | "unsupported";
};

type NormalizedObject = {
  id: string;
  datasetId: string;
  objectType: MaterialObjectType;
  sourceFileIds: string[];
  storageKey: string;
  metadataKey?: string;
  previewKey?: string;
  metadata: Record<string, unknown>;
  hash: string;
};
```

## 5. Data Profile

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

## 6. Tool Registry

```ts
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
  artifactTypes: ArtifactType[];
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
```

Example:

```json
{
  "toolId": "composition.ptable_heatmap",
  "category": "visualization",
  "domain": "composition",
  "implementationSource": "pymatviz",
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
        "description": "Use an element-to-value mapping."
      }
    ]
  }
}
```

## 7. Analysis Plan

```ts
type AnalysisPlan = {
  schemaVersion: "0.1";
  goal: string;
  datasetId: string;
  profileId: string;
  toolRegistryVersion: string;
  assumptions: string[];
  warnings: string[];
  steps: AnalysisStep[];
  expectedArtifacts: ExpectedArtifact[];
};

type AnalysisStep = {
  stepId: string;
  toolId: string;
  purpose: string;
  reason: string;
  inputRefs: Array<{
    refType: "dataset" | "profile" | "normalized_object" | "dataframe_column" | "artifact";
    ref: string;
  }>;
  params: Record<string, unknown>;
  output: {
    artifactTypes: ArtifactType[];
    displayTarget: DisplayTarget;
  };
  constraints?: {
    timeoutSec?: number;
    maxRows?: number;
    maxStructures?: number;
    requiresConfirmation?: boolean;
  };
};

type ExpectedArtifact = {
  name: string;
  type: ArtifactType;
  fromStepId?: string;
};
```

## 8. Job 与事件

```ts
type JobStatus =
  | "created"
  | "queued"
  | "running"
  | "partial_success"
  | "completed"
  | "failed"
  | "cancel_requested"
  | "cancelled";

type JobEvent = {
  id: string;
  jobId: string;
  seq: number;
  eventType: string;
  status: "info" | "running" | "success" | "warning" | "error";
  message: string;
  progress?: number;
  payload?: Record<string, unknown>;
  createdAt: string;
};
```

## 9. Artifact、Recipe 与 Report

```ts
type Artifact = {
  id: string;
  projectId: string;
  datasetId?: string;
  jobId: string;
  toolCallId?: string;
  type: ArtifactType;
  name: string;
  version: string;
  storageKey: string;
  previewKey?: string;
  sizeBytes: number;
  contentHash: string;
  metadata: ArtifactMetadata;
};

type ArtifactMetadata = {
  toolId?: string;
  toolVersion?: string;
  adapterVersion?: string;
  inputHashes: string[];
  paramsHash?: string;
  profileId?: string;
  recipeId?: string;
  reportId?: string;
  createdAt: string;
  provenance: Record<string, unknown>;
};

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
  steps: AnalysisStep[];
  environment: RecipeEnvironment;
};

type RecipeEnvironment = {
  pythonVersion?: string;
  pymatvizVersion?: string;
  pymatgenVersion?: string;
  aseVersion?: string;
  plotlyVersion?: string;
  mattervizVersion?: string;
  llmProviderRequirement?: "openai-compatible";
  modelClass?: "reasoning" | "general";
};
```

## 10. Config 与 Secret

```ts
type LlmExecutionProfile = {
  providerPolicy: "runner_user_byok" | "system_hosted" | "project_default";
  provider?: string;
  model?: string;
  maxCostPerJob: number;
};

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

MVP LLM Secret resolution:

1. `job_runner_user_secret`
2. `project_default_system_provider`
3. `system_hosted_key`

Recipe must not save a concrete `SecretRef`; it only stores provider/model requirements.
